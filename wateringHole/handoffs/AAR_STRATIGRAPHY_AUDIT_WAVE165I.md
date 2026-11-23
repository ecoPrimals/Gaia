# Stratigraphy Audit: golgiBody Process & File Inventory

**Wave 165i — October 7, 2026, 20:27 ET**
**Purpose**: Full geological survey of what's running, what's Python jellystein, what's compiled Rust, what's shell glue, and what's ready to evolve.

---

## Process Taxonomy

### 🦀 Compiled Rust (Production Grade)

| Binary | Service | Size | Since | PID | Purpose |
|--------|---------|------|-------|-----|---------|
| `caddy` | caddy-tls | 46M | May 15 | 2854378 | TLS termination, routing, scatter proxy, honeycomb |
| `skunky-ingest` | skunky-ingest | 5.3M | Oct 7 | 2976038 | Caddy log tailer → skunkBat + scatter server + Caddy bridge |
| `skunkbat` | skunkbat | 3.4M | Oct 6 | 2834181 | Fleet thymus — reconnaissance & automated defense |
| `swarmvine` | swarmvine-membrane | 2.5M | Oct 7 | 2942875 | Epidemic gossip engine — mesh coordination |
| `squirrel` | squirrel-membrane | 8.6M | Aug 10 | 3514834 | AI coordination |
| `membrane` | membrane-webhook | 18M | Oct 7 | 2943146 | Webhook listener (CI-EVO-01) |
| `beardog` | beardog-membrane | — | Jul 27 | 2547656 | BTSP + secrets — genetic token auth |
| `nestgate` | nestgate-sporeprint | 8.5M | Jul 8 | 2017630 | CAS storage |
| `petaltongue` | membrane-petaltongue | 19M | Aug 12 | 4002770 | sporePrint web server |
| `forgejo` | forgejo | — | Oct 7 | 2982005 | Sovereign git forge |
| `step-ca` | step-ca | — | Jul 29 | 2606896 | SSH Certificate Authority |

**Total Rust surface**: 10 binaries, ~130M compiled, all systemd-managed.

### 🦀 Rust Source Inventory (Local)

| Workspace | Crate | Rust Lines | Deployed Binary |
|-----------|-------|------------|-----------------|
| **skunkBat** | skunky-ingest | **11,640** | skunky-ingest (5.3M) |
| skunkBat | skunk-bat-core | — | skunkbat (3.4M) |
| skunkBat | skunk-bat-server | — | (in skunkbat) |
| skunkBat | skunk-bat-integrations | — | (in skunkbat) |
| skunkBat (total) | — | **40,154** | — |
| **squirrel** | (all crates) | **187,980** | squirrel (8.6M) |
| **cellMembrane** | cellmembrane-types | 13,921 | — |
| cellMembrane | membrane-shadow | 58,375 | membrane (18M) |
| cellMembrane (total) | — | **75,237** | — |
| **petalTongue** | (all crates) | **17,291** | petaltongue (19M) |
| **swarmVine** | (all crates) | **7,537** | swarmvine (2.5M) |
| **bearDog** | — | **2,429** | beardog |
| **songBird** | — | **1,205** | (not deployed on golgiBody) |
| **nestGate** | — | 12 | nestgate (8.5M) |

**Total Rust source**: ~331,845 lines across all workspaces.
**Key convergence target**: skunky-ingest (11,640 lines) absorbs 1,921 lines of Python → ~13,561 Rust lines.

### 🐍 Python Jellystein — /opt/membrane/ (Evolve to Rust)

| Script | Lines | Running | Purpose | Evolution Target |
|--------|-------|---------|---------|-----------------|
| `bloom_live.py` | **745** | ✅ PID 2978413 | Epitope collision classifier, L2/L1 classification, dashboard output | **skunky-ingest** — should be a module in the Caddy log tailer |
| `entity_topology.py` | **534** | Imported by bloom_live | Entity topology graph generator, subnet/geo analysis | **skunky-ingest** — topology should be computed in the same pipeline |
| `epitope_bridge.py` | **83** | Cron (*/5 min) | Reads epitope map, rewrites Caddy FLEET_PRESSURE matchers | **skunky-ingest** — the bridge should be internal to the Caddy bridge |
| `investigation_export.py` | **180** | Manual | Export investigation data from bloom state | Can stay Python — offline tooling |

