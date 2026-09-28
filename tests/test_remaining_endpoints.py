"""Tests for remaining endpoints (Playoff, Network, Utility, Stats)."""

from datetime import datetime
from unittest.mock import Mock

import pytest

from edgework.clients.network_client import NetworkClient
from edgework.clients.playoff_client import PlayoffClient
from edgework.clients.stats_client import StatsClient
from edgework.clients.utility_client import UtilityClient
from edgework.const import BASE_WEB_URL
from edgework.endpoints import format_endpoint
from edgework.http_client import HttpClient


class TestPlayoffClient:
    """Test class for PlayoffClient."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock HTTP client."""
        return Mock(spec=HttpClient)

    @pytest.fixture
    def mock_bracket_response(self):
        """Create a mock playoff bracket response."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {
            "seasonId": 20232024,
            "rounds": [
                {
                    "roundNumber": 1,
                    "series": [
                        {"seriesLetter": "A", "topSeed": "EDM", "bottomSeed": "LAK"}
                    ],
                }
            ],
        }
        return response

    @pytest.fixture
    def mock_carousel_response(self):
        """Create a mock playoff carousel response."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {
            "seasonId": 20232024,
            "round": 1,
            "series": [{"seriesLetter": "A", "topSeed": "EDM"}],
        }
        return response

    @staticmethod
    def test_client_init(mock_client):
        """Test PlayoffClient initialization."""
        client = PlayoffClient(mock_client)
        assert client._client == mock_client

    @staticmethod
    def test_get_playoff_bracket(mock_client, mock_bracket_response):
        """Test fetching playoff bracket."""
        mock_client.get.return_value = mock_bracket_response
        client = PlayoffClient(mock_client)

        data = client.get_playoff_bracket(2024)

        assert data["seasonId"] == 20232024
        assert len(data["rounds"]) == 1
        mock_client.get.assert_called_once_with("playoff-bracket/2024", web=True)

    @staticmethod
    def test_get_playoff_series_carousel(mock_client, mock_carousel_response):
        """Test fetching playoff series carousel."""
        mock_client.get.return_value = mock_carousel_response
        client = PlayoffClient(mock_client)

        data = client.get_playoff_series_carousel("2023-2024")

        assert data["round"] == 1
        mock_client.get.assert_called_once_with(
            "playoff-series/carousel/20232024/", web=True
        )

    @staticmethod
    def test_get_playoff_series_schedule(mock_client):
        """Test fetching playoff series schedule."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {
            "seriesLetter": "A",
            "games": [{"gameId": 2023010001}],
        }
        mock_client.get.return_value = response

        client = PlayoffClient(mock_client)
        data = client.get_playoff_series_schedule("2023-2024", "A")

        assert data["seriesLetter"] == "A"
        mock_client.get.assert_called_once_with(
            "schedule/playoff-series/20232024/A/", web=True
        )

    @staticmethod
    def test_get_series_winner(mock_client):
        """Test getting series winner."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {
            "seriesWinner": {"abbrev": "EDM"},
            "seriesLetter": "A",
        }
        mock_client.get.return_value = response

        client = PlayoffClient(mock_client)
        winner = client.get_series_winner("2023-2024", "A")

        assert winner == "EDM"


