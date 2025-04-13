from datetime import datetime
from typing import Dict, Any, List, Optional, Union
import httpx

from edgework.models.base import BaseNHLModel
from edgework.http_client import SyncHttpClient
from edgework.endpoints import API_PATH
from edgework.utilities import dict_camel_to_snake


class Player(BaseNHLModel):
    """
    Player model to store player information using a PRAW-like design pattern
    with lazy loading of attributes.
    
    This class implements a Reddit PRAW-like pattern where:
    1. Attributes are loaded lazily when accessed
    2. API data is cached to minimize requests
    3. Camel case keys from the API are converted to snake case
    """

    def __init__(self, edgework_client, obj_id=None, player_id=None, **kwargs):
        """
        Initialize a Player object.
        
        Args:
            edgework_client: The Edgework client
            obj_id: The ID of the player object
            player_id: Player ID is a unique identifier for the player
            **kwargs: Additional player attributes that can be set directly
        """
        super().__init__(edgework_client, obj_id)
        
        # Core identifier - prefer player_id over obj_id 
        self.player_id = player_id or obj_id
        
        # Initialize cache for API data
        self._raw_data = {}  # Raw API response (camelCase)
        self._data = {}      # Converted to snake_case
        self._game_logs = {}
        self._stats = {}
        
        # Store any kwargs as attributes
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        # Set up HTTP client
        if hasattr(edgework_client, 'http_client'):
            self._http_client = edgework_client.http_client
        else:
            self._http_client = SyncHttpClient()
    @property
    def full_name(self) -> str:
        """Get the full name of the player."""
        self._fetch_if_not_fetched()
        first_name = getattr(self, 'first_name', '')
        last_name = getattr(self, 'last_name', '')
        return f"{first_name} {last_name}".strip()

    def __str__(self):
        """Returns a string representation of the player."""
        self._fetch_if_not_fetched()
        team_abbr = getattr(self, 'current_team_abbr', '')
        return f"{self.full_name} {team_abbr}".strip()

    def __repr__(self):
        """Returns a string representation of the player for debugging."""
        return f"Player(id={self.player_id})"
        
    def fetch_data(self):
        """
        Fetch the player data from the NHL API.
        This implements the PRAW-like lazy loading pattern.
        """
        if not self.player_id:
            raise ValueError("Player ID is required to fetch player data")
        
        path = API_PATH["player_landing"].format(player_id=self.player_id)
        response = self._http_client.get(path)
        
        if response.status_code == 200:
            # Store the raw data (camelCase)
            self._raw_data = response.json()
            
            # Convert to snake_case for easier Python use
            self._data = dict_camel_to_snake(self._raw_data)
            
            # Update object attributes from API data
            self._update_attributes_from_data()
            self._fetched = True
            return self
        else:
            raise Exception(f"Failed to fetch player data: HTTP {response.status_code}")
    
    def _update_attributes_from_data(self):
        """
        Update player attributes from the snake_case API data.
        """
        # Core identification
        if 'player_id' in self._data:
            self.player_id = self._data['player_id']
        
        if 'player_slug' in self._data:
            self.player_slug = self._data['player_slug']
              # Define field mapping for simple direct assignments
        # format: api_field_name -> object_attribute_name
        field_mapping = {
            'is_active': 'is_active',
            'position': 'position',
            'shoots_catches': 'shoots_catches',
            'height_in_inches': 'height_in_inches',
            'weight_in_pounds': 'weight_in_pounds',
            'current_team_id': 'current_team_id', 
            'current_team_abbrev': 'current_team_abbrev',
            'sweater_number': 'sweater_number',
            'birth_country': 'birth_country',
            'headshot': 'headshot_url',
            'hero_image': 'hero_image_url'
        }
        
        # Handle simple field mappings
        for api_field, attr_name in field_mapping.items():
            if api_field in self._data:
                setattr(self, attr_name, self._data[api_field])
        
        # Handle nested fields with default value in a dictionary
        nested_default_fields = {
            'first_name': 'first_name',
            'last_name': 'last_name',
            'birth_city': 'birth_city',
            'birth_state_province': 'birth_state_province',
            'full_team_name': 'current_team_name'
        }
        
        for api_field, attr_name in nested_default_fields.items():
            if api_field in self._data and isinstance(self._data[api_field], dict):
                setattr(self, attr_name, self._data[api_field].get('default', ''))
        
        # Handle date fields with special parsing
        if 'birth_date' in self._data and self._data['birth_date']:
            try:
                self.birth_date = datetime.strptime(self._data['birth_date'], "%Y-%m-%d")
            except (ValueError, TypeError):
                pass
                
        # Handle complex nested structures
        if 'draft_details' in self._data and self._data['draft_details']:
            draft = self._data['draft_details']
            # Define draft field mappings
            draft_fields = {
                'year': 'draft_year',
                'round': 'draft_round',
                'pick_in_round': 'draft_pick',
                'overall_pick': 'draft_overall_pick',
                'team_abbrev': 'draft_team_abbr'
            }
            
            # Apply draft field mappings
            for api_field, attr_name in draft_fields.items():
                if api_field in draft:
                    setattr(self, attr_name, draft.get(api_field))
    
    def get_game_log(self, season: Optional[str] = None, game_type: int = 2) -> List[Dict[str, Any]]:
        """
        Get the game log for the player.
        
        Args:
            season: The season in format YYYYYYYY (e.g. "20232024")
            game_type: Game type (2 for regular season, 3 for playoffs)
            
        Returns:
            List of game log entries with snake_case keys
        """
        self._fetch_if_not_fetched()
        
        # Create a cache key for this specific request
        cache_key = f"{season or 'current'}_{game_type}"
        
        # Return cached result if we have it
        if cache_key in self._game_logs:
            return self._game_logs[cache_key]
            
        # Determine the path based on whether a season is specified
        if season:
            path = API_PATH["player_game_logs"].format(
                player_id=self.player_id,
                season=season,
                **{"game-type": game_type}  # Handle the hyphen in the URL param
            )
        else:
            path = API_PATH["player_game_log_now"].format(
                player_id=self.player_id
            )
                
        # Fetch the data
        response = self._http_client.get(path)
        
        if response.status_code == 200:
            raw_data = response.json()
            # Convert camelCase to snake_case
            data = dict_camel_to_snake(raw_data)
            game_logs = data.get("game_log", [])
            self._game_logs[cache_key] = game_logs
            return game_logs
        else:
            raise Exception(f"Failed to fetch game log: HTTP {response.status_code}")
    
    def get_stats(self, season: Optional[str] = None, game_type: int = 2) -> Dict[str, Any]:
        """
        Get the stats for the player.
        
        Args:
            season: The season in format YYYYYYYY (e.g. "20232024")
            game_type: Game type (2 for regular season, 3 for playoffs)
            
        Returns:
            Dictionary of player stats with snake_case keys
        """
        self._fetch_if_not_fetched()
        
        # Create a cache key for this specific request
        cache_key = f"{season or 'current'}_{game_type}"
        
        # Return cached result if we have it
        if cache_key in self._stats:
            return self._stats[cache_key]
            
        # For stats, we'll use the game log endpoint since it contains the season totals
        if season:
            path = API_PATH["player_game_logs"].format(
                player_id=self.player_id,
                season=season,
                **{"game-type": game_type}  # Handle the hyphen in the URL param
            )
        else:
            path = API_PATH["player_game_log_now"].format(
                player_id=self.player_id
            )
        
        # Fetch the data
        response = self._http_client.get(path)
        
        if response.status_code == 200:
            raw_data = response.json()
            # Convert camelCase to snake_case
            data = dict_camel_to_snake(raw_data)
            
            # Extract the season totals from the response
            stats = data.get("season_totals", {})
            self._stats[cache_key] = stats
            return stats
        else:
            raise Exception(f"Failed to fetch player stats: HTTP {response.status_code}")
    
    @classmethod
    def get(cls, player_id: int, edgework_client) -> 'Player':
        """
        Get a player by ID without immediately fetching data.
        Data will be fetched lazily when attributes are accessed.
        
        Args:
            player_id: The player ID
            edgework_client: The Edgework client
            
        Returns:
            A Player object
        """
        return cls(edgework_client, player_id=player_id)
    
    @classmethod
    def from_id(cls, player_id: int, edgework_client) -> 'Player':
        """
        Create a Player object from a player ID and immediately fetch data.
        
        Args:
            player_id: The player ID
            edgework_client: The Edgework client
            
        Returns:
            A fully loaded Player object
        """
        player = cls(edgework_client, player_id=player_id)
        player.fetch_data()  # Immediately fetch data
        return player
        
    @classmethod
    def from_api_data(cls, edgework_client, data: Dict[str, Any]) -> 'Player':
        """
        Create a Player object from API response data.
        
        Args:
            edgework_client: The Edgework client
            data: The API response data (in camelCase)
            
        Returns:
            A Player object
        """
        # First extract the player ID
        player_id = data.get("playerId")
        if not player_id:
            raise ValueError("API data must contain a playerId")
            
        # Create player instance
        player = cls(edgework_client, player_id=player_id)
        
        # Store and process the data
        player._raw_data = data
        player._data = dict_camel_to_snake(data)
        player._update_attributes_from_data()
        player._fetched = True
        
        return player
