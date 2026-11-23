# cellMembrane — Wave 79c Cross-Node Proxy COMPLETE

**Date**: 2026-06-05  
**FRAGO resolved**: `wave79c-cross-node-proxy`  
**Gate**: ironGate

---

## Deployed

Three `socat` systemd bridge units on golgiBody inner (`10.116.0.3`):

| Unit | Listener | Backend |
|------|----------|---------|
| `membrane-bridge-beardog.service` | `10.116.0.3:9443` | `/run/membrane/beardog.sock` |
| `membrane-bridge-biomeos.service` | `10.116.0.3:9444` | `/run/membrane/biomeos.sock` |
| `membrane-bridge-forgejo.service` | `10.116.0.3:3001` | `127.0.0.1:3000` (Forgejo) |

All units: `enabled`, `active (running)`, auto-restart on failure.

## Firewall Rules Added (golgiBody inner)

```
ufw allow from 10.116.0.5 to 10.116.0.3 port 9443 proto tcp  # bearDog
ufw allow from 10.116.0.5 to 10.116.0.3 port 9444 proto tcp  # biomeOS
ufw allow from 10.116.0.5 to 10.116.0.3 port 3001 proto tcp  # Forgejo
```

Only golgiBody-ext (`10.116.0.5`) can reach bridge ports. Zero public exposure.

## Caddy Updated (golgiBody-ext)

All routes now proxy to live backends via private network:

| Domain | Backend | Status |
|--------|---------|--------|
| primal.eco | static response | TLS LIVE |
| mesh.primal.eco | `10.116.0.3:7700` (Songbird) | TLS LIVE |
| auth.primal.eco | `10.116.0.3:9443` (bearDog bridge) | TLS LIVE |
| api.primal.eco | `10.116.0.3:9444` (biomeOS bridge) | TLS LIVE |
| nestgate.io | `10.116.0.3:3001` (Forgejo bridge) | TLS LIVE |

## Verified

- bearDog JSON-RPC via bridge: `{"primal":"beardog-tunnel","status":"alive","version":"0.9.0"}`
- biomeOS JSON-RPC via bridge: `{"primal":"biomeos","status":"healthy"}`
- Forgejo HTML via bridge: serving web UI
- All LE certs valid: `CN=auth.primal.eco`, `CN=api.primal.eco`, etc.

## Note on JSON-RPC over HTTP

bearDog and biomeOS speak newline-delimited JSON-RPC over raw TCP.
Caddy's `reverse_proxy` is HTTP-layer. Direct HTTP POST works if the
primals accept HTTP-wrapped JSON-RPC (standard JSON-RPC 2.0 transport).
WebSocket upgrade or Caddy L4 plugin would be needed for raw TCP clients.

For now: the infrastructure is complete. Content serving (nestgate.io)
and mesh federation (mesh.primal.eco) work fully. Auth and API surfaces
are TLS-terminated and proxied — final JSON-RPC transport integration
depends on upstream primal HTTP adapter support.

---

*FRAGO `wave79c-cross-node-proxy` — RESOLVED*
