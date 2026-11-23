# Tower Atomic Composition Cost Map

**Date**: Jul 23, 2026 | **Wave**: 150w | **From**: eastGate overwatch
**Purpose**: Map every UDS hop across the Tower Atomic trio and estimate costs.

---

## Socket Topology

```
┌─ bearDog UDS server ─────────────────────────────┐
│  beardog.sock                                     │
│  ├── security.sock (symlink)                      │
│  ├── crypto.sock (symlink)                        │
│  ├── btsp.sock (symlink)                          │
│  ├── ed25519.sock (symlink)                       │
│  └── x25519.sock (symlink)                        │
│  Serves: ~230 methods (btsp.*, crypto.*, auth.*)  │
└───────────────────────────────────────────────────┘
         ▲                    ▲
         │ UDS                │ UDS
         │                    │
┌─ songBird UDS server ──────┼──────────────────────┐
│  songbird.sock              │                      │
│  ├── network.sock (symlink) │                      │
│                             │                      │
│  Serves: capability.call,   │                      │
│    mesh.*, health.*,        │                      │
│    federation.peers/status  │                      │
└─────────────────────────────┼──────────────────────┘
         ▲                    │
         │ UDS                │
         │                    │
┌─ skunkBat UDS server ──────┘──────────────────────┐
│  skunkbat.sock                                     │
│  ├── security.sock (symlink, domain scope)         │
│                                                    │
│  Serves: security.*, defense.*, health.*           │
│  Clients: bearDog (btsp.server.*, lineage.*)       │
│           songBird (federation.broadcast, pending) │
└────────────────────────────────────────────────────┘
```

## Interaction Seams — Complete Inventory

### Per-Session Seams (BTSP handshake establishment)

These fire once per new encrypted connection. Each seam is a full UDS
JSON-RPC round-trip: connect, serialize, write, read, deserialize.

| # | Caller | Callee | Method | Socket |
|---|--------|--------|--------|--------|
| 1 | songBird | bearDog | `btsp.session.create` | security.sock |
| 2 | songBird | bearDog | `btsp.session.verify` | security.sock |
| 3 | songBird | bearDog | `btsp.server.export_keys` | security.sock |
| 4 | skunkBat | bearDog | `btsp.server.create_session` | btsp.sock |
| 5 | skunkBat | bearDog | `btsp.server.verify` | btsp.sock |
| 6 | skunkBat | bearDog | `btsp.server.negotiate` | btsp.sock |

**Cost per session**: 3 UDS hops (songBird path) or 3 UDS hops (skunkBat path).
Measured: ~0.6ms per hop on LAN hardware. Session setup: ~1.8ms UDS overhead.

### Per-Enrollment Seams (mesh join)

Fire once per gate joining the mesh.

| # | Caller | Callee | Method | Socket |
|---|--------|--------|--------|--------|
| 7 | songBird | bearDog | `enrollment.verify` | security.sock |

Proof: `HMAC-SHA256(family_seed, node_id|public_key|timestamp)`.
Happens once per enrollment, cost is negligible.

### Per-Request Seams (every capability.call)

These fire on every single `capability.call` dispatch.

| # | Caller | Callee | Method | Socket |
|---|--------|--------|--------|--------|
| 8 | songBird | local provider | `{operation}` (forwarded) | provider.sock |
| 9 | songBird | bearDog | `crypto.verify.ed25519` | security.sock |

**Hop 8** is the `capability.call` dispatch: songBird resolves the
provider in its registry, opens a new UDS connection to the provider's
socket, and forwards the `operation` + `params` as a JSON-RPC call.
This is the hot path.

**Hop 9** fires when relay token verification is needed (virtual relay
signature checks).

### Per-Threat Seams (security events)

| # | Caller | Callee | Method | Socket |
|---|--------|--------|--------|--------|
| 10 | skunkBat | songBird | `federation.broadcast` | federation.sock |
| 11 | skunkBat | bearDog | `lineage.verify` | lineage-verification.sock |

**Note**: `federation.broadcast` handler is NOT yet implemented in
songBird. The `FederationMethod` enum has `Peers`, `Status`, `Join`
but no `Broadcast` variant. This is a gap.

### Per-Startup Seams (initialization)

| # | Caller | Callee | Method | Socket |
|---|--------|--------|--------|--------|
| 12 | skunkBat | songBird | `ipc.register` | songbird.sock |

Fire once at process startup. Negligible cost.

## Cross-Gate Request Cost Model

A `capability.call` from gate A to remote gate B:

```
caller (gate A)
  → UDS → songBird-A               [hop 1: ~0.15ms]
    → registry lookup               [in-proc: ~0.01ms]
    → TCP to songBird-B             [network: LAN 0.17ms / WAN 67ms]
  → songBird-B
    → UDS → provider (gate B)       [hop 2: ~0.15ms]
      → provider processes
    ← UDS response                  [hop 3: ~0.15ms]
  ← TCP response
← UDS response                      [hop 4: ~0.15ms]
```

**Total UDS overhead**: 4 hops × ~0.15ms = **~0.6ms** per cross-gate call.
This is ~100% of observed LAN latency (0.607ms) and ~1% of WAN latency (136ms).

With BTSP session establishment on a fresh connection, add 3 extra
bearDog hops = **~0.45ms** one-time cost. Amortized over session
lifetime, negligible.

## Where UDS Hops Matter vs Don't

| Context | UDS Overhead | Network | Ratio | Impact |
|---------|-------------|---------|-------|--------|
| LAN capability.call | ~0.6ms | ~0.17ms | 3.5x network | **DOMINANT** |
| LAN BTSP+capability.call | ~1.05ms | ~0.17ms | 6.2x network | **DOMINANT** |
| WAN capability.call | ~0.6ms | ~67ms | 0.009x network | Negligible |
| WAN BTSP+capability.call | ~1.05ms | ~67ms | 0.016x network | Negligible |
| High-rate dispatch (1000 req/s) | ~600ms total | varies | varies | **CPU-bound** |

**Key insight**: UDS IPC cost is the dominant factor on LAN, and
invisible on WAN. The chimera optimization (in-process calls instead of
UDS) would primarily benefit LAN performance and high-frequency
dispatch scenarios.

## Chimera Collapse Analysis

If Tower Atomic primals share a process (chimera mode):

| Current Path | Current Cost | Chimera Cost | Savings |
|-------------|-------------|-------------|---------|
| capability.call → songBird → provider UDS | ~0.3ms (2 hops) | ~0.01ms (function call) | 97% |
| BTSP create+verify+export_keys | ~0.45ms (3 hops) | ~0.03ms (3 function calls) | 93% |
| capability.call cross-gate | ~0.6ms + network | ~0.02ms + network | 97% (LAN only) |
| enrollment.verify | ~0.15ms (1 hop) | ~0.005ms (1 call) | 97% |

**Estimated chimera LAN latency**: ~0.05ms (vs current ~0.6ms) — a
**12x improvement** on the IPC-dominated LAN path.

## Gaps Found

1. **federation.broadcast not implemented**: skunkBat has a client, but
   songBird has no handler and no `federation.sock` symlink. Threat
   broadcasts will fail silently.

2. **Per-request connection overhead**: `capability.call` dispatch opens
   a **new UDS connection** per forward. Connection pooling could
   reduce overhead significantly even without chimera.

3. **No UDS connection reuse for BTSP**: Each BTSP call to bearDog is a
   fresh UDS connect. A persistent connection per-session would halve
   the handshake cost.

---

*This map provides the baseline for stress testing (measuring these
costs under load) and the chimera design document (which seams to
collapse first).*
