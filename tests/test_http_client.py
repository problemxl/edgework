"""Tests for HttpClient URL construction (Web vs. Stats API routing)."""

from unittest.mock import Mock

import pytest

from edgework.const import BASE_WEB_URL, STATS_API_URL
from edgework.http_client import HttpClient


@pytest.fixture
def client():
    """HttpClient with a mocked httpx client (no real network)."""
    http_client = HttpClient()
    http_client._client = Mock()
    return http_client


def _last_request_url(http_client) -> str:
    """Return the URL the mocked httpx client was last called with."""
    assert http_client._client.get.call_count == 1
    return http_client._client.get.call_args.args[0]


class TestWebApiUrls:
    """Web API requests target api-web.nhle.com under /v1."""

    @staticmethod
    def test_web_url_gets_version_prefix(client):
        """Verify web url gets version prefix."""
        client.get("season", web=True)
        assert _last_request_url(client) == f"{BASE_WEB_URL}/v1/season"

    @staticmethod
    def test_web_url_strips_leading_slash(client):
        """Verify web url strips leading slash."""
        client.get("/standings/now", web=True)
        assert _last_request_url(client) == f"{BASE_WEB_URL}/v1/standings/now"

    @staticmethod
    def test_web_url_ignores_lang(client):
        """Verify web url ignores lang."""
        client.get("franchise", web=True, lang="fr")
        assert _last_request_url(client) == f"{BASE_WEB_URL}/v1/franchise"

    @staticmethod
    def test_web_openapi_spec_has_no_double_version_prefix(client):
        """The OpenAPI spec lives at /model/v1/openapi.json, not /v1/model/..."""
        client.get("model/v1/openapi.json", web=True)
        assert _last_request_url(client) == f"{BASE_WEB_URL}/model/v1/openapi.json"

    @staticmethod
    def test_web_params_stay_in_query_string(client):
        """Verify web params stay in query string."""
        client.get("meta", web=True, params={"players": "8478402"})
        assert _last_request_url(client) == f"{BASE_WEB_URL}/v1/meta"
        assert client._client.get.call_args.kwargs["params"] == {"players": "8478402"}


class TestStatsApiUrls:
    """Stats API requests target api.nhle.com/stats/rest with a language prefix."""

    @staticmethod
    def test_default_english_stats_url(client):
        """Verify default english stats url."""
        client.get("franchise")
        assert _last_request_url(client) == f"{STATS_API_URL}en/franchise"

    @staticmethod
    def test_explicit_english_stats_url(client):
        """Verify explicit english stats url."""
        client.get("franchise", lang="en")
        assert _last_request_url(client) == f"{STATS_API_URL}en/franchise"

    @staticmethod
    def test_alternate_language_stats_url(client):
        """Verify alternate language stats url."""
        client.get("franchise", lang="fr")
        assert _last_request_url(client) == f"{STATS_API_URL}fr/franchise"

    @staticmethod
    def test_root_stats_route_has_no_language_prefix(client):
        """/ping is documented without a language segment."""
        client.get("ping", lang=None)
        assert _last_request_url(client) == f"{STATS_API_URL}ping"

    @staticmethod
    def test_stats_params_stay_in_query_string(client):
        """Verify stats params stay in query string."""
        client.get("skater/summary", params={"limit": 10, "cayenneExp": "seasonId=20232024"})
        assert _last_request_url(client) == f"{STATS_API_URL}en/skater/summary"
        assert client._client.get.call_args.kwargs["params"] == {
            "limit": 10,
            "cayenneExp": "seasonId=20232024",
        }


class TestLegacyPrefixStripping:
    """Legacy ``rest/`` / ``stats/rest/`` / ``en/`` prefixes are stripped."""

    @staticmethod
    def test_strips_en_prefix(client):
        """Verify strips en prefix."""
        client.get("en/glossary")
        assert _last_request_url(client) == f"{STATS_API_URL}en/glossary"

    @staticmethod
    def test_strips_rest_prefix(client):
        """Verify strips rest prefix."""
        client.get("rest/en/glossary")
        assert _last_request_url(client) == f"{STATS_API_URL}en/glossary"

    @staticmethod
    def test_strips_stats_rest_prefix(client):
        """Verify strips stats rest prefix."""
        client.get("stats/rest/en/glossary")
        assert _last_request_url(client) == f"{STATS_API_URL}en/glossary"

    @staticmethod
    def test_legacy_prefix_swapped_for_alternate_language(client):
        """Verify legacy prefix swapped for alternate language."""
        client.get("en/team", lang="fr")
        assert _last_request_url(client) == f"{STATS_API_URL}fr/team"

    @staticmethod
    def test_legacy_embedded_query_string_is_preserved(client):
        """Existing callers embed query strings in the route (e.g. models)."""
        path = "skater/summary?isAggregate=False&isGame=True&limit=-1&start=0"
        client.get(path)
        assert (
            _last_request_url(client) == f"{STATS_API_URL}en/{path}"
        )

    @staticmethod
    def test_legacy_shiftcharts_route(client):
        """Verify legacy shiftcharts route."""
        client.get("shiftcharts?cayenneExp=gameId=2021020001")
        assert (
            _last_request_url(client)
            == f"{STATS_API_URL}en/shiftcharts?cayenneExp=gameId=2021020001"
        )


class TestBackwardCompatibility:
    """Existing call patterns keep constructing the same requests."""

    @staticmethod
    def test_web_call_unchanged(client):
        """Verify web call unchanged."""
        client.get("player/8478402/landing", web=True)
        assert (
            _last_request_url(client)
            == f"{BASE_WEB_URL}/v1/player/8478402/landing"
        )

    @staticmethod
    def test_stats_call_with_path_kwarg_unchanged(client):
        """Verify stats call with path kwarg unchanged."""
        client.get(
            endpoint="stats",
            path="goalie/summary?isAggregate=False&isGame=True",
            params=None,
            web=False,
        )
        assert (
            _last_request_url(client)
            == f"{STATS_API_URL}en/goalie/summary?isAggregate=False&isGame=True"
        )

    @staticmethod
    def test_get_raw_uses_url_verbatim(client):
        """Verify get raw uses url verbatim."""
        client.get_raw("https://example.com/data", params={"q": "1"})
        assert _last_request_url(client) == "https://example.com/data"
        assert client._client.get.call_args.kwargs["params"] == {"q": "1"}

    @staticmethod
    def test_get_raw_forwards_headers(client):
        """Sprites-host calls need Referer: https://www.nhl.com/ (403 without)."""
        client.get_raw(
            "https://wsr.nhle.com/sprites/20252026/2025020740/ev95.json",
            headers={"Referer": "https://www.nhl.com/"},
        )
        assert client._client.get.call_args.kwargs["headers"] == {
            "Referer": "https://www.nhl.com/"
        }

    @staticmethod
    def test_get_raw_headers_default_to_none(client):
        """Omitting headers leaves the request headers untouched (httpx merges
        per-request headers over the client defaults when provided)."""
        client.get_raw("https://example.com/data")
        assert client._client.get.call_args.kwargs["headers"] is None

    @staticmethod
    def test_query_params_not_embedded_in_route_for_new_callers(client):
        """Verify query params not embedded in route for new callers."""
        client.get("players", params={"start": 0, "limit": 100})
        url = _last_request_url(client)
        assert url == f"{STATS_API_URL}en/players"
        assert "?" not in url
