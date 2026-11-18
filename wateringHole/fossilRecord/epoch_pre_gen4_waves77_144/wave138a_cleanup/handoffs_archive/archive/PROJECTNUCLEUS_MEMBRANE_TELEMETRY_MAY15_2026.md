# projectNUCLEUS — L3+L4 Membrane Telemetry Handoff

**Date**: 2026-05-15
**Author**: projectNUCLEUS (ironGate)
**Audience**: primalSpring upstream audit, primalPSing review
**Scope**: Continuous sovereignty telemetry pipeline, unified baselines, permanent shadow model

---

## Summary

Layer 3 (external membrane / VPS) and Layer 4 (internal membrane / gate) are
now connected through a unified telemetry pipeline. Shadow data collection is
**permanent** — it does not stop after a primal reaches parity and replaces an
external service. This formalizes the "calibrate-shadow-cutover" protocol into
a continuous health signal.

---

## What Was Built

### 1. `deploy/membrane_telemetry.sh` — Unified Probe Script

Single cron-ready script collecting telemetry across both membranes every 15 min.

**External membrane (L3 — VPS):**
- Caddy health endpoint (`:80/health`) — latency, status
- Songbird TURN reachability (TCP `:3478`)
- RustDesk hbbs reachability (TCP `:21116`)
- BearDog TLS shadow (`:8443`) — if running
- VPS resource snapshot via SSH (`free -m`, `df -h`, service count)

**Internal membrane (L4 — gate):**
- Cloudflare tunnel latency (external baseline)
- Per-primal RPC health (beardog, songbird, nestgate, skunkbat, biomeos)
- Content parity (VPS cache TTFB vs GitHub Pages TTFB)
- BTSP auth events (btsp/pam/fail counts from JupyterHub log)

**Output**: `validation/baselines/daily/membrane_telemetry_YYYY-MM-DD.csv`
**Columns**: `timestamp_utc, probe_name, target, latency_ms, status, http_code, extra`

### 2. `deploy/membrane_summary.sh` — Rolling 7-Day Summary

Aggregates daily CSVs into `validation/baselines/membrane_7day.toml`:

- `[external_membrane]` — Caddy uptime, TURN reachability, BearDog TLS p50/p95
- `[internal_membrane]` — primal health %, Cloudflare TTFB, BTSP auth %
- `[parity]` — tls_parity, nat_reachable, content_parity, auth_accumulating
- `[thresholds]` — cutover gates requiring N consecutive days of parity

The `membrane_7day.toml` IS committed to git — it's the canonical state snapshot.
Daily CSVs are `.gitignore`d (operational data).

### 3. `nucleus_config.sh` — Telemetry Settings

```
MEMBRANE_TELEMETRY_INTERVAL=900      # 15 min
MEMBRANE_TELEMETRY_DIR=$NUCLEUS_PROJECT_ROOT/validation/baselines/daily
MEMBRANE_SUMMARY_DAYS=7
MEMBRANE_CUTOVER_CONSECUTIVE_DAYS=7
```

### 4. `shadow_run_orchestrator.sh` — Baseline Path Fix

Fixed the gap where `btsp_tls_parity.sh` looked for baselines in
`infra/benchScale/baselines/` but the 7-day summary lives at
`validation/baselines/`. Orchestrator now reads:

1. `membrane_7day.toml` (unified, preferred)
2. `cloudflare_tunnel_7day.toml` (fallback)
3. `benchScale/baselines/*.toml` (legacy)

Orchestrator results now append to the unified daily telemetry CSV.

### 5. `routing_config.toml [telemetry]` — Permanent Shadow Mode

```toml
[telemetry]
enabled = true
shadow_mode = "permanent"
collection_interval_s = 900
retention_days = 90
skunkbat_correlation = true
cutover_gate_days = 7
```

Formalizes that shadow data collection is permanent, not a pre-cutover phase.
SkunkBat audit events correlate with telemetry probes for Layer 2 validation.

### 6. Documentation Updates

- `PRIMAL_VS_SOVEREIGNTY_GOALS.md` — new "L3+L4 Membrane Bridge" section
- `SOVEREIGN_COMPOSITION_EVOLUTION.md` — new "Layer 3+4: The Membrane Bridge" section,
  updated Layer 4 to reference continuous telemetry, membrane telemetry in Bash tooling list

---

## Architectural Insight

The calibrate-shadow-cutover protocol remains unchanged. What changes is the
lifecycle of the "shadow" phase — it becomes permanent telemetry:

- **Before cutover**: telemetry validates parity (BearDog p95 <= Cloudflare p95)
- **After cutover**: telemetry detects regression, baseline drift, cost anomalies
- **Permanently**: SkunkBat correlates telemetry probes with audit events

This mirrors the biological model: a cell continues monitoring its membrane even
after all internal protein synthesis is operational.

---

## Files Changed (projectNUCLEUS)

| File | Change |
|------|--------|
| `deploy/membrane_telemetry.sh` | NEW — unified probe script |
| `deploy/membrane_summary.sh` | NEW — rolling 7-day summary |
| `deploy/nucleus_config.sh` | ADD telemetry settings |
| `deploy/routing_config.toml` | ADD `[telemetry]` section |
| `infra/benchScale/scenarios/shadow_run_orchestrator.sh` | FIX baseline path, wire to unified CSV |
| `.gitignore` | CLARIFY daily CSV vs committed TOML |
| `README.md` | UPDATE telemetry references |
| `PHASES.md` | UPDATE Phase 2 status line |
| `specs/EVOLUTION_GAPS.md` | ADD changelog entry, update scoring |

## Files Changed (wateringHole)

| File | Change |
|------|--------|
| `PRIMAL_VS_SOVEREIGNTY_GOALS.md` | ADD L3+L4 membrane bridge section |

## Files Changed (whitePaper)

| File | Change |
|------|--------|
| `gen4/architecture/SOVEREIGN_COMPOSITION_EVOLUTION.md` | ADD Layer 3+4 membrane bridge, permanent shadow model |

---

## Upstream Review Notes

- **No upstream primal changes needed** — this is all deployment ops (bash scripts, TOML config)
- The telemetry data format (CSV + TOML) is readable by future Rust tooling
- `membrane_summary.sh` can evolve to Rust when it needs to (per priority: stability → sovereign → Rust)
- SkunkBat correlation is the composition integration point (Layer 2 validating L3+L4)
- Individual parity scripts (`btsp_tls_parity.sh`, etc.) remain for deep-dive analysis
- `capture_tunnel_metrics.sh` coexists (membrane_telemetry subsumes it)
- darkforest validation is separate (point-in-time security, not continuous telemetry)
