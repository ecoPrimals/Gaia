# AAR: Deployment Failure Taxonomy — Wave 161

**Date**: Oct 5, 2026 | **Wave**: 161 | **Scope**: golgiBody + sporeGate + eastGate
**From**: overwatch/agentic session (sporeGate inner membrane)
**Type**: Failure Analysis — Pattern extraction for resilient design evolution

---

## Summary

13 distinct failures encountered across a single fossilization + stabilization +
redundancy audit session. Every failure leaked through existing defenses. This AAR
catalogs each failure, classifies it by taxonomy, extracts the pattern, and proposes
design abstractions to prevent recurrence or mitigate blast radius.

**Key insight**: Most failures share a common root — **state that outlives its
context**. Stale PIDs, stale routes, stale binaries, stale worktrees, unbounded
databases. The organism's biggest weakness isn't any single component — it's that
components assume their environment hasn't changed since they last checked.

---

## Failure Catalog

### F-01: Forgejo git gc OOM Kill

| Field | Value |
|-------|-------|
| **Host** | golgiBody (2GB RAM VPS) |
| **Trigger** | `git gc --aggressive --window=250` on beardog.git (647M) |
| **Blast radius** | Forgejo killed (3 auto-restarts), git operations unavailable ~2 min |
| **Category** | Resource exhaustion — unbounded memory on constrained host |
| **Root cause** | Aggressive GC window needs ~1.5× repo size in RAM. 647M × 1.2 = 780M. Forgejo + OS already using 1.2G. OOM killer chose git, then Forgejo. |

**Pattern**: **Unbounded operation on bounded host.** Any operation whose memory
scales with data size is dangerous on a fixed-resource VPS. The relay layer should
never run operations that scale with repository size.

**Abstraction**: Resource-aware command dispatch. Before running expensive git
operations, check available memory: `MemAvailable / repo_size > 2.0` or don't run.
Better: delegate GC to a LAN gate with surplus RAM via songbird capability routing.

```
DESIGN: git.gc should be a capability, not a local command.
  golgi requests → songbird dispatches → eastGate (128GB) runs GC → pushes result back.
  Relay never touches data-proportional operations.
```

---

### F-02: Webhook Deploy Pipeline Broken by Fossilization

| Field | Value |
|-------|-------|
| **Host** | golgiBody |
| **Trigger** | Deleted `/opt/ecoPrimals/detroit/worktree` during disk cleanup |
| **Blast radius** | Webhook deploy silently failed — "worktree missing, skipping git update" |
| **Category** | Dependency chain breakage — cleanup destroyed runtime dependency |
| **Root cause** | No manifest declaring which directories are runtime-required vs. cleanable |

**Pattern**: **Implicit dependency.** The webhook's dependency on the worktree
was encoded in bash logic, not in a declarable manifest. Cleanup couldn't
distinguish "safe to remove" from "breaks the pipeline."

**Abstraction**: Explicit runtime dependency manifest per host.
```toml
# /opt/ecoPrimals/.runtime-manifest.toml
[detroit]
required_paths = [
    "/opt/ecoPrimals/detroit/public",      # served by Caddy
    "/opt/ecoPrimals/detroit/worktree",    # git pull target for webhook
]
cleanable_paths = [
    "/opt/ecoPrimals/detroit/worktree/.git/objects/pack/*.old",
]
```
Any cleanup script checks the manifest before deleting. Missing required path
triggers an alert, not silent continuation.

---

### F-03: 12GB state.vscdb — Unbounded IDE State Growth

| Field | Value |
|-------|-------|
| **Host** | sporeGate |
| **Trigger** | Cursor accumulates chat/agent/checkpoint state without limits |
| **Blast radius** | IDE crashes, 12GB disk consumed, RAM pressure on 27GB machine |
| **Category** | Unbounded accumulation — no TTL, no size limit, no rotation |
| **Root cause** | `cursorDiskKV` table has no pruning policy. 806K rows across 3 months. |

**Pattern**: **Accumulator without drain.** Any system that appends without
pruning will eventually fill its container. This is thermodynamic — entropy
increases in closed systems. Every accumulator needs a drain.

**Abstraction**: Every persistent store must declare its retention policy:
```
agentKv:       keep last 200 sessions, TTL 30 days
bubbleId:      keep last 200, TTL 30 days  
checkpointId:  keep last 50, TTL 7 days
```
Implemented in `vacuum-cursor-state.sh` — but this is reactive maintenance.
The real fix is upstream (Cursor should rotate its own state).

**Cross-reference**: This same pattern appears in Caddy logs (83M), Forgejo logs
(101M), journal (990M), btmp (33M). Every one was an accumulator without a drain.

