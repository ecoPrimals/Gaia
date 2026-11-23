# projectFOUNDATION — Wave 76 Deep Debt: Typed Errors & Display Evolution

**Date:** June 3, 2026
**Wave:** 76 (consolidation)
**Gate:** ironGate
**Repo:** `gardens/projectFOUNDATION`
**Commit:** `390b94b` (main)

## Delivered

### Typed Error Enums — Zero `Result<_, String>` in Workspace

All stringly-typed error paths replaced with structured `thiserror` enums:

| Crate | Before | After |
|-------|--------|-------|
| `foundation-fetch` | `Result<String, String>` × 2 methods, 6 `format!` error sites | `FetchError` enum: `Http`, `Io`, `FileTooSmall`, `Hash`, `RetriesExhausted`, `NoUrl` |
| `foundation-validate` | `Result<Output, String>` in process executor | `ProcessError` enum: `Spawn`, `Timeout`, `Wait` |

### `unreachable!()` Eliminated

`fetcher.rs:217` — removed via proper loop fallthrough with `last_error` accumulation.
Zero `unreachable!()`, `todo!()`, `unimplemented!()` remain in production.

### Display Impls on Report Structs

| Struct | Crate | Before | After |
|--------|-------|--------|-------|
| `DriftReport` | foundation-core | `summary() -> format!()` | `impl Display` + `summary()` delegates |
| `HealthTriad` | foundation-ipc | `summary() -> format!()` | `impl Display` |
| `CommitResult` | foundation-ipc | `summary() -> format!()+collect` | `impl Display` (zero-alloc) |
| `SessionStatus` | foundation-validate | `summary() -> format!()` | `impl Display` |

### Allocation Elimination

- Thread ID filter: `t.id.to_string() == *filter` → `filter.parse::<u32>() == Some(t.id)` (2 sites)
- Vec pre-sizing: `check_drift` uses `Vec::with_capacity(springs + primals)`
- Silent `unwrap_or_default()` in IPC client: now emits `tracing::warn!` on missing field

## Metrics

| Metric | Wave 74 | Wave 76 |
|--------|---------|---------|
| Lines (Rust) | 8,391 | 9,179 |
| Tests | 170 | 173 |
| `Result<_, String>` | 2 functions | 0 |
| `unreachable!()` | 1 | 0 |
| `Display` impls on reports | 0 | 4 |
| Clippy warnings | 0 | 0 |
| Binary size | 3.2 MB | 3.1 MB |

## Repository State

- Zero unsafe in production (test-only with `#[expect(reason)]`)
- Zero TODO/FIXME/HACK in codebase
- Zero hardcoded literals (all centralized in `primal_names`, `env_keys`, `paths::conventions`, `methods`, `urls`)
- All files under 453 lines (limit: 1000)
- AGPL-3.0 + ORC + CC-BY-SA 4.0 triple license

## Phase C Remaining (Unchanged)

1. NestGate content registration (wire IPC)
2. toadStool workload dispatch (wire IPC)
3. Full `ProvenanceSession` trio commit
4. `backfill --write` TOML mutation
5. Database-specific fetch orchestration
6. sporePrint notify trigger from `publish`
7. Bidirectional Forgejo mirror

## For Upstream Teams

- **primalSpring**: Foundation typed errors provide structured context for composition
  validation. `FetchError::Http { url, source }` and `ProcessError::Timeout { timeout_secs }`
  are now machine-parseable in validation reports.
- **guideStone**: Boundary spec updated for Wave 76 trust infrastructure (bearDog w135,
  NestGate s90). Shared lineage schema includes optional `[record.trust]` section.
- **projectNUCLEUS**: No interface changes. Foundation remains validation-side only.

## No Archive Candidates

Reviewed full repository:
- `expressions/LTEE_EVOLUTION.md` — already marked "retained as fossil record"
- `specs/EVOLUTION_GAPS.md` — valid redirect stub to projectNUCLEUS canonical
- `validation/handbacks/archive/` — geological record (9 files), correctly archived
- `deploy/` bash scripts — still production-canonical until Phase C cutover
- All benchmarks active in CI

No debris, stale TODOs, or outdated scripts found.
