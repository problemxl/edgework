from datetime import datetime
import pytest

from edgework.edgework import Edgework
from edgework.models.schedule import Schedule

@pytest.fixture
def edgework():
    return Edgework()


def test_get_schedule(edgework):
    schedule: Schedule = edgework.schedule.get_schedule()
    assert isinstance(schedule, Schedule)
    assert schedule.previous_start_date
    assert schedule.games
    assert schedule.pre_season_start_date
    assert schedule.regular_season_start_date
    assert schedule.regular_season_end_date
    assert schedule.playoff_end_date
    assert schedule.number_of_games
    assert len(schedule.games) == schedule.number_of_games

def test_schedule_initialization():
    previous_start_date = datetime.now()
    games = [{"game": "game1"}, {"game": "game2"}]
    pre_season_start_date = datetime.now()
    regular_season_start_date = datetime.now()
    regular_season_end_date = datetime.now()
    playoff_end_date = datetime.now()
    number_of_games = 2

    schedule = Schedule(
        previous_start_date,
        games,
        pre_season_start_date,
        regular_season_start_date,
        regular_season_end_date,
        playoff_end_date,
        number_of_games,
    )

    assert schedule.previous_start_date == previous_start_date
    assert schedule.games == games
    assert schedule.pre_season_start_date == pre_season_start_date
    assert schedule.regular_season_start_date == regular_season_start_date
    assert schedule.regular_season_end_date == regular_season_end_date
    assert schedule.playoff_end_date == playoff_end_date
    assert schedule.number_of_games == number_of_games

def test_schedule_from_dict():
    data = {
        "previousStartDate": "2021-01-01",
        "gameWeek": [{"games": ["game1", "game2"]}, {"games": ["game3", "game4"]}],
        "preSeasonStartDate": "2021-01-01",
        "regularSeasonStartDate": "2021-01-01",
        "regularSeasonEndDate": "2021-01-01",
        "playoffEndDate": "2021-01-01",
        "numberOfGames": 2,
    }

    schedule = Schedule.from_dict(data)

    assert schedule.previous_start_date == datetime.fromisoformat(data["previousStartDate"])
    assert schedule.games == ['game1', 'game2', 'game3', 'game4']
    assert schedule.pre_season_start_date == datetime.fromisoformat(data["preSeasonStartDate"])
    assert schedule.regular_season_start_date == datetime.fromisoformat(data["regularSeasonStartDate"])
    assert schedule.regular_season_end_date == datetime.fromisoformat(data["regularSeasonEndDate"])
    assert schedule.playoff_end_date == datetime.fromisoformat(data["playoffEndDate"])
    assert schedule.number_of_games == data["numberOfGames"]

def test_get_schedule_for_date(edgework):
    date = "2023-10-13"
    schedule: Schedule = edgework.schedule.get_schedule_for_date(date)
    assert isinstance(schedule, Schedule)
    assert schedule.previous_start_date
    assert schedule.games
    assert schedule.pre_season_start_date
    assert schedule.regular_season_start_date
    assert schedule.regular_season_end_date
    assert schedule.playoff_end_date
    assert schedule.number_of_games
    assert len(schedule.games) == schedule.number_of_games

def tests_get_schedule_for_date_invalid_date(edgework):
    date = "2021-01-01-01"
    with pytest.raises(ValueError):
        edgework.schedule.get_schedule_for_date(date)

def test_get_schedule_for_date_range(edgework):
    start_date = "2021-01-01"
    end_date = "2021-01-02"
    schedule: Schedule = edgework.schedule.get_schedule_for_date_range(start_date, end_date)
    print(schedule.games)
    assert isinstance(schedule, Schedule)
    assert schedule.previous_start_date
    assert schedule.games == []
    assert schedule.regular_season_start_date
    assert schedule.regular_season_end_date
    assert schedule.playoff_end_date
    assert schedule.number_of_games is not None
    assert len(schedule.games) == schedule.number_of_games

def test_get_schedule_for_team(edgework):
    team_abbr = "TOR"
    schedule: Schedule = edgework.schedule.get_schedule_for_team(team_abbr)
    assert isinstance(schedule, Schedule)
    assert schedule.games is not None
    assert schedule.number_of_games is not None
    assert len(schedule.games) == schedule.number_of_games