---

### F-04: Songbird riboCipher Protocol Mismatch

| Field | Value |
|-------|-------|
| **Host** | sporeGate → golgiBody |
| **Trigger** | sporeGate songbird (Aug 12) sending legacy riboCipher to golgi songbird (Aug 14) |
| **Blast radius** | Federation broken — golgi returns `invalid HTTP method parsed` |
| **Category** | Version skew — binary mismatch across mesh nodes |
| **Root cause** | No automated binary sync between depot and deployed nodes. Manual deployment drifts. |

**Pattern**: **Version skew across distributed nodes.** When N nodes run the same
binary but update independently, the mesh is only as strong as its oldest node.
Protocol-breaking changes without negotiation create silent partitions.

**Abstraction**: Two-phase:
1. **Version announcement**: songbird federation handshake should include protocol
   version. Mismatched nodes log the skew and fall back to common protocol.
2. **Depot freshness sensor**: each gate's membrane periodically checks depot hash
   against its deployed binary. Skew > threshold triggers a cascade impulse:
   `BINARY_STALE { gate: "sporeGate", binary: "songbird", local: "abc123", depot: "def456" }`

```
DESIGN: songbird.federation.handshake should include:
  { protocol_version: 3, binary_hash: "e7e37e0...", node_id: "sporeGate" }
  If peer protocol_version != local, negotiate common subset or reject with clear error.
```

---

### F-05: Stale PID Lock — eastGate Songbird

| Field | Value |
|-------|-------|
| **Host** | eastGate |
| **Trigger** | Songbird PID file contains PID 1299 (now reassigned to beardog after reboot) |
| **Blast radius** | songbird-federation.service crash-looping (49,500+ restarts) |
| **Category** | Stale state — PID file survives reboot, PID recycled to different process |
| **Root cause** | PID file at `~/.local/share/songbird/songbird.pid` AND `~/.songbird/songbird.pid` not cleaned on shutdown. After reboot, PID 1299 is beardog. Songbird checks `/proc/1299/` — exists! — and refuses to start. |

**Pattern**: **Identity confusion from state reuse.** PID files assume PIDs are
stable identifiers. They're not — they're recycled. After a reboot, any PID can
map to any process. Checking "is PID alive?" without checking "is PID *this binary*?"
is a class of bugs.

**Abstraction**: PID lock should verify process identity, not just existence:
```rust
fn is_stale_pid(pid_file: &Path) -> bool {
    let pid = read_pid(pid_file);
    if !process_exists(pid) { return true; }
    // KEY: check process name matches
    let cmdline = read_to_string(format!("/proc/{}/cmdline", pid));
    !cmdline.contains("songbird")
}
```
Additionally: PID files in `$XDG_RUNTIME_DIR` (tmpfs) are automatically cleaned
on reboot. Using `~/.local/share/` for PID files is the root error — that path
persists across reboots.

**Cross-reference**: This is the same class as F-02 (state outliving its context).
The PID file was written in one boot epoch and read in another.

---

### F-06: Caddy Routes to Dead WG Peer (.7 = 502)

| Field | Value |
|-------|-------|
| **Host** | golgiBody Caddy → 10.13.37.7 (ironGate/flockGate) |
| **Trigger** | WG peer .7 offline 49 days. Caddy still routing to it. |
| **Blast radius** | footprint.primals.eco → 502, webb.primals.eco → 502 |
| **Category** | Static routing to dynamic backend — no health check |
| **Root cause** | Caddy reverse_proxy has no health checking. Routes are static in Caddyfile. If backend dies, Caddy returns 502 forever until human edits config. |

**Pattern**: **Static config pointing at dynamic infrastructure.** The Caddyfile
is a point-in-time snapshot of "where services live." The mesh is dynamic — nodes
come and go. Static routing to dynamic backends guarantees stale routes.

**Abstraction**: Two approaches:
1. **Passive health + fallback**: Caddy supports `lb_policy` with `health_uri` and
   `fail_duration`. Configure:
   ```caddyfile
   reverse_proxy 10.13.37.7:3002 10.13.37.2:8090 {
       lb_policy first
       health_uri /health
       health_interval 30s
       fail_duration 60s
   }
   ```
2. **Dynamic routing via songbird**: Instead of static IPs in Caddyfile, Caddy queries
   songbird for the current provider of capability `footprint.serve`. songbird knows
   which node is alive and advertising the capability.

**Fix applied this session**: Rerouted footprint → .2, webb → 503 maintenance.
This is a bandaid — the real fix is health-aware routing.

---

