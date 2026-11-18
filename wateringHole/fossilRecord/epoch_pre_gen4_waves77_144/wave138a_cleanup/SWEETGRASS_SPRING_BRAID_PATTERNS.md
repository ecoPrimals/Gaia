# sweetGrass Spring Braid Patterns

> Per-spring attribution braid patterns for science experiments.
> Braids tie computation, data, and contributors into verifiable
> reproducibility artifacts.

**Date**: May 5, 2026
**Version**: 1.0.0
**Depends on**: `SPRING_PROVENANCE_TRIO_INTEGRATION_PATTERN.md` v1.0
**License**: AGPL-3.0-or-later

---

## What a Braid Is

A sweetGrass **braid** is a signed JSON-LD/W3C PROV-O document that links:
- **Agents** — who contributed (people, springs, primals, AI models)
- **Activities** — what computation was performed (experiments, analyses)
- **Entities** — what data was produced (results, figures, datasets)

The braid is created at the end of a provenance session after:
1. **rhizoCrypt** tracks the ephemeral DAG of events (session → steps → merkle root)
2. **loamSpine** commits the session to the permanent ledger (append-only spine)
3. **sweetGrass** weaves the attribution braid (agents + activities + entities)

```
rhizoCrypt (DAG)  →  loamSpine (ledger)  →  sweetGrass (braid)
   session              commit                attribution
   events               spine entry           W3C PROV-O
   merkle root          content hash          signed JSON-LD
```

The braid IS the reproducibility artifact. It answers: "who did what, with
what data, producing what result, and can we verify it?"

---

## Braid Anatomy

```json
{
  "braid_id": "braid-2026-05-05-hotspring-qcd-001",
  "commit_ref": "loamspine-entry-abc123",
  "merkle_root": "blake3:deadbeef...",
  "agents": [
    {
      "did": "did:key:z6Mk...",
      "role": "author",
      "contribution": 0.7,
      "spring": "hotSpring",
      "description": "Lattice QCD simulation"
    },
    {
      "did": "did:key:z6Mk...",
      "role": "compute",
      "contribution": 0.2,
      "primal": "barraCuda",
      "description": "GPU tensor operations via IPC"
    },
    {
      "did": "did:key:z6Mk...",
      "role": "storage",
      "contribution": 0.1,
      "primal": "NestGate",
      "description": "Gauge configuration archival"
    }
  ],
  "activities": [
    {"id": "hmc-thermalization", "type": "computation", "method": "HMC"},
    {"id": "measurement", "type": "analysis", "observable": "plaquette"}
  ],
  "entities": [
    {"id": "gauge-config-1024", "type": "dataset", "hash": "blake3:..."},
    {"id": "plaquette-mean", "type": "result", "value": 0.593}
  ]
}
```

---

## Per-Spring Braid Patterns

---

### hotSpring — QCD Simulation Braids

**Session type**: `QcdSimulation`

**Agents**:
- `hotSpring` (author) — simulation setup, parameter selection
- `barraCuda` (compute) — GPU tensor operations, SU(3) matmul, df64
- `coralReef` (shader) — QCD-specific WGSL compilation
- `toadStool` (dispatch) — GPU fleet partitioning
- `NestGate` (storage) — gauge configuration cache
- Human researcher (supervisor) — parameter review, publication decision

**Activities**:
- `hmc-thermalization` — HMC trajectory with specified trajectory length
- `hmc-measurement` — Observable measurement on thermalized configurations
- `gradient-flow` — Wilson/Symanzik flow at specified flow times
- `continuum-extrapolation` — Lattice spacing → continuum limit

**Entities**:
- Gauge configurations (content-addressed by BLAKE3 hash)
- Plaquette measurements, Polyakov loops, Wilson loops
- Gradient flow observables (t²E, w₀)
- Nuclear EOS curves, phase diagram data points

**Reproducibility claim**: Given the same lattice parameters, RNG seed, and
NUCLEUS composition, the simulation produces identical gauge configurations
(bit-for-bit via df64) with the same merkle root.

