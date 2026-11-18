<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# primalSpring Overwatch — Spring Audit Context (Wave 109)

**Date**: 2026-06-11
**From**: eastGate overwatch (cellMembrane)
**For**: primalSpring overwatch team — context reboot for all Spring audits
**Wave**: 109 — guideStone Deployment Convergence

---

## Context

Review this Spring's codebase, specs/, docs, and the ecosystem standards at
`ecoPrimals/infra/wateringHole/` (especially `README.md`,
`PURE_RUST_SOVEREIGN_STACK_GUIDANCE.md`, `TARGETED_GUIDESTONE_STANDARD.md`,
`ECOBIN_ARCHITECTURE_STANDARD.md`, `PRIMAL_REGISTRY.md`,
`STANDARDS_AND_EXPECTATIONS.md`, and `DEPLOYMENT_VALIDATION_STANDARD.md`).
Also review sibling springs for handoff patterns and cross-spring conventions.

---

## What is a Spring?

A Spring is a niche validation domain that proves scientific Python baselines
can be faithfully ported to sovereign Rust+GPU compute using the ecoPrimals
stack. Springs depend on barraCuda (pure math — WGSL shaders, precision
strategy) for all numerical work. They coordinate with toadStool (hardware
discovery, compute orchestration) and coralReef (sovereign shader compiler)
via JSON-RPC IPC. Springs never import other springs — they coordinate
through wateringHole handoffs and shared barraCuda primitives.

Springs compose NUCLEUS atomics — the canonical primal compositions defined
in `primalSpring/graphs/fragments/`. Every spring has a proto-nucleate graph
in `primalSpring/graphs/downstream/` that defines its target NUCLEUS
composition (which primals, which capabilities, which bonding model). The
proto-nucleate is the bridge between validation code and primal composition.

---

## The NUCLEUS Atomic Model

```
Tower (electron):   BearDog + Songbird — trust boundary, crypto, discovery
Node  (proton):     Tower + ToadStool + barraCuda + coralReef — compute
Nest  (neutron):    Tower + NestGate + rhizoCrypt + loamSpine + sweetGrass — storage + provenance
NUCLEUS (atom):     Tower + Node + Nest (9 core primals)
Meta-tier:          biomeOS + Squirrel + petalTongue — cross-atomic (orchestration, AI, UI)
Full composition:   13 primals — deployed alive on 5+ gates (Wave 109)
```

---

## Current Ecosystem State (Wave 109)

- **13/13 primals** deployed and alive on golgiBody (VPS), eastGate, grapheneGate (Pixel 8a)
- **5-gate mesh** operational (LAN x86_64 + WAN + ARM aarch64)
- **guideStone-grade deployment** in convergence:
  - `gate.bootstrap` shipped (6-phase enrollment + deployment.toml emission)
  - Gate profiles declared in `ecosystem_manifest.toml` (target, mobility, bind_mode, composition, transport)
  - `plasmid.build` — guideStone-grade Rust build pipeline with ELF validation and provenance
  - BLAKE3 fail-closed checksum verification at all layers
  - JSON-RPC health probes replacing pgrep process detection
- **Standard Primal Startup Contract** (Stream 1) in progress:
  - Envelope: `$PRIMAL server --bind-mode $PRIMAL_BIND_MODE --port $PORT`
  - `PlatformCapabilities::detect()` auto-senses transport
  - biomeOS v4.22 SHIPPED (first adopter of --bind-mode + HEALTH-01)
- **HEALTH-01 endpoint** becoming standard:
  - `{"method":"health"}` → `{"status":"ok","primal":"X","version":"Y","uptime_s":N}`
  - 10/13 primals already respond; rhizoCrypt, petalTongue, songBird converging

---

## Five guideStone Properties (audit lens)

Every artifact — binary, deployment, validation — must satisfy:

| # | Property | Standard |
|---|----------|----------|
| P1 | **Deterministic** | Same depot + same gate profile = identical NUCLEUS state |
| P2 | **Reference-Traceable** | Every binary traces to provenance.toml (commit, rustc, timestamp, blake3) |
| P3 | **Self-Verifying** | BLAKE3 fail-closed; mismatch = abort |
| P4 | **Environment-Agnostic** | musl-static ecoBins, no runtime deps, no local builds |
| P5 | **Tolerance-Documented** | Named tolerances for staleness, handshake, convergence, startup |

---

## The Evolution Path

```
Python baseline → Rust validation → barraCuda CPU → barraCuda GPU →
fused TensorSession pipeline → sovereign dispatch (coralReef native) →
primal composition (proto-nucleate graph: call primals by capability via IPC) →
NUCLEUS deployment (biomeOS deploys the graph, springs are compositions)
```

