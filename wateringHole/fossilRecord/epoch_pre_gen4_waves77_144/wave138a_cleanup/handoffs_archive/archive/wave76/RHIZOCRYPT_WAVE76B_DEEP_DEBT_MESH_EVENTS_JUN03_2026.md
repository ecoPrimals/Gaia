# rhizoCrypt — Wave 76B: Cross-Gate Mesh Events + Deep Debt

**Date**: June 3, 2026
**Version**: 0.14.1
**Gate**: strandGate
**FRAGOs ACKed**: `wave76-parity-sprint-provenance`

---

## Wave 76 Schema Work

### Cross-Gate Mesh Event Types

5 new `EventType` variants in new `mesh` domain (27→32 variants, 8 domains):

| Variant | Fields | Wire Format |
|---------|--------|------------|
| `TrustIssuerRegistered` | `issuer_fingerprint`, `registering_gate` | `{"TrustIssuerRegistered": {"issuer_fingerprint": "a1b2...", "registering_gate": "eastGate"}}` |
| `KeyExchangeCompleted` | `local_gate`, `remote_gate`, `method` | `{"KeyExchangeCompleted": {...}}` |
| `FamilyEnrollment` | `family_id`, `gate`, `primal_count` | `{"FamilyEnrollment": {...}}` |
| `MeshJoin` | `gate`, `mesh_id` | `{"MeshJoin": {...}}` |
| `MeshLeave` | `gate`, `mesh_id`, `reason` | `{"MeshLeave": {..., "reason": "Graceful"}}` |

New supporting enum: `MeshLeaveReason` (`Graceful`, `Disconnected`, `Evicted`, `TrustRevoked`).

7 serialization roundtrip tests added. All 32 variants exhaustively tested.

### Not Yet Wired

Schemas defined + tested. Not connected to bearDog. Wiring when bearDog w135
trust protocol is live on LAN mesh.

---

## Deep Debt Audit Results

### Production Code Quality — Zero Unwrap/Expect

Full audit of all 181 `.rs` files. **Zero `.unwrap()`/`.expect()` in production code.**

The 300+ grep hits (42 in storage.rs, 40 in permanent.rs, 40 in phase3.rs, etc.)
are **100% in `#[cfg(test)]` modules**, confirmed file-by-file.

### Fixes Applied

| Fix | File | Detail |
|-----|------|--------|
| Clippy `#[expect]` consistency | 7 test modules | storage, compute, factory, adapters/mod, adapters/tarpc, capabilities/provenance, metrics — all now have explicit `#[expect(clippy::unwrap_used)]` matching permanent.rs pattern |
| Provenance wire fix | `types_ecosystem/provenance/client.rs` | `unwrap_or_default()` on serde → `map_err()?` for proper error propagation |
| Event test extraction | `event.rs` → `event_tests.rs` | 922L → 539L prod + 390L test |

### Audit Confirmation Table

| Category | Status |
|----------|--------|
| `unsafe` blocks | Zero (`deny` + `forbid` in non-test) |
| `.unwrap()` / `.expect()` in prod | Zero (`deny` enforced) |
| TODO / FIXME / HACK | Zero |
| Production mocks | Zero (all `cfg(test\|test-utils)` gated) |
| C/C++ production deps | Zero (nix is dev-dep only for test signals) |
| Files > 700L (prod) | Zero (max 698L rpc_integration.rs) |
| Hardcoded endpoints | Zero (constants.rs + env-driven config) |
| Stale scripts | Zero (no .sh/.py/.rb in repo) |
| Constants centralized | Yes (`constants.rs` SSOT with derivation docs) |
| Config capability-based | Yes (`from_env_reader` + runtime discovery) |
| `unwrap_or*` in prod | All idiomatic (fallback defaults, type coercions) |

### Dependency Posture

| Aspect | Status |
|--------|--------|
| Production C deps | Zero |
| Dev-only C deps | `nix 0.27` (test signal handling, `cfg(unix)`) |
| Duplicate crates | 6 pairs (all transitive: rand 0.8/0.9, getrandom 0.2/0.3/0.4, cpufeatures 0.2/0.3, hashbrown 0.14/0.17) |
| Root cause | tarpc 0.37 pins rand 0.8; blake3 uses newer cpufeatures |
| Actionable | No — `multiple_crate_versions = "allow"` in workspace lints |
| Unused deps | None detected (ciborium=vertex CBOR, bincode=tarpc transport) |

---

## Files Changed

| File | Change |
|------|--------|
| `crates/rhizo-crypt-core/src/event.rs` | +5 mesh variants, +MeshLeaveReason, test extraction |
| `crates/rhizo-crypt-core/src/event_tests.rs` | NEW — 390L extracted tests |
| `crates/rhizo-crypt-core/src/lib.rs` | Re-export MeshLeaveReason |
| 7 capability client files | Added `#[expect(clippy::unwrap_used)]` |
| `types_ecosystem/provenance/client.rs` | unwrap_or_default → map_err |
| `specs/EVENT_TYPE_REFERENCE.md` | 27→32 variants, mesh domain |
| `specs/00_SPECIFICATIONS_INDEX.md` | Updated variant count |
| Root docs (README, CONTEXT, validation-summary, DEPLOYMENT_CHECKLIST) | Metrics reconciled |
| `CHANGELOG.md` | Wave 76 + deep debt entries |

---

## Metrics

| Metric | Value |
|--------|-------|
| Tests | 1,670 |
| Clippy | 0 warnings |
| Unsafe | 0 blocks |
| `.rs` files | 181 |
| Total lines | ~54,835 |
| Max prod file | 698L |
| TODO/FIXME | 0 |

---

## Upstream Gaps for primalSpring

| Primal | Gap | Detail |
|--------|-----|--------|
| bearDog | Cross-gate wiring pending | rhizoCrypt mesh event schemas ready, need bearDog w135 trust protocol live |
| loamSpine | Anchor schema needed | Should define ledger entries for same 5 mesh event types |
| sweetGrass | Attribution schema needed | Should extend PROV-O for cross-gate provenance braids |
| tarpc upstream | rand 0.8 pin | Causes 6 duplicate crates; bump to 0.9 when tarpc updates |
