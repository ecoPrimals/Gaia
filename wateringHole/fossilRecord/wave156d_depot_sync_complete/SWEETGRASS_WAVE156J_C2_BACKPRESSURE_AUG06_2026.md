# sweetGrass — Cephalization C2 + Backpressure AAR

**Status**: SHIPPED | **Wave**: 156j | **Date**: Aug 6, 2026
**Gate**: eastGate | **Team**: sporeGate
**Commit**: `cefec6b` | **Lines**: +498/-7

---

## Summary

sweetGrass ships the G64 Cephalization dual-socket UDS pattern (C2) and the
convergence backpressure signal designed on westGate. Both features are live
in JSON-RPC and tarpc binary paths.

---

## Delivered

### 1. Dual-Socket UDS Pattern (C2)

| Component | Detail |
|-----------|--------|
| Module | `crates/sweet-grass-service/src/tarpc_uds.rs` |
| Socket | `sweetgrass.tarpc.sock` (alongside `sweetgrass.sock` for JSON-RPC) |
| Transport | `tarpc::serde_transport::unix` — length-delimited bincode |
| Latency | Sub-ms intra-gate (same NUCLEUS primals) |
| Resolution | 5-tier: `SWEETGRASS_TARPC_SOCKET` → `BIOMEOS_SOCKET_DIR/{name}.tarpc.sock` → XDG → TMPDIR → default |
| Lifecycle | Stale socket removed on start. Cleanup on graceful shutdown. |
| Tests | 4 unit tests (resolution: explicit, env, family-scoped, suffix check) |

sweetGrass is now `tarpc-default + dual-socket`, matching songBird (C1a)
and petalTongue (C1b+C2) tier.

### 2. Convergence Backpressure (`convergence.pressure`)

| Aspect | Detail |
|--------|--------|
| Method | `convergence.pressure` (JSON-RPC + tarpc) |
| Input | `filter` (optional QueryFilter), `scan_limit` (default 10,000) |
| Output | `total_scanned`, `converged`, `backlog_by_depth[0..6]`, `pressure` (0.0–1.0), `throttle` (bool) |
| Throttle threshold | pressure > 0.8 |
| Design doc | `SWEETGRASS_CONVERGENCE_BACKPRESSURE_DESIGN.md` (westGate, Wave 156d) |
| Tests | 3 unit tests (empty, all-unconverged, backlog reporting) |

Implements the "passive polling" path from the design document. Download
pipelines (`bulk_braid.py`, `manifest_download.py`, `alphafold_bulk_download`)
can poll `convergence.pressure` to get GO/WAIT/STOP verdicts.

### 3. tarpc Trait Enrichment

Added to `SweetGrassRpc` trait (available over tarpc binary path):
- `convergence_check(data_hash) → {converged, depth}`
- `convergence_pressure(scan_limit) → {total_scanned, converged, pressure, throttle}`

---

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| Methods | 47 + 11 aliases | 48 + 11 aliases |
| Tests | 1,655 | 1,662 |
| Clippy warnings | 0 | 0 |
| tarpc tier | `tarpc-wired` | `tarpc-default + dual-socket` |
| Files > 800L | 0 | 0 |
| Unsafe | 0 | 0 |
| Hardcoded names | 0 | 0 |

---

## Cross-Primal Dependencies

| Dependency | Direction | Status |
|------------|-----------|--------|
| Download pipelines → `convergence.pressure` | Consumers poll sweetGrass | API ready, consumers pending |
| Primals → `sweetgrass.tarpc.sock` | Intra-gate binary RPC | Socket ready, clients pending |

---

## Gaps / Follow-up

1. **C2 client-side wiring**: Other primals need to discover and connect to
   `sweetgrass.tarpc.sock`. Blocked on C6 (sourDough reference impl) defining
   the canonical client pattern.
2. **Active backpressure (future)**: Design doc describes active push via
   `trust.event("backpressure")` through cellMembrane. Current implementation
   is passive polling only.
3. **Download pipeline integration**: westGate scripts need to call
   `convergence.pressure` instead of (or alongside) `os.statvfs`. This is
   westGate team responsibility.

---

## Upstream Impact

- **westGate**: Can now poll `convergence.pressure` for download gating
- **sourDough (C6)**: sweetGrass dual-socket pattern is a reference for
  other primals adopting C2
- **overwatch**: sweetGrass promoted to `tarpc-default + dual-socket` tier
  in depot status

---

*sweetGrass Wave 156j — Cephalization C2 + Backpressure SHIPPED.*
