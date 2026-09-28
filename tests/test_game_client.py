"""Tests for the game client module."""

from datetime import datetime
from unittest.mock import Mock

import pytest

from edgework.clients.game_client import GameClient
from edgework.clients.shift_client import ShiftClient
from edgework.const import BASE_WEB_URL
from edgework.endpoints import API_PATH, format_endpoint
from edgework.http_client import HttpClient
from edgework.models.game import Game
from edgework.models.play_by_play import PlayByPlay
from edgework.models.shift import Shift


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

    @staticmethod
    def test_client_init(mock_client):
        """Test GameClient initialization."""
        client = GameClient(mock_client)
        assert client._client == mock_client

    @staticmethod
    def test_get_game(mock_client, mock_game_response):
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

    @staticmethod
    def test_get_play_by_play(mock_client):
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

    @staticmethod
    def test_get_game_landing(mock_client, mock_landing_response):
        """Test fetching game landing data."""
        mock_client.get.return_value = mock_landing_response
        client = GameClient(mock_client)

        data = client.get_game_landing(2023020001)

        assert data["id"] == 2023020001
        assert data["awayTeam"]["abbrev"] == "NJD"
        mock_client.get.assert_called_once_with(
            "gamecenter/2023020001/landing", web=True
        )

    @staticmethod
    def test_get_game_boxscore(mock_client, mock_game_response):
        """Test fetching game boxscore as dictionary."""
        mock_client.get.return_value = mock_game_response
        client = GameClient(mock_client)

        data = client.get_game_boxscore(2023020001)

        assert data["id"] == 2023020001
        assert data["awayTeam"]["abbrev"] == "NJD"

    @staticmethod
    def test_get_game_story(mock_client):
        """Test fetching game story."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"summary": "Game story content"}
        mock_client.get.return_value = response

        client = GameClient(mock_client)
        data = client.get_game_story(2023020001)

        assert data["summary"] == "Game story content"
        mock_client.get.assert_called_once_with("wsc/game-story/2023020001", web=True)

    @staticmethod
    def test_get_game_right_rail(mock_client):
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

    @staticmethod
    def test_get_score_current(mock_client, mock_score_response):
        """Test fetching current scores."""
        mock_client.get.return_value = mock_score_response
        client = GameClient(mock_client)

        data = client.get_score()

        assert "games" in data
        mock_client.get.assert_called_once_with("score/now", web=True)

    @staticmethod
    def test_get_score_for_date(mock_client, mock_score_response):
        """Test fetching scores for specific date."""
        mock_client.get.return_value = mock_score_response
        client = GameClient(mock_client)

        date = datetime(2023, 10, 10)
        data = client.get_score(date)

        assert "games" in data
        mock_client.get.assert_called_once_with("score/2023-10-10", web=True)

    @staticmethod
    def test_get_score_for_date_string(mock_client, mock_score_response):
        """Test fetching scores for date as string."""
        mock_client.get.return_value = mock_score_response
        client = GameClient(mock_client)

        data = client.get_score("2023-10-10")

        assert "games" in data
        mock_client.get.assert_called_once_with("score/2023-10-10", web=True)

    @staticmethod
    def test_get_scoreboard(mock_client):
        """Test fetching scoreboard."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"scoreboard": []}
        mock_client.get.return_value = response

        client = GameClient(mock_client)
        data = client.get_scoreboard()

        assert data["scoreboard"] == []
        mock_client.get.assert_called_once_with("scoreboard/now", web=True)

    @staticmethod
    def test_get_where_to_watch(mock_client):
        """Test fetching where to watch."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"broadcasts": []}
        mock_client.get.return_value = response

        client = GameClient(mock_client)
        data = client.get_where_to_watch("US")

        assert data["broadcasts"] == []
        mock_client.get.assert_called_once_with("partner-game/US/now", web=True)

    @staticmethod
    def test_get_where_to_watch_default(mock_client):
        """Test fetching where to watch with default country."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"broadcasts": []}
        mock_client.get.return_value = response

        client = GameClient(mock_client)
        client.get_where_to_watch()

        mock_client.get.assert_called_once_with("partner-game/US/now", web=True)


