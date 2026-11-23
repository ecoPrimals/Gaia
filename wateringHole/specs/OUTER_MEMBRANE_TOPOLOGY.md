# Membrane Topology — Full Surface Specification (Eukaryotic Model)

**Date**: Oct 9, 2026 | **Wave**: 167+ | **Owner**: overwatch + sporeGate (sporePrint)
**Status**: LIVE reference. Update this file when any surface configuration changes.
**Model**: Eukaryotic 5-layer + nucleus (evolved from prokaryotic 3-layer, Wave 157k)

---

## Architecture

The architecture follows the **Eukaryotic Cell Model**. Public traffic terminates at
**golgiBody Caddy** (`[RELAY_PUBLIC]:443`). Observation layers distribute across
jurisdictions. The **nucleus** is a sovereign personal core tied to a human, not a system.

```
Internet
    │
    ├─ primals.eco ─────── OUTER MEMBRANE (Cloudflare DNS → golgiBody Caddy)
    │     RustDesk relay, commensal beacon, fleet observation
    │
    ├─ *.primals.eco ──── PERIPLASM (observation layers, public surfaces)
    │     sporePrint, detroit, signal, thesis, tuebor, HUD
    │     golgi-de, golgi-in, golgi-jp, golgi-us (fleet observation)
    │
    ├─ nestgate.io ─────── PEPTIDOGLYCAN (Sovereign Knot DNS → golgiBody Caddy)
    │     petalTongue live data/trust surface (CAS, provenance, federation)
    │
    ├─ primal.eco ──────── INNER MEMBRANE (Sovereign Knot DNS, SEALED)
    │     0 public A records. WireGuard mesh only.
    │
    └─ nucleus ─────────── NUCLEUS (10.13.37.16, no public surface)
          Sovereign human core. Repo mirrors, identity, vault.
          Nuclear envelope: DNS + SSH-inner-only + WG.
          ns2.primals.eco Knot slave (load-bearing).
```

---

## DNS Layer

### Registrar + Nameserver Ownership

| Domain | Registrar | DNS Provider | Nameservers |
|--------|-----------|--------------|-------------|
| **primals.eco** | Porkbun | **Cloudflare** | `albertus.ns.cloudflare.com`, `serena.ns.cloudflare.com` |
| **nestgate.io** | Porkbun | **Sovereign Knot DNS** | `ns1.primals.eco`, `ns2.primals.eco` |
| **primal.eco** | Porkbun | **Sovereign Knot DNS** | `ns1.primals.eco`, `ns2.primals.eco` |

### Sovereign DNS Infrastructure

| Server | IP | Role |
|--------|-----|------|
| `ns1.primals.eco` | `[RELAY_PUBLIC]` | golgiBody — Knot master |
| `ns2.primals.eco` | `137.184.197.151` | **nucleus** — Knot slave (formerly golgiBody-ext) |

- Auto DNSSEC (ECDSA P-256), AXFR/IXFR zone transfers
- CAA records: `issue "letsencrypt.org"` + `issuewild "letsencrypt.org"`
- DNSSEC for primals.eco verified: DS 2371/13/2 chain (Porkbun → .eco TLD → Cloudflare KSK)

### Cloudflare DNS Records (primals.eco)

| Type | Name | Target | Notes |
|------|------|--------|-------|
| A | `primals.eco` | `[RELAY_PUBLIC]` | Root domain |
| CNAME | `sporeprint` | `primals.eco` | Main website |
| CNAME | `lab` | `primals.eco` | JupyterHub |
| CNAME | `relay` | `primals.eco` | RustDesk bootstrap |
| CNAME | `ca` | `primals.eco` | step-ca SSH CA |
| CNAME | `depot` | `primals.eco` | Binary depot |
| A | `git` | `[RELAY_PUBLIC]` | Forgejo |
| Wildcard | `*.primals.eco` | → golgiBody | Caddy is routing authority |

**Not in repo**: Cloudflare zone is managed via dashboard. No API automation exists.

---

## TLS + Caddy Routing

