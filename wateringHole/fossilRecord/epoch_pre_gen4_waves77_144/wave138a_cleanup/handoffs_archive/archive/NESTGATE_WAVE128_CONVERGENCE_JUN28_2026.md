# NestGate Wave 128 — Convergence + Debt (eastGate overwatch)

**Date**: 2026-06-28  
**Primal**: nestGate (v0.5.0)  
**Atomic**: Nest (sporeGate)  
**Author**: eastGate overwatch (agentic, primalSpring)

---

## Summary

Wave 128 convergence pass from eastGate overwatch. Focuses on silent stub
elimination, provenance depth wiring (P1 from blurb), and discovery honesty.
No new features — stabilization only.

**Build status**: PASS — 12,885 tests passed, 0 failures, 420 ignored, clippy/fmt clean.

---

## Changes

### P0: Silent Stub Elimination

| Item | Before | After |
|------|--------|-------|
| Discovery `announce_via_mechanism` (mDNS, DNS-SD, Consul) | `debug!("not yet implemented"); Ok(())` — silent success | `anyhow::bail!("not yet wired")` — honest error |
| Metrics collector 6 historical methods | `Ok(vec![])` / `Ok(HashMap::new())` | `Err(NestGateError::not_implemented(...))` |
| tarpc `discover_capability` on failure | `warn!(); Ok(Vec::new())` — callers see "no services" | `Err(NestGateRpcError::InternalError {...})` |
| S3 object_storage `list_datasets`/`list_snapshots` | `info!("deferred"); Ok(Vec::new())` | `Err(NestGateError::not_implemented(...))` |
| File-level `#[expect(clippy::unnecessary_wraps)]` | Blanket suppression on knowledge.rs | Removed — no longer needed after announce fix |

### P1: Provenance Depth (Nest ledger → 5+)

#### Content CAS sidecar lineage

- `content.put` now accepts `parent_hash` (string) and `derivation_depth` (u64) in params or `metadata` object
- `derivation_depth` defaults to 1 when `parent_hash` is present, 0 otherwise
- Both fields persisted in `.meta.json` sidecar and returned via `content.get`
- `SIDECAR_PROVENANCE_KEYS` extended from 5 → 7 fields

#### Bonding ledger depth tracking

- `bonding.ledger.store` auto-increments `ledger_depth` counter per contract
- Depth persisted in `__depth.json` alongside record files
- `ledger_depth` and `ledger_timestamp` injected into each stored record
- `bonding.ledger.retrieve` returns `ledger_depth` in response envelope
- `bonding.ledger.list` filters `__depth.json` from `record_types` output

#### Depth semantics

| Surface | Max depth | Mechanism |
|---------|-----------|-----------|
| Content CAS | Unbounded (caller-supplied chain) | `parent_hash` + `derivation_depth` fields |
| Bonding ledger | Unbounded (auto-incremented) | `__depth.json` counter per contract |
| Combined | 5+ achievable | 3 bond lifecycle stages + 2+ content derivations |

### Test Updates

- `realtime_metrics_collector_new_and_helpers` → `realtime_metrics_collector_historicals_return_not_implemented`
- `bonding_ledger_multiple_record_types` → `bonding_ledger_multiple_record_types_with_depth` (asserts depth 1→2→3)
- `bonding_ledger_round_trip` — extended to verify `ledger_depth` in store/retrieve responses

---

## Audit Summary

Full deep debt audit (4 dimensions) completed via explore subagent:

| Dimension | Status |
|-----------|--------|
| Silent stubs | 4 P0 items fixed this wave; remaining are explicit 501s or dev-stubs-gated |
| Discovery honesty | announce mechanisms now fail explicitly; discover returns `Ok(None)` (correct "not found" semantic) |
| Provenance depth | Schema extended; depth 5+ achievable via bond lifecycle + content derivation chains |
| File sizes | Zero files >800L; 25 files 600-779L identified for optional future splits |

---

## Remaining Items (for upstream teams)

- **`#[must_use]` gaps**: `init_config`, `JsonRpcClient::connect_*`, `StorageService::new`, 14 `linux_proc.rs` helpers
- **Clone optimization**: Discovery caches could use `Arc<DiscoveredPrimal>` instead of full clones
- **ZFS REST parity**: ~25 explicit 501 endpoints in HTTP handlers (ZFS, collaboration, load testing, dashboard)
- **Stale docs**: `docs/DEPLOYMENT_GUIDE.md`, `docs/api/REST_API.md`, `docs/architecture/COMPONENT_INTERACTIONS.md` moved to fossilRecord in sweep x6
- **Trio integration**: rhizoCrypt/loamSpine/sweetGrass provenance verification paths not yet wired (cross-primal)

---

## File Change Summary

```
10 files modified
Discovery: 1 file (knowledge.rs — announce honesty + lint cleanup)
Metrics: 2 files (collector.rs + tests.rs)
tarpc: 1 file (tarpc_server/mod.rs)
Object storage: 1 file (operations.rs)
Content: 1 file (content_handlers.rs — provenance depth)
Bonding: 1 file (bonding_handlers.rs — ledger depth)
Docs: 2 files (STATUS.md, handoff)
```
