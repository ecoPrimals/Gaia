# cellMembrane Wave 151b — BTSP ClientHello Evolution + Deep Debt Sweep

**Date**: 2026-07-26 | **Wave**: 151b | **Author**: cellMembrane team (sporeGate)
**Trigger**: Sub-wave 151b — all primals evolve to BTSP standard before Nest Atomic

---

## Summary

cellMembrane now implements the BTSP `ClientHello` 4-step handshake for all
bearDog UDS communication, matching the songBird reference implementation.
Post-BTSP deep debt sweep eliminates remaining hardcoding, bumps `getrandom`
to 0.4, and preventively extracts tests from files approaching 800L.

## BTSP Architecture

New module: `btsp_client.rs` (sync + async handshake variants)

**Handshake protocol:**
1. Client → `ClientHello { protocol: "btsp", version: 1, client_ephemeral_pub }`
2. Server → `ServerHello { challenge, session_id }`
3. Client → `ChallengeResponse { session_id, hmac: HMAC-SHA256(BTSP_KEY, challenge) }`
4. Server → `HandshakeComplete { cipher, session_id }`

**Key derivation:** `HKDF-SHA256(FAMILY_SEED, "ribocipher-v1", "btsp-challenge")`
— distinct from riboCipher mito key (`"mito-signal"` info param).

## Deep Debt Sweep

| Debt Item | Resolution |
|-----------|-----------|
| `gateway/shadow.rs` inline `"lab.primals.eco"` | → `LAB_DOMAIN` constant |
| `gate/enroll.rs` IP fallback `"10.13.37.1"` | → `DEFAULT_HUB_MESH_IP` constant + `mesh_address()` |
| `post_sync.rs` 791L (approaching 800L) | Tests extracted → `post_sync_tests.rs` (716L) |
| `plasmid/mod.rs` 788L (approaching 800L) | Tests extracted → `mod_tests.rs` (662L) |
| `getrandom` 0.2 | → 0.4 (`getrandom()` → `fill()`, 2 call sites) |

## Changed Files

| File | Change |
|------|--------|
| `btsp_client.rs` | **NEW** — 11 tests, sync + async handshake, key derivation, HMAC |
| `plasmid/signing.rs` | BTSP handshake before `crypto.sign_ed25519`, fallback to plain |
| `impulse/primal.rs` | BTSP for bearDog sockets, riboCipher for others, `is_beardog_socket()` |
| `jsonrpc.rs` | `call_btsp()` — async BTSP-aware JSON-RPC variant |
| `tower/timer.rs` | bearDog probe uses `probe_socket_btsp()` instead of `probe_socket()` |
| `lib.rs` | Register `btsp_client` module |
| `gateway/shadow.rs` | Domain literal → `LAB_DOMAIN` constant |
| `gate/enroll.rs` | IP fallback → `DEFAULT_HUB_MESH_IP` + `mesh_address()` chain |
| `gate/nucleus.rs` | `getrandom::getrandom()` → `getrandom::fill()` |
| `service/constants.rs` | New `DEFAULT_HUB_MESH_IP` constant |
| `temporal/post_sync.rs` | Tests extracted to `post_sync_tests.rs` (791→716L) |
| `plasmid/mod.rs` | Tests extracted to `mod_tests.rs` (788→662L) |
| `Cargo.toml` | `getrandom` 0.2 → 0.4 |

## Health Metrics

| Metric | Value |
|--------|-------|
| Tests | 1,167 (was 1,156) |
| Production unwraps | 0 (575 test-only) |
| Unsafe code | 0 (`#![forbid(unsafe_code)]`) |
| Files >800L | 0 (largest 745L) |
| Clippy warnings | 0 |
| Format drift | 0 |

## Codebase Audit Summary (Post-151b)

| Category | Count | Notes |
|----------|-------|-------|
| Production `.unwrap()` | 0 | 575 test-only |
| Production `.expect()` | 7 | All crypto/HMAC — key length guaranteed valid |
| `unsafe` code | 0 | Workspace forbid |
| TODO/FIXME/HACK | 0 | |
| Production mocks | 0 | |
| Files >800L | 0 | Largest: `dispatch/gate.rs` at 745L |
| `as` casts (production) | 6 | All guarded by compile-time assertions |

## For Upstream Primal Teams

cellMembrane BTSP status: **DONE**. Reference the songBird implementation
(`btsp_client.rs` in songBird) or cellMembrane's `btsp_client.rs` for the
handshake pattern. Key requirements:
- `FAMILY_SEED` env var must be available at runtime
- Signal prefix `[0xEC, 0x03]` before handshake
- HMAC-SHA256 with HKDF-derived key (not raw FAMILY_SEED)

## Deployment Actions (sporeGate team)

1. `cargo build --release -p membrane-shadow` — rebuild with `getrandom` 0.4
2. Deploy to all gates via `membrane plasmid.harvest && membrane plasmid.refresh`
3. Verify BTSP handshake with `membrane tower.status` (bearDog probe should show LIVE)
