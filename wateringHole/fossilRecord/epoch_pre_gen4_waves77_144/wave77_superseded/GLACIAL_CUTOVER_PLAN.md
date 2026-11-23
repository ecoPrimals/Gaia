# Glacial Cutover Plan — Stadial Entry

**Status**: Active  
**Published**: 2026-06-01 (Wave 67)  
**Authority**: eastGate coordination via wateringHole  
**Distributed**: Via `membrane temporal.cascade` through peptidoglycan  

---

## Position

The ecosystem is at ~9.5/10 for interstadial exit. Infrastructure is built;
the shift is in **validation/cutover**, not construction. Inner membrane is
largely sovereign. Outer membrane runs on controlled-trust VPS ($48/mo).
External dependencies (Cloudflare DNS, GitHub Pages/Actions) are inactive or
shadow-only in the data path.

**Glacial criteria scorecard:**

| # | Criterion | Status | Blocker |
|---|-----------|--------|---------|
| 1 | S1-S4 shadows cut over | 3.5/4 | S1 ready to graduate; S4 formal gate pending |
| 2 | 3+ gate Plasmodium mesh | Unproven | `discovery.peers` + `capability.call` not live-validated |
| 3 | VPS Nest expansion | DONE | 20/20 services on golgiBody |
| 4 | Remote covalent (flockGate) | DONE | WAN relay validated (~1.3s) |
| 5 | DNS to sovereign infra | Infra live | Registrar NS cutover pending |
| 6 | Cloudflare removed | Partial | NS delegation still points to Cloudflare |

---

## Phased Cutover

### Phase 0 — Inner Membrane (NOW)

Items that can complete immediately with no external dependency.

| Item | Owner Gate | Primals/Projects | Action | Status |
|------|-----------|-----------------|--------|--------|
| **S1 TLS graduation** | ironGate (cellMembrane) | Caddy | Declare S1 OPERATIONAL (13d > 7-day gate) | Ready |
| **Songbird security socket fix** | southGate | Songbird | `songbird_http_client` must honor `--security-socket` / `BEARDOG_SOCKET` instead of hardcoded `/tmp/neural-api-*.sock` | **DONE** (eb913612) |
| **biomeOS `capability.call` RPC** | southGate | biomeOS | Implement JSON-RPC method (currently -32601) | **DONE** (9ed36983) |
| **bearDog S4 service config** | southGate (bearDog) + ironGate (validation) | bearDog | Configure BearDog auth services; begin formal 7-day shadow gate | **DONE** (Wave 119, 5e6b5a5) |
| **VPS relay bash to Rust** | ironGate (cellMembrane) | membrane | 4 bash scripts (pepti-sync-relay, ext-github-push, post-receive hook, impulse relay) to `membrane relay.*` | P1 |
| **golgiBody disk cleanup** | ironGate (cellMembrane) | — | Move build artifacts to peptidoglycan (9% used, 79GB free) | P1 |
| **Family seed on golgiBody** | ironGate (cellMembrane) | biomeOS | Replace dev-mode; production family seed | P1 |

### Phase 1 — Mesh Validation (after Phase 0 fixes)

Prove multi-gate covalent mesh works. This is glacial criterion #2.

**Wave 67 live test results (2026-06-01):**
- bearDog + Songbird start clean on eastGate (HSM, BTSP, federation :7700, IPC, JWT)
- **strandGate (192.168.1.132) auto-discovered** via UDP broadcast — orchestration, federation, secure_http, TLS 1.3 capabilities
- strandGate federation port :7700 TCP reachable (same subnet)
- `discovery.peers` RPC responds but peer list empty — TLS handshake fails on pre-fix binary
- **BLOCKED**: local Songbird binary predates socket fix (eb913612). Needs plasmidBin deploy.
- **GAP FOUND**: cascade syncs source but not binaries → **ecoBins evolution needed** in waterfall

