# eastGate Computational Slack Pickup — Wave 163

**Date**: Oct 5, 2026 12:08 EDT | **From**: sporeGate inner membrane session
**Target**: eastGate overwatch (Ryzen 9 7950X, 64GB, 10G SFP+)
**Goal**: eastGate absorbs computational backpressure so sporeGate stays lean as inner membrane to golgi

---

## Why Now

sporeGate is running load 3.4 on 4 cores — not danger, but warm. The heat is Cursor + Zola builds (60s full CPU each). sporeGate's job is inner membrane: NAT/DNS/DHCP router, songbird federation hub, primal orchestration relay. It should NOT be the primary build host.

eastGate has **load 0.68 on 16 cores** and **47GB free RAM**. It's barely working. The 10G SFP+ backbone makes it the natural build and compute anchor for the cytoplasm.

---

## Computational Slack Items

### 1. Zola Builds → eastGate

sporePrint builds take 60s on sporeGate. eastGate can do them in <15s with 16 cores.

**Setup**: Clone sporePrint on eastGate, build there, rsync to golgi directly.
```bash
# On eastGate:
cd ~/Development/ecoPrimals/infra/sporePrint
git pull
zola build --force
rsync -avz --delete public/ golgi:/opt/ecoPrimals/sporePrint/public/
```

This removes the biggest CPU spike from sporeGate. sporeGate still commits and pushes to Forgejo — that's lightweight. eastGate does the heavy build + deploy.

### 2. Detroit Builds → eastGate

Same pattern — detroit Zola builds move to eastGate:
```bash
cd ~/Development/ecoPrimals/infra/detroit/site
zola build --output-dir public --force
rsync -avz --delete public/ golgi:/opt/ecoPrimals/detroit/public/
```

### 3. Signal Data Generation → eastGate (future)

Currently gen-signal-data.py runs on golgi via cron (every 15 min). golgi is a 2GB VPS — this Python process processes all Caddy logs including gzipped rotations. As log volume grows, this should move to eastGate:

- eastGate pulls access logs from golgi
- Runs gen-signal-data.py (CPU + memory headroom)
- Pushes signal-data.js back to golgi

**Not urgent** — golgi handles it fine now. But if golgi memory pressure appears, this is the first thing to offload.

### 4. Rust Compilation → eastGate Primary

All `cargo build --release --target x86_64-unknown-linux-musl` should happen on eastGate. sporeGate has 27GB RAM but only 4 cores — release builds are CPU-bound.

eastGate is already a depot builder (18 binaries synced to golgi this session). Formalize this:
- eastGate builds → eastGate depot → rsync to golgi depot
- sporeGate pulls binaries FROM depot, doesn't compile them

### 5. Songbird Federation — Fix and Hold

eastGate songbird is still broken (stale PID lock from Wave 161). Fix:
```bash
systemctl --user stop songbird-federation
rm -f ~/.local/share/songbird/songbird.pid ~/.songbird/songbird.pid
# Binary was updated from depot this session (25MB, fresh build)
systemctl --user start songbird-federation
curl http://127.0.0.1:7700/health
```

Once federating, eastGate becomes the second LAN federation peer → stronger gossip, capability routing through the 10G backbone.

---

## What sporeGate Keeps

sporeGate stays focused on inner membrane duties:

| Function | Why sporeGate |
|----------|--------------|
| NAT/DHCP/DNS (dnsmasq) | Router position, all LAN traffic flows through |
| Songbird federation hub | First hop from LAN to golgi WireGuard |
| Primal orchestration (17 services) | Inner membrane — IPC relay for cytoplasm |
| Git commits + pushes | Lightweight, no build needed |
| Cursor IDE | Where the human works |
| RustDesk relay | Outer membrane access to gates |

**sporeGate does NOT need to**: build Zola sites, compile Rust, process signal logs, or run heavy analysis. Those go to eastGate.

---

## What Changed This Session (Wave 163)

Things eastGate should know about:

1. **Lysogeny protocol ACTIVE** — all 8 public sites now serve scyBorg license headers on every response. `X-Lysogeny: active` on every HTTP response from golgi.

2. **Signal v3 deployed** — `gen-signal-data.py` now tracks ALL sites (not just detroit), builds cumulative historical data in `/opt/ecoPrimals/detroit/data/signal-history.json`, records 15-min snapshots. 5,467 pages tracked across 4 active sites.

3. **Forgejo bot filter active** — git.primals.eco has 6-layer Caddy bot filter. Bots get 403, humans pass through, git protocol (clone/fetch/push) always works.

4. **baseCamp 30 + 31 published** — Adversarial Receptor Evolution + The Lysogeny Protocol. 31 papers, 343 pages on sporePrint.

5. **sporeGate songbird binary updated** — fresh binary from eastGate depot (25MB, fixed riboCipher). Federation to golgi: OK.

6. **golgiBody depot synced** — 18 musl binaries from eastGate + fresh songbird. BLAKE3SUMS regenerated.

---

## Architecture

```
OUTER MEMBRANE — golgiBody (Caddy TLS, public internet, relay.primals.eco)
    ↕ WireGuard 10.13.37.0/24
INNER MEMBRANE — sporeGate (router, 2.5G RJ45, 17 primals, federation hub)
    ↕ LAN 192.168.4.0/22 (10G backbone via CRS310)
CYTOPLASM — eastGate (10G overwatch, BUILD AUTHORITY, compute anchor)
             westGate (data NAS, sleeping)
             ironGate (GPU compute, sleeping)
             strandGate (128-thread HPC, sleeping)
```

sporeGate is the plasma membrane. eastGate is the ribosome — where the RNA (Python/JS jelly) gets translated into proteins (running services) and where the DNA (Rust binaries) gets compiled. The inner membrane relays; the cytoplasm computes.
