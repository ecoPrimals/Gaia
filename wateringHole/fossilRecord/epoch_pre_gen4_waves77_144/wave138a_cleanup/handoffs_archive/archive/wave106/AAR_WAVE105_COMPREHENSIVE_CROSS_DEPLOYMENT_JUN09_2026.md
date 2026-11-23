# Comprehensive AAR: Wave 105 Cross-Deployment Campaign

**Date**: 2026-06-09
**From**: eastGate overwatch
**Scope**: Every deployment issue, pipeline problem, and interaction gap encountered during the Wave 104-105 cross-deployment push
**Purpose**: Reshape handoffs and FRAGOs going forward — evolve the ecosystem as gates redeploy, validating across all arch, WAN, LAN, and topologies

---

## 1. DEPLOYMENT ISSUES

### 1.1 Post-Primordial Depot Violation (Self-Inflicted, RESOLVED)

**What happened**: eastGate manually ran `cargo build --release` for bearDog and biomeOS, then copied the binaries into `plasmidBin/primals/`. This created locally-built binaries that diverged from the VPS-authoritative depot. When `checksums.toml` was updated (correctly) to reflect the VPS depot, all 14 local checksums showed MISMATCH.

**Root cause**: No enforcement mechanism prevented local builds from being deployed. The post-primordial standard was understood but not enforced — there was nothing stopping `cp target/release/beardog primals/x86_64-unknown-linux-musl/beardog`.

**Resolution**: Stopped all NUCLEUS primals. Fetched 13/13 from VPS (`membrane.primals.eco/depot/`). Verified BLAKE3 checksums. Restarted NUCLEUS. Standard now documented as mandatory in GLACIAL, ECOBIN, and FRAGO.

**Going forward**: 
- `plasmid.fetch` or `curl` from VPS is the ONLY way to update gate depot
- `sourdough validate depot` should fail if binary hash doesn't match VPS checksum
- cellMembrane could add a pre-commit hook: if checksums.toml changes, verify binaries match
- Consider a `plasmidBin/primals/.depot-source` marker file that records fetch origin + timestamp

### 1.2 ETXTBSY on plasmid.harvest (RESOLVED by cellMembrane)

**What happened**: `membrane plasmid.harvest beardog` and `biomeos` both exited code 1 after ~9.5 minutes. The binary being overwritten was mapped into a running process.

**Root cause**: Harvest attempted direct file write to a running executable. Linux returns `ETXTBSY`.

**Resolution**: cellMembrane already shipped atomic rename (`stage_to_depot` uses `.new` + `rename(2)`). The failure occurred on an older manual code path. Current pipeline is correct.

**Going forward**: 
- Delete or deprecate any code path that does direct binary writes (non-atomic)
- All harvest paths must use the `.new` + `rename(2)` pattern
- Consider `lifecycle.shutdown` JSON-RPC before harvest for clean binary replacement

### 1.3 plasmid.fetch --source vps Path Doubling

**What happened**: `membrane plasmid.fetch --source vps` downloaded to `primals/x86_64-unknown-linux-musl/primals/x86_64-unknown-linux-musl/` — a doubled-up nested path. All 13 fetches showed `download_failed`.

**Root cause**: The destination path computation in `plasmid.fetch` concatenates the arch subdirectory to an already-complete path. When the `--source vps` codepath was added, it didn't normalize the destination against the existing depot layout.

**Resolution**: Fell back to direct `curl` from WAN endpoint. Works correctly.

**Going forward**:
- cellMembrane: fix `plasmid.fetch --source vps` destination path normalization
- Add integration test: `plasmid.fetch --source vps --dry-run` should print correct paths
- Consider `plasmid.fetch --source wan` (the flag that was attempted first but rejected as unknown)

### 1.4 NUCLEUS Went Down After Cascade (Multiple Occurrences)

**What happened**: On at least 3 occasions during Wave 105, all NUCLEUS primals were found to be down after a cascade or extended operation. Each time, manual restart from depot was required.

**Root cause**: Multiple factors:
1. Binary replacement during depot operations can leave orphaned processes
2. No systemd/supervisor for NUCLEUS primals — they run as bare backgrounded processes
3. No health watchdog — if a primal dies, nothing restarts it
4. Shell session termination may kill backgrounded children

**Resolution**: Manual restart each time from depot binaries.

