"""Shift charts client for the NHL Stats API.

``ShiftClient`` is the canonical wrapper for the documented Stats API
shiftcharts route (``/{lang}/shiftcharts?cayenneExp=gameId={game_id}``).
``GameClient`` and the ``Game`` model delegate here (or reuse
:func:`build_shiftcharts_query`) so the route and query construction live in
a single place.
"""

from typing import Any, Dict, List, Optional

from edgework.http_client import HttpClient
from edgework.models.shift import Shift

# Route target on the Stats API (language prefix and base URL are added by
# ``HttpClient``); the registry template lives at ``API_PATH["stats_shiftcharts"]``.
SHIFTCHARTS_ROUTE = "shiftcharts"


def build_shiftcharts_query(
    game_id: Optional[int] = None, cayenne_exp: Optional[str] = None
) -> Dict[str, str]:
    """Build the query parameters for a shiftcharts request.

    The documented shiftcharts route filters through a ``cayenneExp`` query
    parameter; the documented usage is ``cayenneExp=gameId={game_id}``. The
    expression is returned in ``params`` (never embedded in the route string)
    so it is encoded correctly.

    Args:
        game_id: NHL game ID (the documented filter).
        cayenne_exp: Raw Cayenne filter expression (escape hatch for filters
            beyond the documented game-ID filter). Ignored when ``game_id``
            is given.

    Returns:
        Query parameter dict for ``HttpClient.get(..., params=...)``.

    Raises:
        ValueError: If neither ``game_id`` nor ``cayenne_exp`` is provided.
    """
    if game_id is not None:
        return {"cayenneExp": f"gameId={game_id}"}
    if cayenne_exp:
        return {"cayenneExp": cayenne_exp}
    raise ValueError(
        "shiftcharts requires a filter: pass game_id or a raw cayenne_exp expression"
    )


class ShiftClient:
    """Canonical client for the Stats API ``/{lang}/shiftcharts`` route."""

    def __init__(self, client: HttpClient):
        """
        Initialize the shift client.

        Args:
            client: HTTP client instance for making API requests.
        """
        self._client = client

    def get_shiftcharts(
        self,
        game_id: Optional[int] = None,
        cayenne_exp: Optional[str] = None,
        lang: str = "en",
    ) -> List[Dict[str, Any]]:
        """Fetch raw shift chart rows for a Cayenne filter expression.

        Args:
            game_id: NHL game ID (the documented filter).
            cayenne_exp: Raw Cayenne filter expression (escape hatch).
            lang: Language code for the Stats API request (default "en").

        Returns:
            List of raw shift chart dictionaries from the API response.
        """
        params = build_shiftcharts_query(game_id=game_id, cayenne_exp=cayenne_exp)
        response = self._client.get(SHIFTCHARTS_ROUTE, params=params, lang=lang)
        return response.json()["data"]

    def get_shifts(self, game_id: int, lang: str = "en") -> List[Shift]:
        """Fetch shift data for a game as Shift objects.

        Args:
            game_id: The NHL game ID.
            lang: Language code for the Stats API request (default "en").

        Returns:
            List of Shift objects.
        """
        data = self.get_shiftcharts(game_id=game_id, lang=lang)
        return [Shift.from_api(d) for d in data]
