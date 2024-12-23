from dataclasses import dataclass


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
