<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# LoamSpine — Wave 157a: Vertebrate Evolution Self-Audit

**Date**: August 9, 2026  
**Wave**: 157a  
**From**: sporeGate (loamSpine team)  
**Status**: SHIPPED — self-audit complete, abstractions extracted

---

## What Shipped

### RPC Self-Audit — 54/54 Methods Verified

Full cross-reference of actual JSON-RPC dispatch against `capability_registry.toml`:

| Surface | Registry | Implemented | Match |
|---------|----------|-------------|-------|
| JSON-RPC methods | 54 | 54 | **100%** |
| tarpc methods | 37 | 37 | **100%** |
| Legacy aliases | 8 | 8 | Correctly undeclared |

**One fix applied**: `domains.waypoint` → `domains.slice` in `capability_registry.toml` to match the wire prefix (`slice.anchor`, `slice.checkout`).

**loamSpine does NOT have the P0-B problem** (nestGate phantom API). Every declared method has a working implementation.

### Vertebrate Abstraction: `persist_tip` Helper

New `LoamSpineService::persist_tip(&self, spine: &Spine) -> LoamSpineResult<&Entry>` method extracts the canonical post-append sequence:

```rust
// Before (repeated 18 times across 8 service modules):
let appended = spine.tip_entry()
    .ok_or_else(|| LoamSpineError::Internal("tip empty after append".into()))?;
self.entry_storage.save_entry(appended).await?;
self.spine_storage.save_spine(&spine).await?;

// After:
self.persist_tip(&spine).await?;
```

Applied in: `mod.rs`, `integration.rs` (6), `waypoint.rs` (3), `anchor.rs` (2), `trust_ledger.rs`, `bond_ledger.rs`, `certificate.rs` (2), `certificate_loan.rs` (3), `certificate_escrow.rs`.

### Vertebrate Abstraction: Attestation IPC Consolidation

`DiscoveredAttestationProvider::jsonrpc_call` reduced from ~40 lines of hand-rolled NDJSON framing to shared `ndjson_rpc_call` helper. Connect timeout preserved.

### Cross-Focus Audit

| Area | Verdict |
|------|---------|
| BTSP handshake | Consumer/orchestrator — delegates crypto to bearDog via IPC |
| Trust ledger | Ledger storage — stores events, doesn't verify trust |
| Braid/attribution | Records commits — doesn't compute braids |
| Content/CAS | No blob CAS — spine permanence only |
| Signing | Consumer — delegates to `crypto.sign_ed25519` via UDS |
| Mocks | All `#[cfg(test)]` or `#[cfg(any(test, feature = "testing"))]` — zero production mocks |

**Only borderline items**: `btsp_client.rs` local HMAC (documented bootstrap workaround), `get_attribution`/`get_provenance_chain` (reasonable permanence-layer read queries).

### Signing Path Ready for bearDog P0-A

`JsonRpcCryptoSigner` → `crypto.sign_ed25519` via capability-discovered UDS. No hardcoded socket paths. `consumed.signing` correctly declared in `capability_registry.toml`. When bearDog rebuilds with actual Ed25519 signing, loamSpine's `session.commit` will work without code changes.

---

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| Tests | 1,796 | **1,796** (no test change — abstractions are behavioral-neutral) |
| Source files | 215 | **215** |
| Duplicated persist pattern | 18 sites | **1** (helper + 18 call sites) |
| Hand-rolled IPC | 2 paths | **1** (attestation consolidated) |
| Registry mismatches | 1 (waypoint≠slice) | **0** |
| Clippy | 0 | 0 |
| Fmt | clean | clean |
| Doc | 0 warnings | 0 warnings |

---

## Files Changed

| File | Change |
|------|--------|
| `config/capability_registry.toml` | `domains.waypoint` → `domains.slice` |
| `crates/loam-spine-core/src/service/mod.rs` | Added `persist_tip` helper, used in `append_prepared_entry` |
| `crates/loam-spine-core/src/service/integration.rs` | 6 sites → `persist_tip` |
| `crates/loam-spine-core/src/service/waypoint.rs` | 3 sites → `persist_tip` |
| `crates/loam-spine-core/src/service/anchor.rs` | 2 sites → `persist_tip` |
| `crates/loam-spine-core/src/service/trust_ledger.rs` | 1 site → `persist_tip` |
| `crates/loam-spine-core/src/service/bond_ledger.rs` | 1 site → `persist_tip` |
| `crates/loam-spine-core/src/service/certificate.rs` | 2 sites → `persist_tip` |
| `crates/loam-spine-core/src/service/certificate_loan.rs` | 3 sites → `persist_tip`, removed unused `EntryStorage` import |
| `crates/loam-spine-core/src/service/certificate_escrow.rs` | 1 site → `persist_tip`, removed unused `EntryStorage` import |
| `crates/loam-spine-core/src/discovery/mod.rs` | `jsonrpc_call` → `ndjson_rpc_call` (−40 LOC) |
| Root docs | Changelog, roadmap |

---

## Commit

```
15559e7..HEAD on main
```

---

## What's Next for loamSpine

- **bearDog P0-A unblock**: When bearDog ships Ed25519 signing, `session.commit` will work. loamSpine is ready.
- **swarmVine integration**: `cas.have` data gossip (future wave).
- **v0.10.0 targets**: Signing capability middleware, collision layer validation.
- **Depot rebuild**: After P0s resolve and G68 convergence completes.

---

*Wave 157a VERTEBRATE EVOLUTION — loamSpine self-audit complete. 54/54 RPC methods verified against registry (zero phantom APIs). `persist_tip` helper abstracts 18-site pattern. Attestation IPC consolidated. Cross-focus clean. Signing path ready for bearDog P0-A. 1,796 tests, 215 source files.*
