from edgework.http_client import HttpClient
from edgework.models.season import Season


class SeasonClient:
    def __init__(self, client: HttpClient):
        self._client = client

    def get_seasons(self) -> list[Season]:
        """Get all NHL seasons.

        Returns
        -------
        list[Season]
            A list of Season objects representing all NHL seasons.

        """
        response = self._client.get("season")
        season_ids = response.json()
        return [Season.from_id(sid) for sid in season_ids]
