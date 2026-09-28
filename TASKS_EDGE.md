# Task List: NHL Edge Client + Goal Visualizer

Source research: `docs/research/nhl-edge-endpoints.md` (read it first — it contains the full
endpoint catalog, param enums, response schemas, and quirks). Execute tasks in order; each builds
on the prior. After each task run `python -m pytest tests/ -x -q` (no live network) and fix
failings before finishing. Follow repo conventions established in TASKS.md (completed):
registry-first, params always in `params=`, raw-dict returns where no stable model exists,
manifest entries for every canonical route.

Ground rules for all tasks:
- All Edge routes are **Web API** (`web=True` on `HttpClient.get`), under `/v1/edge/...`.
- `season` accepts `"now"` (the API 307-redirects; `httpx` already follows redirects).
- Empty results are legitimate (`[]`) — never raise on them.
- Tracking data exists only from 2024-25 on; don't hard-code a season list — expose
  `seasonsWithEdgeStats` from responses where relevant.

---

## Task E1 — Registry + EdgeClient foundation (landings, details, comparisons)

**Files:** `edgework/endpoints.py`, new `edgework/clients/edge_client.py`, `edgework/edgework.py`, `edgework/clients/__init__.py`, tests

1. Register these canonical routes in `API_PATH` with `edge_`-prefixed keys (Web API family):
   - `edge_skater_landing`: `/{API_VERSION}/edge/skater-landing/{season}/{game-type}`
   - `edge_goalie_landing`, `edge_team_landing` (same shape)
   - `edge_skater_detail`: `/{API_VERSION}/edge/skater-detail/{player-id}/{season}/{game-type}`
   - `edge_goalie_detail`, `edge_team_detail` (same shape; team uses `{team-id}`)
   - `edge_skater_comparison`: `/{API_VERSION}/edge/skater-comparison/{player-id}/{season}/{game-type}`
   - `edge_goalie_comparison`, `edge_team_comparison`
2. New `EdgeClient(http_client)` with methods (raw dict returns — schemas vary by metric):
   - `get_skater_landing(season="now", game_type=2)` (+ goalie/team variants)
   - `get_skater_detail(player_id, season="now", game_type=2)` (+ goalie/team variants)
   - `compare(entity, id_a, id_b, season="now", game_type=2)` → returns `{"a": ..., "b": ...}` by
     fetching both sides (composite helper — see manifest exclusion rule), **plus** per-entity
     methods `get_skater_comparison(...)` etc. that own the canonical route.
   - `get_available_seasons()` convenience hitting any landing and returning `seasonsWithEdgeStats`.
3. Instantiate `self.edge = EdgeClient(http_client=self._client)` in the `Edgework` facade.
4. Tests (mocked `respx`/existing pattern): route correctness incl. `/now`, game-type
   substitution, facade exposure, `compare()` fan-out produces exactly 2 requests.

**Done when:** 9 canonical routes registered, EdgeClient + facade live, tests pass.

---

## Task E2 — View details + top-10 leaderboards with param validation

**Files:** `edgework/clients/edge_client.py`, `edgework/endpoints.py`, tests

1. Register view-detail routes (5 more; names exactly as the API spells them):
   - `edge_skater_shot_speed_detail`, `edge_skater_skating_speed_detail`,
     `edge_skater_skating_distance_detail`, `edge_skater_shot_location_detail`
     — `/{API_VERSION}/edge/skater-{view}-detail/{player-id}/{season}/{game-type}`
   - `edge_goalie_shot_location_detail` (goalie variant)
   - `edge_team_shot_speed_detail`, `edge_team_skating_speed_detail`,
     `edge_team_skating_distance_detail`, `edge_team_shot_location_detail`
   - `edge_team_zone_time_details` — ⚠️ **plural `-details`**, only endpoint spelled this way:
     `/{API_VERSION}/edge/team-zone-time-details/{team-id}/{season}/{game-type}`
2. Register top-10 routes (note the differing param orders/shapes):
   - `edge_skater_shot_speed_top_10`: `.../skater-shot-speed-top-10/{situation}/{sort}/{season}/{game-type}`
   - `edge_team_shot_speed_top_10`, `edge_team_skating_speed_top_10` (same shape)
   - `edge_skater_shot_location_top_10`: `.../skater-shot-location-top-10/{situation}/{metric}/{filter}/{season}/{game-type}`
   - `edge_team_shot_location_top_10` (same shape)
   - `edge_team_skating_distance_top_10`: `.../team-skating-distance-top-10/{situation}/{param}/{sort}/{season}/{game-type}`
   - `edge_team_zone_time_top_10`: `.../team-zone-time-top-10/{situation}/{zone}/{season}/{game-type}`
   - `edge_goalie_shot_location_top_10`: ⚠️ **metric first**: `.../goalie-shot-location-top-10/{metric}/{situation}/{season}/{game-type}`
