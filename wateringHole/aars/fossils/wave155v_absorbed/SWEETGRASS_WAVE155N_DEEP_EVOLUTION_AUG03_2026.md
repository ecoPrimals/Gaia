# sweetGrass — Deep Evolution AAR (Wave 155n+)

**Date**: 2026-08-03  
**Primal**: sweetGrass  
**Version**: v0.8.0  
**Gate**: eastGate  
**Status**: DH-0 CLEAN — Zero debt, zero unsafe, zero hardcoded names

---

## Summary

Executed comprehensive deep debt elimination and evolution pass on sweetGrass
following completion of the G31 batch provenance pipeline. All identified debt
items resolved to zero.

## Changes Shipped

### Architecture Evolution

| Change | Impact |
|--------|--------|
| **Zero-copy `Arc<str>` evolution** | `Witness` (6 fields), `LoamAnchor.spine_id`, `EcoPrimalsAttributes.session_ref` → O(1) clone on every braid copy/serialization path |
| **`primal_names::names` module** | Canonical primal identifiers (`LOAMSPINE`, `NESTGATE`, `BEARDOG`, `SONGBIRD`) for socket filenames without hardcoding |
| **`#[non_exhaustive]` enums** | `TransportEndpoint` + `CrossGateTrustEvent` forward-compatible for new variants |
| **BTSP protocol validation** | `ServerHello.version` mismatch now rejected; `HandshakeError.error` surfaced in rejection messages |

### Code Quality

| Metric | Before | After |
|--------|--------|-------|
| Hardcoded primal strings | 6 sites | 0 |
| `#[expect(dead_code)]` in prod | 3 | 0 |
| Files >800L | 1 (806L) | 0 (max 804L from test isolation) |
| Production code max | 806L | 545L |
| Tests | 1,644 | 1,645 |
| Methods | 40 → 42 | 42 |
| Clippy warnings | 0 | 0 |

### New Environment Variable Constants

Added to `primal_names::env_vars`:
- `LOAMSPINE_SOCKET` — ledger provider socket override
- `BEARDOG_UDS_REQUIRE_BTSP` — BTSP enforcement flag
- `BTSP_STRICT_MODE` — ecosystem-wide BTSP mode

### Files Touched

- `crates/sweet-grass-core/src/braid/types.rs` — split to 545L + `types_tests.rs`
- `crates/sweet-grass-core/src/braid/mod.rs` — module declaration
- `crates/sweet-grass-core/src/braid/cross_gate.rs` — `#[non_exhaustive]`
- `crates/sweet-grass-core/src/dehydration.rs` — `Witness` → `Arc<str>`
- `crates/sweet-grass-core/src/primal_names.rs` — `names` module + new env vars
- `crates/sweet-grass-core/src/transport.rs` — `#[non_exhaustive]`
- `crates/sweet-grass-service/src/btsp_client.rs` — consume dead_code + use env constants
- `crates/sweet-grass-service/src/btsp/server.rs` — test env isolation
- `crates/sweet-grass-service/src/ledger_client.rs` — use `names::LOAMSPINE`
- `crates/sweet-grass-service/src/transport_connect.rs` — wildcard match arm
- `crates/sweet-grass-store-nestgate/src/client.rs` — wildcard match arm
- `crates/sweet-grass-store-nestgate/src/discovery.rs` — use `names::NESTGATE`
- Multiple test files — `Arc<str>` assertion updates

## Upstream Gaps / Coordination

### For rhizoCrypt team
- `DehydrationSummary.source_primal` and `.session_id` remain `String` (wire boundary).
  If rhizoCrypt evolves to send `Arc<str>`-compatible wire data, no sweetGrass change needed — serde handles it transparently.

### For nestGate team
- `TransportEndpoint` is now `#[non_exhaustive]`. Any new variants (e.g. `Quic`, `P2P`) will require a `_ => ...` arm in downstream match statements — already done in sweetGrass.

### For ecosystem
- `primal_names::names` module establishes the canonical registry of primal identifiers for socket filename construction. Other primals should adopt this pattern rather than hardcoding strings.

## Validation

```
cargo fmt --all --check     → clean
cargo clippy --all-features → 0 warnings
cargo test --all-features   → 1,645 passed, 0 failed
cargo deny check            → clean
```

## Next Steps (sweetGrass perspective)

- **No P0/P1 issues** — sweetGrass is DH-0 clean
- E2E integration testing with live loamSpine on westGate (when available)
- Cross-gate attribution with northGate data (next trio convergence)
- Property testing expansion for `Arc<str>` witness roundtrips

---

*Filed from eastGate overwatch. Ready for upstream audit via golgiBody cascade.*
