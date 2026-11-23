# Gen5 — Impulse/Potential and K-Derm Interactions

**Authority**: wateringHole consensus (Wave 63+)
**Prerequisites**: `KDERM_DIDERM_APPLICATION.md`, `IMPULSE_POTENTIAL_STANDARD.md`, `CONTEXT_BRAID_STANDARD.md`
**Status**: Active — implementation live, graduation in progress
**Date**: May 31, 2026

---

## Overview

The K-Derm diderm envelope (`KDERM_DIDERM_APPLICATION.md`) defines the physical
infrastructure: inner membrane, peptidoglycan, outer membrane. The impulse/potential
system defines the coordination protocol: fire, propagate, sense, acknowledge.

This document maps how impulses and context braids interact with the K-Derm
layers — which bonds carry coordination traffic, which channel proteins mediate
access, and how the three-layer communication model (git/impulses/context) maps
to the five-layer cell envelope (cytoplasm → extracellular).

---

## Impulse Propagation Through the Envelope

An impulse fired from a gate traverses the K-Derm layers:

```
Cytoplasm (gate workspace)
  │
  │ membrane impulse.post → writes TOML to impulses/active/
  │ git add + commit + push
  │
  ▼ [Covalent bond: SSH to inner membrane]
Inner membrane (golgiBody Forgejo)
  │
  │ Forgejo receives push, stores in wateringHole repo
  │
  ▼ [Metallic bond: SSH fleet key]
Peptidoglycan (build/sync hub)
  │
  │ cascade-pull temporal sync picks up new impulse
  │ (peptidoglycan builds membrane binary but doesn't consume impulses)
  │
  ▼ [Ionic bond: BTSP-scoped, read-only]
Outer membrane (golgiBody-ext)
  │
  │ sporePrint can display impulse summaries (future)
  │ No write access — outer membrane cannot fire impulses
  │
  ▼ [Weak bond: passive diffusion]
Extracellular (GitHub)
  │
  │ GitHub mirror receives impulse TOML in wateringHole push
  │ External gates (flockGate) pull from GitHub, discover impulses
  │
```

### Bond Type Constraints on Coordination

| Bond | Direction | Impulse behavior | Context behavior |
|------|-----------|------------------|------------------|
| Covalent (gate → inner) | Bidirectional | Fire + ack (full access) | Weave + sense + clear |
| Metallic (inner ↔ peptidoglycan) | Bidirectional | Sync only (no fire/ack) | Sync only |
| Ionic (peptidoglycan → outer) | Read-forward | Read-only summary | Read-only summary |
| Weak (outer → extracellular) | Outward only | Mirror (passive) | Mirror (passive) |

Only **covalent bonds** permit creating coordination artifacts. Gates fire impulses
and weave context braids through their covalent connection to the inner membrane.
All other bonds carry coordination artifacts as read-only passengers on git sync.

### Channel Proteins for Coordination

| Boundary | Channel | Coordination traffic |
|----------|---------|---------------------|
| Cytoplasm → Inner | Aquaporin (always open) | `git push forgejo` carries impulses/context TOMLs |
| Inner → Peptidoglycan | Aquaporin (fleet SSH) | `cascade-pull` syncs entire wateringHole including impulses/ |
| Peptidoglycan → Outer | Gated ion | Method filtering: `content.serve` only, no `impulse.post` |
| Outer → Extracellular | Passive diffusion | GitHub push mirror includes impulses/ directory |

---

## Context Braids and Gate Identity

Context braids are inherently gate-scoped: `context/{gate}/repo.toml`. This maps
naturally to K-Derm identity:

| K-Derm layer | Can weave braids? | Can read braids? | Identity |
|-------------|-------------------|-----------------|----------|
| Cytoplasm (gate) | Yes — own gate only | All gates | `gate = "eastGate"` |
| Inner membrane | No (not a gate) | All (via Forgejo) | N/A |
| Peptidoglycan | No (not a gate) | All (via sync) | N/A |
| Outer membrane | No | Summary only | N/A |
| Extracellular (GitHub) | No | Mirror copy | N/A |

