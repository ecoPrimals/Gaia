# AAR: Enrollment Endpoint Deployment — Wave 155a

**Date**: 2026-07-27 | **Gate**: sporeGate → golgiBody | **Wave**: 155a

## Summary

Deployed the `mesh.gate_enroll` enrollment endpoint on golgiBody, completing
Track B Phase 0. Gates anywhere in the world can now self-enroll by POSTing
a JSON-RPC request to `https://primals.eco/enroll`.

## What Shipped

### songBird Code Fixes (c4c5d2d)
1. **GateEnroll dispatch arm**: Wired `MeshMethod::GateEnroll` into the IPC
   dispatch match in `songbird-orchestrator`. Without this, the variant was
   defined but never routed, causing a compile error (`E0004`).

2. **Drawbridge body-method fallback**: When the path-derived JSON-RPC method
   is empty (e.g. `/enroll` with prefix `/enroll`), the drawbridge now extracts
   the method from the HTTP body's `"method"` field. Also preserves the caller's
   JSON-RPC `id` instead of hardcoding `1`.

### golgiBody Infrastructure
1. **Legacy service consolidation**: Disabled `songbird-gateway.service` (legacy)
   which competed for port 7780/7700 with `songbird-membrane.service`. The
   gateway was an older service unit without enrollment or dark forest support.

2. **Drawbridge enrollment drop-in**: Created systemd override at
   `/etc/systemd/system/songbird-membrane.service.d/enrollment.conf`:
   - `SONGBIRD_DRAWBRIDGE_ADDR=127.0.0.1:7780`
   - `SONGBIRD_DRAWBRIDGE_ROUTES=/enroll=mesh!public`
   - `SONGBIRD_PROXY_ROUTES=mesh=jsonrpc:///run/membrane/songbird.sock`
   - `GATE_ENROLLMENT_TOKEN` (generated, stored at `/etc/membrane/enrollment_token`)
   - `FORGEJO_API_TOKEN` (scoped: write:admin,write:user,write:organization)

3. **Caddy TLS proxy**: Added `/enroll` handler to `primals.eco` block:
   ```caddy
   handle /enroll* {
       reverse_proxy 127.0.0.1:7780
   }
   handle {
       redir https://sporeprint.primals.eco{uri} permanent
   }
   ```
   The `handle` grouping ensures `/enroll` is matched before the redirect.

## Verification Results

| Test | Method | Result |
|------|--------|--------|
| Local (golgiBody) | `curl http://127.0.0.1:7780/enroll` | `missing field gate_name` |
| WAN via Caddy | `curl https://primals.eco/enroll` | `missing field gate_name` |
| With token | `gate_name` + `enrollment_token` | `missing field wg_public_key` |
| Redirect (other paths) | `https://primals.eco/about` | 301 → sporePrint |
| All surfaces | sporeprint/footprint/live/webb/git | 200 |

## Issues Encountered

1. **Binary mismatch after deploy**: The `rsync` to golgiBody depot succeeded
   but the runtime copy (`/opt/membrane/songbird`) didn't match. Root cause:
   the "Text file busy" error on `scp` caused a silent failure. Fix: use
   rename-trick (`mv old; cp new; rm old`) consistently.

2. **Port conflict (orphan process)**: An old songbird process (from
   `songbird-gateway.service`) held port 7780 when `songbird-membrane` tried
   to start. systemd showed "active" but the drawbridge logs showed
   "Address in use". Fix: disabled the legacy service.

3. **Caddy handle ordering**: Initial `redir` was catching `/enroll` before
   `handle /enroll`. Fix: wrap redirect in `handle { }` so named handles
   take priority.

4. **Drawbridge path-to-method derivation**: The drawbridge derives JSON-RPC
   methods from HTTP paths (e.g. `/api/mesh/status` → `mesh.status`). With
   `/enroll` mapped to prefix `/enroll`, the derived method was empty.
   Fix: body-method fallback in `proxy_to_jsonrpc_backend`.

## What's Next (Phase 1)

The enrollment endpoint is live. Next: actual gate enrollment.

- 3 gates have WG keys (southGate, strandGate, westGate) — ready for `gate-enroll.sh`
- 2 gates pending keygen (blueGate, swiftGate)
- `CRITICAL`: Enrollment template still has `DNS=10.13.37.1` — must be removed

## Tokens (stored securely)

- Enrollment token: `/etc/membrane/enrollment_token` (chmod 600)
- Forgejo API token: systemd environment only (not on disk)
- Family seed: `/etc/membrane/family/family.key` (pre-existing)
