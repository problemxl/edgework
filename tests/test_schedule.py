import pytest

from edgework.http_client import AsyncHttpClient
from edgework.edgework import Edgework
from edgework.clients.schedule_client import ScheduleClient
from edgework.models.schedule import Schedule

@pytest.fixture
def edgework():
    return Edgework()

@pytest.mark.asyncio
async def test_get_schedule(edgework):
    schedule: Schedule = await edgework.schedule.get_schedule()
    assert isinstance(schedule, Schedule)
    assert schedule.next_start_date
    assert schedule.previous_start_date
    assert schedule.games
    assert schedule.pre_season_start_date
    assert schedule.regular_season_start_date
    assert schedule.regular_season_end_date
    assert schedule.playoff_end_date
    assert schedule.number_of_games
    assert len(schedule.games) == schedule.number_of_games