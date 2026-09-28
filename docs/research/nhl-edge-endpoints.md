# NHL Edge API — Investigation Findings

> Research notes on the endpoints powering [nhl.com/nhl-edge](https://www.nhl.com/nhl-edge/teams)
> (puck- and player-tracking data: shot speed, skating speed/distance, zone time, shot/save locations).
>
> **Unverified/unofficial**: reverse-engineered from the NHL Edge web app (webpack bundles + live
> network capture + direct probing, ~1000 requests). All requests are plain `GET` JSON on
> `https://api-web.nhle.com` — no auth, no cookies; a browser-like `User-Agent` is sufficient.

## How this was investigated

1. Scraped the SPA's JS bundles (`wsr.nhle.com/static/js/`) and extracted the webpack chunk-name map
   (`EdgeTeamLanding`, `EdgeSkaterDetail`, `EdgeComparison`, ...).
2. Loaded the site in headless Chromium (Playwright) and captured live API traffic while clicking
   through every page/tab.
3. Systematically probed candidate routes (`{skater|goalie|team}` × `{view}` × `{detail|details|top-10}`
   × parameter combinations) across two seasons.

---

## Endpoint catalog

Conventions:
- `{season}` = 8-digit form (`20252026`). **`now`** is accepted in place of `{season}/{gameType}` and
  307-redirects to the resolved current season (follow redirects).
- `{gameType}` = `2` (regular season), `3` (playoffs).
- `{situation}` = `all` | `es` (even strength) | `pp` | `pk` — many top-10s only return data for `all`.
- Valid route + no data ⇒ `[]` (HTTP 200, 2-byte empty array), not 404.
- Measures come in imperial/metric pairs: `{"imperial": 102.4, "metric": 165.0, "overlay": {...}}`.

### 1. Landing pages (leaderboards)

| Endpoint | Leader keys in response |
|---|---|
| `GET /v1/edge/skater-landing/{season}/{gameType}` | hardestShot, maxSkatingSpeed, totalDistanceSkated, distanceMaxGame, highDangerSOG, offensiveZoneTime, defensiveZoneTime |
| `GET /v1/edge/goalie-landing/{season}/{gameType}` | highDangerSavePctg, highDangerSaves, highDangerGoalsAgainst, savePctg5v5, gamesAbove900 (plus `minimumGamesPlayed`) |
| `GET /v1/edge/team-landing/{season}/{gameType}` | shotAttemptsOver90, burstsOver22, distancePer60, highDangerSOG, offensive/neutral/defensiveZoneTime |

All three also accept `/now` and return `seasonsWithEdgeStats: [{id, gameTypes}]` for season discovery.

### 2. Base detail

| Endpoint | Response shape |
|---|---|
| `GET /v1/edge/skater-detail/{playerId}/{season}/{gameType}` | `player` bio + percentile `stats` vs league avg |
| `GET /v1/edge/goalie-detail/{goalieId}/{season}/{gameType}` | `player` + `stats.{metric: {value, percentile, leagueAvg}}` (GAA, gamesAbove900, goalDifferentialPer60, goalSupportAvg, ...) |
| `GET /v1/edge/team-detail/{teamId}/{season}/{gameType}` | team equivalent |

### 3. Comparison (fetch each side separately, diff client-side)

| Endpoint |
|---|
| `GET /v1/edge/skater-comparison/{playerId}/{season}/{gameType}` |
| `GET /v1/edge/goalie-comparison/{goalieId}/{season}/{gameType}` |
| `GET /v1/edge/team-comparison/{teamId}/{season}/{gameType}` |

Skater comparison bundles `shotSpeedDetails`, `skatingSpeedDetails`, skating distance, zone time,
shot locations — one call per entity; the UI requests both entities it compares. `/now` also works.

### 4. View-specific detail

| Endpoint | Notes |
|---|---|
| `GET /v1/edge/skater-shot-speed-detail/{playerId}/{season}/{gt}` | topShotSpeed/avgShotSpeed + attempts buckets (100+/90-100/80-90/70-80) |
| `GET /v1/edge/skater-skating-speed-detail/{playerId}/{season}/{gt}` | maxSkatingSpeed + bursts over 22/20/18 mph |
| `GET /v1/edge/skater-skating-distance-detail/{playerId}/{season}/{gt}` | distance per game/situation |
| `GET /v1/edge/skater-shot-location-detail/{playerId}/{season}/{gt}` | `shotLocationDetails[]` (by area: sog, goals, pctg, percentile) + `shotLocationTotals[]` (with league avgs) |
| `GET /v1/edge/goalie-shot-location-detail/{goalieId}/{season}/{gt}` | save % by danger zone (all/highDanger/midRange/longRange) |
| `GET /v1/edge/team-shot-speed-detail/{teamId}/{season}/{gt}` | |
| `GET /v1/edge/team-skating-speed-detail/{teamId}/{season}/{gt}` | |
| `GET /v1/edge/team-skating-distance-detail/{teamId}/{season}/{gt}` | |
| `GET /v1/edge/team-shot-location-detail/{teamId}/{season}/{gt}` | |
| `GET /v1/edge/team-zone-time-details/{teamId}/{season}/{gt}` | ⚠️ plural `-details` (only endpoint like this): zone % + rank + league avg by strength, plus `shotDifferential` |

### 5. Top-10 leaderboards

| Endpoint | Params |
|---|---|
| `GET /v1/edge/skater-shot-speed-top-10/{situation}/{sort}/{season}/{gt}` | sort `max` (others return `[]`) |
| `GET /v1/edge/team-shot-speed-top-10/{situation}/{sort}/{season}/{gt}` | same |
| `GET /v1/edge/team-skating-speed-top-10/{situation}/{sort}/{season}/{gt}` | same |
| `GET /v1/edge/skater-shot-location-top-10/{situation}/{metric}/{filter}/{season}/{gt}` | metric `sog`\|`goals`, filter `all` |
| `GET /v1/edge/team-shot-location-top-10/{situation}/{metric}/{filter}/{season}/{gt}` | same |
| `GET /v1/edge/team-skating-distance-top-10/{situation}/{param}/{sort}/{season}/{gt}` | only `all/all/total` returns data |
| `GET /v1/edge/team-zone-time-top-10/{situation}/{zone}/{season}/{gt}` | zone `offensive`\|`defensive`\|`neutral` |
| `GET /v1/edge/goalie-shot-location-top-10/{metric}/{situation}/{season}/{gt}` | ⚠️ param order differs: metric first (`save-pctg`\|`saves`\|`goals-against`), situation `all` only |

### Not found (404) — checked exhaustively

- `skater-skating-speed-top-10`, `skater-zone-time-top-10`, `goalie-*-top-10` (except shot-location),
  `skater|goalie|team-five-on-five-*`, `*-save-locations-*`, `*-save-pctg-detail` — these views are
  served by the base detail/comparison payloads or the landing leaders instead.
- `goalie-shot-location-*` at season `20242025` (data starts `20252026` for that family);
  skater/team families have data from `20242025`.

## Data availability & quirks

- **Seasons**: tracking data exists from **2024-25** onward (goalie save locations from 2025-26).
  Use `seasonsWithEdgeStats` from any landing/detail response to discover valid combos.
- **Empty ≠ invalid**: e.g. `.../es/max/...` top-10s legitimately return `[]`.
- **`/now`** redirects (307) — make sure the HTTP client follows redirects.
- Team IDs are the numeric NHL team id (e.g. `14` = Tampa Bay); player IDs are the standard NHL
  player id (e.g. `8478402` = Connor McDavid).
- i18n: names come localized (`firstName: {default, cs, fi, sk}`).

## The Goal Visualizer (Puck & Player Tracking replays)

The site's player/puck **location** feature is the **"EDGE | Goal Visualizer"** at
`https://www.nhl.com/ppt-replay/goal/{gameId}/{eventId}` — an animated 2D rink view of every goal,
built from actual Puck & Player Tracking frames. It is **not** a live stream: no WebSockets exist on
the site (verified by capture); it is per-goal-event replay data, published shortly after each goal.

### Data pipeline

1. Get goal events from `GET /v1/wsc/play-by-play/{gameId}` (already in the library). Goals have
   `typeDescKey: "goal"`; note `eventId` there (e.g. `95`).
2. `GET https://api-web.nhle.com/v1/ppt-replay/{gameId}/{eventId}` → goal metadata incl.
   **`goal.pptReplayUrl`** (e.g. `https://wsr.nhle.com/sprites/20252026/2025020740/ev95.json`).
   The `/ppt-replay/goal/...` variant just 307-redirects to this. Preseason games return **no**
   `pptReplayUrl` (no tracking coverage); regular-season goals have it.
3. `GET {pptReplayUrl}` → the tracking frames. **Requires `Referer: https://www.nhl.com/` header**
   (UA alone or `Origin` alone → 403 from the CDN — same guard as the wsr.nhle.com JS chunks).

### Sprite frame format

```json
[
  {
    "timeStamp": 17685233789,          // frame counter, 1 unit = 0.1s (10 fps)
    "onIce": {
      "1":    { "id": 1,    "playerId": "",      "x": 2352.46, "y": 390.10,
                 "sweaterNumber": "", "teamId": "", "teamAbbrev": "" },   // ← the PUCK is id "1"
      "7006": { "id": 7006, "playerId": 8484145, "x": 2364.78, "y": 713.54,
                 "sweaterNumber": 6,  "teamId": 7,  "teamAbbrev": "BUF" }
    }
  }
]
```

- ~140 frames per goal ≈ 14 s of play leading to the score (10 fps).
- 13–15 entities per frame: 12 players (5v5 + 2 goalies, occasional extra during changes) + puck.
- Player keys look like `{teamId digit}{sweaterNumber}` (e.g. `7006` = BUF #6).
- **Coordinates are inches**: x ∈ [0, 2400] (200 ft rink length), y ∈ [0, 1020] (85 ft width).
  Divide by 12 for feet. Puck step ≈ 23–41 in/frame ≈ 13–23 mph — sanity-checks the 10 fps reading.

## Proposed client integration (not yet implemented)

A natural fit is a new `EdgeClient` on the existing `HttpClient` (Web API host):

```python
client.edge.get_skater_landing(season="20252026", game_type=2)
client.edge.get_skater_detail(player_id=8482095, season="now")
client.edge.get_team_zone_time_details(team_id=14)          # plural route!
client.edge.get_goalie_shot_location_top_10(metric="save-pctg")
client.edge.compare_skaters(8482095, 8478402, season="20252026")

# Goal Visualizer tracking frames (needs the Referer header on the sprites host)
client.edge.get_goal_frames(game_id=2025020740, event_id=95)
# → follows ppt-replay metadata → pptReplayUrl → frame list (puck id "1", inches, 10 fps)
```

All ~28 routes above would register in `edgework/endpoints.py` under an `edge_*` namespace and join
the endpoint-coverage manifest. The Goal Visualizer needs one `HttpClient` addition: the sprites
host requires `Referer: https://www.nhl.com/` (the existing `get_ppt_replay` methods in
`GameClient` already return the metadata; only the `pptReplayUrl` follow-through is new).
