from datetime import timedelta

from edgework.models.base import BaseNHLModel


class PeriodTime(BaseNHLModel):
    """PeriodTime model to store period time information."""

    def __init__(self, edgework_client=None, obj_id=None, **kwargs):
        """
        Initialize a PeriodTime object with dynamic attributes.

        Args:
            edgework_client: The Edgework client
            obj_id: The ID of the period time
            **kwargs: Dynamic attributes for period time properties
        """
        super().__init__(edgework_client, obj_id)
        self._data = kwargs
        # Set defaults if not provided
        if "minutes" not in self._data:
            self._data["minutes"] = 0
        if "seconds" not in self._data:
            self._data["seconds"] = 0
        self.validate()

    @classmethod
    def from_string(cls, edgework_client, time_str):
        """
        Create a PeriodTime object from a string in "MM:SS" format.

        Args:
            edgework_client: The Edgework client
            time_str (str): Time string in "MM:SS" format

        Returns:
            PeriodTime: A PeriodTime object
        """
        minutes, seconds = map(int, time_str.split(":"))
        return cls(edgework_client, minutes=minutes, seconds=seconds)

    def validate(self):
        """Validate that minutes and seconds are within valid ranges."""
        if not (0 <= self.minutes < 60):
            raise ValueError(f"Minutes must be between 0 and 59, got {self.minutes}")
        if not (0 <= self.seconds < 60):
            raise ValueError(f"Seconds must be between 0 and 59, got {self.seconds}")

    @property
    def minutes(self) -> int:
        """Return the minutes component of the time."""
        return self._data.get("minutes", 0)

    @property
    def seconds(self) -> int:
        """Return the seconds component of the time."""
        return self._data.get("seconds", 0)

    def to_timedelta(self) -> timedelta:
        """Convert to a timedelta object."""
        return timedelta(minutes=self.minutes, seconds=self.seconds)

    def __str__(self) -> str:
        """Return string representation in "MM:SS" format."""
        return f"{self.minutes:02d}:{self.seconds:02d}"

    def __repr__(self) -> str:
        """Return detailed string representation."""
        return f"PeriodTime({self.minutes:02d}:{self.seconds:02d})"

    def __eq__(self, other) -> bool:
        """Compare two PeriodTime objects."""
        if not isinstance(other, PeriodTime):
            return NotImplemented
        return self.minutes == other.minutes and self.seconds == other.seconds

    def __lt__(self, other) -> bool:
        """Compare if this time is less than another."""
        if not isinstance(other, PeriodTime):
            return NotImplemented
        return self.to_timedelta() < other.to_timedelta()


class Shift(BaseNHLModel):
    """Shift model to store shift information."""

    def __init__(self, edgework_client=None, obj_id=None, **kwargs):
        """
        Initialize a Shift object.

        Args:
            edgework_client: The Edgework client
            obj_id: The ID of the shift
            **kwargs: Shift properties
        """
        super().__init__(edgework_client, obj_id)
        self._data = kwargs

    @classmethod
    def from_api(cls, data: dict):
        """
        Create a Shift object from API response data.

        Args:
            data: Raw API response dictionary

        Returns:
            Shift: A Shift object
        """
        return cls(
            player_id=data.get("playerId"),
            shift_start=data.get("startTime"),
            shift_end=data.get("endTime"),
            duration=data.get("duration"),
            period=data.get("period"),
        )

    @property
    def player_id(self) -> int:
        """Return the player ID."""
        return self._data.get("player_id")

    @property
    def shift_start(self) -> str:
        """Return the shift start time."""
        return self._data.get("shift_start")

    @property
    def shift_end(self) -> str:
        """Return the shift end time."""
        return self._data.get("shift_end")

    @property
    def duration(self) -> str:
        """Return the shift duration."""
        return self._data.get("duration")

    @property
    def period(self) -> int:
        """Return the period number."""
        return self._data.get("period")

    def fetch_data(self):
        """
        Fetch the data for the shift.

        Note: Shift data is typically fetched via the Game endpoint.
        This method raises NotImplementedError.
        """
        raise NotImplementedError(
            "Shift data is fetched via GameClient. Use GameClient.get_shifts() instead."
        )