External collaborator gates (gen5 pattern) would weave braids under their own
directory: `context/gonzalesGate/`. Their braids propagate inward through the
WaterFall external sovereignty pattern, crossing from weak → ionic → metallic →
covalent as they're validated and absorbed.

---

## Graduated Primal Interactions at Each Layer

When primals graduate to handling coordination, their interactions respect the
K-Derm bond types:

### Covalent Zone (cytoplasm + inner membrane)

- **bearDog** signs impulses with Ed25519 (integrity within family seed)
- **rhizoCrypt** records impulse events in the DAG (provenance)
- **sweetGrass** validates context braid schema (data quality)
- **loamSpine** anchors completed braids to the ledger (permanence)

All of these operate within the covalent boundary. They require family seed
trust. External entities cannot trigger them.

### Metallic Zone (inner ↔ peptidoglycan)

- **nestGate** stores and pushes impulse/braid TOMLs to remotes (transport)
- **songbird** relays impulse notifications via mesh (speed)
- Build infrastructure on peptidoglycan builds the membrane binary that
  processes impulses

These cross between inner membrane and peptidoglycan. They use fleet SSH keys
(metallic bonds). They can transport coordination artifacts but cannot create them.

### Ionic Zone (peptidoglycan → outer)

- **sporePrint** could render impulse summaries on lab.primals.eco (future)
- BTSP-scoped tokens control which impulse metadata is visible externally
- Method filtering: `content.serve` permitted, `impulse.post` denied

### Weak Zone (outer → extracellular)

- GitHub receives impulse TOMLs as passive mirrors
- External gates pull from GitHub, discover impulses via `potential.sense`
- No write path: external entities cannot fire impulses into the ecosystem
  without first establishing a covalent bond (gate registration)

---

## Bonding Model for Coordination Graduation

The endosymbiosis path from `KDERM_DIDERM_APPLICATION.md` applies to
coordination patterns as well:

| Phase | Bond | Coordination capability |
|-------|------|------------------------|
| 1 External | Weak | Can read impulses from GitHub mirror |
| 2 Contract | Ionic | Can read impulses + braids from sporePrint API |
| 3 Fleet | Metallic | Can sync impulses via cascade-pull on peptidoglycan |
| 4 Internalized | Covalent | Can fire impulses, weave braids, sign with family seed |

A new collaborator starts at Phase 1 (weak: reads from GitHub). As trust
escalates, they gain coordination capabilities. At Phase 4, they're a full
gate participant: firing impulses, weaving braids, signed by bearDog, recorded
by rhizoCrypt.

---

## Multi-Vendor Implications

The K-Derm multi-vendor evolution path affects coordination:

**Multi-diderm** (DO + Hetzner): Each outer membrane has its own impulse mirror.
Impulses fired to one diderm propagate to the other through the shared periplasm
(Forgejo on inner membrane). The impulse travels: gate → inner membrane →
peptidoglycan → both outer membranes → both extracellular mirrors.

**Geo-distributed** (inner in nyc1, outer in eu-west): Latency affects impulse
propagation speed but not correctness. Temporal sync handles the eventual
consistency. A gate in Europe discovers impulses slightly later than a gate in
NYC, but the semantic guarantees hold.

**Nested diderm** (university lab): The lab's outer membrane is the ecosystem's
extracellular. Impulses enter the lab through the weak bond (GitHub mirror),
cross the lab's own K-Derm layers, and arrive at the collaborator's gate.
The nesting is transparent — impulse schema is the same at every level.

---

*"The nerve fires through the membrane. The membrane shapes which nerves can fire
and which can only listen. Covalent gates command. Metallic bridges transport.
Ionic channels filter. Weak bonds observe. The coordination architecture mirrors
the cell envelope because the cell envelope is the coordination architecture."*
