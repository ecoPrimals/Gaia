# Wave 55+ — Springs Launch + Cross-Gate NUCLEUS Handoff

**Date**: 2026-05-26  
**From**: primalSpring (coordination)  
**To**: All spring teams, garden product teams  
**Context**: PostPrimordial complete. Waves 53–54 clear primal mountains and
stabilize gates. This handoff previews Wave 55+ spring launch work so teams
can prepare. Glacial shift wave plan at `wateringHole/GLACIAL_SHIFT_WAVE_PLAN.md`.

---

## Prerequisites (Waves 53–54)

Before spring launch:
- All 4 gates at 13/13 primals (southGate + biomeGate fixes)
- `s_covalent_mesh` PASS on all 4 gates (Songbird mesh validated)
- cellMembrane VPS Nest expansion complete

---

## Per-Spring Guidance

### primalSpring (COORDINATION — owns cross-gate validation)

v0.9.30, 92 experiments, 175/193 certify. Zero debt.

- **Cross-gate capability.call smoke tests**: from each gate, call capabilities
  on every other gate via Songbird braid relay
- **`s_covalent_mesh` scenario**: run against all 4 gates as the mesh
  validation milestone
- **Cephalization validation**: exp113 results feed back to biomeOS
- **K-Derm boundary scenario**: `s_kderm_boundary` after consuming
  `cellmembrane-types`
- **Proto-nucleate verification**: validate parity on all deployed graphs

### wetSpring (southGate — pending gate stabilization)

- **PG-02**: Provenance trio live roundtrip verification on stable southGate
  (rhizoCrypt → sweetGrass → loamSpine cycle)
- **PG-04**: NestGate storage roundtrip verification
- Chemistry entity types feed sweetGrass v0.8.0

### neuralSpring (southGate — pending gate stabilization)

- **loamSpine Tokio double-runtime crash**: investigate and fix — blocks full
  Nest Atomic on southGate
- **Squirrel provider registration**: wire Squirrel AI into composition for
  inference routing
- **toadStool `health.liveness`**: verify -32601 error resolved after
  southGate redeploy
- ML surrogate validation: additive (lithoSpore dependency), not blocking

### hotSpring (biomeGate — pending federation fix)

- **BiomeGate federation**: after gate operator restarts Songbird (Wave 54),
  verify hotSpring's NUCLEUS composition is fully healthy
- **Ionic GPU lease prototype**: GAP-HS-005 — BearDog `crypto.sign_contract`
  for cross-family GPU scheduling. Begin prototype once BearDog confirms
  contract signing capability.
- Covalent HPC confirmed (Wave 50); focus is cross-gate interaction

### healthSpring (ironGate — already operational)

- **BTSP probe pattern**: implement `btsp.capabilities` query before
  attempting BTSP negotiation. Currently `FAMILY_SEED` presence causes
  unconditional negotiation which fails against primals that don't support it.
- **Ionic bridge**: dual-tower enclave pattern is live; cross-tower ionic
  bridge validation next
- ironGate deployment is stable; no gate dependency

### ludoSpring (ironGate — already operational)

- **6 game.* methods for esotericWebb**: `game.push_scene`, `game.state`,
  `game.inventory`, `game.dialogue`, `game.combat`, `game.save` — wire these
  for the gen4 CRPG product
- **Notebook gap**: ludoSpring has 0 Jupyter notebooks vs other springs
  averaging 20+. Not blocking but noted for parity.
- ironGate deployment is stable; no gate dependency

### groundSpring (eastGate — already operational)

- **Squirrel composition integration**: additive. Wire Squirrel AI into
  composition context for geology/measurement workflows.
- eastGate deployment is reference; no gate dependency
- Low urgency — continue at current pace

### airSpring (eastGate — already operational)

- **AG-006**: coralReef shader compilation for ecology visualization
  (barraCuda → coralReef pipeline)
- **AG-009**: petalTongue direct IPC (bypass Neural API for latency-sensitive
  rendering)
- **AG-021**: Akida NPU driver integration (hardware-specific, deferred)
- eastGate deployment is reference; no gate dependency

---

## Per-Primal Guidance (Wave 55 items)

### songbird

- Mesh validated across all 4 gates (prerequisite from Wave 53–54)
- Braid relay for cross-gate `capability.call` — primalSpring drives testing
- Federation should be stable; Songbird's role is passive relay at this point

### bearDog

- `crypto.sign_contract` capability for hotSpring ionic GPU lease (GAP-HS-005)
- After TCP drop (Wave 54): validate crypto accessibility from remote gates
  via Songbird relay
- TLS 7-day parity: confirm with projectNUCLEUS H2-12

### biomeOS

