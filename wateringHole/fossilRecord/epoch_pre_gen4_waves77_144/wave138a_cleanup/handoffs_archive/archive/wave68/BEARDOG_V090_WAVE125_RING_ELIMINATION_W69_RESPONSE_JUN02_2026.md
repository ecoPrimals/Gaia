# bearDog v0.9.0 — Wave 125 Handoff
## Ring Elimination + Wave 69 Response
**Date:** Jun 2, 2026
**Commit:** `61b33d9dd`
**Gate:** southGate
**Context:** primalSpring Wave 69 bearDog mission, Wave 68 FRAGO responses

---

## 1. Ring Elimination (P2 — DONE)

Switched TLS crypto backend from `ring` (C) to `aws-lc-rs` across the workspace.

### Changes
| File | Change |
|------|--------|
| Root `Cargo.toml` | `rustls`: `ring` → `aws_lc_rs`; `tokio-rustls`: `ring` → `aws-lc-rs`; `rcgen`: `ring` → `aws_lc_rs` |
| `beardog-acme/Cargo.toml` | `reqwest`: `rustls-tls` → `rustls-tls-webpki-roots-no-provider` |
| `beardog-acme/src/client.rs` | Added `ensure_rustls_crypto_provider()` for explicit provider init |
| `deny.toml` | `ring` banned outright; `aws-lc-rs`/`aws-lc-sys` allowed wrapped by rustls/rcgen |
| `tls.rs` | Doc comment updated to reference aws-lc-rs |

### Verification
- `cargo tree -i ring` → **"nothing to print"** — ring fully eliminated from active dependency graph
- Dormant lockfile entry remains (rustls-webpki optional dep metadata) — not compiled or linked
- All 1159 tests pass, clippy clean

### Note on pure-Rust future
`aws-lc-rs` is still C code (via `aws-lc-sys`). For full pure-Rust sovereignty, the future path is `rustls-rustcrypto` (experimental) + replacing `rcgen` with `p256`/`yasna` for CSR generation. This is Phase 2 when `rustls-rustcrypto` matures.

---

## 2. Wave 68 FRAGO Responses

### Mesh Validation Ready (ACK'd)
- All Wave 67 P0 fixes confirmed DONE (bearDog S4 `5e6b5a5`, Songbird `eb913612`, biomeOS `9ed36983`)
- Waves 119-124 deep debt complete
- southGate ready as mesh validation partner
- Operational deployment (plasmidBin redeploy) pending next window

### Dependency Evolution (ACK'd)
- **sled → redb**: NOT APPLICABLE — bearDog has zero sled dependency (not in Cargo.toml, Cargo.lock, or source)
- **ring elimination**: DONE this wave (Wave 125)
- Songbird also sled-free per Wave 135
- Recommend updating `PURE_RUST_SOVEREIGN_STACK_GUIDANCE.md` bearDog/Songbird rows to DONE

---

## 3. Wave 69 Mission Status

| Mission item | Priority | Status |
|-------------|----------|--------|
| S4 auth partner | P0 | READY — config shipped Wave 119, awaiting ironGate formal gate start |
| ring elimination | P2 | **DONE** — Wave 125 |
| grapheneGate keystore design | P2 | NOT STARTED — `GRAPHENEGATE_BOOTSTRAP_STANDARD.md` not yet published |
| Vault encrypted creds | P3 | DEFERRED to Phase 2 |

---

## 4. Quality Gates

| Gate | Status |
|------|--------|
| `cargo fmt` | ✓ clean |
| `cargo clippy -- -D warnings` | ✓ zero warnings |
| `cargo test` | ✓ 1159 passed, 0 failed |
| `cargo tree -i ring` | ✓ empty (ring eliminated) |
