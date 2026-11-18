# sweetGrass — Wave 49 Ecosystem Tightening

**Date**: May 25, 2026
**From**: sweetGrass team
**Audit**: primalSpring Wave 49 — ecosystem tightening handoff

---

## Vectors Completed

### A. Stale Deployment Patterns (HIGH)
- Removed all `target/release/sweetgrass` references from README.md,
  QUICK_COMMANDS.md (30+ occurrences)
- Updated to `sweetgrass` (plasmidBin binary) or `cargo run -p sweet-grass-service`
- Zero `which sweetgrass` references existed
- `notify-plasmidbin.yml` confirmed active

### B. Local `wateringHole/` Consolidation (MEDIUM)
- No local `wateringHole/` tree — already clean
- Broken `wateringHole/` refs in showcase eliminated by fossilization

### C. Showcase Fossilization (LOW)
- 87 files (1.1 MB) archived to `fossilRecord/primals/sweetGrass/showcase_wave49/`
- Replaced with pointer `showcase/README.md`
- Removed orphaned `.gitignore` showcase rules

---

## Doc Metric Synchronization

Fixed drift between code (37 methods, 1,560 tests, 194 files) and docs:

| File | Issue | Fix |
|------|-------|-----|
| CONTEXT.md | "35 methods across 11 domains" | 37 methods across 12 domains; added `attribution.witness`, `lifecycle.status` |
| README.md | 1,549 tests, 32 methods, 199 files | 1,560 tests, 37 methods, 194 files (55,496 LOC) |
| DEVELOPMENT.md | 1,522 tests | 1,560 tests |
| QUICK_COMMANDS.md | 1,522 tests, `REST_PORT`/`TARPC_PORT` | 1,560 tests, `SWEETGRASS_HTTP_PORT`/`SWEETGRASS_TARPC_ADDRESS` |
| env.example | `TARPC_PORT`/`REST_PORT` | Current `SWEETGRASS_*` env vars |
| sporeprint/validation-summary.md | 1,553 tests, missing domains | 1,560 tests, 37 methods across all domains |

---

## Pipeline Debt: Startup Latency (>8s)

Investigated and documented:
- `health.liveness` is zero-cost (no store queries, sync return)
- Delay is storage backend init (redb/postgres) blocking before listener bind
- Memory backend starts instantly
- Lazy init would require `AppState` architecture refactor — documented as known

---

## Verification Checklist

- [x] No `showcase/` directory (pointer README only)
- [x] No local `wateringHole/` tree
- [x] No `which sweetgrass` or `target/release/sweetgrass` in any file
- [x] `notify-plasmidbin.yml` active
- [x] `notify-sporeprint.yml` active
- [x] All doc metrics synchronized to 37 methods / 1,560 tests / 194 files

---

## Metrics

| Metric | Value |
|--------|-------|
| Version | v0.7.38 |
| Tests | 1,560 local + 56 Docker CI |
| Methods | 37 (12 domains + 10 wire aliases) |
| Source files | 194 `.rs` (55,496 LOC), max 674 lines |
| Clippy | 0 warnings |
| Production debt | 0 findings across 12 audit categories |
