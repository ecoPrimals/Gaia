# Team Work Vectors — Wave 157k

**Purpose**: Mesh-available reference so every gate knows what every other gate and team is working on. Solo work that enables full enmeshment of atomics and gates is called out explicitly.

**Updated**: Aug 12, 2026 | **Wave**: 157k

---

## GATE FLEET — STATUS

| Gate | Platform | Mesh IP | Composition | Status | Hardware |
|------|----------|---------|-------------|--------|----------|
| **golgiBody** | Linux (VPS) | 10.13.37.1 | thin-relay | ONLINE | DO NYC, Forgejo + depot + relay |
| **sporeGate** | Linux | 10.13.37.2 | full | ONLINE | Ryzen 5 6600H NUC, 27 GB, 2.5G |
| **eastGate** | Linux | 10.13.37.5 | full | ONLINE | Ryzen 9 7950X, 128 GB DDR5, 10G SFP+ |
| **ironGate** | Linux | 10.13.37.7 | full | NUCLEUS (13) | i9-14900K, RTX 5070 Ti, 94 GB, 14 TB HDD + NVMe |
| **southGate** | Linux | NO WG | full | NUCLEUS (13) | Pop!_OS, RTX 4060 |
| **strandGate** | Linux | 10.13.37.10 | compute | NUCLEUS | Dual EPYC 7452, RTX 3090 + RX 6950 XT + AKD1000, 256 GB |
| **westGate** | Linux | 10.13.37.11 | nest | NUCLEUS (14) | Ryzen 7 5700X, 64 GB, ZFS 50.7 TB |
| **blueGate** | Windows | 10.13.37.12 | tower | ONLINE | Windows builder, 2.5G Flint 2 |
| **graftGate** | macOS | 10.13.37.13 | tower (15) | ENMESHED | M4 Mac Mini, 16 GB |
| **biomeGate** | Linux | 10.13.37.3 | compute | **DOWN** | Threadripper 3970X, 128 GB, 3 VFIO GPUs |
| **northGate** | Windows | — | full | ONLINE | Ryzen 9950X3D, RTX 5090, 96 GB. **DO NOT DEPLOY.** |
| **grapheneGate** | Android | — | tower | ONLINE | Pixel 8a, GrapheneOS |
| **flockGate** | Linux | 10.13.37.6 | full | DOWN | i9-13900K, dead CMOS |
| **fieldGate** | Linux | — | full | OFFLINE | DDR3 NUC, dead CMOS |
| **swiftGate** | Windows | — | full | HW READY | House 2 hobby/gaming |
| **piGate** | Linux | — | tower | PLANNED | Raspberry Pi 500/500+, $180-190 |
| **riscGate** | Linux | — | tower | ON ORDER | Milk-V Jupiter 2, RISC-V, 60 TOPS NPU |
| **steamGate** | SteamOS | — | tower | QUEUED | Steam Deck OLED |
| **iosGate** | iOS | — | tower | GLACIAL | iPhone XS |
| **cloudGate** | Linux | — | tower | GLACIAL | Oracle Ampere A1 free tier |

**11 ONLINE** (6 NUCLEUS + graftGate enmeshed + 4 other). biomeGate **DOWN** (SSH recovery pending). 3 planned/on-order. 2 offline. 3 glacial/queued.

---

## REPOSITORY CATALOG (40 repos)

### Primals (16)

| Primal | Domain | Primary Gate | Description |
|--------|--------|-------------|-------------|
| **bearDog** | Security | ironGate | Crypto, BTSP identity, `trust.evaluate_peer` |
| **songBird** | Discovery | ironGate | Mesh routing, federation, MeshRelay, drawbridge |
| **biomeOS** | Orchestration | eastGate | Composition graph, capability routing, Neural API |
| **squirrel** | AI/MCP | eastGate | Agent orchestration, MCP integration |
| **toadStool** | Compute | strandGate | Compute dispatch, silicon ledger, WASM (38/48) |
| **barraCuda** | GPU | strandGate | GPU compute, HMC, concurrent routing, shaders |
| **coralReef** | Shaders | strandGate | Sovereign WGSL/SPIR-V/GLSL compiler, 3,553 tests |
| **rhizoCrypt** | Provenance | westGate | DAG provenance, braid.verify 99/100 |
| **loamSpine** | Provenance | westGate | Spine construction, braid structure |
| **sweetGrass** | Provenance | westGate | Braid attribution, riboCipher transport |
| **nestGate** | Storage | westGate | CAS, content-addressed storage, /depot/ + /provenance/ |
| **petalTongue** | UI | ironGate | Storytelling bridge, nestgate.io surface, Caddy |
| **skunkBat** | Defense | ironGate | Gossip audit, vine-bat validation, 672 tests |
| **swarmVine** | Gossip | ironGate | Epidemic gossip, cascade.notify, Windows DONE |
| **sourDough** | Bootstrap | graftGate | Starter culture, CI validators |
| **bingoCube** | Commitment | ironGate | Human-verifiable cryptographic commitment |

