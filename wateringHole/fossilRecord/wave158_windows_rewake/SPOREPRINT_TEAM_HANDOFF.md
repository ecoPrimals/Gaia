# sporePrint Team Handoff — Wave 157k

**Date**: Aug 18, 2026 | **Wave**: 157k | **From**: sporeGate (foreman)
**To**: sporeGate sporePrint team
**Status**: P1 fixes DEPLOYED. Content refresh + NUCLEUS evolution NEXT.

---

## What's Already Done (sporeGate ops — Aug 17)

### sitemap.xml 500 — FIXED

The `sitemap.xml` was returning 500 intermittently because Caddy's sporePrint vhost used a
SPA-style `try_files` fallback that served `index.html` as XML when the file was missing:

```
handle {
    try_files {path} {path}/index.html /index.html   ← catches everything
}
```

**Fix deployed**: Explicit `handle` blocks for static discovery files **before** the SPA
fallback. These now match first and serve the correct file with correct content-type:

```
handle /sitemap.xml { file_server }
handle /robots.txt  { file_server }
handle /llms*.txt   { file_server }
handle /identity.json { file_server }
handle { try_files {path} {path}/index.html /index.html; file_server }
```

Caddy reloaded via admin API, then binary restored (was deleted from disk) and service
restarted clean with v2.11.4. All routes verified 200.

### Dual Checkout Path — RESOLVED

There is no `/opt/ecoPrimals/infra/sporePrint/` on golgiBody — confirmed. The single
checkout at `/opt/ecoPrimals/sporePrint/` is the canonical location. The confusion was from
the repo path `infra/sporePrint` in the local dev tree vs the golgi deploy path.

### Content Staleness — FIXED

sporePrint was stuck at Wave 157d (`a0d5c0f`). Updated to Wave 157k+ (`1949d347`) and
rebuilt Zola: **338 pages + 25 sections**. Two `_index.md` files had `date` fields that
Zola 0.19 rejects in section front matter — fix committed to Forgejo (`dd9f9647`).

Post-receive hook `50-zola-publish` was already wired in Forgejo and will auto-rebuild
on future pushes.

### Caddy Binary — RESTORED

`/opt/membrane/caddy` had been deleted from disk (process was running from memory for
3 weeks). Downloaded fresh v2.11.4, restarted service cleanly.

---

## What Needs Doing (sporePrint team)

### 1. Update Homepage Stats (P1)

Current site still shows stale counts from Wave 155m era. Update to reflect reality:

| Metric | Old Value | Current Value |
|--------|-----------|---------------|
| Tests | ~135K | **160K+** |
| Gates | 11 | **12** (biomeGate ONLINE) |
| NUCLEUS | 5 | **6** (graftGate FULL NUCLEUS) |
| QCD configs | — | **45** (SU(3) 32⁴ production COMPLETE) |
| Cross-GPU delta | — | **0.19%** (RTX 3090 vs RX 6950 XT) |
| MILC delta | — | **3×10⁻⁹** (plaquette agreement) |
| Primals | 15 | **16** (bonsai-bt ingesting) |
| Braids | — | **2,630** (100% verified, westGate estate) |
| Fossilized | — | **228 files / 1,514 records** |
| Depot targets | 3 | **4** (x86_64, aarch64, darwin, windows) |

Key areas: homepage, architecture pages, data catalog, pseudoSpore gallery.

### 2. Get QCD Data + Proofs Visible (P1)

strandGate has banked production data that should be on the site:

- **45 SU(3) 32⁴ configurations** — full production campaign
- **Cross-GPU reproducibility**: RTX 3090 vs RX 6950 XT, Δ = 0.19%
- **MILC agreement**: plaquette values match published MILC results to 3×10⁻⁹
- **K80 VBIOS decoded** — vendor PROM table extracted via sysfs (no nvidia-smi)
- **pseudoSpore bundles**: downloadable data with full sweetGrass provenance braids

Content lives in:
- `content/pseudospore/hotspring-qcd-sun.md` (main page)
- `content/pseudospore/hotspring-qcd-sun-audit.md` (computation audit)
- `content/pseudospore/hotspring-qcd-sun-paper.md` (arXiv draft)
- `content/lab/gpu-compute-live.md` (GPU compute evidence)

Verify these pages have current data. Add plaquette comparison table if missing.

### 3. NUCLEUS-Served Live Surface (P2 — Architecture)

The long-term goal: stats should never go stale again. Phase plan from
`specs/OUTER_MEMBRANE_TOPOLOGY.md`:

**Phase 0 (NOW)**: Static Zola site is current, sitemap works, Google can crawl.

**Phase 1**: Add live data endpoints via petalTongue.
- Gate status, test counts, depot versions served by petalTongue `:8190`
- Caddy proxies new routes from `sporeprint.primals.eco/live/*` to sporeGate
- Same pattern as nestgate.io Phase 2+3

**Phase 2**: cellMembrane data pipeline.
- Validation counts, spring results, provenance chain stats pushed to petalTongue
- QCD data (45 configs, plaquette values) served live
- CAS links for references and datasets

**Phase 3**: Semantic layer.
- Structured data for external validators (translate.js — Validation Class V)
- Machine-readable science data, JSON-LD enrichment
- `membrane seo.*` commands for Google Search Console automation

### 4. Zola Version (P3)

Currently running Zola **0.19.2** on golgiBody. Latest is 0.22.x. The `date` field issue
in `_index.md` may work in newer versions. Consider upgrading, but test locally first —
Zola template syntax changes between major versions.

---

## File Index

| What | Where |
|------|-------|
| Live site | `sporeprint.primals.eco` |
| Git repo | `git.primals.eco/ecoPrimals/sporePrint` |
| Local checkout | `/home/sporegate/Development/ecoPrimals/infra/sporePrint` |
| golgi deploy | `/opt/ecoPrimals/sporePrint/` (single checkout, auto-build on push) |
| Caddy config | `/etc/membrane/Caddyfile` on golgiBody |
| Post-receive hook | `sporeprint.git/hooks/post-receive.d/50-zola-publish` |
| Outer membrane spec | `wateringHole/specs/OUTER_MEMBRANE_TOPOLOGY.md` |
| Phase plan | `sporePrint/specs/BUILD_DEPLOY_PIPELINE.md` |
| GSC credentials | `/opt/ecoPrimals/credentials/gsc-service-account.json` on golgi |

---

## golgiBody Notes

- **Disk**: 68% used (3.1 GB free) — monitor on large Zola rebuilds
- **Caddy**: v2.11.4, restored from download (was deleted from disk)
- **Zola**: 0.19.2 (not apt-managed, standalone binary)
- **Auto-build**: Forgejo post-receive hook triggers `git reset --hard && zola build --force`

---

*sporePrint team: P1 infra is fixed. Content refresh is the priority — update stats to
160K+ tests / 12 gates / 45 QCD configs / 0.19% cross-GPU, get the science data visible.
Then start Phase 1 of the NUCLEUS live surface so we stop hand-updating numbers.*
