# airSpring Comprehensive Handoff — May 16, 2026

**Spring**: airSpring v0.10.0 | **guideStone**: L4 (structural L5)
**Tests**: 1,057 lib + 62 forge = 1,435 total | **Capabilities**: 51
**Registry**: 451-method canonical sync (Wave 17) | **Debt**: Zero actionable

---

## 1. Primal Consumption Map

airSpring consumes 10 of 13 ecosystem primals at runtime. Zero compile-time coupling
between primals — all interaction is JSON-RPC 2.0 over Unix sockets or TCP.

| Primal | Methods Called | Wire Status |
|--------|---------------|-------------|
| **biomeOS** | `capability.call`, `primal.announce` (Wave 17), `composition.status`, `lifecycle.status` | Production — `primal.announce` primary, `method.register`/`lifecycle.register`/`capability.register` legacy fallback |
| **barraCuda** | `precision.route` (advisory) | Tier 2 IPC — typed `PrecisionAdvice` (requires_compiler, adapter) |
| **toadStool** | `toadstool.validate`, `toadstool.list_workloads`, `compute.offload` | Tier 2 IPC — workload pre-flight + dispatch |
| **bearDog** | `health.liveness` | Tower probe only — no crypto payloads from airSpring |
| **songBird** | `health.liveness`, transport discovery | Tower probe + `SongbirdTransport` for data routing |
| **skunkBat** | `security.audit_log` (startup audit) | Defense — audit event emission (correct wire: `security.audit_log`, NOT `defense.audit`) |
| **nestGate** | `content.store`, `content.get`, `storage.status` | Tier 2 IPC — typed CAS client |
| **squirrel** | `inference.embed`, `inference.complete`, `inference.models` | Wired through `dispatch_science` — soil sensor similarity is documented embed use case |
| **rhizoCrypt** | `dag.create_session`, `dag.append_event`, `dag.dehydration.trigger` | Via provenance trio (or `nest.store`/`nest.commit` signal dispatch) |
| **loamSpine** | `commit.session` | Via provenance trio (or `nest.commit` signal dispatch) |
| **sweetGrass** | `provenance.create_braid` | Via provenance trio (or `nest.store`/`nest.commit` signal dispatch) |
| **coralReef** | — | Discovery only — AG-006: sovereign shader compile not wired |
| **petalTongue** | — | Graph-level only — AG-009: no direct IPC |

### Wire Hygiene Learnings (for all springs)

1. **bearDog**: Messages use base64 encoding. If you're sending raw bytes, wrap in `base64::encode()`. airSpring only sends health probes.
2. **skunkBat**: Audit method is `security.audit_log`, NOT `defense.audit`. ludoSpring found this — check your wiring.
3. **Tower = bearDog + songBird + skunkBat** (triple-first per plasmidBin v2026.05.14). All Tower detection must include skunkBat.
4. **NestGate**: Does NOT serve `data.*` methods. If you're calling `data.open_meteo_weather` through NestGate, that's wrong — route through `capability.call` instead.

---

## 2. Wave 17 Signal Adoption

### Registration: `primal.announce`

Single-call replaces `lifecycle.register` + `capability.register` + `method.register`:

```json
{
  "method": "primal.announce",
  "params": {
    "primal": "airspring",
    "socket": "/run/ecoprimals/airspring-{family}.sock",
    "capabilities": ["agriculture", "ecology", "provenance"],
    "methods": ["science.et0_fao56", "... 51 total ..."],
    "signal_tiers": ["nest"],
    "version": "0.10.0"
  }
}
```

Automatic fallback to legacy 3-call pattern if biomeOS is pre-v3.57.

### Provenance Signals: `nest.store` + `nest.commit`

**`nest.store`** replaces: `NestGate.content.put` → `rhizoCrypt.dag.event.append` → `loamSpine.spine.seal` → `sweetGrass.braid.create`

**`nest.commit`** replaces: `rhizoCrypt.dehydrate` → `bearDog.sign` → `NestGate.store` → `loamSpine.seal`

Both fall back gracefully to legacy provenance trio pipeline when signal dispatch is unavailable. Domain-specific math (`science.et0_fao56`, `ag.measure`, etc.) remains as direct `capability.call`.

---

## 3. NUCLEUS Composition Patterns

### Atomic Definitions

| Atomic | Components | Role |
|--------|-----------|------|
| **Tower** | bearDog + songBird + skunkBat | Trust boundary (crypto + discovery + defense) |
| **Node** | Tower + toadStool | Compute dispatch |
| **Nest** | Tower + nestGate | Data storage + provenance |

### Deploy Graphs (7)

| Graph | Purpose |
|-------|---------|
| `airspring_eco_pipeline.toml` | Weather → ET₀ → Water Balance → Yield |
| `airspring_provenance_pipeline.toml` | Session → Science → Dehydrate → Commit → Attribute |
| `airspring_niche_deploy.toml` | Full niche: Tower + Trio + NestGate + ToadStool + airSpring |
| `cross_primal_soil_microbiome.toml` | Cross-spring: airSpring θ(t) → wetSpring diversity |
| `airspring_gpu_batch_deploy.toml` | GPU batch: barraCuda / batched dispatch stages |
| `airspring_sovereign_data_deploy.toml` | Sovereign data: NestGate / Songbird-aligned routing |
| `airspring_uncertainty_deploy.toml` | Uncertainty / UQ pipeline: bootstrap, jackknife, MC layers |

