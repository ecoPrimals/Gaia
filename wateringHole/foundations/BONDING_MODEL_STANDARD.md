<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Bonding Model Standard — Organo-Metallo-Salt Model for Ecosystem Interactions

**Version**: 1.0.0
**Date**: May 26, 2026
**Status**: Active
**Authority**: wateringHole Consensus
**Related**: `K_DERM_TOPOLOGY_STANDARD.md`, `BTSP_PROTOCOL_STANDARD.md`, `SOVEREIGNTY_STANDARDS.md`, `GATE_SPRING_OWNERSHIP.md`
**Typed implementation**: `gardens/cellMembrane/crates/cellmembrane-types/src/envelope.rs` (`BondType`)
**Canonical bonding spec**: `primals/biomeOS/specs/NUCLEUS_BONDING_MODEL.md`

---

## Purpose

This document unifies the organo-metallo-salt bonding model — the five
bond types that govern all interactions between primals, gates, VPS
nodes, external services, and cross-family partnerships. The bonding
model determines what crosses each K-Derm envelope layer boundary,
which BTSP cipher suite is enforced, and how braid (provenance) is
handled at each transition.

---

## The Five Bond Types

Ordered by trust level (highest first):

### 1. Covalent — Shared Family, Full Trust

| Property | Value |
|----------|-------|
| **Trust model** | GeneticLineage (Nuclear tier) |
| **What it means** | Same family seed, same administrative domain, full capability access |
| **BTSP cipher** | `BTSP_NULL` minimum (all three ciphers allowed) |
| **K-Derm layer** | Cytoplasm, Plasma membrane |
| **Channel protein** | Aquaporin (always open) |
| **Braid policy** | Pass-through (no inspection) |
| **Genetics requirement** | Nuclear key (spawned fresh, never cloned) |
| **Example** | Primals within a single gate's NUCLEUS communicating via UDS IPC |

Covalent bonds are the default within a gate's cytoplasm. All 13 primals
in a full NUCLEUS share covalent bonding. Cross-gate covalent bonds
(Plasmodium mesh) require Songbird federation + family seed verification.

### 2. Metallic — Delocalized Fleet, Specialized but Coordinated

| Property | Value |
|----------|-------|
| **Trust model** | Organizational (Mito-Beacon family) |
| **What it means** | Fleet compute, shared organization, specialized roles |
| **BTSP cipher** | `BTSP_HMAC_PLAIN` minimum |
| **K-Derm layer** | Plasma membrane, Periplasm |
| **Channel protein** | Aquaporin (always open) |
| **Braid policy** | Pass-through |
| **Genetics requirement** | Mito-Beacon membership (discovery, NAT) |
| **Example** | GPU cluster dispatch across multiple gates in same family; HPC pool |

Metallic bonds model the delocalized electron sea from chemistry.
Compute resources are shared across a fleet without per-operation
contracts. The organizational trust (Mito-Beacon) ensures discovery
without sharing nuclear credentials.

### 3. Ionic — Contract-Based, Scoped Access

| Property | Value |
|----------|-------|
| **Trust model** | Contractual |
| **What it means** | Formal contract, BTSP scoped tokens, capability masks, metered |
| **BTSP cipher** | `BTSP_CHACHA20_POLY1305` (encrypted only, non-negotiable) |
| **K-Derm layer** | Periplasm, Outer membrane |
| **Channel protein** | Gated ion (BTSP token opens gate, method-level filtering) |
| **Braid policy** | Verify (braid metadata checked at boundary) |
| **Genetics requirement** | None (contract-based, not family-based) |
| **Example** | University lab consuming HPC compute; ABG ionic compute sharing |

Ionic bonds are metered. Usage is tracked (call count, byte volume).
Contracts have lifecycle: Proposed → Active → Sealed (with provenance
seal containing merkle_root and braid_id). Capability deny lists
(`storage.*`, `dag.*`, `braid.*`, `crypto.*`) prevent braid internals
from crossing ionic boundaries.

### 4. Ceremony — Time-Bound Decay

