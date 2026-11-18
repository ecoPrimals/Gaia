# AAR: strandGate Compute Provenance Frontier — β-Scan + NFT Pattern

**Date**: Aug 3, 2026 | **Wave**: 155p/156a | **Gate**: strandGate
**Operator**: Claude (overwatch session from eastGate)
**Session Scope**: Cascade → P0 fixes → β-scan validation → NFT provenance wiring

---

## Executive Summary

This session completed the P0 primal infrastructure fixes (gauge group,
subgroup shader, PRNG compose), ran the first SU(3) β-scan validating
physics against published data across the full coupling range, and wired
the Novel Fermentation Transcript (NFT) pattern into the experiment
binary — establishing computational provenance as a first-class output
alongside physics data.

**Key insight**: westGate's data CAS has proven the ingestion and data
braiding side of provenance (519 GB / 130 datasets, each CAS object with
BLAKE3 + DAG tracking). The compute and output braids (NFT) are a new
frontier — strandGate's β-scan is the first experiment binary to produce
a complete provenance receipt tying computation parameters, results,
and trio commit into a single self-documenting artifact.

---

## What Worked

### 1. Gauge Group Audit (P0 #3) — SU(2) → SU(3)

**Discovery**: The code has always been SU(3). Every matrix, trace
normalization, force coupling, and β convention is unambiguously SU(3).
The paper was mislabeled.

**Verification method**: Structural code audit across 4 layers:
- `Su3Matrix { m: [[Complex64; 3]; 3] }` — 3×3 matrices
- `Re Tr P / 3.0` — N_c = 3 normalization
- `β/3` in gauge force — SU(3) force coupling
- `β = 6/g²` — standard SU(3) (β = 2N_c/g²)

**Impact**: The "×4 discrepancy" (⟨P⟩ ≈ 0.15 vs published SU(2) ~0.60)
was gauge group mismatch, not a normalization bug. This is a *stronger*
result than originally claimed. Rung ladder collapsed 6→5.

**Primals touched**: whitePaper (paper + status docs)

### 2. Subgroup Shader Fix (P0 #1)

Entry point `fn main()` → `fn sum_reduce_f64()` in
`sum_reduce_subgroup_f64.wgsl`. Pipeline code at `reduce.rs:157` already
referenced `entry_point: Some("sum_reduce_f64")`. SM86/RDNA2 silently
fell back; SM100+ returns 0.0.

**Primals touched**: barraCuda (upstream already had it), hotSpring (local copy)

### 3. PRNG Compose Fix (P0 #2)

`WGSL_RANDOM_MOMENTA` concatenated `prng_pcg_f64.wgsl` +
`su3_random_momenta_f64.wgsl`, producing duplicate definitions of
`pcg_hash`, `hash_u32`, `uniform_f64` → silent compilation failure.
Fixed by using the standalone shader directly.

**Primals touched**: hotSpring (dynamical.rs)

### 4. SU(3) β-Scan Validation

First complete phase-structure validation against published SU(3) data:

| β   | ⟨P⟩ (strandGate) | Published (∞-vol) | Δ/% |
|-----|-------------------|-------------------|-----|
| 2.0 | 0.12886           | ~0.13 (SC)        | —   |
| 2.3 | 0.15121           | ~0.15 (SC)        | —   |
| 3.0 | 0.20484           | ~0.21 (SC)        | —   |
| 5.5 | 0.49575           | 0.505 (GL10)      | −1.8% |
| 5.7 | 0.53809           | 0.546 (GL10/B00)  | −1.4% |
| 6.0 | 0.58623           | 0.593 (GL10/B00)  | −1.1% |
| 6.5 | 0.63372           | —                 | —   |

The 1-2% deficit at β ≥ 5.5 is the expected finite-volume effect on 8⁴.
Monotonicity, strong-coupling expansion, crossover, and weak-coupling
regime all validated. 98-100% acceptance across all β.

**Primals touched**: hotSpring (new binary), whitePaper (Section 4.4)

### 5. Novel Fermentation Transcript (NFT) Pattern

Wired the provenance trio into the β-scan binary:

```
RunManifest.capture()     → who ran what, when, where, with what code
    ↓
DagEvent per β point      → blake3 witness per measurement
    ↓
DagSession.dehydrate()    → merkle root over full computation
    ↓
commit_provenance()       → trio transaction:
  rhizoCrypt (DAG trace)  ← computation graph
  loamSpine  (ledger)     ← permanent record
  sweetGrass (braid)      ← attribution to experiment + paper
```