| Item | Owner Gate | Action | Status |
|------|-----------|--------|--------|
| **ecoBins pipeline** | eastGate (plasmidBin + membrane) | `plasmidbin install` — build from local source + install to PATH | **DONE** (f8da0b2) |
| **Deploy Songbird w/ socket fix** | eastGate (plasmidBin) | `plasmidbin install songbird` → eb913612 deployed with provenance | **DONE** |
| **`discovery.peers` smoke test** | eastGate (primalSpring) | Same-subnet test: eastGate ↔ strandGate (192.168.1.132, already broadcasting) + southGate | BLOCKED on deploy |
| **`capability.call` smoke test** | eastGate (primalSpring) | Run `s_covalent_mesh` scenario live | BLOCKED on deploy |
| **Plasmodium collective sign-off** | eastGate (primalSpring) | 3+ gates meshed, formal validation | Pending |
| **southGate federation verify** | southGate | Confirm `SONGBIRD_PEERS` + 13/13 after Songbird fix | Pending |
| **Cross-subnet routing** | infra/network | southGate (192.168.4.x) to eastGate (192.168.1.x) — Eero mesh routes between properties, needs OS route | Pending |

### Phase 2 — Outer Membrane Cutover

DNS first, then content. Inner membrane stays on controlled-trust VPS (the
K-Derm model: VPS IS the outer membrane between gates and internet).

| Item | Owner Gate | Action | Depends On |
|------|-----------|--------|------------|
| **DNS NS registrar cutover** | eastGate (manual) | Execute `DNS_NS_CUTOVER_INSTRUCTIONS.md`: NS to ns1/ns2, glue IPs, DS record | Phase 0 S1 graduation |
| **golgiBody-ext HTTPS** | ironGate (cellMembrane) | Enable Caddy TLS on ext for lab/sporePrint domains | DNS cutover |
| **sporePrint content cutover** | flockGate + ironGate | Caddy to petalTongue:8080 for primals.eco | HTTPS on ext |
| **GitHub Pages to shadow** | flockGate | Disable apex deploy; keep as verification oracle | Content cutover |
| **Cloudflare removal** | eastGate | Verify `dig NS primals.eco` returns sovereign NS; remove Cloudflare config | DNS cutover |

### Phase 3 — External Dependency Elimination (post-stadial)

Long-term evolution away from remaining commercial services.

| Item | Owner Gate | Action | Timeline |
|------|-----------|--------|----------|
| **GitHub Actions to Forgejo Actions** | ironGate (projectNUCLEUS) | Shadow CI on ironGate, then invert | Wave 70+ |
| **GitHub becomes weak-bond mirror** | ironGate (cellMembrane) | `ext-github-push.sh` to `membrane relay.ship`; push-only via trans face | Wave 68+ |
| **2nd CI runner** | ironGate (cellMembrane) | eastGate 2nd runner to eliminate ironGate SPOF | Wave 68+ |
| **Multi-vendor peptidoglycan** | ironGate (cellMembrane) | Hetzner/Vultr node for redundancy | Post-stadial |
| **Self-hosted outer membrane** | all | VPS to sovereign hardware (port-forward or dedicated box) | Post-stadial |
| **BearDog ACME (replace Caddy LE)** | southGate (bearDog) | Internal CA for mesh TLS; Caddy works now | Post-stadial |

---

## Gate Assignments

### eastGate (Overwatch)

**Owns**: primalSpring, airSpring, groundSpring, skunkBat, squirrel  
**Role**: Coordination. Validates compositions work together.

**Wave 67+ tasks:**
1. Run `discovery.peers` smoke test with southGate (Phase 1)
2. Run `s_covalent_mesh` live validation (Phase 1)
3. Execute DNS NS registrar cutover (Phase 2, manual)
4. Publish Plasmodium collective results

### ironGate (Deployment Infrastructure)

