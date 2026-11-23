# Distributed Covalent Deployment

**Status**: Architecture + implementation guide  
**Scope**: Multi-household compute via covalent-bonded gates  
**Last updated**: 2026-06-13 (Wave 111, reviewed 155h: **9-gate mesh LIVE** — westGate + strandGate Tower LIVE. Architecture still current. Gate fleet expanded.)

---

## Overview

A covalent family mesh extends NUCLEUS across multiple physical locations —
gates in different households, connected via cellMembrane relay over WAN.
The mesh handles the realities of residential computing: power cycles, owner
foreground load, ISP variability, and geographic daylight patterns.

cellMembrane acts as the **intra-layer** — the always-available rendezvous
that gates connect through when direct paths are unavailable.

```
                    cellMembrane VPS
                   (TURN relay, TLS,
                    rendezvous point)
                    /              \
              WAN / Songbird        \ WAN / Songbird
                /                    \
    ┌──────────────────┐    ┌──────────────────┐
    │  LAN Cluster A   │    │  flockGate        │
    │  (Michigan home)  │    │  (remote household)│
    │                   │    │                   │
    │  ironGate ──┐     │    │  i9-13900K        │
    │  eastGate ──┤ 1G  │    │  RTX 3070 Ti      │
    │  northGate ─┤     │    │  64 GB DDR5       │
    │  westGate ──┤     │    │  Ubuntu 24.04     │
    │  strandGate ┘     │    │                   │
    └──────────────────┘    └──────────────────┘
```

## Trust Model

All gates in a distributed covalent mesh share a **family seed** — the same
cryptographic root used for BirdSong discovery and BTSP session establishment.

| Layer | What | Trust level |
|-------|------|-------------|
| Gate ↔ Gate (LAN) | BirdSong UDP multicast, BTSP | Covalent (full) |
| Gate ↔ Gate (WAN) | Songbird TCP fallback via cellMembrane TURN | Covalent (full — BTSP encrypts through relay) |
| Gate ↔ cellMembrane | Tower services, TURN relay | Controlled (you operate VPS; provider has hypervisor) |
| cellMembrane ↔ Internet | TLS, DNS, content serving | Outer membrane (public) |

The cellMembrane VPS **never sees plaintext family traffic** — BTSP tunnels
are end-to-end encrypted between gates. The VPS only relays opaque bytes.

## cellMembrane as Intra-Layer

The VPS serves three roles for distributed gates:

### 1. Rendezvous (always-on)

Gates behind residential NAT cannot accept inbound connections. cellMembrane
provides the stable endpoint for:
- Songbird TURN relay (UDP :3478)
- RustDesk relay for remote desktop access (:21115-21117)
- BirdSong TCP fallback discovery (when LAN multicast is unavailable)

### 2. State Awareness

cellMembrane tracks which gates are currently reachable. When a gate goes
offline (power cycle, sleep, ISP outage), the relay notes the absence.
When it returns, Songbird re-establishes the mesh automatically.

### 3. Workload Routing

For cross-household dispatch, cellMembrane routing means:
- Latency-tolerant work (overnight GPU batches) routes to remote gates
- Latency-sensitive work (interactive, sub-100ms) stays on LAN
- Data-heavy work pre-stages artifacts via NestGate before dispatch

## Compute Scheduling Awareness

Distributed residential compute must handle availability that shifts with:

### Power Cycles

Gates sleep, reboot, lose power. toadStool workloads must:
- **Checkpoint** progress periodically (configurable interval)
- **Resume** on the same or different gate after reconnection
- **Timeout** gracefully — Songbird health probes detect gate absence

### Owner Foreground Load

toadStool's `max_guest_load` parameter (default 50% for remote gates like
flockGate) means dispatched GPU work yields when the owner starts gaming,
dev work, or other foreground tasks. The dispatch pattern:

1. toadStool monitors GPU/CPU utilization on the gate
2. When owner load exceeds threshold, guest workloads are paused
3. When load drops below threshold, workloads resume
4. If paused longer than configurable timeout, checkpoint and migrate

### Geographic Daylight Patterns

Gates in different timezones have complementary idle windows:
- Michigan LAN gates idle overnight (EST midnight-8am)
- Remote gates in other timezones may be idle during Michigan daytime
- Batch workloads can follow the idle window around the mesh

