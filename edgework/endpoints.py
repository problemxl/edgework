"""Registry of NHL API endpoint routes.

The NHL exposes two primary APIs (see ``NHL API Documentation.md``):

- **Web API** (``https://api-web.nhle.com``): language-independent routes
  versioned under ``/v1`` (except the OpenAPI specification, which lives at
  ``/model/v1/openapi.json``).
- **Stats API** (``https://api.nhle.com/stats/rest``): routes prefixed with a
  language code (e.g. ``/en/``, ``/fr/``), except a few root routes such as
  ``/ping``.

Route templates use braces for path parameters (e.g. ``{player_id}``) and
``{API_VERSION}`` for the Web API version segment. Stats API routes use the
``{lang}`` placeholder for the language segment.

Keys are domain-oriented. Stats API keys are prefixed with ``stats_`` to make
the Web vs. Stats distinction explicit. Legacy key names are preserved as
aliases where existing callers may depend on them.
"""

from .const import API_VERSION

# ---------------------------------------------------------------------------
# Web API (api-web.nhle.com) — routes are served under /{API_VERSION}
# ---------------------------------------------------------------------------
API_PATH: dict = {
    # Player endpoints
    "player_game_logs": "/{API_VERSION}/player/{player_id}/game-log/{season}/{game-type}",
    "player_game_log_now": "/{API_VERSION}/player/{player_id}/game-log/now",
    "player_landing": "/{API_VERSION}/player/{player_id}/landing",
    "player_spotlight": "/{API_VERSION}/player-spotlight",
    # Skater/goalie stats-leader endpoints (Web API leaderboards)
    "skater_stats_now": "/{API_VERSION}/skater-stats-leaders/current",
    "skater_stats_season_game_type": "/{API_VERSION}/skater-stats-leaders/{season}/{game-type}",
    "goalie_stats_now": "/{API_VERSION}/goalie-stats-leaders/current",
    "goalie_stats_season_game_type": "/{API_VERSION}/goalie-stats-leaders/{season}/{game-type}",
    # Standings endpoints
    "standings": "/{API_VERSION}/standings/now",
    "standings_date": "/{API_VERSION}/standings/{date}",
    "standings_season": "/{API_VERSION}/standings-season",
    # Club stats endpoints
    "club_stats": "/{API_VERSION}/club-stats/{team}/now",
    "club_stats_season": "/{API_VERSION}/club-stats-season/{team}",
    # Documented route: /v1/club-stats/{team}/{season}/{game-type}
    "club_stats_season_game_type": "/{API_VERSION}/club-stats/{team}/{season}/{game-type}",
    "team_scoreboard": "/{API_VERSION}/scoreboard/{team}/now",
    # Roster endpoints
    "roster_current": "/{API_VERSION}/roster/{team}/current",
    "roster_season": "/{API_VERSION}/roster/{team}/{season}",
    "roster_season_team": "/{API_VERSION}/roster-season/{team}",
    "team_prospects": "/{API_VERSION}/prospects/{team}",
    # Schedule endpoints
    "club_schedule_season_now": "/{API_VERSION}/club-schedule-season/{team}/now",
    "club_schedule_season": "/{API_VERSION}/club-schedule-season/{team}/{season}",
    "club_schedule_month_now": "/{API_VERSION}/club-schedule/{team}/month/now",
    "club_schedule_month": "/{API_VERSION}/club-schedule/{team}/month/{month}",
    "club_schedule_week": "/{API_VERSION}/club-schedule/{team}/week/{date}",
    "club_schedule_week_now": "/{API_VERSION}/club-schedule/{team}/week/now",
    "schedule_now": "/{API_VERSION}/schedule/now",
    "schedule_date": "/{API_VERSION}/schedule/{date}",
    "schedule_calendar_now": "/{API_VERSION}/schedule-calendar/now",
    "schedule_calendar_date": "/{API_VERSION}/schedule-calendar/{date}",
    # Game endpoints
    "score_now": "/{API_VERSION}/score/now",
    "score_date": "/{API_VERSION}/score/{date}",
    "scoreboard_now": "/{API_VERSION}/scoreboard/now",
    "where_to_watch": "/{API_VERSION}/where-to-watch",
    "play_by_play": "/{API_VERSION}/gamecenter/{game_id}/play-by-play",
    "game_landing": "/{API_VERSION}/gamecenter/{game_id}/landing",
    "game_boxscore": "/{API_VERSION}/gamecenter/{game_id}/boxscore",
    "game_story": "/{API_VERSION}/wsc/game-story/{game_id}",
    "game_right_rail": "/{API_VERSION}/gamecenter/{game_id}/right-rail",
    "wsc_play_by_play": "/{API_VERSION}/wsc/play-by-play/{game_id}",
    # Network endpoints
    "tv_schedule_date": "/{API_VERSION}/network/tv-schedule/{date}",
    "tv_schedule_now": "/{API_VERSION}/network/tv-schedule/now",
    # Odds endpoints
    "partner_game": "/{API_VERSION}/partner-game/{country_code}/now",
    # Playoff endpoints
    "playoff_series_carousel": "/{API_VERSION}/playoff-series/carousel/{season}/",
    "playoff_series_schedule": "/{API_VERSION}/schedule/playoff-series/{season}/{series_letter}/",
    "playoff_bracket": "/{API_VERSION}/playoff-bracket/{year}",
    # Season endpoints
    "season": "/{API_VERSION}/season",
    # Draft endpoints
    "draft_rankings_now": "/{API_VERSION}/draft/rankings/now",
    "draft_rankings": "/{API_VERSION}/draft/rankings/{season}/{prospect_category}",
    "draft_tracker_picks_now": "/{API_VERSION}/draft-tracker/picks/now",
    "draft_picks_now": "/{API_VERSION}/draft/picks/now",
    "draft_picks": "/{API_VERSION}/draft/picks/{season}/{round}",
    # Miscellaneous endpoints
    "meta": "/{API_VERSION}/meta",
    "meta_game": "/{API_VERSION}/meta/game/{game_id}",
    "location": "/{API_VERSION}/location",
    "meta_playoff_series": "/{API_VERSION}/meta/playoff-series/{year}/{series_letter}",
    "postal_lookup": "/{API_VERSION}/postal-lookup/{postal_code}",
    "goal_replay": "/{API_VERSION}/ppt-replay/goal/{game_id}/{event_number}",
    "play_replay": "/{API_VERSION}/ppt-replay/{game_id}/{event_number}",
    # OpenAPI specification — served outside the /{API_VERSION} namespace
    "openapi_spec": "/model/{API_VERSION}/openapi.json",
    # ---------------------------------------------------------------------------
    # Stats API (api.nhle.com/stats/rest) — routes are prefixed with a language
    # code ({lang}), except root routes such as /ping.
    # ---------------------------------------------------------------------------
    # Player endpoints
    "stats_players": "/{lang}/players",
    "stats_skater": "/{lang}/skater",
    "stats_skater_report": "/{lang}/skater/{report}",
    "stats_skater_leaders": "/{lang}/leaders/skaters/{attribute}",
    "stats_skater_milestones": "/{lang}/milestones/skaters",
    "stats_goalie_report": "/{lang}/goalie/{report}",
    "stats_goalie_leaders": "/{lang}/leaders/goalies/{attribute}",
    "stats_goalie_milestones": "/{lang}/milestones/goalies",
    # Team/franchise endpoints
    "stats_team": "/{lang}/team",
    "stats_team_by_id": "/{lang}/team/id/{team_id}",
    "stats_team_report": "/{lang}/team/{report}",
    "stats_franchise": "/{lang}/franchise",
    # Draft endpoints
    "stats_draft": "/{lang}/draft",
    # Season endpoints
    "stats_component_season": "/{lang}/componentSeason",
    "stats_season": "/{lang}/season",
    # Game endpoints
    "stats_game": "/{lang}/game",
    "stats_game_meta": "/{lang}/game/meta",
    # Configuration/utility endpoints
    "stats_config": "/{lang}/config",
    "stats_ping": "/ping",
    "stats_country": "/{lang}/country",
    "stats_shiftcharts": "/{lang}/shiftcharts",
    "stats_glossary": "/{lang}/glossary",
    "stats_content_module": "/{lang}/content/module/{template_key}",
}

