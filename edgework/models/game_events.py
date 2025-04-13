from datetime import datetime
from typing import List
from edgework.models.base import BaseNHLModel


class GameEvent(BaseNHLModel):
    """GameEvent model to store game event information."""

    def __init__(self, edgework_client, obj_id=None, game_id=None, event_id=None, 
                 event_type=None, event_description=None, period=None, period_time=None,
                 remaining_time=None, x_coordinate=None, y_coordinate=None, home_score=None,
                 away_score=None, home_sog=None, away_sog=None, zone=None, assist1_id=None,
                 assist1_total=None, assist2_id=None, assist2_total=None, scoring_player_id=None,
                 scoring_player_total=None, secondary_result=None, type_code=None,
                 blocking_player_id=None, winning_player_id=None, losing_player_id=None,
                 hittee_id=None, served_by_id=None, event_owner_team_id=None, shot_type=None,
                 drawn_by_player_id=None, reason=None, player_id=None, goalie_in_net_id=None,
                 hitting_player_id=None, shooting_player_id=None):
        """
        Initialize a GameEvent object.
        
        Args:
            edgework_client: The Edgework client
            obj_id: The ID of the event
            game_id: Game ID is the unique identifier for the game the event is in
            event_id: Event ID is the unique identifier for the event
            event_type: Event type is the type of event that occurred
            event_description: Event description is the description of the event that occurred
            period: Period is the period the event occurred in
            period_time: Time is the time the event occurred
            remaining_time: Remaining time is the time remaining in the period when the event occurred
            x_coordinate: x coordinate is the x coordinate of the event
            y_coordinate: y coordinate is the y coordinate of the event
            home_score: Home score is the score of the home team when the event occurred
            away_score: Away score is the score of the away team when the event occurred
            home_sog: Home SOG is the number of shots on goal for the home team when the event occurred
            away_sog: Away SOG is the number of shots on goal for the away team when the event occurred
            zone: Zone is the zone the event occurred in
            assist1_id: assist1 ID is the unique identifier for the first player that assisted the event
            assist1_total: assist1 total is the total number of assists the first player has
            assist2_id: assist2 ID is the unique identifier for the second player that assisted the event
            assist2_total: assist2 total is the total number of assists the second player has
            scoring_player_id: scoring player ID is the unique identifier for the player that scored the goal
            scoring_player_total: scoring player total is the total number of goals the player has
            secondary_result: secondary result is the secondary result of the event
            type_code: type code is the type code of the event
            blocking_player_id: Blocking player ID is the unique identifier for the player that blocked a shot
            winning_player_id: Winning player ID is the unique identifier for the player that won the faceoff
            losing_player_id: Losing player ID is the unique identifier for the player that lost the faceoff
            hittee_id: Hittee ID is the unique identifier for the player that was hit
            served_by_id: Served by ID is the unique identifier for the player that served a penalty
            event_owner_team_id: Event owner team ID is the unique identifier for the team that owns the event
            shot_type: Shot type is the type of shot that was taken
            drawn_by_player_id: Drawn by player ID is the unique identifier for the player that drew a penalty
            reason: Reason is the reason for the event
            player_id: Player ID is the unique identifier for the player that the event is associated with
            goalie_in_net_id: Goalie in net ID is the unique identifier for the goalie that was in the net
            hitting_player_id: Hitting player ID is the unique identifier for the player that hit another player
            shooting_player_id: Shooting player ID is the unique identifier for the player that took the shot
        """
        super().__init__(edgework_client, obj_id)
        self.game_id = game_id
        self.event_id = event_id
        self.event_type = event_type
        self.event_description = event_description
        self.period = period
        self.period_time = period_time
        self.remaining_time = remaining_time
        self.x_coordinate = x_coordinate
        self.y_coordinate = y_coordinate
        self.home_score = home_score
        self.away_score = away_score
        self.home_sog = home_sog
        self.away_sog = away_sog
        self.zone = zone
        self.assist1_id = assist1_id
        self.assist1_total = assist1_total
        self.assist2_id = assist2_id
        self.assist2_total = assist2_total
        self.scoring_player_id = scoring_player_id
        self.scoring_player_total = scoring_player_total
        self.secondary_result = secondary_result
        self.type_code = type_code
        self.blocking_player_id = blocking_player_id
        self.winning_player_id = winning_player_id
        self.losing_player_id = losing_player_id
        self.hittee_id = hittee_id
        self.served_by_id = served_by_id
        self.event_owner_team_id = event_owner_team_id
        self.shot_type = shot_type
        self.drawn_by_player_id = drawn_by_player_id
        self.reason = reason
        self.player_id = player_id
        self.goalie_in_net_id = goalie_in_net_id
        self.hitting_player_id = hitting_player_id
        self.shooting_player_id = shooting_player_id
        
    def fetch_data(self):
        """
        Fetch the data for the game event.
        """
        # Implementation depends on how data is fetched from the API
        pass
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


class GameLog(BaseNHLModel):
    """GameLog model to store game log information."""

    def __init__(self, edgework_client, obj_id=None, game_id=None, season=None, 
                 date=None, events=None):
        """
        Initialize a GameLog object.
        
        Args:
            edgework_client: The Edgework client
            obj_id: The ID of the game log
            game_id: Game ID is the unique identifier for the game
            season: Season is the season the game was played in
            date: Date is the date the game was played
            events: Events is a list of GameEvent objects that occurred in the game
        """
        super().__init__(edgework_client, obj_id)
        self.game_id = game_id
        self.season = season
        self.date = date
        self.events = events or []
        
    def fetch_data(self):
        """
        Fetch the data for the game log.
        """
        # Implementation depends on how data is fetched from the API
        pass
