# Wave 87: PostPrimordial Deployment Standard Audit

**Date**: 2026-06-07  
**Author**: eastGate overwatch  
**Type**: Ecosystem-wide deployment pattern validation  
**Status**: Complete — 2 fixes applied, remaining gaps documented

---

## Standard

Post-primordial deployment: all primal binaries come from the `plasmidBin` depot.
No `target/release/` fallbacks. No `~/.local/bin` fallbacks. No `cargo build --release`
for primal deployment. Springs consume primals from the depot via `ECOPRIMALS_PLASMID_BIN`
or `ECOPRIMALS_ROOT/infra/plasmidBin`.

---

## Audit Results

### Fully Compliant

| Component | Binary Resolution | Notes |
|-----------|-------------------|-------|
| **primalSpring** (Rust) | `launcher::discover_binary()` — 4-tier plasmidBin-only | No target/release fallback |
| **primalSpring** (deploy validation) | `validate_deployment_readiness()` uses `discover_binary()` | Enforces depot-only |
| **wetSpring** | `primal_binary.rs` — plasmidBin-only, Wave 49 compliant | Explicitly no PATH/target fallback |
| **healthSpring** | `fetch_primals.sh` + `gate_nucleus.sh` — plasmidBin-only | Clean postPrimordial |
| **ludoSpring** | `validate_gate.sh`, `ludo_composition.sh` — no stale refs | Uses composition lib |
| **plasmidBin membrane services** | All `.service` files — no stale paths | UDS-only, depot paths |

### Fixed This Wave

| Component | Issue | Fix |
|-----------|-------|-----|
| **neuralSpring** `visualize.sh` | `find_binary()` had `target/release` fallback + wrong path (`plasmidBin/bin/`) | Rewritten: plasmidBin triple-aware → flat → PATH, no target/release |
| **primalSpring** `validate_release.sh` | `plasmidbin` CLI fallback to `target/release/plasmidbin`; stale `springs/` binary check | Removed target/release fallback, removed excised spring binary checks, added `membrane plasmid.status` check |

### biomeOS Team Gaps (not fixed — owned by biomeOS)

| ID | Issue | Priority |
|----|-------|----------|
| BIO-SEARCH-01 | `discover_binaries_with()` in `nucleus_procs.rs` searches `livespore-usb/` before `ECOPRIMALS_PLASMID_BIN` | P2 |
| BIO-DEPLOY-02 | `deployment.rs` search order includes `target/release` as fallback | P3 |
| BIO-BOOT-01 | `initramfs.rs` + `rootfs/builder/install.rs` use `target/release/biomeos-init` | P3 (legitimate for boot image building) |

### Spring Scripts with `cargo build --release` (Legitimate)

These scripts build the spring's OWN binaries (not primals) — this is expected:

| Spring | Script | What It Builds |
|--------|--------|---------------|
| groundSpring | `build-guidestone.sh` | `groundspring_guidestone` (spring validation binary) |
| hotSpring | `build-guidestone.sh` | `hotspring` validation binary |
| hotSpring | archived experiment scripts | Science experiment runners |

### Archived/Fossil Scripts (Not Active)

hotSpring has ~20 archived scripts in `scripts/archive/` and `experiments/archive/` that
reference `target/release`. These are fossil record and do not need updating.

---

## Validation

- primalSpring: `cargo check` — clean (27 warnings, all pre-existing doc warnings)
- primalSpring: `cargo test --workspace` — **942 passed, 0 failed**
- neuralSpring `visualize.sh` — updated to triple-aware plasmidBin-first resolution

---

## Summary

The ecosystem is at **~95% postPrimordial deployment compliance**. The two active scripts
with stale patterns have been fixed. The remaining gaps are all in biomeOS and are the
biomeOS team's responsibility (BIO-SEARCH-01 is the most impactful — it's the P2 blocker
for depot-sourced NUCLEUS startup).

| Level | Compliance |
|-------|-----------|
| primalSpring (Rust) | 100% — plasmidBin-only binary discovery |
| Springs (scripts) | 100% — all active scripts now plasmidBin-first |
| Gates (biomeOS NUCLEUS) | ~60% — livespore-usb priority bug, target/release fallback |
| VPS (membrane services) | 100% — UDS-only, depot paths |

---

*"The standard is set. The springs follow it. biomeOS needs to catch up."*
