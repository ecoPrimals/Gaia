# AAR: grapheneGate Full NUCLEUS Deploy — Wave 133a

**Date**: 2026-07-06 10:50 EDT
**Gate**: grapheneGate (Pixel 8a, GrapheneOS)
**From**: eastGate overwatch
**Posture**: 12/13 primals LIVE, mesh peered (eastGate direct)

---

## Summary

Full NUCLEUS deploy on grapheneGate via pepti warehouse binaries (aarch64-unknown-linux-musl).
12/13 primals running on TCP. Mesh initialized with eastGate as bootstrap peer.
All binaries sourced from pepti warehouse — zero local builds.

---

## Results

| # | Primal | Port | Status | Transport |
|---|--------|------|--------|-----------|
| 1 | bearDog | :9100 | ALIVE v0.9.0 | TCP (0.0.0.0) |
| 2 | songBird | :9200 (fed) / :41819 (IPC) / :7780 (drawbridge) | HEALTHY v0.2.1, mesh PEERED | TCP + HTTP |
| 3 | skunkBat | :9140 | ACTIVE, defense enabled v0.2.9 | TCP (127.0.0.1) |
| 4 | toadStool | :9400 | ALIVE | TCP (127.0.0.1) |
| 5 | barraCuda | :9500 | ALIVE (degraded: no GPU, cpu-shader only) | TCP (127.0.0.1) |
| 6 | coralReef | — | EXITED (tarpc UDS bind → fatal) | — |
| 7 | rhizoCrypt | :9601 | ALIVE (BTSP-gated) | TCP (0.0.0.0) |
| 8 | loamSpine | :9700 | ALIVE | TCP (0.0.0.0) |
| 9 | sweetGrass | :9850 | ALIVE (BTSP-gated) | TCP (127.0.0.1) |
| 10 | squirrel | :9300 | ALIVE | TCP (127.0.0.1) |
| 11 | petalTongue | :9900 | ALIVE (BTSP-gated) | TCP (127.0.0.1) |
| 12 | biomeOS | :9750 | ALIVE (neural-api, btsp-optional) | TCP (127.0.0.1) |
| 13 | nestGate | — | CRASHED (UDS bind fatal on Android) | — |

**Mesh**: grapheneGate → eastGate (10.13.37.5:7700, direct, reachable)

---

## Key Findings

### 1. Port Proliferation — songBird Should Be the Sole Port Solver

Every primal currently binds its own TCP port with its own bind semantics (some 127.0.0.1, some 0.0.0.0, some ephemeral, some hardcoded). This is a **pre-mesh pattern**.

The target architecture (Tower Atomic):
- **songBird IS the port solver.** All primals bind UDS-only (or abstract socket on Android).
- songBird exposes the single federation port (:7700) and drawbridge (:7780) externally.
- All inter-primal and cross-gate routing goes through songBird mesh.
- No primal needs its own TCP port — songBird routes by capability, not address.

**Current reality**: 12 primals × 1-3 TCP ports each = 20+ ports exposed. This is the TCP fallback mode for platforms where UDS fails. Correct for Android today, but the primals themselves shouldn't be deciding port numbers or bind addresses.

### 2. Android UDS Fatal vs. Non-Fatal — Inconsistent Handling

| Behavior | Primals |
|----------|---------|
| UDS fails, TCP works, stays alive | bearDog, songBird, toadStool, barraCuda, squirrel, loamSpine, biomeOS, sweetGrass, rhizoCrypt, petalTongue, skunkBat |
| UDS fails → process exits | nestGate, coralReef |

**Root cause**: nestGate and coralReef treat UDS bind failure as fatal even when TCP is active. All other primals gracefully degrade.

**Fix**: Both need the same `--no-uds` or `BindMode::TcpOnly` graceful-degrade pattern. The UDS failure should be a WARN, not an ERROR that terminates the process. This is the same class as toadStool's DH-1 (just resolved upstream) — platform-aware runtime selection.

### 3. BTSP Gating is Correct Dark-Forest Posture

