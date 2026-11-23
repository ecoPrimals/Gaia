# AAR — strandGate Full Divergence Report — Wave 155m

**Gate**: strandGate  
**Wave**: 155m  
**Date**: 2026-07-31  
**Operator**: strandGate overwatch (Cursor agent)  
**Runtime at observation**: ~14 minutes post `biomeos nucleus start`

---

## Executive Summary

Pure depot deploy of all 13 primals + biomeOS from `depot.primals.eco`.
biomeOS depot binary includes commit `999044e7` (user-space binary discovery fix).
Binary path retention is confirmed fixed. However, biomeOS's health supervisor has a
**P1 process accumulation bug** — the respawn loop creates unbounded process growth.

**Snapshot health at probe time: 11/12 healthy, 912 methods, 27 sockets.**  
**Actual state: 175 primal processes running (should be 13), 538 resurrections in 14 minutes.**

---

## P1 — Process Accumulation (Respawn Storm)

### Observation

biomeOS's supervisor health-checks all primals via RPC ping using riboCipher framing.
Most depot primals respond to plain JSON-RPC, not riboCipher. The health pings therefore
fail for all primals after ~30 seconds, triggering DEGRADED → resurrect → respawn for
every primal, every ~90 seconds.

### Evidence

```
Runtime: 14 minutes

Total respawns:      350
Total kills:         187
Total resurrections: 538

Process counts (should be 1 each):
  beardog:     23
  skunkbat:    21
  coralreef:   22
  rhizocrypt:  22
  petaltongue: 21
  nestgate:    17
  loamspine:   17
  squirrel:    15
  barracuda:   13
  songbird:     2 (+ zombie)
  toadstool:    2 (+ zombie)
  sweetgrass:   2 (+ zombie)

Total primal processes: 175
Zombie processes: 3 (toadstool, sweetgrass, songbird)
```

### DEGRADED event counts (14 min window)

Every primal cycles through DEGRADED multiple times:

| Primal      | DEGRADED events |
|-------------|-----------------|
| sweetGrass  | 37              |
| skunkBat    | 33              |
| petalTongue | 33              |
| coralReef   | 32              |
| bearDog     | 31              |
| rhizoCrypt  | 31              |
| toadStool   | 28              |
| songBird    | 26              |
| nestGate    | 26              |
| loamSpine   | 26              |
| squirrel    | 26              |
| barraCuda   | 24              |

Virtual services also cycle:
| Service       | DEGRADED events |
|---------------|-----------------|
| security      | 23              |
| btsp          | 22              |
| crypto        | 22              |
| dag           | 21              |
| visualization | 21              |
| permanence    | 15              |
| ledger        | 17              |
| x25519        | 16              |
| ed25519       | 16              |
| ai            | 14              |

### Root Cause

1. biomeOS health pings use riboCipher framing (`0xEC 0x01` prefix)
2. Primals that speak plain JSON-RPC reject/timeout the riboCipher ping
3. After 3 failures → DEGRADED → biomeOS calls resurrect
4. Resurrect spawns a new process from `~/.local/bin/<primal>` (path discovery works)
5. The old process is NOT reliably killed — the kill PID may be stale, or overlapping
   respawn cycles race each other
6. New process binds to a new socket (or same socket), but old process keeps running
7. Each ~90s cycle adds more processes — unbounded growth

### Impact

- Memory/CPU exhaustion over time (175 processes at 14 min, ~750/hour extrapolated)
- Socket churn — filesystem sockets created and destroyed repeatedly
- The composition "works" because at any given moment enough instances have live sockets
- **Will degrade to OOM or PID exhaustion within hours of unattended operation**

### Severity: P1

### Recommendation

biomeOS supervisor needs two fixes:
1. **Kill-before-spawn**: Before respawning, reliably kill ALL processes matching the binary
   path, not just the tracked PID. Use process group kill or `pkill -f`.
2. **Ping protocol negotiation**: Health ping should fall back to plain JSON-RPC if
   riboCipher ping fails, or primals should declare their protocol at registration so
   biomeOS pings in the correct framing.

---

## P2 — songBird Socket Evaporation

### Observation

songBird starts and creates its socket, transitions to ACTIVE. biomeOS's RPC ping
fails (riboCipher mismatch). After 3 failures → DEGRADED. biomeOS kills songBird
and respawns it. The respawned songBird fails to bind its socket (previous instance
may still hold it, or zombie prevents cleanup). "Socket not found" → re-DEGRADED → loop.

songBird is the only primal where the socket is persistently absent — other primals
have enough overlapping instances that at least one has a live socket at any given moment.

### Evidence

```
ls /run/user/1000/membrane/songbird-e8b62b6e.sock → No such file or directory
ps aux | grep songbird → PID 3477256 running, but no socket
```

### Severity: P2 (known since Wave 155i)

---

## P2 — Zombie Processes

### Observation

Three primals have zombie (`<defunct>`) processes from the initial launch:

```
toadstool  PID 3477712  <defunct>
sweetgrass PID 3478667  <defunct>
songbird   PID 3544110  <defunct>
```

biomeOS spawns child processes but doesn't `waitpid()` on them after killing, leaving
zombies. These don't consume resources but indicate the supervisor isn't properly
reaping children.

### Severity: P2

---

## P2 — Virtual Service DEGRADED Churn

