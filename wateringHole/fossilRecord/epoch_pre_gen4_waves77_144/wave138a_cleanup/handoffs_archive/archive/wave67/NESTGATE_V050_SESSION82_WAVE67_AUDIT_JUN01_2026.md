# NestGate v0.5.0 — Session 82: Wave 67 Audit Response (Jun 1, 2026)

## Wave 67 Assessment

NestGate has **no blockers** in the glacial cutover plan:

- **S3 Content serving**: NestGate + Caddy LIVE (67ms TTFB) — no code change needed
- **S4 Auth validation**: BTSP support already wired — validation env is an ops task
- **Content federation**: 4 methods shipped (Session 80) — ready for signal graphs
- **VPS deploy readiness**: v0.5.0 unified, all crates build, no code blockers
- **aarch64-musl**: Linker fix shipped (Session 76), needs hardware re-test (ops)

## Changes Made

### Critical: Version regression fix
- Upstream commits (`47066fbb`) removed `version = "0.5.0"` from `[workspace.package]`
  and set root `[package]` to `0.1.0` — broke all 21 crate builds
- Restored `version.workspace = true` on root + `version = "0.5.0"` on workspace

### DH-1: /tmp hardcoding removal
- `nestgate-fsmonitor/unified_fsmonitor_config/event_processing.rs`:
  - `queue.dat` and `dlq.dat` paths moved from `/tmp/` to XDG-compliant `fsmonitor_data_dir()`
- `nestgate-fsmonitor/unified_fsmonitor_config/storage.rs`:
  - backup location moved from `/tmp/fsmonitor_backup` to `fsmonitor_data_dir()/backup`
- New helper: `fsmonitor_data_dir()` — `$XDG_DATA_HOME/nestgate/fsmonitor` → `$HOME/.local/share/nestgate/fsmonitor` → `/var/lib/nestgate/fsmonitor`

### Coverage push: 27 new tests
- `federation_ops.rs` (12): git helpers, sync error paths, transport error paths
- `fsmonitor/event_processing.rs` (10): defaults, serialization, /tmp assertions
- `fsmonitor/security.rs` (5): defaults, path assertions, serialization

## Metrics
- **Tests**: 12,512 passing (up from 12,500)
- **Clippy**: 0 warnings
- **Build**: All 22 workspace crates compile at v0.5.0

## Remaining for downstream audit
- Coverage target 90% not reached (83.61%+)
- `nestgate-api/handlers/` has ~78 files without inline tests
- `nestgate-discovery/production_discovery.rs` (516L) untested
- `nucleus-aarch64-mixed-tcp` cell blocked on hardware re-test
