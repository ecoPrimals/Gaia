# Wave 70 — Remaining Work & Status

**Date**: 2026-06-03 (Wave 74 update)
**Author**: eastGate (overwatch + evolution)
**Wave**: 74 (post Songbird critical path fix)
**Status**: Active — guides Wave 74+ assignments
**Supersedes**: WAVE68_SOVEREIGN_EVOLUTION_REMAINING_WORK_JUN02_2026.md (archived)

---

## Executive Summary

**SONGBIRD CRITICAL PATH FIX DEPLOYED.** All 4 P1/P2 blockers resolved (d6a6f714):
HTTP POST dispatch, mesh_seed auto-bootstrap, string format parsing, latency in health
cycle. Cross-gate `capability.call` UNBLOCKED. Full ecosystem sprint: barraCuda
ml.mlp_train COMPLETE (strandGate, <150ms). biomeOS v3.99 perceptron consumer (shadow).
bearDog w131 scopes fixed. NestGate ZFS backend + federation + route.register. sporePrint
cas-manifest + CAS design. petalTongue mesh content routing + WASM trim. Every team delivered.

**Critical path**: Live capability.call test → 3-gate plasmodium → DNS NS cutover.

---

## Track 1: Glacial Cutover (P0)

### 1A. Live Mesh Validation (eastGate + strandGate) — WAVE 72 UPDATE

| Item | Status | Notes |
|------|--------|-------|
| Songbird `latency_ms` in `discovery.peers` | **DONE** | Wired into health cycle every 4th tick (~2min). Songbird w73. |
| biomeOS endpoints ready | **DONE** | v3.99: gate.register + perceptron consumer |
| `discovery.peers` live 2-gate test | **DONE** | Wave 72: eastGate ↔ strandGate, 1 peer, quality 1.0 |
| Songbird HTTP dispatch fix | **DONE** | d6a6f714: HTTP POST to /jsonrpc. FRAGO resolved. |
| Songbird mesh_seed auto-bootstrap | **DONE** | d6a6f714: spawn_mesh_seed wired into startup. |
| `capability.call` cross-gate test | **UNBLOCKED** | Songbird fix deployed. **LIVE TEST NEXT** |
| Cross-subnet routing (192.168.4.x) | **DEFERRED** | Eero doesn't route VLANs. TURN relay available |
| 3+ gate plasmodium collective | **UNBLOCKED** | After capability.call verified, add ironGate (.238) |

**Critical path**: capability.call live test. Songbird fix deployed — execute NOW.

### 1B. Sovereignty Shadow Graduation

| Shadow | Status | Remaining |
|--------|--------|-----------|
| S1 TLS | **Infra verified** (198 probes, 0 failures, p95 < 120ms) | NS cutover (registrar manual) → remove Cloudflare |
| S2 NAT | **GRADUATED** | — |
| S3 Content | **Ready** (sporePrint 101 tests, zero-C, 67ms TTFB) | Cutover after DNS NS switch |
| S4 Auth | **7-day gate ACTIVE** (started Jun 2, ends ~Jun 9) | Monitoring via 15-min probes |
| S5 DNS | **Infra LIVE** (knot-dns, DNSSEC) | Registrar NS cutover (operator) |

**Critical path**: Operator DNS NS registrar cutover. S4 gate runs autonomously until ~Jun 9.

---

## Track 2: Primal Code Evolution (P1-P2)

### 2A. southGate — ALL P1 COMPLETE

| Primal | Delivered | Remaining |
|--------|-----------|-----------|
| **Songbird** v0.2.5 w73 | All previous + **HTTP dispatch FIX** (d6a6f714), **mesh_seed auto-bootstrap**, string format parsing, **latency in health cycle** | Virtual relay Phase 2 (flip default, BTSP relay), TLS sovereignty (Phase C, horizon), env var alignment with biomeOS |
| **biomeOS** v3.99 | All previous + **perceptron consumer interface** (36-dim, shadow mode, weight I/O, 13 tests), **test extraction wave 3** (771L extracted from http_client + lifecycle_manager) | A/B shadow analysis (1000 dispatch milestone), perceptron Phase 2 (epsilon-greedy, after trained weights), cross-gate mesh testing |
| **bearDog** v0.9.0 w131 | All previous + **auth.verify_ionic scopes FIXED** (top-level scopes in all responses), health.liveness confirmed ALREADY IMPLEMENTED, Android type stack confirmed ALREADY feature-gated | AI deprecated modules design (type incompatibility, needs redesign), pure-Rust crypto tracking, mobile feature flag |

### 2B. biomeGate — OFFLINE (kernel recovery)

