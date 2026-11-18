# Gen5 — Transport Evolution: Nanowire to Quorum Sensing

**Authority**: wateringHole consensus (Wave 63+)
**Prerequisites**: `KDERM_DIDERM_APPLICATION.md`, `IMPULSE_POTENTIAL_KDERM_INTERACTIONS.md`, `BONDING_MODEL_STANDARD.md`
**Status**: Conceptual — current infrastructure is nanowire; quorum sensing is the target
**Date**: May 31, 2026

---

## Overview

The K-Derm diderm relay chain (`pepti-sync-relay.sh` → `ext-github-push.sh`) uses
direct SSH connections between nodes. In biological terms, this is **nanowire**:
point-to-point conductive filaments between specific cells. Nanowire is the correct
early-stage transport — it's reliable, debuggable, and maps cleanly to the metallic
bond model. But it is not the target architecture.

The target is **quorum sensing**: a diffusion-based coordination model where nodes
detect environmental signals (impulses in the periplasm) and respond independently,
without point-to-point wiring. The relay chain should fire because nodes *sense*
that coordination is needed, not because a specific script SSHs into them.

This is the Gram-negative bacteria pattern: nanowire for specialized direct
interactions (like type IV pili), quorum sensing for population-level coordination
(autoinducer diffusion).

---

## Current Architecture: Nanowire

```
Gate ──SSH──→ golgiBody-inner ──SSH──→ peptidoglycan ──SSH──→ golgiBody-ext ──SSH──→ GitHub
```

Every hop is a direct SSH call. Each node knows the next node's address, holds its
SSH key, and issues an explicit command. This is:

- **Point-to-point**: each node has hardcoded knowledge of the next
- **Synchronous**: the relay waits for each hop to complete
- **Sequential**: inner→pepti→outer, always in this order
- **Fragile to topology changes**: adding or removing a node requires rewiring scripts

### Where nanowire is correct

Nanowire remains the correct pattern for **metallic bond** interactions:

| Interaction | Why nanowire | Long-term role |
|-------------|-------------|----------------|
| Gate SSH to Forgejo | Authentication requires direct connection | Permanent — covalent bond demands nanowire |
| Fleet key operations | SSH key rotation, admin commands | Permanent — metallic bond between trusted nodes |
| Build dispatch to peptidoglycan | Compilation needs specific hardware | Permanent — specialized compute routing |
| Emergency rollback | Operator needs deterministic control | Permanent — override channel |

These are **pili**: specialized conductive appendages for specific functions.
They don't need to evolve away from nanowire.

---

## Target Architecture: Quorum Sensing

```
Gate pushes to Forgejo
  → Forgejo emits autoinducer (impulse TOML to impulses/active/)
  → Peptidoglycan senses autoinducer concentration (potential.sense)
  → Peptidoglycan responds (sync + relay) based on local policy
  → golgiBody-ext senses sync state (ahead of GitHub?)
  → golgiBody-ext responds (push to GitHub) based on local policy
```

Each node acts autonomously based on what it senses in its environment. No node
explicitly calls the next. The coordination is **emergent** from each node following
its own sensing→response loop.

### Biological analog

In Gram-negative bacteria, quorum sensing works through **autoinducers** — small
molecules that diffuse through the periplasm. When concentration exceeds a threshold,
genes activate. Key properties:

- **Diffusion-based**: no wiring between sender and receiver
- **Threshold-driven**: response fires at concentration, not on signal
- **Population-aware**: each cell contributes to and senses the shared pool
- **Robust to topology**: adding/removing cells changes concentration, not wiring

### Mapping to ecoPrimals

| Biological | ecoPrimals analog | Current | Target |
|-----------|-------------------|---------|--------|
| Autoinducer molecule | Impulse TOML in `impulses/active/` | SSH webhook trigger | `potential.sense` polling + threshold |
| Periplasm diffusion | Git repo sync (temporal.sync) | Direct SSH relay | Autonomous poll from each node |
| Concentration threshold | Pending impulse count > 0 | Always relay on trigger | Sense + conditional response |
| Gene activation | Script execution (sync, push) | Direct SSH command | Systemd timer / event loop |
| Quorum | Multiple gates pushing | Not considered | Rate-aware batching |

### Implementation path

**Phase 1 — Timer-based sensing (minimal change)**:
Each K-Derm node runs a systemd timer that periodically runs `potential.sense`.
If pending impulses or sync drift detected, it acts. No SSH trigger needed.

```ini
# peptidoglycan: /etc/systemd/system/pepti-sense.timer
[Timer]
OnCalendar=*:0/2
# Every 2 minutes, sense the periplasm
```

```ini
# peptidoglycan: /etc/systemd/system/pepti-sense.service
[Service]
ExecStart=/opt/ecoPrimals/infra/wateringHole/hooks/forgejo/pepti-sync-relay.sh
```

golgiBody-ext similarly runs a timer that checks if its Forgejo mirror is ahead
of GitHub and pushes if so. No SSH from peptidoglycan needed.

**Phase 2 — Songbird mesh relay (primal graduation)**:
Songbird's `mesh.publish` carries impulse notifications as lightweight signals.
Nodes subscribe to channels relevant to their K-Derm layer role. The relay
becomes a multicast rather than point-to-point SSH chain.

```
Gate fires impulse → songbird mesh.publish("impulse.fired", {repo, gate, ref})
  → peptidoglycan subscriber: received, pulling from Forgejo...
  → golgiBody-ext subscriber: received, checking sync state...
```

**Phase 3 — Capability-routed quorum (full graduation)**:
Nodes discover their role through `topology.roles` in the manifest and register
capabilities with songbird. Coordination routing is capability-based:

