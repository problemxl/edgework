"""Mocked tests for the expanded StatsClient (Task 4).

Covers report query assembly (params-encoded, registry-accurate URLs), the
new simple resource endpoints, and the Web API leaderboards with
``categories``/``limit`` support.
"""

from datetime import datetime
from unittest.mock import Mock, patch

import httpx
import pytest

from edgework.clients.stats_client import StatsClient
from edgework.const import BASE_WEB_URL, STATS_API_URL
from edgework.endpoints import format_endpoint
from edgework.http_client import HttpClient
from edgework.models.stats import GoalieStats, SkaterStats, TeamStats

SEASON = 20232024


def _skater_payload():
    return {
        "data": [
            {
                "playerId": 8478402,
                "firstName": "Connor",
                "lastName": "McDavid",
                "skaterFullName": "Connor McDavid",
                "points": 100,
                "goals": 40,
                "assists": 60,
                "gamesPlayed": 82,
            }
        ]
    }


def _mock_http_client(payload=None):
    """HttpClient whose underlying httpx client is mocked (records URLs)."""
    http_client = HttpClient()
    http_client._client = Mock()
    http_client._client.get.return_value = Mock(
        json=Mock(return_value=payload if payload is not None else {})
    )
    return http_client


def _captured_url(http_client):
    """Return the effective final URL (recorded route + encoded params)."""
    args, kwargs = http_client._client.get.call_args
    url = args[0]
    params = kwargs.get("params")
    if params:
        url = f"{url}?{httpx.QueryParams(params)}"
    return url


def _query_of(url):
    """Decode the query string of a URL into a dict (lists via get_list)."""
    if "?" not in url:
        return httpx.QueryParams("")
    return httpx.QueryParams(url.split("?", 1)[1])


# ---------------------------------------------------------------------------
# Report endpoints
# ---------------------------------------------------------------------------


