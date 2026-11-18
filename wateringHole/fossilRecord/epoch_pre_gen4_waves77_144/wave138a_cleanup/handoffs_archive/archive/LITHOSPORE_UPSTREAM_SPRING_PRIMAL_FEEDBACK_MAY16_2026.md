<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->

# lithoSpore → Upstream Spring + Primal Feedback

**Date**: 2026-05-16
**From**: lithoSpore workstream (gardens/lithoSpore)
**For**: All spring teams, primal teams, NUCLEUS integration, biomeOS

## Purpose

lithoSpore is the ecosystem's first **Targeted GuideStone** — a complete
verification chassis that went from Python notebooks to USB-deployable
Rust ecoBins with primal composition annotations. This document captures
patterns, lessons, and requests that are relevant to upstream evolution.

---

## 1. Patterns That Worked (Adopt/Evolve)

### Capability-Based Discovery (All Primals)

lithoSpore's discovery chain proves the ecosystem's capability-based
resolution model works in practice:

```
$CAPABILITY_PORT → UDS discovery.sock → TURN relay → standalone
```

**Key insight**: Discovery code should never contain primal names in the
primary resolution path. lithoSpore evolved from `$SONGBIRD_TURN_SERVER`
to `$RELAY_SERVER` with legacy fallback — the code works regardless of
which primal provides relay services.

**Recommendation for all primals**: Use `$CAPABILITY_PORT` naming convention
(e.g. `$STORAGE_PORT`, `$COMPUTE_PORT`) for env-based discovery. Reserve
primal-name env vars as legacy fallback only.

### In-Process Module Dispatch (Gardens/Products)

lithoSpore unified 7 separate binaries into a single `litho` CLI with
in-process `lib.rs` dispatch. Benefits:
- Single 5.1 MB binary instead of 7 × ~2 MB
- No subprocess coordination or IPC for module calls
- argv[0] symlink detection for USB entry points
- Shared `litho-core` eliminates ~200 LOC of duplicated harness code

**Recommendation**: Any garden with multiple modules should consider
the lib-crate-with-cli-dispatch pattern over separate binaries.

### Scope-Driven Configuration (Gardens/Products)

lithoSpore's `scope.toml` + `data.toml` pattern decouples the chassis
(validate/fetch/assemble) from the instance (LTEE). The chassis reads
module tables at runtime, falling back to compiled constants.

**Pattern**:
```toml
# scope.toml — what this instance validates
[[module]]
name = "power_law_fitness"
crate = "ltee-fitness"
```

This enables lithoSpore to validate non-LTEE datasets without code
changes — just provide a different scope.toml.

### DataBinding Builder Helpers (Visualization)

Rather than constructing `serde_json::json!({})` objects inline,
lithoSpore extracted typed builder helpers that reduce 400+ lines of
repetitive JSON construction to ~50 lines of function calls:

```rust
viz::timeseries("fitness_over_time", "Fitness", x, y, "Generation", "Relative Fitness")
```

**Recommendation for petalTongue team**: Consider promoting these
helpers to `petal-tongue-types` for ecosystem-wide use.

---

## 2. Lessons from the Elevation (Python → Rust → Primal)

### Tolerance Calibration Is Non-Trivial

Python (numpy C extensions) and Rust (native f64) produce slightly
different results for iterative algorithms (Nelder-Mead, Pearson).
lithoSpore needed per-module named tolerances with scientific justification:

```toml
[power_law_exponent]
tolerance = 0.01
reason = "Nelder-Mead optimizer path sensitivity between scipy and Rust"
```

**Recommendation**: Any spring producing golden values should include
tolerance bands, not just expected values.

### BLAKE3 Pure Rust Is Production-Ready

The `blake3` crate with `default-features = false, features = ["pure", "std"]`
eliminates all C/assembly code while maintaining acceptable performance
for data integrity (GB-scale hashing). The `pure` feature is essential
for ecoBin compliance — without it, `blake3` pulls `cc` for SIMD
assembly acceleration.

**Note**: The `ureq → rustls → ring` TLS chain still requires C/assembly
for constant-time cryptography. No production-grade pure-Rust TLS exists.
This is an ecosystem-wide constraint that affects any primal doing HTTPS.

### `#![forbid(unsafe_code)]` at Workspace Level Works

lithoSpore enforces `unsafe_code = "forbid"` at the workspace lint level.
All 9 crates inherit via `[lints] workspace = true`. Zero unsafe blocks
exist in the codebase while maintaining full numerical performance.

**Recommendation**: All primals should evaluate workspace-level
`forbid(unsafe_code)` unless they have justified unsafe blocks.

---

## 3. Requests to Primal Teams

### songBird: TURN Client Library

lithoSpore's geo-delocalized mode resolves TURN endpoints from env vars
but has no actual TURN relay protocol. The `discover_from_turn()` function
returns an endpoint address, but all RPC calls use standard TCP, which
only works if the relay forwards raw TCP.

**Need**: A Rust TURN client library that lithoSpore (and other gardens)
can use to relay JSON-RPC calls through Songbird relays.

**Workaround**: lithoSpore degrades gracefully to standalone mode.

### petalTongue: Discovery Socket Registration

