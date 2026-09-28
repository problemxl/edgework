from edgework.clients.draft_client import DraftClient
from edgework.clients.edge_client import EdgeClient
from edgework.clients.game_client import GameClient
from edgework.clients.glossary_client import GlossaryClient
from edgework.clients.network_client import NetworkClient
from edgework.clients.player_client import PlayerClient
from edgework.clients.playoff_client import PlayoffClient
from edgework.clients.schedule_client import ScheduleClient
from edgework.clients.shift_client import ShiftClient
from edgework.clients.standings_client import StandingClient
from edgework.clients.stats_client import StatsClient
from edgework.clients.team_client import TeamClient
from edgework.clients.utility_client import UtilityClient
from edgework.http_client import HttpClient

from edgework.models.player import Player
from edgework.models.schedule import Schedule
from edgework.models.stats import GoalieStats, SkaterStats, TeamStats
from edgework.models.team import Roster, Team
from edgework.utilities import validate_season_format as _validate_season_format


class Edgework:
    """Main Edgework NHL API client with access to all endpoints.
    This class provides a unified interface to all NHL API endpoints    through dedicated client instances.
    Usage:
        >>> import edgework
        >>> client = edgework.Edgework()
        >>>
        >>> # Get current standings
        >>> standings = client.standings.get_standings()
        >>>
        >>> # Get today's games
        >>> games = client.games.get_current_games()
        >>>
        >>> # Get player information
        >>> player = client.players.get_player(8478402)
    """

    def __init__(self, user_agent: str = "EdgeworkClient/2.0"):
        """
        Initializes the Edgework API client with all sub-clients.

        Args:
            user_agent (str, optional): The User-Agent string for requests.
                Defaults to "EdgeworkClient/2.0".
        """
        self._client = HttpClient(user_agent=user_agent)

        # Expose all clients as public attributes
        self.players = PlayerClient(http_client=self._client)
        self.teams = TeamClient(client=self._client)
        self.schedule = ScheduleClient(client=self._client)
        self.games = GameClient(client=self._client)
        self.standings = StandingClient(client=self._client)
        self.draft = DraftClient(client=self._client)
        self.edge = EdgeClient(http_client=self._client)
        self.stats = StatsClient(client=self._client)
        self.playoffs = PlayoffClient(client=self._client)
        self.network = NetworkClient(client=self._client)
        self.utility = UtilityClient(client=self._client)
        self.glossary = GlossaryClient(client=self._client)
        self.shifts = ShiftClient(client=self._client)

        # Initialize model handlers
        self._skaters = SkaterStats(edgework_client=self._client)
        self._goalies = GoalieStats(edgework_client=self._client)
        self._team_stats = TeamStats(edgework_client=self._client)

    def get_all_players(self, active_only: bool = True) -> list[Player]:
        """
        Fetch a list of players.

        Args:
            active_only (bool): If True, fetch only active players.
                If False, fetch all players. Defaults to True.

        Returns:
            list[Player]: A list of Player objects.
        """
        if active_only:
            return self.players.get_active_players()
        else:
            return self.players.get_all_players()

    def get_player(self, player_id: int) -> Player:
        """
        Get a player by ID.

        Args:
            player_id (int): The NHL player ID.

        Returns:
            Player: A Player object with full details.
        """
        return self.players.get_player(player_id)

    def get_teams(self) -> list[Team]:
        """
        Fetch a list of all NHL teams.

        Returns:
            list[Team]: A list of Team objects.
        """
        return self.teams.get_teams()

    def get_roster(self, team_code: str, season: str = None) -> Roster:
        """
        Fetch a roster for a specific team.

        Args:
            team_code (str): The team code (e.g., 'TOR', 'NYR').
            season (str, optional): The season in format "YYYY-YYYY".
                If None, gets current roster.

        Returns:
            Roster: A Roster object containing the team's players.
        """
        converted_season = None
        if season:
            converted_season = _validate_season_format(season)
        return self.teams.get_roster(team_code, converted_season)

    def get_schedule_now(self) -> Schedule:
        """
        Get the current NHL schedule.

        Returns:
            Schedule: Current NHL schedule.
        """
        return self.schedule.get_schedule()

    def get_schedule_for_date(self, date: str) -> Schedule:
        """
        Get the NHL schedule for a specific date.

        Args:
            date (str): The date in format 'YYYY-MM-DD'.

        Returns:
            Schedule: NHL schedule for the specified date.
        """
        return self.schedule.get_schedule_for_date(date)

    def close(self):
        """Closes the underlying HTTP client session."""
        if hasattr(self._client, "close"):
            self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
