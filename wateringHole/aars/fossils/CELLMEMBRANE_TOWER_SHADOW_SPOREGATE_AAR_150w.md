# AAR — cellMembrane `tower.shadow` Command — sporeGate

**Wave**: 150w | **Date**: Jul 23, 2026 | **Gate**: sporeGate | **Team**: cellMembrane

---

## Summary

Shipped `membrane tower.shadow` — the P0 blocker from Wave 150w. The command
enables continuous Tower Atomic vs WireGuard parity metrics via a systemd timer
that benchmarks all mesh peers periodically using `songbird benchmark`.

## What Was Done

| # | Action | Status |
|---|--------|--------|
| 1 | Cascade sync from golgiBody | DONE — bearDog has local changes (not our repo) |
| 2 | Restart songbird-gateway with `BUILD_AUTHORITY=1` | DONE — drop-in loaded, service active |
| 3 | Built `tower/timer.rs` module in membrane-shadow | DONE — 0 warnings, 14 tower tests pass |
| 4 | Added `tower.shadow --enable\|--disable` (systemd timer lifecycle) | DONE |
| 5 | Added `tower.shadow.status` (timer + results state) | DONE |
| 6 | Added `tower.status` (stack health: songBird + bearDog + skunkBat) | DONE |
| 7 | Added `tower.benchmark --peer` (immediate on-demand run) | DONE |
| 8 | Extended existing `tower.shadow` probe (WG vs Tower TCP) | PRESERVED |
| 9 | Enabled shadow timer at 60min interval, 7 mesh peers | DONE |
| 10 | Updated depot binary + /usr/local/bin | DONE |

## Commands Shipped

```
membrane tower.shadow --enable [--interval N]   # Install systemd timer
membrane tower.shadow --disable                 # Remove timer
membrane tower.shadow.status                    # Timer + results status
membrane tower.shadow                           # Existing probe (unchanged)
membrane tower.shadow.export                    # Existing export (unchanged)
membrane tower.status                           # Stack health (3 primals)
membrane tower.benchmark [--peer ADDR]          # Immediate benchmark run
```

## Verification

```
$ membrane tower.status --json
Tower Atomic: 3/3 LIVE
  songBird: LIVE | bearDog: LIVE | skunkBat: LIVE
  shadow: ACTIVE

$ membrane tower.shadow.status --json
tower shadow: ACTIVE
results: 20 files
latest: wireguard_10_13_37_5:7700_20260723T154353.json

$ systemctl status tower-shadow-benchmark.timer
Active: active (waiting) — next run in ~1h
```

## Architecture

- **Module**: `crates/membrane-shadow/src/tower/timer.rs`
- **Dispatch**: Extended `tower/mod.rs` — `--enable`/`--disable` flags fork to timer
  submodule, bare `tower.shadow` preserves existing probe behavior
- **Benchmark**: Delegates to `songbird benchmark` subprocess, writes JSON to
  `benchScale/tower_shadow/`
- **Timer**: systemd oneshot service + timer, calls generated bash script that
  benchmarks all mesh peers in both modes
- **Discovery**: Peers from `cellmembrane_types::cytoplasm::known_mesh_gates()`

## Test Results

| Suite | Result |
|-------|--------|
| `cargo test` (all) | PASS — 0 failed |
| `cargo test tower` | 14 passed (7 existing + 7 new timer tests) |
| `cargo build --release` | 0 warnings |
| `tower.status` live | 3/3 LIVE |
| `tower.benchmark` live | 2/2 runs OK against eastGate |

## P0 Blocker Resolution

**RESOLVED** — `membrane tower.shadow` exists and is deployed on sporeGate.
flockGate and golgiBody can now use the same binary (depot updated).

## Remaining Items (not sporeGate P0)

| # | Item | Owner |
|---|------|-------|
| 1 | Mesh enrollment (stale peers) | flockGate (songBird team) |
| 2 | `songbird.sock` is a directory | flockGate |
| 3 | Drawbridge 502 on :7780 | flockGate |
| 4 | Direct LAN peering (sporeGate ↔ eastGate) | operator/hardware |
| 5 | 10G backbone cabling | operator/hardware |
