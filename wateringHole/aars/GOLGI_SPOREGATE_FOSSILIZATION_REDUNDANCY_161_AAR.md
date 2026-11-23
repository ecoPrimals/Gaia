# AAR: golgiBody Fossilization + Redundancy Audit + Membrane Sync — Wave 161

**Date**: Oct 5, 2026 08:00–09:47 EDT | **Wave**: 161 | **Gates**: golgiBody, sporeGate
**From**: overwatch/agentic session
**Type**: After-Action Report — Infrastructure sweep, fossilization, redundancy quantification

---

## Summary

Full fossilization sweep of golgiBody (outer relay) and sporeGate (inner membrane).
golgiBody disk reduced from **65% → 49%** (freed 1.6GB on a 10GB droplet). sporeGate
stabilized: killed 1.4GB of zombie Cursor processes, vacuumed journal (990MB → 277MB),
persisted journal size limits. Redundancy audit quantified 6 evidence surfaces across
5 failure domains. Pen tested detroit.primals.eco. Synced GitHub mirror. Seeded
Wayback Machine. Fixed Server header leak. Enhanced /validate/ page with BLAKE3
verification instructions.

**Key architectural finding**: golgiBody hosts both the live site AND Forgejo on the
same VPS — one failure domain kills the 2 most important surfaces. Forgejo should
migrate to LAN (sporeGate or blueGate) with golgiBody becoming a reverse proxy.

---

## golgiBody Fossilization

### Disk: 65% → 49% (freed 1.6GB)

| Action | Freed | Notes |
|--------|-------|-------|
| apt cache clean | 81M | Standard maintenance |
| Caddy logs (83M → 12K) | 83M | Rotated, no data loss |
| Forgejo logs (101M → 4K) | 101M | Old log accumulation |
| btmp.1 | 33M | Failed login archive |
| Journal vacuum | 29M | Compressed old entries |
| plasmidBin unused targets | **600M** | Removed win, aarch64-apple, aarch64-musl, x86_64-gnu — only musl needed on golgi |
| venv-gsc (stale venv) | **163M** | GSC Python venv, unreferenced by any service or cron |
| detroit/worktree (.git) | 88M | Git worktree — build artifact, not runtime |
| infra/wateringHole clone | **236M** | Full repo clone on relay — source not needed at runtime |
| sporePrint .git + source | **200M** | Only public/ needed for serving |

### What remains (runtime only)

```
/opt/ecoPrimals/
  plasmidBin/     177M  (x86_64-musl depot only)
  detroit/         88M  (public/ + evidence/)
  sporePrint/      24M  (public/ only)
  guerillaGorilla/  1M  (public/)
```

### What should NOT be on golgiBody

| Heavy tenant | Size | Target |
|-------------|------|--------|
| Forgejo (full git forge) | **1.8G** | Migrate to LAN host, golgi becomes `reverse_proxy 10.13.37.x:3000` |
| plasmidBin (binary depot) | 177M | Acceptable for now; canonical depot should be LAN |

### Failed: Old kernel removal

Attempted to remove `linux-image-6.1.0-47-amd64` but it's the **running kernel**
(142 days uptime, never rebooted into -53). Needs a reboot to boot into newer kernel
before old one can be removed. ~150M reclaimable.

### Failed: Forgejo git gc --aggressive

`--aggressive` with `--window=250` OOM-killed on the 2GB droplet (beardog.git = 647M).
Killed Forgejo in the process (restarted automatically). Lightweight `git gc --prune=now`
ran but didn't save space — repos genuinely contain that much data. Not worth retrying
on this host.

---

## sporeGate Local Stabilization

### Root Cause: 12GB state.vscdb

Cursor's `~/.config/Cursor/User/globalStorage/state.vscdb` grew to **12GB** — a single
SQLite database storing 806,452 rows of chat/agent/checkpoint history:

| Prefix | Rows | Size |
|--------|------|------|
| agentKv | 368K | 5.0 GB |
| bubbleId | 416K | 4.9 GB |
| checkpointId | 1.5K | 1.6 GB |
| (misc) | 13K | 200 MB |

This is the nature of heavy agentic IDE use across multiple machines — a month of
conversations. Vacuum script written at `infra/scripts/vacuum-cursor-state.sh` for
periodic maintenance. Requires Cursor closed to run safely.

### Local cleanup

