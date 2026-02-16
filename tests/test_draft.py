"""Tests for the draft module."""

from unittest.mock import Mock

import pytest

from edgework.clients.draft_client import DraftClient
from edgework.http_client import HttpClient
from edgework.models.draft import Draft, Draftee, DraftRanking


class TestDraftee:
    """Test class for Draftee model."""

    def test_draftee_init(self):
        """Test Draftee initialization."""
        data = {
            "player_id": 8478402,
            "first_name": "Connor",
            "last_name": "McDavid",
            "position": "C",
            "year": 2015,
            "round": 1,
            "overall_pick": 1,
            "team_abbrev": "EDM",
        }
        draftee = Draftee(**data)

        assert draftee.player_id == 8478402
        assert draftee.first_name == "Connor"
        assert draftee.last_name == "McDavid"
        assert draftee.full_name == "Connor McDavid"
        assert draftee.position == "C"
        assert draftee.year == 2015
        assert draftee.round == 1
        assert draftee.overall_pick == 1
        assert draftee.team_abbrev == "EDM"

    def test_draftee_defaults(self):
        """Test Draftee default values."""
        draftee = Draftee()

        assert draftee.first_name == ""
        assert draftee.last_name == ""
        assert draftee.full_name == ""
        assert draftee.position == ""
        assert draftee.team_abbrev == ""

    def test_draftee_str(self):
        """Test Draftee string representation."""
        draftee = Draftee(
            first_name="Connor",
            last_name="McDavid",
            year=2015,
            overall_pick=1,
        )
        str_repr = str(draftee)

        assert "Connor McDavid" in str_repr
        assert "2015" in str_repr
        assert "#1" in str_repr


class TestDraftRanking:
    """Test class for DraftRanking model."""

    def test_draft_ranking_init(self):
        """Test DraftRanking initialization."""
        rankings_data = [
            {
                "id": 1,
                "firstName": {"default": "John"},
                "lastName": {"default": "Doe"},
                "position": "C",
            },
            {
                "id": 2,
                "firstName": {"default": "Jane"},
                "lastName": {"default": "Smith"},
                "position": "D",
            },
        ]
        ranking = DraftRanking(rankings=rankings_data)

        assert len(ranking) == 2
        assert len(ranking.rankings) == 2

    def test_draft_ranking_prospects(self):
        """Test getting prospects as Draftee objects."""
        rankings_data = [
            {
                "id": 1,
                "firstName": {"default": "John"},
                "lastName": {"default": "Doe"},
                "position": "C",
            },
        ]
        ranking = DraftRanking(rankings=rankings_data)
        prospects = ranking.get_prospects()

        assert len(prospects) == 1
        assert prospects[0].first_name == "John"
        assert prospects[0].position == "C"

    def test_draft_ranking_top_prospects(self):
        """Test getting top prospects."""
        rankings_data = [
            {
                "id": 1,
                "firstName": {"default": "Rank1"},
                "lastName": {"default": "Player"},
                "position": "C",
            },
            {
                "id": 2,
                "firstName": {"default": "Rank2"},
                "lastName": {"default": "Player"},
                "position": "D",
            },
            {
                "id": 3,
                "firstName": {"default": "Rank3"},
                "lastName": {"default": "Player"},
                "position": "G",
            },
        ]
        ranking = DraftRanking(rankings=rankings_data)
        top = ranking.get_top_prospects(n=2)

        assert len(top) == 2

    def test_draft_ranking_get_by_rank(self):
        """Test getting prospect by rank."""
        rankings_data = [
            {
                "id": 1,
                "firstName": {"default": "First"},
                "lastName": {"default": "Pick"},
                "position": "C",
            },
        ]
        ranking = DraftRanking(rankings=rankings_data)
        prospect = ranking.get_prospect_by_rank(1)

        assert prospect is not None
        assert prospect.first_name == "First"

        # Out of range
        assert ranking.get_prospect_by_rank(99) is None

    def test_draft_ranking_iteration(self):
        """Test DraftRanking iteration."""
        rankings_data = [
            {
                "id": 1,
                "firstName": {"default": "Player1"},
                "lastName": {"default": "Name"},
                "position": "C",
            },
            {
                "id": 2,
                "firstName": {"default": "Player2"},
                "lastName": {"default": "Name"},
                "position": "D",
            },
        ]
        ranking = DraftRanking(rankings=rankings_data)
        # Iteration uses get_prospects() internally
        prospects = list(ranking)

        assert len(prospects) == 2


