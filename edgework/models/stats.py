from datetime import datetime, timedelta
import json
from edgework.models.base import BaseNHLModel
from edgework.utilities import dict_camel_to_snake

# Development imports
from icecream import ic


class StatEntity(BaseNHLModel):
    """
    PlayerStats model to store player statistics.
    """

    def __init__(
        self, edgework_client, id: int | None = None, data: dict | None = None
    ):
        super().__init__(edgework_client, id)
        self._data = data
        self._fetched = True


class SkaterStats(BaseNHLModel):
    """
    SkaterStats model to store skater statistics.
    """

    def __init__(self, edgework_client, obj_id=None, **kwargs):
        """
        Initialize a SkaterStats object with dynamic attributes.
        """
        super().__init__(edgework_client, obj_id)
        players: list[StatEntity] = []
        self._data = kwargs

    def fetch_data(
        self,
        report: str = "summary",
        season: int = None,
        aggregate: bool = False,
        game: bool = True,
        limit: int = -1,
        start: int = 0,
        sort: str | list[str] = "points",
        direction: str | list[str] = "DESC",
        game_type: int = None,
    ) -> None:
        """
        Fetch the data for the skater stats.

        Args:
            report: The type of report to get (e.g. "summary", "bios", etc.)
            season: The season to get stats for (e.g. 20232024)
            aggregate: Whether to aggregate the stats
            game: Whether to get game stats
            limit: Number of results to return (-1 for all)
            start: Starting index for results
            sort: Field to sort by
        """
        if not season:
            if datetime.now().month >= 7:
                season = datetime.now().year * 10000 + (datetime.now().year + 1)
            else:
                season = (datetime.now().year - 1) * 10000 + datetime.now().year
        
        if isinstance(sort, str) and isinstance(direction, str):
            sort_dict = {"property": sort, "direction": direction}
        elif (
            isinstance(sort, list)
            and isinstance(direction, list)
            and len(sort) == len(direction)
        ):
            if not all(isinstance(s, str) for s in sort) or not all(
                isinstance(d, str) for d in direction
            ):
                raise ValueError("Sort and direction must be lists of strings.")
            sort_dict = [
                {"property": s, "direction": d} for s, d in zip(sort, direction)
            ]
        else:
            raise ValueError(
                "Sort and direction must be either both strings or both lists."
            )

        if game_type is not None:
            if game_type not in [2, 3]:
                raise ValueError(
                    "game_type must be either 2 (regular season) or 3 (playoffs)."
                )
            cayenne_exp = f"seasonId={season} and gameTypeId={game_type}"
        else:
            cayenne_exp = f"seasonId={season}"

        sort_dict = json.dumps(sort_dict)

        url_path = f"en/skater/{report}"
        params = {
            "isAggregate": aggregate,
            "isGame": game,
            "limit": limit,
            "start": start,
            "sort": sort_dict,
            "cayenneExp": cayenne_exp,
        }

        response = self._client.get(path=url_path, params=params, web=False)

        if response.status_code != 200:
            raise Exception(
                f"Failed to fetch skater stats: {response.status_code} {response.text}"
            )

        data = response.json()["data"]

        # Convert camelCase to snake_case and update data
        if data:
            self._data = data
            self.players = [
                StatEntity(self._client, data=dict_camel_to_snake(player))
                for player in data
            ]