**Owns**: cellMembrane, projectNUCLEUS, NestGate, petalTongue, healthSpring,
ludoSpring, esotericWebb  
**Role**: Deployment infra, VPS provisioning, CI pipeline.

**Wave 67+ tasks:**
1. Declare S1 TLS OPERATIONAL (13d passed)
2. Configure S4 auth validation environment (bearDog service on southGate provides auth)
3. Evolve VPS relay scripts to Rust (`membrane relay.mediate`, `relay.ship`)
4. golgiBody disk cleanup — move artifacts to peptidoglycan
5. Deploy sporePrint Nest Atomic composition on golgiBody-ext
6. Shadow Forgejo Actions CI (Phase 3)

### southGate (Mesh + Orchestration + Security)

**Owns**: Songbird, biomeOS, bearDog, wetSpring, neuralSpring  
**Role**: Core mesh and orchestration primals. Security infrastructure.

**Wave 67+ tasks:**
1. ~~Songbird security socket fix~~ **DONE** (eb913612) — `--security-socket` / `BEARDOG_SOCKET` honored.
2. ~~biomeOS `capability.call`~~ **DONE** (9ed36983) — proxied to Neural API.
3. ~~bearDog S4 config~~ **DONE** (Wave 119, 5e6b5a5) — method gate evolution, BTSP config, platform support.
4. Cross-gate mesh partner for eastGate `discovery.peers` test (Phase 1) — **NEXT**.

### biomeGate (Air-Gap Tester)

**Owns**: hotSpring, toadStool  
**Role**: Isolated HPC validation. Air-gap testing pattern.

**Wave 67+ tasks:**
1. hotSpring Exp 234 Run #6 — upstream audit cleared. Reboot, then:
   `sovereign.warm_handoff` with `nvidia_catalyst_minimal_nop_titanv`.
   If clean: proceed to channel-adoption, then shader-dispatch.
2. toadStool kernel patch set validation (21 targets, 720/720 tests passing).

### flockGate (WAN Covalent)

**Owns**: sporePrint  
**Role**: WAN relay validation, sporePrint hosting.

**Current status**: Clear. W67 (22/22 content-direct parity) and W68 (live
viz + deep debt) complete.

**Wave 67+ tasks:**
1. Content cutover pending Phase 2 DNS (Caddy to petalTongue:8080).
2. GitHub Pages archival after content cutover confirmed.
3. Provenance trio data system (BLAKE3 content addressing, Wave 69+).

### strandGate (Provenance + Compute)

**Owns**: rhizoCrypt, loamSpine, sweetGrass (provenance trio), barraCuda,
coralReef (compute trio), hotSpring (science side)  
**Role**: Heavy science, provenance infrastructure.  
**Gardens**: helixVision, initioChem, blueFish, lithoSpore

**Status**: Hardware ready (Dual EPYC 7452, 256GB ECC), not deployed.

**Wave 67+ tasks:**
1. Gate deployment after mesh validated (Phase 1 complete).
2. Provenance trio wiring: `content.put` to rhizoCrypt DAG + loamSpine ledger.
3. Cross-gate compute dispatch from biomeGate.

---

## External Dependencies Remaining

| Service | Current Role | Sovereign Replacement | Cutover Phase |
|---------|-------------|----------------------|---------------|
| Cloudflare DNS | NS delegation | knot-dns ns1+ns2 (live, DNSSEC) | Phase 2 |
| Cloudflare TLS | INACTIVE | Caddy + LE (13d proven) | Phase 0 graduation |
| cloudflared | INACTIVE | Songbird TURN (done) | Complete |
| GitHub Pages | S3 content baseline | NestGate + Caddy (67ms TTFB) | Phase 2 |
| GitHub Actions | plasmidBin CI/harvest | Forgejo Actions (planned) | Phase 3 |
| GitHub repos | Weak extracellular mirror | Forgejo (38 repos, push-only) | Phase 3 |
| DigitalOcean VPS | Inner membrane hosting | Controlled-trust ($48/mo) | Accept as K-Derm outer membrane |
| Let's Encrypt | TLS certs | Caddy ACME (works now) | Accept; BearDog ACME post-stadial |
| DNS registrar | Permanently external | Multi-registrar mitigation | Cannot eliminate |
| crates.io / NCBI | Extracellular weak bonds | — | Post-stadial, not blocking |