| Property | Value |
|----------|-------|
| **Trust model** | Temporal |
| **What it means** | Time-limited covalent access that decays to ionic then weak |
| **BTSP cipher** | Matches current decay phase |
| **K-Derm layer** | Any (depends on decay phase) |
| **Channel protein** | Voltage-gated (time-bound gate with decay) |
| **Braid policy** | Verify |
| **Genetics requirement** | Nuclear during covalent phase, Mito-Beacon after decay |
| **Example** | Workshop access, visiting researcher, human entropy ceremony |

Ceremony bonds model voltage-gated ion channels: the gate opens for a
defined period, then progressively closes. A visiting researcher starts
with covalent access (full lab), decays to ionic (compute only, no
storage), then to weak (read-only, eventually expires).

### 5. Weak — No Active Transport, Read-Only

| Property | Value |
|----------|-------|
| **Trust model** | ZeroTrust |
| **What it means** | Public, read-only, passive API, no family trust |
| **BTSP cipher** | `BTSP_CHACHA20_POLY1305` (or TLS 1.3 at extracellular) |
| **K-Derm layer** | Outer membrane, Extracellular |
| **Channel protein** | Passive diffusion (no active transport) |
| **Braid policy** | Block (braid stripped, only results cross) |
| **Genetics requirement** | None |
| **Example** | Public website visitor; API consumer without authentication |

Weak bonds are the default for all traffic from the extracellular space
(Dark Forest principle). Traffic escalates to stronger bond types only
after authentication.

---

## Composite: OrganoMetalSalt

OrganoMetalSalt is not a sixth bond type but a **composite topology**
where a single workload crosses multiple bond-type boundaries:

```
Covalent core (cytoplasm)
  → Metallic fleet (plasma membrane + periplasm)
    → Ionic edge (outer membrane)
```

BTSP cipher follows the weakest boundary crossed. A workload originating
in a covalent cytoplasm and reaching an ionic partner through the
periplasm must use `BTSP_CHACHA20_POLY1305` for the ionic segment.

The name comes from chemistry: organo (carbon-based, covalent) + metallo
(metal coordination, delocalized) + salt (ionic crystal lattice).

---

## Bonding × K-Derm Layer Matrix

| Bond Type | Cytoplasm | Plasma Membrane | Periplasm | Outer Membrane | Extracellular |
|-----------|:---------:|:---------------:|:---------:|:--------------:|:-------------:|
| Covalent  | **HOME**  | crosses         | —         | —              | —             |
| Metallic  | —         | crosses         | crosses   | —              | —             |
| Ionic     | —         | —               | crosses   | crosses        | —             |
| Ceremony  | (decaying)| (decaying)      | (decaying)| —              | —             |
| Weak      | —         | —               | —         | crosses        | **HOME**      |

**HOME** = the bond type's natural habitat. **crosses** = may transit
through. **(decaying)** = Ceremony bonds pass through but lose trust
level over time.

---

## Bonding × BTSP Cipher Enforcement

From `BTSP_PROTOCOL_STANDARD.md`:

| Bond Type | Trust Model | Minimum Cipher | Negotiable Down To |
|-----------|-------------|----------------|---------------------|
| Covalent | GeneticLineage | `BTSP_NULL` | `BTSP_NULL` (all three allowed) |
| Metallic | Organizational | `BTSP_HMAC_PLAIN` | `BTSP_HMAC_PLAIN` |
| Ionic | Contractual | `BTSP_CHACHA20_POLY1305` | None (encrypted only) |
| Weak | ZeroTrust | `BTSP_CHACHA20_POLY1305` | None (encrypted only) |
| OrganoMetalSalt | Per-scope | Covalent core → `BTSP_NULL`, ionic edge → encrypted |

---

## Bonding × Genetics Alignment

From `GATE_SPRING_OWNERSHIP.md`:

| Genetics Tier | Type | Role | Cloneable | Minimum Bond |
|---------------|------|------|-----------|--------------|
| 1 | Mito-Beacon | Discovery, NAT, metadata | Yes | Metallic, Ionic |
| 2 | Nuclear | Permissions, auth, sessions | No (spawn fresh) | Covalent |
| 3 | Tag | Open channels (deprecated) | Yes | — |

