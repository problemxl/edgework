from datetime import timedelta
from pydantic import BaseModel, Field, field_validator, model_validator


class PeriodTime(BaseModel):
    minutes: int = Field(description="Minutes in the period time")
    seconds: int = Field(description="Seconds in the period time")

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, str):
            minutes, seconds = map(int, v.split(":"))
            return cls(minutes=minutes, seconds=seconds)
        return v

    @field_validator('minutes')
    def validate_minutes(cls, v):
        if v < 0:
            raise ValueError("Time cannot be negative")
        if v > 20:
            raise ValueError("Minutes must be less than 20")
        return v

    @field_validator('seconds')
    def validate_seconds(cls, v):
        if v < 0:
            raise ValueError("Time cannot be negative")
        if v >= 60:
            raise ValueError("Seconds must be less than 60")
        return v

    @model_validator(mode='after')
    def validate_time(self):
        if self.minutes == 20 and self.seconds > 0:
            raise ValueError("Minutes must be less than 20")
        return self

    @property
    def total_seconds(self):
        return self.minutes * 60 + self.seconds

    @property
    def timedelta(self):
        return timedelta(minutes=self.minutes, seconds=self.seconds)

    def __sub__(self, other):
        if isinstance(other, PeriodTime):
            return self.timedelta - other.timedelta

        if isinstance(other, timedelta):
            return self.timedelta - other


class Shift(BaseModel):
    """
    Shift model to store shift information.

    A shift is a period of time when a player is on the ice.
    """
    shift_id: int = Field(description="Unique identifier for the shift")
    game_id: int = Field(description="Unique identifier for the game the shift is in")
    player_id: int = Field(description="Unique identifier for the player on the shift")
    first_name: str = Field(description="The first name of the player on the shift")
    last_name: str = Field(description="The last name of the player on the shift")
    period: int = Field(description="Period of the game the shift is in")
    shift_start: PeriodTime = Field(description="Time the shift started")
    shift_end: PeriodTime = Field(description="Time the shift ended")
    shift_number: int = Field(description="Order of the shift in the game")
    team_id: int = Field(description="Team the player is on")
    team_abbrev: str = Field(description="Abbreviation of the team the player is on")
    
    class Config:
        arbitrary_types_allowed = True

    @property
    def duration(self) -> timedelta:
        return timedelta(seconds=self.shift_end.total_seconds - self.shift_start.total_seconds)

    @property
    def shift_length(self):
        return self.shift_end - self.shift_start

    def __str__(self):
        return f"Shift {self.shift_id} - {self.shift_length}"

    def __repr__(self):
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
