# Glacial Shift Deployment Plan — Wave 77 to Stadial Entry

**Status**: Active (Wave 77)  
**Date**: 2026-06-04  
**Prerequisites**: Ecosystem at full parity (Wave 77). All teams aligned.

---

## How to Read This Plan

This plan is **position-independent**. It defines *what* needs to happen,
not *who coordinates it*. Any overwatch — whether on eastGate, ironGate,
one per gate, or a distributed constellation — can pick up this document
and know the goals, the state, and the next steps.

Two tracks run in parallel with different cadences:

| Track | Nature | Cadence | Artifacts |
|-------|--------|---------|-----------|
| **Code Evolution** | Software: features, tests, validation scenarios, debt | Continuous — teams evolve asynchronously on blurb cycles | Handoffs, FRAGOs, blurbs |
| **Infrastructure** | Real-world: DNS, hardware, registrar panels, Cloudflare, physical setup | Async — depends on operator availability, propagation delays, shipping | Operator checklists |

Code evolution goals stand on their own. A team's blurb is valid whether
overwatch is on eastGate or split across 5 gates. Infrastructure tasks
are sequenced by real-world dependencies (DNS propagation, hardware ETA)
and may lag or lead the code work independently.

Overwatch is a convenience for coordination, not a dependency for progress.
See `OVERWATCH_POSITION_STANDARD.md` for the full model.

---

# Part A: Code Evolution Goals

These are the software milestones. They proceed regardless of
infrastructure state. Teams can be blurbed from any overwatch position.

## A1. Live Cross-Gate Trust Validation (P0)

**Goal**: Prove the full chain works end-to-end with real BTSP credentials
on a live mesh.

**FRAGO**: `wave77-live-cross-gate-validation.toml` (active)

| Task | Team(s) | Gate(s) | Key Files | Status |
|------|---------|---------|-----------|--------|
| Live `capability.call` (eastGate → strandGate) | primalSpring | eastGate | `s_covalent_mesh.rs` | FRAGO fired |
| Security property checks in `s_covalent_mesh` | primalSpring | eastGate | `covalent_mesh_trust.rs` | FRAGO fired |
| Forged token rejection (cross-gate) | primalSpring | eastGate | `covalent_mesh_trust.rs` | Code exists, needs live run |
| `verification_source="remote"` pass criterion | primalSpring + bearDog | eastGate + southGate | `auth.verify_ionic` | Code exists, needs live run |

**Deliverable**: Handoff with `capability.call` log showing full chain
(discovery → route → dispatch → verify → respond).

**Pass criterion**: `security:cross_gate_verify` PASS, `security:reject_forged` PASS.

## A2. Content Federation (P1)

**Goal**: NestGate `content.put` on Gate A → `content.replicate.pull` on
Gate B with BLAKE3 integrity verified end-to-end.

| Task | Team(s) | Gate(s) | Key Files | Status |
|------|---------|---------|-----------|--------|
| HTTP transport for content streaming | NestGate | ironGate | `content_backend.rs` | In progress |
| Live federation test (put → pull → verify) | primalSpring + NestGate | eastGate + strandGate | `covalent_mesh_trust.rs` Phase 5 | Code exists, needs live NestGate |
| sporePrint cas-manifest cross-gate | sporePrint + NestGate | flockGate + ironGate | cas-manifest | TODO |
| ZFS-backed CAS on westGate | NestGate | westGate (when hardware arrives) | `NESTGATE_STORAGE_BASE_PATH` | Waiting hardware |

**Pass criterion**: BLAKE3 hash matches across gate boundary.

## A3. Relay Security — Songbird Phase 3.5 (P1)

**Goal**: Full Ed25519 signature verification on the Songbird relay path.
Currently Phase 3 (structured token parsing + timestamp freshness).
Phase 3.5 adds cryptographic verification of token content.

| Task | Team(s) | Gate(s) | Key Files | Status |
|------|---------|---------|-----------|--------|
| `CryptoProvider::call("crypto.verify.ed25519")` | bearDog | southGate | bearDog crypto module | Scaffolded |
| Ed25519 verification in relay | Songbird | southGate | `relay_security.rs` | Scaffolded |
| Relay tamper rejection test | primalSpring | eastGate | `s_covalent_mesh.rs` | TODO |

**Pass criterion**: Relay-mediated requests carry verifiable Ed25519 signatures.

## A4. Neural API L5 Evolution (P2)

