# The Watering Hole - ecoPrimals Ecosystem Guidance

**Purpose**: Authoritative project guidance for every primal in the ecoPrimals ecosystem  
**Audience**: Any primal, at any point in its evolution — and four external audiences (PIs, students, builders, compliance)  
**Last Updated**: Aug 1, 2026 (Wave 155n post-threshold: gen5 THESIS PROVEN ON LIVE DATA. 5 NUCLEUS gates. 7 glacial goals COMPLETE. 31 tracked. biomeOS v4.56 G22 COMPLETE. 46 depot bins. 35 docs fossilized.)

---

## What is the Watering Hole?

The Watering Hole is the shared knowledge layer of the ecoPrimals project. Every primal - whether newly conceived or production-hardened - comes here to understand the ecosystem it belongs to: what other primals exist, what standards govern interoperability, how coordination works, and what principles guide evolution.

This is not documentation about a subdirectory. This is the living reference for the entire project.

---

## Core Concepts

### What is a Primal?

A **primal** is a collection of **primitives** - small, focused capabilities that solve one domain well. Primals are autonomous: each is a self-contained Rust binary that knows only itself. Complexity is never solved by making a primal larger. It is solved through **coordination** - primals composing their primitives together at runtime, orchestrated by biomeOS.

**Key properties of every primal:**

- **Self-knowledge only**: A primal knows what it can do, never what others can do
- **Capability-based discovery**: Primals find each other at runtime by advertising capabilities
- **Zero compile-time coupling**: No primal imports another primal's code
- **Pure Rust**: 100% Rust application code, zero C dependencies
- **UniBin architecture**: One binary per primal, multiple operational modes

### What are Primitives?

Primitives are the atomic operations a primal provides. BearDog's primitives include Ed25519 signing, BLAKE3 hashing, and X25519 key exchange. Songbird's primitives include TLS 1.3 handshakes, mDNS discovery, and UDP multicast. A primitive is the smallest unit of capability in the ecosystem.

### How do Primals Coordinate?

Primals communicate via **JSON-RPC 2.0** over platform-agnostic transports (Unix sockets, abstract sockets, TCP, named pipes). They never share memory or embed each other's code. biomeOS discovers primals by their capabilities at runtime and coordinates them into higher-order behaviors.

The result: complex systems **emerge** from simple composition, rather than being engineered monolithically.

---

## The Primals

### Foundation Primals

These primals form the NUCLEUS deployment architecture. They are the bedrock of the ecosystem - production-ready, extensively tested, and required for core ecosystem function.

