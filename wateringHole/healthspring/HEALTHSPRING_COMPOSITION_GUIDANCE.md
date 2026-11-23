# healthSpring — Composition Guidance for Springs and Primals

**Date**: May 28, 2026
**From**: healthSpring V65a (ironGate — post-primordial)
**License**: AGPL-3.0-or-later

---

## Purpose

This document describes how healthSpring's capabilities can be leveraged:
1. **Solo** — what healthSpring offers as a standalone primal
2. **Trio combos** — healthSpring composed with the Memory & Attribution Stack (rhizoCrypt + sweetGrass + loamSpine)
3. **Wider primal compositions** — healthSpring in NUCLEUS, cross-spring, and multi-primal pipelines

Each primal in the ecosystem should write an equivalent document. No primal knows about another at compile time — all composition happens at runtime via capability-based discovery through biomeOS.

---

## 1. healthSpring Solo — Self-Knowledge Capabilities

healthSpring is a health science compute primal. It owns the `health` domain and advertises 88 capabilities across 10 science domains, plus infrastructure and composition health. Post-primordial deployment on ironGate — plasmidBin-only, NUCLEUS operational, Songbird TCP federation on port 7700.

### Science Capabilities (What We Compute)

| Domain | Count | Capabilities | Use Cases |
|--------|-------|-------------|-----------|
| **PK/PD** | 14 | `science.pkpd.hill_dose_response`, `one_compartment_pk`, `two_compartment_pk`, `pbpk_simulate`, `population_pk`, `michaelis_menten_nonlinear`, `allometric_scale`, `auc_trapezoidal`, `nlme_foce`, `nlme_saem`, `nca_analysis`, `cwres_diagnostics`, `vpc_simulate`, `gof_compute` | Drug dosing, pharmacokinetic simulation, population modeling, nonlinear mixed-effects, visual predictive checks |
| **Microbiome** | 13 | `science.microbiome.shannon_index`, `simpson_index`, `pielou_evenness`, `chao1`, `anderson_gut`, `colonization_resistance`, `fmt_blend`, `bray_curtis`, `antibiotic_perturbation`, `scfa_production`, `gut_brain_serotonin`, `qs_gene_profile`, `qs_effective_disorder` | Gut diversity, C. difficile resistance, FMT optimization, quorum sensing, short-chain fatty acid modeling |
| **Biosignal** | 8 | `science.biosignal.pan_tompkins`, `hrv_metrics`, `ppg_spo2`, `eda_analysis`, `eda_stress_detection`, `arrhythmia_classification`, `fuse_channels`, `wfdb_decode` | ECG QRS detection, heart rate variability, pulse oximetry, electrodermal stress, multi-channel fusion |
| **Endocrine** | 5 | `science.endocrine.testosterone_pk`, `trt_outcomes`, `population_trt`, `hrv_trt_response`, `cardiac_risk` | TRT pharmacokinetics, population outcomes, cardiac risk modeling |
| **Diagnostic** | 3 | `science.diagnostic.assess_patient`, `population_montecarlo`, `composite_risk` | Multi-track patient assessment, Monte Carlo population simulation, integrated risk scoring |
| **Clinical** | 3 | `science.clinical.trt_scenario`, `patient_parameterize`, `risk_annotate` | Clinical decision support, scenario generation |
| **Comparative** | 3 | `science.comparative.cross_species_pk`, `canine_il31`, `canine_jak1` | Cross-species pharmacokinetics, veterinary dermatology (IL-31/JAK1 inhibitors) |
| **Discovery** | 4 | `science.discovery.matrix_score`, `hts_analysis`, `compound_library`, `fibrosis_pathway` | Drug discovery screening, HTS hit triage, compound library analytics, fibrosis pathway modeling |
| **Toxicology** | 3 | `science.toxicology.biphasic_dose_response`, `toxicity_landscape`, `hormetic_optimum` | Hormesis biphasic response, toxicity landscape mapping, hormetic zone optimization |
| **Simulation** | 2 | `science.simulation.mechanistic_fitness`, `ecosystem_simulate` | Mechanistic population fitness, ecosystem dynamics simulation |

