# Wave 150u — Team Evolution Blurbs

**Date**: Jul 21, 2026 | **Wave**: 150u | **From**: eastGate overwatch
**Purpose**: Structured evolution assignments for all teams. Each section is a
self-contained blurb — paste the relevant section when spinning up a team session.

---

## 1. bearDog team (southGate) — HSM Android Keystore + grapheneGate Testing

> **bearDog** — Wave 150u evolution assignment.
>
> **Context**: You shipped the `CredentialStore` trait with `InMemoryCredentialStore`
> and `FileVaultCredentialStore` backends (Wave 150t). The `secrets.*` JSON-RPC
> interface is live. The squirrel handoff is issued. That's excellent work.
>
> **Assignment**: Implement the **Android Keystore backend** for grapheneGate.
> grapheneGate is a Pixel 8a (Tensor G3, 8GB) running Tower Atomic (bearDog +
> songBird + skunkBat). It needs a `CredentialStoreBackend::AndroidKeystore`
> variant that delegates to Android's hardware-backed keystore via JNI or the
> NDK keystore API. This is the HSM abstraction the ecosystem needs for mobile
> trust anchors.
>
> **Deliverables**:
> 1. `AndroidKeystoreCredentialStore` implementing `CredentialStore` trait
> 2. `CredentialStoreBackend::AndroidKeystore` variant in enum dispatch
> 3. Feature-gated behind `#[cfg(target_os = "android")]` with trait fallback
>    (Silicon Atheism pattern — same trait, platform-specific backend)
> 4. Integration test: store/retrieve/list/delete cycle on grapheneGate hardware
> 5. Handoff to eastGate overwatch with test results from Pixel 8a
>
> **Testing plan**: eastGate will provide grapheneGate (Pixel 8a) for hands-on
> testing. Deploy bearDog with Android Keystore backend, run the 5-point
> verification checklist from the squirrel handoff, confirm keys survive app
> restart and are hardware-backed (TEE/StrongBox where available).
>
> **Code pointers**:
> - Trait: `crates/beardog-traits/src/unified/storage.rs`
> - Existing backends: `crates/beardog-tunnel/src/credential_store/`
> - Enum dispatch: `crates/beardog-tunnel/src/credential_store/backend.rs`
>
> **Standards**: `foundations/SECRETS_AND_SEEDS_STANDARD.md`,
> `protocols/BTSP_PROTOCOL_STANDARD.md`

---

## 2. squirrel team (eastGate) — CredentialStore Integration

> **squirrel** — Wave 150u evolution assignment.
>
> **Context**: bearDog has shipped the `CredentialStore` trait and `secrets.*`
> JSON-RPC interface. A detailed handoff is at
> `primals/bearDog/infra/wateringHole/handoffs/SQUIRREL_CREDENTIAL_STORE_HANDOFF.md`.
>
> **Assignment**: Integrate squirrel's `SecurityProvider` with bearDog's
> `secrets.*` JSON-RPC. Route AI provider API keys through `secrets.retrieve`
> instead of raw env vars. This eliminates plaintext secrets from environment
> and makes credential storage platform-agnostic (FileVault on desktop,
> Android Keystore on grapheneGate, in-memory for tests).
>
> **Deliverables**:
> 1. `CredentialStorage::SecurityProvider` delegates to `secrets.*` over IPC
> 2. AI key retrieval via `secrets.retrieve` (not `std::env::var`)
> 3. Graceful fallback to env vars when bearDog is not running
> 4. 5-point verification checklist (from handoff) passing
> 5. Report back on handoff doc with results
>
> **Wire contract**: `secrets.store({name, value})`, `secrets.retrieve({name})`,
> `secrets.list({})`, `secrets.delete({name})` — see handoff for full JSON-RPC.

---

## 3. Tower Atomic Parity — Multi-Gate Benchmark (primalSpring + ironGate + VPS)

