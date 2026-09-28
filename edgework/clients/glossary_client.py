"""Glossary client for the NHL Stats API."""

from edgework.http_client import HttpClient
from edgework.models.glossary import Glossary, Term


class GlossaryClient:
    """Client for the documented ``/{lang}/glossary`` Stats API route."""

    def __init__(self, client: HttpClient):
        self._client = client

    def get_glossary(self, lang: str = "en") -> Glossary:
        """Fetch the glossary for a language.

        Args:
            lang: Language code for the Stats API request (default "en").

        Returns:
            Glossary object containing Term entries.
        """
        response = self._client.get("glossary", web=False, lang=lang)
        terms = [
            Term(edgework_client=self._client, **term)
            for term in response.json()["data"]
        ]
        return Glossary(edgework_client=self._client, terms=terms)