### F-07: Caddy Reload Namespace Failure (PrivateTmp)

| Field | Value |
|-------|-------|
| **Host** | golgiBody |
| **Trigger** | `systemctl reload caddy-tls` |
| **Blast radius** | Reload failed — Caddy kept running with OLD config |
| **Category** | systemd mount namespace conflict with reload mechanism |
| **Root cause** | `PrivateTmp=yes` in caddy-tls.service. On reload, systemd spawns a new caddy process in a new mount namespace to validate config. The new namespace can't mount /tmp (the old mount still exists). Error: `Failed to mount /tmp: No such file or directory`. |

**Pattern**: **Side-effect of security hardening.** PrivateTmp is a security
feature that isolates /tmp. But it conflicts with systemd's reload mechanism,
which needs to spawn a parallel process. Security measure creates operational
fragility.

**Abstraction**: Use binary reload instead of systemd reload:
```bash
# This always works — talks to running Caddy's admin API
caddy reload --config /etc/membrane/Caddyfile --adapter caddyfile
```
Document in protocol: `wateringHole/protocols/CADDY_DEPLOY_PROTOCOL.md`:
- NEVER use `systemctl reload caddy-tls`
- ALWAYS use `/opt/membrane/caddy reload --config ... --adapter caddyfile`

---

### F-08: Server Header Information Leak

| Field | Value |
|-------|-------|
| **Host** | golgiBody Caddy |
| **Trigger** | Default Caddy behavior exposes `Server: Caddy` header |
| **Blast radius** | Low — fingerprinting only. Scanners know it's Caddy. |
| **Category** | Information disclosure — default-insecure |
| **Root cause** | The `(security_headers)` snippet had HSTS, CSP, etc. but didn't strip Server. The detroit block had its own header block that also didn't strip it. |

**Pattern**: **Defaults leak.** Every HTTP server ships with identification headers
enabled. Security hardening must be additive (add new headers) AND subtractive
(remove existing ones). Missing the subtractive step is common.

**Abstraction**: The `(security_headers)` snippet should be the single authority
for all security headers. It should include `-Server` so every block that imports
it automatically strips identification. Fixed this session.

---

### F-09: Zombie Cursor Process (1.4GB RAM)

| Field | Value |
|-------|-------|
| **Host** | sporeGate |
| **Trigger** | Sep 26 Cursor zygote process survived IDE shutdown |
| **Blast radius** | 1.4GB RAM consumed for 9 days. RAM pressure on other services. |
| **Category** | Process leak — parent exited, child persisted |
| **Root cause** | Electron-based Cursor uses zygote processes. When the main IDE exits, zygotes should be cleaned up. Crash or signal-loss can orphan them. |

**Pattern**: **Process outliving its purpose.** The zygote's reason for existing
(serving the IDE) ended, but the process continued consuming resources. No watchdog
detected the orphan.

**Abstraction**: Periodic process audit — a lightweight cron or systemd timer:
```bash
# /etc/cron.daily/orphan-check
pgrep -f 'cursor.*zygote' | while read pid; do
    parent=$(cat /proc/$pid/stat | awk '{print $4}')
    if [ "$parent" = "1" ]; then  # orphaned to init
        age_days=$(( ($(date +%s) - $(stat -c %Y /proc/$pid)) / 86400 ))
        if [ $age_days -gt 1 ]; then
            logger "killing orphan cursor zygote $pid (age: ${age_days}d)"
            kill $pid
        fi
    fi
done
```

---

### F-10: Unbounded Journal Growth (990MB)

| Field | Value |
|-------|-------|
| **Host** | sporeGate |
| **Trigger** | Default journald has no size limit on Pop!_OS |
| **Blast radius** | 990MB disk consumed by journal. Not critical but cumulative. |
| **Category** | Unbounded accumulation (same class as F-03) |
| **Root cause** | No `/etc/systemd/journald.conf.d/` override. Default is unlimited. |

**Pattern**: Same as F-03 — **accumulator without drain.**

**Fix applied**: Created `/etc/systemd/journald.conf.d/size-limit.conf`:
`SystemMaxUse=200M`, `RuntimeMaxUse=100M`. Persists across reboots.

**Abstraction**: Every gate enrollment should include journald size limits as a
standard step. Add to `gate-enroll.sh`:
```bash
mkdir -p /etc/systemd/journald.conf.d/
cat > /etc/systemd/journald.conf.d/size-limit.conf << 'EOF'
[Journal]
SystemMaxUse=200M
RuntimeMaxUse=100M
EOF
systemctl restart systemd-journald
```

---

