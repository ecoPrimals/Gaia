<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Ecosystem Architecture Context

**Purpose**: Universal operational context for any instance (AI or human) working on any part of the ecoPrimals project. This document describes *how the ecosystem works* — patterns, models, workflows — independent of any specific deployment.

**Companion**: `DEPLOYMENT_INSTANCE.toml` contains the instance-specific state (IPs, SSH aliases, active wave, VPS topology) for *this* deployment. A parallel team sharing the repos would use this document unchanged but write their own instance TOML.

**Deep methodology**: `infra/whitePaper/gen4/knome/THE_PROMPT_BANK.md` — 6 months of K-NOME working prompts and the methodology behind ecosystem coordination.

**Last Updated**: 2026-06-13 (Wave 111)

---

## 1. Architecture Model

### The Three Context Tiers

```
Tier 1: whitePaper (Theory + Methodology)
  └── gen4/knome/ — K-NOME methodology, prompt bank, geological constraint
  └── gen4/architecture/ — sovereignty evolution, K-Derm reconciliation
  └── gen5/ — external collaboration model, collaborator case studies

Tier 2: wateringHole (Universal Ops Standards)  ← YOU ARE HERE
  └── *_STANDARD.md — 50+ ecosystem standards (portable to any deployment)
  └── This document — architecture, patterns, workflows
  └── ECOSYSTEM_COMMUNICATION_STANDARD.md — coordination artifact model

Tier 3: Instance Layer (This Deployment)
  └── DEPLOYMENT_INSTANCE.toml — VPS nodes, IPs, SSH, endpoints
  └── freshness.toml — live HEAD commits (regenerated per cascade)
  └── impulses/active/ — current FRAGOs (time-bounded work DAGs)
  └── ecosystem_manifest.toml [topology] — this fleet's node placement
```

### The Communication Trio

The ecosystem coordinates through three artifacts (see `ECOSYSTEM_COMMUNICATION_STANDARD.md`):

- **Handoffs** (loamSpine analog) — permanent fossil record, `handoffs/archive/`
- **FRAGOs** (rhizoCrypt analog) — time-bounded work DAGs, `impulses/active/`
- **Blurbs** (sweetGrass analog) — session-scoped context seeds

### Parallel Deployment Model

The architecture supports multiple independent deployments sharing the same repos:

- **Universal layer** (this doc + standards): usable by any NUCLEUS deployment unchanged
- **Instance layer** (`DEPLOYMENT_INSTANCE.toml` + FRAGOs): unique per fleet
- **Lineage** (handoffs + whitePaper): shared history, read-only reference

A parallel HPC team could share GitHub repos, have their own peptidoglycan layer (build hub), file their own FRAGOs, and run their own cascade — all while using the same standards.

---

## 2. Workspace Layout

Every gate (deployment endpoint) maintains the same workspace structure:

```
~/Development/ecoPrimals/          (or $ECOPRIMALS_ROOT)
├── primals/          # 15 primal repos (bearDog, songBird, biomeOS, etc.)
├── springs/          # 8 spring repos (hotSpring, neuralSpring, etc.)
│   └── primalSpring/ # Infrastructure spring (not a primal — provides IPC crate)
├── gardens/          # 5 garden repos (cellMembrane, lithoSpore, etc.)
├── infra/            # Shared infrastructure
│   ├── wateringHole/ # Standards, handoffs, impulses, manifest
│   ├── plasmidBin/   # Binary depot (checksums.toml, provenance.toml, primals/)
│   ├── whitePaper/   # Scientific whitepaper (gen0-gen5)
│   ├── sporePrint/   # Public-facing project
│   ├── benchScale/   # Benchmarking tools
│   └── agentReagents/ # AI agent tools
├── fossilRecord/     # Archived history
└── sort-after/       # Unsorted staging
```

### Key Files

| File | Purpose |
|------|---------|
| `infra/wateringHole/ecosystem_manifest.toml` | Repo catalog, gate profiles, topology, sync config |
| `infra/wateringHole/freshness.toml` | Live HEAD commits (published by cascade) |
| `infra/wateringHole/DEPLOYMENT_INSTANCE.toml` | This deployment's VPS nodes, endpoints, paths |
| `infra/plasmidBin/checksums.toml` | BLAKE3 hashes for all deployed binaries |
| `infra/plasmidBin/provenance.toml` | Build traceability (commit, rustc, timestamp) |
| `infra/plasmidBin/sources.toml` | Source registry for all primal repos |
| `gardens/cellMembrane/membrane.toml` | K-Derm layer config, channels, service topology |

