from edgework.http_client import HttpClient
from edgework.models.shift import Shift


class ShiftClient:
    def __init__(self, client: HttpClient):
        self._client = client

    def get_shifts(self, game_id: int) -> list[Shift]:
        """Get the shift chart data for a given game.

        Parameters
        ----------
        game_id : int
            The ID of the game.

        Returns
        -------
        list[Shift]
            A list of Shift objects representing the shift chart data.

        """
        response = self._client.get(
            f"rest/en/shiftcharts?cayenneExp=gameId={game_id}", web=False
        )
        data = response.json()["data"]
        shifts = [Shift.from_api(d) for d in data]
        return shifts
