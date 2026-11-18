# Songbird GAP-HS-119 — Discovery Propagation via `ipc.watch`

**Date**: June 1, 2026  
**From**: southGate (songbird team)  
**To**: hotSpring (Exp 234 pipeline), toadStool team  
**Priority**: P0 response  
**FRAGO origin**: hotSpring sovereign compute cascade  

---

## Problem Statement

When coralReef registers capabilities (`shader`, `compile`, `visualization`) with
songbird via `ipc.register`, toadStool doesn't see them because it uses an internal
`self.coral_client.is_available()` check — not songbird resolution.

## Solution Delivered: `ipc.watch`

Songbird now implements **revision-tracked registry event propagation** via `ipc.watch`.

### How It Works

1. `ServiceRegistry` maintains a monotonic **revision counter** (increments on every
   `register` / `unregister` mutation).
2. Every mutation appends to a **bounded event log** (256 entries, ring-buffer semantics).
3. Consuming primals call `ipc.watch` with their last-known revision to get changes.

### API

```json
// Request
{
  "method": "ipc.watch",
  "params": {
    "since_revision": 0,
    "capabilities": ["shader", "compile", "visualization"]
  }
}

// Response
{
  "revision": 3,
  "events": [
    {
      "revision": 3,
      "kind": "registered",
      "primal": "coralReef",
      "capabilities": ["shader", "compile", "visualization", "rendering", "transform", "pipeline", "compute"],
      "endpoint": "unix:///run/user/1000/biomeos/coralreef-nucleus01.sock"
    }
  ]
}
```

### Integration Pattern for toadStool

```rust
// On startup or periodically (e.g. every 5s):
let response = songbird_client.call("ipc.watch", json!({
    "since_revision": last_known_revision,
    "capabilities": ["shader", "compile", "visualization"]
})).await?;

if !response.events.is_empty() {
    // New provider available — resolve endpoint
    let provider = songbird_client.call("ipc.resolve", json!({
        "capability": "shader"
    })).await?;
    // Update internal service client with discovered endpoint
    self.coral_client.connect(provider.socket).await?;
}
last_known_revision = response.revision;
```

### Why This Design (vs alternatives)

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **Push (server-sent)** | Instant | Requires persistent connections, complex | Not chosen |
| **Long-poll** | Near-real-time | Ties up connections, complex timeout handling | Not chosen |
| **Revision-tracked poll** | Simple, stateless, works with existing JSON-RPC req/res model | Small latency (poll interval) | **Chosen** |

The poll approach fits the ecosystem's JSON-RPC model perfectly — no persistent
connections needed, no server-side subscription state, and toadStool controls
its own polling frequency.

## What Was Already Working

- `ipc.register`: Stores capabilities correctly
- `ipc.resolve`: Returns correct endpoints
- `ipc.discover`: Returns all providers for a capability
- Socket management: Reliable and stable
- Multi-capability registration: 7 caps in one call

## What's New

- `ServiceRegistry` emits `RegistryEvent` on every mutation
- Event log retained (bounded 256 events, ring-buffer)
- `ipc.watch` method dispatched and introspected
- Capability token registered
- `rpc.methods` updated

## Recommendation to toadStool

The standard pattern going forward:
1. On DRM dispatch, call `ipc.resolve("shader")` on songbird before checking internal availability
2. Optionally run a background `ipc.watch` loop (5s interval) to pre-warm the provider cache
3. Fall back to internal registry only when songbird resolution returns no results

This eliminates the "isolated primals" gap — any primal registered with songbird
becomes discoverable by all other primals in the composition.
