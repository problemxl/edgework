"""Playoff client for fetching NHL playoff data."""

from typing import Dict, List, Optional

from edgework.http_client import HttpClient


class PlayoffClient:
    """Client for fetching NHL playoff data."""

    def __init__(self, client: HttpClient):
        """
        Initialize the playoff client.

        Args:
            client: HTTP client instance for making API requests
        """
        self._client = client

    def get_playoff_bracket(self, year: int) -> Dict:
        """
        Fetch the full playoff bracket for a specific year.

        Args:
            year: The year of the playoffs (e.g., 2024 for 2023-24 season)

        Returns:
            Dictionary with complete playoff bracket including:
            - All rounds and series
            - Team matchups and results
            - Series winners and progression
        """
        response = self._client.get(f"playoff-bracket/{year}", web=True)
        return response.json()

    def get_playoff_series_carousel(self, season: Optional[str] = None) -> Dict:
        """
        Fetch playoff series carousel data.

        Args:
            season: Season in format "YYYY-YYYY" (e.g., "2023-2024").
                If None, fetches current playoff series.

        Returns:
            Dictionary with playoff series carousel data including:
            - Active series information
            - Series summaries
            - Current playoff round
        """
        if season:
            try:
                start_year, end_year = season.split("-")
                season_id = f"{start_year}{end_year}"
            except (ValueError, AttributeError):
                raise ValueError(
                    f"Invalid season format: '{season}'. Expected format: 'YYYY-YYYY'"
                )
            response = self._client.get(
                f"playoff-series/carousel/{season_id}/", web=True
            )
        else:
            # Try to get current playoff series (no season specified)
            response = self._client.get("playoff-series/carousel/", web=True)
        return response.json()

    def get_playoff_series_schedule(self, season: str, series_letter: str) -> Dict:
        """
        Fetch schedule for a specific playoff series.

        Args:
            season: Season in format "YYYY-YYYY" (e.g., "2023-2024")
            series_letter: Series identifier (e.g., "A", "B", "C", etc.)

        Returns:
            Dictionary with series schedule including:
            - Game dates and times
            - Team information
            - Venue details
            - Series status
        """
        try:
            start_year, end_year = season.split("-")
            season_id = f"{start_year}{end_year}"
        except (ValueError, AttributeError):
            raise ValueError(
                f"Invalid season format: '{season}'. Expected format: 'YYYY-YYYY'"
            )

        response = self._client.get(
            f"schedule/playoff-series/{season_id}/{series_letter}/", web=True
        )
        return response.json()

    def get_current_playoff_bracket(self) -> Dict:
        """
        Fetch the current playoff bracket.

        Returns:
            Dictionary with current playoff bracket data.
            Note: Uses the most recent completed playoffs if no active playoffs.
        """
        # Default to current year - use 2024 as current playoff year
        from datetime import datetime

        current_year = datetime.now().year
        return self.get_playoff_bracket(current_year)

    def get_playoff_series_by_round(self, season: str, round_num: int) -> List[Dict]:
        """
        Get all series in a specific playoff round.

        Args:
            season: Season in format "YYYY-YYYY"
            round_num: Playoff round number (1-4)

        Returns:
            List of series dictionaries for that round
        """
        bracket = self.get_playoff_bracket(int(season.split("-")[1]))
        series_list = []

        # Navigate bracket structure based on round
        rounds_data = bracket.get("rounds", [])
        for round_data in rounds_data:
            if round_data.get("roundNumber") == round_num:
                series_list.extend(round_data.get("series", []))

        return series_list

    def get_series_winner(self, season: str, series_letter: str) -> Optional[str]:
        """
        Get the winner of a specific playoff series.

        Args:
            season: Season in format "YYYY-YYYY"
            series_letter: Series identifier

        Returns:
            Team abbreviation of the series winner, or None if series incomplete
        """
        try:
            schedule = self.get_playoff_series_schedule(season, series_letter)
            return schedule.get("seriesWinner", {}).get("abbrev")
        except Exception:
            return None
