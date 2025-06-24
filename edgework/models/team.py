from typing import Optional, List, Union
from datetime import datetime
from edgework.models.base import BaseNHLModel
from edgework.models.player import Player


def roster_api_to_dict(data: dict) -> dict:
    """Convert roster API response data to roster dictionary format."""
    # The API returns forwards, defensemen, goalies arrays directly
    players = []
    players.extend(data.get("forwards", []))
    players.extend(data.get("defensemen", []))
    players.extend(data.get("goalies", []))
    
    return {
        "season": data.get("season"),
        "roster_type": data.get("rosterType"), 
        "team_abbrev": data.get("teamAbbrev"),
        "team_id": data.get("teamId"),
        "players": players
    }


def team_api_to_dict(data: dict) -> dict:
    """Convert team API response data to team dictionary format."""
    # Helper function to extract default value from nested dict
    def extract_default(value):
        if isinstance(value, dict) and 'default' in value:
            return value['default']
        return value
    
    # For standings API, the team data is in the root level
    return {
        "team_id": data.get("teamId") or data.get("id"),
        "team_abbrev": extract_default(data.get("teamAbbrev")) or extract_default(data.get("abbrev")),
        "team_name": extract_default(data.get("teamName")) or extract_default(data.get("name")) or extract_default(data.get("teamCommonName")),
        "full_name": extract_default(data.get("fullName")) or extract_default(data.get("teamName")),
        "location_name": extract_default(data.get("locationName")) or extract_default(data.get("placeName")),
        "team_common_name": extract_default(data.get("teamCommonName")),
        "team_place_name": extract_default(data.get("teamPlaceName")) or extract_default(data.get("placeName")),
        "logo": data.get("logo") or data.get("teamLogo"),
        "dark_logo": data.get("darkLogo"),
        "french_name": data.get("frenchName"),
        "french_place_name": data.get("frenchPlaceName"),
        "venue": data.get("venue"),
        "conference": data.get("conferenceName"),
        "division": data.get("divisionName"),
        "website": data.get("website"),
        "franchise_id": data.get("franchiseId"),
        "active": data.get("active", True)
    }


class Roster(BaseNHLModel):
    """Roster model to store a team's roster information."""
    
    def __init__(self, edgework_client, obj_id=None, **kwargs):
        """
        Initialize a Roster object with dynamic attributes.
        
        Args:
            edgework_client: The Edgework client
            obj_id: The ID of the roster (team_id)
            **kwargs: Dynamic attributes for roster properties
        """
        super().__init__(edgework_client, obj_id)
        self._data = kwargs
        self._players: List[Player] = []
        
        # Process players data if provided
        if 'players' in self._data and self._data['players']:
            self._process_players()
          # Mark as fetched if we have data
        if kwargs:
            self._fetched = True

    def _process_players(self):
        """Process raw player data into Player objects."""
        players_data = self._data.get('players', [])
        self._players = []
        
        for player_data in players_data:
            # Handle nested name structure
            first_name = player_data.get("firstName", {})
            if isinstance(first_name, dict):
                first_name = first_name.get("default", "")
            
            last_name = player_data.get("lastName", {})
            if isinstance(last_name, dict):
                last_name = last_name.get("default", "")
            
            birth_city = player_data.get("birthCity", {})
            if isinstance(birth_city, dict):
                birth_city = birth_city.get("default", "")
            
            birth_country = player_data.get("birthCountry", "")
            if isinstance(birth_country, dict):
                birth_country = birth_country.get("default", "")
            
            birth_state_province = player_data.get("birthStateProvince", {})
            if isinstance(birth_state_province, dict):
                birth_state_province = birth_state_province.get("default", "")
            
            # Convert player data to expected format
            player_dict = {
                "player_id": player_data.get("id"),
                "first_name": first_name,
                "last_name": last_name,
                "sweater_number": player_data.get("sweaterNumber"),
                "position": player_data.get("positionCode"),
                "shoots_catches": player_data.get("shootsCatches"),
                "height": player_data.get("heightInCentimeters"),
                "weight": player_data.get("weightInKilograms"),
                "birth_date": player_data.get("birthDate"),
                "birth_city": birth_city,
                "birth_country": birth_country,
                "birth_state_province": birth_state_province,
                "current_team_id": self._data.get("team_id"),
                "current_team_abbr": self._data.get("team_abbrev"),
                "is_active": True,
                "headshot": player_data.get("headshot")
            }
            
            player = Player(self._client, player_dict["player_id"], **player_dict)
            self._players.append(player)

    @property
    def players(self) -> List[Player]:
        """
        Get all players in the roster.
        
        Returns:
            List[Player]: List of all players in the roster.
        """
        return self._players

    def get_player_by_number(self, sweater_number: int) -> Optional[Player]:
        """
        Get a player by their sweater number.
        
        Args:
            sweater_number: The player's sweater number
            
        Returns:
            Player: The player with the given number, or None if not found.
        """
        for player in self._players:
            if player.sweater_number == sweater_number:
                return player
        return None

    def get_player_by_name(self, name: str) -> Optional[Player]:
        """
        Get a player by their full name.
        
        Args:
            name: The player's full name
            
        Returns:
            Player: The player with the given name, or None if not found.
        """
        for player in self._players:
            if player.full_name == name:
                return player
        return None

    @property
    def forwards(self) -> list[Player]:
        """
        Get the forwards from the roster.
        
        Returns:
            list[Player]: List of forwards in the roster.
        """
        return [p for p in self._players if p.position in {"C", "LW", "RW"}]
    
    @property
    def defensemen(self) -> list[Player]:
        """
        Get the defensemen from the roster.
        
        Returns:
            list[Player]: List of defensemen in the roster.
        """
        return [p for p in self._players if p.position == "D"]
    
    @property
    def goalies(self) -> list[Player]:
        """
        Get the goalies from the roster.
        
        Returns:
            list[Player]: List of goalies in the roster.
        """
        return [p for p in self._players if p.position == "G"]
    
    def fetch_data(self):
        """
        Fetch the roster data from the API.
        """
        if not self._client:
            raise ValueError("No client available to fetch roster data")
        if not self.obj_id:
            raise ValueError("No team ID available to fetch roster data")
          # Use current roster endpoint
        response = self._client.get(f"roster/{self.obj_id}/current", web=True)
        
        if response.status_code != 200:
            raise Exception(f"Failed to fetch roster: {response.status_code} {response.text}")
        
        data = response.json()
        self._data = roster_api_to_dict(data)
        self._process_players()
        self._fetched = True


