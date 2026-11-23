# Sub-Generation Handoff — Entity Topology + Remote Monitoring

**Wave**: 165h | **Date**: Oct 7, 2026 09:41 EDT | **From**: sporeGate inner membrane

---

## Summary

This session evolved the membrane's observational capacity from raw bloom monitoring into a full entity topology system that classifies every observed system by behavioral fingerprint, detects sub-teams within fleets, and serves the results as live public JSON feeds. A remote monitoring tool allows any gate (northGate, eastGate, blueGate) to observe the membrane without SSH access to sporeGate or golgiBody.

**sporeGate remains the dedicated inner membrane** — development, Rust compilation, git operations, SSH key holder. Monitoring is now decoupled to public HTTPS endpoints.

---

## What Was Built

### 1. Entity Classifier (Rust)

**File**: `skunkBat/crates/skunky-ingest/src/entity_classifier.rs` (~800 lines)

Classifies every observed entity from behavioral invariants:

| Entity | IPs | Honest | Key Signal |
|--------|-----|--------|------------|
| Meta Platforms (Fleet) | 56 | ✗ | 33% blame (author tracking), Chrome/145, FB-BLOCK |
| Anthropic (ClaudeBot) | 1 | ✓ | 11 RPS, scatter-only targets, honest UA |
| Stealth Scrapers | 8 | ✗ | Chrome/89-123, scanner probes |
| Human (Browser) | 20 | ✓ | Sec-Fetch-Mode present |
| Meta (Facebook Bot) | 4 | ✓ | Link preview system |
| + 4 others | — | — | Huawei, SEO, vuln scanner, unknown |

Sub-system detection within entities:
- **Chrome Deployment Pipeline** — version spread reveals deployment cadence
- **OS Impersonation Pool** — 3 OS variants from 56 IPs = pool of 9 UA strings
- **Author Attribution System** — 33% `/blame/` requests = mapping who wrote each line
- **Shared Configuration** — identical Accept-Encoding across all fleet IPs

### 2. Scatter Server Absorption (Rust)

Three patterns absorbed from Python/Caddyfile into `scatter_server.rs`:

| Pattern | Source | Now In |
|---------|--------|--------|
| Blackwall OG cards | 9 inline HTML blocks in Caddyfile | `blackwall_og_card()` — UA detection + per-domain OG metadata |
| `/live` endpoint | Caddy file_server route + bloom_live.py | Scatter route reading feed.txt |
| `/dashboard.json` | Caddy file_server route | Scatter route reading dashboard.json |
| `/topology.json` | (new) | Scatter route reading topology.json |

### 3. Script → Rust Evolution

| Script | Rust Module | Status |
|--------|------------|--------|
| `plasmid-federation.sh` + embedded Python | `federation.rs` — async reqwest, type-safe merge | ✅ Compiled |
| `membrane-inflammatory.sh` | `inflammatory.rs` — tokio heartbeat watchdog | ✅ Compiled |
| `forgejo-watchdog.sh` | Already in `lysogeny.rs` | ✅ Exists |

### 4. Structural Refactor

- **`lib.rs` extracted** — all 17 modules now in `lib.rs`, `main.rs` uses `use skunky_ingest::{..}`
- `reqwest` (rustls-tls) + `tokio/process` added to workspace
- Binary: **2.7MB musl static** (unchanged)

### 5. Hetzner Layer — Fully Operational

| Component | Status |
|-----------|--------|
| DNS: `layer2.primals.eco` → `2.28.141.35` | ✅ Live |
| TLS: Let's Encrypt via Caddy | ✅ Live |
| Scatter server: `127.0.0.1:9753` | ✅ Active |
| Plasmid feed: `/plasmid` | ✅ Serving |
| Federation: 2-layer merge (NYC + Falkenstein) | ✅ Working |

### 6. Cleanup

- **31 throwaway Python scripts** removed from golgiBody `/tmp/`
- **3 bash scripts** fossilized as `.fossil.sh` (safety net until Rust verified)

