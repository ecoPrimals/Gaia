# AAR: Deployment Pipeline Evolution — What's Working, What's Still Jelly

**Date**: 2026-07-27 | **Gate**: sporeGate | **Wave**: 155a–155b
**Scope**: Full session — enrollment endpoint, 3-target harvest, primalSpring calibration

---

## WHAT WORKED WELL

### 1. Enrollment Endpoint (Phase 0) — Pure Primal Deployment

The `mesh.gate_enroll` endpoint is **isomorphic Rust all the way down**:

```
Client → HTTPS (Caddy TLS) → songBird drawbridge (Rust TCP)
       → JSON-RPC IPC (Rust UDS) → mesh handler (Rust)
       → bearDog BTSP verification (Rust) → Forgejo API (automated)
```

No scripts. No Python. No shell glue. The enrollment code lives in songBird's
crate tree, dispatches via the standard IPC handler, and authenticates via
bearDog's crypto spine. This is the **gold standard** for how deployment should
work across the ecosystem.

### 2. Cross-Architecture Harvest

13 primals × 3 targets = 39 binaries, all from one machine (sporeGate), all
pushed to golgiBody's depot via rsync. Provenance tracked with blake3 checksums,
builder attribution, toolchain version.

### 3. primalSpring as Living Validation

197 scenarios, 1241 unit tests, catches regressions immediately. The gate
topology expansion (11 → 13 gates) broke 4 tests within minutes of cascade.
This is the system working as designed — data-driven topology changes surface
validation gaps instantly.

### 4. songBird Drawbridge Architecture

The capability-routed drawbridge is genuinely elegant:
- `SONGBIRD_DRAWBRIDGE_ROUTES` maps URL paths to capabilities
- `SONGBIRD_PROXY_ROUTES` maps capabilities to backends
- Auth is per-route (`!public` suffix)
- JSON-RPC IPC translation is automatic

This pattern replaces what would traditionally be nginx/Caddy route configs +
shell scripts + systemd socket activation. It's pure Rust, hot-configurable
via environment, and capability-aware.

---

## WHAT'S STILL AD-HOC / JELLY STRING

### J1. Harvest is Manual Shell Loops (CRITICAL)

**Current state**: The harvest is a `for primal in $PRIMALS; do cargo build; strip; cp; done`
loop run by an operator (or agent) in a shell. This is the single biggest
jelly-string in the deployment chain.

**What it should be**: `membrane plasmid.harvest --all --targets x86_64-musl,aarch64-musl,x86_64-windows-gnu`

A single cellMembrane command that:
- Reads `plasmidBin/manifest.toml` for the primal registry
- Builds each primal for each target
- Strips binaries (target-aware: `strip` vs `x86_64-w64-mingw32-strip`)
- Generates provenance.toml with blake3 checksums
- Copies to depot directory
- Optionally pushes to golgiBody

**Owner**: cellMembrane team. The data structures exist (`manifest.toml`, provenance format).
The shell loop is the reference implementation. It just needs to be codified in Rust.

**Fractal note**: blueGate as a distributed builder would use this same command.
The foreman pattern (sporeGate delegates to blueGate) requires this command to exist.

### J2. Depot Push is rsync (MEDIUM)

**Current state**: `rsync -avz depot/ golgi:/path/`

**What it should be**: `membrane plasmid.push --depot golgiBody`

The push should:
- Compare local provenance against remote (only push changed binaries)
- Verify checksums after transfer
- Atomically swap binaries on the remote (rename-trick, not overwrite)
- Update the remote provenance.toml
- Optionally restart affected services

**Owner**: cellMembrane team. The rsync works, but it's not idempotent,
doesn't verify integrity, and doesn't handle "Text file busy" on running binaries.

### J3. Service Restart is systemctl (MEDIUM)

**Current state**: `ssh golgi 'systemctl stop X; mv old; cp new; systemctl start X'`

**What it should be**: `membrane deploy.hot-swap --primal songbird --gate golgiBody`

Or better: the gate's own cascade timer detects a new binary in the depot,
verifies provenance, and hot-swaps automatically. The cascade-sense pipeline
for sporePrint content already does this (detect change → rebuild → atomic swap).
The same pattern should work for binaries.

**Owner**: cellMembrane team + songBird (for self-restart coordination).

### J4. Caddy Configuration is Manual sed/vim (LOW)

**Current state**: SSH into golgiBody, edit `/etc/membrane/Caddyfile`, validate,
reload. Required for adding the `/enroll` route.

**What it should be**: `membrane route.add --path /enroll --backend drawbridge --public`

songBird's drawbridge already handles capability routing. Caddy should be
auto-configured from the drawbridge route table, or replaced entirely by
songBird's native TLS termination (when bearDog's ACME implementation matures).