```toml
# peptidoglycan registers:
[capabilities]
"kderm.sync_mediator" = true
"potential.sense" = true

# golgiBody-ext registers:
[capabilities]
"kderm.external_publisher" = true
"mirror.github" = true
```

A gate pushing to Forgejo doesn't know or care which node handles sync mediation.
The manifest declares the roles, songbird routes the coordination, and each node
senses and responds based on its registered capabilities. The K-Derm topology
becomes discoverable rather than hardcoded.

---

## Bond Type Alignment

The transport evolution aligns with bond type semantics:

| Bond | Nanowire (current) | Quorum (target) | When to transition |
|------|-------------------|-----------------|-------------------|
| **Covalent** | SSH direct | SSH direct | Never — pili are permanent |
| **Metallic** | SSH fleet key | SSH fleet key + songbird relay | Phase 2 — dual-path |
| **Ionic** | SSH relay script | Songbird subscription + timer sensing | Phase 2 |
| **Weak** | `git push` from outer | `git push` from outer (timer-triggered) | Phase 1 |

Covalent bonds never evolve away from nanowire. They are the pili — direct,
authenticated, specific. Metallic bonds gain a secondary songbird path but retain
SSH for reliability. Ionic bonds transition to sensing-based coordination. Weak
bonds remain passive `git push` but trigger on local sensing rather than remote SSH.

---

## Coexistence During Shadow Period

Nanowire and quorum sensing coexist during the transition:

1. **Current**: SSH-triggered relay chain (nanowire only)
2. **Shadow**: Timer-based sensing + SSH fallback (both active, sensing is primary)
3. **Graduated**: Timer/songbird sensing only, SSH retained for metallic/covalent ops

The shadow period validates that autonomous sensing produces the same result as
direct SSH triggering. If a timer-sensed relay misses or delays, the SSH nanowire
catches it. When sensing proves reliable, the SSH triggers become the fallback
rather than the primary.

---

## Multi-Vendor and Air-Gap Implications

**Multi-vendor quorum**: When peptidoglycan spans multiple providers (DO + Hetzner),
each peptidoglycan node senses independently. Quorum sensing naturally handles this —
autoinducer diffusion doesn't require point-to-point wiring between peptidoglycan
instances. Each senses Forgejo, each syncs to its local outer membrane.

**Air-gapped gates**: biomeGate's async hardware workflow validates air-gap-like
resilience. Under nanowire, a delayed push requires the relay chain to fire when
the gate surfaces. Under quorum sensing, the timer on peptidoglycan catches the
new state on its next poll — no trigger needed. The async cadence is naturally
absorbed.

**WAN gates**: flockGate (WAN) pushes through higher-latency links. Quorum sensing
is latency-tolerant by nature — concentration threshold doesn't care about
propagation speed, only about eventual accumulation. A WAN gate's push arrives
later but is sensed identically.

---

## Phase 4: Sovereign Transport Envelope (Wave 121+)

Beyond quorum sensing for coordination, the transport layer gains a second
dimension: **opacity**. The Sovereign Transport Envelope separates the physical
topology (hardware, cables, switches) from the digital topology (how traffic
appears to external observers).

**Principle**: model on Tor's onion routing, but use our own primitives.

```
Physical topology: [ISP] → sporeGate → switches → gates      (designed for bandwidth)
Digital topology:  BTSP-wrapped hops → songBird relays      (designed for privacy)
```

The ecosystem already has the building blocks:

- **songbird-sovereign-onion**: Ed25519 identity, X25519 KEX, ChaCha20-Poly1305
  encrypted channels with `.onion`-style addressing (feature-gated)
- **bearDog ntor + cell crypto**: Tor Phase 2 circuit primitives delegated to
  bearDog as security provider
- **songBird relay tiers**: lineage-gated UDP relay → STUN → beacon mesh →
  sovereign .onion → full Tor circuits
- **Dark Forest Protocol**: zero-metadata discovery via encrypted beacons
- **cellMembrane TransportEndpoint.mesh_relay**: typed but not yet operational

The envelope evolves in phases:

1. **Audit**: verify all inter-gate traffic is encrypted; map plaintext IPC
2. **Relay activation**: enable songBird relay on golgiBody-ext with lineage auth
3. **Transport graduation**: wire cellMembrane's mesh_relay into songBird mesh
4. **Dark Forest deployment**: encrypted beacon discovery on LAN

The key design constraint: **primal code does not change**. Only the
TransportEndpoint resolution layer changes — from direct TCP to multi-hop
BTSP-encrypted relay. The abstraction boundary lives in cellMembrane.

See: `impulses/active/2026-06-22T07-40_sporeGate__wave121-sovereign-transport-envelope.toml`

---

## Relationship to Existing Standards

- `KDERM_DIDERM_APPLICATION.md` defines the physical layer. This document defines
  how coordination transport evolves within that physical layer.
- `IMPULSE_POTENTIAL_KDERM_INTERACTIONS.md` maps coordination artifacts to K-Derm
  zones. This document maps coordination *transport* evolution.
- `BONDING_MODEL_STANDARD.md` defines bond types. This document maps transport
  mechanisms to those bond types and defines when each transitions.
- `CAPABILITY_BASED_DISCOVERY_STANDARD.md` defines capability routing. Phase 3
  of this evolution depends on capability discovery being operational.

---

*"Nanowire is how the first cells coordinated — direct physical contact, pili
touching pili. Quorum sensing is how populations coordinate — molecules diffusing
through shared space, each cell sensing and responding to the collective state.
The ecosystem evolves from organism to population. The transport must follow."*