### F-11: Old Kernel Trap — Can't Remove Running Kernel

| Field | Value |
|-------|-------|
| **Host** | golgiBody |
| **Trigger** | 142 days uptime, running kernel -47, newer kernel -53 installed but never booted |
| **Blast radius** | ~150M disk unrecoverable without reboot |
| **Category** | Deferred maintenance — update installed but not activated |
| **Root cause** | No reboot policy. Uptime treated as virtue, not risk. |

**Pattern**: **Deferred activation.** The kernel was updated but the update requires
a reboot to take effect. Without a reboot policy, the gap between "installed" and
"running" grows indefinitely. This also means 142 days of kernel patches are installed
but not protecting the host.

**Abstraction**: Reboot-after-kernel-update policy. For a relay with < 1 second
downtime tolerance, this means:
- Schedule monthly maintenance window (e.g., 04:00 UTC first Sunday)
- `needrestart -k` check on login (is running kernel current?)
- Automated notification if kernel age > 30 days

---

### F-12: WG Mesh Peer Staleness (8 of 11 stale/never)

| Field | Value |
|-------|-------|
| **Host** | golgiBody WG hub |
| **Trigger** | House2 power-off, remote nodes offline |
| **Blast radius** | 73% of mesh unreachable. Services routing through dead peers → 502. |
| **Category** | Mesh decay — no liveness monitoring |
| **Root cause** | WG peers have keepalive but no alerting when handshake age exceeds threshold |

**Pattern**: **Silent degradation.** The mesh lost 8 of 11 peers over 44-68 days.
No alert fired. No dashboard showed it. Discovery happened only during manual audit.

**Abstraction**: Mesh liveness sensor (skunkBat or skunky-ingest):
```
SENSOR: wg.peer.staleness
  for each peer in wg show:
    if handshake_age > 24h AND peer.expected_online:
      emit observation { level: "warn", peer, age, last_handshake }
    if handshake_age > 7d:
      emit observation { level: "alert", peer, age }
```
The sensor already has the infrastructure (skunky-ingest is live on golgi).
It just needs WG-specific probes.

---

### F-13: Binary Version Drift Across Depot/Deployed

| Field | Value |
|-------|-------|
| **Host** | sporeGate vs golgiBody depot |
| **Trigger** | sporeGate membrane (Aug 17) vs golgi depot (Sep 26) — 40 days behind |
| **Blast radius** | Potential protocol mismatches, missing fixes, stale behavior |
| **Category** | Deployment drift — no automated sync |
| **Root cause** | Manual `scp` deployment. No cascade-pull for binaries. |

**Pattern**: **Manual deployment drifts.** When deployment is a human action,
it happens at human frequency (weeks to months). The gap between "built" and
"deployed" grows silently.

**Abstraction**: Binary freshness cascade. When foreman builds new binaries:
1. `plasmid.harvest` pushes to depot (exists)
2. Depot notifies subscribed gates: `BINARY_UPDATED { binary, hash, arch }`
3. Gate auto-fetches IF hash differs from deployed (pull model)
4. Gate restarts service IF binary changed (with rollback on health failure)

This is the `mesh.subscribe → plasmid.auto_fetch` pattern described in
`compositions.thin-relay` but not yet implemented.

---

## Failure Taxonomy — Pattern Classes

### Class A: State Outliving Context (F-02, F-03, F-05, F-09, F-10)

The largest class. State written in one epoch is read in another where its
assumptions no longer hold.

| Failure | State | Epoch boundary |
|---------|-------|---------------|
| F-02 | worktree path | cleanup vs runtime |
| F-03 | chat/agent history | month vs session |
| F-05 | PID file | boot epoch |
| F-09 | zygote process | IDE session |
| F-10 | journal entries | weeks vs days |

**Design principle**: **Every piece of state must declare its lifetime.**
- Boot-scoped → `$XDG_RUNTIME_DIR` (tmpfs, cleaned on reboot)
- Session-scoped → named temp dir with TTL
- Persistent → explicit retention policy + rotation

### Class B: Static Config ↔ Dynamic Infrastructure (F-04, F-06, F-12, F-13)

Configuration assumes the world is frozen. The world moves. Config rots.

| Failure | Static thing | Dynamic thing |
|---------|-------------|---------------|
| F-04 | Binary version | Protocol evolution |
| F-06 | Caddy route IP | WG peer liveness |
| F-12 | WG peer config | Physical power state |
| F-13 | Deployed binary hash | Depot binary hash |

**Design principle**: **Config that references dynamic state must include a
liveness check.** Every route should health-check. Every binary deployment
should version-check. Every mesh peer should handshake-age-check.

