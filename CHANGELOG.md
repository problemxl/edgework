# Changelog

All notable changes to Edgework project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.9.0] - 2025-02-16

### Added
- **Player Client Enhancement**: Complete PlayerClient implementation with all missing endpoints
  - Added `get_player_landing()` - Fetch comprehensive player profile with career/current stats
  - Added `get_player_game_logs()` - Get game-by-game statistics for specific season
  - Added `get_player_game_log_now()` - Get current season game logs
  - Added `get_player_spotlight()` - Get featured/spotlight players
  - Added `get_player()` - Get Player object by ID with full data
  - Added `get_player_by_id()` - Get player with error handling
  - Updated game_type parameter to use numeric values (2=Regular Season, 3=Playoffs, 1=Pre-season)
  - Added comprehensive test suite with 19 tests (all passing)

### New API Endpoints Supported:
- `player/{player_id}/landing` - Player profile and statistics
- `player/{player_id}/game-log/{season}/{game_type}` - Season game logs
- `player/{player_id}/game-log/now` - Current season game logs
- `player-spotlight` - Featured players

## [0.8.0] - 2025-02-16

### Added
- **Game Client Enhancement**: Complete GameClient implementation with all missing endpoints
  - Added `get_game_landing()` - Fetch comprehensive game landing page data
  - Added `get_game_boxscore()` - Get raw boxscore dictionary
  - Added `get_game_story()` - Fetch game story/narrative content
  - Added `get_game_right_rail()` - Get right rail game information
  - Added `get_score()` - Fetch current or historical scores by date
  - Added `get_scoreboard()` - Get current scoreboard data
  - Added `get_where_to_watch()` - Get broadcast information
  - Added `get_games_for_date()` - Get all games for a specific date
  - Added `get_current_games()` - Get current/upcoming games
  - Fixed `get_play_by_play()` to return proper PlayByPlay object
  - Fixed `get_game()` to use correct web API endpoint
  - Added comprehensive test suite with 19 tests (18 passing, 1 skipped due to season availability)

### Changed
- **GameClient**: Updated all game endpoints to use web API (`web=True` parameter)
- **GameClient**: Fixed incomplete `get_play_by_play()` method implementation

### Fixed
- **GameClient**: Corrected endpoint URLs for gamecenter API calls

## [0.7.0] - 2025-02-16

### Added
- **Standings Module**: Complete implementation of NHL standings functionality
  - New `StandingClient` for fetching current and historical standings
  - Refactored `Standings` and `Seeding` models using BaseNHLModel inheritance
  - Added filtering methods: `get_team_standing()`, `get_division_standings()`, `get_playoff_teams()`, `get_wildcard_race()`
  - Added comprehensive test suite with 24 tests including live API tests
- **Draft Module**: Complete implementation of NHL draft functionality
  - New `DraftClient` with methods for draft picks, rankings, and tracker
  - `Draft` model with support for filtering picks by round, team, and overall pick number
  - `Draftee` model for individual draft selections with full player details
  - `DraftRanking` model for prospect rankings with top prospect queries
  - Added comprehensive test suite with 23 tests including live API tests
- **New API Endpoints Supported**:
  - `/standings/now` and `/standings/{date}` - Current and historical standings
  - `/draft/picks/now` and `/draft/picks/{season}/{round}` - Draft picks
  - `/draft/rankings/now` and `/draft/rankings/{season}/{category}` - Draft rankings
  - `/draft-tracker/picks/now` - Live draft tracker

## [0.6.0] - 2025-02-01

### Added
- **Play Model**: New `Play` model for individual play events in a game (goals, penalties, shots, faceoffs, etc.)
- **PlayByPlay Model**: New `PlayByPlay` model for full play-by-play game data
- **Game Model**: Add `play_by_play` property to `Game` object with lazy loading
- **Play Model**: Add helper properties (`is_goal`, `is_penalty`, `is_shot`, `goal_details`, `scoring_player_id`, `assist_player_ids`)
- **PlayByPlay Model**: Add filtering methods (`goals`, `penalties`, `shots` properties)
- **PlayByPlay Model**: Add query methods (`get_plays_by_period()`, `get_plays_by_team()`, `get_plays_by_player()`)
- **Tests**: Add comprehensive play-by-play test suite with 23 test cases

