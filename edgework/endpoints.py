from .const import API_VERSION

API_PATH: dict = {
    # Player endpoints
    "player_game_logs": "/v1/player/{player_id}/game-log/{season}/{game-type}",
    "player_game_log_now": "/v1/player/{player_id}/game-log/now",
    "player_landing": "/v1/player/{player_id}/landing",
    "player_spotlight": "/v1/player-spotlight",
    # Stats endpoints
    "skater_stats_now": "/v1/skater-stats-leaders/current",
    "skater_stats_season_game_type": "/v1/skater-stats-leaders/{season}/{game_type}",
    "goalie_stats_now": "/v1/goalie-stats-leaders/current",
    "goalie_stats_season_game_type": "/v1/goalie-stats-leaders/{season}/{game_type}",
    # Standings endpoints
    "standings": "/v1/standings/now",
    "standings_date": "/v1/standings/{date}",
    "standings_season": "/v1/standings-season",
    # Club stats endpoints
    "club_stats": "/v1/club-stats/{team}/now",
    "club_stats_season": "/v1/club-stats-season/{team}",
    "club_stats_season_season_game_type": "/v1/club-stats-season/{team}/{season}/{game_type}",
    "team_scoreboard": "/v1/scoreboard/{team}/now",
    # Roster endpoints
    "roster_current": "/v1/roster/{team}/current",
    "roster_season": "/v1/roster/{team}/{season}",
    "roster_season_team": "/v1/roster-season/{team}",
    "team_prospects": "/v1/prospects/{team}",
    # Schedule endpoints
    "club_schedule_season_now": "/v1/club-schedule-season/{team}/now",
    "club_schedule_season": "/v1/club-schedule-season/{team}/{season}",
    "club_schedule_month_now": "/v1/club-schedule/{team}/month/now",
    "club_schedule_month": "/v1/club-schedule/{team}/month/{month}",
    "club_schedule_week": "/v1/club-schedule/{team}/week/{date}",
    "club_schedule_week_now": "/v1/club-schedule/{team}/week/now",
    "schedule_now": "/v1/schedule/now",
    "schedule_date": "/v1/schedule/{date}",
    "schedule_calendar_now": "/v1/schedule-calendar/now",
    "schedule_calendar_date": "/v1/schedule-calendar/{date}",
    # Game endpoints
    "score_now": "/v1/score/now",
    "score_date": "/v1/score/{date}",
    "scoreboard_now": "/v1/scoreboard/now",
    "where_to_watch": "/v1/where-to-watch",
    "play_by_play": "/v1/gamecenter/{game_id}/play-by-play",
    "game_landing": "/v1/gamecenter/{game_id}/landing",
    "game_boxscore": "/v1/gamecenter/{game_id}/boxscore",
    "game_story": "/v1/wsc/game-story/{game_id}",
    "game_right_rail": "/v1/gamecenter/{game_id}/right-rail",
    "wsc_play_by_play": "/v1/wsc/play-by-play/{game_id}",
    # Network endpoints
    "tv_schedule_date": "/v1/network/tv-schedule/{date}",
    "tv_schedule_now": "/v1/network/tv-schedule/now",
    # Odds endpoints
    "partner_game": "/v1/partner-game/{country_code}/now",
    # Playoff endpoints
    "playoff_series_carousel": "/v1/playoff-series/carousel/{season}/",
    "playoff_series_schedule": "/v1/schedule/playoff-series/{season}/{series_letter}/",
    "playoff_bracket": "/v1/playoff-bracket/{year}",
    # Season endpoints
    "season": "/v1/season",
    # Draft endpoints
    "draft_rankings_now": "/v1/draft/rankings/now",
    "draft_rankings": "/v1/draft/rankings/{season}/{prospect_category}",
    "draft_tracker_picks_now": "/v1/draft-tracker/picks/now",
    "draft_picks_now": "/v1/draft/picks/now",
    "draft_picks": "/v1/draft/picks/{season}/{round}",
    # Miscellaneous endpoints
    "meta": "/v1/meta",
    "meta_game": "/v1/meta/game/{game_id}",
    "location": "/v1/location",
    "meta_playoff_series": "/v1/meta/playoff-series/{year}/{series_letter}",
    "postal_lookup": "/v1/postal-lookup/{postal_code}",
    "goal_replay": "/v1/ppt-replay/goal/{game_id}/{event_number}",
    "play_replay": "/v1/ppt-replay/{game_id}/{event_number}",
    "openapi_spec": "/model/v1/openapi.json",
}
