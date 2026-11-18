# ecoPrimals — Standards & Expectations Index

**Purpose**: Single-document reference for what ecoPrimals expects of every primal,
spring, contributor, and session.  Read this first, read everything else second.

**Last Updated**: July 21, 2026 (Wave 150s — standards reorganized into `foundations/`, `protocols/`, `operations/`, `compositions/`)

---

## Companion Documents

- **`GLOSSARY.md`** — Every term defined (gate, primal, spring, atomic, niche, etc.)
- **`operations/GATE_SPRING_OWNERSHIP.md`** — Gate-spring routing SSOT: ownership, hardware profiles, covalent evolution path
- **`TARGETED_GUIDESTONE_STANDARD.md`** — Self-contained scientific artifact packaging (USB/ecoBin)
- **`DERIVATION_ANCHORING_STANDARD.md`** — Zero Magic Numbers: all numeric thresholds must be formally derived and runtime-enforced
- **`LITHOSPORE_USB_DEPLOYMENT.md`** — Spore taxonomy: ColdSpore → LiveSpore → lithoSpore
- **`PSEUDOSPORE_STANDARD.md`** — (canonical: `gardens/lithoSpore/specs/`) Braid-first proof artifacts
- **`compositions/PRIMAL_REGISTRY.md`** — Authoritative primal/spring version catalog
- **`protocols/ECOSYSTEM_COMMUNICATION_STANDARD.md`** — Three-layer coordination model (git/impulses/context)
- **`protocols/IMPULSE_POTENTIAL_STANDARD.md`** — Inter-gate action potentials (rootPulse/quorumSignal)
- **`protocols/CONTEXT_BRAID_STANDARD.md`** — Ephemeral developer-state weaving
- **`operations/GATE_SETUP_STANDARD.md`** — Gate setup, sync, and resync
- **`operations/THYMUS_SELF_RECOGNITION_STANDARD.md`** — Firewall self-identity, loopback bypass, autoimmune prevention
- **`operations/VPS_ENMESHMENT_STANDARD.md`** — Bringing a new VPS node into the WireGuard mesh

---

## 1. Language & Toolchain

| Expectation | Detail |
|-------------|--------|
| **Language** | Rust — 100% application code. No C, no C++, no Python in production binaries. |
| **Edition** | Rust 2024 (`edition = "2024"` in Cargo.toml) |
| **Linting** | `clippy::pedantic` + `clippy::nursery` — ZERO warnings, all-features. Non-negotiable. |
| **Unsafe** | `#![forbid(unsafe_code)]` on all crate roots unless hardware-touching (coralReef VFIO, toadStool sysmon). Justify every exception. |
| **Dependencies** | Minimize. Prefer `no_std`-capable crates. No openssl, no ring, no vendor SDKs. Pure Rust cryptography (RustCrypto suite). |
| **Documentation** | `#![warn(missing_docs)]` on library crates. Doctests count as tests. |
| **License** | AGPL-3.0-only for all primals and springs. See `SCYBORG_PROVENANCE_TRIO_GUIDANCE.md` for full licensing standard. |

## 2. Binary Architecture

Every binary follows the **evolutionary ladder**:

```
UniBin   (structure)    → One binary, multiple modes (subcommands, --help, --version)
  ↓
ecoBin   (portability)  → + Pure Rust, cross-compilation, platform-agnostic IPC
  ↓
genomeBin (deployment)  → + Auto-detection, service integration, health monitoring
```

| Standard | File | Status |
|----------|------|--------|
| UniBin | `UNIBIN_ARCHITECTURE_STANDARD.md` | Ecosystem Standard |
| ecoBin | `fossilRecord/wave150s_standards/ECOBIN_ARCHITECTURE_STANDARD.md` | Ecosystem Standard v3.0 (fossilized — stable since v3.0) |
| genomeBin | `GENOMEBIN_ARCHITECTURE_STANDARD.md` | Ecosystem Standard |

