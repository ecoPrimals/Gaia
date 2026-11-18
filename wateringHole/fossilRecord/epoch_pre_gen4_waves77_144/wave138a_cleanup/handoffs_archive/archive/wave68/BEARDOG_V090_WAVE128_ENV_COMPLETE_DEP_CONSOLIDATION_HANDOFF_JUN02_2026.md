# bearDog v0.9.0 — Wave 128 Handoff: Env Migration Complete + Dependency Consolidation

**Date**: Jun 2, 2026
**Wave**: 128
**Author**: southGate (autonomous)
**Status**: COMPLETE

## Summary

Environment variable centralization is now **complete**. All 370+ inline `std::env::var("BEARDOG_*")` literals across 96 production files have been migrated to `env_keys::ENV_*` constants. The only remaining inline strings (3 total) are external system variables (`ANDROID_NDK_HOME`, `NDK_HOME`) that are not BearDog-specific.

Dependency consolidation removed `base64-url` and replaced the `crossbeam` meta-crate with `crossbeam-queue`.

## Changes

### Env Migration Waves 6-7

- **Wave 6**: 47 files in `beardog-types/src/` migrated (169 inline vars → 0)
- **Wave 7**: 49 files across `beardog-core`, `beardog-genetics`, `beardog-monitoring`, `beardog-utils`, `beardog-tunnel`, `beardog-cli` migrated
- `env_keys.rs` grew from 562 to **803+ constants**
- New constant groups: OAuth, JWT, workflow engine, AI/inference, adapter/service mesh, monitoring/alerting, performance/Redis, mobile HSM, Kubernetes, Vault, cloud auth
- Final state: **0 inline BEARDOG_* strings** in production code

### Dependency Consolidation

| Crate | Action | Reason |
|-------|--------|--------|
| `base64-url` | **Removed** | 2 call sites replaced with `base64::URL_SAFE_NO_PAD` |
| `crossbeam` | → `crossbeam-queue` | Only `ArrayQueue`/`SegQueue` used |
| `dirs` + `directories` | **Kept both** | Different APIs needed (simple vs ProjectDirs) |
| `data-encoding` | **Kept** | Base32 for Tor v3; not covered by `hex` |
| `bs58` | **Kept** | Widely used across tunnel/crypto |

### Doc Test Fixes

- Added `use beardog_config::env_keys;` imports to doc examples in `beardog-tower-atomic/src/lib.rs`, `beardog-types/src/production/config.rs`, `beardog-types/src/canonical/config/security/authentication.rs`

### Last-Mile Env Cleanup

- `beardog-deploy/src/device.rs`: `BEARDOG_LOGCAT_FOLLOW_SECS`, `BEARDOG_PACKAGE_NAME` → env_keys
- `beardog-production/src/lib.rs`: `BEARDOG_MASTER_KEY` → env_keys
- `beardog-config/src/runtime_network_discovery.rs`: `BEARDOG_BIND_ADDRESS`, `BEARDOG_NETWORK_PROBE_TARGET` → env_keys
- `beardog-config/src/global.rs`: `BEARDOG_CONFIG_PATH` → env_keys

## Quality Gates

- `cargo fmt` — clean
- `cargo clippy --workspace -- -D warnings` — clean
- `cargo test --workspace` — **14,988 passed, 0 failed, 132 ignored**

## File Scan

Largest non-test, non-env_keys file: `beardog-acme/src/client.rs` at 859L (cohesive ACME protocol implementation, not worth splitting). All previously identified >800L files have been split in prior waves.

## Remaining Env Debt: Zero (BearDog-specific)

```
$ grep -r 'std::env::var("' crates/ --include='*.rs' -c
crates/beardog-tunnel/build.rs:1       # ANDROID_NDK_HOME (external)
crates/beardog-deploy/src/builder.rs:2  # ANDROID_NDK_HOME, NDK_HOME (external)
```

## Coordination

- Upstream: primalSpring audit will validate env_keys completeness
- Downstream: grapheneGate keystore design (P2) — next priority after env work
