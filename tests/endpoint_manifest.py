"""Declarative endpoint coverage manifest.

This module is the *coverage contract* between the NHL API documentation
(``edgework/NHL API Documentation.md``), the endpoint registry
(:data:`edgework.endpoints.API_PATH`) and the implementing client methods.

Every canonical documented server route gets exactly one :class:`ManifestEntry`
mapping it to the client method that owns the request. ``test_endpoint_coverage``
uses the manifest to assert, for every documented route:

- the registry entry exists and the invoked client produces the URL derived
  from it (host + version/language prefix + path-param substitution),
- query parameters travel in ``params`` (never embedded in the route string),
- Web vs. Stats routing targets the documented host,
- the documented return type is produced.

Exclusions
----------
Only *unique server routes* appear here:

- **Composite helpers** (methods that fan one route out into many requests,
  e.g. ``GameClient.get_games_for_date`` = schedule + per-game boxscores) are
  excluded; the canonical route they consume is manifested instead.
- **Duplicate model accessors** (model-side fetches that delegate to or repeat
  a client route, e.g. ``Config.fetch_data`` for ``/{lang}/config``) are listed
  on ``also_implemented_by`` so their existence is still verified, without a
  second manifest entry for the same server route.

Maintenance
-----------
Add a route to :data:`edgework.endpoints.API_PATH` → add a matching
:class:`ManifestEntry` here. The completeness test fails otherwise, so the
registry and the documentation can never silently drift apart.
"""

from dataclasses import dataclass, field
from typing import Any, Optional

from edgework.models.draft import Draft, DraftRanking
from edgework.models.glossary import Glossary
from edgework.models.play_by_play import PlayByPlay
from edgework.models.schedule import Schedule
from edgework.models.standings import Standings
from edgework.models.team import Roster, Team


# ---------------------------------------------------------------------------
# Minimal mock payloads shared by manifest entries. Each payload is shaped so
# the implementing method can parse it without errors (they are intentionally
# minimal — parsing itself is covered by the per-client test suites).
# ---------------------------------------------------------------------------

def _team_row(team_id: int = 10, abbrev: str = "TOR") -> dict:
    return {
        "teamId": team_id,
        "fullName": "Toronto Maple Leafs",
        "abbreviation": abbrev,
    }


def _standings_row() -> dict:
    return {"teamName": {"default": "Toronto Maple Leafs"}, "teamAbbrev": "TOR"}


def _roster_payload() -> dict:
    return {
        "season": 20232024,
        "teamAbbrev": "TOR",
        "teamId": 10,
        "forwards": [],
        "defensemen": [],
        "goalies": [],
    }


def _schedule_payload() -> dict:
    return {"gameWeek": [], "previousStartDate": None}


def _play_by_play_payload() -> dict:
    return {
        "id": 2023020204,
        "season": 20232024,
        "gameType": 2,
        "gameDate": "2023-11-10",
        "startTimeUTC": "2023-11-10T23:00:00Z",
        "plays": [],
    }


def _draft_picks_payload() -> dict:
    return {"draftYear": 2023, "rounds": [], "picks": []}


def _report_row(skater_id: int = 8478402) -> dict:
    return {"skaterId": skater_id, "points": 20}


def _edge_seasons() -> list:
    """``seasonsWithEdgeStats`` — tracking data exists from 2024-25 on."""
    return [{"id": 20242025, "gameTypes": [2, 3]}]


def _edge_measure(imperial: float, metric: float) -> dict:
    """Edge measures arrive as imperial/metric pairs (see the research doc)."""
    return {"imperial": imperial, "metric": metric}


@dataclass(frozen=True)
class ManifestEntry:
    """One canonical documented route and its implementing client method.

    Attributes:
        registry_key: Key in :data:`edgework.endpoints.API_PATH`.
        target: Dotted path ``module.Class.method`` of the implementing method.
        web: True for the Web API host (api-web.nhle.com), False for the
            Stats API host (api.nhle.com/stats/rest/).
        args: Positional arguments for the implementing method.
        call: Keyword arguments for the implementing method.
        endpoint_params: Path-placeholder → sample value used to derive the
            expected URL from the registry template.
        expected_params: Exact query-parameter dict the method must pass to
            ``HttpClient.get(params=...)``. ``None`` means "no query
            parameters" (``params`` omitted, ``None`` or empty).
        payload: JSON body served to the method by the mocked HTTP layer.
        returns: Acceptable return type(s); ``None`` skips the type assertion.
        lang: Stats API language segment used by the default invocation
            (``None`` for the non-language-prefixed ``/ping`` route).
        lang_kwarg: Whether the method accepts a ``lang=`` keyword (enables
            the alternate-language route test).
        also_implemented_by: Dotted paths of model accessors / convenience
            methods that hit the same server route (existence-verified only).
        note: Free-form clarification.
    """

    registry_key: str
    target: str
    web: bool
    args: tuple = ()
    call: dict = field(default_factory=dict)
    endpoint_params: dict = field(default_factory=dict)
    expected_params: Optional[dict] = None
    payload: Any = None
    returns: Optional[tuple] = None
    lang: Optional[str] = "en"
    lang_kwarg: bool = False
    also_implemented_by: tuple = ()
    note: str = ""


# ---------------------------------------------------------------------------
# Web API (api-web.nhle.com) — canonical documented routes
# ---------------------------------------------------------------------------

