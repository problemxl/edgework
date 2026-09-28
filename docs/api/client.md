# Edgework Client

The main client class for interacting with NHL APIs.

!!! warning "Unofficial APIs"
    Edgework targets the NHL's unofficial Web and Stats APIs. Endpoint
    availability is verified against the local reference documentation via
    the test-suite coverage contract — see
    [NHL API Documentation](nhl-apis.md#how-endpoint-availability-is-verified).

## Main Client Class

::: edgework.Edgework

## HTTP Client

::: edgework.http_client.HttpClient

## Season Validation

::: edgework.edgework._validate_season_format

## Usage Examples

### Basic Initialization

```python
from edgework import Edgework

# Default initialization
client = Edgework()

# Custom user agent
client = Edgework(user_agent="MyApp/1.0")
```

### Facade Attributes

The `Edgework` facade exposes every domain client as a public attribute, so
you never need to construct the sub-clients yourself:

| Attribute | Client | Domain |
|---|---|---|
| `client.players` | `PlayerClient` | Players, game logs, landing, spotlight |
| `client.teams` | `TeamClient` | Teams, rosters, club stats, prospects |
| `client.schedule` | `ScheduleClient` | League and club schedules, calendar |
| `client.games` | `GameClient` | Scores, gamecenter routes, replays |
| `client.standings` | `StandingClient` | Standings (now / by date / by season) |
| `client.draft` | `DraftClient` | Draft picks and rankings |
| `client.stats` | `StatsClient` | Stats API reports, leaders, resources |
| `client.playoffs` | `PlayoffClient` | Carousel, series schedule, bracket |
| `client.network` | `NetworkClient` | TV schedule, where-to-watch, odds |
| `client.utility` | `UtilityClient` | Season, meta, location, OpenAPI spec |
| `client.glossary` | `GlossaryClient` | Stats API glossary |
| `client.shifts` | `ShiftClient` | Shift charts (canonical wrapper) |

### Players

```python
client = Edgework()

# Player object with landing-page data (lazy attributes)
player = client.players.get_player(8478402)

# Raw landing data as a dict
landing = client.players.get_player_landing(8478402)

# Game logs (raw dict); season format "YYYY-YYYY"
logs = client.players.get_player_game_logs(8478402, season="2023-2024", game_type=2)

# Featured players (list of dicts)
spotlight = client.players.get_player_spotlight()

# Search-based listing of Player objects
players = client.get_all_players(active_only=True)   # -> list[Player]
```

### Games

```python
# Boxscore / play-by-play
boxscore = client.games.get_game_boxscore(2023020204)   # -> dict
pbp = client.games.get_play_by_play(2023020204)         # -> PlayByPlay

# Daily scores
scores = client.games.get_score()                        # -> dict (score/now)
scores = client.games.get_score("2023-11-10")            # -> dict (score/{date})

# Game story / right rail
story = client.games.get_game_story(2023020204)          # -> dict

# Replays (game/event IDs)
goal = client.games.get_goal_replay(2023020204, 12)      # -> dict
play = client.games.get_play_replay(2023020204, 12)      # -> dict
```

### Stats (Stats API)

```python
# Report-based stats -> list of model objects (SkaterStats / GoalieStats / TeamStats)
skaters = client.stats.get_skaters_stats(report="summary", season=20232024)
goalies = client.stats.get_goalies_stats(report="summary", season=20232024, game_type=3)
teams = client.stats.get_team_stats(report="summary", season=20232024)

# Season in YYYYYYYY integer format here; invalid formats raise ValueError.
# Leaderboards (Web API) with categories + limit
leaders = client.stats.get_skater_stats_leaders(
    categories=["goals", "assists"], limit=10
)

# Simple resources -> raw JSON (dict or list); no stable models exist
players = client.stats.get_players(limit=10, start=0)
seasons = client.stats.get_seasons()
ping = client.stats.ping()          # connectivity check -> dict
```

Report names are validated against `edgework.stats_reports`; unsupported
names raise `ValueError`. Every report method accepts an `extra_params` dict
as a raw escape hatch for additional query parameters.

### Glossary and Shifts

```python
glossary = client.glossary.get_glossary()      # -> Glossary (list of Term)
for term in glossary.terms:
    print(term)

shifts = client.shifts.get_shifts(2021020001)  # -> list[Shift]
rows = client.shifts.get_shiftcharts(game_id=2021020001)  # -> list[dict]
```

`client.shifts` is the canonical shiftcharts wrapper; `GameClient.get_shifts`
and the `Game` model delegate to it, so routes are never duplicated.

### Schedule and Standings

```python
schedule = client.get_schedule_now()                    # -> Schedule
schedule = client.get_schedule_for_date("2023-11-10")   # -> Schedule
month = client.schedule.get_schedule_for_team_for_month("TOR", "2023-11")
week = client.schedule.get_schedule_for_team_for_week("TOR", "2023-11-10")

standings = client.standings.get_standings()            # -> Standings (now)
standings = client.standings.get_standings("2023-11-10")
standings = client.standings.get_standings_for_season("2023-2024")
```

### Teams, Draft, Playoffs, Network, Utility

```python
teams = client.get_teams()                              # -> list[Team]
roster = client.get_roster("TOR", season="2023-2024")   # -> Roster

draft = client.draft.get_draft_picks(season="2023-2024")      # -> Draft
rankings = client.draft.get_draft_rankings(season="2023-2024")  # -> DraftRanking

bracket = client.playoffs.get_playoff_bracket(2023)     # -> dict

streams = client.network.get_where_to_watch()           # -> dict (streaming)
odds = client.network.get_partner_game_odds("US")       # -> dict (odds)

season = client.utility.get_season()                    # -> dict
spec = client.utility.get_openapi_spec()                # -> dict
```

### Partner game odds vs. where-to-watch

These are **different endpoints** and historically confused with each other:

- `client.network.get_where_to_watch()` requests the documented
  `/v1/where-to-watch` **streaming** route.
- `client.network.get_partner_game_odds("US")` requests the documented
  `/v1/partner-game/{country-code}/now` **odds** route.
- `GameClient.get_where_to_watch()` is a **deprecated alias** of
  `GameClient.get_partner_game_odds()` — it has always fetched odds and emits
  a `DeprecationWarning`.

## Return Types

| Method family | Return type |
|---|---|
| Report stats (`client.stats.get_*_stats`) | `list[SkaterStats]` / `list[GoalieStats]` / `list[TeamStats]` |
| Web leaderboards (`get_*_stats_leaders*`) | `dict` |
| Simple Stats resources (`get_players`, `get_seasons`, ...) | raw `dict` or `list` |
| Schedule methods | `Schedule` |
| Standings methods | `Standings` |
| Rosters / teams | `Roster` / `Team` / `list[Team]` |
| Draft picks / rankings | `Draft` / `DraftRanking` |
| Glossary / shifts | `Glossary` / `list[Shift]` or `list[dict]` |
| Gamecenter, scores, replays, meta, utility | raw `dict` (no stable models) |

## Language Handling

Stats API routes are language-prefixed. Every `StatsClient` resource method,
plus `GlossaryClient.get_glossary` and `ShiftClient` methods, accepts a
`lang` keyword argument (default `"en"`):

```python
glossary = client.glossary.get_glossary(lang="fr")
players = client.stats.get_players(lang="fr")
```

Web API routes are language-independent; `lang` is ignored for them.

## Raw-Response Methods

Where no stable model exists, Edgework returns the raw JSON payload as a
`dict` or `list` — for example all `client.utility` methods, gamecenter
raw routes (`get_game_landing`, `get_game_boxscore`, `get_game_story`),
and the simple `client.stats` resources. For maximum control, every method's
query parameters can be extended via the `extra_params` escape hatch on the
Stats API methods, and `HttpClient.get(...)` remains available for custom
calls.

## Error Handling

The client raises various exceptions for different error conditions:

- `ValueError` - Invalid input parameters (e.g., wrong season format,
  unsupported report name, invalid categories/limit values)
- `httpx.HTTPStatusError` - API request failures (raised by
  `response.raise_for_status()`)
- `Exception` - Other unexpected errors

```python
from edgework import Edgework

client = Edgework()

try:
    stats = client.stats.get_skaters_stats(season=20232024)
except ValueError as e:
    print(f"Invalid parameters: {e}")
except Exception as e:
    print(f"API error: {e}")
```
