# Songbird Virtual Endpoint Relay — Design Document

**Status**: DESIGN (Wave 68)
**Owner**: southGate (Songbird team)
**Priority**: P2 — after L4 weighted routing + mesh validation

---

## Problem

Today Songbird is a **resolver, not a relay**. The discovery flow:

1. Client calls Songbird `ipc.resolve("beardog")` -> gets `/run/user/1000/biomeos/beardog-*.sock`
2. Client opens **direct UDS connection** to bearDog
3. Songbird is no longer in the path

This means:
- 13 UDS sockets per gate, each primal with its own listener
- Songbird cannot apply Dark Forest rules to inter-primal traffic
- No centralized rate limiting, audit, or access control on IPC
- Cross-gate traffic already goes through Songbird (capability.call relay)
  but local traffic bypasses it entirely

## Proposed Solution: Virtual Endpoints

### Architecture

```
BEFORE (current):
  Client → ipc.resolve → native UDS path → direct connection to primal

AFTER (virtual relay):
  Client → ipc.resolve → Songbird virtual endpoint → Songbird forwards to native UDS
```

### How It Works

1. **Registration**: When a primal calls `ipc.register`, Songbird creates a
   **virtual endpoint** alongside the native one. The virtual endpoint is a
   Songbird-managed UDS socket (e.g., `/run/user/$UID/songbird/virtual/beardog.sock`).

2. **Resolution**: `ipc.resolve` returns the virtual endpoint by default.
   A `native: true` parameter still returns the direct path (for perf-critical
   or same-process calls).

3. **Relay**: Songbird accepts JSON-RPC on the virtual socket, validates the
   request (BTSP session, rate limits, Dark Forest rules), then forwards to
   the native UDS socket. Responses flow back through Songbird.

4. **Cross-gate**: For cross-gate calls, the flow is identical — Songbird is
   already the relay. Virtual endpoints unify local and remote into one path.

### Benefits

| Benefit | Detail |
|---------|--------|
| Single ingress point | All IPC flows through Songbird; gate surface = 1 socket |
| Centralized audit | SkunkBat can monitor all inter-primal traffic via Songbird |
| Rate limiting | Songbird applies per-capability, per-caller rate limits |
| Dark Forest enforcement | Songbird validates BTSP on every call, not just cross-gate |
| Uniform local/remote | Same API for local and cross-gate calls |
| Hot-swap support | Songbird can reroute virtual endpoint to new primal instance |

### Performance Considerations

- **Overhead**: One extra UDS hop per call (~0.05ms on Linux UDS)
- **Throughput**: Songbird must handle all IPC; async multiplexing essential
- **Opt-out**: Performance-critical paths (e.g., barraCuda tensor ops) can
  request `native: true` from `ipc.resolve` to bypass relay
- **Batching**: `capability.call` already supports batch operations; relay
  forwards batches as single messages

### Migration Path

**Phase 1 — Shadow mode (non-breaking)**
- Songbird creates virtual endpoints alongside native ones
- `ipc.resolve` returns native by default (no behavior change)
- Clients can opt-in to virtual via `virtual: true` parameter
- Songbird logs virtual relay traffic for performance baselining

**Phase 2 — Default virtual**
- `ipc.resolve` returns virtual endpoint by default
- `native: true` parameter for opt-out
- primalSpring composition context updated to use virtual

**Phase 3 — Native endpoints internal-only**
- Native UDS sockets bound to Songbird-managed namespace
- External clients (springs, experiments) only see virtual
- Native endpoints accessible only by Songbird process

### Wire Contract Changes

```
ipc.resolve:
  CURRENT:  { primal_id: "beardog" } → { endpoint: "/run/.../beardog-*.sock" }
  PROPOSED: { primal_id: "beardog" } → { endpoint: "/run/.../songbird/virtual/beardog.sock",
                                          native_endpoint: "/run/.../beardog-*.sock",
                                          relay: true }

  With native: true:
            { primal_id: "beardog", native: true } → { endpoint: "/run/.../beardog-*.sock",
                                                         relay: false }
```

### Dependencies

- Songbird async UDS relay (tokio/smol based)
- BTSP session management for virtual connections
- SkunkBat audit integration for relay traffic
- primalSpring CompositionContext update (prefer virtual_endpoint)

---

## Relation to Existing Architecture

| Component | Impact |
|-----------|--------|
| `tower_membrane.toml` | No change — VPS already uses Songbird as sole surface |
| `capability.call` cross-gate | No change — already relayed through Songbird |
| `ipc.register` / `ipc.watch` | Extended with virtual_endpoint field |
| `DISCOVERY_WIRE_CONTRACT.md` | Updated with relay field in resolve response |
| Dark Forest Glacial Gate | Phase B completes Pillar 3 (Songbird sole surface) for local traffic |

---

*Wave 68. Design document. Implementation is southGate Songbird team P2.*