class GoalieStats(BaseNHLModel):
    """
    GoalieStats model to store goalie statistics.
    """

    def __init__(self, edgework_client, obj_id=None, **kwargs):
        """
        Initialize a GoalieStats object with dynamic attributes.
        """
        super().__init__(edgework_client, obj_id)
        self._data = kwargs
        self.players: list[StatEntity] = []

    def fetch_data(
        self,
        report: str = "summary",
        season: int = None,
        aggregate: bool = False,
        game: bool = True,
        limit: int = -1,
        start: int = 0,
        sort: str | list[str] = "wins",
        direction: str | list[str] = "DESC",
        game_type: int | None = None,
    ) -> None:
        """
        Fetch the data for the goalie stats.

        Args:
            report: The type of report to get (e.g. "summary", "advanced", etc.)
            season: The season to get stats for (e.g. 20232024)
            aggregate: Whether to aggregate the stats
            game: Whether to get game stats
            limit: Number of results to return (-1 for all)
            start: Starting index for results
            sort: Field to sort by
            direction: Direction to sort (e.g. "DESC", "ASC")
            game_type: Type of game (e.g. 2 for regular season, 3 for playoffs)
        """
        if not season:
            season = datetime.now().year * 10000 + (datetime.now().year + 1)

        if isinstance(sort, str) and isinstance(direction, str):
            sort_dict = {"property": sort, "direction": direction}
        elif (
            isinstance(sort, list)
            and isinstance(direction, list)
            and len(sort) == len(direction)
        ):
            if not all(isinstance(s, str) for s in sort) or not all(
                isinstance(d, str) for d in direction
            ):
                raise ValueError("Sort and direction must be lists of strings.")
            sort_dict = [
                {"property": s, "direction": d} for s, d in zip(sort, direction)
            ]
        else:
            raise ValueError(
                "Sort and direction must be either both strings or both lists."
            )

        if game_type is not None:
            if game_type not in [2, 3]:
                raise ValueError(
                    "game_type must be either 2 (regular season) or 3 (playoffs)."
                )
            cayenne_exp = f"seasonId={season} and gameTypeId={game_type}"
        else:
            cayenne_exp = f"seasonId={season}"

        sort_dict = json.dumps(sort_dict)
        url_path = f"en/goalie/{report}"

        params = {
            "isAggregate": aggregate,
            "isGame": game,
            "limit": limit,
            "start": start,
            "sort": sort_dict,
            "cayenneExp": cayenne_exp,
        }
        response = self._client.get(path=url_path, params=params, web=False)
        data = response.json()["data"]

        if data:
            self._data = data
            self.players = [
                StatEntity(self._client, data=dict_camel_to_snake(player))
                for player in data
            ]


class TeamStats(BaseNHLModel):
    """Team Stats model to store team statistics for a season."""

    def __init__(self, edgework_client, obj_id=None, **kwargs):
        """
        Initialize a TeamStats object with dynamic attributes.
        """
        super().__init__(edgework_client, obj_id)
        self._data = kwargs
        self.teams: list[StatEntity] = []

    def fetch_data(
        self,
        report: str = "summary",
        season: int = None,
        aggregate: bool = False,
        game: bool = True,
        limit: int = -1,
        start: int = 0,
        sort: str = "wins",
        direction: str = "DESC",
        game_type: int = 2,
    ) -> None:
        """
        Fetch the data for the team stats.

        Args:
            report: The type of report to get (e.g. "summary", "faceoffpercentages", etc.)
            season: The season to get stats for (e.g. 20232024)
            aggregate: Whether to aggregate the stats
            game: Whether to get game stats. If False, returns aggregate stats.
            limit: Number of results to return (-1 for all). Default is -1.
            start: Starting index for results. Default is 0.
            sort: Field to sort by. Can be a string (e.g. "points") or a list of dicts for multiple fields. Default is "wins".
            direction: Direction to sort (e.g. "DESC", "ASC"). Default is "DESC".
            game_type: Type of game (e.g. 2 for regular season, 3 for playoffs). Default is 2.
        """
        if not season:
            season = datetime.now().year * 10000 + (datetime.now().year + 1)

        if isinstance(sort, str) and isinstance(direction, str):
            sort_dict = {"property": sort, "direction": direction}

        elif (
            isinstance(sort, list)
            and isinstance(direction, list)
            and len(sort) == len(direction)
        ):
            if not all(isinstance(s, str) for s in sort) or not all(
                isinstance(d, str) for d in direction
            ):
                raise ValueError("Sort and direction must be lists of strings.")
            if not all(d in ["ASC", "DESC"] for d in direction):
                raise ValueError("Direction must be either 'ASC' or 'DESC'.")
            sort_dict = [
                {"property": s, "direction": d} for s, d in zip(sort, direction)
            ]
        else:
            raise ValueError(
                "Sort and direction must be either both strings or both lists of the same length."
            )

        if game_type is not None:
            if game_type not in [2, 3]:
                raise ValueError(
                    "game_type must be either 2 (regular season) or 3 (playoffs)."
                )
            cayenne_exp = f"seasonId={season} and gameTypeId={game_type}"
        else:
            cayenne_exp = f"seasonId={season}"

        sort_dict = json.dumps(sort_dict)

        url_path = f"en/team/{report}"
        params = {
            "isAggregate": aggregate,
            "isGame": game,
            "limit": limit,
            "start": start,
            "sort": sort_dict,
            "cayenneExp": cayenne_exp,
        }

        response = self._client.get(path=url_path, params=params, web=False)

        data = response.json().get("data", [])
        if not data:
            raise Exception(
                f"Failed to fetch team stats: {response.status_code} {response.text}"
            )
        data = [dict_camel_to_snake(d) for d in data]
        if data:
            self._data = data
            self.teams = [StatEntity(self._client, data=team) for team in data]
