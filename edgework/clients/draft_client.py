"""Draft client for fetching NHL draft data."""

from typing import Dict, List, Optional

from edgework.http_client import HttpClient
from edgework.models.draft import Draft, Draftee, DraftRanking


class DraftClient:
    """Client for fetching NHL draft data."""

    def __init__(self, client: HttpClient):
        """Initialize the draft client.

        Args:
            client: HTTP client instance for making API requests.
        """
        self._client = client

    def get_draft_picks(
        self, season: Optional[str] = None, round_num: Optional[str] = "all"
    ) -> Draft:
        """Fetch draft picks for a specific season or current draft.

        Args:
            season: Season in format "YYYY-YYYY" (e.g., "2023-2024").
                If None, fetches current draft.
            round_num: Round number to fetch (default: "all" for all rounds).

        Returns:
            Draft object containing draft picks data.
        """
        if season:
            try:
                start_year, end_year = season.split("-")
                season_id = f"{start_year}{end_year}"
            except (ValueError, AttributeError):
                raise ValueError(
                    f"Invalid season format: '{season}'. Expected format: 'YYYY-YYYY'"
                )
            path = f"draft/picks/{season_id}/{round_num}"
        else:
            path = "draft/picks/now"

        response = self._client.get(path, web=True, params={})
        data = response.json()

        return Draft(
            edgework_client=self._client,
            year=data.get("draftYear"),
            rounds=data.get("rounds", []),
            picks=data.get("picks", []),
            _raw_data=data,
        )

    def get_draft_rankings(
        self, season: Optional[str] = None, prospect_category: str = "all"
    ) -> DraftRanking:
        """Fetch draft rankings for a specific season or current rankings.

        Args:
            season: Season in format "YYYY-YYYY" (e.g., "2023-2024").
                If None, fetches current rankings.
            prospect_category: Category of prospects to fetch (default: "all").

        Returns:
            DraftRanking object containing draft rankings data.
        """
        if season:
            try:
                start_year, end_year = season.split("-")
                season_id = f"{start_year}{end_year}"
            except (ValueError, AttributeError):
                raise ValueError(
                    f"Invalid season format: '{season}'. Expected format: 'YYYY-YYYY'"
                )
            path = f"draft/rankings/{season_id}/{prospect_category}"
        else:
            path = "draft/rankings/now"

        response = self._client.get(path, web=True, params={})
        data = response.json()

        return DraftRanking(
            edgework_client=self._client,
            rankings=data.get("rankings", []),
            _raw_data=data,
        )

    def get_draft_tracker_picks(self) -> List[Dict]:
        """Fetch current draft tracker picks.

        Returns:
            List of draft picks from the tracker.
        """
        response = self._client.get("draft-tracker/picks/now", web=True, params={})
        data = response.json()
        return data.get("picks", [])

    def get_draftee(self, player_id: int) -> Optional[Draftee]:
        """Fetch draft information for a specific player.

        Args:
            player_id: The NHL player ID.

        Returns:
            Draftee object if found, None otherwise.
        """
        try:
            response = self._client.get(
                f"player/{player_id}/landing", web=True, params={}
            )
            data = response.json()

            draft_details = data.get("draftDetails")
            if draft_details:
                return Draftee(
                    edgework_client=self._client,
                    player_id=player_id,
                    first_name=data.get("firstName", {}).get("default", ""),
                    last_name=data.get("lastName", {}).get("default", ""),
                    year=draft_details.get("year"),
                    round=draft_details.get("round"),
                    overall_pick=draft_details.get("overallPick"),
                    pick_in_round=draft_details.get("pickInRound"),
                    team_abbrev=draft_details.get("teamAbbrev"),
                    _raw_data=draft_details,
                )
        except Exception:
            pass

        return None

    def get_prospect_info(self, prospect_id: int) -> Optional[Draftee]:
        """Fetch prospect information by prospect ID.

        Args:
            prospect_id: The NHL prospect ID.

        Returns:
            Draftee object if found, None otherwise.
        """
        response = self._client.get(f"prospects/{prospect_id}", web=True, params={})
        data = response.json()

        if data:
            return Draftee(
                edgework_client=self._client,
                prospect_id=prospect_id,
                first_name=data.get("firstName", {}).get("default", ""),
                last_name=data.get("lastName", {}).get("default", ""),
                position=data.get("position", ""),
                height=data.get("height"),
                weight=data.get("weight"),
                birth_date=data.get("birthDate"),
                birth_country=data.get("birthCountry"),
                _raw_data=data,
            )

        return None
