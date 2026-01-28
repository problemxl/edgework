"""Tests for schedule-related functionality in the Edgework client."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, Mock, patch

import pytest

from edgework.clients.schedule_client import ScheduleClient
from edgework.models.game import Game
from edgework.models.schedule import Schedule, schedule_api_to_dict


class TestScheduleApiToDict:
    """Test class for schedule_api_to_dict function."""

    def test_schedule_api_to_dict_basic(self):
        """Test schedule_api_to_dict with basic API data."""
        api_data = {
            "previousStartDate": "2024-06-01T00:00:00Z",
            "games": [{"id": 1}, {"id": 2}],
            "preSeasonStartDate": "2024-09-15T00:00:00Z",
            "regularSeasonStartDate": "2024-10-01T00:00:00Z",
            "regularSeasonEndDate": "2025-04-15T00:00:00Z",
            "playoffEndDate": "2025-06-30T00:00:00Z",
            "numberOfGames": 2,
        }

        result = schedule_api_to_dict(api_data)

        assert result["previous_start_date"] == "2024-06-01T00:00:00Z"
        assert result["games"] == [{"id": 1}, {"id": 2}]
        assert result["pre_season_start_date"] == "2024-09-15T00:00:00Z"
        assert result["regular_season_start_date"] == "2024-10-01T00:00:00Z"
        assert result["regular_season_end_date"] == "2025-04-15T00:00:00Z"
        assert result["playoff_end_date"] == "2025-06-30T00:00:00Z"
        assert result["number_of_games"] == 2

    def test_schedule_api_to_dict_with_game_week(self):
        """Test schedule_api_to_dict with gameWeek structure."""
        api_data = {
            "gameWeek": [{"games": [{"id": 1}, {"id": 2}]}, {"games": [{"id": 3}]}]
        }

        result = schedule_api_to_dict(api_data)

        assert result["games"] == [{"id": 1}, {"id": 2}, {"id": 3}]
        assert result["number_of_games"] == 3

    def test_schedule_api_to_dict_empty_data(self):
        """Test schedule_api_to_dict with empty data."""
        api_data = {}

        result = schedule_api_to_dict(api_data)

        assert result["games"] == []
        assert result["number_of_games"] == 0
        assert result["previous_start_date"] is None


class TestSchedule:
    """Test class for Schedule model."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_client = Mock()
        self.mock_http_client = Mock()
        self.mock_client.http_client = self.mock_http_client

    def test_schedule_init_basic(self):
        """Test Schedule initialization with basic data."""
        schedule = Schedule(self.mock_client, obj_id=123, games=[], number_of_games=0)

        assert schedule._client == self.mock_client
        assert schedule.obj_id == 123
        assert schedule._data["games"] == []
        assert schedule._data["number_of_games"] == 0
        assert schedule._fetched is True
        assert schedule._games_objects == []

    def test_schedule_init_without_games(self):
        """Test Schedule initialization without games data."""
        schedule = Schedule(self.mock_client)

        assert schedule._data["games"] == []
        # _fetched is False when no kwargs are provided
        assert schedule._fetched is False

    def test_schedule_str_with_dates(self):
        """Test Schedule string representation with dates."""
        schedule = Schedule(
            self.mock_client,
            number_of_games=82,
            regular_season_start_date="2024-10-01T00:00:00Z",
            regular_season_end_date="2025-04-15T00:00:00Z",
        )

        result = str(schedule)
        assert "Schedule (82 games): 2024-10-01 to 2025-04-15" == result

    def test_schedule_str_with_datetime_objects(self):
        """Test Schedule string representation with datetime objects."""
        start_date = datetime(2024, 10, 1, tzinfo=timezone.utc)
        end_date = datetime(2025, 4, 15, tzinfo=timezone.utc)

        schedule = Schedule(
            self.mock_client,
            number_of_games=82,
            regular_season_start_date=start_date,
            regular_season_end_date=end_date,
        )

        result = str(schedule)
        assert "Schedule (82 games): 2024-10-01 to 2025-04-15" == result

    def test_schedule_str_without_dates(self):
        """Test Schedule string representation without dates."""
        schedule = Schedule(self.mock_client, number_of_games=5)

        result = str(schedule)
        assert result == "Schedule (5 games)"

    def test_schedule_str_empty(self):
        """Test Schedule string representation with no data."""
        schedule = Schedule(self.mock_client)

        result = str(schedule)
        assert result == "Schedule"

    def test_schedule_repr(self):
        """Test Schedule repr representation."""
        schedule = Schedule(self.mock_client, games=[{"id": 1}, {"id": 2}])

        result = repr(schedule)
        assert result == "Schedule(games=2)"

    def test_from_dict_with_date_strings(self):
        """Test Schedule.from_dict with date strings."""
        data = {
            "regular_season_start_date": "2024-10-01T00:00:00Z",
            "regular_season_end_date": "2025-04-15T00:00:00Z",
            "games": [{"id": 1}],
            "number_of_games": 1,
        }

        schedule = Schedule.from_dict(self.mock_client, data)

        assert isinstance(schedule._data["regular_season_start_date"], datetime)
        assert isinstance(schedule._data["regular_season_end_date"], datetime)
        assert schedule._data["games"] == [{"id": 1}]
        assert schedule._data["number_of_games"] == 1

    def test_from_dict_with_datetime_objects(self):
        """Test Schedule.from_dict with datetime objects."""
        start_date = datetime(2024, 10, 1, tzinfo=timezone.utc)
        data = {
            "regular_season_start_date": start_date,
            "games": [],
            "number_of_games": 0,
        }

        schedule = Schedule.from_dict(self.mock_client, data)

        assert schedule._data["regular_season_start_date"] == start_date

    def test_from_dict_with_invalid_dates(self):
        """Test Schedule.from_dict with invalid date strings."""
        data = {
            "regular_season_start_date": "invalid-date",
            "games": [],
            "number_of_games": 0,
        }

        schedule = Schedule.from_dict(self.mock_client, data)

        assert schedule._data["regular_season_start_date"] == "invalid-date"

    def test_from_api(self):
        """Test Schedule.from_api method."""
        api_data = {
            "games": [{"id": 1}],
            "regularSeasonStartDate": "2024-10-01T00:00:00Z",
            "numberOfGames": 1,
        }

        schedule = Schedule.from_api(self.mock_client, api_data)

        assert len(schedule._data["games"]) == 1
        assert schedule._data["number_of_games"] == 1
        assert isinstance(schedule._data["regular_season_start_date"], datetime)

    def test_fetch_data_without_client(self):
        """Test fetch_data raises error without client."""
        schedule = Schedule(None)

        with pytest.raises(
            ValueError, match="No client available to fetch schedule data"
        ):
            schedule.fetch_data()

    def test_fetch_data_with_client(self):
        """Test fetch_data with client."""
        schedule = Schedule(self.mock_client)

        # Should raise NotImplementedError since fetch_data is not implemented
        with pytest.raises(NotImplementedError):
            schedule.fetch_data()

    @patch("edgework.models.game.Game")
    def test_games_property_with_client(self, mock_game_class):
        """Test games property with client creates Game objects."""
        mock_game = Mock()
        mock_game_class.from_api.return_value = mock_game

        game_data = {"id": 1, "gameState": "FINAL"}
        schedule = Schedule(self.mock_client, games=[game_data])

        games = schedule.games

        assert len(games) == 1
        assert games[0] == mock_game
        mock_game_class.from_api.assert_called_once_with(game_data, self.mock_client)

    def test_games_property_without_client(self):
        """Test games property without client returns empty list."""
        schedule = Schedule(None, games=[{"id": 1}])

        games = schedule.games

        assert games == []

    def test_games_property_no_games_data(self):
        """Test games property with no games data."""
        schedule = Schedule(self.mock_client)

        games = schedule.games

        assert games == []

    def test_games_property_cached(self):
        """Test games property uses cached objects."""
        schedule = Schedule(self.mock_client)
        mock_game = Mock()
        schedule._games_objects = [mock_game]

        games = schedule.games

        assert games == [mock_game]

    @patch("edgework.models.schedule.datetime")
    def test_games_today(self, mock_datetime):
        """Test games_today property."""
        # Mock current date
        mock_date = datetime(2024, 6, 1).date()
        mock_datetime.now.return_value.date.return_value = mock_date

        # Create mock games
        game_today = Mock()
        game_today._data = {"game_date": datetime(2024, 6, 1).date()}

        game_tomorrow = Mock()
        game_tomorrow._data = {"game_date": datetime(2024, 6, 2).date()}

        schedule = Schedule(self.mock_client)
        schedule._games_objects = [game_today, game_tomorrow]

        games_today = schedule.games_today

        assert len(games_today) == 1
        assert games_today[0] == game_today

    @patch("edgework.models.schedule.datetime")
    def test_upcoming_games(self, mock_datetime):
        """Test upcoming_games property."""
        # Mock current time
        mock_now = datetime(2024, 6, 1, 12, 0, 0)
        mock_datetime.now.return_value = mock_now

        # Create mock games
        past_game = Mock()
        past_game._data = {"start_time_utc": datetime(2024, 5, 31, 12, 0, 0)}

        future_game = Mock()
        future_game._data = {"start_time_utc": datetime(2024, 6, 2, 12, 0, 0)}

        schedule = Schedule(self.mock_client)
        schedule._games_objects = [past_game, future_game]

        upcoming_games = schedule.upcoming_games

        assert len(upcoming_games) == 1
        assert upcoming_games[0] == future_game

    def test_upcoming_games_missing_start_time(self):
        """Test upcoming_games property with missing start_time_utc."""
        # Create mock game without start_time_utc
        game_no_time = Mock()
        game_no_time._data = {}

        schedule = Schedule(self.mock_client)
        schedule._games_objects = [game_no_time]

        # Should not crash and return empty list (uses now as default)
        upcoming_games = schedule.upcoming_games

        assert len(upcoming_games) == 0

    def test_completed_games(self):
        """Test completed_games property."""
        # Create mock games with different states
        final_game = Mock()
        final_game._data = {"game_state": "FINAL"}

        off_game = Mock()
        off_game._data = {"game_state": "OFF"}

        live_game = Mock()
        live_game._data = {"game_state": "LIVE"}

        pre_game = Mock()
        pre_game._data = {"game_state": "PRE"}

        no_state_game = Mock()
        no_state_game._data = {}

        schedule = Schedule(self.mock_client)
        schedule._games_objects = [
            final_game,
            off_game,
            live_game,
            pre_game,
            no_state_game,
        ]

        completed_games = schedule.completed_games

        assert len(completed_games) == 2
        assert final_game in completed_games
        assert off_game in completed_games
        assert live_game not in completed_games
        assert pre_game not in completed_games
        assert no_state_game not in completed_games

    def test_completed_games_empty(self):
        """Test completed_games property with no completed games."""
        live_game = Mock()
        live_game._data = {"game_state": "LIVE"}

        schedule = Schedule(self.mock_client)
        schedule._games_objects = [live_game]

        completed_games = schedule.completed_games

        assert len(completed_games) == 0


