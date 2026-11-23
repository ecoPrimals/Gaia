# tideGlass Phase 0 — Internal Assessment (Overwatch Response to northGate Review)

**Date**: Aug 16, 2026 | **Wave**: 157k | **From**: overwatch (eastGate)
**Responding to**: `TIDEGLASS_PHASE0_EXTERNAL_REVIEW_AUG16_2026.md` (northGate, via GitHub→Forgejo cascade)
**Type**: Internal gap analysis + FRAGO preparation

---

## The Core Finding: northGate Sees an Empty Field — We Have a Planted One

northGate's external review concludes tideGlass Phase 0 "does not exist" — no code, no repo, no scaffold. This is what the **outer membrane** (GitHub) shows: `protoKarya/tideGlass` is empty.

**Internally, on the inner membrane (Forgejo):**

| What northGate sees (GitHub) | What actually exists (Forgejo) |
|------------------------------|-------------------------------|
| `protoKarya/tideGlass` — empty | 9-crate Rust workspace, 220+ tests |
| "No code, no repo, no scaffold" | `tideglass-core`, `tideglass-rcl`, `tideglass-gps4drug`, `tideglass-molsearch`, `tideglass-screening`, `tideglass-octad`, `tideglass-nf`, `tideglass-bin`, `tideglass-cas-client` |
| Data tracing "NOT DONE" | Data tracing **DONE** — 482 GB on westGate ZFS, 7/7 modules federated, CAS braided |
| Paper lineage "NOT DONE" | Paper lineage **DONE** — Lamb 2006 → Chen 2017 → Cell 2026 documented |
| Dependency graph "NOT DONE" | Rust dependency graph **EXISTS** — ecosystem composition validated (primalSpring scenario) |
| Zenodo ingestion "NOT DONE" | GPS platform scoring data **ON westGate CAS** (~1.5 GB, 8 braided files, JSON converted) |
| Environment mapping "NOT DONE" | ✅ **Genuinely NOT DONE** — `gps_env.yml` Python 2/3 boundaries not mapped |
| Model weights "NOT DONE" | ✅ **Genuinely NOT DONE** — PyTorch checkpoints from Zenodo not loaded |

**northGate's assessment is correct for the outer membrane surface.** But the actual work is far more advanced than the external review suggests.

---

## What's Actually Done (Not Visible to northGate)

### 1. Rust Codebase (protists/tideGlass/)

9-crate workspace on Forgejo (`protoKarya/tideGlass`). Key implementations:

| Crate | Capability | Status |
|-------|-----------|--------|
| `tideglass-core` | Weighted KS enrichment, RGES, permutation p-values | **Implemented + tested** |
| `tideglass-rcl` | Cell-line SNR selection (RCL proxy) | **Scaffold + tests** |
| `tideglass-gps4drug` | Linear-regression structure→expression predictor | **Scaffold** (no DL weights) |
| `tideglass-molsearch` | MCTS molecular optimization | **Scaffold + tests** |
| `tideglass-screening` | Drug screening pipeline | **Scaffold** |
| `tideglass-octad` | OCTAD integration | **Scaffold** |
| `tideglass-nf` | NF scoring module | **Scaffold** |
| `tideglass-bin` | CLI + CAS client + petalTongue viz scenes | **Wired** (5 viz scenes) |
| `tideglass-cas-client` | Live nestGate CAS client via Neural API | **Wired + tested** |

### 2. Data Estate (westGate ZFS)

| Dataset | Size | Status |
|---------|------|--------|
| LINCS L1000 | ~20 GB | **Federated**, CAS braided |
| ChEMBL 37 | ~15 GB | **Federated**, CAS braided |
| GPS platform scoring | ~1.5 GB | **Federated**, 8 files braided, JSON converted (103 MB CAS) |
| NF Data Portal | 658 files, 666 MB | **Federated**, CAS braided |
| AlphaFold structures | ~14.76 GiB (Phase A) | **Ingested** (246M structures total) |
| GEO expression data | Various | **In ZFS** |
| Model weights (Zenodo) | ~500 MB | **NOT LOADED** — raw tarballs not inventoried |

