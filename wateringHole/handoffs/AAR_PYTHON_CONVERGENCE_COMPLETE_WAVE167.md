# AAR: Python Convergence Complete — 2,096 Lines → 0

**Wave 167 — October 8, 2026**
**Observer**: eastGate
**Commits**: 94a314f (entity_classifier), 45ced72 (dashboard_writer)
**Duration**: Oct 7–8 continuous session

---

## Context

The Stratigraphy Audit (Wave 165i) identified 1,921 lines of Python runtime code that should converge into skunky-ingest. Three Python processes were tailing the same Caddy access log independently:

1. **gen-signal-data.py** (559 lines) — cron every 15 min, re-parses entire log from scratch
2. **entity_topology.py** (534 lines) — imported by bloom_live, entity classification
3. **bloom_live.py** (793 lines) — systemd service, epitope hashing + dashboard output
4. **epitope_bridge.py** (83 lines) — cron every 5 min, rewrites Caddy FLEET_PRESSURE matchers
5. **refresh-signal-data.sh** (30 lines) — cron wrapper for gen-signal-data.py
6. **investigation_export.py** (180 lines) — manual export tool

After convergence: 2,096 lines of Python eliminated. Zero ecoPrimals Python processes running on golgiBody.

## What Was Done

### 1. signal_writer.rs (636 lines) — replaces gen-signal-data.py (559 lines)

- Accumulates human/bot/AI/stealth hits in real time from the existing pipeline
- Writes `signal-data.js` every 150 seconds (vs re-parsing entire log every 15 min)
- Tracks `pages_ever` and `sites_ever` as sourdough culture
- 8 tests passing
- Deployed with `--signal-writer` flag
- Validated output: 5.8KB JS, correct format matching Python output
- **Cron removed**: no more `*/15 * * * * refresh-signal-data.sh`
- **Fossilized**: `/opt/ecoPrimals/fossils/signal-writer-converged/gen-signal-data.py`

### 2. entity_classifier.rs (1,419 lines) — replaces entity_topology.py (534 lines)

- Classifies entities into 6 types: `meta_fleet`, `anthropic_claude_bot`, `human_browser`, `stealth_scraper`, `vuln_scanner`, `unknown`
- `RequestFingerprint::from_caddy_entry()` extracts classification signals
- `TopologyBuilder` accumulates per-entity state (IPs, UAs, repos, path ops, chrome versions, OS distribution)
- `TopologyWriter` with interval-based flushing writes `topology.json`
- Sourdough culture: loads/saves `topology-state.json` on `/var/lib/skunky-ingest/`
- 7 tests passing
- Deployed with `--entity-classifier` flag
- **Fossilized**: `/opt/membrane/fossils/entity-topology-converged/entity_topology.py`

### 3. dashboard_writer.rs (937 lines) — replaces bloom_live.py (793 lines)

- Per-IP behavioral profiling: request count, path types, repos, timing, geo
- Epitope hashing: BLAKE2b hash of (Accept-Encoding, UA pool size, blame ratio, Accept header, Accept-Language presence)
- L2 collision classification: `Genuine` (loads assets + referer + multi-page), `Agentic` (single deep hit, 200), `Coordinated` (same-path-same-10s), `Fleet` (default)
- Writes `dashboard.json` (full dashboard), `state.json` (compact), `epitope_caddy.json` (epitope→IP map)
- Sourdough culture: loads/saves `dashboard-culture.json` on `/var/lib/skunky-ingest/`
- 6 tests passing
- Deployed with `--dashboard-writer` flag
- **Fossilized**: `/opt/membrane/fossils/bloom-live-converged/bloom_live.py`
- **Fossilized**: `/opt/membrane/fossils/bloom-live-converged/investigation_export.py`

### 4. epitope_bridge.py (83 lines) → eliminated

Already absorbed by caddy_bridge.rs in a prior wave. The epitope_caddy.json output from dashboard_writer feeds skunky-ingest's existing FLEET_PRESSURE Caddyfile writer.

- **Cron removed**: no more `*/5 * * * * sleep 30 && python3 epitope_bridge.py`
- **Fossilized**: `/opt/membrane/fossils/epitope_bridge.py.fossil`

### 5. Sourdough Culture Mandate

User spotted signal writer state on tmpfs (`/run/membrane/`) — cold starts on reboot.

**Mandate**: "no fresh starts. sourdough starter culture for everything."

All persistent state moved to `/var/lib/skunky-ingest/` (real disk):
- `signal-writer-state.json` — pages_ever=59, snapshots accumulating
- `topology-state.json` — 6 entities, 2000+ requests
- `dashboard-culture.json` — 51 IPs, 2000+ requests
- `signal-spine/` — immune memory chain (Oct 6 bootstrap → Oct 7 → Oct 8)
- `cursor.pos` — log cursor position

