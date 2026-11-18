# cellMembrane Deep Debt Sprint — Wave 56b

**Date:** 2026-05-27
**From:** cellMembrane team (ironGate)
**To:** primalSpring coordination, projectNUCLEUS, all spring teams

---

## Summary

Systematic deep debt resolution across all 4 owned repos (cellMembrane, benchScale,
agentReagents, plasmidBin) targeting modern idiomatic Rust, typed APIs, env-driven
configuration, and comprehensive test coverage for the Wave 56 VPS deployment standard.

---

## Changes by Repo

### benchScale (272 tests pass)

| Change | Category | Impact |
|--------|----------|--------|
| `senescence.rs` (829L) smart refactored into `senescence/{types.rs, mod.rs}` | Large file refactor | Domain types extracted; monitor stays cohesive |
| `backend_type: String` → `BackendType` enum (Libvirt, Docker) | Stringly-typed → enum | Eliminates string matching across registry, server, CLI |
| Interactive VNC pause gated on `IsTerminal` | CI safety | No longer blocks headless/CI builds |
| `ip_pool::default_libvirt()` `.expect()` → `unwrap_or_else(unreachable!())` | Panic cleanup | Infallible compile-time constants |
| `DEFAULT_DEPLOY_DIR` `/opt/biomeos/bin` → `/opt/plasmidBin` | Legacy path cleanup | Aligns with post-consolidation install location |

### agentReagents (94 tests pass)

| Change | Category | Impact |
|--------|----------|--------|
| `CloudInitStatusInfo.status: String` → `CloudInitStatus` enum | Stringly-typed → enum | Uses existing typed enum already defined in `cloud_init_monitor.rs` |
| `running: bool` / `finished: bool` fields → `running()` / `finished()` methods | Redundant fields removed | Derived from enum variants, single source of truth |
| `Display` impl for `CloudInitStatus` + `CloudInitStage` | API completeness | Progress callbacks use typed Display instead of raw strings |

### plasmidBin

| Change | Category | Impact |
|--------|----------|--------|
| Centralized `DEFAULT_REMOTE_DIR` + `ECOPRIMALS_PLASMID_BIN` env var | Hardcoded → env-driven | deploy/stop/bootstrap CLI args now respect env override |
| clap `env` feature enabled | Capability | CLI args auto-populate from env vars |
| `/tmp/biomeos` socket dirs → `/run/membrane` | Stale path cleanup | Aligns with Wave 56 UDS standard |
| SAFETY comment on `libc::getuid()` | Code hygiene | Documents the only `unsafe` call |

### cellMembrane (93 tests pass — 13 new)

| Change | Category | Impact |
|--------|----------|--------|
| `tests/transport.rs` — 13 TransportMode tests | Test coverage | UDS-only/TcpOptIn/TcpDefault classification, socket path conventions, composition UDS queries |
| Root docs updated (README, GLACIAL_SHIFT_TRACKER, RUNBOOKS, VPS_STATE, IRONGATE_VERIFICATION) | Doc freshness | Test counts, Wave 56 references, caddy-tls unit name, handoff paths, UDS verification steps |

---

## Test Matrix After Sprint

| Repo | Tests | Clippy | Unsafe |
|------|-------|--------|--------|
| cellMembrane | 93 | 0 warnings | `#![forbid(unsafe_code)]` |
| benchScale | 272 | 0 warnings | libvirt FFI only (feature-gated) |
| agentReagents | 94 | 0 warnings | `#![forbid(unsafe_code)]` |
| plasmidBin | — | 0 warnings | `libc::getuid()` only |

---

## Remaining Debt (for tracking, not blocking)

- benchScale `src/backend/libvirt/dhcp_leases.rs` — unsafe FFI (6 blocks), feature-gated and isolated
- plasmidBin `deploy_membrane.sh` (1378L) — split candidate for future refactor
- plasmidBin `provenance.toml` covers 3/14 primals (upstream dependency)
- benchScale CLI `println!` in `bin/main.rs` (~24 calls) — acceptable for CLI UX
- agentReagents CLI `println!` in `bin/agent-reagents.rs` + `bin/lab-cleanup.rs` — acceptable for CLI UX

---

## Upstream Dependencies

| Item | Owner | Status |
|------|-------|--------|
| `nucleus_launcher` binary in plasmidBin releases | projectNUCLEUS | Pending |
| `biomeos deploy` live test with cell graph | biomeOS | Pending |
| NC-3.3 NS cutover (registrar) | cellMembrane + registrar | Pending |
| NC-3.4 Forgejo releases | cellMembrane + plasmidBin | Pending |
| NC-3.5 sporePrint living content | BearDog scope expansion | Blocked |

---

*All changes committed and pushed. cellMembrane is ready for upstream primalSpring audit.*
