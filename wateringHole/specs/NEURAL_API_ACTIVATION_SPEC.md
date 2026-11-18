# G67: Neural API Activation — Stage 2 Transition

**Status**: ACTIVE
**Created**: Wave 156z (Aug 7, 2026)
**Depends on**: G64 (Cephalization), G65 (Protocol Negotiation), G66 (Transport Abstraction) — all COMPLETE

---

## Problem

Primals communicate over UDS sockets. Consumers must know socket paths.
This creates jelly strings: hardcoded paths, manual wiring per gate, Python
scripts that bypass primal-native RPCs (westGate AAR), compositions that
can't move between gates without reconfiguration.

G64-G66 solved the protocol layer (tarpc convergence, single-socket
negotiation, transport abstraction). The routing layer remains primordial:
direct socket connections, no capability discovery, no composition semantics.

## Solution

biomeOS Neural API becomes the sole routing substrate for all primal
communication within a gate. Consumers call capabilities, not sockets.
Compositions are TOML graphs executed by the Neural API graph executor.

### Three Evolutionary Stages

```
STAGE 1 — PRIMORDIAL (deprecated after Stage 2 activation)
  Consumer → UDS socket path → Primal
  Manual wiring. Per-gate config. Jelly string prone.
  Primals own their sockets and protocols.

STAGE 2 — NEURAL API ROUTING (current activation target)
  Consumer → neural-api-default.sock → capability.call → Primal
  Capability discovery. Graph execution. Isomorphic deployment.
  biomeOS owns routing. Primals own computation.

STAGE 3 — BIOMEOS AS OS (glacial)
  biomeOS IS the operating system.
  Primals are processes. Capability registry is the process table.
  Graph executor is the scheduler. rootPulse is the filesystem.
  Transport layer is the IPC kernel.
```

Stage 1 is the bootstrap pattern — how primals start before Neural API
exists. Stage 2 is the intended long-form existence. Stage 3 is the
convergence point where biomeOS replaces Linux/Windows as the bare-metal
substrate.

### Stage 2 Properties

**Isomorphic deployment**: A single `graph.execute(nucleus_complete)` deploys
identically on any gate. Same graph, different hardware, same composition
semantics. The capability registry adapts to what's available.

**Fractal self-similarity**: Each gate is a self-similar NUCLEUS. Compositions
scale from single-gate to full mesh without rewiring. A Steam Deck runs the
same graphs as a 128 GB Threadripper — the Neural API routes to available
capabilities.

**Port-aesthetic**: songBird handles inter-gate routing (cross-membrane).
Neural API handles intra-gate routing (intramembrane). tarpc elevates
cross-gate as compositions mature. The two layers compose: Neural API
discovers local capabilities, songBird discovers remote ones, the graph
executor orchestrates both.

**Jelly string elimination**: No consumer ever imports a socket path.
`capability.call("crypto", "sign_ed25519", {...})` resolves at runtime.
When primals evolve (e.g., nestGate adds `content.query`), consumers get
the new capability without rewiring.

### Deprecation Boundary

Stage 1 is fully primordial when **no consumer on any gate calls a primal
socket directly**. All communication routes through `neural-api-default.sock`
via capability semantics. Direct socket paths exist only in:
- Neural API's own discovery layer (it scans sockets to build the registry)
- Primal-to-primal communication that Neural API has explicitly delegated
- Bootstrap mode (before Neural API is alive)

## Architecture

### Capability Routing

