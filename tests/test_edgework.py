"""
Pytest tests for the main Edgework client class.
This file tests all methods and functionality of the Edgework class.
"""

from unittest.mock import Mock, patch

import pytest

from edgework.clients.draft_client import DraftClient
from edgework.clients.game_client import GameClient
from edgework.clients.network_client import NetworkClient
from edgework.clients.player_client import PlayerClient
from edgework.clients.playoff_client import PlayoffClient
from edgework.clients.schedule_client import ScheduleClient
from edgework.clients.standings_client import StandingClient
from edgework.clients.stats_client import StatsClient
from edgework.clients.team_client import TeamClient
from edgework.clients.utility_client import UtilityClient
from edgework.edgework import Edgework, _validate_season_format
from edgework.models.player import Player
from edgework.models.stats import GoalieStats, SkaterStats, TeamStats
from edgework.models.team import Roster, Team


def _make_player(player_id=8478402, last_name="McDavid"):
    """Build a Player populated with data, as the player client would."""
    return Player(
        player_id=player_id,
        first_name="Connor",
        last_name="McDavid",
        position="C",
        is_active=True,
    )


class TestEdgeworkInitialization:
    """Test class for Edgework initialization."""

    @patch("edgework.edgework.PlayerClient")
    @patch("edgework.edgework.HttpClient")
    def test_init_default_user_agent(self, mock_http_client, mock_player_client):
        """Test Edgework initialization with default user agent."""
        mock_client_instance = Mock()
        mock_http_client.return_value = mock_client_instance

        edgework = Edgework()

        # Verify HTTP client was created with default user agent
        mock_http_client.assert_called_once_with(user_agent="EdgeworkClient/2.0")

        # Verify player client was initialized with the HTTP client
        mock_player_client.assert_called_once_with(http_client=mock_client_instance)

        # Verify stats models were initialized
        assert isinstance(edgework._skaters, SkaterStats)
        assert isinstance(edgework._goalies, GoalieStats)
        assert isinstance(edgework._team_stats, TeamStats)

    @patch("edgework.edgework.PlayerClient")
    @patch("edgework.edgework.HttpClient")
    def test_init_custom_user_agent(self, mock_http_client, mock_player_client):
        """Test Edgework initialization with custom user agent."""
        custom_user_agent = "MyCustomAgent/2.0"
        mock_client_instance = Mock()
        mock_http_client.return_value = mock_client_instance

        edgework = Edgework(user_agent=custom_user_agent)

        # Verify HTTP client was created with custom user agent
        mock_http_client.assert_called_once_with(user_agent=custom_user_agent)

    @patch("edgework.edgework.PlayerClient")
    @patch("edgework.edgework.HttpClient")
    def test_init_exposes_all_clients(self, mock_http_client, mock_player_client):
        """Test that the facade exposes every dedicated client."""
        mock_client_instance = Mock()
        mock_http_client.return_value = mock_client_instance

        edgework = Edgework()

        # PlayerClient is patched in this test; verify it received the HTTP client
        assert edgework.players is mock_player_client.return_value

        assert isinstance(edgework.teams, TeamClient)
        assert isinstance(edgework.schedule, ScheduleClient)
        assert isinstance(edgework.games, GameClient)
        assert isinstance(edgework.standings, StandingClient)
        assert isinstance(edgework.draft, DraftClient)
        assert isinstance(edgework.stats, StatsClient)
        assert isinstance(edgework.playoffs, PlayoffClient)
        assert isinstance(edgework.network, NetworkClient)
        assert isinstance(edgework.utility, UtilityClient)

    @patch("edgework.edgework.PlayerClient")
    @patch("edgework.edgework.HttpClient")
    def test_init_creates_stats_models_with_client(
        self, mock_http_client, mock_player_client
    ):
        """Test that stats models are initialized with the HTTP client."""
        mock_client_instance = Mock()
        mock_http_client.return_value = mock_client_instance

        edgework = Edgework()

        # Verify all stats models have the HTTP client
        assert edgework._skaters._client == mock_client_instance
        assert edgework._goalies._client == mock_client_instance
        assert edgework._team_stats._client == mock_client_instance


