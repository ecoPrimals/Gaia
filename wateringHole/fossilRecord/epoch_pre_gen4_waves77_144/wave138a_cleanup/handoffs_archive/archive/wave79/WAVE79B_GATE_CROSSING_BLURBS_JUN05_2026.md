# Wave 79b Gate-Crossing Blurbs — Teams with Pending Action

**Date**: 2026-06-05  
**From**: eastGate overwatch  
**Purpose**: Copy-paste context for each team with work blocking stadial gate entry  

---

## Primals with Pending Work

---

### toadStool (biomeGate)

**Status**: VPS binary rolled back — headless regression  
**Blocking**: Full VPS NUCLEUS refresh (10/13 currently deployed)

The fresh HEAD build of toadStool hard-fails on VPS startup:
```
Error: Setup("No Akida devices found. Check lspci output.")
```

The new binary unconditionally probes for Akida NPU hardware at startup.
VPS (and most deployment targets) have no NPU. The old binary ran an IPC
server fine without GPU/NPU.

**Action needed**: Add `--headless` or `--no-hardware` flag that skips the
Akida NPU probe and starts the IPC server in pure-compute mode. The
`server --socket /run/membrane/toadstool.sock` path must work without
hardware enumeration.

**Test**: `toadstool server --socket /tmp/test.sock --headless` starts
without error on a machine with no Akida/GPU.

---

### coralReef (strandGate)

**Status**: VPS binary rolled back — headless regression  
**Blocking**: Full VPS NUCLEUS refresh

The fresh HEAD build fails immediately:
```
Error: Cannot read ./specs/amd/amdgpu_isa_rdna2.xml
```

coralReef now requires GPU ISA spec files at startup, even for `server`
mode. VPS has no GPU specs on disk. The shader compiler should only need
specs when actually compiling shaders, not at process startup.

**Action needed**: Lazy-load GPU ISA specs on first compile request, or add
`--headless` flag that skips spec loading. The IPC server must start
cleanly without GPU spec files on disk.

**Test**: `coralreef server --socket /tmp/test.sock` starts without error
when `./specs/` directory doesn't exist.

---

### squirrel (eastGate)

**Status**: VPS binary rolled back — server mode regression  
**Blocking**: Full VPS NUCLEUS refresh

The fresh HEAD build no longer has a `server` subcommand:
```
error: unrecognized subcommand 'server'
```

Available commands are: `text-generation`, `code-generation`,
`multi-model-workflow`, `list-models`, `test-local`, `benchmark`.
The IPC `server` mode that provides JSON-RPC over UDS was removed or
was never in the latest code.

**Action needed**: Restore `server` subcommand (or add `ipc` subcommand)
that starts UDS JSON-RPC service mode. The squirrel primal must be
deployable as a long-running IPC server, not just a CLI tool.

**Test**: `squirrel server --socket /tmp/test.sock` starts UDS JSON-RPC
listener and responds to `health.check`.

---

### sweetGrass (strandGate)

**Status**: Refreshed to v0.7.50 on VPS — ALIVE via UDS  
**Issue**: `--http-address` defaults to `0.0.0.0:0` (all interfaces)

The VPS unit works around this with `--http-address 127.0.0.1:0`, but
the upstream default should be localhost-only per Tower Atomic posture.

**Action needed**: Change `--http-address` default from `0.0.0.0:0` to
`127.0.0.1:0`. External binding should be opt-in (`0.0.0.0:PORT`), not
default.

**Priority**: P1 (not blocking gate, workaround deployed)

---

### skunkBat (eastGate)

**Status**: Refreshed to v0.2.5 on VPS — ALIVE via TCP (localhost:9140)  
**Issue**: No UDS socket support in current binary

skunkBat is the only primal without a `/run/membrane/skunkbat.sock`. The
`server` subcommand has `--bind` and `--port` but no `--socket` flag.
The binary creates a UDS socket internally unless `--no-uds` is passed,
but it doesn't appear at the expected `/run/membrane/` path.

