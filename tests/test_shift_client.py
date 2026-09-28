"""Mocked tests for the canonical ShiftClient shiftcharts wrapper (Task 3).

Covers the route/query builder, the raw escape hatch, delegation from
``GameClient`` and the ``Game`` model, and facade exposure.
"""

from unittest.mock import Mock, patch

import pytest

from edgework.clients.shift_client import (
    SHIFTCHARTS_ROUTE,
    ShiftClient,
    build_shiftcharts_query,
)
from edgework.const import STATS_API_URL
from edgework.edgework import Edgework
from edgework.endpoints import API_PATH, format_endpoint
from edgework.http_client import HttpClient
from edgework.models.game import Game
from edgework.models.shift import Shift

GAME_ID = 2021020001


def _shift_payload():
    """Build a minimal shiftcharts API payload."""
    return {
        "data": [
            {
                "playerId": 8478402,
                "startTime": "00:00",
                "endTime": "00:45",
                "duration": "00:45",
                "period": 1,
            },
            {
                "playerId": 8479351,
                "startTime": "01:00",
                "endTime": "01:30",
                "duration": "00:30",
                "period": 2,
            },
        ]
    }


def _mock_http_client(payload=None):
    """HttpClient whose underlying httpx client is mocked (records URLs)."""
    http_client = HttpClient()
    http_client._client = Mock()
    http_client._client.get.return_value = Mock(json=Mock(return_value=payload or {}))
    return http_client


class TestShiftChartQueryBuilder:
    """Tests for the shared shiftcharts route/query builder."""

    @staticmethod
    def test_documented_game_filter():
        """The documented filter is cayenneExp=gameId={game_id}."""
        assert build_shiftcharts_query(game_id=GAME_ID) == {
            "cayenneExp": f"gameId={GAME_ID}"
        }

    @staticmethod
    def test_raw_cayenne_expression_escape_hatch():
        """A raw Cayenne expression is passed through as the filter."""
        assert build_shiftcharts_query(cayenne_exp="playerId=8478402") == {
            "cayenneExp": "playerId=8478402"
        }

    @staticmethod
    def test_game_id_takes_precedence():
        """An explicit game_id wins over a raw expression."""
        query = build_shiftcharts_query(
            game_id=GAME_ID, cayenne_exp="playerId=8478402"
        )
        assert query == {"cayenneExp": f"gameId={GAME_ID}"}

    @staticmethod
    def test_query_requires_a_filter():
        """Requests without any filter are rejected."""
        with pytest.raises(ValueError, match="requires a filter"):
            build_shiftcharts_query()


class TestShiftClientRoutes:
    """Mocked route tests for ShiftClient (the canonical shiftcharts wrapper)."""

    def setup_method(self):
        """Set up a client with a mocked HTTP layer."""
        self.http_client = Mock(spec=HttpClient)
        self.http_client.get.return_value = Mock(
            json=Mock(return_value=_shift_payload())
        )
        self.client = ShiftClient(self.http_client)

    def test_get_shifts_route_and_params(self):
        """get_shifts requests shiftcharts with the cayenneExp filter in params."""
        shifts = self.client.get_shifts(GAME_ID)

        self.http_client.get.assert_called_once_with(
            SHIFTCHARTS_ROUTE,
            params={"cayenneExp": f"gameId={GAME_ID}"},
            lang="en",
        )
        assert len(shifts) == 2
        assert all(isinstance(shift, Shift) for shift in shifts)
        assert shifts[0].player_id == 8478402
        assert shifts[1].period == 2

    def test_get_shifts_alternate_language(self):
        """The language prefix is controlled by the lang argument."""
        self.client.get_shifts(GAME_ID, lang="fr")

        assert self.http_client.get.call_args.kwargs["lang"] == "fr"

    def test_get_shiftcharts_returns_raw_rows(self):
        """get_shiftcharts returns raw dictionaries for arbitrary filters."""
        rows = self.client.get_shiftcharts(cayenne_exp="playerId=8478402")

        self.http_client.get.assert_called_once_with(
            SHIFTCHARTS_ROUTE,
            params={"cayenneExp": "playerId=8478402"},
            lang="en",
        )
        assert rows == _shift_payload()["data"]

    def test_get_shifts_requires_game_id(self):
        """get_shifts without a game ID is rejected before any request."""
        with pytest.raises(ValueError, match="requires a filter"):
            self.client.get_shiftcharts(lang="en")

        self.http_client.get.assert_not_called()

    @staticmethod
    def test_final_url_matches_stats_registry():
        """End-to-end URL must equal the stats_shiftcharts registry route."""
        http_client = _mock_http_client(_shift_payload())
        ShiftClient(http_client).get_shifts(GAME_ID)

        expected_route = format_endpoint("stats_shiftcharts", lang="en").lstrip("/")
        assert API_PATH["stats_shiftcharts"] == "/{lang}/shiftcharts"

        actual_url = http_client._client.get.call_args.args[0]
        assert actual_url == f"{STATS_API_URL}{expected_route}"
        assert actual_url == f"{STATS_API_URL}en/shiftcharts"
        assert http_client._client.get.call_args.kwargs["params"] == {
            "cayenneExp": f"gameId={GAME_ID}"
        }


