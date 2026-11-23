# petalTongue Spring Science Map

> Per-spring visualization channel mapping and live presentation vision.
> "The computation IS the presentation."

**Date**: May 5, 2026
**Version**: 1.0.0
**Depends on**: `VISUALIZATION_INTEGRATION_GUIDE.md` v2.1.0 (DataBinding spec)
**License**: AGPL-3.0-or-later

---

## Design Principle

Every spring's science output should be directly renderable by petalTongue
without manual figure generation. The IPC result from a NUCLEUS composition
IS the visualization input. When a spring rewires from library to binary-only,
the IPC response payloads become the natural DataBinding source — the
computation presents itself.

```
Spring science workflow (NUCLEUS composition)
    │ JSON-RPC result
    ▼
petalTongue DataBinding
    │ Grammar of Graphics auto-compilation
    ▼
Multi-modal output (GUI, TUI, SVG, audio, headless)
```

This map documents which petalTongue `channel_type` values express each
spring's science, what a live presentation looks like, and what gaps remain.

---

## Channel Type Reference

| Type | Fields | Stream Ops |
|------|--------|------------|
| `timeseries` | x_values, y_values, labels, unit | append |
| `distribution` | values, mean, std, comparison_value | replace |
| `bar` | categories, values, unit | replace |
| `gauge` | value, min, max, normal_range, warning_range | set_value |
| `heatmap` | x_labels, y_labels, values (row-major), unit | replace |
| `scatter` | x, y, point_labels, x_label, y_label, unit | replace |
| `scatter3d` | x, y, z, point_labels, unit | replace |
| `fieldmap` | grid_x, grid_y, values (row-major), unit | replace |
| `spectrum` | frequencies, amplitudes, unit | append |
| `game_scene` | scene JSON (tilemap/sprites or description/npcs/choices) | replace |
| `soundscape` | definition JSON (layers with waveform/frequency/amplitude) | replace |

---

## Per-Spring Science Mapping

---

### hotSpring — Lattice QCD / HPC Physics

**Current petalTongue status**: Not wired

| Science Output | Channel Type | Binding ID Pattern | Notes |
|---------------|-------------|-------------------|-------|
| Gauge field configurations | `heatmap` | `lattice-gauge-{config_id}` | 2D slice of SU(3) lattice; row-major plaquette values |
| HMC trajectory | `timeseries` | `hmc-trajectory-{run_id}` | Molecular dynamics steps on X, action/Hamiltonian on Y |
| Plaquette convergence | `timeseries` | `plaquette-convergence` | MC sweeps on X, average plaquette on Y; streaming append |
| Acceptance rate | `gauge` | `hmc-acceptance` | Value 0-1, normal_range [0.6, 0.8] |
| Phase diagram | `scatter3d` | `phase-diagram-{observable}` | Temperature, density, order parameter |
| Nuclear EOS curves | `timeseries` | `eos-{model}-{observable}` | Density on X, pressure/energy on Y |
| Gradient flow | `timeseries` | `gradient-flow-{config}` | Flow time on X, observable on Y |
| df64 precision comparison | `scatter` | `precision-{method}` | Library result vs IPC result; validates rewiring |
| Dielectric function | `spectrum` | `dielectric-{material}` | Frequency on X, response amplitude on Y |
| ESN reservoir state | `heatmap` | `esn-reservoir-{step}` | Neuron grid state at each timestep |

**Live presentation vision**: A running lattice QCD simulation streams plaquette
convergence as a `timeseries`, gauge field snapshots as `heatmap` frames, and
acceptance rate as a `gauge`. The HMC trajectory IS the figure in the paper.
The dashboard IS the reproducibility artifact — every panel is backed by a
provenance-tracked IPC call.

**Multi-panel dashboard**: `hotspring_qcd_dashboard`
- Row 1: `timeseries` (plaquette convergence) + `gauge` (acceptance rate)
- Row 2: `heatmap` (gauge field slice) + `timeseries` (gradient flow)
- Row 3: `scatter3d` (phase diagram)

**Gaps**:
- 3D volume rendering for full lattice (no channel type yet)
- Animation/frame sequences for time-evolved heatmaps (petalTongue supports
  session streaming but no explicit animation channel)

---

### wetSpring — Life Science & Analytical Chemistry

**Current petalTongue status**: Partial (referenced in integration docs)

