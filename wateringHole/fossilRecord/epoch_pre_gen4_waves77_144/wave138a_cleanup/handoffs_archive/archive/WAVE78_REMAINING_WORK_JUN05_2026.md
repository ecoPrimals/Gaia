# Wave 79 Remaining Work — Full Parity & Mesh Deployment

**Date**: 2026-06-05  
**Author**: eastGate overwatch  
**Supersedes**: Wave 76 remaining work (archived)  
**Status**: Active  
**Updated**: Wave 82b — ecoPrimals workspace dewired from NestGate legacy. Root `.git` removed, `primals/nestGate/` is canonical. tideGlass seeded (protoKarya/tideGlass). Deep Debt Sprint COMPLETE (16/16, 929 tests). plasmidBin ownership formalized (cellMembrane → projectNUCLEUS). See `WAVE82_DEEP_DEBT_SPRINT_COMPLETE_JUN06_2026.md`.

---

## Strategic Context

Wave 77 delivered the diderm membrane architecture (3-layer sovereign TLS),
NUCLEUS deep debt evolution (TOML-driven routing, profile-driven launcher,
zero C deps), and live cross-gate trust chain proof (eastGate ↔ strandGate).

Wave 78 upstream deliveries resolved the two highest-priority blockers:
- **SB-TLS-01**: Songbird direct-mode TLS crypto routing (symmetric mesh unblocked)
- **SB-TLS-02**: Phase 3.5 Ed25519 relay signature verification shipped
- **BD-TRUST-01**: bearDog `auth.exchange_trust` (zero-operator trust seeding)
- **RC-POLL-01**: rhizoCrypt `MeshEventListener` polling wired

Wave 79 established the UDS-only stadial gate in primalSpring: launcher defaults
port-free, TCP discovery gated, all graphs `uds_only`, deploy profiles port-free.
BD-TRUST-01 resolved — Songbird wired `auth.exchange_trust` into `mesh.init`.
All 4 upstream gaps are closed. Songbird Wave 81 deep debt pass absorbed.

**Remaining critical path**: `deploy_membrane.sh refresh` → 13/13 ALIVE → mesh.init
with gate peers → 3-gate mesh proof → stadial entry.
ALL 13 primals VPS-ready. All headless regressions RESOLVED. Pipeline fully validated.

---

## Ecosystem Freshness Assessment (Jun 6, 2026 — Wave 82b)

**39/39 repos clean. Zero dirty. Zero unpushed.**

### Tier 1: HOT — All pushed, synced (Jun 6)

| Repo | Gate | Version/Wave | Latest |
|------|------|--------------|--------|
| primalSpring | eastGate | w82 | Deep debt sprint COMPLETE (16/16), 929 tests |
| wateringHole | eastGate | w82b | Glacial goals + tideGlass + dewiring |
| cellMembrane | ironGate | w82b | Deep debt refactor pushed |
| coralReef | strandGate | w82b | Socket path XDG simplification |
| loamSpine | strandGate | w82b | Lint fix, discovery doc comments |
| petalTongue | ironGate | w82b | Redundant MIME check removed |
| rhizoCrypt | strandGate | w82b | Discovery registration simplified |
| wetSpring | southGate | w82b | Deploy service unit added |
| esotericWebb | eastGate | w82b | Interactive launch script + deploy graph |
| bingoCube | eastGate | w82b | egui/eframe pinned to 0.28 |
| neuralSpring | southGate | w82b | Merge conflict resolved |
| ludoSpring | ironGate | w82b | Merge conflict resolved |
| bearDog | southGate | v0.9.0 / w140 | `auth.exchange_trust`, auto trust seeding |
| songBird | southGate | v0.2.9-w81 | SB-TLS-01, BD-TRUST-01 mesh.init |
| biomeOS | southGate | v4.07 / w77 | Perceptron training data pipeline |
| toadStool | biomeGate | S290 | CallerContext fan_out, --headless fix |
| sweetGrass | strandGate | v0.7.51 / w79b | Localhost-only default bind |
| NestGate | ironGate | s95b | HTTP parity, content serving, UDS compliance |
| barraCuda | strandGate | v0.4.0 / w76 | ML pipeline, mesh.trust_verify |
| skunkBat | eastGate | v0.2.2 | defense.status health probe |
| squirrel | eastGate | w76 | 7,098 tests. Env centralization done. |

### Tier 2: WARM — Functional, minor lag

| Repo | Gate | Last Wave | Parity Work Needed |
|------|------|-----------|--------------------|
| healthSpring | ironGate | w76 (Jun 2) | V65c glacial cutover done. Absorb Wave 82 patterns. |

### Tier 3: COOL — Evolving on separate tracks

