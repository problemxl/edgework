import pytest

from edgework.clients.game_client import GameClient
from edgework.edgework import Edgework
from edgework.models.game import Game

@pytest.fixture
def edgework():
    return Edgework()


def test_get_game(edgework):
    game: Game = edgework.game.get_game(2023020038)
    assert isinstance(game, Game)
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