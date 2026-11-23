# hotSpring v0.6.32 — Upstream Ecosystem Handoff (May 13, 2026)

**From**: hotSpring (strandGate team)  
**To**: All primal teams + river delta spring teams + primalSpring coordination  
**Classification**: Niche convergence → atomic deployment readiness  

---

## Executive Summary

hotSpring is at **zero deep debt** across all 7 dimensions. **592 (default) / 1,041 (barracuda-local)** lib tests pass with zero clippy warnings, zero TODO/FIXME/HACK, zero production mocks, zero library unsafe, zero C dependencies on default build. The Node atomic is structurally validated. Deploy graphs, harvest scripts, and wire names are aligned with canonical upstream specs. This handoff documents what primals and springs should absorb from hotSpring's evolution, what we need from upstream, and composition patterns proven for NUCLEUS deployment.

---

## 1. What hotSpring Proved (Patterns for Absorption)

### 1.1 Three-Tier Validation Arc (Python → Rust UniBin → Primal NUCLEUS Composition)

hotSpring's validation pipeline is the reference implementation for science-validated compute springs:

| Tier | Implementation | Status |
|------|---------------|--------|
| **Tier 0**: Python baseline | 25/25 papers reproduced in `baselines/` notebooks (SciPy/NumPy) | COMPLETE |
| **Tier 1**: Rust validation | `hotspring_unibin validate` — 17 default / 20 barracuda-local scenarios | COMPLETE |
| **Tier 2**: NUCLEUS composition | `validate_nucleus_*` binaries — IPC parity against Rust baselines | COMPLETE (bare mode 30/30) |

**Pattern for springs**: Every science claim should have a Python baseline, a Rust validation binary, and a NUCLEUS composition validator that proves IPC-routed results match direct Rust execution within documented tolerances.

### 1.2 Eukaryotic UniBin

`hotspring_unibin` consolidates 5 modes: `certify` (L0-L6 guideStone), `validate` (scenario registry), `serve` (JSON-RPC server), `status`, `version`. The ScenarioRegistry pattern (`validation/scenarios/registry.rs`) with `ScenarioMeta` provenance tracking is reusable across springs.

**Pattern for springs**: Migrate from N separate binaries to a single UniBin with mode dispatch. The `OrExit<T>` trait and `ValidationHarness` with exit codes (0=pass, 1=fail, 2=skip) are documented for adoption.

### 1.3 Capability-Based Discovery (Zero Hardcoded Primal Knowledge)

All IPC calls use `call_by_capability(domain, method, params)` — no hardcoded socket paths, no hardcoded primal names. The niche advertises `LOCAL_CAPABILITIES` (21 served) and `ROUTED_CAPABILITIES` (26 proxied with canonical providers). Registration with biomeOS via `lifecycle.register` + `capability.register`.

**Pattern for springs**: Replace any direct `PrimalName::socket_path()` calls with `by_domain()` NUCLEUS discovery. Feature-gate all IPC behind `primal-proof` for CI that doesn't need live primals.

### 1.4 Sovereign GPU Compute Ladder (CPU → GPU → Sovereign)

hotSpring's 3-tier compute ladder is documented in `projectNUCLEUS/workloads/hotspring/`:

| Tier | Substrate | Example |
|------|-----------|---------|
| CPU | Pure Rust | Wilson plaquette, RHMC, molecular dynamics |
| GPU (wgpu) | Cross-platform WGSL shaders | 128 shaders, gradient flow, HMC |
| Sovereign | VFIO/DRM direct | RTX 5060 (8/8 PASS), Titan V (warm-catch), K80 (warm-catch) |

**Pattern for springs with GPU needs**: Use wgpu for cross-platform, sovereign dispatch for vendor-specific. Feature-gate sovereign behind `barracuda-local`.

### 1.5 Deploy Graph Structure