All public TLS terminates at golgiBody Caddy. Let's Encrypt certificates via ACME.

**Version-controlled Caddyfile**: `infra/plasmidBin/membrane/Caddyfile`
**Live Caddyfile**: `/etc/membrane/Caddyfile` on golgiBody
**Known drift**: RESOLVED (Wave 158 — VC synced to live Sep 27)

### Full Routing Map

| Hostname | DNS Source | Caddy Action | Backend Target | Gate | Service |
|----------|-----------|-------------|----------------|------|---------|
| `primals.eco` | CF A | 301 → `sporeprint.primals.eco` (except `/enroll*`) | — | golgi | Redirect |
| `primals.eco/enroll*` | CF A | `reverse_proxy 127.0.0.1:7780` | local | golgi | Enrollment portal |
| `www.primals.eco` | CF CNAME | 301 → `sporeprint.primals.eco` | — | golgi | Redirect |
| **`sporeprint.primals.eco`** | CF CNAME | `file_server /opt/ecoPrimals/sporePrint/public` | local | golgi | **Zola static site** |
| `footprint.primals.eco` | CF wildcard | `reverse_proxy 10.13.37.7:3002` | WG→ironGate | ironGate | footPrint GIS |
| `webb.primals.eco` | CF wildcard | `reverse_proxy 10.13.37.7:8090` | WG→ironGate | ironGate | esotericWebb CRPG |
| `live.primals.eco` | CF wildcard | `reverse_proxy 10.13.37.2:8190` | WG→sporeGate | sporeGate | petalTongue topo-viz |
| `lab.primals.eco` | CF CNAME | `reverse_proxy 10.13.37.2:7780` + basicauth | WG→sporeGate | sporeGate | JupyterHub gateway |
| `membrane.primals.eco` | CF wildcard | Mixed: `/depot/*`, `/hooks/*`, health | local | golgi | Depot hooks, status |
| `depot.primals.eco` | CF CNAME | `file_server /opt/ecoPrimals/plasmidBin/` | local | golgi | Binary depot browser |
| `git.primals.eco` | CF A | `reverse_proxy localhost:3000` | local | golgi | **Forgejo** |
| `ca.primals.eco` | CF CNAME | `reverse_proxy localhost:9443` (TLS skip) | local | golgi | **step-ca SSH CA** |
| `relay.primals.eco` | CF CNAME | `file_server` + basicauth | local | golgi | RustDesk info page |
| **`detroit.primals.eco`** | CF wildcard | `file_server /opt/ecoPrimals/detroit/public` | local | golgi | **Cash for Kids 2 evidence library** |
| **`gorilla.primals.eco`** | CF wildcard | `file_server /opt/ecoPrimals/guerillaGorilla/site/public` | local | golgi | **guerillaGorilla methodology** |
| **`guerillagorilla.primals.eco`** | CF wildcard | alias → `gorilla.primals.eco` | local | golgi | guerillaGorilla alias |
| **`nestgate.io`** | Knot A | `reverse_proxy 10.13.37.2:8190` | WG→sporeGate | sporeGate | **petalTongue peptidoglycan** |
| `www.nestgate.io` | Knot A | 301 → `nestgate.io` | — | golgi | Redirect |

### Security Headers (all vhosts)

- HSTS: `max-age=63072000; includeSubDomains; preload`
- X-Content-Type-Options: `nosniff`
- X-Frame-Options: `DENY`
- CSP: per-vhost (sporePrint allows inline styles for Zola)
- Access log: JSON to `/var/log/caddy/access.log` (50 MiB rotation)

---

## sporePrint Deploy Pipeline

### Current Flow (Sovereign-Primary)

```
Developer push → Forgejo (git.primals.eco)
    │
    ├─ post-receive hook: 50-zola-publish
    │     git reset --hard → zola build --force
    │     output → /opt/ecoPrimals/sporePrint/public
    │     Caddy serves immediately (no restart needed)
    │
    ├─ sovereign-ci-trigger → sporeGate (WG mesh)
    │     builds primals, syncs depot (NOT Zola)
    │
    └─ golgiBody-ext: 15-min timer pull
         └─ GitHub Pages trailing shadow (CI: deploy.yml)
```

