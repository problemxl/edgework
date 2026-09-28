"""Tests for the NHL Edge client and its registry entries.

Covers Task E1 scope: the nine canonical ``edge_*`` routes (landing, detail,
comparison for skater/goalie/team), ``EdgeClient`` URL construction including
the ``now`` season shortcut and game-type substitution, the ``compare()``
fan-out (exactly two requests), ``get_available_seasons()`` discovery and
facade exposure via ``Edgework.edge``.

Covers Task E2 scope: the ten view-detail routes (including the plural
``team-zone-time-details``) and eight top-10 leaderboards with their
validated path parameters — notably the goalie route's metric-first order
and the three-parameter shot-location / skating-distance forms.

Covers Task E3 scope: the Goal Visualizer — ``get_goal_frames`` chains the
``ppt-replay`` metadata route to the sprites host (which requires the
``Referer: https://www.nhl.com/`` header and 403s without it), returns
``None`` when ``pptReplayUrl`` is absent, and the pure frame helpers
``puck_frames`` / ``player_frames`` (puck entity key "1", inch coordinates).
"""

from unittest.mock import Mock, patch

import pytest

from edgework.clients.edge_client import (
    DISTANCE_PARAM,
    DISTANCE_SORT,
    GOALIE_METRIC,
    PUCK_ENTITY_KEY,
    SHOT_LOCATION_FILTER,
    SHOT_METRIC,
    SITUATION,
    SORT,
    SPRITES_REFERER,
    ZONE,
    EdgeClient,
    _edge_path,
    _ppt_replay_path,
    _validate_choice,
    player_frames,
    puck_frames,
)
from edgework.edgework import Edgework
from edgework.endpoints import API_PATH, format_endpoint
from edgework.http_client import HttpClient

SEASON = "20252026"
PLAYER_ID = 8478402  # Connor McDavid
GOALIE_ID = 8481740
TEAM_ID = 14  # Tampa Bay
GAME_ID = 2025020740  # BUF @ EDM, 2025-26 regular season
EVENT_ID = 95
SPRITES_URL = f"https://wsr.nhle.com/sprites/{SEASON}/{GAME_ID}/ev{EVENT_ID}.json"


def _response(payload):
    """Build a mock ``httpx.Response`` surface as the clients consume it."""
    response = Mock()
    response.status_code = 200
    response.json.return_value = payload
    return response


LANDING_PAYLOAD = {
    "hardestShot": [{"playerId": PLAYER_ID, "imperial": 102.4, "metric": 165.0}],
    "seasonsWithEdgeStats": [
        {"id": 20242025, "gameTypes": [2]},
        {"id": 20252026, "gameTypes": [2, 3]},
    ],
}

PPT_METADATA = {
    "gameId": GAME_ID,
    "goal": {
        "eventId": EVENT_ID,
        "pptReplayUrl": SPRITES_URL,
    },
}

# Sprite frame fixture in the exact shape served by wsr.nhle.com: one dict
# per frame with a decisecond ``timeStamp`` and an ``onIce`` entity mapping
# keyed "1" for the puck and "{teamId digit}{sweaterNumber}" for players.
# Coordinates are inches on the 2400×1020 rink grid.
TRACKING_FRAMES = [
    {
        "timeStamp": 17685233789,
        "onIce": {
            "1": {
                "id": 1,
                "playerId": "",
                "x": 2352.46,
                "y": 390.10,
                "sweaterNumber": "",
                "teamId": "",
                "teamAbbrev": "",
            },
            "7006": {
                "id": 7006,
                "playerId": 8484145,
                "x": 2364.78,
                "y": 713.54,
                "sweaterNumber": 6,
                "teamId": 7,
                "teamAbbrev": "BUF",
            },
            "22097": {
                "id": 22097,
                "playerId": PLAYER_ID,
                "x": 1800.0,
                "y": 500.0,
                "sweaterNumber": 97,
                "teamId": 22,
                "teamAbbrev": "EDM",
            },
        },
    },
    {
        "timeStamp": 17685233799,
        "onIce": {
            "1": {"id": 1, "playerId": "", "x": 2330.0, "y": 388.0},
            "7006": {
                "id": 7006,
                "playerId": 8484145,
                "x": 2360.0,
                "y": 710.0,
                "sweaterNumber": 6,
                "teamId": 7,
                "teamAbbrev": "BUF",
            },
        },
    },
]


@pytest.fixture
def mock_client():
    """Create a mock HTTP client."""
    return Mock(spec=HttpClient)


@pytest.fixture
def edge(mock_client):
    """EdgeClient wired to a mocked HTTP client."""
    return EdgeClient(http_client=mock_client)


# ---------------------------------------------------------------------------
# Registry: the nine canonical Edge routes
# ---------------------------------------------------------------------------


