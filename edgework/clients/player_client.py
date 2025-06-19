"""Player client for fetching player data from NHL APIs."""

from typing import List, Optional
from edgework.http_client import SyncHttpClient
from edgework.models.player import Player


class PlayerClient:
    """Client for fetching player data."""
    
    def __init__(self, http_client: SyncHttpClient):
        """
        Initialize the player client.
        
        Args:
            http_client: HTTP client instance
        """
        self.client = http_client
        self.base_url = "https://search.d3.nhle.com/api/v1/search/player"
    
    def get_all_players(self, active: Optional[bool] = None, limit: int = 10000) -> List[Player]:
        """
        Get all players from the NHL search API.
        
        Args:
            active: Filter by active status (True for active, False for inactive, None for all)
            limit: Maximum number of players to return
            
        Returns:
            List of Player objects
        """
        params = {
            "culture": "en-us",
            "limit": limit,
            "q": "*"
        }
        
        if active is not None:
            params["active"] = str(active).lower()
        
        response = self.client.get(self.base_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        players_data = data.get("results", [])
        
        return [Player(**player_data) for player_data in players_data]
    
    def get_active_players(self, limit: int = 10000) -> List[Player]:
        """
        Get all active players.
        
        Args:
            limit: Maximum number of players to return
            
        Returns:
            List of active Player objects
        """
        return self.get_all_players(active=True, limit=limit)
    
    def get_inactive_players(self, limit: int = 10000) -> List[Player]:
        """
        Get all inactive players.
        
        Args:
            limit: Maximum number of players to return
            
        Returns:
            List of inactive Player objects
        """
        return self.get_all_players(active=False, limit=limit)
