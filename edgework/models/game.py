from dataclasses import dataclass, field
from datetime import datetime

from edgework.http_client import HttpClient
from edgework.models.shift import Shift


@dataclass
class Game:
    game_id: int
    game_date: datetime
    start_time_utc: datetime
    game_state: str
    away_team_abbrev: str
    away_team_id: int
    away_team_score: int
    home_team_abbrev: str
    home_team_id: int
    home_team_score: int
    season: int
    venue: str

    _shifts: list[Shift] = field(default_factory=list)
    _client: HttpClient = field(default=None, repr=False, compare=False)

    @property
    def game_time(self):
        return self.start_time_utc.strftime("%I:%M %p")

    def __str__(self):
        return f"{self.away_team_abbrev} @ {self.home_team_abbrev} | {self.game_time} | {self.away_team_score} - {self.home_team_score}"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.game_id == other.game_id
    
    def __hash__(self):
        return hash(self.game_id)
    
    def _get(self):
        """Get the game information."""
        pass

    @property
    def shifts(self) -> list[Shift]:
        if not self._shifts:
            self._shifts = self._get_shifts()
        return self._shifts

    @classmethod
    def from_dict(cls, data: dict, client: HttpClient):
        return cls(
            game_id=data.get("game_id"),
            game_date=data.get("game_date"),
            start_time_utc=data.get("start_time_utc"),
            game_state=data.get("game_state"),
            away_team_abbrev=data.get("away_team_abbrev"),
            away_team_id=data.get("away_team_id"),
            away_team_score=data.get("away_team_score"),
            home_team_abbrev=data.get("home_team_abbrev"),
            home_team_id=data.get("home_team_id"),
            home_team_score=data.get("home_team_score"),
            season=data.get("season"),
            venue=data.get("venue"),
            _client=client
        )

    @classmethod
    def from_api(cls, data: dict, client: HttpClient):
        game_dict = {
            "game_id": data.get("id"),
            "game_date": datetime.strptime(data.get("gameDate"), "%Y-%m-%d"),
            "start_time_utc": datetime.strptime(data.get("startTimeUTC"), "%Y-%m-%dT%H:%M:%SZ"),
            "game_state": data.get("gameState"),
            "away_team_abbrev": data.get("awayTeam").get("abbrev"),
            "away_team_id": data.get("awayTeam").get("id"),
            "away_team_score": data.get("awayTeam").get("score"),
            "home_team_abbrev": data.get("homeTeam").get("abbrev"),
            "home_team_id": data.get("homeTeam").get("id"),
            "home_team_score": data.get("homeTeam").get("score"),
            "season": data.get("season"),
            "venue": data.get("venue").get("default")
        }
        return cls.from_dict(game_dict, client)

    @classmethod
    def get_game(cls, game_id: int, client: HttpClient):
        response = client.get(f'gamecenter/{game_id}/boxscore')
        data = response.json()
        return cls.from_api(data, client)

    def _get_shifts(self):
        """Get the shifts for the game."""
        response = self._client.get(f"rest/en/shiftcharts?cayenneExp=gameId={self.game_id}", web=False)
        data = response.json()["data"]
        shifts = [Shift.from_api(d) for d in data]
        self._shifts = shifts
        return shifts
