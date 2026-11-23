# hotSpring v0.6.32 — Niche Convergence → Atomic Deployment Handoff

**Date:** May 13, 2026
**From:** strandGate (hotSpring)
**To:** primalSpring coordination, biomeGate team, upstream primal teams
**Trigger:** Delta Spring Directive — Niche Convergence → Atomic Deployment (May 13, 2026)

---

## Summary

This sprint addresses the directive's hotSpring-specific targets: wire name
hygiene, Node atomic deployment path, and plasmidBin readiness. All changes
are verified with zero clippy warnings across both feature sets.

## Changes Made

### 1. bearDog Wire Name Hygiene (FIXED)

**Problem:** `receipt_signing.rs` used `{"payload": ..., "encoding": "utf8",
"algorithm": "Ed25519"}` params for `crypto.sign_ed25519`. bearDog's upstream
handler expects `{"message": <base64>}`.

**Fix:** Corrected to `{"message": base64(receipt_json), "purpose": "receipt"}`.
Also fixed `validate_nucleus_tower.rs` to base64-encode its probe message.

**`skunkBat` verified:** Already uses `security.audit_log` — matches upstream.
No fix needed.

### 2. base64_encode Extraction

The inline base64 encoder in `dag_provenance.rs` was extracted to
`src/base64_encode.rs` (shared crate module). Used by:
- `dag_provenance.rs` (merkle root signing)
- `receipt_signing.rs` (receipt signing)
- `validate_nucleus_tower.rs` (probe message encoding)

### 3. s_node_atomic Validation Scenario (NEW)

Created `src/validation/scenarios/s_node_atomic.rs` — registered in the
UniBin `validate` registry. 15 checks covering:
- Node domain composition (5 domains: crypto, discovery, compute, math, shader)
- Tower superset property
- Standalone behavior (zero primals → not passed, all missing)
- SEMF Pb-208 baseline (finite, range)
- Lattice plaquette baseline (finite, positive, range)

This provides the UniBin `validate` path for Node atomic. The live
validation path remains `validate_nucleus_node` (standalone binary) which
exercises actual primal IPC.

### 4. Harvest Script Update

`scripts/harvest-ecobin.sh` updated from retired `hotspring_primal` to
`hotspring_unibin`. All five UniBin modes registered: certify, validate,
serve, status, version.

### 5. Clippy Resolution (8 errors)

| Lint | File | Fix |
|------|------|-----|
| `too_long_first_doc_paragraph` | `compute_dispatch.rs` | Split doc into paragraphs |
| `if_not_else` | `toadstool_report.rs` | Swapped branches |
| `bool_to_int_with_if` | `validation/harness.rs` | `i32::from(!)` |
| `manual_let_else` + `single_match` | `s_hotqcd_dispatch.rs` | `let Ok(..) else` |
| `map_unwrap_or` | `bench/report.rs` | `map_or_else` |
| `unwrap_used` (×2) | `s_gradient_flow.rs` | Index access |

---

## Metrics

| Metric | Value |
|--------|-------|
| Tests (default) | 592 |
| Tests (barracuda-local) | 1,041 |
| Clippy warnings | 0 (both feature sets) |
| Scenarios (default) | 17 |
| Scenarios (barracuda-local+sovereign) | 20 |
| Experiments | 190 |

---

## Node Atomic Deployment Status

The `validate_nucleus_node` binary is the live validation path. It checks:
- ToadStool `compute.capabilities` + `compute.dispatch.submit`
- coralReef `shader.list` + `shader.compile.wgsl`
- SEMF parity (local Rust vs IPC)
- Lattice plaquette parity (local Rust vs IPC)
- Standalone fallback when no primals discovered

**What's needed for live validation pass:**
1. All Node domain primals running: bearDog, songBird, toadStool, barraCuda, coralReef
2. `NucleusContext::detect()` must discover non-empty nucleus
3. Each primal must respond to `health.liveness`
4. Science parity: IPC results within tolerance of local Rust baselines

**hotSpring team split:**
- **biomeGate:** Sovereign dispatch (FECS, kernel-level) — Titan V warm-catch, K80 livepatch
- **strandGate:** AMD + NVIDIA hardware validation, Node atomic deployment proof

---

## Upstream Primal Interactions

| Primal | Wire Method | Status |
|--------|------------|--------|
| bearDog | `crypto.sign_ed25519` (`message` base64) | FIXED (was `payload`) |
| skunkBat | `security.audit_log` | Verified correct |
| toadStool | `compute.capabilities`, `compute.dispatch.submit` | Wired via `by_domain` |
| coralReef | `shader.list`, `shader.compile.wgsl` | Wired via `by_domain` |
| nestGate | Not yet wired (deployment-only gap) | Upstream blocked |
| songBird | `discovery.find_primals` | Wired |

---

## Foundation Thread Coverage

hotSpring contributes to:
- **Thread 2** (Plasma/QCD): Fully active
- **Thread 7** (Anderson RMT): Active via LTEE B2 reproduction

Threads 4 (enviro genomics), 9 (gaming), 10 (provenance) are outside
hotSpring's domain. No action needed.

---

## plasmidBin Readiness

- `harvest-ecobin.sh` now builds `hotspring_unibin` (x86_64 + optional aarch64)
- `metadata.toml` references `hotspring_unibin` with all 5 modes
- b3sum checksums computed when `b3sum` is available
- `CHECKSUMS` file lists 15 source/script paths (binary hashes generated at harvest time)

---

## Remaining Gaps

1. **Node atomic live validation** — needs all Node domain primals running locally.
   Binary exists (`validate_nucleus_node`). Scenario exists (`s_node_atomic`).
   Gap is deployment, not code.
2. **NestGate content pipeline** — not wired in hotSpring (deployment-only gap).
   Documented in GAP-HS-082.
3. **Sovereign GPU niche** — FECS warm dispatch and K80 livepatch are active
   research (biomeGate team), not blockers. Documented in GAP-HS-073/076/093.