**Going forward**:
- **Critical need**: systemd user units or a minimal supervisor for NUCLEUS primals
- biomeOS `composition.deploy` should include a watchdog mode that restarts failed primals
- `nucleus-deploy` should register processes with systemd `--user` when available
- Consider a `nucleus.service` user unit template that biomeOS instantiates per-primal
- At minimum: `biomeOS lifecycle.watchdog` that polls `health.liveness` every 30s and restarts failures

---

## 2. PIPELINE / BUILD PROBLEMS

### 2.1 Cascade ff-only Conflicts (RESOLVED by cellMembrane)

**What happened**: Recurring merge conflicts on `checksums.toml` and `freshness.toml` during `membrane temporal.cascade`. Occurred on Waves 99, 102, 103. Required manual `git stash`, `git pull --rebase`, `git stash pop` sequences.

**Root cause**: Both files are locally-generated AND upstream-synced. Multiple gates writing within the same window breaks ff-only. `freshness.toml` is auto-published by cascade on every gate. `checksums.toml` is regenerated after every depot rebuild.

**Resolution**: cellMembrane shipped auto-discard for regenerable metadata before ff-only pull. 38/38 cascades now complete cleanly.

**Going forward**: 
- The pattern is correct — regenerable metadata should be treated as ephemeral
- If new auto-generated files are added to repos, they must be registered in the auto-discard list
- Monitor for new conflict patterns as more gates come online and push concurrently

### 2.2 aarch64 Sweep Destroyed x86_64 Checksums (RESOLVED by cellMembrane)

**What happened**: The aarch64 cross-compile sweep (commit `c46cc1c`) regenerated `checksums.toml` with only the `[aarch64-unknown-linux-musl]` section, silently deleting the `[x86_64-unknown-linux-musl]` section (14 entries).

**Root cause**: Single-writer assumption — the pipeline treated checksums.toml as a single-target file. When only one target existed, this was fine. With dual targets, the second sweep overwrote the first.

**Resolution**: cellMembrane shipped read-modify-write (commit `3a1900b`) with a validation gate that aborts if a pre-existing section would be lost, plus a regression test.

**Going forward**:
- As more targets are added (windows-msvc, wasm32-wasi), the TOML merge becomes more important
- Consider per-target checksum files instead of a single monolithic file: `checksums.x86_64.toml`, `checksums.aarch64.toml`
- Or: checksums embedded in the depot directory per-target: `primals/x86_64-unknown-linux-musl/.checksums.toml`

### 2.3 sourdough validate depot Segfault

**What happened**: `sourdough validate depot` crashed (segfault) when attempting to verify depot checksums.

**Root cause**: Unknown — likely a memory safety issue in the sourdough binary. Not investigated deeply due to the ad-hoc workaround being available (manual `b3sum` + `rg` verification).

**Resolution**: Fell back to manual verification. The crash is a known issue.

**Going forward**:
- sourdough team: investigate and fix the segfault. Running under `RUST_BACKTRACE=1` should help.
- Consider `sourdough validate depot --verbose` for debugging output
- This is LOW priority but erodes trust in the validation tooling

### 2.4 No Automated Cross-Arch CI for Depot Binaries

**What happened**: The aarch64 sweep was run manually. There is no CI/CD pipeline that builds for all targets and validates checksums before merge.

**Root cause**: GitHub Actions outage (Wave 51) stalled outer membrane CI evolution. Forgejo CI evaluation is still in progress.

**Going forward**:
- peptidoglycan should have a cron job or cascade-triggered build for all target triples
- `plasmid.refresh` on peptidoglycan should build for all registered targets, not just x86_64
- cellMembrane `plasmid.depot_sync` should verify all target sections exist after build

---

## 3. INTERACTION / NEURAL API GAPS

### 3.1 Songbird Federation Port Not Binding

**What happened**: Songbird was restarted with `SONGBIRD_FEDERATION_PORT=7700` and `--port 7700` but port 7700 never appeared in `ss -tlnp`. The env vars were set, the process was running, but the TCP listener never started.

**Root cause**: The `SONGBIRD_FEDERATION_PORT` env var and `--port` CLI flag are consumed during songbird initialization, but in UDS-only server mode, the federation listener requires `SONGBIRD_PRODUCTION_BIND_ADDRESS` to be set AND the internal federation module to be initialized. The env var may be getting swallowed by the shell backgrounding pattern (`cmd &>/dev/null &`).

