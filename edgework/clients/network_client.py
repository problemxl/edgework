"""Network client for fetching NHL TV and broadcast data."""

from datetime import datetime
from typing import Dict, List, Optional, Union

from edgework.http_client import HttpClient


class NetworkClient:
    """Client for fetching NHL TV and broadcast data."""

    def __init__(self, client: HttpClient):
        """
        Initialize the network client.

        Args:
            client: HTTP client instance for making API requests
        """
        self._client = client

    def get_tv_schedule(self, date: Optional[Union[datetime, str]] = None) -> Dict:
        """
        Fetch TV schedule for games.

        Args:
            date: Date for TV schedule. If None, fetches current schedule.
                  Can be datetime object or string in YYYY-MM-DD format.

        Returns:
            Dictionary with TV schedule information including:
            - Game times and broadcasts
            - National and local TV networks
            - Streaming information
        """
        if date is None:
            response = self._client.get("network/tv-schedule/now", web=True)
        else:
            if isinstance(date, datetime):
                date_str = date.strftime("%Y-%m-%d")
            else:
                date_str = date
            response = self._client.get(f"network/tv-schedule/{date_str}", web=True)
        return response.json()

    def get_tv_schedule_now(self) -> Dict:
        """
        Fetch current TV schedule.

        Returns:
            Dictionary with current TV schedule.
        """
        return self.get_tv_schedule()

    def get_tv_schedule_for_date(self, date: Union[datetime, str]) -> Dict:
        """
        Fetch TV schedule for a specific date.

        Args:
            date: Date for schedule (datetime or YYYY-MM-DD string)

        Returns:
            Dictionary with TV schedule for that date.
        """
        return self.get_tv_schedule(date)

    def get_broadcasts_for_game(self, game_id: int) -> List[Dict]:
        """
        Get broadcast information for a specific game.

        Args:
            game_id: The NHL game ID

        Returns:
            List of broadcast dictionaries including:
            - Network names
            - Broadcast types (national, local, etc.)
            - Streaming platforms
        """
        response = self._client.get(f"gamecenter/{game_id}/landing", web=True)
        data = response.json()

        # Extract broadcast information from game landing
        broadcasts = []
        tv_broadcasts = data.get("tvBroadcasts", [])

        for broadcast in tv_broadcasts:
            broadcasts.append(
                {
                    "network": broadcast.get("network", ""),
                    "country": broadcast.get("countryCode", ""),
                    "type": broadcast.get("type", ""),
                }
            )

        return broadcasts

    def get_where_to_watch(self, include: Optional[str] = None) -> Dict:
        """
        Fetch streaming options from the documented ``/where-to-watch`` route.

        Note:
            This is the real where-to-watch endpoint. It is distinct from
            ``/partner-game/{country-code}/now`` (odds), which earlier
            versions of this method incorrectly requested — use
            :meth:`get_partner_game_odds` for that data.

        Args:
            include: Optional ``include`` query filter documented for the
                route. Passed as a query parameter, never embedded in the
                route string.

        Returns:
            Dictionary with streaming options.
        """
        params = {"include": include} if include is not None else None
        response = self._client.get("where-to-watch", web=True, params=params)
        return response.json()

    def get_partner_game_odds(self, country_code: str = "US") -> Dict:
        """
        Fetch odds for games in a specific country as of the current moment.

        Targets the documented ``/partner-game/{country-code}/now`` route.
        This is an *odds* endpoint and is NOT where-to-watch streaming
        information.

        Args:
            country_code: Country code for odds (default: "US")

        Returns:
            Dictionary with partner game odds information.
        """
        response = self._client.get(f"partner-game/{country_code}/now", web=True)
        return response.json()
