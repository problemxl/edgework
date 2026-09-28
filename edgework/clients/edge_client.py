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
- The Goal Visualizer (per-goal tracking replays) chains the ``ppt-replay``
  metadata route to a ``pptReplayUrl`` on the sprites host, which 403s unless
  the request carries ``Referer: https://www.nhl.com/``. Preseason/no-coverage
  goals have no ``pptReplayUrl`` — :meth:`EdgeClient.get_goal_frames` returns
  ``None`` instead of raising.
"""

from typing import Any, Dict, FrozenSet, List, Optional, Tuple

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

# ---------------------------------------------------------------------------
# Validated path parameters for the top-10 leaderboards. Values were probed
# against the live API (see ``docs/research/nhl-edge-endpoints.md``); some
# combos are valid routes that legitimately return ``[]`` while others are
# enumerated here from the Edge web app's own option lists. Values are
# matched case-insensitively and normalized to lowercase.
# ---------------------------------------------------------------------------

#: ``{situation}`` segment across top-10 routes: all, even strength,
#: power play, penalty kill. Many top-10s only return data for ``all``.
SITUATION: FrozenSet[str] = frozenset({"all", "es", "pp", "pk"})

#: ``{sort}`` segment of the shot/skating-speed top-10 routes. Only ``max``
#: was observed returning data; ``avg`` is a valid empty route.
SORT: FrozenSet[str] = frozenset({"max", "avg"})

#: ``{metric}`` segment of the skater/team shot-location top-10 routes.
SHOT_METRIC: FrozenSet[str] = frozenset({"sog", "goals"})

#: ``{zone}`` segment of the team zone-time top-10 route.
ZONE: FrozenSet[str] = frozenset({"offensive", "defensive", "neutral"})

#: ``{metric}`` segment of the goalie shot-location top-10 route (the route
#: with the metric-first param order).
GOALIE_METRIC: FrozenSet[str] = frozenset({"save-pctg", "saves", "goals-against"})

#: ``{filter}`` segment of the shot-location top-10 routes — only ``all`` has
#: been observed returning data so far; widen when the API grows this enum.
SHOT_LOCATION_FILTER: FrozenSet[str] = frozenset({"all"})

#: ``{param}`` (middle) segment of the team skating-distance top-10 route —
#: only ``all`` has been observed returning data so far.
DISTANCE_PARAM: FrozenSet[str] = frozenset({"all"})

#: ``{sort}`` segment of the team skating-distance top-10 route. Unlike the
#: speed routes, only ``total`` was observed returning data.
DISTANCE_SORT: FrozenSet[str] = frozenset({"total"})


def _resolve_keyword_alias(value, kwargs: dict[str, Any], alias: str, default):
    """Resolve a legacy keyword alias without shadowing a built-in name."""
    if alias in kwargs:
        if value != default:
            raise TypeError(f"Got multiple values for argument {alias!r}")
        value = kwargs.pop(alias)
    if kwargs:
        unexpected = next(iter(kwargs))
        raise TypeError(f"Unexpected keyword argument {unexpected!r}")
    return value


def _validate_choice(name: str, value, allowed: FrozenSet[str]) -> str:
    """Validate a path parameter against its allowed values.

    Args:
        name: Parameter name used in the error message (e.g. ``"situation"``).
        value: Raw parameter value; normalized to lowercase before matching.
        allowed: The set of accepted lowercase values.

    Returns:
        The normalized (lowercase) value.

    Raises:
        ValueError: If the normalized value is not in ``allowed``.
    """
    normalized = str(value).lower()
    if normalized not in allowed:
        raise ValueError(f"{name} must be one of {sorted(allowed)}, got {value!r}")
    return normalized


# ---------------------------------------------------------------------------
# Goal Visualizer (Puck & Player Tracking replay frames)
# ---------------------------------------------------------------------------

#: Entity key of the puck inside a frame's ``onIce`` mapping — every other
#: key is a skater or goalie (``{teamId digit}{sweaterNumber}``).
PUCK_ENTITY_KEY = "1"

#: The sprites host (wsr.nhle.com) rejects requests without this Referer
#: (user agent alone — or Origin alone — is answered with 403 by the CDN).
SPRITES_REFERER = "https://www.nhl.com/"


def _ppt_replay_path(game_id, event_id) -> str:
    """Return the registry-driven path for ``/v1/ppt-replay/{game}/{event}``.

    The ``play_replay`` route is owned by ``GameClient.get_play_replay``;
    this helper reuses its registry entry (no duplicated route string) and
    strips the version segment exactly like :func:`_edge_path`.
    """
    path = format_endpoint("play_replay", game_id=game_id, event_number=event_id)
    if path.startswith(_VERSION_PREFIX):
        path = path[len(_VERSION_PREFIX) :]
    return path


def puck_frames(frames: List[Dict]) -> List[Tuple]:
    """Extract the puck track from raw Goal Visualizer frames.

    Args:
        frames: Raw frame list as served by the sprites host — one dict per
            frame with ``timeStamp`` and an ``onIce`` entity mapping.

    Returns:
        ``(timestamp, x, y)`` tuples for the puck (entity key ``"1"``), one
        per frame, in frame order. Frames missing the puck entity are skipped.

    Units (see ``docs/research/nhl-edge-endpoints.md``):
        - Coordinates are **inches** on a 2400×1020 rink grid (200 ft × 85 ft;
          divide by 12 for feet).
        - ``timestamp`` is a decisecond frame counter at 10 fps — a typical
          goal carries ~140 frames ≈ 14 s of play leading to the score.
    """
    track = []
    for frame in frames:
        puck = (frame.get("onIce") or {}).get(PUCK_ENTITY_KEY)
        if puck is not None:
            track.append((frame.get("timeStamp"), puck.get("x"), puck.get("y")))
    return track


def player_frames(
    frames: List[Dict], player_id: Optional[int] = None
) -> Dict[int, List[Tuple]]:
    """Extract per-player tracks from raw Goal Visualizer frames.

    Players are matched on their NHL ``playerId`` field (not the ``onIce``
    mapping key, which is a derived ``{teamId digit}{sweaterNumber}``). The
    puck is excluded — it has no ``playerId``.

    Args:
        frames: Raw frame list as served by the sprites host.
        player_id: Optional NHL player ID. When given, only that player's
            track is returned (``[]`` if they never appear on ice).

    Returns:
        Without ``player_id``: a mapping ``{playerId: [(timestamp, x, y),
        ...]}`` with one list per player, in first-appearance order. With
        ``player_id``: just that player's ``(timestamp, x, y)`` list.

    Units: same as :func:`puck_frames` — coordinates in inches (rink
    2400×1020), timestamps as decisecond counters at 10 fps.
    """
    tracks: Dict[int, List[Tuple]] = {}
    for frame in frames:
        for entity in (frame.get("onIce") or {}).values():
            pid = entity.get("playerId")
            if not pid:
                continue  # the puck (or an unnamed entity) — not a player
            pid = int(pid)
            if player_id is not None and pid != int(player_id):
                continue
            tracks.setdefault(pid, []).append(
                (frame.get("timeStamp"), entity.get("x"), entity.get("y"))
            )
    if player_id is not None:
        return tracks.get(int(player_id), [])
    return tracks

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

    # ------------------------------------------------------------------
    # View-specific detail (per-metric breakdowns)
    # ------------------------------------------------------------------

    def get_skater_shot_speed_detail(
        self, player_id: int, season: str = "now", game_type: int = 2
    ) -> Dict:
        """Fetch a skater's shot-speed breakdown (``skater-shot-speed-detail``).

        Returns ``topShotSpeed``/``avgShotSpeed`` plus the attempts buckets
        (100+ / 90-100 / 80-90 / 70-80 mph).

        Args:
            player_id: NHL player ID.
            season: 8-digit season (``"20252026"``) or ``"now"`` (default).
            game_type: ``2`` for regular season, ``3`` for playoffs.
                Ignored when ``season="now"``.

        Returns:
            Raw detail payload as a dictionary (``[]`` when no data).
        """
        response = self._client.get(
            _edge_path(
                "edge_skater_shot_speed_detail",
                season,
                game_type,
                **{"player-id": player_id},
            ),
            web=True,
            params={},
        )
        return response.json()

    def get_skater_skating_speed_detail(
        self, player_id: int, season: str = "now", game_type: int = 2
    ) -> Dict:
        """Fetch a skater's skating-speed breakdown (``skater-skating-speed-detail``).

        Returns ``maxSkatingSpeed`` plus the bursts-over-threshold counts
        (22 / 20 / 18 mph).

        Args:
            player_id: NHL player ID.
            season: 8-digit season (``"20252026"``) or ``"now"`` (default).
            game_type: ``2`` for regular season, ``3`` for playoffs.
                Ignored when ``season="now"``.

        Returns:
            Raw detail payload as a dictionary (``[]`` when no data).
        """
        response = self._client.get(
            _edge_path(
                "edge_skater_skating_speed_detail",
                season,
                game_type,
                **{"player-id": player_id},
            ),
            web=True,
            params={},
        )
        return response.json()

    def get_skater_skating_distance_detail(
        self, player_id: int, season: str = "now", game_type: int = 2
    ) -> Dict:
        """Fetch a skater's skating-distance breakdown.

        Returns distance skated per game and per situation.

        Args:
            player_id: NHL player ID.
            season: 8-digit season (``"20252026"``) or ``"now"`` (default).
            game_type: ``2`` for regular season, ``3`` for playoffs.
                Ignored when ``season="now"``.

        Returns:
            Raw detail payload as a dictionary (``[]`` when no data).
        """
        response = self._client.get(
            _edge_path(
                "edge_skater_skating_distance_detail",
                season,
                game_type,
                **{"player-id": player_id},
            ),
            web=True,
            params={},
        )
        return response.json()

    def get_skater_shot_location_detail(
        self, player_id: int, season: str = "now", game_type: int = 2
    ) -> Dict:
        """Fetch a skater's shot-location breakdown.

        Returns ``shotLocationDetails[]`` (per rink area: sog, goals, pctg,
        percentile) and ``shotLocationTotals[]`` with league averages.

        Args:
            player_id: NHL player ID.
            season: 8-digit season (``"20252026"``) or ``"now"`` (default).
            game_type: ``2`` for regular season, ``3`` for playoffs.
                Ignored when ``season="now"``.

        Returns:
            Raw detail payload as a dictionary (``[]`` when no data).
        """
        response = self._client.get(
            _edge_path(
                "edge_skater_shot_location_detail",
                season,
                game_type,
                **{"player-id": player_id},
            ),
            web=True,
            params={},
        )
        return response.json()

    def get_goalie_shot_location_detail(
        self, player_id: int, season: str = "now", game_type: int = 2
    ) -> Dict:
        """Fetch a goalie's save-location breakdown.

        Returns save percentage by danger zone (all / highDanger / midRange /
        longRange). Data for the goalie shot-location family starts in
        2025-26 (later than the other Edge views).

        Args:
            player_id: NHL goalie ID.
            season: 8-digit season (``"20252026"``) or ``"now"`` (default).
            game_type: ``2`` for regular season, ``3`` for playoffs.
                Ignored when ``season="now"``.

        Returns:
            Raw detail payload as a dictionary (``[]`` when no data).
        """
        response = self._client.get(
            _edge_path(
                "edge_goalie_shot_location_detail",
                season,
                game_type,
                **{"player-id": player_id},
            ),
            web=True,
            params={},
        )
        return response.json()

    def get_team_shot_speed_detail(
        self, team_id: int, season: str = "now", game_type: int = 2
    ) -> Dict:
        """Fetch a team's shot-speed breakdown.

        Args:
            team_id: Numeric NHL team ID (e.g. ``14`` = Tampa Bay).
            season: 8-digit season (``"20252026"``) or ``"now"`` (default).
            game_type: ``2`` for regular season, ``3`` for playoffs.
                Ignored when ``season="now"``.

        Returns:
            Raw detail payload as a dictionary (``[]`` when no data).
        """
        response = self._client.get(
            _edge_path(
                "edge_team_shot_speed_detail",
                season,
                game_type,
                **{"team-id": team_id},
            ),
            web=True,
            params={},
        )
        return response.json()

    def get_team_skating_speed_detail(
        self, team_id: int, season: str = "now", game_type: int = 2
    ) -> Dict:
        """Fetch a team's skating-speed breakdown.

        Args:
            team_id: Numeric NHL team ID.
            season: 8-digit season (``"20252026"``) or ``"now"`` (default).
            game_type: ``2`` for regular season, ``3`` for playoffs.
                Ignored when ``season="now"``.

        Returns:
            Raw detail payload as a dictionary (``[]`` when no data).
        """
        response = self._client.get(
            _edge_path(
                "edge_team_skating_speed_detail",
                season,
                game_type,
                **{"team-id": team_id},
            ),
            web=True,
            params={},
        )
        return response.json()

    def get_team_skating_distance_detail(
        self, team_id: int, season: str = "now", game_type: int = 2
    ) -> Dict:
        """Fetch a team's skating-distance breakdown.

        Args:
            team_id: Numeric NHL team ID.
            season: 8-digit season (``"20252026"``) or ``"now"`` (default).
            game_type: ``2`` for regular season, ``3`` for playoffs.
                Ignored when ``season="now"``.

        Returns:
            Raw detail payload as a dictionary (``[]`` when no data).
        """
        response = self._client.get(
            _edge_path(
                "edge_team_skating_distance_detail",
                season,
                game_type,
                **{"team-id": team_id},
            ),
            web=True,
            params={},
        )
        return response.json()

    def get_team_shot_location_detail(
        self, team_id: int, season: str = "now", game_type: int = 2
    ) -> Dict:
        """Fetch a team's shot-location breakdown.

        Args:
            team_id: Numeric NHL team ID.
            season: 8-digit season (``"20252026"``) or ``"now"`` (default).
            game_type: ``2`` for regular season, ``3`` for playoffs.
                Ignored when ``season="now"``.

        Returns:
            Raw detail payload as a dictionary (``[]`` when no data).
        """
        response = self._client.get(
            _edge_path(
                "edge_team_shot_location_detail",
                season,
                game_type,
                **{"team-id": team_id},
            ),
            web=True,
            params={},
        )
        return response.json()

    def get_team_zone_time_details(
        self, team_id: int, season: str = "now", game_type: int = 2
    ) -> Dict:
        """Fetch a team's zone-time breakdown (``team-zone-time-details``).

        ⚠️ The only Edge route spelled with the plural ``-details`` suffix.
        Returns zone percentage + rank + league average by strength, plus
        ``shotDifferential``.

        Args:
            team_id: Numeric NHL team ID.
            season: 8-digit season (``"20252026"``) or ``"now"`` (default).
            game_type: ``2`` for regular season, ``3`` for playoffs.
                Ignored when ``season="now"``.

        Returns:
            Raw detail payload as a dictionary (``[]`` when no data).
        """
        response = self._client.get(
            _edge_path(
                "edge_team_zone_time_details",
                season,
                game_type,
                **{"team-id": team_id},
            ),
            web=True,
            params={},
        )
        return response.json()

    # ------------------------------------------------------------------
    # Top-10 leaderboards (validated path parameters)
    # ------------------------------------------------------------------

    def get_skater_shot_speed_top_10(
        self,
        situation: str = "all",
        sort: str = "max",
        season: str = "now",
        game_type: int = 2,
    ) -> list:
        """Fetch the top-10 hardest shots (``skater-shot-speed-top-10``).

        Args:
            situation: ``all`` (default), ``es``, ``pp`` or ``pk``. Many
                situations legitimately return ``[]``.
            sort: ``max`` (default; the only sort observed returning data)
                or ``avg``.
            season: 8-digit season (``"20252026"``) or ``"now"`` (default).
            game_type: ``2`` for regular season, ``3`` for playoffs.
                Ignored when ``season="now"``.

        Returns:
            Raw leaderboard as a list (``[]`` when no data).

        Raises:
            ValueError: If ``situation`` or ``sort`` is invalid.
        """
        situation = _validate_choice("situation", situation, SITUATION)
        sort = _validate_choice("sort", sort, SORT)
        response = self._client.get(
            _edge_path(
                "edge_skater_shot_speed_top_10",
                season,
                game_type,
                situation=situation,
                sort=sort,
            ),
            web=True,
            params={},
        )
        return response.json()

    def get_team_shot_speed_top_10(
        self,
        situation: str = "all",
        sort: str = "max",
        season: str = "now",
        game_type: int = 2,
    ) -> list:
        """Fetch the top-10 hardest-shot teams (``team-shot-speed-top-10``).

        Args:
            situation: ``all`` (default), ``es``, ``pp`` or ``pk``.
            sort: ``max`` (default) or ``avg``.
            season: 8-digit season (``"20252026"``) or ``"now"`` (default).
            game_type: ``2`` for regular season, ``3`` for playoffs.
                Ignored when ``season="now"``.

        Returns:
            Raw leaderboard as a list (``[]`` when no data).

        Raises:
            ValueError: If ``situation`` or ``sort`` is invalid.
        """
        situation = _validate_choice("situation", situation, SITUATION)
        sort = _validate_choice("sort", sort, SORT)
        response = self._client.get(
            _edge_path(
                "edge_team_shot_speed_top_10",
                season,
                game_type,
                situation=situation,
                sort=sort,
            ),
            web=True,
            params={},
        )
        return response.json()

    def get_team_skating_speed_top_10(
        self,
        situation: str = "all",
        sort: str = "max",
        season: str = "now",
        game_type: int = 2,
    ) -> list:
        """Fetch the top-10 fastest-skating teams (``team-skating-speed-top-10``).

        Args:
            situation: ``all`` (default), ``es``, ``pp`` or ``pk``.
            sort: ``max`` (default) or ``avg``.
            season: 8-digit season (``"20252026"``) or ``"now"`` (default).
            game_type: ``2`` for regular season, ``3`` for playoffs.
                Ignored when ``season="now"``.

        Returns:
            Raw leaderboard as a list (``[]`` when no data).

        Raises:
            ValueError: If ``situation`` or ``sort`` is invalid.
        """
        situation = _validate_choice("situation", situation, SITUATION)
        sort = _validate_choice("sort", sort, SORT)
        response = self._client.get(
            _edge_path(
                "edge_team_skating_speed_top_10",
                season,
                game_type,
                situation=situation,
                sort=sort,
            ),
            web=True,
            params={},
        )
        return response.json()

    def get_skater_shot_location_top_10(
        self,
        situation: str = "all",
        metric: str = "sog",
        filter_value: str = "all",
        season: str = "now",
        game_type: int = 2,
        **kwargs: Any,
    ) -> list:
        """Fetch the top-10 skaters by shot location (three-parameter form).

        Targets ``skater-shot-location-top-10/{situation}/{metric}/{filter}/...``.

        Args:
            situation: ``all`` (default), ``es``, ``pp`` or ``pk``.
            metric: ``sog`` (shots on goal, default) or ``goals``.
            filter: Rink-area filter — only ``all`` has been observed
                returning data so far.
            season: 8-digit season (``"20252026"``) or ``"now"`` (default).
            game_type: ``2`` for regular season, ``3`` for playoffs.
                Ignored when ``season="now"``.

        Returns:
            Raw leaderboard as a list (``[]`` when no data).

        Raises:
            ValueError: If ``situation``, ``metric`` or ``filter`` is invalid.
        """
        filter_value = _resolve_keyword_alias(
            filter_value, kwargs, "filter", "all"
        )
        situation = _validate_choice("situation", situation, SITUATION)
        metric = _validate_choice("metric", metric, SHOT_METRIC)
        filter_value = _validate_choice("filter", filter_value, SHOT_LOCATION_FILTER)
        response = self._client.get(
            _edge_path(
                "edge_skater_shot_location_top_10",
                season,
                game_type,
                situation=situation,
                metric=metric,
                filter=filter_value,
            ),
            web=True,
            params={},
        )
        return response.json()

    def get_team_shot_location_top_10(
        self,
        situation: str = "all",
        metric: str = "sog",
        filter_value: str = "all",
        season: str = "now",
        game_type: int = 2,
        **kwargs: Any,
    ) -> list:
        """Fetch the top-10 teams by shot location (three-parameter form).

        Targets ``team-shot-location-top-10/{situation}/{metric}/{filter}/...``.

        Args:
            situation: ``all`` (default), ``es``, ``pp`` or ``pk``.
            metric: ``sog`` (shots on goal, default) or ``goals``.
            filter: Rink-area filter — only ``all`` has been observed
                returning data so far.
            season: 8-digit season (``"20252026"``) or ``"now"`` (default).
            game_type: ``2`` for regular season, ``3`` for playoffs.
                Ignored when ``season="now"``.

        Returns:
            Raw leaderboard as a list (``[]`` when no data).

        Raises:
            ValueError: If ``situation``, ``metric`` or ``filter`` is invalid.
        """
        filter_value = _resolve_keyword_alias(
            filter_value, kwargs, "filter", "all"
        )
        situation = _validate_choice("situation", situation, SITUATION)
        metric = _validate_choice("metric", metric, SHOT_METRIC)
        filter_value = _validate_choice("filter", filter_value, SHOT_LOCATION_FILTER)
        response = self._client.get(
            _edge_path(
                "edge_team_shot_location_top_10",
                season,
                game_type,
                situation=situation,
                metric=metric,
                filter=filter_value,
            ),
            web=True,
            params={},
        )
        return response.json()

    def get_team_skating_distance_top_10(
        self,
        situation: str = "all",
        param: str = "all",
        sort: str = "total",
        season: str = "now",
        game_type: int = 2,
    ) -> list:
        """Fetch the top-10 teams by skating distance (three-parameter form).

        Targets
        ``team-skating-distance-top-10/{situation}/{param}/{sort}/...`` —
        only ``all/all/total`` was observed returning data.

        Args:
            situation: ``all`` (default), ``es``, ``pp`` or ``pk``.
            param: Distance qualifier — only ``all`` has been observed
                returning data so far.
            sort: ``total`` (default; the only sort observed returning data
                for this route — note it differs from the speed routes'
                ``max``/``avg``).
            season: 8-digit season (``"20252026"``) or ``"now"`` (default).
            game_type: ``2`` for regular season, ``3`` for playoffs.
                Ignored when ``season="now"``.

        Returns:
            Raw leaderboard as a list (``[]`` when no data).

        Raises:
            ValueError: If ``situation``, ``param`` or ``sort`` is invalid.
        """
        situation = _validate_choice("situation", situation, SITUATION)
        param = _validate_choice("param", param, DISTANCE_PARAM)
        sort = _validate_choice("sort", sort, DISTANCE_SORT)
        response = self._client.get(
            _edge_path(
                "edge_team_skating_distance_top_10",
                season,
                game_type,
                situation=situation,
                param=param,
                sort=sort,
            ),
            web=True,
            params={},
        )
        return response.json()

    def get_team_zone_time_top_10(
        self,
        situation: str = "all",
        zone: str = "offensive",
        season: str = "now",
        game_type: int = 2,
    ) -> list:
        """Fetch the top-10 teams by zone time (``team-zone-time-top-10``).

        Args:
            situation: ``all`` (default), ``es``, ``pp`` or ``pk``.
            zone: ``offensive`` (default), ``defensive`` or ``neutral``.
            season: 8-digit season (``"20252026"``) or ``"now"`` (default).
            game_type: ``2`` for regular season, ``3`` for playoffs.
                Ignored when ``season="now"``.

        Returns:
            Raw leaderboard as a list (``[]`` when no data).

        Raises:
            ValueError: If ``situation`` or ``zone`` is invalid.
        """
        situation = _validate_choice("situation", situation, SITUATION)
        zone = _validate_choice("zone", zone, ZONE)
        response = self._client.get(
            _edge_path(
                "edge_team_zone_time_top_10",
                season,
                game_type,
                situation=situation,
                zone=zone,
            ),
            web=True,
            params={},
        )
        return response.json()

    def get_goalie_shot_location_top_10(
        self,
        metric: str = "save-pctg",
        situation: str = "all",
        season: str = "now",
        game_type: int = 2,
    ) -> list:
        """Fetch the top-10 goalies by save location (metric-first route).

        ⚠️ The only Edge top-10 route whose parameter order differs:
        ``goalie-shot-location-top-10/{metric}/{situation}/...`` puts the
        metric FIRST, so this method's signature mirrors that order.
        Data for the goalie shot-location family starts in 2025-26.

        Args:
            metric: ``save-pctg`` (default), ``saves`` or ``goals-against``.
            situation: ``all`` (default) — the only situation observed
                returning data. ``es``/``pp``/``pk`` are accepted.
            season: 8-digit season (``"20252026"``) or ``"now"`` (default).
            game_type: ``2`` for regular season, ``3`` for playoffs.
                Ignored when ``season="now"``.

        Returns:
            Raw leaderboard as a list (``[]`` when no data).

        Raises:
            ValueError: If ``metric`` or ``situation`` is invalid.
        """
        metric = _validate_choice("metric", metric, GOALIE_METRIC)
        situation = _validate_choice("situation", situation, SITUATION)
        response = self._client.get(
            _edge_path(
                "edge_goalie_shot_location_top_10",
                season,
                game_type,
                metric=metric,
                situation=situation,
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

    # ------------------------------------------------------------------
    # Goal Visualizer (Puck & Player Tracking replay frames)
    # ------------------------------------------------------------------

    def get_goal_frames(self, game_id: int, event_id: int) -> Optional[List[Dict]]:
        """Fetch the Puck & Player Tracking frames for one goal event.

        This is the data behind the "EDGE | Goal Visualizer" — an animated
        2D rink replay of the ~14 s of play leading to a goal. The frame
        list is fetched from the sprites host and parsed with the pure
        helpers :func:`puck_frames` / :func:`player_frames`.

        Pipeline (see ``docs/research/nhl-edge-endpoints.md``):

        1. ``GET /v1/ppt-replay/{game_id}/{event_id}`` (the route owned by
           ``GameClient.get_play_replay`` — no duplicated route logic here)
           and read ``goal.pptReplayUrl``.
        2. ``GET {pptReplayUrl}`` with ``Referer: https://www.nhl.com/`` —
           the sprites host 403s without it.

        Args:
            game_id: The NHL game ID (e.g. ``2025020740``).
            event_id: The goal's ``eventId`` from the play-by-play.

        Returns:
            The parsed frame list (see :func:`puck_frames` for the frame
            format and units: coordinates in inches on a 2400×1020 rink,
            timestamps as decisecond counters at 10 fps). ``None`` when the
            goal has no ``pptReplayUrl`` (preseason / no tracking coverage)
            — this is not an error and never raises.
        """
        metadata = self._client.get(
            _ppt_replay_path(game_id, event_id), web=True, params={}
        ).json()
        if not isinstance(metadata, dict):
            return None
        ppt_url = (metadata.get("goal") or {}).get("pptReplayUrl")
        if not ppt_url:
            # Absent/empty pptReplayUrl = no tracking coverage (preseason).
            return None
        response = self._client.get_raw(
            ppt_url, headers={"Referer": SPRITES_REFERER}
        )
        return response.json()
