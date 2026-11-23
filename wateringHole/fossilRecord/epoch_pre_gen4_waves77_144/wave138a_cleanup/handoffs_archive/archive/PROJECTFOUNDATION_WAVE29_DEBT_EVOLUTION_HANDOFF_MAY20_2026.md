# projectFOUNDATION — Wave 28-29 Absorption + Debt Evolution Handoff

**Date**: May 20, 2026
**From**: projectFOUNDATION
**To**: primalSpring, projectNUCLEUS, plasmidBin
**Commits**: `8a19090`, `b0a0c62`

## Context

primalSpring issued Waves 28-29 (sporePrint pappusCast, cellMembrane Nest
Atomic). projectFOUNDATION has no direct Wave 28-29 gaps — SP-4, CM-1–CM-4
belong to projectNUCLEUS and plasmidBin. However, this pass resolves
significant local debt identified during the audit review and prepares
sporePrint integration.

## Resolved Items

### 1. Typed IPC Parsing (commit `8a19090`)

All `grep '"result"'` patterns in `foundation_validate.sh` replaced with
typed Python JSON-RPC helpers:

- `rpc_has_result()` — check for successful result field
- `rpc_extract_field()` — extract typed field from result
- `rpc_has_error()` / `rpc_error_message()` — error handling

Library: `deploy/lib/json_rpc.sh` (new, 105 lines)

### 2. Structured Workload Result Parsing (commit `8a19090`)

`grep -c '[OK]'` / `[FAIL]'` / `[SKIP]'` replaced with `parse_workload_results()`.
Supports both legacy tag counting and JSON-line structured output
(`{status: "PASS", target_id: ...}`). Workloads can evolve incrementally.

### 3. Runtime Thread Registry (commit `8a19090`)

`deploy/lib/thread_registry.sh` reads `lineage/THREAD_INDEX.toml` at runtime.
Three parallel thread-resolution mechanisms (THREAD_MAP in fetch_sources.sh,
case block in target_compare.sh, thread_registry.sh) unified onto single source.

### 4. Dead Code Removal (commit `b0a0c62`)

170 lines of unreachable `fetch_thread*` functions removed from
`fetch_sources.sh`. Manifest-driven dispatch was sole code path since Wave 24;
legacy functions were dead but documented as "fallback."

### 5. results.json Emission (commit `b0a0c62`)

Phase 8 now produces `results.json` (schema: `foundation-validation-result/v1`):

```json
{
  "schema": "foundation-validation-result/v1",
  "session": "...", "thread": "...", "date": "...",
  "results": { "ok": N, "fail": N, "skip": N, "target_hits": N, "target_misses": N },
  "provenance": { "dag_session_id": "...", "merkle_root": "...", "braid_urn": "..." },
  "degradation": { "trio_state": "full|dag_spine|dag_only|standalone" }
}
```

Copied into spring-dated folders alongside `provenance.toml` and `braid.json`.
This is the primary machine-readable artifact for sporePrint metric ingestion.

### 6. sporePrint Wave 28 Readiness (commit `b0a0c62`)

- Created `sporeprint/validation-summary.md` (Zola-compatible Tier 2 content)
- Flipped `notify-sporeprint.yml` payload to `content: "true"`
- No upstream blocker — content feeds sporePrint auto-merge when SP-1 lands

### 7. Additional Fixes

| Fix | Detail |
|-----|--------|
| Phase 4 dedup | Removed catch-all `find` re-registration; manifest-only now |
| Spring-folder export | Added wetSpring, neuralSpring routing; copies results.json |
| XDG socket consistency | All paths use `${XDG_RUNTIME_DIR:-/tmp}/ecoPrimals/` |
| Gate name configurable | `GATE_NAME` / `NUCLEUS_GATE` env vars |
| Workload skip coverage | 29/29 workloads have `[skip]` section |
| BASECAMP_PAPER_MAP | Paper 02: 11 NCBI + 4 Dryad anchors aligned with thread05_ltee.toml |
| Safe command execution | JSON-array-to-bash-array in toadStool fallback |
| Stale docs | data/README.md, deploy/README.md, validation/README.md counts corrected |
| CI extensions | Workload skip coverage gate, shellcheck for json_rpc + thread_registry |

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| deploy/lib/ files | 2 | 4 |
| fetch_sources.sh LOC | 609 | 369 |
| Dead code (unreachable functions) | 170 lines | 0 |
| Thread resolution mechanisms | 3 | 1 (THREAD_INDEX.toml) |
| Phase 8 output formats | 2 (md + toml) | 3 (md + toml + json) |
| sporePrint content | metrics only | Tier 2 lab pages |

## projectFOUNDATION Status Summary

| # | Gap | Priority | Status |
|---|-----|----------|--------|
| FN-1 | BLAKE3 backfill (Thread 1 WCM) | MEDIUM | **10/25 hashed** — 15 unfetchable documented |
| FN-5 | Thread 1 WCM CI validation | MEDIUM | **RESOLVED** — 3 CI gates operational |
| Wave 28 | sporePrint content contribution | LOW | **READY** — `sporeprint/` + content=true |

## Upstream Dependencies

- **SP-1** (sporePrint auto-merge): blocks foundation content appearing on primals.eco
- **CM-1** (membrane --composition nest): no foundation dependency
- **NestGate content.put** (SP-4): blocks sovereign publishing of validation artifacts
