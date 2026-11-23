# K-Derm Convergence AAR — Wave 158 (Sep 27, 2026)

**Wave**: 158 | **Gate**: sporeGate | **Session**: Sep 27 morning
**Scope**: Outer membrane config convergence + sporePrint build fix

---

## What Was Done

### 1. sporePrint Build Permission Fix (golgiBody)

**Problem**: Zola `--force` build fails with `Permission denied (os error 13)`.
Post-receive hook runs as `git` user but `public/` was owned by `root:root`.
Multiple content files also root-owned from prior manual operations.

**Fix**: `chown -R git:git /opt/ecoPrimals/sporePrint/` — entire worktree.
Verified: `sudo -u git zola build --force` → 340 pages, 25 sections, Done in 52.3s.

**Root cause**: Zola `--force` deletes the entire `public/` directory before
rebuilding. Any root-owned file inside (e.g., `.well-known/aspe`) blocks
the delete. This recurred because root operations (manual debugging, chattr,
etc.) create root-owned artifacts that survive the next `chown`.

**Permanent fix pattern**: Post-receive hook should `chown -R git:git` the
worktree before `zola build`, not rely on prior ownership.

### 2. Caddyfile Version Control Sync

**Drift**: VC Caddyfile was 245 lines (18 vhosts), live was 327 lines (20 vhosts).

| Drift | VC (stale) | Live (correct) |
|-------|-----------|----------------|
| detroit.primals.eco | missing | present |
| gorilla/guerillagorilla.primals.eco | missing | present |
| live.primals.eco port | `:9900` | `:8190` |
| depot path | `/opt/ecoPrimals/depot/` | `/opt/ecoPrimals/plasmidBin/` |
| footprint port | `:8090` | `:3002` |
| basicauth syntax | `basicauth` (Caddy v1) | `basic_auth` (Caddy v2) |
| sporePrint handle blocks | no sitemap/robots explicit | explicit handles |

**Fix**: VC Caddyfile updated to match live. 98 insertions, 22 deletions.
Committed `11a987e` to plasmidBin, pushed to Forgejo.

### 3. OUTER_MEMBRANE_TOPOLOGY.md Update

Added detroit + gorilla routing entries. Marked resolved: sitemap 500,
content stale, public/ permissions, Caddyfile drift. Updated GSC state,
page counts, footer. Committed `2a02a0f` to wateringHole (rebased on
eastGate's HARDWARE.md + Pi 500s push).

---

## K-Derm Audit Findings

### Healthy

- 12 golgiBody services all green (Caddy, Forgejo, bearDog, songBird×2, squirrel, petalTongue, webhook, skunky-ingest, hbbs, hbbr, step-ca)
- 15 sporeGate primals all running since Sep 20 (7 days stable)
- WireGuard mesh: 3 peers FRESH (sporeGate, eastGate, northGate)
- All 4 sitemaps returning 200
- 5-arch plasmidBin depot: 17 .exe, 67 musl, all arches populated

### Stale/Offline

- 6 WG peers STALE (36-59 days): strandGate, graftGate, blueGate, ironGate, biomeGate, flockGate
- 2 WG peers never connected: southGate, westGate
- These are all House 2 (power rebalance pending) or physically offline

### Minor Config Issues Noted

- westGate dnsmasq entry still commented out (no LAN IP)
- southGate dnsmasq IP (192.168.4.148) may differ from manifest (192.168.4.149)
- grapheneGate/westGate alias on same WG IP (10.13.37.11) — likely rename
- northGate has WG entry but no LAN IP in dnsmasq

---

## Convergence State

```
Forgejo (git.primals.eco):
  plasmidBin  → 11a987e (Caddyfile sync)     ✅
  wateringHole → 2a02a0f (topology update)    ✅

Live Caddyfile ↔ VC Caddyfile: CONVERGED     ✅
OUTER_MEMBRANE_TOPOLOGY.md: CURRENT          ✅
sporePrint build: WORKING (340 pages)         ✅
All sitemaps: 200                             ✅
```

---

*K-Derm convergence complete. Outer membrane config is code again. sporePrint
builds clean. eastGate handling hardware + dev evolution. sporeGate refocused
on inner membrane tracks: NanoWire retirement, depot authority, golgiBody
intermediary health.*