class TestStatsReportQueries:
    """Report methods build params-encoded requests on registry routes."""

    @pytest.fixture
    def http_client(self):
        return _mock_http_client(_skater_payload())

    @pytest.mark.parametrize(
        "method_name,registry_key,default_sort",
        [
            ("get_skaters_stats", "stats_skater_report", "points"),
            ("get_goalies_stats", "stats_goalie_report", "wins"),
            ("get_team_stats", "stats_team_report", "wins"),
        ],
    )
    def test_report_default_query(
        self, http_client, method_name, registry_key, default_sort
    ):
        """Default report request hits /{lang}/{family}/{report} in params."""
        getattr(StatsClient(http_client), method_name)(season=SEASON)

        url = _captured_url(http_client)
        expected_base = (
            STATS_API_URL
            + format_endpoint(
                registry_key, lang="en", report="summary"
            ).lstrip("/")
        )
        expected_query = httpx.QueryParams(
            {
                "isAggregate": "false",
                "isGame": "true",
                "limit": "-1",
                "start": "0",
                "sort": default_sort,
                "cayenneExp": f"seasonId={SEASON}",
            }
        )
        assert url == f"{expected_base}?{expected_query}"

    def test_report_language_prefix(self):
        """A non-default language is used for the Stats API route."""
        http_client = _mock_http_client(_skater_payload())
        StatsClient(http_client).get_skaters_stats(season=SEASON, lang="fr")

        url = _captured_url(http_client)
        assert url.startswith(f"{STATS_API_URL}fr/skater/summary?")

    def test_goalie_report_language_registry_url(self):
        http_client = _mock_http_client(_skater_payload())
        StatsClient(http_client).get_goalies_stats(season=SEASON, lang="fr")

        expected_base = (
            STATS_API_URL
            + format_endpoint(
                "stats_goalie_report", lang="fr", report="summary"
            ).lstrip("/")
        )
        assert _captured_url(http_client).startswith(expected_base + "?")

    @pytest.mark.parametrize("game_type", [2, 3])
    def test_game_type_appended_to_cayenne(self, game_type):
        http_client = _mock_http_client(_skater_payload())
        StatsClient(http_client).get_skaters_stats(
            season=SEASON, game_type=game_type
        )

        query = _query_of(_captured_url(http_client))
        assert query["cayenneExp"] == (
            f"seasonId={SEASON} and gameTypeId={game_type}"
        )

    def test_invalid_game_type_rejected(self):
        http_client = _mock_http_client(_skater_payload())
        with pytest.raises(ValueError, match="Game type"):
            StatsClient(http_client).get_skaters_stats(
                season=SEASON, game_type=7
            )
        http_client._client.get.assert_not_called()

    def test_cayenne_exp_escape_hatch_overrides_season(self):
        """A raw cayenne_exp replaces the built season expression."""
        http_client = _mock_http_client(_skater_payload())
        StatsClient(http_client).get_skaters_stats(
            season=SEASON, cayenne_exp="playerId=8478402"
        )

        query = _query_of(_captured_url(http_client))
        assert query["cayenneExp"] == "playerId=8478402"

    def test_default_season_computed_when_none(self):
        """season=None computes the current season (October 2023 -> 20232024)."""
        http_client = _mock_http_client(_skater_payload())
        with patch("edgework.models.stats.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 10, 1)
            StatsClient(http_client).get_skaters_stats()

        query = _query_of(_captured_url(http_client))
        assert query["cayenneExp"] == "seasonId=20232024"

    @pytest.mark.parametrize(
        "method_name",
        ["get_skaters_stats", "get_goalies_stats", "get_team_stats"],
    )
    def test_invalid_report_rejected_without_request(
        self, http_client, method_name
    ):
        client = StatsClient(http_client)
        if method_name == "get_skaters_stats":
            call = lambda: client.get_skaters_stats(report="not_a_report")
        elif method_name == "get_goalies_stats":
            call = lambda: client.get_goalies_stats(
                season=SEASON, report="not_a_report"
            )
        else:
            call = lambda: client.get_team_stats(
                season=SEASON, report="not_a_report"
            )

        with pytest.raises(ValueError, match="Unsupported"):
            call()
        http_client._client.get.assert_not_called()

    def test_alias_report_passes_through_in_route(self):
        """Legacy alias names keep their historical wire format."""
        http_client = _mock_http_client({"data": []})
        StatsClient(http_client).get_skaters_stats(
            "powerPlay", season=SEASON
        )

        url = _captured_url(http_client)
        assert url.startswith(f"{STATS_API_URL}en/skater/powerPlay?")

    def test_dir_and_fact_cayenne_exp_params(self):
        http_client = _mock_http_client(_skater_payload())
        StatsClient(http_client).get_skaters_stats(
            season=SEASON,
            dir="ASC",
            fact_cayenne_exp="points>=50",
        )

        query = _query_of(_captured_url(http_client))
        assert query["dir"] == "ASC"
        assert query["factCayenneExp"] == "points>=50"

    def test_include_and_exclude_sent_as_params(self):
        http_client = _mock_http_client(_skater_payload())
        StatsClient(http_client).get_skaters_stats(
            season=SEASON,
            include=["playoffs", "regularSeason"],
            exclude="shootouts",
        )

        query = _query_of(_captured_url(http_client))
        assert query.get_list("include") == ["playoffs", "regularSeason"]
        assert query["exclude"] == "shootouts"

    def test_extra_params_escape_hatch(self):
        http_client = _mock_http_client(_skater_payload())
        StatsClient(http_client).get_skaters_stats(
            season=SEASON, extra_params={"customKey": "customValue"}
        )

        query = _query_of(_captured_url(http_client))
        assert query["customKey"] == "customValue"

    @pytest.mark.parametrize(
        "kwargs,match",
        [
            ({"limit": 0}, "Limit must be"),
            ({"limit": -5}, "Limit must be"),
            ({"start": -1}, "Start must be"),
        ],
    )
    def test_limit_start_validation(self, kwargs, match):
        http_client = _mock_http_client(_skater_payload())
        with pytest.raises(ValueError, match=match):
            StatsClient(http_client).get_skaters_stats(
                season=SEASON, **kwargs
            )
        http_client._client.get.assert_not_called()

    def test_legacy_positional_call_order_preserved(self):
        """The original positional signature keeps working."""
        http_client = _mock_http_client(_skater_payload())
        StatsClient(http_client).get_skaters_stats(
            "bios", False, True, 10, 5, "goals", 20222023
        )

        url = _captured_url(http_client)
        assert url.startswith(f"{STATS_API_URL}en/skater/bios?")
        query = _query_of(url)
        assert query["isAggregate"] == "false"
        assert query["isGame"] == "true"
        assert query["limit"] == "10"
        assert query["start"] == "5"
        assert query["sort"] == "goals"
        assert query["cayenneExp"] == "seasonId=20222023"


class TestStatsReportModels:
    """Report rows become stats models with the client bound."""

    def test_rows_become_models_with_client_bound(self):
        http_client = _mock_http_client(_skater_payload())
        stats = StatsClient(http_client).get_skaters_stats(season=SEASON)

        assert len(stats) == 1
        assert isinstance(stats[0], SkaterStats)
        # Regression: the model's client is the HTTP client (previously the
        # first data key was silently bound to edgework_client).
        assert stats[0]._client is http_client
        assert stats[0]._fetched is True

    @pytest.mark.parametrize(
        "payload,model_cls,method",
        [
            (
                {
                    "data": [
                        {
                            "playerId": 8478402,
                            "goalieFullName": "Connor Hellebuyck",
                            "wins": 30,
                        }
                    ]
                },
                GoalieStats,
                "get_goalies_stats",
            ),
            (
                {
                    "data": [
                        {
                            "teamId": 10,
                            "teamFullName": "Toronto Maple Leafs",
                            "wins": 45,
                        }
                    ]
                },
                TeamStats,
                "get_team_stats",
            ),
        ],
    )
    def test_goalie_and_team_rows(self, payload, model_cls, method):
        http_client = _mock_http_client(payload)
        stats = getattr(StatsClient(http_client), method)(season=SEASON)

        assert isinstance(stats[0], model_cls)
        assert stats[0]._client is http_client

    def test_attribute_access_does_not_refetch(self):
        """Loaded rows serve attributes from _data without a second request."""
        http_client = _mock_http_client(_skater_payload())
        stats = StatsClient(http_client).get_skaters_stats(season=SEASON)

        assert stats[0].player_id == 8478402
        assert stats[0].skater_full_name == "Connor McDavid"
        assert stats[0].points == 100
        http_client._client.get.assert_called_once()


# ---------------------------------------------------------------------------
# Simple resource endpoints
# ---------------------------------------------------------------------------


class TestStatsResources:
    """One route/param-encoding assertion per new resource endpoint."""

    @pytest.fixture
    def http_client(self):
        return _mock_http_client({"data": []})

    @pytest.mark.parametrize(
        "call,registry_key,format_kwargs",
        [
            (lambda c: c.get_players(), "stats_players", {}),
            (lambda c: c.get_skaters(), "stats_skater", {}),
            (
                lambda c: c.get_skater_leaders("points"),
                "stats_skater_leaders",
                {"attribute": "points"},
            ),
            (
                lambda c: c.get_skater_milestones(),
                "stats_skater_milestones",
                {},
            ),
            (
                lambda c: c.get_goalie_leaders("gaa"),
                "stats_goalie_leaders",
                {"attribute": "gaa"},
            ),
            (
                lambda c: c.get_goalie_milestones(),
                "stats_goalie_milestones",
                {},
            ),
            (lambda c: c.get_draft(), "stats_draft", {}),
            (lambda c: c.get_franchises(), "stats_franchise", {}),
            (
                lambda c: c.get_component_seasons(),
                "stats_component_season",
                {},
            ),
            (lambda c: c.get_seasons(), "stats_season", {}),
            (lambda c: c.get_games(), "stats_game", {}),
            (lambda c: c.get_game_meta(), "stats_game_meta", {}),
            (lambda c: c.get_config(), "stats_config", {}),
            (lambda c: c.get_countries(), "stats_country", {}),
            (
                lambda c: c.get_content_module("template"),
                "stats_content_module",
                {"template_key": "template"},
            ),
        ],
    )
    def test_resource_route_matches_registry(
        self, http_client, call, registry_key, format_kwargs
    ):
        call(StatsClient(http_client))

        expected = STATS_API_URL + format_endpoint(
            registry_key, lang="en", **format_kwargs
        ).lstrip("/")
        assert _captured_url(http_client) == expected

    def test_resource_language_prefix(self):
        """Non-default languages flow into the registry template."""
        http_client = _mock_http_client({"data": []})
        StatsClient(http_client).get_franchises(lang="fr")

        expected = STATS_API_URL + format_endpoint(
            "stats_franchise", lang="fr"
        ).lstrip("/")
        assert _captured_url(http_client) == expected

    def test_players_pagination_params(self):
        http_client = _mock_http_client({"data": [], "total": 0})
        StatsClient(http_client).get_players(limit=10, start=5)

        url = _captured_url(http_client)
        assert url.startswith(f"{STATS_API_URL}en/players?")
        query = _query_of(url)
        assert query["limit"] == "10"
        assert query["start"] == "5"

    def test_players_without_pagination_has_no_query(self):
        http_client = _mock_http_client({"data": [], "total": 0})
        StatsClient(http_client).get_players()

        assert "?" not in _captured_url(http_client)

    def test_content_module_template_key_substituted(self):
        http_client = _mock_http_client({})
        StatsClient(http_client).get_content_module("my-template-key")

        url = _captured_url(http_client)
        assert url == f"{STATS_API_URL}en/content/module/my-template-key"

    def test_ping_hits_root_route_without_language(self):
        """``/ping`` is a root Stats route (no language prefix)."""
        http_client = _mock_http_client({})
        StatsClient(http_client).ping()

        expected = STATS_API_URL + format_endpoint("stats_ping").lstrip("/")
        assert _captured_url(http_client) == expected

    def test_resources_return_raw_json(self):
        payload = [{"franchiseId": 1}, {"franchiseId": 2}]
        http_client = _mock_http_client(payload)

        result = StatsClient(http_client).get_franchises()

        assert result == payload


# ---------------------------------------------------------------------------
# Web API leaderboards
# ---------------------------------------------------------------------------


class TestLeaderboards:
    """Leaderboard methods expose categories/limit on current + historical."""

    @pytest.fixture
    def http_client(self):
        return _mock_http_client({"points": []})

    def test_current_skater_leaders_default(self, http_client):
        """No categories/limit -> the documented route with no query."""
        StatsClient(http_client).get_skater_stats_leaders()

        expected = BASE_WEB_URL + format_endpoint("skater_stats_now")
        assert _captured_url(http_client) == expected
        assert "?" not in _captured_url(http_client)

    def test_current_goalie_leaders_default(self):
        http_client = _mock_http_client({"wins": []})
        StatsClient(http_client).get_goalie_stats_leaders()

        expected = BASE_WEB_URL + format_endpoint("goalie_stats_now")
        assert _captured_url(http_client) == expected

    def test_single_category(self, http_client):
        StatsClient(http_client).get_skater_stats_leaders(
            categories="goals", limit=5
        )

        query = _query_of(_captured_url(http_client))
        assert query["categories"] == "goals"
        assert query["limit"] == "5"

    def test_multi_category_joined_with_commas(self, http_client):
        StatsClient(http_client).get_skater_stats_leaders(
            categories=["goals", "assists", "points"]
        )

        query = _query_of(_captured_url(http_client))
        assert query["categories"] == "goals,assists,points"
        assert "limit" not in query

    def test_limit_boundary_of_one_accepted(self, http_client):
        StatsClient(http_client).get_skater_stats_leaders(limit=1)

        query = _query_of(_captured_url(http_client))
        assert query["limit"] == "1"

    @pytest.mark.parametrize("limit", [0, -5, "10", True])
    def test_invalid_limit_rejected(self, http_client, limit):
        with pytest.raises(ValueError, match="limit must be"):
            StatsClient(http_client).get_skater_stats_leaders(limit=limit)
        http_client._client.get.assert_not_called()

    def test_invalid_categories_type_rejected(self, http_client):
        with pytest.raises(ValueError, match="categories must be"):
            StatsClient(http_client).get_skater_stats_leaders(
                categories={"goals": True}
            )
        http_client._client.get.assert_not_called()

    def test_deprecated_positional_game_type_warns_and_ignored(
        self, http_client
    ):
        """Legacy positional call (old signature was game_type) still works."""
        with pytest.warns(DeprecationWarning, match="game_type"):
            StatsClient(http_client).get_skater_stats_leaders(3)

        expected = BASE_WEB_URL + format_endpoint("skater_stats_now")
        assert _captured_url(http_client) == expected

    def test_empty_category_list_omits_param(self, http_client):
        StatsClient(http_client).get_skater_stats_leaders(categories=[])

        assert "?" not in _captured_url(http_client)

    def test_deprecated_game_type_on_current_warns_and_ignored(
        self, http_client
    ):
        """game_type is unused by /current: warns, request unchanged."""
        with pytest.warns(DeprecationWarning, match="game_type"):
            StatsClient(http_client).get_skater_stats_leaders(game_type=3)

        expected = BASE_WEB_URL + format_endpoint("skater_stats_now")
        assert _captured_url(http_client) == expected

    def test_skater_leaders_by_season_with_categories_and_limit(
        self, http_client
    ):
        StatsClient(http_client).get_skater_stats_leaders_by_season(
            "2023-2024", 2, categories="assists", limit=3
        )

        url = _captured_url(http_client)
        assert url.startswith(f"{BASE_WEB_URL}/v1/skater-stats-leaders/20232024/2?")
        query = _query_of(url)
        assert query["categories"] == "assists"
        assert query["limit"] == "3"

    def test_skater_leaders_by_season_registry_url(self, http_client):
        StatsClient(http_client).get_skater_stats_leaders_by_season(
            "2022-2023", 3
        )

        expected = BASE_WEB_URL + format_endpoint(
            "skater_stats_season_game_type",
            season="20222023",
            **{"game-type": 3},
        )
        assert _captured_url(http_client) == expected

    def test_goalie_leaders_by_season_with_categories(self):
        http_client = _mock_http_client({"wins": []})
        StatsClient(http_client).get_goalie_stats_leaders_by_season(
            "2023-2024", categories=["wins", "gaa"]
        )

        url = _captured_url(http_client)
        assert url.startswith(
            f"{BASE_WEB_URL}/v1/goalie-stats-leaders/20232024/2?"
        )
        assert _query_of(url)["categories"] == "wins,gaa"

    def test_leaders_by_season_invalid_season_rejected(self, http_client):
        with pytest.raises(ValueError):
            StatsClient(http_client).get_skater_stats_leaders_by_season(
                "invalid"
            )
        http_client._client.get.assert_not_called()
