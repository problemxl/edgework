from dataclasses import dataclass
from datetime import datetime


@dataclass
class Term:
    """
    Term dataclass to store term information.

    Attributes:
    id (int): The ID of the term.
    abbreviation (str): The abbreviation of the term.
    definition (str): The definition of the term.
    first_season (int): The first season the term was used.
    last_updated (datetime): The last time the term was updated.
    """

    id: int
    abbreviation: str
    definition: str
    first_season: int
    last_updated: datetime


@dataclass
class Glossary:
    """
    Glossary dataclass to store glossary information.

    Attributes:
    terms (lists[Term]): A list of terms in the glossary.
    """

    terms: list[Term]