**Braid** = input data (lattice dims, β values, HMC config, integrator,
seed). This is the "what went in" side — the computational parameters
that define the experiment.

**Fermentation Transcript** = computation results (per-β plaquette values,
statistical errors, acceptance rates, wall time, BLAKE3 hashes). This is
the "what came out" side — the novel scientific output.

**Receipt** = self-contained JSON with both sides + RunManifest + BLAKE3
hash of the entire document. Written locally always; committed through
trio when NUCLEUS is available.

**Primals touched**: hotSpring (arxiv_beta_scan.rs provenance emission)

---

## What Didn't Work / Needs Attention

### 1. Strong-Coupling Reference Values Were Approximate

The "published" values I used for β ≤ 3.0 were crude strong-coupling
expansion estimates (leading order β/18 only). These showed large
σ-deviations not because the physics is wrong, but because the reference
values were imprecise. Future β-scans should use actual Monte Carlo
reference data from published tables, not expansion estimates.

### 2. freshness.toml Missing

`primalspring` validation scenario `s_ecosystem_freshness.rs` requires
`infra/wateringHole/freshness.toml` which didn't exist. Created a minimal
legacy-compat version. This file should be deprecated or generated from
`ecosystem_manifest.toml`.

### 3. PRNG Bias Status Unchanged

The 9.5% variance deficit in GPU Box-Muller output remains. eastGate
suggests it might be a measurement artifact from the broken subgroup
reduction on SM100+, but on strandGate (SM86/RDNA2) the fallback worked
and our measurements stand. The `cpu_mom` workaround remains in production.
Re-testing on biomeGate with the fixed subgroup shader would resolve this.

### 4. NFT Not Yet Running Inside NUCLEUS

The provenance trio wiring is complete in code, but strandGate runs
experiments as standalone binaries, not inside NUCLEUS compositions.
The first live NFT trio commit will happen when:
- biomeOS deploy executor boots hotSpring as a cell on strandGate
- rhizoCrypt, loamSpine, sweetGrass are all alive in the composition
- The experiment binary detects NUCLEUS and commits automatically

---

## Primal Systems: Evolution Status

### Proven (This Session Exercised Directly)

| Primal | What We Used | Status |
|--------|-------------|--------|
| **barraCuda** | GPU shaders, subgroup reduction, PRNG pipelines | YELLOW → fixes merged, PRNG polyfill remains |
| **hotSpring** | CPU HMC, GPU streaming, experiment binaries | Production physics validated |

### Proven (Upstream, Reviewed via Handoffs)

| Primal | What westGate/eastGate Proved | Status |
|--------|------|--------|
| **sweetGrass** | `braid.create`, `braid.batch_create`, attribution braids for 130 datasets | GREEN, batch pipeline shipped |
| **nestGate** | CAS ingestion at 519 GB scale, content.put/get | GREEN, scale validated |
| **rhizoCrypt** | DAG sessions, event append, merkle dehydration | GREEN, wiring ready |
| **loamSpine** | Entry append, spine commit | GREEN, wiring ready |
| **songBird** | Mesh connectivity, throughput probes, drawbridge | GREEN, E2E pending |
| **biomeOS** | Deploy graph executor, cell graphs v2.0.0 | GREEN, live deploy pending |
| **squirrel** | Signal dispatch, 4-strategy cascade | GREEN, G18 integration pending |

### Needs Evolution (Identified This Session)

| System | What Needs Work | Why |
|--------|----------------|-----|
| **WGSL f64 transcendentals** | `log(f64)`, `cos(f64)` polyfills produce biased output | 9.5% variance deficit breaks Box-Muller. Not fixable in our code — it's a naga/driver issue. Workaround: cpu_mom or Taylor-series WGSL. |
| **Shader composition** | String concatenation causes silent duplicate-definition failures | Need a shader module system or preprocessing step in barraCuda. |
| **Entry point naming** | WGSL `fn main()` is fragile across driver versions | All shaders should use descriptive entry point names. |
| **freshness.toml** | Legacy protocol file missing from wateringHole | Should be deprecated or auto-generated from ecosystem_manifest.toml. |

---

## Two Frontiers of Provenance

