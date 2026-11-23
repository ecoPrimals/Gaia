# LIVE-ACTIVATE AAR — Wave 137b

**Date**: Jul 13, 2026 | **Wave**: 137b | **Author**: sporeGate overwatch

---

## Summary

Activated petalTongue in **NUCLEUS dual-port mode** (HTTP + UDS IPC) on sporeGate, preparing the `live.primals.eco` public surface for the TOPO-VIS live topology visualization.

## What Was Done

### 1. DEPOT-REFRESH — songBird 74cf7101

- Built songBird `74cf7101` (FP-API: HTTPS outbound proxy for external GIS) for `x86_64-unknown-linux-musl`.
- Updated depot binary (was Jul 9, now Jul 13), regenerated checksums, re-signed, synced to golgi.
- **SONGBIRD-EASTGATE unblocked** — eastGate can now `plasmid.fetch --source wan` the fixed binary.

### 2. SIGN-VERIFY-ON-FETCH — Already Implemented

Code review confirmed the full verification chain is already in `cellMembrane`:

```
plasmid.fetch (WAN) → Phase 1: fetch signatures.toml → Phase 2: verify_depot_with_policy() → Phase 3: download binaries
```

- `DepotTrustPolicy` enum: `IntegrityOnly` | `VerifyIfPresent` (default) | `RequireSigned`
- `verify_depot_with_policy()` in `plasmid/signing.rs` (L111-151): verifies Ed25519 sig against checksums BLAKE3 hash.
- Default `VerifyIfPresent` verifies signatures when present (which they are since SIGN-01 is active).
- **Remaining cellMembrane decision**: promote default to `RequireSigned` or set `DEPOT_TRUST_POLICY=require-signed` in gate service units. This is a cellMembrane team call.

### 3. LIVE-ACTIVATE — petalTongue NUCLEUS on sporeGate

#### Binary

- Built petalTongue `d79f096` (TOPO-VIS Phase 2: routing weights, SSE live push, edge viz).
- Deployed to depot + plasmidBin, re-signed, synced to golgi.

#### Systemd Service — NUCLEUS Dual-Port

Previous: `server --socket /run/membrane/petaltongue.sock` (IPC only)
Current: `web --port 9900 --ipc --spa --allowed-origins "https://live.primals.eco,https://primals.eco"`

- **HTTP**: `0.0.0.0:9900` — serves TOPO-VIS dashboard + API endpoints
- **IPC**: UDS socket at `/run/user/0/biomeos/petaltongue-e8b62b6e.sock`
- **SPA mode**: index.html fallback for client-side routing
- **CORS**: restricted to `live.primals.eco` and `primals.eco`

Unit file: `/etc/systemd/system/membrane-petaltongue.service`

#### API Endpoints Verified

| Endpoint | Status | Data |
|----------|--------|------|
| `/` | 200 | 41KB TOPO-VIS dashboard HTML |
| `/api/status` | 200 | `{"mode":"web","pure_rust":true,"status":"ok","version":"1.6.6"}` |
| `/api/topology/live` | 200 | 7 mesh peers, edge data |
| `/api/topology-layers` | 200 | diderm architecture, 5 hardening controls |
| `/api/gate-mesh` | 200 | 6 enrolled gates |
| `/api/events` | SSE | Live push stream |

#### Caddy Config — golgi

Added `live.primals.eco` block to `/etc/membrane/Caddyfile`:

```caddyfile
live.primals.eco {
    import security_headers
    import csp_proxy
    import access_log

    reverse_proxy 10.13.37.2:9900 {
        header_up Host {host}
        header_up X-Real-IP {remote_host}
        header_up X-Forwarded-For {remote_host}
        header_up X-Forwarded-Proto {scheme}
    }
}
```

Caddy config validated. **NOT reloaded** — waiting for DNS.

#### WireGuard Reachability

Confirmed golgi can reach petalTongue over WireGuard:
```
root@golgi $ curl -s http://10.13.37.2:9900/api/status
{"mode":"web","pure_rust":true,"status":"ok","version":"1.6.6"}
```

### 4. Provision Script Updated

`provision-golgi.sh` updated with the `live.primals.eco` Caddy block (replaces the "reserved" comment).

## Pending — DNS Cutover

**Cloudflare DNS record needed** (user action):

| Type | Name | Content | Proxy |
|------|------|---------|-------|
| A | `live` | `[RELAY_PUBLIC]` | OFF (grey cloud — required for ACME HTTP-01) |

Once DNS propagates:
1. Reload Caddy on golgi: `systemctl reload caddy-tls.service`
2. Caddy will auto-obtain Let's Encrypt cert for `live.primals.eco`
3. `https://live.primals.eco` will serve the TOPO-VIS dashboard

## Architecture

```
User → live.primals.eco → Caddy (golgi, TLS) → WireGuard → petalTongue (sporeGate:9900)
                                                             ├── HTTP API (topology, mesh, SSE)
                                                             └── UDS IPC (Neural API integration)
```

## Depot State

- 32 binaries across 2 architectures (x86_64 + aarch64)
- Signed by sporeGate (Ed25519, `6cf29a81...`)
- Synced to golgi public depot

## Socket Directory Note

IPC socket created at `/run/user/0/biomeos/petaltongue-e8b62b6e.sock` (not `/run/membrane/`).
This is the SOCKET-DIR-UNIFY issue (biomeOS team, 2-4hr). Not a blocker.

---

*LIVE-ACTIVATE: sporeGate side complete. petalTongue NUCLEUS serving on :9900 with TOPO-VIS Phase 2. Caddy block prepared. Awaiting DNS A record for `live.primals.eco` → `[RELAY_PUBLIC]`.*
