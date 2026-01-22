import re
from datetime import datetime, timedelta

from edgework.http_client import SyncHttpClient
from edgework.models.schedule import Schedule


class ScheduleClient:
    def __init__(self, client: SyncHttpClient):
        self._client = client

    def get_schedule(self) -> Schedule:
        response = self._client.get("schedule/now")
        data = response.json()
        schedule_dict = {
            "previousStartDate": data["previousStartDate"],
            "games": [game for day in data["gameWeek"] for game in day["games"]],
            "preSeasonStartDate": data["preSeasonStartDate"],
            "regularSeasonStartDate": data["regularSeasonStartDate"],
            "regularSeasonEndDate": data["regularSeasonEndDate"],
            "playoffEndDate": data["playoffEndDate"],
            "numberOfGames": data["numberOfGames"],
        }
        return Schedule.from_dict(schedule_dict)

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
        schedule_dict = {
            "previousStartDate": response.json()["previousStartDate"],
            "games": [
                game for day in response.json()["gameWeek"] for game in day["games"]
            ],
            "preSeasonStartDate": response.json()["preSeasonStartDate"],
            "regularSeasonStartDate": response.json()["regularSeasonStartDate"],
            "regularSeasonEndDate": response.json()["regularSeasonEndDate"],
            "playoffEndDate": response.json()["playoffEndDate"],
            "numberOfGames": response.json()["numberOfGames"],
        }
        return Schedule.from_dict(schedule_dict)

    def get_schedule_for_date_range(self, start_date: str, end_date: str) -> Schedule:
        """Get the schedule for the given date range.

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
        d = {
            "previousStartDate": None,
            "games": [],
            "pre_season_start_date": None,
            "regularSeasonStartDate": None,
            "regularSeasonEndDate": None,
            "playoffEndDate": None,
            "numberOfGames": None,
        }
        for i in range((end_dt - start_dt).days + 1):
            date = start_dt + timedelta(days=i)
            response = self._client.get(f"schedule/{date.strftime('%Y-%m-%d')}")
            data = response.json()
            games += [game for day in data.get("gameWeek") for game in day["games"]]
            if d["previousStartDate"] is None:
                d["previousStartDate"] = data.get("previousStartDate")
            d["regularSeasonStartDate"] = data.get("regularSeasonStartDate")
        d["regularSeasonEndDate"] = data.get("regularSeasonEndDate")
        d["playoffEndDate"] = data.get("playoffEndDate")
        d["numberOfGames"] = len(games)
        d["games"] = games
        return Schedule.from_dict(d)

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
        schedule_dict = {
            "previousStartDate": None,
            "games": data.get("games"),
            "preSeasonStartDate": None,
            "regularSeasonStartDate": None,
            "regularSeasonEndDate": None,
            "playoffEndDate": None,
            "numberOfGames": len(data.get("games")),
        }
        return Schedule.from_dict(schedule_dict)

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
        return Schedule.from_dict(response.json())

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
        return Schedule.from_dict(response.json())