| Primal | Last State | Reassigned? |
|--------|------------|-------------|
| **toadStool** | Wave 68: PBDMA diagnostic, wgpu dispatch verified | **NO** — Titan V hardware-dependent, stays biomeGate |
| **coralReef** | Wave 68: SM120 barrier fix, SPIR-V prep | **PARTIAL** — SPIR-V compiler work → strandGate. SM120 Blackwell testing stays biomeGate |
| **barraCuda** | Wave 68: deep debt complete | **YES** — ml.mlp_train → strandGate (pure software) |

toadStool ownership stays biomeGate. Resume trigger: kernel recovery + cascade sync.
FRAGO: `wave72-strandgate-compute-trio-pickup` (supersedes `wave70-biomegate-down-compute-trio-paused`)

### 2C. strandGate — ACTIVE (provenance + compute trio pickup)

| Primal | Status |
|--------|--------|
| **loamSpine** | Tokio panic **FIXED**, anchoring pipeline **COMPLETE** |
| **rhizoCrypt** | Discovery fallback hardening **DONE** |
| **sweetGrass** | PROV-O completeness, privacy edge tests, store parity **DONE** |
| **barraCuda** (pickup) | **ml.mlp_train COMPLETE** — 36→16 perceptron, <150ms, dual-mode (dims + explicit), 6 new tests. MESH PEER LIVE. | coralReef SPIR-V (next) |
| **coralReef** (partial pickup) | SPIR-V output compiler next (pure software). SM120 Blackwell testing remains biomeGate |

strandGate hardware: Dual EPYC 7452 (64c), 256GB ECC — ideal for pure-software compute work.
Hardware deployment (NUCLEUS) also proceeds on strandGate.

### 2D. ironGate — Sovereignty EXECUTED

| Project | Delivered | Remaining |
|---------|-----------|-----------|
| **cellMembrane** w71 | S1 verified, S4 activated, disk 60%, membrane on VPS, relay Rust-native, **legacy cascade() REMOVED**, **3 new commands** (relay.status, gate.health, content.verify), **S3 VPS READY** (Caddyfile configured, cutover = single DNS flip) | S4 monitoring (auto, ends ~Jun 9), NS cutover (operator), S3 cutover coord |
| **projectNUCLEUS** w73 | All previous + **CI runner provisioning script**, **primalSpring CI workflow PoC**, **genomeBin harvest automation**, strandGate + westGate deploy graphs | Forgejo Actions full implementation (P2), plasmidbin auto-symlinks (P2) |
| **projectFOUNDATION** w73 | All previous + **lineage freshness updated** (41,500+ ecosystem checks), **SPRING_VERSIONS.toml** (machine-readable), mesh evaluation spec (cross-gate = guideStone responsibility) | Spring evolution auto-tracking (P3), drift detection (P3) |
| **NestGate** v0.5.0 s85 | All previous + **ZFS backend env** (`NESTGATE_STORAGE_BASE_PATH`), **content.replicate.pull** (cold-from-hot), **route.register** for mesh, 12,537 tests | westGate onboarding (ZFS dataset provision), cross-gate integration test, streaming transfer (P3) |
| **petalTongue** v1.6.8 w73 | All previous + **mesh content routing** (4-tier discovery: UDS→TCP→socket-dir→mesh), **WASM trim** (toml+tracing removed), **Tokio reduction** (dead deps from 3 crates), 6,209 tests | Sovereign rendering post-cutover, WASM bundle profiling (P3) |

### 2E. flockGate

| Project | Delivered | Remaining |
|---------|-----------|-----------|
| **sporePrint** w73 | All previous + **cas-manifest subcommand** (BLAKE3 hashing), **pre-cutover verification doc**, **NestGate CAS integration 4-phase design**, GitHub URL audit (zero hardcoded), 107 tests | S3 cutover execution (post-DNS), CAS Phase 1 implementation (P2) |

### 2F. eastGate

| Project | Status | Remaining |
|---------|--------|-----------|
| **primalSpring** v0.9.31 w72 | Security hardened, deprecated API migration, **LIVE MESH VALIDATED**, s_covalent_mesh wire format fix, **AAR published**, 842 tests | **capability.call live test (P0)** — Songbird fix deployed! 3-gate plasmodium. Perceptron feature extraction. Composition mesh awareness. |
| **squirrel** | Stable | Mesh-aware composition planning for multi-gate dispatch (P3) |
| **skunkBat** | Stable | westGate enrollment FRAGO active. Family seed protocol. (P2) |

---

## Track 3: Dependency Evolution — LARGELY COMPLETE

