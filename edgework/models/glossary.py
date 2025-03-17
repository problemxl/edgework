from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

class Term(BaseModel):
    id: int = Field(description="Unique identifier for the term")
    abbreviation: str = Field(description="Abbreviated form of the term")
    definition: str = Field(description="Full definition of the term")
    first_season: int = Field(description="First season this term was used")
    last_updated: datetime = Field(description="When this term was last updated")

class Glossary(BaseModel):
    terms: List[Term] = Field(description="List of terminology entries")
