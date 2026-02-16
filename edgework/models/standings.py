from datetime import datetime
from typing import Dict, List, Optional

from edgework.models.base import BaseNHLModel


class Seeding(BaseNHLModel):
    """
    Represents a team's standing/seeding in the NHL.

    This model stores comprehensive team statistics including conference and
    division standings, home/road splits, and streak information.
    """

    def __init__(self, edgework_client=None, obj_id=None, **kwargs):
        """
        Initialize a Seeding object.

        Args:
            edgework_client: The Edgework client instance
            obj_id: The ID of the seeding record
            **kwargs: Team standing data from API
        """
        super().__init__(edgework_client, obj_id)
        self._data = kwargs
        if kwargs:
            self._fetched = True

    @property
    def conference_abbrev(self) -> str:
        return self._data.get("conference_abbrev", "")

    @property
    def conference_name(self) -> str:
        return self._data.get("conference_name", "")

    @property
    def division_abbrev(self) -> str:
        return self._data.get("division_abbrev", "")

    @property
    def division_name(self) -> str:
        return self._data.get("division_name", "")

    @property
    def team_name(self) -> Dict[str, str]:
        return self._data.get("team_name", {})

    @property
    def team_common_name(self) -> Dict[str, str]:
        return self._data.get("team_common_name", {})

    @property
    def team_abbrev(self) -> str:
        abbrev = self._data.get("team_abbrev", "")
        return abbrev.get("default", "") if isinstance(abbrev, dict) else str(abbrev)

    @property
    def team_logo(self) -> str:
        return self._data.get("team_logo", "")

    @property
    def games_played(self) -> int:
        return self._data.get("games_played", 0)

    @property
    def wins(self) -> int:
        return self._data.get("wins", 0)

    @property
    def losses(self) -> int:
        return self._data.get("losses", 0)

    @property
    def ot_losses(self) -> int:
        return self._data.get("ot_losses", 0)

    @property
    def points(self) -> int:
        return self._data.get("points", 0)

    @property
    def point_pctg(self) -> float:
        return self._data.get("point_pctg", 0.0)

    @property
    def goals_for(self) -> int:
        return self._data.get("goal_for", 0)

    @property
    def goals_against(self) -> int:
        return self._data.get("goal_against", 0)

    @property
    def goal_differential(self) -> int:
        return self._data.get("goal_differential", 0)

    @property
    def win_pctg(self) -> float:
        return self._data.get("win_pctg", 0.0)

    @property
    def streak_code(self) -> str:
        return self._data.get("streak_code", "")

    @property
    def streak_count(self) -> int:
        return self._data.get("streak_count", 0)

    @property
    def clinch_indicator(self) -> str:
        return self._data.get("clinch_indicator", "")

    @property
    def wildcard_sequence(self) -> int:
        return self._data.get("wildcard_sequence", 0)

    @property
    def conference_sequence(self) -> int:
        return self._data.get("conference_sequence", 0)

    @property
    def division_sequence(self) -> int:
        return self._data.get("division_sequence", 0)

    @property
    def is_clinched(self) -> bool:
        return bool(self.clinch_indicator)

    @property
    def is_in_playoffs(self) -> bool:
        return self.conference_sequence <= 8 if self.conference_sequence else False

    def __str__(self) -> str:
        return f"{self.team_abbrev}: {self.points} pts ({self.wins}-{self.losses}-{self.ot_losses})"

    def fetch_data(self):
        raise NotImplementedError(
            "Seeding data is fetched via Standings. Use StandingClient.get_standings() instead."
        )


class Standings(BaseNHLModel):
    """
    Represents NHL standings for a specific date or season.

    Provides access to team standings organized by conference and division,
    with filtering methods for different views.
    """

    def __init__(
        self,
        edgework_client=None,
        obj_id=None,
        date: Optional[datetime] = None,
        seedings: Optional[List[Seeding]] = None,
        season: Optional[int] = None,
    ):
        """
        Initialize a Standings object.

        Args:
            edgework_client: The Edgework client instance
            obj_id: The ID of the standings (not typically used)
            date: The date these standings represent
            seedings: List of Seeding objects for all teams
            season: The season ID (e.g., 20232024)
        """
        super().__init__(edgework_client, obj_id)
        self._data = {
            "date": date,
            "seedings": seedings or [],
            "season": season,
        }
        self._fetched = True

    @property
    def date(self) -> Optional[datetime]:
        return self._data.get("date")

    @property
    def season(self) -> Optional[int]:
        return self._data.get("season")

    @property
    def seedings(self) -> List[Seeding]:
        return self._data.get("seedings", [])

    @property
    def east_standings(self) -> List[Seeding]:
        return [s for s in self.seedings if s.conference_abbrev == "E"]

    @property
    def west_standings(self) -> List[Seeding]:
        return [s for s in self.seedings if s.conference_abbrev == "W"]

    def get_division_standings(self, division: str) -> List[Seeding]:
        """
        Get standings for a specific division.

        Args:
            division: Division abbreviation (e.g., 'ATL', 'MET', 'CEN', 'PAC')

        Returns:
            List of Seeding objects for the division, sorted by points
        """
        division = division.upper()
        return [s for s in self.seedings if s.division_abbrev.upper() == division]

    def get_team_standing(self, team_abbrev: str) -> Optional[Seeding]:
        """
        Get the standing for a specific team.

        Args:
            team_abbrev: Team abbreviation (e.g., 'TOR', 'NYR')

        Returns:
            Seeding object for the team, or None if not found
        """
        team_abbrev = team_abbrev.upper()
        for seeding in self.seedings:
            if seeding.team_abbrev.upper() == team_abbrev:
                return seeding
        return None

    def get_playoff_teams(self) -> List[Seeding]:
        """
        Get all teams currently in playoff positions.

        Returns:
            List of Seeding objects for teams in playoff positions
        """
        playoff_teams = []
        for conference in ["E", "W"]:
            conf_standings = [
                s for s in self.seedings if s.conference_abbrev == conference
            ]
            sorted_standings = sorted(
                conf_standings,
                key=lambda s: s._data.get("conference_sequence", 999) or 999,
            )
            playoff_teams.extend(sorted_standings[:8])
        return playoff_teams

    def get_wildcard_race(self, conference: str) -> List[Seeding]:
        """
        Get the wildcard race for a specific conference.

        Args:
            conference: Conference abbreviation ('E' or 'W')

        Returns:
            List of Seeding objects for teams in the wildcard race
        """
        conference = conference.upper()
        conf_standings = [s for s in self.seedings if s.conference_abbrev == conference]
        sorted_standings = sorted(
            conf_standings,
            key=lambda s: s.wildcard_sequence if s.wildcard_sequence else 999,
        )
        return [s for s in sorted_standings if 7 <= (s.wildcard_sequence or 0) <= 10]

    def __len__(self) -> int:
        return len(self.seedings)

    def __iter__(self):
        return iter(self.seedings)

    def __str__(self) -> str:
        date_str = self.date.strftime("%Y-%m-%d") if self.date else "now"
        return f"NHL Standings ({date_str}) - {len(self)} teams"

    def fetch_data(self):
        raise NotImplementedError(
            "Standings data is fetched via StandingClient. "
            "Use StandingClient.get_standings() to fetch fresh data."
        )
