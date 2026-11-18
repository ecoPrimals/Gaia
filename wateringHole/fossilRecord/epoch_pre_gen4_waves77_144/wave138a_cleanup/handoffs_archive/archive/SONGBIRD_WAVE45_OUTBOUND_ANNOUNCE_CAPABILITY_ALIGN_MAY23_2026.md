# Songbird — primalSpring Wave 44/45: Outbound Announce + Capability Alignment

**Date**: May 23, 2026
**From**: songBird
**To**: primalSpring, biomeOS
**Version**: v0.2.1
**Commit**: `4a8f4cdc` (main)

## Context

Wave 44/45 identified songbird as the last foundation (tower-tier) primal without
outbound `primal.announce` on startup, plus a capability/hints key mismatch that
prevented Neural API routing weights from attaching correctly.

## Changes

### 1. Outbound `primal.announce` Push on Startup

New module `songbird-orchestrator::neural_announce` pushes `primal.announce` to
biomeOS Neural API immediately after IPC socket bind. Follows WAVE42 tiered socket
discovery:

1. `$NEURAL_API_SOCKET` — explicit override
2. `$XDG_RUNTIME_DIR/biomeos/neural-api-{family}.sock`
3. `/tmp/biomeos/neural-api-{family}.sock`

Non-blocking (`tokio::spawn`), non-fatal (logs warning if Neural API unavailable).
Includes small 100ms delay post-bind to ensure socket is fully ready.

### 2. Capability/Hints Key Alignment

| Before | After |
|--------|-------|
| `"capabilities": ["network.relay", "network.discovery", ...]` (15 entries) | `"capabilities": ["relay", "communication", "presence"]` |
| `"cost_hints": { "relay": 15.0, ... }` | Unchanged |
| `"latency_estimates": { "relay": 20, ... }` | Unchanged |

Now all three fields use the same domain keys, so biomeOS correctly attaches weights.

### 3. Test Coverage

4 tests validate:
- `announce_payload_has_aligned_capabilities_and_hints` — every capability has matching hint/latency keys
- `announce_payload_has_required_fields` — primal, socket, signal_tiers, methods, status
- `resolve_neural_api_socket_returns_none_when_no_env` — graceful fallback
- `resolve_family_id_uses_env_or_default` — env resolution

## Validation

After this change, starting songbird with a running biomeOS Neural API should show:

```bash
echo '{"jsonrpc":"2.0","method":"neural_api.routing_weights","params":{},"id":1}' | \
  socat - UNIX-CONNECT:$XDG_RUNTIME_DIR/biomeos/neural-api-ecoPrimal.sock
# Should show songbird with relay/communication/presence weights
```

## Ecosystem Status

With this fix, **12/13 primals** have working outbound `primal.announce` on startup.
The Neural API routing layer is now functional at ecosystem scale.
