# barraCuda — Wave 44 Outbound Neural API Startup Announce

> **Date**: 2026-05-23
> **Sprint**: Wave 44 P1 (primalSpring audit response)
> **biomeOS**: v3.68+ Neural API
> **primalSpring**: v0.9.26

---

## Summary

Addressed Wave 44 P1 gap: barraCuda had a correct inbound `primal.announce`
handler but no outbound startup push. Now pushes `primal.announce` to the
biomeOS Neural API socket immediately after server bind, enabling routing
weight computation without waiting for inbound queries.

## Architecture

```
Server startup
  → Socket bind (UDS or TCP)
  → Discovery file written
  → Legacy symlink created
  → register_with_discovery()
  → [100ms delay] → announce_to_neural_api()  ← NEW
  → serve_unix() / serve_tcp_listener()
```

## Socket Discovery (WAVE42 3-tier)

1. `$NEURAL_API_SOCKET` — explicit override
2. `$XDG_RUNTIME_DIR/biomeos/neural-api-{family}.sock`
3. `/tmp/biomeos/neural-api-{family}.sock`

Family resolved from `ECOPRIMALS_FAMILY_ID` → `BIOMEOS_FAMILY_ID` → `FAMILY_ID`
→ default `ecoPrimal`.

## Payload (v3.68 schema)

```json
{
  "jsonrpc": "2.0",
  "method": "primal.announce",
  "params": {
    "primal": "barraCuda",
    "namespace": "barracuda",
    "version": "0.4.0",
    "domain": "math",
    "pid": <process_id>,
    "socket": "<own_socket_path>",
    "capabilities": ["math", "shader", "compute"],
    "methods": [<all 87 methods>],
    "signal_tiers": ["node"],
    "cost_hints": { "math": 20.0, "shader": 50.0, "compute": 80.0 },
    "latency_estimates": { "math": 10, "shader": 100, "compute": 200 },
    "attestation": null
  },
  "id": 1
}
```

## Files Added/Modified

- `crates/barracuda-core/src/ipc/neural_announce.rs` — NEW: module with resolve, build, send
- `crates/barracuda-core/src/ipc/mod.rs` — registered module
- `crates/barracuda-core/src/bin/barracuda.rs` — wired into all 3 startup paths

## Validation

```
cargo check          — clean
cargo clippy -D warn — clean
cargo test (IPC)     — 149 passed (145 existing + 4 new), 0 failed
```

## Reference Pattern

This implementation follows sweetGrass `neural_announce.rs` pattern:
- DI-friendly socket resolver for testability
- Fire-and-forget background task with post-bind delay
- Non-fatal standalone degradation (info-level log, no error)
- Newline-delimited JSON-RPC over UDS with 5s read timeout

## Wave 44 Status

| Priority | Team | Status |
|----------|------|--------|
| P0 wire broken | coralReef, petalTongue, skunkBat | pending (other teams) |
| **P1 no outbound** | **barraCuda** | **✅ COMPLETE** |
| P1 no outbound | songbird | pending |
| P2 socket/methods | squirrel, toadStool | pending |
| P3 minor | bearDog | pending |
