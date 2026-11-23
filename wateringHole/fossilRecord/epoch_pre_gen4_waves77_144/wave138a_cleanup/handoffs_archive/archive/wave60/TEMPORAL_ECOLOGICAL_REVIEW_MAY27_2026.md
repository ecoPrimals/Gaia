# Full Temporal / Glacial / Ecological Review — May 27, 2026

**Status**: Active review document
**Phase**: PostPrimordial → Glacial Shift (Wave 55b checkpoint)
**Author**: primalSpring / eastGate
**Scope**: All levels — primals, springs, gardens, infra, sovereignty

---

## I. Temporal Review: Where We Are in Time

### Wave Timeline

```
Wave 1–22   Primordial era → Stadial gate entry
Wave 22–39  Upstream absorption → Neural API → Observatory
Wave 40–47  Behavioral convergence → BTSP Phase 3 → 13/13 zero debt
Wave 48     Covalent spring mesh (8/8 springs confirmed)
Wave 49     Post-primordial enforcement (plasmidBin-only deployment)
Wave 50     Covalent HPC (7/7 delta springs, cross-subnet routing)
Wave 51     discovery.peers shipped, Songbird mesh+registry merge
Wave 52     plasmidBin pipeline elevation (Rust CLI, reproducible builds)
Wave 52b    Full NUCLEUS live on eastGate (13/13, 19/19 sockets)
Wave 53     Primal mountains (12/13 resolved, southGate ops pending)
Wave 54     Provenance-elevated checksums, gate redeploy, cellMembrane  ← NOW
Wave 55+    Springs cross-gate NUCLEUS, proto-nucleate deployment
```

### Velocity Assessment

| Metric | Count | Trend |
|--------|-------|-------|
| Waves shipped (May 2026) | 8 (W47–W54) | Sustained high throughput |
| Primal handoff acks (W53–54) | 14 per-primal responses | Full ecosystem participation |
| Spring handoffs (W50–54) | 8/8 springs engaged | All responsive |
| plasmidBin releases | v2026.05.25, v2026.05.26 | ~daily harvest cadence |
| New scenarios (W54-prep) | 3 (56 total) | Consistent validation growth |
| Provenance elevation (W54) | Layer 2 shipped | Major infra milestone |

### Debt Status (Ecosystem-Wide)

| Level | TODO/FIXME/HACK/XXX | Result |
|-------|---------------------|--------|
| primalSpring (Rust + shell) | **0** | Clean |
| plasmidBin (Rust + shell) | **0** | Clean |
| wateringHole (docs) | N/A | Living |
| All 13 NUCLEUS primals | Per PRIMAL_GAPS: **13/13 CLEAN** | Zero debt |
| All 8 springs | Zero code debt per W50 review | Clean |

**The ecosystem has achieved and is maintaining zero technical debt across all
levels.** This is a remarkable position to be in before the glacial shift.

---

## II. Glacial Review: Shift Readiness

### Exit Criteria Assessment (7 criteria)

| # | Criterion | Status | Progress | Blocker? |
|---|-----------|--------|----------|----------|
| 1 | S1–S4 sovereignty shadows cut over | **3/4** | S4 auth shadow code-built, not observed | No — S4 is last |
| 2 | Multi-gate LAN mesh operational | **Unblocked** | 4 gates up, discovery.peers shipped W51; `s_covalent_mesh` not yet run | **YES** — needs fresh deploy + live test |
| 3 | cellMembrane Nest expansion on VPS | **Not deployed** | NestGate v0.5.0 unified, provenance trio ready | **YES** — cellMembrane team |
| 4 | Remote covalent (flockGate WAN) | **Not deployed** | NAT traversal shipped, TURN live | No — soft criterion |
| 5 | Sovereign DNS | **Planned** | knot-dns documented, not deployed | **YES** — cellMembrane |
| 6 | Cloudflare removed from production path | **S1 not cut** | Caddy shadow live on VPS | Depends on #5 |
| 7 | CI on inner membrane | **1 runner (SPOF)** | ironGate runner live, 2nd planned | **YES** — GitHub Actions outage exposed this |

### Honest Assessment

**What's done**: Everything computational — 13/13 primals at zero debt, 460/460 methods
exercised, BTSP Phase 3 AEAD on all primals, provenance-elevated checksums shipped,
plasmidBin Rust CLI sovereign. The software is ready.

**What's not done**: Infrastructure sovereignty — DNS, VPS Nest expansion, CI runners,
TLS cutover. These are all cellMembrane-owned and don't depend on upstream primal
work. They are deployment tasks, not engineering tasks.

