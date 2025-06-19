"""Player client for fetching player data from NHL APIs."""

from datetime import datetime
from typing import List, Optional
from edgework.http_client import SyncHttpClient
from edgework.models.player import Player


def api_to_dict(data: dict) -> dict:
    """Convert API response data to player dictionary format."""
    name = data.get('name', '')
    slug = f"{name.replace(' ', '-').lower()}-{data.get('playerId')}" if name else f"player-{data.get('playerId')}"
    
    # Split name into first and last name
    name_parts = name.split(' ') if name else []
    first_name = name_parts[0] if name_parts else ""
    last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ""
    
    return {
        "player_id": int(data.get("playerId")) if data.get("playerId") else None,
        "first_name": first_name,
        "last_name": last_name,
        "player_slug": slug,
        "sweater_number": data.get("sweaterNumber"),
        "birth_date": data.get("birthDate"),  # This field doesn't seem to be in the search API
        "birth_city": data.get("birthCity"),
        "birth_country": data.get("birthCountry"),
        "birth_state_province": data.get("birthStateProvince"),
        "height": data.get("heightInCentimeters"),
        "height_inches": data.get("heightInInches"),
        "height_formatted": data.get("height"),
        "weight": data.get("weightInKilograms"),
        "weight_pounds": data.get("weightInPounds"),
        "position": data.get("positionCode"),
        "is_active": data.get("active"),
        "current_team_id": int(data.get("teamId")) if data.get("teamId") else None,
        "current_team_abbr": data.get("teamAbbrev"),
        "last_team_id": int(data.get("lastTeamId")) if data.get("lastTeamId") else None,
        "last_team_abbr": data.get("lastTeamAbbrev"),
        "last_season_id": data.get("lastSeasonId")
    }

def landing_to_dict(data: dict) -> dict:
    """Convert landing page API response data to player dictionary format."""
    birth_date = None
    if data.get("birthDate"):
        try:
            birth_date = datetime.strptime(data.get("birthDate"), "%Y-%m-%d")
        except (ValueError, TypeError):
            birth_date = None
    
    draft_year = None
    if data.get("draftDetails", {}).get("year"):
        try:
            draft_year = datetime(data.get("draftDetails", {}).get("year"), 1, 1)
        except (ValueError, TypeError):
            draft_year = None
    
    return {
        "player_id": int(data.get("playerId")) if data.get("playerId") else None,
        "player_slug": data.get("playerSlug"),
        "birth_city": data.get("birthCity", {}).get("default") if isinstance(data.get("birthCity"), dict) else data.get("birthCity"),
        "birth_country": data.get("birthCountry"),
        "birth_date": birth_date,
        "birth_state_province": data.get("birthStateProvince", {}).get("default") if isinstance(data.get("birthStateProvince"), dict) else data.get("birthStateProvince"),
        "current_team_abbr": data.get("currentTeamAbbrev"),
        "current_team_id": data.get("currentTeamId"),
        "current_team_name": data.get("fullTeamName", {}).get("default") if isinstance(data.get("fullTeamName"), dict) else data.get("fullTeamName"),
        "draft_overall_pick": data.get("draftDetails", {}).get("overallPick"),
        "draft_pick": data.get("draftDetails", {}).get("pickInRound"),
        "draft_round": data.get("draftDetails", {}).get("round"),
        "draft_team_abbr": data.get("draftDetails", {}).get("teamAbbrev"),
        "draft_year": draft_year,
        "first_name": data.get("firstName", {}).get("default") if isinstance(data.get("firstName"), dict) else data.get("firstName"),
        "last_name": data.get("lastName", {}).get("default") if isinstance(data.get("lastName"), dict) else data.get("lastName"),
        "headshot_url": data.get("headshot"),
        "height": data.get("heightInInches"),
        "hero_image_url": data.get("heroImage"),
        "is_active": data.get("isActive"),
        "position": data.get("position"),
        "shoots_catches": data.get("shootsCatches"),
        "sweater_number": data.get("sweaterNumber"),
        "weight": data.get("weightInPounds")
    }
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
        
        response = self.client.get_raw(self.base_url, params=params)
        data = response.json()
        
        # The API returns a list directly, not a dict with "results"
        if isinstance(data, list):
            players_data = data
        else:
            # Fallback in case the API structure changes
            players_data = data.get("results", [])
            
        return [Player(**api_to_dict(player)) for player in players_data]
        
    
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