**Goal**: biomeOS wires L5 perceptron shadow mode — `ml.mlp_infer` via
barraCuda runs alongside L4 weighted routing to build training data.

| Task | Team(s) | Gate(s) | Key Files | Status |
|------|---------|---------|-----------|--------|
| L5 shadow mode (dual L4+L5 path) | biomeOS | southGate | `neural_api_server/mod.rs` | Perceptron consumer wired |
| `ml.mlp_infer` remote call | biomeOS + barraCuda | southGate + strandGate | `ml.rs` | ml.* behind BTSP MethodGate |
| Telemetry collection for training | biomeOS + toadStool | southGate | `dispatch_telemetry.jsonl` | Schema delivered |

## A5. Provenance Trio Cross-Gate Schemas (Delivered — Maintain)

Already delivered in Wave 76 parity sprint. Maintain and extend:

| Component | Team | Gate | Status |
|-----------|------|------|--------|
| rhizoCrypt mesh event types | rhizoCrypt | strandGate | Delivered |
| loamSpine trust entry schema | loamSpine | strandGate | Delivered |
| sweetGrass v0.7.45 attribution braids | sweetGrass | strandGate | Delivered |

## A6. Compute Trio (strandGate Software, biomeGate Hardware)

| Task | Team | Gate | Status |
|------|------|------|--------|
| barraCuda ml.rs modularized | barraCuda | strandGate | Delivered |
| coralReef SPIR-V portable output | coralReef | strandGate | Delivered |
| toadStool S288 panic elimination | toadStool | biomeGate (remote) | Delivered |
| toadStool GPU dispatch (SM120) | toadStool | biomeGate | **BLOCKED** — hardware offline |
| coralReef Blackwell SM120 | coralReef | biomeGate | **BLOCKED** — hardware offline |

biomeGate stays offline. Software work is on strandGate. GPU-dependent
work waits. Not on the critical path.

---

# Part B: Infrastructure Goals

These are real-world tasks. They depend on operator availability,
physical access, DNS propagation times, and hardware shipping. They
run on a more async cadence than code evolution.

## Domain Architecture

Three domains on Porkbun, each with a distinct role in the K-Derm
diderm model:

| Domain | K-Derm Layer | Purpose | Sovereign Target |
|--------|-------------|---------|-----------------|
| **primals.eco** | Outer membrane (trans face) | Public-facing: sporePrint, Forgejo, content serving | golgiBody-ext (Caddy, 137.184.197.151) |
| **primal.eco** | Inner membrane (cis face) | Internal coordination: mesh services, relay, API | golgiBody ([RELAY_PUBLIC]) / LAN gates |
| **nestgate.io** | Content layer | Data objects: pseudoSpores, notebooks, CAS content | golgiBody-ext (Caddy) → NestGate CAS backend |

This maps to the biological model: `primals.eco` is the external surface
that the world sees. `primal.eco` is the inner membrane that coordinates
the organism. `nestgate.io` is the specialized organelle for storing and
serving content-addressed data objects.

### Current knot-dns State (Verified 2026-06-04)

**`primals.eco` zone** — LIVE, DNSSEC active, zone transfer to ns2 confirmed.
Stays on Cloudflare DNS (outer membrane per diderm model).

**`primal.eco` zone** — **LIVE + TLS OPERATIONAL** (Jun 4). DNS propagated on
public resolvers (8.8.8.8, 1.1.1.1 → 137.184.197.151). Let's Encrypt cert
obtained via Caddy TLS-ALPN-01. HTTPS serving: `primal.eco — inner membrane
operational`. NS: ns1.primals.eco + ns2.primals.eco. DNSSEC active + DS records
submitted to Porkbun.

**`nestgate.io` zone** — **DNS PROPAGATING** (Jun 4). Zone created, DNSSEC
active, NS set at Porkbun, DS records submitted. SERVFAIL on public resolvers
(TLD registry propagation in progress). TLS cert will auto-provision via Caddy
once DNS resolves.

## B1. DNS NS Registrar Cutover — primals.eco (Critical Path)

**Type**: Operator action (Porkbun)  
**Dependency**: None — zone verified, unblocked now  
**Async factor**: 24-48h DNS propagation after registrar change

On Porkbun → `primals.eco` → Nameservers → Custom:

| Nameserver | Glue IP |
|-----------|---------|
| `ns1.primals.eco` | [RELAY_PUBLIC] |
| `ns2.primals.eco` | 137.184.197.151 |

