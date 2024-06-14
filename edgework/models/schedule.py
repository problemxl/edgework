from datetime import datetime

from edgework.http_client import AsyncHttpClient


class Schedule:
    next_start_date: datetime
    previous_start_date: datetime
    games: list[dict]

    pre_season_start_date: datetime
    regular_season_start_date: datetime
    regular_season_end_date: datetime
    playoff_end_date: datetime

    number_of_games: int

    @classmethod
    def from_dict(cls, data: dict) -> "Schedule":
        return cls(
            next_start_date=datetime.fromisoformat(data["nextStartDate"]),
            previous_start_date=datetime.fromisoformat(data["previousStartDate"]),
            games=[game for day in data["gameWeek"] for game in day["games"]],
            pre_season_start_date=datetime.fromisoformat(data["preSeasonStartDate"]),
            regular_season_start_date=datetime.fromisoformat(data["regularSeasonStartDate"]),
            regular_season_end_date=datetime.fromisoformat(data["regularSeasonEndDate"]),
            playoff_end_date=datetime.fromisoformat(data["playoffEndDate"]),
            number_of_games=data["numberOfGames"],
        )        

    @classmethod
    async def get_schedule(self, client: AsyncHttpClient, date: str|None = None) -> "Schedule":
        """Get the schedule for the given date."""
        path = f"schedule/{date}" if date else "schedule/now"
        res = await client.get(path)
        data = res.json()
        return Schedule(
            next_start_date=datetime.fromisoformat(data["nextStartDate"]),
            previous_start_date=datetime.fromisoformat(data["previousStartDate"]),
            games=data["gameWeek"],
            pre_season_start_date=datetime.fromisoformat(data["preSeasonStartDate"]),
            regular_season_start_date=datetime.fromisoformat(data["regularSeasonStartDate"]),
            regular_season_end_date=datetime.fromisoformat(data["regularSeasonEndDate"]),
            playoff_end_date=datetime.fromisoformat(data["playoffEndDate"]),
            number_of_games=data["numberOfGames"],
        )
    