from datetime import datetime

import pytest

from edgework.clients.standings_client import StandingClient
from edgework.edgework import Edgework
from edgework.models.standings import Standings, Seeding


@pytest.fixture
def edgework():
    return Edgework()


@pytest.fixture
def standing_client(edgework):
    return StandingClient(edgework.http_client)


@pytest.fixture
def standing(edgework):
    return edgework.standings.get_standings("now")


@pytest.fixture
def sample_seeding():
    return Seeding(
        clinch_indicator="x",
        conference_abbrev="E",
        conference_home_sequence=1,
        conference_l10_sequence=1,
        conference_name="Eastern",
        conference_road_sequence=1,
        conference_sequence=1,
        date="2023-01-01",
        division_abbrev="ATL",
        division_home_sequence=1,
        division_l10_sequence=1,
        division_name="Atlantic",
        division_road_sequence=1,
        division_sequence=1,
        game_type_id=2,
        games_played=82,
        goal_differential=50,
        goal_differential_pctg=0.5,
        goal_against=200,
        goal_for=250,
        goals_for_pctg=0.6,
        home_games_played=41,
        home_goal_differential=30,
        home_goals_against=90,
        home_goals_for=120,
        home_losses=10,
        home_ot_losses=5,
        home_points=55,
        home_regulation_plus_ot_wins=25,
        home_regulation_wins=20,
        home_ties=0,
        home_wins=25,
        l10_games_played=10,
        l10_goal_differential=10,
        l10_goals_against=20,
        l10_goals_for=30,
        l10_losses=2,
        l10_ot_losses=1,
        l10_points=15,
        l10_regulation_plus_ot_wins=7,
        l10_regulation_wins=6,
        l10_ties=0,
        l10_wins=7,
        league_home_sequence=1,
        league_l10_sequence=1,
        league_road_sequence=1,
        league_sequence=1,
        losses=20,
        ot_losses=10,
        place_name={"default": "First Place"},
        point_pctg=0.7,
        points=115,
        regulation_plus_ot_win_pctg=0.6,
        regulation_plus_ot_wins=50,
        regulation_win_pctg=0.5,
        regulation_wins=40,
        road_games_played=41,
        road_goal_differential=20,
        road_goals_against=110,
        road_goals_for=130,
        road_losses=10,
        road_ot_losses=5,
        road_points=60,
        road_regulation_plus_ot_wins=25,
        road_regulation_wins=20,
        road_ties=0,
        road_wins=25,
        season_id=2023,
        shootout_losses=5,
        shootout_wins=5,
        streak_code="W5",
        streak_count=5,
        team_name={"default": "Team A"},
        team_common_name={"default": "Team A"},
        team_abbrev={"default": "TA"},
        team_logo="https://example.com/logo.png",
        ties=0,
        waivers_sequence=1,
        wildcard_sequence=1,
        win_pctg=0.7,
        wins=55
    )


@pytest.fixture
def sample_standings(sample_seeding):
    return Standings(
        season=2023,
        date=datetime(2023, 1, 1),
        seedings=[sample_seeding]
    )


def test_east_standings(sample_standings):
    east_standings = sample_standings.east_standings
    assert len(east_standings) == 1
    assert all(s.conference_abbrev == "E" for s in east_standings)


def test_west_standings(sample_standings):
    west_standings = sample_standings.west_standings
    assert len(west_standings) == 0
    assert all(s.conference_abbrev == "W" for s in west_standings)


def test_real_standings(standing):
    assert standing
    assert isinstance(standing, Standings)
    assert standing.season == -1
    assert standing.date
    assert standing.seedings
    assert all(isinstance(s, Seeding) for s in standing.seedings)
