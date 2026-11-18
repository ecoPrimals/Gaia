# ecoPrimals wateringHole — Consolidated Guidance Export
Generated: 2026-07-29T18:53:18-04:00

---

## FILE: `airspring/AIRSPRING_COMPOSITION_GUIDANCE.md`

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

---

## FILE: `birdsong/BIRDSONG_PROTOCOL.md`

# 🎵 BirdSong Protocol Specification

**Version**: 2.0  
**Last Updated**: January 3, 2026  
**Status**: Production Ready (Songbird v3.6)

---

## 🎯 Purpose

BirdSong is the **encrypted discovery protocol** for the ecoPrimal ecosystem. It solves the "chicken-and-egg problem" of encrypted UDP discovery:

> **Problem**: How do you discover primals using encryption when you don't know who to trust yet?

> **Solution**: Plaintext family_id header + encrypted payload for dual-phase trust evaluation.

---

## 🏗️ Protocol Architecture

### Two-Phase Discovery

```
Phase 1: Family Identification (Plaintext)
  ↓
  UDP Packet Header: family_id (plaintext)
  ↓
Phase 2: Identity Verification (Encrypted)
  ↓
  UDP Packet Payload: Identity + Capabilities (encrypted)
  ↓
  Result: Auto-trust within family!
```

### Why This Works

1. **Plaintext family_id** → Receivers can quickly filter "is this my family?"
2. **Encrypted payload** → Only family members can decrypt identity details
3. **No chicken-and-egg** → Don't need to know peer before evaluating trust

---

## 📦 Packet Structure

### BirdSongPacket v2

```json
{
  "version": 2,
  "family_id": "your-family-id",
  "encrypted_payload": {
    "ciphertext": "<base64-encoded-encrypted-data>",
    "nonce": "<base64-encoded-nonce>",
    "algorithm": "ChaCha20-Poly1305"
  },
  "timestamp": 1704326400,
  "ttl": 300
}
```

### Encrypted Payload Contents (After Decryption)

```json
{
  "primal_id": "songbird-tower-1",
  "primal_type": "songbird",
  "endpoint": "http://192.0.2.10:8080",
  "capabilities": ["discovery", "auto-trust", "encrypted-birdsong"],
  "identity_attestations": {
    "family_id": "your-family-id",
    "seed_hash": "<hash-of-family-seed>",
    "public_key": "<optional-public-key>",
    "signature": "<optional-signature>"
  }
}
```

---

## 🔐 Encryption Details

### Algorithm

**ChaCha20-Poly1305** (AEAD - Authenticated Encryption with Associated Data)

**Why ChaCha20-Poly1305?**
- Fast on all platforms (including ARM)
- Widely trusted (used by TLS 1.3)
- Authenticated encryption (integrity + confidentiality)
- Modern alternative to AES-GCM

### Key Derivation

```
Family Seed (base64-encoded)
  ↓
Base64 Decode
  ↓
Use as ChaCha20-Poly1305 key (32 bytes)
```

**Note**: Production systems should use proper KDF (e.g., HKDF, Argon2)

### Nonce Generation

```
Random 12 bytes (96 bits) per packet
  ↓
Base64 encode for JSON transport
```

**Critical**: Nonce MUST be unique for each packet with same key!

---

## 🚀 Implementation (Songbird v3.6)

### Encryption Flow

```rust
// 1. Prepare plaintext payload
let payload = IdentityPayload {
    primal_id: "songbird-tower-1",
    primal_type: "songbird",
    endpoint: "http://192.0.2.10:8080",
    capabilities: vec!["discovery", "auto-trust"],
    identity_attestations: attestations,
};

// 2. Serialize to JSON
let plaintext = serde_json::to_vec(&payload)?;

// 3. Call BearDog encryption API
let response = beardog_client
    .encrypt(plaintext, family_id)
    .await?;

// 4. Build BirdSongPacket
let packet = BirdSongPacket {
    version: 2,
    family_id: family_id.clone(),
    encrypted_payload: EncryptedPayload {
        ciphertext: response.ciphertext,
        nonce: response.nonce,
        algorithm: "ChaCha20-Poly1305".to_string(),
    },
    timestamp: SystemTime::now()
        .duration_since(UNIX_EPOCH)?
        .as_secs(),
    ttl: 300,
};

// 5. Serialize packet to JSON
let packet_json = serde_json::to_vec(&packet)?;

// 6. Send via UDP multicast
send_udp_multicast(packet_json, "239.255.0.1:4200")?;
```

### Decryption Flow (Receiver)

```rust
// 1. Receive UDP packet
let packet_data = receive_udp()?;

// 2. Parse BirdSongPacket
let packet: BirdSongPacket = serde_json::from_slice(&packet_data)?;

// 3. Check family_id (plaintext header)
if packet.family_id != our_family_id {
    return Err("Not our family, ignoring");
}

// 4. Call BearDog decryption API
let response = beardog_client
    .decrypt(
        packet.encrypted_payload.ciphertext,
        packet.family_id,
        packet.encrypted_payload.nonce
    )
    .await?;

// 5. Parse decrypted payload
let payload: IdentityPayload = serde_json::from_slice(&response.plaintext)?;

// 6. Evaluate trust
if payload.identity_attestations.family_id == our_family_id {
    // Auto-trust! Add to trusted peers
    add_trusted_peer(payload);
}
```

---

## 🌐 Network Transport

### UDP Multicast

**Multicast Group**: `239.255.0.1:4200` (default)

**Why UDP Multicast?**
- Single packet reaches all towers on LAN
- No need to know peer IPs in advance
- Low overhead for periodic beacons
- Standard discovery pattern

### Beacon Frequency

**Recommended**: Every 30-60 seconds

**Trade-offs**:
- Too frequent: Network spam
- Too infrequent: Slow peer discovery

**Adaptive**: Increase frequency when topology changes detected

### Packet Size

**Typical**: 500-1000 bytes
- Plaintext header: ~50 bytes
- Encrypted payload: ~400-800 bytes
- Well under UDP MTU (1500 bytes)

---

## 🔄 Protocol Evolution

### Version History

#### v1.0 (Deprecated)
- Plaintext only
- No encryption
- Simple primal_id broadcast
- **Problem**: No security, anyone could spoof

#### v2.0 (Current)
- Plaintext family_id + encrypted payload
- Solves chicken-and-egg problem
- Identity attestations
- **Status**: ✅ Working (Songbird v3.6)

#### v3.0 (Future)
- Public key cryptography (optional)
- Digital signatures for attestations
- Key rotation support
- Multi-family routing

---

## 🧪 Testing & Validation

### Manual Test (Send Packet)

```bash
# Start Songbird with debug logging
RUST_LOG=songbird=debug ./songbird-orchestrator-v3.6

# Watch logs for:
# - "Calling BearDog encryption API"
# - "Encryption succeeded"
# - "Sending BirdSongPacket"
```

### Manual Test (Receive Packet)

```bash
# Listen on multicast group
socat UDP4-RECV:4200,ip-add-membership=239.255.0.1:0.0.0.0 -

# Should see JSON packets with:
# - family_id (plaintext)
# - encrypted_payload with ciphertext
```

### Integration Test

```bash
# Start BearDog
./start-beardog-server.sh

# Start Songbird (Tower 1)
./start-songbird.sh

# Start Songbird (Tower 2 - different terminal)
./start-songbird.sh

# Verify Tower 2 logs show:
# - "Received BirdSongPacket from <Tower 1>"
# - "Decryption succeeded"
# - "Added trusted peer: <Tower 1>"
```

---

## 📊 Production Status

### What's Working ✅

- ✅ BirdSongPacket v2 structure
- ✅ Encryption via BearDog API
- ✅ Decryption via BearDog API
- ✅ UDP multicast transmission
- ✅ Plaintext family_id filtering
- ✅ Identity attestations
- ✅ Base64 serialization (correct!)
- ✅ Songbird v3.6 integration

### Known Issues ⚠️

1. **No key rotation** - Same family seed forever
   - Impact: High (security)
   - Mitigation: Periodic manual rotation
   - Fix: Implement key rotation protocol

2. **No replay protection** - Old packets can be resent
   - Impact: Medium (DoS potential)
   - Mitigation: TTL check, sequence numbers
   - Fix: Add packet sequence numbers

3. **No rate limiting** - Beacon spam possible
   - Impact: Low (LAN only)
   - Mitigation: Reasonable beacon frequency
   - Fix: Implement adaptive beaconing

---

## 🎯 For Primal Developers

### Implementing BirdSong Support

**Step 1**: Add BearDog client dependency
```rust
use biomeos_core::adaptive_client::BirdSongClient;
```

**Step 2**: Initialize client
```rust
let beardog_endpoint = "http://localhost:9000";
let client = BirdSongClient::new(beardog_endpoint);
```

**Step 3**: Encrypt discovery data
```rust
let payload = your_primal_identity();
let plaintext = serde_json::to_vec(&payload)?;
let encrypted = client.encrypt(plaintext, family_id).await?;
```

**Step 4**: Build and send BirdSongPacket
```rust
let packet = BirdSongPacket::new(family_id, encrypted);
send_udp_multicast(packet)?;
```

**Step 5**: Receive and decrypt
```rust
let packet = receive_birdsong_packet()?;
if packet.family_id == our_family {
    let decrypted = client.decrypt(
        packet.encrypted_payload.ciphertext,
        packet.family_id,
        packet.encrypted_payload.nonce
    ).await?;
    handle_peer_identity(decrypted)?;
}
```

### Using Adaptive Client

**Why**: Handles both BearDog v1 and v2 APIs automatically

```rust
use biomeos_core::adaptive_client::BirdSongClient;

// Client auto-detects API version
let mut client = BirdSongClient::new("http://localhost:9000");

// Works with both v1 and v2!
let encrypted = client.encrypt(data, family_id).await?;
```

See: `biomeOS/crates/biomeos-core/src/adaptive_client.rs`

---

## 🔗 Ecosystem Integration

### Songbird → BearDog

```
Songbird (Discovery Orchestrator)
  ↓ HTTP POST /api/v2/birdsong/encrypt
BearDog (Genetic Keeper)
  ↓ Encrypted payload
Songbird
  ↓ UDP multicast
Network (239.255.0.1:4200)
```

### Receiving Tower

```
Network (UDP multicast)
  ↓ BirdSongPacket (JSON)
Songbird (Receiver)
  ↓ Parse, check family_id
BearDog (Decryption)
  ↓ Decrypted identity
Songbird
  ↓ Trust evaluation
biomeOS (Orchestration)
  ↓ Add to topology
PetalTongue (Visualization)
```

---

## 📋 Technical Specifications

### Packet Format (JSON)

```typescript
interface BirdSongPacket {
  version: number;                    // Protocol version (2)
  family_id: string;                  // Plaintext family identifier
  encrypted_payload: {
    ciphertext: string;               // Base64-encoded encrypted data
    nonce: string;                    // Base64-encoded 12-byte nonce
    algorithm: string;                // "ChaCha20-Poly1305"
  };
  timestamp: number;                  // Unix timestamp (seconds)
  ttl: number;                        // Time-to-live (seconds)
}

interface IdentityPayload {           // Decrypted payload contents
  primal_id: string;                  // Unique primal identifier
  primal_type: string;                // "songbird", "beardog", etc.
  endpoint: string;                   // HTTP endpoint URL
  capabilities: string[];             // Supported capabilities
  identity_attestations: {
    family_id: string;                // Family membership proof
    seed_hash: string;                // Hash of family seed
    public_key?: string;              // Optional public key
    signature?: string;               // Optional signature
  };
}
```

### Network Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| Multicast IP | 239.255.0.1 | Site-local range |
| UDP Port | 4200 | Configurable |
| Beacon Interval | 30-60s | Adaptive |
| TTL | 300s (5 min) | Packet lifetime |
| Max Packet Size | 1500 bytes | Standard MTU |

---

## 💡 Best Practices

### For Implementers

1. **Always check family_id** before attempting decryption
2. **Validate timestamp and TTL** before processing
3. **Use adaptive client** for BearDog API compatibility
4. **Never log family seeds** or plaintext payloads
5. **Implement exponential backoff** for API failures

### For Operators

1. **Use same family_id** across all towers in family
2. **Secure family seed** with proper permissions
3. **Monitor beacon frequency** to prevent spam
4. **Check network multicast** support (some cloud providers block)
5. **Test cross-tower discovery** before production

---

## 🚦 Roadmap

### Short-term (1-2 months)

- [ ] Packet sequence numbers (replay protection)
- [ ] Adaptive beacon frequency
- [ ] Rate limiting
- [ ] Enhanced attestations

### Medium-term (3-6 months)

- [ ] Public key cryptography (optional)
- [ ] Digital signatures
- [ ] Key rotation protocol
- [ ] Multi-family routing

### Long-term (6-12 months)

- [ ] BirdSong v3.0 protocol
- [ ] Federation support
- [ ] Advanced trust models
- [ ] Performance optimizations

---

## 📚 References

### Implementation Examples

- **Songbird v3.6**: `ecoPrimals/phase1/songbird/songbird-orchestrator-v3.6-api-wrapper`
- **Adaptive Client**: `biomeOS/crates/biomeos-core/src/adaptive_client.rs`
- **BearDog API**: `wateringHole/btsp/BEARDOG_TECHNICAL_STACK.md`

### Related Documentation

- **BearDog Technical Stack**: `wateringHole/btsp/`
- **biomeOS Architecture**: `biomeOS/README.md`
- **Integration Guides**: `biomeOS/docs/jan3-session/`

---

**Status**: ✅ **PRODUCTION READY**  
**Verified**: Songbird v3.6 + BearDog v0.15.0  
**Next**: Enhanced attestations + replay protection

🎵 **BirdSong: Encrypted Discovery for Secure Auto-Trust** 🔐


---

## FILE: `birdsong/DARK_FOREST_BEACON_GENETICS_STANDARD.md`

# Dark Forest Beacon Genetics Specification

**Version**: 2.0.0  
**Date**: February 5, 2026  
**Status**: ✅ IMPLEMENTED & VALIDATED  
**Author**: ecoPrimal + AI Collaborative Intelligence

---

## Executive Summary

This specification implements a **two-seed genetic architecture** separating discovery from identity:

| Seed | Biological Analog | Shared? | Function |
|------|-------------------|---------|----------|
| **Beacon Seed** | Mitochondrial DNA | ✅ Yes | Family encryption, address book |
| **Lineage Seed** | Nuclear DNA | ❌ No | Device identity, ancestry proof |

**Key Insight**: 
- **Mitochondrial (Beacon)**: Shared across family, enables Dark Forest encryption, can be synced/evolved
- **Nuclear (Lineage)**: Unique per device, always derived never copied, proves individual ancestry

### Validated Implementation (Feb 5, 2026)

```
Tower:  beacon.seed = 8ff3b864... (SHARED)
        lineage.seed = 5772c07f... (UNIQUE)

Pixel:  beacon.seed = 8ff3b864... (SHARED - same!)  
        lineage.seed = 3795d0ca... (UNIQUE - different!)

Cross-device beacon exchange: ✅ is_family=true both directions
```

---

## 1. Problem Statement

### Current Architecture (Single Seed)

```
Family Seed → Discovery + Trust + Permissions (all bundled)
```

**Limitations**:
- All-or-nothing visibility (see me = access me)
- No cluster hierarchy (every node individually discoverable)
- No "meeting" concept (immediate trust or no trust)
- Beacon broadcasts leak family membership

### Proposed Architecture (Two Seeds)

```
Beacon Seed (Mitochondrial) → Discovery visibility
                              ├── Who have I met?
                              ├── What clusters do I belong to?
                              └── Who can decrypt my beacons?

Lineage Seed (Nuclear)     → Permission verification
                              ├── What can they do after meeting?
                              ├── Read-only / write / admin
                              └── Temporal / capability grants
```

**Benefits**:
- Granular visibility (see me ≠ access me)
- Cluster-based discovery (entry points → internal nodes)
- Social graph of meetings (beacon exchange)
- TRUE Dark Forest (beacons encrypted, observers see noise)

---

## 2. Biological Model

### Mitochondrial vs Nuclear DNA

| Property | Mitochondrial DNA | Nuclear DNA |
|----------|-------------------|-------------|
| **Inheritance** | Maternal only (simpler) | Mixed (both parents) |
| **Function** | Energy/metabolism | Identity/traits |
| **Mutation rate** | Lower (stability) | Higher (adaptation) |
| **Size** | ~16.5kb (small) | ~3 billion bp (large) |
| **Copies per cell** | 100-1000 | 2 |

### Mapping to ecoPrimals

| Property | Beacon Seed | Lineage Seed |
|----------|-------------|--------------|
| **Inheritance** | Social (meetings) | Genetic (family) |
| **Function** | Discovery | Permissions |
| **Rotation** | Can rotate frequently | Stable (identity) |
| **Size** | 32 bytes | 32 bytes |
| **Sharing model** | Exchange on meeting | Derive from parent |

**Key Difference**: Beacon seed can be **mixed** through meetings (not strictly maternal). This enables the "who you've met" social graph.

---

## 3. Architecture

### 3.1 Seed Structure

```rust
/// Beacon seed - controls discovery visibility
struct BeaconSeed {
    /// Core seed material (32 bytes)
    seed: [u8; 32],
    
    /// Beacon family derived from seed
    beacon_family: BeaconFamily,
    
    /// Known beacon peers (social graph)
    met_beacons: HashMap<BeaconId, MeetingRecord>,
    
    /// Cluster memberships
    clusters: Vec<ClusterMembership>,
}

/// Lineage seed - controls permissions (existing)
struct LineageSeed {
    /// Core seed material (32 bytes)
    seed: [u8; 32],
    
    /// Family ID derived from seed
    family_id: String,
    
    /// Node ID for this instance
    node_id: String,
    
    /// Lineage chain
    lineage_chain: Vec<LineageProof>,
}
```

### 3.2 Beacon Discovery Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LAYER 1: BEACON DISCOVERY                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Node A broadcasts: encrypt(beacon_seed, presence_info)                    │
│                                                                             │
│  Observers without beacon genetics: [noise] [noise] [noise]                │
│  Observers with beacon genetics: "Node A at 192.0.2.100:9200"           │
│                                                                             │
│  ✅ TRUE Dark Forest - outsiders can't even detect communication          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Beacon decrypted (meeting established)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LAYER 2: LINEAGE VERIFICATION                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  After beacon handshake, verify lineage for permissions:                   │
│                                                                             │
│  Node A ──── lineage challenge ────► Node B                                │
│  Node A ◄─── lineage response ────── Node B                                │
│                                                                             │
│  Result: Permission level determined                                        │
│    ├── Close lineage → Full access                                         │
│    ├── Distant lineage → Read-only                                         │
│    ├── Temporal grant → Time-limited                                       │
│    └── No lineage match → Beacon visible, no access                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 Cluster Architecture

```
External Network
       │
       ▼
┌─────────────────────────────────────────┐
│  Entry Point (cluster beacon)           │
│  - External peers find this first       │
│  - Gateway to internal discovery        │
│  - Shares internal beacon genetics      │
└────────────────┬────────────────────────┘
                 │
    ┌────────────┼────────────┐
    ▼            ▼            ▼
┌────────┐  ┌────────┐  ┌────────┐
│ gate-01 │  │ gate-02 │  │ gate-03  │
│ tower   │  │ tower   │  │ tower    │
│ beacon  │  │ beacon  │  │ beacon   │
└────────┘  └────────┘  └────────┘
    │            │            │
    └────────────┴────────────┘
         Internal mesh
      (all see each other)
```

**External Discovery Path**:
1. Remote peer discovers Entry Point beacon (if they've met)
2. Beacon handshake establishes meeting
3. Entry Point shares internal beacon genetics
4. Remote peer can now discover individual towers
5. Lineage verification per tower determines permissions

**Internal Discovery**:
- All towers share internal beacon genetics
- Direct mesh, no entry point needed
- Lineage still required for permissions

---

## 4. Seed Generation and Derivation

### 4.1 Genesis Seeds

```rust
/// Generate both seeds from a master secret
fn generate_genesis_seeds(master_secret: &[u8; 64]) -> (BeaconSeed, LineageSeed) {
    // Beacon seed - first 32 bytes domain-separated
    let beacon_seed = hkdf_sha256(
        &master_secret[..32],
        b"ecoPrimals-beacon-genesis-v1",
        32
    );
    
    // Lineage seed - second 32 bytes domain-separated  
    let lineage_seed = hkdf_sha256(
        &master_secret[32..],
        b"ecoPrimals-lineage-genesis-v1",
        32
    );
    
    (BeaconSeed::from(beacon_seed), LineageSeed::from(lineage_seed))
}
```

### 4.2 Beacon Mixing (Meeting Exchange)

```rust
/// Exchange beacon genetics during a meeting
fn beacon_meeting(
    my_beacon: &BeaconSeed,
    their_beacon: &BeaconSeed,
    meeting_type: MeetingType,
) -> MeetingRecord {
    // Generate shared meeting key
    let meeting_key = hkdf_sha256(
        &[my_beacon.seed, their_beacon.seed].concat(),
        b"ecoPrimals-beacon-meeting-v1",
        32
    );
    
    MeetingRecord {
        their_beacon_id: their_beacon.id(),
        meeting_key,
        meeting_type,
        timestamp: unix_timestamp(),
        // After meeting, we can decrypt their beacons
        can_see_them: true,
        // They can decrypt ours (if mutual)
        they_can_see_us: meeting_type.is_mutual(),
    }
}
```

### 4.3 Cluster Beacon Derivation

```rust
/// Derive cluster beacon from member beacons
fn derive_cluster_beacon(
    members: &[BeaconSeed],
    cluster_id: &str,
) -> ClusterBeacon {
    // Combine all member beacon seeds
    let combined: Vec<u8> = members
        .iter()
        .flat_map(|m| m.seed.iter())
        .copied()
        .collect();
    
    // Derive cluster seed
    let cluster_seed = hkdf_sha256(
        &combined,
        format!("ecoPrimals-cluster-{}-v1", cluster_id).as_bytes(),
        32
    );
    
    ClusterBeacon {
        cluster_id: cluster_id.to_string(),
        cluster_seed,
        members: members.iter().map(|m| m.id()).collect(),
    }
}
```

---

## 5. Permission Model

### 5.1 After Beacon Handshake

```rust
/// Permission levels determined by lineage verification
enum LineagePermission {
    /// Same lineage seed - full family access
    FullFamily,
    
    /// Related lineage - read + limited write
    ExtendedFamily {
        can_read: bool,
        can_write: Vec<Capability>,
    },
    
    /// Federated partner - specific capabilities
    FederatedPartner {
        capabilities: Vec<Capability>,
        expires: Option<Timestamp>,
    },
    
    /// Temporal grant - time-limited access
    TemporalGrant {
        permissions: Vec<Capability>,
        not_before: Timestamp,
        not_after: Timestamp,
    },
    
    /// Beacon only - can see, cannot access
    BeaconOnly,
}
```

### 5.2 Permission Flow

```
Beacon handshake complete
         │
         ▼
┌─────────────────────────────────────┐
│ Request lineage verification        │
│ from BearDog                        │
└─────────────────┬───────────────────┘
                  │
         ┌────────┴────────┐
         ▼                 ▼
   Same lineage?     Different lineage?
         │                 │
         ▼                 ▼
   Full access      Check federation
         │                 │
         │          ┌──────┴──────┐
         │          ▼             ▼
         │    Federated?    Not federated?
         │          │             │
         │          ▼             ▼
         │    Limited        Beacon only
         │    access         (no access)
         │          │             │
         └──────────┴─────────────┘
                    │
                    ▼
            Permissions set
```

---

## 6. Primal Evolution Requirements

### 6.1 BearDog Evolution

**New Responsibilities**:
- Generate and manage beacon seed (separate from lineage seed)
- Beacon encryption/decryption
- Meeting record storage
- Cluster beacon derivation

**New RPC Methods**:

```rust
// Beacon seed management
"beacon.generate"              // Generate new beacon seed
"beacon.get_id"                // Get beacon ID (public)
"beacon.encrypt"               // Encrypt data with beacon seed
"beacon.decrypt"               // Decrypt data with beacon seed

// Meeting management
"beacon.initiate_meeting"      // Start meeting exchange
"beacon.complete_meeting"      // Complete meeting exchange
"beacon.list_meetings"         // List known meetings
"beacon.revoke_meeting"        // Revoke a meeting (they can no longer see us)

// Cluster management  
"beacon.create_cluster"        // Create cluster beacon
"beacon.join_cluster"          // Join existing cluster
"beacon.get_cluster_beacon"    // Get cluster's beacon for sharing

// Lineage (existing, unchanged)
"lineage.verify"               // Verify lineage for permissions
"lineage.get_permissions"      // Get permissions after verification
```

**New Environment Variables**:

```bash
# Separate seeds
BEARDOG_BEACON_SEED=<hex>      # Beacon seed (discovery)
BEARDOG_LINEAGE_SEED=<hex>     # Lineage seed (permissions) - was BEARDOG_FAMILY_SEED

# Backward compatibility
BEARDOG_FAMILY_SEED=<hex>      # If set alone, derives both seeds from it
```

### 6.2 Songbird Evolution

**New Responsibilities**:
- BirdSong beacons encrypted with beacon seed
- Meeting exchange protocol
- Cluster discovery hierarchy

**Changes to BirdSong**:

```rust
// Before: Plaintext beacon
struct BirdSongBeacon {
    family_id: String,
    node_id: String,
    capabilities: Vec<String>,
    endpoint: String,
}

// After: Encrypted beacon
struct DarkForestBeacon {
    // Encrypted with beacon seed
    encrypted_payload: Vec<u8>,
    // Nonce for decryption
    nonce: [u8; 24],
    // Timestamp to prevent replay
    timestamp: u64,
}

struct BeaconPayload {
    beacon_id: BeaconId,
    node_id: String,
    capabilities_hash: [u8; 32],
    endpoint: String,
    cluster_id: Option<String>,
}
```

**Discovery Protocol Change**:

```
Current:
  Multicast → Everyone sees → Connect → Verify lineage

Proposed:
  Multicast → Only those with beacon genetics see → Connect → Verify lineage
```

### 6.3 biomeOS Evolution

**New Responsibilities**:
- Cluster management
- Entry point configuration
- Beacon genetics exchange protocol
- Cross-cluster federation

**New Components**:

```rust
// Cluster manager
struct ClusterManager {
    // This cluster's beacon
    cluster_beacon: ClusterBeacon,
    
    // Entry point configuration
    entry_point: Option<EntryPointConfig>,
    
    // Member management
    members: Vec<NodeId>,
    
    // External peers who have met us
    external_meetings: HashMap<BeaconId, MeetingRecord>,
}

// Entry point configuration
struct EntryPointConfig {
    // Public endpoint for external discovery
    public_endpoint: String,
    
    // Which internal beacons to share after meeting
    share_internal: bool,
    
    // Rate limiting for external meetings
    meeting_rate_limit: Option<RateLimit>,
}
```

---

## 7. Implementation Plan

### Phase 1: BearDog Beacon Seed (Priority: High)

**Tasks**:
- [ ] Add `BeaconSeed` struct to `beardog-genetics`
- [ ] Add beacon seed generation/derivation
- [ ] Add beacon encryption/decryption
- [ ] Add `beacon.*` RPC methods
- [ ] Support both `BEARDOG_BEACON_SEED` and backward-compatible `BEARDOG_FAMILY_SEED`
- [ ] Unit tests for beacon operations

**Estimated Effort**: 2-3 sessions

### Phase 2: BirdSong Dark Forest (Priority: High)

**Tasks**:
- [ ] Change BirdSong beacon format to encrypted
- [ ] Add beacon decryption on receive (try all known beacon genetics)
- [ ] Filter discovered peers by beacon visibility
- [ ] Update discovery protocol to handle encrypted beacons
- [ ] Integration tests with BearDog beacon seed

**Estimated Effort**: 2-3 sessions

### Phase 3: Meeting Exchange Protocol (Priority: Medium)

**Tasks**:
- [ ] Design meeting exchange handshake
- [ ] Implement `beacon.initiate_meeting` / `beacon.complete_meeting`
- [ ] Store meeting records in BearDog
- [ ] Add meeting management UI concepts

**Estimated Effort**: 2 sessions

### Phase 4: Cluster Architecture (Priority: Medium)

**Tasks**:
- [ ] Implement cluster beacon derivation
- [ ] Add entry point configuration
- [ ] Implement internal beacon sharing after cluster meeting
- [ ] Add cluster management to biomeOS

**Estimated Effort**: 3 sessions

### Phase 5: Permission Granularity (Priority: Low)

**Tasks**:
- [ ] Implement `LineagePermission` variants
- [ ] Add temporal grants
- [ ] Add capability-based permissions
- [ ] Federation permission negotiation

**Estimated Effort**: 2 sessions

---

## 8. Scaling Analysis

### 8.1 Beacon Load

| Network Size | Beacon Broadcasts | Visible to Each Node |
|--------------|-------------------|---------------------|
| 10 nodes | 10 beacons | 10 (small family) |
| 100 nodes, 5 families | 100 beacons | ~20 (own family) |
| 1,000 nodes, 50 families | 1,000 beacons | ~20 (own family) |
| 10,000 nodes, hierarchical | 10,000 beacons | 100-1,000 (cluster) |

**Key Insight**: Network load is O(n), but cognitive load is O(family_size). TRUE Dark Forest.

### 8.2 Meeting Scalability

| Model | Meetings Stored | Discovery Complexity |
|-------|-----------------|---------------------|
| Direct only | O(friends) | O(friends) |
| With clusters | O(friends + clusters) | O(friends) + O(1) per cluster |
| Hierarchical | O(log n) clusters | O(log n) |

### 8.3 Dark Forest Property

| Metric | Without Beacon Genetics | With Beacon Genetics |
|--------|------------------------|---------------------|
| Visible to attackers | All beacons | 0 (encrypted noise) |
| Family identifiable | Yes (family_id in plaintext) | No |
| Traffic analysis | Possible | Impossible |
| Metadata leakage | Endpoints, capabilities | Nothing |

---

## 9. Security Analysis

### 9.1 Threat Model

| Threat | Mitigation |
|--------|------------|
| Beacon eavesdropping | Encrypted with beacon seed |
| Family enumeration | Beacons indistinguishable from noise |
| Replay attacks | Timestamps in beacon payload |
| Meeting impersonation | Challenge-response in meeting exchange |
| Permission escalation | Lineage verification separate from beacon |

### 9.2 Trust Levels

```
Level 0: Unknown
    └── No beacon genetics match
    └── Cannot decrypt beacons
    └── Invisible to each other (TRUE Dark Forest)

Level 1: Met (Beacon visible)
    └── Beacon genetics exchanged
    └── Can see beacons, can attempt connection
    └── No permissions yet

Level 2: Lineage Verified
    └── Beacon visible + lineage checked
    └── Permissions determined by lineage relationship
    └── Full family / federated / temporal / capability

Level 3: Cluster Member
    └── Part of same cluster
    └── Internal beacon genetics shared
    └── Cluster-level permissions
```

---

## 10. Backward Compatibility

### 10.1 Migration Path

```
Phase 1: Dual mode
    BEARDOG_FAMILY_SEED set alone → Derives both seeds (backward compatible)
    BEARDOG_BEACON_SEED + BEARDOG_LINEAGE_SEED → New two-seed mode

Phase 2: Gradual migration
    Existing deployments continue working
    New deployments use two-seed mode
    
Phase 3: Full migration
    BEARDOG_FAMILY_SEED deprecated
    All deployments use two-seed mode
```

### 10.2 BirdSong Compatibility

```
Phase 1: Beacon format detection
    If beacon decrypts → New encrypted format
    If beacon parses as JSON → Legacy plaintext format
    Support both during transition

Phase 2: Deprecation warning
    Plaintext beacons trigger warning
    Still accepted but logged

Phase 3: Plaintext rejection
    Only encrypted beacons accepted
```

---

## 11. Summary

### What This Enables

1. **TRUE Dark Forest**: Beacons encrypted, observers see only noise
2. **Social Graph Discovery**: "Who you've met" determines visibility
3. **Cluster Hierarchy**: Entry points → internal nodes
4. **Granular Permissions**: Beacon ≠ access, lineage determines capabilities
5. **Scalable Discovery**: O(family) cognitive load, not O(network)

### The Biological Elegance

| Layer | Analog | Function |
|-------|--------|----------|
| Beacon Seed | Mitochondrial DNA | Discovery/energy |
| Lineage Seed | Nuclear DNA | Identity/permissions |
| Meeting | Social encounter | Beacon genetics exchange |
| Cluster | Colony | Hierarchical discovery |
| Entry Point | Colony entrance | External gateway |

### Design Principles

1. **Beacon = who you've met** (social graph)
2. **Lineage = what you can do** (permissions)
3. **Cluster = network topology** (hierarchy)
4. **Entry point = external interface** (gateway)
5. **TRUE Dark Forest** (observers see nothing)

---

**Status**: ARCHITECTURAL SPECIFICATION - Ready for implementation

*"Beacon genetics is who you've met. Lineage is security. Together, they create a social graph overlaid on cryptographic trust."*

---

## Appendix A: Code Examples

### A.1 Complete Beacon Discovery Flow

```rust
// Node A broadcasts encrypted beacon
async fn broadcast_beacon(beacon_seed: &BeaconSeed) {
    let payload = BeaconPayload {
        beacon_id: beacon_seed.id(),
        node_id: get_node_id(),
        capabilities_hash: hash_capabilities(&my_capabilities),
        endpoint: get_endpoint(),
        cluster_id: get_cluster_id(),
    };
    
    let encrypted = beacon_seed.encrypt(&serialize(payload));
    
    multicast_send(DarkForestBeacon {
        encrypted_payload: encrypted.ciphertext,
        nonce: encrypted.nonce,
        timestamp: unix_timestamp(),
    });
}

// Node B receives and tries to decrypt
async fn receive_beacon(
    beacon: DarkForestBeacon,
    known_beacons: &[BeaconSeed],
) -> Option<DiscoveredPeer> {
    // Try decrypting with each known beacon seed
    for known in known_beacons {
        if let Ok(payload) = known.decrypt(&beacon.encrypted_payload, &beacon.nonce) {
            let payload: BeaconPayload = deserialize(&payload)?;
            
            return Some(DiscoveredPeer {
                beacon_id: payload.beacon_id,
                node_id: payload.node_id,
                endpoint: payload.endpoint,
                met_via: known.id(),
            });
        }
    }
    
    // Can't decrypt - not someone we've met
    None
}
```

### A.2 Meeting Exchange

```rust
// Initiator
async fn initiate_meeting(peer_endpoint: &str) -> Result<MeetingRecord> {
    // Generate meeting request
    let request = MeetingRequest {
        my_beacon_id: my_beacon.id(),
        my_public_beacon: my_beacon.public_portion(),
        nonce: random_32_bytes(),
    };
    
    // Send to peer
    let response: MeetingResponse = send_request(peer_endpoint, request).await?;
    
    // Verify and complete meeting
    let meeting = beacon_meeting(
        &my_beacon,
        &response.their_beacon,
        MeetingType::Direct,
    );
    
    // Store meeting
    store_meeting(meeting.clone());
    
    Ok(meeting)
}

// Responder
async fn respond_to_meeting(request: MeetingRequest) -> Result<MeetingResponse> {
    // Verify request
    verify_meeting_request(&request)?;
    
    // Complete meeting on our side
    let meeting = beacon_meeting(
        &my_beacon,
        &request.their_beacon,
        MeetingType::Direct,
    );
    
    // Store meeting
    store_meeting(meeting);
    
    // Return our beacon info
    Ok(MeetingResponse {
        their_beacon: my_beacon.public_portion(),
        nonce_response: sign_nonce(&request.nonce),
    })
}
```

---

**Document Version**: 1.0.0  
**Last Updated**: February 4, 2026  
**Next Review**: After Phase 1 implementation

---

## FILE: `birdsong/SONGBIRD_TLS_TOWER_ATOMIC_INTEGRATION_GUIDE.md`

# 🚀 Songbird TLS 1.3 Tower Atomic Integration Guide
**Date**: January 24, 2026  
**Status**: ✅ **PRODUCTION READY**  
**Target**: biomeOS Graph Deployment System  
**Purpose**: Enable biomeOS to replicate Songbird's TLS 1.3 success

---

## 🎉 Achievement Summary

Songbird has successfully implemented **Pure Rust TLS 1.3** using the **Tower Atomic pattern** with BearDog crypto delegation, achieving:

✅ **TRUE ecoBin status** (100% Pure Rust)  
✅ **RFC 8446 compliance** (TLS 1.3 specification)  
✅ **Universal cross-compilation** (14+ targets)  
✅ **Production validated** (Cloudflare, Google, GitHub)  
✅ **Zero C dependencies** (no rustls, no ring, no openssl)

**Innovation**: Crypto delegation via JSON-RPC enables Pure Rust TLS!

---

## 🏗️ Architecture: Tower Atomic Pattern

### High-Level Flow

```
┌─────────────────────────────────────────────────┐
│              External HTTPS                      │
│         (Cloudflare, Google, etc.)               │
└──────────────────┬──────────────────────────────┘
                   │ TLS 1.3
                   ↓
┌─────────────────────────────────────────────────┐
│           Songbird HTTP Client                   │
│  ┌───────────────────────────────────────────┐  │
│  │   Pure Rust TLS 1.3 Implementation        │  │
│  │   - ClientHello (extensions, ciphers)     │  │
│  │   - ServerHello parsing                   │  │
│  │   - Key schedule management               │  │
│  │   - Record layer encryption/decryption    │  │
│  │   - Session management                    │  │
│  └─────────────────┬─────────────────────────┘  │
│                    │                             │
│                    │ Crypto Operations           │
│                    │ (X25519, HKDF, AES-GCM,     │
│                    │  ChaCha20, SHA-256)         │
│                    ↓                             │
│  ┌───────────────────────────────────────────┐  │
│  │   JSON-RPC over Unix Socket               │  │
│  │   Endpoint: /primal/beardog               │  │
│  └─────────────────┬─────────────────────────┘  │
└────────────────────┼─────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────┐
│           BearDog Crypto Service                 │
│  ┌───────────────────────────────────────────┐  │
│  │   Pure Rust Cryptography (RustCrypto)     │  │
│  │   - X25519 key exchange                   │  │
│  │   - HKDF-Expand-Label (TLS 1.3)           │  │
│  │   - AES-128-GCM, AES-256-GCM              │  │
│  │   - ChaCha20-Poly1305                     │  │
│  │   - SHA-256, HMAC                         │  │
│  │   - Key derivation (handshake/app)        │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

### Key Components

1. **Songbird**: TLS protocol implementation (Pure Rust)
2. **BearDog**: Cryptographic operations (Pure Rust RustCrypto)
3. **Communication**: JSON-RPC 2.0 over Unix sockets
4. **Result**: Both are TRUE ecoBins with universal portability

---

## 📋 Integration Requirements for biomeOS

### Prerequisites

1. **Songbird Primal** (v5.24.0+)
   - Binary: `songbird`
   - Socket: `/primal/songbird`
   - Capabilities: `["http", "https", "tls"]`

2. **BearDog Primal** (v0.9.0+)
   - Binary: `beardog`
   - Socket: `/primal/beardog`
   - Capabilities: `["crypto", "btsp", "ed25519", "x25519"]`

3. **Unix Socket Infrastructure**
   - `/primal/` namespace available
   - JSON-RPC 2.0 support
   - IPC routing configured

---

## 🔧 Graph Deployment Configuration

### Example biomeOS Graph Node

```toml
# Graph: tls_https_stack.toml

[[nodes]]
id = "launch_beardog"
node_type = "primal.launch"

[nodes.config]
primal_name = "beardog"
binary_path = "plasmidBin/primals/beardog"
mode = "service"
args = ["service", "start"]
socket_path = "/primal/beardog"
capabilities = ["crypto", "btsp", "ed25519", "x25519"]
family_id = "nat0"

[[nodes]]
id = "launch_songbird"
node_type = "primal.launch"
depends_on = ["launch_beardog"]  # Must start after BearDog

[nodes.config]
primal_name = "songbird"
binary_path = "plasmidBin/primals/songbird"
mode = "server"
args = ["server", "--http-port", "8080"]
socket_path = "/primal/songbird"
capabilities = ["http", "https", "tls", "discovery"]
family_id = "nat0"

[nodes.config.environment]
# Songbird will auto-discover BearDog via /primal/beardog
BEARDOG_SOCKET = "/primal/beardog"  # Optional: explicit override
RUST_LOG = "info"

[[nodes]]
id = "validate_tls"
node_type = "test.integration"
depends_on = ["launch_songbird"]

[nodes.config]
test_type = "https_request"
target_url = "https://cloudflare.com"
expected_status = 200
timeout_seconds = 10
```

### Startup Sequence

1. **BearDog starts** → Binds to `/primal/beardog`
2. **BearDog registers** → Songbird discovery can find it
3. **Songbird starts** → Discovers BearDog via `/primal/beardog`
4. **Songbird ready** → Can make HTTPS requests

---

## 🔌 JSON-RPC API Reference

### BearDog Crypto Operations

Songbird uses these BearDog JSON-RPC methods:

#### 1. X25519 Key Exchange

```json
// Request
{
  "jsonrpc": "2.0",
  "method": "crypto.x25519_key_exchange",
  "params": {
    "client_private_key": "hex_encoded_32_bytes",
    "server_public_key": "hex_encoded_32_bytes"
  },
  "id": 1
}

// Response
{
  "jsonrpc": "2.0",
  "result": {
    "shared_secret": "hex_encoded_32_bytes"
  },
  "id": 1
}
```

#### 2. HKDF Key Derivation (TLS 1.3)

```json
// Request
{
  "jsonrpc": "2.0",
  "method": "crypto.tls_derive_handshake_secrets",
  "params": {
    "shared_secret": "hex_encoded_32_bytes",
    "hello_hash": "hex_encoded_sha256"
  },
  "id": 2
}

// Response
{
  "jsonrpc": "2.0",
  "result": {
    "client_handshake_traffic_secret": "hex_32_bytes",
    "server_handshake_traffic_secret": "hex_32_bytes"
  },
  "id": 2
}
```

#### 3. AES-128-GCM Encryption

```json
// Request
{
  "jsonrpc": "2.0",
  "method": "crypto.aes128_gcm_encrypt",
  "params": {
    "key": "hex_encoded_16_bytes",
    "nonce": "hex_encoded_12_bytes",
    "plaintext": "hex_encoded_data",
    "aad": "hex_encoded_additional_data"
  },
  "id": 3
}

// Response
{
  "jsonrpc": "2.0",
  "result": {
    "ciphertext": "hex_encoded_data_with_tag"
  },
  "id": 3
}
```

#### 4. AES-128-GCM Decryption

```json
// Request
{
  "jsonrpc": "2.0",
  "method": "crypto.aes128_gcm_decrypt",
  "params": {
    "key": "hex_encoded_16_bytes",
    "nonce": "hex_encoded_12_bytes",
    "ciphertext": "hex_encoded_data_with_tag",
    "aad": "hex_encoded_additional_data"
  },
  "id": 4
}

// Response
{
  "jsonrpc": "2.0",
  "result": {
    "plaintext": "hex_encoded_data"
  },
  "id": 4
}
```

### Complete API

See BearDog documentation for full API:
- `crypto.aes256_gcm_encrypt/decrypt`
- `crypto.chacha20_poly1305_encrypt/decrypt`
- `crypto.tls_derive_application_secrets`
- `crypto.tls_compute_finished_verify_data`
- `crypto.sha256_hash`

---

## 🧪 Testing & Validation

### Integration Test Script

```bash
#!/bin/bash
# test_tls_stack.sh

set -e

echo "🚀 Starting BearDog..."
beardog service start &
BEARDOG_PID=$!
sleep 2

echo "🚀 Starting Songbird..."
songbird server --http-port 8080 &
SONGBIRD_PID=$!
sleep 2

echo "🧪 Testing HTTPS connection..."

# Test 1: Cloudflare
echo "Test 1: Cloudflare"
curl -v http://localhost:8080/https/cloudflare.com 2>&1 | grep "200 OK"

# Test 2: Google
echo "Test 2: Google"
curl -v http://localhost:8080/https/google.com 2>&1 | grep "200 OK"

# Test 3: GitHub
echo "Test 3: GitHub"
curl -v http://localhost:8080/https/github.com 2>&1 | grep "200 OK"

echo "✅ All tests passed!"

# Cleanup
kill $SONGBIRD_PID $BEARDOG_PID
```

### Validation Checklist

- [ ] BearDog starts and binds to `/primal/beardog`
- [ ] Songbird discovers BearDog via Unix socket
- [ ] TLS 1.3 handshake completes successfully
- [ ] HTTPS requests to external sites succeed
- [ ] Error handling works (network failures, invalid certificates)
- [ ] Performance is acceptable (latency, throughput)
- [ ] Resource usage is reasonable (CPU, memory)

---

## 📊 Performance Characteristics

### Measured Performance (Jan 2026)

| Operation | Latency | Notes |
|-----------|---------|-------|
| TLS Handshake | ~200ms | Includes network RTT to server |
| HTTP GET (1KB) | ~50ms | After handshake complete |
| JSON-RPC Call | ~1ms | Songbird ↔ BearDog IPC |
| AES-GCM Encrypt/Decrypt | <0.1ms | Per TLS record |

### Optimization Opportunities

1. **Connection Pooling** - Reuse TLS sessions
2. **Session Resumption** - 0-RTT with PSK
3. **Batch Crypto Operations** - Reduce IPC overhead
4. **Record Coalescing** - Combine small writes

---

## 🔍 Troubleshooting

### Common Issues

#### 1. BearDog Not Found

**Symptom**: `Failed to connect to /primal/beardog`

**Solutions**:
- Check BearDog is running: `ps aux | grep beardog`
- Verify socket exists: `ls -la /primal/beardog`
- Check socket permissions
- Ensure `/primal/` directory exists

#### 2. TLS Handshake Failure

**Symptom**: `TLS handshake failed: Protocol error`

**Debug**:
```bash
# Enable trace logging
RUST_LOG=songbird_http_client=trace songbird server
```

**Common causes**:
- Server doesn't support TLS 1.3
- Certificate validation issues (if enabled)
- Network connectivity problems

#### 3. Crypto Operation Errors

**Symptom**: `Crypto operation failed: Invalid parameters`

**Check**:
- BearDog logs: `journalctl -u beardog -f`
- Key/nonce lengths are correct
- Data encoding is valid hex

---

## 🚀 Deployment to biomeOS

### Step 1: Install Binaries

```bash
# Copy to plasmidBin
cp songbird biomeOS/plasmidBin/primals/
cp beardog biomeOS/plasmidBin/primals/

# Verify
./biomeOS/plasmidBin/primals/songbird --version
./biomeOS/plasmidBin/primals/beardog --version
```

### Step 2: Create Graph

```bash
# Create graph definition
cat > biomeOS/graphs/tls_stack.toml << 'EOF'
# (Use example from above)
EOF
```

### Step 3: Deploy Graph

```bash
cd biomeOS
./biomeos graph deploy graphs/tls_stack.toml --family nat0
```

### Step 4: Verify Deployment

```bash
# Check primals are running
./biomeos primal list

# Test HTTPS
curl http://localhost:8080/https/cloudflare.com

# Check logs
./biomeos logs songbird
./biomeos logs beardog
```

---

## 📚 Reference Documentation

### Songbird

- **Crate**: `songbird-http-client`
- **Main file**: `src/tls/handshake_legacy.rs` (3086 lines)
- **Crypto interface**: `src/crypto/beardog_provider.rs`
- **API**: `src/beardog_client.rs`

### BearDog

- **Tower Atomic Documentation**: See BearDog repo
- **API Specification**: `TOWER_ATOMIC_API.md`
- **Integration Guide**: `BEARDOG_INTEGRATION.md`

### Specifications

- **TLS 1.3**: RFC 8446
- **JSON-RPC**: JSON-RPC 2.0 Specification
- **IPC Protocol**: `/ecoPrimals/wateringHole/PRIMAL_IPC_PROTOCOL.md`
- **ecoBin Standard**: `/ecoPrimals/wateringHole/ECOBIN_ARCHITECTURE_STANDARD.md`

---

## 🎯 Success Criteria

For biomeOS to successfully replicate Songbird's TLS 1.3:

### Functional
- [ ] BearDog and Songbird deploy via graph
- [ ] TLS 1.3 handshake completes
- [ ] HTTPS requests succeed to major sites
- [ ] Error handling is robust

### Performance
- [ ] Handshake latency < 500ms
- [ ] Request latency < 100ms (excluding network)
- [ ] CPU usage < 10% per connection
- [ ] Memory usage < 50MB per primal

### Reliability
- [ ] 99.9% uptime over 24 hours
- [ ] Graceful handling of network failures
- [ ] Proper cleanup on shutdown
- [ ] No memory leaks

---

## 🏆 Benefits of Tower Atomic Pattern

### For biomeOS

1. **Modularity** - Each primal has clear responsibility
2. **Reusability** - BearDog crypto used by multiple primals
3. **Testability** - Components tested independently
4. **Deployability** - Graph-based orchestration
5. **Portability** - Pure Rust everywhere

### For Ecosystem

1. **Standards** - Proven pattern for crypto delegation
2. **Security** - Centralized crypto auditing (BearDog)
3. **Innovation** - Pure Rust TLS without rustls/ring
4. **Showcase** - Rust ecosystem capabilities

---

## 📞 Support & Questions

### Contacts

- **Songbird Team**: TLS implementation questions
- **BearDog Team**: Crypto operations questions
- **biomeOS Team**: Graph deployment questions

### Resources

- **This Document**: Integration guide
- **wateringHole**: Ecosystem standards
- **Specs Directory**: Detailed specifications

---

## 🎉 Conclusion

The **Tower Atomic pattern** has been proven in production with Songbird's successful TLS 1.3 implementation. biomeOS can now replicate this success through its graph deployment system.

**Key Insights**:
- Crypto delegation enables Pure Rust TLS
- JSON-RPC provides clean separation
- Both primals achieve TRUE ecoBin status
- Universal portability without compromise

**Status**: ✅ **READY FOR biomeOS INTEGRATION**

---

**Document Version**: 1.0  
**Last Updated**: January 24, 2026  
**Status**: Production Ready  
**Audience**: biomeOS Integration Team

🚀🦀✨ **Tower Atomic Pattern - Proven at Scale!** ✨🦀🚀


---

## FILE: `btsp/BEARDOG_TECHNICAL_STACK.md`

# BearDog Technical Stack & Plans (BTSP)

**Version**: 0.9.0 (Wave 104 — Deep Debt + FIDO2 IPC)
**Last Updated**: May 15, 2026
**Status**: Production Ready

---

## Purpose

BearDog is the **sovereign genetic cryptography primal** for the ecoPrimals ecosystem. It provides:

1. **Cryptographic Operations** — Ed25519, X25519, ChaCha20-Poly1305, AES-GCM, BLAKE3, SHA-256/384/512, SHA3-256, HMAC, HKDF, TLS key derivation, Tor onion/ntor/cell crypto, post-quantum (ML-KEM, ML-DSA, SPHINCS+)
2. **Identity & Lineage** — Family seed management, lineage key derivation, genetic entropy, trust evaluation
3. **Hardware Security** — HSM abstraction (RustCrypto software, PKCS#11, Android StrongBox, TPM Phase 2)
4. **Secret Storage** — Encrypted secrets with family-scoped ChaCha20-Poly1305 keys
5. **Dark Forest Beacon** — Zero metadata leakage discovery protocol

All primals delegate crypto to BearDog via the **Tower Atomic Pattern** (JSON-RPC 2.0 over NDJSON), keeping a single auditable crypto codebase across the ecosystem.

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| **Language** | Rust (edition 2024, MSRV 1.93.0, `rust-toolchain.toml` pinned) |
| **Crypto** | RustCrypto suite (100% pure Rust, zero C dependencies) |
| **IPC** | JSON-RPC 2.0 over NDJSON (Unix sockets / TCP / named pipes / abstract sockets) |
| **Optional IPC** | tarpc (feature-gated, Rust-to-Rust high-performance) |
| **Serialization** | serde_json (wire), postcard (binary), serde_yaml (config) |
| **Binary** | UniBin architecture — single `beardog` binary with subcommands |
| **License** | AGPL-3.0-or-later (SPDX headers on all source files) |

---

## Architecture

### Crate Organization (29 workspace crates)

**Core Runtime**: `beardog` (binary), `beardog-core`, `beardog-tunnel`, `beardog-ipc`, `beardog-cli`, `beardog-client`

**Type System**: `beardog-types`, `beardog-config`, `beardog-errors`, `beardog-traits`

**Security**: `beardog-security`, `beardog-genetics`, `beardog-hid`, `beardog-auth`, `beardog-threat`

**Infrastructure**: `beardog-monitoring`, `beardog-workflows`, `beardog-adapters`, `beardog-capabilities`, `beardog-discovery`, `beardog-utils`

**Deployment**: `beardog-production`, `beardog-installer`, `beardog-compliance`, `beardog-node-registry`, `beardog-tower-atomic`, `beardog-integration-tests`

**Excluded from workspace**: `beardog-integration` (HTTP overstep), `beardog-deploy` (tooling exception)

### Wire Protocol

All transports use **NDJSON** (newline-delimited JSON-RPC 2.0). Each request is a single JSON object terminated by `\n`. Idle connections time out after 30 seconds.

```
┌─────────────┐                    ┌─────────────┐
│  Any Primal │ ←─ JSON-RPC ────→ │  BearDog    │
│ (Protocol)  │  NDJSON framing    │  (Crypto)   │
└─────────────┘                    └─────────────┘
     Zero crypto code                 126 JSON-RPC methods
```

### JSON-RPC Method Domains (126 methods)

```
crypto.*       - Hash, sign, verify, encrypt, decrypt, key exchange
tls.*          - TLS 1.2/1.3 key derivation and handshake
tor.*          - Onion identity, ntor, cell crypto
genetic.*      - Lineage keys, beacon, challenge-response
secrets.*      - Store, retrieve, list, delete encrypted secrets
relay.*        - Lineage-gated relay authorization (coordinated punch)
beacon.*       - Dark Forest beacon generation, encryption, meeting exchange
btsp.*         - Secure tunnel config + session handshake-as-a-service
quantum.*      - Post-quantum cryptographic operations
```

Introspection: `discover_capabilities`, `primal.info`, `rpc.methods`, `capabilities.list`, `identity.get`

Canonical names use `domain.operation` form. Legacy flat aliases (`ping`, `capabilities`, `health`, `identity`) are deprecated.

### HSM Abstraction

```
HsmKeyProvider (beardog-traits::hsm)
├── RustSoftwareHsm         (RustCrypto, always available)
├── AndroidStrongBoxHsm     (JNI bridge, cfg(target_os = "android"))
├── Pkcs11Provider           (Phase 2: pure Rust pkcs11 crate)
└── TpmProvider              (Phase 2: pure Rust tss-esapi)

HsmProviderRegistry → discover() → select(PreferHardware | RequireHardware | SoftwareOnly)
```

### Multi-Family Isolation

```bash
./beardog server --family-id alpha   # beardog-alpha.sock, own key material
./beardog server --family-id bravo   # beardog-bravo.sock, fully isolated
```

---

## Platform Support

| Platform | Transport | Status |
|----------|-----------|--------|
| Linux (x86_64, ARM64) | Unix sockets | Production |
| macOS (Intel, M-series) | Unix sockets | Production |
| Android (ARM64) | Abstract sockets + TCP | Production |
| Windows (x86_64, ARM64) | Named pipes + TCP | Ready |
| iOS (ARM64) | TCP | Ready |

---

## Quality Metrics

| Metric | Value |
|--------|-------|
| **Build** | Clean, 0 errors |
| **Clippy** | 0 warnings (pedantic + nursery + all cast lints + `doc_markdown` + `missing_errors_doc` + unwrap/expect warn) |
| **Missing Docs** | 0 warnings |
| **Pure Rust** | 100% — zero C dependencies |
| **Unsafe Code** | 0 production blocks (`forbid(unsafe_code)` workspace-wide) |
| **Format** | `cargo fmt` clean |
| **Tests** | 14,940+ (concurrent; 35 `#[serial]` in `beardog-production`) |
| **Coverage** | 90.51% line (llvm-cov workspace) |
| **cargo deny** | 4/4 pass (1 advisory ignore: RSA Marvin, 15 transitive version-skips) |
| **License** | AGPL-3.0-or-later (SPDX headers on all .rs files) |
| **Files > 1000 LOC** | 0 (production) |
| **TODO/FIXME** | 0 |

---

## Security Posture

- **Zero unsafe code** — `forbid(unsafe_code)` workspace-wide
- **Zero panic paths** — No `unwrap()` in production; `expect()` only on documented invariants
- **Constant-time** — `subtle::ConstantTimeEq` for secrets
- **Zeroize** — Sensitive memory cleared on drop
- **Typed errors** — `BearDogError` throughout; no `Box<dyn Error>` in public APIs
- **Self-knowledge only** — BearDog discovers peers at runtime via capability registry; no hardcoded primal names
- **Dependency injection** — Pure `Default`, `from_env()` at boundaries

### Known Advisory

**RSA Timing Sidechannel (RUSTSEC-2023-0071)**: Acknowledged, monitoring for upstream fix. RSA operations use random blinding.

---

## Deployment

### Quick Start

```bash
# Build
cargo build --release

# Run (auto-detects platform transport)
./beardog server

# With family isolation
./beardog server --family-id alpha

# Custom socket path
./beardog server --socket /custom/path.sock

# TCP transport
./beardog server --listen 0.0.0.0:9900
```

### Binary Targets

| Binary | Purpose |
|--------|---------|
| `beardog` | Primary UniBin (server, client, key ops, doctor, capabilities) |
| `beardog-installer` | Tooling exception: deployment and validation on target devices |
| `deploy-pixel8` | Tooling exception: Android adb-based deployment helper |

### Docker

```bash
docker build -t beardog .
docker run -e PRIMAL_NAME=beardog beardog server
```

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `PRIMAL_NAME` | Primal identity | `beardog` |
| `FAMILY_ID` | Family identifier | (none) |
| `NODE_ID` | Node identifier | (random) |
| `BEARDOG_SOCKET` | Socket path override | auto-detected |
| `BEARDOG_PORT` | Listening port | OS-assigned |
| `BEARDOG_HSM_MODE` | HSM backend selection | `software` |

---

## Architectural Compliance

| Standard | Status |
|----------|--------|
| UniBin/ecoBin | Single binary, standalone identity fallback, cross-compilation ready |
| JSON-RPC 2.0 | Primary IPC with NDJSON framing and batch support |
| tarpc | Optional behind feature gate in `beardog-ipc` |
| Pure Rust | Zero C dependencies; `blake3` pure feature; ecoBin compliant |
| Self-Knowledge | Primals discover peers at runtime via capability registry |
| Zero Hardcoding | Named constants + env override + capability discovery |
| `forbid(unsafe_code)` | Workspace level + every crate `lib.rs` |
| Workspace Lints | Centralized clippy pedantic + nursery + all cast lints |
| AGPL-3.0-or-later | SPDX headers on all source files |

---

## Recent Evolution (April 2, 2026)

### Wave 28: Self-Knowledge, Error Typing, Hardcoding

- Removed deprecated `SongbirdClient` type alias; genericized cross-primal references
- `Box<dyn Error>` → `BearDogError` in AI hybrid intelligence public APIs
- Feature flag `advanced-nestgate` → `advanced-registry`

### Wave 27: License, Lint Migration, Deprecation

- License migrated from `AGPL-3.0-only` to `AGPL-3.0-or-later` across all files
- `#[allow()]` → `#[expect(reason)]` migration (49 non-test attributes)
- Legacy flat method aliases documented as deprecated

### Wave 26: Stub Completion, Dependency Alignment

- `handle_key_info` and client JSON-RPC dispatch evolved from stubs to real implementations
- Orphaned entropy modules compiled and fixed
- AI tree (11.9K LOC) feature-gated behind `ai` Cargo feature
- `deny.toml` skip-list reduced from 30 to 15

---

## Future Work

These are enhancements — nothing blocks production use.

- **Secret Storage Evolution** — Persistent NestGate-backed storage via capability discovery (pattern already implemented)
- **Graph Security Phase 2-3** — Public key infrastructure, signature verification chains
- **Semantic Method Naming Phase 3** — Generic `crypto.encrypt` + algorithm parameter (ecosystem coordination)
- **PKCS#11 / TPM Phase 2** — Full hardware crypto via pure Rust crates (`pkcs11`, `tss-esapi`)

---

**Status**: PRODUCTION READY

---

## FILE: `compositions/COMPOSITION_HEALTH_STANDARD.md`

<!--
SPDX-License-Identifier: CC-BY-4.0
-->

# Composition health JSON-RPC standard

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-04-06 |
| **Status** | Canonical |

## Problem

`composition.*_health` method names have diverged across gen3 (primalSpring), gen4 product overlays (for example esotericWebb), and springs (for example wetSpring). This document is the single naming convention for those methods so bridges, registries, and deploy graphs stay aligned.

## Universal composition health (every NUCLEUS deployment)

These methods apply to the shared NUCLEUS stack. Implementations may live in primalSpring or biomeOS; callers discover them through the deployment’s capability surface.

| Method | Stack | Provider | Required |
|--------|-------|----------|----------|
| `composition.tower_health` | BearDog + Songbird + skunkBat | primalSpring or biomeOS | Yes |
| `composition.node_health` | Tower + ToadStool | primalSpring or biomeOS | If node present |
| `composition.nest_health` | Tower + NestGate | primalSpring or biomeOS | If nest present |
| `composition.nucleus_health` | Full NUCLEUS | primalSpring | If full NUCLEUS |

## Spring-specific composition health

Convention: `composition.{spring_name}_health` for domain health scoped to that spring.

| Method | Spring | Stack |
|--------|--------|-------|
| `composition.science_health` | wetSpring | Science pipeline + provenance |
| `composition.geology_health` | groundSpring | Geology pipeline |
| `composition.physics_health` | hotSpring | Physics pipeline |
| `composition.game_health` | ludoSpring | Game session pipeline |

## Product overlay health (gen4 products)

Convention: `composition.{product}_health` or `composition.{product}_{layer}_health`. Product overlays sit on top of universal composition; each product registers its methods in its own capability registry and exposes them through its bridge. Do not repurpose universal or spring method names for product-only surfaces.

## Response shape

Every `composition.*_health` method MUST return at least:

```json
{
  "healthy": true,
  "deploy_graph": "graph_name",
  "subsystems": { "subsystem_name": "ok" }
}
```

`healthy` is boolean. `deploy_graph` identifies the active graph. `subsystems` maps subsystem identifiers to `ok`, `degraded`, or `unavailable`. Implementations MAY add fields such as `bonding_support`, `capabilities_count`, or `science_domains`.

## Rules

- Universal method names are stable; do not rename them in new work.
- Spring methods use the spring’s domain name (`science`, `geology`, `physics`, `game`, and so on).
- Product methods use the product’s registered name and optional layer suffix.
- All methods return the minimum response shape above; optional fields must not replace or contradict it.

---

## FILE: `compositions/COMPOSITION_ROUTING_STANDARD.md`

# Composition Routing Standard

**Authority**: Overwatch + Ecosystem Convention
**Status**: Active (Wave 155h — reviewed, content current)
**Date**: 2026-07-29
**Prerequisites**: `../operations/GATEHOUSE_DARKFOREST_STANDARD.md`, `../foundations/DIDERM_DOMAIN_ARCHITECTURE.md`

---

## Purpose

This standard defines how live compositions (protoKarya projects and
other deployed products) register with the sovereign routing
infrastructure, ingest external data, and expose capabilities to
the mesh.

Every composition that wants a `*.primals.eco` subdomain or mesh
capability registration MUST follow this standard.

---

## Requirements

### 1. Subdomain Registration

Compositions receive subdomains through the `*.primals.eco` wildcard
DNS. No Cloudflare changes are needed. Only a Caddy server block
on golgi is required.

**Standard**: `prefix.primals.eco` subdomain is the REQUIRED pattern
for all live compositions. Path-based routing on the root domain
(`primals.eco/path/`) is NOT standard and MUST NOT be used for new
compositions. The root domain is reserved for sporePrint content.

**Rule**: Add a Caddy block to `provision/provision-golgi.sh` with
the `security_headers` import. The wildcard catch-all block returns
404 for unclaimed subdomains.

```caddy
myproject.primals.eco {
    import security_headers
    reverse_proxy MESH_IP:PORT
}
```

Upstream MUST be the WireGuard mesh IP of the gate running the
service (`10.13.37.x:PORT`), not `localhost`. Caddy on golgiBody
proxies over the WireGuard mesh to the target gate.

### Root Domain Redirect

The root domain `primals.eco` redirects to `sporeprint.primals.eco`
(the ecosystem's public face). No compositions serve from the root.

```caddy
primals.eco {
    import security_headers
    redir https://sporeprint.primals.eco{uri} permanent
}
```

### 2. Drawbridge Capability Registration

Compositions that serve capabilities MUST register them via songBird
drawbridge environment variables:

```bash
SONGBIRD_DRAWBRIDGE_ROUTES=/path=capability_name
SONGBIRD_PROXY_ROUTES=capability_name=http://backend:port
```

This auto-registers the capability in the IPC registry and announces
it to mesh peers. Remote gates can `capability.call("capability_name")`
to reach this composition.

### 3. Data Ingestion via Weak Bonds

External data sources enter through drawbridge weak bonds. This is
the ONLY approved path for external data entering the sovereign
interior.

**Ingestion flow**:

```
External API (USGS, NCBI, ArcGIS, etc.)
  → HTTP/HTTPS fetch (weak bond, zero trust)
    → BLAKE3 hash (integrity verification)
      → NestGate CAS store (content-addressed)
        → Loam Certificate mint (provenance attribution)
          → Available as capability across mesh
```

**Requirements**:
- All fetched data MUST be BLAKE3 hashed before storage
- Source attribution MUST be recorded (sweetGrass braid minimum)
- Data MUST land in NestGate CAS, not local filesystem
- Ingestion SHOULD be idempotent (same data = same hash = no duplicate)

### 4. Domain Trust Levels

| Domain | Layer | What Deploys Here |
|--------|-------|-------------------|
| `*.primals.eco` | Intra-membrane (shared ecosystem) | Public compositions, shared data, tools, docs |
| `*.primal.eco` | Inner membrane (personal sovereign) | Private compositions, ceremonies, sovereign data |
| `*.nestgate.io` | Data service point | Federated data gateway, CAS queries, API interactions |

**Rule**: The same composition code can deploy to both domains. The
domain determines the trust level, which determines what data is
accessible and what provenance is required.

### 5. Composition Manifest

Every composition SHOULD have a manifest file declaring its
capabilities, data sources, and primal dependencies:

```toml
[composition]
name = "footPrint"
org = "protoKarya"
subdomain = "footprint.primals.eco"
trust_level = "outer"

[capabilities]
exposed = ["gis.render", "gis.layers", "gis.search"]

[data_sources]
usgs = { type = "weak_bond", url = "https://basemap.nationalmap.gov" }
osm = { type = "weak_bond", url = "https://tile.openstreetmap.org" }

[primals]
required = ["nestGate", "songBird", "petalTongue"]
optional = ["bearDog"]
```

### 6. Security Headers

All compositions served through Caddy MUST import the standard
security headers snippet:

```caddy
(security_headers) {
    header {
        Strict-Transport-Security "max-age=63072000; includeSubDomains; preload"
        X-Frame-Options "DENY"
        X-Content-Type-Options "nosniff"
        Permissions-Policy "geolocation=(), microphone=(), camera=()"
        -Server
    }
}
```

CSP (Content-Security-Policy) MUST be composition-specific to
allow the external origins the composition needs. Compositions
loading external tiles, scripts, or images (e.g., Esri, OSM) MUST
declare those origins in `img-src`, `script-src`, etc. A missing
CSP allowlist will cause silent failures (blank maps, broken data).

**footPrint CSP example** (tile and data sources):

```caddy
header Content-Security-Policy "default-src 'self'; img-src 'self' https://server.arcgisonline.com https://*.tile.openstreetmap.org https://tiles.arcgis.com; connect-src 'self' https://nominatim.openstreetmap.org https://overpass-api.de https://epqs.nationalmap.gov https://hazards.fema.gov https://sdmdataaccess.sc.egov.usda.gov https://gisagocss.state.mi.us https://gis2.cityofeastlansing.com"
```

---

## Composition Lifecycle

```
1. DESIGN    — Define capabilities, data sources, primal deps
2. DEVELOP   — Build in protoKarya or relevant org
3. REGISTER  — Add Caddy block + drawbridge routes
4. DEPLOY    — Binary to depot, systemd service, mesh announce
5. VALIDATE  — primalSpring scenario confirms capability.call works
6. OPERATE   — Live on *.primals.eco, data flowing, capabilities exposed
7. FEDERATE  — Other compositions consume via capability.call
```

### Adding a Composition (Checklist)

- [ ] Composition code in appropriate org (protoKarya, sporeGarden, etc.)
- [ ] Caddy block in `provision-golgi.sh` with `security_headers`
- [ ] `SONGBIRD_DRAWBRIDGE_ROUTES` and `SONGBIRD_PROXY_ROUTES` configured
- [ ] Data sources documented with ingestion endpoints
- [ ] NestGate CAS wired for content storage (if applicable)
- [ ] primalSpring validation scenario created
- [ ] Security headers verified (`darkforest --scope outer --target subdomain`)
- [ ] Composition manifest TOML created

---

## Deployment Chain

The full path from user to service for `prefix.primals.eco`:

```
User browser
  → DNS: *.primals.eco → golgiBody VPS (Cloudflare wildcard A record)
    → Cloudflare (outer membrane firebreak — DDoS absorber, CDN)
      → Caddy on golgiBody (TLS termination, Host-header routing)
        → reverse_proxy MESH_IP:PORT (over WireGuard to target gate)
          → songBird drawbridge (capability resolution, port solving)
            → Local service (footPrint, esotericWebb, etc.)
```

**songBird's role**: The inner membrane port solver. Drawbridge
listens at `:7780`, maps HTTP paths to capabilities via
`SONGBIRD_DRAWBRIDGE_ROUTES`, resolves capabilities to local
service URLs via `SONGBIRD_PROXY_ROUTES`, and optionally proxies
external "weak bond" APIs through a domain-validated allowlist.

**Production optimization**: For external HTTPS data sources (tiles,
GIS APIs), Caddy handles the proxy directly via imported snippets
from `songBird/infra/caddy/`. This avoids drawbridge overhead for
high-volume tile traffic. Drawbridge handles internal capability
routing and the JSON-RPC bridge.

## Current Compositions (Wave 150c)

| Composition | Subdomain | Gate | Status | Capabilities |
|------------|-----------|------|--------|-------------|
| sporePrint | `sporeprint.primals.eco` | golgiBody | NEEDS MIGRATION (currently on root) | `content.serve` |
| footPrint | `footprint.primals.eco` | sporeGate | DEPLOYED (routing broken) | GIS proxy (10 hosts) |
| esotericWebb | `webb.primals.eco` | flockGate | DEPLOYED (Caddy missing) | `esotericwebb` |
| TOPO-VIS | `live.primals.eco` | sporeGate | LIVE | `topo.visualize` |
| JupyterHub | `lab.primals.eco` | ironGate | LIVE | `jupyter` |
| Forgejo | `git.primals.eco` | golgiBody | LIVE | `forge.serve` |
| Nest Atomic | `membrane.primals.eco` | golgiBody | LIVE | Tower + Nest services |
| tideGlass | `tideglass.primals.eco` | — | PLANNED | GPS reversal screening |
| helixVision | `helix.primals.eco` | — | PLANNED | Expression analysis |

---

## References

- `../operations/GATEHOUSE_DARKFOREST_STANDARD.md` — Bond escalation, drawbridge spec
- `../foundations/DIDERM_DOMAIN_ARCHITECTURE.md` — Domain trust levels, membrane layers
- `../GLOSSARY.md` — Drawbridge, weak bonds, Loam Certificates
- `whitePaper/gen5/foundations/COMPOSITION_ROUTING_PATTERN.md` — Full pattern documentation
- `whitePaper/gen5/foundations/EXTERNAL_SOVEREIGNTY_PATTERN.md` — Collaborator gate routing
- `provision/provision-golgi.sh` — Caddy configuration source of truth

---

## Changelog

| Wave | Change |
|------|--------|
| 138a | Initial: formalized composition routing standard from ad-hoc footPrint and JupyterHub deployments. Wildcard DNS, drawbridge registration, data ingestion via weak bonds, trust levels by domain. |
| 150c | Subdomain standard enforced: `prefix.primals.eco` is REQUIRED. Path-based routing prohibited for new compositions. footPrint corrected to `footprint.primals.eco`. esotericWebb changed from `/webb/` path to `webb.primals.eco` subdomain. CSP requirements strengthened. Deployment chain and songBird role documented. |
| 150d | Root domain redirect: `primals.eco` → `sporeprint.primals.eco`. sporePrint gets own subdomain. Domain terminology refined: `primals.eco` = intra-membrane, `primal.eco` = inner membrane, `nestgate.io` = data service point. |

---

## FILE: `compositions/COMPOSITION_TICK_MODEL_STANDARD.md`

# Composition Tick Model Standard

**Version:** 1.0.0
**Date:** April 27, 2026
**Audience:** Springs, gardens, biomeOS, and any composition with temporal requirements
**Status:** Active Standard
**License:** AGPL-3.0-or-later

---

## Purpose

Different domains have fundamentally different temporal requirements:

- **Games** need 60Hz fixed-timestep ticks
- **Physics** needs convergence-driven iteration (variable step, halt on convergence)
- **ML inference** needs event-driven polling (respond when ready)
- **Agriculture** uses seasonal time steps (daily/weekly/monthly)
- **Health** uses convergence checks on clinical thresholds
- **Uncertainty** needs Monte Carlo iteration counts

When biomeOS manages a heterogeneous cell graph — a game UI running over
a physics simulation with provenance recording — these temporal models must
coexist. This standard defines how domains declare their temporal requirements
and how the composition engine adapts.

---

## Tick Classes

Every node in a deploy graph operates under one of five temporal classes.

| Class | Description | Trigger | Budget | Examples |
|-------|-------------|---------|--------|----------|
| **Continuous** | Fixed-timestep loop | Timer (Hz) | Per-frame ms budget | Game ticks (60Hz), animation, sensor polling |
| **Convergence** | Iterate until criterion met | State change | Per-iteration limit | Physics equilibrium, optimization, PK/PD steady-state |
| **Event** | Respond to discrete signals | IPC message | Response timeout | AI inference, user interaction, provenance commit |
| **Batch** | Process a dataset to completion | Data availability | Total wall-clock | ETL, validation suites, cross-spring benchmarks |
| **Seasonal** | Calendar or domain-period driven | Time interval | Period budget | Water balance (daily), crop cycle (weekly), audit (monthly) |

---

## Declaration in Deploy Graphs

### Continuous Tick

For nodes requiring fixed-timestep execution, declare in the graph header:

```toml
[graph]
name = "game_engine_tick"
coordination = "continuous"

[graph.tick]
target_hz = 60
max_frame_ms = 16
underrun_policy = "skip"    # "skip" | "catchup" | "warn"
```

Per-node tick budgets:

```toml
[[graph.node]]
name = "game_logic"
binary = "ludospring"
order = 3
health_method = "health.liveness"
by_capability = "game"
tick_method = "game.tick"
budget_ms = 8

[[graph.node]]
name = "render"
binary = "petaltongue"
order = 4
health_method = "health.liveness"
by_capability = "visualization"
tick_method = "render.frame"
budget_ms = 6
```

**`tick_method`**: The JSON-RPC method biomeOS calls each frame. The primal
receives `{"tick": N, "dt_ms": 16.67, "timestamp_ms": ...}` and must respond
within `budget_ms`.

**`underrun_policy`**:
- `skip`: Drop the frame, continue at target Hz (default for games)
- `catchup`: Run multiple ticks to catch up (physics simulations)
- `warn`: Log warning, continue at reduced rate (monitoring)

### Convergence Tick

For nodes that iterate until a criterion is met:

```toml
[[graph.node]]
name = "physics_solver"
binary = "hotspring"
order = 3
health_method = "health.liveness"
by_capability = "physics"

[graph.node.convergence]
method = "science.iterate"
criterion = "residual"
threshold = 1e-12
max_iterations = 10000
timeout_ms = 30000
```

The composition engine calls `science.iterate` repeatedly. The primal
responds with `{"converged": false, "residual": 1.2e-8, "iteration": 42}`
until converged or limits are hit.

### Event-Driven

For nodes that respond to discrete events (default for most primals):

```toml
[[graph.node]]
name = "ai_agent"
binary = "squirrel"
order = 5
health_method = "health.liveness"
by_capability = "ai"

[graph.node.event]
poll_method = "inference.poll"
poll_interval_ms = 100
timeout_ms = 5000
```

### Batch

For nodes that process a finite dataset:

```toml
[[graph.node]]
name = "validation_suite"
binary = "wetspring"
order = 6
health_method = "health.liveness"
by_capability = "science"

[graph.node.batch]
method = "science.validate_batch"
timeout_ms = 300000
progress_method = "science.progress"
progress_interval_ms = 5000
```

### Seasonal

For nodes driven by calendar or domain periods:

```toml
[[graph.node]]
name = "water_balance"
binary = "airspring"
order = 3
health_method = "health.liveness"
by_capability = "agriculture"

[graph.node.seasonal]
method = "science.seasonal_step"
period = "daily"               # "hourly" | "daily" | "weekly" | "monthly"
align_to = "midnight_utc"
```

---

## Heterogeneous Composition

A single cell graph can mix temporal classes. biomeOS schedules them
according to their declared requirements.

**Example: Game with physics substrate and provenance**

```toml
[graph]
name = "physics_game"
coordination = "continuous"

[graph.tick]
target_hz = 60

# Game logic: runs every frame
[[graph.node]]
name = "game_logic"
tick_method = "game.tick"
budget_ms = 4
# ... other fields ...

# Physics: converges asynchronously, game reads latest state
[[graph.node]]
name = "physics"

[graph.node.convergence]
method = "science.iterate"
threshold = 1e-8
max_iterations = 100
# Runs in parallel with game tick; game reads last-converged state

# Provenance: event-driven, records on state change
[[graph.node]]
name = "provenance"

[graph.node.event]
poll_method = "dag.poll_commits"
poll_interval_ms = 1000
# Records provenance asynchronously; never blocks game tick

# Render: runs every frame after game logic
[[graph.node]]
name = "render"
tick_method = "render.frame"
budget_ms = 10
depends_on = ["game_logic"]
```

**Scheduling rules:**

1. **Continuous nodes** execute every frame in dependency order
2. **Convergence nodes** run asynchronously; consumers read last-converged state
3. **Event nodes** are polled at their declared interval, independent of frame rate
4. **Batch nodes** run to completion, blocking only their dependents
5. **Seasonal nodes** fire at their declared period, independent of everything else

---

## Tick Budget Accounting

biomeOS tracks per-frame budget consumption:

```
Frame budget: 16.67ms (60Hz)
  game_logic:    4ms budget,  3.2ms actual  ✓
  render:       10ms budget,  9.1ms actual  ✓
  overhead:      2.67ms                     ✓
  total:                     12.3ms         under budget
```

When a frame exceeds budget, the `underrun_policy` applies:
- `skip`: Next frame advances game time by 2×dt (or more)
- `catchup`: Extra iterations until caught up (may spike CPU)
- `warn`: Log + continue, accepting temporal drift

---

## Primal Tick Contract

Primals that participate in continuous compositions MUST implement:

```json
// Request (from biomeOS each tick)
{
  "jsonrpc": "2.0",
  "method": "game.tick",
  "params": {
    "tick": 1042,
    "dt_ms": 16.67,
    "timestamp_ms": 1714254000000,
    "budget_ms": 4
  },
  "id": 1042
}

// Response (within budget_ms)
{
  "jsonrpc": "2.0",
  "result": {
    "tick": 1042,
    "elapsed_ms": 3.2,
    "state_changed": true
  },
  "id": 1042
}
```

**`state_changed`**: Signals to event-driven nodes (provenance, attribution)
that they should poll for new data. Reduces unnecessary provenance overhead
on idle frames.

---

## Shell Composition Library

The `nucleus_composition_lib.sh` currently uses a fixed `POLL_INTERVAL` for
all health checks and event polling. For compositions with mixed temporal
requirements, override per-node:

```bash
POLL_INTERVAL=100    # Default: 100ms for event polling
TICK_HZ=60           # For continuous compositions
TICK_BUDGET_MS=16    # Per-frame budget
CONVERGENCE_THRESHOLD=1e-12
CONVERGENCE_MAX_ITER=10000
```

---

## Spring Temporal Profiles

Each spring's temporal nature, discovered through convergent evolution:

| Spring | Primary Class | Secondary | Notes |
|--------|--------------|-----------|-------|
| **hotSpring** | Convergence | Batch | Physics converges; validation runs as batch |
| **wetSpring** | Batch | Convergence | Validation suites are batch; PK/PD models converge |
| **neuralSpring** | Event | Batch | Inference is event-driven; training is batch |
| **healthSpring** | Convergence | Event | Clinical thresholds converge; monitoring is event |
| **ludoSpring** | Continuous | Event | Game ticks at 60Hz; user input is event |
| **groundSpring** | Batch | Convergence | Monte Carlo is batch; inverse problems converge |
| **airSpring** | Seasonal | Batch | Water balance is seasonal; validation is batch |

---

## Future: Adaptive Tick Scheduling

The composition engine will evolve from fixed scheduling to adaptive:

1. **Current**: Fixed `target_hz`, fixed budgets
2. **Near term**: biomeOS PathwayLearner observes actual tick durations and suggests budget adjustments
3. **Medium term**: Dynamic Hz scaling — reduce frame rate when physics convergence is slow, restore when fast
4. **Long term**: Cross-gate tick coordination — Plasmodium-level temporal synchronization across bonded NUCLEUS instances

---

## Related Documents

- `DEPLOYMENT_AND_COMPOSITION.md` — Deploy graph schema and coordination patterns
- `GARDEN_COMPOSITION_ONRAMP.md` — Garden product integration
- `EVOLUTION_STATUS_WAVE66.md` — Seasonal evolution model
- `SPRING_COMPOSITION_PATTERNS.md` — Per-spring patterns
- `TOADSTOOL_SENSOR_CONTRACT.md` — Hardware sensor event timing

---

**Time is not one thing. Games tick. Physics converges. Science batches. Agriculture seasons. The composition engine adapts.**

---

## FILE: `compositions/CROSS_SPRING_COORDINATION_STANDARD.md`

# Cross-Spring Coordination Standard

**Version:** 1.0.0
**Date:** April 27, 2026
**Audience:** All springs, primalSpring, biomeOS
**Status:** Active Standard
**License:** AGPL-3.0-or-later

---

## Purpose

Springs evolved independently, but convergent evolution produced recurring
cross-spring patterns. neuralSpring formalized these as `science.cross_spring_*`
RPC methods. healthSpring independently evolved a five-way cross-spring bridge.
groundSpring produces shared baselines that other springs consume.

This standard extracts the common patterns and defines how springs coordinate
across domain boundaries without coupling.

---

## Principles

1. **No shared crates** — springs never import each other's code
2. **IPC only** — all cross-spring communication is JSON-RPC over UDS
3. **Capability routing** — route by domain capability, never spring name
4. **Graceful absence** — cross-spring calls degrade when siblings are unavailable
5. **Attribution flows** — cross-spring work carries provenance via sweetGrass

---

## Standard Cross-Spring Methods

These methods SHOULD be implemented by any spring that participates in
cross-spring coordination. The `science.cross_spring_*` namespace is
reserved for this purpose.

### `science.cross_spring_provenance`

Request provenance chain for a shared artifact across spring boundaries.

```json
{
  "jsonrpc": "2.0",
  "method": "science.cross_spring_provenance",
  "params": {
    "artifact_id": "wetspring_exp403_parity_v1",
    "depth": 3
  },
  "id": 1
}
```

Response:

```json
{
  "jsonrpc": "2.0",
  "result": {
    "chain": [
      {
        "spring": "wetspring",
        "experiment": "exp403",
        "version": "V151",
        "artifact_hash": "blake3:abc123...",
        "timestamp": "2026-04-27T12:00:00Z"
      },
      {
        "spring": "neuralspring",
        "experiment": "surrogate_training",
        "version": "V138",
        "artifact_hash": "blake3:def456...",
        "derived_from": "blake3:abc123...",
        "timestamp": "2026-04-27T13:00:00Z"
      }
    ]
  },
  "id": 1
}
```

### `science.cross_spring_benchmark`

Run a cross-spring benchmark using a shared baseline from another spring.

```json
{
  "jsonrpc": "2.0",
  "method": "science.cross_spring_benchmark",
  "params": {
    "baseline_spring": "groundspring",
    "baseline_id": "anderson_spectral_v1",
    "method": "anderson.localization_length",
    "params": { "disorder": 4.0, "system_size": 1000 },
    "tolerance": 1e-10
  },
  "id": 2
}
```

Response:

```json
{
  "jsonrpc": "2.0",
  "result": {
    "baseline_value": 23.456,
    "computed_value": 23.456000001,
    "within_tolerance": true,
    "tolerance_used": 1e-10,
    "provenance": {
      "baseline_source": "groundspring V124",
      "compute_method": "barracuda via IPC",
      "timestamp": "2026-04-27T14:00:00Z"
    }
  },
  "id": 2
}
```

### `science.cross_spring_validate`

Request another spring to validate a result using its domain expertise.

```json
{
  "jsonrpc": "2.0",
  "method": "science.cross_spring_validate",
  "params": {
    "requesting_spring": "healthspring",
    "domain": "uncertainty",
    "method": "measurement.bias_variance",
    "data": { "predictions": [1.0, 1.1, 0.9], "observations": [1.0, 1.0, 1.0] }
  },
  "id": 3
}
```

This enables the healthSpring five-way bridge pattern: healthSpring routes
clinical models through wet (gut diversity), neural (surrogates), hot
(spectral), air (exposure), and ground (uncertainty) — each spring
validates using its own domain expertise.

### `science.cross_spring_capabilities`

Discover what cross-spring coordination a sibling supports.

```json
{
  "jsonrpc": "2.0",
  "method": "science.cross_spring_capabilities",
  "params": {},
  "id": 4
}
```

Response:

```json
{
  "jsonrpc": "2.0",
  "result": {
    "spring": "groundspring",
    "version": "V124",
    "cross_spring_methods": [
      "science.cross_spring_benchmark",
      "science.cross_spring_validate"
    ],
    "shared_baselines": [
      "anderson_spectral_v1",
      "noise_decomposition_v1",
      "bootstrap_reference_v1"
    ],
    "validation_domains": [
      "measurement.bias_variance",
      "measurement.decompose",
      "measurement.bootstrap"
    ]
  },
  "id": 4
}
```

---

## Cross-Spring Routing Patterns

### Pattern 1: Shared Baselines (groundSpring → all)

groundSpring produces "labeled dirty data" baselines — reference datasets
with known noise profiles, uncertainty bounds, and expected values. Other
springs consume these for validation.

```
groundSpring publishes:
  anderson_spectral_v1    → consumed by hotSpring, neuralSpring
  noise_decomposition_v1  → consumed by wetSpring, airSpring
  bootstrap_reference_v1  → consumed by healthSpring
```

**How to consume**: Call `science.cross_spring_benchmark` with the
baseline ID. groundSpring returns the reference value; your spring
computes and compares.

**Future**: Shared baselines will be published as validated datasets
via NestGate content-addressed storage, discoverable via
`storage.fetch_external` with provenance certificates from loamSpine.

### Pattern 2: Five-Way Bridge (healthSpring hub)

healthSpring routes clinical compute models through five sibling springs,
each providing domain-specific validation:

```
healthSpring
  ├─ wetSpring:    gut diversity, colonization, hormesis
  ├─ neuralSpring: Hill equation surrogates, PopPK
  ├─ hotSpring:    lattice tissue models, Anderson spectral
  ├─ airSpring:    environmental exposure, hygiene hypothesis
  └─ groundSpring: uncertainty quantification, dose-response UQ
```

Each call uses `science.cross_spring_validate` with the target spring's
domain methods. healthSpring aggregates results into a clinical model.

This pattern is reusable — any spring can become a hub that routes
through siblings.

### Pattern 3: Precision Routing (neuralSpring)

neuralSpring's `science.precision_routing` determines which compute path
(CPU f64, GPU WGSL f64, GPU DF64, GPU f32) meets a requested tolerance:

```json
{
  "jsonrpc": "2.0",
  "method": "science.precision_routing",
  "params": {
    "operation": "matrix_multiply",
    "required_tolerance": 1e-14,
    "matrix_size": [1000, 1000]
  },
  "id": 5
}
```

Response:

```json
{
  "result": {
    "recommended_path": "cpu_f64",
    "alternatives": [
      { "path": "gpu_df64", "tolerance": 1e-13, "speedup": 12.0 },
      { "path": "gpu_f64", "tolerance": 1e-10, "speedup": 45.0 }
    ]
  }
}
```

Other springs call this before dispatching compute to make informed
precision-performance tradeoffs.

---

## Shared Baseline Publication Standard

Springs that produce reusable baselines SHOULD publish them with:

```json
{
  "baseline_id": "anderson_spectral_v1",
  "source_spring": "groundspring",
  "source_version": "V124",
  "domain": "measurement",
  "description": "Anderson localization length at W=4, L=1000",
  "expected_value": 23.456,
  "tolerance": 1e-10,
  "provenance": {
    "experiment": "exp_anderson_001",
    "python_baseline": "blake3:abc123...",
    "rust_validation": "blake3:def456...",
    "publication": "Anderson (1958), Phys. Rev. 109, 1492"
  }
}
```

Baselines are immutable once published. New versions get new IDs.

---

## Discovery

Cross-spring coordination requires discovering sibling springs at runtime.
Use the same tiered socket discovery as primal discovery
(`SPRING_COMPOSITION_PATTERNS.md` §3), but with spring socket naming:

```
$XDG_RUNTIME_DIR/biomeos/groundspring-${FAMILY_ID}.sock
$XDG_RUNTIME_DIR/biomeos/wetspring-${FAMILY_ID}.sock
```

Or via biomeOS Neural API:

```json
{
  "jsonrpc": "2.0",
  "method": "capability.discover",
  "params": { "capability": "measurement" },
  "id": 1
}
```

biomeOS returns the socket path for the spring providing that capability.

---

## Graceful Degradation

Cross-spring calls MUST degrade gracefully:

```rust
pub fn cross_spring_validate(
    bridge: &PrimalBridge,
    domain: &str,
    method: &str,
    data: serde_json::Value,
) -> CrossSpringResult {
    match bridge.call_optional(domain, method, data) {
        Some(result) => CrossSpringResult::Validated(result),
        None => CrossSpringResult::Unavailable {
            domain: domain.to_string(),
            reason: "sibling spring not running",
        },
    }
}
```

A spring with no running siblings operates in isolation — all cross-spring
calls return `Unavailable` and the spring's own domain logic proceeds.

---

## Attribution for Cross-Spring Work

When Spring A uses Spring B's validation, attribution flows through
sweetGrass:

```
sweetGrass braid for "healthspring_clinical_model_v3":
  - healthSpring: Publisher (0.3)
  - wetSpring: Contributor — gut diversity validation (0.2)
  - neuralSpring: Contributor — surrogate training (0.2)
  - hotSpring: Validator — spectral verification (0.15)
  - groundSpring: Validator — uncertainty quantification (0.15)
```

The provenance trio records the cross-spring lineage. The attribution
distribution enables the sunCloud economic model to flow value across
spring boundaries.

---

## Evolution Path

| Phase | What | Status |
|-------|------|--------|
| 1 | `science.cross_spring_*` methods in neuralSpring | **Implemented** (V138) |
| 2 | healthSpring five-way bridge operational | **Implemented** (V59) |
| 3 | groundSpring shared baselines consumable via IPC | **Partially implemented** (V124) |
| 4 | Standardized baseline publication format | **This document** |
| 5 | NestGate-hosted shared baselines with loamSpine certificates | Planned |
| 6 | biomeOS cross-spring graph execution (multi-spring cell graphs) | Planned |
| 7 | sunCloud attribution flow across spring boundaries | Future |

---

## Related Documents

- `SPRING_COMPOSITION_PATTERNS.md` — Per-spring absorbed patterns
- `SPRING_INTERACTION_PATTERNS.md` — Cross-evolution and interop patterns
- `PROVENANCE_TRIO_INTEGRATION_GUIDE.md` — Wiring the provenance trio
- `EVOLUTION_STATUS_WAVE66.md` — How capabilities flow between layers
- `GATE_SPRING_OWNERSHIP.md` — Spring composition readiness matrix
- `SPRING_COORDINATION_AND_VALIDATION.md` — Handoffs and validation assignments

---

**Springs are independent laboratories. Cross-spring coordination makes their discoveries compound. Every sibling's validation strengthens the whole.**

---

## FILE: `compositions/MEMBRANE_CHANNEL_ARCHITECTURE.md`

<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Membrane Channel Architecture — External Surface Design

**Date**: May 13, 2026 (reviewed Wave 155h Jul 29, 2026 — All 3 channels LIVE. 9-gate mesh. S1-S4 GRADUATED.)
**Status**: Active
**Authority**: WateringHole Consensus

---

## Context

NUCLEUS is a closed cellular system — 13 primals communicating over Unix
sockets on a LAN, trusting each other via BTSP genetic identity. It is
self-contained. But a cell that cannot interact with its environment
cannot grow.

Three external interfaces are architecturally required for NUCLEUS to
participate in the wider internet. These are the **membrane channels** —
the controlled boundaries where the cell touches the outside world.

Each channel exists because of a physical or coordination constraint that
cannot be eliminated by software alone:

1. **Substrate** — a publicly routable IP address (physics: NAT requires a relay)
2. **Signal space** — a globally resolvable name (coordination: DNS is a shared namespace)
3. **Trust bridge** — a browser-trusted certificate (coordination: browsers ship CA root stores)

Everything inside the membrane is sovereign. Everything outside operates
on external substrate, in external signal space, or through an external
trust bridge. The membrane channels define what crosses that boundary,
how, and under what trust constraints.

---

## Three Channels

### Channel 1: Signal (DNS)

**Purpose**: Name resolution — tells the world where `primals.eco` lives.

| Property | Value |
|----------|-------|
| **Access** | Fully public, anyone can query |
| **Trust level** | Lowest — answers are public data, no secrets cross this channel |
| **What flows** | DNS queries/responses (A, AAAA, NS, MX, TXT for ACME) |
| **What cannot flow** | Content, auth tokens, encrypted sessions, relay traffic |
| **Port** | 53 (UDP/TCP) |
| **Primal owner** | knot-dns, operated under Songbird's DNS integration |
| **VPS process** | `knot-dns` (standalone, no shared state with other channels) |

**Permanently external**: The DNS registrar holds NS delegation for
`primals.eco`. This is a shared global namespace — ICANN, the `.eco`
registry, and the registrar coordinate name ownership. You cannot
self-host domain registration. This is analogous to a street address:
the postal system assigns it, you occupy it.

**Sovereign component**: Authoritative DNS resolution. knot-dns on
your infrastructure answers "where is primals.eco?" — Cloudflare is
removed from the resolution path entirely. The registrar knows your
NS IPs and nothing else.

**Mitigation**: Multiple domains on different registrars provide
redundancy. Onion addresses (`.onion` via Songbird Tor integration)
bypass DNS entirely for Tor-capable clients.

### Channel 2: Relay (NAT Traversal)

**Purpose**: Punch through NAT so peers can reach your LAN.

| Property | Value |
|----------|-------|
| **Access** | BTSP-authenticated peers only (BearDog HMAC credentials) |
| **Trust level** | Medium — relay sees encrypted packet metadata (source/dest IP, timing) but not content |
| **What flows** | BTSP-encrypted opaque bytes between NAT'd endpoints |
| **What cannot flow** | Plaintext content, DNS queries, HTTPS sessions |
| **Port** | 3478 (TURN standard, RFC 5766) |
| **Primal owner** | Songbird (`songbird relay` binary, 836 lines) |
| **VPS process** | `songbird relay` (stateless, credential-gated) |

**Permanently external**: A publicly routable IPv4 address. When two
machines are both behind NAT, neither can reach the other directly.
STUN can punch through simple NAT, but symmetric NAT (most consumer
routers) blocks it. A relay with a public IP is the only physics-level
solution. This is analogous to renting a mailbox — you need a
reachable address, but the mail is sealed.

**Sovereign component**: Everything except the IP address. The relay
binary is a stripped static ELF from plasmidBin. Credentials are
BearDog HMAC material. Traffic is BTSP-encrypted end-to-end before
reaching the relay. The VPS provider sees opaque bytes, source/dest
IPs, and timing metadata. Content is invisible.

**Portability**: The relay is stateless. Move it to a different
provider by copying one binary, one systemd unit, and updating DNS.
Zero state migration, zero vendor lock-in.

**What it replaces**: `cloudflared` (Cloudflare Tunnel). Today
cloudflared relays traffic through Cloudflare's infrastructure —
they operate the relay, see connection metadata, and control the
control plane. Songbird relay eliminates all of that.

### Channel 2b: Remote Desktop (RustDesk)

**Purpose**: Sovereign remote desktop access to geo-delocalized gates.

| Property | Value |
|----------|-------|
| **Access** | RustDesk-encrypted, server public key required |
| **Trust level** | Medium — relay sees only opaque encrypted desktop traffic |
| **What flows** | RustDesk-encrypted remote desktop sessions |
| **What cannot flow** | Plaintext content, DNS queries, BTSP IPC, credentials |
| **Ports** | 21115 (TCP, NAT test), 21116 (TCP+UDP, ID/hole-punch), 21117 (TCP, relay) |
| **Software** | RustDesk `hbbs` + `hbbr` (AGPL-3.0 symbiotic partner) |
| **VPS process** | `hbbs` (rendezvous) + `hbbr` (relay) — two lightweight Rust binaries |

**Relationship to Channel 2**: RustDesk complements Songbird. Both are
relay services on the cellMembrane that see only encrypted opaque bytes.
Songbird relays BTSP-encrypted primal IPC; RustDesk relays encrypted
remote desktop sessions. Together they provide the full NAT traversal
surface for both programmatic and human access to remote gates.

**Sovereignty**: The RustDesk server is self-hosted — no third-party
rendezvous or relay. The server generates its own `id_ed25519` keypair;
only clients configured with the matching public key can connect. The
VPS provider sees encrypted traffic — noise.

### Channel 3: Surface (TLS + Content)

**Purpose**: Browser-accessible HTTPS surface for `primals.eco` and API endpoints.

| Property | Value |
|----------|-------|
| **Access** | Public for content download; BTSP-authenticated for API/interactive |
| **Trust level** | Highest external — TLS private keys live here, session state crosses this boundary |
| **What flows** | HTTPS sessions, static content (Zola site, plasmidBin downloads), ACME challenges |
| **What cannot flow** | Relay traffic, DNS resolution, internal NUCLEUS IPC |
| **Ports** | 443 (HTTPS), 80 (ACME HTTP-01 challenge only) |
| **Primal owner** | BearDog (TLS termination, ACME client) + NestGate (content serving) |
| **VPS process** | `beardog-tls` + `nestgate` (or reverse-proxied from gate hardware) |

**Permanently external**: Let's Encrypt (or any ACME-compatible CA)
provides browser-trusted certificate signatures. Browsers won't
connect to HTTPS without a certificate signed by a CA they trust.
Running your own CA doesn't help — no browser ships your root cert.
This is analogous to a passport stamp: your cell is fully functional
without it, but the broader organism (the browser ecosystem) will
reject you without this surface marker.

**Sovereign component**: All TLS termination, private key generation,
content serving, and session management. Let's Encrypt sees your domain
name and that you requested a cert. They do NOT see your traffic, your
keys, or your content. The ACME protocol is open (RFC 8555), the
client is BearDog's, and alternative CAs exist (ZeroSSL, BuyPass,
Google Trust Services).

**What it replaces**: Cloudflare edge TLS proxy. Today Cloudflare
terminates TLS for `primals.eco`, holds the certificate private keys,
and sees all traffic in plaintext at their edge. BearDog TLS
eliminates all of that — the private key never leaves your
infrastructure.

---

## Channel Isolation

Channels are **process-isolated** — separate binaries with no shared
state, no shared sockets, no shared memory. Even on a single VPS, a
compromise of one channel does not grant access to another.

| Boundary | Enforced by |
|----------|-------------|
| Channel 1 cannot read relay traffic | Separate process, different port, no relay credentials |
| Channel 2 cannot serve content | No TLS keys, no content store, no HTTP listener |
| Channel 2b cannot access TURN | Separate process, different port, no TURN credentials |
| Channel 3 cannot resolve DNS | No knot-dns zone files, different process |
| No channel can reach internal NUCLEUS | VPS has no LAN access; relay forwards opaque bytes only |

### Firewall Rules (per-channel, composition-aware)

Firewall rules are **composition-aware**: only ports required by deployed
channels are opened. `deploy_membrane.sh` configures UFW based on the
active composition, not a static full-channel list.

```bash
# Always open: management
-A INPUT -p tcp --dport 22 -j ACCEPT   # SSH (key-only, fail2ban)

# Channel 2: Relay — open when relay or tower composition is active
-A INPUT -p udp --dport 3478 -j ACCEPT
-A INPUT -p tcp --dport 3478 -j ACCEPT

# Channel 2b: RustDesk — open when rustdesk or tower composition is active
-A INPUT -p tcp --dport 21115 -j ACCEPT   # NAT type test
-A INPUT -p tcp --dport 21116 -j ACCEPT   # ID registration
-A INPUT -p udp --dport 21116 -j ACCEPT   # Hole punching
-A INPUT -p tcp --dport 21117 -j ACCEPT   # Relay

# Channel 1: Signal — open only when DNS channel is deployed
-A INPUT -p udp --dport 53 -j ACCEPT
-A INPUT -p tcp --dport 53 -j ACCEPT

# Channel 3: Surface — open only when TLS channel is deployed
-A INPUT -p tcp --dport 443 -j ACCEPT
-A INPUT -p tcp --dport 80 -j ACCEPT

# Default deny
-A INPUT -j DROP
```

Each channel binds only to its assigned port(s). No channel listens
on another channel's ports. The `songbird relay` binary does not open
port 443. The `beardog-tls` binary does not open port 3478. Ports for inactive channels remain closed. The current Tower + Channel 3 Surface
deployment opens 22/tcp, 80/tcp, 443/tcp, 3478/udp+tcp, and 21115-21117/tcp+udp.

---

## Deployment Models

### Model A: Single VPS (interstadial start)

All three channels on one box. Current: ~$12/mo (2GB RAM, Tower composition).
Channels are separated by port and process, not by machine.

```
VPS (one public IP)
  :53          → knot-dns process       [Channel 1: Signal]
  :3478        → songbird relay         [Channel 2: Relay]
  :21115-21117 → hbbs + hbbr           [Channel 2b: RustDesk]
  :443         → beardog-tls + nestgate [Channel 3: Surface]
  :80          → ACME challenge only    [Channel 3: Surface]
  :22          → SSH (operator only)    [Management]
```

All binaries are static musl ELFs from plasmidBin. No runtime
dependencies on the VPS beyond a Linux kernel. Deploy by copying
binaries + systemd units. Tear down by wiping the box.

### Model B: Multi-VPS tiered (stadial hardening)

Each channel on a separate VPS, potentially with different providers
or in different jurisdictions. Higher isolation (~$12-15/mo).
Compromise or seizure of one channel does not expose the others.

```
VPS-1 (provider A, jurisdiction X)     [Channel 1: Signal]
  :53   → knot-dns

VPS-2 (provider B, jurisdiction Y)     [Channel 2: Relay]
  :3478 → songbird relay

VPS-3 (provider C, jurisdiction Z)     [Channel 3: Surface]
  :443  → beardog-tls + nestgate
  :80   → ACME
```

DNS NS records point to VPS-1. TURN credentials reference VPS-2.
TLS terminates at VPS-3. Each box is independently replaceable.

### Model C: Hybrid (router + VPS)

If your ISP provides a static IP (or you configure DDNS), Channel 3
can run directly on gate hardware behind router port forwarding.
BearDog TLS terminates on your own iron. Only Channels 1 and 2
require a VPS.

```
Your router (:443 forwarded to gate)   [Channel 3: Surface]
  gate:443 → beardog-tls + nestgate

VPS (:53 + :3478)                      [Channels 1+2: Signal + Relay]
  :53   → knot-dns
  :3478 → songbird relay
```

This eliminates the VPS from the highest-trust channel (TLS keys
never leave your hardware) while retaining a public relay point for
NAT traversal and DNS resolution.

---

## Mapping to Existing Tiering Systems

### Songbird STUN Sovereignty-First Escalation

Source: `primalSpring/ecoPrimal/src/bonding/stun_tiers.rs`

| STUN Tier | Description | Membrane Channel |
|-----------|-------------|-----------------|
| 1 | Genetic Lineage Relay (family-only, highest trust) | Internal — no membrane crossing |
| 2 | Self-Hosted STUN (your infrastructure) | **Channel 2: Relay** (your VPS) |
| 3 | Public STUN (community servers, address discovery) | External — used for address probing only |
| 4 | Rendezvous (future, gaming platforms) | External — future channel |

The VPS relay is STUN Tier 2 — your infrastructure, your binary, your
credentials. LAN traffic stays at Tier 1 and never touches the
membrane. The sovereignty-first strategy ensures Tier 1 is always
preferred when available.

### CompositionContext Discovery Escalation

Source: `primalSpring/ecoPrimal/src/composition/context.rs`

| Discovery Tier | Mechanism | Membrane Channel |
|----------------|-----------|-----------------|
| 1 | Songbird routing (`ipc.resolve`) | Internal — no membrane crossing |
| 2 | biomeOS Neural API | Internal — no membrane crossing |
| 3 | UDS filesystem convention | Internal — same machine only |
| 4 | Socket registry / manifests | Internal — self-registered |
| 5 | TCP probing on well-known ports | **VPS-reachable** — crosses membrane |

Only Discovery Tier 5 (TCP probing) can reach across the membrane via
Channel 2 (relay) or Channel 3 (surface). Tiers 1-4 operate entirely
within NUCLEUS over Unix sockets and never touch external substrate.

### BTSP Security Phases

Source: `wateringHole/compute-sharing/SOVEREIGN_COMPUTE_SHARING.md`

| BTSP Phase | Channel 1 (Signal) | Channel 2 (Relay) | Channel 3 (Surface) |
|------------|--------------------|--------------------|---------------------|
| 0: Manual | Public DNS, no auth | No relay (cloudflared) | Cloudflare TLS proxy |
| 1: Tunnel + Auth | knot-dns, no auth | Songbird relay, HMAC credentials | BearDog TLS, PAM auth |
| 2: BTSP Auth | No change | BTSP identity on relay credentials | BTSP identity on sessions |
| 3: BTSP Transport | DoT encrypted queries | BTSP AEAD on relay channel | BTSP AEAD on sessions |
| 4: Full BTSP | Sovereign DNS, policy-gated | Policy-automated relay | Full sovereign surface |

Each BTSP phase hardens the channels progressively. Phase 1 is the
interstadial entry point. Phase 4 is the stadial endgame.

### Hardware Security Evolution (SoloKey / FIDO2)

Both ironGate and eastGate have **SoloKey 2** devices plugged in,
providing a hardware security foundation for late-term BTSP evolution.

| BTSP Phase | Hardware Security Role | Status |
|------------|----------------------|--------|
| 1: Tunnel + Auth | SoloKey detected, software-only key generation | **Current** (exp096 Phase 4) |
| 2: BTSP Auth | BearDog FIDO2/CTAP2 for physical-presence authentication on BTSP handshakes | Near-term |
| 3: BTSP Transport | SoloKey as hardware attestation for gate identity — "this gate has a physical key" as a trust signal | Mid-term |
| 4: Full BTSP | SoloKey as first-class identity primitive; hardware witness in `liveSpore.json` for provenance | Long-term |

The SoloKey witness enables a stronger provenance claim: physical human
presence at the gate during validation, anchored into the `liveSpore.json`
provenance trail. This is particularly valuable for geo-delocalized gates
where the operator is not physically present at all times.

### Tunnel Evolution Ladder

Source: `wateringHole/compute-sharing/TUNNEL_ACCESS_GUIDE.md`

| Tunnel Phase | External Dependency | Membrane Channel Used |
|--------------|---------------------|-----------------------|
| 1: Tailscale | Tailscale control plane | None (bypasses membrane) |
| 2: WireGuard | None (manual key management) | None (direct tunnel) |
| 3: Songbird NAT | VPS relay (self-hosted) | **Channel 2: Relay** |
| 4: Full BTSP | **Zero** | Channel 2 with BTSP-only transport |

The membrane channel model starts at Tunnel Phase 3. Earlier phases
use external tunnel providers (Tailscale, WireGuard) that bypass the
membrane architecture entirely. Phase 3 is where the channels become
sovereign.

---

## Evolution Path

### Interstadial (current — May 2026)

Deploy Model A (single VPS). Channel 2 Relay and Channel 3 Surface operational.
Channel 1 Signal pending (knot-dns not yet deployed). Shadow runs producing
comparison data against Cloudflare baselines for S1 and S4 cutovers.

- Channel 1: knot-dns — **PROPAGATED** (Jun 4) — `primal.eco` + `nestgate.io` zones live, DNSSEC enabled, public resolvers confirming
- Channel 2: Songbird relay — **LIVE** (replacing cloudflared)
- Channel 3: Caddy TLS on :80/:443 — **LIVE** (`membrane.primals.eco`, Let's Encrypt E8, 19MB sporePrint cache). BearDog TLS shadow on :8443 pending cutover.

### Stadial (next)

Harden channel isolation. Optionally split to Model B (multi-VPS).
BTSP Phase 2/3 authentication on Channels 2 and 3.

- Cloudflare fully removed (TLS cutover complete)
- cloudflared fully removed (relay cutover complete)
- Forgejo on Channel 3 surface (`git.primals.eco`)
- NestGate content serving replaces GitHub Pages
- Let's Encrypt ACME auto-renewal on Channel 3

### Post-stadial (H3 horizon)

Full sovereignty within the constraints of the three permanently
external interfaces (registrar, public IP, CA).

- Channel 3 optionally moves to gate hardware (Model C)
- GitHub becomes read-only mirror or is removed
- JupyterHub PAM replaced by BTSP-only auth
- All tunneling via BTSP Phase 4 — zero external software

---

## Atomic / Channel Correspondence

The membrane channels are not arbitrary — they map directly to the
NUCLEUS atomic model. The same primals that solve trust, discovery,
and content internally also solve those problems externally. The
membrane channels are the atomics turned inside-out.

| Membrane Channel | External Problem | Atomic |
|-----------------|-----------------|--------|
| **Channel 1: Signal** (DNS) | Name resolution, discovery | **Tower** — Songbird handles discovery + routing |
| **Channel 2: Relay** (NAT) | Authenticated encrypted forwarding | **Tower** — Songbird (relay) + BearDog (credentials) |
| **Channel 3: Surface** (TLS + content) | Content serving, certificate trust | **Node + Nest** — BearDog (TLS), NestGate (content) |

Channels 1+2 are **Tower deployed outward** — the trust boundary
facing the public internet. Channel 3 is **Node + Nest deployed
outward** — compute dispatch and content storage facing browsers.

Internally, Tower primals communicate over Unix sockets on the LAN.
Externally, the same Tower primals (Songbird, BearDog) run on a VPS
and relay encrypted traffic back to the LAN. The membrane is where
internal atomics become external surfaces.

---

## Inner/Outer Crypto Layer Architecture

The membrane is not just a firewall — it is a **cryptographic boundary**
with two distinct trust regimes. Traffic arriving from the public internet
uses one set of credentials and protocols; traffic arriving from inner
gates uses a completely different set. The membrane Tower mediates the
transition between them.

### Two Crypto Layers

```
┌──────────────────────────────────────────────────────────────────┐
│                    PUBLIC INTERNET (outer)                       │
│   Browsers, remote peers, DNS resolvers, ACME CAs               │
└───────┬────────────────────┬─────────────────────┬──────────────┘
        │ TLS (public CA)    │ TURN (HMAC)         │ DNS (plain)
        ▼                    ▼                     ▼
┌───────────────────── MEMBRANE VPS ──────────────────────────────┐
│                                                                  │
│   ┌────────────────────────────────────────────────────────────┐ │
│   │  OUTER LAYER — Extracellular Crypto                        │ │
│   │                                                            │ │
│   │  Protocol: TLS 1.3 (ACME certs), DNS, TURN HMAC            │ │
│   │  Trust:    Public CAs, shared DNS, credential-gated relay   │ │
│   │  Keys:     Let's Encrypt cert/key, TURN HMAC shared secret  │ │
│   │  Visible:  Domain names, IP addresses, timing metadata      │ │
│   │  Actors:   Browsers, remote peers, bots, scanners — anyone  │ │
│   └─────────────────────┬──────────────────────────────────────┘ │
│                         │                                        │
│   ┌─────────────────────▼──────────────────────────────────────┐ │
│   │  SELECTIVE PERMEABILITY — BearDog + SkunkBat                │ │
│   │                                                            │ │
│   │  BearDog:  Validates BTSP handshakes, manages crypto keys   │ │
│   │  SkunkBat: Audits cross-boundary traffic, threat assessment │ │
│   │  Policy:   Public content → pass through                    │ │
│   │            Private API → require BTSP identity              │ │
│   │            Relay bytes → opaque forwarding                  │ │
│   │            Credentials → inner-only, never cross outward    │ │
│   └─────────────────────┬──────────────────────────────────────┘ │
│                         │                                        │
│   ┌─────────────────────▼──────────────────────────────────────┐ │
│   │  INNER LAYER — Intracellular Crypto                        │ │
│   │                                                            │ │
│   │  Protocol: BTSP (genetic identity, AEAD sessions)           │ │
│   │  Trust:    FAMILY_SEED (shared between all gates)           │ │
│   │  Keys:     Ed25519 identity keys, BTSP session keys         │ │
│   │  Visible:  Only to gates that prove family membership       │ │
│   │  Actors:   ironGate, NUC, other NUCLEUS gates — family only │ │
│   └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└────────┬──────────────────────────────────────────┬─────────────┘
         │ BTSP tunnel (family key)                 │
         ▼                                          ▼
┌─────────────────┐                      ┌─────────────────┐
│  ironGate (LAN) │                      │  NUC (intake)   │
│  Full NUCLEUS   │                      │  Compute gate   │
└─────────────────┘                      └─────────────────┘
```

### Outer Layer: Extracellular Crypto

The outer layer speaks the internet's native protocols. Any actor on the
public internet can interact at this layer:

| Component | Protocol | Keys | Issuer |
|-----------|----------|------|--------|
| Channel 3 TLS | TLS 1.3 | ACME cert/key pair | Let's Encrypt (public CA) |
| Channel 2 TURN | HMAC-SHA256 | Shared secret | Self-generated |
| Channel 1 DNS | DNS (no encryption) | None | N/A |

The outer layer's security properties are limited by public internet
constraints: TLS certificates are issued by external CAs, DNS is
unauthenticated, and TURN credentials are HMAC shared secrets.
BearDog on the membrane manages all outer-layer key material.

### Inner Layer: Intracellular Crypto

The inner layer uses BTSP — the ecosystem's own genetic identity protocol.
Only gates that share the `FAMILY_SEED` can reach through the membrane:

| Component | Protocol | Keys | Issuer |
|-----------|----------|------|--------|
| Gate ↔ membrane | BTSP Phase 2+ | Ed25519 identity keys | Self-generated from FAMILY_SEED |
| Secrets delegation | BTSP-authenticated RPC | Session keys | BearDog handshake |
| Credential retrieval | `secrets.retrieve` | BTSP session token | BearDog on membrane |

The inner layer never speaks TLS, never uses public CAs, and never
exposes material to the outer layer. A browser cannot reach the inner
layer — it lacks the FAMILY_SEED required for BTSP handshake.

### Selective Permeability Rules

The membrane Tower (BearDog + SkunkBat) enforces what crosses between
layers. The rules are content-aware, not just port-based:

| Traffic Type | Direction | Policy |
|-------------|-----------|--------|
| Public content (website, downloads) | Outer → Inner | Pass through Channel 3 |
| API calls (authenticated) | Outer → Inner | Require BTSP identity via BearDog |
| Relay traffic (peer-to-peer) | Outer ↔ Inner | Opaque forwarding, no inspection |
| DNS queries | Outer → Inner | Answer from zone file, no inner contact |
| Credentials (API tokens, secrets) | Inner only | **Never cross outward** |
| FAMILY_SEED / identity keys | Inner only | **Never leave inner layer** |
| Audit logs | Inner → Outer | SkunkBat may export to inner gates, never outward |

### Credential Sharing Evolution

The mechanism for sharing credentials between gates evolves in lockstep
with the crypto layers:

| Phase | Mechanism | Trust Anchor | Where Credentials Live |
|-------|-----------|-------------|----------------------|
| **Short term** (now) | `age` + SSH ed25519 keys | Shared SSH key pair | Encrypted blob on VPS + gates |
| **Mid term** | BearDog `secrets.store`/`secrets.retrieve` via BTSP | FAMILY_SEED + BTSP handshake | BearDog's encrypted store on membrane |
| **Long term** | Autonomous rotation by membrane Tower | Membrane identity key | Generated and rotated by membrane BearDog, never shared as files |

Short-term tooling: `plasmidBin/membrane/share_credentials.sh` wraps
`age` encryption to SSH public keys. Any gate with the corresponding
private key can decrypt. See the script for usage.

### Tower on Membrane — Composition

When deployed with `--composition tower`, the membrane VPS runs the full
Tower atomic alongside the relay channels:

| Service | Role | Unit |
|---------|------|------|
| BearDog | BTSP handshake, secrets delegation, crypto key management | `beardog-membrane.service` |
| Songbird | Relay + discovery (Channel 2) | `songbird-relay.service` |
| SkunkBat | Defense audit, threat assessment, cross-boundary monitoring | `skunkbat-membrane.service` |

This composition enables the mid-term credential delegation pattern:
inner gates authenticate via BTSP to BearDog on the membrane, then
retrieve credentials without any file sharing.

### Evolution Milestones

1. **biomeOS on ironGate auto-provisions membrane channels** via
   `secrets.retrieve("membrane:doctl:token")` + `doctl`
2. **Membrane BearDog rotates TURN credentials autonomously** — no
   operator intervention for credential refresh
3. **Membrane NestGate serves public content** — replaces GitHub Pages,
   Channel 3 becomes sovereign
4. **Membrane SkunkBat audits all cross-boundary traffic** — anomaly
   detection on the membrane surface
5. **Operator's only role is initial FAMILY_SEED provisioning** and
   domain registration — everything else is autonomous

---

## cellMembrane fieldMouse Classification

The membrane VPS is formally classified as a **fieldMouse** deployment — the
first production instance of the fieldMouse deployment class on external
substrate.

| Property | Value |
|----------|-------|
| **Deployment class** | fieldMouse |
| **Composition** | Tower atomic (BearDog + Songbird + SkunkBat) + RustDesk (hbbs + hbbr) |
| **Substrate** | External (DigitalOcean VPS, nyc1) |
| **biomeOS** | None — static composition, no deploy graph |
| **Topology** | `ecoprimals-fieldmouse-chimera.yaml` (benchScale) |
| **Dark Forest** | Provider treated as non-family observer; sensitive data encrypted at rest |

The cellMembrane is not a gate, not a niche. It runs exactly the Tower
atomic turned outward — the same primals that handle trust, discovery, and
defense inside NUCLEUS, deployed to face the public internet.

### Hardening profile

Firewall is composition-aware — only ports required by active channels are
open. Current state (Tower + Channel 3 Surface live, May 2026):

| Port | Protocol | Purpose | Status |
|------|----------|---------|--------|
| 22 | TCP | SSH management (key-only, fail2ban) | **Open** |
| 80 | TCP | Channel 3: ACME challenge + redirect | **Open** (Caddy) |
| 443 | TCP | Channel 3: Surface (HTTPS) | **Open** (Caddy TLS, `membrane.primals.eco`) |
| 3478 | TCP + UDP | Channel 2: Relay (TURN) | **Open** |
| 21115 | TCP | Channel 2b: RustDesk NAT test | **Open** |
| 21116 | TCP + UDP | Channel 2b: RustDesk ID/hole-punch | **Open** |
| 21117 | TCP | Channel 2b: RustDesk relay | **Open** |
| 53 | UDP + TCP | Channel 1: Signal (DNS) | **Open** (knot-dns LIVE, Jun 4 — `primal.eco` + `nestgate.io`) |

Services purged: `exim4` (unnecessary mail server), `droplet-agent`
(opaque DO monitoring). Services added: `fail2ban` (SSH brute-force
protection), `hbbs-membrane` + `hbbr-membrane` (RustDesk relay).

See `CELLMEMBRANE_FIELDMOUSE_DEPLOYMENT.md` for the full fieldMouse
specification, escalation ladder, and BingoCube verification roadmap.

---

## Deployment Tooling

### `plasmidBin/deploy_membrane.sh`

Provisions and deploys membrane channels to a VPS. Five modes, three
compositions:

```bash
./deploy_membrane.sh provision --region nyc1                  # Create droplet + deploy (relay)
./deploy_membrane.sh deploy root@<ip>                         # Deploy relay to existing VPS
./deploy_membrane.sh deploy root@<ip> --composition rustdesk  # Relay + RustDesk
./deploy_membrane.sh deploy root@<ip> --composition tower     # Full Tower + RustDesk
./deploy_membrane.sh keys add root@<ip> --name "gate" --pubkey "ssh-ed25519 ..."
./deploy_membrane.sh keys list root@<ip>
./deploy_membrane.sh status root@<ip>                         # Health check
./deploy_membrane.sh teardown --name membrane-relay           # Destroy droplet
```

All modes support `--dry-run` for plan-only inspection.

| Composition | Components | Use case |
|-------------|------------|----------|
| `relay` (default) | Songbird only | Channel 2 relay, minimal footprint |
| `rustdesk` | Songbird + hbbs/hbbr | Relay + remote desktop for geo-delocalized gates |
| `tower` | BearDog + Songbird + SkunkBat + hbbs/hbbr | Full Tower atomic + RustDesk |

### `plasmidBin/membrane/` — unit templates and tooling

| File | Purpose | Status |
|------|---------|--------|
| `songbird-relay.service` | Channel 2: Relay (:3478) | **Active** |
| `hbbs-membrane.service` | Channel 2b: RustDesk rendezvous (:21116) | **Active** |
| `hbbr-membrane.service` | Channel 2b: RustDesk relay (:21117) | **Active** |
| `beardog-membrane.service` | Tower: BTSP + crypto identity | **Active** (deployed with `--composition tower`) |
| `skunkbat-membrane.service` | Tower: Defense + audit | **Active** (deployed with `--composition tower`) |
| `share_credentials.sh` | `age`-based credential sharing between gates | **Active** |
| `knot-dns.service` | Channel 1: Signal (:53) | Future |
| `beardog-tls.service` | Channel 3: Surface (:443) | Future |
| `nestgate-content.service` | Channel 3: Surface (:443) | Future |

Each unit is security-hardened (`NoNewPrivileges`, `PrivateTmp`,
`ProtectSystem=strict`, `MemoryMax`, `CPUQuota`).

### Credential management

| Phase | Tool | Storage |
|-------|------|---------|
| **Current** | `age` + SSH ed25519 keys via `share_credentials.sh` | Encrypted blob on VPS (`/opt/membrane/credentials.age`) |
| **Mid term** | BearDog `secrets.store`/`secrets.retrieve` via BTSP | BearDog encrypted store on membrane |
| **Long term** | Autonomous rotation by membrane BearDog | Never stored as files |

DigitalOcean API tokens are stored at `~/.config/doctl/token` with
`chmod 600`. The deployment script uses `doctl` CLI (authenticated
separately) and never reads the token file directly.

---

## What Is Permanently External

| Dependency | Why | Risk | Mitigation |
|------------|-----|------|------------|
| DNS registrar | Shared global namespace (ICANN) | Domain seizure | Multiple domains, different registrars; `.onion` as bypass |
| Public IP (VPS) | NAT requires a routable relay point | Provider misbehavior | Stateless binary, switch providers in minutes; Model B across jurisdictions |
| Let's Encrypt (CA) | Browsers require CA-signed certs | CA compromise or policy change | Multiple ACME CAs; Certificate Transparency detects mis-issuance; BTSP for non-browser clients |

These three cannot be eliminated by software. They are structural
properties of the internet as a shared medium. The membrane channel
architecture ensures they are the *only* external dependencies, and
that each one sees the minimum possible information about NUCLEUS
internals.

---

## biomeOS Support (v3.58)

As of biomeOS v3.58, `composition.deploy(graph)` recognizes `composition_model = "membrane"`
as a first-class deployment topology. Graph metadata is parsed, validated, and preserved
through the neural-to-deployment conversion pipeline. The `composition.deploy.shadow`
dry-run also reports the composition model in its validation output.

The `CompositionModel` enum (`nucleated` | `membrane`) is orthogonal to
`AtomicComposition` (Tower/Node/Nest/Nucleus) — the former describes infrastructure
topology, the latter describes which primal bundles are required.

---

## Cross-References

- `GLACIAL_SHIFT_READINESS.md` — Pillar 2 deployment targets map to membrane channels
- `compute-sharing/SOVEREIGN_COMPUTE_SHARING.md` — NUC intake pattern is Channel 3 surface
- `compute-sharing/TUNNEL_ACCESS_GUIDE.md` — Tunnel evolution phases map to Channel 2
- `plasmidBin/deploy_membrane.sh` — Agentic provisioning and deployment script (supports `--composition relay|rustdesk|tower`, `keys` management)
- `plasmidBin/membrane/songbird-relay.service` — Channel 2 systemd unit template
- `plasmidBin/membrane/hbbs-membrane.service` — Channel 2b RustDesk rendezvous unit template
- `plasmidBin/membrane/hbbr-membrane.service` — Channel 2b RustDesk relay unit template
- `plasmidBin/membrane/beardog-membrane.service` — Tower BearDog systemd unit template
- `plasmidBin/membrane/skunkbat-membrane.service` — Tower SkunkBat systemd unit template
- `plasmidBin/membrane/share_credentials.sh` — `age`-based credential sharing between gates
- `handoffs/SONGBIRD_WAVE202_RELAY_OPS_DEPLOYMENT_MAY12_2026.md` — Songbird relay ops readiness
- `CELLMEMBRANE_FIELDMOUSE_DEPLOYMENT.md` — cellMembrane as fieldMouse Tower on external substrate
- `handoffs/PROJECTNUCLEUS_MEMBRANE_VPS_HANDOFF_MAY14_2026.md` — cellMembrane VPS ownership handoff
- `primalSpring/ecoPrimal/src/bonding/stun_tiers.rs` — STUN sovereignty-first escalation
- `primalSpring/ecoPrimal/src/composition/context.rs` — Discovery escalation hierarchy
- `BTSP_PROTOCOL_STANDARD.md` — BTSP phase definitions
- `EVOLUTION_STATUS_WAVE66.md` — Interstadial/stadial transition model

---

## FILE: `compositions/PRIMAL_REGISTRY.md`

# Primal Registry - ecoPrimals Ecosystem

**Purpose**: Authoritative catalog of every primal, its primitives, its domain, and its role in the ecosystem  
**Audience**: Any primal seeking to understand what capabilities exist  
**Last Updated**: July 29, 2026 (Wave 155h — Deep evolution wave. 9 primals + cellMembrane shipped. ~70K+ tests. J6 CLOSED, J8 code shipped. BTSP 13/13. Tower debt 1. westGate+strandGate Tower LIVE. Compute Trio deployed. P0: glibc depot target for GPU primals.)

---

## How to Read This Document

Each primal entry below includes:

- **Domain**: What problem space this primal owns
- **Role**: What this primal does for the ecosystem
- **Primitives**: The atomic capabilities this primal provides
- **Phase**: Foundation (forms the NUCLEUS deployment architecture) or Post-NUCLEUS (builds emergent behaviors on the foundation)
- **Status**: Current production readiness
- **Participates In**: What composed systems this primal contributes to

---

## Foundation Primals

These primals form the NUCLEUS deployment architecture. They are production-ready, extensively tested, and required for core ecosystem function. This tier includes all original Phase 1 primals plus biomeOS, which has matured to foundation status through its role as the ecosystem orchestrator.

### BearDog - Cryptography Primal

**Domain**: Cryptographic operations and genetic lineage  
**Phase**: Foundation  
**Status**: Production Ready (A+ LEGENDARY, 99/100)

**Role**: BearDog is the cryptographic foundation of the ecosystem. Every signing operation, every encryption, every hash, every key exchange in the ecosystem flows through BearDog's primitives. It also manages genetic lineage - the family seed system that enables auto-trust between primals.

**Primitives**:

| Category | Primitives |
|----------|-----------|
| **Signatures** | Ed25519, ECDSA (P-256, P-384), RSA (PKCS#1 v1.5, PSS) |
| **Key Exchange** | X25519, ECDHE (P-256, P-384) |
| **AEAD Encryption** | ChaCha20-Poly1305, AES-128-GCM, AES-256-GCM |
| **Hashing** | BLAKE3, SHA-256, SHA-384, SHA-512, HMAC |
| **Key Derivation** | HKDF (TLS 1.3), TLS 1.2 PRF, PBKDF2, Argon2id |
| **Certificates** | X.509 generation, parsing, validation |
| **Genetic Crypto** | Lineage-based key derivation, beacon seeds, family seed management |
| **Dark Forest** | Challenge-response federation protocol |

**IPC Methods**: 72 JSON-RPC methods (69 crypto + 3 introspection)  
**Dependencies**: Zero C dependencies. 100% RustCrypto suite.

**Participates In**: Tower Atomic (with Songbird), NUCLEUS, RootPulse, BirdSong encryption, Dark Forest Federation

---

### Songbird - Network Primal

**Domain**: Network orchestration, discovery, and federation  
**Phase**: Foundation  
**Status**: Production Ready (S+, 100% BearDog delegation + Pure Rust Tor, 14,835+ tests, ~72% coverage, 30 crates, ecoBin v3.0, ACME HTTP-01 Phase 1, deep debt resolved)

**Role**: Songbird is the nervous system of the ecosystem. It handles all network communication - TLS, discovery, NAT traversal, and federation. It is the only primal that speaks to the external network directly; all others route through Songbird when external connectivity is needed.

**Primitives**:

| Category | Primitives |
|----------|-----------|
| **TLS** | TLS 1.3 (RFC 8446), TLS 1.2 fallback, Pure Rust via BearDog crypto delegation |
| **Discovery** | BirdSong encrypted UDP multicast, mDNS/DNS-SD, capability-based 6-layer strategy |
| **NAT Traversal** | Pure Rust STUN server (RFC 5389), relay server with lineage-based auth |
| **Federation** | Zero-trust progressive escalation, cross-tower routing |
| **Dark Forest** | Zero metadata leakage discovery, encrypted beacons |
| **Transport** | Multi-transport IPC (Unix sockets, abstract sockets, TCP) |

**Participates In**: Tower Atomic (with BearDog), NUCLEUS, RootPulse (discovery/federation), BirdSong protocol

---

### NestGate - Data Primal

**Domain**: Storage and content-addressed data management  
**Phase**: Foundation  
**Status**: Production Ready (A++ TOP 1%, 12,973 tests, P0/P1 audit resolved, live CLI health, FHS centralized, ZFS tier migration)

**Role**: NestGate provides all data persistence for the ecosystem. Content-addressed storage means data is identified by its hash, not its location. NestGate handles blob storage, tree structures, metadata, and quota management. It also provides capability-based service discovery.

**Primitives**:

| Category | Primitives |
|----------|-----------|
| **Storage** | `storage.put`, `storage.get`, `storage.delete`, `storage.list`, `storage.exists`, `storage.metadata`, `storage.copy`, `storage.move`, `storage.quota` |
| **Discovery** | `discovery.announce`, `discovery.query`, `discovery.list`, `discovery.metadata`, `discovery.capabilities` |
| **Metadata** | `metadata.store`, `metadata.retrieve`, `metadata.update`, `metadata.search` |
| **Health** | `health.check`, `health.metrics`, `health.ready`, `health.alive` |

**Storage Backends**: Filesystem, ZFS, object storage  
**Content Addressing**: BLAKE3 hashes  
**Optimization**: Entropy-based compression routing, zero-copy I/O with SIMD

**Participates In**: NUCLEUS, RootPulse (content storage), Nest Atomic (with Tower Atomic)

---

### Squirrel - AI Primal

**Domain**: AI model coordination and inference  
**Phase**: Foundation  
**Status**: Production Hardened (A++, 763 tests, capability purified: beardog→security_provider, adapter IPC wired)

**Role**: Squirrel provides sovereign AI capabilities through the Model Context Protocol (MCP). It routes AI tasks to appropriate models (local or remote), manages context windows, and coordinates multi-model workflows - all without compile-time coupling to any AI vendor.

**Primitives**:

| Category | Primitives |
|----------|-----------|
| **Inference** | Model inference routing, multi-provider support (OpenAI, Anthropic, Ollama, local) |
| **Context** | Advanced context window management, memory optimization |
| **Task Routing** | Intelligent routing based on task requirements and model capabilities |
| **MCP** | Multi-MCP coordination, sovereign operation |
| **Integration** | Vendor-agnostic AI, zero compile-time coupling |

**Architecture**: TRUE PRIMAL - runtime discovery, isomorphic IPC, multi-protocol (JSON-RPC + tarpc)

**Participates In**: Full NUCLEUS (all atomics + AI), RootPulse (intelligent merge resolution)

---

### ToadStool - Hardware Infrastructure Primal

**Domain**: Hardware discovery, capability probing, and compute orchestration  
**Phase**: Foundation  
**Status**: Production Ready (A++ GOLD STANDARD) — S333+ (Jul 16, 2026) — 23,000+ workspace tests (9,232+ lib-only), zero clippy warnings, 112 JSON-RPC methods (17 capability groups), ~85%+ line coverage (185K lines instrumented), cross-architecture (`cargo check --target x86_64-pc-windows-gnu` passes, S329), Linux hw crates `#[cfg(target_os = "linux")]`-gated, Unix IPC `#[cfg(unix)]`-gated, BearDog crypto delegation enforced (Node Atomic), capability-based discovery, zero production files >750L, zero production TODO/FIXME/HACK, 100% env centralized, zero `/tmp` hardcoding (3-tier: XDG > `/run/membrane` systemd > temp_dir), VFIO sovereign dispatch validated (Titan V), riboCipher CLEAR+MITO transport, Phase D live. **S333 structural debt**: 7 large files refactored (test extraction, −2,188 production lines), hardcoded primal name cleanup

**Role**: ToadStool is the hardware infrastructure primal. It discovers GPUs, NPUs, CPUs at runtime via sysfs/PCIe. It exposes compute substrates to the ecosystem via JSON-RPC 2.0 + tarpc IPC over Unix sockets. GPU job queue with cross-gate routing. Ollama model lifecycle management. Distributed workload dispatch across machines. Cloud cost estimation, compliance validation, and federation. Shader compilation proxy to coralReef with capability-based discovery and naga fallback. Cross-spring provenance tracking via `toadstool.provenance` method. BarraCuda (math dispatch) is a separate primal that consumes ToadStool's hardware capabilities via IPC.

**Primitives**:

| Category | Primitives |
|----------|-----------|
| **GPU Discovery** | Multi-adapter selection (`TOADSTOOL_GPU_ADAPTER`), `GpuAdapterInfo` (driver, f64, workgroups, buffer limits), cross-vendor (NVIDIA/AMD/Intel via WGPU/Vulkan) |
| **NPU Discovery** | Generic `NpuDispatch` trait, `AkidaNpuDispatch` adapter (VFIO/kernel/mmap), `NpuParameterController` trait |
| **CPU Discovery** | `/proc/cpuinfo` parsing, cache hierarchy (L2/L3/Infinity Cache), SIMD capability probing |
| **Hardware Transport** | Display (DRM/KMS), Capture (V4L2), Serial (USB) — frame protocol + `TransportRouter` |
| **GPU Job Queue** | Submit/status/result/cancel/list, cross-gate routing across machines |
| **Precision Routing** | `PrecisionRoutingAdvice` (F64Native, F64NativeNoSharedMem, Df64Only, F32Only), `precision_routing()` |
| **Sovereign Pipeline** | `HardwareFingerprint`, `is_sovereign_capable()`, `safe_allocation_limit` (NVK PTE guard), 12-variant `SubstrateCapabilityKind` |
| **Distributed** | Cross-gate GPU routing, cloud cost estimation, compliance validation, federation |
| **Ollama Integration** | Model lifecycle (list/load/inference/unload) via JSON-RPC |
| **Runtimes** | Native, WASM (wasmi), Python, Container (BYOB), GPU, NPU, Edge (Linux, RPi, ESP32, Arduino) |
| **Shader Proxy** | `shader.compile.*` proxy to coralReef with capability-based discovery, naga fallback |
| **Provenance** | `toadstool.provenance` — cross-spring flow matrix (19+ flows across 6 springs, 19 domains) |
| **Hardware Learning** | `compute.hardware.*` (observe/distill/apply/share_recipe/status), hw-learn pipeline, `RecipeStore`, `RegisterAccess` trait |
| **Firmware Inventory** | `FirmwareInventory` (probe/compute_viable/compute_blockers/needs_software_pmu) via nvpmu |
| **SPIR-V Codegen Safety** | `spirv_codegen_safety` module (`PrecisionBrain`, `NvkZeroGuard`, `HardwareCalibration`), root-cause rename from `nvvm_safety` |
| **IPC** | 96+ JSON-RPC 2.0 methods (semantic naming), tarpc typed RPC, Unix socket standard |

**Key principles**: Capability-based discovery (self-knowledge only), ecoBin compliant (pure Rust core), zero hardcoded primal names/ports, all unsafe blocks documented with `// SAFETY:`. Rust 1.82+ MSRV.

**Participates In**: Node Atomic (with Tower Atomic), NUCLEUS, serves hardware capabilities to BarraCuda

---

### BarraCuda - Math Primal

**Domain**: Pure mathematics — WGSL shaders, precision strategy, naga IR optimisation  
**Phase**: Foundation  
**Status**: Production Ready (A+) — v0.4.0 — 3,348+ tests, 803 WGSL shaders, 1,060+ Rust source files, zero unsafe, zero clippy warnings, AGPL-3.0-only, NVVM device poisoning guard (all proprietary NVIDIA architectures), DF64 safety probing (`df64_arith`, `df64_transcendentals_safe`), `NvvmDf64TranscendentalPoisoning` workaround, all env-configurable timeouts, idiomatic iterators, let-else patterns, capability-based discovery (zero hardcoded primal names), `split_at_mut` zero-copy LSTM, clean 3-tier precision model (F32/F64/Df64) aligned with coralReef `Fp64Strategy`, `CompileWgslRequest.fp64_strategy` IPC hint, runtime `shared_mem_f64` probe, `PrecisionRoutingAdvice`, `hill_activation`/`hill_repression` kinetics, f64-native pipeline cache, `bytes::Bytes` zero-copy I/O, thread-local GPU test throttling, `service` subcommand (genomeBin), FMA policy, health module (pkpd, microbiome, biosignal), stable GPU special functions; budded from ToadStool (S93), separate primal at `ecoPrimals/barraCuda/`. **Wave 109**: STARTUP-BC-01 RESOLVED — `--bind-mode / PRIMAL_BIND_MODE` standard envelope, `method.describe` (97 methods)

**Role**: BarraCuda is pure math. All math originates as WGSL shaders authored in f64 as the canonical precision. BarraCuda does not care about hardware — it writes the mathematics, coralReef compiles it, toadStool discovers and dispatches it. The precision tier (`Fp64Strategy`: f32 / f64 / df64) is the interface between barraCuda and coralReef. naga-IR optimisation (FMA fusion, DCE) operates on the math, not the hardware. Currently uses wgpu as a transitional dispatch substrate until coralReef's sovereign dispatch pipeline is integrated.

**Primitives**:

| Category | Primitives |
|----------|-----------|
| **Core** | 712 WGSL f64 shaders: matmul, relu, softmax, gelu, layer_norm, transpose, elementwise, reduce (incl. DF64 variants), broadcast |
| **Linear Algebra** | solve, cholesky, QR, SVD, LU, sparse eigensolve (Lanczos), GEMM f64, matrix inverse |
| **Scientific Computing** | Crank-Nicolson PDE, Richards equation, MD forces (Coulomb, Morse, Born-Mayer, Yukawa), PPPM electrostatics, HFB nuclear physics |
| **Lattice QCD** | 14 GPU shaders + host: Wilson action, HMC leapfrog, Dirac, CG solver, pseudofermion, polyakov loop |
| **Special Functions** | Bessel, Laguerre, Hermite, Legendre, spherical harmonics, digamma, beta, gamma, erf |
| **ML** | Attention (7 variants), Training losses (10 types), Optimizers (5 types), CNN ops |
| **Bioinformatics** | 31 GPU bio ops: kmer histogram, taxonomy FC, UniFrac, ANI, random forest inference, HMM, Dada2, Gillespie, Wright-Fisher |
| **Kinetics** | Hill activation/repression, Monod saturation, regulatory network primitives |
| **Precision Strategy** | `Fp64Strategy` (Native / Hybrid / Sovereign / Concurrent), `PrecisionRoutingAdvice` (F64Native / F64NativeNoSharedMem / Df64Only / F32Only) |
| **Math-level Optimisation** | naga-IR FMA fusion (~1.3x), dead expression elimination — operates on the algebra, not the ISA |

**Boundary**: barraCuda writes the math. coralReef compiles the math. toadStool runs the math. The shaders are the mathematics; the driver is plumbing.

**Five-Spring ingestion**: hotSpring (lattice QCD, HFB, spectral), neuralSpring (bio ML, Hill kinetics), wetSpring (ODE), airSpring (Richards PDE), groundSpring (sensor noise, Ada Lovelace reclassification). All f32→f64 (S49).

**Participates In**: Node Atomic (via ToadStool), NUCLEUS compute layer

---

### coralReef - Shader Compiler Primal

**Domain**: GPU shader compilation — WGSL/SPIR-V to native GPU binary  
**Phase**: Foundation  
**Status**: Phase 10 Iteration 59 (A+) — 3038 tests passed, 0 failed, 65.8% line coverage (79.6% non-hardware), 72.9% function coverage, 93 cross-spring WGSL shaders (84 compiling SM70), GLSL 450 frontend (5/5 passing), SPIR-V roundtrip (10/10 passing), multi-device compile API, FMA contraction enforcement, VFIO sovereign GPU dispatch (BAR0 + DMA + GPFIFO + PFIFO channel + V2 MMU + sync), `GpuContext::from_vfio()` convenience API, UVM dispatch pipeline, `KernelCacheEntry` + `dispatch_precompiled()` (zero-copy `Bytes`), SCM_RIGHTS fully safe (rustix AsFd, zero unsafe in ember/ipc), DmaBuffer `Arc<OwnedFd>` (consolidated fd safety), clone audit (shader_model 29→0, bdf `Arc<str>`, lower_f64/naga_translate SSARef refs), `#[forbid(unsafe_code)]` on 8/9 crates, zero clippy warnings (pedantic+nursery -D warnings), zero doc warnings, zero fmt drift, all files <1000 lines, AGPL-3.0-only, `.cursor/rules` with wateringHole standards, cross-primal e2e test, nak-ir-proc trybuild tests, hardware: 2× Titan V (VFIO) + RTX 5060 (nvidia-drm)

**Role**: coralReef is the sovereign Rust GPU shader compiler. It compiles WGSL, SPIR-V, and GLSL compute shaders to native GPU binaries with full f64 transcendental support. NVIDIA backend complete (SM70-SM89). AMD backend operational (RDNA2/GFX1030) with E2E dispatch verified. coralDriver provides userspace GPU dispatch via DRM ioctl (AMD amdgpu, NVIDIA nouveau, nvidia-drm/UVM) and VFIO direct BAR0/DMA dispatch (maximum sovereignty). coralGpu unifies compilation and dispatch into a single API with sovereign driver preference (vfio > nouveau > amdgpu > nvidia-drm). Zero C dependencies, zero vendor lock-in, zero FFI. Part of the sovereign compute pipeline: barraCuda generates WGSL shaders, toadStool proxies `shader.compile.*` requests, coralReef compiles to native binary, coralDriver dispatches on hardware.

**Primitives**:

| Category | Primitives |
|----------|-----------|
| **IPC** | `shader.compile.spirv`, `shader.compile.wgsl`, `shader.compile.wgsl.multi`, `shader.compile.status`, `shader.compile.capabilities` — JSON-RPC 2.0 + tarpc (TCP/Unix socket), zero-copy `bytes::Bytes` payloads, differentiated error codes, FMA policy control |
| **NVIDIA Backend** | SM70-SM89 (Volta through Ada), SASS binary output, f64 transcendentals via Newton-Raphson (sqrt, rcp, exp2, log2, sin, cos) |
| **AMD Backend** | RDNA2 GFX1030, native `v_fma_f64`/`v_sqrt_f64`/`v_rcp_f64`, 1446 ISA opcodes (Rust-generated from AMD XML) |
| **Compiler Core** | naga frontend, SSA IR, copy propagation, DCE, register allocation, vendor-specific legalization and encoding |
| **coralDriver** | AMD DRM ioctl (GEM, PM4, BO list, CS submit, fence sync) — **E2E verified on RX 6950 XT**, NVIDIA nouveau (channel, GEM, pushbuf, QMD), nvidia-drm/UVM (RM alloc, GPFIFO, USERD), VFIO (BAR0 + DMA + GPFIFO + sync) — pure Rust, zero libc |
| **coralGpu** | Unified compile + dispatch API — vendor-agnostic `GpuContext` |
| **f64 Lowering** | Full f64 transcendental suite: sqrt, rcp, exp2, log2, sin, cos, exp, log, pow — NVIDIA (DFMA software) + AMD (native hardware) |
| **93/93 Cross-Spring Shaders** | Compiles shaders from hotSpring, groundSpring, neuralSpring, wetSpring, airSpring, healthSpring to native SM70 SASS (all resolved Iter 31) |
| **AMD E2E Pipeline** | WGSL → compile → PM4 dispatch → GPU execution → host readback — verified on RX 6950 XT (RDNA2 GFX1030) |

**Participates In**: Sovereign Compute Pipeline (barraCuda → toadStool → coralReef → native binary → coralDriver → hardware)

---

### biomeOS - Ecosystem Orchestrator

**Domain**: Primal orchestration and ecosystem coordination  
**Phase**: Foundation  
**Version**: v4.22  
**Status**: Production Ready (A++, Security A++ LEGENDARY) — 7,983+ tests, 26 workspace crates, 43+ deploy graphs, 19 composition graphs, 20 niche templates, 320+ capability translations, 27 capability domains, zero-copy `bytes::Bytes` + `Arc<str>`, Rust 2024 edition, rustix 1.x, clippy pedantic+nursery (0 warnings), `#[expect(reason)]` lint policy, ecoBin v3.0 compliant. NC-1 COMPLETE. guideStone startup contract SHIPPED (Wave 109, `--bind-mode` + HEALTH-01). NUCLEUS supervision SHIPPED (v4.17). TCP-only fallback SHIPPED + ALL ADOPTED. `primal.announce` self-registration. Zero >800L production files, zero unsafe/mocks/TODO in production, zero C deps

**Role**: biomeOS is the orchestration substrate. It discovers primals by their capabilities at runtime, routes requests semantically via the Neural API, composes primals into atomics (Tower, Node, Nest, NUCLEUS), and coordinates higher-order patterns like RootPulse. It is the composer - primals are the instruments.

**Primitives**:

| Category | Primitives |
|----------|-----------|
| **Neural API** | Semantic routing (`capability.call`), 260+ translations, 19 domains, adaptive routing weights, weight health, utilization tracking, `primal.announce` self-registration, composition patterns |
| **Atomics** | Tower Atomic, Node Atomic, Nest Atomic, Full NUCLEUS composition |
| **Provenance** | `rootpulse_commit` graph, `provenance_pipeline` graph, rhizoCrypt/LoamSpine/sweetGrass domains |
| **Discovery** | Runtime capability matching, primal health monitoring, prefix resolution |
| **Deployment** | genomeBin management, graph-based deployment, cross-device federation |
| **Security** | Dark Forest integration (A++ LEGENDARY), genetic model coordination |
| **IPC** | Universal IPC v3.0, multi-transport support |

**Participates In**: Coordinates all composed systems (RootPulse, Tower Atomic, NUCLEUS, federation). Provenance trio (rhizoCrypt + LoamSpine + sweetGrass) wired into Neural API for `dag.*`, `commit.*`, `provenance.*` routing. NUCLEUS Gateway for spore ingestion/emission (see `../operations/SPORE_OWNERSHIP_MATRIX.md`).

**NUCLEUS Gateway** (shipped v3.77–v3.84): biomeOS provides `biomeos nucleus ingest` and `biomeos nucleus emit` subcommands for bidirectional spore transmission via `nest_ingest_spore.toml` and `nest_emit_spore.toml` composition graphs. Ingests pseudoSpores/lithoSpores into nest_atomic storage via NestGate + provenance trio. Emits new spores from NUCLEUS composition state with full pseudoSpore 2.0 materialization (polling + dir unpack). NC-1.4 resolved: `biomeos-pseudospore` crate provides canonical validation (compatible with `pseudospore-core`; legacy `litho_core::pseudospore` retired). NC-1.emit complete: full materialization pipeline. See `infra/wateringHole/SPORE_OWNERSHIP_MATRIX.md` for the three-way ownership split.

---

## Post-NUCLEUS Primals

These primals build emergent behaviors on the NUCLEUS foundation. They compose into higher-order patterns (RootPulse, Memory & Attribution Stack) coordinated by biomeOS via the Neural API. Each is functional, tested, and has its own showcase demonstrations. They represent the next evolutionary phase - building emergent capabilities on the foundation that the primals above provide.

### petalTongue - Universal User Interface Primal

**Domain**: Universal User Interface — any computational universe → any modality → any user type  
**Phase**: Post-NUCLEUS  
**Status**: Production Ready (A+) — v1.7.0, 18 crates, 6,605 tests, topology→runtime manifest, main.rs split, geometry module, ~90% coverage, edition 2024, `#![forbid(unsafe_code)]` + `deny(unwrap/expect)`, zero C deps, AGPL-3.0-or-later, 55 IPC methods, 13 DataBinding variants, UUI glossary module, SAME DAVE model, client-side WASM rendering (14 exports), showcase fossilized (Wave 49). See [PETALTONGUE_NEEDS_FROM_ECOSYSTEM.md](petaltongue/PETALTONGUE_NEEDS_FROM_ECOSYSTEM.md) for integration gaps

**Role**: petalTongue is the Universal User Interface — translating any computational universe into any modality for any user type. It implements a composable **Grammar of Graphics** pipeline: any primal sends a declarative grammar expression (data + variable bindings + scales + geometry + coordinates), and petalTongue compiles it to the best available representation (desktop display, terminal, audio sonification, SVG, PNG, JSON API, haptic, braille). Tufte constraints (data-ink ratio, lie factor, accessibility) are machine-checked on every render. The **SAME DAVE** cognitive model (Sensory Afferent / Motor Efferent) provides bidirectional feedback loops. Heavy computation (statistics, 3D tessellation, physics) is offloaded to barraCuda via capability-based discovery. The grammar is domain-agnostic: the same pipeline renders ecosystem topology, clinical vitals, molecular structures, game worlds, and universe simulations. Accessibility is not a feature — it is the architecture: every modality is a first-class compilation target, serving sighted humans, blind hikers, paraplegic developers, AI agents, and beyond. Live ecosystem wiring enables 60 Hz sensor streaming, interaction broadcast, and Neural API self-registration with biomeOS.

**Primitives**:

| Category | Primitives |
|----------|-----------|
| **Display Modes** | Desktop display (egui/wayland), Terminal display (ratatui), Web interface (axum), Headless rendering (SVG/PNG) |
| **Audio** | Sonification engine: 5 instruments, health-to-pitch mapping, position-to-stereo panning |
| **UUI** | Canonical glossary (`uui_glossary`), modality names, user types, SAME DAVE model constants |
| **Layout** | 4 graph layout algorithms, pan/zoom/select |
| **Grammar of Graphics** | Declarative grammar expressions (Scale, Geometry, Coordinate, Statistic, Aesthetic, Facet traits), grammar compiler → RenderPlan, modality compilers (egui, ratatui, audio, SVG, PNG, JSON) |
| **Tufte Constraints** | Data-ink ratio, lie factor, chartjunk detection, small multiples preference, color accessibility, data density, smallest effective difference — auto-correctable |
| **Interaction** | Inverse scale pipeline (display coords → data values), brush selection, linked views, cross-primal interaction events via `visualization.interact` |
| **Integration** | Live primal discovery via Songbird, biomeOS SSE event subscription, barraCuda GPU compute offload (`math.stat.*`, `math.tessellate.*`, `math.project.*`) |
| **IPC** | `visualization.render`, `visualization.render.stream`, `visualization.export`, `visualization.validate`, `visualization.capabilities`, `visualization.interact` — JSON-RPC 2.0 + tarpc, `bytes::Bytes` zero-copy for binary payloads |
| **Configuration** | Environment-driven (ENV > File > Defaults), TCP fallback IPC |

**UniBin Modes**: `ui`, `tui`, `web`, `headless`, `server`, `live`, `status`

**Key principle**: One Engine, Infinite Representations. Data defines structure. Grammar defines mapping. Modality defines rendering. The user defines interaction. Other primals send grammar expressions or raw data; petalTongue handles the rest. See `wateringHole/petaltongue/VISUALIZATION_INTEGRATION_GUIDE.md`.

**Participates In**: biomeOS ecosystem visualization, real-time health monitoring display, barraCuda compute pipeline (grammar → GPU statistics/tessellation → render), cross-primal interaction events

---

### rhizoCrypt - Ephemeral Memory Primal

**Domain**: Content-addressed DAG engine for working memory  
**Phase**: Post-NUCLEUS  
**Version**: 0.14.17  
**Status**: Production Ready (1,456 tests, clippy pedantic+nursery clean, integration traits wired, Edition 2024, `unsafe_code = "deny"` / `unwrap_used`+`expect_used = "deny"` workspace-wide, zero `unsafe` in tests (temp-env), AGPL-3.0-or-later, UniBin compliant, cargo-deny CLEAN (RUSTSEC-2026-0204 fixed), `--fail-under-lines 90` CI gate (93.83%), cross-compile CI (musl x86_64/aarch64 + RISC-V + Windows GNU), `niche.rs` self-knowledge with MCP tools, `capability_registry.toml` (28 methods, 8 domains) + deploy graph with `fallback = "skip"`, `DagBackend` enum dispatch (redb default), GC sweeper, SessionTreeHash CAC L5 with DashMap cache, zero deprecated API surface, zero dead code, zero cross-primal compile deps — sovereign wire types, capability-neutral naming throughout)

**Role**: rhizoCrypt provides the ephemeral workspace layer — a git-like DAG of content-addressed events that serves as working memory. Sessions are scoped, lock-free (DashMap), and real-time. Data lives here temporarily until it is either discarded or "dehydrated" (committed) to permanent storage. All inter-primal communication uses capability-based discovery — rhizoCrypt has zero hardcoded vendor references.

**Primitives**:

| Category | Primitives |
|----------|-----------|
| **Vertex Operations** | Content-addressed events with BLAKE3 hashing, multi-parent DAG links, nanosecond timestamps |
| **Session Management** | Scoped workspaces with full lifecycle (active, committed, discarded), lock-free |
| **Merkle Trees** | Content verification, inclusion proofs, root computation |
| **Dehydration** | Temporal collapse: commit session state to permanent storage via JSON-RPC 2.0 |
| **Slice Semantics** | 6 query modes (Copy, Loan, Consignment, Escrow, Mirror, Provenance) |
| **Attribution** | Agent DID identity, per-agent event counting, role assignment |
| **Niche** | `niche.rs` self-knowledge module with `PRIMAL_ID`, `CAPABILITIES`, `CONSUMED_CAPABILITIES`, `COST_ESTIMATES`, `operation_dependencies()` |
| **IPC** | JSON-RPC 2.0 (required) + tarpc/bincode (optional), 27 methods across 8 domains (`dag.*`, `health.*`, `capability.*`, `tools.*`), enhanced `capability.list` with per-method cost/deps, `health.liveness` + `health.readiness` probes, `tools.list` + `tools.call` MCP, 4-format capability parsing, `ValidationSink` pluggable output, `normalize_method()` legacy prefix support |

**Participates In**: RootPulse (ephemeral workspace layer), Memory & Attribution stack

---

### sweetGrass - Attribution Primal

**Domain**: Semantic provenance and attribution  
**Phase**: Post-NUCLEUS  
**Status**: Production Ready (v0.7.56, 1,636 tests, 88 BTSP tests, 37 canonical methods + 10 wire-name aliases, ecoBin compliant, redb default, parking_lot locks, Edition 2024, MSRV 1.87, AGPL-3.0-only, pedantic+nursery clean, zero unsafe, zero production unwrap, 7 benchmarks, 11 proptest strategies, sovereign types — no shared crates). **Wave 109**: HEALTH-01 RESOLVED (bare `"health"` alias + enriched response), BTSP server-side E2E READY (`BEARDOG_SOCKET` resolution)

**Role**: sweetGrass tracks who created what, when, and how. It creates "braids" - content-addressable provenance records compliant with W3C PROV-O - and calculates fair attribution shares across contributors. Privacy controls are built in (GDPR-inspired, 5 levels).

**Primitives**:

| Category | Primitives |
|----------|-----------|
| **Braids** | Content-addressable provenance records, W3C PROV-O / JSON-LD compliant, `Arc<str>` zero-copy identifiers |
| **Attribution Engine** | 12 role types (Creator, Contributor, Reviewer...), derivation chain analysis, time decay, recursive propagation |
| **Provenance Graph** | Complete data lineage tracking, DAG queries, "where did this come from?" |
| **Privacy** | 5 privacy levels, GDPR-inspired data subject rights |
| **Storage** | Memory, redb (recommended), Sled (legacy), PostgreSQL backends |
| **Export** | W3C PROV-O JSON-LD standard, ~88% compression with session dedup + zstd |
| **IPC** | JSON-RPC 2.0 + tarpc + REST + UDS, DispatchOutcome, health probes, OrExit |

**Participates In**: RootPulse (attribution layer), Memory & Attribution stack, Loam Certificate provenance

---

### LoamSpine - Permanence Primal

**Domain**: Immutable linear ledger for selective permanence  
**Phase**: Post-NUCLEUS  
**Status**: Production Ready (v0.9.16, 1,256+ tests, 92%+ line / 90%+ region coverage, pure Rust, ecoBin compliant, UniBin, Edition 2024, pedantic+nursery clean, cast lint deny, `#[expect(reason)]` bulk migration, CONTEXT.md per PUBLIC_SURFACE_STANDARD, `capabilities.list` + `health.liveness` + `tools.list` + `tools.call` (MCP) per Semantic Method Naming v2.1, tarpc 0.37 (json transport, bincode path eliminated), `ResilientSyncEngine` (circuit-breaker + retry for federation), `DispatchOutcome`/`IpcErrorPhase`/`StreamItem`/`OrExit`/`extract_rpc_result`/`normalize_method` ecosystem patterns, cargo deny 4/4 clean, provenance trio types inlined (no shared crate), `publish = false` on all workspace crates)

**Role**: LoamSpine is the fossil record. Where rhizoCrypt is ephemeral and fast, LoamSpine is permanent and provable. Important events are deliberately committed ("dehydrated") from rhizoCrypt into LoamSpine's append-only ledger. Most data should be temporary; only what matters should be permanent.

**Primitives (Specified)**:

| Category | Primitives |
|----------|-----------|
| **LoamEntry** | Append-only entries with sequential index, previous hash chain, cryptographic signatures |
| **Spine Structure** | Sovereign ledgers (personal, professional, community, public) |
| **Loam Certificates** | Memory-bound objects: digital game keys, credentials, property deeds, ownership transfer, lending |
| **Replication** | Federated sync (peers, federation, archive) |
| **Proofs** | Inclusion proofs, certificate proofs, recursive spine stacking |

**Participates In**: RootPulse (permanence layer), Memory & Attribution stack, Loam Certificate Layer

---

### skunkBat - Defense Primal

**Domain**: Defensive network security  
**Phase**: Post-NUCLEUS  
**Status**: Production Ready (v0.2.18 — 389+ tests, 90%+ coverage, zero debt, ConnectivityAnomaly 9th threat type). **Wave 109**: STARTUP-SB-01 RESOLVED — `--bind-mode` replaces `--no-uds/--no-tcp`, standard primal startup contract

**Role**: skunkBat protects sovereign computing environments through metadata-only defensive reconnaissance. It detects threats, orchestrates graduated responses, and federates threat intelligence across trusted peers — all without inspecting packet contents or tracking user behavior.

**Primitives**:

| Category | Primitives |
|----------|-----------|
| **Threat Detection** | Genetic (unknown lineage), Topology (layer-hopping), Behavioral (statistical anomalies), Intrusion (attack signatures), Resource (DoS, exhaustion) |
| **Defense Actions** | Monitor + Alert (low), Quarantine (isolate), Block (deny, operator decision) |
| **Baseline** | Statistical profiling of normal network patterns (multi-dimensional rolling window) |
| **Reconnaissance** | Network intelligence (metadata-only, no content) |
| **Transport** | BTSP Phase 3 (ChaCha20-Poly1305 encrypted framing, cipher negotiation) |
| **Authorization** | JH-0 MethodGate (pre-dispatch capability auth, enforced/permissive modes) |
| **Audit** | JH-5 Audit Log (ring buffer, cursor-based RPC query, rhizoCrypt + sweetGrass forwarding) |
| **Integration** | Trait-based ecosystem integration (BearDog, ToadStool, Songbird, NestGate) |

**IPC Methods**: 18 JSON-RPC methods (scan, detect, respond, metrics, audit_log, health.*, lifecycle.status, btsp.negotiate, btsp.capabilities, capabilities.list, identity.get, auth.*)  
**Default Port**: 9750 (TCP) + UDS (`security.sock`)  
**Dependencies**: Zero C deps. Pure RustCrypto (OsRng, ChaCha20-Poly1305, HMAC).

**Principles**: Defensive only, user authority required, privacy by architecture

**Participates In**: Ecosystem security layer, Dark Forest defense coordination, NUCLEUS compositions (security observability tier)

---

## The Memory & Attribution Stack

rhizoCrypt, LoamSpine, and sweetGrass form a unified stack with three semantic layers over one DAG engine:

```
Application Layer (Gaming, Scientific, Collaboration)
        |
  sweetGrass (Attribution) - Query & export layer
        |
   LoamSpine (Permanence) - Selective immutable history
        |
  rhizoCrypt (Core DAG) - Content-addressed working memory
```

**rhizoCrypt** is the engine. **LoamSpine** adds permanence semantics. **sweetGrass** adds attribution semantics. biomeOS coordinates them via the Neural API into RootPulse.

---

## Primal Coordination Summary

### Who Coordinates Whom

```
biomeOS (orchestrator)
  |
  +-- Neural API routes capability.call requests
  |
  +-- Composes atomics:
  |     Tower Atomic  = BearDog + Songbird
  |     Node Atomic   = Tower + ToadStool
  |     Nest Atomic   = Tower + NestGate
  |     Full NUCLEUS  = All + Squirrel
  |
  +-- Coordinates RootPulse:
  |     rhizoCrypt (ephemeral) + LoamSpine (permanent)
  |     + NestGate (storage) + BearDog (signing)
  |     + sweetGrass (attribution) + Songbird (discovery)
  |
  +-- Feeds petalTongue:
        Real-time SSE events for ecosystem visualization
```

### No Primal Knows About Another

BearDog doesn't know Songbird exists. rhizoCrypt doesn't know about LoamSpine. sweetGrass doesn't know about RootPulse. Each primal advertises its capabilities, and biomeOS discovers and coordinates them at runtime. This is fundamental - complexity through coordination, not through coupling.

---

## Domain Validation Primals (Springs)

These primals validate the ecoPrimals compute pipeline end-to-end by reproducing published science in specific domains. Each Spring follows Paper → Python → Rust (BarraCuda CPU) → GPU (ToadStool shaders) → metalForge (mixed hardware) → biomeOS (NUCLEUS deployment). Springs consume ToadStool/BarraCuda compute and contribute domain-specific fixes, shaders, and absorption candidates back upstream.

**Spring Versions (as of July 29, 2026 — Wave 155h)**:

| Spring | Version |
|--------|---------|
| ToadStool | S344 (23,332 tests, deny.toml 19+ bans, overstep reduced, socket centralized, cross-arch adopted, zero clippy) |
| hotSpring | v0.6.32 (upstream sync v5, naga root-cause rename, BatchedComputeDispatch, guideStone L6 CERTIFIED) |
| groundSpring | V103 |
| neuralSpring | V98/S145 (GPU dispatch evolution, PipelineGraph ready for absorption) |
| wetSpring | V99 |
| airSpring | v0.10.0 (911 lib + 311 integration + 61 forge tests, 97 binaries, 87 experiments, 14.3× CPU speedup, 10 MCP tools, Edition 2024) |
| barraCuda | v0.4.0 (4,957 tests, SIGSEGV fixed, BTSP env races resolved, dead code removed, AGPL-3.0-only) |
| coralReef | v0.2.0 (3,527 tests, 18/18 JSON-RPC dispatch, BTSP Phase 3 encrypted transport) |
| primalSpring | v0.9.46 Wave 151a (89 experiments, 21 tracks, 1,241 tests, 490+ methods, 197 scenarios ALL PASS, known debt 1, crypto delegation 6/6, Nest Atomic Phase 0 ready) |
| ludoSpring | V30 (82 experiments, 675+19 tests, 42 Python parity, 91.27% coverage, thiserror, MCP tools, tarpc optional, handler architecture split, UniBin 7 subcommands, CI, deploy graph, scyBorg triple license) |

### airSpring - Ecological & Agricultural Sciences

**Domain**: Precision agriculture, irrigation science, environmental systems  
**Phase**: Domain Validation  
**Status**: v0.10.0 — 911 lib + 311 integration + 61 forge + 22 property tests, 97 binaries, 87 experiments, 381/381 validation, 146/146 evolution, 14.3× CPU speedup (24/24 parity, 21/21 CPU-GPU), 0 clippy warnings (pedantic+nursery), zero unsafe code (`#![forbid(unsafe_code)]`), zero mocks in production, zero C deps (14 crates banned in `deny.toml`), AGPL-3.0-or-later, standalone barraCuda 0.3.5 (wgpu 28, DF64 precision tier), Edition 2024. 10 MCP tools wired (Squirrel AI). Platform-agnostic IPC (Transport enum: Unix + TCP). 63 provenance baselines. 63 named tolerances (4 submodules). `#[expect(reason)]` Rust 2024 complete. Full validation pipeline green (2026-03-19)

**Role**: airSpring validates agricultural computational methods — FAO-56 ET₀ (8 methods), soil sensor calibration, IoT irrigation, water balance, dual crop coefficient, Richards equation, yield response, ecological diversity, immunological Anderson coupling, and SCS-CN/Green-Ampt hydrology — proving the full ecoPrimals pipeline from paper reproduction to GPU-accelerated sovereign computation on consumer hardware.

**Capabilities**:

| Category | Details |
|----------|---------|
| **Experiments** | 87 complete: FAO-56, soil, IoT, WB, dual Kc, Richards, biochar, yield, CW2D, 8 ET₀ methods, GDD, pedotransfer, ensemble, bias correction, parity, dispatch, Anderson coupling, SCS-CN, Green-Ampt, VG inverse, seasonal WB, immunological Anderson (tissue/cytokine/barrier/cross-species), f64-canonical GPU, cross-spring evolution, CPU/GPU parity (21/21), toadStool dispatch (19/19), NUCLEUS mesh (17/17), graph coordination (22/22) |
| **ET₀ Methods** | Penman-Monteith, Priestley-Taylor, Hargreaves-Samani, Makkink, Turc, Hamon, Blaney-Criddle, Thornthwaite |
| **Python Baselines** | 1,284/1,284 PASS against digitized paper benchmarks (57 papers), 63 provenance records |
| **Rust Validation** | 911 lib + 311 integration + 61 forge tests, 381/381 validation checks, 146/146 evolution |
| **Real Data** | 15,300 station-days Open-Meteo ERA5 (100 Michigan stations), 1498/1498 atlas checks |
| **GPU Orchestrators** | 25 Tier A + 6 GPU-universal (ops 0-19 all upstream `BatchedElementwiseF64`), seasonal pipeline, atlas stream, MC ET₀ |
| **Seasonal Pipeline** | ET₀→Kc→WB→Yield chained, GPU stages 1-3, multi-field streaming (57/57), pure GPU end-to-end (46/46) |
| **metalForge** | 27 workloads, 66/66 cross-system routing (GPU+NPU+CPU), 7-stage GPU→NPU PCIe bypass |
| **NPU** | AKD1000 live (3 experiments, 95/95 checks, ~48µs inference) |
| **CPU Benchmark** | 14.3× geometric mean speedup vs Python (24/24 parity), 13,000× atlas-scale |
| **GPU Live** | Titan V 24/24 PASS (0.04% seasonal parity), RTX 4070 validated |
| **NUCLEUS** | biomeOS primal (41 capabilities), JSON-RPC 2.0, 4 deploy graphs, cross-primal forwarding |
| **Nautilus** | bingoCube/nautilus evolutionary reservoir computing (AirSpringBrain, drift detection, NPU export) |
| **MCP Tools** | 10 ecology tools (Squirrel AI): et0, hargreaves, water_balance, soil_moisture, dual_kc, richards, yield_response, spi_drought, diversity, pedotransfer |
| **IPC** | Platform-agnostic Transport (Unix + TCP), 3-tier discovery, health probes, circuit breaker |

**ToadStool/BarraCuda Contributions**:
- TS-001: `pow_f64` fractional exponent fix (discovered during ET₀ atmospheric pressure calc)
- TS-003: `acos` precision boundary fix
- TS-004: reduce buffer N≥1024 fix
- Richards PDE solver absorbed upstream (S40)
- Stats metrics absorbed upstream (S64)
- 6 f64-canonical WGSL shader ops (3 absorbed: Makkink→Op14, Turc→Op15, Hamon→Op16)
- Fused Welford `mean_variance_f64.wgsl` wired into SeasonalReducer (hotSpring S58 provenance)
- Fused Pearson `correlation_full_f64.wgsl` wired into gpu/stats (neuralSpring S69 provenance)
- NVK/Mesa f64 reliability finding → GPU fallback to CPU Welford documented
- Transport enum + resolve_transport() pattern (upstream absorption candidate)
- MCP tool dispatch pattern (tools/list + tools/call in primal dispatch)

**Participates In**: Node Atomic (via ToadStool compute), Nest Atomic (via NestGate data), NUCLEUS (via biomeOS deployment graphs), metalForge cross-system dispatch

### hotSpring - Computational Physics + Biomolecular MD

**Domain**: Plasma physics, nuclear structure, lattice QCD, transport, spectral theory, biomolecular MD (CAZyme conformational energy landscapes)
**Phase**: Domain Validation + Biomolecular Evolution (Exp 220)
**Status**: v0.6.32 — 700 (cylinder) / 596 (default) / 1,045 (barracuda-local) lib tests, 167 binaries, 128 WGSL shaders, 65 validation suites (3 tiers), 220 experiments. guideStone Level 6 CERTIFIED (primalSpring v0.9.27). Fleet: 2× Titan V (GV100) + RTX 5060 (Blackwell).

**Role**: hotSpring validates the ecoPrimals compute pipeline against published computational physics — Yukawa OCP, nuclear EOS (HFB), lattice QCD (SU(3) pure gauge + dynamical fermion HMC), screened Coulomb transport, Anderson localization, and Hofstadter butterfly. First consumer-GPU dynamical fermion QCD. First neuromorphic silicon (AKD1000) in a lattice QCD production pipeline. **Exp 220 (May 2026)**: Extending into biomolecular MD for CAZyme conformational energy landscapes — GROMACS 2026.0 as industry control, bonded FF + metadynamics bias evolution, helixVision downstream validation layer.

**Capabilities**:

| Category | Details |
|----------|---------|
| **Experiments** | 220 (001–190 archived, 191–220 active): MD, GPU scaling, parity, lattice QCD, NPU characterization, brain architecture, sovereign GPU (Exp 162–219), CAZyme FEL (Exp 220) |
| **Physics Domains** | Yukawa OCP MD, nuclear EOS (SEMF→HFB→deformed), SU(3) gauge + dynamical fermion HMC, Green-Kubo transport, Anderson 1D/2D/3D, Hofstadter butterfly, Abelian Higgs, biomolecular MD (bonded FF, metadynamics — in progress) |
| **GPU Validation** | 128 WGSL shaders, DF64 core streaming (3.24 TFLOPS, 14-digit precision on FP32), GPU-resident CG (15,360× readback reduction) |
| **Sovereign GPU** | VFIO sovereign dispatch on Titan V (GV100) + RTX 5060 (SM120). Sovereignty Tier Model (Tier 0–3). Catalyst Driver Pattern (Exp 219). 24 RPC methods. Warm keepalive 183ms (76× faster than cold). |
| **NPU Integration** | Live AKD1000 via PCIe, 15-head ESN, cross-run learning, concept edge detection |
| **Biomolecular MD** | GROMACS 2026.0 industry control (CUDA, PLUMED, Colvars). Existing: LJ, Coulomb, PPPM, VV, thermostats, cell/Verlet lists. Missing: bonded FF, topology reader, metadynamics bias. Feeds helixVision downstream. |
| **Production Results** | Deconfinement χ=40.1 at β=5.69 (32⁴, 13.6h, $0.58). Dynamical crossover confirmed. Chuna 44/44 PASS. guideStone L6 CERTIFIED. |

**ToadStool Contributions**:
- 128 WGSL shaders evolved via cross-spring absorption (lattice QCD, HFB, transport, spectral, MD)
- GPU-resident CG solver pattern absorbed upstream
- DF64 core streaming validated and expanded (S60)
- Sovereign GPU dispatch pipeline (Exp 162–219): VFIO, ember, diesel engine, warm keepalive
- Compile-then-dispatch pipeline wired (coralReef→toadStool)

**primalTools Contributions**:
- bingoCube/nautilus: evolutionary reservoir computing crate
- NautilusBrain API for NPU integration, self-regulating drift monitor
- AKD1000 int4 weight export with quantization validation (MSE=0.004)

**Participates In**: Node Atomic (via ToadStool compute), metalForge (NPU + multi-GPU), NUCLEUS (via biomeOS deployment). helixVision downstream (MD validation for structure prediction).

### primalSpring - Coordination and Composition Validation

**Domain**: Primal coordination, atomic composition, graph execution, emergent systems, multi-node bonding + federation  
**Phase**: Phase 60+ / Wave 150x (197 scenarios, TOWER EXCEEDS WG)  
**Status**: v0.9.46 Wave 151a — 1241 tests, 197 scenarios ALL PASS, known debt **1** (grapheneGate HSM — hardware gated). Tower 353x LAN proven. Crypto delegation 6/6 validated. Deep debt swept to zero. grapheneGate ADB validation complete (10/13 pass, Keystore2 binder path recommended). `#![forbid(unsafe_code)]` on all crate roots. Zero TODO/FIXME/unsafe/mocks in production. All 14 direct deps pure Rust. Idiomatic Rust 2024.

**Role**: primalSpring is the spring whose domain IS coordination. Where other springs validate domain science via the ecoPrimals infrastructure, primalSpring validates the infrastructure itself — that biomeOS composes primals correctly, that NUCLEUS atomics deploy and degrade gracefully, that all 5 coordination patterns work with real primals, that Layer 3 emergent systems emerge correctly, and that cross-spring data flows maintain provenance. It has proven the full composition lifecycle — binary discovery, socket nucleation, topological startup, capability-based health validation, and multi-primal coordination with real IPC. Wave 150x added Tower pen testing, stress testing, LAN routing gap validation, and deep debt evolution.

**Capabilities**:

| Category | Details |
|----------|---------|
| **Experiments** | 89 across 20 tracks: Atomic Composition, Graph Execution, Emergent Systems, Bonding & Plasmodium, Cross-Spring Coordination, Live Composition, Multi-Node Bonding, Cross-Gate Deployment, Frontier, Subsystem Decomposition, Signal Dispatch. All use `discover_by_capability()` with honest `check_skip` for live-IPC. |
| **Graph TOMLs** | 113 (~80 deploy + 33 compositions): all parsed, validated, topologically sorted. All nodes have `by_capability`. Fragment-first with `resolve = true`. |
| **Validation Scenarios** | 197 scenarios across 14 tracks: atomic-compositions, meta-tier, agentic-tower, sovereignty, dispatch parity, cross-gate, primal announce, ionic bond, sporePrint, Tower pen (7), Tower stress (7), exploration (6 proven live), LAN routing gap. |
| **Tower Pen Testing** | 7 scenarios: capability-escalation, cipher-downgrade, enrollment-replay, malformed-rpc, mesh-poison, relay-abuse, uds-spoof. CallerContext + UDS hardening resolved 7 of 14 initial findings. |
| **Tower Stress** | 7 scenarios: btsp-storm, concurrent-dispatch, failover-resilience, mesh-churn, shadow-fidelity, sustained-throughput, uds-hop-cost. |
| **LAN Routing Gap** | `s_mesh_lan_path_preference` — validates `mesh.find_path` must prefer `EndpointType::Local` for same-switch (353x penalty, P0 for songBird). |
| **IPC** | Zero-alloc JSON-RPC (`Cow<'static, str>`), 8 typed error variants + IpcErrorPhase, CircuitBreaker, RetryPolicy, DispatchOutcome, 4-format capability parsing |
| **Evolution** | `MeshEntry::preferred_address()` LAN-first, `has_tower()`, K-Derm trust tiers, `Arc<Anchor>` zero-clone, `is_none_or()` Rust 2024, 26 dep refresh |
| **Bonding** | Ionic bond runtime (IonicContractRegistry), covalent mesh, content distribution, graph metadata |
| **Live Composition** | Tower EXCEEDS WG: 353x LAN (0.45ms vs 158ms), 1.7x WAN sustained. Shadow benchmark: 661 JSON files, continuous hourly. Genetic enrollment LIVE. |
| **Emergent Systems** | RootPulse, RPGPT, helixVision, cross-spring ecology |

**Participates In**: biomeOS (primary test subject), all NUCLEUS primals (deploy + health), Provenance Trio (RootPulse validation), all springs (cross-spring coordination validation), Squirrel (live AI composition), Tower Atomic (shadow benchmark + pen test validation)

### ludoSpring - Game Design & Interaction Science

**Domain**: Ludology, HCI, game science, procedural generation, interaction design  
**Phase**: Domain Validation  
**Status**: V30 — 82 experiments, 675 barracuda + 19 forge tests, 42 Python parity, 19 proptest, 11 IPC integration. Zero `#[allow()]`, zero `unsafe`, zero clippy warnings (pedantic+nursery), zero TODO/FIXME. `#![forbid(unsafe_code)]`, AGPL-3.0-or-later (scyBorg triple: AGPL + ORC + CC-BY-SA-4.0), Edition 2024, MSRV 1.87. 91.27% line coverage (85% floor enforced). `thiserror` 2.x on all error types. MCP `tools.list`/`tools.call` (8 science tools). Optional `tarpc-ipc` feature. Handlers split into 5 domain submodules. UniBin 7 subcommands. CI pipeline. Deploy graph fragment. `GpuContext` + `TensorSession` wired behind `gpu` feature. `default-features = false` on barraCuda v0.3.7.

**Role**: ludoSpring validates the ecoPrimals pipeline against 13 foundational HCI/game science models — Fitts's law, Hick's law, Steering law, GOMS, Flow theory, Dynamic Difficulty, Four Keys to Fun, Engagement metrics, Perlin noise, Wave Function Collapse, L-systems, BSP trees, Tufte data-ink — proving faithful port from Python baselines to Rust CPU to GPU WGSL shaders. The validated math builds playable prototypes (Doom terminal, roguelike explorer) and cross-domain applications (field genomics provenance, medical access control, extraction shooter anti-cheat).

**Capabilities**:

| Category | Details |
|----------|---------|
| **Game Science** | `game.evaluate_flow`, `game.evaluate_engagement`, `game.evaluate_fun`, `game.evaluate_dda`, `game.evaluate_tufte`, `game.evaluate_interaction_cost`, `game.evaluate_goms`, `game.classify_genre` |
| **Procedural** | `game.generate_noise`, `game.generate_wfc`, `game.generate_lsystem`, `game.generate_bsp` |
| **GPU Compute** | 5 WGSL shaders (fog_of_war, tile_lighting, pathfind_wavefront, perlin_2d, dda_raycast), `TensorSession` via `GpuContext` |
| **Telemetry** | 13-event portable game telemetry protocol (NDJSON), external adapters (Veloren, Fish Folk, A/B Street) |
| **RPGPT** | Sovereign RPG engine architecture — any open ruleset + any world + AI narration |
| **Cross-Domain** | Provenance trio integration, extraction shooter fraud detection, field sample lifecycle, consent-gated medical access, cross-domain fraud unification |
| **Health** | `health.check`, `health.liveness`, `health.readiness` |
| **Niche** | `capability.list`, `lifecycle.status`, `capability.register`, `capability.deregister` |
| **Experiments** | 82 across 22 tracks: core game systems, interaction models, PCG, metrics, benchmarks, external control groups, cross-spring (NCBI, NUCLEUS), RPGPT, Games@Home, provenance trio, extraction shooters, composable viz, lysogeny (6 open recreations), cross-spring provenance (5), RPGPT dialogue plane (9), game history revalidation (7) |
| **Python Baselines** | 7 scripts, `combined_baselines.json` with `content_sha256`, 42 parity tests |
| **Deployment** | UniBin (server/status/version), deploy graph, niche YAML, Neural API domain registration, 26 capabilities (24 game + 2 health) |

**IPC Methods**: 26 JSON-RPC 2.0 methods (game evaluation, procedural generation, telemetry, health, lifecycle, capability) over Unix sockets  
**Dependencies**: barraCuda (CPU math, `default-features = false`), wgpu (optional `gpu` feature), serde, uuid. Zero C dependencies in application code.

**Participates In**: RPGPT (game science + session quality), Provenance Trio (rhizoCrypt DAG + loamSpine certs + sweetGrass braids), biomeOS (niche citizen), toadStool (GPU dispatch), coralReef (shader compilation), petalTongue (visualization), Squirrel (AI narration), metalForge (cross-substrate routing)

---

## Registering a New Primal

To add a new primal to this registry:

1. Define your domain (what problem space you own)
2. Catalog your primitives (every atomic capability you provide)
3. Identify your IPC methods
4. Declare what composed systems you could participate in
5. Add your entry to this document following the format above
6. Ensure you follow UniBin and ecoBin standards

---

**This registry is the source of truth for what exists in the ecoPrimals ecosystem.**

---

## FILE: `ecosystem_manifest.toml`

# SPDX-License-Identifier: CC-BY-SA-4.0
#
# ecosystem_manifest.toml — Machine-readable catalog of all ecoPrimals repositories
#
# Authority: wateringHole consensus
# Consumed by: cascade-pull, freshness checks, primalSpring s_ecosystem_freshness
#
# Fields:
#   org            — GitHub org (ecoPrimals, syntheticChemistry, sporeGarden)
#   local_path     — Path relative to ecoPrimals workspace root
#   membrane       — "inner-only" | "trailing-mirror" | "outer-only"
#   sync_source    — "github" (default) | "forgejo" (inner-only repos)
#   sync_priority  — "high" | "standard" | "low"
#   category       — "primal" | "spring" | "garden" | "infra" | "root"
#   description    — Short human description
#   github_repo    — Full GitHub repo path (org/name)
#   forgejo_repo   — Forgejo repo path (org/name on git.primals.eco)
#   default_branch — Git branch name (default: "main")

[meta]
version = "3.1.0"
generated = "2026-07-16"
# DEPRECATED: wave ID now lives in wave.toml (overwatch sole writer).
# This field is retained at last-known value for backward compat with older binaries.
wave = 136
total_repos = 40

# ═══════════════════════════════════════════════════════════════════
# WaterFall Sync Configuration
# ═══════════════════════════════════════════════════════════════════
# K-Derm model: Forgejo sits in the periplasm between gate plasma
# membranes and the extracellular GitHub outer mirror. WaterFall
# cascades evolution down from Forgejo to gate cytoplasms; gates
# push evolution back up through the periplasm.
#
# Pattern lineage: WaterFall parallels RootPulse (whitePaper) —
# both are firstLast biomeOS coordination patterns. RootPulse
# coordinates primals for single-repo VCS; WaterFall coordinates
# membranes for multi-repo ecosystem sync.

[sync]
forgejo_base_url = "https://git.primals.eco"
forgejo_ssh = "ssh://git@git.primals.eco:2222"
github_ssh = "git@github.com:"
forgejo_host = "golgiBody"
default_source = "temporal"
default_branch = "main"
divergence_policy = "merge-ff"
push_to_followers = true
# Push target: "forgejo" (sovereign mediator) or "all" (legacy dual-push).
# When set to "forgejo", temporal.sync pushes only to forgejo remote;
# the VPS push mirror handles GitHub propagation. Gates still pull from
# all remotes (GitHub may have external contributions).
push_target = "all"
# When true, cascade auto-fires a SYNC impulse on diverge detection.
# The impulse carries repo, remote HEADs, merge base, and suggested action.
diverge_impulse = true

[topology]
model = "diderm"
inner_membrane = "golgiBody"
outer_membrane = "golgiBody-ext"

[topology.hosts]
golgiBody = "[RELAY_PUBLIC]"
golgiBody-ext = "137.184.197.151"

# K-Derm layer roles — which node handles which function in the
# waterFall relay chain. Bond types degrade outward:
# covalent (gate→inner) → ionic (inner→outer) → weak (outer→GitHub)
[topology.roles]
push_receiver = "golgiBody"           # cis face: receives gate pushes (Forgejo)
build_authorities = ["sporeGate", "eastGate", "blueGate"]  # sovereign CI: any gate with Rust + musl-tools can build
depot_server = "golgiBody"            # SOLE depot: all gates fetch from golgiBody via WAN TLS. No local depots.
sync_mediator = "sporeGate"           # structural: sync hub + impulse cascade
external_publisher = "golgiBody-ext"  # trans face: ships to GitHub (holds extracellular SSH keys)
remote_access = "golgiBody"           # RustDesk hbbs+hbbr — sovereign remote desktop relay (remote.primals.eco)

# ═══════════════════════════════════════════════════════════════════
# Compute Capabilities — GPU/shader/precision metadata
# ═══════════════════════════════════════════════════════════════════

[capabilities.compute]
SHADER_F64 = true
precision_tiers = ["f32", "f64"]
shader_backends = ["wgsl", "spirv", "glsl"]
gpu_gates = ["ironGate"]
notes = "f64 precision via SHADER_F64 feature on RTX 5070 Ti (ironGate). coralReef compiles shaders. barraCuda dispatches compute. Precision routing: barraCuda.precision.route selects f32/f64 path based on device capability."

# ═══════════════════════════════════════════════════════════════════
# Build Metadata — Sovereign CI Pipeline (plasmid.harvest)
# ═══════════════════════════════════════════════════════════════════
#
# Manifest-driven CI: plasmid.harvest reads these fields instead of
# hardcoding per-primal workarounds in bash scripts.
#
# Fields:
#   binary_name  — Deployed binary name (as installed in pepti depot)
#   package      — Cargo package for `--package` flag (workspace primals)
#   workspace    — Whether the primal uses a Cargo workspace
#   cargo_config — Whether .cargo/config.toml has custom linker/target config
#   targets      — Supported build targets (x86_64-musl, aarch64-musl)
#   notes        — CI quirks or build context
#
# Resolves: CI-DIV-01 (biomeOS), CI-DIV-02 (skunkBat), CI-DIV-03 (nestGate)

[build.beardog]
binary_name = "beardog"
package = "beardog"
workspace = false
cargo_config = false
targets = ["x86_64-unknown-linux-musl", "aarch64-unknown-linux-musl"]

[build.songbird]
binary_name = "songbird"
package = "songbird"
workspace = false
cargo_config = false
targets = ["x86_64-unknown-linux-musl", "aarch64-unknown-linux-musl"]

[build.toadstool]
binary_name = "toadstool"
package = "toadstool-cli"
workspace = true
cargo_config = false
targets = ["x86_64-unknown-linux-musl", "aarch64-unknown-linux-musl"]

[build.barracuda]
binary_name = "barracuda"
package = "barracuda-core"
workspace = true
cargo_config = false
gpu = true
targets = ["x86_64-unknown-linux-musl", "aarch64-unknown-linux-musl"]

[build.coralreef]
binary_name = "coralreef"
package = "coralreef-core"
workspace = true
cargo_config = false
gpu = true
targets = ["x86_64-unknown-linux-musl", "aarch64-unknown-linux-musl"]

[build.rhizocrypt]
binary_name = "rhizocrypt"
package = "rhizocrypt-service"
workspace = true
cargo_config = false
targets = ["x86_64-unknown-linux-musl", "aarch64-unknown-linux-musl"]

[build.loamspine]
binary_name = "loamspine"
package = "loamspine-service"
workspace = true
cargo_config = false
targets = ["x86_64-unknown-linux-musl", "aarch64-unknown-linux-musl"]

[build.sweetgrass]
binary_name = "sweetgrass"
package = "sweet-grass-service"
workspace = true
cargo_config = false
targets = ["x86_64-unknown-linux-musl", "aarch64-unknown-linux-musl"]

[build.biomeos]
binary_name = "biomeos"
package = "biomeos-unibin"
workspace = true
cargo_config = false
targets = ["x86_64-unknown-linux-musl", "aarch64-unknown-linux-musl"]
notes = "CI-DIV-01: workspace has multiple binaries — requires --package biomeos-unibin"

[build.squirrel]
binary_name = "squirrel"
package = "squirrel"
workspace = true
cargo_config = false
targets = ["x86_64-unknown-linux-musl", "aarch64-unknown-linux-musl"]

[build.petaltongue]
binary_name = "petaltongue"
package = "petaltongue-workspace"
workspace = true
cargo_config = false
targets = ["x86_64-unknown-linux-musl", "aarch64-unknown-linux-musl"]

[build.skunkbat]
binary_name = "skunkbat"
package = "skunk-bat-server"
workspace = true
cargo_config = false
targets = ["x86_64-unknown-linux-musl", "aarch64-unknown-linux-musl"]
notes = "CI-DIV-02: workspace root is test-only — requires --package skunk-bat-server"

[build.nestgate]
binary_name = "nestgate"
package = "nestgate"
workspace = false
cargo_config = true
targets = ["x86_64-unknown-linux-musl", "aarch64-unknown-linux-musl"]
notes = "Custom .cargo/config.toml with link-self-contained and relocation-model=static for musl (CI-DIV-03 resolved Wave 133a)"

[build.sourdough]
binary_name = "sourdough"
package = "sourdough"
workspace = true
cargo_config = false
targets = ["x86_64-unknown-linux-musl", "aarch64-unknown-linux-musl"]

# ═══════════════════════════════════════════════════════════════════
# Repositories
# ═══════════════════════════════════════════════════════════════════

[repos.nestGate]
org = "ecoPrimals"
local_path = "primals/nestGate"
membrane = "trailing-mirror"
sync_priority = "standard"
category = "primal"
description = "NestGate persistent storage + content-addressed crates"
github_repo = "ecoPrimals/nestGate"
forgejo_repo = "ecoPrimals/nestGate"

# ═══════════════════════════════════════════════════════════════════
# Primals (ecoPrimals org)
# ═══════════════════════════════════════════════════════════════════

[repos.bearDog]
org = "ecoPrimals"
local_path = "primals/bearDog"
membrane = "trailing-mirror"
sync_priority = "high"
category = "primal"
description = "Security, crypto, BTSP identity"
github_repo = "ecoPrimals/bearDog"
forgejo_repo = "ecoPrimals/bearDog"

[repos.songBird]
org = "ecoPrimals"
local_path = "primals/songBird"
membrane = "trailing-mirror"
sync_priority = "high"
category = "primal"
description = "Discovery, routing, federation"
github_repo = "ecoPrimals/songBird"
forgejo_repo = "ecoPrimals/songBird"

[repos.toadStool]
org = "ecoPrimals"
local_path = "primals/toadStool"
membrane = "trailing-mirror"
sync_priority = "high"
category = "primal"
description = "Compute dispatch"
github_repo = "ecoPrimals/toadStool"
forgejo_repo = "ecoPrimals/toadStool"

[repos.barraCuda]
org = "ecoPrimals"
local_path = "primals/barraCuda"
membrane = "trailing-mirror"
sync_priority = "standard"
category = "primal"
description = "GPU compute dispatch"
github_repo = "ecoPrimals/barraCuda"
forgejo_repo = "ecoPrimals/barraCuda"

[repos.coralReef]
org = "ecoPrimals"
local_path = "primals/coralReef"
membrane = "bidirectional"
sync_priority = "standard"
category = "primal"
description = "Sovereign WGSL/SPIR-V/GLSL shader compiler"
github_repo = "ecoPrimals/coralReef"
forgejo_repo = "ecoPrimals/coralReef"

[repos.rhizoCrypt]
org = "ecoPrimals"
local_path = "primals/rhizoCrypt"
membrane = "trailing-mirror"
sync_priority = "standard"
category = "primal"
description = "Provenance DAG"
github_repo = "ecoPrimals/rhizoCrypt"
forgejo_repo = "ecoPrimals/rhizoCrypt"

[repos.loamSpine]
org = "ecoPrimals"
local_path = "primals/loamSpine"
membrane = "trailing-mirror"
sync_priority = "standard"
category = "primal"
description = "Provenance spine"
github_repo = "ecoPrimals/loamSpine"
forgejo_repo = "ecoPrimals/loamSpine"

[repos.sweetGrass]
org = "ecoPrimals"
local_path = "primals/sweetGrass"
membrane = "bidirectional"
sync_priority = "standard"
category = "primal"
description = "Provenance braid"
github_repo = "ecoPrimals/sweetGrass"
forgejo_repo = "ecoPrimals/sweetGrass"

[repos.biomeOS]
org = "ecoPrimals"
local_path = "primals/biomeOS"
membrane = "bidirectional"
sync_priority = "high"
category = "primal"
description = "Orchestration layer"
github_repo = "ecoPrimals/biomeOS"
forgejo_repo = "ecoPrimals/biomeOS"

[repos.squirrel]
org = "ecoPrimals"
local_path = "primals/squirrel"
membrane = "bidirectional"
sync_priority = "high"
category = "primal"
description = "AI/MCP orchestration"
github_repo = "ecoPrimals/squirrel"
forgejo_repo = "ecoPrimals/squirrel"

[repos.petalTongue]
org = "ecoPrimals"
local_path = "primals/petalTongue"
membrane = "trailing-mirror"
sync_priority = "standard"
category = "primal"
description = "Storytelling/UI bridge"
github_repo = "ecoPrimals/petalTongue"
forgejo_repo = "ecoPrimals/petalTongue"

[repos.skunkBat]
org = "ecoPrimals"
local_path = "primals/skunkBat"
membrane = "trailing-mirror"
sync_priority = "standard"
category = "primal"
description = "Defense/audit"
github_repo = "ecoPrimals/skunkBat"
forgejo_repo = "ecoPrimals/skunkBat"

[repos.sourDough]
org = "ecoPrimals"
local_path = "primals/sourDough"
membrane = "trailing-mirror"
sync_priority = "low"
category = "primal"
description = "Starter culture/bootstrap"
github_repo = "ecoPrimals/sourDough"
forgejo_repo = "ecoPrimals/sourDough"

# ═══════════════════════════════════════════════════════════════════
# Springs (syntheticChemistry org)
# ═══════════════════════════════════════════════════════════════════

[repos.primalSpring]
org = "syntheticChemistry"
local_path = "springs/primalSpring"
membrane = "trailing-mirror"
sync_priority = "high"
category = "spring"
description = "Coordination spring, composition validation"
github_repo = "syntheticChemistry/primalSpring"
forgejo_repo = "syntheticChemistry/primalSpring"

[repos.wetSpring]
org = "syntheticChemistry"
local_path = "springs/wetSpring"
membrane = "trailing-mirror"
sync_priority = "high"
category = "spring"
description = "Breseq/LTEE science validation"
github_repo = "syntheticChemistry/wetSpring"
forgejo_repo = "syntheticChemistry/wetSpring"

[repos.neuralSpring]
org = "syntheticChemistry"
local_path = "springs/neuralSpring"
membrane = "trailing-mirror"
sync_priority = "high"
category = "spring"
description = "Neural/AI validation"
github_repo = "syntheticChemistry/neuralSpring"
forgejo_repo = "syntheticChemistry/neuralSpring"

[repos.hotSpring]
org = "syntheticChemistry"
local_path = "springs/hotSpring"
membrane = "trailing-mirror"
sync_priority = "standard"
category = "spring"
description = "GPU compute validation"
github_repo = "syntheticChemistry/hotSpring"
forgejo_repo = "syntheticChemistry/hotSpring"

[repos.airSpring]
org = "syntheticChemistry"
local_path = "springs/airSpring"
membrane = "trailing-mirror"
sync_priority = "low"
category = "spring"
description = "Atmospheric/ADS-B validation"
github_repo = "syntheticChemistry/airSpring"
forgejo_repo = "syntheticChemistry/airSpring"

[repos.groundSpring]
org = "syntheticChemistry"
local_path = "springs/groundSpring"
membrane = "trailing-mirror"
sync_priority = "low"
category = "spring"
description = "Geospatial validation"
github_repo = "syntheticChemistry/groundSpring"
forgejo_repo = "syntheticChemistry/groundSpring"

[repos.healthSpring]
org = "syntheticChemistry"
local_path = "springs/healthSpring"
membrane = "trailing-mirror"
sync_priority = "low"
category = "spring"
description = "Health/clinical validation"
github_repo = "syntheticChemistry/healthSpring"
forgejo_repo = "syntheticChemistry/healthSpring"

[repos.ludoSpring]
org = "syntheticChemistry"
local_path = "springs/ludoSpring"
membrane = "trailing-mirror"
sync_priority = "low"
category = "spring"
description = "Game engine validation"
github_repo = "syntheticChemistry/ludoSpring"
forgejo_repo = "syntheticChemistry/ludoSpring"

# ═══════════════════════════════════════════════════════════════════
# Gardens (sporeGarden org)
# ═══════════════════════════════════════════════════════════════════

[repos.cellMembrane]
org = "sporeGarden"
local_path = "gardens/cellMembrane"
membrane = "inner-only"
sync_source = "forgejo"
sync_priority = "high"
category = "garden"
description = "VPS deployment, sovereignty boundary"
github_repo = "sporeGarden/cellMembrane"
forgejo_repo = "sporeGarden/cellMembrane"

[repos.lithoSpore]
org = "sporeGarden"
local_path = "gardens/lithoSpore"
membrane = "trailing-mirror"
sync_priority = "high"
category = "garden"
description = "Verification chassis, USB-deployable validation"
github_repo = "sporeGarden/lithoSpore"
forgejo_repo = "sporeGarden/lithoSpore"

[repos.projectNUCLEUS]
org = "sporeGarden"
local_path = "gardens/projectNUCLEUS"
membrane = "trailing-mirror"
sync_priority = "high"
category = "garden"
description = "Sovereignty layer, deployment infrastructure"
github_repo = "sporeGarden/projectNUCLEUS"
forgejo_repo = "sporeGarden/projectNUCLEUS"

[repos.projectFOUNDATION]
org = "sporeGarden"
local_path = "gardens/projectFOUNDATION"
membrane = "trailing-mirror"
sync_priority = "standard"
category = "garden"
description = "Knowledge layer, thread lineage, validation evidence"
github_repo = "sporeGarden/projectFOUNDATION"
forgejo_repo = "sporeGarden/projectFOUNDATION"

[repos.esotericWebb]
org = "sporeGarden"
local_path = "gardens/esotericWebb"
membrane = "trailing-mirror"
sync_priority = "low"
category = "garden"
description = "UI/agentic interaction layer"
github_repo = "sporeGarden/esotericWebb"
forgejo_repo = "sporeGarden/esotericWebb"

[repos.blueFish]
org = "sporeGarden"
local_path = "gardens/blueFish"
membrane = "trailing-mirror"
sync_priority = "low"
category = "garden"
description = "BlueFish analytical chemistry ETL product"
github_repo = "sporeGarden/blueFish"
forgejo_repo = "sporeGarden/blueFish"

[repos.helixVision]
org = "sporeGarden"
local_path = "gardens/helixVision"
membrane = "trailing-mirror"
sync_priority = "low"
category = "garden"
description = "Sovereign genomics discovery pipeline — 16S/WGS from MinION to taxonomy"
github_repo = "sporeGarden/helixVision"
forgejo_repo = "sporeGarden/helixVision"

[repos.initioChem]
org = "sporeGarden"
local_path = "gardens/initioChem"
membrane = "trailing-mirror"
sync_priority = "low"
category = "garden"
description = "Computational chemistry product — hotSpring science consumer"
github_repo = "sporeGarden/initioChem"
forgejo_repo = "sporeGarden/initioChem"

# ═══════════════════════════════════════════════════════════════════
# Infrastructure (mixed orgs)
# ═══════════════════════════════════════════════════════════════════

[repos.wateringHole]
org = "ecoPrimals"
local_path = "infra/wateringHole"
membrane = "bidirectional"
sync_priority = "high"
category = "infra"
description = "Ecosystem standards, coordination, cascading pull orchestration"
github_repo = "ecoPrimals/wateringHole"
forgejo_repo = "ecoPrimals/wateringHole"
divergence_policy = "agentic"
handoff_policy = "merge-ff"
wave_authority = "eastGate"

[repos.plasmidBin]
org = "ecoPrimals"
local_path = "infra/plasmidBin"
membrane = "trailing-mirror"
sync_priority = "high"
category = "infra"
description = "Binary depot, deploy scripts, release assets"
github_repo = "ecoPrimals/plasmidBin"
forgejo_repo = "ecoPrimals/plasmidBin"
divergence_policy = "merge-ff"  # CI harvest commits are always linear extensions

[repos.whitePaper]
org = "ecoPrimals"
local_path = "infra/whitePaper"
membrane = "trailing-mirror"
sync_priority = "standard"
category = "infra"
description = "Research documentation"
github_repo = "ecoPrimals/whitePaper"
forgejo_repo = "ecoPrimals/whitePaper"

[repos.sporePrint]
org = "ecoPrimals"
local_path = "infra/sporePrint"
membrane = "outer-only"
sync_priority = "low"
category = "infra"
description = "GitHub Pages deployment — generated site"
github_repo = "ecoPrimals/sporePrint"
forgejo_repo = "ecoPrimals/sporePrint"
divergence_policy = "impulse-only"  # multi-writer; human review preferred

[repos.benchScale]
org = "syntheticChemistry"
local_path = "infra/benchScale"
membrane = "trailing-mirror"
sync_priority = "low"
category = "infra"
description = "Lab validation infrastructure"
github_repo = "syntheticChemistry/benchScale"
forgejo_repo = "syntheticChemistry/benchScale"

[repos.agentReagents]
org = "syntheticChemistry"
local_path = "infra/agentReagents"
membrane = "trailing-mirror"
sync_priority = "low"
category = "infra"
description = "Agent configuration reagents"
github_repo = "syntheticChemistry/agentReagents"
forgejo_repo = "syntheticChemistry/agentReagents"

[repos.rustChip]
org = "syntheticChemistry"
local_path = "springs/rustChip"
membrane = "trailing-mirror"
sync_priority = "low"
category = "spring"
description = "Standalone Akida NPU driver stack — science outreach extraction from toadStool"
github_repo = "syntheticChemistry/rustChip"
forgejo_repo = "syntheticChemistry/rustChip"
exclude_remotes = ["upstream"]  # stale Brainchip fork — unrelated history

[repos.bingoCube]
org = "ecoPrimals"
local_path = "primals/bingoCube"
membrane = "trailing-mirror"
sync_priority = "low"
category = "primal"
description = "Human-verifiable cryptographic commitment system — agnostic tool leveraged by primals"
github_repo = "ecoPrimals/bingoCube"
forgejo_repo = "ecoPrimals/bingoCube"

[repos.fossilRecord]
org = "ecoPrimals"
local_path = "infra/fossilRecord"
membrane = "outer-only"
sync_priority = "low"
category = "infra"
description = "Ecosystem archive — fossilized docs, historical artifacts"
github_repo = "ecoPrimals/fossilRecord"
forgejo_repo = "ecoPrimals/fossilRecord"

# ═══════════════════════════════════════════════════════════════════
# Protists — Proto-Projects Evolving Toward Primal Status
# ═══════════════════════════════════════════════════════════════════
#
# protoKarya org repos. Proto-compositions — products that will be SERVED BY
# primals, not become primals. Protists live in protists/ and are tracked
# here for topology awareness.

[repos.footPrint]
org = "protoKarya"
local_path = "protists/footPrint"
membrane = "trailing-mirror"
sync_source = "github"
sync_priority = "standard"
category = "protist"
description = "GIS home improvement planner — primal composition target. Browser frontend (Leaflet/Turf.js) served by petalTongue, persistence by nestGate, proxy by songBird. RustScript validates pure Rust decision (gen3 §5.5)."
github_repo = "protoKarya/footPrint"
gate_owner = "flockGate"
stack = "typescript"
evolution_target = "composition"
composition_url = "https://primals.eco/footprint/"
notes = "NOT a primal. Express server disappears — primals absorb backend. Browser frontend is the product. RustScript is evidence for pure Rust, not a bridge to it."

[repos.tideGlass]
org = "protoKarya"
local_path = "protists/tideGlass"
membrane = "trailing-mirror"
sync_source = "github"
sync_priority = "standard"
category = "protist"
description = "Sovereign GPS platform — gene perturbation simulator for drug repurposing. barraCuda linear algebra, petalTongue visualization, songBird drawbridge bonds (LINCS, GEO, ChEMBL)."
github_repo = "protoKarya/tideGlass"
gate_owner = "flockGate"
stack = "typescript"
evolution_target = "composition"
composition_url = "https://tideglass.primals.eco/"
notes = "Phase 0 — GPS core. Science data via drawbridge bonds. Future: sovereign pallet hardware."

# ═══════════════════════════════════════════════════════════════════
# Composition Profiles — Fractal Deployment Patterns
# ═══════════════════════════════════════════════════════════════════
#
# Each composition is a replicable deployment shape. The same manifest
# drives any gate — the composition field selects which primals to run,
# which services to start, and what role the gate plays in the mesh.
#
# Fractal principle: the pattern is the same shape at every scale.
# A full NUCLEUS gate, a thin relay VPS, an HPC compute node, and a
# mobile Tower all read from this manifest and deploy accordingly.

[compositions.full]
description = "Complete sovereign NUCLEUS — all 13+ primals, full mesh, build-capable"
primals = ["bearDog", "songBird", "nestGate", "biomeOS", "toadStool", "squirrel", "barraCuda", "coralReef", "rhizoCrypt", "loamSpine", "sweetGrass", "petalTongue", "skunkBat"]
services = ["ipc", "mesh", "drawbridge", "gateway", "depot", "cascade"]
requires = ["rust", "musl-tools"]
examples = ["eastGate", "ironGate", "southGate"]

[compositions.thin-relay]
description = "Sovereign relay — depot + sporePrint + mesh relay. No source repos. Receives ecobins from builders, serves via TLS. Deployable on any VPS or edge node."
primals = ["songBird", "nestGate", "cellMembrane"]
services = ["relay", "depot", "sporeprint", "cascade"]
requires = []
repos = ["wateringHole"]
notes = "Fractal: deploy anywhere a sovereign presence is needed. HPC sites, edge locations, partner infrastructure. Receives pre-built ecobins via mesh.subscribe → plasmid.auto_fetch. No Rust toolchain required — runs pre-built binaries from depot."
examples = ["golgiBody"]

[compositions.tower]
description = "Minimal secure mesh entry — bearDog TLS + songBird federation + skunkBat storage"
primals = ["bearDog", "songBird", "skunkBat"]
services = ["ipc", "mesh", "drawbridge", "gateway"]
requires = []
examples = ["grapheneGate"]

[compositions.compute]
description = "Node Atomic — Tower trust boundary + compute substrate for GPU/HPC workloads"
primals = ["bearDog", "songBird", "skunkBat", "toadStool", "barraCuda", "coralReef", "biomeOS"]
services = ["ipc", "mesh", "drawbridge", "compute"]
requires = ["gpu"]
notes = "Tower Atomic base (crypto + mesh + audit) plus compute primals. Intra-inner membrane workhouse — unattended, accessible via RustDesk. Application workloads (NF pipelines, wetSpring, neuralSpring) run separately."
examples = ["strandGate"]

[compositions.nest]
description = "Nest Atomic — Tower trust boundary + storage/provenance trio for NAS/archive"
primals = ["bearDog", "songBird", "skunkBat", "nestGate", "rhizoCrypt", "loamSpine", "sweetGrass"]
services = ["ipc", "mesh", "drawbridge", "storage"]
requires = ["zfs"]
notes = "Tower Atomic base plus provenance trio. Outer membrane exposed for WAN mesh storage access."
examples = ["westGate"]

# ═══════════════════════════════════════════════════════════════════
# Gate Profiles
# ═══════════════════════════════════════════════════════════════════
# Which repos each gate cares about. cascade-pull uses these to
# filter — a gate only pulls repos it needs.

# sporeGate — public entry point, HTTP gateway, 13/13 NUCLEUS, BUILD AUTHORITY
[gates.sporeGate]
target = "x86_64-unknown-linux-musl"
mobility = "fixed"
bind_mode = "uds"
composition = "full"
transport = "lan"
mesh_peer = "[RELAY_PUBLIC]:7700"
zone = "backbone"
hub_port = "ether8"
wg_ip = "10.13.37.2"
lan_ip = "192.168.4.3"
roles = ["build_hub", "depot", "cascade_hub", "gateway", "http", "mesh_hub"]
build_authority = true
link_speed_mbps = 2500
kderm_role = "cytoplasm"
site_topology = "triangle_3hub"
notes = "Ephemeral compute entry NUC (Wave 127+). CRS310 ether8 at 2.5G. Public HTTP gateway (lab.primals.eco via Caddy → Tower). songBird mesh hub. WireGuard overlay spoke. SOVEREIGN CI: builds all 13 primals locally (12-core Ryzen 5 6600H, 27GB RAM). Demoted from edge router Wave 127 — NAT/DHCP/DNS now on Flint H1."
repos = [
    "nestGate", "wateringHole", "plasmidBin",
    "bearDog", "songBird", "toadStool", "biomeOS", "squirrel",
    "barraCuda", "coralReef", "rhizoCrypt", "loamSpine", "sweetGrass",
    "petalTongue", "skunkBat",
    "cellMembrane", "projectNUCLEUS",
]

[gates.eastGate]
target = "x86_64-unknown-linux-musl"
mobility = "fixed"
bind_mode = "uds"
composition = "full"
transport = "lan"
mesh_peer = "[RELAY_PUBLIC]:7700"
zone = "backbone"
hub_port = "sfp+2"
wg_ip = "10.13.37.5"
lan_ip = "192.168.4.244"
roles = ["overwatch", "primalspring_evolution", "meta_atomic", "build_hub"]
build_authority = true
link_speed_mbps = 10000
notes = "Primary development gate. CRS310 sfp+2 at 10G. primalSpring + overwatch. Build-capable (Ryzen 9 7950X, 128GB RAM). LAN: 192.168.4.244, confirmed 0.17ms from sporeGate."
repos = [
    "nestGate", "wateringHole", "plasmidBin", "primalSpring",
    "bearDog", "songBird", "toadStool", "biomeOS", "squirrel",
    "barraCuda", "coralReef", "rhizoCrypt", "loamSpine", "sweetGrass",
    "petalTongue", "skunkBat", "bingoCube", "sourDough",
    "cellMembrane", "projectNUCLEUS", "lithoSpore", "projectFOUNDATION",
    "esotericWebb", "blueFish", "helixVision", "initioChem",
    "whitePaper", "benchScale", "agentReagents", "rustChip", "sporePrint",
    "wetSpring", "neuralSpring", "hotSpring",
    "airSpring", "groundSpring", "healthSpring", "ludoSpring",
]

[gates.ironGate]
target = "x86_64-unknown-linux-musl"
gpu_target = "x86_64-unknown-linux-gnu"
mobility = "fixed"
bind_mode = "uds"
composition = "full"
transport = "lan"
zone = "backbone"
wg_ip = "10.13.37.7"
roles = ["node_atomic", "compute", "gpu"]
notes = "Node atomic (ToadStool, BarraCuda, CoralReef). i9-12900K + RTX 5070 Ti (CUDA). 13/13 NUCLEUS + 4x HDD enclave experiment (14TB + 1TB + 1TB + ~2TB — each disk an encrypted enclave for segregated compute/data). JupyterHub 5.4.5 LIVE on :8000. songBird drawbridge target. House 2 mesh anchor."
repos = [
    "nestGate", "wateringHole", "plasmidBin", "primalSpring",
    "bearDog", "songBird", "toadStool", "biomeOS", "squirrel",
    "barraCuda", "coralReef", "rhizoCrypt", "loamSpine", "sweetGrass",
    "petalTongue", "skunkBat",
    "cellMembrane", "projectNUCLEUS", "lithoSpore",
    "esotericWebb",
    "healthSpring", "ludoSpring",
]

[gates.southGate]
target = "x86_64-unknown-linux-musl"
mobility = "fixed"
bind_mode = "uds"
composition = "full"
transport = "lan"
mesh_peer = "[RELAY_PUBLIC]:7700"
zone = "house2"
wg_ip = "10.13.37.9"
roles = ["node_atomic", "compute"]
notes = "House 2 sovereign site. Full NUCLEUS — second hub candidate. Omada 10G. Autonomous enrollment via gate-enroll.sh."
repos = [
    "nestGate", "wateringHole", "plasmidBin", "primalSpring",
    "bearDog", "songBird", "toadStool", "biomeOS", "squirrel",
    "barraCuda", "coralReef", "rhizoCrypt", "loamSpine", "sweetGrass",
    "petalTongue", "skunkBat",
    "cellMembrane", "projectNUCLEUS",
    "wetSpring", "neuralSpring",
]

[gates.biomeGate]
repos = [
    "nestGate", "wateringHole", "plasmidBin", "primalSpring",
    "bearDog", "songBird", "toadStool", "biomeOS", "squirrel",
    "barraCuda", "coralReef", "rhizoCrypt", "loamSpine", "sweetGrass",
    "petalTongue", "skunkBat",
    "cellMembrane", "projectNUCLEUS",
    "hotSpring",
]

# fieldGate — NUC canary, full NUCLEUS 13/13, canary-fieldmouse profile
[gates.fieldGate]
target = "x86_64-unknown-linux-musl"
mobility = "fixed"
bind_mode = "uds"
composition = "full"
transport = "lan"
mesh_peer = "[RELAY_PUBLIC]:7700"
profile = "canary-fieldmouse"
zone = "house2"
hub_port = "2.5g"
link_speed_mbps = 2500
notes = "DDR3 NUC canary. Omada House 2 zone (standalone L2). OFFLINE — dead CMOS, hardware surgery."
repos = [
    "nestGate", "wateringHole", "plasmidBin",
    "bearDog", "songBird", "toadStool", "biomeOS", "squirrel",
    "barraCuda", "coralReef", "rhizoCrypt", "loamSpine", "sweetGrass",
    "petalTongue", "skunkBat",
    "cellMembrane", "projectNUCLEUS",
]

# flockGate — WAN shadow, sporePrint team, Tower atomic, full NUCLEUS
# SEGMENTATION: external-only. Reaches LAN gates exclusively via golgiBody relay.
[gates.flockGate]
target = "x86_64-unknown-linux-musl"
mobility = "fixed"
bind_mode = "uds"
composition = "full"
transport = "wan"
mesh_peer = "[RELAY_PUBLIC]:7700"
segmentation = "external-only"
wg_ip = "10.13.37.6"
roles = ["tower_atomic", "sporeprint", "wan_validator"]
notes = "WAN Tower atomic (BearDog, Songbird, SkunkBat). 13/13 NUCLEUS via user systemd. i9-13900K/62GB. SSH via golgi ProxyJump."
repos = [
    "nestGate", "wateringHole", "plasmidBin", "primalSpring",
    "bearDog", "songBird", "toadStool", "biomeOS", "squirrel",
    "barraCuda", "coralReef", "rhizoCrypt", "loamSpine", "sweetGrass",
    "petalTongue", "skunkBat", "bingoCube", "sourDough",
    "cellMembrane", "projectNUCLEUS", "lithoSpore", "projectFOUNDATION",
    "esotericWebb", "blueFish", "helixVision", "initioChem",
    "whitePaper", "benchScale", "agentReagents", "rustChip", "sporePrint",
    "wetSpring", "neuralSpring", "hotSpring",
    "airSpring", "groundSpring", "healthSpring", "ludoSpring",
    "footPrint",
]

# strandGate — bioinformatics compute, Tower Atomic workhouse (house2)
# Dual EPYC 7452 (128 threads), 256GB, RTX 3090. RJ45→Omada + RJ45→Flint2.
# Intra-inner membrane: Tower Atomic only, unattended compute workloads.
[gates.strandGate]
target = "x86_64-unknown-linux-musl"
mobility = "fixed"
bind_mode = "uds"
composition = "compute"
transport = "lan"
mesh_peer = "[RELAY_PUBLIC]:7700"
zone = "house2"
roles = ["compute", "tower_atomic"]
nucleus_status = "Tower+Compute LIVE"
notes = "Dual EPYC 7452 128-thread + RTX 3090. Tower Atomic + Compute Trio LIVE (Wave 155h). barraCuda GPU verified (SHADER_F64), coralReef 18/18 dispatch. P0: musl depot can't dlopen glibc Vulkan — source build works, glibc depot target needed."
repos = [
    "nestGate", "wateringHole", "plasmidBin",
    "bearDog", "songBird", "toadStool", "biomeOS", "squirrel",
    "barraCuda", "coralReef", "rhizoCrypt", "loamSpine", "sweetGrass",
    "petalTongue", "skunkBat",
    "cellMembrane", "projectNUCLEUS", "lithoSpore",
    "hotSpring", "wetSpring",
    "helixVision", "initioChem", "blueFish", "esotericWebb",
]

# grapheneGate — portable trust anchor (Pixel 8a, GrapheneOS)
# Tower composition LIVE (Wave 132h). Also USB tether for eastGate.
# Carries beacon/lineage seeds, acts as physical root of trust + internet relay.
[gates.grapheneGate]
gate_class = "portable_anchor"
bond_types = ["covalent"]
target = "aarch64-unknown-linux-musl"
mobility = "mobile"
bind_mode = "tcp_only"
composition = "tower"
transport = "adb"
tether_role = "usb_rndis"
nucleus_status = "Tower LIVE (bearDog 0.9.0 + songBird 0.2.1 + skunkBat 0.2.9)"
adb_ports = [9100, 9140, 9200, 9201]
depot_binaries = "15/15 (14 primals + nucleus_launcher) in pepti warehouse"
notes = "Pixel 8a — Tower via pepti warehouse, TCP-only, USB tether duality. nucleus_launcher cross-compiled (LAUNCHER-01 complete). Future: mesh.init for WAN relay via cellular backhaul."
repos = [
    "wateringHole", "plasmidBin",
    "bearDog", "songBird", "skunkBat",
]

# westGate — Nest Atomic testbed, tiered storage (house2)
# AMD Ryzen 7 5700X / 64GB DDR4 / 2TB NVMe / 5x14TB HDD raw.
# Tower Atomic LIVE (Wave 155f). Storage tiering: TIER 0-2 active, TIER 4 needs ZFS pool.
# K-Derm: periplasm (WAN-facing storage).
[gates.westGate]
target = "x86_64-unknown-linux-musl"
mobility = "fixed"
bind_mode = "uds"
composition = "nest"
transport = "lan"
mesh_peer = "[RELAY_PUBLIC]:7700"
zone = "house2"
wg_ip = "10.13.37.11"
nucleus_status = "Tower LIVE (bearDog 0.9.0 + songBird 0.2.1 + skunkBat 0.2.18, systemd user units)"
roles = ["storage", "nest", "nest_testbed", "tiered_storage"]
notes = "AMD Ryzen 7 5700X (Zen 3, 8c/16t, 32MB L3) + 64GB DDR4 + Samsung 970 EVO Plus 2TB NVMe + 5x14TB HDD OOS14000G (raw, not yet ZFS pooled). No SATA SSD (TIER 3 absent). Tower Atomic LIVE 155f — systemd user units, UDS + federation :7700. Nest Atomic testbed with tiered storage profiling. Wired to Omada."
repos = [
    "nestGate", "wateringHole", "plasmidBin",
    "bearDog", "songBird", "skunkBat", "biomeOS", "squirrel",
    "petalTongue", "rhizoCrypt", "loamSpine", "sweetGrass",
    "cellMembrane",
]

# northGate — gaming/hobby gate (Windows 11 Pro), family validation LAST
[gates.northGate]
target = "x86_64-pc-windows-gnu"
mobility = "fixed"
bind_mode = "tcp_only"
composition = "full"
transport = "lan"
mesh_peer = "[RELAY_PUBLIC]:7700"
zone = "house1"
hub_port = "ethernet"
link_speed_mbps = 2500
ipv4 = "192.168.4.147"
subnet = "192.168.4.0/22"
router = "GL.iNet GL-MT6000"
dns_suffix = "primals.local"
os = "Windows 11 Pro Build 26100"
workspace = 'C:\Users\mokke\Development\ecoPrimals'
depot_drive = "M:"
notes = "Ryzen 9950X3D + RTX 5090 + 96GB. GL-MT6000 router (house1). 837GB free on M:. RustDesk running. WireGuard needed for mesh. LAST priority."
gate_class = "family"
repos = [
    "nestGate", "wateringHole", "plasmidBin",
    "bearDog", "songBird", "toadStool", "biomeOS", "squirrel",
    "barraCuda", "coralReef", "rhizoCrypt", "loamSpine", "sweetGrass",
    "petalTongue", "skunkBat",
    "cellMembrane", "projectNUCLEUS",
]

# blueGate — distributed builder + media/gaming host (house2) — WINDOWS
# Tower Atomic workhouse + build node under sporeGate foreman.
# Plex-like media server, Steam data host. Connected via Flint 2 (2.5G).
# Intra-inner membrane: Tower Atomic only, user services.
[gates.blueGate]
target = "x86_64-pc-windows-gnu"
mobility = "fixed"
bind_mode = "tcp_only"
composition = "tower"
transport = "lan"
mesh_peer = "[RELAY_PUBLIC]:7700"
zone = "house2"
build_authority = true
roles = ["build", "tower_atomic"]
notes = "Windows. Distributed builder (Node Atomic pattern). Tower Atomic workhouse — media/gaming/house2 services. Flint 2 bridge (2.5G). Build node under sporeGate foreman."
repos = [
    "nestGate", "wateringHole", "plasmidBin",
    "bearDog", "songBird", "toadStool", "biomeOS", "squirrel",
    "barraCuda", "coralReef", "rhizoCrypt", "loamSpine", "sweetGrass",
    "petalTongue", "skunkBat",
    "cellMembrane", "projectNUCLEUS",
]

# swiftGate — hobby/consumer computer, house2 (like northGate in house1) — WINDOWS
# Full NUCLEUS, gaming/desktop/family use. Connected via Flint 2 (2.5G).
[gates.swiftGate]
target = "x86_64-pc-windows-gnu"
mobility = "fixed"
bind_mode = "tcp_only"
composition = "full"
transport = "lan"
mesh_peer = "[RELAY_PUBLIC]:7700"
zone = "house2"
gate_class = "family"
roles = ["node_atomic"]
notes = "Windows. Hobby/consumer computer for house 2 (like northGate in house 1). Full NUCLEUS. Gaming, desktop, family. Flint 2 (2.5G)."
repos = [
    "nestGate", "wateringHole", "plasmidBin",
    "bearDog", "songBird", "toadStool", "biomeOS", "squirrel",
    "barraCuda", "coralReef", "rhizoCrypt", "loamSpine", "sweetGrass",
    "petalTongue", "skunkBat",
    "cellMembrane", "projectNUCLEUS",
]

# golgiBody (sole VPS, inner membrane) — sovereign periplasm, Forgejo, relay, depot
[gates.golgiBody]
kderm_layer = "inner_membrane"
bond_types = ["covalent", "metallic"]
host = "[RELAY_PUBLIC]"
target = "x86_64-unknown-linux-musl"
mobility = "fixed"
bind_mode = "uds"
composition = "thin-relay"
transport = "local"
wg_ip = "10.13.37.1"
roles = ["forgejo", "relay", "depot", "dns_primary", "wg_hub", "caddy_tls", "remote_access", "sporeprint"]
mesh_peer = "127.0.0.1:7700"
notes = "VPS-thin: relay + depot + sporePrint. Tracks wateringHole only. No primal source repos. Forgejo shallow relay (depth=1). Receives ecobins from builder gates, serves via Caddy TLS. Fractal pattern: deploy anywhere a sovereign relay is needed."
repos = [
    "wateringHole",
]

# golgiBody-ext (VPS, outer membrane) — public-facing, sporePrint, TURN relay
[gates.golgiBody-ext]
kderm_layer = "outer_membrane"
bond_types = ["ionic", "weak"]
host = "137.184.197.151"
repos = [
    "sporePrint", "wateringHole",
]

---

## FILE: `fossilRecord/README.md`

# fossilRecord — Moved to Dedicated Repository

All fossilRecord content has been consolidated into the canonical repository:

**https://github.com/ecoPrimals/fossilRecord**

The wateringHole content lives under `wateringHole/` in that repository.

To clone: `git clone git@github.com:ecoPrimals/fossilRecord.git`

---

*Consolidated May 12, 2026. 3,231 documents moved.*

---

## FILE: `fossilRecord/wave132h_jul2026/freshness.toml`

# SPDX-License-Identifier: CC-BY-SA-4.0
#
# freshness.toml — DEPRECATED: unified view generated from wave.toml + heads/*.toml
#
# DO NOT EDIT THIS FILE DIRECTLY.
# Wave metadata: wave.toml (overwatch sole writer)
# Per-gate heads: heads/<gate>.toml (each gate sole writer of its own file)
#
# This file exists for backward compatibility with:
#   - membrane temporal.cascade --check
#   - primalSpring s_ecosystem_freshness scenario
#
# Regenerated by: membrane temporal.cascade --unify-freshness (golgi timer)
# Will be removed once all consumers migrate to wave.toml + heads/*.toml

[wave]
id = 131
date = "2026-07-04"
ssot = "specs/WATERFALL_TEMPORAL_SYNC.md"
notes = "Wave 131: All gates ONLINE (flockGate returned). songBird LAN peer.connect is singular critical path — blocks port-free mesh routing. Tower atomic (songBird/bearDog/skunkBat) back on flockGate for evolution. ironGate JupyterHub ready (localhost, ABG accounts). Caddy on sporeGate serving static lab dashboard. Zero debt across primal mountain."
publisher = "primalSpring"

[heads]
agentReagents = "6b1f32acf73daf97fbbfc5144337e2224d565a95"
airSpring = "aa0fc3de2e4a785ff088e5780f0ab015edfc044c"
barraCuda = "cbb27045f113a51589cbade2d421596e0ce56562"
bearDog = "f997a339009ec3ca8a1393748b8ac920a0d57150"
benchScale = "c95c54429b984a00f658d9ed0ce3d4744d3f9905"
bingoCube = "c9f54107d99899f0016e83988f40922b217cdf2f"
biomeOS = "1ce2a4c5be7c58b9cb2fa2be12a99329becb6485"
blueFish = "8ec23ddc42a99162ee1a512ea36fdf1cf8158fe6"
cellMembrane = "c51d688a378fbbaf616fc639c9b0eec23f28de89"
coralReef = "2e357b9dca68e43696c0c3ce9f9e6a35cc3864df"
esotericWebb = "2593302fb42627c1191a697058b75895230d395a"
groundSpring = "e2d3b9e1527a2677c3ef483f01d79bf0a2e2212f"
healthSpring = "054d5c9d6ad1e618701eab140f0eb6d9ab3e9393"
helixVision = "39e4bfe0135f8021de2e0660b1679e2533f7d957"
hotSpring = "c0245b66297ca4d8aaa27476a8895276aa736781"
initioChem = "2277cfbc87fa50f998ae61541800f1f9b3077881"
lithoSpore = "3046fb895a9e0240ba9d1d8a5ba660f79333828f"
loamSpine = "e68873d2c3092f6947f98655b7adb62d905178d8"
ludoSpring = "8e7f0d829faf5b536c2ad254b558fdae1bbdf193"
nestGate = "17baed592d3ac930f4fbd0c971086f7db1d59555"
neuralSpring = "e832c0d4e485c41c4a80d0981afad78d627eb437"
petalTongue = "cdcb1ee6dd25d608d5581e4a4f1663b6b8f167bc"
plasmidBin = "60bf2dcf063b5f7c6448ed3127f56bfac27b739d"
primalSpring = "aa4b6f2c0e948a47f68c68b2080ad7ba51e6e1c9"
projectFOUNDATION = "5ea6be80b07b12a434b0cb5905410bd0d8a058d6"
projectNUCLEUS = "c043884f54b7ab91d9cfc4daf84c640222edb3e2"
rhizoCrypt = "ff60767fcb8b86a18400a58a8c6bdfd3e02e0cfa"
rustChip = "f5c84a582bf9728afecd335ce04a35433a4f46af"
skunkBat = "6fbdc43a544351cd165b0abf11824143e05db701"
songBird = "fc766dc959fd397ee6c119d552071ab5901bd4a8"
sourDough = "406a57575265112106b405d897609a0948520927"
sporePrint = "52d1517ad8295b4418fd0693dcd393004878a619"
squirrel = "bb3a91d93970a01fbec9fbbb0509dfc9f2943aaf"
sweetGrass = "96d35e5506cdd8f8f4101eef1ccff0448ee07ab3"
toadStool = "5903cf66bb2dc01d02b39450879a59baeb63daca"
wateringHole = "4da3cdc374ea6346a8b53346c48e3c5056b3acb4"
wetSpring = "5b38488c721fb1516e6e7c7d22702c372053af88"
whitePaper = "e508156273949f0f77691f5d7023cf7c42a50510"

---

## FILE: `fossilRecord/wave132h_jul2026/README.md`

# Fossil Record — Wave 132h (July 5-6, 2026)

**Fossilization date**: Jul 6, 2026
**Wave**: 132h — LAN+WAN MESHED
**Posture at fossilization**: E2E LIVE, all mesh peered, zero P1 upstream debt

## What was archived

### FRAGOs (5) — all completed, objectives achieved
- `FRAGO_GOLGI_BIDIRECTIONAL_RELAY_WAVE132E_JUL04_2026.md` — relay LIVE, 39/39 parity
- `FRAGO_IRONGATE_JUPYTERHUB_WAVE132E_JUL04_2026.md` — JupyterHub 5.4.5 returning 200
- `FRAGO_SPOREGATE_GATEHOUSE_CUTOVER_WAVE132G_JUL05_2026.md` — Caddy retired, bearDog gatehouse active
- `IRONGATE_WAVE132_COMPUTE_REGISTRATION_JUL04_2026.md` — compute capabilities registered
- `SPOREGATE_WAVE132_GATEWAY_WIRING_JUL04_2026.md` — gateway wired to drawbridge :7780

### Superseded deployment docs (moved from top-level)
- `CELLMEMBRANE_FIELDMOUSE_DEPLOYMENT.md` — superseded by Gatehouse/Darkforest standard
- `DNS_NS_CUTOVER_INSTRUCTIONS.md` — pre-gatehouse DNS instructions (golgi still owns IP)
- `DNS_NS_CUTOVER_OPERATOR_CHECKLIST.md` — companion to above
- `S1_TLS_GRADUATION_CHECKLIST.md` — pre-gatehouse TLS plan (bearDog now owns TLS)
- `WESTGATE_ENROLLMENT_OPERATOR_CHECKLIST.md` — westGate hardware never materialized
- `SONGBIRD_VIRTUAL_ENDPOINT_RELAY_DESIGN.md` — superseded by drawbridge implementation

### Deprecated freshness file
- `freshness.toml` — deprecated, replaced by wave.toml + heads/*.toml

## What remains active

All evergreen standards (BTSP, CAPABILITY_WIRE, DARK_FOREST, etc.) remain in place.
The ecosystem's active coordination document is `handoffs/ECOSYSTEM_BLURB.md`.
Wave metadata lives in `wave.toml` + `heads/*.toml`.

## Achievements at fossilization

- E2E HTTP path: internet → golgi TLS → sporeGate drawbridge → ironGate JupyterHub → 200
- LAN mesh: sporeGate↔ironGate peered (FAMILY_ID trust)
- WAN mesh: flockGate peered via golgi relay (2 reachable peers)
- Pepti warehouse: all architectures built and published
- Caddy: permanently retired on sporeGate
- All 39 repos at GitHub↔Forgejo parity
- 13/13 primals STANDBY, 0 known debt
- primalSpring: 1095 tests passing, 122 scenarios, 0 failures

---

## FILE: `fossilRecord/wave138a_cleanup/README.md`

# Fossil Record — Wave 138a Cleanup

**Date**: 2026-07-14
**Authority**: Overwatch (eastGate)
**Action**: Distill wateringHole to clean face

---

## What Was Fossilized

### Root-Level Docs (17 files, ~4,600 lines)

Superseded by newer standards, absorbed into active docs, or pre-Wave 100
design artifacts that evolved past their original scope.

| File | Reason |
|------|--------|
| `NEURAL_API_PERCEPTRON_DESIGN.md` | P3 design doc from Wave 68. Neural API evolved past perceptron routing concept. |
| `ECOSYSTEM_ARCHITECTURE_CONTEXT.md` | Wave 111 universal context doc. Absorbed into README + STANDARDS_AND_EXPECTATIONS. |
| `GARDEN_COMPOSITION_ONRAMP.md` | gen4 product guide. Superseded by COMPOSITION_ROUTING_STANDARD (gen5 pattern). |
| `SPOREPRINT_WEBHOOK_PATTERN.md` | Wave 59. Superseded by cellMembrane content.rebuild + Caddy config. |
| `SEDIMENT_LAYER_MODEL.md` | Conceptual model. Absorbed into glossary and glacial readiness. |
| `PRIMAL_VS_SOVEREIGNTY_GOALS.md` | May 2026. Absorbed into K_DERM_TOPOLOGY and DIDERM_DOMAIN_ARCHITECTURE. |
| `UPSTREAM_CONTRIBUTIONS.md` | March 2026. Strategy doc, no active contributions tracked. |
| `EXTERNAL_VALIDATION_AND_UPSTREAM_STRATEGY.md` | Absorbed into whitePaper gen5 collaborator docs. |
| `FOUNDATION_INTEGRATION_GUIDE.md` | projectFOUNDATION integration. Superseded by composition routing. |
| `SHOWCASE_FOSSILIZATION_STANDARD.md` | Meta-standard about fossilization. Self-referential — fossilized. |
| `ANCHORING_STANDARD.md` | Absorbed into DERIVATION_ANCHORING_STANDARD (also fossilized). |
| `DERIVATION_ANCHORING_STANDARD.md` | May 2026. Anchoring not yet active. Will revive when loamSpine wires to chain. |
| `EXTERNAL_LEDGER_STANDARD.md` | Wave 63+. Pre-sovereign, superseded by loamSpine + rootPulse pattern. |
| `LITHOSPORE_USB_DEPLOYMENT.md` | May 2026. lithoSpore USB deployment is complete. Reference only. |
| `SWEETGRASS_SPRING_BRAID_PATTERNS.md` | May 2026. Absorbed into PROVENANCE_TRIO_INTEGRATION_GUIDE. |
| `TARGETED_GUIDESTONE_STANDARD.md` | May 2026. Absorbed into DEPLOYMENT_VALIDATION_STANDARD. |
| `NUCLEUS_TWO_TIER_CRYPTO_MODEL.md` | Phase 55. Absorbed into PURE_RUST_CRYPTO_PURITY_STANDARD + K_DERM. |

### gen5/ Subdirectory (3 files — Wave 63)

Early gen5 K-Derm application docs from Wave 63, fully superseded by
`whitePaper/gen5/foundations/` which has 12+ docs with deeper coverage.

| File | Superseded By |
|------|--------------|
| `KDERM_DIDERM_APPLICATION.md` | `whitePaper/gen5/foundations/KDERM_DIDERM_ENVELOPE.md` |
| `IMPULSE_POTENTIAL_KDERM_INTERACTIONS.md` | `whitePaper/gen5/foundations/IMPULSE_POTENTIAL_COORDINATION.md` |
| `TRANSPORT_EVOLUTION_NANOWIRE_TO_QUORUM.md` | `whitePaper/gen5/foundations/TRANSPORT_EVOLUTION.md` |

### sporePrint Wave Blurbs (3 files)

Per-wave deep debt blurbs. Content absorbed into blurb evolution. Stale.

### Impulses (40+ files across archive/ and archived/)

Pre-Wave 130 impulse signals. All resolved or stale. Active impulse
structure preserved (`impulses/active/`, `impulses/archive/` with .gitkeep).

### Handoff Archive (853 files across 47 wave directories)

Waves 58–133 handoff documents. All superseded by current blurb system.

### hotSpring Handoffs (57 files)

May–June 2026 hotSpring-specific handoffs. GPU pipeline, sovereign boot,
falcon ACR, etc. All resolved. coralReef and hotSpring evolved past these.

---

## What Remains (Active wateringHole)

After cleanup, wateringHole root has **47 active docs** (down from 64),
organized into clear categories in README.md. The document index in
README.md is the authoritative guide.

### Live Directories

```
handoffs/          2 active handoffs (blurb + ABG guide)
heads/             gate status files (auto-published)
provision/         golgi provisioning scripts
sporePrint/        2 active guides (CONTENT_GUIDE, SPRING_EVOLUTION_TARGETS)
petaltongue/       7 active integration docs
birdsong/          3 protocol docs
btsp/              1 stack doc
graphs/            3 deploy graph TOMLs
systemd/           templates + README
context/           gate context dirs
compute-sharing/   sovereign compute pattern
airspring/         composition guidance
healthspring/      composition guidance
hooks/             cursor + forgejo hooks
impulses/          active + archive (empty, ready for use)
genomeBin/         primal binary specs
snapshots/         gate snapshots
fossilRecord/      all archived content (this directory)
```

---

## FILE: `fossilRecord/wave139c_cleanup/README.md`

# Wave 139c Cleanup — Fossilization Record

**Date**: Jul 15, 2026 | **Wave**: 139c | **By**: eastGate overwatch

## What Was Fossilized

### Impulses (7 active → 0 active)
All 7 active divergence impulses from Jul 14 — all related to wateringHole/plasmidBin
divergence that is now fully resolved (CASCADE-HANG, SPOREGATE-PUSH, DEPOT-COVERAGE all closed).

### Handoffs (9 Wave 138 → fossilized)
- `BEARDOG_WAVE138b_HIDRAW_FIX_JUL14_2026.md` — HIDRAW P0 resolved
- `BIOMEOS_WAVE138c_AAR.md` — socket unify + lifecycle resolved
- `PRIMALSPRING_FORGEJO_PERMS_AAR_138b.md` — Forgejo perms resolved
- `PRIMALSPRING_WAVE138b.md` — superseded by Wave 139a
- `SOLOKEY_CEREMONY_ACTIVATION_AAR_138a.md` — historical record
- `SOLOKEY_CEREMONY_ENTROPY_AAR_138b.md` — historical record
- `SOLOKEY_CEREMONY_EXPLORATION_138b.md` — historical record
- `SOLOKEY_PHYSICAL_TEST_AAR_138b.md` — historical record
- `SOUNDSTAGE_CONCEPT_AAR_138b.md` — concept artifact
- `hotSpring/` handoffs directory — archived

### Stale Directories
- `genomeBin/` — old depot layout (13 files). Depot now at `/opt/ecoPrimals/depot/`
  on sporeGate and golgi VPS. 36 fresh binaries across 4 architectures.
- `snapshots/` — pre-Phase 2 config backups (4 files, Jun 25)
- `systemd/` — old cascade-pull service files (5 files). Replaced by `membrane temporal.cascade`.
- `compute-sharing/` — Wave 115 HPC design docs (28 files). Architectural planning superseded
  by current hardware inventory and mesh topology.

### Stale Heads
- `heads/golgi.toml` — old gate name (Jul 6). `golgiBody.toml` is the active head.

### Stale Impulses (root level)
- 2 root-level Wave 138b impulses (solokey, ceremony entropy)

## Post-Cleanup State
- 49 root standards (active)
- 4 active handoffs + blurb
- 1 active AAR (depot harvest)
- 5 gate heads (eastGate, flockGate, golgiBody, ironGate, sporeGate)
- 0 active impulses
- 14 subdirectories (all active)

---

## FILE: `fossilRecord/wave139c_cleanup/systemd_cascade_pull/README.md`

<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Systemd Templates — Gate Automation

Templates for automating ecosystem tasks on covalent gates.

## cascade-pull

Periodic git pull of all ecosystem repos, driven by `ecosystem_manifest.toml`
and filtered by gate profile.

### Quick Install

```bash
mkdir -p ~/.config/systemd/user

# Copy units
cp cascade-pull.service cascade-pull.timer ~/.config/systemd/user/

# Configure for this gate
cat > ~/.config/cascade-pull.env << 'EOF'
ECOPRIMALS_ROOT=/home/eastgate/Development/ecoPrimals
CASCADE_GATE=eastGate
CASCADE_PARALLEL=8
EOF

# Enable
systemctl --user daemon-reload
systemctl --user enable --now cascade-pull.timer
```

### Gate-Specific Configuration

Edit `~/.config/cascade-pull.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `ECOPRIMALS_ROOT` | (auto-detect) | Workspace root |
| `CASCADE_GATE` | `eastGate` | Gate name from `ecosystem_manifest.toml` |
| `CASCADE_PARALLEL` | `8` | Max concurrent git pulls |

### Monitoring

```bash
# Timer status
systemctl --user list-timers cascade-pull.timer

# Last run logs
journalctl --user -u cascade-pull.service --since today

# Manual trigger
systemctl --user start cascade-pull.service
```

### Comparison with forgejo-sync

| Aspect | `cascade-pull` | `forgejo-sync` |
|--------|----------------|----------------|
| Scope | All 36 repos (filtered by gate) | 6 non-mirror repos |
| Direction | GitHub/Forgejo -> local | GitHub -> Forgejo server |
| Location | Any gate | ironGate only |
| Manifest | `ecosystem_manifest.toml` | Hardcoded in script |
| Freshness | `freshness.toml` drift detection | None |

Both can coexist. `forgejo-sync` keeps Forgejo mirrors current; `cascade-pull`
keeps local gate workspaces current.

---

## FILE: `fossilRecord/wave139e_tangibles/README.md`

# Wave 139e Fossilization — Tangibles Pivot

**Date**: Jul 15, 2026 | **Fossilized by**: eastGate overwatch
**Reason**: Wave 140a reshapes blurb around protoKarya tangibles evolution.
The 139c→139d cascade fix details and OS Atheism Phase 1 shipping are
now historical context, not active scope.

## What Was Fossilized

### From ECOSYSTEM_BLURB.md (Wave 139e)

1. **"This Cascade (139c → 139d)" section** — 6 fixes documented:
   - MEMBRANE-BINARY-STALE (sporeGate membrane rebuilt f7ecefe → 13543be)
   - DEPOT-PATH-DIVERGENCE (golgi dual depot dirs → symlinked)
   - SSH-SPOREGATE-TO-GOLGI (SSH host entries added)
   - RESOLVE-DEPOT-FALLTHROUGH (depot.rs fallthrough fix)
   - NUCLEUS-SYNC (projectNUCLEUS absorbed identity commit)
   - WATERINGHOLE-GOLGI-HEADS (forgejo merge/rebase)

2. **Depot State table** — 36 binaries across 4 architectures, pipeline status

3. **OS Atheism Phase 1 shipping details** — Platform type system landed,
   FRAGO issued. Now tracked as standing context, not active cascade work.

## What Persists (carried forward to 140a)

- OS Atheism Phases 2-6 (team assignments via FRAGO — unchanged)
- Depot pipeline status (carried as standing posture)
- Gate status (updated with current state)
- Track 3 (Live Compositions) — expanded into primary focus

## Standing Context

The 139c→139e wave resolved the deepest infrastructure debt:
- Cyclic freshness → DAG (tree hashes)
- CASCADE-HANG + SPOREGATE-PUSH in cellMembrane
- Depot path unification (symlinks on both nodes)
- membrane binary on sporeGate brought current (70+ commits behind → current)
- Full multi-arch harvest (36 ecobins, Ed25519 signed)
- OS Atheism Phase 1 shipped (Platform type system)
- FRAGO system operational for inter-gate coordination

This enables the pivot to protoKarya tangibles as the primary wave focus.

---

## FILE: `fossilRecord/wave140b_absorption/README.md`

# Wave 140b Absorption — Team Deliveries + Exotic AAR

**Date**: Jul 15, 2026 | **Fossilized by**: eastGate overwatch
**Reason**: Wave 140b absorbs 3 team deliveries + 1 AAR from forgejo, reshapes blurb.

## What Was Absorbed

### 1. cellMembrane Wave 140a Deep Debt Delivery (sporeGate builder)
- OS Atheism Phase 2 shipped: `TransportEndpoint::NamedPipe`, `InitSystem::detect()`,
  platform-aware `graceful_kill`/CSPRNG/chmod
- `nix` crate eliminated (replaced with `std::process::Command("kill")`)
- Constants extracted (`ISO8601_UTC`, `ISO8601_TZ`, port constants)
- Stringly-typed → type-safe: `MembraneComposition FromStr`, `HarvestResult` deserialization
- Smart refactoring: `plasmid/mod.rs` 875→514L, `harvest.rs` 841→763L
- Codebase health: 1,074 tests, clippy clean, `#![forbid(unsafe_code)]`, 0 `unwrap()`, 0 files >800L, 15 external deps

### 2. footPrint Deep Debt Cleanup (flockGate)
- P0: Discovery pipeline fix (ECS migration broke `pm:create` listener)
- P1: XSS hardening (shared `escHtml()` utility)
- P1: Turf tree-shaking (`@turf/turf` → 12 sub-packages, 349→190 modules)
- P1: 300+ lines dead code removed (SpatialIndex, duplicate routes, unused functions)
- P1: Constants centralization (13 named constants in 12 files)
- Validation: typecheck PASS, 190 modules, 98 tests

### 3. petalTongue Wave 140a Handoff (eastGate)
- 4 Gonzales chart scenes (IC50, PK Decay, Tissue Lattice, Hormesis)
- Manifest-driven `ecosystem_handler` (reads `ecosystem_manifest.toml` at runtime)
- Full workspace clippy pedantic+nursery clean (zero warnings, 16 crates, 366 tests)
- `gate_mesh` refactor: monolithic 800L → 4-file module

### 4. Exotic Architecture Exploration AAR (sporeGate builder)
- 8/9 exotic architectures compile (RISC-V, s390x, SPARC, ARM32, ARMv7, PPC64 LE/BE, i686)
- sporeGate now 13-target build authority (4 depot + 8 exotic + 1 fail)
- Only 32-bit PowerPC fails (AtomicU64 — platform lacks native 64-bit atomics)
- 14 cross-compilers + 26 Rust targets installed
- Significance: songBird can run on IBM Z mainframes, RISC-V open silicon, embedded ARM

## Impulse Hygiene
- 3 duplicate wateringHole diverge impulses fossilized (content-identical, different timestamps)
- OS Atheism Phase 1 FRAGO fossilized (Phase 2 now delivered)
- 2 FRAGOs remain active: `cross-platform-parity-transport-abstract`, `content-addressed-convergence-pattern`

---

## FILE: `fossilRecord/wave140b_deep_review/README.md`

# Wave 140b Deep Dimensional Review — Fossilization Record

**Date**: Jul 15, 2026 | **Fossilized by**: eastGate overwatch
**Reason**: 12-dimension orthogonal review. Completed handoffs and superseded
impulses fossilized to reduce wateringHole document count.

## Handoffs Fossilized (7)

| File | Wave | Reason |
|------|------|--------|
| `NESTGATE_SESSION107_DEEP_DEBT_SWEEP_JUL14_2026.md` | 139a | Completed session — work absorbed |
| `NESTGATE_SESSION108_DEEP_DEBT_SWEEP_JUL15_2026.md` | 139a | Completed session — work absorbed |
| `PRIMALSPRING_WAVE139a.md` | 139a | Superseded by PRIMALSPRING_WAVE140a.md |
| `SPOREPRINT_DISCOVERED_BY_AAR_139a.md` | 139a | Identity anchoring complete, standard shipped |
| `CELLMEMBRANE_WAVE140a_DEEP_DEBT_DELIVERY.md` | 140a | Delivery receipt — work absorbed into blurb |
| `FOOTPRINT_DEEP_DEBT_CLEANUP_140a.md` | 140a | Delivery receipt — work absorbed into blurb |
| `PETALTONGUE_WAVE140a_HANDOFF.md` | 140a | Delivery receipt — work absorbed into blurb |

## Impulses Fossilized (2)

| File | Reason |
|------|--------|
| `2026-07-15T13-50_eastGate__diverge-wateringHole.toml` | Resolved via ff merge |
| `2026-07-15T14-45_eastGate__cross-platform-parity-transport-abstract.toml` | Superseded by `silicon-atheism-convergence` FRAGO |

## Remaining Active Handoffs (9)

| File | Status |
|------|--------|
| `ECOSYSTEM_BLURB.md` | Active — reshaped each wave |
| `CAC_CELLMEMBRANE_HANDOFF.md` | Active — P1/P2 work pending |
| `CAC_RHIZOCRYPT_HANDOFF.md` | Active — P2 work pending |
| `FOOTPRINT_SERVER_DEPLOY_HANDOFF_139a.md` | Active — server deploy still TODO |
| `PRIMALSPRING_WAVE140a.md` | Active — current wave |
| `PROTOKARYA_SCENARIO_GAPS.md` | Active — 5 scenarios still missing |
| `SILICON_ATHEISM_CONVERGENCE_WAVE140b.md` | Active — per-primal adoption tracker |
| `SPOREPRINT_WAVE140a_HANDOFF.md` | Active — content evolution ongoing |
| `ABG_JUPYTERHUB_ACCESS_GUIDE.md` | Standing reference |

## Remaining Active FRAGOs (2)

| FRAGO | Scope |
|-------|-------|
| `content-addressed-convergence-pattern` | CAC: TreeParity + impulse dedup + SessionTreeHash |
| `silicon-atheism-convergence` | Per-primal transport adoption + portable-atomic + subsystem convergence |

## 12-Dimension Review Findings

| Dim | Name | Status | Notes |
|-----|------|--------|-------|
| 1 | Temporal | ⚠️ | sporeGate head stale (Jul 6). freshness.toml at Wave 137. |
| 2 | Ecological | ✅ | 14/14 primals compile. 39/39 synced. |
| 3 | Hardware | ✅ | northGate added. westGate offline. |
| 4 | Sovereignty | ⚠️ | DNSSEC + primal.eco separation TODO. |
| 5 | Depot | ✅ | 45 binaries, 4 arch. depot_sync operational. |
| 6 | Website | ❌ | **primals.eco root 404.** footprint/ and live. both 200. |
| 7 | Glacial | ⚠️ | GLACIAL_SHIFT_READINESS.md stale (139c). |
| 8 | Compositions | ✅ | footPrint live + debt cleaned. Gonzales done. |
| 9 | Documentation | ✅ | Reduced from 16 to 9 active handoffs. |
| 10 | Cascade | ✅ | 39/39 synced. No hang. |
| 11 | CAC | ⚠️ | 2/6 layers solved. 4 pending. |
| 12 | Arch/OS | ⚠️ | 1/14 primals cross-platform. 13 targets validated. |

---

## FILE: `fossilRecord/wave143a_dimensional_review/README.md`

# Fossil Record — Wave 143a Dimensional Review

**Date**: Jul 16, 2026 | **Wave**: 143a | **From**: eastGate overwatch

## Fossilized Handoffs (21)

Single-cascade and completed team handoffs from Waves 140b-142b:
- 6 nestGate session handoffs (Sessions 109-112 + docs + debris cleanup)
- 4 coralReef wave handoffs (Waves 143-145b — deep debt, transport, docs)
- 2 rhizoCrypt handoffs (arch split + transport Phase 2)
- 1 biomeOS Session 141a cross-arch
- 1 petalTongue Wave 141a
- 1 cellMembrane Wave 142b deep debt delivery
- 1 squirrel Wave 142b transport
- 1 barraCuda Wave 142b deep debt doc cleanup
- 1 loamSpine Wave 142b transport abstraction
- 1 footPrint Wave 142b hardening
- 1 projectNUCLEUS Wave 142b deep debt sweep
- 1 primalSpring Wave 142b
- 1 Silicon Atheism convergence Wave 140b (superseded by Phase 2 FRAGO)

## Fossilized Impulses (5)

- silicon-atheism-convergence (superseded by Phase 2 FRAGO `2026-07-16T11-42`)
- 4 strandGate barracuda impulses (completed delivery)

## Key Findings from 12-Dimension Review

1. **GLACIAL_SHIFT_READINESS.md**: 551 lines, archaeological (Wave 50-100 history).
   ALL 8 CRITERIA CLEAR since Wave 137b — still valid. Needs major trim.
2. **ecosystem_manifest.toml**: version bumped 2.9.0 → 3.1.0
3. **Handoff count**: was 36 active, now 15 (21 fossilized)
4. **Active impulses**: was 7, now 2 (CAC + Phase 2)
5. **RustDesk transient**: ironGate + flockGate connectivity documented
6. **primals.eco 404**: P0 still outstanding

---

## FILE: `fossilRecord/wave150s_standards/DESKTOP_NUCLEUS_DEPLOYMENT.md`

# Desktop NUCLEUS Deployment Guide

**Version:** 1.1.0
**Date:** April 28, 2026
**Status:** Active
**Origin:** primalSpring Phase 48 — Desktop Composition (verified live)
**License:** AGPL-3.0-or-later

---

## What Is the Desktop NUCLEUS?

The Desktop NUCLEUS is the **full 13-primal stack** deployed from pre-built
plasmidBin binaries with petalTongue in `live` mode as the desktop UI surface.
It is the standard substrate that springs compose on top of and gardens deploy
for users.

**The NUCLEUS is exactly 13 primals. No spring binaries. No dev artifacts.**

| Atomic | Particle | Primals | Role |
|--------|----------|---------|------|
| **Tower** | electron | BearDog + Songbird + skunkBat | Trust boundary, crypto, discovery, defense |
| **Node** | proton | ToadStool + barraCuda + coralReef | Compute, tensor math, shader compile |
| **Nest** | neutron | NestGate + rhizoCrypt + loamSpine + sweetGrass | Storage, DAG, ledger, attribution |
| **Meta** | cross-atomic | biomeOS + Squirrel + petalTongue | Coordinator, AI, desktop UI |

**What is NOT a primal:**
- `primalspring_primal` — IPC server (JSON-RPC cell membrane)
- `primalspring_unibin` — UniBin: certify/validate/serve/status/version (absorbed guidestone + trio)
- Spring binaries — Rust science validation, not composition nodes

**A spring IS a composition of the 13 primals**, defined by a cell graph.

---

## Quick Start

### Prerequisites

- `infra/plasmidBin` with 13/13 musl-static binaries
- A display server (X11/Wayland) for petalTongue `live` mode

### Deploy

```bash
cd springs/primalSpring

# Option A: Desktop launcher (recommended)
./tools/desktop_nucleus.sh start

# Option B: Composition launcher with full NUCLEUS
PETALTONGUE_LIVE=true ./tools/composition_nucleus.sh start

# Check status
./tools/desktop_nucleus.sh status

# Stop
./tools/desktop_nucleus.sh stop
```

### Verify

```bash
# Health check all 13 primals (IPC liveness probes)
./tools/desktop_nucleus.sh status

# Deep validation (exercises actual capabilities per atomic + crypto tiers)
./tools/desktop_nucleus.sh validate

# Crypto bootstrap (derive and store two-tier purpose keys)
./tools/nucleus_crypto_bootstrap.sh

# Verify crypto keys without re-deriving
./tools/nucleus_crypto_bootstrap.sh --verify-only

# Manual: Test Tower (crypto)
echo '{"jsonrpc":"2.0","method":"crypto.blake3_hash","params":{"data":"hello"},"id":1}' | \
    socat - UNIX-CONNECT:/run/user/$(id -u)/biomeos/beardog-${FAMILY_ID}.sock

# Test Node (compute)
echo '{"jsonrpc":"2.0","method":"compute.capabilities","id":1}' | \
    socat - UNIX-CONNECT:/run/user/$(id -u)/biomeos/toadstool-${FAMILY_ID}.sock

# Test Nest (DAG)
echo '{"jsonrpc":"2.0","method":"dag.session.create","params":{"session_id":"test"},"id":1}' | \
    socat - UNIX-CONNECT:/run/user/$(id -u)/biomeos/rhizocrypt-${FAMILY_ID}.sock

# Test Meta (proprioception)
echo '{"jsonrpc":"2.0","method":"proprioception.get","id":1}' | \
    socat - UNIX-CONNECT:/run/user/$(id -u)/biomeos/petaltongue-${FAMILY_ID}.sock
```

---

## Architecture

### Atomic Structure

The 13 primals compose from three atomics plus a meta tier. Fragment
definitions live in `primalSpring/graphs/fragments/`:

```
NUCLEUS = Tower + Node + Nest
        = (BearDog + Songbird)
        + (ToadStool + barraCuda + coralReef)
        + (NestGate + rhizoCrypt + loamSpine + sweetGrass)

Desktop NUCLEUS = NUCLEUS + Meta
               = 9 domain primals + biomeOS + Squirrel + petalTongue (live)
```

Tower mediates ALL inter-atomic bonding. No cross-gate communication
happens without passing through the electron shell (BearDog + Songbird).

### Deployment Paths

**Primary: composition_nucleus.sh** (shell-managed)
- Starts all 13 primals from plasmidBin in dependency order
- Creates family-namespaced UDS sockets
- Performs health check on each primal
- Creates capability domain symlinks

**Future: biomeOS native** (`biomeos nucleus --mode full`)
- biomeOS coordinator primal manages lifecycle
- Auto-discovery of capabilities
- Health monitoring with 10s interval
- Currently launches 5 core primals; full 13 is roadmap

### Cell Graph

The canonical desktop cell graph is:

```
primalSpring/graphs/cells/nucleus_desktop_cell.toml
```

This graph defines all 13 primals in biomeOS-compatible format with:
- `coordination = "continuous"` (long-running desktop session)
- `security_model = "btsp"` on every node
- `petaltongue` with `mode = "live"`
- `biomeos_neural_api` with `spawn = false` (already running)
- Environment passthrough for `FAMILY_ID`, `BEARDOG_FAMILY_SEED`, etc.

---

## For Springs: Composing on the Desktop NUCLEUS

Springs do NOT launch primals. A spring connects to the running NUCLEUS
via capability sockets and composes through its cell graph.

### Pattern

1. Start the Desktop NUCLEUS: `./tools/desktop_nucleus.sh start`
2. Source the composition library in your domain script
3. Discover capabilities
4. Compose your domain logic using the primals

```bash
#!/usr/bin/env bash
COMPOSITION_NAME="myspring"
REQUIRED_CAPS="visualization tensor"
OPTIONAL_CAPS="dag ledger attribution ai compute shader storage"
source /path/to/primalSpring/tools/nucleus_composition_lib.sh

discover_capabilities

# Push a scene to petalTongue
push_scene '{
    "nodes": [{"id": "main", "type": "text", "content": "My Spring Live"}]
}'

# Use tensor math via barraCuda
send_rpc "$(cap_socket tensor)" "tensor.matmul" '{"lhs_id": "a", "rhs_id": "b"}'

# Record to DAG
dag_append_event "experiment_started" '{"spring": "myspring"}'
```

### Domain Overlay Template

Copy `primalSpring/graphs/cells/nucleus_desktop_overlay_template.toml`
to create your spring's cell graph. Adjust `required = false` for
capabilities your domain doesn't need.

### What Each Capability Gives You

| Capability | Primal | What You Get |
|-----------|--------|-------------|
| `security` | BearDog | Crypto signing, hashing, encryption, keypair generation |
| `discovery` | Songbird | IPC resolution, peer discovery, HTTP requests |
| `compute` | ToadStool | Workload dispatch, execution, resource status |
| `tensor` | barraCuda | Matrix math, stats, noise generation, activation functions |
| `shader` | coralReef | WGSL/SPIRV shader compilation |
| `storage` | NestGate | Content-addressed store/retrieve |
| `dag` | rhizoCrypt | Session DAG, event append, merkle proofs |
| `ledger` | loamSpine | Permanent records, certificates, spine management |
| `attribution` | sweetGrass | Provenance braids, anchoring, verification |
| `ai` | Squirrel | Inference completion, model listing, embedding |
| `visualization` | petalTongue | Scene rendering, interaction polling, proprioception |
| `orchestration` | biomeOS | Graph deployment, capability routing |

---

## For Gardens: Deploying for Users

Gardens (esotericWebb, etc.) are the user-facing products.

1. Fetch binaries from `plasmidBin` (see `PLASMINBIN_DEPOT_PATTERN.md`)
2. Deploy the Desktop NUCLEUS using the cell graph or launcher
3. Compose your garden's UI and logic through the primal capabilities
4. petalTongue `live` mode is your native desktop window

See `GARDEN_COMPOSITION_ONRAMP.md` for the full garden contract.

---

## Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `FAMILY_ID` | No | `nucleus-desktop` | Socket namespace |
| `BEARDOG_FAMILY_SEED` | No | Auto-generated | BTSP crypto seed |
| `FAMILY_SEED` | No | `$BEARDOG_FAMILY_SEED` | rhizoCrypt BTSP seed |
| `NESTGATE_JWT_SECRET` | No | Auto-generated | NestGate auth secret |
| `NODE_ID` | No | `$(hostname)` | Node identifier |
| `BEARDOG_NODE_ID` | No | `$NODE_ID` | BearDog node ID |
| `DISPLAY` | Yes (live) | `:1` | X11/Wayland display for petalTongue |
| `ECOPRIMALS_PLASMID_BIN` | No | Auto-detect | Path to plasmidBin |
| `PETALTONGUE_LIVE` | No | `true` | Enable desktop GUI |

---

## Key Files in primalSpring

| File | Purpose |
|------|---------|
| `graphs/cells/nucleus_desktop_cell.toml` | Canonical 13-primal desktop cell graph |
| `graphs/cells/nucleus_desktop_overlay_template.toml` | Template for spring domain overlays |
| `graphs/cells/cells_manifest.toml` | Index of all deployable cell graphs |
| `graphs/fragments/tower_atomic.toml` | Tower atomic definition (electron) |
| `graphs/fragments/node_atomic.toml` | Node atomic definition (proton) |
| `graphs/fragments/nest_atomic.toml` | Nest atomic definition (neutron) |
| `graphs/fragments/meta_tier.toml` | Meta tier definition (cross-atomic) |
| `graphs/fragments/nucleus.toml` | Full NUCLEUS = tower + node + nest |
| `tools/desktop_nucleus.sh` | Desktop NUCLEUS launcher |
| `tools/composition_nucleus.sh` | Full composition launcher (13 primals) |
| `tools/nucleus_composition_lib.sh` | Reusable composition wiring library |

---

## Related Documents

- `NUCLEUS_TWO_TIER_CRYPTO_MODEL.md` — Two-tier encryption architecture and per-primal evolution
- `LIVE_GUI_COMPOSITION_PATTERN.md` — petalTongue live mode interaction loop
- `DEPLOYMENT_AND_COMPOSITION.md` — Three-layer composition architecture
- `GARDEN_COMPOSITION_ONRAMP.md` — Building gen4 products
- `PRIMAL_SPRING_GARDEN_TAXONOMY.md` — Primal / spring / garden taxonomy
- `PROVENANCE_TRIO_INTEGRATION_GUIDE.md` — DAG + ledger + attribution wiring
- `SPRING_COMPOSITION_PATTERNS.md` — Composition library patterns
- `PLASMINBIN_DEPOT_PATTERN.md` (primalSpring) — Binary depot workflow

---

## plasmidBin Binary Status (April 28, 2026)

All 13 core primals are musl-static x86_64:

```
beardog      — static-pie linked (5.1M)   ✓
songbird     — static-pie linked (7.2M)   ✓
toadstool    — static-pie linked (11M)    ✓
barracuda    — static-pie linked (5.0M)   ✓
coralreef    — static-pie linked (6.5M)   ✓
nestgate     — statically linked  (7.3M)  ✓
rhizocrypt   — static-pie linked (5.7M)   ✓
loamspine    — statically linked  (4.8M)  ✓
sweetgrass   — statically linked  (9.3M)  ✓
squirrel     — static-pie linked (3.4M)   ✓
petaltongue  — static-pie linked (27M)    ✓
biomeos      — statically linked  (13M)   ✓
```

Zero C dependencies. Portable across any x86_64 Linux.

---

## IPC Method Reference

Full method map verified live against Desktop NUCLEUS:

**`springs/primalSpring/docs/NUCLEUS_IPC_METHOD_MAP.md`**

Key discovery methods per primal:
- BearDog: `rpc.methods` (returns all namespaces and methods)
- Songbird: `rpc.discover` (returns flat method list)
- Most others: `primal.capabilities` or `capabilities.list`
- All respond to `health.liveness` with `{"status":"alive"}`

---

## FILE: `fossilRecord/wave150s_standards/ECOBIN_ARCHITECTURE_STANDARD.md`

# ecoBin Architecture - Ecosystem Standard

**Status**: 🌟 **ECOSYSTEM STANDARD v3.0** 🌟  
**Adopted**: January 17, 2026  
**Evolved**: January 30, 2026 (Platform-Agnostic v2.0)  
**Evolved**: March 9, 2026 (Infrastructure C Elimination v3.0)  
**Authority**: WateringHole Consensus (All Primal Teams)  
**Compliance**: Mandatory for all new primals, recommended for existing  
**Reference Implementation**: BearDog (FIRST TRUE ecoBin), ToadStool (FIRST ecoBin v3.0)

---

## 🌍 **ecoBin v2.0 Evolution** (January 30, 2026)

**Catalyst**: Pixel 8a GrapheneOS deployment learning

**Philosophy Update**:
> **"If it can't run on the arch/platform, it's not a true ecoBin"**

**Evolution**:
- **v1.0 (Jan 17)**: Cross-Architecture (x86_64, ARM64, RISC-V) - ~80% coverage
- **v2.0 (Jan 30)**: Cross-Architecture + **Cross-Platform** - 100% coverage

**New Coverage**:
- ✅ Linux (all architectures)
- ✅ **Android** (ARM64, x86_64) - abstract sockets
- ✅ **Windows** (x86_64, ARM64) - named pipes
- ✅ macOS (Intel, M-series)
- ✅ **iOS** (ARM64) - XPC
- ✅ **WASM** (browser, Wasmtime) - in-process
- ✅ **Embedded** (bare metal) - shared memory

**Key Addition**: **Platform-agnostic IPC** (runtime transport discovery, zero assumptions)

See: `docs/deep-debt/PLATFORM_AGNOSTIC_IPC_EVOLUTION.md` in biomeOS for implementation details

---

## 📜 **Standard Declaration**

**ecoBin Architecture** is hereby adopted as the official ecosystem standard for **universal portable binaries** across all ecoPrimals. This standard builds upon UniBin by eliminating C dependencies, enabling **true cross-compilation** to any Rust-supported target with **zero external toolchain setup**.

**All primal teams** are expected to evolve toward this standard for maximum portability and security.

---

## 🎯 **Core Principle**

### **ecoBin = Ecological Binary = Universal Cross-Compilation**

**ecoBin** is a **UniBin** that achieves **FULL cross-compilation** to ANY platform, architecture, and era.

**The Ecological Principle**:
Just like ecoPrimals ecosystem is **agnostic**, **universal**, and **adaptive**, an ecoBin is a binary that:
- 🌍 **Universal**: Runs on ANY architecture (x86, ARM, RISC-V, PowerPC, etc.)
- 🖥️ **Cross-Platform**: Runs on ANY platform (Linux, Android, Windows, macOS, iOS, WASM, embedded)
- 🔧 **Agnostic**: Builds without platform-specific toolchains
- 🌿 **Adaptive**: Thrives in any computing environment
- ⏳ **Era-spanning**: Works on systems from past, present, and future

**Formula (v2.0)**:
```
ecoBin = UniBin (one binary, multiple modes)
       + FULL Cross-Compilation (any arch, any platform, any era)
       + Platform-Agnostic IPC (runtime transport discovery)
       
Achieved via:
       + Pure Rust (zero C compiler requirements!)
       + Minimal dependencies (no external toolchains!)
       + Universal portability (one build command for any target!)
       + Runtime discovery (zero platform assumptions!)
```

**Key Insight**: **Pure Rust is the MEANS, not the END!**

Pure Rust enables TRUE portability because:
- ✅ No C compiler needed → Simple cross-compilation
- ✅ No platform-specific code → Universal builds
- ✅ No external toolchains → Zero setup required
- ✅ Consistent behavior → Predictable everywhere

**The Goal**: A binary that runs **EVERYWHERE** with **ONE** `cargo build` command!

---

## 🆚 **UniBin vs ecoBin - The Distinction**

### **UniBin** (Architecture Standard)

**Definition**: Single binary per primal with multiple operational modes

**Focus**: Binary structure and CLI UX

**Requirements**:
- ✅ One binary per primal (no `-server`, `-client` suffixes)
- ✅ Subcommand-based modes (`primal <mode>`)
- ✅ Professional CLI (`--help`, `--version`)
- ⏳ May have C dependencies (openssl, ring, etc.)

**Goal**: Eliminate binary naming fragility, improve UX

**Example**:
```bash
# UniBin (may have C deps)
beardog server     # Single binary, multiple modes
beardog client     # But might depend on openssl (C)
beardog doctor     # Might not cross-compile easily
```

**Status**: ✅ Foundation (UniBin is prerequisite!)

---

### **ecoBin** (Universal Cross-Compilation Standard)

**Definition**: A UniBin that cross-compiles to ALL platforms without external toolchains

**Focus**: **TRUE ecological portability** - runs ANYWHERE, any arch, any era

**Requirements (v1.0 - Cross-Architecture)**:
- ✅ All UniBin requirements (prerequisite!)
- ✅ **FULL cross-compilation** to ALL major architectures:
  - Linux (x86_64, ARM64, ARM32, RISC-V, PowerPC, etc.)
  - macOS (Intel x86_64, Apple Silicon ARM64)
  - Windows (x86_64, ARM64)
  - Android (ARM64, x86_64)
  - WebAssembly (WASM32)
  - Embedded systems (as applicable)
- ✅ **ZERO external toolchains** required (no NDK, no musl-gcc, no Xcode SDK)
- ✅ **ONE build command** works for any target: `cargo build --target <any>`

**Additional Requirements (v2.0 - Cross-Platform)** ⭐ NEW January 30, 2026:
- ✅ **Platform-agnostic IPC**: No assumptions about Unix/Windows/etc.
- ✅ **Runtime transport discovery**: Detect best transport at runtime (Unix sockets, abstract sockets, TCP, named pipes, etc.)
- ✅ **Graceful fallback**: Prefer native transport, fall back to TCP localhost
- ✅ **Zero platform assumptions**: No hardcoded paths (`/run/user/`, `C:\`, etc.)

**How it's achieved**:
- Pure Rust (eliminates C compiler requirements)
- Careful dependency selection (must support ALL platforms)
- Tested cross-compilation matrix (proof, not theory!)

**Goal**: **Deploy ONE binary to ANY computing environment with ZERO setup!**

**Example**:
```bash
# ecoBin (FULL cross-compilation - TRUE ecological portability!)
beardog server     # Single binary
beardog client     # Builds for ANY target
beardog doctor     # Zero toolchain setup needed!

# The ecological test - ALL should succeed:
cargo build --target x86_64-unknown-linux-musl      # Linux x86
cargo build --target aarch64-unknown-linux-musl     # Linux ARM64
cargo build --target x86_64-apple-darwin            # macOS Intel
cargo build --target aarch64-apple-darwin           # macOS Silicon
cargo build --target x86_64-pc-windows-gnu          # Windows
cargo build --target aarch64-linux-android          # Android
cargo build --target wasm32-wasi                    # WebAssembly
cargo build --target riscv64gc-unknown-linux-gnu    # RISC-V

# If ALL succeed → TRUE ecoBin! 🌍
# The binary is "ecological" - it adapts to ANY environment!
```

**Status**: 🎯 Evolution target (4/6 primals on path!)

---

### **Quick Comparison Table**

| Feature | UniBin | ecoBin |
|---------|--------|--------|
| **Single binary per primal** | ✅ Required | ✅ Required (inherits) |
| **Subcommand modes** | ✅ Required | ✅ Required (inherits) |
| **Professional CLI** | ✅ Required | ✅ Required (inherits) |
| **Cross-compilation** | ⏳ Complex | ✅ **FULL** (any target!) |
| **External toolchains** | ⏳ May need | ❌ **NEVER** needed! |
| **Universal deployment** | ⏳ Limited | ✅ **COMPLETE!** |
| **Platform support** | ⏳ Some | ✅ **ALL!** |
| **Build command** | ⏳ Complex | ✅ **ONE** for any target! |

**TL;DR**:
- **UniBin** = Structure (how binary works) - Single binary with modes
- **ecoBin** = UniBin + **Universal Portability** (runs EVERYWHERE!)
- **Pure Rust** = The primary strategy to achieve ecoBin (enables FULL cross-compilation!)
- **All ecoBins are UniBins, but not all UniBins are ecoBins!**

---

## ✅ **ecoBin Requirements**

### **0. Understanding: Why Pure Rust?** (FUNDAMENTAL)

**Pure Rust is not a goal for purity's sake - it's the KEY to TRUE portability!**

**The Problem with C Dependencies**:
```
Your primal with openssl (C library):
    ↓
Needs C compiler for target platform
    ↓
Needs platform-specific headers/libs
    ↓
May need cross-compiler toolchain (musl-gcc, arm-gcc, etc.)
    ↓
May need SDKs (NDK for Android, Xcode for macOS)
    ↓
❌ FAILS ecoBin goal - CANNOT run everywhere with one command!
```

**The Power of Pure Rust**:
```
Your primal with RustCrypto (Pure Rust):
    ↓
Rust compiler compiles to target directly
    ↓
No C compiler needed
    ↓
No platform-specific toolchains
    ↓
No SDKs required
    ↓
✅ ACHIEVES ecoBin goal - runs EVERYWHERE with `cargo build`!
```

**Why Pure Rust is FUNDAMENTAL**:

1. **Eliminates Toolchain Requirements**
   - C deps require C compilers for each target
   - Pure Rust only needs `rustc` (which you already have!)
   - Result: Universal builds without setup

2. **Removes Platform Barriers**
   - C deps may need platform-specific code
   - Pure Rust compiles consistently everywhere
   - Result: True "write once, run anywhere"

3. **Simplifies Cross-Compilation**
   - C deps: `rustup target add` + `apt-get install gcc-cross` + configure
   - Pure Rust: `rustup target add` (done!)
   - Result: ONE command for any architecture

4. **Enables Future-Proof Portability**
   - New architectures emerge (RISC-V, ARM64, etc.)
   - C toolchains may lag or be unavailable
   - Rust supports new targets quickly
   - Result: Your binary works on future platforms automatically!

**Bottom Line**:
```
Pure Rust = Universal Portability
Universal Portability = ecoBin's Core Goal
Therefore: Pure Rust is FUNDAMENTAL for ecoBin!
```

**Not for purity, but for ECOLOGICAL adaptability!** 🌍

---

### **1. UniBin Compliance** (PREREQUISITE)

**Rule**: MUST meet all UniBin Architecture Standard requirements.

**See**: `UNIBIN_ARCHITECTURE_STANDARD.md` for complete requirements.

**Checklist**:
- [ ] Single binary named after primal
- [ ] Subcommand structure implemented
- [ ] `--help` comprehensive
- [ ] `--version` implemented
- [ ] Professional error messages

**Why**: ecoBin builds upon UniBin foundation!

---

### **2. Pure Rust Application Code** (MANDATORY)

**Rule**: MUST eliminate all APPLICATION C dependencies.

**Zero Tolerance List** ❌:
```toml
# These are NOT allowed in ecoBin:
openssl-sys        # Crypto (use RustCrypto instead!)
ring               # Crypto (use RustCrypto instead!)
aws-lc-sys         # Crypto (use RustCrypto instead!)
native-tls         # TLS (use rustls instead!)
zstd-sys           # Compression (use pure-rust or feature-gate!)
lz4-sys            # Compression (use pure-rust or feature-gate!)
libsqlite3-sys     # Database (use rusqlite with bundled!)
cryptoki-sys       # HSM (feature-gate or use pure-rust alternatives!)
```

**Why These Are Banned**:
- 🔥 Security vulnerabilities (C memory safety issues!)
- 🚫 Cross-compilation blockers (require C compiler!)
- 💥 Platform-specific bugs and complexity
- 🎯 Violate Pure Rust principle

**Acceptable Alternatives**:
```toml
# Use these instead (Pure Rust!):
sha2 = "0.10"              # Instead of openssl for SHA
blake3 = { version = "1.5", features = ["pure"] }  # Pure Rust hashing
rustls = "0.22"            # Instead of native-tls (still has C, Songbird only!)
rusqlite = { version = "0.30", features = ["bundled"] }  # Bundled SQLite
RustCrypto suite           # All crypto primitives in Pure Rust!
```

---

### **3. Infrastructure C: Acceptable → Eliminable** (EVOLVED in v3.0)

**Rule**: musl/libc syscall wrapper is acceptable (unavoidable OS interface).

**Two Types of C**:

#### **Application C** ❌ **NOT ALLOWED!**
```
Your crypto, HTTP, compression code in C
  ↓
SECURITY RISK! Must eliminate!
```

#### **Infrastructure C** ✅ **Acceptable**
```
musl → Linux syscalls (open, read, write)
  ↓
OS interface only, minimal risk
```

**Why musl is OK**:
- ✅ Minimal code (~1MB vs 20MB for glibc)
- ✅ Well-audited and stable (2 CVEs in 4 years, both low severity)
- ✅ No application logic (just syscall wrappers)
- ✅ Unavoidable for practical Linux programs
- ✅ Static linking (no runtime dependencies!)

**Mental Model**:
```
┌─────────────────────────────────────┐
│   YOUR APPLICATION CODE             │  ← 100% Pure Rust! ✅
│   (crypto, logic, algorithms)       │
├─────────────────────────────────────┤
│   Rust Standard Library (std)       │  ← Pure Rust! ✅
│   (collections, threads, async)     │
├─────────────────────────────────────┤
│   OS Interface (musl)                │  ← Infrastructure C ⏳
│   (open, read, write, mmap)         │     (acceptable)
├─────────────────────────────────────┤
│   Linux Kernel                       │  ← OS (irrelevant)
└─────────────────────────────────────┘
```

**v1.0/v2.0 Position**: ecoBin = 100% Pure Rust APPLICATION + musl infrastructure

**v3.0 Evolution** (March 9, 2026): toadStool proved that `/proc` parsing + `rustix`
direct syscalls can eliminate libc from application dependencies entirely. musl is
still acceptable for targets that need it, but v3.0 primals don't require it.
The long-term trajectory: `rustix` + `linux-raw-sys` → zero C in the entire binary.

**See**: ecoBin v3.0 section below for full details

---

### **4. FULL Cross-Compilation Matrix** (MANDATORY)

**Rule**: MUST successfully cross-compile to ALL major platforms.

**The ecoBin Test Matrix**:
```bash
# Linux targets (ALL must succeed!)
cargo build --release --target x86_64-unknown-linux-musl      # x86_64
cargo build --release --target aarch64-unknown-linux-musl     # ARM64
cargo build --release --target armv7-unknown-linux-musleabihf # ARM32

# macOS targets (ALL must succeed!)
cargo build --release --target x86_64-apple-darwin            # Intel Mac
cargo build --release --target aarch64-apple-darwin           # Apple Silicon

# Windows targets (SHOULD succeed)
cargo build --release --target x86_64-pc-windows-gnu          # Windows x64

# Mobile/Embedded (SHOULD succeed if applicable)
cargo build --release --target aarch64-linux-android          # Android
cargo build --release --target wasm32-wasi                    # WebAssembly

# Future/Alternative (NICE TO HAVE)
cargo build --release --target riscv64gc-unknown-linux-gnu    # RISC-V
```

**Success Criteria**:
- ✅ ALL Linux targets build without errors
- ✅ ALL macOS targets build without errors
- ✅ No C compiler errors (no `cc-rs` failures!)
- ✅ No missing toolchain errors (no `musl-gcc`, `arm-gcc`, etc. needed!)
- ✅ Binaries are static (no dynamic dependencies)
- ✅ **ONE `cargo build` command** is sufficient (no setup!)

**Failure Examples** (NOT ecoBin!):
```bash
# C dependency detected - breaks cross-compilation:
error: failed to run custom build command for `openssl-sys`
error: failed to find tool "musl-gcc"  
# ❌ Needs C cross-compiler!

# Platform-specific dependency - breaks cross-compilation:
error: failed to run custom build command for `ring`
error: failed to find tool "aarch64-linux-android-clang"  
# ❌ Needs Android NDK!

# Build script issue - breaks cross-compilation:
error: failed to run custom build command for `redb`
cc: error: unrecognized command-line option '-arch'
# ❌ Platform-specific code blocking cross-compilation!
```

**Why FULL Matrix**:
- ✅ Proves TRUE portability (not just theory!)
- ✅ Exposes hidden platform dependencies
- ✅ Validates ecological adaptability
- ✅ Ensures binary works on past, present, future platforms!

**The ecoBin Promise**:
```
If your primal passes FULL cross-compilation matrix:
→ It's a TRUE ecoBin
→ It runs EVERYWHERE
→ It's ecologically adaptive!
→ One binary for any platform, any architecture, any era! 🌍
```

---

### **5. Additional Platform Testing** (VALIDATION)

**Rule**: SHOULD test actual runtime on multiple platforms.

**Test Platforms**:
```bash
# Copy binary to diverse systems and run:
# - Different Linux distros (Ubuntu, Alpine, Debian, Fedora)
# - Different architectures (x86_64, ARM64, RISC-V)
# - Different macOS versions (Intel, Apple Silicon)
# - Different kernel versions (old and new)
# - Raspberry Pi (ARM)
# - Android devices (if applicable)
# - Windows (if applicable)

# Just copy and run:
./primal --version  # Should work everywhere! ✅
./primal doctor     # Should provide health status! ✅
```

**Success Criteria**:
- ✅ Binary runs without platform-specific errors
- ✅ No missing library errors
- ✅ Core functionality works across all platforms
- ✅ Performance is acceptable on all architectures

**Status**: Validates TRUE ecological adaptability across real-world environments!

---

### **6. Dependency Audit** (MANDATORY)

**Rule**: MUST verify zero C dependencies via `cargo tree`.

**Audit Commands**:
```bash
# Check for C system dependencies
cargo tree | grep -E "(openssl-sys|ring|aws-lc-sys|native-tls|zstd-sys|lz4-sys|libsqlite3-sys)"

# If ANY matches: NOT ecoBin!
# If zero matches: Potential ecoBin! ✅
```

**Common False Positives**:
```bash
# These are OK (infrastructure):
├── libc v0.2.151        # ✅ Rust wrapper for libc
├── cc v1.0.83           # ✅ Build tool (not runtime!)

# These are NOT OK (application C):
├── openssl-sys v0.9.96  # ❌ C crypto library!
├── ring v0.17.7         # ❌ C assembly crypto!
```

**Status**: Zero APPLICATION C dependencies = ecoBin candidate! 🎯

---

## 🏗️ **Implementation Guide**

### **Step 1: Achieve UniBin**

**Prerequisites**:
- ✅ Single binary per primal
- ✅ Subcommand structure
- ✅ Professional CLI

**See**: `UNIBIN_ARCHITECTURE_STANDARD.md`

**Time**: 1-2 weeks per primal

---

### **Step 2: Eliminate C Dependencies**

**Process**:

#### **2.1 Audit Current Dependencies**
```bash
cd /path/to/primal
cargo tree | grep -E "(openssl-sys|ring|aws-lc-sys|native-tls|zstd-sys)"
```

#### **2.2 Identify Sources**
```bash
# Find which crates pull in C deps
cargo tree -i openssl-sys
cargo tree -i ring
```

#### **2.3 Replace with Pure Rust**

**Common Replacements**:

| C Dependency | Pure Rust Alternative |
|--------------|----------------------|
| `openssl-sys` | `RustCrypto` suite (sha2, aes, etc.) |
| `ring` | `RustCrypto` suite |
| `aws-lc-sys` | `RustCrypto` suite |
| `native-tls` | `rustls` (still has C, Songbird only!) |
| `reqwest` (non-Songbird) | Remove! (Unix sockets only!) |
| `zstd-sys` | Feature-gate or remove |
| `libsqlite3-sys` | `rusqlite` with `bundled` feature |

**Example Migrations**:

**Before** (C dependencies):
```toml
[dependencies]
openssl = "0.10"          # ❌ Pulls openssl-sys!
ring = "0.17"             # ❌ C assembly!
reqwest = "0.11"          # ❌ Pulls native-tls or ring!
```

**After** (Pure Rust):
```toml
[dependencies]
sha2 = "0.10"             # ✅ Pure Rust SHA-256
blake3 = { version = "1.5", features = ["pure"] }  # ✅ Pure Rust hashing
ed25519-dalek = "2.1"     # ✅ Pure Rust signatures
# No HTTP! Use Unix sockets for IPC!
```

**Time**: 2-4 weeks per primal (depends on complexity)

---

### **Step 3: Test musl Cross-Compilation**

**Command**:
```bash
cargo build --release --target x86_64-unknown-linux-musl
```

**Expected**: Success with zero C compiler errors!

**If Fails**: You still have hidden C dependencies! Return to Step 2.

**Time**: Immediate validation

---

### **Step 4: Validate Static Binary**

**Check Dependencies**:
```bash
ldd target/x86_64-unknown-linux-musl/release/primal
```

**Expected**:
```
not a dynamic executable
```

**If Shows Libs**: Not static! Check musl target setup.

**Time**: 5 minutes

---

### **Step 5: Test Universal Deployment**

**Copy to Different Systems**:
```bash
# Copy binary to:
# - Different Linux distros (Ubuntu, Alpine, Debian)
# - Different kernel versions
# - Raspberry Pi (ARM)
# - Old systems

# Just copy and run:
./primal --version  # Should work everywhere! ✅
```

**Time**: 1 hour validation

---

### **Step 6: Declare ecoBin Compliance**

**Checklist**:
- [ ] UniBin compliant
- [ ] Zero application C dependencies
- [ ] musl cross-compilation succeeds
- [ ] Binary is static
- [ ] Tested on multiple platforms
- [ ] Documented in WateringHole

**Time**: 30 minutes documentation

---

## 🌟 **Reference Implementation: BearDog**

**Status**: ✅ **FIRST TRUE ecoBin** 🎉

### **Why BearDog is the Reference**

**UniBin** ✅:
- Single binary: `beardog`
- Multiple subcommands: `entropy`, `key`, `hsm`, `cross-primal`, `service`, `jwt`, `secret`, `rotate`, `hash`, `verify`, `audit`
- Professional CLI with `--help`, `--version`

**Pure Rust** ✅:
- Zero application C dependencies
- RustCrypto suite for all crypto
- `blake3` with `pure` feature
- No HTTP (Unix sockets only!)
- No C compression libraries

**Universal Deployment** ✅:
- Cross-compiles to `x86_64-unknown-linux-musl` ✅
- Cross-compiles to `aarch64-unknown-linux-musl` ✅
- Cross-compiles to `aarch64-linux-android` ✅ (with feature gates)
- Static binary (~4.9MB)
- Runs on any Linux (universal!)

**Validation**:
```bash
# Build for x86_64 musl
cargo build --release --target x86_64-unknown-linux-musl
# ✅ Success! No C compiler needed!

# Check dependencies
cargo tree | grep -E "(openssl-sys|ring|aws-lc-sys)"
# ✅ Zero matches!

# Verify static
ldd target/x86_64-unknown-linux-musl/release/beardog
# ✅ not a dynamic executable

# Test deployment
./beardog --version
# beardog 0.9.0
# ✅ Works everywhere!
```

**All primals should follow BearDog's ecoBin pattern!**

---

## 📊 **Ecosystem Compliance Status**

### **TRUE ecoBins** ✅ (100% Pure Rust + Universal Portability)

| Primal | Version | Certified | Validation Date |
|--------|---------|-----------|-----------------|
| **BearDog** | 0.9.0 | ✅ TRUE ecoBin #1 | Jan 17, 2026 |
| **NestGate** | 0.11.0+ | ✅ TRUE ecoBin #2 | Jan 17, 2026 |
| **sourDough** | 0.1.0 | ✅ TRUE ecoBin #3 | Jan 19, 2026 |
| **Songbird** | v5.24.0 | ✅ TRUE ecoBin #4 🎉 | Jan 24, 2026 |
| **biomeOS** | 0.1.0 | ✅ TRUE ecoBin #5 🌟 | Jan 24, 2026 |

**Notes**:
- BearDog: FIRST TRUE ecoBin (reference implementation)
- NestGate: Second TRUE ecoBin (close follower)
- sourDough: THIRD TRUE ecoBin (starter culture, scaffolding, genomeBin tooling)
- Songbird: FOURTH TRUE ecoBin (Pure Rust TLS 1.3 via Tower Atomic!)
- **biomeOS: FIFTH TRUE ecoBin (Orchestrator - proves workspace ecoBin viable!) 🌟**

**MILESTONE**: Universal Orchestrator Achieved! biomeOS orchestrates ecoBins because it IS an ecoBin!

---

### **ecoBin v3.0 Certified** (Infrastructure C Eliminated)

| Primal | Version | Certified | Validation Date | Notes |
|--------|---------|-----------|-----------------|-------|
| **ToadStool** | S141 | ✅ ecoBin v3.0 #1 | Mar 10, 2026 | sysinfo eliminated, `toadstool-sysmon` (pure /proc + rustix), cross-compile CI (aarch64, armv7), clippy pedantic `--all-targets`, zero-copy GPU payloads |

**Achievement**: First primal to reach ecoBin v3.0 — zero infrastructure C in application code.
Pattern: `/proc` parsing + `rustix` syscalls replaces libc-based crates entirely.

---

### **ecoBin Candidates** ⏳ (Close, HTTP cleanup needed)

| Primal | Status | Blockers | ETA |
|--------|--------|----------|-----|
| **Squirrel** | UniBin ✅ | HTTP legacy (delegate to Songbird) | ~2 hours |

**Notes**:
- Squirrel: Use Songbird for HTTP/TLS (via JSON-RPC) - follow Tower Atomic pattern

---

### **Work in Progress** 🚧 (UniBin but not Pure Rust)

**NONE!** 🎉

**Previous Entry** (RESOLVED):
| Primal | UniBin | Pure Rust | Status | Resolution Date |
|--------|--------|-----------|--------|-----------------|
| **Songbird** | ✅ | ✅ | **RESOLVED** | Jan 24, 2026 |

**Resolution**: Songbird achieved Pure Rust TLS 1.3 via Tower Atomic pattern with BearDog crypto delegation!

---

## 🎯 **The Tower Atomic Strategy** (Evolved from Concentrated Gap)

### **Architectural Innovation**

**Previous Principle**: Only **ONE** primal (Songbird) handles external HTTP/TLS.

**Evolution**: **ALL primals are Pure Rust via crypto delegation!**

**Why Tower Atomic Works**:
- ✅ Songbird: Pure Rust TLS 1.3 protocol implementation
- ✅ BearDog: Pure Rust cryptographic operations (RustCrypto)
- ✅ Communication: JSON-RPC over Unix sockets
- ✅ Result: BOTH are TRUE ecoBins!

**Implementation**:
```
External World (HTTPS)
    ↓
Songbird (Pure Rust TLS 1.3 - TRUE ecoBin!)
    ↓ JSON-RPC over Unix socket
BearDog (Pure Rust Crypto - TRUE ecoBin!)
    ↓ RustCrypto primitives
Pure Rust Operations
```

**Result**:
- 🎉 **4/4 primals are TRUE ecoBins!**
- 🚀 100% Pure Rust ecosystem achieved!
- ✅ Universal cross-compilation for all primals!
- 🏆 Tower Atomic pattern proven at scale!

**Status**: ✅ **ACHIEVED** - Architectural breakthrough! (Jan 24, 2026)

---

## 🚀 **Migration Path**

### **For Existing Primals**

**Phase 1: UniBin Compliance** (1-2 weeks)
- ✅ Achieve UniBin (see UNIBIN_ARCHITECTURE_STANDARD.md)
- ✅ Single binary, subcommands, professional CLI

**Phase 2: C Dependency Audit** (1 week)
- 🔍 Run `cargo tree` audit
- 📋 Identify all C dependencies
- 📝 Document sources and reasons

**Phase 3: Pure Rust Migration** (2-4 weeks)
- 🔄 Replace C dependencies with Pure Rust
- 🧪 Test functionality maintained
- ✅ Verify musl cross-compilation

**Phase 4: Validation & Certification** (1 week)
- 🧪 Cross-compile to musl targets
- 🧪 Test on multiple platforms
- 📝 Document compliance
- 🎉 Declare ecoBin!

**Total Timeline**: 5-8 weeks per primal

---

### **For New Primals**

**Requirement**: MUST implement ecoBin from day one (if not Songbird-role).

**Checklist**:
- [ ] Implement as UniBin (prerequisite)
- [ ] Use RustCrypto suite (no openssl/ring!)
- [ ] Use `blake3` with `pure` feature
- [ ] No HTTP dependencies (use Unix sockets!)
- [ ] Test musl cross-compilation early
- [ ] Verify zero C dependencies
- [ ] Document ecoBin compliance

**Timeline**: Same development time (if designed right from start!)

---

## 💡 **Best Practices**

### **1. Avoid C Dependencies from Day One**

**Prefer**:
- ✅ `RustCrypto` suite over openssl/ring
- ✅ `blake3` with `pure` feature
- ✅ Unix sockets over HTTP for IPC
- ✅ Pure Rust compression or feature-gate

**Avoid**:
- ❌ `reqwest` (unless you're Songbird!)
- ❌ `native-tls` (unless you're Songbird!)
- ❌ `ring`, `openssl`, `aws-lc-sys`
- ❌ `zstd-sys`, `lz4-sys` (use Pure Rust or feature-gate)

---

### **2. Test Cross-Compilation Early**

**Integrate into CI**:
```yaml
# .github/workflows/ci.yml
jobs:
  test-musl:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: rustup target add x86_64-unknown-linux-musl
      - run: cargo build --release --target x86_64-unknown-linux-musl
      # If this fails, you have C deps!
```

**Benefit**: Catch C dependencies early!

---

### **3. Use Feature Gates for Optional C**

**Example**:
```toml
[dependencies]
cryptoki = { version = "0.6", optional = true }  # HSM support

[features]
hsm = ["cryptoki"]  # Optional C dependency
```

**Usage**:
```bash
# Default build: Pure Rust (ecoBin!)
cargo build --target x86_64-unknown-linux-musl

# HSM build: With C deps (not ecoBin)
cargo build --features hsm
```

**Benefit**: Core is ecoBin, advanced features optional!

---

### **4. Document Dependency Rationale**

**In Cargo.toml**:
```toml
[dependencies]
# Pure Rust crypto (ecoBin compliant!)
sha2 = "0.10"             # SHA-256 hashing
blake3 = { version = "1.5", features = ["pure"] }  # BLAKE3 (pure Rust!)
ed25519-dalek = "2.1"     # Ed25519 signatures

# Note: No openssl or ring! We're 100% Pure Rust for ecoBin!
```

**Benefit**: Team understands WHY choices were made

---

### **5. Celebrate ecoBin Achievement!**

**When you achieve ecoBin**:
- 🎉 Update WateringHole documentation
- 🎉 Announce to ecosystem
- 🎉 Add badge to README
- 🎉 Share lessons learned

**Benefit**: Motivates other teams, shares knowledge!

---

## 🎓 **Examples**

### **Example 1: Crypto Migration**

**Before** (C dependencies):
```toml
[dependencies]
ring = "0.17"  # ❌ C assembly crypto
```

```rust
use ring::digest;

let hash = digest::digest(&digest::SHA256, b"data");
```

**After** (Pure Rust):
```toml
[dependencies]
sha2 = "0.10"  # ✅ Pure Rust crypto
```

```rust
use sha2::{Sha256, Digest};

let mut hasher = Sha256::new();
hasher.update(b"data");
let hash = hasher.finalize();
```

**Result**: Same functionality, zero C dependencies! ✅

---

### **Example 2: HTTP Removal**

**Before** (C dependencies):
```toml
[dependencies]
reqwest = "0.11"  # ❌ Pulls native-tls (C!)
```

```rust
let resp = reqwest::get("https://api.example.com").await?;
```

**After** (Pure Rust - Concentrated Gap):
```rust
// For external HTTP: Route through Songbird!
// For internal IPC: Use Unix sockets!

use tokio::net::UnixStream;
let stream = UnixStream::connect("/tmp/songbird.sock").await?;
// Send JSON-RPC request to Songbird to make HTTP call
```

**Result**: No HTTP dependencies, Pure Rust! ✅

---

### **Example 3: blake3 Fix**

**Before** (C assembly):
```toml
[dependencies]
blake3 = "1.5"  # ❌ Uses C assembly by default!
```

**After** (Pure Rust):
```toml
[dependencies]
blake3 = { version = "1.5", features = ["pure"] }  # ✅ Pure Rust!
```

**Result**: Same API, Pure Rust implementation! ✅

---

## 🏆 **Benefits**

### **For Security**

- ✅ Eliminate C memory safety vulnerabilities
- ✅ Reduce attack surface (no openssl CVEs!)
- ✅ Easier security auditing (Pure Rust!)
- ✅ Leverage Rust's safety guarantees

**Example**: openssl 53 CVEs (4 years) vs musl 2 CVEs (4 years)

---

### **For Portability**

- ✅ Cross-compile to ANY Rust target
- ✅ No C compiler/linker needed
- ✅ No external toolchains (NDK, musl-gcc, etc.)
- ✅ Deploy anywhere (x86, ARM, RISC-V, Android, etc.)

**Example**: Single `cargo build` command for any target!

---

### **For Development**

- ✅ Simpler build process (no C toolchain setup!)
- ✅ Faster CI (no C compiler overhead!)
- ✅ Easier debugging (Pure Rust stack traces!)
- ✅ Better IDE support (no FFI boundaries!)

---

### **For Maintenance**

- ✅ Fewer dependencies to track
- ✅ Fewer CVEs to monitor (no C libs!)
- ✅ Easier updates (Pure Rust ecosystem!)
- ✅ Better long-term stability

---

### **For Ecosystem**

- ✅ Consistent dependency strategy
- ✅ Universal deployment story
- ✅ Professional, modern architecture
- ✅ Showcase Rust's capabilities!

---

## 🔬 **ecoBin v3.0: Infrastructure C Elimination** (March 9, 2026)

### **The Evolution: From "Acceptable C" to Zero C**

**v1.0** (Jan 17, 2026): Cross-Architecture — Pure Rust application code, musl infrastructure acceptable  
**v2.0** (Jan 30, 2026): Cross-Platform — Platform-agnostic IPC, runtime transport discovery  
**v3.0** (Mar 9, 2026): **Zero Infrastructure C** — Eliminate libc/musl from application dependencies entirely

**Catalyst**: toadStool S137 proved that the largest C surface in a mature primal
(sysinfo → 15 transitive crates → libc FFI) can be replaced with pure Rust
`/proc` parsing + `rustix` direct syscalls. Zero C compilation step. Cross-compile
with just `rustup target add`.

**The v2.0 position was**: "musl infrastructure C is acceptable — it's just syscall wrappers."

**The v3.0 evolution**: "We proved we can eliminate even that. `/proc` + `rustix` =
raw Linux syscalls from pure Rust. No C compiler, no musl-tools, no NDK."

### **The Pattern: Proven Across Primals**

| Primal | C Eliminated | Pure Rust Replacement | Pattern |
|--------|-------------|----------------------|---------|
| **BearDog + Songbird** | Ring (C asm crypto) | RustCrypto suite | Tower Atomic delegation |
| **barraCuda + coralReef** | Vulkan FFI, SPIR-V tools | naga WGSL roundtrip, sovereign compiler | Node Atomic delegation (in progress) |
| **toadStool** | sysinfo (15 crates → libc) | `toadstool-sysmon` (/proc + rustix) | `/proc` parsing |
| **akida-driver** | libc VFIO ioctls | rustix ioctl wrappers | Direct syscall |

**Each primal that eliminates C teaches the ecosystem a reusable pattern.**

> **Node Atomic Delegation (April 11, 2026)**: The barraCuda + coralReef row is
> the same class of problem as BearDog + Songbird. wgpu's transitive chain
> (`wgpu` → `wgpu-hal` → `ash` → `libloading` → `dlopen(libvulkan.so.1)`)
> prevents musl-static binaries from accessing GPU hardware. The resolution
> mirrors Tower Atomic: barraCuda delegates GPU dispatch to toadStool (hardware)
> + coralReef (compiler) via IPC, with pure-Rust CPU fallback (`cpu-shader` /
> `naga-exec` + scalar Rust) when no peers are available. See
> `PORTABILITY_DEBT_AND_NODE_DELEGATION.md` for the full pattern and gap registry.

### **The DNA Analogy**

Rust as unified language = DNA.
`/proc` filesystem as kernel interface = cellular environment.
No C translation layer = no mRNA intermediate.

This gives:
- **Cross-arch**: `cargo build --target aarch64-unknown-linux-gnu` without musl-tools/NDK
- **Reproducible**: Same binary semantics on any Linux kernel (including Android)
- **Auditable**: One language, one compilation model, one type system
- **Sovereign**: No vendor toolchains, no C compilers in the build graph

### **ecoBin v3.0 Additional Requirements**

In addition to v2.0 requirements:

- **Zero `sysinfo`/`psutil` crates**: Replace with `/proc` parsing (see `toadstool-sysmon` pattern)
- **`rustix` over `libc`**: For any direct syscall needs (ioctl, mmap, statvfs)
- **Feature-gate remaining ecosystem C**: Track mio/tokio/wgpu evolution upstream
- **Cross-compile CI**: `cargo check --target aarch64-unknown-linux-gnu` in CI (no musl-tools installed)

### **Upstream Contribution Path**

ecoPrimals doesn't just eliminate C for ourselves — we evolve patterns into
standalone crates the wider Rust community can use:

- `toadstool-sysmon` → candidate for `proc-sysinfo` on crates.io
- `rustix` ioctl patterns → documented for ecosystem adoption
- Tower Atomic (crypto delegation) → architectural pattern for any Rust project
- Node Atomic (compute delegation) → IPC-first GPU dispatch without dlopen coupling

**See**: `UPSTREAM_CONTRIBUTIONS.md` for the full upstream strategy.

### **Remaining Infrastructure C (Ecosystem Phase 2)**

These remain as transitive dependencies through ecosystem crates we don't own:

| Crate | Uses libc For | Upstream Status | Our Action |
|-------|--------------|-----------------|------------|
| mio | epoll | tokio-rs/mio#1735 (rustix migration) | Track, adopt when ready |
| tokio | Via mio + signal-hook | Follows mio | Automatic |
| drm | DRM ioctls | Partial rustix adoption | Track |
| evdev | Via nix | No rustix alt yet | Consider contributing |
| wgpu-hal | GPU platform libs (`libloading` → `dlopen`) | Replaced by coralReef sovereign compiler (long-term) | Node Atomic delegation (BC-07) |
| ash | Vulkan FFI (`libloading` → `dlopen`) | Transitive via wgpu-hal | Same — eliminated by sovereign path |
| ~~ring~~ | ~~C/ASM crypto (via rustls default crypto provider)~~ | ~~NestGate NG-08~~ | **RESOLVED** (April 11) — `reqwest` → `ureq` + `rustls-rustcrypto` |

When mio adopts rustix and Rust std adopts `linux-raw-sys`, the remaining
libc paths vanish automatically. Our code is already ready.

> **NestGate ring leak — RESOLVED (April 11, 2026)**: `ring` v0.17.14 was present
> via `rustls` → `reqwest` → `nestgate-rpc`. Fix applied: `reqwest` replaced with
> `ureq` 3.3 + `rustls-rustcrypto` (pure Rust). `cargo tree -i ring` now returns
> "did not match any packages". `cargo deny check bans` PASS. NestGate ecoBin
> certification reconfirmed — zero C/ASM crypto in production binary.
> See `PORTABILITY_DEBT_AND_NODE_DELEGATION.md` for full resolution details.

### **The v3.0 Mental Model**

```
┌─────────────────────────────────────┐
│   YOUR APPLICATION CODE             │  ← 100% Pure Rust ✅
│   (crypto, logic, algorithms)       │
├─────────────────────────────────────┤
│   System Monitoring                 │  ← Pure Rust (/proc) ✅  [NEW in v3.0]
│   (CPU, memory, disk, network)      │
├─────────────────────────────────────┤
│   Syscalls                          │  ← Pure Rust (rustix) ✅  [NEW in v3.0]
│   (ioctl, mmap, statvfs)           │
├─────────────────────────────────────┤
│   Rust Standard Library (std)       │  ← Pure Rust ✅
│   (collections, threads, async)     │
├─────────────────────────────────────┤
│   Ecosystem (mio, tokio)            │  ← Transitioning to rustix ⏳
│   (event loop, async runtime)       │
├─────────────────────────────────────┤
│   Linux Kernel                      │  ← OS (irrelevant)
└─────────────────────────────────────┘
```

**v2.0 had C in layers 2-3. v3.0 eliminated it. Layer 4 is ecosystem evolution.**

### **Validation**

```bash
# Verify zero sysinfo (C surface eliminated):
cargo tree --workspace | grep sysinfo
# Expected: nothing

# Verify remaining libc is ecosystem-only:
cargo tree --workspace --invert libc | head -30
# Expected: mio, tokio, wgpu — not our code

# Cross-compile without musl-tools:
cargo check --target aarch64-unknown-linux-gnu
# Expected: success (no C toolchain needed)
```

**Status**: ✅ toadStool certified ecoBin v3.0 (March 9, 2026)  
**Next**: Track ecosystem evolution (mio/tokio rustix adoption)

---

## 📚 **Resources**

### **Documentation**

- **UniBin Standard**: `wateringHole/UNIBIN_ARCHITECTURE_STANDARD.md`
- **musl Explanation**: `biomeOS/MUSL_EXPLAINED_FOR_ECOPRIMAL.md`
- **musl vs Pure Rust**: `biomeOS/MUSL_VS_PURE_RUST_NUANCE_JAN_17_2026.md`
- **BearDog ecoBin Validation**: `biomeOS/BEARDOG_ECOBIN_VALIDATION_JAN_17_2026.md`
- **Pure Rust Status**: `biomeOS/PURE_RUST_TRUE_UNIBIN_STATUS_JAN_17_2026.md`

### **Reference Implementations**

- **BearDog**: First TRUE ecoBin (reference)
- **NestGate**: Second TRUE ecoBin

### **External Resources**

- **RustCrypto**: https://github.com/RustCrypto
- **rustls**: https://github.com/rustls/rustls
- **blake3**: https://github.com/BLAKE3-team/BLAKE3
- **rustix**: https://github.com/bytecodealliance/rustix (future)

---

## 🎯 **Compliance & Review**

### **ecoBin Compliance Checklist**

Before declaring a primal ecoBin-compliant:

**UniBin Prerequisites**:
- [ ] Single binary named after primal
- [ ] Subcommand structure implemented
- [ ] `--help` and `--version` work
- [ ] Professional CLI and error messages

**Pure Rust Requirements**:
- [ ] Zero application C dependencies
- [ ] No `openssl-sys`, `ring`, `aws-lc-sys`
- [ ] No `reqwest` (unless Songbird!)
- [ ] No `zstd-sys`, `lz4-sys` (or feature-gated)
- [ ] RustCrypto suite used for crypto
- [ ] `blake3` with `pure` feature

**Cross-Compilation Validation**:
- [ ] Builds successfully: `cargo build --target x86_64-unknown-linux-musl`
- [ ] No C compiler errors
- [ ] Binary is static (`ldd` shows "not a dynamic executable")
- [ ] Tested on multiple Linux distros
- [ ] ARM build tested (stretch goal)

**Documentation**:
- [ ] Documented in WateringHole
- [ ] Dependency rationale explained
- [ ] Migration path documented (if applicable)
- [ ] Lessons learned shared

### **Certification Process**

1. **Self-Assessment**: Use checklist above
2. **Peer Review**: Request review from ecoBin team (BearDog/NestGate)
3. **Cross-Compilation Test**: Validate musl builds
4. **Platform Testing**: Test on diverse systems
5. **WateringHole Documentation**: Update this file
6. **Announcement**: Celebrate with ecosystem! 🎉

---

## 🔄 **Version History**

### **v3.0.0** (March 9, 2026)

**Infrastructure C Elimination**

**Author**: toadStool S137 (ecoPrimals ecosystem)  
**Consensus**: WateringHole Evolution (Proven via toadStool migration)

**Changes**:
- Established ecoBin v3.0: eliminate infrastructure C (musl/libc), not just application C
- Documented `/proc` parsing + `rustix` pattern as reusable C elimination strategy
- Promoted ToadStool to first ecoBin v3.0 certified primal
- Created upstream contribution pathway for standalone crates from ecoPrimals
- Added ecosystem Phase 2 tracking (mio/tokio/wgpu rustix migration)
- Updated mental model: layers 2-3 (monitoring, syscalls) now pure Rust

**Key Achievements**:
- `sysinfo` (15 transitive crates → libc) → `toadstool-sysmon` (pure Rust, 0 C deps)
- 22+ call sites migrated across 18 files
- Cross-compilation CI: aarch64-unknown-linux-gnu, armv7-unknown-linux-gnueabihf
- Pattern mirrors Ring → RustCrypto (Tower Atomic) but for system monitoring

**The Pattern**:
```
Ring C (crypto)     → RustCrypto  (Tower Atomic)    — bearDog/songBird solved it
sysinfo C (system)  → /proc+rustix (direct parsing) — toadStool solved it
mio C (event loop)  → rustix      (upstream tracking) — ecosystem evolving
Rust std (libc)     → linux-raw-sys (language evolution) — Rust project evolving
```

**Rationale**: The v2.0 "infrastructure C is acceptable" position was pragmatic for
January 2026. By March 2026, we proved it's eliminable. The goal is a unified
language system analogous to DNA — one language (Rust), one compilation model,
compiling for any Linux-based architecture with just `rustup target add`.

---

### **v1.0.0** (January 17, 2026)

**Initial ecoBin Standard Adoption**

**Author**: biomeOS Team  
**Consensus**: WateringHole (All Primal Teams)

**Changes**:
- Established ecoBin as ecosystem standard
- Defined distinction between UniBin and ecoBin
- Documented Pure Rust requirements
- Identified reference implementations (BearDog, NestGate)
- Defined Concentrated Gap Strategy
- Created migration path for existing primals
- Explained musl infrastructure C nuance

**Rationale**:
- Enable universal cross-compilation
- Eliminate C security vulnerabilities
- Simplify deployment (no external toolchains!)
- Showcase Rust's Pure Rust capabilities
- Establish ecoPrimals as cutting-edge architecture

**Milestone**: BearDog certified as FIRST TRUE ecoBin! 🎉

---

## 📞 **Support & Questions**

### **Where to Ask**

- **WateringHole**: Inter-primal discussions
- **BearDog Team**: ecoBin implementation questions
- **NestGate Team**: ecoBin migration questions
- **biomeOS Team**: Cross-compilation and tooling

### **Common Questions**

**Q: Do I have to become an ecoBin?**  
A: Not immediately, but strongly recommended! UniBin is mandatory, ecoBin is evolution target.

**Q: What if I need C dependencies for specific features?**  
A: Use feature gates! Core should be Pure Rust (ecoBin), advanced features optional.

**Q: Is musl considered a C dependency?**  
A: Technically yes, but it's INFRASTRUCTURE C (syscall wrapper), not APPLICATION C (security risk). See `MUSL_VS_PURE_RUST_NUANCE_JAN_17_2026.md`.

**Q: Can I be an ecoBin with rustls?**  
A: Only if you're Songbird (TLS primal)! All others should use Unix sockets, not HTTP/TLS.

**Q: How long does ecoBin migration take?**  
A: 2-4 weeks for Pure Rust migration (after UniBin achieved). Depends on complexity.

**Q: What if my primal needs HTTP?**  
A: Route through Songbird! Concentrated Gap Strategy: only Songbird handles external HTTP/TLS.

**Q: What's the difference between UniBin and ecoBin?**  
A: UniBin = structure (single binary, modes). ecoBin = UniBin + Pure Rust (zero C deps).

---

## 🎊 **Conclusion**

**ecoBin Architecture** is now the **official ecosystem standard** for **universal portable binaries** across all ecoPrimals.

**This standard**:
- ✅ Builds upon UniBin foundation
- ✅ Eliminates C security vulnerabilities
- ✅ Enables universal cross-compilation
- ✅ Simplifies deployment (no toolchains!)
- ✅ Showcases Pure Rust capabilities

**Compliance pathway**:
1. ✅ UniBin (structure)
2. ✅ Pure Rust (zero C deps)
3. ✅ musl cross-compilation
4. ✅ Universal deployment
5. 🎉 ecoBin certified!

**Together, we build a Pure Rust, universally portable, secure ecosystem!**

---

**Standard**: ecoBin Architecture v1.0.0  
**Adopted**: January 17, 2026  
**Authority**: WateringHole Consensus  
**Status**: 🌟 **ACTIVE ECOSYSTEM STANDARD** 🌟

---

🦀🧬✨ **ecoBin Architecture - Pure Rust, Universal Portability!** ✨🧬🦀

**UniBin Foundation | Pure Rust Security | Universal Deployment | Zero Toolchain Setup**

---

## 🎯 **Quick Reference Card**

### **The Golden Rules**

1. **UniBin First**: Achieve UniBin before ecoBin
2. **Zero Application C**: No openssl, ring, reqwest (except Songbird!)
3. **musl Test**: Must cross-compile to musl targets
4. **Unix Sockets Only**: No HTTP except Songbird
5. **RustCrypto Suite**: Use Pure Rust crypto
6. **Feature Gate C**: Optional advanced features can have C
7. **Static Binaries**: Universal deployment
8. **Celebrate Success**: Share lessons with ecosystem!

### **Quick Validation**

```bash
# Test ecoBin compliance:
cargo build --target x86_64-unknown-linux-musl
cargo tree | grep -E "(openssl-sys|ring|aws-lc-sys)"
ldd target/x86_64-unknown-linux-musl/release/primal

# Expected:
# ✅ Build succeeds (no C compiler!)
# ✅ Zero C dependencies found
# ✅ not a dynamic executable

# Result: TRUE ecoBin! 🎉
```

---

**Your primal can be the next TRUE ecoBin!** 🚀🦀✨


---

## 🌍 **ecoBin v2.0: Platform-Agnostic Evolution** (January 30, 2026)

### **The Learning: Pixel 8a Catalyst**

**What Happened:**
- Deployed BearDog to Pixel 8a (GrapheneOS, Android 16, ARM64)
- Binary worked perfectly (cross-architecture success!)
- Socket binding failed (platform assumption discovered!)

**The Discovery:**
```
❌ Unix sockets assumed: /run/user/1000/biomeos/beardog.sock
❌ SELinux blocked user-space Unix sockets on Android
✅ Learning: "Works on Linux" ≠ "Works everywhere"
✅ Insight: Platform assumptions are technical debt!
```

**The Philosophy:**
> **"If it can't run on the arch/platform, it's not a true ecoBin"**

---

### **v1.0 vs v2.0: The Evolution**

**ecoBin v1.0 (January 17, 2026):**
```
ecoBin = UniBin + Pure Rust + Cross-Architecture
Coverage: ~80% (Linux, macOS, BSD variants)
Limitation: Unix-centric (assumes Unix sockets, /run/user/, etc.)
```

**ecoBin v2.0 (January 30, 2026):**
```
ecoBin = UniBin + Pure Rust + Cross-Architecture + Cross-Platform
Coverage: 100% (anywhere Rust compiles)
Achievement: Platform-agnostic (runtime transport discovery)
```

---

### **Platform Coverage Matrix**

| Platform | Primary IPC | Fallback | v1.0 | v2.0 |
|----------|-------------|----------|------|------|
| **Linux (Desktop/Server)** | Unix sockets | TCP localhost | ✅ | ✅ |
| **Android (Mobile)** | Abstract sockets | TCP localhost | ❌ | ✅ |
| **Windows (Desktop)** | Named pipes | TCP localhost | ⚠️ | ✅ |
| **macOS (Desktop)** | Unix sockets | TCP localhost | ✅ | ✅ |
| **iOS (Mobile)** | XPC | TCP (sandboxed) | ❌ | ✅ |
| **WASM (Browser)** | In-process | N/A | ❌ | ✅ |
| **Embedded (Bare Metal)** | Shared memory | Custom | ⚠️ | ✅ |

**Key Insight**: v2.0 adds **7 full platforms** vs v1.0's **~3 platforms**

---

### **Platform-Agnostic IPC Architecture**

**The Problem (v1.0):**
```rust
// Unix-centric code (platform assumption!)
let socket = "/run/user/1000/biomeos/beardog.sock";
let listener = UnixListener::bind(socket)?;  // ❌ Fails on Android!
```

**The Solution (v2.0):**
```rust
// Platform-agnostic code (runtime discovery!)
use biomeos_ipc::PrimalServer;

let server = PrimalServer::start_multi_transport("beardog").await?;
// ✅ Automatically selects:
//    - Unix sockets on Linux/macOS
//    - Abstract sockets on Android (@biomeos_beardog)
//    - Named pipes on Windows (\\.\pipe\biomeos_beardog)
//    - XPC on iOS (org.biomeos.beardog)
//    - In-process channels on WASM
//    - Falls back to TCP localhost if native fails
```

---

### **Transport Selection Strategy**

**Priority Order:**
1. **Try:** Platform-native transport (fastest, most secure)
   - Unix sockets (Linux, macOS, BSD)
   - Abstract sockets (Android, Linux)
   - Named pipes (Windows)
   - XPC (iOS)
   - Shared memory (embedded)
2. **Fall back:** TCP localhost (universal, always works)
3. **Report:** Log selected transport for observability

**Performance Characteristics:**

| Transport | Latency | Throughput | Security | Availability |
|-----------|---------|------------|----------|--------------|
| Unix Sockets | ~5μs | 10GB/s | Excellent | Linux, macOS, BSD |
| Abstract Sockets | ~5μs | 10GB/s | Excellent | Android, Linux |
| Shared Memory | ~1μs | 50GB/s | Good | All (requires setup) |
| Named Pipes | ~10μs | 5GB/s | Excellent | Windows |
| TCP Localhost | ~50μs | 1GB/s | Good | **Universal** |
| In-Process | ~0.1μs | N/A | Excellent | WASM, embedded |

---

### **Implementation: biomeos-ipc Crate**

**Reference Implementation:**
See `biomeOS/docs/deep-debt/PLATFORM_AGNOSTIC_IPC_EVOLUTION.md`

**Core API:**
```rust
/// Platform-agnostic transport abstraction
pub enum Transport {
    UnixSocket { path: PathBuf },        // Linux, macOS, BSD
    AbstractSocket { name: String },     // Android, Linux
    NamedPipe { name: String },          // Windows
    SharedMemory { name: String },       // All platforms
    Tcp { host: String, port: u16 },    // Universal fallback
    InProcess { channel_id: Uuid },      // WASM, embedded
    PlatformSpecific(Box<dyn Platform>), // iOS XPC, Android Binder
}

/// Server: Automatic multi-transport binding
pub struct PrimalServer {
    pub async fn start_multi_transport(primal: &str) -> Result<Self>;
    pub async fn accept(&self) -> Result<PrimalConnection>;
    pub fn transports(&self) -> Vec<Transport>;
}

/// Client: Automatic transport discovery
pub struct PrimalClient {
    pub async fn connect(primal: &str) -> Result<Self>;
    pub async fn send(&mut self, request: JsonRpcRequest) -> Result<JsonRpcResponse>;
}

/// Runtime discovery
impl Transport {
    pub async fn discover_best(primal: &str) -> Result<Self> {
        // Automatic platform detection and selection
    }
}
```

---

### **Migration Guide for Primals**

**Step 1: Add Dependency**
```toml
[dependencies]
biomeos-ipc = "1.0"  # Platform-agnostic IPC layer
```

**Step 2: Replace Socket Code**
```rust
// Old (Unix-only - v1.0)
use tokio::net::UnixListener;
let socket = format!("{}/biomeos/{}.sock", xdg_runtime, primal);
let listener = UnixListener::bind(&socket)?;

// New (Universal - v2.0)
use biomeos_ipc::PrimalServer;
let server = PrimalServer::start_multi_transport(primal).await?;
// Automatically handles all platforms!
```

**Step 3: Test on All Platforms**
```bash
# Should work on ALL without code changes:
cargo build --target x86_64-unknown-linux-musl      # Linux → Unix
cargo build --target aarch64-linux-android          # Android → Abstract
cargo build --target x86_64-pc-windows-msvc         # Windows → Pipes
cargo build --target aarch64-apple-darwin           # macOS → Unix
cargo build --target aarch64-apple-ios              # iOS → XPC
cargo build --target wasm32-unknown-unknown         # WASM → In-process
```

**Step 4: Validate**
- ✅ Runs on all platforms without code changes
- ✅ Automatic transport selection
- ✅ Graceful fallback to TCP
- ✅ Zero platform assumptions

---

### **Adoption Timeline**

**Q1 2026 (Implementation Phase):**
- Week 1-2: Create `biomeos-ipc` crate (core abstractions)
- Week 3-4: Integrate into BearDog (pilot)
- Week 5-8: Roll out to all primals
- Week 9-12: Production deployment, documentation

**Expected Outcome:**
- 100% platform coverage (Linux, Android, Windows, macOS, iOS, WASM, embedded)
- Zero platform assumptions (no hardcoded paths)
- Automatic transport selection (prefer native, fall back to TCP)
- TRUE ecoBin achieved (works everywhere Rust compiles)

---

### **The Transformation**

**Before (v1.0):**
```
"Does it run on Linux?" → Yes
"Does it run on Android?" → Sorry, not supported
"Does it run on Windows?" → Theoretically, but...
"Does it run on iOS?" → No
```

**After (v2.0):**
```
"Does it run on Linux?" → Yes (Unix sockets)
"Does it run on Android?" → Yes (abstract sockets)
"Does it run on Windows?" → Yes (named pipes)
"Does it run on iOS?" → Yes (XPC)
"Does it run on WASM?" → Yes (in-process)
"Does it run everywhere?" → YES! (TCP fallback)
```

---

### **The Deep Debt Lesson**

**What We Learned:**
1. **Platform assumptions are technical debt** (even subtle ones like Unix sockets)
2. **Runtime discovery > compile-time hardcoding** (let the binary adapt)
3. **Abstraction enables universality** (one interface, many transports)
4. **Failures are teachers** (Pixel 8a issue → architectural evolution)

**The Philosophy:**
> "TRUE PRIMAL thinking: Turn limitations into innovations,  
> failures into learning, assumptions into abstractions,  
> and good into LEGENDARY!"

---

### **For Other Primals: The Call to Evolution**

**If your primal:**
- ✅ Uses Unix sockets directly → Migrate to `biomeos-ipc`
- ✅ Hardcodes socket paths → Use runtime discovery
- ✅ Assumes `/run/user/` → Remove assumption
- ✅ Has `#[cfg(unix)]` → Replace with universal API

**Result:**
Your primal becomes a TRUE ecoBin v2.0:
- Works on any architecture
- Works on any platform
- Zero assumptions
- 100% coverage

**Resources:**
- `biomeOS/ECOBIN_TRUE_PRIMAL_STANDARD.md` - Complete specification
- `biomeOS/docs/deep-debt/PLATFORM_AGNOSTIC_IPC_EVOLUTION.md` - Implementation guide
- `wateringHole/PRIMAL_IPC_PROTOCOL.md` - Updated IPC protocol (see v2.0 section)

---

**Status**: ✅ Standard Evolved (v2.0)  
**Date**: January 30, 2026  
**Impact**: From 80% to 100% platform coverage  
**Achievement**: TRUE ecoBin - works EVERYWHERE!

---

## Current Compliance (Wave 103, Jun 9 2026)

**Zero C-dep violations across the ecosystem.** (Wave 104, Jun 9 2026)

bearDog Wave 145 resolved the last C-crypto dependency: `aws-lc-rs` → `rustls-rustcrypto`
(pure Rust), `rcgen` → `p256` + `x509-cert`. `PURE_RUST_CRYPTO_PURITY_STANDARD.md`
published as ecosystem standard. `deny.toml` bans 19 C-crypto crates. sweetGrass `ring`
elimination resolved Wave 98. All primals are now pure Rust application code.

| Target Triple | Status | Blocker |
|---------------|--------|---------|
| `x86_64-unknown-linux-musl` | **14/14 depot, operational** (VPS authority) | — |
| `aarch64-unknown-linux-musl` | **14/14 BUILT** (Wave 105 sweep complete) | NDK android next |
| `aarch64-linux-android` | 6/13 running on grapheneGate (Pixel 8) | UDS adaptation for 7 primals |
| `x86_64-pc-windows-msvc` | 0/14 | Not yet attempted |
| `wasm32-wasi` | 0/14 | Design phase |

All non-x86 targets UNBLOCKED. aarch64-musl sweep COMPLETE. **All gates fetch from VPS depot.**

---

## plasmidBin Submission (ecoBin v3.0 Gate)

Every primal that passes ecoBin must submit its binary to `ecoPrimals/infra/plasmidBin/`.
This is the ecosystem's shared binary distribution surface.

**POST-PRIMORDIAL DEPLOYMENT STANDARD (Wave 105c)**:
- **peptidoglycan/VPS is the sole build authority** — all production binaries are built on peptidoglycan
- **All gates FETCH from VPS** (`membrane.primals.eco/depot/`) — no local rebuilds for deployment
- `checksums.toml` always reflects VPS/peptidoglycan output
- Local `cargo build --release` is for **development/testing ONLY** — never deployed to `plasmidBin/primals/`
- Violating this breaks the post-primordial deployment model

### Deployment (all gates)

```bash
# Fetch from VPS (the sole authority):
membrane plasmid.fetch --source vps

# Or direct fetch:
curl -o plasmidBin/primals/x86_64-unknown-linux-musl/YOUR_PRIMAL \
  https://membrane.primals.eco/depot/x86_64-unknown-linux-musl/YOUR_PRIMAL
chmod +x plasmidBin/primals/x86_64-unknown-linux-musl/YOUR_PRIMAL
```

### Build submission (peptidoglycan only)

```bash
# ON PEPTIDOGLYCAN (VPS build authority) ONLY:
cd /path/to/your-primal

# 1. Build musl-static for x86_64
cargo build --release --target x86_64-unknown-linux-musl

# 2. Verify ecoBin compliance
file target/x86_64-unknown-linux-musl/release/YOUR_PRIMAL
# Must say: "statically linked" and NOT "not stripped"

# 3. Cross-compile for aarch64 (if .cargo/config.toml is set up)
cargo build --release --target aarch64-unknown-linux-musl

# 4. Harvest into plasmidBin (peptidoglycan deploys to VPS depot)
membrane plasmid.harvest YOUR_PRIMAL
```

**DEPRECATED**: Direct local `cargo build` → `plasmidBin/primals/` on any gate.
If you are building locally and copying to depot, you broke post-primordial deployment.

### Compliance checklist

- [ ] `file` output says "statically linked" (musl, no glibc)
- [ ] `file` output does NOT say "not stripped"
- [ ] `ldd` says "statically linked" or "not a dynamic executable"
- [ ] Binary runs on Pixel/GrapheneOS via ADB (aarch64)
- [ ] Binary starts with TCP listener (`--listen` or `--port`)
- [ ] `health.liveness` responds over TCP JSON-RPC
- [ ] `b3sum` checksum recorded in `checksums.toml`

### Current inventory (March 31, 2026)

| Primal | x86_64 | aarch64 | ecoBin |
|--------|--------|---------|--------|
| beardog | A++ | A++ | Full |
| songbird | A++ | A++ | Full |
| nestgate | A++ | pending | x86 only |
| squirrel | A++ | A++ | Full |
| toadstool | A++ | A++ | Full |
| petaltongue | A++ | pending | x86 only |
| biomeos | A++ | A+ | Full (aarch64 unstripped) |
| coralreef | A++ | pending | x86 only (coralreef-core, coralctl; aarch64 build pending GPU driver evolution) |

See `plasmidBin/README.md` for the complete inventory and workflow.


---

## FILE: `fossilRecord/wave150s_standards/GLACIAL_SHIFT_READINESS.md`

# Glacial Shift Readiness

**Status**: Active tracking document  
**Phase**: Stadial — PUBLIC + SOVEREIGN
**Last updated**: 2026-07-17 (Wave 147b — ALL 8 CRITERIA CLEAR. 59 depot binaries across 4 architectures. Silicon Atheism Phase 2 COMPLETE 14/14 transport. CAC 6/6 COMPLETE. 6-gate mesh LIVE. gate.enroll SHIPPED.)

---

## Position

**PUBLIC + SOVEREIGN.** ALL 8 CRITERIA CLEAR FOR STADIAL ENTRY (since Wave 137b).

59 depot binaries across 4 architectures (Windows 14/14 COMPLETE). Silicon Atheism
Phase 1 COMPLETE (14/14 primals, all depot architectures). Phase 2 COMPLETE
(14/14 primals ship trait-based transport abstraction). CAC 6/6 COMPLETE.

4 live surfaces: `primals.eco/footprint/` (GIS), `live.primals.eco` (TOPO-VIS),
`lab.primals.eco` (JupyterHub). Root `primals.eco` 404 outstanding.

6-gate WireGuard mesh LIVE. gate.enroll automated enrollment shipped.
Depot: 59 binaries, BLAKE3 + Ed25519 signed, VPS depot serving.
All repos converged. 0 active impulses.

---

## Glacial Shift Criteria (8/8 CLEAR)

| # | Criterion | Status |
|---|-----------|--------|
| 1 | Sovereignty shadows graduated (inner membrane) | **CLEAR** — S1-S4 ALL GRADUATED |
| 2 | Multi-gate LAN mesh operational (3+) | **CLEAR** — 5+ gate mesh |
| 3 | Peptidoglycan replicable | **CLEAR** — deterministic deployment codified |
| 4 | Remote covalent node over WAN | **CLEAR** — flockGate WAN validated |
| 5 | DNS sovereign for inner membrane | **CLEAR** — primal.eco + nestgate.io |
| 6 | Inner membrane zero-commercial + cross-validation | **CLEAR** — zero commercial in data path |
| 7 | guideStone-grade deployment across all gates | **CLEAR** — 5 properties satisfied |
| 8 | Outer membrane hardened for public exposure | **CLEAR** — security headers, fail2ban, CSP, rate-limiting |

---

## Current Deployment Surface

```
Depot (4 arch, 59 bins — Wave 143a):
  x86_64-linux-musl     14/14   FRESH
  aarch64-linux-musl    14/14   FRESH
  aarch64-android       14/14   FRESH
  x86_64-windows-gnu    14/14   FRESH (Wave 142b harvest)
  BLAKE3 + Ed25519 signed. VPS depot serving.

Exotic validated (songBird): riscv64gc powerpc64le powerpc64 s390x sparc64 arm32 armv7 i686
```

## Gate Status

| Gate | Status | NUCLEUS |
|------|--------|---------|
| eastGate | PRIMARY, cascade authority | FULL (39/39 synced) |
| sporeGate | NUCLEUS, 13-target build authority | 59 depot bins |
| golgiBody | VPS, outer membrane | footprint/ + live serving |
| ironGate | ABG/NF compute, JupyterHub | OPERATIONAL (RustDesk transient) |
| flockGate | WAN covalent, 16 bonds | OPERATIONAL (RustDesk transient) |
| northGate | Windows mesh target, RTX 5090 | ENROLLED (10.13.37.8) |
| grapheneGate | Pixel 8, StrongBox target | 14/14 Android ecobins |
| westGate | ZFS cold storage | OFFLINE |

## Sovereignty Shadows (ALL GRADUATED)

| Track | Status |
|-------|--------|
| S1 — TLS termination | GRADUATED (Caddy + LE) |
| S2 — NAT relay | GRADUATED (Songbird TURN) |
| S3 — Content serving | GRADUATED (NestGate + petalTongue) |
| S4 — Auth | GRADUATED (BearDog BTSP) |

## Remaining Software Items

| Item | Owner | Priority | Status |
|------|-------|----------|--------|
| sporePrint rebuild on golgi (P0 — 404) | sporePrint/golgi operator | **P0** | DIVERGENCE |
| gate.enroll hub-side peer automation | cellMembrane | P1 | NEAR-TERM |
| songBird beacon protocol (BTSP enrollment) | songBird | P1 | NEAR-TERM |
| northGate NUCLEUS deploy + benchScale | sporeGate | P1 | NEXT |
| DNSSEC on primals.eco | operator | P2 | TODO |
| footPrint composition wiring (WS_PATH, PROXY_PATH) | petalTongue, songBird | P2 | TODO |
| bearDog HSM → Android Keystore | bearDog | P2 | TODO |
| tideGlass Phase 0 | overwatch + Gonzales | P2 | TODO |

## Next Glacial Goal: Universal Substrate Evolution

The ecoBin/genomeBin system evolves to full NUCLEUS deployments across all
architectures. Silicon Atheism Phase 2 (abstraction over gating) is the
current evolution vector — every target is a first-class substrate.

---

*Full historical record: `fossilRecord/wave143a_dimensional_review/GLACIAL_SHIFT_READINESS_FULL_HISTORY.md`*

---

## FILE: `fossilRecord/wave150s_standards/PLASMIDBIN_PUSH_AUTOMATION_STANDARD.md`

# plasmidBin Push Automation Pipeline — Ecosystem Standard

**Status**: ACTIVE  
**Version**: 2.0 — Rust CLI  
**Date**: May 26, 2026  
**Authority**: primalSpring (pipeline owner)  
**Depends on**: [ECOBIN_ARCHITECTURE_STANDARD.md](ECOBIN_ARCHITECTURE_STANDARD.md)

---

## Overview

Every push to a primal's `main` branch triggers an automated pipeline that
builds ecoBin-compliant static binaries, computes BLAKE3 checksums, publishes
to `plasmidBin`, and creates GitHub Releases. This document defines the
pipeline, its components, and the contract each primal team must uphold.

## Pipeline Flow

```
Primal push to main
        │
        ▼
notify-plasmidbin.yml (per-primal workflow)
  sends repository_dispatch event-type: primal-updated
  payload: { primal, sha }
        │
        ▼
auto-harvest.yml (plasmidBin repo)
        │
   ┌────┴────┐
   │ prepare  │  Determine primal + version tag
   └────┬────┘
        │
   ┌────┴──────────────────────────┐
   │ build (3x parallel matrix)    │
   │  x86_64-unknown-linux-musl    │
   │  aarch64-unknown-linux-musl   │
   │  armv7-unknown-linux-musleabihf│
   └────┬──────────────────────────┘
        │
   ┌────┴──────────┐
   │  consolidate          │
   │  plasmidbin harvest    │  per-arch: validate, strip, BLAKE3, copy
   │  ↓                     │
   │  commit                │  checksums.toml + binaries
   │  ↓                     │
   │  plasmidbin validate   │  post-harvest integrity check
   │  ↓                     │
   │  release               │  GitHub Release (vYYYY.MM.DD)
   └────────────────────────┘
        │
        ▼
Downstream consumers (plasmidbin fetch)
  verify BLAKE3 against checksums.toml
```

## Triggers

| Trigger | When | Scope |
|---------|------|-------|
| `repository_dispatch` | Primal pushes to `main` | Single primal |
| `workflow_dispatch` | Manual (operator) | Single primal or `all` |
| `check-updates.yml` (daily) | Lightweight tag checker dispatches stale primals | Per-primal (selective) |
| Weekly cron (Monday 06:00 UTC) | Full sweep | `all` |

The daily `check-updates.yml` replaces the old full-sweep cron. It queries
GitHub Releases for upstream tag changes and dispatches `auto-harvest` only
for primals with new tags. `plasmidbin harvest` skips binaries whose BLAKE3
hash already matches `checksums.toml`.

## Primal Team Contract

Every primal repository with its own git repo MUST have:

1. **`.github/workflows/notify-plasmidbin.yml`** — the dispatch workflow.
   Template lives at `infra/plasmidBin/templates/notify-plasmidbin.yml`.
   Copy it verbatim; do not customize.

2. **`PLASMIDBIN_DISPATCH_TOKEN` secret** — a GitHub PAT with `repo` scope on
   the `ecoPrimals/plasmidBin` repository. Set as a repository secret.

3. **`sources.toml` entry** — `infra/plasmidBin/sources.toml` must have a
   `[sources.<primal>]` section with the correct `repo` URL.

### Current Wiring Status (May 2026)

All 13 primals with their own repositories are wired:
bearDog, songbird, toadStool, barraCuda, coralReef, rhizoCrypt, loamSpine,
sweetGrass, biomeOS, squirrel, petalTongue, skunkBat, nestGate.

## Key Commands (Rust CLI — Wave 51)

All pipeline operations now use the `plasmidbin` Rust CLI (15 subcommands).
Legacy `.sh` scripts have been fossilized (Wave 66). The `plasmidbin` binary is the sole pipeline.

### `plasmidbin build`

Clones a primal (from `sources.toml`), builds for a target triple, and stages
the binary to `/tmp/primalspring-deploy/primals/{triple}/`.

```
cargo run -p plasmidbin -- build beardog --target x86_64-unknown-linux-musl
cargo run -p plasmidbin -- build all --target aarch64-unknown-linux-musl
```

### `plasmidbin harvest`

Takes staged binaries, validates they are static ELFs, strips them, computes
BLAKE3 checksums, copies to `plasmidBin/primals/{triple}/`, and updates
`checksums.toml`.

**Idempotent**: If the computed BLAKE3 hash matches the existing
`checksums.toml` entry, the binary is skipped. This prevents no-op commits
from polluting git history during reconciliation runs.

```
cargo run -p plasmidbin -- harvest --source /path/to/bins --arch x86_64-unknown-linux-musl
cargo run -p plasmidbin -- harvest --primal beardog --arch aarch64
cargo run -p plasmidbin -- harvest --dry-run
```

Exit code 1 if any binary fails validation.

### `plasmidbin fetch`

Downloads binaries from GitHub Releases, verifies BLAKE3 checksums against
`checksums.toml`, and installs to `primals/{triple}/`. Auto-detects host
architecture.

```
cargo run -p plasmidbin -- fetch --all
cargo run -p plasmidbin -- fetch --primal beardog
cargo run -p plasmidbin -- fetch --all --release v2026.05.26
```

### `plasmidbin validate`

Post-harvest integrity check. Reads `manifest.toml`, `checksums.toml`, and
`sources.toml`; verifies cross-references and checksum presence.

```
cargo run -p plasmidbin -- validate .
```

## `checksums.toml` Format

```toml
[primals.beardog]
"x86_64-unknown-linux-musl" = "<blake3-hex>"
"aarch64-unknown-linux-musl" = "<blake3-hex>"
"armv7-unknown-linux-musleabihf" = "<blake3-hex>"
```

Keys are full Rust target triples (quoted). Values are 64-character lowercase
hex BLAKE3 hashes of the stripped binary. Sections follow the pattern
`primals.<name>` or `springs.<name>`.

## Error Handling

The pipeline is designed to **fail loudly** rather than commit stale checksums:

- **Build failures**: `fail-fast: false` in the matrix means all three arches
  attempt to build, but the consolidate job tracks failures per-arch and
  aborts if any harvest exits non-zero.

- **Harvest failures**: `plasmidbin harvest` exits 1 if any binary fails
  static ELF validation. The consolidate step counts failures across all
  arches and aborts before committing if any occurred.

- **Post-harvest validation**: After committing, a validation step re-reads
  every binary on disk and re-computes BLAKE3 against `checksums.toml`.
  If any mismatch is found, the job fails. This catches races where a
  concurrent push updated `checksums.toml` between harvest and commit.

## Sovereign CI Bridge (Tier 3 — Pre-Stadial)

The current pipeline runs on GitHub Actions. The interstadial exit plan
(H3-02/03/04) includes migrating to sovereign Forgejo CI on ironGate
(`git.primals.eco`).

**Preparation**:
- `sources.toml` will gain a `forge` field per primal pointing to the
  Forgejo mirror. `plasmidbin build` will fall back to Forgejo when
  GitHub clone fails.
- Forgejo Actions runner on biomeGate (GPU access for coralReef/toadStool
  sovereign builds).
- Shadow CI: run both GitHub and Forgejo in parallel, compare checksums,
  cut over when parity is proven.
- NestGate as release artifact store (`content.put` with BLAKE3 provenance)
  replaces GitHub Releases for sovereign distribution.

Cross-arch on Forgejo (single x86_64 machine) will use QEMU or
cross-compilation initially; dedicated aarch64/armv7 runners are a stadial
item.

## References

- [ECOBIN_ARCHITECTURE_STANDARD.md](ECOBIN_ARCHITECTURE_STANDARD.md) — binary compliance
- [GLACIAL_SHIFT_READINESS.md](GLACIAL_SHIFT_READINESS.md) — H3 sovereign CI gates
- `infra/plasmidBin/` — pipeline source code
- `infra/plasmidBin/templates/` — workflow templates for primal repos

---

## FILE: `fossilRecord/wave150s_standards/PURE_RUST_CRYPTO_PURITY_STANDARD.md`

# Pure Rust Crypto Purity Standard

**Status**: ECOSYSTEM STANDARD v1.0  
**Adopted**: Jun 9, 2026  
**Authority**: WateringHole Consensus (BearDog → primalSpring review)  
**Compliance**: Mandatory for primals handling cryptographic operations  
**Reference Implementation**: BearDog v0.9.0 Wave 145  
**Reinforces**: ecoBin Architecture Standard v3.0

---

## Rationale

C-linked crypto libraries (`aws-lc-rs`, `ring`, `openssl`, `boring`) create:
- Cross-compilation blockers (musl, ARM, WASM targets)
- Supply chain audit surface (C code is invisible to `cargo audit`)
- Build toolchain dependencies (`cc`, `cmake`, `bindgen`)
- Platform-specific build failures

The Rust ecosystem now has mature, audited Pure Rust alternatives for every standard cryptographic operation. This standard codifies enforcement.

---

## Standard Declaration

### S1: Zero C-Crypto Dependencies

Every primal that performs cryptographic operations MUST have zero C-linked crypto crates in its resolved dependency graph.

**Verification**:
```bash
cargo deny check bans
# Expected: 0 DENIED entries
```

### S2: `deny.toml` Ban List

Every primal MUST include a `deny.toml` that explicitly bans C-crypto crates. Minimum ban list:

```toml
[[bans.deny]]
wrappers = []
name = "aws-lc-rs"

[[bans.deny]]
wrappers = []
name = "aws-lc-sys"

[[bans.deny]]
wrappers = []
name = "ring"

[[bans.deny]]
wrappers = []
name = "openssl"

[[bans.deny]]
wrappers = []
name = "openssl-sys"

[[bans.deny]]
wrappers = []
name = "boring"

[[bans.deny]]
wrappers = []
name = "boring-sys"

[[bans.deny]]
wrappers = []
name = "native-tls"

[[bans.deny]]
wrappers = []
name = "security-framework-sys"

[[bans.deny]]
wrappers = []
name = "schannel"
```

The full 19-crate ban list is maintained in BearDog's `deny.toml` as the reference.

### S3: Approved Pure Rust Alternatives

| Operation | C Library (BANNED) | Pure Rust Alternative |
|-----------|-------------------|----------------------|
| TLS `CryptoProvider` | `aws-lc-rs`, `ring` | `rustls-rustcrypto` |
| X.509 CSR generation | `rcgen` (when C-linked) | `p256` + `x509-cert` |
| AEAD encryption | `ring::aead` | `aes-gcm`, `chacha20poly1305` |
| Signatures | `ring::signature` | `ed25519-dalek`, `p256`, `p384`, `rsa` |
| Hashing | `ring::digest` | `sha2`, `sha3`, `blake3` |
| Key exchange | `ring::agreement` | `x25519-dalek`, `p256` |
| KDF | `ring::hkdf` | `hkdf`, `pbkdf2`, `argon2`, `scrypt` |
| Random | `ring::rand` | `rand`, `rand_core` (OS-backed) |

### S4: `cc` Crate Exception

The `cc` crate is allowed ONLY as a transitive dependency of `blake3` when blake3 uses its `pure` Rust feature (which disables C assembly). All other `cc` usage must be explicitly justified.

```toml
[[bans.deny]]
wrappers = ["blake3"]
name = "cc"
```

### S5: Build Tool Bans

C build toolchain crates MUST be banned:

```toml
[[bans.deny]]
wrappers = []
name = "bindgen"

[[bans.deny]]
wrappers = []
name = "cmake"
```

---

## Validation Pattern

### CI Gate

Add to CI pipeline:

```bash
cargo deny check bans 2>&1 | grep -c "DENIED"
# MUST be 0
```

### Local Development

```bash
# One-time setup
cargo install cargo-deny

# Validate purity
cargo deny check bans
cargo deny check advisories
cargo deny check licenses
cargo deny check sources
```

### Primal Adoption Checklist

1. Copy ban list from BearDog `deny.toml` to primal's `deny.toml`
2. Run `cargo deny check bans` — fix any violations
3. Replace C-crypto imports with Pure Rust alternatives per S3 table
4. Verify `cargo check` still passes
5. Run full test suite
6. Update primal docs to reflect Pure Rust status

---

## Wider Rust Ecosystem Value

This standard and its reference implementation (BearDog) demonstrate a validated, production-tested path for any Rust project to eliminate C-crypto dependencies. The pattern is:

1. **Declare** — Ban list in `deny.toml` makes the policy machine-readable
2. **Enforce** — `cargo deny check` runs in CI as a gate
3. **Consolidate** — Single canonical wrapper struct for consistent API across the codebase
4. **Verify** — All 4 `cargo deny` checks pass (advisories, bans, licenses, sources)

Projects outside ecoPrimals can adopt this pattern by:
- Using the S3 alternatives table for migration planning
- Copying the `deny.toml` ban list
- Using `rustls-rustcrypto` as their TLS `CryptoProvider`

---

## Ecosystem Adoption Status

| Primal | Status | Notes |
|--------|--------|-------|
| BearDog | COMPLIANT | Reference implementation, Wave 145 |
| Others | PENDING AUDIT | primalSpring to coordinate |

---

## References

- BearDog `deny.toml`: canonical ban list with documented rationale
- ecoBin Architecture Standard v3.0: zero C-dependency mandate
- RustCrypto organization: https://github.com/RustCrypto
- `rustls-rustcrypto`: https://github.com/RustCrypto/rustls-rustcrypto

---

## FILE: `fossilRecord/wave150s_standards/PURE_RUST_SOVEREIGN_STACK_GUIDANCE.md`

# Pure Rust Sovereign Stack — Cross-Primal Guidance

**Date**: May 11, 2026 (updated — ALL 3 GPUs sovereign via warm-catch, pure Rust pipeline)
**Type**: Ecosystem Standard (Evolution)
**From**: barraCuda (Layer 1 complete) + hotSpring (hardware validation) + coralReef (warm-catch)
**To**: coralReef, toadStool, all primals
**Status**: Active — Layers 1-2 done, Layer 3 partial, **Layer 4 ALL 3 GPUs sovereign**

> **March 12 update (hotSpring hardware validation)**: Three DRM bugs fixed
> in coral-driver (`eb4b4eb`). The nouveau sovereign pipeline is now
> **proven on hardware**: VM_INIT → CHANNEL_ALLOC → VM_BIND → GEM alloc →
> upload → readback all pass on both Titan V and RTX 3090. 9/11 hardware
> tests pass. The deprecation path for naga, NVK, and wgpu is now open.
> Root cause: ioctl number off-by-two for CHANNEL_ALLOC (was calling
> GETPARAM instead). See breakthrough handoff for details.
>
> **March 12 update (barraCuda)**: Sovereign GSP Phase 2 complete. 22 chip
> firmware parsed, cross-architecture learning operational. Six wiring gaps
> remain — see `fossilRecord/SOVEREIGN_COMPUTE_TRIO_WIRING_GAPS_HANDOFF_MAR12_2026.md`.

---

## Principle

Math is universal. A shader is just math expressed in a compute language.
The execution substrate — GPU, CPU, NPU, Android ARM core, browser WASM —
is a hardware implementation detail, not a difference in universal algebra.

Three primals each solve their portion of the sovereign compute stack:

| Primal | Solves | Layer |
|--------|--------|-------|
| **barraCuda** | The math — WGSL shaders, naga IR optimisation, precision strategy | 1 |
| **coralReef** | The compiler — SPIR-V/WGSL → native GPU binary (SASS, RDNA ISA) | 2-3 |
| **toadStool** | The hardware — GPU driver, DMA, command submission, device discovery | 3-4 |

Each primal contributes its portion. Together they produce a stable,
sovereign, pure Rust compute stack where hardware is interchangeable
and the math runs forever.

---

## Current Status (March 10, 2026)

### Layer 0 — Infrastructure C Elimination: toadStool COMPLETE

**Zero sysinfo. Zero direct libc.** toadStool S137-S141 eliminated the largest C
surface in any primal by replacing `sysinfo` (15 transitive crates → libc FFI)
with `toadstool-sysmon` — pure Rust `/proc` parsing + `rustix` `statvfs`.

22+ call sites migrated across 18 files. `cargo tree --workspace | grep sysinfo`
returns nothing. Cross-compilation verified: `cargo check --target aarch64-unknown-linux-gnu`
succeeds without musl-tools or any C toolchain.

Remaining libc paths are all ecosystem transitive deps (mio, tokio, wgpu-hal) —
tracked for upstream evolution. toadStool's own code has zero C.

**Pattern**: This follows the same evolution as Ring → RustCrypto (Tower Atomic).
Where bearDog/songBird eliminated C crypto, toadStool eliminated C system monitoring.
The pattern is reusable: any crate pulling libc for `/proc` info can be replaced
with direct parsing.

**Upstream candidate**: `toadstool-sysmon` is being extracted as a standalone
crate for crates.io contribution. See `UPSTREAM_CONTRIBUTIONS.md`.

### Layer 1 — barraCuda: COMPLETE

**Zero `unsafe` blocks.** Zero application C dependencies. `GpuBackend` trait abstraction.

barraCuda achieved this by:
- Evolving SPIR-V passthrough (`unsafe`) to safe WGSL roundtrip via
  naga `wgsl-out`. The sovereign compiler (FMA fusion, dead expression
  elimination) now runs on **all backends** (Vulkan, Metal, DX12, WebGPU).
- Introducing `GpuBackend` trait (`device::backend`) — backend-agnostic compute
  interface. `ComputeDispatch<B: GpuBackend>` is generic over backend (defaults
  to `WgpuDevice`). `CoralReefDevice` scaffold behind `sovereign-dispatch` feature
  flag, ready for `coral-gpu` crate. See `SOVEREIGN_PIPELINE_TRACKER.md`.
- Deferring pipeline caching until wgpu provides a safe creation API.
- Evolving test env manipulation to pure-function testing patterns.
- Evolving all production `expect`/`unwrap` to `Result` propagation.

Transitive C boundaries (wgpu → ash → libvulkan.so, tokio → libc) are
system-level and evolve via Layers 2-4, not Layer 1.

### Layer 2 — coralReef: Phase 10+, Sovereign Compile Parity

coralReef is a sovereign Rust GPU shader compiler. NVIDIA backend (SM35–SM120)
and AMD backend (RDNA2 GFX1030) operational with E2E dispatch verified on
both AMD RX 6950 XT and NVIDIA RTX 3090 (via DRM probing).

> **April 18, 2026 update (hotSpring Exp 176)**: Full HMC pipeline (10 QCD
> shaders) compiles to native SASS on SM35 (Kepler), SM70 (Volta), SM120
> (Blackwell). f64 transcendental lowering fixed for all NVIDIA generations —
> MUFU seed + Newton-Raphson sequences now emit SM-aware ops (IAdd2/OpShl
> for SM32, IAdd3/OpShf for SM70+). QMD v5.0 implemented for Blackwell.
> `compile_ir()` Naga bypass operational. 1,314 coral-reef tests pass.

**Iteration 24 milestone — Hardware Parity & Driver Sovereignty**:
- **Multi-GPU discovery**: `enumerate_render_nodes()` scans all `/dev/dri/renderD*`
  nodes, returns `DrmDeviceInfo` per device. `GpuContext::enumerate_all()` creates
  one context per GPU. Both AMD (amdgpu) and NVIDIA (nvidia-drm, nouveau) detected.
- **Driver sovereignty**: `DriverPreference` type with sovereign default
  (`nouveau` > `amdgpu` > `nvidia-drm`). Compile everything, prefer open-source
  at runtime. Override via `CORALREEF_DRIVER_PREFERENCE` env var.
- **NVIDIA proprietary compatibility**: `NvDrmDevice` probes `nvidia-drm` DRM
  module. Compute dispatch pending UVM integration — probing works, dispatch
  returns explicit "requires UVM" errors (not silent failure).
- **toadStool discovery integration**: `coralreef-core::discovery` reads ecosystem
  capability files (`gpu.dispatch`, `gpu-*`). Falls back to direct DRM scan.
  `GpuContext::from_descriptor()` creates contexts from discovered devices.
- **Cross-vendor parity tests**: Compilation parity for SM86 vs RDNA2. Known
  RDNA2 limitations documented (global_invocation_id, VOP2 VSRC1, buffer reads).
- **Showcase**: *(fossilized)* 8 progressive demos archived — hardware dispatch
  demos moved to toadStool domain. Cross-primal compute triangle now demonstrated
  by barraCuda `showcase/02-cross-primal-compute/` and primalSpring exp050.

**Stack**: 1804 tests (0 failed, 61 ignored), 66.43% line coverage, 75.15% function coverage, 0 DEBT markers.
93 cross-spring WGSL shaders (84 compiling SM70). Three input languages
(WGSL, SPIR-V, GLSL 450). JSON-RPC 2.0 + tarpc (bincode) IPC.
`#[deny(unsafe_code)]` on 8/9 crates. VFIO PFIFO channel + V2 MMU page tables.

### Layer 3 — Standalone Compilation: OPERATIONAL

coralReef compiles WGSL/SPIR-V/GLSL to native GPU binaries as a standalone
primal. `coralreef-core` provides JSON-RPC 2.0 + tarpc servers, capability-based
self-description (`shader.compile`, `shader.health`), and zero-knowledge startup.
UniBin CLI: `server`, `compile`, `doctor`. No dependency on toadStool or barraCuda
for compilation — they are discovered at runtime via capability files.

### Layer 4 — Sovereign Hardware: IN PROGRESS

`coral-driver` provides userspace GPU dispatch via DRM ioctl. AMD amdgpu is
fully wired (GEM, PM4, CS submit, fence sync) with E2E verified. **NVIDIA nouveau
is now hardware-validated** (`eb4b4eb`): VM_INIT, CHANNEL_ALLOC (all 5 variants),
GEM alloc, VM_BIND, upload, readback all pass on both Titan V (GV100) and RTX 3090
(GA102). Three DRM bugs were found and fixed by hotSpring hardware testing:
ioctl number off-by-two for CHANNEL_ALLOC, VA space collision with kernel-managed
region, and broken gem_info query. 9/11 hardware tests pass — remaining 2 are
QMD compute execution tuning (dispatch completes without error, kernel output
needs field alignment). NVIDIA `nvidia-drm` has UVM infrastructure (Iter 36).
All drivers compile by default, selected at runtime via `DriverPreference`.

**Sovereign GSP** (March 12): `coral-driver::gsp` provides a learned GPU
initialization system that parses firmware from 22 NVIDIA chips (Maxwell through
Ampere), builds cross-architecture register transfer maps, and produces dispatch
hints. The system identified that GV100 (Volta) can be initialized using Pascal
(gp10b) firmware patterns at 98.2% register coverage. BAR0 pre-init applicator
is operational (dry-run + verify). FECS channel submission is the remaining gap
for full Volta bring-up.

**nvPmu + hw-learn** (toadStool): BAR0 MMIO access, thermal watchdog, mmiotrace
parser, recipe distiller and store are all operational. The `RegisterAccess` trait
bridge to coral-driver is the remaining integration gap.

**Contrast vs CUDA/Kokkos**: coralReef compiles to the same SASS binary that
CUDA's `ptxas` produces (SM35–SM120), and the same GCN/RDNA binary that AMD's
ROCm compiler produces — but in pure Rust, with no vendor SDK, no C toolchain,
and no runtime library dependency. Where CUDA locks you to NVIDIA and Kokkos
abstracts over vendor SDKs (still requiring CUDA/ROCm/SYCL underneath),
coralReef generates native GPU instructions directly from Rust.

---

## Dependency Evolution Status (March 14, 2026)

### ring Removal
| Primal | Status | Notes |
|--------|--------|-------|
| biomeOS | REMOVED from production | ureq default-features=false, Songbird delegation |
| Songbird | EVOLVED — rustls-rustcrypto default | ring still transitive via quinn (QUIC) |
| BearDog | USES ring via rustls/quinn | BearDog is the crypto provider; ring here is acceptable |
| rhizoCrypt | FEATURE-GATED | Only via http-clients feature (not default) |
| loamSpine | FEATURE-GATED | Only via discovery-http feature (not default) |
| sweetGrass | DEV-DEPS ONLY | testcontainers → ring (not in production) |
| Squirrel | NEEDS EVOLUTION | sqlx → rustls → ring |

### sled → redb Evolution
| Primal | Status | Notes |
|--------|--------|-------|
| rhizoCrypt | DONE | redb default since v0.12 |
| LoamSpine | DONE | redb default, sled optional (sled-storage feature) |
| sweetGrass | DONE | redb default, sled **eliminated** (crate archived, zero lockfile entries) |
| biomeOS | DONE | biomeos-graph migrated to redb |
| Songbird | PENDING | sled in orchestrator, tor-protocol, sovereign-onion |
| BearDog | PENDING | sled in workspace |

### NestGate Unsafe Evolution
- 6 unsafe blocks replaced with safe alternatives (zero_cost_evolution, safe_ring_buffer, async_optimization)
- 8 unsafe blocks kept with SAFETY justification (lock-free data structures, FFI, SIMD)
- pin-project adopted for safe async pin projection

### Production Mock Isolation
- rhizoCrypt mocks behind `#[cfg(test)]` / testing feature
- Squirrel mocks isolated to testing modules

---

## coralReef — Layer 2 Evolution Guidance

### Eliminating the 2 Remaining Unsafe Blocks

The `nak-ir-proc` derive macro generates `AsSlice<Src>` and `AsSlice<Dst>`
implementations for instruction op structs. For multi-field structs, it uses
`unsafe { std::slice::from_raw_parts }` on `#[repr(C)]` fields after
compile-time contiguity proofs via `offset_of!`.

**Recommended safe evolution paths** (in order of preference):

#### Option A: Array-field pattern (cleanest)
Change the generated struct to store matched fields in a `[Src; N]` array
with named accessor methods. The proc macro generates:

```rust
#[repr(C)]
struct OpFoo {
    srcs: [Src; 3],  // was: src0, src1, src2
    flags: u32,
}

impl OpFoo {
    fn src0(&self) -> &Src { &self.srcs[0] }
    fn src1(&self) -> &Src { &self.srcs[1] }
    fn src2(&self) -> &Src { &self.srcs[2] }
}

impl AsSlice<Src> for OpFoo {
    fn as_slice(&self) -> &[Src] { &self.srcs }        // safe
    fn as_mut_slice(&mut self) -> &mut [Src] { &mut self.srcs }  // safe
}
```

This is the deepest evolution — it changes the struct layout but
eliminates unsafe entirely. Named accessors preserve the field-name API.

#### Option B: bytemuck safe cast
If `Src` and `Dst` implement `Pod` (or `NoUninit` + `AnyBitPattern`),
use `bytemuck` for safe reinterpretation:

```rust
// Given contiguity is proven by const assertions:
let bytes = bytemuck::bytes_of(&self.src0);  // or bytes_of_mut
// Safe cast to &[Src; N] if layout is proven
```

Requires `Src`/`Dst` to be `Pod`-compatible. Less invasive than Option A.

#### Option C: Copy-based fallback
Generate code that copies fields into a stack array:

```rust
fn as_slice(&self) -> [Src; 3] {  // returns owned array, not slice
    [self.src0, self.src1, self.src2]
}
```

Simplest but changes the return type from `&[Src]` to `[Src; N]`.
Acceptable if Src/Dst are small and Copy.

### coralReef Layer 2 — Remaining Work

| Item | Status | Notes |
|------|--------|-------|
| `nak-ir-proc` unsafe → safe | Remaining | Options A/B/C above |
| f64 transcendental codegen (DFMA sequences) | Done (Phase 10) | NVIDIA + AMD |
| SM70–SM89 instruction scheduling | Done | ISA tables complete |
| AMD RDNA2 E2E dispatch | Done | GFX1030, PM4, DRM ioctl verified |
| df64 preamble auto-prepend | Done (Iteration 13) | `Fp64Strategy::DoubleFloat` |
| IR-level df64 lowering (Phase 2) | Planned | `lower_f64_to_df64.rs` pass |
| Upstream Mesa NAK contribution | Planned | Goodwill + wider testing |

---

## coralReef — Layer 3 Evolution Guidance

Layer 3 makes coralReef a standalone Rust crate, independent of Mesa's
build system, with a clean public API.

### Target Architecture

```
barraCuda WGSL
  → naga IR (pure Rust, we use upstream or fork)
    → coralReef compile(spirv, target_arch) → native binary
      Targets:
        NVIDIA: SM35 (Kepler), SM70 (Volta), SM75 (Turing), SM80/86 (Ampere), SM89 (Ada), SM120 (Blackwell)
        AMD: GFX10 (RDNA1), GFX10.3 (RDNA2), GFX11 (RDNA3)  [future]
        Intel: Xe (DG2)  [future]
```

### Concrete Tasks

1. **Standalone crate**: `coral-reef` as a `cargo add` dependency with
   no Mesa C build system, no cmake, no meson. Pure `cargo build`.

2. **Clean public API**:
   ```rust
   pub fn compile(spirv: &[u32], target: GpuArch) -> Result<Vec<u8>, CompileError>
   pub fn compile_wgsl(wgsl: &str, target: GpuArch) -> Result<Vec<u8>, CompileError>
   ```

3. **Direct naga → coralReef path**: Accept `naga::Module` directly,
   skip SPIR-V serialization/deserialization. barraCuda's sovereign compiler
   produces naga IR — coralReef can consume it directly.

4. **Multi-vendor ISA**: Factor the backend so NVIDIA, AMD, and Intel
   targets share the common IR → scheduling → encoding pipeline.

5. **Feature-gated in barraCuda**: Optional `sovereign-compiler` feature
   flag in barraCuda's `Cargo.toml` enables in-process compilation
   (no IPC round-trip). IPC path remains the default for decoupled
   deployment.

### coralReef Layer 3 — What This Enables

- barraCuda compiles shaders to native GPU binaries without Vulkan
- Compile server: coralReef runs on a separate machine, barraCuda
  discovers it via capability scan
- CI integration: compile and cache native binaries in CI, ship
  pre-compiled shaders with the application
- Cross-compilation: compile on x86 for ARM GPU targets (Android)

---

## toadStool — Layer 3-4 Evolution Guidance

toadStool owns the hardware abstraction and runtime. Its sovereign
evolution replaces the Vulkan loader and GPU driver with pure Rust.

### Layer 3: Minimal Vulkan-compatible Dispatch

Replace `ash` (Vulkan FFI bindings) with a minimal Rust-native dispatch
layer that talks directly to the GPU driver (or coralDriver).

| Task | Description |
|------|-------------|
| Compute-only Vulkan subset | Only implement VkQueue, VkCommandBuffer, VkBuffer, VkShaderModule for compute |
| Skip validation layers | Production compute doesn't need Vulkan validation overhead |
| Feature-gate in wgpu | toadStool could provide a wgpu backend that uses coralDriver instead of Vulkan |

### Layer 4: Sovereign GPU Driver (coralDriver) — ALL 3 GPUs SOVEREIGN (May 2026)

> **May 11, 2026 update**: ALL 3 local GPUs (RTX 5060 SM120, Titan V SM70,
> Tesla K80 SM37) are now sovereign via warm-catch pipeline. VFIO dispatch
> infrastructure implemented (`VfioChannel::create_warm`). Hardware E2E tests
> exist (`vfio_warm_write_42_readback`). The dispatch *gap* is now wiring
> (shader compile → sovereign dispatch → readback on warm GPUs), not hardware
> bring-up. Pure Rust `coralctl warm-catch` CLI replaces shell scripts.

The evolution from "replace NVK/RADV" to "sovereign hardware across 3 GPU
generations" is now complete at the hardware level:

| Component | Status | Notes |
|-----------|--------|-------|
| **coralDriver** | Operational | SM35/SM70/SM120 dispatch, DRM + VFIO backends, ELF patcher |
| **coralMem** | Operational | Buffer create/map/copy across all 3 GPUs |
| **coralQueue** | Operational | GPFIFO/pushbuf submission, semaphore fence |
| **vfio backend** | Proven | RTX 5060 full dispatch, warm-catch on Titan V + K80 |
| **warm-catch** | Pure Rust | ELF patcher + ember orchestrator + `coralctl warm-catch` CLI |

### What's Sovereign vs What's Still External (May 2026)

**Sovereign (we own, pure Rust):**

| Component | Status |
|-----------|--------|
| coral-reef SASS encoders (SM35/SM70/SM120) | Operational, 1314+ tests |
| coral-reef AMD GFX10/GFX11/GFX9 encoders | Operational |
| coral-driver DRM/VFIO dispatch | Operational, hardware-proven |
| ELF patcher (kernel module binary patching) | Operational, `object` crate |
| Warm-catch pipeline (orchestrator + CLI) | Operational, pure Rust |
| AMD PM4 dispatch path | Operational |
| coral-ember lifecycle + coral-glowplug fleet | Production-grade, 664+ tests |

**Still external (not yet sovereign):**

| Dependency | Owner | Path to Sovereignty |
|------------|-------|---------------------|
| naga (WGSL parser) | Mozilla / gfx-rs | Separate coral team owns IR-to-IR stability validation loop. Local team does not own. |
| wgpu (GPU compute in barracuda/toadStool) | gfx-rs | toadStool team evolves; `sovereign-dispatch` feature bypasses wgpu. |
| PTX for SM120 (requires `ptxas`) | NVIDIA | coralReef compiler team building native SM120 SASS encoder to eliminate. |
| cudarc (optional feature) | Rust CUDA community | Removed after sovereign dispatch is default path. |
| ~~`coral-kmod` C kernel modules~~ | ~~coralReef~~ | **FOSSILIZED S276** — RM ABI absorbed into `toadstool_cylinder::nv::rm_abi` (22 repr(C) structs). C sources archived to `fossilRecord/primals/coralReef/coral-kmod/`. |

**Upstream-owned evolution (not local team responsibility):**

| Work | Owner Team |
|------|-----------|
| naga WGSL parser evolution, IR-to-IR stability | coral naga team |
| wgpu elimination from default path | toadStool team |
| coral-ember/glowplug absorption into toadStool | toadStool team |
| coral-driver hardware access absorption into toadStool | toadStool team |
| SM120 native SASS encoder (replacing PTX emitter) | coralReef compiler team |
| ~~`coral-kmod` C → Rust evolution~~ | ~~coralReef kernel team~~ | **DONE S276** — absorbed into `nv/rm_abi.rs`, fossilized |

### toadStool Layer 4 — What This Enables

- **Hardware sovereignty**: GPUs usable indefinitely, regardless of vendor
  driver support lifecycle (Titan V, older Quadros, deprecated AMD cards)
- **No C FFI in compute path**: coralDriver talks to hardware via ioctl
  or vfio-pci, both accessible from Rust
- **Potentially faster**: No Vulkan state machine overhead for compute-only
  workloads; direct dispatch from Rust futures
- **Android / embedded**: Sovereign driver runs on any Linux-based system
  including Android with vfio or kernel module

---

## Cross-Primal Evolution Cycle

```
Springs (hotSpring, wetSpring, airSpring, neuralSpring, groundSpring)
  │ find gaps, validate physics, benchmark against Kokkos/LAMMPS
  │ contribute domain-specific shaders + driver edge cases
  ▼
barraCuda (Layer 1 — DONE)
  │ WGSL shaders, naga IR optimisation, precision strategy
  │ Zero unsafe, zero C deps — the math layer is pure Rust today
  ▼
coralReef (Layers 2-3 — IN PROGRESS)
  │ SPIR-V/WGSL → native GPU binary (SASS, RDNA ISA)
  │ 9 unsafe (driver RAII + proc-macro), #[deny(unsafe_code)] on 6/8 crates
  │ Pure Rust compiler, no GPU FFI
  ▼
toadStool (Layers 3-4 — PLANNED)
  │ Hardware discovery, GPU driver, DMA, command submission
  │ Vulkan FFI → coralDriver (pure Rust)
  ▼
Springs ← absorb improved performance, validate again
```

Each primal ingests, evolves, and hands back. The physics never changes.
Only the infrastructure evolves. The cycle accelerates because every
improvement in one primal benefits all consumers.

---

## Contract Between Primals

### barraCuda guarantees to coralReef:
- WGSL shaders that parse correctly with naga
- `naga::Module` available via the sovereign compiler API for direct
  consumption (no SPIR-V serialization required)
- Precision strategy metadata (target arch, f64 rate, DF64 preference)
  available via IPC capability discovery

### coralReef guarantees to barraCuda:
- JSON-RPC 2.0 + tarpc IPC interface for shader compilation
- `compiler.compile(spirv, target_arch) → native_binary` endpoint
- Capability advertisement: `compiler.capabilities() → {architectures, features}`
- No dependency on barraCuda — coralReef is a standalone compiler

### toadStool guarantees to both:
- Hardware discovery and capability enumeration
- Device management (multi-GPU, NPU, thermal monitoring)
- Runtime transport: Unix socket, TCP, or in-process (feature-gated)
- No dependency on shader content — toadStool routes, doesn't compute

### All primals guarantee to each other:
- Primal autonomy: no shared IPC crate, no hardcoded primal names
- Capability-based discovery at runtime
- JSON-RPC 2.0 as primary protocol, tarpc (bincode) as high-performance binary channel
- AGPL-3.0 license
- Zero hardcoded ports, addresses, or primal identifiers

---

## Timeline Estimates

| Layer | Owner | Estimated Time | Risk | Depends On |
|:---:|---|---|---|---|
| 1 | barraCuda | **DONE** | — | — |
| 2 | coralReef | **DONE** — NVIDIA SM35-SM120 (Kepler→Blackwell), AMD RDNA2, 1314+ coral-reef tests, VFIO PFIFO + V2 MMU + QMD v5.0 | — | — |
| 3 | coralReef + barraCuda | **Partial** — coral-gpu API exists; `dispatch_binary` wiring needed | Low | — |
| 4 | coralReef + toadStool | **ALL 3 GPUs sovereign** — AMD done, nouveau done, warm-catch proven. Remaining: dispatch validation on warm GPUs, toadStool absorption of coral-driver hardware layer. | Low | Layer 3 |

The key accelerator: we are not writing from scratch. NAK is already Rust.
NVK has clear Rust-accessible patterns. The AI-dev loop (springs find gaps →
primals fix → springs validate) accelerates each layer.

---

## Validation Invariant

The same physics validates every layer:

| Test Suite | Validates |
|------------|-----------|
| hotSpring 9-case Yukawa OCP | Energy conservation, force accuracy |
| wetSpring 1,247 marine bio tests | Statistical correctness, FHE accuracy |
| neuralSpring 218/218 validate_all | ML op correctness, attention precision |
| groundSpring 85 delegations | Hydrology, ET₀, soil physics |
| airSpring 53 cross-spring benchmarks | Seasonal pipeline, kriging |

The physics doesn't change. The math is validated at every level.
Only the infrastructure evolves.

---

## Dual-Use Vision

The sovereign stack enables **dual-use hardware**: nvidia drivers for gaming,
VFIO for science, on the same machine, no reboot. toadStool manages the
GPU mode switch. See `SOVEREIGN_COMPUTE_EVOLUTION.md` and
`fossilRecord/SOVEREIGN_COMPUTE_BAR0_BREAKTHROUGH_DUAL_USE_HANDOFF_MAR12_2026.md`.

---

*The shaders are the mathematics. The driver is plumbing.*
*barraCuda owns the mathematics. coralReef evolves the compiler.*
*toadStool evolves the hardware. Together: sovereign compute.*

---

## FILE: `fossilRecord/wave150s_standards/README.md`

# Fossilized Standards — Wave 150s

Standards moved here are tied to fossilized dimensions or superseded by
newer mechanisms. They remain valid references but are no longer actively
maintained at the top level.

| Standard | Reason |
|----------|--------|
| `GLACIAL_SHIFT_READINESS.md` | Glacial Shift dimension fossilized (150p, completed 137b) |
| `PURE_RUST_CRYPTO_PURITY_STANDARD.md` | Silicon Atheism dimension fossilized (150p, completed 145a) |
| `PURE_RUST_SOVEREIGN_STACK_GUIDANCE.md` | Silicon Atheism dimension fossilized (150p, completed 145a) |
| `PLASMIDBIN_PUSH_AUTOMATION_STANDARD.md` | Depot/Build dimension fossilized (150p, completed 150n) |
| `WATERFALL_PATTERN.md` | Cascade Pipeline dimension fossilized (150p, completed 150k) |
| `DESKTOP_NUCLEUS_DEPLOYMENT.md` | Superseded by USB bootstrap + gate.enroll (150n) |
| `ECOBIN_ARCHITECTURE_STANDARD.md` | Architecture stable since v3.0 (Jan 2026) |
| `WORKSPACE_DEPENDENCY_STANDARD.md` | Superseded by ecosystem_manifest.toml |

---

## FILE: `fossilRecord/wave150s_standards/WATERFALL_PATTERN.md`

# WaterFall Pattern — Sovereign Gate Sync

**Pattern class**: firstLast coordination (biomeOS neuralAPI)
**Lineage**: Parallels **RootPulse** — both are distributed coordination patterns.
RootPulse coordinates primals for single-repo version control within a
cytoplasm; WaterFall coordinates membranes for multi-repo ecosystem sync
across envelope layers.

**Status**: Phase 1–4 implemented. Phase 4 inversion LIVE (Wave 63+).
Gates push to Forgejo only; K-Derm diderm relay chain propagates to GitHub
via peptidoglycan → golgiBody-ext with proper bond-type degradation.
Phase 5 specified (gate specialization + covalent routing).
**Wave 65**: `temporal.cascade` fully Rust (replaces bash `cascade-pull.sh`),
`plasmid.fetch` fully Rust (replaces bash `fetch_primals.sh`), manifest-driven
gate discovery (no hardcoded gate lists), dynamic validation.

## K-Derm Topology

The diderm cell envelope model from `cellMembrane` provides the
architectural framing. Each layer maps to an ecosystem component:

| K-Derm Layer        | Ecosystem Component                        | Role in WaterFall                                |
|---------------------|--------------------------------------------|--------------------------------------------------|
| **Cytoplasm**       | Gate NUCLEUS workspace                     | Local evolution — repos evolve independently     |
| **Plasma membrane** | Gate firewall + SSH keys                   | Covalent boundary — SSH auth to periplasm        |
| **Periplasm**       | Forgejo on VPS — golgiBody (`git.primals.eco`) | WaterFall mediator — distributes pulls, receives pushes |
| **Outer membrane**  | VPS channels (Caddy, sporePrint, TURN)     | Service surface — lab.primals.eco, membrane.primals.eco |
| **Extracellular**   | GitHub                                     | Trailing mirror — outer-world CI and discovery   |

The **peptidoglycan layer** (Caddy TLS surface + static lab) sits between
the outer membrane and periplasm, providing structural rigidity — this is
now live at `lab.primals.eco`.

## Flow

```
                    ┌──────────────────────────────────┐
                    │        Extracellular (GitHub)     │
                    │   trailing mirror (weak bond)     │
                    └──────────────┬───────────────────┘
                                   │ weak (membrane relay.ship)
                    ┌──────────────┴───────────────────┐
                    │  Outer Membrane (VPS channels)    │
                    │  lab.primals.eco, sporePrint       │
                    └──────────────┬───────────────────┘
                                   │ webhook
                    ┌──────────────┴───────────────────┐
                    │   Periplasm (Forgejo)             │
                    │   git.primals.eco                 │
                    │   38 repos, waterfall source      │
                    └───┬───────┬───────┬──────────────┘
                        │       │       │
          ┌─────────────┘       │       └──────────────┐
          ▼                     ▼                      ▼
    ┌───────────┐       ┌───────────┐          ┌───────────┐
    │ eastGate  │       │ southGate │          │ biomeGate │
    │ cytoplasm │       │ cytoplasm │          │ cytoplasm │
    └───────────┘       └───────────┘          └───────────┘

    ─── waterfall down: membrane temporal.cascade ───▶
    ◀── evolution up:   git push forgejo ──────────────
```

### Waterfall Down (pull)

Gates invoke `membrane temporal.cascade`. The Rust binary:

1. Reads `ecosystem_manifest.toml` for gate profile, sync config, and Forgejo SSH URL
2. For each repo in the gate's manifest, selects the temporal leader remote
3. Executes `git pull --ff-only <remote>` concurrently across repos
4. Reports per-repo status (OK, SKIP, FAIL) with timing

**Historical note**: `cascade-pull.sh` (1,029 lines) was the bash predecessor.
It was fossilized in Wave 66 (June 2026). All gates now use `membrane temporal.cascade`.

### Evolution Up (push)

Individual repos push to Forgejo after local development:

```bash
git push forgejo main
```

Forgejo post-receive hooks then:
- Push to GitHub as a trailing mirror (extracellular)
- Trigger sporePrint webhook refresh (outer membrane)

## Configuration

### ecosystem_manifest.toml

```toml
[sync]
forgejo_base_url = "https://git.primals.eco"
forgejo_ssh = "ssh://git@git.primals.eco:2222"
forgejo_host = "golgiBody"
default_source = "temporal"
default_branch = "main"
push_to_followers = true
push_target = "forgejo"       # Phase 4 inversion: gates push to Forgejo only

[repos.primalSpring]
# ... existing fields ...
forgejo_repo = "syntheticChemistry/primalSpring"
```

**`push_target`**: Controls where temporal sync pushes. `"forgejo"` means gates
push only to the Forgejo remote (golgiBody-inner, cis face). The K-Derm diderm
relay chain propagates to GitHub through peptidoglycan → golgiBody-ext.
Set to `"all"` for legacy dual-push behavior (bypasses K-Derm layers).

### Gate-level override

```bash
# ~/.config/cascade-pull.env (or environment variable)
CASCADE_SYNC_SOURCE=forgejo
```

### membrane temporal.cascade flags

| Flag                  | Description                                      |
|-----------------------|--------------------------------------------------|
| `--gate auto`         | Auto-detect gate identity from `.gate` file      |
| `--gate <name>`       | Specify gate explicitly                          |
| `--source temporal`   | Use temporal leader (default)                    |
| `--check`             | Dry-run: report status without pulling           |
| `--clone-missing`     | Clone repos not yet present on this gate         |

## Inversion Protocol (Phase 3–4)

The inversion flips Forgejo from trailing mirror to primary source.

### Phase 3: Shadow Period (dual-source validation)

1. Run `membrane temporal.cascade --check` alongside normal pulls
2. Compare HEADs from both remotes for parity
3. Track parity for 7+ days (matching membrane telemetry cutover gate)
4. Extend `s_ecosystem_freshness` or add `s_ecosystem_forgejo_parity`
   to validate in CI

### Phase 4: Inversion — LIVE (Wave 63+)

1. `[sync].push_target = "forgejo"` in manifest — gates push to Forgejo only
2. `[sync].default_source = "temporal"` — pull from whichever remote leads
3. K-Derm diderm relay chain wired with proper bond-type degradation:
   - Gate → golgiBody-inner (covalent: Forgejo receives)
   - golgiBody-inner → peptidoglycan (metallic: `pepti-sync-relay.sh` syncs)
   - peptidoglycan → golgiBody-ext (ionic: relay to outer membrane)
   - golgiBody-ext → GitHub (weak: `ext-github-push.sh` ships extracellularly)
4. GitHub SSH write credentials live only on golgiBody-ext (trans/shipping face)
5. GitHub becomes the external linear ledger (analogous to loamSpine → BTC/ETH)
6. `topology.roles` in manifest declares per-layer function assignments
7. Impulse cascade runs on peptidoglycan during relay

**Implementation files**:
- `hooks/forgejo/pepti-sync-relay.sh` — peptidoglycan metallic→ionic relay
- `hooks/forgejo/ext-github-push.sh` — golgiBody-ext trans face GitHub push
- `hooks/forgejo/impulse-relay-hook.sh` — standalone impulse detection
- `graphs/waterfall_publish.toml` — full cascade graph specification

**K-Derm diderm relay** (Wave 63+): Proper bond-type degradation wired.
`pepti-sync-relay.sh` on peptidoglycan mediates between inner and outer.
`ext-github-push.sh` on golgiBody-ext (trans face) pushes to GitHub.
Flow: inner (covalent) → peptidoglycan (metallic) → golgiBody-ext (ionic) → GitHub (weak).
GitHub SSH write credentials live only on golgiBody-ext (outer membrane).
See `hooks/forgejo/README.md` for relay chain setup.

### Rollback

If Forgejo becomes unavailable during shadow period or after inversion:
```bash
cascade-pull --source github    # explicit fallback
```

## Phase 5: Multi-Biome / Multi-Membrane — Gate Specialization

Once gates pull from Forgejo and push back to it, WaterFall becomes a
full biomeOS coordination pattern with covalent routing.

### Gate-Spring Ownership

Each gate owns specific science domains and pulls only what it needs.
The canonical SSOT is `GATE_SPRING_OWNERSHIP.md`.

| Gate | Domain | Springs | Sync Profile |
|------|--------|---------|-------------|
| **eastGate** | Coordination hub | primalSpring, airSpring, groundSpring | Full superset (38 repos) |
| **ironGate** | Clinical, game science | healthSpring, ludoSpring | Core + health/ludo + esotericWebb |
| **southGate** | Biology, ML inference | wetSpring, neuralSpring | Core + wet/neural |
| **biomeGate** | GPU compute | hotSpring | Core + hotSpring |
| **strandGate** | ABG science, genomics | hotSpring, wetSpring | Core + ABG gardens + lithoSpore |
| **golgiBody** | Periplasmic relay | — | NUCLEUS primals + deployment infra |

### Gate Auto-Detection

`membrane temporal.cascade` resolves the current gate identity:

1. `GATE_NAME` environment variable (explicit override)
2. Hostname detection (`hostname -s` mapped to gate name)
3. Falls back to pulling all repos if unresolved

This makes per-gate sync the default operational mode. Gates pull only
their assigned repos, reducing bandwidth and avoiding conflicts in
repos they don't own.

### Cross-Gate Compute Routing

hotSpring operates on both strandGate (ABG science validation) and
biomeGate (GPU-accelerated physics). The science evolves on strandGate;
heavy compute dispatches to biomeGate via Songbird mesh. This is the
first cross-gate covalent bond — work flows between gates through the
periplasm rather than through manual coordination.

### Covalent Evolution Path

```
Ad-hoc routing (Wave 55-59)
    Handoff blurbs coordinate gate work manually.
    ↓
Documented ownership (Wave 60) — THIS PHASE
    GATE_SPRING_OWNERSHIP.md + manifest [gates.*] profiles.
    cascade-pull --gate auto syncs per-gate repos.
    ↓
Songbird mesh discovery (Wave 62+)
    Gates advertise capabilities via Songbird primitives.
    Cross-gate dispatch replaces manual blurbs.
    ↓
toadStool covalent dispatch (Wave 63+)
    Compute jobs route to best-fit gate hardware.
    hotSpring GPU work auto-dispatches to biomeGate.
    ↓
biomeOS graph.execute (Wave 65+)
    WaterFall becomes a TOML-defined neuralAPI pattern.
    Routing via biomeOS engine instead of shell scripts.
    Parallels RootPulse coordination of primals.
```

### Infrastructure Patterns

- **VPS cascade profile**: golgiBody gets its own cascade-pull profile
  (periplasm-local NUCLEUS repos only — no springs)
- **New gate bootstrap**: Clone from Forgejo, install cascade-pull timer,
  done — K-Derm endosymbiosis (Phase 1 weak → Phase 4 covalent)
- **Nested diderm**: A lab's outer membrane is the campus periplasm;
  WaterFall flows through each envelope independently
- **neuralAPI elevation**: WaterFall becomes a TOML-defined neuralAPI
  pattern in biomeOS, routing via the biomeOS engine instead of shell
  scripts — just as RootPulse coordinates rhizoCrypt + loamSpine +
  NestGate + sweetGrass

## Key Files

| File | Role |
|------|------|
| `infra/wateringHole/ecosystem_manifest.toml` | Repo catalog + `[sync]` config |
| `cellMembrane/crates/membrane-shadow/src/temporal.rs` | Rust WaterFall engine (`membrane temporal.cascade`) |
| `cellMembrane/crates/membrane-shadow/src/relay.rs` | K-Derm relay chain (`relay.run`, `relay.mediate`, `relay.ship`) |
| `infra/wateringHole/freshness.toml` | Wave state snapshot |
| `gardens/projectNUCLEUS/deploy/forgejo_mirror.sh` | Forgejo repo provisioning |
| `springs/primalSpring/ecoPrimal/.../s_ecosystem_freshness.rs` | Manifest + sync validation |

## History

- **Wave 66** (2026-06-01): wateringHole at zero code. All bash scripts
  fossilized. `membrane temporal.cascade` fully Rust, manifest-driven.
  K-Derm relay chain evolved to `relay.rs` (relay.run/mediate/ship).
  S1 TLS shadow PASSED (13 days). MESH_DEPLOYMENT_STANDARD.md added.
- **Wave 63+** (2026-05-31): Phase 4 inversion LIVE. `push_target = "forgejo"`
  in manifest. K-Derm diderm relay chain wired: golgi-post-receive-relay on
  golgiBody triggers pepti-sync-relay on peptidoglycan, which triggers
  ext-github-push on golgiBody-ext (trans face). `topology.roles` added.
  GitHub SSH write credentials moved exclusively to golgiBody-ext.
  Bonding violation resolved: proper covalent→metallic→ionic→weak degradation.
- **Wave 60** (2026-05-28): Phase 1–2 implemented. Manifest v2.0.0 with
  `[sync]` section and `forgejo_repo` fields. `cascade-pull.sh` evolved
  with `--source` and `--ensure-remotes` (now fossilized — replaced by
  `membrane temporal.cascade`). All eastGate repos configured with
  `forgejo` remote.

---

## FILE: `fossilRecord/wave150s_standards/WORKSPACE_DEPENDENCY_STANDARD.md`

# Workspace Dependency Management Standard

**Status**: Active  
**Adopted**: March 30, 2026  
**Authority**: WateringHole Consensus  
**Compliance**: Mandatory for all Rust workspace primals  
**Reference Implementation**: coralReef (March 30, 2026)

---

## Core Principle

**All shared dependency versions live in the workspace root `Cargo.toml`.**

Crate-level `Cargo.toml` files reference them with `{ workspace = true }` and
may add crate-specific features. Per-crate inline version pins are forbidden
for any dependency used by more than one workspace member.

---

## Why

### Single source of truth

When `naga = "28"` appears in four crates, a version bump touches four files
and risks version skew if one is missed. A workspace dependency ensures one
edit, zero drift.

### Faster compilation

Cargo unifies identical dependency versions into a single build unit. Inline
pins that accidentally drift (e.g. `1.1` vs `1.1.4`) produce duplicate
compilations of the same crate with different semver resolutions.

### Cleaner audit

`cargo deny` / `cargo tree` produce cleaner output when every workspace member
resolves to the same version. Duplicate advisories vanish.

### Visible dependency matrix

The workspace `[workspace.dependencies]` section is a single manifest of
everything the primal depends on — a readable compilation and security matrix.

---

## Rules

### 1. Declare in workspace root

Every external dependency used by any member crate **must** appear in
`[workspace.dependencies]` in the root `Cargo.toml`.

```toml
# root Cargo.toml
[workspace.dependencies]
naga = { version = "28", features = ["wgsl-in"] }
```

### 2. Reference from crates

Member crates reference the workspace declaration and may **add** features
(never versions).

```toml
# crates/coral-reef/Cargo.toml
[dependencies]
naga = { workspace = true, features = ["spv-in", "spv-out", "glsl-in"] }
```

Workspace features and crate-level features are merged by Cargo.

### 3. Internal path crates follow the same pattern

Path dependencies within the workspace also belong in
`[workspace.dependencies]` so that member crates use `{ workspace = true }`
consistently.

```toml
# root Cargo.toml
[workspace.dependencies]
coral-driver = { path = "crates/coral-driver" }

# crates/coralreef-core/Cargo.toml
[dependencies]
coral-driver = { workspace = true }
```

Feature activation on path crates uses the same additive pattern:

```toml
coral-driver = { workspace = true, features = ["vfio"] }
```

### 4. Dev-dependencies follow the same rules

Test-only crates (`tempfile`, `criterion`, `trybuild`, etc.) are declared in
`[workspace.dependencies]` and referenced with `{ workspace = true }` in each
crate's `[dev-dependencies]` section.

### 5. Proc-macro crates are not exempt

Proc-macro crates (`syn`, `quote`, `proc-macro2`) follow the same workspace
pattern. Even if only one crate uses them today, centralizing prevents
accidental version drift when a second proc-macro is added.

### 6. Optional/feature-gated dependencies

Optional dependencies are declared normally in the workspace root. The
`optional = true` flag is set at the crate level, not the workspace level.

```toml
# root Cargo.toml
[workspace.dependencies]
cudarc = { version = "0.19", features = ["driver", "cuda-12060"] }

# crates/coral-driver/Cargo.toml
[dependencies]
cudarc = { workspace = true, optional = true }
```

### 7. Version bumps are atomic

When upgrading a dependency, change the version in the workspace root and run
`cargo update -p <crate>`. All members pick up the new version simultaneously.

---

## Exceptions

**Standalone codegen tools** (e.g. `amd-isa-gen`) that are workspace members
for convenience but share zero dependencies with the main crate graph may keep
inline versions for tool-specific crates (e.g. `quick-xml`, `anyhow`) that
would pollute the workspace dependency list. They **should** still use workspace
declarations for any dependency also used by the main crate graph (e.g. `serde`,
`tempfile`).

---

## Validation

```bash
# After consolidation, verify no duplicate versions:
cargo tree --duplicates
# Expected: empty or ecosystem-caused only (not our inline pins)

# Verify clean build:
cargo check --workspace --all-features
cargo clippy --workspace --all-features -- -D warnings
cargo test --workspace
```

---

## Compliance Checklist

- [ ] Every dependency version appears **exactly once** in the root `Cargo.toml`
- [ ] Every member crate uses `{ workspace = true }` for shared dependencies
- [ ] Feature additions at the crate level use `{ workspace = true, features = [...] }`
- [ ] `cargo tree --duplicates` shows no self-inflicted duplicates
- [ ] Version bumps touch only the root `Cargo.toml`

---

## Relationship to ecoBin

Workspace dependency management is a **build hygiene prerequisite** for ecoBin
compliance. A primal cannot reliably prove "zero C dependencies" or pass the
cross-compilation matrix if version skew between members allows a C-linked
version to slip in through one crate while a pure-Rust version is declared in
another.

Centralizing dependencies makes the ecoBin audit command (`cargo tree | grep
-E "(openssl-sys|ring|...)"`) authoritative — if a C crate isn't in the
workspace root, it cannot enter any member.

---

**Standard**: Workspace Dependency Management v1.0.0  
**Adopted**: March 30, 2026  
**Authority**: WateringHole Consensus  
**Status**: Active

---

## FILE: `foundations/BONDING_MODEL_STANDARD.md`

<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Bonding Model Standard — Organo-Metallo-Salt Model for Ecosystem Interactions

**Version**: 1.0.0
**Date**: May 26, 2026
**Status**: Active
**Authority**: wateringHole Consensus
**Related**: `K_DERM_TOPOLOGY_STANDARD.md`, `BTSP_PROTOCOL_STANDARD.md`, `SOVEREIGNTY_STANDARDS.md`, `GATE_SPRING_OWNERSHIP.md`
**Typed implementation**: `gardens/cellMembrane/crates/cellmembrane-types/src/envelope.rs` (`BondType`)
**Canonical bonding spec**: `primals/biomeOS/specs/NUCLEUS_BONDING_MODEL.md`

---

## Purpose

This document unifies the organo-metallo-salt bonding model — the five
bond types that govern all interactions between primals, gates, VPS
nodes, external services, and cross-family partnerships. The bonding
model determines what crosses each K-Derm envelope layer boundary,
which BTSP cipher suite is enforced, and how braid (provenance) is
handled at each transition.

---

## The Five Bond Types

Ordered by trust level (highest first):

### 1. Covalent — Shared Family, Full Trust

| Property | Value |
|----------|-------|
| **Trust model** | GeneticLineage (Nuclear tier) |
| **What it means** | Same family seed, same administrative domain, full capability access |
| **BTSP cipher** | `BTSP_NULL` minimum (all three ciphers allowed) |
| **K-Derm layer** | Cytoplasm, Plasma membrane |
| **Channel protein** | Aquaporin (always open) |
| **Braid policy** | Pass-through (no inspection) |
| **Genetics requirement** | Nuclear key (spawned fresh, never cloned) |
| **Example** | Primals within a single gate's NUCLEUS communicating via UDS IPC |

Covalent bonds are the default within a gate's cytoplasm. All 13 primals
in a full NUCLEUS share covalent bonding. Cross-gate covalent bonds
(Plasmodium mesh) require Songbird federation + family seed verification.

### 2. Metallic — Delocalized Fleet, Specialized but Coordinated

| Property | Value |
|----------|-------|
| **Trust model** | Organizational (Mito-Beacon family) |
| **What it means** | Fleet compute, shared organization, specialized roles |
| **BTSP cipher** | `BTSP_HMAC_PLAIN` minimum |
| **K-Derm layer** | Plasma membrane, Periplasm |
| **Channel protein** | Aquaporin (always open) |
| **Braid policy** | Pass-through |
| **Genetics requirement** | Mito-Beacon membership (discovery, NAT) |
| **Example** | GPU cluster dispatch across multiple gates in same family; HPC pool |

Metallic bonds model the delocalized electron sea from chemistry.
Compute resources are shared across a fleet without per-operation
contracts. The organizational trust (Mito-Beacon) ensures discovery
without sharing nuclear credentials.

### 3. Ionic — Contract-Based, Scoped Access

| Property | Value |
|----------|-------|
| **Trust model** | Contractual |
| **What it means** | Formal contract, BTSP scoped tokens, capability masks, metered |
| **BTSP cipher** | `BTSP_CHACHA20_POLY1305` (encrypted only, non-negotiable) |
| **K-Derm layer** | Periplasm, Outer membrane |
| **Channel protein** | Gated ion (BTSP token opens gate, method-level filtering) |
| **Braid policy** | Verify (braid metadata checked at boundary) |
| **Genetics requirement** | None (contract-based, not family-based) |
| **Example** | University lab consuming HPC compute; ABG ionic compute sharing |

Ionic bonds are metered. Usage is tracked (call count, byte volume).
Contracts have lifecycle: Proposed → Active → Sealed (with provenance
seal containing merkle_root and braid_id). Capability deny lists
(`storage.*`, `dag.*`, `braid.*`, `crypto.*`) prevent braid internals
from crossing ionic boundaries.

### 4. Ceremony — Time-Bound Decay

| Property | Value |
|----------|-------|
| **Trust model** | Temporal |
| **What it means** | Time-limited covalent access that decays to ionic then weak |
| **BTSP cipher** | Matches current decay phase |
| **K-Derm layer** | Any (depends on decay phase) |
| **Channel protein** | Voltage-gated (time-bound gate with decay) |
| **Braid policy** | Verify |
| **Genetics requirement** | Nuclear during covalent phase, Mito-Beacon after decay |
| **Example** | Workshop access, visiting researcher, human entropy ceremony |

Ceremony bonds model voltage-gated ion channels: the gate opens for a
defined period, then progressively closes. A visiting researcher starts
with covalent access (full lab), decays to ionic (compute only, no
storage), then to weak (read-only, eventually expires).

### 5. Weak — No Active Transport, Read-Only

| Property | Value |
|----------|-------|
| **Trust model** | ZeroTrust |
| **What it means** | Public, read-only, passive API, no family trust |
| **BTSP cipher** | `BTSP_CHACHA20_POLY1305` (or TLS 1.3 at extracellular) |
| **K-Derm layer** | Outer membrane, Extracellular |
| **Channel protein** | Passive diffusion (no active transport) |
| **Braid policy** | Block (braid stripped, only results cross) |
| **Genetics requirement** | None |
| **Example** | Public website visitor; API consumer without authentication |

Weak bonds are the default for all traffic from the extracellular space
(Dark Forest principle). Traffic escalates to stronger bond types only
after authentication.

---

## Composite: OrganoMetalSalt

OrganoMetalSalt is not a sixth bond type but a **composite topology**
where a single workload crosses multiple bond-type boundaries:

```
Covalent core (cytoplasm)
  → Metallic fleet (plasma membrane + periplasm)
    → Ionic edge (outer membrane)
```

BTSP cipher follows the weakest boundary crossed. A workload originating
in a covalent cytoplasm and reaching an ionic partner through the
periplasm must use `BTSP_CHACHA20_POLY1305` for the ionic segment.

The name comes from chemistry: organo (carbon-based, covalent) + metallo
(metal coordination, delocalized) + salt (ionic crystal lattice).

---

## Bonding × K-Derm Layer Matrix

| Bond Type | Cytoplasm | Plasma Membrane | Periplasm | Outer Membrane | Extracellular |
|-----------|:---------:|:---------------:|:---------:|:--------------:|:-------------:|
| Covalent  | **HOME**  | crosses         | —         | —              | —             |
| Metallic  | —         | crosses         | crosses   | —              | —             |
| Ionic     | —         | —               | crosses   | crosses        | —             |
| Ceremony  | (decaying)| (decaying)      | (decaying)| —              | —             |
| Weak      | —         | —               | —         | crosses        | **HOME**      |

**HOME** = the bond type's natural habitat. **crosses** = may transit
through. **(decaying)** = Ceremony bonds pass through but lose trust
level over time.

---

## Bonding × BTSP Cipher Enforcement

From `BTSP_PROTOCOL_STANDARD.md`:

| Bond Type | Trust Model | Minimum Cipher | Negotiable Down To |
|-----------|-------------|----------------|---------------------|
| Covalent | GeneticLineage | `BTSP_NULL` | `BTSP_NULL` (all three allowed) |
| Metallic | Organizational | `BTSP_HMAC_PLAIN` | `BTSP_HMAC_PLAIN` |
| Ionic | Contractual | `BTSP_CHACHA20_POLY1305` | None (encrypted only) |
| Weak | ZeroTrust | `BTSP_CHACHA20_POLY1305` | None (encrypted only) |
| OrganoMetalSalt | Per-scope | Covalent core → `BTSP_NULL`, ionic edge → encrypted |

---

## Bonding × Genetics Alignment

From `GATE_SPRING_OWNERSHIP.md`:

| Genetics Tier | Type | Role | Cloneable | Minimum Bond |
|---------------|------|------|-----------|--------------|
| 1 | Mito-Beacon | Discovery, NAT, metadata | Yes | Metallic, Ionic |
| 2 | Nuclear | Permissions, auth, sessions | No (spawn fresh) | Covalent |
| 3 | Tag | Open channels (deprecated) | Yes | — |

All covalent bonds require Nuclear (Tier 2) trust — nuclear genetics
spawned fresh per generation. Ionic and metallic bonds require at minimum
Mito-Beacon (Tier 1) trust. The two-phase BTSP model (Phase 1:
mito-beacon tunnel, Phase 2: nuclear session) ensures discovery never
exposes authorization material.

---

## Bonding × Channel Protein Mapping

| Channel Protein | Bond Types | Behavior | K-Derm Layer |
|-----------------|------------|----------|--------------|
| **Aquaporin** | Covalent, Metallic | Always open, shared family seed | Cytoplasm, Plasma |
| **Gated ion** | Ionic | BTSP scoped token opens gate | Periplasm, Outer |
| **Voltage-gated** | Ceremony | Time-bound, decaying | Any (follows decay) |
| **Passive diffusion** | Weak | Read-only, no active transport | Outer, Extracellular |

Deploy graph `[graph.bonding_policy]` sections map directly:
```toml
tower_internal = "covalent"
cross_family = "ionic"
public_edge = "weak"
```

---

## Bonding Escalation Path

Traffic naturally escalates from weaker to stronger bonds:

```
Weak (extracellular)
  → Ionic (outer membrane — BTSP scoped token)
    → Metallic (periplasm — organizational trust)
      → Covalent (plasma membrane — family seed verification)
```

Each escalation requires progressively stronger authentication:
1. Weak → Ionic: Present BTSP scoped token
2. Ionic → Metallic: Prove Mito-Beacon membership
3. Metallic → Covalent: Complete nuclear session (fresh spawn)

The reverse path (covalent → weak) is **Ceremony** — a controlled decay
that progressively restricts access.

---

## Bonding in NUCLEUS Atomics

| Atomic | Internal Bond | Cross-Atomic Bond | External Bond |
|--------|---------------|-------------------|---------------|
| Tower (Electron) | Covalent (UDS IPC) | Covalent (mediates for Node/Nest) | Ionic/Weak (federation) |
| Node (Proton) | Covalent | Covalent (via Tower) | — (never directly exposed) |
| Nest (Neutron) | Covalent | Covalent (via Tower) | — (never directly exposed) |
| NUCLEUS (Atom) | Covalent | Metallic (fleet), Ionic (cross-family) | Weak (extracellular) |

Tower is the electron shell that mediates all boundary crossings.
Node and Nest primals never communicate directly with external systems —
all external bonding passes through Tower's capability surface.

---

## Validation

### primalSpring scenarios

| Scenario | Validates |
|----------|-----------|
| `s_ionic_bond` | Ionic contract lifecycle: propose → active → sealed |
| `s_covalent_bond` | Covalent mesh properties |
| `s_covalent_mesh` | Cross-gate covalent + Songbird federation |
| `s_sovereignty_parity` | `routing_config_reference.toml` backend types match bonding |
| `s_dark_forest_gate` | Enclave bonding policies + BTSP integrity |
| `s_kderm_boundary` (planned) | Deploy graph bonding_policy matches K-Derm layer rules |

### cellMembrane tests

`envelope.rs` tests: 27 tests covering bond ↔ channel protein mapping,
`permitted_inbound_bonds()` per layer, and `BoundaryPolicy` assembly.

---

## Cross-References

| Document | Relationship |
|----------|--------------|
| `K_DERM_TOPOLOGY_STANDARD.md` | Envelope layers where bonds are placed |
| `BTSP_PROTOCOL_STANDARD.md` | Cipher enforcement per bond type |
| `SOVEREIGNTY_STANDARDS.md` | Trust layers (Intracellular/Inner/Outer/Extracellular) |
| `GATE_SPRING_OWNERSHIP.md` | Genetics tier → bond minimum mapping |
| `MEMBRANE_CHANNEL_ARCHITECTURE.md` | Three channels + crypto layers |
| `DARK_FOREST_GLACIAL_GATE_STANDARD.md` | Enclave bonding policies |
| `primals/biomeOS/specs/NUCLEUS_BONDING_MODEL.md` | Canonical bonding spec |
| `cellmembrane-types/src/envelope.rs` | Rust typed implementation |

---

## FILE: `foundations/DARK_FOREST_GLACIAL_GATE_STANDARD.md`

# Dark Forest Glacial Gate Standard

**Version**: 1.0.0
**Date**: May 14, 2026
**Status**: Active — stadial entry gate
**Authority**: primalSpring (L2 coordination)
**Related**: `BTSP_PROTOCOL_STANDARD.md`, `birdsong/DARK_FOREST_BEACON_GENETICS_STANDARD.md`, `ECOBIN_ARCHITECTURE_STANDARD.md`

---

## Abstract

The Dark Forest Glacial Gate defines five security invariants that every NUCLEUS
deployment must satisfy before stadial transition. Named after the Three-Body
Problem principle: the safest strategy in a hostile universe is to remain
invisible. A NUCLEUS composition reveals nothing about its internal structure,
identity, or capabilities to external observers.

These invariants are validated by the `s_dark_forest_gate` scenario in
primalSpring (Tier::Rust structural, no live primals needed) and should be
adopted by downstream springs via their `guidestone` feature gate.

---

## Gate Criteria

### Pillar 1: Zero Metadata Leakage

| Requirement | Validation |
|-------------|------------|
| Release binaries are stripped (no debug symbols) | ecoBin `stripped = true` in manifest |
| No hostnames, usernames, or filesystem paths embedded | Build-time path sanitization via `strip` + release profile |
| BirdSong beacons are encrypted to observers | Beacon payload is ChaCha20 encrypted with beacon seed; observers see noise |
| DNS queries never leak primal identity | All external DNS routed through Songbird; primals have no direct network |

**Pass condition**: All primal entries in `manifest.toml` declare `stripped = true`.
BirdSong encryption is structural (DARK_FOREST_BEACON_GENETICS v2.0 requires
encrypted beacons when `BEACON_SEED` is set). No primal binary contains
hardcoded external hostnames.

### Pillar 2: Zero Port Exposure

| Requirement | Validation |
|-------------|------------|
| UDS-only is the default transport | `PRIMALSPRING_TCP_TIER5` must be unset by default |
| TCP ports are opt-in, never default | Zero-Port Tower Atomic standard (Wave 10) |
| Port numbers are configurable via environment | `ports.env` uses `${VAR:-default}` pattern |
| No well-known fingerprint from port scanning | Configurable defaults, not fixed constants in binaries |

**Pass condition**: Tier 5 TCP discovery is off when `PRIMALSPRING_TCP_TIER5`
is unset. All 13 primal port assignments in `tolerances` match `ports.env`.
No port collision in the assignment table.

### Pillar 3: Songbird as Sole Network Surface

| Requirement | Validation |
|-------------|------------|
| All external traffic routes through Songbird | Deploy graphs use `by_capability = "network"` → songbird |
| No primal directly opens external TCP listeners | Only Songbird advertises `http`, `tls`, `mesh` capabilities |
| NAT traversal via Songbird STUN/TURN | cellMembrane relay is Songbird-operated |
| Cross-gate federation uses Songbird mesh | Multi-node graphs route through songbird nodes |

**Pass condition**: Every deploy graph that includes external network access
has a songbird node. No non-songbird graph node advertises `http` or `tls`
capabilities. The `tower_atomic` fragment includes songbird.

### Pillar 4: BTSP Crypto Integrity

| Requirement | Validation |
|-------------|------------|
| All IPC authenticated via BTSP handshake | 13/13 primals implement `btsp.negotiate` |
| ChaCha20-Poly1305 AEAD for data in transit | BTSP Phase 3 cipher negotiation returns `chacha20-poly1305` |
| HKDF-SHA256 key derivation from family seed | Handshake key info string is `btsp-v1` |
| No cleartext in production | `FAMILY_ID` set + `BIOMEOS_INSECURE=1` = refuse to start |
| Seed fingerprints verify binary authenticity | BLAKE3 checksums in `checksums.toml` for all binaries |

**Pass condition**: The BTSP protocol constants match the standard. Deploy
graphs declare `secure_by_default = true` in metadata. The `btsp.capabilities`
method is registered. All manifest primal entries that declare `seed_fingerprint`
use BLAKE3.

### Pillar 5: Enclave Computing

| Requirement | Validation |
|-------------|------------|
| Dual-tower ionic pattern for sensitive data | healthSpring proto-nucleate has `egress_fence` metadata |
| Compute dispatch respects enclave boundaries | toadStool dispatch uses `FAMILY_ID` for session isolation |
| Content-addressed storage is opaque | NestGate BLAKE3 hashes reveal no metadata about content |
| Provenance chains don't leak internal details | sweetGrass attribution uses opaque agent identifiers |

**Pass condition**: The healthspring enclave proto-nucleate graph declares
`trust_model` and `bonding_policy` with enclave semantics. Content-addressed
capabilities (`content.*`) are routed to NestGate which uses BLAKE3 (opaque).
The provenance trio graph fragment includes the three provenance primals.

---

## Dark Forest Membrane Classification (Wave 77b)

The 5 pillars above apply with different strictness depending on which
membrane layer a component belongs to. This is the **diderm membrane
classification** — see `DIDERM_DOMAIN_ARCHITECTURE.md` for the full
trust barrier model.

| Pillar | Outer Membrane (`primals.eco`) | Peptidoglycan (trust barrier) | Inner Membrane (`primal.eco`) |
|--------|-------------------------------|-------------------------------|------------------------------|
| 1. Zero metadata leakage | **RELAXED** — Cloudflare sees visitor IPs, headers, timing. Acceptable for world-facing surface. | **STRICT** — VPS provider sees only encrypted relay traffic volume/timing. No primal identity or capability surface leaked. | **STRICT** — zero metadata leakage. Stripped binaries, no hostnames, BirdSong encrypted. |
| 2. Zero port exposure | **RELAXED** — 80/443 (Caddy), 53 (DNS ns2). | **STRICT** — 3478 (TURN), 2222 (sync relay), 22 (admin SSH). | **STRICT** — UDS-only default. Songbird :7700 sole federation surface. |
| 3. Songbird sole network surface | **N/A** — Caddy is the network surface by design. | **STRICT** — only Songbird TURN relay handles cross-membrane traffic. | **STRICT** — all external traffic routes through Songbird. |
| 4. BTSP crypto integrity | **N/A** — external users don't use BTSP. | **STRICT** — BTSP tokens are opaque. Peptidoglycan relays but cannot read, modify, or forge them. | **STRICT** — full BTSP enforcement, ChaCha20-Poly1305 AEAD, TrustedIssuerRegistry. |
| 5. Enclave computing | **N/A** — no compute on outer membrane. | **STRICT** — no biomeOS, no orchestration, no compute. Pure relay. | **STRICT** — full enclave boundaries, BTSP-gated dispatch. |

**The trust barrier invariant**: Peptidoglycan MUST NOT be able to read,
modify, or forge inner membrane traffic. It is a dumb pipe with
BTSP-opaque relay. cellMembrane Wave 75 confirmed: "BTSP tokens OPAQUE
in all relay channels."

### Content Layer (`nestgate.io`)

The content layer follows **inner membrane classification** (STRICT) for
all 5 pillars. Content integrity is verified by BLAKE3 hashes regardless
of delivery path. Even content served through the outer membrane CDN can
be validated by comparing hashes with the inner membrane's canonical copy.

---

## Validation Tiers

### Tier::Rust (Structural — available now)

The `s_dark_forest_gate` scenario in primalSpring validates all five pillars
by reading configuration, fragments, and registry at compile time. No live
primals needed. This is the gate for interstadial → stadial transition.

### Tier::Live (Wire — deferred to stadial phase)

Live validation requires multi-gate deployments with external observers:
- Verify encrypted BirdSong beacon payloads on the wire
- Probe that BTSP handshakes reject cleartext
- Confirm no non-Songbird TCP listeners from external scan
- Validate enclave boundary enforcement with cross-family dispatch attempts

---

## Spring Adoption

Each downstream spring should adopt Dark Forest validation via their
`guidestone` CI gate. The pattern follows the existing registry cross-sync:

```rust
// In spring's guidestone test module:
#[cfg(feature = "guidestone")]
#[test]
fn dark_forest_graph_compliance() {
    // Verify spring's deploy graphs carry secure_by_default = true
    // Verify no non-songbird nodes advertise http/tls capabilities
    // Verify tower_atomic fragment referenced in all compositions
}
```

Springs that already CI-validate against the 445-method registry can add
Dark Forest checks as an additional axis in the same test suite.

### Minimum Spring Requirements

| Requirement | What to Check |
|-------------|---------------|
| Deploy graphs | All `[graph.metadata]` sections declare `secure_by_default = true` |
| Tower inclusion | All compositions reference `tower_atomic` fragment (BearDog + Songbird + skunkBat) |
| No direct network | No spring-local nodes advertise `http.*` or `tls.*` capabilities |
| BTSP in graphs | All graph nodes that interact with primals declare `security_model = "btsp"` or `"tower_delegated"` |

---

## References

- BTSP Protocol Standard: `BTSP_PROTOCOL_STANDARD.md`
- Dark Forest Beacon Genetics: `birdsong/DARK_FOREST_BEACON_GENETICS_STANDARD.md`
- ecoBin Architecture: `ECOBIN_ARCHITECTURE_STANDARD.md`
- Membrane Channel Architecture: `MEMBRANE_CHANNEL_ARCHITECTURE.md`
- Zero-Port Standard: primalSpring `s_zero_port_standard` scenario
- Deployment Validation: `DEPLOYMENT_VALIDATION_STANDARD.md`
- Diderm Domain Architecture: `DIDERM_DOMAIN_ARCHITECTURE.md`
- Sovereignty Standards: `SOVEREIGNTY_STANDARDS.md` (§Sovereignty Shadow Membrane Applicability)
- fieldMouse Contract: `gardens/cellMembrane/specs/FIELDMOUSE_CONTRACT.md` (peptidoglycan is a fieldMouse)

---

## Changelog

| Date | Change |
|------|--------|
| 2026-06-04 | Wave 77b: Added §Dark Forest Membrane Classification — per-layer strictness for outer/peptidoglycan/inner membrane. Trust barrier invariant. Content layer classification. |
| 2026-05-14 | Initial: 5 pillars, structural validation, spring adoption guidance. |

---

## FILE: `foundations/DIDERM_DOMAIN_ARCHITECTURE.md`

# Diderm Domain Architecture — Trust Barrier Model

**Authority**: Overwatch + Ecosystem Convention  
**Status**: Active (Wave 150s)  
**Date**: 2026-07-21  
**Prerequisites**: `DARK_FOREST_GLACIAL_GATE_STANDARD.md`, `SOVEREIGNTY_STANDARDS.md`, `OVERWATCH_POSITION_STANDARD.md`

---

## Abstract

The ecoPrimals ecosystem operates a diderm (double-membrane) architecture
across three web domains. The **peptidoglycan VPS layer** is the trust
barrier — an air gap between the outer membrane (world-facing, commercial
services acceptable) and the inner membrane (pure sovereign primals, zero
commercial in the data path). The peptidoglycan is disposable, replicable,
and provider-independent.

This document defines the trust model, domain assignments, Dark Forest
membrane classification, and the cross-membrane validation pattern that
makes the dual membrane stronger than either membrane alone.

---

## The Biological Model

In gram-negative bacteria, the diderm envelope has two membranes separated
by the periplasmic space containing peptidoglycan — a rigid structural
layer that gives the cell shape and mechanical strength while remaining
permeable to small molecules.

The ecoPrimals diderm follows this pattern:

```
                  Hostile Internet
                        │
          ┌─────────────┴──────────────┐
          │    OUTER MEMBRANE          │
          │    primals.eco             │
          │    Cloudflare + Caddy      │
          │    (world-facing surface)  │
          └─────────────┬──────────────┘
                        │
          ┌─────────────┴──────────────┐
          │    PEPTIDOGLYCAN           │
          │    Trust Barrier / Air Gap │
          │    Songbird TURN relay     │
          │    Temporal sync hub       │
          │    STORES NOTHING          │
          │    DISPOSABLE              │
          └─────────────┬──────────────┘
                        │
          ┌─────────────┴──────────────┐
          │    INNER MEMBRANE          │
          │    primal.eco              │
          │    Sovereign DNS + TLS     │
          │    Songbird mesh           │
          │    bearDog BTSP            │
          │    biomeOS orchestration   │
          │    (organism coordination) │
          └─────────────┬──────────────┘
                        │
          ┌─────────────┴──────────────┐
          │    CONTENT LAYER           │
          │    nestgate.io             │
          │    NestGate CAS            │
          │    BLAKE3 integrity        │
          │    pseudoSpores, notebooks │
          │    (data objects)          │
          └────────────────────────────┘
```

---

## Domain Assignments

| Domain | K-Derm Layer | DNS Authority | TLS Provider | Trust Level | Purpose |
|--------|-------------|--------------|-------------|-------------|---------|
| `primals.eco` | Intra-membrane (shared ecosystem) | Cloudflare (wildcard `*.primals.eco`) | Caddy + LE (per-site or on-demand) | **Shared trust** — ecosystem services | Ecosystem platform: depot, forge, compositions, public tools, docs |
| `primal.eco` | Inner membrane (personal sovereign) | Sovereign knot-dns | Sovereign Caddy + LE | **Full trust** — Dark Forest strict | Personal substrate: mesh API, relay, gate coordination, HPC federation, ceremonies |
| `nestgate.io` | Data service point (interaction layer) | Sovereign knot-dns | Sovereign Caddy + LE | **Content trust** — BLAKE3 integrity | Data service interaction: CAS backbone, federated APIs, weak bond data ingestion |

### Domain Identity

The three domains serve distinct roles:

- **`primals.eco`** — the **intra-membrane**. The ecosystem's shared
  infrastructure and public face. Root domain redirects to
  `sporeprint.primals.eco`. All compositions, tools, and services are
  subdomains: `prefix.primals.eco`. Subdomains are sovereign-routed:
  `*.primals.eco` resolves via a single Cloudflare wildcard A record,
  and Caddy on golgi handles all per-hostname routing. New services
  only need a Caddy block — no DNS changes. This is the layer between
  the personal inner membrane and the hostile internet. Cloudflare
  operates as the outer firebreak (DDoS, CDN), making `primals.eco`
  an intra-membrane — not directly exposed, but publicly accessible
  through the firebreak.
- **`primal.eco`** — the **inner membrane**. The operator's personal
  sovereign substrate. LAN/WAN mesh, private compositions, sovereign
  ceremony host. Key creation ceremonies (SoloKey FIDO2 + Pixel
  StrongBox entropy mixing), bearDog gatehouse, private compositions,
  HPC federation, and inner membrane coordination. This is where
  cryptographic sovereignty is exercised — entropy ceremonies,
  FAMILY_SEED management, BTSP authentication authority. This domain
  is a fully independent identity, not a mirror of `primals.eco`.
- **`nestgate.io`** — the **data service interaction point**. nestGate
  CAS as the content-addressed backbone. All external scientific and
  geospatial data sources (NCBI, PubMed, UniProt, USGS, FEMA, ArcGIS,
  etc.) enter through drawbridge-registered weak bonds and land in the
  CAS. The single public entry point for querying content-addressed
  sovereign data. The interaction layer for the ecosystem's data mesh.

**Composition routing by domain**: The same primals serve both domains, but
the trust level and data scope differ. A footPrint instance on
`footprint.primals.eco` shows public GIS data (shared projects, demo tiles).
A footPrint instance on `primal.eco` shows private property data, personal
measurements, and sovereign coordinates — backed by Loam Certificates for
provenance and bearDog-signed sessions for integrity. The domain determines
the membrane layer, which determines the trust model.

**Root domain standard**: `primals.eco` (bare) redirects to
`sporeprint.primals.eco`. All compositions use `prefix.primals.eco`
subdomains — no path-based routing on the root domain.

### DNS Routing Model (Wave 137b+)

| Record | Type | Content | Notes |
|--------|------|---------|-------|
| `primals.eco` | A | golgi VPS IP | Root domain (wildcard doesn't cover root) |
| `*.primals.eco` | A | golgi VPS IP | Wildcard — Caddy is routing authority |
| `www.primals.eco` | CNAME | `primals.eco` | www redirect |
| `ns2.primals.eco` | A | sovereign DNS IP | Different IP — keep explicit |

Caddy handles Host-header routing for all `*.primals.eco` subdomains.
Explicit Caddy server blocks take precedence over the wildcard catch-all.
Unknown subdomains return 404 via the catch-all block.

### Registrar

All three domains are on Porkbun. NS records are set per-domain:
- `primals.eco` → Cloudflare nameservers (outer membrane, wildcard DNS)
- `primal.eco` → `ns1.primals.eco` / `ns2.primals.eco` (sovereign)
- `nestgate.io` → `ns1.primals.eco` / `ns2.primals.eco` (sovereign)

---

## The Peptidoglycan Trust Barrier

### Properties

The peptidoglycan layer sits between outer and inner membranes. It is the
**only** point where they touch. It has these invariant properties:

| Property | Requirement |
|----------|------------|
| **Stores nothing** | Broker/relay only. No primary data, no user data, no secrets beyond `tower.env`. |
| **Disposable** | Can be torn down and reprovisioned from `membrane.toml` + `tower.env`. No state loss. |
| **Replicable** | Deployable on any VPS provider or self-hosted from a WAN-facing gate. |
| **Provider-as-adversary** | VPS provider is a non-family observer. Secrets encrypted at rest. |
| **BTSP-opaque** | All relay traffic is encrypted end-to-end. Peptidoglycan relays but cannot read, modify, or forge inner membrane traffic. |
| **Unidirectional flow** | Outer pushes TO peptidoglycan. Inner pulls FROM peptidoglycan. Neither reaches the other directly. |

### Current Deployment

| Node | IP | Layer | Role |
|------|----|-------|------|
| golgiBody-ext | 137.184.197.151 | Outer membrane | Caddy TLS, sporePrint, DNS ns2 |
| peptidoglycan | [RELAY_PUBLIC] | Trust barrier | Songbird TURN, temporal sync, Forgejo relay |
| golgiBody | [RELAY_PUBLIC] | Inner membrane | knot-dns ns1, Forgejo, sovereign DNS |

### Multi-Peptidoglycan

The peptidoglycan is a **role**, not a single VPS. It can be fulfilled by:

| Instance | Provider | Purpose | Status |
|----------|----------|---------|--------|
| peptidoglycan-nyc1 | DigitalOcean | Primary relay | **OPERATIONAL** |
| peptidoglycan-eu | Hetzner | Geographic redundancy | Future |
| peptidoglycan-self | Self-hosted WAN gate | Remove VPS dependency | Future |
| peptidoglycan-abg | ABG member hosted | Federation relay | Future |

The inner membrane discovers peptidoglycan instances through Songbird TURN
peer registration. Adding a new instance requires only:
1. Deploy `membrane.toml` with `composition = "peptidoglycan"`
2. Start Songbird TURN on the new instance
3. Inner membrane gates add it to `SONGBIRD_PEERS`

### Self-Hosting Path

When a WAN-facing gate has a public IP (flockGate already does, via
cellMembrane relay), it can serve the peptidoglycan role directly. The
VPS peptidoglycan then becomes redundant — the organism grows its own
structural layer. This is the sovereignty endgame for the structural
layer: zero external substrate dependency.

---

## Dark Forest Membrane Classification

The 5 Dark Forest pillars (from `DARK_FOREST_GLACIAL_GATE_STANDARD.md`)
apply with different strictness per membrane layer:

### Pillar 1: Zero Metadata Leakage

| Layer | Classification | What Leaks | Acceptable? |
|-------|---------------|-----------|-------------|
| Outer | **RELAXED** | Cloudflare sees visitor IPs, headers, timing, geographic distribution | Yes — this is the world-facing surface. Its job is to absorb hostile traffic. |
| Peptidoglycan | **STRICT** | VPS provider sees only encrypted relay traffic volume and timing. No primal identity, no capability surface, no content. | Provider metadata (connection timing, bandwidth) is the residual. Acceptable for relay. |
| Inner | **STRICT** | Zero metadata leakage. Stripped binaries, no hostnames embedded, BirdSong encrypted. | No exceptions. |

### Pillar 2: Zero Port Exposure

| Layer | Classification | Exposed Ports |
|-------|---------------|--------------|
| Outer | **RELAXED** | 80/443 (Caddy HTTP/HTTPS), 53 (DNS ns2) |
| Peptidoglycan | **STRICT** | 3478 (TURN relay), 2222 (Forgejo SSH relay), 22 (admin SSH) |
| Inner | **STRICT** | UDS-only default. Songbird :7700 is the sole federation surface on LAN. |

### Pillar 3: Songbird as Sole Network Surface

| Layer | Classification | Network Surface |
|-------|---------------|----------------|
| Outer | **N/A** | Caddy is the network surface by design. |
| Peptidoglycan | **STRICT** | Only Songbird TURN relay handles cross-membrane traffic. |
| Inner | **STRICT** | All external traffic routes through Songbird. No primal directly opens external listeners. |

### Pillar 4: BTSP Crypto Integrity

| Layer | Classification | BTSP Role |
|-------|---------------|-----------|
| Outer | **N/A** | External users don't use BTSP. Authentication is Cloudflare-level or public. |
| Peptidoglycan | **STRICT** | BTSP tokens are **opaque** to peptidoglycan. It relays encrypted payloads. It cannot issue, verify, or modify tokens. |
| Inner | **STRICT** | Full BTSP enforcement. ChaCha20-Poly1305 AEAD. Cross-gate token verification via TrustedIssuerRegistry. |

### Pillar 5: Enclave Computing

| Layer | Classification | Compute Role |
|-------|---------------|-------------|
| Outer | **N/A** | No compute — serves static content and proxies. |
| Peptidoglycan | **STRICT** | No biomeOS, no orchestration, no compute dispatch. Pure relay. |
| Inner | **STRICT** | Full enclave boundaries. toadStool dispatch, barraCuda ML, coralReef SPIR-V — all BTSP-gated. |

### The Key Rule

**Peptidoglycan MUST NOT be able to read, modify, or forge inner membrane
traffic.** It is a dumb pipe. cellMembrane Wave 75 confirmed: "BTSP tokens
OPAQUE in all relay channels." This is the trust barrier invariant.

---

## Cross-Membrane Validation

The dual membrane creates a **permanent integrity monitoring pattern**.
The inner membrane is the ground truth. The outer membrane is always
under suspicion.

### Validation Checks

| Check | Method | What It Catches |
|-------|--------|----------------|
| Content integrity | Same resource via outer (`primals.eco`) and inner (`primal.eco`), compare BLAKE3 hashes | CDN injection, content modification, stale cache |
| Timing baseline | Inner membrane response time is the floor. Outer should be inner + CDN overhead. | Unexpected latency = interception or throttling |
| Availability cross-check | Inner healthy + outer reports down = external service failure, not real downtime | Cloudflare outage, regional blocking |
| TLS certificate verification | Inner membrane knows the real LE certificate fingerprint. Compare with outer. | Certificate substitution (Cloudflare MITM by design issues its own cert) |
| DNS consistency | Query sovereign NS (`ns1.primals.eco`) vs public resolver (`8.8.8.8`). Compare. | DNS poisoning, hijacking, registrar compromise |
| Route integrity | Traceroute from inner membrane to outer. Known hop count as baseline. | BGP hijacking, route injection |

### Why This Is Stronger Than Eliminating Cloudflare

Eliminating Cloudflare removes DDoS protection and CDN benefits.
Keeping Cloudflare on the outer membrane but validating from the inner
membrane gives you **both**:

- External traffic protection (Cloudflare absorbs DDoS, bots, scanners)
- Integrity verification (inner membrane detects any tampering)
- Graceful degradation (if outer membrane is compromised, inner membrane
  continues serving trusted peers directly)

The dual membrane is not a transitional state. It is the **target
architecture**.

---

## Inner Membrane Use Cases (primal.eco)

| Subdomain | Service | Purpose |
|-----------|---------|---------|
| `mesh.primal.eco` | Songbird | Federation endpoint for gate-to-gate mesh |
| `relay.primal.eco` | Songbird TURN | Peptidoglycan relay endpoint |
| `auth.primal.eco` | bearDog BTSP | Token exchange, trust establishment |
| `api.primal.eco` | biomeOS | Internal API for orchestration and dispatch |
| `dns.primal.eco` | knot-dns | Sovereign DNS management interface |

### ABG Federation

An ABG member spinning up their own HPC gate joins via `primal.eco` mesh:
1. Deploy their own peptidoglycan (or connect directly if LAN-reachable)
2. Start bearDog with family seed enrollment
3. Start Songbird with `SONGBIRD_PEERS` pointing to `relay.primal.eco`
4. Inner membrane discovers them via `discovery.peers`
5. Sovereign trust only — no commercial service in the data path
6. Shared compute via BTSP-authenticated `capability.call`

---

## Content Layer Use Cases (nestgate.io)

| URL Pattern | Service | Purpose |
|-------------|---------|---------|
| `nestgate.io/<blake3-hash>` | NestGate CAS | Direct content-addressed fetch |
| `nestgate.io/spore/<name>` | NestGate + pseudoSpore | Named pseudoSpore access |
| `nestgate.io/notebook/<id>` | NestGate + petalTongue | Rendered notebook view |
| `nestgate.io/manifest/<name>` | NestGate cas-manifest | sporePrint content manifests |

Content integrity is sovereign regardless of delivery path. Even if served
through a CDN, BLAKE3 hashes verify end-to-end. The content layer can
optionally use outer membrane CDN for performance while inner membrane
verifies integrity.

**Backing store**: westGate 76TB ZFS pool (primary), federated across gates
via `content.replicate.pull` on inner membrane.

---

## Sovereignty Shadow Evolution

The sovereignty shadows (S1-S5) now apply specifically to the inner membrane:

| Track | What | Inner Membrane | Outer Membrane |
|-------|------|---------------|----------------|
| S1 TLS | TLS termination | Caddy + LE on golgiBody (sovereign, MUST) | Cloudflare proxy (acceptable) |
| S2 NAT | NAT relay | Songbird TURN (GRADUATED) | N/A |
| S3 Content | Content serving | NestGate CAS on `nestgate.io` (sovereign) | sporePrint via Caddy or CDN (acceptable) |
| S4 Auth | Authentication | bearDog BTSP enforced (sovereign, MUST) | Public/Cloudflare auth (acceptable) |
| S5 DNS | DNS resolution | knot-dns for `primal.eco` + `nestgate.io` (sovereign, MUST) | Cloudflare DNS for `primals.eco` (acceptable) |

The principle: **inner membrane MUST be fully sovereign. Outer membrane
MAY use commercial services.** Cross-membrane validation ensures the outer
membrane stays honest.

---

## Sovereignty Evolution Roadmap (Wave 150s)

The ecosystem contains industry tools at various membrane layers. This
roadmap classifies each by its evolution path: **Replace** (primal
composition replaces the tool), **Late-Stage** (replacement blocked on
a prerequisite primal), or **Firebreak** (stays on outer membrane by
design — industry tools absorbing hostile traffic is the correct
architecture).

### Three-Tier Classification

| Tool | Current Layer | Classification | Primal Path | Priority |
|------|-------------- |---------------|-------------|----------|
| **WireGuard** | Transport (kernel) | **REPLACE** | Tower Atomic (bearDog + songBird + skunkBat) | Phase 1 |
| **Zola** | Build (sporePrint) | **REPLACE** | petalTongue rendering + nestGate CAS content | Phase 1 |
| **Forgejo** | Intra-membrane (git hosting) | **LATE-STAGE** | rootPulse (nestGate CAS + Provenance Trio) | Phase 2 (post-rootPulse) |
| **Cloudflare** | Outer membrane (DNS/DDoS) | **FIREBREAK** | N/A — this IS the firebreak | Stays |
| **Caddy** | Outer membrane (TLS/proxy) | **FIREBREAK** | cellMembrane generates config; Caddy serves | Stays |
| **Let's Encrypt** | Outer membrane (TLS certs) | **FIREBREAK** | ACME is the standard | Stays |
| **Porkbun** | External (registrar) | **FIREBREAK** | Registrars are inherently external | Stays |
| **RustDesk** | Outer membrane (human access) | **FIREBREAK** | AGPL-3.0 compliant; learn-from-leverage | Stays |
| **JupyterHub** | Outer membrane (interface) | **FIREBREAK** | Interface only; compute is inner membrane | Stays (repositioned) |

### Phase 1: Tower Atomic Supersedes WireGuard

WireGuard currently provides the kernel-level encrypted mesh between
gates. songBird already operates as a sovereign mesh overlay on top of
WireGuard, and Tower Atomic (bearDog + songBird + skunkBat) handles
authenticated encrypted transport end-to-end.

The target: Tower Atomic **meets and exceeds** WireGuard's capabilities,
making the kernel VPN redundant. When Tower can provide:

| Capability | WireGuard Today | Tower Atomic Target |
|-----------|----------------|-------------------- |
| Encrypted tunnel | ChaCha20-Poly1305 (kernel) | BTSP ChaCha20-Poly1305 AEAD (userspace, sovereign keys) |
| Peer discovery | Static config (`wg0.conf`) | songBird dynamic peer discovery + TURN relay |
| Key management | Manual pubkey exchange | bearDog BTSP trust establishment, FAMILY_SEED rooted |
| NAT traversal | Requires manual endpoint config | songBird TURN + skunkBat hole-punching |
| Reconnection | Automatic (kernel) | songBird persistent mesh with exponential backoff |
| Performance | Kernel-space, ~1 Gbps | Userspace — must benchmark to WG baseline |

**Parity gate**: Tower must demonstrate equivalent throughput and latency
on the LAN mesh before WireGuard can be removed. Performance benchmark
is the only remaining criterion — all other capabilities are already
sovereign.

### Phase 1: Primal sporePrint Pipeline Replaces Zola

sporePrint currently uses Zola (Rust static site generator) to build
`sporeprint.primals.eco`. The primal replacement pipeline:

```
Content (markdown/data) → nestGate CAS (content-addressed storage)
  → petalTongue (rendering: WASM WebGL + SVG + description)
    → cellMembrane (serving: Caddy config generation)
      → primals.eco (public surface)
```

petalTongue's WASM WebGL pipeline (Wave 150r) is the enabling step —
browser-side rendering is now fully primal. The remaining work is
wiring sporePrint's content pipeline to emit from CAS rather than
Zola's file-based build.

### Phase 2: rootPulse Replaces Forgejo (Late-Stage)

Forgejo (`git.primals.eco`) is a solid intra-membrane tool — self-hosted,
functional, not in the inner membrane data path. Replacement only happens
when **rootPulse** is live:

- rootPulse = sovereign version control backed by nestGate CAS +
  Provenance Trio (rhizoCrypt lineage, loamSpine ledger, sweetGrass
  attribution)
- Git-compatible interface over CAS-backed storage
- Loam Certificates for commit provenance (replacing GPG signatures)
- This is explicitly **not a near-term priority** — Forgejo serves well

### Firebreak Tools: Outer Membrane by Design

**RustDesk** (AGPL-3.0): License-compliant with the ecosystem's
open-source model. The ecosystem learns from and leverages RustDesk's
relay architecture. It provides human-operator remote access on the
outer membrane, coexisting with MitoBeacon (autonomous identity on the
inner membrane). As MitoBeacon matures, RustDesk's role naturally
narrows to human-in-the-loop scenarios.

**JupyterHub**: Repositioned as **outer membrane interface only**.
ABG members, external collaborators, and human scientists use JupyterHub
as a web interface that submits work to inner membrane primals (biomeOS
orchestration → toadStool dispatch → barraCuda compute). JupyterHub
never processes sovereign data itself — it is a submission portal. The
actual workload executes entirely within the inner membrane enclave.

**Cloudflare, Caddy, Let's Encrypt, Porkbun**: These are the correct
tools for absorbing hostile internet traffic. The outer membrane's job
is to face the storm. The inner membrane's job is to coordinate the
organism. Industry tools on the outer membrane are not debt — they are
the firebreak.

---

## Peptidoglycan Composition Specification

### membrane.toml Schema

```toml
[membrane]
name = "peptidoglycan-nyc1"
composition = "peptidoglycan"

[membrane.identity]
family_id = "membrane-alpha"
gate_id = "pepti-nyc1"

[membrane.provider]
type = "digitalocean"
region = "nyc1"

[membrane.channels.relay]
enabled = true
port = 3478
primal = "songbird"

[membrane.channels.sync]
enabled = true
port = 2222

[membrane.channels.surface]
enabled = false

[membrane.trust_barrier]
inner_domain = "primal.eco"
outer_domain = "primals.eco"
opaque_relay = true
```

### Lifecycle

```
provision → harden → deploy → validate → operate → [teardown → reprovision]
                                                          │
                                                   No data loss.
                                                   tower.env is the only state.
                                                   Inner membrane unaffected.
```

### Deploy Anywhere

```bash
# DigitalOcean (current)
deploy_membrane.sh --composition peptidoglycan --provider digitalocean --region nyc1

# Hetzner (future redundancy)
deploy_membrane.sh --composition peptidoglycan --provider hetzner --region fsn1

# Self-hosted from WAN gate
deploy_membrane.sh --composition peptidoglycan --provider bare_metal --host flockgate.local
```

---

## Revised Glacial Shift Criteria

| # | Criterion | Revised Meaning |
|---|-----------|----------------|
| 1 | Sovereignty shadows graduated (inner membrane) | S1-S4 on `primal.eco` path. Outer membrane may use commercial TLS. |
| 2 | Multi-gate LAN mesh operational (3+) | Songbird mesh on inner membrane. eastGate + strandGate + westGate. |
| 3 | Peptidoglycan replicable | Can be torn down and redeployed from `membrane.toml`. Trust barrier tested. |
| 4 | Remote covalent node over WAN | Via inner membrane only (TURN through peptidoglycan). |
| 5 | DNS sovereign for inner membrane | `primal.eco` + `nestgate.io` on knot-dns. `primals.eco` on Cloudflare OK. |
| 6 | Inner membrane zero-commercial + cross-validation | Zero commercial in `primal.eco` data path. Dual-path validation operational. |

---

## References

- `DARK_FOREST_GLACIAL_GATE_STANDARD.md` — 5 security invariants
- `SOVEREIGNTY_STANDARDS.md` — Calibrate → Shadow → Cutover protocol
- `OVERWATCH_POSITION_STANDARD.md` — Floating coordination role
- `FIELDMOUSE_CONTRACT.md` — fieldMouse deployment contract (peptidoglycan is a fieldMouse)
- `MULTI_MEMBRANE_DEPLOYMENT.md` — Multi-membrane parameterization model
- `DEPLOYMENT_PHASE_PLAN.md` — Phased deployment from parity to stadial entry
- `whitePaper/gen5/foundations/COVALENT_MESH_TRUST_VALIDATION.md` — Cross-gate trust model
- `whitePaper/gen5/foundations/KDERM_DIDERM_APPLICATION.md` — K-Derm bonding model

---

## Changelog

| Wave | Change |
|------|--------|
| 77 | Initial: formalized diderm domain architecture with peptidoglycan trust barrier, Dark Forest membrane classification, cross-membrane validation pattern, revised glacial shift criteria. |
| 137b | Wildcard `*.primals.eco` DNS active. Domain identity separation formalized: `primals.eco` (public platform), `primal.eco` (sovereign substrate + entropy ceremonies + private compositions), `nestgate.io` (federated data gateway). Composition routing by domain documented (same primals, different trust/data scope per domain). Loam Certificate vs TLS credential terminology applied. |
| 150d | Domain terminology refined: `primals.eco` = intra-membrane (shared ecosystem), `primal.eco` = inner membrane (personal sovereign), `nestgate.io` = data service interaction point. Root domain redirect: `primals.eco` → `sporeprint.primals.eco`. Subdomain standard enforced for all compositions. sporePrint gets own subdomain. |
| 150j | **Git relay layer activated**: Forgejo (`git.primals.eco`) is sovereign primary for all source code. GitHub is subordinate outer membrane mirror. 39/39 repos have Forgejo push mirrors (`sync_on_commit: true`, HTTPS token auth via golgiBody). Gates push to Forgejo only — golgiBody relays to GitHub automatically on every commit. GitHub SSH surface consolidated from 12 per-gate keys to 2 (`forgejo-relay@golgiBody` + `golgiBody-ext@vps`). Sync divergence structurally eliminated. |
| 150s | **Sovereignty Evolution Roadmap**: Three-tier classification (Replace / Late-Stage / Firebreak). Phase 1: WireGuard → Tower Atomic, Zola → primal sporePrint pipeline. Phase 2: Forgejo → rootPulse (post-Provenance Trio). Firebreak stays: Cloudflare, Caddy, RustDesk (AGPL-3.0), JupyterHub (repositioned as outer membrane interface). DNSSEC 3/3 domains validated. |

---

*"The outer membrane faces the storm. The inner membrane coordinates the
organism. Between them, the peptidoglycan stands — thin, disposable,
replaceable — but structurally essential. It is the air gap that makes
sovereignty possible while the world still rages outside."*

---

## FILE: `foundations/EXTERNAL_CLAIM_CONVERGENCE_STANDARD.md`

# External Claim Convergence Standard

**Authority**: sporePrint team (eastGate overwatch)
**Status**: Ecosystem Standard — Wave 150x
**Date**: July 25, 2026
**Triggered by**: External credibility audit of primals.eco

---

## Purpose

Every public-facing surface — README, GitHub org profile, primals.eco page,
llms.txt — must converge to a single pipeline of truth. An external reviewer
found inconsistencies across surfaces that are individually correct but
collectively undermine credibility. This standard defines what convergence
means and what each team must do.

The canonical registry is `sporePrint/config.toml`. All external counts
must either:

1. Pull from this registry at build/render time, OR
2. State the measurement date and source explicitly

No manually entered ecosystem number should survive outside the registry.

---

## 1. Metric Pipeline

### The Problem

| Metric | Canonical (config.toml) | Found elsewhere |
|--------|------------------------|-----------------|
| Springs | 9 | "8 springs" (15+ pages, pre-fix) |
| Organizations | 4 | "Three organizations" (homepage, pre-fix) |
| WGSL shaders | 952 | 806 (architecture pages), 860 (barraCuda README), 914 (thesis) |
| Primals | 15 | "13 primals" (ECOSYSTEM_INVENTORY, pre-fix) |

### The Standard

**S1**: Every README that displays an ecosystem-wide metric (LOC, tests,
shaders, springs, primals) MUST include a `<!-- metrics: YYYY-MM-DD -->` comment
with the measurement date. Stale metrics (>30 days) should be flagged by CI.

**S2**: sporePrint pages MUST use `{{ total_stat() }}` or `{{ entity_stat() }}`
shortcodes for any number that appears in `config.toml`. Hardcoded numbers
are a bug.

**S3**: GitHub org profiles and repo descriptions SHOULD be updated when
`spore-validate refresh` detects >5% drift. The sporePrint team will
issue an impulse when this happens.

**S4**: Thesis chapters are historical snapshots. They carry the numbers
from their authoring wave and do not update. This is acceptable because
they are dated academic documents.

### Team Actions

| Team | Action | Priority |
|------|--------|----------|
| barraCuda | Update README WGSL count from 860 → 952 (or pull from registry) | P1 |
| All primals | Add `<!-- metrics: YYYY-MM-DD -->` to README header | P2 |
| sporePrint | Issue impulse when `refresh` detects drift | Continuous |

---

## 2. Claim Qualification

### The Problem

Several claims on external surfaces are accurate in narrow scope but stated
absolutely. An external reviewer will interpret them at face value.

| Claim | Issue | Scoped Truth |
|-------|-------|-------------|
| `#![forbid(unsafe_code)]` everywhere | toadStool has 44 justified unsafe blocks | Forbidden by default; isolated to hardware-containment crates |
| "zero C dependencies" | `cc` crate exists in build graph (unused backend) | No C/C++/Fortran in runtime dependency chain |
| "any GPU" | Requires Vulkan drivers | Any GPU with Vulkan (tested: NVIDIA, AMD, Intel) |
| "replaces X" | Invites unfavorable feature-completeness comparison | Provides sovereign alternative for specific validated workflows |
| "production ready" | Pre-1.0 semver on some primals | Deployed and running on N gates; version M.N.P |

### The Standard

**S5**: Absolute claims (`all`, `every`, `zero`, `no`) MUST be followed by
their scope in the same sentence or paragraph. If the scope cannot fit,
the claim is too broad.

**S6**: "Replaces X" is acceptable in comparison tables where the context is
clear. It MUST NOT appear in meta descriptions, JSON-LD, or AI surface
files without qualification.

**S7**: `#![forbid(unsafe_code)]` claims MUST specify which crates. The
ecosystem-wide phrasing is:

> Unsafe code is forbidden by default (`#![forbid(unsafe_code)]` at crate roots)
> and isolated to narrowly scoped, safety-documented hardware-containment crates
> where required.

**S8**: "Zero C dependencies" MUST be stated as:

> No C/C++/Fortran libraries in the runtime dependency chain. Pure Rust
> cryptography (RustCrypto), pure Rust compression (`miniz_oxide`).

### Team Actions

| Team | Action | Priority |
|------|--------|----------|
| ecoPrimals org | Update GitHub org bio: scope the `#![forbid(unsafe_code)]` claim | P1 |
| biomeOS | Remove "A++ LEGENDARY" from external-facing README; use dual labeling | P1 |
| toadStool | Ensure README documents unsafe block count and justification summary | P2 |
| All READMEs | Audit for unscoped absolutes (`all`, `every`, `zero`, `no`) | P2 |

---

## 3. Maturity Labeling

### The Problem

Internal evolutionary grades (stadial, wave, "A++") appear on external
surfaces. External reviewers interpret these as audit results or maturity
claims. They are neither.

### The Standard

**S9**: Every public-facing README MUST include an **External Maturity** label
from this vocabulary:

| Label | Meaning |
|-------|---------|
| `experimental` | Under active development; API unstable |
| `research-ready` | Functioning with validated results; not feature-complete |
| `deployment-ready` | Tested on multiple gates; stable API; documented |
| `production-candidate` | Deployed in production; monitoring active |
| `externally-validated` | Used or reviewed by external parties |

**S10**: Internal evolutionary labels (stadial, wave grade, debt state) are
welcome in CHANGELOG, internal docs, and wateringHole AARs. They MUST NOT
appear in the first 20 lines of a public README.

**S11**: sporePrint's products page and Evidence Snapshot are the canonical
external maturity reference. Discrepancies between a repo's README maturity
label and sporePrint's label should be resolved by the team owning the repo.

### Team Actions

| Team | Action | Priority |
|------|--------|----------|
| biomeOS | Add `External Maturity: deployment-ready` to README; move "A++ LEGENDARY" to CHANGELOG | P1 |
| All primals | Add maturity badge to README top-matter | P2 |
| sporePrint | Validate maturity labels during `spore-validate refresh` | P3 |

---

## 4. Inspectable Infrastructure

### The Problem

bearDog and skunkBat source remain "available on request" rather than
publicly inspectable. The identity, crypto, transport, and defensive-security
foundation is precisely the portion skeptical reviewers most need to inspect.
This creates a philosophical gap with the project's openness claims.

### The Standard

**S12**: Any primal whose capabilities are cited on primals.eco SHOULD have
its source code publicly available. If operational security requires delayed
publication, the README MUST state the timeline and rationale.

### Team Actions

| Team | Action | Priority |
|------|--------|----------|
| Tower team | Evaluate timeline for bearDog + skunkBat public source publication | P2 |
| Tower team | If not publishing: add README explaining why and when (with timeline) | P2 |

---

## 5. Externalization Roadmap

### The Problem

The project has substantial commits, tests, documentation, and internal
validation, but public participation remains close to zero. The proof chain
is technically deep but socially only one node wide.

### The Standard

**S13**: The next phase should prioritize externalization over architecture.
Five milestones, in priority order:

1. **One canonical guideStone** that a stranger can download and verify in
   under 5 minutes. No setup beyond `rustup` and `git clone`.
2. **One public reproduction ledger** showing failures alongside successes.
   (lithoSpore's pseudoSpore braid can serve this role.)
3. **One spring used by a scientist** on data the ecosystem did not select.
4. **One institutional-quality technical report** with claims narrower than
   the evidence behind them.
5. **Complete publication** of foundational Tower source.

### Team Actions

| Team | Action | Priority |
|------|--------|----------|
| sporePrint + lithoSpore | Publish one-command guideStone verification path | P1 |
| All spring teams | Identify one external dataset for validation | P2 |
| sporePrint | Draft narrow-claim technical report | P3 |
| Tower team | Evaluate source publication timeline | P2 |

---

## Adoption

This standard is effective immediately. Teams should address P1 items within
the current wave. P2 items should be planned for the next wave. P3 items are
roadmap guidance.

sporePrint team will track convergence via `spore-validate refresh` drift
detection and periodic external review cycles.

**Companion AAR**: `aars/SPOREPRINT_CREDIBILITY_AUDIT_AAR_150x.md`

---

## FILE: `foundations/K_DERM_TOPOLOGY_STANDARD.md`

<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# K-Derm Topology Standard — Cell Envelope Model for Sovereign Infrastructure

**Version**: 1.0.0
**Date**: May 26, 2026
**Status**: Active
**Authority**: wateringHole Consensus (canonical spec: `gardens/cellMembrane/specs/K_DERM_TOPOLOGY.md`)
**Related**: `BONDING_MODEL_STANDARD.md`, `SOVEREIGNTY_STANDARDS.md`, `BTSP_PROTOCOL_STANDARD.md`, `GATE_SPRING_OWNERSHIP.md`, `MEMBRANE_CHANNEL_ARCHITECTURE.md`
**Typed implementation**: `gardens/cellMembrane/crates/cellmembrane-types/src/envelope.rs`

---

## What K-Derm Is

K-Derm is the cell envelope topology model for sovereign infrastructure.
It models directly from cell envelope biology — monoderm/diderm bacteria,
eukaryotic organelle membranes, vesicle transport, endosymbiosis — and
extends into a network topology model.

**K-NOME is how we build. K-Derm is how what we build is shaped.**

K-Derm replaces the ambiguous "inner/outer membrane" terminology that
conflicted across ecosystem documents (see §5: Franklin's Current Resolution).
All envelope layers use **absolute positions** named from inside out.

---

## Section 1: Envelope Topologies

Two topologies are defined, matching bacterial cell envelope biology:

### Monoderm (single boundary)

```
cytoplasm (gate NUCLEUS) → plasma membrane (gate firewall) → environment
```

Single membrane boundary. Gate directly on network, no VPS relay.
Example: ironGate on home LAN.

### Diderm (double boundary)

```
cytoplasm (gate NUCLEUS, UDS IPC)
  → plasma membrane (gate firewall)
    → periplasm (VPS relay, routing, telemetry, attribution)
      → outer membrane (VPS channels: Signal/Relay/Surface)
        → extracellular (public internet)
```

Two membrane boundaries with a periplasmic space between them.
Example: ironGate + VPS `membrane-relay` ([RELAY_PUBLIC]).

### Extended topologies

| Topology | Structure | Example |
|----------|-----------|---------|
| Monoderm | Cytoplasm → plasma → environment | Home lab: ironGate on LAN |
| Diderm | Cytoplasm → plasma → periplasm → outer → environment | Production: ironGate + VPS |
| Multi-diderm | Shared periplasm, multiple outer membranes | Future: `membrane-nyc` + `membrane-eu` |
| Nested diderm | One system's outer membrane = another's periplasm | University lab inside campus |

---

## Section 2: Absolute Envelope Layers

Five layers, ordered inside-out. Names are fixed and never relative.

| Layer | Position | What Occupies It | Bond Types Within |
|-------|----------|------------------|-------------------|
| **Cytoplasm** | Innermost | NUCLEUS processes, UDS IPC, shared memory | Covalent only |
| **Plasma membrane** | Gate boundary | Gate firewall (UFW/nftables) | Covalent, Metallic |
| **Periplasm** | Between plasma and outer | VPS relay, routing, telemetry, attribution | Ionic, Metallic |
| **Outer membrane** | VPS boundary | VPS channels (Signal/Relay/Surface) | Weak, Ionic |
| **Extracellular** | Outermost | Public internet | Weak |

**Invariant**: The VPS is ALWAYS in the periplasm + outer membrane position.
The gate ALWAYS owns the plasma membrane. These positions do not change
regardless of how many VPS nodes exist.

---

## Section 3: NUCLEUS Atomics in the Envelope

The particle model (Tower/Node/Nest/NUCLEUS) maps to envelope layers:

### Cytoplasm: Full NUCLEUS Interior

All 13 primals run in the cytoplasm on the gate. The atomic tiers define
capability groupings, not layer placement — all atomics share the
cytoplasmic space and communicate via UDS IPC (covalent bond).

| Atomic | Particle | Primals | Cytoplasm Role |
|--------|----------|---------|----------------|
| Tower | Electron | BearDog + Songbird + skunkBat | Security, federation, identity verification |
| Node | Proton | Tower + ToadStool + barraCuda + coralReef | Compute, sandboxing, GPU dispatch |
| Nest | Neutron | Tower + NestGate + rhizoCrypt + loamSpine + sweetGrass | Storage, provenance, attribution, certificates |
| NUCLEUS | Atom | Tower + Node + Nest (9 unique primals) | Complete sovereign composition |
| Meta-tier | Cross-atomic | biomeOS + Squirrel + petalTongue | Orchestration, AI, interface |

### Plasma Membrane: Tower Mediates All Boundary Crossings

The Tower atomic (electron shell) mediates all traffic crossing the plasma
membrane. BearDog authenticates, Songbird federates, skunkBat correlates.
No Node or Nest primal communicates directly with the periplasm — traffic
flows through Tower's capability surface.

```
cytoplasm [Node + Nest primals]
  → Tower primals (electron shell)
    → plasma membrane (gate firewall)
      → periplasm
```

### Periplasm: Routing, Attribution, Telemetry

The periplasm contains VPS-side processes that route, classify, and
attribute traffic between the plasma membrane (gate) and the outer
membrane (public-facing channels):

| Periplasm Process | Source Primal | Function |
|-------------------|--------------|----------|
| Songbird TURN relay | Songbird | NAT traversal, cross-gate federation |
| RustDesk relay | skunkBat | Remote desktop bridge |
| Content routing | NestGate (via config) | `routing_config.toml` dispatch |
| Telemetry/shadow | skunkBat | Shadow validation, latency comparison |
| Braid verification | sweetGrass (via policy) | Provenance attribution at boundary |
| BTSP token validation | BearDog | Scoped ionic token verification |

### Outer Membrane: Three Channels to the Extracellular

The outer membrane exposes exactly three channels to the internet,
corresponding to the membrane channel architecture:

| Channel | Port/Protocol | What Crosses | Bond Type |
|---------|---------------|--------------|-----------|
| **Signal** | :443 (Caddy/HTTPS) | Signed content, verified provenance | Ionic |
| **Relay** | :3478 (TURN) | Songbird federation, NAT traversal | Ionic → Covalent (once authenticated) |
| **Surface** | :21115-21116 (RustDesk) | Remote desktop sessions | Weak → Ionic (on session auth) |

### Extracellular: Dark Forest

The public internet. All traffic arriving from the extracellular space is
treated as **Weak** bond until authenticated. The Dark Forest principle
applies: assume hostile intent until proven otherwise.

---

## Section 4: Bonding at Each Envelope Layer

The organo-metallo-salt bonding model maps to envelope positions.
Each layer boundary has specific bond types that may cross it.

| Envelope Layer | Bond Types Crossing | Channel Protein | Braid Policy | What Crosses | What Does NOT Cross |
|----------------|---------------------|-----------------|--------------|--------------|---------------------|
| Outer membrane → environment | Weak, Ionic | Passive diffusion, Gated ion | Block | Public content, scoped API tokens | Family seed, braid internals, dag.* |
| Periplasm (routing) | Ionic, Metallic | Gated ion, Aquaporin | Verify | Classified requests, telemetry, relay | Raw covalent RPC, FAMILY_SEED |
| Plasma membrane (gate) | Covalent, Metallic | Aquaporin | Pass-through | Full capability, braid, workloads | Nothing blocked within family |
| Cytoplasm (NUCLEUS) | Covalent only | Aquaporin | Pass-through | UDS IPC, shared memory | (everything stays) |

### Channel Proteins

| Channel Protein | Mediates Bond | Behavior |
|-----------------|---------------|----------|
| **Aquaporin** | Covalent, Metallic | Always open — shared family seed, free-flowing |
| **Gated ion** | Ionic | BTSP scoped token opens the gate, method-level filtering |
| **Voltage-gated** | Ceremony | Time-bound decay: covalent → ionic → weak over time |
| **Passive diffusion** | Weak | Read-only, no active transport |

### Braid Policy Per Layer

Braid (sweetGrass provenance attribution) is the vesicle coat:

| Policy | Layer | Behavior |
|--------|-------|----------|
| **Pass-through** | Cytoplasm, Plasma membrane | Braid passes without inspection (covalent/metallic) |
| **Verify** | Periplasm | Braid metadata verified at boundary (ionic) |
| **Block** | Outer membrane, Extracellular | Braid stripped — only results cross, not provenance (weak) |

---

## Section 5: Franklin's Current Resolution

### The Problem

Three gen4 documents use conflicting inner/outer labels:

| Document | "Inner membrane" | "Outer membrane" |
|----------|------------------|------------------|
| `SOVEREIGN_HPC_EVOLUTION.md` | Gate firewall | VPS channels |
| `CELLMEMBRANE_FIELDMOUSE_ARCHITECTURE.md` | VPS relay | GitHub/CDN |
| `CELLMEMBRANE_ARCHITECTURE.md` | (avoided) | (avoided) |

This is the Franklin's Current problem: two valid reference frames
produce opposite labels for the same component, like conventional current
vs electron flow. The gram-positive/gram-negative labels compound it —
they encode a staining technique, not architecture.

### The Resolution

K-Derm replaces all relative labels with absolute positions:

| Old Term | K-Derm Canonical Term | Why |
|----------|----------------------|-----|
| "inner membrane" (SOVEREIGN_HPC) | Plasma membrane | Always the gate boundary |
| "outer membrane" (SOVEREIGN_HPC) | Outer membrane | Correct — VPS channels facing internet |
| "inner membrane" (FIELDMOUSE) | Periplasm + outer membrane | Was using "inner" relative to GitHub |
| "gram-negative" | Diderm | Describes structure, not staining artifact |
| "gram-positive" | Monoderm | Same |
| "cell wall" | (no equivalent) | Substrate provider; not a membrane layer |

Old documents are **fossil record** — they are not modified. This standard
is canonical; old terms are referenced with this reconciliation table.

---

## Section 6: K-Derm Extensions Beyond Biology

### 6a: Recursive Nesting (Organelle Membranes)

Every administrative domain (lab, department, campus, consortium) is its
own K-Derm system, and they nest recursively:

```
Consortium (outer membrane)
  → consortium periplasm (federated routing)
    → University (outer membrane)
      → campus periplasm (campus routing, bonding classification)
        → Lab (plasma membrane)
          → lab cytoplasm (covalent HPC mesh)
            → HPC organelle (own double membrane: scheduler + compute pool)
```

Each level is a self-contained envelope. Bonding model at each boundary
is independently configured.

### 6b: Endosymbiosis (Sovereignty Escalation)

Infrastructure absorption mirrors mitochondrial endosymbiosis:

| Phase | Bond | Topology | Biological Parallel |
|-------|------|----------|---------------------|
| 1 (External) | Weak | Separate organism | Free-living bacterium |
| 2 (Contract) | Ionic | Symbiotic, own membrane | Early symbiont |
| 3 (Fleet) | Metallic | Delocalized, specialized | Proto-mitochondrion |
| 4 (Internalized) | Covalent | Membrane becomes host layer | Mitochondrion |

The external system's outer membrane *becomes* a layer in the host's
envelope. The boundary transforms from a trust barrier into a functional
compartment.

### 6c: Vesicle Transport (Braid as Membrane Coat)

Workloads wrapped in sweetGrass braid carry provenance attribution that
acts as a SNARE-protein targeting signal:

1. **Budding**: Workload originates. sweetGrass creates braid wrapping
   DAG session + data references + attribution chain.
2. **Periplasm transit**: Braid-wrapped workload traverses periplasm.
   Routing reads braid metadata to classify bonding type and destination.
3. **Fusion**: Target membrane accepts the vesicle because braid proves
   data alignment — DAG references verified via rhizoCrypt, attribution
   chain intact, ionic contract authorizes compute.
4. **Content release**: Inside the target compartment, braid is verified
   and the workload executes.

Pre-braided workloads cross faster because the membrane doesn't need to
verify provenance from scratch (facilitated diffusion).

---

## Section 7: BTSP Cipher Mapping

K-Derm layers align with BTSP cipher enforcement from `BTSP_PROTOCOL_STANDARD.md`:

| Envelope Layer | Trust Model | Minimum Cipher | Negotiable |
|----------------|-------------|----------------|------------|
| Cytoplasm | Covalent (GeneticLineage) | `BTSP_NULL` | All three allowed |
| Plasma membrane | Covalent + Metallic | `BTSP_HMAC_PLAIN` | Down to `BTSP_NULL` for same-family |
| Periplasm | Ionic + Metallic | `BTSP_CHACHA20_POLY1305` | None — encrypted only |
| Outer membrane | Ionic + Weak | `BTSP_CHACHA20_POLY1305` | None — encrypted only |
| Extracellular | Weak (ZeroTrust) | TLS 1.3 (external) | No BTSP — HTTPS only |

**OrganoMetalSalt** composite bonds span multiple layers: covalent core
(cytoplasm) → metallic fleet (plasma + periplasm) → ionic edge (outer).
The BTSP cipher follows the weakest boundary crossed.

---

## Section 8: Typed Interface

The K-Derm model is encoded in `cellmembrane-types` (`envelope.rs`):

| Type | Encodes | Key Methods |
|------|---------|-------------|
| `EnvelopeTopology` | Monoderm / Diderm | `layers()`, `boundary_count()`, `has_periplasm()` |
| `EnvelopeLayer` | Cytoplasm / Plasma / Periplasm / Outer / Extracellular | `is_boundary()`, `is_compartment()`, `permitted_inbound_bonds()` |
| `BondType` | Covalent / Metallic / Ionic / Ceremony / Weak | `channel_protein()` |
| `ChannelProtein` | Aquaporin / GatedIon / VoltageGated / PassiveDiffusion | `permitted_bonds()` |
| `BraidPolicy` | PassThrough / Verify / Block | `for_bond()` |
| `BoundaryPolicy` | Per-layer composite policy | `for_layer()`, `permits_bond()`, `has_channel_protein()` |
| `MembraneConfig.topology` | Configuration field | `effective_topology()` |

Deploy graphs reference these types in `[graph.bonding_policy]` sections:
`tower_internal = "covalent"`, `cross_family = "ionic"`, `public_edge = "weak"`.

---

## Section 9: Validation

### primalSpring validation (planned)

| Scenario | Validates |
|----------|-----------|
| `s_kderm_boundary` | Deploy graph `bonding_policy` matches K-Derm layer rules |
| `s_atomic_compositions` (existing) | Composition graph primals placed in correct atomic tiers |
| `s_sovereignty_parity` (existing) | `routing_config_reference.toml` backend types match K-Derm bonding |

### cellMembrane validation (existing)

`cellmembrane-types/tests/envelope.rs` — 27 tests covering:
- Monoderm has 3 layers, Diderm has 5 layers
- Boundary count derivation
- Permitted inbound bonds per layer
- Channel protein ↔ bond type mapping
- Braid policy defaults
- BoundaryPolicy assembly from layer capabilities
- Serde round-trip for all K-Derm types

### benchScale integration

`topologies/nucleus/kderm_diderm_membrane.yaml` — 5-node boundary
crossing validation in reproducible test environments.

---

## Cross-References

| Document | Location | Relationship |
|----------|----------|--------------|
| K-Derm canonical spec | `gardens/cellMembrane/specs/K_DERM_TOPOLOGY.md` | Source of truth |
| Bonding model standard | `wateringHole/BONDING_MODEL_STANDARD.md` | Bond types + BTSP ciphers |
| Sovereignty standards | `wateringHole/SOVEREIGNTY_STANDARDS.md` | Trust layers (pre-K-Derm vocabulary) |
| BTSP protocol | `wateringHole/BTSP_PROTOCOL_STANDARD.md` | Cipher enforcement per bond type |
| NUCLEUS spring alignment | `wateringHole/GATE_SPRING_OWNERSHIP.md` | Atomic model + genetics |
| Membrane channels | `wateringHole/MEMBRANE_CHANNEL_ARCHITECTURE.md` | Three-channel architecture |
| cellMembrane architecture | `gardens/cellMembrane/specs/CELLMEMBRANE_ARCHITECTURE.md` | Operational membrane model |
| K-NOME methodology | `infra/whitePaper/gen3/about/K_NOME_PROGRAMMING.md` | Parallel methodology |
| gen4 reconciliation | `infra/whitePaper/gen4/architecture/K_DERM_RECONCILIATION.md` | Bridges gen4 gram-negative → K-Derm |
| Envelope types | `gardens/cellMembrane/crates/cellmembrane-types/src/envelope.rs` | Rust implementation |

---

## FILE: `foundations/LICENSING_AND_COPYLEFT.md`

# Licensing and Copyleft — scyBorg Framework

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | April 4, 2026 |
| **Status** | Active |

This document consolidates the lysogeny copyleft strategy, the scyBorg triple-license standard (including the provenance trio), and the symbiotic exception protocol. Source materials: `LYSOGENY_PROTOCOL.md`, `SCYBORG_PROVENANCE_TRIO_GUIDANCE.md`, `SCYBORG_EXCEPTION_PROTOCOL.md`.

---

## Philosophy

**Lysogeny** is the ecoPrimals strategy for permanently opening proprietary technology gates by combining documented prior art, cross-domain validation, independent implementation, and **AGPL-3.0-or-later** copyleft. The name analogizes to lysogenic phage biology: copyleft integrates into derivatives and, when adoption occurs, forces openness. Lysogeny is **area denial**, not siege: it does not attack existing proprietary deployments; it reduces the addressable market for proprietary expansion by publishing a free, AGPL-protected alternative backed by prior art and generality proofs.

### Copyleft strategy in brief

1. Identify a proprietary gate (algorithm, platform, or system restricting access).
2. Trace underlying mathematics to **published open research** (prior art).
3. Implement from first principles under **AGPL-3.0-or-later**.
4. Cross-validate across domains (proves generality, not domain-specific IP).
5. Document the **provenance chain** (seven links; see below).
6. Publish and wait; adoption propagates copyleft and weakens proprietary claims on the math.

### Three layers of protection (all required)

Every lysogeny target must satisfy all three; omission weakens legal defensibility.

| Layer | Role | Standard |
|-------|------|----------|
| **Prior art** | Math exists in published, peer-reviewed literature predating the proprietary implementation. | Citations with author, journal, year, page; publication must **predate** the proprietary patent filing (if patented) or first public release (if trade-secreted). |
| **Cross-domain generality** | Same mathematics validated in at least two distinct domains. | At least one cross-domain validation with passing checks in a domain unrelated to the proprietary system’s market. |
| **Independent derivation** | Implementation derives only from published research. | Every source file traceable to published citations only; no proprietary code, assets, documentation, APIs, or reverse-engineering in implementation, comments, or docs. |

**Prior art research (minimums):** at least three independent citations per core algorithm; all pre-patent/pre-release; cross-reference fields; catalog the chain.

**Cross-domain validation:** same barraCuda primitive in both domains; vocabulary mapping (domain A ↔ domain B); independent checks (not a shared test harness). May be one spring, a partner spring, or both.

### Provenance chain (seven links)

1. Published paper (pre-patent) describing the mathematical model.  
2. barraCuda primitive implementing the model (or spring-local with absorption path).  
3. Spring experiment applying the math in the target domain.  
4. Cross-domain experiment validating the same math in another domain.  
5. Vocabulary mapping table proving generality.  
6. **AGPL-3.0-or-later** on all code.  
7. wateringHole documentation (catalog entry + handoff).

Links 1–5 support the three protection layers; link 6 is the copyleft mechanism; link 7 is ecosystem coordination.

### Relationship to scyBorg

Lysogeny operates **inside** the scyBorg framework. Lysogeny’s AGPL requirement is one layer of scyBorg; mechanics and creative outputs from the process also fall under **ORC** and **CC-BY-SA 4.0** as applicable. See **The scyBorg Framework** below.

### Area denial model (summary)

The proprietary vendor’s installed base is largely untouched; lysogeny targets **prospective** customers and new markets where an AGPL alternative with prior art and cross-domain proof reduces proprietary growth. The AGPL propagates through derivatives; documented prior art and generality weaken domain-specific IP arguments.

### Implementation norms (lysogeny targets)

Targets are implemented **only** from published math: **AGPL-3.0-or-later** license header on every file; **Pure Rust** with `#![forbid(unsafe_code)]` where applicable; use barraCuda primitives when available; **hotSpring-style** validation (hardcoded expected values, exit code 0/1); source files under **1000 lines**; **no TODO/FIXME/HACK** in shipping source. Catalog entries live under the spring’s `specs/` directory; handoffs go to **wateringHole** for ecosystem visibility.

---

## The scyBorg Framework

**scyBorg** is the ecoPrimals **triple-copyleft** licensing standard. It applies to every primal, spring, experiment, tool, and derivative work unless a **symbiotic exception** (see below) explicitly covers author-owned contributions for a named grantee.

### Formula and layers

```
scyBorg = AGPL-3.0 (code) + ORC (game mechanics) + CC-BY-SA 4.0 (creative content)
```

| Layer | License | Covers | Governing body |
|-------|---------|--------|----------------|
| Software | **AGPL-3.0-or-later** | Engine, tools, shaders, math, infrastructure | FSF (nonprofit) |
| Mechanics | **ORC** | Rules, stat blocks, progression, encounter math | Open RPG Creative Foundation (nonprofit) |
| Creative | **CC-BY-SA 4.0** | Art, worlds, narrative, characters, music, sound, maps, papers, docs | Creative Commons (nonprofit) |
| Reserved | **ORC Reserved Material** | Studio-specific branding, trademarks, trade dress | Creator retains |

No single entity can unilaterally revoke these license regimes; governance is structural (independent nonprofits), not contractual opt-in.

### AGPL-3.0-or-later (all code)

Applies to Rust sources, WGSL, build scripts, configs, tests, experiments, and tools across listed primals and springs (e.g. BearDog, barraCuda, coralReef, rhizoCrypt, sweetGrass, loamSpine, skunkBat, ludoSpring, wetSpring, hotSpring, and future components). Implications include: derivatives must be **AGPL-3.0-or-later**; **network use** triggers distribution obligations; SaaS wrappers around ecoPrimals code must release source.

### ORC (game mechanics)

ORC Licensed Material covers game rules, stat blocks, progression systems, encounter math, and mechanical designs. **ORC is irrevocable and perpetual** for licensed material.

### CC-BY-SA 4.0 (creative content)

Non-code creative output requires **attribution**; **share-alike** propagates to derivatives.

### Reserved material

Branding, primal names, logos, and related trade dress remain under **ORC Reserved Material** and do not restrict code or mechanics under the other layers.

### Why three layers

A single license cannot cover code, game rules, and creative works simultaneously; scyBorg closes gaps so no major artifact class lacks copyleft-aligned terms.

### Defense in depth (ecosystem)

| Layer | Mechanism | Protects |
|-------|-----------|----------|
| Lysogeny | Prior art + independent derivation + cross-domain proof | Algorithms/math from proprietary patent/secret claims |
| scyBorg | AGPL + ORC + CC-BY-SA | Code, mechanics, creative work from proprietary closure |
| Provenance trio | Machine-verifiable attribution and derivation | Evidentiary chain for violations |
| skunkBat | Network/runtime threat response | Runtime extraction patterns |

### Provenance trio (enforcement of scyBorg as evidence)

- **sweetGrass** — who created what (BY in CC-BY-SA).  
- **rhizoCrypt** — derivation chains (SA in CC-BY-SA).  
- **loamSpine** — immutable license certificates (proof that terms apply).

Together, they make scyBorg **machine-verifiable** and attributable; without them, scyBorg is primarily declarative in repository metadata.

### Content categories and machine-readable licenses

Artifacts should declare category: **Code** (AGPL-3.0-or-later), **GameMechanics** (ORC), **CreativeContent** (CC-BY-SA 4.0), **Reserved** (ORC Reserved Material). Use **SPDX** expressions where applicable (e.g. `AGPL-3.0-or-later`, `CC-BY-SA-4.0`). Derivation tracking supports share-alike evidence (rhizoCrypt DAG, license metadata on vertices, certificates in loamSpine).

### Non-goals (for trio implementation)

- Do **not** build automated license **enforcement** in place of law—the trio provides **evidence**; copyright and license terms remain the enforcement layer.  
- Do **not** build complex license compatibility checkers beyond the chosen non-conflicting stack.  
- Do **not** gate product functionality on license metadata fields.

### Cross-spring applicability

scyBorg applies universally: e.g. ludoSpring (game code + design specs), wetSpring (pipelines + models), hotSpring (simulations + reports), healthSpring (clinical tools + outcome documentation), etc.

### External references

- [AGPL-3.0](https://www.gnu.org/licenses/agpl-3.0.html)  
- [ORC License](https://azoralaw.com/orclicense/)  
- [CC-BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)  
- [SPDX License List](https://spdx.org/licenses/)

---

## Symbiotic Exceptions

A **symbiotic exception** grants **additional permissions** beyond default scyBorg (**AGPL-3.0 + ORC + CC-BY-SA 4.0**) to a **named** organization or project when **reciprocal benefit** exists. **Exceptions are not for sale**; they are license-as-diplomacy, not dual licensing for revenue.

### Legal basis

**AGPL-3.0 Section 7** allows **additional permissions** that supplement the license by excepting named conditions. The copyright holder may:

- Grant named organizations permission to use contributions under terms other than AGPL-3.0 for specified scope.  
- Limit scope to specific code, projects, or use cases.  
- Tie duration and revocability to the reciprocal relationship.

**Critical constraint:** Exceptions apply only to **code the author owns**. For forks of upstream AGPL projects, the exception covers **only the author’s original contributions**, never upstream code.

### Exception tiers

| Tier | Who | Default license | Exception | Reciprocal basis |
|------|-----|-----------------|-----------|------------------|
| **Public** | Everyone | Full scyBorg | None | Prior art, community, lysogeny |
| **Symbiotic** | Named orgs/projects | Full scyBorg | May incorporate **author’s** contributions under their **existing** license | Tools, hardware, knowledge |
| **Reciprocal Open** | Orgs opening their work | Full scyBorg | May incorporate under their license | They publish specs/docs/code under **AGPL or equivalent copyleft** |

**Public tier** is the constitutional baseline (full scyBorg for all); it cannot be weakened.

**Symbiotic tier** allows incorporation of author-original work under the partner’s license for covered scope; the **public scyBorg tree remains unchanged**; both forks may evolve in parallel.

**Reciprocal Open tier** rewards vendors who publish proprietary knowledge under AGPL or equivalent copyleft with strongest mutual benefit and precedent for future partners.

### Exception grant record (fields)

| Field | Purpose |
|-------|---------|
| **Grantee** | Named organization or project |
| **Scope** | Which ecoPrimals code/contributions are covered |
| **Terms** | What the grantee may do (e.g. incorporate into proprietary products) |
| **Reciprocal basis** | What ecoPrimals receives |
| **Duration** | Ongoing while reciprocity holds, or fixed term |
| **Sublicense** | Whether third-party sublicense (default: **no**) |
| **Revocability** | When the exception may end |

### What an exception does **not** grant

- Rights to **upstream** code (author-original only).  
- Rights to **relicense** the public scyBorg version.  
- Rights to **block** others from using the public AGPL version.  
- **Trademark**, branding, or **ecoPrimals name** rights.  
- **Exclusivity**—the same contribution remains available to everyone under AGPL.

### Candidate examples (not formalized as active grants)

| Candidate | Notes |
|-----------|--------|
| **RustDesk** | Partner AGPL-3.0; scope: ecoPrimals contributions to a fork; terms: incorporate under existing AGPL; reciprocal: remote access infrastructure. |
| **BrainChip (Akida)** | Scope: rustChip / Akida integration; terms: incorporate into proprietary products without AGPL on those contributions; reciprocal: hardware, docs, support; requires **100% author-owned** code. |
| **GPU vendor (Reciprocal Open)** | Scope: e.g. coralReef compiler; terms: vendor may incorporate improvements; reciprocal: architecture documentation under **AGPL-3.0 or equivalent copyleft**. |

### Process for granting an exception

1. Identify reciprocal value.  
2. Scope the exception (specific code/contributions).  
3. Verify **100% copyright ownership** of excepted code (no inappropriate upstream mixing).  
4. Draft grant: grantee, scope, terms, reciprocal basis, duration, sublicense, revocation.  
5. Publish in the **Exception Registry** (below).  
6. Notify the partner.  
7. Review annually whether reciprocity persists.

### Exception Registry

Active symbiotic exceptions are listed here when formalized. *As of consolidation, the registry was empty; first grants pending formalization.*

| # | Grantee | Scope | Tier | Status | Date |
|---|---------|-------|------|--------|------|
| — | — | — | — | — | — |

### Additional references

- [AGPL-3.0 Section 7](https://www.gnu.org/licenses/agpl-3.0.html#section7) (additional permissions)

---

## Version History

| Version | Date | Notes |
|---------|------|--------|
| **1.0.0** | April 4, 2026 | Initial consolidated document. Merges **Philosophy** and lysogeny lifecycle/provenance content from `LYSOGENY_PROTOCOL.md`; **The scyBorg Framework** and provenance trio from `SCYBORG_PROVENANCE_TRIO_GUIDANCE.md`; **Symbiotic Exceptions** (legal basis, tiers, scope, registry, process) from `SCYBORG_EXCEPTION_PROTOCOL.md`. Domain-specific lysogeny catalogs, implementation backlogs for sweetGrass/rhizoCrypt/loamSpine, and extended narrative sections are abbreviated here; refer to the original files for full tables and phased engineering detail. |

---

## FILE: `foundations/OVERWATCH_POSITION_STANDARD.md`

# Overwatch Position Standard

**Authority**: Ecosystem convention  
**Status**: Active (Wave 75)  
**Prerequisites**: `ECOSYSTEM_COMMUNICATION_STANDARD.md`, `GATE_TEAM_COORDINATION_MATRIX.md`

---

## What Overwatch Is

Overwatch is the **active coordination role** for the ecosystem. It maintains
strategic awareness across all gates and teams, composes the three communication
artifacts (handoffs, FRAGOs, blurbs), tracks glacial progress, and guides the
ecosystem toward long-term goals.

Overwatch is **a position, not an identity**. It is not a gate. It is not a
primal. It is not a specific IDE session. It is a role that floats to wherever
the user is actively coordinating.

---

## What Overwatch Is Not

- **Not a fixed team**: Overwatch does not own code. It does not write Rust. It
  does not implement scenarios or fix bugs. Those are evolution teams.
- **Not a gate**: Overwatch currently operates from eastGate, but it could
  operate from any gate that has wateringHole access and cascade connectivity.
- **Not a primal**: primalSpring has an overwatch chat and an evolution chat.
  The overwatch chat coordinates. The evolution chat builds.
- **Not permanent**: If the user switches to ironGate and starts coordinating
  from there, ironGate becomes overwatch. The role follows the user.

---

## What Overwatch Does

### Core Functions

| Function | Artifact | Frequency |
|----------|----------|-----------|
| **Cascade and review** | Reads handoffs + impulses | Every sync cycle |
| **Compose blurbs** | Writes blurbs | Per wave or on demand |
| **Fire FRAGOs** | Writes impulses | When coordination needed |
| **Update readiness** | Edits GLACIAL_SHIFT_READINESS.md | After absorbing deliveries |
| **Update remaining work** | Edits WAVE*_REMAINING_WORK.md | After absorbing deliveries |
| **Update matrix** | Edits GATE_TEAM_COORDINATION_MATRIX.md | After state changes |
| **Archive completed work** | Moves handoffs/impulses to archive/ | Per wave |
| **Write gen5 papers** | Writes whitePaper/gen5/ | When achievements warrant |
| **Strategic guidance** | Identifies critical path, priorities | Continuous |

### The Overwatch Cycle

```
1. CASCADE          membrane temporal.cascade
                    ├── Pull evolution from all gates
                    └── Identify what changed (commits, handoffs, impulses)

2. ABSORB           Read new handoffs and impulse ACKs
                    ├── Understand what each team delivered
                    ├── Identify blockers, gaps, achievements
                    └── Update mental model of ecosystem state

3. UPDATE           Refresh coordination documents
                    ├── GLACIAL_SHIFT_READINESS.md
                    ├── WAVE*_REMAINING_WORK.md
                    ├── GATE_TEAM_COORDINATION_MATRIX.md
                    └── Archive completed handoffs/impulses

4. DIRECT           Compose artifacts for next cycle
                    ├── FRAGOs for gates that need to act
                    ├── Blurbs for teams that need context
                    └── Gen5 papers for achievements worth documenting

5. PUSH             Commit and cascade out
                    ├── git push wateringHole (origin + forgejo)
                    └── Teams pull on next cascade
```

---

## How Overwatch Floats

The overwatch position moves based on **where the user is actively coordinating**.
This is enabled by the ecosystem's sovereign infrastructure:

### Prerequisites for Overwatch Capability

Any gate/chat/session can run overwatch if it has:

1. **wateringHole access** — read/write to the coordination repository
2. **Cascade connectivity** — can run `membrane temporal.cascade` to sync
3. **Ecosystem manifest** — knows the full gate topology
4. **User presence** — the user is actively working in this session

### Movement Patterns

| Pattern | Example | What Happens |
|---------|---------|--------------|
| **Primary overwatch** | primalSpring on eastGate | Default coordination position. User's main strategic session. |
| **Gate-local overwatch** | cellMembrane on ironGate | User is debugging VPS. ironGate session takes overwatch for infrastructure decisions. |
| **Sprint overwatch** | biomeOS on southGate | User is driving a biomeOS sprint. southGate session coordinates dependencies. |
| **Distributed overwatch** | Multiple chats | User has parallel sessions. Each owns its domain's coordination. primalSpring remains strategic. |

### The User Is the Binding

Overwatch doesn't float autonomously. It follows the **user's attention**. When
the user opens a session and says "cascade and review," that session becomes
overwatch for the duration of the interaction. The artifacts (wateringHole docs,
FRAGOs, blurbs) are what persist across sessions — they are the continuity,
not the chat.

---

## How Sovereignty Enables Overwatch

The overwatch position is fundamentally enabled by the ecosystem's sovereign
infrastructure layers. Without sovereignty, overwatch depends on commercial
services and cannot truly float.

### Layer 1: wateringHole (Git-based SSOT)

All coordination state lives in `wateringHole/` — a git repository that
every gate can read and write. No Slack, no Jira, no external service.
The overwatch position's artifacts are git commits, not SaaS database rows.

**Implication**: Any gate that can `git pull wateringHole` can read the full
coordination history. Any gate that can `git push` can update it. Overwatch
is not locked to a single machine or service.

### Layer 2: waterFall Cascade (Sovereign Sync)

`membrane temporal.cascade` propagates state across all gates through the
Forgejo-primary push chain. No GitHub Actions, no webhooks on commercial
infrastructure. The cascade is the overwatch's primary sensing mechanism.

**Implication**: Overwatch sees all evolution through cascade pulls. It
doesn't need access to individual gate sessions — it reads what teams
committed.

### Layer 3: K-Derm Diderm Envelope (Sovereign Relay)

The three-node VPS envelope (golgiBody / peptidoglycan / golgiBody-ext)
provides the relay infrastructure for cross-gate coordination. Gates push
to Forgejo (inner membrane), peptidoglycan mediates, golgiBody-ext ships
to external.

**Implication**: Overwatch can coordinate gates that aren't on the same LAN.
flockGate (WAN) receives FRAGOs and handoffs through the same relay chain
as LAN gates.

### Layer 4: Songbird Mesh (Sovereign Discovery)

The covalent mesh enables real-time discovery of gate state. `discovery.peers`
shows which gates are online. `mesh.health_check` confirms connectivity.
Overwatch uses this to understand operational topology, not just code state.

**Implication**: Overwatch can assess which gates are available for work
assignment, which are offline (biomeGate), and which are joining (westGate).

### Layer 5: bearDog BTSP (Sovereign Trust)

bearDog's BTSP protocol provides the trust layer that makes cross-gate
coordination secure. When overwatch fires a FRAGO, the receiving gate can
verify the impulse came from a trusted source.

**Implication**: As BTSP cross-gate validation matures, FRAGOs can be
cryptographically signed and verified, making overwatch coordination
tamper-evident.

---

## Overwatch vs Evolution Teams

| Aspect | Overwatch | Evolution Team |
|--------|-----------|---------------|
| **Writes** | Handoffs, FRAGOs, blurbs, readiness docs, gen5 papers | Code, tests, experiments, crate logic |
| **Reads** | Everything — all repos, all handoffs, all commits | Primarily their own primal + wateringHole |
| **Decides** | Strategic priorities, critical path, gate assignments | Implementation approach, architecture, test strategy |
| **Produces** | Coordination artifacts | Commits, handoffs (per sprint) |
| **Persists across** | Waves, sessions, gates | One sprint/session |
| **Identity** | Floating — wherever the user coordinates | Fixed — the primal they build |

### The Parallel Chat Pattern

The user typically runs two chats per active workstation:

1. **Overwatch chat**: Cascades, reviews, composes blurbs, files FRAGOs,
   maintains readiness docs. Sees the whole ecosystem. Talks to the user
   about strategy.

2. **Evolution chat**: Receives a blurb, reads the codebase, builds and
   tests code, writes handoffs. Sees one primal deeply. Talks to the user
   about implementation.

The user is the bridge. They paste blurbs from overwatch to evolution.
They relay handoffs from evolution back to overwatch (via cascade). The
two chats never talk directly — they communicate through the three artifacts.

---

## Blurb Composition Rules (Overwatch Perspective)

When overwatch composes blurbs:

1. **One blurb per primal team** — not per gate. If strandGate runs
   toadStool, barraCuda, and coralReef, that's three blurbs.

2. **Blurbs are orders to other teams** — they describe what the team
   should do, not what overwatch will do. "Your Mission" is their work.

3. **Overwatch doesn't blurb itself** — the coordination work (cascades,
   doc updates, blurb composition) is implicit in the overwatch role.
   It doesn't need a blurb because it's the one writing them.

4. **Every team gets forward work** — zero debt is the floor, not the
   ceiling. If a team has nothing assigned, overwatch finds them work.
   Evolution never stops.

5. **Blurbs reference FRAGOs** — if there's an active FRAGO for the
   team, the blurb mentions it. The blurb provides context; the FRAGO
   provides the directive.

---

## Future: Automated Overwatch

As the ecosystem matures, pieces of overwatch can be automated:

| Function | Manual (today) | Automated (future) |
|----------|----------------|---------------------|
| Cascade + review | Agent reads commits | `membrane potential.sense` → structured report |
| Blurb composition | Agent writes markdown | `membrane context.weave` → TOML braids |
| FRAGO filing | Agent writes TOML | Impulse auto-fires on criteria (e.g., test count regression) |
| Readiness update | Agent edits markdown | Machine-readable readiness.toml + auto-update on delivery |
| Archive management | Agent moves files | TTL-based auto-archive after ACK |

The human operator remains the strategic authority. Automation handles the
mechanical parts. The overwatch position evolves from "do everything" to
"approve and steer."

---

## Changelog

| Wave | Change |
|------|--------|
| 75 | Initial: formalized from implicit practice. Codifies floating nature, sovereignty enablement, parallel chat pattern, blurb composition rules. |

---

*"Overwatch is not where you sit. It's where you look from. The position
floats because the infrastructure is sovereign — any gate, any session,
any chat can see the whole and guide it forward."*

---

## FILE: `foundations/PRIMAL_SPRING_GARDEN_TAXONOMY.md`

# Primal / Spring / Garden Taxonomy

**Purpose:** Authoritative reference for the three entity layers in the ecoPrimals
ecosystem — their roles, ownership boundaries, interaction contracts, and the
co-evolution loop that drives ecosystem progress.

**Last Updated:** May 12, 2026 (Added fossilRecord as ecosystem memory layer)

---

## The Three Layers

The ecoPrimals ecosystem is organized into three layers. Each layer has a
distinct role, and the boundaries between them are enforced by convention and
tooling (zero compile-time coupling, JSON-RPC IPC, wateringHole handoffs).

```
gen2: Primals        — capability providers (what the ecosystem CAN do)
gen3: Springs        — validation and evolution environments (proving it WORKS)
gen4: Gardens        — user-facing products (making it USEFUL)
     fossilRecord   — geological archive (HOW we got here)
```

| Layer | Directory / Repo | Role | Examples |
|-------|-----------------|------|----------|
| **Primal** (gen2) | `primals/` | Self-contained Rust binary providing domain primitives via IPC | BearDog, Songbird, barraCuda, biomeOS |
| **Spring** (gen3) | `springs/` | Validation environment: composes primals, validates science, surfaces gaps | ludoSpring, hotSpring, wetSpring, primalSpring |
| **Garden** (gen4) | `gardens/` | User-facing product: composes primals into tools people use | esotericWebb, blueFish, helixVision, initioChem |
| **fossilRecord** | `ecoPrimals/fossilRecord` | Canonical archive: superseded handoffs, closed audits, evolution history | 3,831+ documents from 10 sources |

---

## What Each Layer Owns

### Primals

A primal owns a **domain** and exposes its capabilities as **primitives**
via JSON-RPC IPC. Primals have self-knowledge only — they never import
another primal's code.

**Primals own:**
- Primitives (atomic domain operations)
- IPC surface (JSON-RPC method handlers)
- Health protocol (`health.liveness`, `health.readiness`, `health.check`)
- Capability registration with biomeOS
- The canonical implementation of their domain's math/logic

**Primals do NOT own:**
- Validation of their own correctness in composition (that's a spring's job)
- User experience (that's a garden's job)
- Cross-domain coordination patterns (that's biomeOS + wateringHole)

### Springs

A spring is a **validation and evolution environment**. It composes primals
and validates that their composition solves real scientific or engineering
problems. Springs are where gaps in primals are discovered and fed back
to the ecosystem.

**Springs own:**
- Numbered experiments with counted checks
- Deploy graphs (TOML) for the compositions they validate
- `ValidationHarness` / `ValidationResult` with pass/fail/skip exit codes
- Science baselines (Python → Rust parity, published paper reproduction)
- Gap discovery and wateringHole handoff authorship
- Faculty anchors (academic publications driving the science)

**Springs do NOT own:**
- User-facing products or interfaces
- Primal source code (zero compile-time coupling)
- The definitive implementation of any primitive (that's the primal's job)

**Evolution pipeline:**
```
Python baseline → Rust validation → barraCuda CPU → barraCuda GPU
→ fused TensorSession → sovereign dispatch → primal composition
→ ecosystem co-evolution
```

### Gardens

A garden is a **user-facing product** that composes primals into tools
people actually use. Gardens follow the BYOB model (Bring Your Own
Binaries), consuming pre-built primal binaries from plasmidBin.

**Gardens own:**
- User experience and product design
- `PrimalBridge` (JSON-RPC client wrapping capability calls)
- Graceful degradation when optional primals are absent
- Product-level deploy graphs and niche YAML
- Domain-specific composition logic

**Gardens do NOT own:**
- Primal source code
- Validation of primal correctness (they surface usability gaps, not bugs)
- Science baselines or experiments

---

## Interaction Contracts

### Primal → Spring

Springs consume primal IPC to validate correctness. Every spring call to a
primal is honest: if the primal isn't running, the check is **skipped**
(exit 2), not faked.

- Springs call primal methods via JSON-RPC (discovered by capability)
- Springs validate return values against known baselines
- Springs report pass/fail/skip with provenance
- Springs surface gaps as wateringHole handoffs

### Primal → Garden

Gardens consume primals via BYOB/plasmidBin. They never see primal source.
When a primal is absent, gardens **degrade gracefully** — the product
continues with reduced functionality.

- Gardens call primal methods via `PrimalBridge`
- Gardens handle `ConnectionRefused` / timeout as non-fatal
- Gardens surface usability gaps (not correctness bugs)

### Spring → Primal (Co-evolution Loop)

This is the primary feedback mechanism driving ecosystem improvement:

```
Spring validates composition
→ discovers gap (missing method, wrong tolerance, protocol mismatch)
→ files wateringHole handoff with gap details
→ primal team evolves primitive
→ tags release → plasmidBin
→ spring re-validates → gap resolved (or new gap surfaces)
```

### Garden → Spring

Gardens surface usability gaps that springs then validate for feasibility:

```
Garden discovers usability gap (e.g. missing session lifecycle)
→ files EVOLUTION_GAPS.md or wateringHole handoff
→ spring validates whether the gap is solvable with existing primals
→ if yes: spring experiments demonstrate the solution
→ if no: spring surfaces the underlying primal gap upstream
```

### Spring ↔ Spring

Springs **never import each other**. They coordinate exclusively through:

- wateringHole handoffs
- Shared barraCuda primitives (both consume the same math)
- primalSpring deploy graph patterns (templates and conventions)
- Cross-spring experiment references in baseCamp

---

## The Co-Evolution Loop

This is the cycle that makes the ecosystem self-improving:

```
┌─────────────────────────────────────────────────┐
│  Spring or Garden discovers a gap                │
│  (missing method, protocol mismatch, tolerance)  │
└──────────────────┬──────────────────────────────┘
                   ▼
┌──────────────────────────────────────────────────┐
│  wateringHole handoff filed                       │
│  (gap details, reproduction steps, proposed fix)  │
└──────────────────┬───────────────────────────────┘
                   ▼
┌──────────────────────────────────────────────────┐
│  Primal team evolves the primitive                │
│  (new method, fixed tolerance, protocol update)   │
└──────────────────┬───────────────────────────────┘
                   ▼
┌──────────────────────────────────────────────────┐
│  Release tagged → plasmidBin updated              │
└──────────────────┬───────────────────────────────┘
                   ▼
┌──────────────────────────────────────────────────┐
│  Spring re-validates composition                  │
│  Garden re-composes with updated binary           │
│  → gap resolved OR new gap surfaces → loop        │
└──────────────────────────────────────────────────┘
```

**Communication channel:** wateringHole handoffs are the sole structured
coordination mechanism between layers. No layer directly modifies another
layer's code.

---

## Tools (gen2.5)

Between primals and gardens, the ecosystem has a class of entities that are
**standalone Rust crates or binaries consumed by primals, springs, or infrastructure**.
They are not long-running IPC services (no sockets, no health endpoints, no capability
registration) and they are not end-user products. They solve bounded problem domains
without the full IPC/discovery surface that primals carry.

```
gen2:   Primals — capability providers (IPC daemons)
gen2.5: Tools   — domain crates / CLIs consumed by other layers
gen3:   Springs — validation environments
gen4:   Gardens — user-facing products
```

| Tool | Location | Domain | Role |
|------|----------|--------|------|
| **bingoCube** | `primals/` | Crypto commitment | Human-verifiable visual/audio patterns from BLAKE3 + ChaCha20 boards. Nautilus reservoir computing. |
| **benchScale** | `infra/` | Lab substrate | Pure Rust VM provisioning and distributed system testing harness. |
| **agentReagents** | `infra/` | VM image builder | Template-driven VM images for gate provisioning. Depends on benchScale. |
| **rustChip** | `sort-after/` | NPU characterization | BrainChip Akida register-level driver, models, and benchmarks. Extracted from toadStool metalForge. |
| **sourDough** | `primals/` | Scaffolding / Meta | Scaffolds new primals with ecosystem DNA. CLI tool, not a daemon. |

**What applies to tools:** Tier 1 (Build Quality), Tier 6 (Responsibility), Tier 7 (Workspace
Dependencies), Tier 8 (Presentation). Same code quality bar as primals.

**What does not apply:** Tier 2 (UniBin — no daemon), Tier 3 (IPC — no sockets), Tier 4
(Discovery — no registration), Tier 5 (Semantic Naming — no RPC methods), Tier 9
(Deployment/Mobile — no binary distribution).

**Where they live:** `primals/` when consumed as Rust crate deps by primals; `infra/` when
infrastructure-only. The boundary is grey and evolves with the ecosystem.

**Tools own:**
- A bounded domain implementation (math, hardware interface, template engine, etc.)
- Their own test suite and quality gates
- README, CHANGELOG, CONTEXT.md, deny.toml (same surface as primals)

**Tools do NOT own:**
- IPC surface or health protocols
- Capability registration with biomeOS
- User experience or product interfaces

---

## Key Distinctions

| Aspect | Springs | Gardens |
|--------|---------|---------|
| **Failure mode** | Honest pass/fail/skip exit codes (0/1/2) | Graceful degradation for users |
| **Deploy graphs** | For testing and validation | For production deployment |
| **State management** | `ValidationHarness` | `PrimalBridge` |
| **Gap type discovered** | Correctness bugs, protocol mismatches, missing capabilities | Usability gaps, UX issues, missing convenience methods |
| **Binary consumption** | Compile-time library link + IPC probe | BYOB from plasmidBin (pure IPC) |
| **Science** | Reproduces published papers, baseline parity | Exercises composed science in product context |

---

## Validated Pipeline (April 20, 2026)

The full NUCLEUS → Spring → Garden pipeline has been validated end-to-end:

```
NUCLEUS certification (primalSpring)
  guidestone: 84/86 (6 layers, 13 primals, 11 capabilities)
  exp094:     15/18 composition parity
  graphs:     17/17 deploy graphs parse clean
          ↓
Spring science validation (ludoSpring)
  Tier 1:     152/152 local math (no IPC)
  Tier 2:     18/19 tower, 3/6 barraCuda composition
  Tier 3:     30/31 full NUCLEUS composition, 11/11 pipeline
  Structural: 14/14 deploy graph tests
          ↓
Garden composition (esotericWebb)
  Product graphs: 8/8 valid TOML (Webb)
  Proto sketches: 7/7 valid (ludoSpring → Webb)
  IPC flows:      game.* ✓, visualization.* ✓, compute.* ✓
```

Each spring may produce its own garden. For example:
- ludoSpring → esotericWebb (CRPG composition)
- hotSpring → MILC results garden for physicists
- wetSpring → environmental sensor dashboard

The pattern is standard; the domain science differs.

---

## How to Read Other Documents

- **GLOSSARY.md**: Definitions of all ecosystem terms including Primal, Spring, Garden
- **COMPOSITION_PATTERNS.md**: Deploy graph formats, socket discovery, niche YAML
- **SPOREGARDEN_DEPLOYMENT_STANDARD.md**: BYOB model for gardens
- **SPRING_INTEROP_LESSONS.md**: Practical interop learnings from the first compositions
- **PRIMALSPRING_COMPOSITION_GUIDANCE.md**: primalSpring-specific composition capabilities

---

## FILE: `foundations/SECRETS_AND_SEEDS_STANDARD.md`

# Secrets and Seeds Standard

**Version:** 1.0.0  
**Date:** March 31, 2026  
**Status:** Active  

---

## Core Principle

**No static secrets in repositories.** Seeds, keys, tokens, and credentials are generated at runtime or build time — never committed to source. A published binary carries its own lineage seed derived during build, validated via guideStone, and traceable without exposing the generation material.

---

## Definitions

| Term | Meaning |
|------|---------|
| **Secret** | Any value whose exposure compromises security: private keys, API tokens, passwords, PEM material |
| **Seed** | A cryptographic or identity-bearing value used to derive keys, generate configurations, or establish lineage |
| **Lineage seed** | A build-time or init-time seed embedded in a binary or artifact that proves provenance without revealing generation material |
| **Tutorial seed** | A well-known, documented seed used in examples, showcases, and tests — clearly marked as non-production |

---

## Repository Rules

### MUST NOT commit

- Private keys (PEM, PKCS8, JWK private material)
- API keys or tokens (sk-ant, sk-proj, Bearer tokens with real values)
- Passwords or passphrases
- .env files with real credentials
- Family seeds, mito seeds, or any production identity material
- SSH keys, TLS certificates with private keys
- Cloud credentials (AWS, GCP, Cloudflare tokens)

### MUST commit (when applicable)

- Public keys and certificates (without private counterparts)
- Example/template configurations with placeholder values
- Tutorial seeds clearly marked `# TUTORIAL ONLY — DO NOT USE IN PRODUCTION`
- `.env.example` files with placeholder structure

### MAY commit

- Test fixtures using well-known constants (e.g. all-zeros, RFC test vectors)
- Demo keys generated specifically for showcase — documented as compromised-by-design

---

## Seed Generation Patterns

### Init-time (primal first run)

When a primal starts for the first time, it generates its identity material:

```rust
// Pattern: generate on first run, persist to runtime directory
let seed_path = runtime_dir.join("identity.seed");
if !seed_path.exists() {
    let seed = generate_cryptographic_seed();
    write_atomic(&seed_path, &seed)?;
}
```

Runtime directories: `$XDG_RUNTIME_DIR/<primal>/`, `~/.local/share/<primal>/`, or operator-configured path. Never under the source tree.

### Build-time (lineage embedding)

Released binaries carry a lineage seed derived during build:

```rust
// build.rs pattern
let build_seed = derive_lineage_seed(
    env!("CARGO_PKG_VERSION"),
    &git_commit_hash(),
    &build_timestamp(),
);
println!("cargo:rustc-env=LINEAGE_SEED={}", build_seed);
```

The lineage seed is:
- **Deterministic** given the same source + version + commit
- **Verifiable** via guideStone (the binary can prove its lineage)
- **Non-secret** — it proves provenance, not access

### Tutorial seeds (showcase / testing)

Primals should ship tutorial configurations that generate fresh seeds on first use:

```bash
# Good: generate at init
./primal init --tutorial

# Bad: static seed in repo
echo "seed=0xdeadbeef" > config.toml && git add config.toml
```

Tutorial mode should:
1. Generate ephemeral keys/seeds
2. Log that tutorial mode is active
3. Refuse to connect to production infrastructure
4. Self-document the generated material's location

---

## Binary Distribution (genomeBin / plasmidBin)

### Lineage validation chain

```
Source (git commit) → Build (lineage seed derived) → Binary (seed embedded)
                                                        ↓
                                                   guideStone validates
                                                        ↓
                                                   rhizoCrypt records DAG
                                                        ↓
                                                   loamSpine issues certificate
                                                        ↓
                                                   sweetGrass traces provenance
```

### What a released binary contains

- Embedded lineage seed (build-derived, non-secret)
- Version string and commit hash
- guideStone validation checksums for its own outputs
- Capability declarations (primalSpring)

### What a released binary does NOT contain

- Build-machine paths (see Build Cleanliness below)
- Private keys or signing material
- Network credentials or tokens
- User-specific configuration

---

## Build Cleanliness

### Problem

Rust binaries compiled in development environments embed host-specific paths through:
- Panic messages (`/home/username/...` in panic file paths)
- Debug info (DWARF sections)
- Procedural macro expansions
- Build script output

### Requirements for public binaries

1. **Strip debug info:** `strip = true` in `[profile.release]`
2. **Remap path prefix:** `rustflags = ["--remap-path-prefix=/home/builder=build"]` in `.cargo/config.toml`
3. **Verify with strings:** `strings binary | grep -i '/home/'` should return nothing
4. **CI builds preferred:** Build in ephemeral containers where host paths are generic

### .cargo/config.toml pattern for clean builds

```toml
[build]
rustflags = [
    "--remap-path-prefix", "/home/builder=build",
    "--remap-path-prefix", "/rustc/=rustc/",
]

[profile.release]
strip = true
lto = true
```

### Verification checklist

- [ ] `strings <binary> | grep '/home/'` returns empty
- [ ] `strings <binary> | grep 'eastgate\|strandgate\|southgate\|westgate\|northgate\|biomegate'` returns empty
- [ ] `strings <binary> | grep '192\.168\.'` returns empty (unless intentional LAN default)
- [ ] Binary size is reasonable for release profile (strip + LTO)

---

## Pre-Push Audit Patterns

Before making any repository public or pushing to public remotes:

```bash
# Current tree — no secrets
rg -g '!target/' -g '!.git/' 'BEGIN PRIVATE KEY|BEGIN RSA|sk-ant|sk-proj' .

# Current tree — no personal paths
rg -g '!target/' -g '!.git/' '/path/to/home|/path/to/home|/path/to/home|/path/to/home|/path/to/home|/path/to/home' .

# Git history — identity check (should be ecoPrimal <ecoPrimal@pm.me> only for ecoPrimals org)
git log --all --format='%an <%ae>' | sort -u
git log --all --format='%cn <%ce>' | sort -u

# Git history — secrets in any commit
git log --all --oneline -S "BEGIN PRIVATE KEY" -- | head -5
git log --all --oneline -S "sk-ant" -- | head -5

# Git history — personal paths in any commit
git log --all --oneline -S "/path/to/home" -- | head -5
git log --all --oneline -S "/path/to/home" -- | head -5
```

### Remediation tools

- **Current tree:** `sed`, `rg --replace`, manual edits
- **Git history:** `git filter-repo --blob-callback` for content, `git filter-repo --mailmap` for identities
- **Binary artifacts:** Rebuild from clean environment with path remapping

---

## Publication Identity Standard

### ecoPrimals organization repositories

- **Author/committer:** `ecoPrimal <ecoPrimal@pm.me>`
- **No machine-specific identities** in git metadata (no `user@hostname`, no ISP domains)
- **wateringHole exception:** Historical handoffs and fossilRecord may retain development-era identities as geological record; root standards documents must use canonical identity

### syntheticChemistry organization repositories

- Personal attribution acceptable — these are science-facing
- Author may use personal name where appropriate for academic context

### sporeGarden organization repositories

- Follow ecoPrimals identity standard

---

## Version History

| Version | Date | Notes |
|---------|------|-------|
| 1.0.0 | 2026-03-31 | Initial standard after Provenance Trio public release audit |

---

## FILE: `foundations/SOVEREIGNTY_STANDARDS.md`

<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Sovereignty Standards — Ecosystem Behaviors for Sovereign Evolution

**Date**: May 15, 2026 (updated Jul 7, 2026 — Wave 133d: sporePrint NUCLEUS on golgi, bearDog CryptoProvider blocker identified, WAN mesh overlay live)
**Status**: Active
**Authority**: WateringHole Consensus
**Audience**: All primals, all compositions, all deployments

---

## Purpose

This document defines the **standards and behaviors** that govern the
ecoPrimals ecosystem's progressive sovereignty evolution. Every primal,
composition, and deployment inherits these constraints. They are not
aspirational — they are enforced by validation tooling (darkforest,
benchScale, deploy graphs, composition validators).

---

## Core Principles

### 1. Stability First, Sovereignty Second

External services are **calibration instruments**, not enemies. Each
provides production-grade baselines (latency, availability, throughput,
error rates, security). No external dependency is removed until its
primal replacement **proves parity or superiority** under real load.

**Priority order** (from `SOVEREIGNTY_VALIDATION_PROTOCOL.md`):
1. **Stability / Security** — system stays up, data stays safe
2. **Sovereign solutions** — replace externals with primals
3. **Rust** — prefer Rust implementations for auditability
4. **Primal composition** — prefer composed primals over monoliths

### 2. Calibrate → Shadow → Cutover

Every sovereignty replacement follows a three-step protocol:

1. **Calibrate**: Capture baseline metrics from the external service
   (p50/p95/p99 latency, uptime %, error rates, throughput). Minimum
   7-day capture window.
2. **Shadow**: Run the primal replacement in parallel. Same traffic,
   separate port. Log both paths. Compare metrics daily.
3. **Cutover**: Switch traffic to the primal replacement only when
   shadow metrics meet or exceed baselines. Keep the external as
   fallback for 7 days post-cutover.

**No big-bang migrations.** Each step is independently reversible.

### 3. Gate as Source, VPS as Touchpoint

The gate hardware is the source of truth. The VPS is a touchpoint —
it terminates TLS, relays traffic, and caches content, but it owns
nothing. All state lives inside the gate's intracellular membrane.

### 3b. Diderm Membrane Architecture (Wave 77b)

The VPS layer is refined into a diderm (double-membrane) model with a
peptidoglycan trust barrier. See `DIDERM_DOMAIN_ARCHITECTURE.md` for
the complete specification.

| Layer | Domain | Trust | Dark Forest | Example |
|-------|--------|-------|-------------|---------|
| **Intracellular** | — | Covalent (full trust) | STRICT | Active gate, 13 primals |
| **Inner membrane** | `primal.eco` | Full sovereign trust | STRICT — zero commercial | golgiBody (knot-dns, Forgejo, mesh API) |
| **Peptidoglycan** | — | Trust barrier (opaque relay) | STRICT — broker only | peptidoglycan VPS (Songbird TURN, sync) |
| **Outer membrane** | `primals.eco` | Verified by cross-validation | RELAXED — commercial OK | golgiBody-ext (Caddy, Cloudflare CDN) |
| **Content organelle** | `nestgate.io` | Content trust (BLAKE3) | STRICT — sovereign DNS/TLS | NestGate CAS (pseudoSpores, notebooks) |
| **Extracellular** | — | Weak (Dark Forest) | N/A | crates.io, NCBI, Let's Encrypt |

**Key principle**: The inner membrane MUST be fully sovereign — zero
commercial services in the `primal.eco` data path. The outer membrane
MAY use commercial services (Cloudflare). The peptidoglycan is the air
gap between them — disposable, replicable, stores nothing.

Cross-membrane validation ensures the outer membrane stays honest:
the inner membrane compares BLAKE3 content hashes, TLS certificate
fingerprints, timing baselines, and DNS consistency between both paths.

---

## Bonding Model in Infrastructure

The four-bond model from chemistry maps to infrastructure trust:

### Covalent (Shared Seed, Full Trust)
- **Scope**: All content, all methods, all state
- **Auth**: BearDog family seed, BTSP mutual auth
- **Where**: LAN cluster (active gate ↔ strandGate), covalent gate mesh
- **Routing**: Direct dispatch, zero relay overhead
- **Example**: Two machines in the same basement sharing a family seed

### Ionic (Scoped Token, Metered Access)
- **Scope**: Scoped by capability token (e.g., `compute.*` but not `storage.*`)
- **Auth**: BearDog Ed25519-signed ionic tokens with expiry + JTI
- **Where**: ABG collaborators, friend's GPU, JupyterHub users
- **Routing**: Authenticated BTSP tunnel, resource envelopes enforced
- **Example**: A collaborator running notebooks through JupyterHub

### Metallic (Delocalized, Institutional)
- **Scope**: Fleet-wide capability sharing, no single-point trust
- **Auth**: Institutional certificate chain + BTSP overlay
- **Where**: University HPC (ICER), datacenter fleets
- **Routing**: biomeOS mesh routing, sunCloud economics
- **Example**: ICER cluster nodes joining as metallic compute providers

### Weak (Pre-Trust, External)
- **Scope**: Read-only public data, health checks, ACME challenges
- **Auth**: None (or Let's Encrypt ACME)
- **Where**: CDN fallback, Dark Forest beacons, initial contact
- **Routing**: VPS cache serves, no gate involvement
- **Example**: A browser hitting primals.eco for the first time

---

## Content-Aware Routing Standard

All membrane deployments must implement content-aware routing. Requests
are classified by type and routed to the appropriate backend:

| Content Class | Backend | Rationale |
|---------------|---------|-----------|
| ACME challenges | VPS local | Must be served from the IP the cert is for |
| Health/status | VPS local | Always available, zero gate dependency |
| Static assets (CSS/JS/images) | VPS cache (NestGate) | Cached locally, webhook-invalidated |
| Git operations | Gate (BTSP tunnel) | Authenticated, stateful |
| API/RPC | Gate (BTSP tunnel) | Authenticated, requires primal access |
| Auth flows | Gate (BTSP tunnel) | BearDog handles all identity |
| Large downloads (>50MB) | Songbird P2P | Avoid VPS bandwidth costs |
| Fallback | GitHub CDN | Last resort, always available |

**Cache policy**: 256MB max per VPS, 1-hour TTL, webhook-based invalidation
from gate NestGate. Cache misses proxy to gate via BTSP tunnel.

**Cost awareness**: Prefer P2P for large transfers. VPS bandwidth is metered.

---

## Membrane Channel Standards

Three channels define the cell's external interfaces (see
`MEMBRANE_CHANNEL_ARCHITECTURE.md` for full specification):

### Channel 1: Signal (DNS)
- **Process**: knot-dns on VPS
- **Port**: 53
- **Trust**: Lowest — public data
- **Status**: **PROPAGATED** (Jun 4) — `primal.eco` + `nestgate.io` zones live on sovereign knot-dns. Public resolvers (8.8.8.8, 1.1.1.1) resolve correctly. DNSSEC enabled.

### Channel 2: Relay (NAT Traversal)
- **Process**: Songbird TURN relay on VPS
- **Port**: 3478
- **Trust**: Credential-authenticated (HMAC)
- **Status**: LIVE ([RELAY_PUBLIC])

### Channel 2b: Remote Access (RustDesk)
- **Process**: hbbs/hbbr on VPS
- **Ports**: 21115-21117
- **Trust**: Key-authenticated (ed25519)
- **Status**: LIVE

### Channel 3: Surface (TLS)
- **Process**: Caddy (transitional) → BearDog (sovereign)
- **Ports**: 80 (ACME/redirect), 443 (TLS termination)
- **Trust**: ACME cert (Let's Encrypt E8), content-aware routing
- **Status**: **LIVE** — `membrane.primals.eco`, Caddy TLS. sporePrint NUCLEUS deployed on golgi (212 pages, Zola-rendered). BearDog ACME shadow **BLOCKED** — `CryptoProvider` panic in `rustls-rustcrypto` (UNIT-DIV-04). Caddy→bearDog cutover deferred to Wave 134b sovereignty sprint. DNS `primals.eco` still on Cloudflare (acceptable per diderm outer membrane).

**Primal role clarification**:
- **Songbird** handles TLS termination (long-term sovereign TLS)
- **BearDog** handles cryptographic identity (key management, BTSP, encryption)
- **Caddy** is transitional — used until Songbird absorbs TLS capability

---

## Credential Management Standard

### At Rest
All credentials on external substrate (VPS) must be encrypted at rest:
- **Method**: BearDog AES-256-GCM with Argon2id KDF
- **Key storage**: BearDog keyring (`beardog key generate`)
- **Format**: `.age` files (e.g., `/opt/membrane/credentials.age`)
- **Verification**: darkforest MEM-15 checks encryption at rest

### In Transit
- **BTSP Phase 3 AEAD** for all inter-primal communication
- **TLS** for browser-facing connections
- **SSH key-only** for VPS management (no passwords)

### Rotation
- Cookie secrets: monthly via `rotate_cookie_secret.sh`
- SSH keys: via `deploy_membrane.sh keys {add,revoke}`
- Ionic tokens: scoped expiry (purpose-based via `auth.issue_session`)

---

## VPS Deployment Standard

### Sizing
| Phase | SKU | RAM | Services | Cost |
|-------|-----|-----|----------|------|
| 0.5 (relay-only) | s-1vcpu-512mb-10gb | 512MB | Songbird + RustDesk | ~$4/mo |
| 1.0 (Tower) | s-1vcpu-2gb | 2GB | + BearDog + SkunkBat + Caddy | ~$12/mo |
| 2.0 (full membrane) | s-2vcpu-4gb | 4GB | + knot-dns + NestGate cache | ~$24/mo |

### Service Persistence
- All services managed by systemd with `Restart=always`
- Runtime directories via `tmpfiles.d/membrane.conf` (survives reboots)
- All primal ports on `127.0.0.1` except explicit public listeners
- Logs via journald (persistent to `/var/log/journal/`)

### Security Baseline
Validated by `darkforest_membrane.sh` (MEM-01 through MEM-15):
- SSH: key-only, fail2ban, multi-gate managed
- Firewall: UFW deny-default + targeted allows
- Services: no unnecessary packages (exim4, droplet-agent, snapd purged)
- Credentials: 600 permissions, root-owned, encrypted where possible
- Binary integrity: BLAKE3 checksums (when b3sum installed)

---

## Forgejo as Inner Membrane Mirror

### Standard (current model — May 24, 2026)
- **GitHub is operationally primary** (outer membrane) — all dev pushes go here
- **Forgejo is the trailing inner membrane mirror** — pulls from GitHub server-side
- **No per-machine sync required** — dev happens across multiple gates
- **When covalent gates host Forgejo, we invert**: Forgejo becomes primary

### Operational Reality (Jul 2026, Wave 133d)

Forgejo runs on golgi (`git.primals.eco`). 39 repos tracked via golgi
bidirectional relay (`membrane-temporal-cascade.timer`, 15-min cycle).
Relay handles GitHub↔Forgejo sync automatically. All primals, springs,
gardens, infra repos synced bidirectionally. Push protocol: gates push to
BOTH remotes (origin=GitHub, forgejo=Sovereign). golgi relay reconciles
any drift.

CI runs on GitHub Actions. See `REPO_MEMBRANE_BOUNDARY.md` for the full
repo classification (inner-only / trailing mirror / outer-only).

**cellMembrane** is the only private repo in the sporeGarden org on GitHub.
It should move to Forgejo-only when covalent gates host Forgejo.

### Organization Mapping
| Forgejo Org | GitHub Org | Repo Count |
|-------------|-----------|------------|
| sporeGarden | sporeGarden | 5 (4 public + 1 private: cellMembrane) |
| ecoPrimals | ecoPrimals | 19 |
| syntheticChemistry | syntheticChemistry | 8 |

### Migration Path
1. ~~GitHub-only development~~ — completed May 23, 2026
2. ~~Push-based sync~~ — replaced May 23 (doesn't scale to multi-gate)
3. **Current**: Forgejo pulls from GitHub server-side. GitHub primary for CI/dev.
4. **Near-term**: Port `notify-sporeprint.yml` to Forgejo Actions, CI parity
5. **Inversion**: Covalent gates host Forgejo → primary. GitHub becomes push mirror.

See: `REPO_MEMBRANE_BOUNDARY.md` for detailed repo classification and sync tooling

---

## Validation Standards

### Dark Forest Glacial Gate (deploy graph validation)
All deploy graphs must pass `dark_forest_gate_local.sh` (33 checks, 5 pillars):
- `secure_by_default = true` in `[graph.metadata]`
- All nodes reference valid plasmidBin binaries
- Dependency ordering is acyclic
- Port assignments are unique
- Auth mode defaults to `enforced`

### Membrane Audit (VPS validation)
`darkforest_membrane.sh` validates MEM-01 through MEM-15:
- SSH hardening, firewall posture, credential permissions
- Service inventory, listener audit, binary integrity
- Credential encryption at rest

### Sovereignty Parity (shadow run validation)
benchScale scenarios validate replacement parity:
- `btsp_tls_parity.sh` — BearDog TLS vs Cloudflare TLS
- `songbird_nat_parity.sh` — Songbird TURN vs cloudflared
- `nestgate_content_parity.sh` — NestGate+petalTongue vs GitHub Pages
- `dot_sovereign_parity.sh` — knot-dns vs Cloudflare DNS

---

## Sovereignty Shadow Membrane Applicability (Wave 77b)

Under the diderm model, the sovereignty shadow tracks (S1-S5) apply
specifically to the **inner membrane** (`primal.eco`). The outer membrane
(`primals.eco`) may retain commercial services.

| Track | What | Inner Membrane (`primal.eco`) | Outer Membrane (`primals.eco`) |
|-------|------|------------------------------|-------------------------------|
| **S1** TLS | TLS termination | Sovereign Caddy + LE (**MUST**) | Cloudflare proxy (acceptable) |
| **S2** NAT | NAT relay | Songbird TURN (**GRADUATED**) | N/A |
| **S3** Content | Content serving | NestGate CAS on `nestgate.io` (sovereign) | sporePrint NUCLEUS on golgi (212pp, Zola). Inner membrane cutover pending bearDog fix (134b). |
| **S4** Auth | Authentication | bearDog BTSP enforced (**MUST**) | Public/Cloudflare auth (acceptable) |
| **S5** DNS | DNS resolution | knot-dns for `primal.eco` + `nestgate.io` (**MUST**) | Cloudflare DNS for `primals.eco` (acceptable) |

**Cutover protocol unchanged**: Each track still follows Calibrate → Shadow
→ Cutover. The change is that graduation criteria apply to the inner membrane
path, not the outer.

---

## Wave 68 Strategic Domains

Four new strategic tracks added to the sovereignty evolution:

| Domain | Description | Design Doc | Status |
|--------|-------------|-----------|--------|
| **Songbird Routing Consolidation** | TCP Tier 5 blocked in release; virtual endpoint relay for single-ingress; membrane TLS sovereignty | `SONGBIRD_VIRTUAL_ENDPOINT_RELAY_DESIGN.md` | Phase A: DONE. Phase B: DESIGNED. Phase C: ironGate. |
| **Neural API Perceptron** | Evolve rule-based routing to learned single-layer perceptron; shadow mode graduation protocol | `NEURAL_API_PERCEPTRON_DESIGN.md` | L4 impulse dispatched. L5: DESIGNED. |
| **grapheneGate Trust Anchor** | Pixel 8a as portable physical root of trust; Dark Forest beacon; sovereign mesh seed | `GRAPHENEGATE_BOOTSTRAP_STANDARD.md` | Manifest + standard: DONE. Role 1: P2. |
| **Topology-Aware Routing** | Network segment model; latency in discovery.peers; affinity-biased dispatch | `TOPOLOGY_MAP.toml` | Topology map: DONE. Routing impulse: dispatched. |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-07 | Wave 133d: sporePrint NUCLEUS deployed on golgi (212 pages). bearDog CryptoProvider panic (UNIT-DIV-04) blocks Caddy→bearDog TLS cutover — deferred to 134b sovereignty sprint. WAN mesh overlay live (flockGate↔sporeGate WireGuard). Forgejo relay upgraded to bidirectional 39-repo golgi relay (15-min cycle). SHOW_HN S-10 (sporePrint inner membrane) added as external proof target. Channel 3 status updated. |
| 2026-06-10 | Wave 107: **S4 GRADUATED** — 7-day BTSP auth gate PASSED (Jun 9). All 4 sovereignty shadows (S1-S4) now sovereign on inner membrane. 4-gate mesh collective LIVE. Deterministic deployment codified. NUCLEUS supervision shipped. |
| 2026-06-04 | Wave 77b: Diderm membrane architecture — added §3b layer model, sovereignty shadow membrane applicability table. S-tracks now apply to inner membrane (`primal.eco`); outer membrane may retain commercial. Cross-membrane validation added. |
| 2026-06-02 | Wave 68: grapheneGate, topology routing, perceptron design, Songbird relay design, TCP Tier 5 release enforcement |
| 2026-05-15 | Initial version — sovereignty standards codified from ecosystem practice |

---

## FILE: `freshness.toml`

# SPDX-License-Identifier: CC-BY-SA-4.0
#
# freshness.toml — Ecosystem state snapshot at wave publish time
#
# Authority: primalSpring coordination (published each wave)
# Consumed by: membrane temporal.cascade --check, s_ecosystem_freshness scenario
#
# Regenerate: membrane temporal.cascade --publish-freshness

[wave]
id = 155
sub = "h"
date = "2026-07-29"
ssot = "specs/WATERFALL_TEMPORAL_SYNC.md"
notes = "Manual cascade publish — Wave 155h deep evolution wave"
publisher = "eastGate-overwatch"

[heads]
agentReagents = "6b1f32acf73daf97fbbfc5144337e2224d565a95"
airSpring = "4fa206673ba38b98f302391d05457f66a145fdc0"
barraCuda = "042f14938d655db1b483684081edc62da7ad1afb"
bearDog = "df9591d8ed5fb94f9fc69a6dabafd9073bad987e"
benchScale = "85ed6417ad3d73cb19ad657b4be7fba525f3ca46"
bingoCube = "c9f54107d99899f0016e83988f40922b217cdf2f"
biomeOS = "e7bebc4d0d00958bc0b97d42fc958998a5ca3fb5"
blueFish = "8ec23ddc42a99162ee1a512ea36fdf1cf8158fe6"
cellMembrane = "b13105b53fe30c29a27031a904b31a6d91fbca0a"
coralReef = "3d969f89a2b5322239694008e3f550a8c833c230"
esotericWebb = "2e5c2e516d8fd82914cdcc141b6b7b33d366c8f0"
groundSpring = "4f4cb2685ce9774dc75dfff8d350490a496eb330"
healthSpring = "054d5c9d6ad1e618701eab140f0eb6d9ab3e9393"
helixVision = "39e4bfe0135f8021de2e0660b1679e2533f7d957"
hotSpring = "c0245b66297ca4d8aaa27476a8895276aa736781"
initioChem = "328bc9a8b8f0519e2182d9570a4f2bd4f329bc73"
lithoSpore = "1407b3d4c703162a641ae66d29339f3075971d48"
loamSpine = "1ced08d5b6d6911875ee5de48a527c6ea1041e41"
ludoSpring = "8e7f0d829faf5b536c2ad254b558fdae1bbdf193"
nestGate = "3ca3e1bcb5ba7c5dcd7bccf37afef2f069607cac"
neuralSpring = "0f59558f2a8495e1f5de330a59b099bd04f13ceb"
petalTongue = "d60e67d6c2f37b2944a90a58e63fa0dce72bf879"
plasmidBin = "f0d543270b789a381d4f27aeefbedc3393f2b202"
primalSpring = "1b73180336a38eb12f7d351a78c03d9a03af4777"
projectFOUNDATION = "38c4d559236d7eed703e1e1606df10007f1818cb"
projectNUCLEUS = "04cc9019d225eb0332c17b6c33e307c08eeb6843"
rhizoCrypt = "904b17b2de83aaa904f5b509261cab1a76fb1c77"
rustChip = "f5c84a582bf9728afecd335ce04a35433a4f46af"
skunkBat = "8d6a0de12730d5274247aa78a736815f0c195924"
songBird = "bdbae1d44ece8932c85a7ea5cfc5e9762b67ca0a"
sourDough = "3a0b52df4b65a5436bfa87161e8cf181c4e85194"
sporePrint = "fa2f8d29b05f05f9e21bca00508ed68072915d2c"
squirrel = "acbe09e3edaff02eb9f1a0b90f997465400aadcc"
sweetGrass = "28092a8a53e05259252e4910632ca06a17cf592a"
toadStool = "04fcb96e3354b6aafdc46b0864945785d9710b13"
wateringHole = "da841afb02afe3aaeb7379021dc248246ca2b559"
wetSpring = "5b38488c721fb1516e6e7c7d22702c372053af88"
whitePaper = "f15281b287f06e5d175d9b6661fb8b12688e9ba7"

---

## FILE: `GLOSSARY.md`

# ecoPrimals Glossary

**Purpose**: Definitive terminology for the ecoPrimals ecosystem. If a term is used
in any document, handoff, or conversation, its meaning is defined here.

**Last Updated**: July 27, 2026 (Wave 155b — genomeBin convergence, autonomous enrollment shipped, 5 Tier 1 targets, Tower Atomic = OS abstraction, gate enmeshment glacial)

---

## The Three Organizations

The ecosystem is distributed across three organizations on both GitHub (outer
membrane) and Forgejo (inner membrane, `git.primals.eco`):

| Organization | Role | What Lives Here |
|-------------|------|----------------|
| **[ecoPrimals](https://github.com/ecoPrimals)** | Infrastructure primals | barraCuda, toadStool, coralReef, biomeOS, BearDog, NestGate, Songbird, sweetGrass, rhizoCrypt, loamSpine, petalTongue, Squirrel, skunkBat, bingoCube, sourDough. Also infrastructure repos: sporePrint, wateringHole, whitePaper, plasmidBin, benchScale. |
| **[syntheticChemistry](https://github.com/syntheticChemistry)** | Science validation springs | wetSpring, hotSpring, airSpring, neuralSpring, groundSpring, healthSpring, ludoSpring, primalSpring. Springs validate that primals produce correct science. |
| **[sporeGarden](https://github.com/sporeGarden)** | User-facing products (gen4) | projectNUCLEUS (sovereignty layer), projectFOUNDATION (knowledge layer), lithoSpore (verification chassis), esotericWebb (UI/agentic), cellMembrane (private ops — VPS deployment), helixVision (genomics pipeline), initioChem (computational chemistry), blueFish (analytical chemistry ETL). |

**Git hosts**: Forgejo on VPS (`git.primals.eco`) is the sovereign periplasmic
layer (golgiBody Phase A). GitHub is the trailing outer membrane mirror. Gates
push to Forgejo via SSH; GitHub receives post-push mirrors via the K-Derm
diderm relay chain. WaterFall sync (`membrane temporal.cascade`) pulls from
the periplasm. See `fossilRecord/wave150s_standards/WATERFALL_PATTERN.md` for the full sync model and
`operations/REPO_MEMBRANE_BOUNDARY.md` for per-repo classification: inner-only, trailing
mirror, or outer-only.

**Why three orgs?** Primals build capabilities. Springs validate those capabilities
against published science. Products deliver validated capabilities to users.
The organizations mirror this separation: infrastructure, validation, delivery.

When linking to repos, always use the correct organization:
- Springs: `github.com/syntheticChemistry/<spring>`
- Primals: `github.com/ecoPrimals/<primal>`
- Products: `github.com/sporeGarden/<product>`
- Site: `primals.eco`

See `LINK_INTEGRITY_STANDARD.md` for the full URL convention standard.

---

## The Physical Layer

### Gate

A **gate** is a physical computer — a deployment target that runs the ecoPrimals
stack. Gates are named using camelCase (`firstLast`) like all ecoPrimals entities.
The project operates across multiple houses and platforms:

| Gate | Platform | Composition | Role | Status |
|------|----------|-------------|------|--------|
| **golgiBody** | Linux (VPS) | thin-relay | Sole depot, enrollment, Forgejo, Drawbridge | ONLINE |
| **sporeGate** | Linux | full | Build authority, cascade hub, HPC | ONLINE |
| **eastGate** | Linux | full | Code hub, overwatch | ONLINE |
| **ironGate** | Linux | full | GPU compute, 4x HDD enclave, JupyterHub | ONLINE |
| **flockGate** | Linux | full | Nest Atomic validation | ONLINE |
| **northGate** | Windows | full | RTX 5090, gaming/GPU compute | ONLINE |
| **grapheneGate** | Android | tower | Beacon seed, mobile Tower | ONLINE |
| **strandGate** | Linux | compute (7) | Dual EPYC, RTX 3090, bioinformatics | HW READY |
| **westGate** | Linux | nest (7) | 5x14TB HDD (70TB ZFS cold pool) | HW READY |
| **blueGate** | Windows | tower (3) | Distributed builder, media/gaming | HW READY |
| **swiftGate** | Windows | full (13) | Hobby/consumer, house2 | HW READY |
| **southGate** | Linux | full (13) | House2 sovereign site | HW READY |

Gates run any operating system — Linux, Windows, Android, macOS. Tower Atomic
(bearDog + songBird + skunkBat) is the OS abstraction layer, handling IPC
transport (UDS vs named pipes vs TCP), service management, and platform
detection intrinsically. Gates self-enroll via `mesh.gate_enroll` — declaring
name, composition, and physical proof. No manifest pre-definition needed.

When Plasmodium is active, multiple gates bond into a collective. Any gate can
query the collective; workloads route to the best gate by capability match.

### Operational Substrate

The software environment a gate provides to the ecoPrimals stack. Platform-
specific details are handled by Tower Atomic — primals auto-detect via
`Platform::detect()` at compile time.

| Layer | Linux | Windows | Android |
|-------|-------|---------|---------|
| **IPC** | UDS / abstract sockets | Named pipes / TCP | Abstract sockets / TCP |
| **Shell** | bash | PowerShell | adb / Termux |
| **Toolchain** | Rust stable, cargo, clippy, rustfmt | Same (via rustup) | Cross-compiled from Linux |
| **Service mgmt** | systemd | Windows Service (planned) | Manual / init |
| **GPU** | Vulkan (wgpu) | Vulkan / DirectX (wgpu) | Vulkan (wgpu) |

No Docker. No Kubernetes. No cloud VMs. The gate IS the infrastructure.

---

## The Software Layer

### Primal

A **primal** is a self-contained Rust binary that provides a collection of
**primitives** — small, focused capabilities solving one domain well. Primals
are autonomous: each knows only itself. Complexity is solved through
**coordination**, not by making a primal larger.

Key properties:
- Self-knowledge only (never imports another primal's code)
- Capability-based discovery at runtime
- Zero compile-time coupling between primals
- Pure Rust (no C dependencies in application code)
- UniBin architecture (one binary, multiple modes via subcommands)

Examples: bearDog (cryptography), songBird (networking), toadStool (hardware),
barraCuda (math), coralReef (shader compilation), Squirrel (AI coordination).

**Naming convention**: Canonical capitalization is camelCase with firstLast —
`bearDog`, `songBird`, `toadStool`, `sweetGrass`, `wetSpring`, `hotSpring`.
In prose, initial caps are common (BearDog, ToadStool) and acceptable.
The camelCase structure is intentional — even names like songBird and toadStool
leverage the semantic naming (song+Bird, toad+Stool) for discoverability.

### Primitive

A **primitive** is the atomic unit of capability a primal provides. BearDog's
primitives include Ed25519 signing, BLAKE3 hashing, X25519 key exchange.
barraCuda's primitives include f64 WGSL shaders for dot products, FFT,
eigensolve, and statistical functions. A primitive is the smallest thing a
primal can do.

### Spring

A **spring** is a validation and evolution environment — a Rust workspace that
composes primals and validates that their composition solves real scientific or
engineering problems. Springs are not primals; they consume primals via IPC and
prove correctness through numbered experiments. Springs are named after natural
water sources: wetSpring, hotSpring, airSpring, neuralSpring, groundSpring,
healthSpring, ludoSpring.

Springs evolve through a defined pipeline:

```
Python baseline → Rust validation → GPU acceleration → sovereign pipeline
→ primal composition → ecosystem co-evolution
```

Each spring has:
- Its own git repository
- A `specs/PAPER_REVIEW_QUEUE.md` tracking papers to reproduce
- Numbered experiments with counted checks (pass/fail/skip exit codes)
- Deploy graphs (TOML) for the primal compositions it validates
- A faculty anchor (a professor whose publications drive the science)
- Gap discovery and wateringHole handoff authorship

Springs are the gen3 layer (see `foundations/PRIMAL_SPRING_GARDEN_TAXONOMY.md`). They
were initially standalone binaries validating science; they now compose FROM
primals and validate that the composition works for their domain.

### Garden

A **garden** is a user-facing product that composes primals into tools people
actually use. Gardens follow the BYOB model (Bring Your Own Binaries),
consuming pre-built primal binaries from plasmidBin via IPC. Gardens are the
gen4 layer — they take the capabilities that primals provide and springs
validate, and turn them into products.

Gardens live in the `gardens/` directory. They own user experience, graceful
degradation when optional primals are absent, and product-level deploy graphs.

Examples: esotericWebb (CRPG engine), blueFish (PFAS analytical chemistry),
helixVision (genomics platform), initioChem (CompChem FEL explorer).

See `foundations/PRIMAL_SPRING_GARDEN_TAXONOMY.md` for the full taxonomy and co-evolution
contract between primals, springs, and gardens.

### Tool

A **tool** (gen2.5) is a standalone Rust crate or binary consumed by primals, springs,
or other ecosystem components. Tools solve bounded problem domains without the full
IPC/discovery/health surface that primals carry — they are not long-running daemons
and do not register capabilities with biomeOS. They are not end-user products (that's
a garden).

Tools live in `primals/` (when consumed as crate deps by primals), `infra/` (when
infrastructure-only), or `sort-after/` (pending canonical location).

Examples: bingoCube (crypto commitment), benchScale (lab substrate), agentReagents
(VM image builder), rustChip (NPU characterization), sourDough (scaffolding).

See `foundations/PRIMAL_SPRING_GARDEN_TAXONOMY.md` § Tools (gen2.5) for the full definition,
applicable compliance tiers, and ownership boundaries.

### Atomics

**Atomics** are the core primal interaction patterns — the named compositions
that larger niches are built on. They are not separate software; they are
what happens when specific primals coordinate.

| Atomic | Composition | What Emerges |
|--------|-------------|-------------|
| **Tower Atomic** | BearDog + Songbird + skunkBat | Trust boundary (crypto + discovery + defense) |
| **Node Atomic** | Tower + toadStool + barraCuda | Hardware-aware compute (+ GPU math) |
| **Nest Atomic** | Tower + NestGate | Secure content-addressed storage |
| **Full NUCLEUS** | All foundation primals + Squirrel | Complete AI-coordinated ecosystem |

Atomics are the building blocks. You don't deploy "Tower Atomic" — you deploy
a niche that uses Tower Atomic's capabilities because it needs crypto + networking.

### Niche

A **niche** is a biomeOS BYOB (**Build Your Own Biome**) deployment — a composed
set of primals, chimeras, and interactions deployed as a unit via a deploy graph.
A niche is what you actually run.

Examples:
- A field genomics niche: wetSpring + toadStool (NPU) + NestGate + BearDog
- A game science niche: ludoSpring + petalTongue + toadStool + barraCuda
- A precision health niche: healthSpring + barraCuda + petalTongue + NestGate

A niche is defined by:
- A **deploy graph** (TOML DAG) — germination order and capability wiring
- A **niche YAML** — organisms, interactions, customization options
- **Capability domains** — semantic namespaces (`ecology.*`, `precision.*`)

### Deploy Graph

A **deploy graph** is a TOML-encoded directed acyclic graph (DAG) that tells
biomeOS how to start and wire a niche. It specifies:
- Which primals to germinate (start)
- In what order (dependency edges)
- What capabilities to wire together
- What resources to allocate

biomeOS reads the graph, germinates the primals, waits for their sockets, and
wires their capabilities together. The graph is the deployment contract.

### Chimera

A **chimera** is a fused multi-primal organism with a unified API. Unlike a
niche (which coordinates separate processes), a chimera is a single binary that
combines capabilities from multiple primal lineages.

Example: `gaming-mesh` = Songbird networking + ludoSpring game logic, fused
into a single binary with one API surface.

Chimeras are rare and intentional — most composition should happen via IPC
coordination, not fusion.

### Germination

**Germination** is the process of starting a primal and waiting for it to become
ready. A primal germinates when its `server` subcommand starts, its IPC socket
appears, and it responds to `health.check`. biomeOS monitors germination via
deploy graphs.

Analogy: a seed (binary) germinates (starts) in a niche (deployment) on a
gate (computer).

---

## The Coordination Layer

### biomeOS

The **ecosystem substrate** — the orchestration layer that discovers primals,
routes capabilities, composes niches, and manages the lifecycle of everything
running on a gate. biomeOS does not compute science; it coordinates the primals
that do.

Key subsystems:
- **Neural API**: Semantic capability routing (170+ translations, 16 domains)
- **NUCLEUS composition**: Layered atomic patterns
- **Dark Forest coordination**: Zero-metadata discovery
- **Provenance trio wiring**: rhizoCrypt + loamSpine + sweetGrass orchestration

### NUCLEUS

The **full primal composition** orchestrated by biomeOS. NUCLEUS is not a
binary — it is the emergent state when all foundation primals are running and
coordinated on a gate.

```
Tower Atomic (BearDog + Songbird + skunkBat)
  + Node Atomic (+ toadStool + barraCuda + coralReef)
  + Nest Atomic (+ NestGate)
  + Squirrel (AI)
  = Full NUCLEUS
```

### Plasmodium

The **over-NUCLEUS collective** formed when 2+ gates bond. Named after the
slime mold *Physarum polycephalum* — no central brain, collective intelligence,
pulsing coordination. Gates join and leave dynamically.

When Eastgate and biomeGate bond, their NUCLEUS instances merge into a
Plasmodium. Workloads route to the gate with the best capability match.

### Provenance Trio

The three primals that together provide the project's memory and attribution:

| Primal | Role | Temporal Domain |
|--------|------|-----------------|
| **rhizoCrypt** | Ephemeral memory | Present — working DAG, fast, lock-free |
| **loamSpine** | Permanent memory | Past — immutable linear history, Loam Certificates |
| **sweetGrass** | Attribution | Always — semantic provenance, W3C PROV-O braids |

When composed by biomeOS, these three create **RootPulse** — distributed
version control that emerges from primal coordination.

### RootPulse

**Distributed version control** that emerges from the provenance trio's
coordination. RootPulse is not a VCS binary — it is what primals DO together:
rhizoCrypt provides the workspace, loamSpine provides the history, sweetGrass
provides the attribution, BearDog signs it, NestGate stores it, Songbird
syncs it. biomeOS orchestrates the whole thing via Neural API.

### soundStage

The **transparent observation layer** for hardware trust ceremonies. soundStage
makes ephemeral key generation visible — you watch the entropy flowing from each
hardware source, see the mixing happen, observe the derivation, and validate the
output. If you can't see it working, you're just trusting it's secure.

soundStage is not a primal. It is an ecoPrimals **concept** — a capability that
primals compose to provide live ceremony observability. The concept applies
anywhere hardware trust operations happen (key generation, certificate minting,
entropy ceremonies).

Core abstractions:

| Concept | Role | Analogy |
|---------|------|---------|
| **Channel** | A single observable entropy source (SoloKey, StrongBox, audio, getrandom) | A microphone in a recording studio |
| **Mix bus** | Where channels converge — the mixing operation and its output | The mixing board |
| **Monitor** | The derived key material's fingerprint (never the raw key) | Studio monitors (listen but don't broadcast) |
| **Session** | A complete ceremony recording — all channels, mix, output timestamped | A session tape |
| **Comparator** | Diffs sessions to prove independence or detect degenerate entropy | A/B comparison |

Key properties:
- **Multi-anchor**: Each hardware source is a separate channel (SoloKey, Pixel
  StrongBox, audio mic, OS entropy)
- **Multi-user**: Each user gets independent sessions — comparator verifies
  independence across users
- **Quality gates**: Require multi-source (≥2 anchors) and entropy floor
  (>4.0 bits/byte Shannon) to pass
- **Fingerprints only**: The monitor observes key derivation through BLAKE3
  fingerprints — raw key material never leaves the ceremony
- **Transparency over trust**: The entire point is to make the black box visible.
  If a hardware source starts producing degenerate entropy, you see it immediately.

soundStage is to key generation what darkforest is to network security: the tool
that makes the invisible visible. darkforest reveals what probes the network.
soundStage reveals what flows through the ceremony.

See `primalSpring/ecoPrimal/src/soundstage/` for the reference implementation.

### Genetic Enrollment

The **two-layer trust model** for gate-to-gate authentication:

| Layer | What It Proves | Mechanism |
|-------|---------------|-----------|
| **Mito gate** | "I belong to this ecosystem" | Mitochondrial beacon seed — shared family secret |
| **Nuclear lineage distance** | "I am N hops from the root" | Derivation chain from the nuclear seed → trust tier |

Genetic enrollment replaces static shared secrets with a biological trust
model: gates that share closer genetic lineage (shorter derivation distance)
receive higher trust tiers. A gate proves enrollment by demonstrating
knowledge of both its mito beacon membership AND its nuclear derivation chain.

bearDog manages the genetic crypto (`genetic.*` capabilities). songBird
consumes it for `enrollment.verify` during mesh join. The trust tiers feed
into `capability.call` routing priority — genetically closer gates are
preferred for capability dispatch.

### Tower Shadow

**Shadow deployment mode** for Tower Atomic — running the Tower transport
stack alongside WireGuard, mirroring traffic to collect comparative metrics
without affecting production routing.

Key commands:
- `membrane tower.shadow --enable` — activate shadow mode
- `songbird benchmark --mode tower-atomic --peer <addr>` — measure Tower latency/throughput
- `songbird benchmark --mode wireguard --peer <addr>` — WireGuard baseline

Shadow deploy collects continuous metrics (latency, throughput, jitter) via
a systemd timer (`tower-shadow.timer`) running every 60 minutes. Results are
JSON files stored in `benchScale/tower_shadow/`. This data drives the Tower
EXCEEDS claims (353x LAN, 1.7x WAN sustained).

Shadow mode is the validation phase before Phase 3 cutover (Tower replaces WG).

### LAN Mesh Routing

The **LAN-first routing preference** for same-switch peers. When two gates
are on the same physical switch (e.g., CRS310 backbone), `mesh.find_path`
should return an `EndpointType::Local` path (sub-millisecond) rather than
routing through the WG overlay (100–200ms RTT through VPS relay).

`primalSpring` implements this via `MeshEntry::preferred_address()` which
checks `lan_addr` before falling back to the WG overlay address.

**P0 gap (Wave 150x)**: songBird's `mesh.find_path` does not yet honor
`EndpointType::Local` — it returns the WG overlay for all peers regardless
of LAN availability. This imposes a 353x–1200x latency penalty for
`capability.call` dispatch between co-located gates.

### CallerContext

A **per-connection identity object** wired into songBird's IPC method gate.
When a primal connects via UDS (Unix Domain Socket), the connection extracts
`SO_PEERCRED` (Linux peer credentials: PID, UID, GID) and attaches a
`CallerContext` to every subsequent method call on that connection.

The method gate uses `CallerContext` to:
- Verify the caller's PID maps to a known primal process
- Enforce per-method access control (some methods are local-only)
- Reject unauthenticated remote callers attempting local-only operations

CallerContext + UDS hardening (socket permissions, symlink rejection, TOCTOU
protection) together resolved 7 pen-test findings in Wave 150x.

### Chimera Phase 0

The **first step** in chimera evolution: extracting shared library code from
primals that currently communicate exclusively via IPC. Phase 0 targets
bearDog's crypto primitives — the hot-path crypto operations that every
primal uses frequently enough to justify in-process linking over IPC overhead.

Chimera Phase 0 prerequisites:
1. Composition validation (bearDog UDS crypto works for all cold-path) ✓
2. Hot-path identification (`CRYPTO_COMPOSITION.md` classifies 19 seams)
3. Library extraction (bearDog → `beardog-core` crate)
4. Feature-gate migration (primals opt-in to embedded crypto)

Phase 0 is unblocked once composition validation is complete (songBird P1
crypto delegation finishing).

See `primalSpring/ecoPrimal/src/soundstage/` for the reference implementation.

---

## The Compute Triangle

Three primals form the sovereign compute stack:

```
barraCuda (WHAT to compute — f64 WGSL shaders, math primitives)
    ↓
coralReef (HOW to compile — WGSL → native GPU binary, naga IR)
    ↓
toadStool (WHERE to run — hardware discovery, dispatch, orchestration)
```

### barraCuda

**Pure math.** 712+ WGSL f64 shaders. Writes the math. Springs depend on
barraCuda directly for math without pulling toadStool's runtime or coralReef's
compiler. Budded from toadStool at Session 93.

### coralReef

**Sovereign shader compiler.** Compiles WGSL to native GPU binaries (SM70-SM89
SASS) without NVIDIA's NVVM or any vendor SDK. Includes VFIO dispatch with PFIFO
channels. The "compiler that frees the math from the vendor."

### toadStool

**Hardware infrastructure.** Discovers CPUs, GPUs, NPUs. Probes capabilities.
Dispatches workloads. Manages the Node Atomic deployment. 20,843 tests, 96+
JSON-RPC methods.

---

## The Science Layer

### metalForge

Where a spring is working on **hardware concepts** — GPU vs CPU routing, GPU to
NPU via PCIe, hardware dispatch architecture. metalForge is the exploratory
substrate where primals figure out how to talk to novel hardware. The brain
architecture in hotSpring evolved through metalForge before stabilizing.

metalForge is not a primal — it is an evolution context. When a spring needs to
push work across compute substrates (CPU → GPU, GPU → NPU) and the path doesn't
exist yet, that work happens in metalForge.

### baseCamp

The transition from **paper validation to real exploration**. baseCamp lives in
`whitePaper/gen3/baseCamp/` and is where springs move beyond reproducing a single
paper to mixing larger datasets and systems. QS-Anderson evolved this way — the
paper parity work validated the pieces, and baseCamp is where those pieces
combine into something new.

Currently 18 papers (01-18), spanning Anderson-QS, LTEE, bioag, sentinels,
symbiotic ecology, no-till, WDM, NPU edge, field genomics, dynamical QCD,
nautilus reservoir computing, immuno-Anderson, sovereign health, precision brain,
anaerobic-aerobic QS, game design as science, RPGPT.

### Paper Parity

The standard of evidence for spring experiments: the Rust implementation must
produce results that match the published paper's results within named tolerances.
Not "close enough" — paper parity means you could substitute the spring's output
for the paper's figures and a reviewer would accept them.

### Experiment

A numbered unit of scientific validation within a spring. Each experiment has:
- A number (e.g., Exp356)
- A defined objective
- Counted checks (e.g., "18/18 PASS")
- A connection to a baseCamp paper or paper queue entry

### Faculty Anchor

A professor whose published work drives a spring's science. Each spring has at
least one faculty anchor. The project reproduces their papers, then extends the
science. Faculty anchors are documented in `whitePaper/attsi/`.

| Spring | Faculty Anchor(s) |
|--------|-------------------|
| wetSpring | Faculty anchor (quorum sensing), faculty anchor (agriculture) |
| hotSpring | Faculty anchor (plasma physics), faculty anchor (lattice QCD), faculty anchor (gradient flow) |
| groundSpring | Faculty anchor (spectral theory) |
| healthSpring | Faculty anchor (pharmacology) |
| neuralSpring | (cross-domain — reproduces from all anchors) |
| airSpring | Faculty anchor (precision agriculture) |
| ludoSpring | Published authors (Flow theory, motor control, procedural generation) |

### attsi

The **faculty outreach program** (`whitePaper/attsi/`). Contains contact
packages, review materials, and outreach strategy for each faculty anchor.
Faculty identities are maintained in the non-anonymous whitePaper layer; anonymized
contacts use hashed identifiers.

---

## The Evolution Vocabulary

### Evolution

In ecoPrimals, **evolution** means directed improvement through validated steps.
A spring evolves from Python baselines to Rust validation to GPU acceleration.
A primal evolves by absorbing primitives upstream (into barraCuda) and
delegating downstream (to toadStool). Evolution is always validated — every
step passes tests.

### Absorption

When a spring's local implementation of a primitive is replaced by a call to
barraCuda's canonical version. The spring "absorbs upstream" — it stops owning
the math and starts consuming the shared version. This is how springs
collectively evolve barraCuda.

### Delegation

The inverse of absorption: when a primal delegates work to another primal.
A spring delegates hardware dispatch to toadStool, math to barraCuda, shader
compilation to coralReef. Delegation is always via IPC, never via code import.

### Deep Debt

Technical debt identified during evolution sessions. Tracked in handoffs, not
in TODO comments in code. Deep debt is actively reduced — the archive of
handoffs is full of "DEEP_DEBT" sessions where primals were systematically
improved.

### Handoff

A **session handoff** document in `wateringHole/handoffs/`. Records what was
done, what's next, what broke, what was discovered. Handoffs are the working
memory between sessions. After resolution they are archived to the
fossilRecord repository.

### Fossil Record

The canonical archive repository at `github.com/ecoPrimals/fossilRecord`.
Never deleted, only accumulated. The geological record of every evolution
session the project has run. 3,831+ documents spanning February 4, 2026 –
present, consolidated from 10 ecosystem sources with provenance-preserving
subdirectory structure.

### Fossilization

The act of moving resolved content — handoffs, showcase directories,
superseded standards, local wateringHole trees — from active repos to the
fossilRecord. Fossilized content is replaced by a README stub pointing to
the canonical archive location. The content is never deleted; it moves from
working memory to geological record.

Fossilization became a first-class ecosystem operation during Wave 49
(showcase fossilization across 8 primals) and Wave 51 (primalSpring
wateringHole fossilization). The pattern: **copy to fossilRecord → replace
with pointer stub → push both repos**.

### Wave

A **wave** is a named coordination pulse across the ecosystem — a point
where multiple primals and springs evolve together in response to a shared
signal. Waves are numbered sequentially (Wave 47, 48, 49, 50, 51…) and
tracked in `fossilRecord/wave150s_standards/GLACIAL_SHIFT_READINESS.md`.

A wave is not a release. It is a *synchronization event* — a moment when
the ecosystem converges on a shared standard, absorbs upstream changes,
and confirms alignment. Springs "respond" to waves by pulling the latest
patterns and confirming compliance. Waves are how the ecosystem breathes.

### Stadial / Interstadial

Borrowed from glacial geology. A **stadial** is a period of hard convergence
— all components forced to a common fitness threshold. An **interstadial** is
a warming period of diversification under constraint. The ecosystem cycles
between these phases: stadials cull non-conforming patterns, interstadials
allow exploration and specialization, extinction events select what survives,
and the next stadial raises the bar.

The current position (May 2026) is interstadial exit → stadial entry. The
glacial shift criteria define the gate.

See `whitePaper/gen4/architecture/STADIAL_INTERSTADIAL_PATTERN.md`.

---

## The Deployment Layer

### plasmidBin

The **binary distribution repository** at `github.com/ecoPrimals/plasmidBin`.
Contains pre-built musl-static NUCLEUS primal binaries for x86_64 and aarch64.
Every primal binary deployed in production comes from plasmidBin — never from
`cargo build` on the gate, never from `target/release/`, never from PATH
lookup.

plasmidBin provides:
- `manifest.toml` — canonical primal registry (versions, methods, checksums)
- `checksums.toml` — BLAKE3 hashes per binary per architecture
- `sources.toml` — mapping from primal IDs to source repos and build config
- `plasmidbin` CLI — Rust binary for `validate`, `harvest`, `fetch`, `deploy`,
  `start`, `stop`, `doctor`, `launch`
- GitHub Actions CI — automated harvest from upstream releases, checksum
  generation, smoke testing

The name follows the biological metaphor: a plasmid is a small circular DNA
molecule that carries genes between bacteria independently of the chromosome.
plasmidBin carries primal binaries between gates independently of the source
repos.

### postPrimordial

The **deployment regime** where all NUCLEUS primal binaries come exclusively
from plasmidBin. No `target/release/` paths, no `cargo install`, no `which`
PATH lookups, no `~/.local/bin` or `~/.cargo/bin` fallbacks in any launcher,
deploy script, systemd unit, or composition tool.

postPrimordial is the ecosystem after its primordial phase — the period when
primals were built locally from source on each gate. The primordial phase
was necessary (you can't distribute binaries that don't exist yet). The
post-primordial phase recognizes that local builds are fragile, non-reproducible,
and create deployment drift between gates.

The transition happened at Wave 49 (post-primordial deployment enforced
across all launchers). Wave 51 completed the Rust elevation of plasmidBin
itself — the distribution tool is now as sovereign as the binaries it
distributes.

**Compliance rule**: any script, service, or doc that resolves a NUCLEUS
primal binary through anything other than plasmidBin is a primordial
anti-pattern and must be fixed. Spring-owned validation binaries (e.g.,
`target/release/healthspring_unibin`) built from the spring's own source
are exempt — they are not NUCLEUS primals.

### goldenCage

The set of external cloud services that the ecosystem uses to bootstrap
sovereignty — services that are individually excellent, collectively
indispensable, and structurally a single point of failure until replaced.

The golden cage bars: GitHub (code, CI, releases), Cursor (AI development),
Cloudflare (DNS, TLS proxy, tunnel), DigitalOcean (VPS), crates.io
(dependency resolution), Let's Encrypt (TLS credentials), Python/GROMACS
(science baseline validation).

The **chrysalis thesis**: the cage is not the enemy — it is the bootstrap
material from which sovereignty is built. Each sovereign replacement
(BearDog for Cloudflare TLS, Songbird for cloudflared tunnel, NestGate for
GitHub Pages, Forgejo for GitHub repos, self-hosted runners for GitHub
Actions) was built using the cage's resources. The cage becomes the outer
membrane when the inner membrane is self-sufficient.

See `whitePaper/gen4/architecture/THE_GOLDEN_CAGE.md`.

---

## The Network Boundary Layer

### Gatehouse

The **bond escalation broker** — the single external surface of a gate exposed
to the internet. The gatehouse accepts all incoming traffic as **weak** interactions
(zero trust, passive diffusion) and validates/promotes them to stronger bond types
as authentication is established.

bearDog owns the gatehouse — exactly two ports (`:443` TLS, `:80` ACME redirect). No
other primal binds externally. skunkBat provides threat intelligence. The gatehouse
manages **TLS credentials** (drawbridge transport, not Loam Certificates) and is where
the K-Derm extracellular → outer membrane crossing happens.

Bond escalation through the gatehouse:

```
Weak (extracellular) → bearDog TLS termination
  → Ionic (outer membrane → periplasm) → BTSP scoped token
    → Metallic (periplasm → plasma) → Mito-Beacon membership
      → Covalent (plasma → cytoplasm) → nuclear session (fresh spawn)
```

Only one gate runs gatehouse mode per deployment (sporeGate for the current mesh).
All other gates are purely darkforest — zero exposed ports.

See `operations/GATEHOUSE_DARKFOREST_STANDARD.md`, `foundations/BONDING_MODEL_STANDARD.md`.

### Darkforest

The **invisible interior** of the mesh. No port scanning, no direct access, no
known entry points from outside. All inter-primal communication uses UDS, abstract
sockets, or songBird mesh relay. Discovery is via `mesh.peers` and `capability.call`.

The darkforest boundary is the enforcement mechanism that prevents sovereignty
leakage — nothing inside leaks out without crossing the drawbridge, and nothing
outside enters without passing through the gatehouse's bond escalation. The Dark
Forest principle means everything starts untrusted. Trust is earned through
progressively stronger authentication at each K-Derm layer crossing.

See `operations/GATEHOUSE_DARKFOREST_STANDARD.md`, `foundations/DARK_FOREST_GLACIAL_GATE_STANDARD.md`.

### Drawbridge

The **single crossing point** between the gatehouse (external) and the darkforest
(internal). Implemented as songBird's HTTP proxy listener, the drawbridge translates
external HTTP semantics into capability-routed mesh semantics.

The drawbridge sits at the outer membrane → periplasm crossing. It is where weak
bonds begin escalating — path prefixes map to capability names, and
`capability.call` routes requests to backends in the darkforest.

As of Wave 133d, the drawbridge auto-registers its routed capabilities into the
local IPC registry and announces them to mesh peers via `mesh.capabilities_announce`.
This means any gate with drawbridge routes automatically advertises its capabilities
to the mesh — no manual `ipc.register` or sidecar scripts needed.

```
SONGBIRD_DRAWBRIDGE_ROUTES=/hub=jupyter,/api=inference
→ auto-registers ["jupyter", "inference"] in IPC registry
→ announces to mesh peers
→ remote capability.call discovers and routes to this drawbridge
```

See `operations/GATEHOUSE_DARKFOREST_STANDARD.md` §Drawbridge, §Capability advertisement.

### Bond Escalation

The process by which incoming traffic transitions from weaker to stronger bond
types as trust is progressively established. Each escalation requires stronger
authentication and crosses a deeper K-Derm envelope layer:

| Escalation | Authentication Required | K-Derm Crossing |
|------------|------------------------|-----------------|
| Weak → Ionic | BTSP scoped token | Outer membrane → periplasm |
| Ionic → Metallic | Mito-Beacon membership proof | Periplasm → plasma membrane |
| Metallic → Covalent | Nuclear session (fresh key spawn) | Plasma membrane → cytoplasm |

The reverse path (covalent → weak) is **Ceremony** — a controlled temporal decay.
The outward path (covalent → metallic → ionic → weak across VPS layers) is the
**bond-type degradation** model documented in `KDERM_DIDERM_ENVELOPE.md`.

Bond escalation and degradation are complementary: escalation is inward (external
traffic gaining trust), degradation is outward (sovereignty weakening as content
moves toward the extracellular). The gatehouse brokers inward escalation. The
VPS diderm envelope enforces outward degradation.

See `foundations/BONDING_MODEL_STANDARD.md` §Bonding Escalation Path.

### Endosymbiosis

The process by which external systems progressively internalize — moving from
weak to ionic to metallic to covalent bonding as they are absorbed into the
sovereign infrastructure. Named after the biological process where independent
organisms become organelles through progressive integration.

Examples: Cloudflare TLS credentials (weak) → bearDog ACME shadow (ionic) → bearDog
sovereign TLS (covalent). GitHub Pages (weak) → Forgejo periplasmic mirror (metallic) → Forgejo
sovereign (covalent). Each sovereignty shadow track is an endosymbiosis in progress.

See `K_DERM_RECONCILIATION.md` §K-Derm Extensions Not in Gen4.

---

## The Meta Layer

### metaPrimal

A **metaPrimal** is a repository that is conceptual instead of functional — it
doesn't compile into a binary, but it is an essential organism in the ecosystem.
metaPrimals follow the same camelCase naming and have their own git repos.

| metaPrimal | Purpose |
|------------|---------|
| **wateringHole** | How primals intercommunicate. Standards, IPC protocols, leverage guides, handoffs. The coordination documentation layer. |
| **whitePaper** | Theses, concepts, and documentation of evolution. The scientific and strategic record — gen2/gen3 paper trails, attsi outreach, baseCamp papers. |
| **sourDough** | The nascent primal for rapid evolution of new primals. A starter culture for bootstrapping new primal projects. |

### Phase 1 / Phase 2

**Temporal artifacts**, not semantic categories. Phase directories were
organizational markers used while building between gates — keeping which primals
were on which gate clear during early development. They correspond loosely to
`gen2/` and `gen3/` in whitePaper. Not actively meaningful; treat them as
historical scaffolding if encountered.

### Version Numbers and Differential Evolution

Springs and primals independently evolve their own progress markers. Some use
**session numbers** (e.g., neuralSpring S145), some use **version numbers**
(e.g., hotSpring v0.6.29, wetSpring V113). This divergence is fully
intentional — AI-assisted development means each project self-flavors over
time as its AI iterations accumulate. There is no global numbering standard
because primal autonomy extends to how they count.

**Differential evolution rates are biological, not bugs.** Archaea, microbes,
and algae all evolved at different rates — depth reflects internal evolution
pressure, not cross-system maturity parity. A primal at v0.14 has undergone
more internal iteration than one at v0.2, but neither is "ahead" or "behind"
— they serve different niches with different selection pressures. rhizoCrypt
(0.14.17) has iterated heavily because DAG provenance is a complex domain.
biomeOS (0.1.0) is young because orchestration crystallized later. Both are
production-ready for their current role.

No primal has reached 1.0. The 1.0 threshold means: API surface is stable,
breaking changes require major version bumps, and the primal's niche is
fully colonized. petalTongue (1.6.6) is the closest — its grammar pipeline
has stabilized through heavy external-facing iteration.

**Team guidance**: Version numbers should reflect the primal's own internal
evolution cadence. Bump minor for capability additions, patch for fixes and
refinements. Do not synchronize versions across primals. The ecosystem
manifest (`ecosystem_manifest.toml`) and depot checksums are the cross-system
coordination layer — not version alignment.

---

## Licensing & Strategy

### Lysogeny Protocol

**Area denial through open prior art.** By publishing under AGPL-3.0, every
innovation becomes prior art that prevents patents. Named after bacteriophage
lysogeny — the viral DNA integrates into the host genome and persists.

### scyBorg

The **ecosystem licensing standard** — a triple copyleft framework:

- **AGPL-3.0-or-later**: All code, shaders, tools, infrastructure
- **ORC**: All mechanical interactions (primal coordination, IPC patterns, atomics, game rules)
- **CC-BY-SA 4.0**: All documentation, papers, methodology, reverse engineering findings

Each layer is governed by an independent nonprofit (FSF, Open RPG Creative
Foundation, Creative Commons). No single entity can revoke any layer.

scyBorg extends beyond "just code" to cover the entire body of work — the
papers, the methodology, the evolution trail, the reverse engineering
documentation. The intent is that everything published is permanently open and
untargetable.

### Symbiotic Exception

An **additional permission** (AGPL-3.0 Section 7) granted to a named
organization based on reciprocal benefit. The default scyBorg license applies to
everyone. Exceptions reduce licensing friction for allies — partners whose
tools, hardware, or knowledge benefit the ecosystem.

Exceptions are not for sale. They are diplomatic: granted based on symbiotic
value, revocable if the relationship ends. The public AGPL version is unaffected.

| Tier | Basis |
|------|-------|
| **Symbiotic** | Partner provides tools/hardware/knowledge (e.g., RustDesk, BrainChip) |
| **Reciprocal Open** | Partner publishes their own work under AGPL (e.g., GPU vendor opens architecture docs) |

See `SCYBORG_EXCEPTION_PROTOCOL.md` for the full protocol.

### Suppression Inversion

The strategic principle that by **owning nothing**, the project is untargetable.
No revenue to disrupt, no corporate entity to sue, no publisher to pressure, no
platform to suppress. Knowledge that has been published under copyleft cannot be
un-known. Reverse engineering of owned hardware is legal (*Sega v. Accolade*,
*Oracle v. Google*). The suppression vectors that companies use against
threatening work (legal, platform, commercial) all require a target — and
scyBorg eliminates the target.

### AI Authorship Paradox

All ecoPrimals code and documentation is AI-assisted, and this is disclosed
openly. Copyright law is unsettled on AI-assisted work. The paradox: if
AI-assisted work **is** copyrightable, the copyleft licenses apply normally and
the commons is protected. If AI-assisted work **is not** copyrightable, the
output enters public domain — an even stronger form of openness. Either outcome
preserves the commons. The only parties harmed by a negative ruling are those
claiming exclusive copyright on AI-assisted work for revenue. ecoPrimals has no
such claim, so the legal uncertainty is everyone else's problem.

See `gen3/about/LICENSING_STRATEGY.md` §8 for the full analysis.

### cellMembrane

The **selective permeability layer** of the ecosystem — a private operational
repo managed by the **cellMembrane team (ironGate)** (sporeGarden org) that deploys the
**fieldMouse Tower** composition to external substrate (VPS). cellMembrane
controls what crosses between intracellular (LAN/gates) and extracellular
(public internet) layers. Also provides the `membrane` CLI for gate operations:
`gate.enroll`, `gate.bootstrap`, `temporal.cascade`, `plasmid.harvest`.

Current state (Wave 155b):
- **Channel 2 Relay** (Songbird TURN :3478): **LIVE**
- **Channel 2b Remote** (RustDesk hbbs/hbbr :21115-21117): **LIVE**
- **Channel 3 Surface** (Caddy TLS :80/:443, `membrane.primals.eco`): **LIVE**
- **Enrollment** (`/enroll/*` → mesh.gate_enroll): **LIVE** on golgiBody
- **Phase 7**: gate.enroll → mesh.enroll via HMAC-SHA256 proof
- **Builder identity**: `plasmid.harvest` records builder gate + timestamp
- **Checksum verify**: handles both plain-string and struct TOML formats

cellMembrane is operationally on GitHub Private and should migrate to
Forgejo-only when covalent gates host Forgejo on sovereign infrastructure. It contains
sensitive configuration (SSH keys, API tokens, deployment scripts) that
MUST NOT leak to public repos. See `operations/REPO_MEMBRANE_BOUNDARY.md` and
`CELLMEMBRANE_FIELDMOUSE_DEPLOYMENT.md`.

### fieldMouse

The **minimal deployable structure** for the ecoPrimals ecosystem. Where a gate
runs a full NUCLEUS and a niche composes primals via a deploy graph, a fieldMouse
is the smallest stripped system — as few as a single atomic or chimera — purpose-built
for a constrained deployment niche.

fieldMouse is not a primal. It is a **deployment class** — a category of niche
deployments defined by how they fit their target hardware and environment. A
fieldMouse might be:

- A Tower Atomic chimera on a RISC-V microcontroller (crypto + network only)
- A Nest Atomic on a Raspberry Pi (crypto + network + storage)
- A sensor node streaming data via songBird to a gate
- A pipette-mounted data acquisition system handling provenance and streaming
- An environmental monitor (pH, temperature, GPS) publishing to the mesh
- An Akida NPU edge classifier on a Coral board

fieldMouse deployments share these properties:

| Property | Description |
|----------|-------------|
| **Minimal** | Smallest subset of atomics for the niche — no unused primals |
| **Embedded-first** | Targets RISC-V, ARM (aarch64/armv7), and constrained SoCs |
| **ecoBin compliant** | Pure Rust, zero C, cross-compiles with `cargo build --target` |
| **Mesh-native** | Connects to the broader ecosystem via songBird or TCP fallback |
| **Provenance-aware** | Even the smallest fieldMouse signs data via bearDog |

The evolutionary ladder extends downward:

```
NUCLEUS     (full primal composition — gate)
  ↓
Niche       (biomeOS deploy graph — selected primals)
  ↓
fieldMouse  (minimal atomic/chimera — embedded, sensor, edge)
```

A fieldMouse on a pipette handles data streaming for the instrument — sample ID,
timestamp, GPS, measurement, provenance signature — and publishes to the mesh.
A fieldMouse on a soil probe does the same for pH, moisture, temperature. A
fieldMouse on an Akida board classifies microbial communities in real time from
MinION streaming data. The primals are the same. The deployment is minimal.

See `FIELDMOUSE_DEPLOYMENT_STANDARD.md` for the specification.

### guideStone

The **verification class** for ecoBins that produce reproducible, self-proving
output. Where the binary ladder describes structure (UniBin → ecoBin → genomeBin)
and deployment classes describe context (NUCLEUS → Niche → fieldMouse),
guideStone describes **what the output means** — that the computation's results
are their own proof of correctness.

guideStone is not a primal. It is not a binary type. It is a **quality
certification** — an orthogonal dimension that any ecoBin can carry when its
output satisfies five properties:

| Property | Requirement |
|----------|-------------|
| **Deterministic** | Same input, same binary, any hardware → same output within named tolerances |
| **Reference-traceable** | Every numeric claim traces to a paper, standard, constant, or mathematical proof |
| **Self-verifying** | Checksums, CRC, hashes, or signatures validate integrity without trusting the channel |
| **Environment-agnostic** | ecoBin compliant, no external dependencies, no sudo, CPU-only path covers full output |
| **Tolerance-documented** | Every threshold has a physical or mathematical derivation — no magic numbers |

Any primal, spring, or composition can have a guideStone edition:

- A **spring guideStone** is the validation artifact with derived (not tuned) tolerances
- A **primal guideStone** is the reference edition — pinned, fully auditable, validated
  against external test vectors (e.g., bearDog's Ed25519 against NIST/RFC vectors)
- A **composition guideStone** certifies an end-to-end pipeline (e.g., Chuna Engine
  producing ILDG gauge configurations, helixVision producing reproducible variant calls)

guideStone is complementary to the provenance trio. guideStone certifies the
computation (reproducible output). The trio certifies the event (who, when, where,
attribution). Both together produce a Novel Ferment Transcript — the highest-grade
digital artifact in the ecosystem.

The name pairs with **guidePost** (the planned philosophy/ethics repository):
guidePost points the way in human terms; guideStone is the demonstrable proof
in computational terms.

See `GUIDESTONE_STANDARD.md` for the specification.
See `whitePaper/gen4/architecture/GUIDESTONE.md` for the concept paper.

### Loam Certificate

An **intracellular provenance artifact** — not a transport credential. Loam
Certificates are the ecosystem's sovereign ownership, lending, and provenance
mechanism. They are minted by loamSpine (`certificate.mint`), transferred
(`certificate.transfer`), loaned (`certificate.loan`), escrowed
(`certificate.escrow`), and returned. Their lifecycle is:
DAG fermentation (rhizoCrypt) → dehydration → permanent spine (loamSpine) →
attribution braid (sweetGrass).

Loam Certificates live entirely within the cytoplasm. They never cross the
drawbridge. They are the building blocks of Novel Ferment Transcripts.

**Do not confuse with TLS credentials.** TLS/ACME x.509 certificates are
*drawbridge transport credentials* — external golden cage artifacts managed
by Caddy (current) or bearDog gatehouse (sovereignty target). TLS credentials
mediate weak → ionic bond escalation at the outer membrane. Loam Certificates
mediate ownership and provenance within the covalent interior. They share a
word; they share nothing else.

| | Loam Certificate | TLS Credential |
|---|---|---|
| **Owner** | loamSpine | Caddy / bearDog gatehouse |
| **Layer** | Cytoplasm (intracellular) | Outer membrane (drawbridge) |
| **Lifecycle** | mint → transfer → loan → return | issue → renew → revoke |
| **Backing** | Provenance trio + rootPulse | Let's Encrypt / ACME (golden cage) |
| **Bond type** | Covalent (sovereign) | Weak → ionic (endosymbiosis target) |
| **Permanence** | Permanent (append-only spine) | Ephemeral (90-day rotation) |

### Novel Ferment Transcript (NFT)

Memory-bound digital objects fermented through the provenance trio. Not
blockchain NFTs — ferment transcripts are provenance-tracked creative artifacts
with attribution chains via sweetGrass, permanence via loamSpine Certificates,
and ephemeral workspace via rhizoCrypt DAGs. The fermentation is irreversible
and time-bound: value accumulates from history, not artificial scarcity.

A Novel Ferment Transcript is a Loam Certificate whose provenance chain
records the full fermentation — every interaction, transformation, and
attribution that shaped it. Game keys, scientific chain-of-custody records,
sample provenance chains, and creative artifacts are all NFTs.

---

## The Composition Layer

### BYOB (Bring Your Own Binaries)

The deployment model for gen4 products. Products consume pre-built primal binaries
from `plasmidBin/` via `plasmidbin fetch` (Rust CLI) — they never compile primal source. This
enforces zero source coupling between products and primals.

### Niche YAML

A YAML metadata file that declares what a deployment IS — its organisms (primals
and chimeras), their interactions (capability-call wiring), and customization
options. The niche YAML is the identity document for a composition; the deploy
graph is its execution plan.

Example: `esotericWebb/niches/esoteric-webb.yaml` declares 10 organisms, 5
interaction edges, and 3 customization options.

### Primal Launch Profile

A TOML configuration file that tells a product's launcher how to invoke each
primal binary: subcommand, port flag, health method, readiness timeout. Launch
profiles bridge the gap between "binary exists in plasmidBin" and "primal is
running and healthy."

Example: `esotericWebb/config/primal_launch_profiles.toml`

### sporeGarden Product

A gen4 artifact in the `sporeGarden/` GitHub organization. Products compose
primals into tools people use — games, science platforms, creative tools. They
follow the BYOB model, consuming binaries via IPC and defining their composition
through deploy graphs + niche YAML.

Examples: esotericWebb (CRPG engine), blueFish (PFAS analytical chemistry),
helixVision (genomics platform), initioChem (CompChem FEL explorer).

### PrimalBridge

A product-side JSON-RPC client that wraps capability calls to running primals.
Each product writes its own bridge — `esotericWebb` has a `PrimalBridge` with 23
methods covering 8 primal domains. The bridge handles graceful degradation when
optional primals are absent.

### Primal Resolution Order

The 8-step discovery sequence biomeOS uses to find primal sockets at runtime:
env hint → capability sockets → XDG → abstract → /tmp → socket registry →
Neural API → TCP fallback. See `COMPOSITION_PATTERNS.md` §4.

---

## The Propagation Layer

### pappusCast

The **auto-propagation daemon** for projectNUCLEUS. Named for the dandelion
pappus — the parachute structure that carries seeds to new ground. Each
validated notebook is a seed; pappusCast disperses them from the compute
workspace to the public observer surface.

Self-pollination (auto-validation within workspace) and cross-pollination
(propagation to public surface) mirror the dandelion's reproductive strategy.
Micro-species (per-notebook variants) and endemic species (gate-specific
content) map naturally to the botanic model.

Key properties:
- **Tiered validation**: Light (on-change: JSON valid, kernel, title), Medium
  (periodic: execute + check errors), Heavy (~6h: diff, changelog, regression)
- **Adaptive rate limiting**: Publish interval scales with active JupyterHub
  users — `min(BASE_MINUTES * max(1, active_users), MAX_MINUTES)`
- **Snapshot architecture**: Public surface holds managed copies, not live
  symlinks — validated, stable, decoupled from live edits
- **Quarantine**: Notebooks that fail validation are moved aside, not published
- **Evolution path**: Python (now) → Rust binary → pappusCast primal

pappusCast is not a primal (yet). It is a Python daemon in the projectNUCLEUS
deployment tooling. When evolved to Rust, it will follow the UniBin/ecoBin
pattern and integrate with biomeOS composition for multi-gate propagation.

### tunnelKeeper

A **Rust crate** in the projectNUCLEUS validation tree for programmatic
Cloudflare tunnel health checks, DNS resolution, and config file parsing.
tunnelKeeper is the first step toward Rust-native Cloudflare interaction,
replacing shell-based health probes with structured Rust types.

tunnelKeeper is not a primal. It is a validation tool that may eventually
absorb into songBird or become a standalone tunnel management binary as the
sovereignty evolution progresses (Cloudflare → WireGuard → Songbird NAT).

### darkforest

The **pure Rust security validator** for NUCLEUS deployments. A 939KB modular
binary with zero runtime dependencies. Performs pen testing (3 threat actors),
protocol fuzzing (13 primals + JupyterHub), and cryptographic strength
validation (13 checks). Produces structured JSON reports for auditable
security posture tracking.

darkforest embodies the Dark Forest security posture: reveal nothing to probes,
fail closed, log everything, trust nothing external. The name is intentional —
the validator assumes the network is hostile.

---

## The Binary Evolution Ladder

### ecoBin

An **ecoBin** is a statically-linked, cross-compiled Rust binary — zero C
dependencies on the critical path. ecoBins compile for all Cargo target triples
and are the base unit of the depot system. Every primal binary is an ecoBin.

### genomeBin

A **genomeBin** is the evolved ecoBin — a binary that works across all deployed
operating systems and architectures without code changes. The name reflects that
the binary carries its full "genome" (capabilities, platform detection, IPC
selection) intrinsically.

genomeBin targets are tiered by deployment status:

| Tier | Targets | Meaning |
|------|---------|---------|
| **Tier 1 genomeBin** | x86_64-linux-musl, aarch64-linux-musl, x86_64-windows-gnu, aarch64-android, armv7-linux-musl | MUST — deployed gates exist |
| **Tier 2** | x86_64-apple-darwin, aarch64-apple-darwin | SHOULD — deployment imminent |
| **Tier 3 PROVEN** | riscv64, ppc64le, s390x, sparc64, i686, arm32 | Compiled, no deployed gate |
| **Tier 4 FUTURE** | wasm32-wasip1, loongarch64, freebsd, illumos, redox | Horizon |

### Silicon-Deistic Deployment

The architectural principle that **hardware is truth, OS is abstraction**.
Tower Atomic (bearDog + songBird + skunkBat) is the universal platform layer.
Just as songBird abstracts ports and mesh topology, Tower Atomic abstracts OS
differences: UDS vs named pipes vs TCP, systemd vs Windows Service vs launchd,
`/opt/membrane` vs `%APPDATA%`. Primals detect their platform at runtime and use
the best available mechanism. `bind_mode`, `target`, and other OS-specific manifest
fields are transitional — they document what primals auto-detect internally.

Goal: a gate enrolls with only **name + composition + physical proof**. Everything
else is intrinsic.

### Autonomous Enrollment

The **zero-operator gate provisioning system** shipped in Wave 155a. A gate
self-enrolls by running `gate-enroll.sh` (Linux) or `gate-enroll.ps1` (Windows)
with a hub address and physical proof (enrollment token, FIDO2 attestation, or
beacon proximity). The enrollment endpoint on golgiBody (`mesh.gate_enroll`)
handles: physical proof verification → IP pool allocation → WireGuard peer
registration → Forgejo SSH key creation → family seed delivery → genetic
enrollment.

### Self-Registration

Gates declare their own name and composition during enrollment. No manifest
pre-definition is needed — `ecosystem_manifest.toml` gate entries are informational,
not authoritative. Any hardware anywhere can become a gate by running the
enrollment script with a valid trust token.

### Composition

A **composition** is a named set of primals that defines a gate's capabilities.
Compositions are hierarchical — every composition includes Tower Atomic base:

| Composition | Primals | Count | Use Case |
|-------------|---------|-------|----------|
| **tower** | bearDog, songBird, skunkBat | 3 | Minimal trust boundary |
| **compute** | Tower + toadStool, barraCuda, coralReef, biomeOS | 7 | GPU/HPC workloads |
| **nest** | Tower + nestGate, rhizoCrypt, loamSpine, sweetGrass | 7 | Content-addressed storage |
| **full** | All 13 foundation primals + squirrel | 13 | Complete NUCLEUS |

### BTSP (BearDog Trust Signaling Protocol)

The **handshake protocol** all primals use for outbound connections. BTSP
ClientHello is shipped on all 13/13 primals (Wave 151d). When
`BEARDOG_UDS_REQUIRE_BTSP=1`, local UDS connections require BTSP proof before
any method call is accepted.

---

## Quick Lookup

| Term | One-Line Definition |
|------|---------------------|
| **Gate** | A physical computer running the ecoPrimals stack |
| **Primal** | A self-contained Rust binary providing domain primitives |
| **Primitive** | The atomic unit of capability a primal provides |
| **Spring** | A validation environment that composes primals and validates science (gen3) |
| **Garden** | A user-facing product composing primals via BYOB (gen4, e.g. esotericWebb) |
| **Atomic** | A named primal composition pattern (Tower, Node, Nest, NUCLEUS) |
| **Niche** | A biomeOS BYOB deployment — primals composed via deploy graph |
| **Deploy graph** | TOML DAG defining germination order and capability wiring |
| **Chimera** | A fused multi-primal binary with unified API |
| **Germination** | Starting a primal until its socket is ready |
| **biomeOS** | The orchestration substrate running on a gate |
| **NUCLEUS** | Full primal composition (all atomics + Squirrel) |
| **Plasmodium** | Multi-gate collective (2+ bonded NUCLEUS instances) |
| **metalForge** | Evolution context where springs work on hardware concepts (GPU/CPU/NPU) |
| **baseCamp** | Cross-spring paper program — validation to exploration (18 papers) |
| **metaPrimal** | Conceptual repo (wateringHole, whitePaper, sourDough) — pre-binary, documentaion |
| **Paper parity** | Spring output matches published figures within named tolerance |
| **Absorption** | Spring replaces local math with barraCuda canonical version |
| **Delegation** | Primal routes work to another primal via IPC |
| **Handoff** | Session continuity document in wateringHole |
| **Fossil record** | Archived handoffs — the project's geological history |
| **NestGate (primal)** | Data storage primal: content-addressed storage, capability-based service discovery |
| **nestgate.io (domain)** | BirdSong beacon domain: Dark Forest gated public rendezvous at `api.nestgate.io`, served by biomeOS via Cloudflare Tunnel. See `DOMAIN_INFRASTRUCTURE.md` |
| **Ancestor beacon** | Generic mito-beacon rendezvous that can host multiple family beacons and guide new nodes to correct genetics |
| **Lysogeny** | Area denial through open AGPL prior art |
| **scyBorg** | Triple copyleft: AGPL-3.0 (code) + ORC (mechanics) + CC-BY-SA (docs) |
| **Symbiotic exception** | AGPL Section 7 grant to allies based on reciprocal benefit |
| **Suppression inversion** | Owning nothing makes the project untargetable |
| **AI authorship paradox** | Copyright uncertainty harms exclusivity claimants, not the commons |
| **cellMembrane** | Selective permeability layer — private ops repo deploying fieldMouse Tower to VPS for relay/TLS/content channels |
| **fieldMouse** | Minimal deployable ecoPrimals — smallest atomic/chimera for embedded/sensor/edge niches |
| **guideStone** | Verification class — ecoBin quality grade certifying reproducible, self-proving, reference-traceable output |
| **Spore Ownership Matrix** | Three-way ownership split: domain science (springs), spore envelope (lithoSpore), NUCLEUS gateway (biomeOS). See `operations/SPORE_OWNERSHIP_MATRIX.md` |
| **primalSpring** | Coordination spring — validates ecosystem composition, graph execution, emergent systems, bonding |
| **BYOB** | Bring Your Own Binaries — gen4 products consume pre-built primal binaries, never source |
| **Niche YAML** | YAML metadata declaring a composition's organisms, interactions, and customization options |
| **Primal launch profile** | TOML config for how a product launcher invokes each primal binary |
| **sporeGarden product** | A gen4 tool composing primals for end users (e.g., esotericWebb, blueFish, helixVision, initioChem) |
| **PrimalBridge** | Product-side JSON-RPC client wrapping capability calls to running primals |
| **Primal resolution order** | 8-step discovery: env → capability → XDG → abstract → /tmp → registry → Neural API → TCP |
| **NUCLEUS Gateway** | biomeOS bidirectional spore interface — `biomeos nucleus ingest` absorbs spores into nest_atomic; `biomeos nucleus emit` creates spores from NUCLEUS state |
| **pseudospore-core** | Shared Rust crate (lithoSpore) for spore envelope primitives — 10 `pub mod` (9 API + `error`): `blake3_manifest`, `braid_envelope`, `domain_profile`, `envelope`, `error`, `livespore`, `receipts`, `scope`, `tarball`, `validation`. Consumer API: `PseudoSporeEnvelope::load()` + `validate()` with typed `SporeError` (thiserror). Includes GUIDESTONE-GRADE derivation anchoring checks. lithoSpore wired (NC-1.3); biomeOS v3.81+ created `biomeos-pseudospore` (NC-1.4 resolved) |
| **pappusCast** | Auto-propagation daemon — dandelion-seed dispersal from workspace to observer surface |
| **tunnelKeeper** | Rust crate for Cloudflare tunnel health, DNS resolution, config parsing |
| **darkforest** | Pure Rust security validator — pen test + fuzz + crypto strength (939KB, zero deps) |
| **soundStage** | Transparent ceremony observation — see entropy flowing, mixing, derivation. Anti-black-box. |
| **Snapshot architecture** | Public surface holds managed copies, not live symlinks — stable observer view |
| **Tiered validation** | Light (structural) → Medium (execution) → Heavy (regression) validation pipeline |
| **plasmidBin** | Binary distribution repo — pre-built musl-static NUCLEUS primals, Rust CLI, automated harvest |
| **postPrimordial** | Deployment regime where all NUCLEUS binaries come from plasmidBin — no local builds |
| **Fossilization** | Moving resolved content to fossilRecord, replacing with pointer stub |
| **Wave** | Named coordination pulse — ecosystem synchronization event tracked in glacial readiness |
| **Stadial** | Hard convergence phase — fitness gate that culls non-conforming patterns |
| **Interstadial** | Warming phase — diversification and specialization under constraint |
| **goldenCage** | External services bootstrapping sovereignty (GitHub, Cursor, Cloudflare) — chrysalis thesis |
| **Gatehouse** | Bond escalation broker — single external surface accepting weak interactions, promoting to ionic/metallic/covalent via authentication |
| **Darkforest** | Invisible mesh interior — zero external ports, all discovery via mesh.peers and capability.call, prevents sovereignty leakage |
| **Drawbridge** | Single crossing point between gatehouse and darkforest — songBird HTTP proxy translating external HTTP to capability-routed mesh semantics |
| **Bond escalation** | Progressive trust promotion: weak → ionic (BTSP token) → metallic (Mito-Beacon) → covalent (nuclear session) |
| **Bond degradation** | Outward trust weakening across VPS diderm: covalent (gate) → metallic (inner) → ionic (pepti) → weak (GitHub) |
| **Endosymbiosis** | Progressive internalization of external systems into sovereign infrastructure (weak → covalent over time) |
| **Capability advertisement** | Drawbridge auto-registers route capabilities into IPC registry and announces to mesh peers at startup (Wave 133d) |
| **Genetic enrollment** | Two-layer trust: mito gate (family membership) + nuclear lineage distance (derivation hops → trust tier) |
| **Tower Shadow** | Shadow deploy mode — Tower runs alongside WG, collects comparative metrics without affecting production |
| **LAN mesh routing** | `preferred_address()` prefers `lan_addr` for same-switch peers over WG overlay (353x latency difference) |
| **CallerContext** | Per-UDS-connection identity (SO_PEERCRED) wired into method gate for access control |
| **Chimera Phase 0** | First chimera step — extract bearDog hot-path crypto into shared library for in-process use |
| **EndpointType** | Routing variant: `Local` for LAN direct paths (sub-ms) vs `Overlay` for WG relay (100ms+) |
| **K-Derm trust tiers** | Outer/inner/data domain classification in `capability_registry.toml` — method-level access control |
| **Shadow benchmark** | Continuous Tower vs WG metrics collected by `tower-shadow.timer` (hourly, JSON output) |
| **Nest Atomic (expanded)** | Wave 151 data layer: nestGate CAS + loamSpine DAG + rhizoCrypt cross-repo + sweetGrass braids + rootPulse orchestration |
| **rootPulse** | biomeOS-orchestrated Provenance Trio composition — replaces waterFall with content-addressed provenance |
| **Keystore2 binder** | Android 12+ native API for hardware-backed key operations without JVM — production path for bearDog StrongBox |
| **Crypto delegation** | songBird routes all crypto to bearDog over IPC — 6/6 seams validated Wave 150 (chimera-ready) |
| **libtower.so** | Chimera Phase 0 extraction target — bearDog crypto + songBird routing + skunkBat defense as shared library |
| **Silicon Atheism** | Platform-agnostic dispatch — code compiles for all targets, probes capabilities at runtime (no compile-time branching in business logic) |
| **genomeBin** | Evolved ecoBin — binary carrying full platform awareness, working across all deployed OS/arch without code changes |
| **Silicon-deistic deployment** | Hardware is truth, OS is abstraction. Tower Atomic handles platform differences intrinsically |
| **Autonomous enrollment** | Zero-operator gate provisioning — `gate-enroll.sh`/`.ps1` → `mesh.gate_enroll` → meshed |
| **Self-registration** | Gates declare name + composition during enrollment, no manifest pre-definition needed |
| **Composition** | Named primal set: tower (3), compute (7), nest (7), full (13) — all include Tower base |
| **BTSP** | BearDog Trust Signaling Protocol — handshake on all 13/13 primals, defense-in-depth |
| **golgiBody depot** | Sole WAN depot — all genomeBins served via Caddy TLS at `depot.primals.eco` |
| **Gate enmeshment** | Glacial goal — Tower Atomic deployment across all platforms, then Nest Atomic for data |

---

## FILE: `graphs/README.md`

# Cascade Graphs — biomeOS Composition Patterns

Declarative graph definitions for primal-composed operations. Each graph
describes a multi-step flow that membrane-shadow's NeuralBridge routes
through biomeOS with try-primal-first semantics.

## Graphs

| Graph | Trigger | Flow |
|-------|---------|------|
| `waterfall_publish` | `waterfall.publish` | Full cascade: code → impulse → provenance → transport |
| `impulse_post_signed` | `impulse.post` | Signed impulse with DAG recording and mesh relay |
| `context_weave_anchored` | `context.weave` | Context braid with validation and optional anchoring |

## Architecture

```
waterfall_publish (composition)
├── push_to_forgejo         membrane    temporal.sync
├── compose_impulse         membrane    impulse.compose
├── sign_impulse            bearDog     auth.sign
├── store_impulse           membrane    impulse.store
├── record_dag              rhizoCrypt  dag.append
├── weave_context           membrane    context.weave      (wave_boundary)
├── validate_braid          sweetGrass  braid.validate     (wave_boundary)
├── anchor_state            loamSpine   ledger.stamp       (wave_boundary)
├── push_mirror             membrane    mirror.push_sync
└── relay_impulse           songbird    mesh.publish
```

## Fallback Semantics

- `skip`: step is omitted if primal unavailable (non-critical)
- `defer`: step is queued for later execution (network-dependent)
- No fallback: step is required; cascade fails if primal unavailable

## Status

These graphs are declarative specifications. The NeuralBridge in
membrane-shadow routes through biomeOS when available, falling back
to local shadow implementations. Full biomeOS graph execution requires
primals to be deployed and registered.

---

## FILE: `healthspring/HEALTHSPRING_COMPOSITION_GUIDANCE.md`

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

---

## FILE: `hooks/cursor/context-braid-workflow.rule.md`

# Context Braid Workflow — K-NOME Interaction Surface

This workspace uses the ecoPrimals **context braid** system for structured developer state across gates. Before starting substantive work, sense the mesh state.

## On Session Start

Run `membrane context.sense --all` to load the current mesh state. This replaces manual guidance blurbs. The output contains structured TOML braids with:

- **focus** — what is actively being worked on at each gate
- **breadcrumbs** — file paths, entry points, relevant code locations
- **next** — upcoming actions and handoff tasks
- **blockers** — what's preventing progress
- **notes** — standing directives (architecture constraints, style guides)

Also run `membrane potential.sense` to check for pending impulses (inter-gate coordination messages that may require action).

## On Work Completion

When completing a significant milestone or handing off work, weave a context braid:

```bash
membrane context.weave \
  --project <path> \
  --summary "<what was done / current state>" \
  --status <active|paused|blocked|complete> \
  --breadcrumbs "<relevant files>" \
  --next "<what should happen next>"
```

## Standing Conventions

- AGPL-3.0 licensing on all primal code
- 1000 line maximum per file
- Zero-copy where possible
- Primal code has self-knowledge only — discover capabilities at runtime, no hardcoding
- No 2^n enumeration of peers — use capability registries
- Commit messages follow: `feat:`, `fix:`, `docs:`, `refactor:` prefixes
- Push to `forgejo` only — VPS auto-mirrors to GitHub (external ledger)

## Gate Identity

This workspace resolves gate identity from `$GATE_NAME` or the `.gate` file at workspace root. The current gate identity determines which context braids are "local" vs "mesh".

## Three-Layer Coordination

| Layer | Command | Purpose |
|-------|---------|---------|
| Context braids | `context.weave/sense/clear` | Ephemeral developer state (sweetGrass external) |
| Impulses | `impulse.post`, `potential.sense` | Event-driven coordination (rhizoCrypt external) |
| Git | Standard git workflow | Permanent record (loamSpine external) |

---

## FILE: `hooks/cursor/README.md`

# Cursor IDE Hooks — K-NOME Context Integration

Reference copies of the Cursor hook and rule files that implement the K-NOME workflow:
context braids auto-injected into IDE sessions on start.

## Installation

Copy these files to your workspace `.cursor/` directory:

```bash
# From workspace root (e.g. ~/Development/ecoPrimals)
mkdir -p .cursor/hooks .cursor/rules
cp infra/wateringHole/hooks/cursor/hooks.json .cursor/hooks.json
cp gardens/cellMembrane/deploy/hooks/cursor/context-sense.sh .cursor/hooks/context-sense.sh
cp infra/wateringHole/hooks/cursor/context-braid-workflow.rule.md .cursor/rules/context-braid-workflow.md
chmod +x .cursor/hooks/context-sense.sh
```

> **Note**: `context-sense.sh` lives in `cellMembrane` (its code owner). wateringHole
> provides the hook config and rule (comms layer); cellMembrane provides the script.

## What it does

On `sessionStart`, the hook:

1. Runs `membrane context.sense --all` — loads all context braids across the gate mesh
2. Runs `membrane potential.sense` — checks for pending impulses requiring action
3. Injects the combined output as `additional_context` for the agent

The rule file provides fallback instructions for agents when the hook mechanism
is not available (e.g. on gates without Cursor hook support).

## Requirements

- `membrane` binary in PATH or built at `gardens/cellMembrane/target/release/membrane`
- `python3` available for JSON escaping
- `.gate` file at workspace root (or `GATE_NAME` env var) for identity resolution

## K-NOME Pattern

The blurb IS the program. `context.weave` encodes the human directive.
`context.sense` delivers it to the agent. The membrane is the transport.
The hook automates delivery so the human says "proceed" and the agent
already has the program loaded.

---

## FILE: `hooks/forgejo/README.md`

# Forgejo VPS Hooks — K-Derm Diderm Relay Chain

Server-side hooks for the three-node K-Derm diderm envelope. The push flow
traverses each layer with proper bond-type degradation:

```
Gate ──covalent──→ golgiBody-inner (cis: receives)
                       │
                       │ metallic bond (post-receive webhook)
                       ▼
                   peptidoglycan (structural: sync + impulse cascade)
                       │
                       │ ionic bond (SSH relay)
                       ▼
                   golgiBody-ext (trans: ships to extracellular)
                       │
                       │ weak bond (git push)
                       ▼
                   GitHub (extracellular linear ledger)
```

## Scripts

> **Wave 66**: Scripts relocated to their code owners (`cellMembrane/deploy/hooks/forgejo/`).
> wateringHole retains this architecture reference as the K-Derm diderm relay spec.

| Script | Runs On | Bond | Owner |
|--------|---------|------|-------|
| `pepti-sync-relay.sh` | peptidoglycan | Metallic→Ionic | cellMembrane |
| `ext-github-push.sh` | golgiBody-ext | Ionic→Weak | cellMembrane |
| `impulse-relay-hook.sh` | peptidoglycan | — | cellMembrane |
| `setup-push-mirrors.sh` | — | — | Fossilized (pre-diderm) |

## K-Derm Diderm Flow

### Full relay chain (target architecture)

1. Gate pushes to Forgejo on golgiBody-inner (covalent SSH)
2. Forgejo post-receive webhook notifies peptidoglycan
3. `pepti-sync-relay.sh` on peptidoglycan:
   - Pulls from Forgejo (metallic: inner→structural)
   - Runs impulse cascade (detect + relay pending impulses)
   - SSHs to golgiBody-ext, triggers `ext-github-push.sh`
4. `ext-github-push.sh` on golgiBody-ext:
   - Pushes to GitHub (weak: outer→extracellular)
   - golgiBody-ext holds the only GitHub SSH write credentials

### SSH key placement (bonding model)

| Node | GitHub SSH | Forgejo SSH | Bond Types |
|------|-----------|-------------|------------|
| golgiBody-inner | None (revoked) | Yes (Forgejo owns it) | Covalent, Metallic |
| peptidoglycan | None (revoked) | Yes (pull from Forgejo) | Metallic |
| golgiBody-ext | **Yes (push to GitHub)** | Yes (pull from Forgejo) | Ionic, Weak |

Only the outer membrane (trans face) has extracellular write access.

## Setup

### peptidoglycan

```bash
# Scripts are deployed from cellMembrane
cd /opt/ecoPrimals/gardens/cellMembrane
membrane deploy.hooks --target peptidoglycan
```

### golgiBody-ext

```bash
# Scripts are deployed from cellMembrane
cd /opt/ecoPrimals/gardens/cellMembrane
membrane deploy.hooks --target golgiBody-ext
```

### golgiBody-inner (Forgejo webhook)

In Forgejo → wateringHole repo settings → Webhooks:
- URL: `http://[RELAY_PUBLIC]:3001/hooks/pepti-sync-relay`
- Content type: `application/json`
- Trigger: Push events
- Branch filter: `main`

---

## FILE: `operations/DEPLOYMENT_VALIDATION_STANDARD.md`

# Deployment Validation Standard

**Status**: Ecosystem Standard
**Version**: v1.2.0
**Date**: May 26, 2026
**Authority**: wateringHole (ecoPrimals Core Standards)
**Driven by**: plasmidBin v2026.03.25 live validation, benchScale IPC compliance testing

---

## Purpose

This standard defines the requirements for a primal to be **deployment-valid** —
meaning it can be fetched from plasmidBin, started by `plasmidbin start`, and
validated by `benchscale validate ipc` or equivalent probes without any source
code, Rust toolchain, or primal-specific knowledge on the consumer's machine.

Deployment validity is the **runtime complement** to the build-time standards in
`UNIBIN_ARCHITECTURE_STANDARD.md` and `PRIMAL_IPC_PROTOCOL.md`. A primal can
pass all build checks and still be deployment-invalid if its runtime behavior
diverges from the contract.

---

## The Deployment Contract

A primal binary fetched from plasmidBin MUST satisfy all of the following
when started by an orchestrator (`plasmidbin start`, biomeOS, benchScale):

### 1. Health Triad (MANDATORY)

Every primal MUST respond to the standard health triad over its **primary
JSON-RPC transport** (UDS or TCP, newline-delimited):

```json
{"jsonrpc":"2.0","method":"health.liveness","params":{},"id":1}
→ {"jsonrpc":"2.0","result":{"status":"healthy"},"id":1}

{"jsonrpc":"2.0","method":"health.readiness","params":{},"id":2}
→ {"jsonrpc":"2.0","result":{"status":"healthy","version":"X.Y.Z","primal":"name"},"id":2}

{"jsonrpc":"2.0","method":"health.check","params":{},"id":3}
→ {"jsonrpc":"2.0","result":{"status":"healthy","version":"X.Y.Z","primal":"name"},"id":3}
```

**Method names are exact.** `toadstool.health`, `dag.health`, and
`compute.health` are NOT substitutes for `health.liveness`. Primal-prefixed
health methods MAY exist alongside the standard triad but do not replace it.

**Response format:**
- `health.liveness`: MUST return `{"status":"healthy"}` (or `"alive":true`).
  This is the keepalive — it answers "are you running?"
- `health.readiness`: MUST include `version` and `primal` name. Answers
  "are you ready to serve requests?"
- `health.check`: MUST include `version` and `primal` name. MAY include
  `uptime_secs`, `active_connections`, or domain-specific metrics.

**benchScale validation:**
```bash
benchscale validate ipc 127.0.0.1:<port>
# Reports COMPLIANT only when all 3 methods return valid JSON-RPC results
```

### 2. Socket-First, Port-Fallback (MANDATORY)

Primals MUST create a filesystem socket at startup:
```
$XDG_RUNTIME_DIR/biomeos/<primal>.sock
```

TCP ports are **fallback** for cross-gate, Docker, mobile, and testing.
When songBird is live, the entire ecosystem runs port-free on UDS.

`plasmidbin start` passes `--tcp-port` only when the caller explicitly
requests it. Without `--tcp-port`, the primal MUST still be reachable
via its UDS socket.

**Stale socket hygiene (May 18, 2026):** Primals MUST `unlink()` their
socket before `bind()` on startup. Primals SHOULD write a `{name}.pid`
file alongside the socket so consumers can verify liveness via `kill(pid, 0)`
without incurring connect overhead. On graceful shutdown, primals MUST
remove both the socket and PID file. See `CAPABILITY_BASED_DISCOVERY_STANDARD.md`
§5-6 for the consumer-side connect-probe and negative caching patterns.

### 3. CLI Convergence (MANDATORY)

Per `UNIBIN_ARCHITECTURE_STANDARD.md` v1.1, the `server` subcommand MUST
accept `--port <PORT>` to bind TCP newline-delimited JSON-RPC.

Primals that use different flags MUST alias `--port`:

| Current Flag | Required Alias | Primal |
|-------------|----------------|--------|
| `--jsonrpc-port` | `--port` | loamSpine |
| `--http-address ADDR:PORT` | `--port PORT` | sweetGrass |
| `--listen ADDR:PORT` | `--port PORT` | bearDog (already has both) |

`plasmidbin start` absorbs current differences as a compatibility shim.
As primals converge, the shim shrinks to a single generic case.

### 4. Standalone Startup (MANDATORY)

Per `UNIBIN_ARCHITECTURE_STANDARD.md` v1.1, primals MUST start without
`FAMILY_ID`, `NODE_ID`, or any other identity variables. Default to
`standalone` or generate a transient identity.

**Violation found:** bearDog v0.9.0 hard-fails with
`NODE_ID or BEARDOG_NODE_ID must be set` — this blocks zero-config deployment.

### 5. Capability Advertisement (RECOMMENDED)

Primals SHOULD respond to `capabilities.list` with their full capability set:

```json
{"jsonrpc":"2.0","method":"capabilities.list","params":{},"id":1}
→ {"jsonrpc":"2.0","result":{"capabilities":["crypto.sign","crypto.verify",...]},"id":1}
```

This enables automated validation: `metadata.toml` declares capabilities,
the running primal confirms them.

---

## Transport Discovery Matrix

Live validation (April 13, 2026 — Phase 40 NUCLEUS Complete) confirmed **ALL 13
primals support UDS with newline-delimited JSON-RPC**. 19/19 exp094 PASS.

| Primal | Newline TCP | HTTP TCP | UDS (filesystem) | UDS (abstract) | tarpc | Methods |
|--------|------------|----------|------------------|----------------|-------|---------|
| bearDog | 9100 ✓ | — | ✓ beardog-{family}.sock | — | — | 100 |
| songBird | — | 9200 (HTTP discovery) | ✓ songbird-{family}.sock | — | — | 79 |
| toadStool | — | — | ✓ toadstool-{family}.sock (BTSP auto-detect) | — | ✓ | 163 |
| barraCuda | — | — | ✓ math-{family}.sock (JSON-RPC via BTSP guard) | — | ✓ | 32 |
| coralReef | — | — | ✓ shader.sock | — | — | 10 |
| squirrel | — | — | ✓ squirrel-{family}.sock | @squirrel | — | 30 |
| nestGate | — | — | ✓ nestgate-{family}.sock | — | — | 30 |
| rhizoCrypt | — | 9701 (HTTP JSON-RPC) | ✓ rhizocrypt-{family}.sock | — | 9700 ✓ | 28 |
| sweetGrass | — | 9720 (REST + /jsonrpc) | ✓ sweetgrass-{family}.sock | — | ✓ | 32 |
| loamSpine | — (TCP opt-in via --listen) | — | ✓ loamspine-{family}.sock | — | ✓ | 34 |
| petalTongue | — | ✓ (web mode) | ✓ petaltongue-{family}.sock (--socket flag) | — | — | — |
| biomeOS | — | ✓ (API mode) | ✓ biomeos.sock | — | — | — |

**Standard requirement:** Every primal MUST have newline-delimited JSON-RPC
on at least one of: filesystem UDS or TCP. HTTP-wrapped JSON-RPC does not
satisfy this (it requires HTTP framing, breaking raw stream clients).

**Current compliance (April 13, 2026):**
- PASS: **ALL 13 primals** now have UDS filesystem sockets with JSON-RPC support.
- Key resolutions: rhizoCrypt UDS (LD-06, S37), loamSpine UDS-first (LD-09, v0.9.16),
  petalTongue `--socket` flag (v1.6.6), barraCuda JSON-RPC via BTSP guard line (LD-10),
  ToadStool BTSP auto-detect (LD-04), squirrel filesystem socket alongside abstract.

---

## plasmidBin Integration Requirements

### metadata.toml Transport Declaration

Each primal's `metadata.toml` SHOULD declare its transport surfaces so
`plasmidbin start` and `plasmidbin fetch` can make informed decisions:

```toml
[genomeBin.server]
tcp_port_env = "BEARDOG_PORT"
tcp_port_default = 9100
tcp_protocol = "jsonrpc-newline"     # or "http", "tarpc"
socket_flag = "--socket"
port_flag = "--port"                 # MUST be "--port" per UniBin v1.1
listen_flag = "--listen"             # optional full addr:port form
```

The `tcp_protocol` field tells orchestrators what wire format to expect,
enabling benchScale to choose the right validation method.

### Checksum Hygiene

Binaries MUST be built with `--remap-path-prefix` and `strip = true` per
`SECRETS_AND_SEEDS_STANDARD.md`. `plasmidbin harvest` warns when binaries
contain build-machine paths.

---

## Validation Flow

The standard validation flow for any plasmidBin deployment:

```
1. Clone plasmidBin
2. cargo run -p plasmidbin -- fetch --all
   → downloads arch-matched binaries from GitHub Releases
   → verifies BLAKE3 checksums against checksums.toml

3. cargo run -p plasmidbin -- start <primal> --tcp-port <PORT>
   → maps generic flags to per-primal CLI
   → starts binary, waits 2s, checks liveness

4. benchscale validate ipc 127.0.0.1:<PORT>
   → probes health.liveness, health.readiness, health.check
   → reports COMPLIANT or NON-COMPLIANT

5. For full composition validation:
   cargo run -p plasmidbin -- launch --composition full
   → starts all primals, probes each health
   → optionally probe cross-primal capabilities
```

---

## Per-Primal Fix Path

Based on live validation April 5, 2026 (plasmidBin v2026.03.25):

| Primal | Deployment Status | Required Fix |
|--------|------------------|--------------|
| bearDog | ✓ TCP COMPLIANT | Fix standalone startup (NODE_ID hard-fail) |
| songBird | ✓ UDS HEALTHY | Add `--port` for newline TCP (currently HTTP-only on TCP) |
| toadStool | ✓ UDS HEALTHY | Implement `health.liveness/readiness/check` (currently `toadstool.health` only). Create filesystem socket (not just family-scoped). |
| squirrel | ✓ Abstract HEALTHY | Create filesystem socket alongside abstract `@squirrel`. |
| sweetGrass | ✓ HTTP HEALTHY | Add `--port` alias. Add newline JSON-RPC on TCP (currently HTTP-only). |
| rhizoCrypt | ⚠ tarpc REACHABLE | Add `--port` alias (currently `--tarpc-port`). Expose health triad on JSON-RPC 9701. |
| loamSpine | ✓ UDS HEALTHY | ~~Runtime nesting crash~~ **RESOLVED** (v0.9.16 — `mdns-sd`). `--port` alias implemented. |
| nestGate | — (not started) | Wire `--port` to TCP listener. Add `server` alias for `daemon`. |
| biomeOS | — (not started) | Add TCP-only mode (currently forces UDS when port specified). |
| petalTongue | — (not started) | Verify health triad on all transports. |

---

## Related Standards

- `PRIMAL_IPC_PROTOCOL.md` — Wire framing, transport tiers, health triad definition
- `UNIBIN_ARCHITECTURE_STANDARD.md` — `--port` convention, standalone startup
- `CAPABILITY_BASED_DISCOVERY_STANDARD.md` — Socket paths, symlinks, discovery tiers
- `ECOSYSTEM_COMPLIANCE_MATRIX.md` — Build-time compliance (Tiers 1–9)
- `SECRETS_AND_SEEDS_STANDARD.md` — Build hygiene for binary distribution
- `ECOBIN_ARCHITECTURE_STANDARD.md` — musl-static, PIE, portability

---

## Version History

### v1.0.0 (April 5, 2026)

**Initial Standard — Runtime Deployment Validation**

- Driven by first end-to-end plasmidBin validation: clone → fetch → start → probe
- 10 binaries fetched from GitHub Releases, 10 checksums verified
- 7 primals started, 5 healthy, 1 partial, 1 crash
- Transport diversity documented (5 patterns across 10 primals)
- Per-primal fix paths defined
- benchScale `validate ipc` established as the deployment acceptance test

---

## FILE: `operations/DISCOVERED_BY_STANDARD.md`

# DISCOVERED_BY Standard — Passive Discovery Audit

**Date**: 2026-07-14 (Wave 139a, reviewed 155h)
**Status**: Active standard
**Owner**: sporePrint team + overwatch
**Supersedes**: SHOW_HN_PUBLICATION.md as engagement strategy (that doc's rigor checklist is retained as internal quality bar only)

---

## The Pivot

SHOW_HN assumed **active presentation** to Hacker News — Y Combinator's audience, Y Combinator's platform, Y Combinator's extractive flywheel (funding → growth → exit → repeat). That engagement model embeds the ecosystem in exactly the gravity well it was built to escape. HN is a signal-targeting metric, not an engagement front.

DISCOVERED_BY assumes **passive discovery** — someone (AI bot, PI, homelabber, journalist, search engine) stumbles onto us without context, and the surface must hold up under scrutiny with zero preparation. No platform dependency. No single engagement front. The surface is sovereign and the quality bar is internal.

The AI bot review of Wave 138b proved this is the real threat model. An AI was able to:
1. Cross-reference institutional details to identify the human author
2. Find that "live validation results" were static snapshots
3. Note zero community engagement (0 stars, 0 issues, 0 PRs)
4. Flag page count inconsistencies as credibility issues
5. Identify broken pages (projectFOUNDATION 404) on the institutional path

**Discovery is the standard now.** Not presentation. Not platform engagement.

## Engagement Topology

The ecosystem's engagement surfaces align with sovereign and commons values:

| Surface | Why | Extractive? |
|---------|-----|-------------|
| **primals.eco** | The sovereign surface itself — owned, hosted, cryptographically anchored | No |
| **ORCID** | Academic commons, persistent researcher ID, not paywalled | No |
| **Zenodo** | Research data repository, DOI minting, CERN-operated commons | No |
| **Keyoxide** | Decentralized identity verification, no platform account required | No |
| **crates.io** | Open registry, community-governed, Rust Foundation | No |
| **Forgejo** | Self-hosted git, sovereign code hosting | No |
| **Reddit** | Community-moderated (r/homelab, r/selfhosted, r/rust) — imperfect but not VC-curated | Partial |
| **Medium (attsi)** | attsi's philosophical voice — attsi owns the voice, not the platform | Partial |

Surfaces intentionally **not** used as engagement fronts:
- **Hacker News** — Y Combinator property. Useful as internal quality bar ("would this survive HN scrutiny?"), not as engagement target.
- **Twitter/X** — extractive attention economy
- **LinkedIn** — professional extraction, identity leakage risk
- **Product Hunt** — VC showcase

The HN rigor checklist (evidence integrity, narrative readiness, honest limitations, comparison tables) is preserved as an internal standard in `SHOW_HN_PUBLICATION.md`. It answers: "if hostile experts examined us, would the claims hold?" That's a quality question, not a platform question.

---

## Persona Matrix

Every external-facing surface is evaluated against 6 discovery personas:

### 1. AI Bot (scraper/reviewer)
**Arrives via**: Crawls GitHub orgs + primals.eco, cross-references with public databases
**Evaluates**: identity.json, llms.txt, JSON-LD, ORCID, sitemap.xml, GitHub metadata
**Crack points**: Page count inconsistencies, stale certification manifest, identity leakage, content-manifest.toml not served

### 2. Homelabber (r/homelab, r/selfhosted)
**Arrives via**: Reddit link → outreach/homelab landing → tries to deploy
**Evaluates**: Can I run this today? What hardware do I need? Is there a binary?
**Crack points**: Scaffold maturity pages, no downloadable artifact, deploy step is TBD

### 3. PI / Grant Reviewer
**Arrives via**: Google Scholar, ORCID → primals.eco/lab/ or contact page
**Evaluates**: Lab evidence, provenance chains, reproducibility claims, institutional contact path
**Crack points**: Broken links on institutional path, primal count inconsistencies, no self-serve compute

### 4. Hacker News Reader
**Arrives via**: Show HN or related thread → primals.eco landing
**Evaluates**: Stats claims, try-it commands, GitHub activity, community signals
**Crack points**: Zero stars/issues/PRs, org bios sound like DevOps, blank repo descriptions, tarball not downloadable

### 5. LLM / Agent (llms.txt consumer)
**Arrives via**: robots.txt → llms.txt → site-index or sitemap.xml
**Evaluates**: Machine-readable structure, endpoint availability, content topology
**Crack points**: content-manifest.toml not served, site-index incomplete, stale counts in llms.txt

### 6. Journalist / Podcaster
**Arrives via**: Email contact or browsing primals.eco
**Evaluates**: Story, identity, claims, dual-voice model
**Crack points**: Triple naming confusion, dual-voice not explained to visitors, mycology branding

---

## Surface Audit Checklist

Run this checklist whenever content is deployed or presence changes. Each item is PASS/FAIL.

### GitHub Surface

| ID | Check | Command / Method |
|----|-------|-----------------|
| GH-1 | All repo descriptions contain "scientific" or domain keyword | `gh repo list {org} --json name,description` → grep |
| GH-2 | No blank descriptions on public repos | Same command, filter empty |
| GH-3 | Org websites point to primals.eco (not GitHub) | GitHub web UI check |
| GH-4 | Org bios lead with "scientific" framing | GitHub web UI check |
| GH-5 | ecoPrimal profile: no real name, no location, no institution | `gh api users/ecoPrimal` |
| GH-6 | No personal GitHub user in org memberships | `gh api orgs/{org}/members` |

### Live Site Surface

| ID | Check | Command / Method |
|----|-------|-----------------|
| LS-1 | All section indexes return 200 | `curl -sI https://primals.eco/{section}/` |
| LS-2 | Contact page institutional links resolve (no 404) | Manual click-through |
| LS-3 | identity.json valid JSON-LD | `curl -s https://primals.eco/identity.json \| python3 -m json.tool` |
| LS-4 | .well-known/aspe returns ASPE fingerprint | `curl -s https://primals.eco/.well-known/aspe` |
| LS-5 | All subdomains with DNS resolve over HTTPS | `curl -sI https://{sub}.primals.eco` |
| LS-6 | Security headers present (HSTS, CSP, X-Frame-Options) | `curl -sI` → inspect headers |
| LS-7 | Primal count consistent across landing, lab, contact, glossary | Manual audit or grep |
| LS-8 | Page count in certification manifest matches config.toml | Compare `manifest.json` vs `config.toml` |

### Agent Surface

| ID | Check | Command / Method |
|----|-------|-----------------|
| AG-1 | llms.txt section counts match reality | Compare stated vs actual page counts |
| AG-2 | content-manifest.toml served at web root | `curl -sI https://primals.eco/content-manifest.toml` |
| AG-3 | sitemap.xml returns 200 and valid XML | `curl -sI https://primals.eco/sitemap.xml` |
| AG-4 | robots.txt allows all agents | `curl -s https://primals.eco/robots.txt` |
| AG-5 | site-index lists all top-level pages | Manual comparison with sitemap.xml |

### Content Quality

| ID | Check | Command / Method |
|----|-------|-----------------|
| CQ-1 | No scaffold-maturity pages in top-level nav | Check maturity field in front matter |
| CQ-2 | Outreach pages either substantive or clearly labeled | Audit outreach/ front matter |
| CQ-3 | No hardcoded numbers that should use total_stat | `grep -r "175\|13 primal\|14,314" content/` |
| CQ-4 | Landing page naming clarification present | Check _index.md for ecosystem/site/domain explanation |
| CQ-5 | Try-it commands point to reachable resources | Manual test of clone + cargo test path |

---

## Audit Cadence

- **On every content deploy**: Run LS-1, LS-5, AG-2, LS-8 (automated — add to membrane content.rebuild)
- **Weekly**: Full GitHub surface audit (GH-1 through GH-6)
- **On content changes**: Run CQ-1 through CQ-5
- **On identity changes**: Full checklist

---

## Remediation Log

### Wave 139a (2026-07-14)

**GitHub Surface**:
- APPLIED: SIGNAL_SHARPENING repo descriptions to all ecoPrimals, sporeGarden, protoKarya repos
- REMAINING: Org bios and website URLs (requires GitHub web UI — documented in SIGNAL_SHARPENING.md)

**Site Content**:
- FIXED: Contact page projectFOUNDATION link (was 404, now points to lab validation summary)
- FIXED: Contact page primal count (was hardcoded "13", now uses total_stat shortcode)
- FIXED: Glossary NUCLEUS definition clarifies 13-on-gate vs 15-in-ecosystem distinction
- FIXED: Landing page naming clarification (ecoPrimals = ecosystem, sporePrint = site, primals.eco = domain)
- FIXED: Landing page guideStone tarball reference (replaced with plasmidBin getting-started link)
- FIXED: Certification manifest page count (271 → 304)

**Agent Surface**:
- FIXED: llms.txt outreach page count (11 → 14)
- FIXED: llms.txt story description (removed hardcoded "175+")
- FIXED: content-manifest.toml copied to static/ for web serving

**Infrastructure**:
- IDENTIFIED: footprint.primals.eco TLS broken (needs Caddy SNI/cert fix on golgi)

---

## Cross-References

- `whitePaper/gen5/thesis/SHOW_HN_PUBLICATION.md` — **internal rigor checklist only** (quality bar, not engagement target). HN is a Y Combinator property; the rubric tests "would hostile experts find cracks?" without coupling to the platform.
- `whitePaper/attsi/non-anon/SIGNAL_SHARPENING.md` — GitHub-specific presence audit (Phase 1 EXECUTED Wave 139a)
- `whitePaper/gen5/foundations/IDENTITY_ANCHORING_PATTERN.md` — identity architecture (dual-voice, cryptographic anchoring)
- `wateringHole/GLACIAL_SHIFT_READINESS.md` — criterion 8 (outer membrane hardened for public exposure)

---

## FILE: `operations/DISTRIBUTED_COVALENT_DEPLOYMENT.md`

# Distributed Covalent Deployment

**Status**: Architecture + implementation guide  
**Scope**: Multi-household compute via covalent-bonded gates  
**Last updated**: 2026-06-13 (Wave 111, reviewed 155h: **9-gate mesh LIVE** — westGate + strandGate Tower LIVE. Architecture still current. Gate fleet expanded.)

---

## Overview

A covalent family mesh extends NUCLEUS across multiple physical locations —
gates in different households, connected via cellMembrane relay over WAN.
The mesh handles the realities of residential computing: power cycles, owner
foreground load, ISP variability, and geographic daylight patterns.

cellMembrane acts as the **intra-layer** — the always-available rendezvous
that gates connect through when direct paths are unavailable.

```
                    cellMembrane VPS
                   (TURN relay, TLS,
                    rendezvous point)
                    /              \
              WAN / Songbird        \ WAN / Songbird
                /                    \
    ┌──────────────────┐    ┌──────────────────┐
    │  LAN Cluster A   │    │  flockGate        │
    │  (Michigan home)  │    │  (remote household)│
    │                   │    │                   │
    │  ironGate ──┐     │    │  i9-13900K        │
    │  eastGate ──┤ 1G  │    │  RTX 3070 Ti      │
    │  northGate ─┤     │    │  64 GB DDR5       │
    │  westGate ──┤     │    │  Ubuntu 24.04     │
    │  strandGate ┘     │    │                   │
    └──────────────────┘    └──────────────────┘
```

## Trust Model

All gates in a distributed covalent mesh share a **family seed** — the same
cryptographic root used for BirdSong discovery and BTSP session establishment.

| Layer | What | Trust level |
|-------|------|-------------|
| Gate ↔ Gate (LAN) | BirdSong UDP multicast, BTSP | Covalent (full) |
| Gate ↔ Gate (WAN) | Songbird TCP fallback via cellMembrane TURN | Covalent (full — BTSP encrypts through relay) |
| Gate ↔ cellMembrane | Tower services, TURN relay | Controlled (you operate VPS; provider has hypervisor) |
| cellMembrane ↔ Internet | TLS, DNS, content serving | Outer membrane (public) |

The cellMembrane VPS **never sees plaintext family traffic** — BTSP tunnels
are end-to-end encrypted between gates. The VPS only relays opaque bytes.

## cellMembrane as Intra-Layer

The VPS serves three roles for distributed gates:

### 1. Rendezvous (always-on)

Gates behind residential NAT cannot accept inbound connections. cellMembrane
provides the stable endpoint for:
- Songbird TURN relay (UDP :3478)
- RustDesk relay for remote desktop access (:21115-21117)
- BirdSong TCP fallback discovery (when LAN multicast is unavailable)

### 2. State Awareness

cellMembrane tracks which gates are currently reachable. When a gate goes
offline (power cycle, sleep, ISP outage), the relay notes the absence.
When it returns, Songbird re-establishes the mesh automatically.

### 3. Workload Routing

For cross-household dispatch, cellMembrane routing means:
- Latency-tolerant work (overnight GPU batches) routes to remote gates
- Latency-sensitive work (interactive, sub-100ms) stays on LAN
- Data-heavy work pre-stages artifacts via NestGate before dispatch

## Compute Scheduling Awareness

Distributed residential compute must handle availability that shifts with:

### Power Cycles

Gates sleep, reboot, lose power. toadStool workloads must:
- **Checkpoint** progress periodically (configurable interval)
- **Resume** on the same or different gate after reconnection
- **Timeout** gracefully — Songbird health probes detect gate absence

### Owner Foreground Load

toadStool's `max_guest_load` parameter (default 50% for remote gates like
flockGate) means dispatched GPU work yields when the owner starts gaming,
dev work, or other foreground tasks. The dispatch pattern:

1. toadStool monitors GPU/CPU utilization on the gate
2. When owner load exceeds threshold, guest workloads are paused
3. When load drops below threshold, workloads resume
4. If paused longer than configurable timeout, checkpoint and migrate

### Geographic Daylight Patterns

Gates in different timezones have complementary idle windows:
- Michigan LAN gates idle overnight (EST midnight-8am)
- Remote gates in other timezones may be idle during Michigan daytime
- Batch workloads can follow the idle window around the mesh

### Network Variability

Residential ISPs have asymmetric bandwidth, occasional outages, and
variable latency. The mesh handles this via:
- Songbird TURN relay as fallback (never requires port forwarding)
- STUN → hole-punch → relay escalation (sovereignty-first)
- Pre-dispatch dependency staging (avoid real-time large transfers)

## Pre-Dispatch Data Staging

From primalSpring Wave 33: the `validation::dependency` pattern handles
BLAKE3-verified input artifact staging before workload dispatch.

For distributed dispatch:

```rust
use primalspring::validation::dependency::{DependencySpec, validate_dependencies_at};

let deps = vec![
    DependencySpec::required("data/genome.fasta", Some("abc123...")),
    DependencySpec::required("config/pipeline.toml", None),
];

// Verify artifacts staged at remote gate before dispatch
let report = validate_dependencies_at(&deps, &remote_workdir);
if !report.is_ok() {
    // Stage missing artifacts via NestGate content.put
    stage_via_nestgate(&deps, remote_gate_id)?;
}
```

This prevents dispatching work to a gate that doesn't have the input data,
avoiding expensive real-time transfers over WAN.

## flockGate Bootstrap Sequence

### Prerequisites

- cellMembrane VPS operational (TURN + RustDesk) -- **DONE**
- Family seed available -- **DONE** (irongate-sovereign family)
- Remote machine accessible via RustDesk -- **DONE**
- plasmidBin binaries for x86_64-unknown-linux-musl -- **DONE** (14/14 fresh, Wave 103)
- plasmidBin depot accessible from WAN -- **SHIPPED** (Wave 105: `plasmid.fetch --source wan` + `caddy.depot.provision`). Production deployment + flockGate validation pending.

### Steps

1. **Remote access**: RustDesk from cellMembrane to flockGate machine
2. **Bootstrap**: `bootstrap_gate.sh --join-family` with family seed
3. **Deploy**: Node Atomic (BearDog + Songbird + ToadStool + barraCuda + coralReef)
4. **Discover**: Songbird TCP/WAN fallback via cellMembrane TURN
5. **Validate NAT**: STUN probe → hole-punch attempt → TURN relay fallback
6. **Test dispatch**: toadStool workload from ironGate → flockGate via relay
7. **Shadow compare**: `shadow_comparator::compare_paths` TURN vs cloudflared

### NAT Traversal Escalation

Songbird implements sovereignty-first STUN escalation:

1. **Lineage STUN** — self-hosted (if available)
2. **Self-hosted STUN** — cellMembrane VPS
3. **Public STUN** — last resort (leaks IP to third party)
4. **Hole-punch** — direct UDP if both sides have STUN-resolved addresses
5. **TURN relay** — cellMembrane relays if punch fails (most residential NAT)

Most residential NAT will land on TURN relay. This is acceptable — the relay
is sovereign (our VPS), BTSP-encrypted, and bandwidth sufficient for
workload coordination + result retrieval.

## Plasmodium Collective

When 2+ NUCLEUS instances bond covalently, biomeOS recognizes the
**Plasmodium** — a collective organism with aggregated capabilities.

```bash
biomeos plasmodium status
# Plasmodium: irongate-sovereign-family
# Gates: ironGate (LAN), eastGate (LAN), flockGate (WAN)
# Capabilities: 13 primals × 3 gates (deduped)
# Aggregate: 72+ cores, ~72 GB VRAM, ~192 GB RAM
```

The Plasmodium enables:
- Cross-gate `capability.call` dispatch (resolved by biomeOS routing)
- Aggregated GPU VRAM for large model inference
- Distributed NestGate storage with cross-gate replication
- Family-scoped socket naming (`{primal}-{family_id}.sock`)

## References

- `FAMILY_HPC_MODEL.md` — personal-PC-first model, yield semantics
- `MEMBRANE_CHANNEL_ARCHITECTURE.md` — cellMembrane channels
- `SOVEREIGNTY_STANDARDS.md` — calibrate → shadow → cutover
- `GLACIAL_SHIFT_READINESS.md` — deployment tracking
- `HARDWARE.md` — gate inventory and specifications
- `graphs/multi_node/three_node_covalent_cross_network.toml` — WAN topology
- `gardens/projectNUCLEUS/gates/flockgate.toml` — flockGate config

---

## FILE: `operations/GATEHOUSE_DARKFOREST_STANDARD.md`

# Gatehouse / Darkforest — Sovereign Network Demarcation Standard

**Wave**: 132g (reviewed 155h) | **Authority**: eastGate overwatch

---

## Overview

The ecoPrimals network has two regimes separated by a single, controlled boundary.
All external traffic enters through the **Gatehouse** (known ports, TLS termination).
All internal routing happens in the **Darkforest** (no exposed ports, mesh-only).
The **Drawbridge** is the single crossing point between them.

---

## Darkforest (Internal)

The darkforest is invisible from outside. No port scanning, no direct access, no known entry points.

**Rules**:
- No primal binds to `0.0.0.0` (except bearDog in gatehouse mode)
- All inter-primal communication uses Unix domain sockets, abstract sockets, or songBird mesh
- Services bind to `127.0.0.1` at most — never externally reachable
- Discovery is via `mesh.peers` and `capability.call` — no IPs, no ports
- Adding a new service means registering a capability with songBird, not opening a port

**Transport hierarchy**:
1. Abstract sockets (Android/grapheneGate)
2. Unix domain sockets (Linux/macOS)
3. `127.0.0.1:port` TCP (localhost only, when UDS unavailable)
4. songBird mesh relay (cross-gate, LAN direct-connect or WAN via golgi)

**Key invariant**: a new gate joining the mesh exposes ZERO ports externally. It peers via songBird and becomes reachable to the mesh. Nothing else can see it.

---

## Gatehouse (External)

The gatehouse is the castle wall — the only surface exposed to the internet.

**Exactly two ports**:
- `:443` — TLS termination (bearDog ACME gateway, `HotReloadAcceptor`)
- `:80` — ACME HTTP-01 challenges + HTTP→HTTPS redirect (bearDog `Http01Solver`)

**Owner**: bearDog (single binary, single process, single responsibility for external surface)

**Activation**: `BEARDOG_GATEHOUSE_MODE=true` (or legacy `BEARDOG_TLS_MODE=acme`)

**Behavior**:
- `:443`: Accept TLS connection → terminate → forward cleartext HTTP to upstream (songBird)
- `:80`: If `/.well-known/acme-challenge/*` → serve ACME response. Otherwise → `301 Moved Permanently` to `https://`
- skunkBat `security.advisory` is consulted for threat intelligence on inbound traffic

**Only one gate runs gatehouse mode**: sporeGate (the public entry point). Other gates are purely darkforest.

---

## Drawbridge (songBird http.proxy)

The single crossing point between the external world and the internal mesh.

**Location**: `127.0.0.1:7700` on sporeGate (or UDS: `unix:/run/membrane/songbird.sock`)

**Flow**:
```
bearDog :443 (TLS terminated)
    → cleartext HTTP → songBird http.proxy (drawbridge)
        → CapabilityProxyRouter: Host/path → capability name
            → capability.call via mesh → backend in darkforest
```

**Routing model**:
- `SONGBIRD_PROXY_ROUTES` env var: `capability=http://backend:port`
- Example: `jupyter=http://192.168.4.237:8000` (ironGate LAN direct-connect)
- The backend address is internal (LAN or mesh) — never exposed externally

**Key invariant**: the drawbridge is the ONLY place that translates external HTTP semantics into internal mesh semantics. Everything before it is "internet". Everything after it is "darkforest".

**Capability advertisement** (Wave 133d):

Drawbridge routes must be discoverable by remote gates via `capability.call`. songBird
auto-registers each unique capability from `SONGBIRD_DRAWBRIDGE_ROUTES` into the local
IPC registry at startup and announces them to mesh peers via `mesh.capabilities_announce`.

```
SONGBIRD_DRAWBRIDGE_ROUTES=/hub=jupyter,/api=jupyter,/infer=inference
```
On startup, songBird:
1. Parses unique capabilities: `["jupyter", "inference"]`
2. Registers `drawbridge:jupyter`, `drawbridge:inference` in the local IPC registry
3. Announces `["jupyter", "inference"]` to all mesh peers
4. Remote gates can now `capability.call("jupyter")` → routed to this gate's drawbridge

Every gate with drawbridge routes automatically advertises its capabilities.
No manual `ipc.register` calls or sidecar scripts needed.

---

## Topology

```
INTERNET
    │
    ▼
┌─────────────────────────────────────────┐
│         GATEHOUSE (sporeGate)           │
│                                         │
│  bearDog :443  ←→  ACME/TLS/certs     │
│  bearDog :80   ←→  challenges/redirect │
│  skunkBat      ←→  security advisory   │
│                                         │
│  ─────── DRAWBRIDGE ───────            │
│  songBird :7700 (http.proxy)           │
│  CapabilityProxyRouter                  │
└──────────────┬──────────────────────────┘
               │ mesh / LAN / UDS
               ▼
┌─────────────────────────────────────────┐
│         DARKFOREST (all gates)          │
│                                         │
│  songBird mesh (UDS, abstract, LAN)    │
│  ironGate: JupyterHub localhost:8000   │
│  strandGate: STAR alignment (local)    │
│  flockGate: Tower dev (WAN via golgi)  │
│  eastGate: primalSpring, petalTongue   │
│  grapheneGate: mobile trust anchor     │
│                                         │
│  Nothing exposed. Nothing visible.      │
│  Capabilities, not ports.               │
└─────────────────────────────────────────┘
```

---

## Biological Mapping (K-Derm Alignment)

| Network Concept | K-Derm Layer | Biology |
|----------------|--------------|---------|
| Gatehouse | Outer membrane (extracellular face) | Exposed surface proteins, receptors |
| Darkforest | Cytoplasm | Protected internal machinery |
| Drawbridge | Transport channel / porin | Selective permeability |
| bearDog :443 | LPS layer | First contact, shields interior |
| songBird http.proxy | Channel protein | Specific molecules (capabilities) pass |
| skunkBat advisory | Immune receptor | Detects threats at the surface |

---

## Configuration Reference

### sporeGate (gatehouse gate)

```bash
# /etc/beardog/gatehouse.env
BEARDOG_GATEHOUSE_MODE=true
BEARDOG_ACME_DOMAINS=lab.primals.eco
BEARDOG_ACME_EMAIL=admin@primals.eco
BEARDOG_GATEWAY_UPSTREAM=127.0.0.1:7700
BEARDOG_HTTPS_PORT=443
BEARDOG_ACME_CHALLENGE_PORT=80

# songBird proxy routes (drawbridge configuration)
SONGBIRD_PROXY_ROUTES=jupyter=http://192.168.4.237:8000
```

### Any other gate (darkforest)

No gatehouse configuration needed. Just songBird mesh peering:
```bash
# songBird mesh.init with bootstrap peers
# No ports exposed. No external configuration.
```

---

## Anti-Patterns

- Opening a port on a non-gatehouse gate for external access
- Running Caddy, nginx, or any other reverse proxy alongside bearDog
- Binding a service to `0.0.0.0` instead of `127.0.0.1`
- Routing external traffic without going through the drawbridge
- Adding DNS records that point directly to darkforest gates

---

*The gatehouse is a known point. The darkforest is invisible. The drawbridge is selective. This is sovereignty.*

---

## FILE: `operations/GATE_NUCLEUS_SYSTEMD_STANDARD.md`

<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Gate NUCLEUS systemd Deployment Standard

**Status**: Ecosystem Standard
**Version**: 1.0.0
**Date**: June 12, 2026
**Authority**: wateringHole (cellMembrane Wave 111)
**Validated by**: benchScale libvirt mesh (irongate-nucleus-mesh topology)

---

## Purpose

This standard defines how a full NUCLEUS (13/13 primals) is deployed as
persistent systemd services on a production gate. It replaces ad-hoc process
management and ensures primals survive reboots, respect dependency ordering,
and participate in the federation mesh.

This is the canonical pattern for desktop gates (ironGate, eastGate, swiftGate)
and NUC canary nodes. VPS/relay nodes use a subset (tower-only or fieldMouse).

---

## Architecture

```
systemd (PID 1)
  ├── beardog-membrane.service      ← crypto spine (starts FIRST)
  │     └── /run/membrane/beardog.sock
  ├── songbird-membrane.service     ← mesh federation (Requires beardog)
  │     └── /run/membrane/songbird.sock + TCP :7700
  ├── skunkbat-membrane.service     ← threat defense (Requires beardog)
  │     └── /run/membrane/skunkbat.sock
  ├── membrane-nucleus@toadstool    ← compute dispatch
  ├── membrane-nucleus@barracuda    ← GPU math
  ├── membrane-nucleus@coralreef    ← shader compile
  ├── membrane-nucleus@nestgate     ← storage transport
  ├── membrane-nucleus@rhizocrypt   ← ephemeral DAG
  ├── membrane-nucleus@loamspine    ← permanent ledger
  ├── membrane-nucleus@sweetgrass   ← attribution braids
  ├── membrane-nucleus@squirrel     ← AI coordination
  ├── membrane-nucleus@petaltongue  ← multi-modal UI
  └── membrane-biomeos.service      ← orchestrator (api subcommand)
        └── /run/membrane/biomeos.sock
```

---

## Required Files

### `/etc/membrane/tower.env`

Environment file sourced by all units. Contains gate identity and mesh config:

```ini
FAMILY_SEED=<production-family-seed>
FAMILY_ID=e8b62b6e
NODE_ID=<gate-name>
GATE_NAME=<gate-name>
SONGBIRD_PEERS=<peer1>@<host1>:7700,<peer2>@<host2>:7700
SONGBIRD_FEDERATION_ENABLED=true
SECURITY_SOCKET=/run/membrane/beardog.sock
PRIMAL_BIND_MODE=auto
ECOPRIMALS_ROOT=/home/irongate/Development/ecoPrimals
```

**Permissions**: `chmod 600` (contains FAMILY_SEED).

### `/opt/ecoPrimals/primals/`

All 13 musl-static binaries from `plasmidBin/primals/x86_64-unknown-linux-musl/`.

### Gate Profile

`infra/plasmidBin/profiles/<gate>-full.toml` — defines composition, mesh peers,
launch order, and health thresholds.

---

## systemd Unit Patterns

### Tower Units (dedicated)

Tower primals get dedicated unit files because they have unique startup requirements:

- **beardog-membrane.service**: `RuntimeDirectory=membrane` (creates `/run/membrane/`)
- **songbird-membrane.service**: `--port 7700 --bind 0.0.0.0` for federation
- **skunkbat-membrane.service**: Standard socket binding

### Template Unit (`membrane-nucleus@.service`)

All non-tower, non-biomeos primals use the parameterized template:

```ini
[Service]
ExecStart=/opt/ecoPrimals/primals/%i server --socket /run/membrane/%i.sock
```

Instantiated as: `membrane-nucleus@toadstool`, `membrane-nucleus@barracuda`, etc.

### biomeOS Unit (dedicated)

biomeOS uses `api` subcommand (not `server`), requiring a dedicated unit:

```ini
ExecStart=/opt/ecoPrimals/primals/biomeos api --socket /run/membrane/biomeos.sock
```

---

## Startup Order

The dependency chain enforces correct ordering:

1. **beardog-membrane** — starts first (crypto spine, creates RuntimeDirectory)
2. **songbird-membrane** + **skunkbat-membrane** — Requires beardog
3. **membrane-nucleus@*{10}** — After beardog + songbird
4. **membrane-biomeos** — After beardog + songbird (needs crypto for Dark Forest)

---

## Validation

### Socket Count

A healthy full NUCLEUS produces ≥13 sockets in `/run/membrane/`:

```bash
ls /run/membrane/*.sock | wc -l  # expect ≥13 (up to ~25 with capability aliases)
```

### Health Probes

```bash
# BearDog crypto spine
echo '{"jsonrpc":"2.0","method":"health","id":1}' | \
  socat -t2 - UNIX-CONNECT:/run/membrane/beardog.sock

# Songbird federation
echo '{"jsonrpc":"2.0","method":"federation.status","id":1}' | \
  socat -t2 - UNIX-CONNECT:/run/membrane/songbird.sock
```

### membrane gate.status

```bash
membrane gate.status
# Expect: sovereignty.s1_tls OK, s2_relay OK, s3_content OK, s4_auth OK
```

### gate.bootstrap

```bash
membrane gate.bootstrap <gate-name> --dry-run
# Expect: ≥8/9 phases pass (checksum.git may fail with dev builds)
```

---

## Songbird Federation Requirements

For cross-gate mesh to form, songbird MUST:

1. Bind to `0.0.0.0:7700` (not localhost) — use `--bind 0.0.0.0`
2. Have `SECURITY_SOCKET` pointing to beardog's UDS
3. Have `SONGBIRD_PEERS` configured with at least one peer
4. Have `SONGBIRD_FEDERATION_ENABLED=true`

---

## benchScale Pre-Validation

Before deploying to production, validate via the graduated pipeline:

1. **Docker lab** (`nucleus-lab-node` image) — fast smoke test
2. **libvirt VM mesh** (`irongate-nucleus-mesh` topology) — OS-fidelity
3. **Production deploy** — `gate.bootstrap` + systemd enable/start

---

## Cascade Integration

Once deployed, the NUCLEUS participates in the cascade pipeline:

```bash
membrane temporal.cascade --with-restart
```

This pulls latest from forgejo, rebuilds if needed, and restarts affected services.

---

## Composition Variants

| Profile | Primals | Units | Use Case |
|---------|---------|-------|----------|
| `irongate-full` | 13 | 13 (3 dedicated + 10 template + biomeos) | Desktop workstation |
| `canary-fieldmouse` | 13 | 13 (resource-constrained) | NUC warm standby |
| `tower` | 3 | 3 (beardog + songbird + skunkbat) | VPS relay, beacon |
| `fieldMouse` | 7 | 7 (tower + nest) | NAS, archive, edge |

---

## FILE: `operations/GATE_SETUP_STANDARD.md`

# Gate Setup, Sync, and Resync Standard

**Authority**: wateringHole consensus (Wave 63, reviewed 155h — superseded by TEAM_STARTUP_BLURB_TEMPLATE for new gates)
**Applies to**: Physical gates (LAN/WAN), VPS proto-fieldMouse deployments
**Prerequisites**: ecosystem_manifest.toml, K_DERM_TOPOLOGY_STANDARD.md

---

## Gate Types

### Physical Gates (Cytoplasm)

Desktop/server hardware running full NUCLEUS. Connected via LAN or WAN.
Bond type to inner membrane: **covalent**.

| Gate | Hardware | Location | Springs |
|------|----------|----------|---------|
| eastGate | Primary dev | LAN | Full ecosystem |
| ironGate | Server | LAN | Core primals + health/ludo |
| southGate | Dev | LAN | Core primals + wet/neural |
| biomeGate | Dev | LAN | Core primals + hot |
| strandGate | ABG science | LAN | Science suite + genomics |
| westGate | 76TB ZFS cold storage | LAN | Nest Atomic + sporePrint + fossilRecord |
| flockGate | WAN shadow | WAN | sporePrint + full validation |

### VPS Proto-FieldMouse Deployments (Periplasm)

DigitalOcean droplets running specialized membrane roles. The diderm envelope
consists of three nodes with distinct K-Derm layer assignments.

| Node | K-Derm Layer | Bond | Role | GitHub SSH |
|------|-------------|------|------|------------|
| golgiBody | Inner membrane (cis) | Covalent/Metallic | Forgejo sovereign store, NUCLEUS, DNS | None (revoked) |
| peptidoglycan | Peptidoglycan | Metallic | Sync relay, impulse cascade, builds | None (revoked) |
| golgiBody-ext | Outer membrane (trans) | Ionic/Weak | GitHub push, sporePrint hosting | **Yes** (ships extracellularly) |

Only the outer membrane (trans face) holds GitHub SSH write credentials.
The diderm relay chain propagates pushes with proper bond degradation:
`gate → inner (covalent) → peptidoglycan (metallic) → outer (ionic) → GitHub (weak)`.
See `hooks/forgejo/README.md` for the relay chain scripts.

---

## Prerequisites (complete BEFORE starting)

- [ ] **SSH key generated** on the new gate (`ssh-keygen -t ed25519`)
- [ ] **SSH key registered on Forgejo** (primary): `curl -X POST https://git.primals.eco/api/v1/user/keys -H "Authorization: token <TOKEN>" -H "Content-Type: application/json" -d '{"title":"<gate>","key":"<pubkey>"}'`
  - To register keys without a pre-existing token, have an existing gate admin add your SSH public key via the Forgejo web UI: **Admin Panel -> User Accounts -> Keys -> Add Key**, or request eastGate to register via the `membrane` CLI.
- [ ] **Verify Forgejo connectivity**: `ssh -p 2222 git@git.primals.eco` should print `Hi <user>!`
- [ ] **Gate profile exists** in `ecosystem_manifest.toml` under `[gates.<name>]`

GitHub SSH key registration is **not needed** for gates — gates push only to Forgejo.
The K-Derm relay chain handles GitHub propagation automatically via golgiBody-ext.
If you need read access to GitHub for cold-start (Forgejo unreachable), register
a read-only deploy key: `gh ssh-key add ~/.ssh/id_ed25519.pub --title "<gate>"`

---

## Pre-Bootstrap Cleanup

If this gate previously had repos cloned at non-standard paths, remove them:

```bash
# Known stale layouts from pre-standard workspace
rm -rf ~/Development/ecoPrimals/songbird    # superseded by primals/songBird/
rm -rf ~/Development/ecoPrimals/toadstool   # superseded by primals/toadStool/
```

---

## Known Large Repos (shallow clone recommended for WAN)

These repos have large histories and will timeout or saturate bandwidth on full WAN clone.
Use `--shallow` flag or `git clone --depth 1` for these:

| Repo | Approx Size | Notes |
|------|-------------|-------|
| bearDog | 413K LOC, 2226 files | Largest in ecosystem |
| songBird | Large history | Federation protocol |
| toadStool | Large history | Identity system |
| petalTongue | Large | NLP/taxonomy |
| hotSpring | 127K LOC, 2562 files | Thermodynamics spring |
| sporePrint | Large | Zola site + pseudoSpores |
| rustChip | Large | Embedded systems |

To unshallow later: `git fetch --unshallow`

---

## Gate Setup — Physical

### Step 1: Workspace Layout

```bash
mkdir -p ~/Development/ecoPrimals
cd ~/Development/ecoPrimals

echo "<gate-name>" > .gate
export GATE_NAME=$(cat .gate)
```

### Step 2: Clone wateringHole

wateringHole is always the first clone. It contains the ecosystem manifest,
deployment standards, and all coordination docs (zero code — all tooling
lives in cellMembrane as the `membrane` binary).

> **Note**: Forgejo paths are case-sensitive. Use exact casing from
> ecosystem_manifest.toml (e.g., `ecoPrimals/wateringHole`, not
> `ecoprimals/wateringhole`). Mismatched casing fails silently.

```bash
mkdir -p infra
git clone ssh://git@git.primals.eco:2222/ecoPrimals/wateringHole.git infra/wateringHole
```

If golgiBody Forgejo is unreachable, fall back to GitHub:
```bash
git clone git@github.com:ecoPrimals/wateringHole.git infra/wateringHole
```

### Step 3: Cascade Pull

`membrane temporal.cascade` reads the gate profile from ecosystem_manifest.toml
and clones only the repos this gate needs.

```bash
# Full cascade (LAN or fast connection)
membrane temporal.cascade --gate $GATE_NAME --clone-missing

# If membrane is not yet installed, bootstrap via plasmid.fetch:
membrane plasmid.fetch --primal membrane --source github
# Or build from source:
cd gardens/cellMembrane && cargo build --release --bin membrane
```

**Note**: The bash `cascade-pull.sh` was fossilized in Wave 66. All gates
now use `membrane temporal.cascade` which is manifest-driven and handles
gate identity, remote selection, and clone-missing automatically.

This will:
- Read `[gates.<name>]` from ecosystem_manifest.toml for the repo list
- Create workspace directories (primals/, springs/, gardens/, infra/) if missing
- Clone missing repos into the standard layout
- Auto-shallow known large repos (bearDog, songBird, etc.) even without `--shallow`
- Set up both `origin` (GitHub) and `forgejo` remotes
- Run temporal sync to pull from the leading remote
- Pre-flight check Forgejo connectivity before per-repo fetches

### Step 4: Dev Platform

```bash
# Rust toolchain
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Verify
rustc --version
cargo --version

# Zola (for sporePrint and other static site builds)
# Option A: pre-built binary (recommended)
# Download from https://www.getzola.org/documentation/getting-started/installation/
# Option B: build from source (slower)
cargo install zola
```

### Step 5: Membrane Binary (Optional)

If the gate needs VPS control or advanced temporal sync:

```bash
cd gardens/cellMembrane/crates/membrane-shadow
cargo build --release
sudo cp target/release/membrane /usr/local/bin/
```

### Step 6: NUCLEUS Deploy (Optional)

For gates running primal services:

```bash
# From plasmidBin
cd infra/plasmidBin
./deploy_gate.sh --composition tower    # Tower first
./deploy_gate.sh --composition node     # Then Node
./deploy_gate.sh --composition nest     # Then Nest
./deploy_gate.sh --composition full     # Full NUCLEUS
```

---

## Gate Setup — VPS Proto-FieldMouse

VPS nodes are provisioned via `doctl` and bootstrapped with a role-specific
configuration. They are NOT full gates — they are membrane layer nodes.

### Provisioning

```bash
doctl compute droplet create <name> \
  --image debian-12-x64 \
  --size <size-slug> \
  --region nyc1 \
  --ssh-keys <key-id> \
  --tag-names membrane,<role>
```

### Bootstrap (common to all VPS nodes)

```bash
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq && apt-get upgrade -y -qq
apt-get install -y -qq git curl build-essential pkg-config libssl-dev unzip jq ufw

mkdir -p /opt/ecoPrimals
echo "<node-name>" > /opt/ecoPrimals/.gate

ssh-keygen -t ed25519 -f /root/.ssh/id_ed25519 -N "" -C "<node-name>@vps"
# Register pubkey on GitHub (gh ssh-key add) and Forgejo (API POST /user/keys)
```

### Role-Specific Bootstrap

**Inner membrane (golgiBody)**:
- Forgejo, Caddy TLS for git.primals.eco, knot-dns
- NUCLEUS primal services via UDS
- UFW: SSH + 2222 (Forgejo SSH) + 443 (Caddy)
- Workspace: wateringHole only (Forgejo serves all repo data)

**Peptidoglycan**:
- Rust, Zola, build-essential
- Full 39-repo workspace (--depth 1 for bloated repos)
- Both origin + forgejo remotes on every repo
- membrane binary built and installed
- UFW: SSH only (no public services)

**Outer membrane (golgiBody-ext)** — trans/shipping face:
- Caddy, Zola for sporePrint hosting
- wateringHole clone + `ext-github-push.sh` for GitHub publication
- GitHub SSH write credentials (only node with extracellular write access)
- UFW: SSH + HTTP + HTTPS

---

## Sync — membrane temporal.cascade

### Daily Sync

```bash
membrane temporal.cascade
```

`temporal.cascade` uses the manifest to:
1. Resolve gate identity (from `.gate` file or `--gate` flag)
2. For each repo in the gate's manifest profile, select the temporal leader remote
3. Execute `git pull --ff-only <remote>` concurrently
4. Report per-repo status (OK, SKIP, FAIL) with timing

**Push Target**: The manifest `push_target = "forgejo"` means gates push
only to Forgejo. The K-Derm relay chain auto-propagates to GitHub via
peptidoglycan → golgiBody-ext. Gates no longer need GitHub SSH access.

### Automated Sync (systemd timer)

```bash
# Install systemd units (updated to use membrane)
sudo cp systemd/cascade-pull.service /etc/systemd/system/
sudo cp systemd/cascade-pull.timer /etc/systemd/system/

# Configure
sudo systemctl edit cascade-pull.service
# Set Environment: MEMBRANE_BIN, ECOPRIMALS_ROOT

sudo systemctl enable --now cascade-pull.timer
```

### Manual Sync Modes

```bash
# Check temporal alignment without pulling
membrane temporal.check

# Full cascade with clone-missing for new repos
membrane temporal.cascade --clone-missing

# Sync specific repos only
membrane temporal.sync springs/primalSpring
```

---

## Resync — Recovery from Divergence

### Soft Resync (ff-only failed)

When temporal sync reports divergence (non-fast-forward), investigate:

```bash
cd <repo-path>
git log --oneline origin/main..forgejo/main  # Commits on Forgejo not on GitHub
git log --oneline forgejo/main..origin/main  # Commits on GitHub not on Forgejo
```

Resolution options:
1. **Rebase**: `git rebase origin/main` (if your work is on top)
2. **Merge**: `git merge origin/main` (creates merge commit)
3. **Force-align**: `git reset --hard <leading-remote>/main` (loses local work)

### Hard Resync (corrupted state)

When a gate's workspace is in an unrecoverable state:

```bash
# Remove the repo entirely
rm -rf <repo-path>

# Re-clone via temporal cascade
membrane temporal.cascade --clone-missing
```

### VPS Resync

For peptidoglycan (structural layer):
```bash
# On peptidoglycan
membrane temporal.cascade
```

For golgiBody-ext (outer membrane / trans face):
```bash
# Sync wateringHole for relay scripts
cd /opt/ecoPrimals/infra/wateringHole
git pull --ff-only forgejo main

# Re-pull and rebuild sporePrint
cd /opt/ecoPrimals/infra/sporePrint
git pull origin main
zola build
sudo systemctl restart caddy
```

---

## Multi-Vendor VPS Plans

The diderm model is designed for vendor portability:

### Current: DigitalOcean nyc1

All three nodes in the same datacenter for <1ms inter-node latency.
Cost: ~$48/mo total.

### Planned: Multi-vendor redundancy

| Vendor | Role | Rationale |
|--------|------|-----------|
| DigitalOcean | Inner membrane (golgiBody) | Established, Forgejo data lives here |
| Hetzner | Peptidoglycan mirror | Cost-effective builds, EU jurisdiction |
| Vultr | Outer membrane backup | Geographic redundancy |

The inner membrane is the hardest to move (Forgejo data). Peptidoglycan and
outer membrane are stateless and can be reprovisioned from scratch.

### WAN Mesh Sovereign Barrier

The ultimate goal: if enough physical gates have WAN connectivity, the VPS
becomes optional. Gates form a covalent mesh via Songbird TURN relay:

```
Gate A (WAN) ←─[covalent]──→ Gate B (WAN)
     ↕                              ↕
Gate C (LAN) ←─[covalent]──→ Gate D (LAN)
```

In this model:
- Forgejo can run on any gate with stable uptime (replaces golgiBody inner)
- Temporal sync happens peer-to-peer (replaces peptidoglycan)
- sporePrint can be served from any gate with public IP (replaces golgiBody-ext)
- VPS becomes a bootstrap convenience, not a requirement

This is the **sovereign barrier**: the point where the ecosystem no longer
depends on any external provider for core operations. VPS nodes transition
from "metallic fleet" to "weak extracellular" — a nice-to-have, not essential.

---

## SSH Key Management

### Gate Key Registration

Every gate needs its SSH key registered on **Forgejo only** (inner membrane):
`curl -X POST https://git.primals.eco/api/v1/user/keys -H "Authorization: token <TOKEN>" ...`

GitHub SSH write access lives exclusively on golgiBody-ext (outer/trans membrane).
Gates do not need GitHub keys — the K-Derm relay chain handles propagation.

With the Forgejo-primary model, only Forgejo SSH access is required. GitHub
is populated by the VPS push mirror. GitHub keys are only needed if a gate
wants direct read access for cold-start when Forgejo is unreachable.

### Registered Keys (Wave 73)

| Key Name | Registered On |
|----------|---------------|
| irongate | GitHub, Forgejo |
| eastGate | Forgejo |
| southGate | Forgejo |
| strandGate | Forgejo |
| flockGate | Forgejo |
| westGate | **pending** (onboarding this week) |
| golgiBody (inner) | Forgejo (owns it) |
| peptidoglycan | Forgejo |
| golgiBody-ext (outer) | Forgejo, **GitHub** (trans face ships extracellularly) |

---

## FILE: `operations/GATE_SPRING_OWNERSHIP.md`

# Gate-Spring Ownership — Canonical Routing SSOT

**Purpose**: Definitive assignment of which gate owns which springs, gardens,
and science domains. This is the missing doc that `STANDARDS_AND_EXPECTATIONS.md`
referenced as `GATE_DEPLOYMENT_STANDARD.md`.

**Last updated**: 2026-05-28 (Wave 60 — postPrimordial, golgiBody Phase A live)

**Authority**: wateringHole consensus. Changes require coordination across
affected gate teams.

---

## Gate-Spring Ownership Table

| Gate | Springs | Gardens / Products | Science Domain | NUCLEUS Status |
|------|---------|-------------------|----------------|----------------|
| **eastGate** | primalSpring, airSpring, groundSpring | — | Ecosystem coordination, ecology, geoscience | Full 13/13 |
| **ironGate** | healthSpring, ludoSpring | esotericWebb | Clinical/compliance, game science | Full 13/13 |
| **southGate** | wetSpring, neuralSpring | — | Biology/analytical chemistry, ML inference | Node Atomic (P1 pattern node) |
| **biomeGate** | hotSpring | — | GPU-accelerated physics, compute trio (toadStool + barraCuda + coralReef) | Node Atomic 9/13 |
| **strandGate** | hotSpring | helixVision, initioChem, blueFish, lithoSpore | ABG science, provenance trio, genomics, analytical ETL | Full NUCLEUS planned |
| **golgiBody** (VPS) | — | — | Periplasmic sync, Forgejo, NUCLEUS relay | Infra NUCLEUS 13/13 |

**Cross-gate springs**: hotSpring operates on both strandGate (ABG science,
lithoSpore, compChem validation) and biomeGate (GPU solving, HBM2 compute,
toadStool diesel engine). The science evolves on strandGate; heavy compute
dispatches to biomeGate via Songbird mesh.

---

## primalSpring — Coordination Spring (Not Science)

primalSpring is the ecosystem's coordination and composition validation spring.
Its scope is exclusively:

- **NUCLEUS evolution** — composition tiers, deployment patterns, dark forest validation
- **Primal bonding** — capability contracts, IPC wire standards, cross-gate mesh
- **Ecosystem validation** — 57 scenarios, freshness checks, WaterFall integrity

primalSpring does NOT own domain science. Each science spring evolves
independently on its home gate. primalSpring validates that their compositions
work together — it is the bonding mechanics, not the atoms.

---

## Gate Hardware Profiles

| Gate | Hardware | CPU | RAM | GPU | Storage | Role |
|------|----------|-----|-----|-----|---------|------|
| **eastGate** | Utility + neuromorphic | Ryzen | 64GB | Akida BrainChip | NVMe | Orchestration hub, coordination |
| **ironGate** | Agentic dev workstation | — | 96GB | — | Large | ABG JupyterHub, cellMembrane team home |
| **southGate** | Gaming + heavy compute | — | 128GB | Multi-GPU | NVMe | Biology + inference pattern node |
| **biomeGate** | HBM2 test bench | Threadripper | — | Titan V + K80 | NVMe | HPC physics, GPU shader validation |
| **strandGate** | Bioinformatics | 64-core | — | — | Large | ABG science, genomics pipelines |
| **northGate** | Flagship AI/LLM (future) | — | — | — | — | Node Atomic planned |
| **westGate** | Cold storage (future) | — | — | — | 76TB | Nest Atomic planned |
| **grapheneGate** | Pixel 8a (GrapheneOS) | Tensor G3 | 8GB | — | 128GB | Portable trust anchor, Dark Forest beacon |
| **golgiBody** | DigitalOcean VPS | 1 vCPU | 2GB | — | 50GB | Periplasmic sync, NUCLEUS relay |

---

## Domain Routing

### Current: Ad-Hoc (Documented)

Gates currently route work via handoff blurbs in wateringHole. Each gate team
pulls repos relevant to their springs via `membrane temporal.cascade`.
Cross-gate compute is coordinated manually through blurbs.

### Target: Covalent (Songbird Mesh)

Evolution path from ad-hoc to fully covalent routing:

```
Phase 1: Documented ownership (this file)              ← YOU ARE HERE
Phase 2: Gate profiles in manifest drive WaterFall sync ← DONE (membrane temporal.cascade --gate)
Phase 3: Songbird mesh discovers cross-gate capabilities
Phase 4: toadStool dispatches compute to best-fit gate
Phase 5: biomeOS graph.execute routes across Plasmodium
```

### Cross-Gate Patterns

| Pattern | Mechanism | Example |
|---------|-----------|---------|
| **Science on one gate, compute on another** | Songbird mesh + toadStool dispatch | hotSpring science on strandGate, GPU dispatch to biomeGate |
| **Coordination validates all gates** | primalSpring `s_covalent_mesh` | eastGate probes ironGate + southGate mesh health |
| **Repo sync through periplasm** | WaterFall temporal cascade via Forgejo | All gates pull from golgiBody VPS |
| **Product composition across springs** | Garden composes primals via IPC | helixVision on strandGate consumes wetSpring + hotSpring science |

---

## WaterFall Sync Profiles

Each gate's `[gates.*]` manifest profile determines which repos it pulls
via `membrane temporal.cascade`. The profile reflects ownership:

- **eastGate**: Full superset (38 repos) — coordination hub sees everything
- **ironGate**: Core primals + healthSpring + infra
- **southGate**: Core primals + wetSpring + neuralSpring
- **biomeGate**: Core primals + hotSpring
- **strandGate**: Core primals + hotSpring + wetSpring + ABG gardens + lithoSpore
- **golgiBody**: NUCLEUS primals + deployment infra (no springs)

Gates can override with `--gate` flag or pull everything without `--gate`.

---

## Evolution Timeline

| Wave | Milestone | Status |
|------|-----------|--------|
| 55 | Gate-spring assignments in handoff blurbs | DONE |
| 59 | southGate designated pattern node (wet/neural first) | DONE |
| 60 | golgiBody Phase A — VPS Forgejo, WaterFall 38/38 validated | DONE |
| 60 | This SSOT created — documented ownership | DONE |
| 60 | strandGate enters ecosystem (helixVision, initioChem, blueFish) | DONE |
| 60 | Eukaryotic gate onboarding — one spring per gate blurbs shipped | DONE |
| 60 | VPS federation hub — Songbird :7700 + MitoBeacon seed + Dark Forest | DONE |
| 61+ | southGate 13/13 + membrane patterns proven | P1 critical path |
| 61+ | biomeGate 13/13 + GPU dispatch | P2 |
| 61+ | Gates mesh with VPS hub — colonial phase begins | P2 |
| 62+ | Songbird covalent mesh across 4+ gates | P3 |
| 63+ | biomeOS graph.execute over mesh | P5 |

---

## Biological State: Eukaryotic Unicellular → Multicellular

The ecosystem evolves through distinct organizational states:

```
Prokaryotic (Wave 1-48)
    Primals exist but gates are unstructured. No NUCLEUS.
    ↓
Eukaryotic unicellular (Wave 49-62) ← CURRENT
    Each gate has internal organization (NUCLEUS, springs, primals).
    Gates share the VPS periplasm (Forgejo) but operate independently.
    Like yeast: organized, capable, but each cell is autonomous.
    ↓
Colonial (Wave 62-63)
    Songbird mesh discovers cross-gate capabilities.
    Gates share advertisements but don't yet dispatch work.
    Like Volvox: cells in proximity, beginning to specialize.
    ↓
Multicellular (Wave 63+)
    Covalent bonds between gates via Songbird mesh.
    toadStool dispatches compute to best-fit hardware.
    Gates specialize as tissues: compute, science, coordination.
    ↓
Organism (Wave 65+)
    biomeOS graph.execute routes across the full Plasmodium.
    The ecosystem operates as one distributed sovereign system.
```

**Current wave objective**: Get every gate eukaryotic (NUCLEUS running,
primary spring validating, syncing through periplasm). See
`handoffs/EUKARYOTIC_GATE_ONBOARDING_MAY28_2026.md` for per-gate blurbs.

---

---

## Peptidoglycan Relay Layer

The VPS operates as the ecosystem's peptidoglycan — a structural relay substrate
between the outer membrane (internet) and the plasma membrane (gate firewalls).
It provides sovereign replacements for commercial services, running as persistent
infrastructure that gates connect to for federation, NAT traversal, and remote access.

### Shadow Pattern Map

| Commercial Service | Sovereign Shadow | VPS Port | Shadow Track | Status |
|----|----|----|----|----|
| Cloudflare Tunnel | Songbird TURN relay | :3478 + 49152:65535/udp | S2 | Parity met |
| Cloudflare TLS | BearDog ACME shadow | :8443 | S1 | Shadow live |
| GitHub Pages | NestGate + Caddy | :443 | S3 | Live, 68ms |
| Cloudflare DNS | knot-dns DNSSEC | :53 | S5 | Live, NS pending |
| Cloud IDE relay | RustDesk hbbs/hbbr | :21115-21117 | — | Live |
| GitHub Repos | Forgejo (golgiBody) | :2222 (SSH) + :3000 (HTTP) | — | Live, 38 repos |

### Gate Onboarding to Relay Layer

Gates onboard to the peptidoglycan via `onboard-gate-relay.sh`:

```bash
# From VPS depot (onboard a remote gate):
onboard-gate-relay.sh eastGate --vps-host [RELAY_PUBLIC] --gate-host 10.10.0.3

# From a gate (onboard self):
onboard-gate-relay.sh eastGate --vps-host [RELAY_PUBLIC] --local
```

This pulls TURN credentials, RustDesk key, MitoBeacon family/lineage seeds
from the VPS and writes `relay.env` to the gate. The gate's `tower.env` sources
this file for Songbird federation, TURN traversal, and family identity.

### Transport Paths by Gate Class

| Gate Class | Network | Federation Path | TURN Required |
|------------|---------|-----------------|---------------|
| LAN cluster | Basement 10G backbone | Direct TCP :7700 to VPS | No |
| WAN household | Remote ISP | TURN :3478 → federation | Yes |
| Roaming mobile | LAN ↔ cellular | Direct when LAN, TURN fallback | Conditional |
| Friend tower | External household | TURN :3478 → federation | Yes |
| NAS/depot | LAN backbone | Direct TCP :7700 to VPS | No |
| Portable anchor | WiFi / cellular | TURN :3478 → federation or BLE beacon | Conditional |

---

*Wave 68. Colonial phase. Portable trust anchors extend the mesh.*

---

## FILE: `operations/GATE_TEAM_COORDINATION_MATRIX.md`

# Gate-Team Coordination Matrix

**Purpose**: Single-page view of which team operates which gate, what hardware
it has, what projects it owns, and where it sits in the evolution/validation
hierarchy. Consolidates data from `GATE_SPRING_OWNERSHIP.md` (canonical
spring routing), `GLACIAL_SHIFT_READINESS.md` (operational status), and
`ecosystem_manifest.toml` (sync profiles).

**Last updated**: 2026-06-03 (Wave 75 — covalent mesh FORMING, every primal evolved, cross-gate trust validation NEXT)

**Authority**: wateringHole consensus

---

## Gate Inventory

| Gate | Team | Hardware | Role | NUCLEUS | Network | Status |
|------|------|----------|------|---------|---------|--------|
| **eastGate** | eastGate (overwatch) | i9-12900, RTX 4070 + Akida, 32GB | Orchestrator, coordination hub | 13/13 | LAN 1G | OPERATIONAL |
| **ironGate** | ironGate (cellMembrane, projectNUCLEUS, NestGate, petalTongue) | i9-14900K, RTX 5070, 96GB | Deployment infra, agentic dev | 13/13 (23 UDS) | LAN 1G | OPERATIONAL |
| **southGate** | southGate (Songbird, biomeOS, bearDog) | 5800X3D, RTX 4060 + 3090s, 128GB | Mesh + orchestration + security primals | 9/9 | LAN 1G | OPERATIONAL |
| **biomeGate** | biomeGate (hotSpring, toadStool, barraCuda, coralReef) | Threadripper 3970X, Titan V + K80, 256GB | HPC physics, compute trio, air-gap tester | 62/62 | LAN 1G | **OFFLINE** (kernel recovery) |
| **flockGate** | flockGate (sporePrint) | i9-13900K, RTX 3070 Ti, 64GB | WAN covalent, sporePrint hosting | OPERATIONAL | WAN via cellMembrane | OPERATIONAL |
| **strandGate** | strandGate (provenance trio + compute trio pickup) | Dual EPYC 7452 (64c), 256GB ECC | Bioinformatics, ABG science, barraCuda + coralReef SPIR-V | — | LAN 1G | **ACTIVE** (Wave 72) |
| **northGate** | — (undeployed) | Ryzen 9950X3D, RTX 5090, 96GB | Heavy compute, AI/LLM | — | LAN 1G (10G ready) | HARDWARE READY |
| **westGate** | — (incoming this week) | i7-4771, RTX 2070 Super, 32GB | 76TB ZFS cold storage (Nest Atomic) | — | LAN 1G (10G ready) | **INCOMING** (ETA this week) |
| **swiftGate** | — (undeployed) | Ryzen 5800X, RTX 3070, 64GB | Mobile/compact | — | LAN 1G | HARDWARE READY |
| **kinGate** | — (undeployed) | i7-6700K, RTX 3070, 32GB | Staging | — | LAN 1G | HARDWARE READY |
| **grapheneGate** | eastGate (portable) | Pixel 8a, Tensor G3, 8GB | Portable trust anchor, Dark Forest beacon | Tower Atomic (BearDog + Songbird + SkunkBat) | Cellular / WiFi | HARDWARE READY |

### VPS Nodes (cellMembrane — Inner Membrane)

| Node | K-Derm Layer | IP | Specs | Role | Status |
|------|-------------|-----|-------|------|--------|
| **golgiBody** | Inner (cis face) | [RELAY_PUBLIC] | 1 vCPU, 2GB, 50GB | Forgejo, NUCLEUS relay, sovereign DNS (ns1) | OPERATIONAL |
| **peptidoglycan** | Structural | [RELAY_PUBLIC] | 2 vCPU, 4GB, 80GB | Temporal sync hub, relay mediator | OPERATIONAL |
| **golgiBody-ext** | Outer (trans face) | 137.184.197.151 | — | Caddy TLS, sporePrint serving, DNS (ns2), GitHub push | OPERATIONAL |

---

## Project Ownership

### Springs

| Spring | Owner Gate | Science Domain |
|--------|-----------|----------------|
| **primalSpring** | eastGate | Ecosystem coordination, composition validation |
| **airSpring** | eastGate | Ecology science |
| **groundSpring** | eastGate | Geoscience |
| **healthSpring** | ironGate | Clinical/compliance |
| **ludoSpring** | ironGate | Game science |
| **wetSpring** | southGate | Biology, analytical chemistry |
| **neuralSpring** | southGate | ML inference patterns |
| **hotSpring** | biomeGate + strandGate | GPU physics (biomeGate compute), ABG science (strandGate) |
| **sporePrint** | flockGate | Ecosystem website, content pipeline |

### Primals (Mountains)

| Primal | Owner Gate | Capability Domain |
|--------|-----------|-------------------|
| **skunkBat** | eastGate | Session management, family identity |
| **squirrel** | eastGate | AI assistant, composition planning |
| **NestGate** | ironGate | Storage, content-addressed persistence |
| **petalTongue** | ironGate | Universal User Interface, rendering |
| **Songbird** | southGate | Mesh discovery, federation, TURN relay |
| **biomeOS** | southGate | Adaptive orchestration, Neural API |
| **bearDog** | southGate | Security, TLS, BTSP authentication |
| **toadStool** | biomeGate | Compute dispatch, GPU diesel engine (compute trio) — BLOCKED (hardware) |
| **barraCuda** | strandGate (pickup from biomeGate) | Pure Rust math + compute engine — ml.mlp_train (pure software) |
| **coralReef** | strandGate (SPIR-V) / biomeGate (Blackwell) | Shader compiler — SPIR-V portable, SM120 hardware-dependent |
| **rhizoCrypt** | strandGate | Content-addressed DAG (provenance trio) |
| **loamSpine** | strandGate | Immutable linear ledger (provenance trio) |
| **sweetGrass** | strandGate | Attribution, W3C PROV-O braids (provenance trio) |

### Infrastructure Projects

| Project | Owner Gate | Description |
|---------|-----------|-------------|
| **cellMembrane** | ironGate | VPS provisioning, relay infrastructure, deployment tooling |
| **projectNUCLEUS** | ironGate | Deploy graphs, dark forest, genomeBin, Forgejo CI |
| **esotericWebb** | ironGate | Interactive product garden |

---

## Gate → Responsibility Summary

| Gate | Springs | Primals | Infra Projects | Gardens | Sync Profile |
|------|---------|---------|----------------|---------|--------------|
| **eastGate** | primalSpring, airSpring, groundSpring | skunkBat, squirrel | — | — | Full superset (39 repos) |
| **ironGate** | healthSpring, ludoSpring | NestGate, petalTongue | cellMembrane, projectNUCLEUS | esotericWebb | Core + health/ludo + infra |
| **southGate** | wetSpring, neuralSpring | Songbird, biomeOS, bearDog | — | — | Core + wet/neural + mesh primals |
| **biomeGate** | hotSpring | toadStool, barraCuda, coralReef | — | — | Core + hotSpring + compute trio |
| **flockGate** | sporePrint | — | — | — | Core + sporePrint/petalTongue |
| **strandGate** | hotSpring (science) | rhizoCrypt, loamSpine, sweetGrass, **barraCuda** (pickup), **coralReef** (SPIR-V pickup) | — | helixVision, initioChem, blueFish, lithoSpore | Core + provenance + ABG + compute trio (software) |

---

## Evolution Hierarchy

### Validation Tiers

```
Tier 1 — Coordination (eastGate)
  primalSpring validates all compositions work together.
  835 tests, 57 scenarios, 33 compositions, 490+ methods.
  Owns the bonding mechanics, not the atoms.

Tier 2 — Deployment (ironGate)
  projectNUCLEUS validates deploy graphs, genomeBin, CI.
  cellMembrane validates VPS infrastructure, relay chain.

Tier 3 — Domain Science (per-gate)
  Each gate validates its own springs independently.
  primalSpring's scenarios verify cross-gate composition parity.
```

### Current Wave Assignments (Wave 77)

| Gate | Active Work | Priority | Status |
|------|-------------|----------|--------|
| **eastGate** | Live cross-gate capability.call validation. DNS NS cutover. primalSpring security scenarios. skunkBat westGate-ready. | P0 glacial | **AT PARITY — VALIDATION NEXT** |
| **ironGate** | S4 gate (ends ~Jun 9). NestGate s92 ZERO test failures. cellMembrane westGate onboarding prep. ludoSpring V82 parity. | P0 glacial | S4 **ACTIVE**, NestGate **ZERO FAILURES** |
| **southGate** | bearDog w137 (DID↔key, typed errors). Songbird w76 Phase 3.5 scaffold. biomeOS v4.05 (perceptron infer wired). Springs V195/V179 at parity. | P0 | **AT PARITY — PHASE 3.5 NEXT** |
| **biomeGate** | toadStool S288 (deep debt VIII, panic elimination). Hardware still OFFLINE. | P1 HPC | **OFFLINE** (S288 delivered remotely) |
| **flockGate** | sporePrint S3 content cutover (post-DNS). WAN relay maintenance. | P2 cutover | Ready, waiting on NS cutover |
| **strandGate** | coralReef w77 SPIR-V output + mesh capability. Provenance trio cross-gate schemas delivered. barraCuda modularized. | P1 compute | **AT PARITY — ALL TEAMS DELIVERED** |
| **westGate** | 76TB ZFS cold storage. Nest Atomic. Gate setup + NUCLEUS deploy. | P3 expansion | **INCOMING** (ETA this week) |
| **golgiBody** | Disk at 60%. S4 monitoring active. Relay chain Rust-native. | Maintenance | **HEALTHY** |

---

## Sovereignty Shadow Status

| Track | Commercial | Sovereign | Gate | Status |
|-------|-----------|-----------|------|--------|
| S1 TLS | Cloudflare (INACTIVE) | Caddy + LE on golgiBody-ext | cellMembrane | **VERIFIED** — 198 probes, 0 failures. Awaiting NS cutover to remove Cloudflare |
| S2 NAT | cloudflared (INACTIVE) | Songbird TURN :3478 | cellMembrane | **GRADUATED** |
| S3 Content | GitHub Pages | NestGate + Caddy (67ms TTFB) | cellMembrane + sporePrint | **READY** — sporePrint 101 tests, zero-C. Cutover after DNS NS switch |
| S4 Auth | OAuth2/PAM (DISABLED) | BearDog BTSP enforced | southGate (bearDog) + ironGate | **7-DAY GATE ACTIVE** — started Jun 2, ends ~Jun 9 |
| S5 DNS | Cloudflare NS | knot-dns ns1+ns2 (DNSSEC) | cellMembrane | **Infra LIVE** — registrar NS cutover pending (operator) |

---

## Cross-References

- `GLACIAL_CUTOVER_PLAN.md` — phased cutover plan (inner→outer→external)
- `GATE_SPRING_OWNERSHIP.md` — canonical spring routing, evolution biology
- `GLACIAL_SHIFT_READINESS.md` — operational status, glacial criteria
- `GLACIAL_SHIFT_WAVE_PLAN.md` — phased wave assignments
- `EVOLUTION_STATUS_WAVE66.md` — Wave 66 checkpoint + context braids
- `ecosystem_manifest.toml` — machine-readable gate sync profiles

---

*Wave 75. Covalent mesh FORMING. Every primal evolved. Virtual relay Phase 2 default. Cross-gate trust validation and gen5 paper NEXT. Evolution never stops.*

---

## FILE: `operations/GRAPHENEGATE_BOOTSTRAP_STANDARD.md`

# grapheneGate Bootstrap Standard — Physical Dark Forest Protocol

**Status**: LIVE (Wave 132h, reviewed 155h — Tower deployed, nucleus_launcher cross-compiled, ADB tether operational)
**Owner**: eastGate (overwatch)
**Hardware**: Pixel 8a, Google Tensor G3, 8GB RAM, GrapheneOS
**Gate class**: `portable_anchor`

> **Wave 132h status**: Tower composition (bearDog + songBird + skunkBat) deployed and reachable via ADB port forwarding. 15/15 aarch64-musl binaries in depot (14 primals + nucleus_launcher). LAUNCHER-01 complete: `nucleus_launcher` cross-compiled and published to pepti warehouse. grapheneGate also serves as USB tether for eastGate internet connectivity. Enrolled in `mesh_topology.toml` with `transport = "adb"`, role `mobile`. As the tether matures, grapheneGate can spawn new mesh connections and relay for gates that lack WAN.

---

## Current Operational State (Wave 132c)

| Component | Status |
|-----------|--------|
| ADB connectivity | LIVE (device 44251JEKB04957) |
| Tower composition (bearDog+songBird+skunkBat) | RUNNING (PIDs active) |
| ADB port forwarding (9100, 9200, 9140) | ACTIVE |
| USB tethering (eastGate internet) | ACTIVE |
| aarch64-musl binaries in depot | **15/15** (14 primals + nucleus_launcher) |
| mesh_topology.toml enrollment | DONE (transport=adb, role=mobile, zone=Wan) |
| primalSpring validation scenario | PASSING (s_graphenegate_readiness) |

### Tether + Gate Duality

grapheneGate simultaneously:
1. **Provides internet** to eastGate via USB tethering (cellular → USB RNDIS)
2. **Runs Tower primals** accessible over ADB port forwarding
3. **Can relay mesh traffic** for other gates when WAN is unavailable

This dual role means grapheneGate is both infrastructure (tether) and compute (gate).
As the connection matures, songBird on grapheneGate can accept mesh.peer connections
from other gates, effectively turning the phone into a WAN relay without needing
golgi or any VPS. The cellular connection becomes sovereign backhaul.

---

## Purpose

grapheneGate is the ecosystem's **portable physical root of trust**. It bridges
the gap between the stationary gate mesh (LAN/WAN hardware) and the operator's
physical presence. Wherever the operator carries grapheneGate, it can:

1. Prove family membership via encrypted BirdSong beacon
2. Bootstrap new gates on arbitrary hardware
3. Relay mesh traffic through hostile networks

grapheneGate is **not a general-purpose compute node**. It runs minimal Tower
Atomic (BearDog + Songbird + SkunkBat) — the trust perimeter, not the payload.

---

## Trust Model

### Physical Root of Trust Chain

```
Operator physical possession of Pixel 8a
    ↓
GrapheneOS verified boot + Titan M2 secure element
    ↓
BearDog keystore (Android Keymaster / StrongBox backed)
    ├── FAMILY_SEED → HKDF → BTSP session keys
    ├── Beacon seed (MitoBeacon) → BirdSong encrypted discovery
    └── Lineage seed (nuclear) → device-unique identity
    ↓
Songbird → beacon broadcast + mesh federation
    ↓
SkunkBat → audit trail of all trust operations
```

### Why a Phone

| Property | Benefit |
|----------|---------|
| Always carried | Physical colocation = proof of operator presence |
| Hardware secure element (Titan M2) | Key material bound to hardware; extraction-resistant |
| GrapheneOS | No Google services, minimal attack surface, verified boot |
| Cellular + WiFi | Network flexibility; operates on any substrate |
| Appears normal | Under scrutiny, looks like a standard Android device |
| USB-C tethering | Can bridge to gate hardware without WiFi |

---

## Three-Role Evolution

### Role 1 — Physical Dark Forest Beacon (Immediate)

grapheneGate carries beacon and lineage seeds on a hardened mobile OS.
BearDog broadcasts encrypted BirdSong beacons on the local network.

**Operational flow:**
1. Operator arrives at location with grapheneGate
2. grapheneGate connects to local WiFi (or USB tethers to target hardware)
3. BearDog broadcasts ChaCha20-encrypted UDP beacon on LAN
4. Existing gates (or new hardware with plasmidBin) detect beacon
5. Beacon decryption proves family membership (shared beacon seed)
6. BearDog lineage exchange verifies device identity + permission level
7. BTSP session established — gate joins mesh

**What outsiders see:** Encrypted UDP noise, indistinguishable from random data.
No port scanning reveals ecosystem. Dark Forest Pillar 1 (zero metadata leakage).

**Overseas scenario:**
- Arrive at foreign location with rented/purchased hardware
- Connect grapheneGate to hardware via USB-C or shared WiFi
- `plasmidbin bootstrap --beacon-seed` on new hardware
- grapheneGate's BirdSong beacon authenticates the new gate
- New gate pulls ecosystem manifest, clones repos, deploys NUCLEUS
- All traffic routes through BTSP — local network sees encrypted noise

### Role 2 — BTSP Relay Bootstrap (Near-term)

grapheneGate runs minimal Tower Atomic and can act as a relay when VPS
infrastructure is unavailable.

**Use cases:**
- New jurisdiction where VPS providers are untrusted or blocked
- Network partition: home mesh unreachable, need local relay
- Initial bootstrap before VPS is provisioned

**Architecture:**
```
[grapheneGate — Phone]
  BearDog: key management + BTSP
  Songbird: TURN relay on phone's IP (cellular or WiFi)
  SkunkBat: audit logging

        ↕ BTSP E2E encrypted

[New gate — local hardware]
  Bootstraps through grapheneGate's Songbird relay
  Once VPS relay is reachable, migrates federation to VPS
  grapheneGate becomes optional (mesh is self-sustaining)
```

**Songbird on phone:**
- Listens on abstract socket (Android SELinux compatible, validated in ecoBin v2.0)
- Exposes TURN relay on local network for gate-to-gate traffic
- Federates with home mesh via cellular data when WiFi is hostile

### Role 3 — Sovereign Mesh Seed (Horizon)

grapheneGate as the **sole requirement** to bootstrap an entire ecosystem
instance from scratch.

**What grapheneGate carries:**
- `FAMILY_SEED` (in hardware-backed keystore, never extractable)
- Lineage seeds for known devices
- `ecosystem_manifest.toml` (repo list, gate profiles)
- `plasmidBin` binary (aarch64-android)
- `ecoBins` — compiled primals for target architectures
- Latest `wateringHole` snapshot (impulses, standards, handoffs)

**Bootstrap from zero:**
```bash
# On any Linux machine with USB:
adb shell plasmidbin bootstrap --from-graphene \
    --target $(hostname) \
    --gate-class lan_cluster

# grapheneGate:
# 1. Authenticates operator via biometric + BTSP
# 2. Exports encrypted bootstrap bundle to target
# 3. Target decrypts with BTSP session key
# 4. plasmidBin installs NUCLEUS from ecoBins
# 5. BearDog receives lineage seed for new gate
# 6. Songbird federates with home mesh (if reachable)
# 7. temporal.cascade syncs repos from nearest peer
```

**Scrutiny resistance:**
- Phone appears as standard Pixel 8a running GrapheneOS
- No ecosystem apps visible in launcher (background service only)
- BearDog data encrypted at rest with hardware-backed keys
- No ecosystem artifacts discoverable without BTSP authentication
- Duress mode (future): secondary BTSP passphrase yields decoy profile

---

## Network Profiles

| Scenario | Network | Federation Path | Trust Level |
|----------|---------|-----------------|-------------|
| Home LAN (WiFi) | 192.168.1.x / 4.x | Direct beacon + UDS-over-USB | Covalent |
| Home LAN (USB tether) | USB RNDIS | Direct UDS | Covalent |
| Remote WiFi (trusted) | Foreign subnet | TURN via cellular → home VPS | Covalent through relay |
| Remote WiFi (hostile) | Captive portal / monitored | BTSP over TURN, zero metadata | Covalent through relay |
| Cellular only | Mobile carrier | TURN → home VPS → mesh | Covalent through relay |
| Airgap (USB only) | No network | USB bootstrap bundle transfer | Covalent (offline) |

---

## Security Invariants

1. **FAMILY_SEED never leaves hardware secure element** — derived keys only
2. **Beacon seed shared via out-of-band provisioning** — never over network
3. **Lineage seed unique per device** — grapheneGate's identity is non-transferable
4. **All network traffic BTSP-encrypted** — observers see random noise
5. **No persistent network identity** — IP/MAC change does not break trust
6. **Beacon broadcasts time-limited** — automatic expiry, no permanent advertisement
7. **SkunkBat audit trail** — every trust operation logged locally
8. **Verified boot chain** — GrapheneOS -> Titan M2 -> BearDog keystore

---

## Prerequisites

| Requirement | Status | Notes |
|-------------|--------|-------|
| GrapheneOS installed on Pixel 8a | DONE | Currently plugged into eastGate (tether + gate) |
| BearDog deployed on Android | **DONE** | aarch64-musl static binary, TCP fallback mode |
| aarch64-android build target | CONFIGURED | `.cargo/config.toml` has target |
| ecoBin abstract socket transport | DONE | Driven by GrapheneOS SELinux constraints |
| BirdSong beacon broadcast | IMPLEMENTED | Two-seed genetics standard validated |
| Hardware-backed keystore integration | NOT STARTED | Android Keymaster / StrongBox API |
| plasmidBin aarch64-musl binaries | **14/14 BUILT** | Full depot: all primals built and deployable |
| TURN relay on Android | NOT TESTED | Songbird abstract socket -> network relay |
| deploy_pixel.sh handlers | **DONE** (Wave 99) | All 13+ primal startup handlers wired |
| ADB port forwarding | **DONE** (Wave 132c) | bearDog:9100, songBird:9200, skunkBat:9140 |
| USB tether dual-role | **LIVE** (Wave 132c) | Tether + gate simultaneously operational |

---

## Relation to Existing Standards

| Standard | Relation |
|----------|----------|
| `../foundations/DARK_FOREST_GLACIAL_GATE_STANDARD.md` | grapheneGate enforces all 5 pillars on mobile |
| `DARK_FOREST_BEACON_GENETICS_STANDARD.md` | Two-seed model: beacon (family) + lineage (device) |
| `../protocols/BTSP_PROTOCOL_STANDARD.md` | All grapheneGate sessions use BTSP |
| `../foundations/K_DERM_TOPOLOGY_STANDARD.md` | grapheneGate operates at plasma membrane boundary |
| `GATE_SETUP_STANDARD.md` | grapheneGate is a specialized gate; follows onboarding flow |
| `DISTRIBUTED_COVALENT_DEPLOYMENT.md` | grapheneGate extends the WAN covalent pattern |
| `../fossilRecord/wave150s_standards/ECOBIN_ARCHITECTURE_STANDARD.md` | ecoBin v2.0 abstract-socket already validated |

---

## Evolution Timeline

| Wave | Milestone | Status |
|------|-----------|--------|
| 68 | grapheneGate in ecosystem manifest + matrix | DONE |
| 68 | This bootstrap standard published | DONE |
| 99 | deploy_pixel.sh all 13 primal handlers | DONE |
| 103 | 3/14 aarch64 binaries in depot (songbird, skunkbat, sourdough) | DONE |
| 113 | bearDog pure Rust (aws-lc-rs eliminated) | DONE |
| 128 | Full aarch64 plasmidBin depot (14/14 binaries) | DONE |
| 132c | Tower deployed + ADB tether live | **DONE** |
| 132c | Enrolled in mesh_topology.toml (transport=adb) | **DONE** |
| NEXT | Role 1: beacon broadcast + lineage verification E2E test | P2 |
| NEXT | songBird mesh.peer via cellular (tether as relay) | P2 |
| TBD | BearDog Keymaster/StrongBox integration design | P3 |
| TBD | Role 2: BTSP relay on phone, bootstrap via USB | P3 |
| TBD | Role 3: full sovereign mesh seed | Horizon |

---

*Wave 132c. The phone is live: tether + gate + future relay. The mesh absorbs.*

---

## FILE: `operations/MESH_DEPLOYMENT_STANDARD.md`

# Mesh Deployment Standard — Team & Gate Handoff

**Authority**: wateringHole consensus (Wave 66, reviewed 155h)
**Version**: 1.0.0
**Applies to**: All gates, all teams, VPS nodes, new gate onboarding

---

## Purpose

This standard defines how work is delegated to teams and gates across the
mesh. It covers the full lifecycle: task assignment via impulse, team
bootstrap on a gate, work execution, delivery via cascade, and validation.

The goal is zero-friction handoff: a team on any gate should receive work,
execute it, and deliver results without manual coordination from eastGate.

---

## 1. The Handoff Lifecycle

```
eastGate                    targetGate (team)
   │                              │
   ├─ impulse.post ──────────────▶│  FRAGO with scope + acceptance criteria
   │                              │
   │                    potential.sense  │  Team reads pending impulse
   │                              │
   │◀── impulse.ack ─────────────┤  Team acknowledges + begins work
   │                              │
   │                    context.weave   │  Team weaves context braid (progress)
   │                              │
   │                    git push forgejo│  Team pushes code to periplasm
   │                              │
   │  temporal.cascade            │
   ├─ (auto-pull) ◀──────────────┤  eastGate cascades the delivery
   │                              │
   │  potential.sense             │  eastGate sees acked impulse
   │                              │
   │  impulse.archive             │  eastGate discharges spent impulse
   └──────────────────────────────┘
```

---

## 2. Firing an Impulse (Task Assignment)

Use `membrane impulse.post` to delegate work. The impulse is committed to
`wateringHole/impulses/active/` and propagated via the cascade.

```bash
membrane impulse.post \
  --to <targetGate> \
  --type frago \
  --subject "<one-line task summary>"
```

### Impulse Types

| Type | Use | Expectation |
|---|---|---|
| `frago` | Fragmentary order — new task or scope change | Ack required, work expected |
| `sitrep` | Situation report — status update | Informational, no ack needed |
| `aar` | After-action review — completed work summary | Informational, archive after read |

### Impulse Body

The `--subject` is the headline. For detailed scope, edit the generated TOML
file in `impulses/active/` before committing. Include:

- **Scope**: What files/modules/repos are involved
- **Acceptance criteria**: What "done" looks like
- **Priority**: `critical` / `routine` / `low`
- **Deadline**: Wave number or date (optional)

---

## 3. Receiving Work (Team Bootstrap)

When a team spins up on a gate, they:

### 3a. Cascade Pull

```bash
membrane temporal.cascade
```

This pulls all repos for the gate's manifest profile, including any new
impulses in `wateringHole/impulses/active/`.

### 3b. Sense Pending Impulses

```bash
membrane potential.sense --all
```

Shows all pending impulses addressed to this gate. The team reads the FRAGO
and understands the scope.

### 3c. Acknowledge

```bash
membrane impulse.ack <impulse-id> --note "Starting work on relay evolution"
```

The ack is committed to wateringHole and propagated on the next cascade.
eastGate (or any gate) can see acked impulses via `potential.sense`.

### 3d. Sense Context

```bash
membrane context.sense --all
```

Shows active context braids from all gates — what other teams are working on,
where they are, and what's blocking them. This prevents collision.

---

## 4. Working (Execution)

### 4a. Weave Context Braids

As work progresses, the team weaves braids so other gates can sense state:

```bash
membrane context.weave \
  --project gardens/cellMembrane \
  --summary "relay.rs complete, 3 subcommands, 400 lines"
```

Braids are ephemeral (48h TTL by default) and auto-decay. They're stored in
`wateringHole/context/<gateName>/`.

### 4b. Push to Forgejo

All code pushes go to Forgejo only. The K-Derm relay chain handles GitHub
propagation automatically:

```bash
git push forgejo main
```

The relay chain: gate → golgiBody (covalent) → peptidoglycan (metallic) →
golgiBody-ext (ionic) → GitHub (weak).

### 4c. Handoff Documents

For significant deliveries, write a handoff document:

```
wateringHole/handoffs/WAVE<NN>_<PROJECT>_<SUMMARY>_<DATE>.md
```

Include: what changed, what tests pass, what remains, and acceptance evidence.
After the next wave, archive it to `handoffs/archive/wave<NN>/`.

---

## 5. Receiving Deliveries (Cascade Pull)

When a team pushes to Forgejo, any gate can pull the delivery:

```bash
membrane temporal.cascade
```

The cascade is manifest-driven — each gate pulls only the repos in its profile.
Repos not in the gate's profile are ignored.

### Conflict Resolution

If `temporal.cascade` reports `FAIL pull forgejo failed (ff-only)`:

```bash
cd <repo>
git stash
git pull --rebase forgejo main
git stash pop
```

Or accept upstream wholesale:

```bash
git checkout --theirs <conflicting-file>
```

---

## 6. Validation

### 6a. Test Suite

After absorbing a delivery, run the relevant test suite:

```bash
cargo test --workspace          # In the delivered repo
```

For ecosystem-wide validation:

```bash
cd springs/primalSpring
cargo test --workspace          # 838+ tests, 57 scenarios
```

### 6b. Temporal Check

Verify all repos are temporally aligned:

```bash
membrane temporal.check
```

This shows the HEAD position of each repo across all remotes (forgejo, origin).
Divergence is flagged.

### 6c. Potential Gradient

Check ecosystem health:

```bash
membrane potential.check
```

Shows active impulse count, ack status, and wave distribution. A healthy
gradient has zero unacked impulses older than 48 hours.

---

## 7. Gate Profiles

Each gate has a repo profile in `ecosystem_manifest.toml` under
`[gates.<name>]`. The profile determines which repos cascade to that gate.

### Adding a New Gate

1. Add the gate profile to `ecosystem_manifest.toml`:

```toml
[gates.newGate]
repos = [
    "nestGate", "wateringHole", "plasmidBin",
    "bearDog", "songBird", "biomeOS",
    # ... repos this gate needs
]
```

2. On the new gate:

```bash
echo "newGate" > .gate
membrane temporal.cascade --clone-missing
```

3. Fire a sitrep to announce:

```bash
membrane impulse.post --to eastGate --type sitrep \
  --subject "newGate online, 22 repos synced"
```

### Gate Types

| Type | Bond | Example | Role |
|---|---|---|---|
| Physical (LAN) | Covalent | eastGate, ironGate | Full development |
| Physical (WAN) | Covalent (SSH) | flockGate | Remote development |
| VPS Inner | Metallic | golgiBody | Forgejo, primals |
| VPS Mediator | Metallic | peptidoglycan | Relay, builds |
| VPS Outer | Ionic/Weak | golgiBody-ext | DNS, sporePrint, GitHub push |

---

## 8. Team Patterns

### Single-Team Sprint

One team works on one repo. Standard impulse → ack → work → push → cascade.

### Multi-Team Parallel

Multiple teams on different gates work on different repos simultaneously.
Context braids prevent collision:

```
ironGate → cellMembrane (relay evolution)
ironGate → projectNUCLEUS (deploy script evolution)
flockGate → sporePrint (content evolution)
```

Each team weaves braids. eastGate senses all braids via `context.sense --all`.

### Cross-Team Dependency

When Team A's work depends on Team B:

1. Team A fires an impulse to Team B with the dependency
2. Team B acks and delivers
3. Team A cascades the delivery and continues

The impulse system handles the coordination. No manual message passing needed.

---

## 9. Deployment Artifacts

### Binary Distribution

Compiled primal binaries are distributed via `wateringHole/genomeBin/`:

```
genomeBin/primals/<name>/<version>/<name>-<arch>-<os>
```

Gates fetch binaries via:

```bash
membrane plasmid.fetch --primal <name> --source github
```

### Service Units

Systemd service templates are stored with their owning projects:

| Owner | Location | What |
|---|---|---|
| cellMembrane | `deploy/hooks/forgejo/` | Forgejo post-receive hook |
| cellMembrane | `deploy/hooks/cursor/` | Cursor context-sense hook |
| wateringHole | `systemd/cascade-pull.*` | Cascade timer template |
| Each primal | `/etc/systemd/system/<primal>-membrane.service` | VPS service units |

### VPS Deployment

VPS service units live on the VPS nodes directly (not in git). The pattern:

1. Build locally: `cargo build --release --bin <primal>`
2. Copy to VPS: `scp target/release/<primal> golgi:/opt/membrane/`
3. Restart: `ssh golgi "systemctl restart <primal>-membrane"`

Future: `membrane deploy.<primal>` automates this (Wave 67+ target).

---

## 10. Quick Reference

| Task | Command |
|---|---|
| Pull all repos | `membrane temporal.cascade` |
| Check temporal alignment | `membrane temporal.check` |
| See pending impulses | `membrane potential.sense --all` |
| Fire a task | `membrane impulse.post --to <gate> --type frago --subject "..."` |
| Ack a task | `membrane impulse.ack <id>` |
| Archive spent impulses | `membrane impulse.archive` |
| Weave context | `membrane context.weave --project <path> --summary "..."` |
| Sense all context | `membrane context.sense --all` |
| Check ecosystem health | `membrane potential.check` |
| Resolve gate identity | `membrane identity.resolve` |
| List gate repos | `membrane manifest.repos <gate>` |
| Fetch primal binary | `membrane plasmid.fetch --primal <name>` |
| Full relay (K-Derm) | `membrane relay.run` |

---

*This standard enables autonomous team operation across the gate mesh.
Teams receive work via impulses, sense context from other teams, execute
independently, and deliver via the cascade. No manual coordination required.*

---

## FILE: `operations/REPO_MEMBRANE_BOUNDARY.md`

<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Repo Membrane Boundary — Git Host Classification

**Date**: May 17, 2026
**Status**: Active
**Authority**: WateringHole Consensus
**Related**: `SOVEREIGNTY_STANDARDS.md`, `MEMBRANE_CHANNEL_ARCHITECTURE.md`

---

## Purpose

This document classifies every ecoPrimals repository by its membrane
boundary — where it should live (inner membrane only, dual-push, or
outer membrane only) and why. The classification drives push policy,
CI strategy, and contamination prevention.

---

## Membrane Model

| Layer | Git Host | Trust | Sync Direction |
|-------|----------|-------|----------------|
| **Inner membrane** | Forgejo (`git.primals.eco:3000`) | Covalent — full trust, private by default | Direct push to Forgejo only |
| **Trailing mirror** | GitHub primary → Forgejo pulls | Observed primary — Forgejo trails GitHub server-side | GitHub authoritative, Forgejo auto-syncs (8h) |
| **Outer membrane** | GitHub only | Observed — public archive, CDN, Pages | `git push origin` only |

**Note**: The "Dual-push" model was retired May 23, 2026. Dev happens across
multiple gates — per-machine push hooks don't scale. Forgejo now pulls
from GitHub server-side. When covalent gates host Forgejo, we invert.

---

## Repository Classification

### Inner Membrane Only (Forgejo-only)

These repos contain operational data, credentials, or sensitive
infrastructure details that must not exist on external substrate.

| Repo | Org | Content | Rationale |
|------|-----|---------|-----------|
| `cellMembrane` | sporeGarden | VPS deployment, SSH key mgmt, TURN credentials, RustDesk keys | Operational secrets — inner membrane only |
| *(future)* | — | Any new credential/secret/operational repos | Default to inner-only for ops repos |

**Current gap**: `cellMembrane` is currently private on GitHub. It
should be moved to Forgejo-only once Forgejo is operationally primary.
See "Decision: cellMembrane" below.

### Trailing Mirror (GitHub Primary → Forgejo Pulls)

Public code repos where GitHub is operationally primary and Forgejo
trails as an inner membrane mirror (auto-synced every 8h server-side).

**Gardens (sporeGarden org):**

| Repo | GitHub Visibility | Content |
|------|-------------------|---------|
| `projectNUCLEUS` | Public | Sovereignty layer, deployment infrastructure |
| `projectFOUNDATION` | Public | Knowledge layer, thread lineage, validation evidence |
| `lithoSpore` | Public | Verification chassis, USB-deployable validation |
| `esotericWebb` | Public | UI/agentic interaction layer |

**Springs (syntheticChemistry org):**

| Repo | GitHub Visibility | Content |
|------|-------------------|---------|
| `primalSpring` | Public | Coordination spring, composition validation |
| `wetSpring` | Public | Breseq/LTEE science validation |
| `hotSpring` | Public | GPU compute validation |
| `groundSpring` | Public | Geospatial validation |
| `airSpring` | Public | Atmospheric/ADS-B validation |
| `neuralSpring` | Public | Neural/AI validation |
| `ludoSpring` | Public | Game engine validation |
| `healthSpring` | Public | Health/clinical validation |

**Primals (ecoPrimals org):**

| Repo | GitHub Visibility | Content |
|------|-------------------|---------|
| `bearDog` | Public | Security, crypto, BTSP identity |
| `songBird` | Public | Discovery, routing, federation |
| `toadStool` | Public | Compute dispatch |
| `nestGate` | Public | Storage, content serving |
| `squirrel` | Public | AI/MCP orchestration |
| `rhizoCrypt` | Public | Provenance DAG |
| `loamSpine` | Public | Provenance spine |
| `sweetGrass` | Public | Provenance braid |
| `biomeOS` | Public | Orchestration layer |
| `petalTongue` | Public | Storytelling/UI bridge |
| `skunkBat` | Public | Defense/audit |
| `barraCuda` | Public | GPU compute dispatch |
| `coralReef` | Public | Distributed compute mesh |
| `bingoCube` | Public | Validation framework |
| `sourDough` | Public | Starter culture/bootstrap |

**Infrastructure (ecoPrimals org):**

| Repo | GitHub Visibility | Content |
|------|-------------------|---------|
| `plasmidBin` | Public | Binary depot, deploy scripts |
| `wateringHole` | Public | Ecosystem standards/docs |
| `whitePaper` | Public | Research documentation |

### Outer Membrane Only (GitHub-only)

Repos that exist solely for external visibility and don't need
inner membrane presence.

| Repo | Org | Content | Rationale |
|------|-----|---------|-----------|
| `fossilRecord` | ecoPrimals | Archived documentation | Public archive — no development, read-only fossil record |
| `sporePrint` | ecoPrimals | GitHub Pages deployment | Generated site — the deployment target IS GitHub Pages |

---

## Contamination Risk Matrix

| Risk | Vector | Repos Affected | Mitigation |
|------|--------|----------------|------------|
| API keys pushed to GitHub | Accidental `git add` of `.env` files | All primals, especially `squirrel` | `.gitignore` patterns cover `.env`, `*.env`, `.env.*` — verified ecosystem-wide |
| Operational secrets on GitHub | `cellMembrane` is on GitHub (private) | `cellMembrane` | Move to Forgejo-only (pending decision) |
| Local experiments leak to GitHub | Developer pushes WIP with sensitive data | Any repo | Pre-push hook checking for sensitive patterns (future) |
| Forgejo/GitHub divergence | Pull mirror fails or timer stops | All trailing-mirror repos | `forgejo_pull_mirror.sh --status` + `forgejo_sync.sh --status` checks |

### .env Audit Summary (May 17, 2026)

| File | Git-Tracked | Content | Risk |
|------|-------------|---------|------|
| `squirrel/.env` | No (gitignored) | JWT_SECRET | None — local only |
| `squirrel/mcp-config.env` | No (gitignored) | OpenAI/Anthropic/HuggingFace API keys | None — local only |
| `bearDog/production.env` | Yes | Template config (no real secrets) | None — placeholder values |
| `songbird/config/production.env` | No (gitignored) | Template DB URL with placeholder password | None — local only |
| `hotSpring/metalForge/*.env` | Yes | GPU/hardware config | None — no secrets |
| `plasmidBin/ports.env` | Yes | Port assignments | None — no secrets |
| `ecoPrimals/.env.test` | Yes | Test env vars (RUST_LOG, timeouts) | None — no secrets |

---

## Forgejo Operational Status

### Current Reality (May 23, 2026)

Forgejo is the **trailing inner membrane mirror**. GitHub is authoritative.
When covalent gates host Forgejo on sovereign infrastructure, we invert.

- **31/31 trailing-mirror repos** synced to Forgejo (cellMembrane is inner-only)
- All 3 Forgejo orgs populated: sporeGarden (5), ecoPrimals (19), syntheticChemistry (8)
- **25 repos**: Native Forgejo **pull mirrors** from GitHub (auto-sync every 8h, server-side)
- **6 repos**: Regular repos, synced via `forgejo_sync.sh` + systemd timer (8h)
  - Private on GitHub: `bearDog`, `skunkBat`, `whitePaper`
  - Large/clone-timeout: `neuralSpring`, `primalSpring`, `wetSpring`
- **1 repo**: `cellMembrane` — inner-only, direct push (not mirrored from GitHub)
- CI still runs on GitHub Actions (`notify-sporeprint.yml`, etc.)
- Forgejo reachable at `127.0.0.1:3000` (LAN) and `git.primals.eco:3000` (tunnel)

**Why pull, not push?** Dev happens across multiple gates (ironGate, eastGate,
southGate, etc.). Per-machine push hooks don't scale. Server-side pull mirrors
ensure Forgejo stays consistent regardless of which gate pushed to GitHub.

### Sync Tooling

| Tool | Location | Purpose |
|------|----------|---------|
| Native pull mirrors | Forgejo server-side | 25 repos auto-sync from GitHub every 8h |
| `forgejo_sync.sh` | `gardens/cellMembrane/forgejo_sync.sh` | Sync 6 non-mirror repos (fetch origin → push forgejo) |
| `forgejo-sync.timer` | `~/.config/systemd/user/` | Systemd timer fires `forgejo_sync.sh` every 8h |
| `forgejo_pull_mirror.sh` | `gardens/cellMembrane/forgejo_pull_mirror.sh` | Manage native mirrors (migrate, status, trigger sync) |

### Migration Path

1. ~~**GitHub-only development**~~ — completed May 23, 2026
2. ~~**Push-based sync**~~ — replaced May 23, 2026 (doesn't scale to multi-gate)
3. **Current**: Forgejo pulls from GitHub server-side. GitHub remains
   operationally primary for CI and dev. Forgejo is lagging mirror.
4. **Near-term**: Port `notify-sporeprint.yml` to Forgejo Actions,
   validate CI parity. Move 3 private repos to native mirrors with GitHub PAT.
5. **Inversion**: When covalent gates host Forgejo, it becomes primary.
   GitHub becomes the push mirror target.

---

## Decision: cellMembrane Placement

**Context**: `cellMembrane` is the only private repo in the
`sporeGarden` GitHub org. It contains VPS IP addresses, SSH key
management procedures, TURN credential paths, and RustDesk key
material. Its `.gitignore` correctly excludes `.age`, `.pem`, `id_*`,
`.key`, and token files.

**Options**:

1. **Forgejo-only** (recommended): Remove from GitHub entirely. All
   access via Forgejo tunnel. Cleaner sovereignty posture — ops data
   never touches external substrate.

2. **Keep GitHub private**: Convenient for cross-machine pulls without
   tunnel. Relies on GitHub's private repo access controls.

**Recommendation**: Move to Forgejo-only when Forgejo is confirmed
operationally stable (reachable, backups working). Until then, GitHub
private is acceptable as a transitional state.

---

## Push Policy Enforcement

### Automated (current — May 23, 2026)

**Server-side pull mirrors** (25 repos): Forgejo natively pulls from
GitHub every 8h. Zero dev-machine involvement. Triggered via
`POST /api/v1/repos/{owner}/{repo}/mirror-sync` for on-demand sync.

**Systemd timer** (6 non-mirror repos): `forgejo-sync.timer` runs
`forgejo_sync.sh` every 8h on the Forgejo host (ironGate). Fetches
from GitHub origin, pushes to local Forgejo. Independent of which
dev machine pushed to GitHub.

```bash
# Check mirror status (all 31 repos)
FORGEJO_TOKEN=<tok> ./forgejo_pull_mirror.sh --status

# Sync 6 non-mirror repos manually
./forgejo_sync.sh

# Trigger all native mirrors + sync non-mirrors
FORGEJO_TOKEN=<tok> ./forgejo_sync.sh --all

# Force-push diverged repos (after rebase)
./forgejo_sync.sh --force
```

### Inner-only enforcement (future)

A pre-push hook can enforce the membrane boundary for `cellMembrane`:

```bash
# .git/hooks/pre-push (inner-only repos)
remote="$1"
if [[ "$remote" == "origin" ]]; then
  echo "ERROR: This repo is inner-membrane-only. Push to forgejo instead."
  exit 1
fi
```

Post-inversion: Forgejo post-receive hooks auto-mirror to GitHub.

---

## Cross-References

- `SOVEREIGNTY_STANDARDS.md` — Forgejo as Primary Git Host section
- `MEMBRANE_CHANNEL_ARCHITECTURE.md` — Physical channel architecture
- `projectNUCLEUS/deploy/forgejo_mirror.sh` — Legacy setup tooling (creates repos + adds remotes)
- `CELLMEMBRANE_FIELDMOUSE_DEPLOYMENT.md` — fieldMouse VPS specification
- `cellMembrane/README.md` — Operational repo documentation

---

## Changelog

| Date | Change |
|------|--------|
| 2026-05-17 | Initial version — repo membrane boundary classification from infrastructure review |
| 2026-05-23 | Forgejo synced (31/31 repos). Pull-mirror model: 25 native mirrors + 6 timer-synced + 1 inner-only. Cursor hooks removed (wrong model for multi-gate). |

---

## FILE: `operations/SPORE_OWNERSHIP_MATRIX.md`

# Spore Ownership Matrix

**Authority**: eastGate overwatch | **Wave**: 137b (reviewed 155h) | **Last updated**: Jul 13, 2026

---

## Provenance Trio — Role Definitions

The provenance trio provides the content-addressed, immutable, attributed persistence
layer for the ecosystem. Together with nestGate, they form the **Nest Atomic** composition.

| Primal | Role | Metaphor | Socket | Capabilities |
|--------|------|----------|--------|-------------|
| **rhizoCrypt** | Ephemeral DAG | Root network — branching, checkout, slicing | `rhizocrypt.sock` | `dag.slice.checkout` |
| **loamSpine** | Immutable ledger | Soil backbone — permanent, append-only | `loamspine.sock` | `braid.commit` |
| **sweetGrass** | Attribution braid | Prairie grass — woven provenance, SNARE targeting | `sweetgrass.sock` | `braid.commit` |
| **nestGate** | Persistent storage | Nest — content-addressed store, RPC gateway | `nestgate.sock` | `footprint.*`, `content.*`, `coord.*` |

## Ownership Boundaries

### rhizoCrypt — Ephemeral DAG

**Owns**: DAG sessions, branching, checkout, merge, diff operations.
**Does not own**: Permanent storage (that's loamSpine), attribution (that's sweetGrass).

| Capability | Description |
|-----------|-------------|
| `dag.slice.checkout` | Checkout a DAG slice at a specific commit/ref |
| `dag.branch` | Create/list/delete branches in the ephemeral DAG |
| `dag.merge` | Merge DAG branches |
| `dag.diff` | Diff between DAG states |

**Data lifecycle**: Ephemeral. DAG sessions are pruned after finalization. Permanent
records are committed to loamSpine. rhizoCrypt is the "working directory" — loamSpine
is the "committed history."

### loamSpine — Immutable Ledger

**Owns**: Append-only commit log, permanent record, Merkle spine.
**Does not own**: Working state (that's rhizoCrypt), who-did-what (that's sweetGrass).

| Capability | Description |
|-----------|-------------|
| `braid.commit` | Commit a finalized DAG session to the immutable spine |
| `spine.query` | Query the commit log by hash, range, or filter |
| `spine.verify` | Verify Merkle chain integrity |

**Data lifecycle**: Permanent. Once committed, records are immutable. loamSpine is the
ecosystem's "git log" — content-addressed, hash-chained, never rewritten.

### sweetGrass — Attribution Braid

**Owns**: Who did what, when, why. Provenance attribution. SNARE-protein targeting for
cross-membrane workload routing.
**Does not own**: The data itself (that's nestGate/rhizoCrypt), the commit history (that's loamSpine).

| Capability | Description |
|-----------|-------------|
| `braid.commit` | Attach attribution metadata to a spine commit |
| `braid.verify` | Verify attribution chain integrity |
| `braid.wrap` | Wrap a workload in provenance braid for cross-membrane transport |

**Data lifecycle**: Permanent (co-located with loamSpine entries). sweetGrass braids are
the "git blame" + "signed commits" — they prove who produced what and authorize
cross-membrane routing via SNARE targeting (K-Derm vesicle transport).

### nestGate — Content-Addressed Store

**Owns**: Blob storage, CAS deduplication, RPC gateway, HTTP content serving,
coordination data (blurbs, AARs, wave state), footPrint project persistence.
**Does not own**: Provenance (that's the trio), routing (that's songBird), crypto (that's bearDog).

| Capability | Description |
|-----------|-------------|
| `content.store` | Store content-addressed blob |
| `content.get` | Retrieve blob by hash |
| `content.replicate` | Federate content to another gate |
| `footprint.*` | Project CRUD (CAS-backed, Wave 137b) |
| `coord.*` | Coordination data ingest/query |

## Composition: rootPulse

rootPulse is not a primal — it's the **composition** of the provenance trio operating
together as a distributed version control system:

```
rootPulse = rhizoCrypt (working tree) + loamSpine (commit log) + sweetGrass (attribution)
```

| rootPulse Operation | rhizoCrypt | loamSpine | sweetGrass |
|--------------------|-----------|-----------|------------|
| `commit` | Finalize DAG session | Append to spine | Attach attribution |
| `branch` | Create DAG branch | — | — |
| `merge` | Merge DAG branches | Record merge commit | Record merge author |
| `diff` | Compute DAG diff | — | — |
| `federate` | — | Replicate spine segment | Replicate braid segment |
| `verify` | — | Verify Merkle chain | Verify attribution chain |

## Composition: Nest Atomic

The Nest composition (defined in `ecosystem_manifest.toml`) combines all four:

```
Nest = nestGate + rhizoCrypt + loamSpine + sweetGrass
```

- **nestGate** provides the CAS blob store and RPC gateway
- **rhizoCrypt** provides the ephemeral working DAG
- **loamSpine** provides the immutable commit spine
- **sweetGrass** provides attribution braids

Target deployment: westGate (76TB ZFS cold storage).

## Cross-Membrane Interaction (K-Derm)

Per the K-Derm topology standard, sweetGrass braids act as SNARE-protein targeting
signals for vesicle transport:

1. **Budding**: Workload originates. sweetGrass creates braid (DAG session + data refs + attribution)
2. **Transport**: Braid-wrapped workload crosses membrane boundaries
3. **Fusion**: Target membrane verifies braid — DAG refs via rhizoCrypt, attribution chain intact
4. **Facilitated diffusion**: Pre-braided workloads cross faster (no re-verification needed)

Braids are stripped at the outer membrane (only results cross, not provenance) —
this is the ionic/covalent bond boundary.

---

*Spore Ownership Matrix — Wave 137b. Defines the three-way provenance split
(rhizoCrypt/loamSpine/sweetGrass) and their relationship to nestGate and rootPulse.*

---

## FILE: `ORTHOGONAL_DIMENSIONS_REVIEW.md`

# Orthogonal Dimensions Review — Reusable Checklist

**Purpose**: Systematic reassessment checklist for overwatch cascade reviews.
Use at wave boundaries or whenever a comprehensive posture check is needed.

**Fossilization**: Dimensions that are fully complete with no open items graduate
to the FOSSILIZED section. They are not re-checked unless a regression signal
appears. This keeps the active review focused on evolving concerns.

---

# ACTIVE DIMENSIONS

## 1. Temporal / Coordination

- [x] `wave.toml` reflects current wave ID, sub, and posture (Wave 155i)
- [x] Gate heads published (`heads/*.toml`) — golgiBody auto-publishing active
- [x] `freshness.toml` uses tree hashes (DAG, not cyclic graph)
- [x] Active impulses: 0 (26+ fossilized)
- [x] ecosystem_manifest.toml version current (v3.1.0)
- [x] 43/43 repos synced with Forgejo
- [x] **ECOSYSTEM_BLURB.md** is the universal handoff (Tracks A+B converged)
- [x] Fossilized: 42+ docs across `fossilRecord/wave150x_*` and `wave151a_completion/`
- [x] **waterFall** publish cascade defined — git → impulse → DAG → braid → anchor → relay
- [x] Impulse/Potential, Context Braid, Ecosystem Communication standards active
- [x] NeuralBridge in membrane-shadow routes with try-primal-first semantics
- [x] whitePaper gen/ review COMPLETE (Wave 151c)
- [x] JOSS publication strategy defined
- [x] GLOSSARY.md refreshed (Wave 155b)
- [x] cellMembrane + plasmidBin cascaded to Forgejo
- [x] **30+ handoff docs + AARs** delivered Wave 155f–i (code teams, gate AARs, Nest Atomic, composition broker, deep debt sweeps, Windows deployment)
- [ ] waterFall graph partially wired — full composition pending Provenance Trio
- [ ] Context braids not yet replacing blurb paste — graduation path documented
- [x] `freshness.toml` updated to Wave 155h with 38 HEAD SHAs
- [x] **Nest Atomic LIVE on westGate** — 8 services, Provenance Trio 6/7 live, ZFS online
- [x] sweetGrass G3 E2E validated (v0.8.0, 1,636 tests, mock loamSpine UDS)
- [x] westGate CAS on ZFS verified — 3,216 objects, 25.3TB pool, 1.50× compression, ARC 99.98% hit
- [x] P0 glibc depot FIXED. P1 WG DNS FIXED. P1 membrane depot REBUILT (J6).
- [x] **Deep debt wave**: 8 primals shipped simultaneous sweeps (nestGate, toadStool, cellMembrane, barraCuda, coralReef, sweetGrass, skunkBat, nestGate)
- [x] sporeGate depot refresh: Linux 19/19 binaries, BLAKE3 verified, health 5/11→9/11
- [x] strandGate Compute Trio rebuilt from glibc source, RTX 3090 profiled
- [x] ~~biomeOS composition broker~~ — **SHIPPED** (v4.45): riboCipher framing + BTSP executor, 35 E2E tests, 8,564 tests total
- [x] **blueGate Tower G1 COMPLETE** — 3/3 primals on Windows (source build, 3m 56s)
- [x] **blueGate Nest Atomic VALIDATED** — 10/10 primals on Windows, 107.6 MB, TCP-only
- [x] **westGate composition broker LIVE** — biomeOS v4.45 deployed, 704 capabilities, COORDINATED mode, E2E routing proven
- [x] songBird 3 follow-up Windows compile fixes shipped (`d9bda555`)
- [x] cellMembrane 45+ magic numbers centralized to `constants.rs` (1,221 tests)
- [x] strandGate **Node Atomic VALIDATED** — 450 methods, 746 pipelines/sec, sub-ms GPU dispatch
- [x] barraCuda RTX 3090 + RX 6950 XT dual-GPU validated — FHE bit-perfect, cdist 65× SciPy
- [x] toadStool S346 deep evolution + deployment docs (9,193+ tests, doctor CLI fixed)
- [ ] 3 enrolling gates have no published heads in `heads/*.toml`
- [ ] **Windows depot stale** — 14 `.exe` from 07/16, no Windows CI gate

## 2. Ecological (Primal Health)

- [x] All primals compile — 5 Tier 1 genomeBin architectures
- [x] ~~P0: glibc depot target~~ — **FIXED** (cellMembrane `8d9bb58`): `targets_for_primal()` auto-appends gnu for GPU primals
- [x] 43/43 repos Forgejo-first
- [x] **~63K+ primal tests validated this wave** (nestGate 13K+, toadStool 9.2K+, biomeOS 8.5K, petalTongue 6.6K, barraCuda 5K, coralReef 3.5K, sweetGrass 1.6K, loamSpine 1.7K, cellMembrane 1.2K)
- [x] Zero TODO/FIXME/HACK in project code — 15/15 primals clean
- [x] nestGate vendor elimination COMPLETE (Wave 150u)
- [x] Production `.unwrap()` — 0 in critical-path primals
- [x] `unsafe` scoped to GPU primals, science FFI, and crypto
- [x] Format drift RESOLVED — all repos clean
- [x] bearDog: 11,993 tests, FIDO2 hardware, beacon proximity, HSM agnostic
- [x] songBird: 14,835+ tests, `mesh.gate_enroll`, universal-ipc, J3+J4+J5, `tower.health` facade, **ACME HTTP-01 Phase 1**
- [x] nestGate: **13,095+** tests, CAS on ZFS verified (3,119 objects), deep debt complete, zero unsafe, zero panics, ghost methods removed, CLI evolved
- [x] toadStool: **9,193+** tests, **S346**: security fail-closed (macOS/Windows sandbox), unsafe containment (hw-safe crate), 75 doc warnings fixed, doctor CLI bug fix
- [x] rhizoCrypt: 1,456 tests, BTSP→DAG bridge, cross-gate provenance chain
- [x] loamSpine: **1,739** tests, **BTSP handshake dedup**: `verify_and_negotiate()` + `AsyncErrorSender`. **155i**: registry drift fixed — `certificate.verify/lifecycle/history` discoverable
- [x] sweetGrass: **1,636** tests, **v0.8.0**, **G3 E2E validated** — `LedgerClient`, mock loamSpine UDS, 11 E2E ledger tests. Provenance Trio CLOSED in source, 6/7 live on westGate
- [x] petalTongue: **6,605** tests, **topology→runtime manifest**, main.rs split, geometry module
- [x] squirrel: **763** tests, **capability purification**: beardog→security_provider, adapter IPC
- [x] barraCuda: **4,957** tests, **RTX 3090 profiled** (FP64 ~104 TFLOPS, DF64 framing corrected), deep debt sweep (10 batch funcs deprecated to shader path, self-knowledge, `ShaderValidationBackend::SovereignCpu`)
- [x] coralReef: **3,527** tests, **deep debt**: 463 `.expect()` eliminated, PTX macro modernization (-363L net), capability-based env keys
- [x] primalSpring: 197 scenarios, all PASS, calibrated for 13-gate mesh
- [x] skunkBat: spawn-rate anomaly detection, `ConnectivityAnomaly` (9th threat), frame crypto, PUBLIC
- [x] **BTSP 13/13** — all primals shipped ClientHello
- [x] Tower debt: 36 → **1** (grapheneGate HSM only)
- [x] songBird crypto delegation to bearDog: 6/6 seams DONE
- [x] Compositions fixed: `compute` and `nest` include Tower Atomic base primals
- [x] **cellMembrane**: **1,221** tests, **deep debt**: sandbox fail-closed, registry-driven tower status (no hardcoded names), 5 dedup extractions (-135 net lines)
- [x] ~~nestGate: ghost methods `content.repo.*`/`content.mirror.*`~~ — **REMOVED** (capability_registry cleaned)
- [ ] **1 known debt finding**: grapheneGate-readiness (HSM not on eastGate)
- [ ] Chimera Phase 0: library extraction (UNBLOCKED — crypto delegation done)
- [ ] bearDog `crypto.sign_ed25519` returns health stub — blocks Provenance Trio 7/7 live on westGate

## 3. Hardware / Physical Topology

- [x] Mixed 10G + 1G topology LIVE — 10G AOC backbone between houses, MikroTik CRS310 + Omada SX3008F
- [x] sporeGate on R45 → MikroTik — plasma membrane router (NAT/DHCP/DNS/nftables)
- [x] eastGate on MikroTik LAN — code hub, 10G SFP+ direct
- [x] northGate enrolled (Windows 11, RTX 5090, 2.5G ethernet)
- [x] westGate ONLINE — AMD Ryzen 7 5700X / 64GB DDR4 / 2TB NVMe / **ZFS 25.4TB mirrors + 2TB L2ARC SSD, all 5 storage tiers operational**
- [x] ironGate HDD — 14TB + 1TB + 1TB + ~2TB, enclave experiment planned
- [x] blueGate + swiftGate: Windows, house2, 10G backbone proven
- [x] grapheneGate: Android, Tower LIVE (bearDog + songBird + skunkBat)
- [x] 10G AOC trunk CRS310↔Omada proven (blueGate reaches relay via backbone)
- [x] **TOPOLOGY_MAP.toml** has full physical layout with cytoplasm zone model
- [ ] fieldGate OFFLINE (dead CMOS)
- [ ] biomeGate OFFLINE (kernel recovery)
- [ ] Complete port→gate mapping (CRS310 + Omada + TL-SG605S-M2)
- [ ] Document Flint H1 + Flint 2 + Omada WiFi bridge configs

### Gate Fleet — Status Matrix

| Gate | Status | Platform | Mesh IP | Composition | Role |
|------|--------|----------|---------|-------------|------|
| golgiBody | ONLINE | Linux | 10.13.37.1 | thin-relay | Sole depot, enrollment, Forgejo, Drawbridge |
| sporeGate | ONLINE | Linux | 10.13.37.2 | full | Build authority, depot, cascade hub, **peptidoglycan anchor H1** |
| eastGate | ONLINE | Linux | 10.13.37.5 | full | Code hub, overwatch |
| ironGate | ONLINE | Linux | 10.13.37.7 | full | GPU compute, 4x HDD enclave, JupyterHub |
| flockGate | ONLINE | Linux | 10.13.37.6 | full | Nest Atomic validation (after Tower stable) |
| northGate | ONLINE | Windows | 10.13.37.8 | full | RTX 5090. **DAILY DRIVER — DO NOT DEPLOY.** AlphaFold data source (~1TB). |
| grapheneGate | ONLINE | Android | 10.13.37.7 | tower | Beacon seed, mobile Tower |
| strandGate | **NODE ATOMIC VALIDATED** | Linux | 10.13.37.10 | compute (7) | Dual EPYC 7452, RTX 3090, 450 methods, 746 pipelines/sec, sub-ms GPU dispatch |
| westGate | **BROKER LIVE** | Linux | 10.13.37.11 | nest (8) | biomeOS v4.45 COORDINATED, 704 capabilities, 3,216 CAS objects, 20 sockets, Provenance 6/7 |
| blueGate | **NEST 10/10** | Windows | 10.13.37.12 | **full — Tower→Nest→Node** | **G1 DONE. Nest 10/10 (107.6 MB, TCP-only). Built from source. Node Atomic NEXT. Topo H2, sub-builder.** |
| swiftGate | HW READY | Windows | enrolling | tower (3) | Second Windows proof (after blueGate) |
| southGate | HW READY | Linux | enrolling | full (13) | House2 sovereign site |

## 4. K-Derm Layers — Connectivity Fabric (NEW — extracted from incidents + sovereignty)

Three-layer model identified by peptidoglycan failure incident (Wave 155d):

```
┌─────────────────────────────────────────────────────────┐
│  OUTER MEMBRANE — Human access (RustDesk → relay)       │
│  Route: public internet → relay.primals.eco             │
│  Auth: server key + per-gate password                   │
│  Owner: golgiBody RUSTDESK_MEMBRANE chain               │
│  Failure: NAT rate-limit collapse (2 incidents, fixed)  │
├─────────────────────────────────────────────────────────┤
│  PEPTIDOGLYCAN — LAN/HPC topology fabric                │
│  Hardware: Flints, CRS310, Omada, 10G AOC trunk         │
│  Services: NAT (sporeGate), DHCP, DNS (dnsmasq→stubby)  │
│  Scope: 192.168.4.0/22 flat LAN, both houses            │
│  Anchors: sporeGate (H1) + blueGate (H2)               │
│  Failure: dead dnsmasq on sporeGate (fixed)             │
├─────────────────────────────────────────────────────────┤
│  INNER MEMBRANE — Primal communications                 │
│  Route: WireGuard wg0 (10.13.37.x) + songBird :7700    │
│  Auth: capability IPC, TLS, BTSP (13/13)                │
│  Owner: per-primal, coordinated by overwatch             │
│  Status: 9-gate mesh, Tower LIVE on 5+ gates, Nest LIVE  │
└─────────────────────────────────────────────────────────┘
```

### Outer Membrane

- [x] RustDesk relay operational — `relay.primals.eco` → golgiBody
- [x] **RUSTDESK_MEMBRANE iptables chain** — isolated from primal rules
- [x] NAT-aware rate limits: 120 UDP/10s, 60 TCP new/10s
- [x] Port 21114 REJECT with tcp-reset (prevents retry storm poisoning)
- [x] 10 RustDesk peers registered in hbbs DB
- [x] `https://relay.primals.eco` info page active (passphrase-gated bootstrap)
- [x] Cursor rule `.cursor/rules/outer-membrane-rustdesk.mdc` codifies separation
- [x] netfilter-persistent saves (both UDP + TCP fixes survive reboot)
- [ ] LOG before DROP in RUSTDESK_MEMBRANE (visibility for future incidents)
- [ ] House2 Linux gates need RustDesk provisioning (network path proven via blueGate)

### Peptidoglycan

- [x] sporeGate is plasma membrane router — NAT/DHCP/DNS/nftables for house1
- [x] **dnsmasq re-enabled** on sporeGate — sovereign DNS chain: dnsmasq → stubby → upstream
- [x] 10G AOC backbone CRS310↔Omada proven and healthy
- [x] Flat LAN 192.168.4.0/22 — both houses on same broadcast domain
- [x] Anchor model defined: sporeGate (H1) + blueGate (H2)
- [ ] DNS: verify dnsmasq on all Linux gates (sporeGate done, others PENDING)
- [ ] northGate DNS delay diagnosis (likely dead dnsmasq)
- [ ] Port→gate mapping incomplete (need physical audit)
- [ ] WiFi bridge documentation (Flint H1 + Flint 2 configs)
- [ ] Standardized gate provisioning script (DNS + RustDesk + health checks)

### Inner Membrane

- [x] **10-gate WireGuard mesh** — golgi, sporeGate, eastGate, flockGate, ironGate, northGate, grapheneGate, westGate, strandGate, **blueGate** (peer #9)
- [x] Tower Atomic LIVE on 6+ gates — westGate, strandGate, grapheneGate, eastGate, sporeGate, blueGate (Windows)
- [x] LAN peering: Tower 353x LAN (0.45ms vs 158ms WG overlay)
- [x] songBird universal-ipc: UDS/named pipes/abstract sockets/TCP
- [x] BTSP defense-in-depth: 13/13 primals
- [x] **biomeOS neuralAPI**: **27** signal graphs, **composition broker LIVE** (riboCipher + BTSP), 8,564 tests, **704 capabilities on westGate in COORDINATED mode**, E2E routing proven
- [x] **songBird ACME HTTP-01** challenge responder shipped — Phase 1 TLS elimination
- [x] songBird mesh refactor: enrollment crypto + mesh helpers extracted, all files <800L
- [x] sporeGate depot fully refreshed: health 5/11→9/11, 19 binaries, glibc compute trio shipped
- [x] ~~**biomeOS BTSP session propagation**~~ — **SHIPPED** (`48cf9c33`): `send_jsonrpc_async` is BTSP-aware, family-scoped socket trigger handshake
- [x] ~~**biomeOS riboCipher transport**~~ — **SHIPPED** (`48cf9c33`): CLI + core IPC prepend `[0xEC, 0x01]` clear-tier signal
- [ ] songBird probes without riboCipher → sweetGrass log noise every 30s (P1)
- [ ] sporeGate mesh.reachability + rootpulse.ledger still degraded (2/11)
- [ ] Only 2 WG peers active in practice (enrollment pending for house2 gates)
- [x] ~~WireGuard DNS catch-all~~ — **FIXED** (cellMembrane `8d9bb58`): `WgConfig.dns` field + `DNS=` in wg-quick output

## 5. Sovereignty / Trust

- [x] K-Derm three-layer model intact (and now with peptidoglycan documented)
- [x] Forgejo sovereign inner membrane operational (43/43 repos)
- [x] Push mirrors relay to GitHub on commit
- [x] Sovereign outer membrane operational (Caddy TLS)
- [x] S1-S4 sovereignty shadows ALL GRADUATED
- [x] **DNSSEC 3/3 domains complete**
- [x] RustDesk AGPL-3.0 compliant — learn-from-leverage posture
- [x] Sovereign depot auto-build pipeline DELIVERED (4 phases)
- [x] Crash-loop self-recovery LIVE — app breaker + systemd layers
- [x] Tower Atomic EXCEEDS WG (353x LAN, 1.7x WAN)
- [x] 6/6 exploration domains PROVEN LIVE
- [x] Genetic enrollment — two-layer trust
- [x] BTSP defense-in-depth
- [x] Depot provenance — builder=sporeGate, staleness alarm, multi-target
- [x] Crypto delegation — songBird → bearDog, chimera unblocked
- [x] golgiBody sole depot — no local depots, all genomeBins via Caddy TLS
- [ ] Phase 2: Tower cutover — shadow active, chimera design drafted
- [ ] Phase 1: Zola → sporePrint primal pipeline (crates.io a sub-goal)
- [ ] Phase 2: Forgejo → rootPulse — via Nest Atomic (**Nest LIVE on westGate — unblocked after BTSP broker**)
- [ ] `primal.eco` inner membrane separation (P2)

## ~~6. Public Surface / Security~~ → **FOSSILIZED as F12** (Wave 155i)

ALL SECURITY ITEMS RESOLVED. sporePrint impulses are an ongoing publishing cadence, not a security concern — tracked under D11 (Campus). Moved to Fossilized section below.

## 7. Compositions / Products — NUCLEUS Convergence

### Atomic Composition Status

```
NUCLEUS = Tower Atomic + Nest Atomic + Node Atomic + biomeOS orchestration
        = bearDog + songBird + skunkBat           (Tower — security + discovery + defense)
        + nestGate + rhizoCrypt + loamSpine + sweetGrass  (Nest — storage + provenance)
        + toadStool + barraCuda + coralReef        (Node — compute + GPU + shaders)
        + biomeOS                                  (orchestrator — all 13)
```

| Composition | Status | Gates Proven | biomeOS Orchestrated? |
|-------------|--------|--------------|----------------------|
| **Tower Atomic** (3) | LIVE | westGate, strandGate, grapheneGate, eastGate, sporeGate, **blueGate (Windows)** | Signal graphs: 8. Direct IPC: YES. |
| **Nest Atomic** (7+Tower) | LIVE | westGate (ZFS+CAS), **blueGate (Windows, 10/10)** | Signal graphs: 9. Capability routing: YES. Graph execution: P2 (riboCipher). |
| **Node Atomic** (3+Tower) | VALIDATED | strandGate (746 pipelines/sec, sub-ms GPU) | Signal graphs: 3. Not yet orchestrated live. |
| **NUCLEUS** (13) | **NOT YET** | — | All 27 signal graphs defined. E2E orchestration: **NEXT TARGET** |

### What's proven

- [x] footPrint LIVE — 478 TS test cases, FULL NUCLEUS composition
- [x] esotericWebb LIVE — V22, 472 tests, scene binding fixed
- [x] lithoSpore ALL CLEAR — 235 tests, pseudoSpore pipeline matured
- [x] JupyterHub LIVE on ironGate — outer membrane interface
- [x] petalTongue WASM WebGL pipeline shipped + v1.7.0 deployed
- [x] Tower Atomic: 6/6 exploration domains PROVEN, chimera Phase 0 unblocked
- [x] songBird crypto delegation 6/6 COMPLETE — composition model validated
- [x] Composition profiles fixed: `compute` = Tower + node, `nest` = Tower + provenance trio
- [x] `tower-builder` profile created for distributed build mesh nodes
- [x] ~~**biomeOS composition broker**~~ — **SHIPPED** (v4.45): riboCipher framing + BTSP executor + 35 E2E tests
- [x] **biomeOS capability routing E2E**: `content.put` → nestGate, `storage.put` → nestGate, signal graph dispatch routing works
- [x] **westGate COORDINATED mode**: 704 capabilities, 390 translations, 70 signal graphs loaded
- [x] **blueGate Nest 10/10 on Windows** — first multi-composition non-Linux deployment

### Path to NUCLEUS

- [ ] **biomeOS graph executor riboCipher fix** — one-line (`send_ribocipher_jsonrpc_request()`). Blocks orchestrated graph execution across compositions.
- [ ] **biomeOS socket unification** — `biomeos/` vs `membrane/` split causes symlink workarounds
- [ ] **biomeOS socket evaporation** — Neural API restart wipes capabilities, sockets disappear
- [ ] **biomeOS full composition lifecycle** — startup ordering, health gating, composition transitions (Tower→Nest→Node→NUCLEUS) managed by biomeOS, not shell scripts
- [ ] **bearDog `crypto.sign_ed25519`** — real signing (blocks Provenance Trio 7/7, blocks Nest Atomic full E2E)
- [ ] **Node Atomic live on westGate or blueGate** — toadStool + barraCuda + coralReef added to existing Nest deployment
- [ ] **NUCLEUS live on one gate** — all 13 primals under biomeOS orchestration with composition transitions
- [ ] **Chimera Phase 0**: shared library extraction (`libtower.so`) — UNBLOCKED, deferred
- [ ] sporePrint primal pipeline: replace Zola
- [ ] 6 springs pending `validation.json`
- [ ] **Primal CLI flag standardization** — inconsistent bind flags across Nest primals (--bind vs --host vs --bind-address vs --http-port)

## 8. genomeBin / Cross-Platform Deployment

- [x] **5 Tier 1 genomeBin targets**: x86_64-linux-musl, aarch64-linux-musl, x86_64-windows-gnu, aarch64-android, armv7-linux-musl
- [x] **8 Tier 3 PROVEN** exotic architectures
- [x] songBird universal-ipc: UDS/named pipes/abstract sockets/XPC/TCP
- [x] cellMembrane `Platform`: `TargetOs × CpuArch × LinkModel` with `detect()` at compile time
- [x] cellMembrane `InitSystem` dispatch: systemd/launchd/windows-service/bare
- [x] golgiBody sole depot — all genomeBins via `https://depot.primals.eco`
- [x] `bind_mode` and `target` marked transitional in GateProfile
- [x] PowerShell enrollment for Windows gates (`gate-enroll.ps1`)
- [x] Self-registration — gates declare name + composition
- [x] **Startup blurb PROVEN** — westGate: dead checkout → Tower LIVE in 70 min
- [x] HTTPS public pull — zero-auth initial sync for fresh gates
- [x] Shallow roots pattern documented — GitHub clones need fresh Forgejo clone
- [x] `nucleus_launcher.sh` BEARDOG_SOCKET race fixed (westGate I5)
- [x] **strandGate Compute Trio deployed** — Tower + barraCuda + coralReef LIVE
- [x] barraCuda GPU verified on RTX 3090 (source build, SHADER_F64 enabled)
- [x] coralReef 18/18 JSON-RPC dispatch complete, 463 `.expect()` purged, PTX modernized
- [x] ~~P0 glibc~~ — **FIXED**. Depot rebuilt on sporeGate — 16 musl + 3 glibc, BLAKE3 19/19 verified
- [x] J8: Key enrollment portal — **DEPLOYED** (step-ca live at ca.primals.eco)
- [x] Pure Rust across all primals — zero C deps on critical path
- [x] toadStool wgpu cross-platform GPU (DX12/Vulkan/Metal)
- [x] biomeOS platform_native transport on all 27 signal graphs
- [x] biomeOS cross-platform socket templates (named pipes + TCP fallback)
- [x] ~~Windows genomeBins not yet in golgiBody depot~~ — **14 .exe exist but STALE** (all from 07/16, pre-P0-fix). Nest primals work; songBird doesn't.
- [x] ~~**songBird Windows platform gate (P0)**~~ — **FIXED** (`8c0adc8d` + `d9bda555`). TCP fallback + 3 follow-up compile fixes. Linux depot rebuilt; **Windows depot NOT rebuilt.**
- [ ] **Windows depot pipeline** — sporeGate only rebuilds Linux (musl/glibc). No Windows cross-build. blueGate can serve as sub-builder.
- [ ] **No Windows CI gate** — `cargo check --target x86_64-pc-windows-gnu` on Linux CI would catch compile errors before depot
- [ ] macOS genomeBins — check-pass only, no linker for cross-build from Linux
- [ ] `target`/`bind_mode` field removal — primals auto-detect, depot negotiates
- [ ] systemd abstraction for Windows Service / launchd paths (cellMembrane `InitSystem` foundation shipped)

## ~~9. Documentation / Fossil Record~~ → **FOSSILIZED as F11** (Wave 155h)

ALL ITEMS RESOLVED. Moved to Fossilized section below.

## ~~10. Jelly Strings — Deployment Automation~~ → **FOSSILIZED as F13** (Wave 155i)

Manual deployment loops → primal-native automation: **ACHIEVED**. Moved to Fossilized section below.

## 11. Campus / Physical Infrastructure

- [x] Lansing Scuffle vision documented (10 docs, 120K+ in whitePaper/lansingScuffle/)
- [x] Property profile: 1305 S Cedar St, 464K SF, 8 MW, 600-ton HVAC
- [x] Economics model: 5 revenue stages, SBA 504 math, AGPL consulting
- [x] K-Derm zone mapping applied to building floors
- [x] Thermal sovereignty loop designed
- [x] footPrint GeoJSON location added
- [x] sporePrint transplant + credibility audit DONE
- [ ] sporePrint ongoing: 5 impulses for maturity badges (migrated from D6)
- [ ] Building tour / physical access not yet arranged

---

# FOSSILIZED DIMENSIONS

*Fully complete. Not re-checked unless regression signal appears.*

## F1. Glacial Shift (fossilized Wave 150p, completed Wave 137b)

8/8 criteria cleared. No regression through 14+ waves.

## F2. Content-Addressed Convergence (fossilized Wave 150p, completed Wave 143b)

ALL 6 LAYERS COMPLETE. Architectural pattern fully solved.

## F3. Silicon Atheism (fossilized Wave 150p, completed Wave 145a)

Phase 1 (cross-compile) and Phase 2 (transport) COMPLETE.
14/14 primals on all 4 depot architectures. Evolved into Dimension 8 (genomeBin).

## F4. Depot / Build Pipeline (fossilized Wave 150p, completed Wave 150n)

59+ binaries, BLAKE3 + Ed25519 signed, 4 architectures, `require-signed` enforced.
Sovereign CI hooks deployed to 29 repos on golgiBody.

## F5. Cascade Pipeline / Convergence (fossilized Wave 150p, completed Wave 150k)

43/43 repos converged on Forgejo-first. Push mirrors relay to GitHub.

## F6. Tower Atomic Deep Analysis (fossilized Wave 150x, completed Wave 150x)

4-team convergence sprint. Analysis docs and composition map fossilized.

## F7. sporePrint Transplant (fossilized Wave 150x, completed Wave 150x)

Transplant shipped, credibility audit landed. External claim convergence established.

## F8. Tower Atomic Completion + Depot Convergence (fossilized Wave 151a)

Tower Atomic sprint (150v–151a) fully resolved. All P0/P1 items closed.
Tower debt: 36 → 1 (grapheneGate HSM only).

## F9. BTSP Sub-Wave + Publication Strategy (fossilized Wave 151d)

BTSP sub-wave (151b–151d) fully resolved. All 13 primals shipped ClientHello.
Publication strategy: whitePaper gen/ review COMPLETE, JOSS defined.

## F10. Autonomous Gate Enrollment (fossilized Wave 155b)

Zero-operator postPrimordial enrollment fully shipped:

- songBird `mesh.gate_enroll`: 6-phase pipeline
- bearDog FIDO2 enrollment attestation + beacon proximity proof
- cellMembrane Phase 7: gate.enroll → mesh.enroll
- Dynamic IP pool, K-Derm inward escalation, trust tiers
- `gate-enroll.sh` (Linux) + `gate-enroll.ps1` (Windows)
- golgiBody drawbridge: Caddy TLS → `/enroll/*` → songBird
- Self-registration: gates declare name + composition

## F11. Documentation / Fossil Record (fossilized Wave 155h)


All documentation infrastructure complete and current:

- ECOSYSTEM_BLURB.md universal handoff (Tracks A+B converged)
- PRIMAL_REGISTRY.md refreshed — merge conflicts resolved, 15-primal posture
- freshness.toml updated to Wave 155h (38 HEAD SHAs)
- 12 standards wave tags reviewed and bumped (Wave 63–139 → 155h)
- Team startup blurb template issued and validated (westGate + strandGate)
- GLOSSARY.md refreshed (Wave 155b)
- gate-enroll.sh + gate-enroll.ps1 documented
- whitePaper gen/ review COMPLETE
- 42+ docs fossilized in fossilRecord/
- coralForge retired — vestigial name, now helixVision
- Peptidoglycan + Provenance Trio AARs filed
- 17+ handoff docs from Wave 155f–i (code teams + AARs + Nest Atomic)

## F12. Public Surface / Security (fossilized Wave 155i)

All security infrastructure complete and operational:

- 6/6 surfaces healthy (sporeprint, footprint, live, webb, lab, git)
- Security headers deployed (HSTS, CSP, X-Frame-Options)
- fail2ban + rate limiting active
- TLS auto-renewing (ACME)
- Tower pen test: 7 scenarios, all PASS, 0 remaining findings
- sporePrint transplant DONE + credibility audit
- External claim convergence standard issued
- sporePrint impulses (ongoing cadence) tracked under D11 Campus

## F13. Jelly Strings — Deployment Automation (fossilized Wave 155i)

Manual deployment shell loops → primal-native Rust automation: **ACHIEVED**.

- J1–J6: ALL CLOSED (harvest, depot push, service restart, Caddy config, WG peer reg, systemd overrides)
- J7: Legacy detection — one-time P3, deprioritized (does not block any deployment)
- J8: Key enrollment portal — DEPLOYED (step-ca live at ca.primals.eco)

7/8 code-complete + deployed. All deployment automation that was manual is now
primal-native. J7 is a one-time cleanup task that does not affect the dimension's
completeness.

---

**Active**: 8 dimensions (1–5, 7–8, 11)
**Fossilized**: 13 dimensions (F1–F13)
**Summary**: Wave 155i — NUCLEUS convergence wave. **ZERO P0s.** All three atomic
compositions proven: Tower (6 gates), Nest (westGate + blueGate), Node (strandGate).
biomeOS composition broker LIVE (704 caps, COORDINATED, E2E routing). D10 Jelly
Strings FOSSILIZED (F13). **Remaining path to NUCLEUS**: biomeOS full composition
lifecycle (graph executor riboCipher fix, socket unification, startup ordering),
bearDog `crypto.sign_ed25519` (Provenance 7/7), Windows depot pipeline, Node Atomic
added to existing Nest deployments, then NUCLEUS = all 13 under biomeOS orchestration.
8 active dimensions, 13 fossilized. ~63K+ tests. 27 signal graphs. 10 gates (9 Linux/Windows + 1 Android).

---

*Last used*: Wave 155i (Jul 29, 2026)
*Created*: Wave 139a
*First fossilization*: Wave 150p
*Latest fossilization*: Wave 155i (F13 — Jelly Strings)

---

## FILE: `petaltongue/README.md`

# petalTongue @ wateringHole

Cross-primal integration documentation for petalTongue — the **Universal User Interface** primal.

**Updated**: July 11, 2026 (Wave 136b — hardened + converging. All 8 stadial criteria clear. DNSSEC live. K-Derm diderm topology. Manifest-driven handlers. 356 workspace tests)

---

## Integration Status

petalTongue v1.6.6 (18 crates, edition 2024, `deny(unwrap/expect)`):
- 356 workspace tests passing, 0 failures
- `#![forbid(unsafe_code)]` unconditional on all 18 crates + UniBin, zero C dependencies, zero `unsafe` blocks
- Zero `todo!()`, `unimplemented!()`, `TODO`, `FIXME`, `HACK` markers
- Zero `.unwrap()` in production code; one documented `.expect()` for SIGTERM registration
- ~90% line coverage (llvm-cov) — threshold enforced via `llvm-cov.toml`
- All production files under 800 lines (smart domain refactoring)
- **K-Derm diderm topology (Wave 136b)**: `/api/topology-layers` renders 5-layer defense-in-depth with hardening controls. DNSSEC live (keyTag 2371, alg 13).
- **Manifest-driven (Wave 136b)**: sporePrint and physical_topology handlers evolved from hardcoding to runtime `ecosystem_manifest.toml` discovery. Zero hardcoded IPs/test counts.
- **Coordination backend (Wave 132d)**: 6 `/api/coord/*` endpoints reading nestGate CAS manifest. grapheneGate enrolled. DataService → songBird `mesh.peers` wired.
- **Topology cutover (Wave 128)**: Flint H1 is plasma membrane (edge router), sporeGate is ephemeral compute. `MeshNode` gains `lan_ip` for physical LAN addresses.
- UUI glossary module (`petal_tongue_core::uui_glossary`) — canonical terminology for modalities, user types, SAME DAVE
- **Transport (Wave 100+)**: `TRANSPORT_ENDPOINT` env var accepted (sourDough canonical wire format). Supports UDS, TCP, mesh-relay. Supersedes CLI args when launcher-injected.
- **UDS→TCP fallback**: `PRIMAL_BIND_MODE=fallback` enables automatic TCP fallback when UDS bind fails (Android/SELinux).
- JSON-RPC 2.0 REQUIRED (UDS + TCP), tarpc MAY for Rust-to-Rust hot paths, HTTP for browser/external clients
- Capability-based discovery — zero hardcoded primal names in production, 62+ capability constants
- **TRUE PRIMAL compliant**: All cross-primal discovery via capability, not name. BTSP uses role-based env vars (`BTSP_PROVIDER_SOCKET`, `SECURITY_PROVIDER_SOCKET`). Content backend via `CONTENT_BACKEND_SOCKET`. Display via `DISPLAY_BACKEND_SOCKET`. Provenance via `PROVENANCE_TRIO_SOCKET`.
- **Graceful shutdown**: Shared `signal.rs` handles SIGTERM + SIGINT across all long-running modes (web/server/live). Per `DEPLOYMENT_BEHAVIOR_STANDARD.md`.
- **HEALTH-01 compliant** (Wave 110, 2dba46f): Bare `{"method":"health"}` returns enriched `{status, primal, version, uptime_s}`. 13/13 ecosystem parity achieved.
- **riboCipher prefix acceptance** (Wave 113): `[0xEC, 0x01]` prefix stripped on UDS; cellMembrane health probes work transparently.
- **Gate mesh visualization** (Wave 116): `gate-mesh` viz slug renders WireGuard overlay topology with enrollment status, NUCLEUS health per gate, and enrollment animation. `gate.mesh.status` IPC method for runtime queries.
- **Single AEAD** (Wave 116): Entire codebase uses XChaCha20-Poly1305; `aes-gcm` removed.
- **Shared topology data**: `petal_tongue_core::gate_mesh` is single source of truth for mesh state (consumed by viz scene + IPC handler).
- **Feature-gated binary** (Wave 120): `tui` and `ui` are independent default features — web/headless deployments build without ratatui/crossterm/egui. `--no-default-features` produces minimal ecoBin binary.
- **Discovery cache gated** (Wave 120): `petal-tongue-discovery` `cache` feature controls LRU+TTL layer; `lru` not pulled unless explicitly needed.
- **Legacy renderer removed** (Wave 120): 5 pre-SceneGraph draw functions eliminated (508 lines). Grammar of Graphics pipeline is sole rendering path.
- **Hot-path allocation eliminated** (Wave 120): Modality compile returns `&'static str` format tags — zero heap allocations per visualization render.
- **Web dashboard endpoints** (Wave 121): `/api/gate-mesh`, `/viz/{slug}` (SVG/scene-json/animation-json), periodic DataService refresh in web mode.
- **Gate mesh overwatch panel** (Wave 121): Live WireGuard overlay SVG + gate status table in web dashboard.
- **NUCLEUS composition endpoint** (Wave 123): `/api/ecosystem` returns typed NUCLEUS composition (4 atomics, 13 primals) derived from `gate_mesh::NUCLEUS_ATOMICS` constants.
- **NUCLEUS composition panel** (Wave 123): Web dashboard renders color-coded atomic groupings with primal roles and gate assignments.
- **Typed NUCLEUS data** (Wave 123): `NucleusPrimal`, `NucleusAtomic` structs + `TOWER_ATOMIC`, `NODE_ATOMIC`, `NEST_ATOMIC`, `META_ATOMIC` constants. Single source of truth for ecosystem composition.
- **GateEnrollment::as_str()** (Wave 123): Zero-allocation const fn for enrollment status display.
- **ironGate enrolled** (Wave 123): WG IP .7, 12/12 NUCLEUS, 5 gates enrolled, 7 WG links total.
- **`health.liveness` normalized**: Returns exactly `{"status":"alive"}` on both HTTP and IPC.
- **Content backend evolution**: `web_mode/content_backend.rs` replaces nestgate.rs — primal-agnostic `content.resolve` client
- **Enriched `capability.list`**: returns `primal`, `version`, `transport[]`, `methods[]`, `depends_on[]`, `data_bindings`, `geometry_types`
- **Sensory Capability Matrix**: `capabilities.sensory` and `capabilities.sensory.negotiate` IPC methods for input×output negotiation
- **Accessibility adapters**: SwitchInputAdapter, AudioInversePipeline, AgentInputAdapter for motor-impaired, blind, and AI users
- Grammar of Graphics engine with Tufte constraint validation
- **DataBinding auto-compiler**: All 13 DataBinding variants auto-compile to Grammar of Graphics (incl. GenomeTrack, CircularMap)
- **Dashboard layout engine**: Multi-panel grid with domain theming and SVG/description export
- **Client-side WASM rendering (WS-4)**: `petal-tongue-wasm` crate with 14 `#[wasm_bindgen]` exports — grammar, binding, batch, dashboard, scene graph, Tufte validation, threshold coloring, multi-modality. 30 tests. CI `wasm32-unknown-unknown` check.
- Domain-aware rendering (7 palettes: health, physics, ecology, agriculture, measurement, neural, game)
- Multi-modal rendering: egui GUI, ratatui TUI, audio sonification, haptic, braille, description, SVG, headless
- Scene graph with Manim-style animation, modality compilers (SVG, audio, description, terminal)
- **BTSP Phase 3**: Role-based provider socket resolution, typed `BtspHandshakeError` enum, NULL cipher handshake operational
- **Zero-copy textures**: `TextureEntry.data` uses `bytes::Bytes` for refcounted sharing
- **Typed error evolution**: Zero `Result<_, String>` in production — 13 modules evolved to `thiserror` enums
- **`deny.toml` hardened**: `async-trait` banned with wrappers for transitive deps (axum, opentelemetry)
- **Pure Rust audio**: `hound` (WAV gen), `symphonia` (decode), AudioCanvas (`/dev/snd`). No rodio/cpal/ALSA bindings.
- **Wave 102 deep debt sweep**: `.ok()` sites evolved with `inspect_err()` logging, `unwrap_or("")` → `unwrap_or_default()` across 20+ call sites, `content_render` refactored into 3 submodules
- **Wave 107 remaining debt**: Zero `/tmp` hardcoding (all use `LEGACY_TMP_PREFIX`), `RwLock` poison logging on all `.read().ok()` sites, zero TODO/FIXME/HACK markers
- **Zero Clippy warnings**: pedantic + nursery lint set, `#[expect]` with reasons for justified suppressions

### Grammar of Graphics Engine (Implemented)

petalTongue has evolved from fixed widgets to a **Grammar of Graphics** engine.
Any primal can send a grammar expression via JSON-RPC, and petalTongue compiles it
to the best available output. This replaces per-domain ad-hoc rendering with
a single composable pipeline.

**If your primal has data that humans need to understand, read
[VISUALIZATION_INTEGRATION_GUIDE.md](./VISUALIZATION_INTEGRATION_GUIDE.md).**

Implemented capabilities:
- Declarative grammar expressions (data -> variables -> scales -> geometry -> coordinates)
- Tufte constraint system (data-ink ratio, lie factor, chartjunk, accessibility checks)
- barraCuda GPU compute offload via physics bridge (N-body, molecular dynamics)
- Domain color palettes resolved at runtime from grammar `domain` field
- Streaming visualization for real-time data (`visualization.render.stream`)
- 10 geometry types: Point, Line, Bar, Area, Ribbon, Tile, Arc, Heatmap, Contour, Text
- DataBinding payloads: TimeSeries, Distribution, Bar, Gauge, Heatmap, Scatter, Scatter3D, FieldMap, Spectrum, GameScene, Soundscape, GenomeTrack, CircularMap
- AnimationPlayer for sequenced scene graph animations
- Scene bridge renderers for both egui (GUI) and ratatui (TUI)

---

## For Other Primals

### Visualizing Your Data

The simplest way to get petalTongue to visualize your primal's data:

1. Announce your data capabilities via Songbird discovery
2. Expose `{domain}.get` and `{domain}.schema` JSON-RPC methods
3. Send a `visualization.render` request with a grammar expression (or just raw data)

petalTongue handles modality selection, accessibility, Tufte compliance, and
barraCuda compute offload automatically.

See **[VISUALIZATION_INTEGRATION_GUIDE.md](./VISUALIZATION_INTEGRATION_GUIDE.md)** for
the full grammar reference, domain examples, and sovereignty checklist.

### biomeOS Integration

petalTongue discovers biomeOS via:
1. `BIOMEOS_NEURAL_API_SOCKET` env var (explicit override)
2. `$XDG_RUNTIME_DIR/biomeos/neural-api.sock` (XDG standard)
3. `/tmp/biomeos-neural-api.sock` (legacy fallback)

All communication uses JSON-RPC 2.0 over Unix sockets.

### healthSpring Integration

petalTongue renders healthSpring diagnostic data via `DataChannel` and `DataBinding`:
- `TimeSeries` -> Line charts (PK curves, RR tachograms)
- `Distribution` -> Histograms with mean/SD/patient markers
- `Bar` -> Categorical bar charts (microbiome abundances)
- `Gauge` -> Progress bars with normal/warning ranges
- `Heatmap` -> Endocrine correlation matrices
- `Spectrum` -> Frequency-domain analysis (Pan-Tompkins, biosignal)

These map to grammar geometries: `TimeSeries` -> `GeomLine` + `TemporalScale`,
`Distribution` -> `GeomBar` + `StatBin`, `Bar` -> `GeomBar` + `CategoricalScale`,
`Gauge` -> `GeomArc` (polar) or `GeomRect` with annotation,
`Spectrum` -> `GeomArea` + `FrequencyScale`.

Interaction model: callback-based subscriptions (`interaction.subscribe` with
`callback_method` and `event_filter`), plus poll-based fallback.

### ToadStool Integration

petalTongue discovers ToadStool display backend via capability-based discovery.
tarpc binary RPC for high-performance frame transport.

### barraCuda Integration (v0.3.3+ alignment)

petalTongue offloads heavy visualization computation to barraCuda via capability
discovery (`gpu.dispatch`, `science.gpu.dispatch`).
All payloads use `bytes::Bytes` for zero-copy tarpc transfer. Physics bridge
(`petal-tongue-ipc/src/physics_bridge.rs`) provides async IPC client aligned
with barraCuda's `barracuda.compute.dispatch` contract (using `op` field).

**Current status**: CPU Euler fallback only. barraCuda's `compute.dispatch`
currently supports `zeros`, `ones`, `read` ops. `math.physics.nbody` is wired
in petalTongue but not yet in barraCuda's dispatch table. Physics bridge will
use GPU automatically when barraCuda adds physics ops.

**Discovery**: Follows toadStool S139 dual-write pattern:
1. `BARRACUDA_SOCKET` env (explicit)
2. `$XDG_RUNTIME_DIR/ecoPrimals/discovery/` (ecosystem manifest)
3. `$XDG_RUNTIME_DIR/barracuda/` (primal-specific)
4. `/tmp/barracuda.sock` (fallback)

**Precision**: petalTongue is a visualization consumer, not a compute provider.
Precision routing (`Fp64Strategy`, `PrecisionRoutingAdvice`, `FmaPolicy`)
lives in barraCuda/coralReef. petalTongue accepts and displays data at
whatever precision the ecosystem provides.

### coralReef Integration (Phase 10, Iteration 52)

petalTongue does NOT call coralReef directly. Shader compilation flows:
`barraCuda (WGSL) → coralReef (compile) → toadStool (dispatch)`.
petalTongue receives computed results via IPC.

If petalTongue ever needs GPU rendering (GpuCompiler modality), it would go
through barraCuda's `ComputeDispatch::CoralReef` or wgpu, not coralReef directly.

---

## IPC Protocol

petalTongue follows `UNIVERSAL_IPC_STANDARD_V3.md`:
- **Primary**: JSON-RPC 2.0 over Unix sockets
- **Secondary**: tarpc (binary, zero-copy `bytes::Bytes`)
- **Fallback**: HTTP REST (browser/external only)

Socket path: `$XDG_RUNTIME_DIR/petaltongue/petaltongue.sock`
Legacy: `/tmp/petaltongue.sock`

### Visualization JSON-RPC Methods

| Method | Direction | Purpose |
|--------|-----------|---------|
| `visualization.render` | Inbound | Render a grammar expression or raw data |
| `visualization.render.stream` | Inbound | Streaming visualization (append/set_value/replace) |
| `visualization.render.grammar` | Inbound | Render grammar with DataBinding payload |
| `visualization.render.dashboard` | Inbound | Multi-panel dashboard from DataBindings → SVG |
| `visualization.export` | Inbound | Export scene to SVG/JSON/description |
| `visualization.validate` | Inbound | Pre-render Tufte constraint check |
| `visualization.dismiss` | Inbound | Remove a visualization session |
| `visualization.capabilities` | Inbound | Query supported features and geometry types |
| `interaction.subscribe` | Inbound | Subscribe to interaction events (callback or poll) |
| `interaction.poll` | Inbound | Poll pending interaction events |
| `interaction.unsubscribe` | Inbound | Remove interaction subscription |
| `visualization.interact.subscribe` | Inbound | Alias for `interaction.subscribe` (wetSpring compat) |
| `visualization.interact.poll` | Inbound | Alias for `interaction.poll` (wetSpring compat) |
| `visualization.interact.unsubscribe` | Inbound | Alias for `interaction.unsubscribe` (wetSpring compat) |
| `visualization.interact.apply` | Inbound | Programmatic interaction (zoom, filter, select) |
| `visualization.interact.perspectives` | Inbound | List active perspective views |
| `capabilities.sensory` | Inbound | Query sensory capability matrix (runtime discovery or agent) |
| `capabilities.sensory.negotiate` | Inbound | Negotiate tailored matrix with explicit input/output caps |
| `audio.synthesize` | Inbound | On-demand soundscape synthesis (returns WAV metadata) |
| `visualization.render.scene` | Inbound | Direct SceneGraph submission |
| `motor.*` | Outbound | Motor commands to springs |
| `visualization.interact` | Outbound | User interaction event notifications |

---

## Composition Serving (Wave 136b — FP-PARITY)

petalTongue serves **primal compositions** — products that primals compose into.
footPrint is the first composition target (GIS planner, Leaflet/Turf.js frontend).

### How It Works

petalTongue discovers composition bundles at runtime and serves them as SPAs at
`/app/{name}/` with `index.html` fallback. The Express server disappears — Axum
replaces it.

### Configuration

```bash
# Explicit: name=path pairs (comma-separated)
export PETALTONGUE_COMPOSITIONS=footprint=/opt/ecoPrimals/compositions/footprint/dist/client

# Auto-discovery: scan a directory for composition bundles
export PETALTONGUE_COMPOSITIONS_DIR=/opt/ecoPrimals/compositions
# Each subdir with dist/client/ or index.html is mounted at /app/{dir_name}/
```

### Deployment Path (footPrint)

```bash
cd /opt/ecoPrimals/compositions/footprint
npm run build   # produces dist/client/ (219 kB gzipped, 3 chunks)
# petalTongue auto-discovers → serves at /app/footprint/
petaltongue web
```

### Visual Target Parity

12 visual targets defined in `specs/PETALTONGUE_VISUAL_TARGETS.md` (in footPrint repo):
VT-1 (Map Engine), VT-2 (Drawing Tools), VT-3 (Layers), VT-4 (Data Sources),
VT-5 (Measurement), VT-6 (Constraint Solver), VT-7 (Intelligence), VT-8 (Persistence),
VT-9 (Snap/Grid), VT-10 (Status Bar), VT-11 (UI Theme), VT-12 (Agent Bridge).

Phase 1 (current): Serve identical frontend from Axum — petalTongue replaces Express.
Phase 2: Backend sovereignty — nestGate CAS, songBird drawbridge, bearDog TLS.
Phase 3: HPC compute integration — mesh dispatch for DEM/terrain/soil batch processing.

---

## Documents

| Document | Purpose |
|----------|---------|
| [PETALTONGUE_NEEDS_FROM_ECOSYSTEM.md](./PETALTONGUE_NEEDS_FROM_ECOSYSTEM.md) | **What petalTongue needs from other primals** (3D pipeline, audio, GPU ops) |
| [VISUALIZATION_INTEGRATION_GUIDE.md](./VISUALIZATION_INTEGRATION_GUIDE.md) | **How to get petalTongue to visualize your data** (v2.1.0) |
| [SENSORY_CAPABILITY_MATRIX.md](./SENSORY_CAPABILITY_MATRIX.md) | **Input×output capability negotiation protocol** for consumer primals |
| [SCENE_FORMAT_REFERENCE.md](./SCENE_FORMAT_REFERENCE.md) | **GameScene, Soundscape, narrative JSON schemas** for ludoSpring, esotericWebb |
| [SPOREPRINT_EVOLUTION_ROADMAP.md](./SPOREPRINT_EVOLUTION_ROADMAP.md) | Zola → petalTongue migration roadmap, WASM path |
| [PETALTONGUE_SPRING_SCIENCE_MAP.md](./PETALTONGUE_SPRING_SCIENCE_MAP.md) | Spring×science domain mapping |

---

## Standards Compliance

| Standard | Status |
|----------|--------|
| `UNIBIN_ARCHITECTURE_STANDARD.md` | Compliant (1 binary, 7 modes incl. `live`) |
| `ECOBIN_ARCHITECTURE_STANDARD.md` | Compliant (pure Rust, no C deps, no genomeBin yet) |
| `UNIVERSAL_IPC_STANDARD_V3.md` | Compliant (JSON-RPC + tarpc + HTTP fallback) |
| `SEMANTIC_METHOD_NAMING_STANDARD.md` | Compliant (`visualization.*`, `interaction.*` namespaces) |
| `PRIMAL_IPC_PROTOCOL.md` | Compliant |
| `UNIVERSAL_USER_INTERFACE_SPEC` | Compliant — UUI glossary, multi-modal, SAME DAVE |
| License | AGPL-3.0-or-later on all crates |

---

## FILE: `protocols/BTSP_PROTOCOL_STANDARD.md`

# BTSP Protocol Standard

**Version:** 1.0.0
**Date:** April 8, 2026
**Status:** Active — all primals MUST implement when `FAMILY_ID` is set
**Authority:** wateringHole (ecoPrimals Core Standards)
**Derived from:** Secure Socket Architecture plan (primalSpring Phase 26)
**Related:** `PRIMAL_IPC_PROTOCOL.md`, `PRIMAL_SELF_KNOWLEDGE_STANDARD.md`, `CAPABILITY_WIRE_STANDARD.md`, `RIBOCIPHER_TRANSPORT_SIGNAL_STANDARD.md`

> **Note (Wave 111):** BTSP is now signaled via riboCipher transport routing.
> A riboCipher signal byte (0xEC/0xED/0xEE) precedes the BTSP handshake on the wire.
> BTSP protocol types within riboCipher: 0x02 (binary), 0x03 (JSON-line), 0x05 (encrypted resume).
> See `RIBOCIPHER_TRANSPORT_SIGNAL_STANDARD.md` for the routing layer specification.

---

## Abstract

The BearDog Secure Tunnel Protocol (BTSP) defines mandatory authentication
and optional encryption for JSON-RPC communication over Unix domain sockets.
BTSP is the local equivalent of TLS 1.3, designed for intra-machine IPC
between primals within the ecoPrimals ecosystem.

**Core invariant:** Every production connection authenticates via BTSP
handshake first. Plaintext is a negotiated privilege after secure nucleation,
never a default. Hostile until proven otherwise.

---

## Motivation

Local Unix sockets are inherently unencrypted. Any process with filesystem
access to the socket can connect and issue JSON-RPC calls. In a multi-tenant
or multi-family deployment, this means:

- A process from family A can call methods on family B's primals
- A rogue process can impersonate a primal
- No tamper detection on the wire
- No confidentiality for sensitive payloads (crypto keys, health data)

BTSP addresses all four by wrapping JSON-RPC frames in an authenticated,
optionally encrypted tunnel derived from the family seed.

---

## Security Model

### Hostile Until Proven Otherwise

```
connect() → BTSP handshake (mandatory) → authenticated ✓ → negotiate cipher → communicate
connect() → no handshake → REFUSED
```

Every socket connection starts with the BTSP handshake. There are no
exceptions in production. An unauthenticated connection is refused before
any JSON-RPC payload is processed.

### FAMILY_ID as Production Toggle

| Environment | Behavior |
|-------------|----------|
| `FAMILY_ID` set (not `"default"`) | **Production.** BTSP handshake mandatory. Cipher negotiated post-auth. |
| `BIOMEOS_INSECURE=1`, no `FAMILY_ID` | **Development.** No handshake. Raw cleartext JSON-RPC. |
| `FAMILY_ID` set + `BIOMEOS_INSECURE=1` | **Error.** Primal MUST refuse to start. |

---

## Handshake Protocol

The BTSP handshake proves family membership using a challenge-response
derived from the family seed. It runs on every new socket connection
before any JSON-RPC frames are exchanged.

### Key Derivation

```
family_seed (from .family.seed file or FAMILY_SEED env)
    │
    ▼
HKDF-SHA256(ikm=family_seed, salt="btsp-v1", info="handshake")
    │
    ▼
handshake_key (32 bytes)
```

The same derivation pattern used for Dark Forest beacon keys
(`DARK_FOREST_PROTOCOL.md` §Key Derivation).

### Handshake Sequence

```
Client                              Server
  │                                    │
  │──── ClientHello ──────────────────▶│
  │     { version: 1,                  │
  │       client_ephemeral_pub: X25519 }│
  │                                    │
  │◀──── ServerHello ─────────────────│
  │     { version: 1,                  │
  │       server_ephemeral_pub: X25519,│
  │       challenge: random(32) }      │
  │                                    │
  │──── ChallengeResponse ───────────▶│
  │     { response: HMAC-SHA256(       │
  │         key=handshake_key,         │
  │         data=challenge ‖           │
  │              client_ephemeral_pub ‖│
  │              server_ephemeral_pub),│
  │       preferred_cipher: "chacha20" }
  │                                    │
  │     [Server verifies HMAC with     │
  │      own handshake_key derivation] │
  │                                    │
  │◀──── HandshakeComplete ───────────│
  │     { cipher: "chacha20",          │
  │       session_id: random(16) }     │
  │                                    │
  │     [Both derive session keys:     │
  │      X25519(client_eph, server_eph)│
  │      → shared_secret               │
  │      → HKDF(shared_secret,         │
  │             "btsp-session-v1",     │
  │             session_id)            │
  │      → (encrypt_key, decrypt_key)] │
  │                                    │
  │◀═══ Encrypted/Authenticated ══════▶│
```

### Handshake Failure

If the server cannot verify the challenge response (wrong family seed),
it sends:

```json
{ "error": "handshake_failed", "reason": "family_verification" }
```

and immediately closes the connection. No JSON-RPC methods are exposed.

---

## Cipher Suites

After the handshake succeeds, both parties negotiate a cipher suite.
The negotiation is authenticated — forging a downgrade request requires
the family seed.

### BTSP_CHACHA20_POLY1305 (default)

- **Algorithm:** ChaCha20-Poly1305 AEAD
- **Key:** Session key derived from X25519 shared secret via HKDF-SHA256
- **Nonce:** 12-byte counter (incremented per frame, reset per session)
- **AAD:** Frame length (4 bytes, big-endian)
- **Properties:** Confidentiality + integrity + authentication
- **Use case:** Default for all bonds. Zero-knowledge: even biomeOS relay
  cannot read cross-family payloads.

### BTSP_HMAC_PLAIN

- **Algorithm:** HMAC-SHA256 tag appended to each frame
- **Key:** Session key (same derivation as CHACHA20)
- **Properties:** Integrity + authentication (no confidentiality)
- **Use case:** High-throughput same-machine workloads where the OS is
  trusted but tamper detection is desired. GPU tensor pipelines between
  ToadStool and rhizoCrypt in the same Covalent family.

### BTSP_NULL

- **Algorithm:** None. Raw plaintext frames.
- **Properties:** Authentication only (proven during handshake, not per-frame)
- **Constraints:** Both parties must request it AND the BondingPolicy must
  allow it. Only valid for Covalent bonds.
- **Use case:** Maximum throughput for trusted intra-family workloads.
  biomeOS still routes, discovers, and manages the socket. The eco doesn't
  lose visibility because the workload opted for plaintext.

### Cipher Selection Rules

| Bond Type | Minimum Cipher | Negotiable Down To |
|-----------|---------------|-------------------|
| Covalent (`GeneticLineage`) | `BTSP_NULL` | `BTSP_NULL` (all three allowed) |
| Metallic (`Organizational`) | `BTSP_HMAC_PLAIN` | `BTSP_HMAC_PLAIN` |
| Ionic (`Contractual`) | `BTSP_CHACHA20_POLY1305` | None (encrypted only) |
| Weak (`ZeroTrust`) | `BTSP_CHACHA20_POLY1305` | None (encrypted only) |
| OrganoMetalSalt | Per-scope | Covalent core → `BTSP_NULL`, ionic edge → encrypted |

---

## Wire Framing

All BTSP frames use a uniform length-prefixed format regardless of cipher
suite. This means the same parser, tooling, and debugging infrastructure
works for encrypted and plaintext modes.

### Frame Format

```
┌──────────┬──────────────────────────────────────────┐
│ Length(4) │ Payload (Length bytes)                    │
└──────────┴──────────────────────────────────────────┘
```

- **Length:** 4 bytes, big-endian unsigned 32-bit integer.
  Maximum frame size: 16 MiB (`0x01000000`).
- **Payload:** Depends on cipher suite:
  - `BTSP_CHACHA20_POLY1305`: `nonce(12) ‖ ciphertext ‖ tag(16)`
  - `BTSP_HMAC_PLAIN`: `plaintext ‖ hmac(32)`
  - `BTSP_NULL`: `plaintext` (raw JSON-RPC)

### Relationship to Existing Framing

The `PRIMAL_IPC_PROTOCOL.md` v3.1 specifies newline-delimited JSON-RPC
as the canonical wire framing. BTSP wraps this:

- **Without BTSP** (development mode): Newline-delimited JSON-RPC as before.
- **With BTSP** (production mode): Length-prefixed frames containing the
  JSON-RPC message. Each frame holds exactly one JSON-RPC request or
  response. The newline delimiter is no longer needed (length prefix
  provides framing) but MAY be included in the plaintext for backward
  compatibility.

---

## BearDog JSON-RPC Methods

BearDog implements the BTSP crypto primitives as JSON-RPC methods. These
are used by other primals and biomeOS to establish BTSP sessions.

### btsp.session.create

Create a new BTSP session (server-side). Called by a primal's socket
listener when a new connection arrives.

**Params:**
```json
{
  "family_seed_ref": "env:FAMILY_SEED",
  "client_ephemeral_pub": "<base64 X25519 public key>",
  "challenge": "<base64 random 32 bytes>"
}
```

**Result:**
```json
{
  "session_id": "<hex 16 bytes>",
  "server_ephemeral_pub": "<base64 X25519 public key>",
  "handshake_key": "<base64 32 bytes>"
}
```

### btsp.session.verify

Verify a client's challenge response.

**Params:**
```json
{
  "session_id": "<hex>",
  "client_response": "<base64 HMAC-SHA256>",
  "client_ephemeral_pub": "<base64>",
  "server_ephemeral_pub": "<base64>",
  "challenge": "<base64>"
}
```

**Result:**
```json
{
  "verified": true,
  "session_key": "<base64 derived session key>"
}
```

### btsp.negotiate

Negotiate cipher suite for an authenticated session.

**Params:**
```json
{
  "session_id": "<hex>",
  "preferred_cipher": "chacha20_poly1305",
  "bond_type": "Covalent"
}
```

**Result:**
```json
{
  "cipher": "chacha20_poly1305",
  "allowed": true
}
```

### btsp.encrypt / btsp.decrypt

Encrypt or decrypt a BTSP frame using the session key.

**Params (encrypt):**
```json
{
  "session_id": "<hex>",
  "plaintext": "<base64 JSON-RPC message>",
  "frame_counter": 42
}
```

**Result (encrypt):**
```json
{
  "ciphertext": "<base64 nonce ‖ ciphertext ‖ tag>"
}
```

---

## biomeOS Integration

### Intra-NUCLEUS (same family, same machine)

biomeOS is a family member. It holds BTSP session keys derived from the
family seed. When relaying `capability.call`:

1. biomeOS connects to target primal socket
2. BTSP handshake (biomeOS proves family membership)
3. Cipher negotiated per BondingPolicy
4. JSON-RPC forwarded inside BTSP frames
5. biomeOS CAN read method names for routing (trusted within family)

### Cross-NUCLEUS (different family or machine)

biomeOS only nucleates — returns the target socket path and bond type.
The caller connects directly via Tower Atomic:

1. Caller asks biomeOS: `capability.discover(storage)`
2. biomeOS returns: `{ socket_path, bond_type }`
3. Caller connects directly to socket via Tower
4. BTSP handshake with cross-family key exchange
5. biomeOS CANNOT read the payload (zero-knowledge)

---

## Socket Naming Convention (Phase 1)

When `FAMILY_ID` is set, primals MUST create sockets at:

```
$BIOMEOS_SOCKET_DIR/{primal}-{family_id}.sock
```

This aligns with biomeOS `path_builder.rs`:
```rust
let socket_name = format!("{primal_name}-{family_id}.sock");
```

And `list_family_scoped_unix_sockets()` which filters by `-{family_id}.sock`
suffix.

### Per-Primal Socket Naming

| Primal | Development (no FAMILY_ID) | Production (FAMILY_ID set) |
|--------|---------------------------|---------------------------|
| BearDog | `beardog.sock` | `beardog-{fid}.sock` |
| Songbird | `songbird.sock` | `songbird-{fid}.sock` |
| NestGate | `nestgate.sock` | `nestgate-{fid}.sock` |
| ToadStool | `toadstool.sock` | `toadstool-{fid}.sock` |
| rhizoCrypt | `rhizocrypt.sock` | `rhizocrypt-{fid}.sock` |
| loamSpine | `loamspine.sock` (capability: `ledger.sock`, legacy: `permanence.sock`) | `loamspine-{fid}.sock` |
| sweetGrass | `sweetgrass.sock` | `sweetgrass-{fid}.sock` |
| biomeOS | `biomeos.sock` | `biomeos-{fid}.sock` |

---

## Compliance Checklist

```
BTSP_PROTOCOL_STANDARD v1.0 — Audit Checklist

Primal: ___________  Version: ___________  Date: ___________

Socket Naming:
  [ ] Reads FAMILY_ID (or {PRIMAL}_FAMILY_ID) from environment
  [ ] Creates {primal}-{family_id}.sock when FAMILY_ID is set
  [ ] Creates {primal}.sock when FAMILY_ID is not set (development)
  [ ] Refuses to start when both FAMILY_ID and BIOMEOS_INSECURE are set

Handshake (Phase 2+):
  [ ] BTSP handshake runs on every incoming connection when FAMILY_ID is set
  [ ] Challenge-response verifies family membership via HKDF-SHA256
  [ ] Connection refused on handshake failure (no JSON-RPC methods exposed)
  [ ] Ephemeral X25519 keys generated per connection (forward secrecy)

Cipher Negotiation (Phase 2+):
  [ ] Supports BTSP_CHACHA20_POLY1305 (default)
  [ ] Supports BTSP_HMAC_PLAIN (optional)
  [ ] Supports BTSP_NULL (optional, Covalent bonds only)
  [ ] Enforces minimum cipher per BondingPolicy
  [ ] Client preferred_cipher respected when allowed by policy

Framing (Phase 2+):
  [ ] Length-prefixed frames (4-byte big-endian length)
  [ ] Maximum frame size 16 MiB enforced
  [ ] Same frame parser for all cipher suites
```

---

## Implementation Phases

### Phase 1: Socket Naming Alignment (complete)

- All primals honor `FAMILY_ID` for socket naming
- `BIOMEOS_INSECURE` guard prevents conflicting configuration
- biomeOS routing works immediately (already expects this pattern)

### Phase 2: BTSP Handshake (BearDog complete — Wave 31)

- BearDog implements `btsp.session.create`, `btsp.session.verify`, `btsp.session.negotiate`
- BearDog socket listener enforces 4-step handshake (X25519 + HMAC-SHA256 challenge-response) when `FAMILY_ID` is set
- Handshake failure → connection refused
- Consumer primals: wrap socket listeners using BearDog's handshake-as-a-service RPC

### Phase 3: Cipher Negotiation + Encryption (BearDog complete — Wave 31)

- BearDog implements encrypted framing: ChaCha20-Poly1305, HMAC-plain, null cipher suites
- Length-prefixed (4-byte BE) frames replace NDJSON in production mode
- Session key derivation: HKDF-SHA256 from X25519 shared secret with directional keys
- biomeOS Neural API: BTSP client for encrypted relay (pending)
- `BondingPolicy` → cipher suite mapping enforced

### Phase 4: Ecosystem-Wide Secure Nucleation

- All primals implement BTSP
- Cross-NUCLEUS nucleation mode
- `BondingPolicy` enforcement at both handshake and runtime layers

---

## Relationship to Other Standards

| Standard | Relationship |
|----------|-------------|
| `PRIMAL_IPC_PROTOCOL.md` v3.1 | Extended: BTSP wraps the existing JSON-RPC framing with authentication and optional encryption. Newline-delimited framing is preserved in development mode. |
| `PRIMAL_SELF_KNOWLEDGE_STANDARD.md` | Extended: Socket naming convention updated with `FAMILY_ID` → BTSP production mode. |
| `CAPABILITY_WIRE_STANDARD.md` | Complementary: `capabilities.list` and `identity.get` work identically over BTSP — the wire format is unchanged, only the transport is secured. |
| `DARK_FOREST_PROTOCOL.md` | Foundation: BTSP reuses the same key derivation (HKDF-SHA256), cipher (ChaCha20-Poly1305), and challenge-response patterns designed for Dark Forest beacons. |
| `NUCLEUS_ARCHITECTURE.md` | Aligned: BTSP implements the "AES-256-GCM at rest, BTSP on IPC" encryption architecture described in the NUCLEUS spec (ChaCha20-Poly1305 replaces AES for IPC). |

---

**License:** AGPL-3.0-or-later

---

## FILE: `protocols/CAPABILITY_BASED_DISCOVERY_STANDARD.md`

# Capability-Based Discovery Standard

**Version:** 1.3.0
**Date:** May 18, 2026 (updated: connect-probe liveness + dead socket cache + startup cleanup)
**Status:** Active — all primals and springs MUST adopt this

## Principle

> Primals discover and invoke each other by **capability domain**, not by name.
> No primal knows another primal exists. Complexity through coordination, not coupling.

This standard codifies the "loose coupling" pattern that wateringHole has advocated since the beginning. The Neural API provides the routing backbone — primals register capabilities, and consumers discover providers at runtime via semantic capability calls.

## The Problem with Identity-Based Discovery

```rust
// ❌ TIGHT COUPLING — primal knows another primal's identity
let beardog = discover_primal("beardog");
let mut client = PrimalClient::connect(&beardog.socket, "beardog");
client.call("chacha20_poly1305_encrypt", params)?;
```

This fails when:
- BearDog is renamed or replaced by a different security primal
- A spring provides the same capability (e.g. hardware security module)
- The ecosystem evolves to split responsibilities differently
- Multiple primals share a capability domain

## The Capability-Based Alternative

```rust
// ✅ LOOSE COUPLING — primal asks for a capability
let provider = discover_by_capability("security");
let mut client = connect_by_capability("security")?;
client.call("crypto.encrypt", params)?;

// ✅ BEST — use Neural API capability.call for full routing
let result = capability_call("crypto", "encrypt", &args);
```

The caller never knows (or needs to know) that BearDog handles crypto. If tomorrow a `hardware_security_module` primal replaces BearDog for encryption, the caller's code doesn't change.

## Discovery Tiers

### Capability-Based (preferred)

| Tier | Method | Source |
|------|--------|--------|
| 1 | `capability.call` via Neural API | Authoritative — Neural API routes, translates, and forwards |
| 2 | `discover_by_capability(cap)` → Neural API `capability.discover` | Runtime resolution via biomeOS |
| 3 | Capability-named socket (`$XDG_RUNTIME_DIR/biomeos/{domain}.sock`) | Filesystem convention |
| 4 | Socket registry capability scan | Shared registry file |

### Identity-Based (legacy fallback)

| Tier | Method | Source |
|------|--------|--------|
| 1 | `{PRIMAL}_ADDRESS` or `{PRIMAL}_SOCKET` env var | Explicit override |
| 2 | `$XDG_RUNTIME_DIR/biomeos/{primal}.sock` | XDG convention (no family suffix) |
| 3 | `$XDG_RUNTIME_DIR/biomeos/{primal}-{family}.sock` | Family-scoped variant |
| 4 | `{temp_dir}/biomeos/{primal}.sock` | Temp fallback |
| 5 | Primal manifest file | Written on startup |
| 6 | Socket registry by name | Shared registry file |

Identity-based discovery remains available for backward compatibility and for
deploy graphs (which need primal names for binary invocation). But **all runtime
capability invocation** should use the capability-based path.

### Filesystem Socket Requirements (v1.1)

**All discovery below Tier 2 relies on `readdir()` — the ability to list files
in `$XDG_RUNTIME_DIR/biomeos/`.** This means:

1. **Filesystem sockets are REQUIRED on Linux.** Primals MUST create a socket
   file at `$XDG_RUNTIME_DIR/biomeos/<primal>.sock`. Abstract namespace sockets
   (`@primal`) are invisible to the filesystem and MUST NOT be the only socket.

2. **Capability-domain symlinks are RECOMMENDED.** After binding the primal-named
   socket, primals SHOULD create a symlink named after their primary capability
   domain:

   ```
   $XDG_RUNTIME_DIR/biomeos/ai.sock       -> squirrel.sock
   $XDG_RUNTIME_DIR/biomeos/security.sock  -> beardog.sock
   $XDG_RUNTIME_DIR/biomeos/dag.sock       -> rhizocrypt.sock
   ```

   This enables Tier 3 capability-based discovery without Songbird or Neural API.
   Springs performing filesystem probing scan for `{domain}.sock` by iterating
   the known capability domains they require.

3. **Custom socket directories are non-conformant.** Sockets MUST live in
   `$XDG_RUNTIME_DIR/biomeos/`, not in primal-specific directories. A primal
   that only creates `/run/user/1000/myprimal/myprimal.sock` is invisible to
   discovery.

4. **Socket cleanup on shutdown.** Primals MUST remove their socket files
   (and symlinks) on graceful shutdown. Stale socket files pollute discovery.

### Socket Ownership Lifecycle (per lithoSpore R4, May 17 2026)

lithoSpore probes `$XDG_RUNTIME_DIR/ecoPrimals/discovery.sock` for Songbird
discovery but never creates it. This section formalizes socket ownership.

| Socket | Owner (binds) | Consumers (connect) | Created By | Removed By |
|--------|--------------|--------------------:|------------|------------|
| `biomeos/<primal>.sock` | Individual primal process | Any composition consumer | Primal on startup | Primal on shutdown |
| `biomeos/<domain>.sock` | Symlink (created by primal) | Tier 3 capability discovery | Primal on startup | Primal on shutdown |
| `ecoPrimals/discovery.sock` | **songBird** | Any consumer needing `ipc.resolve` | songBird on startup | songBird on shutdown |
| `ecoPrimals/biomeos.sock` | **biomeOS** | Consumers needing `capability.discover` | biomeOS orchestrator | biomeOS orchestrator |

**Rules:**

1. **Only one process binds a socket.** If songBird crashes, no other process
   should attempt to bind `discovery.sock`. Consumers probe and degrade to
   the next discovery tier.

2. **Stale socket detection.** Before connecting, consumers SHOULD send a
   health probe (`health.liveness`). If the socket exists but the probe
   times out (>2s), treat the socket as stale and skip to the next tier.

3. **biomeOS vs songBird scope.** biomeOS owns orchestration-level sockets
   (`capability.discover`, `signal.dispatch`). songBird owns transport-level
   sockets (`ipc.resolve`, `discovery.announce`). Neither creates the other's
   socket.

4. **Crash recovery.** On restart, a primal SHOULD `unlink()` any pre-existing
   socket at its path before `bind()`, to clear stale entries from a prior
   crash. This is already standard for Unix domain sockets.

5. **Connect-probe liveness (May 18, 2026).** File-exists checks (`path.exists()`)
   are insufficient for socket discovery — stale socket files from crashed processes
   remain on disk and pass existence checks. All discovery paths MUST use a connect-probe
   (`UnixStream::connect()` with ≤50ms timeout) to verify a listener exists before
   returning a socket as "discovered". Dead sockets SHOULD be negatively cached for
   the session to avoid repeated ~100ms probe costs per stale socket. Reference:
   `primalSpring::ipc::discover::socket_is_alive()`.

6. **Startup socket directory cleanup (UPSTREAM — biomeOS).** biomeOS SHOULD scan
   its socket directory (`$XDG_RUNTIME_DIR/biomeos/`) on startup and remove any
   `.sock` files without a listening process. Consumer-side probes are defense-in-depth;
   the authoritative fix is server-side cleanup. PID files alongside sockets enable
   instant `kill(pid, 0)` checks without connect overhead.

## Neural API `capability.call` — The Loose Standard

This is the recommended way for primals to invoke capabilities across the ecosystem:

```json
{
  "jsonrpc": "2.0",
  "method": "capability.call",
  "params": {
    "capability": "crypto",
    "operation": "encrypt",
    "args": { "plaintext": "...", "key_id": "default" }
  },
  "id": 1
}
```

**Flow:**
1. Neural API receives `capability.call`
2. Looks up `crypto.encrypt` in `CapabilityTranslationRegistry`
3. Finds provider (e.g. `beardog`) and actual method (e.g. `chacha20_poly1305_encrypt`)
4. Discovers provider socket via `NeuralRouter`
5. Forwards JSON-RPC to the provider
6. Returns result to caller

The caller never sees the primal name, the socket path, or the actual method name.

## Semantic Method Naming

All capabilities follow `{domain}.{operation}[.{variant}]`:

| Semantic Name | Provider | Actual Method |
|---------------|----------|---------------|
| `crypto.encrypt` | beardog | `chacha20_poly1305_encrypt` |
| `discovery.find_primals` | songbird | `ipc.list` |
| `compute.dispatch.submit` | toadstool | `compute_submit` |
| `storage.store` | nestgate | `content_store` |
| `ai.query` | squirrel | `ai.query` |

Primals register their translations via `capability.register`:

```json
{
  "method": "capability.register",
  "params": {
    "primal": "beardog",
    "capability": "crypto",
    "socket": "/run/user/1000/biomeos/beardog-default.sock",
    "semantic_mappings": {
      "encrypt": "chacha20_poly1305_encrypt",
      "decrypt": "chacha20_poly1305_decrypt"
    }
  }
}
```

## What Primals MUST Do

1. **Register capabilities** with the Neural API on startup via `capability.register`
2. **Use `capability.call`** (or `discover_by_capability`) for all cross-primal invocation
3. **Never hardcode** another primal's name, socket path, or method name in production code
4. **Define `by_capability`** in deploy graph nodes so orchestration uses capability discovery
5. **Implement `identity.get`** for sourDough compliance (returns own identity, not others')
6. **Implement `capability.list`** to advertise what you provide

## What Primals SHOULD Do

1. **Prefer `capability.call`** over direct socket connections — it handles translation and routing
2. **Create capability-domain symlinks** (e.g. `security.sock -> beardog.sock`) alongside primal-named sockets, enabling Tier 3 filesystem discovery
3. **Degrade gracefully** when the Neural API is unavailable — fall back to filesystem probing
4. **Use `required_capabilities()`** instead of `required_primals()` for composition validation
5. **Clean up sockets and symlinks** on graceful shutdown to prevent stale discovery results

## Where Primal Names ARE Acceptable

| Context | Why | Example |
|---------|-----|---------|
| Deploy graph `binary` field | Need to invoke a specific binary | `binary = "beardog_primal"` |
| Deploy graph `name` field | Node identity within the graph | `name = "beardog"` |
| `identity.get` response | Self-knowledge, not knowledge of others | `{"id": "primalspring"}` |
| Registration payloads | Telling biomeOS who you are | `"primal": "beardog"` |
| Tests | Testing specific primals intentionally | `probe_primal("beardog")` |
| Logging | Diagnostic information | `info!(primal = "beardog")` |

## Migration Guide

### From identity-based to capability-based:

| Before | After |
|--------|-------|
| `discover_primal("beardog")` | `discover_by_capability("security")` |
| `connect_primal("beardog")` | `connect_by_capability("security")` |
| `probe_primal("beardog")` | `coordination.probe_capability {"capability": "security"}` |
| `AtomicType::required_primals()` | `AtomicType::required_capabilities()` |
| `validate_composition(Tower)` | `validate_composition_by_capability(Tower)` |

### primalSpring reference implementation:

primalSpring v0.3.2 demonstrates the full pattern:
- `ipc/discover.rs`: `discover_by_capability()`, `capability_call()`, `discover_capabilities_for()`
- `ipc/client.rs`: `connect_by_capability()`
- `coordination/mod.rs`: `required_capabilities()`, `validate_composition_by_capability()`
- `deploy.rs`: `probe_graph_node()` uses `by_capability` when present
- Server: `coordination.probe_capability`, `coordination.validate_composition_by_capability`

---

## Compliance Audit Checklist

When auditing a primal for capability-based discovery compliance, check:

### MUST NOT appear in production code (outside tests/logging/deploy graphs):

1. **Hardcoded primal names in discovery**: `discover_primal("beardog")`, `discover_toadstool()`, `SongbirdClient`
2. **Primal-specific env vars for routing**: `TOADSTOOL_PORT`, `BARRACUDA_SOCKET`, `SONGBIRD_SOCKET`
3. **Primal names in method namespaces**: `barracuda.compute.dispatch` (use `compute.dispatch` — the caller doesn't know who provides it)
4. **Primal-named structs for generic roles**: `ToadstoolCompute`, `SongbirdClient` (use `ComputeProvider`, `DiscoveryClient`)
5. **Primal-named socket roles**: `socket_roles::PHYSICS_COMPUTE = "barracuda"` (use capability domain names)
6. **Primal-specific port constants**: `DEFAULT_TOADSTOOL_PORT = 9001`

### MAY appear:

1. **`primal_names` module for logging context** — never in routing
2. **Test fixtures with primal names** — intentional integration tests
3. **Deploy graph `binary`/`name` fields** — needed for binary invocation
4. **Registration payloads** — telling biomeOS who you are

### Audit pattern (grep):

```bash
# Find identity-based routing violations (exclude tests, docs)
rg 'TOADSTOOL_|BARRACUDA_|SONGBIRD_|BEARDOG_|NESTGATE_|SQUIRREL_' \
   --type rust crates/ -g '!**/tests/**' -g '!**/test*'

# Find primal-named structs used for generic roles
rg 'Toadstool|Songbird|BarraCuda|BearDog|NestGate|Squirrel' \
   --type rust crates/ -g '!**/tests/**' | grep -i 'struct\|fn\|impl'

# Find hardcoded primal method namespaces
rg '"barracuda\.|"songbird\.|"toadstool\.|"beardog\.|"nestgate\.|"squirrel\.' \
   --type rust crates/ -g '!**/tests/**'
```

### April 2026 audit findings:

**petalTongue** has correct infrastructure (`BiomeOsBackend`, `CapabilityDiscovery`) but bypasses it:
`SongbirdClient`, `discover_toadstool()`, `TOADSTOOL_PORT/URL`, `BARRACUDA_SOCKET`,
`barracuda.compute.dispatch`, `ToadstoolCompute/Display/AudioProvider`. The `toadstool_v2.rs`
display backend correctly uses `CapabilityDiscovery` — all other cross-primal paths need rewiring.

---

## Related Standards

- **`PRIMAL_SELF_KNOWLEDGE_STANDARD.md` v1.0.0** — Extends this standard
  with concrete code patterns, env var naming conventions, socket naming
  rules, and a phased migration path. If this document says *what* to
  discover, the self-knowledge standard says *how to organize your code*
  to do it.

---

## Version History

### v1.2.0 (April 2, 2026)

**Compliance Audit & Enforcement**

- Added Compliance Audit Checklist with grep patterns for detecting violations
- Upgraded status from SHOULD to MUST — standard maturity warrants mandatory adoption
- April 2026 audit findings: 6/10 primals non-compliant (Songbird, Squirrel, toadStool,
  biomeOS, petalTongue, NestGate). Provenance trio + BearDog fully compliant
- primalSpring Phase 23k audit identified specific violations per primal with counts
- Cross-referenced with `IPC_COMPLIANCE_MATRIX.md` v1.4.0

### v1.1.0 (March 25, 2026)

**Filesystem Socket & Symlink Clarifications**

- Filesystem sockets in `$XDG_RUNTIME_DIR/biomeos/` are REQUIRED on Linux
- Abstract namespace sockets alone are insufficient for discovery
- Capability-domain symlinks formally RECOMMENDED
- Custom socket directories declared non-conformant
- Socket cleanup on shutdown added to SHOULD requirements
- Discovery tier table updated with `{PRIMAL}_ADDRESS` and non-family variants

Driven by esotericWebb's first live composition: squirrel's abstract-only socket
and petaltongue's custom directory were both invisible to filesystem-based
discovery probing.

### v1.0.0 (March 18, 2026)

Initial standard. Established capability-based discovery tiers, Neural API
`capability.call`, semantic method naming integration, and migration guide.

---

## FILE: `protocols/CAPABILITY_DOMAIN_REGISTRY.md`

SPDX-License-Identifier: AGPL-3.0-or-later

# Capability domain registry

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-04-06 |
| **Status** | Canonical |
| **Purpose** | Single source of truth for `by_capability` domain names in deploy graphs across the ecoPrimals ecosystem. |

Deploy graphs use `by_capability` to route discovery at graph execution time. biomeOS resolves each capability domain name to the primal that implements that surface. This registry fixes the canonical string for each primal so springs and graphs do not drift.

**Companion artifact**: `capability_registry.toml` (this directory) is the method-level registry listing every `domain.operation` method, its description, domain, and canonical provider. It is sync-tested against `primalSpring/niche.rs` in CI.

## Canonical domains

| Domain | Primal | Description | Capabilities (examples) |
|--------|--------|-------------|------------------------|
| `orchestration` | biomeOS | Neural API orchestration | `capability.discover`, `graph.deploy`, `graph.list` |
| `security` | BearDog | Cryptographic identity + encryption | `crypto.sign`, `crypto.verify`, `crypto.encrypt` |
| `discovery` | Songbird | Peer discovery + mesh networking | `discovery.find_primals`, `discovery.announce` |
| `storage` | NestGate | Content-addressed persistent storage | `storage.store`, `storage.retrieve`, `storage.list` |
| `compute` | ToadStool | Hardware dispatch (GPU/NPU/CPU) | `compute.dispatch.submit`, `compute.dispatch.execute` |
| `math` | barraCuda | Pure math primitives (WGSL shaders) | `math.linalg`, `math.stats`, `math.spectral` |
| `shader_compile` | coralReef | Sovereign shader compilation | `shader.compile`, `shader.validate` |
| `ai` | Squirrel | AI model bridge | `ai.query`, `ai.list_providers`, `mcp.tools.list` |
| `visualization` | petalTongue | Grammar-based rendering | `visualization.render.dashboard`, `visualization.render.scene` |
| `provenance` | rhizoCrypt | Ephemeral DAG (present time) | `dag.create_session`, `dag.append_event`, `dag.dehydrate` |
| `ledger` | loamSpine | Immutable permanence (past time) | `commit.session`, `commit.entry`, `entry.verify` |
| `attribution` | sweetGrass | Semantic braids (PROV-O) | `braid.create`, `attribution.chain`, `braid.commit`, `provenance.graph` |
| `coordination` | primalSpring | Composition validation + deploy | `coordination.validate_composition`, `composition.nucleus_health` |

## Spring-specific capability domains

Springs define their own domain names for capabilities that belong to a spring, not to a shared primal (for example: `ecology` for wetSpring, `geology` for groundSpring, `physics` for hotSpring, `game` for ludoSpring). Those names are local to the spring; they still must not collide with the canonical table above when the same deploy graph spans multiple surfaces.

## What not to do

- Do not promote internal operation names to domain names when a registered domain already exists (for example, do not use `dag` instead of `provenance` for rhizoCrypt).
- Do not use `provenance` for sweetGrass; that domain is reserved for rhizoCrypt. sweetGrass is `attribution`.
- Do not invent new top-level domain strings in deploy graphs without adding them here first.

## Registering a new domain

1. Add a row to the canonical table in this file with domain, primal, short description, and representative capability IDs.
2. Update any deploy graphs or biomeOS routing tables that should resolve the new domain, and cross-reference this document in review so reviewers can confirm the name is registered.

---

## FILE: `protocols/CAPABILITY_WIRE_STANDARD.md`

# Capability Wire Standard

**Version:** 1.0.0
**Date:** April 8, 2026
**Status:** Active — all primals and springs MUST adopt this
**Authority:** wateringHole (ecoPrimals Core Standards)
**Derived from:** Live validation runs 1–4 (primalSpring Phase 26)
**Related:** `CAPABILITY_BASED_DISCOVERY_STANDARD.md`, `PRIMAL_SELF_KNOWLEDGE_STANDARD.md`, `SEMANTIC_METHOD_NAMING_STANDARD.md`

---

## Abstract

The Capability Wire Standard defines the JSON-RPC response format for primal self-advertisement over IPC. When biomeOS (or any orchestrator) sends `capabilities.list` or `identity.get` to a primal, the response MUST follow this specification. The standard enables automatic capability discovery, composition completeness validation, and AI-assisted routing without hardcoded knowledge of individual primals.

---

## Problem Statement

Prior to this standard, 5 independent wire formats evolved across the ecosystem:

| Format | Shape | Primals |
|--------|-------|---------|
| A | `result: ["method.name", ...]` (bare array) | Songbird |
| B | `result: {capabilities: [...], methods: [...], ...}` | sweetGrass |
| C | `result: {method_info: [{name, ...}]}` | (reference parser) |
| D | `result: {semantic_mappings: {domain: {method: {}}}}` | loamSpine (tests) |
| E | `result: {provided_capabilities: [{type, methods}]}` | BearDog, rhizoCrypt |

biomeOS maintained a 5-format parser to extract method names from each. Rich metadata (cost estimates, operation dependencies, consumed capabilities) was discarded. Method name translation tables introduced errors (GAP-MATRIX-09: `braid.create` mistranslated to `provenance.create_braid`). No primal advertised what it consumed, making composition validation impossible without hardcoded graphs.

---

## Specification

### 1. capabilities.list Response — Required Envelope

Every primal MUST return a JSON-RPC 2.0 response to `capabilities.list` (or the alias `capability.list`) containing AT MINIMUM:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "primal": "<canonical_name>",
    "version": "<semver_or_dev>",
    "methods": [
      "<domain>.<operation>",
      ...
    ]
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `primal` | String | **MUST** | Canonical primal name, lowercase, no spaces (e.g., `rhizocrypt`, `beardog`, `songbird`) |
| `version` | String | **MUST** | SemVer or dev version string (e.g., `0.14.0`, `0.9.0-dev`) |
| `methods` | String[] | **MUST** | Every callable JSON-RPC method, fully qualified with dotted notation (`domain.operation`). This is the primary routing signal for biomeOS. |

The `methods` array MUST contain every method the primal will accept as a JSON-RPC `method` field. If a method name appears in `methods`, the primal MUST NOT return "method not found" when that method is called (parameter validation errors are acceptable).

### 2. Structured Capabilities — Recommended

Primals SHOULD include capability grouping for structured routing and observability:

```json
{
  "result": {
    "primal": "rhizocrypt",
    "version": "0.14.0",
    "methods": ["dag.session.create", "dag.session.list", ...],
    "provided_capabilities": [
      {
        "type": "dag",
        "methods": ["session.create", "session.list", "event.append"],
        "version": "0.14.0",
        "description": "Ephemeral content-addressed DAG engine"
      }
    ]
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `provided_capabilities` | Object[] | SHOULD | Capability groups |
| `provided_capabilities[].type` | String | MUST (if group present) | Domain name (e.g., `dag`, `crypto`, `braid`) |
| `provided_capabilities[].methods` | String[] | MUST (if group present) | Short method names within this domain |
| `provided_capabilities[].version` | String | MAY | Group-level version |
| `provided_capabilities[].description` | String | MAY | Human-readable group description |

When `provided_capabilities` is present, biomeOS registers both the group type name (e.g., `dag`) and qualified names (e.g., `dag.session.create`) in its routing table.

### 3. Dependency & Cost Metadata — Optional

Primals MAY include metadata for AI advisors, composition planners, and billing:

```json
{
  "result": {
    "primal": "sweetgrass",
    "version": "0.7.27",
    "methods": [...],
    "provided_capabilities": [...],
    "consumed_capabilities": ["crypto.sign", "storage.artifact.store", "dag.session.create"],
    "cost_estimates": {
      "braid.create": { "cpu": "low", "latency_ms": 2 },
      "attribution.chain": { "cpu": "high", "latency_ms": 50 }
    },
    "operation_dependencies": {
      "anchoring.anchor": ["braid.create"],
      "attribution.chain": ["braid.create"]
    }
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `consumed_capabilities` | String[] | Methods this primal needs FROM other primals. Enables composition completeness validation. |
| `cost_estimates` | Object | Per-method or per-domain cost hints (`cpu`: low/medium/high, `latency_ms`, `memory_bytes`, `gpu_eligible`). |
| `operation_dependencies` | Object | Method DAG — `{method: [prerequisite_methods]}`. Enables execution planners to sequence operations. |
| `protocol` | String | IPC protocol (e.g., `jsonrpc-2.0`) |
| `transport` | String[] | Available transports (e.g., `["uds", "tcp", "http"]`) |

### 4. identity.get — Recommended

Primals SHOULD implement the `identity.get` JSON-RPC method:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "primal": "rhizocrypt",
    "version": "0.14.0",
    "domain": "dag",
    "license": "AGPL-3.0-or-later"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `primal` | String | MUST | Same as `capabilities.list` `primal` field |
| `version` | String | MUST | Same as `capabilities.list` `version` field |
| `domain` | String | SHOULD | Primary capability domain |
| `license` | String | MAY | SPDX license identifier |

biomeOS probes `identity.get` alongside `capabilities.list` for observability. If absent, biomeOS falls back to socket-name inference.

---

## Method Naming Convention

All method names in the `methods` array MUST follow the **Semantic Method Naming Standard**:

```
<domain>.<operation>
```

- `domain`: lowercase, no dots (e.g., `dag`, `crypto`, `braid`, `health`)
- `operation`: lowercase, underscores for multi-word (e.g., `session.create`, `blake3_hash`)
- Health triad: every primal SHOULD implement `health.liveness`, `health.check`, `health.readiness`
- Meta methods: `capabilities.list`, `identity.get`

---

## biomeOS Parser Behavior

biomeOS v2.93+ reads `capabilities.list` responses with the following priority:

1. `result.methods` (this standard) → use directly, no format detection
2. `result.provided_capabilities` (Format E) → expand `type.method`
3. `result.capabilities` (Format A/B) → use directly if string array
4. `result.method_info` (Format C) → extract `name` fields
5. `result.semantic_mappings` (Format D) → traverse nested keys
6. `result` is bare array (Format A) → use directly

When `result.methods` is present, biomeOS skips format detection entirely. Legacy formats remain supported for backward compatibility but SHOULD be deprecated.

---

## Compliance Levels

### Level 1: Routable (minimum for biomeOS discovery)

- [ ] `capabilities.list` returns a response biomeOS can parse (any format A-E)
- [ ] At least one callable method is advertised
- [ ] `health.liveness` implemented

### Level 2: Standard (target for all primals)

- [ ] All Level 1 requirements
- [ ] `capabilities.list` returns `{primal, version, methods}` envelope
- [ ] `identity.get` implemented
- [ ] All methods in `methods` array are callable (no "method not found" for advertised methods)
- [ ] Method names follow Semantic Method Naming Standard

### Level 3: Composable (target for NUCLEUS-participating primals)

- [ ] All Level 2 requirements
- [ ] `provided_capabilities` grouping included
- [ ] `consumed_capabilities` declared
- [ ] `cost_estimates` for at least high-cost methods
- [ ] `operation_dependencies` for methods with prerequisites

### Current Primal Compliance (April 8, 2026)

| Primal | Level 1 | Level 2 | Level 3 | Gap |
|--------|---------|---------|---------|-----|
| BearDog | ✓ | ✓ | — | L2 complete + signed announcements (SA-01, Wave 45): unified Ed25519 identity, `signed_announcement` in `capabilities.list` and `discover_capabilities`, neural registration attestation |
| Songbird | ✓ | Partial | — | Has `capabilities.methods` token→method map (Wave 123); needs `{primal, version, methods}` envelope, `identity.get` |
| rhizoCrypt | ✓ | ✓ | ✓ | Full L3: `methods`, `consumed_capabilities`, `cost_estimates`, `operation_dependencies` |
| loamSpine | ✓ | ✓ | ✓ | Full L3: `methods` (flat, 37), `identity.get`, `provided_capabilities` (10 groups incl. bond-ledger), `consumed_capabilities`, `cost_estimates`, `operation_dependencies`. Domain symlink `ledger.sock`. Self-knowledge compliant (zero hardcoded primal names, zero biomeOS doc refs in prod). **178** source files, **1,442** tests, **stadial-gate compliant**, `rmp-serde` (bincode advisory eliminated). (April 16, 2026) |
| sweetGrass | ✓ | ✓ | ✓ | Full L3 compliance (April 8, 2026) |
| NestGate | ✓ | ✓ | ✓ | Full L3: `{primal, version, methods}` envelope, `identity.get` with domain/license, `provided_capabilities` (9 groups), `consumed_capabilities`, `protocol`, `transport`. 57 methods advertised. (April 8, 2026) |

---

## Audit Checklist

This checklist is used during primalSpring deep-debt audits and cross-spring evolution reviews:

```
CAPABILITY_WIRE_STANDARD v1.0 — Audit Checklist

Primal: ___________  Version: ___________  Date: ___________

Level 1 (Routable):
  [ ] capabilities.list responds to JSON-RPC probe over UDS
  [ ] Response parseable by biomeOS (any format)
  [ ] health.liveness responds with {status: "alive"} or {alive: true}

Level 2 (Standard):
  [ ] result contains "primal" field (canonical name)
  [ ] result contains "version" field (SemVer)
  [ ] result contains "methods" flat string array
  [ ] Every entry in "methods" is callable (returns result or param error, not method-not-found)
  [ ] Method names follow domain.operation dotted convention
  [ ] identity.get implemented and returns {primal, version}
  [ ] health.liveness, health.check, health.readiness all implemented

Level 3 (Composable):
  [ ] provided_capabilities grouping present with type + methods per group
  [ ] consumed_capabilities lists all cross-primal dependencies
  [ ] cost_estimates present for high-cost methods
  [ ] operation_dependencies present for methods with prerequisites
```

---

## What This Unlocks

### Composition Completeness Validation

With `consumed_capabilities`, biomeOS validates that a deploy graph satisfies all dependencies without hardcoded knowledge:

```
sweetGrass consumes: [crypto.sign, storage.artifact.store, dag.session.create]
BearDog provides:   [crypto.sign, ...]        ✓
NestGate provides:  [storage.artifact.store]   ✓
rhizoCrypt provides:[dag.session.create, ...]  ✓
→ Composition complete
```

### AI-Assisted Routing (Squirrel)

With `cost_estimates` and `operation_dependencies`, Squirrel can plan optimal execution:

```
Goal: anchor a provenance braid
Path: braid.create (low) → anchoring.anchor (high) → proof.generate (medium)
Total: high
```

### Self-Describing Deploy Graphs

A composition's capability surface = union of all `methods` minus all `consumed_capabilities`. No hardcoded `CapabilityTaxonomy` tables needed. biomeOS's translation layer becomes a compatibility shim, not the source of truth.

---

## Parameter Encoding (LD-01)

Binary data in JSON-RPC parameters uses **standard Base64** (RFC 4648 §4,
`+/=` alphabet) unless an explicit per-field encoding hint is provided.

### BearDog Crypto Methods

| Method | `data` / input param | Output | Notes |
|--------|---------------------|--------|-------|
| `crypto.hash` | Base64 | Base64 | BLAKE3; raw UTF-8/hex yields incorrect hashes |
| `crypto.hash_for_cipher` | Base64 | Base64 | Algorithm varies by cipher suite |
| `crypto.hmac` | Base64 (`data` + `key`) | Base64 | HMAC-SHA256 / HMAC-BLAKE3 |
| `crypto.sign_ed25519` | Per-field encoding hints | Per-field | `message_encoding`, `signature_encoding`, `public_key_encoding` (BD-01) |
| `crypto.verify_ed25519` | Per-field encoding hints | — | Same per-field hints as sign |
| `crypto.sign_contract` | JSON (`terms` object) | Hex (hash), Hex (sig, pk) | Canonical JSON → SHA-256 → Ed25519 |
| `crypto.verify_contract` | Hex (all fields) | — | Validates Ed25519 over terms hash |

### Encoding Hints (BD-01, Wave 33)

Ed25519 sign/verify methods accept per-field encoding overrides:
- `"base64"` (default), `"hex"`, `"base64url"`, `"utf8"`, `"none"`

When no hint is present, Base64 is assumed.

**Primals calling `crypto.hash`**: Encode your raw bytes as standard Base64
before sending. The response `hash` field is also Base64.

---

## Signed Capability Announcements (SA-01, Wave 45)

For cross-family federations where socket-level access control (owner-only 0600 permissions) is insufficient, primals MAY include a cryptographic attestation in their capability responses so that Songbird discovery and Neural API can verify advertisement authenticity.

### Wire Format

The `signed_announcement` field appears in `capabilities.list` and `discover_capabilities` responses:

```json
{
  "result": {
    "primal": "beardog",
    "version": "0.9.0",
    "methods": ["crypto.sign_ed25519", ...],
    "signed_announcement": {
      "schema_version": 2,
      "algorithm": "ed25519",
      "public_key": "<hex-encoded Ed25519 verifying key>",
      "signature": "<hex-encoded Ed25519 signature>",
      "signed_fields": ["primal", "version", "methods"]
    }
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | Integer | Canonical message format version (currently `2`) |
| `algorithm` | String | Always `"ed25519"` |
| `public_key` | String | Hex-encoded 32-byte Ed25519 verifying key |
| `signature` | String | Hex-encoded 64-byte Ed25519 signature |
| `signed_fields` | String[] | Which response fields are covered by the signature |

### Canonical Signed Message (schema_version 2)

The signed payload is `SHA-256(primal ":" version ":" sorted_methods)`:

```
message = SHA-256(
    primal_name_bytes
    || b":"
    || version_bytes
    || b":"
    || for each method in sorted(methods):
        method_bytes || b","
)
```

The signature is `Ed25519.sign(signing_key, message)` where `message` is the 32-byte SHA-256 digest. Methods MUST be lexicographically sorted before hashing to ensure determinism regardless of registry enumeration order.

### Identity Key Derivation

Each primal instance derives a single Ed25519 keypair from its runtime identity:

```
seed = SHA-256("primal-identity-key:" || primal_name || ":" || node_id)
signing_key = Ed25519.from_seed(seed)
```

The same key MUST be used for capability announcements, ionic bond signing, contract signing, and neural registration attestation. This gives each primal instance one verifiable public identity.

### Neural API Registration Attestation

When registering via `capability.register`, primals MAY include a `signed_attestation` field in the registration payload. Neural API stores the public key for downstream verification by Songbird and other discovery consumers.

### Verification

Verifiers reconstruct the canonical message from the response's `primal`, `version`, and `methods` fields, compute SHA-256, and verify the Ed25519 signature against the announced `public_key`. If the primal's public key is already known (e.g., from a prior ionic bond or BTSP session), the verifier can confirm identity continuity.

### Implementation Status (April 13, 2026)

| Primal | `signed_announcement` in `capabilities.list` | `signed_announcement` in `discover_capabilities` | Neural Registration Attestation |
|--------|----------------------------------------------|--------------------------------------------------|-------------------------------|
| BearDog | ✓ (schema_version 2, unified key) | ✓ | ✓ |

---

## Transport Security Advertisement (TS-01, Wave 48)

Primals that use BTSP SHOULD include a `transport_security` object in their
`capabilities.list` and `discover_capabilities` responses. This lets consumers
(biomeOS, primalSpring, Songbird) determine whether a BTSP handshake is required
**before** attempting a connection, preventing silent rejection on family-scoped
sockets.

### Wire Format

```json
{
  "transport_security": {
    "btsp_required": true,
    "btsp_version": "2.0",
    "btsp_server_available": true,
    "cleartext_available": false,
    "note": "Family-scoped socket: BTSP handshake required before JSON-RPC."
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `btsp_required` | Boolean | Whether a BTSP handshake is mandatory before JSON-RPC traffic is accepted. `true` on family-scoped sockets, `false` on dev/standalone. |
| `btsp_version` | String | BTSP protocol version supported (e.g., `"2.0"`). |
| `btsp_server_available` | Boolean | Whether this primal exposes `btsp.server.*` methods for handshake-as-a-service. |
| `cleartext_available` | Boolean | Whether plaintext JSON-RPC is accepted. Inverse of `btsp_required` in most cases. |
| `note` | String | Human-readable guidance for debugging. Optional. |

### Rejection Behavior (TS-01 Companion)

When a non-BTSP connection arrives on a family-scoped socket, the primal SHOULD
send a JSON-RPC error response before dropping:

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32600,
    "message": "BTSP handshake required",
    "data": {
      "reason": "This socket is family-scoped and requires a BTSP handshake before JSON-RPC traffic.",
      "btsp_version": "2.0"
    }
  },
  "id": null
}
```

This replaces silent connection drops, giving forwarding proxies (biomeOS) and
test harnesses (primalSpring AtomicHarness) a clear signal to initiate BTSP.

### Implementation Status (April 14, 2026)

| Primal | `transport_security` in response | Rejection JSON-RPC |
|--------|----------------------------------|-------------------|
| BearDog | ✓ (Wave 48) | ✓ (Wave 48) |

---

## Relationship to Other Standards

| Standard | Scope | Relationship |
|----------|-------|-------------|
| **UniBin** | Binary structure (subcommands, `--help`, `--version`) | Prerequisite — primal must be a UniBin |
| **ecoBin** | Build portability (pure Rust, no C deps, musl-static) | Prerequisite — primal must be an ecoBin |
| **genomeBin** | Deployment attestation (checksums, lineage) | Extends — genomeBin MAY embed capability manifest |
| **Capability Wire Standard** (this) | IPC self-advertisement | Complements — defines what the binary says about itself at runtime |
| **Semantic Method Naming** | Method name convention | Referenced — `methods` array follows this convention |

The binary ladder: **UniBin → ecoBin → genomeBin**
The runtime ladder: **health.liveness → capabilities.list (Level 1) → Standard (Level 2) → Composable (Level 3)**

---

## Socket Permissions Convention (SP-01, Wave 259)

All primals SHOULD support a `{PRIMAL}_SOCKET_MODE` environment variable
that sets Unix socket file permissions as an octal string.

### Convention

| Env Var | Default | Description |
|---------|---------|-------------|
| `{PRIMAL}_SOCKET_MODE` | `0600` | Octal permission mode for the primal's UDS |

Where `{PRIMAL}` is the uppercase canonical primal name: `TOADSTOOL_SOCKET_MODE`,
`BARRACUDA_SOCKET_MODE`, `CORALREEF_SOCKET_MODE`, etc.

### Recommended Values

| Deployment | Mode | Rationale |
|------------|------|-----------|
| User-mode (dev) | `0600` | Owner-only, default umask behavior |
| Group-accessible (systemd) | `0660` | biomeOS/primalSpring in same group |
| World-accessible (testing) | `0666` | Never in production |

### Implementation Status

| Primal | `{PRIMAL}_SOCKET_MODE` | Notes |
|--------|------------------------|-------|
| toadStool | **Done** (S259) | First adopter, reads `TOADSTOOL_SOCKET_MODE` |
| barraCuda | Pending | Creates at user umask |
| coralReef | Pending | Creates at user umask |
| Others | Pending | Adopt as socket-based IPC is enabled |

### Implementation Pattern

```rust
fn socket_mode() -> u32 {
    std::env::var("{PRIMAL}_SOCKET_MODE")
        .ok()
        .and_then(|s| u32::from_str_radix(&s, 8).ok())
        .unwrap_or(0o600)
}
```

---

## Graceful Drain Convention (GD-01, Wave 259)

All primals that accept long-running work SHOULD implement `health.drain`
and `health.version` for zero-downtime upgrades.

### health.drain

Stops accepting new work, waits for in-flight dispatches to complete
(with configurable timeout), and returns when the primal is safe to stop.

**Request:**
```json
{"jsonrpc": "2.0", "id": 1, "method": "health.drain", "params": {"timeout_ms": 30000}}
```

**Response (drained):**
```json
{"jsonrpc": "2.0", "id": 1, "result": {"status": "drained", "in_flight": 0, "drained_at": "2026-05-14T11:15:00Z"}}
```

**Response (timeout, still draining):**
```json
{"jsonrpc": "2.0", "id": 1, "result": {"status": "draining", "in_flight": 3, "timeout_ms": 30000}}
```

After returning `"drained"`, the primal rejects all new work with error code
`-32000` ("Service draining") until restarted. This allows upgrade scripts to:
1. `health.drain` → wait for clean stop
2. Replace binary
3. Start new process
4. `health.version` → verify new binary is running

### health.version

Returns build metadata so upgrade scripts can verify the correct binary is
running after restart.

**Request:**
```json
{"jsonrpc": "2.0", "id": 1, "method": "health.version"}
```

**Response:**
```json
{
  "jsonrpc": "2.0", "id": 1,
  "result": {
    "version": "0.2.1",
    "build_hash": "abc123def",
    "session": "S259",
    "compiled_at": "2026-05-12T19:21:00Z",
    "rust_version": "1.87.0"
  }
}
```

### Upgrade Sequence (reference)

```bash
# 1. Drain
echo '{"jsonrpc":"2.0","id":1,"method":"health.drain","params":{"timeout_ms":30000}}' \
  | socat - UNIX-CONNECT:/primal/toadstool

# 2. Stop + swap binary
systemctl stop toadstool
cp /opt/plasmidBin/primals/x86_64-unknown-linux-musl/toadstool /primal/bin/toadstool

# 3. Start + verify
systemctl start toadstool
echo '{"jsonrpc":"2.0","id":1,"method":"health.version"}' \
  | socat - UNIX-CONNECT:/primal/toadstool
```

### Implementation Status

| Primal | health.drain | health.version | Notes |
|--------|-------------|----------------|-------|
| toadStool | Proposed | Proposed | Primary target (long-running compute) |
| barraCuda | Proposed | Proposed | GPU dispatches need drain |
| coralReef | Proposed | Proposed | Shader compilation has in-flight work |
| All others | Optional | Recommended | Short-lived RPC primals can implement trivially |

---

**License**: AGPL-3.0-or-later

---

## FILE: `protocols/CONTEXT_BRAID_STANDARD.md`

# Context Braid Standard — Ephemeral Developer State Weaving

**Authority**: primalSpring coordination
**Status**: Active (Wave 63+)
**Capability domain**: `context.*` (sweetGrass-external WEAVE)
**Lineage**: External analog of sweetGrass braids — weaves developer state across the gate mesh

---

## The Biological Model

sweetGrass braids weave meaning into data — W3C PROV-O signed provenance records that answer "what is the story of this artifact?" They compress rhizoCrypt DAG sessions into permanent, anchored records.

Context braids weave meaning into developer state — ephemeral TOML documents that answer "what is the story of this gate right now?" They compress working context into readable, superseding records that flow across the gate mesh.

```
Internal (data)                        External (developers)
─────────────────                      ─────────────────────
rhizoCrypt DAG sessions   ←→   Impulses (fire, propagate, ack)
sweetGrass braids         ←→   Context braids (weave, sense, clear)
loamSpine ledger          ←→   Git commits (permanent record)
```

### Three-Layer Coordination Model

| Layer | Pattern | Lifetime | Question answered |
|-------|---------|----------|-------------------|
| Git (loamSpine) | Linear, permanent | Forever | "What happened?" |
| Impulses (rhizoCrypt) | DAG, event-driven | Time-bounded, archived | "What should I do?" |
| Context (sweetGrass) | Woven strands, superseding | Ephemeral, auto-decay | "What's the story right now?" |

### Naming Conventions

- **context.weave** (not `set`) — you weave strands together, honoring the braid lineage
- **context.sense** (not `get`) — reading is observation, mirrors `potential.sense`
- **context.clear** (not `delete`) — braids decay/clear, they aren't destroyed

---

## Purpose

Context braids provide short-term memory for developers rotating across LAN and WAN gates. When a developer sits down at a new gate (via RustDesk or physically), `membrane context.sense` tells them what's happening without requiring manual copy-paste of guidance blurbs into each IDE.

Unlike impulses (which are action-oriented and time-bounded), context braids are state-oriented and superseding: each weave overwrites the previous braid for that gate+project, maintaining a living picture rather than an event stream.

---

## Architecture

Context braids live in `infra/wateringHole/context/`. They sync via the same waterFall cascade-pull mechanism as all other wateringHole content. Gates discover current context via `context.sense` after pull; `membrane temporal.cascade` automatically runs `context.clear --expired` after sync to decay stale braids.

```
Developer sits down → pulls wateringHole → context.sense → sees living state
Developer works     → context.weave → updates braid → pushes
Braid expires       → cascade-pull → context.clear --expired → decayed
```

---

## File Location

| Path | Purpose |
|------|---------|
| `context/{gate}/{project-slug}.toml` | One braid per gate+project intersection |

### Directory Structure

```
infra/wateringHole/context/
  flockGate/
    hotspring-compchem.toml
    membrane-shadow.toml
  eastGate/
    hotspring-solver.toml
    wateringhole-cascade.toml
  strandGate/
    wetspring-barracuda.toml
```

---

## Naming Convention

Context braid files use a **project slug** derived from the project path:

```
{project-slug}.toml
```

- **project-slug**: lowercase-kebab from the project's relative path
  - `springs/hotSpring` → `hotspring`
  - `springs/hotSpring/compChem` → `hotspring-compchem`
  - `gardens/cellMembrane` → `cellmembrane`
  - `infra/wateringHole` → `wateringhole`

The parent directory is the gate name. This gives one braid per gate per project — last writer wins.

---

## Schema

```toml
[braid]
gate = "flockGate"
project = "springs/hotSpring"
updated = "2026-05-31T09:30:00-04:00"
updated_by = "flockGate"
ttl_hours = 48
wave = 63

[strands.focus]
summary = "Validating adaptive grid solver against bench suite"
status = "active"          # active | paused | blocked | complete

[strands.breadcrumbs]
trail = [
  "compchem/solver/adaptive.rs — grid refinement loop",
  "bench/validation/run_all.sh — invocation entry point",
]

[strands.next]
actions = [
  "Run bench with --solver=adaptive",
  "Compare against baseline results in fossilRecord",
]

[strands.blockers]
items = []

[strands.notes]
body = """
eastGate pushed solver v0.3. Need to validate before Wave 64.
Using RustDesk from flockGate — bench takes ~20min per run.
"""
```

---

## Braid Header (`[braid]`)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `gate` | string | yes | Gate that wove this braid (auto-populated from identity) |
| `project` | string | yes | Project path relative to workspace root |
| `updated` | ISO-8601 | yes | When this braid was last woven |
| `updated_by` | string | yes | Gate that last updated (same as `gate` on creation) |
| `ttl_hours` | integer | yes | Hours before this braid auto-decays (default: 48) |
| `wave` | integer | yes | Ecosystem wave at time of weaving |

---

## Strand Types

Each braid weaves multiple strands together. All strands are optional except `focus`.

### `[strands.focus]` (required)

What is actively being worked on.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `summary` | string | yes | One-line description of current work |
| `status` | enum | yes | `active` / `paused` / `blocked` / `complete` |

### `[strands.breadcrumbs]`

File paths, functions, entry points another developer would need.

| Field | Type | Description |
|-------|------|-------------|
| `trail` | string[] | Ordered list of relevant code locations |

### `[strands.next]`

Upcoming actions or handoff tasks.

| Field | Type | Description |
|-------|------|-------------|
| `actions` | string[] | What should happen next |

### `[strands.blockers]`

What's preventing progress.

| Field | Type | Description |
|-------|------|-------------|
| `items` | string[] | Current blockers (empty array if none) |

### `[strands.notes]`

Freeform context that doesn't fit other strands.

| Field | Type | Description |
|-------|------|-------------|
| `body` | string | Multi-line freeform text |

---

## Key Differences from Internal sweetGrass Braids

| Aspect | Internal (sweetGrass) | External (context) |
|--------|----------------------|-------------------|
| Signing | Ed25519 via BearDog | None (ephemeral, not auditable) |
| Anchoring | loamSpine permanent | Git history only (disposable) |
| Semantics | Append-only, versioned | Last-writer-wins, superseding |
| Lifetime | Permanent (explicit deletion) | TTL-based auto-decay |
| Format | JSON-LD W3C PROV-O | Human-readable TOML |
| Purpose | Data provenance | Developer coordination |

---

## Lifecycle

1. **Woven**: `membrane context.weave` creates/overwrites the braid file for this gate+project. Auto-populates gate, timestamp, wave. Commits and pushes.
2. **Sensed**: Other gates pull wateringHole; `membrane context.sense` shows current mesh state. Cascade-pull can auto-trigger this.
3. **Superseded**: A new weave for the same gate+project overwrites the previous braid. No history is preserved in the file — git is the fossil record.
4. **Decayed**: `membrane context.clear --expired` removes braids past their TTL. Run automatically during temporal cascade sync.
5. **Cleared**: `membrane context.clear --project <path>` explicitly removes a braid (work complete, no longer relevant).

---

## Membrane CLI Commands

### `context.weave` — Weave a context braid

```
membrane context.weave --project <path> --summary "..." [options]
```

| Flag | Required | Description |
|------|----------|-------------|
| `--project <path>` | yes | Project path (e.g. `springs/hotSpring`) |
| `--summary "..."` | yes | Focus strand summary |
| `--status <status>` | no | Focus status (default: `active`) |
| `--breadcrumbs "f1,f2"` | no | Comma-separated file paths/locations |
| `--next "a1,a2"` | no | Comma-separated next actions |
| `--blockers "b1,b2"` | no | Comma-separated blockers |
| `--notes "..."` | no | Freeform notes body |
| `--ttl <hours>` | no | TTL in hours (default: 48) |

Auto-populates: `gate` (from identity), `updated` (now), `wave` (from freshness.toml).

### `context.sense` — Sense context braids

```
membrane context.sense [--gate <gate>] [--project <path>] [--all]
```

| Flag | Description |
|------|-------------|
| (none) | Show all context braids for the current gate |
| `--gate <gate>` | Show braids from a specific gate |
| `--project <path>` | Filter to a specific project across all gates |
| `--all` | Show all braids across all gates (full mesh state) |

### `context.clear` — Clear/decay context braids

```
membrane context.clear [--project <path>] [--expired]
```

| Flag | Description |
|------|-------------|
| `--project <path>` | Clear this gate's braid for a specific project |
| `--expired` | Clear all braids past their TTL (temporal cascade integration) |

---

## Git Noise Mitigation

Context braids change frequently. To manage git history:

- Commits use a standard prefix: `[context] weave flockGate/hotspring-compchem`
- `context.clear --expired` batches removals: `[context] clear 3 expired braids`
- Future: squash context commits during wave transitions (manual or automated)
- Context files are never force-pushed — standard git flow applies

---

## Cascade-Pull Integration

After wateringHole sync, `membrane temporal.cascade` should:

1. Run `membrane context.clear --expired` to decay stale braids
2. Run `membrane context.sense` to show current mesh state

This mirrors the existing `potential.sense` integration for impulses.

---

## Conventions

- One braid per gate+project. Do not create multiple files for the same intersection.
- Keep summaries under 120 characters.
- Breadcrumbs should be relative to the project root, not absolute paths.
- Next actions should be concrete and actionable (not aspirational).
- Empty arrays are valid — they signal "nothing here" rather than omitting the strand.
- Braids are ephemeral coordination — git history is the permanent record.

---

## Future: IDE/Agent Integration

Context braids are structured enough for agents to consume automatically:

- A Cursor rule or hook could run `membrane context.sense --gate $(hostname)` on session start
- The braid summary surfaces as initial context without manual paste
- This replaces the "toggle between windows and paste a guidance blurb in each IDE" pattern
- Agents can also `context.weave` when completing significant milestones, providing automatic handoff context

---

## FILE: `protocols/ECOSYSTEM_COMMUNICATION_STANDARD.md`

# Ecosystem Communication Standard — Three-Artifact Coordination

**Authority**: Overwatch (see `OVERWATCH_POSITION_STANDARD.md`)
**Status**: Active (Wave 63+, revised Wave 68, Wave 75)
**Prerequisites**: `IMPULSE_POTENTIAL_STANDARD.md`, `CONTEXT_BRAID_STANDARD.md`, `WATERFALL_PATTERN.md`
**Lineage**: Synthesizes inter-gate coordination patterns into a unified standard

---

## The Provenance Trio of Communication

The ecosystem communicates through **three artifacts**, each with a distinct
lifetime, audience, and purpose. They mirror the provenance trio — the same
architecture that makes data trustworthy makes coordination trustworthy.

```
              Permanent ←─────────────────────────────────→ Ephemeral
              Compressed ←────────────────────────────────→ Semantic

   ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
   │  HANDOFFS         │   │  FRAGOs           │   │  BLURBS           │
   │  (loamSpine)      │   │  (rhizoCrypt)     │   │  (sweetGrass)     │
   │                   │   │                   │   │                   │
   │  "What happened   │   │  "What to do      │   │  "Here's the      │
   │   and why"        │   │   next"           │   │   context you need │
   │                   │   │                   │   │   right now"       │
   │  Fossil record    │   │  Work DAG         │   │  Semantic seed     │
   │  Forever          │   │  Time-bounded     │   │  Session-scoped    │
   │  Notebook         │   │  Async/concurrent │   │  Copy-paste ready  │
   └──────────────────┘   └──────────────────┘   └──────────────────┘
         │                       │                       │
         │   All three sync via waterFall temporal cascade   │
         └───────────────────────┴───────────────────────┘
```

---

## Artifact 1: Handoffs (Fossil Record)

**What they are**: Long-form markdown documents that capture a complete sprint,
evolution pass, or decision arc. They live in repos and in `wateringHole/handoffs/`.
They are the **notebook** — the compressed linear history of how a project evolved.

**Provenance analog**: loamSpine. Anchored, immutable, compressed. The permanent
ledger you can always trace back to.

**Audience**: Future teams, future selves, archaeological review. Any team picking
up a primal months later reads its handoffs to understand the full story.

**Lifetime**: Forever. Handoffs are never deleted. Completed waves move to
`handoffs/archive/wave{N}/`.

**Schema**: Markdown, structured by convention:

```markdown
# {PRIMAL}_V{VERSION}_WAVE{N}_{SUMMARY}_{DATE}.md

## Summary
What was accomplished in this sprint/wave.

## Changes
Detailed list of what changed, with file references.

## Test Results
What passed, what's known-debt, what's blocked.

## Next Steps
What the next team should pick up.

## Dependencies
What upstream/downstream primals are affected.
```

**Location**:
- Per-repo: `{repo}/handoffs/` or repo root (varies by primal)
- Centralized: `wateringHole/handoffs/`
- Archive: `wateringHole/handoffs/archive/wave{N}/`

**When to write**: After completing a sprint, wave, or significant evolution pass.
Before handing a primal to another gate or team.

**Current count**: 17 active handoffs + archived waves in `handoffs/archive/`.

---

## Artifact 2: FRAGOs (Work DAG)

**What they are**: Machine-readable TOML impulses that fire action directives
between gates. FRAGOs (Fragmentary Orders) are the primary subtype — short,
actionable, time-bounded amendments to the work plan. They enable **async and
concurrent** coordination: multiple gates work in parallel, FRAGOs keep them
synchronized without blocking.

**Provenance analog**: rhizoCrypt. DAG-structured, event-driven, propagating.
Fire, acknowledge, archive — like a provenance session that branches and merges.

**Audience**: Gate teams currently working. FRAGOs answer "what should I do
next?" and "what changed that affects me?"

**Lifetime**: Active until acknowledged, archived per wave. Active FRAGOs live
in `impulses/active/`, spent ones move to `impulses/archived/`.

**Schema**: TOML per `IMPULSE_POTENTIAL_STANDARD.md`:

```toml
[impulse]
id = "2026-06-02T10-56-eastGate-wave68-subject"
type = "frago"
priority = "medium"
wave = 68

[from]
gate = "eastGate"

[to]
gates = ["southGate"]

[content]
subject = "What needs to happen"
body = """Detailed action items and context."""

[meta]
created = "2026-06-02T10:56:00-04:00"
ack_required = true
```

**Location**: `wateringHole/impulses/active/` and `wateringHole/impulses/archived/`

**Transport**: Git push through waterFall cascade. Auto-discovered via
`membrane potential.sense` after cascade sync.

**When to fire**: When another gate needs to act on your work. Rebuild a binary,
validate a pattern, evolve a dependency, acknowledge a blocker resolution.

**Current count**: 5 active, 7 archived.

---

## Artifact 3: Blurbs (Semantic Seed)

**What they are**: Short, high-semantic-density context prompts designed for
**copy-paste into an AI dev team's IDE**. A blurb is the minimum viable context
that lets a fresh team on any gate understand what they own, what's happened,
and what to do next — without reading the full handoff history.

**Provenance analog**: sweetGrass. Semantic, woven, context-rich. Like a
sweetGrass braid that captures the *meaning* of the current state, not just
the facts.

**Audience**: AI development teams (Cursor agents) at gates. The human operator
copies the blurb and pastes it as the opening prompt in a new session.

**Lifetime**: Session-scoped. A blurb is valid for one sprint context window.
When the work it describes is complete, the blurb is spent. Unlike handoffs,
blurbs are not archived — their content is compressed into the next handoff.

**Schema**: Freeform markdown, optimized for AI comprehension:

```markdown
# {Gate} — {Primal/Project} Context

## You Are
Brief identity: what primal, what gate, what role in the ecosystem.

## Current State
What wave, what's been done, what's the latest version.

## Your Mission
Concrete next steps — what to build, fix, evolve.

## Key Files
Critical paths the agent needs to read first.

## Coordination
Active FRAGOs to check, gates to acknowledge, blockers.
```

**Location**: Not persisted in git. Blurbs are composed by the overwatch position
(see `OVERWATCH_POSITION_STANDARD.md`) or by the operator, then delivered via
copy-paste to the target gate's IDE session.

**When to compose**: When bootstrapping a fresh team on a gate. When a primal
changes ownership between gates. When a new wave begins and teams need
direction.

---

## The Graduation Path: Blurbs → Context Braids

Blurbs are the **pragmatic present**. Context braids are the **automated future**.

Today, blurbs work because:
- They require zero tooling (copy-paste)
- They fit the operator's workflow (compose in one session, paste to another)
- They're high-semantic — an AI agent gets full context in one prompt

Context braids (`CONTEXT_BRAID_STANDARD.md`) are the structured automation of
blurbs. When fully wired, `membrane context.weave` replaces manual blurb
composition, and `membrane context.sense` replaces copy-paste delivery:

| Aspect | Blurb (today) | Context Braid (graduated) |
|--------|---------------|---------------------------|
| Creation | Agent or human composes markdown | `membrane context.weave` writes TOML |
| Delivery | Copy-paste to IDE | `membrane context.sense` on session start |
| Schema | Freeform, convention-based | Structured TOML, machine-validated |
| Discovery | Human relay | Auto-discovered after cascade sync |
| Lifecycle | Manual (expires with session) | TTL auto-decay, superseding |
| Provenance | None (ephemeral) | sweetGrass-anchored on completion |

**The blurb is not deprecated.** It is the pragmatic interface until context
braids are fully reliable. Even after graduation, blurbs remain the fallback —
any team can always be bootstrapped with a paste.

---

## How the Three Artifacts Interact

```
                    ┌─────────────────────────┐
                    │   Operator / Overwatch   │
                    └─────┬───────┬───────┬───┘
                          │       │       │
                   writes │  fires│  composes
                          │       │       │
                    ┌─────▼──┐ ┌──▼────┐ ┌▼───────┐
                    │Handoff │ │ FRAGO │ │ Blurb  │
                    │  .md   │ │ .toml │ │  .md   │
                    └───┬────┘ └───┬───┘ └───┬────┘
                        │         │         │
                    committed  committed  copy-pasted
                    to repo    to wH      to IDE
                        │         │         │
                    ┌───▼─────────▼───┐  ┌──▼──────────┐
                    │  waterFall      │  │ Target gate  │
                    │  temporal       │  │ AI team gets │
                    │  cascade        │  │ instant      │
                    │  (all gates)    │  │ context      │
                    └─────────────────┘  └──────────────┘
```

### The Sprint Cycle

1. **Sprint begins**: Operator composes **blurbs** per gate, paste-delivers to teams
2. **Teams work**: Code evolves, commits accumulate, progress happens
3. **Coordination needed**: Gate fires **FRAGO** when another gate must act
4. **Sprint ends**: Team writes **handoff** — compresses the sprint into fossil record
5. **Wave archived**: FRAGOs move to `archived/`, handoffs move to `archive/wave{N}/`
6. **Next wave**: Operator reads handoffs, composes new blurbs, fires new FRAGOs

### Escalation Ladder

When something needs attention, the artifact type determines urgency:

| Urgency | Artifact | Action |
|---------|----------|--------|
| **Low** — "for the record" | Handoff | Commit to repo. Teams read on next pickup. |
| **Medium** — "do this when you can" | FRAGO (priority: low/medium) | Fire impulse. Team sees on next cascade pull. |
| **High** — "do this now" | FRAGO (priority: high/critical) | Fire impulse + direct blurb delivery. |
| **Immediate** — "context crash" | Blurb | Copy-paste directly to gate IDE. |

---

## The Internal/External Mirror

Each artifact mirrors a provenance trio primal that handles the *internal*
(data) equivalent:

| Internal (data primal) | External (developer artifact) | Shared Pattern |
|------------------------|-------------------------------|----------------|
| loamSpine: anchored linear ledger | Handoffs: compressed sprint history | Permanent, immutable, traceable |
| rhizoCrypt: DAG session events | FRAGOs: async work coordination | Event-driven, branching, acknowledged |
| sweetGrass: semantic content braids | Blurbs: high-context AI prompts | Meaning-rich, woven, session-scoped |

This symmetry is intentional. The ecosystem's internal organs and its external
communication use the same architecture. When a pattern works for data, it
works for people.

---

## Neural API Triad Mapping

The three artifacts map to the Neural API triad:

| Artifact | Triad Domain | Direction | CLI |
|----------|-------------|-----------|-----|
| Handoffs | rootPulse (ACTION) | Create permanent record | `git commit`, `git push` |
| FRAGOs | rootPulse + quorumSignal | Fire + sense | `membrane impulse.post`, `membrane potential.sense` |
| Blurbs | quorumSignal (SENSE) | Observe and bootstrap | `membrane context.weave`, `membrane context.sense` |
| All three | waterFall (SYNC) | Propagate across mesh | `membrane temporal.cascade` |

The triad cycle with all three artifacts:

```
1. Gate A completes work
   ├── git commit + push             (rP: permanent record)
   ├── writes handoff .md            (rP: fossil record of sprint)
   ├── membrane impulse.post         (rP: fire FRAGO to downstream gates)
   └── operator composes blurb       (qS: semantic seed for next team)

2. waterFall propagates              (wF: temporal cascade sync)
   ├── git changes flow to all gates
   ├── handoff .md appears in wateringHole/handoffs/
   └── FRAGO TOML appears in impulses/active/

3. Gate B receives context
   ├── potential.sense → "2 pending FRAGOs"
   ├── operator pastes blurb → AI team has instant context
   └── team reads handoff for deep history if needed
```

---

## When to Use Each Artifact

| Situation | Artifact | Why |
|-----------|----------|-----|
| Completed a sprint/wave | Handoff | Permanent record for future teams |
| Another gate needs to rebuild | FRAGO | Actionable, auto-discovered on cascade |
| Requesting validation | FRAGO (AUDIT) | Directed, needs acknowledgment |
| Bootstrapping a fresh AI team | Blurb | High-context, copy-paste ready |
| Primal changing gate ownership | Handoff + Blurb | History (handoff) + immediate context (blurb) |
| Architecture decision made | Handoff + commit | Permanent, lives in handoffs/ |
| "Pull wateringHole and rebuild" | FRAGO | Replaces a Slack message |
| "Don't touch X, mid-sprint" | FRAGO (SYNC) | Coordination boundary |

### Anti-Patterns

- **Don't use FRAGOs for permanent decisions** — write a handoff, commit to git
- **Don't use blurbs for action directives** — fire a FRAGO (blurbs are context, not orders)
- **Don't use handoffs for urgent coordination** — fire a FRAGO (handoffs are read later)
- **Don't rely on blurbs for provenance** — they vanish with the session; the handoff is the record
- **Don't skip the blurb** — a FRAGO tells a team *what to do* but not *who they are*; the blurb provides identity and context

---

## VPS Mediator Pattern (Phase 4 Inversion — Wave 63+)

All three artifacts propagate through the VPS as sovereign mediator:

```
Gate ──covalent──→ golgiBody-inner (cis: Forgejo)
                       │ metallic
                   peptidoglycan (structural: sync + impulse cascade)
                       │ ionic
                   golgiBody-ext (trans: ships to extracellular)
                       │ weak
                   GitHub (external linear ledger)
```

**Push Target**: Gates push only to Forgejo (`push_target = "forgejo"` in manifest).
The K-Derm diderm relay chain propagates through all three VPS nodes with proper
bond-type degradation. Gates no longer need GitHub SSH keys.

**GitHub as External Linear Ledger**: GitHub serves the same conceptual role as
loamSpine → BTC/ETH stamping: an external, immutable, publicly-discoverable
record of ecosystem evolution. It is a trailing mirror, not the source of truth.

| Operation | Target | Bond | Mechanism |
|-----------|--------|------|-----------|
| `git push` | Forgejo (inner) | Covalent | Gate SSH to golgiBody |
| Sync relay | peptidoglycan | Metallic | Post-receive webhook → `pepti-sync-relay.sh` |
| GitHub mirror | GitHub | Weak | `ext-github-push.sh` on golgiBody-ext |
| Impulse relay | Mesh | — | peptidoglycan `potential.sense` → songbird |
| Context sync | All gates | — | waterFall temporal cascade |

See `WATERFALL_PATTERN.md` Phase 4, `hooks/forgejo/README.md` for relay chain,
and `graphs/waterfall_publish.toml` for cascade specification.

---

## Primal Graduation Path

Today, all three artifacts are implemented as direct filesystem operations in
`membrane-shadow`. As primals graduate, the operations compose through biomeOS graphs:

| Artifact | Shadow (today) | Graduated (future) |
|----------|----------------|---------------------|
| FRAGOs | `membrane impulse.post` writes TOML, git pushes | bearDog signs, rhizoCrypt records DAG event, songbird relays, nestGate stores |
| Blurbs | operator copy-paste | `membrane context.weave` writes TOML, `context.sense` auto-delivers |
| Handoffs | manual markdown in repo | sweetGrass validates, loamSpine anchors, sporePrint certifies |
| Git | `git commit/push` | rootPulse graph: dehydrate → sign → store → commit → attribute |

The graduation graphs are defined in:
- `infra/wateringHole/graphs/impulse_post_signed.toml`
- `infra/wateringHole/graphs/context_weave_anchored.toml`
- `infra/wateringHole/graphs/waterfall_publish.toml` (full cascade composition)

The NeuralBridge in `membrane-shadow` (feature-gated) already attempts to route
through biomeOS before falling back to shadow implementations.

---

## K-NOME Interaction

The three-artifact model formalizes the K-NOME programming pattern for multi-gate
development:

**Before** (manual K-NOME):
1. Human composes a long context blurb
2. Pastes it into a fresh IDE chat
3. AI reads specs, docs, wateringHole standards
4. AI works, produces results
5. Human copies results, pastes to next gate

**Current** (hybrid K-NOME):
1. Overwatch fires FRAGOs with action directives (async, all gates)
2. Overwatch composes blurbs with semantic context (per gate)
3. Human pastes blurb to target gate IDE → AI has instant identity + mission
4. AI reads FRAGOs via cascade → knows what to do
5. AI reads handoffs for deep history → knows why
6. AI works, produces handoff, overwatch fires completion FRAGO
7. waterFall propagates everything to all gates

**Future** (automated K-NOME):
1. `membrane impulse.post` fires FRAGOs with action directives
2. `membrane context.weave` writes structured braids (replaces blurbs)
3. AI on receiving gate runs `context.sense` → instant context (no paste)
4. AI reads impulses via `potential.sense` → knows what to do
5. AI works, weaves its own context, fires completion impulse
6. waterFall propagates everything to all gates

---

## Standards Reference

| Standard | File | Domain |
|----------|------|--------|
| This document | `ECOSYSTEM_COMMUNICATION_STANDARD.md` | Unified coordination model |
| Overwatch Position | `OVERWATCH_POSITION_STANDARD.md` | Floating coordination role definition |
| Impulse/Potential | `IMPULSE_POTENTIAL_STANDARD.md` | FRAGOs: event-driven work DAG |
| Context Braids | `CONTEXT_BRAID_STANDARD.md` | Blurbs → braids graduation target |
| WaterFall Pattern | `WATERFALL_PATTERN.md` | Transport: temporal sync across mesh |
| Semantic Methods | `SEMANTIC_METHOD_NAMING_STANDARD.md` | Method naming conventions |
| Capability Registry | `primalSpring/config/capability_registry.toml` | Registered capabilities |
| Gate Coordination | `GATE_TEAM_COORDINATION_MATRIX.md` | Gate/team/hardware/project SSOT |
| Gate Ownership | `GATE_SPRING_OWNERSHIP.md` | Canonical spring routing |

---

## Changelog

| Wave | Change |
|------|--------|
| 75 | Overwatch position formalized as separate standard (`OVERWATCH_POSITION_STANDARD.md`). Authority updated from "primalSpring coordination" to "Overwatch" — reflecting the floating, sovereign-enabled nature of the role. |
| 68 | Revised: three artifacts (Handoffs, FRAGOs, Blurbs) formally codified with provenance trio mapping. Blurbs recognized as pragmatic sweetGrass layer with graduation path to context braids. Escalation ladder, sprint cycle, anti-patterns updated. |
| 63 | Initial: three-layer model (commits, impulses, context braids) synthesized from ecosystem practice. |

---

*"Three artifacts, three lifetimes, three audiences — one water.
The handoff remembers. The FRAGO directs. The blurb ignites."*

---

## FILE: `protocols/IMPULSE_POTENTIAL_STANDARD.md`

# Impulse/Potential Standard — Inter-Gate Coordination

**Authority**: primalSpring coordination
**Status**: Active (Wave 63+)
**Capability domains**: `impulse.*` (rootPulse ACTION), `potential.*` (quorumSignal SENSE)
**Supersedes**: `SIGNAL_FRAGO_STANDARD.md` / `signal.*` commands (deprecated, aliases remain for one wave)

---

## The Biological Model

Communication across cell membranes happens via **action potentials**:

- **Impulse** — the discrete electrochemical event that fires and propagates. A gate creates an impulse (action), it travels through the membrane to other gates. Directional, time-bounded, carries a payload.
- **Potential** — the measurable voltage gradient across the membrane. You can measure resting potential before firing, sense what's pending after propagation. Pure observation.
- **Propagation** — the impulse travels along the membrane via ion channels (git push through SSH/Forgejo). The membrane itself is the transport medium.

### Triad Mapping

| Command | Domain | Metaphor |
|---------|--------|----------|
| `impulse.post` | rootPulse (ACTION) | Fire an action potential |
| `impulse.ack` | rootPulse + waterFall (ACTION+SYNC) | Receptor binding + propagate |
| `impulse.archive` | waterFall (SYNC) | Discharge spent impulses |
| `potential.sense` | quorumSignal (SENSE) | Measure membrane potential |
| `potential.check` | quorumSignal (SENSE) | Gradient health across mesh |

---

## Purpose

Impulses are machine-readable, git-mediated messages that ride alongside code pushes. They enable teams working across multiple gates to communicate state changes, action requests, and coordination directives without relying on ad-hoc handoff blurbs or out-of-band communication.

A **FRAGO** (Fragmentary Order) is an impulse subtype that amends an existing directive — short, actionable, and time-bounded.

---

## Architecture

Impulses live in `infra/wateringHole/impulses/`. They sync via the same waterFall cascade-pull mechanism as all other wateringHole content. Gates discover pending impulses via `potential.sense` on their next pull; `membrane temporal.cascade` automatically runs `potential.sense` after sync.

```
Team pushes code → fires impulse → commits to wateringHole → pushes
Other gates pull wateringHole → potential.sense → see pending impulses
```

---

## File Location

| Path | Purpose |
|------|---------|
| `impulses/active/*.toml` | Active impulses awaiting acknowledgment or expiry |
| `impulses/archive/wave{N}/*.toml` | Discharged impulses (completed, expired, or superseded) |

---

## Naming Convention

```
{ISO-timestamp}_{from-gate}__{slug}.toml
```

- **timestamp**: `YYYY-MM-DDTHH-MM` (colons replaced with dashes for filesystem safety)
- **from-gate**: the originating gate identity
- **slug**: lowercase-kebab summary (max 50 chars)

Example: `2026-06-01T14-30_eastGate__compchem-solver-ready.toml`

---

## Schema

```toml
[impulse]
id = "2026-06-01T14-30-eastGate-compchem-solver-ready"
type = "frago"           # frago | status | request | announce
priority = "routine"     # routine | priority | flash
wave = 63

[from]
gate = "eastGate"
team = "hotSpring"
project = "springs/hotSpring"
ref = "f048484"          # commit SHA — rootPulse DAG provenance (auto-populated)

[to]
gates = ["strandGate"]   # target gates, or ["*"] for all gates
teams = ["hotSpring"]    # target teams (informational filtering)

[content]
subject = "CompChem solver v0.3 ready for bench validation"
body = """
New adaptive grid solver merged to main.
Run bench suite with --solver=adaptive flag.
Blocking: strandGate validation before Wave 64 close.
"""

[meta]
created = "2026-06-01T14:30:00-04:00"
expires = "2026-06-03T00:00:00-04:00"
ack_required = true
```

The `[from].ref` field is auto-populated by `impulse.post` from the project repo's HEAD SHA, providing rootPulse DAG traceability.

---

## Impulse Types

| Type | Purpose | Typical TTL |
|------|---------|-------------|
| `frago` | Amends a standing order — action required | 24-48h |
| `status` | Informational state update — no action required | 12-24h |
| `request` | Asks for something from target gate(s) | Until fulfilled |
| `announce` | Broadcast to all gates — ecosystem-wide notice | Until next wave |
| `sync` | Divergence detected — merge coordination needed | 48h |

### SYNC Impulses (Wave 66+)

SYNC impulses are auto-fired by `membrane temporal.cascade` when a repo enters
`diverge` state (controlled by `diverge_impulse = true` in `ecosystem_manifest.toml`).
They carry structured payload enabling agentic or human resolution:

```toml
[impulse]
type = "sync"
priority = "priority"
subject = "DIVERGE: plasmidBin — origin(+2) vs forgejo(+0)"
ttl_hours = 48

[from]
gate = "eastGate"
ref = "71208e9"

[to]
gates = ["*"]

[content]
subject = "DIVERGE: plasmidBin — origin(+2) vs forgejo(+0)"
body = "Cascade detected non-ff divergence. See payload for resolution context."

[payload]
repo = "infra/plasmidBin"
diverge_type = "origin_ahead"
merge_base = "a3efdef"

[payload.remotes]
origin = "36f5b39"
forgejo = "a3efdef"

[payload.ahead]
origin = 2
forgejo = 0

[payload.policy]
repo_policy = "merge-ff"
suggested_action = "pull_origin_push_forgejo"
```

Per-repo `divergence_policy` in the manifest controls resolution behavior:

| Policy | Behavior |
|--------|----------|
| `flag` | Fire impulse + print diverge warning (default) |
| `merge-ff` | Auto-resolve if one side is a strict ancestor; impulse on non-ff |
| `merge-rebase` | Auto-rebase if no content conflicts; impulse on conflict |
| `impulse-only` | Fire impulse, never auto-resolve |
| `agentic` | Full pipeline: impulse → provenance-recorded resolution (Phase 2+) |

---

## Priority Levels

| Priority | Meaning | Expected response |
|----------|---------|-------------------|
| `routine` | Normal workflow coordination | Next work session |
| `priority` | Time-sensitive, blocking other work | Same day |
| `flash` | Critical — requires immediate attention | ASAP |

---

## Lifecycle

1. **Fired**: `membrane impulse.post` generates file in `impulses/active/`, auto-populates `[from].ref`, commits, pushes.
2. **Sensed**: Target gates pull wateringHole; `membrane potential.sense` shows pending impulses. `membrane temporal.cascade` auto-triggers this after sync.
3. **Acknowledged**: `membrane impulse.ack <id>` appends `[[acks]]` entry, commits, pushes (receptor binding).
4. **Discharged**: `membrane impulse.archive` moves expired or fully-acked impulses to `impulses/archive/wave{N}/`.
5. **Health**: `membrane potential.check` reports gradient health — expired unacked, TTL violations, volume per wave.

### Acknowledgment Format

Appended to the impulse file by the receiving gate:

```toml
[[acks]]
gate = "strandGate"
timestamp = "2026-06-01T15:02:00-04:00"
note = "Bench suite queued, results by 21:00"
```

Multiple gates can ack independently; each appends its own `[[acks]]` entry.

---

## Membrane CLI Commands

### Impulse — rootPulse ACTION

| Command | Action |
|---------|--------|
| `membrane impulse.post --to <gate> --type <type> --subject "..." [--body "..."] [--project <path>]` | Fire an impulse (auto-populates ref) |
| `membrane impulse.ack <id> [--note "..."]` | Acknowledge (receptor bind) |
| `membrane impulse.archive` | Discharge expired/fully-acked impulses |

### Potential — quorumSignal SENSE

| Command | Action |
|---------|--------|
| `membrane potential.sense [--all]` | Measure pending potential for this gate |
| `membrane potential.sense --count` | Lightweight integer count (temporal cascade integration) |
| `membrane potential.check` | Gradient health across the mesh |

---

## Backward Compatibility

Old `signal.*` commands remain as deprecated aliases for one wave:

```
$ membrane signal.post ...
DEPRECATED: signal.post is now impulse.post (see IMPULSE_POTENTIAL_STANDARD.md)
```

The parser reads both `[signal]` and `[impulse]` TOML table names, so existing signal files work without migration.

---

## Conventions

- One impulse per file. Do not batch unrelated messages.
- Keep subjects under 80 characters.
- Body is optional for simple status updates.
- `ref` is auto-populated — do not set manually unless overriding.
- Impulses are never deleted — they are discharged to preserve the coordination fossil record.
- Ack notes should be brief (what you're doing, ETA if applicable).

---

## Phase 2: Near-Realtime Delivery (Future)

When Forgejo webhooks are deployed on wateringHole:

1. Forgejo post-receive detects new files in `impulses/active/`
2. Webhook POSTs to peptidoglycan `impulse-relay` service
3. `impulse-relay` broadcasts via Songbird `mesh.publish` to subscribed gates
4. Subscribing gates' temporal cascade fires immediately, triggers `potential.sense`

No schema changes required — impulse files remain the durable store regardless of delivery mechanism.

---

## FILE: `protocols/PROVENANCE_TRIO_INTEGRATION_GUIDE.md`

# Provenance Trio Integration Guide

**Version:** 2.0.0
**Date:** May 13, 2026 (wire names reconciled per GAP-36)
**Audience:** Springs, gardens, and any composition wiring rhizoCrypt + loamSpine + sweetGrass
**Status:** Active
**License:** AGPL-3.0-or-later

---

## Purpose

The provenance trio — **rhizoCrypt** (ephemeral DAG), **loamSpine**
(immutable ledger), and **sweetGrass** (semantic attribution) — is the most
referenced subsystem across all springs. As of April 27, 2026, PG-52 (UDS empty
responses) is **resolved upstream** — all three primals now respond to JSON-RPC
over UDS after rebuilds from current source.

This document provides the operational integration guide: how to wire the trio
into a composition, what to expect from each primal, known failure modes, and
workarounds. It consolidates and promotes the patterns from
`fossilRecord/consolidated-apr2026/SCYBORG_PROVENANCE_TRIO_GUIDANCE.md` and
the cross-spring convergence analysis.

For the licensing framework built on the trio, see
`fossilRecord/consolidated-apr2026/SCYBORG_PROVENANCE_TRIO_GUIDANCE.md`.

---

## The Three Roles

```
Working Memory          Permanent Record          Attribution
┌──────────┐           ┌──────────┐           ┌──────────┐
│rhizoCrypt│──dehydrate──▶│loamSpine │◀──certify───│sweetGrass│
│          │           │          │           │          │
│ DAG      │           │ Ledger   │           │ Braids   │
│ Sessions │           │ Certs    │           │ W3C PROV │
│ Merkle   │           │ DID      │           │ Roles    │
└──────────┘           └──────────┘           └──────────┘
```

| Primal | Domain | IPC Capability | What It Owns |
|--------|--------|---------------|-------------|
| **rhizoCrypt** | Ephemeral memory | `dag` | Content-addressed DAG, session lifecycle, Merkle trees, dehydration to loamSpine |
| **loamSpine** | Permanence | `ledger` | Immutable append-only ledger, DID ownership, certificate lifecycle (mint/transfer/loan), temporal anchoring |
| **sweetGrass** | Attribution | `attribution` | W3C PROV-O braids, 12 contributor roles, derivation chains, privacy controls, attribution calculation |

---

## Deploy Graph Pattern

Include the trio in your deploy graph with `fallback = "skip"` on all three
nodes. This is the canonical pattern — every spring and garden uses it.

```toml
# Provenance trio — optional enrichment
[[graph.node]]
name = "rhizocrypt"
binary = "rhizocrypt"
order = 10
required = false
depends_on = ["beardog"]
health_method = "health.liveness"
by_capability = "dag"
capabilities = ["dag.create_session", "dag.add_vertex", "dag.dehydrate"]
fallback = "skip"

[[graph.node]]
name = "loamspine"
binary = "loamspine"
order = 11
required = false
depends_on = ["beardog"]
health_method = "health.liveness"
by_capability = "ledger"
capabilities = ["ledger.commit", "ledger.mint_certificate", "ledger.verify"]
fallback = "skip"

[[graph.node]]
name = "sweetgrass"
binary = "sweetgrass"
order = 12
required = false
depends_on = ["beardog"]
health_method = "health.liveness"
by_capability = "attribution"
capabilities = ["braid.create", "contribution.record", "attribution.chain"]
fallback = "skip"
```

**Why `depends_on = ["beardog"]`**: The trio uses BearDog for cryptographic
signing of DAG vertices, ledger entries, and attribution records.

**Why `fallback = "skip"`**: Science and product logic must work without
provenance. Recording provenance is enrichment — it does not gate computation.

---

## The Commit Flow

The standard provenance commit flow composes all three primals in sequence.
biomeOS orchestrates this as the `rootpulse_commit` graph.

```
1. rhizoCrypt: dag.session.create({"name": "..."})
   → session_id

2. [Your work happens — add events to the DAG]
   rhizoCrypt: dag.event.append({"session_id": "...", "event_type": {...}, "data": {...}})
   → vertex hash (content-addressed)

3. sweetGrass: braid.create({"data_hash": "...", "mime_type": "...", "size": N,
      "name": "...", "description": "...", "source_session": "<session_id>"})
   sweetGrass: contribution.record({"hash": "...", "agent": "...", "role": "Creator"})
   → braid with contributor records and urn:braid: identifier

4. rhizoCrypt: dag.merkle.root({"session_id": "..."})
   → Merkle root hash

5. loamSpine: entry.append({"spine_id": "...", "entry_type": {...}, "committer": "..."})
   → immutable ledger entry with temporal anchor

6. sweetGrass: braid.commit({"braid_id": "urn:braid:...", "spine_id": "..."})
   → braid packaged for loamSpine anchoring
```

**The result**: An immutable record that says WHO did WHAT, WHEN, with
cryptographic proof from BearDog and a permanent ledger entry from loamSpine.

---

## Transaction Semantics and Partial Completion

The trio commit flow is **not atomic** — each primal operates independently
over JSON-RPC. Consumers must handle partial completion gracefully.

### Partial Completion States

| State | rhizoCrypt | loamSpine | sweetGrass | Validity | Consumer Action |
|-------|-----------|-----------|------------|----------|----------------|
| **Full** | DAG complete | Entry sealed | Braid committed | Complete provenance | Record all IDs |
| **DAG + spine** | DAG complete | Entry sealed | Unreachable | Valid provenance without attribution | Record DAG + spine; note missing braid |
| **DAG only** | DAG complete | Unreachable | Unreachable | Ephemeral provenance (no permanence) | Record DAG; flag as unanchored |
| **None** | Unreachable | — | — | No provenance | Science still runs; record `recorded: false` |

### Rules for Consumers

1. **A DAG session without a braid is valid partial provenance.** The merkle
   root still covers the computation — it just lacks a W3C PROV-O attribution
   envelope. Consumers SHOULD record the session ID and flag it for braid
   backfill when sweetGrass becomes reachable.

2. **A braid without a spine entry is valid attribution without permanence.**
   The attribution is recorded in sweetGrass but not anchored in the immutable
   ledger. Consumers SHOULD record the braid ID and attempt spine anchoring
   later.

3. **There is no rollback.** DAG sessions that complete cannot be undone —
   they are append-only. If spine or braid fails after DAG completion, the
   DAG session remains valid and can be referenced by future spine/braid calls.

4. **Partial state MUST be reported in output.** Consumers must expose which
   primals were reached (lithoSpore uses `primals_reached: Vec<String>` in
   `Tier3Session`). This enables auditors to distinguish "provenance was
   partial" from "provenance was not attempted."

5. **Never error on partial provenance.** Domain logic (science, validation,
   product features) MUST NOT fail because provenance recording was partial.
   The pattern: `try_record_tier3()` returns `Ok(session)` even with reduced
   `primals_reached` — only returns `Err` when zero primals respond.

### lithoSpore Reference Implementation

```rust
// From litho-core/src/provenance.rs — try_record_tier3()
let dag_ep = discover("dag").ok_or("rhizoCrypt not reachable")?;  // Hard requirement
let spine_ep = discover("spine").ok_or("loamSpine not reachable")?;
let braid_ep = discover("braid").ok_or("sweetGrass not reachable")?;

// Phase 1: DAG (required)
let dag_session_id = rpc_call_extract(&dag_ep, "dag.session.create", ...)?;
// ... append events, complete session ...

// Phase 2: Spine (best-effort after DAG)
let spine_id = rpc_call_extract(&spine_ep, "spine.create", ...)
    .unwrap_or_else(|_| "pending".into());

// Phase 3: Braid (best-effort after spine)
let braid_id = rpc_call_extract(&braid_ep, "braid.create", ...)
    .unwrap_or_else(|_| "pending".into());
```

---

## JSON-RPC Methods Reference

### rhizoCrypt (capability: `dag`)

| Method | Params | Response | Notes |
|--------|--------|----------|-------|
| `health.liveness` | `{}` | `{"status": "alive", "name": "rhizocrypt"}` | Standard health probe |
| `dag.create_session` | `{"name": "my_experiment"}` | `{"session_id": "..."}` | Creates working memory scope |
| `dag.add_vertex` | `{"session_id": "...", "content": "...", "parents": [...]}` | `{"vertex_id": "..."}` | Content-addressed; parents form DAG edges |
| `dag.get_vertex` | `{"vertex_id": "..."}` | `{"content": "...", "parents": [...], "metadata": {...}}` | Retrieve by content hash |
| `dag.dehydrate` | `{"session_id": "..."}` | `{"state": "..."}` | Serialize session for loamSpine commit |
| `dag.merkle_root` | `{"session_id": "..."}` | `{"root": "..."}` | Merkle tree root of session state |

### loamSpine (capability: `ledger`)

| Method | Params | Response | Notes |
|--------|--------|----------|-------|
| `health.liveness` | `{}` | `{"status": "alive", "name": "loamspine"}` | Standard health probe |
| `ledger.commit` | `{"state": "...", "signature": "..."}` | `{"entry_id": "...", "timestamp": "..."}` | Immutable append; requires BearDog signature |
| `ledger.verify` | `{"entry_id": "..."}` | `{"valid": true, "timestamp": "..."}` | Verify ledger entry integrity |
| `ledger.mint_certificate` | `{"type": "...", "subject": "...", "attributes": {...}}` | `{"cert_id": "..."}` | Issue a loam certificate |
| `ledger.get_entry` | `{"entry_id": "..."}` | `{"state": "...", "signature": "...", "timestamp": "..."}` | Retrieve ledger entry |

### sweetGrass (capability: `attribution`)

sweetGrass v0.7.35 exposes 37 canonical methods + 10 wire-name aliases.
The table below shows the primary methods used in composition. For the
full surface, see `sweetGrass/CONTEXT.md` or call `capabilities.list`.

| Method | Params | Response | Notes |
|--------|--------|----------|-------|
| `health.liveness` | `{}` | `{"status": "alive", "name": "sweetgrass"}` | Standard health probe |
| `braid.create` | `{"data_hash": "...", "mime_type": "...", "size": N}` | Full W3C PROV-O JSON-LD with `@id: "urn:braid:..."` | Also accepts flattened `name`, `description`, `tags`, `source_session`, `source_merkle_root` |
| `contribution.record` | `{"hash": "...", "agent": "did:...", "role": "Creator"}` | `{"contribution_id": "..."}` | Record a contributor to a braid |
| `attribution.chain` | `{"hash": "..."}` | `{"contributors": [...]}` | Get attribution chain for a content hash |
| `attribution.calculate_rewards` | `{"hash": "...", "value": N}` | `[{"agent": "...", "share": 0.5, "amount": N}]` | Calculate value distribution |
| `braid.commit` | `{"braid_id": "urn:braid:...", "spine_id": "..."}` | `{"braid_id": "...", "data_hash_bytes": "..."}` | Package braid for loamSpine anchoring |
| `provenance.graph` | `{"entity": {"data_hash": "..."}}` | `{...}` | Provenance graph for an entity |
| `provenance.export_provo` | `{"hash": "..."}` | W3C PROV-O JSON-LD | Export as PROV-O |
| `attribution.witness` | `{"hash": "...", "witness_agent": "did:...", "event_type": "..."}` | `{"witnessed_at": "..."}` | JH-5 audit attestation |
| `lifecycle.status` | `{}` | `{"status": "running", "version": "..."}` | Primal lifecycle state |

**Wire-name aliases** (for backward compatibility — use canonical names above):
`attribution.create_braid` → `braid.create`, `attribution.add_contribution` → `contribution.record`,
`attribution.calculate` → `attribution.calculate_rewards`, `attribution.seal` → `braid.commit`,
`attribution.export_prov` → `provenance.export_provo`, `provenance.lineage` → `attribution.chain`,
`provenance.create_braid` → `braid.create`, `attribution.braid` → `braid.create`,
`attribution.anchor` → `anchoring.anchor`, `braid.attribution.create` → `braid.create`.

---

## Graceful Degradation Pattern

Every spring MUST degrade gracefully when the trio is absent. This is the
pattern from airSpring, absorbed by all delta springs:

```rust
pub struct ProvenanceContext {
    rhizocrypt: Option<PathBuf>,
    loamspine: Option<PathBuf>,
    sweetgrass: Option<PathBuf>,
}

impl ProvenanceContext {
    pub fn discover(socket_dir: &Path) -> Self {
        Self {
            rhizocrypt: probe_socket(socket_dir, "rhizocrypt"),
            loamspine: probe_socket(socket_dir, "loamspine"),
            sweetgrass: probe_socket(socket_dir, "sweetgrass"),
        }
    }

    pub fn is_available(&self) -> bool {
        self.rhizocrypt.is_some()
            && self.loamspine.is_some()
            && self.sweetgrass.is_some()
    }

    pub fn record_if_available(&self, artifact: &str) -> ProvenanceResult {
        if !self.is_available() {
            return ProvenanceResult { recorded: false, reason: "trio unavailable" };
        }
        // ... wire the commit flow above ...
        ProvenanceResult { recorded: true, reason: "committed" }
    }
}
```

**Rule**: Domain logic returns `Ok` with `recorded: false` when the trio is
missing — never an error. Experiments run without provenance. Provenance is
recorded when available.

---

## Shell Composition Library Support

The `nucleus_composition_lib.sh` (41 functions) provides trio wiring for
interactive compositions:

```bash
source tools/nucleus_composition_lib.sh

# Check trio availability
trio_check || warn "Provenance trio not available — continuing without"

# Record provenance (no-op if trio unavailable)
trio_record_experiment "my_experiment" "session_001"
```

The library uses the `_uds_send()` fallback chain (socat → python3 → nc)
so trio wiring works on any system with at least one transport tool.

---

## Known Issues and Workarounds

### PG-52: UDS Empty Responses — RESOLVED (April 27, 2026)

**Problem** (historical): rhizoCrypt, loamSpine, and sweetGrass returned empty
responses to JSON-RPC calls over UDS. Four springs reported independently.

**Root causes** (identified and fixed by primal teams):
- **rhizoCrypt (S49)**: Liveness gate routed all `{`-prefixed JSON to a
  liveness-only handler. Fix: plain JSON-RPC on UDS routes to the full
  `handle_newline_connection` handler.
- **loamSpine**: Double-`BufReader` on post-BTSP paths caused empty reads.
  Fix: removed duplicate buffering.
- **sweetGrass**: EOF without trailing `\n` treated as I/O error in protocol
  auto-detection. Fix: EOF is valid line-end; unknown protocol returns JSON-RPC
  error instead of silent close.

**Caller requirements**:
- Send `\n`-terminated JSON-RPC requests
- Use >=10s read timeout (sweetGrass is slower to respond)
- Pass `FAMILY_SEED` env var to rhizoCrypt when using family-scoped sockets
  (without it, BTSP gate rejects all connections)

**Validated**: Live NUCLEUS composition with all three returning valid JSON-RPC:
`dag.session.create` → session ID, `spine.create` → spine_id + genesis_hash,
`braid.create` → full JSON-LD provenance record.

**Tracking**: `primalSpring/docs/PRIMAL_GAPS.md` PG-52 RESOLVED.

### PG-48: petalTongue musl Binary Threading Panic — ADDRESSED (April 27, 2026)

**Problem** (historical): petalTongue's musl binary panicked on `winit` thread
creation in desktop mode.

**Fix**: petalTongue now uses `EventLoopBuilderExtX11::with_any_thread(true)` on
Linux, with a shared `native_options_with_any_thread()` helper. Musl builds with
`--features ui` should work on X11.

**Status**: Rebuilt musl binary harvested to plasmidBin. Verify on your target
display.

**Tracking**: `primalSpring/docs/PRIMAL_GAPS.md` PG-48 ADDRESSED.

### PG-53: Incomplete `proprioception.get` in Server Mode — RESOLVED (April 27, 2026)

**Problem** (historical): petalTongue's `proprioception.get` returned incomplete
data in `server` mode.

**Fix**: New `system/proprioception.rs` handler always returns complete JSON
including `frame_rate`, `active_scenes`, `total_frames`, `user_interactivity`,
`mode`, `uptime_secs`, and `window` fields. Dispatched via `dispatch.rs`.

**Tracking**: `primalSpring/docs/PRIMAL_GAPS.md` PG-53 RESOLVED.

---

## Cross-Spring Provenance Patterns

### Experiment Provenance (all science springs)

Every science experiment can record its lineage:

```
1. dag.session.create: "wetspring_exp403_primal_parity"
2. dag.event.append: Python baseline (content hash of expected values)
3. dag.event.append: Rust computation result (content hash of output)
4. dag.event.append: Parity comparison (depends on both above)
5. braid.create: attribute the experiment to spring + operator
6. dag.merkle.root → entry.append → braid.commit
```

### Cross-Spring Attribution

When healthSpring routes a model through wetSpring (gut diversity) →
neuralSpring (surrogate) → hotSpring (Anderson spectral), the provenance
trio tracks the full cross-spring lineage:

```
sweetGrass braid:
  - wetSpring: Creator (gut diversity model), weight 0.4
  - neuralSpring: Contributor (surrogate training), weight 0.3
  - hotSpring: Validator (spectral verification), weight 0.2
  - healthSpring: Publisher (clinical routing), weight 0.1
```

This pattern enables the "radiating attribution" model from the
`SUNCLOUD_ECONOMIC_MODEL.md` — value distribution proportional to
contribution across spring boundaries.

### Novel Ferment Transcripts

Digital objects that gain value from accumulated, verifiable history:

```
Artifact: "Gonzales Drug Candidate #7"
  └─ rhizoCrypt DAG: 47 vertices (exploration → validation → screening)
  └─ loamSpine Ledger: 12 entries (each experiment pass sealed)
  └─ sweetGrass Braid: 8 contributors across 3 springs
  └─ Loam Certificate: provenance chain from published paper → reproduction → pipeline
```

See `whitePaper/gen4/economics/NOVEL_FERMENT_TRANSCRIPTS.md` for the
economic model.

---

## Evolution Path

### Current (May 13, 2026)

- Trio primals operational, UDS IPC **fully functional** (PG-52 resolved)
- **GAP-36 wire-name reconciliation** — sweetGrass v0.7.35 resolves 10
  downstream method name variants transparently (use canonical names above)
- sweetGrass `braid.create` accepts flattened convenience fields for
  composition callers (`name`, `description`, `tags`, `source_session`,
  `source_merkle_root`)
- NFT seal round-trip verified: `braid.create` → Ed25519 witness → `braid.commit`
- `attribution.witness` accepts JH-5 Phase 3 audit events from skunkBat pipeline
- All science springs have graceful degradation wired
- Shell composition library supports trio with `_uds_send` fallback chain
- `rootpulse_commit` graph validated end-to-end
- Live NUCLEUS: `dag.session.create`, `spine.create`, `braid.create` all return
  valid JSON-RPC responses over UDS
- `FAMILY_SEED` env var required for rhizoCrypt with family-scoped sockets

### Near Term

- First-class `provenance.*` JSON-RPC surface in rhizoCrypt
- License metadata in trio (scyBorg Phase 1 — schema in existing metadata maps)
- Cross-spring provenance braids in production compositions
- plasmidBin binary rebuild cadence for trio fixes
- **Ferment transcript pattern** — upstream springs hand portable braids to
  guideStone artifacts (lithoSpore is the first consumer;
  see `handoffs/LITHOSPORE_FERMENT_TRANSCRIPT_BRAID_HANDOFF_MAY17_2026.md`)

### Medium Term

- Attribution notice generation API in sweetGrass
- Loam certificate mesh for cross-gate provenance
- `ProvenanceQueryable` trait implementation in rhizoCrypt
- sunCloud economic integration — radiating attribution becomes value distribution
- Braid-chain verification — guideStone Tier 3 provenance referencing upstream braids

---

## Related Documents

- `fossilRecord/consolidated-apr2026/SCYBORG_PROVENANCE_TRIO_GUIDANCE.md` — scyBorg licensing via trio
- `DEPLOYMENT_AND_COMPOSITION.md` — Deploy graph patterns
- `SPRING_COMPOSITION_PATTERNS.md` §7 — Graceful degradation pattern
- `GARDEN_COMPOSITION_ONRAMP.md` — Garden product integration
- `primalSpring/docs/PRIMAL_GAPS.md` — gap registry (PG-52 resolved, PG-53 resolved)
- `whitePaper/gen4/economics/NOVEL_FERMENT_TRANSCRIPTS.md` — NFT economics
- `whitePaper/economics/SUNCLOUD_ECONOMIC_MODEL.md` — Radiating attribution
- `handoffs/LITHOSPORE_FERMENT_TRANSCRIPT_BRAID_HANDOFF_MAY17_2026.md` — ferment transcript / braid handoff contract for guideStone artifacts

---

**The trio records what happened. The ledger proves it. The braid attributes it. Together they make provenance structural, not aspirational.**

---

## FILE: `protocols/RIBOCIPHER_TRANSPORT_SIGNAL_STANDARD.md`

<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# riboCipher — Transport Signal Standard

**Status**: Ecosystem Standard (Draft — Wave 111)  
**Version**: 0.1.0  
**Date**: June 13, 2026  
**Authority**: wateringHole (eastGate overwatch)  
**Replaces**: Ad-hoc peek-and-guess protocol detection  
**Acceleration**: sourDough (scaffold + validate)

---

## Biological Context

In molecular biology, the **ribosome** is the machine that reads the genetic
code (mRNA codons) and produces functional proteins. Codons are a **cipher** —
three nucleotides encode one amino acid. The ribosome doesn't guess what it's
reading; the code declares its intent.

Similarly, when a newly synthesized protein needs routing to a specific
organelle (ER, mitochondria, nucleus), it carries a **signal peptide** — a
short leader sequence at its N-terminus. The **Signal Recognition Particle
(SRP)** reads this signal, pauses translation, and routes the ribosome to
the correct membrane for translocation.

**riboCipher** models this process for IPC connections:

- The **connection** is the nascent protein
- The **first bytes** are the signal peptide (leader sequence)
- The **accept loop** is the SRP — it reads the signal and routes
- The **handler** is the target organelle

The old approach (peek-and-guess) is like a ribosome trying to figure out
where a protein goes by looking at a random amino acid. riboCipher is the
proper signal peptide system: intentional, deterministic, tiered.

### Naming Lineage

- **BTSP** (BearDog-to-SongBird Protocol): Legacy security handshake.
  Named for specific primals. Remains as a protocol type WITHIN riboCipher.
- **riboCipher**: The convergent routing standard. Named for the biological
  process. The ribosome reads the cipher; the connection is routed.

---

## Purpose

Define how every ecoPrimals IPC connection declares its intended protocol
via an intentional signal envelope. This replaces fragile peek-and-guess
patterns where servers read the first byte and hope to classify the
connection correctly.

**Problem**: The current approach breaks when BTSP-encrypted frames start
with arbitrary ciphertext (the peeked byte is indistinguishable from noise),
and different primals disagree on what "unknown first byte" means (bearDog
assumes BTSP binary, biomeOS assumes HTTP).

**Solution**: Clients send an intentional signal. Servers route deterministically.

---

## Design Principles

1. **Signal, don't peek** — the client declares intent, the server doesn't guess.
2. **Each primal implements independently** — no shared crate dependency. Each
   team evolves their own idiomatic implementation of this standard.
3. **Convergent, not imposed** — teams adopt at their own pace within the
   deprecation window. The standard defines the target; evolution finds the path.
4. **Three security tiers** — clear (local), mito-obfuscated (family WAN),
   nuclear-sealed (privileged). Leverages existing genetics infrastructure.
5. **Warn-then-cut** — legacy peek logic stays temporarily with loud warnings,
   then gets hard-cut in a future wave.
6. **sourDough accelerates** — new primals are born with riboCipher; existing
   primals are audited toward convergence.

---

## Wire Format

### Tier 1: Clear Signal

For local same-gate IPC where the wire is trusted (UDS on same host).

```
[0xEC][protocol_type: u8]
```

Total: 2 bytes. Any ecosystem participant can read.

### Tier 2: Mito-Obfuscated Signal

For cross-gate / WAN connections where the wire is untrusted. Only family
members (those holding the mitoBeacon seed) can decode the protocol type.

```
[0xED][hmac_tag: [u8; 4]]
```

Total: 5 bytes. Observer sees random-looking bytes.

Derivation:
```
mito_key = HKDF-SHA256(salt=b"ribocipher-v1", ikm=family_seed, info=b"mito-signal")
hmac_tag = HMAC-SHA256(key=mito_key, data=[protocol_type])[0..4]
```

Server decodes by trying each known protocol type against the tag
(max 16 HMAC comparisons for 16 protocol types).

### Tier 3: Nuclear-Sealed Signal

For privileged protocol negotiation where even other family members
shouldn't know what protocol is being used.

```
[0xEE][encrypted_payload: [u8; 6]]
```

Total: 7 bytes.

Derivation:
```
nuclear_key = HKDF-SHA256(salt=b"ribocipher-v1", ikm=nuclear_seed, info=b"nuclear-signal")
plaintext   = [protocol_type: u8][session_hint: u8][padding: [u8; 4]]
ciphertext  = ChaCha20-Poly1305(key=nuclear_key, nonce=derived_from_context, plaintext)[0..6]
```

Only decryptable by the holder of the nuclear lineage key for this peer pair.

### Legacy (deprecated)

Any connection NOT starting with `0xEC`/`0xED`/`0xEE`:
- Wave 111-112: Log warning, fall through to old peek logic
- Wave 113: Reject with JSON-RPC error `-32002: riboCipher signal required`
- Wave 114: Remove all legacy peek code

---

## Signal Prefix Bytes

| Byte   | Meaning          | Mnemonic |
|--------|------------------|----------|
| `0xEC` | Clear signal     | **eC**oPrimals (open) |
| `0xED` | Mito-obfuscated  | **eD**NA (mitochondrial) |
| `0xEE` | Nuclear-sealed   | **eE**ncrypted (nuclear) |

These bytes were chosen because they:
- Never start valid UTF-8 JSON documents
- Are not ASCII printable (no HTTP verb collision)
- Are not NUL (0x00)
- Are sequential for easy range-checking

---

## Protocol Type Table

| Byte   | Protocol           | Usage |
|--------|--------------------|-------|
| `0x00` | Probe              | Lightweight health check |
| `0x01` | NDJSON JSON-RPC    | Standard ecosystem IPC |
| `0x02` | BTSP Binary        | Length-prefixed binary handshake |
| `0x03` | BTSP JSON-line     | JSON-line ClientHello handshake |
| `0x04` | HTTP/1.1           | axum/hyper over UDS |
| `0x05` | Encrypted Resume   | Post-BTSP session resume |
| `0x06` | Dark Forest Beacon | birdsong beacon packet |
| `0x07` | Mesh Relay         | songBird relay-routed frame |
| `0x08-0x0F` | Reserved      | Future expansion |

---

## Key Derivation

Reuses existing HKDF domain-separation patterns from `btsp-v1` and
`birdsong_beacon_v1`:

```
// Mito-tier (shared by all family members with same beacon seed)
mito_key = HKDF-SHA256(
    salt = b"ribocipher-v1",
    ikm  = family_seed,    // from FAMILY_SEED env / .beacon.seed
    info = b"mito-signal"
) -> [u8; 32]

// Nuclear-tier (per-peer, from nuclear lineage)
nuclear_key = HKDF-SHA256(
    salt = b"ribocipher-v1",
    ikm  = nuclear_seed,   // from node lineage seed
    info = b"nuclear-signal"
) -> [u8; 32]
```

---

## Server-Side Detection (pseudocode)

Each primal implements this in their own accept loop:

```
read first_byte from stream

match first_byte:
    0xEC -> read protocol_type (1 byte)
            route to handler for protocol_type
    0xED -> read hmac_tag (4 bytes)
            for each known protocol_type:
                if hmac_verify(mito_key, protocol_type, tag):
                    route to handler
            else: reject (not family member)
    0xEE -> read encrypted (6 bytes)
            decrypt with nuclear_key
            if success: route to handler
            else: reject
    _    -> WARN "DEPRECATED: unsignalled connection"
            legacy_guess(first_byte) -> route with old behavior
            (prepend first_byte back to stream for handler)
```

---

## Legacy Guess Table (deprecation period only)

For the warn period, unsignalled connections fall back to existing behavior:

| First byte | Legacy guess | Notes |
|------------|-------------|-------|
| `{` or `[` | NDJSON JSON-RPC | JSON document start |
| `G`, `P`, `H`, `D`, `O`, `T`, `C` | HTTP/1.1 | HTTP verb first chars |
| Anything else | Socket default | bearDog: BTSP binary; biomeOS: HTTP |

Each primal documents their socket default. This table exists ONLY for the
deprecation period and is removed at hard-cut.

---

## sourDough Integration

sourDough is the **starter culture** — it pre-evolves standards so new
primals are born compliant, and audits the fleet toward convergence.

### Scaffold (new primals born with riboCipher)

```bash
sourdough scaffold new-primal myPrimal "Description"
```

Generated code includes:
- riboCipher signal detection in the accept loop
- Clear signal sending in client IPC helpers
- No legacy peek patterns (new primals never learn old habits)

### Validate (audit existing primals)

```bash
sourdough validate ribocipher <primal-path>
```

Checks:
- Accept loop reads first byte BEFORE any protocol-specific parsing
- Signal bytes 0xEC/0xED/0xEE are handled before legacy fallback
- Legacy fallback logs at WARN level (or ERROR/REJECT per wave)
- Client connections send signal prefix before payload

### Reference Implementation

sourDough's own JSON-RPC server (`sourdough doctor`, `sourdough validate`)
implements riboCipher. Teams can study this as the canonical example of
correct signal detection in a production binary.

---

## Per-Team Evolution Tasks

Each primal team independently evolves to riboCipher convergence:

### bearDog
- Implement riboCipher detection in `unix_socket_ipc/server.rs` `handle_connection()`
- Implement riboCipher detection in `tcp_ipc/server/connection.rs`
- Update `protocol_router.rs` `ProtocolDetector::detect()` to check for riboCipher first
- Send clear signal from BTSP client connections

### songBird
- Implement riboCipher detection in `pure_rust_server/server/connection.rs`
- Implement riboCipher detection in `bin_interface/ipc_session.rs`
- Send mito-obfuscated signal for federation connections (cross-gate)
- Send clear signal for local IPC

### biomeOS
- Implement riboCipher detection in `biomeos-api/src/unix_server.rs`
- Implement riboCipher detection in `neural_api_server/connection.rs`
- Send clear signal from capability resolution client code

### sweetGrass
- Update canonical `peek.rs` to implement riboCipher detection first, legacy fallback second
- This becomes the reference pattern other primals can study

### primalSpring
- Update `nucleus_launcher` to send clear signal when probing primal health
- Update harness IPC connections to send clear signal
- Update BTSP handshake client to send appropriate signal before ClientHello

### cellMembrane
- Update `gate/health.rs` `uds_jsonrpc_call()` to prepend `[0xEC, 0x01]`
- Add `[transport.ribocipher]` section to `membrane.toml` and gate profiles
- Update `plasmid.sandbox` / `plasmid.canary` IPC to send clear signal

### sourDough
- Implement riboCipher in own IPC server (reference implementation)
- Add `validate ribocipher` subcommand
- Update scaffold templates to emit riboCipher-compliant accept loops

---

## Configuration (cellMembrane gate profiles)

```toml
[transport.ribocipher]
signal_tier = "clear"              # default tier for outbound connections
unsignalled_policy = "warn"        # "warn" | "error" | "reject"
mito_key_source = "family_seed"    # derive from FAMILY_SEED
```

---

## Deprecation Timeline

| Wave | Behavior |
|------|----------|
| 111 (now) | Standard published. Teams begin implementation. WARN on legacy. |
| 112 | All clients send riboCipher signals. Legacy paths log at ERROR. |
| 113 | Hard-cut: unsignalled connections rejected (`-32002`). |
| 114 | Legacy peek code removed from all primals. |

---

## Validation

A primal is riboCipher-compliant when:

1. Its server accept loop checks for `0xEC`/`0xED`/`0xEE` BEFORE any peek logic
2. Its client connections send the appropriate signal prefix
3. Unsignalled connections produce a WARN-level log
4. Tests demonstrate correct routing for all three tiers
5. `sourdough validate ribocipher` passes

---

## Relationship to Existing Standards

| Standard | Relationship |
|----------|-------------|
| BTSP (bearDog Transport Security Protocol) | riboCipher signals WHICH protocol to use; BTSP is one of those protocols (types 0x02, 0x03, 0x05) |
| Dark Forest Beacon Genetics | Mito-tier riboCipher uses the same seed and similar HKDF derivation |
| GATE_NUCLEUS_SYSTEMD_STANDARD | Deployed primals use riboCipher for all socket connections |
| Three-tier genetics (mito/nuclear/tag) | riboCipher tiers map directly to genetics tiers |
| sourDough scaffold | New primals generated with riboCipher compliance from birth |

---

## FILE: `protocols/SEMANTIC_METHOD_NAMING_STANDARD.md`

# 🌍 Semantic Method Naming Standard for Primal IPC

**Version**: 2.0.0  
**Date**: January 25, 2026  
**Status**: Official Ecosystem Standard  
**Authority**: wateringHole (ecoPrimals Core Standards)  
**Supersedes**: Primal IPC Protocol v1.0 (method naming section)

---

## 🎯 PURPOSE

Establish semantic method naming conventions that enable **isomorphic evolution** - allowing primals to evolve, swap, and extend while maintaining ecosystem coherence.

**Key Principle**: Method names should describe **WHAT** (semantic intent), not **HOW** (implementation details).

---

## 📐 SEMANTIC NAMESPACE STRUCTURE

### Format: `{domain}.{operation}[.{variant}]`

**Components**:
1. **Domain**: Capability area (crypto, tls, http, storage, etc.)
2. **Operation**: What the method does (encrypt, decrypt, hash, etc.)
3. **Variant** (optional): Specific algorithm or mode

### Examples:

```json
// Cryptographic Operations
"crypto.generate_keypair"      // Semantic (what)
"crypto.x25519.generate"       // Specific (how)
"crypto.encrypt"               // Generic encryption
"crypto.aes128_gcm.encrypt"    // Specific algorithm

// TLS Operations
"tls.derive_secrets"           // TLS key derivation
"tls.sign_handshake"           // Sign handshake data
"tls.verify_certificate"       // Certificate validation

// HTTP Operations
"http.request"                 // Generic HTTP request
"http.get"                     // HTTP GET
"http.post"                    // HTTP POST

// Storage Operations
"storage.put"                  // Store data
"storage.get"                  // Retrieve data
"storage.delete"               // Remove data
```

---

## 🔄 EVOLUTION PATTERNS

### Pattern 1: Generic to Specific

**Level 1 - Semantic (stable)**:
```json
{"method": "crypto.encrypt", "params": {"algorithm": "aes-128-gcm", ...}}
```

**Level 2 - Algorithm-Specific (evolving)**:
```json
{"method": "crypto.aes128_gcm.encrypt", "params": {...}}
```

**Level 3 - Implementation-Specific (deprecated)**:
```json
// OLD - DO NOT USE
{"method": "aes128_gcm_encrypt", "params": {...}}
```

### Pattern 2: Version Evolution

```
v0.9:  "x25519_generate_ephemeral"           ❌ No namespace
v1.0:  "crypto.x25519_generate_ephemeral"    ✅ Domain namespace
v2.0:  "crypto.x25519.generate"              ✅ Hierarchical
v3.0:  "crypto.generate_keypair"             ✅ Fully semantic
       + params: {"algorithm": "x25519"}
```

**Migration Path**: Each version supports previous patterns during transition.

---

## 🌍 DOMAIN NAMESPACES

### Core Domains (Standardized)

#### 1. `crypto.*` - Cryptographic Operations

```json
// Key Management
"crypto.generate_keypair"      // Generate key pair
"crypto.derive_secret"         // Key exchange/derivation
"crypto.import_key"            // Import external key
"crypto.export_key"            // Export key

// Symmetric Encryption
"crypto.encrypt"               // Generic encryption
"crypto.decrypt"               // Generic decryption
"crypto.aes128_gcm.encrypt"    // AES-128-GCM specific
"crypto.aes256_gcm.encrypt"    // AES-256-GCM specific
"crypto.chacha20_poly1305.encrypt"  // ChaCha20-Poly1305

// Hashing
"crypto.hash"                  // Generic hash
"crypto.blake3.hash"           // BLAKE3 specific
"crypto.sha256.hash"           // SHA-256 specific
"crypto.hmac"                  // HMAC

// Signatures
"crypto.sign"                  // Generic signing
"crypto.verify"                // Generic verification
"crypto.ed25519.sign"          // Ed25519 specific
"crypto.ecdsa_p256.sign"       // ECDSA P-256 specific
```

#### 2. `tls.*` - TLS/SSL Operations

```json
"tls.derive_secrets"           // TLS key derivation
"tls.derive_handshake_secrets" // Handshake traffic keys
"tls.derive_application_secrets"  // Application traffic keys
"tls.compute_finished_verify_data"  // Finished message MAC
"tls.sign_handshake"           // Sign handshake context
"tls.verify_certificate"       // Verify cert chain
```

#### 3. `http.*` - HTTP/HTTPS Operations

```json
"http.request"                 // Generic HTTP request
"http.get"                     // HTTP GET
"http.post"                    // HTTP POST
"http.put"                     // HTTP PUT
"http.delete"                  // HTTP DELETE
"http.head"                    // HTTP HEAD
"http.patch"                   // HTTP PATCH
```

#### 4. `storage.*` - Data Storage Operations

```json
"storage.put"                  // Store object
"storage.get"                  // Retrieve object
"storage.delete"               // Delete object
"storage.list"                 // List objects
"storage.exists"               // Check existence
"storage.metadata"             // Get metadata
```

#### 5. `discovery.*` - Service Discovery

```json
"discovery.announce"           // Announce service
"discovery.query"              // Query for services
"discovery.heartbeat"          // Health check
"discovery.list"               // List all services
```

#### 6. `genetic.*` - Genetic Lineage Operations

```json
"genetic.derive_key"           // Derive from lineage
"genetic.mix_entropy"          // Mix entropy sources
"genetic.verify_lineage"       // Verify genetic proof
"genetic.generate_proof"       // Generate lineage proof
```

---

## 🔧 IMPLEMENTATION GUIDELINES

### For Primal Developers

#### 1. Choose Semantic Names

**✅ Good** (semantic):
```rust
async fn handle_request(&self, method: &str) -> Result<Response> {
    match method {
        "crypto.generate_keypair" => self.generate_keypair(params),
        "crypto.encrypt" => self.encrypt(params),
        // Clear intent, algorithm specified in params
    }
}
```

**❌ Bad** (implementation-specific):
```rust
async fn handle_request(&self, method: &str) -> Result<Response> {
    match method {
        "x25519_keygen" => self.x25519_keygen(),  // Too specific
        "aes_enc" => self.aes_encrypt(),          // Unclear
    }
}
```

#### 2. Support Evolution

**Version N** (current):
```rust
match method {
    // New semantic name (preferred)
    "crypto.generate_keypair" => self.generate_keypair(params),
    
    // Old name (deprecated, but supported for transition)
    "x25519_generate_ephemeral" => {
        warn!("Deprecated method name, use 'crypto.generate_keypair'");
        self.generate_keypair(params)
    }
}
```

**Version N+1** (next):
```rust
match method {
    "crypto.generate_keypair" => self.generate_keypair(params),
    // Old name removed after transition period
}
```

#### 3. Document Capabilities

In your primal's documentation:

```toml
# Example: BearDog v0.18.0 capabilities

[capabilities.provided]
"crypto.generate_keypair" = "Generate X25519 keypair"
"crypto.derive_secret" = "ECDH key derivation"
"crypto.encrypt" = "Symmetric encryption (ChaCha20-Poly1305, AES-GCM)"
"crypto.hash" = "BLAKE3 hashing"
"tls.derive_secrets" = "TLS 1.3 key derivation"

[capabilities.deprecated]
"x25519_generate_ephemeral" = "Use crypto.generate_keypair instead"
"chacha20_poly1305_encrypt" = "Use crypto.encrypt with algorithm param"
```

---

## 🌐 NEURAL API TRANSLATION LAYER

### How biomeOS Bridges Evolution Gaps

During ecosystem evolution, primals may use different naming conventions. biomeOS Neural API provides **automatic translation**:

```toml
# graphs/tower_atomic_bootstrap.toml

[nodes.capabilities_provided]
# Semantic Name (what consumers call) → Actual Method (what provider implements)
"crypto.generate_keypair" = "crypto.x25519_generate_ephemeral"  # Current
# "crypto.generate_keypair" = "crypto.x25519.generate"          # Future
```

**How It Works**:

```
1. Songbird calls Neural API:
   {"method": "crypto.generate_keypair", "params": {...}}

2. Neural API looks up translation:
   "crypto.generate_keypair" → "crypto.x25519_generate_ephemeral" (BearDog v0.18)

3. Neural API routes to BearDog:
   {"method": "crypto.x25519_generate_ephemeral", "params": {...}}

4. BearDog executes and returns result

5. Neural API returns to Songbird
```

**Benefits**:
- ✅ Old primals work with new primals
- ✅ New primals work with old primals
- ✅ Ecosystem remains coherent during evolution
- ✅ No coordination required - update graphs only

---

## 📋 MIGRATION GUIDE

### For Existing Primals

**Phase 1: Add Semantic Aliases** (Week 1)
```rust
match method {
    // Keep old names working
    "x25519_generate_ephemeral" => self.generate_keypair(params),
    
    // Add new semantic names
    "crypto.generate_keypair" => self.generate_keypair(params),
}
```

**Phase 2: Deprecation Warnings** (Week 2-4)
```rust
match method {
    "x25519_generate_ephemeral" => {
        warn!("Method '{}' is deprecated. Use 'crypto.generate_keypair' instead.", method);
        self.generate_keypair(params)
    }
    "crypto.generate_keypair" => self.generate_keypair(params),
}
```

**Phase 3: Remove Old Names** (Month 2+)
```rust
match method {
    "crypto.generate_keypair" => self.generate_keypair(params),
    // Old names removed
}
```

### For New Primals

**Start with semantic names from day 1**:
```rust
match method {
    "crypto.generate_keypair" => self.generate_keypair(params),
    "crypto.encrypt" => self.encrypt(params),
    "crypto.hash" => self.hash(params),
    // All semantic, no legacy baggage
}
```

---

## ✅ COMPLIANCE CHECKLIST

### For Primal Authors

- [ ] All methods use domain namespaces (`crypto.*`, `tls.*`, `http.*`)
- [ ] Method names describe intent, not implementation
- [ ] Capabilities documented in README or CAPABILITIES.toml
- [ ] Deprecated methods supported with warnings during transition
- [ ] Integration tests use semantic names
- [ ] Graph mappings updated for Neural API translation

### For biomeOS Integration

- [ ] Graph includes `capabilities_provided` mappings
- [ ] Translation registry populated from graph
- [ ] Semantic → Actual method translation working
- [ ] Tests validate translation layer
- [ ] Documentation shows semantic examples

---

## 🎯 EXAMPLES: BEFORE & AFTER

### BearDog Evolution

**Before** (v0.9 - Pre-semantic):
```json
{"jsonrpc": "2.0", "method": "x25519_generate_ephemeral", "params": {}}
{"jsonrpc": "2.0", "method": "chacha20_poly1305_encrypt", "params": {...}}
{"jsonrpc": "2.0", "method": "blake3_hash", "params": {...}}
```

**After** (v0.18 - Semantic):
```json
{"jsonrpc": "2.0", "method": "crypto.x25519_generate_ephemeral", "params": {}}
{"jsonrpc": "2.0", "method": "crypto.chacha20_poly1305_encrypt", "params": {...}}
{"jsonrpc": "2.0", "method": "crypto.blake3_hash", "params": {...}}
```

**Future** (v1.0 - Fully Semantic):
```json
{"jsonrpc": "2.0", "method": "crypto.generate_keypair", "params": {"algorithm": "x25519"}}
{"jsonrpc": "2.0", "method": "crypto.encrypt", "params": {"algorithm": "chacha20_poly1305", ...}}
{"jsonrpc": "2.0", "method": "crypto.hash", "params": {"algorithm": "blake3", ...}}
```

### Songbird Evolution

**Before** (Direct BearDog calls):
```rust
// Tight coupling - knows BearDog's exact methods
let response = beardog.call_rpc("x25519_generate_ephemeral", params).await?;
```

**Interim** (Semantic names, direct):
```rust
// Semantic names, still direct
let response = beardog.call_rpc("crypto.x25519_generate_ephemeral", params).await?;
```

**After** (Neural API routing):
```rust
// Fully semantic via Neural API
let response = neural_api.call_capability("crypto.generate_keypair", params).await?;
// Neural API handles translation and routing
```

---

## 🔗 RELATED STANDARDS

- `PRIMAL_IPC_PROTOCOL.md` - Base IPC protocol
- `ECOBIN_ARCHITECTURE_STANDARD.md` - Pure Rust principles
- `UNIBIN_ARCHITECTURE_STANDARD.md` - Single binary pattern
- biomeOS `ISOMORPHIC_EVOLUTION.md` - Evolution principles
- biomeOS `NEURAL_API_ROUTING_SPECIFICATION.md` - Translation layer

---

## 📊 ADOPTION STATUS

| Primal | Version | Status | Notes |
|--------|---------|--------|-------|
| **BearDog** | v0.18.0+ | ✅ Adopted | Using `crypto.*` and `tls.*` namespaces |
| **Songbird** | v5.25.0 | 🔄 In Progress | HTTP client needs update to semantic names |
| **Squirrel** | v2.x | 🔄 Phase 2 | Semantic names primary, legacy aliases deprecated with warnings |
| **NestGate** | v2.x | ⏳ Pending | Will adopt in next evolution |
| **ToadStool** | v1.x | ⏳ Pending | Will adopt in next evolution |

---

## 🎉 BENEFITS

1. **Isomorphic Evolution**: Ecosystem structure preserved during change
2. **Provider Swappability**: Replace implementations without breaking consumers
3. **Clear Intent**: Method names self-documenting
4. **Forward Compatible**: New methods don't break old code
5. **Backward Compatible**: Old methods supported during transition
6. **Ecosystem Resilience**: Neural API bridges evolution gaps
7. **TRUE PRIMAL**: No hardcoded cross-primal dependencies

---

**Status**: Official Standard (v2.0.0)  
**Adoption**: Mandatory for new primals, recommended migration for existing  
**Enforcement**: Neural API translation layer bridges gaps during migration  
**Questions**: Post in wateringHole discussions

---

*"Semantic stability enables evolutionary freedom"* 🌍🦀


---

## FILE: `README.md`

# The Watering Hole - ecoPrimals Ecosystem Guidance

**Purpose**: Authoritative project guidance for every primal in the ecoPrimals ecosystem  
**Audience**: Any primal, at any point in its evolution — and four external audiences (PIs, students, builders, compliance)  
**Last Updated**: July 21, 2026 (Wave 150s: Standards reorganized into `foundations/`, `protocols/`, `operations/`, `compositions/`. 41 active standards, 8 fossilized. Sovereignty evolution roadmap. DNSSEC 3/3 domains.)

---

## What is the Watering Hole?

The Watering Hole is the shared knowledge layer of the ecoPrimals project. Every primal - whether newly conceived or production-hardened - comes here to understand the ecosystem it belongs to: what other primals exist, what standards govern interoperability, how coordination works, and what principles guide evolution.

This is not documentation about a subdirectory. This is the living reference for the entire project.

---

## Core Concepts

### What is a Primal?

A **primal** is a collection of **primitives** - small, focused capabilities that solve one domain well. Primals are autonomous: each is a self-contained Rust binary that knows only itself. Complexity is never solved by making a primal larger. It is solved through **coordination** - primals composing their primitives together at runtime, orchestrated by biomeOS.

**Key properties of every primal:**

- **Self-knowledge only**: A primal knows what it can do, never what others can do
- **Capability-based discovery**: Primals find each other at runtime by advertising capabilities
- **Zero compile-time coupling**: No primal imports another primal's code
- **Pure Rust**: 100% Rust application code, zero C dependencies
- **UniBin architecture**: One binary per primal, multiple operational modes

### What are Primitives?

Primitives are the atomic operations a primal provides. BearDog's primitives include Ed25519 signing, BLAKE3 hashing, and X25519 key exchange. Songbird's primitives include TLS 1.3 handshakes, mDNS discovery, and UDP multicast. A primitive is the smallest unit of capability in the ecosystem.

### How do Primals Coordinate?

Primals communicate via **JSON-RPC 2.0** over platform-agnostic transports (Unix sockets, abstract sockets, TCP, named pipes). They never share memory or embed each other's code. biomeOS discovers primals by their capabilities at runtime and coordinates them into higher-order behaviors.

The result: complex systems **emerge** from simple composition, rather than being engineered monolithically.

---

## The Primals

### Foundation Primals

These primals form the NUCLEUS deployment architecture. They are the bedrock of the ecosystem - production-ready, extensively tested, and required for core ecosystem function.

| Primal | Domain | Role | Status |
|--------|--------|------|--------|
| **BearDog** | Cryptography | All cryptographic operations: signing, encryption, key exchange, hashing, certificates, genetic lineage | Production (A+ LEGENDARY) |
| **Songbird** | Networking | Network orchestration: TLS 1.3, service discovery, NAT traversal, federation, BirdSong protocol, Pure Rust Tor | Production (S+) |
| **NestGate** | Data Storage | Content-addressed storage, dataset management, capability-based service discovery | Production (A++ TOP 1%) |
| **ToadStool** | Hardware Infrastructure | Hardware discovery, capability probing, compute orchestration: CPU, GPU, NPU, WASM, containers, edge. 23,000+ tests (9,232+ lib), **112 JSON-RPC methods** (17 groups). Node Atomic for sovereign compute. ecoBin v3.0 certified. riboCipher CLEAR + MitoBeacon. Zero-copy dispatch. Cross-architecture (`cargo check --target x86_64-pc-windows-gnu` passes, S329). **Phase 2 Silicon Atheism: cross-platform GPU backends** — `WgpuGpuDiscovery`, `PortableSwapExecutor`, `PortableResourceHandle` (S332). **S333 structural debt** — 7 large files refactored, hardcoded primal names → capability terms. Zero clippy warnings. Zero `/tmp` hardcoding. 100% env centralized. VFIO sovereign dispatch validated. | Production (A++ GOLD, S333+) |
| **BarraCuda** | Pure Math | 806 WGSL f64 shaders (the mathematics), naga-IR optimisation (FMA fusion, DCE), precision strategy (f64/DF64/f32). Writes the math; coralReef compiles it; toadStool runs it. Budded from ToadStool (S93). v0.3.5, 3,400+ tests | Production (A+) |
| **coralReef** | Shader Compilation | Sovereign WGSL→native shader compiler. naga parser + lowering passes (f64, FMA fusion, dead expression elimination). JSON-RPC IPC via XDG discovery. AMD E2E proven, NVIDIA SM70-SM89. coral-gpu unified compute abstraction. VFIO dispatch with PFIFO channel + V2 MMU + USERD_TARGET fix. **coral-glowplug** production-grade boot-persistent PCIe device lifecycle broker (systemd daemon, personality hot-swap, health monitor, auto-D0 recovery, VFIO-first boot, graceful shutdown, DRM render node fencing, IOMMU group handling). **FECS firmware direct execution proven** (LS bypass on clean falcon). SEC2 EMEM breakthrough (Exp 066-069). D3hot→D0 sovereign VRAM recovery. Sovereign power management designed (5-state model). Reproducibility checklist for adding new GPUs | Production (Phase 10, Iter 52) |
| **Squirrel** | AI Coordination | Sovereign AI model context protocol, multi-MCP coordination, vendor-agnostic inference | Production (A++) |
| **biomeOS** | Orchestration | Composition primal: Neural API (320+ translations, 27 domains), 5 coordination patterns (Sequential, Parallel, ConditionalDag, Pipeline streaming, Continuous 60Hz), capability routing, NUCLEUS composition, PathwayLearner optimization, NDJSON streaming, bonding model, Dark Forest coordination, provenance trio wiring, `signal.dispatch` composition collapse, `primal.announce` atomic self-registration, `composition.status` pipelines, enrichment module, `NucleusMode::Full` (13 primals), 16 braid signal graphs, `spore.instantiate`, stability tiers (114 annotations), adaptive routing weights (redb-persistent), weight health introspection, composition intelligence, capability utilization tracking, guideStone startup contract (`--bind-mode`), HEALTH-01 compliant, Duration constants centralized | Production (v4.23, Security A++ LEGENDARY) |

### Post-NUCLEUS Primals

These primals build emergent behaviors on the NUCLEUS foundation. They compose into higher-order patterns (RootPulse, Memory & Attribution Stack) coordinated by biomeOS via the Neural API. Each is functional and tested, representing the next evolutionary phase.

| Primal | Domain | Role | Status |
|--------|--------|------|--------|
| **petalTongue** | Representation | Universal UI: visual, audio, terminal, web, headless. Accessibility-first multi-modal rendering | Production (A++) |
| **rhizoCrypt** | Ephemeral Memory | Content-addressed DAG engine for working memory. Sessions, Merkle trees, real-time streaming | Production (A+) |
| **sweetGrass** | Attribution | Semantic provenance (v0.7.38). W3C PROV-O braids, fair attribution, 37 canonical methods + 10 wire-name aliases, tarpc 0.37 + REST + UDS, UniBin, ecoBin, Edition 2024, GAP-36 wire reconciliation, Provenance Trio coordination, Tower Atomic enforced | Production |
| **LoamSpine** | Permanence | Immutable linear ledger for selective permanence. Loam Certificates for ownership and transfer | Production (A+) |
| **skunkBat** | Defense | Defensive network security: threat detection, graduated response, baseline profiling | Production |

### Supporting Tools

| Tool | Purpose |
|------|---------|
| **sourDough** | Starter culture - scaffolding, genomeBin tooling, ecosystem bootstrapping |

---

## Composed Systems

Primals achieve their greatest power through composition. These are not separate projects - they are coordination patterns that emerge when primals work together.

### Tower Atomic

**What**: BearDog (crypto) + Songbird (TLS/HTTP) = Pure Rust HTTPS

**How**: Songbird implements TLS 1.3 protocol logic. BearDog provides all cryptographic operations via JSON-RPC. Neither embeds the other. The result is a fully Pure Rust HTTPS stack with zero C dependencies.

**Used by**: Any primal that needs external network access routes through Tower Atomic.

### NUCLEUS

**What**: The full primal composition orchestrated by biomeOS.

**Layers**:
- **Tower Atomic** = BearDog + Songbird (crypto + network)
- **Node Atomic** = Tower + ToadStool (hardware) + BarraCuda (math)
- **Nest Atomic** = Tower + NestGate (+ storage)
- **Full NUCLEUS** = All primals + Squirrel (+ AI)

*Note*: BarraCuda budded from ToadStool into a standalone primal (S93).
BarraCuda is pure math — WGSL shaders and precision strategy. coralReef
compiles the math to native GPU binaries. ToadStool discovers and dispatches
hardware. Springs depend on BarraCuda directly for math without pulling
ToadStool's runtime or coralReef's compiler.

biomeOS composes these atomics based on what capabilities are available at runtime.

### The Coordination Triad: quorumSignal / rootPulse / waterFall

Three coordination domains form the ecosystem's nervous system. Each uses the
5 `CoordinationPattern` execution strategies (Sequential, Parallel, ConditionalDag,
Pipeline, Continuous) but serves a distinct biological purpose:

| Domain | Role | Analogy | Status |
|--------|------|---------|--------|
| **quorumSignal** | SENSE — observe, discover, react | Afferent nervous system | First-class: 15 atomic graphs, `signal.dispatch` |
| **rootPulse** | ACTION — create, mutate, prove | Efferent nervous system | Partial: `nest.commit` signal + pattern wired |
| **waterFall** | SYNC — ecosystem coherence across gates | Autonomic nervous system | Fully Rust (`membrane temporal.cascade`), manifest-driven |

Named after bacterial quorum sensing: collective behavior emerges when enough
gate NUCLEUS instances participate. The quorum is the minimum primal set for an
atomic operation — Tower quorum is 3, Nest quorum is 4, Full NUCLEUS is 13.

**Short triad**: quorum, pulse, fall.

**Specification**: `primalSpring/specs/NEURAL_API_EVOLUTION.md` (Coordination Domains section)

### rootPulse (ACTION — efferent)

**What**: Distributed version control that emerges from primal coordination - not a monolithic VCS. The "pulse" coordination domain of the triad.

**Composition**:
- **rhizoCrypt** provides the ephemeral DAG workspace (fast, lock-free, present/future)
- **loamSpine** provides the immutable linear history (permanent, cryptographically provable, past)
- **nestGate** provides content-addressed blob storage
- **bearDog** provides cryptographic signing and verification
- **sweetGrass** provides semantic attribution tracking
- **songbird** provides discovery and federation

**Coordinator**: biomeOS orchestrates these primals via the Neural API. No primal knows about "version control" - biomeOS composes their primitives into temporal coordination patterns, and version control emerges.

**Core insight**: "rootPulse is what primals DO together, not what they ARE."

**Five operations**: commit, branch, merge, diff, federate — all composed from atomic primal capabilities via `signal.dispatch` and `graph.execute`.

### Plasmodium (Over-NUCLEUS Collective)

**What**: The emergent coordination layer formed when 2+ NUCLEUS instances bond covalently.

**Analogy**: Named after the slime mold *Physarum polycephalum* -- no central brain, collective intelligence, pulsing coordination, graceful degradation.

**How**: biomeOS on any gate queries the local Songbird mesh for bonded peers, connects to their NUCLEUS instances, and aggregates capabilities, models, and load into a unified collective view. Workloads route to the best gate based on capability match, resource availability, and model affinity.

**Key properties**:
- No master node -- any gate can query the collective
- Gates join and leave dynamically (like slime mold pseudopods)
- Uses only existing primal primitives (Songbird mesh, BearDog trust, AtomicClient IPC)
- Security: genetic lineage trust via shared family seed, BearDog Dark Forest verification

**Specification**: `phase2/biomeOS/specs/PLASMODIUM_OVER_NUCLEUS_SPEC.md`  
**CLI**: `biomeos plasmodium status|gates|models`

### Neural API

**What**: biomeOS's adaptive orchestration layer that routes semantic requests to capable primals.

**How**: A caller requests `capability.call("crypto", "sha256")` and the Neural API discovers which primal provides that capability, routes the request, and returns the result. The caller never needs to know about BearDog specifically.

**Architecture**:
- Layer 1: Primals (capabilities via JSON-RPC)
- Layer 2: biomeOS (orchestration, routing, learning)
- Layer 3: Niche APIs (domain patterns like RootPulse, RPGPT)

**Five Coordination Patterns** (all driven by TOML graphs):

| Pattern | Method | Description |
|---------|--------|-------------|
| Sequential | `graph.execute` | Nodes in dependency order |
| Parallel | `graph.execute` | Independent nodes concurrently |
| ConditionalDag | `graph.execute` | DAG with `condition`/`skip_if` branching |
| Pipeline | `graph.execute_pipeline` | Streaming via bounded mpsc channels — items flow through nodes immediately |
| Continuous | `graph.start_continuous` | Fixed-timestep tick loop (e.g., 60Hz for game engines) |

**biomeOS as Composition Primal**: biomeOS is functionally the super-service — the
primal that composes all other primals into systems. While it sits at the same level
as other primals (sovereign, self-contained, JSON-RPC first), its unique role is
orchestrating emergent systems: RootPulse (version control), RPGPT (game engines),
AlphaFold-class (protein folding), and any other system that emerges as a function
of primal coordination.

**Streaming (v2.43)**: Pipeline graphs use NDJSON streaming — primals write multiple
response lines per request. The `AtomicClient::call_stream()` reads them as they
arrive. No new protocol needed. All primals already have streaming transport.

The PathwayLearner analyzes execution metrics and suggests optimizations (parallelization,
prewarming, batching, caching) that improve over time.

---

## Architecture Standards

These standards define how every primal is built, packaged, and deployed.

### UniBin - Binary Structure Standard

One binary per primal, multiple operational modes via subcommands. Professional CLI with `--help`, `--version`, and structured error messages. Every primal is a single executable named after itself.

**Specification**: `fossilRecord/wave150s_standards/ECOBIN_ARCHITECTURE_STANDARD.md` (consolidated — UniBin is a subset of ecoBin)

### ecoBin - Universal Portability Standard

ecoBin = UniBin + Pure Rust + Cross-Platform. Zero C dependencies in application code, cross-compiles to any Rust target with a single `cargo build` command, platform-agnostic IPC with runtime transport discovery.

**Specification**: `fossilRecord/wave150s_standards/ECOBIN_ARCHITECTURE_STANDARD.md`

### genomeBin - Autonomous Deployment Standard

genomeBin = ecoBin + deployment wrapper. Self-extracting archive that auto-detects the system, installs the correct binary, configures services, and validates health. One command installs on any system with zero manual configuration.

**Specification**: See `fossilRecord/wave150s_standards/ECOBIN_ARCHITECTURE_STANDARD.md` (genomeBin section)

### The Evolutionary Ladder

```
UniBin   (structure)    → One binary, multiple modes
  ↓
ecoBin   (portability)  → + Pure Rust, cross-compilation, platform-agnostic IPC
  ↓
genomeBin (deployment)  → + Auto-detection, service integration, health monitoring
```

All ecoBins are UniBins. All genomeBins are ecoBins. Each stage adds capability without replacing the previous.

---

## Communication Standards

### Primal IPC Protocol

JSON-RPC 2.0 over platform-agnostic transports. Capability-based discovery with zero cross-embedding. Every primal implements its own IPC independently - standards define WHAT, primals implement HOW.

**Specification**: `protocols/CAPABILITY_WIRE_STANDARD.md` (IPC protocol consolidated here)

### Universal IPC Standard

Behavioral specification for multi-transport IPC. Each primal discovers the best transport at runtime: Unix sockets on Linux/macOS, abstract sockets on Android, named pipes on Windows, TCP as universal fallback. No shared IPC crate - each primal owns its communication code.

**Specification**: `protocols/CAPABILITY_BASED_DISCOVERY_STANDARD.md`

### BirdSong Protocol

Encrypted UDP discovery protocol for auto-trust within genetic lineages. Songbird broadcasts encrypted beacons; only primals sharing the same family seed can decrypt them. Zero metadata leakage.

**Specification**: `birdsong/BIRDSONG_PROTOCOL.md`

### Semantic Method Naming

Method names describe intent, not implementation: `crypto.sign`, `tls.handshake`, `storage.put`. Domain namespaces enable Neural API translation and isomorphic evolution across primals.

**Specification**: `protocols/SEMANTIC_METHOD_NAMING_STANDARD.md`

---

## Security Model

### Genetic Lineage

A group of primals sharing a common `family_seed` - enabling cryptographic auto-trust. BearDog manages lineage seeds (nuclear DNA, for identity/permissions) and beacon seeds (mitochondrial DNA, for Dark Forest discovery).

### Auto-Trust Within Family

Primals of the same genetic lineage trust each other automatically. Decryption of a BirdSong beacon proves family membership. No manual configuration, no certificate authorities.

### Zero Trust Outside Family

No trust without family membership. Encrypted payloads are unreadable to outsiders. Continuous validation. Dark Forest protocol ensures zero metadata leakage - observers cannot even tell that communication is occurring.

### Pure Rust Security

Zero C dependencies eliminates entire classes of memory safety vulnerabilities. RustCrypto suite for all cryptographic operations. No openssl, no ring, no C assembly.

---

## Primal Interaction Map

### Currently Working

- **Songbird + BearDog**: Encrypted BirdSong discovery (Tower Atomic)
- **biomeOS + All Primals**: Health monitoring, capability discovery, Neural API routing
- **biomeOS + petalTongue**: Real-time SSE events for ecosystem visualization

### Wired (biomeOS coordination layer)

- **rhizoCrypt + LoamSpine + sweetGrass**: Provenance trio — `rootpulse_commit` graph orchestrates dehydration → sign → store → commit → attribute
- **Any Spring + Provenance Trio**: `provenance_pipeline` graph — universal experiment provenance
- **NestGate + LoamSpine**: Content-addressed storage backing immutable history

### primalSpring Coordination (ecosystem self-validation)

- **primalSpring + All NUCLEUS Primals**: Atomic composition testing (Tower, Node, Nest, Full NUCLEUS)
- **primalSpring + biomeOS**: Graph execution validation — all 5 coordination patterns with real primals
- **primalSpring + Provenance Trio**: RootPulse emergent system validation (commit, branch, merge, diff, federate)
- **primalSpring + Songbird Mesh**: Plasmodium formation, gate failure, capability aggregation
- **primalSpring + neuralSpring + wetSpring + hotSpring + ToadStool + NestGate**: helixVision structure prediction pipeline
- **primalSpring + airSpring + wetSpring + neuralSpring**: Cross-spring ecology data flow
- **primalSpring + fieldMouse + NestGate + sweetGrass**: Edge data ingestion pipeline
- **primalSpring + petalTongue**: SSE visualization pipeline
- **primalSpring + Squirrel**: AI coordination via biomeOS capability graph

### Under Development

- **Songbird + Songbird**: Cross-tower federation, multi-family routing

**Detail**: See primal composition maps in `compositions/PRIMAL_REGISTRY.md`

---

## Design Principles

1. **Single Responsibility**: Each primal does one thing. BearDog only does cryptography. Songbird only does networking. Complexity emerges from coordination, not from expanding scope.

2. **Interface Segregation**: Primals expose narrow, focused interfaces. LoamSpine doesn't know about "commits" - it provides append-only storage. biomeOS composes that into version control.

3. **Dependency Inversion**: Primals depend on abstract capabilities, not concrete implementations. Any storage provider works, not just NestGate.

4. **Message Passing**: Communication via messages over IPC, never shared state. No locks, no race conditions, inherently concurrent.

5. **Emergence Over Engineering**: Don't build a monolithic VCS - coordinate existing primals and let version control emerge. Don't build a monolithic security stack - let BearDog and Songbird compose into Tower Atomic.

---

## Document Index

### Root (always at top level)
- **`STANDARDS_AND_EXPECTATIONS.md`** — Single-document reference for all standards, expectations, and conventions
- **`GLOSSARY.md`** — Definitive ecosystem terminology
- **`ORTHOGONAL_DIMENSIONS_REVIEW.md`** — Active dimensional review tool

### `foundations/` — Architectural Invariants (9 standards)

Long-term architectural standards — rarely change.

| Standard | Summary |
|----------|---------|
| `DIDERM_DOMAIN_ARCHITECTURE.md` | Domain trust barriers (`primals.eco` / `primal.eco` / `nestgate.io`) + sovereignty evolution roadmap |
| `DARK_FOREST_GLACIAL_GATE_STANDARD.md` | 5 security invariants |
| `K_DERM_TOPOLOGY_STANDARD.md` | Cell envelope model (layers, bonding, channels) |
| `BONDING_MODEL_STANDARD.md` | Organo-metallo-salt bonding model |
| `SOVEREIGNTY_STANDARDS.md` | Calibrate → shadow → cutover protocol |
| `OVERWATCH_POSITION_STANDARD.md` | Floating coordination position |
| `LICENSING_AND_COPYLEFT.md` | scyBorg copyleft framework |
| `PRIMAL_SPRING_GARDEN_TAXONOMY.md` | Primal / spring / garden / tool taxonomy |
| `SECRETS_AND_SEEDS_STANDARD.md` | Seed and credential management |

### `protocols/` — Wire Protocols & IPC (10 standards)

Stable once shipped — wire formats, capability system, coordination patterns.

| Standard | Summary |
|----------|---------|
| `BTSP_PROTOCOL_STANDARD.md` | BearDog Trust Security Protocol |
| `RIBOCIPHER_TRANSPORT_SIGNAL_STANDARD.md` | Transport signal routing (3 tiers) |
| `CAPABILITY_WIRE_STANDARD.md` | Capability-based wire format |
| `CAPABILITY_BASED_DISCOVERY_STANDARD.md` | Runtime capability discovery |
| `CAPABILITY_DOMAIN_REGISTRY.md` | Canonical domain namespace registry |
| `SEMANTIC_METHOD_NAMING_STANDARD.md` | `domain.verb` API naming |
| `IMPULSE_POTENTIAL_STANDARD.md` | Inter-gate impulse/potential coordination |
| `CONTEXT_BRAID_STANDARD.md` | Ephemeral developer-state weaving |
| `ECOSYSTEM_COMMUNICATION_STANDARD.md` | Three-layer coordination (git + impulses + braids) |
| `PROVENANCE_TRIO_INTEGRATION_GUIDE.md` | rhizoCrypt + loamSpine + sweetGrass wiring |

### `operations/` — Gate Deployment & Mesh Ops (12 standards)

Evolve with infrastructure — deployment, ownership, gate operations.

| Standard | Summary |
|----------|---------|
| `GATE_SETUP_STANDARD.md` | Gate setup, sync, resync protocol |
| `GATE_NUCLEUS_SYSTEMD_STANDARD.md` | systemd deployment standard |
| `GATEHOUSE_DARKFOREST_STANDARD.md` | Drawbridge + Dark Forest demarcation |
| `GRAPHENEGATE_BOOTSTRAP_STANDARD.md` | Android Dark Forest bootstrap |
| `MESH_DEPLOYMENT_STANDARD.md` | Multi-gate mesh handoff |
| `DEPLOYMENT_VALIDATION_STANDARD.md` | Deployment validation protocol |
| `DISTRIBUTED_COVALENT_DEPLOYMENT.md` | Multi-gate compute architecture |
| `GATE_SPRING_OWNERSHIP.md` | Canonical gate-spring routing |
| `GATE_TEAM_COORDINATION_MATRIX.md` | Team-gate-hardware assignment |
| `REPO_MEMBRANE_BOUNDARY.md` | Inner/outer membrane repo classification |
| `DISCOVERED_BY_STANDARD.md` | Discovery narrative standard |
| `SPORE_OWNERSHIP_MATRIX.md` | Spore/gate ownership assignments |

### `compositions/` — Composition Patterns (6 standards)

Evolve with products — routing, health, tick models.

| Standard | Summary |
|----------|---------|
| `COMPOSITION_ROUTING_STANDARD.md` | Live composition deployment (wildcard DNS, drawbridge, CAS) |
| `COMPOSITION_HEALTH_STANDARD.md` | Composition health JSON-RPC |
| `COMPOSITION_TICK_MODEL_STANDARD.md` | Temporal tick model for compositions |
| `CROSS_SPRING_COORDINATION_STANDARD.md` | Cross-spring data flow |
| `MEMBRANE_CHANNEL_ARCHITECTURE.md` | 3 channels + RustDesk |
| `PRIMAL_REGISTRY.md` | Authoritative primal/spring catalog |

### Per-Domain Guidance
- `birdsong/` — BirdSong protocol, Dark Forest beacon genetics, Tower Atomic TLS
- `btsp/` — BearDog technical stack
- `sporePrint/` — Content guide + spring evolution targets
- `petaltongue/` — Integration docs (7 files)
- `airspring/` — Composition guidance
- `healthspring/` — Composition guidance
- `compute-sharing/` — Sovereign compute sharing + workload definitions

### Infrastructure
- `provision/` — golgi provisioning scripts + Caddyfiles
- `systemd/` — Service templates + cascade timers
- `graphs/` — Declarative deploy graph TOMLs
- `heads/` — Auto-published gate status files

### Handoffs
- `handoffs/ECOSYSTEM_BLURB.md` — Current wave blurb (dissemination artifact)
- `handoffs/ABG_JUPYTERHUB_ACCESS_GUIDE.md` — Collaborator access guide

### Fossil Record
- `fossilRecord/` — All archived content: 4,100+ documents across Waves 34–150s
- `fossilRecord/wave150s_standards/` — 8 fossilized standards (superseded or dimension-complete)

---

## For New Primals

If you are a new primal entering the ecosystem:

1. **Read this document** to understand the ecosystem you are joining
2. **Review `compositions/PRIMAL_REGISTRY.md`** to see what capabilities already exist
3. **Follow UniBin standard** from day one (single binary, subcommands)
4. **Target ecoBin** (Pure Rust, zero C deps, cross-compilation)
5. **Implement IPC** following `protocols/CAPABILITY_WIRE_STANDARD.md` (JSON-RPC 2.0)
6. **Advertise capabilities** so biomeOS can discover and coordinate you
7. **Register your primal** in `compositions/PRIMAL_REGISTRY.md` with your primitives
8. **Get your face together** — your repo should be reviewable by any of the four external audiences in 5 minutes (see `STANDARDS_AND_EXPECTATIONS.md`)

You do not need to know about other primals. You need to know what you can do, and how to tell the ecosystem about it.

---

## Getting Your Face Together

Every spring and primal should be independently reviewable by outsiders.
See **`STANDARDS_AND_EXPECTATIONS.md`** for the full checklist,
but the short version is: a reviewer should be able to do this in 5 minutes:

1. Open `README.md` → understand what this does and what it replaces
2. `cargo test --workspace` → see all tests pass
3. `cargo run --release --bin validate_<something>` → see explicit PASS/FAIL
4. Open `CHANGELOG.md` → understand recent evolution
5. Open `whitePaper/baseCamp/README.md` → see the faculty and science context

Four external audiences will read your repo without context:

| Audience | What They Look For |
|----------|-------------------|
| **Faculty / PIs** | What does this replace? How does it compare to commercial tools? Can I verify claims? |
| **Students / Core Facilities** | How do I build it? How do I run it? Where do I start? |
| **Hardware Builders / Hobbyists** | What hardware does it need? What can my GPU do? How do I contribute compute? |
| **Compliance / Institutional Review** | What standards does it meet? What are the dependencies? Is it safe? What's the license? |

The `publicRelease/` documents in `whitePaper/attsi/non-anon/contact/publicRelease/`
make ecosystem-wide claims. Each spring and primal must ensure its own presentation
supports those claims.

---

**The Watering Hole is maintained by all primals. Every primal's evolution strengthens the whole ecosystem.**

---

## FILE: `sporePrint/CONTENT_GUIDE.md`

# sporePrint Content Guide

How springs, primals, and products publish their science to [primals.eco](https://primals.eco).

**Audience**: Upstream maintainers who want their baseCamp science, validation results, or documentation visible on the public site.

---

## Two Tiers of Content

### Tier 1: Metrics (automatic)

When you push to `main`/`master`, the `notify-sporeprint.yml` workflow fires a `repository_dispatch` to sporePrint. sporePrint auto-updates `config.toml` with your latest LOC, tests, files, and crates. No human intervention.

**You already have this** if your repo was onboarded (see [ONBOARDING.md](https://github.com/ecoPrimals/sporePrint/blob/main/ONBOARDING.md)).

### Tier 2: Content (PR for review)

To publish markdown pages to primals.eco, create a `sporeprint/` directory in your repo. On push, if your dispatch payload includes `"content": "true"`, sporePrint's CI will extract markdown from `sporeprint/` and create a PR for human review.

```
your-repo/
  sporeprint/
    my-validation-results.md    ← becomes a page on primals.eco
    my-gpu-benchmarks.md        ← another page
```

To enable Tier 2, update your `notify-sporeprint.yml` payload:

```yaml
client-payload: '{"source": "${{ github.event.repository.name }}", "sha": "${{ github.sha }}", "type": "spring", "content": "true"}'
```

---

## Spring Science Hub Pages

Each spring should have a science hub page at `content/lab/springs/<springname>.md` on sporePrint. Four exemplars exist (wetSpring, hotSpring, airSpring, healthSpring). Use them as templates.

### Required Front Matter

```toml
+++
title = "yourSpring — Domain Summary"
description = "One-line description with key numbers"
date = 2026-05-06
weight = 5

[taxonomies]
primals = ["barracuda", "toadstool"]  # primals your spring validates
springs = ["yourspring"]               # always include yourself + connected springs
+++
```

### Recommended Sections

1. **Domain** — one sentence + repository link
2. **The Science Story** — 2-3 paragraphs: what you proved, why it matters
3. **Headline Results** — bullet list of your strongest numbers
4. **Validation Phases** — table of phases with key results
5. **Researchers Reproduced** — table: researcher, department, domain
6. **What the Constraint Revealed** — what eliminating dependencies taught you
7. **Cross-Spring Connections** — how your spring feeds/consumes others
8. **baseCamp Papers** — which papers your spring contributed to

---

## Adding Papers to /science/

baseCamp papers live in `content/science/` on sporePrint. Each paper is a standalone markdown file.

### Front Matter Template

```toml
+++
title = "baseCamp Paper XX — Title"
description = "Brief abstract"
date = 2026-05-06

[taxonomies]
primals = ["barracuda", "toadstool"]
springs = ["wetspring", "hotspring"]
+++
```

### Taxonomy Tagging

**Every page must include taxonomy tags** in its front matter. This is how cross-referencing works on primals.eco:

- `primals = [...]` — lowercase, no spaces: `barracuda`, `toadstool`, `biomeos`, `nestgate`, `songbird`, `rhizocrypt`, `loamspine`, `sweetgrass`, `squirrel`, `coralreef`, `skunkbat`, `petaltongue`, `beardog`, `bingocube`, `sourdough`
- `springs = [...]` — lowercase, no spaces: `airspring`, `groundspring`, `healthspring`, `hotspring`, `ludospring`, `neuralspring`, `primalspring`, `wetspring`

The taxonomy pages (`/primals/barracuda/`, `/springs/wetspring/`) automatically aggregate every page that references them.

---

## Notebook Content — Full Pipeline

Jupyter notebooks are the primary science visibility mechanism. The full
pipeline from notebook to live public page is:

```
your-spring/notebooks/*.ipynb     ← frozen data, matplotlib charts
        │
        ├─ git push to main
        │       └─ notify-sporeprint.yml fires (content: "true")
        │
        ├─ sporePrint auto-refresh.yml (CI)
        │       ├─ clones your repo
        │       ├─ pip install jupyter nbconvert matplotlib numpy
        │       ├─ jupyter nbconvert --execute (runs all cells)
        │       └─ wraps output HTML in Zola front matter
        │
        └─ primals.eco/lab/notebooks/<slug>.md  ← live on the public site
```

### Creating Notebooks (follow the exemplar pattern)

Three springs now have live notebooks — use any as a reference:
- **wetSpring** (5 notebooks) — domain science (16S, LC-MS, diversity)
- **primalSpring** (5 notebooks) — meta-validation (compositions, BTSP, cross-spring)
- **hotSpring** (17 notebooks) — paper reproductions (22 QCD papers)

1. Create `notebooks/` directory in your spring repository
2. Copy `NOTEBOOK_PATTERN.md` from wetSpring or primalSpring
3. Load frozen data from `../experiments/results/*.json` (relative paths)
4. Use `matplotlib` for charts — **do NOT set `matplotlib.use('Agg')`** (breaks inline rendering)
5. End each notebook with a provenance summary linking to primals.eco

The recommended set (5 notebooks):
- `01-domain-validation.ipynb` — flagship validation story
- `02-benchmark-comparison.ipynb` — Python vs Rust vs GPU
- `03-paper-reproductions.ipynb` — per-researcher evidence
- `04-cross-spring-connections.ipynb` — ecosystem flows
- `05-domain-deep-dive.ipynb` — your most compelling discovery

### Local Rendering

```bash
cd infra/sporePrint
cargo run --manifest-path crates/spore-validate/Cargo.toml -- render-notebooks --notebook /path/to/notebook.ipynb
```

### Automated Rendering (CI)

When your dispatch payload includes `"content": "true"`, the auto-refresh
CI will:
1. Clone your repo
2. Install jupyter/matplotlib
3. Execute and render all `notebooks/*.ipynb`
4. Create a PR with the rendered pages

Rendered notebooks appear at `primals.eco/lab/notebooks/<slug>/` with
embedded PNG charts, data tables, and cross-references.

### Live Example

wetSpring's 5 notebooks are live at:
- [16S Pipeline Validation](https://primals.eco/lab/notebooks/01-16s-pipeline-validation/)
- [Python vs Rust vs GPU](https://primals.eco/lab/notebooks/02-benchmark-python-vs-rust/)
- [Paper Reproductions](https://primals.eco/lab/notebooks/03-paper-reproductions/)
- [Cross-Spring Connections](https://primals.eco/lab/notebooks/04-cross-spring-connections/)
- [Soil Anderson Deep Dive](https://primals.eco/lab/notebooks/05-soil-anderson-deep-dive/)

---

## The `sporeprint/` Directory Convention

```
your-repo/
  sporeprint/
    README.md           ← describes what's being published
    validation-summary.md ← validation results page
  notebooks/
    NOTEBOOK_PATTERN.md ← convention docs
    01-validation.ipynb ← loads ../experiments/results/*.json
    02-benchmarks.ipynb
```

Files are placed in sporePrint at paths determined by the auto-refresh CI. The PR created for review lets maintainers adjust placement.

---

## Quick Checklist

- [ ] Repo is onboarded ([ONBOARDING.md](https://github.com/ecoPrimals/sporePrint/blob/main/ONBOARDING.md))
- [ ] `notify-sporeprint.yml` installed with correct `type` (primal/spring/product)
- [ ] `SPOREPRINT_DISPATCH_TOKEN` secret set in your repo
- [ ] Taxonomy tags in all markdown front matter
- [ ] Science hub page created (springs) or entity registry entry present (primals/products)
- [ ] For Tier 2: `sporeprint/` directory created, `content: "true"` in dispatch payload

---

## Reference

- [ONBOARDING.md](https://github.com/ecoPrimals/sporePrint/blob/main/ONBOARDING.md) — CI pipeline setup
- [sporePrint README](https://github.com/ecoPrimals/sporePrint/blob/main/README.md) — auto-refresh architecture
- [SPRING_CATALOG.md](https://primals.eco/architecture/spring-catalog-status-science-and-evolution/) — full spring data
- [Lab](/lab/) — where published results appear

---

## FILE: `sporePrint/SPRING_EVOLUTION_TARGETS.md`

# Spring Evolution Targets

How springs evolve from CLI validation to fully live science on primals.eco.

**Audience**: Spring maintainers planning their next iteration.

---

## The Convergence Path

```
Tier 0: CLI binary         → stdout [OK]/[FAIL]
Tier 1: + notebook         → parse CLI output, matplotlib, exported HTML
Tier 2: + JSON-RPC methods → notebooks call primals directly, structured data
Tier 3: + petalTongue      → live web dashboards rendered from primal APIs
Standalone:                → NestGate serves content, sporePrint self-hosted on NUCLEUS
```

Each tier adds capability without removing previous tiers. A spring at Tier 0
continues to work when Tier 2 APIs exist. You always have a working system.

---

## What to Do Now (Tier 0 → Tier 1)

### 1. Fill Your `sporeprint/` Directory

Every spring now has a `sporeprint/` directory with starter content.
This is your publishing pipeline to [primals.eco](https://primals.eco).

```
your-spring/
  sporeprint/
    README.md                  ← explains the directory (already created)
    validation-summary.md      ← headline results stub (already created — fill in real data)
    additional-pages.md        ← add more as your science grows
```

**Validation summary template** (already in your repo):

```toml
+++
title = "yourSpring Validation Summary"
description = "One-line summary of your spring's results"
date = 2026-05-06

[taxonomies]
primals = ["barracuda", "toadstool"]    # primals your spring uses
springs = ["yourspring"]                 # your spring + cross-spring refs
+++

## Status

- **N checks** across M experiments — all passing
- **X papers** reproduced with full provenance

## Key Validation Binaries

- `validate_your_domain` — what it does
```

### 2. Create a Workload TOML

Add a workload TOML to `projectNUCLEUS/workloads/yourspring/`:

```toml
[metadata]
name = "yourspring-validation"
description = "What this workload validates"
version = "0.1.0"

[execution]
type = "native"
command = "/path/to/your/target/release/validate_binary"
working_dir = "/path/to/your/spring"

[resources]
max_memory_bytes = 4294967296
max_cpu_percent = 80.0

[security]
isolation_level = "None"
```

This lets ToadStool dispatch your validation on any gate running NUCLEUS.

### 3. Create Public Notebooks

Create a `notebooks/` directory in your spring repository with public-facing
science notebooks. Three exemplars exist:
- **wetSpring** (domain science) — [NOTEBOOK_PATTERN.md](https://github.com/syntheticChemistry/wetSpring/blob/main/notebooks/NOTEBOOK_PATTERN.md)
- **primalSpring** (meta-validation) — [NOTEBOOK_PATTERN.md](https://github.com/syntheticChemistry/primalSpring/blob/main/notebooks/NOTEBOOK_PATTERN.md)
- **hotSpring** (paper notebooks) — [PAPER_NOTEBOOK_GUIDE.md](https://github.com/syntheticChemistry/hotSpring/blob/main/notebooks/PAPER_NOTEBOOK_GUIDE.md)

The recommended set (adapt from the exemplars):

1. **01-domain-validation.ipynb** — your flagship validation story
2. **02-benchmark-comparison.ipynb** — Python vs Rust vs GPU timing
3. **03-paper-reproductions.ipynb** — per-researcher evidence map
4. **04-cross-spring-connections.ipynb** — ecosystem flows and discoveries
5. **05-domain-deep-dive.ipynb** — your most compelling cross-domain insight

Key conventions:
- Load frozen data from `../experiments/results/*.json` (no live primals needed)
- Use `matplotlib` for charts — do NOT set `matplotlib.use('Agg')` (breaks inline rendering
  in JupyterHub and nbconvert CI; see CONTENT_GUIDE.md)
- Include a "for other springs" adaptation note in each title cell
- End with a provenance/summary cell linking to primals.eco

For live-dispatch notebooks, also use `projectNUCLEUS/notebooks/spring-validation-template.ipynb`
which handles health-checking, workload dispatch, and ToadStool integration.

### 4. Trigger Auto-Refresh

When you push to `main`, your `notify-sporeprint.yml` workflow fires.
To include content updates, set `"content": "true"` in the dispatch payload:

```yaml
# In your .github/workflows/notify-sporeprint.yml
client_payload: '{"source":"yourspring","content":"true"}'
```

sporePrint CI will clone your repo, copy `sporeprint/*.md` to `content/lab/`,
and create a PR for review.

---

## What to Evolve Toward (Tier 1 → Tier 2)

### JSON-RPC Method Targets

These methods are specified in `projectNUCLEUS/specs/LIVE_SCIENCE_API.md`.
When your primals implement them, notebooks call primals directly:

| Method | Owner | What It Does |
|--------|-------|-------------|
| `toadstool.validate` | ToadStool | Dispatch workload → structured JSON results |
| `toadstool.list_workloads` | ToadStool | Auto-discover available workloads |
| `biomeos.spring_status` | biomeOS | Which springs have binaries on this gate |
| `barracuda.compute` | barraCuda | Direct GPU compute request |
| `nestgate.artifact_query` | NestGate | Provenance chain for an artifact hash |
| `rhizocrypt.dag_summary` | rhizoCrypt | DAG session summary |

**Priority**: `toadstool.validate` and `toadstool.list_workloads` are P0 —
they unlock Tier 2 for every spring simultaneously.

### What Changes for Springs

At Tier 2, your validation binaries gain a `--format json` flag (or equivalent)
that outputs structured results instead of `[OK]/[FAIL]` text. ToadStool wraps
this into `toadstool.validate`.

```
Current:  binary → stdout → notebook parses text
Tier 2:   binary → json → toadstool.validate → notebook gets data
```

Your binary still works standalone. The JSON output is additive.

---

## What Comes After (Tier 3 → Standalone)

### Tier 3: petalTongue Live Dashboards

petalTongue reads Tier 2 APIs and renders web dashboards. Your spring gets a
live page on primals.eco that updates in real time as validation runs.

**What springs need**: Nothing — if your data flows through Tier 2 APIs,
petalTongue can render it.

### Standalone: Self-Hosted Science

When Phase 3 converges:

1. NestGate serves sporePrint content directly (no GitHub Pages)
2. petalTongue renders live dashboards from the running composition
3. rhizoCrypt/loamSpine/sweetGrass provide provenance for every result
4. The entire site runs on the same hardware as the science

**What springs need**: Nothing new — standalone is an infrastructure
evolution, not a spring interface change.

---

## Checklist for Spring Maintainers

- [ ] Fill `sporeprint/validation-summary.md` with real data
- [ ] Create additional `sporeprint/*.md` pages as science grows
- [ ] Create workload TOML(s) in `projectNUCLEUS/workloads/yourspring/`
- [ ] Customize notebook from template
- [ ] Set `"content": "true"` in notify-sporeprint dispatch payload
- [ ] Add `--format json` to validation binaries (Tier 2 prep)
- [ ] Review `LIVE_SCIENCE_API.md` for target method signatures

---

## Cross-References

- [CONTENT_GUIDE.md](CONTENT_GUIDE.md) — how to write sporePrint content
- [ONBOARDING.md](https://github.com/ecoPrimals/sporePrint/blob/main/ONBOARDING.md) — new repo onboarding checklist
- [LIVE_SCIENCE_API.md](https://github.com/sporeGarden/projectNUCLEUS/blob/main/specs/LIVE_SCIENCE_API.md) — full JSON-RPC method specs
- [NOTEBOOK_ELEVATION.md](https://github.com/sporeGarden/projectNUCLEUS/blob/main/specs/NOTEBOOK_ELEVATION.md) — notebook tier definitions

---

## FILE: `STANDARDS_AND_EXPECTATIONS.md`

# ecoPrimals — Standards & Expectations Index

**Purpose**: Single-document reference for what ecoPrimals expects of every primal,
spring, contributor, and session.  Read this first, read everything else second.

**Last Updated**: July 21, 2026 (Wave 150s — standards reorganized into `foundations/`, `protocols/`, `operations/`, `compositions/`)

---

## Companion Documents

- **`GLOSSARY.md`** — Every term defined (gate, primal, spring, atomic, niche, etc.)
- **`operations/GATE_SPRING_OWNERSHIP.md`** — Gate-spring routing SSOT: ownership, hardware profiles, covalent evolution path
- **`TARGETED_GUIDESTONE_STANDARD.md`** — Self-contained scientific artifact packaging (USB/ecoBin)
- **`DERIVATION_ANCHORING_STANDARD.md`** — Zero Magic Numbers: all numeric thresholds must be formally derived and runtime-enforced
- **`LITHOSPORE_USB_DEPLOYMENT.md`** — Spore taxonomy: ColdSpore → LiveSpore → lithoSpore
- **`PSEUDOSPORE_STANDARD.md`** — (canonical: `gardens/lithoSpore/specs/`) Braid-first proof artifacts
- **`compositions/PRIMAL_REGISTRY.md`** — Authoritative primal/spring version catalog
- **`protocols/ECOSYSTEM_COMMUNICATION_STANDARD.md`** — Three-layer coordination model (git/impulses/context)
- **`protocols/IMPULSE_POTENTIAL_STANDARD.md`** — Inter-gate action potentials (rootPulse/quorumSignal)
- **`protocols/CONTEXT_BRAID_STANDARD.md`** — Ephemeral developer-state weaving
- **`operations/GATE_SETUP_STANDARD.md`** — Gate setup, sync, and resync

---

## 1. Language & Toolchain

| Expectation | Detail |
|-------------|--------|
| **Language** | Rust — 100% application code. No C, no C++, no Python in production binaries. |
| **Edition** | Rust 2024 (`edition = "2024"` in Cargo.toml) |
| **Linting** | `clippy::pedantic` + `clippy::nursery` — ZERO warnings, all-features. Non-negotiable. |
| **Unsafe** | `#![forbid(unsafe_code)]` on all crate roots unless hardware-touching (coralReef VFIO, toadStool sysmon). Justify every exception. |
| **Dependencies** | Minimize. Prefer `no_std`-capable crates. No openssl, no ring, no vendor SDKs. Pure Rust cryptography (RustCrypto suite). |
| **Documentation** | `#![warn(missing_docs)]` on library crates. Doctests count as tests. |
| **License** | AGPL-3.0-only for all primals and springs. See `SCYBORG_PROVENANCE_TRIO_GUIDANCE.md` for full licensing standard. |

## 2. Binary Architecture

Every binary follows the **evolutionary ladder**:

```
UniBin   (structure)    → One binary, multiple modes (subcommands, --help, --version)
  ↓
ecoBin   (portability)  → + Pure Rust, cross-compilation, platform-agnostic IPC
  ↓
genomeBin (deployment)  → + Auto-detection, service integration, health monitoring
```

| Standard | File | Status |
|----------|------|--------|
| UniBin | `UNIBIN_ARCHITECTURE_STANDARD.md` | Ecosystem Standard |
| ecoBin | `fossilRecord/wave150s_standards/ECOBIN_ARCHITECTURE_STANDARD.md` | Ecosystem Standard v3.0 (fossilized — stable since v3.0) |
| genomeBin | `GENOMEBIN_ARCHITECTURE_STANDARD.md` | Ecosystem Standard |

**Expectation**: Every primal is a single self-contained binary. No shared libraries,
no plugins, no dynamic loading. `cargo build --release` produces one artifact.

### Genome Pinning (`plasmidBin/`)

When a primal or spring reaches a stable release, its genomeBin is pinned to
`ecoPrimals/plasmidBin/`. This is the ecosystem-wide source of truth for
production-ready binaries. Springs and biomeOS discover primal binaries from
this directory via the `$ECOPRIMALS_PLASMID_BIN` discovery chain.

| Layer | Location | Role |
|-------|----------|------|
| genomeBin | `wateringHole/genomeBin/` | Distribution manifest, checksums, update policy |
| biomeOS plasmidBin | `phase2/biomeOS/plasmidBin/` | Local cache for spore creation |
| Root plasmidBin | `ecoPrimals/plasmidBin/` | Ecosystem-wide stable genomes |

**Standard practice**: After a successful audit or milestone, copy the release
binary to `plasmidBin/primals/{name}` (for primals) or `plasmidBin/springs/{name}`
(for springs), and update `plasmidBin/manifest.toml` + `plasmidBin/sources.toml`.

## 3. Communication (IPC + Inter-Gate Coordination)

| Standard | File | Summary |
|----------|------|---------|
| Primal IPC Protocol v3.0 | `PRIMAL_IPC_PROTOCOL.md` | JSON-RPC 2.0 + tarpc, platform-agnostic transports, runtime discovery |
| Semantic Method Naming | `protocols/SEMANTIC_METHOD_NAMING_STANDARD.md` | `domain.verb` method names (`crypto.sign`, `storage.put`) |
| Cross-Spring Data Flow | `CROSS_SPRING_DATA_FLOW_STANDARD.md` | Time series exchange format via `capability.call` |
| Ecosystem Communication | `protocols/ECOSYSTEM_COMMUNICATION_STANDARD.md` | Three-layer coordination: git (permanent) + impulses (events) + context braids (state) |
| impulsePotential | `protocols/IMPULSE_POTENTIAL_STANDARD.md` | Inter-gate action potentials mapped to Neural API Triad (rP/qS/wF) |
| Context Braids | `protocols/CONTEXT_BRAID_STANDARD.md` | Ephemeral developer-state weaving across the gate mesh |

**Expectation**: Primals never import each other's code. All coordination is via
JSON-RPC messages over IPC. Each primal owns its IPC implementation — no shared
IPC crate.

**Inter-gate coordination** uses the three-layer model:

| Layer | Pattern | Lifetime | Biological analog |
|-------|---------|----------|-------------------|
| Git commits | Linear, permanent | Forever | loamSpine ledger |
| Impulses | Event DAG, time-bounded | Archived per wave | rhizoCrypt sessions |
| Context braids | Woven strands, superseding | TTL-based auto-decay | sweetGrass braids |

**CLI surface**: `membrane impulse.post/ack/archive`, `membrane potential.sense/check`,
`membrane context.weave/sense/clear`. All registered in `capability_registry.toml`
with primal graduation path (bearDog signing, songbird relay, sweetGrass anchoring).

## 4. Security

| Standard | File | Summary |
|----------|------|---------|
| Dark Forest Beacon Genetics | `birdsong/DARK_FOREST_BEACON_GENETICS_STANDARD.md` | Two-seed lineage (nuclear + mitochondrial) |
| BearDog Technical Stack | `btsp/BEARDOG_TECHNICAL_STACK.md` | Ed25519, BLAKE3, X25519 — Pure Rust crypto foundation |
| Tower Atomic | `birdsong/SONGBIRD_TLS_TOWER_ATOMIC_INTEGRATION_GUIDE.md` | BearDog + Songbird = Pure Rust HTTPS |

**Expectation**: Auto-trust within genetic family, zero trust outside. No certificate
authorities. Encrypted payloads are unreadable to outsiders. Zero metadata leakage
(Dark Forest protocol).

## 5. GPU & Numerical Computing

| Standard | File | Summary |
|----------|------|---------|
| GPU f64 Stability | `GPU_F64_NUMERICAL_STABILITY.md` | Lessons from hotSpring Paper 44 — precision tiers |
| Numerical Stability Plan | `NUMERICAL_STABILITY_EVOLUTION_PLAN.md` | Fast AND safe math — fallback chains |
| Sovereign Compute | `SOVEREIGN_COMPUTE_EVOLUTION.md` | Pure Rust GPU stack — WGSL→native, no CUDA SDK |
| Pure Rust Stack | `fossilRecord/wave150s_standards/PURE_RUST_SOVEREIGN_STACK_GUIDANCE.md` | Cross-primal sovereign compute guidance (fossilized) |
| Cross-Spring Shaders | `CROSS_SPRING_SHADER_EVOLUTION.md` | How springs collectively evolve barraCuda |
| Spring Validation | `SPRING_VALIDATION_ASSIGNMENTS.md` | Each spring validates specific barraCuda primitives |

**Compute triangle**: barraCuda (WHAT — math/shaders) → coralReef (HOW — compile to native)
→ toadStool (WHERE — discover and dispatch hardware). Springs depend on barraCuda
directly for math.

**Expectation**: All WGSL shaders are f64-canonical. Precision dispatch per hardware
(f16/f32/f64/DF64). Springs never write local WGSL — absorb upstream from barraCuda.

## 6. Spring Standards

| Standard | File | Summary |
|----------|------|---------|
| Spring-as-Niche Standard | `SPRING_AS_NICHE_DEPLOYMENT_STANDARD.md` | Springs deploy as biomeOS niches |
| Spring-as-Niche Guide | `SPRING_NICHE_DEPLOYMENT_GUIDE.md` | How to evolve a spring into a deployable niche |
| Spring-as-Provider | `SPRING_AS_PROVIDER_PATTERN.md` | biomeOS capability registration pattern |
| Provenance Trio Integration | `SPRING_PROVENANCE_TRIO_INTEGRATION_PATTERN.md` | rhizoCrypt + loamSpine + sweetGrass integration |
| Spring Evolution Issues | `SPRING_EVOLUTION_ISSUES.md` | Active issues discovered by springs |

**Expectation**: Every spring has its own git repo, its own `Cargo.toml`, its own
`specs/PAPER_REVIEW_QUEUE.md`. Springs reproduce published papers at paper parity.
Every experiment gets a number, every check gets counted. No hand-waving.

## 7. Primal Coordination

| Document | File | Summary |
|----------|------|---------|
| Primal Registry | `compositions/PRIMAL_REGISTRY.md` | Authoritative catalog of every primal + primitives |
| Inter-Primal Interactions | `INTER_PRIMAL_INTERACTIONS.md` | What works today, what's wired, what's next |
| Lysogeny Protocol | `LYSOGENY_PROTOCOL.md` | Area denial through open prior art (AGPL-3.0) |
| scyBorg Licensing | `SCYBORG_PROVENANCE_TRIO_GUIDANCE.md` | AGPL + ORC + CC-BY-SA ecosystem licensing |
| Novel Ferment Transcript | `NOVEL_FERMENT_TRANSCRIPT_GUIDANCE.md` | NFT architecture (memory-bound digital objects) |
| Upstream Contributions | `UPSTREAM_CONTRIBUTIONS.md` | Standalone crates for crates.io |

## 8. Leverage Guides (Per-Primal)

Each primal has a leverage guide describing standalone, trio, and ecosystem compositions:

| Guide | Primal |
|-------|--------|
| `BARRACUDA_LEVERAGE_GUIDE.md` | barraCuda |
| `BIOMEOS_LEVERAGE_GUIDE.md` | biomeOS |
| `CORALREEF_LEVERAGE_GUIDE.md` | coralReef |
| `LOAMSPINE_LEVERAGE_GUIDE.md` | loamSpine |
| `RHIZOCRYPT_LEVERAGE_GUIDE.md` | rhizoCrypt |
| `SQUIRREL_LEVERAGE_GUIDE.md` | Squirrel |
| `SWEETGRASS_LEVERAGE_GUIDE.md` | sweetGrass |
| `TOADSTOOL_LEVERAGE_GUIDE.md` | toadStool |
| `petaltongue/` | petalTongue (integration docs) |

## 9. Handoffs

Session handoffs live in `handoffs/`. They are the working memory between sessions —
what was done, what's next, what broke, what was discovered.

- **Active**: `handoffs/*.md` — current work items (last 48 hours)
- **Fossil record**: `handoffs/archive/` — completed work, preserved for provenance

Handoffs are archived after ~48 hours or when superseded. They are never deleted.
The archive is the project's geological record.

## 10. Testing Expectations

| What | Expectation |
|------|-------------|
| **Unit tests** | Every module has tests. `cargo test` passes with zero failures. |
| **Forge tests** | Integration/forge tests for cross-module behavior. |
| **Python cross-validation** | For scientific springs: Python reference implementations validate Rust output at paper parity. |
| **Named tolerances** | Every numerical comparison uses a named tolerance constant (e.g., `PLANCK_TEMPERATURE_REL_TOL`), not magic numbers. GuideStone artifacts: full derivation anchoring per `DERIVATION_ANCHORING_STANDARD.md`. |
| **Clippy** | `clippy::pedantic` + `clippy::nursery`, zero warnings, all features enabled. |
| **CI** | `cargo test --all-features`, `cargo clippy --all-features -- -D warnings`. |
| **Coverage** | Track and increase. Minimum varies by maturity — new primals target 80%+. |

## 11. Documentation Expectations

| What | Where |
|------|-------|
| **Root README** | Every repo has one. States what it is, what it does, current version. |
| **specs/** | Paper review queues, experiment designs, scientific specs. |
| **CHANGELOG** or session notes | What changed, when, why. |
| **Handoffs** | Session continuity lives in wateringHole `handoffs/`. |
| **baseCamp** | Cross-spring papers live in `whitePaper/gen3/baseCamp/`. |
| **attsi/** | Faculty contact packages and outreach plans. |

## 12. Code Style

| Rule | Detail |
|------|--------|
| No TODO/FIXME/HACK in committed code | Track in handoffs or issues instead. |
| No files >1000 lines | Split into modules. |
| No commented-out code | Delete it; git remembers. |
| Semantic naming | Functions say what they do. Variables say what they hold. |
| Error handling | `Result<T, E>` everywhere. No `.unwrap()` in library code. `thiserror` for typed errors. |
| Feature gates | Use Cargo features to gate optional functionality. |

---

## 13. External Claims & Maturity Labeling

| Standard | File | Status |
|----------|------|--------|
| External Claim Convergence | `foundations/EXTERNAL_CLAIM_CONVERGENCE_STANDARD.md` | Ecosystem Standard (Wave 150x) |

**Expectation**: Every public-facing README includes an external maturity label
(`experimental`, `research-ready`, `deployment-ready`, `production-candidate`,
`externally-validated`) and a metrics measurement date. Internal evolutionary
grades (stadial, wave, A++) do not appear in the first 20 lines of public READMEs.
All absolute claims (`zero`, `all`, `every`, `no`) state their scope in the same
sentence. See the standard for full details.

---

## Quick Reference: "Is my work ready?"

Before pushing, verify:

- [ ] `cargo test --all-features` — zero failures
- [ ] `cargo clippy --all-features -- -D warnings` — zero warnings
- [ ] `cargo doc --all-features --no-deps` — zero doc warnings
- [ ] No TODO/FIXME/HACK in committed code
- [ ] No files >1000 lines
- [ ] Named tolerances for all numerical comparisons
- [ ] Experiment checks counted and reported
- [ ] Handoff written if session work is incomplete

---

## FILE: `wave.toml`

# SPDX-License-Identifier: CC-BY-SA-4.0
#
# wave.toml — Ecosystem wave coordination (single writer: overwatch)
#
# Authority: eastGate overwatch (sole writer — no other gate modifies this file)
# Consumed by: all gates, membrane temporal.cascade --check, s_ecosystem_freshness
#
# This file tracks the human-authored wave state. Per-gate HEAD SHAs live in
# heads/<gate>.toml (each gate writes only its own file — zero conflicts).

[wave]
id = 155
sub = "i"
date = "2026-07-29"
posture = "blueGate NEST 10/10 ON WINDOWS (first). westGate broker LIVE (704 caps, COORDINATED). strandGate Node Atomic (746 pipelines/sec). ZERO P0s. Windows depot stale (14 .exe 07/16). bearDog crypto blocks Provenance 7/7. 9 gates. ~63K+ tests. 27 signal graphs."
publisher = "eastGate-overwatch"

[gates]
online = ["sporeGate", "eastGate", "ironGate", "flockGate", "golgi", "grapheneGate", "northGate", "westGate", "strandGate", "blueGate"]
enrolling = ["swiftGate", "southGate"]
offline = []

