# Gate-Team Coordination Matrix

**Purpose**: Single-page view of which team operates which gate, what hardware
it has, what projects it owns, and where it sits in the evolution/validation
hierarchy. Consolidates data from `GATE_SPRING_OWNERSHIP.md` (canonical
spring routing), `GLACIAL_SHIFT_READINESS.md` (operational status), and
`ecosystem_manifest.toml` (sync profiles).

**Last updated**: 2026-06-03 (Wave 75 — covalent mesh FORMING, every primal evolved, cross-gate trust validation NEXT)

**Authority**: wateringHole consensus

---

## Gate Inventory

| Gate | Team | Hardware | Role | NUCLEUS | Network | Status |
|------|------|----------|------|---------|---------|--------|
| **eastGate** | eastGate (overwatch) | i9-12900, RTX 4070 + Akida, 32GB | Orchestrator, coordination hub | 13/13 | LAN 1G | OPERATIONAL |
| **ironGate** | ironGate (cellMembrane, projectNUCLEUS, NestGate, petalTongue) | i9-14900K, RTX 5070, 96GB | Deployment infra, agentic dev | 13/13 (23 UDS) | LAN 1G | OPERATIONAL |
| **southGate** | southGate (Songbird, biomeOS, bearDog) | 5800X3D, RTX 4060 + 3090s, 128GB | Mesh + orchestration + security primals | 9/9 | LAN 1G | OPERATIONAL |
| **biomeGate** | biomeGate (hotSpring, toadStool, barraCuda, coralReef) | Threadripper 3970X, Titan V + K80, 256GB | HPC physics, compute trio, air-gap tester | 62/62 | LAN 1G | **OFFLINE** (kernel recovery) |
| **flockGate** | flockGate (sporePrint) | i9-13900K, RTX 3070 Ti, 64GB | WAN covalent, sporePrint hosting | OPERATIONAL | WAN via cellMembrane | OPERATIONAL |
| **strandGate** | strandGate (provenance trio + compute trio pickup) | Dual EPYC 7452 (64c), 256GB ECC | Bioinformatics, ABG science, barraCuda + coralReef SPIR-V | — | LAN 1G | **ACTIVE** (Wave 72) |
| **northGate** | — (undeployed) | Ryzen 9950X3D, RTX 5090, 96GB | Heavy compute, AI/LLM | — | LAN 1G (10G ready) | HARDWARE READY |
| **westGate** | — (incoming this week) | i7-4771, RTX 2070 Super, 32GB | 76TB ZFS cold storage (Nest Atomic) | — | LAN 1G (10G ready) | **INCOMING** (ETA this week) |
| **swiftGate** | — (undeployed) | Ryzen 5800X, RTX 3070, 64GB | Mobile/compact | — | LAN 1G | HARDWARE READY |
| **kinGate** | — (undeployed) | i7-6700K, RTX 3070, 32GB | Staging | — | LAN 1G | HARDWARE READY |
| **grapheneGate** | eastGate (portable) | Pixel 8a, Tensor G3, 8GB | Portable trust anchor, Dark Forest beacon | Tower Atomic (BearDog + Songbird + SkunkBat) | Cellular / WiFi | HARDWARE READY |

### VPS Nodes (cellMembrane — Inner Membrane)

| Node | K-Derm Layer | IP | Specs | Role | Status |
|------|-------------|-----|-------|------|--------|
| **golgiBody** | Inner (cis face) | [RELAY_PUBLIC] | 1 vCPU, 2GB, 50GB | Forgejo, NUCLEUS relay, sovereign DNS (ns1) | OPERATIONAL |
| **peptidoglycan** | Structural | [RELAY_PUBLIC] | 2 vCPU, 4GB, 80GB | Temporal sync hub, relay mediator | OPERATIONAL |
| **golgiBody-ext** | Outer (trans face) | 137.184.197.151 | — | Caddy TLS, sporePrint serving, DNS (ns2), GitHub push | OPERATIONAL |