| Action | Freed |
|--------|-------|
| Journal vacuum (990M → 277M) | 745M disk |
| Cursor old logs (227M → 49M) | 178M disk |
| Kill Sep 26 zombie zygote | 1.4GB RAM |
| Journal size limit persisted (200M max) | Prevents regrowth |

---

## Redundancy Audit

### Evidence Surfaces (6 total)

| Surface | Host | Domain | Status |
|---------|------|--------|--------|
| detroit.primals.eco | golgiBody (DO NYC3) | A | 200 ✓ |
| git.primals.eco (Forgejo) | golgiBody (DO NYC3) | A | 200 ✓ |
| github.com/defendDetroit | GitHub (Microsoft) | B | 200 ✓ |
| sporeGate local clone | sporeGate (house1) | C | exists ✓ |
| web.archive.org | Internet Archive | D | seeded ✓ |
| Google Cache | Google | E | indexed ✓ |

### Failure Domains (5)

| Domain | What it kills | Survives | Probability |
|--------|-------------|----------|-------------|
| **A: golgiBody** | detroit site, Forgejo, sporePrint, depot, llms.txt | GitHub, local, Wayback | Medium |
| B: GitHub | Mirror only | Everything else | Low |
| C: sporeGate | Local clone, LAN services | Everything else | Low |
| D: DNS (primals.eco) | ALL *.primals.eco | GitHub, local | Very Low |
| E: TLS/ACME | TLS on all primals.eco | GitHub, local | Low |

### Key Finding: Domain A is overloaded

golgiBody hosts the live site AND Forgejo — the 2 most important surfaces share one
VPS. Migrating Forgejo to LAN (following the existing pattern for footprint, webb,
live, lab) would split domain A into two independent domains. This is the single
highest-value redundancy improvement.

### Redundancy Score

| Asset | Independent copies |
|-------|-------------------|
| Git history (signed) | 3 (Forgejo, GitHub, local) — 2 independent |
| HTML site (rendered) | 1 live + 1 cached (Wayback) |
| Evidence PDFs | 2 (served + source) |
| network-data.js | 3 (served, in repo, built locally) |
| BLAKE3 manifest | 3 (Forgejo, GitHub, local) |

---

## Pen Test Results

### Probe Rejection (Wave 160 scanner hardening)

All 13 vulnerability scanner probes returned **403** (blocked):
`/.env`, `/.git/config`, `/wp-admin/`, `/wp-login.php`, `/phpmyadmin/`,
`/xmlrpc.php`, `/.aws/credentials`, `/config.json`, `/index.php`,
`/wp-config.php`, `/test.php`, `/../etc/passwd`, `%00`

### Security Headers

| Header | Status |
|--------|--------|
| HSTS (63072000, includeSubDomains, preload) | ✓ |
| X-Content-Type-Options: nosniff | ✓ |
| X-Frame-Options: DENY | ✓ |
| Referrer-Policy: strict-origin-when-cross-origin | ✓ |
| Permissions-Policy (camera, mic, geo blocked) | ✓ |
| Server header hidden | ✓ (fixed this session) |
| No cookies | ✓ |
| No CORS headers | ✓ |
| HTTP methods locked to GET | ✓ (405 for POST/PUT/DELETE/PATCH/OPTIONS/TRACE) |
| Host header injection | ✓ (returns empty) |

---

## Membrane Sync

### Inner Membrane (WireGuard)

| Peer | IP | Status | Last handshake |
|------|-----|--------|---------------|
| sporeGate | 10.13.37.2 | **ALIVE** | seconds ago |
| (unnamed) | 10.13.37.5 | **ALIVE** | seconds ago |
| (unnamed) | 10.13.37.8 | **ALIVE** | seconds ago |
| flockGate | 10.13.37.7 | **DOWN** | 49 days |
| (unnamed) | 10.13.37.10 | stale | 44 days |
| (unnamed) | 10.13.37.12 | stale | 49 days |
| (unnamed) | 10.13.37.13 | stale | 49 days |
| (unnamed) | 10.13.37.3 | stale | 52 days |
| blueGate? | 10.13.37.6 | stale | 68 days |
| (unnamed) | 10.13.37.9 | never | — |
| (unnamed) | 10.13.37.11 | never | — |

### Outer Membrane (RustDesk)

- hbbs + hbbr both active, 142 days uptime
- RUSTDESK_MEMBRANE firewall chain: 10 rules, **zero rate-limit drops**
- 158K UDP heartbeats accepted, 279K TCP connections accepted
- Port 21114 REJECT rule: only 3 hits (scanners, not gates)
- RustDesk client active on sporeGate

