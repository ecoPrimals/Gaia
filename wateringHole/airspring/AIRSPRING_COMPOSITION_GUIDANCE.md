# airSpring — Composition Guidance for Springs and Primals

**Date**: March 17, 2026
**From**: airSpring V0.8.9
**License**: AGPL-3.0-or-later

---

## Purpose

This document describes how airSpring's capabilities can be leveraged:
1. **Solo** — what airSpring offers as a standalone primal
2. **Trio combos** — airSpring composed with the Memory & Attribution Stack (rhizoCrypt + sweetGrass + loamSpine)
3. **Wider primal compositions** — airSpring in NUCLEUS, cross-spring, and multi-primal pipelines

Each primal in the ecosystem should write an equivalent document. No primal knows about another at compile time — all composition happens at runtime via capability-based discovery through biomeOS.

---

## 1. airSpring Solo — Self-Knowledge Capabilities

airSpring is a precision agriculture and ecological science compute primal. It owns the `ecology` domain and advertises 40+ capabilities across 7 science categories.

### Science Capabilities (What We Compute)

| Domain | Capabilities | Use Cases |
|--------|-------------|-----------|
| **Evapotranspiration** (7 methods) | `science.et0_fao56`, `et0_hargreaves`, `et0_priestley_taylor`, `et0_makkink`, `et0_turc`, `et0_hamon`, `et0_blaney_criddle` | Reference crop ET₀ from weather data — 7 independent methods for ensemble comparison and inter-method bias detection |
| **Water balance & yield** | `science.water_balance`, `yield_response` | Field-scale daily water budget (FAO-56 dual depletion), Stewart yield-water response function for crop yield prediction |
| **Soil physics** | `science.richards_1d`, `scs_cn_runoff`, `green_ampt_infiltration`, `soil_moisture_topp`, `pedotransfer_saxton_rawls` | Richards equation vadose zone flow, SCS curve number runoff, Green-Ampt infiltration, Topp dielectric sensor calibration, Saxton-Rawls pedotransfer |
| **Crop & irrigation** | `science.dual_kc`, `sensor_calibration`, `gdd` | FAO-56 dual Kc (basal + evaporation), SoilWatch 10 VWC sensor calibration, Growing Degree Days |
| **Biodiversity** | `science.shannon_diversity`, `bray_curtis` | Shannon-Wiener H', Bray-Curtis dissimilarity for soil microbiome community comparison |
| **Monthly ET & drought** | `science.thornthwaite`, `spi_drought_index`, `autocorrelation`, `gamma_cdf` | Thornthwaite monthly ET₀, Standardized Precipitation Index (SPI) drought classification, temporal autocorrelation, gamma CDF for SPI normalization |
| **Geophysics coupling** | `science.anderson_coupling` | Anderson disorder W — tissue diversity / soil microbiome coupling to physical disorder metrics |

### Infrastructure Capabilities (How We Coordinate)

| Capability | Description |
|-----------|-------------|
| `capability.list` | Advertise all capabilities with operation dependencies and cost estimates |
| `compute.offload` | Delegate GPU-eligible work to toadStool via Node Atomic |
| `data.weather` / `data.cross_spring_weather` | Weather data routing — standalone or cross-spring exchange |
| `primal.forward` | Forward cross-domain requests to discovered primals |
| `primal.discover` | Runtime capability-based discovery of peer primals |
| `health.liveness` / `health.readiness` | Health probes for biomeOS orchestration |
| `provenance.begin/record/complete/status` | Session-scoped provenance tracking |
| `science.timeseries` | Cross-spring time series exchange (ecoPrimals/time-series/v1) |

### Solo Leverage Patterns

**For any spring or primal** that needs ecological or agricultural compute:

```
capability.call("ecology.et0_fao56", {
  "t_max": 32.1, "t_min": 19.8, "rh_mean": 55.0,
  "wind_2m": 1.7, "rs": 22.5, "lat": 42.73, "doy": 180, "elev": 264.0
})
→ { "et0": 5.23, "rn": 14.8, "method": "penman_monteith_fao56" }
```

