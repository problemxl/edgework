from dataclasses import dataclass
from datetime import datetime


@dataclass
class GameEvent:
    """GameEvent dataclass to store game event information.

    Attributes:
        game_id: Game ID is the unique identifier for the game the event is in.
        event_id: Event ID is the unique identifier for the event.
        event_type: Event type is the type of event that occurred.
        event_description: Event description is the description of the event that occurred.
        period: Period is the period the event occurred in.
        period_time: Time is the time the event occurred.
        remaining_time: Remaining time is the time remaining in the period when the event occurred.
        x_coordinate: x coordinate is the x coordinate of the event.
        y_coordinate: y coordinate is the y coordinate of the event.
        home_score: Home score is the score of the home team when the event occurred.
        away_score: Away score is the score of the away team when the event occurred.
        home_sog: Home SOG is the number of shots on goal for the home team when the event occurred.
        away_sog: Away SOG is the number of shots on goal for the away team when the event occurred.
        zone: Zone is the zone the event occurred in.
        assist1_id: assist1 ID is the unique identifier for the first player that assisted the event.
        assist1_total: assist1 total is the total number of assists the first player has.
        assist2_id: assist2 ID is the unique identifier for the second player that assisted the event.
        assist2_total: assist2 total is the total number of assists the second player has.
        scoring_player_id: scoring player ID is the unique identifier for the player that scored the goal.
        scoring_player_total: scoring player total is the total number of goals the player has.
        secondary_result: secondary result is the secondary result of the event.
        type_code: type code is the type code of the event.
        blocking_player_id: Blocking player ID is the unique identifier for the player that blocked a shot.
        winning_player_id: Winning player ID is the unique identifier for the player that won the faceoff.
        losing_player_id: Losing player ID is the unique identifier for the player that lost the faceoff.
        hittee_id: Hittee ID is the unique identifier for the player that was hit.
        served_by_id: Served by ID is the unique identifier for the player that served a penalty.
        event_owner_team_id: Event owner team ID is the unique identifier for the team that owns the event.
        shot_type: Shot type is the type of shot that was taken. Can be wrist, snap, slap, backhand, tip, deflection, wraparound, or flip.
        drawn_by_player_id: Drawn by player ID is the unique identifier for the player that drew a penalty.
        reason: Reason is the reason for the event.
        player_id: Player ID is the unique identifier for the player that the event is associated with.
        goalie_in_net_id: Goalie in net ID is the unique identifier for the goalie that was in the net when the event occurred.
        hitting_player_id: Hitting player ID is the unique identifier for the player that hit another player.
        shooting_player_id: Shooting player ID is the unique identifier for the player that took the shot.
    """

    game_id: int
    event_id: int
    event_type: str
    event_description: str
    period: int
    period_time: str
    remaining_time: str
    x_coordinate: int
    y_coordinate: int
    home_score: int
    away_score: int
    home_sog: int
    away_sog: int
    zone: str
    assist1_id: int
    assist1_total: int
    assist2_id: int
    assist2_total: int
    scoring_player_id: int
    scoring_player_total: int
    secondary_result: str
    type_code: str
    blocking_player_id: int
    winning_player_id: int
    losing_player_id: int
    hittee_id: int
    served_by_id: int
    event_owner_team_id: int
    shot_type: str  # TODO: Add shot type to the dataclass
    drawn_by_player_id: int
    reason: str
    player_id: int
    goalie_in_net_id: int
    hitting_player_id: int
    shooting_player_id: int


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