**Paper connection**: Each baseCamp paper (Chuna gradient flow, Murillo lattice
QCD, etc.) maps to a braid template. The braid proves the computation in the
paper was performed by this NUCLEUS composition with these inputs.

---

### wetSpring — Sample Provenance Braids

**Session type**: `SampleAnalysis`

**Agents**:
- `wetSpring` (author) — sample processing, analysis pipeline
- `barraCuda` (compute) — spectral analysis, statistical clustering
- `NestGate` (storage) — specimen/sensor time-series
- `Squirrel` (inference) — AI triage, anomaly detection
- Field collector (contributor) — sample collection, metadata
- Lab technician (contributor) — sample preparation

**Activities**:
- `sample-collection` — Field collection with GPS, timestamp, conditions
- `spectral-analysis` — Mass spec / IR / Raman deconvolution
- `biodiversity-assessment` — PCoA, Shannon/Simpson, abundance profiling
- `drug-screening` — Dose-response curves, IC50 determination
- `anderson-localization` — Disorder → transport analysis

**Entities**:
- Raw sensor data streams (content-addressed)
- Spectral peaks, deconvolution results
- Diversity indices, ordination coordinates
- Drug response curves, potency estimates
- Anderson localization parameters (disorder strength, mobility edge)

**Reproducibility claim**: The complete chain from field sample to analytical
result is traceable. Each spectral deconvolution, each diversity calculation,
each drug screening result links back to the raw sample data and the exact
NUCLEUS composition that processed it.

**Paper connection**: Gonzales pharmacology braids tie drug screening to
ADDRC samples. Anderson atlas braids tie localization analysis to biological
disorder measurements. Sub-thesis braids link the full analysis pipeline.

---

### neuralSpring — Model Provenance Braids

**Session type**: `InferenceSession` / `TrainingRun`

**Agents**:
- `neuralSpring` (author) — model architecture, training setup
- `barraCuda` (compute) — transformer shaders, matmul, attention
- `coralReef` (shader) — ML-specific WGSL compilation
- `Squirrel` (routing) — inference request routing
- `NestGate` (storage) — model weight cache
- Training data curator (contributor)

**Activities**:
- `model-training` — Training run with hyperparameters, dataset, epochs
- `inference-session` — Token generation with prompt, temperature, model
- `attention-analysis` — Layer-by-layer attention pattern extraction
- `weight-analysis` — Anderson localization in weight matrices

**Entities**:
- Model weights (content-addressed by BLAKE3)
- Training loss curves, validation metrics
- Generated tokens, attention matrices
- Weight distribution statistics, localization lengths

**Reproducibility claim**: A model's training run is fully traceable from
dataset to final weights. Each inference result links to the specific model
weights, prompt, and NUCLEUS composition that produced it.

**Paper connection**: Weight Hamiltonians paper braids tie spectral analysis
of weight matrices to the models and training procedures. Information
propagation paper braids tie Anderson framework to neural network analysis.

---

### healthSpring — Clinical Provenance Braids

**Session type**: `ClinicalAssessment` / `DrugAnalysis`

**Agents**:
- `healthSpring` (author) — clinical analysis pipeline
- `barraCuda` (compute) — PK/PD modeling, biostatistics
- `NestGate-A` (storage, Tower A) — patient data custody
- `NestGate-B` (storage, Tower B) — model/analytics cache
- `BearDog` (security) — ionic bond enforcement, data egress control
- Clinician (supervisor) — treatment decision
- Patient (subject) — de-identified via ionic fence

**Activities**:
- `pk-analysis` — Pharmacokinetic modeling (Cmax, AUC, t½)
- `microbiome-assessment` — 16S sequencing, PCoA, diversity
- `biosignal-monitoring` — ECG/EEG/EMG continuous acquisition
- `risk-assessment` — Composite clinical risk scoring
- `drug-interaction-check` — Multi-drug interaction matrix

