from edgework.http_client import AsyncHttpClient
from edgework.models.schedule import Schedule

class ScheduleClient:
    def __init__(self, client: AsyncHttpClient):
        self._client = client

    async def get_schedule(self) -> Schedule:
        response = await self._client.get('schedule')
        return Schedule.from_dict(response.json())