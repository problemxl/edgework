from dataclasses import dataclass
from datetime import datetime


@dataclass
class Player:
    player_id: int
    player_slug: str
    birth_city: str
    birth_country: str
    birth_date: datetime
    birth_state_province: str
    current_team_abbr: str
    current_team_id: int
    current_team_name: str
    draft_overall_pick: int
    draft_pick: int
    draft_round: int
    draft_team_abbr: str
    draft_year: datetime
    first_name: str
    headshot_url: str
    height: int
    hero_image_url: str
    is_active: bool
    position: str
    shoots_catches: str
    sweater_number: int
    weight: int

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.name} ({self.score})"

    def __repr__(self):
        return str(self)
