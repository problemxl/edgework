from datetime import datetime
from httpx import Client
from edgework.models.game import Game

class GameClient:
    def __init__(self, client: Client):
        self._client = client

    def get_game(self, game_id: int) -> Game:
        response = self._client.get(f'gamecenter/{game_id}/boxscore')
        data = response.json()

        game_dict = {
            "game_id": data.get("id"),
            "game_date": datetime.strptime(data.get("gameDate"), "%Y-%m-%d"),
            "start_time_utc": datetime.strptime(data.get("startTimeUTC"), "%Y-%m-%dT%H:%M:%SZ"),
            "game_state": data.get("gameState"),
            "away_team_abbrev": data.get("awayTeam").get("abbrev"),
            "away_team_id": data.get("awayTeam").get("id"),
            "away_team_score": data.get("awayTeam").get("score"),
            "home_team_abbrev": data.get("homeTeam").get("abbrev"),
            "home_team_id": data.get("homeTeam").get("id"),
            "home_team_score": data.get("homeTeam").get("score"),
            "season": data.get("season"),
            "venue": data.get("venue").get("default")
        }

        return Game.from_dict(game_dict)