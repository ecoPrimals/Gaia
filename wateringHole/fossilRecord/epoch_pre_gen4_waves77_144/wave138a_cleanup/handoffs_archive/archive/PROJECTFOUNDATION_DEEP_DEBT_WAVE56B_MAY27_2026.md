# projectFOUNDATION — Deep Debt Wave 56B

**Date:** 2026-05-27
**Commit:** `a7bc0b7` (main)
**primalSpring context:** Wave 56, v0.9.30

## Summary

Post-Wave-56 deep debt sweep targeting hardcoding elimination, fail-closed
semantics, CI expansion, and documentation completeness.

## Changes

### 1. Centralized environment bootstrap (`deploy/lib/env.sh`)

New sourced library resolves `ECOPRIMALS_ROOT`, `SPRINGS_ROOT`, `NUCLEUS_ROOT`,
`PLASMIDBIN_DIR`, and `FAMILY_ID` from environment or discovery socket.
Previously these were set inconsistently (or not at all) across the three deploy
entrypoints. All three (`foundation_validate.sh`, `fetch_sources.sh`,
`backfill_hashes.sh`) now source `env.sh` as their first library.

### 2. Graph-driven health checks

The Phase 1 health-check loop in `foundation_validate.sh` no longer contains
hardcoded primal names or port assignments. Instead it iterates
`graphs/foundation_validation.toml` nodes, reading `name`, `health_method`,
and `required` from the graph. Ports are resolved per-node via `discover_port()`
at check time. The Songbird HTTP `/health` special case is eliminated — all
primals now use the `health_method` declared in the graph TOML.

### 3. BLAKE3 no-hash stub removed

`blake3_hash()` in both `primal_ipc.sh` and `fetch_sources.sh` now returns
exit code 1 when neither `b3sum` nor `blake3` Python module is available.
All callers in `fetch_sources.sh` handle the failure gracefully: the fetch
still counts as successful but NestGate registration is skipped (no corrupt
digest stored in provenance).

### 4. API rate limiting

Added configurable inter-request delays for UniProt (`UNIPROT_DELAY`, default
0.5s) and KEGG (`KEGG_DELAY`, default 0.5s) fetchers. NCBI nucleotide and
BioProject already had `NCBI_DELAY`.

### 5. CI fixture test expansion

The "Shell library fixture tests" step now covers:

- `discover_port` — config file fallback (nestgate→9500, rhizocrypt→9601),
  env override, explicit default parameter
- `discover_socket` — empty return when no socket exists, env override with
  a real mock Unix socket
- `_rpc_uds` — send/receive JSON-RPC over mock socket
- `blake3_hash` — failure on nonexistent file
- `DISCOVERY_FALLBACK_COUNT` — counter incremented after fallback resolution

### 6. Documentation completeness

- `workloads/README.md`: added sections for threads 3, 5, 8, 9, 10 (was
  missing 10 of 29 workloads)
- `COMPOSITION_GAPS.md`: fixed stale 30→29 workload count
- Root `README.md` and `deploy/README.md`: updated lib count 5→6, added
  `env.sh` to library tables
- `FOUNDATION_VALIDATE_ELEVATION_REVIEW.md`: updated to 6 libs, ~740 LOC,
  graph-driven health description

## Pipeline State

| Metric | Value |
|--------|-------|
| Workload TOMLs | 29 (10 threads + 2 cross-cutting) |
| Source manifest entries | 76+ across 10 files |
| Validation targets | 185 across 11 files |
| Deploy lib modules | 6 (`env`, `primal_ipc`, `json_rpc`, `thread_registry`, `target_compare`, `report_writer`) |
| CI gates | 17 |

## Open Items

| ID | Item | Status |
|----|------|--------|
| FN-1 | BLAKE3 backfill threads 4, 5, 1 | Blocked on `.data/` fetch |
| FN-5 | Rust elevation Phase B | Unblocked by Wave 56 |
| NC-1 | Thread 10 spore ingest | Code COMPLETE (v3.81) — gated on VPS deploy |

## Upstream Notes

- **primalSpring**: all health methods in `foundation_validation.toml` are
  `health.liveness` — confirm this is the canonical method across all primals
  (previously Songbird used HTTP GET `/health`)
- **toadStool**: env expansion in workload TOMLs (`${SPRINGS_ROOT}`) remains
  undocumented — `COMPOSITION_GAPS.md` Gap 8
- **biomeOS**: `FAMILY_ID` discovery via `family.id` JSON-RPC on discovery
  socket — confirm method name in v3.77+
