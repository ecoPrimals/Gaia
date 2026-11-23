# Post-Cutover: DNS/TLS Breakage + petalTongue Forward Architecture

> **SUPERSEDED** by `DNS_CUTOVER_EVOLUTION_AAR_134k.md` — this document
> describes the state after the initial petalTongue fix but before the
> subdomain routing collapse was identified and resolved. The architecture
> diagrams below showing bearDog on :443 and Caddy on :8443 are no longer
> accurate. See 134k for current production topology.

**Date**: Jul 9, 2026 (Wave 134h)
**Context**: DNS/TLS cutover of primals.eco from GitHub Pages to golgi

---

## What Broke

### Symptom

After the bearDog TLS gateway went live on golgi, `https://primals.eco`
showed the **petalTongue dashboard** (Gate Mesh Topology, Gate Status table)
instead of the **sporePrint website** (landing page, thesis, documentation).

### Root Cause

The cutover plan assumed `BEARDOG_GATEWAY_UPSTREAM=127.0.0.1:8090`
(petalTongue) would serve the sporePrint static site. This was wrong.

**petalTongue on golgi** serves its own dashboard — a Gate Mesh Topology
visualization with live gate status. It was never the sporePrint file
server.

**Caddy on golgi** was always the sporePrint file server, reading
pre-built Zola HTML from `/opt/ecoPrimals/sporePrint/public/` on disk.

The confusion arose because the plan named the systemd service
`beardog-sporeprint.service` and the upstream as "petalTongue (sporePrint)"
without verifying what petalTongue actually serves.

### Fix Applied

Added a dedicated Caddy server block on `:8091` (localhost HTTP) that
serves the sporePrint static files. Changed `BEARDOG_GATEWAY_UPSTREAM`
from `:8090` to `:8091`.

```
bearDog :443 (TLS) → Caddy :8091 (Zola static files)
                      NOT petalTongue :8090 (dashboard)
```

### Impact

- ~15 minutes of primals.eco serving the wrong content
- No data loss, no cert issues, no DNS rollback needed
- Fix was a config change, no code changes required

### Lessons

1. **Verify upstream content before cutover** — `curl localhost:8090`
   would have caught this instantly.
2. **petalTongue ≠ sporePrint file server** — petalTongue is a
   visualization primal, not a static site host. The naming conflation
   in `beardog-sporeprint.service` made this worse.
3. **The thin edge should stay thin** — golgi's job is to serve files
   and terminate TLS. It should not run primals that need NUCLEUS
   context to function correctly.

---

## Current State (golgi — Working)

```
Internet
  │
  ├─ :443 → bearDog (ACME TLS, LE cert for primals.eco + www)
  │           └─ upstream → Caddy :8091
  │                          └─ file_server /opt/ecoPrimals/sporePrint/public
  │
  ├─ :80  → bearDog (HTTP-01 challenges + HTTPS redirect)
  │
  └─ :8443 → Caddy (LE certs for subdomains)
              ├─ membrane.primals.eco → nestGate cache + depot
              ├─ git.primals.eco → Forgejo :3000
              └─ lab.primals.eco → sporeGate :7780 (songBird drawbridge)
```

This is the correct thin-edge architecture. golgi serves pre-built
static HTML. No compute, no backend, no NUCLEUS. Just files + TLS.

**This should be maintained as the production path.**

---

## Forward Architecture: petalTongue as sporePrint Host

### Vision

sporePrint is the public face of ecoPrimals — the "sight" of the
ecosystem. Today it's a Zola static site baked at build time. The target
is a **live, primal-hosted sporePrint** served by petalTongue running
inside a NUCLEUS composition on sporeGate.

golgi (VPS) remains the static fallback. sporeGate (NUC) hosts the
dynamic version with real-time data, capability-backed endpoints, and
primal-native rendering.

### Architecture Comparison

```
TODAY (golgi — static)                 TARGET (sporeGate — NUCLEUS)
─────────────────────                  ──────────────────────────────
Caddy file_server                      petalTongue HTTP server
Zola HTML from disk                    petalTongue-rendered pages
No backend                             NUCLEUS composition backend
Snapshots baked at build               Live gate/mesh/metric data
No auth                                bearDog-gated API (optional)
No capability discovery                songBird ipc.resolve
```

