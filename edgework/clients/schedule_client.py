from datetime import datetime, timedelta
import re
from edgework.http_client import SyncHttpClient
from edgework.models.schedule import Schedule

class ScheduleClient:
    def __init__(self, client: SyncHttpClient):
        self._client = client

    def get_schedule(self) -> Schedule:
        response = self._client.get('schedule/now')
        
        schedule_dict = {
            "previousStartDate": response.json()["previousStartDate"],
            "games": [game for day in response.json()["gameWeek"] for game in day["games"]],
            "preSeasonStartDate": response.json()["preSeasonStartDate"],
            "regularSeasonStartDate": response.json()["regularSeasonStartDate"],
            "regularSeasonEndDate": response.json()["regularSeasonEndDate"],
            "playoffEndDate": response.json()["playoffEndDate"],
            "numberOfGames": response.json()["numberOfGames"]
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
            raise ValueError("Invalid date format. Should be in the format of 'YYYY-MM-DD'.")
        
        response = self._client.get(f'schedule/{date}')
        schedule_dict = {
            "previousStartDate": response.json()["previousStartDate"],
            "games": [game for day in response.json()["gameWeek"] for game in day["games"]],
            "preSeasonStartDate": response.json()["preSeasonStartDate"],
            "regularSeasonStartDate": response.json()["regularSeasonStartDate"],
            "regularSeasonEndDate": response.json()["regularSeasonEndDate"],
            "playoffEndDate": response.json()["playoffEndDate"],
            "numberOfGames": response.json()["numberOfGames"]
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
        if not re.match(r"\d{4}-\d{2}-\d{2}", start_date) and not re.match(r"\d{4}-\d{2}-\d{2}", end_date):
            raise ValueError("Invalid date format. Should be in the format of 'YYYY-MM-DD'.")
        
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)

        if start_dt > end_dt:
            raise ValueError("Start date cannot be after end date.")
        
        for i in range((end_dt - start_dt).days + 1):
            response = self._client.get(f'schedule/{start_date + timedelta(days=i)}')
            return Schedule.from_dict(response.json())
    
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
        response = self._client.get(f'club-schedule-season/{team_abbr}/now')
        schdeule_dict = {
            "previousStartDate": response.json()["previousStartDate"],
            "games": [game for day in response.json()["gameWeek"] for game in day["games"]],
            "preSeasonStartDate": response.json()["preSeasonStartDate"],
            "regularSeasonStartDate": response.json()["regularSeasonStartDate"],
            "regularSeasonEndDate": response.json()["regularSeasonEndDate"],
            "playoffEndDate": response.json()["playoffEndDate"],
            "numberOfGames": response.json()["numberOfGames"]
        }
        return Schedule.from_dict(schdeule_dict)
    
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
        response = self._client.get(f'schedule/club-schedule/{team_abbr}/now')
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
        response = self._client.get(f'schedule/club-schedule/{team_abbr}/now')
        return Schedule.from_dict(response.json())