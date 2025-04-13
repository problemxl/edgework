from datetime import datetime
from typing import List, Optional, Dict

from edgework.models.base import BaseNHLModel
from edgework.http_client import AsyncHttpClient

class Schedule(BaseNHLModel):
    """Schedule model to store schedule information."""
    
    def __init__(self, edgework_client, obj_id=None, previous_start_date=None, games=None,
                 pre_season_start_date=None, regular_season_start_date=None, 
                 regular_season_end_date=None, playoff_end_date=None, number_of_games=0):
        """
        Initialize a Schedule object.
        
        Args:
            edgework_client: The Edgework client
            obj_id: The ID of the schedule
            previous_start_date: Start date of the previous period
            games: List of games in the schedule
            pre_season_start_date: Start date of the pre-season
            regular_season_start_date: Start date of the regular season
            regular_season_end_date: End date of the regular season
            playoff_end_date: End date of the playoffs
            number_of_games: Total number of games in the schedule
        """
        super().__init__(edgework_client, obj_id)
        self.previous_start_date = previous_start_date
        self.games = games or []
        self.pre_season_start_date = pre_season_start_date
        self.regular_season_start_date = regular_season_start_date
        self.regular_season_end_date = regular_season_end_date
        self.playoff_end_date = playoff_end_date
        self.number_of_games = number_of_games
    
    @classmethod
    def from_dict(cls, edgework_client, data: dict) -> "Schedule":
        previous = datetime.fromisoformat(data["previousStartDate"]) if data.get("previousStartDate") else None
        games = data.get("games") or [game for day in data.get("gameWeek", []) for game in day.get("games", [])]
        pre_season = datetime.fromisoformat(data["preSeasonStartDate"]) if data.get("preSeasonStartDate") else None
        reg_start = datetime.fromisoformat(data["regularSeasonStartDate"]) if data.get("regularSeasonStartDate") else None
        reg_end = datetime.fromisoformat(data["regularSeasonEndDate"]) if data.get("regularSeasonEndDate") else None
        playoff = datetime.fromisoformat(data["playoffEndDate"]) if data.get("playoffEndDate") else None
        number_of_games = data.get("numberOfGames") or 0
        return cls(
            edgework_client=edgework_client,
            previous_start_date=previous,
            games=games,
            pre_season_start_date=pre_season,
            regular_season_start_date=reg_start,
            regular_season_end_date=reg_end,
            playoff_end_date=playoff,
            number_of_games=number_of_games,
        )

    @classmethod
    async def get_schedule(cls, edgework_client, client: AsyncHttpClient, date: Optional[str] = None) -> "Schedule":
        path = f"schedule/{date}" if date else "schedule/now"
        res = await client.get(path)
        data = res.json()
        return cls.from_dict(edgework_client, data)
        
    def fetch_data(self):
        """
        Fetch the data for the schedule.
        """
        # Implementation depends on how data is fetched from the API
        pass

    @classmethod
    async def get_schedule(cls, client: AsyncHttpClient, date: Optional[str] = None) -> "Schedule":
        path = f"schedule/{date}" if date else "schedule/now"
        res = await client.get(path)
        data = res.json()
        return cls.from_dict(data)
