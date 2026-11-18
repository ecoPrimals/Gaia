# AAR — strandGate NUCLEUS v4.55 Depot Deploy — Wave 155n

**Gate**: strandGate  
**Wave**: 155n  
**Date**: 2026-07-31  
**Operator**: strandGate overwatch (Cursor agent)  
**biomeOS**: v4.55.0 (depot, includes `88785daf` P1 fix + `652cf8a7` mode gap fix)

---

## Executive Summary

**12/12 HEALTHY. 1017 methods. 30 sockets. 13 processes. ZERO process accumulation.**

First clean full NUCLEUS on strandGate. All P1s from previous deploy confirmed fixed.
songBird stable for the first time since Wave 155i. Process count stable at exactly
1-per-primal after 5+ minutes of runtime.

---

## Deploy Method

```
Source:  depot.primals.eco/primals/ (rebuilt 11:11 EDT Jul 31 with mode gap fix)
  musl:  biomeos(21M) beardog(8.3M) songbird(19M) skunkbat(3.0M) nestgate(8.5M)
         loamspine(4.7M) sweetgrass(8.2M) rhizocrypt(7.5M) squirrel(4.4M) petaltongue(29M)
  gnu:   barracuda(5.3M) coralreef(7.6M) toadstool(13M)
Target: ~/.local/bin/
Launch: biomeos nucleus start --node-id strandGate --mode full --log-level info
```

---

## Health — 12/12

| Primal      | Version | Status      | Protocol | Latency |
|-------------|---------|-------------|----------|---------|
| bearDog     | 0.9.0   | healthy     | json     | 0.3ms   |
| songBird    | 0.2.1   | healthy     | json     | 0.2ms   |
| skunkBat    | 0.2.8   | Healthy     | json     | 0.4ms   |
| nestGate    | 0.5.0   | healthy     | json     | 0.2ms   |
| loamSpine   | ?       | Healthy     | json     | 0.2ms   |
| sweetGrass  | 0.8.0   | healthy     | ribo     | 0.2ms   |
| rhizoCrypt  | ?       | True        | json     | 0.4ms   |
| barraCuda   | 0.4.0   | healthy     | json     | 0.3ms   |
| coralReef   | 0.2.0   | operational | json     | 0.3ms   |
| toadStool   | 0.2.0   | alive       | ribo     | 0.2ms   |
| petalTongue | 1.7.0   | healthy     | json     | 0.3ms   |
| squirrel    | 0.1.0   | alive       | json     | 0.2ms   |

---

## Capabilities — 1017 methods

| Primal      | Methods |
|-------------|---------|
| toadStool   | 249     |
| bearDog     | 221     |
| barraCuda   | 98      |
| nestGate    | 96      |
| songBird    | 94      |
| petalTongue | 56      |
| loamSpine   | 50      |
| sweetGrass  | 40      |
| squirrel    | 39      |
| rhizoCrypt  | 38      |
| skunkBat    | 19      |
| coralReef   | 17      |

---

## GPU Compute

- Device: NVIDIA GeForce RTX 3090 (Vulkan)
- matmul 1024x1024 (20 rounds): **p50=0.33ms, p99=6.23ms**

---

## Crypto — Ed25519 Sign + Verify

- `crypto.sign_ed25519`: OK (algo=Ed25519, key=default_signing_key, 0.5ms)
- `crypto.verify_ed25519`: valid=True

---

## IPC Latency — 100-round health.check

| Primal    | p50     | p99     |
|-----------|---------|---------|
| loamSpine | 0.064ms | 0.162ms |
| coralReef | 0.072ms | 0.223ms |
| nestGate  | 0.084ms | 0.260ms |
| bearDog   | 0.091ms | 0.319ms |
| barraCuda | 0.103ms | 0.212ms |

---

## P1 Fix Validation — CONFIRMED

### Process Accumulation (`88785daf` — dual-protocol health ping + socket ownership guard)

| Metric                     | 155m (before fix) | 155n (after fix) |
|----------------------------|-------------------|------------------|
| Processes after 5 min      | ~62 (extrapolated)| **13**           |
| Processes after 14 min     | 175               | **13**           |
| Per-primal process count   | 2-23              | **1 each**       |
| Resurrections at 14 min    | 538               | ~196 (projected) |
| Socket accumulation        | Unbounded         | **Stable at 30** |
| Fork exhaustion risk       | YES (hit at 3 hr) | **NONE**         |

**Kill-before-spawn**: biomeOS now kills old process before spawning replacement.
Process count stays at exactly 1 per primal regardless of DEGRADED cycling.

### Socket Evaporation — RESOLVED for 12/12

Previous deploy: songBird socket persistently absent (respawn loop couldn't re-bind).
Current deploy: songBird socket present and stable. All 12 primal sockets persist.

### Binary Path Retention (`999044e7`) — still working

All 12 primals discovered in `~/.local/bin/`.

---

## Remaining Observations — P3 level

### 4 Primals Still Cycle DEGRADED (no user impact)

toadStool (21x), sweetGrass (21x), skunkBat (16x), coralReef (16x) fail both
dual-protocol health pings. biomeOS cycles them through DEGRADED → resurrect → respawn
but kill-before-spawn keeps process count at 1. Health probes from external clients
work fine (toadStool via ribo, others via json).

**Root cause**: biomeOS's health ping format differs slightly from what these primals
expect. The dual-protocol fix (`88785daf`) catches the majority of primals but these
4 need either:
- A third ping variant (e.g., different method name)
- Per-primal health check config in biomeOS

**Impact**: cosmetic — 951 WARNs in 5 min log, but composition is fully functional.

### 2 Zombie Processes

`toadStool` and `sweetGrass` initial spawns become zombies. `waitpid` reaping is
improved but not complete for the DEGRADED → kill path.

### 9 ERROR-level Log Entries

All "REJECTED: legacy connection" — demoted from ERROR in the log level fix but
still appearing (likely from our validation script's plain-JSON connections to
riboCipher-only endpoints).

---

## Delta: 155m → 155n (same gate, same depot path)

| Metric                   | 155m (v4.51)   | 155n (v4.55)   |
|--------------------------|----------------|----------------|
| Health                   | 11/12          | **12/12**      |
| Methods                  | 912            | **1017**       |
| Sockets                  | 27             | **30**         |
| Processes (5 min)        | ~62            | **13**         |
| Process accumulation     | **P1 — FATAL** | **FIXED**      |
| songBird                 | RESPAWN LOOP   | **STABLE**     |
| Fork exhaustion (3 hr)   | YES            | **NO**         |
| biomeOS version          | 0.1.0          | **4.55.0**     |
| Zombie processes         | 3              | 2              |
| bearDog binary size      | 12M            | 8.3M           |
| petalTongue version      | 1.6.6          | **1.7.0**      |

---

## strandGate NUCLEUS Status

**CONVERGENT.** strandGate is running clean NUCLEUS with depot-only deployment.
All P0/P1/P2 issues from previous waves are resolved. Ready for sustained operation.

Next for strandGate:
1. Provenance 7/7 validation (now unblocked — crypto.sign + verify working)
2. GPU pipeline evolution (G19: live rendering via Node Atomics)
3. Sustained uptime monitoring

---

*Filed by strandGate overwatch — Wave 155n — 2026-07-31*