- **Climate modeling**: Any primal computing future climate scenarios can delegate reference ET₀ for crop water demand projection
- **Environmental monitoring**: Any IoT sensor network can route soil moisture through `sensor_calibration` and `soil_moisture_topp`
- **Food security**: Any supply chain primal can invoke `yield_response` for water-limited crop yield estimates
- **Drought assessment**: Any regional monitoring system can use `spi_drought_index` for standardized drought classification
- **Soil health**: Any biodiversity pipeline can route community matrices through `shannon_diversity` and `bray_curtis`

---

## 2. Trio Combos — airSpring + Memory & Attribution Stack

The Memory & Attribution Stack (rhizoCrypt + sweetGrass + loamSpine) provides ephemeral memory, attribution, and permanent records. airSpring's science capabilities gain powerful new properties when composed with this stack.

### airSpring + rhizoCrypt (Ephemeral Memory)

| Composition | Pattern | Example |
|------------|---------|---------|
| **Irrigation experiment tracking** | `provenance.begin` → run ET₀ + water balance + yield → `dag.append` per computation → `provenance.complete` | Track every FAO-56 computation, every soil moisture reading, every yield prediction in a growing season experiment as a DAG of content-addressed events |
| **Multi-field comparison** | `dag.session.create` per field → parallel `water_balance` calls → `dag.merge` → aggregate field-level statistics | Process multi-field irrigation trials in isolated sessions, merge for regional analysis |
| **Iterative calibration** | `dag.session.create` → calibrate sensor A → `dag.append` → adjust → calibrate sensor B → `dag.append` → compare → `dag.session.commit` | Record each calibration step for later audit and refinement |
| **Seasonal pipeline replay** | Full season ET₀→Kc→WB→Yield → `dag.append` each stage → compare with previous season DAG | Reproduce and diff entire growing seasons for management evolution |

### airSpring + sweetGrass (Attribution)

| Composition | Pattern | Example |
|------------|---------|---------|
| **Reproducible agricultural science** | Each `science.*` call records attribution (FAO-56 reference, barraCuda version, sensor model) → sweetGrass braid | Every ET₀ value is traceable to exact method, exact parameters, exact code commit, exact Python baseline comparison |
| **Multi-stakeholder field trial** | Agronomist A runs ET₀ → Soil scientist B runs Richards → Economist C runs yield → sweetGrass tracks roles | Fair attribution in collaborative agricultural research workflows |
| **Regulatory compliance** | `provenance.record` + sweetGrass braid → W3C PROV-O export | Standards-compliant provenance for USDA NRCS, EPA, or EU Nitrates Directive submissions |

### airSpring + loamSpine (Permanence)

| Composition | Pattern | Example |
|------------|---------|---------|
| **Permanent field records** | Season water balance → rhizoCrypt session → `dehydrate` → loamSpine entry with inclusion proof | A field's entire water balance history becomes an immutable, cryptographically signed record |
| **Loam Certificates for yield** | `yield_response` prediction + actual yield → loamSpine certificate | Issue verifiable yield credentials ("Field 12 achieved 92% of FAO-56 predicted yield for corn 2026") |
| **Long-term soil health** | Annual `shannon_diversity` + `bray_curtis` → loamSpine entries → trend analysis over permanent history | Track soil microbiome health across decades with tamper-evident records |
| **Drought record permanence** | `spi_drought_index` monthly → loamSpine entries | Build an immutable, auditable drought history for insurance and policy |

### Full Trio: airSpring + rhizoCrypt + sweetGrass + loamSpine

**Pattern: Provenance-Tracked Growing Season Pipeline**

```
1. rhizoCrypt: dag.session.create("corn_field_12_2026")
2. airSpring: ecology.et0_fao56(weather_april) → ET₀ time series
3. rhizoCrypt: dag.append(et0_result)
4. airSpring: science.dual_kc(crop="corn", kcb_mid=1.15) → daily Kc
5. rhizoCrypt: dag.append(kc_result)
6. airSpring: science.water_balance(et0, kc, precip, irrigation) → soil depletion
7. rhizoCrypt: dag.append(wb_result)
8. airSpring: science.yield_response(wb_result) → yield estimate
9. rhizoCrypt: dag.append(yield_result)
10. sweetGrass: braid.create(session_dag, attribution=[agronomist, drone_data_v3, fao56_method])
11. loamSpine: entry.append(yield_record, braid, inclusion_proof)
12. rhizoCrypt: dag.session.commit → permanent record
```

Every step is content-addressed, attributed, and permanently auditable. The farmer, the agronomist, the regulator, and the insurer all see the same chain of evidence.

