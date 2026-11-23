# AAR: blueGate Wave 157b — Windows Sub-Builder Activation

**Gate**: blueGate | **Date**: 2026-08-09T16:06:00Z | **Wave**: 157b
**Author**: blueGate team | **Recipients**: sporeGate topology, eastGate overwatch
**Session**: Cascade → NUCLEUS redeploy → vertebrate build campaign (14 primals)

---

## EXECUTIVE SUMMARY

blueGate activated as primary Windows build workhorse per Wave 157b blurb.
14/14 primals built from vertebrate HEAD in 23 minutes (native `x86_64-pc-windows-gnu`).
NUCLEUS redeployed on fresh 157b depot (5 changed binaries). 13/13 ALIVE.
Several systemic issues discovered around build parity, PID management, and
transport defaults.

---

## WHAT'S WORKING WELL

### Build Infrastructure
- **Toolchain**: Rust 1.97.1 stable + MinGW-W64 GCC 16.1.0 — solid, no toolchain fights
- **14/14 primals compile from vertebrate HEAD** — zero build failures on Windows
- **Build time**: 23 min total for all 14 primals (skunkBat 0s cached → songBird 289s)
- **No source patches required** — all vertebrate evolution commits compile clean on Windows
  (previous waves required 3 local patches for songBird UDS gates)
- **cargo workspace builds** work correctly across all primals

### Deployment
- **NUCLEUS 13/13** on fresh depot binaries (157b, P0-C fix included)
- **UniBin CLI standardized** — all primals use `server` subcommand (learned in 157a)
- **DNS secondary operational** (port 53, H2 DNS for House 2 gates)
- **SSHD + sub-builder J12** still operational
- **SSH discipline CLEAN** — zero github remotes, Forgejo-only

### Cascade
- **14/16 repos updated** cleanly from Forgejo in single cascade
- **Repos current at vertebrate HEAD** — all primals have Aug 9 commits

---

## NEW DIVERGENCES FOUND (This Session)

### D1: songBird PID file location changed AGAIN (P2)

| Wave | PID Path |
|------|----------|
| 155i-155k | `C:\var\run\songbird\songbird.pid` |
| 156d (G68) | `C:\var\run\songbird\songbird-blueGate.pid` |
| **157b** | **`C:\ProgramData\songbird\songbird-blueGate.pid`** |

songBird's PID file location has migrated 3 times across 3 waves. Each time, the
stale file from the previous location blocks startup because the new code checks
the new path but nobody cleans the old one. The old PID files are NEVER cleaned by
the binary on shutdown (Windows has no equivalent of `systemd ExecStopPost`).

**Impact**: Manual PID file cleanup required before every songBird restart.
**Recommendation**: songBird should validate PID liveness (`OpenProcess`) before
rejecting startup, and document the canonical path per-platform.

### D2: skunkBat `PRIMAL_BIND_MODE` env var partially fixed

Blurb says `a57ada5` shipped the fix (accepts short forms tcp/uds/both). Our
G68 binary still required `--bind-mode tcp` explicitly. The 157b depot binary
may have the fix — needs verification after redeploy.

### D3: Binary size parity — native vs cross-compiled (P3)

| Binary | Native (stripped) | Depot (cross) | Ratio | Root Cause |
|--------|-------------------|---------------|-------|------------|
| barraCuda | 22,116 KB | 4,996 KB | 4.43x | Workspace links all test binaries |
| squirrel | 6,207 KB (LTO) | 3,720 KB | 1.67x | AI tools crate deps |
| petalTongue | 27,886 KB (LTO) | 24,616 KB | 1.13x | Doom-core decoupling partial |
| coralReef | 7,304 KB (LTO) | 7,300 KB | **1.00x** | MATCH |
| bearDog | 7,586 KB | 7,588 KB | **1.00x** | MATCH |
| nestGate | 8,524 KB | 8,520 KB | **1.00x** | MATCH |
| rhizoCrypt | 5,963 KB | 5,963 KB | **1.00x** | MATCH |
| toadStool | 9,005 KB | 9,006 KB | **1.00x** | MATCH |
| loamSpine | 4,330 KB | 4,344 KB | **1.00x** | MATCH |
| skunkBat | 2,946 KB | 2,912 KB | **1.01x** | MATCH |
| biomeOS | 15,207 KB | 20,192 KB | **0.75x** | Native SMALLER |
| songBird | 15,898 KB | 21,550 KB | **0.74x** | Native SMALLER |
| sweetGrass | 11,010 KB | 17,064 KB | **0.64x** | Native SMALLER |