| Dependency | Status |
|------------|--------|
| sled → redb | **N/A** — sled eliminated from Songbird (Wave 135), never in rhizoCrypt |
| ring → aws-lc-rs | **DONE** — bearDog Wave 125, deny.toml bans ring |
| rustls-pemfile | **DONE** — absorbed into cert stack |
| loamSpine Tokio panic | **DONE** — already fixed |
| neuralSpring target/release hardcode | Open (P3, low priority) |
| bincode 1.x RUSTSEC | Open — blocked on tarpc upstream (not actionable) |
| hickory-resolver 0.26 | Deferred — upstream SRV/TXT API unstable |

---

## Track 4: Strategic Evolution

### 4A. Songbird Routing Consolidation

| Phase | Status |
|-------|--------|
| A: TCP Tier 5 elimination | **DONE** |
| B: Virtual endpoint relay | **Phase 1 LIVE** (shadow mode, opt-in). Phase 2: flip default, BTSP validation, connection pooling |
| C: Membrane TLS sovereignty | Horizon — post S1 graduation |

### 4B. Neural API Perceptron

| Phase | Status |
|-------|--------|
| L4 weighted selection | **DONE** (biomeOS v3.94) |
| L4 topology affinity | **DONE** (biomeOS v3.94) |
| A/B shadow analysis | **ACTIVE** (1000 dispatch counter running) |
| PathwayLearner feedback | **WIRED** (per-node graph execution timing) |
| L5 perceptron training | **UNBLOCKED** — barraCuda ml.mlp_train COMPLETE (strandGate). biomeOS consumer ready. |

### 4C. grapheneGate Trust Anchor

| Role | Status |
|------|--------|
| Manifest + standard | **DONE** |
| Role 1: Beacon | P2 — bearDog keystore design DONE. Phase 2 hardware wiring (NDK + device) |
| Role 2: BTSP Relay | P3 |
| Role 3: Mesh Seed | Horizon |

### 4D. Topology-Aware Routing

| Phase | Status |
|-------|--------|
| A: TOPOLOGY_MAP.toml + latency discovery | **DONE** |
| B: Locality-biased routing | **DONE** (biomeOS topology affinity factor) |
| C: Segment-aware deployment | Horizon |

---

## Track 5: Infrastructure Expansion (P3)

strandGate ACTIVATED for compute trio pickup. westGate expected back online this week.

| Gate | Planned Role | Status | Blocker |
|------|-------------|--------|---------|
| strandGate | Provenance trio + compute trio pickup (barraCuda, coralReef SPIR-V) | **ACTIVE** — assigned via FRAGO wave72 | NUCLEUS deployment needed |
| westGate | 76TB ZFS cold storage (Nest Atomic) | **INCOMING** — ETA this week | Gate setup + NUCLEUS deploy |
| northGate | Heavy compute, AI/LLM | Hardware ready | No blocker (P3) |
| swiftGate | Mobile/compact | Hardware ready | No blocker (P4) |
| kinGate | Staging | Hardware ready | No blocker (P4) |

---

## Immediate Critical Path (Priority Order)

1. **Live capability.call cross-gate test (P0)** — Songbird fix deployed. Execute NOW.
2. **3-gate plasmodium collective (P0)** — after capability.call works, add ironGate (.238).
3. **S4 Auth 7-day gate** — running autonomously, ends ~Jun 9.
4. **DNS NS registrar cutover** — operator manual action.
5. **S1 TLS graduation** — after NS cutover, remove Cloudflare.
6. **S3 content cutover** — after DNS, sporePrint targets VPS (single flip).
7. **Perceptron end-to-end** — barraCuda training DONE + biomeOS consumer DONE = wire together.
8. **westGate bring-up** — ETA this week. 76TB ZFS. NestGate CAS ready.
9. **coralReef SPIR-V** — strandGate next compute item.
10. **biomeGate recovery** — toadStool + coralReef Blackwell testing.

---

## Decision Log (Wave 70 additions)

| Decision | Rationale | Wave |
|----------|-----------|------|
| Compute trio PAUSED, not transferred | Hardware-dependent work blocked; software items available for opportunistic pickup | 70 |
| strandGate FRAGO archived | All items resolved by upstream teams | 70 |
| 3 biomeGate FRAGOs consolidated | Superseded by single wave70 pause FRAGO | 70 |
| Wave 68 remaining work archived | Superseded by this document | 70 |
| Compute trio → strandGate (partial) | barraCuda (full) + coralReef SPIR-V (partial) moved to strandGate. toadStool stays biomeGate (hardware). | 72 |
| westGate incoming | ETA this week. 76TB ZFS cold storage, Nest Atomic role. | 72 |

---

*Wave 74. Songbird critical path FIX DEPLOYED. capability.call UNBLOCKED. barraCuda
ml.mlp_train COMPLETE. biomeOS perceptron consumer READY. Every team delivered.
The glacial shift accelerates. Evolution never stops.*
