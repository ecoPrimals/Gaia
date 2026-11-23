# Wave 79 Parity Blurbs — Ecosystem Level

**Date**: 2026-06-05 | **Source**: eastGate overwatch ecosystem survey
**Updated**: Wave 79 — BD-TRUST-01 resolved, UDS-only stadial gate, transport evolution formalized
**Purpose**: Copy-paste context per team. Primals first, then springs.
Springs inherit full primal parity — solve primals, springs follow.

**Ecosystem standard (Wave 79)**:
- Zero clippy (pedantic + nursery)
- Zero `#[allow]` in production
- `capability_registry.toml` (machine-readable, TOML)
- BTSP Phase 3
- Wire Standard L2+
- MethodGate pre-dispatch
- plasmidBin ecoBin compliant
- `forbid(unsafe_code)` or justified opt-out
- 90% line coverage (stadial target)
- **UDS-only default** — no standalone TCP ports (Wave 79 stadial gate)
- **Transport-ignorant target** — primals must not hardcode transport (see `TRANSPORT_EVOLUTION.md`)

---

# PRIMALS

---

## bearDog — REFERENCE TIER

**Version**: v0.9.0 | **Wave**: 140 | **Tests**: 15,004 | **Coverage**: 90.5%
**Registry**: `capability_registry.toml` at root (not `config/`)
**Last commit**: Jun 4

**Status**: Ecosystem reference. Zero gaps. BD-TRUST-01 `auth.exchange_trust`
delivered. S4 auth graduation ~Jun 9.

**Parity items**: NONE. Move `capability_registry.toml` to `config/` for
consistency with biomeOS/petalTongue/sweetGrass convention (optional hygiene).

---

## songBird — P0 TRANSPORT EVOLUTION + P1 COVERAGE

**Version**: v0.2.9 | **Wave**: 81 | **Tests**: 13,971+ | **Coverage**: 73.4%
**Registry**: Has `capability_registry.toml` ✓ (delivered Wave 81)
**Last commit**: Jun 5

**RESOLVED this wave**:
- SB-TLS-01 (direct-mode TLS crypto) ✓
- SB-TLS-02 (Phase 3.5 Ed25519 relay verification) ✓
- **BD-TRUST-01** (`auth.exchange_trust` wired into `mesh.init`) ✓
- Deep debt: 8 inline port literals → `songbird_types::defaults` constants ✓
- Production stubs hardened (NFC, lineage, TLS) ✓

**P0 — Transport evolution**: Songbird is the universal routing bus.
`ipc.resolve` must evolve to return transport-qualified endpoints:
```json
{ "transport": "uds", "path": "/run/membrane/beardog.sock" }
{ "transport": "mesh_relay", "peer_id": "strand-gate", "capability": "security" }
```
See FRAGO `wave79-transport-evolution-capability-routing` and
`primalSpring/docs/TRANSPORT_EVOLUTION.md`.

**P1 — Coverage sprint**: 73.4% → 90%. Largest quantitative gap across all
14 primals. Every other primal with significant surface is 80%+.

**P3 — Doc drift**: README says v0.2.8-wave76, CHANGELOG says v0.2.9-wave81.
Sync banner.

---

## biomeOS — REFERENCE TIER

**Version**: v4.07 | **Wave**: 77 | **Tests**: 7,983 | **Coverage**: 90%+
**Registry**: `config/capability_registry.toml` ✓
**Last commit**: Jun 4

**Status**: NUCLEUS orchestrator reference. 27 domains, 320+ translations.
L5 perceptron in shadow mode. Zero blocking debt.

**Parity items**: NONE.

---

## toadStool — P2 REGISTRY + COVERAGE

**Version**: v0.2.0 | **Session**: S290 | **Tests**: 23,000+ | **Coverage**: ~84%
**Registry**: MISSING `capability_registry.toml`
**Last commit**: Jun 4

**Status**: Largest test suite in ecosystem. 46 documented `unsafe` in hardware
containment crates (justified). CallerContext fan_out wired.

**P2 — Create `config/capability_registry.toml`**:
```toml
[capabilities.compute]
owner = "toadstool"
methods = [
    "compute.dispatch.submit",
    "compute.capabilities",
    "compute.dispatch.verify_trust",
    "toadstool.validate",
    "toadstool.list_workloads",
]
```

**P2 — Coverage**: 84% → 90%. Hardware paths inherently gapped — focus
coverage on non-VFIO code paths.

---

## nestGate — P2 COVERAGE

**Version**: v0.5.0 | **Session**: 93 | **Tests**: 12,551 | **Coverage**: ~84%
**Registry**: Has `capability_registry.rs` in code (Rust), not TOML
**Last commit**: Jun 4