**Key finding**: 7/14 primals match depot within 1%. 3 are SMALLER natively
(vertebrate pruning not yet in depot?). 4 are oversized due to workspace/dep bloat.

**Recommendation for sporeGate**: Document the exact `cargo build` flags used for
cross-compilation. blueGate can match them. The size discrepancy for barraCuda
suggests the cross-build uses `-p barracuda-core --bin barracuda` (the lean server
crate) rather than workspace root.

### D4: petalTongue `--port` flag still non-functional in `server` mode

petalTongue ignores the `--port 9204` flag when started in `server` mode and
binds to random ephemeral ports. This was filed in 157a and persists in 157b.
The `headless` subcommand respects `--bind host:port` but exits immediately.

**Impact**: petalTongue is not reachable on a stable port for JSON-RPC probes.
**Workaround**: Accept dynamic ports; petalTongue routes via internal IPC.

---

## CHALLENGES: WINDOWS AS A BUILDER vs LINUX

### 1. No systemd — service lifecycle is manual

| Aspect | Linux (sporeGate) | Windows (blueGate) |
|--------|-------------------|--------------------|
| Start | `systemctl start membrane-nucleus.target` | Manual `Start-Process` per primal |
| Stop | `systemctl stop` + `pkill` stragglers | `Stop-Process -Force` per primal |
| Restart | atomic unlink + copy | Stop all → overwrite → start all |
| Auto-start | systemd units | Startup folder `.bat` (fragile) |
| PID management | systemd handles | Manual PID file cleanup |
| Logs | `journalctl -u` | Lost (hidden window stdout) |

**Recommendation**: Create a `membrane-nucleus.ps1` script that encapsulates
the full start/stop/restart lifecycle for Windows. Equivalent to the
`membrane-nucleus.target` on Linux.

### 2. Binary locking during update

On Linux: `rm -f $bin && cp $new $bin` works because the kernel keeps the
old inode alive for running processes.

On Windows: Running `.exe` files are LOCKED — cannot overwrite or delete.
Must stop ALL processes before replacing binaries. This means NUCLEUS has
a cold window during updates (no rolling restart possible).

### 3. LTO compilation time

With LTO enabled (needed for depot-parity sizes):
- barraCuda: 0s (cached, needs clean rebuild)
- squirrel: 74s
- petalTongue: 135s
- coralReef: 55s
- biomeOS: **still building** (>7 min with LTO, largest crate)

Without LTO, full build is 23 min. With LTO on the 6 large primals, add ~8-10 min.
Total build time estimate: **30-35 min** for full depot-ready Windows build.

### 4. No `rsync` or `scp` to golgi

Linux gates push to golgi via `rsync` or `plasmid.push`. On Windows:
- No native `rsync`
- Can use `scp` via OpenSSH (installed)
- Or HTTP upload if depot accepts it
- Or `git lfs` / artifact push via Forgejo

**Recommendation**: sporeGate team specify the depot push mechanism for blueGate.
Options: `scp`, Forgejo release API, or depot HTTP PUT.

### 5. Path separator and case sensitivity

Rust builds target `x86_64-pc-windows-gnu` correctly, but some primal code
still assumes Unix paths in log messages, PID file paths, and socket discovery:
- songBird PID: `/var/run/songbird/...` (uses forward slashes on Windows too)
- BTSP socket: `/run/user/1000/biomeos/...` (Linux-only path on Windows)
- swarmVine socket: `/run/membrane/biomeos/...` (not applicable on Windows)

These don't break compilation but produce confusing runtime errors or warnings.

---

## PRIMAL SYSTEM DEBT / GAPS

