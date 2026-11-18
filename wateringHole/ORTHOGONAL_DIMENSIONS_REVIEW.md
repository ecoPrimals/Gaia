# Orthogonal Dimensions Review — Reusable Checklist

**Purpose**: Systematic reassessment checklist for overwatch cascade reviews.
Use at wave boundaries or whenever a comprehensive posture check is needed.

**Fossilization**: Dimensions that are fully complete with no open items graduate
to the FOSSILIZED section. They are not re-checked unless a regression signal
appears. This keeps the active review focused on evolving concerns.

---

# ACTIVE DIMENSIONS

## 1. Temporal / Coordination

- [x] `wave.toml` reflects current wave ID, sub, and posture (Wave 157k)
- [x] Gate heads published (`heads/*.toml`) — golgiBody auto-publishing active
- [x] `freshness.toml` uses tree hashes (DAG, not cyclic graph)
- [x] **ECOSYSTEM_BLURB.md** is the universal handoff (Tracks A+B converged)
- [x] **70+ handoff docs + AARs** delivered Wave 155b–n. 10 AARs + 2 handoffs fossilized this wave.
- [x] **ZERO P0 (all 3 resolved + DEPLOYED Wave 157e):** ~~P0-A bearDog~~ DEPLOYED FLEET-WIDE (westGate: `crypto.sign_ed25519` signs in 0.4ms). ~~P0-B nestGate~~ DEPLOYED (westGate: `content.ingest` 5 files/6.3ms, Rust-native). ~~P0-C biomeOS FD~~ DEPLOYED (westGate: 13→15 FDs after 7 calls). All 6 gates on 157e depot. 16 primals self-audited — zero phantom methods.
- [x] **NUCLEUS ACHIEVED on 7 gates** — westGate, strandGate, blueGate, sporeGate, southGate, ironGate, **graftGate** (Full NUCLEUS via biomeOS Neural API — 21 ACTIVE domains, 1830 capabilities, <60s). All Linux gates v4.57+ G68-converged. graftGate first darwin NUCLEUS. Gate validation AARs fossilized.
- [x] **Depot UNIFIED + PRUNED + PEPTI LAYER (Wave 157e)** — Canonical path `/opt/ecoPrimals/plasmidBin/primals`. Auto-prune on every harvest. Disk health guard (80% warn, 90% block). **G69 Phase 3 CAS archival wired** (`archive_superseded_binary()` sign→spine→braid→CAS). G69 Depot Lineage spec published. blueGate → golgi push SOLVED. graftGate registered. Forgejo GC timer. golgi at 74% disk. **All 6 gates deployed Wave 157e.** **Wave 157k ortho cascade: sporeGate rebuilt depot (15/15 musl CURRENT). Fleet pushed to golgiBody, eastGate, ironGate, strandGate. eastGate was Jun 4 binaries (2+ months stale) — now Aug 12. graftGate pushed 5/15 darwin refreshed. Provenance gap FIXED (swarmVine + membrane added to `provenance.toml`). `membrane-cascade.service` path drift FIXED. BLAKE3 verified across all paths.** **PIPELINE DIVERGENCE RESOLVED (Aug 14, sporeGate `3f9fa14`)**: serde(flatten) collision silently dropped per-entry `target`/`builder`, making harvest blind to architecture mismatches. Two-pass TOML parse + target-aware drift detection + rootPulse trio wiring. 13/13 x86_64 rebuilt from current HEAD, 28 binaries pushed. Stale `~/.local/bin/membrane` (11 days old) fixed. Flat provenance.toml now a cache — rootPulse trio is the designed authority.
- [x] **biomeOS v4.56 SHIPPED** — G22 convergence steps 1+2: unified namespace, 244 caps, 47 deps removed.
- [x] **westGate ZFS rebuilt** — mirror → raidz1, 25.4 → 50.7 TB usable. AlphaFold DB fits.
- [x] **Golgi post-receive hook FIXED** (3 bugs: dispatcher, case, category). Sovereign CI E2E verified.
- [x] **cellMembrane 1,281+ tests** — MEMBRANE_*, crypto dedup, J16+J13+J19 killed, registry API hardened.
- [x] **squirrel -48,672 lines** (Waves 156e→156z deep cleanup). 3 orphan crates excised, 157 functions de-asynced, PluginV2 dead code eliminated, PrimalType + EcosystemPrimalType fossils deleted, config crate removed. 313 files changed. 0 unsafe, 0 clippy.
- [x] **Provenance 7/7 COMPLETE** — E2E validated on westGate (5th consecutive pass) + blueGate (Windows). **Braid pen test 86/87 PASS (Wave 157e)** — first-ever E2E provenance chain verification. **~~P1: `braid.verify` missing~~ → SHIPPED (sweetGrass, Wave 157g)** — method #48, capability-registered. **~~P2: braid.verify behavioral tests~~ → CLOSED (sweetGrass `a6cc287`, Wave 157i)** — 5 behavioral tests: unsigned braids, format validation, crypto-down permissive, not-found, attribution metadata. **PROVENANCE TRIO EXPERIMENTS 14/14 (westGate, Aug 14)**: `membrane experiment.*` Rust-native validation suite. 2,630 braids verified, 1,421 DAG sessions / 390,984 vertices, 2 spines (1,386 commits). Cross-industry export (W3C PROV-O, RO-Crate, BagIt, DataCite). primalSpring exp124 codified. 4 routing gaps documented (sweetGrass auto-announce, bearDog AEAD, rhizoCrypt dehydration, content.put). `native_braid.py` formally deprecated.
- [x] **Sovereign CI LIVE** — push-to-deploy E2E verified for ALL 13 primals including biomeOS (coevolution).
- [x] **Wave 157e MESH DEPLOYED** — ALL 6 NUCLEUS gates on 157e depot. **Wave 157i**: G72 Pandemic: **11/11 teams Tier 1 COMPLETE** (~155+ crates shed fleet-wide). Gossip **3→7/16 primals LIVE** (barraCuda **22/22** full spec, wetSpring **4/4**, nestGate 11 CAS sites wired). **P2 braid.verify CLOSED** (sweetGrass behavioral tests). toadStool tokio 118→65 (45%). **graftGate Tower Atomic RUNNING on macOS** — 4th platform proven (G11). hotSpring pseudoSpore E2E pipeline shipped. bearDog +41 dead deps removed. petalTongue telemetry excised + runtime discovery. nestGate S147/S148 (1,666 tests). **Wave 157k POST-PANDEMIC**: graftGate **FULL NUCLEUS** via biomeOS Neural API (21 ACTIVE domains, 1830 caps, <60s). **iosGate FIRST DEPLOY** (BearDogApp on iPhone XS — 6th OS family). songBird deep-debt sweep (148 files, -1,236 lines, `content.locate` FUNCTIONAL, `--node-id` RESOLVED). swarmVine P2s RESOLVED (riboCipher + relay), 186 tests, 90.8% coverage. biomeOS spawn leak RESOLVED (`6df4220e`). toadStool wgpu28 RESOLVED in source. **All 4 canary bugs RESOLVED + DEPLOYED** (ironGate confirmed 4/4 in depot). Ownership rationalized. **Deployment signaling gap identified** — spec filed. **Wave 157k ORTHO CASCADE**: sporeGate depot REBUILT (15/15 musl current). Fleet pushed to 4 gates. ironGate 13/13, 2ms dispatch, 4 mesh peers, blocker #3 CLOSED. blueGate 13/13 but 2 Windows build failures (songBird toolchain + swarmVine UDS). graftGate 5 rebuilt, sourDough atomic model corrected in code (`3dd320a`), D11 filed (swarmVine missing from biomeOS graph). westGate `content.locate` mesh scope WIRED (`a5dbe79b2`). primalSpring v0.9.49 (1,253 tests, deploy health Phase 2 scaffolded).
- [x] **Overwatch retooled (Wave 157g)** — gate-agnostic temporal script (`overwatch-temporal.sh`) sweeps all 4 Forgejo orgs via HTTPS API, compares 43 repos against local HEAD, outputs human/JSON. No SSH needed. Overwatch position formally separated from primalSpring team: overwatch = coordination/blurb/review (floats to any gate); primalSpring = code + deployment (eastGate-resident). Phase B impulse-driven overwatch adoption accelerated.
- [x] **Coevolution contract COMPLETE (G21)** — biomeOS `composition.test_swap` + cellMembrane `validate_with_deps`. Mode gap FIXED (`652cf8a7`).
- [x] **228 files fossilized** across 20 checkpoints. Latest: `wave157k_interstadial/` (strandGate full session AAR). Active handoffs: **20** (16 prior + K80 wedge AAR + vendor excision AAR + sovereign ground truth + strandGate science status). **1,514 total fossil records.**
- [x] **northGate cascade validated (Aug 16)** — tideGlass Phase 0 external review pushed to GitHub (outer membrane) by `DataScienceBioLab`, pulled to eastGate, pushed to Forgejo (inner membrane). GitHub→eastGate→Forgejo cascade topology working. northGate = personal machine, external reviewer surface, future Steam cloud compute pool validation.
- [x] **biomeGate Titan V Tier 1 CONFIRMED (Aug 16)** — 4 measurement bugs fixed (D3hot reads as cold, Tier 2 without FECS, sleeping GPU as warm, catalyst PC range). `RegisterRead` enum replaces raw `u32` at 10 sites. Nouveau warm handoff achieves Tier 1 (23 engines, PRAMIN accessible). FECS PRI fault blocks Tier 2 (Volta GPCCS HS fuse lock). K80 blocked by missing GK210 chipset entry (software gap, not hardware wall). `toadstool sovereign handoff|status|strategies` CLI shipped.
- [x] **biomeGate DRM hot-add root cause (Aug 16)** — Single root cause behind 3 session kills: nouveau registers DRM node under `modeset=2`, Xorg hot-adds it and `abort()`s. Machine-checked preflight + live DRM watch landed in `toadstool-cylinder`.
- [x] **rootPulse 6/6 graphs REGISTERED (Aug 16)** — biomeOS `af1dc9d3`: all 6 rootPulse graphs in `CompositionPatternRegistry::with_canonical_patterns()`. `graph.list` exposes all. 1,608 biomeOS tests pass. **Item #10 CLOSED.**
- [x] **tideGlass Phase 0 external review (northGate, Aug 16)** — 10-week gap assessed. Infrastructure prerequisites ALL COMPLETE. Revised estimate: 5-7 focused days (was 1-2 weeks). Priority 1: start Phase 0 this week. Priority 2: arXiv Rung 1 reviewer send (parallel, 6-8h). Priority 3: Gonzales reactivation (gated on Phase 0). Assessment: "the pivot point is now."
- [x] **northGate FRAGO issued (overwatch, Aug 16)** — Internal assessment reveals tideGlass far more advanced than outer membrane shows (9-crate 220+ test workspace vs empty GitHub). Revised Phase 0 estimate: **3-5 focused days** (not 5-7). FRAGO redirects northGate to external surface tasks (GitHub mirror, sporePrint update, arXiv send, Gonzales email prep) while inner membrane handles genuine gaps (Python baseline, weights, env mapping). Files: `TIDEGLASS_PHASE0_INTERNAL_ASSESSMENT_AUG16_2026.md`, `FRAGO_NORTHGATE_TIDEGLASS_AUG16_2026.md`.
- [ ] **D14 External Surface REOPENED (Aug 16)** — primals.eco (sporePrint/Zola) NOT OPERABLE. F12 partially reopened. sporePrint team assigned: website fix (blocks arXiv), content refresh, Google SEO audit. northGate tideGlass gap exposed dual-reality between inner/outer membranes. See D14 for full audit. **CONCEPT EVOLVED (Aug 17)**: sporePrint should evolve from static Zola site → **NUCLEUS-served live data surface**. NUCLEUS + cellMembrane serve data/references directly. petalTongue semantic layer exposed for translate.js validation. Zola remains as templating, but science data, validation counts, gate status, provenance chains, and spring results are served live by primals.
- [x] **strandGate 45 production configs BANKED (Aug 17)** — SU(3) pure gauge 3β × 3V × 5 seeds. Cross-GPU validated (AMD/NVIDIA 0.19% delta at β=6.20 32⁴). Dark silicon 7/8 unit classes lit (ROPs, RT cores, rasterizer, depth buffer, video encoder, mesh shaders — tensor cores blocked on PTX). **Protocol mismatch identified**: 16⁴/24⁴ at dt=0.01 vs 32⁴ at dt=0.0025. **Thermalization insufficient**: 32⁴ 13-29σ below literature (Bali 2000, Necco-Sommer 2002). Resolution: unified protocol run with 2000+ warmup. **Upstream needs**: barraCuda configurable warmup P1, plaquette time-series export P1. Full session AAR fossilized. Science status handoff pushed.
- [x] **biomeGate K80 wedge hunt (Aug 16 evening)** — 4 bugs found, all sentinel-as-data: (1) `pgraph_reset` ignored `PowerSafetyProfile`, clocked GR pre-devinit; (2) PRAMIN sentinel test wrote into untrained GDDR5; (3) `FalconDiagnostic::probe` wrote `0x1854` through PRI-faulted PBUS ring — **the actual killer** (3 of 5 die-losses); (4) interpreter executed 76%-unknown VBIOS parse. **PROM VBIOS decoded for first time** — `0xAA55` signature at `BAR0+0x300000`, no un-shadowing write needed. K80 cold bring-up now completes with die alive (×4). Live edge moved from "no VBIOS source" to "cannot decode the VBIOS scripts." Kepler opcode coverage is the sole K80 blocker.
- [x] **biomeGate vendor tool excision (Aug 17)** — GPU detection replaced: `nvidia-smi`/`rocm-smi`/`lspci` → native sysfs/procfs. Found 4 GPUs (was 1). Phantom Intel GPU removed. 216 tests recovered that had silently stopped compiling. Real bug found: `RwLock` guard held across `.await` in `AgentBackend`. Floating `rust-toolchain.toml` found (stable→1.97.1 drift, 542 unformatted files, 682 clippy warnings). **6 ecosystem-wide gaps raised**: (1) pin toolchain versions; (2) gate `cargo test --workspace --no-run` in CI; (3) grep for `cfg(all())`; (4) vendor tooling in observation paths (barraCuda, coralReef); (5) `runtime/edge` 8,124 LOC in limbo; (6) VRAM native source for NVIDIA.
- [x] **SOVEREIGN_GROUND_TRUTH.md established (Aug 17)** — Single source of truth for sovereign compute claims. Key finding: **"No shader has ever executed on the sovereign path on any NVIDIA GPU."** All verified GPU compute runs through wgpu/Vulkan with vendor drivers. Sovereign VFIO path reaches hardware bring-up but has never produced a numeric result. Tier ladder formalized: 0 (cold) → 1 (warm infra, Titan V only) → 2 (warm compute, not achieved) → 3 (full sovereign cold boot). Writing rules established: wiring ≠ result, name the path, date claims.
- [x] **bonsai-bt FORKED + FIRST CONTACT (Aug 16)** — github.com/Sollimann/bonsai (MIT, v0.13.0) → git.primals.eco/ecoPrimals/bonsai-bt. Full mirror (all branches + tags + 207 commits). Code audit: 0 unsafe, 3,197 LOC core, 76 tests pass, 0 TODO/FIXME. DECIDE layer meta-primal ingestion pipeline started (Phase 0: code review + scyBorg license conversion). **Exp125 LIVE (primalSpring `08068ed4`)**: 5 behavior trees executed against NUCLEUS — reactive health check, compute fallback (Select), provenance pipeline (Sequence), serialization round-trip (550B JSON, BLAKE3 hashable, equality preserved), memoryless reactive policy. 23/24 checks pass (1 expected: no live sockets). `EcoAction` enum references Neural API domains, never primal names. Trees are content-addressable ecosystem artifacts. Architecture: `squirrel→REASON | [name]→DECIDE | biomeOS→ROUTE | primals→ACT | sweetGrass→WITNESS | PathwayLearner→ADAPT`. Ingestion plan: `whitePaper/subGen/contacts/BONSAI_INGESTION_PLAN.md`.
- [x] **translate.js ASSESSED (Aug 16)** — External semantic validator (Validation Class V). Do NOT fork. Use as-is to test whether independently developed software can consume petalTongue's semantic output. Assessment: `whitePaper/subGen/contacts/TRANSLATE_JS_EXTERNAL_SEMANTIC_VALIDATION.md`.
- [x] **whitePaper convergence (G22)**: **COMPLETE** — biomeOS v4.56 single-process merge. Dual-protocol (riboCipher + JSON-RPC) in one process. Validated on westGate + sporeGate.
- [x] **Portability checkpoint (G17) — PROVEN.** southGate 22/22 PASS. NUCLEUS from public depot, own entropy, user-space paths, no WireGuard, no inherited identity. 20h stable, 32 sockets, 76MB RSS, 29,294 foreign peer rejections.
- [x] **DATA FEDERATION (westGate)** — **3.21 TB, 153 datasets, 17+ domains, 2.5 TB CAS federated**, 100% provenance. tideGlass 7/7 COMPLETE. AlphaFold v6 42/46 proteomes. 50+ public sources. `data_catalog.toml` v2.0.0 shipped. **NG-05 CLOSED — CAS federation live, 26 capabilities registered.** Inter-gate via Tower Atomic LAN.
- [x] **Peptidoglycan DNS G29 COMPLETE** — 3-way redundancy: sporeGate dnsmasq (primary) + blueGate dnsproxy H2 secondary (LIVE) + golgi mesh DNS. Confirmed by sporeGate infrastructure verification.
- [x] **strandGate v4.56 DEPLOYED** — Carry-forward resolved. G22 confirmed. GPU QCD: 38-58× speedup, 5,500 traj/hr. hotSpring composition validated on live NUCLEUS.
- [x] **sporePrint DEMONSTRATION ERA** — 334→190 pages. pseudoSpore LIVE at primals.eco/pseudospore/. Hype cleaned (20 files). Tests: 116,930. First arXiv draft scaffolded.
- [x] **arXiv Rung 1 REFRAMED** — "Toward Vendor-Agnostic Lattice QCD on Consumer GPUs: SU(2) HMC with DF64 WebGPU/WGSL and Cryptographic Provenance." AI review absorbed. Scope ladder, plaquette normalization eq, precision matrix added. LaTeX updated. 6-rung research program defined. Experiment queue ACTIVE (β-scan, HMC diagnostics, increased stats).
- [x] **westGate persistence HARDENED** — ZFS auto-import, 13/13 NUCLEUS units enabled, boot dependency chain, daily snapshots, monthly scrub. 9/9 boot check PASS.
- [x] **hotSpring** — 627+ tests, 0 clippy. **pseudoSpore E2E pipeline SHIPPED** (pure Rust: `arxiv_production_campaign` → `arxiv_analysis` → `pseudospore_manifest` → `pseudospore_bundle` → `pseudospore_sign` (bearDog Ed25519) → `pseudospore_register` (westGate CAS + ironGate NFT)). 10 gossip events defined (scaffold — not yet hooked). 32⁴ thermalization fix (dt 0.01→0.005, warmup 500→1500). Rung 1 science COMPLETE — all physics validated. (**Wave 157i**)
- [x] **publications/ directory** — Auditable data transfer point for papers + pseudoSpore. Lattice QCD data centralized with full audit trail.
- [x] **golgi auto-publish fix** — THREE compounding bugs fixed: (1) worktree ownership mismatch (`git:git` vs `root:root`), (2) missing `--force` flag on `zola build`, (3) SSH config pointing at wrong golgi IP. sporePrint now deploys correctly to both inner and outer membrane.
- [x] **ironGate ONLINE** — Dev loop validated. Tower Atomic deployed (bearDog 10.6 MB + songBird 16.7 MB + skunkBat 2.6 MB). Forgejo SSH + HTTPS + depot all verified. 42 repos synced. Mesh: golgi 38ms, sporeGate 77ms, eastGate 78ms. **Ready for esotericWebb (G20).**
- [x] **P2 RESOLVED: GPU PRNG polyfill bias** — Root cause: WGSL transcendental polyfills (`log_f64`, `sqrt_f64`, `cos_f64`) in Box-Muller momentum shader produced wrong variance. Three-path comparison proves GPU MD pipeline is correct (bit-exact 4e-17). `cpu_mom` workaround deployed — CPU generates momenta, GPU does all MD at full speed. Section 3.2 UNBLOCKED. Finding strengthens the paper (validation methodology).
- [x] **SPRINGS-TO-NUCLEUS MESH (Aug 2)** — All 10 springs/gardens assigned to gates by hardware specialization. Cell graphs v2.0.0 (content.get + provenance trio + gate metadata). tideGlass Cargo workspace LIVE. biomeOS deploy graphs v2.0.0. Inter-gate CAS data access config created. ecosystem_manifest v3.3.0 with spring_mesh assignments.
- [x] ~~PLANNED SERVICE INTERRUPTION (Aug 2)~~ — **COMPLETE.** [ISP] gateway + DS224+ moved. reefGate enrollment queued. steamGate queued.

