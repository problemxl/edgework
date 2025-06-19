from edgework.http_client import SyncHttpClient
from edgework.clients.player_client import PlayerClient
from edgework.models.player import Player
from typing import List, Optional

# Import the SkaterStats model - commented out until stats module is available
# from edgework.models.stats import SkaterStats, GoalieStats, TeamStats


class Edgework:
    def __init__(self, user_agent: str = "EdgeworkClient/1.0"):
        """
        Initializes the Edgework API client.

        Args:
            user_agent (str, optional): The User-Agent string to use for requests.
                                        Defaults to "EdgeworkClient/1.0".
        """
        self._client = SyncHttpClient(user_agent=user_agent)

        # Initialize player client
        self.player_client = PlayerClient(self._client)

        # Initialize model handlers, passing the shared HTTP client
        # TODO: Uncomment when stats models are available
        # self.skaters = SkaterStats(edgework_client=self._client)
        # self.goalies = GoalieStats(edgework_client=self._client)
        # self.teams = TeamStats(edgework_client=self._client)

    def get_all_players(self, active: Optional[bool] = None, limit: int = 10000) -> List[Player]:
        """
        Fetch a list of all players.
        
        Args:
            active: Filter by active status (True for active, False for inactive, None for all)
            limit: Maximum number of players to return
            
        Returns:
            List of Player objects
        """
        return self.player_client.get_all_players(active=active, limit=limit)
    
    def get_active_players(self, limit: int = 10000) -> List[Player]:
        """
        Fetch all active players.
        
        Args:
            limit: Maximum number of players to return
            
        Returns:
            List of active Player objects
        """
        return self.player_client.get_active_players(limit=limit)
    
    def get_inactive_players(self, limit: int = 10000) -> List[Player]:
        """
        Fetch all inactive players.
        
        Args:
            limit: Maximum number of players to return
            
        Returns:
            List of inactive Player objects
        """
        return self.player_client.get_inactive_players(limit=limit)    # TODO: Uncomment and implement when stats models are available
    # def skater_stats(self, ...):
    # def goalie_stats(self, ...):  
    # def team_stats(self, ...):

    def close(self):
        """Closes the underlying HTTP client session."""
        if hasattr(self._client, "close"):
            self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
