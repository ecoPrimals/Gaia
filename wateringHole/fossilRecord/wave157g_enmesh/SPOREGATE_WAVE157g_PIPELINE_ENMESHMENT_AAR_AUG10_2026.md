# AAR: sporeGate Wave 157g — Pipeline Enmeshment

**Date**: Aug 10, 2026 | **Gate**: sporeGate | **Wave**: 157g ENMESH

---

## Summary

Executed pipeline enmeshment work from Wave 157g blurb. Three HIGH-priority items resolved, one diagnosed as gate-ops scope. Depot fully current (13/13).

---

## Completed

### 1. sourDough CI Wired into Golgi Post-Receive Hook

**Status**: SHIPPED — installed in 15 primal repos on golgi

The `golgi-post-receive-ci.sh` hook now runs 4 sourDough static validators before dispatching the sovereign CI trigger:

- `transport` — G66 transport injection compliance
- `ribocipher` — signal peptide compliance
- `platform-substrate` — G68 silicon deism audit
- `neural-api` — Neural API routing compliance

Validation is **advisory** (logged, does not block push). Hook checks out HEAD to a temp dir, runs validators, cleans up, then fires the CI trigger in background.

**Commit**: `2430a0b` (cellMembrane) — pushed to Forgejo.

**Install location**: `/opt/forgejo/data/repositories/ecoprimals/*.git/hooks/post-receive.d/30-sovereign-ci`

### 2. swarmVine Socket Discovery — FIXED

**Status**: RESOLVED — root cause identified and fixed

**Root Cause**: swarmVine's `platform_default()` created JSON-RPC sockets at `{XDG_RUNTIME_DIR}/biomeos/{name}.sock` (e.g., `/run/membrane/biomeos/swarmvine-e8b62b6e.sock`), while biomeOS's `SystemPaths.primal_socket()` resolves to `{runtime_dir}/{name}.sock` (e.g., `/run/membrane/swarmvine-e8b62b6e.sock`). The `/biomeos/` subdirectory mismatch caused biomeOS to never find swarmVine's JSON-RPC socket.

Additionally, socket files were being cleaned by tmpfiles.d between restarts — the kernel-side listeners were active but the filesystem entries were gone.

**Fix**: Added `Environment=BIOMEOS_RUNTIME_DIR=/run/membrane` to the `membrane-swarmvine.service` systemd unit. The upstream code (`fb0d6be`) already consolidated socket dir resolution via `platform_paths::runtime_socket_dir()` which respects `BIOMEOS_RUNTIME_DIR` as the highest-priority override.

**Result**: Both sockets now live in `/run/membrane/`:
- `swarmvine-e8b62b6e.sock` (JSON-RPC) — biomeOS can discover this
- `swarmvine-e8b62b6e.tarpc.sock` (tarpc binary RPC)

JSON-RPC probe returns `gossip.status` cleanly. Self-injection (`endpoint.alive`) working.

**Gate ops note for other gates**: Any gate running swarmVine needs `BIOMEOS_RUNTIME_DIR` set to match the socket directory biomeOS uses (typically `/run/membrane`).

### 3. toadStool Rebuild (S375/S376)

**Status**: DONE — depot 13/13 current

toadStool had commit drift (depot `b39445a9` vs source `7980b429`). S375 = biome.yaml manifest, S376 = WASM 38/48 + Tokio blast radius. Rebuilt, pushed to golgi.

### 4. TCP 7800 Cross-Gate Gossip Reachability — Diagnosed

**Status**: DIAGNOSED — gate-ops scope

| Gate | TCP 7800 | TCP 7700 | WG Ping | Assessment |
|------|----------|----------|---------|------------|
| sporeGate | LISTENING | LISTENING | — | Healthy |
| strandGate | OPEN | OPEN | OK | Healthy |
| eastGate | OPEN | OPEN | OK | Healthy |
| ironGate | CLOSED | CLOSED | OK | SSH key missing — needs service check |
| southGate | CLOSED | CLOSED | FAIL | Offline or WG tunnel down |
| blueGate | CLOSED | OPEN | N/A | Windows — swarmVine not deployed |
| westGate | CLOSED | CLOSED | N/A | No WG/LAN IP in MESH_REGISTRY |

**Gossip mesh is live between sporeGate ↔ strandGate ↔ eastGate** (3-gate mesh). Remaining gates need gate-ops intervention (service deployment, firewall, WG tunnel repair).

---

## Handoff Items for Other Gates

### ironGate
- Verify swarmVine is running: `systemctl status membrane-swarmvine`
- Ensure TCP 7800 is open (firewall)
- Add `BIOMEOS_RUNTIME_DIR=/run/membrane` to swarmVine systemd unit

### southGate
- WireGuard tunnel appears down from sporeGate perspective
- Verify WG peer handshake and endpoint

### blueGate
- swarmVine is not deployed (Windows). TCP 7700 works (songBird is running).
- swarmVine Windows port handoff already exists at `handoffs/SWARMVINE_WINDOWS_PORT_HANDOFF.md`

### westGate
- No WG or LAN IP in `MESH_REGISTRY` — needs manifest entry
- Verify swarmVine running and TCP 7800 open

### All Gates
- sourDough CI hook is now installed on golgi — primal pushes will run static validation
- Pull latest swarmVine binary from depot if upgrading

---

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| Depot staleness | 12/13 (toadStool stale) | 13/13 current |
| sourDough CI validators | 0 wired | 4 in 15 repos |
| swarmVine JSON-RPC socket | Missing (path mismatch) | Live at `/run/membrane/` |
| Gossip mesh reachable | Unknown | 3/6 gates (sporeGate, strandGate, eastGate) |
| Self-injection | Not running | 1 tower entry (`endpoint.alive`) |