**Status**: Storage/content leader. HTTP parity complete. All 8 `content.*`
methods on all 4 transport surfaces.

**P2 — Create `config/capability_registry.toml`**: Extract from Rust registry
to TOML format for ecosystem tooling consistency.

**P2 — Coverage**: 84% → 90%. Focus on content pipeline paths and HTTP API
handlers.

---

## squirrel — CLEAN

**Version**: v0.1.0 | **Wave**: 76 | **Tests**: 7,098 | **Coverage**: 90.1%
**Registry**: `capability_registry.toml` at root ✓
**Last commit**: Jun 3

**Status**: Coverage target met. Inference/BTSP/MethodGate parity strong.
`CONSUMED_CAPABILITIES` in `niche.rs`.

**Parity items**: Move `capability_registry.toml` to `config/` for convention
consistency (optional hygiene).

---

## barraCuda — P2 REGISTRY + COVERAGE

**Version**: v0.4.0 | **Wave**: 76 | **Tests**: 4,393 | **Coverage**: 81%
**Registry**: MISSING `capability_registry.toml` (inline in `primal.rs`)
**Last commit**: Jun 4

**Status**: Sovereign dispatch wire extracted. 96 JSON-RPC methods. Stadial
gate release. GPU coverage requires real hardware (llvmpipe only reaches 81%).

**P2 — Create `config/capability_registry.toml`**:
```toml
[capabilities.math]
owner = "barracuda"
methods = [
    "stats.mean",
    "stats.variance",
    "stats.std",
    "precision.route",
    "tensor.create",
]

[capabilities.compute_dispatch]
owner = "barracuda"
methods = [
    "compute.dispatch.submit",
]
```

**P2 — Coverage**: 81% → 90%. Hardware-gated — track llvmpipe and real GPU
separately.

---

## petalTongue — P2 COVERAGE (sprint active)

**Version**: v1.6.6 | **Wave**: 78 | **Tests**: 6,259 | **Coverage**: ~85%+
**Registry**: `config/capability_registry.toml` ✓
**Last commit**: Jun 5

**Status**: Coverage sprint active — 42 new tests added (Wave 78). Deep debt
passes 4-5 completed (tokio narrowing, anyhow demotion, format idiom cleanup).

**Parity items**:
**P2 — Coverage**: 85% → 90%. Continue coverage sprint on content-backend
and discovery integration paths.

---

## rhizoCrypt — CLEAN (delivered Wave 78)

**Version**: v0.14.2 | **Wave**: 78 | **Tests**: 1,683+ | **Coverage**: stadial
**Registry**: `config/capability_registry.toml` ✓ (moved from root Wave 78)
**Last commit**: Jun 5

**Status**: ALL BLURB ITEMS DELIVERED:
- ✓ Mesh-trust session auto-provision on first poll result
- ✓ DAG append: `poll_events()` results wired into `append_vertex()`
- ✓ Lifecycle wiring: `spawn_mesh_poller()` called after `Arc::new(primal)`
- ✓ `capability_registry.toml` moved to `config/`

**Parity items**: NONE. VPS binary refresh needed (deployed is pre-Wave 78).

---

## loamSpine — P2 REGISTRY

**Version**: v0.9.16 | **Wave**: 76 | **Tests**: 1,600 | **Coverage**: 90.9%
**Registry**: MISSING `capability_registry.toml` (`CONSUMED_CAPABILITIES` in `niche.rs`)
**Last commit**: Jun 4

**Status**: Coverage met. Trust ledger IPC wired. Provenance trio complete.

**P2 — Create `config/capability_registry.toml`**:
```toml
[capabilities.ledger]
owner = "loamspine"
methods = [
    "spine.create",
    "spine.list",
    "spine.status",
    "entry.append",
    "entry.list",
    "entry.get",
]

[capabilities.session]
owner = "loamspine"
methods = [
    "session.create",
    "session.commit",
    "session.status",
]
```

---

## sweetGrass — CLEAN

**Version**: v0.7.48 | **Wave**: 78b | **Tests**: 1,623 | **Coverage**: 91.7%
**Registry**: `config/capability_registry.toml` ✓
**Last commit**: Jun 4

**Status**: Coverage met. Zero hot-path env reads. Cross-gate trust weaving.
Attribution/provenance leader.

**Parity items**: rhizoCrypt DAG append + lifecycle wiring DELIVERED (Wave 78).
Attribution braid testing against live mesh events now UNBLOCKED.

---

## coralReef — P2 REGISTRY