| Primal | Domain | Role | Status |
|--------|--------|------|--------|
| **BearDog** | Cryptography | All cryptographic operations: signing, encryption, key exchange, hashing, certificates, genetic lineage | Production (A+ LEGENDARY) |
| **Songbird** | Networking | Network orchestration: TLS 1.3, service discovery, NAT traversal, federation, BirdSong protocol, Pure Rust Tor | Production (S+) |
| **NestGate** | Data Storage | Content-addressed storage, dataset management, capability-based service discovery | Production (A++ TOP 1%) |
| **ToadStool** | Hardware Infrastructure | Hardware discovery, capability probing, compute orchestration: CPU, GPU, NPU, WASM, containers, edge. 23,000+ tests (9,232+ lib), **112 JSON-RPC methods** (17 groups). Node Atomic for sovereign compute. ecoBin v3.0 certified. riboCipher CLEAR + MitoBeacon. Zero-copy dispatch. Cross-architecture (`cargo check --target x86_64-pc-windows-gnu` passes, S329). **Phase 2 Silicon Atheism: cross-platform GPU backends** — `WgpuGpuDiscovery`, `PortableSwapExecutor`, `PortableResourceHandle` (S332). **S333 structural debt** — 7 large files refactored, hardcoded primal names → capability terms. Zero clippy warnings. Zero `/tmp` hardcoding. 100% env centralized. VFIO sovereign dispatch validated. | Production (A++ GOLD, S333+) |
| **BarraCuda** | Pure Math | 806 WGSL f64 shaders (the mathematics), naga-IR optimisation (FMA fusion, DCE), precision strategy (f64/DF64/f32). Writes the math; coralReef compiles it; toadStool runs it. Budded from ToadStool (S93). v0.3.5, 3,400+ tests | Production (A+) |
| **coralReef** | Shader Compilation | Sovereign WGSL→native shader compiler. naga parser + lowering passes (f64, FMA fusion, dead expression elimination). JSON-RPC IPC via XDG discovery. AMD E2E proven, NVIDIA SM70-SM89. coral-gpu unified compute abstraction. VFIO dispatch with PFIFO channel + V2 MMU + USERD_TARGET fix. **coral-glowplug** production-grade boot-persistent PCIe device lifecycle broker (systemd daemon, personality hot-swap, health monitor, auto-D0 recovery, VFIO-first boot, graceful shutdown, DRM render node fencing, IOMMU group handling). **FECS firmware direct execution proven** (LS bypass on clean falcon). SEC2 EMEM breakthrough (Exp 066-069). D3hot→D0 sovereign VRAM recovery. Sovereign power management designed (5-state model). Reproducibility checklist for adding new GPUs | Production (Phase 10, Iter 52) |
| **Squirrel** | AI Coordination | Sovereign AI model context protocol, multi-MCP coordination, vendor-agnostic inference | Production (A++) |
| **biomeOS** | Orchestration | Composition primal: v4.56 G22 COMPLETE — single-process dual-protocol (riboCipher + JSON-RPC), 244 capabilities, 27 signal graphs, 5 coordination patterns, capability routing, NUCLEUS composition, PathwayLearner, bonding model, Dark Forest, provenance trio wiring, `signal.dispatch`, `primal.announce`, `composition.test_swap`, stability tiers, adaptive routing weights, composition intelligence, guideStone contract | Production (v4.56, Security A++ LEGENDARY) |

### Post-NUCLEUS Primals

These primals build emergent behaviors on the NUCLEUS foundation. They compose into higher-order patterns (RootPulse, Memory & Attribution Stack) coordinated by biomeOS via the Neural API. Each is functional and tested, representing the next evolutionary phase.

| Primal | Domain | Role | Status |
|--------|--------|------|--------|
| **petalTongue** | Representation | Universal UI: visual, audio, terminal, web, headless. Accessibility-first multi-modal rendering | Production (A++) |
| **rhizoCrypt** | Ephemeral Memory | Content-addressed DAG engine for working memory. Sessions, Merkle trees, real-time streaming | Production (A+) |
| **sweetGrass** | Attribution | Semantic provenance (v0.7.38). W3C PROV-O braids, fair attribution, 37 canonical methods + 10 wire-name aliases, tarpc 0.37 + REST + UDS, UniBin, ecoBin, Edition 2024, GAP-36 wire reconciliation, Provenance Trio coordination, Tower Atomic enforced | Production |
| **LoamSpine** | Permanence | Immutable linear ledger for selective permanence. Loam Certificates for ownership and transfer | Production (A+) |
| **skunkBat** | Defense | Defensive network security: threat detection, graduated response, baseline profiling | Production |

### Supporting Tools

| Tool | Purpose |
|------|---------|
| **sourDough** | Starter culture - scaffolding, genomeBin tooling, ecosystem bootstrapping |

---

## Composed Systems

Primals achieve their greatest power through composition. These are not separate projects - they are coordination patterns that emerge when primals work together.

### Tower Atomic

**What**: BearDog (crypto) + Songbird (TLS/HTTP) = Pure Rust HTTPS

**How**: Songbird implements TLS 1.3 protocol logic. BearDog provides all cryptographic operations via JSON-RPC. Neither embeds the other. The result is a fully Pure Rust HTTPS stack with zero C dependencies.

**Used by**: Any primal that needs external network access routes through Tower Atomic.

### NUCLEUS

**What**: The full primal composition orchestrated by biomeOS.

**Layers**:
- **Tower Atomic** = BearDog + Songbird (crypto + network)
- **Node Atomic** = Tower + ToadStool (hardware) + BarraCuda (math)
- **Nest Atomic** = Tower + NestGate (+ storage)
- **Full NUCLEUS** = All primals + Squirrel (+ AI)

