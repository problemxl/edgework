from dataclasses import dataclass
from datetime import timedelta


@dataclass
class SkaterStats:
    """
    SkaterStats dataclass to store skater statistics.
    """

    """Game ID is the unique identifier for the game the skater is in."""
    game_id: int

    """Player ID is the unique identifier for the player."""
    player_id: int

    """Player name is the name of the player."""
    player_name: str

    """Team ID is the unique identifier for the team the player is on."""
    team_id: int

    """Position is the position the player plays."""
    position: str

    """Goals is the number of goals the player has scored."""
    goals: int

    """Assists is the number of assists the player has."""
    assists: int

    """Points is the total number of combined goals and assists the player has."""
    points: int

    """Plus/minus is the player's plus/minus rating. A positive number means the player's team has scored more goals
       while the player is on the ice than the opposing team. A negative number means the opposing team has scored more
       goals while the player is on the ice than the player's team."""
    plus_minus: int

    """Penalties is the number of penalties the player has taken."""
    pim: int

    """Hits is the number of hits the player has made."""
    hits: int

    """Blocked shots is the number of shots the player has blocked."""
    blocked_shots: int

    """Power play goals is the number of power play goals the player has scored."""
    power_play_goals: int

    """Power play points is the number of power play points the player has."""
    power_play_points: int

    """Short handed goals is the number of short handed goals the player has scored."""
    short_handed_goals: int

    """Short handed points is the number of short handed points the player has."""
    short_handed_points: int

    """Shots is the number of shots the player has taken."""
    shots: int

    """Faceoff wins is the number of faceoffs the player has won."""
    faceoff_wins: int

    """Faceoff losses is the number of faceoffs the player has lost."""
    faceoff_losses: int

    """Faceoff total is the total number of faceoffs the player has taken."""
    faceoff_total: int

    """Faceoff percentage is the percentage of faceoffs the player has won."""
    faceoff_percentage: float

    """Time on ice is the total amount of time the player has spent on the ice."""
    time_on_ice: timedelta

    """Power play time on ice is the total amount of time the player has spent on the ice during power plays."""
    power_play_toi: timedelta

    """Short handed time on ice is the total amount of time the player has spent on the ice during short handed
       situations."""
    short_handed_toi: timedelta

    


@dataclass
class GoalieStats:
    """
    GoalieStats dataclass to store goalie statistics.
    """
    assists: int
    game_date: datetime
    game_id: int
    games_played: int
    games_started: int
    goalie_full_name: str
    goals: int
    goals_against: int
    goals_against_average: float
    home_road: str
    last_name: str
    losses: int
    opponent_team_abbrev: str
    ot_losses: int
    penalty_minutes: int
    player_id: int
    points: int
    save_pct: Optional[float]
    saves: int
    shoots_catches: str
    shots_against: int
    shutouts: int
    team_abbrev: str
    ties: None
    time_on_ice: int
    wins: int

@dataclass
class TeamStats:
    """Team Stats dataclass to store team statistics for a season."""

    team_id: int

    team_full_name: str

    season: int

    games_played: int

    points: int

    points_percentage: float

    wins: int

    losses: int

    ties: int

    wins_regulation: int

    wins_overtime: int

    wins_shootout: int

    wins_regulation_plus_overtime: int

    losses_regulation: int

    losses_overtime: int

    losses_shootout: int

    goals_for: int

    goals_for_per_game: float

    goals_against: int

    goals_against_per_game: float

    goal_differential: int

    shots_for: int

    shots_for_per_game: float

    shots_against: int

    shots_against_per_game: float

    power_play_percentage: float

    power_play_net_percentage: float

    penalty_kill_percentage: float

    penalty_kill_net_percentage: float

    faceoff_win_percentage: float
