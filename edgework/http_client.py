"""HTTP client for making requests to NHL APIs."""

from typing import Any, Dict, Optional

import httpx

from . import __version__


class HttpClient:
    """Base HTTP client for NHL API requests."""

    def __init__(self, user_agent: str = f"EdgeworkClient/{__version__}"):
        """
        Initialize the HTTP client.

        Args:
            user_agent: User agent string for requests
        """
        self._user_agent = user_agent
        self._base_url = "https://api-web.nhle.com/v1/"
        self._stats_base_url = "https://api.nhle.com/stats/rest/en/"
        self._client = httpx.Client(
            headers={"User-Agent": self._user_agent}, follow_redirects=True
        )

    def get(
        self,
        endpoint: str,
        path: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        web: bool = False,
    ) -> httpx.Response:
        """
        Make a GET request to an NHL API endpoint.

        Args:
            endpoint: API endpoint (without base URL)
            path: Optional full path to override endpoint
            params: Optional query parameters
            web: If True, use the web API base URL

        Returns:
            httpx.Response object
        """
        url = f"{self._base_url if web else self._stats_base_url}{path or endpoint}"

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
        url = f"{self._base_url if web else self._stats_base_url}{path}"

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


class SyncHttpClient(HttpClient):
    """Synchronous HTTP client - alias for backward compatibility."""

    pass
