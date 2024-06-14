from dataclasses import dataclass
from datetime import timedelta


class PeriodTime:
    minutes: int
    seconds: int

    def __init__(self, time_str):
        self.minutes, self.seconds = map(int, time_str.split(":"))
        if self.minutes < 0 or self.seconds < 0:
            raise ValueError("Time cannot be negative")
        if self.seconds >= 60:
            raise ValueError("Seconds must be less than 60")
        if self.minutes >= 20:
            raise ValueError("Minutes must be less than 20")

    @property
    def total_seconds(self):
        return self.minutes * 60 + self.seconds


@dataclass
class Shift:
    """
    Shift dataclass to store shift information.

    A shift is a period of time where a player is on the ice.
    """

    """Shift ID is a unique identifier for the shift."""
    shift_id: int

    """Game ID is the unique identifier for the game the shift is in."""
    game_id: int

    """Player ID is the unique identifier for the player on the shift."""
    player_id: int

    """Player name is the name of the player on the shift."""
    player_name: str

    """Period is the period of the game the shift is in."""
    period: int

    """Shift start is the time the shift started."""
    shift_start: PeriodTime

    """Shift end is the time the shift ended."""
    shift_end: PeriodTime

    """Duration is the length of the shift."""
    duration: timedelta

    """Shift number is the order of the shift in the game."""
    shift_number: int

    def __init__(
        self,
        shift_id: int,
        game_id: int,
        player_id: int,
        player_name: str,
        period: int,
        shift_start: str,
        shift_end: str,
        shift_number: int,
    ):
        self.shift_id = shift_id
        self.game_id = game_id
        self.player_id = player_id
        self.player_name = player_name
        self.period = period
        self.shift_start = PeriodTime(shift_start)
        self.shift_end = PeriodTime(shift_end)
        self.duration = timedelta(seconds=self.shift_end.total_seconds - self.shift_start.total_seconds)
        self.shift_number = shift_number

    @property
    def shift_length(self):
        return self.shift_end - self.shift_start

    def __str__(self):
        return f"Shift {self.shift_id} - {self.shift_length}"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.shift_id == other.shift_id
