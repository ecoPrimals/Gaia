# AAR: songBird Wave 111 — riboCipher + Deep Debt Evolution

**Date**: 2026-06-13  
**Primal**: songBird  
**Commits**: `053163f3`, `7b0cac77`, `a0062f95`  
**Tests**: 8,929 (was 8,918)

---

## Stream 7: riboCipher Transport Signal Detection

Implemented the `RIBOCIPHER_TRANSPORT_SIGNAL_STANDARD` convergent evolution across all 3 accept loops:

### Insertion points

| Loop | File | Detection method |
|------|------|-----------------|
| pure_rust_server | `connection.rs` `handle_connection_with_peek` | `fill_buf` peek before `{`/BTSP fork |
| bin_interface | `ipc_session.rs` `handle_connection` | `fill_buf` peek before `read_line` |
| http_server (federation) | `http_server.rs` accept loop | `tcp_stream.peek` before TLS/HTTP |

### Signal bytes

| Tier | Byte | Routing |
|------|------|---------|
| Clear | `0xEC` | NDJSON JSON-RPC (local IPC) |
| Mito | `0xED` | Federation inter-gate NDJSON |
| Nuclear | `0xEE` | BTSP encrypted session |

### Constants module

`songbird_types::constants::ribocipher` — signal bytes, version byte, prefixes, `is_signal_byte()`, `tier_name()`.

### Deprecation

Legacy connections (no signal prefix) still work. Wave 112: WARN. Wave 113: REJECT. Wave 114: REMOVE.

---

## Deep Debt Evolution

### SRP Extractions (>800L threshold → 0 violations)

| File | Before | After | Extracted to |
|------|--------|-------|--------------|
| `connection.rs` | 815L | 472L | `session_protocol.rs` (359L) |
| `hardcoded_elimination.rs` | 872L | 689L | `hardcoded_replace.rs` (172L) |

### Hardcoded Elimination

- `16 * 1024 * 1024` → `BTSP_MAX_FRAME_SIZE` constant
- `format!("http://{}:{}/jsonrpc", ...)` → `jsonrpc_endpoint_url()` + `JSONRPC_PATH`
- `port == 8443` → `port == DEFAULT_HTTPS_PORT`

### Stale Debt Cleanup

- Removed 30-line stale "DEEP DEBT: polling loop" comment from `lineage-relay/relay.rs` (implementation was already event-driven via `wait_for_message_by_type`)

### Survey Findings (not actionable locally)

- Zero unsafe code (`unsafe_code = "forbid"` workspace-wide)
- `UnavailableVerifier` is correct secure-default (blocked on bearDog crypto-provider IPC)
- Legacy primal-name env vars already emit deprecation WARN (Wave 111-112 schedule)
- Dependency stack: pure Rust-first, no C/C++ in default features

---

## For Upstream

- **sourDough**: songBird is riboCipher-compliant. Signal prefix `[0xEC, 0x01]` on local IPC, `[0xED, 0x01]` on federation.
- **cellMembrane**: `uds_jsonrpc_call()` should prepend `[0xEC, 0x01]` per standard.
- **primalSpring**: `nucleus_launcher` + harness should send clear signal per standard.
- **bearDog**: `BtspSignatureVerifier` trait ready for `crypto.verify_signature` RPC when available.