**Version**: v0.2.0 | **Wave**: 78 | **Tests**: 3,307 | **Coverage**: clean
**Registry**: MISSING `capability_registry.toml` (self-knowledge in code)
**Last commit**: Jun 4

**Status**: Pure compiler domain. Phase D hardware cutover to toadStool.
SPIR-V E2E proven. Zero unsafe/FFI.

**P2 — Create `config/capability_registry.toml`**:
```toml
[capabilities.shader]
owner = "coralreef"
methods = [
    "shader.compile.wgsl",
    "shader.compile.capabilities",
    "shader.compile.module",
]
```

---

## skunkBat — P2 REGISTRY + SCALE

**Version**: v0.2.2 | **Wave**: 76b | **Tests**: 391 | **Coverage**: 90%+ fn
**Registry**: MISSING `capability_registry.toml` (`CONSUMED_CAPABILITIES` in `dispatch.rs`)
**Last commit**: Jun 4

**Status**: Defense meta-primal. westGate deployment primal.
`defense.status` health probe added. Smallest test surface (391 vs 1,600-15,000).

**P2 — Create `config/capability_registry.toml`**:
```toml
[capabilities.defense]
owner = "skunkbat"
methods = [
    "defense.status",
    "defense.audit",
    "security.audit_log",
]

[capabilities.reconnaissance]
owner = "skunkbat"
methods = [
    "reconnaissance.scan",
    "reconnaissance.report",
]
```

**P3 — Scale**: Consider expanding test surface to at least 500+ to cover
thymic selection design when it moves from spec to implementation.

---

## sourDough — META-PRIMAL (N/A)

**Version**: v0.3.1 | **Tests**: 281 | **Coverage**: 95%+
**Last commit**: May 28

**Status**: Meta-primal scaffold tool. Not a runtime service. Generates
capability wire + MethodGate + BTSP for scaffolded primals. Runtime parity
N/A. Last touched May 28 — no urgency.

**Parity items**: NONE (meta-tool, not a primal service).

---

# SPRINGS

Springs inherit full primal parity. When primals ship ecosystem-level
features (registry TOML, trust exchange, coverage), springs absorb
automatically through their NUCLEUS dependency. Sprint-specific work below.

---

## wetSpring — P1 SOUTHGATE STABILIZATION

**Version**: V196 | **Wave**: 77 | **Gate**: southGate | **Tests**: 2,089
**Profile**: `domain_profile.toml` ✓
**Last commit**: Jun 4

**Status**: Largest validation surface (345 scenarios, 5,967+ checks).
guideStone L5. Forward evolution complete. Forgejo push blocked.

**P1 — southGate health**: 11/13 health → 13/13. Two primals BTSP-gated.
Investigate cold-start timing vs `SONGBIRD_PEERS` env vs OOM.

**P2 — Science gaps**: WS-9 (L3 cross-tier parity), WS-11 (variant-caller
MAPQ calibration). Not blocking mesh.

---

## neuralSpring — P1 SOUTHGATE + P2 PROFILE

**Version**: V179 | **Wave**: 76 | **Gate**: southGate | **Tests**: 930+
**Profile**: MISSING `domain_profile.toml`
**Last commit**: Jun 4

**Status**: guideStone L5. IPC-first. Deep debt (real IPC stubs) done.
southGate deployment partner with wetSpring.

**P1 — southGate mesh**: `discovery.peers` empty on cold starts. Coordinate
with wetSpring on peer seeding and BTSP timing.

**P2 — Create `domain_profile.toml`**: Pattern — copy airSpring or wetSpring
profile and adapt for neural/ML domain (inference pipeline, NestGate weight
persistence, Squirrel inference integration).

---

## healthSpring — CLEAN (P3 FRESHENING)

**Version**: V65c | **Wave**: 76 | **Gate**: ironGate (13/13) | **Tests**: 1,056
**Profile**: `domain_profile.toml` ✓
**Last commit**: Jun 3

**Status**: guideStone L5. Highest application-spring maturity. 60 scenarios,
88 capabilities. S4 BTSP auth scenario wired.

**P3 — Wave 79 absorption**: Pull latest primals. Absorb
`auth.exchange_trust` awareness + UDS-only posture. Update wave marker.
Low priority — ironGate is stable.

---

## hotSpring — P2 PROFILE

**Version**: v0.6.32 | **Session**: S284 | **Gate**: biomeGate | **Tests**: 720-1,045
**Profile**: MISSING root `domain_profile.toml` (only nested compchem profiles)
**Last commit**: Jun 1

