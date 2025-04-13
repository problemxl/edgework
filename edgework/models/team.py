from edgework.models.base import BaseNHLModel
from edgework.models.player import Player


class Roster(BaseNHLModel):
    """Roster model to store a team's roster information."""
    
    def __init__(self, edgework_client, obj_id=None, players=None):
        """
        Initialize a Roster object.
        
        Args:
            edgework_client: The Edgework client
            obj_id: The ID of the roster
            players: List of players on the roster
        """
        super().__init__(edgework_client, obj_id)
        self.players = players or []

    @property
    def forwards(self):
        return [p for p in self.players if p.position == "C" or p.position == "LW" or p.position == "RW"]
    
    @property
    def defensemen(self):
        return [p for p in self.players if p.position == "D"]
    
    @property
    def goalies(self):
        return [p for p in self.players if p.position == "G"]
    
    def fetch_data(self):
        """
        Fetch the data for the roster.
        """
        # Implementation depends on how data is fetched from the API
        pass
            

class Team(BaseNHLModel):
    """Team model to store team information."""
    
    def __init__(self, edgework_client, obj_id=None, id=None, abbreviation=None, 
                 name=None, roster=None):
        """
        Initialize a Team object.
        
        Args:
            edgework_client: The Edgework client
            obj_id: The ID of the team object
            id: Unique identifier for the team
            abbreviation: Abbreviated form of the team name
            name: Full name of the team
            roster: Roster of players on the team
        """
        super().__init__(edgework_client, obj_id)
        self.id = id
        self.abbreviation = abbreviation
        self.name = name
        self.roster = roster
    
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