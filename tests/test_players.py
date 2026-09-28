"""Tests for the players() method in the Edgework client."""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from edgework.clients.player_client import PlayerClient, landing_to_dict
from edgework.edgework import Edgework
from edgework.http_client import HttpClient
from edgework.models.player import Player


class TestPlayersMethod:
    """Test class for player access through the Edgework facade.

    The facade exposes the ``PlayerClient`` as ``client.players`` and
    delegates convenience lookups to it via ``get_all_players`` and
    ``get_player``.
    """

    def setup_method(self):
        """Set up test fixtures before each test method."""
        with (
            patch("edgework.edgework.HttpClient"),
            patch("edgework.edgework.PlayerClient") as mock_player_client,
        ):
            self.mock_player_client_instance = Mock(spec=PlayerClient)
            mock_player_client.return_value = self.mock_player_client_instance
            self.client = Edgework()

    def _make_player(
        self,
        player_id=8478402,
        first_name="Connor",
        last_name="McDavid",
        position="C",
        is_active=True,
    ):
        """Build a Player populated with data, as the client would."""
        return Player(
            player_id=player_id,
            first_name=first_name,
            last_name=last_name,
            position=position,
            is_active=is_active,
        )

    def test_players_attribute_is_player_client(self):
        """Test that the facade exposes the PlayerClient as `players`."""
        assert isinstance(self.client.players, PlayerClient)

    def test_players_active_only_default(self):
        """Test that get_all_players() returns only active players by default."""
        mock_players = [self._make_player(), self._make_player(player_id=8479351)]
        self.mock_player_client_instance.get_active_players.return_value = mock_players

        players = self.client.get_all_players()

        self.mock_player_client_instance.get_active_players.assert_called_once()
        self.mock_player_client_instance.get_all_players.assert_not_called()
        assert players == mock_players
        assert all(player._data.get("is_active") is True for player in players)

    def test_players_active_only_explicit(self):
        """Test that get_all_players(active_only=True) returns only active players."""
        mock_players = [self._make_player()]
        self.mock_player_client_instance.get_active_players.return_value = mock_players

        players = self.client.get_all_players(active_only=True)

        self.mock_player_client_instance.get_active_players.assert_called_once()
        self.mock_player_client_instance.get_all_players.assert_not_called()
        assert players == mock_players

    def test_players_all_players(self):
        """Test that get_all_players(active_only=False) returns all players."""
        all_players = [
            self._make_player(player_id=1, is_active=True),
            self._make_player(player_id=2, last_name="Gretzky", is_active=False),
        ]
        self.mock_player_client_instance.get_all_players.return_value = all_players

        players = self.client.get_all_players(active_only=False)

        self.mock_player_client_instance.get_all_players.assert_called_once()
        self.mock_player_client_instance.get_active_players.assert_not_called()
        assert players == all_players
        assert any(player._data.get("is_active") is False for player in players)

    def test_players_return_type(self):
        """Test that get_all_players returns a list of Player objects."""
        self.mock_player_client_instance.get_active_players.return_value = []
        assert isinstance(self.client.get_all_players(), list)

    def test_players_method_no_exceptions(self):
        """Test that get_all_players does not raise for either parameter value."""
        self.mock_player_client_instance.get_active_players.return_value = [
            self._make_player()
        ]
        self.mock_player_client_instance.get_all_players.return_value = [
            self._make_player()
        ]

        assert self.client.get_all_players(active_only=True)
        assert self.client.get_all_players(active_only=False)

    def test_get_player_delegates_to_client(self):
        """Test that get_player delegates to the player client."""
        mock_player = self._make_player()
        self.mock_player_client_instance.get_player.return_value = mock_player

        player = self.client.get_player(8478402)

        self.mock_player_client_instance.get_player.assert_called_once_with(8478402)
        assert player == mock_player

    def test_player_object_structure(self):
        """Test that Player objects have the expected structure."""
        player = self._make_player()

        assert isinstance(player, Player), "Should be a Player object"
        assert hasattr(player, "_data"), "Player should have _data"
        assert hasattr(player, "obj_id"), "Player should have obj_id"

        data = player._data
        assert data["player_id"] == 8478402
        assert isinstance(data["player_id"], int), "player_id should be an integer"
        assert data["player_id"] > 0, "player_id should be positive"
        assert isinstance(data["first_name"], str), "first_name should be a string"
        assert isinstance(data["last_name"], str), "last_name should be a string"
        assert data["position"] in ["C", "L", "R", "D", "G"], (
            f"Position {data['position']} should be valid"
        )

    def test_player_string_methods(self):
        """Test Player object string representations."""
        player = self._make_player()

        assert isinstance(str(player), str), "__str__ should return a string"
        assert len(str(player)) > 0, "__str__ should not be empty"

        assert "Player(id=" in repr(player), "__repr__ should contain Player(id="

        full_name = player.full_name
        assert isinstance(full_name, str), "full_name should return a string"
        assert len(full_name) > 0, "full_name should not be empty"
        assert (
            player._data["first_name"] in full_name
        ), "full_name should contain first name"
        assert (
            player._data["last_name"] in full_name
        ), "full_name should contain last name"

    def test_player_equality_and_hashing(self):
        """Test Player object equality and hashing."""
        player1 = self._make_player()
        player2 = self._make_player(player_id=8479351)
        player1_copy = Player(**player1._data)

        # Test equality
        assert player1 == player1_copy, "Players with same ID should be equal"
        assert player1 != player2, "Players with different IDs should not be equal"

        # Test hashing (for use in sets/dicts)
        player_set = {player1, player1_copy, player2}
        assert len(player_set) == 2, "Set should contain only unique players"

    @pytest.mark.live_api
    def test_players_active_only_live(self):
        """Test get_all_players with the live API."""
        client = Edgework()
        players = client.get_all_players(active_only=True)

        assert isinstance(players, list), "players should return a list"
        assert len(players) > 0, "Should return at least some active players"
        for player in players:
            assert isinstance(player, Player), "Each item should be a Player object"
            assert player._data.get("is_active") is True