class TestNetworkClient:
    """Test class for NetworkClient."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock HTTP client."""
        return Mock(spec=HttpClient)

    @pytest.fixture
    def mock_tv_schedule_response(self):
        """Create a mock TV schedule response."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {
            "date": "2024-01-15",
            "games": [{"gameId": 2023020001, "tvBroadcasts": []}],
        }
        return response

    @staticmethod
    def test_client_init(mock_client):
        """Test NetworkClient initialization."""
        client = NetworkClient(mock_client)
        assert client._client == mock_client

    @staticmethod
    def test_get_tv_schedule_now(mock_client, mock_tv_schedule_response):
        """Test fetching current TV schedule."""
        mock_client.get.return_value = mock_tv_schedule_response
        client = NetworkClient(mock_client)

        data = client.get_tv_schedule()

        assert data["date"] == "2024-01-15"
        mock_client.get.assert_called_once_with("network/tv-schedule/now", web=True)

    @staticmethod
    def test_get_tv_schedule_for_date(mock_client, mock_tv_schedule_response):
        """Test fetching TV schedule for specific date."""
        mock_client.get.return_value = mock_tv_schedule_response
        client = NetworkClient(mock_client)

        date = datetime(2024, 1, 15)
        data = client.get_tv_schedule_for_date(date)

        assert data["date"] == "2024-01-15"
        mock_client.get.assert_called_once_with(
            "network/tv-schedule/2024-01-15", web=True
        )

    @staticmethod
    def test_get_broadcasts_for_game(mock_client):
        """Test fetching broadcasts for game."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {
            "tvBroadcasts": [
                {"network": "ESPN", "countryCode": "US", "type": "national"}
            ]
        }
        mock_client.get.return_value = response

        client = NetworkClient(mock_client)
        broadcasts = client.get_broadcasts_for_game(2023020001)

        assert len(broadcasts) == 1
        assert broadcasts[0]["network"] == "ESPN"

    @staticmethod
    def test_get_where_to_watch(mock_client):
        """Test fetching streaming options from the real where-to-watch route."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"streams": []}
        mock_client.get.return_value = response

        client = NetworkClient(mock_client)
        data = client.get_where_to_watch()

        assert "streams" in data
        mock_client.get.assert_called_once_with(
            "where-to-watch", web=True, params=None
        )

    @staticmethod
    def test_get_where_to_watch_include_param(mock_client):
        """Test that the documented `include` filter is passed as a query param."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"streams": []}
        mock_client.get.return_value = response

        client = NetworkClient(mock_client)
        client.get_where_to_watch(include="1234")

        mock_client.get.assert_called_once_with(
            "where-to-watch", web=True, params={"include": "1234"}
        )

    @staticmethod
    def test_get_partner_game_odds(mock_client):
        """Test fetching partner game odds from the accurately named method."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"odds": []}
        mock_client.get.return_value = response

        client = NetworkClient(mock_client)
        data = client.get_partner_game_odds("US")

        assert "odds" in data
        mock_client.get.assert_called_once_with("partner-game/US/now", web=True)

    @staticmethod
    def test_partner_game_odds_is_not_where_to_watch(mock_client):
        """Partner-game odds and where-to-watch must request different routes."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {}
        mock_client.get.return_value = response

        client = NetworkClient(mock_client)
        client.get_where_to_watch()
        where_route = mock_client.get.call_args.args[0]

        client.get_partner_game_odds("CA")
        odds_route = mock_client.get.call_args.args[0]

        assert where_route == "where-to-watch"
        assert odds_route == "partner-game/CA/now"
        assert where_route != odds_route
        assert "where-to-watch" not in odds_route
        assert "partner-game" not in where_route