### Class C: Unbounded Operations on Bounded Resources (F-01, F-11)

Operations that scale with data size run on hosts that don't scale.

| Failure | Operation | Bound |
|---------|----------|-------|
| F-01 | git gc --aggressive | 2GB VPS RAM |
| F-11 | kernel accumulation | 10GB VPS disk |

**Design principle**: **Delegate data-proportional operations to capable hosts.**
The relay should process and route, never crunch. If an operation's memory/disk
requirement scales with data, dispatch it to a LAN gate.

### Class D: Security Hardening Side-Effects (F-07, F-08)

Security features interact poorly with operational patterns.

| Failure | Security feature | Operational conflict |
|---------|-----------------|---------------------|
| F-07 | PrivateTmp | systemd reload mount namespace |
| F-08 | Default headers | Information disclosure |

**Design principle**: **Security hardening must be tested against operational
workflows, not just attack vectors.** A security feature that breaks deployment
is a net negative.

---

## Proposed Resilience Abstractions

### 1. Runtime Manifest (prevents F-02 class)

Every host declares its runtime dependencies in a machine-readable file.
Cleanup scripts, fossilization, and agentic operations check the manifest
before modifying the filesystem.

### 2. State Lifetime Annotations (prevents F-03, F-05, F-09, F-10 class)

Every persistent state file declares its scope:
- `boot` → use tmpfs
- `session` → use session-scoped dir with cleanup hook
- `retained(N)` → rotate after N entries or T time

### 3. Freshness Sensors (prevents F-04, F-06, F-12, F-13 class)

skunkBat observations for:
- `binary.freshness` — deployed hash vs depot hash
- `wg.peer.staleness` — handshake age vs expected
- `caddy.route.health` — backend reachability
- `service.version.skew` — protocol version across mesh

### 4. Capability-Routed Operations (prevents F-01 class)

Operations that require more resources than the local host has should be
dispatched via songbird capability routing to a gate with sufficient capacity:
- `git.gc { repo, min_ram: "4G" }` → dispatched to eastGate (128GB)
- `zola.build { site, min_disk: "2G" }` → dispatched to ironGate

### 5. Health-Aware Routing (prevents F-06 class)

Caddy backends should health-check and failover:
- Primary: current route
- Fallback: songbird-discovered alternative
- Last resort: 503 with meaningful message

### 6. Deployment Cascade (prevents F-13 class)

When a binary is built:
1. Builder pushes to depot (exists)
2. Depot hashes propagate via songbird gossip
3. Gates with stale binaries auto-fetch
4. Gates restart with new binary
5. Health check → rollback if unhealthy

---

## Cross-Reference: Prior Failures (from fossil record)

| Prior AAR | Failure | Same Class |
|-----------|---------|-----------|
| IRONGATE_INCIDENT_DOUBLE_LAUNCH_IPC_LOCKUP | Double songbird launch → socket contention | A (state collision) |
| CORALREEF_WAVE157E_PROCESS_LEAK_FIX | coralReef process leak after test runs | A (process outliving purpose) |
| PIPELINE_DIVERGENCE_AAR | Binary drift across gates | B (version skew) |
| OUTER_MEMBRANE_TOPOLOGY_FAILURE_155b | NAT rate limit amplification | C (unbounded on bounded) |
| BIOMEGATE_RECOVERY_AAR | Power loss → stale service state | A (state outliving context) |
| SONGBIRD_WAVE157K_DEEP_DEBT_SWEEP | Transport protocol evolution debt | B (protocol drift) |

**The same four pattern classes explain failures across 6+ months of AARs.**

---

## Priority Implementation Order

1. **journald size limits in gate-enroll.sh** — 5 minutes, prevents F-10 everywhere (DONE for sporeGate)
2. **Caddy binary reload protocol** — 5 minutes, document and enforce (DONE)
3. **WG staleness sensor in skunky-ingest** — 1 hour, prevents F-12 class
4. **Binary freshness impulse in cascade** — 2 hours, prevents F-04/F-13 class
5. **Runtime manifest for golgiBody** — 30 minutes, prevents F-02 class
6. **Songbird PID file → XDG_RUNTIME_DIR** — code change, prevents F-05 class
7. **Caddy health-check routing** — 1 hour per route, prevents F-06 class
8. **capability.call dispatch for git GC** — larger evolution, prevents F-01 class

---

*Every failure is a fossil. Extract the pattern. Evolve the design. Build the
antibody. The organism remembers what killed it — that's how it stops dying.*

*Wave 161 — 13 failures cataloged, 4 pattern classes identified, 8 abstractions proposed.*