| Repo | Gate | Last Wave | Status |
|------|------|-----------|---------| 
| airSpring | eastGate | w60 (May 29) | v0.10.0, 1,446 tests. Not on parity sprint. |
| groundSpring | eastGate | w63 (May 30) | V146, 1,123 tests. Squirrel integration done. |
| hotSpring | biomeGate | S284 (Jun 1) | v0.6.32, L6. Separate sovereign-compute track. |

### Tier 4: DORMANT (evolve on demand)

| Repo | Last Commit | Assessment |
|------|------------|------------|
| sourDough | Jun 4 | Meta-primal, scaffold tool. Current. |
| rustChip | Apr 30 | Utility crate. Not blocking. |

---

## Parity Gaps — Cross-Cutting

### Missing `domain_profile.toml` (3 springs)

Springs need root `domain_profile.toml` for `litho emit-pseudospore` and
ecosystem classification.

| Spring | Status |
|--------|--------|
| hotSpring | Has nested compchem profiles, no root profile |
| ludoSpring | Missing — composition-only spring |
| neuralSpring | Missing |

### Missing `capability_registry.toml` (6 primals)

Machine-readable TOML registry enables primalSpring `DOMAIN_OWNER_MAP` and
ecosystem tooling to auto-discover capabilities.

| Primal | Current State | Priority |
|--------|---------------|----------|
| songBird | `consumed_capabilities` in code only | MEDIUM |
| toadStool | `provided_capabilities` in handlers | MEDIUM |
| barraCuda | Inline in `primal.rs` | LOW |
| coralReef | Self-knowledge in code/CONTEXT | LOW |
| loamSpine | `CONSUMED_CAPABILITIES` in `niche.rs` | LOW |
| skunkBat | `CONSUMED_CAPABILITIES` in `dispatch.rs` | LOW |

### Coverage vs 90% Stadial Target

| Met (≥90%) | Below |
|------------|-------|
| bearDog (90.5%), biomeOS (90%+), squirrel (90.1%), sweetGrass (91.7%), loamSpine (90.9%), sourDough (95%+), skunkBat (90%+ fn) | **songBird (73%)**, nestGate (84%), petalTongue (~85%), toadStool (~84%), barraCuda (81% llvmpipe) |

---

## Remaining Work by Track

### Track 1: Parity Sprint — COMPLETE ✓ (Wave 76)

All teams absorbed Wave 76 trust infrastructure. 20 handoffs archived.

### Track 2: Live Cross-Gate Validation — PROVEN ✓ (Wave 77d)

Full trust chain proven live: eastGate ↔ strandGate via Songbird mesh +
bearDog ionic tokens + rhizoCrypt DAG provenance.

### Track 3: Diderm Membrane — LIVE ✓ (Wave 77-78)

| Layer | Domain | Status | TLS |
|-------|--------|--------|-----|
| Outer Membrane | primals.eco | LIVE (sporePrint) | Cloudflare |
| Inner Membrane | primal.eco | LIVE | Let's Encrypt (sovereign) |
| Content Layer | nestgate.io | LIVE | Let's Encrypt (sovereign) |
| Peptidoglycan (VPS) | golgiBody/golgiBody-ext | LIVE | Sovereign knot-dns |

### Track 4: VPS Binary Refresh (P0 — blocks mesh)

**Wave 79 deployment (Jun 5)**:
- `nucleus_launcher` v0.9.31 deployed to VPS (musl-static, Wave 79 UDS-only default)
- All 13 systemd units updated: Nest/Node/Meta switched to UDS-only or localhost-bound
- `membrane-socket-bridge.service` created for `/run/membrane/` → `/run/biomeos/` path alignment
- Legacy Nest TCP firewall rules (9500, 9601, 9700, 9850) removed from ufw
- Stale /tmp sockets cleaned

**VPS health (Jun 5, post Wave 79 unit refresh)**: 13/13 services active, 10/12 UDS ALIVE.
`skunkbat` TCP-only (needs binary rebuild for UDS), `squirrel`/`petaltongue` UDS connected
but health probe silent (binary-level framing difference). Mesh not yet initialized.

**Binary versions on VPS** (Wave 79b refresh):
10/13 primals refreshed to HEAD builds (Jun 5). skunkBat v0.2.5, rhizoCrypt v0.14.2,
sweetGrass v0.7.50, nestGate v0.5.0 (notable version jumps). 3 rolled back to pre-refresh
(toadstool/coralreef/squirrel) — headless VPS regressions in new code.

