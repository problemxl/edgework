from dataclasses import dataclass


@dataclass
class Team:
    id: int
    abbreviation: str
    name: str

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, Team):
            return self.id == other.id
        return False