---

## 3. The Cascade System

### What It Does

The cascade is how code flows from development to production. It's a manifest-driven parallel sync system that keeps all repos coherent across git remotes and gates.

### How to Run It

```bash
membrane temporal.cascade                 # full parallel sync
membrane temporal.cascade --check         # dry-run: show stale repos
membrane temporal.cascade --with-harvest  # sync + rebuild drifted primals
membrane temporal.cascade --clone-missing # clone repos not yet on this gate
membrane temporal.sync path/to/repo       # single-repo sync
```

### Flow Model

```
Sovereign Authority (Forgejo)  ←→  Local Gate  →  Public Mirror (GitHub)
         ↕                                              ↕
    VPS workspace                                  Outer membrane
    (depot authority)                             (read-only mirror)
```

The cascade:
1. Reads `ecosystem_manifest.toml` to discover repos for this gate
2. Pulls from sovereign authority (Forgejo SSH) — the single source of truth
3. Pushes to public mirror (GitHub) — the outer membrane
4. Publishes `freshness.toml` with HEAD commits
5. Optionally harvests (builds) primals with upstream changes

### Remote Naming Convention

Every repo has two remotes:
- `forgejo` → sovereign authority (SSH, inner membrane)
- `origin` → public mirror (HTTPS, outer membrane)

### Conflict Resolution

```bash
# If ff-only fails (common on shared repos like wateringHole):
git pull --rebase origin main    # or forgejo main
git push forgejo main && git push origin main

# If freshness.toml conflicts (auto-generated, always take theirs):
git checkout --theirs freshness.toml && git add freshness.toml && git commit --no-edit
```

---

## 4. Build and Deploy Pipeline

### Build Commands

```bash
membrane plasmid.build <primal> [--target T] [--dry-run]  # single guideStone-grade build
membrane plasmid.harvest [--force] [--target T]            # build all changed primals
membrane plasmid.ndk.check                                  # verify NDK for Android builds
```

### Deploy Commands

```bash
membrane plasmid.refresh              # push binaries to VPS (atomic replace + restart)
membrane plasmid.pipeline             # zero-touch: harvest → refresh → health check
membrane plasmid.depot_sync           # inner→outer membrane BLAKE3 diff sync
```

### Gate Enrollment

```bash
membrane gate.bootstrap <name> [--dry-run] [--mobile]  # full 6-phase enrollment
membrane gate.status                                    # local health (JSON-RPC + depot + mesh)
membrane gate.profile <gate>                           # read gate config from manifest
membrane gate.health                                   # VPS 13-primal sweep via SSH
```

### Binary Depot Structure

```
plasmidBin/
├── checksums.toml        # BLAKE3 hashes per target
├── provenance.toml       # Build metadata (commit, rustc, timestamp, blake3)
├── sources.toml          # Source registry (repo URLs, binary names, build args)
└── primals/
    ├── x86_64-unknown-linux-musl/    # VPS + desktop gates
    └── aarch64-unknown-linux-musl/   # ARM gates (grapheneGate, mobile NUCs)
```

---

## 5. Configuration Model

### Resolution Priority

1. Environment variables (highest)
2. `membrane.toml` in workspace or `/etc/membrane/membrane.toml`
3. Compiled defaults in `cellmembrane-types` (lowest)

### Key Environment Variables

| Variable | Purpose |
|----------|---------|
| `ECOPRIMALS_ROOT` | Local workspace root |
| `MEMBRANE_SSH_HOST` | SSH alias for inner membrane |
| `FORGEJO_SSH_HOST` | Forgejo clone endpoint |
| `VPS_ECOPRIMALS_ROOT` | VPS workspace root |
| `MEMBRANE_VPS_PEER` | Songbird federation peer address |
| `WAN_DEPOT_URL` | Public binary depot URL |
| `MEMBRANE_INSTALL_BASE` | Binary install base path |
| `PRIMAL_BIND_MODE` | Startup bind mode override |
| `ANDROID_NDK_HOME` | NDK root for Android cross-compile |

