"""Tests for the NHL Edge client and its registry entries.

Covers Task E1 scope: the nine canonical ``edge_*`` routes (landing, detail,
comparison for skater/goalie/team), ``EdgeClient`` URL construction including
the ``now`` season shortcut and game-type substitution, the ``compare()``
fan-out (exactly two requests), ``get_available_seasons()`` discovery and
facade exposure via ``Edgework.edge``.
"""

from unittest.mock import Mock, patch

import pytest

from edgework.clients.edge_client import EdgeClient, _edge_path
from edgework.edgework import Edgework
from edgework.endpoints import API_PATH, format_endpoint
from edgework.http_client import HttpClient

SEASON = "20252026"
PLAYER_ID = 8478402  # Connor McDavid
GOALIE_ID = 8481740
TEAM_ID = 14  # Tampa Bay


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
        ],
    )
    def test_edge_routes_registered(self, key, expected):
        assert API_PATH[key] == expected

    def test_team_routes_use_team_id_placeholder(self):
        """Skater/goalie carry {player-id}; team routes carry {team-id}."""
        assert "{player-id}" in API_PATH["edge_skater_detail"]
        assert "{player-id}" in API_PATH["edge_goalie_detail"]
        assert "{team-id}" in API_PATH["edge_team_detail"]
        assert "{player-id}" in API_PATH["edge_skater_comparison"]
        assert "{player-id}" in API_PATH["edge_goalie_comparison"]
        assert "{team-id}" in API_PATH["edge_team_comparison"]

    def test_format_endpoint_substitutes_edge_route(self):
        route = format_endpoint(
            "edge_skater_landing", season=SEASON, **{"game-type": 2}
        )
        assert route == f"/v1/edge/skater-landing/{SEASON}/2"


# ---------------------------------------------------------------------------
# Path builder: "now" shortcut and game-type substitution
# ---------------------------------------------------------------------------


class TestEdgePath:
    """``_edge_path`` derives client paths from the registry templates."""

    def test_explicit_season_keeps_game_type(self):
        path = _edge_path("edge_skater_landing", SEASON, 2)
        assert path == f"edge/skater-landing/{SEASON}/2"

    def test_playoffs_game_type_substitution(self):
        path = _edge_path("edge_skater_landing", SEASON, 3)
        assert path == f"edge/skater-landing/{SEASON}/3"

    @pytest.mark.parametrize("now", ["now", "NOW"])
    def test_now_replaces_season_and_game_type(self, now):
        path = _edge_path("edge_skater_landing", now, 2)
        assert path == "edge/skater-landing/now"
        assert not path.endswith("/2")

    def test_now_with_entity_id(self):
        path = _edge_path("edge_skater_detail", "now", 2, **{"player-id": PLAYER_ID})
        assert path == f"edge/skater-detail/{PLAYER_ID}/now"

    def test_now_with_team_id_containing_game_type_digit(self):
        """The tail split must not trip over ids that contain the digits."""
        path = _edge_path("edge_team_detail", "now", 2, **{"team-id": 22})
        assert path == "edge/team-detail/22/now"

    def test_version_segment_stripped(self):
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
        mock_client.get.return_value = _response({})

        edge.get_skater_landing(season=SEASON, game_type=3)

        mock_client.get.assert_called_once_with(
            f"edge/skater-landing/{SEASON}/3", web=True, params={}
        )


class TestAvailableSeasons:
    """``get_available_seasons`` exposes ``seasonsWithEdgeStats``."""

    def test_returns_seasons_with_edge_stats(self, mock_client, edge):
        mock_client.get.return_value = _response(LANDING_PAYLOAD)

        seasons = edge.get_available_seasons()

        assert seasons == LANDING_PAYLOAD["seasonsWithEdgeStats"]
        # Discovery hits the (default "now") skater landing route.
        mock_client.get.assert_called_once_with(
            "edge/skater-landing/now", web=True, params={}
        )

    def test_missing_field_returns_empty_list(self, mock_client, edge):
        mock_client.get.return_value = _response({})

        assert edge.get_available_seasons() == []

    def test_none_field_returns_empty_list(self, mock_client, edge):
        mock_client.get.return_value = _response({"seasonsWithEdgeStats": None})

        assert edge.get_available_seasons() == []


