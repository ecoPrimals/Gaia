# Wave 68 — Remaining Evolution Work & Team Decomposition

**Date**: 2026-06-02
**Author**: eastGate (overwatch)
**Wave**: 68 (post sovereign evolution strategic review)
**Status**: Active — guides Wave 69+ assignments

---

## Executive Summary

Infrastructure is ~9.5/10 built. Deep debt is cleared (18/18). Cascade is at
38/38 parity. Four sovereignty shadows are live (S1-S4), DNS infra operational.
The remaining work falls into **five tracks**, each owned by a specific gate.

---

## Track 1: Glacial Cutover (P0 — blocks sovereignty)

The hard requirements before we can call the glacial shift complete.

### 1A. Live Mesh Validation (eastGate + southGate)

| Item | Owner | Status | Next |
|------|-------|--------|------|
| `discovery.peers` same-subnet live test | eastGate (primalSpring) | UNBLOCKED | Seed `SONGBIRD_PEERS` on eastGate+southGate, run `s_covalent_mesh` live |
| `capability.call` cross-gate smoke test | eastGate (primalSpring) | UNBLOCKED | biomeOS capability.call done (9ed36983), scenario written, needs live run |
| Cross-subnet routing (southGate 192.168.4.x) | infra | UNBLOCKED | southGate is on Eero mesh bridge, Cat6e to backbone — should route directly |
| Plasmodium collective (3+ gates meshed) | eastGate | BLOCKED on above | After 2-gate mesh verified, add ironGate/biomeGate |

**Who runs it**: eastGate drives primalSpring scenarios, southGate provides
Songbird + biomeOS endpoints. This is a paired test — both gates online
simultaneously.

### 1B. Sovereignty Shadow Graduation (ironGate + cellMembrane)

| Shadow | Status | Remaining | Owner |
|--------|--------|-----------|-------|
| S1 TLS | 13d PASSED | Graduate: remove Cloudflare config, update DNS TXT records | ironGate (cellMembrane) |
| S2 NAT | DONE | Graduated | — |
| S3 Content | LIVE | Cutover after DNS NS switch: update sporePrint build to target VPS | ironGate (cellMembrane) + flockGate (sporePrint) |
| S4 Auth | Shadow live | Formal 7-day gate: restart ironGate services with bearDog BTSP as sole auth | ironGate + southGate (bearDog) |
| S5 DNS | Infra LIVE | **Manual registrar action**: point NS records to ns1.primals.eco + ns2.primals.eco | operator (manual) |

**Who runs it**: ironGate runs the S4 formal gate + graduates S1. Operator does
the DNS registrar cutover (manual, instructions in `DNS_NS_CUTOVER_INSTRUCTIONS.md`).
flockGate updates sporePrint for S3 content cutover.

### 1C. Cloudflare Removal (post-cutover)

After all shadows graduated and DNS cut over:
1. Remove Cloudflare proxy from all DNS records
2. Delete Cloudflare zone configuration
3. Verify all traffic routes through sovereign stack
4. 7-day monitoring period, then decommission

**Who runs it**: operator (manual) + ironGate (cellMembrane validation).

---

## Track 2: Primal Code Evolution (P1 — quality + capability)

Active evolution work on primal codebases.

### 2A. southGate — Mesh + Orchestration + Security

| Primal | Work | Priority |
|--------|------|----------|
| **Songbird** | Virtual endpoint relay (Phase B from design doc). `latency_ms` in `discovery.peers` response. sled→redb migration. | P2 |
| **biomeOS** | L4 weighted routing: wire `ProviderWeight::score()` into `discover_capability`. Topology affinity factor. `--tcp-only` deprecation. | P1 |
| **bearDog** | Hardware-backed keystore design (for grapheneGate). S4 auth formal validation partner. ACME → sovereign cert management. | P2 |

**FRAGO dispatched**: `wave68-biomeos-l4-weighted-routing.toml` covers biomeOS L4 + topology.

### 2B. biomeGate — Compute Trio

| Primal | Work | Priority |
|--------|------|----------|
| **toadStool** | PBDMA runlist root cause. VFIO enumeration (GAP-BC-002). Exp 234 Run #6 completion. | P1 |
| **barraCuda** | `ml.mlp_train` wiring for perceptron routing. Pure Rust math evolution. | P2 |
| **coralReef** | SM120 barrier fix landed. SPIR-V output (GAP-HS-124). Blackwell zero readback (GAP-HS-115). Math pack/unpack evolution. | P1 |

