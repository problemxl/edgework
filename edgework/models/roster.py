from dataclasses import dataclass
from typing import Optional


@dataclass
class RosterPlayer:
    id: int
    first_name: str
    last_name: str
    position_code: str
    shoots_catches: str
    height_in_inches: int
    weight_in_pounds: int
    height_in_centimeters: int
    weight_in_kilograms: int
    birth_date: str
    birth_city: str
    birth_country: str
    birth_state_province: Optional[str] = None
    sweater_number: Optional[int] = None
    headshot: Optional[str] = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return (
            f"#{self.sweater_number} {self.full_name}"
            if self.sweater_number
            else self.full_name
        )

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, RosterPlayer):
            return self.id == other.id
        return False

    @classmethod
    def from_api(cls, data: dict) -> "RosterPlayer":
        first_name = data.get("firstName", {})
        last_name = data.get("lastName", {})
        birth_city = data.get("birthCity", {})
        birth_state_province = data.get("birthStateProvince", {})

        return cls(
            id=data.get("id"),
            first_name=first_name.get("default", ""),
            last_name=last_name.get("default", ""),
            position_code=data.get("positionCode", ""),
            shoots_catches=data.get("shootsCatches", ""),
            height_in_inches=data.get("heightInInches", 0),
            weight_in_pounds=data.get("weightInPounds", 0),
            height_in_centimeters=data.get("heightInCentimeters", 0),
            weight_in_kilograms=data.get("weightInKilograms", 0),
            birth_date=data.get("birthDate", ""),
            birth_city=birth_city.get("default", ""),
            birth_country=data.get("birthCountry", ""),
            birth_state_province=birth_state_province.get("default"),
            sweater_number=data.get("sweaterNumber"),
            headshot=data.get("headshot"),
        )


@dataclass
class Roster:
    forwards: list[RosterPlayer]
    defensemen: list[RosterPlayer]
    goalies: list[RosterPlayer]

    @classmethod
    def from_api(cls, data: dict) -> "Roster":
        forwards = [RosterPlayer.from_api(p) for p in data.get("forwards", [])]
        defensemen = [RosterPlayer.from_api(p) for p in data.get("defensemen", [])]
        goalies = [RosterPlayer.from_api(p) for p in data.get("goalies", [])]

        return cls(
            forwards=forwards,
            defensemen=defensemen,
            goalies=goalies,
        )