**Subtotal**: 1,542 lines. **bloom_live + entity_topology + epitope_bridge = 1,362 lines** that should converge into skunky-ingest.

### 🐍 Python Jellystein — /opt/ecoPrimals/bin/ (Signal & Fleet)

| Script | Lines | Running | Purpose | Evolution Target |
|--------|-------|---------|---------|-----------------|
| `gen-signal-data.py` | **559** | Cron (via refresh-signal-data.sh, */15 min) | Parses Caddy logs → signal-data.js for signal page | **skunky-ingest** — signal data should be computed in the log pipeline, not re-parsed from raw logs |
| `gsc-agent.py` | **253** | Manual | Google Search Console agent — sitemap submission, indexing health | Stay Python — external API tooling |
| `gsc-status.py` | **43** | Manual | GSC status check | Stay Python — external API tooling |
| `fleet-pressure.fossil.py` | **306** | 🪨 Fossil | Old fleet pressure script (superseded by bloom_live + skunky-ingest) | Already fossilized |

**Subtotal**: 1,161 lines. **gen-signal-data.py = 559 lines** that should converge into skunky-ingest.

### 🐍 Python Jellystein — /opt/ecoPrimals/clutch/api/ (Justice Graph)

| Script | Lines | Running | Purpose | Evolution Target |
|--------|-------|---------|---------|-----------------|
| `build-unified-graph.py` | **343** | Manual | Merges detroit + barry investigation graphs → graph.json | Stay Python — offline data tooling |
| `ingest.py` | **217** | Manual | Investigation submission ingestion | Stay Python — offline data tooling |

**Subtotal**: 560 lines. Both stay Python — investigation tooling, not runtime.

### 🐍 Total Python Inventory

| Category | Lines | Evolve to Rust | Stay Python |
|----------|-------|----------------|-------------|
| /opt/membrane/ | 1,542 | 1,362 | 180 |
| /opt/ecoPrimals/bin/ | 1,161 | 559 | 602 |
| /opt/ecoPrimals/clutch/ | 560 | 0 | 560 |
| **Total** | **3,263** | **1,921** | **1,342** |

**59% of Python should evolve to Rust (1,921 lines → skunky-ingest).**
**41% stays Python (offline tooling, external APIs, investigation graphs).**

### 🐚 Shell Glue (Minimize)

| Script | Lines | Running | Purpose | Evolution Target |
|--------|-------|---------|---------|-----------------|
| `braid-billboard.sh` | 13 | Cron (*/5 min) | Auto-braid billboard snapshots | Could stay shell or move into a provenance service |
| `refresh-signal-data.sh` | 25 | Cron (*/15 min) | Shells out to gen-signal-data.py | Eliminate when skunky-ingest writes signal data natively |
| `cascade-sense.sh` | 35 | Manual | Cascade sense — detects Forgejo state | Stay shell — diagnostics |
| `sovereign-ci-trigger.sh` | 47 | Manual | CI trigger for sovereign pipeline | Stay shell — CI glue |
| `ssh-hygiene.sh` | — | Manual | SSH key hygiene | Stay as-is |

**Total shell glue**: 120 lines across golgiBody. Minimal — good.

### 🪨 Fossils (Already Stopped)

Located in `/opt/membrane/fossils/`:
- `bloom_live_v2.py.fossil` — binary classifier (superseded by v4)
- `bloom_live_v3.py.fossil` — behavioral collision (superseded by v4)
- `entity_topology.pre-epitope.py` — pre-epitope version
- `epitope_bridge.sh.fossil` — first attempt (heredoc quoting issues)
- `feed-to-repo.fossil.sh` — old feed pipeline
- `forgejo-watchdog.fossil.sh` — old watchdog
- `membrane-inflammatory.fossil.sh` — old inflammatory response
- `plasmid-federation.fossil.sh` — old federation script
- `tower-shadow-benchmark.fossil.*` — old benchmark
- `skunky-backups/` — **13 old skunky-ingest binaries** (evolution trail)
- `wg0.conf.pre-wave166` — old WireGuard config

