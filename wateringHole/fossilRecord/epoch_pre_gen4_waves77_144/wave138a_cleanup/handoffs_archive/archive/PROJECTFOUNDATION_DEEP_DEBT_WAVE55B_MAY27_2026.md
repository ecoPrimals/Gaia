# projectFOUNDATION Deep Debt — Wave 55B (May 27, 2026)

**Commit**: `80bcf20`
**primalSpring**: v0.9.30 (Wave 55 context)
**Pipeline**: 460 methods · 56 scenarios · 185 targets · 30 workloads

## Changes

### Architecture — Discovery Config (Single Source of Truth)
- Created `deploy/discovery_defaults.toml` — all bootstrap port numbers (BearDog
  9100, Songbird 9200, ToadStool 9400, NestGate 9500, rhizoCrypt 9601, loamSpine
  9700, sweetGrass 9850) now in one file instead of scattered as string literals.
- `primal_ipc.sh:discover_port()` reads defaults from TOML when no env/socket
  available. Resolution chain: env → discovery socket → config file → argument.
- `foundation_validate.sh` no longer passes hardcoded port literals.
- `fetch_sources.sh` delegates to `discover_port()` when available.

### Architecture — Report Extraction (547L → was 728L)
- Extracted Phase 8 (report writing, provenance TOML, results JSON, spring folder
  distribution) into `deploy/lib/report_writer.sh` (181 lines).
- Functions: `write_validation_report()`, `write_provenance_toml()`,
  `write_results_json()`, `resolve_workload_spring()`,
  `distribute_to_spring_folders()`.
- `foundation_validate.sh` now 547 lines (approaching but not exceeding 800L
  ceiling for the split policy).

### Dead Code → Live Wiring
- `rpc_has_error()` and `rpc_error_message()` in `json_rpc.sh` were dead code.
  Now wired into provenance WARN paths (DAG session, loamSpine commit, sweetGrass
  braid) for structured error diagnostics instead of raw response dumps.

### Hardcoding Elimination
- **Workload scan dirs**: replaced `groundspring`/`hotspring` hardcoded list with
  dynamic glob of `$WORKLOAD_DIR/*/`.
- **Spring metadata lookup**: added `metadata.spring` as tertiary fallback in
  `resolve_workload_spring()` (after `provenance.upstream_spring` and
  `metadata.spring_upstream`).
- **backfill_hashes.sh thread filter**: now uses `resolve_thread_manifests()`
  from `thread_registry.sh` for registry-driven filtering instead of substring
  match. Falls back to substring only for unregistered shorts.

### Dependency Unification
- **blake3_hash**: `primal_ipc.sh` now includes full Python fallback
  (`blake3` PyPI module) when `b3sum` is absent. All scripts that source
  `primal_ipc.sh` inherit the unified function. `fetch_sources.sh` keeps a
  standalone fallback for independent execution.

### Workload Env Defaults
- All 6 airspring workloads now use
  `${AIRSPRING_ROOT:-${SPRINGS_ROOT:-${ECOPRIMALS_ROOT}/springs}/airSpring}`
  (was bare `${AIRSPRING_ROOT}` without fallback).

### CI Expansion
- **Shell library fixture tests**: new CI step exercises `json_rpc.sh`
  (`rpc_has_result`, `rpc_has_error`, `rpc_error_message`, `rpc_extract_field`)
  and `thread_registry.sh` (`list_thread_shorts`, `resolve_thread_dir`) against
  known inputs.
- shellcheck now covers `deploy/lib/report_writer.sh`.

### Minor
- SRA fetcher skip message clarified to mention `sra-tools: fasterq-dump`.
- `fetch_sources.sh` NESTGATE_PORT resolved via `discover_port()` when sourced.

## Files Changed (13)

| File | Change |
|------|--------|
| `deploy/discovery_defaults.toml` | **NEW** — bootstrap port defaults |
| `deploy/lib/report_writer.sh` | **NEW** — extracted Phase 8 module |
| `deploy/foundation_validate.sh` | -181L Phase 8 extraction, config-driven ports |
| `deploy/lib/primal_ipc.sh` | Config-driven discover_port, unified blake3_hash |
| `deploy/lib/json_rpc.sh` | No changes (functions were already there) |
| `deploy/backfill_hashes.sh` | Registry-driven thread filter |
| `deploy/fetch_sources.sh` | Unified blake3, discovery-aware port, SRA message |
| `.github/workflows/ci.yml` | Shell fixture tests, report_writer shellcheck |
| `workloads/thread06_ag/airspring-*.toml` (×6) | Env fallback defaults |

## Open Items

| ID | Item | Blocker |
|----|------|---------|
| FN-1 | BLAKE3 backfill (threads 4, 5, 1-remaining) | `.data/` fetch + b3sum |
| FN-2 | SRA fetcher implementation | sra-tools dependency decision |
| FN-3 | Thread 5 LTEE — 4 targets pending | ferment braids (Era 3) |
| FN-4 | Thread 1 WCM live Nest gate run | Nest Atomic on irongate |
| FN-5 | Rust CLI elevation (Phase B) | primalSpring CompositionContext |
| FN-6 | Python inline consolidation | 24× `python3 -c` across scripts |
| FN-7 | `resolve_workload_spring` prefix fallback | Should derive from THREAD_INDEX |

## Upstream Notes

- **primalSpring**: validate `compute.execute` capability matches toadStool
  canonical registry.
- **biomeOS**: skunkbat and biomeOS `neural_api` are in graph TOML but not
  health-checked by `foundation_validate.sh` — either add health checks or
  document as optional-only.
- **toadStool**: direct-exec fallback in Phase 5 bypasses scheduler — should
  match toadStool validate interface exactly.
