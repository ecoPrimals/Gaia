# wetSpring → biomeOS: Stale Socket Detection + Auto-Cleanup

**Date:** May 18, 2026
**Author:** wetSpring workstream (southGate)
**Audience:** biomeOS team, plasmidBin team
**Status:** Deployment Issue — observed in production
**License:** AGPL-3.0-or-later

---

## Issue

`/run/user/1000/biomeos/` contains 50+ stale sockets from previous biomeOS
deployments that are no longer listening. No biomeOS process is running, but
the sockets still exist on disk:

```
/run/user/1000/biomeos/neural-api-neural-tier-run-user-9c2e.sock  — stale
/run/user/1000/biomeos/braid.sock                                  — stale
/run/user/1000/biomeos/commit.sock                                 — stale
/run/user/1000/biomeos/discovery.sock                              — stale
...
```

Consumer primals (wetSpring) discover these via `$XDG_RUNTIME_DIR/biomeos/`
but get `ConnectionRefused` (errno 111) when attempting to connect. The
degradation path works correctly (`Trio available: false`, falls back to
local IDs), but consumers cannot distinguish between "trio not deployed"
and "trio deployed but crashed" without attempting a connection that times out.

## Impact

- Socket discovery succeeds (file exists) but connection fails (no listener)
- Each `capability_call` attempt incurs a ~100ms connection timeout
- Per-clone pipeline with 3 trio calls × 7 clones = 21 failed connections = ~2s wasted
- No way to know if trio *should* be running or intentionally isn't

## Recommendations

### 1. Crash Cleanup in biomeOS

On startup, biomeOS should `fuser` or `lsof` its socket directory and remove
any sockets without a listening process. The `CAPABILITY_BASED_DISCOVERY_STANDARD`
already documents this:

```rust
// On biomeOS startup:
for socket in glob("$XDG_RUNTIME_DIR/biomeos/*.sock") {
    if !has_listener(&socket) {
        std::fs::remove_file(&socket).ok();
    }
}
```

### 2. PID File or Lock

Each primal should write a `{name}.pid` alongside its socket. Consumers can
check `kill(pid, 0)` before attempting a socket connection — instant answer
with no timeout cost.

### 3. plasmidBin `doctor.sh` Enhancement

`plasmidBin/doctor.sh` should check for stale sockets and report them:

```bash
for sock in /run/user/$(id -u)/biomeos/*.sock; do
    if ! fuser "$sock" >/dev/null 2>&1; then
        echo "STALE: $sock (no listener)"
    fi
done
```

### 4. Consumer-Side: Cache Socket Liveness

Once `Trio available: false` is determined, consumers should cache this for
the session rather than re-attempting on every `capability_call`. Our
`neural_api_socket()` currently re-probes on every call.

---

## Data Collected

```
$ fuser /run/user/1000/biomeos/neural-api-*.sock
(empty — no process listening)

$ python3 -c "socket.connect(...)"
ConnectionRefusedError: [Errno 111] Connection refused

$ ps aux | grep biomeos
(empty — no biomeOS process)
```

Family ID: `neural-tier-run-user-9c2e`
Socket count in biomeos/: 50+ files
Stale songbird sockets in /tmp/: 100+ files
