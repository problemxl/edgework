"""Tests for the Config model (Task 5).

``Config.fetch_data`` lazily fetches the documented Stats API
``/{lang}/config`` route (registry key ``stats_config``) by delegating to
``StatsClient.get_config``; the local ``API_PATH`` registry is never stored
as server config.
"""

from unittest.mock import Mock

import httpx
import pytest

from edgework.clients.stats_client import StatsClient
from edgework.const import STATS_API_URL
from edgework.endpoints import format_endpoint
from edgework.http_client import HttpClient
from edgework.models.config import Config

CONFIG_PAYLOAD = {
    "title": "NHL Stats API",
    "api_tm_path": "https://api.nhle.com/stats/rest",
    "copyright": "NHL and the NHL Shield are registered trademarks",
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


class TestConfigLazyFetch:
    """Config follows the BaseNHLModel lazy-load conventions."""

    def test_attribute_access_triggers_single_lazy_fetch(self):
        http_client = _mock_http_client(CONFIG_PAYLOAD)
        config = Config(http_client)

        assert config.title == "NHL Stats API"
        assert config.api_tm_path == "https://api.nhle.com/stats/rest"
        # Exactly one request, on first attribute access only.
        http_client._client.get.assert_called_once()

    def test_fetch_hits_documented_stats_config_route(self):
        http_client = _mock_http_client(CONFIG_PAYLOAD)
        Config(http_client).fetch_data()

        expected = STATS_API_URL + format_endpoint(
            "stats_config", lang="en"
        ).lstrip("/")
        assert _captured_url(http_client) == expected

    def test_language_flows_through_to_route(self):
        http_client = _mock_http_client(CONFIG_PAYLOAD)
        Config(http_client, lang="fr").fetch_data()

        expected = STATS_API_URL + format_endpoint(
            "stats_config", lang="fr"
        ).lstrip("/")
        assert _captured_url(http_client) == expected

    def test_fetch_data_populates_data_and_marks_fetched(self):
        http_client = _mock_http_client(CONFIG_PAYLOAD)
        config = Config(http_client)

        config.fetch_data()

        assert config._fetched is True
        for key, value in CONFIG_PAYLOAD.items():
            assert config._data[key] == value

    def test_explicit_refetch_does_not_double_request_when_fetched(self):
        http_client = _mock_http_client(CONFIG_PAYLOAD)
        config = Config(http_client)

        config.fetch_data()
        assert config.title == "NHL Stats API"

        # Lazy path (attribute access) must not refetch after fetch_data.
        http_client._client.get.assert_called_once()

    def test_server_values_win_over_constructor_kwargs(self):
        http_client = _mock_http_client({"title": "from server"})
        config = Config(http_client, title="from constructor")

        assert config.title == "from server"

    def test_non_dict_payload_rejected(self):
        http_client = _mock_http_client(["unexpected", "list"])
        config = Config(http_client)

        with pytest.raises(ValueError, match="expected a JSON object"):
            config.fetch_data()


class TestConfigNotLocalRegistry:
    """The local API_PATH registry must not be stored as server config."""

    def test_registry_keys_not_stored(self):
        http_client = _mock_http_client(CONFIG_PAYLOAD)
        config = Config(http_client)
        config.fetch_data()

        assert "api_path" not in config._data
        assert "api_version" not in config._data
        assert "api_base_url" not in config._data
        assert "api_url" not in config._data

    def test_local_registry_dict_not_referenced_from_data(self):
        from edgework.endpoints import API_PATH

        http_client = _mock_http_client(CONFIG_PAYLOAD)
        config = Config(http_client)
        config.fetch_data()

        for value in config._data.values():
            assert value is not API_PATH


class TestConfigDelegation:
    """Config and StatsClient.get_config construct identical requests."""

    @pytest.mark.parametrize("lang", ["en", "fr", "fi"])
    def test_model_and_client_urls_are_identical(self, lang):
        model_client = _mock_http_client(CONFIG_PAYLOAD)
        client_client = _mock_http_client(CONFIG_PAYLOAD)

        Config(model_client, lang=lang).fetch_data()
        StatsClient(client_client).get_config(lang=lang)

        assert _captured_url(model_client) == _captured_url(client_client)
        assert _captured_url(model_client) == f"{STATS_API_URL}{lang}/config"
