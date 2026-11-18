# rhizoCrypt Wave 155n — G31 Batch Provenance Pipeline

**Date**: Aug 4, 2026 | **Wave**: 156d | **Head**: `ed67a9d`

## Summary

G31 batch provenance pipeline foundation for rhizoCrypt. Adds batch-optimized
append, concurrent multi-session dehydration, and a coordinated pipeline ingest
method to support 10× faster bulk ingestion (38 datasets, PDB 220K structures).

## What Shipped

| Component | Change |
|-----------|--------|
| `append_vertices_batch()` | Single session lock for N vertices (amortized lock overhead) |
| `append_batch` RPC auto-routing | Same-session batches use optimized path automatically |
| `dehydrate_batch()` | Concurrent multi-session dehydration via JoinSet |
| `dag.dehydration.trigger_batch` | JSON-RPC + tarpc for batch dehydration |
| `dag.pipeline.ingest` | Coordinated create + batch append + optional dehydrate |
| `notify_dehydration_batch()` | Single JSON-RPC with array of summaries (N→1 round-trips) |
| `BatchDehydrateResult` | Per-session success/failure reporting |
| `PipelineIngestRequest/Response` | Wire types for coordinated ingest |
| METHOD_CATALOG | 2 new methods (39 total) |
| Capability registry | 2 new capabilities + provenance wire aliases |

## Architecture

```
Bulk ingestion (before G31):
  client → N × (create_session → append_event × M → dehydrate → notify)
  = N × (1 + M + 2) round-trips per dataset

Bulk ingestion (after G31):
  client → 1 × pipeline.ingest(events=M, dehydrate=true)
  = 1 round-trip per dataset (session created server-side)

Multi-session dehydration:
  client → 1 × dehydration.trigger_batch(session_ids=[...])
  = 1 round-trip, concurrent execution server-side
```

## Metrics

| Metric | Value |
|--------|-------|
| Tests | 1,785 (all green) |
| Source files | 214 `.rs` (-11 dead) |
| Lines | ~59,500 |
| Coverage | 93.83% |
| Clippy | 0 warnings |
| cargo deny | CLEAN |
| Cross-compile | 4 targets, zero warnings |
| Methods | 39 (METHOD_CATALOG) |
| Head | `ed67a9d` |

## Deep Debt (Wave 155n late)

- **12 pre-existing test failures fixed**: BTSP FAMILY_ID env leaked from gate deployment into tests
- 7 deps updated to latest patches, pedantic clippy sweep clean
- `#[allow]`/`#[expect]` audit: all justified with reason strings
- Zero debt markers, zero hardcoded values, zero mocks in production
- Root docs + crate READMEs: 6 stale "37 methods" refs corrected to 39, CHANGELOG heading hierarchy fixed
- Stability tiers updated: 31 stable, 8 evolving (was 6 — added `trigger_batch`, `pipeline.ingest`)
- Debris audit: zero scripts, zero stale files, zero empty files, `cargo clean` 28.5 GiB reclaimed

## Wave 156d — Root Doc Cleanup + Debris Audit (Aug 4, 2026)

- Stale metrics scrubbed from DEPLOYMENT_CHECKLIST (1,914→1,785 tests, 225→214 files, Wave 151b→156c)
- Stale metrics scrubbed from RHIZOCRYPT_SPECIFICATION (1,914→1,785 tests)
- Stale frontmatter scrubbed from validation-summary.md (1,914→1,785 tests, date updated)
- Debris audit: zero backup/temp/log/empty/orphan files, proptest-regressions valid (7 lines)
- False-positive scan: zero stale TODOs in `.rs`, 1 valid spec evolution item (`Arc<str>`), operator checklists correct
- `cargo clean`: 20,935 files, 14.9 GiB reclaimed

## Wave 156c — RPC Integration Port Isolation + Deep Debt Gate (Aug 4, 2026)

- **Port collision fix**: live `rhizocrypt` on port 19501 caused test to connect to gate instance; remapped all 10 tarpc test ports to 197xx
- `temp_env::with_vars(BTSP_CLEAR_ENV)` isolation on all tarpc integration tests
- `cargo update`: regex-automata 0.4.16 → 0.4.17
- Full deep debt gate: 0 clippy warnings, fmt clean, deny clean, 0 unsafe, 0 debt markers, cross-compile clean (windows-gnu, musl)

## Wave 156b — Batch Notify Wire + Dead Code Purge (Aug 4, 2026)

- **`notify_dehydration_batch` wired**: `dehydrate_batch()` now sends 1 sweetGrass RPC (was N per-session)
- `dehydrate_core()` private method: shared pipeline for single + batch callers
- `RpcClient`: add `dehydrate_batch()` + `pipeline_ingest()` typed API
- Deploy graph + MCP tools: 3 batch capabilities + `dag.partial_dehydrate` added
- **Dead vendor HTTP purge**: 5 modules, 11 files, ~4,100 lines, 132 dead tests removed

## What Remains for G31

rhizoCrypt's batch foundation is **SHIPPED**. Remaining for full G31:

1. **loamSpine**: batch commit API for multi-summary permanent storage
2. **sweetGrass**: `contribution.record_dehydration_batch` endpoint to consume batch notifications
3. **Orchestration**: biomeOS pipeline graph wiring batch ingest across all three primals
4. **Validation**: westGate PDB 220K structure bulk ingest at production scale

## Upstream Status

| Item | Status |
|------|--------|
| Batch append (single lock) | **SHIPPED** |
| Batch dehydration (concurrent) | **SHIPPED** |
| Pipeline ingest (coordinated) | **SHIPPED** |
| Batch provenance notify | **SHIPPED** |
| METHOD_CATALOG + registry | **SHIPPED** |
| 14 tests | **PASSING** |
| Cross-primal batch orchestration | Needs loamSpine + sweetGrass + biomeOS |