---

## 3. Wider Primal Compositions

### airSpring + barraCuda (GPU Math)

| Composition | What Happens |
|------------|-------------|
| **Batched ET₀ for 100+ stations** | airSpring prepares weather parameters → barraCuda `BatchedElementwiseF64` (op=0) → GPU-parallel FAO-56 for continental-scale ET₀ |
| **Richards PDE acceleration** | airSpring 1D domain setup → barraCuda `pde::richards_gpu` → Picard iteration entirely on GPU with `cyclic_reduction_f64.wgsl` tridiagonal solver |
| **Kriging interpolation** | airSpring soil moisture stations → barraCuda `KrigingF64` → spatial interpolation for unmonitored locations |
| **Monte Carlo ET₀ uncertainty** | airSpring parameter perturbation → barraCuda batched ET₀ → GPU-parallel 10K-sample uncertainty quantification |
| **Seasonal stats** | airSpring daily time series → barraCuda `FusedMapReduceF64` → mean/var/min/max in single GPU pass for N≥1024 |
| **Bootstrap confidence intervals** | airSpring sensor data → barraCuda `BootstrapMeanGpu` → GPU-parallel 10K bootstrap resamples |

**Absorption flow**: airSpring writes local WGSL shaders → validates parity with CPU → hands off to barraCuda for upstream absorption → leans on upstream ops. 42 barraCuda touchpoints currently wired.

### airSpring + toadStool (Compute Orchestration)

| Composition | What Happens |
|------------|-------------|
| **GPU job dispatch** | `compute.offload` with workload descriptor → toadStool routes to best GPU/CPU |
| **Precision routing** | `PrecisionRoutingAdvice` → f64 on Titan V, df64 on consumer GPUs, f32 fallback |
| **Multi-station pipeline** | 100-station atlas → toadStool partitions across available GPUs → airSpring processes each partition |
| **OnceLock device sharing** | airSpring's `OnceLock` GPU probe integrates cleanly with toadStool's device registry |

### airSpring + coralReef (Shader Compilation)

| Composition | What Happens |
|------------|-------------|
| **Sovereign compute** | airSpring WGSL → coralReef compiles to native SASS/ISA binary → no vendor SDK needed |
| **f64 transcendentals** | coralReef's full f64 lowering (DFMA on NVIDIA, native on AMD) replaces wgpu's limited f64 |
| **Cross-platform** | airSpring writes one WGSL shader → coralReef compiles for NVIDIA, AMD, Intel → same ET₀ everywhere |

### airSpring + petalTongue (Visualization)

| Composition | What Happens |
|------------|-------------|
| **Farm dashboard** | `water_balance` time series → petalTongue renders interactive soil moisture + irrigation schedule + yield forecast |
| **Regional ET₀ heatmap** | `atlas_stream` 100-station data → petalTongue spatial heatmap with temporal animation |
| **Kriging contour map** | `kriging` interpolation grid → petalTongue 2D contour overlay on satellite imagery |
| **SPI drought map** | `spi_drought_index` regional → petalTongue choropleth with D0-D4 drought classification colors |
| **Soil profile** | Richards equation output → petalTongue animated depth profile showing wetting front progression |

### airSpring + Squirrel (AI Inference)

| Composition | What Happens |
|------------|-------------|
| **ML-augmented ET₀** | Historical weather + airSpring FAO-56 → Squirrel trains surrogate MLP → R²=0.999 at 100x speed for real-time systems |
| **Irrigation scheduling AI** | Soil moisture, weather forecast, crop stage → Squirrel inference → optimal irrigation schedule → airSpring validates with water balance |
| **Natural language ecology queries** | Farmer asks "what's the drought risk for next month?" → Squirrel routes to airSpring `spi_drought_index` + `et0_fao56` → answer |
| **Pest/disease prediction** | Squirrel inference on GDD + humidity → disease risk → airSpring validates thermal accumulation |

### airSpring + NestGate (Data Storage)

| Composition | What Happens |
|------------|-------------|
| **Three-tier weather fetch** | airSpring requests weather → biomeOS NestGate → local cache / NAS / Open-Meteo HTTP |
| **Content-addressed results** | Season water balance stored via `storage.put` with BLAKE3 hash → reproducible retrieval across seasons |
| **Dataset provenance** | `data/manifest.toml` accession numbers (USDA SCAN, AmeriFlux, EPA STORET, NCBI SRA) → NestGate `discovery.query` for availability |

