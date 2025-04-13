from datetime import datetime, timedelta
from typing import Optional
from edgework.models.base import BaseNHLModel


class SkaterStats(BaseNHLModel):
    """
    SkaterStats model to store skater statistics.
    """
    def __init__(self, edgework_client, obj_id=None, game_id=None, player_id=None, player_name=None,
                 team_id=None, position=None, goals=None, assists=None, points=None, plus_minus=None,
                 pim=None, hits=None, blocked_shots=None, power_play_goals=None, power_play_points=None,
                 short_handed_goals=None, short_handed_points=None, shots=None, faceoff_wins=None,
                 faceoff_losses=None, faceoff_total=None, faceoff_percentage=None, time_on_ice=None,
                 power_play_toi=None, short_handed_toi=None):
        """
        Initialize a SkaterStats object.
        
        Args:
            edgework_client: The Edgework client
            obj_id: The ID of the skater stats
            game_id: Unique identifier for the game the skater is in
            player_id: Unique identifier for the player
            player_name: Name of the player
            team_id: Unique identifier for the team the player is on
            position: Position the player plays
            goals: Number of goals the player has scored
            assists: Number of assists the player has
            points: Total number of combined goals and assists the player has
            plus_minus: Player's plus/minus rating
            pim: Number of penalties the player has taken
            hits: Number of hits the player has made
            blocked_shots: Number of shots the player has blocked
            power_play_goals: Number of power play goals the player has scored
            power_play_points: Number of power play points the player has
            short_handed_goals: Number of short handed goals the player has scored
            short_handed_points: Number of short handed points the player has
            shots: Number of shots the player has taken
            faceoff_wins: Number of faceoffs the player has won
            faceoff_losses: Number of faceoffs the player has lost
            faceoff_total: Total number of faceoffs the player has taken
            faceoff_percentage: Percentage of faceoffs the player has won
            time_on_ice: Total amount of time the player has spent on the ice
            power_play_toi: Total amount of time the player has spent on the ice during power plays
            short_handed_toi: Total amount of time the player has spent on the ice during short handed situations
        """
        super().__init__(edgework_client, obj_id)
        self.game_id = game_id
        self.player_id = player_id
        self.player_name = player_name
        self.team_id = team_id
        self.position = position
        self.goals = goals
        self.assists = assists
        self.points = points
        self.plus_minus = plus_minus
        self.pim = pim
        self.hits = hits
        self.blocked_shots = blocked_shots
        self.power_play_goals = power_play_goals
        self.power_play_points = power_play_points
        self.short_handed_goals = short_handed_goals
        self.short_handed_points = short_handed_points
        self.shots = shots
        self.faceoff_wins = faceoff_wins
        self.faceoff_losses = faceoff_losses
        self.faceoff_total = faceoff_total
        self.faceoff_percentage = faceoff_percentage
        self.time_on_ice = time_on_ice
        self.power_play_toi = power_play_toi
        self.short_handed_toi = short_handed_toi
        
    def fetch_data(self):
        """
        Fetch the data for the skater stats.
        """
        # Implementation depends on how data is fetched from the API
        pass


class GoalieStats(BaseNHLModel):
    """
    GoalieStats model to store goalie statistics.
    """
    def __init__(self, edgework_client, obj_id=None, assists=None, game_date=None, game_id=None,
                 games_played=None, games_started=None, goalie_full_name=None, goals=None,
                 goals_against=None, goals_against_average=None, home_road=None, last_name=None,
                 losses=None, opponent_team_abbrev=None, ot_losses=None, penalty_minutes=None,
                 player_id=None, points=None, save_pct=None, saves=None, shoots_catches=None,
                 shots_against=None, shutouts=None, team_abbrev=None, ties=None, time_on_ice=None,
                 wins=None):
        """
        Initialize a GoalieStats object.
        
        Args:
            edgework_client: The Edgework client
            obj_id: The ID of the goalie stats
            assists: Number of assists the goalie has
            game_date: Date of the game
            game_id: Unique identifier for the game
            games_played: Number of games the goalie has played
            games_started: Number of games the goalie has started
            goalie_full_name: Full name of the goalie
            goals: Number of goals the goalie has scored
            goals_against: Number of goals scored against the goalie
            goals_against_average: Average goals against per game
            home_road: Whether the game was home or away
            last_name: Last name of the goalie
            losses: Number of losses
            opponent_team_abbrev: Abbreviation of the opponent team
            ot_losses: Number of overtime losses
            penalty_minutes: Number of penalty minutes
            player_id: Unique identifier for the player
            points: Total points (goals + assists)
            save_pct: Save percentage
            saves: Number of saves
            shoots_catches: Which hand the goalie catches with
            shots_against: Number of shots against
            shutouts: Number of shutouts
            team_abbrev: Abbreviation of the goalie's team
            ties: Number of ties
            time_on_ice: Time on ice in seconds
            wins: Number of wins
        """
        super().__init__(edgework_client, obj_id)
        self.assists = assists
        self.game_date = game_date
        self.game_id = game_id
        self.games_played = games_played
        self.games_started = games_started
        self.goalie_full_name = goalie_full_name
        self.goals = goals
        self.goals_against = goals_against
        self.goals_against_average = goals_against_average
        self.home_road = home_road
        self.last_name = last_name
        self.losses = losses
        self.opponent_team_abbrev = opponent_team_abbrev
        self.ot_losses = ot_losses
        self.penalty_minutes = penalty_minutes
        self.player_id = player_id
        self.points = points
        self.save_pct = save_pct
        self.saves = saves
        self.shoots_catches = shoots_catches
        self.shots_against = shots_against
        self.shutouts = shutouts
        self.team_abbrev = team_abbrev
        self.ties = ties
        self.time_on_ice = time_on_ice
        self.wins = wins
        
    def fetch_data(self):
        """
        Fetch the data for the goalie stats.
        """
        # Implementation depends on how data is fetched from the API
        pass