class TestEdgeRegistry:
    """The ``edge_*`` namespace registers the nine canonical routes."""

    @pytest.mark.parametrize(
        "key,expected",
        [
            (
                "edge_skater_landing",
                "/{API_VERSION}/edge/skater-landing/{season}/{game-type}",
            ),
            (
                "edge_goalie_landing",
                "/{API_VERSION}/edge/goalie-landing/{season}/{game-type}",
            ),
            (
                "edge_team_landing",
                "/{API_VERSION}/edge/team-landing/{season}/{game-type}",
            ),
            (
                "edge_skater_detail",
                "/{API_VERSION}/edge/skater-detail/{player-id}/{season}/{game-type}",
            ),
            (
                "edge_goalie_detail",
                "/{API_VERSION}/edge/goalie-detail/{player-id}/{season}/{game-type}",
            ),
            (
                "edge_team_detail",
                "/{API_VERSION}/edge/team-detail/{team-id}/{season}/{game-type}",
            ),
            (
                "edge_skater_comparison",
                "/{API_VERSION}/edge/skater-comparison/{player-id}/{season}/{game-type}",
            ),
            (
                "edge_goalie_comparison",
                "/{API_VERSION}/edge/goalie-comparison/{player-id}/{season}/{game-type}",
            ),
            (
                "edge_team_comparison",
                "/{API_VERSION}/edge/team-comparison/{team-id}/{season}/{game-type}",
            ),
            # Task E2: view-detail routes (spelled exactly as the API serves
            # them — team-zone-time-details is the only plural form).
            (
                "edge_skater_shot_speed_detail",
                "/{API_VERSION}/edge/skater-shot-speed-detail/{player-id}/{season}/{game-type}",
            ),
            (
                "edge_skater_skating_speed_detail",
                "/{API_VERSION}/edge/skater-skating-speed-detail/{player-id}/{season}/{game-type}",
            ),
            (
                "edge_skater_skating_distance_detail",
                "/{API_VERSION}/edge/skater-skating-distance-detail/{player-id}/{season}/{game-type}",
            ),
            (
                "edge_skater_shot_location_detail",
                "/{API_VERSION}/edge/skater-shot-location-detail/{player-id}/{season}/{game-type}",
            ),
            (
                "edge_goalie_shot_location_detail",
                "/{API_VERSION}/edge/goalie-shot-location-detail/{player-id}/{season}/{game-type}",
            ),
            (
                "edge_team_shot_speed_detail",
                "/{API_VERSION}/edge/team-shot-speed-detail/{team-id}/{season}/{game-type}",
            ),
            (
                "edge_team_skating_speed_detail",
                "/{API_VERSION}/edge/team-skating-speed-detail/{team-id}/{season}/{game-type}",
            ),
            (
                "edge_team_skating_distance_detail",
                "/{API_VERSION}/edge/team-skating-distance-detail/{team-id}/{season}/{game-type}",
            ),
            (
                "edge_team_shot_location_detail",
                "/{API_VERSION}/edge/team-shot-location-detail/{team-id}/{season}/{game-type}",
            ),
            (
                "edge_team_zone_time_details",
                "/{API_VERSION}/edge/team-zone-time-details/{team-id}/{season}/{game-type}",
            ),
            # Task E2: top-10 routes (differing param orders are intentional).
            (
                "edge_skater_shot_speed_top_10",
                "/{API_VERSION}/edge/skater-shot-speed-top-10/{situation}/{sort}/{season}/{game-type}",
            ),
            (
                "edge_team_shot_speed_top_10",
                "/{API_VERSION}/edge/team-shot-speed-top-10/{situation}/{sort}/{season}/{game-type}",
            ),
            (
                "edge_team_skating_speed_top_10",
                "/{API_VERSION}/edge/team-skating-speed-top-10/{situation}/{sort}/{season}/{game-type}",
            ),
            (
                "edge_skater_shot_location_top_10",
                "/{API_VERSION}/edge/skater-shot-location-top-10/{situation}/{metric}/{filter}/{season}/{game-type}",
            ),
            (
                "edge_team_shot_location_top_10",
                "/{API_VERSION}/edge/team-shot-location-top-10/{situation}/{metric}/{filter}/{season}/{game-type}",
            ),
            (
                "edge_team_skating_distance_top_10",
                "/{API_VERSION}/edge/team-skating-distance-top-10/{situation}/{param}/{sort}/{season}/{game-type}",
            ),
            (
                "edge_team_zone_time_top_10",
                "/{API_VERSION}/edge/team-zone-time-top-10/{situation}/{zone}/{season}/{game-type}",
            ),
            (
                "edge_goalie_shot_location_top_10",
                "/{API_VERSION}/edge/goalie-shot-location-top-10/{metric}/{situation}/{season}/{game-type}",
            ),
        ],
    )
    def test_edge_routes_registered(self, key, expected):
        """Verify test edge routes registered."""
        assert API_PATH[key] == expected

    @staticmethod
    def test_team_routes_use_team_id_placeholder():
        """Skater/goalie carry {player-id}; team routes carry {team-id}."""
        assert "{player-id}" in API_PATH["edge_skater_detail"]
        assert "{player-id}" in API_PATH["edge_goalie_detail"]
        assert "{team-id}" in API_PATH["edge_team_detail"]
        assert "{player-id}" in API_PATH["edge_skater_comparison"]
        assert "{player-id}" in API_PATH["edge_goalie_comparison"]
        assert "{team-id}" in API_PATH["edge_team_comparison"]
        assert "{player-id}" in API_PATH["edge_skater_shot_speed_detail"]
        assert "{player-id}" in API_PATH["edge_goalie_shot_location_detail"]
        assert "{team-id}" in API_PATH["edge_team_shot_speed_detail"]
        assert "{team-id}" in API_PATH["edge_team_zone_time_details"]

    @staticmethod
    def test_format_endpoint_substitutes_edge_route():
        """Verify test format endpoint substitutes edge route."""
        route = format_endpoint(
            "edge_skater_landing", season=SEASON, **{"game-type": 2}
        )
        assert route == f"/v1/edge/skater-landing/{SEASON}/2"


