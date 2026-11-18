# cellMembrane Wave 150x — Crash-Loop Breaker + Deep Debt Sweep

**Date:** 2026-07-24
**Wave:** 150x
**Author:** cellMembrane (sporeGate)
**Posture:** SERVICE CRASH-LOOP DIVERGENCE RESOLVED

---

## Context

Wave 150x revealed a systemd crash-loop divergence on eastGate:

| Service | Restarts | Rate | Cause |
|---------|----------|------|-------|
| `membrane-nucleus@nestgate` | 17,920+ | every 3s | Binary CLI evolved — `--socket` flag rejected (exit 2) |
| `biomeos-beacon` | 11,161+ | every 5s | Binary doesn't exist (exit 203) |

Combined ~890 restarts/hour ran for 15+ hours undetected. AT&T gateway throttled
eastGate for excessive outgoing connections from the rapid spawn churn.

**Root cause:** No primal detected or intervened. `Restart=always` + `RestartSec=3`
ran indefinitely with no crash-loop detection, no CLI contract validation, and no
resource anomaly detection.

---

## Deliverables

### 1. Crash-Loop Breaker (P0)

**Types** (`cellmembrane-types/src/process.rs`):
- `CrashLoopAction` enum: `Disabled`, `Logged`, `FailedToDisable`
- `CrashLoopEntry` struct: unit, restart_count, sub_state, action
- `CrashLoopReport` struct: loops, threshold, scanned + methods (`has_loops`, `disabled_count`)
- `CRASH_LOOP_RESTART_THRESHOLD` constant: 5 (default)

**Implementation** (`membrane-shadow/src/gate/crash_loop.rs`):
- `scan_and_break()` — sync variant for bootstrap/preflight contexts
- `scan_and_break_async()` — async variant for cascade/temporal contexts
- `scan_only()` — dry-run (report only, no disable)
- `discover_membrane_units()` — filters `systemctl list-units` by service registry
- `query_unit_restart_info()` — parses `NRestarts` and `SubState` via `systemctl show`
- `disable_unit()` / `disable_unit_async()` — `systemctl stop + disable`
- `format_report()` — human-readable summary

**Dispatch** (`membrane-shadow/src/dispatch/gate.rs`):
- New command: `membrane gate.crash-loop [--dry-run] [--threshold N]`
- Returns `CrashLoopReport` as JSON data with formatted summary

**Integration points:**
- `gate.status` health probes — adds `service.crash-loop` probe (scan_only)
- `temporal.cascade` post-sync — scans after restart, auto-disables crash-looping services

### 2. nestgate Service Unit Fix (P0)

**Problem:** nestgate binary CLI evolved and no longer accepts `--socket` flag.
Service template generated `ExecStart=/opt/membrane/nestgate server --socket /path`
which exits 2 on every attempt.

**Fix:**
- Added `ServerContract::ServerNoSocket` variant — generates `ExecStart=.../binary server`
  (socket path via env var / convention)
- Updated nestgate registry entry: `SocketOnly` → `ServerNoSocket`
- Updated sporePrint unit template: passes socket path via `NESTGATE_SOCKET` env var
- Updated tests to assert `--socket` is NOT present in nestgate units

---

## Changed Files

| File | Change |
|------|--------|
| `cellmembrane-types/src/process.rs` | `CrashLoopAction`, `CrashLoopEntry`, `CrashLoopReport`, threshold const, tests |
| `cellmembrane-types/src/lib.rs` | Re-export crash-loop types |
| `cellmembrane-types/src/service/mod.rs` | `ServerContract::ServerNoSocket` variant |
| `cellmembrane-types/src/service/registry.rs` | nestgate: `SocketOnly` → `ServerNoSocket` |
| `membrane-shadow/src/gate/crash_loop.rs` | **NEW** — crash-loop breaker module |
| `membrane-shadow/src/gate/mod.rs` | Register `crash_loop` module |
| `membrane-shadow/src/gate/health.rs` | Integrate crash-loop probe into `gate.status` |
| `membrane-shadow/src/gate/sporeprint.rs` | nestgate unit: `--socket` → env var |
| `membrane-shadow/src/dispatch/gate.rs` | `gate.crash-loop` command dispatch |
| `membrane-shadow/src/temporal/post_sync.rs` | Post-cascade crash-loop scan |
| `membrane-shadow/src/gate/nucleus.rs` | RestartSec=3→5, add StartLimitBurst |
| `membrane-shadow/src/provision/bootstrap.rs` | Restart=always→on-failure, burst limits |
| `deploy/systemd/*.service` (7 files) | Restart=always→on-failure, burst limits |
| `deploy/systemd/user/membrane-nucleus-nosocket@.service` | **NEW** — ServerNoSocket template |
| `membrane-shadow/src/manifest/tests.rs` | **NEW** — extracted 454L manifest tests |
| `membrane-shadow/src/webhook/tests.rs` | **NEW** — extracted 360L webhook tests |
| `cellmembrane-types/src/gateway_tests.rs` | **NEW** — extracted 462L gateway tests |
| `membrane-shadow/src/plasmid/harvest_tests.rs` | **NEW** — extracted 383L harvest tests |
| `membrane-shadow/src/manifest/mod.rs` | 785→333L after test extraction |
| `membrane-shadow/src/webhook/mod.rs` | 703→345L after test extraction |
| `cellmembrane-types/src/gateway.rs` | 833→371L after test extraction |
| `membrane-shadow/src/plasmid/harvest.rs` | 804→422L after test extraction |
| `cellmembrane-types/src/cytoplasm.rs` | `MESH_REGISTRY` + `lan_ip` field, `lan_address()` |
| `cellmembrane-types/src/lib.rs` | Re-export `lan_address` |