### Deployment via neuralAPI from biomeOS

airSpring registers as a biomeOS niche at startup. The registration flow:

1. Discover orchestrator socket (biomeOS)
2. `primal.announce` (51 capabilities, `nest` signal tier)
3. Heartbeat loop: `lifecycle.status` every 30s with health + capability count + composition state

biomeOS routes inbound requests to airSpring via capability matching. No hardcoded routing — biomeOS learns which methods airSpring serves from the announce call.

---

## 4. Evolution Opportunities for Upstream Teams

### For barraCuda team
- **AG-010**: `TensorSession`/`TensorContext` not available — seasonal GPU pipeline blocked on persistent buffer pooling
- **AG-011**: Anderson coupling WGSL shader — `science.anderson_coupling` is CPU-only; no upstream shader exists (Tier C in GPU promotion map)
- **Precision advisory**: `PrecisionAdvice` response now includes `requires_compiler` and `adapter` fields — coralReef can use these

### For toadStool team
- **AG-007**: `compute.dispatch` returns opaque JSON — need typed response contract for ecology workloads
- 6 airSpring workloads registered in projectNUCLEUS (ET₀ pipeline, seasonal batch, etc.)

### For coralReef team
- **AG-006**: `discover_shader_compiler()` hook exists in airSpring but is unused. Once coralReef stability (bind_stat timeout, FECS cold init, naga::Module ingest from Pass 12) is resolved, we can wire sovereign shader compilation

### For nestGate team
- airSpring now uses `nest.store`/`nest.commit` signals — biomeOS manages the graph. Individual `content.store`/`content.get`/`storage.status` calls remain for direct CAS access

### For primalSpring team
- 451-method registry sync confirmed (cross-sync test passes)
- `primal.announce` adopted with fallback
- `nest.store` + `nest.commit` adopted with fallback
- Thread 6 (Agricultural Science): 36 foundation targets exist, need expression refresh
- `methods.rs` drift-proofing: `capabilities_match_registry` + `capability_cross_sync` CI tests ensure zero drift

---

## 5. Science Validation Summary

### Python → Rust → GPU Pipeline
- **1,284** Python control checks across 62 scripts
- **25/25** CPU timing parity algorithms (14.3× geometric mean speedup)
- **21/21** CPU-GPU parity modules
- **90** experiments (87 numbered + 3 composition)
- **LTEE E3** (FLS2 plant immunity): Python 12/12 + Rust 29/29 PASS

### Benchmark Coverage
- **CPU parity**: 25/25 in `bench_cpu_vs_python` (ET₀ ×6, Soil ×5, Hydrology ×3, Crop ×4, Ecology ×5, Pipeline ×2)
- **GPU parity**: 21/21 CPU-GPU, 46/46 `validate_gpu_math`, 25 Tier A upstream ops
- **Cross-spring**: 146/146 evolution checks, 32/32 provenance benchmarks
- **Not started**: Kokkos Tier 1 (barraCuda domain, not airSpring)

### Paper Queue Status
| Tier | Paper | Status |
|------|-------|--------|
| Complete | FAO-56, HYDRUS, USDA/NASS, Dong 2020, Anderson, LTEE E3 | 60+ papers reproduced |
| Tier 1 | #6, #7 — Dong multi-sensor IoT (2024+) | Awaiting field data |
| Tier 3 | #16 — Cover crop water use | Future |
| Tier 4 | #23, #24 — Dolson sensor, Waters microbiome | Future |

---

## 6. Active Gaps

| ID | Primal | Gap | Owner |
|----|--------|-----|-------|
| AG-006 | coralReef | Sovereign shader compile not wired | coralReef team |
| AG-007 | ToadStool | `compute.dispatch` opaque JSON | toadStool team |
| AG-009 | petalTongue | No direct IPC from airSpring | Low priority |
| AG-010 | barraCuda | TensorSession/TensorContext | barraCuda roadmap |
| AG-011 | barraCuda | Anderson coupling WGSL shader | barraCuda Tier C |

All remaining gaps are **upstream-blocked**, not airSpring code debt.

---

## 7. Codebase Health

| Metric | Value |
|--------|-------|
| TODO/FIXME/HACK | 0 |
| unsafe (non-test) | 0 |
| Production mocks | 0 |
| Files >800 LOC | 0 |
| Hardcoded paths | 0 |
| `#[allow()]` in production | 0 |
| Clippy pedantic+nursery | 0 warnings |
| External C deps | 0 |
| Edition | 2024 |
| Line coverage | 90.56% |

---

**Submitted by**: airSpring v0.10.0
**For**: primalSpring upstream audit + primal/spring team absorption
