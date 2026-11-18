# barraCuda — Wave 49 Ecosystem Tightening

**Date**: 2026-05-25
**Primal**: barraCuda v0.4.0
**Type**: Ecosystem tightening — showcase fossilization, deployment pattern cleanup
**Commit**: `7ee28073`

---

## Wave 49 Vectors Addressed

| # | Vector | Status |
|---|--------|--------|
| A | Cut stale deployment patterns | Done — 3 `target/release/barracuda` refs removed |
| B | Consolidate local `wateringHole/` | N/A — no local tree existed |
| C | Fossilize `showcase/` | Done — 26 files → `fossilRecord/primals/barraCuda/showcase_wave49/` |

---

## Changes

### Showcase Fossilization

- 9 demos (4 Cargo crates + 3 shell scripts + 2 hybrid) archived
- 26 files moved to `ecoPrimals/fossilRecord/primals/barraCuda/showcase_wave49/`
- `showcase/` replaced with single `README.md` pointer to fossil archive
- Stale `target/release/barracuda` default paths in demo.sh scripts archived with content
- Single `wateringHole` cross-reference in `01-jsonrpc-server/README.md` archived

### Documentation Updated

- `STATUS.md`: Documentation grade updated (fossilized, not active)
- `CHANGELOG.md`: Wave 49 "Removed" entry
- `WHATS_NEXT.md`: Wave 49 in "Recently Completed"
- `specs/REMAINING_WORK.md`: Showcase section marked fossilized

### Verification

- [x] `showcase/` contains only README pointer
- [x] No `target/release/barracuda` in active code
- [x] No `which barracuda` anywhere
- [x] No local `wateringHole/` directory
- [x] `notify-plasmidbin.yml` active in `.github/workflows/`
- [x] No pipeline debt identified

---

## Pre-existing Compliance (confirmed)

- `notify-plasmidbin.yml` dispatches rebuild to plasmidBin on push to main
- Binary distribution: plasmidBin exclusive (musl-static ELF)
- CI: `ci.yml` runs quality gates only (no binary publishing)
- Local dev: `cargo run`/`cargo build` only (no `cargo install` self-install)
- `scripts/test-tiered.sh`: uses `cargo nextest`/`cargo clippy` only

---

## For primalSpring Audit

barraCuda is Wave 49 compliant. All three vectors addressed. Post-primordial
mandate in effect. No further action required from ecosystem coordination.
