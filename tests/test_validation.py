"""
Pytest tests for the stats validation functions.
This file tests all the validation helper functions in the stats module.
"""

from datetime import datetime

import pytest

from edgework.models.stats import (
    validate_game_type,
    validate_limit_and_start,
    validate_report_type,
    validate_season,
    validate_sort_direction,
)
from edgework.utilities import validate_season_format


class TestValidateSortDirection:
    """Test class for validate_sort_direction function."""

    @staticmethod
    def test_valid_single_sort():
        """Test valid single sort and direction."""
        result = validate_sort_direction("points", "DESC")
        expected = {"property": "points", "direction": "DESC"}
        assert result == expected

    @staticmethod
    def test_valid_single_sort_asc():
        """Test valid single sort with ASC direction."""
        result = validate_sort_direction("goals", "ASC")
        expected = {"property": "goals", "direction": "ASC"}
        assert result == expected

    @staticmethod
    def test_valid_multiple_sort():
        """Test valid multiple sort and directions."""
        result = validate_sort_direction(["points", "goals"], ["DESC", "ASC"])
        expected = [
            {"property": "points", "direction": "DESC"},
            {"property": "goals", "direction": "ASC"},
        ]
        assert result == expected

    @staticmethod
    def test_invalid_direction():
        """Test invalid direction raises ValueError."""
        with pytest.raises(
            ValueError, match="Direction must be either 'ASC' or 'DESC'"
        ):
            validate_sort_direction("points", "INVALID")

    @staticmethod
    def test_mismatched_list_lengths():
        """Test mismatched list lengths raises ValueError."""
        with pytest.raises(
            ValueError, match="Sort and direction lists must be of the same length"
        ):
            validate_sort_direction(["points", "goals"], ["DESC"])

    @staticmethod
    def test_empty_lists():
        """Test empty lists raise ValueError."""
        with pytest.raises(
            ValueError, match="Sort and direction lists cannot be empty"
        ):
            validate_sort_direction([], [])

    @staticmethod
    def test_mixed_types_string_and_list():
        """Test mixed types (string and list) raise ValueError."""
        with pytest.raises(
            ValueError,
            match="Sort and direction must be either both strings or both lists",
        ):
            validate_sort_direction("points", ["DESC"])

    @staticmethod
    def test_mixed_types_list_and_string():
        """Test mixed types (list and string) raise ValueError."""
        with pytest.raises(
            ValueError,
            match="Sort and direction must be either both strings or both lists",
        ):
            validate_sort_direction(["points"], "DESC")

    @staticmethod
    def test_non_string_in_sort_list():
        """Test non-string values in sort list raise ValueError."""
        with pytest.raises(
            ValueError, match="Sort must be a string or a list of strings"
        ):
            validate_sort_direction([123, "goals"], ["DESC", "ASC"])

    @staticmethod
    def test_non_string_in_direction_list():
        """Test non-string values in direction list raise ValueError."""
        with pytest.raises(
            ValueError, match="Direction must be a string or a list of strings"
        ):
            validate_sort_direction(["points", "goals"], ["DESC", 123])

    @staticmethod
    def test_invalid_direction_in_list():
        """Test invalid direction in list raises ValueError."""
        with pytest.raises(
            ValueError, match="Direction must be either 'ASC' or 'DESC'"
        ):
            validate_sort_direction(["points", "goals"], ["DESC", "INVALID"])


class TestValidateSeason:
    """Test class for validate_season function."""

    @staticmethod
    def test_auto_calculated_season_july_onwards():
        """Test auto-calculated season when current month is July or later."""
        # Mock the current date to be in July (season starts prep)
        result = validate_season(None)
        # Should be current year + next year (e.g., 2024-2025 = 20242025)
        current_year = datetime.now().year
        if datetime.now().month >= 7:
            expected = current_year * 10000 + (current_year + 1)
        else:
            expected = (current_year - 1) * 10000 + current_year
        assert result == expected

    @staticmethod
    def test_valid_manual_season():
        """Test valid manual season."""
        result = validate_season(20232024)
        assert result == 20232024

    @staticmethod
    def test_valid_historical_season():
        """Test valid historical season."""
        result = validate_season(19171918)  # First NHL season
        assert result == 19171918

    @staticmethod
    def test_invalid_season_too_short():
        """Test invalid season format (too short) raises ValueError."""
        with pytest.raises(
            ValueError,
            match="Season must be in format YYYYZZZZ.*and within valid NHL history",
        ):
            validate_season(2023)

    @staticmethod
    def test_invalid_season_wrong_year_sequence():
        """Test invalid season with wrong year sequence raises ValueError."""
        with pytest.raises(
            ValueError,
            match="Season must follow format YYYYZZZZ where ZZZZ = YYYY \\+ 1",
        ):
            validate_season(20232025)  # Should be 20232024

    @staticmethod
    def test_invalid_season_too_old():
        """Test season too old raises ValueError."""
        with pytest.raises(
            ValueError,
            match="Season must be in format YYYYZZZZ.*within valid NHL history",
        ):
            validate_season(19001901)

    @staticmethod
    def test_invalid_season_too_future():
        """Test season too far in future raises ValueError."""
        with pytest.raises(
            ValueError,
            match="Season must be in format YYYYZZZZ.*and within valid NHL history",
        ):
            validate_season(21102111)  # Well beyond the valid range

    @staticmethod
    def test_non_integer_season():
        """Test non-integer season raises ValueError."""
        with pytest.raises(ValueError, match="Season must be an integer.*or None"):
            validate_season("20232024")


