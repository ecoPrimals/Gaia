# Stale Socket Detection + Cleanup — Upstream Asks

**Date:** May 18, 2026
**From:** primalSpring (coordination spring)
**To:** biomeOS team, songbird team, plasmidBin team, all primal teams
**Source:** wetSpring production observation (southGate, 50+ stale sockets)
**License:** AGPL-3.0-or-later

---

## What Happened

wetSpring's sovereign pipeline discovered 50+ stale sockets in
`/run/user/1000/biomeos/` and 100+ stale songbird sockets in `/tmp/`.
No biomeOS or songbird process was running, but the socket files persisted
on disk from prior deployments. Discovery succeeded (file exists) but
connections failed (errno 111 — `ConnectionRefused`), causing ~100ms
wasted per failed probe.

## What primalSpring Fixed (Consumer Side)

All discovery paths now use **connect-probe liveness** instead of file-exists:

- `socket_is_alive(path)` — `UnixStream::connect()` with 50ms timeout before
  reporting a socket as discovered. Stale sockets fail instantly (ECONNREFUSED)
  vs the previous 5s read timeout on the full `PrimalClient::connect()` path.
- `DEAD_SOCKET_CACHE` — process-level negative cache. Once a socket is confirmed
  dead, it's never re-probed in the same session.
- Updated: `discover_primal()`, `discover_by_capability()`, `NeuralBridge::discover()`,
  socket registry scan, manifest discovery — all 6 discovery tiers.

**Standards updated:**
- `CAPABILITY_BASED_DISCOVERY_STANDARD.md` v1.3.0 (§5-6)
- `DEPLOYMENT_VALIDATION_STANDARD.md` (stale socket hygiene section)

Consumer-side probes are defense-in-depth. The authoritative fix is server-side
cleanup on startup.

---

## Upstream Asks

### 1. biomeOS: Socket Directory Cleanup on Startup (R9 — MEDIUM)

On startup, biomeOS should scan its socket directory and remove stale sockets:

```rust
// On biomeOS startup, before binding any new sockets:
for entry in std::fs::read_dir(socket_dir)? {
    let path = entry?.path();
    if path.extension().is_some_and(|e| e == "sock") {
        if UnixStream::connect(&path).is_err() {
            std::fs::remove_file(&path).ok();
        }
    }
}
```

biomeOS is the natural owner of `$XDG_RUNTIME_DIR/biomeos/` — it created
the directory and manages the socket namespace. Cleaning up on startup
prevents consumers from ever encountering stale sockets.

### 2. songbird: Socket Cleanup on Startup (R10 — LOW)

songbird creates sockets in `/tmp/` (and sometimes `$XDG_RUNTIME_DIR`).
The same startup cleanup pattern applies. wetSpring observed 100+ stale
songbird sockets.

### 3. All Primals: PID File Pattern (R11 — LOW)

Each primal SHOULD write `{name}.pid` alongside its socket. Consumers
can check `kill(pid, 0)` for instant liveness without connect overhead:

```rust
// On startup:
std::fs::write(pid_path, std::process::id().to_string())?;
// On shutdown:
std::fs::remove_file(pid_path).ok();
std::fs::remove_file(socket_path).ok();
```

This is enrichment — primalSpring's connect-probe works without PID files,
but PID files eliminate even the 50ms probe cost.

### 4. plasmidBin: `doctor.sh` Enhancement (R12 — LOW)

`doctor.sh` should check for stale sockets and report them:

```bash
for sock in /run/user/$(id -u)/biomeos/*.sock; do
    if ! fuser "$sock" >/dev/null 2>&1; then
        echo "STALE: $sock (no listener)"
    fi
done
```

### 5. All Primals: `unlink()` Before `bind()` (EXISTING STANDARD)

Already in `CAPABILITY_BASED_DISCOVERY_STANDARD.md` §4 — primals SHOULD
`unlink()` any pre-existing socket at their path before `bind()`. This is
standard Unix domain socket practice and prevents stale sockets from
accumulating after crashes. If your primal doesn't do this, add it.

---

## Impact Summary (Updated May 18 — Post-Absorption Sweep)

| Layer | Action | Priority | Status |
|-------|--------|----------|--------|
| primalSpring (consumer) | Connect-probe + dead cache | DONE | `socket_is_alive()`, `DEAD_SOCKET_CACHE` |
| biomeOS (server) | Startup cleanup of `biomeos/*.sock` | MEDIUM | **ABSORBED** — CHANGELOG confirms socket hygiene |
| songbird (server) | Startup cleanup of stale sockets | LOW | **ABSORBED** — CHANGELOG confirms socket hygiene |
| All primals | PID file alongside socket | LOW | **DEPRIORITIZED** — consumer-side connect-probe provides equivalent liveness |
| plasmidBin | `doctor.sh` stale socket check | LOW | **RESOLVED** — stale socket section added |
| plasmidBin | `stop_gate.sh` post-kill socket cleanup | — | **RESOLVED** — cleans `biomeos/`, `ecoprimals/`, `/tmp/biomeos/` after stopping |
| plasmidBin | `start_primal.sh` pre-start socket cleanup | — | **RESOLVED** — removes stale socket at `--socket` path before bind |
| All primals | `unlink()` before `bind()` | — | **13/14 CONFIRMED** — see absorption table below |
| **barraCuda** | `unlink()` before `bind()` at 2 sites | LOW | **RESOLVED** — `transport.rs` `remove_file` at both bind sites + legacy symlink cleanup |

### Absorption Table (May 18 sweep)

| Primal | Absorbed | Evidence |
|--------|:--------:|----------|
| bearDog | YES | fault tests + integration tests |
| biomeOS | YES | CHANGELOG + CURRENT_STATUS |
| coralReef | YES | ecosystem.rs + tarpc_transport |
| loamSpine | YES | CHANGELOG + uds.rs |
| nestgate | YES | socket_config.rs + isomorphic_ipc |
| petalTongue | YES | unix_socket_server + server |
| rhizoCrypt | YES | CHANGELOG + uds.rs + uds_tests |
| skunkBat | YES | ipc/mod.rs |
| songbird | YES | platform/unix.rs + android.rs |
| sourDough | YES | scaffold template generates clean |
| squirrel | YES | CHANGELOG + DEPLOYMENT_GUIDE |
| sweetGrass | YES | CHANGELOG + uds.rs + roundtrip tests |
| toadStool | YES | S264: 6/6 sites, CLI+Display fixed, 9,028 tests |
| **barraCuda** | **YES** | `transport.rs`: `remove_file` before bind at both sites + legacy symlink cleanup |

## Degradation Posture

All asks are enrichment. If unavailable:
- No biomeOS cleanup → primalSpring's connect-probe catches stale sockets (50ms cost)
- No PID files → connect-probe still works (50ms vs 0ms)
- No `doctor.sh` check → manual `fuser` inspection still possible

Science is never gated behind socket hygiene.
