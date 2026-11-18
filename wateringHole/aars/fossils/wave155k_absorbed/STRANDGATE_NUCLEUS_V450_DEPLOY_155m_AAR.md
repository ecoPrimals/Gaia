# AAR: strandGate NUCLEUS v4.50 Deploy — Wave 155m

**Date**: Jul 30, 2026 20:20 EDT
**Gate**: strandGate
**Team**: strandGate hardware/overwatch
**Wave**: 155m
**Classification**: DEPLOYMENT — biomeOS v4.50 (source) lifecycle-managed NUCLEUS

---

## EXECUTIVE SUMMARY

Cascaded Wave 155m (biomeOS +8 commits including v4.50 P2 fixes, bearDog +3, petalTongue +3,
wateringHole +11). Deployed NUCLEUS using depot genomeBins (11 primals) + source-built
biomeOS v4.50. **All 12 primal processes run. All 18 kernel sockets listen.** However,
biomeOS's health monitoring still removes filesystem socket entries — the v4.50 fix targets
sporeGate's `plasmidBin/` structure, not strandGate's `~/.local/bin/` user-space deploy.

The composition is valid. The deployment ergonomics need one more iteration for
non-sporeGate deploy paths.

---

## CASCADE DELTA

| Repo | Delta | Key |
|------|-------|-----|
| biomeOS | +8 | v4.50: socket ownership `0666`, dead dep purge, futures narrowing |
| bearDog | +3 | dual-socket fix, FAMILY_SEED precedence, 94 orphan files deleted |
| petalTongue | +3 | `--family-id` propagation, clippy zero warnings, deep debt |
| wateringHole | +11 | gen4 COMPLETE, gen5 reshape, biomeOS socket fix, 4 AAR fixes |

---

## DEPLOYMENT

### Depot Binaries (unchanged from 155k)
All 11 genomeBins in `~/.local/bin/` — verified current.

### biomeOS v4.50 (source-built)
Built from source at commit `0e45262f` (fix: socket ownership for multi-user access).
Includes both P2 fixes from blurb: `06ed323f` (evaporation + binary path).

### `biomeos nucleus start --node-id strandGate --mode full`

Lifecycle manager launched all 12 primals:
```
beardog → songbird → skunkbat → toadstool → coralreef → barracuda →
nestgate → rhizocrypt → loamspine → sweetgrass → squirrel → petaltongue
```

Family ID derived from `.family.seed`: `8ff3b864a4bc589a`
Socket path: `/run/user/1000/membrane/`

---

## RESULTS

### Confirmed Working

| # | What | Evidence |
|---|------|----------|
| 1 | All 12 primal processes running | `ps` shows all 12 PIDs from `~/.local/bin/` |
| 2 | All 18 kernel sockets listening | `ss -xl` confirms all `*-8ff3b864a4bc589a.sock` paths bound |
| 3 | sweetGrass accessible (riboCipher) | `health.check` → healthy v0.8.0 (0.2ms) |
| 4 | toadStool accessible (riboCipher) | `health.check` → alive v0.2.0 (0.2ms) |
| 5 | bearDog accessible (default socket) | `health.check` → alive v0.9.0 |
| 6 | biomeOS auto-discovery works | 35 ACTIVE transitions, capability registration |
| 7 | Unified membrane/ socket path | All sockets under `/run/user/1000/membrane/` |

### Still Broken — Socket Filesystem Evaporation

biomeOS health monitoring removes socket filesystem entries after 3 failed RPC pings.
The v4.50 fix (`06ed323f`) changed detection logic ("any successful `call_btsp()` = alive")
but pings still fail because:

1. **RPC ping format**: biomeOS sends a specific ping that most primals don't understand
2. **Binary path resolution**: v4.50 probes `./plasmidBin/primals/` — works for sporeGate's
   structure but not for strandGate's `~/.local/bin/` user-space deploy
3. **Resurrection fails**: "No deployment node or binary path for [primal]" for most primals

Timeline of evaporation:
```
T+0s:   biomeOS launches all 12 primals → all create sockets → all ACTIVE
T+10s:  Health pings start failing (format mismatch)
T+30s:  3 failures → DEGRADED → resurrection attempted → path not found
T+60s:  Unregistered → filesystem socket entry removed
         (kernel socket still listening, process still alive)
```

### Finding: Family ID Derivation

biomeOS v4.50 source build derives family ID from `.family.seed` file → `8ff3b864a4bc589a`.
The depot binary (v4.47-era) used `FAMILY_ID` env var → `e8b62b6e` (short prefix).
This is the bearDog fix `a875d463` "FAMILY_SEED precedence" — correct behavior,
but means socket names change between depot and source biomeOS.

---

## COMPARISON: v4.47 depot vs v4.50 source

| Aspect | v4.47 depot (155k) | v4.50 source (155m) |
|--------|-------------------|---------------------|
| Primal launch | All 12 ✓ | All 12 ✓ |
| Socket path | membrane/ | membrane/ |
| Family ID | e8b62b6e (env) | 8ff3b864a4bc589a (seed file) |
| Socket evaporation | Yes (all primals) | Yes (all except sweetGrass/toadStool) |
| Binary path for respawn | None found | `./plasmidBin/` (wrong for user-space) |
| Auto-respawn | sweetGrass/toadStool only | Same |
| sweetGrass/toadStool loop | Kill/respawn every 20s | Still cycling |

**Verdict**: v4.50 P2 fixes are incomplete for non-sporeGate deploy structures.
The fixes target sporeGate's `plasmidBin/` layout. strandGate deploys to `~/.local/bin/`.

---

## RECOMMENDATION FOR eastGate

The socket evaporation fix needs to account for user-space deploys:

1. **Binary path from nucleus start**: When `biomeos nucleus start` launches a primal
   from `~/.local/bin/X`, it should store that exact path for resurrection — not rely
   on probing `./plasmidBin/`.

2. **RPC ping fallback**: Try plain JSON-RPC `health.check` if riboCipher ping fails.
   bearDog responds to `{"jsonrpc":"2.0","method":"health.check","params":{},"id":1}` —
   that IS proof of life.

3. **Don't unlink kernel-bound sockets**: If `ss -xl` shows the socket is still listening,
   don't remove the filesystem entry.

---

## WHAT'S WORKING ON strandGate RIGHT NOW

Despite evaporation, the NUCLEUS IS RUNNING:
- 12 processes alive
- 18 kernel sockets listening
- sweetGrass + toadStool accessible via riboCipher
- bearDog accessible via default socket
- GPU hardware available (RTX 3090)
- All depot binaries current (Wave 155k rebuilt)

The composition is valid. The filesystem socket entries are the gap.

---

*strandGate — Wave 155m. biomeOS v4.50 source deploy. 12 primals running, 18 kernel
sockets. Socket evaporation persists (P2 fix targets sporeGate structure, not user-space).
All chains closed. Zero P0/P1. Awaiting next biomeOS iteration for strandGate deploy path.*