| Step | Owner | Status |
|------|-------|--------|
| Build fresh musl-static binaries for all 13 primals | plasmidBin / eastGate ops | **DONE** — 13 built, harvested with blake3 checksums |
| Deploy to golgiBody `/opt/membrane/` | operator | **DONE** — 10/13 refreshed, 3 rolled back (toadstool/coralreef/squirrel need repo fixes) |
| `nucleus_launcher` v0.9.31 to VPS | eastGate ops | **DONE** — Wave 79 binary deployed |
| Systemd units → UDS-only / localhost | eastGate ops | **DONE** — 13 units updated + songbird-mesh.service created |
| Wire `auth.exchange_trust` in Songbird `mesh.init` | Songbird (code) | **RESOLVED** — Binary refreshed on VPS |
| ~~Fix toadstool headless mode~~ | toadStool (biomeGate) | **RESOLVED** — v0.2.0 --headless flag, harvested |
| Call `mesh.init` on VPS Songbird with gate peers | operator | **READY** — all 13 confirmed, deploy refresh then mesh.init |
| 3-gate mesh proof | primalSpring overwatch | **BLOCKED** on mesh.init |
| S4 auth 7-day gate completion | bearDog + ironGate | ~Jun 9 |
| westGate enrollment | skunkBat + eastGate | Hardware pending |

### Track 4b: DH-1 Socket Standardization + UDS-Only Migration

**Wave 79 (Jun 5)**: Full systemd unit refresh. All 13 primals now have
UDS-only or localhost-bound units. `deploy_membrane.sh` updated: Nest units
generate `--socket` flags, skunkBat unit uses `--socket --no-tcp`, firewall
no longer opens standalone primal ports.

**UDS posture** (13/13 services active, 10/12 UDS health ALIVE):

| Primal | Transport | Socket | TCP | Status |
|--------|-----------|--------|-----|--------|
| beardog | UDS+TCP | `/run/membrane/beardog.sock` | 127.0.0.1:9100 (binary default) | ALIVE via UDS |
| songbird | UDS+TCP | `/run/membrane/songbird.sock` | :7700 (federation, correct) | ALIVE via UDS |
| biomeos | UDS | `/run/membrane/biomeos.sock` | — | ALIVE via UDS |
| barracuda | UDS | `/run/membrane/barracuda.sock` | — | ALIVE via UDS |
| coralreef | UDS | `/run/membrane/coralreef.sock` | 127.0.0.1:random | ALIVE via UDS |
| toadstool | UDS | `/run/membrane/toadstool.sock` | 127.0.0.1:random | ALIVE via UDS |
| nestgate | UDS+TCP | `/run/membrane/nestgate.sock` | 127.0.0.1:9500 | ALIVE via UDS |
| rhizocrypt | UDS | `/run/membrane/rhizocrypt.sock` | — | ALIVE via UDS |
| loamspine | UDS | `/run/membrane/loamspine.sock` | — | ALIVE via UDS |
| sweetgrass | UDS+HTTP | `/run/membrane/sweetgrass.sock` | 127.0.0.1:random (HTTP) | ALIVE via UDS |
| squirrel | UDS | `/run/membrane/squirrel.sock` | — | Socket connects, health silent |
| petaltongue | UDS | `/run/membrane/petaltongue.sock` | — | Socket connects, health silent |
| skunkbat | TCP-only | (no UDS in current binary) | 127.0.0.1:9140 | ALIVE via TCP |

**Socket path bridge**: `/run/membrane/*.sock` → symlinked to `/run/biomeos/*.sock`
and `/run/user/0/biomeos/*.sock` via `membrane-socket-bridge.service`.

**Firewall (ufw)**: Default deny incoming. Allows: SSH(22), DNS(53), HTTP/S(80/443),
Forgejo(2222), Songbird(3478/7700), TURN data(49152-65535/udp). Zero standalone
primal TCP ports exposed externally.

**Remaining for full UDS purity**:
- skunkBat binary needs rebuild with UDS support
- ~~sweetgrass `--http-address` defaults to `0.0.0.0:0`~~ **RESOLVED** — v0.7.51 defaults to `127.0.0.1:0`
- squirrel/petaltongue health probe framing investigation

### Track 5: Caddy Reverse Proxy Wiring — LIVE ✓

| Endpoint | Backend | Status |
|----------|---------|--------|
| primal.eco | Static response | **LIVE** (LE cert) |
| mesh.primal.eco | Songbird 10.116.0.3:7700 | **LIVE** (LE cert, reverse proxy) |
| auth.primal.eco | bearDog via socat bridge 10.116.0.3:9443 | **LIVE** (LE cert, JSON-RPC verified) |
| api.primal.eco | biomeOS via socat bridge 10.116.0.3:9444 | **LIVE** (LE cert, JSON-RPC verified) |
| nestgate.io | Forgejo via socat bridge 10.116.0.3:3001 | **LIVE** (LE cert, content serving) |