**Entities**:
- De-identified patient metrics (via ionic fence — raw data never leaves Tower A)
- PK parameters, dose-response curves
- Microbiome ordination, diversity indices
- Biosignal waveforms, HRV spectra
- Clinical risk scores, treatment recommendations

**Reproducibility claim**: The clinical analysis is traceable from de-identified
input to treatment recommendation, with the ionic fence guaranteeing that raw
patient data never appears in the braid. The braid proves computation integrity
without exposing protected health information.

**Unique pattern**: Dual-tower braids — Tower A produces a braid for data
custody events (what was accessed, by whom, under what ionic bond). Tower B
produces a braid for analytics events (what was computed, with what model).
The two braids are linked but Tower A's braid contains no raw data.

---

### airSpring — Environmental Compliance Braids

**Session type**: `FieldSurvey` / `ComplianceReport`

**Agents**:
- `airSpring` (author) — ecological analysis pipeline
- `barraCuda` (compute) — PDE solvers, FFT, statistics
- `NestGate` (storage) — IoT sensor time-series, model outputs
- Field sensor network (contributor) — automated data collection
- Agronomist (supervisor) — irrigation/management decisions

**Activities**:
- `et0-calculation` — Evapotranspiration modeling
- `soil-moisture-mapping` — Spatial interpolation from sensor grid
- `yield-prediction` — Crop yield model with inputs and outputs
- `microbiome-survey` — Soil 16S diversity assessment
- `compliance-reporting` — Environmental regulation verification

**Entities**:
- Sensor readings (timestamped, GPS-located)
- ET0 maps, soil moisture grids
- Yield predictions with confidence intervals
- Microbiome diversity indices
- Compliance certificates

**Reproducibility claim**: Environmental measurements are traceable from sensor
to compliance report. Each ET0 calculation, each yield prediction links to the
raw sensor data and the NUCLEUS composition that processed it. Regulatory
auditors can verify the entire chain.

---

### groundSpring — Calibration Traceability Braids

**Session type**: `CalibrationEvent` / `GeologicalSurvey`

**Agents**:
- `groundSpring` (author) — measurement science pipeline
- `barraCuda` (compute) — FFT, matrix decomposition, statistical tests
- `NestGate` (storage) — geospatial data, calibration records
- Measurement instrument (contributor) — hardware serial, calibration state
- Metrologist (supervisor) — calibration approval

**Activities**:
- `instrument-calibration` — Reference standard comparison
- `seismic-survey` — Frequency analysis of seismic signals
- `inverse-problem` — Parameter estimation from observations
- `quality-assessment` — Anderson-Darling, statistical acceptance tests

**Entities**:
- Calibration reference values (NIST-traceable where applicable)
- Seismic spectra, geological maps
- Estimated parameters with uncertainty bounds
- Quality test results (pass/fail with p-values)

**Reproducibility claim**: Metrological traceability from instrument calibration
through measurement to derived result. The braid proves the measurement chain
is unbroken and each derived value links to calibrated instruments.

---

### ludoSpring — Game Session Braids

**Session type**: `GameSession` / `ScienceExperiment`

**Agents**:
- `ludoSpring` (author) — game logic, science validation
- `barraCuda` (compute) — game math (Fitts, noise, physics)
- `coralReef` (shader) — game WGSL (Perlin, WFC)
- `Squirrel` (inference) — AI Dungeon Master narration
- `petalTongue` (render) — scene presentation
- `NestGate` (storage) — session persistence
- Player (subject) — interaction data

**Activities**:
- `game-session` — Play session with tick-by-tick state
- `engagement-measurement` — Fitts/Hick law validation
- `pcg-generation` — Procedural content with quality metrics
- `ai-narration` — Dungeon Master response generation
- `parity-validation` — Python→Rust→IPC composition verification

**Entities**:
- Game states (per-tick snapshots, content-addressed)
- Engagement metrics (movement times, decision times)
- PCG artifacts (maps, encounters, narratives)
- Parity test results (library vs IPC values)

