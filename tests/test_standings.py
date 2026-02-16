"""Tests for the standings module."""

from datetime import datetime
from unittest.mock import Mock

import pytest

from edgework.clients.standings_client import StandingClient
from edgework.http_client import HttpClient
from edgework.models.standings import Seeding, Standings


class TestSeeding:
    """Test class for Seeding model."""

    def test_seeding_init_with_data(self):
        """Test Seeding initialization with team data."""
        data = {
            "conference_abbrev": "E",
            "conference_name": "Eastern",
            "division_abbrev": "ATL",
            "division_name": "Atlantic",
            "team_abbrev": "TOR",
            "team_name": {"default": "Toronto Maple Leafs"},
            "games_played": 82,
            "wins": 45,
            "losses": 25,
            "ot_losses": 12,
            "points": 102,
            "goal_differential": 40,
            "conference_sequence": 3,
            "wildcard_sequence": 0,
            "clinch_indicator": "x",
        }
        seeding = Seeding(**data)

        assert seeding.conference_abbrev == "E"
        assert seeding.team_abbrev == "TOR"
        assert seeding.points == 102
        assert seeding.wins == 45
        assert seeding.is_clinched is True
        assert seeding.is_in_playoffs is True

    def test_seeding_default_values(self):
        """Test Seeding default values when data is missing."""
        seeding = Seeding()

        assert seeding.conference_abbrev == ""
        assert seeding.team_abbrev == ""
        assert seeding.points == 0
        assert seeding.wins == 0
        assert seeding.is_clinched is False
        assert seeding.is_in_playoffs is False

    def test_seeding_str(self):
        """Test Seeding string representation."""
        data = {
            "team_abbrev": "TOR",
            "points": 102,
            "wins": 45,
            "losses": 25,
            "ot_losses": 12,
        }
        seeding = Seeding(**data)
        str_repr = str(seeding)

        assert "TOR" in str_repr
        assert "102" in str_repr

    def test_seeding_fetch_data_raises(self):
        """Test that fetch_data raises NotImplementedError."""
        seeding = Seeding()
        with pytest.raises(NotImplementedError):
            seeding.fetch_data()


class TestStandings:
    """Test class for Standings model."""

    def test_standings_init(self):
        """Test Standings initialization."""
        date = datetime(2024, 1, 15)
        seedings = [
            Seeding(team_abbrev="TOR", points=102, conference_abbrev="E"),
            Seeding(team_abbrev="NYR", points=98, conference_abbrev="E"),
            Seeding(team_abbrev="EDM", points=95, conference_abbrev="W"),
        ]
        standings = Standings(date=date, seedings=seedings, season=20232024)

        assert standings.date == date
        assert len(standings) == 3
        assert standings.season == 20232024

    def test_standings_east_standings(self):
        """Test filtering Eastern Conference standings."""
        seedings = [
            Seeding(team_abbrev="TOR", points=102, conference_abbrev="E"),
            Seeding(team_abbrev="NYR", points=98, conference_abbrev="E"),
            Seeding(team_abbrev="EDM", points=95, conference_abbrev="W"),
        ]
        standings = Standings(seedings=seedings)
        east = standings.east_standings

        assert len(east) == 2
        assert all(s.conference_abbrev == "E" for s in east)

    def test_standings_west_standings(self):
        """Test filtering Western Conference standings."""
        seedings = [
            Seeding(team_abbrev="TOR", points=102, conference_abbrev="E"),
            Seeding(team_abbrev="EDM", points=95, conference_abbrev="W"),
            Seeding(team_abbrev="COL", points=92, conference_abbrev="W"),
        ]
        standings = Standings(seedings=seedings)
        west = standings.west_standings

        assert len(west) == 2
        assert all(s.conference_abbrev == "W" for s in west)

    def test_standings_get_team_standing(self):
        """Test getting a specific team standing."""
        seedings = [
            Seeding(team_abbrev="TOR", points=102),
            Seeding(team_abbrev="NYR", points=98),
        ]
        standings = Standings(seedings=seedings)
        team = standings.get_team_standing("TOR")

        assert team is not None
        assert team.team_abbrev == "TOR"
        assert team.points == 102

    def test_standings_get_team_standing_not_found(self):
        """Test getting a team that doesn't exist."""
        seedings = [Seeding(team_abbrev="TOR", points=102)]
        standings = Standings(seedings=seedings)
        team = standings.get_team_standing("XYZ")

        assert team is None

    def test_standings_get_division_standings(self):
        """Test filtering by division."""
        seedings = [
            Seeding(team_abbrev="TOR", points=102, division_abbrev="ATL"),
            Seeding(team_abbrev="BOS", points=98, division_abbrev="ATL"),
            Seeding(team_abbrev="NYR", points=95, division_abbrev="MET"),
        ]
        standings = Standings(seedings=seedings)
        atlantic = standings.get_division_standings("ATL")

        assert len(atlantic) == 2
        assert all(s.division_abbrev == "ATL" for s in atlantic)

    def test_standings_iteration(self):
        """Test that Standings is iterable."""
        seedings = [
            Seeding(team_abbrev="TOR", points=102),
            Seeding(team_abbrev="NYR", points=98),
        ]
        standings = Standings(seedings=seedings)

        teams = list(standings)
        assert len(teams) == 2

    def test_standings_str(self):
        """Test Standings string representation."""
        date = datetime(2024, 1, 15)
        seedings = [Seeding(team_abbrev="TOR", points=102)]
        standings = Standings(date=date, seedings=seedings)
        str_repr = str(standings)

        assert "NHL Standings" in str_repr
        assert "2024-01-15" in str_repr
        assert "1 teams" in str_repr

    def test_standings_fetch_data_raises(self):
        """Test that fetch_data raises NotImplementedError."""
        standings = Standings()
        with pytest.raises(NotImplementedError):
            standings.fetch_data()


