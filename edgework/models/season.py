from dataclasses import dataclass


@dataclass
class Season:
    id: int
    start_year: int
    end_year: int

    def __str__(self):
        return f"{self.start_year}-{self.end_year}"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, Season):
            return self.id == other.id
        return False

    @classmethod
    def from_id(cls, season_id: int) -> "Season":
        return cls(
            id=season_id,
            start_year=int(str(season_id)[:4]),
            end_year=int(str(season_id)[4:]),
        )
