# hotSpring → petalTongue + barraCuda: CompChem Explorer Molecular Viz + Tessellation

**Date:** May 28, 2026
**From:** hotSpring (computational chemistry)
**To:** petalTongue team (visualization) + barraCuda team (GPU math)
**Priority:** Phase 4 implementation — first consumer driving spec priority
**Reference:** `hotSpring/specs/COMPCHEM_SPOREGARDEN_PRODUCT.md`

---

## Summary

hotSpring is building the **CompChem Explorer** — a sporeGarden-tier product
for interactive 3D molecular visualization and GPU-accelerated free energy
landscape computation. It is designed as the **first consumer** of petalTongue's
Phase 4 molecular visualization capabilities and barraCuda's `math.tessellate`
surface mesh generation.

**The ask:**

1. **petalTongue:** Prioritize Phase 4 implementation (`Perspective3DCoord`,
   `GeomSphere`, `GeomCylinder`, `GeomMesh3D`) — we have a concrete product
   consuming these immediately upon availability.
2. **barraCuda:** Implement `math.tessellate.isosurface` for FEL surface mesh
   generation from scalar field grids.

---

## What hotSpring Has Ready

| Component | Status | Location |
|-----------|--------|----------|
| pseudoSpore v1.7.0 | 190/190 checks PASS | `pseudoSpore_hotSpring-CompChem-GuideStone_v1.7.0/` |
| 16 FEL landscapes | Complete (free + enzyme-bound) | `modules/01-06/` in pseudoSpore |
| FES GPU shader | 11-14× accel, RMSD 1e-14 | Paper 50, proven on RTX 4070 |
| Product spec | Drafted | `hotSpring/specs/COMPCHEM_SPOREGARDEN_PRODUCT.md` |
| Deploy graphs | 6 tiers defined | `hotSpring/graphs/compchem_*.toml` |
| Niche YAML | Complete | `hotSpring/niches/compchem-explorer.yaml` |
| Atom/bond data | PDB + GRO parsers in cazyme-fel | `staging/cazyme-fel/` |

---

## petalTongue: Phase 4 Request

### Capabilities Needed

| Capability | Spec Section | CompChem Usage |
|-----------|-------------|----------------|
| `Perspective3DCoord` | GoG Architecture Phase 4 | Orbit camera for molecular structures and FEL surfaces |
| `GeomSphere` | GoG Architecture Phase 4 | Atom rendering (Van der Waals / ball-and-stick) |
| `GeomCylinder` | GoG Architecture Phase 4 | Bond rendering (stick model) |
| `GeomMesh3D` | GoG Architecture Phase 4 | Isosurface meshes for FEL landscapes |
| `Navigate3D` | GoG Architecture Phase 5 | Orbit, pan, zoom interaction for molecular scenes |
| `DataBinding::FieldMap` | Extension needed | 2D scalar field → color-mapped surface (theta × phi × energy) |

### Data Channel Requirements

| Channel | Schema | Rate | Description |
|---------|--------|------|-------------|
| `Scatter3D` | `{x, y, z, element, radius, color}[]` | 1 Hz (static molecule) | Atom positions from PDB/GRO |
| `FieldMap` | `{grid: f64[][], theta_range, phi_range, energy_unit}` | 1 Hz (on recompute) | FEL surface grid |
| `GameScene` | Standard petalTongue scene graph | 60 Hz | Full interactive molecular scene |

### Minimum Viable Integration

For Tier 2 (Node Atomic), we need at minimum:

1. `Perspective3DCoord` rendering a list of positioned spheres and cylinders
2. Orbit camera via `interaction.poll` (mouse drag → rotation, scroll → zoom)
3. Color mapping from a scalar value (energy in kJ/mol) to a color ramp

This is enough to render a molecule (atoms as spheres, bonds as cylinders) and
an FEL surface (colored mesh from tessellated grid).

### Suggested Implementation Path

