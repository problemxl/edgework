from datetime import datetime, timedelta
from edgework.models.base import BaseNHLModel
from edgework.utilities import dict_camel_to_snake

class StatEntity(BaseNHLModel):
    """
    PlayerStats model to store player statistics.
    """
    def __init__(self, edgework_client, id: int | None = None, data: dict | None = None):
        super().__init__(edgework_client, id)
        self._data = data
        self._fetched = True

class SkaterStats(BaseNHLModel):
    """
    SkaterStats model to store skater statistics.
    """
    def __init__(self, edgework_client, obj_id=None, **kwargs):
        """
        Initialize a SkaterStats object with dynamic attributes.
        """
        super().__init__(edgework_client, obj_id)
        players : list[StatEntity] = []
        self._data = kwargs

    def fetch_data(self, report: str = "summary", season: int = None, aggregate: bool = False, 
                  game: bool = True, limit: int = -1, start: int = 0, sort: str = "points"):
        """
        Fetch the data for the skater stats.
        
        Args:
            report: The type of report to get (e.g. "summary", "bios", etc.)
            season: The season to get stats for (e.g. 20232024)
            aggregate: Whether to aggregate the stats
            game: Whether to get game stats
            limit: Number of results to return (-1 for all)
            start: Starting index for results
            sort: Field to sort by
        """
        if not season:
            if datetime.now().month >= 7:
                season = datetime.now().year * 10000 + (datetime.now().year + 1)
                
            else:
                season = (datetime.now().year - 1) * 10000 + datetime.now().year
        print(f"Fetching skater stats for season: {season}")
        url_path = f"en/skater/{report}?isAggregate={aggregate}&isGame={game}&limit={limit}&start={start}&sort={sort}&cayenneExp=seasonId={season}"
        response = self._client.get(path=url_path, params=None, web=False)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch skater stats: {response.status_code} {response.text}")

        data = response.json()["data"]
        
        # Convert camelCase to snake_case and update data
        if data:
            self._data = data
            self.players = [StatEntity(self._client, data=dict_camel_to_snake(player)) for player in data]

class GoalieStats(BaseNHLModel):
    """
    GoalieStats model to store goalie statistics.
    """
    def __init__(self, edgework_client, obj_id=None, **kwargs):
        """
        Initialize a GoalieStats object with dynamic attributes.
        """
        super().__init__(edgework_client, obj_id)
        self._data = kwargs
        self.players : list[StatEntity] = []
    
    def fetch_data(self, report: str = "summary", season: int = None, aggregate: bool = False,
                  game: bool = True, limit: int = -1, start: int = 0, sort: str = "wins"):
        """
        Fetch the data for the goalie stats.
        
        Args:
            report: The type of report to get (e.g. "summary", "advanced", etc.)
            season: The season to get stats for (e.g. 20232024)
            aggregate: Whether to aggregate the stats
            game: Whether to get game stats
            limit: Number of results to return (-1 for all)
            start: Starting index for results
            sort: Field to sort by
        """
        if not season:
            season = datetime.now().year * 10000 + (datetime.now().year + 1)
            
        url_path = f"en/goalie/{report}?isAggregate={aggregate}&isGame={game}&limit={limit}&start={start}&sort={sort}&cayenneExp=seasonId={season}"
        response = self._client.get(path=url_path, params=None, web=False)
        data = response.json()["data"]
       
        if data:
            self._data = data
            self.players = [StatEntity(self._client, data=dict_camel_to_snake(player)) for player in data]


class TeamStats(BaseNHLModel):
    """Team Stats model to store team statistics for a season."""
    def __init__(self, edgework_client, obj_id=None, **kwargs):
        """
        Initialize a TeamStats object with dynamic attributes.
        """
        super().__init__(edgework_client, obj_id)
        self._data = kwargs
        self.teams : list[StatEntity] = []
        
    def fetch_data(self, report: str = "summary", season: int = None, aggregate: bool = False,
                  game: bool = True, limit: int = -1, start: int = 0, sort: str = "wins"):
        """
        Fetch the data for the team stats.
        
        Args:
            report: The type of report to get (e.g. "summary", "faceoffpercentages", etc.)
            season: The season to get stats for (e.g. 20232024)
            aggregate: Whether to aggregate the stats
            game: Whether to get game stats
            limit: Number of results to return (-1 for all)
            start: Starting index for results
            sort: Field to sort by
        """
        if not season:
            season = datetime.now().year * 10000 + (datetime.now().year + 1)
            
        url_path = f"en/team/{report}?isAggregate={aggregate}&isGame={game}&limit={limit}&start={start}&sort={sort}&cayenneExp=seasonId={season}"
        response = self._client.get(path=url_path, params=None, web=False)
        print(response.url)
        data = response.json()["data"]
        data = [dict_camel_to_snake(d) for d in data]
        if data:
            self._data = data
            self.teams = [StatEntity(self._client, data=team) for team in data]