### airSpring + BearDog (Cryptography)

| Composition | What Happens |
|------------|-------------|
| **Signed yield reports** | `yield_response` → BearDog Ed25519 sign → cryptographically authenticated yield prediction for insurance |
| **Encrypted field data** | Proprietary sensor data → BearDog ChaCha20-Poly1305 → secure storage and transport |
| **Genetic lineage** | airSpring instance → BearDog family seed → auto-trust with sibling niche deployments |

### airSpring + Songbird (Network)

| Composition | What Happens |
|------------|-------------|
| **Cross-tower field data** | Remote weather stations arrive via Songbird TLS → airSpring processes locally → results return encrypted |
| **Federated regional ET₀** | Multiple farms contribute station data → Songbird federation → airSpring atlas aggregation across private networks |
| **Discovery** | Songbird BirdSong multicast → find airSpring instances with specific capabilities (e.g., `science.richards_1d` for custom soil types) |

### airSpring + biomeOS (Orchestration)

| Composition | What Happens |
|------------|-------------|
| **Niche deployment** | `graphs/airspring_niche_deploy.toml` → biomeOS deploys airSpring + dependencies as a niche |
| **Pathway Learner** | `operation_dependencies` + `cost_estimates` → biomeOS optimizes execution order (ET₀ before Kc before WB before yield) |
| **Neural API** | `capability.call("ecology.et0_fao56", ...)` → biomeOS routes to airSpring regardless of topology |

---

## 4. Cross-Spring Compositions

Springs never import each other. They coordinate through shared barraCuda primitives and biomeOS capability discovery.

### airSpring + groundSpring (Uncertainty Quantification)

| Composition | What Happens |
|------------|-------------|
| **ET₀ uncertainty decomposition** | airSpring ET₀ + groundSpring sensitivity analysis → "humidity dominates ET₀ uncertainty at 66%" → targeted sensor investment |
| **Sensor noise characterization** | groundSpring Anderson noise model → airSpring sensor calibration with uncertainty bounds |
| **Monte Carlo water balance** | groundSpring parametric uncertainty → airSpring MC water balance → yield confidence intervals |
| **Inverse modeling** | airSpring Richards forward model + groundSpring inverse solver → estimate soil hydraulic properties from field data |

### airSpring + neuralSpring (ML + Agriculture)

| Composition | What Happens |
|------------|-------------|
| **MLP ET₀ surrogate** | neuralSpring trains MLP on airSpring FAO-56 output → R²=0.999 surrogate for real-time deployment |
| **Transfer learning** | neuralSpring trains on Michigan data → transfers to New Mexico → airSpring validates with local baselines |
| **Structure prediction** | neuralSpring protein fold → soil enzyme activity → airSpring soil microbial community model |
| **Spatio-temporal interpolation** | neuralSpring attention model on multi-station time series → airSpring validates against kriging ground truth |

### airSpring + wetSpring (Life Science + Ecology)

| Composition | What Happens |
|------------|-------------|
| **Kriging spatial interpolation** | wetSpring Shannon diversity + airSpring kriging → spatial mapping of soil biodiversity |
| **Anderson W(t) coupling** | wetSpring dynamic disorder + airSpring soil moisture → time-dependent disorder models for soil-microbiome feedback |
| **PFAS soil contamination** | wetSpring PFAS mass spectrometry → airSpring pedotransfer → PFAS leaching prediction through soil profile |
| **Biochar adsorption** | airSpring Langmuir/Freundlich isotherm fitting → wetSpring enzyme kinetics → contaminant removal efficiency |

### airSpring + healthSpring (Environmental + Human Health)

| Composition | What Happens |
|------------|-------------|
| **Environmental health correlation** | airSpring atmospheric data (ET₀, water quality) + healthSpring microbiome diversity → environmental health impact |
| **Agricultural toxicology** | airSpring soil chemistry → healthSpring PBPK model → pesticide exposure risk assessment |
| **Seasonal health patterns** | airSpring seasonal pipeline → healthSpring population PK with seasonal covariates (humidity, allergen load) |
| **One Health bridge** | airSpring soil microbiome + healthSpring gut microbiome → Anderson disorder W connects soil and human biodiversity |