### 3. Ecosystem Wiring

| Component | Status |
|-----------|--------|
| Deploy graph (`tideglass_cell.toml`) | **Written** — 14-primal westGate NUCLEUS cell boot |
| Guidestone graph (`tideglass_guidestone.toml`) | **Written** — 7-module validation composition |
| Composition routing scenario (primalSpring) | **Validated** — barraCuda, petalTongue, songBird bonds |
| songBird drawbridge bonds | **Registered** — LINCS, GEO, ChEMBL, NF portal paths |
| Caddy pharma API proxy | **Config present** |
| ecosystem_manifest.toml entry | **Present** — ironGate assigned, westGate data |

### 4. Documentation

| Document | Location | Status |
|----------|----------|--------|
| Phase 0 checklist | `protists/tideGlass/specs/PHASE_0_CHECKLIST.md` | **Mixed** — header says archived; Zenodo/RGES Python steps unchecked |
| Module specs (7 modules) | `protists/tideGlass/specs/MODULE_SPECS.md` | **Complete** |
| Data access paths | `protists/tideGlass/specs/DATA_ACCESS.md` | **Documented** |
| DATA_MANIFEST.md | `whitePaper/attsi/.../gonzales/gps/` | **Complete** — fetch commands for all sources |
| VIABILITY.md | `whitePaper/attsi/.../gonzales/gps/` | **Analysis** — Python 2 debt, 10-year stack |
| LINEAGE.md | `whitePaper/attsi/.../gonzales/gps/` | **Complete** — 20-year paper chain |

### 5. Adjacent Validated Springs

| Spring | What it provides | Validated | Wired to tideGlass |
|--------|-----------------|-----------|---------------------|
| wetSpring (Gonzales tracks) | ChEMBL JAK panel, pharmacology IPC | Yes (40/40) | **No** — shares data domain, no composition handshake |
| healthSpring MATRIX | Fajgenbaum/Anderson drug scoring | Yes (233/233) | **No** — adjacent ChEMBL/LINCS domain, not composed |
| neuralSpring | safetensors weight loader, MCTS, expression models | Yes (1518+ tests) | **No** — generic ML, not GPS-specific |

---

## What's Genuinely Not Done

These are the items northGate correctly identified, and they remain the true Phase 0 gaps:

### 1. Zenodo Tarball Inventory (Minutes → Hours)
- v5 (713 MB) and v6 (840 MB) tarballs exist as fetch targets in `DATA_MANIFEST.md`
- Raw files **not unpacked and inventoried** on any gate
- GPS scoring JSON already on CAS, but the **full Python codebase from Zenodo has not been inspected**

### 2. `gps_env.yml` Environment Mapping (1 Day)
- Python 2 vs 3 boundaries **not mapped**
- `VIABILITY.md` identifies this as the key technical risk
- No Conda environment has been constructed or tested on any gate

### 3. Python RGES Baseline Reproduction (1-2 Days)
- Rust `tideglass-core/enrichment.rs` implements RGES — but it's **not validated against the Python baseline**
- Chen 2017 reports r ≥ 0.52 correlation — this threshold is in specs but **not tested**
- No `validation/expected/` fixtures exist

### 4. PyTorch Model Weight Loading (1 Day)
- `gps4drug/prediction.rs` has a linear scaffold — **no DL weight loading**
- neuralSpring has a generic safetensors loader but **not wired to GPS checkpoints**
- ~500 MB of model weights referenced but never fetched

### 5. Phase Numbering + Path Reconciliation (Hours)
- Internal `CONTEXT.md` says Phase 4 (Package) while external docs say Phase 0 not started
- `tideglass-gps-validation.toml` references `gardens/tideGlass` (stale) — code is at `protists/tideGlass`
- `gps_to_json.py` conversion ran once but script is now deprecated/broken in fossil record

---