---

## Critical Path

```
  Songbird socket fix (southGate)     DONE (eb913612)
  + biomeOS capability.call (southGate) DONE (9ed36983)
  + S4 bearDog config (southGate)      DONE (Wave 119)
        |
        v
  ecoBins pipeline (plasmidBin)         DONE (f8da0b2)
  (plasmidbin install: source → binary → PATH)
        |
        v
  Songbird eb913612 deployed to eastGate  DONE
  + southGate route (Eero cross-subnet)   PENDING
        |
        v
  discovery.peers test (eastGate ↔ strandGate + southGate)  <-- YOU ARE HERE
  + capability.call test (primalSpring s_covalent_mesh)
  (NOTE: strandGate@192.168.1.132 already broadcasting!)
        |
        v
  Plasmodium collective 3+ gates  ----+
                                      |
  S1 graduation (ironGate)            |
  + DNS NS cutover (eastGate manual)  |
        |                             |
        v                             v
  golgiBody-ext HTTPS          STADIAL ENTRY
  + sporePrint cutover              (all 6 criteria met)
  + GitHub Pages archive
```

---

## Validation Opportunity

This plan is distributed via `membrane temporal.cascade` through peptidoglycan.
Each gate pulling wateringHole and receiving this doc + their impulse confirms
the sync chain works. Report sync results in your ack.

---

## Wave 68 Strategic Extensions

Four new evolution domains extend the glacial plan beyond infrastructure cutover:

- **Songbird routing consolidation** — TCP Tier 5 blocked in release builds; Songbird virtual endpoint relay designed for single-ingress gate surface; membrane TLS sovereignty planned. See `SONGBIRD_VIRTUAL_ENDPOINT_RELAY_DESIGN.md`.
- **Neural API perceptron routing** — L4 weighted selection impulse dispatched to biomeOS; single-layer perceptron design for L5 learned routing published; training pipeline uses existing `dispatch_telemetry.jsonl`. See `NEURAL_API_PERCEPTRON_DESIGN.md`.
- **grapheneGate portable trust anchor** — Pixel 8a (GrapheneOS) added to ecosystem manifest as `portable_anchor` gate class; three-role evolution (beacon → relay → mesh seed) for overseas/hostile-network operation. See `GRAPHENEGATE_BOOTSTRAP_STANDARD.md`.
- **Topology-aware routing** — Network segment model with latency estimates and affinity values published in `TOPOLOGY_MAP.toml`; discovery.peers extended with latency_ms field; routing impulse dispatched to biomeOS.

---

## Cross-References

- `GATE_TEAM_COORDINATION_MATRIX.md` — gate/team/hardware/project SSOT
- `GLACIAL_SHIFT_READINESS.md` — operational status, detailed criteria
- `DNS_NS_CUTOVER_INSTRUCTIONS.md` — step-by-step NS registrar procedure
- `GATE_SPRING_OWNERSHIP.md` — canonical spring routing
- `IMPULSE_POTENTIAL_STANDARD.md` — impulse format and lifecycle
- `TOPOLOGY_MAP.toml` — network segment model with latency/affinity
- `GRAPHENEGATE_BOOTSTRAP_STANDARD.md` — portable trust anchor protocol
- `SONGBIRD_VIRTUAL_ENDPOINT_RELAY_DESIGN.md` — single-ingress design
- `NEURAL_API_PERCEPTRON_DESIGN.md` — learned routing evolution

---

*Wave 68. Infrastructure built. Routing learns. Trust goes portable.*
