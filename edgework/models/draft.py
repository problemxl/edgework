from dataclasses import dataclass
from typing import Optional


@dataclass
class DraftPick:
    year: int
    round_number: int
    pick_number: int
    team_id: int
    team_abbrev: str
    player_id: Optional[int] = None
    player_first_name: Optional[str] = None
    player_last_name: Optional[str] = None
    player_position: Optional[str] = None
    height_in_inches: Optional[int] = None
    weight_in_pounds: Optional[int] = None

    @property
    def player_full_name(self) -> Optional[str]:
        if self.player_first_name and self.player_last_name:
            return f"{self.player_first_name} {self.player_last_name}"
        return None

    def __str__(self):
        if self.player_full_name:
            return f"R{self.round_number}P{self.pick_number}: {self.player_full_name} ({self.team_abbrev})"
        return f"R{self.round_number}P{self.pick_number}: {self.team_abbrev}"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, DraftPick):
            return (
                self.year == other.year
                and self.round_number == other.round_number
                and self.pick_number == other.pick_number
            )
        return False

    @classmethod
    def from_api(cls, data: dict, year: int) -> "DraftPick":
        return cls(
            year=year,
            round_number=data.get("roundNumber"),
            pick_number=data.get("pickInRound"),
            team_id=data.get("teamId"),
            team_abbrev=data.get("teamAbbrev"),
            player_id=data.get("playerId"),
            player_first_name=data.get("firstName"),
            player_last_name=data.get("lastName"),
            player_position=data.get("positionCode"),
            height_in_inches=data.get("heightInInches"),
            weight_in_pounds=data.get("weightInPounds"),
        )


@dataclass
class DraftRanking:
    rank: int
    player_id: int
    first_name: str
    last_name: str
    position: str
    height_in_inches: Optional[int] = None
    weight_in_pounds: Optional[int] = None
    team: Optional[str] = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"#{self.rank}: {self.full_name} ({self.position})"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, DraftRanking):
            return self.rank == other.rank
        return False
