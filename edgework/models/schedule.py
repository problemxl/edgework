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

    def __init__(
        self,
        previous_start_date: datetime,
        games: list[dict],
        pre_season_start_date: datetime,
        regular_season_start_date: datetime,
        regular_season_end_date: datetime,
        playoff_end_date: datetime,
        number_of_games: int,
    ):
        self.previous_start_date = previous_start_date
        self.games = games
        self.pre_season_start_date = pre_season_start_date
        self.regular_season_start_date = regular_season_start_date
        self.regular_season_end_date = regular_season_end_date
        self.playoff_end_date = playoff_end_date
        self.number_of_games = number_of_games

    @classmethod
    def from_dict(cls, data: dict) -> "Schedule":
        return cls(
            previous_start_date=datetime.fromisoformat(data["previousStartDate"]) if data["previousStartDate"] else None,
            games=data.get("games") if data.get("games") is not None else [game for day in data.get("gameWeek") for game in day["games"]],
            pre_season_start_date=datetime.fromisoformat(data["preSeasonStartDate"]) if data.get("preSeasonStartDate") is not None else None,
            regular_season_start_date=datetime.fromisoformat(data["regularSeasonStartDate"]) if data.get("regularSeasonStartDate") is not None else None,
            regular_season_end_date=datetime.fromisoformat(data["regularSeasonEndDate"]) if data.get("regularSeasonEndDate") is not None else None,
            playoff_end_date=datetime.fromisoformat(data["playoffEndDate"]) if data.get("playoffEndDate") is not None else None,
            number_of_games=data["numberOfGames"] if data.get("numberOfGames") is not None else 0,
        )        

    @classmethod
    async def get_schedule(self, client: AsyncHttpClient, date: str|None = None) -> "Schedule":
        """Get the schedule for the given date."""
        path = f"schedule/{date}" if date else "schedule/now"
        res = await client.get(path)
        data = res.json()
        return Schedule(
            previous_start_date=datetime.fromisoformat(data["previousStartDate"]),
            games=[game for day in data.get("gameWeek") for game in day["games"]],
            pre_season_start_date=datetime.fromisoformat(data.get("preSeasonStartDate")),
            regular_season_start_date=datetime.fromisoformat(data["regularSeasonStartDate"]),
            regular_season_end_date=datetime.fromisoformat(data["regularSeasonEndDate"]),
            playoff_end_date=datetime.fromisoformat(data["playoffEndDate"]),
            number_of_games=data["numberOfGames"],
        )
    