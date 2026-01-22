from edgework.http_client import HttpClient
from edgework.models.draft import DraftPick, DraftRanking


class DraftClient:
    def __init__(self, client: HttpClient):
        self._client = client

    def get_picks_now(self) -> list[DraftPick]:
        """Get the current draft picks.

        Returns
        -------
        list[DraftPick]
            A list of DraftPick objects representing current draft picks.

        """
        response = self._client.get("draft/picks/now")
        data = response.json()
        year = data.get("year")
        picks = [DraftPick.from_api(pick, year) for pick in data.get("picks", [])]
        return picks

    def get_picks(self, year: int) -> list[DraftPick]:
        """Get the draft picks for a given year.

        Parameters
        ----------
        year : int
            The draft year.

        Returns
        -------
        list[DraftPick]
            A list of DraftPick objects for the specified year.

        """
        response = self._client.get(f"draft/picks/{year}")
        data = response.json()
        picks = [DraftPick.from_api(pick, year) for pick in data.get("picks", [])]
        return picks

    def get_rankings_now(self) -> list[DraftRanking]:
        """Get the current draft rankings.

        Returns
        -------
        list[DraftRanking]
            A list of DraftRanking objects representing current draft rankings.

        """
        response = self._client.get("draft/prospects/now")
        data = response.json()
        rankings = [self._parse_ranking(r) for r in data.get("prospects", [])]
        return rankings

    def get_rankings(self, year: int) -> list[DraftRanking]:
        """Get the draft rankings for a given year.

        Parameters
        ----------
        year : int
            The draft year.

        Returns
        -------
        list[DraftRanking]
            A list of DraftRanking objects for the specified year.

        """
        response = self._client.get(f"draft/prospects/{year}")
        data = response.json()
        rankings = [self._parse_ranking(r) for r in data.get("prospects", [])]
        return rankings

    def _parse_ranking(self, data: dict) -> DraftRanking:
        """Helper method to parse draft ranking data.

        Parameters
        ----------
        data : dict
            Raw API response data for a draft ranking.

        Returns
        -------
        DraftRanking
            A DraftRanking object.

        """
        first_name = data.get("firstName", {})
        last_name = data.get("lastName", {})

        return DraftRanking(
            rank=data.get("rank", 0),
            player_id=data.get("playerId", 0),
            first_name=first_name.get("default", ""),
            last_name=last_name.get("default", ""),
            position=data.get("positionCode", ""),
            height_in_inches=data.get("heightInInches"),
            weight_in_pounds=data.get("weightInPounds"),
            team=data.get("teamName"),
        )
