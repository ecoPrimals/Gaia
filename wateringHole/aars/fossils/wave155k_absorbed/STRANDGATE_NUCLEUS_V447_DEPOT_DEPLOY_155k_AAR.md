# AAR: strandGate NUCLEUS v4.47 Depot Deploy — Wave 155k

**Date**: Jul 30, 2026 10:10 EDT
**Gate**: strandGate
**Team**: strandGate hardware/overwatch
**Wave**: 155k
**Classification**: DEPLOYMENT — biomeOS v4.47 lifecycle-managed NUCLEUS from depot

---

## EXECUTIVE SUMMARY

Deployed NUCLEUS on strandGate using **depot-path genomeBins** and biomeOS v4.47's
`nucleus start` lifecycle manager. biomeOS successfully launched all 12 primals from
`~/.local/bin/` in composition order. All processes run, all kernel sockets listen.
However, **biomeOS's health monitoring causes socket evaporation** — it removes
filesystem socket entries for primals whose RPC ping fails, breaking direct IPC
access. This is a P2 maturity issue, not a composition failure.

---

## WHAT WE DID

### 1. Cascaded Wave 155k from golgiBody

| Repo | Delta | Key Changes |
|------|-------|-------------|
| biomeOS | +6 commits | v4.47: riboCipher fix, socket unification, composition lifecycle, `nucleus start` |
| bearDog | +2 commits | `crypto.sign_ed25519` real signing + Windows platform gating |
| songBird | +1 commit | TCP registration fix + Windows maturity |
| loamSpine | +1 commit | `--bind` alias for composition lifecycle |
| sweetGrass | +1 commit | `braid_id→UUID` mismatch fix |
| rhizoCrypt | +2 commits | Cross-compile hygiene + `--bind` alias |
| wateringHole | +21 commits | blueGate NUCLEUS, depot rebuild, chain closures, 50 fossilized handoffs |

### 2. Pulled 11 genomeBins from Depot

All binaries fetched from `depot.primals.eco/primals/`:

| Target | Binaries | Sizes |
|--------|----------|-------|
| `x86_64-unknown-linux-musl` | beardog, songbird, skunkbat, nestgate, loamspine, sweetgrass, rhizocrypt, biomeos | 3.0–20 MB |
| `x86_64-unknown-linux-gnu` | barracuda, coralreef, toadstool | 5.3–13 MB |

Versions confirmed matching blurb: bearDog 0.9.0, songBird 0.2.1, skunkBat 0.2.18,
biomeOS 0.1.0, barraCuda 0.4.0, coralReef 0.2.0, nestGate 0.5.0, loamSpine 0.9.16,
sweetGrass 0.8.0, rhizoCrypt 0.14.17, toadStool 0.2.0.

### 3. Deployed via `biomeos nucleus start`

```bash
biomeos nucleus start --node-id strandGate --mode full
```

biomeOS v4.47 lifecycle manager:
- Discovered all 12 primal binaries in `~/.local/bin/`
- Launched in composition order: bearDog → songBird → skunkBat → toadStool → coralReef → barraCuda → nestGate → rhizoCrypt → loamSpine → sweetGrass → squirrel → petalTongue
- Created unified socket directory: `/run/user/1000/membrane/`
- Created capability symlinks (security→skunkbat, dag→rhizocrypt, permanence→loamspine, etc.)
- Registered auto-discovery topology (22 entries)
- Supervised processes with health monitoring and auto-respawn

---

## RESULTS

### What Worked

1. **biomeOS v4.47 `nucleus start` launches all 12 primals** from depot genomeBins
2. **All 12 processes running** — confirmed via `ps`:
   - beardog, songbird, skunkbat, toadstool, coralreef, barracuda, nestgate, rhizocrypt, loamspine, sweetgrass, squirrel, petaltongue
3. **All kernel sockets listening** — confirmed via `ss -xl`:
   - All 12 family-scoped sockets (`*-e8b62b6e.sock`) present in kernel
4. **Unified socket path** — `membrane/` replaces `biomeos/`
5. **Capability-based symlinks** — biomeOS creates domain aliases (security, dag, permanence, provenance, ai, visualization, x25519)
6. **Supervised lifecycle** — biomeOS tracks PIDs, detects failures, attempts respawn
7. **Auto-respawn works** — for primals with tracked binary paths (sweetGrass, toadStool)
8. **Structured logging** — per-primal logs in `membrane/logs/`

### What Failed — Socket Evaporation (P2)

biomeOS's health monitoring **removes filesystem socket entries** for primals whose
RPC ping fails. Observed sequence:

```
1. biomeOS launches primal → primal creates socket → biomeOS discovers it → ACTIVE
2. biomeOS periodic health ping (riboCipher-framed) fails:
   "🔴 RPC ping failed: /run/user/1000/membrane/songbird-e8b62b6e.sock"
3. After 3 failures: "🔴 songbird DEGRADED"
4. biomeOS attempts resurrection: "⚠️ No deployment node or binary path"
5. Socket entry removed: "🧹 Unregistered primal songbird: removed 25 capability registration(s)"
```

**Root causes**:

| Issue | Detail |
|-------|--------|
| RPC ping format | biomeOS pings with riboCipher framing; most depot primals respond to plain JSON-RPC only |
| Binary path tracking | biomeOS loses the binary path during auto-discovery phase, can't respawn primals it launched itself |
| sweetGrass/toadStool loop | These primals enforce riboCipher but biomeOS's specific ping format doesn't match → 20s kill/respawn cycle |

**Impact**: Processes alive, kernel sockets listening, but filesystem socket entries removed → direct IPC via `socat`/Python fails for most primals.

---

## COMPARISON: v4.47 lifecycle vs manual deploy (155i)

| Aspect | Manual Deploy (155i) | biomeOS v4.47 nucleus start (155k) |
|--------|---------------------|-------------------------------------|
| Primal launch | Manual `nohup` × 10 | Single command, biomeOS launches all 12 |
| Startup ordering | Manual (Tower→Nest→Node→biomeOS) | biomeOS manages automatically |
| Socket path | `/run/user/1000/biomeos/` | `/run/user/1000/membrane/` (unified) |
| Health monitoring | None (fire and forget) | Supervised with auto-respawn |
| Socket stability | Stable (no evaporation once biomeOS starts last) | **Unstable** (health ping removes entries) |
| Direct IPC access | 8/9 healthy, 674 methods | Processes alive but sockets evaporated |
| GPU compute | RTX 3090 validated, 0.30ms matmul | Not accessible (socket removed) |
| Operational complexity | High (10 nohup commands, ordering matters) | Low (one command) |

**Verdict**: biomeOS v4.47 lifecycle management is a significant improvement for deployment
ergonomics. The health monitoring evaporation is a P2 that needs one more iteration: either
standardize RPC ping format across all primals, or make biomeOS tolerant of primals that
respond to plain JSON-RPC but not riboCipher.

---

## RECOMMENDATIONS

### For eastGate / biomeOS team (P2)

1. **RPC ping tolerance** — biomeOS health ping should try plain JSON-RPC if riboCipher
   ping fails, before declaring the primal dead. All depot primals respond to `health.check`
   via plain JSON-RPC.

2. **Binary path retention** — `nucleus start` launches primals from known paths but loses
   this mapping during auto-discovery. The binary path should persist so resurrection works
   for ALL primals, not just the ones biomeOS can re-discover.

3. **sweetGrass/toadStool ping cycle** — these primals enforce riboCipher but biomeOS's
   specific ping format still triggers rejection. The kill/respawn loop wastes resources.
   Either fix the ping format or exempt primals that biomeOS just respawned from immediate
   re-checking.

### For strandGate (this gate)

- **Depot-path deployment works** — genomeBins are current, `nucleus start` launches everything
- **Wait for biomeOS health ping fix** — then redeploy for stable lifecycle-managed NUCLEUS
- **Manual deploy remains viable** — the 155i approach (nohup + biomeOS last) still works
  if uninterrupted IPC access is needed for validation or profiling

---

## DEPOT STATUS

| Binary | Version | Target | Source |
|--------|---------|--------|--------|
| beardog | 0.9.0 | musl | depot.primals.eco |
| songbird | 0.2.1 | musl | depot.primals.eco |
| skunkbat | 0.2.18 | musl | depot.primals.eco |
| biomeos | 0.1.0 | musl | depot.primals.eco |
| nestgate | 0.5.0 | musl | depot.primals.eco |
| loamspine | 0.9.16 | musl | depot.primals.eco |
| sweetgrass | 0.8.0 | musl | depot.primals.eco |
| rhizocrypt | 0.14.17 | musl | depot.primals.eco |
| barracuda | 0.4.0 | glibc | depot.primals.eco |
| coralreef | 0.2.0 | glibc | depot.primals.eco |
| toadstool | 0.2.0 | glibc | depot.primals.eco |

All binaries deployed to `~/.local/bin/`, verified with `--version`.

---

## FINDINGS SUMMARY

| # | Finding | Severity | Owner |
|---|---------|----------|-------|
| 1 | biomeOS v4.47 `nucleus start` successfully launches all 12 primals | **POSITIVE** | — |
| 2 | Socket path unified to `membrane/` | **POSITIVE** | — |
| 3 | Capability symlinks created automatically | **POSITIVE** | — |
| 4 | Health ping removes sockets for plain-JSON-RPC primals | P2 | biomeOS |
| 5 | Binary path lost during auto-discovery, blocks resurrection | P2 | biomeOS |
| 6 | sweetGrass/toadStool in 20s kill/respawn loop | P2 | biomeOS |
| 7 | bearDog capabilities.list response format unrecognized | P3 | bearDog + biomeOS |
| 8 | Depot musl binaries for GPU trio (glibc) separate — correct and working | NOTE | — |

**ZERO P0/P1s.** All findings are P2 maturity issues in biomeOS's health monitoring loop.
The composition itself is valid — all primals launch, run, and listen.

---

*strandGate — Wave 155k depot-path NUCLEUS deploy. biomeOS v4.47 lifecycle manager launches
all 12 primals. Socket evaporation from health ping mismatch is the remaining P2. All
processes running, all kernel sockets listening. Awaiting biomeOS ping tolerance fix for
stable lifecycle-managed NUCLEUS.*