# ---------------------------------------------------------------------------
# Path builder: "now" shortcut and game-type substitution
# ---------------------------------------------------------------------------


class TestEdgePath:
    """``_edge_path`` derives client paths from the registry templates."""

    @staticmethod
    def test_explicit_season_keeps_game_type():
        """Verify test explicit season keeps game type."""
        path = _edge_path("edge_skater_landing", SEASON, 2)
        assert path == f"edge/skater-landing/{SEASON}/2"

    @staticmethod
    def test_playoffs_game_type_substitution():
        """Verify test playoffs game type substitution."""
        path = _edge_path("edge_skater_landing", SEASON, 3)
        assert path == f"edge/skater-landing/{SEASON}/3"

    @pytest.mark.parametrize("now", ["now", "NOW"])
    def test_now_replaces_season_and_game_type(self, now):
        """Verify test now replaces season and game type."""
        path = _edge_path("edge_skater_landing", now, 2)
        assert path == "edge/skater-landing/now"
        assert not path.endswith("/2")

    @staticmethod
    def test_now_with_entity_id():
        """Verify test now with entity id."""
        path = _edge_path("edge_skater_detail", "now", 2, **{"player-id": PLAYER_ID})
        assert path == f"edge/skater-detail/{PLAYER_ID}/now"

    @staticmethod
    def test_now_with_team_id_containing_game_type_digit():
        """The tail split must not trip over ids that contain the digits."""
        path = _edge_path("edge_team_detail", "now", 2, **{"team-id": 22})
        assert path == "edge/team-detail/22/now"

    @staticmethod
    def test_version_segment_stripped():
        """HttpClient.get(web=True) prepends /v1 itself — paths omit it."""
        path = _edge_path("edge_team_comparison", SEASON, 2, **{"team-id": TEAM_ID})
        assert not path.startswith("v1/")
        assert path == f"edge/team-comparison/{TEAM_ID}/{SEASON}/2"


# ---------------------------------------------------------------------------
# Landing pages
# ---------------------------------------------------------------------------


class TestEdgeLanding:
    """Landing methods target the canonical routes and return raw dicts."""

    def test_get_skater_landing_defaults_to_now(self, mock_client, edge):
        """Verify test get skater landing defaults to now."""
        mock_client.get.return_value = _response(LANDING_PAYLOAD)

        result = edge.get_skater_landing()

        mock_client.get.assert_called_once_with(
            "edge/skater-landing/now", web=True, params={}
        )
        assert result == LANDING_PAYLOAD

    @pytest.mark.parametrize(
        "method,route", [
            ("get_goalie_landing", "edge/goalie-landing"),
            ("get_team_landing", "edge/team-landing"),
        ]
    )
    def test_goalie_and_team_landing_routes(self, mock_client, edge, method, route):
        """Verify test goalie and team landing routes."""
        mock_client.get.return_value = _response({})

        getattr(edge, method)(season=SEASON, game_type=3)

        mock_client.get.assert_called_once_with(
            f"{route}/{SEASON}/3", web=True, params={}
        )

    def test_empty_landing_passes_through(self, mock_client, edge):
        """Valid route with no data returns [] — never raises."""
        mock_client.get.return_value = _response([])

        assert edge.get_team_landing() == []

    def test_season_and_game_type_forwarded(self, mock_client, edge):
        """Verify test season and game type forwarded."""
        mock_client.get.return_value = _response({})

        edge.get_skater_landing(season=SEASON, game_type=3)

        mock_client.get.assert_called_once_with(
            f"edge/skater-landing/{SEASON}/3", web=True, params={}
        )