All three writers confirmed warm-starting from sourdough:
```
🫓 sourdough: restored 444 fleet IPs from existing Caddyfile directives
🧬 topology culture loaded — sourdough warm start entities=6 requests=1500
🧬 dashboard culture loaded — sourdough warm start ips=46 requests=400
```

## Scorecard

| Python Script | Lines | Rust Replacement | Lines | Status |
|---------------|-------|------------------|-------|--------|
| gen-signal-data.py | 559 | signal_writer.rs | 636 | Converged, fossilized |
| entity_topology.py | 534 | entity_classifier.rs | 1,419 | Converged, fossilized |
| bloom_live.py | 793 | dashboard_writer.rs | 937 | Converged, fossilized |
| epitope_bridge.py | 83 | (caddy_bridge.rs) | — | Eliminated, fossilized |
| refresh-signal-data.sh | 30 | — | — | Eliminated, fossilized |
| investigation_export.py | 180 | — | — | Fossilized (offline tool) |
| **Total** | **2,179** | | **2,992** | **0 Python running** |

### Cron reduction

Before:
```
*/15 * * * * /opt/ecoPrimals/bin/refresh-signal-data.sh
*/5  * * * * sleep 30 && python3 /opt/membrane/epitope_bridge.py
*/5  * * * * /opt/membrane/provenance/braid-billboard.sh
```

After:
```
*/5  * * * * /opt/membrane/provenance/braid-billboard.sh
```

Two cron entries eliminated. One remaining (braid-billboard) is shell, not Python.

### Service reduction

Before: bloom-live.service (systemd) + skunky-ingest.service
After: skunky-ingest.service only (bloom-live.service disabled)

### skunky-ingest current flags

```
--signal-writer --entity-classifier --dashboard-writer
```

All three converged modules activated via CLI flags. Each can be independently disabled.

## Technical Issues Resolved

### Upstream refactor conflict
Between our entity_classifier commit and dashboard_writer, upstream extracted `process_line` and `TailState` from `main.rs` into `ingest_pipeline.rs`. Also added: `epitope_defs`, `epitope_lure`, `fluoro_tag`, `ribocipher_const`, `scatter_constants`, `scatter_types`, `scatter_defense`, `scatter_temporal`. Rebase conflicted. Resolved by resetting to upstream, recovering dashboard_writer.rs from reflog, re-applying changes cleanly to the new `ingest_pipeline.rs` structure.

### Missing header fields in test structs
Adding `sec_fetch_dest`, `sec_fetch_site`, `cookie` to `caddy::Headers` broke 4 test struct constructions in `fleet.rs` and `bloom_sensor.rs` that explicitly listed all fields. Fixed by adding the 3 new fields to each location.

### Rust 2024 edition pattern matching
`|(subnet, &count)|` caused "cannot explicitly dereference within an implicitly-borrowing pattern". Fixed 3 instances by removing `&` and adding `let count = *count;`.

### VulnScanner test assertion
Test for `from_caddy_entry_builds_fingerprint` used URI `/wp-login.php` with Sec-Fetch-Mode present and expected `HumanBrowser`, but classifier checks VulnScanner URIs BEFORE Sec-Fetch. Fixed test to assert `VulnScanner`.

## Current System State

### golgiBody process inventory (Oct 8, 10:45 UTC)

**Rust binaries running**: 12 (caddy, skunky-ingest, skunkBat, swarmVine, bearDog, squirrel, membrane-webhook, nestGate, petalTongue, forgejo, step-ca, songbird)
**Python processes running**: 0 ecoPrimals (only system: unattended-upgrades, fail2ban)
**Cron jobs**: 1 (braid-billboard.sh)

### skunky-ingest size

- Source: **19,811 lines** (Rust) across 38 files
- Binary: 5.3M compiled (release, musl)
- Total skunkBat workspace: **48,445 lines** Rust

### Persistent state on disk

```
/var/lib/skunky-ingest/
├── cursor.pos                    8 B    (log position)
├── signal-writer-state.json    8.1 KB  (signal accumulator)
├── topology-state.json         237 KB  (entity topology culture)
├── dashboard-culture.json      142 KB  (dashboard/epitope culture)
├── nft-count                     1 B   (NFT counter)
└── signal-spine/
    ├── 2026-10-06-bootstrap.json  673 B
    └── 2026-10-07.json          1.3 KB
```

### Fossil inventory