| Science Output | Channel Type | Binding ID Pattern | Notes |
|---------------|-------------|-------------------|-------|
| Mass spectrometry | `spectrum` | `ms-{sample_id}` | m/z on X, intensity on Y |
| Spectral deconvolution | `spectrum` | `deconv-{sample_id}` | Overlaid raw + deconvolved peaks |
| Growth curves | `timeseries` | `growth-{organism}-{condition}` | Time on X, OD/CFU on Y; streaming append |
| Sensor streams | `timeseries` | `sensor-{station}-{metric}` | Live streaming from IoT |
| PCoA ordination | `scatter` / `scatter3d` | `pcoa-{dataset}` | PC1/PC2 (2D) or PC1/PC2/PC3 (3D); point_labels = sample IDs |
| Microbiome abundance | `bar` | `abundance-{sample}-{level}` | Genus/phylum categories |
| Shannon/Simpson diversity | `gauge` | `diversity-{index}-{sample}` | Normal ranges from literature |
| Drug dose-response | `timeseries` | `dose-response-{compound}` | Concentration on X, response on Y |
| Anderson localization | `heatmap` | `anderson-{system}-{disorder}` | Spatial grid showing localized vs extended states |
| Phylogenetic distances | `heatmap` | `phylo-distance-{dataset}` | Species x species distance matrix |

**Live presentation vision**: A running biodiversity assay streams sensor data
as `timeseries`, computes diversity indices as `gauge` values, and produces PCoA
ordination as `scatter3d` — all in real time. The spectral deconvolution IS the
analytical result. The sensor stream IS the lab notebook.

**Multi-panel dashboard**: `wetspring_lab_dashboard`
- Row 1: `timeseries` (sensor streams) + `gauge` (Shannon diversity)
- Row 2: `spectrum` (mass spec) + `bar` (genus abundance)
- Row 3: `scatter3d` (PCoA) + `heatmap` (Anderson localization)

**Gaps**: None — all science patterns map to existing channel types.

---

### neuralSpring — ML / AI Inference

**Current petalTongue status**: Not wired

| Science Output | Channel Type | Binding ID Pattern | Notes |
|---------------|-------------|-------------------|-------|
| Training loss | `timeseries` | `loss-{model}-{run}` | Epoch on X, loss on Y; streaming append |
| Attention weights | `heatmap` | `attention-{layer}-{head}` | Token x token attention matrix |
| Token probabilities | `bar` | `token-probs-{step}` | Top-k token categories with probabilities |
| Perplexity evolution | `timeseries` | `perplexity-{model}` | Step on X, perplexity on Y |
| Embedding space | `scatter3d` | `embeddings-{model}-{layer}` | UMAP/t-SNE of hidden states |
| Weight distribution | `distribution` | `weights-{layer}` | Histogram of weight values per layer |
| Inference throughput | `gauge` | `throughput-tokens-per-sec` | Tokens/sec with normal range |
| KV-cache utilization | `gauge` | `kv-cache-{model}` | Percentage with warning threshold |
| Loss landscape | `heatmap` | `loss-landscape-{model}` | Parameter grid with loss values |
| Anderson localization in weights | `heatmap` | `anderson-weight-{layer}` | Spatial disorder vs transport in weight matrices |

**Live presentation vision**: A running inference session streams token
probabilities as `bar` charts, attention matrices as `heatmap` frames, and
loss evolution as `timeseries`. The attention pattern IS the interpretability
figure. The token generation IS the demonstration.

**Multi-panel dashboard**: `neuralspring_inference_dashboard`
- Row 1: `timeseries` (loss) + `gauge` (throughput)
- Row 2: `heatmap` (attention) + `bar` (token probabilities)
- Row 3: `scatter3d` (embedding space) + `distribution` (weight distribution)

**Gaps**:
- Animated attention across sequence positions (frame-by-frame heatmap)
- Network topology visualization (not a current channel type)

---

### healthSpring — Clinical / Compliance

**Current petalTongue status**: DataChannel wired (reference exemplar)

| Science Output | Channel Type | Binding ID Pattern | Notes |
|---------------|-------------|-------------------|-------|
| PK/PD curves | `timeseries` | `pk-{drug}-{route}` | Time on X, concentration on Y |
| Population PK distributions | `distribution` | `pop-pk-{parameter}` | Cmax, AUC, t½ distributions |
| Biomarker panels | `bar` | `biomarkers-{patient}` | Lab categories with reference ranges |
| Vital signs | `gauge` | `vitals-{metric}` | HR, SpO2, BP with normal/warning ranges |
| Microbiome PCoA | `scatter3d` | `microbiome-pcoa-{cohort}` | Patient samples in ordination space |
| Drug interaction matrix | `heatmap` | `interactions-{drug_set}` | Drug x drug interaction severity |
| Biosignal waveforms | `timeseries` | `biosignal-{type}-{patient}` | ECG, EEG, EMG waveforms |
| Clinical risk composite | `gauge` | `risk-composite-{patient}` | Composite score with thresholds |
| HRV power spectrum | `spectrum` | `hrv-{patient}` | Frequency vs power |
| C. diff colonization | `timeseries` | `cdiff-{patient}-{metric}` | Days on X, colonization metric on Y |

