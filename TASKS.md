# Task List: Complete NHL Endpoint Coverage

Derived from the planner's implementation plan. Execute tasks in order — each builds on the prior. After each task, run the unit test suite (`python -m pytest tests/ -x -q`, no live network) before moving on. Keep public method names/return types unless explicitly noted; add deprecated aliases where behavior is corrected.

---

## Task 1 — Foundation: endpoint registry + HTTP client (plan steps 1–2)

**Files:** `edgework/endpoints.py`, `edgework/http_client.py`, plus URL-construction tests

1. Reconcile `edgework/endpoints.py` against `edgework/NHL API Documentation.md`:
   - Add every documented Web API and Stats API endpoint to the registry.
   - Fix the invalid `club-stats-season/{team}/{season}/{game_type}` entry to the documented `club-stats/{team}/{season}/{game-type}` route.
   - Give endpoint keys consistent domain-oriented names; explicitly distinguish Web API vs. Stats API routes.
   - Preserve existing keys as aliases if removal would break compatibility.
2. Extend `HttpClient` URL construction so Stats requests can target:
   - Language-prefixed resources (`/{lang}/franchise`).
   - Non-language/root endpoints (`/ping`).
   - Alternate language values (not just `en`).
3. Preserve `get(..., web=True/False)` behavior for existing callers; keep query params in `params` (never embedded in route strings).
4. Tests: Web URLs, default-English Stats URLs, alternate-language Stats URLs, root Stats routes, stripping of legacy `rest/`/`en/` prefixes, and the special OpenAPI path (see Task 3).

**Done when:** registry covers all documented endpoints; URL tests pass.

---

## Task 2 — Team + schedule coverage (plan steps 3–4)

**Files:** `edgework/clients/team_client.py`, `edgework/clients/schedule_client.py`, `edgework/models/team.py`, tests

1. `TeamClient`:
   - Add `/club-stats-season/{team}` and `/roster-season/{team}` methods (raw season metadata where no model exists).
   - Correct team lookup to `/team/id/{id}` in `TeamClient.get_team()` **and** model-level lazy loading in `edgework/models/team.py`.
2. `ScheduleClient`:
   - Add `/club-schedule/{team}/month/{month}` and `/club-schedule/{team}/week/{date}` methods; keep existing `now` methods; share request/model conversion via a private helper.
   - Validate/normalize month/date inputs consistently with the API's expected formats.
3. Reuse a shared season-normalization helper (no new inline `YYYY-YYYY` conversions).
4. Tests: route corrections (`/team/id/{id}`), month/week schedules, season normalization, regression that prior public methods still construct the same requests except the explicit fixes.

**Done when:** team + schedule routes implemented and tested.

---

## Task 3 — Game, watch, OpenAPI, glossary & shifts (plan steps 5–6, 11)

**Files:** `edgework/clients/game_client.py`, `edgework/clients/network_client.py`, `edgework/clients/utility_client.py`, `edgework/clients/shift_client.py`, `edgework/edgework.py`, tests

1. `GameClient`: add
   - `/ppt-replay/goal/{game-id}/{event-number}`
   - `/ppt-replay/{game-id}/{event-number}`
   - `/wsc/play-by-play/{game-id}`
2. `NetworkClient`: implement real `/where-to-watch`; keep `/partner-game/{country-code}/now` methods separate and accurately named (they are NOT where-to-watch).
3. `UtilityClient`: add OpenAPI retrieval for `/model/v1/openapi.json` — must not double-prefix `/v1` (coordinate with Task 1 URL construction).
4. Implement `ShiftClient` as the canonical `/shiftcharts` wrapper (game ID + documented filters); have `GameClient`/`Game` delegate or share a route/query builder; retain existing public game shift methods.
5. Instantiate `GlossaryClient` and `ShiftClient` in the `Edgework` facade.
6. Tests: replay/WSC routes, where-to-watch vs. partner-game distinction, OpenAPI path correctness, shiftcharts through both facade and game, glossary exposure.