# Legacy alias keys kept for backward compatibility. These were superseded by
# corrected canonical routes above but may still be referenced by callers.
API_PATH["club_stats_season_season_game_type"] = API_PATH[
    "club_stats_season_game_type"
]


def get_endpoint(key: str) -> str:
    """
    Return the route template registered under ``key``.

    Args:
        key: Endpoint registry key (e.g. ``"player_landing"``).

    Returns:
        The route template string.

    Raises:
        KeyError: If the key is not present in the registry.
    """
    return API_PATH[key]


def format_endpoint(key: str, api_version: str = API_VERSION, **params) -> str:
    """
    Return a fully substituted route for ``key``.

    Path parameters are filled from keyword arguments; the ``{API_VERSION}``
    placeholder is filled from ``api_version``. The ``{lang}`` placeholder,
    when present, must be supplied via ``lang=...``.

    Args:
        key: Endpoint registry key (e.g. ``"club_stats_season_game_type"``).
        api_version: Web API version segment (defaults to ``API_VERSION``).
        **params: Path parameters to substitute (e.g. ``team="TOR"``).

    Returns:
        The route with all placeholders substituted.

    Raises:
        KeyError: If the key is unknown or a placeholder has no value.
    """
    route = get_endpoint(key)
    values = {"API_VERSION": api_version, **params}
    return route.format(**values)