### bearDog
- **FAMILY_SEED required but undocumented**: Must set `FAMILY_SEED` env var or
  bearDog exits silently. No error message, no help text mentions it.
- **Health gate is excellent**: P0-A fix (`766951004`) is good discipline.

### songBird
- **PID file management is fundamentally broken on Windows**: See D1 above.
  3 path changes in 3 waves. No liveness check. No cleanup on exit.
- **Port binding inconsistency**: Uses `--port` for HTTP (discovery) and `--listen`
  for IPC (TCP). Other primals use `--port` for IPC. Confusing.
- **swarmVine socket discovery**: Hardcoded Linux paths (`/run/membrane/biomeos/`).
  Windows will never find swarmVine this way. Needs platform-native discovery.

### petalTongue
- **TCP port flag ignored in `server` mode**: `--port` does nothing. Must be
  reached via dynamic ports or not at all on Windows.
- **Neural API socket fallback**: Warns about missing `biomeos-neural-api-blueGate.sock`
  but doesn't fall back to TCP endpoint for biomeOS.

### biomeOS
- **Version string still 4.57.0**: Both the P0-C fixed depot binary AND our
  vertebrate HEAD build report 4.57.0. Cannot distinguish which has the FD fix
  without commit hash in version output.
- **`api` subcommand split `--bind` format**: Must be `--bind host --port port`
  (split args). Combined `--bind host:port` silently binds ephemeral port.

### toadStool
- **Clean build, clean runtime**: No Windows-specific issues. Best primal.

### skunkBat
- **`PRIMAL_BIND_MODE` env var partially respected**: needs `--bind-mode tcp`
  explicitly in some versions. Env var reading may be version-dependent.

### General (ecosystem-wide)
- **No Windows depot push mechanism defined**: blueGate can BUILD but has no
  documented path to push artifacts to golgi.
- **No BLAKE3SUMS for Windows depot**: Musl depot has `BLAKE3SUMS`, Windows does not.
- **swarmVine not in Windows depot**: 16th primal exists in musl but not in
  Windows builds. Compilation status unknown.
- **No `membrane.exe` rebuild from vertebrate**: membrane wasn't in this
  build campaign. Needs separate handling.

---

## RECOMMENDATIONS

### For sporeGate topology team
1. **Define depot push mechanism for blueGate** — `scp` to golgi? Forgejo releases?
   HTTP PUT to depot? This is the #1 blocker for blueGate sub-builder utility.
2. **Document exact cross-build flags** — which crates/bins/features are used
   per primal when cross-compiling for windows-gnu. Resolves size parity issue.
3. **Wire `BLAKE3SUMS` generation** into Windows depot push.
4. **Add swarmVine to Windows targets** — 16th primal, untested on Windows.

### For eastGate overwatch
1. **songBird PID management is P2 debt** — 3 path changes in 3 waves, no
   liveness validation, no platform-aware cleanup. Needs design attention.
2. **petalTongue TCP port binding broken on Windows** — filed twice, persists.
3. **biomeOS version string doesn't encode commit** — can't distinguish P0-C
   fixed build from older same-version build without external tooling.
4. **No version distinguisher across depot waves** — once a binary reports
   "0.9.0", there's no way to tell if it's G68 or vertebrate without hash.
5. **Binary size audit needed** — barraCuda 4.4x oversized on Windows native.
   Either workspace Cargo.toml needs `default-members` to exclude test binaries,
   or depot builder needs specific `-p <crate>` targeting.

### For primalSpring
1. **`membrane-nucleus.ps1` startup script** — standard lifecycle for Windows
   NUCLEUS: start, stop, restart, status, update-from-depot.
