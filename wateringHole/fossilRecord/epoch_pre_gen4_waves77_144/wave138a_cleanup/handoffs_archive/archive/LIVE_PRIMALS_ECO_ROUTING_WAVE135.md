# live.primals.eco — Routing Setup (Wave 135)

**Date**: Jul 9, 2026
**From**: eastGate overwatch
**To**: sporeGate / golgiBody operations team

## Objective

Route `live.primals.eco` through golgi (thin-relay) to sporeGate's petalTongue
NUCLEUS dashboard, which now includes the coordination backend sections.

## Architecture

```
live.primals.eco → Cloudflare DNS → golgi ([RELAY_PUBLIC])
  → Caddy :8443 → WireGuard → sporeGate 10.13.37.2:9900
    → petalTongue web (coordination dashboard + NUCLEUS topology)
```

## DNS (Cloudflare — operator action)

Add a new A record:

| Type | Name | Content | Proxy | TTL |
|------|------|---------|-------|-----|
| A | live.primals.eco | [RELAY_PUBLIC] | DNS only | 300 |

## Caddy (golgi — already in provision script)

The `live.primals.eco` block has been added to `provision-golgi.sh`:

```
live.primals.eco {
    reverse_proxy 10.13.37.2:9900 {
        header_up Host {host}
        header_up X-Forwarded-Proto {scheme}
    }
}
```

After adding the DNS record, reload Caddy on golgi:

```bash
systemctl reload caddy-tls
```

Caddy will automatically obtain a Let's Encrypt cert for `live.primals.eco`
via the :8443 HTTPS listener.

## petalTongue (sporeGate — already built)

petalTongue on sporeGate serves on port 9900 (default `PETALTONGUE_PORT`).
The dashboard now includes coordination sections that read from nestGate's
CAS on the shared filesystem.

Ensure petalTongue is running in web mode:
```bash
petaltongue web --bind 0.0.0.0:9900
```

## nestGate Coordination Backend (sporeGate)

nestGate now has a `coord.*` JSON-RPC domain and `/coord/*` HTTP routes.
To populate the coordination backend:

```bash
# Via JSON-RPC (encode blurb content as base64):
echo '{"jsonrpc":"2.0","method":"coord.ingest","params":{"filename":"ECOSYSTEM_BLURB.md","content_base64":"..."},"id":1}' | \
  socat - UNIX-CONNECT:/run/user/1000/nestgate-default.sock
```

Or from cellMembrane cascade:
```bash
membrane coord.ingest --source wateringHole/handoffs/
```

## Validation

After DNS propagation:
1. `curl -sI https://live.primals.eco/health` — should return 200
2. `curl -s https://live.primals.eco/api/status` — petalTongue version
3. `curl -s https://live.primals.eco/api/coord/blurbs` — coordination data
4. Browser: open `https://live.primals.eco` — full dashboard with coordination sections

## Dependencies

- DNS cutover for `primals.eco` already complete (Wave 134h)
- bearDog cert consolidation (Wave 135 Goal 3) will eventually move this to :443
- Until then, Caddy handles the cert on :8443
