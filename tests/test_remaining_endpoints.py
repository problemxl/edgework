"""Tests for remaining endpoints (Playoff, Network, Utility, Stats)."""

from datetime import datetime
from unittest.mock import Mock

import pytest

from edgework.clients.network_client import NetworkClient
from edgework.clients.playoff_client import PlayoffClient
from edgework.clients.stats_client import StatsClient
from edgework.clients.utility_client import UtilityClient
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

    def test_client_init(self, mock_client):
        """Test PlayoffClient initialization."""
        client = PlayoffClient(mock_client)
        assert client._client == mock_client

    def test_get_playoff_bracket(self, mock_client, mock_bracket_response):
        """Test fetching playoff bracket."""
        mock_client.get.return_value = mock_bracket_response
        client = PlayoffClient(mock_client)

        data = client.get_playoff_bracket(2024)

        assert data["seasonId"] == 20232024
        assert len(data["rounds"]) == 1
        mock_client.get.assert_called_once_with("playoff-bracket/2024", web=True)

    def test_get_playoff_series_carousel(self, mock_client, mock_carousel_response):
        """Test fetching playoff series carousel."""
        mock_client.get.return_value = mock_carousel_response
        client = PlayoffClient(mock_client)

        data = client.get_playoff_series_carousel("2023-2024")

        assert data["round"] == 1
        mock_client.get.assert_called_once_with(
            "playoff-series/carousel/20232024/", web=True
        )

    def test_get_playoff_series_schedule(self, mock_client):
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

    def test_get_series_winner(self, mock_client):
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

    def test_client_init(self, mock_client):
        """Test NetworkClient initialization."""
        client = NetworkClient(mock_client)
        assert client._client == mock_client

    def test_get_tv_schedule_now(self, mock_client, mock_tv_schedule_response):
        """Test fetching current TV schedule."""
        mock_client.get.return_value = mock_tv_schedule_response
        client = NetworkClient(mock_client)

        data = client.get_tv_schedule()

        assert data["date"] == "2024-01-15"
        mock_client.get.assert_called_once_with("network/tv-schedule/now", web=True)

    def test_get_tv_schedule_for_date(self, mock_client, mock_tv_schedule_response):
        """Test fetching TV schedule for specific date."""
        mock_client.get.return_value = mock_tv_schedule_response
        client = NetworkClient(mock_client)

        date = datetime(2024, 1, 15)
        data = client.get_tv_schedule_for_date(date)

        assert data["date"] == "2024-01-15"
        mock_client.get.assert_called_once_with(
            "network/tv-schedule/2024-01-15", web=True
        )

    def test_get_broadcasts_for_game(self, mock_client):
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

    def test_get_where_to_watch(self, mock_client):
        """Test fetching where to watch."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"broadcasts": []}
        mock_client.get.return_value = response

        client = NetworkClient(mock_client)
        data = client.get_where_to_watch("US")

        assert "broadcasts" in data
        mock_client.get.assert_called_once_with("partner-game/US/now", web=True)


class TestUtilityClient:
    """Test class for UtilityClient."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock HTTP client."""
        return Mock(spec=HttpClient)

    def test_client_init(self, mock_client):
        """Test UtilityClient initialization."""
        client = UtilityClient(mock_client)
        assert client._client == mock_client

    def test_get_season(self, mock_client):
        """Test fetching season metadata."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"seasonId": 20232024}
        mock_client.get.return_value = response

        client = UtilityClient(mock_client)
        data = client.get_season()

        assert data["seasonId"] == 20232024
        mock_client.get.assert_called_once_with("season", web=True)

    def test_get_meta(self, mock_client):
        """Test fetching API metadata."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"endpoints": []}
        mock_client.get.return_value = response

        client = UtilityClient(mock_client)
        data = client.get_meta()

        assert "endpoints" in data
        mock_client.get.assert_called_once_with("meta", web=True)

    def test_get_meta_game(self, mock_client):
        """Test fetching game metadata."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"gameId": 2023020001}
        mock_client.get.return_value = response

        client = UtilityClient(mock_client)
        data = client.get_meta_game(2023020001)

        assert data["gameId"] == 2023020001
        mock_client.get.assert_called_once_with("meta/game/2023020001", web=True)

    def test_get_location(self, mock_client):
        """Test fetching location data."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"locations": []}
        mock_client.get.return_value = response

        client = UtilityClient(mock_client)
        data = client.get_location()

        assert "locations" in data
        mock_client.get.assert_called_once_with("location", web=True)


