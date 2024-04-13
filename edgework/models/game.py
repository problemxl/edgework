from dataclasses import dataclass
from datetime import datetime


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

    @property
    def game_time(self):
        return self.start_time_utc.strftime("%I:%M %p")

    def __str__(self):
        return f"{self.away_team_abbrev} @ {self.home_team_abbrev} | {self.game_time} | {self.away_team_score} - {self.home_team_score}"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.game_id == other.game_id
