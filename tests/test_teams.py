"""Tests for team-related functionality in the Edgework client."""

from unittest.mock import Mock

import pytest

from edgework.clients.team_client import TeamClient
from edgework.const import STATS_API_URL
from edgework.edgework import Edgework
from edgework.endpoints import API_PATH
from edgework.http_client import HttpClient
from edgework.models.player import Player
from edgework.models.team import Roster, Team


class TestTeamMethods:
    """Test class for team-related methods."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.client = Edgework()

    def test_get_teams(self):
        """Test that get_teams() returns a list of teams."""
        teams = self.client.get_teams()

        # Assert that we get teams
        assert isinstance(teams, list), "get_teams() should return a list"
        assert len(teams) > 0, "Should return at least some teams"
        assert len(teams) == 62, "Should return exactly 32 teams"

        # Check that all returned items are Team objects
        for team in teams:
            assert isinstance(team, Team), "Each item should be a Team object"
            assert hasattr(team, "_data"), "Team should have _data attribute"
            assert hasattr(team, "abbrev"), "Team should have abbrev property"
            assert hasattr(team, "name"), "Team should have name property"

    def test_get_roster_current(self):
        """Test that get_roster() returns a roster for a team."""
        # Use Toronto Maple Leafs as test team
        roster = self.client.get_roster("TOR")

        # Assert that we get a roster
        assert isinstance(roster, Roster), "get_roster() should return a Roster object"
        assert hasattr(roster, "players"), "Roster should have players property"

        # Check that roster has players
        players = roster.players
        assert isinstance(players, list), "Roster.players should return a list"
        assert len(players) > 0, "Roster should have at least some players"

        # Check that all players are Player objects
        for player in players:
            assert isinstance(player, Player), "Each player should be a Player object"

    def test_roster_position_properties(self):
        """Test that roster position properties work correctly."""
        roster = self.client.get_roster("TOR")

        # Test position properties
        forwards = roster.forwards
        defensemen = roster.defensemen
        goalies = roster.goalies

        assert isinstance(forwards, list), "forwards should return a list"
        assert isinstance(defensemen, list), "defensemen should return a list"
        assert isinstance(goalies, list), "goalies should return a list"

        # Check that we have players in each position
        assert len(forwards) > 0, "Should have at least some forwards"
        assert len(defensemen) > 0, "Should have at least some defensemen"
        assert len(goalies) > 0, "Should have at least some goalies"

        # Check position codes
        for forward in forwards:
            assert forward.position in [
                "C",
                "L",
                "R",
                "LW",
                "RW",
            ], f"Forward {forward} has invalid position: {forward.position}"

        for defenseman in defensemen:
            assert (
                defenseman.position == "D"
            ), f"Defenseman {defenseman} has invalid position: {defenseman.position}"

        for goalie in goalies:
            assert (
                goalie.position == "G"
            ), f"Goalie {goalie} has invalid position: {goalie.position}"

    def test_team_properties(self):
        """Test that Team objects have correct properties."""
        teams = self.client.get_teams()

        if teams:
            team = teams[0]  # Test with first team

            # Test basic properties
            assert hasattr(team, "name"), "Team should have name property"
            assert hasattr(team, "abbrev"), "Team should have abbrev property"
            assert hasattr(team, "full_name"), "Team should have full_name property"

            # Test string representation
            assert str(team) != "", "Team string representation should not be empty"
            assert repr(team) != "", "Team repr should not be empty"

            # Test equality
            same_team = teams[0]
            assert team == same_team, "Same team should be equal to itself"

    def test_team_methods(self):
        """Test that Team methods work correctly."""
        teams = self.client.get_teams()

        if teams:

            for team in teams:
                if team.tri_code == "TOR":
                    break

            # Test get_roster method
            roster = team.get_roster()
            assert isinstance(
                roster, Roster
            ), "Team.get_roster() should return a Roster object"

            # Test get_stats method (should return response object)
            stats_response = team.get_stats()
            assert hasattr(
                stats_response, "status_code"
            ), "get_stats should return a response object"

            # Test get_schedule method (should return response object)
            schedule_response = team.get_schedule()
            assert hasattr(
                schedule_response, "status_code"
            ), "get_schedule should return a response object"

    def test_roster_utility_methods(self):
        """Test roster utility methods."""
        roster = self.client.get_roster("TOR")

        # Test get_player_by_number if we have players with numbers
        players = roster.players
        if players:
            for player in players:
                if player.sweater_number:
                    found_player = roster.get_player_by_number(player.sweater_number)
                    assert (
                        found_player is not None
                    ), f"Should find player with number {player.sweater_number}"
                    assert (
                        found_player == player
                    ), "Found player should be the same as original"
                    break

        # Test get_player_by_name if we have players
        if players:
            player = players[0]
            found_player = roster.get_player_by_name(player.full_name)
            assert (
                found_player is not None
            ), f"Should find player with name {player.full_name}"
            assert found_player == player, "Found player should be the same as original"

    def teardown_method(self):
        """Clean up after each test method."""
        if hasattr(self.client, "close"):
            self.client.close()


class TestTeamIntegration:
    """Integration tests for team functionality."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.client = Edgework()

    def test_full_team_workflow(self):
        """Test a complete workflow with teams and rosters."""
        # Get all teams
        teams = self.client.get_teams()
        assert len(teams) > 0, "Should have teams"

        # Pick a team (Toronto Maple Leafs)
        tor_team = None
        for team in teams:
            if team.abbrev == "TOR":
                tor_team = team
                break

        if tor_team:
            # Get roster
            roster = tor_team.get_roster()
            assert isinstance(roster, Roster), "Should get a roster"

            # Check positions
            assert len(roster.forwards) > 0, "Should have forwards"
            assert len(roster.defensemen) > 0, "Should have defensemen"
            assert len(roster.goalies) > 0, "Should have goalies"

            # Test player search
            if roster.players:
                first_player = roster.players[0]
                found_by_name = roster.get_player_by_name(first_player.full_name)
                assert found_by_name == first_player, "Should find player by name"

    def teardown_method(self):
        """Clean up after each test method."""
        if hasattr(self.client, "close"):
            self.client.close()


