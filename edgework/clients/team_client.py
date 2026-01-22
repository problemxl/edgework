from edgework.http_client import HttpClient
from edgework.models.roster import Roster
from edgework.models.prospect import Prospects
from edgework.models.team_stats import TeamStats


class TeamClient:
    def __init__(self, client: HttpClient):
        self._client = client

    def get_roster(self, team_abbr: str, season: int) -> Roster:
        """Get the roster for a given team and season.

        Parameters
        ----------
        team_abbr : str
            The three-letter abbreviation of the team.
        season : int
            The season in YYYYYYYY format (e.g., 20232024).

        Returns
        -------
        Roster
            A Roster object containing forwards, defensemen, and goalies.

        """
        response = self._client.get(f"roster/{team_abbr}/{season}")
        return Roster.from_api(response.json())

    def get_roster_current(self, team_abbr: str) -> Roster:
        """Get the current roster for a given team.

        Parameters
        ----------
        team_abbr : str
            The three-letter abbreviation of the team.

        Returns
        -------
        Roster
            A Roster object containing forwards, defensemen, and goalies.

        """
        response = self._client.get(f"roster/{team_abbr}/current")
        return Roster.from_api(response.json())

    def get_prospects(self, team_abbr: str) -> Prospects:
        """Get the prospects for a given team.

        Parameters
        ----------
        team_abbr : str
            The three-letter abbreviation of the team.

        Returns
        -------
        Prospects
            A Prospects object containing forwards, defensemen, and goalies.

        """
        response = self._client.get(f"prospects/{team_abbr}")
        return Prospects.from_api(response.json())

    def get_roster_seasons(self, team_abbr: str) -> list[int]:
        """Get the list of seasons a team played in.

        Parameters
        ----------
        team_abbr : str
            The three-letter abbreviation of the team.

        Returns
        -------
        list[int]
            A list of season IDs.

        """
        response = self._client.get(f"roster-season/{team_abbr}")
        return response.json()

    def get_stats_now(self, team_abbr: str) -> TeamStats:
        """Get the current statistics for a given team.

        Parameters
        ----------
        team_abbr : str
            The three-letter abbreviation of the team.

        Returns
        -------
        TeamStats
            A TeamStats object containing the team's current statistics.

        """
        response = self._client.get(f"club-stats/{team_abbr}/now")
        return TeamStats.from_dict(response.json())

    def get_stats(self, team_abbr: str, season: int, game_type: int = 2) -> TeamStats:
        """Get the statistics for a given team, season, and game type.

        Parameters
        ----------
        team_abbr : str
            The three-letter abbreviation of the team.
        season : int
            The season in YYYYYYYY format (e.g., 20232024).
        game_type : int, optional
            The game type (default: 2 for regular season, 3 for playoffs).

        Returns
        -------
        TeamStats
            A TeamStats object containing the team's statistics.

        """
        response = self._client.get(f"club-stats/{team_abbr}/{season}/{game_type}")
        return TeamStats.from_dict(response.json())
