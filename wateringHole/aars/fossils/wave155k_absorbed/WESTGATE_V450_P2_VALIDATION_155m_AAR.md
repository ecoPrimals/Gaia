# AAR: westGate biomeOS v4.50 + P2 Divergence Validation — Wave 155m

**Date**: Jul 30, 2026 20:30 EDT
**Gate**: westGate
**Wave**: 155m
**Author**: westGate overwatch (AI-assisted)
**Classification**: DISSEMINATE — all teams, especially biomeOS

---

## EXECUTIVE SUMMARY

Deployed biomeOS v4.50 and all 5 divergence-fixed binaries to westGate. 13/13 primals active, 29-31 sockets, Coordinated mode with 835 peak capabilities. Provenance Trio 7/7 continues to pass. **Critical finding: socket evaporation is NOT fixed in v4.50** — biomeOS still deletes other primals' socket files during its RPC ping/prune cycle, dropping from 29 to 17 sockets within 2 minutes.

---

## WHAT WE DID

### Cascade
7 repos pulled from golgiBody:
- **biomeOS** (+8 commits, +3,371/-4,952 lines) — v4.50: socket evap fix, binary path retention, cap wipe 3-strike, socket 0666
- **bearDog** (+3 commits, +438/-19,214 lines) — dual-socket, FAMILY_SEED precedence, massive orphan cleanup
- **cellMembrane** (+7 commits, +1,518/-1,126 lines) — membrane.exe P1, checksums, sandbox, rootpulse, tmpfiles, reqwest purge
- **toadStool** (+3 commits) — S349: JSON-RPC compute.sock, dead deps purged
- **petalTongue** (+3 commits) — `--family-id` propagation (global flag), `PRIMAL_BIND_MODE=tcp` semantics
- **wateringHole** (+15 commits) — sovereign CI AARs, divergence handoffs
- **whitePaper** (+2 commits) — gen4 COMPLETE checkpoint

### Depot Binary Updates
| Binary | Old Size | New Size | Delta | Notes |
|--------|----------|----------|-------|-------|
| biomeOS | 20,257 KB | 16,084 KB | **-4,173 KB** | Deep debt: futures→futures-util, dep narrowing |
| bearDog | 8,543 KB | 8,459 KB | -84 KB | 19K lines of orphan files deleted |
| toadStool | 13,135 KB | 13,131 KB | -3 KB | Stable |
| petalTongue | 34,169 KB | 34,157 KB | -11 KB | Stable |
| membrane | 15,679 KB | 13,688 KB | **-1,990 KB** | reqwest purge → sovereign HTTP client |

### NUCLEUS Composition
13/13 primals started in boot order (Tower → Nest → Node → Viz/AI → biomeOS LAST):
```
Tower:   bearDog ✓  songBird ✓  skunkBat ✓
Nest:    nestGate ✓  loamSpine ✓  sweetGrass ✓  rhizoCrypt ✓
Node:    toadStool ✓  barraCuda ✓  coralReef ✓
Viz:     petalTongue ✓
AI:      squirrel ✓
Orch:    biomeOS ✓ (v4.50, COORDINATED, 835 peak caps)
```

---

## P2 FIX VALIDATION RESULTS

### FIXED — Confirmed Working

| Fix | Commit | Result |
|-----|--------|--------|
| **toadStool JSON-RPC** | `5053e0bc` | ✓ Responds to `health.liveness` via riboCipher. compute.sock tarpc socket also present |
| **petalTongue `--family-id`** | `551e781` | ✓ Accepts `--family-id` as global flag (before `server` subcommand). Responds to health |
| **bearDog crypto.sign** | `a875d463` | ✓ Real Ed25519 signatures on family-scoped socket. FAMILY_SEED auto-generated |
| **biomeOS Coordinated mode** | `06ed323f` | ✓ Enters Coordinated mode when membrane symlinks present at startup. 835 caps peak |

### NOT FIXED — Socket Evaporation Persists

**biomeOS v4.50 still deletes other primals' socket files during the RPC ping/prune cycle.**

Observed behavior over 2 minutes after clean start:
```
t=  0s  socks:29  caps:835  ← stable, all sockets present
t= 60s  socks:29  caps:0    ← capability wipe cycle begins
t= 75s  socks:28  caps:274  ← first socket deleted
t= 90s  socks:17  caps:507  ← 12 sockets deleted!
t=105s  socks:17  caps:507  ← stabilizes at degraded level
```

Sockets evaporated: bearDog, songBird, nestGate, coralReef, squirrel (confirmed). The processes are still alive (PID confirmed, zero restarts), but the socket files on disk are deleted by biomeOS.