---

## Project Ownership

### Springs

| Spring | Owner Gate | Science Domain |
|--------|-----------|----------------|
| **primalSpring** | eastGate | Ecosystem coordination, composition validation |
| **airSpring** | eastGate | Ecology science |
| **groundSpring** | eastGate | Geoscience |
| **healthSpring** | ironGate | Clinical/compliance |
| **ludoSpring** | ironGate | Game science |
| **wetSpring** | southGate | Biology, analytical chemistry |
| **neuralSpring** | southGate | ML inference patterns |
| **hotSpring** | biomeGate + strandGate | GPU physics (biomeGate compute), ABG science (strandGate) |
| **sporePrint** | flockGate | Ecosystem website, content pipeline |

### Primals (Mountains)

| Primal | Owner Gate | Capability Domain |
|--------|-----------|-------------------|
| **skunkBat** | eastGate | Session management, family identity |
| **squirrel** | eastGate | AI assistant, composition planning |
| **NestGate** | ironGate | Storage, content-addressed persistence |
| **petalTongue** | ironGate | Universal User Interface, rendering |
| **Songbird** | southGate | Mesh discovery, federation, TURN relay |
| **biomeOS** | southGate | Adaptive orchestration, Neural API |
| **bearDog** | southGate | Security, TLS, BTSP authentication |
| **toadStool** | biomeGate | Compute dispatch, GPU diesel engine (compute trio) — BLOCKED (hardware) |
| **barraCuda** | strandGate (pickup from biomeGate) | Pure Rust math + compute engine — ml.mlp_train (pure software) |
| **coralReef** | strandGate (SPIR-V) / biomeGate (Blackwell) | Shader compiler — SPIR-V portable, SM120 hardware-dependent |
| **rhizoCrypt** | strandGate | Content-addressed DAG (provenance trio) |
| **loamSpine** | strandGate | Immutable linear ledger (provenance trio) |
| **sweetGrass** | strandGate | Attribution, W3C PROV-O braids (provenance trio) |

### Infrastructure Projects

| Project | Owner Gate | Description |
|---------|-----------|-------------|
| **cellMembrane** | ironGate | VPS provisioning, relay infrastructure, deployment tooling |
| **projectNUCLEUS** | ironGate | Deploy graphs, dark forest, genomeBin, Forgejo CI |
| **esotericWebb** | ironGate | Interactive product garden |

---

## Gate → Responsibility Summary

| Gate | Springs | Primals | Infra Projects | Gardens | Sync Profile |
|------|---------|---------|----------------|---------|--------------|
| **eastGate** | primalSpring, airSpring, groundSpring | skunkBat, squirrel | — | — | Full superset (39 repos) |
| **ironGate** | healthSpring, ludoSpring | NestGate, petalTongue | cellMembrane, projectNUCLEUS | esotericWebb | Core + health/ludo + infra |
| **southGate** | wetSpring, neuralSpring | Songbird, biomeOS, bearDog | — | — | Core + wet/neural + mesh primals |
| **biomeGate** | hotSpring | toadStool, barraCuda, coralReef | — | — | Core + hotSpring + compute trio |
| **flockGate** | sporePrint | — | — | — | Core + sporePrint/petalTongue |
| **strandGate** | hotSpring (science) | rhizoCrypt, loamSpine, sweetGrass, **barraCuda** (pickup), **coralReef** (SPIR-V pickup) | — | helixVision, initioChem, blueFish, lithoSpore | Core + provenance + ABG + compute trio (software) |

---

## Evolution Hierarchy

### Validation Tiers

