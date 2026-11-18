# petalTongue v1.6.6 — Wave 61 Deep Debt + DH-1 Cleanup Handoff

**Date**: 2026-05-29
**Primal**: petalTongue
**Version**: v1.6.6
**Author**: ecoPrimals Agent

---

## Summary

Wave 61 deep debt cleanup covering DH-1 `/tmp` compliance, dependency evolution,
TRUE PRIMAL violation fix, production mock leak isolation, and root doc sync.
6,191 tests passed, zero clippy warnings.

## Changes

### DH-1 /tmp Cleanup (Wave 61)

All production socket and data writes now resolve through the DH-1 tiered chain:
`BIOMEOS_SOCKET_DIR` > `XDG_RUNTIME_DIR` > `/run/user/{uid}` > `/tmp` (last resort).

- Added `resolve_biomeos_socket_dir()` to `petal-tongue-core/constants/network.rs`
- Rewired 11+ production modules through the resolver
- Added `resolve_telemetry_dir()` for data files
- `LEGACY_TMP_PREFIX` retained as lowest-priority fallback only
- Zero production `/tmp` writes when `BIOMEOS_SOCKET_DIR` or `XDG_RUNTIME_DIR` is set
- Unblocks `ProtectSystem=strict` on VPS membrane

### Dependency Evolution

| Change | Impact |
|--------|--------|
| Removed `mdns-sd` (dead — never imported) | -1 dep, cleaner lockfile |
| `tokio/full` → explicit 8-feature set | Reduced unused subsystems |
| Dropped `serde/rc`, `clap/cargo`, `tower-http/set-header` | Unused features shed |
| Bumped `tower` 0.4 → 0.5 | Deduplicates with axum 0.7 transitive |
| Removed `mdns_discovery.rs` + `mdns` feature | Dead code cleanup |

### TRUE PRIMAL Violation Fix

`content_backend.rs` default provider changed from `"nestgate"` (primal name coupling)
to `"content-provider"` (capability-based). `CONTENT_BACKEND_PROVIDER` and
`CONTENT_BACKEND_SOCKET` env vars remain as explicit routing overrides.

### Production Mock Leak Isolation

| Leak | Fix |
|------|-----|
| UI `app/init.rs` auto-fallback injected fake primals | Now logs guidance, shows empty graph |
| Headless binary always loaded demo topology | Now requires `--demo` or `SHOWCASE_MODE=true`; added `--scenario <file>` |
| Sensory discovery assumed audio/mic capabilities | Now probes Linux subsystems (ALSA, PipeWire, PulseAudio) |

### Global CLI Flags (Wave 54)

`--socket`, `--port`, `--family-id` accepted before subcommands.
Subcommand-specific flags take precedence.

### Doc Sync

- START_HERE.md: Updated to Wave 61, added global flags, DH-1 env vars
- README.md: Test count 6,191+, fixed monorepo path references
- CHANGELOG.md: Added Wave 61 unreleased section
- CONTEXT.md: Updated test count, wave status, pairing table
- sporeprint/validation-summary.md: Updated metrics, date, wave ref

### Debris Scan

- **Zero** `.bak`, `.tmp`, `.orig` files
- **Zero** TODO/FIXME/HACK in production `.rs` source
- **Zero** stale scripts at repo root
- `fossilRecord/showcase_wave49/` preserved as fossil (36 files, Wave 49)
- `showcase/` is redirect stub only
- No local `infra/` or `wateringHole/` (clean per Wave 49)

## Metrics

| Metric | Value |
|--------|-------|
| Tests | 6,191 passed, 0 failed |
| Clippy | Zero warnings (workspace, pedantic + nursery) |
| Unsafe | `forbid(unsafe_code)` on all 18 crates + root |
| IPC methods | 53 across 10 domains |
| Max file LOC | 866 (WASM lib, ~560 are tests) |
| Edition | 2024 |
| Rust version | 1.87 stable |

## Status

**COMPLETE** — ready for primalSpring audit.