class TestValidateGameType:
    """Test class for validate_game_type function."""

    @staticmethod
    def test_none_game_type():
        """Test None game type returns empty string."""
        result = validate_game_type(None)
        assert result == ""

    @staticmethod
    def test_regular_season_game_type():
        """Test regular season game type."""
        result = validate_game_type(2)
        assert result == " and gameTypeId=2"

    @staticmethod
    def test_playoffs_game_type():
        """Test playoffs game type."""
        result = validate_game_type(3)
        assert result == " and gameTypeId=3"

    @staticmethod
    def test_invalid_game_type_number():
        """Test invalid game type number raises ValueError."""
        with pytest.raises(ValueError, match="Game type must be either 2.*or 3"):
            validate_game_type(1)

    @staticmethod
    def test_invalid_game_type_high_number():
        """Test invalid high game type number raises ValueError."""
        with pytest.raises(ValueError, match="Game type must be either 2.*or 3"):
            validate_game_type(5)

    @staticmethod
    def test_non_integer_game_type():
        """Test non-integer game type raises ValueError."""
        with pytest.raises(ValueError, match="Game type must be an integer or None"):
            validate_game_type("2")


class TestValidateReportType:
    """Test class for validate_report_type function."""

    @staticmethod
    def test_valid_skater_report():
        """Test valid skater report type."""
        valid_reports = ["summary", "bios", "faceoffpercentages"]
        result = validate_report_type("summary", valid_reports)
        assert result == "summary"

    @staticmethod
    def test_valid_goalie_report():
        """Test valid goalie report type."""
        valid_reports = ["summary", "advanced", "savesByStrength"]
        result = validate_report_type("advanced", valid_reports)
        assert result == "advanced"

    @staticmethod
    def test_valid_team_report():
        """Test valid team report type."""
        valid_reports = ["summary", "faceoffpercentages", "powerPlay"]
        result = validate_report_type("powerPlay", valid_reports)
        assert result == "powerPlay"

    @staticmethod
    def test_invalid_report_for_context():
        """Test invalid report for given context raises ValueError."""
        valid_skater_reports = ["summary", "bios", "faceoffpercentages"]
        with pytest.raises(
            ValueError, match="Report must be one of: summary, bios, faceoffpercentages"
        ):
            validate_report_type("advanced", valid_skater_reports)

    @staticmethod
    def test_non_string_report():
        """Test non-string report raises ValueError."""
        valid_reports = ["summary", "bios"]
        with pytest.raises(ValueError, match="Report must be a string"):
            validate_report_type(123, valid_reports)

    @staticmethod
    def test_empty_report():
        """Test empty report string raises ValueError."""
        valid_reports = ["summary", "bios"]
        with pytest.raises(ValueError, match="Report must be one of"):
            validate_report_type("", valid_reports)


class TestValidateLimitAndStart:
    """Test class for validate_limit_and_start function."""

    @staticmethod
    def test_valid_all_records():
        """Test valid 'all records' parameters."""
        limit, start = validate_limit_and_start(-1, 0)
        assert limit == -1
        assert start == 0

    @staticmethod
    def test_valid_limited_records():
        """Test valid limited records parameters."""
        limit, start = validate_limit_and_start(100, 25)
        assert limit == 100
        assert start == 25

    @staticmethod
    def test_valid_large_numbers():
        """Test valid large numbers."""
        limit, start = validate_limit_and_start(1000, 500)
        assert limit == 1000
        assert start == 500

    @staticmethod
    def test_invalid_limit_zero():
        """Test invalid limit (zero) raises ValueError."""
        with pytest.raises(ValueError, match="Limit must be -1.*or a positive integer"):
            validate_limit_and_start(0, 0)

    @staticmethod
    def test_invalid_limit_negative_not_minus_one():
        """Test invalid negative limit (not -1) raises ValueError."""
        with pytest.raises(ValueError, match="Limit must be -1.*or a positive integer"):
            validate_limit_and_start(-5, 0)

    @staticmethod
    def test_invalid_start_negative():
        """Test invalid negative start raises ValueError."""
        with pytest.raises(ValueError, match="Start must be a non-negative integer"):
            validate_limit_and_start(100, -1)

    @staticmethod
    def test_non_integer_limit():
        """Test non-integer limit raises ValueError."""
        with pytest.raises(ValueError, match="Limit must be an integer"):
            validate_limit_and_start("100", 0)

    @staticmethod
    def test_non_integer_start():
        """Test non-integer start raises ValueError."""
        with pytest.raises(ValueError, match="Start must be an integer"):
            validate_limit_and_start(100, "0")

    @staticmethod
    def test_float_limit():
        """Test float limit raises ValueError."""
        with pytest.raises(ValueError, match="Limit must be an integer"):
            validate_limit_and_start(100.5, 0)

    @staticmethod
    def test_float_start():
        """Test float start raises ValueError."""
        with pytest.raises(ValueError, match="Start must be an integer"):
            validate_limit_and_start(100, 0.5)