**Honest timeline**: Criteria 2 (live mesh test) can close in days. Criteria 3/5/7
require cellMembrane deployment sprints. Criteria 1/6 follow from 5. Criteria 4 is
soft. **A focused cellMembrane sprint could close 5 of 7 criteria within 2 weeks.**

### Glacial Checkpoint — What Would a Stadial Gate Look Like?

The stadial gate represents the ecosystem operating fully from sovereign infrastructure.
The interstadial was proving the software stack works. The glacial shift is proving the
infrastructure stack works. The stadial is running production workloads on both.

```
INTERSTADIAL (done)     → Prove all primals compose, communicate, and are secure
GLACIAL SHIFT (current) → Migrate infra from commercial to sovereign (DNS, CI, TLS, VPS)
STADIAL (goal)          → Operate sovereign infra as production baseline
POST-STADIAL            → Scale (more gates, more gardens, Forgejo-native CI, WASM)
```

---

## III. Ecological Review: Health Across All Levels

### Level 1: Primals (Foundation Layer)

| Primal | Version | Tests | ecoBin | BTSP P3 | JH-0 | Debt |
|--------|---------|------:|:------:|:-------:|:----:|:----:|
| bearDog | 0.9.0 | 14,784+ | A++ | FULL | Y | CLEAN |
| songbird | 0.2.1 | 7,178+ | A++ | FULL | Y | CLEAN |
| toadStool | 0.2.0 | 23,000+ | A++ | FULL | Y | CLEAN |
| biomeOS | 0.1.0 | 8,026+ | A++ | FULL | Y | CLEAN |
| nestGate | 0.5.0 | 12,393+ | A++ | FULL | Y | CLEAN |
| squirrel | 0.1.0 | 7,178 | A++ | FULL | Y | CLEAN |
| barraCuda | 0.4.0 | 4,422+ | A++ | FULL | Y | CLEAN |
| petalTongue | 1.6.6 | 6,297+ | A++ | FULL | Y | CLEAN |
| rhizoCrypt | 0.14.0 | 1,642+ | A+ | FULL | Y | CLEAN |
| loamSpine | 0.9.16 | 1,528+ | A+ | FULL | Y | CLEAN |
| sweetGrass | 0.7.37 | 1,553 | A+ | FULL | Y | CLEAN |
| coralReef | 0.2.0 | 4,506+ | A++ | FULL | Y | CLEAN |
| skunkBat | 0.2.0 | 389+ | A+ | FULL | Y | CLEAN |
| sourDough | 0.3.1 | 281 | A++ | — | — | Scaffolding |
| **Total** | | **93,237+** | | **13/13** | **13/13** | **13/13 CLEAN** |

**Aggregate primal test count: ~93,000+ across 14 repositories.** All Phase 1 and Phase 2
primals are at A+ or A++ ecoBin grade with full BTSP Phase 3 and MethodGate adoption.

### Level 2: Springs (Validation Layer)

| Spring | Version | Tests | Gate | Evolution | Key Focus |
|--------|---------|------:|------|-----------|-----------|
| primalSpring | 0.9.30 | 813 | eastGate | composing | Coordination, 56 scenarios, 460 methods |
| wetSpring | 0.3.0 | 1,962 | southGate | **composed** | Biology, ferment transcripts |
| neuralSpring | 0.1.0 | 1,453 | southGate | composing | ML inference, Squirrel provider |
| hotSpring | 0.6.32 | 1,042 | biomeGate | composing | Computational physics, QCD |
| airSpring | 0.10.0 | 1,435 | eastGate | **composed** | Agriculture, soil dynamics |
| groundSpring | 0.1.0 | 1,123 | eastGate | composing | Uncertainty, measurement |
| healthSpring | 0.1.0 | 1,018 | ironGate | composing | PK/PD, clinical |
| ludoSpring | 0.1.0 | 862 | ironGate | **composed** | Game science, esotericWebb |
| **Total** | | **9,694** | **4 gates** | | **3 composed, 5 composing** |

**Gate distribution**:
- **eastGate** (3 springs): primalSpring + airSpring + groundSpring — healthy
- **ironGate** (2 springs): ludoSpring + healthSpring — healthy
- **southGate** (2 springs): wetSpring + neuralSpring — **unstable (7–12/13 primals)**
- **biomeGate** (1 spring): hotSpring — operational but federation fix pending

### Level 3: Gardens (Product Layer)