ENDPOINT_MANIFEST: dict[str, ManifestEntry] = {
    # -- Player information -------------------------------------------------
    "player_game_logs": ManifestEntry(
        registry_key="player_game_logs",
        target="edgework.clients.player_client.PlayerClient.get_player_game_logs",
        web=True,
        args=(8478402,),
        call={"season": "2023-2024", "game_type": 2},
        endpoint_params={"player_id": 8478402, "season": 20232024, "game-type": 2},
        payload={"gameLog": []},
        returns=(dict,),
    ),
    "player_game_log_now": ManifestEntry(
        registry_key="player_game_log_now",
        target="edgework.clients.player_client.PlayerClient.get_player_game_log_now",
        web=True,
        args=(8478402,),
        endpoint_params={"player_id": 8478402},
        payload={"gameLog": []},
        returns=(dict,),
    ),
    "player_landing": ManifestEntry(
        registry_key="player_landing",
        target="edgework.clients.player_client.PlayerClient.get_player_landing",
        web=True,
        args=(8478402,),
        endpoint_params={"player_id": 8478402},
        payload={"playerId": 8478402, "firstName": {"default": "Connor"}},
        returns=(dict,),
        also_implemented_by=(
            "edgework.clients.player_client.PlayerClient.get_player",
            "edgework.models.player.Player.fetch_data",
            "edgework.clients.draft_client.DraftClient.get_draftee",
        ),
        note="Duplicate accessors all reuse the landing route.",
    ),
    "player_spotlight": ManifestEntry(
        registry_key="player_spotlight",
        target="edgework.clients.player_client.PlayerClient.get_player_spotlight",
        web=True,
        payload=[{"id": 8478402}],
        returns=(list,),
    ),
    # -- Web leaderboards ---------------------------------------------------
    "skater_stats_now": ManifestEntry(
        registry_key="skater_stats_now",
        target="edgework.clients.stats_client.StatsClient.get_skater_stats_leaders",
        web=True,
        call={"categories": ["goals", "assists"], "limit": 5},
        expected_params={"categories": "goals,assists", "limit": 5},
        payload={},
        returns=(dict,),
        note="Multi-category lists are joined with commas (documented encoding).",
    ),
    "skater_stats_season_game_type": ManifestEntry(
        registry_key="skater_stats_season_game_type",
        target=(
            "edgework.clients.stats_client."
            "StatsClient.get_skater_stats_leaders_by_season"
        ),
        web=True,
        call={"season": "2022-2023", "game_type": 2, "categories": "assists", "limit": 3},
        endpoint_params={"season": 20222023, "game-type": 2},
        expected_params={"categories": "assists", "limit": 3},
        payload={},
        returns=(dict,),
    ),
    "goalie_stats_now": ManifestEntry(
        registry_key="goalie_stats_now",
        target="edgework.clients.stats_client.StatsClient.get_goalie_stats_leaders",
        web=True,
        call={"categories": "wins", "limit": 5},
        expected_params={"categories": "wins", "limit": 5},
        payload={},
        returns=(dict,),
    ),
    "goalie_stats_season_game_type": ManifestEntry(
        registry_key="goalie_stats_season_game_type",
        target=(
            "edgework.clients.stats_client."
            "StatsClient.get_goalie_stats_leaders_by_season"
        ),
        web=True,
        call={"season": "2023-2024", "game_type": 2, "categories": "wins", "limit": 3},
        endpoint_params={"season": 20232024, "game-type": 2},
        expected_params={"categories": "wins", "limit": 3},
        payload={},
        returns=(dict,),
    ),
    # -- Standings -----------------------------------------------------------
    "standings": ManifestEntry(
        registry_key="standings",
        target="edgework.clients.standings_client.StandingClient.get_standings",
        web=True,
        endpoint_params={},
        expected_params={},
        payload={"standings": [_standings_row()]},
        returns=(Standings,),
        note="Default invocation (date='now') requests the /standings/now route.",
    ),
    "standings_date": ManifestEntry(
        registry_key="standings_date",
        target="edgework.clients.standings_client.StandingClient.get_standings",
        web=True,
        args=("2023-11-10",),
        endpoint_params={"date": "2023-11-10"},
        expected_params={},
        payload={"standings": [_standings_row()]},
        returns=(Standings,),
    ),
    "standings_season": ManifestEntry(
        registry_key="standings_season",
        target="edgework.clients.standings_client.StandingClient.get_standings_for_season",
        web=True,
        args=("2023-2024",),
        expected_params={"seasonId": 20232024},
        payload={"data": [_standings_row()]},
        returns=(Standings,),
    ),
    # -- Club stats / team ---------------------------------------------------
    "club_stats": ManifestEntry(
        registry_key="club_stats",
        target="edgework.clients.team_client.TeamClient.get_team_stats",
        web=True,
        args=("TOR",),
        endpoint_params={"team": "TOR"},
        payload={},
        returns=(dict,),
        also_implemented_by=("edgework.models.team.Team.get_stats",),
        note="season=None requests the documented /club-stats/{team}/now route.",
    ),
    "club_stats_season": ManifestEntry(
        registry_key="club_stats_season",
        target="edgework.clients.team_client.TeamClient.get_club_stats_season",
        web=True,
        args=("TOR",),
        endpoint_params={"team": "TOR"},
        payload={},
        returns=(dict,),
    ),
    "club_stats_season_game_type": ManifestEntry(
        registry_key="club_stats_season_game_type",
        target="edgework.clients.team_client.TeamClient.get_team_stats",
        web=True,
        args=("TOR", 20232024, 2),
        endpoint_params={"team": "TOR", "season": 20232024, "game-type": 2},
        payload={},
        returns=(dict,),
        also_implemented_by=("edgework.models.team.Team.get_stats",),
    ),
    "team_scoreboard": ManifestEntry(
        registry_key="team_scoreboard",
        target="edgework.clients.team_client.TeamClient.get_scoreboard",
        web=True,
        args=("TOR",),
        endpoint_params={"team": "TOR"},
        payload={},
        returns=(dict,),
    ),
    # -- Roster ---------------------------------------------------------------
    "roster_current": ManifestEntry(
        registry_key="roster_current",
        target="edgework.clients.team_client.TeamClient.get_roster",
        web=True,
        args=("TOR",),
        endpoint_params={"team": "TOR"},
        payload=_roster_payload(),
        returns=(Roster,),
        also_implemented_by=(
            "edgework.models.team.Roster.fetch_data",
            "edgework.models.team.Team.get_roster",
        ),
    ),
    "roster_season": ManifestEntry(
        registry_key="roster_season",
        target="edgework.clients.team_client.TeamClient.get_roster",
        web=True,
        args=("TOR", 20232024),
        endpoint_params={"team": "TOR", "season": 20232024},
        payload=_roster_payload(),
        returns=(Roster,),
        also_implemented_by=("edgework.models.team.Team.get_roster",),
    ),
    "roster_season_team": ManifestEntry(
        registry_key="roster_season_team",
        target="edgework.clients.team_client.TeamClient.get_roster_season",
        web=True,
        args=("TOR",),
        endpoint_params={"team": "TOR"},
        payload={},
        returns=(dict,),
    ),
    "team_prospects": ManifestEntry(
        registry_key="team_prospects",
        target="edgework.clients.team_client.TeamClient.get_team_prospects",
        web=True,
        args=("TOR",),
        endpoint_params={"team": "TOR"},
        payload={"prospects": []},
        returns=(dict,),
        also_implemented_by=("edgework.clients.draft_client.DraftClient.get_prospect_info",),
        note="DraftClient.get_prospect_info uses the same route with a prospect ID.",
    ),
    # -- Team schedule ---------------------------------------------------------
    "club_schedule_season_now": ManifestEntry(
        registry_key="club_schedule_season_now",
        target="edgework.clients.schedule_client.ScheduleClient.get_schedule_for_team",
        web=True,
        args=("TOR",),
        endpoint_params={"team": "TOR"},
        payload=_schedule_payload(),
        returns=(Schedule,),
        also_implemented_by=("edgework.models.team.Team.get_schedule",),
    ),
    "club_schedule_season": ManifestEntry(
        registry_key="club_schedule_season",
        target="edgework.clients.team_client.TeamClient.get_team_schedule",
        web=True,
        args=("TOR", 20232024),
        endpoint_params={"team": "TOR", "season": 20232024},
        payload={},
        returns=(dict,),
        also_implemented_by=("edgework.models.team.Team.get_schedule",),
    ),
    "club_schedule_month_now": ManifestEntry(
        registry_key="club_schedule_month_now",
        target=(
            "edgework.clients.schedule_client."
            "ScheduleClient.get_schedule_for_team_for_month"
        ),
        web=True,
        args=("TOR",),
        endpoint_params={"team": "TOR"},
        payload=_schedule_payload(),
        returns=(Schedule,),
        note="month=None requests the documented .../month/now route.",
    ),
    "club_schedule_month": ManifestEntry(
        registry_key="club_schedule_month",
        target=(
            "edgework.clients.schedule_client."
            "ScheduleClient.get_schedule_for_team_for_month"
        ),
        web=True,
        args=("TOR", "2023-11"),
        endpoint_params={"team": "TOR", "month": "2023-11"},
        payload=_schedule_payload(),
        returns=(Schedule,),
    ),
    "club_schedule_week": ManifestEntry(
        registry_key="club_schedule_week",
        target=(
            "edgework.clients.schedule_client."
            "ScheduleClient.get_schedule_for_team_for_week"
        ),
        web=True,
        args=("TOR", "2023-11-10"),
        endpoint_params={"team": "TOR", "date": "2023-11-10"},
        payload=_schedule_payload(),
        returns=(Schedule,),
    ),
    "club_schedule_week_now": ManifestEntry(
        registry_key="club_schedule_week_now",
        target=(
            "edgework.clients.schedule_client."
            "ScheduleClient.get_schedule_for_team_for_week"
        ),
        web=True,
        args=("TOR",),
        endpoint_params={"team": "TOR"},
        payload=_schedule_payload(),
        returns=(Schedule,),
        note="date=None requests the documented .../week/now route.",
    ),
    # -- League schedule ---------------------------------------------------------
    "schedule_now": ManifestEntry(
        registry_key="schedule_now",
        target="edgework.clients.schedule_client.ScheduleClient.get_schedule",
        web=True,
        payload=_schedule_payload(),
        returns=(Schedule,),
        also_implemented_by=("edgework.clients.game_client.GameClient.get_current_games",),
        note="GameClient.get_current_games is a composite consumer of this route.",
    ),
    "schedule_date": ManifestEntry(
        registry_key="schedule_date",
        target="edgework.clients.schedule_client.ScheduleClient.get_schedule_for_date",
        web=True,
        args=("2023-11-10",),
        endpoint_params={"date": "2023-11-10"},
        payload=_schedule_payload(),
        returns=(Schedule,),
        also_implemented_by=("edgework.clients.game_client.GameClient.get_games_for_date",),
    ),
    "schedule_calendar_now": ManifestEntry(
        registry_key="schedule_calendar_now",
        target="edgework.clients.schedule_client.ScheduleClient.get_schedule_calendar",
        web=True,
        payload={"dates": []},
        returns=(dict,),
    ),
    "schedule_calendar_date": ManifestEntry(
        registry_key="schedule_calendar_date",
        target=(
            "edgework.clients.schedule_client."
            "ScheduleClient.get_schedule_calendar_for_date"
        ),
        web=True,
        args=("2023-11-10",),
        endpoint_params={"date": "2023-11-10"},
        payload={"dates": []},
        returns=(dict,),
    ),
    # -- Daily scores ----------------------------------------------------------
    "score_now": ManifestEntry(
        registry_key="score_now",
        target="edgework.clients.game_client.GameClient.get_score",
        web=True,
        payload={"games": []},
        returns=(dict,),
    ),
    "score_date": ManifestEntry(
        registry_key="score_date",
        target="edgework.clients.game_client.GameClient.get_score",
        web=True,
        args=("2023-11-10",),
        endpoint_params={"date": "2023-11-10"},
        payload={"games": []},
        returns=(dict,),
    ),
    "scoreboard_now": ManifestEntry(
        registry_key="scoreboard_now",
        target="edgework.clients.game_client.GameClient.get_scoreboard",
        web=True,
        payload={},
        returns=(dict,),
    ),
    "where_to_watch": ManifestEntry(
        registry_key="where_to_watch",
        target="edgework.clients.network_client.NetworkClient.get_where_to_watch",
        web=True,
        payload={"streams": []},
        returns=(dict,),
        note="The real streaming route; NOT partner-game odds.",
    ),
    # -- Game events ------------------------------------------------------------
    "play_by_play": ManifestEntry(
        registry_key="play_by_play",
        target="edgework.clients.game_client.GameClient.get_play_by_play",
        web=True,
        args=(2023020204,),
        endpoint_params={"game_id": 2023020204},
        payload=_play_by_play_payload(),
        returns=(PlayByPlay,),
        also_implemented_by=("edgework.models.game.Game._get_play_by_play",),
    ),
    "game_landing": ManifestEntry(
        registry_key="game_landing",
        target="edgework.clients.game_client.GameClient.get_game_landing",
        web=True,
        args=(2023020204,),
        endpoint_params={"game_id": 2023020204},
        payload={"id": 2023020204},
        returns=(dict,),
        also_implemented_by=(
            "edgework.clients.network_client.NetworkClient.get_broadcasts_for_game",
        ),
    ),
    "game_boxscore": ManifestEntry(
        registry_key="game_boxscore",
        target="edgework.clients.game_client.GameClient.get_game_boxscore",
        web=True,
        args=(2023020204,),
        endpoint_params={"game_id": 2023020204},
        payload={"id": 2023020204},
        returns=(dict,),
        also_implemented_by=(
            "edgework.clients.game_client.GameClient.get_game",
            "edgework.models.game.Game.fetch_data",
        ),
        note="Model-level Game access delegates to the same route (Task 5).",
    ),
    "game_story": ManifestEntry(
        registry_key="game_story",
        target="edgework.clients.game_client.GameClient.get_game_story",
        web=True,
        args=(2023020204,),
        endpoint_params={"game_id": 2023020204},
        payload={"id": 2023020204},
        returns=(dict,),
    ),
    "game_right_rail": ManifestEntry(
        registry_key="game_right_rail",
        target="edgework.clients.game_client.GameClient.get_game_right_rail",
        web=True,
        args=(2023020204,),
        endpoint_params={"game_id": 2023020204},
        payload={},
        returns=(dict,),
    ),
    "wsc_play_by_play": ManifestEntry(
        registry_key="wsc_play_by_play",
        target="edgework.clients.game_client.GameClient.get_wsc_play_by_play",
        web=True,
        args=(2023020204,),
        endpoint_params={"game_id": 2023020204},
        payload={"gameId": 2023020204, "plays": []},
        returns=(dict,),
        note="Distinct from the gamecenter play-by-play route.",
    ),
    # -- Network / odds ------------------------------------------------------------
    "tv_schedule_date": ManifestEntry(
        registry_key="tv_schedule_date",
        target="edgework.clients.network_client.NetworkClient.get_tv_schedule",
        web=True,
        args=("2023-11-10",),
        endpoint_params={"date": "2023-11-10"},
        payload={"games": []},
        returns=(dict,),
    ),
    "tv_schedule_now": ManifestEntry(
        registry_key="tv_schedule_now",
        target="edgework.clients.network_client.NetworkClient.get_tv_schedule_now",
        web=True,
        payload={"games": []},
        returns=(dict,),
    ),
    "partner_game": ManifestEntry(
        registry_key="partner_game",
        target="edgework.clients.network_client.NetworkClient.get_partner_game_odds",
        web=True,
        args=("US",),
        endpoint_params={"country_code": "US"},
        payload={"games": []},
        returns=(dict,),
        also_implemented_by=(
            "edgework.clients.game_client.GameClient.get_partner_game_odds",
        ),
        note="Odds route; GameClient.get_where_to_watch is a deprecated alias of it.",
    ),
    # -- Playoffs ---------------------------------------------------------------------
    "playoff_series_carousel": ManifestEntry(
        registry_key="playoff_series_carousel",
        target="edgework.clients.playoff_client.PlayoffClient.get_playoff_series_carousel",
        web=True,
        args=("2023-2024",),
        endpoint_params={"season": 20232024},
        payload={"seasonId": 20232024, "round": 1},
        returns=(dict,),
    ),
    "playoff_series_schedule": ManifestEntry(
        registry_key="playoff_series_schedule",
        target="edgework.clients.playoff_client.PlayoffClient.get_playoff_series_schedule",
        web=True,
        args=("2023-2024", "A"),
        endpoint_params={"season": 20232024, "series_letter": "A"},
        payload={"series": []},
        returns=(dict,),
    ),
    "playoff_bracket": ManifestEntry(
        registry_key="playoff_bracket",
        target="edgework.clients.playoff_client.PlayoffClient.get_playoff_bracket",
        web=True,
        args=(2022,),
        endpoint_params={"year": 2022},
        payload={"seasonId": 20222023, "rounds": []},
        returns=(dict,),
        note="PlayoffClient.get_playoff_series_by_round composes on this route.",
    ),
    # -- Season / draft -----------------------------------------------------------------
    "season": ManifestEntry(
        registry_key="season",
        target="edgework.clients.utility_client.UtilityClient.get_season",
        web=True,
        payload={"seasons": []},
        returns=(dict,),
    ),
    "draft_rankings_now": ManifestEntry(
        registry_key="draft_rankings_now",
        target="edgework.clients.draft_client.DraftClient.get_draft_rankings",
        web=True,
        expected_params={},
        payload={"rankings": []},
        returns=(DraftRanking,),
    ),
    "draft_rankings": ManifestEntry(
        registry_key="draft_rankings",
        target="edgework.clients.draft_client.DraftClient.get_draft_rankings",
        web=True,
        args=("2023-2024", "1"),
        endpoint_params={"season": 2023, "prospect_category": "1"},
        expected_params={},
        payload={"rankings": []},
        returns=(DraftRanking,),
    ),
    "draft_tracker_picks_now": ManifestEntry(
        registry_key="draft_tracker_picks_now",
        target="edgework.clients.draft_client.DraftClient.get_draft_tracker_picks",
        web=True,
        expected_params={},
        payload={"picks": []},
        returns=(list,),
    ),
    "draft_picks_now": ManifestEntry(
        registry_key="draft_picks_now",
        target="edgework.clients.draft_client.DraftClient.get_draft_picks",
        web=True,
        expected_params={},
        payload=_draft_picks_payload(),
        returns=(Draft,),
    ),
    "draft_picks": ManifestEntry(
        registry_key="draft_picks",
        target="edgework.clients.draft_client.DraftClient.get_draft_picks",
        web=True,
        args=("2023-2024", "all"),
        endpoint_params={"season": 2023, "round": "all"},
        expected_params={},
        payload=_draft_picks_payload(),
        returns=(Draft,),
    ),
    # -- Miscellaneous -----------------------------------------------------------------
    "meta": ManifestEntry(
        registry_key="meta",
        target="edgework.clients.utility_client.UtilityClient.get_meta",
        web=True,
        payload={"players": [], "teams": []},
        returns=(dict,),
    ),
    "meta_game": ManifestEntry(
        registry_key="meta_game",
        target="edgework.clients.utility_client.UtilityClient.get_meta_game",
        web=True,
        args=(2023020204,),
        endpoint_params={"game_id": 2023020204},
        payload={},
        returns=(dict,),
    ),
    "location": ManifestEntry(
        registry_key="location",
        target="edgework.clients.utility_client.UtilityClient.get_location",
        web=True,
        payload={"locations": []},
        returns=(dict,),
    ),
    "meta_playoff_series": ManifestEntry(
        registry_key="meta_playoff_series",
        target="edgework.clients.utility_client.UtilityClient.get_meta_playoff_series",
        web=True,
        args=(2023, "a"),
        endpoint_params={"year": 2023, "series_letter": "a"},
        payload={},
        returns=(dict,),
    ),
    "postal_lookup": ManifestEntry(
        registry_key="postal_lookup",
        target="edgework.clients.utility_client.UtilityClient.get_postal_lookup",
        web=True,
        args=("90210",),
        endpoint_params={"postal_code": "90210"},
        payload={},
        returns=(dict,),
    ),
    "goal_replay": ManifestEntry(
        registry_key="goal_replay",
        target="edgework.clients.game_client.GameClient.get_goal_replay",
        web=True,
        args=(2023020204, 12),
        endpoint_params={"game_id": 2023020204, "event_number": 12},
        payload={},
        returns=(dict,),
    ),
    "play_replay": ManifestEntry(
        registry_key="play_replay",
        target="edgework.clients.game_client.GameClient.get_play_replay",
        web=True,
        args=(2023020204, 12),
        endpoint_params={"game_id": 2023020204, "event_number": 12},
        payload={},
        returns=(dict,),
        also_implemented_by=(
            "edgework.clients.edge_client.EdgeClient.get_goal_frames",
        ),
        note=(
            "EdgeClient.get_goal_frames is a composite consumer: it chains "
            "this route to the pptReplayUrl on the sprites host (with a "
            "Referer header) — manifested here, excluded there."
        ),
    ),
    "openapi_spec": ManifestEntry(
        registry_key="openapi_spec",
        target="edgework.clients.utility_client.UtilityClient.get_openapi_spec",
        web=True,
        payload={"openapi": "3.0.1", "paths": {}},
        returns=(dict,),
        note="Served outside the /v1 namespace; HttpClient must not double-prefix /v1.",
    ),
    # ---------------------------------------------------------------------------
    # NHL Edge (api-web.nhle.com /v1/edge/...) — canonical documented routes
    #
    # Reverse-engineered from the NHL Edge web app; the full catalog, response
    # schemas and quirks live in ``docs/research/nhl-edge-endpoints.md``. The
    # mock payloads below are minimal shapes derived from that research — Edge
    # responses carry no stable model, so the clients return them as-is.
    #
    # Composite helpers are excluded per the manifest rules (their canonical
    # routes are manifested here):
    #   - ``EdgeClient.compare()`` fans out to the three *_comparison routes.
    #   - ``EdgeClient.get_available_seasons()`` reads ``seasonsWithEdgeStats``
    #     off the skater landing route.
    #   - ``EdgeClient.get_goal_frames()`` chains the manifested ``play_replay``
    #     route to the sprites host (listed on play_replay.also_implemented_by).
    #
    # The entries invoke the explicit-season form: ``season="now"`` (the
    # methods' default) collapses the ``{season}/{game-type}`` template tail
    # into a single ``now`` segment via 307 redirect, which the registry
    # template cannot express.
    # ---------------------------------------------------------------------------

    # -- Landing pages (season leaderboards) ---------------------------------
    "edge_skater_landing": ManifestEntry(
        registry_key="edge_skater_landing",
        target="edgework.clients.edge_client.EdgeClient.get_skater_landing",
        web=True,
        call={"season": "20252026", "game_type": 2},
        endpoint_params={"season": 20252026, "game-type": 2},
        payload={"seasonsWithEdgeStats": _edge_seasons(), "hardestShot": {}},
        returns=(dict,),
        also_implemented_by=(
            "edgework.clients.edge_client.EdgeClient.get_available_seasons",
        ),
        note="get_available_seasons is a composite consumer of seasonsWithEdgeStats.",
    ),
    "edge_goalie_landing": ManifestEntry(
        registry_key="edge_goalie_landing",
        target="edgework.clients.edge_client.EdgeClient.get_goalie_landing",
        web=True,
        call={"season": "20252026", "game_type": 2},
        endpoint_params={"season": 20252026, "game-type": 2},
        payload={"seasonsWithEdgeStats": _edge_seasons(), "highDangerSavePctg": {}},
        returns=(dict,),
    ),
    "edge_team_landing": ManifestEntry(
        registry_key="edge_team_landing",
        target="edgework.clients.edge_client.EdgeClient.get_team_landing",
        web=True,
        call={"season": "20252026", "game_type": 2},
        endpoint_params={"season": 20252026, "game-type": 2},
        payload={"seasonsWithEdgeStats": _edge_seasons(), "shotAttemptsOver90": {}},
        returns=(dict,),
    ),
    # -- Base detail (percentiles vs league average) --------------------------
    "edge_skater_detail": ManifestEntry(
        registry_key="edge_skater_detail",
        target="edgework.clients.edge_client.EdgeClient.get_skater_detail",
        web=True,
        args=(8478402,),
        call={"season": "20252026", "game_type": 2},
        endpoint_params={"player-id": 8478402, "season": 20252026, "game-type": 2},
        payload={"player": {"playerId": 8478402}, "stats": {}},
        returns=(dict,),
    ),
    "edge_goalie_detail": ManifestEntry(
        registry_key="edge_goalie_detail",
        target="edgework.clients.edge_client.EdgeClient.get_goalie_detail",
        web=True,
        args=(8476979,),
        call={"season": "20252026", "game_type": 2},
        endpoint_params={"player-id": 8476979, "season": 20252026, "game-type": 2},
        payload={"player": {"playerId": 8476979}, "stats": {}},
        returns=(dict,),
    ),
    "edge_team_detail": ManifestEntry(
        registry_key="edge_team_detail",
        target="edgework.clients.edge_client.EdgeClient.get_team_detail",
        web=True,
        args=(14,),
        call={"season": "20252026", "game_type": 2},
        endpoint_params={"team-id": 14, "season": 20252026, "game-type": 2},
        payload={"team": {"teamId": 14}, "stats": {}},
        returns=(dict,),
    ),
    # -- Comparison payloads (one call per entity; diffed client-side) --------
    "edge_skater_comparison": ManifestEntry(
        registry_key="edge_skater_comparison",
        target="edgework.clients.edge_client.EdgeClient.get_skater_comparison",
        web=True,
        args=(8478402,),
        call={"season": "20252026", "game_type": 2},
        endpoint_params={"player-id": 8478402, "season": 20252026, "game-type": 2},
        payload={
            "shotSpeedDetails": [],
            "skatingSpeedDetails": [],
            "skatingDistanceDetails": [],
            "zoneTimeDetails": [],
            "shotLocationDetails": [],
        },
        returns=(dict,),
        also_implemented_by=("edgework.clients.edge_client.EdgeClient.compare",),
        note=(
            "compare('skater', ...) fans out to this route once per compared "
            "entity (goalie/team analogues below)."
        ),
    ),
    "edge_goalie_comparison": ManifestEntry(
        registry_key="edge_goalie_comparison",
        target="edgework.clients.edge_client.EdgeClient.get_goalie_comparison",
        web=True,
        args=(8476979,),
        call={"season": "20252026", "game_type": 2},
        endpoint_params={"player-id": 8476979, "season": 20252026, "game-type": 2},
        payload={
            "shotSpeedDetails": [],
            "skatingSpeedDetails": [],
            "zoneTimeDetails": [],
            "shotLocationDetails": [],
        },
        returns=(dict,),
        also_implemented_by=("edgework.clients.edge_client.EdgeClient.compare",),
    ),
    "edge_team_comparison": ManifestEntry(
        registry_key="edge_team_comparison",
        target="edgework.clients.edge_client.EdgeClient.get_team_comparison",
        web=True,
        args=(14,),
        call={"season": "20252026", "game_type": 2},
        endpoint_params={"team-id": 14, "season": 20252026, "game-type": 2},
        payload={
            "shotSpeedDetails": [],
            "skatingSpeedDetails": [],
            "skatingDistanceDetails": [],
            "zoneTimeDetails": [],
            "shotLocationDetails": [],
        },
        returns=(dict,),
        also_implemented_by=("edgework.clients.edge_client.EdgeClient.compare",),
    ),
    # -- View-specific detail (per-metric breakdowns) -------------------------
    "edge_skater_shot_speed_detail": ManifestEntry(
        registry_key="edge_skater_shot_speed_detail",
        target="edgework.clients.edge_client.EdgeClient.get_skater_shot_speed_detail",
        web=True,
        args=(8478402,),
        call={"season": "20252026", "game_type": 2},
        endpoint_params={"player-id": 8478402, "season": 20252026, "game-type": 2},
        payload={
            "topShotSpeed": _edge_measure(102.4, 165.0),
            "avgShotSpeed": _edge_measure(90.1, 145.0),
        },
        returns=(dict,),
    ),
    "edge_skater_skating_speed_detail": ManifestEntry(
        registry_key="edge_skater_skating_speed_detail",
        target=(
            "edgework.clients.edge_client."
            "EdgeClient.get_skater_skating_speed_detail"
        ),
        web=True,
        args=(8478402,),
        call={"season": "20252026", "game_type": 2},
        endpoint_params={"player-id": 8478402, "season": 20252026, "game-type": 2},
        payload={
            "maxSkatingSpeed": _edge_measure(24.05, 38.7),
            "burstsOver22": 2,
            "burstsOver20": 5,
            "burstsOver18": 9,
        },
        returns=(dict,),
    ),
    "edge_skater_skating_distance_detail": ManifestEntry(
        registry_key="edge_skater_skating_distance_detail",
        target=(
            "edgework.clients.edge_client."
            "EdgeClient.get_skater_skating_distance_detail"
        ),
        web=True,
        args=(8478402,),
        call={"season": "20252026", "game_type": 2},
        endpoint_params={"player-id": 8478402, "season": 20252026, "game-type": 2},
        payload={
            "totalDistanceSkated": _edge_measure(5.0, 8.0),
            "distanceMaxGame": _edge_measure(0.31, 0.5),
        },
        returns=(dict,),
    ),
    "edge_skater_shot_location_detail": ManifestEntry(
        registry_key="edge_skater_shot_location_detail",
        target=(
            "edgework.clients.edge_client."
            "EdgeClient.get_skater_shot_location_detail"
        ),
        web=True,
        args=(8478402,),
        call={"season": "20252026", "game_type": 2},
        endpoint_params={"player-id": 8478402, "season": 20252026, "game-type": 2},
        payload={"shotLocationDetails": [], "shotLocationTotals": []},
        returns=(dict,),
    ),
    "edge_goalie_shot_location_detail": ManifestEntry(
        registry_key="edge_goalie_shot_location_detail",
        target=(
            "edgework.clients.edge_client."
            "EdgeClient.get_goalie_shot_location_detail"
        ),
        web=True,
        args=(8476979,),
        call={"season": "20252026", "game_type": 2},
        endpoint_params={"player-id": 8476979, "season": 20252026, "game-type": 2},
        payload={
            "all": {"savePctg": 0.912},
            "highDanger": {"savePctg": 0.884},
            "midRange": {},
            "longRange": {},
        },
        returns=(dict,),
        note="Zone-keyed save percentages; data starts in 2025-26.",
    ),
    "edge_team_shot_speed_detail": ManifestEntry(
        registry_key="edge_team_shot_speed_detail",
        target="edgework.clients.edge_client.EdgeClient.get_team_shot_speed_detail",
        web=True,
        args=(14,),
        call={"season": "20252026", "game_type": 2},
        endpoint_params={"team-id": 14, "season": 20252026, "game-type": 2},
        payload={
            "topShotSpeed": _edge_measure(101.1, 162.7),
            "avgShotSpeed": _edge_measure(88.9, 143.1),
        },
        returns=(dict,),
    ),
    "edge_team_skating_speed_detail": ManifestEntry(
        registry_key="edge_team_skating_speed_detail",
        target=(
            "edgework.clients.edge_client."
            "EdgeClient.get_team_skating_speed_detail"
        ),
        web=True,
        args=(14,),
        call={"season": "20252026", "game_type": 2},
        endpoint_params={"team-id": 14, "season": 20252026, "game-type": 2},
        payload={
            "maxSkatingSpeed": _edge_measure(23.4, 37.7),
            "burstsOver22": 7,
            "burstsOver20": 18,
            "burstsOver18": 41,
        },
        returns=(dict,),
    ),
    "edge_team_skating_distance_detail": ManifestEntry(
        registry_key="edge_team_skating_distance_detail",
        target=(
            "edgework.clients.edge_client."
            "EdgeClient.get_team_skating_distance_detail"
        ),
        web=True,
        args=(14,),
        call={"season": "20252026", "game_type": 2},
        endpoint_params={"team-id": 14, "season": 20252026, "game-type": 2},
        payload={
            "totalDistanceSkated": _edge_measure(302.0, 486.0),
            "distancePer60": _edge_measure(22.5, 36.2),
        },
        returns=(dict,),
    ),
    "edge_team_shot_location_detail": ManifestEntry(
        registry_key="edge_team_shot_location_detail",
        target=(
            "edgework.clients.edge_client."
            "EdgeClient.get_team_shot_location_detail"
        ),
        web=True,
        args=(14,),
        call={"season": "20252026", "game_type": 2},
        endpoint_params={"team-id": 14, "season": 20252026, "game-type": 2},
        payload={"shotLocationDetails": [], "shotLocationTotals": []},
        returns=(dict,),
    ),
    "edge_team_zone_time_details": ManifestEntry(
        registry_key="edge_team_zone_time_details",
        target="edgework.clients.edge_client.EdgeClient.get_team_zone_time_details",
        web=True,
        args=(14,),
        call={"season": "20252026", "game_type": 2},
        endpoint_params={"team-id": 14, "season": 20252026, "game-type": 2},
        payload={
            "offensiveZoneTime": {},
            "neutralZoneTime": {},
            "defensiveZoneTime": {},
            "shotDifferential": {},
        },
        returns=(dict,),
        note="The only Edge route spelled with the plural -details suffix.",
    ),
    # -- Top-10 leaderboards (validated path parameters) ----------------------
    "edge_skater_shot_speed_top_10": ManifestEntry(
        registry_key="edge_skater_shot_speed_top_10",
        target="edgework.clients.edge_client.EdgeClient.get_skater_shot_speed_top_10",
        web=True,
        call={
            "situation": "all",
            "sort": "max",
            "season": "20252026",
            "game_type": 2,
        },
        endpoint_params={
            "situation": "all",
            "sort": "max",
            "season": 20252026,
            "game-type": 2,
        },
        payload=[{"playerId": 8478402, "topShotSpeed": _edge_measure(102.4, 165.0)}],
        returns=(list,),
    ),
    "edge_team_shot_speed_top_10": ManifestEntry(
        registry_key="edge_team_shot_speed_top_10",
        target="edgework.clients.edge_client.EdgeClient.get_team_shot_speed_top_10",
        web=True,
        call={
            "situation": "all",
            "sort": "max",
            "season": "20252026",
            "game_type": 2,
        },
        endpoint_params={
            "situation": "all",
            "sort": "max",
            "season": 20252026,
            "game-type": 2,
        },
        payload=[{"teamId": 14, "topShotSpeed": _edge_measure(101.1, 162.7)}],
        returns=(list,),
    ),
    "edge_team_skating_speed_top_10": ManifestEntry(
        registry_key="edge_team_skating_speed_top_10",
        target=(
            "edgework.clients.edge_client."
            "EdgeClient.get_team_skating_speed_top_10"
        ),
        web=True,
        call={
            "situation": "all",
            "sort": "max",
            "season": "20252026",
            "game_type": 2,
        },
        endpoint_params={
            "situation": "all",
            "sort": "max",
            "season": 20252026,
            "game-type": 2,
        },
        payload=[{"teamId": 14, "maxSkatingSpeed": _edge_measure(23.4, 37.7)}],
        returns=(list,),
    ),
    "edge_skater_shot_location_top_10": ManifestEntry(
        registry_key="edge_skater_shot_location_top_10",
        target=(
            "edgework.clients.edge_client."
            "EdgeClient.get_skater_shot_location_top_10"
        ),
        web=True,
        call={
            "situation": "all",
            "metric": "sog",
            "filter": "all",
            "season": "20252026",
            "game_type": 2,
        },
        endpoint_params={
            "situation": "all",
            "metric": "sog",
            "filter": "all",
            "season": 20252026,
            "game-type": 2,
        },
        payload=[{"playerId": 8478402, "sog": 120, "goals": 18}],
        returns=(list,),
    ),
    "edge_team_shot_location_top_10": ManifestEntry(
        registry_key="edge_team_shot_location_top_10",
        target=(
            "edgework.clients.edge_client."
            "EdgeClient.get_team_shot_location_top_10"
        ),
        web=True,
        call={
            "situation": "all",
            "metric": "sog",
            "filter": "all",
            "season": "20252026",
            "game_type": 2,
        },
        endpoint_params={
            "situation": "all",
            "metric": "sog",
            "filter": "all",
            "season": 20252026,
            "game-type": 2,
        },
        payload=[{"teamId": 14, "sog": 950, "goals": 88}],
        returns=(list,),
    ),
    "edge_team_skating_distance_top_10": ManifestEntry(
        registry_key="edge_team_skating_distance_top_10",
        target=(
            "edgework.clients.edge_client."
            "EdgeClient.get_team_skating_distance_top_10"
        ),
        web=True,
        call={
            "situation": "all",
            "param": "all",
            "sort": "total",
            "season": "20252026",
            "game_type": 2,
        },
        endpoint_params={
            "situation": "all",
            "param": "all",
            "sort": "total",
            "season": 20252026,
            "game-type": 2,
        },
        payload=[{"teamId": 14, "totalDistanceSkated": _edge_measure(302.0, 486.0)}],
        returns=(list,),
        note="Only all/all/total observed returning data for this route.",
    ),
    "edge_team_zone_time_top_10": ManifestEntry(
        registry_key="edge_team_zone_time_top_10",
        target="edgework.clients.edge_client.EdgeClient.get_team_zone_time_top_10",
        web=True,
        call={
            "situation": "all",
            "zone": "offensive",
            "season": "20252026",
            "game_type": 2,
        },
        endpoint_params={
            "situation": "all",
            "zone": "offensive",
            "season": 20252026,
            "game-type": 2,
        },
        payload=[{"teamId": 14, "offensiveZoneTime": 38.2}],
        returns=(list,),
    ),
    "edge_goalie_shot_location_top_10": ManifestEntry(
        registry_key="edge_goalie_shot_location_top_10",
        target=(
            "edgework.clients.edge_client."
            "EdgeClient.get_goalie_shot_location_top_10"
        ),
        web=True,
        call={
            "metric": "save-pctg",
            "situation": "all",
            "season": "20252026",
            "game_type": 2,
        },
        endpoint_params={
            "metric": "save-pctg",
            "situation": "all",
            "season": 20252026,
            "game-type": 2,
        },
        payload=[{"playerId": 8476979, "savePctg": 0.912}],
        returns=(list,),
        note=(
            "The only Edge top-10 with a differing param order: metric first. "
            "Data starts in 2025-26."
        ),
    ),
    # ---------------------------------------------------------------------------
    # Stats API (api.nhle.com/stats/rest) — canonical documented routes
    # ---------------------------------------------------------------------------
    "stats_players": ManifestEntry(
        registry_key="stats_players",
        target="edgework.clients.stats_client.StatsClient.get_players",
        web=False,
        call={"limit": 10, "start": 20},
        expected_params={"limit": 10, "start": 20},
        payload={"total": 0, "data": []},
        returns=(dict,),
        lang_kwarg=True,
    ),
    "stats_skater": ManifestEntry(
        registry_key="stats_skater",
        target="edgework.clients.stats_client.StatsClient.get_skaters",
        web=False,
        payload=[],
        returns=(list,),
        lang_kwarg=True,
        note="Skater listing; report-based stats live under stats_skater_report.",
    ),
    "stats_skater_report": ManifestEntry(
        registry_key="stats_skater_report",
        target="edgework.clients.stats_client.StatsClient.get_skaters_stats",
        web=False,
        call={"report": "summary", "season": 20232024},
        endpoint_params={"report": "summary"},
        expected_params={
            "isAggregate": False,
            "isGame": True,
            "limit": -1,
            "start": 0,
            "sort": "points",
            "cayenneExp": "seasonId=20232024",
        },
        payload={"data": [_report_row()]},
        returns=(list,),
        lang_kwarg=True,
        also_implemented_by=("edgework.models.stats.SkaterStats.fetch_data",),
    ),
    "stats_skater_leaders": ManifestEntry(
        registry_key="stats_skater_leaders",
        target="edgework.clients.stats_client.StatsClient.get_skater_leaders",
        web=False,
        call={"attribute": "points"},
        endpoint_params={"attribute": "points"},
        payload=[],
        returns=(list,),
        lang_kwarg=True,
        note="Stats API leaders listing; Web leaderboards are skater_stats_now etc.",
    ),
    "stats_skater_milestones": ManifestEntry(
        registry_key="stats_skater_milestones",
        target="edgework.clients.stats_client.StatsClient.get_skater_milestones",
        web=False,
        payload=[],
        returns=(list,),
        lang_kwarg=True,
    ),
    "stats_goalie_report": ManifestEntry(
        registry_key="stats_goalie_report",
        target="edgework.clients.stats_client.StatsClient.get_goalies_stats",
        web=False,
        call={"season": 20232024},
        endpoint_params={"report": "summary"},
        expected_params={
            "isAggregate": False,
            "isGame": True,
            "limit": -1,
            "start": 0,
            "sort": "wins",
            "cayenneExp": "seasonId=20232024",
        },
        payload={"data": [{"goalieId": 8476979, "wins": 30}]},
        returns=(list,),
        lang_kwarg=True,
        also_implemented_by=("edgework.models.stats.GoalieStats.fetch_data",),
    ),
    "stats_goalie_leaders": ManifestEntry(
        registry_key="stats_goalie_leaders",
        target="edgework.clients.stats_client.StatsClient.get_goalie_leaders",
        web=False,
        call={"attribute": "gaa"},
        endpoint_params={"attribute": "gaa"},
        payload=[],
        returns=(list,),
        lang_kwarg=True,
    ),
    "stats_goalie_milestones": ManifestEntry(
        registry_key="stats_goalie_milestones",
        target="edgework.clients.stats_client.StatsClient.get_goalie_milestones",
        web=False,
        payload=[],
        returns=(list,),
        lang_kwarg=True,
    ),
    "stats_team": ManifestEntry(
        registry_key="stats_team",
        target="edgework.clients.team_client.TeamClient.get_teams",
        web=False,
        expected_params=None,
        payload={"data": [_team_row()]},
        returns=(list,),
        note="TeamClient.get_teams requests the /{lang}/team collection route.",
    ),
    "stats_team_by_id": ManifestEntry(
        registry_key="stats_team_by_id",
        target="edgework.clients.team_client.TeamClient.get_team",
        web=False,
        args=(10,),
        endpoint_params={"team_id": 10},
        payload={"data": [_team_row()]},
        returns=(Team,),
        also_implemented_by=("edgework.models.team.Team.fetch_data",),
    ),
    "stats_team_report": ManifestEntry(
        registry_key="stats_team_report",
        target="edgework.clients.stats_client.StatsClient.get_team_stats",
        web=False,
        call={"season": 20232024},
        endpoint_params={"report": "summary"},
        expected_params={
            "isAggregate": False,
            "isGame": True,
            "limit": -1,
            "start": 0,
            "sort": "wins",
            "cayenneExp": "seasonId=20232024",
        },
        payload={"data": [{"teamId": 10, "wins": 40}]},
        returns=(list,),
        lang_kwarg=True,
        also_implemented_by=("edgework.models.stats.TeamStats.fetch_data",),
    ),
    "stats_franchise": ManifestEntry(
        registry_key="stats_franchise",
        target="edgework.clients.stats_client.StatsClient.get_franchises",
        web=False,
        payload=[],
        returns=(list,),
        lang_kwarg=True,
    ),
    "stats_draft": ManifestEntry(
        registry_key="stats_draft",
        target="edgework.clients.stats_client.StatsClient.get_draft",
        web=False,
        payload=[],
        returns=(list,),
        lang_kwarg=True,
        note="Stats API draft listing; Web draft routes live in DraftClient.",
    ),
    "stats_component_season": ManifestEntry(
        registry_key="stats_component_season",
        target="edgework.clients.stats_client.StatsClient.get_component_seasons",
        web=False,
        payload=[],
        returns=(list,),
        lang_kwarg=True,
    ),
    "stats_season": ManifestEntry(
        registry_key="stats_season",
        target="edgework.clients.stats_client.StatsClient.get_seasons",
        web=False,
        payload=[],
        returns=(list,),
        lang_kwarg=True,
        note="Distinct from the Web API /v1/season route (UtilityClient.get_season).",
    ),
    "stats_game": ManifestEntry(
        registry_key="stats_game",
        target="edgework.clients.stats_client.StatsClient.get_games",
        web=False,
        payload=[],
        returns=(list,),
        lang_kwarg=True,
    ),
    "stats_game_meta": ManifestEntry(
        registry_key="stats_game_meta",
        target="edgework.clients.stats_client.StatsClient.get_game_meta",
        web=False,
        payload=[],
        returns=(list,),
        lang_kwarg=True,
    ),
    "stats_config": ManifestEntry(
        registry_key="stats_config",
        target="edgework.clients.stats_client.StatsClient.get_config",
        web=False,
        payload={"rosters": {"current": {}}},
        returns=(dict,),
        lang_kwarg=True,
        also_implemented_by=("edgework.models.config.Config.fetch_data",),
        note="Config.fetch_data delegates to StatsClient.get_config (Task 5).",
    ),
    "stats_ping": ManifestEntry(
        registry_key="stats_ping",
        target="edgework.clients.stats_client.StatsClient.ping",
        web=False,
        payload={"pong": True},
        returns=(dict,),
        lang=None,
        note="Root route — the only Stats API route without a language prefix.",
    ),
    "stats_country": ManifestEntry(
        registry_key="stats_country",
        target="edgework.clients.stats_client.StatsClient.get_countries",
        web=False,
        payload=[],
        returns=(list,),
        lang_kwarg=True,
    ),
    "stats_shiftcharts": ManifestEntry(
        registry_key="stats_shiftcharts",
        target="edgework.clients.shift_client.ShiftClient.get_shiftcharts",
        web=False,
        call={"game_id": 2021020001},
        expected_params={"cayenneExp": "gameId=2021020001"},
        payload={"data": [{"gameId": 2021020001, "shiftNumber": 1}]},
        returns=(list,),
        lang_kwarg=True,
        also_implemented_by=(
            "edgework.clients.shift_client.ShiftClient.get_shifts",
            "edgework.clients.game_client.GameClient.get_shifts",
            "edgework.models.game.Game._get_shifts",
        ),
        note="ShiftClient is the canonical wrapper; game-level access delegates.",
    ),
    "stats_glossary": ManifestEntry(
        registry_key="stats_glossary",
        target="edgework.clients.glossary_client.GlossaryClient.get_glossary",
        web=False,
        payload={"data": [{"id": 1, "term": "Zamboni", "definition": "Ice resurfacer."}]},
        returns=(Glossary,),
        lang_kwarg=True,
    ),
    "stats_content_module": ManifestEntry(
        registry_key="stats_content_module",
        target="edgework.clients.stats_client.StatsClient.get_content_module",
        web=False,
        call={"template_key": "overview"},
        endpoint_params={"template_key": "overview"},
        payload=[],
        returns=(list,),
        lang_kwarg=True,
    ),
}

# Registry keys intentionally absent from the manifest. Each entry maps the
# key to the reason it is not a unique canonical server route.
REGISTRY_EXCLUSIONS: dict[str, str] = {
    "club_stats_season_season_game_type": (
        "Legacy alias of 'club_stats_season_game_type' (identical server "
        "route), kept for backward compatibility with pre-Task-1 callers."
    ),
    # NHL Edge (Tasks E1–E3): all 27 canonical /v1/edge/... routes are
    # manifested in ENDPOINT_MANIFEST above (see the NHL Edge block). The
    # composite EdgeClient helpers (compare, get_available_seasons,
    # get_goal_frames) are methods, not registry routes, so they are simply
    # not manifested — their canonical routes carry the entries.
}