### LAN Service Reachability (through golgi)

| Subdomain | Backend | Status |
|-----------|---------|--------|
| live.primals.eco | 10.13.37.2:8190 | **200** ✓ |
| nestgate.io | 10.13.37.2:8190 | **200** ✓ |
| lab.primals.eco | 10.13.37.2:7780 | **401** ✓ (auth required) |
| footprint.primals.eco | 10.13.37.7:3002 | **502** — .7 is down |
| webb.primals.eco | 10.13.37.7:8090 | **502** — .7 is down |

### Binary Version Sync

| Binary | golgi depot (Sep) | sporeGate local (Aug) | Match |
|--------|-------------------|----------------------|-------|
| membrane | 18M (Sep 26, e7e37e0) | 17M (Aug 17, 39f79d4) | **BEHIND** |
| songbird | 19M (Aug 14) | 25M (Aug 12) | **DIFFERENT** (size mismatch) |
| beardog | 8.8M (Aug 14) | 8.8M (Aug 12) | close |
| petaltongue | 24M (Aug 14) | 24M (Aug 12) | close |
| biomeos | 17M (Aug 16) | 17M (Aug 12) | close |

### Songbird Federation Issue

sporeGate songbird is sending **legacy riboCipher** (deprecated Wave 112, reject Wave 113)
to golgiBody. golgiBody songbird rejects with `invalid HTTP method parsed`. Federation
is broken — needs binary update on sporeGate.

---

## Fixes Applied This Session

1. **golgiBody disk** — 65% → 49% (1.6GB freed)
2. **GitHub mirror synced** — was 10 commits behind, now at HEAD
3. **Server header hidden** — `-Server` added to detroit Caddy block
4. **Verify page enhanced** — BLAKE3 instructions, three-surface independence table
5. **Wayback Machine seeded** — 14 of 15 key pages archived (302)
6. **skunky-ingest enabled** — was `--dry-run`, now live (emitting to skunkBat when LAN connects)
7. **Journal size limit persisted** — 200M max via /etc/systemd/journald.conf.d/
8. **Zombie processes killed** — Sep 26 Cursor zygote (1.4GB RAM freed)
9. **detroit worktree recreated** — webhook deploy pipeline restored after fossilization

---

## Remaining Work

### High Priority
- **Migrate Forgejo to LAN** — splits domain A, biggest redundancy gain
- **Update sporeGate binaries** — membrane + songbird behind golgi depot
- **Fix songbird federation** — riboCipher mismatch blocking mesh
- **Reroute footprint/webb** — Caddy → .2 (sporeGate) since .7 is down

### Medium Priority
- **Second DNS domain** — defenddetroit.org or similar for DNS-level independence
- **Auto-push GitHub mirror** — post-receive hook on Forgejo
- **golgiBody reboot** — boot into kernel -53, remove old -47 (150M)

### Low Priority
- **Wake stale WG peers** — .6, .10, .12, .13 (may be intentionally offline)
- **footprint-server** — running on sporeGate but not binding port, needs debug
- **Caddy log rotation** — 23M and growing, add roll_size to detroit block

---

## Architecture Note: Golgi as Thin Relay

golgiBody's intended role is a **Golgi apparatus** — it processes and routes, it does
not store. The membrane on golgi receives from the outside and packages for delivery
to the LAN. Current state is close but Forgejo (1.8G) is the remaining heavy tenant.

**Target architecture (per routing_config.toml)**:
- Static sites → VPS cache (thin, current build only)
- Git operations → gate (LAN via WireGuard)
- API calls → gate
- Large downloads → Songbird P2P
- Authenticated → gate via BTSP
- Public/cached → VPS local filesystem

Five subdomains already follow this pattern (reverse proxy to LAN):
footprint, webb, live, lab, nestgate.io. Forgejo should be the sixth.

---

## Traffic Snapshot (at time of audit)

- **detroit.primals.eco**: 235 requests, 10 unique subnets, 21 human page views
- **git.primals.eco**: 10,385 requests (Meta/Facebook: 3,606, Chrome: 6,727)
- **Wayback Machine**: actively crawling (20+ pages)
- **OpenAI**: crawled llms.txt (AI agent ingestion ready)
- **golgiBody health**: 49% disk, 800M/1.9G RAM, load 0.55

---

*Wave 161 — fossilization complete, redundancy quantified, membranes audited.*
