<<<<<<< HEAD
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
=======
from datetime import datetime
from edgework.models.base import BaseNHLModel


class Player(BaseNHLModel):
    """Player model to store player information."""
    
    def __init__(self, edgework_client=None, obj_id=None, **kwargs):
        """
        Initialize a Player object with dynamic attributes.
        
        Args:
            edgework_client: The Edgework client (optional for player data from API)
            obj_id: The ID of the player object
            **kwargs: Dynamic attributes for player properties
        """
        super().__init__(edgework_client, obj_id)
        self._data = kwargs
        
        # Set the player_id as obj_id if provided in kwargs
        if 'player_id' in kwargs:
            self.obj_id = kwargs['player_id']
        
        # Mark as fetched since we're initializing with data
        self._fetched = True

    def __str__(self):
        """String representation showing player name and number."""
        first_name = self._data.get('first_name', '')
        last_name = self._data.get('last_name', '')
        sweater_number = self._data.get('sweater_number')
        team_abbr = self._data.get('current_team_abbr', '')
        
        name = f"{first_name} {last_name}".strip()
        if sweater_number and team_abbr:
            return f"#{sweater_number} {name} ({team_abbr})"
        elif team_abbr:
            return f"{name} ({team_abbr})"
        elif sweater_number:
            return f"#{sweater_number} {name}"
        else:
            return name

    def __repr__(self):
        """Developer representation of the Player object."""
        player_id = self._data.get('player_id', self.obj_id)
        return f"Player(id={player_id})"

    def __eq__(self, other):
        """Compare players by their player_id."""
        if isinstance(other, Player):
            return self._data.get('player_id') == other._data.get('player_id')
        return False

    def __hash__(self):
        """Hash based on player_id for use in sets and dicts."""
        return hash(self._data.get('player_id'))
        
    def fetch_data(self):
        """
        Fetch the data for the player from the API.
        Note: This would require the player_id and client to be set.
        """
        if not self._client:
            raise ValueError("No client available to fetch player data")
        if not self.obj_id:
            raise ValueError("No player ID available to fetch data")
        
        # This would be implemented if we need to fetch individual player details
        # For now, players are typically created with all data from the search API
        pass

    @property
    def full_name(self):
        """Get the player's full name."""
        first_name = self._data.get('first_name', '')
        last_name = self._data.get('last_name', '')
        return f"{first_name} {last_name}".strip()

    @property
    def name(self):
        """Alias for full_name."""
        return self.full_name

    @property
    def age(self):
        """Calculate player's age from birth_date."""
        birth_date = self._data.get('birth_date')
        if birth_date:
            if isinstance(birth_date, str):
                birth_date = datetime.fromisoformat(birth_date.replace('Z', '+00:00'))
            elif isinstance(birth_date, datetime):
                pass
            else:
                return None
            
            today = datetime.now()
            age = today.year - birth_date.year
            if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
                age -= 1
            return age
        return None
>>>>>>> origin/main
