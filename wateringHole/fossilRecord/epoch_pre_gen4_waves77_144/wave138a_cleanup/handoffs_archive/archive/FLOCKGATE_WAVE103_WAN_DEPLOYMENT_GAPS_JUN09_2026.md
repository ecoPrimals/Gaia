# flockGate Wave 103 — WAN Mesh Deployment Validation Failure

**Date:** 2026-06-09
**Gate:** flockGate (WAN)
**Status:** BLOCKED — depot empty, prerequisites missing

## Validation Result: FAIL

flockGate cannot enroll in WAN mesh. Local depot is empty and
prerequisites for `plasmidBin fetch` and mesh enrollment are missing.

## Gap Assessment

### G1: Depot Empty (P1 — blocks mesh enrollment)

`infra/plasmidBin/primals/` contains zero binaries. Checksums exist
(checksums.toml has all 14 primals for x86_64-unknown-linux-musl) but
no actual binaries have been fetched.

**Required for mesh:** songbird, beardog (minimum core stack)
**Required for full NUCLEUS:** all 13 primals

### G2: Missing Prerequisites (P1 — blocks depot fetch)

| Tool | Status | Needed For |
|------|--------|-----------|
| `b3sum` | NOT INSTALLED | Checksum validation on fetch |
| `gh` | NOT INSTALLED | GitHub release download (private repos) |
| `socat` | NOT INSTALLED | UDS mesh enrollment commands |

### G3: No SSH Access to VPS (P2 — blocks direct pull)

No SSH key/config for golgiBody-ext (137.184.197.151). VPS is reachable
(34.8ms ping) but no authenticated access. The `peptidoglycan` relay
operates at the git layer (cascade sync), not binary distribution.

### G4: Network Topology Confirms WAN (informational)

```
flockGate: 192.168.60.20/24 (separate subnet)
eastGate:  192.168.1.144    (LAN — NOT REACHABLE from flockGate)
strandGate: 192.168.1.173   (LAN — NOT REACHABLE from flockGate)
VPS:       137.184.197.151  (WAN — REACHABLE, 34.8ms)
```

flockGate is genuinely WAN-isolated. Mesh enrollment would prove
cross-network transport. But first we need binaries.

## Required Actions (upstream)

1. **cellMembrane team**: Define the WAN binary distribution path.
   Options:
   a. GitHub Releases (`fetch.sh` — needs `gh` or public URLs)
   b. VPS HTTP endpoint (Caddy serving depot binaries)
   c. SSH/rsync from VPS peptidoglycan layer
   d. Cascade-carried binary distribution (build-carrying cascades, Wave 103 item 5)

2. **Operator (eastGate)**: Provision flockGate SSH access to VPS if
   option (c) is selected. Or confirm `fetch.sh` from GitHub Releases
   is the sanctioned WAN path.

3. **flockGate (self)**: Install `b3sum`, `gh`, `socat` once distribution
   path is confirmed. These are prerequisites regardless of binary source.

## What Works

- `membrane` CLI installed and operational (cascade sync, identity, impulses)
- `sporePrint` primal fully evolved (133 tests, transport-agnostic, zero C deps)
- VPS reachable (34.8ms) — WAN path confirmed
- Git cascade sync operational via peptidoglycan relay
- ECOPRIMALS_ROOT and workspace structure intact (all repos present)

## Coordination

- **Blocked on:** Binary distribution path decision (cellMembrane/eastGate)
- **Not blocked:** sporePrint evolution, cascade sync, content pipeline
- **Ready to execute:** Once binaries arrive, mesh enrollment is:
  ```bash
  SECURITY_PROVIDER_SOCKET=... songbird server --port 7700
  echo '{"jsonrpc":"2.0","method":"mesh.init","params":{...}}' | socat - UNIX-CONNECT:...
  ```
