from edgework.http_client import HttpClient
from edgework.models.player_stats import SkaterStats
from edgework.models.team_stats import TeamStats
from edgework.models.goalie_stats import GoalieStats
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
        "startedVsRelieved"]

    team_reports: list[str] = [
        'summary',
        'faceoffpercentages',
        'daysbetweengames',
        'faceoffwins',
        'goalsagainstbystrength',
        'goalsbyperiod',
        'goalsforbystrength',
        'leadingtrailing',
        'realtime',
        'outshootoutshotby',
        'penalties',
        'penaltykill',
        'penaltykilltime',
        'powerplay',
        'powerplaytime',
        'summaryshooting',
        'percentages',
        'scoretrailfirst',
        'shootout',
        'shottype',
        'goalgames']

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
            f"en/skater/{report}?isAggregate={aggregate}&isGame={game}&limit={limit}&start={start}&sort={sort}&cayenneExp=seasonId={season}"
        )

        data = response.json()["data"]
        skater_stats_dict = [dict_camel_to_snake(d) for d in data]

        return [SkaterStats(**d) for d in skater_stats_dict]

    def get_goalies_stats(
            self,
            report: str = "summary",
            aggregate: bool,
            game: bool,
            limit: int,
            start: int,
            sort: str,
            season: int,
    ) -> list[SkaterStats]:
        if report not in self.goalie_reports:
            raise ValueError(
                f"Invalid report: {report}, must be one of {', '.join(self.goalie_reports)}"
            )

        url_path = f"en/goalie/{report}?isAggregate={aggregate}&isGame={game}&limit={limit}&start={start}&sort={sort}&cayenneExp=seasonId={season}"
        response = self._client.get(url_path)
        data = response.json()["data"]

        skater_stats_dict = [dict_camel_to_snake(d) for d in data]
        return [SkaterStats(**d) for d in skater_stats_dict]

    def get_team_stats(
            self,
            report: str = "summary",
            aggregate: bool,
            game: bool,
            limit: int,
            start: int,
            sort: str,
            season: int,
    ) -> list[TeamStats]:

        response = self._client.get(f"en/team/stats?cayenneExp=seasonId={season}")
        data = response.json()["data"]
        team_stats_dict = [dict_camel_to_snake(d) for d in data]
        return [TeamStats(**d) for d in team_stats_dict]


    def get_goalie_stats(
            self,
            report: str = "summary",
            aggregate: bool,
            game: bool,
            limit: int,
            start: int,
            sort: str,
            season: int,
    ) -> list[GoalieStats]:
        """
        Get goalie stats for a given season.
        """
        if report not in self.goalie_reports:
            raise ValueError(
                f"Invalid report: {report}, must be one of {', '.join(self.goalie_reports)}"
            )

        response = self._client.get(
            f"en/goalie/{report}?isAggregate={aggregate}&isGame={game}&limit={limit}&start={start}&sort={sort}&cayenneExp=seasonId={season}"
        )

        data = response.json()["data"]
        goalie_stats_dict = [dict_camel_to_snake(d) for d in data]

        return [GoalieStats(**d) for d in goalie_stats_dict]

