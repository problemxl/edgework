from datetime import datetime
from typing import List, Optional

from edgework.http_client import HttpClient
from edgework.models.base import BaseNHLModel
from edgework.models.shift import Shift
from edgework.models.play_by_play import PlayByPlay


class Game(BaseNHLModel):
    """Game model to store game information."""

    def __init__(self, edgework_client, obj_id=None, **kwargs):
        """
        Initialize a Game object with dynamic attributes.

        Args:
            edgework_client: The Edgework client
            obj_id: The ID of the game object
            **kwargs: Dynamic attributes for game properties
        """
        super().__init__(edgework_client, obj_id)
        self._data = kwargs
        self._shifts: Optional[List[Shift]] = None
        self._play_by_play: Optional[PlayByPlay] = None

    @property
    def game_time(self):
        return self._data.get("start_time_utc").strftime("%I:%M %p")

    def __str__(self):
        return f"{self._data.get('away_team_abbrev')} @ {self._data.get('home_team_abbrev')} | {self.game_time} | {self._data.get('away_team_score')} - {self._data.get('home_team_score')}"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        # Compare using game_id only
        return self._data.get("game_id") == getattr(other, "game_id", None)

    def __hash__(self):
        return hash(self._data.get("game_id"))

    def _get(self):
        """Get the game information."""
        raise NotImplementedError("Use from_api or from_dict to create Game instances")

    @property
    def shifts(self) -> List[Shift]:
        if not self._shifts:
            self._shifts = self._get_shifts()
        return self._shifts

    @property
    def play_by_play(self) -> PlayByPlay:
        if not self._play_by_play:
            self._play_by_play = self._get_play_by_play()
        return self._play_by_play

    @classmethod
    def from_dict(cls, data: dict, client: HttpClient):
        game = cls(edgework_client=client, **data)
        return game

    @classmethod
    def from_api(cls, data: dict, client: HttpClient):
        game_dict = {
            "game_id": data.get("id"),
            "start_time_utc": datetime.strptime(
                data.get("startTimeUTC"), "%Y-%m-%dT%H:%M:%SZ"
            ),
            "game_state": data.get("gameState"),
            "away_team_abbrev": data.get("awayTeam").get("abbrev"),
            "away_team_id": data.get("awayTeam").get("id"),
            "away_team_score": data.get("awayTeam").get("score"),
            "home_team_abbrev": data.get("homeTeam").get("abbrev"),
            "home_team_id": data.get("homeTeam").get("id"),
            "home_team_score": data.get("homeTeam").get("score"),
            "season": data.get("season"),
            "venue": data.get("venue").get("default"),
        }
        game = cls.from_dict(game_dict, client)
        game._fetched = True
        return game

    @classmethod
    def get_game(cls, game_id: int, client: HttpClient):
        # Intentional delegation: GameClient owns the gamecenter boxscore
        # route (registry key ``game_boxscore``); this classmethod reuses it
        # so both paths issue identical requests. The model keeps its own
        # (smaller) field mapping via ``from_api``.
        from edgework.clients.game_client import GameClient

        data = GameClient(client).get_game_boxscore(game_id)
        return cls.from_api(data, client)

    def fetch_data(self):
        """Fetch the game data from the API.

        Uses the NHL API gamecenter endpoint to get detailed game information.

        Raises:
            ValueError: If no client is available to fetch game data.
            ValueError: If no game ID is available to fetch data.
        """
        if not self._client:
            raise ValueError("No client available to fetch game data")
        if not self.obj_id:
            raise ValueError("No game ID available to fetch data")

        # Intentional delegation: GameClient owns the gamecenter boxscore
        # route (registry key ``game_boxscore``); lazy refresh reuses it so
        # model and client construct identical requests. Local import avoids
        # the models.game <-> game_client import cycle.
        from edgework.clients.game_client import GameClient

        data = GameClient(self._client).get_game_boxscore(self.obj_id)

        game_dict = {
            "game_id": data.get("id"),
            "start_time_utc": datetime.strptime(
                data.get("startTimeUTC"), "%Y-%m-%dT%H:%M:%SZ"
            ),
            "game_state": data.get("gameState"),
            "away_team_abbrev": data.get("awayTeam").get("abbrev"),
            "away_team_id": data.get("awayTeam").get("id"),
            "away_team_score": data.get("awayTeam").get("score"),
            "home_team_abbrev": data.get("homeTeam").get("abbrev"),
            "home_team_id": data.get("homeTeam").get("id"),
            "home_team_score": data.get("homeTeam").get("score"),
            "season": data.get("season"),
            "venue": data.get("venue").get("default"),
        }

        self._data.update(game_dict)
        self._fetched = True

    def _get_shifts(self):
        """Get the shifts for the game.

        Intentional delegation: ShiftClient is the canonical shiftcharts
        wrapper, so the model and GameClient construct identical requests.
        """
        from edgework.clients.shift_client import ShiftClient

        return ShiftClient(self._client).get_shifts(self.game_id)

    def _get_play_by_play(self):
        """Get the play-by-play data for the game.

        Intentional delegation: GameClient owns the gamecenter play-by-play
        route (registry key ``play_by_play``); the model produces an
        identical request through it. The WSC play-by-play is a distinct
        route (``GameClient.get_wsc_play_by_play``).
        """
        # Local import avoids the models.game <-> game_client import cycle.
        from edgework.clients.game_client import GameClient

        return GameClient(self._client).get_play_by_play(self.game_id)
