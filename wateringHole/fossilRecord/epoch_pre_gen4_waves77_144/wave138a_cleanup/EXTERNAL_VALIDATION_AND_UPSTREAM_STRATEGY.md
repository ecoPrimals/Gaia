# External Validation and Upstream Strategy — Signal Through Collaboration

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | May 3, 2026 |
| **Status** | Active |
| **Authority** | WateringHole Consensus |
| **Related** | `UPSTREAM_CONTRIBUTIONS.md`, `GPU_AND_COMPUTE_EVOLUTION.md`, `SPRING_INTERACTION_PATTERNS.md` |

---

## Principle

Springs are evolutionary pressure chambers for primals. The more diverse the
selective pressure, the fitter the code that survives. External systems —
published physics, open-source frameworks, community standards — are additional
selective environments. Every external system we validate against, and solve
problems for, increases the signal our evolution responds to.

This is Jevons paradox applied to compute: making GPU scientific computing
more accessible does not reduce demand for our stack. It expands the space
of people who can use it, which expands the validation surface, which
strengthens the primals.

There is no competition between humans if you accept Jevons paradox.

---

## The Evolve → Validate → Abstract → Upstream Cycle

```
Spring evolves shaders under domain-specific pressure
  → Validates against published results (faculty, papers)
  → Validates against external frameworks (Rapier, Kokkos, etc.)
  → Battle-tested shaders absorb into barraCuda
  → Abstracted solutions extracted as standalone crates
  → Handed upstream to external projects
  → External adoption provides wider testing + peer validation
  → Wider ecosystem strengthens the substrate we build on
```

This is the same cycle described in `UPSTREAM_CONTRIBUTIONS.md`, extended to
include external validation as an explicit evolutionary pressure source.

---

## External Validation Targets

### Tier 1: Peer Projects (Solve Their Documented Problems)

Projects on similar paths where we have solved problems they've documented
hitting. The approach is proof-of-work, not a pitch — reproduce their
journey, show we went further, offer standalone solutions.

| Project | Their Documented Gap | Our Solution | Standalone Extraction |
|---------|---------------------|--------------|----------------------|
| **Dimforge / wgmath** | "WGSL lacks a module system" (Jan 2026 blog) | coralReef `prepare_wgsl` preamble composition | `wgsl-compose` or similar |
| **Dimforge / wgmath** | No f64/precision beyond f32 on consumer GPUs | barraCuda DF64 (88K lines WGSL, 3.24 TFLOPS RTX 3090) | `wgsl-precision` (DF64 + PrecisionBrain) |
| **Dimforge / wgmath** | Abandoned WGSL for rust-gpu due to language limitations | 1,145 WGSL shaders proving WGSL scales with infrastructure | Documentation + shader corpus reference |
| **Dimforge / wgmath** | No hardware-adaptive precision routing | toadStool PrecisionBrain + HardwareCalibration | Part of `wgsl-precision` |

**Approach**: Same as faculty network — reproduce equivalent physics (rigid
body dynamics as validation target), show results, offer standalone solution.
Not onboarding. Peer engagement.

### Tier 2: Framework Reproduction (Validate Our Shaders Against Theirs)

Use external frameworks as additional selective pressure on spring shaders.
Run equivalent physics on both systems, compare correctness and performance.

| Framework | Domain | Spring | Validation Target |
|-----------|--------|--------|-------------------|
| **Rapier** (Dimforge) | Rigid body dynamics | ludoSpring / hotSpring | Contact, BVH, joint constraints |
| **Kokkos** | HPC parallel patterns | hotSpring | Yukawa MD (already benchmarked: 27× → 3.7× gap closed) |
| **LAMMPS** | Molecular dynamics | hotSpring | LJ, EAM, many-body potentials |
| **MILC** | Lattice QCD | hotSpring | Wilson/staggered fermion HMC |
| **Sarkas** | Yukawa plasma MD | hotSpring | Already validated (195/195 checks, 0.000% drift) |

