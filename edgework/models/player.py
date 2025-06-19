"""Player model using Pydantic."""

from typing import Optional
from pydantic import BaseModel, Field


class Player(BaseModel):
    """Player model representing NHL player data from the search API."""
    
    player_id: str = Field(alias="playerId")
    name: str
    position_code: str = Field(alias="positionCode")
    team_id: Optional[str] = Field(default=None, alias="teamId")
    team_abbrev: Optional[str] = Field(default=None, alias="teamAbbrev") 
    last_team_id: Optional[str] = Field(default=None, alias="lastTeamId")
    last_team_abbrev: Optional[str] = Field(default=None, alias="lastTeamAbbrev")
    last_season_id: Optional[str] = Field(default=None, alias="lastSeasonId")
    sweater_number: Optional[int] = Field(default=None, alias="sweaterNumber")
    active: bool = True
    height: Optional[str] = None
    height_in_inches: Optional[int] = Field(default=None, alias="heightInInches")
    height_in_centimeters: Optional[int] = Field(default=None, alias="heightInCentimeters")
    weight_in_pounds: Optional[int] = Field(default=None, alias="weightInPounds")
    weight_in_kilograms: Optional[int] = Field(default=None, alias="weightInKilograms")
    birth_city: Optional[str] = Field(default=None, alias="birthCity")
    birth_state_province: Optional[str] = Field(default=None, alias="birthStateProvince")
    birth_country: Optional[str] = Field(default=None, alias="birthCountry")
    
    class Config:
        """Pydantic configuration."""
        allow_population_by_field_name = True