### Infrastructure Capabilities (How We Coordinate)

| Capability | Description |
|-----------|-------------|
| `composition.health_health` | Composition health per `compositions/COMPOSITION_HEALTH_STANDARD.md` (returns `healthy`, `deploy_graph`, `subsystems`) |
| `capability.list` | Advertise all capabilities with operation dependencies and cost estimates |
| `compute.offload` | Delegate GPU-eligible work to toadStool via Node Atomic |
| `compute.shader_compile` | Coordinate shader compilation via coralReef |
| `model.inference_route` | Route inference requests via Squirrel |
| `data.fetch` | Resolve datasets through NestGate three-tier fetch |
| `primal.forward` | Forward cross-domain requests to discovered primals |
| `primal.discover` | Runtime capability-based discovery of peer primals |
| `health.check` / `health.liveness` / `health.readiness` | Health triad per `DEPLOYMENT_VALIDATION_STANDARD.md` |
| `provenance.begin/record/complete/status` | Session-scoped provenance tracking |

### Solo Leverage Patterns

**For any spring or primal** that needs health science compute:

```
capability.call("science.pkpd.hill_dose_response", {
  "concentration": 10.0, "ic50": 5.0, "hill_n": 2.0, "e_max": 100.0
})
→ { "response": 80.0 }
```

- **Drug interaction modeling**: Any primal computing molecular interactions can delegate dose-response curves
- **Physiological monitoring**: Any biosignal-producing device can route through Pan-Tompkins QRS detection and HRV analysis
- **Risk scoring**: Any clinical workflow can invoke `assess_patient` for multi-track diagnostic integration
- **Population simulation**: Any epidemiological model can use `population_montecarlo` for Monte Carlo patient cohorts

---

## 2. Trio Combos — healthSpring + Memory & Attribution Stack

The Memory & Attribution Stack (rhizoCrypt + sweetGrass + loamSpine) provides ephemeral memory, attribution, and permanent records. healthSpring's science capabilities gain powerful new properties when composed with this stack.

### healthSpring + rhizoCrypt (Ephemeral Memory)

| Composition | Pattern | Example |
|------------|---------|---------|
| **Clinical session tracking** | `provenance.begin` → run science ops → `dag.append` per computation → `provenance.complete` | Track every PK simulation, diversity calculation, and risk score in a patient encounter as a DAG of content-addressed events |
| **Iterative dosing optimization** | `dag.session.create` → simulate dose 1 → `dag.append` → adjust → simulate dose 2 → `dag.append` → compare → `dag.session.commit` | Find optimal dose by recording each simulation attempt as a DAG vertex, enabling rollback and comparison |
| **Multi-patient workspace** | `dag.session.create` per patient → parallel `assess_patient` calls → `dag.merge` → aggregate statistics | Process patient cohorts in isolated sessions, merge results into a single analysis DAG |

### healthSpring + sweetGrass (Attribution)

| Composition | Pattern | Example |
|------------|---------|---------|
| **Reproducible science** | Each `science.*` call records attribution (model version, parameters, barraCuda version) → sweetGrass braid | Every Hill dose-response curve is traceable to exact model, exact code commit, exact parameters |
| **Multi-contributor analysis** | Clinician A runs microbiome → Specialist B runs endocrine → sweetGrass tracks roles and shares | Fair attribution in collaborative patient assessment workflows |
| **Regulatory audit trail** | `provenance.record` + sweetGrass braid → W3C PROV-O export | Generate standards-compliant provenance for FDA/EMA submission |

### healthSpring + loamSpine (Permanence)

| Composition | Pattern | Example |
|------------|---------|---------|
| **Permanent patient records** | `assess_patient` → rhizoCrypt session → `dehydrate` → loamSpine entry with inclusion proof | Patient's diagnostic assessment becomes an immutable, cryptographically signed record |
| **Loam Certificates for health data** | `composite_risk` score → loamSpine certificate | Issue verifiable health credentials (e.g., "cardiac risk < 5% as of 2026-03-17") |
| **Long-term outcome tracking** | Monthly `assess_patient` → loamSpine entries → trend analysis over permanent history | Track treatment efficacy across months/years with tamper-evident records |