| Garden | Purpose | Status | Tests | Maturity |
|--------|---------|--------|------:|----------|
| cellMembrane | Inner membrane VPS + typed spec | LIVE Tower | 80 | Active (sovereignty blocker) |
| projectNUCLEUS | Gate orchestration + deploy scripts | Active | — | Coordination hub |
| projectFOUNDATION | Validation lineage, benchmarks | Background | — | Thread registry |
| lithoSpore | Field deployment (USB spores) | v1.0.0 | 7/7 | Stable |
| esotericWebb | gen4 CRPG product | V10 | 357 | 12 open gaps |

### Level 4: Infrastructure

| Component | Status | Health |
|-----------|--------|--------|
| plasmidBin | Rust CLI, Tier 1 cross-arch, provenance-elevated | **Excellent** |
| wateringHole | 310+ handoffs, living standards, glacial tracking | **Excellent** |
| whitePaper | gen3/gen4/neuralAPI/sovereignty docs | **Healthy** |
| benchScale | Isolated test environments, K-Derm topology | **Healthy** |
| agentReagents | VM image building, cloud-init | **Healthy** |
| fossilRecord | ~9,920 files, structured archive | **Comprehensive** |

### Level 5: Deployment Infrastructure

| Component | Status | Sovereign? |
|-----------|--------|:----------:|
| Hardware (11 towers) | 4 active, 6 ready, 1 WAN | **YES** |
| LAN backbone | Cat6 1G, 4 gates connected | **YES** |
| VPS (cellMembrane) | OPERATIONAL (DO nyc1) | Partial |
| TLS termination | Caddy shadow live, Cloudflare active | **Shadow** |
| DNS | Commercial registrar | **NO** |
| CI/CD | GitHub Actions + 1 self-hosted runner | **Partial** |
| Source hosting | Forgejo primary + GitHub mirror | **YES** |
| Binary distribution | plasmidBin (GitHub Releases) | Partial |
| Remote access | RustDesk + Songbird TURN | **YES** |

### Cross-Level Dependency Flow

```
                    ┌─────────────────────────────────────┐
                    │         fossilRecord (archive)       │
                    └──────────────────┬──────────────────┘
                                       │ fossils flow down
┌──────────┐   standards   ┌───────────┴──────────────────┐
│ whitePaper├──────────────►│       wateringHole            │
└──────────┘               │  (standards + handoffs)       │
                           └──┬────┬────┬────┬────────────┘
                              │    │    │    │
              ┌───────────────┘    │    │    └──────────────────┐
              ▼                    ▼    ▼                       ▼
    ┌─────────────┐     ┌──────────┐  ┌──────────┐    ┌──────────────┐
    │  plasmidBin  │     │ 14 primals│  │ 8 springs │    │  5 gardens   │
    │ (binary depot│     │ (Rust src)│  │(validation)│    │  (products)  │
    │  + harvest)  │     └────┬─────┘  └────┬──────┘    └──────┬───────┘
    └──────┬───────┘          │             │                   │
           │ binaries         │ compose     │ validate          │ consume
           ▼                  ▼             ▼                   ▼
    ┌──────────────────────────────────────────────────────────────┐
    │                4-gate LAN NUCLEUS deployment                 │
    │     eastGate ─── ironGate ─── southGate ─── biomeGate       │
    │           Songbird TCP :7700 covalent mesh                   │
    └──────────────────────────┬───────────────────────────────────┘
                               │
                               ▼
    ┌──────────────────────────────────────────────────────────────┐
    │                cellMembrane VPS (inner membrane)              │
    │     TURN :3478 ─── RustDesk ─── Caddy TLS ─── (knot-dns)   │
    └──────────────────────────────────────────────────────────────┘
```

### Active Ecosystem Issues

| Issue | Level | Severity | Owner | Status |
|-------|-------|----------|-------|--------|
| southGate primal instability | Deployment | MEDIUM | southGate ops | 7–12/13 health; fresh redeploy handoff issued |
| GitHub Actions as CI SPOF | Infra | HIGH | cellMembrane | May 26 outage exposed this; 2nd runner planned |
| Cloudflare on production TLS | Infra | MEDIUM | cellMembrane | Shadow live, not cut over |
| No sovereign DNS | Infra | MEDIUM | cellMembrane | knot-dns planned, not deployed |
| VPS Nest expansion | Infra | MEDIUM | cellMembrane | NestGate v0.5.0 ready, not deployed |
| manifest.toml version drift | Hygiene | LOW | plasmidBin | Some header versions lag reality |
| Songbird coverage 73% | Quality | LOW | Songbird team | I/O-heavy paths; not blocking |
| biomeOS LiveSpore uses ~/.local/bin | Hygiene | LOW | biomeOS team | Conflicts with plasmidBin-only |