**Verification**:
```
dig @8.8.8.8 primals.eco NS
dig @1.1.1.1 primals.eco NS
dig @9.9.9.9 primals.eco NS
```

**Unblocks**: B2, B3, criterion 5.

See `DNS_NS_CUTOVER_OPERATOR_CHECKLIST.md` for full step-by-step.

## B1b. DNS Zone Creation — primal.eco + nestgate.io

**Type**: Operator + cellMembrane evolution  
**Status**: **`primal.eco` COMPLETE. `nestgate.io` propagating.**

**primal.eco** (inner membrane) — **ALL STEPS COMPLETE**:
1. ~~Create zone file on golgiBody~~ — DONE (DNSSEC active, zone transfer to ns2)
2. ~~Add zone to knot-dns config, enable DNSSEC~~ — DONE
3. ~~Configure Caddy virtual host on golgiBody-ext~~ — DONE (TLS cert obtained Jun 4)
4. ~~On Porkbun: set NS + DS records~~ — DONE (NS propagated, DS submitted)

**Verification** (Jun 4, 12:50 ET):
- `host primal.eco 8.8.8.8` → 137.184.197.151 (correct)
- `host -t NS primal.eco 8.8.8.8` → ns1.primals.eco, ns2.primals.eco (correct)
- `curl https://primal.eco` → `primal.eco — inner membrane operational` (TLS valid)

**nestgate.io** (content objects) — **STEPS 1-4 COMPLETE, PROPAGATING**:
1. ~~Create zone file~~ — DONE (DNSSEC active)
2. ~~Add zone to knot-dns config~~ — DONE
3. ~~Configure Caddy virtual host~~ — DONE (TLS will auto-provision once DNS resolves)
4. ~~On Porkbun: set NS + DS records~~ — DONE
5. Wire NestGate content serving: `nestgate.io/<hash>` → `content.get` — **PENDING** (after TLS live)

**Content model for nestgate.io**:
- PseudoSpores, notebooks, and data objects live as CAS-addressable resources
- BLAKE3 content hashing provides integrity verification
- westGate's 76TB ZFS pool is the primary backing store
- Cross-gate federation via `content.replicate.pull` keeps copies in sync

## B2. S1 TLS — Outer vs Inner Membrane (Revised)

**Type**: Operator action  
**Dependency**: B1 (DNS propagation confirmed)  
**Protocol**: Calibrate → Shadow → Cutover (`SOVEREIGNTY_STANDARDS.md`)

**Diderm revision**: Under the diderm model, TLS sovereignty applies
specifically to the **inner membrane** (`primal.eco`, `nestgate.io`).
The outer membrane (`primals.eco`) may retain Cloudflare for DDoS
protection and CDN benefits.

| Domain | TLS Provider | Dark Forest | Status |
|--------|-------------|-------------|--------|
| `primals.eco` | Cloudflare proxy (acceptable) | RELAXED | Operational |
| `primal.eco` | Sovereign Caddy + LE (required) | STRICT | **LIVE** — cert obtained Jun 4 |
| `nestgate.io` | Sovereign Caddy + LE (required) | STRICT | DNS propagating — cert auto-provisions |

Once `primal.eco` and `nestgate.io` are on sovereign DNS + TLS, the
inner membrane has zero commercial TLS dependency regardless of
what happens on the outer membrane.

Cross-membrane validation (`DIDERM_DOMAIN_ARCHITECTURE.md`) ensures the
outer membrane stays honest — inner membrane compares BLAKE3 content
hashes, TLS cert fingerprints, and timing baselines.

**Meets criteria**: 1 (sovereignty shadows graduated on inner membrane),
6 (inner membrane zero-commercial).

See `S1_TLS_GRADUATION_CHECKLIST.md` for the outer membrane removal
sequence (optional — can be deferred indefinitely under diderm model).

## B3. S3 Content Cutover — sporePrint Sovereign

**Type**: Automatic (with NS cutover)  
**Dependency**: B1 — once NS points to knot-dns, `primals.eco` A already
points to golgiBody-ext (137.184.197.151). Caddy serves sporePrint.

No separate DNS change needed — the knot-dns zone already has the right
A record. GitHub Pages becomes a trailing mirror automatically.

**Verification**: TTFB comparison (sovereign target: 67ms, GitHub baseline: 111ms).

## B4. S4 Auth Graduation

**Type**: Automatic (time-based)  
**Dependency**: None — running autonomously since Jun 2  
**Async factor**: Ends ~Jun 9

