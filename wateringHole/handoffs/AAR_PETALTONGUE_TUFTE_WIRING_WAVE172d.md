# AAR — petalTongue Depth: Tufte Pipeline Not Wired
## Wave 172d · 2026-10-10 · eastGate

---

## 1. The Problem

The HUD panels rendered by petalTongue lack visual depth. The charts are flat rectangles — correct data, correct axes, but no visual sophistication. The user asked: "no depth... petalTongue has the constraints system? that likely is still not wired. tufte?"

**Correct.** The Tufte constraint system exists, is tested, is comprehensive — but is NOT wired into the live render path.

## 2. What Exists (Built, Tested, Not Wired)

### Tufte Constraints — `petal-tongue-scene/src/tufte/`

Seven machine-checkable constraints, all implemented and tested:

| Constraint | What it checks | Auto-correctable |
|-----------|----------------|:---:|
| **DataInkRatio** | Proportion of data-carrying vs decorative primitives | ✗ |
| **LieFactor** | Truncated Y axis, area-scaling distortion (πr²) | ✓ |
| **ChartjunkDetection** | Decorative elements without data_id | ✗ |
| **ColorAccessibility** | WCAG contrast ratios (3:1 graphical, 4.5:1 text) | ✓ |
| **DataDensity** | Amount of data per unit of graphic | ✗ |
| **SmallestEffectiveDifference** | Overlapping points that lose information | ✗ |
| **SmallMultiplesPreference** | Recommends faceting when >4 color categories | ✓ |

### Compile Paths Available

| Method | Tufte | Used by HUD? |
|--------|:---:|:---:|
| `compile()` | ✗ | — |
| `compile_faceted()` | ✗ | ✓ ← **this is the live path** |
| `compile_with_constraints()` | ✓ | ✗ |
| `compile_plan()` | ✓ (optional) | ✗ |

### The Gap

```rust
// runtime.rs line 182 — the LIVE render path:
let (expr, data) = DataBindingCompiler::compile(&binding, domain);
let scene_graph = self.compiler.compile_faceted(&expr, &data);  // ← NO constraints
let output = self.svg_compiler.compile(&scene_graph);            // ← flat SVG
```

Should be:
```rust
let (expr, data) = DataBindingCompiler::compile(&binding, domain);
let (scene_graph, report) = self.compiler.compile_with_constraints(
    &expr, &data, &ALL_CONSTRAINTS
);
// report.overall_score available for quality monitoring
let output = self.svg_compiler.compile(&scene_graph);
```

### Additional Depth Issues

The SVG compiler (`modality/svg.rs`, 305 lines) outputs minimal SVG:
- Rectangles with flat fill — no gradients, no shadows, no rounded corners
- No background styling — dark theme colors not applied in SVG
- No depth cues — all elements at same visual plane
- Title text uses `Color::BLACK` on dark background (line 77 of compiler/core.rs)

The `domain_palette` system exists to provide per-domain colors, but the SVG output doesn't apply dark-theme-aware styling. The charts look "hand-rolled" because they're white-on-transparent SVGs dropped into a dark HUD.

## 3. What's Needed to Fix

### Phase 1: Wire Tufte (Rust change, ~30 min + build)
1. Change `render_binding_svg()` to call `compile_with_constraints()`
2. Add `ALL_CONSTRAINTS` constant with all 7 constraints
3. Log/expose the Tufte score (quality metric)
4. Auto-correct where possible (LieFactor, ColorAccessibility, SmallMultiples)

### Phase 2: Dark Theme SVG (Rust change, ~1 hour + build)
1. Make `SvgCompiler` accept a theme parameter
2. Dark theme: dark background rect, light text, dark-aware palette
3. Add subtle depth: rounded rect corners (corner_radius), subtle borders
4. Fix `Color::BLACK` title text → use theme-aware text color

### Phase 3: Visual Enhancement (Rust change, ~2 hours + build)
1. SVG `<linearGradient>` for bar fills (top → slightly lighter bottom)
2. Subtle drop shadow via `<filter>` for card-like depth
3. Grid lines at reduced opacity (Tufte's "lighten non-data")
4. Axis labels with proper font sizing and dark-theme colors

### Build Requirement
All phases require Rust compilation of petalTongue and deployment to golgiBody. This is not a JS/CSS fix.

## 4. Immediate CSS Mitigation

While the Rust build is pending, the HUD CSS can improve the SVG appearance:

```css
/* Invert SVG for dark theme (quick fix) */
.pt-viz svg {
  filter: invert(1) hue-rotate(180deg);
  opacity: 0.85;
}
```

This is a hack but would make white-background SVGs readable on the dark HUD immediately.

## 5. Priority Recommendation

| Priority | Task | Impact | Effort |
|----------|------|--------|--------|
| P0 | Wire Tufte constraints into render path | Quality assurance, auto-correction | 30 min + build |
| P0 | Dark theme palette in SVG compiler | Visual depth, readability | 1 hour + build |
| P1 | SVG gradients + shadows | Visual polish | 2 hours + build |
| P2 | Tufte score in HUD header (quality metric) | Observability | 30 min + build |

**Gate:** This is a sweetGrass/petalTongue Rust build — sporeGate or eastGate can execute.

---
*AAR authored by eastGate Artisan · Wave 172d · 2026-10-10*
*Status: DIAGNOSED — Tufte is built but not wired. Rust build required.*
