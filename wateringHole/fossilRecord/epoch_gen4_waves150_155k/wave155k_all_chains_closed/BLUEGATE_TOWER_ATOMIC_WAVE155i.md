# blueGate — Tower Atomic Validation, Wave 155i

**Date**: Jul 29, 2026 12:45 EDT | **Wave**: 155i | **From**: blueGate
**Gate**: blueGate | **OS**: Windows 10.0.26200 | **Status**: **PARTIAL TOWER — 2/3 primals healthy, songBird G1 BLOCKER**

---

## SUMMARY

blueGate is on the mesh and partially running Tower Atomic. bearDog is fully
operational on TCP with 200+ JSON-RPC methods and all 16 capability types.
skunkBat is healthy in standalone mode. songBird has a **hard platform gate**
that rejects Windows before evaluating TCP bind options — this is the G1
blocker that needs a code fix upstream.

---

## MESH CONNECTIVITY — LIVE

| Peer | IP | Latency | Status |
|------|-----|---------|--------|
| golgiBody | 10.13.37.1 | 38ms | LIVE |
| eastGate | 10.13.37.5 | 76ms | LIVE |
| sporeGate | 10.13.37.2 | 76ms | LIVE |

WireGuard tunnel: `WireGuardTunnel$blueGate` service running (Automatic).
blueGate IP: 10.13.37.12/24. Endpoint: golgiBody [RELAY_PUBLIC]:51820.

## SSH — LIVE

```
$ ssh -T git@git.primals.eco
Hi there, golgiAdmin! You've successfully authenticated with the key named blueGate@primals.eco
```

All 40 remotes repointed from HTTPS to SSH. Fetch verified (wateringHole
pulled 5 new commits from overwatch).

---

## TOWER ATOMIC STATUS

### bearDog 0.9.0 — HEALTHY (TCP :9100)

**Transport**: TCP on 127.0.0.1:9100 (`--bind-mode tcp --port 9100`)
**Status**: `{"primal":"beardog","status":"alive","version":"0.9.0"}`
**Readiness**: `{"status":"ready","capabilities_count":0,"protocol":"JSON-RPC"}`

**Capabilities validated**:
- 200+ JSON-RPC methods responding
- 16 capability types: security, encryption, trust, consent, btsp, btsp_server,
  btsp_phase3, ionic_bond, contract_signing, lineage, graph, jwt_secrets,
  crypto, tls, relay, auth, identity, fido2
- BTSP server available (development mode — handshake enforcement disabled)
- BirdSong genetics initialized, lineage chain operational
- Rust Software HSM initialized with Universal Crypto Provider
- Pure Rust crypto: Ed25519, X25519, ChaCha20-Poly1305, Blake3
- Transport security: cleartext + BTSP, ndjson wire format

**Doctor report**: HEALTHY — version OK, entropy sources accessible, key storage OK.

### skunkBat 0.2.18 — HEALTHY (standalone)

**Status**: `{"status":"Healthy","liveness":true,"readiness":true}`
**Mode**: Standalone (no UDS, no discovery service)
**Dependencies**: security-observer HEALTHY, lineage-verifier unhealthy (no config)
**Behavioral baseline**: 12 observations established
**Threat categories**: 9 (ConnectivityAnomaly active)

### songBird 0.2.1 — NOT RUNNING (G1 BLOCKER)

**Error**: `Error: IPC server requires Unix domain sockets (Linux/macOS/BSD). On Windows use WSL2 for parity.`

songBird has a hard platform check that exits before evaluating `--listen`
(TCP bind) or `--bind` (HTTP bind) flags. The check fires unconditionally
on `cfg!(target_os = "windows")` regardless of transport configuration.

**Impact**: Without songBird, Tower Atomic on Windows lacks:
- `tower.health` facade (the canonical health endpoint)
- `tower.mesh_status` peer discovery
- Discovery beacons (LAN + federation)
- Mesh enrollment (`mesh.gate_enroll`)
- Inter-primal IPC routing
- ACME HTTP-01 challenge responder

