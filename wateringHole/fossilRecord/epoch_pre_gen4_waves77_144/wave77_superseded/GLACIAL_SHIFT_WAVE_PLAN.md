# Glacial Shift Wave Plan — PostPrimordial to Sovereignty

**Status**: Active roadmap  
**Phase**: PostPrimordial (Wave 65) → Glacial Shift  
**Last updated**: 2026-05-31  
**Owner**: primalSpring (coordination); cellMembrane (deployment); primal teams (mountains)

---

## Current Position

Interstadial exit achieved. 13/13 NUCLEUS primals shipped via plasmidBin with
checksums + provenance-elevated fingerprints (Wave 54). eastGate is the reference
deployment (13/13, 19/19 sockets, doctor 35/35 pass). 4 gates operational
(eastGate, ironGate, southGate, biomeGate) with varying completeness. 8/8 springs
at zero code debt, primordial patterns extinct, covalent HPC confirmed.

Three phases below are ordered by dependency: mountains feed deployment,
deployment feeds springs, springs feed cross-gate interaction.

**Wave 54 provenance elevation completed**: `provenance.toml` (Layer 2 composite
fingerprint + sweetGrass braids) shipped in plasmidBin. `plasmidbin verify-provenance`
subcommand added. primalSpring consumer tooling rewired. VPS NUCLEUS route: zero
mountain debt blocking, `deploy_membrane.sh --composition nest` ready.

**Wave 61 sovereign shadow functions completed**: `membrane-shadow` Rust crate
replaces bash `membrane.sh` for agentic VPS control. Typed APIs for Forgejo repo/mirror
management, systemd service control, gate info/pull/check. Capability registries aligned:
nestGate `content.repo.*`/`content.mirror.*`, bearDog `auth.token.*`, biomeOS
`gate.service.*` + shadow translation entries. Forgejo pull mirrors operational for all
38 repos. Temporal sync spec published (`primalSpring/specs/WATERFALL_TEMPORAL_SYNC.md`).
Ecosystem standardization audit completed — stale remotes, duplicate repos, branch
naming all resolved. 13/14 upstream Neural API methods shipped.

---

## Phase 1 — Wave 53: Primal Mountains (RESOLVED)

### Resolution status (reviewed May 26, 2026)

| Item | Status | Detail |
|------|--------|--------|
| Songbird stale socket cleanup | **DONE** | `unlink()` before `bind()` hardened at 2 bind sites (connection.rs, unix_listener.rs). Ignores `NotFound`. |
| Songbird BTSP stress tests | **DONE** | 3 new tests: 100-request sequential, varying payload (1B–4KB), 10-client concurrent sessions. |
| Songbird coverage 73→90% | **OPEN** | Still at 73.41%. I/O-heavy + integration paths remain. Not blocking deployment. |
| Songbird Tor onion | **DEFERRED** | Reclassified from BLOCKED to DEFERRED. Not a glacial-shift blocker. |
| BearDog TCP opt-in | **DONE** | TCP now opt-in only (`--port`/`--listen`/`BEARDOG_TCP_IPC_PORT`). UDS-only by default. All 127 methods available via UDS. |
| SkunkBat seed_fingerprint | **DONE** | BLAKE3 fingerprint backfilled in plasmidBin manifest.toml. |
| SourDough manifest drift | **DONE** | plasmidBin manifest bumped 0.3.0→0.3.1. |
| LoamSpine storage backends | **DONE** | Documented as roadmap (not blocker) in WHATS_NEXT.md. Wave 53 ack filed. Zero mountain debt. |
| CoralReef depth/array/cube | **DONE** | Depth texture comparison PTX, array/cube sampling, vector math. +18 tests (3,220 total). |
| BarraCuda coverage | **DONE** | +24 handler-level tests (4,501+ total). All IPC handler gaps closed. |
| ToadStool ipc.register | **DONE** | Aligned from stale 2-cap set to full 9-cap Node Atomic set. S276 deep debt evolution: zero production panics, sovereign split, memmap2→rustix. |
| NestGate version unify | **DONE** | Unified to 0.5.0 across all 21 workspace crates + plasmidBin manifest (Session 77). Coverage 83.61% (Session 78); 90% target ongoing. |
| SouthGate crash investigation | **OPEN** | Ops/deployment follow-up — Songbird socket hardening shipped but southGate redeploy not yet done. |

### Summary

12/13 Wave 53 items resolved. 1 remaining item (SouthGate ops redeploy) carries into
Wave 54. NestGate unified to v0.5.0 (Session 77). Songbird coverage (73→90%) is
incremental, not blocking. All mountain code debt is clear — remaining work is
ops/deployment.

---

## Phase 2 — Wave 54: Deployment + cellMembrane