class TestPlayerFetchData:
    """Test class for the Player.fetch_data() method."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_client = Mock(spec=HttpClient)

    def test_fetch_data_success(self):
        """Test successful data fetching from the landing API."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "playerId": 8478402,
            "firstName": {"default": "Connor"},
            "lastName": {"default": "McDavid"},
            "birthDate": "1997-01-13",
            "position": "C",
            "sweaterNumber": 97,
            "currentTeamAbbrev": "EDM",
            "draftDetails": {
                "year": 2015,
                "round": 1,
                "overallPick": 1,
                "teamAbbrev": "EDM",
            },
        }
        self.mock_client.get.return_value = mock_response

        # Create player and fetch data
        player = Player(edgework_client=self.mock_client, obj_id=8478402)
        player._data = {}  # Clear initial data
        player._fetched = False

        player.fetch_data()

        # Verify API call was made correctly
        self.mock_client.get.assert_called_once_with("player/8478402/landing", web=True)

        # Verify data was updated
        assert player._fetched is True
        assert player._data["player_id"] == 8478402
        assert player._data["first_name"] == "Connor"
        assert player._data["last_name"] == "McDavid"
        assert player._data["position"] == "C"
        assert player._data["sweater_number"] == 97
        assert player._data["current_team_abbrev"] == "EDM"
        assert player._data["draft_year"] == datetime(2015, 1, 1)
        assert player._data["draft_round"] == 1
        assert player._data["draft_overall_pick"] == 1

    def test_fetch_data_no_client(self):
        """Test fetch_data raises ValueError when no client is available."""
        player = Player(edgework_client=None, obj_id=8478402)

        with pytest.raises(
            ValueError, match="No client available to fetch player data"
        ):
            player.fetch_data()

    def test_fetch_data_no_player_id(self):
        """Test fetch_data raises ValueError when no player ID is available."""
        player = Player(edgework_client=self.mock_client, obj_id=None)

        with pytest.raises(ValueError, match="No player ID available to fetch data"):
            player.fetch_data()

    def test_fetch_data_preserves_existing_data(self):
        """Test that fetch_data preserves existing data and merges new data."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "playerId": 8478402,
            "firstName": {"default": "Connor"},
            "lastName": {"default": "McDavid"},
            "position": "C",
        }
        self.mock_client.get.return_value = mock_response

        # Create player with some existing data
        player = Player(edgework_client=self.mock_client, obj_id=8478402)
        player._data = {"existing_field": "existing_value", "player_id": 8478402}
        player._fetched = False

        player.fetch_data()

        # Verify existing data is preserved and new data is added
        assert player._data["existing_field"] == "existing_value"
        assert player._data["player_id"] == 8478402
        assert player._data["first_name"] == "Connor"
        assert player._data["last_name"] == "McDavid"
        assert player._data["position"] == "C"

    @pytest.mark.live_api
    def test_fetch_data_live_api(self):
        """Test fetch_data with live API call."""
        client = Edgework()

        # Create player with Connor McDavid's ID
        player = Player(edgework_client=client._client, obj_id=8478402)
        player._data = {}
        player._fetched = False

        player.fetch_data()

        # Verify data was fetched
        assert player._fetched is True
        assert player._data["player_id"] == 8478402
        assert player._data["first_name"] == "Connor"
        assert player._data["last_name"] == "McDavid"
        assert player._data["position"] == "C"
        assert player._data["current_team_abbrev"] == "EDM"
        assert isinstance(player._data["birth_date"], datetime)


class TestLandingToDict:
    """Test class for the landing_to_dict function."""

    def test_simple_camel_to_snake_conversion(self):
        """Test basic camelCase to snake_case conversion."""
        data = {
            "playerId": 12345,
            "firstName": "John",
            "lastName": "Doe",
            "isActive": True,
            "sweaterNumber": 99,
        }

        result = landing_to_dict(data)

        assert result["player_id"] == 12345
        assert result["first_name"] == "John"
        assert result["last_name"] == "Doe"
        assert result["is_active"] is True
        assert result["sweater_number"] == 99

    def test_nested_dict_with_default_extraction(self):
        """Test extraction of 'default' values from nested dictionaries."""
        data = {
            "firstName": {"default": "Connor", "fr": "Connor"},
            "lastName": {"default": "McDavid", "fr": "McDavid"},
            "birthCity": {"default": "Richmond Hill", "fr": "Richmond Hill"},
            "simpleField": "not_nested",
        }

        result = landing_to_dict(data)

        assert result["first_name"] == "Connor"
        assert result["last_name"] == "McDavid"
        assert result["birth_city"] == "Richmond Hill"
        assert result["simple_field"] == "not_nested"

    def test_draft_details_special_handling(self):
        """Test special handling of draftDetails nested object."""
        data = {
            "playerId": 8478402,
            "draftDetails": {
                "year": 2015,
                "round": 1,
                "overallPick": 1,
                "pickInRound": 1,
                "teamAbbrev": "EDM",
            },
        }

        result = landing_to_dict(data)

        assert result["player_id"] == 8478402
        assert result["draft_year"] == datetime(2015, 1, 1)
        assert result["draft_round"] == 1
        assert result["draft_overall_pick"] == 1
        assert result["draft_pick_in_round"] == 1
        assert result["draft_team_abbrev"] == "EDM"

    def test_date_string_parsing(self):
        """Test automatic parsing of date strings."""
        data = {
            "birthDate": "1997-01-13",
            "someTimestamp": "2023-12-25T15:30:00",
            "isoTimestamp": "2023-12-25T15:30:00Z",
            "notADate": "just_a_string",
        }

        result = landing_to_dict(data)

        assert result["birth_date"] == datetime(1997, 1, 13)
        assert result["some_timestamp"] == datetime(2023, 12, 25, 15, 30, 0)
        assert result["iso_timestamp"] == datetime(2023, 12, 25, 15, 30, 0)
        assert result["not_a_date"] == "just_a_string"

    def test_nested_object_flattening(self):
        """Test flattening of complex nested objects."""
        data = {
            "careerTotals": {
                "regularSeason": {
                    "gamesPlayed": 695,
                    "goals": 335,
                    "assists": 645,
                },
                "playoffs": {"gamesPlayed": 79, "goals": 42},
            }
        }

        result = landing_to_dict(data)

        assert result["career_totals_regular_season_games_played"] == 695
        assert result["career_totals_regular_season_goals"] == 335
        assert result["career_totals_regular_season_assists"] == 645
        assert result["career_totals_playoffs_games_played"] == 79
        assert result["career_totals_playoffs_goals"] == 42

    def test_list_handling(self):
        """Test handling of lists in the data."""
        data = {
            "awards": ["Hart Trophy", "Art Ross Trophy"],
            "teams": [{"id": 1, "name": "Team1"}, {"id": 2, "name": "Team2"}],
            "simpleList": [1, 2, 3],
        }

        result = landing_to_dict(data)

        assert result["awards"] == ["Hart Trophy", "Art Ross Trophy"]
        assert len(result["teams"]) == 2
        assert result["teams"][0]["id"] == 1
        assert result["teams"][0]["name"] == "Team1"
        assert result["simple_list"] == [1, 2, 3]

    def test_null_and_empty_values(self):
        """Test handling of null and empty values."""
        data = {
            "nullField": None,
            "emptyString": "",
            "zeroValue": 0,
            "falseValue": False,
            "emptyList": [],
            "emptyDict": {},
        }

        result = landing_to_dict(data)

        assert result["null_field"] is None
        assert result["empty_string"] == ""
        assert result["zero_value"] == 0
        assert result["false_value"] is False
        assert result["empty_list"] == []
        # Empty dicts are processed but result in no additional fields

    def test_complex_real_world_structure(self):
        """Test with a complex structure similar to real NHL API response."""
        data = {
            "playerId": 8478402,
            "firstName": {"default": "Connor"},
            "lastName": {"default": "McDavid"},
            "birthDate": "1997-01-13",
            "currentTeamAbbrev": "EDM",
            "draftDetails": {
                "year": 2015,
                "round": 1,
                "overallPick": 1,
            },
            "featuredStats": {
                "regularSeason": {
                    "subSeason": {
                        "goals": 64,
                        "assists": 89,
                        "points": 153,
                    },
                    "career": {"goals": 335, "assists": 645},
                }
            },
            "isActive": True,
            "awards": ["Hart Trophy", "Art Ross Trophy"],
        }

        result = landing_to_dict(data)

        # Verify basic fields
        assert result["player_id"] == 8478402
        assert result["first_name"] == "Connor"
        assert result["last_name"] == "McDavid"
        assert result["birth_date"] == datetime(1997, 1, 13)
        assert result["current_team_abbrev"] == "EDM"
        assert result["is_active"] is True

        # Verify draft details
        assert result["draft_year"] == datetime(2015, 1, 1)
        assert result["draft_round"] == 1
        assert result["draft_overall_pick"] == 1

        # Verify nested stats
        assert result["featured_stats_regular_season_sub_season_goals"] == 64
        assert result["featured_stats_regular_season_sub_season_assists"] == 89
        assert result["featured_stats_regular_season_sub_season_points"] == 153
        assert result["featured_stats_regular_season_career_goals"] == 335
        assert result["featured_stats_regular_season_career_assists"] == 645

        # Verify awards list
        assert result["awards"] == ["Hart Trophy", "Art Ross Trophy"]

    def test_camel_to_snake_edge_cases(self):
        """Test edge cases in camelCase to snake_case conversion."""
        data = {
            "HTML": "html",
            "XMLParser": "xml_parser",
            "HTTPSConnection": "https_connection",
            "someHTTPURL": "some_httpurl",  # This is what the actual conversion produces
            "a": "a",
            "aB": "a_b",
            "AB": "ab",
            "ABC": "abc",
        }

        result = landing_to_dict(data)

        assert "html" in result
        assert "xml_parser" in result
        assert "https_connection" in result
        assert "some_httpurl" in result  # Fixed expectation
        assert "a" in result
        assert "a_b" in result


class TestPlayersIntegration:
    """Integration tests for player access with real API calls."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.client = Edgework()

    @pytest.mark.live_api
    def test_players_data_consistency(self):
        """Test that player data is consistent across multiple calls."""
        players1 = self.client.get_all_players(active_only=True)
        players2 = self.client.get_all_players(active_only=True)

        # Results should be consistent
        assert len(players1) == len(
            players2
        ), "Multiple calls should return same number of players"

        # Convert to sets of player IDs for comparison
        ids1 = {p._data.get("player_id") for p in players1}
        ids2 = {p._data.get("player_id") for p in players2}

        assert ids1 == ids2, "Multiple calls should return same players"

    @pytest.mark.live_api
    def test_players_team_data_presence(self):
        """Test that active players have team information."""
        players = self.client.get_all_players(active_only=True)

        players_with_teams = [
            p
            for p in players
            if p._data.get("current_team_id") or p._data.get("current_team_abbr")
        ]

        # Most active players should have team information
        team_percentage = len(players_with_teams) / len(players)
        assert (
            team_percentage > 0.8
        ), f"Expected >80% of active players to have team info, got {team_percentage:.1%}"