**Live presentation vision**: healthSpring is the reference implementation.
The patient assessment dashboard streams vitals as `gauge`, PK curves as
`timeseries`, and lab panels as `bar` — all within the ionic-fenced dual-tower
architecture. Tower A (data custody) produces DataBindings; Tower B (analytics)
renders them through petalTongue. The clinical workflow IS the dashboard.

**Multi-panel dashboard**: `healthspring_clinical_dashboard`
- Row 1: `gauge` (HR) + `gauge` (SpO2) + `gauge` (composite risk)
- Row 2: `timeseries` (PK curve) + `distribution` (population PK)
- Row 3: `bar` (biomarkers) + `heatmap` (drug interactions)
- Row 4: `scatter3d` (microbiome PCoA) + `spectrum` (HRV)

**Gaps**: None — healthSpring's DataChannel pattern is the ecosystem exemplar.

---

### airSpring — Ecological & Agricultural Science

**Current petalTongue status**: Not wired

| Science Output | Channel Type | Binding ID Pattern | Notes |
|---------------|-------------|-------------------|-------|
| ET0 spatial maps | `fieldmap` | `et0-{date}-{region}` | Grid of evapotranspiration values |
| Soil moisture grids | `fieldmap` | `soil-moisture-{depth}-{date}` | Spatial moisture distribution |
| Weather station streams | `timeseries` | `weather-{station}-{metric}` | Live streaming; append |
| Canopy resistance models | `heatmap` | `canopy-{crop}-{stage}` | Spatial resistance patterns |
| Crop stress classification | `bar` | `stress-{field}-{date}` | Stress categories with severity |
| Yield predictions | `timeseries` | `yield-{crop}-{season}` | Growth stage on X, predicted yield on Y |
| NCBI 16S diversity | `scatter` | `16s-pcoa-{site}` | Microbial community ordination |
| Irrigation threshold | `gauge` | `irrigation-{zone}` | Soil moisture with depletion thresholds |
| Forecast scheduling | `timeseries` | `forecast-{metric}-{horizon}` | Future projections |
| Soil microbiome abundance | `bar` | `microbiome-{site}-{depth}` | Genus/phylum composition |

**Live presentation vision**: A field sensor network streams weather data as
`timeseries`, soil moisture as `fieldmap` grids, and irrigation thresholds as
`gauge` values. The ET0 map IS the irrigation recommendation. The sensor grid
IS the agronomic decision tool.

**Multi-panel dashboard**: `airspring_field_dashboard`
- Row 1: `fieldmap` (ET0) + `fieldmap` (soil moisture)
- Row 2: `timeseries` (weather streams) + `gauge` (irrigation)
- Row 3: `bar` (crop stress) + `scatter` (16S PCoA)

**Gaps**: None — fieldmap channel handles spatial grids well.

---

### groundSpring — Geoscience & Measurement Science

**Current petalTongue status**: Not wired

| Science Output | Channel Type | Binding ID Pattern | Notes |
|---------------|-------------|-------------------|-------|
| Geospatial grids | `fieldmap` | `geo-{survey}-{layer}` | Spatial measurement data |
| Seismic FFT | `spectrum` | `seismic-fft-{station}` | Frequency content of seismic signals |
| Statistical quality checks | `distribution` | `stats-{test}-{dataset}` | Anderson-Darling, WDM distributions |
| Calibration traces | `timeseries` | `calibration-{instrument}` | Long-duration calibration records |
| Inverse problem estimates | `scatter` | `inverse-{parameter_pair}` | Parameter estimation scatter |
| Noise filter results | `spectrum` | `noise-{method}-{signal}` | Before/after spectral comparison |
| Matrix decomposition | `heatmap` | `decomp-{method}-{matrix}` | Factor matrices |
| Measurement uncertainty | `distribution` | `uncertainty-{measurement}` | Measurement distribution with bounds |

**Live presentation vision**: A calibration run streams instrument readings as
`timeseries`, quality checks as `distribution`, and spatial results as `fieldmap`.
The calibration trace IS the verification certificate. The seismic spectrum IS
the geological survey.

