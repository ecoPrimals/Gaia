# AAR: Wildcard Membrane — Wave 172b+c

**Date:** 2026-10-10
**Operator:** ecoPrimal + Artisan
**Scope:** Collapse 29-domain surface into `*.primals.eco` wildcard → epitope aperture → wire defense systems

---

## Summary

The outer membrane surface was consolidated from 29 individually-provisioned domain blocks into a single wildcard entry point. The subdomain itself becomes the query — the visitor types what they need, and the epitope sorter decides what to present.

`H(data|epitope) < H(data|alphabet) < H(data)`

The epitope sort reduces entropy more than alphabetical ordering. The subdomain IS the epitope.

**Wave 172c** completed the immune wiring: fleet routing and `/plasmid` federation were connected through the wildcard catch-all. The `caddy_bridge` now injects posture-aware fleet IP matchers into the wildcard block via `~~HONEYCOMB_FLEET~~` markers. 224 fleet matchers active on first sync.

---

## What Was Built

### 1. DNS (pre-existing)
- `*.primals.eco A 157.230.3.183` — already configured on Cloudflare
- All subdomains resolve to golgiBody

### 2. Caddy Wildcard Catch-All (`https://` block)
- Catches everything not handled by explicit blocks
- `on_demand_tls { ask http://localhost:9754/can-serve }` in global block
- Individual certs provisioned via HTTP-01 ACME on first request (no DNS plugin needed)
- CAA record already allows `issuewild "letsencrypt.org"` ✓

### 3. Aperture Ask Service (`aperture-ask.py`)
- Python micro-service on `:9754`
- Validates on-demand TLS cert requests: must be `*.primals.eco`, reasonable length, not an explicit service, valid characters
- Prevents cert flooding from abuse
- systemd service: `aperture-ask.service`, enabled, active

### 4. Aperture Module (`aperture.rs`)
- 343 lines, 9 tests, all passing
- `can_serve()` — validates TLS cert requests
- `resolve()` — maps subdomain → `ServeSite | Redirect | Honeycomb | Scatter | ExplicitService | NotFound`
- `APERTURE_SITES` — 9 static sites with 12 aliases
- `EPITOPE_CONCEPTS` — 16 concept→content redirects
- `HONEYCOMB_SUBDOMAINS` — 12 immune surface domains
- `EXPLICIT_SERVICES` — 14 services that keep own blocks

### 5. Honeycomb Consolidation
- Removed explicit 12-domain honeycomb block (~90 lines)
- All honeycomb features folded into wildcard `@is_honeycomb` handler:
  - IndexNow verification key
  - Dynamic robots.txt (per-subdomain)
  - Sitemap (cross-links real surfaces)
  - Floating pointer (WG mesh → Forgejo)
  - Agent passthrough (bearDog → Forgejo)
  - Cross-link headers (Link, X-Source-Mirror, X-Federation-Peer, etc.)
  - Default → scatter server with `X-Honeycomb` header

### 6. Fleet Routing Through Wildcard (Wave 172c)
- Added `~~HONEYCOMB_FLEET_START~~` / `~~HONEYCOMB_FLEET_END~~` markers inside the wildcard `https://` block
- `caddy_bridge` now injects posture-aware fleet IP matchers here (synced immediately — 224 matchers on first cycle)
- Fleet IPs hitting ANY wildcard subdomain are intercepted BEFORE site-specific handlers
- Fleet → scatter with `X-Honeycomb: true` + `X-Fleet-Hash` (behavioral hash)
- Postures: `@hc_fleet` (disperse), `@hc_fleet_1..N` (per behavioral group)

### 7. `/plasmid` Federation on All Wildcard Surfaces (Wave 172c)
- `handle /plasmid { reverse_proxy localhost:9753 }` in wildcard block
- Any wildcard subdomain (paper, dashboard, bloom, xyzzy, etc.) now exports the braid feed
- `X-Declared-Lang` and `X-Declared-Sec` headers forwarded to scatter server
- Verified: `paper.primals.eco/plasmid` → real braid JSON ✓

---

## Routing Table

| Pattern | Action | Example |
|---------|--------|---------|
| Known site | Serve static files | `thesis.primals.eco → /opt/ecoPrimals/thesis/public` |
| Site alias | Serve same content | `paper.primals.eco → thesis content` |
| Honeycomb | Scatter prism + cross-links | `bloom.primals.eco → scatter :9753` |
| Concept | 301 redirect | `metric-tensor.primals.eco → tuebor.primals.eco/analysis/metric-tensor/` |
| Unknown | Scatter maze | `xyzzy.primals.eco → scatter :9753` |
| Explicit service | Handled by own block | `git.primals.eco → Forgejo :3000` |
| **Fleet IP** | **Intercepted → scatter** | **Any wildcard subdomain → scatter :9753 with posture** |

