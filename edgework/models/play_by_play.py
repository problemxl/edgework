from typing import TYPE_CHECKING, Dict, List, Optional

from edgework.models.base import BaseNHLModel
from edgework.models.play import Play

if TYPE_CHECKING:
    from edgework.http_client import HttpClient


def play_by_play_api_to_dict(data: dict) -> dict:
    """Convert play-by-play API response data to dictionary format."""
    return {
        "game_id": data.get("id"),
        "season": data.get("season"),
        "game_type": data.get("gameType"),
        "limited_scoring": data.get("limitedScoring"),
        "game_date": data.get("gameDate"),
        "venue": data.get("venue", {}).get("default"),
        "venue_location": data.get("venueLocation", {}).get("default"),
        "start_time_utc": data.get("startTimeUTC"),
        "eastern_utc_offset": data.get("easternUTCOffset"),
        "venue_utc_offset": data.get("venueUTCOffset"),
        "tv_broadcasts": data.get("tvBroadcasts", []),
        "game_state": data.get("gameState"),
        "game_schedule_state": data.get("gameScheduleState"),
        "period_descriptor": data.get("periodDescriptor"),
        "away_team": data.get("awayTeam", {}),
        "home_team": data.get("homeTeam", {}),
        "shootout_in_use": data.get("shootoutInUse"),
        "ot_in_use": data.get("otInUse"),
        "clock": data.get("clock", {}),
        "display_period": data.get("displayPeriod"),
        "max_periods": data.get("maxPeriods"),
        "game_outcome": data.get("gameOutcome"),
        "roster_spots": data.get("rosterSpots"),
        "regular_periods": data.get("regPeriods"),
        "summary": data.get("summary", {}),
        "plays": data.get("plays", []),
    }


class PlayByPlay(BaseNHLModel):
    """PlayByPlay model to store play-by-play game data."""

    def __init__(self, http_client, obj_id=None, **kwargs):
        """
        Initialize a PlayByPlay object with dynamic attributes.

        Args:
            http_client: The HttpClient
            obj_id: The ID of the play-by-play (game_id)
            **kwargs: Dynamic attributes for play-by-play properties
        """
        super().__init__(http_client, obj_id)
        self._data = kwargs.copy()
        self._plays_objects: Optional[List[Play]] = None

        if kwargs:
            self._fetched = True
        else:
            self._fetched = False

    @classmethod
    def from_dict(cls, http_client, data: dict) -> "PlayByPlay":
        """
        Create a PlayByPlay object from a dictionary.

        Args:
            http_client: The HttpClient
            data: Dictionary containing play-by-play data

        Returns:
            PlayByPlay: A PlayByPlay object
        """
        processed_data = data.copy()
        plays_data = processed_data.pop("plays", [])
        play_by_play = cls(
            http_client=http_client, obj_id=data.get("game_id"), **processed_data
        )
        play_by_play._data["plays"] = plays_data
        return play_by_play

    @classmethod
    def from_api(cls, data: dict, http_client) -> "PlayByPlay":
        """
        Create a PlayByPlay object from raw API response data.

        Args:
            data: Raw API response data
            http_client: The HttpClient

        Returns:
            PlayByPlay: A PlayByPlay object
        """
        play_by_play_dict = play_by_play_api_to_dict(data)
        return cls.from_dict(http_client, play_by_play_dict)

    @property
    def plays(self) -> List[Play]:
        """
        Get the plays as Play objects.

        Returns:
            List[Play]: List of Play objects
        """
        if not self._plays_objects and self._data.get("plays"):
            plays_data = self._data["plays"]
            self._plays_objects = [
                Play.from_api(play_data, self._client) for play_data in plays_data
            ]
        return self._plays_objects

    @property
    def goals(self) -> List[Play]:
        """
        Get all goal plays.

        Returns:
            List[Play]: List of goal plays
        """
        return [play for play in self.plays if play.is_goal]

    @property
    def penalties(self) -> List[Play]:
        """
        Get all penalty plays.

        Returns:
            List[Play]: List of penalty plays
        """
        return [play for play in self.plays if play.is_penalty]

    @property
    def shots(self) -> List[Play]:
        """
        Get all shot plays (includes shots on goal, missed shots, blocked shots).

        Returns:
            List[Play]: List of shot plays
        """
        return [play for play in self.plays if play.is_shot]

    @property
    def total_plays(self) -> int:
        """
        Get total number of plays.

        Returns:
            int: Total number of plays
        """
        plays_data = self._data.get("plays", [])
        return len(plays_data)

    def get_plays_by_period(self, period_number: int) -> List[Play]:
        """
        Get all plays from a specific period.

        Args:
            period_number: The period number (1, 2, 3, etc.)

        Returns:
            List[Play]: List of plays from the specified period
        """
        return [
            play
            for play in self.plays
            if play._data.get("period_number") == period_number
        ]

    def get_plays_by_team(self, team_id: int) -> List[Play]:
        """
        Get all plays for a specific team.

        Args:
            team_id: The team ID

        Returns:
            List[Play]: List of plays involving the specified team
        """
        return [
            play
            for play in self.plays
            if play._data.get("details", {}).get("eventOwnerTeamId") == team_id
        ]

    def get_plays_by_player(self, player_id: int) -> List[Play]:
        """
        Get all plays for a specific player.

        Args:
            player_id: The player ID

        Returns:
            List[Play]: List of plays involving the specified player
        """
        result = []
        for play in self.plays:
            details = play._data.get("details", {})
            if (
                details.get("scoringPlayerId") == player_id
                or details.get("assist1PlayerId") == player_id
                or details.get("assist2PlayerId") == player_id
                or details.get("playerId") == player_id
                or details.get("penaltyOnPlayerId") == player_id
                or details.get("drewByPlayerId") == player_id
            ):
                result.append(play)
        return result

    def __str__(self) -> str:
        """
        Return a human-readable string representation of play-by-play.

        Returns:
            str: String representation of play-by-play
        """
        game_id = self._data.get("game_id")
        plays_data = self._data.get("plays", [])
        total_plays = len(plays_data)
        return f"PlayByPlay(game_id={game_id}, {total_plays} plays)"

    def __repr__(self) -> str:
        """
        Return a detailed string representation of play-by-play.

        Returns:
            str: Detailed representation of play-by-play
        """
        return self.__str__()