### Springs (9)

| Spring | Domain | Primary Gate | Description |
|--------|--------|-------------|-------------|
| **primalSpring** | Coordination | eastGate | Composition validation, hardware cascade |
| **wetSpring** | Science | westGate | Breseq/LTEE validation, gossip 4/4 |
| **neuralSpring** | AI | southGate | Neural/AI validation |
| **hotSpring** | GPU Compute | strandGate | QCD lattice, pseudoSpore, gossip 10/10 |
| **rustChip** | NPU | strandGate | Akida NPU driver stack |
| **airSpring** | Atmospheric | ironGate | ADS-B validation |
| **groundSpring** | Geospatial | ironGate | Geospatial validation |
| **healthSpring** | Clinical | ironGate | Health/clinical validation |
| **ludoSpring** | Gaming | ironGate | Game engine validation |

### Gardens (8)

| Garden | Domain | Primary Gate | Description |
|--------|--------|-------------|-------------|
| **cellMembrane** | Ops | sporeGate | VPS deployment, sovereignty boundary, 1,353 tests |
| **lithoSpore** | Verification | sporeGate | USB-deployable validation chassis, pseudoSpore website |
| **projectNUCLEUS** | Sovereignty | eastGate | Deployment infrastructure, manifest |
| **projectFOUNDATION** | Knowledge | westGate | Thread lineage, validation evidence |
| **esotericWebb** | UI | ironGate | Browser surface, agentic interaction |
| **blueFish** | Chemistry | eastGate | Analytical chemistry ETL |
| **helixVision** | Genomics | strandGate | 16S/WGS MinION→taxonomy |
| **initioChem** | CompChem | strandGate | Computational chemistry, hotSpring consumer |

### Protists (2)

| Protist | Domain | Primary Gate | Description |
|---------|--------|-------------|-------------|
| **footPrint** | GIS | ironGate | Home improvement planner, Leaflet/Turf.js |
| **tideGlass** | GPS/Drug | ironGate | Gene perturbation simulator, drug repurposing |

### Infrastructure (7)

| Repo | Domain | Authority | Description |
|------|--------|-----------|-------------|
| **wateringHole** | Coordination | eastGate | Ecosystem standards, cascade orchestration |
| **plasmidBin** | Depot | sporeGate | Binary depot, deploy scripts |
| **whitePaper** | Research | eastGate | Research documentation |
| **sporePrint** | Public | eastGate | GitHub Pages site (code on eastGate, deployed via golgiBody) |
| **benchScale** | Lab | eastGate | Lab validation infrastructure |
| **agentReagents** | Agents | eastGate | Agent configuration reagents |
| **fossilRecord** | Archive | eastGate | Ecosystem archive |

---

## TEAM WORK VECTORS — BY GATE

### eastGate — Overwatch + Orchestration

**Role**: Development machine, overwatch coordination, sovereignty layer. Code teams: biomeOS, squirrel, projectNUCLEUS.
**Hardware**: Ryzen 9 7950X, 128 GB DDR5, 10G SFP+

| Team | Primals/Repos | Current Work Vector |
|------|---------------|---------------------|
| **overwatch** | wateringHole, sporePrint, fossilRecord, whitePaper, benchScale, agentReagents | Ecosystem coordination, blurb cascade, glacial/orthogonal review. **IMMEDIATE**: NUCLEUS restart + hostname fix (`pop-os` → `eastGate`). |
| **primalSpring** | primalSpring | Composition validation, hardware cascade evolution, biome manifest. |
| **biomeOS** | biomeOS | category shadow FIXED, riboCipher P0 FIXED. **NEXT**: graph executor maturation, Neural API as primary routing. |
| **squirrel** | squirrel | 4,090 tests. **NEXT**: ironGate systemd deployment (`squirrel.sock`). |
| **projectNUCLEUS** | projectNUCLEUS | Sovereignty layer. Manifest-driven deployment infrastructure. |
| **blueFish** | blueFish | Analytical chemistry ETL. Parked. |

### ironGate — Primal Workhorse + NFT Braid

**Role**: Primary Linux builder, NFT braid/CAS compute, remaining primal code teams.
**Hardware**: i9-14900K, RTX 5070 Ti, 94 GB, 14 TB HDD + NVMe