7 deploy graphs (`graphs/*.toml`) define NUCLEUS deployment topologies. Each specifies:
- `[[graph.nodes]]` with spawn order, health probes, fragment references
- `hotspring_unibin` as the application node (order 10)
- 10 primal dependencies (BearDog, Songbird, coralReef, ToadStool, BarraCuda, NestGate, rhizoCrypt, loamSpine, sweetGrass, Squirrel)
- Tiered encryption matching NUCLEUS boundary semantics

---

## 2. What We Need from Upstream Primals

### 2.1 Critical: NestGate Liveness

**Priority: HIGH**. hotSpring's provenance pipeline (`dag_provenance.rs`, `receipt_signing.rs`) is wired for NestGate `content.put`/`content.get`/`content.hash` but cannot be live-validated until NestGate deploys. This blocks:
- DAG provenance chain validation
- Content-addressed experiment result storage
- BLAKE3 hash verification pipeline

**Ask**: NestGate team — deploy a minimal content-hash endpoint so springs can validate their provenance pipelines.

### 2.2 coralReef Sovereign Middleware Rebuild

hotSpring's sovereign GPU experiments use coral-era socket paths (`/run/coralreef/ember-*.sock`, `/run/coralreef/glowplug.sock`). We've evolved to env-var discovery (`TOADSTOOL_RUN_DIR`, `TOADSTOOL_GLOWPLUG_SOCKET`) but the underlying middleware needs the coralReef SM rebuild to ship. Phase C execution plan documented in `wateringHole/handoffs/HOTSPRING_PHASE_C_EXECUTION_PLAN_MAY12_2026.md`.

**Ask**: coralReef team — confirm toadStool socket path conventions so we can finalize discovery helpers.

### 2.3 bearDog Wire Name Confirmation

hotSpring corrected `crypto.sign_ed25519` parameters from `{"payload", "encoding", "algorithm"}` to `{"message" (base64), "purpose"}` based on ludoSpring's findings. We believe this matches bearDog's `handle_sign_ed25519` implementation.

**Ask**: bearDog team — confirm the canonical parameter schema for `crypto.sign_ed25519` so all springs use identical wire format.

### 2.4 Songbird Canonical Method Names

hotSpring routes `monitoring.*` capabilities to Songbird. Wire names used: `monitoring.report_measurement`, `monitoring.report_anomaly`.

**Ask**: Songbird team — confirm these are the canonical method names in your JSON-RPC handler registry.

---

## 3. What River Delta Springs Should Absorb

### 3.1 For All Springs

| Pattern | Where to Find It | Why |
|---------|-------------------|-----|
| `call_by_capability()` IPC | `barracuda/src/composition.rs` | Unified discovery + transport, zero hardcoded paths |
| `ValidationHarness` + exit codes | `barracuda/src/validation/harness.rs` | Consistent pass/fail/skip semantics |
| `ScenarioRegistry` | `barracuda/src/validation/scenarios/registry.rs` | Declarative scenario metadata with provenance |
| `OrExit<T>` trait | `barracuda/src/validation/harness.rs` | Zero-panic binary patterns |
| `#[expect(clippy::*, reason = "...")]` | Throughout crate | Rust 2024 lint idiom with documented reasons |
| Tolerance-driven validation | `barracuda/src/tolerances/` | Named constants, not magic numbers |
| env-var discovery for sockets | `barracuda/src/fleet_client.rs` | `ember_socket_candidates()`, `glowplug_socket_path()` |

### 3.2 For Springs with LTEE Reproductions

hotSpring's B2 Anderson fitness reproduction (`experiments/results/ltee/ltee_b2_anderson_expected.json`) feeds lithoSpore module 7 (`ltee-anderson`). The pattern: `expected_values.json` with tolerance fields, Python baseline notebook, Rust validation binary, BLAKE3 hash for lithoSpore ingestion.

### 3.3 For projectNUCLEUS

hotSpring workload TOMLs document the 3-tier compute ladder (CPU/GPU/sovereign) with resource requirements per tier. The pattern is reusable for any spring with heterogeneous compute.

---