class TestDraft:
    """Test class for Draft model."""

    def test_draft_init(self):
        """Test Draft initialization."""
        picks_data = [
            {
                "playerId": 1,
                "firstName": "John",
                "lastName": "Doe",
                "round": 1,
                "overallPick": 1,
            },
            {
                "playerId": 2,
                "firstName": "Jane",
                "lastName": "Smith",
                "round": 1,
                "overallPick": 2,
            },
        ]
        draft = Draft(year=2024, picks=picks_data)

        assert draft.year == 2024
        assert draft.total_picks == 2
        assert len(draft.get_picks()) == 2

    def test_draft_get_picks_by_round(self):
        """Test filtering picks by round."""
        picks_data = [
            {
                "playerId": 1,
                "firstName": "R1",
                "lastName": "P1",
                "round": 1,
                "overallPick": 1,
            },
            {
                "playerId": 2,
                "firstName": "R2",
                "lastName": "P1",
                "round": 2,
                "overallPick": 33,
            },
        ]
        draft = Draft(picks=picks_data)
        round1 = draft.get_picks_by_round(1)

        assert len(round1) == 1
        assert round1[0].round == 1

    def test_draft_get_picks_by_team(self):
        """Test filtering picks by team."""
        picks_data = [
            {
                "playerId": 1,
                "firstName": "TOR",
                "lastName": "Pick",
                "round": 1,
                "teamAbbrev": "TOR",
            },
            {
                "playerId": 2,
                "firstName": "NYR",
                "lastName": "Pick",
                "round": 1,
                "teamAbbrev": "NYR",
            },
        ]
        draft = Draft(picks=picks_data)
        tor_picks = draft.get_picks_by_team("TOR")

        assert len(tor_picks) == 1
        assert tor_picks[0].team_abbrev == "TOR"

    def test_draft_get_pick_by_overall(self):
        """Test getting pick by overall number."""
        picks_data = [
            {"playerId": 1, "firstName": "First", "lastName": "Pick", "overallPick": 1},
            {
                "playerId": 2,
                "firstName": "Second",
                "lastName": "Pick",
                "overallPick": 2,
            },
        ]
        draft = Draft(picks=picks_data)
        pick = draft.get_pick_by_overall(1)

        assert pick is not None
        assert pick.overall_pick == 1
        assert pick.first_name == "First"

        # Not found
        assert draft.get_pick_by_overall(999) is None

    def test_draft_iteration(self):
        """Test Draft iteration."""
        picks_data = [
            {"playerId": 1, "firstName": "P1", "lastName": "Name"},
            {"playerId": 2, "firstName": "P2", "lastName": "Name"},
        ]
        draft = Draft(picks=picks_data)
        picks = list(draft)

        assert len(picks) == 2


