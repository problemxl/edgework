"""Task 5: duplicate client/model access is intentional delegation.

Every duplicate access path must construct a request identical to its
client counterpart (Game model <-> GameClient/ShiftClient, Config <->
StatsClient — the latter lives in ``tests/test_config.py``), and season
normalization must flow through the shared
``edgework.utilities.validate_season_format`` helper everywhere.
"""

from unittest.mock import Mock

import httpx
import pytest

from edgework.clients.draft_client import DraftClient
from edgework.clients.game_client import GameClient
from edgework.clients.player_client import PlayerClient
from edgework.clients.playoff_client import PlayoffClient
from edgework.clients.shift_client import ShiftClient
from edgework.clients.standings_client import StandingClient
from edgework.const import BASE_WEB_URL, STATS_API_URL
from edgework.endpoints import format_endpoint
from edgework.http_client import HttpClient
from edgework.models.game import Game

GAME_ID = 2023020001

BOXSCORE_PAYLOAD = {
    "id": GAME_ID,
    "startTimeUTC": "2023-10-10T23:30:00Z",
    "gameState": "LIVE",
    "awayTeam": {"id": 10, "abbrev": "TOR", "score": 3},
    "homeTeam": {"id": 6, "abbrev": "MTL", "score": 2},
    "season": 20232024,
    "venue": {"default": "Bell Centre"},
}

SHIFT_PAYLOAD = {
    "data": [
        {
            "playerId": 8478402,
            "startTime": "00:00",
            "endTime": "00:45",
            "duration": "45",
            "period": 1,
        }
    ]
}


def _mock_http_client(payload):
    """HttpClient whose underlying httpx client is mocked (records URLs)."""
    http_client = HttpClient()
    http_client._client = Mock()
    http_client._client.get.return_value = Mock(json=Mock(return_value=payload))
    return http_client


def _captured_url(http_client):
    """Return the effective final URL (recorded route + encoded params)."""
    args, kwargs = http_client._client.get.call_args
    url = args[0]
    params = kwargs.get("params")
    if params:
        url = f"{url}?{httpx.QueryParams(params)}"
    return url


class TestGameModelDelegation:
    """Game model access paths construct identical requests to clients."""

    @staticmethod
    def test_game_shifts_route_matches_shift_client():
        """Verify test game shifts route matches shift client."""
        model_client = _mock_http_client(SHIFT_PAYLOAD)
        client_client = _mock_http_client(SHIFT_PAYLOAD)

        # from_api marks the game fetched so lazy attribute access does not
        # trigger the (otherwise identical) boxscore refresh first.
        game = Game.from_api(BOXSCORE_PAYLOAD, model_client)
        game._get_shifts()
        ShiftClient(client_client).get_shifts(GAME_ID)

        assert _captured_url(model_client) == _captured_url(client_client)
        expected = (
            STATS_API_URL
            + format_endpoint("stats_shiftcharts", lang="en").lstrip("/")
            + f"?cayenneExp=gameId%3D{GAME_ID}"
        )
        assert _captured_url(model_client) == expected

    @staticmethod
    def test_game_play_by_play_route_matches_game_client():
        """Verify test game play by play route matches game client."""
        model_client = _mock_http_client({})
        client_client = _mock_http_client({})

        game = Game.from_api(BOXSCORE_PAYLOAD, model_client)
        game._get_play_by_play()
        GameClient(client_client).get_play_by_play(GAME_ID)

        assert _captured_url(model_client) == _captured_url(client_client)
        assert _captured_url(model_client) == BASE_WEB_URL + format_endpoint(
            "play_by_play", game_id=GAME_ID
        )

    @staticmethod
    def test_game_fetch_data_route_matches_game_client_boxscore():
        """Verify test game fetch data route matches game client boxscore."""
        model_client = _mock_http_client(BOXSCORE_PAYLOAD)
        client_client = _mock_http_client(BOXSCORE_PAYLOAD)

        game = Game(model_client, obj_id=GAME_ID)
        game.fetch_data()
        GameClient(client_client).get_game_boxscore(GAME_ID)

        assert _captured_url(model_client) == _captured_url(client_client)
        assert _captured_url(model_client) == BASE_WEB_URL + format_endpoint(
            "game_boxscore", game_id=GAME_ID
        )

    @staticmethod
    def test_game_get_game_classmethod_route_matches_game_client():
        """Verify test game get game classmethod route matches game client."""
        model_client = _mock_http_client(BOXSCORE_PAYLOAD)
        client_client = _mock_http_client(BOXSCORE_PAYLOAD)

        Game.get_game(GAME_ID, model_client)
        GameClient(client_client).get_game_boxscore(GAME_ID)

        assert _captured_url(model_client) == _captured_url(client_client)

    @staticmethod
    def test_fetch_data_and_get_game_are_equivalent():
        """Verify test fetch data and get game are equivalent."""
        model_client = _mock_http_client(BOXSCORE_PAYLOAD)
        game = Game(model_client, obj_id=GAME_ID)
        game.fetch_data()

        other = Game.get_game(GAME_ID, _mock_http_client(BOXSCORE_PAYLOAD))

        assert game._data == other._data