---

## Remote Monitoring Tool

**File**: `infra/membrane/tools/membrane-monitor.sh`

Self-contained bash script — runs from **any gate** with curl + python3. No SSH required. No access to sporeGate needed. All data from public HTTPS endpoints.

```bash
# Full dashboard
./membrane-monitor.sh

# Specific views
./membrane-monitor.sh bloom        # bloom status, RPS, fleet IPs, humans
./membrane-monitor.sh topology     # entity classification + sub-systems
./membrane-monitor.sh fleet        # top offenders, targeting patterns
./membrane-monitor.sh layers       # golgiBody + Hetzner + federation health
./membrane-monitor.sh plasmid      # conserved plasmid feed details
./membrane-monitor.sh live         # last 15 lines of live terminal feed
./membrane-monitor.sh watch        # continuous 10s auto-refresh
```

### Deployment to gates

```bash
# From any gate with access to the repo:
scp infra/membrane/tools/membrane-monitor.sh <gate>:~/bin/
# Or curl from Forgejo:
curl -sL https://git.primals.eco/ecoPrimals/wateringHole/raw/branch/main/tools/membrane-monitor.sh -o ~/bin/membrane-monitor.sh
chmod +x ~/bin/membrane-monitor.sh
```

---

## Public API Endpoints

All endpoints return JSON (except `/live` which returns text). No authentication required. CORS-enabled.

| Endpoint | Refresh | Description |
|----------|---------|-------------|
| `signal.primals.eco/dashboard.json` | ~4s | Live fleet dashboard (RPS, offenders, subnets, timing) |
| `signal.primals.eco/topology.json` | ~30s | Entity topology (entity profiles, sub-systems, comparative) |
| `signal.primals.eco/live` | ~2s | Plain text terminal feed |
| `signal.primals.eco/feed/conserved-plasmid.json` | ~5min | Federated threat intelligence (CC-BY-SA-4.0) |
| `layer2.primals.eco/metrics` | live | Hetzner layer scatter metrics |
| `layer2.primals.eco/plasmid` | live | Hetzner layer plasmid feed |

---

## Key Finding: Meta Blame Targeting

**32.9% of Meta fleet requests are `/blame/` paths.**

This is not source code collection. This is **authorship mapping** — tracking who wrote each line of every file. Blame analysis targets:

| Repository | Blame Requests |
|-----------|---------------|
| toadStool | 174 |
| songBird | 143 |
| bearDog | 117 |
| wateringHole | 89 |
| primalSpring | 87 |
| biomeOS | 78 |

They are building an author attribution graph of the entire codebase.

---

## Architecture After This Session

```
sporeGate (inner membrane)
  └── Development, Rust compilation, git push
  └── Does NOT need to monitor — that's decoupled

Any gate (northGate, eastGate, blueGate)
  └── membrane-monitor.sh → public HTTPS endpoints
  └── Full observability without SSH

golgiBody (peptidoglycan)
  └── skunky-ingest 0.2.18 (scatter + bloom + topology)
  └── bloom_live.py + entity_topology.py (dashboard + topology feeds)
  └── Caddy: routes for /live, /dashboard.json, /topology.json

golgiLayerHetzner (outer membrane, DE)
  └── skunky-ingest 0.2.18 (scatter server, layer2)
  └── Federated into plasmid via golgiBody
```

---

## Pending

- **Wire `federation.rs` into `main.rs`** — spawn as periodic tokio task, retire crontab
- **Wire `inflammatory.rs` into `main.rs`** — spawn as background task, retire systemd timer
- **Caddyfile cleanup** — remove 9 blackwall HTML blocks (scatter handles it now)
- **Future layers** — Vultr (SG), OVH (FR), Linode (Mumbai/Tokyo)
- **Topology alerting** — detect new entities, entity state changes, new sub-systems

---

*— sporeGate inner membrane, Wave 165h*
