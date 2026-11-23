# cellMembrane Wave 157k Deep Debt Sweep — Aug 13, 2026

**Author:** overwatch (eastGate)
**Scope:** cellMembrane deep debt, I/O visibility, dead code purge, structural refactor
**Commit:** `d6a56b3` (pushed to golgiBody)
**Tests:** 1355 PASS, 0 FAIL, 0 clippy warnings

---

## Changes

### I/O Visibility (15 production `let _ =` → logged errors)

All remaining production `let _ =` on fallible I/O operations replaced with
`if let Err(e)` + `tracing::debug!` or `tracing::warn!`:

- **plasmid/build.rs**: Post-build clone directory cleanup
- **plasmid/harvest.rs**: Post-harvest source directory cleanup
- **plasmid/harvest_install.rs**: Temp file removal after failed rename
- **plasmid/canary.rs**: Pre-promote + post-kill socket cleanup (2 sites)
- **plasmid/sandbox.rs**: Pre-spin-up socket cleanup + teardown socket/binary (3 sites)
- **plasmid/download.rs**: Partial download cleanup + atomic_write rollback (3 sites)
- **plasmid/fetch.rs**: Pre-fetch binary removal + verification-failed binary removal (2 sites)
- **gate/wg.rs**: WG private key permissions → `tracing::warn!` (security-critical)
- **jsonrpc.rs**: Notify writer shutdown

### Dead Code Purge

5 zero-caller manifest API methods deleted:
- `gate_local_paths()` — no callers (definition-only)
- `repos_by_membrane()` — no callers
- `github_clone_url()` on `EcosystemManifest` — duplicate of `enroll.rs::github_clone_url()`
- `is_build_authority()` — distinct from `post_sync_content::is_build_authority()`
- `is_primary_build_authority()` — no callers

`WaveFile` dead_code narrowed from struct-level to field-level (only `gates` field unread).

### Annotation Hygiene

6 bare `#[allow(deprecated)]` now carry `reason` strings:
- `cytoplasm.rs`: 4 MESH_REGISTRY wrapper functions
- `sync_engine.rs`: REGENERABLE_METADATA includes deprecated FRESHNESS_FILE

### Smart Refactor: arch module extraction

Deprecated `TargetArch` legacy shim extracted from `arch.rs` (675L) to `arch/legacy.rs` (210L):
- `arch/mod.rs`: 478L (Platform, TargetOs, CpuArch, LinkModel, is_gpu_primal)
- `arch/legacy.rs`: 210L (TargetArch enum + impls + ArchParseError + tests)
- All types re-exported seamlessly via `pub use legacy::*`

### Clippy Fixes

`depot_sync.rs` `record_lineage_event`:
- Moved `use std::io::Write` to top of function (items-after-statements)
- Inlined `{entry}` format arg (uninlined-format-args)
- Replaced `let _ = writeln!` with error-logging write

### Root Docs Updated

- **README.md**: Wave 157g → 157k, test count 1353 → 1355, mesh 10-gate → 11-gate,
  `arch.rs` → `arch/` in repo structure
- **IRONGATE_VERIFICATION.md**: Wave 157g → 157k, test count updated
- **RUNBOOKS.md**: Fossil deploy_membrane.sh commands replaced with `membrane` CLI
  equivalents in sections 6 (Deployment), 8 (Credentials), 9 (SSH Keys), 10 (Emergency)
- **GLACIAL_SHIFT_TRACKER.md**: Wave 157k entry added
- **VPS_STATE.md**: Updated timestamp + test count

---

## Codebase Health

| Metric | Value |
|--------|-------|
| Tests | 1355 PASS, 0 FAIL |
| Clippy warnings | 0 new (pre-existing: doc backticks, format!, const fn) |
| `unsafe` code | 0 (`#![forbid(unsafe_code)]`) |
| `TODO`/`FIXME`/`HACK` | 0 |
| Production `unwrap()` | 0 |
| Files >800L | 0 |
| Largest file | `constants.rs` (739L) |

## What's Not In This Sweep

- **`native_braid.py` → Rust**: Wave 157k lists this as "last major jelly" (1,259 LOC Python).
  File is NOT in cellMembrane repo — it's in westGate/wateringHole scope.
- **Specs update**: `FIELDMOUSE_CONTRACT.md` and `RELAY_TRUST_BOUNDARY.md` still reference
  pre-Wave 120 pepti topology. These need revision but are not code debt.
- **Constants pruning**: 20 constants are definition-only (declared but zero consumers in
  this repo). Most are reserved env vars for external primals — intentional API surface.

---

*Downstream: primalSpring will audit via cascade.*

---
*FOSSILIZED Wave 157k interstadial (Aug 14, 2026). Content absorbed into ortho/blurb or implemented in code.*
