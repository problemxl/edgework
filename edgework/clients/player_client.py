from datetime import datetime

from edgework.http_client import HttpClient
from edgework.models.player import Player


def api_to_dict(data: dict) -> dict:
    slug = f"{data.get('name').replace(' ', '-').lower()}-{data.get('playerId')}"
    return {
        "player_id": data.get("playerId"),
        "first_name": data.get("name").split(" ")[0],
        "last_name": data.get("name").split(" ")[1],
        "player_slug": slug,
        "sweater_number": data.get("sweaterNumber"),
        "birth_date": data.get("birthDate"),
        "birth_city": data.get("birthCity"),
        "birth_country": data.get("birthCountry"),
        "birth_state_province": data.get("birthStateProvince"),
        "height": data.get("heightInCentimeters"),
        "weight": data.get("weightInKilograms"),
        "position": data.get("positionCode"),
        "is_active": data.get("active"),
        "current_team_id": data.get("teamId") if data.get("teamId") else data.get("lastTeamId"),
        "current_team_abbr": data.get("teamAbbrev") if data.get("teamAbbrev") else data.get("lastTeamAbbrev")
    }


def landing_to_dict(data: dict) -> dict:
    return {
        "player_id": data.get("playerId"),
        "player_slug": data.get("playerSlug"),
        "birth_city": data.get("birthCity", {}).get("default"),
        "birth_country": data.get("birthCountry"),
        "birth_date": datetime.strptime(data.get("birthDate"), "%Y-%m-%d"),
        "birth_state_province": data.get("birthStateProvince", {}).get("default"),
        "current_team_abbr": data.get("currentTeamAbbrev"),
        "current_team_id": data.get("currentTeamId"),
        "current_team_name": data.get("fullTeamName", {}).get("default"),
        "draft_overall_pick": data.get("draftDetails", {}).get("overallPick"),
        "draft_pick": data.get("draftDetails", {}).get("pickInRound"),
        "draft_round": data.get("draftDetails", {}).get("round"),
        "draft_team_abbr": data.get("draftDetails", {}).get("teamAbbrev"),
        "draft_year": datetime(data.get("draftDetails", {}).get("year"), 1, 1),
        "first_name": data.get("firstName", {}).get("default"),
        "last_name": data.get("lastName", {}).get("default"),
        "headshot_url": data.get("headshot"),
        "height": data.get("heightInInches"),
        "hero_image_url": data.get("heroImage"),
        "is_active": data.get("isActive"),
        "position": data.get("position"),
        "shoots_catches": data.get("shootsCatches"),
        "sweater_number": data.get("sweaterNumber"),
        "weight": data.get("weightInPounds")
    }


class PlayerClient:
    def __init__(self, client: HttpClient):
        self._client = client

    def get_player(self, player_id: int) -> dict:
        response = self._client.get(f'player/{player_id}/landing', web=True)
        data = response.json()
        return landing_to_dict(data)

    def get_all_players(self) -> list[Player]:
        response = self._client.get_raw('https://search.d3.nhle.com/api/v1/search/player?culture=en-us&limit=25000&q=*')
        data = response.json()
        return [Player(**api_to_dict(player)) for player in data]

    def get_all_active_players(self) -> list[Player]:
        params = {
            "culture": "en-us",
            "limit": 25000,
            "q": "*",
            "active": True
        }


        response = self._client.get_raw(
            'https://search.d3.nhle.com/api/v1/search/player', params=params)
        data = response.json()
        for player in data:
            print(player)
        print(data)
        return [Player(**api_to_dict(player)) for player in data]

    def get_all_inactive_players(self) -> list[Player]:
        params = {
            "culture": "en-us",
            "limit": 25000,
            "q": "*",
            "active": False
        }
        response = self._client.get_raw(
            'https://search.d3.nhle.com/api/v1/search/player?culture=en-us&limit=25000&q=*&active=false')
        data = response.json()
        
        return [Player(**api_to_dict(player)) for player in data]
