# Gate-Spring Ownership — Canonical Routing SSOT

**Purpose**: Definitive assignment of which gate owns which springs, gardens,
and science domains. This is the missing doc that `STANDARDS_AND_EXPECTATIONS.md`
referenced as `GATE_DEPLOYMENT_STANDARD.md`.

**Last updated**: 2026-05-28 (Wave 60 — postPrimordial, golgiBody Phase A live)

**Authority**: wateringHole consensus. Changes require coordination across
affected gate teams.

---

## Gate-Spring Ownership Table

| Gate | Springs | Gardens / Products | Science Domain | NUCLEUS Status |
|------|---------|-------------------|----------------|----------------|
| **eastGate** | primalSpring, airSpring, groundSpring | — | Ecosystem coordination, ecology, geoscience | Full 13/13 |
| **ironGate** | healthSpring, ludoSpring | esotericWebb | Clinical/compliance, game science | Full 13/13 |
| **southGate** | wetSpring, neuralSpring | — | Biology/analytical chemistry, ML inference | Node Atomic (P1 pattern node) |
| **biomeGate** | hotSpring | — | GPU-accelerated physics, compute trio (toadStool + barraCuda + coralReef) | Node Atomic 9/13 |
| **strandGate** | hotSpring | helixVision, initioChem, blueFish, lithoSpore | ABG science, provenance trio, genomics, analytical ETL | Full NUCLEUS planned |
| **golgiBody** (VPS) | — | — | Periplasmic sync, Forgejo, NUCLEUS relay | Infra NUCLEUS 13/13 |

**Cross-gate springs**: hotSpring operates on both strandGate (ABG science,
lithoSpore, compChem validation) and biomeGate (GPU solving, HBM2 compute,
toadStool diesel engine). The science evolves on strandGate; heavy compute
dispatches to biomeGate via Songbird mesh.

---

## primalSpring — Coordination Spring (Not Science)

primalSpring is the ecosystem's coordination and composition validation spring.
Its scope is exclusively:

- **NUCLEUS evolution** — composition tiers, deployment patterns, dark forest validation
- **Primal bonding** — capability contracts, IPC wire standards, cross-gate mesh
- **Ecosystem validation** — 57 scenarios, freshness checks, WaterFall integrity

primalSpring does NOT own domain science. Each science spring evolves
independently on its home gate. primalSpring validates that their compositions
work together — it is the bonding mechanics, not the atoms.

---

## Gate Hardware Profiles

| Gate | Hardware | CPU | RAM | GPU | Storage | Role |
|------|----------|-----|-----|-----|---------|------|
| **eastGate** | Utility + neuromorphic | Ryzen | 64GB | Akida BrainChip | NVMe | Orchestration hub, coordination |
| **ironGate** | Agentic dev workstation | — | 96GB | — | Large | ABG JupyterHub, cellMembrane team home |
| **southGate** | Gaming + heavy compute | — | 128GB | Multi-GPU | NVMe | Biology + inference pattern node |
| **biomeGate** | HBM2 test bench | Threadripper | — | Titan V + K80 | NVMe | HPC physics, GPU shader validation |
| **strandGate** | Bioinformatics | 64-core | — | — | Large | ABG science, genomics pipelines |
| **northGate** | Flagship AI/LLM (future) | — | — | — | — | Node Atomic planned |
| **westGate** | Cold storage (future) | — | — | — | 76TB | Nest Atomic planned |
| **grapheneGate** | Pixel 8a (GrapheneOS) | Tensor G3 | 8GB | — | 128GB | Portable trust anchor, Dark Forest beacon |
| **golgiBody** | DigitalOcean VPS | 1 vCPU | 2GB | — | 50GB | Periplasmic sync, NUCLEUS relay |

---

## Domain Routing

### Current: Ad-Hoc (Documented)

Gates currently route work via handoff blurbs in wateringHole. Each gate team
pulls repos relevant to their springs via `membrane temporal.cascade`.
Cross-gate compute is coordinated manually through blurbs.

### Target: Covalent (Songbird Mesh)

Evolution path from ad-hoc to fully covalent routing:

```
Phase 1: Documented ownership (this file)              ← YOU ARE HERE
Phase 2: Gate profiles in manifest drive WaterFall sync ← DONE (membrane temporal.cascade --gate)
Phase 3: Songbird mesh discovers cross-gate capabilities
Phase 4: toadStool dispatches compute to best-fit gate
Phase 5: biomeOS graph.execute routes across Plasmodium
```

### Cross-Gate Patterns

| Pattern | Mechanism | Example |
|---------|-----------|---------|
| **Science on one gate, compute on another** | Songbird mesh + toadStool dispatch | hotSpring science on strandGate, GPU dispatch to biomeGate |
| **Coordination validates all gates** | primalSpring `s_covalent_mesh` | eastGate probes ironGate + southGate mesh health |
| **Repo sync through periplasm** | WaterFall temporal cascade via Forgejo | All gates pull from golgiBody VPS |
| **Product composition across springs** | Garden composes primals via IPC | helixVision on strandGate consumes wetSpring + hotSpring science |

---

## WaterFall Sync Profiles

Each gate's `[gates.*]` manifest profile determines which repos it pulls
via `membrane temporal.cascade`. The profile reflects ownership:

- **eastGate**: Full superset (38 repos) — coordination hub sees everything
- **ironGate**: Core primals + healthSpring + infra
- **southGate**: Core primals + wetSpring + neuralSpring
- **biomeGate**: Core primals + hotSpring
- **strandGate**: Core primals + hotSpring + wetSpring + ABG gardens + lithoSpore
- **golgiBody**: NUCLEUS primals + deployment infra (no springs)

Gates can override with `--gate` flag or pull everything without `--gate`.

---

## Evolution Timeline

| Wave | Milestone | Status |
|------|-----------|--------|
| 55 | Gate-spring assignments in handoff blurbs | DONE |
| 59 | southGate designated pattern node (wet/neural first) | DONE |
| 60 | golgiBody Phase A — VPS Forgejo, WaterFall 38/38 validated | DONE |
| 60 | This SSOT created — documented ownership | DONE |
| 60 | strandGate enters ecosystem (helixVision, initioChem, blueFish) | DONE |
| 60 | Eukaryotic gate onboarding — one spring per gate blurbs shipped | DONE |
| 60 | VPS federation hub — Songbird :7700 + MitoBeacon seed + Dark Forest | DONE |
| 61+ | southGate 13/13 + membrane patterns proven | P1 critical path |
| 61+ | biomeGate 13/13 + GPU dispatch | P2 |
| 61+ | Gates mesh with VPS hub — colonial phase begins | P2 |
| 62+ | Songbird covalent mesh across 4+ gates | P3 |
| 63+ | biomeOS graph.execute over mesh | P5 |

---

## Biological State: Eukaryotic Unicellular → Multicellular

The ecosystem evolves through distinct organizational states:

```
Prokaryotic (Wave 1-48)
    Primals exist but gates are unstructured. No NUCLEUS.
    ↓
Eukaryotic unicellular (Wave 49-62) ← CURRENT
    Each gate has internal organization (NUCLEUS, springs, primals).
    Gates share the VPS periplasm (Forgejo) but operate independently.
    Like yeast: organized, capable, but each cell is autonomous.
    ↓
Colonial (Wave 62-63)
    Songbird mesh discovers cross-gate capabilities.
    Gates share advertisements but don't yet dispatch work.
    Like Volvox: cells in proximity, beginning to specialize.
    ↓
Multicellular (Wave 63+)
    Covalent bonds between gates via Songbird mesh.
    toadStool dispatches compute to best-fit hardware.
    Gates specialize as tissues: compute, science, coordination.
    ↓
Organism (Wave 65+)
    biomeOS graph.execute routes across the full Plasmodium.
    The ecosystem operates as one distributed sovereign system.
```

**Current wave objective**: Get every gate eukaryotic (NUCLEUS running,
primary spring validating, syncing through periplasm). See
`handoffs/EUKARYOTIC_GATE_ONBOARDING_MAY28_2026.md` for per-gate blurbs.

---

---

## Peptidoglycan Relay Layer

The VPS operates as the ecosystem's peptidoglycan — a structural relay substrate
between the outer membrane (internet) and the plasma membrane (gate firewalls).
It provides sovereign replacements for commercial services, running as persistent
infrastructure that gates connect to for federation, NAT traversal, and remote access.

### Shadow Pattern Map

| Commercial Service | Sovereign Shadow | VPS Port | Shadow Track | Status |
|----|----|----|----|----|
| Cloudflare Tunnel | Songbird TURN relay | :3478 + 49152:65535/udp | S2 | Parity met |
| Cloudflare TLS | BearDog ACME shadow | :8443 | S1 | Shadow live |
| GitHub Pages | NestGate + Caddy | :443 | S3 | Live, 68ms |
| Cloudflare DNS | knot-dns DNSSEC | :53 | S5 | Live, NS pending |
| Cloud IDE relay | RustDesk hbbs/hbbr | :21115-21117 | — | Live |
| GitHub Repos | Forgejo (golgiBody) | :2222 (SSH) + :3000 (HTTP) | — | Live, 38 repos |

### Gate Onboarding to Relay Layer

Gates onboard to the peptidoglycan via `onboard-gate-relay.sh`:

```bash
# From VPS depot (onboard a remote gate):
onboard-gate-relay.sh eastGate --vps-host [RELAY_PUBLIC] --gate-host 10.10.0.3

# From a gate (onboard self):
onboard-gate-relay.sh eastGate --vps-host [RELAY_PUBLIC] --local
```

This pulls TURN credentials, RustDesk key, MitoBeacon family/lineage seeds
from the VPS and writes `relay.env` to the gate. The gate's `tower.env` sources
this file for Songbird federation, TURN traversal, and family identity.

### Transport Paths by Gate Class

| Gate Class | Network | Federation Path | TURN Required |
|------------|---------|-----------------|---------------|
| LAN cluster | Basement 10G backbone | Direct TCP :7700 to VPS | No |
| WAN household | Remote ISP | TURN :3478 → federation | Yes |
| Roaming mobile | LAN ↔ cellular | Direct when LAN, TURN fallback | Conditional |
| Friend tower | External household | TURN :3478 → federation | Yes |
| NAS/depot | LAN backbone | Direct TCP :7700 to VPS | No |
| Portable anchor | WiFi / cellular | TURN :3478 → federation or BLE beacon | Conditional |

---

*Wave 68. Colonial phase. Portable trust anchors extend the mesh.*
