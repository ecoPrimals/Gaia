# footPrint Composition Audit AAR — Wave 136b

**Date**: 2026-07-11
**Gate**: flockGate
**Type**: After Action Report — Deep Debt Pass + Composition Audit
**Scope**: Full codebase audit and evolution of `protists/footPrint`

---

## Summary

flockGate completed a full composition audit and deep debt pass on footPrint —
the first primal composition target. The codebase was audited against 7 quality
axes (completeness, code quality, architecture compliance, test coverage, code
size, sovereignty/licensing, archive status) and all identified issues were
resolved in a single evolution pass.

## Delivered

| ID | What | Detail |
|----|------|--------|
| S1 | Sovereignty fix | AGPL-3.0-or-later LICENSE file added; `package.json` license corrected from MIT |
| S2 | npm audit fix | 11 vulnerabilities → 1 (low severity, esbuild Windows-only dev tooling) |
| H1 | Hardcoding elimination | Created `src/constants.ts` — centralized all URLs, conversion factors, proxy allowlist, cache TTLs, solver tuning |
| H2 | WebSocket URL fix | `agent-bridge.ts` derives WS URL from `location.host` instead of hardcoded `:3000` |
| H3 | Proxy path centralized | All 8 source modules use `PROXY_PATH` from constants instead of inline `/api/proxy` |
| D1 | Dead code pruned | Removed `getMap()` (map.ts, datasources.ts), `isAgentConnected()`, `MLInferenceResult`, `CacheTTLConfig`, `GRID_SPACINGS_FT` |
| D2 | Dead CSS removed | `.modal-input-row` selectors removed (unused) |
| D3 | Missing CSS added | `@keyframes fadeout` added (was referenced by `storage.ts` toast but never defined) |
| R1 | Solver decomposed | 191-line `solveConstraints` → 4 focused functions: `buildSolverState`, `evaluateConstraintErrors`, `gaussNewtonStep`, `applySolverResult` |
| R2 | point-on-line constraint | Implemented with full cross-product error function + Jacobian |
| R3 | RustScript evolution | Fixed tautological `isSome` in discover.ts; removed unused imports |
| R4 | Primal discovery evolved | `primal.ts` gains `onRegistryChange()`, `requireCapability()`, `hasCapability()`, `'Unavailable'` error kind |
| T1 | ESLint config added | `eslint.config.js` — strict TypeScript ESLint (`strictTypeChecked` + `stylisticTypeChecked`) |
| T2 | Prettier config added | `.prettierrc` — consistent formatting baseline |
| T3 | Vitest config added | `vitest.config.ts` — V8 coverage, 80% thresholds on core/rustscript |
| T4 | Test foundation | 46 tests across 7 files (Result, Option, Owned, RustVec, Iter, Primal, Constants) — all passing |
| B1 | Bundle optimization | Vite `manualChunks` splits 819 kB monolith → 3 chunks (app 90 kB, turf 307 kB, leaflet 427 kB) |
| B2 | WS proxy in Vite | Dev server now proxies `/ws` to Express (was broken in dev mode) |
| B3 | Production static serving | Express serves `dist/client/` for production deployment |
| P1 | README rewritten | Reflects actual TypeScript/Vite/ECS architecture (was describing dead vanilla JS stack) |
| P2 | Specs updated | `PROJECT.md`: 7 active constraint types (point-on-line). `PETALTONGUE_VISUAL_TARGETS.md`: npm/Vite (not CDN), constraint parity corrected, broken doc link fixed |
| P3 | .gitignore extended | Added coverage/, .env*, logs, OS cruft |
| P4 | tsconfig.server.json | Explicit `constants.ts` include |
| P5 | package.json scripts | Added lint, format, test, test:coverage, check |

## Verification

| Check | Result |
|-------|--------|
| `tsc --noEmit` | **0 errors** |
| `vitest run` | **46/46 tests pass** |
| `vite build` | **Clean, 1.33s, 3 optimized chunks** |
| `npm audit` | **1 low severity** (esbuild Windows-only) |
| TODO/FIXME/HACK comments | **0 in source** |
| `any` types | **0 across codebase** |

## Files Changed

