# blueGate Wave 157j — Depot Pull + MeshRelay Validated

**Date**: Aug 12, 2026 | **Wave**: 157j (depot-current) | **Gate**: blueGate (10.13.37.12)
**Operator**: blueGate sub-builder | **From**: overwatch (gate-agnostic)
**Status**: **NUCLEUS 13/13. MESHRELAY LIVE. DEPOT DIVERGENCE: songBird.**

---

## Summary

blueGate pulled the rebuilt depot. **1/15 binary changed** (songBird). However, the depot songBird binary for `x86_64-pc-windows-gnu` does NOT contain MeshRelay methods — `gossip.inject`, `gossip.spread`, `gossip.subscribe` all return "unknown method". blueGate is running the locally-built MeshRelay songBird (commit `9351230d`, 17.2MB LTO) as a workaround. All gossip methods validated. 13/13 NUCLEUS alive.

---

## CRITICAL FINDING: Depot songBird Windows Binary Missing MeshRelay

| Binary | Size | MeshRelay | Source |
|--------|------|-----------|--------|
| **Depot** (`x86_64-pc-windows-gnu`) | 21,550 KB | **NO** — gossip.inject/spread/subscribe return "unknown method" | sporeGate cross-compile |
| **Local build** (blueGate native) | 17,203 KB | **YES** — all 3 methods available, inject verified | commit `9351230d`, LTO thin |

**Root cause hypothesis**: sporeGate rebuilt the depot and tested MeshRelay on the Linux binary. The Windows cross-compiled binary may have been built from a pre-MeshRelay commit, or the cross-compilation target for `x86_64-pc-windows-gnu` was not included in the re-rebuild.

**Action for sporeGate**: Verify the Windows depot songBird was built from commit `9351230d` or later (which contains "gossip.subscribe completes MeshRelay surface"). Rebuild the `x86_64-pc-windows-gnu/songbird.exe` from HEAD.

**blueGate workaround**: Running locally-built songBird with MeshRelay. This binary could also be pushed to golgi depot as the authoritative Windows songBird.

---

## Depot Pull Results

| Binary | Size | Changed | Note |
|--------|------|---------|------|
| songbird.exe | 21,550 KB | **CHANGED** | New hash but MeshRelay MISSING |
| beardog.exe | 7,588 KB | current | |
| skunkbat.exe | 2,912 KB | current | |
| nestgate.exe | 8,520 KB | current | |
| loamspine.exe | 4,344 KB | current | |
| rhizocrypt.exe | 5,963 KB | current | |
| sweetgrass.exe | 17,064 KB | current | |
| petaltongue.exe | 24,616 KB | current | |
| squirrel.exe | 3,720 KB | current | |
| toadstool.exe | 9,002 KB | current | |
| barracuda.exe | 5,071 KB | current | |
| coralreef.exe | 7,300 KB | current | |
| biomeos.exe | 20,314 KB | current | |
| membrane.exe | 8,218 KB | current | |
| sourdough.exe | 2,895 KB | current | |

---

## MeshRelay Validation (Local Build)

```
mesh.init: OK (node_id=blueGate, 7 bootstrap peers incl graftGate .13)
reachable_peers: 7
relay_enabled: true

gossip.inject:    AVAILABLE
gossip.spread:    AVAILABLE
gossip.subscribe: AVAILABLE

gossip.inject test:
  → {"origin_gate":"blueGate","status":"injected","subscribers_notified":0,"topic":"gate.heartbeat"}
```

---

## Other Fixes This Session

### PID File Path Change

songBird depot binary uses `C:\ProgramData\songbird\songbird.pid` (not `songbird-blueGate.pid`). Both paths need cleanup before restart. The PID file path inconsistency across versions remains a Windows-specific operational burden.

### dnsproxy Restart

G29 Phase 2 DNS proxy had died overnight. Restarted successfully.

---

## NUCLEUS Health

| Component | Status | Port | Binary |
|-----------|--------|------|--------|
| beardog | ALIVE | :9100 OPEN | depot |
| **songbird** | **ALIVE** | **:7700 OPEN** | **LOCAL BUILD (MeshRelay, 9351230d)** |
| skunkbat | ALIVE | :9102 OPEN | depot |
| nestgate | ALIVE | :9200 OPEN | depot |
| loamspine | ALIVE | :9201 OPEN | depot |
| rhizocrypt | ALIVE | :9202 OPEN | depot |
| sweetgrass | ALIVE | :9213 OPEN | depot |
| petaltongue | ALIVE | :9204 closed | depot (P2) |
| squirrel | ALIVE | :9205 OPEN | depot |
| toadstool | ALIVE | :9300 OPEN | depot |
| barracuda | ALIVE | :9301 OPEN | depot |
| coralreef | ALIVE | :9302 OPEN | depot |
| biomeos | ALIVE | :9090 OPEN | depot |
| builder.serve | ALIVE | :9800 OPEN | depot membrane |
| dnsproxy | ALIVE | — | restarted |

**13/13 NUCLEUS | 12/13 ports | MeshRelay LIVE | builder.serve + dnsproxy**

---

## Remaining Items

| Item | Priority | Detail |
|------|----------|--------|
| **Depot songBird Windows rebuild** | HIGH | Depot binary missing MeshRelay. sporeGate needs to rebuild `x86_64-pc-windows-gnu/songbird.exe` from HEAD. OR: blueGate pushes local build to golgi. |
| **swarmVine Windows port** | P2 | 5 UDS call sites need TCP fallback. |
| **petalTongue port** | P2 | :9204 still closed in server mode. |
| **PID file path stability** | LOW | songBird PID path varies between versions. |

---

*blueGate 157j depot-current: 13/13 NUCLEUS. MeshRelay LIVE (local build workaround). Depot songBird for Windows MISSING MeshRelay — needs sporeGate re-rebuild or blueGate push. gossip.inject verified. 7 mesh peers. Ready for fleet gossip.*
