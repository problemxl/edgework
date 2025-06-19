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
    def __init__(self, user_agent: str = "EdgeworkClient/1.0"):
        self.client = httpx.Client(
            headers={"User-Agent": user_agent},
            follow_redirects=True
        )

    def get(self, path: str, params=None, web=True) -> httpx.Response:        
        url_to_request: str
        # Ensure path is relative and doesn't cause double slashes
        relative_path = path.lstrip('/')
        if web:
            url_to_request = f"{self.WEB_BASE_URL}/{self.API_VERSION}/{relative_path}"
        else:
            url_to_request = f"{self.API_BASE_URL}/stats/rest/{relative_path}"
        
        if params is None:
            params = {}
        return self.client.get(url_to_request, params=params, follow_redirects=True)

    def get_raw(self, url: str, params=None) -> httpx.Response:
        if params is None:
            params = {}
        return self.client.get(url, params=params, follow_redirects=True)

    def close(self):
        """Closes the underlying HTTPX client."""
        if hasattr(self, 'client') and self.client is not None:
            self.client.close()