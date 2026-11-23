# cellMembrane Wave 147a Handoff — `gate.enroll` Automated Mesh Enrollment

**Date**: 2026-07-17 | **Wave**: 147a | **From**: eastGate cellMembrane team
**Commits**: `467560d` (gate.enroll), `56f8c0c` (deep debt refinement)

---

## Summary

Implemented `membrane gate.enroll <name> [--dry-run]` — automated mesh enrollment
that codifies the manual northGate enrollment AAR into a repeatable command.

### What `gate.enroll` Does

| Phase | Action |
|-------|--------|
| `manifest.resolve` | Read gate profile from `ecosystem_manifest.toml` — mesh IP, transport, roles |
| `wg.keygen` | Generate WireGuard keypair (or reuse existing) — `wg genkey`/`wg pubkey`, 0600 permissions |
| `wg.config` | Render wg-quick config from manifest peers — hub endpoints, keepalive, AllowedIPs |
| `mesh.verify` | Verify WireGuard tunnel connectivity — ping hub (10.13.37.1) |
| `forgejo.verify` | Verify Forgejo SSH connectivity via mesh — SSH to `git.primals.eco:2222` |
| `git.remotes` | Configure Forgejo-first remotes on all local repos — `origin` = Forgejo, `github` = GitHub mirror |

### Enrollment Standard (K-Derm Membrane Model)

```
origin = ssh://git@git.primals.eco:2222/<org>/<repo>.git   (Forgejo — inner membrane)
github = git@github.com:<org>/<repo>.git                   (GitHub — outer membrane)
```

### Files Changed

| File | Change |
|------|--------|
| `crates/membrane-shadow/src/gate/enroll.rs` | **NEW** — 753L enrollment module (5 phases + 8 tests) |
| `crates/membrane-shadow/src/gate/mod.rs` | Register `enroll` module + re-export `EnrollResult` |
| `crates/membrane-shadow/src/dispatch/gate.rs` | Wire `gate.enroll` dispatch + `dispatch_enroll` function |
| `README.md` | Wave 147a updates — test count, gate.enroll command, 6-gate mesh |
| `GLACIAL_SHIFT_TRACKER.md` | Wave 147a entry, 6-node mesh count |
| `VPS_STATE.md` | Wave 147a date |
| `RUNBOOKS.md` | Wave 147a date |
| `IRONGATE_VERIFICATION.md` | Wave 147a validation, 6-node mesh, northGate |

### Test Coverage

8 new tests:
- `forgejo_url_format` — Forgejo SSH URL structure
- `github_url_format` — GitHub SSH URL structure
- `wg_private_key_path_is_under_config_dir` — key path resolution
- `wg_config_path_is_under_config_dir` — config path resolution
- `manifest_to_wg_config_generates_peers` — manifest → WG peers with hub endpoint + keepalive
- `manifest_to_wg_config_excludes_self` — self-exclusion from peer list
- `wg_config_renders_valid_output` — rendered wg-quick config validation
- `enroll_dry_run_completes` — full dry-run phase sequencing

### Verification

```
cargo build:  0 errors
cargo clippy: 0 warnings (pedantic + nursery)
cargo test:   1,081 passed, 0 failed
```

---

## Deep Debt Audit

| Check | Result |
|-------|--------|
| Files >800L | 0 (largest: harvest.rs 762L, enroll.rs 753L) |
| `todo!` / `unimplemented!` | 0 |
| `unsafe` blocks | 0 (`#![forbid(unsafe_code)]` on both crates) |
| Clippy warnings | 0 |
| TODO/FIXME/HACK markers | 0 |

---

## Upstream Signals

- **northGate** now enrolled — 6th mesh node (Windows 11, RTX 5090)
- Garden gate assignments formalized: lithoSpore→ironGate, esotericWebb→flockGate
- Phase 2 Transport 14/14 COMPLETE, CAC 6/6 COMPLETE, Glacial 8/8 ALL CLEAR