### Network Variability

Residential ISPs have asymmetric bandwidth, occasional outages, and
variable latency. The mesh handles this via:
- Songbird TURN relay as fallback (never requires port forwarding)
- STUN → hole-punch → relay escalation (sovereignty-first)
- Pre-dispatch dependency staging (avoid real-time large transfers)

## Pre-Dispatch Data Staging

From primalSpring Wave 33: the `validation::dependency` pattern handles
BLAKE3-verified input artifact staging before workload dispatch.

For distributed dispatch:

```rust
use primalspring::validation::dependency::{DependencySpec, validate_dependencies_at};

let deps = vec![
    DependencySpec::required("data/genome.fasta", Some("abc123...")),
    DependencySpec::required("config/pipeline.toml", None),
];

// Verify artifacts staged at remote gate before dispatch
let report = validate_dependencies_at(&deps, &remote_workdir);
if !report.is_ok() {
    // Stage missing artifacts via NestGate content.put
    stage_via_nestgate(&deps, remote_gate_id)?;
}
```

This prevents dispatching work to a gate that doesn't have the input data,
avoiding expensive real-time transfers over WAN.

## flockGate Bootstrap Sequence

### Prerequisites

- cellMembrane VPS operational (TURN + RustDesk) -- **DONE**
- Family seed available -- **DONE** (irongate-sovereign family)
- Remote machine accessible via RustDesk -- **DONE**
- plasmidBin binaries for x86_64-unknown-linux-musl -- **DONE** (14/14 fresh, Wave 103)
- plasmidBin depot accessible from WAN -- **SHIPPED** (Wave 105: `plasmid.fetch --source wan` + `caddy.depot.provision`). Production deployment + flockGate validation pending.

### Steps

1. **Remote access**: RustDesk from cellMembrane to flockGate machine
2. **Bootstrap**: `bootstrap_gate.sh --join-family` with family seed
3. **Deploy**: Node Atomic (BearDog + Songbird + ToadStool + barraCuda + coralReef)
4. **Discover**: Songbird TCP/WAN fallback via cellMembrane TURN
5. **Validate NAT**: STUN probe → hole-punch attempt → TURN relay fallback
6. **Test dispatch**: toadStool workload from ironGate → flockGate via relay
7. **Shadow compare**: `shadow_comparator::compare_paths` TURN vs cloudflared

### NAT Traversal Escalation

Songbird implements sovereignty-first STUN escalation:

1. **Lineage STUN** — self-hosted (if available)
2. **Self-hosted STUN** — cellMembrane VPS
3. **Public STUN** — last resort (leaks IP to third party)
4. **Hole-punch** — direct UDP if both sides have STUN-resolved addresses
5. **TURN relay** — cellMembrane relays if punch fails (most residential NAT)

Most residential NAT will land on TURN relay. This is acceptable — the relay
is sovereign (our VPS), BTSP-encrypted, and bandwidth sufficient for
workload coordination + result retrieval.

## Plasmodium Collective

When 2+ NUCLEUS instances bond covalently, biomeOS recognizes the
**Plasmodium** — a collective organism with aggregated capabilities.

```bash
biomeos plasmodium status
# Plasmodium: irongate-sovereign-family
# Gates: ironGate (LAN), eastGate (LAN), flockGate (WAN)
# Capabilities: 13 primals × 3 gates (deduped)
# Aggregate: 72+ cores, ~72 GB VRAM, ~192 GB RAM
```

The Plasmodium enables:
- Cross-gate `capability.call` dispatch (resolved by biomeOS routing)
- Aggregated GPU VRAM for large model inference
- Distributed NestGate storage with cross-gate replication
- Family-scoped socket naming (`{primal}-{family_id}.sock`)

## References

- `FAMILY_HPC_MODEL.md` — personal-PC-first model, yield semantics
- `MEMBRANE_CHANNEL_ARCHITECTURE.md` — cellMembrane channels
- `SOVEREIGNTY_STANDARDS.md` — calibrate → shadow → cutover
- `GLACIAL_SHIFT_READINESS.md` — deployment tracking
- `HARDWARE.md` — gate inventory and specifications
- `graphs/multi_node/three_node_covalent_cross_network.toml` — WAN topology
- `gardens/projectNUCLEUS/gates/flockgate.toml` — flockGate config
