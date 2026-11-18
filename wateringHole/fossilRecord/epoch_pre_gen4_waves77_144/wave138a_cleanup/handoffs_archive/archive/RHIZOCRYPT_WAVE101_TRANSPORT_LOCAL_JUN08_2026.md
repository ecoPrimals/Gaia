# rhizoCrypt — Wave 101 Handoff: Transport Self-Knowledge Fix

**Date**: 2026-06-08
**Version**: 0.14.3
**Wave**: 101
**Tests**: 1,683 (`--all-features`), 0 clippy, 0 unsafe

## Summary

Removed `sourdough-core` path dependency (primal self-knowledge violation).
Implemented `TransportEndpoint`, `TransportStream`, and `connect_transport()`
locally in `transport.rs` (~170 lines). Wire-compatible with ecosystem
standard (same `#[serde(tag = "transport")]` JSON format).

## What Changed

1. **Removed** `sourdough-core` from workspace `Cargo.toml` and `rhizo-crypt-core/Cargo.toml`
2. **Added** `TransportEndpoint`, `TransportStream`, `connect_transport()` to
   `crates/rhizo-crypt-core/src/transport.rs` — local implementation
3. **Updated** all imports: `sourdough_core::transport::` → `crate::transport::`
4. **Updated** re-exports in `lib.rs`: from sourdough-core → local transport module
5. **Verified**: `cargo tree | grep sourdough` returns empty — zero cross-primal deps

## Wire Compatibility

```json
{ "transport": "uds", "path": "/run/user/1000/biomeos/rhizocrypt.sock" }
{ "transport": "tcp", "host": "127.0.0.1", "port": 9100 }
{ "transport": "mesh_relay", "peer_id": "strandgate", "capability": "security" }
```

Same tagged JSON format as sourDough, songBird, cellMembrane, sweetGrass,
nestGate, coralReef, squirrel. The wire format is the contract.

## Key Files

- `crates/rhizo-crypt-core/src/transport.rs` — local TransportEndpoint (398L total)
- `Cargo.toml` — sourdough-core removed
- `crates/rhizo-crypt-core/Cargo.toml` — sourdough-core removed

## Ecosystem Status

rhizoCrypt now follows the correct LOCAL pattern (like coralReef, squirrel,
sweetGrass, nestGate). 6/14 primals transport-injected, 0 with cross-primal
path deps.