class TestGameReplayRoutes:
    """Mocked tests for ppt-replay and WSC routes (Task 3)."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock HTTP client."""
        return Mock(spec=HttpClient)

    @staticmethod
    def _response(payload):
        """Build a mock HTTP response with the given JSON payload."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = payload
        return response

    def test_get_goal_replay_route(self, mock_client):
        """get_goal_replay must request /ppt-replay/goal/{game-id}/{event-number}."""
        payload = {"mediaPlaybackId": "abc123"}
        mock_client.get.return_value = self._response(payload)

        client = GameClient(mock_client)
        data = client.get_goal_replay(2023020204, 12)

        assert data == payload
        mock_client.get.assert_called_once_with(
            "ppt-replay/goal/2023020204/12", web=True
        )

    def test_get_goal_replay_final_url_matches_registry(self):
        """Final URL must equal the documented goal_replay registry route."""
        http_client = HttpClient()
        http_client._client = Mock()
        http_client._client.get.return_value = self._response({})

        GameClient(http_client).get_goal_replay(2023020204, 12)

        expected = f"{BASE_WEB_URL}{format_endpoint('goal_replay', game_id=2023020204, event_number=12)}"
        actual = http_client._client.get.call_args.args[0]
        assert actual == expected == f"{BASE_WEB_URL}/v1/ppt-replay/goal/2023020204/12"

    def test_get_play_replay_route(self, mock_client):
        """get_play_replay must request /ppt-replay/{game-id}/{event-number}."""
        payload = {"mediaPlaybackId": "def456"}
        mock_client.get.return_value = self._response(payload)

        client = GameClient(mock_client)
        data = client.get_play_replay(2023020204, 12)

        assert data == payload
        mock_client.get.assert_called_once_with("ppt-replay/2023020204/12", web=True)

    def test_get_play_replay_final_url_matches_registry(self):
        """Final URL must equal the documented play_replay registry route."""
        http_client = HttpClient()
        http_client._client = Mock()
        http_client._client.get.return_value = self._response({})

        GameClient(http_client).get_play_replay(2023020204, 12)

        expected = f"{BASE_WEB_URL}{format_endpoint('play_replay', game_id=2023020204, event_number=12)}"
        actual = http_client._client.get.call_args.args[0]
        assert actual == expected == f"{BASE_WEB_URL}/v1/ppt-replay/2023020204/12"

    def test_goal_replay_and_play_replay_are_distinct_routes(self, mock_client):
        """Goal replays use the /ppt-replay/goal/ prefix, play replays do not."""
        mock_client.get.return_value = self._response({})

        client = GameClient(mock_client)
        client.get_goal_replay(2023020204, 12)
        goal_route = mock_client.get.call_args.args[0]

        client.get_play_replay(2023020204, 12)
        play_route = mock_client.get.call_args.args[0]

        assert goal_route != play_route
        assert goal_route.startswith("ppt-replay/goal/")
        assert play_route.startswith("ppt-replay/2023020204")

    def test_get_wsc_play_by_play_route(self, mock_client):
        """get_wsc_play_by_play must request /wsc/play-by-play/{game-id}."""
        payload = {"plays": []}
        mock_client.get.return_value = self._response(payload)

        client = GameClient(mock_client)
        data = client.get_wsc_play_by_play(2023020204)

        assert data == payload
        mock_client.get.assert_called_once_with("wsc/play-by-play/2023020204", web=True)

    def test_get_wsc_play_by_play_final_url_matches_registry(self):
        """Final URL must equal the documented wsc_play_by_play registry route."""
        http_client = HttpClient()
        http_client._client = Mock()
        http_client._client.get.return_value = self._response({})

        GameClient(http_client).get_wsc_play_by_play(2023020204)

        expected = (
            f"{BASE_WEB_URL}"
            f"{format_endpoint('wsc_play_by_play', game_id=2023020204)}"
        )
        actual = http_client._client.get.call_args.args[0]
        assert actual == expected == f"{BASE_WEB_URL}/v1/wsc/play-by-play/2023020204"

    def test_wsc_play_by_play_is_distinct_from_gamecenter_route(self, mock_client):
        """The WSC route must differ from the gamecenter play-by-play route."""
        mock_client.get.return_value = self._response({"plays": []})

        client = GameClient(mock_client)
        client.get_play_by_play(2023020204)
        gamecenter_route = mock_client.get.call_args.args[0]

        client.get_wsc_play_by_play(2023020204)
        wsc_route = mock_client.get.call_args.args[0]

        assert gamecenter_route == "gamecenter/2023020204/play-by-play"
        assert wsc_route == "wsc/play-by-play/2023020204"
        assert gamecenter_route != wsc_route


class TestGameClientPartnerGame:
    """Mocked tests for the partner-game vs. where-to-watch distinction."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock HTTP client."""
        return Mock(spec=HttpClient)

    @staticmethod
    def _response(payload):
        """Build a mock HTTP response with the given JSON payload."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = payload
        return response

    def test_get_partner_game_odds_route(self, mock_client):
        """get_partner_game_odds must request /partner-game/{cc}/now."""
        payload = {"odds": []}
        mock_client.get.return_value = self._response(payload)

        client = GameClient(mock_client)
        data = client.get_partner_game_odds("CA")

        assert data == payload
        mock_client.get.assert_called_once_with("partner-game/CA/now", web=True)

    def test_get_partner_game_odds_default_country(self, mock_client):
        """get_partner_game_odds defaults to the US country code."""
        mock_client.get.return_value = self._response({})

        GameClient(mock_client).get_partner_game_odds()

        mock_client.get.assert_called_once_with("partner-game/US/now", web=True)

    def test_get_where_to_watch_alias_still_hits_partner_game(self, mock_client):
        """The deprecated alias keeps its historical partner-game request."""
        payload = {"odds": []}
        mock_client.get.return_value = self._response(payload)

        client = GameClient(mock_client)
        with pytest.warns(DeprecationWarning):
            data = client.get_where_to_watch("SE")

        assert data == payload
        mock_client.get.assert_called_once_with("partner-game/SE/now", web=True)

    def test_game_client_where_to_watch_never_requests_the_real_route(
        self, mock_client
    ):
        """GameClient.get_where_to_watch must not request /where-to-watch."""
        mock_client.get.return_value = self._response({})

        client = GameClient(mock_client)
        with pytest.warns(DeprecationWarning):
            client.get_where_to_watch()

        requested = mock_client.get.call_args.args[0]
        documented = API_PATH["where_to_watch"]  # /{API_VERSION}/where-to-watch

        assert requested == "partner-game/US/now"
        assert "where-to-watch" not in requested
        assert documented == "/{API_VERSION}/where-to-watch"


class TestGameClientShiftDelegation:
    """GameClient shift methods must delegate to the canonical ShiftClient."""

    @staticmethod
    def test_get_shifts_delegates_to_shift_client():
        """get_shifts issues the canonical shiftcharts request."""
        http_client = Mock(spec=HttpClient)
        http_client.get.return_value = Mock(
            json=Mock(
                return_value={"data": [{"playerId": 8478402, "period": 1}]}
            )
        )

        client = GameClient(http_client)
        shifts = client.get_shifts(2021020001)

        http_client.get.assert_called_once_with(
            "shiftcharts",
            params={"cayenneExp": "gameId=2021020001"},
            lang="en",
        )
        assert len(shifts) == 1
        assert isinstance(shifts[0], Shift)
        assert shifts[0].player_id == 8478402

    @staticmethod
    def test_get_shifts_request_identical_to_shift_client():
        """GameClient and ShiftClient must construct byte-identical requests."""
        game_http = Mock(spec=HttpClient)
        game_http.get.return_value = Mock(json=Mock(return_value={"data": []}))
        shift_http = Mock(spec=HttpClient)
        shift_http.get.return_value = Mock(json=Mock(return_value={"data": []}))

        GameClient(game_http).get_shifts(2021020001)
        ShiftClient(shift_http).get_shifts(2021020001)

        assert game_http.get.call_args == shift_http.get.call_args


class TestGameClientLiveAPI:
    """Live API tests for GameClient."""

    @pytest.fixture
    def real_client(self):
        """Create a real HTTP client."""
        return HttpClient()

    @pytest.mark.live_api
    @staticmethod
    def test_get_game_live(real_client):
        """Test fetching a real game."""
        client = GameClient(real_client)
        # Use a game from recent season (2024-25 season opener)
        game = client.get_game(2024020001)

        assert game._data["game_id"] == 2024020001
        assert "game_date" in game._data

    @pytest.mark.live_api
    @staticmethod
    def test_get_play_by_play_live(real_client):
        """Test fetching real play-by-play data."""
        client = GameClient(real_client)
        pbp = client.get_play_by_play(2024020001)

        assert isinstance(pbp, PlayByPlay)
        assert pbp._data.get("game_id") == 2024020001

    @pytest.mark.live_api
    @staticmethod
    def test_get_game_landing_live(real_client):
        """Test fetching real game landing data."""
        client = GameClient(real_client)
        data = client.get_game_landing(2024020001)

        assert data["id"] == 2024020001
        assert "awayTeam" in data
        assert "homeTeam" in data

    @pytest.mark.live_api
    @staticmethod
    def test_get_score_current_live(real_client):
        """Test fetching current scores."""
        client = GameClient(real_client)
        data = client.get_score()

        assert "games" in data or "gameWeek" in data

    @pytest.mark.live_api
    @staticmethod
    def test_get_scoreboard_live(real_client):
        """Test fetching current scoreboard."""
        client = GameClient(real_client)
        data = client.get_scoreboard()

        # Should return scoreboard data
        assert isinstance(data, dict)

    @pytest.mark.live_api
    @staticmethod
    def test_get_current_games(real_client):
        """Test fetching current games."""
        client = GameClient(real_client)
        games = client.get_current_games()

        # Returns list (may be empty if no games scheduled)
        assert isinstance(games, list)
