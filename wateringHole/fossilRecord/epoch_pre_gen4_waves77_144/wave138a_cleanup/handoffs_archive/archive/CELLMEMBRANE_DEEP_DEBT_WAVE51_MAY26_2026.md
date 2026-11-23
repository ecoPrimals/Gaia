# cellMembrane — Deep Debt Sprint + Infrastructure Convergence

**From**: cellMembrane team (ironGate)
**To**: primalSpring (upstream audit), projectNUCLEUS, hotSpring
**Date**: May 26, 2026
**Wave**: 51
**Priority**: Medium — evolves three owned repos toward modern idiomatic Rust
**Status**: Complete — requesting upstream review

---

## Summary

Systematic deep debt resolution across all three cellMembrane-owned repositories:
`cellmembrane-types`, `benchScale`, and `agentReagents`. Targets were identified via
comprehensive audit (large files, unsafe code, hardcoding, mocks, external deps,
`println!` usage, clone patterns, String vs `&'static str`). Changes align with
ecosystem principles: capability-based design, self-knowledge only, postPrimordial
compliance, and modern idiomatic Rust.

Additionally, benchScale (~22k LOC, 308 tests) and agentReagents (~7.9k LOC, 113 tests)
were converged from `sort-after/` into their canonical `infra/` locations, with
dependency alignment, postPrimordial compliance enforcement, K-Derm topology wiring,
and archive cleanup — completing their transition to fully operational testing
infrastructure.

## Changes by Repository

### cellMembrane (`cellmembrane-types`)

| Change | Impact |
|--------|--------|
| `FirewallRule.comment: String` → `&'static str` | Zero heap allocation per rule |
| Remove `Deserialize` from `FirewallRule`, `FirewallRuleset` | Output-only types, correct trait bounds |
| `MembraneService.extra_ports` field | hbbs 21115, caddy 80 declared in registry (not special-cased in firewall) |
| `push_port_rules()` helper | Eliminates match repetition, `svc.binary` used directly |

80 tests pass, 0 clippy warnings.

### agentReagents

| Change | Impact |
|--------|--------|
| 10 `println!` → `tracing::info!` with structured fields | Library embeddability, consistent observability |
| `attach_mode: String` → `PciAttachMode` enum with serde | Type safety at deserialization boundary |
| Unused `Path` import removed | Clean compiler output |
| 26 `missing_docs` warnings resolved on `verification/types.rs` | Zero agentReagents-specific warnings |

113 tests pass.

### benchScale

| Change | Impact |
|--------|--------|
| `constants::deploy` module | `BENCHSCALE_DEPLOY_DIR` env → `/opt/biomeos/bin` default |
| `constants::libvirt_defaults` module | `BENCHSCALE_LIBVIRT_NETWORK` env → `"default"` default |
| Replace hardcoded `/opt/biomeos/bin` in `plasmid.rs`, `lab/mod.rs` | All deploy paths discoverable via env var |
| Replace hardcoded `"default"` across 6 libvirt modules | Single constant, env-overridable |
| 9 `println!` → `tracing::info!` in `stages.rs` | Structured logging for interactive VNC prompt |
| `dhcp_leases.rs` API: `*const c_char` → `Option<&CStr>` | Safe at call sites, no raw pointer imports |
| `c_str_or_empty` → `unsafe fn` with safety contract | Narrowed unsafe surface |

308 tests pass.

## Infrastructure Convergence (Wave 50–51)

| Action | Detail |
|--------|--------|
| benchScale moved from `sort-after/benchScale/` to `infra/benchScale/` | Canonical location, git history preserved |
| agentReagents moved from `sort-after/agentReagents/` to `infra/agentReagents/` | Canonical location, git history preserved |
| Slim bash predecessors archived to `infra/*-slim-archive/` | Fossil record preserved |
| Dependency alignment | `thiserror` 2.0, `serde_yaml` 0.10, `clap` 4.5 |
| postPrimordial compliance | Binary deploy to `/opt/biomeos/bin/`, `PLASMID_BIN` env, `fetch.sh` fallback |
| K-Derm diderm topology | `topologies/nucleus/kderm_diderm_membrane.yaml` + parsing test |
| Archive cleanup | `archive/`, `scripts/legacy/`, `templates/archive/` removed from working tree |

## Debt Audit Findings (For Upstream Teams)

Audit identified remaining debt targets for future cycles:

### benchScale (for hotSpring / projectNUCLEUS)
- Dual SSH architecture: `russh` vs `ssh(1)` still split across libvirt vs image-builder/senescence
- 5 files near 800L threshold (799, 778, 754, 745, 713) — smart refactor candidates
- `qemu-img` shell-outs in 3 modules — shared abstraction or pure-Rust candidate
- IP address/subnet duplication across `capabilities.rs`, `ip_pool.rs`, `constants.rs`

### agentReagents (for hotSpring)
- `manifest.rs` (780L) — schema + defaults + validation monolith, split candidate
- `vm_handle.rs` ssh/scp fallback — host dependency on external `ssh(1)`
- Hardcoded cloud-init package list in `cloud_init.rs:66`

### cellMembrane
- `config.rs` (460L) — validation logic growth target as compositions expand
- File I/O in types crate (`MembraneConfig::load`) — consider separating loader from pure types

## Upstream Review Requested

### For primalSpring
- [ ] Audit deep debt changes for alignment with ecosystem Rust standards
- [ ] Review `extra_ports` pattern — does this generalize to other service registries?
- [ ] Validate `PciAttachMode` enum variants against hotSpring GPU passthrough usage

### For projectNUCLEUS
- [ ] Review centralized deploy paths (`BENCHSCALE_DEPLOY_DIR`) against `deploy_membrane.sh`
- [ ] Validate K-Derm diderm topology YAML against Dark Forest boundary model

### For hotSpring
- [ ] Confirm `PciAttachMode::Cold`/`HotManaged`/`HotUnmanaged` covers VFIO anchor patterns
- [ ] Review dual SSH debt in benchScale — priority for hotSpring VM workflow?

## Next Cycle
- benchScale `stages.rs` + `senescence.rs` smart refactor (near 800L threshold)
- Unify SSH architecture (russh everywhere, eliminate ssh(1) fallbacks)
- IP/subnet capability discovery (replace hardcoded `192.168.122.x` defaults)
- cellMembrane CLI binary (parse + validate + generate UFW script)
- K-Derm topology evolution: recursive nesting, endosymbiosis
