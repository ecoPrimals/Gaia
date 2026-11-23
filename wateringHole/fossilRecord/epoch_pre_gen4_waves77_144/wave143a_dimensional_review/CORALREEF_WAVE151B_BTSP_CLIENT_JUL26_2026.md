<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# coralReef — Wave 151b BTSP Client Handshake (July 26, 2026)

## Commit

`9f7f40e` on `main` (preceded by `13bf1a0` feat commit)

## Summary

Implements songBird-style BTSP `ClientHello → ServerHello →
ChallengeResponse → HandshakeComplete` wire protocol per
`BTSP_PROTOCOL_STANDARD` v1.0 for coralReef. Part of Sub-Wave 151b:
all primals evolve to BTSP standard before Nest Atomic.

All crypto operations delegated to security provider via
`btsp.session.create` and `btsp.session.verify` RPCs — coralReef
never handles raw key material.

## Changes

### New: `btsp_client.rs` (~260 lines)

| Item | Purpose |
|------|---------|
| `BtspSession` | Authenticated session result (`session_id` + `cipher`) |
| `BtspClientError` | Typed errors: I/O, JSON, Protocol |
| `handshake_on_stream_sync()` | 7-step wire handshake on already-connected stream |
| `provider_rpc()` | Sync JSON-RPC helper for security provider |
| `read_json_line()` | Byte-by-byte reader (avoids BufReader buffering) |
| `write_json_line()` | Newline-delimited JSON writer |

### Modified: `provenance.rs`

`try_sign()` now:
1. Checks `btsp::btsp_mode()` — if Production, discovers security provider
2. Calls `btsp_client::handshake_on_stream_sync()` before `crypto.sign` RPC
3. Logs session details on success; returns `None` on failure (unsigned provenance)
4. Development mode unchanged (plain JSON-RPC)

### Modified: `btsp.rs`

`discover_security_socket()` elevated from `fn` to `pub fn` for
cross-module access by `btsp_client` and `provenance`.

### Wire Protocol Alignment

Uses songBird-standard params:
- `btsp.session.create`: `{ family_seed_ref: "env:FAMILY_SEED", role: "client" }`
- `btsp.session.verify`: `{ session_id, client_ephemeral_pub, server_ephemeral_pub, challenge, role: "client" }`

## Quality Gates

- `cargo fmt --check` — PASS
- `cargo clippy --all-features -- -D warnings` — PASS (zero warnings)
- `cargo check --target x86_64-pc-windows-gnu` — PASS (zero warnings)
- `cargo test --all-features` — PASS (3700 total, 0 failures, 4 ignored)

## Remaining BTSP Work

| Item | Status |
|------|--------|
| Client handshake for `crypto.sign` | **DONE (Wave 151b)** |
| Server-side incoming ClientHello support | Deferred — current first-byte guard works for existing peers |
| Ecosystem registry BTSP (`capability.register` etc.) | Low priority — not bearDog direct |
| `FAMILY_SEED` passthrough to provider | Done via `family_seed_ref: "env:FAMILY_SEED"` |