Stabilize all gates and hand off deployment infrastructure to cellMembrane.

Wave 53 resolved most mountain code debt. Wave 54 focuses on ops/deployment
and the glacial shift infrastructure blockers.

### Primal prep (DONE — Wave 53 + 54-prep)

| Item | Status | Detail |
|------|--------|--------|
| BearDog TCP opt-in | **DONE** | UDS-only by default. TCP requires `--port`/`BEARDOG_TCP_IPC_PORT`. All 127 methods via UDS validated. |
| Songbird socket hardening | **DONE** | `unlink()` before `bind()` at all sites. BTSP 3-test stress suite. |
| ToadStool ipc.register | **DONE** | 9-cap Node Atomic set. S276 deep debt: zero panics, sovereign split. |
| BarraCuda coverage | **DONE** | +24 handler tests, all IPC gaps closed. |
| CoralReef ptx_emit | **DONE** | Depth textures, array/cube, vector math. 3,220 tests. |
| LoamSpine ack | **DONE** | Zero mountain debt. PostgreSQL/RocksDB documented as roadmap. |
| primalSpring scenarios | **DONE** | 3 new: `s_cephalization`, `s_tower_cns`, `s_kderm_boundary`. 56 total. |

### Gate stabilization

| Item | Owner | Detail |
|------|-------|--------|
| SouthGate redeploy | plasmidBin + southGate operator | Fresh NUCLEUS with Songbird socket hardening: `plasmidbin fetch --all --force && plasmidbin launch`. Target: 13/13 primals. Songbird socket cleanup is now hardened (Wave 53). Verify `SONGBIRD_PEERS=192.168.1.144:7700`. |
| BiomeGate federation | biomeGate operator | Restart Songbird with `SONGBIRD_FEDERATION_PORT=7700` + `SONGBIRD_PEERS`. Push to 13/13. |
| Live covalent mesh | primalSpring | Run `s_covalent_mesh` against all 4 gates after redeploy. |
| NestGate version unify | NestGate team | **DONE** — v0.5.0 across 21 workspace crates (Session 77). Coverage at 83.61%, pushing toward 90%. Ready for VPS deploy. |

### cellMembrane handoffs

| Item | Owner | Detail |
|------|-------|--------|
| 2nd CI runner on eastGate | cellMembrane | Eliminate ironGate runner SPOF. |
| VPS Nest expansion | cellMembrane | Deploy rhizoCrypt, loamSpine, sweetGrass, NestGate on VPS. Glacial blocker 1. loamSpine confirmed mountain-clean (90.92% coverage, 1,528 tests). |
| Sovereign DNS | cellMembrane | Deploy knot-dns on VPS (Channel 1). Glacial blocker 2. |
| K-Derm wire contract | cellMembrane → wateringHole | Publish `membrane.toml` schema, layer placement, `BoundaryPolicy` set. primalSpring `s_kderm_boundary` scenario ready to consume. |
| Sovereign shadow functions | cellMembrane | **DONE** (Wave 62) — `membrane-shadow` Rust crate: agentic VPS control + temporal sync + manifest reader + gate identity. Deep debt sprint (security, hardcoding, error handling). |
| Forgejo bidirectional repos | cellMembrane | **DONE** (Wave 62) — 5 repos bidirectional (biomeOS, coralReef, sweetGrass, squirrel, wateringHole). 33 remaining as pull mirrors. |
| waterFall temporal sync | cellMembrane | **DONE** (Wave 62→66) — `membrane temporal.cascade` (pure Rust). Multi-remote DAG sync: fetch all, measure position, pull leader, push followers. Bash `cascade-pull.sh` fossilized. |
| K-Derm diderm deployment | cellMembrane | **DONE** (Wave 63) — Three-node VPS envelope: golgiBody (inner, Forgejo), peptidoglycan (structural, builds), golgiBody-ext (outer, sporePrint live). $48/mo total. |
| GATE_SETUP_STANDARD | wateringHole | **DONE** (Wave 63) — Standardized gate setup/sync/resync for physical gates and VPS proto-fieldMouse deployments. |
| waterFall Phase 4 inversion | cellMembrane + wateringHole | **DONE** (Wave 63+) — Forgejo-primary push model. `push_target = "forgejo"` in manifest; push mirror API in membrane-shadow; cascade graphs defined. K-Derm diderm relay chain wired with proper bond degradation. |
| K-Derm bonding enforcement | cellMembrane + wateringHole | **DONE** (Wave 63+) — Diderm relay chain: `pepti-sync-relay.sh` on peptidoglycan mediates metallic→ionic; `ext-github-push.sh` on golgiBody-ext ships to GitHub (weak). GitHub SSH keys moved to outer membrane (trans face). `topology.roles` in manifest. Bonding violation resolved: covalent→metallic→ionic→weak. |
| Transport: nanowire→quorum Phase 1 | cellMembrane | **NEXT** — Replace SSH-triggered relay with timer-based `potential.sense` on peptidoglycan + golgiBody-ext. Nodes sense and respond autonomously. Nanowire SSH retained for metallic/covalent ops. See `gen5/TRANSPORT_EVOLUTION_NANOWIRE_TO_QUORUM.md`. |
| Transport: nanowire→quorum Phase 2 | cellMembrane + songbird | **FUTURE** — Songbird `mesh.publish` carries impulse notifications. Nodes subscribe to K-Derm-layer-relevant channels. Relay becomes multicast, not point-to-point SSH. |
| Transport: nanowire→quorum Phase 3 | cellMembrane + songbird + biomeOS | **FUTURE** — Capability-routed quorum. Nodes register K-Derm roles via songbird capabilities. Coordination routing is topology-discoverable, not hardcoded. |
| Multi-vendor peptidoglycan | cellMembrane | **FUTURE** — Additional VPS node(s) on different providers (Hetzner/Vultr) as peptidoglycan layer redundancy. Validates quorum sensing across providers. ABG compute workload submission interface. |
| Air-gap validation loop | biomeGate | **ACTIVE** — biomeGate's async hardware cadence validates temporal sync tolerance for delayed pushes. Pattern maps to air-gapped/intermittent gates post-stadial. |

