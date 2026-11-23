# NAPI-SYSTEMD + Bidirectional Mesh Deployment — AAR Wave 137b

**Date**: Jul 12, 2026 | **Wave**: 137b | **Gates**: sporeGate + golgi
**Status**: NAPI-SYSTEMD **DONE** | NAPI-CROSS-GATE **DONE** | GOLGI-WG-BIND **DONE**

---

## What Happened

Three HIGH items from Phase 1 resolved in a single session. Neural API promoted to systemd. songBird `f05918a` deployed to both sporeGate and golgi. Bidirectional mesh over WireGuard overlay is live.

## Actions Taken

### 1. NAPI-SYSTEMD — Neural API as Systemd Service

**Created**: `/etc/systemd/system/membrane-neural-api.service` on sporeGate.

Key configuration:
- `UMask=0000` — sockets created as `srwxrwxrwx`
- `ExecStartPre` symlinks all `/run/membrane/*.sock` into `/run/biomeos-root/` and `/run/biomeos-default/` (including family-scoped `*-e8b62b6e.sock` variants)
- `--btsp-optional` — bootstrap mode for initial activation
- `--graphs-dir` points to wateringHole graphs
- `After=membrane-beardog.service` — ensures crypto available before routing

**Coexists with**: `membrane-biomeos.service` (api mode, PID 859, running 5+ days). The Neural API (`neural-api` mode) and API server (`api` mode) are separate biomeOS processes.

**Verified**: `crypto.sign` routes through Neural API → bearDog, `lifecycle.status` returns, 48 primals discovered (includes family-scoped variants).

**Discovery**: The `FAMILY_ID=e8b62b6e` environment variable causes Neural API to look for sockets in `/run/biomeos-default/` with family-scoped names (`beardog-e8b62b6e.sock`). The ExecStartPre symlink loop bridges this.

### 2. NAPI-CROSS-GATE — songBird f05918a Deployment

**sporeGate**:
- Built songBird from `f05918a` (mesh port 8080→7700 fix + `?url=` compat)
- Stopped `songbird-gateway.service`, replaced binary, restarted
- Updated unit: `UMask=0000`, added `MEMBRANE_MESH_PEERS=10.13.37.1:7700`
- Mesh initialized via `mesh.init` RPC with `node_id=sporeGate`

**golgi**:
- Deployed `f05918a` binary via `scp` to `/opt/membrane/songbird`
- Relay service (`songbird-relay.service` on port 3478) briefly stopped for binary swap, restarted
- Updated `songbird-gateway.service`: `UMask=0000`, `--federation-port 7700`, `MEMBRANE_MESH_PEERS=10.13.37.2:7700`
- Enabled and started gateway service (was previously disabled and dead)
- Mesh initialized via `mesh.init` RPC with `node_id=golgiBody`

### 3. GOLGI-WG-BIND — Port 7700 Now Reachable

**Root cause**: golgi's `songbird-gateway.service` was disabled and dead. No songBird was listening on port 7700.

**Fix**: Enabled the service. It binds to `0.0.0.0:7700` (all interfaces), which includes the WireGuard interface `10.13.37.1`.

**Ports on golgi**:
- `:7700` — songBird federation (mesh hub, all interfaces)
- `:8091` — songBird drawbridge/HTTP proxy (all interfaces)
- `:7780` — songBird drawbridge (localhost only)
- `:3478` — songBird TURN relay (all interfaces, separate service)

## Mesh Topology (Post-Deploy)

```
sporeGate (10.13.37.2:7700) ↔ golgi (10.13.37.1:7700)
  ├── WireGuard overlay, ~30ms latency
  ├── songBird mesh: 1 peer each, direct path, reachable
  └── Bidirectional discovery active
```

Both nodes see each other as `online` with `path_type: direct`.

## Socket Directory Architecture

Three socket directories on sporeGate, bridged by symlinks:

| Directory | Purpose | Populated by |
|-----------|---------|--------------|
| `/run/membrane/` | Primary socket dir | Primal processes |
| `/run/biomeos-root/` | Neural API legacy lookup | ExecStartPre symlinks |
| `/run/biomeos-default/` | Family-scoped lookup (FAMILY_ID) | ExecStartPre symlinks |

**Long-term**: Unify to `/run/membrane/` only (SOCKET-DIR-UNIFY).

## Remaining Phase 1

| ID | Action | Status |
|----|--------|--------|
| ~~NAPI-SYSTEMD~~ | Neural API systemd service | **DONE** |
| ~~NAPI-CROSS-GATE~~ | songBird f05918a deployed | **DONE** |
| ~~GOLGI-WG-BIND~~ | golgi port 7700 live | **DONE** |
| NAPI-LIFECYCLE | LifecycleManager registration (count=0) | biomeOS — pending |
| SOCKET-DIR-UNIFY | Unify socket directories | biomeOS — MEDIUM |

**Phase 1 is now 10/12 items complete.** Only lifecycle registration and socket directory unification remain.

---

*Wave 137b: Neural API promoted to systemd. songBird f05918a deployed to sporeGate + golgi. Bidirectional mesh live over WireGuard overlay. golgi port 7700 bound on all interfaces. Phase 1 at 10/12.*
