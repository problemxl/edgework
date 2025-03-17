from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, Field


class SkaterStats(BaseModel):
    """
    SkaterStats model to store skater statistics.
    """
    game_id: int = Field(description="Unique identifier for the game the skater is in")
    player_id: int = Field(description="Unique identifier for the player")
    player_name: str = Field(description="Name of the player")
    team_id: int = Field(description="Unique identifier for the team the player is on")
    position: str = Field(description="Position the player plays")
    goals: int = Field(description="Number of goals the player has scored")
    assists: int = Field(description="Number of assists the player has")
    points: int = Field(description="Total number of combined goals and assists the player has")
    plus_minus: int = Field(
        description="Player's plus/minus rating. A positive number means the player's team has "
                    "scored more goals while the player is on the ice than the opposing team. "
                    "A negative number means the opposing team has scored more goals while the "
                    "player is on the ice than the player's team"
    )
    pim: int = Field(description="Number of penalties the player has taken")
    hits: int = Field(description="Number of hits the player has made")
    blocked_shots: int = Field(description="Number of shots the player has blocked")
    power_play_goals: int = Field(description="Number of power play goals the player has scored")
    power_play_points: int = Field(description="Number of power play points the player has")
    short_handed_goals: int = Field(description="Number of short handed goals the player has scored")
    short_handed_points: int = Field(description="Number of short handed points the player has")
    shots: int = Field(description="Number of shots the player has taken")
    faceoff_wins: int = Field(description="Number of faceoffs the player has won")
    faceoff_losses: int = Field(description="Number of faceoffs the player has lost")
    faceoff_total: int = Field(description="Total number of faceoffs the player has taken")
    faceoff_percentage: float = Field(description="Percentage of faceoffs the player has won")
    time_on_ice: timedelta = Field(description="Total amount of time the player has spent on the ice")
    power_play_toi: timedelta = Field(description="Total amount of time the player has spent on the ice during power plays")
    short_handed_toi: timedelta = Field(
        description="Total amount of time the player has spent on the ice during short handed situations"
    )


class GoalieStats(BaseModel):
    """
    GoalieStats model to store goalie statistics.
    """
    assists: int = Field(description="Number of assists the goalie has")
    game_date: datetime = Field(description="Date of the game")
    game_id: int = Field(description="Unique identifier for the game")
    games_played: int = Field(description="Number of games the goalie has played")
    games_started: int = Field(description="Number of games the goalie has started")
    goalie_full_name: str = Field(description="Full name of the goalie")
    goals: int = Field(description="Number of goals the goalie has scored")
    goals_against: int = Field(description="Number of goals scored against the goalie")
    goals_against_average: float = Field(description="Average goals against per game")
    home_road: str = Field(description="Whether the game was home or away")
    last_name: str = Field(description="Last name of the goalie")
    losses: int = Field(description="Number of losses")
    opponent_team_abbrev: str = Field(description="Abbreviation of the opponent team")
    ot_losses: int = Field(description="Number of overtime losses")
    penalty_minutes: int = Field(description="Number of penalty minutes")
    player_id: int = Field(description="Unique identifier for the player")
    points: int = Field(description="Total points (goals + assists)")
    save_pct: Optional[float] = Field(description="Save percentage", default=None)
    saves: int = Field(description="Number of saves")
    shoots_catches: str = Field(description="Which hand the goalie catches with")
    shots_against: int = Field(description="Number of shots against")
    shutouts: int = Field(description="Number of shutouts")
    team_abbrev: str = Field(description="Abbreviation of the goalie's team")
    ties: Optional[None] = Field(description="Number of ties", default=None)
    time_on_ice: int = Field(description="Time on ice in seconds")
    wins: int = Field(description="Number of wins")


class TeamStats(BaseModel):
    """Team Stats model to store team statistics for a season."""
    team_id: int = Field(description="Unique identifier for the team")
    team_full_name: str = Field(description="Full name of the team")
    season: int = Field(description="Season for these statistics")
    games_played: int = Field(description="Number of games played")
    points: int = Field(description="Total points")
    points_percentage: float = Field(description="Percentage of possible points earned")
    wins: int = Field(description="Total wins")
    losses: int = Field(description="Total losses")
    ties: int = Field(description="Total ties")
    wins_regulation: int = Field(description="Wins in regulation time")
    wins_overtime: int = Field(description="Wins in overtime")
    wins_shootout: int = Field(description="Wins in shootout")
    wins_regulation_plus_overtime: int = Field(description="Combined regulation and overtime wins")
    losses_regulation: int = Field(description="Losses in regulation time")
    losses_overtime: int = Field(description="Losses in overtime")
    losses_shootout: int = Field(description="Losses in shootout")
    goals_for: int = Field(description="Total goals scored")
    goals_for_per_game: float = Field(description="Average goals scored per game")
    goals_against: int = Field(description="Total goals allowed")
    goals_against_per_game: float = Field(description="Average goals allowed per game")
    goal_differential: int = Field(description="Goal differential (goals for - goals against)")
    shots_for: int = Field(description="Total shots taken")
    shots_for_per_game: float = Field(description="Average shots taken per game")
    shots_against: int = Field(description="Total shots against")
    shots_against_per_game: float = Field(description="Average shots against per game")
    power_play_percentage: float = Field(description="Power play conversion percentage")
    power_play_net_percentage: float = Field(description="Power play net percentage")
    penalty_kill_percentage: float = Field(description="Penalty kill percentage")
    penalty_kill_net_percentage: float = Field(description="Penalty kill net percentage")
    faceoff_win_percentage: float = Field(description="Percentage of faceoffs won")