**Resolution**: Used `mesh.init` via JSON-RPC over UDS to establish peering. This works because songbird connects outbound to peers even without a local listener. However, this means eastGate can only initiate connections, not accept them — other gates cannot mesh.init to eastGate.

**Going forward**:
- **This is a REAL problem**: without port 7700 listening, eastGate cannot accept incoming mesh connections
- ironGate was documented as BLOCKED specifically because eastGate:7700 refused connections
- songbird needs a `federation.enable` JSON-RPC method that opens the TCP listener at runtime
- Or: `mesh.init` should automatically start the listener when peers are added
- systemd user unit with proper env vars would fix the backgrounding issue
- For now: run songbird in foreground in a tmux/screen session with correct env vars

### 3.2 Mesh Initialization is Manual

**What happened**: Every time songbird restarts, mesh state is lost. The operator must manually call `mesh.init` with peer addresses. There is no persistent peer configuration.

**Root cause**: Mesh peer configuration is in-memory only. No peer persistence file, no auto-discovery, no mDNS/LAN broadcast.

**Resolution**: Manual `mesh.init` after every songbird restart.

**Going forward**:
- songbird should persist peers to `~/.local/share/songbird/peers.toml` or similar
- On startup, auto-load and attempt to connect to known peers
- `mesh.init` should append to persistent store, not just memory
- LAN auto-discovery via mDNS (`_songbird._tcp.local`) would eliminate manual peer seeding
- At minimum: a `songbird.peers` env var that pre-seeds peers on startup (like `SONGBIRD_PEERS` but from a file)

### 3.3 No Auto-Deploy on Cascade

**What happened**: When `membrane temporal.cascade` syncs new binaries (via checksums.toml updates), the running NUCLEUS is not automatically updated. Gates must manually fetch, stop, replace, restart.

**Root cause**: Cascade is source-level sync only — it pulls git repos. It does not trigger binary deployment or NUCLEUS restart. The deployment pipeline is decoupled from cascade.

**Going forward**:
- Post-cascade hook: if `checksums.toml` changed, trigger `plasmid.fetch` + selective NUCLEUS restart
- biomeOS `composition.deploy --watch` mode that monitors checksums and auto-updates
- cellMembrane `plasmid.auto-refresh` timer that checks VPS depot for newer binaries
- This is the key to autonomous gate self-healing — cascade for source, auto-fetch for binaries, auto-restart for primals

### 3.4 No Gate Self-Healing

**What happened**: When primals died (see 1.4), nothing detected or recovered the failure. Manual operator intervention was required every time.

**Root cause**: No supervision layer. No health monitoring. No restart policy.

**Going forward**: Same as 1.4 — systemd user units, biomeOS watchdog, or `nucleus-deploy --supervised`.

### 3.5 JSON-RPC Probing Cannot Distinguish Dead from tarpc

**What happened**: During liveness checks, tarpc sockets (compute-tarpc, coralreef-core-default-tarpc, toadstool) return empty responses to JSON-RPC probes, appearing as "dead" rather than "alive-but-different-protocol".

**Root cause**: tarpc uses a binary framing protocol incompatible with JSON-RPC text probing. There's no way to distinguish a tarpc socket from a dead socket using only `echo '{"jsonrpc":"2.0"...}' | socat`.

**Going forward**:
- `plasmidbin doctor` or `biomeOS health.sweep` should understand both protocols
- sourdough or biomeOS should maintain a socket type registry: `beardog.sock: jsonrpc`, `compute-tarpc.sock: tarpc`
- Health checks should use the correct probe for each protocol
- Consider a universal health endpoint: all sockets accept a `\x00PING` byte sequence regardless of protocol

---

## 4. TOPOLOGY GAPS

### 4.1 LAN Gates Offline — No Auto-Recovery

**What happened**: strandGate (192.168.1.132/173) and ironGate are both offline — no ping, no SSH. When they come back online, they have no way to auto-update from the VPS depot.

**Root cause**: Physical hardware (powered off, sleeping, or disconnected). No wake-on-LAN configuration. No scheduled uptime. No "come back online and self-update" mechanism.

**Resolution**: Wait for physical power-on. Then manual `plasmid.fetch` + `mesh.init`.

**Going forward**:
- **Gate enrollment playbook** for when a gate comes online:
  1. `curl https://membrane.primals.eco/depot/x86_64-unknown-linux-musl/<primal>` for each of 13 primals
  2. `chmod +x` all binaries
  3. Start songbird with `--port 7700`, run `mesh.init` to VPS + any known LAN peers
  4. Start remaining NUCLEUS from depot
  5. Verify `plasmidbin doctor` or manual liveness sweep