### Full Trio: healthSpring + rhizoCrypt + sweetGrass + loamSpine

**Pattern: Provenance-Tracked Clinical Decision Pipeline**

```
1. rhizoCrypt: dag.session.create("patient_encounter_42")
2. healthSpring: science.pkpd.one_compartment_pk → PK curve
3. rhizoCrypt: dag.append(pk_result)
4. healthSpring: science.microbiome.shannon_index → diversity score
5. rhizoCrypt: dag.append(diversity_result)
6. healthSpring: science.diagnostic.assess_patient → composite risk
7. rhizoCrypt: dag.append(assessment)
8. sweetGrass: braid.create(session_dag, attribution=[clinician, model_v34])
9. loamSpine: entry.append(assessment, braid, inclusion_proof)
10. rhizoCrypt: dag.session.commit → permanent record
```

Every step is content-addressed, attributed, and permanently auditable.

---

## 3. Wider Primal Compositions

### healthSpring + barraCuda (GPU Math)

| Composition | What Happens |
|------------|-------------|
| **Hill dose-response sweep** | healthSpring prepares parameters → barraCuda `HillFunctionF64` GPU op → 100K concentrations in parallel |
| **Population PK Monte Carlo** | healthSpring generates patient cohort → barraCuda `PopulationPkF64` → GPU-parallel AUC computation |
| **Diversity batch** | healthSpring prepares community matrices → barraCuda `DiversityFusionGpu` → batch Shannon/Simpson on GPU |
| **Michaelis-Menten batch PK** | healthSpring ODE parameters → barraCuda Euler ODE per patient → GPU-parallel nonlinear PK |

**Absorption flow**: healthSpring writes local WGSL shaders → validates parity with CPU → hands off to barraCuda for upstream absorption → leans on upstream ops. Current Tier B candidates: `michaelis_menten_batch_f64.wgsl`, `scfa_batch_f64.wgsl`, `beat_classify_batch_f64.wgsl`.

### healthSpring + toadStool (Compute Orchestration)

| Composition | What Happens |
|------------|-------------|
| **GPU job dispatch** | `compute.dispatch.submit` with workload descriptor → toadStool routes to best GPU/CPU/NPU |
| **Precision routing** | `metalForge::PrecisionRouting` → f64 on Titan V, df64 on consumer GPUs, f32 fallback |
| **Multi-device pipeline** | Population PK on GPU → diversity on NPU → risk scoring on CPU, orchestrated by toadStool |
| **Streaming results** | `execute_streaming` → petalTongue progress bar for long Monte Carlo runs |

### healthSpring + coralReef (Shader Compilation)

| Composition | What Happens |
|------------|-------------|
| **Sovereign compute** | healthSpring WGSL → coralReef compiles to native SASS/ISA binary → no vendor SDK needed |
| **f64 transcendentals** | `strip_f64_enable()` workaround replaced by coralReef's full f64 lowering (DFMA on NVIDIA, native on AMD) |
| **Multi-GPU** | `shader.compile.wgsl.multi` → compile once, dispatch to heterogeneous GPUs |

### healthSpring + petalTongue (Visualization)

| Composition | What Happens |
|------------|-------------|
| **Patient dashboard** | `assess_patient` → `ScenarioNode` graph → petalTongue renders interactive clinical dashboard |
| **Population distribution** | `population_montecarlo` → `DataChannel::Distribution` → petalTongue violin plots with patient overlay |
| **PK curve animation** | `one_compartment_pk` time series → `DataChannel::TimeSeries` → petalTongue live animation |
| **Gut microbiome heatmap** | `bray_curtis` dissimilarity → `DataChannel::Heatmap` → petalTongue interactive heatmap |
| **3D PCoA ordination** | Community distance matrix → `DataChannel::Scatter3D` → petalTongue rotatable 3D view |