class TestDraftClient:
    """Test class for DraftClient."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock HTTP client."""
        return Mock(spec=HttpClient)

    @pytest.fixture
    def mock_draft_picks_response(self):
        """Create a mock API response for draft picks."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {
            "draftYear": 2024,
            "rounds": [{"round": 1}, {"round": 2}],
            "picks": [
                {
                    "playerId": 1,
                    "firstName": "Connor",
                    "lastName": "McDavid",
                    "round": 1,
                    "overallPick": 1,
                    "teamAbbrev": "EDM",
                },
                {
                    "playerId": 2,
                    "firstName": "Jack",
                    "lastName": "Eichel",
                    "round": 1,
                    "overallPick": 2,
                    "teamAbbrev": "BUF",
                },
            ],
        }
        return response

    @pytest.fixture
    def mock_rankings_response(self):
        """Create a mock API response for draft rankings."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {
            "rankings": [
                {
                    "id": 1,
                    "firstName": {"default": "Top"},
                    "lastName": {"default": "Prospect"},
                    "position": "C",
                },
                {
                    "id": 2,
                    "firstName": {"default": "Second"},
                    "lastName": {"default": "Best"},
                    "position": "D",
                },
            ],
            "lastUpdated": "2024-01-01T00:00:00Z",
        }
        return response

    def test_client_init(self, mock_client):
        """Test DraftClient initialization."""
        client = DraftClient(mock_client)
        assert client._client == mock_client

    def test_get_draft_picks_current(self, mock_client, mock_draft_picks_response):
        """Test fetching current draft picks."""
        mock_client.get.return_value = mock_draft_picks_response
        client = DraftClient(mock_client)

        draft = client.get_draft_picks()

        assert draft.year == 2024
        assert draft.total_picks == 2
        mock_client.get.assert_called_with("draft/picks/now", web=True, params={})

    def test_get_draft_picks_for_season(self, mock_client, mock_draft_picks_response):
        """Test fetching draft picks for specific season."""
        mock_client.get.return_value = mock_draft_picks_response
        client = DraftClient(mock_client)

        draft = client.get_draft_picks(season="2023-2024")

        mock_client.get.assert_called_with(
            "draft/picks/20232024/all", web=True, params={}
        )

    def test_get_draft_picks_invalid_season(self, mock_client):
        """Test invalid season format."""
        client = DraftClient(mock_client)
        with pytest.raises(ValueError):
            client.get_draft_picks(season="invalid")

    def test_get_draft_rankings_current(self, mock_client, mock_rankings_response):
        """Test fetching current draft rankings."""
        mock_client.get.return_value = mock_rankings_response
        client = DraftClient(mock_client)

        rankings = client.get_draft_rankings()

        assert len(rankings) == 2
        mock_client.get.assert_called_with("draft/rankings/now", web=True, params={})

    def test_get_draft_rankings_for_season(self, mock_client, mock_rankings_response):
        """Test fetching draft rankings for specific season."""
        mock_client.get.return_value = mock_rankings_response
        client = DraftClient(mock_client)

        rankings = client.get_draft_rankings(season="2024-2025")

        mock_client.get.assert_called_with(
            "draft/rankings/20242025/all", web=True, params={}
        )

    def test_get_draft_tracker_picks(self, mock_client):
        """Test fetching draft tracker picks."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"picks": [{"pick": 1}, {"pick": 2}]}
        mock_client.get.return_value = response

        client = DraftClient(mock_client)
        picks = client.get_draft_tracker_picks()

        assert len(picks) == 2
        mock_client.get.assert_called_with(
            "draft-tracker/picks/now", web=True, params={}
        )


class TestDraftLiveAPI:
    """Live API tests for draft."""

    @pytest.fixture
    def real_client(self):
        """Create a real HTTP client."""
        return HttpClient()

    @pytest.mark.live_api
    def test_get_current_draft_picks(self, real_client):
        """Test fetching current draft picks from NHL API."""
        client = DraftClient(real_client)
        draft = client.get_draft_picks()

        assert draft.year is not None
        picks = draft.get_picks()
        assert len(picks) > 0

        # Check first pick has required fields
        first_pick = picks[0]
        assert first_pick.overall_pick is not None
        assert first_pick.first_name
        assert first_pick.last_name

    @pytest.mark.live_api
    def test_get_draft_rankings(self, real_client):
        """Test fetching draft rankings from NHL API."""
        client = DraftClient(real_client)
        rankings = client.get_draft_rankings()

        assert len(rankings.rankings) > 0

        # Check first ranked prospect
        top_prospects = rankings.get_top_prospects(5)
        assert len(top_prospects) <= 5

    @pytest.mark.live_api
    def test_get_draftee_info(self, real_client):
        """Test fetching draftee information for a known player."""
        client = DraftClient(real_client)
        # Connor McDavid (2015 #1 overall)
        draftee = client.get_draftee(8478402)

        if draftee:
            assert draftee.player_id == 8478402
            assert draftee.year == 2015
            assert draftee.overall_pick == 1