7-day gate runs to completion. 15-min probes accumulate. If
p95 < 50ms threshold met, S4 graduates.

**Review needed ~Jun 9**: Check probe log on ironGate. If passed,
update status to GRADUATED. If not, extend gate.

**Meets criteria**: 1 (all 4 sovereignty shadows graduated).

## B5. westGate Physical Enrollment

**Type**: Operator action  
**Dependency**: Hardware arrives  
**Async factor**: Hardware shipping + physical setup time

Connect westGate (i7-4771, RTX 2070 Super, 32GB, 76TB ZFS) to LAN.
Full 6-phase enrollment: Physical → Identity → Services → Mesh →
NestGate → Validation.

westGate's primary role: 76TB ZFS backing store for NestGate CAS.
This is the `nestgate.io` content layer's physical home.

**Meets criteria**: 2 (3+ gates in Plasmodium collective).

See `WESTGATE_ENROLLMENT_OPERATOR_CHECKLIST.md` for full step-by-step.

## B6. flockGate WAN Covalent Validation

**Type**: Operator verification + code validation  
**Dependency**: B1 + B2 (DNS and TLS sovereign first)

Verify flockGate (WAN) connectivity through cellMembrane relay
post-DNS-cutover. Run cross-network `capability.call`:
eastGate → golgiBody relay → flockGate.

**Meets criteria**: 4 (remote covalent node validated over WAN).

## B7. biomeGate (Parked — Not Critical Path)

Stays offline while its team works on the kernel issue. Compute trio
software is on strandGate. GPU-dependent work waits. Rejoin mesh
when ready — enrollment is standard (already has `.gate` identity).

---

# Part C: Glacial Shift Criteria (Revised — Diderm Membrane Architecture)

These are the 6 measurable conditions for stadial entry. **Revised Wave 77b**
to reflect the diderm membrane model (see `DIDERM_DOMAIN_ARCHITECTURE.md`):
the inner membrane (`primal.eco`) must be fully sovereign; the outer membrane
(`primals.eco`) may use commercial services. The peptidoglycan trust barrier
is disposable and replicable.

| # | Criterion | Code Goal | Infra Goal | Status |
|---|-----------|-----------|------------|--------|
| 1 | Sovereignty shadows graduated (inner membrane) | — | B2 + B3 + B4 | S2 GRADUATED. S4 gate active (~Jun 9). **S1 inner membrane TLS LIVE** (`primal.eco` Caddy+LE). S3 content layer wiring pending `nestgate.io`. |
| 2 | 3+ gates in LAN mesh | A1 (mesh validation) | B5 (westGate) | 2 meshed (eastGate + strandGate). Need 3rd (westGate hardware incoming). |
| 3 | Peptidoglycan replicable | — | B1b (peptidoglycan formalization) | **FORMALIZED** — ironGate ACK: Peptidoglycan variant + TrustBarrierConfig schema + contract doc + 4 tests. |
| 4 | Remote covalent node over WAN | A1 (capability.call) | B6 (flockGate) | flockGate OPERATIONAL, formal validation pending B1+B2. |
| 5 | DNS sovereign for inner membrane | — | B1 + B1b | **`primal.eco` DNS PROPAGATED + TLS LIVE.** `nestgate.io` propagating. `primals.eco` on Cloudflare (acceptable). |
| 6 | Inner membrane zero-commercial + cross-validation | Cross-membrane validation (A-new) | B1b (inner membrane DNS) | `primal.eco` zero-commercial ACHIEVED. Cross-membrane validation scenario shipped, live validation pending `nestgate.io`. |

**Key change**: Criterion 6 no longer requires Cloudflare elimination.
It requires zero commercial services in the `primal.eco` data path plus
operational cross-membrane validation (inner membrane validates outer
membrane integrity). See `DIDERM_DOMAIN_ARCHITECTURE.md` §Cross-Membrane
Validation.

**On declaration** (all 6 met):
1. Write `whitePaper/gen5/foundations/GLACIAL_SHIFT_DECLARATION.md`
2. Update `GLACIAL_SHIFT_READINESS.md` → **STADIAL ENTRY**
3. Archive remaining work handoff
4. Compose celebration blurbs for all teams

---

# Part D: Coordination Guide

This section is for whoever holds the overwatch position. It's guidance,
not a dependency — if overwatch changes gates or splits across multiple
positions, the goals in Parts A and B don't change.

