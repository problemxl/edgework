from dataclasses import dataclass
from datetime import datetime

@dataclass
class Player:
    """
    Player dataclass to store player information.

    Attributes:
        player_id (int): Player ID is a unique identifier for the player.
        player_slug (str): Player slug is a unique identifier for the player.
        birth_city (str): The city where the player was born.
        birth_country (str): The country where the player was born.
        birth_date (datetime): The birth date of the player.
        birth_state_province (str): The state or province where the player was born.
        current_team_abbr (str): The abbreviation of the current team the player is on.
        current_team_id (int): The ID of the current team the player is on.
        current_team_name (str): The name of the current team the player is on.
        draft_overall_pick (int): The overall pick number in the draft.
        draft_pick (int): The pick number in the draft.
        draft_round (int): The round number in the draft.
        draft_team_abbr (str): The abbreviation of the team that drafted the player.
        draft_year (datetime): The year the player was drafted.
        first_name (str): The first name of the player.
        last_name (str): The last name of the player.
        headshot_url (str): The URL of the player's headshot image.
        height (int): The height of the player in inches.
        hero_image_url (str): The URL of the player's hero image.
        is_active (bool): Whether the player is currently active.
        position (str): The position the player plays.
        shoots_catches (str): The hand the player uses to shoot or catch.
        sweater_number (int): The sweater number of the player.
        weight (int): The weight of the player in pounds.
    """

    player_id: int
    player_slug: str
    birth_city: str = ""
    birth_country: str = ""
    birth_date: datetime = datetime(1, 1, 1)
    birth_state_province: str = ""
    current_team_abbr: str = ""
    current_team_id: int = -1
    current_team_name: str = ""
    draft_overall_pick: int = -1
    draft_pick: int = -1
    draft_round: int = -1
    draft_team_abbr: str = ""
    draft_year: datetime = datetime(1, 1, 1)
    first_name: str = ""
    last_name: str = ""
    headshot_url: str = ""
    height: int = -1
    hero_image_url: str = ""
    is_active: bool = False
    position: str = ""
    shoots_catches: str = ""
    sweater_number: int = -1
    weight: int = -1

    @property
    def full_name(self):
        """
        Returns the full name of the player.
        """
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        """
        Returns a string representation of the player.
        """
        return f"{self.full_name} {self.current_team_abbr}"

    def __repr__(self):
        """
        Returns a string representation of the player for debugging.
        """
        return f"Player({self.full_name}, {self.player_id})"
