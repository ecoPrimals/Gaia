# footPrint Composition Integration — Wave 136b

**Date**: 2026-07-11
**From**: eastGate overwatch
**To**: petalTongue, nestGate, songBird, projectNUCLEUS, flockGate teams
**Wave**: 136b

---

## What Happened

footPrint (`protoKarya/footPrint`) — a GIS home improvement planner built in
isolation — has been introduced to the ecosystem. It is the first **primal
composition target**: a product that will be served BY primals, not become one.

- Cloned to `protists/footPrint` (new top-level directory for protoKarya org)
- Registered in `ecosystem_manifest.toml` (repo 40/40, gate owner: flockGate)
- Dev server verified on eastGate (Vite + Express, zero TS errors, build passes)
- 12 petalTongue visual target areas documented (`specs/PETALTONGUE_VISUAL_TARGETS.md`)
- RustScript evidence added to gen3 thesis (`CONSTRAINED_EVOLUTION_FORMAL.md` §5.5)

---

## What footPrint Is

A browser-based GIS tool for property planning in Lansing, MI:
- Leaflet map with satellite imagery + 8 data source overlays
- Drawing tools (Geoman) with layer management
- ECS architecture, command pipeline, undo/redo
- Gauss-Newton parametric constraint solver (6 active constraint types)
- Intelligence layer (proximity, conflict detection, elevation)
- Snap, grid, dimensions, terrain, status bar

## What footPrint Is NOT

- **Not a primal.** It will never have IPC, `health.liveness`, or an ecoBin.
- **Not a stepping stone to Rust.** The browser frontend stays TypeScript.
  RustScript validates why primals should be pure Rust (see §5.5).

---

## Team Actions

### petalTongue
- Serve footPrint's browser frontend from Axum static file server
- 12 visual target areas define parity scope (VT-1 through VT-12)
- This is the first interactive tool for `live.primals.eco`

### nestGate
- Replace footPrint's `projects/` JSON file CRUD with CAS persistence
- Project data becomes content-addressed, rootPulse-traced
- `coord.ingest` can absorb project metadata alongside blurbs/AARs

### songBird
- Replace footPrint's Express `/api/proxy` with drawbridge routing
- Same allowlist pattern (OSM, FEMA, USGS, ArcGIS), sovereign proxy
- Rate limiting + caching already solved by drawbridge architecture

### projectNUCLEUS
- Package the composition: petalTongue + nestGate + songBird serving footPrint
- Validate as a deployable composition profile
- This is the pattern for all future interactive tools

### flockGate (gate owner)
- Host the composition on WAN
- Dispatch compute-heavy operations (DEM, batch elevation) to LAN HPC
- Validate WAN accessibility of the GIS tool

---

## RustScript — For the Record

footPrint contains RustScript: 12 zero-dep TypeScript modules encoding Rust safety
primitives (Result, Option, Owned, RefCell, Iter, Vec, Cow, Channel, Brand, exhaustive).

This is NOT ecosystem infrastructure. It is a **control experiment** that validates
why primals are pure Rust:
- 17/20 Rust constraints enforceable in TypeScript
- But 3 cannot be expressed at all (lifetimes, Send/Sync, zero-cost abstractions)
- And 9 require runtime wrappers instead of compile-time enforcement
- The gap between "safer TypeScript" and "safe by construction Rust" is the thesis

Anyone who wants to use RustScript in their TypeScript projects should — it genuinely
helps. For ecoPrimals, the conclusion is: use Rust.

---

*eastGate overwatch — Wave 136b. footPrint introduced as first primal composition target.*
