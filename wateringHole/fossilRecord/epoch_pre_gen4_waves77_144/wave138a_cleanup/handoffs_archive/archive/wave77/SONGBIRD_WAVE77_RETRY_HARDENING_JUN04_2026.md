# Songbird — Wave 77 Handoff: Retry Hardening + Flaky Test Elimination

**Date**: June 4, 2026  
**Version**: v0.2.8-wave77  
**Gate**: southGate  
**Status**: Complete, all 13,971 tests passing (×3 runs), clippy clean, fmt clean

---

## Deliverables

### 1. Capability Announce Retry Hardening

Stress-tested for 5+ gates with unreachable peers:

- **Exponential backoff**: 120s × 2^attempt (attempt 1 immediate, attempt 2 skip 1 cycle, attempt 3 skip 3 cycles, etc.)
- **Queue depth cap**: 50 entries max — prevents unbounded memory growth when multiple gates are simultaneously unreachable
- **Stale capability TTL**: `PeerCapabilityEntry` tracks `last_seen: Instant`; entries >10min evicted on health cycle
- **Max retries raised**: 3 → 5, giving transient outages more recovery time
- **Age-based eviction**: Entries enqueued >10min are dropped regardless of attempt count
- **Observability**: Retry cycle logs `retried`/`dropped`/`deferred` counts

### 2. Flaky Test Race Elimination

Fixed 3 distinct env-var test race conditions (nondeterministic failures in full workspace test):

| File | Test(s) | Root Cause | Fix |
|------|---------|------------|-----|
| `songbird-cli/commands/quick/resources.rs` | `detect_network_speed_*` (3 tests) | `ScopedEnv` racing on `SONGBIRD_NETWORK_SPEED` | Extract `parse_network_speed()` pure fn, test without env |
| `songbird-cli/commands/quick/discovery.rs` | `discovery_http_port_*` (3 tests) | `ScopedEnv` racing on `SONGBIRD_DISCOVERY_PORT` | Test pure parsing + constant assertion |
| `songbird-cli/commands/tower.rs` | `tower_bind_*` (3 tests) | `ScopedEnv` racing on `SONGBIRD_BIND_ADDRESS` | Extract `resolve_bind_address()` pure fn |
| `songbird-config/agnostic_primal_config.rs` | `test_migration_helper` | `EnvOverride::contains_key` fallback to global env | Serialize via `lock_overlay_env_tests()` |
| `songbird-orchestrator/node_identity.rs` | `test_stable_id_generation` | `NODE_ID` racing between calls | Pin with `ScopedEnv("SONGBIRD_NODE_ID", "test-stable")` |
| `songbird-orchestrator/node_identity.rs` | `new_or_load_uses_custom_data_dir_and_is_stable` | Manual env set/restore racing | Use `ScopedEnv` guards |

All tests verified stable over 3 consecutive full workspace runs with zero failures.

---

## Phase 3.5 Status

**Still blocked on bearDog CryptoProvider Ed25519 interface delivery.**

Scaffold in place:
- `BtspSignatureVerifier` trait (object-safe, boxed-future)
- `NoopSignatureVerifier` placeholder active
- `BtspValidation::Valid` stores `payload_bytes` + `signature_bytes`
- `set_signature_verifier()` injection point ready

When bearDog delivers: wire real verifier → replace NoopSignatureVerifier → final relay security milestone.

---

## Metrics

| Metric | Value |
|--------|-------|
| Tests | 13,971 passed, 0 failures |
| Clippy | Zero warnings (pedantic + nursery) |
| Format | Clean |
| cargo-deny | All clear |
| Files >800L | 0 (largest: 791L virtual_relay.rs) |
| Flaky tests | 0 (verified ×3 full runs) |

---

## Coordination

- **bearDog**: Awaiting CryptoProvider Ed25519 verification interface for Phase 3.5 completion
- **primalSpring**: Ready for audit — retry hardening addresses 5+ gate stress scenario
