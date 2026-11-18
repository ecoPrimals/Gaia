# NestGate v0.5.0 — Session 89 Documentation & Debris Cleanup

**Date**: 2026-06-03
**Gate**: ironGate (eastGate)
**Primal**: nestgate v0.5.0
**Session**: 89

## Delivered

### Root Documentation Sweep (HIGH)

Canonical test counts established from fresh `cargo test` runs:

| Scope | Tests Passing |
|-------|--------------|
| `--workspace --lib` | 2,267 |
| `-p nestgate-rpc --lib` (RPC) | 747 |
| `--workspace` (full) | 3,732 |

All root markdown files updated from inflated/stale counts (previously claimed 12,522+):

- `README.md`, `STATUS.md`, `START_HERE.md`, `QUICK_START.md`, `QUICK_REFERENCE.md`
- `CONTEXT.md`, `CONTRIBUTING.md`, `CAPABILITY_MAPPINGS.md`, `DOCUMENTATION_INDEX.md`
- `sporeprint/validation-summary.md`
- `tests/README.md`, `tests/DISABLED_TESTS_REFERENCE.md`
- `docs/guides/DOCS_QUICK_GUIDE.md`, `docs/DEVELOPER_ONBOARDING.md`

Session references updated from "Session 84" → "Session 88" across 9 root docs.

### Broken `specs/` References (MEDIUM)

The `specs/` directory was referenced in 23 files but never existed on disk.
All references repointed to `capability_registry.toml` or `CAPABILITY_MAPPINGS.md`
as the living source of truth for method/capability declarations.

### `capability_registry.toml` Version Fix (MEDIUM)

- `version` corrected from `"4.7.0-dev"` to `"0.5.0"` matching workspace `Cargo.toml`

### Method Count Correction

- `CAPABILITY_MAPPINGS.md`: 68 UDS methods → 77 UDS methods (matches `UNIX_SOCKET_SUPPORTED_METHODS`)

## Metrics

- **3,732 tests** passing (workspace full, serial), 12 pre-existing env-race failures
- **2,267 tests** lib-only
- **747 RPC tests** (`nestgate-rpc --lib`)
- **0 clippy warnings**
- **23 files** updated (root docs, docs/, tests/, code/ crate READMEs)
- **All `specs/` references** eliminated (was 23 files)

## Known Issues

- 12 test failures in parallel execution: pre-existing environment variable race conditions
  in `nestgate-rpc` tests (pass with `--test-threads=1`)
- Previous test counts (12,522+) were significantly inflated; root cause unknown but likely
  a counting methodology error in earlier sessions

## Next

- Debris review: stale scripts, archive candidates
- `cargo clean` to reclaim build artifacts
- Cascade push for primalSpring audit
