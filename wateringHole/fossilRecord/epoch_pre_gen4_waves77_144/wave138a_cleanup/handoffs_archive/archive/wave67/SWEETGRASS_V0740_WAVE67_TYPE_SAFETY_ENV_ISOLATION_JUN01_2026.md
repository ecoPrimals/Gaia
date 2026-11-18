# sweetGrass v0.7.40 — Wave 67: Type Safety + Handler Env Isolation

**Date**: 2026-06-01
**Gate**: strandGate
**Wave**: 67 (glacial cutover audit response)

---

## Summary

Responds to Wave 67 glacial cutover audit and strandGate gate deployment impulse.
Two categories of work: (1) remaining handler env-read debt from Wave 63,
(2) `Timestamp` newtype evolution for cross-crate type safety.

Additionally: full provenance trio assessment completed (rhizoCrypt v0.14.0,
loamSpine v0.9.16, sweetGrass v0.7.40) with integration gap analysis.

---

## Changes

### Handler Environment Isolation (completes Wave 63 pattern)

Wave 63 fixed `capability.list` by snapshotting `tcp_transport_active` and
`btsp_required` into `AppState`. Two handler paths were missed:

1. **`composition.*_health`** — `probe_capability()` read `BIOMEOS_SOCKET_DIR`,
   `XDG_RUNTIME_DIR`, `TMPDIR` on every request to locate capability sockets.
   Now uses `AppState.socket_dir` (snapshotted at construction).

2. **`health_detailed`** — `check_integrations()` read `DISCOVERY_ADDRESS` on
   every request. Now uses `AppState.discovery_address` (snapshotted at
   construction).

**Files changed:**
- `crates/sweet-grass-service/src/state.rs` — added `socket_dir: PathBuf`,
  `discovery_address: Option<String>`, `snapshot_socket_dir()`
- `crates/sweet-grass-service/src/handlers/jsonrpc/composition.rs` — handlers
  use `state.socket_dir`; old DI functions gated `#[cfg(test)]`
- `crates/sweet-grass-service/src/handlers/health/mod.rs` — `check_integrations`
  reads from state; old `check_integrations_with_reader` removed
- `crates/sweet-grass-service/src/handlers/health/tests.rs` — tests use state

**Env reads in handlers**: 0 (was 2 in composition + 1 in health)

### Timestamp Newtype Evolution

`Timestamp` evolved from `pub type Timestamp = u64` (bare alias) to a proper
newtype struct:

```rust
#[derive(Copy, Clone, Debug, Default, PartialEq, Eq, PartialOrd, Ord, Hash,
         Serialize, Deserialize)]
#[serde(transparent)]
pub struct Timestamp(u64);
```

API: `Timestamp::now()`, `Timestamp::new(nanos)`, `Timestamp::ZERO`,
`Timestamp::nanos()`, `From<u64>`, `Display`.

Wire-compatible via `#[serde(transparent)]` — no protocol changes.

**Impact**: 25+ struct fields, 6 crates, 25 test files updated. Prevents
accidental mixing of nanosecond timestamps with arbitrary integers or
second-precision values (which was happening in integration test code using
`chrono::Utc::now().timestamp()` seconds vs `current_timestamp_nanos()`
nanoseconds).

**Files changed** (production): `braid/types.rs`, `braid/mod.rs`, `activity/mod.rs`,
`primal.rs`, `factory/mod.rs`, `factory/contribution.rs`, `session/mod.rs`,
`provo/mod.rs`, `memory/filter.rs`, `store-postgres/store/mod.rs`,
`store-postgres/store/row_mapping.rs`, `signer/tarpc_client.rs`,
`signer/testing.rs`, `anchor/mod.rs`

### Provenance Trio Assessment

Completed full assessment of trio wiring readiness:

| Primal | Version | Tests | Coverage | Status |
|--------|---------|-------|----------|--------|
| rhizoCrypt | v0.14.0 | 1,654 | 93.88% | Wire-ready |
| loamSpine | v0.9.16 | 1,533 | 90.92% | Wire-ready |
| sweetGrass | v0.7.40 | 1,565 | — | Attribution sink ready |

**Identified gaps for v0.8.0:**
- No outbound JSON-RPC clients for rhizoCrypt/loamSpine in integration crate
- `pipeline.attribute` is a stub (empty merkle root + commit ref)
- `contribution.record_provenance` handler not implemented
- `anchoring.verify` returns `pending_integration`
- No cross-primal E2E integration tests

---

## Metrics

| Metric | Before (v0.7.39) | After (v0.7.40) |
|--------|-------------------|-------------------|
| Version | 0.7.39 | 0.7.40 |
| Tests | 1,565 | 1,565 |
| LOC | 55,718 | 55,825 |
| Clippy | 0 warnings | 0 warnings |
| Env reads in handlers | 3 | 0 |

---

## Verification

```
cargo clippy --all-targets --all-features -- -D warnings  # 0 warnings
cargo test --all-features                                  # 1565 passed, 0 failed
```