**Owner**: songBird team (native TLS), cellMembrane team (Caddy config generation).

### J5. WireGuard Peer Registration is wg set + wg-quick save (LOW)

**Current state**: `ssh golgi 'wg set wg0 peer <key> allowed-ips <ip>/32'`

**What it should be**: Handled by `mesh.gate_enroll` — the enrollment endpoint
already has the code path for this. It's just not live-tested yet. Once Phase 1
enrollment runs, this jelly string should be eliminated.

**Owner**: songBird mesh handler (already shipped, needs live validation).

### J6. systemd Drop-in Overrides are Manual (LOW)

**Current state**: `cat > /etc/systemd/system/X.service.d/enrollment.conf << EOF`

**What it should be**: `membrane gate.configure --set SONGBIRD_DRAWBRIDGE_ROUTES=/enroll=mesh!public`

Gate configuration should be declarative. The gate profile in `ecosystem_manifest.toml`
or a local `gate.toml` should specify environment variables, and `membrane gate.apply`
should generate the systemd overrides (or launchd plists, or Windows services).

**Owner**: cellMembrane team. This is part of the cross-platform service management
work (G1: `nucleus.rs` needs Windows Service + launchd paths).

### J7. Legacy Service Consolidation was Manual (LOW)

**Current state**: We discovered `songbird-gateway.service` competing with
`songbird-membrane.service` only because of a port conflict. Disabled it manually.

**What it should be**: `membrane gate.audit --services` should detect duplicate
service units, conflicting port bindings, and orphan processes. primalSpring
should have a scenario that validates service unit consistency.

**Owner**: cellMembrane team (audit), primalSpring team (scenario).

---

## EVOLUTION PRIORITY

| # | Jelly String | Impact | Effort | Priority |
|---|-------------|--------|--------|----------|
| J1 | Harvest is shell loops | Blocks distributed building (blueGate foreman) | Medium | **P0** |
| J2 | Depot push is rsync | No integrity verification, no atomic swap | Medium | **P1** |
| J3 | Service restart is manual | Blocks automated cascade-driven deployment | Medium | **P1** |
| J4 | Caddy config is manual | Blocks self-configuring routes | Low | **P2** |
| J5 | WG peer registration | Already coded, just needs live testing | Low | **P2** |
| J6 | systemd overrides manual | Blocks cross-platform service config | Low | **P2** |
| J7 | Legacy service detection | One-time issue, low recurrence | Low | **P3** |

### The Fractal Test

A deployment is **isomorphic** when:
1. The same command works on any gate (sporeGate, blueGate, golgiBody)
2. The same command works for any target (Linux, Windows, Android)
3. The command is a primal method (not a shell script)
4. The command is self-verifying (provenance, checksums, health checks)
5. The command is idempotent (running it twice is safe)

Today, only the enrollment endpoint passes all 5 criteria. The harvest,
push, and deploy chains fail criteria 1-3. That's the evolution frontier.

### The Convergence Path

```
Current (jelly string):
  operator → shell loop → cargo build → strip → cp → rsync → ssh systemctl

Phase 1 (cellMembrane commands):
  operator → membrane plasmid.harvest → membrane plasmid.push → membrane deploy.hot-swap

Phase 2 (automated cascade):
  cascade timer → detect drift → auto-harvest → auto-push → auto-swap → verify

Phase 3 (distributed foreman):
  sporeGate → delegate harvest to blueGate → both push to golgiBody → gates auto-update
```

Phase 1 is the cellMembrane team's immediate work. Phases 2-3 depend on Phase 1
but are mechanically straightforward once the commands exist.

---

## SESSION ARTIFACTS

| What | Where | Status |
|------|-------|--------|
| songBird GateEnroll dispatch | `c4c5d2d` | SHIPPED |
| songBird drawbridge body-method fallback | `c4c5d2d` | SHIPPED |
| rhizoCrypt Windows cfg(unix) fix | `d4972b0` | SHIPPED |
| primalSpring gate count calibration | `05e72e4` | SHIPPED |
| Enrollment endpoint on golgiBody | `primals.eco/enroll` | LIVE |
| 3-target depot (39 binaries) | golgiBody | SYNCED |
| Legacy songbird-gateway disabled | golgiBody | DONE |
| Drawbridge enrollment drop-in | golgiBody systemd | ACTIVE |
| Caddy /enroll route | golgiBody Caddyfile | ACTIVE |

---

*The ecosystem is at the inflection point where the primitives exist but the
orchestration is still manual. Every jelly string listed above has a clear
Rust-native replacement path. The work is not invention — it's codification
of patterns we've already proven in shell. That's the best kind of evolution:
the unknown is zero, the implementation is mechanical.*
