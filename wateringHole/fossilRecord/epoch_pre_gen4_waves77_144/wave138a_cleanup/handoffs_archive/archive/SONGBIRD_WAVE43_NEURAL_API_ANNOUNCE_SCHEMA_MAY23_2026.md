# Songbird — primalSpring Wave 43: Neural API `primal.announce` Schema Alignment

**Date**: May 23, 2026
**From**: songBird
**To**: primalSpring, biomeOS
**Version**: v0.2.1
**Commit**: `9bfcd377` (main)

## Context

primalSpring Wave 43 identified a schema mismatch blocking Neural API routing data:
songBird's `primal.announce` used `provided_capabilities` instead of `capabilities`,
and was missing `socket`, `cost_hints`, and `latency_estimates` fields.

## Changes

### Schema Alignment (biomeOS v3.69 Neural API wire format)

| Field | Before | After |
|-------|--------|-------|
| `provided_capabilities` | Array of capability strings | **Removed** (renamed) |
| `capabilities` | Not present | Array of capability strings (biomeOS-expected key) |
| `socket` | Not present | Full UDS path (`$XDG_RUNTIME_DIR/biomeos/songbird-{family_id}.sock`) |
| `cost_hints` | Not present | `{ "relay": 15.0, "communication": 10.0, "presence": 5.0 }` |
| `latency_estimates` | Not present | `{ "relay": 20, "communication": 10, "presence": 5 }` |
| `signal_tiers` | `["tower"]` | `["tower"]` (unchanged) |

### API Addition

- `primal_announce_with_socket(socket_path: &str)` — accepts explicit socket path
- `primal_announce()` — auto-resolves from `XDG_RUNTIME_DIR` / `FAMILY_ID` env

### Orchestrator Integration

The pure Rust IPC server now passes its actual bound `socket_path` to
`primal_announce_with_socket()` instead of relying on env-only fallback.

## Validation

After this change, calling `primal.announce` on songbird's UDS returns:

```json
{
  "primal": "songbird",
  "capabilities": ["relay", "communication", "presence", ...],
  "socket": "/run/user/1000/biomeos/songbird-ecoPrimal.sock",
  "signal_tiers": ["tower"],
  "cost_hints": { "relay": 15.0, "communication": 10.0, "presence": 5.0 },
  "latency_estimates": { "relay": 20, "communication": 10, "presence": 5 },
  "methods": [...],
  "status": "ready"
}
```

biomeOS `neural_api.routing_weights` should now show entries for `relay.*` and
`communication.*` with non-default affinity after songbird announces.

## Downstream Impact

- **biomeOS**: Can now compute routing weights for songbird capabilities
- **Other primals**: Wire format example for their own Wave 43/44/45 implementations