```
                    ┌─────────────────────────────────────┐
                    │          neural-api-default.sock     │
                    │                                     │
                    │  ┌──────────────────────────────┐   │
                    │  │     Capability Registry       │   │
                    │  │  754+ capabilities from 10+   │   │
                    │  │  primals, weighted routing,    │   │
                    │  │  L4 provider selection         │   │
                    │  └──────────────────────────────┘   │
                    │                                     │
                    │  ┌──────────────────────────────┐   │
                    │  │     Graph Executor             │   │
                    │  │  75 TOML graphs, topological   │   │
                    │  │  phases, parallel dispatch,    │   │
                    │  │  checkpoint + rollback         │   │
                    │  └──────────────────────────────┘   │
                    │                                     │
                    │  ┌──────────────────────────────┐   │
                    │  │     Translation Registry       │   │
                    │  │  Semantic → actual method      │   │
                    │  │  decouples consumers from      │   │
                    │  │  primal API evolution          │   │
                    │  └──────────────────────────────┘   │
                    └─────────┬───────────┬───────────────┘
                              │           │
              ┌───────────────┤           ├───────────────┐
              │               │           │               │
    ┌─────────▼──────┐ ┌─────▼────┐ ┌────▼─────┐ ┌──────▼────────┐
    │  Tower Atomic   │ │  Node    │ │  Nest    │ │  Meta         │
    │  bearDog        │ │  Atomic  │ │  Atomic  │ │  squirrel     │
    │  songBird       │ │ toadStool│ │ nestGate │ │  petalTongue  │
    │  skunkBat       │ │ barraCuda│ │ rhizoCrypt│ │               │
    │                 │ │ coralReef│ │ loamSpine│ │               │
    │                 │ │          │ │ sweetGrass│ │               │
    └─────────────────┘ └──────────┘ └──────────┘ └───────────────┘
```

### Composition Tiers

| Tier | Primals | Capability Domains |
|------|---------|-------------------|
| Tower | bearDog + songBird + skunkBat | crypto, tls, mesh, discovery, defense |
| Node | Tower + toadStool + barraCuda + coralReef | compute, GPU, shaders, tensor |
| Nest | Tower + nestGate + rhizoCrypt + loamSpine + sweetGrass | storage, DAG, provenance, braids |
| Nucleus | All 13 | Full composition |
| Meta | squirrel + petalTongue | AI agent, visualization |

### Signal Graphs (composition intercept)

When `capability.call("nest", "store", ...)` arrives, the Neural API checks
for a signal graph. If `signals/nest_store.toml` exists, it executes the full
composition (store -> DAG append -> spine commit -> braid) instead of routing
to a single primal. This is how complex compositions emerge from simple
capability calls.

### rootPulse as Reference Composition

rootPulse commit is the canonical complex composition:

1. Health checks (rhizoCrypt + loamSpine) — parallel
2. DAG dehydration (rhizoCrypt) — Merkle root
3. Cryptographic signing (bearDog) — Ed25519
4. Content-addressed storage (nestGate) — CAS
5. Permanent commit (loamSpine) — immutable spine
6. Attribution braid (sweetGrass) — semantic provenance

Six primals, six phases, all routed through capability semantics. Same graph
works on any gate with a Nest Atomic deployed.

## Activation Tasks

| ID | Task | Gate | Blocks |
|----|------|------|--------|
| N1 | Fix forwarding path (tarpc/BTSP fast-fail for dev-mode primals) | eastGate | N2-N6 |
| N2 | Deploy neural-api-server systemd service | eastGate (test) | N3 |
| N3 | Verify Tower Atomic routing | eastGate | N4 |
| N4 | Verify Provenance Trio routing (rootPulse) | eastGate | N5 |
| N5 | Verify Node Atomic routing | eastGate | N6 |
| N6 | Deploy on production gates (sporeGate, westGate, strandGate) | all | — |

## Anti-Patterns (Stage 1 violations after Stage 2 activation)

- Importing a primal socket path in consumer code
- Python scripts calling primals via direct UDS (westGate jelly strings)
- Manual socket wiring in gate deployment scripts
- Hardcoded port numbers in composition config
- Any consumer that breaks when a primal socket moves

## Relationship to Other Specs

- **G64 (Cephalization)**: Gave all primals tarpc. Neural API leverages tarpc
  for high-performance forwarding.
- **G65 (Protocol Negotiation)**: Single-socket dual-protocol. Neural API
  uses G65 negotiation on incoming connections and can negotiate on forwards.
- **G66 (Transport Abstraction)**: Silicon-agnostic IPC. Neural API's
  `TransportEndpoint` model builds on sourDough's reference.
- **rootPulse**: First complex composition to prove Stage 2 works.
- **Plasmodium mode**: Stage 2.5 — multi-gate Neural API coordination.

---

*sourDough is the reference for transport (G66). biomeOS is the reference for
routing (G67). Each primal evolves independently — convergent, not shared.*