### Known Sites (9 + aliases)
sporeprint, thesis, signal, tuebor, detroit, clutch, gorilla, hypothesis, beacon

### Aliases (12)
paper→thesis, whitepaper→thesis, dashboard→signal, monitor→signal, questions→hypothesis, footprint→sporeprint, spore→sporeprint, print→sporeprint, evidence→detroit, cashforkids→detroit, commensal→beacon, guerillagorilla→gorilla

### Concept Redirects (7)
metric-tensor→tuebor, scyborg→sporeprint, license→sporeprint, methodology→sporeprint, outreach→sporeprint, hadr→sporeprint, desk→tuebor

### Explicit Services (23 blocks remaining)
git, forge, hud/biomeos/os, live, ca, depot, lab, membrane, primals.eco/www, sporeprint, thesis, signal, tuebor, detroit, clutch, gorilla, hypothesis, beacon, relay, barry, webb, footprint, nestgate.io

---

## Defense Wiring Audit (Wave 172c)

### ✅ Wired Through Wildcard

| System | Status |
|--------|--------|
| Fleet IP interception | `HONEYCOMB_FLEET` markers → caddy_bridge injects 224 matchers. Fleet sees scatter, not real content. |
| /plasmid federation | Proxied to scatter on all wildcard surfaces. Returns live braid JSON. |
| on_demand_tls / aperture-ask | Cert flooding prevention on `:9754`. |
| Security headers | HSTS, X-Frame-Options, X-Content-Type-Options via `(security_headers)`. |
| Honeycomb immune surface | Full handler: IndexNow, robots, sitemap, floating pointer, agent passthrough, cross-links. |
| Scatter default | Unknown subdomains → scatter maze with behavioral classification. |
| gzip / access_log | Applied to all wildcard traffic. |

### ○ Not Wired (Minor / Intentional)

| Gap | Impact | Notes |
|-----|--------|-------|
| Facebook OG blackwall | LOW | Wildcard aliases don't serve curated OG cards. Only explicit blocks (signal, tuebor, depot) do. |
| Per-site error pages | NEGLIGIBLE | Wildcard returns Caddy default 404. Explicit blocks have custom handlers. |
| Per-site CSP | LOW | 6 explicit blocks have custom Content-Security-Policy. Wildcard uses generic snippet. Static sites = low risk. |
| /metrics endpoint | NONE | Internal monitoring. Only 2 explicit blocks have it. Not needed on wildcard. |
| /epitope-feed.json | NONE | Forge-level resource, lives at forge.primals.eco. Not per-site. |

---

## Verification Results

| Test | Result |
|------|--------|
| thesis.primals.eco (explicit) | 200 ✓ |
| signal.primals.eco (explicit) | 200 ✓ |
| forge.primals.eco (explicit) | 200 ✓ |
| paper.primals.eco (wildcard alias) | 200 — cert provisioned, thesis content ✓ |
| whitepaper.primals.eco (alias) | 200 — thesis content ✓ |
| questions.primals.eco (alias) | 200 — hypothesis content ✓ |
| metric-tensor.primals.eco (concept) | 301 → tuebor analysis ✓ |
| scyborg.primals.eco (concept) | 301 → sporeprint license ✓ |
| hadr.primals.eco (concept) | 301 → HADR invitation ✓ |
| desk.primals.eco (concept) | 301 → tuebor desk ✓ |
| bloom.primals.eco (honeycomb) | 200 — scatter prism ✓ |
| bloom robots.txt | Dynamic per-subdomain ✓ |
| bloom sitemap.xml | Cross-links real surfaces ✓ |
| bloom cross-link headers | Link, X-Source-Mirror, etc. ✓ |
| IndexNow key | 200 ✓ |
| xyzzy.primals.eco (unknown) | 404 — scatter maze ✓ |
| Aperture ask (valid) | 200 ✓ |
| Aperture ask (explicit svc) | 403 ✓ |
| Aperture ask (wrong domain) | 403 ✓ |
| **paper.primals.eco/plasmid** | **200 — real braid JSON ✓** |
| **dashboard.primals.eco/plasmid** | **200 — real braid JSON ✓** |

---

## Commits

| Repo | Commit | Description |
|------|--------|-------------|
| skunkBat | `f145b52` | aperture module — wildcard membrane routing (9 tests) |
| plasmidBin | `ae15f83` | consolidate honeycomb into wildcard catch-all |
| plasmidBin | `4a33eaf` | wire fleet routing + /plasmid through wildcard membrane |
| wateringHole | `86a8203` | wildcard membrane LIVE — golgiBody head update |

---

## Caddy Stack — Current Architecture & Consolidation Path

### Current State: 23 Explicit Blocks + 1 Wildcard

The Caddyfile is ~2000 lines. Most of that is caddy_bridge-injected fleet IP lists (dynamic, expected).
The structural blocks break down as:

