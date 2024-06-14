from dataclasses import dataclass
from datetime import datetime


@dataclass
class GameEvent:
    """GameEvent dataclass to store game event information."""

    game_id: int
    """Game ID is the unique identifier for the game the event is in."""

    event_id: int
    """Event ID is the unique identifier for the event."""

    event_type: str
    """Event type is the type of event that occurred."""

    event_description: str
    """Event description is the description of the event that occurred."""

    period: int
    """Period is the period the event occurred in."""

    period_time: str
    """Time is the time the event occurred."""

    remaining_time: str
    """Remaining time is the time remaining in the period when the event occurred."""

    x_coordinate: int
    """x coordinate is the x coordinate of the event."""

    y_coordinate: int
    """y coordinate is the y coordinate of the event."""

    home_score: int
    """Home score is the score of the home team when the event occurred."""

    away_score: int
    """Away score is the score of the away team when the event occurred."""

    home_sog: int
    """Home SOG is the number of shots on goal for the home team when the event occurred."""

    away_sog: int
    """Away SOG is the number of shots on goal for the away team when the event occurred."""

    zone: str
    """Zone is the zone the event occurred in."""

    assist1_id: int
    """assist1 ID is the unique identifier for the first player that assisted the event."""

    assist1_total: int
    """assist1 total is the total number of assists the first player has."""

    assist2_id: int
    """assist2 ID is the unique identifier for the second player that assisted the event."""

    assist2_total: int
    """assist2 total is the total number of assists the second player has."""

    scoring_player_id: int
    """scoring player ID is the unique identifier for the player that scored the goal."""

    scoring_player_total: int
    """scoring player total is the total number of goals the player has."""

    secondary_result: str
    """secondary result is the secondary result of the event."""

    type_code: str
    """type code is the type code of the event."""

    blocking_player_id: int
    """Blocking player ID is the unique identifier for the player that blocked a shot."""

    winning_player_id: int
    """Winning player ID is the unique identifier for the player that won the faceoff."""

    losing_player_id: int
    """Losing player ID is the unique identifier for the player that lost the faceoff."""

    hittee_id: int
    """Hittee ID is the unique identifier for the player that was hit."""

    served_by_id: int
    """Served by ID is the unique identifier for the player that served a penalty."""

    event_owner_team_id: int
    """Event owner team ID is the unique identifier for the team that owns the event."""

    shot_type: str  # TODO: Add shot type to the dataclass
    """Shot type is the type of shot that was taken. Can be wrist, snap, slap, backhand, tip, deflection, wraparound, or flip."""

    drawn_by_player_id: int
    """Drawn by player ID is the unique identifier for the player that drew a penalty."""

    reason: str
    """Reason is the reason for the event."""

    player_id: int
    """Player ID is the unique identifier for the player that the event is associated with."""

    goalie_in_net_id: int
    """Goalie in net ID is the unique identifier for the goalie that was in the net when the event occurred."""

    hitting_player_id: int
    """Hitting player ID is the unique identifier for the player that hit another player."""

    shooting_player_id: int
    """Shooting player ID is the unique identifier for the player that took the shot."""


@dataclass
class GameLog:
    """GameLog dataclass to store game log information."""

    game_id: int
    """Game ID is the unique identifier for the game"""

    season: int
    """Season is the season the game was played in"""

    date: datetime
    """Date is the date the game was played"""

    events: list[GameEvent]
    """Events is a list of GameEvent objects that occurred in the game"""