All variable names and defaults are defined in `cellmembrane-types/src/service.rs`. Instance-specific values (IPs, hosts) live in `DEPLOYMENT_INSTANCE.toml`.

---

## 6. Primal Composition

### The 13 NUCLEUS Primals

| Primal | Binary | Domain |
|--------|--------|--------|
| bearDog | `beardog` | Cryptography (signing, encryption, key exchange, certificates) |
| songBird | `songbird` | Networking (TLS, discovery, federation, NAT traversal) |
| nestGate | `nestgate` | Storage (content-addressed, capability discovery) |
| toadStool | `toadstool` | Hardware (GPU/CPU/NPU probing, compute orchestration) |
| barraCuda | `barracuda` | Math/GPU (806 WGSL f64 shaders, precision strategy) |
| coralReef | `coralreef` | Shader compile (WGSL→native, naga-IR, VFIO dispatch) |
| squirrel | `squirrel` | AI coordination (MCP, inference routing) |
| biomeOS | `biomeos` | Orchestration (Neural API, composition, coordination) |
| rhizoCrypt | `rhizocrypt` | Provenance (ephemeral DAG, attestation) |
| loamSpine | `loamspine` | Persistent store (anchored, immutable lineage) |
| sweetGrass | `sweetgrass` | Data provenance (braid signals, dataset tracking) |
| petalTongue | `petaltongue` | UI/CLI (human interface, terminal rendering) |
| skunkBat | `skunkbat` | Telemetry (shadow data, correlation, monitoring) |

### NUCLEUS Atomic Model

```
Tower (electron):   BearDog + Songbird — trust boundary, crypto, discovery
Node  (proton):     Tower + ToadStool + barraCuda + coralReef — compute
Nest  (neutron):    Tower + NestGate + rhizoCrypt + loamSpine + sweetGrass — storage
NUCLEUS (atom):     Tower + Node + Nest (9 core primals)
Meta-tier:          biomeOS + Squirrel + petalTongue — cross-atomic
Full:               13 primals (NUCLEUS + Meta-tier + skunkBat)
```

### Standard Startup Envelope

```bash
$PRIMAL server --bind-mode $PRIMAL_BIND_MODE --port $PORT
```

- `PRIMAL_BIND_MODE`: `uds_only` | `tcp_only` | `dual` | `fallback`
- UDS sockets: `/run/membrane/{primal}.sock` or `$XDG_RUNTIME_DIR/biomeos/{primal}.sock`
- `PlatformCapabilities::detect()` auto-senses transport from environment

### Standard Health Endpoint (HEALTH-01)

```json
→ {"jsonrpc":"2.0","method":"health","params":{},"id":1}
← {"jsonrpc":"2.0","result":{"status":"ok","primal":"beardog","version":"0.9.1","uptime_s":42},"id":1}
```

---

## 7. guideStone Properties

Every deployment artifact must satisfy all 5 properties:

| # | Property | Standard |
|---|----------|----------|
| P1 | **Deterministic** | Same depot + same gate profile = identical NUCLEUS state |
| P2 | **Reference-Traceable** | Every binary traces to provenance.toml (commit, rustc, timestamp, blake3) |
| P3 | **Self-Verifying** | BLAKE3 fail-closed; mismatch = abort |
| P4 | **Environment-Agnostic** | musl-static ecoBins, no runtime deps, no local builds |
| P5 | **Tolerance-Documented** | Named tolerances for staleness, handshake, convergence, startup |

---

## 8. Wave System

### What Waves Are

Waves are numbered iterations of ecosystem-wide coordination. Each wave has:
- A **blurb** (high-level guidance from overwatch)
- A **FRAGO** (Fragmentary Order — machine-readable TOML in `impulses/active/`)
- **Handoffs** (per-team deliverables in `handoffs/`)

### Wave Lifecycle

```
Blurb issued → FRAGO filed → Teams execute → Handoffs filed →
FRAGO updated → Items resolved → Archive → Next wave
```

### Active FRAGOs

Check: `ls impulses/active/` — these are the current work DAGs (rhizoCrypt analog).

---

## 9. AI Interaction Patterns

### Starting a Session

1. **Read `DEPLOYMENT_INSTANCE.toml`** for this fleet's nodes and endpoints
2. **Read this document** for universal patterns
3. **Cascade**: `git pull --ff-only forgejo main` on relevant repos
4. **Check `impulses/active/`** for current FRAGOs and work items