### Cephalization + Tower CNS (primalSpring-validated)

| Item | Owner | Status | Detail |
|------|-------|--------|--------|
| BearDog TCP drop | BearDog + primalSpring | **VALIDATED** | BearDog UDS-only running on eastGate (nucleus01, no `--port`). All 5 domain sockets confirmed. primalSpring `s_tower_cns` scenario passes. |
| Socket namespacing | primalSpring + biomeOS | **SCENARIO READY** | `s_cephalization` scenario validates ownership map, orphan detection. Phase A (beardog/5 + barracuda/5) ready for live prototype after gate stabilization. |
| K-Derm boundary | primalSpring | **SCENARIO READY** | `s_kderm_boundary` validates all 13 primals placed in K-Derm layers. Zero boundary violations. Pending cellMembrane `membrane.toml` for channel protein integration. |

---

## Phase 3 — Wave 55+: Springs Launch + Cross-Gate NUCLEUS

Mountains clean, gates stable — springs connect and interact across the mesh.

### Spring proto-nucleate deployment

All 7 delta springs deploy `proto_nucleate_template.toml` on their assigned gates:

| Gate | Springs | Status |
|------|---------|--------|
| eastGate | airSpring, groundSpring | Already operational |
| ironGate | ludoSpring, healthSpring | Already operational |
| southGate | wetSpring, neuralSpring | Pending gate stabilization |
| biomeGate | hotSpring | Pending federation fix |

### Cross-gate capability routing

| Item | Owner | Detail |
|------|-------|--------|
| capability.call smoke tests | primalSpring | From each gate, call capabilities on every other gate via Songbird braid relay. |
| Provenance trio roundtrips | wetSpring | PG-02 (provenance trio live) and PG-04 (NestGate storage) verification. |
| Ionic cross-family GPU lease | hotSpring + BearDog | GAP-HS-005: `crypto.sign_contract` for cross-family GPU scheduling. |

### pseudoSpore Ecosystem — Delta Spring Releases (Wave 55+)

hotSpring and lithoSpore completed the pseudoSpore Ecosystem Evolution (May 27):
`pseudospore-core` crate extracted, domain-agnostic `litho emit-pseudospore`, unified
`liveSpore.json` schema, `SPORE_OWNERSHIP_MATRIX.md` published, biomeOS `nucleus ingest`
scaffolded. The CompChem pseudoSpore is at v1.6.1. **lithoSpore NC-1.3 COMPLETE** —
`ltee-cli` and `litho-core` consume `pseudospore-core`.

**Goal**: Every delta spring produces a pseudoSpore release artifact on sporePrint.

| Spring | Domain | pseudoSpore Target | Status |
|--------|--------|-------------------|--------|
| hotSpring | CompChem | `pseudoSpore_hotSpring-CompChem-GuideStone_v1.6.1` | **DONE** — reference implementation |
| wetSpring | Biology | Ferment transcript spore (Barrick 2009 SEALED, Tenaillon 2016 in-flight) | READY — data exists, needs `domain_profile.toml` + `litho emit-pseudospore` |
| neuralSpring | ML/Structure | Inference benchmark spore (model weights + eval metrics) | SCAFFOLD — needs domain_profile |
| healthSpring | Clinical/PK-PD | Drug interaction model spore (PBPK curves + PD responses) | SCAFFOLD — needs domain_profile |
| ludoSpring | Game Science | Game telemetry spore (Fitts, WFC, engagement models) | SCAFFOLD — needs domain_profile |
| groundSpring | Measurement | Uncertainty quantification spore (calibration datasets) | SCAFFOLD — needs domain_profile |
| airSpring | Agriculture | Soil dynamics spore (ET₀, diversity indices) | SCAFFOLD — needs domain_profile |