class TeamStats(BaseNHLModel):
    """Team Stats model to store team statistics for a season."""
    def __init__(self, edgework_client, obj_id=None, team_id=None, team_full_name=None, season=None,
                 games_played=None, points=None, points_percentage=None, wins=None, losses=None,
                 ties=None, wins_regulation=None, wins_overtime=None, wins_shootout=None,
                 wins_regulation_plus_overtime=None, losses_regulation=None, losses_overtime=None,
                 losses_shootout=None, goals_for=None, goals_for_per_game=None, goals_against=None,
                 goals_against_per_game=None, goal_differential=None, shots_for=None,
                 shots_for_per_game=None, shots_against=None, shots_against_per_game=None,
                 power_play_percentage=None, power_play_net_percentage=None, penalty_kill_percentage=None,
                 penalty_kill_net_percentage=None, faceoff_win_percentage=None):
        """
        Initialize a TeamStats object.
        
        Args:
            edgework_client: The Edgework client
            obj_id: The ID of the team stats
            team_id: Unique identifier for the team
            team_full_name: Full name of the team
            season: Season for these statistics
            games_played: Number of games played
            points: Total points
            points_percentage: Percentage of possible points earned
            wins: Total wins
            losses: Total losses
            ties: Total ties
            wins_regulation: Wins in regulation time
            wins_overtime: Wins in overtime
            wins_shootout: Wins in shootout
            wins_regulation_plus_overtime: Combined regulation and overtime wins
            losses_regulation: Losses in regulation time
            losses_overtime: Losses in overtime
            losses_shootout: Losses in shootout
            goals_for: Total goals scored
            goals_for_per_game: Average goals scored per game
            goals_against: Total goals allowed
            goals_against_per_game: Average goals allowed per game
            goal_differential: Goal differential (goals for - goals against)
            shots_for: Total shots taken
            shots_for_per_game: Average shots taken per game
            shots_against: Total shots against
            shots_against_per_game: Average shots against per game
            power_play_percentage: Power play conversion percentage
            power_play_net_percentage: Power play net percentage
            penalty_kill_percentage: Penalty kill percentage
            penalty_kill_net_percentage: Penalty kill net percentage
            faceoff_win_percentage: Percentage of faceoffs won
        """
        super().__init__(edgework_client, obj_id)
        self.team_id = team_id
        self.team_full_name = team_full_name
        self.season = season
        self.games_played = games_played
        self.points = points
        self.points_percentage = points_percentage
        self.wins = wins
        self.losses = losses
        self.ties = ties
        self.wins_regulation = wins_regulation
        self.wins_overtime = wins_overtime
        self.wins_shootout = wins_shootout
        self.wins_regulation_plus_overtime = wins_regulation_plus_overtime
        self.losses_regulation = losses_regulation
        self.losses_overtime = losses_overtime
        self.losses_shootout = losses_shootout
        self.goals_for = goals_for
        self.goals_for_per_game = goals_for_per_game
        self.goals_against = goals_against
        self.goals_against_per_game = goals_against_per_game
        self.goal_differential = goal_differential
        self.shots_for = shots_for
        self.shots_for_per_game = shots_for_per_game
        self.shots_against = shots_against
        self.shots_against_per_game = shots_against_per_game
        self.power_play_percentage = power_play_percentage
        self.power_play_net_percentage = power_play_net_percentage
        self.penalty_kill_percentage = penalty_kill_percentage
        self.penalty_kill_net_percentage = penalty_kill_net_percentage
        self.faceoff_win_percentage = faceoff_win_percentage
        
    def fetch_data(self):
        """
        Fetch the data for the team stats.
        """
        # Implementation depends on how data is fetched from the API
        pass
