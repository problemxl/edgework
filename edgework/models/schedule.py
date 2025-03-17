from datetime import datetime
from typing import List, Optional, Dict

from pydantic import BaseModel, Field
from edgework.http_client import AsyncHttpClient

class Schedule(BaseModel):
    previous_start_date: Optional[datetime] = Field(description="Start date of the previous period", default=None)
    games: List[Dict] = Field(description="List of games in the schedule")
    pre_season_start_date: Optional[datetime] = Field(description="Start date of the pre-season", default=None)
    regular_season_start_date: Optional[datetime] = Field(description="Start date of the regular season", default=None)
    regular_season_end_date: Optional[datetime] = Field(description="End date of the regular season", default=None)
    playoff_end_date: Optional[datetime] = Field(description="End date of the playoffs", default=None)
    number_of_games: int = Field(description="Total number of games in the schedule")

    @classmethod
    def from_dict(cls, data: dict) -> "Schedule":
        previous = datetime.fromisoformat(data["previousStartDate"]) if data.get("previousStartDate") else None
        games = data.get("games") or [game for day in data.get("gameWeek", []) for game in day.get("games", [])]
        pre_season = datetime.fromisoformat(data["preSeasonStartDate"]) if data.get("preSeasonStartDate") else None
        reg_start = datetime.fromisoformat(data["regularSeasonStartDate"]) if data.get("regularSeasonStartDate") else None
        reg_end = datetime.fromisoformat(data["regularSeasonEndDate"]) if data.get("regularSeasonEndDate") else None
        playoff = datetime.fromisoformat(data["playoffEndDate"]) if data.get("playoffEndDate") else None
        number_of_games = data.get("numberOfGames") or 0
        return cls(
            previous_start_date=previous,
            games=games,
            pre_season_start_date=pre_season,
            regular_season_start_date=reg_start,
            regular_season_end_date=reg_end,
            playoff_end_date=playoff,
            number_of_games=number_of_games,
        )

    @classmethod
    async def get_schedule(cls, client: AsyncHttpClient, date: Optional[str] = None) -> "Schedule":
        path = f"schedule/{date}" if date else "schedule/now"
        res = await client.get(path)
        data = res.json()
        return cls.from_dict(data)