**FRAGO dispatched**: `wave68-biomegate-compute-trio-onboarding.toml` + `wave68-biomegate-exp234-hpc-update.toml`.

### 2C. strandGate — Provenance Trio

| Primal | Work | Priority |
|--------|------|----------|
| **rhizoCrypt** | v0.14.1 landed (neural_api extracted, handler tests split). Next: eager peer population hardening. | P2 |
| **loamSpine** | Tokio runtime-in-runtime panic on health probe (2 gates affected). | P2 |
| **sweetGrass** | v0.7.43 landed (convergence + privacy + probes). Next: attribution completeness. | P3 |

**Note**: strandGate hardware not deployed yet. Provenance trio currently runs on
other gates; strandGate deployment is post-mesh-validation.

### 2D. ironGate — Infra + Deployment

| Project | Work | Priority |
|---------|------|----------|
| **cellMembrane** | Graduated composition (Wave 68 handoff landed). Relay bash→Rust (4 remaining scripts on golgiBody). | P1 |
| **projectNUCLEUS** | Forgejo Actions CI. Deploy graph evolution. | P2 |
| **NestGate** | v0.5.0 unified. Session 82 audit complete. Stable. | Maintenance |
| **petalTongue** | v1.67 flockGate review done. WASM rendering stable. | Maintenance |

### 2E. eastGate — Coordination + Evolution

| Project | Work | Priority |
|---------|------|----------|
| **primalSpring** | Perceptron feature extraction (Wave 70). Topology-aware dispatch integration. Validation scenario hardening. | P2 |
| **squirrel** | Stable. Context-aware composition planning. | Maintenance |
| **skunkBat** | Stable. Session management. | Maintenance |

---

## Track 3: Dependency Evolution (P2 — Rust purity)

Cross-cutting dependency modernization.

| Dependency | Current | Target | Owner | Priority |
|------------|---------|--------|-------|----------|
| sled → redb | Songbird, rhizoCrypt | redb (maintained, safe Rust) | southGate (Songbird), strandGate (rhizoCrypt) | P2 |
| ring → rustls-only | bearDog, others | Eliminate ring C dependency | southGate (bearDog) | P2 |
| rustls-pemfile removal | bearDog | Absorbed into cert stack | southGate (bearDog) — Wave 123 handoff landed | P2 |
| neuralSpring `target/release/` hardcode | neuralSpring | Fix `composition_nucleus.sh` | southGate | P3 |
| loamSpine Tokio panic | loamSpine | Runtime-in-runtime fix | strandGate | P2 |

**FRAGO dispatched**: `wave68-dependency-evolution-coordination.toml`.

---

## Track 4: Strategic Evolution (P2-P3 — capability expansion)

New capabilities from the Wave 68 sovereign evolution review.

### 4A. Songbird Routing Consolidation

| Phase | What | Owner | Status |
|-------|------|-------|--------|
| A: TCP Tier 5 elimination | Release builds block TCP. Droppable ports validated. | eastGate | **DONE** (Wave 68) |
| B: Virtual endpoint relay | Songbird as universal RPC relay. Single-ingress. | southGate | **DESIGNED** (`SONGBIRD_VIRTUAL_ENDPOINT_RELAY_DESIGN.md`) |
| C: Membrane TLS sovereignty | Songbird terminates TLS, Caddy removed. | ironGate | Horizon |

### 4B. Neural API Perceptron

| Phase | What | Owner | Status |
|-------|------|-------|--------|
| L4 weighted selection | Replace first-match with `ProviderWeight::score()` | southGate (biomeOS) | **Impulse dispatched** |
| L5 perceptron design | Single-layer perceptron, shadow mode, graduation | eastGate + biomeGate | **DESIGNED** (`NEURAL_API_PERCEPTRON_DESIGN.md`) |
| Training pipeline | `dispatch_telemetry.jsonl` → barraCuda `ml.mlp_train` | biomeGate (barraCuda) | P3 |

### 4C. grapheneGate Trust Anchor

| Role | What | Owner | Status |
|------|------|-------|--------|
| Manifest + standard | Ecosystem manifest entry, bootstrap standard | eastGate | **DONE** (Wave 68) |
| Role 1: Beacon | BirdSong broadcast + lineage verification | eastGate + southGate (bearDog) | P2 |
| Role 2: BTSP Relay | Songbird relay on phone, bootstrap via USB | southGate (Songbird) | P3 |
| Role 3: Mesh Seed | Full sovereign bootstrap from phone | Horizon | Horizon |

