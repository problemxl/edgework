"""NHL Edge client for puck- and player-tracking data.

NHL Edge powers https://www.nhl.com/nhl-edge (shot speed, skating
speed/distance, zone time, shot/save locations). Its routes are served by the
Web API under ``/v1/edge/...`` and are *unofficial* — reverse-engineered from
the NHL Edge web app (see ``docs/research/nhl-edge-endpoints.md`` for the full
endpoint catalog, schemas and quirks).

Quirks every caller should know about:

- Tracking data exists only from 2024-25 onward (goalie save-location views
  from 2025-26); use :meth:`EdgeClient.get_available_seasons` for discovery
  instead of hard-coding a season list.
- ``season="now"`` replaces the whole ``{season}/{game-type}`` pair; the API
  307-redirects to the resolved current season and ``httpx`` already follows
  redirects.
- A valid route with no data returns ``[]`` (HTTP 200), never a 404 — empty
  results are legitimate and passed through as-is.
- Response schemas vary per metric view and carry no stable model, so all
  methods return raw dictionaries. Measures come in imperial/metric pairs:
  ``{"imperial": 102.4, "metric": 165.0, "overlay": {...}}``.
"""

from typing import Dict

from edgework.const import API_VERSION
from edgework.endpoints import format_endpoint
from edgework.http_client import HttpClient

# Comparison route per entity kind. These are the canonical routes owned by
# the per-entity ``get_*_comparison`` methods; :meth:`EdgeClient.compare`
# fans the same routes out across both compared entities.
_COMPARISON_ROUTES: Dict[str, str] = {
    "skater": "edge_skater_comparison",
    "goalie": "edge_goalie_comparison",
    "team": "edge_team_comparison",
}

# ``format_endpoint`` fills ``{API_VERSION}``; ``HttpClient.get(web=True)``
# prepends ``/{API_VERSION}`` itself, so the version segment is stripped.
_VERSION_PREFIX = f"/{API_VERSION}/"


def _edge_path(route_key: str, season, game_type, **entity_params) -> str:
    """Return the substituted route path for an Edge endpoint.

    Args:
        route_key: Registry key in the ``edge_`` namespace.
        season: 8-digit season (``"20252026"``) or ``"now"`` (case-
            insensitive; normalized to lowercase).
        game_type: ``2`` (regular season) or ``3`` (playoffs). Ignored by the
            API when ``season="now"``.
        **entity_params: Entity placeholder values keyed by their registry
            placeholder names (e.g. ``**{"player-id": 8478402}`` or
            ``**{"team-id": 14}``).

    Returns:
        The route path with all placeholders substituted, without the version
        segment (``"edge/skater-landing/20252026/2"``).

    ``season="now"`` collapses the ``{season}/{game-type}`` tail into a single
    ``now`` segment — the API 307-redirects ``/now`` to the resolved current
    season and ``httpx`` follows redirects.
    """
    season = "now" if str(season).lower() == "now" else season
    path = format_endpoint(
        route_key, season=season, **{"game-type": game_type}, **entity_params
    )
    if path.startswith(_VERSION_PREFIX):
        path = path[len(_VERSION_PREFIX) :]
    if season == "now":
        # "now" replaces the whole {season}/{game-type} pair: drop the
        # substituted game-type segment. rpartition matches the tail, so
        # entity ids that contain the game-type digits are unaffected.
        path = path.rpartition(f"/{game_type}")[0]
    return path


