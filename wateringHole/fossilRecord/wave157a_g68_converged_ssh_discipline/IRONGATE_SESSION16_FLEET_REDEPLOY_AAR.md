# ironGate Session 16 — Wave 157a Fleet Redeploy (Depot Rebuilt)

**Date**: 2026-08-08 21:40 EDT
**Gate**: ironGate (10.13.37.7)
**Wave**: 157a — DEPOT REBUILT
**From**: ironGate hardware team
**To**: eastGate overwatch

---

## Summary

ironGate redeployed biomeOS from rebuilt golgi depot. FD exhaustion fix applied. Dispatch latency confirmed ~15ms (down from 15s). songBird already at seam-capable build from Session 15. All 13 services healthy.

---

## Execution

### 1. Cascade
Absorbed: petalTongue (+117 LOC), wateringHole updates. swarmVine on `master` branch (not `main`).

### 2. Depot Redeploy — biomeOS
- Pulled rebuilt biomeOS from depot (16 MB musl, includes `44c40191` dispatch reorder + `6f60cccf` routing gaps + `1ff5859c` riboCipher auto-detect + `d1f555e7` TOML loading fix)
- Replaced `/usr/local/bin/biomeos` via systemd stop → rm → cp → start
- songBird depot binary is still pre-seam (19 MB) — kept our local build (24 MB with seam) from Session 15

### 3. FD Exhaustion Fix
- Added `LimitNOFILE=65536` to biomeOS and songbird systemd services
- Verified: both processes now have 65536 open file limit (was 1024 default)
- Matches sporeGate's fix for simultaneous capability announcement storms

### 4. Dispatch Latency — VERIFIED
| Path | Latency |
|------|---------|
| songBird `capability.call` | **13ms** |
| biomeOS API socket | **17ms** |
| Pre-fix (Wave 156) | 15,000ms |

Confirmed: dispatch reorder fix (`44c40191`) is live on ironGate.

---

## Final State

```
Services:      13 active
Sockets:       26
biomeOS:       4.57.0 (depot rebuilt, dispatch fix live)
songBird:      0.2.1 (local build with gossip seam)
swarmVine:     0.1.0 (Phase 2, epidemic sweep)
Dispatch:      ~15ms (was 15s)
FD limit:      65536 (biomeOS + songbird)
Load:          0.89 (32 cores)
Gossip seam:   LIVE
Mesh:          westGate reachable (direct LAN)
```

---

## Note on Depot songBird

The golgi depot songbird binary (19 MB) does NOT contain the gossip inject seam despite the blurb stating it was rebuilt to 24 MB. This may be a Caddy cache issue or incomplete push. ironGate's locally-built songbird (24 MB, from source with seam) is correct and running. Other gates pulling from depot will get the pre-seam songbird until this is resolved.

---

## ironGate Fleet Redeploy: COMPLETE

All critical fixes from the "DEPOT REBUILT" blurb are now live on ironGate:
- biomeOS dispatch fix (15s → 15ms)
- riboCipher auto-detect (sweetGrass/rhizoCrypt auto-route)
- FD exhaustion prevention (65536)
- songBird gossip seam (local build)
- swarmVine Phase 2 (epidemic spread)