**Reproducibility claim**: A game session is fully reproducible — given the
same seed, player inputs, and NUCLEUS composition, the session produces
identical state evolution. The parity validation braid proves that the IPC
composition matches the library baseline.

**Reference implementation**: ludoSpring's `ipc/provenance/{rhizocrypt.rs,
loamspine.rs, sweetgrass.rs}` is the ecosystem exemplar for per-trio-primal
braid wiring.

---

## ABG Connection

The ABG (Accelerated Bioinformatics Group) capability audit identified 6
external proposals that map to NUCLEUS compositions. Each proposal's workflow
would produce braids following these spring patterns:

| ABG Proposal | Closest Spring Pattern | Braid Type |
|-------------|----------------------|------------|
| Mark's MD simulation | hotSpring QCD + wetSpring Anderson | Simulation braid |
| Jeremy's scRNA-seq | wetSpring sample + healthSpring clinical | Analysis braid |
| Jeremy's HS-Crohn's | healthSpring clinical + wetSpring biodiversity | Clinical braid |
| bake3011's AlphaFold | neuralSpring model + hotSpring MD | Model provenance braid |
| bake3011's TMS/Huntington's | healthSpring biosignal + neuralSpring inference | Clinical braid |
| Mark's PTP expression | wetSpring sample + healthSpring drug | Analysis braid |

External collaborators using NUCLEUS compositions automatically get provenance
braids — the system produces reproducibility artifacts as a structural property,
not a social agreement.

---

## Adoption Checklist (per spring)

From `SPRING_PROVENANCE_TRIO_INTEGRATION_PATTERN.md`:

- [ ] Create `ipc/provenance/` directory with per-primal modules
- [ ] `rhizocrypt.rs` — session create, event append, dehydration trigger
- [ ] `loamspine.rs` — session commit, spine entry
- [ ] `sweetgrass.rs` — braid create with domain-specific agent list
- [ ] Wire session lifecycle into domain handlers (begin/record/complete)
- [ ] Define domain-specific agent roles (from patterns above)
- [ ] Define domain-specific activity types
- [ ] Define domain-specific entity types with BLAKE3 content addressing
- [ ] Ensure graceful degradation (domain logic never fails on provenance unavailability)
- [ ] Test with provenance trio unavailable (degradation path)
- [ ] Test with full NUCLEUS (happy path — braid created)
- [ ] Create deploy graph with provenance trio nodes

### Current Adoption Status

| Spring | `ipc/provenance/` | rhizoCrypt | loamSpine | sweetGrass | Braid Creation |
|--------|-------------------|-----------|-----------|------------|----------------|
| **ludoSpring** | Per-primal modules | Wired | Wired | Wired | **Operational** |
| **wetSpring** | `provenance.rs` + `sweetgrass.rs` | Wired | Partial | Partial | **Partial** |
| **airSpring** | `provenance.rs` | Referenced | Referenced | Not wired | **Not operational** |
| **healthSpring** | Via `ecoPrimal/src/ipc/` | Referenced | Referenced | Not wired | **Not operational** |
| **hotSpring** | Via `composition.rs` | Referenced | Referenced | Not wired | **Not operational** |
| **neuralSpring** | Via `ipc_dispatch.rs` | Referenced | Not wired | Not wired | **Not operational** |
| **groundSpring** | Not present | Not wired | Not wired | Not wired | **Not operational** |

---

## Downstream Consumers: Ferment Transcript Pattern

Springs that produce braids may hand them to **guideStone artifacts**
(gardens) for portable provenance. lithoSpore is the first consumer of
this pattern: it stores upstream braid IDs in `data.toml` and verifies
the chain when online. The braid must be **self-describing** — a
guideStone on a USB stick cannot query sweetGrass, but it can document
the braid ID and verify it when reconnected.

See `handoffs/LITHOSPORE_FERMENT_TRANSCRIPT_BRAID_HANDOFF_MAY17_2026.md`
for the contract between upstream springs and lithoSpore.

---

**License**: AGPL-3.0-or-later