*Note*: BarraCuda budded from ToadStool into a standalone primal (S93).
BarraCuda is pure math — WGSL shaders and precision strategy. coralReef
compiles the math to native GPU binaries. ToadStool discovers and dispatches
hardware. Springs depend on BarraCuda directly for math without pulling
ToadStool's runtime or coralReef's compiler.

biomeOS composes these atomics based on what capabilities are available at runtime.

### The Coordination Triad: quorumSignal / rootPulse / waterFall

Three coordination domains form the ecosystem's nervous system. Each uses the
5 `CoordinationPattern` execution strategies (Sequential, Parallel, ConditionalDag,
Pipeline, Continuous) but serves a distinct biological purpose:

| Domain | Role | Analogy | Status |
|--------|------|---------|--------|
| **quorumSignal** | SENSE — observe, discover, react | Afferent nervous system | First-class: 15 atomic graphs, `signal.dispatch` |
| **rootPulse** | ACTION — create, mutate, prove | Efferent nervous system | Partial: `nest.commit` signal + pattern wired |
| **waterFall** | SYNC — ecosystem coherence across gates | Autonomic nervous system | Fully Rust (`membrane temporal.cascade`), manifest-driven |

Named after bacterial quorum sensing: collective behavior emerges when enough
gate NUCLEUS instances participate. The quorum is the minimum primal set for an
atomic operation — Tower quorum is 3, Nest quorum is 4, Full NUCLEUS is 13.

**Short triad**: quorum, pulse, fall.

**Specification**: `primalSpring/specs/NEURAL_API_EVOLUTION.md` (Coordination Domains section)

### rootPulse (ACTION — efferent)

**What**: Distributed version control that emerges from primal coordination - not a monolithic VCS. The "pulse" coordination domain of the triad.

**Composition**:
- **rhizoCrypt** provides the ephemeral DAG workspace (fast, lock-free, present/future)
- **loamSpine** provides the immutable linear history (permanent, cryptographically provable, past)
- **nestGate** provides content-addressed blob storage
- **bearDog** provides cryptographic signing and verification
- **sweetGrass** provides semantic attribution tracking
- **songbird** provides discovery and federation

**Coordinator**: biomeOS orchestrates these primals via the Neural API. No primal knows about "version control" - biomeOS composes their primitives into temporal coordination patterns, and version control emerges.

**Core insight**: "rootPulse is what primals DO together, not what they ARE."

**Five operations**: commit, branch, merge, diff, federate — all composed from atomic primal capabilities via `signal.dispatch` and `graph.execute`.

### Plasmodium (Over-NUCLEUS Collective)

**What**: The emergent coordination layer formed when 2+ NUCLEUS instances bond covalently.

**Analogy**: Named after the slime mold *Physarum polycephalum* -- no central brain, collective intelligence, pulsing coordination, graceful degradation.

**How**: biomeOS on any gate queries the local Songbird mesh for bonded peers, connects to their NUCLEUS instances, and aggregates capabilities, models, and load into a unified collective view. Workloads route to the best gate based on capability match, resource availability, and model affinity.

**Key properties**:
- No master node -- any gate can query the collective
- Gates join and leave dynamically (like slime mold pseudopods)
- Uses only existing primal primitives (Songbird mesh, BearDog trust, AtomicClient IPC)
- Security: genetic lineage trust via shared family seed, BearDog Dark Forest verification

**Specification**: `phase2/biomeOS/specs/PLASMODIUM_OVER_NUCLEUS_SPEC.md`  
**CLI**: `biomeos plasmodium status|gates|models`

### Neural API

**What**: biomeOS's adaptive orchestration layer that routes semantic requests to capable primals.

**How**: A caller requests `capability.call("crypto", "sha256")` and the Neural API discovers which primal provides that capability, routes the request, and returns the result. The caller never needs to know about BearDog specifically.

**Architecture**:
- Layer 1: Primals (capabilities via JSON-RPC)
- Layer 2: biomeOS (orchestration, routing, learning)
- Layer 3: Niche APIs (domain patterns like RootPulse, RPGPT)

**Five Coordination Patterns** (all driven by TOML graphs):