Shaders that survive validation against external frameworks absorb into
barraCuda. The external framework's physics becomes another test suite for
our GPU compute substrate.

### Tier 3: Community Ecosystems (Expand the User Surface)

Communities where our technology solves existing pain points. The approach
is onboarding — making our tools usable by people who aren't us.

| Community | Platform | What We Offer | Entry Point |
|-----------|----------|---------------|-------------|
| **r/webgpu** | Reddit | Largest WGSL shader corpus, DF64 precision | ludoSpring browser demo |
| **wgpu users** | Discord/Matrix | Science-grade compute on consumer GPUs | barraCuda shader crates |
| **Rust gamedev** (Bevy, Fyrox) | Discord | DF64 precision for physics, coralReef composition | Standalone precision crate |
| **burn / candle** | GitHub | Scientific precision (DF64) for ML on wgpu | Precision layer integration |
| **numr** | Rust forums | 827 production WGSL kernels they need contributors for | Kernel contribution |
| **Scientific Computing in Rust** | Annual workshop | Cross-domain GPU compute methodology | Talk / paper submission |

---

## Spring Guidance: External Validation as Selective Pressure

### For All Springs

1. **Identify external frameworks** in your domain that implement equivalent
   physics or computation. These are validation targets, not competitors.

2. **Reproduce their results** on our stack. This is the same discipline as
   faculty paper reproduction: run their benchmark, match their output, document
   the comparison.

3. **Document gaps** discovered during reproduction. These become evolution
   targets for barraCuda shaders.

4. **Absorb upstream** when shaders are validated. Battle-tested shaders move
   from the spring into barraCuda via the standard handoff pattern.

5. **Abstract standalone solutions** when we've solved a problem an external
   project has documented. Package as a standalone crate following the
   `UPSTREAM_CONTRIBUTIONS.md` pattern (MIT/Apache-2.0 for adoption, AGPL
   for primal-specific code).

### Per-Spring External Validation Targets

| Spring | External Targets | What We Validate |
|--------|-----------------|------------------|
| **hotSpring** | Kokkos, LAMMPS, MILC, Sarkas, Rapier (physics subset) | MD forces, lattice QCD, nuclear structure, rigid body dynamics |
| **wetSpring** | BLAST+, Kraken2, MetaPhlAn, RDKit | Spectral matching, phylogenetics, metagenomics |
| **airSpring** | FAO-56 reference implementations, DSSAT, AquaCrop | Evapotranspiration, water balance, crop modeling |
| **groundSpring** | SciPy stats, uncertainties (Python), GUM framework | Measurement uncertainty, sensor calibration |
| **neuralSpring** | PyTorch, burn, tch-rs, ONNX Runtime | ML primitives, transformer attention, protein folding |
| **healthSpring** | NONMEM, Monolix, PK-Sim | Pharmacokinetics, dose-response, microbiome diversity |
| **ludoSpring** | Rapier, Box2D, Godot physics, Unity DOTS Physics | Rigid body, collision, procedural generation |
| **primalSpring** | plasmidBin, Docker, systemd | Composition validation, deployment, binary distribution |

### The Absorption Path

```
Spring shader (evolved under external pressure)
  → Validated against external framework output
  → Passes internal test suite (83,587+ tests)
  → Handoff to barraCuda (ABSORPTION_MANIFEST pattern)
  → Spring deletes local copy, rewires to upstream
  → barraCuda gains battle-tested kernel
  → Standalone extraction if externally valuable
  → Upstream contribution to external project
```

Every cycle through this loop makes barraCuda more capable. Every domain
added makes the next domain faster to add (shared infrastructure: DF64,
precision routing, preamble composition, hardware adaptation). The compound
effect is a GPU compute library that spans games to lattice QCD, validated
against external frameworks across every domain.

---

