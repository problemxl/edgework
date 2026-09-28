"""Mocked tests for GlossaryClient and facade glossary exposure (Task 3)."""

from unittest.mock import Mock, patch

import pytest

from edgework.clients.glossary_client import GlossaryClient
from edgework.const import STATS_API_URL
from edgework.edgework import Edgework
from edgework.endpoints import format_endpoint
from edgework.http_client import HttpClient
from edgework.models.glossary import Glossary, Term


def _glossary_payload():
    """Build a minimal glossary API payload."""
    return {
        "data": [
            {"id": 1, "glossaryTerm": "Power play"},
            {"id": 2, "glossaryTerm": "Penalty kill"},
        ]
    }


class TestGlossaryClient:
    """Mocked route/model tests for the documented /{lang}/glossary route."""

    def setup_method(self):
        """Set up a client with a mocked HTTP layer."""
        self.http_client = Mock(spec=HttpClient)
        self.http_client.get.return_value = Mock(
            json=Mock(return_value=_glossary_payload())
        )
        self.client = GlossaryClient(self.http_client)

    def test_get_glossary_route(self):
        """get_glossary requests the Stats API glossary route with lang=en."""
        glossary = self.client.get_glossary()

        self.http_client.get.assert_called_once_with("glossary", web=False, lang="en")
        assert isinstance(glossary, Glossary)
        assert len(glossary.terms) == 2
        assert all(isinstance(term, Term) for term in glossary.terms)

    def test_get_glossary_term_content(self):
        """Term entries expose the raw API fields."""
        glossary = self.client.get_glossary()

        assert glossary.terms[0]._data["glossaryTerm"] == "Power play"
        assert glossary.terms[1]._data["id"] == 2

    def test_get_glossary_alternate_language(self):
        """The language prefix is controlled by the lang argument."""
        self.client.get_glossary(lang="fr")

        self.http_client.get.assert_called_once_with("glossary", web=False, lang="fr")

    def test_final_url_matches_stats_registry(self):
        """End-to-end URL must equal the stats_glossary registry route."""
        http_client = HttpClient()
        http_client._client = Mock()
        http_client._client.get.return_value = Mock(
            json=Mock(return_value=_glossary_payload())
        )
        GlossaryClient(http_client).get_glossary()

        expected_route = format_endpoint("stats_glossary", lang="en").lstrip("/")
        actual_url = http_client._client.get.call_args.args[0]

        assert actual_url == f"{STATS_API_URL}{expected_route}"
        assert actual_url == f"{STATS_API_URL}en/glossary"


class TestGlossaryFacadeExposure:
    """The Edgework facade must expose a working GlossaryClient."""

    def test_facade_exposes_glossary_client(self):
        """edgework.glossary is a GlossaryClient sharing the facade HTTP client."""
        with patch("edgework.edgework.HttpClient") as mock_http_client:
            edgework = Edgework()

            assert isinstance(edgework.glossary, GlossaryClient)
            assert edgework.glossary._client is mock_http_client.return_value

    def test_facade_glossary_returns_glossary_model(self):
        """Requests through the facade produce a Glossary with Term entries."""
        with patch("edgework.edgework.HttpClient") as mock_http_client:
            http_instance = mock_http_client.return_value
            http_instance.get.return_value = Mock(
                json=Mock(return_value=_glossary_payload())
            )
            edgework = Edgework()

            glossary = edgework.glossary.get_glossary()

            http_instance.get.assert_called_once_with("glossary", web=False, lang="en")
            assert isinstance(glossary, Glossary)
            assert len(glossary.terms) == 2