## Revised Phase 0 Estimate (Internal View)

northGate estimated 5-7 focused days from the **external** view (assuming nothing exists).

From the **internal** view, with existing Rust scaffold + data estate + ecosystem wiring:

| Task | northGate Estimate | Internal Reality | Actual Remaining |
|------|-------------------|------------------|-----------------|
| Download Zenodo | Minutes | GPS scoring already on CAS | **Verify completeness** (hours) |
| Inventory files | 1-2 days | Rust crates exist, MODULE_SPECS done | **Reconcile Python ↔ Rust** (1 day) |
| Map `gps_env.yml` | 1 day | Not done | **1 day** (genuine gap) |
| Identify Fortran | Hours | Likely none per Cell 2026 | **Hours** |
| Trace data deps | Verification only | **DONE** (482 GB, 7/7 federated) | **Verify CAS hashes** (hours) |
| Paper lineage | None | **DONE** | **None** |
| Dependency graph | 1-2 days | Rust graph exists, composition validated | **Map Python→Rust gaps** (1 day) |
| Python baseline reproduction | Not in northGate estimate | **NOT DONE** | **1-2 days** (key validation) |
| Weight loading | Not in northGate estimate | **NOT DONE** | **1 day** |

**Revised total: 3-5 focused days** (2-3 days shorter than northGate's estimate, but with 2 tasks they didn't account for: Python baseline + weight loading).

---

## What northGate Should Focus On (FRAGO Preparation)

northGate's role is the **external surface** — GitHub, sporePrint, public-facing documentation, reviewer contacts. Their review was excellent for identifying the external gap. Their FRAGO should focus on:

### Track A: External Surface Catch-Up (northGate owns)
1. **Push tideGlass existence to GitHub** — mirror the Forgejo state to `protoKarya/tideGlass` on GitHub (or create a public-facing summary)
2. **Update sporePrint** — tideGlass product page needs to reflect 220+ tests, 9 crates, data estate
3. **Prepare Gonzales reactivation email** — draft based on actual internal state, not Phase 0 "not started"
4. **arXiv Rung 1 reviewer send** — this is northGate's parallel track, independent of tideGlass

### Track B: Internal Phase 0 Completion (inner membrane teams own)
1. **westGate**: Verify Zenodo tarball completeness against CAS, confirm data hashes
2. **westGate or strandGate**: Build `gps_env.yml` Conda environment, map Python 2/3 boundaries
3. **westGate**: Run Python RGES baseline, compare against Rust `tideglass-core` r ≥ 0.52
4. **ironGate or strandGate**: Wire neuralSpring safetensors loader to GPS model weights
5. **eastGate (primalSpring)**: Reconcile `PHASE_0_CHECKLIST.md` — mark what's actually done

### Track C: Composition Wiring (downstream)
1. Wire wetSpring Gonzales pharmacology → tideGlass screening module
2. Wire healthSpring MATRIX → tideGlass drug scoring
3. Activate helixVision gene expression module (forced by tideGlass Module 3)
4. Build tideGlass → primal composition graph (which primal serves which module)

---

## Key Insight for the FRAGO

> **northGate sees Phase 0 as archaeology of an unknown codebase.**
> **Internally, Phase 0 is reconciliation of a partially-built Rust replacement against the Python original.**
>
> The archaeology IS largely done. What remains is validation: does our Rust implementation
> reproduce the Python results? And does the data estate we've already federated match
> the Zenodo artifact we haven't fully unpacked?

This reframe changes the FRAGO from "start from scratch" to "validate what we've built."

---

*Internal assessment — Wave 157k. The external reviewer saw an empty field because the
inner membrane doesn't push to the outer membrane by default. That's by design (K-Derm
topology). But it means the FRAGO needs to bridge the gap: update the external surface
to reflect internal reality, then focus northGate on what they uniquely own (external
contacts, publications, GitHub surface) while inner membrane teams complete the genuine
Phase 0 gaps (Python baseline, weight loading, environment mapping).*