- Neural API routing for cross-gate capability discovery
- Cephalization: if exp113 validated (Wave 54), begin implementing
  primal-scoped socket discovery in Neural API
- Plasmodium agents over mesh (SSH deprecated) — background item

### squirrel

- Live provider E2E in compositions: neuralSpring + groundSpring integration
- NestGate content-curation integration (blocked on NestGate `storage.*` API)

### petalTongue

- Downstream dashboards: lithoSpore lab visualization, wetSpring chemistry views
- AG-009 (airSpring direct IPC) requires petalTongue cooperation

### Provenance trio (rhizoCrypt, loamSpine, sweetGrass)

- **E2E live validation**: wetSpring drives PG-02/PG-04 across the trio
- sweetGrass v0.8.0: live signing/session/anchoring providers
- loamSpine v0.10.0: signing middleware on RPC layer
- All three should be live on VPS (cellMembrane Nest expansion, Wave 54)

### Compute trio (barraCuda, coralReef, toadStool)

- **Live CI pipeline**: barraCuda → coralReef compile→dispatch on real silicon
- airSpring AG-006 is the first spring consumer of the compile pipeline
- toadStool multi-GPU OOM auto-migration: background enhancement

### skunkBat, sourDough, bingoCube, NestGate

- No spring-facing Wave 55 items
- Continue normal evolution

---

## Per-Garden Guidance

### esotericWebb (ACTIVE — gen4 product)

V10, 357 tests, 91% coverage. First gen4 creative product (CRPG engine).

- **ludoSpring integration**: 6 `game.*` methods are the primary dependency
- **BearDog crypto bridge** (GAP-015): resolves after BearDog TCP drop prototype
- **Deploy-graph format**: align with primalSpring canonical format
- **Provenance trio E2E** (GAP-008): validate with wetSpring once southGate stable
- 12 open evolution gaps — prioritize ludoSpring methods and provenance

### lithoSpore (PASSIVE — field deployment benefits)

v0.1.0, 7/7 modules PASS. 4 USBs at Barrick Lab.

- **Tier 3 provenance**: benefits from VPS Nest expansion (live NUCLEUS at runtime)
- **Songbird TURN client**: blocked upstream on Songbird — no action for lithoSpore
- **petalTongue dashboards**: lab visualization integration is additive
- **neuralSpring ML surrogates**: additive, not blocking
- **BLAKE3 hash backfill** (FN-1): projectFOUNDATION drives this

### projectNUCLEUS (COORDINATION — gate orchestration)

- **Cross-gate smoke tests**: assist primalSpring with capability.call validation
- **Horizon 2 cutovers**: TLS parity + DNS NS cutover align with cellMembrane Wave 54
- **Horizon 3**: FlockGate cross-WAN (H3-11) — deploy after mesh is validated
- **Phase 2**: ionic compute sharing progresses with hotSpring GPU lease

### projectFOUNDATION (BACKGROUND — validation continues)

- **BLAKE3 backfill**: 155 sources as data becomes available
- **Thread validation**: Threads 1, 4, 5, 10 partial — incremental
- **Composition gaps**: feed back to springs as encountered
- No spring-launch dependencies

### cellMembrane (MEMBRANE INTERACTION)

After Wave 54 blockers cleared:
- **Channel proteins live**: K-Derm channels (TLS, NAT, content, auth) as
  formal NUCLEUS boundary
- **S1 TLS shadow cutover**: Cloudflare → sovereign TLS via Caddy
- **Forgejo Actions**: shadow CI on ironGate, then invert to Forgejo-primary
- Springs don't act on membrane items directly — cellMembrane handles the
  boundary. Springs should be aware that cross-gate traffic will eventually
  route through formal K-Derm channel proteins.

### blueFish (NO ACTION)

Placeholder. Product not started. Foundation defines audience and thread
mapping (Thread 4, wetSpring Track 2). Implementation TBD post-glacial.

---

## Cross-Gate Capability Routing (all springs)

Once gates are stable, primalSpring runs cross-gate smoke tests:

1. From each gate, `capability.call` to capabilities on every other gate
   via Songbird braid relay
2. Verify provenance trio roundtrips across gates
3. Validate ionic cross-family patterns

Springs should be prepared to run their validation scenarios against
remote gates (set `PRIMALSPRING_HOST` + `PRIMALSPRING_TCP_TIER5=1`
for TCP-based cross-gate probing).

---

## Timeline

Wave 55 begins after gates are stable (all 4 at 13/13, mesh validated).
Spring deployment is incremental — already-operational springs continue;
pending springs deploy as their gates come online.

No ack needed for this preview handoff. Per-spring action handoffs follow
when Wave 54 completes.
