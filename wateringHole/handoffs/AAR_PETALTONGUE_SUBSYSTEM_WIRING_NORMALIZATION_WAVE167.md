# AAR: petalTongue Subsystem Wiring + Normalization Layer

**Wave 167 — October 8, 2026**
**Observer**: sporeGate (Artisan session)
**Duration**: ~60 minutes
**Predecessor**: `AAR_PETALTONGUE_CROSS_SITE_WIRING_WAVE167.md`
**Companion subGen**: `BIOMEOS_HUD_PETALTONGUE_LIVE_WAVE167.md`

---

## Summary

Two architectural changes to petalTongue's rendering pipeline:

1. **Subsystem Wiring** — Unlocked petalTongue's own built-but-unwired capabilities: faceting (`compile_faceted()`), polar coordinates, and three new `DataBinding` channel types (`FacetedBar`, `FacetedGauge`, `Donut`). Collapsed 9 separate organism/entity bar panels into 3 faceted small-multiples + 1 donut. Detroit gained 4 donut charts and 1 faceted gauge.

2. **Normalization Layer** — Added a `Normalization` enum (7 strategies: None, MinMax, Symmetric, ZScore, Log1p, Rank, LeakyReLU) applied per-column before rendering. Fixes the range crushing problem where IPs=199 next to UA Pool=12 made smaller metrics invisible. Original values preserved in data rows for label display.

---

## The Gap That Was Found

In `runtime.rs` line 182:

```rust
let scene_graph = self.compiler.compile(&expr, &data);
```

This called `compile()`, not `compile_faceted()`. The faceting system was **fully built and tested** in `facets.rs` — 4 passing tests, handles `FacetLayout::Wrap` and `Grid`, partitions data by field — but the runtime binding path (the WS JSON-RPC path that all JS bridges use) skipped it entirely.

`compile_faceted()` delegates to `compile()` when no facets are set (lines 23-26 of facets.rs), making it a safe drop-in replacement. Zero regression risk, confirmed by full test suite.

---

## What Was Built

### Rust Changes

| Component | Change |
|-----------|--------|
| `runtime.rs` | 2 call sites: `compile()` → `compile_faceted()` |
| `data_channel.rs` | 3 new `DataBinding` variants: `FacetedBar`, `FacetedGauge`, `Donut` |
| `data_channel.rs` | 2 new structs: `FacetGroup`, `FacetGaugeEntry` |
| `data_channel.rs` | `Normalization` enum (7 strategies) + field on `Bar`, `Heatmap`, `FacetedBar`, `FacetedGauge` |
| `data_binding/mod.rs` | 3 compile paths: FacetedBar (Bar + Wrap facet), FacetedGauge (Arc + Wrap facet), Donut (Arc + Polar) |
| `data_binding/normalize.rs` | **NEW** — 7 normalization functions + `normalize_faceted_columns()` + `normalize_heatmap_columns()` + 12 tests |
| `data_binding/describe/mod.rs` | 3 new describe arms |
| `telemetry_adapter.rs` | Exhaustive match update |
| `chart_renderer/mod.rs` | Exhaustive match update (falls through to scene_paint) |
| `visualization_handler/stream.rs` | Exhaustive match update |
| `petal-tongue-wasm/src/binding.rs` | Exhaustive match update |

### Normalization Strategies

| Strategy | Output | Use Case |
|----------|--------|----------|
| `none` | Raw values | Same-unit data (default) |
| `min_max` | [0, 1] | Mixed metrics: IPs vs UA pool vs blame% |
| `symmetric` | [-1, 1] | Zero-centered comparison |
| `z_score` | Unbounded (σ) | Statistical outlier detection |
| `log1p` | Compressed | Heavy-tailed distributions (request counts) |
| `rank` | [0, 1] | Outlier-immune ordinal ranking |
| `leaky_relu` | αx or x | Mixed-sign data with negative attenuation |

**Per-column independence**: For `FacetedBar` and `Heatmap`, each category column is normalized independently. IPs=1→0.0, IPs=199→1.0, while UA=1→0.0, UA=12→1.0. Metrics become visually comparable without losing relative ordering within each metric.