| Pattern | Method | Description |
|---------|--------|-------------|
| Sequential | `graph.execute` | Nodes in dependency order |
| Parallel | `graph.execute` | Independent nodes concurrently |
| ConditionalDag | `graph.execute` | DAG with `condition`/`skip_if` branching |
| Pipeline | `graph.execute_pipeline` | Streaming via bounded mpsc channels — items flow through nodes immediately |
| Continuous | `graph.start_continuous` | Fixed-timestep tick loop (e.g., 60Hz for game engines) |

**biomeOS as Composition Primal**: biomeOS is functionally the super-service — the
primal that composes all other primals into systems. While it sits at the same level
as other primals (sovereign, self-contained, JSON-RPC first), its unique role is
orchestrating emergent systems: RootPulse (version control), RPGPT (game engines),
AlphaFold-class (protein folding), and any other system that emerges as a function
of primal coordination.

**Streaming (v2.43)**: Pipeline graphs use NDJSON streaming — primals write multiple
response lines per request. The `AtomicClient::call_stream()` reads them as they
arrive. No new protocol needed. All primals already have streaming transport.

The PathwayLearner analyzes execution metrics and suggests optimizations (parallelization,
prewarming, batching, caching) that improve over time.

---

## Architecture Standards

These standards define how every primal is built, packaged, and deployed.

### UniBin - Binary Structure Standard

One binary per primal, multiple operational modes via subcommands. Professional CLI with `--help`, `--version`, and structured error messages. Every primal is a single executable named after itself.

**Specification**: `fossilRecord/wave150s_standards/ECOBIN_ARCHITECTURE_STANDARD.md` (consolidated — UniBin is a subset of ecoBin)

### ecoBin - Universal Portability Standard

ecoBin = UniBin + Pure Rust + Cross-Platform. Zero C dependencies in application code, cross-compiles to any Rust target with a single `cargo build` command, platform-agnostic IPC with runtime transport discovery.

**Specification**: `fossilRecord/wave150s_standards/ECOBIN_ARCHITECTURE_STANDARD.md`

### genomeBin - Autonomous Deployment Standard

genomeBin = ecoBin + deployment wrapper. Self-extracting archive that auto-detects the system, installs the correct binary, configures services, and validates health. One command installs on any system with zero manual configuration.

**Specification**: See `fossilRecord/wave150s_standards/ECOBIN_ARCHITECTURE_STANDARD.md` (genomeBin section)

### The Evolutionary Ladder

```
UniBin   (structure)    → One binary, multiple modes
  ↓
ecoBin   (portability)  → + Pure Rust, cross-compilation, platform-agnostic IPC
  ↓
genomeBin (deployment)  → + Auto-detection, service integration, health monitoring
```

All ecoBins are UniBins. All genomeBins are ecoBins. Each stage adds capability without replacing the previous.

---

## Communication Standards

### Primal IPC Protocol

JSON-RPC 2.0 over platform-agnostic transports. Capability-based discovery with zero cross-embedding. Every primal implements its own IPC independently - standards define WHAT, primals implement HOW.

**Specification**: `protocols/CAPABILITY_WIRE_STANDARD.md` (IPC protocol consolidated here)

### Universal IPC Standard

Behavioral specification for multi-transport IPC. Each primal discovers the best transport at runtime: Unix sockets on Linux/macOS, abstract sockets on Android, named pipes on Windows, TCP as universal fallback. No shared IPC crate - each primal owns its communication code.

**Specification**: `protocols/CAPABILITY_BASED_DISCOVERY_STANDARD.md`

### BirdSong Protocol

Encrypted UDP discovery protocol for auto-trust within genetic lineages. Songbird broadcasts encrypted beacons; only primals sharing the same family seed can decrypt them. Zero metadata leakage.

**Specification**: `birdsong/BIRDSONG_PROTOCOL.md`

### Semantic Method Naming

Method names describe intent, not implementation: `crypto.sign`, `tls.handshake`, `storage.put`. Domain namespaces enable Neural API translation and isomorphic evolution across primals.

**Specification**: `protocols/SEMANTIC_METHOD_NAMING_STANDARD.md`

---

## Security Model

### Genetic Lineage

A group of primals sharing a common `family_seed` - enabling cryptographic auto-trust. BearDog manages lineage seeds (nuclear DNA, for identity/permissions) and beacon seeds (mitochondrial DNA, for Dark Forest discovery).

