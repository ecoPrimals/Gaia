# cellMembrane — S3 Content Cutover VPS Readiness

**Date:** 2026-06-02 (Wave 71)
**Owner:** ironGate
**Partner:** flockGate (sporePrint build pipeline)
**Blocker:** DNS NS cutover (operator registrar action)

---

## Status: VPS READY — Cutover is a single DNS flip

All VPS-side infrastructure is configured and operational. The S3 content
cutover requires only the DNS A-record change from GitHub Pages IP to VPS IP.

---

## VPS-Side Verification Checklist

| Component | Status | Details |
|-----------|--------|---------|
| **Caddy TLS** | ACTIVE | `caddy-tls.service` running, ACME auto-renewal, ports 80+443 |
| **NestGate** | ACTIVE | `nestgate-membrane.service` on `:9500` + UDS |
| **Content routes (primals.eco)** | CONFIGURED | Caddyfile `primals.eco {}` block present |
| **sporePrint Zola root** | `/opt/ecoPrimals/sporePrint/public` | file_server with try_files |
| **pseudoSpore gallery** | `/opt/ecoPrimals/sporePrint/spores` | file_server browse (lab/spores/) |
| **www redirect** | CONFIGURED | `www.primals.eco → primals.eco` 301 |
| **TLS for primals.eco** | WILL AUTO-PROVISION | Caddy ACME on first request post-DNS flip |
| **TTFB (shadow test)** | 67ms sovereign vs 89ms GitHub Pages | Measured Wave 68 |
| **UFW** | 443/tcp ALLOW | Channel 3 Surface port open |
| **Let's Encrypt rate limit** | OK | No prior certs for primals.eco domain |

---

## Caddyfile Configuration (SSOT: `plasmidBin/membrane/Caddyfile`)

```
primals.eco {
    handle /lab/spores/* {
        root * /opt/ecoPrimals/sporePrint/spores
        file_server browse
    }
    handle {
        root * /opt/ecoPrimals/sporePrint/public
        file_server
        try_files {path} {path}/ /index.html
    }
}

www.primals.eco {
    redir https://primals.eco{uri} permanent
}
```

---

## Content Pipeline (flockGate sporePrint)

| Stage | Owner | Status |
|-------|-------|--------|
| Zola build | flockGate | sporePrint produces `/public` output |
| Deploy to VPS | cascade | `sporePrint` repo synced via `membrane temporal.cascade` |
| NestGate cache | automatic | `/var/cache/membrane/nestgate/` mirrors catalog |
| Caddy serves | automatic | Static file_server from cascade-synced path |

**Build pipeline note:** flockGate sporePrint currently targets GitHub Pages
deployment. Post-cutover, the pipeline simply pushes to the Forgejo repo and
cascade syncs it to VPS. No pipeline changes needed — cascade already delivers
the content to the correct VPS path.

---

## DNS Cutover Procedure (Single Flip)

1. Operator logs into Cloudflare DNS management for `primals.eco`
2. Update A record: `primals.eco` → VPS IP (remove Cloudflare proxy/orange cloud)
3. Update A record: `www.primals.eco` → VPS IP
4. Caddy auto-provisions Let's Encrypt cert on first HTTPS request
5. Verify: `curl -I https://primals.eco` returns 200 from VPS Caddy

**Rollback:** Re-point A records to GitHub Pages IPs (`185.199.108-111.153`)

---

## Verification Commands (post-cutover)

```bash
# From VPS — verify content exists
ls /opt/ecoPrimals/sporePrint/public/index.html

# From VPS — verify Caddy serves it locally
curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:80/

# From external — verify TLS + content
curl -I https://primals.eco

# membrane binary verification
membrane content.verify
```

---

## Pre-Cutover Testing (without DNS change)

To test the VPS is serving correctly without changing DNS:

```bash
# Direct IP request with Host header
curl -k --resolve primals.eco:443:$VPS_IP https://primals.eco/
```

Note: `-k` needed pre-cutover since Caddy won't have a valid cert for
`primals.eco` until DNS points to it (ACME challenge requires DNS).

---

## Dependencies

- **DNS NS cutover complete** — knot-dns must be authoritative before A-record
  changes propagate correctly through the zone
- **sporePrint repo present on VPS** — confirmed via cascade (`/opt/ecoPrimals/sporePrint/`)
- **No flockGate pipeline changes needed** — cascade handles delivery

---

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| ACME rate limit | primals.eco has no prior LE certs — 50/week limit not a concern |
| Stale content | cascade runs on push — content freshness matches source repo |
| Downtime during propagation | TTL-dependent; set low TTL (300s) before cutover |
| Rollback needed | A-record revert to GitHub Pages IPs takes < 5 min |
