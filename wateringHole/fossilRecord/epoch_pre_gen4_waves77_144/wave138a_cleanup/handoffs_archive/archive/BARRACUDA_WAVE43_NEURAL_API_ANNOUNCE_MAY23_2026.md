# barraCuda — Wave 43 Neural API `primal.announce` Adoption

> **Date**: 2026-05-23
> **Sprint**: Wave 43 (primalSpring audit response)
> **biomeOS**: v3.68+ Neural API schema
> **primalSpring**: v0.9.26

---

## Summary

Upgraded `primal.announce` to the biomeOS v3.68+ Neural API wire schema as
specified in primalSpring Wave 43 audit. barraCuda now provides routing-ready
self-registration that enables Neural API weight computation and
`capability.call` traffic routing.

## Changes

| Field | Before | After |
|-------|--------|-------|
| `capabilities` | Derived from dispatch table (~10 items) | `["math", "shader", "compute"]` (canonical routing domains) |
| `signal_tier` → `signal_tiers` | `"passive"` (string) | `["node"]` (array) |
| `socket` | absent | `$XDG_RUNTIME_DIR/biomeos/math[-{family}].sock` |
| `cost_hints` | absent | `{ "math": 20.0, "shader": 50.0, "compute": 80.0 }` |
| `latency_estimates` | absent | `{ "math": 10, "shader": 100, "compute": 200 }` |

## Files Modified

- `crates/barracuda-core/src/ipc/methods/primal.rs` — announce handler updated
- `crates/barracuda-core/src/ipc/transport.rs` — `discovery_socket_path()` added
- `crates/barracuda-core/src/ipc/methods_tests/primal_wire_tests.rs` — 2 new tests
- `crates/barracuda-core/src/ipc/methods_tests/device_health_tests.rs` — test updated
- `specs/TENSOR_WIRE_CONTRACT.md` — description updated
- `CHANGELOG.md`, `WHATS_NEXT.md`, `STATUS.md` — documentation

## Validation

```
cargo check          — clean
cargo clippy -D warn — clean
cargo test (IPC)     — 145 passed, 0 failed
```

Self-validation (after biomeOS v3.69 running):
```bash
echo '{"jsonrpc":"2.0","method":"neural_api.routing_weights","params":{},"id":1}' | \
  socat - UNIX-CONNECT:$XDG_RUNTIME_DIR/biomeos/neural-api-ecoPrimal.sock
```

## Timeline Position

- Wave 43 HIGH (songbird, toadStool, bearDog) — in progress by those teams
- **Wave 44 MEDIUM (barraCuda)** — ✅ COMPLETE
- Wave 44 MEDIUM (nestgate, coralReef) — pending
