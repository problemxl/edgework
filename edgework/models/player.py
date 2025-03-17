from datetime import datetime
from pydantic import BaseModel, Field


class Player(BaseModel):
    """Player model to store player information."""

    player_id: int = Field(description="Player ID is a unique identifier for the player")
    player_slug: str = Field(description="Player slug is a unique identifier for the player")
    birth_city: str = Field(description="The city where the player was born", default="")
    birth_country: str = Field(description="The country where the player was born", default="")
    birth_date: datetime = Field(description="The birth date of the player", default_factory=lambda: datetime(1, 1, 1))
    birth_state_province: str = Field(description="The state or province where the player was born", default="")
    current_team_abbr: str = Field(description="The abbreviation of the current team the player is on", default="")
    current_team_id: int = Field(description="The ID of the current team the player is on", default=-1)
    current_team_name: str = Field(description="The name of the current team the player is on", default="")
    draft_overall_pick: int = Field(description="The overall pick number in the draft", default=-1)
    draft_pick: int = Field(description="The pick number in the draft", default=-1)
    draft_round: int = Field(description="The round number in the draft", default=-1)
    draft_team_abbr: str = Field(description="The abbreviation of the team that drafted the player", default="")
    draft_year: datetime = Field(description="The year the player was drafted", default_factory=lambda: datetime(1, 1, 1))
    first_name: str = Field(description="The first name of the player", default="")
    last_name: str = Field(description="The last name of the player", default="")
    headshot_url: str = Field(description="The URL of the player's headshot image", default="")
    height: int = Field(description="The height of the player in inches", default=-1)
    hero_image_url: str = Field(description="The URL of the player's hero image", default="")
    is_active: bool = Field(description="Whether the player is currently active", default=False)
    position: str = Field(description="The position the player plays", default="")
    shoots_catches: str = Field(description="The hand the player uses to shoot or catch", default="")
    sweater_number: int = Field(description="The sweater number of the player", default=-1)
    weight: int = Field(description="The weight of the player in pounds", default=-1)

    @property
    def full_name(self):
        """
        Returns the full name of the player.
        """
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        """
        Returns a string representation of the player.
        """
        return f"{self.full_name} {self.current_team_abbr}"

    def __repr__(self):
        """
        Returns a string representation of the player for debugging.
        """
        return f"Player({self.full_name}, {self.player_id})"