**Done when:** all game/network/utility/glossary/shift endpoints live and tested.

---

## Task 4 — Stats API resource families, reports, leaders (plan steps 7–9)

**Files:** `edgework/clients/stats_client.py`, `edgework/models/stats.py`, new `edgework/stats_reports.py`, tests

1. Extend `StatsClient` with all missing documented resources:
   - `/{lang}/players`, `/{lang}/leaders/skaters/{attribute}`, `/{lang}/milestones/skaters`, `/{lang}/skater`
   - `/{lang}/leaders/goalies/{attribute}`, `/{lang}/milestones/goalies`
   - `/{lang}/draft`, `/{lang}/franchise`, `/{lang}/componentSeason`, `/{lang}/season`
   - `/{lang}/game`, `/{lang}/game/meta`, `/{lang}/config`, `/{lang}/country`
   - `/{lang}/content/module/{templateKey}`, `/ping`
2. Accept documented filters/sorting/pagination/language via named args + optional escape hatch for extra query params; keep everything in `params` for correct encoding.
3. New `edgework/stats_reports.py` — single source of truth for skater/goalie/team report names; make `StatsClient`, `SkaterStats`, `GoalieStats`, `TeamStats` validate against it.
4. Leaderboards: expose `categories` and `limit` on current + historical methods; remove/deprecate the unused `game_type` arg on current-season methods.
5. Return raw dicts/lists where no stable model exists.
6. Tests: every accepted report name + rejection of unsupported ones; leaderboard single/multi-category and limit boundary queries; one route/param-encoding assertion per new resource.

**Done when:** Stats API coverage complete per docs.

---

## Task 5 — Config model, shared helpers, dedup (plan steps 10, 12)

**Files:** `edgework/models/config.py`, `edgework/models/game.py`, possibly new `edgework/validation.py`, tests

1. Replace no-op `Config.fetch_data()` with a real fetch from Stats `/config`, following `BaseNHLModel` lazy-load conventions. Don't store the local `API_PATH` registry as server config.
2. Add small internal helpers (endpoint formatting, season normalization, Stats query assembly) — only if no suitable helper exists — and migrate code where it prevents route drift. No wholesale rewrite.
3. Mark duplicate client/model endpoint access as intentional delegation (comments), e.g. `models/game.py` WSC/shift paths.
4. Tests: config lazy fetch; delegation paths produce identical routes to their client counterparts.

**Done when:** config works and route duplication is centralized/delegated.

---

## Task 6 — Coverage contract, docs, final validation (plan steps 13–16)

**Files:** new `tests/endpoint_manifest.py`, new `tests/test_endpoint_coverage.py`, `docs/api/nhl-apis.md`, `docs/api/client.md`, `edgework/NHL API Documentation.md`, tests

1. `tests/endpoint_manifest.py`: declarative mapping of every canonical documented endpoint → implementing client method. Composite helpers and duplicate model accessors excluded (unique server routes only).
2. `tests/test_endpoint_coverage.py`: assert every registry entry appears in the manifest and every manifest entry references an existing method. Optional non-blocking live-OpenAPI comparison behind explicit opt-in.
3. Expand mocked tests so every documented route asserts: host+path, path-param substitution, query encoding, Web-vs-Stats routing, return type. Edge cases: dates, seasons, team abbrevs, game/event IDs, language, pagination, invalid report names.
4. Docs:
   - `docs/api/nhl-apis.md`: full Web + Stats coverage matrix.
   - `docs/api/client.md`: current facade examples (`client.players`, `client.games`, `client.stats`, `client.glossary`, `client.shifts`), return types, language handling, raw-response methods, partner-game vs. where-to-watch.
   - Mark APIs as unofficial; describe how endpoint availability is verified.
   - Fix known route discrepancies in `edgework/NHL API Documentation.md` if it stays the canonical local reference.
5. Run the full unit suite; confirm the manifest reports zero undocumented/unimplemented canonical routes.

**Done when:** coverage contract green, docs current, full test suite passes.
