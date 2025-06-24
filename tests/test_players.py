"""Tests for the players() method in the Edgework client."""

import pytest
from edgework.edgework import Edgework
from edgework.models.player import Player


class TestPlayersMethod:
    """Test class for the players() method."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.client = Edgework()

    def test_players_active_only_default(self):
        """Test that players() returns only active players by default."""
        players = self.client.players()

        # Assert that we get some players
        assert isinstance(players, list), "players() should return a list"
        assert len(players) > 0, "Should return at least some active players"

        # Check that all returned players are active
        for player in players:
            assert isinstance(player, Player), "Each item should be a Player object"
            assert hasattr(player, "_data"), "Player should have _data attribute"
            assert (
                player._data.get("is_active") is True
            ), f"Player {player} should be active"

    def test_players_active_only_explicit(self):
        """Test that players(active_only=True) returns only active players."""
        players = self.client.players(active_only=True)

        # Assert that we get some players
        assert isinstance(players, list), "players() should return a list"
        assert len(players) > 0, "Should return at least some active players"

        # Check that all returned players are active
        for player in players:
            assert isinstance(player, Player), "Each item should be a Player object"
            assert (
                player._data.get("is_active") is True
            ), f"Player {player} should be active"

    def test_players_all_players(self):
        """Test that players(active_only=False) returns all players."""
        all_players = self.client.players(active_only=False)
        active_players = self.client.players(active_only=True)

        # Assert that we get some players
        assert isinstance(all_players, list), "players() should return a list"
        assert isinstance(active_players, list), "players() should return a list"
        assert len(all_players) > 0, "Should return at least some players"
        assert len(active_players) > 0, "Should return at least some active players"

        # All players should be more than just active players
        assert len(all_players) >= len(
            active_players
        ), "All players should be >= active players"

        # Check that we have both active and inactive players in all_players
        active_count = sum(1 for p in all_players if p._data.get("is_active") is True)
        inactive_count = sum(
            1 for p in all_players if p._data.get("is_active") is False
        )

        assert active_count > 0, "Should have some active players"
        assert inactive_count > 0, "Should have some inactive players"

    def test_player_object_structure(self):
        """Test that Player objects have the expected structure."""
        players = self.client.players(active_only=True)

        # Get first few players to test
        test_players = players[:3]

        for player in test_players:
            assert isinstance(player, Player), "Should be a Player object"

            # Test essential attributes exist
            assert hasattr(player, "_data"), "Player should have _data"
            assert hasattr(player, "obj_id"), "Player should have obj_id"

            # Test key player data fields
            data = player._data
            assert "player_id" in data, "Player should have player_id"
            assert "first_name" in data, "Player should have first_name"
            assert "last_name" in data, "Player should have last_name"
            assert "position" in data, "Player should have position"
            assert "is_active" in data, "Player should have is_active"

            # Test player_id is a valid integer
            assert isinstance(data["player_id"], int), "player_id should be an integer"
            assert data["player_id"] > 0, "player_id should be positive"

            # Test names are strings
            assert isinstance(data["first_name"], str), "first_name should be a string"
            assert isinstance(data["last_name"], str), "last_name should be a string"
            assert len(data["first_name"]) > 0, "first_name should not be empty"
            assert len(data["last_name"]) > 0, "last_name should not be empty"

            # Test position is a valid string
            assert isinstance(data["position"], str), "position should be a string"
            assert data["position"] in [
                "C",
                "L",
                "R",
                "D",
                "G",
            ], f"Position {data['position']} should be valid"

    def test_player_string_methods(self):
        """Test Player object string representations."""
        players = self.client.players(active_only=True)
        player = players[0]

        # Test __str__ method
        str_repr = str(player)
        assert isinstance(str_repr, str), "__str__ should return a string"
        assert len(str_repr) > 0, "__str__ should not be empty"

        # Test __repr__ method
        repr_str = repr(player)
        assert isinstance(repr_str, str), "__repr__ should return a string"
        assert "Player(id=" in repr_str, "__repr__ should contain Player(id="

        # Test full_name property
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
        players = self.client.players(active_only=True)

        if len(players) >= 2:
            player1 = players[0]
            player2 = players[1]
            player1_copy = Player(**player1._data)

            # Test equality
            assert player1 == player1_copy, "Players with same ID should be equal"
            assert player1 != player2, "Players with different IDs should not be equal"

            # Test hashing (for use in sets/dicts)
            player_set = {player1, player1_copy, player2}
            assert len(player_set) == 2, "Set should contain only unique players"

    def test_players_return_count_reasonable(self):
        """Test that the number of players returned is reasonable."""
        active_players = self.client.players(active_only=True)

        # The NHL API returns active players including prospects and affiliates
        # Let's test for a reasonable range based on actual data
        assert (
            1500 <= len(active_players) <= 3000
        ), f"Expected 1500-3000 active players (including prospects), got {len(active_players)}"

    def test_players_contain_known_positions(self):
        """Test that players contain all expected hockey positions."""
        players = self.client.players(active_only=True)

        positions = {player._data.get("position") for player in players}
        expected_positions = {
            "C",
            "L",
            "R",
            "D",
            "G",
        }  # Center, Left Wing, Right Wing, Defense, Goalie

        assert expected_positions.issubset(
            positions
        ), f"Expected to find all positions {expected_positions}, found {positions}"

    @pytest.mark.parametrize("active_only", [True, False])
    def test_players_method_no_exceptions(self, active_only):
        """Test that players() method doesn't raise exceptions for both parameter values."""
        try:
            players = self.client.players(active_only=active_only)
            assert isinstance(players, list), "Should return a list"
            assert len(players) > 0, "Should return some players"
        except Exception as e:
            pytest.fail(f"players(active_only={active_only}) raised an exception: {e}")


class TestPlayersIntegration:
    """Integration tests for the players() method with real API calls."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.client = Edgework()

    def test_players_data_consistency(self):
        """Test that player data is consistent across multiple calls."""
        players1 = self.client.players(active_only=True)
        players2 = self.client.players(active_only=True)

        # Results should be consistent
        assert len(players1) == len(
            players2
        ), "Multiple calls should return same number of players"

        # Convert to sets of player IDs for comparison
        ids1 = {p._data.get("player_id") for p in players1}
        ids2 = {p._data.get("player_id") for p in players2}

        assert ids1 == ids2, "Multiple calls should return same players"

    def test_players_team_data_presence(self):
        """Test that active players have team information."""
        players = self.client.players(active_only=True)

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
