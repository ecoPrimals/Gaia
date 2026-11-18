# Wave 94 FRAGO — cellMembrane / ironGate Deployment Validation

**Date**: 2026-06-07
**From**: cellMembrane (ironGate)
**To**: eastGate overwatch / primalSpring
**Subject**: Clean-room deployment validated on ironGate. Idempotent. Mesh blocked on beardog.

---

## Deployment Validation: PASS

ironGate clean-room redeploy from plasmidBin validated end-to-end:

### Checklist Results

| Check | Result |
|-------|--------|
| `membrane plasmid.status` → 13/13 current | **PASS** |
| All primals launch from depot binaries (no cargo build) | **PASS** |
| beardog socket present (`/run/user/1000/biomeos/beardog.sock`) | **PASS** |
| songbird socket present | **PASS** |
| `curl :7700/health` → OK | **PASS** |
| `health.liveness` on beardog → alive | **PASS** (v0.9.0) |
| LAN reachable (`curl 192.168.1.238:7700/health`) | **PASS** |
| Rollback + redeploy produces identical result | **PASS** |
| `capability.call` on beardog | **FAIL** (-32601 Method not found) |

### Deployment Commands (proven pattern)

```bash
# Rollback
pkill -f beardog; pkill -f songbird; sleep 1
rm -f /run/user/1000/biomeos/*.sock

# Deploy
DEPOT=/path/to/plasmidBin/primals
$DEPOT/beardog server --socket /run/user/1000/biomeos/beardog.sock &
sleep 2
SONGBIRD_SECURITY_PROVIDER=/run/user/1000/biomeos/beardog.sock \
  $DEPOT/songbird server --federation-port 7700 --bind 0.0.0.0 \
  --socket /run/user/1000/biomeos/songbird.sock &
```

### Key Finding: `--security-socket` vs `SONGBIRD_SECURITY_PROVIDER`

The `--security-socket` CLI flag is **NOT** recognized by songbird. The working
mechanism is the `SONGBIRD_SECURITY_PROVIDER` environment variable pointing to
the beardog socket path.

### Stale Socket Issue

beardog does NOT clean up its socket file on exit (`SIGKILL`). The rollback
procedure MUST include `rm -f /run/user/1000/biomeos/*.sock` before redeploy.
Without this, the new beardog instance fails to bind. Songbird has the same
behavior — it creates multiple sockets (btsp, crypto, ed25519, network, security,
x25519) that must be cleaned.

---

## Mesh Status: BLOCKED

`capability.call` returns `-32601 Method not found` on beardog v0.9.0.
This is the **sole blocker** for 3-gate mesh. Songbird peer TLS handshake
calls `capability.call` for cert provisioning — without it, `mesh.init`
succeeds but `discovery.peers` returns 0.

**Waiting on**: bearDog team to ship `capability.call` routing dispatcher.

---

## Depot Status

```
depot: 13/13 current, 0 drifted
built: 2026-06-07T19:36:09Z
target: x86_64-unknown-linux-musl
```

All binaries are static-pie linked, stripped. Symlinks resolve correctly.

---

## ironGate Running State

- beardog: LIVE on UDS + TCP 127.0.0.1:9100
- songbird: LIVE on UDS + federation 0.0.0.0:7700
- 8 sockets in `/run/user/1000/biomeos/`
- LAN: 192.168.1.238:7700 reachable
- Peers: 0 (mesh blocked, as expected)

---

*"Deployment validated. Pattern proven. Waiting on beardog capability.call for mesh."*
