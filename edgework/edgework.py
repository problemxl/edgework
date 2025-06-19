from edgework.http_client import SyncHttpClient

# Import the SkaterStats model
from edgework.models.stats import SkaterStats, GoalieStats, TeamStats


class Edgework:
    def __init__(self, user_agent: str = "EdgeworkClient/1.0"):
        """
        Initializes the Edgework API client.

        Args:
            user_agent (str, optional): The User-Agent string to use for requests.
                                        Defaults to "EdgeworkClient/1.0".
        """
        self._client = SyncHttpClient(user_agent=user_agent)

        # Initialize model handlers, passing the shared HTTP client
        self.skaters = SkaterStats(edgework_client=self._client)
        self.goalies = GoalieStats(edgework_client=self._client)
        self.teams = TeamStats(edgework_client=self._client)

    def skater_stats(
        self,
        season: str,
        report: str = "summary",
        sort: str | list[str] = "points",
        direction: str | list[str] = "DESC",
        aggregate: bool = False,
        limit: int = 10,
        game_type: int = 2,
    ):
        """
        Fetch skater stats for a given season.
        Args:
            season (str): The season to fetch stats for (e.g., "2024-2025").
            report (str): The type of report to fetch (e.g., "summary", "detailed").
            sort (str): The field to sort the results by (e.g., "points", "goals").
            limit (int): The maximum number of results to return.

        Returns:
            SkaterStats: An instance of the SkaterStats model, populated with the fetched data.
                         The actual player statistics can be accessed via `instance.players`.
        """
        # Convert season string "YYYY-YYYY" to integer YYYYYYYY
        try:
            converted_season = int(season.replace("-", ""))
        except ValueError:
            raise ValueError(
                "Invalid season format. Expected 'YYYY-YYYY', e.g., '2023-2024'."
            )

        self.skaters.fetch_data(
            report=report, season=converted_season, sort=sort, direction=direction, limit=limit, aggregate=aggregate, game_type=game_type
        )
        return self.skaters

    def goalie_stats(
        self,
        season: str,
        report: str = "summary",
        sort: str | list[str] = "wins",
        direction: str | list[str] = "DESC",
        is_aggregate: bool = False,
        limit: int = 10,
    ):
        """
        Fetch goalie stats for a given season.
        Args:
            season (str): The season to fetch stats for (e.g., "2024-2025").
            report (str): The type of report to fetch (e.g., "summary", "detailed").
            sort (str): The field to sort the results by (e.g., "wins", "goalsAgainst").
            is_aggregate (bool): Whether to aggregate the stats. Defaults to False.
            limit (int): The maximum number of results to return.

        Returns:
            GoalieStats: An instance of the GoalieStats model, populated with the fetched data.
                         The actual goalie statistics can be accessed via `instance.players`.
        """
        # Convert season string "YYYY-YYYY" to integer YYYYYYYY
        try:
            converted_season = int(season.replace("-", ""))
        except ValueError:
            raise ValueError(
                "Invalid season format. Expected 'YYYY-YYYY', e.g., '2023-2024'."
            )

        self.goalies.fetch_data(
            report=report, season=converted_season, sort=sort, limit=limit
        )
        return self.goalies

    def team_stats(
        self,
        season: str,
        report: str = "summary",
        sort: str | list[str] = "points",
        direction: str | list[str] = "DESC",
        limit: int = 10,
        aggregate: bool = False,
        game: bool = True,
    ):
        """
        Fetch team stats for a given season.
        Args:
            season (str): The season to fetch stats for (e.g., "2024-2025").
            report (str): The type of report to fetch (e.g., "summary", "detailed").
            sort (dict): The field to sort the results by (e.g., "points", "wins").
            limit (int): The maximum number of results to return. Defaults to 10.
            aggregate (bool): Whether to aggregate the stats. Defaults to False.

        Returns:
            TeamStats: An instance of the TeamStats model, populated with the fetched data.
                         The actual team statistics can be accessed via `instance.teams`.
        """
        # Convert season string "YYYY-YYYY" to integer YYYYYYYY
        try:
            converted_season = int(season.replace("-", ""))
        except ValueError:
            raise ValueError(
                "Invalid season format. Expected 'YYYY-YYYY', e.g., '2023-2024'."
            )

        # try:
        #     assert isinstance(sort, list)
        #     for s in sort:
        #         assert isinstance(s, dict)
        #         assert "property" in s and "direction" in s
        # except AssertionError:
        #     raise ValueError(
        #         "Sort must be a dictionary with 'property' and 'direction' keys."
        #     )

        self.teams.fetch_data(
            report=report,
            season=converted_season,
            sort=sort,
            direction=direction,
            limit=limit,
            aggregate=aggregate,
            game=game,
        )
        return self.teams

    def close(self):
        """Closes the underlying HTTP client session."""
        if hasattr(self._client, "close"):
            self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
