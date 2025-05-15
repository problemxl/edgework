import threading
from abc import ABC, abstractmethod

import httpx


class HttpClient(ABC):
    WEB_BASE_URL: str = "https://api-web.nhle.com"
    API_BASE_URL: str = "https://api.nhle.com"
    API_VERSION: str = "v1"

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def get(self, path: str, params: dict, web: bool) -> httpx.Response:
        pass


class SyncHttpClient(HttpClient):
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(SyncHttpClient, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'client'):
            self.client = httpx.Client()

    def get(self, path: str, params=None, web=True) -> httpx.Response:        
        url_to_request: str
        if web:
            url_to_request = f"{self.WEB_BASE_URL}/{self.API_VERSION}/{path}"
        else:
            url_to_request = f"{self.API_BASE_URL}/stats/rest/{path}"
        return self.client.get(url_to_request, params=params, follow_redirects=True)

    def get_raw(self, url: str, params=None) -> httpx.Response:
        if params is None:
            params = {}
        return self.client.get(url, params=None, follow_redirects=True)
    def __del__(self):
        self.client.close()


class AsyncHttpClient(HttpClient):
    def __init__(self):
        self.client = httpx.AsyncClient(
            headers={"User-Agent": "EdgeworkClient/1.0"},  # Added User-Agent for consistency
            follow_redirects=True  # Set default follow_redirects here
        )

    async def get(self, path: str, params: dict = None) -> httpx.Response: # Changed default params to None
        if params is None:
            params = {}
        # This client, as originally written, always targets WEB_BASE_URL
        # Ensure path is relative and doesn't cause double slashes
        url_to_request = f"{self.WEB_BASE_URL}/{self.API_VERSION}/{path.lstrip('/')}"
        # print(f"Async requesting URL: {url_to_request}") # Optional: for debugging
        return await self.client.get(url_to_request, params=params) # Use self.client, follow_redirects is now default

    async def close(self):
        """Close the underlying HTTPX client."""
        if hasattr(self, 'client') and self.client is not None:
            await self.client.aclose()
