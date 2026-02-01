from datetime import datetime
from typing import TYPE_CHECKING, Dict, List, Optional

from edgework.models.base import BaseNHLModel


class Play(BaseNHLModel):
    """Play model to store individual play event information."""

    def __init__(self, edgework_client, obj_id=None, **kwargs):
        """
        Initialize a Play object with dynamic attributes.

        Args:
            edgework_client: The Edgework client
            obj_id: The ID of the play object
            **kwargs: Dynamic attributes for play properties
        """
        super().__init__(edgework_client, obj_id)
        self._data = kwargs

    @classmethod
    def from_dict(cls, data: dict, client) -> "Play":
        """
        Create a Play object from a dictionary.

        Args:
            data: Dictionary containing play data
            client: The HttpClient

        Returns:
            Play: A Play object
        """
        return cls(edgework_client=client, **data)

    @classmethod
    def from_api(cls, data: dict, client) -> "Play":
        """
        Create a Play object from raw API response data.

        Args:
            data: Raw API response data
            client: The HttpClient

        Returns:
            Play: A Play object
        """
        play_dict = {
            "event_id": data.get("eventId"),
            "period_number": data.get("periodDescriptor", {}).get("number"),
            "period_type": data.get("periodDescriptor", {}).get("periodType"),
            "time_in_period": data.get("timeInPeriod"),
            "time_remaining": data.get("timeRemaining"),
            "situation_code": data.get("situationCode"),
            "home_team_defending_side": data.get("homeTeamDefendingSide"),
            "type_code": data.get("typeCode"),
            "type_desc_key": data.get("typeDescKey"),
            "sort_order": data.get("sortOrder"),
            "details": data.get("details", {}),
            "ppt_replay_url": data.get("pptReplayUrl"),
        }
        play = cls.from_dict(play_dict, client)
        play._fetched = True
        return play

    @property
    def is_goal(self) -> bool:
        """Check if this play is a goal."""
        return self._data.get("type_desc_key") == "goal"

    @property
    def is_penalty(self) -> bool:
        """Check if this play is a penalty."""
        return self._data.get("type_desc_key") == "penalty"

    @property
    def is_shot(self) -> bool:
        """Check if this play is a shot."""
        return self._data.get("type_desc_key") in [
            "shot-on-goal",
            "missed-shot",
            "blocked-shot",
        ]

    @property
    def goal_details(self) -> Optional[Dict]:
        """Get goal-specific details if this is a goal."""
        if self.is_goal and self._data.get("details"):
            return self._data["details"]
        return None

    @property
    def scoring_player_id(self) -> Optional[int]:
        """Get the scoring player ID for a goal."""
        details = self.goal_details
        if details:
            return details.get("scoringPlayerId")
        return None

    @property
    def assist_player_ids(self) -> List[int]:
        """Get assist player IDs for a goal."""
        details = self.goal_details
        assists = []
        if details:
            if details.get("assist1PlayerId"):
                assists.append(details["assist1PlayerId"])
            if details.get("assist2PlayerId"):
                assists.append(details["assist2PlayerId"])
        return assists

    def __str__(self) -> str:
        """Return a human-readable string representation of the play."""
        event_id = self._data.get("event_id")
        period = self._data.get("period_number")
        time = self._data.get("time_in_period")
        play_type = self._data.get("type_desc_key")

        return f"Period {period} @ {time}: {play_type} (ID: {event_id})"

    def __repr__(self) -> str:
        """Return a detailed string representation of the play."""
        return f"Play(event_id={self._data.get('event_id')}, type={self._data.get('type_desc_key')})"