## 4. Foundation Thread Contributions

| Thread | Status | Content |
|--------|--------|---------|
| **Thread 2** (Plasma/QCD) | ACTIVE | Sarkas Yukawa MD targets, Wilson plaquette, gradient flow, RHMC |
| **Thread 7** (Anderson RMT) | REFERENCED | Anderson localization analysis from B2 LTEE reproduction |

hotSpring does not currently contribute to Threads 4, 9, or 10 — those are outside our physics domain.

---

## 5. Composition Patterns for NUCLEUS Deployment via neuralAPI from biomeOS

### 5.1 Atomic Instantiation: Node Atomic (Proton)

The Node atomic composes: `crypto` (bearDog), `discovery` (Songbird), `compute` (BarraCuda + ToadStool), `math` (BarraCuda), `shader` (coralReef).

Validated via `s_node_atomic` scenario in UniBin registry:
- 5 domain composition checks (crypto, discovery, compute, math, shader)
- Tower superset verification (Node ⊂ Tower for all domains)
- Standalone behavior validation (no live primals required)
- SEMF binding energy + Wilson plaquette science baselines

### 5.2 Deploy Graph → neuralAPI

The deploy graph (`graphs/hotspring_*_deploy.toml`) defines the NUCLEUS composition. biomeOS reads the graph, spawns primals in dependency order, and exposes the composed niche via neuralAPI. hotSpring's `hotspring_unibin serve` registers with biomeOS and advertises capabilities.

The full deployment path: `plasmidBin` packages → biomeOS graph instantiation → neuralAPI exposure → external consumers call `capability.call` with domain routing.

### 5.3 plasmidBin Readiness

`scripts/harvest-ecobin.sh` builds `hotspring_unibin` and generates `metadata.toml` with all 5 UniBin modes. Checksums validate via SHA256. The binary is ecoBin-compliant (zero C deps on default, `deny.toml` enforced).

---

## 6. Deep Debt Audit Summary (All Clean)

| Dimension | Status | Details |
|-----------|--------|---------|
| TODO/FIXME/HACK | **ZERO** | No markers in library or binary code |
| Modern Rust | **CLEAN** | `#![forbid(unsafe_code)]`, `#![deny(clippy::unwrap_used)]`, zero clippy |
| External deps | **CLEAN** | Zero C deps on default build; `deny.toml` bans 12 categories |
| Large files | **OK** | 17 files >800L are bin targets; library max is `niche.rs` (846L) |
| Unsafe | **MINIMAL** | 2 files, both feature-gated (`low-level`, `cuda-validation`) |
| Hardcoding | **EVOLVED** | All socket/sysfs/proc paths use env-var discovery |
| Mocks | **ZERO** | All test-only (`#[cfg(test)]`) |

---

## 7. Metrics

| Metric | Value |
|--------|-------|
| Lib tests (default) | 592 |
| Lib tests (barracuda-local) | 1,041 |
| Binaries | 167 |
| Validation scenarios | 17 default / 20 barracuda-local |
| WGSL shaders | 128 |
| Deploy graphs | 7 |
| Papers reproduced (CPU) | 25/25 |
| Papers reproduced (GPU) | 20/25 |
| Clippy warnings | 0 |
| guideStone level | L6 CERTIFIED |
| Experiments | 190 |

---

## 8. Open Items (Not Blockers — Evolution Candidates)

1. **25 binaries use `panic!`** in unrecoverable paths — evolution to `Result` mains is polish, not debt.
2. **5 GPU papers** awaiting sovereign hardware validation (Titan V FECS, K80 livepatch — active research).
3. **NestGate not live** — provenance pipeline wired but cannot be end-to-end validated.
4. **coralReef SM rebuild** — sovereign middleware cutover path documented, awaiting upstream.
5. **LTEE B6-B9** — remaining paper queue items for lithoSpore, bandwidth-permitting.

---

**Handoff complete.** primalSpring may audit at will. All changes pushed via SSH.
