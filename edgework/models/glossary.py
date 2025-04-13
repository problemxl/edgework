from datetime import datetime
from typing import List
from edgework.models.base import BaseNHLModel

class Term(BaseNHLModel):
    """Term model to store terminology information."""
    
    def __init__(self, edgework_client, obj_id=None, id=None, abbreviation=None, 
                 definition=None, first_season=None, last_updated=None):
        """
        Initialize a Term object.
        
        Args:
            edgework_client: The Edgework client
            obj_id: The ID of the term object
            id: Unique identifier for the term
            abbreviation: Abbreviated form of the term
            definition: Full definition of the term
            first_season: First season this term was used
            last_updated: When this term was last updated
        """
        super().__init__(edgework_client, obj_id)
        self.id = id
        self.abbreviation = abbreviation
        self.definition = definition
        self.first_season = first_season
        self.last_updated = last_updated
        
    def fetch_data(self):
        """
        Fetch the data for the term.
        """
        # Implementation depends on how data is fetched from the API
        pass

class Glossary(BaseNHLModel):
    """Glossary model to store terminology entries."""
    
    def __init__(self, edgework_client, obj_id=None, terms=None):
        """
        Initialize a Glossary object.
        
        Args:
            edgework_client: The Edgework client
            obj_id: The ID of the glossary
            terms: List of terminology entries
        """
        super().__init__(edgework_client, obj_id)
        self.terms = terms or []
        
    def fetch_data(self):
        """
        Fetch the data for the glossary.
        """
        # Implementation depends on how data is fetched from the API
        pass