### Common Operations

| Phrase | Meaning |
|--------|---------|
| "Cascade from VPS and review" | Pull all relevant repos from Forgejo, check what changed |
| "Push via cascade" | Commit + push to both remotes (forgejo + origin) |
| "Check VPS state" | `membrane gate.health` — 13-primal SSH sweep |
| "Update the FRAGO" | Edit `impulses/active/*.toml` to mark items complete |

### Handoff Conventions

1. Create handoff: `handoffs/{PRIMAL}_{VERSION}_{TOPIC}_{DATE}.md`
2. Update active FRAGO if completing a wave item
3. Push both remotes
4. If blocking others: file impulse in `impulses/active/`

### Development Standards

- Zero clippy warnings (pedantic + nursery)
- Zero `unwrap()`, `expect()`, `todo!()`, `unimplemented!()`
- Zero `#[allow()]` in production code
- All files under 1000 LOC
- `#![forbid(unsafe_code)]` in application code
- Push to both remotes after every meaningful commit

### Testing

```bash
cargo clippy --workspace --all-targets  # zero warnings
cargo fmt --all -- --check              # formatted
cargo test --workspace                  # all pass
```

---

## 10. Gate Profiles

Gates are declared in `ecosystem_manifest.toml` under `[gates.*]` with topology-aware fields:

| Field | Purpose |
|-------|---------|
| `target` | Architecture triple (e.g. `x86_64-unknown-linux-musl`) |
| `mobility` | `fixed` or `mobile` |
| `bind_mode` | Default `PRIMAL_BIND_MODE` for this gate |
| `composition` | Which primals to run (`full`, `tower`, `compute`) |
| `transport` | How binaries arrive (`lan`, `wan`, `adb`, `local`) |
| `mesh_peer` | Songbird federation endpoint |
| `repos` | Which repos this gate syncs |

`gate.bootstrap` reads the profile to configure without operator memory.

---

## 11. History & Context

### Project Genesis

ecoPrimals is a sovereign computing ecosystem — 13 Rust primals that compose into NUCLEUS deployments. The goal is reproducible scientific computation without vendor lock-in: pure Rust, zero C dependencies, WGSL GPU compute, content-addressed storage, cryptographic provenance.

### Evolution Timeline

- **Waves 1-40**: Individual primal development, Python→Rust ports in springs
- **Waves 40-60**: NUCLEUS composition, deployment scripts, sovereignty graduation
- **Waves 60-80**: K-Derm diderm topology, VPS deployment, 5-gate mesh
- **Waves 80-106**: Cross-topology validation, grapheneGate 13/13, WAN deployment
- **Waves 106-108**: Deterministic deployment (6 invariants), NDK cross-compile, full rebuild
- **Wave 109**: guideStone convergence — all deployments identical and self-verifying

### Bio-Inspired Architecture

- **Primals** = organisms (autonomous, self-contained binaries)
- **Springs** = validation niches (scientific Python→Rust proofs)
- **Gardens** = membrane layers (cellMembrane = infrastructure coordination)
- **Gates** = deployment endpoints (machines running NUCLEUS)
- **K-Derm** = cell membrane topology (inner/peptidoglycan/outer)
- **NUCLEUS** = atomic composition (Tower + Node + Nest)
- **Impulses** = coordination signals (FRAGOs, handoffs, blurbs)
- **Cascade** = temporal sync flow (sovereign authority → gates → public mirror)

### Deep References

| Topic | Where |
|-------|-------|
| K-NOME methodology | `whitePaper/gen4/knome/THE_PROMPT_BANK.md` |
| Sovereignty evolution | `whitePaper/gen4/architecture/SOVEREIGNTY_EVOLUTION_NARRATIVE.md` |
| External collaboration | `whitePaper/gen5/` |
| Primal composition | `whitePaper/gen3/baseCamp/26_primal_composition_as_scientific_methodology.md` |
| Current wave standard | `TARGETED_GUIDESTONE_STANDARD.md` |
| Communication model | `ECOSYSTEM_COMMUNICATION_STANDARD.md` |

---

*This document is universal — usable by any team running a NUCLEUS deployment. For this fleet's specific nodes, IPs, and endpoints, see `DEPLOYMENT_INSTANCE.toml`.*