### New files (14)
- `LICENSE` — AGPL-3.0-or-later with scyBorg triple-license notice
- `.prettierrc` — formatting config
- `eslint.config.js` — ESLint strict TS config
- `vitest.config.ts` — test runner config
- `src/constants.ts` — centralized hardcoded values
- `src/constants.test.ts` — constants validation tests
- `src/core/primal.test.ts` — primal registry tests
- `src/rustscript/result.test.ts` — Result algebra tests
- `src/rustscript/option.test.ts` — Option algebra tests
- `src/rustscript/owned.test.ts` — Owned move-semantics tests
- `src/rustscript/vec.test.ts` — RustVec bounds-checked tests
- `src/rustscript/iter.test.ts` — lazy Iter pipeline tests

### Modified files (26)
- `README.md` — full rewrite
- `package.json` — license, scripts, deps
- `package-lock.json` — ESLint/Prettier/Vitest deps
- `.gitignore` — extended
- `vite.config.ts` — manualChunks, WS proxy
- `tsconfig.server.json` — constants.ts include
- `specs/PROJECT.md` — constraint count fix
- `specs/PETALTONGUE_VISUAL_TARGETS.md` — CDN→npm, constraint parity, doc link
- `public/css/app.css` — dead CSS removed, fadeout keyframes added
- `src/server.ts` — constants import, production static serving
- `src/core/constraints.ts` — decomposed, point-on-line implemented
- `src/core/primal.ts` — runtime discovery evolution
- `src/client/agent-bridge.ts` — WS URL fix, dead export removed
- `src/client/app.ts` — constants import
- `src/client/datasources.ts` — dead getMap() removed
- `src/client/discover.ts` — tautological isSome fixed, constants import
- `src/client/map.ts` — constants import, dead getMap() removed
- `src/client/measurement.ts` — constants import
- `src/client/terrain.ts` — constants import
- `src/client/sources/osm.ts` — constants import
- `src/client/sources/infrastructure.ts` — constants import
- `src/client/sources/fema.ts` — constants import
- `src/client/sources/usgs.ts` — constants import
- `src/client/sources/zoning.ts` — constants import
- `src/client/sources/michigan.ts` — constants import
- `src/client/sources/soils.ts` — constants import, DRY'd WMS URL
- `src/types/api.ts` — dead CacheTTLConfig removed
- `src/types/index.ts` — dead re-exports removed
- `src/types/spatial.ts` — dead MLInferenceResult removed

## Gaps for Upstream Primal Teams

### petalTongue
- **Ready**: footPrint `dist/client/` is a standard static web asset bundle (HTML/CSS/JS, 3 chunks)
- **Action**: Serve from Axum static file server. 12 visual targets documented in `specs/PETALTONGUE_VISUAL_TARGETS.md`
- **Note**: VT-6 constraint parity updated — footPrint now has 7 active types (point-on-line added)

### nestGate
- **Ready**: Project CRUD endpoints mapped (4 endpoints, `ProjectFile` JSON schema in `src/types/project.ts`)
- **Action**: Replace `/api/projects/*` with CAS persistence. Content-address by project content hash
- **Schema**: `ProjectFile` type = `{ layers: SerializedLayers, shapes: SerializedShapeProps[], center: [number, number], zoom: number }`

### songBird
- **Ready**: Proxy allowlist centralized in `src/constants.ts` (10 hosts). Cache TTLs defined per-service
- **Action**: Add drawbridge routing rules for all 10 hosts. Replicate TTL strategy (1d FEMA, 3d Overpass, 7d default, 30d elevation, 90d soils)
- **WebSocket**: Agent bridge protocol defined in `src/agent/protocol.ts` — typed message envelope with discriminated `type` field

### flockGate
- **Ready**: Dev server verified, production build verified, composition surface fully mapped
- **Action**: Host composition on WAN when petalTongue/nestGate/songBird wiring is ready
- **HPC dispatch**: DEM batch elevation (currently rate-limited via USGS EPQS) is the first candidate for LAN compute offload

## Codebase Health Snapshot

| Metric | Value |
|--------|-------|
| Source files | 65 (active) + 7 (test) |
| Source lines | ~8,400 |
| TypeScript errors | 0 |
| `any` types | 0 |
| TODO/FIXME comments | 0 |
| Test count | 46 |
| Bundle size (gzip) | 219 kB (3 chunks) |
| Build time | 1.33s |
| npm vulnerabilities | 1 (low, dev tooling) |
| License | AGPL-3.0-or-later |

---

*flockGate — footPrint composition audit complete. Deep debt resolved. Ready for upstream primal team review and cascade push.*