### Auto-Trust Within Family

Primals of the same genetic lineage trust each other automatically. Decryption of a BirdSong beacon proves family membership. No manual configuration, no certificate authorities.

### Zero Trust Outside Family

No trust without family membership. Encrypted payloads are unreadable to outsiders. Continuous validation. Dark Forest protocol ensures zero metadata leakage - observers cannot even tell that communication is occurring.

### Pure Rust Security

Zero C dependencies eliminates entire classes of memory safety vulnerabilities. RustCrypto suite for all cryptographic operations. No openssl, no ring, no C assembly.

---

## Primal Interaction Map

### Currently Working

- **Songbird + BearDog**: Encrypted BirdSong discovery (Tower Atomic)
- **biomeOS + All Primals**: Health monitoring, capability discovery, Neural API routing
- **biomeOS + petalTongue**: Real-time SSE events for ecosystem visualization

### Wired (biomeOS coordination layer)

- **rhizoCrypt + LoamSpine + sweetGrass**: Provenance trio — `rootpulse_commit` graph orchestrates dehydration → sign → store → commit → attribute
- **Any Spring + Provenance Trio**: `provenance_pipeline` graph — universal experiment provenance
- **NestGate + LoamSpine**: Content-addressed storage backing immutable history

### primalSpring Coordination (ecosystem self-validation)

- **primalSpring + All NUCLEUS Primals**: Atomic composition testing (Tower, Node, Nest, Full NUCLEUS)
- **primalSpring + biomeOS**: Graph execution validation — all 5 coordination patterns with real primals
- **primalSpring + Provenance Trio**: RootPulse emergent system validation (commit, branch, merge, diff, federate)
- **primalSpring + Songbird Mesh**: Plasmodium formation, gate failure, capability aggregation
- **primalSpring + neuralSpring + wetSpring + hotSpring + ToadStool + NestGate**: helixVision structure prediction pipeline
- **primalSpring + airSpring + wetSpring + neuralSpring**: Cross-spring ecology data flow
- **primalSpring + fieldMouse + NestGate + sweetGrass**: Edge data ingestion pipeline
- **primalSpring + petalTongue**: SSE visualization pipeline
- **primalSpring + Squirrel**: AI coordination via biomeOS capability graph

### Under Development

- **Songbird + Songbird**: Cross-tower federation, multi-family routing

**Detail**: See primal composition maps in `compositions/PRIMAL_REGISTRY.md`

---

## Design Principles

1. **Single Responsibility**: Each primal does one thing. BearDog only does cryptography. Songbird only does networking. Complexity emerges from coordination, not from expanding scope.

2. **Interface Segregation**: Primals expose narrow, focused interfaces. LoamSpine doesn't know about "commits" - it provides append-only storage. biomeOS composes that into version control.

3. **Dependency Inversion**: Primals depend on abstract capabilities, not concrete implementations. Any storage provider works, not just NestGate.

4. **Message Passing**: Communication via messages over IPC, never shared state. No locks, no race conditions, inherently concurrent.

5. **Emergence Over Engineering**: Don't build a monolithic VCS - coordinate existing primals and let version control emerge. Don't build a monolithic security stack - let BearDog and Songbird compose into Tower Atomic.

---

## Document Index

### Root (always at top level)
- **`STANDARDS_AND_EXPECTATIONS.md`** — Single-document reference for all standards, expectations, and conventions
- **`GLOSSARY.md`** — Definitive ecosystem terminology
- **`ORTHOGONAL_DIMENSIONS_REVIEW.md`** — Active dimensional review tool

### `foundations/` — Architectural Invariants (9 standards)

Long-term architectural standards — rarely change.