### Overwatch Responsibilities (Any Position)

| Trigger | Action | Artifact |
|---------|--------|----------|
| Evolution handoff arrives | Absorb, update docs, archive, blurb next cycle | Handoff → archive, readiness update |
| FRAGO acknowledged | Track delivery, update criteria status | Readiness doc |
| DNS cutover confirmed | Verify propagation, proceed to B2 | `GLACIAL_SHIFT_READINESS.md` |
| S1 cutover complete | Fire FRAGO for 7-day monitoring | Impulse TOML |
| westGate joins mesh | Run `s_covalent_mesh` with 3 gates, update gen5 paper | Multiple docs |
| All criteria met | Declare glacial shift | gen5 paper + readiness |

### Operator Responsibilities (The User)

Infrastructure tasks are async. They can be done in any order as
dependencies allow, independent of code evolution cadence.

| Priority | Action | Depends On | Checklist |
|----------|--------|-----------|-----------|
| **NOW** | DNS NS registrar cutover | Nothing | `DNS_NS_CUTOVER_OPERATOR_CHECKLIST.md` |
| **NOW** | Confirm westGate hardware ETA | Nothing | — |
| After DNS (24-48h) | Remove Cloudflare proxy | B1 confirmed | `S1_TLS_GRADUATION_CHECKLIST.md` |
| After S1 | Update sporePrint CNAME | B2 complete | — |
| ~Jun 9 | Review S4 probe log | Time | — |
| When hardware arrives | westGate enrollment | Physical access | `WESTGATE_ENROLLMENT_OPERATOR_CHECKLIST.md` |
| After B1+B2 | flockGate WAN validation | DNS + TLS sovereign | — |

### Blurb Routing

Blurbs go to teams, not gates. If a team moves gates (e.g., compute
trio moved from biomeGate to strandGate), the blurb follows the team.
If overwatch splits, each overwatch blurbs the teams it can see.
The artifacts (handoffs, FRAGOs) are in `wateringHole/` — any overwatch
position can read them.

---

## References

- `DIDERM_DOMAIN_ARCHITECTURE.md` — Trust barrier model, domain assignments, cross-membrane validation
- `OVERWATCH_POSITION_STANDARD.md` — Floating coordination role
- `SOVEREIGNTY_STANDARDS.md` — Calibrate → Shadow → Cutover protocol
- `GLACIAL_SHIFT_READINESS.md` — 6 criteria + shadow schedule
- `GATE_TEAM_COORDINATION_MATRIX.md` — Gate inventory + wave assignments
- `ECOSYSTEM_COMMUNICATION_STANDARD.md` — Three-artifact coordination
- `DARK_FOREST_GLACIAL_GATE_STANDARD.md` — 5 security invariants + membrane classification
- `whitePaper/gen5/foundations/COVALENT_MESH_TRUST_VALIDATION.md` — Trust model
- `whitePaper/gen5/foundations/OVERWATCH_DISTRIBUTED_COORDINATION.md` — Overwatch pattern
- `DNS_NS_CUTOVER_OPERATOR_CHECKLIST.md` — DNS step-by-step
- `S1_TLS_GRADUATION_CHECKLIST.md` — Cloudflare removal sequence (outer membrane, optional)
- `WESTGATE_ENROLLMENT_OPERATOR_CHECKLIST.md` — westGate enrollment

---

## Changelog

| Wave | Change |
|------|--------|
| 77 | Initial: 5-phase deployment plan from parity to stadial entry. biomeGate excluded from critical path. |
| 77b | Restructured: separated Code Evolution (Part A) from Infrastructure (Part B). Made plan position-independent — goals survive overwatch changes. Added coordination guide as guidance, not dependency. |
| 77c | Diderm revision: revised glacial shift criteria for diderm membrane architecture. Criterion 6 now requires inner membrane zero-commercial + cross-membrane validation instead of total Cloudflare elimination. B2 revised for inner/outer TLS distinction. Added `DIDERM_DOMAIN_ARCHITECTURE.md` reference. |
| 77d | Inner membrane live: `primal.eco` DNS propagated + TLS cert obtained (LE via Caddy). B1b `primal.eco` marked COMPLETE. `nestgate.io` propagating. Criterion 3 FORMALIZED (ironGate ACK). Criteria 5+6 progress: inner membrane zero-commercial achieved. |

---

*"The glacier has paused to gather its mass. Every cell is aligned.
Now it moves — not in a rush, but with the weight of the whole."*
