import re
from datetime import date, datetime
from typing import Optional, Union

from edgework.http_client import HttpClient
from edgework.models.schedule import Schedule


class ScheduleClient:
    def __init__(self, client: HttpClient):
        self._client = client

    # ------------------------------------------------------------------
    # Input normalization helpers (shared by all date/month parameters)
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_date(value: Union[str, date, datetime], label: str = "date") -> str:
        """Normalize a date input to the API's expected ``YYYY-MM-DD`` string.

        Accepts ``datetime.date``/``datetime.datetime`` objects (normalized
        via ISO formatting) or strings in ``YYYY-MM-DD`` format. The calendar
        validity of the date is also verified (e.g. ``2024-02-31`` is
        rejected).

        Args:
            value: The date to normalize.
            label: Parameter name used in error messages.

        Returns:
            The normalized ``YYYY-MM-DD`` date string.

        Raises:
            ValueError: If the value is not a valid ``YYYY-MM-DD`` date.
        """
        if isinstance(value, datetime):
            return value.date().isoformat()
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            try:
                datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                pass
            else:
                return value
        raise ValueError(
            f"Invalid date format for {label}. Should be in the format of "
            f"'YYYY-MM-DD'. Got: {value!r}"
        )

    @staticmethod
    def _validate_month(value: Union[str, date, datetime]) -> str:
        """Normalize a month input to the API's expected ``YYYY-MM`` string.

        Accepts ``datetime.date``/``datetime.datetime`` objects (truncated to
        their year/month) or strings in ``YYYY-MM`` format with a month
        between ``01`` and ``12``.

        Args:
            value: The month to normalize.

        Returns:
            The normalized ``YYYY-MM`` month string.

        Raises:
            ValueError: If the value is not a valid ``YYYY-MM`` month.
        """
        if isinstance(value, datetime):
            return value.strftime("%Y-%m")
        if isinstance(value, date):
            return value.strftime("%Y-%m")
        if isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}", value):
            month = int(value[5:7])
            if 1 <= month <= 12:
                return value
        raise ValueError(
            f"Invalid month format. Should be in the format of 'YYYY-MM' "
            f"with a month between '01' and '12'. Got: {value!r}"
        )

    def _get_club_schedule(
        self, team_abbr: str, period: str, value: Optional[str]
    ) -> Schedule:
        """Shared request/model conversion for club-schedule routes.

        Builds ``club-schedule/{team}/{period}/{value-or-now}``, performs the
        request and converts the payload into a :class:`Schedule`. Used by
        both the month and the week schedule methods so that route
        construction and response conversion live in exactly one place.

        Args:
            team_abbr: The team abbreviation (e.g., 'TOR').
            period: Either ``'month'`` or ``'week'``.
            value: The normalized month/date segment, or ``None`` for "now".

        Returns:
            Schedule
        """
        segment = value if value is not None else "now"
        response = self._client.get(
            f"club-schedule/{team_abbr}/{period}/{segment}", web=True
        )
        data = response.json()
        return Schedule.from_api(self._client, data)

    def get_schedule(self) -> Schedule:
        """Get the current schedule."""
        response = self._client.get("schedule/now", web=True)
        data = response.json()
        return Schedule.from_api(self._client, data)

    def get_schedule_for_date(
        self, date: Union[str, date, datetime]
    ) -> Schedule:
        """Get the schedule for the given date.

        Parameters
        ----------
        date : str or datetime.date or datetime.datetime
            The date for which to get the schedule. Strings should be in the
            format of 'YYYY-MM-DD'; date objects are normalized.

        Returns
        -------
        Schedule

        """
        date = self._validate_date(date)

        response = self._client.get(f"schedule/{date}", web=True)
        data = response.json()
        return Schedule.from_api(self._client, data)

    def get_schedule_for_date_range(
        self,
        start_date: Union[str, date, datetime],
        end_date: Union[str, date, datetime],
        web: bool = True,
    ) -> Schedule:
        """Get schedule for the given date range.

        Parameters
        ----------
        start_date : str or datetime.date or datetime.datetime
            The start date for which to get the schedule. Strings should be
            in the format of 'YYYY-MM-DD'; date objects are normalized.
        end_date : str or datetime.date or datetime.datetime
            The end date for which to get the schedule. Strings should be in
            the format of 'YYYY-MM-DD'; date objects are normalized.
        web : bool, optional
            Whether to use the web API endpoint. Defaults to True.

        Returns
        -------
        Schedule

        """
        # Validate and normalize the date formats
        start_date = self._validate_date(start_date, label="start date")
        end_date = self._validate_date(end_date, label="end date")

        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)

        if start_dt > end_dt:
            raise ValueError("Start date cannot be after end date.")

        games = []
        schedule_data = {
            "previousStartDate": None,
            "games": [],
            "preSeasonStartDate": None,
            "regularSeasonStartDate": None,
            "regularSeasonEndDate": None,
            "playoffEndDate": None,
            "numberOfGames": 0,
        }

        # Track seen game IDs to avoid duplicates
        seen_game_ids = set()

        current_date = start_date
        while current_date:
            response = self._client.get(f"schedule/{current_date}", web=web)
            data = response.json()

            # Extract games from this page
            page_games = [
                game
                for day in data.get("gameWeek", [])
                for game in day.get("games", [])
            ]

            # Filter out duplicates
            for game in page_games:
                game_id = game.get("id")
                if game_id not in seen_game_ids:
                    seen_game_ids.add(game_id)
                    games.append(game)

            # Set metadata from first page
            if not schedule_data["previousStartDate"]:
                schedule_data["previousStartDate"] = data.get("previousStartDate")
                schedule_data["preSeasonStartDate"] = data.get("preSeasonStartDate")

            # Update season dates
            if data.get("regularSeasonStartDate"):
                schedule_data["regularSeasonStartDate"] = data.get(
                    "regularSeasonStartDate"
                )
            if data.get("regularSeasonEndDate"):
                schedule_data["regularSeasonEndDate"] = data.get("regularSeasonEndDate")
            if data.get("playoffEndDate"):
                schedule_data["playoffEndDate"] = data.get("playoffEndDate")

            # Check if there's a next page
            next_start_date = data.get("nextStartDate")
            if next_start_date:
                # Parse the next start date
                next_start_dt = datetime.fromisoformat(next_start_date)
                # Stop if we've gone past the requested end date
                if next_start_dt.date() > end_dt.date():
                    current_date = None
                else:
                    current_date = next_start_date[:10]  # YYYY-MM-DD format
            else:
                current_date = None

        # Filter games to ensure they're within the requested date range
        filtered_games = []
        for game in games:
            try:
                game_date = datetime.fromisoformat(
                    game.get("startTimeUTC", "").replace("Z", "+00:00")
                ).date()
                if start_dt.date() <= game_date <= end_dt.date():
                    filtered_games.append(game)
            except (ValueError, AttributeError):
                # If we can't parse the date, include the game to avoid losing data
                filtered_games.append(game)

        schedule_data["numberOfGames"] = len(filtered_games)
        schedule_data["games"] = filtered_games
        return Schedule.from_api(self._client, schedule_data)

    def get_schedule_for_team(self, team_abbr: str) -> Schedule:
        """Get the schedule for the given team.

        Parameters
        ----------
        team_abbr : str
            The abbreviation of the team for which to get the schedule.

        Returns
        -------
        Schedule

        """
        response = self._client.get(f"club-schedule-season/{team_abbr}/now", web=True)
        data = response.json()
        return Schedule.from_api(self._client, data)

    def get_schedule_for_team_for_week(
        self, team_abbr: str, date: Optional[Union[str, date, datetime]] = None
    ) -> Schedule:
        """Get the schedule for the given team for a week.

        Uses the documented Web API route
        ``/v1/club-schedule/{team}/week/{date}``; when ``date`` is omitted the
        current week (``.../week/now``) is fetched.

        Parameters
        ----------
        team_abbr : str
            The abbreviation of the team for which to get the schedule.
        date : str or datetime.date or datetime.datetime, optional
            A date within the requested week. Strings should be in the
            format of 'YYYY-MM-DD'; date objects are normalized. Defaults to
            None (the current week).

        Returns
        -------
        Schedule

        """
        normalized_date = (
            self._validate_date(date, label="week date") if date is not None else None
        )
        return self._get_club_schedule(team_abbr, "week", normalized_date)

    def get_schedule_for_team_for_month(
        self, team_abbr: str, month: Optional[Union[str, date, datetime]] = None
    ) -> Schedule:
        """Get the schedule for the given team for a month.

        Uses the documented Web API route
        ``/v1/club-schedule/{team}/month/{month}``; when ``month`` is omitted
        the current month (``.../month/now``) is fetched.

        Parameters
        ----------
        team_abbr : str
            The abbreviation of the team for which to get the schedule.
        month : str or datetime.date or datetime.datetime, optional
            The requested month. Strings should be in the format of
            'YYYY-MM'; date objects are truncated to their year/month.
            Defaults to None (the current month).

        Returns
        -------
        Schedule

        """
        normalized_month = self._validate_month(month) if month is not None else None
        return self._get_club_schedule(team_abbr, "month", normalized_month)

    def get_schedule_calendar(self) -> dict:
        """Get the current schedule calendar.

        Returns
        -------
        dict
            Schedule calendar data showing available dates with games.
        """
        response = self._client.get("schedule-calendar/now", web=True)
        return response.json()

    def get_schedule_calendar_for_date(
        self, date: Union[str, date, datetime]
    ) -> dict:
        """Get the schedule calendar for a specific date.

        Parameters
        ----------
        date : str or datetime.date or datetime.datetime
            The date for which to get the schedule calendar. Strings should
            be in the format of 'YYYY-MM-DD'; date objects are normalized.

        Returns
        -------
        dict
            Schedule calendar data for the specified date.
        """
        date = self._validate_date(date)

        response = self._client.get(f"schedule-calendar/{date}", web=True)
        return response.json()