class TestScheduleClient:
    """Test class for ScheduleClient methods."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_http_client = Mock()
        self.schedule_client = ScheduleClient(self.mock_http_client)

    @patch("edgework.clients.schedule_client.datetime")
    def test_get_schedule_for_date_range_uses_pagination(self, mock_datetime):
        """Test that get_schedule_for_date_range uses nextStartDate pagination."""
        from datetime import datetime as dt

        mock_datetime.fromisoformat.side_effect = lambda x: dt.fromisoformat(x)

        start_date = "2024-01-01"
        end_date = "2024-01-10"

        mock_response_1 = Mock()
        mock_response_1.json.return_value = {
            "gameWeek": [
                {
                    "games": [
                        {"id": 1, "gameDate": "2024-01-01T19:00:00"},
                        {"id": 2, "gameDate": "2024-01-02T19:00:00"},
                    ]
                }
            ],
            "nextStartDate": "2024-01-05",
            "previousStartDate": "2023-12-26",
            "preSeasonStartDate": "2023-09-21",
            "regularSeasonStartDate": "2023-10-10",
            "regularSeasonEndDate": "2024-04-17",
            "playoffEndDate": "2024-06-20",
        }

        mock_response_2 = Mock()
        mock_response_2.json.return_value = {
            "gameWeek": [
                {
                    "games": [
                        {"id": 2, "gameDate": "2024-01-02T19:00:00"},
                        {"id": 3, "gameDate": "2024-01-06T19:00:00"},
                    ]
                }
            ],
            "nextStartDate": "2024-01-12",
            "previousStartDate": "2024-01-01",
            "regularSeasonStartDate": "2023-10-10",
            "regularSeasonEndDate": "2024-04-17",
            "playoffEndDate": "2024-06-20",
        }

        mock_response_3 = Mock()
        mock_response_3.json.return_value = {
            "gameWeek": [{"games": [{"id": 4, "gameDate": "2024-01-12T19:00:00"}]}],
            "nextStartDate": None,
            "previousStartDate": "2024-01-06",
            "regularSeasonStartDate": "2023-10-10",
            "regularSeasonEndDate": "2024-04-17",
            "playoffEndDate": "2024-06-20",
        }

        self.mock_http_client.get.side_effect = [
            mock_response_1,
            mock_response_2,
            mock_response_3,
        ]

        schedule = self.schedule_client.get_schedule_for_date_range(
            start_date, end_date
        )

        game_ids = [g["id"] for g in schedule._data["games"]]

        assert len(game_ids) == 3
        assert 1 in game_ids
        assert 2 in game_ids
        assert 3 in game_ids

        assert game_ids.count(1) == 1
        assert game_ids.count(2) == 1
        assert game_ids.count(3) == 1

        assert self.mock_http_client.get.call_count == 2

    @patch("edgework.clients.schedule_client.datetime")
    def test_get_schedule_for_date_range_filters_by_date(self, mock_datetime):
        """Test that get_schedule_for_date_range filters games to requested date range."""
        from datetime import datetime as dt

        mock_datetime.fromisoformat.side_effect = lambda x: dt.fromisoformat(x)

        start_date = "2024-01-05"
        end_date = "2024-01-10"

        mock_response = Mock()
        mock_response.json.return_value = {
            "gameWeek": [
                {
                    "games": [
                        {"id": 1, "gameDate": "2024-01-01T19:00:00"},
                        {"id": 2, "gameDate": "2024-01-06T19:00:00"},
                        {"id": 3, "gameDate": "2024-01-12T19:00:00"},
                    ]
                }
            ],
            "nextStartDate": None,
            "previousStartDate": "2023-12-26",
            "regularSeasonStartDate": "2023-10-10",
            "regularSeasonEndDate": "2024-04-17",
        }

        self.mock_http_client.get.return_value = mock_response

        schedule = self.schedule_client.get_schedule_for_date_range(
            start_date, end_date
        )

        game_ids = [g["id"] for g in schedule._data["games"]]

        assert len(game_ids) == 1
        assert 2 in game_ids
        assert 1 not in game_ids
        assert 3 not in game_ids

    def test_get_schedule_for_date_range_invalid_date_format(self):
        """Test that get_schedule_for_date_range validates date format."""
        with pytest.raises(ValueError, match="Invalid date format"):
            self.schedule_client.get_schedule_for_date_range("2024/01/01", "2024-01-10")

        with pytest.raises(ValueError, match="Invalid date format"):
            self.schedule_client.get_schedule_for_date_range("2024-01-01", "2024/01/10")

    @patch("edgework.clients.schedule_client.datetime")
    def test_get_schedule_for_date_range_invalid_date_range(self, mock_datetime):
        """Test that get_schedule_for_date_range validates date range."""
        mock_datetime.fromisoformat.side_effect = lambda x: datetime.fromisoformat(x)

        with pytest.raises(ValueError, match="Start date cannot be after end date"):
            self.schedule_client.get_schedule_for_date_range("2024-01-10", "2024-01-01")


class TestScheduleIntegration:
    """Integration tests for Schedule with real Edgework client."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        from edgework.edgework import Edgework

        self.client = Edgework()

    @pytest.mark.integration
    def test_get_schedule_for_date_range_live_api(self):
        """Test get_schedule_for_date_range with live NHL API."""
        start_date = "2026-01-10"
        end_date = "2026-01-16"

        schedule = self.client.get_schedule_for_date_range(start_date, end_date)

        game_ids = [g.get("id") for g in schedule._data["games"]]

        unique_ids = set(game_ids)
        assert len(game_ids) == len(unique_ids), f"Found duplicate game IDs: {game_ids}"

        for game in schedule._data["games"]:
            game_date = game.get("startTimeUTC")
            if game_date:
                from datetime import datetime

                game_date_dt = datetime.fromisoformat(game_date.replace("Z", "+00:00"))
                start_dt = datetime.fromisoformat(start_date)
                end_dt = datetime.fromisoformat(end_date)
                assert start_dt <= game_date_dt.date() <= end_dt, (
                    f"Game {game.get('id')} at {game_date} outside range {start_date} to {end_date}"
                )

    @pytest.mark.integration
    def test_get_schedule_for_single_date(self):
        """Test get_schedule_for_date with live NHL API."""
        from datetime import datetime, timedelta

        test_date = "2026-01-12"
        schedule = self.client.get_schedule_for_date(test_date)

        game_ids = [g.get("id") for g in schedule._data["games"]]
        unique_ids = set(game_ids)

        assert len(game_ids) == len(unique_ids), f"Found duplicate game IDs: {game_ids}"

        test_date_dt = datetime.fromisoformat(test_date)

        for game in schedule._data["games"]:
            game_date_str = game.get("startTimeUTC")
            if game_date_str:
                game_date_dt = datetime.fromisoformat(
                    game_date_str.replace("Z", "+00:00")
                )

                date_diff = abs((game_date_dt.date() - test_date_dt.date()).days)
                assert date_diff <= 7, (
                    f"Game {game.get('id')} at {game_date_str} is {date_diff} days from {test_date}"
                )

    def test_schedule_creation_from_client(self):
        """Test creating Schedule objects through the client."""
        schedule = self.client.get_schedule()
        assert isinstance(schedule, Schedule)