---

## IV. Sovereignty Goals: Long-Term Vision

### The Chrysalis Thesis (from `THE_GOLDEN_CAGE.md`)

The ecosystem currently bootstraps from commercial infrastructure (GitHub, Cloudflare,
DigitalOcean) and progressively replaces each dependency with sovereign alternatives.
This is the **chrysalis** — the commercial cage provides the scaffolding while the
sovereign organism grows inside it. Once sovereign capabilities match or exceed commercial
ones, the cage opens.

### Sovereignty Layer Completion

```
S0 ████████████████████████ COMPLETE    Hardware + LAN
S1 ████████████████████████ COMPLETE    BearDog ACME live (Wave 112)
S2 ████░░░░░░░░░░░░░░░░░░░ 15%         knot-dns planned
S3 ████████████████████████ COMPLETE    RustDesk + Songbird TURN
S4 ████████████████████████ COMPLETE    Forgejo primary
S5 ████████████████████░░░░ 85%         Forgejo Releases pending
S6 ████████████░░░░░░░░░░░░ 50%         Static Zola; living content pending
S7 ████████████████████████ COMPLETE    Neural API + graphs
S8 ████████████████████████ COMPLETE    12/12 primal.announce
                                        ─────────────────────
                                        Overall: ~76% sovereign
```

### Long-Term Sovereignty Roadmap

#### Horizon 1: Inner Membrane Maturity (Waves 54–57)

Target: cellMembrane VPS becomes a fully functional inner membrane node.

| Goal | Owner | Priority | Depends On |
|------|-------|----------|------------|
| **knot-dns on VPS** (sovereign DNS) | cellMembrane | **CRITICAL** | VPS access |
| **VPS Nest expansion** (rhizoCrypt + loamSpine + sweetGrass + NestGate) | cellMembrane | **CRITICAL** | NestGate v0.5.0 (done) |
| **2nd CI runner** (eliminate SPOF) | cellMembrane | HIGH | eastGate hardware (ready) |
| **Forgejo Releases** as sovereign binary channel | projectNUCLEUS | HIGH | Forgejo (operational) |
| **S1 TLS cutover** (Cloudflare → Caddy/BearDog) | cellMembrane | HIGH | S2 DNS done first |
| **provenance.toml → Forgejo** identity | plasmidBin | MEDIUM | Forgejo Releases |

#### Horizon 2: Multi-Gate Sovereignty (Waves 57–62)

Target: LAN mesh operates as a sovereign compute fabric.

| Goal | Owner | Priority |
|------|-------|----------|
| **Plasmodium collective** (3+ gates meshed, `capability.call` validated) | primalSpring | HIGH |
| **northGate deployment** (Node Atomic — heavy compute) | Gate ops | MEDIUM |
| **westGate deployment** (Nest Atomic — 76TB cold storage) | Gate ops | MEDIUM |
| **strandGate deployment** (Full NUCLEUS — bioinformatics, 64-core) | Gate ops | MEDIUM |
| **Forgejo Actions** on ironGate (shadow GitHub Actions) | cellMembrane | HIGH |
| **Cross-gate DNS replication** (knot-dns zone sync) | cellMembrane | MEDIUM |
| **10G LAN elevation** (switch + Cat6a) | Hardware | LOW |

#### Horizon 3: External Sovereignty (Waves 62–70+)

Target: Operate independently of commercial cloud services.

| Goal | Owner | Priority |
|------|-------|----------|
| **flockGate WAN validation** (remote covalent over residential NAT) | primalSpring + cellMembrane | HIGH |
| **GitHub Actions removed** from critical path | cellMembrane | HIGH |
| **Cloudflare removed** from DNS and TLS | cellMembrane | MEDIUM |
| **DigitalOcean VPS → self-hosted** (co-lo or home DMZ) | cellMembrane | LOW (future) |
| **Living content** (primal-served dynamic pages via NestGate) | cellMembrane | MEDIUM |
| **sporePrint on sovereign stack** (NestGate + petalTongue, not GitHub Pages) | cellMembrane | MEDIUM |

#### Horizon 4: Post-Stadial Evolution (Waves 70+)

Target: The sovereign ecosystem generates value and scales.