lithoSpore discovers visualization services via:
1. `$VISUALIZATION_SOCKET` env var
2. `litho_core::discover("visualization")` → discovery socket
3. XDG runtime dir scan (`biomeos/visualization.sock`)

**Need**: petalTongue should register its `visualization` capability with
the ecosystem discovery socket (`$XDG_RUNTIME_DIR/ecoPrimals/discovery.sock`)
so that step 2 works without explicit env vars.

**RPC methods consumed**: `visualization.render`, `visualization.render.dashboard`,
`visualization.render.stream`, `visualization.session.create`

### bearDog: FIDO2 Attestation for liveSpore.json

lithoSpore's `liveSpore.json` records deployment provenance (host, time,
discovery path, checks, hashes). Hardware attestation via SoloKey would
add a FIDO2 witness signature to each entry.

**Need**: A Rust API for FIDO2/CTAP2 assertion that lithoSpore can call
during `liveSpore.json` append.

**Priority**: P3 — liveSpore.json works without attestation.

### biomeOS: Signal Dispatch Routing

lithoSpore's Tier 3 graph annotates `nest.store` and `nest.commit` signals.
When biomeOS supports signal dispatch routing, the provenance phase
(rhizoCrypt → loamSpine → sweetGrass) collapses to a single `nest.store`
dispatch.

**Need**: Signal dispatch routing so that `nest.store` automatically
triggers the provenance trio without explicit graph wiring.

**Current state**: Graph and workload TOMLs are annotated; no runtime
code changes needed when routing is available.

### toadStool: Compute Dispatch Validation

lithoSpore's Tier 3 graph declares toadStool as an optional GPU dispatch
node (`by_capability = "compute"`). lithoSpore has zero GPU code — all
acceleration is deferred to toadStool via `compute.dispatch`.

**Need**: Validation that toadStool can receive lithoSpore-style
validation workloads and return structured JSON results.

---

## 4. Requests to Spring Teams

### groundSpring: Remaining 4 Papers

lithoSpore has B1–B4 complete. Papers B6, B8, B9 need groundSpring
statistical methods:

| Paper | What lithoSpore Needs |
|-------|----------------------|
| B6 | Burden → disorder potential mapping, distribution fitting |
| B8 | Phase variation rate estimation, stochastic switching models |
| B9 | Gamma/exponential/lognormal DFE parameter estimation |

### neuralSpring: ML Surrogate Path

lithoSpore modules 3 (alleles) and 4 (citrate) can accept ML surrogate
enrichment from neuralSpring. The integration point is additive — current
groundSpring-based validation works without ML. When neuralSpring B3/B4
models are ready, lithoSpore can overlay them as additional checks.

### hotSpring: Anderson B9 Extension

Module 7 (Anderson-QS) currently covers B2. hotSpring B9 (DFE evolution)
would extend the disorder framework with DFE fitting. lithoSpore has
a stub dataset entry (`dfe_evolution_2024`) ready for integration.

---

## 5. NUCLEUS Composition and Deployment

### Deployment Matrix Cell

lithoSpore's validated cell is `lithospore-x86-vm-uds`:
- **Platform**: x86_64-unknown-linux-musl
- **Isolation**: VM (libvirt) or container (Podman/Docker)
- **Connectivity**: UDS (LAN) or standalone (airgap)
- **Artifact**: ~16GB USB with data + binaries + Python + provenance

### Atomic Instantiation via neuralAPI

The lithoSpore spore is self-sufficient — it produces valid results without
external orchestration. For neuralAPI atomic instantiation:

1. biomeOS creates a spore instance (USB or container)
2. Discovery socket provides primal topology
3. Validation auto-detects achievable tier
4. Results flow through available provenance channels
5. liveSpore.json records everything

The spore is the atomic unit. NUCLEUS composition adds provenance and
attestation but does not change the validation logic.

### Graph for Tier 3

```
[validate] → [beardog] → [rhizocrypt] → [loamspine] → [sweetgrass]
                          ↓ (optional)
                       [toadstool]
```

All nodes discovered by capability strings. The graph can execute
partially — validation always completes even if provenance nodes are
unavailable. `required = false` on toadStool.

---

## 6. What We Learned That Applies Ecosystem-Wide

1. **Graceful degradation is essential.** lithoSpore runs in 4 modes
   (standalone, env, UDS, TURN) and produces valid results in all of
   them. Every primal interaction is optional with explicit fallback.

2. **Capability strings, not primal names.** Code that names primals
   directly breaks when primals are renamed, merged, or replaced.
   Capability-based discovery survived lithoSpore's full evolution
   without modification.

3. **Scope separation pays off.** Decoupling instance (LTEE) from
   chassis (validate/fetch/assemble) via scope.toml allows the same
   machinery to validate different scientific domains.

4. **Builder helpers reduce JSON construction debt.** Any crate producing
   structured JSON output benefits from typed builders over inline
   `json!({})` macros.

5. **Workspace lint inheritance simplifies governance.** Setting
   `unsafe_code = "forbid"` once at workspace level eliminates the
   need to audit individual crates.

6. **Signal annotation before runtime adoption.** Annotating signals
   in TOML (graph + workload) before runtime support exists creates
   a documented contract for future evolution.