### Known Issues

| Issue | Detail | Priority |
|-------|--------|----------|
| **SP-DIV-04** | `temporal.cascade` rebuilds primals but doesn't push Zola output to golgi | P1 |
| **Dual checkout** | `/opt/ecoPrimals/sporePrint/` vs `/opt/ecoPrimals/infra/sporePrint/` — path confusion | P1 |
| ~~**Content stale**~~ | ~~sporePrint reflects ~Wave 155m~~ **RESOLVED** — sporePrint current (Wave 158+, 340 pages) | ~~P1~~ |
| ~~**Sitemap 500**~~ | ~~sitemap.xml returns 500~~ **RESOLVED** — content/sitemap → site-map, Caddy handle block | ~~P1~~ |
| ~~**public/ permissions**~~ | ~~root-owned public/ blocks zola build~~ **RESOLVED** — chown -R git:git Sep 27 | ~~P1~~ |
| **Zola version** | 0.22.1 pinned — check compatibility if site fails to build | P2 |

### Target Pipeline (Phase B — Not Live)

CAS-backed serving: NestGate `content.get` → Caddy reverse_proxy, with Zola output stored
in CAS rather than filesystem. Designed in `specs/BUILD_DEPLOY_PIPELINE.md`.

---

## Google Search Console

### Current State (Wave 158 — Sep 27)

- **Property**: `sporeprint.primals.eco` (URL-prefix) — verified
- **Property**: `detroit.primals.eco` (URL-prefix) — verified, GSC sitemap Success, 97 pages discovered
- **Sitemap (sporePrint)**: `/sitemap.xml` → 200, 403 URLs
- **Sitemap (detroit)**: `/sitemap.xml` → 200, 127 URLs. Submitted Sep 25, GSC Status: Success
- **Sitemap (gorilla)**: `/sitemap.xml` → 200, 20 URLs. NEW — not yet submitted to GSC
- **Detroit indexing**: Google Indexing API notified 120/120 URLs. Bing verified via BingSiteAuth.xml
- **IndexNow**: Key deployed on detroit (`indexnow-key.txt`)

### Root Cause: sitemap.xml Was Shadowed (RESOLVED Wave 158)

**Measured Aug 17, 2026**: `sitemap.xml` returned 500. Root cause was `content/sitemap/` directory
shadowing Zola's sitemap.xml generation. Additionally, Caddy's SPA-style `try_files` fallback
was catching `.xml` requests and serving `index.html` instead.

**Both fixes applied Sep 25–27**:
1. `content/sitemap/` → `content/site-map/` unblocked Zola sitemap.xml generation
2. Caddy config updated with explicit `handle /sitemap.xml` block before `try_files`
3. `public/` ownership fixed (`chown -R git:git`) so post-receive hook can rebuild

**Current state**: All sitemaps returning 200. sporePrint 403 URLs, detroit 127 URLs, gorilla 20 URLs.

### What Exists

| Component | Status | Location |
|-----------|--------|----------|
| `robots.txt` | Deployed (`Allow: /`, sitemap pointer) | `infra/sporePrint/static/robots.txt` |
| `sitemap.xml` | **200 OK** — all 3 sites serving (sporePrint 403, detroit 127, gorilla 20 URLs) | Auto-built by Zola, explicit `handle` in Caddy |
| `llms.txt` (4 variants) | Deployed (AI discovery) | `infra/sporePrint/static/llms*.txt` |
| `identity.json` (Schema.org) | Deployed | `infra/sporePrint/static/identity.json` |
| google-site-verification | **NOT FOUND** — may be verified via DNS TXT record | — |
| GSC service account | **DEPLOYED** on golgi | `/opt/ecoPrimals/credentials/gsc-service-account.json` |
| GSC project | `ecoprimals-seo` | Service account: `sporeprint-seo@ecoprimals-seo.iam.gserviceaccount.com` |

### API Capability (Available, NOT Implemented)

