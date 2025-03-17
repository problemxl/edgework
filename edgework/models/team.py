from pydantic import BaseModel, Field


class Team(BaseModel):
    id: int = Field(description="Unique identifier for the team")
    abbreviation: str = Field(description="Abbreviated form of the team name")
    name: str = Field(description="Full name of the team")

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, Team):
            return self.id == other.id
        return False
