# Songbird Wave 67 — P0 BLOCKER Resolved: Security Socket Fix

**Date**: June 1, 2026  
**Wave**: 67 (Glacial Cutover Phase 0)  
**Priority**: P0 BLOCKER → RESOLVED  
**Gate**: southGate  

---

## Issue

`songbird_http_client` hardcoded `/tmp/neural-api-*.sock` as the security socket
fallback path. When `BEARDOG_SOCKET` or `--security-socket` was set on southGate,
`SecurityRpcClient::from_env()` ignored it in Neural API mode, falling back to
a non-existent `/tmp` path. This blocked:

- Federation TLS (cross-gate encrypted channels)
- `capability.call` routing across gates
- eastGate ↔ southGate `discovery.peers` validation

## Fix

### `SecurityRpcClient::from_env()` — New Discovery Chain

1. `$SECURITY_PROVIDER_ENDPOINT` (CLI `--security-socket` flag)
2. `$NEURAL_API_SOCKET` (explicit socket path)
3. `$SECURITY_PROVIDER_SOCKET` (capability-first naming)
4. `$BEARDOG_SOCKET` (backward-compatible — southGate standard)
5. XDG runtime socket (`$XDG_RUNTIME_DIR/biomeos/neural-api-{family}.sock`)
6. TCP discovery file
7. `/var/run/biomeos/neural-api.sock` (VPS fallback — DH-1 compliant)

### `discover_neural_api_socket()` (both http-client + crypto-provider)

Same env-first chain. `BEARDOG_SOCKET` and `SECURITY_PROVIDER_SOCKET` now
honored before XDG/VPS fallback. Zero `/tmp` writes.

### `discover_security_socket()` (both crates)

Final fallback changed from `$TMPDIR/security-provider.sock` to
`/var/run/biomeos/security.sock`.

## Files Changed

| File | Change |
|------|--------|
| `crates/songbird-http-client/src/security_rpc_client/core.rs` | `from_env()` → `discover_neural_api_endpoint()` with full env chain |
| `crates/songbird-http-client/src/crypto/socket_discovery.rs` | `discover_neural_api_socket()` + `discover_security_socket()` DH-1 compliant |
| `crates/songbird-http-client/src/crypto/security_provider/mod.rs` | Collapsed `if` for clippy compliance |
| `crates/songbird-http-client/src/security_rpc_client/mod.rs` | Doc examples updated (no `/tmp`) |
| `crates/songbird-http-client/tests/security_rpc_client_e2e_tests.rs` | E2E tests use env-based socket discovery |
| `crates/songbird-crypto-provider/src/socket_discovery.rs` | `discover_neural_api_socket_with()` + `discover_security_socket_with()` DH-1 compliant |

## Verification

- `cargo check --workspace` — clean
- `cargo clippy --workspace` — zero warnings
- `cargo test -p songbird-http-client --lib` — 441 passed
- `cargo test -p songbird-crypto-provider --lib` — 56 passed
- `cargo fmt --all` — clean

## Next Steps (Phase 1)

After this fix lands on southGate:
1. Set `BEARDOG_SOCKET` in the southGate systemd environment
2. eastGate runs `discovery.peers` smoke test (eastGate ↔ southGate)
3. eastGate runs `s_covalent_mesh` live validation

## DH-1 Status

All socket discovery paths in Songbird are now `/tmp`-free:
- Data paths: `$XDG_DATA_HOME/songbird` → `/var/lib/songbird`
- Cache paths: `$XDG_CACHE_HOME/songbird` → `/var/cache/songbird`  
- Security sockets: `$BEARDOG_SOCKET` → XDG → `/var/run/biomeos/`
- Neural API sockets: `$NEURAL_API_SOCKET` → XDG → `/var/run/biomeos/`

`ProtectSystem=strict` compatible on VPS membrane.