### Observation

biomeOS registers virtual/aggregate services (ai, btsp, crypto, dag, ed25519, x25519,
permanence, security, network, ledger, visualization) as capability sockets. These cycle
through DEGRADED because they're not real processes — biomeOS can't resurrect them.

### Evidence

```
/run/user/1000/membrane/ai.sock
/run/user/1000/membrane/btsp.sock
/run/user/1000/membrane/crypto.sock
/run/user/1000/membrane/dag.sock
/run/user/1000/membrane/ed25519.sock
/run/user/1000/membrane/x25519.sock
/run/user/1000/membrane/permanence.sock
/run/user/1000/membrane/security.sock
/run/user/1000/membrane/ledger.sock
```

These should either be excluded from health monitoring, or the health monitor should
understand that virtual services don't need resurrection.

### Severity: P2

---

## P3 — Missing graphs_dir

### Observation

```
WARN ⚠️ Cannot scan graphs_dir /home/strandgate/Development/ecoPrimals/graphs:
     No such file or directory (os error 2)
```

biomeOS defaults to `$CWD/graphs` for graph definitions. strandGate doesn't have
this directory. Non-blocking but indicates biomeOS's path defaults assume sporeGate's
directory structure.

### Severity: P3

---

## P3 — riboCipher Legacy Rejection Errors

### Observation

52 ERROR-level log entries in 14 minutes:

```
ERROR REJECTED: legacy connection (no riboCipher signal) — unsignalled connections
      dropped per Wave 113 policy
```

These fire when external tools (e.g., our validation script) probe sockets with plain
JSON-RPC. biomeOS logs these at ERROR level, which is noisy for what amounts to a
protocol negotiation failure. Should be WARN or DEBUG.

### Severity: P3

---

## P3 — biomeOS `--version` Reports 0.1.0

### Observation

```
$ biomeos --version
biomeos 0.1.0
```

The depot binary reports `v0.1.0` despite the blurb referencing v4.50/v4.51. Either
the version string isn't being set during CI builds, or the depot binary doesn't
include the version bump.

### Severity: P3

---

## Validated / Working

Despite the P1 supervisor issue, the composition's functional layer is healthy:

| Component   | Status |
|-------------|--------|
| **bearDog** crypto.sign_ed25519 + verify | Working (Ed25519) |
| **barraCuda** GPU compute | RTX 3090 Vulkan, matmul 1024x1024 p50=0.39ms |
| **coralReef** shader framework | Operational |
| **toadStool** orchestration | Alive (249 capabilities) |
| **nestGate** storage | Healthy (78 capabilities) |
| **loamSpine** ledger | Healthy (50 capabilities) |
| **sweetGrass** provenance | Healthy via ribo (40 capabilities) |
| **rhizoCrypt** encryption | Healthy (38 capabilities) |
| **petalTongue** network | Healthy (56 capabilities) |
| **squirrel** cache | Alive (39 capabilities) |
| **skunkBat** auth | Healthy (30 capabilities) |
| Binary path discovery (999044e7) | **FIXED** — all primals found in ~/.local/bin/ |
| IPC latency | p50: 0.065–0.118ms |
| Total capabilities | 912 methods |

---

## Delta Summary: 155k → 155m

| Metric                   | 155k (depot) | 155m (depot) |
|--------------------------|--------------|--------------|
| Binary path discovery    | BROKEN       | **FIXED**    |
| Snapshot health          | 7/12         | 11/12        |
| Socket evaporation scope | Widespread   | songBird only|
| Process accumulation     | Not measured | **P1: 175 procs / 14 min** |
| Respawn storm            | Not measured | **P1: 538 resurrections / 14 min** |
| Methods                  | ~780         | 912          |
| Zombie processes         | Not measured | 3            |

---

## Recommendations for eastGate / Overwatch

### P1 — Must Fix

1. **Process accumulation**: biomeOS supervisor must kill ALL instances of a primal
   binary before respawning. Current implementation tracks a single PID which goes
   stale during rapid respawn cycles. Recommend `pkill -f` or process group management.

2. **Health ping protocol**: biomeOS sends riboCipher-framed pings to primals that only
   speak plain JSON-RPC. This causes every primal to cycle through DEGRADED every ~90s.
   Options:
   - Primals declare their protocol at registration (json | ribo)
   - biomeOS falls back to plain JSON-RPC if riboCipher ping fails
   - All depot primals are rebuilt to handle riboCipher health pings

### P2 — Should Fix

3. **Zombie reaping**: biomeOS needs `waitpid(WNOHANG)` or a SIGCHLD handler to reap
   child processes after killing them.

4. **Virtual service exclusion**: Don't health-monitor virtual/aggregate capability
   sockets that aren't backed by real processes.

5. **songBird socket persistence**: songBird specifically fails to re-bind its socket
   after respawn. May be related to the zombie holding the socket FD.

### P3 — Nice to Have

6. **graphs_dir default**: Should fall back gracefully when running outside sporeGate's
   directory structure, or accept `--graphs-dir` from `nucleus start` args.

7. **Legacy rejection log level**: Demote "REJECTED: legacy connection" from ERROR to
   WARN/DEBUG.

8. **Version string**: Set `biomeos --version` to actual version during CI build.

---

*Filed by strandGate overwatch — Wave 155m — 2026-07-31*