- This should be a single script: `membrane gate.bootstrap --source wan`
- strandGate SSH alias is `gate2` (192.168.1.132, user: strandgate)
- Need SSH aliases for ironGate and flockGate in `~/.ssh/config`

### 4.2 flockGate WAN Isolation

**What happened**: flockGate (192.168.60.20) is on a completely separate subnet. eastGate cannot reach it directly. It can only communicate via VPS relay.

**Current status**: flockGate WAN e2e validated 4/5 PASS (fetch + launch + mesh.init + health OK, BLOCKED on VPS songbird relay for mesh peering).

**Resolution**: VPS songbird relay at golgiBody:7700 is now LIVE and meshed with eastGate. flockGate should be able to `mesh.init` to the VPS and reach the collective.

**Going forward**:
- flockGate's mesh topology is: flockGate ↔ golgiBody(VPS) ↔ eastGate/LAN gates
- This is the correct topology for WAN — all WAN traffic routes through the outer membrane
- Test: flockGate `mesh.init` to `[RELAY_PUBLIC]:7700`, verify `discovery.peers` shows transitive discovery of eastGate
- flockGate should have its own `~/.ssh/config` entry and a dedicated enrollment script

### 4.3 grapheneGate UDS Path Adaptation

**What happened**: 7/13 primals failed to start on Pixel 8 (grapheneGate) because they bind to `/run/user/2000/biomeos/` or `/tmp/biomeos/` sockets, which are not writable under ADB shell user on Android.

**Root cause**: Hardcoded Unix socket paths assume a standard Linux desktop environment. Android's filesystem layout and permission model is different.

**Resolution**: 6 primals that use TCP or flexible socket paths work. 7 need adaptation.

**Going forward**:
- `BIOMEOS_SOCKET_DIR` env var override (default: platform-dependent)
- On Android: `/data/local/tmp/biomeos/`
- On Linux: `$XDG_RUNTIME_DIR/biomeos/` or `/run/user/$UID/biomeos/`
- `deploy_pixel.sh` sets this env var before launching each primal
- This is a primal-level change — each of the 7 primals needs to respect the env var
- Alternatively: biomeOS provides a `transport.discover_socket_dir()` helper that all primals use

### 4.4 Cross-Subnet Routing (southGate)

**What happened**: southGate is on 192.168.4.x while eastGate is on 192.168.1.x. Direct federation requires router configuration or TURN relay.

**Current status**: Previous testing showed 4ms latency via router — native routing works. But songbird mesh.init may not discover cross-subnet peers without explicit configuration.

**Going forward**:
- Explicit peer seeding for cross-subnet gates (include in peer persistence file)
- TURN relay through VPS as fallback (already available via songbird TURN on golgiBody)
- Not a blocker — southGate routing works, just needs explicit peer configuration

### 4.5 VPS Depot Serving Architecture

**What happened**: The WAN depot at `membrane.primals.eco` serves from golgiBody ([RELAY_PUBLIC]), where binaries live at `/opt/membrane/<primal>`. The Caddy configuration on golgiBody-ext (137.184.197.151) does NOT have a `/depot/` route — the depot is served from the inner membrane, not the outer.

**Root cause**: The Caddy depot provisioning (`caddy.depot.provision`) was deployed on the inner membrane (golgiBody), not the outer membrane (golgiBody-ext). The DNS for `membrane.primals.eco` resolves to golgiBody.

**Going forward**:
- This is actually correct for the diderm model: inner membrane serves depot to known gates
- But for WAN gates (flockGate), the outer membrane should be the depot surface
- Consider: golgiBody-ext reverse-proxies `/depot/` to golgiBody, adding rate-limiting and TLS termination
- Or: `plasmid.depot_sync` copies binaries to golgiBody-ext, which serves them statically
- The current setup works but puts WAN traffic on the inner membrane

---

## 5. ECOSYSTEM-WIDE PATTERNS TO EVOLVE

### 5.1 Gate Bootstrap Should Be One Command

Currently deploying a gate requires 5+ manual steps. Target: `membrane gate.bootstrap <gate-name>` that:
1. Detects architecture (x86_64, aarch64, etc.)
2. Fetches all depot binaries from VPS
3. Verifies checksums
4. Configures songbird peers
5. Starts NUCLEUS with correct env vars
6. Runs health sweep
7. Reports status

