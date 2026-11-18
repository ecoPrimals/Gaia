# westGate Divergence Report — Wave 155m Consolidated

**Date**: Jul 31, 2026 08:45 EDT
**Gate**: westGate
**Waves covered**: 155k → 155m (3 redeployments: v4.47, v4.50, v4.51)
**Author**: westGate overwatch (AI-assisted)
**Classification**: DISSEMINATE — all teams. biomeOS team: P2 action required.

---

## PURPOSE

This consolidates all divergences, issues, and fix validations from westGate's Wave 155k–155m deployments. Three biomeOS versions were deployed and tested (v4.47, v4.50, v4.51). Provenance 7/7 validated 4 times. Socket evaporation remains the single blocking issue for unattended NUCLEUS operation.

---

## DIVERGENCE MATRIX — BLURB CLAIMS vs WESTGATE REALITY

| # | Blurb Claim | Commit | westGate Result | Verdict |
|---|-------------|--------|-----------------|---------|
| 1 | bearDog dual-socket: default aliases family | `a875d463` | Default socket still separate listener, returns health stub for crypto.sign. Family socket works. | **PARTIAL** — workaround: set `BEARDOG_SOCKET` to family socket |
| 2 | bearDog FAMILY_SEED precedence | `a875d463` | Works — auto-generates seed when not provided | **CONFIRMED** |
| 3 | petalTongue `--family-id` propagation | `551e781` | Works — but as **global** flag, not subcommand flag. Service unit must put `--family-id` before `server` | **CONFIRMED** (with caveat) |
| 4 | biomeOS capability wipe cycle (3-strike) | `f2d4c4b3` | v4.51: caps held at 835 for ~165s (v4.50: ~60s). Eventually wipes to 0. | **IMPROVED** — 175% longer retention |
| 5 | toadStool JSON-RPC via compute.sock | `5053e0bc` | Works — responds to `health.liveness` via **riboCipher** prefix. Plain JSON-RPC rejected. | **CONFIRMED** (riboCipher required) |
| 6 | biomeOS socket evaporation fix (health ping) | `06ed323f` | v4.50: sockets 31→17 in 2 min. v4.51: 31→16 in 3 min. **Socket files still deleted.** | **NOT FIXED** |
| 7 | biomeOS binary path retention (5-tier) | `999044e7` | Caps hold longer (binary found). But socket deletion is separate code path. | **CONFIRMED** (binary discovery works) |
| 8 | Socket ownership 0666 | `0e45262f` | Socket permissions correct on creation. Irrelevant since sockets get deleted. | **CONFIRMED** (moot) |
| 9 | membrane.exe UnixStream P1 | `4ccbab1` | Not tested on westGate (Linux). Blurb says Windows fixed. | **N/A** |
| 10 | cellMembrane steamGate user-space | `4a7391d` | Not tested — steamGate not yet deployed | **N/A** |
| 11 | cellMembrane reqwest purge | `4e77ffd` | membrane binary dropped 2MB (15.7→13.7 KB). Confirmed. | **CONFIRMED** |
| 12 | checksums.toml finalize_depot | `0cfcce5` | Not directly tested on westGate | **N/A** |
| 13 | /run/membrane tmpfiles.d | `0cfcce5` | Symlink bridge still needed manually | **PARTIAL** — tmpfiles.d exists but not activated on westGate |
| 14 | rootpulse.ledger advisory | `0cfcce5` | Not tested | **N/A** |
| 15 | sandbox ServerContract for biomeOS | `0cfcce5` | Not tested | **N/A** |
| 16 | cellMembrane init-scope socket discovery | `301e236` | Not directly tested | **N/A** |

**Score: 7 confirmed, 2 partial, 1 not fixed, 6 not applicable to westGate**

---

## BLOCKING DIVERGENCE — SOCKET EVAPORATION

### The Problem
biomeOS deletes socket files belonging to other primals during its RPC health ping/prune cycle. All primal processes remain alive (PID confirmed, zero restarts) but their socket filesystem entries are removed, making them unreachable.

### Evidence Across 3 Versions

| Version | Peak Caps | Cap Hold Time | Sockets After 3 min | Socket Survival |
|---------|-----------|---------------|---------------------|-----------------|
| v4.47 | 715 | ~30s | ~17/29 | ~59% |
| v4.50 | 835 | ~60s | 17/31 | 55% |
| v4.51 | 835 | **~165s** | **16/31** | 52% |

Capability retention improved dramatically (v4.47→v4.51: 30s→165s, +450%). Socket survival has not improved — it's consistently ~50-55% after 3 minutes regardless of version.

### Evaporation Timeline (v4.51, representative)
```
t=  0s  socks:31  caps:835   stable
t= 60s  socks:20  caps:835   11 sockets deleted, caps still holding
t=105s  socks:16  caps:835   4 more deleted
t=165s  socks:16  caps:0     capability wipe finally hits
```

### Sockets That Consistently Evaporate
- beardog-westgate-tower-155f.sock
- skunkbat-westgate-tower-155f.sock
- nestgate-westgate-tower-155f.sock
- rhizocrypt-westgate-tower-155f.sock
- loamspine-westgate-tower-155f.sock
- barracuda-westgate-tower-155f.sock
- coralreef-westgate-tower-155f.sock

### Sockets That Consistently Survive
- songbird-westgate-tower-155f.sock
- sweetgrass-westgate-tower-155f.sock
- toadstool-westgate-tower-155f.sock
- petaltongue-westgate-tower-155f.sock
- squirrel-westgate-tower-155f.sock