class TestGameModelShiftDelegation:
    """The Game model must delegate shift fetching to the canonical client."""

    def _game(self, http_client):
        """Build a Game marked as fetched so lazy boxscore fetch is skipped."""
        game = Game(edgework_client=http_client, obj_id=GAME_ID, game_id=GAME_ID)
        game._fetched = True
        return game

    def test_game_shifts_delegates_to_shift_client(self):
        """game.shifts issues the exact request ShiftClient would make."""
        http_client = _mock_http_client(_shift_payload())
        game = self._game(http_client)

        shifts = game.shifts

        http_client._client.get.assert_called_once()
        args, kwargs = http_client._client.get.call_args
        assert args[0] == f"{STATS_API_URL}en/shiftcharts"
        assert kwargs["params"] == {"cayenneExp": f"gameId={GAME_ID}"}
        assert len(shifts) == 2
        assert all(isinstance(shift, Shift) for shift in shifts)

    def test_game_shifts_request_identical_to_shift_client(self):
        """Model delegation and direct client use produce identical requests."""
        game_http = _mock_http_client(_shift_payload())
        client_http = _mock_http_client(_shift_payload())

        game_shifts = self._game(game_http).shifts
        client_shifts = ShiftClient(client_http).get_shifts(GAME_ID)

        assert len(game_shifts) == len(client_shifts)

        assert game_http._client.get.call_args == client_http._client.get.call_args

    def test_game_shifts_are_cached(self):
        """A second access reuses the cached shifts without a new request."""
        http_client = _mock_http_client(_shift_payload())
        game = self._game(http_client)

        first_shifts = game.shifts
        second_shifts = game.shifts

        assert first_shifts is second_shifts
        assert http_client._client.get.call_count == 1


class TestFacadeShiftAccess:
    """The Edgework facade must expose the canonical ShiftClient."""

    @staticmethod
    def test_facade_exposes_shift_client():
        """edgework.shifts is a ShiftClient sharing the facade HTTP client."""
        with patch("edgework.edgework.HttpClient") as mock_http_client:
            edgework = Edgework()

            assert isinstance(edgework.shifts, ShiftClient)
            assert edgework.shifts._client is mock_http_client.return_value

    @staticmethod
    def test_facade_shift_client_issues_documented_request():
        """Requests through the facade match the canonical shiftcharts route."""
        with patch("edgework.edgework.HttpClient") as mock_http_client:
            http_instance = mock_http_client.return_value
            http_instance.get.return_value = Mock(
                json=Mock(return_value=_shift_payload())
            )
            edgework = Edgework()

            shifts = edgework.shifts.get_shifts(GAME_ID)

            http_instance.get.assert_called_once_with(
                SHIFTCHARTS_ROUTE,
                params={"cayenneExp": f"gameId={GAME_ID}"},
                lang="en",
            )
            assert all(isinstance(shift, Shift) for shift in shifts)
