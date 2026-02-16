"""Tests for the game client module."""

from datetime import datetime
from unittest.mock import Mock

import pytest

from edgework.clients.game_client import GameClient
from edgework.http_client import HttpClient
from edgework.models.game import Game
from edgework.models.play_by_play import PlayByPlay


class TestGameClient:
    """Test class for GameClient."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock HTTP client."""
        return Mock(spec=HttpClient)

    @pytest.fixture
    def mock_game_response(self):
        """Create a mock game boxscore response."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {
            "id": 2023020001,
            "gameDate": "2023-10-10",
            "startTimeUTC": "2023-10-10T23:00:00Z",
            "gameState": "OFF",
            "awayTeam": {
                "id": 1,
                "abbrev": "NJD",
                "score": 3,
            },
            "homeTeam": {
                "id": 2,
                "abbrev": "NYR",
                "score": 4,
            },
            "season": 20232024,
            "venue": {"default": "Madison Square Garden"},
        }
        return response

    @pytest.fixture
    def mock_landing_response(self):
        """Create a mock game landing response."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {
            "id": 2023020001,
            "gameDate": "2023-10-10",
            "gameState": "OFF",
            "awayTeam": {"id": 1, "abbrev": "NJD", "score": 3},
            "homeTeam": {"id": 2, "abbrev": "NYR", "score": 4},
            "summary": {"goals": []},
        }
        return response

    @pytest.fixture
    def mock_score_response(self):
        """Create a mock score response."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {
            "games": [
                {
                    "id": 2023020001,
                    "awayTeam": {"abbrev": "NJD"},
                    "homeTeam": {"abbrev": "NYR"},
                },
            ]
        }
        return response

    @pytest.fixture
    def mock_schedule_response(self):
        """Create a mock schedule response."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {
            "gameWeek": [
                {
                    "date": "2023-10-10",
                    "games": [
                        {
                            "id": 2023020001,
                            "awayTeam": {"abbrev": "NJD"},
                            "homeTeam": {"abbrev": "NYR"},
                        },
                    ],
                }
            ]
        }
        return response

    def test_client_init(self, mock_client):
        """Test GameClient initialization."""
        client = GameClient(mock_client)
        assert client._client == mock_client

    def test_get_game(self, mock_client, mock_game_response):
        """Test fetching a game boxscore."""
        mock_client.get.return_value = mock_game_response
        client = GameClient(mock_client)

        game = client.get_game(2023020001)

        assert isinstance(game, Game)
        assert game._data["game_id"] == 2023020001
        assert game._data["away_team_abbrev"] == "NJD"
        assert game._data["home_team_abbrev"] == "NYR"
        mock_client.get.assert_called_once_with(
            "gamecenter/2023020001/boxscore", web=True
        )

    def test_get_play_by_play(self, mock_client):
        """Test fetching play-by-play data."""
        pbp_response = Mock()
        pbp_response.status_code = 200
        pbp_response.json.return_value = {
            "id": 2023020001,
            "plays": [],
            "awayTeam": {"id": 1, "abbrev": "NJD"},
            "homeTeam": {"id": 2, "abbrev": "NYR"},
        }
        mock_client.get.return_value = pbp_response

        client = GameClient(mock_client)
        pbp = client.get_play_by_play(2023020001)

        assert isinstance(pbp, PlayByPlay)

    def test_get_game_landing(self, mock_client, mock_landing_response):
        """Test fetching game landing data."""
        mock_client.get.return_value = mock_landing_response
        client = GameClient(mock_client)

        data = client.get_game_landing(2023020001)

        assert data["id"] == 2023020001
        assert data["awayTeam"]["abbrev"] == "NJD"
        mock_client.get.assert_called_once_with(
            "gamecenter/2023020001/landing", web=True
        )

    def test_get_game_boxscore(self, mock_client, mock_game_response):
        """Test fetching game boxscore as dictionary."""
        mock_client.get.return_value = mock_game_response
        client = GameClient(mock_client)

        data = client.get_game_boxscore(2023020001)

        assert data["id"] == 2023020001
        assert data["awayTeam"]["abbrev"] == "NJD"

    def test_get_game_story(self, mock_client):
        """Test fetching game story."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"summary": "Game story content"}
        mock_client.get.return_value = response

        client = GameClient(mock_client)
        data = client.get_game_story(2023020001)

        assert data["summary"] == "Game story content"
        mock_client.get.assert_called_once_with("wsc/game-story/2023020001", web=True)

    def test_get_game_right_rail(self, mock_client):
        """Test fetching game right rail data."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"highlights": []}
        mock_client.get.return_value = response

        client = GameClient(mock_client)
        data = client.get_game_right_rail(2023020001)

        assert data["highlights"] == []
        mock_client.get.assert_called_once_with(
            "gamecenter/2023020001/right-rail", web=True
        )

    def test_get_score_current(self, mock_client, mock_score_response):
        """Test fetching current scores."""
        mock_client.get.return_value = mock_score_response
        client = GameClient(mock_client)

        data = client.get_score()

        assert "games" in data
        mock_client.get.assert_called_once_with("score/now", web=True)

    def test_get_score_for_date(self, mock_client, mock_score_response):
        """Test fetching scores for specific date."""
        mock_client.get.return_value = mock_score_response
        client = GameClient(mock_client)

        date = datetime(2023, 10, 10)
        data = client.get_score(date)

        assert "games" in data
        mock_client.get.assert_called_once_with("score/2023-10-10", web=True)

    def test_get_score_for_date_string(self, mock_client, mock_score_response):
        """Test fetching scores for date as string."""
        mock_client.get.return_value = mock_score_response
        client = GameClient(mock_client)

        data = client.get_score("2023-10-10")

        assert "games" in data
        mock_client.get.assert_called_once_with("score/2023-10-10", web=True)

    def test_get_scoreboard(self, mock_client):
        """Test fetching scoreboard."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"scoreboard": []}
        mock_client.get.return_value = response

        client = GameClient(mock_client)
        data = client.get_scoreboard()

        assert data["scoreboard"] == []
        mock_client.get.assert_called_once_with("scoreboard/now", web=True)

    def test_get_where_to_watch(self, mock_client):
        """Test fetching where to watch."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"broadcasts": []}
        mock_client.get.return_value = response

        client = GameClient(mock_client)
        data = client.get_where_to_watch("US")

        assert data["broadcasts"] == []
        mock_client.get.assert_called_once_with("partner-game/US/now", web=True)

    def test_get_where_to_watch_default(self, mock_client):
        """Test fetching where to watch with default country."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"broadcasts": []}
        mock_client.get.return_value = response

        client = GameClient(mock_client)
        client.get_where_to_watch()

        mock_client.get.assert_called_once_with("partner-game/US/now", web=True)


class TestGameClientLiveAPI:
    """Live API tests for GameClient."""

    @pytest.fixture
    def real_client(self):
        """Create a real HTTP client."""
        return HttpClient()

    @pytest.mark.live_api
    def test_get_game_live(self, real_client):
        """Test fetching a real game."""
        client = GameClient(real_client)
        # Use a game from recent season (2024-25 season opener)
        game = client.get_game(2024020001)

        assert game._data["game_id"] == 2024020001
        assert "game_date" in game._data

    @pytest.mark.live_api
    def test_get_play_by_play_live(self, real_client):
        """Test fetching real play-by-play data."""
        client = GameClient(real_client)
        pbp = client.get_play_by_play(2024020001)

        assert isinstance(pbp, PlayByPlay)
        assert pbp._data.get("id") == 2024020001

    @pytest.mark.live_api
    def test_get_game_landing_live(self, real_client):
        """Test fetching real game landing data."""
        client = GameClient(real_client)
        data = client.get_game_landing(2024020001)

        assert data["id"] == 2024020001
        assert "awayTeam" in data
        assert "homeTeam" in data

    @pytest.mark.live_api
    def test_get_score_current_live(self, real_client):
        """Test fetching current scores."""
        client = GameClient(real_client)
        data = client.get_score()

        assert "games" in data or "gameWeek" in data

    @pytest.mark.live_api
    def test_get_scoreboard_live(self, real_client):
        """Test fetching current scoreboard."""
        client = GameClient(real_client)
        data = client.get_scoreboard()

        # Should return scoreboard data
        assert isinstance(data, dict)

    @pytest.mark.live_api
    def test_get_current_games(self, real_client):
        """Test fetching current games."""
        client = GameClient(real_client)
        games = client.get_current_games()

        # Returns list (may be empty if no games scheduled)
        assert isinstance(games, list)
