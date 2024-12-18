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
        if params is None:
            params = {}
        if web:
            return self.client.get(f"{self.WEB_BASE_URL}/{self.API_VERSION}/{path}", params=params,
                                   follow_redirects=True)
        return self.client.get(f"{self.API_BASE_URL}/stats/{path}", params=params, follow_redirects=True)

    def get_raw(self, url: str, params=None) -> httpx.Response:
        if params is None:
            params = {}
        return self.client.get(url, params=params, follow_redirects=True)

    def __del__(self):
        self.client.close()


class AsyncHttpClient(HttpClient):
    def __init__(self):
        self.client = httpx.AsyncClient()

    async def get(self, path: str, params: dict = {}) -> httpx.Response:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            # print(f"{self.WEB_BASE_URL}/{self.API_VERSION}/{path}")
            return await client.get(f"{self.WEB_BASE_URL}/{self.API_VERSION}/{path}", params=params)     
