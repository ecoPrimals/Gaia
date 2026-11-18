# AAR — petalTongue Bridge Re-ORGAN-ization

**Wave 167 — October 8, 2026**
**Classification**: After Action Review — JS bridge architecture extraction + cleanup
**Duration**: Single session, ~45 minutes
**Operator**: ecoPrimal + artisan

---

## Situation

After the subsystem wiring + normalization session, a debt sweep identified ~80% code duplication across the 4 petalTongue JS bridge files (signal-pt.js, hud-pt.js, detroit-pt.js, thesis-pt.js). Each file carried its own copy of:

- WebSocket connection lifecycle (connect, reconnect, error handling)
- JSON-RPC 2.0 protocol (pending map, timeout, message dispatch)
- Status indicator updates
- SVG injection into DOM elements
- Organism classification heuristic (with behavioral inconsistencies between copies)

Additionally, thesis-pt.js lacked the faceted panels (FacetedBar, FacetedGauge, Donut) that signal and hud had gained in the wiring session. DOM IDs differed between signal and hud for equivalent panels.

## Actions Taken

### 1. Survey (completed prior)

Two subagents mapped the full anatomy:
- Bridge file survey: 4 files × (WS boilerplate, panel render calls, mount HTML, config constants)
- Organism heuristic survey: 5 files, 3 behavioral variants (strict isSelf, relaxed isSelf, relaxed labels)

### 2. Extract pt-bridge-core.js (251 lines)

Created `infra/shared/js/pt-bridge-core.js` as single source of truth:

| Component | Lines | What It Does |
|-----------|-------|-------------|
| `PetalBridge(config)` | ~80 | WS connect, JSON-RPC 2.0, status indicator, SVG inject, metrics |
| `classifyOrganism(cluster)` | ~20 | Unified heuristic: Meta/Anthropic/Self/Unknown |
| `buildOrganismProfile()` | ~20 | Faceted bar: per-organism IPs, UA pool, blame% |
| `buildEntityGauges()` | ~20 | Faceted gauge: per-entity timing CV |
| `buildEntityDetail()` | ~20 | Faceted bar: per-entity chrome lag, blame%, RPS |
| `buildEntityMatrix()` | ~25 | Heatmap: entities × 5 behavioral features |
| `buildAcceptLanguageDonut()` | ~15 | Donut: human vs machine Accept-Language |

Config is parameterized: `wsUrl`, `domain`, `statusEl`, `metricsEl`, `maxHeight`, `reconnectMs`, `rpcTimeoutMs`, `onConnect`.

### 3. Refactor All 4 Bridges

Each bridge became a thin wrapper that sets config + renders site-specific panels:

| File | Before | After | Change |
|------|--------|-------|--------|
| signal-pt.js | 562 lines | 335 lines | −40% |
| hud-pt.js | 445 lines | 309 lines | −31% |
| detroit-pt.js | 422 lines | 376 lines | −11% |
| thesis-pt.js | 250 lines | 237 lines | +faceted panels |

### 4. Migrate Thesis to Faceted Panels

thesis-pt.js now calls shared `build*()` helpers, gaining 5 new panels:
- Organism Profile (faceted_bar with min_max normalization)
- Entity Timing Gauges (faceted_gauge)
- Entity Behavioral Profile (faceted_bar)
- Entity Behavioral Matrix (heatmap with min_max)
- Accept-Language Donut

### 5. Unify DOM IDs

Standardized all DOM IDs to short `pt-*` names. Signal and hud now have identical ID sets. Thesis retains its paper-specific panels (fleet-ratio, machine-conf, entity-vol, epitopes). Detroit retains its graph-specific panels (node-types, flow-types, communities, etc.).

### 6. Organism Classification — Single Source of Truth

The `classifyOrganism()` function uses the relaxed isSelf rule (has_lang + ips=1) with standardized labels (Meta, Anthropic, Self, hash prefix). All 4 bridges now call this through the shared `build*()` helpers. The 5 duplicated copies are eliminated.

### 7. Stale public/ Cleanup

- Added `.gitignore` with `public/` for signal, hud, thesis sites (detroit already had it)
- All 4 sites rebuilt with Zola to produce clean public/ from static/
- Deployed to golgiBody via rsync

## Result

### Before
```
signal-pt.js  562 lines  ┐
hud-pt.js     445 lines  ├── ~400 lines duplicated 4×
detroit-pt.js 422 lines  │   organism heuristic in 5 files
thesis-pt.js  250 lines  ┘   inconsistent DOM IDs
─────────────────────────
Total: 1,679 lines
```

### After
```
pt-bridge-core.js  251 lines  ← single source of truth
signal-pt.js       335 lines  ← thin wrapper
hud-pt.js          309 lines  ← thin wrapper
detroit-pt.js      376 lines  ← thin wrapper (graph-specific)
thesis-pt.js       237 lines  ← thin wrapper + faceted panels
─────────────────────────────
Total: 1,508 lines (−10% total, −100% duplication)
```

### Deployment
- All 4 sites built with `zola build` — zero errors
- `pt-bridge-core.js` copied to each site's `static/js/`
- Script tag added before each site's bridge: `<script src="/js/pt-bridge-core.js">` then `<script src="/js/{site}-pt.js">`
- rsync to golgiBody — all 4 sites verified with `ls -la` on server

## Lessons Learned

1. **Survey before surgery.** The two-subagent survey that mapped all 4 bridges' anatomy (WS boilerplate, panel calls, DOM IDs, organism heuristic variants) made the extraction precise. Without it, the behavioral inconsistencies in isSelf (strict vs relaxed) would have been carried forward silently.

2. **Config objects beat function signatures.** `PetalBridge(config)` with named properties (`wsUrl`, `domain`, `maxHeight`, etc.) is more resilient than positional parameters. Each site overrides only what it needs. Defaults are sensible.

3. **Shared builders hide the faceting complexity.** The `build*()` helpers encapsulate the DataBinding JSON structure. Site-specific bridges don't need to know the shape of a faceted_bar or faceted_gauge — they pass data, the helper builds the binding.

4. **DOM ID unification is free during a rewrite.** Changing `pt-honesty-gauge` to `pt-honesty` costs nothing when you're already rewriting the mount function. The consistency pays dividends when debugging across sites.

5. **gitignore `public/` early.** Having stale build artifacts tracked means every deploy creates confusing diffs. The `.gitignore` should have been there from the start.

## Remaining Debt (MEDIUM)

| Item | Severity | Notes |
|------|----------|-------|
| Canonical source in `shared/js/` vs copies in each `static/js/` | MEDIUM | Currently manual copy; could use symlinks or build-time copy |
| Detroit CSS class naming (`pt-card`) differs from signal (`dash-card`) and hud (`hud-card`) | LOW | Intentional — each site has its own CSS, but could unify |
| hud-core.js (19KB) still hand-wired — not yet migrated to petal-tongue-wasm | LOW | Future: WASM replaces JS dashboard |
| Signal `signal-dashboard.js` (19KB) still hand-wired | LOW | Gradually being replaced by PT panels |

---

*ecoPrimal — Wave 167*
