from pydantic import BaseModel, Field
from datetime import datetime
from typing import List


class GameEvent(BaseModel):
    """GameEvent model to store game event information."""

    game_id: int = Field(description="Game ID is the unique identifier for the game the event is in.")
    event_id: int = Field(description="Event ID is the unique identifier for the event.")
    event_type: str = Field(description="Event type is the type of event that occurred.")
    event_description: str = Field(description="Event description is the description of the event that occurred.")
    period: int = Field(description="Period is the period the event occurred in.")
    period_time: str = Field(description="Time is the time the event occurred.")
    remaining_time: str = Field(description="Remaining time is the time remaining in the period when the event occurred.")
    x_coordinate: int = Field(description="x coordinate is the x coordinate of the event.")
    y_coordinate: int = Field(description="y coordinate is the y coordinate of the event.")
    home_score: int = Field(description="Home score is the score of the home team when the event occurred.")
    away_score: int = Field(description="Away score is the score of the away team when the event occurred.")
    home_sog: int = Field(description="Home SOG is the number of shots on goal for the home team when the event occurred.")
    away_sog: int = Field(description="Away SOG is the number of shots on goal for the away team when the event occurred.")
    zone: str = Field(description="Zone is the zone the event occurred in.")
    assist1_id: int = Field(description="assist1 ID is the unique identifier for the first player that assisted the event.")
    assist1_total: int = Field(description="assist1 total is the total number of assists the first player has.")
    assist2_id: int = Field(description="assist2 ID is the unique identifier for the second player that assisted the event.")
    assist2_total: int = Field(description="assist2 total is the total number of assists the second player has.")
    scoring_player_id: int = Field(description="scoring player ID is the unique identifier for the player that scored the goal.")
    scoring_player_total: int = Field(description="scoring player total is the total number of goals the player has.")
    secondary_result: str = Field(description="secondary result is the secondary result of the event.")
    type_code: str = Field(description="type code is the type code of the event.")
    blocking_player_id: int = Field(description="Blocking player ID is the unique identifier for the player that blocked a shot.")
    winning_player_id: int = Field(description="Winning player ID is the unique identifier for the player that won the faceoff.")
    losing_player_id: int = Field(description="Losing player ID is the unique identifier for the player that lost the faceoff.")
    hittee_id: int = Field(description="Hittee ID is the unique identifier for the player that was hit.")
    served_by_id: int = Field(description="Served by ID is the unique identifier for the player that served a penalty.")
    event_owner_team_id: int = Field(description="Event owner team ID is the unique identifier for the team that owns the event.")
    shot_type: str = Field(description="Shot type is the type of shot that was taken. Can be wrist, snap, slap, backhand, tip, deflection, wraparound, or flip.")
    drawn_by_player_id: int = Field(description="Drawn by player ID is the unique identifier for the player that drew a penalty.")
    reason: str = Field(description="Reason is the reason for the event.")
    player_id: int = Field(description="Player ID is the unique identifier for the player that the event is associated with.")
    goalie_in_net_id: int = Field(description="Goalie in net ID is the unique identifier for the goalie that was in the net when the event occurred.")
    hitting_player_id: int = Field(description="Hitting player ID is the unique identifier for the player that hit another player.")
    shooting_player_id: int = Field(description="Shooting player ID is the unique identifier for the player that took the shot.")


class GameLog(BaseModel):
    """GameLog model to store game log information."""

    game_id: int = Field(description="Game ID is the unique identifier for the game")
    season: int = Field(description="Season is the season the game was played in")
    date: datetime = Field(description="Date is the date the game was played")
    events: List[GameEvent] = Field(description="Events is a list of GameEvent objects that occurred in the game")