class TestStandingClient:
    """Test class for StandingClient."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock HTTP client."""
        return Mock(spec=HttpClient)

    @pytest.fixture
    def mock_standings_response(self):
        """Create a mock API response for standings."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {
            "standings": [
                {
                    "conferenceAbbrev": "E",
                    "conferenceName": "Eastern",
                    "divisionAbbrev": "ATL",
                    "teamAbbrev": "TOR",
                    "teamName": {"default": "Toronto Maple Leafs"},
                    "gamesPlayed": 82,
                    "wins": 45,
                    "losses": 25,
                    "otLosses": 12,
                    "points": 102,
                },
                {
                    "conferenceAbbrev": "W",
                    "conferenceName": "Western",
                    "divisionAbbrev": "PAC",
                    "teamAbbrev": "EDM",
                    "teamName": {"default": "Edmonton Oilers"},
                    "gamesPlayed": 82,
                    "wins": 42,
                    "losses": 28,
                    "otLosses": 12,
                    "points": 96,
                },
            ]
        }
        return response

    def test_client_init(self, mock_client):
        """Test StandingClient initialization."""
        client = StandingClient(mock_client)
        assert client._client == mock_client

    def test_validate_date_now(self, mock_client):
        """Test date validation with 'now'."""
        client = StandingClient(mock_client)
        assert client._validate_date("now") == "now"
        assert client._validate_date(None) == "now"

    def test_validate_date_datetime(self, mock_client):
        """Test date validation with datetime object."""
        client = StandingClient(mock_client)
        date = datetime(2024, 1, 15)
        assert client._validate_date(date) == "2024-01-15"

    def test_validate_date_string(self, mock_client):
        """Test date validation with valid string."""
        client = StandingClient(mock_client)
        assert client._validate_date("2024-01-15") == "2024-01-15"

    def test_validate_date_invalid_format(self, mock_client):
        """Test date validation with invalid format."""
        client = StandingClient(mock_client)
        with pytest.raises(ValueError):
            client._validate_date("2024-01-1")  # Too short
        with pytest.raises(ValueError):
            client._validate_date("2024/01/15")  # Wrong separator
        with pytest.raises(ValueError):
            client._validate_date("abcd-01-15")  # Non-numeric

    def test_get_standings(self, mock_client, mock_standings_response):
        """Test fetching current standings."""
        mock_client.get.return_value = mock_standings_response
        client = StandingClient(mock_client)

        standings = client.get_standings()

        assert len(standings) == 2
        assert standings.get_team_standing("TOR").points == 102
        assert standings.get_team_standing("EDM").points == 96

    def test_get_standings_for_date(self, mock_client, mock_standings_response):
        """Test fetching standings for specific date."""
        mock_client.get.return_value = mock_standings_response
        client = StandingClient(mock_client)

        standings = client.get_standings("2024-01-15")

        mock_client.get.assert_called_once()
        assert standings.date.strftime("%Y-%m-%d") == "2024-01-15"

    def test_get_standings_empty_response(self, mock_client):
        """Test fetching standings with empty response."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"standings": []}
        mock_client.get.return_value = response

        client = StandingClient(mock_client)
        standings = client.get_standings()

        assert len(standings) == 0


class TestStandingsLiveAPI:
    """Live API tests for standings."""

    @pytest.fixture
    def real_client(self):
        """Create a real HTTP client."""
        return HttpClient()

    @pytest.mark.live_api
    def test_get_standings_live(self, real_client):
        """Test fetching live standings from NHL API."""
        client = StandingClient(real_client)
        standings = client.get_standings()

        assert len(standings) > 0
        assert len(standings.seedings) > 0

        # Check that we have both conferences
        assert len(standings.east_standings) > 0
        assert len(standings.west_standings) > 0

        # Check first team has required fields
        first_team = standings.seedings[0]
        assert first_team.team_abbrev
        assert first_team.points is not None
        assert first_team.games_played is not None

    @pytest.mark.live_api
    def test_get_standings_for_specific_date(self, real_client):
        """Test fetching standings for a specific historical date."""
        client = StandingClient(real_client)
        standings = client.get_standings("2024-01-15")

        assert len(standings) > 0
        assert standings.date.strftime("%Y-%m-%d") == "2024-01-15"

    @pytest.mark.live_api
    def test_team_standing_filters(self, real_client):
        """Test filtering standings by conference and division."""
        client = StandingClient(real_client)
        standings = client.get_standings()

        # Test getting specific team
        team = standings.get_team_standing("TOR")
        if team:
            assert team.team_abbrev == "TOR"

        # Test division filtering
        atlantic = standings.get_division_standings("ATL")
        if atlantic:
            assert all(s.division_abbrev == "ATL" for s in atlantic)