class TestSeasonNormalizationMigration:
    """Migrated clients build identical routes via the shared helper."""

    @staticmethod
    def test_player_game_log_route_unchanged():
        """Verify test player game log route unchanged."""
        http_client = _mock_http_client({})
        PlayerClient(http_client).get_player_game_logs(8478402, "2023-2024")

        assert _captured_url(http_client) == BASE_WEB_URL + format_endpoint(
            "player_game_logs",
            player_id=8478402,
            season=20232024,
            **{"game-type": 2},
        )

    @staticmethod
    def test_playoff_carousel_route_unchanged():
        """Verify test playoff carousel route unchanged."""
        http_client = _mock_http_client({})
        PlayoffClient(http_client).get_playoff_series_carousel("2023-2024")

        assert _captured_url(http_client) == BASE_WEB_URL + format_endpoint(
            "playoff_series_carousel", season=20232024
        )

    @staticmethod
    def test_playoff_carousel_now_has_no_season():
        """Verify test playoff carousel now has no season."""
        http_client = _mock_http_client({})
        PlayoffClient(http_client).get_playoff_series_carousel()

        assert _captured_url(http_client) == (
            BASE_WEB_URL + "/v1/playoff-series/carousel/"
        )

    @staticmethod
    def test_playoff_series_schedule_route_unchanged():
        """Verify test playoff series schedule route unchanged."""
        http_client = _mock_http_client({})
        PlayoffClient(http_client).get_playoff_series_schedule("2023-2024", "A")

        assert _captured_url(http_client) == BASE_WEB_URL + format_endpoint(
            "playoff_series_schedule", season=20232024, series_letter="A"
        )

    @staticmethod
    def test_playoff_series_by_round_uses_season_end_year():
        """Verify test playoff series by round uses season end year."""
        http_client = _mock_http_client({"rounds": []})
        series = PlayoffClient(http_client).get_playoff_series_by_round(
            "2019-2020", 1
        )

        assert _captured_url(http_client) == BASE_WEB_URL + format_endpoint(
            "playoff_bracket", year=2020
        )
        assert series == []

    @staticmethod
    def test_draft_picks_route_matches_documentation():
        """Verify test draft picks route matches documentation."""
        http_client = _mock_http_client(
            {"draftYear": 2024, "rounds": [], "picks": []}
        )
        DraftClient(http_client).get_draft_picks(season="2023-2024")

        # Documented route: /v1/draft/picks/{season}/{round} with the draft
        # year in YYYY format (the season's start year), not the YYYYYYYY id.
        assert _captured_url(http_client) == BASE_WEB_URL + format_endpoint(
            "draft_picks", season=2023, round="all"
        )

    @staticmethod
    def test_draft_rankings_route_matches_documentation():
        """Verify test draft rankings route matches documentation."""
        http_client = _mock_http_client({"rankings": []})
        DraftClient(http_client).get_draft_rankings(season="2023-2024")

        # Documented route: /v1/draft/rankings/{season}/{prospect_category}
        # with the draft year in YYYY format, not the YYYYYYYY id.
        assert _captured_url(http_client) == BASE_WEB_URL + format_endpoint(
            "draft_rankings", season=2023, prospect_category="all"
        )

    @staticmethod
    def test_standings_season_query_unchanged():
        """Verify test standings season query unchanged."""
        http_client = _mock_http_client({"data": []})
        StandingClient(http_client).get_standings_for_season("2023-2024")

        url = _captured_url(http_client)
        assert url.startswith(
            BASE_WEB_URL + format_endpoint("standings_season") + "?"
        )
        query = httpx.QueryParams(url.split("?", 1)[1])
        assert query["seasonId"] == "20232024"

    @staticmethod
    def test_migrated_clients_use_shared_helper():
        """The helper is imported, not re-implemented, in each client."""
        import edgework.clients.draft_client as draft_client
        import edgework.clients.player_client as player_client
        import edgework.clients.playoff_client as playoff_client
        import edgework.clients.standings_client as standings_client
        from edgework.utilities import validate_season_format

        assert draft_client.validate_season_format is validate_season_format
        assert player_client.validate_season_format is validate_season_format
        assert playoff_client.validate_season_format is validate_season_format
        assert (
            standings_client.validate_season_format is validate_season_format
        )

    @pytest.mark.parametrize(
        "call",
        [
            lambda c: PlayerClient(c).get_player_game_logs(8478402, "2023-24"),
            lambda c: PlayerClient(c).get_player_game_logs(8478402, 20232024),
            lambda c: PlayoffClient(c).get_playoff_series_carousel("2023-2025"),
            lambda c: PlayoffClient(c).get_playoff_series_carousel("invalid"),
            lambda c: PlayoffClient(c).get_playoff_series_schedule(
                "invalid", "A"
            ),
            lambda c: PlayoffClient(c).get_playoff_series_by_round(
                "2023-24", 1
            ),
            lambda c: DraftClient(c).get_draft_picks(season=20232024),
            lambda c: DraftClient(c).get_draft_picks(season="2023-2025"),
            lambda c: DraftClient(c).get_draft_rankings(season="2023-2025"),
            lambda c: StandingClient(c).get_standings_for_season("2023-24"),
        ],
    )
    @staticmethod
    def test_malformed_seasons_rejected_by_shared_helper(call):
        """Rejection happens in the shared helper before any request."""
        http_client = _mock_http_client({})

        with pytest.raises(ValueError):
            call(http_client)

        http_client._client.get.assert_not_called()
