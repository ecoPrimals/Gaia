# cellMembrane Wave 155f — J6 Completion: `gate.configure` / `gate.apply`

**Date**: 2026-07-28 | **Trigger**: Gate workload distribution — J6 completion
**Gate**: sporeGate (eastGate overwatch)

---

## What Changed

### J6 Completion: `gate.configure` + `gate.apply` CLI Commands

J6 (systemd overrides manual) is now a full CLI surface:

- **`gate.configure [<gate>] [--env K=V]`** — Preview mode. Reads the gate's
  composition from `ecosystem_manifest.toml`, builds a `ServiceSpec` for each
  primal in the composition, and renders to the detected init system
  (systemd/launchd/bare). Output includes the full service config content for
  review before install.

- **`gate.apply [<gate>] [--env K=V]`** — Install mode. Same pipeline as
  `configure`, but writes the generated configs to disk:
  - **Systemd**: writes `<binary>-membrane.service` to `/etc/systemd/system/`,
    runs `daemon-reload` on success.
  - **Launchd**: writes `eco.primals.<binary>.plist` to `/Library/LaunchDaemons/`.
  - **Bare**: writes reference TOML to `$MEMBRANE_CONFIG_DIR/services/`.

- Gate name auto-detected from local identity or passed as argument.
- `--env K=V` flags inject environment overrides into all generated configs.
- `ServiceSpec` composition pipeline: manifest → gate profile → composition →
  primal list → registry lookup → `from_membrane_service()` → `extra_exec_args()`.

### Module Extraction

`dispatch/gate.rs` exceeded 800L after adding configure/apply. Extracted to
`dispatch/gate_configure.rs` (309L). Parent `gate.rs` stays at 747L.

### `nucleus.rs` Visibility Promotions

Three functions promoted from `pub(super)` / private to `pub(crate)`:
- `systemctl()` — daemon-reload after gate.apply installs units
- `resolve_security_socket()` — needed to build `ServiceSpec`
- `extra_exec_args()` — capability-based CLI arg resolution (already was)

### Deep Debt Fixes

1. **Tower port constant**: `7780` in `tower/mod.rs` → `DEFAULT_TOWER_PORT` +
   `ENV_TOWER_PORT` in `cellmembrane-types/src/service/constants.rs`.
2. **Bootstrap arch triple**: `write_gate_identity()` in `provision/bootstrap.rs`
   hardcoded `x86_64-unknown-linux-musl` → `detect_target_triple()`.

---

## Health Metrics

| Metric | Value |
|--------|-------|
| `cargo test` | **1,200** (up from 1,194) |
| `cargo clippy` | 0 warnings |
| `cargo fmt` | 0 drift |
| Production `unwrap()` | 0 |
| Unsafe code | 0 |
| Files >800 lines | 0 |

---

## Jelly String Status After This Wave

| # | What | Status |
|---|------|--------|
| J1 | Harvest | **CLOSED** |
| J2 | Depot push | **CLOSED** |
| J3 | Service restart | **CLOSED** |
| J4 | Caddy config | **CLOSED** |
| J5 | WG peer reg | **HARDENED** |
| J6 | systemd overrides | **CLOSED** — `gate.configure` + `gate.apply` |
| J7 | Legacy detection | OPEN (low priority) |
| J8 | Key enrollment portal | OPEN (songBird + cellMembrane) |

---

## Files Changed

| File | Change |
|------|--------|
| `dispatch/gate.rs` | `gate.configure` + `gate.apply` dispatch entries |
| `dispatch/gate_configure.rs` | **NEW** — configure/apply implementation + 6 tests |
| `dispatch/mod.rs` | Register `gate_configure` module |
| `gate/nucleus.rs` | `systemctl`, `resolve_security_socket` → `pub(crate)` |
| `main.rs` | Usage docs for new commands |
| `cellmembrane-types/service/constants.rs` | `DEFAULT_TOWER_PORT`, `ENV_TOWER_PORT` |
| `tower/mod.rs` | Tower port → constant |
| `provision/bootstrap.rs` | Arch triple → `detect_target_triple()` |

---

## For eastGate Overwatch

- J6 is now **CLOSED** — `gate.configure` previews, `gate.apply` installs.
  Teams deploying to westGate/strandGate can use these commands for automated
  service provisioning.
- Next cellMembrane work: J7 (legacy detection, low priority) or J8 (key
  enrollment portal, joint with songBird).
- 7/8 jelly strings resolved.
