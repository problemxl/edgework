"""Draft models for NHL draft data."""

from typing import Any, Dict, List, Optional

from edgework.models.base import BaseNHLModel


class Draftee(BaseNHLModel):
    """Represents a NHL draftee (player selected in the draft)."""

    def __init__(self, edgework_client=None, obj_id=None, **kwargs):
        super().__init__(edgework_client, obj_id)
        self._data = kwargs
        if kwargs:
            self._fetched = True

    @property
    def player_id(self) -> Optional[int]:
        return self._data.get("player_id")

    @property
    def prospect_id(self) -> Optional[int]:
        return self._data.get("prospect_id")

    @property
    def first_name(self) -> str:
        return self._data.get("first_name", "")

    @property
    def last_name(self) -> str:
        return self._data.get("last_name", "")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def position(self) -> str:
        return self._data.get("position", "")

    @property
    def year(self) -> Optional[int]:
        return self._data.get("year")

    @property
    def round(self) -> Optional[int]:
        return self._data.get("round")

    @property
    def overall_pick(self) -> Optional[int]:
        return self._data.get("overall_pick")

    @property
    def pick_in_round(self) -> Optional[int]:
        return self._data.get("pick_in_round")

    @property
    def team_abbrev(self) -> str:
        return self._data.get("team_abbrev", "")

    @property
    def height(self) -> Optional[str]:
        return self._data.get("height")

    @property
    def weight(self) -> Optional[int]:
        return self._data.get("weight")

    @property
    def birth_date(self) -> Optional[str]:
        return self._data.get("birth_date")

    @property
    def birth_country(self) -> Optional[str]:
        return self._data.get("birth_country")

    def __str__(self) -> str:
        if self.overall_pick:
            return f"{self.full_name} ({self.year} - Pick #{self.overall_pick})"
        return self.full_name

    def fetch_data(self):
        if self.player_id:
            from edgework.clients.draft_client import DraftClient

            client = DraftClient(self._client)
            new_data = client.get_draftee(self.player_id)
            if new_data:
                self._data.update(new_data._data)
                self._fetched = True
        elif self.prospect_id:
            from edgework.clients.draft_client import DraftClient

            client = DraftClient(self._client)
            new_data = client.get_prospect_info(self.prospect_id)
            if new_data:
                self._data.update(new_data._data)
                self._fetched = True
        else:
            raise ValueError("No player_id or prospect_id available to fetch data")


class DraftRanking(BaseNHLModel):
    """Represents NHL draft rankings."""

    def __init__(self, edgework_client=None, obj_id=None, **kwargs):
        super().__init__(edgework_client, obj_id)
        self._data = kwargs
        if kwargs:
            self._fetched = True

    @property
    def rankings(self) -> List[Dict[str, Any]]:
        return self._data.get("rankings", [])

    def _extract_name(self, name_field) -> str:
        """Extract name from string or dict with 'default' key."""
        if isinstance(name_field, dict):
            return name_field.get("default", "")
        return name_field or ""

    def get_prospects(self) -> List[Draftee]:
        """Get ranked prospects as Draftee objects."""
        return [
            Draftee(
                edgework_client=None,
                prospect_id=p.get("id"),
                first_name=self._extract_name(p.get("firstName")),
                last_name=self._extract_name(p.get("lastName")),
                position=p.get("position", ""),
                _raw_data=p,
            )
            for p in self.rankings
        ]

    @property
    def last_updated(self) -> Optional[str]:
        return self._data.get("last_updated")

    def __len__(self) -> int:
        return len(self.rankings)

    def __iter__(self):
        return iter(self.get_prospects())

    def get_top_prospects(self, n: int = 10) -> List[Draftee]:
        """Get the top N prospects."""
        return self.get_prospects()[:n]

    def get_prospect_by_rank(self, rank: int) -> Optional[Draftee]:
        """Get a prospect by their rank (1-based)."""
        prospects = self.get_prospects()
        if 1 <= rank <= len(prospects):
            return prospects[rank - 1]
        return None

    def __str__(self) -> str:
        return f"Draft Rankings ({len(self)} prospects)"

    def fetch_data(self):
        from edgework.clients.draft_client import DraftClient

        client = DraftClient(self._client)
        new_data = client.get_draft_rankings()
        if new_data:
            self._data.update(new_data._data)
            self._fetched = True


class Draft(BaseNHLModel):
    """Represents an NHL draft."""

    def __init__(
        self,
        edgework_client=None,
        obj_id=None,
        year: Optional[int] = None,
        rounds: Optional[List[Dict]] = None,
        picks: Optional[List[Dict]] = None,
        **kwargs,
    ):
        super().__init__(edgework_client, obj_id or year)
        self._data = {
            "year": year,
            "rounds": rounds or [],
            "picks": picks or [],
            **kwargs,
        }
        if rounds or picks:
            self._fetched = True

    @property
    def year(self) -> Optional[int]:
        return self._data.get("year")

    @property
    def rounds(self) -> List[Dict[str, Any]]:
        return self._data.get("rounds", [])

    def _extract_name(self, name_field) -> str:
        """Extract name from string or dict with 'default' key."""
        if isinstance(name_field, dict):
            return name_field.get("default", "")
        return name_field or ""

    def get_picks(self) -> List[Draftee]:
        """Get all picks as Draftee objects."""
        raw_picks = self._data.get("picks", [])
        return [
            Draftee(
                edgework_client=None,
                player_id=p.get("playerId"),
                prospect_id=p.get("prospectId"),
                first_name=self._extract_name(p.get("firstName")),
                last_name=self._extract_name(p.get("lastName")),
                position=p.get("position", ""),
                year=self.year,
                round=p.get("round"),
                overall_pick=p.get("overallPick"),
                pick_in_round=p.get("pickInRound"),
                team_abbrev=p.get("teamAbbrev", ""),
                _raw_data=p,
            )
            for p in raw_picks
        ]

    @property
    def total_picks(self) -> int:
        return len(self._data.get("picks", []))

    @property
    def total_rounds(self) -> int:
        return len(self.rounds)

    def get_picks_by_round(self, round_num: int) -> List[Draftee]:
        """Get picks from a specific round."""
        return [p for p in self.get_picks() if p.round == round_num]

    def get_picks_by_team(self, team_abbrev: str) -> List[Draftee]:
        """Get picks by a specific team."""
        team_abbrev = team_abbrev.upper()
        return [p for p in self.get_picks() if p.team_abbrev.upper() == team_abbrev]

    def get_pick_by_overall(self, overall_pick: int) -> Optional[Draftee]:
        """Get a pick by overall number."""
        for pick in self.get_picks():
            if pick.overall_pick == overall_pick:
                return pick
        return None

    def __len__(self) -> int:
        return self.total_picks

    def __iter__(self):
        return iter(self.get_picks())

    def __str__(self) -> str:
        if self.year:
            return f"NHL {self.year} Draft ({self.total_picks} picks)"
        return f"NHL Draft ({self.total_picks} picks)"

    def fetch_data(self):
        from edgework.clients.draft_client import DraftClient

        client = DraftClient(self._client)
        season = f"{self.year}-{self.year + 1}" if self.year else None
        new_data = client.get_draft_picks(season=season)
        if new_data:
            self._data.update(new_data._data)
            self._fetched = True