| Goal | Owner | Priority |
|------|-------|----------|
| **barraCuda WGSL → sovereign HPC** | hotSpring + barraCuda | Science-dependent |
| **Adaptive Neural API routing** (learned weights) | biomeOS | Research |
| **NUCLEUS absorbs forge** (Forgejo becomes a composition) | cellMembrane + biomeOS | Architecture |
| **Cross-household covalent** (friend/family gates join mesh) | primalSpring | Social |
| **WASM primals** (browser-native composition) | Long-term | Research |
| **esotericWebb as product** (first gen4 shipping game) | esotericWebb | Product |

### The Sovereignty Invariants

These are the non-negotiable principles that guide all sovereignty decisions:

1. **No vendor lock-in**: Every commercial dependency has a documented sovereign
   alternative with Calibrate → Shadow → Cutover path.
2. **Pure Rust, zero C deps**: ecoBin compliance ensures the entire stack compiles
   from source without external binary dependencies.
3. **Hardware ownership**: Physical control of compute is the foundation.
   Cloud VPS is a bridge, not a destination.
4. **Primal autonomy**: Each primal is a standalone Rust binary with its own repo,
   tests, and release cycle. No monorepo coupling.
5. **Fossil record**: Nothing is deleted — docs, standards, and decisions are
   fossilized for institutional memory. The ecosystem learns.
6. **Graph-driven composition**: Products are compositions of primals, not
   monolithic applications. biomeOS is the orchestrator, not a platform.
7. **Provenance by default**: Every binary carries its provenance chain
   (content hash + build context + braid attribution). Trust is verifiable.

---

## V. Ecological Health Summary

### What's Working

- **Zero debt at every level** — unprecedented across 14 primals, 8 springs, 5 gardens
- **93,000+ tests** across the primal layer alone; ~103,000+ including springs
- **Provenance chain complete** — Layer 1 (bytes) + Layer 2 (composite) + Layer 3 (braids)
- **4-gate NUCLEUS operational** with Songbird covalent mesh seeded
- **460/460 method coverage** (100% of capability registry exercised)
- **Wave cadence sustained** at ~2 waves/day during active development
- **fossilRecord comprehensive** (~9,920 files, structured archive)
- **plasmidBin Rust CLI fully sovereign** — no bash script dependencies remain

### What Needs Attention

- **cellMembrane deployment sprint** — 3 glacial criteria blocked on VPS deployments
- **southGate stability** — weakest gate, fresh redeploy needed
- **CI resilience** — GitHub Actions as SPOF was exposed during May 26 outage
- **Sovereignty S2 (DNS)** — the last truly critical missing piece
- **Spring cross-gate validation** — `s_covalent_mesh` never run with live mesh

### The Big Picture

The ecoPrimals ecosystem has completed its software evolution and is now transitioning
to infrastructure sovereignty. The primals are healthy, the springs are validating,
the gardens are growing. The remaining work is about **where things run**, not
**what things do**. This is exactly where you want to be before a glacial shift —
the organism is complete, and it's outgrowing the cage.

---

## Appendix: Gate Hardware Inventory

| Gate | CPU | GPU | RAM | Storage | Status |
|------|-----|-----|-----|---------|--------|
| eastGate | i9-12900 | RTX 4070 + Akida NPU | 32 GB | SSD | **OPERATIONAL** (13/13) |
| ironGate | i9-14900K | RTX 5070 | 96 GB | SSD | **OPERATIONAL** (12/12) |
| southGate | 5800X3D | RTX 4060 + 3090×2 | 128 GB | NVMe | **OPERATIONAL** (unstable) |
| biomeGate | TR 3970X | (HBM2 test bench) | 256 GB | NVMe | **OPERATIONAL** (62/62) |
| strandGate | Dual EPYC 7452 (64c) | — | 256 GB ECC | — | Hardware ready |
| northGate | Ryzen 9950X3D | RTX 5090 | 96 GB | — | Hardware ready |
| westGate | i7-4771 | RTX 2070S | 32 GB | 76TB ZFS | Hardware ready |
| swiftGate | Ryzen 5800X | RTX 3070 | 64 GB | — | Hardware ready |
| flockGate | i9-13900K | RTX 3070 Ti | 64 GB | — | Config ready (WAN) |
| kinGate | i7-6700K | RTX 3070 | 32 GB | — | Hardware ready |

**Aggregate**: 11 towers, 4 operational gates, 6 ready, 1 WAN. ~1 TB aggregate RAM,
4+ HBM2 cards, 3+ NPUs.

---

*This review is a living document. Next review checkpoint: post-cellMembrane deployment sprint (target: Wave 57).*