**Expectation**: Every primal is a single self-contained binary. No shared libraries,
no plugins, no dynamic loading. `cargo build --release` produces one artifact.

### Genome Pinning (`plasmidBin/`)

When a primal or spring reaches a stable release, its genomeBin is pinned to
`ecoPrimals/plasmidBin/`. This is the ecosystem-wide source of truth for
production-ready binaries. Springs and biomeOS discover primal binaries from
this directory via the `$ECOPRIMALS_PLASMID_BIN` discovery chain.

| Layer | Location | Role |
|-------|----------|------|
| genomeBin | `wateringHole/genomeBin/` | Distribution manifest, checksums, update policy |
| biomeOS plasmidBin | `phase2/biomeOS/plasmidBin/` | Local cache for spore creation |
| Root plasmidBin | `ecoPrimals/plasmidBin/` | Ecosystem-wide stable genomes |

**Standard practice**: After a successful audit or milestone, copy the release
binary to `plasmidBin/primals/{name}` (for primals) or `plasmidBin/springs/{name}`
(for springs), and update `plasmidBin/manifest.toml` + `plasmidBin/sources.toml`.

## 3. Communication (IPC + Inter-Gate Coordination)

| Standard | File | Summary |
|----------|------|---------|
| Primal IPC Protocol v3.0 | `PRIMAL_IPC_PROTOCOL.md` | JSON-RPC 2.0 + tarpc, platform-agnostic transports, runtime discovery |
| Semantic Method Naming | `protocols/SEMANTIC_METHOD_NAMING_STANDARD.md` | `domain.verb` method names (`crypto.sign`, `storage.put`) |
| Cross-Spring Data Flow | `CROSS_SPRING_DATA_FLOW_STANDARD.md` | Time series exchange format via `capability.call` |
| Ecosystem Communication | `protocols/ECOSYSTEM_COMMUNICATION_STANDARD.md` | Three-layer coordination: git (permanent) + impulses (events) + context braids (state) |
| impulsePotential | `protocols/IMPULSE_POTENTIAL_STANDARD.md` | Inter-gate action potentials mapped to Neural API Triad (rP/qS/wF) |
| Context Braids | `protocols/CONTEXT_BRAID_STANDARD.md` | Ephemeral developer-state weaving across the gate mesh |

**Expectation**: Primals never import each other's code. All coordination is via
JSON-RPC messages over IPC. Each primal owns its IPC implementation — no shared
IPC crate.

**Inter-gate coordination** uses the three-layer model:

| Layer | Pattern | Lifetime | Biological analog |
|-------|---------|----------|-------------------|
| Git commits | Linear, permanent | Forever | loamSpine ledger |
| Impulses | Event DAG, time-bounded | Archived per wave | rhizoCrypt sessions |
| Context braids | Woven strands, superseding | TTL-based auto-decay | sweetGrass braids |

**CLI surface**: `membrane impulse.post/ack/archive`, `membrane potential.sense/check`,
`membrane context.weave/sense/clear`. All registered in `capability_registry.toml`
with primal graduation path (bearDog signing, songbird relay, sweetGrass anchoring).

## 4. Security

| Standard | File | Summary |
|----------|------|---------|
| Dark Forest Beacon Genetics | `birdsong/DARK_FOREST_BEACON_GENETICS_STANDARD.md` | Two-seed lineage (nuclear + mitochondrial) |
| BearDog Technical Stack | `btsp/BEARDOG_TECHNICAL_STACK.md` | Ed25519, BLAKE3, X25519 — Pure Rust crypto foundation |
| Tower Atomic | `birdsong/SONGBIRD_TLS_TOWER_ATOMIC_INTEGRATION_GUIDE.md` | BearDog + Songbird = Pure Rust HTTPS |

**Expectation**: Auto-trust within genetic family, zero trust outside. No certificate
authorities. Encrypted payloads are unreadable to outsiders. Zero metadata leakage
(Dark Forest protocol).