class TestEdgeworkPlayers:
    """Test class for Edgework player delegation."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        with (
            patch("edgework.edgework.HttpClient"),
            patch("edgework.edgework.PlayerClient") as mock_player_client,
        ):
            self.mock_player_client_instance = Mock()
            mock_player_client.return_value = self.mock_player_client_instance
            self.edgework = Edgework()

    def test_get_all_players_active_only_default(self):
        """Test get_all_players with default active_only=True."""
        mock_players = [_make_player(), _make_player(player_id=8479351)]
        self.mock_player_client_instance.get_active_players.return_value = mock_players

        result = self.edgework.get_all_players()

        self.mock_player_client_instance.get_active_players.assert_called_once()
        self.mock_player_client_instance.get_all_players.assert_not_called()
        assert result == mock_players

    def test_get_all_players_active_only_false(self):
        """Test get_all_players with active_only=False."""
        mock_players = [
            _make_player(player_id=1),
            _make_player(player_id=2, last_name="Gretzky"),
        ]
        self.mock_player_client_instance.get_all_players.return_value = mock_players

        result = self.edgework.get_all_players(active_only=False)

        self.mock_player_client_instance.get_all_players.assert_called_once()
        self.mock_player_client_instance.get_active_players.assert_not_called()
        assert result == mock_players

    def test_get_all_players_return_type(self):
        """Test that get_all_players returns a list."""
        self.mock_player_client_instance.get_active_players.return_value = []
        assert isinstance(self.edgework.get_all_players(), list)

    def test_get_player_delegates_to_client(self):
        """Test that get_player delegates to the player client."""
        mock_player = _make_player()
        self.mock_player_client_instance.get_player.return_value = mock_player

        player = self.edgework.get_player(8478402)

        self.mock_player_client_instance.get_player.assert_called_once_with(8478402)
        assert player == mock_player


class TestEdgeworkTeamScheduleDelegation:
    """Test class for Edgework team and schedule delegation."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        with (
            patch("edgework.edgework.HttpClient"),
            patch("edgework.edgework.PlayerClient"),
            patch("edgework.edgework.TeamClient") as mock_team_client,
            patch("edgework.edgework.ScheduleClient") as mock_schedule_client,
        ):
            self.mock_team_client_instance = Mock()
            self.mock_schedule_client_instance = Mock()
            mock_team_client.return_value = self.mock_team_client_instance
            mock_schedule_client.return_value = self.mock_schedule_client_instance
            self.edgework = Edgework()

    def test_get_teams_delegates_to_team_client(self):
        """Test that get_teams delegates to the team client."""
        result = self.edgework.get_teams()

        self.mock_team_client_instance.get_teams.assert_called_once()
        assert result == self.mock_team_client_instance.get_teams.return_value

    def test_get_roster_without_season(self):
        """Test that get_roster passes through when no season is given."""
        self.edgework.get_roster("TOR")

        self.mock_team_client_instance.get_roster.assert_called_once_with("TOR", None)

    def test_get_roster_with_season_conversion(self):
        """Test that get_roster converts 'YYYY-YYYY' season format."""
        self.edgework.get_roster("TOR", "2023-2024")

        self.mock_team_client_instance.get_roster.assert_called_once_with(
            "TOR", 20232024
        )

    def test_get_roster_invalid_season(self):
        """Test that get_roster rejects invalid season formats."""
        with pytest.raises(ValueError):
            self.edgework.get_roster("TOR", "2023")

        self.mock_team_client_instance.get_roster.assert_not_called()

    def test_get_schedule_now_delegates(self):
        """Test that get_schedule_now delegates to the schedule client."""
        self.edgework.get_schedule_now()

        self.mock_schedule_client_instance.get_schedule.assert_called_once()

    def test_get_schedule_for_date_delegates(self):
        """Test that get_schedule_for_date delegates to the schedule client."""
        self.edgework.get_schedule_for_date("2024-01-15")

        self.mock_schedule_client_instance.get_schedule_for_date.assert_called_once_with(
            "2024-01-15"
        )


