from datetime import datetime
from typing import List, Dict
from edgework.models.base import BaseNHLModel


class Seeding(BaseNHLModel):
    def __init__(self, edgework_client, obj_id=None, conference_abbrev=None, conference_home_sequence=None,
                 conference_l10_sequence=None, conference_name=None, conference_road_sequence=None,
                 conference_sequence=None, date=None, division_abbrev=None, division_home_sequence=None,
                 division_l10_sequence=None, division_name=None, division_road_sequence=None,
                 division_sequence=None, game_type_id=None, games_played=None, goal_differential=None,
                 goal_differential_pctg=None, goal_against=None, goal_for=None, goals_for_pctg=None,
                 home_games_played=None, home_goal_differential=None, home_goals_against=None,
                 home_goals_for=None, home_losses=None, home_ot_losses=None, home_points=None,
                 home_regulation_plus_ot_wins=None, home_regulation_wins=None, home_ties=None,
                 home_wins=None, l10_games_played=None, l10_goal_differential=None, l10_goals_against=None,
                 l10_goals_for=None, l10_losses=None, l10_ot_losses=None, l10_points=None,
                 l10_regulation_plus_ot_wins=None, l10_regulation_wins=None, l10_ties=None, l10_wins=None,
                 league_home_sequence=None, league_l10_sequence=None, league_road_sequence=None,
                 league_sequence=None, losses=None, ot_losses=None, place_name=None, point_pctg=None,
                 points=None, regulation_plus_ot_win_pctg=None, regulation_plus_ot_wins=None,
                 regulation_win_pctg=None, regulation_wins=None, road_games_played=None,
                 road_goal_differential=None, road_goals_against=None, road_goals_for=None,
                 road_losses=None, road_ot_losses=None, road_points=None, road_regulation_plus_ot_wins=None,
                 road_regulation_wins=None, road_ties=None, road_wins=None, season_id=None,
                 shootout_losses=None, shootout_wins=None, streak_code=None, streak_count=None,
                 team_name=None, team_common_name=None, team_abbrev=None, team_logo=None, ties=None,
                 waivers_sequence=None, wildcard_sequence=None, win_pctg=None, wins=None,
                 clinch_indicator=""):
        """
        Initialize a Seeding object.
        
        Args:
            edgework_client: The Edgework client
            obj_id: The ID of the seeding
            conference_abbrev: Conference abbreviation
            conference_home_sequence: Conference home sequence
            conference_l10_sequence: Conference last 10 games sequence
            conference_name: Conference name
            conference_road_sequence: Conference road sequence
            conference_sequence: Conference sequence
            date: Date of the seeding
            division_abbrev: Division abbreviation
            division_home_sequence: Division home sequence
            division_l10_sequence: Division last 10 games sequence
            division_name: Division name
            division_road_sequence: Division road sequence
            division_sequence: Division sequence
            game_type_id: Game type ID
            games_played: Number of games played
            goal_differential: Goal differential
            goal_differential_pctg: Goal differential percentage
            goal_against: Goals against
            goal_for: Goals for
            goals_for_pctg: Goals for percentage
            home_games_played: Number of home games played
            home_goal_differential: Home goal differential
            home_goals_against: Home goals against
            home_goals_for: Home goals for
            home_losses: Home losses
            home_ot_losses: Home overtime losses
            home_points: Home points
            home_regulation_plus_ot_wins: Home regulation plus overtime wins
            home_regulation_wins: Home regulation wins
            home_ties: Home ties
            home_wins: Home wins
            l10_games_played: Last 10 games played
            l10_goal_differential: Last 10 games goal differential
            l10_goals_against: Last 10 games goals against
            l10_goals_for: Last 10 games goals for
            l10_losses: Last 10 games losses
            l10_ot_losses: Last 10 games overtime losses
            l10_points: Last 10 games points
            l10_regulation_plus_ot_wins: Last 10 games regulation plus overtime wins
            l10_regulation_wins: Last 10 games regulation wins
            l10_ties: Last 10 games ties
            l10_wins: Last 10 games wins
            league_home_sequence: League home sequence
            league_l10_sequence: League last 10 games sequence
            league_road_sequence: League road sequence
            league_sequence: League sequence
            losses: Total losses
            ot_losses: Overtime losses
            place_name: Place name
            point_pctg: Point percentage
            points: Total points
            regulation_plus_ot_win_pctg: Regulation plus overtime win percentage
            regulation_plus_ot_wins: Regulation plus overtime wins
            regulation_win_pctg: Regulation win percentage
            regulation_wins: Regulation wins
            road_games_played: Road games played
            road_goal_differential: Road goal differential
            road_goals_against: Road goals against
            road_goals_for: Road goals for
            road_losses: Road losses
            road_ot_losses: Road overtime losses
            road_points: Road points
            road_regulation_plus_ot_wins: Road regulation plus overtime wins
            road_regulation_wins: Road regulation wins
            road_ties: Road ties
            road_wins: Road wins
            season_id: Season ID
            shootout_losses: Shootout losses
            shootout_wins: Shootout wins
            streak_code: Streak code
            streak_count: Streak count
            team_name: Team name
            team_common_name: Team common name
            team_abbrev: Team abbreviation
            team_logo: Team logo URL
            ties: Total ties
            waivers_sequence: Waivers sequence
            wildcard_sequence: Wildcard sequence
            win_pctg: Win percentage
            wins: Total wins
            clinch_indicator: Clinch indicator
        """
        super().__init__(edgework_client, obj_id)
        self.conference_abbrev = conference_abbrev
        self.conference_home_sequence = conference_home_sequence
        self.conference_l10_sequence = conference_l10_sequence
        self.conference_name = conference_name
        self.conference_road_sequence = conference_road_sequence
        self.conference_sequence = conference_sequence
        self.date = date
        self.division_abbrev = division_abbrev
        self.division_home_sequence = division_home_sequence
        self.division_l10_sequence = division_l10_sequence
        self.division_name = division_name
        self.division_road_sequence = division_road_sequence
        self.division_sequence = division_sequence
        self.game_type_id = game_type_id
        self.games_played = games_played
        self.goal_differential = goal_differential
        self.goal_differential_pctg = goal_differential_pctg
        self.goal_against = goal_against
        self.goal_for = goal_for
        self.goals_for_pctg = goals_for_pctg
        self.home_games_played = home_games_played
        self.home_goal_differential = home_goal_differential
        self.home_goals_against = home_goals_against
        self.home_goals_for = home_goals_for
        self.home_losses = home_losses
        self.home_ot_losses = home_ot_losses
        self.home_points = home_points
        self.home_regulation_plus_ot_wins = home_regulation_plus_ot_wins
        self.home_regulation_wins = home_regulation_wins
        self.home_ties = home_ties
        self.home_wins = home_wins
        self.l10_games_played = l10_games_played
        self.l10_goal_differential = l10_goal_differential
        self.l10_goals_against = l10_goals_against
        self.l10_goals_for = l10_goals_for
        self.l10_losses = l10_losses
        self.l10_ot_losses = l10_ot_losses
        self.l10_points = l10_points
        self.l10_regulation_plus_ot_wins = l10_regulation_plus_ot_wins
        self.l10_regulation_wins = l10_regulation_wins
        self.l10_ties = l10_ties
        self.l10_wins = l10_wins
        self.league_home_sequence = league_home_sequence
        self.league_l10_sequence = league_l10_sequence
        self.league_road_sequence = league_road_sequence
        self.league_sequence = league_sequence
        self.losses = losses
        self.ot_losses = ot_losses
        self.place_name = place_name or {}
        self.point_pctg = point_pctg
        self.points = points
        self.regulation_plus_ot_win_pctg = regulation_plus_ot_win_pctg
        self.regulation_plus_ot_wins = regulation_plus_ot_wins
        self.regulation_win_pctg = regulation_win_pctg
        self.regulation_wins = regulation_wins
        self.road_games_played = road_games_played
        self.road_goal_differential = road_goal_differential
        self.road_goals_against = road_goals_against
        self.road_goals_for = road_goals_for
        self.road_losses = road_losses
        self.road_ot_losses = road_ot_losses
        self.road_points = road_points
        self.road_regulation_plus_ot_wins = road_regulation_plus_ot_wins
        self.road_regulation_wins = road_regulation_wins
        self.road_ties = road_ties
        self.road_wins = road_wins
        self.season_id = season_id
        self.shootout_losses = shootout_losses
        self.shootout_wins = shootout_wins
        self.streak_code = streak_code
        self.streak_count = streak_count
        self.team_name = team_name or {}
        self.team_common_name = team_common_name or {}
        self.team_abbrev = team_abbrev or {}
        self.team_logo = team_logo
        self.ties = ties
        self.waivers_sequence = waivers_sequence
        self.wildcard_sequence = wildcard_sequence
        self.win_pctg = win_pctg
        self.wins = wins
        self.clinch_indicator = clinch_indicator
        
    def fetch_data(self):
        """
        Fetch the data for the seeding.
        """
        # Implementation depends on how data is fetched from the API
        pass
    goal_differential: int = Field(description="Goal differential")
    goal_differential_pctg: float = Field(description="Goal differential percentage")
    goal_against: int = Field(description="Goals against")
    goal_for: int = Field(description="Goals for")
    goals_for_pctg: float = Field(description="Goals for percentage")
    home_games_played: int = Field(description="Number of home games played")
    home_goal_differential: int = Field(description="Home goal differential")
    home_goals_against: int = Field(description="Home goals against")
    home_goals_for: int = Field(description="Home goals for")
    home_losses: int = Field(description="Home losses")
    home_ot_losses: int = Field(description="Home overtime losses")
    home_points: int = Field(description="Home points")
    home_regulation_plus_ot_wins: int = Field(description="Home regulation plus overtime wins")
    home_regulation_wins: int = Field(description="Home regulation wins")
    home_ties: int = Field(description="Home ties")
    home_wins: int = Field(description="Home wins")
    l10_games_played: int = Field(description="Last 10 games played")
    l10_goal_differential: int = Field(description="Last 10 games goal differential")
    l10_goals_against: int = Field(description="Last 10 games goals against")
    l10_goals_for: int = Field(description="Last 10 games goals for")
    l10_losses: int = Field(description="Last 10 games losses")
    l10_ot_losses: int = Field(description="Last 10 games overtime losses")
    l10_points: int = Field(description="Last 10 games points")
    l10_regulation_plus_ot_wins: int = Field(description="Last 10 games regulation plus overtime wins")
    l10_regulation_wins: int = Field(description="Last 10 games regulation wins")
    l10_ties: int = Field(description="Last 10 games ties")
    l10_wins: int = Field(description="Last 10 games wins")
    league_home_sequence: int = Field(description="League home sequence")
    league_l10_sequence: int = Field(description="League last 10 games sequence")
    league_road_sequence: int = Field(description="League road sequence")
    league_sequence: int = Field(description="League sequence")
    losses: int = Field(description="Total losses")
    ot_losses: int = Field(description="Overtime losses")
    place_name: Dict = Field(description="Place name")
    point_pctg: float = Field(description="Point percentage")
    points: int = Field(description="Total points")
    regulation_plus_ot_win_pctg: float = Field(description="Regulation plus overtime win percentage")
    regulation_plus_ot_wins: int = Field(description="Regulation plus overtime wins")
    regulation_win_pctg: float = Field(description="Regulation win percentage")
    regulation_wins: int = Field(description="Regulation wins")
    road_games_played: int = Field(description="Road games played")
    road_goal_differential: int = Field(description="Road goal differential")
    road_goals_against: int = Field(description="Road goals against")
    road_goals_for: int = Field(description="Road goals for")
    road_losses: int = Field(description="Road losses")
    road_ot_losses: int = Field(description="Road overtime losses")
    road_points: int = Field(description="Road points")
    road_regulation_plus_ot_wins: int = Field(description="Road regulation plus overtime wins")
    road_regulation_wins: int = Field(description="Road regulation wins")
    road_ties: int = Field(description="Road ties")
    road_wins: int = Field(description="Road wins")
    season_id: int = Field(description="Season ID")
    shootout_losses: int = Field(description="Shootout losses")
    shootout_wins: int = Field(description="Shootout wins")
    streak_code: str = Field(description="Streak code")
    streak_count: int = Field(description="Streak count")
    team_name: Dict = Field(description="Team name")
    team_common_name: Dict = Field(description="Team common name")
    team_abbrev: Dict = Field(description="Team abbreviation")
    team_logo: str = Field(description="Team logo URL")
    ties: int = Field(description="Total ties")
    waivers_sequence: int = Field(description="Waivers sequence")
    wildcard_sequence: int = Field(description="Wildcard sequence")
    win_pctg: float = Field(description="Win percentage")
    wins: int = Field(description="Total wins")
    clinch_indicator: str = Field(description="Clinch indicator", default="")


class Standings(BaseNHLModel):
    def __init__(self, edgework_client, obj_id=None, date=None, seedings=None, season=-1):
        """
        Initialize a Standings object.
        
        Args:
            edgework_client: The Edgework client
            obj_id: The ID of the standings
            date: Date of the standings
            seedings: List of seedings
            season: Season
        """
        super().__init__(edgework_client, obj_id)
        self.date = date
        self.seedings = seedings or []
        self.season = season

    @property
    def east_standings(self):
        return [s for s in self.seedings if s.conference_abbrev == "E"]

    @property
    def west_standings(self):
        return [s for s in self.seedings if s.conference_abbrev == "W"]
        
    def fetch_data(self):
        """
        Fetch the data for the standings.
        """
        # Implementation depends on how data is fetched from the API
        pass