## Standalone Extraction Candidates (Updated)

Extends `UPSTREAM_CONTRIBUTIONS.md` §3 "Future Candidates":

| Candidate | Origin | Target Recipient | Status |
|-----------|--------|-----------------|--------|
| `proc-sysinfo` | toadStool sysmon | Rust ecosystem (crates.io) | Ready for extraction |
| **`wgsl-precision`** | barraCuda DF64 + toadStool PrecisionBrain | **Dimforge / wgmath, burn, Rust GPU community** | **Production — needs packaging** |
| **`wgsl-compose`** | coralReef `prepare_wgsl` | **Dimforge / wgmath, WGSL authors** | **Production — needs packaging** |
| Pure Rust DRM ioctl wrappers | coralReef coral-driver | Linux GPU community | In progress |
| Capability-based service discovery | biomeOS + songBird | Rust microservice community | Under development |
| Genetic lineage trust model | bearDog | Distributed systems community | Conceptual |

### `wgsl-precision` Scope (Priority Extraction)

Minimum viable standalone crate:

- `df64_core.wgsl` — `Df64` struct, `two_sum`, `two_prod` (FMA-based), add/mul/div
- `df64_transcendentals.wgsl` — sqrt (Newton-Raphson), exp (Cody-Waite), log (atanh)
- `prepare_wgsl()` — detect `Df64`/`df64_` usage, prepend preamble, guard duplicates
- `GpuAdapterInfo` — wgpu probing for `SHADER_F64`, f64 reliability, shared-memory pathology
- `HardwareCalibration` — NVVM poisoning risk, driver classification, transcendental safety
- `PrecisionBrain` — `PrecisionHint` → `PrecisionTier` routing with fallbacks
- `PrecisionRoutingAdvice` — F64Native / F64NativeNoSharedMem / Df64Only / F32Only
- Tests validating DF64 arithmetic on NVIDIA + AMD consumer GPUs
- MIT/Apache-2.0 dual license (per `UPSTREAM_CONTRIBUTIONS.md` policy)

### `wgsl-compose` Scope

Minimum viable standalone crate:

- Preamble injection with dependency ordering
- Duplicate detection and guard (skip if struct/fn already defined)
- `enable f64` / `enable f16` stripping (naga compatibility)
- Extensible preamble registry (user-defined libraries, not just DF64)
- MIT/Apache-2.0 dual license

---

## The rustChip Precedent

rustChip demonstrated the standalone extraction pattern: NPU driver extracted
from the sovereign compute pipeline, packaged as an independent workspace
(`akida-chip`, `akida-driver`, `akida-models`, `akida-bench`, `akida-cli`),
no toadStool dependency from a fresh clone, offered to BrainChip with a
SCYBORG licensing exception.

The same pattern applies to `wgsl-precision` for Dimforge: standalone
workspace, their examples, adapted to their crate structure. A solution to
their documented problem, offered as proof of work.

---

## Signal Maximization

The more external systems we validate against and solve problems for:

1. **More selective pressure** → fitter barraCuda kernels
2. **More peer validation** → stronger thesis (sovereign science, K-NOME)
3. **More users** → more testing → fewer bugs → more trust
4. **More domains** → more cross-pollination (DF64 discovery pattern applies everywhere)
5. **More collaborators** → faster evolution (Jevons: the pie grows)

The constraint does not limit what we become. The constraint defines what
we become. Every external system we interact with is another constraint,
another selective pressure, another source of signal that shapes the
evolution of the primals.

---

## Version History

| Version | Date | Notes |
|---------|------|-------|
| **1.0.0** | **2026-05-03** | Initial guidance from ironGate bootstrap session. Captures Dimforge peer analysis, external validation strategy, standalone extraction priorities, and spring-level guidance for incorporating external frameworks as evolutionary pressure. |

*Authority: WateringHole Consensus. AGPL-3.0-or-later.*
