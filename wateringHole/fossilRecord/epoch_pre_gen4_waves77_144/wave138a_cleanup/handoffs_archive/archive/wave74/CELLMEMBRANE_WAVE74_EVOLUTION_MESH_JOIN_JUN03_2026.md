# cellMembrane Wave 74+ — Evolution Sprint + Mesh Join

**Date:** 2026-06-03
**Owner:** ironGate
**Wave:** 74
**Status:** COMPLETE

---

## Summary

Two concurrent deliverables:

1. **ironGate Mesh Join** — ironGate joined the plasmodium collective as the 3rd gate
2. **Deep Debt Evolution** — eliminated all remaining `#[allow]` annotations, evolved types to modern patterns

---

## 1. ironGate Mesh Join (Operational)

ironGate now runs BearDog + Songbird locally and participates in the 3-gate plasmodium mesh.

### Verification Results

| Check | Result |
|-------|--------|
| BearDog running | OK — UDS socket at `/tmp/biomeos/beardog-default.sock` |
| Songbird running | OK — UDS socket + federation :7700 |
| `discovery.peers` | 2 peers (east-gate, strand-gate) |
| `mesh.health_check` | `all_healthy: true` for both peers |
| `capability.call` | HTTP POST JSON-RPC validated (Songbird fix `d6a6f714`) |
| Capability symlinks | security, btsp, crypto, discovery, orchestration — all OK |

### Critical Fix Consumed

Songbird commit `d6a6f714` (pulled from Forgejo):
- TCP → HTTP POST for JSON-RPC cross-gate communication
- `mesh_seed` auto-bootstrap from `SONGBIRD_PEERS`
- String format for `mesh.init` (comma-separated peers)
- `latency_ms` population in health checks

### Configuration

```env
SONGBIRD_PEERS=eastgate.local:7700,strandgate.local:7700
SONGBIRD_FEDERATION_PORT=7700
SECURITY_PROVIDER_SOCKET=/tmp/biomeos/beardog-default.sock
BEARDOG_FAMILY_SEED=<from ~/.config/biomeos/family/.beacon.seed>
```

---

## 2. Deep Debt Evolution (Code)

### Changes

| File | Change |
|------|--------|
| `plasmid.rs` | `fetch()` decomposed: `fetch_primals()`, `format_dry_run()`, `format_fetch_outcome()`. `#[allow(too_many_lines)]` removed. `FetchResult` +Clone, `FetchSource` +Display |
| `config.rs` (types) | `HardeningConfig` — 5 bools with `#[allow(struct_excessive_bools)]` → `HardeningStep` enum + `disabled_steps: Vec`. Extensible, capability-driven |
| `dispatch/data.rs` | NestGate content path evolved to `NESTGATE_CONTENT_PATH` env-overridable |

### Metrics

| Metric | Before | After |
|--------|--------|-------|
| `#[allow]` in production | 2 | **0** |
| Clippy warnings | 0 | **0** |
| Tests | 210 | **210** |
| `unsafe` | 0 | 0 |
| `unwrap()` in prod | 0 | 0 |
| All files < 800L | yes | yes |

---

## Dependencies / Coordination

- **Consumed:** Songbird `d6a6f714` (southGate/eastGate delivered)
- **Consumed:** BearDog family seed (already deployed locally)
- **Upstream impact:** None — all changes local to cellMembrane crate
- **No upstream gaps identified**

---

## Runbook Reference

Mesh join procedure documented in `gardens/cellMembrane/RUNBOOKS.md` §12.
