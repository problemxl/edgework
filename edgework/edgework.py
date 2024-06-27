from edgework.clients.schedule_client import ScheduleClient
from edgework.clients.game_client import GameClient
from edgework.http_client import SyncHttpClient


class Edgework:
    def __init__(self):
        self._client = SyncHttpClient()

        self.schedule: ScheduleClient = ScheduleClient(self._client)
        self.game: GameClient = GameClient(self._client)