3. Client methods with **validated** params (module-level enums or `Literal`, raise `ValueError`
   on invalid, matching `stats_reports.py` style):
   - `SITUATION`: `all|es|pp|pk` · `SORT`: `max|avg` · `SHOT_METRIC`: `sog|goals`
   - `ZONE`: `offensive|defensive|neutral` · `GOALIE_METRIC`: `save-pctg|saves|goals-against`
   - Distance middle param: only `all` observed → accept only `all` for now.
4. Tests: every method builds the exact URL (esp. goalie param order, plural zone-time route);
   invalid params raise; empty-array responses pass through.

**Done when:** all view/top-10 routes registered + methods + tests pass.

---

## Task E3 — Goal Visualizer: PPT tracking frames

**Files:** `edgework/clients/edge_client.py` (+ `game_client.py` touchpoint), `edgework/http_client.py`, `edgework/endpoints.py`, tests

1. `HttpClient.get_raw` gains an optional `headers: Optional[Dict[str, str]]` param (merged over
   defaults). The sprites host **requires** `Referer: https://www.nhl.com/` — UA alone gets 403.
2. `EdgeClient.get_goal_frames(game_id, event_id)`:
   - GET the existing `ppt_replay` route (`/v1/ppt-replay/{game-id}/{event-number}` — already in
     the registry from Task 3 of the prior plan) and read `goal.pptReplayUrl`;
   - return `None` when `pptReplayUrl` is absent (preseason/no coverage) — do not raise;
   - fetch the URL via `get_raw(url, headers={"Referer": "https://www.nhl.com/"})` and return
     the parsed frame list.
3. Frame format helper (pure functions, documented in the research doc):
   - `puck_frames(frames)` → list of `(timestamp, x, y)` for entity key `"1"`;
   - `player_frames(frames, player_id=None)` → per-player frame lists;
   - document units in docstrings: coordinates **inches** (rink 2400×1020), timestamps are
     decisecond counters (10 fps, ~140 frames ≈ 14 s).
4. Keep `GameClient.get_ppt_replay` as-is but delegate/frame-following lives in EdgeClient; note
   the delegation with a comment (no duplicated route logic).
5. Tests: mocked ppt-replay metadata (with and without `pptReplayUrl`) + mocked sprites JSON
   asserting the Referer header is sent; frame helpers unit-tested against a small fixture
   (puck key "1", inch coordinates).

**Done when:** `get_goal_frames` works end-to-end against mocks with correct headers.

---

## Task E4 — Manifest, docs, final validation

**Files:** `tests/endpoint_manifest.py`, `tests/test_endpoint_coverage.py` (fixtures), `docs/api/nhl-apis.md`, `docs/api/client.md`, `edgework/NHL API Documentation.md`, tests

1. Add a `ManifestEntry` for every canonical Edge route registered in E1–E3 (mock payloads per
   the schemas in the research doc). Composite helpers (`compare()`, `get_goal_frames`,
   `get_available_seasons`) are excluded per the manifest rules — their canonical routes are
   already manifested (`compare` → the underlying comparison route; `get_goal_frames` → `ppt_replay`).
2. Confirm completeness test is green: every registry `edge_*` key manifested, zero orphans.
3. Docs:
   - `docs/api/nhl-apis.md`: new Edge section in the coverage matrix (mark data-availability
     caveats: 2024-25+, goalie families 2025-26+, empty-array semantics).
   - `docs/api/client.md`: `client.edge` examples incl. `compare()`, top-10 param enums, and the
     Goal Visualizer flow with the Referer-header note.
   - `edgework/NHL API Documentation.md`: append an "NHL Edge (Player & Puck Tracking)" section
     documenting the ~28 routes + sprites format so the canonical reference stays complete.
   - Link `docs/research/nhl-edge-endpoints.md` from the Edge docs section as provenance.
4. Run the FULL suite `python -m pytest tests/ -q` — zero failures; report the new test count
   vs. the 817 baseline.

**Done when:** manifest gate green, docs current, full suite passes.