| Team | Primals/Repos | Current Work Vector |
|------|---------------|---------------------|
| **bearDog** | bearDog | `trust.evaluate_peer` live. Stable. **WATCH**: eastGate socket rejections (runtime health). |
| **songBird** | songBird | MeshRelay SHIPPED. **NEXT**: `--node-id` / `--gate-id` flag for mesh identity. |
| **skunkBat** | skunkBat | vine-bat validation live. 672 tests. Stable — no immediate vector. |
| **swarmVine** | swarmVine | Windows port DONE. cascade.notify gossip types shipped. **NEXT**: gossip wiring for remaining 7/16 primals. |
| **bingoCube** | bingoCube | Human-verifiable cryptographic commitment. Stable. |
| **petalTongue** | petalTongue | nestgate.io surface (`947183a7`). axum 0.8 done. **NEXT**: WebGPU/wgpu render pipeline (G53). |
| **esotericWebb** | esotericWebb | V33 gossip mesh. 2 session lifecycle events. **NEXT**: HEAD method fix (NG-06), browser surface. |
| **footPrint** | footPrint | CSP + auto-load resolved. **NEXT**: squirrel UDS socket on ironGate. |
| **tideGlass** | tideGlass | G72 alignment done. **NEXT**: GPS core wiring to barraCuda linear algebra. |
| **airSpring** | airSpring | ADS-B validation. Parked. |
| **groundSpring** | groundSpring | Geospatial validation. Parked. |
| **healthSpring** | healthSpring | Health/clinical validation. Parked. |
| **ludoSpring** | ludoSpring | Game engine validation. Parked. |

### westGate — Data NAS + CAS Federation (**SOLO ENABLER**)

**Role**: Provenance data CAS, Nest Atomic testbed, 50.7 TB ZFS storage.
**Hardware**: Ryzen 7 5700X, 64 GB DDR4, 2 TB NVMe, ZFS raidz1 50.7 TB

| Team | Primals/Repos | Current Work Vector |
|------|---------------|---------------------|
| **rhizoCrypt** | rhizoCrypt | braid.verify 99/100 (0.3ms). E2E 8/8 (12ms). DAG lifecycle gossip. Stable. |
| **loamSpine** | loamSpine | Spine events (4 gossip). **NEXT**: HTTP consolidation (G72 Tier 2). |
| **sweetGrass** | sweetGrass | riboCipher transport FIXED. Braid attribution live. Backpressure design filed. |
| **nestGate** | nestGate | S147/S148. 1,666 tests. **NEXT**: content retrieval API (`/cas/{hash}`), CAS federation via songBird `content.locate`. |
| **wetSpring** | wetSpring | 4/4 gossip. Colocated on westGate tower. Local UDS to Nest Atomic. |
| **projectFOUNDATION** | projectFOUNDATION | 50.7 TB ZFS, 452 GB CAS, 5,800 objects. 89 PARTIAL datasets need braid. |

**SOLO ENABLER WORK — westGate CAS**:
> westGate's provenance trio (rhizoCrypt + loamSpine + sweetGrass) and nestGate CAS provide the **data integrity layer** that every other gate depends on for trusted content. The `native_braid.py` → Rust migration (1,308 LOC, last Python in production) is the critical throughput bottleneck: 145/s current → 16K/s target. nestgate.io Phase 3 (`/cas/{hash}` + cross-gate CAS federation via `content.locate`) enables any gate to verify and retrieve content from the mesh without direct westGate access. The CAS Data Plan for wetSpring + projectFOUNDATION (89 PARTIAL datasets, 452 GB) is the data pipeline that feeds the science tracks. **Until westGate CAS federation is live, provenance is westGate-local — every cross-gate braid.verify routes through westGate.**

### strandGate — Compute Trio + Batch Farm (**SOLO ENABLER**)

**Role**: Compute trio code teams, unattended HPC, QCD lattice campaigns, silicon validation.
**Hardware**: Dual EPYC 7452 (128 threads), 256 GB, RTX 3090 + RX 6950 XT + AKD1000