class TestTeamClientRoutes:
    """Mocked unit tests for TeamClient route construction (Task 2).

    Regression coverage: prior public methods must construct the same
    requests as before, except the explicit ``/team/id/{id}`` fix.
    """

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_http_client = Mock()
        self.team_client = TeamClient(self.mock_http_client)

    @staticmethod
    def _response(payload):
        """Build a mock HTTP response with the given JSON payload."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = payload
        return response

    # -- explicit fix: documented /{lang}/team/id/{id} route -------------

    def test_get_team_uses_documented_team_id_route(self):
        """get_team must request 'team/id/{id}' on the Stats API, not 'team/{id}'."""
        self.mock_http_client.get.return_value = self._response(
            {"id": 10, "fullName": "Toronto Maple Leafs", "triCode": "TOR"}
        )

        team = self.team_client.get_team(10)

        self.mock_http_client.get.assert_called_once_with("team/id/10", web=False)
        assert isinstance(team, Team)
        assert team._data.get("team_id") == 10

    def test_get_team_final_url_matches_stats_registry(self):
        """End-to-end URL must equal the stats_team_by_id registry route."""
        http_client = HttpClient()
        http_client._client = Mock()
        http_client._client.get.return_value = self._response({"id": 10})
        team_client = TeamClient(http_client)

        team_client.get_team(10)

        expected = (
            f"{STATS_API_URL}"
            f"{API_PATH['stats_team_by_id'].format(lang='en', team_id=10).lstrip('/')}"
        )
        actual = http_client._client.get.call_args.args[0]
        assert actual == expected == f"{STATS_API_URL}en/team/id/10"

    # -- regression: prior routes unchanged ------------------------------

    def test_get_teams_route_unchanged(self):
        """get_teams still requests the /{lang}/team collection route."""
        self.mock_http_client.get.return_value = self._response(
            {"data": [{"id": 10, "fullName": "Toronto Maple Leafs"}]}
        )

        teams = self.team_client.get_teams()

        self.mock_http_client.get.assert_called_once_with("team", web=False)
        assert isinstance(teams, list)
        assert all(isinstance(team, Team) for team in teams)

    def test_get_roster_route_unchanged(self):
        """get_roster still requests roster/{team}/current for current rosters."""
        self.mock_http_client.get.return_value = self._response(
            {"forwards": [], "defensemen": [], "goalies": []}
        )

        roster = self.team_client.get_roster("TOR")

        self.mock_http_client.get.assert_called_once_with(
            "roster/TOR/current", web=True
        )
        assert isinstance(roster, Roster)

    def test_get_roster_season_route_unchanged(self):
        """get_roster with an int season still requests roster/{team}/{season}."""
        self.mock_http_client.get.return_value = self._response(
            {"forwards": [], "defensemen": [], "goalies": []}
        )

        self.team_client.get_roster("TOR", 20232024)

        self.mock_http_client.get.assert_called_once_with(
            "roster/TOR/20232024", web=True
        )

    def test_get_team_stats_route_unchanged(self):
        """get_team_stats keeps building club-stats routes."""
        self.mock_http_client.get.return_value = self._response({"games": []})

        result = self.team_client.get_team_stats("TOR")
        self.mock_http_client.get.assert_called_once_with(
            "club-stats/TOR/now", web=True
        )
        assert result == {"games": []}

        self.mock_http_client.get.reset_mock()
        self.mock_http_client.get.return_value = self._response({"games": []})
        self.team_client.get_team_stats("TOR", 20232024, 3)
        self.mock_http_client.get.assert_called_once_with(
            "club-stats/TOR/20232024/3", web=True
        )

    def test_get_team_schedule_route_unchanged(self):
        """get_team_schedule keeps building club-schedule-season routes."""
        self.mock_http_client.get.return_value = self._response({"games": []})

        self.team_client.get_team_schedule("TOR")
        self.mock_http_client.get.assert_called_once_with(
            "club-schedule-season/TOR/now", web=True
        )

        self.mock_http_client.get.reset_mock()
        self.mock_http_client.get.return_value = self._response({"games": []})
        self.team_client.get_team_schedule("TOR", 20232024)
        self.mock_http_client.get.assert_called_once_with(
            "club-schedule-season/TOR/20232024", web=True
        )

    def test_get_team_prospects_route_unchanged(self):
        """get_team_prospects still requests prospects/{team}."""
        self.mock_http_client.get.return_value = self._response({"prospects": []})

        self.team_client.get_team_prospects("TOR")

        self.mock_http_client.get.assert_called_once_with("prospects/TOR", web=True)

    def test_get_scoreboard_route_unchanged(self):
        """get_scoreboard still requests scoreboard/{team}/now."""
        self.mock_http_client.get.return_value = self._response({"games": []})

        self.team_client.get_scoreboard("TOR")

        self.mock_http_client.get.assert_called_once_with(
            "scoreboard/TOR/now", web=True
        )

    # -- new: /v1/club-stats-season/{team} and /v1/roster-season/{team} --

    def test_get_club_stats_season_route(self):
        """get_club_stats_season requests club-stats-season/{team} (raw dict)."""
        payload = [{"seasonId": 20232024, "gameTypes": [2, 3]}]
        self.mock_http_client.get.return_value = self._response(payload)

        result = self.team_client.get_club_stats_season("TOR")

        self.mock_http_client.get.assert_called_once_with(
            "club-stats-season/TOR", web=True
        )
        assert result == payload

    def test_get_roster_season_route(self):
        """get_roster_season requests roster-season/{team} (raw dict)."""
        payload = [{"id": 20232024}]
        self.mock_http_client.get.return_value = self._response(payload)

        result = self.team_client.get_roster_season("TOR")

        self.mock_http_client.get.assert_called_once_with(
            "roster-season/TOR", web=True
        )
        assert result == payload

    # -- season normalization through the shared helper -------------------

    def test_get_roster_accepts_dash_season_string(self):
        """'YYYY-YYYY' season strings are normalized via the shared helper."""
        self.mock_http_client.get.return_value = self._response(
            {"forwards": [], "defensemen": [], "goalies": []}
        )

        self.team_client.get_roster("TOR", "2023-2024")

        self.mock_http_client.get.assert_called_once_with(
            "roster/TOR/20232024", web=True
        )

    def test_get_team_schedule_accepts_dash_season_string(self):
        """'YYYY-YYYY' season strings are normalized for schedule requests."""
        self.mock_http_client.get.return_value = self._response({"games": []})

        self.team_client.get_team_schedule("TOR", "2023-2024")

        self.mock_http_client.get.assert_called_once_with(
            "club-schedule-season/TOR/20232024", web=True
        )

    def test_invalid_season_string_raises_value_error(self):
        """Invalid 'YYYY-YYYY' strings raise ValueError from the shared helper."""
        with pytest.raises(ValueError, match="Invalid season format"):
            self.team_client.get_roster("TOR", "2023-24")

        with pytest.raises(ValueError, match="Invalid season format"):
            self.team_client.get_team_schedule("TOR", "2022-2024")


class TestTeamModelLazyLoading:
    """Team model lazy loading must use the documented /{lang}/team/id/{id} route."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_http_client = Mock()
        self.mock_http_client.get.return_value = Mock(
            status_code=200,
            json=Mock(
                return_value={
                    "id": 10,
                    "fullName": "Toronto Maple Leafs",
                    "triCode": "TOR",
                }
            ),
        )
        self.team = Team(self.mock_http_client, 10)

    def test_fetch_data_uses_documented_team_id_route(self):
        """Team.fetch_data must request 'team/id/{id}' on the Stats API."""
        self.team.fetch_data()

        self.mock_http_client.get.assert_called_once_with("team/id/10", web=False)

    def test_fetch_data_final_url_matches_stats_registry(self):
        """The lazy-load URL must equal the stats_team_by_id registry route."""
        http_client = HttpClient()
        http_client._client = Mock()
        http_client._client.get.return_value = self.mock_http_client.get.return_value
        team = Team(http_client, 10)

        team.fetch_data()

        expected = (
            f"{STATS_API_URL}"
            f"{API_PATH['stats_team_by_id'].format(lang='en', team_id=10).lstrip('/')}"
        )
        actual = http_client._client.get.call_args.args[0]
        assert actual == expected == f"{STATS_API_URL}en/team/id/10"

    def test_fetch_data_updates_team_data(self):
        """fetch_data merges the API payload into the model's data."""
        self.team.fetch_data()

        assert self.team._data.get("team_id") == 10
        assert self.team._fetched is True
