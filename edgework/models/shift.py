from datetime import timedelta
from edgework.models.base import BaseNHLModel


class PeriodTime(BaseNHLModel):
    """PeriodTime model to store period time information."""
    
    def __init__(self, edgework_client=None, obj_id=None, minutes=0, seconds=0):
        """
        Initialize a PeriodTime object.
        
        Args:
            edgework_client: The Edgework client
            obj_id: The ID of the period time
            minutes: Minutes in the period time
            seconds: Seconds in the period time
        """
        super().__init__(edgework_client, obj_id)
        self.minutes = minutes
        self.seconds = seconds
        self.validate()
        
    @classmethod
    def from_string(cls, edgework_client, time_str):
        """
        Create a PeriodTime object from a string.
        
        Args:
            edgework_client: The Edgework client
            time_str: The string to parse (format: "MM:SS")
            
        Returns:
            A PeriodTime object
        """
        minutes, seconds = map(int, time_str.split(":"))
        return cls(edgework_client, minutes=minutes, seconds=seconds)
        
    def validate(self):
        """Validate the period time."""
        if self.minutes < 0:
            raise ValueError("Time cannot be negative")
        if self.minutes > 20:
            raise ValueError("Minutes must be less than 20")
        if self.seconds < 0:
            raise ValueError("Time cannot be negative")
        if self.seconds >= 60:
            raise ValueError("Seconds must be less than 60")
        if self.minutes == 20 and self.seconds > 0:
            raise ValueError("Minutes must be less than 20")

    @property
    def total_seconds(self):
        """Get the total seconds."""
        return self.minutes * 60 + self.seconds

    @property
    def timedelta(self):
        """Get the timedelta representation."""
        return timedelta(minutes=self.minutes, seconds=self.seconds)    
    
    def __sub__(self, other):
        """Subtract another PeriodTime or timedelta from this PeriodTime."""
        if isinstance(other, PeriodTime):
            return self.timedelta - other.timedelta
        if isinstance(other, timedelta):
            return self.timedelta - other
            
    def fetch_data(self):
        """
        Fetch the data for the period time.
        """
        # Implementation depends on how data is fetched from the API
        pass


class Shift(BaseNHLModel):
    """
    Shift model to store shift information.

    A shift is a period of time when a player is on the ice.
    """
    def __init__(self, edgework_client, obj_id=None, shift_id=None, game_id=None, player_id=None,
                 first_name=None, last_name=None, period=None, shift_start=None, shift_end=None,
                 shift_number=None, team_id=None, team_abbrev=None):
        """
        Initialize a Shift object.
        
        Args:
            edgework_client: The Edgework client
            obj_id: The ID of the shift object
            shift_id: Unique identifier for the shift
            game_id: Unique identifier for the game the shift is in
            player_id: Unique identifier for the player on the shift
            first_name: The first name of the player on the shift
            last_name: The last name of the player on the shift
            period: Period of the game the shift is in
            shift_start: Time the shift started
            shift_end: Time the shift ended
            shift_number: Order of the shift in the game
            team_id: Team the player is on
            team_abbrev: Abbreviation of the team the player is on
        """
        super().__init__(edgework_client, obj_id)
        self.shift_id = shift_id
        self.game_id = game_id
        self.player_id = player_id
        self.first_name = first_name
        self.last_name = last_name
        self.period = period
        self.shift_start = shift_start
        self.shift_end = shift_end
        self.shift_number = shift_number
        self.team_id = team_id
        self.team_abbrev = team_abbrev

    @property
    def duration(self) -> timedelta:
        """Get the duration of the shift."""
        return timedelta(seconds=self.shift_end.total_seconds - self.shift_start.total_seconds)

    @property
    def shift_length(self):
        """Get the length of the shift."""
        return self.shift_end - self.shift_start

    def __str__(self):
        return f"Shift {self.shift_id} - {self.shift_length}"

    def __repr__(self):
        return str(self)
        
    def fetch_data(self):
        """
        Fetch the data for the shift.
        """
        # Implementation depends on how data is fetched from the API
        pass
        return str(self)

    def __eq__(self, other):
        return self.shift_id == other.shift_id

    @classmethod
    def from_api(cls, data):
        """
        Create a Shift object from API data.
        
        :param data: API data dictionary
        :return: Shift object
        """
        return cls(
            shift_id=data["id"],
            game_id=data["gameId"],
            player_id=data["playerId"],
            first_name=data["firstName"],
            last_name=data["lastName"],
            period=data["period"],
            shift_start=data["startTime"],
            shift_end=data["endTime"],
            shift_number=data["shiftNumber"],
            team_id=data["teamId"],
            team_abbrev=data["teamAbbrev"],
        )