class TestAvailableSeasons:
    """``get_available_seasons`` exposes ``seasonsWithEdgeStats``."""

    def test_returns_seasons_with_edge_stats(self, mock_client, edge):
        """Verify test returns seasons with edge stats."""
        mock_client.get.return_value = _response(LANDING_PAYLOAD)

        seasons = edge.get_available_seasons()

        assert seasons == LANDING_PAYLOAD["seasonsWithEdgeStats"]
        # Discovery hits the (default "now") skater landing route.
        mock_client.get.assert_called_once_with(
            "edge/skater-landing/now", web=True, params={}
        )

    def test_missing_field_returns_empty_list(self, mock_client, edge):
        """Verify test missing field returns empty list."""
        mock_client.get.return_value = _response({})

        assert edge.get_available_seasons() == []

    def test_none_field_returns_empty_list(self, mock_client, edge):
        """Verify test none field returns empty list."""
        mock_client.get.return_value = _response({"seasonsWithEdgeStats": None})

        assert edge.get_available_seasons() == []


# ---------------------------------------------------------------------------
# Base detail
# ---------------------------------------------------------------------------


class TestEdgeDetail:
    """Detail methods substitute entity ids into the canonical routes."""

    def test_get_skater_detail_defaults_to_now(self, mock_client, edge):
        """Verify test get skater detail defaults to now."""
        mock_client.get.return_value = _response({"player": {}, "stats": {}})

        edge.get_skater_detail(PLAYER_ID)

        mock_client.get.assert_called_once_with(
            f"edge/skater-detail/{PLAYER_ID}/now", web=True, params={}
        )

    def test_get_goalie_detail_explicit_season(self, mock_client, edge):
        """Verify test get goalie detail explicit season."""
        mock_client.get.return_value = _response({"player": {}, "stats": {}})

        edge.get_goalie_detail(GOALIE_ID, season=SEASON, game_type=3)

        mock_client.get.assert_called_once_with(
            f"edge/goalie-detail/{GOALIE_ID}/{SEASON}/3", web=True, params={}
        )

    def test_get_team_detail_uses_team_id(self, mock_client, edge):
        """Verify test get team detail uses team id."""
        mock_client.get.return_value = _response({"team": {}})

        edge.get_team_detail(TEAM_ID, season=SEASON)

        mock_client.get.assert_called_once_with(
            f"edge/team-detail/{TEAM_ID}/{SEASON}/2", web=True, params={}
        )

    def test_empty_detail_passes_through(self, mock_client, edge):
        """Verify test empty detail passes through."""
        mock_client.get.return_value = _response([])

        assert edge.get_skater_detail(PLAYER_ID) == []


# ---------------------------------------------------------------------------
# Comparison payloads (one payload per entity)
# ---------------------------------------------------------------------------


class TestEdgeComparison:
    """Per-entity comparison methods own the canonical comparison routes."""

    @pytest.mark.parametrize(
        "method,route,entity_id", [
            ("get_skater_comparison", "edge/skater-comparison", PLAYER_ID),
            ("get_goalie_comparison", "edge/goalie-comparison", GOALIE_ID),
            ("get_team_comparison", "edge/team-comparison", TEAM_ID),
        ]
    )
    def test_comparison_routes(self, mock_client, edge, method, route, entity_id):
        """Verify test comparison routes."""
        mock_client.get.return_value = _response({})

        getattr(edge, method)(entity_id, season=SEASON)

        mock_client.get.assert_called_once_with(
            f"{route}/{entity_id}/{SEASON}/2", web=True, params={}
        )

    def test_comparison_now(self, mock_client, edge):
        """Verify test comparison now."""
        mock_client.get.return_value = _response({})

        edge.get_skater_comparison(PLAYER_ID)

        mock_client.get.assert_called_once_with(
            f"edge/skater-comparison/{PLAYER_ID}/now", web=True, params={}
        )


# ---------------------------------------------------------------------------
# View-specific detail (Task E2)
# ---------------------------------------------------------------------------


