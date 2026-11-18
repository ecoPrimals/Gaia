# SPDX-License-Identifier: AGPL-3.0-or-later

# ludoSpring V68 — Tier 2 Wire Contract Alignment Handoff

**Date:** May 13, 2026
**From:** ludoSpring (game science composition)
**To:** primalSpring (coordination), toadStool, barraCuda, projectNUCLEUS
**Status:** V68 — 858 tests, zero clippy, zero unsafe, 9 validation scenarios

---

## Executive Summary

ludoSpring has aligned its Tier 2 IPC wiring to match the canonical wire
contract in `primalSpring/docs/LIVE_SCIENCE_API.md`. The V67 implementation
(functionally correct but using draft params) is now structurally aligned
with the upstream response schemas.

---

## What Changed (V67 → V68)

### 1. `toadstool.validate` — Param Alignment

**Before (V67):**
```json
{ "workload": "<toml-body>", "requester": "ludospring" }
```

**After (V68, matches LIVE_SCIENCE_API.md):**
```json
{ "workload_path": "/path/to/workload.toml", "dry_run": true }
```

Capability call routes to `toadstool.validate` (was `compute.validate`).

### 2. `barracuda.precision.route` — Param + Response Alignment

**Before (V67):**
```json
Params: { "operation": "...", "input_precision": "f64", "requester": "ludospring" }
Response: { "tier": 7, "hardware_hint": "compute", "requires_compiler": false }
```

**After (V68, matches LIVE_SCIENCE_API.md):**
```json
Params: { "domain": "game_science", "hardware_hint": "compute" }
Response: { "recommended_tier": "DF64", "fma_safe": true, "requires_compiler": false, "hardware_hint": "compute" }
```

### 3. `toadstool.list_workloads` — New Function

```json
Params: { "filter": "active" }
Response: { "workloads": [...], "total": N }
```

### 4. Type Extraction — `tier2_types.rs`

`WorkloadValidation` and `PrecisionAdvice` extracted from `toadstool.rs`
(822→692 LOC) into a dedicated `ipc/tier2_types.rs` module. Re-exported
from `toadstool` for backwards compatibility.

### 5. `PRIMAL_PROOF_IPC_MAPPING.md` Created

Full mapping of every ludoSpring domain operation to its JSON-RPC IPC
equivalent — 6 domain tables + precision strategy + graceful degradation.

### 6. musl Static Build Verified

```
ludospring: ELF 64-bit LSB pie executable, x86-64, static-pie linked
Size: 4.3 MB
Runs: version, validate --list (standalone, no libc)
```

---

## For primalSpring (Coordination)

- ludoSpring is at **Tier 4 IPC-first** with **Tier 2 upstream wire alignment**.
- All params now match `LIVE_SCIENCE_API.md` schemas.
- The V67 handoff remains the central reference for the V64→V67 evolution arc.
- This V68 handoff is a **contract alignment** delta only.
- ludoSpring declares its **evolutionary ceiling** — no further structural
  evolution needed until coralReef FECS ships (GAP-01 auto-resolves).

## For toadStool

- We call `toadstool.validate` with `{ "workload_path", "dry_run" }`.
- We call `toadstool.list_workloads` with `{ "filter" }`.
- Both degrade gracefully to `unavailable` structs when toadStool is not live.
- **Discovery:** `NOTE` — the doc says `barracuda.precision.route` is "NOT
  IMPLEMENTED" in the status table but the blurb says it IS. One is stale.

## For barraCuda

- We call `barracuda.precision.route` with `{ "domain", "hardware_hint" }`.
- Domain values we'll query: `game_science`, `procedural_noise`,
  `interaction_laws`, `engagement_metrics`.
- We expect: `recommended_tier` (string), `fma_safe` (bool),
  `requires_compiler` (bool), `hardware_hint` (string echo).

## For projectNUCLEUS

- Two workload TOMLs (`ludospring-game-validation.toml`,
  `ludospring-composition-parity.toml`) have `--format json` and `[output]`
  section for Tier 2 ingestion.
- musl binary is verified and harvestable — when plasmidBin adds spring
  binaries (currently not in `sources.toml` per "springs not distributed"),
  ludoSpring is ready.

---

## Remaining Gaps (No Action Needed)

| Gap | Owner | Status |
|-----|-------|--------|
| GAP-01: coralReef IPC | coralReef | WIRED, blocked on FECS stability |
| GAP-04: TensorSession expansion | ludoSpring | Partial, low priority |
| GAP-14: Tick model stress | primalSpring | LOW, deferred |

---

## Deep Debt Status: CLEAN

- Zero `unsafe` code (crate-level `#![forbid(unsafe_code)]`)
- Zero `#[allow()]` without `reason` attribute
- Zero TODO/FIXME/HACK/DEBT markers in active code
- Zero mocks in production (all in `#[cfg(test)]` only)
- Zero `unimplemented!()`/`todo!()` in any code path
- Zero files over 800 LOC (max: 747)
- Zero bare `Result<_, String>` — all typed errors
- Zero external non-Rust deps in default build (`signal-hook` = platform layer, `wgpu` = GPU-only feature)
- All `barracuda::` library calls gated behind `#[cfg(feature = "local")]`
- `default = []` — pure IPC-only build is the standard path

---

## Patterns for Sibling Springs

ludoSpring's Tier 2 alignment pattern is replicable:

1. Read `primalSpring/docs/LIVE_SCIENCE_API.md` for exact params/responses
2. Align your `validate_workload()` to `{ "workload_path", "dry_run" }`
3. Align your `precision_route()` to `{ "domain", "hardware_hint" }`
4. Add `list_workloads()` for workload enumeration
5. Create `PRIMAL_PROOF_IPC_MAPPING.md` documenting your domain→IPC map
6. Verify musl static build produces a standalone binary