**Fossil disk**: ~52M (mostly old skunky-ingest binaries). Can be cleaned.

---

## Data Files

### Live Output (bloom_live writes)

| File | Size | Update | Purpose |
|------|------|--------|---------|
| `dashboard.json` | 24K | 10s | Full dashboard with epitope clusters, offenders, geography |
| `state.json` | 210B | 10s | Compact state: RPS, fleet/human IPs, epitope summary |
| `feed.txt` | 27K | Per-event | Rolling text feed of classified events |
| `epitope_caddy.json` | 1.4K | 10s | Epitope→IP map for Caddy bridge |
| `billboard.txt` | 32B | On update | Current billboard text |
| `topology.json` | 33K | Periodic | Entity topology graph |
| `investigation.json` | 2K | Manual | Investigation state |

### Provenance Chain

| Path | Entries | Purpose |
|------|---------|---------|
| `provenance/billboard/braid.jsonl` | 7 | Human billboard braid — content-hashed entries |
| `provenance/billboard/*.txt` | 5 | Billboard snapshots |
| `provenance/artisan/braid.jsonl` | 4 | Artisan reflection braid |
| `provenance/artisan/*.txt` | 4 | Artisan snapshots |

### Content Surfaces

| Surface | Size | Source | Served by |
|---------|------|--------|-----------|
| `signal.primals.eco` | 97K | Hand-rolled HTML | Caddy file_server |
| `thesis.primals.eco` | 36K | Hand-rolled HTML | Caddy file_server |
| `sporeprint.primals.eco` | ~15M | Zola build | petaltongue |
| `git.primals.eco` | — | Forgejo + scatter | Caddy → Forgejo/scatter |

---

## Evolution Roadmap

### Phase 1: Converge Python → skunky-ingest (Rust)

**bloom_live.py** (745 lines) is the biggest jellystein. It:
1. Tails Caddy access log (skunky-ingest already does this)
2. Classifies visitors into L2 classes (skunky-ingest already does fleet detection)
3. Computes epitope hashes (new capability)
4. Tracks behavioral state per IP (new capability)
5. Writes dashboard/state/feed files (skunky-ingest could do this)
6. Writes epitope_caddy.json (epitope_bridge.py reads this)

**Target**: All of bloom_live's classification should move into skunky-ingest as `--bloom-classifier` or `--epitope-mode` flags. The epitope bridge becomes internal — skunky-ingest already writes the FLEET_PRESSURE block, it just needs to group by epitope hash instead of timing.

**entity_topology.py** (534 lines) generates topology graphs. This should be a skunky-ingest output mode.

**epitope_bridge.py** (83 lines) disappears entirely when skunky-ingest does epitope-keyed grouping natively.

**gen-signal-data.py** (559 lines) re-parses the raw access log from scratch every 15 minutes to build signal page data. Wasteful — skunky-ingest already parses the log in real time. Signal data should be a side output of the existing pipeline, not a second parser.

**After convergence**: bloom_live.py, entity_topology.py, epitope_bridge.py, gen-signal-data.py, refresh-signal-data.sh, and fleet-pressure.fossil.py all collapse into skunky-ingest. **1,921 lines of Python → 0.**

### Phase 2: Signal Page → API-Driven

`signal.primals.eco` is 97K of hand-rolled HTML that pulls from `dashboard.json` via JS fetch + gen-signal-data.py output. This works but two different parsers read the same log.

**Target**: skunky-ingest writes signal data natively as part of its existing log pipeline. The signal page stays static HTML — it just fetches from the skunky-ingest output instead of a cron-generated file.

### Phase 3: Provenance → sweetGrass/loamSpine/rhizoCrypt

The braid files (billboard + artisan) are currently JSONL with sha256 content hashing. This is the minimum viable braid — it works but isn't running through the provenance trio.

