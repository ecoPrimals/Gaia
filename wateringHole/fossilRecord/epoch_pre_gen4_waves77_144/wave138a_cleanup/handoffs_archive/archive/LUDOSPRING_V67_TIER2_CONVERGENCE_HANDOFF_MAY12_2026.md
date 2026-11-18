# SPDX-License-Identifier: AGPL-3.0-or-later

# ludoSpring V67 — Tier 2 Convergence Handoff

**Date**: May 12, 2026
**From**: ludoSpring (game science composition)
**To**: barraCuda, toadStool, coralReef, primalSpring, sibling springs, projectNUCLEUS
**Signal**: Tier 2 wiring complete. Pass 14 APIs consumed. 858 tests, 9 scenarios.

---

## Executive Summary

ludoSpring has wired the newly-unblocked Pass 14 APIs (`toadstool.validate` and
`barracuda.precision.route`) into its IPC layer. The spring is now fully Tier 2
convergence-ready and waiting on live primal deployments via plasmidBin for
end-to-end validation.

**Key numbers:**
- **858** workspace tests (0 failures)
- **9** validation scenarios (6 Rust, 3 Live)
- **28** `game.*` canonical methods
- **0** unsafe, 0 clippy, 0 TODO/FIXME, 0 bare `#[allow]`
- `#![forbid(unsafe_code)]` on library + all binaries
- `default = []` (Tier 4 IPC-first since V62)
- `--format json` on all validation output (V66)
- `toadstool.validate` + `precision.route` wired (V67)

---

## What Shipped (V64–V67)

| Version | Date | Change |
|---------|------|--------|
| V64 | May 11 | `default = []`, coralReef IPC wired, domain method parity, 3 notebooks |
| V65 | May 12 | Foundation Thread 9+10 expressions, notebook CI verification |
| V66 | May 12 | `--format json` Tier 2 readiness, barraCuda v0.4.0 absorbed, params GPU split |
| V67 | May 12 | `toadstool.validate` pre-flight + `barracuda.precision.route` advisory |

---

## For barraCuda

### What We Consume
- `barracuda v0.4.0` (optional, feature-gated behind `local`)
- `precision.route` via IPC (advisory — tier, hardware_hint, requires_compiler)
- Activations, stats, RNG, correlation from `barracuda::*` when `local` feature active

### What We Learned
- **Precision routing works well as advisory**: the `PrecisionAdvice` struct with
  tier (u8, 1-15), hardware_hint, and requires_compiler is sufficient for dispatch
  routing decisions. No additional fields needed.
- **Graceful degradation pattern**: when barraCuda is unreachable, ludoSpring returns
  well-formed unavailability (`tier: 0, hardware_hint: ""`) rather than erroring.
  This is the correct IPC contract for non-critical advisory calls.

### Absorption Candidates (barraCuda → absorb from ludoSpring)
| Module | What | Priority |
|--------|------|----------|
| `procedural/noise.rs` | Perlin 2D/3D, fBm with configurable octaves | Medium — when shader tier ready |
| `metrics/engagement.rs` | Engagement batch evaluation (parallel) | Low — domain-specific |
| `tolerances/` | Named tolerance pattern with citations | Pattern (reusable) |
| `capability_domains` pattern | Structured method catalog with introspection | Pattern (reusable) |

---

## For toadStool

### What We Consume
- `compute.submit` — GPU workload dispatch
- `compute.status` — workload status query
- `compute.capabilities` — substrate query
- `compute.dispatch.*` — low-latency direct dispatch
- `compute.validate` — **NEW (V67)**: workload pre-flight
- `compute.list_workloads` — workload TOML enumeration

### What We Learned
- **Pre-flight response shape is good**: `valid`, `gpu_available`, `precision_tier`,
  `estimated_dispatch_time_ms`, `warnings[]`, `required_capabilities[]` covers all
  our decision points for game compute routing.
- **60Hz tick budget validated**: game.tick composite handler runs at 0.6ms (well within
  16.6ms budget). IPC roundtrip is not the bottleneck — it's compute latency.
- **projectNUCLEUS workload TOMLs updated**: Both `ludospring-game-validation.toml` and
  `ludospring-composition-parity.toml` now pass `--format json` and declare
  `[output] schema = "toadstool-validate-v1"`.

### Pattern for Other Springs
ludoSpring's `ipc/toadstool.rs` demonstrates the full toadStool surface:
- Core dispatch (submit/status/capabilities)
- Direct dispatch (low-latency path for real-time)
- Tier 2 pre-flight (validate_workload)
- Precision advisory integration
- Graceful degradation on all paths

---

## For coralReef