### 5.2 Depot Should Be a Service, Not a Directory

Currently `plasmidBin/primals/` is just a directory of executables. It should evolve into a service with:
- Version tracking (which wave was each binary built in?)
- Rollback capability (keep previous binary as `.prev`)
- Fetch-on-demand (binary not present locally? fetch from VPS automatically)
- Health-gated deployment (don't swap binary if new one fails health check)

### 5.3 Mesh Should Be Persistent and Self-Healing

Current mesh state is ephemeral. After any restart, manual `mesh.init` is needed. Target state:
- Peers persisted to disk
- Auto-reconnect on startup
- Periodic peer health checks
- Automatic re-mesh when a gate comes back online
- mDNS/broadcast for LAN peer auto-discovery

### 5.4 The neuralAPI Gap

Many interactions that should be JSON-RPC calls are currently manual shell commands. Examples:
- Deploying binaries: should be `biomeOS composition.deploy --refresh`
- Checking health: should be `biomeOS health.sweep` returning structured JSON
- Mesh management: should be persistent config, not ephemeral `mesh.init`
- Gate enrollment: should be a single neuralAPI call from the enrolling gate
- Depot validation: should be `biomeOS depot.verify` that cross-checks with VPS

The gap is: we have 13 running primals with 490+ methods, but the deployment/operations layer still lives in bash scripts and manual `socat` probes.

---

## 6. CURRENT STATE SNAPSHOT (2026-06-09 23:10 UTC)

### Gates

| Gate | Status | NUCLEUS | Mesh | Depot Source |
|------|--------|---------|------|-------------|
| **eastGate** | OPERATIONAL | 23 JSON-RPC + 3 tarpc | LIVE (1 peer: golgiBody VPS) | VPS-fetched, 13/13 BLAKE3 |
| **golgiBody VPS** | OPERATIONAL | 13/13 RUNNING | LIVE (1 peer: eastGate) | Authority (peptidoglycan) |
| **grapheneGate** | PARTIAL | 2/13 (beardog, songbird) | Not initialized | aarch64-musl via ADB |
| **strandGate** | OFFLINE | Unknown | Previously 17h+ stable | Needs VPS re-fetch |
| **ironGate** | OFFLINE | 23 UDS (last known) | INITIALIZED, blocked on eastGate:7700 | Needs VPS re-fetch |
| **flockGate** | UNREACHABLE | 4/5 WAN e2e passed | INITIALIZED, needs VPS relay | WAN fetch from VPS |
| **peptidoglycan** | REACHABLE | Build authority | N/A (build layer) | Self (source builder) |
| **golgiBody-ext** | REACHABLE | sporePrint only | N/A (outer membrane) | N/A |

### Key Metrics

| Metric | Value |
|--------|-------|
| P1 blockers | **0** |
| P2 remaining | 3 (grapheneGate UDS, ironGate mesh, flockGate WAN e2e) |
| Mesh nodes | 2 live (eastGate + golgiBody VPS) |
| WAN depot | 13/13 HTTP 200 serving |
| Transport | 11/11 non-exempt COMPLETE |
| Depot x86_64 | 14/14 BLAKE3 VERIFIED (VPS authority) |
| Depot aarch64 | 14/14 BUILT |
| Sovereignty | S1-S3 GRADUATED, S4 ending today |
| primalSpring | 887 tests, 0 failures |

---

## 7. RESHAPED PRIORITIES GOING FORWARD

### P1: Gate Self-Healing (blocks autonomous operation)
1. systemd user units or biomeOS watchdog for NUCLEUS primals
2. Persistent mesh peer storage in songbird
3. Post-cascade auto-fetch trigger

### P2: Cross-Topology Validation (blocks stadial)
1. ironGate mesh enrollment (needs eastGate federation port fix)
2. flockGate WAN e2e completion (VPS songbird relay is now LIVE)
3. grapheneGate 13/13 (UDS path adaptation for remaining 7)

### P2: Tooling (blocks automation)
1. `membrane gate.bootstrap` — one-command gate enrollment
2. Fix `plasmid.fetch --source vps` path doubling
3. Fix `sourdough validate depot` segfault
4. songbird `federation.enable` runtime method or persistent config

### LOW: Future Targets
1. Windows ecoBin (named pipes IPC)
2. wasm32-wasi ecoBin
3. NDK android target (bearDog StrongBox)
4. peptidoglycan multi-target CI pipeline
