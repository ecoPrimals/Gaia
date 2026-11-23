# blueGate Wave 157a — G68 Gate Redeploy Complete

**Gate**: blueGate | **Date**: 2026-08-08T13:06:00Z | **Wave**: 157a
**Status**: NUCLEUS 13/13 on G68-converged depot. SSH discipline enforced. Sub-builder + DNS operational.

---

## DEPOT SYNC — 15/15 PULLED, 13 CHANGED

All Windows binaries pulled from golgi depot (`depot.primals.eco/primals/x86_64-pc-windows-gnu/`):

| Binary | Old (KB) | New (KB) | SHA256 prefix |
|--------|----------|----------|---------------|
| beardog.exe | 7,682 | 7,588 | 722777C6ADF7 |
| songbird.exe | 20,806 | 21,550 | 8F5727E35007 |
| skunkbat.exe | 2,641 | 2,912 | F9363C7428B1 |
| nestgate.exe | 8,306 | 8,520 | A2ABFBE8D3C7 |
| loamspine.exe | 4,184 | 4,344 | 420B4784AC3E |
| rhizocrypt.exe | 5,832 | 5,963 | 6A364306C522 |
| sweetgrass.exe | 15,499 | 17,064 | D18BDAD00C90 |
| petaltongue.exe | 25,640 | 24,616 | 61A05F90D452 |
| toadstool.exe | 9,050 | 9,002 | 80EF1D6132D7 |
| barracuda.exe | 5,046 | 5,071 | 2BEC558E3979 |
| coralreef.exe | 7,013 | 7,300 | 3BC5D789ADF6 |
| biomeos.exe | 19,669 | 20,408 | 82DFFA9DD3F3 |
| sourdough.exe | 2,816 | 2,895 | B803489504B1 |
| squirrel.exe | 3,736 | 3,736 | E3173D185C80 (same) |
| membrane.exe | 19,575 | 19,575 | E033B495B6FC (same) |

Notable: sweetGrass +1.5MB (capability.call handler shipped), petalTongue -1MB (cleanup), biomeOS +739KB (v4.57.0 neural API).

---

## VERSION CONFIRMATION

| Primal | Version | Notes |
|--------|---------|-------|
| biomeOS | **4.57.0** | Up from 4.56.0. Stage 2. |
| bearDog | 0.9.0 | |
| songBird | 0.2.1 | |
| nestGate | 0.5.0 | |
| loamSpine | 0.9.16 | |
| toadStool | 0.2.0 | S369 cross-arch |
| squirrel | 0.1.0 | |
| sourdough | 0.4.0 | Live convergence validator |
| membrane | 0.1.0 (edb7f4d) | |
| petalTongue | 1.7.0 | |

---

## HEALTH VALIDATION

```
bearDog(:9100):    {"status":"alive","version":"0.9.0"}
songBird(:7700):   {"status":"healthy","uptime_s":57}
skunkBat(:9102):   connected (tcp-only mode, BTSP active)
nestGate(:9200):   HTTP 400 (REST endpoint, not raw JSON-RPC — correct)
loamSpine(:9201):  {"status":"ok","version":"0.9.16"}
rhizoCrypt(:9202): connected (tarpc binary protocol)
sweetGrass(:9213): {"status":"healthy","braid_count":0}
petalTongue:       running (dynamic port, proprietary IPC)
squirrel(:9205):   {"status":"healthy","version":"0.1.0"}
toadStool(:9300):  riboCipher required (BTSP gate — security working)
barraCuda(:9301):  {"status":"alive"}
coralReef(:9302):  connected (dispatch method routing)
biomeOS(:9090):    HTTP listening (REST API)
```

Total RSS: **264 MB** (13 primals + dnsproxy)

---

## ISSUES — G68 SPECIFIC

### 1. skunkBat PRIMAL_BIND_MODE env var not respected (P3)
The G68 skunkBat binary defaults to "fallback" mode (TCP + UDS) even when
`PRIMAL_BIND_MODE=tcp` is set. UDS then fails on Windows with:
```
Error: Transport(Io(Custom { kind: Unsupported, error: "UDS not available on this platform..." }))
```
**Fix**: Pass `--bind-mode tcp` explicitly on the command line.
**Upstream**: skunkBat should read `PRIMAL_BIND_MODE` env var at startup.

### 2. petalTongue --port flag ignored in server mode (P4)
`petaltongue server --port 9204` binds to random ephemeral ports instead.
The `headless` subcommand respects `--bind host:port` but exits after init (one-shot).
**Workaround**: Accept dynamic ports; petalTongue uses internal IPC routing.
**Upstream**: petalTongue `server` mode TCP port binding on Windows.

### 3. songBird stale PID file — recurring (P3)
Path now `C:\var\run\songbird\songbird-blueGate.pid` (gate-aware naming).
Same issue: stale file from previous session blocks startup.
**Fix**: Clean `C:\var\run\songbird\*` before starting songBird.

---

## SSH KEY DISCIPLINE

- **github remotes**: ZERO across all repos (verified)
- **Access model**: blueGate pushes only to Forgejo (`git.primals.eco:2222`) via SSH key `blueGate`
- **No GitHub SSH config** on this machine
- **Compliant** with Wave 157a K-Derm relay enforcement

---

## STARTUP COMMANDS — G68 REFERENCE

```powershell
$env:PRIMAL_BIND_MODE = "tcp"
$env:FAMILY_SEED = "<base64-seed>"
$env:MEMBRANE_GATE_NAME = "blueGate"

# Clean stale state
Remove-Item "C:\var\run\songbird\*" -Force -ErrorAction SilentlyContinue

# Tower Atomic
beardog.exe server --listen 127.0.0.1:9100
songbird.exe server --bind 127.0.0.1 --port 7700
skunkbat.exe server --bind-mode tcp --bind 127.0.0.1 --port 9102

# Nest Atomic
nestgate.exe service start --listen 127.0.0.1:9200
loamspine.exe server --bind-address 127.0.0.1 --port 9201
rhizocrypt.exe server --port 9202 --bind 127.0.0.1
sweetgrass.exe server --port 127.0.0.1:9213
petaltongue.exe server --port 9204 --bind 127.0.0.1
squirrel.exe server --port 9205 --bind 127.0.0.1

# Node Atomic
toadstool.exe server --bind 127.0.0.1:9300
barracuda.exe server --bind 127.0.0.1:9301
coralreef.exe server --port 9302

# biomeOS
biomeos.exe api --bind 127.0.0.1 --port 9090
```

---

## POSTURE

```
NUCLEUS:       13/13 G68-converged (v4.57.0 biomeOS, S369 toadStool)
DNS proxy:     RUNNING (port 53, H2 DNS secondary)
SSHD:          Running/Automatic
Sub-builder:   Ready (J12 dispatch)
SSH discipline: COMPLIANT (Forgejo-only, no github remotes)
G68 violations: 0 (prod-clean)
RSS:           264 MB total
```

---

*blueGate 157a — G68 gate redeploy complete. 15/15 depot pulled (13 changed), NUCLEUS 13/13 healthy on G68-converged binaries. biomeOS 4.57.0. SSH key discipline enforced (Forgejo-only). 3 Windows-specific issues logged (skunkBat bind-mode env, petalTongue port, songBird PID). 264 MB RSS. Sub-builder + DNS operational.*