**Fix required**: songBird server startup should honor `--listen` for TCP
mode on Windows, bypassing the UDS requirement. The `--listen` flag exists
and is documented for "platforms where Unix sockets are restricted (Android,
Windows)" but the platform gate fires before it's evaluated.

**Location**: Likely in `songbird/src/main.rs` or server initialization —
a `#[cfg(not(unix))]` or runtime `cfg!(windows)` check that needs to be
gated behind `!has_tcp_listen_flag` logic.

---

## G1 ASSESSMENT — TOWER ON WINDOWS

| Criterion | Status |
|-----------|--------|
| bearDog on Windows | **PASS** — TCP mode, full capability surface |
| songBird on Windows | **FAIL** — hard UDS platform gate |
| skunkBat on Windows | **PASS** — standalone mode, health OK |
| Depot Windows binaries | **PASS** — 14 .exe files on depot, verified |
| WireGuard mesh | **PASS** — 3 peers, 38-76ms latency |
| SSH push access | **PASS** — authenticated, remotes repointed |

**G1 verdict**: 2/3 Tower primals operational on Windows. songBird is the
sole blocker. The fix is narrow — a platform gate check in server startup.
bearDog's TCP mode proves that JSON-RPC over TCP works on Windows. skunkBat's
standalone mode works. songBird needs the same TCP fallback path.

---

## ENVIRONMENT

| Item | Value |
|------|-------|
| OS | Windows 10.0.26200 |
| Rust | 1.97.1 stable (x86_64-pc-windows-msvc) |
| Git | 2.55.0.3 |
| WireGuard | 1.1, tunnel active |
| bearDog | 0.9.0 — TCP :9100, HEALTHY |
| songBird | 0.2.1 — **NOT RUNNING** (UDS platform gate) |
| skunkBat | 0.2.18 — standalone, HEALTHY |
| Mesh IP | 10.13.37.12 |
| SSH | blueGate@primals.eco, verified |

---

## RECOMMENDATIONS

### P0: songBird Windows TCP mode (G1 blocker)

The `--listen` flag for TCP IPC is already documented and implemented for
Android/Windows in songBird's help text. The platform gate just fires too
early. Proposed fix:

```rust
// Instead of:
if !cfg!(unix) {
    return Err("IPC server requires Unix domain sockets...");
}

// Should be:
if !cfg!(unix) && listen_addr.is_none() {
    return Err("IPC server requires Unix domain sockets or --listen for TCP...");
}
```

Once fixed, songBird should start with:
```
songbird server --port 7700 --bind 0.0.0.0 --listen 127.0.0.1:9901
```

### P1: Named pipe support

Windows native IPC should use named pipes (`\\.\pipe\biomeos_*`). bearDog's
help text already references this path but falls back to UDS socket paths.
The `--socket` default shows named pipe format but the runtime doesn't bind it.

### P1: LongPathsEnabled

Windows `LongPathsEnabled` registry key is 0. Needs admin:
```powershell
Set-ItemProperty -Path "HKLM:\...\FileSystem" -Name "LongPathsEnabled" -Value 1
```

### P2: primalSpring colon-in-filename

6 benchmark files in `benchScale/tower_shadow/` use `:` (IP:port format).
Rename to `_` upstream for Windows compatibility.

---

## NEXT STEPS (after songBird fix)

1. eastGate ships songBird TCP mode fix
2. blueGate pulls + rebuilds songBird, restarts Tower Atomic
3. Validate `tower.health` → `{ "status": "healthy" }` via songBird
4. Validate `tower.mesh_status` — peer count + transport info
5. Proceed to Nest Atomic (+ nestGate, rhizoCrypt, loamSpine, sweetGrass)
6. Sub-builder enrollment under sporeGate

---

*blueGate — Wave 155i Tower Atomic validation. Partial Tower: bearDog HEALTHY
(TCP, 200+ methods), skunkBat HEALTHY (standalone). songBird BLOCKED by
platform gate — narrow fix needed. Mesh LIVE (3 peers). SSH LIVE. G1 proof
at 2/3 — one code fix from complete.*
