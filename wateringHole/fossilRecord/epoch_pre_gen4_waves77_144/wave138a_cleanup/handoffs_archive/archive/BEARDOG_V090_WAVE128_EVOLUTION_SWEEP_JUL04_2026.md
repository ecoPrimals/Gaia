# BearDog v0.9.0 — Wave 128 Evolution Sweep Handoff

**Date**: Jul 4, 2026  
**Wave**: 128  
**Gate**: eastGate (local primal)  
**Posture**: Convergence + debt  

---

## Delivered

### Security (P0)
- **Simulated PQC gated** — `quantum_crypto` module behind `#[cfg(any(test, feature = "pqc-simulation"))]`; random-byte keys/signatures no longer exposed in production builds
- **PQC capability ads gated** — `QuantumCrypto` + `quantum_resistant` in HSM config only with feature enabled

### Identity Resolution (P0)
- **`resolve_primal_name()` precedence fixed** — `BEARDOG_PRIMAL_NAME` → `PRIMAL_NAME` → `"beardog"` (was missing prefixed variant)
- **`IdentityHints::from_env()` fixed** — reads prefixed env first, matching family/node ID patterns
- **`get_primal_name_with()` fallback corrected** — uses `resolve_primal_name()` not `env!("CARGO_PKG_NAME")`

### Async I/O Migration (P0)
- **beardog-acme** — `store_cert`, `load_cert`, `save()` → `tokio::fs` (was blocking runtime)
- **beardog-monitoring** — `/proc/stat` + `/proc/meminfo` reads → `tokio::fs::read_to_string`; collectors now async

### Lock Evolution (P0–P1)
- **`std::sync::Mutex` → `parking_lot::Mutex`** — monitoring metrics (3 sites)
- **`Arc<Mutex<SystemTime>>` → `Arc<AtomicU64>`** — BTSP tunnel `last_activity` (lock-free)
- **mDNS stats `Mutex` → `parking_lot::RwLock`** — read-heavy path

### Trust Test Coverage (Wave 128 prior commit)
- 11 new tests: `seed_from_env` (5), `try_verify_bearer` (4), `auth.trust_issuer` auth gate (2)
- Orphan `performance_sentinel` files deleted (~460 LOC)
- DID derivation consolidated to single canonical function

### Error Types (P1)
- `SslKeylogError` → `thiserror` derive

---

## Metrics

| Metric | Value |
|--------|-------|
| Tests | 13,866+ |
| Methods | 229 |
| Coverage | 90.51% |
| Clippy | 0 warnings |
| Unsafe | 0 (forbid) |
| cargo clean | 34.3 GiB reclaimed |

---

## Remaining Debt (noted for upstream review)

| Item | Priority | Notes |
|------|----------|-------|
| `handle_ribocipher_signal` dead code | P3 | `#[expect(dead_code)]` — riboCipher accept-path pending |
| Integration API handlers (501) | P1 | BTSP/BirdSong/lineage REST endpoints stubbed; lower-layer providers exist |
| Installer genome defaults | P1 | `default_genome_targets.txt` lists peer primals; should discover at runtime |
| 40+ Jan 2025 spec headers | P3 | Batch refresh or fossil banner |
| Forgejo CI lighter than GitHub | Note | No deny/coverage/all-targets on sovereign mirror |

---

## Cascade

```
git: ecoPrimals/bearDog main → 8d8e2fa
sporeprint: validation-summary.md updated (13,866+, Jul 4)
upstream: wateringHole/handoffs/archive/ (this file)
```
