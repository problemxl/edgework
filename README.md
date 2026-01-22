# Edgework

Edgework is a Python library providing an API wrapper for the NHL's official APIs. The library is styled similarly to PRAW (Python Reddit API Wrapper), providing an object-oriented interface to access NHL data.

## Installation

```bash
pip install edgework
```

## Quick Start

```python
from edgework import Edgework

# Initialize the API client
nhl = Edgework()

# Get current standings
standings = nhl.standings.get_standings_now()
print(standings.east_records)
print(standings.west_records)

# Get today's schedule
schedule = nhl.schedule.get_schedule()
for game in schedule.games:
    print(f"{game.away_team_abbrev} @ {game.home_team_abbrev}")

# Get player information
player = nhl.player.get_player(8478402)
print(player.full_name)

# Get a specific game
game = nhl.game.get_game(2023020204)
print(f"Final Score: {game.away_team_score} - {game.home_team_score}")
```

## Features

Edgework provides access to the following NHL data:

### Schedule
- Get current league schedule
- Get schedule for specific dates
- Get schedule for date ranges
- Get team schedules (season, month, week)

### Games
- Get game information and boxscore
- Get play-by-play data
- Get shift charts

### Players
- Get player information
- Get all players (active/inactive)
- Get player stats

### Teams
- Get team rosters (current and historical)
- Get team prospects
- Get team statistics

### Standings
- Get current standings
- Get standings by date
- Get standings by season

### Draft
- Get draft picks (current and historical)
- Get draft rankings

### Playoffs
- Get playoff brackets
- Get playoff series information

### Seasons
- Get all available seasons

### Stats
- Get skater stats leaders
- Get goalie stats leaders
- Get team stats

## API Clients

Edgework exposes the following clients through the main `Edgework` class:

| Client | Description |
|---------|-------------|
| `schedule` | Access schedule data |
| `game` | Access game information and play-by-play |
| `player` | Access player information and stats |
| `team` | Access team rosters, prospects, and stats |
| `standings` | Access league standings |
| `stats` | Access statistical leaders and team stats |
| `glossary` | Access NHL terminology glossary |
| `shifts` | Access shift chart data |
| `draft` | Access draft information |
| `playoffs` | Access playoff brackets |
| `season` | Access season information |

## Usage Examples

### Getting Player Information

```python
from edgework import Edgework

nhl = Edgework()

# Get a specific player
player = nhl.player.get_player(8478402)
print(f"Player: {player.full_name}")
print(f"Position: {player.position_code}")
print(f"Number: {player.sweater_number}")

# Get all active players
all_players = nhl.player.get_all_active_players()
for player in all_players:
    print(f"{player.full_name} - {player.team_abbrev}")
```

### Working with Schedules

```python
from edgework import Edgework

nhl = Edgework()

# Get today's schedule
schedule = nhl.schedule.get_schedule()
for game in schedule.games:
    print(f"{game.away_team_abbrev} @ {game.home_team_abbrev}")

# Get schedule for a specific date
from datetime import datetime
date_str = "2024-01-15"
schedule = nhl.schedule.get_schedule_for_date(date_str)

# Get team schedule for the month
team_schedule = nhl.schedule.get_schedule_for_team_for_month("TOR")
```

### Getting Game Details

```python
from edgework import Edgework

nhl = Edgework()

# Get game information
game = nhl.game.get_game(2023020204)
print(f"Game ID: {game.game_id}")
print(f"Score: {game.away_team_score} - {game.home_team_score}")

# Get play-by-play data
plays = nhl.game.get_play_by_play(2023020204)
for play in plays:
    print(f"{play.period} - {play.time}: {play.event_description}")

# Get shift charts
shifts = nhl.shifts.get_shifts(2023020204)
for shift in shifts:
    print(f"{shift.player.full_name}: {shift.shift_length}")
```

### Team Information

```python
from edgework import Edgework

nhl = Edgework()

# Get current roster
roster = nhl.team.get_roster_current("TOR")
for player in roster.forwards:
    print(f"#{player.sweater_number} {player.full_name}")

# Get prospects
prospects = nhl.team.get_prospects("TOR")
for prospect in prospects.forwards:
    print(f"Prospect: {prospect.full_name} ({prospect.position_code})")

# Get team stats
stats = nhl.team.get_stats_now("TOR")
print(f"Games Played: {stats.games_played}")
print(f"Wins: {stats.wins}")
```

### Draft Information

```python
from edgework import Edgework

nhl = Edgework()

# Get current draft picks
picks = nhl.draft.get_picks_now()
for pick in picks:
    print(f"Round {pick.round_number}, Pick {pick.pick_number}: {pick.player_full_name}")

# Get draft rankings
rankings = nhl.draft.get_rankings_now()
for ranking in rankings:
    print(f"#{ranking.rank}: {ranking.full_name} ({ranking.position})")
```

### Standings

```python
from edgework import Edgework

nhl = Edgework()

# Get current standings
standings = nhl.standings.get_standings_now()

# Print Eastern Conference standings
print("Eastern Conference")
for record in standings.east_records:
    print(f"{record.team_abbrev}: {record.points} pts")

# Print Western Conference standings
print("\nWestern Conference")
for record in standings.west_records:
    print(f"{record.team_abbrev}: {record.points} pts")
```

### Playoffs

```python
from edgework import Edgework

nhl = Edgework()

# Get playoff bracket for a season
bracket = nhl.playoffs.get_bracket(20232024)
print(f"Playoff Bracket {bracket.season}")
for series in bracket.series:
    print(f"{series.series_name}: {series.series_status}")
```

### Seasons

```python
from edgework import Edgework

nhl = Edgework()

# Get all available seasons
seasons = nhl.season.get_seasons()
for season in seasons:
    print(season)
```

## Data Models

Edgework uses Python dataclasses to represent NHL data:

- `Player` - Player information
- `Game` - Game information and scores
- `Schedule` - Schedule information
- `GameEvent` - Play-by-play events
- `Shift` - Shift chart data
- `Standings` - League standings
- `Prospect` - Team prospect information
- `RosterPlayer` - Roster player information
- `DraftPick` - Draft pick information
- `DraftRanking` - Draft ranking information
- `PlayoffSeries` - Playoff series information
- `PlayoffBracket` - Playoff bracket
- `Season` - Season information

## API Reference

The NHL APIs are documented at:
- [NHL API Reference](https://github.com/Zmalski/NHL-API-Reference)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Acknowledgments

This library wraps the official NHL APIs. The NHL API documentation can be found at:
https://github.com/Zmalski/NHL-API-Reference