| Team | Primals/Repos | Current Work Vector |
|------|---------------|---------------------|
| **toadStool** | toadStool | Silicon ledger (`7f42eeb22`). 38/48 WASM. **NEXT**: S380+ evolution, wgpu 22→28 (G72 Tier 2). |
| **barraCuda** | barraCuda | Concurrent routing upstreamed. InitParams alignment FIXED. 22/22 gossip. **NEXT**: PrecisionBrain Fp64→F16 dispatch. |
| **coralReef** | coralReef | 3,553 tests. Cross-arch FIXED. **NEXT**: PTX SM120/Blackwell target, GEMM Phase 2 IPC. |
| **hotSpring** | hotSpring | 10/10 gossip COMPLETE. gpu_hmc fossilized upstream. **ACTIVE**: arXiv campaign 22/45 (~6h remaining). pseudoSpore E2E pipeline. Rung 1 QCD experiments queued. |
| **rustChip** | rustChip | Akida NPU driver stack. Parked until riscGate arrives. |
| **helixVision** | helixVision | MinION→taxonomy pipeline. Parked until QCD campaign completes. |
| **initioChem** | initioChem | Computational chemistry. hotSpring consumer. Parked. |

**SOLO ENABLER WORK — strandGate QCD**:
> strandGate is the **sole batch compute authority** — no other gate has 128 threads + 256 GB + multi-vendor GPU (NVIDIA + AMD + Akida NPU). The QCD lattice work (hotSpring → barraCuda → coralReef) proves the full compute pipeline: shader compilation → GPU dispatch → provenance-tracked results → arXiv publication. The silicon fold campaign validated 15/15 silicon units, proved AMD Infinity Cache advantage (20x for cache-resident lattices), and established the IC cliff at 128 MB. The arXiv 41/42 campaign (32⁴ lattice, Rung 1) is the first publishable result that demonstrates consumer-GPU lattice QCD — this is the **science credibility proof** for the entire ecosystem. **No other gate can run these workloads.**

### sporeGate — Topology + Depot + Cascade (**SOLO ENABLER**)

**Role**: Fleet foreman, inner membrane authority, depot owner, cascade hub.
**Hardware**: Ryzen 5 6600H NUC, 27 GB, 2.5G

| Team | Primals/Repos | Current Work Vector |
|------|---------------|---------------------|
| **cellMembrane** | cellMembrane | Sovereign defense wired (`5c628f6`). 1,353 tests. **NEXT**: `native_braid.py` → Rust convergence validator. |
| **lithoSpore** | lithoSpore | USB-deployable validation chassis. **NEXT**: pseudoSpore website deployments. |
| **ops** | plasmidBin | Depot 13/13 current. 57 binaries, 4 arch. **ACTIVE**: NanoWire retirement (19 items, 7 tiers). Inner membrane dnsmasq. cascade.notify gossip. |

**SOLO ENABLER WORK — sporeGate topology**:
> sporeGate is the **sole topology authority** — it owns the inner membrane (primals.eco mesh enrollment), the peptidoglycan layer (golgiBody relay), the depot (sole binary distribution point), and the cascade timer (15m systemd, zero drift). The NanoWire retirement audit (18 files, 19 items, 7 tiers) maps the complete path from SSH-based ops to mesh-native `capability.call` dispatch. Tier 2 retirement (gate.pull, gate.check, gate.info, service.*, plasmid.trigger) is the **gateway to autonomous cascade** — once these move to mesh dispatch, gates can self-update without SSH. The inner membrane three-domain topology (primals.eco pull / primal.eco mesh / nestgate.io PETI) was deployed by sporeGate and is the **structural foundation** that all gate enmeshment depends on. **Without sporeGate topology, no gate can enroll, pull binaries, or cascade.**

### blueGate — Windows Builder

**Role**: Sole Windows compilation authority, tower builder.
**Hardware**: Windows, 2.5G Flint 2 bridge

| Team | Primals/Repos | Current Work Vector |
|------|---------------|---------------------|
| **builder** | all 13 primals | 13/13 vertebrate built (23 min). `builder.serve :9800` mesh-native. **IMMEDIATE**: depot pull needed — current depot may be stale. `.210:7700` timed out from southGate. |

### graftGate — Darwin Builder

**Role**: Sole Apple/macOS compilation authority, iOS prerequisite.
**Hardware**: M4 Mac Mini, 16 GB

| Team | Primals/Repos | Current Work Vector |
|------|---------------|---------------------|
| **darwin builder** | 15 primals + sourDough | 15/15 compiled. Depot pushed (104M, BLAKE3). iOS cross-compile live. **NEXT**: iosGate (needs Apple Dev Program $99/yr). |

### southGate — Validation Canary

**Role**: Performance canary, LAN gossip proof, no WireGuard (deliberate).
**Hardware**: Pop!_OS, RTX 4060

| Team | Primals/Repos | Current Work Vector |
|------|---------------|---------------------|
| **validation** | full stack | 18.3K conn/s. LAN gossip VALIDATED (342/1,216 bidirectional). Hostname FIXED. **OPEN**: LAN IP discrepancy (topology `.149` vs actual `.148`). |

