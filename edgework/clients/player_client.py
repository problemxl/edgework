"""Player client for fetching player data from NHL APIs."""

from typing import List, Optional
from edgework.http_client import SyncHttpClient
from edgework.models.player import Player


def api_to_dict(data: dict) -> dict:
    slug = f"{data.get('name').replace(' ', '-').lower()}-{data.get('playerId')}"
    return {
        "player_id": int(data.get("playerId")) if data.get("playerId") else None,
        "first_name": data.get("name").split(" ")[0] if data.get("name") else "",
        "last_name": data.get("name").split(" ")[1] if data.get("name") and len(data.get("name").split(" ")) > 1 else "",
        "player_slug": slug,
        "sweater_number": data.get("sweaterNumber"),
        "birth_date": data.get("birthDate"),
        "birth_city": data.get("birthCity"),
        "birth_country": data.get("birthCountry"),
        "birth_state_province": data.get("birthStateProvince"),
        "height": data.get("heightInCentimeters"),
        "weight": data.get("weightInKilograms"),
        "position": data.get("positionCode"),
        "is_active": data.get("active"),
        "current_team_id": data.get("teamId") if data.get("teamId") else data.get("lastTeamId"),
        "current_team_abbr": data.get("teamAbbrev") if data.get("teamAbbrev") else data.get("lastTeamAbbrev")
    }

def landing_to_dict(data: dict) -> dict:
    return {
        "player_id": int(data.get("playerId")) if data.get("playerId") else None,
        "player_slug": data.get("playerSlug"),
        "birth_city": data.get("birthCity", {}).get("default"),
        "birth_country": data.get("birthCountry"),
        "birth_date": datetime.strptime(data.get("birthDate"), "%Y-%m-%d"),
        "birth_state_province": data.get("birthStateProvince", {}).get("default"),
        "current_team_abbr": data.get("currentTeamAbbrev"),
        "current_team_id": data.get("currentTeamId"),
        "current_team_name": data.get("fullTeamName", {}).get("default"),
        "draft_overall_pick": data.get("draftDetails", {}).get("overallPick"),
        "draft_pick": data.get("draftDetails", {}).get("pickInRound"),
        "draft_round": data.get("draftDetails", {}).get("round"),
        "draft_team_abbr": data.get("draftDetails", {}).get("teamAbbrev"),
        "draft_year": datetime(data.get("draftDetails", {}).get("year"), 1, 1),
        "first_name": data.get("firstName", {}).get("default"),
        "last_name": data.get("lastName", {}).get("default"),
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
        
        response = self.client.get(self.base_url, params=params)
        response.raise_for_status()
        data = response.json()
        players_data = data.get("results", [])
        return [Player(**api_to_dict(player)) for player in players_data]
        
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