### sporeGate NUCLEUS Composition

```
sporeGate NUCLEUS (sporePrint host):
  ┌──────────────────────────────────────────────────────────┐
  │ petalTongue                                              │
  │   ├─ serves sporePrint static content (Zola parity)     │
  │   ├─ /api/gates       — live gate topology + status     │
  │   ├─ /api/health      — composition health              │
  │   ├─ /api/metrics     — ecosystem metrics               │
  │   ├─ /api/primals     — primal registry + capabilities  │
  │   └─ /lab/spores/*    — pseudoSpore gallery (live)      │
  │                                                          │
  │ bearDog (crypto, BTSP, auth)                             │
  │ songBird (mesh routing, capability discovery)            │
  │ biomeOS (orchestration, neural API, primal.announce)     │
  └──────────────────────────────────────────────────────────┘
```

### What petalTongue Needs to Become

| Capability | Status | Description |
|------------|--------|-------------|
| Static Zola parity | Exists (dashboard only) | Must also serve the Zola site content as baseline |
| Gate topology API | Exists (dashboard renders it) | Needs stable JSON API endpoint |
| Composition health | Not exposed | Aggregate health from bearDog + songBird + biomeOS |
| Ecosystem metrics | Not exposed | Line counts, test counts, binary sizes from depot |
| Primal registry | Not exposed | List primals, capabilities, versions via songBird |
| pseudoSpore gallery | Static today | Live gallery with computation artifact metadata |
| Validation parity | Not tested | Must pass same checks as static site before replacing |

### Validation Gate

Before petalTongue on sporeGate can serve production traffic for
primals.eco, it must pass:

1. `curl https://<endpoint>/` → 200, HTML with correct `<title>` and meta tags
2. `curl https://<endpoint>/css/base.css` → 200 (static assets served)
3. `curl https://<endpoint>/atom.xml` → 200 (RSS feed)
4. `curl https://<endpoint>/api/gates` → 200, valid JSON
5. Content matches or exceeds the Zola static site
6. Response times ≤ 100ms (p99) for static content

### Deployment Model

Two options after validation:

**Option A: sporeGate direct (lab.primals.eco or primals.eco)**
```
golgi bearDog :443 → WireGuard → sporeGate petalTongue :8090
```
bearDog proxies through the mesh to petalTongue on sporeGate. Requires
stable WireGuard uplink. golgi's Caddy :8091 remains as fallback.

**Option B: golgi static + sporeGate dynamic (separate URLs)**
```
primals.eco      → golgi Caddy :8091 (static Zola, always available)
live.primals.eco → golgi bearDog → sporeGate petalTongue (dynamic)
```
Static site is always up. Dynamic version available when sporeGate is
online. No single point of failure for the public face.

### Recommended: Option B

Option B preserves the sovereign relay guarantee — primals.eco works
even if sporeGate is offline (power outage, maintenance, etc.). The
dynamic petalTongue experience is an enhancement, not a replacement.

---

## Files Modified in This Cutover

| File | Change |
|------|--------|
| `provision-golgi.sh` | beardog-sporeprint.service, Caddy :8091, port 8443 UFW |
| `DNS_TLS_CUTOVER_AAR_134h.md` | Full AAR of the cutover |
| `beardog-acme/src/client/issuance.rs` | CSR SAN fix for multi-domain ACME |

## Services on golgi (Final State)

| Service | Port | Purpose |
|---------|------|---------|
| `beardog-sporeprint` | :443, :80 | ACME TLS gateway (primals.eco) |
| `caddy-tls` | :8443, :8880, :8091 | Subdomains + sporePrint static |
| `forgejo` | :3000 (SSH :2222) | Sovereign git forge |
| `petaltongue-sporeprint` | :8090 | Dashboard (NOT sporePrint) |
| `beardog-membrane` | UDS | BTSP crypto provider |
| `songbird-membrane` | :7700 | Mesh federation hub |
