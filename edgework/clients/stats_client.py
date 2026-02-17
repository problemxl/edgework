from typing import Dict, List

from edgework.http_client import HttpClient
from edgework.models.stats import GoalieStats, SkaterStats, TeamStats
from edgework.utilities import dict_camel_to_snake


class StatsClient:
    skate_reports: list[str] = [
        "summary",
        "bios",
        "faceoffpercentages",
        "faceoffwins",
        "goalsForAgainst",
        "realtime",
        "penalties",
        "penaltykill",
        "penaltyShots",
        "powerplay",
        "puckPossessions",
        "summaryshooting",
        "percentages",
        "scoringRates",
        "scoringpergame",
        "shootout",
        "shottype",
        "timeonice",
    ]

    goalie_reports: list[str] = [
        "summary",
        "advanced",
        "bios",
        "daysrest",
        "penaltyShots",
        "savesByStrength",
        "shootout",
        "startedVsRelieved",
    ]

    team_reports: list[str] = [
        "summary",
        "faceoffpercentages",
        "daysbetweengames",
        "faceoffwins",
        "goalsagainstbystrength",
        "goalsbyperiod",
        "goalsforbystrength",
        "leadingtrailing",
        "realtime",
        "outshootoutshotby",
        "penalties",
        "penaltykill",
        "penaltykilltime",
        "powerplay",
        "powerplaytime",
        "summaryshooting",
        "percentages",
        "scoretrailfirst",
        "shootout",
        "shottype",
        "goalgames",
    ]

    def __init__(self, client: HttpClient):
        self._client = client

    def get_skaters_stats(
        self,
        report: str,
        aggregate: bool,
        game: bool,
        limit: int,
        start: int,
        sort: str,
        season: int,
    ) -> list[SkaterStats]:
        if report not in self.skate_reports:
            raise ValueError(f"Invalid report: {report}")

        response = self._client.get(
            f"en/skater/{report}?isAggregate={aggregate}&isGame={game}&limit="
            f"{limit}&start={start}&sort={sort}&cayenneExp=seasonId={season}"
        )

        data = response.json()["data"]
        skater_stats_dict = [dict_camel_to_snake(d) for d in data]

        return [SkaterStats(**d) for d in skater_stats_dict]

    def get_goalies_stats(
        self,
        season: int,
        report: str = "summary",
        aggregate: bool = False,
        game: bool = True,
        limit: int = -1,
        start: int = 0,
        sort: str = "wins",
    ) -> list[GoalieStats]:
        if report not in self.goalie_reports:
            raise ValueError(
                f"Invalid report: {report}, must be one of "
                f"{', '.join(self.goalie_reports)}"
            )

        url_path = (
            f"en/goalie/{report}?isAggregate={aggregate}&isGame={game}&limit="
            f"{limit}&start={start}&sort={sort}&cayenneExp=seasonId={season}"
        )
        response = self._client.get(path=url_path, params=None, web=False)
        data = response.json()["data"]

        skater_stats_dict = [dict_camel_to_snake(d) for d in data]
        return [GoalieStats(**d) for d in skater_stats_dict]

    def get_team_stats(
        self,
        season: int,
        report: str = "summary",
        aggregate: bool = False,
        game: bool = True,
        limit: int = -1,
        start: int = 0,
        sort: str = "wins",
    ) -> list[TeamStats]:
        if report not in self.team_reports:
            raise ValueError(
                f"Invalid report: {report}, must be one of "
                f"{', '.join(self.team_reports)}"
            )

        url_path = (
            f"en/team/{report}?isAggregate={aggregate}&isGame={game}&limit="
            f"{limit}&start={start}&sort={sort}&cayenneExp=seasonId={season}"
        )
        response = self._client.get(path=url_path, params=None, web=False)
        data = response.json()["data"]

        team_stats_dict = [dict_camel_to_snake(d) for d in data]
        return [TeamStats(**d) for d in team_stats_dict]

    def get_skater_stats_leaders(self, game_type: int = 2) -> Dict:
        """Fetch current skater statistics leaders.

        Args:
            game_type: Game type ID (2=Regular Season, 3=Playoffs)

        Returns:
            Dictionary with current skater leaders including:
            - Points leaders
            - Goals leaders
            - Assists leaders
        """
        response = self._client.get(f"skater-stats-leaders/current", web=True)
        return response.json()

    def get_goalie_stats_leaders(self, game_type: int = 2) -> Dict:
        """Fetch current goalie statistics leaders.

        Args:
            game_type: Game type ID (2=Regular Season, 3=Playoffs)

        Returns:
            Dictionary with current goalie leaders including:
            - Wins leaders
            - GAA leaders
            - Save percentage leaders
        """
        response = self._client.get(f"goalie-stats-leaders/current", web=True)
        return response.json()

    def get_skater_stats_leaders_by_season(
        self, season: str, game_type: int = 2
    ) -> Dict:
        """Fetch skater statistics leaders for a specific season.

        Args:
            season: Season in format "YYYY-YYYY" (e.g., "2023-2024")
            game_type: Game type ID (2=Regular Season, 3=Playoffs)

        Returns:
            Dictionary with skater leaders for the specified season.
        """
        try:
            start_year, end_year = season.split("-")
            season_id = f"{start_year}{end_year}"
        except (ValueError, AttributeError):
            raise ValueError(
                f"Invalid season format: '{season}'. Expected format: 'YYYY-YYYY'"
            )

        response = self._client.get(
            f"skater-stats-leaders/{season_id}/{game_type}", web=True
        )
        return response.json()

    def get_goalie_stats_leaders_by_season(
        self, season: str, game_type: int = 2
    ) -> Dict:
        """Fetch goalie statistics leaders for a specific season.

        Args:
            season: Season in format "YYYY-YYYY" (e.g., "2023-2024")
            game_type: Game type ID (2=Regular Season, 3=Playoffs)

        Returns:
            Dictionary with goalie leaders for the specified season.
        """
        try:
            start_year, end_year = season.split("-")
            season_id = f"{start_year}{end_year}"
        except (ValueError, AttributeError):
            raise ValueError(
                f"Invalid season format: '{season}'. Expected format: 'YYYY-YYYY'"
            )

        response = self._client.get(
            f"goalie-stats-leaders/{season_id}/{game_type}", web=True
        )
        return response.json()
