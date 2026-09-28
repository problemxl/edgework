# NHL API Documentation

Information about the NHL APIs that Edgework interacts with.

!!! warning "Unofficial APIs"
    The NHL does not publish an official, supported public API. Both APIs
    described below are **unofficial**: they are reverse-engineered from the
    NHL's own web properties, may change without notice, and may rate-limit
    or block clients. Edgework's coverage of them is verified against the
    local reference documentation as described in
    [How endpoint availability is verified](#how-endpoint-availability-is-verified).

## Overview

Edgework provides a Python interface to the two NHL APIs, making it easy to
access NHL data including:

- Player information and statistics
- Team information and rosters
- Game schedules and results
- League standings
- Historical data
- NHL Edge tracking statistics (shot speed, skating speed/distance, zone
  time, shot/save locations, Goal Visualizer replays — 2024-25 onward)

## The two APIs

| | Web API | Stats API |
|---|---|---|
| Base URL | `https://api-web.nhle.com` | `https://api.nhle.com/stats/rest/` |
| Versioning | Routes served under `/v1` | Not versioned |
| Language | Language-independent | Routes prefixed with a language code (`/en/`, `/fr/`, ...), except root routes such as `/ping` |
| Route ownership | Routes are owned by the specific *client that documents them* | Report names validated against `edgework.stats_reports` |

Edgework's route registry (`edgework/endpoints.py`) keys every documented
route with a domain-oriented name; Stats API keys are prefixed with `stats_`
to make the host distinction explicit.

## Coverage matrix — Web API

Every documented Web API route and the Edgework method that implements it.
Route templates use `{...}` for path parameters; in the code below each is
filled with a sample value by the coverage tests (dates, seasons, team
abbreviations, game/event IDs).

| Documented route | Registry key | Implemented by |
|---|---|---|
| `/v1/player/{player_id}/game-log/{season}/{game-type}` | `player_game_logs` | `PlayerClient.get_player_game_logs` |
| `/v1/player/{player_id}/game-log/now` | `player_game_log_now` | `PlayerClient.get_player_game_log_now` |
| `/v1/player/{player_id}/landing` | `player_landing` | `PlayerClient.get_player_landing` |
| `/v1/player-spotlight` | `player_spotlight` | `PlayerClient.get_player_spotlight` |
| `/v1/skater-stats-leaders/current` | `skater_stats_now` | `StatsClient.get_skater_stats_leaders` |
| `/v1/skater-stats-leaders/{season}/{game-type}` | `skater_stats_season_game_type` | `StatsClient.get_skater_stats_leaders_by_season` |
| `/v1/goalie-stats-leaders/current` | `goalie_stats_now` | `StatsClient.get_goalie_stats_leaders` |
| `/v1/goalie-stats-leaders/{season}/{game-type}` | `goalie_stats_season_game_type` | `StatsClient.get_goalie_stats_leaders_by_season` |
| `/v1/standings/now` | `standings` | `StandingClient.get_standings` |
| `/v1/standings/{date}` | `standings_date` | `StandingClient.get_standings` |
| `/v1/standings-season` | `standings_season` | `StandingClient.get_standings_for_season` |
| `/v1/club-stats/{team}/now` | `club_stats` | `TeamClient.get_team_stats` |
| `/v1/club-stats-season/{team}` | `club_stats_season` | `TeamClient.get_club_stats_season` |
| `/v1/club-stats/{team}/{season}/{game-type}` | `club_stats_season_game_type` | `TeamClient.get_team_stats` |
| `/v1/scoreboard/{team}/now` | `team_scoreboard` | `TeamClient.get_scoreboard` |
| `/v1/roster/{team}/current` | `roster_current` | `TeamClient.get_roster` |
| `/v1/roster/{team}/{season}` | `roster_season` | `TeamClient.get_roster` |
| `/v1/roster-season/{team}` | `roster_season_team` | `TeamClient.get_roster_season` |
| `/v1/prospects/{team}` | `team_prospects` | `TeamClient.get_team_prospects` |
| `/v1/club-schedule-season/{team}/now` | `club_schedule_season_now` | `ScheduleClient.get_schedule_for_team` |
| `/v1/club-schedule-season/{team}/{season}` | `club_schedule_season` | `TeamClient.get_team_schedule` |
| `/v1/club-schedule/{team}/month/now` | `club_schedule_month_now` | `ScheduleClient.get_schedule_for_team_for_month` |
| `/v1/club-schedule/{team}/month/{month}` | `club_schedule_month` | `ScheduleClient.get_schedule_for_team_for_month` |
| `/v1/club-schedule/{team}/week/{date}` | `club_schedule_week` | `ScheduleClient.get_schedule_for_team_for_week` |
| `/v1/club-schedule/{team}/week/now` | `club_schedule_week_now` | `ScheduleClient.get_schedule_for_team_for_week` |
| `/v1/schedule/now` | `schedule_now` | `ScheduleClient.get_schedule` |
| `/v1/schedule/{date}` | `schedule_date` | `ScheduleClient.get_schedule_for_date` |
| `/v1/schedule-calendar/now` | `schedule_calendar_now` | `ScheduleClient.get_schedule_calendar` |
| `/v1/schedule-calendar/{date}` | `schedule_calendar_date` | `ScheduleClient.get_schedule_calendar_for_date` |
| `/v1/score/now` | `score_now` | `GameClient.get_score` |
| `/v1/score/{date}` | `score_date` | `GameClient.get_score` |
| `/v1/scoreboard/now` | `scoreboard_now` | `GameClient.get_scoreboard` |
| `/v1/where-to-watch` | `where_to_watch` | `NetworkClient.get_where_to_watch` |
| `/v1/gamecenter/{game_id}/play-by-play` | `play_by_play` | `GameClient.get_play_by_play` |
| `/v1/gamecenter/{game_id}/landing` | `game_landing` | `GameClient.get_game_landing` |
| `/v1/gamecenter/{game_id}/boxscore` | `game_boxscore` | `GameClient.get_game_boxscore` |
| `/v1/wsc/game-story/{game_id}` | `game_story` | `GameClient.get_game_story` |
| `/v1/gamecenter/{game_id}/right-rail` | `game_right_rail` | `GameClient.get_game_right_rail` |
| `/v1/wsc/play-by-play/{game_id}` | `wsc_play_by_play` | `GameClient.get_wsc_play_by_play` |
| `/v1/network/tv-schedule/{date}` | `tv_schedule_date` | `NetworkClient.get_tv_schedule` |
| `/v1/network/tv-schedule/now` | `tv_schedule_now` | `NetworkClient.get_tv_schedule_now` |
| `/v1/partner-game/{country_code}/now` | `partner_game` | `NetworkClient.get_partner_game_odds` |
| `/v1/playoff-series/carousel/{season}/` | `playoff_series_carousel` | `PlayoffClient.get_playoff_series_carousel` |
| `/v1/schedule/playoff-series/{season}/{series_letter}/` | `playoff_series_schedule` | `PlayoffClient.get_playoff_series_schedule` |
| `/v1/playoff-bracket/{year}` | `playoff_bracket` | `PlayoffClient.get_playoff_bracket` |
| `/v1/season` | `season` | `UtilityClient.get_season` |
| `/v1/draft/rankings/now` | `draft_rankings_now` | `DraftClient.get_draft_rankings` |
| `/v1/draft/rankings/{season}/{prospect_category}` | `draft_rankings` | `DraftClient.get_draft_rankings` |
| `/v1/draft-tracker/picks/now` | `draft_tracker_picks_now` | `DraftClient.get_draft_tracker_picks` |
| `/v1/draft/picks/now` | `draft_picks_now` | `DraftClient.get_draft_picks` |
| `/v1/draft/picks/{season}/{round}` | `draft_picks` | `DraftClient.get_draft_picks` |
| `/v1/meta` | `meta` | `UtilityClient.get_meta` |
| `/v1/meta/game/{game_id}` | `meta_game` | `UtilityClient.get_meta_game` |
| `/v1/location` | `location` | `UtilityClient.get_location` |
| `/v1/meta/playoff-series/{year}/{series_letter}` | `meta_playoff_series` | `UtilityClient.get_meta_playoff_series` |
| `/v1/postal-lookup/{postal_code}` | `postal_lookup` | `UtilityClient.get_postal_lookup` |
| `/v1/ppt-replay/goal/{game_id}/{event_number}` | `goal_replay` | `GameClient.get_goal_replay` |
| `/v1/ppt-replay/{game_id}/{event_number}` | `play_replay` | `GameClient.get_play_replay` |
| `/model/v1/openapi.json` | `openapi_spec` | `UtilityClient.get_openapi_spec` |

## Coverage matrix — Stats API

`{lang}` is the language code (`en`, `fr`, ...). Report routes
(`/{lang}/skater/{report}`, `/{lang}/goalie/{report}`, `/{lang}/team/{report}`)
accept the report names listed in `edgework/stats_reports.py`, which is the
single source of truth shared by the client and the stats models.

| Documented route | Registry key | Implemented by |
|---|---|---|
| `/{lang}/players` | `stats_players` | `StatsClient.get_players` |
| `/{lang}/skater` | `stats_skater` | `StatsClient.get_skaters` |
| `/{lang}/skater/{report}` | `stats_skater_report` | `StatsClient.get_skaters_stats` |
| `/{lang}/leaders/skaters/{attribute}` | `stats_skater_leaders` | `StatsClient.get_skater_leaders` |
| `/{lang}/milestones/skaters` | `stats_skater_milestones` | `StatsClient.get_skater_milestones` |
| `/{lang}/goalie/{report}` | `stats_goalie_report` | `StatsClient.get_goalies_stats` |
| `/{lang}/leaders/goalies/{attribute}` | `stats_goalie_leaders` | `StatsClient.get_goalie_leaders` |
| `/{lang}/milestones/goalies` | `stats_goalie_milestones` | `StatsClient.get_goalie_milestones` |
| `/{lang}/team` | `stats_team` | `TeamClient.get_teams` |
| `/{lang}/team/id/{team_id}` | `stats_team_by_id` | `TeamClient.get_team` |
| `/{lang}/team/{report}` | `stats_team_report` | `StatsClient.get_team_stats` |
| `/{lang}/franchise` | `stats_franchise` | `StatsClient.get_franchises` |
| `/{lang}/draft` | `stats_draft` | `StatsClient.get_draft` |
| `/{lang}/componentSeason` | `stats_component_season` | `StatsClient.get_component_seasons` |
| `/{lang}/season` | `stats_season` | `StatsClient.get_seasons` |
| `/{lang}/game` | `stats_game` | `StatsClient.get_games` |
| `/{lang}/game/meta` | `stats_game_meta` | `StatsClient.get_game_meta` |
| `/{lang}/config` | `stats_config` | `StatsClient.get_config` |
| `/ping` | `stats_ping` | `StatsClient.ping` |
| `/{lang}/country` | `stats_country` | `StatsClient.get_countries` |
| `/{lang}/shiftcharts` | `stats_shiftcharts` | `ShiftClient.get_shiftcharts` |
| `/{lang}/glossary` | `stats_glossary` | `GlossaryClient.get_glossary` |
| `/{lang}/content/module/{template_key}` | `stats_content_module` | `StatsClient.get_content_module` |

## Coverage matrix — NHL Edge (Web API host)

The NHL Edge routes (puck- and player-tracking statistics) are also served
by the Web API, under `/v1/edge/...`. They are documented separately because
they are **reverse-engineered from the NHL Edge web app** — the full
endpoint catalog, response schemas and quirks live in the research notes,
[`docs/research/nhl-edge-endpoints.md`](../research/nhl-edge-endpoints.md),
which is the provenance for everything below.

Composite helpers are excluded from this matrix per the manifest rules —
their canonical routes are already listed:

- `EdgeClient.compare(entity, id_a, id_b, ...)` fans out to the three
  `*-comparison` routes, once per compared entity.
- `EdgeClient.get_available_seasons()` reads `seasonsWithEdgeStats` off the
  `edge_skater_landing` route.
- `EdgeClient.get_goal_frames(game_id, event_id)` chains the already-listed
  `/v1/ppt-replay/{game_id}/{event_number}` route to the
  `pptReplayUrl` on the sprites host.

| Documented route | Registry key | Implemented by |
|---|---|---|
| `/v1/edge/skater-landing/{season}/{game-type}` | `edge_skater_landing` | `EdgeClient.get_skater_landing` |
| `/v1/edge/goalie-landing/{season}/{game-type}` | `edge_goalie_landing` | `EdgeClient.get_goalie_landing` |
| `/v1/edge/team-landing/{season}/{game-type}` | `edge_team_landing` | `EdgeClient.get_team_landing` |
| `/v1/edge/skater-detail/{player-id}/{season}/{game-type}` | `edge_skater_detail` | `EdgeClient.get_skater_detail` |
| `/v1/edge/goalie-detail/{player-id}/{season}/{game-type}` | `edge_goalie_detail` | `EdgeClient.get_goalie_detail` |
| `/v1/edge/team-detail/{team-id}/{season}/{game-type}` | `edge_team_detail` | `EdgeClient.get_team_detail` |
| `/v1/edge/skater-comparison/{player-id}/{season}/{game-type}` | `edge_skater_comparison` | `EdgeClient.get_skater_comparison` |
| `/v1/edge/goalie-comparison/{player-id}/{season}/{game-type}` | `edge_goalie_comparison` | `EdgeClient.get_goalie_comparison` |
| `/v1/edge/team-comparison/{team-id}/{season}/{game-type}` | `edge_team_comparison` | `EdgeClient.get_team_comparison` |
| `/v1/edge/skater-shot-speed-detail/{player-id}/{season}/{game-type}` | `edge_skater_shot_speed_detail` | `EdgeClient.get_skater_shot_speed_detail` |
| `/v1/edge/skater-skating-speed-detail/{player-id}/{season}/{game-type}` | `edge_skater_skating_speed_detail` | `EdgeClient.get_skater_skating_speed_detail` |
| `/v1/edge/skater-skating-distance-detail/{player-id}/{season}/{game-type}` | `edge_skater_skating_distance_detail` | `EdgeClient.get_skater_skating_distance_detail` |
| `/v1/edge/skater-shot-location-detail/{player-id}/{season}/{game-type}` | `edge_skater_shot_location_detail` | `EdgeClient.get_skater_shot_location_detail` |
| `/v1/edge/goalie-shot-location-detail/{player-id}/{season}/{game-type}` | `edge_goalie_shot_location_detail` | `EdgeClient.get_goalie_shot_location_detail` |
| `/v1/edge/team-shot-speed-detail/{team-id}/{season}/{game-type}` | `edge_team_shot_speed_detail` | `EdgeClient.get_team_shot_speed_detail` |
| `/v1/edge/team-skating-speed-detail/{team-id}/{season}/{game-type}` | `edge_team_skating_speed_detail` | `EdgeClient.get_team_skating_speed_detail` |
| `/v1/edge/team-skating-distance-detail/{team-id}/{season}/{game-type}` | `edge_team_skating_distance_detail` | `EdgeClient.get_team_skating_distance_detail` |
| `/v1/edge/team-shot-location-detail/{team-id}/{season}/{game-type}` | `edge_team_shot_location_detail` | `EdgeClient.get_team_shot_location_detail` |
| `/v1/edge/team-zone-time-details/{team-id}/{season}/{game-type}` | `edge_team_zone_time_details` | `EdgeClient.get_team_zone_time_details` |
| `/v1/edge/skater-shot-speed-top-10/{situation}/{sort}/{season}/{game-type}` | `edge_skater_shot_speed_top_10` | `EdgeClient.get_skater_shot_speed_top_10` |
| `/v1/edge/team-shot-speed-top-10/{situation}/{sort}/{season}/{game-type}` | `edge_team_shot_speed_top_10` | `EdgeClient.get_team_shot_speed_top_10` |
| `/v1/edge/team-skating-speed-top-10/{situation}/{sort}/{season}/{game-type}` | `edge_team_skating_speed_top_10` | `EdgeClient.get_team_skating_speed_top_10` |
| `/v1/edge/skater-shot-location-top-10/{situation}/{metric}/{filter}/{season}/{game-type}` | `edge_skater_shot_location_top_10` | `EdgeClient.get_skater_shot_location_top_10` |
| `/v1/edge/team-shot-location-top-10/{situation}/{metric}/{filter}/{season}/{game-type}` | `edge_team_shot_location_top_10` | `EdgeClient.get_team_shot_location_top_10` |
| `/v1/edge/team-skating-distance-top-10/{situation}/{param}/{sort}/{season}/{game-type}` | `edge_team_skating_distance_top_10` | `EdgeClient.get_team_skating_distance_top_10` |
| `/v1/edge/team-zone-time-top-10/{situation}/{zone}/{season}/{game-type}` | `edge_team_zone_time_top_10` | `EdgeClient.get_team_zone_time_top_10` |
| `/v1/edge/goalie-shot-location-top-10/{metric}/{situation}/{season}/{game-type}` | `edge_goalie_shot_location_top_10` | `EdgeClient.get_goalie_shot_location_top_10` |

Edge data-availability caveats:

- Tracking data exists only from **2024-25** onward, and the goalie
  shot-location family (detail + top-10) only from **2025-26**. Discover
  valid seasons via `EdgeClient.get_available_seasons()`
  (`seasonsWithEdgeStats`) instead of hard-coding a season list.
- **Empty is legitimate**: a valid route with no data returns `[]` with HTTP
  200, never a 404 — clients pass empty arrays through as-is.
- `season="now"` (the method default) replaces the whole
  `{season}/{game-type}` tail: the API 307-redirects `/now` to the resolved
  current season and `httpx` follows redirects. The coverage tests exercise
  the explicit-season form because the registry template cannot express the
  `now` collapse.
- The Goal Visualizer sprites host (`wsr.nhle.com`) requires
  `Referer: https://www.nhl.com/` — a user agent alone is answered with 403.

## How endpoint availability is verified

Because the APIs are unofficial, Edgework enforces a *coverage contract* in
its unit tests instead of relying on runtime discovery:

1. **Registry completeness** — `edgework/endpoints.py` contains a route
   template for every route documented in the local reference
   (`edgework/NHL API Documentation.md`).
2. **Endpoint manifest** — `tests/endpoint_manifest.py` maps every canonical
   documented route (unique server routes only) to the client method that
   implements it. Composite helpers and duplicate model accessors are excluded;
   the latter are listed as `also_implemented_by` so their existence is still
   verified.
3. **Route contract tests** — `tests/test_endpoint_coverage.py` invokes every
   manifest entry against a mocked HTTP layer and asserts, per route:
   - the full request URL equals the URL derived from the registry template
     (host, `/v1` or language prefix, path-parameter substitution),
   - query parameters travel in `params` (never embedded in the route string),
   - Web-vs-Stats requests target the documented host,
   - the documented return type is produced,
   - language-capable methods render alternate-language URLs correctly.
4. **Live OpenAPI comparison (opt-in, non-blocking)** — running
   `EDGEWORK_OPENAPI_LIVE=1 pytest tests/test_endpoint_coverage.py` additionally
   fetches the live `/model/v1/openapi.json` document and compares it against
   the manifest. Differences are reported as warnings, never failures: the
   live document is unofficial and may change at any time.

If the manifest finds a route that is documented but unimplemented, the
completeness test fails — so coverage regressions cannot land silently.

## Data Formats

### Season Format
All season parameters should be provided in the format `"YYYY-YYYY"`, for example:
- `"2023-2024"` for the 2023-2024 season
- `"2022-2023"` for the 2022-2023 season

Invalid formats raise `ValueError` before any request is made. (The draft
routes are the exception on the wire: the documented draft endpoints take a
4-digit draft year, which Edgework derives from the season's start year.)

### Game Types
- `2` - Regular season games
- `3` - Playoff games

### Player Positions
- `C` - Center
- `LW` - Left Wing
- `RW` - Right Wing
- `D` - Defenseman
- `G` - Goaltender

## Rate Limiting and Best Practices

### API Usage Guidelines
- Be respectful of the NHL's servers
- Implement caching where appropriate
- Use appropriate delays between requests
- Handle errors gracefully

### Error Handling
Common errors you might encounter:
- Network timeouts
- Invalid season formats
- API rate limiting
- Data not available for requested parameters

## Data Availability

### Current Season Data
- Live game data
- Up-to-date player statistics
- Current team standings

### Historical Data
- Previous season statistics
- Historical player data
- Archive game results

Note: Data availability may vary depending on the specific endpoint and time of year.

## Attribution

When using NHL data in your applications, please:
- Acknowledge that the data comes from the NHL
- Follow NHL's terms of service
- Respect intellectual property rights

## Technical Notes

### Response Formats
- All API responses are in JSON format
- Timestamps are typically in UTC
- Numeric values are returned as appropriate types (int, float)

### Data Consistency
- Player IDs are consistent across endpoints
- Team abbreviations are standardized
- Season formats are consistent

For more detailed information about specific data structures, see the API Reference sections for each model type.
