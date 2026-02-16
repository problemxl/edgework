"""Standings client for fetching NHL standings data."""

from datetime import datetime
from typing import Union

import edgework.utilities as utilities
from edgework.http_client import HttpClient
from edgework.models.standings import Seeding, Standings


class StandingClient:
    """Client for fetching NHL standings data."""

    def __init__(self, client: HttpClient):
        """Initialize the standings client.

        Args:
            client: HTTP client instance for making API requests.
        """
        self._client = client

    def _validate_date(self, date: Union[datetime, str, None]) -> str:
        """Validate and normalize date input to string format.

        Args:
            date: Date input as datetime object, string (YYYY-MM-DD), or None.

        Returns:
            Normalized date string in YYYY-MM-DD format or "now".

        Raises:
            ValueError: If date format is invalid.
        """
        if date is None:
            return "now"

        if isinstance(date, datetime):
            return date.strftime("%Y-%m-%d")

        if isinstance(date, str):
            if date == "now":
                return date

            if len(date) != 10:
                raise ValueError(
                    f"Date must be in the format YYYY-MM-DD, or 'now'. "
                    f"Provided date: '{date}' is not 10 characters long."
                )

            if date[4] != "-" or date[7] != "-":
                raise ValueError(
                    f"Date must be in the format YYYY-MM-DD, or 'now'. "
                    f"Provided date: '{date}' does not have '-' in the correct positions."
                )

            if (
                not date[:4].isdigit()
                or not date[5:7].isdigit()
                or not date[8:].isdigit()
            ):
                raise ValueError(
                    f"Date must be in the format YYYY-MM-DD, or 'now'. "
                    f"Provided date: '{date}' contains non-numeric characters."
                )

            return date

        raise ValueError(
            f"Date must be in the format YYYY-MM-DD, 'now', or a datetime object. "
            f"Provided date: '{date}' is not a valid type."
        )

    def get_standings(self, date: Union[datetime, str, None] = "now") -> Standings:
        """Fetch NHL standings for a specific date or current standings.

        Args:
            date: Date to fetch standings for. Can be:
                - "now" (default): Current standings
                - datetime object: Converted to YYYY-MM-DD format
                - string: Must be in YYYY-MM-DD format
                - None: Defaults to "now"

        Returns:
            Standings object containing league standings data.

        Raises:
            ValueError: If date format is invalid.
        """
        date_str = self._validate_date(date)

        response = self._client.get(f"standings/{date_str}", web=True, params={})
        raw_standings = response.json().get("standings", [])
        seedings_dict = [utilities.dict_camel_to_snake(seed) for seed in raw_standings]

        if date_str == "now":
            dt_date = datetime.now()
        else:
            dt_date = datetime.strptime(date_str, "%Y-%m-%d")

        seedings = []
        for seed_data in seedings_dict:
            seedings.append(Seeding(**seed_data))

        return Standings(date=dt_date, seedings=seedings)

    def get_standings_for_season(self, season: str) -> Standings:
        """Fetch NHL standings for a specific season.

        Args:
            season: Season in format "YYYY-YYYY" (e.g., "2023-2024").

        Returns:
            Standings object containing season standings data.
        """
        try:
            start_year, end_year = season.split("-")
            season_id = int(f"{start_year}{end_year}")
        except (ValueError, AttributeError):
            raise ValueError(
                f"Invalid season format: '{season}'. Expected format: 'YYYY-YYYY'"
            )

        response = self._client.get(
            "standings-season",
            web=True,
            params={"seasonId": season_id},
        )

        data = response.json()
        raw_standings = data.get("data", [])
        seedings_dict = [utilities.dict_camel_to_snake(seed) for seed in raw_standings]

        seedings = []
        for seed_data in seedings_dict:
            seedings.append(Seeding(**seed_data))

        return Standings(
            date=datetime.now(),
            seedings=seedings,
            season=season_id,
        )
