# lithoSpore Wave 60 — Typed Errors, Chassis Purity, Dep Trimming

**Date:** May 28, 2026
**From:** lithoSpore
**To:** primalSpring coordination, upstream primal teams
**Commits:** `1b34d6a..35fe3b5`

---

## Summary

Wave 60 introduces the `LithoError` typed error hierarchy for `litho-core`,
restores chassis purity by removing LTEE-specific constants, trims unused
dependencies, and aligns all documentation to current codebase state.

---

## Changes

### 1. `LithoError` typed error hierarchy (NEW)

`litho-core/src/error.rs` — `thiserror`-based enum with 5 variants:

| Variant | Covers |
|---------|--------|
| `Io { path, source }` | File read failures in loaders |
| `Parse { path, detail }` | TOML/JSON parse failures |
| `Serialize` | `serde_json::Error` (from format_output) |
| `Discovery` | Capability discovery failures |
| `Rpc { method, detail }` | JSON-RPC call failures |

**Migrated public APIs:**

| API | Before | After |
|-----|--------|-------|
| `ScopeManifest::load` | `Box<dyn Error>` | `LithoError` |
| `DataManifest::load` | `Box<dyn Error>` | `LithoError` |
| `ToleranceSet::load` | `Box<dyn Error>` | `LithoError` |
| `harness::format_output` | `Result<_, String>` | `Result<_, LithoError>` |
| `provenance::try_record_tier3` | `Result<_, String>` | `Result<_, LithoError>` |

All internal RPC helpers (`rpc_call_extract`, `rpc_call_result`) also migrated.

### 2. Chassis purity restored

`E_COLI_K12_MG1655_BP` and `LTEE_N_POPULATIONS` moved from `litho-core`
to domain crates:
- `ltee-breseq/src/lib.rs` (pub, imported by `ltee-cli/viz/baselines.rs`)
- `ltee-anderson/src/lib.rs` (local const)

`litho-core` now has **12 modules** and zero LTEE science logic in source.

### 3. Dependency trimming

- Removed unused `serde_json` from `ltee-fitness/Cargo.toml`
- Removed unused `serde_json` from `ltee-biobricks/Cargo.toml`
- Removed dead `#[derive(serde::Serialize)]` and unused `k`/`rss` fields
  from `ltee-fitness::ModelFit`
- Added `thiserror` to `litho-core/Cargo.toml` (workspace dep, already present)

### 4. Hardcoding fix

`discovery.rs` `/tmp` XDG fallback → `std::env::temp_dir()` for portability.

### 5. Previous wave (same session)

`1b34d6a` centralized LTEE constants, completed SporeError migration for
`check_livespore_unified`, added `VISUALIZATION_SOCKET`/`PETALTONGUE_SOCKET`
to env_vars (now 20 constants), eliminated unnecessary clones in baselines.rs
and manifest.rs.

### 6. Documentation sync

7 docs updated:
- `ARCHITECTURE.md`: 12 modules, `error.rs` in crate tree, softened claims
- `UPSTREAM_GAPS.md`: LS-6 corrected (thiserror in use, not removed)
- `MODULES.md`: test breakdown corrected (pseudospore-core 45, ltee-cli 58)
- `DEGRADATION_BEHAVIOR.md`: `LithoError` signature
- `experiments/README.md`: Exp 012 added to table, Exp 017 status updated
- `SCIENCE.md`: 82,500+ generations aligned with README
- `whitePaper/baseCamp/README.md`: 12 modules
- `README.md`: crate tree includes `error`

---

## Metrics

```
192 tests             — unchanged
0 clippy warnings     — unchanged
0 cargo deny issues   — unchanged
12 litho-core modules — was 11 (added error.rs)
20 env var constants  — was 18 (added VISUALIZATION_SOCKET, PETALTONGUE_SOCKET)
0 Box<dyn Error>      — was 3 (scope, manifest, tolerance)
0 Result<_, String>   — was 2 public APIs (format_output, try_record_tier3)
```

---

## NC-5 Status

**UNBLOCKED.** No changes to emission path. Code surface ready.
Gated on biomeOS v3.84 VPS deploy + 2 spring column U passes.

---

## Upstream notes for primalSpring

- `litho-core` public API now returns `LithoError` instead of `Box<dyn Error>`
  or `String`. Consumers using `.ok()` need no changes. Consumers using `?`
  need `From<LithoError>` or match on variants.
- `E_COLI_K12_MG1655_BP` and `LTEE_N_POPULATIONS` are no longer in
  `litho_core::` — they live in `ltee_breseq::` and local module constants.
- `thiserror` is now a production dependency of `litho-core` (was previously
  only in `pseudospore-core`).

---

*Wave 60. Typed errors. Chassis clean. Deploy the ecosystem.*
