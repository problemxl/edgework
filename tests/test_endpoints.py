"""Tests for the endpoint registry in edgework.endpoints."""

import pytest

from edgework.const import API_VERSION
from edgework.endpoints import API_PATH, format_endpoint, get_endpoint


class TestRegistryCoverage:
    """The registry covers every documented Web and Stats API route."""

    @pytest.mark.parametrize(
        "key",
        [
            # Players
            "player_game_logs",
            "player_game_log_now",
            "player_landing",
            "player_spotlight",
            # Leaders
            "skater_stats_now",
            "skater_stats_season_game_type",
            "goalie_stats_now",
            "goalie_stats_season_game_type",
            # Standings
            "standings",
            "standings_date",
            "standings_season",
            # Club stats
            "club_stats",
            "club_stats_season",
            "club_stats_season_game_type",
            "team_scoreboard",
            # Roster
            "roster_current",
            "roster_season",
            "roster_season_team",
            "team_prospects",
            # Schedule
            "club_schedule_season_now",
            "club_schedule_season",
            "club_schedule_month_now",
            "club_schedule_month",
            "club_schedule_week",
            "club_schedule_week_now",
            "schedule_now",
            "schedule_date",
            "schedule_calendar_now",
            "schedule_calendar_date",
            # Games
            "score_now",
            "score_date",
            "scoreboard_now",
            "where_to_watch",
            "play_by_play",
            "game_landing",
            "game_boxscore",
            "game_story",
            "game_right_rail",
            "wsc_play_by_play",
            # Network / odds
            "tv_schedule_date",
            "tv_schedule_now",
            "partner_game",
            # Playoffs
            "playoff_series_carousel",
            "playoff_series_schedule",
            "playoff_bracket",
            # Season / draft
            "season",
            "draft_rankings_now",
            "draft_rankings",
            "draft_tracker_picks_now",
            "draft_picks_now",
            "draft_picks",
            # Miscellaneous
            "meta",
            "meta_game",
            "location",
            "meta_playoff_series",
            "postal_lookup",
            "goal_replay",
            "play_replay",
            "openapi_spec",
        ],
    )
    def test_documented_web_endpoints_present(self, key):
        assert key in API_PATH

    @pytest.mark.parametrize(
        "key,expected",
        [
            ("stats_players", "/{lang}/players"),
            ("stats_skater", "/{lang}/skater"),
            ("stats_skater_report", "/{lang}/skater/{report}"),
            ("stats_skater_leaders", "/{lang}/leaders/skaters/{attribute}"),
            ("stats_skater_milestones", "/{lang}/milestones/skaters"),
            ("stats_goalie_report", "/{lang}/goalie/{report}"),
            ("stats_goalie_leaders", "/{lang}/leaders/goalies/{attribute}"),
            ("stats_goalie_milestones", "/{lang}/milestones/goalies"),
            ("stats_draft", "/{lang}/draft"),
            ("stats_team", "/{lang}/team"),
            ("stats_team_by_id", "/{lang}/team/id/{team_id}"),
            ("stats_team_report", "/{lang}/team/{report}"),
            ("stats_franchise", "/{lang}/franchise"),
            ("stats_component_season", "/{lang}/componentSeason"),
            ("stats_season", "/{lang}/season"),
            ("stats_game", "/{lang}/game"),
            ("stats_game_meta", "/{lang}/game/meta"),
            ("stats_config", "/{lang}/config"),
            ("stats_ping", "/ping"),
            ("stats_country", "/{lang}/country"),
            ("stats_shiftcharts", "/{lang}/shiftcharts"),
            ("stats_glossary", "/{lang}/glossary"),
            ("stats_content_module", "/{lang}/content/module/{template_key}"),
        ],
    )
    def test_documented_stats_endpoints_present(self, key, expected):
        assert API_PATH[key] == expected


class TestCorrectedRoutes:
    """Routes that previously drifted from the documentation."""

    def test_club_stats_season_game_type_route_is_documented_route(self):
        """club-stats season+game-type lives under /club-stats, not /club-stats-season."""
        assert API_PATH["club_stats_season_game_type"] == (
            "/{API_VERSION}/club-stats/{team}/{season}/{game-type}"
        )

    def test_club_stats_season_game_type_formats_correctly(self):
        route = format_endpoint(
            "club_stats_season_game_type", team="TOR", season="20232024", **{"game-type": 2}
        )
        assert route == f"/{API_VERSION}/club-stats/TOR/20232024/2"

    def test_openapi_spec_route(self):
        assert API_PATH["openapi_spec"] == "/model/{API_VERSION}/openapi.json"
        assert format_endpoint("openapi_spec") == f"/model/{API_VERSION}/openapi.json"


class TestLegacyAliases:
    """Legacy keys remain available and point at corrected routes."""

    def test_club_stats_season_season_game_type_alias(self):
        assert "club_stats_season_season_game_type" in API_PATH
        assert (
            API_PATH["club_stats_season_season_game_type"]
            == API_PATH["club_stats_season_game_type"]
        )


class TestRegistryHelpers:
    """Registry access helpers."""

    def test_get_endpoint_returns_route(self):
        assert get_endpoint("standings") == "/{API_VERSION}/standings/now"

    def test_get_endpoint_unknown_key_raises(self):
        with pytest.raises(KeyError):
            get_endpoint("not_a_real_endpoint")

    def test_format_endpoint_substitutes_version_and_params(self):
        route = format_endpoint("player_game_logs", player_id=8478402,
                                season="20232024", **{"game-type": 2})
        assert route == f"/{API_VERSION}/player/8478402/game-log/20232024/2"

    def test_format_endpoint_missing_param_raises(self):
        with pytest.raises(KeyError):
            format_endpoint("player_landing")

    def test_stats_routes_use_lang_placeholder(self):
        assert "{lang}" in API_PATH["stats_franchise"]
        assert "{lang}" not in API_PATH["stats_ping"]
