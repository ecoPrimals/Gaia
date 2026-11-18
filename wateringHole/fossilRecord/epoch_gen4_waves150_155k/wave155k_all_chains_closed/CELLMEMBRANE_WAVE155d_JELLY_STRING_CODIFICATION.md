# cellMembrane Wave 155d — J1+J2 Jelly String Codification

**Date**: 2026-07-28 | **Trigger**: Tower Atomic hardening — J1 harvest + J2 push codification
**Commit**: (pending push) | **Gate**: sporeGate (eastGate overwatch)

---

## What Changed

### J1: `plasmid.harvest` — Already Rust, Enhanced (P0)

**Finding**: J1 "harvest is shell loops" was already resolved — orchestration
is pure Rust `for` loops. External tool calls (`cargo`, `strip`, `git`) are
inherent toolchain dependencies, not replaceable shell loops.

**Enhancement**: Added `--push` flag to `plasmid.harvest`. When set, harvest
automatically pushes built binaries to VPS depot after successful build,
combining the harvest→push cycle into a single command:

```
membrane plasmid.harvest --all --local --push
```

Implementation: `append_push_outcome()` calls `depot_sync_push_standalone()`
after `finalize_depot()`. Push is skipped on dry-run or when nothing was built.

### J2: `plasmid.push` — First-Class Command + Depot Sync Refactor (P1)

**New command**: `plasmid.push` dispatched directly (was hidden behind
`plasmid.depot_sync --push`).

**Refactored default `depot_sync`**: The monolithic 30-line embedded bash
`for` loop sent as a single SSH command has been replaced with Rust-orchestrated
per-primal SSH commands:

| Before | After |
|--------|-------|
| 30-line bash `for p in $list` loop | Rust `for primal in &primals` loop |
| Single SSH command, all-or-nothing | Per-primal `sync_single_remote()` |
| Inline bash string concatenation | `RemoteSyncResult` enum (Synced/Current/Missing/Failed) |
| Output parsed from `synced=N current=N ...` | Direct counter tracking |

The per-primal approach uses 2 SSH commands per primal (hash+diff, copy+verify)
vs 1 monolithic command. Trade-off: marginally more SSH connections, but each
operation is individually observable, error-recoverable, and testable.

### Extract + Modularity

`harvest()` was approaching the 100-line clippy limit after the push addition:
- Extracted `finalize_depot()` — post-build metadata/signing/publish phase
- Extracted `append_push_outcome()` — push result merging
- `#[allow(clippy::struct_excessive_bools)]` on `HarvestArgs` (4 bool flags: `force`, `dry_run`, `local`, `push`)

---

## Changed Files

| File | Change |
|------|--------|
| `plasmid/depot_sync.rs` | Refactored `depot_sync()` to per-primal SSH. Added `depot_sync_push_standalone()`, `sync_single_remote()`, `RemoteSyncResult` enum. 5 new tests. |
| `plasmid/harvest.rs` | Added `push: bool` to `HarvestArgs`. Extracted `finalize_depot()`, `append_push_outcome()`. |
| `plasmid/mod.rs` | Re-exported `depot_sync_push_standalone`. |
| `dispatch/plasmid_dispatch.rs` | Added `plasmid.push` dispatch. Wired `--push` flag in harvest args. |
| `main.rs` | Updated usage: `plasmid.push`, `--push` on harvest. |
| `plasmid/harvest_tests.rs` | Added `push: false` to all `HarvestArgs` constructors. |
| `temporal/post_sync.rs` | Added `push: false` to `HarvestArgs` constructors. |
| `dispatch/sovereign.rs` | Added `push: false` to `HarvestArgs` constructor. |
| `webhook/pipeline.rs` | Added `push: false` to `HarvestArgs` constructor. |

---

### J6 Foundation: `ServiceSpec` Cross-Platform Config Model

Introduced `ServiceSpec` in `cellmembrane-types/src/process.rs` — a unified,
platform-agnostic service configuration struct:

| Method | Output |
|--------|--------|
| `to_systemd_unit()` | Full `.service` unit file |
| `to_systemd_override()` | Drop-in `override.conf` (env vars, env file) |
| `to_launchd_plist()` | macOS plist XML (program, args, env, keep-alive) |
| `from_membrane_service()` | Builder from registry + `ServerContract` + capability env |

`nucleus.rs` `generate_unit_content()` now delegates to `ServiceSpec::to_systemd_unit()`
instead of inline format strings.

### Deep Debt Fixes

| Fix | File | Detail |
|-----|------|--------|
| Dup federation port | `tower/mod.rs` | `SONGBIRD_FEDERATION_PORT` → `DEFAULT_FEDERATION_PORT` |
| Hardcoded `:7700` | `gate/enroll.rs` | Literal → `DEFAULT_FEDERATION_PORT` |
| Unguarded systemctl | `gate/crash_loop.rs` | `query_unit_restart_info` + `InitSystem` guard |
| Unguarded systemctl | `tower/timer.rs` | `systemctl()` + `systemctl_is_active()` + `InitSystem` guard |
| Domain fallback | `gateway/mod.rs` | `"primals.eco"` → `SURFACE_DOMAIN` |
| Hardcoded arch | `tower/timer.rs` | `x86_64-unknown-linux-musl` → `detect_target_triple()` |

---

## Health Metrics

| Metric | Value |
|--------|-------|
| `cargo test` | **1,194** (up from 1,182) |
| `cargo clippy` | 0 warnings |
| `cargo fmt` | 0 drift |
| Production `unwrap()` | 0 |
| Unsafe code | 0 |
| Files >800 lines | 0 |

---

## Deep Debt Audit

| Category | Count | Status |
|----------|-------|--------|
| Production `.unwrap()` | 0 | CLEAN |
| `unsafe` blocks | 0 | `#![forbid(unsafe_code)]` |
| TODO/FIXME/HACK | 0 | CLEAN |
| Files >800 lines | 0 | CLEAN |

---

## Jelly String Status After This Wave

| # | What | Status | Notes |
|---|------|--------|-------|
| J1 | Harvest is shell loops | **CLOSED** | Was already Rust. Added `--push`. |
| J2 | Depot push is rsync | **CLOSED** | `plasmid.push` + Rust depot_sync refactor. |
| J3 | Service restart manual | **CLOSED** (songBird) | `deploy.hot_swap` |
| J4 | Caddy config manual | **CLOSED** (songBird) | route self-config |
| J5 | WG peer reg manual | **HARDENED** (songBird) | WG peer management |
| J6 | systemd overrides manual | **FOUNDATION** | `ServiceSpec` model + renderers shipped. Full drop-in generation next. |
| J7 | Legacy service detection | OPEN (low priority) | |

---

## For eastGate Overwatch

- **J1+J2 CLOSED** — `plasmid.harvest --all --local --push` is now a single
  command for the full harvest→push cycle. No more manual rsync to golgiBody.
- **J6 FOUNDATION SHIPPED** — `ServiceSpec` cross-platform model + systemd/launchd
  renderers landed. `nucleus.rs` wired. Next: `gate.configure` / `gate.apply`
  commands for declarative drop-in override generation.
- **Deep debt** — 6 hardcoding / self-knowledge / cross-platform fixes shipped.
- **Tower Atomic hardening** posture maintained per Wave 155d sequencing.