All covalent bonds require Nuclear (Tier 2) trust — nuclear genetics
spawned fresh per generation. Ionic and metallic bonds require at minimum
Mito-Beacon (Tier 1) trust. The two-phase BTSP model (Phase 1:
mito-beacon tunnel, Phase 2: nuclear session) ensures discovery never
exposes authorization material.

---

## Bonding × Channel Protein Mapping

| Channel Protein | Bond Types | Behavior | K-Derm Layer |
|-----------------|------------|----------|--------------|
| **Aquaporin** | Covalent, Metallic | Always open, shared family seed | Cytoplasm, Plasma |
| **Gated ion** | Ionic | BTSP scoped token opens gate | Periplasm, Outer |
| **Voltage-gated** | Ceremony | Time-bound, decaying | Any (follows decay) |
| **Passive diffusion** | Weak | Read-only, no active transport | Outer, Extracellular |

Deploy graph `[graph.bonding_policy]` sections map directly:
```toml
tower_internal = "covalent"
cross_family = "ionic"
public_edge = "weak"
```

---

## Bonding Escalation Path

Traffic naturally escalates from weaker to stronger bonds:

```
Weak (extracellular)
  → Ionic (outer membrane — BTSP scoped token)
    → Metallic (periplasm — organizational trust)
      → Covalent (plasma membrane — family seed verification)
```

Each escalation requires progressively stronger authentication:
1. Weak → Ionic: Present BTSP scoped token
2. Ionic → Metallic: Prove Mito-Beacon membership
3. Metallic → Covalent: Complete nuclear session (fresh spawn)

The reverse path (covalent → weak) is **Ceremony** — a controlled decay
that progressively restricts access.

---

## Bonding in NUCLEUS Atomics

| Atomic | Internal Bond | Cross-Atomic Bond | External Bond |
|--------|---------------|-------------------|---------------|
| Tower (Electron) | Covalent (UDS IPC) | Covalent (mediates for Node/Nest) | Ionic/Weak (federation) |
| Node (Proton) | Covalent | Covalent (via Tower) | — (never directly exposed) |
| Nest (Neutron) | Covalent | Covalent (via Tower) | — (never directly exposed) |
| NUCLEUS (Atom) | Covalent | Metallic (fleet), Ionic (cross-family) | Weak (extracellular) |

Tower is the electron shell that mediates all boundary crossings.
Node and Nest primals never communicate directly with external systems —
all external bonding passes through Tower's capability surface.

---

## Validation

### primalSpring scenarios

| Scenario | Validates |
|----------|-----------|
| `s_ionic_bond` | Ionic contract lifecycle: propose → active → sealed |
| `s_covalent_bond` | Covalent mesh properties |
| `s_covalent_mesh` | Cross-gate covalent + Songbird federation |
| `s_sovereignty_parity` | `routing_config_reference.toml` backend types match bonding |
| `s_dark_forest_gate` | Enclave bonding policies + BTSP integrity |
| `s_kderm_boundary` (planned) | Deploy graph bonding_policy matches K-Derm layer rules |

### cellMembrane tests

`envelope.rs` tests: 27 tests covering bond ↔ channel protein mapping,
`permitted_inbound_bonds()` per layer, and `BoundaryPolicy` assembly.

---

## Cross-References

| Document | Relationship |
|----------|--------------|
| `K_DERM_TOPOLOGY_STANDARD.md` | Envelope layers where bonds are placed |
| `BTSP_PROTOCOL_STANDARD.md` | Cipher enforcement per bond type |
| `SOVEREIGNTY_STANDARDS.md` | Trust layers (Intracellular/Inner/Outer/Extracellular) |
| `GATE_SPRING_OWNERSHIP.md` | Genetics tier → bond minimum mapping |
| `MEMBRANE_CHANNEL_ARCHITECTURE.md` | Three channels + crypto layers |
| `DARK_FOREST_GLACIAL_GATE_STANDARD.md` | Enclave bonding policies |
| `primals/biomeOS/specs/NUCLEUS_BONDING_MODEL.md` | Canonical bonding spec |
| `cellmembrane-types/src/envelope.rs` | Rust typed implementation |
