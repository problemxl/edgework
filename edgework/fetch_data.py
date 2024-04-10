import asyncio
import json
import pickle
import os
import sys

import aiohttp
from aiohttp import ClientSession
from nhlpy import NHLClient

from loguru import logger

cache_dir = os.path.join(os.path.dirname(__file__), ".cache")
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)

DATABASE_HOST = os.environ.get("DATABASE_HOST", "localhost")
DATABASE_USER = os.environ.get("DATABASE_USER", "edgework")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD", "edgework")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "edgework")
DATABASE_PORT = os.environ.get("DATABASE_PORT", 5432)


class NHLDataGatherer:
    """
    A class that handles fetching data from the NHL API

    """

    def __init__(self):
        """
        Initializes the class
        """
        logger.info("Initializing NHLDataGatherer")
        self.client = NHLClient()
        self.seasons: list[int] = []

    async def _fetch_url(self, session: ClientSession, url: str) -> dict | list[dict]:
        """
        Fetches a URL and returns the JSON data

        :param session: The aiohttp session to use
        :param url: The URL to fetch
        :return: The JSON data
        """
        logger.trace(f"Fetching URL: {url}")
        async with session.get(url) as response:
            return await response.json()

    async def get_all_players(self, cache: bool = False) -> list[dict]:
        """
        Gets all players from the NHL API

        :param pickle: Whether or not to pickle the data
        :return: A list of all players
        """
        logger.info("Fetching all players | cache={cache}")
        if cache and os.path.exists(os.path.join(cache_dir, "players.pkl")):
            logger.trace("Loading players from cache")
            with open(os.path.join(cache_dir, "players.pkl"), "rb") as f:
                return pickle.load(f)

        active_url: str = "https://search.d3.nhle.com/api/v1/search/player?culture=en-us&limit=30000&q=*&active=true"
        inactive_url: str = "https://search.d3.nhle.com/api/v1/search/player?culture=en-us&limit=30000&q=*&active=false"
        async with ClientSession() as session:
            active_players: list[dict] = await self._fetch_url(session, active_url)
            inactive_players: list[dict] = await self._fetch_url(session, inactive_url)

        players = active_players["results"] + inactive_players["results"]
        if cache:
            # Pickle the data
            with open(os.path.join(cache_dir, "players.pkl"), "wb") as f:
                pickle.dump(players, f)
        return players

    async def get_team_season_schedule(
        self, team_abbrev: str, season: str, cache: bool = False
    ) -> list[dict]:
        """
        Gets the schedule for a team for a given season

        :param team_id: The ID of the team
        :param season: The season to get the schedule for
        :param pickle: Whether or not to pickle the data
        :return: The schedule for the team
        """
        if cache and os.path.exists(
            os.path.join(cache_dir, f"schedules_{season}_{team_abbrev}.pkl")
        ):
            with open(
                os.path.join(cache_dir, f"schedules_{season}_{team_abbrev}.pkl"), "rb"
            ) as f:
                return pickle.load(f)

        schedule = await self.client.get_season_schedule(team_abbrev, season)

        if cache:
            with open(
                os.path.join(cache_dir, f"schedules_{season}_{team_abbrev}.pkl"), "wb"
            ) as f:
                pickle.dump(schedule, f)
        return schedule

    async def get_all_teams_season_schedules(
        self, season: str, cache: bool = False
    ) -> list[dict]:
        """
        Gets the schedule for all teams for a given season

        :param season: The season to get the schedule for
        :param pickle: Whether or not to pickle the data
        :return: The schedule for the team
        """
        if cache and os.path.exists(os.path.join(cache_dir, f"schedules_{season}.pkl")):
            with open(os.path.join(cache_dir, f"schedules_{season}.pkl"), "rb") as f:
                return pickle.load(f)

        schedules = []
        for team in self.client.teams:
            schedules += await self.get_team_season_schedule(
                team.abbreviation, season, cache
            )

        if cache:
            with open(os.path.join(cache_dir, f"schedules_{season}.pkl"), "wb") as f:
                pickle.dump(schedules, f)

        return schedules

    async def get_all_schedules(self, cache: bool = False) -> list[dict]:
        """
        Gets the schedule for all teams for all seasons

        :param pickle: Whether or not to pickle the data
        :return: The schedule for the team
        """
        if cache and os.path.exists(os.path.join(cache_dir, "schedules.pkl")):
            with open(os.path.join(cache_dir, "schedules.pkl"), "rb") as f:
                return pickle.load(f)

        schedules = []
        for season in self.seasons:
            schedules += await self.get_all_teams_season_schedules(season, cache)

        if cache:
            with open(os.path.join(cache_dir, "schedules.pkl"), "wb") as f:
                pickle.dump(schedules, f)

        return schedules

    async def get_game_log(self, game_id: int, cache: bool = False) -> dict:
        """
        Gets the game log for a given game

        :param game_id: The ID of the game
        :param pickle: Whether or not to pickle the data
        :return: The game log
        """
        if cache and os.path.exists(os.path.join(cache_dir, f"game_log_{game_id}.pkl")):
            with open(os.path.join(cache_dir, f"game_log_{game_id}.pkl"), "rb") as f:
                return pickle.load(f)

        game_log = await self.client.game_center.play_by_play(game_id=game_id)

        if cache:
            with open(os.path.join(cache_dir, f"game_log_{game_id}.pkl"), "wb") as f:
                pickle.dump(game_log, f)

        return game_log

    async def get_game_log_season(self, season: int, cache: bool = False) -> list[dict]:
        """
        Gets the game log for all games in a given season

        :param season: The season to get the game logs for
        :param pickle: Whether or not to pickle the data
        :return: The game logs
        """
        if cache and os.path.exists(os.path.join(cache_dir, f"game_logs_{season}.pkl")):
            with open(os.path.join(cache_dir, f"game_logs_{season}.pkl"), "rb") as f:
                return pickle.load(f)

        game_logs = []
        for game in await self.get_all_teams_season_schedules(season):
            game_logs += await self.get_game_log(game["gamePk"], cache)

        if cache:
            with open(os.path.join(cache_dir, f"game_logs_{season}.pkl"), "wb") as f:
                pickle.dump(game_logs, f)

        return game_logs

    async def get_all_game_logs(self, cache: bool = False) -> list[dict]:
        """
        Gets the game log for all games for all seasons

        :param pickle: Whether or not to pickle the data
        :return: The game logs
        """
        if cache and os.path.exists(os.path.join(cache_dir, "game_logs.pkl")):
            with open(os.path.join(cache_dir, "game_logs.pkl"), "rb") as f:
                return pickle.load(f)

        game_logs = []
        for season in self.seasons:
            game_logs += await self.get_game_log_season(season, cache)

        if cache:
            with open(os.path.join(cache_dir, "game_logs.pkl"), "wb") as f:
                pickle.dump(game_logs, f)

        return game_logs

    async def get_team_stats(self, season: int, cache: bool = False) -> list[dict]:
        """
        Gets the team stats for a given season

        :param season: The season to get the stats for
        :return: The team stats
        """
        if cache and os.path.exists(
            os.path.join(cache_dir, f"team_stats_{season}.pkl")
        ):
            with open(os.path.join(cache_dir, f"team_stats_{season}.pkl"), "rb") as f:
                return pickle.load(f)

        team_api_url = f"https://api.nhle.com/stats/rest/en/team/summary?isAggregate=false&isGame=false&start=00&limit=100&factCayenneExp=gamesPlayed%3E=1&cayenneExp=gameTypeId=2%20and%20seasonId%3C={season}%20and%20seasonId%3E={season}"

        async with ClientSession() as session:
            team_stats = await self._fetch_url(session, team_api_url)

        if cache:
            with open(os.path.join(cache_dir, f"team_stats_{season}.pkl"), "wb") as f:
                pickle.dump(team_stats, f)

        return team_stats  # type: ignore

    async def get_player_landings(
        self, player_ids: list[int], cache: bool = False
    ) -> list[dict]:
        """
        Gets the player landings for all players

        :param pickle: Whether or not to pickle the data
        :return: The player landings
        """
        if cache and os.path.exists(os.path.join(cache_dir, "player_landings.pkl")):
            with open(os.path.join(cache_dir, "player_landings.pkl"), "rb") as f:
                return pickle.load(f)

        player_landings = []
        fetch_tasks = []
        async with ClientSession() as session:
            for player_id in player_ids:
                player_landing_url = (
                    f"https://api-web.nhle.com/v1/player/{player_id}/landing"
                )
                fetch_tasks.append(self._fetch_url(session, player_landing_url))

            player_landings = await asyncio.gather(*fetch_tasks)

        if cache:
            with open(os.path.join(cache_dir, "player_landings.pkl"), "wb") as f:
                pickle.dump(player_landings, f)

        return player_landings

    async def get_skater_stats(self, season: int, cache: bool = False) -> list[dict]:
        """
        Gets the skater stats for a given season

        :param season: The season to get the stats for
        :return: The skater stats
        """
        if cache and os.path.exists(
            os.path.join(cache_dir, f"skater_stats_{season}.pkl")
        ):
            with open(os.path.join(cache_dir, f"skater_stats_{season}.pkl"), "rb") as f:
                return pickle.load(f)

        skater_api_url = f"https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=false&isGame=false&start=0&limit=100&factCayenneExp=gamesPlayed%3E=1&cayenneExp=gameTypeId=2%20and%20seasonId%3C={season}%20and%20seasonId%3E={season}"

        async with ClientSession() as session:
            skater_stats: list[dict] = await self._fetch_url(session, skater_api_url)

        if cache:
            with open(os.path.join(cache_dir, f"skater_stats_{season}.pkl"), "wb") as f:
                pickle.dump(skater_stats, f)

        return skater_stats

    async def get_goalie_stats(self, season: int, cache: bool = False) -> list[dict]:
        pass

    async def get_all_player_stats(self, cache: bool = False) -> list[dict]:
        """
        Gets the player stats for all seasons

        :param pickle: Whether or not to pickle the data
        :return: The player stats
        """
        logger.info("Fetching player stats | cache={cache}")

        logger.trace(
            f"Checking cache | cache={cache} | file exists={os.path.exists(os.path.join(cache_dir, 'player_stats.pkl'))}"
        )
        if cache and os.path.exists(os.path.join(cache_dir, "player_stats.pkl")):
            logger.trace("Loading player stats from cache")
            with open(os.path.join(cache_dir, "player_stats.pkl"), "rb") as f:
                return pickle.load(f)

        player_stats = []
        for season in self.seasons:
            player_stats += await self.get_skater_stats(season, cache)

        if cache:
            logger.trace("Caching player stats")
            with open(os.path.join(cache_dir, "player_stats.pkl"), "wb") as f:
                pickle.dump(player_stats, f)

        return player_stats

    async def get_shift_data(
        self, game_ids: list[int], cache: bool = False
    ) -> list[dict]:
        """
        Gets the shift data for all games

        :param pickle: Whether or not to pickle the data
        :return: The shift data
        """
        logger.info("Fetching shift data | cache={cache}")

        logger.trace(
            f"Checking cache | cache={cache} | file exists={os.path.exists(os.path.join(cache_dir, 'shift_data.pkl'))}"
        )
        if cache and os.path.exists(os.path.join(cache_dir, "shift_data.pkl")):
            logger.trace("Loading shift data from cache")
            with open(os.path.join(cache_dir, "shift_data.pkl"), "rb") as f:
                return pickle.load(f)

        shift_data = []
        fetch_tasks = []
        async with ClientSession() as session:
            logger.trace(f"Building fetch tasks | # of game_ids={len(game_ids)}")
            for game_id in game_ids:
                shift_url = f"https://api.nhle.com/stats/rest/en/shiftcharts?cayenneExp=gameId={game_id}"
                fetch_tasks.append(self._fetch_url(session, shift_url))

            logger.trace("Gathering tasks | # of tasks={len(fetch_tasks)}")
            shift_data = await asyncio.gather(*fetch_tasks)

        logger.trace(f"Shift data fetched | # of games={len(shift_data)}")
        if cache:
            logger.trace("Caching shift data")
            with open(os.path.join(cache_dir, "shift_data.pkl"), "wb") as f:
                pickle.dump(shift_data, f)

        logger.success("Shift data fetched")
        return shift_data

    def read_teams(self) -> list[dict]:
        """
        Reads the teams from the NHL API
        """
        logger.info("Reading teams from NHL API")

        if os.path.exists(os.path.join(cache_dir, "teams.json")):
            logger.trace("Loading teams from cache")
            with open(os.path.join(cache_dir, "teams.json"), "rb") as f:
                return pickle.load(f)
        else:
            logger.trace("Teams not cached")
            raise FileNotFoundError("Teams not cached")
