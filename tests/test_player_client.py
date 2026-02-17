"""Tests for the player client module."""

from datetime import datetime
from unittest.mock import Mock

import pytest

from edgework.clients.player_client import PlayerClient, api_to_dict, landing_to_dict
from edgework.http_client import HttpClient
from edgework.models.player import Player


class TestApiToDict:
    """Test api_to_dict conversion function."""

    def test_api_to_dict_basic(self):
        """Test basic player data conversion."""
        data = {
            "playerId": "8478402",
            "name": "Connor McDavid",
            "sweaterNumber": 97,
            "positionCode": "C",
            "active": True,
            "teamId": "22",
            "teamAbbrev": "EDM",
        }
        result = api_to_dict(data)

        assert result["player_id"] == 8478402
        assert result["first_name"] == "Connor"
        assert result["last_name"] == "McDavid"
        assert result["sweater_number"] == 97
        assert result["position"] == "C"
        assert result["is_active"] is True
        assert result["current_team_id"] == 22
        assert result["current_team_abbr"] == "EDM"

    def test_api_to_dict_single_name(self):
        """Test player with single name."""
        data = {"playerId": "123", "name": "Mario"}
        result = api_to_dict(data)

        assert result["first_name"] == "Mario"
        assert result["last_name"] == ""

    def test_api_to_dict_no_name(self):
        """Test player with no name."""
        data = {"playerId": "456"}
        result = api_to_dict(data)

        assert result["first_name"] == ""
        assert result["last_name"] == ""


class TestLandingToDict:
    """Test landing_to_dict conversion function."""

    def test_landing_to_dict_basic(self):
        """Test basic landing data conversion."""
        data = {
            "firstName": {"default": "Connor"},
            "lastName": {"default": "McDavid"},
            "birthDate": "1997-01-13",
            "height": "6' 1\"",
            "weight": 193,
        }
        result = landing_to_dict(data)

        assert result["first_name"] == "Connor"
        assert result["last_name"] == "McDavid"
        assert isinstance(result["birth_date"], datetime)
        assert result["height"] == "6' 1\""
        assert result["weight"] == 193

    def test_landing_to_dict_draft_details(self):
        """Test draft details processing."""
        data = {
            "draftDetails": {
                "year": 2015,
                "round": 1,
                "overallPick": 1,
                "teamAbbrev": "EDM",
            }
        }
        result = landing_to_dict(data)

        assert isinstance(result["draft_year"], datetime)
        assert result["draft_round"] == 1
        assert result["draft_overall_pick"] == 1
        assert result["draft_team_abbrev"] == "EDM"


