# SHALLOW-PINGPONG Resolution + DRAWBRIDGE-ROUTES Confirmation — AAR Wave 137b

**Date**: Jul 12, 2026 | **Wave**: 137b | **Gates**: sporeGate + golgi
**Status**: SHALLOW-PINGPONG **RESOLVED** | DRAWBRIDGE-ROUTES **CONFIRMED**

---

## What Happened

Converted all 20 Forgejo repos on golgi from shallow (depth=1) to full-depth mirrors. The "Thin Forgejo Relay" pattern is retired — the disk savings (~2G) weren't worth the cascade friction. Also confirmed drawbridge routing is correctly configured.

## SHALLOW-PINGPONG Resolution

### Problem

Shallow bare repos on golgi (`depth=1`, `shallow` file present) rejected pushes after any local rebase because rebased commits reference parent SHAs that don't exist in the shallow repo. This forced `--force` pushes or manual re-shallowing for every cascade — observed on 7 repos (wateringHole, primalSpring, groundSpring, bearDog, nestGate, whitePaper, plasmidBin).

### Fix

1. Stopped Forgejo on golgi
2. For each of the 20 shallow repos: backed up, cloned fresh bare repo from sporeGate over WG SSH, fixed ownership to `git:git`
3. Restarted Forgejo
4. Disabled `forgejo-reshallow.timer` (was set to re-shallow on Aug 1)
5. Verified `git push origin main` works without `--force` on 3 test repos

### Outcome

| Metric | Before | After |
|--------|--------|-------|
| Shallow repos | 19/20 | 0/20 |
| Total disk | 545M | 2.6G |
| golgi free disk | 5.7G (39% used) | 3.5G (63% used) |
| Push friction | Reject + force-push on every rebase | Clean push |
| Reshallow timer | Active (Aug 1) | Disabled |

### Full Commit Counts (Post-Migration)

| Repo | Commits | Size Change |
|------|---------|-------------|
| wateringHole | 3,865 | Largest history |
| toadStool | 2,124 | |
| songBird | 1,742 | |
| bearDog | 1,287 | |
| biomeOS | 1,179 | |
| nestGate | 878 | |
| squirrel | 873 | |
| plasmidBin | 565 | |
| petalTongue | 484 | |
| sporePrint | 463 | Already full |
| coralReef | 349 | |
| whitePaper | 331 | |
| barraCuda | 314 | |
| cellMembrane | 303 | |
| sweetGrass | 242 | |
| rhizoCrypt | 241 | |
| loamSpine | 238 | |
| skunkBat | 110 | |
| sourDough | 64 | |
| fossilRecord | 13 | |
| bingoCube | 12 | |

### Architecture Change

The "Thin Forgejo Relay" pattern (Wave 134b) is retired:

**Before**: golgi hosted depth=1 bare repos. sporeGate maintained full mirrors. Cascading required re-shallowing or force-pushing.

**After**: golgi hosts full-depth bare repos mirrored from sporeGate. Standard `git push` works. No special tooling needed.

The `forgejo-reshallow` service and timer should be removed from `provision-golgi.sh`.

## DRAWBRIDGE-ROUTES Confirmation (#12)

| Check | Result |
|-------|--------|
| `SONGBIRD_PROXY_ROUTES` | `jupyter=http://192.168.4.237:8000/hub` |
| `SONGBIRD_DRAWBRIDGE_ROUTES` | `/hub=jupyter,/api=jupyter,/user=jupyter,/services=jupyter` |
| `SONGBIRD_DRAWBRIDGE_ADDR` | `0.0.0.0:7780` |
| Drawbridge `:7780/hub/` | 302 (JupyterHub redirect) — correct |
| `lab.primals.eco` (WAN) | 401 (basicauth gate) — correct |
| `ipc.list` | Empty — `jupyter` not registered as mesh capability |

The `jupyter` capability not appearing in `mesh.status` is expected — it's an HTTP proxy route, not a mesh-registered IPC service. This is the #7 UDS-HTTP-PROTOCOL gap (songBird team).

---

*Wave 137b: SHALLOW-PINGPONG permanently resolved. 20 Forgejo repos now full-depth on golgi. Thin Relay pattern retired. DRAWBRIDGE-ROUTES confirmed operational. Two items cleared from the debt inventory.*