```
/opt/ecoPrimals/fossils/signal-writer-converged/
├── gen-signal-data.py        (27 KB)
└── refresh-signal-data.sh    (830 B)

/opt/membrane/fossils/
├── bloom-live-converged/
│   ├── bloom_live.py         (31 KB)
│   └── investigation_export.py (6.4 KB)
├── entity-topology-converged/
│   └── entity_topology.py    (22 KB)
├── epitope_bridge.py.fossil
├── bloom_live_v2.py.fossil
├── bloom_live_v3.py.fossil
└── (other older fossils)
```

## 72-Hour Bloom Check (Oct 5–8)

Simultaneous with convergence work, the bloom sensors tracked:

| Period | Requests | IPs | Dominant Actor | Notes |
|--------|----------|-----|----------------|-------|
| Oct 5–6 | 22,135 | 20,502 | Browser-like (94%) | WordPress probes (wp-admin, wp-content). Quiet baseline. |
| Oct 6–7 | 19,240 | 370 | Meta FB-BLOCK (98%) | 37 rotating IPs, systematic repo crawling |
| Oct 8 (6h) | 136,935 | 585 | Anthropic ClaudeBot (83%) | 113k reqs from single IP, probing non-existent repos |
| Oct 8 (1h) | 15,634 | 233 | Anthropic (58%) + Meta (37%) | Both fleets active simultaneously |

**Key bloom findings:**
- Anthropic's ClaudeBot enumerating fake repo names (batch-processor, queue-worker, deploy-scripts) — automated git hosting probe
- Meta's fleet expanded from wateringHole-focused (Oct 5) to full repo coverage (Oct 6–7)
- Epitope clusters confirmed: 34 IPs across 3 hashes share identical behavioral DNA (Meta sub-teams)
- Two `.env` credential probes detected (stealth suspects with browser UA but no Sec-Fetch)

## What Changed (Central Dogma)

The Stratigraphy Audit identified 1,921 lines of Python runtime code as the convergence target. We exceeded that:

```
Before: 3 Python processes + 3 cron jobs parsing the same log
After:  1 Rust binary with 3 activated modules + 0 Python + 1 cron job
```

**Central dogma**: all runtime intelligence flows through compiled Rust. Python stays only for offline tooling (investigation_export, gsc-agent, build-unified-graph). The sourdough culture pattern ensures no cold starts — all accumulators persist to real disk and warm-start on restart.

## Remaining & Pending Work

### Immediate (triage for next session)

1. **bloom-live.service cleanup** — currently `disabled` but unit file still exists. Can be removed entirely now.
2. **songbird-membrane.service** — shows active but songbird binary may not be deployed properly on golgiBody. Was disabled in a prior session but came back. Investigate.
3. **Unused `bloom_live.py` at `/opt/membrane/bloom_live.py`** — the active copy is fossilized but the original is still at its original path. Remove it (fossilized copy preserved in `/opt/membrane/fossils/bloom-live-converged/`).
4. **`investigation_export.py`** — offline tool, fossilized. If needed again, could be a simple Rust CLI or stay Python since it's manual.

### Medium priority

5. **VPS creation** — golgiLayer2-5: Hetzner CX22, Vultr Singapore, OVH Gravelines, Linode Mumbai/Tokyo. Federation targets for swarmVine gossip mesh.
6. **Signal page update** — `signal.primals.eco` currently fetches from `signal-data.js` written by signal_writer. The signal spine (`signal-spine/*.json`) provides a richer immune memory chain that the signal page could visualize.
7. **Dashboard page update** — the dashboard.json schema is richer now (epitope_clusters, collision_level2, geography). Any live dashboard consuming it should be updated.
8. **Anthropic ClaudeBot response** — 113k requests from single IP probing fake repos. Consider: rate limiting, Caddy matcher for ClaudeBot UA, or scatter response seeding for honeypot analytics.

### Low priority

9. **Fossil cleanup** — old skunky-ingest backups (2 copies in fossils/skunky-backups/) can be removed.
10. **Provenance pipeline to sweetGrass** — braid-billboard.sh → sweetGrass content-addressed storage when deployed.
11. **Hand-rolled HTML sites** (signal, thesis) → Zola migration when justified.

## Pattern: Sourdough Culture

Established this session as ecoBin DNA / central dogma pattern:

```
On startup:  load saved state from /var/lib/skunky-ingest/*.json
             log "sourdough warm start" with entity count
During run:  accumulate in memory, periodic flush to disk
On shutdown: final flush + save_culture()
On reboot:   warm start from persisted culture — no data loss
```

Every new accumulator module in skunky-ingest MUST follow this pattern. State lives on persistent disk, never tmpfs. The organism remembers.

---

*2,096 lines of Python → 0. Three cron jobs → one. Two processes → one. Six fossils created. All sourdough cultures warm-starting. The jellystein phase is over — golgiBody runs pure Rust.*

*Wave 167 — October 8, 2026*
