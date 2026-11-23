# cellMembrane Wave 151a — Depot Provenance + Multi-Target + Staleness

**Date**: 2026-07-25 | **Wave**: 151a | **Author**: cellMembrane team (sporeGate)
**Trigger**: P0 DEPOT DIVERGENCE — golgiBody depot 40 days stale, builder "unknown"

---

## Summary

Addressed three P0/P1 tasks from Wave 151a depot divergence analysis:

| # | Task | Priority | Status |
|---|------|----------|--------|
| 1 | `provenance.toml` builder = gate identity | P0 | **DONE** |
| 2 | `plasmid.harvest --all` full sweep | P0 | **ALREADY EXISTS** |
| 3 | Multi-target harvest from manifest `targets` | P1 | **DONE** |
| 4 | `plasmid.status` staleness alarm (>7 days) | P1 | **DONE** |

## Changed Files

| File | Change |
|------|--------|
| `membrane-shadow/src/plasmid/depot.rs` | Builder uses `resolve_local_gate_identity()` not `hostname()`. Dead `hostname()` fn removed |
| `membrane-shadow/src/plasmid/harvest.rs` | `targets_for_primal()` accepts manifest targets; priority: CLI > manifest > host |
| `membrane-shadow/src/plasmid/harvest_manifest.rs` | Populates `targets` from `manifest.build[].targets` |
| `membrane-shadow/src/plasmid/harvest_tests.rs` | 2 new tests: manifest targets override, CLI overrides manifest |
| `membrane-shadow/src/plasmid/mod.rs` | `parse_staleness_days()`, `DEPOT_STALE_THRESHOLD_DAYS=7`, status warns when stale |
| `membrane-shadow/src/manifest/types.rs` | `ManifestBuildConfig.targets: Vec<String>` |

## Health Metrics

| Metric | Value |
|--------|-------|
| Tests | 1,156 (was 1,150) |
| Clippy warnings | 0 |
| Files >800L | 0 |
| Production `.unwrap()` | 0 |

## sporeGate Deployment Actions Required

1. Run `membrane plasmid.harvest --all` on sporeGate for full 13-primal x86_64 rebuild
2. Run `membrane plasmid.refresh` to push to golgiBody depot
3. Install `aarch64-unknown-linux-musl` rustup target + cross-linker (P1)
4. Add `targets` to `[build.*]` entries in `ecosystem_manifest.toml` (P1)
5. Run `membrane plasmid.harvest --all --target aarch64-unknown-linux-musl` (P1)