### healthSpring + Squirrel (AI Inference)

| Composition | What Happens |
|------------|-------------|
| **AI-augmented diagnostics** | `assess_patient` output → Squirrel ML model → refined risk prediction |
| **Natural language clinical queries** | Clinician asks question → Squirrel routes to healthSpring science capabilities → answer |
| **Model-guided dosing** | Historical patient data → Squirrel inference → suggested dose → healthSpring PK validation |

### healthSpring + NestGate (Data Storage)

| Composition | What Happens |
|------------|-------------|
| **Three-tier fetch** | healthSpring requests dataset → biomeOS NestGate → local cache / NAS / NCBI HTTP |
| **Content-addressed results** | Computation outputs stored via `storage.put` with BLAKE3 hash → reproducible retrieval |
| **Dataset provenance** | `data/manifest.toml` accession numbers → NestGate `discovery.query` for availability |

### healthSpring + BearDog (Cryptography)

| Composition | What Happens |
|------------|-------------|
| **Signed assessments** | `assess_patient` → BearDog Ed25519 sign → cryptographically authenticated health record |
| **Encrypted patient data** | Sensitive biosignal data → BearDog ChaCha20-Poly1305 → secure storage |
| **Genetic lineage** | healthSpring instance → BearDog family seed → auto-trust with sibling primals |

### healthSpring + Songbird (Network)

| Composition | What Happens |
|------------|-------------|
| **Cross-tower health compute** | Remote patient data arrives via Songbird TLS → healthSpring processes locally → results return encrypted |
| **Federated population PK** | Multiple sites contribute anonymized PK data → Songbird federation → healthSpring NLME across sites |
| **Discovery** | Songbird BirdSong multicast → find healthSpring instances with specific capabilities |

### healthSpring + biomeOS (Orchestration)

| Composition | What Happens |
|------------|-------------|
| **Niche deployment** | `healthspring_health.yaml` → biomeOS deploys healthSpring + dependencies as a niche |
| **Pathway Learner** | `operation_dependencies` + `cost_estimates` → biomeOS optimizes execution order |
| **Neural API** | `capability.call("science.pkpd.hill_dose_response", ...)` → biomeOS routes to healthSpring |

---

## 4. Cross-Spring Compositions

Springs never import each other. They coordinate through shared barraCuda primitives and biomeOS capability discovery.

### healthSpring + airSpring (Ecological + Health)

| Composition | What Happens |
|------------|-------------|
| **Environmental health correlation** | airSpring atmospheric data (ET₀, water quality) + healthSpring microbiome diversity → environmental health impact |
| **Agricultural toxicology** | airSpring soil chemistry → healthSpring PBPK model → pesticide exposure risk |
| **Seasonal health patterns** | airSpring seasonal pipeline → healthSpring population PK with seasonal covariates |

### healthSpring + neuralSpring (Bioinformatics + Health)

| Composition | What Happens |
|------------|-------------|
| **Genomic-guided dosing** | neuralSpring sequence analysis → pharmacogenomic variants → healthSpring population PK with genetic covariates |
| **Microbiome metagenomics** | neuralSpring taxonomy + QS gene detection → healthSpring Anderson gut model → colonization resistance |
| **Multi-omics risk** | neuralSpring proteomics/metabolomics + healthSpring biosignal + endocrine → composite risk score |

### healthSpring + wetSpring (Life Science + Health)

| Composition | What Happens |
|------------|-------------|
| **Drug-microbiome interaction** | wetSpring enzyme kinetics → healthSpring antibiotic perturbation → microbiome recovery prediction |
| **PFAS health impact** | wetSpring PFAS mass spectrometry → healthSpring PK modeling for bioaccumulation |
| **Structural biology + PK** | wetSpring molecular alignment → healthSpring allometric scaling → cross-species PK prediction |

### healthSpring + groundSpring (Environmental Monitoring + Health)

