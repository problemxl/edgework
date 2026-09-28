"""Game client for fetching NHL game data."""

import warnings
from datetime import datetime
from typing import Dict, List, Optional, Union

from edgework.clients.shift_client import ShiftClient
from edgework.http_client import HttpClient
from edgework.models.game import Game
from edgework.models.game_events import GameEvent
from edgework.models.play_by_play import PlayByPlay
from edgework.models.shift import Shift


class GameClient:
    """Client for fetching NHL game data."""

    def __init__(self, client: HttpClient):
        self._client = client
        # Canonical shiftcharts access is owned by ShiftClient; game-level
        # shift methods delegate to it so routes stay in one place.
        self._shift_client = ShiftClient(client)

    def get_game(self, game_id: int) -> Game:
        """Fetch game boxscore data.

        Args:
            game_id: The NHL game ID.

        Returns:
            Game object with boxscore data.
        """
        response = self._client.get(f"gamecenter/{game_id}/boxscore", web=True)
        data = response.json()

        game_dict = {
            "game_id": data.get("id"),
            "game_date": datetime.strptime(data.get("gameDate"), "%Y-%m-%d"),
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

        return Game.from_dict(game_dict, self._client)

    def get_play_by_play(self, game_id: int) -> PlayByPlay:
        """Fetch play-by-play data for a game.

        Args:
            game_id: The NHL game ID.

        Returns:
            PlayByPlay object with full play-by-play data.
        """
        response = self._client.get(f"gamecenter/{game_id}/play-by-play", web=True)
        data = response.json()
        return PlayByPlay.from_api(data, self._client)

    def get_game_landing(self, game_id: int) -> Dict:
        """Fetch game landing page data.

        Args:
            game_id: The NHL game ID.

        Returns:
            Dictionary with comprehensive game landing data.
        """
        response = self._client.get(f"gamecenter/{game_id}/landing", web=True)
        return response.json()

    def get_game_boxscore(self, game_id: int) -> Dict:
        """Fetch game boxscore data as raw dictionary.

        Args:
            game_id: The NHL game ID.

        Returns:
            Dictionary with boxscore data.
        """
        response = self._client.get(f"gamecenter/{game_id}/boxscore", web=True)
        return response.json()

    def get_game_story(self, game_id: int) -> Dict:
        """Fetch game story/narrative data.

        Args:
            game_id: The NHL game ID.

        Returns:
            Dictionary with game story data.
        """
        response = self._client.get(f"wsc/game-story/{game_id}", web=True)
        return response.json()

    def get_game_right_rail(self, game_id: int) -> Dict:
        """Fetch game right rail data.

        Args:
            game_id: The NHL game ID.

        Returns:
            Dictionary with right rail game information.
        """
        response = self._client.get(f"gamecenter/{game_id}/right-rail", web=True)
        return response.json()

    def get_score(self, date: Optional[Union[datetime, str]] = None) -> Dict:
        """Fetch score data for a specific date or current scores.

        Args:
            date: Date for scores. If None, fetches current scores.
                  Can be datetime object or string in YYYY-MM-DD format.

        Returns:
            Dictionary with score data for the specified date.
        """
        if date is None:
            response = self._client.get("score/now", web=True)
        else:
            if isinstance(date, datetime):
                date_str = date.strftime("%Y-%m-%d")
            else:
                date_str = date
            response = self._client.get(f"score/{date_str}", web=True)
        return response.json()

    def get_scoreboard(self) -> Dict:
        """Fetch current scoreboard data.

        Returns:
            Dictionary with current scoreboard information.
        """
        response = self._client.get("scoreboard/now", web=True)
        return response.json()

    def get_goal_replay(self, game_id: int, event_number: int) -> Dict:
        """Fetch goal replay information for a specific game event.

        Targets the documented ``/ppt-replay/goal/{game-id}/{event-number}``
        route.

        Args:
            game_id: The NHL game ID.
            event_number: The event number within the game.

        Returns:
            Dictionary with goal replay information.
        """
        response = self._client.get(
            f"ppt-replay/goal/{game_id}/{event_number}", web=True
        )
        return response.json()

    def get_play_replay(self, game_id: int, event_number: int) -> Dict:
        """Fetch replay information for a specific game event.

        Targets the documented ``/ppt-replay/{game-id}/{event-number}`` route.

        Delegation note: following ``goal.pptReplayUrl`` from this metadata
        to the actual tracking frames lives in
        :meth:`edgework.clients.edge_client.EdgeClient.get_goal_frames`
        (the sprites host needs a Referer header); this method stays the
        metadata-only owner of the route.

        Args:
            game_id: The NHL game ID.
            event_number: The event number within the game.

        Returns:
            Dictionary with play replay information.
        """
        response = self._client.get(f"ppt-replay/{game_id}/{event_number}", web=True)
        return response.json()

    def get_wsc_play_by_play(self, game_id: int) -> Dict:
        """Fetch WSC play-by-play data for a game.

        Targets the documented ``/wsc/play-by-play/{game-id}`` route, which is
        distinct from the gamecenter play-by-play route used by
        :meth:`get_play_by_play`.

        Args:
            game_id: The NHL game ID.

        Returns:
            Dictionary with WSC play-by-play data.
        """
        response = self._client.get(f"wsc/play-by-play/{game_id}", web=True)
        return response.json()

    def get_partner_game_odds(self, country_code: str = "US") -> Dict:
        """Fetch odds for games in a specific country as of the current moment.

        Targets the documented ``/partner-game/{country-code}/now`` route.

        Note:
            This is the documented *odds* endpoint and is NOT the
            ``/where-to-watch`` streaming endpoint (see
            ``NetworkClient.get_where_to_watch`` for that route).

        Args:
            country_code: Country code for odds info (default: "US").

        Returns:
            Dictionary with partner game odds information.
        """
        response = self._client.get(f"partner-game/{country_code}/now", web=True)
        return response.json()

    def get_where_to_watch(self, country_code: str = "US") -> Dict:
        """Deprecated alias for :meth:`get_partner_game_odds`.

        This method has always fetched partner-game odds from
        ``/partner-game/{country-code}/now``; it does NOT request the real
        ``/where-to-watch`` streaming endpoint. Use
        :meth:`get_partner_game_odds` (or ``NetworkClient.get_where_to_watch``
        for the actual streaming route) instead.

        Args:
            country_code: Country code for odds info (default: "US").

        Returns:
            Dictionary with partner game odds information.
        """
        warnings.warn(
            "GameClient.get_where_to_watch() fetches partner-game odds, not "
            "the /where-to-watch streaming endpoint; use "
            "get_partner_game_odds() (or NetworkClient.get_where_to_watch() "
            "for the real streaming route).",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.get_partner_game_odds(country_code)

    def get_shifts(self, game_id: int) -> List[Shift]:
        """Fetch shift data for a game.

        Delegates to the canonical :class:`ShiftClient` wrapper for the
        documented ``/{lang}/shiftcharts`` route.

        Args:
            game_id: The NHL game ID.

        Returns:
            List of Shift objects.
        """
        # Intentional delegation: ShiftClient owns the shiftcharts route and
        # query construction.
        return self._shift_client.get_shifts(game_id)

    def get_games_for_date(self, date: Union[datetime, str]) -> List[Game]:
        """Fetch all games for a specific date.

        Args:
            date: Date to fetch games for. Can be datetime or YYYY-MM-DD string.

        Returns:
            List of Game objects for that date.
        """
        if isinstance(date, datetime):
            date_str = date.strftime("%Y-%m-%d")
        else:
            date_str = date

        response = self._client.get(f"schedule/{date_str}", web=True)
        data = response.json()

        games = []
        for game_data in data.get("gameWeek", []):
            for game in game_data.get("games", []):
                game_id = game.get("id")
                if game_id:
                    games.append(self.get_game(game_id))

        return games

    def get_current_games(self) -> List[Game]:
        """Fetch all current/upcoming games.

        Returns:
            List of Game objects for current games.
        """
        response = self._client.get("schedule/now", web=True)
        data = response.json()

        games = []
        for game_data in data.get("gameWeek", []):
            for game in game_data.get("games", []):
                game_id = game.get("id")
                if game_id:
                    games.append(self.get_game(game_id))

        return games