class TestEdgeViewDetail:
    """View-detail methods target their per-metric canonical routes."""

    @pytest.mark.parametrize(
        "method,route,entity_id,entity_param", [
            ("get_skater_shot_speed_detail", "edge/skater-shot-speed-detail", PLAYER_ID, "player-id"),
            ("get_skater_skating_speed_detail", "edge/skater-skating-speed-detail", PLAYER_ID, "player-id"),
            ("get_skater_skating_distance_detail", "edge/skater-skating-distance-detail", PLAYER_ID, "player-id"),
            ("get_skater_shot_location_detail", "edge/skater-shot-location-detail", PLAYER_ID, "player-id"),
            ("get_goalie_shot_location_detail", "edge/goalie-shot-location-detail", GOALIE_ID, "player-id"),
            ("get_team_shot_speed_detail", "edge/team-shot-speed-detail", TEAM_ID, "team-id"),
            ("get_team_skating_speed_detail", "edge/team-skating-speed-detail", TEAM_ID, "team-id"),
            ("get_team_skating_distance_detail", "edge/team-skating-distance-detail", TEAM_ID, "team-id"),
            ("get_team_shot_location_detail", "edge/team-shot-location-detail", TEAM_ID, "team-id"),
            ("get_team_zone_time_details", "edge/team-zone-time-details", TEAM_ID, "team-id"),
        ]
    )
    def test_view_detail_defaults_to_now(
        self, mock_client, edge, method, route, entity_id, entity_param
    ):
        """Verify test view detail defaults to now."""
        mock_client.get.return_value = _response({})

        getattr(edge, method)(entity_id)

        mock_client.get.assert_called_once_with(
            f"{route}/{entity_id}/now", web=True, params={}
        )

    @pytest.mark.parametrize(
        "method,route,entity_id", [
            ("get_skater_shot_speed_detail", "edge/skater-shot-speed-detail", PLAYER_ID),
            ("get_team_zone_time_details", "edge/team-zone-time-details", TEAM_ID),
        ]
    )
    def test_view_detail_season_and_game_type(
        self, mock_client, edge, method, route, entity_id
    ):
        """Verify test view detail season and game type."""
        mock_client.get.return_value = _response({})

        getattr(edge, method)(entity_id, season=SEASON, game_type=3)

        mock_client.get.assert_called_once_with(
            f"{route}/{entity_id}/{SEASON}/3", web=True, params={}
        )

    @staticmethod
    def test_zone_time_details_route_is_plural():
        """team-zone-time-details is the only Edge route spelled -details."""
        assert "team-zone-time-details" in API_PATH["edge_team_zone_time_details"]
        assert "edge_team_zone_time_detail" not in API_PATH

    def test_empty_view_detail_passes_through(self, mock_client, edge):
        """Valid route with no data returns [] — never raises."""
        mock_client.get.return_value = _response([])

        assert edge.get_team_zone_time_details(TEAM_ID) == []


# ---------------------------------------------------------------------------
# Top-10 leaderboards (Task E2)
# ---------------------------------------------------------------------------


class TestEdgeTop10:
    """Top-10 methods build the exact per-family parameter orders."""

    @pytest.mark.parametrize(
        "method,route", [
            ("get_skater_shot_speed_top_10", "edge/skater-shot-speed-top-10"),
            ("get_team_shot_speed_top_10", "edge/team-shot-speed-top-10"),
            ("get_team_skating_speed_top_10", "edge/team-skating-speed-top-10"),
        ]
    )
    def test_speed_top10_param_order(self, mock_client, edge, method, route):
        """Speed routes: {situation}/{sort} then season/game-type."""
        mock_client.get.return_value = _response([])

        result = getattr(edge, method)(situation="es", sort="avg")

        mock_client.get.assert_called_once_with(
            f"{route}/es/avg/now", web=True, params={}
        )
        assert result == []

    def test_speed_top10_explicit_season_and_playoffs(self, mock_client, edge):
        """Verify test speed top10 explicit season and playoffs."""
        mock_client.get.return_value = _response([])

        edge.get_skater_shot_speed_top_10(
            situation="pp", sort="max", season=SEASON, game_type=3
        )

        mock_client.get.assert_called_once_with(
            f"edge/skater-shot-speed-top-10/pp/max/{SEASON}/3", web=True, params={}
        )

    @pytest.mark.parametrize(
        "method,route", [
            ("get_skater_shot_location_top_10", "edge/skater-shot-location-top-10"),
            ("get_team_shot_location_top_10", "edge/team-shot-location-top-10"),
        ]
    )
    def test_shot_location_top10_three_param_form(
        self, mock_client, edge, method, route
    ):
        """Verify test shot location top10 three param form."""
        """Shot-location routes: {situation}/{metric}/{filter} then tail."""
        mock_client.get.return_value = _response([])

        getattr(edge, method)(situation="all", metric="goals", filter="all")

        mock_client.get.assert_called_once_with(
            f"{route}/all/goals/all/now", web=True, params={}
        )

    def test_skating_distance_top10_three_param_form(self, mock_client, edge):
        """Distance route: {situation}/{param}/{sort} then tail."""
        mock_client.get.return_value = _response([])

        edge.get_team_skating_distance_top_10(
            situation="all", param="all", sort="total"
        )

        mock_client.get.assert_called_once_with(
            "edge/team-skating-distance-top-10/all/all/total/now",
            web=True,
            params={},
        )

    def test_zone_time_top10_param_order(self, mock_client, edge):
        """Zone-time route: {situation}/{zone} then tail."""
        mock_client.get.return_value = _response([])

        edge.get_team_zone_time_top_10(situation="es", zone="neutral")

        mock_client.get.assert_called_once_with(
            "edge/team-zone-time-top-10/es/neutral/now", web=True, params={}
        )

    def test_goalie_top10_metric_first(self, mock_client, edge):
        """⚠️ The goalie route puts the metric FIRST: {metric}/{situation}."""
        mock_client.get.return_value = _response([])

        edge.get_goalie_shot_location_top_10(metric="saves", situation="all")

        mock_client.get.assert_called_once_with(
            "edge/goalie-shot-location-top-10/saves/all/now", web=True, params={}
        )

    def test_goalie_top10_metric_position_is_not_situation(self, mock_client, edge):
        """The first path segment after the view is the metric, not situation."""
        mock_client.get.return_value = _response([])

        edge.get_goalie_shot_location_top_10(metric="goals-against", situation="all")

        path = mock_client.get.call_args.args[0]
        assert path.startswith("edge/goalie-shot-location-top-10/goals-against/")
        assert not path.startswith("edge/goalie-shot-location-top-10/all/")

    def test_empty_top10_passes_through(self, mock_client, edge):
        """Valid route + empty result (e.g. es/max speed top-10) returns []."""
        mock_client.get.return_value = _response([])

        assert edge.get_team_skating_speed_top_10(situation="es", sort="max") == []