**Action needed**: Add `--socket <PATH>` flag to specify the UDS listener
path, matching the pattern used by bearDog, songBird, and others. When
`--socket` is provided, TCP should be optional (not default).

**Priority**: P1 (TCP localhost is safe, but breaks UDS-only audit)

---

### songBird (southGate)

**Status**: Refreshed on VPS — ALIVE via UDS + federation :7700  
**Issue**: 73% test coverage vs 90% stadial target

songBird has the largest quantitative coverage gap of any primal. All
functional code is solid (SB-TLS-01, BD-TRUST-01 mesh.init, deep debt
pass complete), but the 90% coverage gate requires a dedicated sprint.

**Action needed**: Coverage sprint targeting 90%. Focus on `songbird-tls`,
`songbird-stun`, and `songbird-discovery` crates which likely have the
lowest coverage.

**Priority**: P2 (does not block mesh.init, blocks stadial graduation)

---

## Downstream / Infrastructure

---

### cellMembrane (ironGate)

**Status**: VPS refresh handoff received  
**Blocking**: 3 headless binary fixes (toadstool, coralreef, squirrel above)

See `WAVE79_VPS_REFRESH_HANDOFF_JUN05_2026.md` for full details. Once
the 3 binaries are fixed and redeployed, `mesh.init` can proceed.

**Additional**: `build-primal.sh` has a bug where the release directory
appears empty after successful compilation. Manual builds work fine.
Root cause suspected: workspace `target/` directory interference when
using `--manifest-path`. Investigate and fix.

**Priority**: P0 for binary fixes, P1 for build script

---

### Caddy Reverse Proxy Wiring (ironGate / cellMembrane)

**Status**: Not started  
**Blocking**: Public content surface for inner membrane

All backend services are running. Caddy is active with sovereign TLS.
Four proxy routes need wiring:

| Route | Backend | Notes |
|-------|---------|-------|
| nestgate.io /content/* | Forgejo localhost:3000 | Content-addressed storage |
| mesh.primal.eco | Songbird :7700 | WebSocket upgrade for federation |
| auth.primal.eco | bearDog UDS | BTSP authentication surface |
| api.primal.eco | biomeOS UDS | Neural API (proxied via Caddy) |

**Action needed**: Update `/etc/membrane/Caddyfile` with reverse proxy
blocks. For UDS backends, use Caddy's `unix/` transport directive.

**Priority**: P1 (blocks content serving and API surface)

---

## Teams with NO pending work (cut from blurbs)

These teams are current and do not have gate-blocking action items:

- **bearDog** (southGate) — v0.9.0 refreshed, BD-TRUST-01 resolved, ALIVE via UDS
- **biomeOS** (southGate) — Refreshed, ALIVE via UDS, 90%+ coverage
- **nestGate** (ironGate) — Refreshed to v0.5.0, ALIVE via UDS
- **rhizoCrypt** (strandGate) — Refreshed to v0.14.2, ALIVE via UDS
- **loamSpine** (strandGate) — Refreshed, ALIVE via UDS
- **petalTongue** (ironGate) — Refreshed, ALIVE (health probe silent but socket active)
- **barraCuda** (strandGate) — Refreshed, ALIVE via UDS

---

## Gate Criteria Summary

To cross the stadial gate, we need:

1. **13/13 primals ALIVE on VPS via UDS** — currently 10/12 + skunkBat TCP (need 3 fixes + skunkBat UDS)
2. **mesh.init with gate peers** — songbird-mesh.service ready, needs all 13 confirmed first
3. **3-gate mesh proof** — eastGate ↔ strandGate proven, need golgiBody as 3rd node
4. **S4 Auth graduation** — 7-day gate ends ~Jun 9
5. **Zero externally-exposed primal TCP ports** — ACHIEVED (ufw verified)
6. **All upstream gaps closed** — ACHIEVED (4/4 resolved)

**Critical path**: Fix 3 headless binaries → redeploy → mesh.init → mesh proof → stadial

---

*"Three primals need the warmth of their home teams. Then the glacier crosses."*
