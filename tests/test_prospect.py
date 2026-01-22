import pytest
from edgework.models.prospect import Prospect, Prospects


def test_prospect_initialization():
    prospect = Prospect(
        id=1,
        first_name="Test",
        last_name="Player",
        position_code="C",
        shoots_catches="L",
        height_in_inches=72,
        weight_in_pounds=180,
        height_in_centimeters=183,
        weight_in_kilograms=82,
        birth_date="2000-01-01",
        birth_city="Test City",
        birth_country="USA",
    )
    assert prospect.id == 1
    assert prospect.full_name == "Test Player"
    assert prospect.position_code == "C"


def test_prospect_from_api():
    data = {
        "id": 1,
        "firstName": {"default": "Test"},
        "lastName": {"default": "Player"},
        "positionCode": "C",
        "shootsCatches": "L",
        "heightInInches": 72,
        "weightInPounds": 180,
        "heightInCentimeters": 183,
        "weightInKilograms": 82,
        "birthDate": "2000-01-01",
        "birthCity": {"default": "Test City"},
        "birthCountry": "USA",
    }
    prospect = Prospect.from_api(data)
    assert prospect.id == 1
    assert prospect.full_name == "Test Player"
    assert prospect.birth_city == "Test City"
    assert prospect.birth_country == "USA"


def test_prospects_from_api():
    data = {
        "forwards": [
            {
                "id": 1,
                "firstName": {"default": "Test"},
                "lastName": {"default": "Forward"},
                "positionCode": "L",
                "shootsCatches": "L",
                "heightInInches": 72,
                "weightInPounds": 180,
                "heightInCentimeters": 183,
                "weightInKilograms": 82,
                "birthDate": "2000-01-01",
                "birthCity": {"default": "City"},
                "birthCountry": "USA",
            }
        ],
        "defensemen": [],
        "goalies": [],
    }
    prospects = Prospects.from_api(data)
    assert len(prospects.forwards) == 1
    assert len(prospects.defensemen) == 0
    assert len(prospects.goalies) == 0
    assert prospects.forwards[0].full_name == "Test Forward"