class TestStatsClientLeaders:
    """Test class for StatsClient leaderboard methods."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock HTTP client."""
        return Mock(spec=HttpClient)

    def test_client_init(self, mock_client):
        """Test StatsClient initialization."""
        client = StatsClient(mock_client)
        assert client._client == mock_client

    def test_get_skater_stats_leaders(self, mock_client):
        """Test fetching current skater leaders."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"points": [], "goals": [], "assists": []}
        mock_client.get.return_value = response

        client = StatsClient(mock_client)
        data = client.get_skater_stats_leaders()

        assert "points" in data
        mock_client.get.assert_called_once_with(
            "skater-stats-leaders/current", web=True
        )

    def test_get_goalie_stats_leaders(self, mock_client):
        """Test fetching current goalie leaders."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"wins": [], "gaa": [], "savePercentage": []}
        mock_client.get.return_value = response

        client = StatsClient(mock_client)
        data = client.get_goalie_stats_leaders()

        assert "wins" in data
        mock_client.get.assert_called_once_with(
            "goalie-stats-leaders/current", web=True
        )

    def test_get_skater_stats_leaders_by_season(self, mock_client):
        """Test fetching skater leaders by season."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"points": []}
        mock_client.get.return_value = response

        client = StatsClient(mock_client)
        data = client.get_skater_stats_leaders_by_season("2023-2024", 2)

        assert "points" in data
        mock_client.get.assert_called_once_with(
            "skater-stats-leaders/20232024/2", web=True
        )

    def test_get_skater_stats_leaders_invalid_season(self, mock_client):
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
    def test_get_playoff_bracket_live(self, real_client):
        """Test fetching real playoff bracket."""
        client = PlayoffClient(real_client)
        try:
            data = client.get_playoff_bracket(2024)
            assert isinstance(data, list)
        except Exception:
            pytest.skip("No active playoffs or bracket unavailable")

    @pytest.mark.live_api
    def test_get_playoff_series_carousel_live(self, real_client):
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
    def test_get_tv_schedule_now_live(self, real_client):
        """Test fetching current TV schedule."""
        client = NetworkClient(real_client)
        data = client.get_tv_schedule_now()

        assert isinstance(data, dict)

    @pytest.mark.live_api
    def test_get_where_to_watch_live(self, real_client):
        """Test fetching where to watch."""
        client = NetworkClient(real_client)
        data = client.get_where_to_watch("US")

        assert isinstance(data, dict)


class TestUtilityClientLiveAPI:
    """Live API tests for UtilityClient."""

    @pytest.fixture
    def real_client(self):
        """Create a real HTTP client."""
        return HttpClient()

    @pytest.mark.live_api
    def test_get_season_live(self, real_client):
        """Test fetching season metadata."""
        client = UtilityClient(real_client)
        data = client.get_season()

        assert isinstance(data, list)

    @pytest.mark.live_api
    def test_get_meta_live(self, real_client):
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
    def test_get_skater_stats_leaders_live(self, real_client):
        """Test fetching current skater leaders."""
        client = StatsClient(real_client)
        data = client.get_skater_stats_leaders()

        assert isinstance(data, dict)
        if data:
            assert any(key in data for key in ["points", "goals", "assists"])

    @pytest.mark.live_api
    def test_get_goalie_stats_leaders_live(self, real_client):
        """Test fetching current goalie leaders."""
        client = StatsClient(real_client)
        data = client.get_goalie_stats_leaders()

        assert isinstance(data, dict)
        if data:
            assert any(key in data for key in ["wins", "gaa", "savePercentage"])
