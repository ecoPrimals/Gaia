# Sovereign Validator AAR — Wave 134j

**Date**: 2026-07-09
**Scope**: Post-DNS-cutover validation of primals.eco, subdomain routing fix, content updates

## What Broke

The bearDog ACME gateway cutover (134h) created three regressions:

### 1. Subdomain routing collapse (CRITICAL)

bearDog's TCP proxy on :443 has no Host-header routing. Every domain resolving to
golgi — `git.primals.eco`, `membrane.primals.eco`, `lab.primals.eco` — was proxied
to the sporePrint static site instead of their correct backend.

**Root cause**: bearDog operates as a raw TCP proxy, not an HTTP-aware reverse proxy.
It terminates TLS but forwards all traffic to a single upstream regardless of SNI/Host.

**Fix**: Restored Caddy on :443 as the front door. Caddy provides Host-based routing,
HTTP/2 with ALPN, and ACME cert management for all domains. bearDog ACME gateway
moved to standby on internal port 9999.

### 2. HTTP/2 downgrade

bearDog's raw TCP proxy doesn't negotiate ALPN, so browsers fell back to HTTP/1.1.
Caddy's restoration on :443 immediately restored HTTP/2 (and HTTP/3 via alt-svc).

### 3. Port 8443 exposure

With Caddy on non-standard :8443, all existing links to `git.primals.eco`,
`lab.primals.eco`, and `membrane.primals.eco` on :443 broke. The fix (Caddy on :443)
eliminated the need for :8443 entirely. UFW rule for 8443 removed.

## Content Issues Found

### Missing contact page

The base template references `@/contact.md` which didn't exist in the source tree.
The live site worked because it was built from a previous version. Created
`content/contact.md` with email, GitHub, Forgejo links, and compute access pointer.

### Stale compute-access.md

The lab compute-access page described the old Cloudflare Tunnel architecture.
Updated to reflect the sovereign mesh path:

```
Browser → lab.primals.eco → golgi Caddy :443 → WireGuard → sporeGate songBird
  → capability.call("jupyter") → ironGate JupyterHub :8000
```

- Hardware specs updated (RTX 5070 Ti, 64-core EPYC, 128GB ECC)
- Architecture diagram rewritten for songBird drawbridge routing
- Zero Cloudflare references remaining

## Validation Matrix

| Check | Before | After |
|-------|--------|-------|
| primals.eco :443 | sporePrint (bearDog) | sporePrint (Caddy) |
| www.primals.eco | 301 redirect | 301 redirect |
| membrane.primals.eco :443 | sporePrint (WRONG) | membrane health (Caddy) |
| git.primals.eco :443 | sporePrint (WRONG) | Forgejo (Caddy) |
| lab.primals.eco :443 | sporePrint (WRONG) | songBird drawbridge (Caddy) |
| HTTP/2 | NO (HTTP/1.1, no ALPN) | YES (h2, ALPN negotiated) |
| TLS cert | Let's Encrypt (bearDog) | Let's Encrypt (Caddy) |
| /contact/ | 200 (stale build) | 200 (content created) |
| /lab/compute-access/ | Cloudflare Tunnel text | songBird drawbridge text |
| All 30 internal links | 200 | 200 |

## Architecture — Current State (golgi)

```
Internet → Caddy :443 (ACME, HTTP/2, Host routing)
    ├── primals.eco     → sporePrint static files (/opt/ecoPrimals/sporePrint/public)
    ├── www.primals.eco → 301 → primals.eco
    ├── membrane.*      → depot file_server + health + nestgate
    ├── git.*           → Forgejo :3000
    └── lab.*           → reverse_proxy → sporeGate songBird :7780 (WireGuard)
```

bearDog runs on internal port 9999 (standby). Enabled when bearDog gains SNI-aware
Host routing — then it can replace Caddy for primals.eco while Caddy handles subdomains.

## Files Changed

- `provision-golgi.sh` — Caddy restored to :443, bearDog standby, UFW updated
- `sporePrint/content/lab/compute-access.md` — songBird drawbridge architecture
- `sporePrint/content/contact.md` — new (missing page fix)
- `/etc/membrane/Caddyfile` (golgi live) — full Host routing config
- `beardog-sporeprint.service` (golgi live) — disabled, standby

## Forward Work

1. **bearDog SNI dispatch** — add Host-header routing to bearDog's gateway mode
   so it can eventually replace Caddy for primals.eco TLS
2. **petalTongue visualization** — NUCLEUS composition on sporeGate with
   sporePrint-aware dashboard (see POSTMORTEM_134h.md)
3. **Zola CI pipeline** — sporePrint source lives in git but builds are manual;
   wire `zola build` into the sovereign-ci cascade