## 5. GPU & Numerical Computing

| Standard | File | Summary |
|----------|------|---------|
| GPU f64 Stability | `GPU_F64_NUMERICAL_STABILITY.md` | Lessons from hotSpring Paper 44 — precision tiers |
| Numerical Stability Plan | `NUMERICAL_STABILITY_EVOLUTION_PLAN.md` | Fast AND safe math — fallback chains |
| Sovereign Compute | `SOVEREIGN_COMPUTE_EVOLUTION.md` | Pure Rust GPU stack — WGSL→native, no CUDA SDK |
| Pure Rust Stack | `fossilRecord/wave150s_standards/PURE_RUST_SOVEREIGN_STACK_GUIDANCE.md` | Cross-primal sovereign compute guidance (fossilized) |
| Cross-Spring Shaders | `CROSS_SPRING_SHADER_EVOLUTION.md` | How springs collectively evolve barraCuda |
| Spring Validation | `SPRING_VALIDATION_ASSIGNMENTS.md` | Each spring validates specific barraCuda primitives |

**Compute triangle**: barraCuda (WHAT — math/shaders) → coralReef (HOW — compile to native)
→ toadStool (WHERE — discover and dispatch hardware). Springs depend on barraCuda
directly for math.

**Expectation**: All WGSL shaders are f64-canonical. Precision dispatch per hardware
(f16/f32/f64/DF64). Springs never write local WGSL — absorb upstream from barraCuda.

## 6. Spring Standards

| Standard | File | Summary |
|----------|------|---------|
| Spring-as-Niche Standard | `SPRING_AS_NICHE_DEPLOYMENT_STANDARD.md` | Springs deploy as biomeOS niches |
| Spring-as-Niche Guide | `SPRING_NICHE_DEPLOYMENT_GUIDE.md` | How to evolve a spring into a deployable niche |
| Spring-as-Provider | `SPRING_AS_PROVIDER_PATTERN.md` | biomeOS capability registration pattern |
| Provenance Trio Integration | `SPRING_PROVENANCE_TRIO_INTEGRATION_PATTERN.md` | rhizoCrypt + loamSpine + sweetGrass integration |
| Spring Evolution Issues | `SPRING_EVOLUTION_ISSUES.md` | Active issues discovered by springs |

**Expectation**: Every spring has its own git repo, its own `Cargo.toml`, its own
`specs/PAPER_REVIEW_QUEUE.md`. Springs reproduce published papers at paper parity.
Every experiment gets a number, every check gets counted. No hand-waving.

## 7. Primal Coordination

| Document | File | Summary |
|----------|------|---------|
| Primal Registry | `compositions/PRIMAL_REGISTRY.md` | Authoritative catalog of every primal + primitives |
| Inter-Primal Interactions | `INTER_PRIMAL_INTERACTIONS.md` | What works today, what's wired, what's next |
| Lysogeny Protocol | `LYSOGENY_PROTOCOL.md` | Area denial through open prior art (AGPL-3.0) |
| scyBorg Licensing | `SCYBORG_PROVENANCE_TRIO_GUIDANCE.md` | AGPL + ORC + CC-BY-SA ecosystem licensing |
| Novel Ferment Transcript | `NOVEL_FERMENT_TRANSCRIPT_GUIDANCE.md` | NFT architecture (memory-bound digital objects) |
| Upstream Contributions | `UPSTREAM_CONTRIBUTIONS.md` | Standalone crates for crates.io |

## 8. Leverage Guides (Per-Primal)

Each primal has a leverage guide describing standalone, trio, and ecosystem compositions:

| Guide | Primal |
|-------|--------|
| `BARRACUDA_LEVERAGE_GUIDE.md` | barraCuda |
| `BIOMEOS_LEVERAGE_GUIDE.md` | biomeOS |
| `CORALREEF_LEVERAGE_GUIDE.md` | coralReef |
| `LOAMSPINE_LEVERAGE_GUIDE.md` | loamSpine |
| `RHIZOCRYPT_LEVERAGE_GUIDE.md` | rhizoCrypt |
| `SQUIRREL_LEVERAGE_GUIDE.md` | Squirrel |
| `SWEETGRASS_LEVERAGE_GUIDE.md` | sweetGrass |
| `TOADSTOOL_LEVERAGE_GUIDE.md` | toadStool |
| `petaltongue/` | petalTongue (integration docs) |

## 9. Handoffs

Session handoffs live in `handoffs/`. They are the working memory between sessions —
what was done, what's next, what broke, what was discovered.

- **Active**: `handoffs/*.md` — current work items (last 48 hours)
- **Fossil record**: `handoffs/archive/` — completed work, preserved for provenance

Handoffs are archived after ~48 hours or when superseded. They are never deleted.
The archive is the project's geological record.

## 10. Testing Expectations

| What | Expectation |
|------|-------------|
| **Unit tests** | Every module has tests. `cargo test` passes with zero failures. |
| **Forge tests** | Integration/forge tests for cross-module behavior. |
| **Python cross-validation** | For scientific springs: Python reference implementations validate Rust output at paper parity. |
| **Named tolerances** | Every numerical comparison uses a named tolerance constant (e.g., `PLANCK_TEMPERATURE_REL_TOL`), not magic numbers. GuideStone artifacts: full derivation anchoring per `DERIVATION_ANCHORING_STANDARD.md`. |
| **Clippy** | `clippy::pedantic` + `clippy::nursery`, zero warnings, all features enabled. |
| **CI** | `cargo test --all-features`, `cargo clippy --all-features -- -D warnings`. |
| **Coverage** | Track and increase. Minimum varies by maturity — new primals target 80%+. |

## 11. Documentation Expectations

| What | Where |
|------|-------|
| **Root README** | Every repo has one. States what it is, what it does, current version. |
| **specs/** | Paper review queues, experiment designs, scientific specs. |
| **CHANGELOG** or session notes | What changed, when, why. |
| **Handoffs** | Session continuity lives in wateringHole `handoffs/`. |
| **baseCamp** | Cross-spring papers live in `whitePaper/gen3/baseCamp/`. |
| **attsi/** | Faculty contact packages and outreach plans. |

## 12. Code Style

| Rule | Detail |
|------|--------|
| No TODO/FIXME/HACK in committed code | Track in handoffs or issues instead. |
| No files >1000 lines | Split into modules. |
| No commented-out code | Delete it; git remembers. |
| Semantic naming | Functions say what they do. Variables say what they hold. |
| Error handling | `Result<T, E>` everywhere. No `.unwrap()` in library code. `thiserror` for typed errors. |
| Feature gates | Use Cargo features to gate optional functionality. |

---

## 13. External Claims & Maturity Labeling

| Standard | File | Status |
|----------|------|--------|
| External Claim Convergence | `foundations/EXTERNAL_CLAIM_CONVERGENCE_STANDARD.md` | Ecosystem Standard (Wave 150x) |

**Expectation**: Every public-facing README includes an external maturity label
(`experimental`, `research-ready`, `deployment-ready`, `production-candidate`,
`externally-validated`) and a metrics measurement date. Internal evolutionary
grades (stadial, wave, A++) do not appear in the first 20 lines of public READMEs.
All absolute claims (`zero`, `all`, `every`, `no`) state their scope in the same
sentence. See the standard for full details.

---

## Quick Reference: "Is my work ready?"

Before pushing, verify:

- [ ] `cargo test --all-features` — zero failures
- [ ] `cargo clippy --all-features -- -D warnings` — zero warnings
- [ ] `cargo doc --all-features --no-deps` — zero doc warnings
- [ ] No TODO/FIXME/HACK in committed code
- [ ] No files >1000 lines
- [ ] Named tolerances for all numerical comparisons
- [ ] Experiment checks counted and reported
- [ ] Handoff written if session work is incomplete