### Pattern
The survivors all either (a) respond to biomeOS's health ping format or (b) were recently registered. The evaporated sockets likely fail the RPC ping (wrong transport format, riboCipher mismatch, or timeout), triggering `unlink()`.

### Recommended Fix
biomeOS must **never unlink a socket file it didn't create**. Three options:
1. **Ownership tracking**: registry records which sockets biomeOS `bind()`ed vs discovered
2. **connect() liveness**: before `unlink()`, do `connect()` — if it succeeds, the primal is alive (no RPC needed)
3. **No-delete policy**: biomeOS only marks capabilities as unavailable; never touches the filesystem

---

## OTHER ISSUES

### 1. membrane/ vs biomeos/ Socket Directory Mismatch
- Primals create sockets in `/run/user/1000/biomeos/`
- Neural API hardcodes Tower Atomic detection to `/run/user/1000/membrane/`
- **Workaround**: symlink bridge (manually created before Neural API starts)
- **Status**: Present since v4.47, not addressed in v4.50 or v4.51

### 2. bearDog Default Socket Still Returns Stubs
- `beardog-default.sock`: crypto.sign_ed25519 returns health stub
- `beardog-westgate-tower-155f.sock`: returns real Ed25519 signatures
- **Workaround**: `BEARDOG_SOCKET` in `nest.env` points to family socket
- **Status**: Blurb claims "Default socket now aliases family-scoped" (`a875d463`) — not observed on westGate. Two separate listeners.

### 3. toadStool Requires riboCipher for JSON-RPC
- Plain JSON-RPC rejected: "Connection rejected: missing riboCipher signal"
- riboCipher-prefixed JSON-RPC works for health.liveness
- **Impact**: biomeOS health pings may fail if they don't use riboCipher prefix for toadStool
- **Status**: This may contribute to socket evaporation for other primals too

### 4. sweetGrass Requires riboCipher for Health
- Same pattern as toadStool — plain JSON-RPC rejected for health
- Provenance braid.create works fine with riboCipher prefix
- **Status**: Operational, just needs riboCipher awareness in monitoring

### 5. Capability Wipe Cycle
- 3-strike prune (v4.49) improved retention from ~30s to ~165s
- Still eventually drops to 0 and rebuilds
- During the 0-cap window, graph dispatch fails
- **Impact**: Low for direct IPC (Provenance 7/7 works), high for signal graph orchestration

---

## WHAT WORKS WELL

1. **Provenance 7/7**: 4 consecutive validations across 3 biomeOS versions. Chain is rock-solid.
2. **Boot order discipline**: Tower → Nest → Node → Viz/AI → biomeOS LAST. Produces consistent results.
3. **bearDog crypto.sign_ed25519**: Real Ed25519 signatures. No longer a stub. Unblocked Provenance Trio.
4. **ZFS**: 25.4TB, ONLINE, healthy, 3,256 CAS objects, 1.56x compression. Zero issues.
5. **Direct IPC**: All primals respond correctly when contacted directly (with appropriate transport prefix).
6. **squirrel**: Binary halved (8.4→4.5 MB), 7,138 tests, 90.1% coverage. Impressive deep debt.
7. **Depot pipeline**: Binaries arrive via `curl` from depot, `chmod +x`, restart service. Clean and fast.

---

## OPERATIONAL WORKAROUND (westGate SOP)

```
# NUCLEUS startup procedure (socket-evaporation-resistant)
1. systemctl --user stop neural-api-tower
2. systemctl --user restart beardog-tower songbird-tower skunkbat-tower
3. sleep 2
4. systemctl --user restart nestgate-tower rhizocrypt-tower loamspine-tower sweetgrass-tower
5. sleep 3
6. systemctl --user restart toadstool-tower barracuda-tower coralreef-tower
7. sleep 2
8. systemctl --user restart petaltongue-tower squirrel-tower
9. sleep 2
10. for sock in /run/user/1000/biomeos/*.sock; do
      ln -sf "$sock" "/run/user/1000/membrane/$(basename "$sock")"
    done
11. systemctl --user start neural-api-tower

# If sockets evaporate:
12. Repeat steps 1-11

# For Provenance 7/7 validation:
13. Stop neural-api-tower (prevents evaporation during test)
14. Run 7-step chain via direct IPC
15. Restart neural-api-tower
```

---

## METRICS SUMMARY

| Metric | Value |
|--------|-------|
| NUCLEUS services | **13/13 active** |
| Socket survival (steady state) | **~50%** (evaporation after ~60s) |
| Provenance Trio | **7/7** (4 consecutive passes) |
| CAS objects | **3,256** on ZFS 25.4TB |
| biomeOS version | **v4.51** (20,342 KB) |
| Peak capabilities | **835** (Coordinated mode) |
| Cap retention | **~165s** before wipe |
| P0s | **ZERO** |
| P1s | **ZERO** |
| P2s | **1 OPEN** — socket file deletion during prune |
| P3s | **5 OPEN** — bearDog dual-socket, membrane/ path, tmpfiles.d, riboCipher ping format, cap wipe cycle |

---

*westGate Wave 155m consolidated divergence report. 7/16 fixes confirmed, 2 partial, 1 not fixed (socket evaporation — P2 for biomeOS). Provenance 7/7 rock-solid (4/4 passes). Cap retention +450% across 3 versions. Socket survival stuck at ~50%. biomeOS must stop deleting sockets it doesn't own. Everything else works. NUCLEUS IS THE PLATFORM.*