| Standard | Summary |
|----------|---------|
| `DIDERM_DOMAIN_ARCHITECTURE.md` | Domain trust barriers (`primals.eco` / `primal.eco` / `nestgate.io`) + sovereignty evolution roadmap |
| `DARK_FOREST_GLACIAL_GATE_STANDARD.md` | 5 security invariants |
| `K_DERM_TOPOLOGY_STANDARD.md` | Cell envelope model (layers, bonding, channels) |
| `BONDING_MODEL_STANDARD.md` | Organo-metallo-salt bonding model |
| `SOVEREIGNTY_STANDARDS.md` | Calibrate → shadow → cutover protocol |
| `OVERWATCH_POSITION_STANDARD.md` | Floating coordination position |
| `LICENSING_AND_COPYLEFT.md` | scyBorg copyleft framework |
| `PRIMAL_SPRING_GARDEN_TAXONOMY.md` | Primal / spring / garden / tool taxonomy |
| `SECRETS_AND_SEEDS_STANDARD.md` | Seed and credential management |

### `protocols/` — Wire Protocols & IPC (10 standards)

Stable once shipped — wire formats, capability system, coordination patterns.

| Standard | Summary |
|----------|---------|
| `BTSP_PROTOCOL_STANDARD.md` | BearDog Trust Security Protocol |
| `RIBOCIPHER_TRANSPORT_SIGNAL_STANDARD.md` | Transport signal routing (3 tiers) |
| `CAPABILITY_WIRE_STANDARD.md` | Capability-based wire format |
| `CAPABILITY_BASED_DISCOVERY_STANDARD.md` | Runtime capability discovery |
| `CAPABILITY_DOMAIN_REGISTRY.md` | Canonical domain namespace registry |
| `SEMANTIC_METHOD_NAMING_STANDARD.md` | `domain.verb` API naming |
| `IMPULSE_POTENTIAL_STANDARD.md` | Inter-gate impulse/potential coordination |
| `CONTEXT_BRAID_STANDARD.md` | Ephemeral developer-state weaving |
| `ECOSYSTEM_COMMUNICATION_STANDARD.md` | Three-layer coordination (git + impulses + braids) |
| `PROVENANCE_TRIO_INTEGRATION_GUIDE.md` | rhizoCrypt + loamSpine + sweetGrass wiring |

### `operations/` — Gate Deployment & Mesh Ops (12 standards)

Evolve with infrastructure — deployment, ownership, gate operations.

| Standard | Summary |
|----------|---------|
| `GATE_SETUP_STANDARD.md` | Gate setup, sync, resync protocol |
| `GATE_NUCLEUS_SYSTEMD_STANDARD.md` | systemd deployment standard |
| `GATEHOUSE_DARKFOREST_STANDARD.md` | Drawbridge + Dark Forest demarcation |
| `GRAPHENEGATE_BOOTSTRAP_STANDARD.md` | Android Dark Forest bootstrap |
| `MESH_DEPLOYMENT_STANDARD.md` | Multi-gate mesh handoff |
| `DEPLOYMENT_VALIDATION_STANDARD.md` | Deployment validation protocol |
| `DISTRIBUTED_COVALENT_DEPLOYMENT.md` | Multi-gate compute architecture |
| `GATE_SPRING_OWNERSHIP.md` | Canonical gate-spring routing |
| `GATE_TEAM_COORDINATION_MATRIX.md` | Team-gate-hardware assignment |
| `REPO_MEMBRANE_BOUNDARY.md` | Inner/outer membrane repo classification |
| `DISCOVERED_BY_STANDARD.md` | Discovery narrative standard |
| `SPORE_OWNERSHIP_MATRIX.md` | Spore/gate ownership assignments |

### `compositions/` — Composition Patterns (6 standards)

Evolve with products — routing, health, tick models.

| Standard | Summary |
|----------|---------|
| `COMPOSITION_ROUTING_STANDARD.md` | Live composition deployment (wildcard DNS, drawbridge, CAS) |
| `COMPOSITION_HEALTH_STANDARD.md` | Composition health JSON-RPC |
| `COMPOSITION_TICK_MODEL_STANDARD.md` | Temporal tick model for compositions |
| `CROSS_SPRING_COORDINATION_STANDARD.md` | Cross-spring data flow |
| `MEMBRANE_CHANNEL_ARCHITECTURE.md` | 3 channels + RustDesk |
| `PRIMAL_REGISTRY.md` | Authoritative primal/spring catalog |