class TestEdgeParamValidation:
    """Top-10 parameters are validated before any request is made."""

    @pytest.mark.parametrize(
        "call", [
            lambda edge: edge.get_skater_shot_speed_top_10(situation="5v5"),
            lambda edge: edge.get_skater_shot_speed_top_10(sort="total"),
            lambda edge: edge.get_team_shot_speed_top_10(situation="even"),
            lambda edge: edge.get_team_skating_speed_top_10(sort="min"),
            lambda edge: edge.get_skater_shot_location_top_10(metric="hits"),
            lambda edge: edge.get_skater_shot_location_top_10(filter="danger"),
            lambda edge: edge.get_team_shot_location_top_10(metric="attempts"),
            lambda edge: edge.get_team_shot_location_top_10(filter="high"),
            lambda edge: edge.get_team_skating_distance_top_10(param="per60"),
            lambda edge: edge.get_team_skating_distance_top_10(sort="max"),
            lambda edge: edge.get_team_zone_time_top_10(zone="home"),
            lambda edge: edge.get_goalie_shot_location_top_10(metric="gaa"),
            lambda edge: edge.get_goalie_shot_location_top_10(situation="overtime"),
        ]
    )
    def test_invalid_params_raise_and_skip_http(self, mock_client, edge, call):
        """Verify test invalid params raise and skip http."""
        with pytest.raises(ValueError):
            call(edge)
        mock_client.get.assert_not_called()

    def test_invalid_situation_message_names_choice(self, edge):
        """Verify test invalid situation message names choice."""
        with pytest.raises(ValueError, match="situation must be one of") as excinfo:
            edge.get_team_zone_time_top_10(situation="5v5")
        assert "'all', 'es', 'pk', 'pp'" in str(excinfo.value)

    def test_distance_sort_rejects_speed_sort_values(self, edge):
        """The distance route's sort is 'total', not the speed max/avg."""
        with pytest.raises(ValueError, match="sort must be one of"):
            edge.get_team_skating_distance_top_10(sort="avg")

    @pytest.mark.parametrize(
        "call", [
            lambda edge: edge.get_skater_shot_speed_top_10(situation="PP", sort="MAX"),
            lambda edge: edge.get_goalie_shot_location_top_10(metric="Save-Pctg"),
            lambda edge: edge.get_team_zone_time_top_10(zone="Defensive"),
            lambda edge: edge.get_team_skating_distance_top_10(sort="Total"),
        ]
    )
    def test_params_normalized_case_insensitively(self, mock_client, edge, call):
        """Verify test params normalized case insensitively."""
        mock_client.get.return_value = _response([])

        call(edge)

        mock_client.get.assert_called_once()

    @staticmethod
    def test_validation_helper():
        """Verify test validation helper."""
        assert _validate_choice("zone", "OFFENSIVE", ZONE) == "offensive"
        with pytest.raises(ValueError, match="zone must be one of"):
            _validate_choice("zone", "garbage", ZONE)

    @staticmethod
    def test_param_enums_contents():
        """Module-level enums match the researched option lists."""
        assert SITUATION == frozenset({"all", "es", "pp", "pk"})
        assert SORT == frozenset({"max", "avg"})
        assert SHOT_METRIC == frozenset({"sog", "goals"})
        assert ZONE == frozenset({"offensive", "defensive", "neutral"})
        assert GOALIE_METRIC == frozenset({"save-pctg", "saves", "goals-against"})
        assert SHOT_LOCATION_FILTER == frozenset({"all"})
        assert DISTANCE_PARAM == frozenset({"all"})
        assert DISTANCE_SORT == frozenset({"total"})