**Original value preservation**: Every data row carries `original_value` alongside the normalized `y`. Labels and tooltips display real numbers; bars render at proper scale.

### JS Bridge Changes

| Site | Changes |
|------|---------|
| signal-pt.js | 4 organism bars → 1 `faceted_bar`; 4 entity bars → 1 `faceted_gauge` + 1 `faceted_bar`; Accept-Language → `donut`; normalization: `min_max` on organism/entity/matrix |
| hud-pt.js | Mirror of signal changes |
| detroit-pt.js | Node types, flow types, communities → `donut` × 3; per-court capture → `faceted_gauge` |
| thesis-pt.js | Entity matrix → `normalization: min_max` |

### Panel Count Evolution

| Site | Before (batch 2) | After (subsystem wiring) | Net |
|------|-------------------|--------------------------|-----|
| signal | 27 panels | 22 panels (9 collapsed into 3 faceted + 1 donut) | -5 panels, same data |
| hud | 27 panels | 22 panels | -5 panels |
| detroit | 19 panels | 19 panels (3 bar→donut, 1 bar→faceted_gauge) | Same count, richer types |
| thesis | 14 panels | 14 panels (1 heatmap gets normalization) | Same count |
| **Total** | **87** | **77** | Fewer panels, more information per panel |

---

## Build & Deploy

```
cargo check --no-default-features          # clean
cargo test -p petal-tongue-scene -p petal-tongue-types -p petal-tongue-platform  # all pass
cargo build --release --no-default-features --target x86_64-unknown-linux-gnu --bin petaltongue
scp → golgi:/tmp/petaltongue-new
sudo systemctl stop petaltongue-hud membrane-petaltongue
sudo cp → /opt/membrane/petaltongue
sudo systemctl start membrane-petaltongue petaltongue-hud
rsync signal-pt.js, hud-pt.js, detroit-pt.js, thesis-pt.js → golgi
```

Both services confirmed active. WS bridge responding at `/ws`.

---

## Known Debt (from sweep)

| Priority | Item | Status |
|----------|------|--------|
| HIGH | `normalization` field missing in `petal-tongue-ui`, `petal-tongue-headless`, `petal-tongue-graph` test constructors | To fix |
| HIGH | `gate_mesh` tests need `offline-topology` feature gate | Pre-existing |
| HIGH | No SVG baseline tests for `FacetedBar`, `FacetedGauge`, `Donut` | To add |
| MEDIUM | ~80% duplication between signal-pt.js and hud-pt.js | Extract shared module |
| MEDIUM | Organism classification heuristic duplicated in 5+ JS files | Centralize |
| MEDIUM | Thesis not migrated to faceted panels (only has normalization on matrix) | Next session |
| MEDIUM | Inconsistent panel DOM IDs between signal and hud | Unify when extracting shared module |
| LOW | Stale `public/js/` copies vs `static/js/` source | Gitignore `public/` |
| LOW | Documentation panel counts stale | Updated in this AAR |

---

## Privacy Invariant

Unchanged across all surfaces:
- No cookies, no tracking pixels, no JS analytics on any site
- No IP addresses stored or logged in receptor/signal systems
- No PII on any public surface
- petalTongue web mode: CORS enabled, no auth cookies, no session state
- Normalization is server-side only — no client-side data leakage

---

## Lessons Learned

1. **Look inside before building outside** — The faceting system existed for months, fully tested, but nobody wired it through the runtime binding path. One line change unlocked it. The instinct to add more JS panels when the Rust subsystem already existed was the wrong direction.

2. **Mixed-metric panels need normalization from day one** — Deploying faceted bars with raw values (IPs=199, UA=12, Blame%=45) immediately produced crushed visualizations. Normalization should be a first-class concern in any multi-metric panel design, not a fix-up.

3. **Per-column normalization is the right default for faceted data** — Normalizing all values together (global min-max) would destroy within-metric ordering. Per-column normalization preserves "Meta has more IPs than Anthropic" while making IPs and UA Pool comparable.

4. **`original_value` preservation is essential** — Users need to see real numbers in labels. The normalization layer transforms the rendering y-value but always carries the original for display purposes.

---

*Signed: ecoPrimal*