**Status**: guideStone **L6 CERTIFIED** — ecosystem reference for sovereign
compute. Separate wave numbering (sovereign-compute track). Fleet compute
leader. Functionally most mature spring.

**P2 — Create root `domain_profile.toml`**: For ecosystem classification and
`litho emit-pseudospore`. Pattern:
```toml
[profile]
name = "hotSpring"
domain = "computational_chemistry"
gate = "biomeGate"
guidestone_level = "L6"

[capabilities]
primary = ["sovereign_compute", "cazyme_fel", "vfio_dispatch"]
consumed_primals = ["toadStool", "barraCuda", "coralReef", "bearDog", "songBird"]
```

**Open gaps**: GAP-HS-118-122 (sovereign readback, DRM, cross-gate, Blackwell
firmware, sm_120). Hardware-gated — not blocking mesh.

---

## ludoSpring — P2 PROFILE + DOC FRESHENING

**Version**: V82 | **Wave**: 76 | **Gate**: ironGate (12/12) | **Tests**: 995
**Profile**: MISSING `domain_profile.toml`
**Last commit**: Jun 3

**Status**: guideStone L4. Pure composition spring (no spring binary in
plasmidBin). All 16 gaps resolved.

**P2 — Create `domain_profile.toml`**: Pattern:
```toml
[profile]
name = "ludoSpring"
domain = "interactive_simulation"
gate = "ironGate"
guidestone_level = "L4"

[capabilities]
primary = ["game_engine", "mda_framework", "tower_atomic"]
consumed_primals = ["bearDog", "songBird", "skunkBat", "coralReef"]
```

**P2 — Doc freshening**: `CONTEXT.md` says V78/982 tests. README says
V82/995. Sync CONTEXT to match.

---

## airSpring — P2 WAVE ALIGNMENT

**Version**: v0.10.0 | **Wave**: 60 | **Gate**: eastGate (12/12) | **Tests**: 1,446
**Profile**: `domain_profile.toml` ✓
**Last commit**: May 31

**Status**: guideStone L4. 7 days behind Wave 78. Not on parity sprint.
Code quality solid (pedantic+nursery clean).

**P2 — Wave 78 alignment**:
1. Pull latest primals
2. Verify `CONSUMED_CAPABILITIES` includes trust methods
3. Update `docs/PRIMAL_GAPS.md` for upstream resolutions
4. Bump wave marker in README/CHANGELOG

**Open gaps**: AG-006 (coralReef), AG-007 (toadStool), AG-009 (petalTongue),
AG-010 (barraCuda), AG-011 (Anderson WGSL), AG-021 (Akida NPU).

**Priority**: LOW for mesh — airSpring is not mesh-critical.

---

## groundSpring — P2 WAVE ALIGNMENT

**Version**: V146 | **Wave**: 63 | **Gate**: eastGate (12/12) | **Tests**: 1,123 + 455 py
**Profile**: `domain_profile.toml` ✓
**Last commit**: May 30

**Status**: guideStone L4. 6 days behind Wave 78. Squirrel integration done.

**P2 — Wave 78 alignment**: Same as airSpring — pull primals, verify
capabilities, update wave markers.

**Priority**: LOW for mesh — groundSpring is not mesh-critical.

---

# SUMMARY — WHAT BLOCKS FORWARD PROGRESS

## P0 (blocks mesh)
- ~~**Songbird**: Wire `auth.exchange_trust` in `mesh.init` flow~~ **RESOLVED** (Wave 81)
- **VPS binary refresh**: Deploy binaries with BD-TRUST-01 + SB-TLS-01 + UDS-native
- **Songbird**: Evolve `ipc.resolve` to transport-qualified endpoints (Phase 2 transport evolution)

## P1 (blocks 3-gate mesh)
- **Songbird**: Coverage sprint 73% → 90%
- **wetSpring + neuralSpring**: southGate 11/13 → 13/13 health
- **cellMembrane**: Caddy reverse proxy wiring

## P2 (parity hygiene — parallel, non-blocking)
- **6 primals**: Create/move `config/capability_registry.toml`
- **3 springs**: Create `domain_profile.toml`
- **5 primals**: Coverage sprint to 90%
- **3 springs**: Wave marker freshening
- **ludoSpring**: CONTEXT.md stale
- **All primals**: Evolve toward transport-ignorant binaries (ecoBin compliance)

## Sequence
```
VPS binary refresh (BD-TRUST-01 + UDS-native)
  → mesh.init on golgiBody (auto trust exchange)
    → 3-gate Plasmodium collective
      → Transport evolution Phase 2 (Songbird-routed IPC)
        → Stadial entry
```