### Per-Domain Guidance
- `birdsong/` — BirdSong protocol, Dark Forest beacon genetics, Tower Atomic TLS
- `btsp/` — BearDog technical stack
- `sporePrint/` — Content guide + spring evolution targets
- `petaltongue/` — Integration docs (7 files)
- `airspring/` — Composition guidance
- `healthspring/` — Composition guidance
- `compute-sharing/` — Sovereign compute sharing + workload definitions

### Infrastructure
- `provision/` — golgi provisioning scripts + Caddyfiles
- `systemd/` — Service templates + cascade timers
- `graphs/` — Declarative deploy graph TOMLs
- `heads/` — Auto-published gate status files

### Publications
- `publications/` — Auditable data transfers for papers and pseudoSpore
- `publications/LATTICE_QCD_CONSUMER_GPU_DATA.md` — SU(2) HMC results (arXiv hep-lat)

### Handoffs
- `handoffs/ECOSYSTEM_BLURB.md` — Current wave blurb (dissemination artifact)
- `handoffs/SPOREPRINT_BLURB.md` — sporePrint demonstration era blurb
- `handoffs/TEAM_STARTUP_BLURB_TEMPLATE.md` — Gate/code team bootstrapping

### Fossil Record
- `fossilRecord/` — All archived content across Waves 34–155n
- 24 checkpoint directories spanning gen1→gen5 threshold crossing
- 35+ files fossilized in Wave 155n alone across 3 checkpoints

---

## For New Primals

If you are a new primal entering the ecosystem:

1. **Read this document** to understand the ecosystem you are joining
2. **Review `compositions/PRIMAL_REGISTRY.md`** to see what capabilities already exist
3. **Follow UniBin standard** from day one (single binary, subcommands)
4. **Target ecoBin** (Pure Rust, zero C deps, cross-compilation)
5. **Implement IPC** following `protocols/CAPABILITY_WIRE_STANDARD.md` (JSON-RPC 2.0)
6. **Advertise capabilities** so biomeOS can discover and coordinate you
7. **Register your primal** in `compositions/PRIMAL_REGISTRY.md` with your primitives
8. **Get your face together** — your repo should be reviewable by any of the four external audiences in 5 minutes (see `STANDARDS_AND_EXPECTATIONS.md`)

You do not need to know about other primals. You need to know what you can do, and how to tell the ecosystem about it.

---

## Getting Your Face Together

Every spring and primal should be independently reviewable by outsiders.
See **`STANDARDS_AND_EXPECTATIONS.md`** for the full checklist,
but the short version is: a reviewer should be able to do this in 5 minutes:

1. Open `README.md` → understand what this does and what it replaces
2. `cargo test --workspace` → see all tests pass
3. `cargo run --release --bin validate_<something>` → see explicit PASS/FAIL
4. Open `CHANGELOG.md` → understand recent evolution
5. Open `whitePaper/baseCamp/README.md` → see the faculty and science context

Four external audiences will read your repo without context:

| Audience | What They Look For |
|----------|-------------------|
| **Faculty / PIs** | What does this replace? How does it compare to commercial tools? Can I verify claims? |
| **Students / Core Facilities** | How do I build it? How do I run it? Where do I start? |
| **Hardware Builders / Hobbyists** | What hardware does it need? What can my GPU do? How do I contribute compute? |
| **Compliance / Institutional Review** | What standards does it meet? What are the dependencies? Is it safe? What's the license? |

The `publicRelease/` documents in `whitePaper/attsi/non-anon/contact/publicRelease/`
make ecosystem-wide claims. Each spring and primal must ensure its own presentation
supports those claims.

---

**The Watering Hole is maintained by all primals. Every primal's evolution strengthens the whole ecosystem.**

---

## Live Sites

| Site | Purpose |
|------|---------|
| [sporeprint.primals.eco](https://sporeprint.primals.eco) | ecoPrimals ecosystem documentation (400+ pages) |
| [detroit.primals.eco](https://detroit.primals.eco) | Public evidence library — Detroit charter school racketeering investigation (181 pages) |
| [gorilla.primals.eco](https://gorilla.primals.eco) | guerillaGorilla accountability infrastructure methodology |
| [footprint.primals.eco](https://footprint.primals.eco) | Sovereign GIS platform |
| [webb.primals.eco](https://webb.primals.eco) | esotericWebb cross-evolution CRPG |
