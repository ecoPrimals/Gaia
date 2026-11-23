# System Check AAR — Wave 157k+ (Sep 15, 2026)

**Date**: Sep 15, 2026 | **From**: sporeGate topology + golgiBody team  
**Scope**: Monthly system check — cascade health, disk, mesh, indexing  
**Prior session**: Aug 17, 2026

---

## Executive Summary

golgiBody cascade was **crash-looping for 3 weeks** (Aug 27 – Sep 15). Root cause: a stale `ecosystem_manifest.toml` checkout with `mobility = "portable"` (unknown variant in the deployed `membrane` binary). Cascade sense failed every 15 minutes (1,784 failures). This blocked all autonomous cleanup, depot refresh, and sporePrint rebuilds.

**Impact**: Disk crept from ~68% to 79%, no automatic sporePrint rebuilds, no depot updates from teams, no cascade health signals. The cell membrane on golgiBody was dead.

---

## Issues Found & Fixed

| # | Issue | Root Cause | Fix | Impact |
|---|-------|-----------|-----|--------|
| 1 | **Cascade crash-loop (3 weeks)** | `ecosystem_manifest.toml` stale checkout on golgi had `mobility = "portable"`, membrane binary (Aug 3) didn't have that variant | Reset `wateringHole` checkout to `origin/main`, updated membrane binary to depot version (a38c70d, Aug 14) | Cascade healthy, auto-sense running |
| 2 | **hbbs-membrane DOWN (1+ day)** | Binary deleted from `/opt/membrane/` (same pattern as caddy last month) | Downloaded fresh 1.1.14, installed, `chattr +i` | RustDesk rendezvous restored |
| 3 | **golgiBody disk 79%** | Uncapped journal (1GB), ghost binaries in Windows depot (161M), stale logs, 5% reserved blocks on VPS | Vacuum journal, cap at 100M, clean ghost binaries, setup logrotate, reduce reserved to 1% | 79% → 70% (3.0G free) |
| 4 | **Windows depot had 29 files (should be 16)** | 12 PE32+ binaries pushed WITHOUT `.exe` extension alongside the correct `.exe` builds | Removed 12 ghost binaries (161M freed) | Clean depot |
| 5 | **membrane binary 3-way split** | `/usr/local/bin/membrane` (Aug 3), `/opt/membrane/membrane` (Aug 9), depot (Aug 14) — cascade-sense used the oldest | Installed depot binary to `/usr/local/bin/membrane`, `chattr +i` | Correct membrane version running |
| 6 | **Zola build stale (1 month)** | Last build Aug 17. Cascade broken = no auto-rebuild | Forced Zola rebuild on golgi | Fresh sporePrint content served |
| 7 | **Critical binaries unprotected** | caddy, membrane, zola lacked immutable attribute | `chattr +i` on caddy, hbbs, hbbr, membrane, zola | Prevents future deletion |

## Drifted Primals Rebuilt

| Primal | New Commit | Generation |
|--------|-----------|-----------|
| toadstool | 9763b4da | 8405 |
| biomeos | af1dc9d3 | (rebuilt) |
| squirrel | 026f8d71 | (rebuilt) |
| petaltongue | a1a10f30 | (rebuilt) |

All pushed to golgiBody depot via `plasmid.push`.

## Google Search Console Status

**Full agentic control established:**
- `sc-domain:primals.eco` verified (DNS TXT), service account has `siteFullUser`
- GSC API operational (sitemap management, URL inspection, search analytics)
- GSC venv deployed: `/opt/ecoPrimals/venv-gsc/`
- Monitoring script: `/opt/ecoPrimals/bin/gsc-status.py`

**Indexing status (30-day):**
- Sitemap: 401 submitted, 0 indexed (domain migration in progress)
- 126 pages with impressions, 465 total impressions, 2 clicks
- Homepage: PASS (indexed, last crawl Sep 13)
- Content pages: "Crawled - currently not indexed" under `sporeprint.primals.eco` (Google still migrating from `primals.eco`)
- Sitemap resubmitted after Zola rebuild

**SEO is secondary to mesh stability** — will monitor weekly via `gsc-status.py`.

## Infrastructure Hardening

| Measure | Detail |
|---------|--------|
| Journal capped | `SystemMaxUse=100M`, `MaxFileSec=7day` in `/etc/systemd/journald.conf.d/size-limit.conf` |
| Caddy logrotate | `/etc/logrotate.d/caddy` — daily, 3 rotations, 20M max |
| Forgejo logrotate | `/etc/logrotate.d/forgejo` — daily, 3 rotations, 20M max |
| Reserved blocks | `tune2fs -m 1` (5% → 1% for VPS) — freed 330M |
| Binary immutability | `chattr +i` on caddy, hbbs, hbbr, membrane, zola |

## State After Fix

```
golgiBody (golgi):
  Disk:       70% (3.0G free, was 79%)
  Cascade:    HEALTHY (synced=1, failed=0)
  Services:   hbbs✓ hbbr✓ caddy✓ songbird✓ beardog✓ webhook✓ forgejo✓
  Depot:      15 verified, 0 hash mismatch
  Membrane:   v0.1.0 (a38c70d) — current with depot

sporeGate (local):
  Mesh:       7 peers, 7 reachable
  WireGuard:  Active, handshake 21s ago
  Disk:       23% (682G free)
  RustDesk:   hbbs=OK, hbbr=OK (relay restored)
```

## Lessons

1. **Cascade is the immune system.** When it dies, everything slowly degrades — disk fills, content goes stale, primals drift, binaries diverge. Fixing cascade was the single most impactful action.
2. **Chicken-and-egg**: A stale config prevented cascade from running, which prevented the config from being updated. Manual reset was the only fix.
3. **Binary immutability matters.** Three binaries vanished from disk over 2 months. `chattr +i` prevents recurrence regardless of root cause.
4. **VPS default reserved blocks (5%) waste 500M.** Reduced to 1% — still safe for root processes but recovered critical space.
5. **Depot push needs target validation.** The 12 ghost PE32+ binaries in the Windows dir (without `.exe` extension) indicate a push script bug. Worth investigating in the `plasmid.push` code.

## Remaining

- **blueGate**: Offline (rack move). Depot rebuild when reachable.
- **southGate**: SSH config ready. Enrollment when back online.
- **beardog.git**: 647M — legitimate pack size (git gc didn't help). Consider shallow clones or archive branches.
- **Google indexing**: Domain migration in progress. Monitor weekly.
- **Ghost binary root cause**: `plasmid.push` may have a target-extension bug. Investigate in `depot_sync.rs`.