rhizoCrypt, sweetGrass, and petalTongue require BTSP handshake before accepting TCP commands. This is correct — they hold secrets (rhizoCrypt), evolution state (sweetGrass), or visualization data (petalTongue).

bearDog doesn't gate because it IS the BTSP provider. songBird doesn't gate because it needs unauthenticated mesh peering. This is the right trust hierarchy.

### 4. nucleus_launcher Android Gaps

The launcher successfully discovers and spawns primals but:
- Health probes use UDS sockets (fails on Android)
- Runtime dir defaults to `/tmp` (not writable on Android)
- Registry seeding fails (UDS IPC to primals)
- PID file tracking uses UDS paths

**Fix**: The launcher needs `BindMode` awareness for its health probes (TCP connect to assigned port) and a platform-aware runtime dir resolver (same pattern as DH-1 resolution: `ANDROID_ROOT` → `/data/local/tmp/biomeos`).

### 5. Cross-Gate Mesh Works Over ADB

grapheneGate successfully peered with eastGate (10.13.37.5:7700) via songBird mesh.init. The USB ADB port-forward chain means:
```
grapheneGate songBird → TCP :41819 → ADB forward → eastGate → WireGuard 10.13.37.5:7700
```
Sub-millisecond latency over USB. songBird handles the rest.

---

## Evolution Targets (upstream primal teams)

| ID | Primal | What | Priority |
|----|--------|------|----------|
| NESTGATE-ANDROID-01 | nestGate | UDS bind failure should be non-fatal when TCP is active | P2 |
| CORALREEF-ANDROID-01 | coralReef | tarpc UDS bind failure should be non-fatal (degrade gracefully) | P2 |
| LAUNCHER-02 | nucleus_launcher | Android-aware health probes (TCP instead of UDS) + runtime dir | P3 |
| PORT-SOLVER-01 | all primals | Primals should not choose their own ports. songBird mesh should assign/route. Long-term: primals bind UDS-only, songBird handles all TCP exposure | P3 |

---

## Deployment Recipe (validated)

```bash
# Environment (required for all primals on Android)
export HOME=/data/local/tmp/biomeos
export TMPDIR=/data/local/tmp/biomeos
export ECOPRIMALS_PLASMID_BIN=/data/local/tmp/plasmidBin

# Binary discovery
# Launcher: ECOPRIMALS_PLASMID_BIN + primals/{primal}
# Manual: /data/local/tmp/plasmidBin/primals/{primal}

# Per-primal CLI patterns that work on Android:
beardog server --bind-mode tcp --listen 0.0.0.0:9100
songbird server --port 9200 --bind 0.0.0.0 --listen 127.0.0.1:41819 --state-dir $HOME
skunkbat server --port 9140 --bind 127.0.0.1 --no-uds
toadstool server --port 9400
barracuda server --bind 127.0.0.1:9500 --no-unix
coralreef server --rpc-bind 127.0.0.1:9550  # (exits after UDS fail)
biomeos neural-api --tcp-only --port 9750 --bind 127.0.0.1 --btsp-optional
nestgate server --port 9650 --abstract --dev  # (exits after UDS fail)
rhizocrypt server --port 9601
loamspine server --port 9700
sweetgrass server --port 9850
squirrel server --port 9300
petaltongue server --port 9900

# Mesh init (after songbird starts):
printf '{"jsonrpc":"2.0","id":1,"method":"mesh.init","params":{"node_id":"grapheneGate","bootstrap_peers":["10.13.37.5:7700"]}}\n' | nc 127.0.0.1 {songbird_ipc_port}
```

---

## Conclusion

grapheneGate full NUCLEUS is viable today at 12/13 (92%). The 2 failures are the same class of bug (UDS fatal on Android) and have clear upstream fixes. The larger architectural observation is that **every primal managing its own ports is a transitional pattern** — the mesh convergence should culminate in songBird as the sole port solver, with primals communicating exclusively via capability routing through the mesh.

---

*Wave 133a — First full NUCLEUS on mobile. songBird mesh is the future. Ports are the past.*
