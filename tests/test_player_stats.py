import pytest
from edgework.models.stats import SkaterStats, GoalieStats, TeamStats
from edgework.clients.stats_client import StatsClient


@pytest.fixture
def stats_client():
    return StatsClient()