class TestPlayerClient:
    """Test class for PlayerClient."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock HTTP client."""
        return Mock(spec=HttpClient)

    @pytest.fixture
    def mock_player_search_response(self):
        """Create a mock player search response."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = [
            {
                "playerId": "8478402",
                "name": "Connor McDavid",
                "sweaterNumber": 97,
                "positionCode": "C",
                "active": True,
                "teamId": "22",
                "teamAbbrev": "EDM",
            },
            {
                "playerId": "8477934",
                "name": "Leon Draisaitl",
                "sweaterNumber": 29,
                "positionCode": "C",
                "active": True,
                "teamId": "22",
                "teamAbbrev": "EDM",
            },
        ]
        return response

    @pytest.fixture
    def mock_player_landing_response(self):
        """Create a mock player landing response."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {
            "firstName": {"default": "Connor"},
            "lastName": {"default": "McDavid"},
            "birthDate": "1997-01-13",
            "position": "C",
            "sweaterNumber": 97,
            "teamId": 22,
            "teamAbbrev": "EDM",
        }
        return response

    @pytest.fixture
    def mock_game_log_response(self):
        """Create a mock game log response."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {
            "seasonId": 20232024,
            "gameTypeId": 2,
            "playerStats": [{"gameId": 2023020001, "goals": 2, "assists": 1}],
        }
        return response

    @pytest.fixture
    def mock_spotlight_response(self):
        """Create a mock spotlight response."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = [
            {"playerId": 8478402, "name": "Connor McDavid"},
            {"playerId": 8477934, "name": "Leon Draisaitl"},
        ]
        return response

    def test_client_init(self, mock_client):
        """Test PlayerClient initialization."""
        client = PlayerClient(mock_client)
        assert client.client == mock_client

    def test_get_all_players(self, mock_client, mock_player_search_response):
        """Test fetching all players."""
        mock_client.get_raw.return_value = mock_player_search_response
        client = PlayerClient(mock_client)

        players = client.get_all_players()

        assert len(players) == 2
        assert players[0].obj_id == 8478402
        assert players[1].obj_id == 8477934

    def test_get_active_players(self, mock_client, mock_player_search_response):
        """Test fetching active players."""
        mock_client.get_raw.return_value = mock_player_search_response
        client = PlayerClient(mock_client)

        players = client.get_active_players()

        assert len(players) == 2

    def test_get_player_landing(self, mock_client, mock_player_landing_response):
        """Test fetching player landing data."""
        mock_client.get.return_value = mock_player_landing_response
        client = PlayerClient(mock_client)

        data = client.get_player_landing(8478402)

        assert data["first_name"] == "Connor"
        assert data["last_name"] == "McDavid"
        assert data["player_id"] == 8478402
        mock_client.get.assert_called_once_with("player/8478402/landing", web=True)

    def test_get_player(self, mock_client, mock_player_landing_response):
        """Test fetching player by ID."""
        mock_client.get.return_value = mock_player_landing_response
        client = PlayerClient(mock_client)

        player = client.get_player(8478402)

        assert isinstance(player, Player)
        assert player._data["first_name"] == "Connor"

    def test_get_player_game_logs(self, mock_client, mock_game_log_response):
        """Test fetching player game logs."""
        mock_client.get.return_value = mock_game_log_response
        client = PlayerClient(mock_client)

        data = client.get_player_game_logs(8478402, "2023-2024")

        assert data["seasonId"] == 20232024
        assert data["gameTypeId"] == 2
        mock_client.get.assert_called_once_with(
            "player/8478402/game-log/20232024/2", web=True
        )

    def test_get_player_game_logs_invalid_season(self, mock_client):
        """Test game logs with invalid season format."""
        client = PlayerClient(mock_client)

        with pytest.raises(ValueError):
            client.get_player_game_logs(8478402, "invalid")

    def test_get_player_game_log_now(self, mock_client, mock_game_log_response):
        """Test fetching current season game logs."""
        mock_client.get.return_value = mock_game_log_response
        client = PlayerClient(mock_client)

        data = client.get_player_game_log_now(8478402)

        assert data["gameTypeId"] == 2
        mock_client.get.assert_called_once_with("player/8478402/game-log/now", web=True)

    def test_get_player_spotlight(self, mock_client, mock_spotlight_response):
        """Test fetching player spotlight."""
        mock_client.get.return_value = mock_spotlight_response
        client = PlayerClient(mock_client)

        data = client.get_player_spotlight()

        assert len(data) == 2
        mock_client.get.assert_called_once_with("player-spotlight", web=True)

    def test_get_player_by_id(self, mock_client, mock_player_landing_response):
        """Test getting player by ID with error handling."""
        mock_client.get.return_value = mock_player_landing_response
        client = PlayerClient(mock_client)

        player = client.get_player_by_id(8478402)
        assert player is not None

        # Test with error
        mock_client.get.side_effect = Exception("Not found")
        player = client.get_player_by_id(999)
        assert player is None


class TestPlayerClientLiveAPI:
    """Live API tests for PlayerClient."""

    @pytest.fixture
    def real_client(self):
        """Create a real HTTP client."""
        return HttpClient()

    @pytest.mark.live_api
    def test_get_player_landing_live(self, real_client):
        """Test fetching real player landing data."""
        client = PlayerClient(real_client)
        data = client.get_player_landing(8478402)

        assert data["first_name"] == "Connor"
        assert data["last_name"] == "McDavid"
        assert "position" in data

    @pytest.mark.live_api
    def test_get_player_game_logs_live(self, real_client):
        """Test fetching real player game logs."""
        client = PlayerClient(real_client)
        data = client.get_player_game_logs(8478402, "2023-2024")

        assert "seasonId" in data
        assert "gameLog" in data

    @pytest.mark.live_api
    def test_get_player_game_log_now_live(self, real_client):
        """Test fetching current season game logs."""
        client = PlayerClient(real_client)
        data = client.get_player_game_log_now(8478402)

        assert "seasonId" in data
        assert "gameLog" in data

    @pytest.mark.live_api
    def test_get_player_spotlight_live(self, real_client):
        """Test fetching player spotlight."""
        client = PlayerClient(real_client)
        data = client.get_player_spotlight()

        assert isinstance(data, list)
        if data:
            assert "playerId" in data[0] or "player_id" in data[0]