---

### 3. Systemd Restart=always Elimination (deep debt)

**Problem:** All systemd units used `Restart=always` + `RestartSec=3`, the exact
configuration that caused 17,920 restarts in 15 hours.

**Fix:** All units (code-generated and deploy templates) hardened:
- `Restart=always` → `Restart=on-failure` (only restart on non-zero exit)
- `RestartSec` standardized to 5s (was 3s in many places)
- Added `StartLimitIntervalSec=120` + `StartLimitBurst=10` (max 10 restarts per 2 min)

**Scope:** 12 files changed — 5 Rust-generated unit templates, 7 deploy templates.
Also added `membrane-nucleus-nosocket@.service` for `ServerNoSocket` primals.

---

## Health Metrics

| Metric | Value |
|--------|-------|
| Tests | 1,150 (was 1,136) |
| Clippy warnings | 0 |
| `cargo fmt` drift | 0 |
| Production `unwrap()` | 0 |
| `unsafe` blocks | 0 (`#![forbid(unsafe_code)]`) |
| Files >800L | 0 (zero files exceed 800L) |
| Test extraction | manifest 785→333L, webhook 703→345L, gateway 833→371L, harvest 804→422L |
| `Restart=always` units | 0 (was 8+ across codebase) |
| Disk reclaimed | 2.2 GiB (cargo clean) |

---

## Deep Debt Sweep (afternoon session)

### Hardcode elimination (7 locations)

| File | Old | New |
|------|-----|-----|
| `tower/timer.rs` | `"/run/membrane/beardog.sock"` | `DEFAULT_SOCKET_BASE` + `binary_for(CryptoSigner)` |
| `tower/timer.rs` | `"/run/membrane/skunkbat.sock"` | `DEFAULT_SOCKET_BASE` + `binary_for(Observability)` |
| `tower/timer.rs` | `.join("songbird")` | `binary_for(MeshRelay)` |
| `tower/timer.rs` | `"/etc/systemd/system/"` | `SYSTEMD_UNIT_DIR` |
| `gate/enroll.rs` | `"10.13.37.1"` | `mesh_address("golgi")` |
| `tower/mod.rs` | `"/opt/ecoPrimals"` | `DEFAULT_ECOPRIMALS_ROOT` |
| `relay.rs` | `"forgejo"` | `DEFAULT_SOVEREIGN_REMOTE` |

### Bug-adjacent fix

`temporal/resolve.rs` lines 187, 300: compared against literal `"forgejo"` while
`sovereign_remote()` (which reads `MEMBRANE_SOVEREIGN_REMOTE` env) was defined in
the same module. Now uses `sov` variable consistently. Would have broken if env
var was ever set to override the default.

### `as` casts → safe conversions

- `tower/mod.rs`: `len() as u64` → `u64::try_from`, `PROBE_PAYLOAD_SIZE as u64` → `u64::try_from`
- `gateway.rs`: `passed as f64 / total as f64` → `f64::from(u32::try_from(...))`
- `gate/enroll.rs`: const `as u32` guarded by compile-time assertion

### Idiomatic Rust

- `gate/health.rs`, `plasmid/sandbox.rs`: replaced `.all().iter().find(|s| s.binary == ...)` with `for_binary()`
- Removed unused `portable-atomic` dependency + `extra-platforms` feature

### LAN peer discovery

`MESH_REGISTRY` extended with `lan_ip` field: eastGate `192.168.4.244`,
sporeGate `192.168.4.3`. New `lan_address()` public API + 4 tests.

### Doc cleanup

- Fixed stale 1146→1150 test counts across all root docs
- Removed "NEW Wave 59" labels from VPS_STATE.md
- Fixed Channel 1 Signal status in CELLMEMBRANE_ARCHITECTURE.md ("Planned" → "LIVE")
- Updated RUNBOOKS.md date to Wave 150x

---

## For Upstream Teams

| Item | Owner | Action |
|------|-------|--------|
| biomeos-beacon service unit | biomeOS (flockGate) | Point to depot binary or disable until built |
| skunkBat process spawn rate anomaly | skunkBat (flockGate) | ThreatDetector category for rapid restarts |
| CLI contract validation | cellMembrane | Future: test depot binaries against unit args before deploy |
| Outbound connection monitoring | skunkBat | Future: detect anomalous outgoing connection rates |
| eastGate LAN IP in manifest | wateringHole (upstream) | Set `lan_ip = "192.168.4.244"` for eastGate in `ecosystem_manifest.toml` |
| specs/ re-validation | cellMembrane | 6 spec docs dated May 2026 — re-validate for Wave 150x reality |