**Per-spring steps** (each spring owns):
1. Write `domain_profile.toml` describing their science modules
2. Run `litho emit-pseudospore --spring <name> --domain-profile ./domain_profile.toml`
3. Validate with `litho audit`
4. Promote to sporePrint via `litho promote` or NestGate `content.put`

**primalSpring validation** (coordination):
- `exp115_nest_ingest_pseudospore`: Structural checks for spore gateway
- `s_nest_atomic` Phase 4: Spore ingest/verify round-trip
- `NUCLEUS_VALIDATION_MATRIX` columns U/V/W: Live gateway experiments

### Membrane interaction

| Item | Owner | Detail |
|------|-------|--------|
| Channel proteins live | cellMembrane | K-Derm channels (TLS, NAT, content, auth) as formal NUCLEUS boundary. |
| S1 TLS shadow cutover | cellMembrane | Cloudflare → sovereign TLS via Caddy. Key sovereignty milestone. |
| Forgejo Actions | cellMembrane | Deploy Forgejo on ironGate as shadow CI, then invert (Forgejo-primary). |

### Per-spring next steps

| Spring | Key next step |
|--------|--------------|
| wetSpring | PG-02/PG-04 live verification on stable southGate; **pseudoSpore: ferment transcript spore** |
| neuralSpring | Resolve loamSpine Tokio double-runtime crash; Squirrel provider registration; **pseudoSpore: inference benchmark** |
| hotSpring | BiomeGate federation fix; ionic GPU lease prototype; **pseudoSpore: DONE (v1.6.1)** |
| healthSpring | BTSP `btsp.capabilities` probe pattern; **pseudoSpore: clinical model spore** |
| ludoSpring | 6 game.* methods for esotericWebb; **pseudoSpore: game telemetry spore** |
| groundSpring | Squirrel composition integration; **pseudoSpore: uncertainty quantification spore** |
| airSpring | AG-006 coralReef compile; **pseudoSpore: soil dynamics spore** |

---

## Glacial Shift Exit Criteria

| Criterion | Current (Wave 65) | Target |
|-----------|----------------------|--------|
| Shadow cutover S1–S4 | **3/4** (S1 TLS 7-day gate running ~June 7, S4 blocked on ironGate) | 4/4 |
| Mountain code debt | **13/13 resolved** | 13/13 |
| Multi-gate mesh validated | **5 gates operational** (east/iron/south/biome/flock), mesh.init wired | `s_covalent_mesh` PASS on 5+ gates |
| VPS Nest expansion | **DEPLOYED** (since May 28) — rhizoCrypt + loamSpine + sweetGrass | Operational |
| Sovereign DNS | **OPERATIONAL** — ns1 (golgiBody) + ns2 (golgiBody-ext), DNSSEC, zone transfers | Registrar cutover |
| CI on inner membrane | 1 runner (SPOF) | 2+ runners, Forgejo shadow |
| Cloudflare removed | S1 shadowing (Caddy LIVE, Cloudflare INACTIVE) | DNS cutover complete |
| Primals 90%+ coverage | ~10/13 (songbird 73%, coralReef/barraCuda incremental) | 13/13 |
| BearDog TCP drop | **VALIDATED** — UDS-only on eastGate | All gates UDS-only |
| K-Derm boundary scenarios | **3 scenarios PASS** (57 total) | + channel protein live validation |
| pseudoSpore delta coverage | **2/7** (hotSpring CompChem v1.6.1, healthSpring PROFILE_READY) | 7/7 springs emit domain spore |
| primalSpring lib tests | **838 pass** (807 lib + 10 integration + 4 binary + 17 doc) | All pass |
| K-Derm relay chain | **LIVE** (nanowire SSH diderm relay + Rust temporal.cascade) | Phase 1 quorum (timer-based sensing) |
| Gate validation coverage | **3/5** (flockGate WAN, biomeGate temporal, ironGate LAN pending) | All gates validated + air-gap |
| membrane-shadow Rust | **12 modules** (was bash scripts) — 0 critical bash in pipeline | Feature-complete for Wave 65 |
| Manifest-driven validation | **LIVE** — gates discovered from manifest, not hardcoded | Auto-validates new gates |
