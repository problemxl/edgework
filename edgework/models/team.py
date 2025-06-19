from edgework.models.base import BaseNHLModel
from edgework.models.player import Player


class Roster(BaseNHLModel):
    """Roster model to store a team's roster information."""
    
    def __init__(self, edgework_client, obj_id=None, **kwargs):
        """
        Initialize a Roster object with dynamic attributes.
        
        Args:
            edgework_client: The Edgework client
            obj_id: The ID of the roster
            **kwargs: Dynamic attributes for roster properties
        """
        super().__init__(edgework_client, obj_id)
        self._data = kwargs
        # Initialize empty players list if not provided
        if 'players' not in self._data:
            self._data['players'] = []

    @property
    def forwards(self):
        return [p for p in self._data['players'] if p.position == "C" or p.position == "LW" or p.position == "RW"]
    
    @property
    def defensemen(self):
        return [p for p in self._data['players'] if p.position == "D"]
    
    @property
    def goalies(self):
        return [p for p in self._data['players'] if p.position == "G"]
    
    def fetch_data(self):
        """
        Fetch the data for the roster.
        """
        # Implementation depends on how data is fetched from the API
        pass
            


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

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, Team):
            return self.id == other.id
        return False
        
    def fetch_data(self):
        """
        Fetch the data for the team.
        """
        # Implementation depends on how data is fetched from the API
        pass