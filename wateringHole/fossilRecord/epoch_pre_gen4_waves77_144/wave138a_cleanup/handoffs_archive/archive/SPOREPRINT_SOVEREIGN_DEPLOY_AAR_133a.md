# sporePrint Sovereign Deployment — After Action Review (Wave 133a)

**Gate:** eastGate | **Date:** 2026-07-06 | **Primal:** sporePrint
**From:** eastGate overwatch | **Type:** AAR — deployment divergence + path forward

---

## Situation

sporePrint (`primals.eco`) is the public website for the ecoPrimals ecosystem.
It is currently served via **GitHub Pages** as primary, with a VPS shadow
on golgi (Caddy file_server from `/opt/ecoPrimals/sporePrint/public`).

The sovereign deployment pipeline was designed to make the VPS primary and
GitHub Pages trailing shadow. **DNS NS cutover has not happened.** As a result,
sporePrint remains dependent on GitHub for public visibility.

---

## Divergences Found

### SP-DIV-01: GitHub Pages is still primary (P1 — sovereignty gap)

- `primals.eco` DNS resolves to GitHub Pages, not the VPS
- All site updates require push to GitHub `origin` to be visible
- The VPS shadow exists but serves no public traffic
- **Blocker:** DNS NS cutover requires eastGate manual action (registrar change)
- **Upstream dependency:** TLS graduation on the VPS (bearDog ACME or Caddy TLS)

**Impact:** sporePrint is not sovereign. A GitHub outage would take the public site offline.

### SP-DIV-02: Dual-push requirement (P2 — operational friction)

- sporePrint must push to BOTH `origin` (GitHub) and `forgejo` on every commit
- Previously only pushed to Forgejo, causing 404s on the live site
- This is a workaround for SP-DIV-01, not a fix
- **Fix:** Resolve DNS cutover. Once VPS is primary, Forgejo-only push is sufficient.

### SP-DIV-03: No NUCLEUS on the VPS (P1 — blocks living site)

- The VPS (golgi) serves static files via Caddy `file_server`
- No petalTongue, no NestGate, no songBird on the VPS
- sporePrint's `viz_embed` shortcode renders static SVG fallbacks because
  petalTongue isn't running on the serving host
- Live mesh topology, entity graph visualization, and dynamic content
  all require a NUCLEUS composition (or at minimum petalTongue + NestGate)

**Impact:** sporePrint cannot serve live visualizations or dynamic content.
The site is static HTML only.

### SP-DIV-04: `temporal.cascade` doesn't rebuild Zola (P2 — stale content on VPS)

- `temporal.cascade` on golgi pulls the sporePrint repo (git pull)
- But it does NOT run `zola build` to regenerate `public/`
- The VPS serves whatever `public/` was last built manually
- **Fix:** Add a post-cascade hook that runs `zola build` in the sporePrint
  checkout, or have Sovereign CI on sporeGate rsync the built `public/`
  output to golgi after each build.

### SP-DIV-05: `deploy.yml` still active (P3 — cleanup after cutover)

- `.github/workflows/deploy.yml` runs on every GitHub push
- Labeled as "trailing shadow" since Wave 69 but still doing the actual serving
- After DNS cutover, this workflow should be archived to fossilRecord
- Until then, it's load-bearing — removing it would kill the live site

---

## Path Forward: NUCLEUS on VPS

The correct resolution for SP-DIV-01 through SP-DIV-04 is deploying a minimal
NUCLEUS composition on the VPS (golgi or a dedicated sporePrint host). This
replaces Caddy file_server with content-addressed delivery and enables live
visualizations.

### Minimal NUCLEUS for sporePrint Serving

| Primal | Role | Required? |
|--------|------|-----------|
| **petalTongue** | Content rendering, SVG visualization, `/api/` endpoints | Yes |
| **NestGate** | CAS storage, content-addressed serving, route registration | Yes |
| **songBird** | Mesh routing (for live mesh.peers data in topology viz) | Yes (for live viz) |
| **bearDog** | TLS termination (ACME cert for primals.eco) | Yes (replaces Caddy) |
| **sweetGrass** | Provenance chain for published content | Optional |
| **biomeOS** | Composition coordinator | Optional |

### Deploy Sequence

1. **Build binaries** for VPS target (x86_64-musl — already in depot, Wave 133a)
2. **Deploy petalTongue** on VPS — configure for sporePrint content directory
3. **Deploy NestGate** — run `spore-validate cas-push` to populate CAS
4. **Deploy songBird** — mesh.init with existing peers (sporeGate, eastGate)
5. **Deploy bearDog** — ACME cert for `primals.eco`, TLS on :443
6. **DNS NS cutover** — point `primals.eco` to VPS IP
7. **Shadow period** — bearDog + Caddy in parallel for 7 days
8. **Archive `deploy.yml`** — GitHub Pages becomes trailing shadow only
9. **Remove dual-push** — Forgejo-only push flow restored

### What This Unlocks

- **Live mesh topology** — petalTongue queries songBird `mesh.peers` and renders
  real-time SVG with actual latency data
- **Entity graph visualization** — petalTongue renders the full 66-node entity
  graph as interactive SVG
- **CAS-backed serving** — every page content-addressed with BLAKE3, dedup
  across builds, integrity verified on serve
- **Self-certifying site** — guideStone certification manifest is verified
  at serve time, not just at build time
- **Forgejo-only workflow** — no GitHub dependency for public visibility

---

## Upstream Audit Requests

### For cellMembrane team (sporeGate)

- **SP-DIV-04:** Add post-cascade `zola build` hook for sporePrint checkout, OR
  rsync built `public/` from sporeGate CI to golgi after each build

### For cellMembrane team (golgi)

- **SP-DIV-03:** Evaluate golgi as NUCLEUS host for sporePrint serving.
  Golgi is a 10GB VPS — a minimal composition (petalTongue + NestGate +
  songBird + bearDog) totals ~70MB of binaries. Feasible if disk is managed
  (shallow clones only, per Sovereign CI AAR recommendation).

### For bearDog team (flockGate)

- **SP-DIV-01 dependency:** bearDog CryptoProvider fix (P1 from Wave 132f blurb)
  must land before ACME gateway can run on the VPS for `primals.eco` TLS.

### For eastGate overwatch

- **SP-DIV-01:** DNS NS cutover is a manual registrar action. Schedule after
  bearDog ACME is validated on sporeGate (7-day shadow pass).

---

## Current Workaround

Until NUCLEUS VPS deployment:

```bash
# Every sporePrint commit — push to BOTH remotes
git push origin main && git push forgejo main
```

This ensures GitHub Pages deploys (via `deploy.yml`) AND Forgejo has the
latest for Sovereign CI and cascade.

---

*sporePrint is code-healthy (254 tests, 226 pages, 0 broken links). The gap
is deployment sovereignty. The fix is NUCLEUS on the VPS.*
