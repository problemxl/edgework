from edgework.clients.game_client import GameClient
from edgework.clients.schedule_client import ScheduleClient
from edgework.clients.standings_client import StandingClient
from edgework.clients.stats_client import StatsClient
from edgework.clients.glossary_client import GlossaryClient
from edgework.clients.player_client import PlayerClient
from edgework.clients.shift_client import ShiftClient
from edgework.clients.team_client import TeamClient
from edgework.clients.draft_client import DraftClient
from edgework.clients.playoffs_client import PlayoffsClient
from edgework.clients.season_client import SeasonClient
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
        self.shifts: ShiftClient = ShiftClient(self._client)
        self.team: TeamClient = TeamClient(self._client)
        self.draft: DraftClient = DraftClient(self._client)
        self.playoffs: PlayoffsClient = PlayoffsClient(self._client)
        self.season: SeasonClient = SeasonClient(self._client)
