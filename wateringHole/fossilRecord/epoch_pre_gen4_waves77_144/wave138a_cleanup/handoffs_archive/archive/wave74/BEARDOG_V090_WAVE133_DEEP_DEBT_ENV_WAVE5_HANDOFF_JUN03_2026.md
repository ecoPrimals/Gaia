# BearDog v0.9.0 — Wave 133 Handoff

**Date**: Jun 3, 2026
**Owner**: southGate
**Commit**: `7ea2122b0`
**Tests**: 14,974+ pass, 0 fail

## Summary

Deep debt audit across entire codebase + env migration Wave 5.

## Changes

### Env Migration Wave 5 (~35 literals → constants)

| File | Literals Fixed | Category |
|------|---------------|----------|
| `system.rs` | 10 | App name, version, instance, workers, blocking threads, resources |
| `zero_hardcoding.rs` | 12 | HTTP/RPC/WS/metrics ports, bind addr, 7 timeouts |
| `security/mod.rs` | 6 | Rate limiting (requests/min, burst, window) |
| `testing.rs` | 5 | Test timeout, property iterations, benchmark config |
| `core_learning.rs` | 4 | Online learning (enabled, rate, batch, frequency) |
| `system_logging.rs` | 2 | Log rotation (max size, max files) |
| `compliance.rs` | 2 | Audit retention/frequency |
| `primal_identity.rs` | 2 | Family ID, Node ID |
| `beardog-ipc/lib.rs` | 1 | IPC resolve target param key (deduplicated) |
| `env_keys.rs` | +25 | New centralized constants added |

### Safety Fixes

- **Windows `.expect()` removed**: `platform/mod.rs:179` now uses `unwrap_or_else` with
  fallback named pipe `\\.\pipe\beardog-{primal_name}` instead of panicking
- **iOS XPC hardcoded ID fixed**: `"com.ecoprimals.beardog"` → derived from
  `ENV_PRIMAL_NAME` at runtime (self-knowledge pattern)

### Verified Clean

| Check | Result |
|-------|--------|
| `ring` in dependency graph | **ABSENT** (all targets) |
| `unsafe` blocks in production | **ZERO** |
| `.unwrap()` in production | **ZERO** |
| `todo!()`/`unimplemented!()` | **ZERO** |
| `cargo fmt` | Clean |
| `cargo clippy -D warnings` | Clean |

## Remaining Debt (Documented)

### P0 — Silent Degradation
- HSM mode silent software fallback (`hsm/manager/mod.rs:390-429`)
- Android stub keystore on non-device builds (`android_transports.rs`)
- Service registry/K8s/Consul discovery return empty vectors

### P1 — Env Literals (Wave 6+)
- ~80 remaining files with `"BEARDOG_*"` literals (many in test files)
- Production files with remaining literals: `production/*.rs`, `security/*.rs`, various config domains

### P2 — Architecture
- `env_keys.rs` at 1870 lines (constants registry — cohesive single-responsibility, no split needed)
- `acme/client.rs` at 859 lines (moderately cohesive — order/polling/renewal could split)
- Deprecated API surface (~40 items with `#[deprecated]`)
- PHASE-2 placeholders in FIDO2/entropy orchestrator

### P3 — Dependency
- `sha1` (legacy Git compat), `bcrypt` (Phase 7 legacy)
- `dirs` + `directories` overlap
- `hostname` + `whoami` overlap

## For primalSpring

- `ring` elimination CONFIRMED — zero in `cargo tree --target all`
- Env migration now at Wave 5 (803+ original + 25 new = 828+ constants)
- All quality gates passing
