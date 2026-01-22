from dataclasses import dataclass
from datetime import datetime
from typing import Optional


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
    x_coordinate: Optional[int] = None
    y_coordinate: Optional[int] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    home_sog: Optional[int] = None
    away_sog: Optional[int] = None
    zone: Optional[str] = None
    assist1_id: Optional[int] = None
    assist1_total: Optional[int] = None
    assist2_id: Optional[int] = None
    assist2_total: Optional[int] = None
    scoring_player_id: Optional[int] = None
    scoring_player_total: Optional[int] = None
    secondary_result: Optional[str] = None
    type_code: Optional[str] = None
    blocking_player_id: Optional[int] = None
    winning_player_id: Optional[int] = None
    losing_player_id: Optional[int] = None
    hittee_id: Optional[int] = None
    served_by_id: Optional[int] = None
    event_owner_team_id: Optional[int] = None
    shot_type: Optional[str] = None
    drawn_by_player_id: Optional[int] = None
    reason: Optional[str] = None
    player_id: Optional[int] = None
    goalie_in_net_id: Optional[int] = None
    hitting_player_id: Optional[int] = None
    shooting_player_id: Optional[int] = None

    @classmethod
    def from_api(cls, data: dict, game_id: int) -> "GameEvent":
        details = data.get("details", {})
        period_desc = data.get("periodDescriptor", {})

        return cls(
            game_id=game_id,
            event_id=data.get("eventId", 0),
            event_type=data.get("typeDescKey", ""),
            event_description=data.get("typeDescKey", ""),
            period=period_desc.get("number", 0),
            period_time=data.get("timeInPeriod", ""),
            remaining_time=data.get("timeRemaining", ""),
            x_coordinate=details.get("xCoord"),
            y_coordinate=details.get("yCoord"),
            home_score=details.get("homeScore"),
            away_score=details.get("awayScore"),
            home_sog=details.get("homeSOG"),
            away_sog=details.get("awaySOG"),
            zone=details.get("zoneCode"),
            assist1_id=details.get("assist1PlayerId"),
            assist1_total=details.get("assist1PlayerTotal"),
            assist2_id=details.get("assist2PlayerId"),
            assist2_total=details.get("assist2PlayerTotal"),
            scoring_player_id=details.get("scoringPlayerId"),
            scoring_player_total=details.get("scoringPlayerTotal"),
            secondary_result=details.get("secondaryResult"),
            type_code=str(data.get("typeCode", "")),
            blocking_player_id=details.get("blockingPlayerId"),
            winning_player_id=details.get("winningPlayerId"),
            losing_player_id=details.get("losingPlayerId"),
            hittee_id=details.get("hitteePlayerId"),
            served_by_id=details.get("servedByPlayerId"),
            event_owner_team_id=details.get("eventOwnerTeamId"),
            shot_type=details.get("shotType"),
            drawn_by_player_id=details.get("drawnByPlayerId"),
            reason=details.get("reason"),
            player_id=details.get("playerId"),
            goalie_in_net_id=details.get("goalieInNetId"),
            hitting_player_id=details.get("hittingPlayerId"),
            shooting_player_id=details.get("shootingPlayerId"),
        )


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