```
Phase 4a: Perspective3DCoord + GeomSphere (atom rendering)
Phase 4b: + GeomCylinder (bond rendering → full molecule display)
Phase 4c: + GeomMesh3D (isosurface mesh → FEL landscape)
Phase 4d: + FieldMap data binding (scalar grid → colored surface)
Phase 5a: + Navigate3D (orbit camera interaction)
```

hotSpring will provide test data (PDB atoms + FEL grids) as soon as Phase 4a
rendering is available for integration testing.

---

## barraCuda: Tessellation Request

### `math.tessellate.isosurface`

Generate a triangle mesh from a 2D or 3D scalar field using marching
squares/cubes. This is the bridge between raw FEL grid data and renderable
petalTongue `GeomMesh3D`.

**Input:**

```rust
struct IsosurfaceRequest {
    grid: Vec<f64>,        // flattened scalar field
    dims: [usize; 2],     // grid dimensions (theta_bins × phi_bins)
    isovalue: f64,         // energy threshold for isosurface (or 0.0 for heightmap)
    mode: TessellationMode, // Heightmap | MarchingSquares | MarchingCubes
}
```

**Output:**

```rust
struct IsosurfaceMesh {
    vertices: Vec<[f64; 3]>,   // (x, y, z) positions
    normals: Vec<[f64; 3]>,    // per-vertex normals
    indices: Vec<[u32; 3]>,    // triangle indices
    scalars: Vec<f64>,         // per-vertex scalar for color mapping
}
```

**Use cases:**

1. **Heightmap mode:** 2D FEL grid (theta × phi) → 3D surface where z = energy.
   Used for visualizing a single landscape.
2. **Marching squares:** 2D contour lines at specific energy levels (for
   Ramachandran-style plots on the Cremer-Pople sphere).
3. **Marching cubes:** If we extend to 3D Cremer-Pople analysis (theta × phi × Q),
   generate isoenergy surfaces in the 3D puckering space.

### `math.project.perspective`

Standard 4×4 perspective projection matrix construction and point projection.
May already exist in barraCuda math utilities — if so, expose via PrimalBridge
method `math.project.perspective`.

---

## Integration Timeline (from hotSpring's side)

| Phase | hotSpring Delivers | Needs From petalTongue | Needs From barraCuda |
|-------|-------------------|----------------------|---------------------|
| 0.1 | Product spec, deploy graphs | Nothing | Nothing |
| 0.2 | PDB parser → atom list, fes_*.dat → grid | `Perspective3DCoord` + `GeomSphere` | `math.tessellate.isosurface` (heightmap) |
| 0.4 | HILLS → live FES pipeline, interactive params | `GeomMesh3D` + `FieldMap` | GPU marching squares |
| 0.6 | Live simulation orchestration + streaming COLVAR | `Navigate3D` + full scene | — |
| 1.0 | Collaborative pseudoSpore sharing | — | — |

---

## What This Unblocks

- **First real consumer** of petalTongue Phase 4 molecular viz
- **First product** composing hotSpring science pipeline interactively
- **Reference implementation** for proton-heavy sporeGarden products
- **Validation of composition pattern** — science spring → product via PrimalBridge
- **Drives petalTongue beyond game rendering** into scientific visualization

---

## Related Documents

| Document | Location |
|----------|----------|
| Product spec | `hotSpring/specs/COMPCHEM_SPOREGARDEN_PRODUCT.md` |
| Niche YAML | `hotSpring/niches/compchem-explorer.yaml` |
| Deploy graphs | `hotSpring/graphs/compchem_*.toml` |
| petalTongue GoG spec | `primals/petalTongue/specs/GRAMMAR_OF_GRAPHICS_ARCHITECTURE.md` |
| barraCuda math spec | `primals/barraCuda/specs/` |
| Composition onramp | `infra/wateringHole/GARDEN_COMPOSITION_ONRAMP.md` |
| NUCLEUS matrix | `primalSpring/specs/NUCLEUS_VALIDATION_MATRIX.md` |
| Derivation Anchoring | `infra/wateringHole/DERIVATION_ANCHORING_STANDARD.md` |
