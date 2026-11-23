<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# sweetGrass v0.7.57 — riboCipher Reference Implementation

**Wave**: 111 (Stream 7: Transport Signal Convergence)  
**Date**: 2026-06-13  
**Commit**: `52ec5b4` on `main`  
**Status**: SHIPPED

---

## What Changed

### riboCipher signal detection in `peek.rs`

sweetGrass now implements `RIBOCIPHER_TRANSPORT_SIGNAL_STANDARD.md` as the
**reference implementation** for the ecosystem.

**Before**: `detect_protocol()` peeked the first byte and guessed the protocol.
Bytes outside `{` were assumed to be length-prefixed BTSP binary. This broke
when BTSP ciphertext started with arbitrary bytes indistinguishable from noise.

**After**: `detect_protocol()` checks for riboCipher signal prefix bytes
(`0xEC`, `0xED`, `0xEE`) **before** any legacy peek logic. The accept loop
reads the signal (ribosome reads the codon) and routes deterministically.

### Tier 1 (Clear Signal) Routing

`[0xEC, protocol_type]` — 2 bytes consumed, then routed:

| Protocol Type | UDS | TCP |
|---------------|-----|-----|
| `0x00` Probe | Health response | Health response |
| `0x01` NDJSON JSON-RPC | Raw handler | Rejected (-32001, BTSP required) |
| `0x02` BTSP Binary | BTSP handshake | BTSP handshake |
| `0x03` BTSP JSON-line | ClientHello → handshake | ClientHello → handshake |
| Other | Reject (-32002) | Reject |

### Tiers 2–3 (Mito/Nuclear)

Return `ErrorKind::Unsupported`. Will be implemented when family seed HKDF
infrastructure is available for signal verification.

### Legacy Deprecation (Wave 111)

Connections NOT starting with `0xEC`/`0xED`/`0xEE` fall through to the
existing peek logic with a WARN-level log:

```
DEPRECATED: unsignalled connection (no riboCipher prefix).
Falling back to legacy peek detection.
Clients should send [0xEC, protocol_type] prefix.
```

Deprecation schedule per standard:
- Wave 111-112: WARN (current)
- Wave 112: ERROR
- Wave 113: REJECT (`-32002`)
- Wave 114: REMOVE legacy peek code

---

## Files Changed

| File | Change |
|------|--------|
| `peek.rs` | riboCipher signal detection, constants, protocol_type module, 10 tests |
| `uds.rs` | `RiboCipherClear` dispatch, `handle_ribocipher_clear_uds()`, probe helper |
| `tcp_jsonrpc.rs` | `RiboCipherClear` dispatch, `handle_ribocipher_clear_tcp()` |
| `uds/tests/autodetect.rs` | 2 integration tests (riboCipher JSON-RPC, probe) |
| `Cargo.toml` | v0.7.57 |
| Docs | CHANGELOG, README, ROADMAP updated |

---

## Test Coverage

- **10 new unit tests** in `peek.rs`: all 6 protocol types, mito/nuclear
  unsupported, riboCipher-first precedence
- **2 new integration tests** in `autodetect.rs`: live UDS riboCipher
  JSON-RPC, live UDS riboCipher probe
- **1,647 total tests**, 0 failures, 0 clippy warnings

---

## Upstream Dependencies

None. sweetGrass is the **first primal** to ship riboCipher detection.
Other teams can study `peek.rs` as the canonical reference.

## Upstream Impact

- **cellMembrane**: Can now send `[0xEC, 0x01]` prefix to sweetGrass UDS
  sockets and get routed via riboCipher instead of legacy peek
- **primalSpring**: `nucleus_launcher` health probes can send `[0xEC, 0x00]`
  for lightweight probe response
- **sourDough**: `validate ribocipher sweetGrass` should pass once the
  validator is implemented

---

## Open Items

| Item | Status | Notes |
|------|--------|-------|
| Tier 2 (mito-obfuscated) | DEFERRED | Needs HKDF from family_seed |
| Tier 3 (nuclear-sealed) | DEFERRED | Needs nuclear lineage key |
| Client-side signal sending | NOT STARTED | sweetGrass outbound IPC should prepend signals |
| Wave 112 ERROR escalation | FUTURE | Change WARN to ERROR in legacy path |
