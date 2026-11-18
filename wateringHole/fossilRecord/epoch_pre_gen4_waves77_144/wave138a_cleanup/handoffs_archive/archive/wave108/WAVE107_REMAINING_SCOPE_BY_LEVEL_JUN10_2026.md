# Wave 107 — Remaining Scope by Level

**Date**: 2026-06-10
**From**: eastGate primalSpring team
**State**: ZERO P1. ZERO PRIMAL BLOCKERS. S1-S4 ALL GRADUATED. 4-gate mesh collective LIVE.
**Priority cascade**: ~~Fix primals (mountain)~~ **DONE** → primalSpring absorbs → gates rebuild → gardens automate.

---

## Cross-Level Summary

| Level | P2 | LOW | Key Next Action |
|-------|-----|-----|-----------------|
| **Primals** (mountain) | **0** | 0 | **ALL CLEAR** — CR-TARPC-01, BM-UDS-01, NG-DOWNCAST-01, TOADSTOOL all RESOLVED |
| **primalSpring** | 0 | 1 | grapheneGate 13/13 scenario PASSES. aarch64 rebuild + deploy next. |
| **Springs** | 1 | 15 | healthSpring signal dispatch live test on ironGate |
| **Gates** | 1 | 0 | flockGate power-on (grapheneGate aarch64 REBUILT — deploy pending) |
| **Gardens** | 0 | 2 | NDK pipeline **DONE**. BearDog ACME + Forgejo CI are LOW. |
| **TOTAL** | **3** | **18** | **aarch64 REBUILT — deploy → 13/13 alive** |

---

## Level 1: Primals (Mountain)

### ALL RESOLVED — Mountain Clear

| ID | Owner | Action | primalSpring Tracking |
|----|-------|--------|----------------------|
| ~~`CR-TARPC-01`~~ | coralReef | **RESOLVED** (b1ec1f4). tarpc skips bind on tcp_only. | `blocker:cr_tarpc_01` → **PASS** |
| ~~`BM-UDS-01`~~ | biomeOS | **RESOLVED** (v4.20 d35c943e). All bind paths check tcp_only before UDS. | `blocker:bm_uds_01` → **PASS** |
| ~~`NG-DOWNCAST-01`~~ | nestGate | **RESOLVED** (7c3fe9a6). `is_platform_constraint()` chain-walking. | Workaround removed |
| ~~`TOADSTOOL-SOCKET-CLEANUP`~~ | toadStool | **VERIFIED** — 3-tier resolution adopted. | `blocker:toadstool_socket` → **PASS** |

### LOW

| ID | Owner | Action |
|----|-------|--------|
| `SKUNKBAT-TCP-9750` | skunkBat | **RESOLVED** — Port 9750 DROPPED from federation registry. Zero-port standard clean. |

---

## Level 2: primalSpring

### RESOLVED

| ID | Owner | Action |
|----|-------|--------|
| ~~`GRAPHENEGATE-SCENARIO`~~ | primalSpring | **RESOLVED** — grapheneGate readiness Phase 7 all PASS. 13/13 deployable. aarch64 rebuild + `deploy_pixel.sh` is the next operational step. |

### LOW

| ID | Owner | Action |
|----|-------|--------|
| Federation port cleanup | primalSpring | **RESOLVED** — beardog 9900/9101, skunkBat 9750 all DROPPED. Zero droppable ports. |
| Zero-port standard | primalSpring | **RESOLVED** — `federation:droppable_eliminated` check passes. |

---

## Level 3: Springs

### P2

| ID | Owner | Action |
|----|-------|--------|
| `GAP-47-SIGNAL-DISPATCH-LIVE` | healthSpring + biomeOS | Live test nest.store/nest.commit on ironGate biomeOS with signal graphs loaded. |

### LOW (15 healthSpring upstream)

See `impulses/active/2026-06-10T14-20_ironGate__wave107-healthspring-upstream-gaps.toml`.
2 MEDIUM, 13 LOW. All with stable workarounds.

---

## Level 4: Gates

### P2

| ID | Owner | Action |
|----|-------|--------|
| `FLOCKGATE-WAN-E2E` | flockGate ops | Power on → re-fetch from VPS → mesh.init to [RELAY_PUBLIC]:7700 → verify 5/5. |
| `GRAPHENEGATE-REBUILD` | primalSpring evolution team (eastGate) | **aarch64 REBUILT** (Wave 108, `cdff8b9`). Connect Pixel 8 → `deploy_pixel.sh` → 13/13 alive. |

---

## Level 5: Gardens

### P2

| ID | Owner | Action |
|----|-------|--------|
| ~~`CM-VPS-DEPOT-SYNC`~~ | cellMembrane | **SHIPPED** (ef3f0b8). BLAKE3 diff, atomic copy, checksums verification. |
| ~~`NDK-CROSS-COMPILE`~~ | cellMembrane | **DONE** (Wave 108). `aarch64-linux-android` pipeline, linker auto-detection, `plasmid.ndk.check`. |
| `BEARDOG-ACME-CUTOVER` | cellMembrane + bearDog | TlsProvider wired, awaiting BearDog ACME client to replace Caddy LE. |
| `MOBILE-GOLGI-FLEET` | cellMembrane | **SHIPPED** (9e07b01). GateMobility, --mobile, systemd templates, NM dispatcher hook, provision-golgi.sh. |

### LOW

| ID | Owner | Action |
|----|-------|--------|
| ~~`NG-DOWNCAST-01`~~ | nestGate | **RESOLVED** (7c3fe9a6). Error chain walking. Workaround removed. 7 new tests. |
| `PB-FORWARD-01` | cellMembrane | deploy_pixel.sh ADB port conflict — silent failure. |

---

## Ecosystem-Wide

### LOW

| ID | Owner | Action |
|----|-------|--------|
| `SOURDOUGH-SEGFAULT` | sourDough | `validate depot` segfault. Manual `b3sum` fallback. |
| `INFERENCE-NAMESPACE` | ecosystem | Canonical namespace: `model.*` vs `inference.*` vs `ai.*`. |

---

## Dependency Graph

```
CR-TARPC-01 + BM-UDS-01 (primal code) ← ALL RESOLVED ✓
    │
    ▼
GRAPHENEGATE-REBUILD (aarch64 rebuild) ← DONE ✓ (Wave 108, cdff8b9)
    │
    ▼
deploy_pixel.sh → 13/13 alive on Pixel 8 ← NEXT (physical access)
    │
    ▼
grapheneGate mesh enrollment (future)
```

```
FLOCKGATE-WAN-E2E (independent — just needs power-on)
    │
    ▼
5-gate mesh complete
```

---

## Validation State

| Metric | Value |
|--------|-------|
| primalSpring scenarios | 55 (10 tracks, 3 tiers) |
| lib tests | 901 pass, 2 ignored |
| clippy | zero warnings |
| known_debt | **0** (all upstream blockers resolved) |
| federation ports | 2 non-droppable (songbird), 0 droppable |
| zero-port standard | CLEAN |
| cascade | 38/38 parity |
