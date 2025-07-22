import re
from datetime import datetime, timedelta

from edgework.http_client import SyncHttpClient
from edgework.models.schedule import Schedule


class ScheduleClient:
    def __init__(self, client: SyncHttpClient):
        self._client = client

    def get_schedule(self) -> Schedule:
        """Get the current schedule."""
        response = self._client.get("schedule/now")
        data = response.json()
        return Schedule.from_api(None, data)

    def get_schedule_for_date(self, date: str) -> Schedule:
        """Get the schedule for the given date.

        Parameters
        ----------
        date : str
            The date for which to get the schedule. Should be in the format of 'YYYY-MM-DD'.

        Returns
        -------
        Schedule

        """
        # Validate the date format
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
            raise ValueError(
                "Invalid date format. Should be in the format of 'YYYY-MM-DD'."
            )

        response = self._client.get(f"schedule/{date}")
        data = response.json()
        return Schedule.from_api(None, data)

    def get_schedule_for_date_range(self, start_date: str, end_date: str) -> Schedule:
        """Get the schedule for the given date range.

        Parameters
        ----------
        start_date : strtac
            The start date for which to get the schedule. Should be in the format of 'YYYY-MM-DD'.
        end_date : str
            The end date for which to get the schedule. Should be in the format of 'YYYY-MM-DD'.

        Returns
        -------
        Schedule

        """
        # Validate the date format
        if not re.match(r"\d{4}-\d{2}-\d{2}", start_date):
            raise ValueError(
                f"Invalid date format. Should be in the format of 'YYYY-MM-DD'. Start date given was {start_date}"
            )
        if not re.match(r"\d{4}-\d{2}-\d{2}", end_date):
            raise ValueError(
                f"Invalid date format. Should be in the format of 'YYYY-MM-DD'. End date given was {end_date}"
            )

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

        for i in range((end_dt - start_dt).days + 1):
            date = start_dt + timedelta(days=i)
            response = self._client.get(f'schedule/{date.strftime("%Y-%m-%d")}')
            data = response.json()

            # Extract games from this day
            day_games = [
                game
                for day in data.get("gameWeek", [])
                for game in day.get("games", [])
            ]
            games.extend(day_games)

            # Set metadata from first day
            if i == 0:
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

        schedule_data["numberOfGames"] = len(games)
        schedule_data["games"] = games
        return Schedule.from_api(None, schedule_data)

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
        response = self._client.get(f"club-schedule-season/{team_abbr}/now")
        data = response.json()
        return Schedule.from_api(None, data)

    def get_schedule_for_team_for_week(self, team_abbr: str) -> Schedule:
        """Get the schedule for the given team for the current week.

        Parameters
        ----------
        team_abbr : str
            The abbreviation of the team for which to get the schedule.

        Returns
        -------
        Schedule

        """
        response = self._client.get(f"club-schedule/{team_abbr}/week/now")
        data = response.json()
        return Schedule.from_api(None, data)

    def get_schedule_for_team_for_month(self, team_abbr: str) -> Schedule:
        """Get the schedule for the given team for the current month.

        Parameters
        ----------
        team_abbr : str
            The abbreviation of the team for which to get the schedule.

        Returns
        -------
        Schedule

        """
        response = self._client.get(f"club-schedule/{team_abbr}/month/now")
        data = response.json()
        return Schedule.from_api(None, data)

    def get_schedule_calendar(self) -> dict:
        """Get the current schedule calendar.

        Returns
        -------
        dict
            Schedule calendar data showing available dates with games.
        """
        response = self._client.get("schedule-calendar/now")
        return response.json()

    def get_schedule_calendar_for_date(self, date: str) -> dict:
        """Get the schedule calendar for a specific date.

        Parameters
        ----------
        date : str
            The date for which to get the schedule calendar. Should be in the format of 'YYYY-MM-DD'.

        Returns
        -------
        dict
            Schedule calendar data for the specified date.
        """
        # Validate the date format
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
            raise ValueError(
                "Invalid date format. Should be in the format of 'YYYY-MM-DD'."
            )

        response = self._client.get(f"schedule-calendar/{date}")
        return response.json()
