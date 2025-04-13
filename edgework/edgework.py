from edgework.clients.game_client import GameClient
from edgework.clients.player_client import PlayerClient
from edgework.clients.schedule_client import ScheduleClient
from edgework.clients.standings_client import StandingClient
from edgework.clients.stats_client import StatsClient
from edgework.clients.glossary_client import GlossaryClient
from edgework.http_client import SyncHttpClient


class Edgework:
    def __init__(self):
        self._client = SyncHttpClient()

        self.schedule: ScheduleClient = ScheduleClient(self._client)
        self.game: GameClient = GameClient(self._client)
        self.standings: StandingClient = StandingClient(self._client)
        self.stats: StatsClient = StatsClient(self._client)
        self.glossary: GlossaryClient = GlossaryClient(self._client)
        self.player: PlayerClient = PlayerClient(self._client)

    class _Internal:
        def __init__(self):
            pass

        class _HttpClient:
            
            def get(self, endpoint: str, params: dict = None, api_type: str = "web") -> dict:
                """
                Get data from the NHL API.
                Parameters
                ----------
                endpoint : str
                    The endpoint to get data from.
                params : dict, optional
                    The parameters to pass to the endpoint.
                api_type : str, optional
                    The type of API to use. Default is 'web'. Other options are 'stats' and 'draft'.
                
                Returns
                -------
                dict
                    The data returned from the API.
                """
                pass

            class _Parser:
                def parse_player_landing(self, data: dict) -> dict:
                    """
                    Parse player landing data from the NHL API.
                    Parameters
                    ----------
                    data : dict
                        The data to parse.
                    
                    Returns
                    -------
                    dict
                        The parsed data.
                    """
                    # TODO: Implement using pydantic models, .model_validate(date)
                    pass

                # TODO: Implement other parsing methods using pydantic models, .model_validate(data)