The Google Search Console API provides full agentic management:

| Method | Endpoint | What It Does |
|--------|----------|-------------|
| `sitemaps.submit` | `PUT /webmasters/v3/sites/{siteUrl}/sitemaps/{feedpath}` | Submit/resubmit sitemap |
| `sitemaps.get` | `GET /webmasters/v3/sites/{siteUrl}/sitemaps/{feedpath}` | Check sitemap status |
| `sitemaps.list` | `GET /webmasters/v3/sites/{siteUrl}/sitemaps` | List all submitted sitemaps |
| `searchanalytics.query` | `POST /webmasters/v3/sites/{siteUrl}/searchAnalytics/query` | Query search performance |
| `urlInspection.index.inspect` | `POST /v1/urlInspection/index:inspect` | Inspect specific URL indexing |

**Auth**: OAuth 2.0 with `https://www.googleapis.com/auth/webmasters` scope.
**Credentials**: Service account at `/opt/ecoPrimals/credentials/gsc-service-account.json` on golgi.

### Planned `membrane seo.*` Commands (Spec Only — No Rust Implementation)

| Command | Purpose |
|---------|---------|
| `membrane seo.submit-sitemap` | Submit/resubmit sitemap to GSC |
| `membrane seo.status` | Query indexing coverage stats |
| `membrane seo.request-index` | Request indexing for specific URLs |
| `membrane seo.coverage` | Check indexed vs not-indexed breakdown |

**Owner**: sporeGate (cellMembrane) — credentials deployed, API confirmed available.

---

## The Google Problem

### What's Likely Broken

The screenshots show GSC is *working* — sitemap was successfully read on Aug 13, 401 pages discovered. But:

1. **"Processing data"** on the coverage report is normal for new properties or properties that were recently re-verified. GSC can take 2-7 days to process.

2. **The real issue is the property scope**: GSC shows `sporeprint.primals.eco` as the property. But `primals.eco` (root domain) redirects to `sporeprint.primals.eco`. If Google is crawling `primals.eco` and being redirected, it may see the content under `sporeprint.primals.eco` but attribute it differently.

3. **Recommendation**: Verify `primals.eco` as a **Domain property** (`sc-domain:primals.eco`) in addition to the URL-prefix property for `sporeprint.primals.eco`. Domain properties capture all subdomains. This requires a DNS TXT record verification.

4. **Wildcard routing**: If unrecognized subdomains (e.g., `random.primals.eco`) reach Caddy without a matching server block, Caddy's default behavior varies. Ensure unknown subdomains return 404 or redirect to sporePrint, not serve content under different canonical URLs.

---

## sporePrint → NUCLEUS Live Surface (Concept Evolution)

### Phase 0: Fix the Static Site (NOW)
- Triage Zola build on golgi (post-receive hook, dual checkout path, Zola 0.22.1 compat)
- Get primals.eco serving current content
- Verify Google can crawl it

### Phase 1: Live Data Endpoints
- petalTongue routes for gate status, test counts, depot versions
- Same pattern as nestgate.io Phase 2+3
- Caddy proxies new routes to sporeGate petalTongue `:8190`

### Phase 2: cellMembrane Data Pipeline
- Validation counts, spring results, provenance chain stats → petalTongue
- strandGate QCD data (45 configs, plaquette values) served live
- CAS links for references and datasets

### Phase 3: Semantic Layer
- Structured data for translate.js (Validation Class V)
- Machine-readable science data, validation results, references
- JSON-LD enrichment beyond current `identity.json`

### Phase 4: Google SEO Automation
- Implement `membrane seo.*` commands using GSC API
- Automated sitemap resubmission on content change
- Coverage monitoring and indexing status alerts
- Run via sporeGate as agentic SEO management

---

## Cloudflare Configuration (Not in Repo)

Cloudflare manages DNS for `primals.eco` via their dashboard. No API token or Terraform
config exists in the codebase. To automate Cloudflare DNS, the sporeGate team would need
to create a Cloudflare API token and implement `membrane dns.*` commands.