> **Tower Atomic Parity Benchmark** — Wave 150u joint assignment across 3 gates.
>
> **Context**: songBird has published the Tower Atomic Convergence Brief at
> `primals/songBird/infra/wateringHole/TOWER_ATOMIC_CONVERGENCE.md`. All Tower
> components are live independently. `mesh.enroll` with BTSP-HMAC is live.
> The parity benchmark spec is defined but the harness is not implemented.
>
> **Test topology**: WAN-first. ironGate is temporarily down, so we start with
> the WAN path (eastGate ↔ flockGate ↔ golgiBody) which traverses the full
> membrane stack. LAN testing follows when ironGate returns. This is the
> correct order anyway — LAN and WAN are simply different membrane layers.
> If Tower can cross the outer membrane cleanly, the inner membrane (LAN) is
> a subset of the same traversal with fewer hops.
>
> ```
> Phase 1 — WAN (now):
>
> eastGate (10.13.37.5) ──── WG mesh ──── golgiBody (10.13.37.1, VPS)
>       │                                        │
>       └──── WG mesh ──── flockGate (10.13.37.6) ┘
>
> Benchmark paths:
>   A) eastGate  ↔ flockGate  (WAN, cross-household)
>   B) eastGate  ↔ golgiBody  (WAN, through VPS)
>   C) flockGate ↔ golgiBody  (WAN, co-located outer membrane)
>
> Phase 2 — LAN (when ironGate returns):
>
> eastGate (10.13.37.5) ──── LAN ──── ironGate (10.13.37.7)
>
> Benchmark paths:
>   D) eastGate ↔ ironGate (LAN, same subnet — cytoplasm-to-cytoplasm)
> ```
>
> **Membrane mapping**: WAN paths cross outer membrane → peptidoglycan → inner
> membrane (the full diderm traversal). LAN paths stay within the plasma
> membrane (cytoplasm-to-cytoplasm, covalent bond). Tower must work at every
> layer — proving WAN first proves the harder case.
>
> ### primalSpring team (eastGate) — Orchestration + Atomic Testing
>
> primalSpring owns all composition validation. The Tower Atomic parity test
> is a composition test — bearDog + songBird + skunkBat coordinating.
>
> **Assignment**:
> 1. Create a `tower_atomic_parity` primalSpring scenario that exercises
>    Tower Atomic composition: enrollment, encrypted transport, cross-gate
>    `capability.call`, and drawbridge routing
> 2. Phase 1 (WAN): orchestrate benchmark runs against flockGate and golgiBody
> 3. Phase 2 (LAN): orchestrate benchmark runs against ironGate when it returns
> 4. Validate Tower vs WireGuard results against parity targets
> 5. Report pass/fail per metric per membrane layer
>
> **Parity targets**:
>
> | Metric | WG Baseline | Tower Target | Phase | Path |
> |--------|-------------|--------------|-------|------|
> | Throughput | ~100 Mbps (WAN est.) | ≥80 Mbps | **1 (WAN)** | A,B |
> | Latency | ~20ms (WAN est.) | ≤40ms | **1 (WAN)** | A,B |
> | Connection setup | ~50ms | ≤500ms | **1 (WAN)** | A,B,C |
> | Reconnect | instant | ≤2s | **1 (WAN)** | A |
> | CPU (idle) | ~0% | ≤1% | **1 (WAN)** | A |
> | Throughput | ~900 Mbps (LAN) | ≥720 Mbps | 2 (LAN) | D |
> | Latency | ~0.3ms (LAN) | ≤0.6ms | 2 (LAN) | D |
> | CPU (saturated) | ~5% | ≤20% | 2 (LAN) | D |
>
> ### flockGate team — WAN Benchmark Peer
>
> **Assignment**:
> 1. Ensure Tower Atomic stack is running on flockGate (bearDog + songBird +
>    skunkBat — already running for esotericWebb)
> 2. Accept benchmark connections from eastGate's primalSpring harness
> 3. Run `iperf3` server for WireGuard baseline measurement
> 4. Verify `mesh.enroll` works from eastGate → flockGate via Tower
> 5. Report flockGate-side metrics (CPU, memory, connection stability)
>
> ### golgiBody VPS team — TURN Relay Deployment + WAN Benchmark
>
> **Assignment**:
> 1. Deploy `songbird relay` on golgiBody VPS (systemd unit is ready,
>    needs deployment — see convergence brief §Deployment/Ops)
> 2. Set `SONGBIRD_DRAWBRIDGE_ADDR=0.0.0.0:7780` for cross-WG access
> 3. Accept benchmark connections from eastGate for WAN path (B)
> 4. Verify TURN relay handles NAT traversal for flockGate↔golgiBody path (C)
> 5. Report VPS-side resource usage during benchmark
>
> ### ironGate team — LAN Benchmark Peer (Phase 2, when hardware returns)
>
> **Assignment** (deferred):
> 1. Ensure Tower Atomic stack is running on ironGate
> 2. Accept LAN benchmark connections from eastGate (path D)
> 3. Run `iperf3` server for LAN WireGuard baseline
> 4. Report ironGate-side metrics
>
> ### Upstream primal needs (bearDog, skunkBat — existing assignments)
>
> bearDog (assignment #1 above) and skunkBat (eastGate) still need:
> - bearDog: `enrollment.verify` endpoint (P1), session key export (P2)
> - skunkBat: bond negotiation protocol (P2), version exchange (P2)
> These are prerequisites — primalSpring scenarios should stub/mock initially,
> then validate with real endpoints as they ship.
>
> **4-phase timeline**: Benchmark → Shadow (Tower alongside WG) → Cutover → WG removed

---

## 4. sporeGate team — Deploy petalTongue v1.7+

> **sporeGate** — Wave 150u ops assignment.
>
> **Context**: petalTongue v1.7.0 is built and in the depot. flockGate is still
> running v1.6.6. v1.7+ activates scene graph rendering and the WASM WebGL
> compiler that esotericWebb V22 and bingoCube both depend on.
>
> **Assignment**: Deploy petalTongue v1.7+ to flockGate (and sporeGate if running).
>
> **Deliverables**:
> 1. `plasmid.fetch` petalTongue v1.7.0 on flockGate
> 2. Restart petalTongue service with v1.7+ binary
> 3. Verify `visualization.render.scene` accepts `game_scene` SceneGraph
> 4. Verify `pt.render_webgl` on WebSocket bridge responds
> 5. Confirm `webb.primals.eco` still returns 200 after deploy
>
> **Unblocks**: esotericWebb V22 scene graph (no code changes needed),
> bingoCube interactive widget, sporePrint primal pipeline

---

## 5. sporePrint team (flockGate) — Lansing Scuffle Pages + Primal Pipeline

> **sporePrint** — Wave 150u evolution assignment.
>
> **Context**: The Lansing Scuffle blurb was issued (Wave 150p) — 4 new pages
> (consulting, companies, scuffle, thermal) + 4 updates. footPrint has
> committed the Lansing Scuffle GeoJSON project file. The petalTongue WASM
> WebGL pipeline is shipped (Wave 150r).
>
> **Assignment (NOW)**: Create the 4 Lansing Scuffle public pages on sporePrint.
> See `handoffs/SPOREPRINT_LANSING_SCUFFLE_BLURB.md` for full content spec.
>
> **Assignment (NEAR TERM)**: Begin designing the **sporePrint primal pipeline** —
> the Zola replacement architecture:
> - petalTongue renders content (WASM WebGL for interactive, SVG for static)
> - nestGate CAS stores content-addressed pages
> - cellMembrane serves via Caddy
> - Result: sovereign static site generation, no Zola dependency
>
> **Standards**: `compositions/COMPOSITION_ROUTING_STANDARD.md`,
> `foundations/DIDERM_DOMAIN_ARCHITECTURE.md` (sovereignty evolution roadmap)

---

## 6. cellMembrane team (ironGate) — Unwrap Audit

> **cellMembrane** — Wave 150u evolution assignment.
>
> **Context**: cellMembrane has 456 production `.unwrap()` calls identified in
> the Wave 150o ecosystem audit. Other primals (nestGate, loamSpine, esotericWebb)
> have confirmed 0 production unwraps — their counts were false positives from
> inline `#[cfg(test)]` modules.
>
> **Assignment**: Audit and eliminate production `.unwrap()` calls.
>
> **Approach** (from nestGate and toadStool patterns):
> 1. Run `cargo clippy --workspace -- -W clippy::unwrap_used` to identify true positives
> 2. Distinguish test-module unwraps (acceptable with `#[expect(clippy::unwrap_used)]`)
>    from production code unwraps (must be replaced with `?`, `.ok_or()`, or `.unwrap_or()`)
> 3. Target: 0 production unwraps (match nestGate, loamSpine, toadStool, esotericWebb)
>
> **Deliverables**:
> 1. Production unwrap count: before/after
> 2. Test-module unwraps annotated with `#[expect(clippy::unwrap_used)]`
> 3. Handoff with results

---

## 7. lithoSpore team (strandGate) — pseudoSpore Promotions

> **lithoSpore** — Wave 150u evolution assignment.
>
> **Context**: 7 springs have emitted pseudoSpores. Only hotSpring (CompChem-
> GuideStone v1.6.1) is COMPLETE. 6 are PENDING. The Validation Data Stream
> Standard v1.0 is now published — spring teams know the contract.
>
> **Assignment**: Work with each spring team to promote their 6 PENDING pseudoSpores.
>
> | Spring | Artifact | Action Needed |
> |--------|----------|---------------|
> | groundSpring | LTEE-Measurement v1.0.0 | Populate validation.json |
> | airSpring | Agricultural-Meteorology v1.0.0 | Populate validation.json |
> | healthSpring | Clinical-PKPD v1.0.0 | Populate validation.json |
> | neuralSpring | ML-Surrogates v1.0.0 | Populate validation.json |
> | wetSpring | Life-Science-Analytics v1.0.0 | Populate validation.json |
> | ludoSpring | Game-Science v1.0.0 | Populate validation.json |
>
> **Pipeline**: `litho populate-validation` → `litho audit` → `litho promote-spore`
>
> **Standard**: `gardens/lithoSpore/specs/VALIDATION_DATA_STREAM.md` (v1.0)

---

## 8. bingoCube team — WASM WebGL Widget on primals.eco

> **bingoCube** — Wave 150u evolution assignment.
>
> **Context**: petalTongue's WASM WebGL pipeline shipped in Wave 150r.
> `render_color_grid_webgl(id, cols, rows, colors, reveal)` is exported from
> `petal-tongue-wasm`. bingoCube is unblocked for an interactive visualization
> on `sporeprint.primals.eco`.
>
> **Assignment**: Create an interactive bingoCube commitment widget that renders
> on sporePrint via petalTongue's WASM WebGL pipeline.
>
> **Deliverables**:
> 1. bingoCube commitment grid rendered via `render_color_grid_webgl`
> 2. User interaction: commit → reveal cycle demonstrated in browser
> 3. Deployable on `sporeprint.primals.eco/bingocube` (or similar path)
>
> **Depends on**: petalTongue v1.7+ deployed (see sporeGate team assignment #4)

---

## 9. footPrint team (flockGate) — Data Layer Primal Abstraction

> **footPrint** — Wave 150u evolution assignment.
>
> **Context**: The data layer primal abstraction spec is committed at
> `protists/footPrint/specs/DATA_LAYER_PRIMAL_ABSTRACTION.md`. 15 data sources
> mapped to primal paths. Lansing Scuffle GeoJSON project committed.
>
> **Assignment**: Begin the P1 Source Definition Registry — move from imperative
> `registerSource()` calls to a declarative JSON/TOML manifest that can be
> loaded, shared, and served from nestGate CAS.
>
> **Deliverables**:
> 1. Source definition TOML/JSON schema
> 2. Declarative registry loader replacing per-module `registerSource()` calls
> 3. At least 1 source (OSM buildings) migrated to declarative format
> 4. Handoff with migration plan for remaining 14 sources

---

## 10. esotericWebb team (ironGate/flockGate) — pseudoSpore Explorer (P2)

> **esotericWebb** — Wave 150u evolution assignment (P2 — after petalTongue v1.7 deploy).
>
> **Context**: esotericWebb V22 is live on flockGate. The petalTongue WASM WebGL
> pipeline is shipped. pseudoSpore pipeline has 7 emitted spores. There is no
> existing integration between esotericWebb and pseudoSpore.
>
> **Assignment**: Prototype the **pseudoSpore Explorer** — an interactive interface
> where users can walk through a pseudoSpore's structure (scope, validation
> modules, provenance DAG, receipts, checksums) rendered through petalTongue's
> scene graph.
>
> **Architecture**:
> ```
> pseudoSpore on disk
>   → lithoSpore pseudospore-core::load() + validate()
>   → nestGate ingests artifacts
>   → biomeOS graph.execute routes to:
>       rhizoCrypt  → DAG visualization (provenance)
>       sweetGrass  → attribution rendering
>       bearDog     → BLAKE3 verification
>       petalTongue → scene graph → WASM WebGL → browser
>   → esotericWebb wraps in narrative (Squirrel narrates)
> ```
>
> **Deliverables** (prototype):
> 1. `DataBinding::PseudoSpore` channel type in petalTongue
> 2. `pseudospore.explore` JSON-RPC method in esotericWebb bridge
> 3. Scene builder: `scope.toml` + `validation.json` → SceneGraph nodes
> 4. Load hotSpring CompChem-GuideStone v1.6.1 (the COMPLETE spore) as demo
>
> **Depends on**: petalTongue v1.7+ deployed, pseudoSpore promotions progressing

---

## 11. Ops — southGate + strandGate Enrollment

> **Operator** (eastGate) — Wave 150u ops assignment.
>
> **southGate**: USB enrollment bundle staged at `/mnt/usb/ecoprimals`. IP
> allocated at 10.13.37.9. Physical action: plug USB, run `gate-usb-bootstrap.sh`,
> add WG peer on golgiBody. southGate runs songBird/biomeOS/bearDog (mesh +
> orchestration + security primals).
>
> **strandGate**: Dual EPYC 7452 (64 cores), 256GB ECC, RTX 3090. Enrollment
> pending. This is the provenance trio homeworld + ABG science compute target.
> Once enrolled: rhizoCrypt, loamSpine, sweetGrass, hotSpring (science),
> barraCuda, coralReef SPIR-V, helixVision, initioChem, blueFish, lithoSpore.

---

## Team → Assignment Summary

| # | Team | Gate | Assignment | Priority |
|---|------|------|-----------|----------|
| 1 | bearDog | southGate | Android Keystore backend + grapheneGate testing | **P1** |
| 2 | squirrel | eastGate | CredentialStore integration via `secrets.*` RPC | **P1** |
| 3a | primalSpring | eastGate | Tower parity orchestration — WAN first, LAN when ironGate returns | **P1** |
| 3b | flockGate team | flockGate | WAN benchmark peer (Phase 1 — NOW) | **P1** |
| 3c | golgiBody team | VPS | TURN relay deploy + WAN benchmark peer (Phase 1 — NOW) | **P1** |
| 3d | ironGate team | ironGate | LAN benchmark peer (Phase 2 — when hardware returns) | **P1** deferred |
| 4 | sporeGate ops | sporeGate | Deploy petalTongue v1.7+ to flockGate | **P1** |
| 5 | sporePrint | flockGate | Lansing Scuffle pages + primal pipeline design | **P1** |
| 6 | cellMembrane | ironGate | Unwrap audit (456 production unwraps) | **P2** |
| 7 | lithoSpore | strandGate | Promote 6 pending pseudoSpores | **P2** |
| 8 | bingoCube | eastGate | WASM WebGL widget on primals.eco | **P2** |
| 9 | footPrint | flockGate | Data layer → declarative source registry | **P2** |
| 10 | esotericWebb | ironGate | pseudoSpore Explorer prototype | **P3** |
| 11 | operator | eastGate | southGate + strandGate enrollment | **P1** |

**Note**: All atomic composition testing (Tower Atomic, NUCLEUS compositions,
cross-gate capability.call) is routed through **primalSpring** (eastGate).
primalSpring is the coordination spring — it validates that compositions work,
not the individual atoms. Individual primal teams ship their endpoints;
primalSpring validates the composition.
