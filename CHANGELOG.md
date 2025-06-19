# Changelog

All notable changes to the Edgework project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
