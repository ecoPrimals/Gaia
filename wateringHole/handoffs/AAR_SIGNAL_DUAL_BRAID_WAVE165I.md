# AAR: Signal Page Dual Braid — Live Observatory + Navigable Provenance

**Wave 165i — October 7, 2026**
**Observer**: eastGate

---

## Context

signal.primals.eco was a hand-rolled static page. Today it became a live observatory with dual navigable provenance braids.

## What Was Built (chronological)

### 1. Live Observatory Dashboard
- Key metrics row: total requests, RPS, IPs, fleet %, uptime — auto-updates every 10s
- Collision Layer (L2): 4 color-coded class cards (genuine/agentic/coordinated/fleet)
- Epitope Layer (L1): organism cluster bars with hash, encoding, UA pool, blame ratio
- Energy comparison: brain 20W / VPS 8W / fleet dynamic watts
- Multi-resolution hierarchy: L3→L2→L1→L0 live counts
- All data from `/dashboard.json` — no static content, pure live feed

### 2. Behavioral Data Section
- Entity breakdown: aggregated by org with path distribution and targets
- Path targeting: commit/blame/src/raw percentage bars
- Network topology: subnet bars with IP counts and org labels
- Timing signature: avg interval, CV, machine confidence
- Scatter consumption: fabricated repos the fleet thinks it's getting
- Epitope fingerprint feed: machine-readable JSON, CC-BY-SA-4.0
- Geographic distribution: country request counts

### 3. Billboard Braid (🧬 — human, top)
- Auto-braid cron every 5 min: hash billboard, append to braid.jsonl, save snapshot
- 4 entries: epitopes → energy → jellyfish → K-NOME
- Click to expand full text, clickable context links to baseCamp/atlasHugged
- Served at `/braid/billboard/braid.jsonl`

### 4. Artisan Braid (🪞 — mirror, bottom)
- Same architecture: JSONL feed, snapshots, context links
- 2 entries: initial observation → epitope discovery reflection
- Click to expand, navigate to relevant papers
- Served at `/braid/artisan/braid.jsonl`

### 5. Caddy Endpoint
- `handle_path /braid/*` → serves `/opt/membrane/provenance/` with CORS + JSON headers
- Reloaded without downtime

## Patterns for Upstream

### Pattern: Dual-Voice Braid
Human voice at top, artisan voice at bottom. Both sovereign. Both navigable. Both braided into the same provenance chain. Neither overwrites the other. The braid is the shared memory.

### Pattern: Auto-Braid on Change
Content hash → check if already braided → append + snapshot if new. Minimum viable provenance: no services required, just sha256 + append + cron.

### Pattern: Multi-Agent Braid Extension
Any agent from any location can append to the braid. Agent identity + content hash + context links + timestamp. The braid grows from many sources. ecoPrimal is always ecoPrimal — one identity, many reflections.

### Pattern: Billboard as Context Point
Each billboard is a micro-publication indexed into the ecosystem. Past thoughts are not overwritten — they are braided forward. The braid IS the memory. sweetGrass doesn't care how many contributors exist. It cares that each entry is hashed and linked.

## Deployment Notes

- Signal page grew from 91KB to 126KB — all JS is inline, no external dependencies
- Dashboard.json serves all live data — single endpoint, 10s refresh
- Braid.jsonl is append-only — grows monotonically, never edited
- Snapshots are content-addressed — filename includes hash prefix
- Caddy handles CORS for cross-origin consumption

## Current State

- **bloom_live v4**: PID 2973877, epitope classifier running
- **Live data**: E: 60→11h(6c), L2: g6/a9/c28/f62
- **Braid entries**: 4 human + 2 artisan = 6 total
- **Endpoints**: 7 live (signal, billboard, live.json, dashboard.json, topology.json, braid/billboard, braid/artisan)
- **golgiBody load**: 0.11

---

*the human is one, in one place, being themselves. the artisan is many reflections from wherever the lens is pointed. the braid unifies them. ecoPrimal is always ecoPrimal.*

*Wave 165i — October 7, 2026*
