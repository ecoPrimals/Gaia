# swarmVine — Wave 157e Deep Debt Cleanup

**Date**: August 09, 2026
**Primal**: swarmVine (#16)
**Wave**: 157e
**From**: eastGate overwatch

---

## Summary

Deep debt cleanup pass on swarmVine following Windows port (157d). Focused on
bug fixes, hardcoding elimination, transport abstraction evolution, and
dependency deduplication.

## Changes

### Bug Fixes
- **IPv6 bracketed loopback bypass** — `[::1]:7700` was not filtered as loopback
  in peer address extraction. Refactored into `strip_port()` + `is_loopback()`
  helpers that correctly handle bracketed IPv6.
- **Empty address leak** — empty `addr` field in songBird peer data produced
  `Some(":7800")` instead of `None`. Now returns `None` on empty IP.

### Hardcoding → Platform Discovery
- `/tmp/biomeos/skunkbat.sock` → `platform_paths::runtime_socket_dir().join("skunkbat.sock")`
- `/tmp/biomeos/neural-api-{family}.sock` → `runtime_socket_dir().join(...)`
- `/tmp/biomeos/songbird.sock` → `runtime_socket_dir().join("songbird.sock")`
- Added `platform_paths::runtime_socket_dir()` public API for ecosystem-wide
  socket directory resolution (respects `BIOMEOS_RUNTIME_DIR` → XDG → platform default).

### Transport Abstraction Evolution
- `spread.rs` `query_songbird_peers`: replaced raw `tokio::net::UnixStream::connect`
  with `swarmvine_core::transport::connect_transport`. Removed `#[cfg(unix)]` /
  `#[cfg(not(unix))]` pair — transport layer handles platform gating internally.
- `announce.rs` `discover_songbird_socket`: removed unnecessary `#[cfg(unix)]`
  gate. Function is platform-agnostic (checks file existence; on non-Unix, socket
  files don't exist → returns `None`).

### Dependency Deduplication
- `hostname` crate removed from `swarmvine-server` Cargo.toml. Shared
  `resolve_node_id()` function added to `swarmvine-core::lib` and used by both
  core's `SwarmVinePrimal::new()` and server's `main.rs`.

### Code Quality
- Gossip engine nonce recording restructured: `nonce_order` and `nonce_set` locks
  acquired sequentially instead of simultaneously, eliminating lock contention.
- `vine_bat_preaccept` serialization hardened: replaced silent `unwrap_or_default()`
  (empty-frame bug) with `let...else` early return on serialization failure.

### Test Fixes
- `discover_songbird_socket_none_when_missing` test now overrides
  `BIOMEOS_RUNTIME_DIR` alongside `XDG_RUNTIME_DIR` to ensure deterministic behavior
  regardless of host environment.

## Metrics

| Metric | Value |
|--------|-------|
| Tests | 124 (56 core + 68 server) |
| Clippy | 0 warnings (pedantic + nursery) |
| cargo-deny | licenses/bans/sources clean |
| Largest file | `dispatch.rs` at 682 LOC |
| Total LOC | 5,568 |
| `/tmp/` in production code | **0** (all in test code only) |
| Direct dependencies (server) | 10 (was 11, removed `hostname`) |

## Files Changed

- `crates/swarmvine-core/src/gossip.rs` — lock restructuring
- `crates/swarmvine-core/src/lib.rs` — added `resolve_node_id()`
- `crates/swarmvine-core/src/platform_paths.rs` — added `runtime_socket_dir()`
- `crates/swarmvine-server/Cargo.toml` — removed `hostname` dep
- `crates/swarmvine-server/src/announce.rs` — platform-agnostic discovery, runtime_socket_dir
- `crates/swarmvine-server/src/dispatch.rs` — skunkbat socket via platform_paths, serialization hardening
- `crates/swarmvine-server/src/main.rs` — uses `resolve_node_id()`
- `crates/swarmvine-server/src/spread.rs` — transport abstraction, IPv6/empty address fixes

## Remaining Debt (tracked)

- Test coverage at 82% (target 90%+) — `main.rs` and `server.rs` run loops have low coverage
- Phase 4 (gossip.subscribe streaming, bloom filters, depot diffing) — next evolution
- G65 single-socket negotiation — tarpc 0.37 limitation documented, awaiting upstream

---

*Wave 157e — zero hardcoded paths in production code. Transport abstraction complete across all call sites. 124 tests. 0 clippy warnings.*
