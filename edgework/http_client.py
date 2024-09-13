from abc import ABC, abstractmethod
import httpx

class AbstractHttpClient(ABC):
    WEB_BASE_URL: str = "https://api-web.nhle.com"
    API_BASE_URL: str = "https://api.nhle.com"
    API_VERSION: str = "v1"

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def get(self, path: str, params: dict):
        pass


class SyncHttpClient(AbstractHttpClient):
    def __init__(self):
        self.client = httpx.Client()

    def get(self, path: str, params: dict = {}) -> httpx.Response:
        with httpx.Client(follow_redirects=True) as client:
            # print(f"{self.WEB_BASE_URL}/{self.API_VERSION}/{path}")
            return client.get(f"{self.WEB_BASE_URL}/{self.API_VERSION}/{path}", params=params)


class AsyncHttpClient(AbstractHttpClient):
    def __init__(self):
        self.client = httpx.AsyncClient()

    async def get(self, path: str, params: dict = {}) -> httpx.Response:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            # print(f"{self.WEB_BASE_URL}/{self.API_VERSION}/{path}")
            return await client.get(f"{self.WEB_BASE_URL}/{self.API_VERSION}/{path}", params=params)     