### Maturity Cycle: Local GPU Code

```
Write (local WGSL) → Validate → Handoff → barraCuda Absorbs → Lean on upstream
```

### Maturity Cycle: Primal Composition

```
Read proto-nucleate → Wire IPC to primals → Validate composition →
Discover gaps → Hand back to primalSpring → Primals evolve → Cycle continues
```

### neuralSpring + Squirrel Inference

neuralSpring provides AI inference for the entire ecosystem. Any spring that
adds Squirrel to its composition immediately gains access to `inference.*`
capabilities (`inference.complete`, `inference.embed`, `inference.models`) as
neuralSpring evolves WGSL shader ML. No spring code changes needed — Squirrel
discovers neuralSpring as a provider (falls back to Ollama until native
inference is ready).

---

## Audit Dimensions

### COMPLETION STATUS

What have we not completed? What mocks, TODOs, FIXMEs, debt, hardcoding
(expected values, tolerance thresholds, data paths, primal names, socket
paths) and gaps remain? Are hardcoded validation targets properly sourced
from documented Python runs with provenance (script, commit, date, exact
command)? Is every experiment traceable?

### CODE QUALITY

Are we passing all linting, fmt, clippy (pedantic+nursery), and doc checks
with zero warnings? Are we as idiomatic and pedantic as possible? What bad
patterns and unsafe code do we have? Target:

- Zero unsafe in application code (`#![forbid(unsafe_code)]`)
- Zero `#[allow()]` in production code
- Zero mocks outside `#[cfg(test)]`
- All files under 1000 LOC
- Pure Rust deps only (ecoBin compliant — zero C dependencies in application code)
- Zero-copy where possible (especially I/O parsers — stream, don't buffer)
- No production `unwrap()`, `expect()`, `todo!()`, `unimplemented!()`
- No `TODO`/`FIXME`/`HACK` comments in production code

### VALIDATION FIDELITY

Do ALL Rust results match Python baselines exactly (or within documented,
justified, minimal tolerances)? Is every tolerance named, centralized, and
explained? Are Python baselines still reproducible — rerun and confirm no
baseline drift? Are validation binaries following the hotSpring pattern
(hardcoded expected values, explicit pass/fail, exit 0/1)?

### BARRACUDA DEPENDENCY HEALTH

Are we using barraCuda primitives where they exist (stats, linalg, ops,
dispatch, nn, spectral, nautilus) instead of reinventing? No duplicate math —
if barraCuda has it, delegate to it. Are we on the latest barraCuda version?
Are all local WGSL shaders candidates for upstream absorption
(Write→Absorb→Lean)?

### GPU EVOLUTION READINESS

Which Rust modules are ready for GPU shader promotion (Tier A: direct rewire
to existing barraCuda op, Tier B: adapt existing shader, Tier C: new shader
needed)? What blocks promotion? Document the mapping: Rust module → barraCuda
op / WGSL shader → pipeline stage. Are we using TensorSession for fused
multi-op pipelines where possible?

### PRIMAL COMPOSITION READINESS

Has this spring read its proto-nucleate graph
(`primalSpring/graphs/downstream/{spring}_*_proto_nucleate.toml`)? Which
primals in the composition are wired via IPC? Which are still called via
direct Rust imports (these need to migrate to capability-based IPC)? Are
capabilities registered in the niche (`niche.rs` or equivalent)? Is the
spring discoverable by biomeOS via `capability.list` / `health.liveness` /
`health.readiness`?

What gaps were discovered in the proto-nucleate composition — document and
hand back to primalSpring (`docs/PRIMAL_GAPS.md`). Has the spring added
Squirrel to its composition for AI capabilities? If not, what blocks it?

### TEST COVERAGE

Target 90%+ line coverage (llvm-cov). Do we have: unit tests (analytical
known-values), integration tests (file parsing round-trips, primal IPC),
validation binaries (baseline comparison with exit codes), and determinism
tests (rerun-identical)? For stochastic algorithms, is the seed fixed and
tolerance justified?

### GUIDESTONE DEPLOYMENT READINESS (Wave 109 NEW)

Does this spring's binary:
- Accept the standard startup envelope (`--bind-mode`, `--port`)?
- Respond to `{"method":"health"}` with `{status, primal, version, uptime_s}`?
- Pass `file` arch validation (correct ELF arch, statically linked for musl)?
- Have an entry in `sources.toml` with correct `binary_name`?
- Appear in the gate profile composition for its target gates?
- Emit zero runtime dependencies (pure musl-static ecoBin)?
- Have provenance traceability in `provenance.toml`?

### ECOSYSTEM STANDARDS (wateringHole/)

- License: AGPL-3.0-or-later only (SCYBORG trio: AGPL + ORC + CC-BY-SA)
- Architecture: ecoBin compliant (pure Rust, zero C deps, cross-compile musl-static)
- IPC: JSON-RPC 2.0 over Unix sockets, capability-based discovery
- Files: all under 1000 LOC, single-responsibility modules
- Data provenance: all datasets from public repositories (SRA, Zenodo, EPA, PDB) with documented accession numbers
- Sovereignty: no vendor lock-in, no proprietary dependencies
- Handoffs: `wateringHole/handoffs/` follow naming convention `{SPRING}_{VERSION}_{TOPIC}_HANDOFF_{DATE}.md`
- Atomic alignment: fragments metadata in deploy graphs must accurately reflect which NUCLEUS atomics are present (tower_atomic, node_atomic, nest_atomic, meta_tier, nucleus)
- Bonding policy: cross-atomic compositions must declare bond type, trust model, and encryption tiers per atomic boundary
- guideStone P1-P5: all deployable artifacts must satisfy all 5 properties

### PRIMAL COORDINATION

Are we wired to discover and communicate with relevant primals (toadStool,
Squirrel, petalTongue, biomeOS) via IPC? Is our capability set registered?
Do we have typed IPC clients or MCP tool definitions where appropriate? Are
we calling primals by capability (`by_capability`) not by identity? Is the
spring's deploy graph aligned with its proto-nucleate? Does the spring hand
gaps and new patterns back to primalSpring for ecosystem-wide refinement?

---

## Key References

| Document | Location | Purpose |
|----------|----------|---------|
| Proto-nucleate graph | `primalSpring/graphs/downstream/{spring}_*_proto_nucleate.toml` | Target NUCLEUS composition |
| Fragments (atomics) | `primalSpring/graphs/fragments/` | Canonical atomic definitions |
| Deployment matrix | `primalSpring/config/deployment_matrix.toml` | 43 validation cells |
| Primal gaps | `primalSpring/docs/PRIMAL_GAPS.md` | Known gaps per primal |
| Composition guidance | `primalSpring/wateringHole/PRIMALSPRING_COMPOSITION_GUIDANCE.md` | How to wire primals |
| Ecosystem leverage | `primalSpring/wateringHole/PRIMALSPRING_ECOSYSTEM_LEVERAGE_GUIDE.md` | Spring→primal leverage |
| guideStone standard | `wateringHole/TARGETED_GUIDESTONE_STANDARD.md` | Budding model for portable artifacts |
| ecoBin architecture | `wateringHole/ECOBIN_ARCHITECTURE_STANDARD.md` | Pure Rust binary standard |
| Sovereignty stack | `wateringHole/PURE_RUST_SOVEREIGN_STACK_GUIDANCE.md` | No C deps, no vendor lock |
| Primal registry | `wateringHole/PRIMAL_REGISTRY.md` | All 13 primals, capabilities, IPC |
| Wave 109 FRAGO | `impulses/active/..wave109-guidestone-deployment-convergence.toml` | Current convergence streams |
| Gate profiles | `ecosystem_manifest.toml [gates.*]` | Per-gate topology config |
| cellMembrane AAR | `handoffs/cellMembrane/AAR_CELLMEMBRANE_WAVE106_DETERMINISTIC_DEPLOYMENT_JUN10_2026.md` | Living deployment standard |

---

## What Changed Since Last Context

- **Wave 108**: All 13 primals rebuilt for aarch64-unknown-linux-musl, grapheneGate 13/13 alive, VPS depot fully synced
- **Wave 109**: guideStone convergence — 5 work streams, standard startup contract, gate profiles, deployment.toml, JSON-RPC health
- **cellMembrane**: `plasmid.build` shipped (ELF validation, provenance), `gate.profile` command, deployment.toml emission, JSON-RPC health probes
- **biomeOS v4.22**: First adopter of `--bind-mode` + HEALTH-01, STARTUP-BM-01 SHIPPED
- **nestGate**: STARTUP-NG-01 SHIPPED (HTTP default in server mode)
- **skunkBat v0.2.10**: STARTUP-SB-01 SHIPPED (standard primal startup contract)
- **coralReef**: STARTUP-CR-01 SHIPPED (startup envelope convergence)
- **flockGate**: VPS songbird restarted (Wave 108), WAN re-test pending

---

## Archive Note

Archive code and docs exist for reference and fossil record — ignore them
for this audit. Focus on active production code and current-state docs.