## [0.5.0] - 2025-02-01

### Fixed
- **Schedule**: Fix `get_schedule_for_date_range()` to pass HTTP client to `Schedule.from_api()`, enabling proper lazy loading of games
- **Game**: Fix `Game.from_api()` to set `_fetched=True` flag, preventing unnecessary API fetches
- **Schedule**: Fix empty games list issue when accessing `schedule.games` property for date range queries

### Changed
- **Game Model**: Enable lazy loading for Game objects via BaseNHLModel `_fetch_if_not_fetched()`

## [0.4.8] - 2025-01-28

### Fixed
- **Schedule**: Fix date filtering to use correct API field `startTimeUTC` instead of non-existent `gameDate`
- **Tests**: Update test mocks to use `startTimeUTC` field matching actual API response

## [0.4.7] - 2025-01-28

### Fixed
- **Schedule**: Use nextStartDate pagination to avoid duplicate games when fetching schedule by date range
- **Schedule Client**: Added web=True parameter to get_schedule_for_date_range for correct API endpoint usage
- **Tests**: Added TestScheduleClient unit tests and TestScheduleIntegration live API tests

## [0.4.6] - 2025-01-28

### Fixed
- **Schedule**: Use nextStartDate pagination to avoid duplicate games when fetching schedule by date range
- **Schedule Client**: Added web=True parameter to get_schedule_for_date and get_schedule_for_date_range for correct API endpoint usage

## [0.4.5] - 2025-01-28

### Fixed
- **Schedule**: Use nextStartDate pagination to avoid duplicate games when fetching schedule by date range
- **Schedule Client**: Added web=True parameter to get_schedule_for_date and get_schedule_for_date_range for correct API endpoint usage

## [0.4.3] - 2025-01-28

### Fixed
- **Schedule**: Use nextStartDate pagination to avoid duplicate games when fetching schedule by date range
- **Schedule Client**: Added web=True parameter to get_schedule_for_date and get_schedule_for_date_range for correct API endpoint usage

## [0.3.1] - 2025-06-24

### Added
- **Teams**: Player retrieval methods to Roster class for easier access to team player data
- **Schedule**: String representation (`__str__`) method and fetched data flag for better debugging and state tracking
- **Models**: Enhanced string representations and improved type hints across Player, Schedule, and Team models
- **Documentation**: Comprehensive documentation suite including:
  - API reference documentation for all clients and models
  - Getting started guides (installation, quickstart, configuration)
  - Usage examples (basic, advanced, and common patterns)
  - Contributing guidelines and changelog documentation
  - MkDocs configuration for documentation site generation

### Enhanced
- **Schedule Client**: Improved error handling and data management capabilities
- **Models**: Better string representations for debugging and development experience
- **Type Hints**: Enhanced type annotations throughout the codebase for better IDE support

### Changed
- Updated User-Agent to EdgeworkClient/0.3.1

## [0.2.1] - 2025-06-19

### Fixed
- **Critical**: Fixed player client HTTP method causing 400 Bad Request errors
- Corrected `get()` to `get_raw()` for NHL search API endpoints in PlayerClient
- Added missing `datetime` import in player_client.py
- Ensured all 21 player attributes are properly mapped from NHL search API
- Fixed data type conversions for player_id and team_id fields

### Changed
- Updated User-Agent to EdgeworkClient/0.2.1

## [0.2.0] - 2025-06-19

### Added
- Version constant in `__init__.py` for programmatic access
- Comprehensive pytest test suite for `edgework.py` module
- `players()` method to fetch list of NHL players with active/inactive filtering
  - Returns list of Player objects with full player information
  - Supports `active_only=True` (default) for current players
  - Supports `active_only=False` for all players including retired/inactive
  - Player objects include name, position, team, and other NHL data

### Changed
- Updated project version from 0.1.0 to 0.2.0
- Updated default User-Agent from "EdgeworkClient/1.0" to "EdgeworkClient/0.2.0"

### Fixed
- Robust season string validation that properly validates "YYYY-YYYY" format
- Season validation now raises appropriate `ValueError` for invalid formats

## [0.1.0] - Previous Release

### Added
- Initial release of Edgework NHL API client
- Core functionality for fetching player, skater, goalie, and team statistics
- HTTP client with proper NHL API integration
- Basic model classes for data representation
