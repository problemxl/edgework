"""HTTP client for making requests to NHL APIs."""

from typing import Any, Dict, Optional

import httpx

from . import __version__
from .const import BASE_API_URL, BASE_WEB_URL, STATS_API_URL

# Legacy route prefixes that older callers may still embed in endpoint paths.
# They are stripped before the canonical URL is assembled so that routes such
# as ``stats/rest/en/glossary`` resolve to ``{STATS_API_URL}/en/glossary``.
_LEGACY_ROUTE_PREFIXES = ("stats/rest/", "rest/")

# Route prefix served outside the versioned Web API namespace (the OpenAPI
# specification lives at ``https://api-web.nhle.com/model/v1/openapi.json``).
_UNVERSIONED_WEB_PREFIX = "model/"


def _strip_legacy_prefixes(target: str) -> str:
    """Strip legacy ``stats/rest/``, ``rest/`` and ``en/`` route prefixes."""
    target = target.lstrip("/")
    changed = True
    while changed:
        changed = False
        for prefix in _LEGACY_ROUTE_PREFIXES:
            if target.startswith(prefix):
                target = target[len(prefix) :]
                changed = True
        if target.startswith("en/"):
            target = target[len("en/") :]
            changed = True
    return target


class HttpClient:
    """Base HTTP client for NHL API requests."""

    def __init__(self, user_agent: str = f"EdgeworkClient/{__version__}"):
        """
        Initialize the HTTP client.

        Args:
            user_agent: User agent string for requests
        """
        self._user_agent = user_agent
        self._client = httpx.Client(
            headers={"User-Agent": self._user_agent}, follow_redirects=True
        )

    def get(
        self,
        endpoint: str,
        path: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        web: bool = False,
        lang: Optional[str] = "en",
    ) -> httpx.Response:
        """
        Make a GET request to an NHL API endpoint.

        Args:
            endpoint: API endpoint (without base URL)
            path: Optional full path to override endpoint
            params: Optional query parameters. Query parameters must always be
                passed here (they are never embedded in the route string).
            web: If True, use the web API base URL
            lang: Language code for Stats API requests (default ``"en"``).
                Pass ``None`` for Stats routes that are not language-prefixed
                (e.g. ``/ping``). Ignored for Web API requests.

        Returns:
            httpx.Response object
        """
        target = path or endpoint

        if web:
            target = target.lstrip("/")
            if target.startswith(_UNVERSIONED_WEB_PREFIX):
                # The OpenAPI spec is served outside the /{version} namespace.
                url = f"{BASE_WEB_URL}/{target}"
            else:
                url = f"{BASE_WEB_URL}/v1/{target}"
        else:
            target = _strip_legacy_prefixes(target)
            if target.startswith(_UNVERSIONED_WEB_PREFIX):
                url = f"{STATS_API_URL}{target}"
            elif lang:
                url = f"{STATS_API_URL}{lang}/{target}"
            else:
                url = f"{STATS_API_URL}{target}"

        response = self._client.get(url, params=params)
        response.raise_for_status()
        return response

    def get_raw(
        self, url: str, params: Optional[Dict[str, Any]] = None
    ) -> httpx.Response:
        """
        Make a GET request to a raw URL.

        Args:
            url: Full URL to request
            params: Optional query parameters

        Returns:
            httpx.Response object
        """
        response = self._client.get(url, params=params)
        response.raise_for_status()
        return response

    def get_with_path(
        self, path: str, params: Optional[Dict[str, Any]] = None, web: bool = False
    ) -> httpx.Response:
        """
        Make a GET request using a full path.

        Args:
            path: Full path including query parameters
            params: Optional query parameters
            web: If True, use the web API base URL

        Returns:
            httpx.Response object
        """
        url = f"{BASE_API_URL if web else STATS_API_URL}{path}"

        response = self._client.get(url, params=params)
        response.raise_for_status()
        return response

    def close(self):
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