## 2. Ecological (Primal Health)

- [x] All primals compile — 5 Tier 1 genomeBin architectures
- [x] ~~P0: glibc depot target~~ — **FIXED** (cellMembrane `8d9bb58`): `targets_for_primal()` auto-appends gnu for GPU primals
- [x] 43/43 repos Forgejo-first
- [x] **~150K+ primal tests validated this wave** (songBird 14,840, bearDog 14,019, nestGate 1,630, **toadStool 8,447** (S379 post-gating), biomeOS 8,700+, squirrel ~5K, petalTongue 6,615, **barraCuda 5,054**, **coralReef 3,963+**, **rhizoCrypt 1,858**, loamSpine 1,752+, **sweetGrass 1,746**, cellMembrane 1,349+, **tideGlass 220+**, primalSpring 197+, **swarmVine 187**, skunkBat 672, sourDough 518+, footPrint 708, esotericWebb V33 (484+), bingoCube 31)
- [x] Zero TODO/FIXME/HACK in project code — **16/16 primals clean** (swarmVine budded Wave 157a)
- [x] Production `.unwrap()` — 0 in critical-path primals
- [x] `unsafe` scoped to GPU primals, science FFI, and crypto
- [x] Format drift RESOLVED — all repos clean
- [x] bearDog: **14,019** tests. P0-A IN DEPOT. **Wave 157d**: `RiboCipherHandler` (16th handler kind) — `decode_mito_tag`, `encode_mito_signal`, `protocol_name`, `list_protocols` as JSON-RPC. Auto-announced via `primal.announce`. Unblocks biomeOS riboCipher Tier 2 cross-gate protocol detection. (**Wave 157d**)
- [x] songBird: **8,500+** tests. **Wave 157d**: Transport convergence (`TransportRegistry`, graceful shutdown, dyn-compatible trait). Gossip excised → swarmVine. PID fix. **RIBOCIPHER TIER 2 CHAIN CLOSED**: `dispatch_ribocipher_rpc()` replaces `dispatch_federation_rpc()` — federation port `:7700` routes mito-framed (`0xED`) connections through full `IpcServiceHandler` instead of stub. Health/capabilities intrinsics fast-path, all other methods via shared handler. bearDog encodes → biomeOS sends → songBird accepts. 7 new tests. (**Wave 157d**) **Wave 157k DEEP-DEBT SWEEP** (`5bc2d3988`): 148 files, +6,962/-5,198 lines (net -1,236). `--node-id`/`--gate-id` CLI flag. `mesh.*` → `gossip.*` aliases (relay forwarding restored). `content.locate` FUNCTIONAL (CAS federation relay). `identity.get` L2 complete. 10 legacy methods canonicalized, 5 monoliths split, 14 dead deps removed. (**Wave 157k**)
- [x] nestGate: **1,666** tests (94 IPC methods, 21 capability domains), dual-path CAS + Neural API wiring. **P0-B RESOLVED + IN DEPOT**. `content.stat` shipped. **G72 Tier 1 DONE**: jsonrpsee removed (1,864 LOC, -10 crates), crossbeam umbrella→channel, dead bincode removal. **S146 deep debt**: fake success paths eliminated (Azure/GCS/S3 → `not_implemented`), idiomatic Rust pass. **S147/S148**: nestgate-nas crate dropped, steam feature removed, shared state consolidation, gossip hooks at 11 CAS sites with 6 event types. (**Wave 157i S146-S148**)
- [x] toadStool: **8,447** tests (post-S379 count — feature gating removed vestigial test surface). S375 NUCLEUS manifest. S376 Tokio blast radius. **S377 manifest CONVERGED** (5→2 BiomeManifest structs). **S378 Tokio vestigial segmentation round 2: 118→65 files (45% reduction).** Dead features excised: `plugin-loading` (C FFI dlopen), `vulkano`, core `wgpu`, `wasm-runtime`. **S379 G72 Tier 1 COMPLETE**: 7 dead deps removed (http-body-util, criterion, uuid, env_logger, test-log, tempfile, vulkano), 6 promoted to workspace (bytemuck, zeroize, wasmi, blake3, anyhow, mdns-sd). `tokio::fs` eliminated (28 files → `std::fs`). tokio trimmed to 6 workspace features. **~73 GiB reclaimed** (S377-S379). **38/48 WASM** (79%) — wiring improved (ExecSpec::Wasm, infer_runtime_type), count flat. **G72 EXEMPLAR.** (**Wave 157i S379**)
- [x] biomeOS: **8,700+** tests (578 Neural API). P0-C IN DEPOT. **Wave 157d**: generic capability dispatch executor (`capability_call` handler routes any dotted capability through Neural API, `graph_foreach` for iterative sub-graph execution). **P1 FD exhaustion SELF-HEALING** (`raise_fd_limit()` at startup — soft NOFILE → 65536, cross-platform, no systemd dependency). Client-side riboCipher Tier 2 (`ConnectionPool::send_mito_jsonrpc` — `[0xED, 0x01]` + 32-byte mito-tag on fresh connections, graceful Tier 1 fallback). G69 depot lineage graph templates (`depot_lineage.toml`, `depot_lineage_batch.toml` with `graph_foreach`). (**Wave 157d**)
- [x] petalTongue: **6,755** tests. **Wave 157d G19**: `/ws/scene` WebSocket + `webgl_bridge` compilation (`DoomFrame`/`SceneGraph` → `WebGlScene` vertex/index buffers ready for GPU upload → broadcast channel). `raise_fd_limit()` self-healing (mirrors biomeOS pattern). `DEFAULT_LOOPBACK_HOST` centralized. Browser clients receive fully compiled buffers. esotericWebb + footPrint ready. (**Wave 157d**)
- [x] barraCuda: **5,054** tests. Silicon Fold absorbed. **Full gossip enmeshment — 22/22 events wired across runtime paths** (compute, tower, shader, dispatch, quota, OOM, precision — recovered, precision-degraded, systemic-error final 3 wired). G72 dep audit clean. **CONTEXT.md: 26 method domains.** Node Atomic Trio wiring, zero-panic (17 `.expect()` → `?`/Result). (**Wave 157i**)
- [x] ~~**barraCuda YELLOW**~~ → **GREEN**: PRNG half-range fixed (xoshiro 52→53 bits). Statistical validation harness. -1,488 LOC (LazyLock→const, error helpers). `cpu_mom` remains production HMC path (Box-Muller transcendental polyfill, not PRNG).
- [x] coralReef: **3,963+** tests. GEMM Phase 2 SHIPPED. **G72 Tier 1 DONE**: optional dep gating (futures/tokio-util behind `tarpc-transport`, tokio/process→dev-deps). `#[allow]→#[expect]` Rust 2024 idiom evolution. Health dispatch wired. 46 orphaned BTSP tests recovered. Proactive file splits + EVOLUTION assessment filed. (**Wave 157i**)
- [x] cellMembrane: **1,349+** tests. G69 Phase 1+2+3 COMPLETE. **G72 Tier 1 DONE**: tokio rt-multi-thread→dev-deps, time/macros removed. Socket name dedup (3→1 canonical). NUCLEUS install lifecycle extracted from harvest.rs. Deep debt sweep: error handling + health module extraction + constant consolidation. Cargo update (blake3, thiserror, aho-corasick, cc). (**Wave 157i**)
- [x] rhizoCrypt: **1,858** tests, **92.69% coverage**. **G72 Tier 1 DONE**: wiremock removed (0 usage), **-46 crates (14.6% lockfile reduction)**. hashbrown dedup resolved (0.14+0.17→0.14). Deep debt sweep: vertex builder extracted, handlers standardized, test file split. (**Wave 157i**) **Wave 157k rootPulse**: `rootpulse.record_build` + `rootpulse.dehydrate_state` step handlers ACTIVE. Semantic aliases (`dag.append`→`dag.event.append`, `dehydrate`→`dag.dehydration.trigger`) — **dehydration routing gap CLOSED**. Zero `#[allow]`, zero dead code, port-0 CI, zero-copy vertex hot path. 42 methods / 8 domains. (**Wave 157k**)
- [x] loamSpine: **1,752+** tests. **G72 Tier 1 DONE**: url crate + ICU chain excised (-7 crates), chacha20poly1305 0.10→0.11. RustCrypto unified. Deep debt: test file refactoring + comprehensive audit. Doc hygiene + cargo clean. (**Wave 157i**)
- [x] sweetGrass: **1,746** tests, **89.62% coverage**. **G72 Tier 1 DONE**: tokio `["full"]`→7 explicit features, dead bincode/chrono removed. **P2 braid.verify behavioral tests CLOSED** (5 tests: unsigned braids, format validation, crypto-down permissive, not-found, attribution metadata). Batch + verify extracted into focused submodules. DH-0 (debt horizon zero). (**Wave 157i**) **Wave 157k rootPulse**: `rootpulse.attribute` + `rootpulse.query` + `braid.attribute` alias step handlers DONE. 50/50/50 translation registry alignment verified (zero gaps). Deep debt: env-configurable timeouts, zero-copy traversal, 3 file splits (<800L). 50 methods / 15 domains. Auto-announce functional, needs depot rebuild. (**Wave 157k**)
- [x] squirrel: **C8 DONE — -67,090 lines** total (Waves 156e→157c). 257K→190K lines, 16→12 crates, 4,090 tests. G66 transport abstraction. G65 protocol negotiation origin. 0 unsafe, 0 clippy. **`signal.dispatch` WIRED (G18).** (**Wave 157c**)
- [x] primalSpring: **1,253 tests (v0.9.50), 197 scenarios, 95 experiments.** **Wave 157g: ROLE SPLIT** — eastGate-resident code + deployment team (separated from overwatch). **biome.yaml consumption DONE**: composition module, `biome-eastgate.yaml` (14 primals, 3 compositions), `nucleus_launcher --biome`, exp122 37/37 PASS. `spine.list` routing gap CLOSED. **Wave 157k**: corrected atomic model propagated (SwarmVine added to Tower — 3→4, Node 6→7, Nest 7→8, NUCLEUS 10→11, ALL 13→14). `gossip` domain added to Tower/Node/Nest/FullNucleus required capabilities. Port 7800 registered. 25 test assertions updated. **Deploy health Phase 2 DONE** (`deploy_health.rs` + `nucleus_launcher fleet-health` + `query_fleet_health()`). **FleetDeployHealth wired into CLI** (`d15ab028`, v0.9.50). Dormant — interstadial. (**Wave 157k**)
- [x] skunkBat: 9 threat types, ConnectivityAnomaly, frame crypto, PUBLIC. **`metadata.analyze` shipped** (`e602e09`): 8-check gossip pre-accept validation for vine-bat loop. 672 tests.
- [x] **swarmVine — 186 tests, 90.8% coverage (Wave 157k)**. **Windows port DONE** (`1759b2a`): 4 UDS call sites → G66 transport abstraction, tarpc `#[cfg(unix)]`/`#[cfg(not(unix))]` gating, `tcp` feature enabled. **Deep debt** (`d963d47`): IPv6 bracketed loopback bypass fix, `/tmp/biomeos/` hardcoded paths → `platform_paths::runtime_socket_dir()`, hostname dedup, nonce lock contention eliminated. **Phase 4** (`1322d98`): `gossip.subscribe` with tokio broadcast channel, `BloomFilter` for CAS have-set membership (FNV-1a, zero deps), `ComputeCapacity` scheduling hints, `DepotManifest` + `DepotManifestEntry` for binary distribution gossip. Gossip.rs refactored (941→755 LOC). (**Wave 157d**) **Wave 157k EVOLUTION**: P2 riboCipher framing mismatch RESOLVED (accepts any ASCII-printable first byte). P2 relay method RESOLVED (`gossip.relay`). Zero-copy `Arc<str>` for `GossipEntry`. G65 protocol negotiation DEFAULT. 143→186 tests (+43), 6 integration, 3 benchmarks. Coverage 80.9%→90.8% line, 92.1% function. scyBorg triple license on all 25 source files. **Blocker #7 CLOSED** (`0e4cb75`): `#[cfg(unix)]` on `test_support.rs` + `tests/integration.rs` — blueGate Windows build now clean. (**Wave 157k**) **Wave 157k INTERSTADIAL**: `gossip.relay` topic fix CLOSED (`31e3e0a`) — extract topic from `payload.params.entries[0].topic`, default `"tower"`. **187 tests**. All swarmVine code items CLOSED. (**Wave 157k**)
- [x] **BTSP 15/15 → 16/16** — all primals shipped ClientHello (swarmVine inherits from sourDough scaffold)
- [x] Tower debt: 36 → **1** (grapheneGate HSM only)
- [x] songBird crypto delegation to bearDog: 6/6 seams DONE
- [x] Compositions fixed: `compute` and `nest` include Tower Atomic base primals
- [x] **G64 Cephalization — COMPLETE (Wave 156q)**: C2 dual-socket 15/15, tarpc convergent evolution.
- [x] **G65 Protocol Negotiation — COMPLETE (Wave 156q)**: Single-socket dual-protocol, 15/15 primals. squirrel origin, sourDough reference.
- [x] **G66 Transport Abstraction — COMPLETE (Wave 157a)**: Silicon-agnostic IPC. TransportEndpoint/TransportStream/connect_transport. sourDough reference. **15/15 pass Windows cross-arch.** petalTongue `9a5ed02`, skunkBat `7ef22f3`, squirrel `234fa514` completed the set.
- [x] **C8 squirrel excision — DONE (Wave 157b)**: -67,090 lines, 236 files, 16→12 crates.
- [x] **westGate jelly string elimination (Wave 156v)**: Python braiding pipeline → primal-native RPCs. 4-30x speedup. Neural API would have prevented this.
- [x] **hotSpring ↔ primal deduplication (Wave 157a)**: Audit complete. barraCuda needs to absorb `HardwareCalibration::probe()` + `PrecisionEval` (1,090 LOC). toadStool already replaces `low_level/` and `fleet_*`. 4 systems to push upstream, 6 already wired.
- [ ] **Inter-gate content.get E2E — MESH SCOPE WIRED**: songBird `content.locate` with `scope: "all"` now iterates mesh peers, sends `content.exists` probes, returns verified locations (westGate `a5dbe79b2`, 48/48 dispatch tests). **Unblocks nestgate.io Phase 3** (`/cas/{hash}`). Next: operational E2E test across live gates.
- [x] **G18 squirrel → biomeOS integration — LIVE ON IRONGATE**: squirrel rebuilt from source, `signal.dispatch` operational with 9 primal providers. Cross-primal routing validated (squirrel → rhizoCrypt 1ms, squirrel → bearDog crypto). esotericWebb + footPrint infrastructure confirmed ready. **NEXT**: wire footPrint agent panel (WebSocket → petal → squirrel).
- [x] **CODE OWNERSHIP RATIONALIZED (Wave 157k)**: eastGate (biomeOS, squirrel, projectNUCLEUS, primalSpring, overwatch), ironGate (bearDog, songBird, skunkBat, swarmVine, bingoCube, petalTongue, esotericWebb, footPrint — primal workhorse + 14TB NFT braid), strandGate (compute trio: toadStool, barraCuda, coralReef, hotSpring, rustChip), westGate (provenance trio + nestGate, wetSpring — data CAS 50.7TB), sporeGate (cellMembrane, lithoSpore, plasmidBin ops), graftGate (sourDough — darwin builder). Compute aligned to hardware specialization. All teams at 100% G65 + G66.
- [x] **Cross-arch 15/15 CLEAR (Wave 156z)**: petalTongue `9a5ed02` (TransportListener Phase 2), skunkBat `7ef22f3` (#[cfg(unix)] guards), squirrel `234fa514` (157d compliance). All pass `cargo check --target x86_64-pc-windows-gnu`.
- [ ] **1 known debt finding**: grapheneGate-readiness (HSM not on eastGate)
- [ ] Chimera Phase 0: library extraction (UNBLOCKED — crypto delegation done)

## 3. Hardware / Physical Topology

- [x] Mixed 10G + 1G topology LIVE — 10G AOC backbone between houses, MikroTik CRS310 + Omada SX3008F
- [x] sporeGate on R45 → MikroTik — plasma membrane router (NAT/DHCP/DNS/nftables)
- [x] eastGate on MikroTik LAN — code hub, 10G SFP+ direct, **64 GB DDR5** (upgraded from 32 GB, Wave 157a)
- [x] northGate enrolled (Windows 11, RTX 5090, 2.5G ethernet)
- [x] westGate ONLINE — AMD Ryzen 7 5700X / 64GB DDR4 / 2TB NVMe / **ZFS raidz1 50.7TB usable (rebuilt from mirrors) + 2TB L2ARC SSD**
- [x] ironGate HDD — 14TB + 1TB + 1TB + ~2TB, enclave experiment planned
- [x] blueGate + swiftGate: Windows, house2, 10G backbone proven
- [x] grapheneGate: Android, Tower LIVE (bearDog + songBird + skunkBat)
- [x] 10G AOC trunk CRS310↔Omada proven (blueGate reaches relay via backbone)
- [x] **TOPOLOGY_MAP.toml** has full physical layout with cytoplasm zone model
- [ ] **steamGate** (Steam Deck) — NEXT cross-platform gate. SteamOS (Arch, glibc). User-space deploy.
- [x] **graftGate** (M4 Mac Mini) — **FULLY ENMESHED (Wave 157k).** First `aarch64-apple-darwin` target. **15/15 primals compiled** (~98.1M Mach-O arm64). All 4 darwin failures FIXED upstream (toadStool, squirrel, petalTongue, bearDog). WG LIVE at **10.13.37.13**, 6 mesh peers, 38ms RTT. **Depot pushed**: 104M darwin binaries, BLAKE3 verified, 5th OS family in depot. iOS cross-compile live. Forgejo SSH + org access granted. sporePrint access granted.
- [x] **iosGate** (iPhone XS) — **FIRST DEPLOY (Wave 157k).** BearDogApp + mesh discovery app running. WiFi LAN peer discovery (7 gate IPs). 4 iOS Rust binaries built. 6th OS family. Free provisioning (7-day expiry). Future: sovereign iOS gate with Dev Program.
- [ ] fieldGate OFFLINE (dead CMOS)
- [x] **biomeGate ONLINE — Tower 4/4 + Node Atomic LIVE** — Threadripper 3970X (32c/64t), 128GB DDR4, Ubuntu 24.04.3 kernel 7.0.0-28. Reimaged Aug 13. Tower 4/4 from depot. Node Atomic trio source-built (toadStool+barraCuda GNU for Vulkan, coralReef depot). Ember fleet 4/4 GPUs: RTX 5060 (nvidia-open-595 Vulkan) + Titan V + 2x K80 (runtime vfio-pci). WireGuard UP (10.13.37.3). WG peer + SSH key **REGISTERED** (via sporeGate). 41/42 repos. Sovereign dispatch: 3 toadStool bugs fixed (zstd, D3hot, PRI faults), Exp 223-224 invalidated (false positive), cold boot blocked at HBM2 wall, warm handoff required. Team intermittent (science-track pacing).
- [ ] Complete port→gate mapping (CRS310 + Omada + TL-SG605S-M2)
- [ ] Document Flint H1 + Flint 2 + Omada WiFi bridge configs

### Gate Fleet — Status Matrix

| Gate | Status | Platform | Mesh IP | Composition | Role |
|------|--------|----------|---------|-------------|------|
| golgiBody | ONLINE | Linux | 10.13.37.1 | thin-relay | Sole depot, enrollment, Forgejo, Drawbridge |
| sporeGate | ONLINE | Linux | 10.13.37.2 | full | Topology owner, fallback builder, depot, cascade hub, **peptidoglycan anchor H1** |
| eastGate | ONLINE | Linux | 10.13.37.5 | full | Code hub, overwatch. i9-12900K, **64 GB DDR5**, Z790-P WIFI |
| ironGate | **NUCLEUS (13) — ORTHO CURRENT** | Linux | 10.13.37.7 | **NUCLEUS (13)** | **DOWNSTREAM HOST.** G18 DISPATCH LIVE (9 providers). 12.7 TB CAS. **166 caps, 2ms dispatch** (down from 9ms). **4 mesh peers** (up from 1). TCP 7800 listening. i9-14900K, RTX 5070, 94 GB. esotericWebb V32 + footPrint LIVE. **All 4 canary fixes DEPLOYED. Blocker #3 (--node-id) CLOSED.** |
| flockGate | **DOWN** | Linux | 10.13.37.6 | full | Rebooted, RustDesk locked out. esotericWebb → **ironGate** |
| northGate | ONLINE | Windows | 10.13.37.8 | full | RTX 5090. **DAILY DRIVER — DO NOT DEPLOY.** AlphaFold data source (~1TB). |
| grapheneGate | **TOWER 4-PRIMAL DEPLOYED** | Android | 10.13.37.7 (mobile) | tower (4) | **Pixel 8a.** beardog + songbird + skunkbat + swarmVine ALL ALIVE. SELinux: `--abstract` / `--no-uds` / `--disable-tarpc` workarounds. swarmVine cross-compiled on eastGate (2.3MB). **Missing biomeOS + cellMembrane for aarch64.** 12 binaries from Jun 10 (stale). |
| strandGate | **ORTHO CURRENT** | Linux | 10.13.37.10 | **NUCLEUS** | **SILICON FOLD + PHASE 1 CLEAR.** Campaign 22/45. GEMM PASS. RTX 3090 + RX 6950 XT + AKD1000. **Depot pushed Aug 12 (atomic rename for busy binaries).** |
| westGate | **ORTHO CURRENT (self-built)** | Linux | 10.13.37.11 | **NUCLEUS (14)** | **DATA NAS.** Rust-native pipeline. Signed commits. **44/44 repos cascaded. biomeOS rebuilt. `content.locate` mesh scope WIRED (`a5dbe79b2`). 5 gossip peers, 1,544 ingested. CAS federation progressing.** |
| blueGate | **NUCLEUS 13/13 — ENMESHED** | Windows | 10.13.37.12 | **NUCLEUS (13)** | **WINDOWS BUILDER — ENMESHED.** builder.serve `:9800` ALIVE (riboCipher TCP). 3 builds SUCCEEDED: songBird deep-debt, **swarmVine FIRST WINDOWS BUILD**, membrane enmesh. Depot 0/13 current (awaiting sporeGate dispatch). 5 Windows divergences documented (UDS→TCP fallback needed). |
| biomeGate | **ONLINE — Tower+Node** | Linux | 10.13.37.3 | compute | Threadripper 3970X, 128GB. Tower 4/4 depot + Node Atomic source-built. Ember fleet 4/4 GPUs (runtime VFIO). 3 toadStool bugs fixed. WG pending golgiBody peer. |
| swiftGate | HW READY | Windows | enrolling | tower (3) | Second Windows proof (after blueGate) |
| **reefGate** | **QUEUED** | Linux | — | nest | DDR3 NUC + DS224+ NFS. Enrollment queued post basement move (G44). |
| southGate | **INTERSTADIAL — 13/14** | Linux | **NO WG** (deliberate) | **NUCLEUS (13/14)** | **CANARY.** Cascade complete. neuralSpring GPU parity fix pushed (`4fa0c4c`). 71/80 validate. mesh.relay FIXED (param format remaining — ironGate). skunkBat fork storm cleaned. **SSH ready for enrollment** (port 22 open, key generated). 3 gossip peers, 4 LAN mesh. RTX 4060. **LAN IP: 192.168.4.148.** |
| **steamGate** | **NEXT** | SteamOS | — | tower (3) | Steam Deck. Portable compute. gnu bins in depot. |
| **graftGate** | **FULL NUCLEUS — ENMESHED** | macOS | 10.13.37.13 | **NUCLEUS (13)** | **M4 Mac Mini.** builder.serve `:9800` LIVE (launchd plist). **D12 FIXED** (swarmVine NUCLEUS launch: subcommand + socket path). D13 NEW (env var `${VAR}` expansion). **Depot 16/16 darwin** (was blurbed as 5/15 — corrected). 11/13 primal processes ACTIVE. iOS cross-compile live. ~~Upstream merge needed~~ → **D12/D13 MERGED** (`31da2861` + `3b1da444`). |
| **iosGate** | **FIRST DEPLOY** | iOS | — | tower (4) | **iPhone XS. FIRST DEPLOY ACHIEVED (Wave 157k).** BearDogApp + mesh discovery app running. WiFi LAN peer discovery (7 gate IPs). 4 iOS Rust binaries built (beardog 6.3M, songbird 17M, skunkbat 2.6M, swarmvine 2.1M). Free provisioning signed. **6th OS family proven.** |

### Gate × Team × Deployment Matrix — Rationalized Code-Team Placement (Wave 157i)

Each gate has a hardware specialization. Code teams (Cursor IDE sessions) should be hosted
on the gate whose hardware matches their domain. This reduces eastGate overload and aligns
compute with capability. **Overwatch is gate-agnostic** — locally delegated to eastGate for
coordination but not bound to any single gate.

| Gate | Role | Intended Code Teams (Cursor sessions) |
|------|------|---------------------------------------|
| **eastGate** | Orchestration hub, 64 GB DDR5, 10G | biomeOS, squirrel, projectNUCLEUS, primalSpring, blueFish + overwatch coordination |
| **ironGate** | Primal workhorse, RTX 5070, i9-14900K, 14TB HDD + NVMe | bearDog, songBird, skunkBat, swarmVine, bingoCube, petalTongue, esotericWebb, footPrint, tideGlass + 4 parked springs (NFT braid, primary Linux builder) |
| **strandGate** | Dedicated compute, RTX 3090, dual EPYC | Compute trio (toadStool, barraCuda, coralReef), hotSpring, rustChip, helixVision, initioChem. Batch HPC + science. |
| **westGate** | Data NAS, ZFS 50.7 TB, CAS federation | Provenance trio (rhizoCrypt, loamSpine, sweetGrass), nestGate, wetSpring, projectFOUNDATION (Nest Atomic) |
| **sporeGate** | Build + CI + depot, topology owner | cellMembrane, lithoSpore, plasmidBin ops. **Lean — pseudoSpore deployments.** |
| **graftGate** | darwin builder + FULL NUCLEUS, M4 Mac Mini | sourDough, Apple/darwin builds, iosGate prep |
| **blueGate** | Windows builder, Flint 2 bridge | Build-only sub-builder. **No code teams.** |
| **southGate** | Validation canary, RTX 4060, no WG | neuralSpring. Validation only. |
| **biomeGate** | Cross-vendor GPU lab, 4 VFIO GPUs | **ONLINE.** Tower 4/4 + Node Atomic. Sovereign dispatch research: HBM2 wall on Volta, warm handoff path next. K80 unsigned falcons = most tractable target. |

**Agent lifecycle**:
- **Tier 1 (Gate)**: Hardware overwatch agent — long-lived, rare restart. Gets universal `GATE_SPINUP_BLURB.md`.
- **Tier 2 (Code Team)**: Fresh agent per team — frequent restart. Gets user's K-NOME Blurb 1 (audit) + Blurb 2 (execute) from personal prompt bank on northGate.
- **Tier 3 (Ecosystem)**: Overwatch coordination. Gets `ECOSYSTEM_BLURB.md`.

Agent context is disposable and re-injectable. Persistent memory lives in Forgejo, wateringHole, specs, fossil records, and K-NOME documentation.

### Hardware Deployment Profile — Cross-Architecture Targeting (Wave 157i)

Profiles every deployment form factor the ecosystem can target — proven, imminent, and aspirational.

#### Tier A: Systems (Full OS, interactive or batch)

| Form Factor | Gate(s) | Hardware | Target Triple | Composition | Status |
|-------------|---------|----------|---------------|-------------|--------|
| Desktop/Tower | eastGate, ironGate, strandGate, biomeGate, southGate, flockGate | x86_64, 27-256 GB, optional GPU | `x86_64-unknown-linux-musl` | Full NUCLEUS | **PROVEN** |
| Windows Desktop | northGate, blueGate, swiftGate | x86_64, 62-96 GB | `x86_64-pc-windows-gnu` | Full NUCLEUS / tower-builder | **PROVEN** |
| NAS/Storage | westGate | Ryzen 7, 64 GB, ZFS 50.7 TB | `x86_64-unknown-linux-musl` | Nest Atomic | **PROVEN** |
| NUC/Mini PC | sporeGate | Ryzen 5 6600H NUC, 27 GB | `x86_64-unknown-linux-musl` | Full NUCLEUS | **PROVEN** |
| Mac Mini | graftGate | M4 Apple Silicon, 16 GB | `aarch64-apple-darwin` | Tower (15/15 compiled) | **PROVEN** |
| **Keyboard Computer** | **piGate** | **Raspberry Pi 500/500+**, Cortex-A76 2.4GHz, 8/16 GB, Vulkan 1.3 | `aarch64-unknown-linux-gnu` | Tower → NUCLEUS | **PLANNED** ($180-190) |
| **RISC-V SBC** | **riscGate** | **Milk-V Jupiter 2**, SpacemiT K3 8-core RVA23, up to 32 GB LPDDR5, **60 TOPS NPU**, 10GbE SFP+ | `riscv64gc-unknown-linux-gnu` | Tower → expand | **ON ORDER** (~$300+) |
| Handheld | steamGate | Steam Deck OLED, Zen 2, RDNA2 Vulkan 1.3 | `x86_64-unknown-linux-gnu` | Tower + Node Atomic | **QUEUED** |
| Cloud VM | cloudGate | Oracle Ampere A1 free tier | `aarch64-unknown-linux-gnu` | Tower | **GLACIAL** |
| NUC + NFS pair | reefGate | DDR3 NUC + Synology DS224+ | `x86_64-unknown-linux-musl` | Nest | **QUEUED** |

#### Tier B: Mobile / Tethered

| Form Factor | Gate | Hardware | Target Triple | Status |
|-------------|------|----------|---------------|--------|
| Android phone | grapheneGate | Pixel 8a (GrapheneOS) | `aarch64-unknown-linux-musl` | **PROVEN** — Tower LIVE |
| iOS phone | iosGate | iPhone XS | `aarch64-apple-ios` | **FIRST DEPLOY (Wave 157k)** — BearDogApp + mesh discovery running. 4 binaries built. 6th OS family. |

#### Tier C: Accelerator Cards (resources on Tier A hosts)

| Type | Hardware | Host Gate | Primal Consumer | Status |
|------|----------|-----------|-----------------|--------|
| NVIDIA GPU | RTX 5090 | northGate | toadStool, barraCuda, coralReef | LIVE (do-not-deploy gate) |
| NVIDIA GPU | RTX 5070 Ti | ironGate | toadStool, barraCuda, coralReef | **LIVE** — CUDA, SHADER_F64 |
| NVIDIA GPU | RTX 3090 | strandGate | hotSpring QCD, barraCuda | **LIVE** — DF64, 5,500 traj/hr |
| NVIDIA GPU | RTX 5060 | biomeGate | coralReef wgpu host | **LIVE** |
| NVIDIA GPU | RTX 4060 | southGate | validation canary | **LIVE** |
| NVIDIA VFIO | Titan V (GV100 SM70) | biomeGate | toadStool ember | **LIVE** — multi-gen validation |
| NVIDIA VFIO | K80 (GK210×2 SM37) | biomeGate | toadStool ember | **LIVE** — cross-gen quench |
| AMD GPU | RX 6950 XT | strandGate | barraCuda, coralReef | **LIVE** — Infinity Cache advantage |
| NPU (PCIe) | BrainChip Akida AKD1000 | strandGate | toadStool, rustChip | **LIVE** — 20,545 Hz inference |
| **RISC-V NPU** | **SpacemiT A100** (60 TOPS) | **riscGate** (on-SoC) | toadStool, squirrel | **INCOMING** — INT4/INT8/FP16 |
| FPGA | None in fleet | — | toadStool stubs only | Not planned |

#### Tier D: Edge / IoT / Constrained

| Device | Target | RAM | Feasibility |
|--------|--------|-----|-------------|
| Pi Zero 2W | `armv7-unknown-linux-musleabihf` | 512 MB | bearDog-only beacon. Not a gate. |
| CanaKit Pi 3B+ (2018) | `armv7` / `aarch64` | 1 GB | Below resource floor. Not enrolling. |
| Synology DS224+ | Intel J4125 (DSM) | 2 GB | NFS storage only. No primals on DSM. |
| WASM edge | `wasm32-unknown-unknown` / `wasm32-wasip1` | N/A | 38/48 toadStool crates. Browser compute surface. |

#### Tier E: Exotic / Aspirational (type-check proven, no hardware)

| Target | Platform | Notes |
|--------|----------|-------|
| `powerpc64le-unknown-linux-gnu` | IBM POWER10 HPC | Type-check only |
| `s390x-unknown-linux-gnu` | IBM Z mainframe | Type-check only |
| `loongarch64-unknown-linux-gnu` | Loongson (Chinese sovereign) | Type-check only |
| `sparc64-unknown-linux-gnu` | Oracle SPARC | Type-check only |
| `i686-unknown-linux-gnu` | 32-bit x86 legacy | Type-check only |
| `x86_64-unknown-freebsd` | BSD family | Type-check only |
| `x86_64-unknown-illumos` | Solaris lineage (ZFS origin) | Type-check only |
| `x86_64-unknown-none` | Bare metal x86_64 | ecoPrimals-as-OS concept |
| `aarch64-unknown-none` | Bare metal ARM64 | ecoPrimals-as-OS concept |
| `riscv64gc-unknown-none-elf` | Bare metal RISC-V | ecoPrimals-as-OS concept |

#### ISA × OS Coverage Matrix

| ISA | Linux (musl) | Linux (gnu) | Windows | macOS | Android | iOS | WASM | Bare Metal |
|-----|-------------|-------------|---------|-------|---------|-----|------|------------|
| **x86_64** | PROVEN (6 gates) | PROVEN (GPU layer) | PROVEN (3 gates) | type-check | — | — | PROVEN (38/48) | type-check |
| **aarch64** | PROVEN (grapheneGate) | PLANNED (piGate) | type-check | **PROVEN 15/15** (graftGate) | PROVEN (grapheneGate) | **FIRST DEPLOY** (iosGate) | — | type-check |
| **riscv64** | — | ON ORDER (riscGate) | — | — | — | — | — | type-check |
| **armv7** | depot exists | type-check | — | — | — | — | — | — |

#### Deployment Scenario Matrix

| Scenario | Hardware | Composition | Network | Key Proof |
|----------|----------|-------------|---------|-----------|
| Classroom demo | Pi 500 + HDMI monitor | Tower or NUCLEUS | WiFi → drawbridge → golgiBody | $200 live mesh node for students |
| Conference booth | Pi 500 + portable monitor | NUCLEUS | Phone tether or venue WiFi | Sovereign OS on a keyboard |
| Edge AI | Jupiter 2 | Tower + toadStool + squirrel | 10GbE SFP+ or WiFi 6 | 60 TOPS RISC-V inference |
| Portable compute | Steam Deck | Tower + Node Atomic | WiFi | GPU compute from a handheld |
| Home NAS | westGate / reefGate | Nest Atomic | GigE LAN | Provenance-tracked personal data |
| GPU farm | strandGate / biomeGate | Node Atomic / Compute | 10G backbone | QCD, shader validation, silicon deism |
| WAN proof | cloudGate (Oracle ARM) | Tower | WAN → drawbridge | Trust-boundary crossing, NAT traversal |
| Mobile anchor | grapheneGate (Pixel 8a) | Tower | USB tether / WiFi | Beacon seed, physical root of trust |
| Build farm | blueGate + graftGate + sporeGate | tower-builder | LAN mesh | Cross-platform depot: 3 OS families |

## 4. K-Derm Layers — Connectivity Fabric + Three-Domain Topology

Three-layer model identified by peptidoglycan failure incident (Wave 155d).
**Wave 155v**: formalized as **THREE-DOMAIN TOPOLOGY SPEC** (`specs/THREE_DOMAIN_TOPOLOGY_SPEC.md`) mapping each k-derm layer to a DNS domain: primals.eco (outer), nestgate.io (peptidoglycan), primal.eco (inner).
**Wave 155v/156d**: **K-DERM SEPARATION COMPLETE** — primal.eco 6 A records REMOVED from sovereign Knot DNS (inner membrane SEALED). nestgate.io LIVE on mesh (petalTongue v1.7.0). DNSSEC verified. Caddyfile synced from golgi (14 subdomain routes). dnsmasq config ready for inner membrane resolution. `KDERM_DNS_ACTIONS.md` documents remaining ops items.

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
│  Route: songBird :7700 LAN-first + WG fallback          │
│  Auth: capability IPC, TLS, BTSP (15/15), riboCipher    │
│  Owner: per-primal, coordinated by overwatch             │
│  Status: 10-gate mesh, Tower LIVE on 6+ gates, Nest LIVE │
│  Gossip: swarmVine (primal #16) — vine spreads, bat val │
│  Evolution: Phase 2 riboCipher, Phase 3 swarmVine gossip│
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
- [ ] **G29 — Peptidoglycan isomorphism**: DNS is a recurring SPOF. sporeGate dnsmasq dies → all LAN gates lose resolution. strandGate DNS dead (Aug 1). northGate 2-3s page delays (DNS timeout + fallback). Not fully isomorphic yet.
- [ ] DNS: verify dnsmasq on all Linux gates (sporeGate done, others PENDING)
- [ ] northGate DNS delay diagnosis (DNS timeout pattern — likely single-DNS DHCP + slow fallback)
- [ ] strandGate DNS dead (Aug 1, 2026) — systemd-resolved has no working upstream. sporeGate dnsmasq likely down again.
- [ ] Redundant DNS: DHCP should hand out 2+ DNS servers (sporeGate dnsmasq + 1.1.1.1 fallback)
- [ ] dnsmasq health monitor + auto-restart on sporeGate (systemd watchdog or cellMembrane health check)
- [ ] Port→gate mapping incomplete (need physical audit)
- [ ] WiFi bridge documentation (Flint H1 + Flint 2 configs)
- [ ] Standardized gate provisioning script (DNS + RustDesk + health checks)

### Inner Membrane

- [x] **10-gate WireGuard mesh** — golgi, sporeGate, eastGate, flockGate, ironGate, northGate, grapheneGate, westGate, strandGate, **blueGate** (peer #9)
- [x] Tower Atomic LIVE on 6+ gates — westGate, strandGate, grapheneGate, eastGate, sporeGate, blueGate (Windows)
- [x] LAN peering: Tower 353x LAN (0.45ms vs 158ms WG overlay)
- [x] songBird universal-ipc: UDS/named pipes/abstract sockets/TCP
- [x] BTSP defense-in-depth: **16/16** primals (swarmVine from sourDough scaffold)
- [x] **biomeOS neuralAPI**: **27** signal graphs, **v4.57+**: Stage 2 routing infra shipped (578 Neural API tests). G22 convergence (unified namespace, 244 caps). westGate 26 caps registered. `capability.resolve` working. Deploy sequence evolving to register-gossip-verify-in-mesh. **swarmVine gossip integration NEXT** — `capability.resolve` will query swarmVine gossip table for cross-gate routing. (8,700+ tests)
- [x] **songBird ACME HTTP-01** challenge responder shipped — Phase 1 TLS elimination
- [x] songBird mesh refactor: enrollment crypto + mesh helpers extracted, all files <800L
- [x] sporeGate depot fully refreshed: health **11/11 HEALTHY**, **49 binaries** (18 musl + 16 gnu + 15 windows), BLAKE3 verified. swarmVine binary added. **Ortho cascade: 15/15 musl REBUILT from current HEADs. Fleet pushed to 4 gates. Provenance gap (swarmVine + membrane) FIXED. `membrane-cascade.service` path drift FIXED.**
- [x] **Sovereign CI LIVE** — push-to-deploy E2E verified. **Golgi hook FIXED** (3 bugs: dispatcher, case, category).
- [x] ~~WireGuard DNS catch-all~~ — **FIXED** (cellMembrane `8d9bb58`)
- [x] ~~Socket ownership P2~~ — **FIXED** (biomeOS `0e45262f` + v4.54 socket ownership guard)
- [x] ~~rootpulse.ledger~~ — **FIXED** (cellMembrane `0cfcce5`: advisory OK)
- [x] ~~**P2: Sandbox false positive**~~ — **FIXED** (coevolution: cellMembrane `validate_with_deps()` → biomeOS `composition.test_swap`). Depot now serves v4.55.
- [ ] `/run/membrane` permission reset — biomeOS resets dir to 0770 at runtime (P3)

## 5. Sovereignty / Trust — postPrimordial Alignment Check

### Sovereignty Principles — Status

| Principle | Status | Evidence |
|-----------|--------|----------|
| **No external dependencies** | **ALIGNED + G72 TIER 1 COMPLETE** | Pure-Rust TLS. Zero C deps on critical path. **G72 Tier 1 DONE (11/11 teams)**: ~155+ crates shed, tokio surfaces trimmed/gated, dead deps excised (jsonrpsee, wiremock, vulkano, url+ICU, bearDog +41 deps, petalTongue telemetry). **Tier 2 QUEUED**: HTTP client consolidation (reqwest/ureq/hyper → songBird/capability.call), axum 0.7→0.8, wgpu 22→28. |
| **Single source of truth** | **ALIGNED** | Forgejo (golgiBody) is sole canonical remote. GitHub is push-mirror only. |
| **Sole depot** | **ALIGNED** | All genomeBins from `depot.primals.eco`. Sovereign CI auto-publishes. |
| **Portable mesh** | **PROVEN on 7 NUCLEUS gates** | NUCLEUS proven on 7 gates across 5 OS families. southGate validates without WireGuard. graftGate FULL NUCLEUS on darwin via biomeOS Neural API (<60s). iosGate FIRST DEPLOY. Portability for external deployments validated. |
| **Silicon deism** | **G66 COMPLETE — PROVEN on 5 platforms** | Linux (musl+gnu), Windows (windows-gnu), Android (aarch64), **macOS (aarch64-apple-darwin — 15/15 compiled, FULL NUCLEUS)**, **iOS (aarch64-apple-ios — 4 binaries, FIRST DEPLOY)**. G66 transport abstraction 15/15. SteamOS NEXT. **5 OS families proven, 6th (iOS) first deploy.** |
| **Zero telemetry** | **ALIGNED** | No telemetry, no analytics, no cloud lock-in across all primals. |
| **AGPL-3.0** | **ALIGNED** | All primals, gardens, springs. scyBorg triple-license framework defined. |
| **Pure Rust crypto** | **ALIGNED** | bearDog Ed25519 signing, BTSP 16/16, riboCipher transport. swarmVine inherits full crypto from sourDough scaffold. |
| **Self-healing** | **ALIGNED + GATE VALIDATED** | biomeOS v4.55: dual-protocol health ping, PID-aware kill-before-spawn, socket ownership guard. westGate: 0% socket loss. strandGate: 1 proc/primal. |

### Interstitial Goals — Alignment

| Goal | Status | Notes |
|------|--------|-------|
| **Reconstitutable from cold** | **VALIDATING (southGate)** | Depot has all binaries, Forgejo has all source. southGate is testing: deploy from public depot, own keys, no WireGuard, no `/etc/environment` inheritance. If NUCLEUS launches clean, reconstitution is proven. |
| **Move to new HPC mesh** | **VALIDATING (southGate)** | southGate = "friend's LAN pool" archetype. Deliberately off WireGuard. If it can bond, accept encrypted work, and return signed results across a trust boundary, the system is portable to any network. |
| **Shut down and restart** | **PARTIAL** | biomeOS `nucleus start` works. But `/run/membrane` is tmpfs, socket permissions reset, no systemd tmpfiles.d. Each gate restart requires manual fixup. |
| **No convenience coupling** | **RISK** | sporeGate's `/etc/environment` with `RUSTUP_HOME`, `CARGO_HOME`, `ECOPRIMALS_ROOT` is gate-specific. SSH key aliases (`golgi`) are in user-specific configs. These are jelly strings. |

- [x] K-Derm three-layer model intact (peptidoglycan documented)
- [x] Forgejo sovereign inner membrane operational (43/43 repos)
- [x] Push mirrors relay to GitHub on commit
- [x] Sovereign outer membrane operational (Caddy TLS)
- [x] S1-S4 sovereignty shadows ALL GRADUATED
- [x] **DNSSEC 3/3 domains complete** — primals.eco DS 2371/13/2 chain VERIFIED (Porkbun → .eco TLD → Cloudflare KSK). nestgate.io + primal.eco signed by sovereign Knot DNS (ECDSA P-256, auto re-sign).
- [x] RustDesk AGPL-3.0 compliant — learn-from-leverage posture
- [x] **Sovereign CI LIVE** — push-to-deploy, depot auto-built, BLAKE3 verified
- [x] Crash-loop self-recovery LIVE — app breaker + systemd layers
- [x] Tower Atomic EXCEEDS WG (353x LAN, 1.7x WAN)
- [x] 6/6 exploration domains PROVEN LIVE
- [x] Genetic enrollment — two-layer trust
- [x] BTSP defense-in-depth (16/16)
- [x] Depot provenance — builder=sporeGate, staleness alarm, multi-target
- [x] Crypto delegation — songBird → bearDog, chimera unblocked
- [x] golgiBody sole depot — no local depots, all genomeBins via Caddy TLS
- [x] **cellMembrane reqwest purged** — sovereign HTTP client, pure-Rust TLS
- [x] **Provenance 7/7** — full E2E signed chain, portable across Linux + Windows
- [ ] **PORTABILITY**: cellMembrane site-profile abstraction (decouple from 192.168.4.0/22)
- [ ] **PORTABILITY**: WireGuard endpoint auto-discovery (no hardcoded IPs in peer config)
- [ ] **PORTABILITY**: Depot mirror/relocate (golgiBody is single point of failure)
- [ ] **PORTABILITY**: `pseudoSpore pack/unpack` — reconstitute gate from seed file
- [ ] Phase 2: Tower cutover — shadow active, chimera design drafted
- [ ] Phase 1: Zola → sporePrint primal pipeline (crates.io a sub-goal)
- [ ] Phase 2: Forgejo → rootPulse — via Nest Atomic
- [x] `primal.eco` inner membrane separation — **COMPLETE.** 6 A records removed from Knot DNS. Zero public records. dnsmasq config ready for LAN resolution. Inner membrane SEALED.

## ~~6. Public Surface / Security~~ → **FOSSILIZED as F12** (Wave 155i)

ALL SECURITY ITEMS RESOLVED. sporePrint impulses are an ongoing publishing cadence, not a security concern — tracked under D11 (Campus). Moved to Fossilized section below.

## 7. Compositions / Products — NUCLEUS Convergence

### Atomic Composition Status

```
Tower Atomic = bearDog + songBird + skunkBat + swarmVine
               (security + routing + defense + gossip — the shared electron cloud)

Nest Atomic  = Tower + nestGate + rhizoCrypt + loamSpine + sweetGrass
               (Tower provides crypto/routing; Nest adds CAS + DAG + spine + braids)

Node Atomic  = Tower + toadStool + barraCuda + coralReef
               (Tower provides crypto/routing; Node adds dispatch + GPU + shaders)

NUCLEUS      = Tower + Nest + Node + surfaces/interactions
             + biomeOS    (Hamiltonian — orchestrator + force carrier via Neural API)
             + petalTongue (photon — visualization surface)
             + squirrel    (observer — AI agent surface)
             + cellMembrane (membrane — sovereignty boundary)

Bonding model: Tower is the electron — shared across all compositions like
electrons in chemical bonds (covalent, ionic, metallic). Nest and Node always
include Tower. A gate running "just Nest" has Tower's security substrate.

Genetics hierarchy (bearDog):
  mitoBeacon  → "Are you family?"     (shared family seed, riboCipher hears birdSong)
  Nuclear     → "Which individual?"   (gate authority, derivation distance → trust tier)
  Genetic child → "What did we make?" (fresh spawn at every meaningful interaction)
```

| Composition | Status | Gates Proven | biomeOS Orchestrated? |
|-------------|--------|--------------|----------------------|
| **Tower Atomic** (4: bearDog, songBird, skunkBat, swarmVine) | LIVE | 7+ gates (Linux, Windows, Android, macOS, iOS) | Signal graphs: 8. Direct IPC: YES. Shared electron cloud — present in all compositions. |
| **Nest Atomic** (Tower + nestGate, rhizoCrypt, loamSpine, sweetGrass) | LIVE | westGate (ZFS+CAS), blueGate (Windows) | Signal graphs: 9. Graph execution: **FIXED** (v4.47 riboCipher). Tower provides bearDog crypto for provenance chain. |
| **Node Atomic** (Tower + toadStool, barraCuda, coralReef) | VALIDATED | strandGate (746 pipelines/sec, sub-ms GPU) | Signal graphs: 3. Tower provides gossip for compute advertising. |
| **NUCLEUS** (13+3) | **ACHIEVED ×7 — ZERO P0. NEURAL API VALIDATED AS COMPOSITION AUTHORITY. 16 PRIMALS.** | **sporeGate** (15/15), **ironGate** (13/13), **westGate** (13/13, NG-05 done), **strandGate** (13/13), **blueGate** (13/13), **southGate** (13/13), **graftGate** (13/13, 1830 caps, 21 domains — first darwin NUCLEUS via biomeOS `nucleus start --mode full`) | 27 signal graphs. **All P0s resolved. Mesh-native build dispatch. Deploy evolves: pull → restart → register → gossip-announce → verify-in-mesh. Deployment signaling gap identified — biomeOS needs `deploy.result` gossip emission for automated convergence (see DEPLOYMENT_SIGNALING_EVOLUTION_SPEC.md).** |

### What's proven

- [x] footPrint LIVE — **708 TS tests, Phase 2 DEPLOYED on ironGate.** CAS E2E. golgi Caddy routing DONE.
- [x] esotericWebb LIVE — **V32, 484+ tests, CELL LIVE on ironGate (13/13 ALIVE).** G68 redeployed. 28 caps, `nest.store` signal decomposition.
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
- [x] **Springs-to-NUCLEUS mesh** — 10 springs/gardens assigned to 5 gates. Cell graphs v2.0.0 with content.get/content.put. biomeOS deploy graphs v2.0.0. tideGlass Cargo workspace created. Inter-gate CAS data access documented.
- [x] **ironGate DOWNSTREAM HOST (Aug 3, G68 redeployed Aug 8)** — esotericWebb V32 (CELL LIVE, 13/13 ALIVE) + footPrint 708 tests (Phase 2 deploy ready). NUCLEUS 13/13. RTX 5070. G19 PROVEN. riboCipher transport validated. BTSP local-trust (G63) is remaining CAS blocker.
- [x] **Wave 155v/156d BROAD EVOLUTION ABSORBED (Aug 4)** — Provenance divergence RESOLVED (122×). Three-domain topology spec'd. 12⁴ paper-ready. Federated CAS + compute memoization spec'd. Nanowire→Primal Builder Phase 2a DONE. squirrel pushed (156d sovereignty). ~135K+ tests. 20 docs fossilized (94 total).

### Path to NUCLEUS — ALL CODE SHIPPED

- [x] ~~**biomeOS graph executor riboCipher fix**~~ — **SHIPPED** (v4.47 `bd202674`)
- [x] ~~**biomeOS socket unification**~~ — **SHIPPED** (unified to `membrane/`, 22 graph TOMLs)
- [x] ~~**biomeOS socket evaporation**~~ — **SHIPPED** (capability persistence to disk)
- [x] ~~**biomeOS full composition lifecycle**~~ — **SHIPPED** (`composition.start` RPC + boot_order integration)
- [x] ~~**bearDog `crypto.sign_ed25519`**~~ — **SHIPPED** (`3739e7078`) — Provenance 7/7 UNBLOCKED
- [x] ~~**Node Atomic live**~~ — strandGate VALIDATED (746 pipelines/sec)
- [x] ~~**NUCLEUS live on one gate**~~ — strandGate + blueGate + sporeGate (v4.47 deployed)
- [x] ~~**NUCLEUS lifecycle**~~ — **SHIPPED** (biomeOS `composition.start` + cellMembrane boot_order)
- [x] ~~**Primal CLI flag standardization**~~ — **SHIPPED** (`specs/PRIMAL_BIND_FLAGS_STANDARD.md`)

### Remaining (deployment + glacial)

- [x] ~~Provenance 7/7 live validation~~ — **COMPLETE** on westGate (Linux/ZFS) + blueGate (Windows)
- [x] ~~westGate NUCLEUS~~ — **DONE** (13/13, 654 caps, 29 sockets, Prov 7/7)
- [x] ~~blueGate lifecycle NUCLEUS~~ — **DONE** (14/14 depot, Prov 7/7 on Windows). **Wave 157c: PRIMARY BUILD AUTHORITY** — 14/14 vertebrate built (23 min), `builder.serve :9800` mesh-native dispatch (Tower Atomic, no SSH). Build authorities: `[blueGate, sporeGate, eastGate]`. 7/14 match depot size within 1%. Logged D1-D4 (songBird PID P2, skunkBat bind-mode, binary size parity P3, petalTongue port P4).
- [x] ~~strandGate redeploy~~ — **v4.55 depot deploy, P1 GATE VALIDATED**: 12/12 HEALTHY, 1,017 methods, 13 procs (1 each).
- [x] ~~**Coevolution (G21)**~~ — **COMPLETE**: biomeOS `composition.test_swap` + cellMembrane `validate_with_deps`. Mode gap FIXED. Depot rebuilt.
- [x] **graftGate FULL NUCLEUS (Wave 157k)** — biomeOS Neural API `nucleus start --mode full`, 21 ACTIVE domains, 1830 caps, <60s. 10 divergences documented (D1-D10). Cross-deployment architecture assessment filed.
- [x] **iosGate FIRST DEPLOY (Wave 157k)** — BearDogApp + mesh discovery running on iPhone XS. WiFi LAN peer discovery (7 gate IPs). 4 iOS Rust binaries. **6th OS family proven.** Free provisioning (7-day expiry).
- [ ] **Cross-platform gates remaining** — steamGate (NEXT, UNBLOCKED)
- [ ] **Chimera Phase 0**: shared library extraction (`libtower.so`) — UNBLOCKED, deferred
- [ ] sporePrint primal pipeline: replace Zola
- [ ] 6 springs pending `validation.json`

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
- [x] ~~Windows genomeBins stale~~ — **15/15 REBUILT** (sporeGate Jul 30). membrane.exe NEW. ALL platform gates fixed.
- [x] ~~**songBird Windows platform gate (P0)**~~ — **FIXED + IN DEPOT** (`d9bda555`)
- [x] ~~toadstool.exe~~ **FIXED**. ~~coralreef.exe~~ **FIXED**. ~~beardog.exe~~ **FIXED**. ~~membrane.exe~~ **FIXED** (`4ccbab1`)
- [x] **Depot: 49+ binaries across 5 target directories** (18 musl, 16 gnu, 15 windows-gnu, + aarch64-musl, aarch64-android dirs). swarmVine v0.1.0 (2.4 MB musl) added.
- [x] **Windows cross-arch 15/15 PASS** — `cargo check --target x86_64-pc-windows-gnu` mandated as pre-push. All 15 primals pass (Wave 156z). Not yet in CI automation.
- [x] **macOS genomeBins — 15/15 compiled + FULL NUCLEUS** — can't cross-compile from Linux. **graftGate: 15/15 compiled** (Wave 157k). All 4 darwin failures FIXED upstream (toadStool cfg gate, squirrel target override, petalTongue rustix API, bearDog import). Depot pushed (104M, BLAKE3). **FULL NUCLEUS via biomeOS Neural API** (21 domains, 1830 caps). cellMembrane `InitSystem::Launchd` path to be validated.
- [ ] **SteamOS validation** — gnu depot bins may work as-is on Steam Deck (user-space deploy)
- [ ] `target`/`bind_mode` field removal — primals auto-detect, depot negotiates
- [ ] systemd abstraction for launchd paths (cellMembrane `InitSystem` foundation shipped, darwin untested)

## 13. Vertebrate Evolution — Internal Structure via Abstraction (Wave 157a)

**Phase shift**: Cephalization (G64) gave the ecosystem a nervous system — Neural API, biomeOS routing, Tower mesh. Now primals develop **internal skeletal structure**: shared abstractions across crates, domain delegation to the right primal/spring, self-audit for cross-focus that belongs elsewhere. **Vertebrates vs invertebrates** — the primals that evolved first carry early patterns (repeated connect/send/recv, game engines in viz primals, monolithic cores). The newer primals (swarmVine, skunkBat) are already vertebrate — clean, single-domain, minimal deps.

**Philosophy**: Lean by evolution, not excision. No feature-gating. Code moves to its right home. Patterns converge through shared traits. westGate's 7-session retrospective revealed 6 Python jelly strings that exist because primal API surfaces diverged from assumptions — the vertebrate fix is primal self-audit: each team verifies their actual API surface matches what others expect.

| Primal | Binary | Deps | Crates | Lines | Evolution Path |
|--------|--------|------|--------|-------|----------------|
| petalTongue | **33.8 MB** | **656** | 19 | 209K | **doom-core → ludoSpring** (game rendering belongs in a spring). 656 deps need workspace convergence. |
| songBird | **23.8 MB** | 646 | **31** | **470K** | ~~Transport trait~~ DONE. ~~Gossip excision~~ DONE. ~~PID~~ FIXED. ~~riboCipher :7700~~ DONE. **Vertebrate evolution COMPLETE.** |
| biomeOS | **20.4 MB** | 377 | 26 | 302K | P0-C IN DEPOT. Generic capability dispatch. FD self-healing. riboCipher Tier 2 client pool. G69 depot lineage templates. |
| toadStool | **12.4 MB** | 627 | 14 | **708K** | **`core` 272K → natural S371 WASM split.** 24/48 done. |
| bearDog | **8.3 MB** | 556 | **31** | 498K | ~~P0-A~~ **FIXED + IN DEPOT**. Spine signing unblocked. |
| nestGate | **8.5 MB** | 424 | — | — | ~~P0-B~~ RESOLVED. `content.ingest` shipped S136, stale depot was root cause. `content.stat` shipped. Rebuilt. |
| swarmVine | **2.5 MB** | 113 | 2 | 4K | **Vertebrate baseline** — Windows port DONE, Phase 4 shipped, **186 tests, 90.8% coverage**. P2 riboCipher + relay RESOLVED. G65 default. scyBorg triple license. |
| skunkBat | **3.2 MB** | 156 | 4 | 24K | Vertebrate. |
| sourDough | **3.3 MB** | 212 | 3 | 23K | Vertebrate. |

**Evolutionary action items — primals self-audit:**
- [x] **songBird**: ~~(1) Transport convergence~~ **SHIPPED** (`TransportRegistry` + boxed-closure adapter, graceful shutdown wired). ~~(2) Gossip excision~~ **SHIPPED** (`mesh.capabilities_announce`/`revoke` → swarmVine `gossip.forward` UDS). ~~(3) P2 PID~~ **FIXED** (`cleanup_legacy_pid_files()`).
- [ ] **petalTongue**: Move `doom-core` to **ludoSpring** (already optional `doom = ["dep:doom-core"]`). `/ws/scene` WebSocket SHIPPED (G19 foundation).
- [x] **bearDog**: ~~P0-A~~ **FIXED + IN DEPOT** — health guard deployed fleet-wide. Spine signing unblocked.
- [x] **nestGate**: ~~P0-B~~ RESOLVED — `content.ingest` shipped S136, `content.stat` shipped. Rebuilt + deployed.
- [x] **biomeOS**: ~~P0-C~~ **FIXED + IN DEPOT** (`6a51638d`) — `capability.call` operational fleet-wide.
- [ ] **toadStool**: S371 naturally splitting `core` 272K. Continue.
- [x] **All primals**: ~~Self-audit~~ **COMPLETE** — all 13+ primals verified RPC surface matches capability_registry.toml. bearDog, songBird, biomeOS, nestGate, loamSpine, rhizoCrypt, barraCuda, coralReef, cellMembrane, squirrel, skunkBat all self-audited. Zero phantom methods fleet-wide.
- [ ] **Dep convergence → G72 Dependency Pandemic — TIER 1 COMPLETE**: **11/11 teams responded. ~155+ crates shed fleet-wide.** rhizoCrypt: 316→270 (-14.6%). nestGate: 424→414 (-10) + S147/S148 crate surgery. loamSpine: 306→299 (-7). toadStool: 7 dead deps + 6 workspace-promoted. sweetGrass: bincode/chrono removed. coralReef: optional dep gating. cellMembrane: time/macros trimmed. tideGlass: tokio→current-thread. wetSpring: verified clean. **bearDog: +41 dead deps removed, tokio["full"] eliminated.** **petalTongue: telemetry crate removed, runtime discovery replaces 13 hardcoded peers.** **Tier 2 QUEUED.** See `specs/DEPENDENCY_PANDEMIC_SPEC.md`.
- [ ] **Depot**: Track binary sizes in `sizes.toml` for regression detection.

## ~~9. Documentation / Fossil Record~~ → **FOSSILIZED as F11** (Wave 155h)

ALL ITEMS RESOLVED. Moved to Fossilized section below.

## ~~10. Jelly Strings~~ → **FOSSILIZED as F14** (Wave 156h)

ALL ITEMS RESOLVED. J9–J19 (11/11 KILLED or LIVE E2E). J12 evolution (SSH → songBird IPC) is a G62 concern, not a jelly string. Moved to Fossilized section below.

## 12. gen5 — Full NUCLEUS as Live Platform (NEW)

gen4 is COMPLETE (4 NUCLEUS gates on v4.55, Provenance 7/7, Sovereign CI, coevolution).
gen5 is **NUCLEUS as a usable platform** — validated by strandGate Node Atomic landmark:
2,130 matmul/sec, cross-atomic provenance E2E (GPU→sign→verify→DAG→attribution→Merkle),
W3C PROV-O, AlphaFold 20-30 structures/day capacity. **gen5 thesis VALIDATED.**

### The Full NUCLEUS Stack — Graph of Sub-Graphs

NUCLEUS is not a flat list of primals — it is a **graph of composition sub-graphs**.
Each atomic composition is a sub-graph with internal dependency ordering.
Tower Atomic is the **shared electron cloud** — present in every composition
(bonding model: like electrons in covalent/ionic/metallic bonds). Nest and
Node always include Tower. `biome.yaml` defines which sub-graphs a gate runs.
biomeOS is both graph executor (Hamiltonian) and force carrier (Neural API
mediates interactions between atomics).

```
┌─────────────────────────────────────────────────────────┐
│  NUCLEUS = graph(Tower, Nest, Node, surfaces)            │
│  biome.yaml = composition manifest (BYOB per gate)       │
│  biomeOS = Hamiltonian (orchestrator + force carrier)     │
├─────────────────────────────────────────────────────────┤
│  ┌─── Tower Atomic (shared electron cloud) ──┐           │
│  │ bearDog → songBird → skunkBat → swarmVine  │  shared  │
│  │ (genetics)  (routing) (defense)  (gossip)  │  across  │
│  └───────────────────────────────────────────┘  all      │
│                                                          │
│  ┌─── Nest Atomic (Tower + data) ─────────┐              │
│  │ Tower + nestGate → rhizoCrypt →         │  CAS + DAG  │
│  │         loamSpine → sweetGrass          │  + braids   │
│  └────────────────────────────────────────┘              │
│                                                          │
│  ┌─── Node Atomic (Tower + compute) ──────┐              │
│  │ Tower + toadStool → barraCuda →         │  dispatch   │
│  │         coralReef                       │  + shaders  │
│  └────────────────────────────────────────┘              │
│                                                          │
│  ┌─── Surfaces / Interactions ────────────┐              │
│  │ biomeOS    (Hamiltonian + force carrier)│              │
│  │ petalTongue (photon — viz surface)      │              │
│  │ squirrel    (observer — AI agent)       │              │
│  │ cellMembrane (membrane — sovereignty)   │              │
│  └────────────────────────────────────────┘              │
├─────────────────────────────────────────────────────────┤
│  Genetics: mitoBeacon (family) → nuclear (gate) →        │
│  genetic child (interaction) — bearDog manages all       │
│  Bond escalation: weak→ionic→metallic→covalent           │
├─────────────────────────────────────────────────────────┤
│  primalSpring = experimental ground for compositions     │
│  Prototypes biome.yaml, validates sub-graph lifecycle    │
└─────────────────────────────────────────────────────────┘
```

### What NUCLEUS Enables — gen5 Workloads

| Workload | Stack | Gate(s) | Status |
|----------|-------|---------|--------|
| **Scientific visualization** | hotSpring → toadStool → petalTongue (QCD, molecular) | westGate, strandGate | Node Atomic validated, petalTongue WASM ready |
| **Game engine / creative** | esotericWebb → petalTongue → coralReef (shaders, WebGL) | **ironGate** (downstream host) | **V32, 484+ tests, CELL LIVE on ironGate (13/13).** G68 redeployed. 28 caps. Needs petalTongue WebGL pipeline (G19) for browser surface. |
| **AI agent orchestration** | squirrel (4,613 tests, 90.1% cov, G18 wired) → biomeOS neuralAPI → any primal | any NUCLEUS gate | Capability routing proven (835+ caps) |
| **Genomics pipeline** | wetSpring → toadStool → nestGate (16S rRNA, GPU) | strandGate (RTX 3090) | Pipeline validated, cold (needs data) |
| **NF drug reversal (Gonzales/Bin)** | tideGlass → Nest Atomic → Provenance Trio → petalTongue (GPS viz) | westGate | 214 tests, CAS + petal clients wired, GPS data CONVERTED, 2.5 TB CAS federated. Cell boot NEXT. Mid-term: Cell 2026 rebuild → NF screen → CTF NDU |
| **GIS data** | footPrint → nestGate → petalTongue | **ironGate** (downstream host) | Matures petalTongue G19 → reusable for tideGlass GPS viz |
| **Protein structure** | AlphaFold ~1TB → Nest Atomic CAS → provenance | westGate (ZFS 50.7TB) | Data on northGate, pipeline READY |
| **helixVision** | Genomics + AlphaFold + rendering | multi-gate | Orchestrator role. *(coralForge retired — helixVision is the canonical name.)* |
| **Cross-platform deploy** | cellMembrane → depot → any chip + drive | all gates | 35 binaries, 3 platforms proven |

### Platform Readiness — What's Wired vs What Needs Wiring

| Component | Proven? | What's Next |
|-----------|---------|-------------|
| biomeOS neuralAPI dispatch | **YES — 578 tests, Stage 2 infra shipped (riboCipher pool, auto-transition, TOML caps)** | **N2-N5 verification (primalSpring owns). Fleet-wide boot registration. Capability gossip (Phase 3).** |
| petalTongue WebGL/WASM | YES (6,605 tests, v1.7.0) | Live renders fed by Node Atomic GPU output |
| toadStool GPU dispatch | YES (746 pipes/sec, sub-ms) | petalTongue consumer pipeline |
| coralReef shaders | YES (WGSL/SPIR-V/PTX) | esotericWebb game shader pipeline |
| barraCuda tensor math | YES (FP64 104T, RTX 3090) | hotSpring QCD live computation |
| squirrel AI agent | YES (4,613 tests, 90.1% cov, G18 wired, 156b: 400s→16s) | biomeOS neuralAPI routing, user-facing agent |
| Nest Atomic CAS | YES (3,252 objects, ZFS) | Data ingestion pipelines (AlphaFold, NF) |
| Provenance Trio | YES (7/7 E2E) | Every workload gets provenance tracking |

### gen5 Dual-Science Pipeline

Two mid-term science tracks drive ecosystem evolution. Both consume the same primals, but exercise different capabilities. The support structures (footPrint, esotericWebb on ironGate) mature petalTongue (G19), which then serves both tracks.

**Track A — NF Drug Repurposing (Gonzales/Bin Chen)**
tideGlass rebuilds Cell 2026 GPS platform → NF drug reversal screen → CTF NDU grant.

- [x] **Step 1**: Provenance 7/7 — **DONE**
- [x] **Step 2**: westGate data federation — **3.21 TB / 153 datasets / 2.5 TB CAS federated, convoy COMPLETE (145/s). GPS data CONVERTED.**
- [x] **Step 3**: tideGlass specs shipped (ARCHITECTURE, MODULE_SPECS, DATA_ACCESS, PHASE_0_CHECKLIST, VISUALIZATION)
- [ ] **Step 4**: tideGlass Phase 0 — Zenodo inventory + RGES reproduction (Python). **NEXT.**
- [ ] **Step 5**: Phase 1 — reproduce all 7 modules against published claims
- [ ] **Step 6**: NF reversal screen (novel application)
- [ ] **Step 7**: NF pseudoSpore — **THE gen5 ARTIFACT** (G38)
- [ ] **Step 8**: CTF NDU grant application (G39)

**Track B — Lattice QCD on Consumer GPUs (Murillo/Chuna)**
hotSpring arXiv Rung 1 → 6-rung QCD program → vendor-agnostic physics.

- [x] **Step 1**: barraCuda DF64 GPU compute — **DONE** (FP64 104T on RTX 3090)
- [x] **Step 2**: hotSpring SU(3) pure gauge — **DONE** (5,500 traj/hr, plaquette validated)
- [x] **Step 3**: Gauge group resolved — **SU(3) confirmed**, paper relabel needed
- [ ] **Step 4**: arXiv Rung 1 submission — **PREPRINT 41/42.** NPU silicon continuum integrated (§2.9, §4.7). MILC Δ=3×10⁻⁹. β-scan receipt (7 β-values, 8⁴ SU(3)). Murillo claims audit done. **Wire live site → pseudoSpore → reviewer send.** |
- [ ] **Step 5**: Rung 2 — quenched fermions
- [ ] **Step 6-8**: Rungs 3-6 (dynamical → (2+1)-flavor → finite-T → cross-vendor)

**Support → Science convergence**: footPrint (GIS) + esotericWebb (CRPG) on ironGate mature petalTongue's live render pipeline (G19/G53). The same petalTongue then provides: GPS visualization for tideGlass NF screening (volcano plots, enrichment curves, MCTS traces) + QCD visualization for hotSpring (lattice configs, plaquette evolution, HMC trajectories). The downstream products are not just products — they are infrastructure maturation targets.

### sporePrint — Live Platform as Public Surface

sporePrint is subGen presented to the world. Design: **science first, infrastructure second**.
But the infrastructure IS the product — NUCLEUS running live workloads, not a static site.

Visitor flow: see live science → notice it runs on commodity HW → grab pseudoSpore → discover mesh.

**Sequencing**:
1. Phase 1 (NOW): sporePrint content refresh to Wave 155m reality
2. Phase 2: Live workload surfaces (QCD viz, game engine, GIS, genomics)
3. Phase 3: PseudoSpore grab pattern (NF as first downloadable artifact)
4. Phase 4: projectFOUNDATION auto-feeds from provenance

### Glacial Goals — Post-Threshold Checkpoint (Aug 1, 2026)

**COMPLETE (19 goals — proven on live hardware):**

| ID | Goal | Evidence |
|----|------|----------|
| G3 | Provenance Trio 7/7 | 8th consecutive pass. First real data (PDB+ChEMBL) at 100% provenance. |
| G4 | NUCLEUS on multiple gates | **×7**: westGate, strandGate, blueGate, sporeGate, southGate, ironGate, **graftGate** (FULL NUCLEUS via biomeOS Neural API, 1830 caps, 21 domains). |
| G8 | Plasmodium (multi-gate bonding) | southGate 22/22 PASS. BTSP trust without WireGuard. 29,294 foreign rejections. |
| G10 | Sub-builder mesh | J12 LIVE E2E. **Wave 157c: MESH-NATIVE** — `builder.serve :9800` Tower Atomic dispatch (no SSH). blueGate primary build authority. |
| **G11** | **Any chip + drive = mesh gate** | **5 OS families PROVEN**: Linux (6 gates), Windows (blueGate), Android (grapheneGate), **macOS (graftGate FULL NUCLEUS)**, **iOS (iosGate FIRST DEPLOY)**. steamGate NEXT. Graduated Wave 157k. |
| **G12** | **graftGate (M4 Mac Mini)** | **FULL NUCLEUS ACHIEVED** (Wave 157k). 15/15 compiled, 21 ACTIVE domains, 1830 caps, <60s via biomeOS Neural API. Depot pushed. 10 divergences documented. Cross-deployment architecture assessment filed. iOS cross-compile proven. Graduated Wave 157k. |
| G17 | Portability — reconstitute from cold | southGate: public depot + own entropy + user-space + no WG = 20h NUCLEUS. |
| G21 | biomeOS-cellMembrane coevolution | composition.test_swap + validate_with_deps. |
| G22 | biomeOS API convergence | Single-process dual-protocol. Validated on 3 gates. |
| G29 | Peptidoglycan isomorphism | 3-way DNS: sporeGate + blueGate H2 + golgi mesh. |
| G31 | Batch RPC for provenance pipeline | RESOLVED — superseded by G55 convoy (217/s, 460x). `dag.event.append_batch` LIVE. |
| G55 | Provenance batch RPCs (braids at machine speed) | RESOLVED — 700x. 217/s NVMe, 265/s inline, 4-tier storage. |
| G59 | Three-domain topology (k-derm website separation) | DNS COMPLETE. All 3 layers separated. primal.eco SEALED. nestgate.io LIVE. DNSSEC verified. |
| G64 | Cephalization — tarpc convergent evolution | C2 15/15, G65 15/15, C8 done (-67K lines). All primals dual-protocol. Graduated Wave 156q. |
| G65 | Protocol Negotiation — single-socket dual-protocol | 15/15 primals. squirrel origin, sourDough reference. Spec: `specs/PROTOCOL_NEGOTIATION_SPEC.md`. Graduated Wave 156q. |
| G66 | Transport Abstraction — silicon-agnostic IPC | 15/15 modules shipped. 15/15 Windows cross-arch PASS. sourDough reference. Spec: `specs/TRANSPORT_ABSTRACTION_SPEC.md`. Graduated Wave 157a. |
| **G68** | **Platform Substrate Abstraction** | **16/16 prod-clean, 16/16 cross-arch. 205→0 production violations.** sourDough scanner v2. toadStool S363→S368 (24→0). cellMembrane 15 cfg→3. Graduated Wave 157a. |

**ACTIVE (21 goals — in progress or unblocked):**

*Ecosystem checkpoint (Wave 157a): G68 fossilized (17th COMPLETE). G7+G30, G15+G36, G56+G67 merged (duplicate scopes). G49+G50 reclassified GLACIAL. Deploy infrastructure solved — frontloading primal evolution. Neural API becoming required system.*

| ID | Goal | Status | Next Step |
|----|------|--------|-----------|
| G7/G30 | westGate data federation & ingestion | **3.3 TB on ZFS — 153 datasets, 989K+ files braided inline.** Convoy COMPLETE (145/s, 460x). AlphaFold v6 42/46 proteomes. **7-session retrospective filed**. **All 3 P0s RESOLVED**: ~~P0-A bearDog~~ CODE FIXED, ~~P0-B nestGate~~ RESOLVED (stale depot), ~~P0-C biomeOS FD~~ FIXED (`6a51638d`). Pipeline API fixed. | `native_braid.py` → Rust. Depot rebuild deploys P0-A+C fixes fleet-wide. Spine commit signing unblocked once depot is current. *(Merged G7+G30.)* |
| G9 | arXiv publication (Murillo/Chuna QCD) | **PREPRINT 41/42.** NPU silicon continuum integrated (§2.9, §4.7 rewritten, §7, Appendix A). SU(N) N=2→8, 69 cached configs. β-scan receipt: 7 β-values on 8⁴ (β=2.0→6.5), plaquettes match literature. MILC bidirectional Δ⟨P⟩=3×10⁻⁹. NPU ESN: 100% accuracy (11 features, MCC=1.0). Murillo claims audit complete. | Wire live site (pseudoSpore artifact, `validate.sh`, reviewer JupyterHub). Then reviewer send. |
| G14 | sporePrint live science refresh | ACTIVE | pseudoSpore LIVE. Auto-publish FIXED. |
| G18 | squirrel → biomeOS agent orchestration | **LIVE on ironGate** | 9 providers, cross-primal dispatch validated (Session 10). Wire footPrint agent panel next. |
| G19 | petalTongue + Node Atomics live rendering | ACTIVE | hotSpring QCD viz + esotericWebb. |
| G20 | esotericWebb game engine on NUCLEUS | **CELL LIVE — G68 REDEPLOYED** | **V32** — 484+ tests, 28 caps, 13/13 ALIVE on ironGate. `nest.store` signal decomposition validated. Needs petalTongue WebGL pipeline (G19) for browser surface. |
| G32 | Silicon deism vendor cracking | **NEW — biomeGate** | 3-GPU bench (RTX 5060 + Tesla + Titan V). coralReef diesel engine. hotSpring cross-vendor validation. |
| G35 | Fully agentic LAN | **7/8 DONE** (biomeGate joined mesh). | northGate + flockGate blocked (physical access). `membrane remote.enroll` proposed. |
| G15/G36 | tideGlass NF archaeology & GPS reproduction | **ACTIVE** (214 tests, CAS wired, 5 viz scenes) | GPS data CONVERTED (11 JSON, 103 MB CAS). `content.query` WIRED. PetalTongueClient coded. 17 IPC methods. Cell boot on westGate NEXT (CAS federation now live). Mid-term: **sovereign rebuild of Cell 2026 GPS platform.** *(Merged G15+G36 — same tideGlass track, phased.)* |
| G37 | NF Reversal Screen (Gonzales NF collaboration) | **ACTIVE** | RGES vs LINCS, ZINC compound screening, MEK inhibitors (selumetinib) in top-100. NF Data Portal ingested (658 files). Depends G36. |
| G38 | NF PseudoSpore artifact | **ACTIVE** | Self-verifying USB: data + code + provenance. `./validate` runs 7 tideGlass modules. **First gen5 science deliverable.** |
| G39 | CTF NDU grant ($125K) | **ACTIVE** | Preliminary data package for Children's Tumor Foundation NDU. Depends G36+G37. |
| G43 | steamGate — immutable OS handheld | **ACTIVE** | Steam Deck OLED. User-space musl deploy on read-only SteamOS. G17 pattern. |
| G44 | reefGate — paired intelligence/storage | **ACTIVE** | DDR3 NUC + Synology DS224+ NFS. G23 fractional replication target. |
| G45 | Lattice QCD Rungs 2–6 (Murillo/Chuna program) | **ACTIVE — SU(N) GENERALIZED** | GaugeGroup trait covers N=2,3,4,5,6,8. Rung 1 reframed from SU(3)-only to full SU(N) ladder. 87-config thermalization grid running on 64 EPYC threads (~2wk). `arxiv_measure_battery` ready. 30 finite-T configs for deconfinement T_c/√σ analysis. SU(N>=4) GPU shaders need generalization (WGSL hardcoded for 3x3). |
| **G13** | **iosGate (iPhone XS)** | **ACTIVE — FIRST DEPLOY ACHIEVED** | BearDogApp (PID 557) + mesh discovery (PID 603) running on iPhone XS. WiFi LAN peer discovery (7 gate IPs). 4 iOS Rust binaries built (beardog 6.3M, songbird 17M, skunkbat 2.6M, swarmvine 2.1M). Free provisioning signed (7-day expiry). **6th OS family.** **Remaining**: paid Apple Dev enrollment, persistent provisioning, full Tower Atomic on iOS. |
| **G53** | **petalTongue maturation via downstream consumers** | **ACTIVELY WIRING** | **footPrint**: `petal-bridge.ts` dual-socket WS↔UDS relay (agent→squirrel, viz→petal) WIRED. Auto-load. CSP dedup. **tideGlass**: `PetalTongueClient` ACTIVATED (dead_code removed, `is_viz_method()` gate, fire-and-forget forwarding). **nestgate.io**: 20 primals discovered, 8/12 dashboard sections, Tower Atomic architecture view. **Conjugation**: RustScript (`@protokarya/rustscript`) is the TS conjugation layer — 11 modules. |
| **G54** | **Dual-science mid-term convergence** | **ACTIVE** | **Track A (NF/GPS — Gonzales/Bin)**: tideGlass rebuilds Cell 2026 paper → NF drug repurposing → CTF NDU grant. **Track B (QCD — Murillo/Chuna)**: hotSpring arXiv Rung 1 → 6-rung lattice QCD program. Both tracks consume barraCuda (GPU math), petalTongue (viz), provenance trio (chains), nestGate (data). Infrastructure evolves toward both simultaneously. |

**GLACIAL (21 goals — future phases):**

| ID | Goal | Status | Dependency |
|----|------|--------|------------|
| G6 | bearDog public (crates.io) | GLACIAL | crates.io publishing |
| G16 | pseudoSpore grab pattern on web | GLACIAL | After NF data + tideGlass |
| G23 | nestGate CAS fractional replication | GLACIAL | Data redundancy schema exists |
| G24 | Sovereign Identity Garden | CONCEPT | Gate-first (cameras/sensors), phone later |
| G25 | bearDog StrongBox/Secure Enclave | GLACIAL | Gate-connected first, phone later |
| G26 | sweetGrass zero-knowledge attestations | GLACIAL | Prove encrypted data properties |
| G27 | mitoBeacon identity genetics | GLACIAL | Person-level cryptographic DNA |
| G28 | Cross-platform sovereign identity | GLACIAL | Depends on ~~G12~~ (COMPLETE) + G13 (ACTIVE). Unblocking. |
| G34 | Outer membrane egress masking | GLACIAL | Flint as boundary router. Single opaque tunnel to golgi. [ISP] box sees nothing. Spec exists, no implementation. |
| G40 | cloudGate — WAN enrollment validation | GLACIAL | Oracle ARM VM, NAT traversal, trust-boundary crossing |
| G41 | piGate — resource-constrained ARM proof | GLACIAL | RPi 5, ~$125 edge gate |
| G42 | riscGate — RISC-V third ISA | GLACIAL | StarFive VisionFive 2, open-ISA |
| G46 | Show HN public launch | GLACIAL | 28-item rubric. Blocked until NF pseudoSpore + sporePrint |
| G47 | projectFOUNDATION auto-feed | CONCEPT | Provenance-driven knowledge layer, thread lineage |
| G48 | projectNUCLEUS product packaging | CONCEPT | NUCLEUS product + pseudoSpore delivery pipeline |
| G49 | lab.primals.eco periplasmic JupyterHub | GLACIAL | Reviewer-access interactive compute on ironGate |
| G50 | initioChem pseudoSpore (ABG track) | GLACIAL | Whole-cell expression artifact |
| G51 | Inkfish/Valve marine collaboration | CONCEPT | Marine genomics, coral holobiont science |
| G52 | blueFish PFAS QC (Jones track) | GLACIAL | EPA 1633A open PFAS QC |
| ~~G56/G67~~ | ~~**Neural API activation & Stage 2 routing**~~ | **FOSSILIZED as F15** | N-series 90/91. All P0s deployed fleet-wide. `capability.call` operational. **Evolution continues as G70 (composition graph executor).** |
| **G70** | **Neural API as composition graph executor** | **ACTIVE — POST-PANDEMIC ENMESHMENT** | **NUCLEUS is a graph of sub-graphs.** **Wave 157i enmeshment**: (1-9 from 157g all CLOSED). (10) **G72 Tier 1 COMPLETE** (9/9 teams, ~114 crates shed). (11) **Gossip injection 3→6/16 LIVE** (barraCuda 19 events, esotericWebb 2, lithoSpore synced; wetSpring 2/4 partial; hotSpring scaffold). (12) **P2 braid.verify CLOSED** (sweetGrass behavioral tests). (13) **projectNUCLEUS `nucleus-deploy verify --manifest`** — 29/29 PASS on ironGate (schema, membership, composition kinds, cycle detection, federation). (14) **hotSpring pseudoSpore E2E pipeline** shipped (compute→manifest→bundle→sign→register — pure Rust). **Remaining**: depot rebuild (new gossip binaries), songBird MeshRelay (blueGate + southGate blocked), sourDough live checks (`convergence`+`rpc-surface`), hotSpring gossip wiring (10 events scaffold), multi-composition orchestration, primalSpring modernization, graftGate bootstrap + enrollment. |
| G57 | nestgate.io data identity surface | **PHASE 2 — 10/12 sections + trust surface routes** | `/api/content/stats` (live CAS from rhizoCrypt), `/pseudospore/` (5 bundles), `/api/pseudospore/bundles` — all LIVE. mesh.peers WIRED. 20 primals discovered. **NG-05 CLOSED** (westGate CAS federation). Data Braids card can now query westGate TCP. Remaining: wire Data Braids card against westGate `192.168.4.149:8080`. |
| G58 | Mixed provenance convergence | **ACTIVE** | Promote all westGate data from primordial/CAS-only to fully braided. `is_dataset_converged()` gate for springs. Revalidation running for priority + AlphaFold. All spring-critical data fully braided before Phase 4 boot. |
| G60 | Federated CAS (nestgate.io cross-gate data surface) | **ACTIVE — FEDERATION ENDPOINT SHIPPED** | **petalTongue `/api/content/federation`** (`84e6e48`): combines local rhizoCrypt CAS stats with swarmVine data-topic gossip entries. Mesh-wide content availability via Tower Atomic transport (no SSH). As gates inject `cas.have` + `braid.head` entries, they appear automatically. **biomeOS gossip integration** (`993b97f7`): `capability.resolve` → swarmVine gossip table → targeted mesh dispatch. L1 cache on golgi for hot objects still needed. |
| G61 | Compute memoization via provenance trio | **ACTIVE** | strandGate thermalized lattice configs as CAS objects with provenance braids. 37 min CPU thermalization → instant on cache hit. Same BLAKE3→CAS→DAG→braid pattern as data acquisition. Cross-gate: biomeGate pulls configs for parity checks. Parallel pipeline: GPU produces while CPU thermalizes next β. NFT-style braids for both config and production results. |
| ~~G62~~ | ~~Nanowire → Primal Builder (mesh-routed builds)~~ | **FOSSILIZED as F16** | Phase 2a+2b DONE. Mesh-native dispatch + depot push LIVE. blueGate primary builder. **Remaining** (glacial): biomeGate 2nd sub-builder, `compute.capacity` gossip. |
| G63 | BTSP local-trust (SO_PEERCRED for same-gate UDS) | **ACTIVE** | nestGate accepts same-gate callers without full BTSP X25519 handshake. Process-level auth via `SO_PEERCRED` — membrane group callers are trusted by filesystem perms. Unblocks footPrint CAS write, tideGlass CAS integration, all gardens/protists on same gate. Zero config, maximally primal-like. Proposed in footPrint Phase 2 deploy ready handoff. |
| **G71** | **Science pipeline E2E** (strandGate → ironGate → sporePrint) | **ACTIVE** | First complete science artifact: GPU data → pseudoSpore → NFT → reviewer. Needs: ironGate NFT endpoint, sporePrint QCD page, petalTongue data viz, `validate.sh` → Rust. strandGate campaign 22/45. |
| **G72** | **Dependency Pandemic — Stadial Shift** | **TIER 1 COMPLETE (11/11)** | **Biological pandemic evolution — Tier 1 DONE.** 11/11 teams responded: toadStool (EXEMPLAR — tokio 118→65, 7 dead deps, plugin-loading/vulkano excised, ~73 GiB reclaimed), rhizoCrypt (-46 crates, 14.6%), nestGate (jsonrpsee -1,864 LOC, -10 crates, S147/S148 crate surgery), loamSpine (url+ICU -7 crates), sweetGrass (tokio trimmed, bincode/chrono removed), coralReef (optional dep gating), cellMembrane (rt-multi-thread→dev-deps), tideGlass (rt→current-thread), wetSpring (verified clean), **bearDog (+41 dead deps removed, tokio["full"] eliminated)**, **petalTongue (telemetry crate removed, runtime discovery replaces 13 hardcoded peers)**. **~155+ crates shed fleet-wide.** **Tier 2 QUEUED**: HTTP → songBird/capability.call (nestGate ureq first), axum 0.7→0.8 (5 projects), wgpu 22→28 (toadStool), YAML unification, tokio::sync→std::sync audit. **Tier 3**: sourDough dep validator, archaic pattern excision. See `specs/DEPENDENCY_PANDEMIC_SPEC.md`. |
| — | Chimera Phase 0 (shared library) | GLACIAL | Deferred |
| — | Zola → sporePrint primal pipeline | GLACIAL | Replace static site gen |

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

## 14. External Surface — Public Presence, Website, SEO, Contacts (REOPENED from F12)

**Why reopened**: F12 was fossilized at Wave 155i ("6/6 surfaces healthy"). Since then:
the website (`primals.eco`) is **NOT OPERABLE** — Zola build or deployment is broken.
The public surface has regressed from the fossilized state. Additionally, the northGate
external review revealed a **dual-reality gap**: the outer membrane (GitHub) shows an
empty `protoKarya/tideGlass` while internally there's a 220+ test 9-crate workspace.
The ecosystem's public face does not reflect its internal reality.

### Website (primals.eco / sporePrint) — CONCEPT EVOLUTION (Aug 17)

**The fix is not to repair Zola. The fix is to evolve the website into a NUCLEUS-served live data surface.**

The static Zola site served its purpose through Waves 139-155. But sporePrint is now the outer membrane of an ecosystem with 160K+ tests, 153 datasets, 45 production QCD configs, 7/7 provenance chains, and 12 live gates — none of which a static site can represent without constant manual content updates that always lag.

**Architecture evolution:**

```
BEFORE (broken):   Zola (static) → markdown → HTML → Caddy → primals.eco
                   Manual content updates. Always stale. Currently broken.

AFTER (target):    NUCLEUS primals → cellMembrane (data pipeline) → petalTongue (semantic surface)
                   ├── Live: gate status, test counts, provenance chains, spring results
                   ├── Live: dataset catalog, CAS stats, depot versions
                   ├── Static: philosophy, thesis, architecture docs (Zola templates)
                   └── Semantic layer exposed for translate.js (Validation Class V)
```

**What this means concretely:**
- petalTongue already serves nestgate.io with live primal data (Phase 2+3 LIVE)
- The same pattern extends to primals.eco: petalTongue routes live data queries through Neural API
- cellMembrane provides the data pipeline: primal test counts, spring validation results, gate health
- Zola remains as the **template layer** for static content (philosophy, thesis, architecture)
- **The semantic layer** petalTongue exposes is what translate.js tests against (Class V validation)
- References and data citations become **live CAS links** rather than static markdown

**Immediate items (sporePrint team on sporeGate):**

- [ ] **Phase 0: Fix the static site** — get primals.eco serving SOMETHING while the architecture evolves. Zola triage: golgi auto-publish regression, Zola version, content error, Caddy drift?
- [x] Security infrastructure intact (HSTS, CSP, fail2ban, ACME TLS — carried from F12)
- [ ] **Phase 1: Live data endpoints** — petalTongue routes for gate status, test counts, depot versions (same pattern as nestgate.io)
- [ ] **Phase 2: Content pipeline** — cellMembrane feeds validation counts, spring results, provenance chain stats into petalTongue
- [ ] **Phase 3: Semantic layer** — structured data for translate.js testing. Science data, validation results, and references are machine-readable
- [ ] **Phase 4: Google SEO** — sitemap, indexing, structured data, page speed. Meaningful only after live data surface exists
- [ ] sporePrint pseudoSpore landing with live data (not static markdown)
- [ ] Gate-status dashboard (live from biomeOS/swarmVine gossip)
- [ ] K-Derm architecture page (public-facing topology)
- [ ] Data catalog stats (153 datasets, 3.3 TB, 989K files — live from nestGate CAS)

### GitHub (outer membrane)

- [ ] **protoKarya/tideGlass EMPTY on GitHub** — 220+ test 9-crate workspace exists on Forgejo. Outer membrane has no signal of tideGlass existence. Decision needed: mirror to GitHub, or push a public-facing README only?
- [x] ecoPrimals org repos present on GitHub (trailing mirror)
- [ ] GitHub→Forgejo cascade **VALIDATED** (northGate Aug 16) but no regular outer→inner sync cadence established
- [ ] README freshness audit across GitHub repos — do they reflect current wave state?

### External Contacts (Gen5 Pipeline)

- [x] **Gonzales GPS collaboration**: warm but stalled (10 weeks, no Phase 0 result to report). Fall semester starts Aug 26.
- [ ] **Gonzales reactivation email**: GATED on Phase 0 completion. Draft should reflect internal state (9-crate Rust workspace, 482 GB federated data) not "we haven't started"
- [ ] **Bin Chen introduction**: offered by Gonzales Jun 5, never materialized (no artifact to anchor it)
- [x] **arXiv reviewers formed**: Murillo, Chuna, Bazavov. Paper 41/42. Send blocked only on integration work (~6-8h)
- [ ] **arXiv reviewer send**: needs wire live site → pseudoSpore → send. **Website being down blocks this.**
- [x] **Barrick LTEE**: Interview done, USB delivered. No response. Independent track.
- [ ] **Valve/Inkfish**: 2-week response window passed Aug 12 (silence). Next: LinkedIn warm engagement per OUTREACH_STATUS protocol.

### nestgate.io (peptidoglycan surface)

- [x] Phase 2 LIVE: `/depot/`, `/provenance/`
- [x] Phase 3 LIVE: `/cas/{hash}`, `/cas/{hash}/provenance`
- [x] Federation: songBird `content.locate` across all gates
- [x] Sovereign Knot DNS + DNSSEC (no Cloudflare)
- [ ] Data Braids card → wire against westGate TCP (`192.168.4.149:8080`)

### Ownership

| Surface | Owner | Status |
|---------|-------|--------|
| primals.eco (Zola + deploy) | sporeGate (sporePrint) | **DOWN — needs triage** |
| primals.eco (content refresh) | sporeGate (sporePrint) | STALE |
| Google SEO | sporeGate (sporePrint) | NOT AUDITED |
| nestgate.io | sporeGate (petalTongue) | LIVE |
| GitHub mirror | overwatch | Trailing, README audit needed |
| protoKarya GitHub | overwatch | Decision needed (mirror vs summary) |
| Gonzales email | overwatch + northGate | GATED on Phase 0 |
| arXiv send | strandGate + northGate | BLOCKED on website |
| Valve follow-up | overwatch + northGate | LinkedIn engagement |

### Priority

1. **FIX THE WEBSITE** — sporePrint team. Blocks arXiv reviewer send and external credibility.
2. **sporePrint content refresh** — once website is live. Gate status, K-Derm architecture, data catalog.
3. **Google SEO audit** — sporePrint team. Sitemap, indexing, structured data, page speed.
4. **GitHub README freshness** — overwatch. Quick pass across repos.
5. **protoKarya/tideGlass decision** — overwatch. Mirror or summary.
6. **Gonzales reactivation** — gated on Phase 0 completion.

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
- coralForge retired — **DEAD** (empty repo, 0 commits). Canonical successor: helixVision (gardens/). All active references converged.
- Peptidoglycan + Provenance Trio AARs filed
- 17+ handoff docs from Wave 155f–i (code teams + AARs + Nest Atomic)

## F12. Public Surface / Security (fossilized Wave 155i — PARTIALLY REOPENED as D14)

Security infrastructure remains operational. **Website availability regressed** — primals.eco
(sporePrint/Zola) NOT OPERABLE as of Wave 157k. Reopened as D14 (External Surface) to track
website fix, content refresh, Google SEO, GitHub freshness, and external contact pipeline.

- 6/6 surfaces healthy (sporeprint, footprint, live, webb, lab, git) — **REGRESSED: sporeprint DOWN**
- Security headers deployed (HSTS, CSP, X-Frame-Options)
- fail2ban + rate limiting active
- TLS auto-renewing (ACME)
- Tower pen test: 7 scenarios, all PASS, 0 remaining findings
- sporePrint transplant DONE + credibility audit
- External claim convergence standard issued
- sporePrint impulses (ongoing cadence) tracked under D11 Campus
- **See D14 for current external surface state and action items**

## F13. Jelly Strings — Deployment Automation (fossilized Wave 155i)

Manual deployment shell loops → primal-native Rust automation: **ACHIEVED**.

- J1–J6: ALL CLOSED (harvest, depot push, service restart, Caddy config, WG peer reg, systemd overrides)
- J7: Legacy detection — one-time P3, deprioritized (does not block any deployment)
- J8: Key enrollment portal — DEPLOYED (step-ca live at ca.primals.eco)

7/8 code-complete + deployed. All deployment automation that was manual is now
primal-native. J7 is a one-time cleanup task that does not affect the dimension's
completeness.

## F14. Jelly Strings — Sovereign CI Pipeline (fossilized Wave 156h)

J9–J19 (11/11 KILLED or LIVE E2E). Full sovereign CI pipeline operational:
Forgejo push → cascade → diff → build → checksum → depot push → verify.

- J9–J13: Cascade/build/depot triggers — ALL KILLED
- J12: Sub-builder dispatch — LIVE E2E (SSH-first, songBird IPC evolution → G62)
- J14–J19: Socket ownership, checksums, self-CI, tmpfiles, env coupling, sandbox — ALL KILLED

sporeGate + blueGate sub-builder + cellMembrane portability. SSH → songBird
evolution tracked under G62 (Nanowire → Primal Builder).

## F15. Neural API Activation + Debt Clearing (fossilized Wave 157g)

Neural API activation (G56/G67) COMPLETE — 90/91 verified, deployed fleet-wide:
- N1–N6 all SHIPPED and VERIFIED
- exp118 14/14, exp119 12/12, exp120 29/29, exp121 35/36
- `capability.call` operational: 1.3ms westGate, 4ms ironGate
- riboCipher Tier 2 CLOSED, auto-detect SHIPPED
- All P0s (bearDog, nestGate, biomeOS) resolved + deployed
- 1 remaining: toadStool tarpc protocol mismatch (architecture decision, not P1)

Debt clearing COMPLETE:
- S1–S7, O1–O8, B1+B2 ALL RESOLVED
- C2 dual-socket 15/15
- G64 cephalization, G65 protocol negotiation, G66 transport abstraction — all 15/15
- C8 squirrel excision -67K lines
- Cross-arch 16/16 PASS (`cargo check --target x86_64-pc-windows-gnu`)

**Evolution continues as G70 (Neural API as composition graph executor).**

## F16. Nanowire → Primal Builder (fossilized Wave 157g)

Mesh-native build dispatch fully operational:
- blueGate `builder.serve :9800` Tower Atomic (no SSH)
- Build authorities: `[blueGate, sporeGate, eastGate]`
- Depot push SOLVED (blueGate → golgi SSH key authorized)
- swarmVine `DepotManifest` gossip type shipped
- Remaining glacial: biomeGate as 2nd sub-builder, `compute.capacity` gossip integration

---

**Active**: 11 dimensions (1–5, 7–8, 11–14)
**Fossilized**: 16 dimensions (F1–F16) — **F12 partially reopened as D14** (website regression)
**Summary**: Wave 157k INTERSTADIAL — **12 GATES ONLINE.** biomeGate BACK (reimaged Aug 13, Tower 4/4 + Node Atomic, ember fleet 4/4 GPUs, 3 toadStool bugs fixed, sovereign dispatch research active). K-Derm topology unified (all gates `kderm_role = cytoplasm`). ALL 3 sub-builders ENMESHED (TCP/riboCipher :9800). SSH RETIRED for dispatch. nestgate.io Phase 2+3 LIVE. deploy.result Phases 1+2 DONE. **ALL stadial code tracks CLOSED. 0/0/0.** Primal code teams DORMANT. biomeGate team intermittent (science-track pacing). **16 primals. ~160K+ tests. Interstadial confirmed — downstream patterns active.** **EXTERNAL SURFACE REGRESSION**: primals.eco (sporePrint/Zola) NOT OPERABLE — blocks arXiv reviewer send and external credibility. F12 partially reopened as D14. sporePrint team handles Zola triage + Google SEO.

**Phase shift**: **"Deep interstadial — all code stable, science and infrastructure downstream."** ALL stadial code tracks CLOSED (deploy.result, FleetDeployHealth, debt sweeps, enmeshment). biomeGate online as sovereign dispatch research platform. Remaining work is infrastructure ops (WG enrollment, depot rebuilds, SSH graduation) and science campaigns (QCD, sovereign dispatch, tideGlass). No primal code changes needed.

**217 files fossilized** across 19 wave directories (1,494+ total records). Active surface: **13 handoffs** (BLURB + gate spinup + 3 biomeGate AARs + silicon exploration + 3 science tracks + 3 westGate specs/plans).
- **ironGate: DOWNSTREAM SURFACE.** **ORTHO CASCADE COMPLETE** — 6 repos cascaded, 6 binaries deployed, all 4 canary fixes. 13/13, 166 caps, **2ms dispatch** (down from 9ms), **4 mesh peers** (up from 1). Blocker #3 (songBird `--node-id`) CLOSED. esotericWebb V32 CELL LIVE. G18 LIVE. 12.7 TB CAS. RTX 5070.
- westGate: **INTERSTADIAL — PHASE 3 LIVE + native_braid.py RETIRED.** nestGate S150 deep debt (-1,788L). **nestgate.io Phase 3 LIVE**: `/cas/{hash}` + `/cas/{hash}/provenance` routes (local → mesh federation → 404). sweetGrass announcement persistence FIXED (auto-announce at boot + 30s sweeps). **`native_braid.py` RETIRED** → `membrane content.braid` (Rust-native, routes through biomeOS Neural API). **0 active Python/Bash orchestration.** Nest 6/6 healthy. 3.3 TB / 989K files braided / 153 datasets / 2.5 TB CAS.
- strandGate: **FULL SILICON SATURATION (Aug 13).** **13/13 ALIVE.** Streaming encoder upstreamed to barraCuda (`2ff33c10`): GPU utilization 43%→85-95% (single `CommandEncoder` submit vs 320 round-trips). DF64 hang FIXED (VGPR exhaustion — WG128→WG64 for RDNA2, `split_workgroups()` for dispatch >65535). TMU PRNG wired (`with_tmu()` — Box-Muller via texture units). ROP force accumulation assessed (7.8G scatter-adds/s RTX 3090). 6 gaps exposed: GPU-resident CG (dynamical fermion streaming), async probe, timestamp queries, TMU seed reproducibility, render pipeline for ROP, AMD 32⁴ validation. AMD campaign running (~24h). **250-2500x MILC** for stencil ops. 75/87 thermalization cached.
- **sporeGate: TOPOLOGY + NANOWIRE SSH RETIREMENT UNDERWAY (Aug 13).** **Tier 1 RETIRED**: sub-builder dispatch → Tower Atomic TCP (`call_tcp` + riboCipher `[0xEC, 0x01]`, `e8d4ffa`). blueGate + ironGate enmeshed. `builder.serve` = graduation template for all 19 SSH call sites across 7 tiers. G69 Phase 3 CAS archival LIVE. CAS replication to ironGate 12TB WIRED. Gate hygiene composition-native. NanoWire checklist tracks full retirement roadmap (18 files, 9 SSH primitives in `ssh.rs`). **15/15 ALIVE**, 13,910 caps.
- biomeGate: **GPU LAB — ONLINE + REGISTERED (Aug 13-14).** Tower 4/4 + Node Atomic source-built. Ember fleet 4/4 GPUs (runtime VFIO). WG peer + SSH key registered via sporeGate. 3 toadStool bugs fixed (zstd firmware, D3hot BAR0 wake, PRI fault false positives). Exp 223-224 invalidated (false positive). HBM2 wall on Volta confirmed — warm handoff required. K80 unsigned falcons most tractable sovereign target. **Team intermittent** (science-track pacing). Next: nouveau warm handoff (Exp R6), K80 firmware extraction, full NUCLEUS composition.
- eastGate: **OVERWATCH — ENMESHMENT, ALL TRACKS DONE.** 64 GB DDR5. **biomeOS `deploy.result` Phase 1 LIVE** (`f80e5f2a`). **D12/D13 ALREADY MERGED** (`31da2861` Aug 13). **content.put translation ALREADY IN v4.61.** **gate2_nucleus.toml parity FIXED** (`3b1da444`). **primalSpring v0.9.50** (`144d4aa7`): enmeshment docs, 1,291 tests. **Fork storm RESOLVED**: 1,785 zombies (1,190 coralreef + 595 skunkbat) from stale `~/.local/bin/` binaries — killed, stale binaries removed. 14/14 NUCLEUS alive from plasmidBin depot. **Both eastGate code tracks COMPLETE. Dormant.**
- blueGate: **WINDOWS BUILDER — DEPLOYED, NEEDS ENMESHMENT.** 13/13 NUCLEUS alive. `builder.serve :9800` LIVE (`MembraneBuildServe` scheduled task, `3628fd2`). Health verified from sporeGate via WG mesh. ~~P2 songBird~~ CLOSED. ~~P2 swarmVine~~ CLOSED. **Enmeshment needed**: wire blueGate into golgiBody cascade pipeline so foreman auto-dispatches `x86_64-pc-windows-gnu` builds through mesh (like ironGate aarch64). golgi push SOLVED.
- southGate: **ORTHO CASCADE — SSH FIXED + CANARY.** All repos cascaded. Depot refreshed. SSH installed (was refused). neuralSpring 835/843 tests, guidestone L0 28/28. ~~toadStool wgpu28 crash~~ FIXED in source (`be9b0a293` — runtime Vulkan probe replaces musl ban). Needs depot rebuild to reach southGate. 12/13 IPC reachable. 3 gossip peers, 8 mesh peers.
- graftGate: **ORTHO CASCADE COMPLETE.** 5 primals rebuilt from current HEADs. Depot refreshed (5/15 darwin). sourDough atomic model corrected (`3dd320a`: Tower=4, NUCLEUS=16). ~~D11~~ CLOSED (`af267161` — swarmVine added to biomeOS bootstrap). NUCLEUS redeployed with `--node-id`. iOS cross-compile live.

**12 gates ONLINE** (7 NUCLEUS, 1 GPU lab Tower+Node, 1 crankshaft + agentic, 3 other). **19 glacial goals COMPLETE** (G3, G4, G8, G10, G17, G21, G22, G29, G31, G55, G59, G64, G65, G66, **G68**, **G56/G67** (F15), **G62** (F16), **G11**, **G12**).
**26 ACTIVE** (G7/G30, G9, **G13**, G14, G15/G36, G18, G19, G20, G32, G35, G37, G38, G39, G43, G44, G45, **G53**, **G54**, G57, G58, G60, G61, G63, **G70**, **G71**, **G72**).
**21 GLACIAL/CONCEPT**.
**67+ total glacial goals** tracked.
**ZERO P0. ZERO P1. ZERO P2.** G72 Tier 1 complete. Gossip **9/16**. G69 Phase 3 CAS LIVE. **ALL 3 sub-builders ENMESHED** (ironGate systemd + blueGate scheduled task + graftGate launchd — all TCP + riboCipher on `:9800`). SSH RETIRED for sub-builder dispatch. deploy.result Phases 1+2 DONE. nestgate.io Phase 2+3 LIVE. `native_braid.py` RETIRED. K-Derm topology unified (all gates cytoplasm). **biomeGate ONLINE** — Tower 4/4 + Node Atomic, ember fleet 4/4 GPUs, 3 toadStool bugs fixed, WG+SSH registered, team intermittent. **Pipeline divergence RESOLVED** (sporeGate `3f9fa14`). **rootPulse REFRAMED**: biomeOS graph execution, not primal step handlers — primals participate via existing capabilities; nestGate overstep caught + reverted. rhizoCrypt + sweetGrass have domain handlers (rootPulse IS their domain). **swarmVine topic fix CLOSED** (`31e3e0a`). **Dehydration routing gap CLOSED** (rhizoCrypt semantic aliases). **AlphaFold ingress ACTIVE** (`membrane alphafold.ingest` — Phase A done, B running, C validated — 23 TB pipeline). **DF64 sovereign shader compilation LANDED** (barraCuda + coralReef). **Gen5 critical path: tideGlass Phase 0 = sole bottleneck** → JOSS → CTF NDU $125K. **12 gates ONLINE. Enmeshment phase — fermenter built, now cultivating.** **REMAINING: ~~D12/D13~~ DONE. ~~content.put~~ DONE. biomeOS rootPulse graph wiring, bearDog AEAD Neural API surfacing, cellMembrane UDS→TCP fallback, blueGate depot rebuild + sweetGrass auto-announce, NanoWire SSH retirement Tiers 2-7, biomeGate full NUCLEUS, AlphaFold Phase B+C. SCIENCE: sovereign dispatch, QCD arXiv + pseudoSpore (~6-8h), tideGlass Phase 0 (gen5 bottleneck), science E2E pipeline.**

~~**DEBT CLEARING + NEURAL API ACTIVATION**~~ — **FOSSILIZED as F15 + F16 (Wave 157g).**
All debt items resolved. Neural API 90/91 verified, deployed fleet-wide. Cross-arch 16/16 PASS. See F15 + F16 below.

**REMAINING — TARGETED WAVES FROM HERE:**
- ~~**G68 convergence**~~: **COMPLETE + FOSSILIZED.**
- ~~**Phase A**~~: **DONE** — cascade timer LIVE on sporeGate.
- ~~**Depot rebuild + deploy**~~: **DONE** — musl 15/15 + aarch64 15/15 rebuilt. Sub-builder fan-out WIRED. Fleet pushed.
- ~~**Gate redeploy**~~: **ALL 10 ACTIVE GATES RESPONDED. CASCADE COMPLETE. FOSSILIZED.**
- ~~**Neural API evolution**~~: **ALL PHASES CODE-COMPLETE. DEPLOYED FLEET-WIDE. FOSSILIZED.**
- ~~**All code blockers**~~: **CLOSED.** songBird Windows (`b8c225775`), swarmVine Windows (`0e4cb75`), D11 biomeOS (`af267161`), toadStool musl (`be9b0a293`). **0/0/0.**
- **toadStool long-tail → G72 Exemplar**: S377-S379 DONE. ~65 files irreducible async. **38/48 WASM** (79%). Tier 2 QUEUED.
- ~~**cellMembrane long-tail**~~: **G69 Phase 1+2+3 COMPLETE. Deep debt sweep DONE.** ~~`native_braid.py` → Rust~~ **RETIRED by westGate** (`membrane content.braid` — Rust-native, Neural API routed). `convergence`+`rpc-surface` live validators remain.
- ~~**deploy.result gossip Phase 1+2**~~: **DONE.** biomeOS `deploy.result` emission LIVE (`f80e5f2a`). primalSpring `FleetDeployHealth` wired into `nucleus_launcher` CLI (`d15ab028`, v0.9.50). **Deployment signaling pipeline Phases 1+2 COMPLETE.** Phases 3+4 (cellMembrane sovereignty → gossip, sporeGate topology-aware cascade) await downstream.
- **NanoWire SSH retirement**: **Tier 1 RETIRED** (sub-builder dispatch → Tower Atomic TCP, `e8d4ffa`). `builder.serve` pattern = graduation template for all 19 SSH retirements across 7 tiers. **Tier 2 NEXT**: R-01 `gate.pull` (already `cascade.notify` gossip), R-02 `gate.check`, R-03 `gate.info`, R-04 `plasmid.trigger`, R-05 `service.*`. Each capability added to `builder.serve :9800` removes one SSH call site. **Tier 3**: depot push + CAS archival. NanoWire checklist: `specs/NANOWIRE_RETIREMENT_CHECKLIST.md`.
- ~~**nestgate.io Phase 3**~~: **LIVE.** `/cas/{hash}` + `/cas/{hash}/provenance` routes on peptidoglycan surface. Local → mesh federation → 404.
- **Springs**: tideGlass cell boot, hotSpring viz, esotericWebb browser surface.
- **arXiv**: strandGate production campaign 22/45 (~6h remaining). Wire live site + pseudoSpore + reviewer send.
- **Wave cadence**: targeted primal waves. No more ecosystem-wide convergence days.
- **Neural API escalation**: biomeOS as THE composition interface. Graph executor for multi-step workflows. Pepti + data federation + Neural API = three-pillar architecture.
- **G72 Dependency Pandemic — Tier 2 QUEUED**: HTTP→songBird, axum 0.7→0.8 (5 projects), wgpu 22→28 (toadStool), YAML unification, tokio::sync→std::sync audit. **Tier 3**: sourDough dep validator, archaic pattern excision.
- ~~**biomeGate ONLINE**~~: **REGISTERED.** WG peer + SSH key registered via sporeGate. Tower 4/4 + Node Atomic + ember fleet 4/4 GPUs. 3 toadStool bugs fixed. Team intermittent. **Next**: full NUCLEUS composition, nouveau warm handoff (Exp R6), K80 firmware extraction.
- **K-Derm topology unified**: All gates `kderm_role = cytoplasm` in manifest. THREE_DOMAIN_TOPOLOGY_SPEC Phase 2+3 LIVE. Blurb reshaped with membrane topology diagram + builder dispatch flow + 9 team assignments.
- **Graph visualization spec**: Architecture for biomeOS 79 TOML graphs → petalTongue GraphEngine → nestgate.io `/viz/graphs/`. Handoff to petalTongue + biomeOS teams.
- ~~**Pipeline divergence**~~: **RESOLVED** (sporeGate `3f9fa14`). Serde flatten collision FIXED (two-pass TOML parse). Target-aware drift detection. rootPulse trio wiring. 13/13 x86_64 rebuilt, 28 pushed. Stale `~/.local/bin/membrane` FIXED. Write-back data loss FIXED. Cascade autonomous.
- **rootPulse provenance trio**: 3 neuralAPI graphs LIVE (rootpulse_commit, rootpulse_harvest, rootpulse_diff). Per-target build provenance authority. Trio query → flat file fallback. **REFRAMED**: rootPulse is a biomeOS graph composition — biomeOS executes the graph, calling each primal's *existing* capabilities as steps. rhizoCrypt + sweetGrass implemented domain-specific handlers (rootPulse IS their domain: provenance DAG + attribution). nestGate/bearDog/loamSpine participate via existing `content.*`/`auth.*`/`ledger.*` methods — **no new primal `rootpulse.*` code needed**, only biomeOS graph wiring + Neural API translation entries. nestGate overstep caught and reverted (self-knowledge-only preserved). **Owner: eastGate (biomeOS)**.
- **westGate provenance experiments**: 14/14 `membrane experiment.*` PASS. 2,630 braids verified. Cross-industry export (W3C PROV-O, RO-Crate, BagIt, DataCite). primalSpring exp124 codified. 4 routing gaps documented — **2 CLOSED** (rhizoCrypt dehydration via aliases, sweetGrass 50/50/50), **2 remaining** (biomeOS `content.put` translation, bearDog AEAD surfacing). `experiment.all` recommended as post-deployment validation battery.
- **AlphaFold Neural API ingress** (westGate): `membrane alphafold.ingest` — 3-phase pipeline for 23 TB / 246M structures. Phase A complete (99 files, 14.76 GiB), Phase B running (10M+ files streaming from ZFS), Phase C validated (EBI remote fetch). New "direct-to-primal bypass" pattern for non-default timeouts. Translation gaps fixed (`content.fetch`, `crypto.sign` alias, `path`→`directory`, DAG batch format).
- **Gen5 critical path** (westGate enmeshment AAR): Steps 1-2 COMPLETE (crypto + provenance). **Step 3 tideGlass Phase 0 = sole bottleneck** → JOSS → CTF NDU $125K. QCD pseudoSpore ~6-8h (fastest gen5 proof event). GEN_REVIEW_151c audit: 3/13 done, 2 partial, 8 remaining (mostly documentation debt). CAS + NFT braid architecture documented. subGen writeups pushed.
- **DF64 sovereign shader compilation** (strandGate): barraCuda (`4a3679f0`) DF64 shader compile via coralReef SPIR-V. coralReef (`9c64cfa`) WGSL-to-SPIR-V DF64-safe emission endpoint. Both rebuilt and in depot.
- ~~**swarmVine mesh.relay topic**~~: **CLOSED** (ironGate `31e3e0a`). Topic extracted from payload entries. 187 tests. All swarmVine code items CLOSED.

### ECOSYSTEM CHECKPOINT — DEPLOY SOLVED, PRIMAL EVOLUTION FRONTLOADED (Aug 8)

**Old patterns cleared:**
- ~~Gate-local `cargo build`~~ → golgi depot pull (~30s)
- ~~Manual golgi depot sync~~ → cascade auto-push (zero drift)
- ~~GitHub deploy keys / `github` remotes~~ → Forgejo-first, K-Derm relay
- ~~Manual capability registration~~ → `mesh.register` at boot (cellMembrane shipped)
- ~~WG+SSH for inner membrane RPC~~ → songBird LAN-first mesh (Phase 1 DONE)

**New patterns enforced:**
- Deploy lifecycle: `pull → restart → register → gossip-announce → verify-in-mesh`
- Sovereign fetch: `plasmid.fetch --source forgejo` (all gates)
- LAN-first: `SONGBIRD_LOCAL_PEERS` seeds cross-house peers
- Gossip-first: swarmVine epidemic gossip for capability/data/compute (replaces songBird broadcast for capability discovery)
- Cascade: 15min timer, auto-harvest, auto-push, zero drift
- Dep pandemic (G72): external deps shed as compositions close gaps — HTTP→songBird, tokio surface minimized, version splits unified

**Inner membrane evolution roadmap:**
- **Phase 1 DONE**: songBird mesh connectivity (westGate + strandGate seeded)
- **Phase 2 COMPLETE — CHAIN CLOSED**: riboCipher Tier 2 (`0xED` mito-obfuscated cross-gate transport)
  - bearDog: ~~`decode_mito_tag`~~ **SHIPPED** (`RiboCipherHandler` — 16th handler kind, 4 methods, auto-announced)
  - biomeOS: ~~client pool~~ **SHIPPED** (`ConnectionPool::send_mito_jsonrpc` — `[0xED, 0x01]` + mito-tag, Tier 1 fallback)
  - songBird: ~~accept `0xED` on :7700~~ **SHIPPED** — `dispatch_ribocipher_rpc()` replaces stub, full `IpcServiceHandler` dispatch on mito-framed connections
  - skunkBat: evolve from REJECT to delegate-and-route (P2, future)
- **Phase 3 ACTIVE → Phase 4 SHIPPED**: Capability + data + compute federation via swarmVine (primal #16)
  - **swarmVine**: epidemic gossip engine. **134 tests.** Windows port DONE. **Phase 4 shipped**: `gossip.subscribe` (broadcast channel), `BloomFilter` (CAS have-set), `ComputeCapacity` scheduling hints, `DepotManifest` for binary distribution gossip. Deep debt clean (zero hardcoded paths, IPv6 fix, nonce contention eliminated).
  - **songBird seam LIVE** (`6b580cf0`): `ipc.register` fires `gossip.inject` to local swarmVine. Fire-and-forget — both paths (songBird announce + swarmVine gossip) run in parallel.
  - **skunkBat `metadata.analyze` SHIPPED** (`e602e09`): 8-check gossip pre-accept validation (topic validity, key format, origin identity, TTL bounds, payload size, freshness, lifetime, quarantine). Returns allow/warn/block verdict. 672 tests (+16). **Vine-bat loop enabled.**
  - **biomeOS gossip table SHIPPED** (`993b97f7`): `capability.resolve` → swarmVine `gossip.query` → targeted mesh dispatch. Fallback chain: local discovery → gossip hints → targeted → broadcast. 7 new tests. `discovery_gossip.rs` + `mesh.rs` targeted dispatch.
  - nestGate/loamSpine: inject `cas.have` + `braid.head` data gossip entries (loamSpine 4 events LIVE via `gossip.inject` UDS)
  - **barraCuda 22/22 events FULLY WIRED** (compute, tower, shader, dispatch, quota, OOM, precision — recovered, precision-degraded, systemic-error final 3 wired). **FULL SPEC COVERAGE.**
  - **esotericWebb 2 session lifecycle events LIVE** (V33 gossip mesh enmeshment).
  - **wetSpring 4/4 LIVE** (all events hooked).
  - **nestGate gossip hooks at 11 CAS sites**, 6 event types (S147/S148).
  - hotSpring: 10 gossip events defined (scaffold — not yet hooked at call sites).
  - **Cross-gate gossip LIVE**: **6-gate mesh** (westGate, sporeGate, eastGate, strandGate, ironGate, **southGate**). southGate: 342 ingested, 1,216 sent, bidirectional federation. cascade.notify gossip types wired in swarmVine (`cb58d32`). blueGate awaiting depot pull.
- **Phase 4 FUTURE**: WG deprecation for inner membrane (keeps outer membrane + human ops)

**MID-TERM SCIENCE TRACKS**:
- **Track A (NF/GPS)**: G15→G36→G37→G38→G39. Gonzales/Bin Chen. tideGlass rebuilds Cell 2026 → NF reversal screen → CTF NDU $125K.
- **Track B (QCD)**: G9→G45. Murillo/Chuna. arXiv Rung 1 → 6-rung lattice QCD on consumer GPUs.
- **Support convergence (G53)**: footPrint + esotericWebb on ironGate → petalTongue G19 → GPS viz (Track A) + QCD viz (Track B).

**Gauge group resolved in code** (G9): SU(3) labels disambiguated in barraCuda/hotSpring. Paper/site relabel still needed (sporePrint scope). arXiv UNBLOCKED.

**Open items — prioritized by data pipeline + springs readiness:**
- ~~**G55: Batch RPCs for provenance**~~ — **RESOLVED (460x)**. Convoy at 145/s. Primals never the bottleneck.
- ~~**G59: Three-domain topology**~~ — **DNS SEPARATION COMPLETE.** All 3 layers separated. primal.eco SEALED. nestgate.io LIVE on mesh. DNSSEC verified. Trust surfaces live (3 routes). ~~Remaining: deploy dnsmasq, wire content backend, brand nestgate.io.~~ Content backend wired. dnsmasq ops tracked under D4 peptidoglycan.
- ~~**G56: Neural API activation**~~ — **FOSSILIZED as F15.** All routing operational. Evolution continues as G70.
- **G57: nestgate.io** — **PHASE 2 LIVE** (`947183a7`, `7ffb7a21`). `/depot/` (4 arch, 54 binaries, 594MB) + `/provenance/` (BLAKE3 prefix-match). Phase 3: `/cas/{hash}` content retrieval, cross-gate CAS federation via songBird `content.locate`.
- **G58: Mixed provenance convergence** — promote primordial → braided for all spring-critical data. `is_dataset_converged()` gate. Revalidation running.
- ~~**nestGate canonical client crate (O8)**~~ — **RESOLVED.** Reframed as Neural API wiring — consumers use `capability.call("content", "get", ...)` through coordinator. No primal-specific crate needed. 5 domains, 6 federation methods, MeshRelay transport wired.
- ~~**biomeOS cell attachment CLI**~~ — **SHIPPED** (`biomeos nucleus attach`, v4.57).
- ~~**toadStool ExecStart fix + socket perms (B1+B2)**~~ — **FIXED.** Dir 0o750 (group-traversable), socket 0o660 (group-connectable). Cell boot unblocked on all gates.
- ~~**footPrint CSP + auto-load**~~ — **RESOLVED.** `petal-bridge.ts` wired. `SKIP_CSP=1`. `autoLoadDefaultProject()`. Remaining: squirrel UDS socket on ironGate.
- **esotericWebb HEAD method (E3)** — GET 200 / HEAD 502. HTTP handler missing HEAD support (NG-06). petalTongue WebGL pipeline still needed for live game surface.
- ~~**nestgate.io mesh bridge + mesh.peers (S7)**~~ — **PHASE 2 LIVE.** Neural API bridge discovers 20 primals, **9/12 sections** functional. mesh.peers WIRED (songBird UDS). Remaining: health liveness per primal (S8/NG-03), bearDog routing stub (NG-04).
- **squirrel deploy on ironGate (E2)** — petal-bridge routes `agent.*` → squirrel UDS but squirrel process needs to be running. Deploy as systemd service with `squirrel.sock` at canonical path.
- ~~**nestGate dual-path CAS (O4)**~~ — **SHIPPED.** `NESTGATE_WARM_PATHS` + `NESTGATE_COLD_PATHS` for 2-tier. 7 CAS handlers updated. Backward-compatible.
- ~~arXiv plaquette ×4 normalization~~ — **RESOLVED** (gauge group mismatch SU(2)→SU(3). 12⁴ data paper-ready. Rung 1 UNBLOCKED).
- ~~squirrel → biomeOS G18 integration~~ — **LIVE on ironGate** (Session 10). 9 providers, cross-primal dispatch validated.
- Inter-gate content.get live test (songBird probes + nestGate content.fetch ready)
- petalTongue WebGPU/wgpu evolution (G53 maturation) — conjugation layer (RustScript) established, petalTongue render pipeline is the remaining gap
- ~~barraCuda PRNG validation~~ — **FIXED** (YELLOW→GREEN, statistical validation harness)
- ~~BTSP transport signal documentation~~ — SHIPPED

---

*Last used*: Wave 157k CASCADE — strandGate 45 QCD configs banked (cross-GPU 0.19%). biomeGate K80 wedge hunt (4 bugs, PROM decoded, vendor tools excised). SOVEREIGN_GROUND_TRUTH.md established. sporePrint concept evolved: static Zola → NUCLEUS-served live data surface with semantic layer. 12 gates ONLINE. **19 COMPLETE, 26 ACTIVE, 21 GLACIAL**. 0/0/0. (Aug 17, 2026)
*Created*: Wave 139a
*First fossilization*: Wave 150p
*Latest fossilization*: Wave 157k — 217 files fossilized across 19 wave directories. 14 files in `wave157k_interstadial/` (5 gate AARs + 4 stale handoffs + 5 absorbed docs). (1,494+ total records)
*Latest checkpoint*: Wave 157k CASCADE — strandGate 45 QCD configs (cross-GPU 0.19%, protocol mismatch identified, 2000+ warmup needed). biomeGate K80 PROM VBIOS decoded (4 wedge bugs fixed, die survives cold bring-up ×4, opcode coverage sole blocker). Vendor tool excision (sysfs replaces nvidia-smi, 1→4 GPUs found, 216 hidden test failures recovered). SOVEREIGN_GROUND_TRUTH.md (no shader has ever executed on sovereign path). 6 ecosystem-wide gaps raised. sporePrint concept evolved: Zola → NUCLEUS-served live data surface. barraCuda upstream needs: configurable warmup P1, plaquette time-series P1. 227 files fossilized. (Aug 17, 2026)
*Latest reopen*: Wave 155k (D10 — Jelly Strings J9–J13, extended to J14–J19 in 155n)
