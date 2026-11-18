<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# BearDog v0.9.0 — Wave 109: Ionic Bond Verification + ACME Phase 3

**Date**: May 22, 2026
**Primal**: bearDog
**Version**: 0.9.0
**Resolves**: primalSpring Wave 38 items 1 and 2

---

## Summary

Two deliverables for bearDog from primalSpring Wave 38:

1. **`crypto.ionic_bond.verify_proposal`** — New IPC method + `proposer_public_key` on propose response. Enables target gates to verify a pending bond proposal's Ed25519 signature before committing to acceptance. Unblocks live ionic bonds between gates.

2. **ACME Phase 3 — renewal daemon** — `needs_renewal()` parses X.509 `notAfter` via `x509-parser`. Order polling, CSR finalization, cert download, and key PEM serialization complete the end-to-end renewal flow. Last piece before Cloudflare removal (S1 formal cutover).

---

## Item 1: Ionic Bond `verify_proposal`

### What changed

| Component | Change |
|-----------|--------|
| `IonicBondProposeResponse` (beardog-types) | Added `proposer_public_key: String` field |
| `IonicBondHandler::handle_verify_proposal` (lifecycle.rs) | New handler: looks up pending proposal, verifies Ed25519 sig, checks TTL |
| `IonicBondHandler::methods()` (mod.rs) | 11 → 12 methods |
| Handler dispatch (mod.rs) | New match arm for `crypto.ionic_bond.verify_proposal` |
| Tests (tests.rs) | 3 new: `verify_proposal_valid`, `verify_proposal_not_found`, `propose_returns_public_key` |

### Response shape

```json
{
  "valid": true,
  "proposal_id": "...",
  "terms_hash": "...",
  "proposer": "gate_a",
  "target": "gate_b",
  "proposer_signature": "...",
  "proposer_public_key": "...",
  "trust_model": "Bilateral",
  "created_at": "2026-05-22T...",
  "expires_at": null,
  "error": null
}
```

---

## Item 2: ACME Phase 3 — Renewal Daemon

### What was stubbed (Phase 2)

- `needs_renewal()` — always returned `false`
- `issue_certificate()` — stopped after challenge submission
- No order polling, no CSR finalization, no cert download

### What's implemented (Phase 3)

| Function | Purpose |
|----------|---------|
| `needs_renewal(pem)` | Parse leaf cert `notAfter` via x509-parser, compare to `now + renewal_days_before_expiry` |
| `poll_order_ready(order)` | Exponential backoff (1-10s), 30 attempts, handles `ready`/`valid`/`invalid` |
| `finalize_order(order)` | Generate Ed25519 key pair, build CSR, POST to `finalize_url`, poll until valid, download cert |
| `download_certificate(order)` | POST-as-GET to `certificate_url` with JWS auth, returns PEM chain |
| `ed25519_private_key_pem(key)` | PKCS8 PEM serialization of private key |
| `build_csr(signing_key, verifying_key)` | Minimal DER CSR with CN + SANs |

### Full renewal loop path

```
run_renewal_loop (12h default interval)
  → check_and_renew (per domain)
    → load_cert → needs_renewal (X.509 notAfter parse)
    → issue_certificate
      → discover_directory → register_account → create_order
      → complete_challenges (HTTP-01)
      → poll_order_ready (exponential backoff)
      → finalize_order (CSR + download)
      → store.store_cert (PEM on disk)
      → [hot_reload.reload_from_store available]
```

### New dependency

- `x509-parser 0.16` in `beardog-acme/Cargo.toml`

---

## Quality Gates

| Gate | Result |
|------|--------|
| `cargo fmt` | Clean |
| `cargo clippy --workspace -- -D warnings` | 0 warnings |
| `cargo test --workspace` | All pass, 0 failures |
| `cargo doc` | Clean |

---

## Files Modified

| File | Change |
|------|--------|
| `Cargo.toml` | Removed `showcase/05-mixed-entropy` from workspace members |
| `crates/beardog-types/src/ionic_bond.rs` | Added `proposer_public_key` to `IonicBondProposeResponse` |
| `crates/beardog-tunnel/src/.../ionic_bond/mod.rs` | Added method + dispatch |
| `crates/beardog-tunnel/src/.../ionic_bond/lifecycle.rs` | New `handle_verify_proposal`, updated `handle_propose` |
| `crates/beardog-tunnel/src/.../ionic_bond/tests.rs` | 3 new tests, method count assertions |
| `crates/beardog-acme/Cargo.toml` | Added `x509-parser` dep |
| `crates/beardog-acme/src/client.rs` | `needs_renewal`, `poll_order_ready`, `finalize_order`, `download_certificate`, `build_csr`, `ed25519_private_key_pem` |
| `crates/beardog-acme/README.md` | Phase status updated |
| `STATUS.md` | Wave 109 entry |
| `CHANGELOG.md` | Wave 109 entry |