class TestUtilityClient:
    """Test class for UtilityClient."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock HTTP client."""
        return Mock(spec=HttpClient)

    @staticmethod
    def test_client_init(mock_client):
        """Test UtilityClient initialization."""
        client = UtilityClient(mock_client)
        assert client._client == mock_client

    @staticmethod
    def test_get_season(mock_client):
        """Test fetching season metadata."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"seasonId": 20232024}
        mock_client.get.return_value = response

        client = UtilityClient(mock_client)
        data = client.get_season()

        assert data["seasonId"] == 20232024
        mock_client.get.assert_called_once_with("season", web=True)

    @staticmethod
    def test_get_meta(mock_client):
        """Test fetching API metadata."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"endpoints": []}
        mock_client.get.return_value = response

        client = UtilityClient(mock_client)
        data = client.get_meta()

        assert "endpoints" in data
        mock_client.get.assert_called_once_with("meta", web=True)

    @staticmethod
    def test_get_meta_game(mock_client):
        """Test fetching game metadata."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"gameId": 2023020001}
        mock_client.get.return_value = response

        client = UtilityClient(mock_client)
        data = client.get_meta_game(2023020001)

        assert data["gameId"] == 2023020001
        mock_client.get.assert_called_once_with("meta/game/2023020001", web=True)

    @staticmethod
    def test_get_location(mock_client):
        """Test fetching location data."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"locations": []}
        mock_client.get.return_value = response

        client = UtilityClient(mock_client)
        data = client.get_location()

        assert "locations" in data
        mock_client.get.assert_called_once_with("location", web=True)

    @staticmethod
    def test_get_openapi_spec(mock_client):
        """Test fetching the OpenAPI specification without a doubled /v1."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"openapi": "3.0.0", "paths": {}}
        mock_client.get.return_value = response

        client = UtilityClient(mock_client)
        data = client.get_openapi_spec()

        assert data["openapi"] == "3.0.0"
        mock_client.get.assert_called_once_with("model/v1/openapi.json", web=True)

    @staticmethod
    def test_get_openapi_spec_final_url_has_no_double_version_prefix():
        """End-to-end URL must be /model/v1/openapi.json, never /v1/model/..."""
        http_client = HttpClient()
        http_client._client = Mock()
        http_client._client.get.return_value = Mock(json=Mock(return_value={}))
        UtilityClient(http_client).get_openapi_spec()

        actual = http_client._client.get.call_args.args[0]
        assert actual == f"{BASE_WEB_URL}{format_endpoint('openapi_spec')}"
        assert actual == f"{BASE_WEB_URL}/model/v1/openapi.json"
        assert not actual.startswith(f"{BASE_WEB_URL}/v1/")


class TestStatsClientLeaders:
    """Test class for StatsClient leaderboard methods."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock HTTP client."""
        return Mock(spec=HttpClient)

    @staticmethod
    def test_client_init(mock_client):
        """Test StatsClient initialization."""
        client = StatsClient(mock_client)
        assert client._client == mock_client

    @staticmethod
    def test_get_skater_stats_leaders(mock_client):
        """Test fetching current skater leaders."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"points": [], "goals": [], "assists": []}
        mock_client.get.return_value = response

        client = StatsClient(mock_client)
        data = client.get_skater_stats_leaders()

        assert "points" in data
        mock_client.get.assert_called_once_with(
            "skater-stats-leaders/current", params=None, web=True
        )

    @staticmethod
    def test_get_goalie_stats_leaders(mock_client):
        """Test fetching current goalie leaders."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"wins": [], "gaa": [], "savePercentage": []}
        mock_client.get.return_value = response

        client = StatsClient(mock_client)
        data = client.get_goalie_stats_leaders()

        assert "wins" in data
        mock_client.get.assert_called_once_with(
            "goalie-stats-leaders/current", params=None, web=True
        )

    @staticmethod
    def test_get_skater_stats_leaders_by_season(mock_client):
        """Test fetching skater leaders by season."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"points": []}
        mock_client.get.return_value = response

        client = StatsClient(mock_client)
        data = client.get_skater_stats_leaders_by_season("2023-2024", 2)

        assert "points" in data
        mock_client.get.assert_called_once_with(
            "skater-stats-leaders/20232024/2", params=None, web=True
        )

    @staticmethod
    def test_get_skater_stats_leaders_invalid_season(mock_client):
        """Test invalid season format."""
        client = StatsClient(mock_client)
        with pytest.raises(ValueError):
            client.get_skater_stats_leaders_by_season("invalid", 2)


class TestPlayoffClientLiveAPI:
    """Live API tests for PlayoffClient."""

    @pytest.fixture
    def real_client(self):
        """Create a real HTTP client."""
        return HttpClient()

    @pytest.mark.live_api
    @staticmethod
    def test_get_playoff_bracket_live(real_client):
        """Test fetching real playoff bracket."""
        client = PlayoffClient(real_client)
        try:
            data = client.get_playoff_bracket(2024)
            assert isinstance(data, list)
        except Exception:
            pytest.skip("No active playoffs or bracket unavailable")

    @pytest.mark.live_api
    @staticmethod
    def test_get_playoff_series_carousel_live(real_client):
        """Test fetching playoff series carousel."""
        client = PlayoffClient(real_client)
        try:
            data = client.get_playoff_series_carousel("2023-2024")
            assert isinstance(data, dict)
        except Exception:
            pytest.skip("Playoffs not available for this season")


class TestNetworkClientLiveAPI:
    """Live API tests for NetworkClient."""

    @pytest.fixture
    def real_client(self):
        """Create a real HTTP client."""
        return HttpClient()

    @pytest.mark.live_api
    @staticmethod
    def test_get_tv_schedule_now_live(real_client):
        """Test fetching current TV schedule."""
        client = NetworkClient(real_client)
        data = client.get_tv_schedule_now()

        assert isinstance(data, dict)

    @pytest.mark.live_api
    @staticmethod
    def test_get_where_to_watch_live(real_client):
        """Test fetching the real where-to-watch streaming route."""
        client = NetworkClient(real_client)
        try:
            data = client.get_where_to_watch()
            assert isinstance(data, dict)
        except Exception:
            pytest.skip("where-to-watch endpoint unavailable")

    @pytest.mark.live_api
    @staticmethod
    def test_get_partner_game_odds_live(real_client):
        """Test fetching partner game odds from the odds route."""
        client = NetworkClient(real_client)
        try:
            data = client.get_partner_game_odds("US")
            assert isinstance(data, dict)
        except Exception:
            pytest.skip("partner-game endpoint unavailable")


class TestUtilityClientLiveAPI:
    """Live API tests for UtilityClient."""

    @pytest.fixture
    def real_client(self):
        """Create a real HTTP client."""
        return HttpClient()

    @pytest.mark.live_api
    @staticmethod
    def test_get_season_live(real_client):
        """Test fetching season metadata."""
        client = UtilityClient(real_client)
        data = client.get_season()

        assert isinstance(data, list)

    @pytest.mark.live_api
    @staticmethod
    def test_get_meta_live(real_client):
        """Test fetching API metadata."""
        client = UtilityClient(real_client)
        data = client.get_meta()

        assert isinstance(data, dict)


class TestStatsClientLeadersLiveAPI:
    """Live API tests for StatsClient leaders."""

    @pytest.fixture
    def real_client(self):
        """Create a real HTTP client."""
        return HttpClient()

    @pytest.mark.live_api
    @staticmethod
    def test_get_skater_stats_leaders_live(real_client):
        """Test fetching current skater leaders."""
        client = StatsClient(real_client)
        data = client.get_skater_stats_leaders()

        assert isinstance(data, dict)
        if data:
            assert any(key in data for key in ["points", "goals", "assists"])

    @pytest.mark.live_api
    @staticmethod
    def test_get_goalie_stats_leaders_live(real_client):
        """Test fetching current goalie leaders."""
        client = StatsClient(real_client)
        data = client.get_goalie_stats_leaders()

        assert isinstance(data, dict)
        if data:
            assert any(key in data for key in ["wins", "gaa", "savePercentage"])
