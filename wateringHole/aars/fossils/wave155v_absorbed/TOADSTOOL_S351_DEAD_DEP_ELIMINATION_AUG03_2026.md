# ToadStool S351 — Dead Dependency Elimination

**Date**: Aug 3, 2026 | **Session**: S351 | **Primal**: toadStool | **Gate**: eastGate

## Summary

Systematic elimination of 48 confirmed dead dependency declarations across 21
Cargo.toml files. External dependency count reduced from 47 to 39 (17%
reduction). All removals verified via `cargo-machete` + manual source-level audit
(grep for imports, derive macros, cfg-gated code). Zero false positives removed.

## Changes

### Dead Dependencies Removed (48 total)

| Crate | Removed Dependencies |
|-------|---------------------|
| `runtime/specialty` | `void`, `telnet`, `rexpect`, `nb`, `ebcdic`, `cortex-m`, `embedded-hal`, `serialport`, `toadstool-config` |
| `runtime/container` | `clap`, `flate2`, `tar`, `tempfile`, `thiserror`, `tracing-subscriber` |
| `runtime/gpu` | `ash`, `futures`, `toadstool-ember` |
| `runtime/secure_enclave` | `base64`, `futures`, `serde`, `tokio`, `tracing-subscriber` |
| `runtime/edge` | `embedded-hal`, `esp-idf-sys`, `rppal`, `thiserror` |
| `runtime/display` | `drm-fourcc`, `futures` |
| `runtime/orchestration` | `futures`, `toadstool-config` |
| `runtime/wasm` | `tempfile`, `thiserror` |
| `runtime/native` | `serde`, `serde_json` |
| `runtime/adaptive` | `toadstool`, `uuid` |
| `management/performance` | `indexmap`, `serde_json`, `thiserror`, `toadstool-config`, `tracing-subscriber` |
| `management/monitoring` | `uuid` |
| `management/analytics` | `thiserror`, `toadstool-management-monitoring` |
| `integration/security` | `uuid` |
| `integration/primals` | `toadstool-integration-storage` |
| `runtime/universal` | `toadstool-runtime-native` |
| `distributed` | `sha2` |
| `core/toadstool` | `akida-driver` (+ `npu` feature) |
| `core/config` | `base64`, `semver`, `url` |
| `integration-tests` | `serde` |
| `cli` | Fixed `toadstool/npu` feature reference |

### Feature Cascade Fixes

- Removed `npu = ["dep:akida-driver"]` feature from `core/toadstool`
- Fixed `cli/Cargo.toml`: `npu = ["dep:akida-driver", "toadstool/npu"]` → `npu = ["dep:akida-driver"]`
- Removed orphaned features: `esp32`, `raspberry-pi`, `all-platforms` (edge), `serial-transport` (specialty)

### Mock Audit

All mock types confirmed properly isolated:

- `MockHardwareDetector` / `MockEcosystemDiscoverer`: `#[cfg(any(test, feature = "test-mocks"))]`
- `MockPrimal`: `#[cfg(test)]`
- No production mock leaks

## Quality Gates

| Gate | Status |
|------|--------|
| `cargo check --workspace` | **CLEAN** |
| `cargo clippy --workspace --all-targets` | **0 warnings** |
| `cargo fmt --all -- --check` | **0 diffs** |
| `cargo machete` | **0 dead deps** |
| `cargo test --workspace --lib` | **9,193 pass, 0 fail** |

## Upstream Impact

- No API changes — purely Cargo.toml cleanup
- No behavioral changes
- Compile times may improve slightly due to fewer crate resolutions
- `cargo-machete` now reports clean for entire workspace
