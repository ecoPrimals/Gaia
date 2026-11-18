# biomeOS — Wave 49 Ecosystem Tightening

**Date**: May 25, 2026
**Version**: v3.75 (doc refresh, no code version bump)
**From**: biomeOS
**Scope**: Wave 49 verification, doc tightening, debris cleanup

---

## Wave 49 Verification Checklist — ALL PASS

| Item | Status |
|------|--------|
| No `showcase/` directory | CLEAN |
| No local `wateringHole/` tree | CLEAN |
| `notify-plasmidbin.yml` active | `.github/workflows/notify-plasmidbin.yml` |
| No `which <primal>` in scripts | Only `which socat` (system tool) in deploy script |
| No stale `target/release/<primal>` patterns | `target/release/` retained as dev fallback — biomeOS is the infrastructure layer |

---

## Changes

### plasmidBin emphasis (Vector A)
- Binary discovery order updated across README, QUICK_START, scripts/README:
  `plasmidBin/` (canonical) → `livespore-usb/` → `target/release/` (dev fallback) → `$PATH`
- `plasmidBin/MANIFEST.md`: removed contradictory `cp target/release/...` instructions.
  Harvest tool (`tools/harvest`) is the canonical population path.
- `QUICK_START.md`: removed `target/release/biomeos` from manual startup example.

### Root doc refresh
- All 8 root docs + `graphs/README.md` synced:
  - Version: v3.75
  - Date: May 25, 2026
  - Tests: 8,026 workspace-wide (0 failures)
  - Deploy graphs: 43 (reconciled from conflicting 40/42/43 claims)
  - Active specs: 22 (was incorrectly 26)
  - deny.toml ban list: 16 crates (was incorrectly 18)
  - TODO count: 1 tracked (was incorrectly 0 in EVOLUTION_ROADMAP)
- `START_HERE.md` header was badly stale (v3.73 / 4,303 tests) — fully synced.
- NestGate "Upstream boolean fix" removed — evolved as of Bypass 3.
- `CONTEXT.md`: added version/date stamp.

### EVOLUTION_ROADMAP.md
- §5 Deep Debt Metrics refreshed from v3.23 to v3.75 (all 22 rows current).
- §9 Architecture diagram: 121 → 320+ translations.
- §10 Stadial: cross-gate dispatch via Songbird checked off (v3.75).

### Debris cleanup
- Deleted `examples/universal_ui_config.yaml` and `universal_ui_config_complete.yaml`
  (HTTP localhost UI model, zero references anywhere in codebase).
- `chimeras/README.md`: removed non-existent `mycorrhiza/` and `tardigrade/` dirs.
- `specs/NUCLEUS_ATOMIC_COMPOSITION.md`: replaced references to removed shell scripts
  (`bootstrap_tower_atomic.sh`, `validate_nucleus_quick.sh`, `validate_multi_ai.sh`)
  with current `biomeos nucleus start` commands.
- `crates/biomeos-boot/src/initramfs.rs`: removed reference to non-existent
  `scripts/prepare-kernel.sh` in error message.

### LiveSpore + build script plasmidBin alignment (Priority #2 from audit)
- `livespore-usb/x86_64/scripts/deploy_cross_arch.sh`: default target changed
  from `~/.local/bin` / `/usr/local/bin` to `plasmidBin/primals/`. Supports
  `BIOMEOS_PLASMID_DIR` override. Removed `$PATH` warning (biomeOS discovers
  plasmidBin directly). Updated next-steps to `biomeos nucleus start`.
- `scripts/build_primals_for_testing.sh`: marked DEV-ONLY. After building,
  now copies binaries into `plasmidBin/primals/` so biomeOS discovers them via
  the canonical path. Updated next-steps to reference harvest tool.
- `scripts/README.md`: build script status changed from Active to Dev-only
  with note pointing to `tools/harvest` and `plasmidBin/MANIFEST.md`.

---

## Post-Tightening State

- **Tests**: 8,026 (0 failures)
- **Clippy**: 0 warnings
- **TODO/FIXME**: 1 tracked (`live_discovery.rs` REST route wiring)
- **Unsafe**: 0 production
- **Pipeline debt**: RESOLVED — both audit items (LiveSpore deploy path, build script) fixed

---

## Known Investigation Items (not blocking)

These were found during the debris scan but are not cleanup targets:

| Item | Status | Notes |
|------|--------|-------|
| 11 unregistered `examples/*.rs` | Investigate | Not in root `Cargo.toml` `[[example]]` — can't run via `cargo run --example` |
| 91 `#[ignore]` tests | Intentional | ~82 are environment-dependent (live primals, sudo, QEMU); 4 in `operations_tests.rs` marked stale |
| `tools/` non-harvest binaries | Dev-only | `ecosystem-health`, `all-demos`, `integration-test-runner`, `test-coverage` — not in CI |
| Duplicate biome YAMLs | Low | `examples/biome-configs/` vs `specs/examples/` — overlapping but different detail levels |

---

*Wave 49 ecosystem tightening. plasmidBin is the channel.*
