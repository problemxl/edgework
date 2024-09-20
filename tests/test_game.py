import pytest

from edgework.edgework import Edgework
from edgework.models.game import Game
from edgework.models.shift import Shift


@pytest.fixture
def edgework() -> Edgework:
    return Edgework()


@pytest.fixture
def game(edgework) -> Game:
    return edgework.game.get_game(2023020038)


def test_get_game(edgework, game: Game):
    assert game.game_id == 2023020038
    assert game.game_date
    assert game.start_time_utc
    assert game.game_state
    assert game.away_team_abbrev
    assert game.away_team_id
    assert game.away_team_score
    assert game.home_team_abbrev
    assert game.home_team_id
    assert game.home_team_score
    assert game.season
    assert game.venue

    assert str(game) == f"{game.away_team_abbrev} @ {game.home_team_abbrev} | {game.game_time} | {game.away_team_score} - {game.home_team_score}"


def test_get_shifts(edgework, game):
    shifts = game.shifts
    assert shifts
    assert isinstance(shifts, list)
    assert all(isinstance(shift, Shift) for shift in shifts)
    assert all(shift.game_id == game.game_id for shift in shifts)
    assert all(shift.team_abbrev in [game.away_team_abbrev, game.home_team_abbrev] for shift in shifts)

    assert len(shifts) == 741