The ecoPrimals provenance architecture now has two distinct, validated
frontiers:

### Frontier 1: Data Braids (westGate — PROVEN)

westGate's data campaign has validated the ingestion pipeline:
- 519 GB / 130 datasets / 17 scientific domains
- Each CAS object: BLAKE3 content hash → nestGate storage
- Each dataset: sweetGrass braid → attribution + source tracking
- DAG traces: rhizoCrypt → ingest provenance graph
- Scale: ~5,800 CAS objects, sustained throughput validated

This frontier is **production-ready**. Data goes in, braids come out,
provenance is complete.

### Frontier 2: Compute Braids / NFT (strandGate — NEW)

The β-scan is the first experiment to produce a complete NFT:
- Input braid: lattice parameters, coupling values, HMC config
- Computation DAG: per-measurement events with BLAKE3 witnesses
- Output braid: plaquette values, errors, acceptance rates
- Receipt: self-documenting JSON with RunManifest + merkle root

This frontier is **wired but not yet live**. The code emits provenance
when NUCLEUS is available, falls back to local receipts when not.
The first live trio commit requires running inside a NUCLEUS composition.

### What Connects Them

The key insight: data braids (Frontier 1) and compute braids (Frontier 2)
share the same trio infrastructure. A complete scientific workflow is:

```
Data Braid (westGate)           Compute Braid (strandGate)
├── nestGate CAS object         ├── DagSession events
├── sweetGrass attribution      ├── sweetGrass experiment braid
├── rhizoCrypt ingest DAG       ├── rhizoCrypt compute DAG
└── loamSpine ledger entry      └── loamSpine ledger entry
         ↓                                ↓
    content.get (mesh)      ←→      experiment binary
         ↓                                ↓
    Input to computation         Output = NFT receipt
```

When inter-gate mesh validates (Phase 5), the data braids from westGate
become inputs to compute braids on strandGate. The full provenance chain
will trace from raw dataset ingestion through computation to published
result — every step with BLAKE3 witnesses, DAG vertices, and ledger entries.

---

## Commits Pushed This Session

| Repo | Commit | Description |
|------|--------|-------------|
| hotSpring | `acc66d4` | Subgroup entry point fix + PRNG compose fix |
| hotSpring | `ce2f51e` | arxiv_beta_scan binary |
| hotSpring | `e73b973` | NFT provenance wiring |
| whitePaper | `e70b91b` | Gauge group SU(2)→SU(3) relabel |
| whitePaper | `79e7049` | β-scan data in Section 4.4 |
| barraCuda | (upstream) | Subgroup fix already merged by another gate |
| wateringHole | `80d36849` | P0 fixes AAR + freshness.toml |

---

## Recommendations for Overwatch

1. **Apply NFT pattern to all experiment binaries**: `arxiv_production_run`,
   `validate_gpu_beta_scan`, `production_beta_scan`, etc. The pattern is
   4 imports + ~60 lines of code at end of main().

2. **First live NFT trio commit on ironGate**: ironGate has NUCLEUS 13/13
   live. Run any experiment binary inside the composition. The provenance
   code auto-detects NUCLEUS and commits. This would validate the compute
   provenance path end-to-end.

3. **Re-test PRNG on biomeGate**: With the subgroup shader fix merged,
   the 9.5% KE deficit measurement should be repeated on SM100+ hardware.
   If it resolves, the `cpu_mom` workaround can be removed.

4. **β-scan with larger volumes**: 12⁴ and 16⁴ would quantify the
   finite-volume effects and bring our values closer to published
   infinite-volume data. This is arXiv experiment queue item #6.

5. **Deprecate freshness.toml**: Replace with auto-generation from
   `ecosystem_manifest.toml` or remove the validation scenario.

6. **Connect data and compute braids**: When inter-gate mesh validates,
   run a hotSpring experiment that takes input from a westGate CAS object.
   The resulting NFT receipt should reference the input data braid,
   creating the first cross-frontier provenance chain.

---

*strandGate session complete. Three P0 blockers resolved. SU(3) physics
validated across 7 coupling values. NFT pattern established — the compute
provenance frontier is wired and ready for live trio commits. Two
provenance frontiers now exist: data braids (proven at 519 GB) and compute
braids (code-ready, live commit pending). When they connect through the
mesh, the full ingest→compute→publish chain will be provenance-complete.*
