# cellMembrane Wave 155b — Cross-Platform NUCLEUS + Fleet Convergence

**Date**: 2026-07-27 | **Wave**: 155b | **Author**: cellMembrane team (sporeGate)
**Trigger**: G1 (Tower on Windows) + Track B Fleet Convergence

---

## Summary

**Cross-platform NUCLEUS**: `nucleus.rs` evolved from systemd-only to
`InitSystem::detect()` dispatch — systemd unit generation on Linux, bare process
spawn with PID file tracking on Windows/macOS/containers. This is the G1
dependency for Tower Atomic on Windows (blueGate).

**Fleet convergence**: Checksum verification fix enables all depot formats
(struct + plain-string) to parse correctly. Topology updated for blueGate +
westGate. Build authority foreman pattern verified.

## Changes

### 1. Cross-Platform NUCLEUS (G1 — P0)

`nucleus.rs` dispatches on `InitSystem::detect()`:

| Platform | Init System | Strategy |
|----------|-------------|----------|
| Linux (systemd) | `Systemd` | Unit files + `systemctl enable --now` (existing) |
| Windows | `WindowsSCM` | Bare process spawn + PID files |
| macOS | `Launchd` | Bare process spawn + PID files |
| Containers | `Bare` | Bare process spawn + PID files |

New functions:
- `start_nucleus_bare()` — spawn each primal, write `{install_base}/pids/{binary}.pid`
- `stop_bare_process()` — read PID file, SIGTERM (Unix) / `taskkill` (Windows)
- `restart_bare_process()` — stop, wait, respawn from current depot binary
- `prepare_socket_base()` / `resolve_security_socket()` — extracted shared helpers
- `load_env_file()` — parse `secrets.env` for bare process environment

`systemctl()` and `systemctl_async()` now guard with `InitSystem::detect()` and
trace-warn on non-systemd platforms (previously would fail silently).

### 2. Cascade Restart Cross-Platform

`nucleus_restart.rs` refactored:
- `converge_primal()` extracted (was monolithic 105-line function)
- `ConvergeOutcome` enum replaces manual counter manipulation
- `sandbox_validate()` extracted for clarity
- Restart path dispatches on `InitSystem` — systemd `restart` vs `restart_bare_process()`

### 3. Crash-Loop Guard

`crash_loop.rs` `discover_membrane_units()` now early-returns on non-systemd
platforms. Previously would attempt `systemctl list-units` which fails on Windows.

### 4. Dead Code Cleanup

`verify.rs` — removed orphaned `ChecksumFile` and `ChecksumEntry` structs that
were left after the `parse_checksums_toml()` migration. Also cleaned up test-only
struct definitions.

### 5. Checksum Format Fix (P0)

`gate/verify.rs` migrated to shared `parse_checksums_toml()` from
`plasmid/checksum.rs` — handles both `{ blake3, size }` struct and plain-string
`"hash"` formats.

### 6. Topology (blueGate + westGate)

Both added to `MESH_REGISTRY`, `KNOWN_GATES`, zone fallbacks. WG IPs pending.

## Changed Files

| File | Change |
|------|--------|
| `gate/nucleus.rs` | `InitSystem` dispatch, bare process manager, PID files, `stop`/`restart` |
| `temporal/nucleus_restart.rs` | `converge_primal()` extraction, `ConvergeOutcome`, cross-platform restart |
| `gate/crash_loop.rs` | `InitSystem` guard on `discover_membrane_units()` |
| `gate/verify.rs` | Dead code cleanup, test migration to shared parser |
| `gate/enroll.rs` | Clippy fix (uninlined format args) |
| `plasmid/checksum.rs` | `parse_checksums_toml` promoted to `pub(crate)` |
| `plasmid/mod.rs` | `checksum` module promoted to `pub(crate)` |
| `cytoplasm.rs` | blueGate + westGate topology |

## Health Metrics

| Metric | Value |
|--------|-------|
| Tests | 1,182 (was 1,175) |
| Clippy warnings | 0 |
| Files >800L | 0 (largest: 781L nucleus.rs) |
| Production unwrap | 0 (476 test-only) |
| Unsafe code | 0 (`#![forbid(unsafe_code)]`) |
| TODO/FIXME/HACK | 0 |

## Deep Debt Audit

Full codebase scan confirms:
- Zero production `.unwrap()` — all 476 in test modules
- Zero `unsafe` — `#![forbid(unsafe_code)]` on both crates
- Zero TODO/FIXME/HACK markers
- Zero files over 800 lines
- All hardcoded IPs are in `MESH_REGISTRY` const table (manifest fallback)
- All hardcoded binary names in production are protocol/display constants
- 10 production `.expect()` calls — all on infallible HMAC-SHA256 init (correct)

## For eastGate Overwatch

cellMembrane Wave 155b: **DONE**. Cross-platform NUCLEUS unblocks G1 (Tower on
Windows). blueGate can now run NUCLEUS via bare process spawn — `gate.bootstrap`
will use `start_nucleus_bare()` on Windows. Cascade restart handles non-systemd
restart via PID files. Checksum fix unblocks all depot formats. blueGate/westGate
topology known but need WG IP allocation.

**What we need from primal teams:**
- songBird: Confirm `universal-ipc` named pipe path on blueGate Windows
- bearDog: Confirm BTSP handshake works over Windows named pipe (not just UDS)
- nestGate: G4 Windows CAS path resolution (NTFS considerations)
