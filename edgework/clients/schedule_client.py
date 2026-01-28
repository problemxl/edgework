import re
from datetime import datetime

from edgework.http_client import HttpClient
from edgework.models.schedule import Schedule


class ScheduleClient:
    def __init__(self, client: HttpClient):
        self._client = client

    def get_schedule(self) -> Schedule:
        """Get the current schedule."""
        response = self._client.get("schedule/now", web=True)
        data = response.json()
        return Schedule.from_api(self._client, data)

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

        response = self._client.get(f"schedule/{date}", web=True)
        data = response.json()
        return Schedule.from_api(self._client, data)

    def get_schedule_for_date_range(self, start_date: str, end_date: str) -> Schedule:
        """Get schedule for the given date range.

        Uses nextStartDate pagination to fetch non-overlapping schedule chunks,
        avoiding duplicates that occur when fetching day-by-day.

        Parameters
        ----------
        start_date : str
            The start date for which to get the schedule. Should be in the format of 'YYYY-MM-DD'.
        end_date : str
            The end date for which to get the schedule. Should be in the format of 'YYYY-MM-DD'.

        Returns
        -------
        Schedule

        """
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
        seen_game_ids = set()
        current_date = start_date
        schedule_data = {
            "previousStartDate": None,
            "games": [],
            "preSeasonStartDate": None,
            "regularSeasonStartDate": None,
            "regularSeasonEndDate": None,
            "playoffEndDate": None,
            "numberOfGames": 0,
        }

        while current_date:
            response = self._client.get(f"schedule/{current_date}", web=True)
            data = response.json()

            day_games = [
                game
                for day in data.get("gameWeek", [])
                for game in day.get("games", [])
            ]

            for game in day_games:
                game_id = game.get("id")
                if game_id and game_id not in seen_game_ids:
                    seen_game_ids.add(game_id)
                    games.append(game)

            if not schedule_data["previousStartDate"]:
                schedule_data["previousStartDate"] = data.get("previousStartDate")
                schedule_data["preSeasonStartDate"] = data.get("preSeasonStartDate")

            if data.get("regularSeasonStartDate"):
                schedule_data["regularSeasonStartDate"] = data.get(
                    "regularSeasonStartDate"
                )
            if data.get("regularSeasonEndDate"):
                schedule_data["regularSeasonEndDate"] = data.get("regularSeasonEndDate")
            if data.get("playoffEndDate"):
                schedule_data["playoffEndDate"] = data.get("playoffEndDate")

            next_start = data.get("nextStartDate")
            if not next_start:
                break

            next_date_dt = datetime.fromisoformat(next_start)
            if next_date_dt > end_dt:
                break

            current_date = next_start

        filtered_games = []
        for game in games:
            game_date = game.get("gameDate")
            if game_date:
                game_date_dt = datetime.fromisoformat(game_date)
                if start_dt <= game_date_dt <= end_dt:
                    filtered_games.append(game)

        schedule_data["numberOfGames"] = len(filtered_games)
        schedule_data["games"] = filtered_games
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
        response = self._client.get(f"club-schedule-season/{team_abbr}/now", web=True)
        data = response.json()
        return Schedule.from_api(self._client, data)

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
        response = self._client.get(f"club-schedule/{team_abbr}/week/now", web=True)
        data = response.json()
        return Schedule.from_api(self._client, data)

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
        response = self._client.get(f"club-schedule/{team_abbr}/month/now", web=True)
        data = response.json()
        return Schedule.from_api(self._client, data)

    def get_schedule_calendar(self) -> dict:
        """Get the current schedule calendar.

        Returns
        -------
        dict
            Schedule calendar data showing available dates with games.
        """
        response = self._client.get("schedule-calendar/now", web=True)
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

        response = self._client.get(f"schedule-calendar/{date}", web=True)
        return response.json()