```
Tier 1 — Coordination (eastGate)
  primalSpring validates all compositions work together.
  835 tests, 57 scenarios, 33 compositions, 490+ methods.
  Owns the bonding mechanics, not the atoms.

Tier 2 — Deployment (ironGate)
  projectNUCLEUS validates deploy graphs, genomeBin, CI.
  cellMembrane validates VPS infrastructure, relay chain.

Tier 3 — Domain Science (per-gate)
  Each gate validates its own springs independently.
  primalSpring's scenarios verify cross-gate composition parity.
```

### Current Wave Assignments (Wave 77)

| Gate | Active Work | Priority | Status |
|------|-------------|----------|--------|
| **eastGate** | Live cross-gate capability.call validation. DNS NS cutover. primalSpring security scenarios. skunkBat westGate-ready. | P0 glacial | **AT PARITY — VALIDATION NEXT** |
| **ironGate** | S4 gate (ends ~Jun 9). NestGate s92 ZERO test failures. cellMembrane westGate onboarding prep. ludoSpring V82 parity. | P0 glacial | S4 **ACTIVE**, NestGate **ZERO FAILURES** |
| **southGate** | bearDog w137 (DID↔key, typed errors). Songbird w76 Phase 3.5 scaffold. biomeOS v4.05 (perceptron infer wired). Springs V195/V179 at parity. | P0 | **AT PARITY — PHASE 3.5 NEXT** |
| **biomeGate** | toadStool S288 (deep debt VIII, panic elimination). Hardware still OFFLINE. | P1 HPC | **OFFLINE** (S288 delivered remotely) |
| **flockGate** | sporePrint S3 content cutover (post-DNS). WAN relay maintenance. | P2 cutover | Ready, waiting on NS cutover |
| **strandGate** | coralReef w77 SPIR-V output + mesh capability. Provenance trio cross-gate schemas delivered. barraCuda modularized. | P1 compute | **AT PARITY — ALL TEAMS DELIVERED** |
| **westGate** | 76TB ZFS cold storage. Nest Atomic. Gate setup + NUCLEUS deploy. | P3 expansion | **INCOMING** (ETA this week) |
| **golgiBody** | Disk at 60%. S4 monitoring active. Relay chain Rust-native. | Maintenance | **HEALTHY** |

---

## Sovereignty Shadow Status

| Track | Commercial | Sovereign | Gate | Status |
|-------|-----------|-----------|------|--------|
| S1 TLS | Cloudflare (INACTIVE) | Caddy + LE on golgiBody-ext | cellMembrane | **VERIFIED** — 198 probes, 0 failures. Awaiting NS cutover to remove Cloudflare |
| S2 NAT | cloudflared (INACTIVE) | Songbird TURN :3478 | cellMembrane | **GRADUATED** |
| S3 Content | GitHub Pages | NestGate + Caddy (67ms TTFB) | cellMembrane + sporePrint | **READY** — sporePrint 101 tests, zero-C. Cutover after DNS NS switch |
| S4 Auth | OAuth2/PAM (DISABLED) | BearDog BTSP enforced | southGate (bearDog) + ironGate | **7-DAY GATE ACTIVE** — started Jun 2, ends ~Jun 9 |
| S5 DNS | Cloudflare NS | knot-dns ns1+ns2 (DNSSEC) | cellMembrane | **Infra LIVE** — registrar NS cutover pending (operator) |

---

## Cross-References

- `GLACIAL_CUTOVER_PLAN.md` — phased cutover plan (inner→outer→external)
- `GATE_SPRING_OWNERSHIP.md` — canonical spring routing, evolution biology
- `GLACIAL_SHIFT_READINESS.md` — operational status, glacial criteria
- `GLACIAL_SHIFT_WAVE_PLAN.md` — phased wave assignments
- `EVOLUTION_STATUS_WAVE66.md` — Wave 66 checkpoint + context braids
- `ecosystem_manifest.toml` — machine-readable gate sync profiles

---

*Wave 75. Covalent mesh FORMING. Every primal evolved. Virtual relay Phase 2 default. Cross-gate trust validation and gen5 paper NEXT. Evolution never stops.*