# ---------------------------------------------------------------------------
# compare() fan-out
# ---------------------------------------------------------------------------


class TestCompareFanOut:
    """``compare()`` fetches both sides with exactly two HTTP requests."""

    def test_compare_returns_a_and_b(self, mock_client, edge):
        """Verify test compare returns a and b."""
        payload_a = {"playerId": PLAYER_ID, "shotSpeedDetails": []}
        payload_b = {"playerId": 8478402 + 1, "shotSpeedDetails": []}
        mock_client.get.side_effect = [_response(payload_a), _response(payload_b)]

        result = edge.compare("skater", PLAYER_ID, 8478402 + 1, season=SEASON)

        assert result == {"a": payload_a, "b": payload_b}
        assert mock_client.get.call_count == 2

    @pytest.mark.parametrize(
        "entity,route,entity_id", [
            ("skater", "edge/skater-comparison", PLAYER_ID),
            ("goalie", "edge/goalie-comparison", GOALIE_ID),
            ("team", "edge/team-comparison", TEAM_ID),
        ]
    )
    def test_compare_dispatches_to_entity_route(
        self, mock_client, edge, entity, route, entity_id
    ):
        """Verify test compare dispatches to entity route."""
        mock_client.get.return_value = _response({})

        edge.compare(entity, entity_id, entity_id + 1)

        requested = [call.args[0] for call in mock_client.get.call_args_list]
        assert requested == [
            f"{route}/{entity_id}/now",
            f"{route}/{entity_id + 1}/now",
        ]

    def test_compare_forwards_season_and_game_type(self, mock_client, edge):
        """Verify test compare forwards season and game type."""
        mock_client.get.return_value = _response({})

        edge.compare("team", TEAM_ID, TEAM_ID + 1, season=SEASON, game_type=3)

        requested = [call.args[0] for call in mock_client.get.call_args_list]
        assert requested == [
            f"edge/team-comparison/{TEAM_ID}/{SEASON}/3",
            f"edge/team-comparison/{TEAM_ID + 1}/{SEASON}/3",
        ]

    def test_compare_rejects_unknown_entity(self, edge):
        """Verify test compare rejects unknown entity."""
        with pytest.raises(ValueError, match="entity must be one of"):
            edge.compare("referee", 1, 2)
        # No request may be emitted for an invalid entity.
        edge._client.get.assert_not_called()


# ---------------------------------------------------------------------------
# Goal Visualizer: get_goal_frames (Task E3)
# ---------------------------------------------------------------------------


class TestGoalFrames:
    """``get_goal_frames`` chains ppt-replay metadata → sprites frames."""

    def test_full_pipeline_sends_referer(self, mock_client, edge):
        """Verify test full pipeline sends referer."""
        mock_client.get.return_value = _response(PPT_METADATA)
        mock_client.get_raw.return_value = _response(TRACKING_FRAMES)

        result = edge.get_goal_frames(GAME_ID, EVENT_ID)

        # Step 1: metadata via the canonical play_replay route.
        mock_client.get.assert_called_once_with(
            f"ppt-replay/{GAME_ID}/{EVENT_ID}", web=True, params={}
        )
        # Step 2: the sprites host 403s without the Referer header.
        mock_client.get_raw.assert_called_once_with(
            SPRITES_URL, headers={"Referer": SPRITES_REFERER}
        )
        assert result == TRACKING_FRAMES

    def test_returns_none_when_ppt_replay_url_absent(self, mock_client, edge):
        """Preseason/no-coverage goals omit pptReplayUrl — return None."""
        mock_client.get.return_value = _response(
            {"gameId": GAME_ID, "goal": {"eventId": EVENT_ID}}
        )

        assert edge.get_goal_frames(GAME_ID, EVENT_ID) is None
        mock_client.get.assert_called_once()
        mock_client.get_raw.assert_not_called()

    def test_returns_none_for_empty_payload(self, mock_client, edge):
        """Verify test returns none for empty payload."""
        mock_client.get.return_value = _response({})

        assert edge.get_goal_frames(GAME_ID, EVENT_ID) is None
        mock_client.get_raw.assert_not_called()

    def test_returns_none_for_empty_url(self, mock_client, edge):
        """Verify test returns none for empty url."""
        mock_client.get.return_value = _response({"goal": {"pptReplayUrl": ""}})

        assert edge.get_goal_frames(GAME_ID, EVENT_ID) is None
        mock_client.get_raw.assert_not_called()

    def test_returns_none_for_non_dict_payload(self, mock_client, edge):
        """Verify test returns none for non dict payload."""
        mock_client.get.return_value = _response([])

        assert edge.get_goal_frames(GAME_ID, EVENT_ID) is None
        mock_client.get_raw.assert_not_called()

    @staticmethod
    def test_ppt_replay_path_comes_from_the_registry():
        """_ppt_replay_path reuses the play_replay entry (no duplicated route)."""
        assert _ppt_replay_path(GAME_ID, EVENT_ID) == f"ppt-replay/{GAME_ID}/{EVENT_ID}"
        from edgework.endpoints import API_VERSION

        assert API_PATH["play_replay"] == (
            f"/{{API_VERSION}}/ppt-replay/{{game_id}}/{{event_number}}"
        )
        assert API_VERSION == "v1"


