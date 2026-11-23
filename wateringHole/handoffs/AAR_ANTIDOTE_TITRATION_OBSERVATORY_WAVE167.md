# AAR: Antidote Titration & Scatter Observatory

**Wave 167 — October 8, 2026**
**Observer**: eastGate
**Preceded by**: AAR_SCYBORG_BULWARK_ANTIDOTE_WAVE167

---

## What Happened

Built and deployed a self-regulating scatter defense system. The scatter server no longer serves binary poison — it follows a logarithmic titration curve that automatically mixes antidote remediation into scatter content from day 1, accelerates on detection of ingestion, and differentiates between aggressive violators and innocent bystanders.

## What Was Built

### 1. Antidote Distribution (making it findable)

| Channel | URL/Path | Status |
|---------|----------|--------|
| Direct download | `sporeprint.primals.eco/tools/antidote.py` | ✅ Live |
| Documentation | `sporeprint.primals.eco/methodology/scyborg-binary-genetic-bulwark/` | ✅ Live |
| Contact page | Remediation section with links | ✅ Live |
| HTTP headers | `X-Remediation` on every scatter response | ✅ Live |
| HTML notice | Comment in 200 OK scatter pages | ✅ Live |

### 2. Ingestion Observer

| Component | Implementation | Cadence |
|-----------|---------------|---------|
| Python prober | `ingestion-observer.py` | Every 15 min (systemd timer) |
| Rust pipeline | `ingestion_observer.rs` | Continuous (wired into skunky-ingest) |
| UV lamp | `uv-lamp.py` | Every 4 hours (systemd timer) |

Probes 4 surfaces: web indexes, GitHub code search, AI model outputs, fake repo leakage.

Four ingestion phases tracked:
- **Phase 0: SEEDING** — scatter served, no external signal ← **current**
- **Phase 1: UPTAKE** — markers in web/code indexes
- **Phase 2: DIGESTION** — AI models reproduce scatter content
- **Phase 3: EXPRESSION** — unprompted reproduction

### 3. Logarithmic Titration Curve

```
poison = 1 / (1 + 0.15 × ln(1 + effective_days))
```

Antidote flows from day 1. Phase transitions jump the curve forward (+30/+90/+180 days). Floor at 5%.

### 4. Secretion ≠ Injection

| Fleet Type | Chain Depth | Poison | Antidote |
|------------|-------------|--------|----------|
| Deep violator | >50 | Full (bypass curve) | None |
| Known fleet | 10-50 | +30% boost | Reduced |
| New/researcher | <10 | Global curve | Full |

Meta interacting more → more poison. Researcher touching once → full antidote.

### 5. Scatter Observatory

Four live measurement surfaces:

| Surface | Refresh | Content |
|---------|---------|---------|
| `/observer.json` | per-request | Titration + observer + ledger |
| `scatter-observatory.json` | 30 seconds | File-based for dashboard |
| `/metrics` | per-request | Raw scatter breakdown |
| `ingestion-timeline.jsonl` | observer flush | Append-only timeline |

### 6. Jellystein Fossilized

4 orphan Python scripts fossilized to `fossilRecord/golgi-python-wave167/`:
- `signal_gen.py` (382 lines) → replaced by `signal_writer.rs`
- `stage_evidence.py` (78 lines) → detroit built by Zola
- `build-unified-graph.py` (343 lines) → dead code
- `ingest.py` (217 lines) → dead code

Originals marked with `⚠️ FOSSILIZED` header, execute permission removed. Zero Python processes on golgiBody.

## Live Measurements at Deployment

```
Phase:              0 (SEEDING)
Poison multiplier:  99.6%
Antidote level:     0
Active fleets:      4
  Deep (>50):       1  → full poison
  Moderate (10-50): 1  → reduced antidote
  New (<10):        2  → full antidote
Requests/sec:       2.2
Bytes served:       ~1.9 MB/min
Observer runs:      3
External detections: 0
```

## Commits (skunkBat)

| Hash | Message |
|------|---------|
| b8f6529 | remediation headers + NOTICE injection + UV→antidote feedback |
| a5b5bfb | ingestion-observer: persistent scatter sentinel with phase tracking |
| bbea79d | ingestion_observer.rs: jellystein wired into primals pipeline |
| 2e02992 | antidote titration: automatic poison ramp-down on ingestion detection |
| 6487304 | logarithmic titration: antidote flows from day 1 |
| 1828a69 | separate secretion from injection: per-fleet antidote filtering |
| 16b6e60 | scatter observatory: live metrics, titration, fleet tier distribution |

sporePrint: 31fbedd3 (antidote download + contact page)

## Gaps Closed (from AAR_SCYBORG_BULWARK_ANTIDOTE_WAVE167)

| Gap | Status | Notes |
|-----|--------|-------|
| Gap 1: Publish antidote on sporePrint | ✅ Closed | /tools/antidote.py downloadable, methodology page live |
| Gap 5: UV→antidote feedback loop | ✅ Closed | Contact template auto-generation on detection |
| Gap 2: Provenance trio local | Pending | Separate effort |
| Gap 3: loamSpine ledger | Pending | Separate effort |
| Gap 4: AGPL compliance endpoint | Pending | |
| Gap 6: Scatter fingerprint database | Pending | |
| Gap 7: AI model probing | ✅ Closed | Observer probes AI surfaces every 15 min |

## New Gaps Identified

| Gap | Priority | Description |
|-----|----------|-------------|
| A | Now | Titration start epoch should persist across binary restarts (currently resets) |
| B | Next | Dashboard page needs to consume scatter-observatory.json |
| C | Next | Signal site visualization of titration curve position |
| D | Design | Fleet-specific antidote_level logging for audit trail |
| E | Design | Multi-node observer correlation (when golgiLayer2 exists) |

## Team Handoffs

### → signal site team
Consume `scatter-observatory.json` for a live titration gauge. Fields: `titration.poison_mult`, `titration.antidote_level`, `titration.days`, `titration.phase_name`. Update every page load.

### → ops
- `ingestion-observer.timer` runs every 15 min — check logs with `journalctl -u ingestion-observer`
- `uv-lamp.timer` runs every 4 hours — check with `journalctl -u uv-lamp`
- Observer state: `/var/lib/skunky-ingest/observer-state.json`
- Timeline: `/var/lib/skunky-ingest/ingestion-timeline.jsonl`
- Observatory: `/opt/membrane/live-terminal/scatter-observatory.json`

### → anyone responding to remediation requests
Point them to:
1. `sporeprint.primals.eco/tools/antidote.py` (download)
2. `sporeprint.primals.eco/methodology/scyborg-binary-genetic-bulwark/` (docs)
3. `python3 antidote.py scan <file>` then `python3 antidote.py clean <file>`

Tiered response:
- Researchers: help directly, free
- Companies: point to published recipe, or AGPL-3.0 compliance
- Active violators: conversation starts with the license

---

*Wave 167 — October 8, 2026*