**Target**: When sweetGrass is deployed, braids flow through the proper content-addressed pipeline with Merkle tree verification.

### Phase 4: Fossil Cleanup

- Delete old skunky-ingest backups (13 binaries, ~52M)
- Archive bloom_live v2/v3 fossils (already in fossils/)
- Clean `skunky-ingest.bak` and `swarmvine.bak` from /opt/membrane root

---

## Current System Health

| Metric | Value |
|--------|-------|
| Disk usage | /opt 574M, /var/log 103M |
| Memory | 686M/1.9G used (36%) |
| Processes | 10 Rust + 1 Python + 3 cron |
| Uptime | Since May 15 (golgiBody) |
| Fleet state | 15 organisms, 51 IPs hashed, 8 clusters |
| Human traffic | 79 IPs, 4 genuine, 62 agentic |
| RPS | 11.8 steady |

---

## Summary

**What's solid (Rust, keep)** — 10 binaries, ~130M compiled:
- skunky-ingest, skunkBat, swarmVine, bearDog, squirrel, Caddy, Forgejo, nestGate, petalTongue, step-ca, membrane

**What's jellystein (Python, evolve to Rust)** — 1,921 lines:
- bloom_live.py (745 lines) → skunky-ingest
- gen-signal-data.py (559 lines) → skunky-ingest
- entity_topology.py (534 lines) → skunky-ingest
- epitope_bridge.py (83 lines) → skunky-ingest

**What stays Python (offline/external)** — 1,342 lines:
- investigation_export.py (180 lines) — bloom state export
- gsc-agent.py (253 lines) + gsc-status.py (43 lines) — Google Search Console
- build-unified-graph.py (343 lines) + ingest.py (217 lines) — justice graph
- fleet-pressure.fossil.py (306 lines) — already fossilized

**What's glue (shell, minimize)** — 120 lines:
- braid-billboard.sh (13 lines) — keep for now
- refresh-signal-data.sh (25 lines) — eliminate when skunky-ingest writes signal data
- cascade-sense.sh, sovereign-ci-trigger.sh — keep as diagnostics/CI

**What's fossil (cleaned)** — 29M remaining (was 63M, cleaned 34M):
- 2 most recent skunky-ingest backups kept
- Pre-wave166 configs archived
- bloom_live v2/v3 fossils archived

**The convergence target**: skunky-ingest absorbs bloom_live + entity_topology + epitope_bridge + gen-signal-data. One Rust binary does log tailing, fleet detection, behavioral classification, epitope hashing, topology generation, signal data generation, Caddy bridge writing, and scatter server. **1,921 lines of Python → 0.** Three cron jobs (epitope_bridge, refresh-signal-data, bloom_live systemd) collapse into the existing skunky-ingest process.

## Remaining Convergence Work

### High Priority (reduce Python runtime surface)
1. **Absorb bloom_live epitope classification into skunky-ingest** — this is the critical path. bloom_live and skunky-ingest both tail the same log. Two processes parsing the same data stream is the definition of jellystein.
2. **Absorb epitope bridge into skunky-ingest** — skunky-ingest already writes FLEET_PRESSURE. It just needs to group by epitope hash. 83 lines → 0.
3. **Absorb signal data generation into skunky-ingest** — stop re-parsing the log every 15 min. Signal data should be a side output.

### Medium Priority (tighten)
4. **Consolidate content surfaces** — signal (hand-rolled HTML), thesis (hand-rolled HTML), sporePrint (Zola), clutch (Zola), detroit (Zola), barry (Zola), tuebor (Zola). The hand-rolled ones should eventually be Zola sites.
5. **Provenance pipeline to sweetGrass** — braid-billboard.sh → sweetGrass content-addressed storage.
6. **golgiLayer federation** — pending VPS creation (Hetzner, Vultr, OVH, Linode).

### Low Priority (clean)
7. **Archive remaining fossils** — fossils/ directory is clean but could be moved off-VPS.
8. **Consolidate /opt/ecoPrimals layout** — some orphaned dirs (springs/ empty, skunky-ingest copies in root).

---

*Wave 165i — October 7, 2026*