### biomeGate — GPU Lab (**DOWN**)

**Role**: Cross-vendor GPU validation, VFIO multi-gen testing. **CURRENTLY DOWN — needs SSH triage.**
**Hardware**: Threadripper 3970X, 128 GB, RTX 5060 + Titan V + K80

| Team | Primals/Repos | Current Work Vector |
|------|---------------|---------------------|
| **gpu lab** | (compute trio validation) | **DOWN.** 3 VFIO GPUs configured. coralReef 3,553 tests PASS. 44-experiment revalidation matrix staged. Exp 231 (K80 cross-gen quench) queued. **BLOCKED**: gate unreachable, needs SSH recovery. |

---

## SOLO ENABLER DEPENDENCY MAP

```
                    ┌─────────────────────────────┐
                    │     sporeGate TOPOLOGY       │
                    │  inner membrane / depot /    │
                    │  cascade / NanoWire retire   │
                    └──────────┬──────────────────┘
                               │ gates enroll, pull,
                               │ cascade through here
                    ┌──────────▼──────────────────┐
                    │     ALL GATES ENMESH         │
                    │  binaries + mesh identity +  │
                    │  gossip federation           │
                    └──────┬──────────┬───────────┘
                           │          │
              ┌────────────▼──┐  ┌────▼──────────────┐
              │  westGate CAS │  │ strandGate QCD     │
              │  provenance + │  │ silicon compute +   │
              │  data braid + │  │ arXiv publication + │
              │  CAS federate │  │ batch campaigns     │
              └───────┬───────┘  └────────┬───────────┘
                      │                   │
                      │   cross-gate      │  science
                      │   braid.verify    │  credibility
                      │   + content.get   │  proof
                      ▼                   ▼
              ┌────────────────────────────────────┐
              │     FULL ATOMIC ENMESHMENT         │
              │  any gate can: verify provenance,  │
              │  retrieve content, dispatch compute │
              │  — all mesh-native, no SSH          │
              └────────────────────────────────────┘
```

### What Each Solo Enabler Unlocks

| Enabler | Current Blocker | When Unblocked | What It Enables |
|---------|----------------|----------------|-----------------|
| **sporeGate: NanoWire Tier 2 retirement** | gate.pull/check still use SSH | `--mesh` shadow validation, then SSH removal | Autonomous cascade — gates self-update via mesh |
| **westGate: nestgate.io Phase 3** | `/cas/{hash}` not yet live | nestGate CAS federation API | Any gate can verify+retrieve content without westGate direct access |
| **westGate: native_braid.py → Rust** | Python bottleneck (145/s) | `membrane content.braid` wrapper | 16K/s braid throughput — data pipeline unblocked |
| **strandGate: arXiv Rung 1** | Campaign 22/45 in progress | 32⁴ lattice results published | First peer-reviewed proof of consumer-GPU lattice QCD |
| **strandGate: silicon fold validation** | Complete (15/15 measured) | Already unblocked | IC cliff characterization enables hardware-aware compute routing |

---

## CROSS-CUTTING WORK (all gates)

| Item | Scope | Status |
|------|-------|--------|
| **Gossip wiring** | 9/16 primals live. Remaining 7 need `gossip.inject` at call sites. | Each code team owns their primal. |
| **G72 Tier 2** | HTTP→songBird, axum 0.8 (done in petalTongue), wgpu 28, YAML unification | loamSpine HTTP consolidation is next. |
| **Glue deprecation** | 9 scripts marked, 4 fossilized, 5 active with replacement paths | westGate owns remaining 5. |
| **Depot pull** | blueGate needs fresh depot pull + redeploy | blueGate ops. |
| **Mesh identity** | songBird reports binary name, not gate hostname | songBird `--node-id` flag. |

---

*Wave 157k — 20 gates (11 online, biomeGate DOWN), 40 repos (16 primals, 9 springs, 8 gardens, 2 protists, 7 infra). Code teams: eastGate (biomeOS, squirrel, projectNUCLEUS + overwatch), ironGate (bearDog, songBird, skunkBat, swarmVine, bingoCube, petalTongue + products), strandGate (compute trio + science), westGate (provenance trio + nestGate + projectFOUNDATION), sporeGate (cellMembrane + lithoSpore + ops), graftGate (sourDough). Solo enablers: sporeGate topology, westGate CAS, strandGate QCD.*

---
*FOSSILIZED Wave 157k interstadial (Aug 13, 2026). Content superseded by ECOSYSTEM_BLURB.md and current ecosystem standards.*
