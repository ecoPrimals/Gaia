# SweetGrass — Wave 142b: TransportEndpoint Phase 2

**Date**: Jul 16, 2026  
**Wave**: 142b  
**Commit**: `7596df1`  
**Status**: SHIPPED  

---

## Summary

Phase 2 "Abstraction over Gating" complete for sweetGrass. All raw UDS
callsites now dispatch via `TransportEndpoint` — the same pattern shipped
by petalTongue's `petal-tongue-platform` (ref: `1af1a98`).

Connection code no longer contains `#[cfg(unix)]` branches. Platform dispatch
is handled internally by `connect_transport()` based on the endpoint variant.

---

## Changes

### `sweet-grass-store-nestgate/src/client.rs`
- `NestGateClient` now holds `endpoint: TransportEndpoint` instead of `socket_path: PathBuf`
- `new(endpoint, family_id)` — accepts any `TransportEndpoint`
- `from_socket_path(path, family_id)` — backward-compatible convenience
- `endpoint()` — exposes structured endpoint for logging/introspection
- `call()` — transport-agnostic; dispatches UDS/TCP/mesh via internal `connect()`

### `sweet-grass-service/src/transport_connect.rs`
- **New**: `send_jsonrpc(endpoint, request, timeout)` — transport-agnostic JSON-RPC utility
- **New**: `try_liveness_probe(endpoint)` — shared liveness probe (replaces 3 duplicate impls)
- **New**: `resolve_capability_endpoint(domain, socket_dir)` — discovery: env JSON → UDS fallback
- **New**: `PROBE_TIMEOUT` constant (3s)

### `sweet-grass-service/src/neural_announce.rs`
- `announce_to_neural_api(own_endpoint: &TransportEndpoint, version)` — no longer UDS-only
- `resolve_neural_api_endpoint()` — checks `NEURAL_API_ENDPOINT` (JSON) first, then UDS
- Payload now includes structured `endpoint` field (serde-serialized `TransportEndpoint`)
- Tests include TCP mock (platform-agnostic)

### `sweet-grass-service/src/handlers/health/mod.rs`
- `check_integrations` — no more `#[cfg(unix)]`/`#[cfg(not(unix))]` split
- `probe_integration` — uses `resolve_capability_endpoint` + `try_liveness_probe`

### `sweet-grass-service/src/handlers/jsonrpc/composition.rs`
- `probe_capability_in_dir` — evolved from raw `UnixStream` to `resolve_capability_endpoint`
- All `#[cfg(unix)]` removed from probe functions

### `sweet-grass-service/src/bin/service.rs`
- `spawn_neural_announce` helper — resolves own endpoint based on bind mode
- Platform-correct: UDS on Unix, TCP on non-Unix or `tcp_only` mode

---

## Discovery Order (new)

### Capability Endpoints
1. `CAPABILITY_{DOMAIN}_ENDPOINT` env var (JSON `TransportEndpoint`)
2. `{socket_dir}/{domain}.sock` exists → UDS endpoint (Unix only)

### Neural API
1. `NEURAL_API_ENDPOINT` env var (JSON `TransportEndpoint`)
2. `NEURAL_API_SOCKET` env var → UDS endpoint
3. `{BIOMEOS_SOCKET_DIR}/neural-api-{family}.sock`
4. `{XDG_RUNTIME_DIR}/biomeos/neural-api-{family}.sock`
5. `{temp_dir}/biomeos/neural-api-{family}.sock`

---

## Verification

```
cargo clippy --all-features --all-targets -- -D warnings  → 0 warnings
cargo test --all-features                                  → 1,608 pass / 0 fail
cargo check --target x86_64-pc-windows-gnu                → clean
cargo fmt --all -- --check                                 → clean
```

---

## Ecosystem Alignment

| Primal | Phase 2 Status |
|--------|---------------|
| petalTongue | SHIPPED (reference, `1af1a98`) |
| sweetGrass | **SHIPPED** (`7596df1`) |
| squirrel | Phase 2 |
| rhizoCrypt | Phase 2 |
| biomeOS | Phase 2 (TCP fallback exists) |
| loamSpine / coralReef / skunkBat / barraCuda | Phase 2 |

---

*Wave 142b: sweetGrass TransportEndpoint Phase 2 complete. Abstraction over gating.
petalTongue + sweetGrass shipped. Remaining primals can follow same pattern.*