# ---------------------------------------------------------------------------
# Base detail
# ---------------------------------------------------------------------------


class TestEdgeDetail:
    """Detail methods substitute entity ids into the canonical routes."""

    def test_get_skater_detail_defaults_to_now(self, mock_client, edge):
        mock_client.get.return_value = _response({"player": {}, "stats": {}})

        edge.get_skater_detail(PLAYER_ID)

        mock_client.get.assert_called_once_with(
            f"edge/skater-detail/{PLAYER_ID}/now", web=True, params={}
        )

    def test_get_goalie_detail_explicit_season(self, mock_client, edge):
        mock_client.get.return_value = _response({"player": {}, "stats": {}})

        edge.get_goalie_detail(GOALIE_ID, season=SEASON, game_type=3)

        mock_client.get.assert_called_once_with(
            f"edge/goalie-detail/{GOALIE_ID}/{SEASON}/3", web=True, params={}
        )

    def test_get_team_detail_uses_team_id(self, mock_client, edge):
        mock_client.get.return_value = _response({"team": {}})

        edge.get_team_detail(TEAM_ID, season=SEASON)

        mock_client.get.assert_called_once_with(
            f"edge/team-detail/{TEAM_ID}/{SEASON}/2", web=True, params={}
        )

    def test_empty_detail_passes_through(self, mock_client, edge):
        mock_client.get.return_value = _response([])

        assert edge.get_skater_detail(PLAYER_ID) == []


# ---------------------------------------------------------------------------
# Comparison payloads + compare() fan-out
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
        mock_client.get.return_value = _response({})

        getattr(edge, method)(entity_id, season=SEASON)

        mock_client.get.assert_called_once_with(
            f"{route}/{entity_id}/{SEASON}/2", web=True, params={}
        )

    def test_comparison_now(self, mock_client, edge):
        mock_client.get.return_value = _response({})

        edge.get_skater_comparison(PLAYER_ID)

        mock_client.get.assert_called_once_with(
            f"edge/skater-comparison/{PLAYER_ID}/now", web=True, params={}
        )


class TestCompareFanOut:
    """``compare()`` fetches both sides with exactly two HTTP requests."""

    def test_compare_returns_a_and_b(self, mock_client, edge):
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
        mock_client.get.return_value = _response({})

        edge.compare(entity, entity_id, entity_id + 1)

        requested = [call.args[0] for call in mock_client.get.call_args_list]
        assert requested == [
            f"{route}/{entity_id}/now",
            f"{route}/{entity_id + 1}/now",
        ]

    def test_compare_forwards_season_and_game_type(self, mock_client, edge):
        mock_client.get.return_value = _response({})

        edge.compare("team", TEAM_ID, TEAM_ID + 1, season=SEASON, game_type=3)

        requested = [call.args[0] for call in mock_client.get.call_args_list]
        assert requested == [
            f"edge/team-comparison/{TEAM_ID}/{SEASON}/3",
            f"edge/team-comparison/{TEAM_ID + 1}/{SEASON}/3",
        ]

    def test_compare_rejects_unknown_entity(self, edge):
        with pytest.raises(ValueError, match="entity must be one of"):
            edge.compare("referee", 1, 2)
        # No request may be emitted for an invalid entity.
        edge._client.get.assert_not_called()


# ---------------------------------------------------------------------------
# Facade exposure
# ---------------------------------------------------------------------------


class TestEdgeFacade:
    """``Edgework.edge`` exposes the EdgeClient on the shared HTTP client."""

    @patch("edgework.edgework.HttpClient")
    def test_facade_exposes_edge_client(self, mock_http_client):
        mock_http_client.return_value = Mock(spec=HttpClient)

        edgework = Edgework()

        assert isinstance(edgework.edge, EdgeClient)
        assert edgework.edge._client is edgework._client
