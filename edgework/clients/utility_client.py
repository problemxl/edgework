"""Utility client for fetching NHL metadata and miscellaneous data."""

from typing import Dict, Optional

from edgework.http_client import HttpClient


class UtilityClient:
    """Client for fetching NHL metadata and utility data."""

    def __init__(self, client: HttpClient):
        """
        Initialize the utility client.

        Args:
            client: HTTP client instance for making API requests
        """
        self._client = client

    def get_season(self) -> Dict:
        """
        Fetch current season metadata.

        Returns:
            Dictionary with season information including:
            - Current season ID
            - Season start/end dates
            - Current game type
            - Schedule information
        """
        response = self._client.get("season", web=True)
        return response.json()

    def get_meta(self) -> Dict:
        """
        Fetch API metadata.

        Returns:
            Dictionary with API metadata including:
            - Available endpoints
            - API version information
            - Supported features
        """
        response = self._client.get("meta", web=True)
        return response.json()

    def get_meta_game(self, game_id: int) -> Dict:
        """
        Fetch metadata for a specific game.

        Args:
            game_id: The NHL game ID

        Returns:
            Dictionary with game metadata.
        """
        response = self._client.get(f"meta/game/{game_id}", web=True)
        return response.json()

    def get_meta_playoff_series(self, year: int, series_letter: str) -> Dict:
        """
        Fetch metadata for a playoff series.

        Args:
            year: The playoff year
            series_letter: Series identifier (e.g., "A", "B")

        Returns:
            Dictionary with playoff series metadata.
        """
        response = self._client.get(
            f"meta/playoff-series/{year}/{series_letter}", web=True
        )
        return response.json()

    def get_location(self) -> Dict:
        """
        Fetch location data.

        Returns:
            Dictionary with location information.
        """
        response = self._client.get("location", web=True)
        return response.json()

    def get_postal_lookup(self, postal_code: str) -> Dict:
        """
        Fetch location data for a postal code.

        Args:
            postal_code: Postal/ZIP code to look up

        Returns:
            Dictionary with location data for the postal code.
        """
        response = self._client.get(f"postal-lookup/{postal_code}", web=True)
        return response.json()
