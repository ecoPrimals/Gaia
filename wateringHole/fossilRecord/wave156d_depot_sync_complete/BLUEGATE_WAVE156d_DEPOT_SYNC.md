# blueGate Wave 156d — Depot Sync + UniBin Migration

**Gate**: blueGate | **Date**: 2026-08-04T18:40:00Z | **Wave**: 156d
**Status**: NUCLEUS 13/13 on v4.57+ depot binaries. UniBin CLI migration complete.

---

## DEPOT SYNC

14/14 binaries pulled from `depot.primals.eco/primals/x86_64-pc-windows-gnu/`:

| Binary | Size | Changed |
|--------|------|---------|
| beardog.exe | 7,682 KB | UPDATED (+3 KB) |
| toadstool.exe | 9,050 KB | UPDATED (-2 KB) |
| membrane.exe | 19,575 KB | same |
| biomeos.exe | 19,669 KB | same |
| songbird.exe | 20,806 KB | same |
| petaltongue.exe | 25,640 KB | same |
| sweetgrass.exe | 15,499 KB | same |
| nestgate.exe | 8,306 KB | same |
| squirrel.exe | 3,736 KB | same |
| skunkbat.exe | 2,641 KB | same |
| loamspine.exe | 4,184 KB | same |
| rhizocrypt.exe | 5,832 KB | same |
| barracuda.exe | 5,046 KB | same |
| coralreef.exe | 7,013 KB | same |

---

## UNIBIN CLI MIGRATION

All primals migrated from flat `--bind` flags to `server` subcommand + structured args.

### Old (v4.56) → New (v4.57+) Command Map

| Primal | Old | New |
|--------|-----|-----|
| bearDog | `beardog --bind 127.0.0.1:9100` | `beardog server --listen 127.0.0.1:9100` |
| songBird | `songbird --listen 127.0.0.1:7700 --http 127.0.0.1:7701` | `songbird server --bind 127.0.0.1 --port 7700` |
| skunkBat | `skunkbat --bind 127.0.0.1:9102` | `skunkbat server --bind 127.0.0.1 --port 9102` |
| nestGate | `nestgate --bind 127.0.0.1:9200` | `nestgate service start --listen 127.0.0.1:9200` |
| loamSpine | `loamspine --bind 127.0.0.1:9201` | `loamspine server --bind-address 127.0.0.1 --port 9201` |
| rhizoCrypt | `rhizocrypt --bind 127.0.0.1:9202` | `rhizocrypt server --port 9202 --bind 127.0.0.1` |
| sweetGrass | `sweetgrass --bind 127.0.0.1:9213` | `sweetgrass server --port 127.0.0.1:9213` |
| petalTongue | `petaltongue --bind 127.0.0.1:9204` | `petaltongue server --port 9204 --bind 127.0.0.1` |
| squirrel | `squirrel --bind 127.0.0.1:9205` | `squirrel server --port 9205 --bind 127.0.0.1` |
| toadStool | `toadstool --bind 127.0.0.1:9300` | `toadstool server --bind 127.0.0.1:9300` |
| barraCuda | `barracuda --bind 127.0.0.1:9301` | `barracuda server --bind 127.0.0.1:9301` |
| coralReef | `coralreef --bind 127.0.0.1:9302` | `coralreef server --port 9302` |
| biomeOS | `biomeos api --bind 127.0.0.1:9090` | `biomeos api --bind 127.0.0.1 --port 9090` |

Key env var: `PRIMAL_BIND_MODE=tcp` (forces TCP transport on Windows).

---

## HEALTH VALIDATION

```
bearDog(:9100):    OK — {"status":"alive","version":"0.9.0"}
songBird(:7700):   OK — {"status":"healthy","services":0}
skunkBat(:9102):   OK — connected (no health method, uses different RPC)
nestGate(:9200):   OK — HTTP 400 (expects REST, not raw JSON-RPC — correct)
loamSpine(:9201):  OK — {"status":"ok","version":"0.9.16"}
rhizoCrypt(:9202): OK — connected (tarpc binary protocol)
sweetGrass(:9213): OK — {"status":"healthy","braid_count":0}
petalTongue(:9204):OK — connected (riboCipher gate — security working)
squirrel(:9205):   OK — {"status":"healthy","version":"0.1.0"}
toadStool(:9300):  OK — riboCipher signature required (BTSP active)
barraCuda(:9301):  OK — {"status":"alive"}
coralReef(:9302):  OK — connected (dispatch method routing active)
biomeOS(:9090):    OK — HTTP listening on 9090

Total RSS: 215 MB (13 primals + dnsproxy)
```

---

## ISSUES ENCOUNTERED

### 1. UniBin CLI Breaking Change (P3 — expected)
All primals now require `server` subcommand. The old `--bind` top-level flag
produces "unexpected argument" errors. This is a documented migration.

### 2. songBird Stale PID File — AGAIN (P3 — recurring)
New PID path: `C:\var\run\songbird\songbird-blueGate.pid` (now includes gate name).
Same issue: stale PID from previous session blocks startup. Manual cleanup required.

### 3. biomeOS `--bind` Format Changed (P4)
Old: `--bind 127.0.0.1:9090` (host:port combined)
New: `--bind 127.0.0.1 --port 9090` (split args)
Combined format binds to ephemeral port and ignores the port number.

---

## CURRENT POSTURE

```
NUCLEUS:     13/13 on v4.57+ depot
DNS proxy:   RUNNING (dnsproxy, port 53)
SSHD:        Running/Automatic
Sub-builder: Ready (J12 dispatch operational)
RSS:         215 MB total
```

---

*blueGate 156d — depot synced (14/14 binaries), UniBin CLI migration complete,
NUCLEUS 13/13 healthy on new binaries. songBird PID file issue recurring.
215 MB total RSS. Sub-builder + DNS secondary operational.*