class EdgeClient:
    """Client for NHL Edge tracking endpoints (Web API, ``/v1/edge/...``).

    All methods return raw dictionaries — Edge response schemas vary per
    metric view and there is no stable model to map them onto. Empty result
    sets are legitimate and returned as-is (``[]``).
    """

    def __init__(self, http_client: HttpClient):
        """Initialize the Edge client.

        Args:
            http_client: HTTP client instance for making API requests.
        """
        self._client = http_client

    # ------------------------------------------------------------------
    # Landing pages (season leaderboards)
    # ------------------------------------------------------------------

    def get_skater_landing(self, season: str = "now", game_type: int = 2) -> Dict:
        """Fetch the Edge skater landing page (season leaderboards).

        Leader keys include ``hardestShot``, ``maxSkatingSpeed``,
        ``totalDistanceSkated``, ``distanceMaxGame``, ``highDangerSOG``,
        ``offensiveZoneTime`` and ``defensiveZoneTime``; the payload also
        carries ``seasonsWithEdgeStats`` for season discovery.

        Args:
            season: 8-digit season (``"20252026"``) or ``"now"`` (default).
                Tracking data exists from 2024-25 onward.
            game_type: ``2`` for regular season, ``3`` for playoffs.
                Ignored when ``season="now"``.

        Returns:
            Raw landing payload as a dictionary.
        """
        response = self._client.get(
            _edge_path("edge_skater_landing", season, game_type),
            web=True,
            params={},
        )
        return response.json()

    def get_goalie_landing(self, season: str = "now", game_type: int = 2) -> Dict:
        """Fetch the Edge goalie landing page (season leaderboards).

        Leader keys include ``highDangerSavePctg``, ``highDangerSaves``,
        ``highDangerGoalsAgainst``, ``savePctg5v5`` and ``gamesAbove900``
        (plus a ``minimumGamesPlayed`` qualifier).

        Args:
            season: 8-digit season (``"20252026"``) or ``"now"`` (default).
            game_type: ``2`` for regular season, ``3`` for playoffs.
                Ignored when ``season="now"``.

        Returns:
            Raw landing payload as a dictionary.
        """
        response = self._client.get(
            _edge_path("edge_goalie_landing", season, game_type),
            web=True,
            params={},
        )
        return response.json()

    def get_team_landing(self, season: str = "now", game_type: int = 2) -> Dict:
        """Fetch the Edge team landing page (season leaderboards).

        Leader keys include ``shotAttemptsOver90``, ``burstsOver22``,
        ``distancePer60``, ``highDangerSOG`` and the per-zone
        ``offensiveZoneTime`` / ``neutralZoneTime`` / ``defensiveZoneTime``.

        Args:
            season: 8-digit season (``"20252026"``) or ``"now"`` (default).
            game_type: ``2`` for regular season, ``3`` for playoffs.
                Ignored when ``season="now"``.

        Returns:
            Raw landing payload as a dictionary.
        """
        response = self._client.get(
            _edge_path("edge_team_landing", season, game_type),
            web=True,
            params={},
        )
        return response.json()

    def get_available_seasons(self) -> list:
        """Return the seasons/game types that carry Edge tracking data.

        Convenience over any landing page's ``seasonsWithEdgeStats`` field
        (``[{"id": 20242025, "gameTypes": [2, 3]}, ...]``). Tracking data
        exists only from 2024-25 on — discover it, don't hard-code it.

        Returns:
            List of ``{"id": ..., "gameTypes": [...]}`` entries; an empty
            list when the payload carries no season data.
        """
        payload = self.get_skater_landing()
        return payload.get("seasonsWithEdgeStats") or []

    # ------------------------------------------------------------------
    # Base detail (percentiles vs league average)
    # ------------------------------------------------------------------

    def get_skater_detail(
        self, player_id: int, season: str = "now", game_type: int = 2
    ) -> Dict:
        """Fetch the Edge skater detail page for one player.

        Returns the ``player`` bio plus percentile ``stats`` against the
        league average.

        Args:
            player_id: NHL player ID (e.g. ``8478402``).
            season: 8-digit season (``"20252026"``) or ``"now"`` (default).
            game_type: ``2`` for regular season, ``3`` for playoffs.
                Ignored when ``season="now"``.

        Returns:
            Raw detail payload as a dictionary.
        """
        response = self._client.get(
            _edge_path(
                "edge_skater_detail", season, game_type, **{"player-id": player_id}
            ),
            web=True,
            params={},
        )
        return response.json()

    def get_goalie_detail(
        self, player_id: int, season: str = "now", game_type: int = 2
    ) -> Dict:
        """Fetch the Edge goalie detail page for one goalie.

        Returns the ``player`` bio plus ``stats.{metric: {value, percentile,
        leagueAvg}}`` entries (GAA, ``gamesAbove900``,
        ``goalDifferentialPer60``, ``goalSupportAvg``, ...).

        Args:
            player_id: NHL goalie ID.
            season: 8-digit season (``"20252026"``) or ``"now"`` (default).
            game_type: ``2`` for regular season, ``3`` for playoffs.
                Ignored when ``season="now"``.

        Returns:
            Raw detail payload as a dictionary.
        """
        response = self._client.get(
            _edge_path(
                "edge_goalie_detail", season, game_type, **{"player-id": player_id}
            ),
            web=True,
            params={},
        )
        return response.json()

    def get_team_detail(
        self, team_id: int, season: str = "now", game_type: int = 2
    ) -> Dict:
        """Fetch the Edge team detail page for one team.

        Args:
            team_id: Numeric NHL team ID (e.g. ``14`` = Tampa Bay).
            season: 8-digit season (``"20252026"``) or ``"now"`` (default).
            game_type: ``2`` for regular season, ``3`` for playoffs.
                Ignored when ``season="now"``.

        Returns:
            Raw detail payload as a dictionary.
        """
        response = self._client.get(
            _edge_path("edge_team_detail", season, game_type, **{"team-id": team_id}),
            web=True,
            params={},
        )
        return response.json()

    # ------------------------------------------------------------------
    # Comparison payloads (one call per entity; diff client-side)
    # ------------------------------------------------------------------

    def get_skater_comparison(
        self, player_id: int, season: str = "now", game_type: int = 2
    ) -> Dict:
        """Fetch the Edge skater comparison payload for one player.

        Bundles ``shotSpeedDetails``, ``skatingSpeedDetails``, skating
        distance, zone time and shot locations for the single entity — the
        Edge UI requests both entities it compares and diffs client-side
        (see :meth:`compare` for that fan-out).

        Args:
            player_id: NHL player ID.
            season: 8-digit season (``"20252026"``) or ``"now"`` (default).
            game_type: ``2`` for regular season, ``3`` for playoffs.
                Ignored when ``season="now"``.

        Returns:
            Raw comparison payload as a dictionary.
        """
        response = self._client.get(
            _edge_path(
                "edge_skater_comparison", season, game_type, **{"player-id": player_id}
            ),
            web=True,
            params={},
        )
        return response.json()

    def get_goalie_comparison(
        self, player_id: int, season: str = "now", game_type: int = 2
    ) -> Dict:
        """Fetch the Edge goalie comparison payload for one goalie.

        Args:
            player_id: NHL goalie ID.
            season: 8-digit season (``"20252026"``) or ``"now"`` (default).
            game_type: ``2`` for regular season, ``3`` for playoffs.
                Ignored when ``season="now"``.

        Returns:
            Raw comparison payload as a dictionary.
        """
        response = self._client.get(
            _edge_path(
                "edge_goalie_comparison", season, game_type, **{"player-id": player_id}
            ),
            web=True,
            params={},
        )
        return response.json()

    def get_team_comparison(
        self, team_id: int, season: str = "now", game_type: int = 2
    ) -> Dict:
        """Fetch the Edge team comparison payload for one team.

        Args:
            team_id: Numeric NHL team ID.
            season: 8-digit season (``"20252026"``) or ``"now"`` (default).
            game_type: ``2`` for regular season, ``3`` for playoffs.
                Ignored when ``season="now"``.

        Returns:
            Raw comparison payload as a dictionary.
        """
        response = self._client.get(
            _edge_path(
                "edge_team_comparison", season, game_type, **{"team-id": team_id}
            ),
            web=True,
            params={},
        )
        return response.json()

    def compare(
        self,
        entity: str,
        id_a: int,
        id_b: int,
        season: str = "now",
        game_type: int = 2,
    ) -> Dict:
        """Fetch both sides of an Edge comparison.

        The Edge UI diffs two entities client-side; there is no combined
        server route, so this helper fans out to the per-entity comparison
        route once per ID (exactly two HTTP requests).

        Args:
            entity: ``"skater"``, ``"goalie"`` or ``"team"``.
            id_a: NHL ID of the first entity.
            id_b: NHL ID of the second entity.
            season: 8-digit season (``"20252026"``) or ``"now"`` (default).
            game_type: ``2`` for regular season, ``3`` for playoffs.
                Ignored when ``season="now"``.

        Returns:
            ``{"a": <payload for id_a>, "b": <payload for id_b>}``.

        Raises:
            ValueError: If ``entity`` is not one of the supported kinds.
        """
        kind = str(entity).lower()
        if kind not in _COMPARISON_ROUTES:
            raise ValueError(
                f"entity must be one of {sorted(_COMPARISON_ROUTES)}, got {entity!r}"
            )
        fetch = {
            "skater": self.get_skater_comparison,
            "goalie": self.get_goalie_comparison,
            "team": self.get_team_comparison,
        }[kind]
        return {
            "a": fetch(id_a, season=season, game_type=game_type),
            "b": fetch(id_b, season=season, game_type=game_type),
        }
