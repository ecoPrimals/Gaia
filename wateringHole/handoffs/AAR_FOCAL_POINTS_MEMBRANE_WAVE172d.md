# AAR: Focal Points — Epitope Tangent Membrane Visualization

**Wave**: 172d · **Date**: 2026-10-10 · **Duration**: ~30 min

## What

Built and deployed the **membrane focal-point visualization** for hud.primals.eco — a new SVG panel that renders the membrane as a circle with each epitope as a tangent point on the surface. This is baseCamp 53: the missing structural view that shows the lens, not just the charts.

## Why

The HUD had panels in a flat grid. Every panel had equal visual weight (adjusted by dimensional cost from baseCamp 52), but there were no **focal points** — no geometric structure showing WHERE data converges and WHY. The user identified: each epitope split is a bifurcation point on the membrane manifold, and each bifurcation has a tangent plane. The visualization should render the surface itself.

## Key Concepts

- **Membrane as manifold**: the engagement surface is a topological surface in data space
- **Epitopes as tangent planes**: each classification is a point on the surface with its own tangent
- **Focal distance = 1/C(n) = 1/π^(n/2)**: low-dimensional splits → long focal distance (gentle lens); high-dimensional → short (sharp lens)
- **Category arcs**: signal (fire/orange), membrane (green), immune (purple), beacon (blue) — each occupies a proportional arc on the circle
- **Alive/dormant gating**: dots glow when their panels have data, dim when dormant

## Files Modified

- **`infra/hud/site/public/js/hud-pt.js`** — Added `renderMembraneSVG()` function (~170 lines):
  - Allocates angular arcs by category, proportional to panel count
  - Draws category-colored arcs on the membrane circle
  - Places each panel as a tangent point with tangent lines (length ∝ focal distance)
  - Draws focal points inside the circle (distance ∝ 1/curvature)
  - Dashed lines from tangent point to focal point for alive panels
  - Glow filter on alive epitope dots
  - Labels rotated to follow the circle
  - Legend showing dimensional cost → focal distance mapping
  - Re-renders on each `markAlive()` call
  - Added membrane card HTML in `mount()` function

- **`infra/sporePrint/content/science/53_focal_points_tangent_membrane.md`** — baseCamp 53 paper:
  - Focal points in optics → membrane as lens
  - Epitopes as split points (bifurcations in the data manifold)
  - Tangent planes on the membrane surface
  - Connection to π through curvature
  - petalTongue primitives that support this (ParametricCurve, VectorField, Polar, Perspective3D)
  - What to build: membrane surface panel with tangent lines, focal points, sort vector field

- **`infra/sporePrint/content/science/_index.md`** — Added baseCamp 53 entry

## Verification

- Deployed to golgiBody via SCP
- Verified live at hud.primals.eco — 22/25 panels alive
- Membrane circle renders with all 4 category arcs
- Tangent lines correctly shorter for high-dimensional panels
- Focal points visible inside circle
- Labels readable, following the circle curvature
- Legend and alive/dormant indicators render correctly

## What Comes Next

- **Sort vector field**: Render the gradient of the classification function as arrows on the membrane surface (requires VectorField integration from petalTongue Rust side)
- **3D membrane**: Extend to sphere/torus when Perspective3D rendering is wired
- **Clickable tangent points**: Click an epitope dot to scroll to its panel
- **Tufte pipeline wiring**: Still the P0 Rust build needed (see AAR_PETALTONGUE_TUFTE_WIRING)
- **Curvature visualization**: Show how sharply the membrane bends at each epitope — visual density/fold depth
