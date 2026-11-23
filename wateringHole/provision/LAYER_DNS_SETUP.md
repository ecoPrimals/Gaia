# Golgi Layer DNS Setup — Cloudflare Configuration

## Overview

Each golgi layer gets a subdomain on `primals.eco` via Cloudflare DNS.
The wildcard `*.primals.eco` already points to golgiBody, so layers
need explicit A records (explicit records take priority over wildcard).

## Per-Layer DNS Records

Add these in Cloudflare Dashboard → primals.eco → DNS → Records:

### Layer 2 (Hetzner DE)

| Type | Name | Content | Proxy | TTL |
|------|------|---------|-------|-----|
| A | `layer2` | `<HETZNER_IP>` | DNS only (grey cloud) | Auto |

This creates `layer2.primals.eco → <HETZNER_IP>` (direct, raw traffic).

### Layer 3 (Vultr SG)

| Type | Name | Content | Proxy | TTL |
|------|------|---------|-------|-----|
| A | `layer3` | `<VULTR_IP>` | DNS only (grey cloud) | Auto |

This creates `layer3.primals.eco → <VULTR_IP>` (direct, raw traffic).

### Layer 4 (OVH FR) — CF-Proxied for Fingerprint Learning

| Type | Name | Content | Proxy | TTL |
|------|------|---------|-------|-----|
| A | `layer4` | `<OVH_IP>` | **Proxied (orange cloud)** | Auto |

This creates `layer4.primals.eco → Cloudflare → <OVH_IP>`.
Cloudflare's WAF/bot detection sees all fleet traffic.

## Verification

After adding DNS records, verify propagation:

```bash
# Direct resolution (grey cloud)
dig +short layer2.primals.eco
# Should return: <HETZNER_IP>

# CF-proxied (orange cloud)
dig +short layer4.primals.eco
# Should return: Cloudflare IPs (104.x.x.x or 172.x.x.x)

# TLS check (Caddy auto-obtains cert)
curl -I https://layer2.primals.eco/
# Should return: HTTP/2 200, HSTS headers

# Plasmid endpoint
curl https://layer2.primals.eco/plasmid
# Should return: local conserved plasmid JSON
```

## Fleet Discovery

The fleet discovers new surfaces through:
1. **DNS enumeration** — if they enumerate *.primals.eco subdomains
2. **Cross-links** — existing surfaces link to new layers
3. **Certificate transparency logs** — Let's Encrypt certs are public
4. **Sitemap** — signal.primals.eco/sitemap.xml lists all surfaces

Fleet typically discovers new surfaces within 24-48 hours via CT logs.

## Cloudflare Orange Cloud Notes

When a layer is CF-proxied (orange cloud):
- Cloudflare's WAF/bot detection sees ALL raw requests
- CF may classify fleet as bot and challenge/block them
- If CF blocks: that itself is evidence ("even Cloudflare catches them")
- If CF passes: CF can learn the patterns from our published feed
- TLS cert is CF-issued (not Let's Encrypt) — this is fine
- Caddy should NOT try ACME for CF-proxied domains (use `:80` listener)
- CF adds `CF-Connecting-IP` header — use this instead of X-Real-IP

### CF-Proxied Caddyfile Adjustment

For CF-proxied layers, modify the Caddyfile:

```
${LAYER_DOMAIN} {
    # ... same config ...
    # But trust CF-Connecting-IP for real client IP
    @fleet_cf header CF-Connecting-IP *
    # skunky-ingest should read CF-Connecting-IP header
}
```
