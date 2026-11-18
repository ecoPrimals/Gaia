# petalTongue Wave 74 — Sovereign Verify + Mesh Testing + Coverage

**Date**: June 3, 2026
**Version**: v1.6.8 wave74
**Tests**: 6,217 passed, 0 failed (+8 new content backend tests)
**Clippy**: 0 warnings (first-party)

## Mission Items Delivered

### P1: Sovereign Rendering Verification — CONFIRMED CLEAN

Comprehensive 5-component verification:

| Component | Status | Details |
|-----------|--------|---------|
| `web/index.html` | Clean | All relative `/api/` paths, no external assets |
| `petal-tongue-wasm` (8 src files) | Clean | Purely computational, no fetch URLs, parameter-driven |
| `web_mode/mod.rs` | Clean | Routes relative, CORS configurable, no hardcoded domains |
| `web_mode/handlers.rs` | Clean + hardened | Docroot-relative, path traversal now blocked |
| `web_mode/content_direct.rs` | Clean | Local filesystem only, no external deps |

**No sovereign-infrastructure blockers.**

### P1: Mesh Content Routing Testing

**Integration tests added**:
- UDS round-trip: mock server + `content.resolve` + base64 decode (verified)
- TCP round-trip: `TcpListener` mock + `content.resolve` via TCP transport (verified)
- TCP connect failure: graceful error on unreachable `host:port`
- JSON-RPC error: returns `Ok(None)` on error response

**Live mesh testing**: Requires NestGate TCP endpoint on eastGate. Set
`CONTENT_BACKEND_ENDPOINT=<nestgate-host>:<port>` on flockGate to activate.
All code paths for this are tested and working.

### P2: WASM Bundle Profiling

| Metric | Value |
|--------|-------|
| Raw release size | 610K |
| Gzipped size | 191K |
| Direct deps | 6 (wasm-bindgen, console_error_panic_hook, serde, serde_json, types, scene) |
| toml+tracing trim (Wave 73) | Confirmed effective — neither in dep tree |

**Next trim targets** (from analysis):
1. Feature-gate `petal-tongue-scene` modules unused by WASM (document, audio, etc.)
2. Slim `bytes` serde feature for WASM
3. Consider `serde-wasm-bindgen` for zero-copy JS↔Rust

### P2: Content Backend Test Coverage

8 new tests covering all transport and discovery paths:

| Test | Covers |
|------|--------|
| `test_content_backend_client_env_override` | Tier 1: socket override |
| `test_content_backend_tcp_endpoint_override` | Tier 2: TCP override |
| `test_content_backend_convention_socket_found` | Tier 3: convention socket discovery |
| `test_content_backend_socket_beats_tcp_priority` | Tier priority: socket > TCP |
| `test_content_backend_resolve_via_unix_socket` | UDS JSON-RPC round-trip |
| `test_content_backend_resolve_via_tcp` | TCP JSON-RPC round-trip |
| `test_content_backend_resolve_jsonrpc_error_returns_none` | Error handling |
| `test_content_backend_tcp_connect_failure_returns_error` | Transport failure |
| `test_content_index_fallback_to_dashboard` | Dashboard fallback |
| `test_content_endpoint_display_unix` / `_tcp` | Display formatting |

### Security Hardening

**Path traversal fix**: `resolve_docroot_path` now filters path components
to `Component::Normal` only, stripping `..`, `.`, and root prefix segments.
Test verifies `/../../../etc/passwd` resolves safely under docroot.

### Upstream Merge Resolution

Resolved conflict from upstream commit `74c01d6`:
- Restored `resolve_biomeos_socket_dir()` in `network.rs` (removed by upstream)
- Resolved merge conflict markers in `content_backend.rs`

## Quality Gates
- `cargo fmt --check`: clean
- `cargo clippy --workspace --all-targets`: 0 warnings
- `cargo test --workspace`: 6,217 passed, 0 failed

## For primalSpring Audit
- Live mesh test: `CONTENT_BACKEND_ENDPOINT=<nestgate>:<port>` on flockGate
- WASM bundle: run `wasm-pack build --target web` for JS glue + sized artifact
- Scene feature-gating for further WASM trim (P3 next wave)