### airSpring + hotSpring (Physics + Agriculture)

| Composition | What Happens |
|------------|-------------|
| **Radiation balance** | hotSpring spectral theory → airSpring solar radiation partitioning for ET₀ (Rns/Rnl components) |
| **Soil thermal dynamics** | hotSpring heat equation → airSpring soil temperature profile → GDD with depth-aware thermal correction |
| **Plasma-treated water** | hotSpring plasma physics → airSpring irrigation water quality → enhanced crop response modeling |

### airSpring + ludoSpring (Game Science + Agriculture)

| Composition | What Happens |
|------------|-------------|
| **Farming simulation** | ludoSpring procedural terrain → airSpring water balance on generated soil profiles → realistic farming game mechanics |
| **Irrigation optimization game** | ludoSpring game engine → airSpring real-time ET₀ + water balance → gamified irrigation scheduling training |
| **Engagement-driven learning** | ludoSpring Fitts/Hick models → airSpring complexity estimation → adaptive difficulty for agricultural education |
| **Crop management strategy** | ludoSpring decision trees → airSpring yield response → optimal crop management game with real physics |

---

## 5. Novel Multi-Primal Pipelines

### Full NUCLEUS Precision Agriculture Pipeline

```
biomeOS orchestrates:
  Songbird (discovery) → find airSpring + weather station network
  NestGate (data) → fetch USDA SCAN soil moisture, Open-Meteo weather
  airSpring (compute) → ET₀ → dual Kc → water balance → yield response
  barraCuda (math) → GPU-accelerated batched ET₀ for 100 fields
  toadStool (dispatch) → route heavy compute to Titan V
  coralReef (compile) → sovereign shader compilation
  petalTongue (visualize) → interactive farm management dashboard
  rhizoCrypt (memory) → session DAG for growing season
  sweetGrass (attribution) → attribution braid (farmer + agronomist + sensors)
  loamSpine (permanence) → immutable yield record for insurance
  BearDog (crypto) → sign yield certificate
  Squirrel (AI) → ML-augmented irrigation recommendation
```

### Continental-Scale Drought Monitoring

```
biomeOS orchestrates:
  NestGate → fetch PRISM/CHIRPS precipitation grids
  airSpring → spi_drought_index(scale=3) for 10K grid cells (GPU-batched)
  groundSpring → uncertainty bands on SPI via parametric bootstrap
  barraCuda → FusedMapReduceF64 for spatial aggregation
  petalTongue → animated drought severity map (D0-D4)
  loamSpine → permanent drought record
  Songbird → federate across regional monitoring towers
```

### Precision Irrigation Decision System

```
biomeOS orchestrates:
  toadStool → discover IoT soil moisture sensors
  airSpring → sensor_calibration(raw_counts) → VWC
  airSpring → et0_fao56(weather_forecast) → ET₀ prediction
  airSpring → dual_kc(crop="corn", stage="mid") → Kc
  airSpring → water_balance(ET₀, Kc, precip_forecast) → depletion forecast
  Squirrel → ML inference → optimal irrigation volume + timing
  airSpring → water_balance(+irrigation) → validate schedule won't over-deplete
  petalTongue → farmer-facing irrigation schedule with confidence intervals
  rhizoCrypt → session DAG for this irrigation decision cycle
```

### Cross-Spring Soil-Microbiome-Health Pipeline

```
biomeOS orchestrates:
  wetSpring → 16S microbiome profiling of soil sample
  airSpring → shannon_diversity + bray_curtis on soil community
  airSpring → anderson_coupling → disorder metric W
  healthSpring → anderson_gut → human gut disorder metric
  neuralSpring → correlation analysis between soil and gut W(t)
  petalTongue → parallel violin plots of soil vs gut diversity
  sweetGrass → attribution braid (soil scientist + clinician)
  loamSpine → permanent One Health record
```

---

## Discovery Protocol

All compositions above are **runtime-discovered**. airSpring never imports another primal. The discovery chain:

1. airSpring starts → registers capabilities with biomeOS via `capability.list`
2. biomeOS discovers airSpring → adds to niche capability registry
3. Any primal calls `capability.call("ecology.et0_fao56", params)` → biomeOS routes to airSpring
4. airSpring discovers other primals by capability domain: `discover_shader_compiler()`, `discover_inference_primal()`, `discover_primal_socket()`
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