**Multi-panel dashboard**: `groundspring_survey_dashboard`
- Row 1: `fieldmap` (geospatial) + `spectrum` (seismic FFT)
- Row 2: `timeseries` (calibration) + `distribution` (uncertainty)
- Row 3: `heatmap` (decomposition) + `scatter` (inverse estimates)

**Gaps**: None.

---

### ludoSpring — Game Science / HCI

**Current petalTongue status**: `game_scene` wired (scene push operational)

| Science Output | Channel Type | Binding ID Pattern | Notes |
|---------------|-------------|-------------------|-------|
| Game scene render | `game_scene` | `scene-{session}-{room}` | Tilemaps, sprites, entities |
| Engagement metrics | `timeseries` | `engagement-{metric}-{session}` | Session time on X, metric on Y |
| Tick budget | `gauge` | `tick-budget` | Current tick ms, target 16.6ms, warning at 14ms |
| Fitts law curves | `timeseries` | `fitts-{experiment}` | Distance/width on X, movement time on Y |
| PCG quality metrics | `bar` | `pcg-quality-{algorithm}` | Quality dimensions as categories |
| Player heatmap | `heatmap` | `player-heatmap-{session}` | Spatial distribution of player actions |
| AI narration | `game_scene` | `narration-{session}` | Narrative scenes with NPC dialogue |
| Noise throughput | `gauge` | `noise-throughput` | Samples/sec |
| CPU/GPU parity | `scatter` | `parity-{operation}` | CPU result vs GPU result |
| Game audio | `soundscape` | `audio-{scene}` | Ambient audio layers |

**Live presentation vision**: A game session streams scenes as `game_scene`,
tick budget as `gauge`, and engagement metrics as `timeseries`. The play session
IS the experiment. The engagement curve IS the figure. The AI narration IS
the narrative design validation.

**Multi-panel dashboard**: `ludospring_session_dashboard`
- Row 1: `game_scene` (current scene)
- Row 2: `gauge` (tick budget) + `gauge` (noise throughput)
- Row 3: `timeseries` (engagement) + `timeseries` (Fitts law)
- Row 4: `heatmap` (player actions) + `bar` (PCG quality)

**Gaps**: None — ludoSpring pioneered the `game_scene` and `soundscape` channels.

---

## Rewiring Connection

When springs rewire from library to IPC (Tier 2→3→4), a natural benefit emerges:
**IPC result payloads are already JSON-serialized** and can be directly forwarded
to petalTongue as DataBinding inputs. Library results require a serialization
hop. Binary-only springs get visualization "for free" as a side effect of the
rewiring — every `tensor.matmul` result that comes back as JSON-RPC can be
streamed to petalTongue simultaneously.

```
ecobin primal (barraCuda)
    │ JSON-RPC response: {"result": {"value": [...]}}
    ├──→ Spring domain logic (consume result)
    └──→ petalTongue DataBinding (visualize result)
```

This is why rewiring and visualization are not independent tasks — they
converge. The IPC surface IS the visualization surface.

---

## Priority Order for Wiring

1. **healthSpring** — already wired; reference exemplar for others
2. **ludoSpring** — `game_scene` wired; extend to science metrics dashboards
3. **wetSpring** — partial; highest paper count, most diverse channel needs
4. **hotSpring** — not wired but rich science; HMC dashboard is high-impact
5. **neuralSpring** — not wired; attention heatmaps are high-visibility
6. **airSpring** — fieldmap channel is a perfect fit for spatial ecology
7. **groundSpring** — spectrum + fieldmap cover its primary outputs

---

## Ecosystem Channel Coverage

| Channel Type | Springs Using |
|-------------|--------------|
| `timeseries` | All 7 domain springs |
| `gauge` | All 7 domain springs |
| `heatmap` | hotSpring, wetSpring, neuralSpring, groundSpring, ludoSpring |
| `bar` | wetSpring, neuralSpring, healthSpring, airSpring, ludoSpring |
| `scatter` | wetSpring, airSpring, groundSpring, ludoSpring |
| `scatter3d` | hotSpring, wetSpring, neuralSpring, healthSpring |
| `distribution` | neuralSpring, healthSpring, groundSpring |
| `spectrum` | wetSpring, groundSpring, healthSpring |
| `fieldmap` | airSpring, groundSpring |
| `game_scene` | ludoSpring |
| `soundscape` | ludoSpring |

**No gaps in channel type coverage.** Every spring's science maps to existing
petalTongue DataBinding types. The work is wiring, not inventing new channels.

---

**License**: AGPL-3.0-or-later