| Composition | What Happens |
|------------|-------------|
| **Air quality health impact** | groundSpring sensor noise characterization → healthSpring biosignal stress detection |
| **Water quality monitoring** | groundSpring hydrological data → healthSpring exposure risk modeling |
| **Noise measurement calibration** | groundSpring Anderson noise model → healthSpring biosignal pre-processing |

### healthSpring + hotSpring (Physics + Health)

| Composition | What Happens |
|------------|-------------|
| **Medical imaging physics** | hotSpring spectral theory → healthSpring MRI/CT reconstruction (future) |
| **Radiation dosimetry** | hotSpring nuclear EOS → healthSpring dose-response curves for radiation therapy |
| **MD-guided drug design** | hotSpring molecular dynamics → healthSpring PK prediction for candidate molecules |

### healthSpring + ludoSpring (Game Science + Health)

| Composition | What Happens |
|------------|-------------|
| **Gamified rehabilitation** | ludoSpring game mechanics → healthSpring biosignal monitoring → adaptive difficulty based on HRV/stress |
| **Health education games** | ludoSpring procedural generation → healthSpring PK visualization → interactive dosing simulator |
| **Engagement-driven therapy** | ludoSpring Fitts/Hick models → healthSpring endocrine response → engagement-optimized TRT protocols |

---

## 5. Novel Multi-Primal Pipelines

### Full NUCLEUS Health Pipeline

```
biomeOS orchestrates:
  Songbird (discovery) → find healthSpring
  NestGate (data) → fetch patient records
  healthSpring (compute) → assess_patient
  barraCuda (math) → GPU-accelerated population PK
  toadStool (dispatch) → route to best hardware
  coralReef (compile) → sovereign shader compilation
  petalTongue (visualize) → render clinical dashboard
  rhizoCrypt (memory) → session DAG
  sweetGrass (attribution) → provenance braid
  loamSpine (permanence) → immutable health record
  BearDog (crypto) → sign and encrypt
  Squirrel (AI) → ML-augmented risk prediction
```

### Cross-Spring Population Health Study

```
biomeOS orchestrates:
  airSpring → environmental covariates (ET₀, soil quality)
  groundSpring → sensor calibration data
  neuralSpring → genomic variants
  wetSpring → biochemical pathways
  healthSpring → population_montecarlo(patients=10000, covariates=all)
  petalTongue → interactive population health dashboard
  loamSpine → permanent study record with W3C PROV-O
```

### Real-Time Wearable Health Monitoring

```
biomeOS orchestrates:
  toadStool → discover wearable sensors (serial transport)
  healthSpring → pan_tompkins + hrv_metrics + ppg_spo2 (streaming)
  healthSpring → eda_stress_detection (real-time)
  healthSpring → fuse_channels (multi-sensor fusion)
  petalTongue → live dashboard (60 Hz SSE streaming)
  rhizoCrypt → session DAG (ephemeral, discard after visit)
  Squirrel → anomaly detection (ML inference on fused signal)
```

---

## Discovery Protocol

All compositions above are **runtime-discovered**. healthSpring never imports another primal. The discovery chain:

1. healthSpring starts → registers capabilities with biomeOS via `capability.list`
2. biomeOS discovers healthSpring → adds to niche capability registry
3. Any primal calls `capability.call("science.pkpd.hill_dose_response", params)` → biomeOS routes to healthSpring
4. healthSpring discovers other primals by capability domain: `discover_compute_primal()`, `discover_shader_compiler()`, `discover_inference_primal()`, `discover_data_primal()`
5. No compile-time coupling. Primals come and go. Capabilities are the contract.

---

## For Other Primals Writing This Document

Focus on:
1. **What you compute** — your science/infrastructure capabilities
2. **What you gain from the trio** — how rhizoCrypt/sweetGrass/loamSpine enhance your domain
3. **What cross-primal compositions unlock** — novel capabilities that emerge from combining your domain with others
4. **What cross-spring compositions unlock** — how your validation domain combines with other validation domains
5. **What full NUCLEUS pipelines look like** — the complete sovereign compute story

Remember: complexity through coordination, not coupling.
