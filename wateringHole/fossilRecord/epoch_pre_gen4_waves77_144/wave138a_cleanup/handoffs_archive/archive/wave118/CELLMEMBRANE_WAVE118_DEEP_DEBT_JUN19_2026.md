<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
> **SUPERSEDED** by `CELLMEMBRANE_WAVE119_NATIVE_EVOLUTION_JUN20_2026.md`

# cellMembrane — Wave 118 Deep Debt Consolidation

**Date:** 2026-06-19
**Team:** cellMembrane (sporeGate)
**Gate:** sporeGate → origin (forgejo)
**Tests:** 680 (from 620 at Wave 116d)
**Quality:** cargo fmt + clippy -D warnings + cargo doc — all clean, all files < 600L

---

## What Shipped

### SSH Consolidation (`ssh.rs`)
- Added `exec_on_host()`, `scp_to_host()`, `cat_remote()` — unified 3 independent SSH
  command construction patterns from `provision/bootstrap.rs`, `plasmid/download.rs`,
  `plasmid/canary_remote.rs` into shared transport layer.

### Git Ops Centralization (`git_ops.rs`)
- Added `git_output_opt()` and `head_short()` — replaced raw `Command::new("git")`
  rev-parse/ls-remote calls in `plasmid/build.rs`, `plasmid/drift.rs`,
  `plasmid/toolchain.rs`, `gate/health.rs`.

### Gate Identity Unification
- `gate/local.rs` now delegates to `identity::resolve()` through workspace root
  candidates. Previously had its own resolution chain that diverged silently.
- `tracing::warn!` on fallback to `"unknown"` — no more silent identity failures.

### Duplicate Logic Elimination
- `current_wave()` (14L verbatim copy in `context.rs` + `impulse/types.rs`) →
  canonical in `freshness.rs` using `FreshnessFile` struct. Both callers are thin wrappers.

### Silent Error Observability
- `freshness.rs`: log failed git pull-rebase execution
- `context.rs`: log corrupt braid TOML parse errors with file path
- `dispatch/data.rs`: log topology map load failures before bootstrap fallback

### Webhook Cascade Wiring (from Wave 116)
- `webhook::handle_push` stub → live: Forgejo→`temporal.sync`, GitHub→`relay.mediate`
- Static `CASCADE_REPOS` → manifest-driven `cascade_repos_from_manifest()`
- `rootpulse.commit/verify/status` dispatch + gate health probe

### Hardcoded Path Elimination (from Wave 116)
- All `"infra/wateringHole"` and `"infra/plasmidBin"` literals across 8 files →
  `cellmembrane_types::service::INFRA_WATERING_HOLE` / `INFRA_PLASMID_BIN` constants.

---

## Code Metrics

| Metric | Value |
|--------|-------|
| Tests | 680 |
| Production .unwrap() | 0 |
| TODO/FIXME/HACK markers | 0 |
| Files > 600L (prod) | 0 |
| #[allow] in prod | 3 (documented: mesh dead_code staging, firewall bools, fetch lifetime) |
| Shell-out commands | ~55 (git, ssh, systemctl — consolidation in progress) |
| Crate editions | 2024 |
| Rust version | 1.85 |

---

## Remaining Debt (for upstream awareness)

### P1 — Convergence targets
- **pepti SSH→forgejo**: blocks fresh builds (VPS ops, not code)
- **`webhook.receive` HTTP/UDS listener**: Caddy integration endpoint not yet implemented
- **git2 migration**: ~28 `Command::new("git")` sites could use `git2` crate for read-only ops

### P2 — Further centralization
- **systemctl → zbus D-Bus**: 4 `systemctl` shell-outs in `nucleus.rs`, `preflight.rs`, `nucleus_restart.rs`
- **ip/ss → rtnetlink**: 4 shell-outs in `gate/interface.rs`, `gate/preflight.rs`
- **Test coverage expansion**: `temporal/post_sync.rs`, `gate/bootstrap.rs`, `gate/health.rs` under-tested

### P3 — Metadata
- Gate profile `mobility`/`composition` fields staged in `mesh.rs` (Wave 117+ wiring)

---

## Upstream Dependencies

| Dependency | Status | Notes |
|-----------|--------|-------|
| `ecosystem_manifest.toml` | Consumed | Cascade repos, gate profiles, sync config |
| `TOPOLOGY_MAP.toml` | Consumed | Mesh discovery, zone resolution |
| `freshness.toml` | Read + publish | Wave tracking |
| primalSpring `cellmembrane-types` import | Ready | `CytoplasmZone`, `ZoneLabel`, `BOOTSTRAP_GATES` exported |
