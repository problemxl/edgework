from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr

from edgework.http_client import HttpClient
from edgework.models.shift import Shift

class Game(BaseModel):
    game_id: int = Field(description="Unique identifier for the game")
    game_date: datetime = Field(description="Date the game was played")
    start_time_utc: datetime = Field(description="Start time of the game in UTC")
    game_state: str = Field(description="Current state of the game")
    away_team_abbrev: str = Field(description="Abbreviation of the away team")
    away_team_id: int = Field(description="Unique identifier for the away team")
    away_team_score: int = Field(description="Current score of the away team")
    home_team_abbrev: str = Field(description="Abbreviation of the home team")
    home_team_id: int = Field(description="Unique identifier for the home team")
    home_team_score: int = Field(description="Current score of the home team")
    season: int = Field(description="Season the game is part of")
    venue: str = Field(description="Venue where the game is played")

    # Private attributes
    _shifts: List[Shift] = PrivateAttr(default_factory=list)
    _client: Optional[HttpClient] = PrivateAttr(default=None)

    @property
    def game_time(self):
        return self.start_time_utc.strftime("%I:%M %p")

    def __str__(self):
        return f"{self.away_team_abbrev} @ {self.home_team_abbrev} | {self.game_time} | {self.away_team_score} - {self.home_team_score}"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        # Compare using game_id only
        return self.game_id == getattr(other, 'game_id', None)

    def __hash__(self):
        return hash(self.game_id)

    def _get(self):
        """Get the game information."""
        pass

    @property
    def shifts(self) -> List[Shift]:
        if not self._shifts:
            self._shifts = self._get_shifts()
        return self._shifts

    @classmethod
    def from_dict(cls, data: dict, client: HttpClient):
        game = cls(**data)
        game._client = client
        return game

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
            "venue": data.get("venue").get("default"),
        }
        return cls.from_dict(game_dict, client)

    @classmethod
    def get_game(cls, game_id: int, client: HttpClient):
        response = client.get(f"gamecenter/{game_id}/boxscore")
        data = response.json()
        return cls.from_api(data, client)

    def _get_shifts(self):
        """Get the shifts for the game."""
        response = self._client.get(
            "rest/en/shiftcharts",
            params={"cayenneExp": f"gameId={self.game_id}"},
            web=False,
        )
        data = response.json()["data"]
        shifts = [Shift.from_api(d) for d in data]
        self._shifts = shifts
        return shifts