Cross-node proxy COMPLETE (Wave 79c). Three socat systemd bridge units on
golgiBody inner, firewall-locked to golgiBody-ext private IP only.

### Track 6: Lagging Codebase Parity (P2)

| Codebase | Gap | Action |
|----------|-----|--------|
| airSpring | Wave 60 → 78 (7d behind) | Trust pattern absorption, Wave 78 alignment |
| groundSpring | Wave 63 → 78 (6d behind) | Trust pattern absorption |
| songBird | 73% coverage (vs 90% target) | Coverage sprint — largest quantitative gap |
| hotSpring | Separate track, no root domain_profile.toml | Create root domain_profile.toml |
| ludoSpring | CONTEXT.md stale, no domain_profile.toml | Doc update + profile creation |
| neuralSpring | No domain_profile.toml | Profile creation |

### Track 7: Ongoing Evolution (P3)

| Work | Owner | Notes |
|------|-------|-------|
| biomeGate full NUCLEUS (9→13) | hotSpring + ops | PLANNED |
| northGate deployment planning | — | Heavy compute / AI |
| grapheneGate bootstrap | — | Portable trust anchor |
| Cloudflare → sovereign content cutover | cellMembrane | After Caddy wiring |

### Track 8: Post-Stadial Bloom — tideGlass (P3)

[protoKarya/tideGlass](https://github.com/protoKarya/tideGlass) — gen5-native
GPS sovereign rebuild for NF drug repurposing. First external consumer of
full NUCLEUS composition stack.

| Phase | Scope | Dependencies | Status |
|-------|-------|--------------|--------|
| 0. Archaeology | Zenodo artifact inventory | None | **ACTIVE** |
| 1. Reproduce | Python validation per module | nestGate (data fetch) | Pending |
| 2. Validate | Cross-validation vs primary sources | nestGate + provenance trio | Pending |
| 3. Rebuild sovereign | Rust modules, barraCuda shaders | Full primal mesh | Pending |
| 4. Package | pseudoSpore + lithoSpore + NF extension | All | Post-stadial |

**Deployment implications**: tideGlass Phase 1 will be the first real-world
validation that plasmidBin deployment pipeline -> NUCLEUS composition ->
primal UDS mesh can serve external science workloads. This is why the
cellMembrane/projectNUCLEUS ownership handoff for plasmidBin matters now.

---

## Sovereignty Shadow Status

| Track | Status | Next Step |
|-------|--------|-----------|
| S1 TLS | **LIVE** (sovereign LE on primal.eco + nestgate.io) | 5/5 Caddy endpoints LIVE |
| S2 NAT | **GRADUATED** | Complete |
| S3 Content | **LIVE** (nestgate.io → Forgejo via socat bridge) | Validate content rendering |
| S4 Auth | 7-DAY GATE ACTIVE (started Jun 2, ends ~Jun 9) | Wait → graduate |

---

## Active FRAGOs (Wave 82c — ownership reassigned)

| FRAGO | Owner | Status |
|-------|-------|--------|
| `wave73-westgate-skunkbat-enrollment` | wateringHole overwatch | **P1** — hardware-gated, 10G backbone LIVE |
| `wave79-transport-evolution-capability-routing` | songBird + biomeOS | **Phase 1 COMPLETE**, Phase 2 in progress |
| `wave80c-peptidoglycan-self-awareness` | cellMembrane | **P1** — self-refresh deployed, auto-fetch pending |
| ~~`wave79c-cross-node-proxy`~~ | cellMembrane | **RESOLVED** — 3 socat bridge units deployed, 5/5 endpoints LIVE |

---

## Upstream Gap Summary — ALL RESOLVED

| Gap | Status |
|-----|--------|
| ~~SB-TLS-01~~ | **RESOLVED** — Songbird direct-mode TLS crypto |
| ~~SB-TLS-02~~ | **RESOLVED** — Phase 3.5 Ed25519 relay verification |
| ~~BD-TRUST-01~~ | **RESOLVED** — Songbird `ec978b86` wires `auth.exchange_trust` into `mesh.init`. Zero-operator cross-gate trust seeding. |
| ~~RC-POLL-01~~ | **RESOLVED** — rhizoCrypt MeshEventListener polling wired |

**Zero P0/P1 upstream gaps.** All 13 primals VPS-ready. All headless regressions RESOLVED.
mesh.init ready — deploy refresh then `mesh.init` with gate peers.
primalspring_primal deprecated (Wave 80) — primalSpring composes primals via NUCLEUS.

---

*"The fastest teams wait for the slowest. The glacier moves as one."*
