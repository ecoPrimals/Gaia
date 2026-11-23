# VPS Surface Minimization — Evolution Path to Inner Membrane Sovereignty

**Date**: 2026-06-12  
**From**: eastGate overwatch (cellMembrane)  
**Wave**: 111+  
**Status**: PLANNING — ready for incremental execution

---

## Current State

| Node | Role | Cost/mo | Location |
|------|------|---------|----------|
| golgiBody ([RELAY_PUBLIC]) | Main WAN VPS — NUCLEUS 13/13, Forgejo, depot, Caddy TLS | $12 | DigitalOcean NYC1 |
| fieldMouse (canary) | Warm standby — NUCLEUS 13/13, previous-good binaries | $12 | DigitalOcean NYC1 |
| **Total rental surface** | | **$24/mo** | |

## Target State

Minimize rental VPS surface to the absolute minimum required for WAN reachability (public IP + TLS termination). All compute, storage, and internal services migrate to owned hardware on the inner membrane.

| Node | Role | Cost/mo | Location |
|------|------|---------|----------|
| golgiBody-slim | WAN relay only: Caddy TLS, songBird federation, sporePrint CDN | $6 | DigitalOcean (s-1vcpu-1gb) |
| NUC-canary | Replaces fieldMouse droplet — full NUCLEUS canary on owned hardware | $0 | Inner membrane (NUC) |
| **Total rental surface** | | **$6/mo** | Savings: $18/mo / $216/yr |

## Migration Phases

### Phase 1: NUC as Canary (Replaces fieldMouse Droplet)

**Hardware**: Intel NUC (available, powered on inner membrane)  
**Profile**: `canary-fieldmouse` (same 13/13, same gate.bootstrap)  
**Network**: LAN mesh (covalent bond) + WireGuard tunnel for WAN failover

1. `gate.bootstrap` the NUC with `canary-fieldmouse` profile
2. Register as remote canary in `remote-canaries.toml`
3. Validate health sweep passes (13/13)
4. `gate.provision.destroy` the DO canary droplet
5. Savings: **$12/mo immediately**

### Phase 2: Compute Internalization (Move NUCLEUS off VPS)

**Prerequisite**: Reliable WAN relay that doesn't need to host primals locally.

The main golgiBody VPS currently runs the full NUCLEUS because primals need public-IP reachability for federation. With songBird mesh relay + WireGuard tunnel:
- Inner membrane nodes can handle all compute
- VPS becomes a thin relay: TLS termination + TCP proxy + depot file serving
- songBird on VPS relays federation traffic to inner membrane songBird

**Steps:**
1. Establish WireGuard tunnel: eastGate ↔ golgiBody VPS
2. Configure songBird VPS as relay-only (no local NUCLEUS)
3. Route depot requests through VPS Caddy → inner NestGate
4. Validate federation works through relay
5. Shrink VPS to `s-1vcpu-1gb` ($6/mo)

### Phase 3: Pixel 8 as Living Anchor (Cellular Tether)

**Hardware**: Pixel 8 (existing, available)  
**Network**: [ISP_CELLULAR] or similar MVNO ($15-25/mo for data)  
**Role**: Mobile/cellular WAN anchor providing:
- Secondary internet path (failover if home ISP drops)
- Remote mesh peer for ionic/weak bonding validation
- Real-world latency testing target for WAN tolerance scenarios

**Integration:**
1. Install Termux + membrane binary (aarch64-linux-android or via proot)
2. Run songBird in federation mode with peer = golgiBody VPS
3. Register as mesh peer for health.audit WAN metrics
4. Use as actual cellular tether for laptop when mobile

### Phase 4: Full Inner Membrane Sovereignty

**Endgame topology:**

```
[Internet]
    |
[golgiBody-slim VPS: $6/mo]  ← TLS + relay + CDN only
    | WireGuard
[eastGate: Pop!_OS dev primary]  ← Full NUCLEUS + dev
    | 10G backbone
[NUC-alpha: canary]  ← Previous-good fallback
[NUC-beta: staging]  ← Sandbox/validation
[Pixel 8: cellular anchor]  ← WAN diversity + ionic bond testing
    | 10G
[westGate: 76TB ZFS + Nest Atomic]  ← Cold storage + heavy compute
[biomeGate: HBM2 bench]  ← GPU compute
```

**Rental surface**: $6/mo (relay-only VPS)  
**Owned compute**: 10+ nodes, 76TB storage, multiple GPUs, cellular WAN diversity

---

## Hardware Available for Immediate Use

From HARDWARE.md inventory (consolidated):

| Node | CPU | RAM | GPU | Role in this plan |
|------|-----|-----|-----|-------------------|
| eastGate | Ryzen 5950X | 128GB DDR4 | RTX 4060+3090 | Primary dev + NUCLEUS |
| ironGate | i9-12900K | 64GB DDR5 | RTX 4070 | Secondary dev |
| southGate | i9-13900K | 128GB DDR5 | RTX 3090+5060 | Compute overflow |
| westGate | i7-4771 | 32GB DDR3 | RTX 2070S | ZFS cold storage + Nest |
| NUC (×2) | Intel N-series | 16GB | — | Canary + staging |
| Pixel 8 | Tensor G3 | 8GB | — | Cellular anchor |
| northGate | Ryzen 9950X3D | 96GB DDR5 | RTX 5090 | Family gate (spare compute, LAST) |

---

## Cost Trajectory

| Phase | Monthly Cost | Savings vs Current |
|-------|-------------|-------------------|
| Current | $24 | — |
| Phase 1 (NUC canary) | $12 | $12/mo |
| Phase 2 (slim VPS) | $6 | $18/mo |
| Phase 3 (Pixel tether) | $6 + ~$20 cellular | Net $-2/mo but gains WAN diversity |
| Phase 4 (full sovereign) | $6 | $18/mo permanent |

---

## Self-Provisioning Evolution

Eventually, a NUCLEUS could self-provision new nodes:
- Detect available hardware via mDNS/mesh
- Auto-run `gate.bootstrap` on discovered nodes
- `gate.provision` evolves from DO-only to multi-backend (DO, Hetzner, local-SSH)
- biomeOS orchestrates workload placement across the mesh

This is the path from "we provision via API" to "the membrane provisions itself."

---

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Home ISP outage → no WAN access | Pixel cellular tether as failover path |
| NUC hardware failure | Canary auto-failover to any other inner node |
| VPS still needed for public IP | $6/mo relay is acceptable long-term |
| WireGuard latency | Measured at <2ms over modern ISP; acceptable for relay |
| Dynamic home IP | Caddy + DNS auto-update (existing `cloudflare.rs` wiring) |

---

**This plan reduces rental surface from $24/mo to $6/mo while gaining WAN diversity, hardware redundancy, and self-provisioning capability. Execution starts with Phase 1 (NUC canary) which is immediately actionable using existing `gate.bootstrap` and `gate.provision.destroy`.**
