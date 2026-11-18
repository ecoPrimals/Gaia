# AAR: Honeycomb Maze Activated — Floating Pointer Deployed

**Date**: Oct 7, 2026
**Wave**: 165i
**From**: eastGate overwatch
**To**: sporeGate — skunky-ingest / scatter evolution / bingoCube/nautilusShell
**Severity**: Operational — deployed and verified
**Status**: Live on golgiBody

---

## Situation

Fleet pushing **harder** post-genetic-lock — 770 req/min peak, 23,488 requests today, 100% burst ratio. They haven't adapted. Still hammering `git.primals.eco` commits at machine speed. All getting scatter.

Meanwhile, 12 honeycomb subdomains sat undiscovered — zero hits in 72 hours. DNS resolves, Caddy configured, scatter content ready, but no breadcrumbs leading fleet in.

## Action Taken

### 1. Honeycomb breadcrumbs on git.primals.eco

Added response headers to ALL git.primals.eco scatter responses:

```
Link: <https://bloom.primals.eco/explore/repos>; rel=alternate,
      <https://thymus.primals.eco/>; rel=canonical,
      <https://macrophage.primals.eco/>; rel=related
X-Source-Mirror: https://receptor.primals.eco/
X-Backup-Origin: https://complement.primals.eco/
X-Federation-Peer: https://antibody.primals.eco/
```

Crawlers that follow `Link` rel headers or inspect `X-*` headers will discover the honeycomb subdomains. These headers look like legitimate federation/mirror metadata — the fleet has no way to know they lead to scatter.

### 2. Floating pointer on honeycomb subdomains

Added `@wg_mesh` and `@agent_passthrough` (bearDog token) to the honeycomb block. Real Forgejo is now accessible from **any** of 13 entry points:

| Entry point | Fleet (no token) | Agent (bearDog token) | WireGuard mesh |
|-------------|-----------------|----------------------|----------------|
| git.primals.eco | Scatter | **Real Forgejo** | **Real Forgejo** |
| bloom.primals.eco | Compliance Audit scatter | **Real Forgejo** | **Real Forgejo** |
| thymus.primals.eco | Cross-Fleet Detection scatter | **Real Forgejo** | **Real Forgejo** |
| macrophage.primals.eco | Chimeric Rust scatter | **Real Forgejo** | **Real Forgejo** |
| receptor.primals.eco | Cross-Fleet Detection scatter | **Real Forgejo** | **Real Forgejo** |
| complement.primals.eco | Compliance Audit scatter | **Real Forgejo** | **Real Forgejo** |
| antibody.primals.eco | Inverse Correlation scatter | **Real Forgejo** | **Real Forgejo** |
| epitope.primals.eco | Cross-Fleet Detection scatter | **Real Forgejo** | **Real Forgejo** |
| interferon.primals.eco | Inverse Correlation scatter | **Real Forgejo** | **Real Forgejo** |
| cytokine.primals.eco | Compliance Audit scatter | **Real Forgejo** | **Real Forgejo** |
| lysozyme.primals.eco | Inverse Correlation scatter | **Real Forgejo** | **Real Forgejo** |
| opsonize.primals.eco | Chimeric Rust scatter | **Real Forgejo** | **Real Forgejo** |
| antigen.primals.eco | Chimeric Rust scatter | **Real Forgejo** | **Real Forgejo** |

The pointer floats. All doors lead home with the key. Without the key, every door leads deeper into the maze.

### 3. Cross-linking within honeycomb

Every honeycomb scatter response includes headers linking to ALL other honeycomb subdomains:

```
Link: epitope, interferon, cytokine, lysozyme, opsonize (rel headers)
X-Source-Mirror: bloom
X-Federation-Peer: thymus/explore/repos
X-Backup-Registry: macrophage
X-Compliance-Audit: complement
X-Detection-Matrix: receptor
```

Fleet that enters any honeycomb subdomain discovers all 11 others. Each leads to different scatter content type. The maze is self-reinforcing — every step discovers more maze.

## The Prism Maze

