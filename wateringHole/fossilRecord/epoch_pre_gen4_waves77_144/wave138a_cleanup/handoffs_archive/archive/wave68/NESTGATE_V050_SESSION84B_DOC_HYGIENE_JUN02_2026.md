# NestGate v0.5.0 — Session 84b: Doc Hygiene + Debris Cleanup

**Date**: 2026-06-02
**Wave**: 69 maintenance mode
**Status**: Stable, all tests green, zero clippy warnings

## Root Doc Sync (9 files)

All root markdown files synchronized to Session 84 ground truth:
- **Session/date**: `Jun 2, 2026 (Session 84)` across all files
- **Test count**: `12,522+` (was stale at `12,500+`)
- **Coverage**: Unified to `84%` (resolved `83.61%` vs `84.12%` contradiction)
- **Socket examples**: `/tmp/nestgate.sock` replaced with `$XDG_RUNTIME_DIR/nestgate.sock`
- **Workspace count**: Corrected `23` → `22` members (`tools/` removed in prior session)
- **Last Updated date conflict**: README.md `May 25` → `Jun 2`

## Archived to Git History (Fossil Record)

Removed from HEAD, preserved in git history:

| Item | Files | Reason |
|------|-------|--------|
| `config/` | 3 files | Stale templates (Consul/K8s/NFS references, not loaded by code) |
| `graphs/` | 4 files | biomeOS deploy graphs with BearDog/Songbird primal names |
| `scripts/` | 1 file | Machine-specific test substrate setup (not in CI) |
| `specs/` | 15 files | Pre-evolution design specs (Songbird/BearDog/Consul delegation) |
| `tests/common/config/` | 1 file | Empty stub module with no consumers |

**Total**: 24 files archived. Git history preserves full content for fossil record.

## Doc Fixes

- `TROUBLESHOOTING.md`: Replaced mDNS/Consul discovery section with capability-based IPC
- `ECOSYSTEM_INTEGRATION_GUIDE.md`: Replaced dead `./scripts/test-live-integration.sh` with `cargo test`
- `DOCUMENTATION_INDEX.md`: Removed references to archived dirs, updated tree diagram
- `DOCS_QUICK_GUIDE.md`: Fixed workspace member count (23 → 22)
- `tests/common/mod.rs`: Removed dead `pub mod config;` declaration

## Metrics

- **Tests**: 12,522+ (unchanged — no code changes, only docs/debris)
- **Clippy**: 0 warnings
- **Build**: Clean workspace-wide

## Remaining Doc Debt (for upstream review)

- `CAPABILITY_MAPPINGS.md`: Still contains BearDog/Songbird/ToadStool examples in capability discovery section — these are illustrative but use hardcoded primal names
- `docs/api/REST_API.md`: BearDog security examples in API docs
- `docs/architecture/PRIMAL_SOVEREIGNTY.md`: Teaching doc with Songbird/BearDog env var examples
- Several `docs/integration/biomeos/` files: Historical socket standardization with old primal names
- `docs/guides/LOCAL_TESTING_GUIDE.md`, `ZERO_COST_ARCHITECTURE_GUIDE.md`: Reference removed benchmark targets