# ---------------------------------------------------------------------------
# Goal Visualizer: pure frame helpers (Task E3)
# ---------------------------------------------------------------------------


class TestFrameHelpers:
    """``puck_frames`` / ``player_frames`` parse the sprite frame format."""

    @staticmethod
    def test_puck_frames_extracts_entity_key_one():
        """Verify test puck frames extracts entity key one."""
        assert puck_frames(TRACKING_FRAMES) == [
            (17685233789, 2352.46, 390.10),
            (17685233799, 2330.0, 388.0),
        ]

    @staticmethod
    def test_puck_frames_empty_input():
        """Verify test puck frames empty input."""
        assert puck_frames([]) == []

    @staticmethod
    def test_puck_frames_skips_frame_without_puck():
        """Verify test puck frames skips frame without puck."""
        frames = [{"timeStamp": 1, "onIce": {}}, TRACKING_FRAMES[0]]

        assert puck_frames(frames) == [(17685233789, 2352.46, 390.10)]

    @staticmethod
    def test_puck_frames_handles_missing_on_ice():
        """Verify test puck frames handles missing on ice."""
        assert puck_frames([{"timeStamp": 1}]) == []

    @staticmethod
    def test_puck_entity_key_is_one():
        """Verify test puck entity key is one."""
        assert PUCK_ENTITY_KEY == "1"

    @staticmethod
    def test_player_frames_returns_all_players():
        """Verify test player frames returns all players."""
        tracks = player_frames(TRACKING_FRAMES)

        assert set(tracks) == {8484145, PLAYER_ID}
        assert tracks[8484145] == [
            (17685233789, 2364.78, 713.54),
            (17685233799, 2360.0, 710.0),
        ]
        assert tracks[PLAYER_ID] == [(17685233789, 1800.0, 500.0)]

    @staticmethod
    def test_player_frames_single_player():
        """Verify test player frames single player."""
        assert player_frames(TRACKING_FRAMES, player_id=8484145) == [
            (17685233789, 2364.78, 713.54),
            (17685233799, 2360.0, 710.0),
        ]

    @staticmethod
    def test_player_frames_unknown_player_is_empty_list():
        """Verify test player frames unknown player is empty list."""
        assert player_frames(TRACKING_FRAMES, player_id=1234567) == []

    @staticmethod
    def test_player_frames_exclude_the_puck():
        """The puck has no playerId — it must not appear in player tracks."""
        tracks = player_frames(TRACKING_FRAMES)

        assert PUCK_ENTITY_KEY not in {str(pid) for pid in tracks}
        assert all(frames for frames in tracks.values())

    @staticmethod
    def test_coordinates_are_inch_grid():
        """Fixture sanity: coordinates stay inside the 2400×1020 inch rink."""
        for frame in TRACKING_FRAMES:
            for entity in frame["onIce"].values():
                assert 0 <= entity["x"] <= 2400
                assert 0 <= entity["y"] <= 1020


# ---------------------------------------------------------------------------
# Facade exposure
# ---------------------------------------------------------------------------


class TestEdgeFacade:
    """``Edgework.edge`` exposes the EdgeClient on the shared HTTP client."""

    @patch("edgework.edgework.HttpClient")
    def test_facade_exposes_edge_client(self, mock_http_client):
        """Verify test facade exposes edge client."""
        mock_http_client.return_value = Mock(spec=HttpClient)

        edgework = Edgework()

        assert isinstance(edgework.edge, EdgeClient)
        assert edgework.edge._client is edgework._client
