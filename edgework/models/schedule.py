from datetime import datetime
from typing import List, Optional, Dict, TYPE_CHECKING

from edgework.models.base import BaseNHLModel

if TYPE_CHECKING:
    from edgework.models.game import Game


def schedule_api_to_dict(data: dict) -> dict:
    """Convert schedule API response data to schedule dictionary format."""
    # Extract games from gameWeek structure if present, otherwise use games directly
    games = data.get("games") or []
    if not games and "gameWeek" in data:
        games = [game for day in data.get("gameWeek", []) for game in day.get("games", [])]
    
    return {
        "previous_start_date": data.get("previousStartDate"),
        "games": games,
        "pre_season_start_date": data.get("preSeasonStartDate"),
        "regular_season_start_date": data.get("regularSeasonStartDate"),
        "regular_season_end_date": data.get("regularSeasonEndDate"),
        "playoff_end_date": data.get("playoffEndDate"),
        "number_of_games": data.get("numberOfGames", len(games))
    }


class Schedule(BaseNHLModel):
    """Schedule model to store schedule information."""
    
    def __init__(self, edgework_client, obj_id=None, **kwargs):
        """
        Initialize a Schedule object with dynamic attributes.
        
        Args:
            edgework_client: The Edgework client
            obj_id: The ID of the schedule (optional)
            **kwargs: Dynamic attributes for schedule properties
        """
        super().__init__(edgework_client, obj_id)
        self._data = kwargs
        self._games_objects: List[Game] = []
        
        # Initialize empty games list if not provided
        if 'games' not in self._data:
            self._data['games'] = []
            
        # Mark as fetched if we have data
        if kwargs:
            self._fetched = True

    def __str__(self):
        """String representation showing schedule summary."""
        num_games = self._data.get('number_of_games', 0)
        start_date = self._data.get('regular_season_start_date')
        end_date = self._data.get('regular_season_end_date')
        
        if start_date and end_date:
            if isinstance(start_date, str):
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            if isinstance(end_date, str):
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            return f"Schedule ({num_games} games): {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        elif num_games:
            return f"Schedule ({num_games} games)"
        else:
            return "Schedule"

    def __repr__(self):
        """Developer representation of the Schedule object."""
        return f"Schedule(games={len(self._data.get('games', []))})"

    @classmethod
    def from_dict(cls, edgework_client, data: dict) -> "Schedule":
        """
        Create a Schedule object from dictionary data.
        
        Args:
            edgework_client: The Edgework client
            data: Dictionary containing schedule data
            
        Returns:
            Schedule: A Schedule object
        """
        # Convert date strings to datetime objects if they exist
        processed_data = {}
        
        date_fields = [
            'previous_start_date', 'pre_season_start_date', 
            'regular_season_start_date', 'regular_season_end_date', 'playoff_end_date'
        ]
        
        for field in date_fields:
            if field in data and data[field]:
                try:
                    if isinstance(data[field], str):
                        processed_data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
                    else:
                        processed_data[field] = data[field]
                except (ValueError, TypeError):
                    processed_data[field] = data[field]
            else:
                processed_data[field] = data.get(field)
        
        # Copy other fields
        processed_data['games'] = data.get('games', [])
        processed_data['number_of_games'] = data.get('number_of_games', len(processed_data['games']))
        
        return cls(edgework_client=edgework_client, **processed_data)

    @classmethod 
    def from_api(cls, edgework_client, data: dict) -> "Schedule":
        """
        Create a Schedule object from raw API response data.
        
        Args:
            edgework_client: The Edgework client
            data: Raw API response data
            
        Returns:
            Schedule: A Schedule object
        """
        schedule_dict = schedule_api_to_dict(data)
        return cls.from_dict(edgework_client, schedule_dict)
        
    def fetch_data(self):
        """
        Fetch the data for the schedule.
        This method would be called if the schedule needs to be refreshed from the API.
        """
        if not self._client:
            raise ValueError("No client available to fetch schedule data")
          # For now, schedule data is typically loaded when created
        # If specific schedule fetching is needed, it would be implemented here
        pass

    @property 
    def games(self) -> List['Game']:
        """
        Get the games as Game objects.
        
        Returns:
            List[Game]: List of Game objects
        """
        if not self._games_objects and self._data.get('games'):
            # Lazy import to avoid circular dependencies
            from edgework.models.game import Game
            
            self._games_objects = []
            for game_data in self._data['games']:
                if self._client:
                    game = Game.from_api(game_data, self._client.http_client)
                    self._games_objects.append(game)
        return self._games_objects    @property
    def games_today(self) -> List['Game']:
        """
        Get games scheduled for today.
        
        Returns:
            List[Game]: List of games scheduled for today
        """
        today = datetime.now().date()
        return [game for game in self.games if game._data.get('game_date', '').date() == today]

    @property
    def upcoming_games(self) -> List['Game']:
        """
        Get upcoming games (future games only).
        
        Returns:
            List[Game]: List of upcoming games
        """
        now = datetime.now()
        return [game for game in self.games if game._data.get('start_time_utc', now) > now]

    @property 
    def completed_games(self) -> List['Game']:
        """
        Get completed games.
        
        Returns:
            List[Game]: List of completed games
        """
        return [game for game in self.games if game._data.get('game_state') in ['OFF', 'FINAL']]