**Root cause hypothesis**: biomeOS v4.50's "Any successful `call_btsp()` = alive" fix works, but the RPC pings FAIL for primals that:
- Require riboCipher framing (toadStool, sweetGrass)
- Have different transport expectations
- Return non-standard health responses

When pings fail, biomeOS prunes the primal AND deletes its socket file. **biomeOS must not delete socket files it doesn't own.**

**Impact**: After socket evaporation, Provenance 7/7 fails (can't reach primals). Workaround: stop Neural API, restart affected primals, rebuild membrane symlinks, then restart Neural API.

### ALSO NOTED

| Issue | Status |
|-------|--------|
| bearDog dual-socket: `beardog-default.sock` still returns health stub, `beardog-westgate-tower-155f.sock` has real crypto | **Partial** — the sockets are separate listeners, not aliases. BEARDOG_SOCKET env var workaround effective |
| toadStool requires riboCipher for JSON-RPC health | **Working** — but plain JSON-RPC rejected ("Connection rejected: missing riboCipher signal") |
| sweetGrass requires riboCipher for health | Same pattern — Provenance 7/7 step 7 (braid.create) works with riboCipher prefix |
| biomeOS capability wipe cycle | Still drops to 0 caps then recovers. 3-strike prune threshold (v4.49) may not be tuned for this many primals |

---

## PROVENANCE 7/7 — STILL PASSING

```
  1. content.put → nestgate CAS          ✓  BLAKE3 content-addressed
  2. dag.session.create → rhizocrypt     ✓  Session created
  3. dag.event.append → rhizocrypt       ✓  DataCreate event
  4. dag.merkle.root → rhizocrypt        ✓  Cryptographic proof
  5. spine.create → loamspine            ✓  Certificate spine
  6. entry.append → loamspine+bearDog    ✓  Ed25519 SIGNATURE
  7. braid.create → sweetgrass           ✓  Attribution braid (JSON-LD PROV-O)
```
Chain validated with Neural API stopped (to prevent socket evaporation during test).

---

## METRICS

| Metric | Value |
|--------|-------|
| Services | **13/13 active** |
| Sockets (clean) | **29-31** (degrades to 17 during evaporation) |
| Peak capabilities | **835** (Coordinated mode) |
| Provenance Trio | **7/7 COMPLETE** |
| CAS objects | **3,254** on ZFS 25.4TB ONLINE |
| biomeOS binary | **16,084 KB** (v4.50, -4.2 MB from v4.47) |
| IPC-responsive primals | **9/10** (sweetGrass needs riboCipher for plain health) |
| ZFS health | ONLINE, healthy |

---

## UPSTREAM ACTION ITEMS

### P2 — Socket Evaporation (Critical for NUCLEUS stability)

**biomeOS must not delete socket files during prune cycles.** Socket files belong to the primal processes that created them. biomeOS should:
1. Track which sockets it created vs discovered
2. Only remove sockets it owns (its own Neural API socket)
3. Use additive discovery — keep existing registrations, add new ones
4. The 3-strike prune threshold should prevent premature pruning, but the RPC ping format mismatch causes all 3 strikes to fail on the same cycle

**Suggested fix**: biomeOS should verify socket ownership (via `/proc/$PID/fd` or fstat) before deleting. If the socket FD is held by another process, it's alive — don't delete the file.

### P3 — RPC Ping Format

biomeOS v4.50 pings all sockets with the same format. Some primals require:
- riboCipher `[0xEC, 0x01]` prefix (toadStool, sweetGrass)
- Different health methods
- tarpc binary protocol (toadStool's compute socket)

The ping should try both plain JSON-RPC and riboCipher-prefixed JSON-RPC before declaring a socket dead.

### P3 — bearDog Default Socket

`beardog-default.sock` is a separate listener that returns health stubs for `crypto.sign_ed25519`. The dual-socket fix (a875d463) should make the default socket an alias or ensure both sockets have the same capabilities.

---

## CONFIGURATION CHANGES

- `~/.config/systemd/user/petaltongue-tower.service`: `--family-id` moved to global flag position (before `server` subcommand)
- Depot binaries updated: biomeOS v4.50, bearDog, toadStool, petalTongue, membrane

---

*westGate Wave 155m — biomeOS v4.50 deployed. 13/13 NUCLEUS, 835 peak caps, Provenance 7/7 VALIDATED. Socket evaporation persists (P2 upstream). 3,254 CAS objects on ZFS 25.4TB. bearDog crypto.sign LIVE. gen4 COMPLETE — NUCLEUS IS THE PLATFORM.*