class TestValidationIntegration:
    """Integration tests for validation functions working together."""

    @staticmethod
    def test_typical_skater_stats_parameters():
        """Test typical parameters used for skater stats."""
        # These should all work without raising exceptions
        sort_result = validate_sort_direction("points", "DESC")
        season_result = validate_season(20232024)
        game_type_result = validate_game_type(2)
        report_result = validate_report_type("summary", ["summary", "bios", "advanced"])
        limit_result, start_result = validate_limit_and_start(50, 0)

        assert sort_result == {"property": "points", "direction": "DESC"}
        assert season_result == 20232024
        assert game_type_result == " and gameTypeId=2"
        assert report_result == "summary"
        assert limit_result == 50
        assert start_result == 0

    @staticmethod
    def test_typical_goalie_stats_parameters():
        """Test typical parameters used for goalie stats."""
        sort_result = validate_sort_direction(["wins", "saves"], ["DESC", "DESC"])
        season_result = validate_season(None)  # Auto-calculate
        game_type_result = validate_game_type(3)  # Playoffs
        report_result = validate_report_type(
            "advanced", ["summary", "advanced", "savesByStrength"]
        )
        limit_result, start_result = validate_limit_and_start(-1, 0)  # All records

        assert isinstance(sort_result, list)
        assert len(sort_result) == 2
        assert sort_result[0] == {"property": "wins", "direction": "DESC"}
        assert sort_result[1] == {"property": "saves", "direction": "DESC"}
        assert isinstance(season_result, int)
        assert game_type_result == " and gameTypeId=3"
        assert report_result == "advanced"
        assert limit_result == -1
        assert start_result == 0

    @staticmethod
    def test_edge_case_parameters():
        """Test edge case parameters."""
        # Minimum valid season
        season_result = validate_season(19171918)
        assert season_result == 19171918

        # Single character sort field
        sort_result = validate_sort_direction("g", "ASC")  # goals shortened
        assert sort_result == {"property": "g", "direction": "ASC"}

        # Large pagination
        limit_result, start_result = validate_limit_and_start(10000, 5000)
        assert limit_result == 10000
        assert start_result == 5000


class TestSeasonFormatHelper:
    """Tests for the shared season-normalization helper (Task 2).

    ``edgework.utilities.validate_season_format`` is the single source of
    truth for ``YYYY-YYYY`` -> ``YYYYYYYY`` conversion; the facade re-exports
    it as ``edgework.edgework._validate_season_format`` for backward
    compatibility.
    """

    @staticmethod
    def test_facade_reexports_the_shared_helper():
        """The facade must not keep its own inline implementation."""
        from edgework.edgework import _validate_season_format

        assert _validate_season_format is validate_season_format

    @pytest.mark.parametrize(
        "season_str,expected_int",
        [
            ("2023-2024", 20232024),
            ("2022-2023", 20222023),
            ("1999-2000", 19992000),
            ("1917-1918", 19171918),
        ],
    )
    @staticmethod
    def test_valid_season_strings_convert_to_integer(season_str, expected_int):
        """Valid 'YYYY-YYYY' strings convert to the YYYYYYYY integer format."""
        assert validate_season_format(season_str) == expected_int

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
            "2022-2024",
        ],
    )
    @staticmethod
    def test_invalid_season_strings_raise_value_error(invalid_season):
        """Malformed or non-consecutive seasons are rejected."""
        with pytest.raises(ValueError, match="Invalid season format"):
            validate_season_format(invalid_season)

    @staticmethod
    def test_non_string_seasons_raise_value_error():
        """Non-string inputs (e.g. ints) are rejected."""
        with pytest.raises(ValueError, match="Invalid season format"):
            validate_season_format(20232024)

    @staticmethod
    def test_team_client_uses_shared_helper():
        """TeamClient normalizes 'YYYY-YYYY' seasons through this helper."""
        from unittest.mock import Mock

        from edgework.clients.team_client import TeamClient

        team_client = TeamClient(Mock())
        with pytest.raises(ValueError, match="Invalid season format"):
            team_client.get_roster("TOR", "not-a-season")
