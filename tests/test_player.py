from datetime import datetime

import pytest

from edgework.models.player import Player


@pytest.fixture
def player():
    return Player(
        player_id=1,
        player_slug="player-slug",
        birth_city="City",
        birth_country="Country",
        birth_date=datetime(1990, 1, 1),
        birth_state_province="State",
        current_team_abbr="CT",
        current_team_id=100,
        current_team_name="Current Team",
        draft_overall_pick=1,
        draft_pick=1,
        draft_round=1,
        draft_team_abbr="DT",
        draft_year=datetime(2010, 1, 1),
        first_name="First",
        last_name="Last",
        headshot_url="http://example.com/headshot.jpg",
        height=72,
        hero_image_url="http://example.com/hero.jpg",
        is_active=True,
        position="Forward",
        shoots_catches="Right",
        sweater_number=10,
        weight=200
    )


def test_player_initialization(player):
    assert player.player_id == 1
    assert player.player_slug == "player-slug"
    assert player.birth_city == "City"
    assert player.birth_country == "Country"
    assert player.birth_date == datetime(1990, 1, 1)
    assert player.birth_state_province == "State"
    assert player.current_team_abbr == "CT"
    assert player.current_team_id == 100
    assert player.current_team_name == "Current Team"
    assert player.draft_overall_pick == 1
    assert player.draft_pick == 1
    assert player.draft_round == 1
    assert player.draft_team_abbr == "DT"
    assert player.draft_year == datetime(2010, 1, 1)
    assert player.first_name == "First"
    assert player.last_name == "Last"
    assert player.headshot_url == "http://example.com/headshot.jpg"
    assert player.height == 72
    assert player.hero_image_url == "http://example.com/hero.jpg"
    assert player.is_active is True
    assert player.position == "Forward"
    assert player.shoots_catches == "Right"
    assert player.sweater_number == 10
    assert player.weight == 200


def test_full_name(player):
    assert player.full_name == "First Last"


def test_str_representation(player):
    assert str(player) == "First Last CT"


def test_repr_representation(player):
    assert repr(player) == "Player(First Last, 1)"