### What We Need (GAP-01 — WIRED, **UNBLOCKED** — coralReef Sprint 7 shipped)
- `shader.compile` for sovereign WGSL compilation
- FECS stability proof **SHIPPED** — `try_coralreef_compile` GPU path is now viable
- ludoSpring Perlin/fBm/raycaster shaders ready for sovereign dispatch

### What's Ready on Our Side
- `ipc/coralreef.rs` — typed client with `try_coralreef_compile()` function
- Feature-gated: only exercised when coralReef is reachable
- 5 WGSL shaders in `barracuda/shaders/` ready for sovereign compilation

---

## For Sibling Springs

### Patterns to Absorb

**1. Pure composition deployment** (no spring binary in plasmidBin)
ludoSpring deploys as a NUCLEUS cell graph (`ludospring_cell.toml`) — 12 nodes
composing primals. The `ludospring` binary is the validation target only, not a
deployed service. biomeOS deploys the graph; the spring doesn't run as a daemon.
This is the lightest deployment model — consider for springs that are primarily
science validation.

**2. Tier 2 convergence pattern** (`ipc/toadstool.rs`)
Full surface: submit → status → dispatch → validate → precision_route.
Each function returns a typed result struct with an `available: bool` field.
When primals are unreachable, return well-formed unavailability (not errors).
Tests exercise both paths (live and degraded).

**3. Dual-path math** (`crate::math`)
When `local` feature is enabled: delegates to `barracuda::*` library calls.
When disabled: uses inline pure-Rust fallbacks with identical behavior.
Both paths pass the same `s_tier4_math_parity` scenario (identical outputs).

**4. Validation scenario framework** (`validation/scenarios/`)
Each scenario: `ScenarioMeta` (id, track, tier, provenance_crate, date, description)
+ run function. Scenarios are Tier::Rust (pure, CI-safe) or Tier::Live (requires
deployed primals). UniBin `validate` subcommand runs them with `--format json`.

**5. `--format json` for toadstool.validate dispatch**
```json
{"status": "PASS", "checks": N, "passed": N, "failed": 0, "scenarios": [...]}
```
projectNUCLEUS workload TOMLs reference this schema.

---

## For primalSpring

### Composition Status
- 130/141 checks passing (92.2% composition parity)
- 11 remaining checks are blocked on upstream primal capabilities (provenance trio,
  coralReef SM rebuild, toadStool live dispatch)
- Proto-nucleate: `ludospring_cell.toml` (12 nodes)
- Fragments: tower_atomic, node_atomic, nest_atomic, meta_tier

### Registry Alignment
- 28 `game.*` methods canonical (primalSpring 413-method registry)
- CI cross-sync test validates against `config/capability_registry.toml`
- Method constants: `ipc/methods.rs` (10 domain modules, compile-time consistency test)

### Gaps Remaining (all blocked upstream)
| GAP | Blocked On | Notes |
|-----|-----------|-------|
| ~~GAP-01~~ | ~~coralReef FECS~~ **RESOLVED** (Sprint 7) | SM rebuild → sovereign shader compilation **UNBLOCKED** |
| GAP-04 | rhizoCrypt | Deterministic replay not yet validated |
| GAP-05 | sweetGrass | Braid verification not yet validated |
| GAP-14 | skunkBat E2E | Low priority — IPC module exists |

---

## For projectNUCLEUS

- 2 workload TOMLs updated with `--format json` and `[output]` section
- Binary: `ludospring validate` (requires `--features ipc,guidestone`)
- Build: `cargo build --release --features ipc,local,guidestone`
- Output schema: `toadstool-validate-v1`
- Gate: exit 0 = all pass, exit 1 = any failure

---

## For Foundation

- **Thread 9** (Gaming/Creative): Expression active, 6 data sources documented
- **Thread 10** (Provenance/Economics): Expression active, co-seeded with primalSpring
- Notebooks: 3 verified executable (`01_interaction_laws`, `02_perlin_noise`, `03_flow_engagement`)
- No LTEE reproduction (domain doesn't overlap)

---

## Evolution Ceiling

ludoSpring has reached its evolutionary ceiling for local work. All remaining
evolution depends on upstream:

1. ~~**coralReef** ships FECS~~ → **SHIPPED** (Sprint 7) — exercise sovereign shader compilation
2. **toadStool** deploys to plasmidBin → we exercise live Tier 2 validation
3. **Provenance trio** ships stable binaries → we exercise live DAG/braid
4. **skunkBat** ships E2E → we exercise cross-primal audit logging

Until then: zero debt, zero unsafe, zero gaps in our control, 858 tests green.
