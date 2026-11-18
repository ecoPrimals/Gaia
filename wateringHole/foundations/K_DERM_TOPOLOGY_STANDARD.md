<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# K-Derm Topology Standard — Cell Envelope Model for Sovereign Infrastructure

**Version**: 1.0.0
**Date**: May 26, 2026
**Status**: Active
**Authority**: wateringHole Consensus (canonical spec: `gardens/cellMembrane/specs/K_DERM_TOPOLOGY.md`)
**Related**: `BONDING_MODEL_STANDARD.md`, `SOVEREIGNTY_STANDARDS.md`, `BTSP_PROTOCOL_STANDARD.md`, `GATE_SPRING_OWNERSHIP.md`, `MEMBRANE_CHANNEL_ARCHITECTURE.md`
**Typed implementation**: `gardens/cellMembrane/crates/cellmembrane-types/src/envelope.rs`

---

## What K-Derm Is

K-Derm is the cell envelope topology model for sovereign infrastructure.
It models directly from cell envelope biology — monoderm/diderm bacteria,
eukaryotic organelle membranes, vesicle transport, endosymbiosis — and
extends into a network topology model.

**K-NOME is how we build. K-Derm is how what we build is shaped.**

K-Derm replaces the ambiguous "inner/outer membrane" terminology that
conflicted across ecosystem documents (see §5: Franklin's Current Resolution).
All envelope layers use **absolute positions** named from inside out.

---

## Section 1: Envelope Topologies

Two topologies are defined, matching bacterial cell envelope biology:

### Monoderm (single boundary)

```
cytoplasm (gate NUCLEUS) → plasma membrane (gate firewall) → environment
```

Single membrane boundary. Gate directly on network, no VPS relay.
Example: ironGate on home LAN.

### Diderm (double boundary)

```
cytoplasm (gate NUCLEUS, UDS IPC)
  → plasma membrane (gate firewall)
    → periplasm (VPS relay, routing, telemetry, attribution)
      → outer membrane (VPS channels: Signal/Relay/Surface)
        → extracellular (public internet)
```

Two membrane boundaries with a periplasmic space between them.
Example: ironGate + VPS `membrane-relay` ([RELAY_PUBLIC]).

### Extended topologies

| Topology | Structure | Example |
|----------|-----------|---------|
| Monoderm | Cytoplasm → plasma → environment | Home lab: ironGate on LAN |
| Diderm | Cytoplasm → plasma → periplasm → outer → environment | Production: ironGate + VPS |
| Multi-diderm | Shared periplasm, multiple outer membranes | Future: `membrane-nyc` + `membrane-eu` |
| Nested diderm | One system's outer membrane = another's periplasm | University lab inside campus |

---

## Section 2: Absolute Envelope Layers

Five layers, ordered inside-out. Names are fixed and never relative.

| Layer | Position | What Occupies It | Bond Types Within |
|-------|----------|------------------|-------------------|
| **Cytoplasm** | Innermost | NUCLEUS processes, UDS IPC, shared memory | Covalent only |
| **Plasma membrane** | Gate boundary | Gate firewall (UFW/nftables) | Covalent, Metallic |
| **Periplasm** | Between plasma and outer | VPS relay, routing, telemetry, attribution | Ionic, Metallic |
| **Outer membrane** | VPS boundary | VPS channels (Signal/Relay/Surface) | Weak, Ionic |
| **Extracellular** | Outermost | Public internet | Weak |

**Invariant**: The VPS is ALWAYS in the periplasm + outer membrane position.
The gate ALWAYS owns the plasma membrane. These positions do not change
regardless of how many VPS nodes exist.

---

## Section 3: NUCLEUS Atomics in the Envelope

The particle model (Tower/Node/Nest/NUCLEUS) maps to envelope layers:

### Cytoplasm: Full NUCLEUS Interior

All 13 primals run in the cytoplasm on the gate. The atomic tiers define
capability groupings, not layer placement — all atomics share the
cytoplasmic space and communicate via UDS IPC (covalent bond).

| Atomic | Particle | Primals | Cytoplasm Role |
|--------|----------|---------|----------------|
| Tower | Electron | BearDog + Songbird + skunkBat | Security, federation, identity verification |
| Node | Proton | Tower + ToadStool + barraCuda + coralReef | Compute, sandboxing, GPU dispatch |
| Nest | Neutron | Tower + NestGate + rhizoCrypt + loamSpine + sweetGrass | Storage, provenance, attribution, certificates |
| NUCLEUS | Atom | Tower + Node + Nest (9 unique primals) | Complete sovereign composition |
| Meta-tier | Cross-atomic | biomeOS + Squirrel + petalTongue | Orchestration, AI, interface |

### Plasma Membrane: Tower Mediates All Boundary Crossings

The Tower atomic (electron shell) mediates all traffic crossing the plasma
membrane. BearDog authenticates, Songbird federates, skunkBat correlates.
No Node or Nest primal communicates directly with the periplasm — traffic
flows through Tower's capability surface.

```
cytoplasm [Node + Nest primals]
  → Tower primals (electron shell)
    → plasma membrane (gate firewall)
      → periplasm
```

### Periplasm: Routing, Attribution, Telemetry

The periplasm contains VPS-side processes that route, classify, and
attribute traffic between the plasma membrane (gate) and the outer
membrane (public-facing channels):

| Periplasm Process | Source Primal | Function |
|-------------------|--------------|----------|
| Songbird TURN relay | Songbird | NAT traversal, cross-gate federation |
| RustDesk relay | skunkBat | Remote desktop bridge |
| Content routing | NestGate (via config) | `routing_config.toml` dispatch |
| Telemetry/shadow | skunkBat | Shadow validation, latency comparison |
| Braid verification | sweetGrass (via policy) | Provenance attribution at boundary |
| BTSP token validation | BearDog | Scoped ionic token verification |

### Outer Membrane: Three Channels to the Extracellular

The outer membrane exposes exactly three channels to the internet,
corresponding to the membrane channel architecture:

| Channel | Port/Protocol | What Crosses | Bond Type |
|---------|---------------|--------------|-----------|
| **Signal** | :443 (Caddy/HTTPS) | Signed content, verified provenance | Ionic |
| **Relay** | :3478 (TURN) | Songbird federation, NAT traversal | Ionic → Covalent (once authenticated) |
| **Surface** | :21115-21116 (RustDesk) | Remote desktop sessions | Weak → Ionic (on session auth) |

### Extracellular: Dark Forest

The public internet. All traffic arriving from the extracellular space is
treated as **Weak** bond until authenticated. The Dark Forest principle
applies: assume hostile intent until proven otherwise.

---

## Section 4: Bonding at Each Envelope Layer

The organo-metallo-salt bonding model maps to envelope positions.
Each layer boundary has specific bond types that may cross it.

| Envelope Layer | Bond Types Crossing | Channel Protein | Braid Policy | What Crosses | What Does NOT Cross |
|----------------|---------------------|-----------------|--------------|--------------|---------------------|
| Outer membrane → environment | Weak, Ionic | Passive diffusion, Gated ion | Block | Public content, scoped API tokens | Family seed, braid internals, dag.* |
| Periplasm (routing) | Ionic, Metallic | Gated ion, Aquaporin | Verify | Classified requests, telemetry, relay | Raw covalent RPC, FAMILY_SEED |
| Plasma membrane (gate) | Covalent, Metallic | Aquaporin | Pass-through | Full capability, braid, workloads | Nothing blocked within family |
| Cytoplasm (NUCLEUS) | Covalent only | Aquaporin | Pass-through | UDS IPC, shared memory | (everything stays) |

### Channel Proteins

| Channel Protein | Mediates Bond | Behavior |
|-----------------|---------------|----------|
| **Aquaporin** | Covalent, Metallic | Always open — shared family seed, free-flowing |
| **Gated ion** | Ionic | BTSP scoped token opens the gate, method-level filtering |
| **Voltage-gated** | Ceremony | Time-bound decay: covalent → ionic → weak over time |
| **Passive diffusion** | Weak | Read-only, no active transport |

### Braid Policy Per Layer

Braid (sweetGrass provenance attribution) is the vesicle coat:

| Policy | Layer | Behavior |
|--------|-------|----------|
| **Pass-through** | Cytoplasm, Plasma membrane | Braid passes without inspection (covalent/metallic) |
| **Verify** | Periplasm | Braid metadata verified at boundary (ionic) |
| **Block** | Outer membrane, Extracellular | Braid stripped — only results cross, not provenance (weak) |

---

## Section 5: Franklin's Current Resolution

### The Problem

Three gen4 documents use conflicting inner/outer labels:

| Document | "Inner membrane" | "Outer membrane" |
|----------|------------------|------------------|
| `SOVEREIGN_HPC_EVOLUTION.md` | Gate firewall | VPS channels |
| `CELLMEMBRANE_FIELDMOUSE_ARCHITECTURE.md` | VPS relay | GitHub/CDN |
| `CELLMEMBRANE_ARCHITECTURE.md` | (avoided) | (avoided) |

This is the Franklin's Current problem: two valid reference frames
produce opposite labels for the same component, like conventional current
vs electron flow. The gram-positive/gram-negative labels compound it —
they encode a staining technique, not architecture.

### The Resolution

K-Derm replaces all relative labels with absolute positions:

| Old Term | K-Derm Canonical Term | Why |
|----------|----------------------|-----|
| "inner membrane" (SOVEREIGN_HPC) | Plasma membrane | Always the gate boundary |
| "outer membrane" (SOVEREIGN_HPC) | Outer membrane | Correct — VPS channels facing internet |
| "inner membrane" (FIELDMOUSE) | Periplasm + outer membrane | Was using "inner" relative to GitHub |
| "gram-negative" | Diderm | Describes structure, not staining artifact |
| "gram-positive" | Monoderm | Same |
| "cell wall" | (no equivalent) | Substrate provider; not a membrane layer |

Old documents are **fossil record** — they are not modified. This standard
is canonical; old terms are referenced with this reconciliation table.

---

## Section 6: K-Derm Extensions Beyond Biology

### 6a: Recursive Nesting (Organelle Membranes)

Every administrative domain (lab, department, campus, consortium) is its
own K-Derm system, and they nest recursively:

```
Consortium (outer membrane)
  → consortium periplasm (federated routing)
    → University (outer membrane)
      → campus periplasm (campus routing, bonding classification)
        → Lab (plasma membrane)
          → lab cytoplasm (covalent HPC mesh)
            → HPC organelle (own double membrane: scheduler + compute pool)
```

Each level is a self-contained envelope. Bonding model at each boundary
is independently configured.

### 6b: Endosymbiosis (Sovereignty Escalation)

Infrastructure absorption mirrors mitochondrial endosymbiosis:

| Phase | Bond | Topology | Biological Parallel |
|-------|------|----------|---------------------|
| 1 (External) | Weak | Separate organism | Free-living bacterium |
| 2 (Contract) | Ionic | Symbiotic, own membrane | Early symbiont |
| 3 (Fleet) | Metallic | Delocalized, specialized | Proto-mitochondrion |
| 4 (Internalized) | Covalent | Membrane becomes host layer | Mitochondrion |

The external system's outer membrane *becomes* a layer in the host's
envelope. The boundary transforms from a trust barrier into a functional
compartment.

### 6c: Vesicle Transport (Braid as Membrane Coat)

Workloads wrapped in sweetGrass braid carry provenance attribution that
acts as a SNARE-protein targeting signal:

1. **Budding**: Workload originates. sweetGrass creates braid wrapping
   DAG session + data references + attribution chain.
2. **Periplasm transit**: Braid-wrapped workload traverses periplasm.
   Routing reads braid metadata to classify bonding type and destination.
3. **Fusion**: Target membrane accepts the vesicle because braid proves
   data alignment — DAG references verified via rhizoCrypt, attribution
   chain intact, ionic contract authorizes compute.
4. **Content release**: Inside the target compartment, braid is verified
   and the workload executes.

Pre-braided workloads cross faster because the membrane doesn't need to
verify provenance from scratch (facilitated diffusion).

---

## Section 7: BTSP Cipher Mapping

K-Derm layers align with BTSP cipher enforcement from `BTSP_PROTOCOL_STANDARD.md`:

| Envelope Layer | Trust Model | Minimum Cipher | Negotiable |
|----------------|-------------|----------------|------------|
| Cytoplasm | Covalent (GeneticLineage) | `BTSP_NULL` | All three allowed |
| Plasma membrane | Covalent + Metallic | `BTSP_HMAC_PLAIN` | Down to `BTSP_NULL` for same-family |
| Periplasm | Ionic + Metallic | `BTSP_CHACHA20_POLY1305` | None — encrypted only |
| Outer membrane | Ionic + Weak | `BTSP_CHACHA20_POLY1305` | None — encrypted only |
| Extracellular | Weak (ZeroTrust) | TLS 1.3 (external) | No BTSP — HTTPS only |

**OrganoMetalSalt** composite bonds span multiple layers: covalent core
(cytoplasm) → metallic fleet (plasma + periplasm) → ionic edge (outer).
The BTSP cipher follows the weakest boundary crossed.

---

## Section 8: Typed Interface

The K-Derm model is encoded in `cellmembrane-types` (`envelope.rs`):

| Type | Encodes | Key Methods |
|------|---------|-------------|
| `EnvelopeTopology` | Monoderm / Diderm | `layers()`, `boundary_count()`, `has_periplasm()` |
| `EnvelopeLayer` | Cytoplasm / Plasma / Periplasm / Outer / Extracellular | `is_boundary()`, `is_compartment()`, `permitted_inbound_bonds()` |
| `BondType` | Covalent / Metallic / Ionic / Ceremony / Weak | `channel_protein()` |
| `ChannelProtein` | Aquaporin / GatedIon / VoltageGated / PassiveDiffusion | `permitted_bonds()` |
| `BraidPolicy` | PassThrough / Verify / Block | `for_bond()` |
| `BoundaryPolicy` | Per-layer composite policy | `for_layer()`, `permits_bond()`, `has_channel_protein()` |
| `MembraneConfig.topology` | Configuration field | `effective_topology()` |

Deploy graphs reference these types in `[graph.bonding_policy]` sections:
`tower_internal = "covalent"`, `cross_family = "ionic"`, `public_edge = "weak"`.

---

## Section 9: Validation

### primalSpring validation (planned)

| Scenario | Validates |
|----------|-----------|
| `s_kderm_boundary` | Deploy graph `bonding_policy` matches K-Derm layer rules |
| `s_atomic_compositions` (existing) | Composition graph primals placed in correct atomic tiers |
| `s_sovereignty_parity` (existing) | `routing_config_reference.toml` backend types match K-Derm bonding |

### cellMembrane validation (existing)

`cellmembrane-types/tests/envelope.rs` — 27 tests covering:
- Monoderm has 3 layers, Diderm has 5 layers
- Boundary count derivation
- Permitted inbound bonds per layer
- Channel protein ↔ bond type mapping
- Braid policy defaults
- BoundaryPolicy assembly from layer capabilities
- Serde round-trip for all K-Derm types

### benchScale integration

`topologies/nucleus/kderm_diderm_membrane.yaml` — 5-node boundary
crossing validation in reproducible test environments.

---

## Cross-References

| Document | Location | Relationship |
|----------|----------|--------------|
| K-Derm canonical spec | `gardens/cellMembrane/specs/K_DERM_TOPOLOGY.md` | Source of truth |
| Bonding model standard | `wateringHole/BONDING_MODEL_STANDARD.md` | Bond types + BTSP ciphers |
| Sovereignty standards | `wateringHole/SOVEREIGNTY_STANDARDS.md` | Trust layers (pre-K-Derm vocabulary) |
| BTSP protocol | `wateringHole/BTSP_PROTOCOL_STANDARD.md` | Cipher enforcement per bond type |
| NUCLEUS spring alignment | `wateringHole/GATE_SPRING_OWNERSHIP.md` | Atomic model + genetics |
| Membrane channels | `wateringHole/MEMBRANE_CHANNEL_ARCHITECTURE.md` | Three-channel architecture |
| cellMembrane architecture | `gardens/cellMembrane/specs/CELLMEMBRANE_ARCHITECTURE.md` | Operational membrane model |
| K-NOME methodology | `infra/whitePaper/gen3/about/K_NOME_PROGRAMMING.md` | Parallel methodology |
| gen4 reconciliation | `infra/whitePaper/gen4/architecture/K_DERM_RECONCILIATION.md` | Bridges gen4 gram-negative → K-Derm |
| Envelope types | `gardens/cellMembrane/crates/cellmembrane-types/src/envelope.rs` | Rust implementation |
