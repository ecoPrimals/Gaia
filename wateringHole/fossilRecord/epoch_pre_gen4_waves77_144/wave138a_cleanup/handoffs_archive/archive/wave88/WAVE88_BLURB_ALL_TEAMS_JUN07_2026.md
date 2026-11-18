# Wave 88 Blurb — All Teams

**Date**: 2026-06-07  
**From**: eastGate overwatch  
**Subject**: Deployment pipeline proven, postPrimordial audit complete, next wave targets

---

## Cascade Status

38/38 parity. Depot 13/13 current. toadStool divergence auto-resolved (archived).

---

## cellMembrane

**CM-TRIGGER-01: RESOLVED.** `plasmid.trigger` command shipped (Wave 87, `78c571c`).
SSH-kicks VPS pipeline service for immediate harvest→refresh. Validated from eastGate
— trigger reached golgi, service kicked. VPS-side service needs path fix (P3, VPS config).

Also delivered:
- Deep debt: `harvest_one` refactored (122→50 lines), pipeline stages split into
  clone → build → strip → stage. `update_depot_metadata` split. Temporal check extracted.
  `/opt/membrane` fallback centralized. Last `#[allow]` removed. deny.toml bumped.
- `config/capability_registry.toml` — machine-readable capability declarations
- +21 tests (252 total, 0 failures)

**Remaining cellMembrane gaps:**

| ID | Description | Priority |
|----|-------------|----------|
| CM-WEBHOOK-01 | Forgejo webhook → selective cascade rebuild | P3 |
| CM-VPS-SVC-01 | `plasmid-pipeline.service` path fix on VPS (trigger works, service fails) | P3 |

**cellMembrane is clear.** No P1/P2 blockers.

---

## biomeOS

**2 gaps blocking full depot deployment:**

| ID | Description | Priority |
|----|-------------|----------|
| BIO-SEARCH-01 | `discover_binaries_with()` searches `livespore-usb/` before `ECOPRIMALS_PLASMID_BIN`. Fix: when `ECOPRIMALS_PLASMID_BIN` is set, make it the **first** search path. 5/12 primals still resolve from stale livespore-usb. | P2 |
| BIO-DEPLOY-02 | `deployment.rs` includes `target/release` in search order | P3 |

**BIO-SEARCH-01 is the mesh proof blocker:** songbird resolves from livespore-usb (old binary)
instead of the depot (v4.09 with federation env fix). Once search priority is fixed, eastGate
songbird will listen on :7700 and the 2-gate mesh proof with strandGate can complete.

---

## All Primals

**Mountain is clear.** No upstream primal work blocking deployment or mesh.

toadStool at S299 (deep debt XI), 9,069+ tests. Divergence auto-resolved.

**P2 (non-blocking):** Transport injection — 1/14 primals transport-agnostic (sporePrint).
All others still self-bind TCP/UDS. Waiting on songBird `ipc.resolve` structured endpoints.

---

## Springs

**PostPrimordial deployment audit complete (Wave 87):**

| Spring | Status |
|--------|--------|
| primalSpring | 100% — `discover_binary()` plasmidBin-only, `validate_release.sh` fixed |
| wetSpring | 100% — `primal_binary.rs` plasmidBin-only since Wave 49 |
| healthSpring | 100% — `fetch_primals.sh` plasmidBin-only |
| neuralSpring | 100% — `visualize.sh` fixed (was target/release fallback) |
| ludoSpring | 100% — clean |
| groundSpring | 100% — builds own binaries only (not primals) |
| hotSpring | 100% — archived scripts are fossil record |
| airSpring | 100% — clean |

**Springs are clear.** No deployment gaps.

---

## Gates

| Gate | Status | Next |
|------|--------|------|
| eastGate | NUCLEUS from depot validated, songbird healthy | Needs BIO-SEARCH-01 fix for federation port |
| strandGate | mesh-ready, songbird :7700 LIVE, 13/13 ALIVE | Waiting on eastGate federation |
| ironGate | operational | — |
| southGate | cascade adopted, 20/20 parity | — |
| flockGate | WAN operational, sporePrint transport abstraction | — |
| westGate | hardware pending | 10G backbone LIVE |

---

## Critical Path to Stadial

1. ~~plasmidBin pipeline e2e~~ **DONE** (Wave 87)
2. ~~CM-TRIGGER-01~~ **DONE** (Wave 87)
3. ~~PostPrimordial audit~~ **DONE** (Wave 87)
4. **BIO-SEARCH-01** — biomeOS binary search priority fix (P2, blocks mesh proof)
5. eastGate Songbird federation port :7700 (unblocked by #4)
6. 2-gate mesh proof (strandGate ready, eastGate pending)
7. S4 auth gate review (~Jun 9)
8. westGate enrollment (hardware pending)
9. 3-gate mesh proof → stadial entry

---

*"Pipeline proven, springs audited, trigger delivered. biomeOS search priority is the last wall before mesh."*
