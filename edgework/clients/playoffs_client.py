from edgework.http_client import HttpClient
from edgework.models.playoffs import PlayoffBracket


class PlayoffsClient:
    def __init__(self, client: HttpClient):
        self._client = client

    def get_bracket(self, season: int) -> PlayoffBracket:
        """Get playoff bracket for a given season.

        Parameters
        ----------
        season : int
            The season in YYYYYYYY format (e.g., 20232024).

        Returns
        -------
        PlayoffBracket
            A PlayoffBracket object containing all playoff series for the season.

        """
        response = self._client.get(f"playoff-bracket/{season}")
        return PlayoffBracket.from_api(response.json())