**Critical**: Any DNS changes for `primals.eco` (adding/removing subdomains, TXT records
for domain verification) currently require manual dashboard access.

---

## File Index

| Purpose | Path |
|---------|------|
| Three-domain spec | `wateringHole/specs/THREE_DOMAIN_TOPOLOGY_SPEC.md` |
| This file | `wateringHole/specs/OUTER_MEMBRANE_TOPOLOGY.md` |
| Caddy config (VC) | `plasmidBin/membrane/Caddyfile` |
| sporePrint config | `sporePrint/config.toml` |
| sporePrint deploy spec | `sporePrint/specs/BUILD_DEPLOY_PIPELINE.md` |
| robots.txt | `sporePrint/static/robots.txt` |
| llms.txt | `sporePrint/static/llms.txt` |
| identity.json | `sporePrint/static/identity.json` |
| GitHub shadow CI | `sporePrint/.github/workflows/deploy.yml` |
| Inner DNS (dnsmasq) | `plasmidBin/membrane/primal-eco.dnsmasq.conf` |
| DNS action log | `wateringHole/fossilRecord/.../KDERM_DNS_ACTIONS.md` |
| SEO agentification spec | `wateringHole/fossilRecord/.../CELLMEMBRANE_WAVE151c_SEO_AGENTIFICATION.md` |

---

---

## Nucleus — Sovereign Human Core

**Host**: `nucleus` (formerly `golgiBody-ext`)
**Public IP**: `137.184.197.151` (DO NYC1, 2GB/50GB)
**WireGuard IP**: `10.13.37.16`
**VPC IP**: `10.116.0.5` (DO VPC → golgiBody at `10.116.0.3`)

### Purpose

The nucleus is the innermost layer of the eukaryotic model. It is tied to a HUMAN,
not a system. Every participant who wants sovereignty sets up their own nucleus with
their own physical beacon. This limits computation space to ~n (number of actual
humans with hardware), preventing monopolistic power accumulation.

### Services

| Service | Port | Purpose |
|---------|------|---------|
| Knot DNS | 53 (public) | `ns2.primals.eco` — secondary nameserver (load-bearing) |
| WireGuard | 51820 (public) | Inner membrane mesh (`10.13.37.16`) |
| SSH | 22 (inner-only) | Admin access, restricted to VPC + WG + house WAN |

### Data Store

| Path | Content | Biology |
|------|---------|---------|
| `/opt/nucleus/repos/` | Bare git mirrors (wateringHole, detroit, thesis, signal) | Chromosomes |
| `/opt/nucleus/identity/` | SSH keys, deploy keys | DNA |
| `/opt/nucleus/vault/` | Encrypted credentials (700 perms) | Nuclear pore complex |
| `/opt/nucleus/backup/` | Backup targets | DNA replication |

### Sync

Repo mirrors sync every 30 minutes via `/opt/nucleus/sync-repos.sh`.
Syncs directly from Forgejo bare repo storage on golgiBody via rsync over WireGuard.

### Nuclear Envelope (Firewall)

```
UFW Rules:
  53/tcp,udp    ALLOW     Anywhere        # DNS slave (Knot, ns2)
  22/tcp        ALLOW     10.116.0.3      # SSH from golgiBody VPC
  22/tcp        ALLOW     10.13.37.0/24   # SSH from WireGuard mesh
  22/tcp        ALLOW     [NUCLEUS_WAN]  # SSH from house WAN
  51820/udp     ALLOW     Anywhere        # WireGuard inner membrane
  80,443        BLOCKED   —               # No public HTTP/S. Not a web server.
```

---

*Eukaryotic membrane topology — Wave 167+. Evolved from prokaryotic 3-layer to eukaryotic
5-layer + nucleus. golgiBody Caddy terminates public TLS. Observation layers (Hetzner DE,
Linode IN) federate behavioral data via plasmid sync. Nucleus (formerly golgiBody-ext)
stores sovereign identity and repo mirrors, connected via WireGuard mesh. Knot DNS slave
(ns2.primals.eco) retained on nucleus as load-bearing infrastructure.*