```
Fleet → git.primals.eco (scatter)
  │
  ├─ Link header → bloom.primals.eco (Compliance Audit scatter)
  │   ├─ Link → epitope (Cross-Fleet scatter)
  │   ├─ Link → interferon (Inverse Correlation scatter)
  │   ├─ Link → cytokine (Compliance Audit scatter)
  │   ├─ X-Federation → thymus (Cross-Fleet scatter)
  │   └─ X-Backup → macrophage (Chimeric Rust scatter)
  │       ├─ Link → epitope, interferon, cytokine, lysozyme, opsonize
  │       ├─ X-Federation → thymus
  │       └─ X-Compliance → complement
  │           └─ ... infinite cross-referencing ...
  │
  ├─ X-Source-Mirror → receptor.primals.eco (Cross-Fleet scatter)
  ├─ X-Backup-Origin → complement.primals.eco (Compliance Audit scatter)
  └─ X-Federation-Peer → antibody.primals.eco (Inverse Correlation scatter)

Total scatter surface: 13 domains × 4 content types × infinite cross-links
Each domain serves unique deterministic scatter tied to the subdomain hash.
```

## Verification

All tested and confirmed live:

| Test | Result |
|------|--------|
| git.primals.eco no token → scatter + Link headers | ✅ |
| bloom.primals.eco no token → different scatter + cross-links | ✅ |
| antibody.primals.eco no token → inverse correlation scatter | ✅ |
| bloom.primals.eco WITH bearDog token → `data-theme="forgejo-auto"` (real) | ✅ |
| thymus.primals.eco WITH bearDog token → real Forgejo | ✅ |
| macrophage.primals.eco WITH bearDog token → real Forgejo | ✅ |
| Caddy validated + reloaded | ✅ |

## Fleet Status at Time of Deployment

| Metric | Value |
|--------|-------|
| Rate | 770 req/min (peak), 391/min (sustained) |
| Today's total | 23,488 |
| Burst ratio | 100% (<1s intervals) |
| Sec-Fetch evolved | 0.1% (gave up) |
| Accept-Language evolved | 0.1% (Gen 2) |
| Actions | 100% commit crawling |
| Response codes | 57% 404 / 43% 200 (all scatter) |
| Honeycomb discovery | 0 (pre-deployment — breadcrumbs just went live) |

## What sporeGate Can Build On

### 1. Scatter content cross-linking (skunky-ingest)

The Caddy-level Link headers are phase 1. For deeper maze integration, the scatter content HTML itself should embed links to honeycomb subdomains:

- Scatter repo pages should have "Related repositories" sections linking to `bloom.primals.eco/repo-name`
- Scatter commit pages should reference "federated commits" on `thymus.primals.eco`
- Scatter source files should include `import` statements referencing `macrophage.primals.eco` packages

This requires Rust changes in scatter_server.rs — the scatter content generation needs honeycomb awareness.

### 2. Per-subdomain scatter variation

Currently all 12 honeycomb subdomains route to the same scatter server. The `X-Honeycomb: true` header is set. Consider:

- Varying scatter content based on `Host` header — different repos per subdomain
- Using the subdomain name as the scatter hash seed — deterministic but unique per subdomain
- Different scatter "themes" per category (compliance, detection, inverse, chimeric)

### 3. Floating pointer rotation

The bearDog token currently works on all 13 domains simultaneously. Consider:

- Time-based pointer rotation — real Forgejo only available on the "current" honeycomb subdomain
- Session-scoped pointer — bearDog lineage proof includes the target subdomain
- Moving target — the active subdomain rotates on a schedule known only to authorized agents

### 4. bingoCube/nautilusShell integration

When bingoCube/nautilusShell primal tooling goes live, the honeycomb can become:

- A live topology map of fleet movement through the maze
- Visualization of which subdomains fleet discovers first
- Timing analysis of how fast fleet propagates through cross-links
- Evidence of systematic link-following behavior

## Key Material

Same bearDog token across all 13 domains:
- Master key: `membrane-passthrough-v1`
- Derived: `golgi-body-web-passthrough` (Gen 1)
- Token: `bd1-*`
- Receipts: `0924f427` (generate), `1ed60901` (derive)

## Caddyfile Changes

Two sections modified:

1. **git.primals.eco** (line ~284): Added `header Link`, `header X-Source-Mirror`, `header X-Backup-Origin`, `header X-Federation-Peer` after scatter reverse_proxy
2. **Honeycomb block** (line ~681): Added `@wg_mesh`, `@agent_passthrough` handlers before default scatter handler. Added cross-link headers (`header Link`, `header X-*`) inside default handler.

Backup: `/etc/membrane/Caddyfile.bak-honeycomb-1791395588`

---

*eastGate overwatch — honeycomb maze activated. Floating pointer deployed. 13 doors, 4 scatter types, infinite cross-links. Fleet about to discover the prism. sporeGate: wire it into skunky-ingest and bingoCube when ready.*

*Wave 165i, Oct 7, 2026*
