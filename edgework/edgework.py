from edgework.clients.schedule_client import ScheduleClient
from edgework.http_client import AsyncHttpClient


class Edgework:
    def __init__(self):
        self._client = AsyncHttpClient()

        self.schedule: ScheduleClient = ScheduleClient(self._client)