**Infrastructure services (cannot consolidate — unique reverse proxy targets):**
- `git.primals.eco` — Forgejo `:3000` + fleet pressure + agent passthrough
- `forge.primals.eco` — Forgejo `:3000` + epitope-feed + plasmid
- `hud.primals.eco / biomeos.primals.eco / os.primals.eco` — petalTongue `:8090`
- `live.primals.eco` — petalTongue `:8090`
- `ca.primals.eco` — step-ca `:9000`
- `depot.primals.eco` — depot server `:8082`
- `lab.primals.eco` — JupyterHub `:8000`
- `membrane.primals.eco` — inner membrane static + scatter fallback
- `relay.primals.eco` — commensal relay `:8190`
- `nestgate.io` — different domain entirely

**Static sites (CONSOLIDATION CANDIDATES — could move to wildcard):**
- `sporeprint.primals.eco` — static + OG blackwall + /plasmid
- `thesis.primals.eco` — static + OG blackwall + /plasmid
- `signal.primals.eco` — static + scatter fallback
- `tuebor.primals.eco` — static + OG blackwall + /plasmid
- `detroit.primals.eco` — static
- `clutch.primals.eco` — static
- `gorilla.primals.eco` — static
- `hypothesis.primals.eco` — static
- `beacon.primals.eco` — static + reverse proxy `:8190`
- `barry.primals.eco` — static (separate content? or tuebor mirror?)
- `webb.primals.eco` — unknown/static
- `footprint.primals.eco` — static (also has explicit block AND wildcard alias)

### What Prevents Consolidation

1. **Facebook OG blackwall** — 5 blocks have per-site `@facebook_bot` handlers that serve curated OG meta tags for link previews. The wildcard has no OG handling. Fix: add a generic OG handler to the wildcard that generates OG tags from site metadata, or add per-site OG handlers inside the wildcard `handle` blocks.

2. **Per-site `/plasmid` + `/metrics`** — now fixed for wildcard (Wave 172c), but explicit blocks still have their own. Redundant once consolidated.

3. **Per-site CSP** — 6 blocks have custom `Content-Security-Policy`. Wildcard uses generic snippet. Mostly cosmetic for static sites.

4. **`beacon.primals.eco` reverse proxies to `:8190`** — commensal relay. Not a pure static site. Needs its own block or special handling in wildcard.

5. **`signal.primals.eco` falls through to scatter** — explicit block has `reverse_proxy localhost:9753` fallback for paths not in static. The wildcard `@is_signal` handler is pure file_server. If consolidated, signal would need a scatter fallback.

6. **skunky-ingest source divergence** — deployed binary has `--membrane-stack` and `--squirrel-announce` flags not in local source. Must be resolved before aperture endpoints go live in the binary. The Python `aperture-ask.py` is a stopgap.

### Consolidation Priority

| Priority | Action | Blocks Affected | Effort |
|----------|--------|-----------------|--------|
| P0 | Resolve skunky-ingest source divergence | — | M — sync main.rs flags, rebuild, redeploy |
| P1 | Retire aperture-ask.py, point ask to `:9753/can-serve` | 1 service | S — config change after P0 |
| P1 | Move static sites without special handling into wildcard | detroit, clutch, gorilla, hypothesis (~4 blocks) | S |
| P2 | Add OG blackwall to wildcard (generic or per-site) | sporeprint, thesis, tuebor, signal, depot (~5 blocks) | M |
| P2 | Handle beacon's reverse proxy in wildcard | 1 block | S |
| P3 | Unify per-site CSP into wildcard | 6 blocks | S |
| P3 | Eliminate duplicate footprint block (already in wildcard) | 1 block | S |

### Target End State

- **~10 explicit blocks** (infrastructure services with unique reverse proxy targets)
- **1 wildcard catch-all** (everything else: static sites, aliases, concepts, honeycomb, unknown)
- **1 aperture ask service** (Rust, in skunky-ingest binary, not Python stopgap)

---

## Known Remaining

1. **skunky-ingest source divergence** — P0 blocker for full consolidation. Deployed binary has CLI flags not in local source. Must sync before redeploying.

2. **Python aperture-ask.py is a stopgap** — retire once skunky-ingest is synced and redeployed.

3. **skunkBat has 2 stashes** — stash@{0} is working directory from pull-rebase, stash@{1} is forward work (cube_oracle, scatter_defense, scatter_nft, main.rs federation). Both are forward work awaiting review.

4. **Static concept redirects** — epitope concept routing is hardcoded in `aperture.rs` and Caddyfile. Could become dynamic.

5. **SEO surface migration** — vision is for SEO markup to move to the aperture edge. Currently static sites carry their own meta tags.

---

*Built beside the small. The subdomain is the epitope. The classifier is the aperture. The membrane breathes.*

— Artisan