class TestEdgeworkContextManager:
    """Test class for Edgework context manager functionality."""

    @patch("edgework.edgework.HttpClient")
    @patch("edgework.edgework.PlayerClient")
    def test_context_manager_enter(self, mock_player_client, mock_http_client):
        """Test Edgework as context manager __enter__ method."""
        with Edgework() as edgework:
            assert isinstance(edgework, Edgework)

    @patch("edgework.edgework.HttpClient")
    @patch("edgework.edgework.PlayerClient")
    def test_context_manager_exit_with_close_method(
        self, mock_player_client, mock_http_client
    ):
        """Test Edgework context manager __exit__ calls close if available."""
        mock_client_instance = Mock()
        mock_client_instance.close = Mock()
        mock_http_client.return_value = mock_client_instance

        with Edgework() as edgework:
            pass  # Exit the context

        mock_client_instance.close.assert_called_once()

    @patch("edgework.edgework.HttpClient")
    @patch("edgework.edgework.PlayerClient")
    def test_context_manager_exit_without_close_method(
        self, mock_player_client, mock_http_client
    ):
        """Test Edgework context manager __exit__ handles client without close method."""
        mock_client_instance = Mock()
        # Don't add close method to simulate client without close
        del mock_client_instance.close
        mock_http_client.return_value = mock_client_instance

        # Should not raise an exception
        with Edgework() as edgework:
            assert isinstance(edgework, Edgework)

    @patch("edgework.edgework.HttpClient")
    @patch("edgework.edgework.PlayerClient")
    def test_close_method_directly(self, mock_player_client, mock_http_client):
        """Test calling close method directly."""
        mock_client_instance = Mock()
        mock_client_instance.close = Mock()
        mock_http_client.return_value = mock_client_instance

        edgework = Edgework()
        edgework.close()

        mock_client_instance.close.assert_called_once()

    @patch("edgework.edgework.HttpClient")
    @patch("edgework.edgework.PlayerClient")
    def test_close_method_no_close_attribute(
        self, mock_player_client, mock_http_client
    ):
        """Test close method when client doesn't have close attribute."""
        mock_client_instance = Mock()
        # Simulate client without close method
        del mock_client_instance.close
        mock_http_client.return_value = mock_client_instance

        edgework = Edgework()
        # Should not raise an exception
        edgework.close()


class TestSeasonValidation:
    """Test class for the shared season string conversion helper."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        with (
            patch("edgework.edgework.HttpClient"),
            patch("edgework.edgework.PlayerClient"),
        ):
            self.edgework = Edgework()

    @pytest.mark.parametrize(
        "season_str,expected_int",
        [
            ("2023-2024", 20232024),
            ("2022-2023", 20222023),
            ("2021-2022", 20212022),
            ("2020-2021", 20202021),
            ("1999-2000", 19992000),
        ],
    )
    def test_season_conversion_valid_formats(self, season_str, expected_int):
        """Test season string conversion for various valid formats."""
        assert _validate_season_format(season_str) == expected_int

    @pytest.mark.parametrize(
        "invalid_season",
        [
            "2023",
            "23-24",
            "2023-24",
            "2023/2024",
            "2023_2024",
            "2023 2024",
            "abc-def",
            "2023-abcd",
            "",
            "2023-",
            "-2024",
        ],
    )
    def test_season_conversion_invalid_formats(self, invalid_season):
        """Test season string conversion for various invalid formats."""
        with pytest.raises(
            ValueError, match="Invalid season format. Expected 'YYYY-YYYY'"
        ):
            _validate_season_format(invalid_season)

    def test_season_conversion_non_string(self):
        """Test that non-string seasons are rejected."""
        with pytest.raises(
            ValueError, match="Invalid season format. Expected 'YYYY-YYYY'"
        ):
            _validate_season_format(20232024)

    def test_season_conversion_mismatched_years(self):
        """Test that non-consecutive years are rejected."""
        with pytest.raises(
            ValueError, match="Invalid season format. Expected 'YYYY-YYYY'"
        ):
            _validate_season_format("2022-2024")

    def test_roster_uses_shared_season_helper(self):
        """Test that the facade converts seasons through the shared helper."""
        with (
            patch("edgework.edgework.HttpClient"),
            patch("edgework.edgework.PlayerClient"),
            patch("edgework.edgework.TeamClient") as mock_team_client,
        ):
            edgework = Edgework()
            edgework.get_roster("TOR", "1999-2000")

            mock_team_client.return_value.get_roster.assert_called_once_with(
                "TOR", 19992000
            )


class TestEdgeworkIntegration:
    """Integration tests for Edgework class functionality."""

    @patch("edgework.edgework.PlayerClient")
    @patch("edgework.edgework.HttpClient")
    def test_multiple_method_calls_same_instance(
        self, mock_http_client, mock_player_client
    ):
        """Test that multiple method calls work on the same instance."""
        mock_client_instance = Mock()
        mock_http_client.return_value = mock_client_instance
        mock_player_client_instance = Mock()
        mock_player_client.return_value = mock_player_client_instance

        edgework = Edgework()

        # Test players delegation
        mock_players = [_make_player()]
        mock_player_client_instance.get_active_players.return_value = mock_players
        players_result = edgework.get_all_players()

        # Test client access
        standings_result = edgework.standings
        stats_result = edgework.stats

        # Verify all calls work and return expected objects
        assert players_result == mock_players
        assert standings_result is edgework.standings
        assert stats_result is edgework.stats

    @patch("edgework.edgework.PlayerClient")
    @patch("edgework.edgework.HttpClient")
    def test_client_shared_across_stats_models(
        self, mock_http_client, mock_player_client
    ):
        """Test that the HTTP client is shared across all stats models."""
        mock_client_instance = Mock()
        mock_http_client.return_value = mock_client_instance

        edgework = Edgework()

        # All stats models should share the same HTTP client
        assert edgework._skaters._client == mock_client_instance
        assert edgework._goalies._client == mock_client_instance
        assert edgework._team_stats._client == mock_client_instance
        assert edgework._client == mock_client_instance

    def test_stats_models_are_different_instances(self):
        """Test that stats models are different instances."""
        with (
            patch("edgework.edgework.HttpClient"),
            patch("edgework.edgework.PlayerClient"),
        ):
            edgework = Edgework()

            assert edgework._skaters is not edgework._goalies
            assert edgework._goalies is not edgework._team_stats
            assert edgework._team_stats is not edgework._skaters

    @patch("edgework.edgework.PlayerClient")
    @patch("edgework.edgework.HttpClient")
    def test_error_handling_preserves_instance_state(
        self, mock_http_client, mock_player_client
    ):
        """Test that errors in one method don't affect instance state."""
        mock_client_instance = Mock()
        mock_http_client.return_value = mock_client_instance

        edgework = Edgework()

        # Test that an error in get_roster doesn't break the instance
        with pytest.raises(ValueError):
            edgework.get_roster("TOR", "invalid-season")

        # Instance should still be functional
        mock_players = [_make_player()]
        mock_player_client.return_value.get_active_players.return_value = mock_players
        assert edgework.get_all_players() == mock_players


