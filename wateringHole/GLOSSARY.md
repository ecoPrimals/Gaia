# ecoPrimals Glossary

**Purpose**: Definitive terminology for the ecoPrimals ecosystem. If a term is used
in any document, handoff, or conversation, its meaning is defined here.

**Last Updated**: July 27, 2026 (Wave 155b — genomeBin convergence, autonomous enrollment shipped, 5 Tier 1 targets, Tower Atomic = OS abstraction, gate enmeshment glacial)

---

## The Three Organizations

The ecosystem is distributed across three organizations on both GitHub (outer
membrane) and Forgejo (inner membrane, `git.primals.eco`):

| Organization | Role | What Lives Here |
|-------------|------|----------------|
| **[ecoPrimals](https://github.com/ecoPrimals)** | Infrastructure primals | barraCuda, toadStool, coralReef, biomeOS, BearDog, NestGate, Songbird, sweetGrass, rhizoCrypt, loamSpine, petalTongue, Squirrel, skunkBat, bingoCube, sourDough. Also infrastructure repos: sporePrint, wateringHole, whitePaper, plasmidBin, benchScale. |
| **[syntheticChemistry](https://github.com/syntheticChemistry)** | Science validation springs | wetSpring, hotSpring, airSpring, neuralSpring, groundSpring, healthSpring, ludoSpring, primalSpring. Springs validate that primals produce correct science. |
| **[sporeGarden](https://github.com/sporeGarden)** | User-facing products (gen4) | projectNUCLEUS (sovereignty layer), projectFOUNDATION (knowledge layer), lithoSpore (verification chassis), esotericWebb (UI/agentic), cellMembrane (private ops — VPS deployment), helixVision (genomics pipeline), initioChem (computational chemistry), blueFish (analytical chemistry ETL). |

**Git hosts**: Forgejo on VPS (`git.primals.eco`) is the sovereign periplasmic
layer (golgiBody Phase A). GitHub is the trailing outer membrane mirror. Gates
push to Forgejo via SSH; GitHub receives post-push mirrors via the K-Derm
diderm relay chain. WaterFall sync (`membrane temporal.cascade`) pulls from
the periplasm. See `fossilRecord/wave150s_standards/WATERFALL_PATTERN.md` for the full sync model and
`operations/REPO_MEMBRANE_BOUNDARY.md` for per-repo classification: inner-only, trailing
mirror, or outer-only.

**Why three orgs?** Primals build capabilities. Springs validate those capabilities
against published science. Products deliver validated capabilities to users.
The organizations mirror this separation: infrastructure, validation, delivery.

When linking to repos, always use the correct organization:
- Springs: `github.com/syntheticChemistry/<spring>`
- Primals: `github.com/ecoPrimals/<primal>`
- Products: `github.com/sporeGarden/<product>`
- Site: `primals.eco`

See `LINK_INTEGRITY_STANDARD.md` for the full URL convention standard.

---

## The Physical Layer

### Gate

A **gate** is a physical computer — a deployment target that runs the ecoPrimals
stack. Gates are named using camelCase (`firstLast`) like all ecoPrimals entities.
The project operates across multiple houses and platforms:

| Gate | Platform | Composition | Role | Status |
|------|----------|-------------|------|--------|
| **golgiBody** | Linux (VPS) | thin-relay | Sole depot, enrollment, Forgejo, Drawbridge | ONLINE |
| **sporeGate** | Linux | full | Build authority, cascade hub, HPC | ONLINE |
| **eastGate** | Linux | full | Code hub, overwatch | ONLINE |
| **ironGate** | Linux | full | GPU compute, 4x HDD enclave, JupyterHub | ONLINE |
| **flockGate** | Linux | full | Nest Atomic validation | ONLINE |
| **northGate** | Windows | full | RTX 5090, gaming/GPU compute | ONLINE |
| **grapheneGate** | Android | tower | Beacon seed, mobile Tower | ONLINE |
| **strandGate** | Linux | compute (7) | Dual EPYC, RTX 3090, bioinformatics | HW READY |
| **westGate** | Linux | nest (7) | 5x14TB HDD (70TB ZFS cold pool) | HW READY |
| **blueGate** | Windows | tower (3) | Distributed builder, media/gaming | HW READY |
| **swiftGate** | Windows | full (13) | Hobby/consumer, house2 | HW READY |
| **southGate** | Linux | full (13) | House2 sovereign site | HW READY |

Gates run any operating system — Linux, Windows, Android, macOS. Tower Atomic
(bearDog + songBird + skunkBat) is the OS abstraction layer, handling IPC
transport (UDS vs named pipes vs TCP), service management, and platform
detection intrinsically. Gates self-enroll via `mesh.gate_enroll` — declaring
name, composition, and physical proof. No manifest pre-definition needed.

When Plasmodium is active, multiple gates bond into a collective. Any gate can
query the collective; workloads route to the best gate by capability match.

### Operational Substrate

The software environment a gate provides to the ecoPrimals stack. Platform-
specific details are handled by Tower Atomic — primals auto-detect via
`Platform::detect()` at compile time.

| Layer | Linux | Windows | Android |
|-------|-------|---------|---------|
| **IPC** | UDS / abstract sockets | Named pipes / TCP | Abstract sockets / TCP |
| **Shell** | bash | PowerShell | adb / Termux |
| **Toolchain** | Rust stable, cargo, clippy, rustfmt | Same (via rustup) | Cross-compiled from Linux |
| **Service mgmt** | systemd | Windows Service (planned) | Manual / init |
| **GPU** | Vulkan (wgpu) | Vulkan / DirectX (wgpu) | Vulkan (wgpu) |

No Docker. No Kubernetes. No cloud VMs. The gate IS the infrastructure.

---

## The Software Layer

### Primal

A **primal** is a self-contained Rust binary that provides a collection of
**primitives** — small, focused capabilities solving one domain well. Primals
are autonomous: each knows only itself. Complexity is solved through
**coordination**, not by making a primal larger.

Key properties:
- Self-knowledge only (never imports another primal's code)
- Capability-based discovery at runtime
- Zero compile-time coupling between primals
- Pure Rust (no C dependencies in application code)
- UniBin architecture (one binary, multiple modes via subcommands)

Examples: bearDog (cryptography), songBird (networking), toadStool (hardware),
barraCuda (math), coralReef (shader compilation), Squirrel (AI coordination).

**Naming convention**: Canonical capitalization is camelCase with firstLast —
`bearDog`, `songBird`, `toadStool`, `sweetGrass`, `wetSpring`, `hotSpring`.
In prose, initial caps are common (BearDog, ToadStool) and acceptable.
The camelCase structure is intentional — even names like songBird and toadStool
leverage the semantic naming (song+Bird, toad+Stool) for discoverability.

### Primitive

A **primitive** is the atomic unit of capability a primal provides. BearDog's
primitives include Ed25519 signing, BLAKE3 hashing, X25519 key exchange.
barraCuda's primitives include f64 WGSL shaders for dot products, FFT,
eigensolve, and statistical functions. A primitive is the smallest thing a
primal can do.

### Spring

A **spring** is a validation and evolution environment — a Rust workspace that
composes primals and validates that their composition solves real scientific or
engineering problems. Springs are not primals; they consume primals via IPC and
prove correctness through numbered experiments. Springs are named after natural
water sources: wetSpring, hotSpring, airSpring, neuralSpring, groundSpring,
healthSpring, ludoSpring.

Springs evolve through a defined pipeline:

```
Python baseline → Rust validation → GPU acceleration → sovereign pipeline
→ primal composition → ecosystem co-evolution
```

Each spring has:
- Its own git repository
- A `specs/PAPER_REVIEW_QUEUE.md` tracking papers to reproduce
- Numbered experiments with counted checks (pass/fail/skip exit codes)
- Deploy graphs (TOML) for the primal compositions it validates
- A faculty anchor (a professor whose publications drive the science)
- Gap discovery and wateringHole handoff authorship

Springs are the gen3 layer (see `foundations/PRIMAL_SPRING_GARDEN_TAXONOMY.md`). They
were initially standalone binaries validating science; they now compose FROM
primals and validate that the composition works for their domain.

### Garden

A **garden** is a user-facing product that composes primals into tools people
actually use. Gardens follow the BYOB model (Bring Your Own Binaries),
consuming pre-built primal binaries from plasmidBin via IPC. Gardens are the
gen4 layer — they take the capabilities that primals provide and springs
validate, and turn them into products.

Gardens live in the `gardens/` directory. They own user experience, graceful
degradation when optional primals are absent, and product-level deploy graphs.

Examples: esotericWebb (CRPG engine), blueFish (PFAS analytical chemistry),
helixVision (genomics platform), initioChem (CompChem FEL explorer).

See `foundations/PRIMAL_SPRING_GARDEN_TAXONOMY.md` for the full taxonomy and co-evolution
contract between primals, springs, and gardens.

### Tool

A **tool** (gen2.5) is a standalone Rust crate or binary consumed by primals, springs,
or other ecosystem components. Tools solve bounded problem domains without the full
IPC/discovery/health surface that primals carry — they are not long-running daemons
and do not register capabilities with biomeOS. They are not end-user products (that's
a garden).

Tools live in `primals/` (when consumed as crate deps by primals), `infra/` (when
infrastructure-only), or `sort-after/` (pending canonical location).

Examples: bingoCube (crypto commitment), benchScale (lab substrate), agentReagents
(VM image builder), rustChip (NPU characterization), sourDough (scaffolding).

See `foundations/PRIMAL_SPRING_GARDEN_TAXONOMY.md` § Tools (gen2.5) for the full definition,
applicable compliance tiers, and ownership boundaries.

### Atomics

**Atomics** are the core primal interaction patterns — the named compositions
that larger niches are built on. They are not separate software; they are
what happens when specific primals coordinate.

| Atomic | Composition | What Emerges |
|--------|-------------|-------------|
| **Tower Atomic** | BearDog + Songbird + skunkBat | Trust boundary (crypto + discovery + defense) |
| **Node Atomic** | Tower + toadStool + barraCuda | Hardware-aware compute (+ GPU math) |
| **Nest Atomic** | Tower + NestGate | Secure content-addressed storage |
| **Full NUCLEUS** | All foundation primals + Squirrel | Complete AI-coordinated ecosystem |

Atomics are the building blocks. You don't deploy "Tower Atomic" — you deploy
a niche that uses Tower Atomic's capabilities because it needs crypto + networking.

### Niche

A **niche** is a biomeOS BYOB (**Build Your Own Biome**) deployment — a composed
set of primals, chimeras, and interactions deployed as a unit via a deploy graph.
A niche is what you actually run.

Examples:
- A field genomics niche: wetSpring + toadStool (NPU) + NestGate + BearDog
- A game science niche: ludoSpring + petalTongue + toadStool + barraCuda
- A precision health niche: healthSpring + barraCuda + petalTongue + NestGate

A niche is defined by:
- A **deploy graph** (TOML DAG) — germination order and capability wiring
- A **niche YAML** — organisms, interactions, customization options
- **Capability domains** — semantic namespaces (`ecology.*`, `precision.*`)

### Deploy Graph

A **deploy graph** is a TOML-encoded directed acyclic graph (DAG) that tells
biomeOS how to start and wire a niche. It specifies:
- Which primals to germinate (start)
- In what order (dependency edges)
- What capabilities to wire together
- What resources to allocate

biomeOS reads the graph, germinates the primals, waits for their sockets, and
wires their capabilities together. The graph is the deployment contract.

### Chimera

A **chimera** is a fused multi-primal organism with a unified API. Unlike a
niche (which coordinates separate processes), a chimera is a single binary that
combines capabilities from multiple primal lineages.

Example: `gaming-mesh` = Songbird networking + ludoSpring game logic, fused
into a single binary with one API surface.

Chimeras are rare and intentional — most composition should happen via IPC
coordination, not fusion.

### Germination

**Germination** is the process of starting a primal and waiting for it to become
ready. A primal germinates when its `server` subcommand starts, its IPC socket
appears, and it responds to `health.check`. biomeOS monitors germination via
deploy graphs.

Analogy: a seed (binary) germinates (starts) in a niche (deployment) on a
gate (computer).

---

## The Coordination Layer

### biomeOS

The **ecosystem substrate** — the orchestration layer that discovers primals,
routes capabilities, composes niches, and manages the lifecycle of everything
running on a gate. biomeOS does not compute science; it coordinates the primals
that do.

Key subsystems:
- **Neural API**: Semantic capability routing (170+ translations, 16 domains)
- **NUCLEUS composition**: Layered atomic patterns
- **Dark Forest coordination**: Zero-metadata discovery
- **Provenance trio wiring**: rhizoCrypt + loamSpine + sweetGrass orchestration

### NUCLEUS

The **full primal composition** orchestrated by biomeOS. NUCLEUS is not a
binary — it is the emergent state when all foundation primals are running and
coordinated on a gate.

```
Tower Atomic (BearDog + Songbird + skunkBat)
  + Node Atomic (+ toadStool + barraCuda + coralReef)
  + Nest Atomic (+ NestGate)
  + Squirrel (AI)
  = Full NUCLEUS
```

### Plasmodium

The **over-NUCLEUS collective** formed when 2+ gates bond. Named after the
slime mold *Physarum polycephalum* — no central brain, collective intelligence,
pulsing coordination. Gates join and leave dynamically.

When Eastgate and biomeGate bond, their NUCLEUS instances merge into a
Plasmodium. Workloads route to the gate with the best capability match.

### Provenance Trio

The three primals that together provide the project's memory and attribution:

| Primal | Role | Temporal Domain |
|--------|------|-----------------|
| **rhizoCrypt** | Ephemeral memory | Present — working DAG, fast, lock-free |
| **loamSpine** | Permanent memory | Past — immutable linear history, Loam Certificates |
| **sweetGrass** | Attribution | Always — semantic provenance, W3C PROV-O braids |

When composed by biomeOS, these three create **RootPulse** — distributed
version control that emerges from primal coordination.

### RootPulse

**Distributed version control** that emerges from the provenance trio's
coordination. RootPulse is not a VCS binary — it is what primals DO together:
rhizoCrypt provides the workspace, loamSpine provides the history, sweetGrass
provides the attribution, BearDog signs it, NestGate stores it, Songbird
syncs it. biomeOS orchestrates the whole thing via Neural API.

### soundStage

The **transparent observation layer** for hardware trust ceremonies. soundStage
makes ephemeral key generation visible — you watch the entropy flowing from each
hardware source, see the mixing happen, observe the derivation, and validate the
output. If you can't see it working, you're just trusting it's secure.

soundStage is not a primal. It is an ecoPrimals **concept** — a capability that
primals compose to provide live ceremony observability. The concept applies
anywhere hardware trust operations happen (key generation, certificate minting,
entropy ceremonies).

Core abstractions:

| Concept | Role | Analogy |
|---------|------|---------|
| **Channel** | A single observable entropy source (SoloKey, StrongBox, audio, getrandom) | A microphone in a recording studio |
| **Mix bus** | Where channels converge — the mixing operation and its output | The mixing board |
| **Monitor** | The derived key material's fingerprint (never the raw key) | Studio monitors (listen but don't broadcast) |
| **Session** | A complete ceremony recording — all channels, mix, output timestamped | A session tape |
| **Comparator** | Diffs sessions to prove independence or detect degenerate entropy | A/B comparison |

Key properties:
- **Multi-anchor**: Each hardware source is a separate channel (SoloKey, Pixel
  StrongBox, audio mic, OS entropy)
- **Multi-user**: Each user gets independent sessions — comparator verifies
  independence across users
- **Quality gates**: Require multi-source (≥2 anchors) and entropy floor
  (>4.0 bits/byte Shannon) to pass
- **Fingerprints only**: The monitor observes key derivation through BLAKE3
  fingerprints — raw key material never leaves the ceremony
- **Transparency over trust**: The entire point is to make the black box visible.
  If a hardware source starts producing degenerate entropy, you see it immediately.

soundStage is to key generation what darkforest is to network security: the tool
that makes the invisible visible. darkforest reveals what probes the network.
soundStage reveals what flows through the ceremony.

See `primalSpring/ecoPrimal/src/soundstage/` for the reference implementation.

### Genetic Enrollment

The **two-layer trust model** for gate-to-gate authentication:

| Layer | What It Proves | Mechanism |
|-------|---------------|-----------|
| **Mito gate** | "I belong to this ecosystem" | Mitochondrial beacon seed — shared family secret |
| **Nuclear lineage distance** | "I am N hops from the root" | Derivation chain from the nuclear seed → trust tier |

Genetic enrollment replaces static shared secrets with a biological trust
model: gates that share closer genetic lineage (shorter derivation distance)
receive higher trust tiers. A gate proves enrollment by demonstrating
knowledge of both its mito beacon membership AND its nuclear derivation chain.

bearDog manages the genetic crypto (`genetic.*` capabilities). songBird
consumes it for `enrollment.verify` during mesh join. The trust tiers feed
into `capability.call` routing priority — genetically closer gates are
preferred for capability dispatch.

### Tower Shadow

**Shadow deployment mode** for Tower Atomic — running the Tower transport
stack alongside WireGuard, mirroring traffic to collect comparative metrics
without affecting production routing.

Key commands:
- `membrane tower.shadow --enable` — activate shadow mode
- `songbird benchmark --mode tower-atomic --peer <addr>` — measure Tower latency/throughput
- `songbird benchmark --mode wireguard --peer <addr>` — WireGuard baseline

Shadow deploy collects continuous metrics (latency, throughput, jitter) via
a systemd timer (`tower-shadow.timer`) running every 60 minutes. Results are
JSON files stored in `benchScale/tower_shadow/`. This data drives the Tower
EXCEEDS claims (353x LAN, 1.7x WAN sustained).

Shadow mode is the validation phase before Phase 3 cutover (Tower replaces WG).

### LAN Mesh Routing

The **LAN-first routing preference** for same-switch peers. When two gates
are on the same physical switch (e.g., CRS310 backbone), `mesh.find_path`
should return an `EndpointType::Local` path (sub-millisecond) rather than
routing through the WG overlay (100–200ms RTT through VPS relay).

`primalSpring` implements this via `MeshEntry::preferred_address()` which
checks `lan_addr` before falling back to the WG overlay address.

**P0 gap (Wave 150x)**: songBird's `mesh.find_path` does not yet honor
`EndpointType::Local` — it returns the WG overlay for all peers regardless
of LAN availability. This imposes a 353x–1200x latency penalty for
`capability.call` dispatch between co-located gates.

### CallerContext

A **per-connection identity object** wired into songBird's IPC method gate.
When a primal connects via UDS (Unix Domain Socket), the connection extracts
`SO_PEERCRED` (Linux peer credentials: PID, UID, GID) and attaches a
`CallerContext` to every subsequent method call on that connection.

The method gate uses `CallerContext` to:
- Verify the caller's PID maps to a known primal process
- Enforce per-method access control (some methods are local-only)
- Reject unauthenticated remote callers attempting local-only operations

CallerContext + UDS hardening (socket permissions, symlink rejection, TOCTOU
protection) together resolved 7 pen-test findings in Wave 150x.

### Chimera Phase 0

The **first step** in chimera evolution: extracting shared library code from
primals that currently communicate exclusively via IPC. Phase 0 targets
bearDog's crypto primitives — the hot-path crypto operations that every
primal uses frequently enough to justify in-process linking over IPC overhead.

Chimera Phase 0 prerequisites:
1. Composition validation (bearDog UDS crypto works for all cold-path) ✓
2. Hot-path identification (`CRYPTO_COMPOSITION.md` classifies 19 seams)
3. Library extraction (bearDog → `beardog-core` crate)
4. Feature-gate migration (primals opt-in to embedded crypto)

Phase 0 is unblocked once composition validation is complete (songBird P1
crypto delegation finishing).

See `primalSpring/ecoPrimal/src/soundstage/` for the reference implementation.

---

## The Compute Triangle

Three primals form the sovereign compute stack:

```
barraCuda (WHAT to compute — f64 WGSL shaders, math primitives)
    ↓
coralReef (HOW to compile — WGSL → native GPU binary, naga IR)
    ↓
toadStool (WHERE to run — hardware discovery, dispatch, orchestration)
```

### barraCuda

**Pure math.** 712+ WGSL f64 shaders. Writes the math. Springs depend on
barraCuda directly for math without pulling toadStool's runtime or coralReef's
compiler. Budded from toadStool at Session 93.

### coralReef

**Sovereign shader compiler.** Compiles WGSL to native GPU binaries (SM70-SM89
SASS) without NVIDIA's NVVM or any vendor SDK. Includes VFIO dispatch with PFIFO
channels. The "compiler that frees the math from the vendor."

### toadStool

**Hardware infrastructure.** Discovers CPUs, GPUs, NPUs. Probes capabilities.
Dispatches workloads. Manages the Node Atomic deployment. 20,843 tests, 96+
JSON-RPC methods.

---

## The Science Layer

### metalForge

Where a spring is working on **hardware concepts** — GPU vs CPU routing, GPU to
NPU via PCIe, hardware dispatch architecture. metalForge is the exploratory
substrate where primals figure out how to talk to novel hardware. The brain
architecture in hotSpring evolved through metalForge before stabilizing.

metalForge is not a primal — it is an evolution context. When a spring needs to
push work across compute substrates (CPU → GPU, GPU → NPU) and the path doesn't
exist yet, that work happens in metalForge.

### baseCamp

The transition from **paper validation to real exploration**. baseCamp lives in
`whitePaper/gen3/baseCamp/` and is where springs move beyond reproducing a single
paper to mixing larger datasets and systems. QS-Anderson evolved this way — the
paper parity work validated the pieces, and baseCamp is where those pieces
combine into something new.

Currently 18 papers (01-18), spanning Anderson-QS, LTEE, bioag, sentinels,
symbiotic ecology, no-till, WDM, NPU edge, field genomics, dynamical QCD,
nautilus reservoir computing, immuno-Anderson, sovereign health, precision brain,
anaerobic-aerobic QS, game design as science, RPGPT.

### Paper Parity

The standard of evidence for spring experiments: the Rust implementation must
produce results that match the published paper's results within named tolerances.
Not "close enough" — paper parity means you could substitute the spring's output
for the paper's figures and a reviewer would accept them.

### Experiment

A numbered unit of scientific validation within a spring. Each experiment has:
- A number (e.g., Exp356)
- A defined objective
- Counted checks (e.g., "18/18 PASS")
- A connection to a baseCamp paper or paper queue entry

### Faculty Anchor

A professor whose published work drives a spring's science. Each spring has at
least one faculty anchor. The project reproduces their papers, then extends the
science. Faculty anchors are documented in `whitePaper/attsi/`.

| Spring | Faculty Anchor(s) |
|--------|-------------------|
| wetSpring | Faculty anchor (quorum sensing), faculty anchor (agriculture) |
| hotSpring | Faculty anchor (plasma physics), faculty anchor (lattice QCD), faculty anchor (gradient flow) |
| groundSpring | Faculty anchor (spectral theory) |
| healthSpring | Faculty anchor (pharmacology) |
| neuralSpring | (cross-domain — reproduces from all anchors) |
| airSpring | Faculty anchor (precision agriculture) |
| ludoSpring | Published authors (Flow theory, motor control, procedural generation) |

### attsi

The **faculty outreach program** (`whitePaper/attsi/`). Contains contact
packages, review materials, and outreach strategy for each faculty anchor.
Faculty identities are maintained in the non-anonymous whitePaper layer; anonymized
contacts use hashed identifiers.

---

## The Evolution Vocabulary

### Evolution

In ecoPrimals, **evolution** means directed improvement through validated steps.
A spring evolves from Python baselines to Rust validation to GPU acceleration.
A primal evolves by absorbing primitives upstream (into barraCuda) and
delegating downstream (to toadStool). Evolution is always validated — every
step passes tests.

### Absorption

When a spring's local implementation of a primitive is replaced by a call to
barraCuda's canonical version. The spring "absorbs upstream" — it stops owning
the math and starts consuming the shared version. This is how springs
collectively evolve barraCuda.

### Delegation

The inverse of absorption: when a primal delegates work to another primal.
A spring delegates hardware dispatch to toadStool, math to barraCuda, shader
compilation to coralReef. Delegation is always via IPC, never via code import.

### Deep Debt

Technical debt identified during evolution sessions. Tracked in handoffs, not
in TODO comments in code. Deep debt is actively reduced — the archive of
handoffs is full of "DEEP_DEBT" sessions where primals were systematically
improved.

### Handoff

A **session handoff** document in `wateringHole/handoffs/`. Records what was
done, what's next, what broke, what was discovered. Handoffs are the working
memory between sessions. After resolution they are archived to the
fossilRecord repository.

### Fossil Record

The canonical archive repository at `github.com/ecoPrimals/fossilRecord`.
Never deleted, only accumulated. The geological record of every evolution
session the project has run. 3,831+ documents spanning February 4, 2026 –
present, consolidated from 10 ecosystem sources with provenance-preserving
subdirectory structure.

### Fossilization

The act of moving resolved content — handoffs, showcase directories,
superseded standards, local wateringHole trees — from active repos to the
fossilRecord. Fossilized content is replaced by a README stub pointing to
the canonical archive location. The content is never deleted; it moves from
working memory to geological record.

Fossilization became a first-class ecosystem operation during Wave 49
(showcase fossilization across 8 primals) and Wave 51 (primalSpring
wateringHole fossilization). The pattern: **copy to fossilRecord → replace
with pointer stub → push both repos**.

### Wave

A **wave** is a named coordination pulse across the ecosystem — a point
where multiple primals and springs evolve together in response to a shared
signal. Waves are numbered sequentially (Wave 47, 48, 49, 50, 51…) and
tracked in `fossilRecord/wave150s_standards/GLACIAL_SHIFT_READINESS.md`.

A wave is not a release. It is a *synchronization event* — a moment when
the ecosystem converges on a shared standard, absorbs upstream changes,
and confirms alignment. Springs "respond" to waves by pulling the latest
patterns and confirming compliance. Waves are how the ecosystem breathes.

### Stadial / Interstadial

Borrowed from glacial geology. A **stadial** is a period of hard convergence
— all components forced to a common fitness threshold. An **interstadial** is
a warming period of diversification under constraint. The ecosystem cycles
between these phases: stadials cull non-conforming patterns, interstadials
allow exploration and specialization, extinction events select what survives,
and the next stadial raises the bar.

The current position (May 2026) is interstadial exit → stadial entry. The
glacial shift criteria define the gate.

See `whitePaper/gen4/architecture/STADIAL_INTERSTADIAL_PATTERN.md`.

---

## The Deployment Layer

### plasmidBin

The **binary distribution repository** at `github.com/ecoPrimals/plasmidBin`.
Contains pre-built musl-static NUCLEUS primal binaries for x86_64 and aarch64.
Every primal binary deployed in production comes from plasmidBin — never from
`cargo build` on the gate, never from `target/release/`, never from PATH
lookup.

plasmidBin provides:
- `manifest.toml` — canonical primal registry (versions, methods, checksums)
- `checksums.toml` — BLAKE3 hashes per binary per architecture
- `sources.toml` — mapping from primal IDs to source repos and build config
- `plasmidbin` CLI — Rust binary for `validate`, `harvest`, `fetch`, `deploy`,
  `start`, `stop`, `doctor`, `launch`
- GitHub Actions CI — automated harvest from upstream releases, checksum
  generation, smoke testing

The name follows the biological metaphor: a plasmid is a small circular DNA
molecule that carries genes between bacteria independently of the chromosome.
plasmidBin carries primal binaries between gates independently of the source
repos.

### postPrimordial

The **deployment regime** where all NUCLEUS primal binaries come exclusively
from plasmidBin. No `target/release/` paths, no `cargo install`, no `which`
PATH lookups, no `~/.local/bin` or `~/.cargo/bin` fallbacks in any launcher,
deploy script, systemd unit, or composition tool.

postPrimordial is the ecosystem after its primordial phase — the period when
primals were built locally from source on each gate. The primordial phase
was necessary (you can't distribute binaries that don't exist yet). The
post-primordial phase recognizes that local builds are fragile, non-reproducible,
and create deployment drift between gates.

The transition happened at Wave 49 (post-primordial deployment enforced
across all launchers). Wave 51 completed the Rust elevation of plasmidBin
itself — the distribution tool is now as sovereign as the binaries it
distributes.

**Compliance rule**: any script, service, or doc that resolves a NUCLEUS
primal binary through anything other than plasmidBin is a primordial
anti-pattern and must be fixed. Spring-owned validation binaries (e.g.,
`target/release/healthspring_unibin`) built from the spring's own source
are exempt — they are not NUCLEUS primals.

### goldenCage

The set of external cloud services that the ecosystem uses to bootstrap
sovereignty — services that are individually excellent, collectively
indispensable, and structurally a single point of failure until replaced.

The golden cage bars: GitHub (code, CI, releases), Cursor (AI development),
Cloudflare (DNS, TLS proxy, tunnel), DigitalOcean (VPS), crates.io
(dependency resolution), Let's Encrypt (TLS credentials), Python/GROMACS
(science baseline validation).

The **chrysalis thesis**: the cage is not the enemy — it is the bootstrap
material from which sovereignty is built. Each sovereign replacement
(BearDog for Cloudflare TLS, Songbird for cloudflared tunnel, NestGate for
GitHub Pages, Forgejo for GitHub repos, self-hosted runners for GitHub
Actions) was built using the cage's resources. The cage becomes the outer
membrane when the inner membrane is self-sufficient.

See `whitePaper/gen4/architecture/THE_GOLDEN_CAGE.md`.

---

## The Network Boundary Layer

### Gatehouse

The **bond escalation broker** — the single external surface of a gate exposed
to the internet. The gatehouse accepts all incoming traffic as **weak** interactions
(zero trust, passive diffusion) and validates/promotes them to stronger bond types
as authentication is established.

bearDog owns the gatehouse — exactly two ports (`:443` TLS, `:80` ACME redirect). No
other primal binds externally. skunkBat provides threat intelligence. The gatehouse
manages **TLS credentials** (drawbridge transport, not Loam Certificates) and is where
the K-Derm extracellular → outer membrane crossing happens.

Bond escalation through the gatehouse:

```
Weak (extracellular) → bearDog TLS termination
  → Ionic (outer membrane → periplasm) → BTSP scoped token
    → Metallic (periplasm → plasma) → Mito-Beacon membership
      → Covalent (plasma → cytoplasm) → nuclear session (fresh spawn)
```

Only one gate runs gatehouse mode per deployment (sporeGate for the current mesh).
All other gates are purely darkforest — zero exposed ports.

See `operations/GATEHOUSE_DARKFOREST_STANDARD.md`, `foundations/BONDING_MODEL_STANDARD.md`.

### Darkforest

The **invisible interior** of the mesh. No port scanning, no direct access, no
known entry points from outside. All inter-primal communication uses UDS, abstract
sockets, or songBird mesh relay. Discovery is via `mesh.peers` and `capability.call`.

The darkforest boundary is the enforcement mechanism that prevents sovereignty
leakage — nothing inside leaks out without crossing the drawbridge, and nothing
outside enters without passing through the gatehouse's bond escalation. The Dark
Forest principle means everything starts untrusted. Trust is earned through
progressively stronger authentication at each K-Derm layer crossing.

See `operations/GATEHOUSE_DARKFOREST_STANDARD.md`, `foundations/DARK_FOREST_GLACIAL_GATE_STANDARD.md`.

### Drawbridge

The **single crossing point** between the gatehouse (external) and the darkforest
(internal). Implemented as songBird's HTTP proxy listener, the drawbridge translates
external HTTP semantics into capability-routed mesh semantics.

The drawbridge sits at the outer membrane → periplasm crossing. It is where weak
bonds begin escalating — path prefixes map to capability names, and
`capability.call` routes requests to backends in the darkforest.

As of Wave 133d, the drawbridge auto-registers its routed capabilities into the
local IPC registry and announces them to mesh peers via `mesh.capabilities_announce`.
This means any gate with drawbridge routes automatically advertises its capabilities
to the mesh — no manual `ipc.register` or sidecar scripts needed.

```
SONGBIRD_DRAWBRIDGE_ROUTES=/hub=jupyter,/api=inference
→ auto-registers ["jupyter", "inference"] in IPC registry
→ announces to mesh peers
→ remote capability.call discovers and routes to this drawbridge
```

See `operations/GATEHOUSE_DARKFOREST_STANDARD.md` §Drawbridge, §Capability advertisement.

### Bond Escalation

The process by which incoming traffic transitions from weaker to stronger bond
types as trust is progressively established. Each escalation requires stronger
authentication and crosses a deeper K-Derm envelope layer:

| Escalation | Authentication Required | K-Derm Crossing |
|------------|------------------------|-----------------|
| Weak → Ionic | BTSP scoped token | Outer membrane → periplasm |
| Ionic → Metallic | Mito-Beacon membership proof | Periplasm → plasma membrane |
| Metallic → Covalent | Nuclear session (fresh key spawn) | Plasma membrane → cytoplasm |

The reverse path (covalent → weak) is **Ceremony** — a controlled temporal decay.
The outward path (covalent → metallic → ionic → weak across VPS layers) is the
**bond-type degradation** model documented in `KDERM_DIDERM_ENVELOPE.md`.

Bond escalation and degradation are complementary: escalation is inward (external
traffic gaining trust), degradation is outward (sovereignty weakening as content
moves toward the extracellular). The gatehouse brokers inward escalation. The
VPS diderm envelope enforces outward degradation.

See `foundations/BONDING_MODEL_STANDARD.md` §Bonding Escalation Path.

### Endosymbiosis

The process by which external systems progressively internalize — moving from
weak to ionic to metallic to covalent bonding as they are absorbed into the
sovereign infrastructure. Named after the biological process where independent
organisms become organelles through progressive integration.

Examples: Cloudflare TLS credentials (weak) → bearDog ACME shadow (ionic) → bearDog
sovereign TLS (covalent). GitHub Pages (weak) → Forgejo periplasmic mirror (metallic) → Forgejo
sovereign (covalent). Each sovereignty shadow track is an endosymbiosis in progress.

See `K_DERM_RECONCILIATION.md` §K-Derm Extensions Not in Gen4.

---

## The Meta Layer

### metaPrimal

A **metaPrimal** is a repository that is conceptual instead of functional — it
doesn't compile into a binary, but it is an essential organism in the ecosystem.
metaPrimals follow the same camelCase naming and have their own git repos.

| metaPrimal | Purpose |
|------------|---------|
| **wateringHole** | How primals intercommunicate. Standards, IPC protocols, leverage guides, handoffs. The coordination documentation layer. |
| **whitePaper** | Theses, concepts, and documentation of evolution. The scientific and strategic record — gen2/gen3 paper trails, attsi outreach, baseCamp papers. |
| **sourDough** | The nascent primal for rapid evolution of new primals. A starter culture for bootstrapping new primal projects. |

### Phase 1 / Phase 2

**Temporal artifacts**, not semantic categories. Phase directories were
organizational markers used while building between gates — keeping which primals
were on which gate clear during early development. They correspond loosely to
`gen2/` and `gen3/` in whitePaper. Not actively meaningful; treat them as
historical scaffolding if encountered.

### Version Numbers and Differential Evolution

Springs and primals independently evolve their own progress markers. Some use
**session numbers** (e.g., neuralSpring S145), some use **version numbers**
(e.g., hotSpring v0.6.29, wetSpring V113). This divergence is fully
intentional — AI-assisted development means each project self-flavors over
time as its AI iterations accumulate. There is no global numbering standard
because primal autonomy extends to how they count.

**Differential evolution rates are biological, not bugs.** Archaea, microbes,
and algae all evolved at different rates — depth reflects internal evolution
pressure, not cross-system maturity parity. A primal at v0.14 has undergone
more internal iteration than one at v0.2, but neither is "ahead" or "behind"
— they serve different niches with different selection pressures. rhizoCrypt
(0.14.17) has iterated heavily because DAG provenance is a complex domain.
biomeOS (0.1.0) is young because orchestration crystallized later. Both are
production-ready for their current role.

No primal has reached 1.0. The 1.0 threshold means: API surface is stable,
breaking changes require major version bumps, and the primal's niche is
fully colonized. petalTongue (1.6.6) is the closest — its grammar pipeline
has stabilized through heavy external-facing iteration.

**Team guidance**: Version numbers should reflect the primal's own internal
evolution cadence. Bump minor for capability additions, patch for fixes and
refinements. Do not synchronize versions across primals. The ecosystem
manifest (`ecosystem_manifest.toml`) and depot checksums are the cross-system
coordination layer — not version alignment.

---

## Licensing & Strategy

### Lysogeny Protocol

**Area denial through open prior art.** By publishing under AGPL-3.0, every
innovation becomes prior art that prevents patents. Named after bacteriophage
lysogeny — the viral DNA integrates into the host genome and persists.

### scyBorg

The **ecosystem licensing standard** — a triple copyleft framework:

- **AGPL-3.0-or-later**: All code, shaders, tools, infrastructure
- **ORC**: All mechanical interactions (primal coordination, IPC patterns, atomics, game rules)
- **CC-BY-SA 4.0**: All documentation, papers, methodology, reverse engineering findings

Each layer is governed by an independent nonprofit (FSF, Open RPG Creative
Foundation, Creative Commons). No single entity can revoke any layer.

scyBorg extends beyond "just code" to cover the entire body of work — the
papers, the methodology, the evolution trail, the reverse engineering
documentation. The intent is that everything published is permanently open and
untargetable.

### Symbiotic Exception

An **additional permission** (AGPL-3.0 Section 7) granted to a named
organization based on reciprocal benefit. The default scyBorg license applies to
everyone. Exceptions reduce licensing friction for allies — partners whose
tools, hardware, or knowledge benefit the ecosystem.

Exceptions are not for sale. They are diplomatic: granted based on symbiotic
value, revocable if the relationship ends. The public AGPL version is unaffected.

| Tier | Basis |
|------|-------|
| **Symbiotic** | Partner provides tools/hardware/knowledge (e.g., RustDesk, BrainChip) |
| **Reciprocal Open** | Partner publishes their own work under AGPL (e.g., GPU vendor opens architecture docs) |

See `SCYBORG_EXCEPTION_PROTOCOL.md` for the full protocol.

### Suppression Inversion

The strategic principle that by **owning nothing**, the project is untargetable.
No revenue to disrupt, no corporate entity to sue, no publisher to pressure, no
platform to suppress. Knowledge that has been published under copyleft cannot be
un-known. Reverse engineering of owned hardware is legal (*Sega v. Accolade*,
*Oracle v. Google*). The suppression vectors that companies use against
threatening work (legal, platform, commercial) all require a target — and
scyBorg eliminates the target.

### AI Authorship Paradox

All ecoPrimals code and documentation is AI-assisted, and this is disclosed
openly. Copyright law is unsettled on AI-assisted work. The paradox: if
AI-assisted work **is** copyrightable, the copyleft licenses apply normally and
the commons is protected. If AI-assisted work **is not** copyrightable, the
output enters public domain — an even stronger form of openness. Either outcome
preserves the commons. The only parties harmed by a negative ruling are those
claiming exclusive copyright on AI-assisted work for revenue. ecoPrimals has no
such claim, so the legal uncertainty is everyone else's problem.

See `gen3/about/LICENSING_STRATEGY.md` §8 for the full analysis.

### cellMembrane

The **selective permeability layer** of the ecosystem — a private operational
repo managed by the **cellMembrane team (ironGate)** (sporeGarden org) that deploys the
**fieldMouse Tower** composition to external substrate (VPS). cellMembrane
controls what crosses between intracellular (LAN/gates) and extracellular
(public internet) layers. Also provides the `membrane` CLI for gate operations:
`gate.enroll`, `gate.bootstrap`, `temporal.cascade`, `plasmid.harvest`.

Current state (Wave 155b):
- **Channel 2 Relay** (Songbird TURN :3478): **LIVE**
- **Channel 2b Remote** (RustDesk hbbs/hbbr :21115-21117): **LIVE**
- **Channel 3 Surface** (Caddy TLS :80/:443, `membrane.primals.eco`): **LIVE**
- **Enrollment** (`/enroll/*` → mesh.gate_enroll): **LIVE** on golgiBody
- **Phase 7**: gate.enroll → mesh.enroll via HMAC-SHA256 proof
- **Builder identity**: `plasmid.harvest` records builder gate + timestamp
- **Checksum verify**: handles both plain-string and struct TOML formats

cellMembrane is operationally on GitHub Private and should migrate to
Forgejo-only when covalent gates host Forgejo on sovereign infrastructure. It contains
sensitive configuration (SSH keys, API tokens, deployment scripts) that
MUST NOT leak to public repos. See `operations/REPO_MEMBRANE_BOUNDARY.md` and
`CELLMEMBRANE_FIELDMOUSE_DEPLOYMENT.md`.

### fieldMouse

The **minimal deployable structure** for the ecoPrimals ecosystem. Where a gate
runs a full NUCLEUS and a niche composes primals via a deploy graph, a fieldMouse
is the smallest stripped system — as few as a single atomic or chimera — purpose-built
for a constrained deployment niche.

fieldMouse is not a primal. It is a **deployment class** — a category of niche
deployments defined by how they fit their target hardware and environment. A
fieldMouse might be:

- A Tower Atomic chimera on a RISC-V microcontroller (crypto + network only)
- A Nest Atomic on a Raspberry Pi (crypto + network + storage)
- A sensor node streaming data via songBird to a gate
- A pipette-mounted data acquisition system handling provenance and streaming
- An environmental monitor (pH, temperature, GPS) publishing to the mesh
- An Akida NPU edge classifier on a Coral board

fieldMouse deployments share these properties:

| Property | Description |
|----------|-------------|
| **Minimal** | Smallest subset of atomics for the niche — no unused primals |
| **Embedded-first** | Targets RISC-V, ARM (aarch64/armv7), and constrained SoCs |
| **ecoBin compliant** | Pure Rust, zero C, cross-compiles with `cargo build --target` |
| **Mesh-native** | Connects to the broader ecosystem via songBird or TCP fallback |
| **Provenance-aware** | Even the smallest fieldMouse signs data via bearDog |

The evolutionary ladder extends downward:

```
NUCLEUS     (full primal composition — gate)
  ↓
Niche       (biomeOS deploy graph — selected primals)
  ↓
fieldMouse  (minimal atomic/chimera — embedded, sensor, edge)
```

A fieldMouse on a pipette handles data streaming for the instrument — sample ID,
timestamp, GPS, measurement, provenance signature — and publishes to the mesh.
A fieldMouse on a soil probe does the same for pH, moisture, temperature. A
fieldMouse on an Akida board classifies microbial communities in real time from
MinION streaming data. The primals are the same. The deployment is minimal.

See `FIELDMOUSE_DEPLOYMENT_STANDARD.md` for the specification.

### guideStone

The **verification class** for ecoBins that produce reproducible, self-proving
output. Where the binary ladder describes structure (UniBin → ecoBin → genomeBin)
and deployment classes describe context (NUCLEUS → Niche → fieldMouse),
guideStone describes **what the output means** — that the computation's results
are their own proof of correctness.

guideStone is not a primal. It is not a binary type. It is a **quality
certification** — an orthogonal dimension that any ecoBin can carry when its
output satisfies five properties:

| Property | Requirement |
|----------|-------------|
| **Deterministic** | Same input, same binary, any hardware → same output within named tolerances |
| **Reference-traceable** | Every numeric claim traces to a paper, standard, constant, or mathematical proof |
| **Self-verifying** | Checksums, CRC, hashes, or signatures validate integrity without trusting the channel |
| **Environment-agnostic** | ecoBin compliant, no external dependencies, no sudo, CPU-only path covers full output |
| **Tolerance-documented** | Every threshold has a physical or mathematical derivation — no magic numbers |

Any primal, spring, or composition can have a guideStone edition:

- A **spring guideStone** is the validation artifact with derived (not tuned) tolerances
- A **primal guideStone** is the reference edition — pinned, fully auditable, validated
  against external test vectors (e.g., bearDog's Ed25519 against NIST/RFC vectors)
- A **composition guideStone** certifies an end-to-end pipeline (e.g., Chuna Engine
  producing ILDG gauge configurations, helixVision producing reproducible variant calls)

guideStone is complementary to the provenance trio. guideStone certifies the
computation (reproducible output). The trio certifies the event (who, when, where,
attribution). Both together produce a Novel Ferment Transcript — the highest-grade
digital artifact in the ecosystem.

The name pairs with **guidePost** (the planned philosophy/ethics repository):
guidePost points the way in human terms; guideStone is the demonstrable proof
in computational terms.

See `GUIDESTONE_STANDARD.md` for the specification.
See `whitePaper/gen4/architecture/GUIDESTONE.md` for the concept paper.

### Loam Certificate

An **intracellular provenance artifact** — not a transport credential. Loam
Certificates are the ecosystem's sovereign ownership, lending, and provenance
mechanism. They are minted by loamSpine (`certificate.mint`), transferred
(`certificate.transfer`), loaned (`certificate.loan`), escrowed
(`certificate.escrow`), and returned. Their lifecycle is:
DAG fermentation (rhizoCrypt) → dehydration → permanent spine (loamSpine) →
attribution braid (sweetGrass).

Loam Certificates live entirely within the cytoplasm. They never cross the
drawbridge. They are the building blocks of Novel Ferment Transcripts.

**Do not confuse with TLS credentials.** TLS/ACME x.509 certificates are
*drawbridge transport credentials* — external golden cage artifacts managed
by Caddy (current) or bearDog gatehouse (sovereignty target). TLS credentials
mediate weak → ionic bond escalation at the outer membrane. Loam Certificates
mediate ownership and provenance within the covalent interior. They share a
word; they share nothing else.

| | Loam Certificate | TLS Credential |
|---|---|---|
| **Owner** | loamSpine | Caddy / bearDog gatehouse |
| **Layer** | Cytoplasm (intracellular) | Outer membrane (drawbridge) |
| **Lifecycle** | mint → transfer → loan → return | issue → renew → revoke |
| **Backing** | Provenance trio + rootPulse | Let's Encrypt / ACME (golden cage) |
| **Bond type** | Covalent (sovereign) | Weak → ionic (endosymbiosis target) |
| **Permanence** | Permanent (append-only spine) | Ephemeral (90-day rotation) |

### Novel Ferment Transcript (NFT)

Memory-bound digital objects fermented through the provenance trio. Not
blockchain NFTs — ferment transcripts are provenance-tracked creative artifacts
with attribution chains via sweetGrass, permanence via loamSpine Certificates,
and ephemeral workspace via rhizoCrypt DAGs. The fermentation is irreversible
and time-bound: value accumulates from history, not artificial scarcity.

A Novel Ferment Transcript is a Loam Certificate whose provenance chain
records the full fermentation — every interaction, transformation, and
attribution that shaped it. Game keys, scientific chain-of-custody records,
sample provenance chains, and creative artifacts are all NFTs.

---

## The Composition Layer

### BYOB (Bring Your Own Binaries)

The deployment model for gen4 products. Products consume pre-built primal binaries
from `plasmidBin/` via `plasmidbin fetch` (Rust CLI) — they never compile primal source. This
enforces zero source coupling between products and primals.

### Niche YAML

A YAML metadata file that declares what a deployment IS — its organisms (primals
and chimeras), their interactions (capability-call wiring), and customization
options. The niche YAML is the identity document for a composition; the deploy
graph is its execution plan.

Example: `esotericWebb/niches/esoteric-webb.yaml` declares 10 organisms, 5
interaction edges, and 3 customization options.

### Primal Launch Profile

A TOML configuration file that tells a product's launcher how to invoke each
primal binary: subcommand, port flag, health method, readiness timeout. Launch
profiles bridge the gap between "binary exists in plasmidBin" and "primal is
running and healthy."

Example: `esotericWebb/config/primal_launch_profiles.toml`

### sporeGarden Product

A gen4 artifact in the `sporeGarden/` GitHub organization. Products compose
primals into tools people use — games, science platforms, creative tools. They
follow the BYOB model, consuming binaries via IPC and defining their composition
through deploy graphs + niche YAML.

Examples: esotericWebb (CRPG engine), blueFish (PFAS analytical chemistry),
helixVision (genomics platform), initioChem (CompChem FEL explorer).

### PrimalBridge

A product-side JSON-RPC client that wraps capability calls to running primals.
Each product writes its own bridge — `esotericWebb` has a `PrimalBridge` with 23
methods covering 8 primal domains. The bridge handles graceful degradation when
optional primals are absent.

### Primal Resolution Order

The 8-step discovery sequence biomeOS uses to find primal sockets at runtime:
env hint → capability sockets → XDG → abstract → /tmp → socket registry →
Neural API → TCP fallback. See `COMPOSITION_PATTERNS.md` §4.

---

## The Propagation Layer

### pappusCast

The **auto-propagation daemon** for projectNUCLEUS. Named for the dandelion
pappus — the parachute structure that carries seeds to new ground. Each
validated notebook is a seed; pappusCast disperses them from the compute
workspace to the public observer surface.

Self-pollination (auto-validation within workspace) and cross-pollination
(propagation to public surface) mirror the dandelion's reproductive strategy.
Micro-species (per-notebook variants) and endemic species (gate-specific
content) map naturally to the botanic model.

Key properties:
- **Tiered validation**: Light (on-change: JSON valid, kernel, title), Medium
  (periodic: execute + check errors), Heavy (~6h: diff, changelog, regression)
- **Adaptive rate limiting**: Publish interval scales with active JupyterHub
  users — `min(BASE_MINUTES * max(1, active_users), MAX_MINUTES)`
- **Snapshot architecture**: Public surface holds managed copies, not live
  symlinks — validated, stable, decoupled from live edits
- **Quarantine**: Notebooks that fail validation are moved aside, not published
- **Evolution path**: Python (now) → Rust binary → pappusCast primal

pappusCast is not a primal (yet). It is a Python daemon in the projectNUCLEUS
deployment tooling. When evolved to Rust, it will follow the UniBin/ecoBin
pattern and integrate with biomeOS composition for multi-gate propagation.

### tunnelKeeper

A **Rust crate** in the projectNUCLEUS validation tree for programmatic
Cloudflare tunnel health checks, DNS resolution, and config file parsing.
tunnelKeeper is the first step toward Rust-native Cloudflare interaction,
replacing shell-based health probes with structured Rust types.

tunnelKeeper is not a primal. It is a validation tool that may eventually
absorb into songBird or become a standalone tunnel management binary as the
sovereignty evolution progresses (Cloudflare → WireGuard → Songbird NAT).

### darkforest

The **pure Rust security validator** for NUCLEUS deployments. A 939KB modular
binary with zero runtime dependencies. Performs pen testing (3 threat actors),
protocol fuzzing (13 primals + JupyterHub), and cryptographic strength
validation (13 checks). Produces structured JSON reports for auditable
security posture tracking.

darkforest embodies the Dark Forest security posture: reveal nothing to probes,
fail closed, log everything, trust nothing external. The name is intentional —
the validator assumes the network is hostile.

---

## The Binary Evolution Ladder

### ecoBin

An **ecoBin** is a statically-linked, cross-compiled Rust binary — zero C
dependencies on the critical path. ecoBins compile for all Cargo target triples
and are the base unit of the depot system. Every primal binary is an ecoBin.

### genomeBin

A **genomeBin** is the evolved ecoBin — a binary that works across all deployed
operating systems and architectures without code changes. The name reflects that
the binary carries its full "genome" (capabilities, platform detection, IPC
selection) intrinsically.

genomeBin targets are tiered by deployment status:

| Tier | Targets | Meaning |
|------|---------|---------|
| **Tier 1 genomeBin** | x86_64-linux-musl, aarch64-linux-musl, x86_64-windows-gnu, aarch64-android, armv7-linux-musl | MUST — deployed gates exist |
| **Tier 2** | x86_64-apple-darwin, aarch64-apple-darwin | SHOULD — deployment imminent |
| **Tier 3 PROVEN** | riscv64, ppc64le, s390x, sparc64, i686, arm32 | Compiled, no deployed gate |
| **Tier 4 FUTURE** | wasm32-wasip1, loongarch64, freebsd, illumos, redox | Horizon |

### Silicon-Deistic Deployment

The architectural principle that **hardware is truth, OS is abstraction**.
Tower Atomic (bearDog + songBird + skunkBat) is the universal platform layer.
Just as songBird abstracts ports and mesh topology, Tower Atomic abstracts OS
differences: UDS vs named pipes vs TCP, systemd vs Windows Service vs launchd,
`/opt/membrane` vs `%APPDATA%`. Primals detect their platform at runtime and use
the best available mechanism. `bind_mode`, `target`, and other OS-specific manifest
fields are transitional — they document what primals auto-detect internally.

Goal: a gate enrolls with only **name + composition + physical proof**. Everything
else is intrinsic.

### Autonomous Enrollment

The **zero-operator gate provisioning system** shipped in Wave 155a. A gate
self-enrolls by running `gate-enroll.sh` (Linux) or `gate-enroll.ps1` (Windows)
with a hub address and physical proof (enrollment token, FIDO2 attestation, or
beacon proximity). The enrollment endpoint on golgiBody (`mesh.gate_enroll`)
handles: physical proof verification → IP pool allocation → WireGuard peer
registration → Forgejo SSH key creation → family seed delivery → genetic
enrollment.

### Self-Registration

Gates declare their own name and composition during enrollment. No manifest
pre-definition is needed — `ecosystem_manifest.toml` gate entries are informational,
not authoritative. Any hardware anywhere can become a gate by running the
enrollment script with a valid trust token.

### Composition

A **composition** is a named set of primals that defines a gate's capabilities.
Compositions are hierarchical — every composition includes Tower Atomic base:

| Composition | Primals | Count | Use Case |
|-------------|---------|-------|----------|
| **tower** | bearDog, songBird, skunkBat | 3 | Minimal trust boundary |
| **compute** | Tower + toadStool, barraCuda, coralReef, biomeOS | 7 | GPU/HPC workloads |
| **nest** | Tower + nestGate, rhizoCrypt, loamSpine, sweetGrass | 7 | Content-addressed storage |
| **full** | All 13 foundation primals + squirrel | 13 | Complete NUCLEUS |

### BTSP (BearDog Trust Signaling Protocol)

The **handshake protocol** all primals use for outbound connections. BTSP
ClientHello is shipped on all 13/13 primals (Wave 151d). When
`BEARDOG_UDS_REQUIRE_BTSP=1`, local UDS connections require BTSP proof before
any method call is accepted.

---

## Quick Lookup

| Term | One-Line Definition |
|------|---------------------|
| **Gate** | A physical computer running the ecoPrimals stack |
| **Primal** | A self-contained Rust binary providing domain primitives |
| **Primitive** | The atomic unit of capability a primal provides |
| **Spring** | A validation environment that composes primals and validates science (gen3) |
| **Garden** | A user-facing product composing primals via BYOB (gen4, e.g. esotericWebb) |
| **Atomic** | A named primal composition pattern (Tower, Node, Nest, NUCLEUS) |
| **Niche** | A biomeOS BYOB deployment — primals composed via deploy graph |
| **Deploy graph** | TOML DAG defining germination order and capability wiring |
| **Chimera** | A fused multi-primal binary with unified API |
| **Germination** | Starting a primal until its socket is ready |
| **biomeOS** | The orchestration substrate running on a gate |
| **NUCLEUS** | Full primal composition (all atomics + Squirrel) |
| **Plasmodium** | Multi-gate collective (2+ bonded NUCLEUS instances) |
| **metalForge** | Evolution context where springs work on hardware concepts (GPU/CPU/NPU) |
| **baseCamp** | Cross-spring paper program — validation to exploration (18 papers) |
| **metaPrimal** | Conceptual repo (wateringHole, whitePaper, sourDough) — pre-binary, documentaion |
| **Paper parity** | Spring output matches published figures within named tolerance |
| **Absorption** | Spring replaces local math with barraCuda canonical version |
| **Delegation** | Primal routes work to another primal via IPC |
| **Handoff** | Session continuity document in wateringHole |
| **Fossil record** | Archived handoffs — the project's geological history |
| **NestGate (primal)** | Data storage primal: content-addressed storage, capability-based service discovery |
| **nestgate.io (domain)** | BirdSong beacon domain: Dark Forest gated public rendezvous at `api.nestgate.io`, served by biomeOS via Cloudflare Tunnel. See `DOMAIN_INFRASTRUCTURE.md` |
| **Ancestor beacon** | Generic mito-beacon rendezvous that can host multiple family beacons and guide new nodes to correct genetics |
| **Lysogeny** | Area denial through open AGPL prior art |
| **scyBorg** | Triple copyleft: AGPL-3.0 (code) + ORC (mechanics) + CC-BY-SA (docs) |
| **Symbiotic exception** | AGPL Section 7 grant to allies based on reciprocal benefit |
| **Suppression inversion** | Owning nothing makes the project untargetable |
| **AI authorship paradox** | Copyright uncertainty harms exclusivity claimants, not the commons |
| **cellMembrane** | Selective permeability layer — private ops repo deploying fieldMouse Tower to VPS for relay/TLS/content channels |
| **fieldMouse** | Minimal deployable ecoPrimals — smallest atomic/chimera for embedded/sensor/edge niches |
| **guideStone** | Verification class — ecoBin quality grade certifying reproducible, self-proving, reference-traceable output |
| **Spore Ownership Matrix** | Three-way ownership split: domain science (springs), spore envelope (lithoSpore), NUCLEUS gateway (biomeOS). See `operations/SPORE_OWNERSHIP_MATRIX.md` |
| **primalSpring** | Coordination spring — validates ecosystem composition, graph execution, emergent systems, bonding |
| **BYOB** | Bring Your Own Binaries — gen4 products consume pre-built primal binaries, never source |
| **Niche YAML** | YAML metadata declaring a composition's organisms, interactions, and customization options |
| **Primal launch profile** | TOML config for how a product launcher invokes each primal binary |
| **sporeGarden product** | A gen4 tool composing primals for end users (e.g., esotericWebb, blueFish, helixVision, initioChem) |
| **PrimalBridge** | Product-side JSON-RPC client wrapping capability calls to running primals |
| **Primal resolution order** | 8-step discovery: env → capability → XDG → abstract → /tmp → registry → Neural API → TCP |
| **NUCLEUS Gateway** | biomeOS bidirectional spore interface — `biomeos nucleus ingest` absorbs spores into nest_atomic; `biomeos nucleus emit` creates spores from NUCLEUS state |
| **pseudospore-core** | Shared Rust crate (lithoSpore) for spore envelope primitives — 10 `pub mod` (9 API + `error`): `blake3_manifest`, `braid_envelope`, `domain_profile`, `envelope`, `error`, `livespore`, `receipts`, `scope`, `tarball`, `validation`. Consumer API: `PseudoSporeEnvelope::load()` + `validate()` with typed `SporeError` (thiserror). Includes GUIDESTONE-GRADE derivation anchoring checks. lithoSpore wired (NC-1.3); biomeOS v3.81+ created `biomeos-pseudospore` (NC-1.4 resolved) |
| **pappusCast** | Auto-propagation daemon — dandelion-seed dispersal from workspace to observer surface |
| **tunnelKeeper** | Rust crate for Cloudflare tunnel health, DNS resolution, config parsing |
| **darkforest** | Pure Rust security validator — pen test + fuzz + crypto strength (939KB, zero deps) |
| **soundStage** | Transparent ceremony observation — see entropy flowing, mixing, derivation. Anti-black-box. |
| **Snapshot architecture** | Public surface holds managed copies, not live symlinks — stable observer view |
| **Tiered validation** | Light (structural) → Medium (execution) → Heavy (regression) validation pipeline |
| **plasmidBin** | Binary distribution repo — pre-built musl-static NUCLEUS primals, Rust CLI, automated harvest |
| **postPrimordial** | Deployment regime where all NUCLEUS binaries come from plasmidBin — no local builds |
| **Fossilization** | Moving resolved content to fossilRecord, replacing with pointer stub |
| **Wave** | Named coordination pulse — ecosystem synchronization event tracked in glacial readiness |
| **Stadial** | Hard convergence phase — fitness gate that culls non-conforming patterns |
| **Interstadial** | Warming phase — diversification and specialization under constraint |
| **goldenCage** | External services bootstrapping sovereignty (GitHub, Cursor, Cloudflare) — chrysalis thesis |
| **Gatehouse** | Bond escalation broker — single external surface accepting weak interactions, promoting to ionic/metallic/covalent via authentication |
| **Darkforest** | Invisible mesh interior — zero external ports, all discovery via mesh.peers and capability.call, prevents sovereignty leakage |
| **Drawbridge** | Single crossing point between gatehouse and darkforest — songBird HTTP proxy translating external HTTP to capability-routed mesh semantics |
| **Bond escalation** | Progressive trust promotion: weak → ionic (BTSP token) → metallic (Mito-Beacon) → covalent (nuclear session) |
| **Bond degradation** | Outward trust weakening across VPS diderm: covalent (gate) → metallic (inner) → ionic (pepti) → weak (GitHub) |
| **Endosymbiosis** | Progressive internalization of external systems into sovereign infrastructure (weak → covalent over time) |
| **Capability advertisement** | Drawbridge auto-registers route capabilities into IPC registry and announces to mesh peers at startup (Wave 133d) |
| **Genetic enrollment** | Two-layer trust: mito gate (family membership) + nuclear lineage distance (derivation hops → trust tier) |
| **Tower Shadow** | Shadow deploy mode — Tower runs alongside WG, collects comparative metrics without affecting production |
| **LAN mesh routing** | `preferred_address()` prefers `lan_addr` for same-switch peers over WG overlay (353x latency difference) |
| **CallerContext** | Per-UDS-connection identity (SO_PEERCRED) wired into method gate for access control |
| **Chimera Phase 0** | First chimera step — extract bearDog hot-path crypto into shared library for in-process use |
| **EndpointType** | Routing variant: `Local` for LAN direct paths (sub-ms) vs `Overlay` for WG relay (100ms+) |
| **K-Derm trust tiers** | Outer/inner/data domain classification in `capability_registry.toml` — method-level access control |
| **Shadow benchmark** | Continuous Tower vs WG metrics collected by `tower-shadow.timer` (hourly, JSON output) |
| **Nest Atomic (expanded)** | Wave 151 data layer: nestGate CAS + loamSpine DAG + rhizoCrypt cross-repo + sweetGrass braids + rootPulse orchestration |
| **rootPulse** | biomeOS-orchestrated Provenance Trio composition — replaces waterFall with content-addressed provenance |
| **Keystore2 binder** | Android 12+ native API for hardware-backed key operations without JVM — production path for bearDog StrongBox |
| **Crypto delegation** | songBird routes all crypto to bearDog over IPC — 6/6 seams validated Wave 150 (chimera-ready) |
| **libtower.so** | Chimera Phase 0 extraction target — bearDog crypto + songBird routing + skunkBat defense as shared library |
| **Silicon Atheism** | Platform-agnostic dispatch — code compiles for all targets, probes capabilities at runtime (no compile-time branching in business logic) |
| **genomeBin** | Evolved ecoBin — binary carrying full platform awareness, working across all deployed OS/arch without code changes |
| **Silicon-deistic deployment** | Hardware is truth, OS is abstraction. Tower Atomic handles platform differences intrinsically |
| **Autonomous enrollment** | Zero-operator gate provisioning — `gate-enroll.sh`/`.ps1` → `mesh.gate_enroll` → meshed |
| **Self-registration** | Gates declare name + composition during enrollment, no manifest pre-definition needed |
| **Composition** | Named primal set: tower (3), compute (7), nest (7), full (13) — all include Tower base |
| **BTSP** | BearDog Trust Signaling Protocol — handshake on all 13/13 primals, defense-in-depth |
| **golgiBody depot** | Sole WAN depot — all genomeBins served via Caddy TLS at `depot.primals.eco` |
| **Gate enmeshment** | Glacial goal — Tower Atomic deployment across all platforms, then Nest Atomic for data |