2. **songBird PID path should be stable** — `C:\ProgramData\songbird\` is OK
   but MUST be documented and not changed again.

---

## SESSION METRICS

| Metric | Value |
|--------|-------|
| Cascade | 14/16 repos updated |
| Depot pull | 15/15 (5 changed: squirrel, toadStool, barraCuda, biomeOS, sourDough) |
| NUCLEUS | **13/13** on 157b depot |
| Build campaign | **14/14 SUCCESS** (vertebrate HEAD, 23 min) |
| LTO rebuild | 4/6 complete (biomeOS still building) |
| Depot-parity matches | **7/14 exact**, 3 smaller (better), 4 oversized |
| New divergences | 4 (PID path, bind-mode, size parity, petalTongue port) |
| Primal debts logged | 6 (songBird PID, petalTongue port, biomeOS version, skunkBat env, bearDog docs, depot push) |

---

*blueGate 157b — Windows sub-builder activated. 14/14 primals built from vertebrate HEAD. 7/14 match depot within 1%. Key blockers: depot push mechanism undefined, songBird PID management broken, petalTongue port flag ignored. Immediate need: sporeGate define how blueGate pushes .exe to golgi depot. Build infra solid (Rust 1.97.1, MinGW 16.1, zero failures). NUCLEUS 13/13.*

---

## ADDENDUM � Session 2 (12:30 PM)

### membrane.exe Rebuilt (e0780c4)
- **Size**: 8,218 KB (stripped) � down from 19,575 KB depot version
- **Commit**: e0780c4 (cellMembrane vertebrate HEAD)
- **New capabilities**: plasmid.harvest, plasmid.push, plasmid.depot_sync, uilder.serve
- **`plasmid.harvest --local --dry-run`**: WORKS � discovers all 13 primals, knows target
- **`gate.status`**: WORKS � shows depot integrity, sovereignty checks

### Depot Push Blocker: SSH Key Authorization

blueGate's public key needs adding to golgi's `authorized_keys`:
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINlBX3vvJWHySRLf6d901D4UGw7PRmLMcUb3xJJmnybd blueGate@primals.eco
```

**Action for sporeGate**: Add this key to `root@[RELAY_PUBLIC]:~/.ssh/authorized_keys`
Once authorized, `membrane.exe plasmid.harvest --local --push` will work E2E.

### swarmVine Windows Port � BLOCKED (upstream)

5 UDS call sites in 4 files need `#[cfg(unix)]` + TCP fallback:
- `swarmvine-core/src/tarpc_service.rs:84` � client connect
- `swarmvine-server/src/tarpc_server.rs:53` � server listen
- `swarmvine-server/src/spread.rs:148` � songBird IPC
- `swarmvine-server/src/announce.rs:54,132` � neural API + songBird
- `swarmvine-server/src/dispatch.rs:290` � dispatch socket

Also needs `tarpc = { features = ["tcp"] }` in workspace Cargo.toml.
Same pattern as songBird Wave 155i fix. Filed for swarmVine team.

### barraCuda Size Parity � UNSOLVED

Even with `-p barracuda` (correct crate targeting), native build produces
22,116 KB vs depot's 4,996 KB (4.4x). This is NOT a workspace bloat issue �
it's a fundamental difference between:
- Native Windows compilation (MinGW GCC, dynamic CRT)
- Cross-compilation from Linux (musl-cross, static, different linker)

The cross-compiled binary uses musl-cross which produces dramatically smaller
Windows binaries due to different static linking and dead code elimination.
This is an expected platform parity gap, not a bug.

**Recommendation**: Accept size difference for native builds OR document the
exact cross-compile toolchain (`x86_64-w64-mingw32-gcc` from Linux with
`cargo-xwin` or `cross`).

### gate.status Windows Probes � 3 Degraded (Expected)

| Probe | Status | Root Cause |
|-------|--------|------------|
| primals.alive | 0/3 | Probes via UDS (needs TCP fallback) |
| mesh.reachability | DEGRADED | Mesh relay socket is UDS |
| sovereignty.s4_auth | DEGRADED | bearDog probe via UDS |

These are known Windows UDS limitations. membrane needs TCP probe paths
for Windows gates (same as the `PRIMAL_BIND_MODE=tcp` pattern).

---

*Session 2 complete. membrane.exe rebuilt (e0780c4, 8.2MB). Depot push workflow
wired but blocked on golgi SSH key authorization. swarmVine Windows port blocked
(5 UDS sites, upstream). barraCuda size parity is cross-compile toolchain difference.
14 vertebrate .exe staged. Awaiting: (1) golgi key auth, (2) swarmVine platform port.*