class TestEdgeworkTypeHints:
    """Test class for type hints and return types."""

    @patch("edgework.edgework.PlayerClient")
    @patch("edgework.edgework.HttpClient")
    def test_get_all_players_return_type(self, mock_http_client, mock_player_client):
        """Test that get_all_players returns a list of Player instances."""
        mock_player_client.return_value.get_active_players.return_value = [
            _make_player()
        ]

        edgework = Edgework()
        result = edgework.get_all_players()

        assert isinstance(result, list)
        assert all(isinstance(player, Player) for player in result)

    @patch("edgework.edgework.PlayerClient")
    @patch("edgework.edgework.HttpClient")
    def test_get_player_return_type(self, mock_http_client, mock_player_client):
        """Test that get_player returns a Player instance."""
        mock_player_client.return_value.get_player.return_value = _make_player()

        edgework = Edgework()
        result = edgework.get_player(8478402)

        assert isinstance(result, Player)

    @patch("edgework.edgework.PlayerClient")
    @patch("edgework.edgework.HttpClient")
    def test_get_teams_return_type(self, mock_http_client, mock_player_client):
        """Test that get_teams returns whatever the team client produces."""
        with patch("edgework.edgework.TeamClient") as mock_team_client:
            mock_team_client.return_value.get_teams.return_value = [Mock(spec=Team)]

            edgework = Edgework()
            result = edgework.get_teams()

            assert isinstance(result, list)

    @patch("edgework.edgework.PlayerClient")
    @patch("edgework.edgework.HttpClient")
    def test_get_roster_return_type(self, mock_http_client, mock_player_client):
        """Test that get_roster returns whatever the team client produces."""
        with patch("edgework.edgework.TeamClient") as mock_team_client:
            mock_team_client.return_value.get_roster.return_value = Mock(spec=Roster)

            edgework = Edgework()
            result = edgework.get_roster("TOR", "2023-2024")

            assert result is mock_team_client.return_value.get_roster.return_value

    def test_context_manager_return_type(self):
        """Test that context manager returns Edgework instance."""
        with (
            patch("edgework.edgework.HttpClient"),
            patch("edgework.edgework.PlayerClient"),
        ):
            with Edgework() as edgework:
                assert isinstance(edgework, Edgework)