class Team(BaseNHLModel):
    """Team model to store team information."""    
    
    def __init__(self, edgework_client, obj_id=None, **kwargs):
        """
        Initialize a Team object with dynamic attributes.
        
        Args:
            edgework_client: The Edgework client
            obj_id: The ID of the team object
            **kwargs: Dynamic attributes for team properties
        """
        super().__init__(edgework_client, obj_id)
        self._data = kwargs
        
        # Set team_id as obj_id if provided in kwargs
        if 'team_id' in kwargs:
            self.obj_id = kwargs['team_id']
        
        # Mark as fetched if we have data
        if kwargs:
            self._fetched = True

    def __str__(self):
        """String representation showing team name."""
        name = self._data.get('team_name') or self._data.get('full_name') or 'Unknown Team'
        return name

    def __repr__(self):
        """Developer representation of the Team object."""
        team_id = self._data.get('team_id', self.obj_id)
        abbrev = self._data.get('team_abbrev', 'UNK')
        return f"Team(id={team_id}, abbrev='{abbrev}')"

    def __eq__(self, other):
        """Compare teams by their team_id."""
        if isinstance(other, Team):
            return self._data.get('team_id') == other._data.get('team_id')
        return False

    def __hash__(self):
        """Hash based on team_id for use in sets and dicts."""
        return hash(self._data.get('team_id'))

    @property
    def name(self) -> str:
        """Get the team's name."""
        return self._data.get('team_name') or self._data.get('full_name') or 'Unknown Team'

    @property
    def abbrev(self) -> str:
        """Get the team's abbreviation."""
        return self._data.get('team_abbrev', 'UNK')

    @property
    def full_name(self) -> str:
        """Get the team's full name."""
        return self._data.get('full_name') or self.name

    @property
    def location(self) -> str:
        """Get the team's location."""
        return self._data.get('location_name', '')

    @property
    def common_name(self) -> str:
        """Get the team's common name."""
        return self._data.get('team_common_name', '')

    def get_roster(self, season: Optional[int] = None) -> Roster:
        """
        Get the roster for this team.
        
        Args:
            season: Optional season (e.g., 20232024). If None, gets current roster.
            
        Returns:
            Roster: The team's roster.
        """
        if not self._client:
            raise ValueError("No client available to fetch roster")
        
        team_abbrev = self.abbrev
        if season:
            response = self._client.get(f"roster/{team_abbrev}/{season}", web=True)
        else:
            response = self._client.get(f"roster/{team_abbrev}/current", web=True)
        
        if response.status_code != 200:
            raise Exception(f"Failed to fetch roster: {response.status_code} {response.text}")
        
        data = response.json()
        roster_data = roster_api_to_dict(data)
        roster_data['team_id'] = self._data.get('team_id')
        roster_data['team_abbrev'] = team_abbrev
        
        return Roster(self._client, self._data.get('team_id'), **roster_data)

    def get_stats(self, season: Optional[int] = None, game_type: int = 2):
        """
        Get team stats.
        
        Args:
            season: Optional season (e.g., 20232024). If None, gets current season.
            game_type: Game type (2 for regular season, 3 for playoffs).
            
        Returns:
            Response with team stats.
        """
        if not self._client:
            raise ValueError("No client available to fetch stats")
        
        team_abbrev = self.abbrev
        if season:
            response = self._client.get(f"club-stats/{team_abbrev}/{season}/{game_type}", web=True)
        else:
            response = self._client.get(f"club-stats/{team_abbrev}/now", web=True)
        
        return response

    def get_schedule(self, season: Optional[int] = None):
        """
        Get team schedule.
        
        Args:
            season: Optional season (e.g., 20232024). If None, gets current season.
            
        Returns:
            Response with team schedule.
        """
        if not self._client:
            raise ValueError("No client available to fetch schedule")
        
        team_abbrev = self.abbrev
        if season:
            response = self._client.get(f"club-schedule-season/{team_abbrev}/{season}", web=True)
        else:
            response = self._client.get(f"club-schedule-season/{team_abbrev}/now", web=True)
        
        return response

    def get_prospects(self):
        """
        Get team prospects.
        
        Returns:
            Response with team prospects.
        """
        if not self._client:
            raise ValueError("No client available to fetch prospects")
        
        team_abbrev = self.abbrev
        response = self._client.get(f"prospects/{team_abbrev}", web=True)
        
        return response
        
    def fetch_data(self):
        """
        Fetch the team data from the API.
        Note: This implementation assumes team data is provided at initialization.
        Individual team endpoints may not exist in the current API.
        """
        # Most team data comes from roster, standings, or stats endpoints
        # Individual team detail endpoints may not be available
        if not self._fetched:
            self._fetched = True