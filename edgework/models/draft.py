from datetime import datetime
from edgework.models.base import BaseNHLModel

class Draftee(BaseNHLModel):
    """
    This class represents a NHL draftee.
    """
    def __init__(self, edgework_client, obj_id=None, first_name=None, last_name=None, 
                 position=None, shoots_catches=None, height=None, weight=None,
                 last_amateur_team=None, last_amateur_league=None, birth_date=None,
                 birth_city=None, birth_state=None, birth_country=None, rank=None):
        """
        Initialize a Draftee object.
        
        Args:
            edgework_client: The Edgework client
            obj_id: The ID of the draftee
            first_name: The first name of the draftee
            last_name: The last name of the draftee
            position: The position of the draftee. 'C', 'LW', 'RW', 'D', 'G'
            shoots_catches: The hand the draftee shoots/catches with. 'L', 'R'
            height: The height of the draftee. Units are in inches
            weight: The weight of the draftee. Units are in pounds
            last_amateur_team: The last amateur team of the draftee
            last_amateur_league: The last amateur league of the draftee
            birth_date: The birth date of the draftee
            birth_city: The birth city of the draftee
            birth_state: The birth state of the draftee
            birth_country: The birth country of the draftee
            rank: The rank of the draftee
        """
        super().__init__(edgework_client, obj_id)
        self.first_name = first_name
        self.last_name = last_name
        self.position = position
        self.shoots_catches = shoots_catches
        self.height = height
        self.weight = weight
        self.last_amateur_team = last_amateur_team
        self.last_amateur_league = last_amateur_league
        self.birth_date = birth_date
        self.birth_city = birth_city
        self.birth_state = birth_state
        self.birth_country = birth_country
        self.rank = rank
        
    def fetch_data(self):
        """
        Fetch the data for the draftee.
        """
        # Implementation depends on how data is fetched from the API
        pass

class DraftRanking(BaseNHLModel):
    """
    This class represents a NHL draft ranking.
    """
    def __init__(self, edgework_client, obj_id=None, year=None, category_id=None,
                 category=None, draftees=None):
        """
        Initialize a DraftRanking object.
        
        Args:
            edgework_client: The Edgework client
            obj_id: The ID of the draft ranking
            year: The year of the draft
            category_id: The category id of the draft
            category: The category of the draft. 'north-american-skater', 'north-american-goalie', 
                      'international-skater', 'international-goalie'
            draftees: The draftees in the draft ranking
        """
        super().__init__(edgework_client, obj_id)
        self.year = year
        self.category_id = category_id
        self.category = category
        self.draftees = draftees or []
    
    def fetch_data(self):
        """
        Fetch the data for the draft ranking.
        """
        # Implementation depends on how data is fetched from the API
        pass

class Draft(BaseNHLModel):
    """
    This class represents a NHL draft.
    """
    def __init__(self, edgework_client, obj_id=None, year=None, rounds=None):
        """
        Initialize a Draft object.
        
        Args:
            edgework_client: The Edgework client
            obj_id: The ID of the draft
            year: The year of the draft
            rounds: The rounds in the draft
        """
        super().__init__(edgework_client, obj_id)
        self.year = year
        self.rounds = rounds or []
    
    def fetch_data(self):
        """
        Fetch the data for the draft.
        """
        # Implementation depends on how data is fetched from the API
        pass
    