### 4D. Topology-Aware Routing

| Phase | What | Owner | Status |
|-------|------|-------|--------|
| A: Topology discovery | TOPOLOGY_MAP.toml, latency in discovery.peers | eastGate | **DONE** (Wave 68) |
| B: Locality-biased routing | Topology factor in ProviderWeight::score() | southGate (biomeOS) | **Impulse dispatched** |
| C: Segment-aware deployment | biomeOS graph.deploy considers topology | Horizon | Horizon |

---

## Track 5: Infrastructure Expansion (P3 — capacity)

Gates that are hardware-ready but not deployed.

| Gate | Hardware | Planned Role | Blocker |
|------|----------|-------------|---------|
| **strandGate** | Dual EPYC 7452, 256GB ECC | Full NUCLEUS, provenance trio, bioinformatics | Mesh validation must complete first |
| **northGate** | Ryzen 9950X3D, RTX 5090, 96GB | Heavy compute, AI/LLM inference | No active blocker, priority P3 |
| **westGate** | i7-4771, RTX 2070 Super, 32GB, **76TB ZFS** | Nest Atomic cold storage | No active blocker, priority P3 |
| **swiftGate** | Ryzen 5800X, RTX 3070, 64GB | Mobile/compact deployment | No active blocker, priority P4 |
| **kinGate** | i7-6700K, RTX 3070, 32GB | Staging, testing | No active blocker, priority P4 |

---

## Team Decomposition — Wave 69+ Assignments

### eastGate (overwatch)
- **P0**: Live mesh validation (`discovery.peers` + `capability.call`)
- **P0**: DNS NS registrar cutover (manual, operator action)
- **P1**: Cloudflare removal post-cutover
- **P2**: Perceptron feature extraction in primalSpring
- **P2**: grapheneGate Role 1 (beacon test with bearDog)

### ironGate (infra + deployment)
- **P0**: S1 TLS graduation (remove Cloudflare config)
- **P0**: S4 Auth formal 7-day gate (restart services with BTSP-only)
- **P1**: cellMembrane relay bash→Rust (4 scripts)
- **P2**: Forgejo Actions CI
- **P2**: S3 content cutover coordination with flockGate

### southGate (mesh + orchestration + security)
- **P1**: biomeOS L4 weighted routing (replace first-match with score())
- **P1**: biomeOS topology affinity factor
- **P0**: Mesh validation partner (provide Songbird/biomeOS endpoints)
- **P2**: Songbird virtual endpoint relay (Phase B implementation)
- **P2**: bearDog sled→redb, ring elimination
- **P2**: Songbird latency_ms in discovery.peers

### biomeGate (HPC + compute trio)
- **P1**: toadStool PBDMA runlist + Exp 234
- **P1**: coralReef SPIR-V output + Blackwell zero readback
- **P2**: barraCuda ml.mlp_train wiring for perceptron
- **P2**: coralReef math pack/unpack evolution

### flockGate (content + WAN)
- **P2**: sporePrint S3 content cutover (target VPS instead of GitHub Pages)
- Maintenance: WAN relay validation, sporePrint content pipeline

### strandGate (provenance + science)
- **P2**: loamSpine Tokio runtime panic fix
- **P2**: rhizoCrypt eager peer population hardening
- **P3**: Hardware deployment (post mesh validation)
- **P3**: sweetGrass attribution completeness

---

## Decision Log

| Decision | Rationale | Wave |
|----------|-----------|------|
| Compute trio moved to biomeGate | Consolidate GPU work; Threadripper + Titan V best suited | 68 |
| grapheneGate as `portable_anchor` gate class | Phone is physically carried; distinct from stationary gates | 68 |
| TCP Tier 5 blocked in release builds | Glacial zero-port standard; debug builds still allow for testing | 68 |
| Blurbs formally codified alongside Handoffs/FRAGOs | Recognized as pragmatic AI-team interface; graduates to context braids | 68 |
| TOPOLOGY_MAP.toml published | Machine-readable network model enables topology-aware routing | 68 |

---

*Wave 68. The infrastructure is built. The mesh validates. The routing learns.
Trust goes portable. Five tracks, six gates, one water.*
