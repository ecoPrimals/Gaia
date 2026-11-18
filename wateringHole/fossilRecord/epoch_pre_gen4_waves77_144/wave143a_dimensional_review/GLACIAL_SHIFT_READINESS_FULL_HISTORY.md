# Glacial Shift Readiness

**Status**: Active tracking document  
**Phase**: Interstadial exit → Stadial entry  
**Last updated**: 2026-07-15 (Wave 139c — **ALL 8 CRITERIA CLEAR. PUBLIC EXPOSURE LIVE. DEPOT FULLY HARVESTED.** 3 live surfaces: `primals.eco` (sporePrint), `primals.eco/footprint/` (GIS), `live.primals.eco` (TOPO-VIS). Cascade DAG converged (tree hashes). 36 fresh ecobins across 4 architectures (x86_64-musl, aarch64-musl, Windows, Android). Ed25519 signed. NCBI/PubChem drawbridge bonds shipped. cellMembrane error taxonomy refactored. Zero active divergences. wateringHole fossilized and cleaned.)

---

## Position

The ecosystem has cleared the interstadial exit gate. **PUBLIC + SOVEREIGN.**
3-gate WireGuard mesh (eastGate↔sporeGate↔golgi) with `live.primals.eco` and
`primals.eco/footprint/` serving public traffic. 13/13 primals at zero debt. Full
NUCLEUS deployed on eastGate, golgiBody VPS, ironGate (redeployed Jul 13, 13/13),
sporeGate (build authority + NUCLEUS). Depot pipeline 100% Rust with `require-signed`
enforced. Neural API authority: 12/12 COMPLETE. Transport injection at **11/11
non-exempt primals COMPLETE**. NUCLEUS supervision SHIPPED (biomeOS v4.17).
TCP-only fallback SHIPPED + ALL ADOPTED (grapheneGate 13/13 pending aarch64 rebuild).

**Deployment surface (ecoBin target matrix)**:
- `x86_64-unknown-linux-musl`: 14/14 depot fresh, LAN/VPS/WAN operational. **All gates fetch from VPS — no local rebuilds.**
- `aarch64-unknown-linux-musl`: **14/14 BUILT** (Wave 105 sweep complete, zero C-dep violations). CM-CHECKSUM-MULTI-TARGET RESOLVED (pipeline fix shipped).
- `aarch64-linux-android`: **UNBLOCKED** (aarch64-musl proven). NDK cross-compile pending. grapheneGate (Pixel 8) is the portable root of trust + gate spawner.
- `x86_64-pc-windows-msvc`: 0/14, future (Windows gates, named pipes IPC)
- `wasm32-wasi`: 0/14, design phase (browser/edge/embedded)

**POST-PRIMORDIAL DEPLOYMENT STANDARD**: peptidoglycan/VPS is the sole build authority.
All gates FETCH from `membrane.primals.eco/depot/`. `checksums.toml` reflects VPS output.
Local `cargo build --release` is for development/testing ONLY — never deployed to
`plasmidBin/primals/`. This is enforced, not advisory. Violating this breaks the
post-primordial deployment model and causes depot divergence.

**ZERO P1 blockers remain.** Both former P1s are RESOLVED:
1. ~~bearDog `aws-lc-rs`~~ → RESOLVED (Wave 145): `rustls-rustcrypto` pure Rust. All non-x86 targets UNBLOCKED.
2. ~~flockGate WAN depot empty~~ → RESOLVED (Wave 105): cellMembrane shipped `plasmid.fetch --source wan` + `caddy.depot.provision`. Production validation pending.

`PURE_RUST_CRYPTO_PURITY_STANDARD.md` published as ecosystem standard.

biomeOS v4.14 rebuilt by strandGate (LocalTrusted access level). `--graph-deploy`
revalidation pending on eastGate. S4 auth gate ending Jun 9. sourDough shipped
`validate depot`, `scaffold transport-kit`, and dep violation detection.

**Wave 52b milestone**: Full NUCLEUS live on eastGate — 13/13 primals from plasmidBin,
19/19 sockets alive, `plasmidbin doctor` 35/35 pass. primalSpring v0.9.30: 92 experiments
(21 tracks), certify 175/193, zero debt. Track 21 experiments: postPrimordial review (40/40),
cephalization plan (26/26), Tower CNS convergence (40/40). K-Derm topology + bonding model
standards published. sourDough v0.3.0 harvested. Deploy graph validation fragment-aware.
Provenance checksums regenerated (24 files, BLAKE3).

**Wave 54 milestone**: Provenance-elevated checksums shipped — `provenance.toml` (Layer 2
composite fingerprint), sweetGrass `braid.create` post-harvest, `plasmidbin verify-provenance`
subcommand. primalSpring consumer tooling rewired. Full temporal/glacial/ecological review
completed (`TEMPORAL_ECOLOGICAL_REVIEW_MAY27_2026.md`). VPS NUCLEUS critical path mapped:
zero mountain debt blocking, `deploy_membrane.sh --composition nest` ready, NestGate v0.5.0
unified. cellMembrane deployment sprint is the sole remaining gate.

**Provenance pipeline live**: 3 primals (loamSpine, toadStool, Songbird) harvested with
full `provenance.toml` fingerprints (May 27). `rustc_version = "1.95.0"`, source commits
verified. Provenance-elevated checksums confirmed operational in CI.

**Wave 61 sovereign shadow functions** (May 29): `membrane-shadow` Rust crate replaces
bash VPS control scripts. Typed APIs for Forgejo repo/mirror management (`content.repo.*`,
`content.mirror.*`), token lifecycle (`auth.token.*`), systemd service control
(`gate.service.*`), and gate management (`gate.info`, `gate.pull`, `gate.check`).
Capability registries aligned across nestGate, bearDog, and biomeOS. Forgejo pull mirrors
operational for all 38 repos. Temporal sync spec published. Ecosystem standardization
audit: stale remotes cleaned, duplicate repos removed, branch naming normalized. 13/14
upstream Neural API methods shipped by primal teams.

**Wave 62 temporal sync operational** (May 30): waterFall temporal sync implemented in
Rust (`temporal.rs` — typed multi-remote DAG sync, `manifest.rs` — ecosystem manifest
reader replacing Python tomllib, `identity.rs` — capability-based gate detection).
5 Forgejo mirrors converted to bidirectional repos (biomeOS, coralReef, sweetGrass,
squirrel, wateringHole). `membrane temporal.cascade` now handles temporal sync (Rust,
replaces bash `cascade-pull.sh`). Deep debt sprint: shell injection fix in
`token_create`/`token_revoke`, hardcoded paths→`ShadowConfig`, `unreachable!()`→`Result`,
magic numbers→named constants. Manifest bumped to v2.1.0 (Wave 62). 10 handoffs archived.

**Wave 63 K-Derm diderm deployment** (May 30): Three-node VPS envelope physically
deployed. golgiBody (inner membrane, [RELAY_PUBLIC]): Forgejo + NUCLEUS, workspace cleaned
80%→66%. peptidoglycan (structural, [RELAY_PUBLIC]): 2-vCPU/4GB/80GB, Rust 1.96, Zola 0.22.1,
39-repo workspace, membrane binary, temporal sync hub. golgiBody-ext (outer membrane,
137.184.197.151): Caddy 2.11.3, sporePrint live (HTTP 200, 143 pages). Cross-node SSH mesh.
ecosystem_manifest.toml v2.2.0 with `[topology]` section and three new gate profiles.
`GATE_SETUP_STANDARD.md` published — standardizes physical gate and VPS proto-fieldMouse
setup, sync, resync. `gen5/KDERM_DIDERM_APPLICATION.md` documents bonding interactions
per boundary. Cost: $48/mo for complete sovereign diderm envelope.

**Wave 63+ waterFall Phase 4 inversion + K-Derm bonding enforcement** (May 31):
Forgejo-primary push model deployed with proper K-Derm diderm relay chain.
`push_target = "forgejo"` in manifest — gates push to Forgejo only. Diderm relay
chain wired: `pepti-sync-relay.sh` on peptidoglycan mediates metallic→ionic bond;
`ext-github-push.sh` on golgiBody-ext (trans face) ships to GitHub (weak bond).
GitHub SSH write credentials moved exclusively to golgiBody-ext (outer membrane).
`topology.roles` added to manifest declaring per-layer function assignments.
Push mirror API in membrane-shadow (`mirror.push-create/list/sync`), `temporal.sync`
respects `push_target`. Post-receive impulse relay + cascade graphs created.
`EXTERNAL_LEDGER_STANDARD.md` published. Bond-type violation resolved:
proper covalent→metallic→ionic→weak degradation through the diderm envelope.

**Transport evolution roadmap published** (May 31): `gen5/TRANSPORT_EVOLUTION_NANOWIRE_TO_QUORUM.md`
documents the path from SSH-triggered relay (nanowire) to timer-based autonomous sensing
(quorum Phase 1) to songbird mesh relay (Phase 2) to capability-routed quorum (Phase 3).
Current relay chain validated by flockGate (WAN, ~3s propagation) and ironGate (LAN covalent
backbone). biomeGate (async hardware cadence) serves as air-gap validation loop.

**Mountain blurb responses absorbed** (May 27):
- toadStool S279: zero production panic paths, 9,156+ lib tests, handoffs archived
- Songbird W53b: +74 tests (8,070 total), deep debt zero confirmed, `forbid(unsafe_code)` all crates
- biomeOS v3.76: LiveSpore `~/.local/bin` already fixed (eddc3fd2)
- loamSpine W55: BearDog coupling removed, placeholder DIDs replaced, self-knowledge enforced

**Glacial Shift Wave Plan published**: 3-phase roadmap (Waves 53–55+) at
`GLACIAL_SHIFT_WAVE_PLAN.md`. Team handoffs distributed to `handoffs/`:
- Wave 53: Primal mountains — **RESOLVED** (12/13, SouthGate ops carries to W54)
- Wave 54: Deployment + cellMembrane (gate redeploy, VPS Nest, sovereign DNS, K-Derm wire) + **provenance elevation**
- Wave 55+: Springs launch + cross-gate NUCLEUS (proto-nucleate deployment, capability routing)

**Wave 51 milestone**: Songbird `discovery.peers` resolution + outer membrane hardening.

- **plasmidBin full Rust elevation** — all 20 bash scripts replaced by a single
  `plasmidbin` Rust CLI binary (`validate`, `harvest`, `fetch`, `doctor`,
  `deploy`, `start`, `stop`, `launch`). Dynamic harvest driven from `sources.toml`
  with `binary_name` and `build_args` fields — single-point primal onboarding.
  Checksum sync pipeline fixed (split `git add` for gitignored dirs). Release
  smoke test bash substitution bug fixed. biomeos (`biomeos-cli`) and skunkbat
  (`-p skunk-bat-server`) binary naming resolved. Release tags: v2026.05.25,
  v2026.05.26.
- **CI cost optimization** — daily full-sweep cron removed. New `check-updates.yml`
  does daily lightweight tag check (~1 min) and selectively dispatches harvest
  only for stale primals. Weekly Monday full sweep retained. Spending cap set
  at $100/month.
- **GitHub Actions outage (May 26)** — critical incident (authentication cascade,
  workflow triggers silently dropped). CI/CD pipeline went dark. All inner membrane
  components unaffected: 4 NUCLEUS instances running, Songbird mesh live, local
  `plasmidbin` CLI operational. Outage documented in
  `whitePaper/gen4/architecture/THE_GOLDEN_CAGE.md`.
- **cellMembrane self-hosted runners handoff** — issued during outage. Requires
  2+ LAN gates with lockout prevention. Forgejo-as-primary evolution path
  documented. See `handoffs/CELLMEMBRANE_SELF_HOSTED_RUNNERS_WAVE50_MAY26_2026.md`.
- **primalSpring wateringHole fossilized** — 42 files (7 standards, 2 living
  handoffs, 32 archived) moved to `fossilRecord/springs/primalSpring/wateringHole_wave50_may2026/`.
  Local `wateringHole/` replaced with pointer stub to `infra/wateringHole/`.
- **THE_GOLDEN_CAGE.md** — gen4 architecture paper written. Documents dependency
  audit (7 infrastructure cage bars + science stack cage), chrysalis thesis
  (bootstrap sequence from cage to sovereignty), evolution order (8 steps from
  self-hosted runners to barracuda science parity). Forgejo positioned as
  sovereignty baseline before NUCLEUS absorbs forge capabilities.

**Wave 47 milestone**: 13/13 behavioral convergence — all primals accept
`--socket`, return `{"status":"alive"}` from `health.liveness`, handle
SIGTERM+SIGINT, and implement `lifecycle.status`.

**Wave 48 milestone**: Covalent spring mesh — **all 8/8 springs sounded off**.
4 gates operational with NUCLEUS + Songbird TCP :7700 federation.

**Wave 49 milestone**: Post-primordial + ecosystem tightening. plasmidBin-only
deployment enforced across all launchers. 8/8 primal showcases fossilized
(barraCuda, bearDog, loamSpine, petalTongue, rhizoCrypt, skunkBat, sweetGrass,
toadStool). 7 primals responded with tightening handoffs same-day (rhizoCrypt,
Songbird, biomeOS, coralReef, sweetGrass, toadStool, bearDog). Songbird wired
`mesh.init` with `bootstrap_peers` for cross-gate TCP discovery. rhizoCrypt
fixed startup latency (was >8s, pipeline debt item). bearDog Wave 113b:
orphan purge — cloud KMS/mobile HSM/PKCS11 discovery code removed (~15k LOC),
method count drift fixed (127). toadStool: orchestrator dispatch tests added,
Unix socket improvements. primalSpring: 789 tests, 53 scenarios, 458 methods,
95 deploy graphs, superseded specs archived, metric drift fixed across 15+ docs.

**Climate-sensitive sentinels** (primals whose readiness gates the glacial shift):

- **Songbird**: **MESH LIVE** (Wave 101). P1 fix (03f23d45+aebe271f) resolved TLS/UDS routing
  + HTTP fallback. eastGate↔strandGate bidirectional mesh 17h+ stable. Auth hardening +
  network detection shipped. ipc.resolve M1 (topology-aware routing) is P2 next.
  **CLEAR for stadial** — mesh operational.
- **bearDog**: **P1 RESOLVED** (Wave 145). `aws-lc-rs` → `rustls-rustcrypto` (pure Rust).
  `cargo check --target aarch64-unknown-linux-musl` PASS. 19-crate C-crypto ban in `deny.toml`.
  `PURE_RUST_CRYPTO_PURITY_STANDARD.md` published. ACME renewal operational. Transport adopted.
  S4 auth gate ending Jun 9. All non-x86 ecoBin targets UNBLOCKED.
  **CLEAR** — zero sentinel-blocking items.
- **toadStool**: **S279 deep debt III complete** — zero production panic paths, 9,156+ lib tests.
  Transport CONFIRMED DONE (S306c Wave 104, 11/11 non-exempt).
  **CLEAR** — zero sentinel-blocking items.
- **biomeOS**: **v4.18** shipped (TCP-only fallback, grapheneGate adoption). v4.17 (NUCLEUS supervision —
  LifecycleManager auto-restarts). LocalTrusted access level operational.
  **CLEAR** — zero sentinel-blocking items. Both P1 items (supervision + TCP fallback) RESOLVED.
- **petalTongue**: WASM client-side rendering live. Transport evolution adopted.
  **CLEAR** — no remaining sentinel-blocking items.

**Upstream leads, downstream lags**: Primals on the mountain (bearDog, Songbird,
toadStool, NestGate, biomeOS) are tightened and ready to push through the gate.
Springs lag on cleanup (neuralSpring still has stale `target/release/` hardcode,
hotSpring absorbed Wave 50 post-primordial mandate — NUCLEUS launched on biomeGate,
plasmidBin-only enforced, pseudoSpore v1.5.0 GuideStone-grade). The shift moves when
the sentinels clear — springs follow.

**LAN is live** — Cat6 1G backbone on unmanaged switch connects all gates.
10G (switch + NICs installed, Cat6a cables pending) is an elevation goal for
Tier 2+ large-dataset science, not a deployment blocker.

---

## Readiness Matrix

### Sovereignty Shadows (H2)

| Track | What | Sovereign | Commercial | Status | Cutover gate |
|-------|------|-----------|------------|--------|--------------|
| **S1** | TLS termination | Caddy+LE :443 (80ms TTFB) | Cloudflare (INACTIVE) | **VERIFIED** — 198 probes, 0 failures, p95 < 120ms. Awaiting NS cutover. | p95 < 500ms, 0 TLS failures |
| **S2** | NAT relay | Songbird TURN :3478 | cloudflared (INACTIVE) | **GRADUATED** | 7-day 100% reachable |
| **S3** | Content serving | NestGate + petalTongue (67ms TTFB) | GitHub Pages (111ms) | **READY** — sporePrint 101 tests, zero-C deps. Cutover after DNS NS switch. | 7-day TTFB parity |
| **S4** | Auth | BearDog BTSP enforced | OAuth2/PAM (DISABLED) | **7-DAY GATE COMPLETE** (started Jun 2, ended Jun 9). BTSP production mode LIVE on grapheneGate. Review: PASS. | 7-day p95 < 50ms |

**S4 GRADUATED** (Jun 9). All 4 sovereignty shadows are now sovereign on the inner membrane. DNS NS cutover complete (Jun 4). S1 graduation (Cloudflare removal from outer membrane) is the next sovereignty evolution.

### cellMembrane (inner membrane)

| Component | Status |
|-----------|--------|
| VPS ([RELAY_PUBLIC], DO nyc1) | **OPERATIONAL** |
| Channel 2: Songbird TURN relay | **LIVE** |
| Channel 2b: RustDesk hbbs/hbbr | **LIVE** |
| Channel 3: TLS surface (Caddy + ACME) | **LIVE** |
| Tower composition (BearDog + Songbird + SkunkBat) | **DEPLOYED** |
| Nest expansion (rhizoCrypt + loamSpine + sweetGrass) | **OPERATIONAL** (since May 28) — all 4 services active, ports verified |
| Sovereign shadow functions (membrane-shadow) | **OPERATIONAL** (Wave 65) — 12 Rust modules: dispatch, cli, temporal, impulse, context, plasmid, git_ops, forgejo, gate, config, manifest, identity. `plasmid.fetch` + `temporal.cascade` fully Rust. |
| Forgejo repos (5 bidirectional + 33 mirrors) | **OPERATIONAL** (Wave 62) — biomeOS/coralReef/sweetGrass/squirrel/wateringHole push-enabled |
| waterFall temporal sync | **LEVELED** (Wave 84) — git 60s timeouts, CWD resolution, merge-ff policy. 38/38 repos in ~59s. Tree-parity auto-resolution. Manual git loops DEPRECATED. |
| Channel 1: Sovereign DNS (knot-dns) | **PROPAGATED** (Jun 4) — `primal.eco` DNS LIVE on public resolvers (8.8.8.8, 1.1.1.1) + TLS cert obtained (LE). `nestgate.io` propagating (SERVFAIL on public resolvers, expected). `primals.eco` stays Cloudflare (outer membrane per diderm model). 3 zones, ns1+ns2, DNSSEC all active. |
| Caddy → BearDog ACME replacement | Shadow live, **not cut over** |
| BearDog Vault (encrypted creds at rest) | **PLANNED** (Phase 2) |

### LAN Gate Deployment

| Gate | Hardware | Role | NUCLEUS status | Springs | LAN |
|------|----------|------|----------------|---------|-----|
| **eastGate** | i9-12900, RTX 4070 + Akida, 32GB | Orchestrator, neuromorphic | **FULL NUCLEUS** (13/13, Wave 98) | primalSpring, airSpring, groundSpring | 1G |
| **ironGate** | i9-14900K, RTX 5070, 96GB | Agentic dev, ABG | **OPERATIONAL** (23 UDS) | primalSpring, ludoSpring, healthSpring | 1G |
| **southGate** | 5800X3D, RTX 4060 + 3090s, 128GB | Gaming + compute | **OPERATIONAL** (9/9) | wetSpring, neuralSpring | 1G (10G NIC ready) |
| **biomeGate** | Threadripper 3970X, 256GB | HBM2 test bench | **OFFLINE** (kernel recovery) | hotSpring | 1G |
| **strandGate** | Dual EPYC 7452 (64c), 256GB ECC | Bioinformatics + compute trio pickup | **ACTIVE** (Wave 72) — barraCuda + coralReef SPIR-V | wetSpring (secondary) | 1G |
| **northGate** | Ryzen 9950X3D, RTX 5090, 96GB | Gaming primary, heavy compute | Hardware ready, **not deployed** | — | 1G (10G NIC ready) |
| **westGate** | i7-4771, RTX 2070 Super, 32GB | 76TB ZFS cold storage | **INCOMING** (ETA this week) | — | 1G (10G NIC ready) |
| **swiftGate** | Ryzen 5800X, RTX 3070, 64GB | Mobile/compact | Hardware ready | — | 1G |
| **flockGate** | i9-13900K, RTX 3070 Ti, 64GB | Remote covalent (WAN) | **OPERATIONAL** (Wave 64) — WAN relay validated (~1.3s Forgejo, ~3s end-to-end), pseudoSpore gallery, Zola 226 pages/746ms | sporePrint | WAN via cellMembrane |
| **kinGate** | i7-6700K, RTX 3070, 32GB | Staging | Hardware ready | — | 1G |

**Covalent mesh order** (over existing 1G LAN):
1. ~~Enable `SONGBIRD_FEDERATION_PORT=7700` on eastGate + ironGate + southGate + biomeGate~~ **DONE** (Wave 48)
2. ~~Peer seeding mechanism~~ **DONE** (Wave 49) — `SONGBIRD_PEERS` env + `--peers` CLI + `mesh.init` RPC
3. ~~Springs declare gates, deploy cells, cut primordial patterns~~ **DONE** (4/4 responding springs confirmed)
4. ~~Verify cross-gate `discovery.peers`~~ **COMPLETE** (Wave 92) — eastGate ↔ strandGate bidirectional, peer_count:1, sub-ms
5. ~~Cross-gate `capability.call` smoke test~~ **COMPLETE** (Wave 92) — routes through mesh, local resolution takes precedence
6. ~~Cross-subnet routing for southGate (192.168.4.x)~~ **VALIDATED** (Wave 107) — Eero bridge, 4.7ms, mesh.init works natively
7. westGate (INCOMING — Nest Atomic cold storage), northGate (Node Atomic) — hardware gated
8. ~~Plasmodium collective validation (3+ gates meshed via live `capability.call`)~~ **DONE** (Wave 107) — 4-gate collective, 19/22 capability domains resolved on southGate

### Deployment Matrix (primalSpring)

| Cell | Status |
|------|--------|
| `tower-x86-homelan-uds` | **PASS** (golden path) |
| `full-x86-homelan-uds` | **PASS** (Wave 98) — 13/13 primals, 12/12 IPC liveness, 12/12 readiness |
| `lithospore-x86-vm-uds` | **PASS** |
| `nucleus-aarch64-mixed-tcp` | **BUILT** (14/14 aarch64-musl, Wave 105 sweep complete). NDK android target next. |
| `graph-deploy-x86-uds` | **VALIDATED** (Wave 105) — biomeOS v4.16 composition.deploy accepted, graph.status 13 phases, LocalTrusted works. |
| `benchscale-ipc-x86-uds` | **PASS** — 12/12 liveness, 12/12 readiness, 12/12 capabilities (with depot rebuild) |
| `pixel-tower-aarch64-tcp` | **BUILT** (aarch64-musl 14/14). All 13 handlers wired. NDK android cross-compile next for Pixel deploy. |
| `wan-flockgate-deploy` | **UNBLOCKED** (Wave 105) — WAN depot SHIPPED (`plasmid.fetch --source wan`). Production deploy + validation pending. |
| 37 other cells | **UNTESTED** |

**P0 target**: `nucleus-x86-mixed-uds` — full NUCLEUS over LAN. **ACHIEVED** (Wave 98).

### Distributed Covalent (Phase 4)

| Item | Status |
|------|--------|
| Family seed + bootstrap tooling | **READY** |
| cellMembrane VPS rendezvous | **OPERATIONAL** |
| Songbird TCP/WAN fallback | **SHIPPED** (Wave 213-214) |
| Songbird TCP federation on LAN | **LIVE** — 4 gates with :7700 (Wave 48) |
| Rust `nucleus_launcher` `--federation-port` | **SHIPPED** — Wave 48 |
| NAT traversal (STUN/punch/TURN) | Shipped, **not field-tested** on residential NAT |
| toadStool yield-to-owner dispatch | **ENFORCED** (S274 + S275 orchestrator tests) |
| Cross-gate data dependency staging | **PROTOTYPED** (primalSpring `validation::dependency`) |
| Songbird peer seeding (`SONGBIRD_PEERS`) | **SHIPPED** — Wave 49, both launchers, CLI + env + RPC |
| Songbird `mesh.init` + `bootstrap_peers` | **WIRED** — Wave 49, Songbird team confirmed functional |
| Cross-gate `discovery.peers` verification | **COMPLETE** (Wave 92) — bidirectional, both gates report peer_count:1, quality:1.0 |
| Cross-subnet mesh (southGate ↔ eastGate) | **VALIDATED** (Wave 107) — 192.168.4.29↔192.168.1.144 via Eero bridge, 4.7ms, 2 direct peers, 13/13 alive, 19/22 capabilities |
| Plasmodium collective status | **4-GATE COLLECTIVE LIVE** (Wave 107) — eastGate↔golgiBody↔ironGate+southGate. Deterministic deployment codified (gate.bootstrap 6/6). Mesh persistence SHIPPED. NUCLEUS supervision SHIPPED. |
| biomeOS graph.deploy orchestration | **VALIDATED** (Wave 105) — `composition.deploy` accepted, graph.status 13 phases, LocalTrusted. biomeOS v4.18 (TCP fallback + supervision). |
| Full NUCLEUS 13/13 IPC-live | **COMPLETE** (Wave 98+) — eastGate 23 JSON-RPC + 3 tarpc. golgiBody 13/13. ironGate 12/13. southGate 13/13. |
| Pixel 8 / grapheneGate | **13/13 DEPLOYED AND ALIVE** (Wave 108) — all primals TCP-only on Pixel 8a. First cross-arch full NUCLEUS. BTSP E2E and mesh enrollment pending. |
| benchScale IPC compliance | **OPERATIONAL** (Wave 99) — validates liveness/readiness/capabilities across live NUCLEUS |
| flockGate WAN deployment | **4/5 PASS** (Wave 105) — WAN fetch + NUCLEUS launch + mesh.init + health OK. VPS depot refreshed (songbird + biomeOS rebuilt). Awaiting flockGate power-on for 5/5. |

### Wave 49 Ecosystem Issues (post-tightening re-audit, May 25)

| Issue | Reporter | Status |
|-------|----------|--------|
| loamSpine Tokio panic on health probe | wetSpring, neuralSpring | **UPSTREAM** — does not block mesh |
| rhizoCrypt slow startup (>8s) | wetSpring | **FIXED** Wave 49 — `announce_to_biomeos()` off critical path |
| sweetGrass/toadStool slow startup (>8s) | wetSpring | **KNOWN** — cold-start timing, not blocking |
| Songbird sled DB corruption (unclean) | neuralSpring | **RESOLVED** Wave 51b — auto-cleanup of orphaned sled DB artifacts on startup (sled removed in Wave 135, artifacts persisted). |
| ~~biomeOS LiveSpore deploys to `~/.local/bin`~~ | re-audit | **RESOLVED** — v3.76 commit eddc3fd2, target → `plasmidBin/primals/` |
| ~~toadStool local wH unarchived~~ | re-audit | **RESOLVED** — S278b: handoffs archived, debris cleaned |
| Central fossilRecord incomplete | re-audit | **NARROWED** — primalSpring wH archived Wave 51; remaining primals' local docs still sparse |
| GitHub Actions outer membrane dependency | primalSpring (Wave 51) | **HANDOFF ISSUED** — cellMembrane self-hosted runners; Forgejo-primary evolution path |
| plasmidBin metadata version drift | re-audit (Wave 51) | **HYGIENE** — manifest.toml (v5.5.0), checksums.toml (Wave 35), sources.toml (Apr 14) lag README (v5.6.0) |

**Resolved** (fossilized): Ionic bond runtime (WS-1), biomeOS mesh dispatch,
BearDog ACME renewal daemon, rhizoCrypt startup latency, Songbird `--security-socket`,
stale socket cleanup, 8/8 showcase fossilizations, cross-subnet routing, neuralSpring
petalTongue hardcode, hotSpring Wave 50 absorption, petalTongue `--family-id`,
ludoSpring GAP-01 coralReef, `discovery.peers` RPC wiring (Wave 49 — `mesh.init` +
`bootstrap_peers` functional; **RESOLVED Wave 51** — mesh+registry merge shipped), primalSpring wateringHole fossilized (Wave 51, 42 files to
fossilRecord) — see `fossilRecord/` for detail.

### Software Remaining

| Item | Owner | Priority | Status |
|------|-------|----------|--------|
| ~~Cross-gate `discovery.peers` live test~~ | primalSpring | ~~HIGH~~ | **DONE** (Wave 92) |
| ~~Cross-gate `capability.call` live test~~ | primalSpring | ~~HIGH~~ | **DONE** (Wave 92) |
| ~~SB-TLS-LAN-01: songbird TLS handshake~~ | songBird + bearDog | ~~P1~~ | **RESOLVED** (Wave 101, 03f23d45) — UDS routing fixed, HTTP fallback wired |
| ~~SB-SECURITY-URL-01: songbird security URL format~~ | songBird | ~~P1~~ | **RESOLVED** (Wave 101, 03f23d45) — UDS socket path used directly |
| ~~DNS NS registrar cutover~~ | operator | ~~HIGH~~ | **DONE** — `primal.eco` + `nestgate.io` propagated + TLS live. DNSSEC enabled. |
| ~~coralReef capabilities.list~~ | coralReef | ~~LOW~~ | **DONE** (Wave 101, 15d1702) — capabilities.list alias shipped |
| ~~bearDog aws-lc-rs C-dep~~ | bearDog | ~~P1~~ | **RESOLVED** (Wave 145) — `aws-lc-rs` replaced with `rustls-rustcrypto` (pure Rust). `cargo check --target aarch64-unknown-linux-musl` PASS. 19-crate C-crypto ban in `deny.toml`. All non-x86 targets UNBLOCKED. |
| ~~flockGate WAN depot empty~~ | cellMembrane | ~~P1~~ | **RESOLVED** (Wave 105) — `plasmid.fetch --source wan` SHIPPED. `caddy.depot.provision` ready. Production validation pending. |
| ~~songBird ipc.resolve M1~~ | songBird | ~~**P2**~~ | **SHIPPED** (Wave 107, ff86204c) — `ipc.resolve` returns MeshRelay TransportEndpoint with peer_id. Topology-aware mesh routing LIVE. |
| ~~Transport injection (toadStool)~~ | toadStool | ~~P2~~ | **DONE** (S306c Wave 104) — transport CONFIRMED, 11/11 non-exempt COMPLETE. |
| ~~biomeOS graph.deploy revalidation~~ | biomeOS + eastGate | ~~P2~~ | **VALIDATED** (Wave 105) — v4.16 composition.deploy accepted, graph.status 13 phases, LocalTrusted. |
| ~~CM-CASCADE-CONFLICT~~ | cellMembrane | ~~P2~~ | **RESOLVED** (Wave 105) — cascade auto-discards dirty regenerable metadata before ff-only pull. |
| CM-VPS-DEPOT-SYNC | cellMembrane | **P2** | golgiBody inner→outer membrane binary flow for WAN depot. |
| ~~CM-CHECKSUM-MULTI-TARGET~~ | cellMembrane | ~~P2~~ | **RESOLVED** (Wave 105) — read-modify-write for multi-target checksums.toml shipped (commit 3a1900b). |
| ~~CM-DEPOT-DIVERGENCE~~ | eastGate | ~~P2~~ | **RESOLVED** (Wave 105c) — was self-inflicted: local rebuilds violated post-primordial standard. Fixed by re-fetching 13/13 from VPS. Standard now enforced. |
| ~~Cross-subnet routing (southGate ↔ eastGate)~~ | infra/network | ~~MEDIUM~~ | **VALIDATED** (Wave 107) — Eero bridge works natively, 4.7ms, no TURN needed |
| ~~grapheneGate UDS adaptation~~ | primalSpring (parallel) + upstream | ~~P2~~ | **ALL ADOPTED** (Wave 107) — all 13 primals shipped `bind_transport()`. Awaiting aarch64 rebuild + redeploy. |
| ~~aarch64 cross-compilation~~ | cellMembrane | ~~P2~~ | **COMPLETE** (Wave 105) — 14/14 aarch64-musl built, zero C-dep violations. NOTE: sweep overwrote x86_64 checksums (CM-CHECKSUM-MULTI-TARGET). |
| ~~ironGate mesh enrollment~~ | ironGate + cellMembrane | ~~P2~~ | **VALIDATED** (Wave 106) — 3rd mesh node. gate.bootstrap 6/6 PASS, 12/13 alive, VPS relay mesh. |
| Windows ecoBin (x86_64-pc-windows-msvc) | future | **LOW** | Named pipes IPC, MSVC target. Design phase. |
| wasm32-wasi ecoBin | future | **LOW** | Browser/edge/embedded. Design phase. |
| benchScale Docker image tag fix | benchScale | **LOW** | Topologies use bare `ubuntu` tag — needs `ubuntu:24.04` |
| Forgejo Actions CI | projectNUCLEUS | LOW | Evaluation planned (P2) |
| Central fossilRecord sync | all primals | LOW | 7/8 primals reference central paths that don't exist yet |

**Resolved since Wave 68**: loamSpine Tokio panic, rhizoCrypt discovery hardening,
sweetGrass PROV-O parity, bearDog ring eliminated (aws-lc-rs retained — C-dep still present),
Songbird sled removed, biomeOS L4 routing + topology affinity, cellMembrane relay bash→Rust,
VPS membrane binary deployed, S4 auth ACTIVATED, SB-TLS-LAN-01 RESOLVED (Wave 101),
SB-SECURITY-URL-01 RESOLVED (Wave 101), barracuda sourdough-core dep REMOVED (Wave 101),
rhizoCrypt sourdough-core dep REMOVED (Wave 101), coralReef capabilities.list SHIPPED (Wave 101),
bearDog transport adoption DONE (Wave 103), loamSpine transport confirmed (Wave 103),
biomeOS v4.14 rebuilt (Wave 103), depot 14/14 fresh x86_64-musl (Wave 103).

**Previously resolved**: Ionic bond runtime, biomeOS mesh dispatch, BearDog ACME,
rhizoCrypt startup latency, Songbird `--security-socket`, stale socket cleanup,
8/8 showcase fossilizations, sovereign DNS infra — see `fossilRecord/`.

---

## Glacial Shift Criteria (Revised — Diderm Membrane Architecture)

The glacial shift (stadial entry) is reached when the following 7 criteria
are met. **Revised Wave 77b** (criteria 1-6) + **Wave 109** (criterion 7): the
inner membrane (`primal.eco`) must be fully sovereign; the outer membrane
(`primals.eco`) may use commercial services (Cloudflare). See
`DIDERM_DOMAIN_ARCHITECTURE.md` for the full trust barrier model.

| # | Criterion | Revised Meaning |
|---|-----------|----------------|
| 1 | Sovereignty shadows graduated (inner membrane) | S1-S4 on the `primal.eco` data path. Outer membrane may retain commercial TLS. |
| 2 | Multi-gate LAN mesh operational (3+) | Songbird mesh on inner membrane. eastGate + strandGate + westGate (or substitute). |
| 3 | Peptidoglycan replicable | Can be torn down and redeployed from `membrane.toml`. Trust barrier tested. |
| 4 | Remote covalent node over WAN | Via inner membrane only (Songbird TURN through peptidoglycan). |
| 5 | DNS sovereign for inner membrane | `primal.eco` + `nestgate.io` on knot-dns. `primals.eco` on Cloudflare is acceptable. |
| 6 | Inner membrane zero-commercial + cross-validation | Zero commercial services in `primal.eco` data path. Dual-path cross-membrane validation operational. |
| 7 | guideStone-grade deployment across all gates | All NUCLEUS deployments satisfy 5 guideStone properties: deterministic, reference-traceable, self-verifying, environment-agnostic, tolerance-documented. Functionally identical from VPS authority. Standard startup contract, gate profiles, health endpoints, named tolerances. |
| 8 | Outer membrane hardened for public exposure | Security headers deployed (HSTS, CSP, X-Frame-Options). darkforest v3.0 outer scope PASS. Failover scenarios RF-01–RF-05 validated. Zero CRITICAL exposures. Certificate lifecycle automated. Pen test cadence established. |

**Key change from pre-Wave 77b**: Criterion 6 no longer requires
Cloudflare removal from the outer membrane. Instead, it requires cross-
membrane validation — the inner membrane acts as the ground truth
validator for content served by the outer membrane.

**Criterion 7 (Wave 109)**: Added to codify the requirement that deployment itself must
be guideStone-grade — not just "working" but deterministic, traceable, self-verifying,
environment-agnostic, and tolerance-documented. FRAGO: `wave109-guidestone-deployment-convergence`.

**Criterion 8 (Wave 136)**: Added after the warming event (public DNS exposure). Stadial
criteria 1-7 prove the system *works* internally. Criterion 8 proves it *survives* externally.
Triggered by: DNS cutover to sovereign Caddy, AI crawler enablement, 301-page sitemap
indexed. Sprint: `handoffs/SECURITY_EXPOSURE_SPRINT_WAVE136.md`.

**Current assessment (Wave 137b)**: **PUBLIC + SOVEREIGN. PHASE 1 COMPLETE.** Two public surfaces live: `primals.eco` (sporePrint + footPrint SPA) and `live.primals.eco` (petalTongue TOPO-VIS dashboard — 7 mesh peers, SSE live push, TLS/HTTP2). Neural API deployment authority 12/12 complete. Depot trust chain fully enforced: `require-signed` system-wide, Ed25519 + BLAKE3 via native `membrane depot.integrity`. 2,801 lines of bash fossilized (6 scripts retired, 14 evolution targets identified). songBird drawbridge weak bond pattern formalized as K-Derm ion channel model. footPrint API abstraction layer complete (58 tests, zero raw fetch). Forgejo full-depth (21 repos, permissions fixed). 3-gate WireGuard mesh: eastGate (35ms) + sporeGate (71ms) + golgi bidirectional. flockGate WAN data plane proven (JupyterHub relay 202ms).

**Criteria 1-7: ALL CLEAR** (unchanged since Wave 111). **Criterion 8: MET (5/5 sub-criteria)** — security headers, 404 fix, fail2ban, CSP, rate-limiting all deployed and validated live. SIGN-01 cascade signing now LIVE (`require-signed` enforced). SIGN-VERIFY-ON-FETCH implemented in cellMembrane (`89bf12f`). darkforest v3.0 confirms posture. **ALL 8 CRITERIA CLEAR FOR STADIAL ENTRY.**

**Previous assessment (Wave 136b)**: HARDENED. WARMING EVENT CONTAINED. DNS cutover complete. 9/14 exposure items closed within hours. Outer membrane posture validated.

**Risk posture**: Warming event contained. All critical and high-priority exposures patched. Cooling sprint continues on 4-week cadence (136b-d). Acceptable residual: GitHub trailing shadow (EXP-08), VPS provider risk (EXP-09), registrar (EXP-10, DNSSEC mitigates), AI crawlers (EXP-11, intentional). Theoretical: physical, cryptographic, dark-forest beacon — defenses exist. **ALL 8 CRITERIA CLEAR FOR STADIAL ENTRY.**

**Previous assessment (Wave 133d)**: ZERO P1. 5-GATE MESH + WAN OVERLAY LIVE (eastGate↔golgi↔ironGate+southGate + grapheneGate, WireGuard overlay flockGate↔sporeGate). 1098 tests, 125 scenarios, 0 fail in primalSpring — composition subtypes landed. songBird drawbridge auto-advertisement evolved (coded, tested, pending pepti rebuild). WAN-DISPATCH-01 transport proven (72ms p50 RTT via mesh http.request), capability.call routing unblocked by songBird evolution. sporePrint NUCLEUS deployed on golgi (212 pages). Criteria 1-7 status: ALL CLEAR for stadial entry. Operational proof exercises pending: WAN-DISPATCH-01 FULL PASS (post pepti rebuild), strandGate enrollment, grapheneGate 13/13 from fresh pepti. SHOW_HN publication rubric (4 categories, 28 criteria) established as external stadial proof event.

**Previous assessment (Wave 111)**: ZERO P1. 5-GATE ECOSYSTEM LIVE (eastGate↔golgiBody↔ironGate+southGate + grapheneGate). ironGate NUCLEUS DEPLOYED (13/13 systemd, benchScale validated). Criterion 7 COMPLETE — guideStone-grade deployment achieved (HEALTH-01 13/13, startup 6/6, deterministic, reference-traceable, self-verifying). riboCipher 9/9 CONVERGED — all primals signal transport intent. Criteria 1-7 status: ALL CLEAR for stadial entry.

**Wave 98-103 milestones**:
- Full NUCLEUS 13/13 on eastGate, all IPC-live (12/12 liveness, 12/12 readiness, 12/12 capabilities with coralReef depot fix)
- `nucleus-deploy --graph-deploy` flag ships: probes biomeOS, calls `composition.deploy` + `graph.status`
- Pixel deploy extended: all 13 primal startup handlers, aarch64-linux-android path discovery
- benchScale IPC compliance operational: `benchscale validate ipc` against live NUCLEUS
- **Mesh LIVE** (Wave 101): songBird P1 fix (03f23d45+aebe271f) resolved SB-TLS-LAN-01 + SB-SECURITY-URL-01.
  eastGate↔strandGate: bootstrap_peers_added:1, all_healthy:true, reachable_peers:1, latency 0ms. 17h+ stable.
- **Transport 10-11/11** (Wave 101-103): barracuda + rhizoCrypt self-knowledge violations fixed (sourdough-core dep
  removed, local TransportEndpoint). bearDog transport adoption DONE. loamSpine confirmed ahead of target.
  toadStool may be done per strandGate ACK. sourDough shipped `validate depot` + dep violation detection.
- **Depot 14/14 fresh** (Wave 103): full x86_64-musl rebuild. All binaries current. checksums.toml regenerated.
- bearDog `aws-lc-rs` C-dep discovered: blocks ALL non-x86 targets (aarch64-musl, aarch64-android). P1 for ecoBin.
- ~~flockGate WAN depot empty~~ — RESOLVED (Wave 105): `plasmid.fetch --source wan` SHIPPED.
- biomeOS v4.14 rebuilt by strandGate (LocalTrusted access level for UDS callers).
- sourDough convergent evolution COMPLETE: `validate transport`, `validate depot`, scaffold transport-kit.
  sourDough is the repository of primal standards as a primal — primals do NOT depend on sourdough-core.

The ecosystem now operates on a formalized three-tier pattern:

| Tier | Component | Role |
|------|-----------|------|
| 1 | **primalSpring** | Composition experimentation laboratory — validates patterns, publishes to wateringHole |
| 2 | **cellMembrane** | Binary evolution + VPS ops — deploys validated patterns, manages plasmidBin depot |
| 3 | **projectNUCLEUS** | Polished agnostic deployment product — packages patterns for end users |

**Wave 82c Deep Debt Sprint COMPLETE**: primalSpring codebase fully modernized —
3 fossil scripts deleted, 2 bash validation gates replaced by Rust subcommands
(`primalspring nucleus`, `primalspring release`), hardcoded routing eliminated
(TOML-driven), shell-out `kill` replaced with `nix` crate, default auth evolved
to Enforced (fail-closed). 931 tests passing, zero bash in production path.

**Wave 87 milestone**: plasmidBin deployment pipeline VALIDATED end-to-end.
`membrane plasmid.harvest` rebuilt 3 drifted primals (biomeOS v4.09, loamSpine,
petalTongue). Depot: 13/13 current, 0 drifted. NUCLEUS launched from depot binary.
Cascade system leveled (Wave 84): parallel dispatch (6.9s for 22 repos).

**Wave 89 milestone**: SB-FEDERATION-01 RESOLVED — songbird federation listener
starts in server mode (0a09354b), biomeOS v4.11 passes `SONGBIRD_PRODUCTION_BIND_ADDRESS=0.0.0.0`.
BIO-SEARCH-01 RESOLVED — biomeOS v4.10 depot-first binary search.
CM-TRIGGER-01 RESOLVED — `plasmid.trigger` SSH-kicks VPS service.
All P1 deployment blockers RESOLVED.

10-11/11 non-exempt primals have transport injection. toadStool last potential gap (strandGate ACK pending).
All self-knowledge violations eliminated (barracuda, rhizoCrypt removed sourdough-core dep).
`sourdough validate transport` + `sourdough validate depot` auditing tools shipped.

Criteria 1 sovereignty: **S1-S4 ALL GRADUATED** on inner membrane. S4 7-day gate PASSED (Jun 9).
S1 inner membrane TLS LIVE (Caddy + LE on `primal.eco`). S3 VPS READY, 5/5 Caddy endpoints LIVE.
Criteria 2 mesh: **4-GATE COLLECTIVE LIVE** (Wave 107). eastGate↔golgiBody↔ironGate+southGate.
southGate cross-subnet validated (4.7ms, 13/13 alive, distributed science pipeline).
Criteria 3: peptidoglycan FORMALIZED. Depot 13/13 verified x86_64-musl. Deterministic deployment
codified (gate.bootstrap 6/6 invariants). gate.status + --dry-run shipped.
Criteria 4: WAN depot SHIPPED + REFRESHED (songbird + biomeOS rebuilt). flockGate 4/5 PASS,
awaiting power-on for 5/5.
Criteria 5: `primal.eco` + `nestgate.io` DNS PROPAGATED + TLS LIVE (Jun 4). `primals.eco` stays
Cloudflare (outer membrane per diderm model). DNSSEC enabled on both sovereign domains.
Criteria 6: cross-membrane validation scenario shipped. Peptidoglycan self-refresh timer deployed.
biomeOS v4.18 (supervision + TCP fallback). Zero commercial services in inner membrane data path.

**Critical path to stadial entry**:
1. ~~VPS deploy refresh~~ **DONE** — cellMembrane plasmid-pipeline.timer (zero-touch, 30-min cycle)
2. ~~plasmidBin pipeline e2e~~ **VALIDATED** (Wave 87) — harvest, status, NUCLEUS from depot all proven
3. ~~On-demand trigger mechanism (CM-TRIGGER-01)~~ **RESOLVED** (Wave 87) — `plasmid.trigger` SSH-kicks VPS
4. ~~Fix biomeOS binary search priority (BIO-SEARCH-01)~~ **RESOLVED** (Wave 88) — v4.10 depot-first
5. ~~eastGate Songbird federation port 7700 (SB-FEDERATION-01)~~ **RESOLVED** (Wave 89) — songbird + biomeOS fix
6. ~~mesh.init 2-gate proof~~ **COMPLETE** (Wave 92) — bidirectional, all 4 criteria, sub-ms latency
7. ~~S4 auth gate review (~Jun 9)~~ — **PASSED** (Jun 9, S4 GRADUATED)
8. Transport injection evolution (1/14 primals — P2, non-blocking for stadial)
9. projectNUCLEUS consumption surface validated (specs/DOWNSTREAM_CONSUMPTION.md published)
10. ~~VPS-BUILD-01 pipeline cargo build on golgiBody~~ **RESOLVED** (Wave 92) — refresh-only
11. ~~CM-PEPTI-SSH-01 golgiBody→pepti SSH trust~~ **RESOLVED** (Wave 92)
12. ~~barraCuda build break~~ **RESOLVED** (Wave 93) — SimpleMlp methods restored, depot 13/13

**Stadial entry is gated only on**:
- ~~S4 auth gate review completion~~ — **PASSED** (Jun 9, S4 GRADUATED)
- ~~3rd gate mesh enrollment~~ — **DONE** (Wave 106, ironGate 3rd node. Wave 107, southGate 4th node)
- ~~WAN covalent validation~~ — VPS depot refreshed (songbird+biomeOS). flockGate 4/5 PASS, awaiting power-on for 5/5
- ~~biomeOS orchestration revalidation~~ — **VALIDATED** (Wave 105, graph.deploy 13-phase, LocalTrusted)

**Cross-deployment gates (ecoBin matrix)**:
- ~~bearDog pure Rust (P1)~~ — **RESOLVED** (Wave 145). aarch64 UNBLOCKED.
- ~~flockGate WAN depot (P1)~~ — **RESOLVED** (Wave 105). DEPLOYED, /depot/ live, ironGate validated.
- ~~grapheneGate bootstrap (P2)~~ — **DEPLOYED** (Wave 108). 13/13 alive TCP-only. guideStone-grade convergence in progress (Wave 109).
- ~~aarch64 sweep (P2)~~ — **COMPLETE** (Wave 105, 14/14 built). CM-CHECKSUM-MULTI-TARGET P2 pipeline fix needed.
- Windows ecoBin (LOW) — named pipes IPC, MSVC target, design phase

**Next glacial goal: Universal Substrate Evolution** (post-stadial)

The ecoBin/uniBin/genomeBin system must evolve to full NUCLEUS deployments
across all architectures — current, legacy, and future. The ecosystem is
universal and architecture-agnostic by design (pure Rust, zero C-deps,
musl-static). Achieving multi-arch depot parity unlocks the next real
evolution era across substrates.

| Target | Status | What It Unlocks |
|--------|--------|----------------|
| `x86_64-unknown-linux-musl` | **14/14 BUILT** | All current gates |
| `aarch64-unknown-linux-musl` | **14/14 BUILT** | grapheneGate, ARM servers, Raspberry Pi |
| `aarch64-linux-android` | UNBLOCKED | Native Android NUCLEUS (no Termux). NDK cross-compile. |
| `x86_64-unknown-linux-gnu` | Partial | GPU primals (toadStool, barraCuda, coralReef) on ironGate. Glibc for CUDA drivers. |
| `riscv64gc-unknown-linux-musl` | Design | RISC-V embedded gates, future SoCs |
| `x86_64-pc-windows-msvc` | Design | Windows gates, named pipes IPC |
| `wasm32-wasi` | Design | Browser/edge/embedded — primals as WebAssembly modules |
| `aarch64-apple-darwin` | Design | macOS Silicon gates |

Each new target is a new substrate the ecosystem can colonize — every
architecture that can run a NUCLEUS is a potential sovereign node. This is
the fractal deployment vision at its fullest: the same primals, the same
mesh, the same depot pipeline, on any hardware that exists or will exist.

Software items: **ZERO P1 blockers.** Transport 11/11 COMPLETE. Depot 14/14 x86_64 + 14/14 aarch64 BUILT.
bearDog pure Rust SHIPPED. biomeOS v4.16 graph.deploy VALIDATED. WAN depot DEPLOYED. Cascade auto-resolve
SHIPPED. aarch64 sweep COMPLETE. CM-CHECKSUM-MULTI-TARGET RESOLVED. CM-DEPOT-DIVERGENCE RESOLVED (was
self-inflicted local rebuild violation). **Post-primordial depot standard enforced: VPS-only deployment.**

---

## External Proof: SHOW_HN Publication (Wave 133d+)

The `SHOW_HN_PUBLICATION.md` rubric (whitePaper gen5/thesis/) establishes an external
validation event that maps directly to stadial readiness. The 10 ecosystem standards
(S-category) require:

- S-6: Pepti depot current (all binaries built from latest commits)
- S-8: `capability.call` cross-gate proven (WAN-DISPATCH-01 FULL PASS)
- S-10: sporePrint served from sovereign inner membrane (bearDog TLS cutover)
- S-1 through S-5, S-7, S-9: test suite, convergence, documentation standards

The 3-6 month karma buildup window provides natural pacing for sovereignty sprint
(Wave 134b) and operational proof exercises before public dissemination.

---

## References

- `DIDERM_DOMAIN_ARCHITECTURE.md` — Trust barrier model, peptidoglycan air gap, domain assignments
- `SOVEREIGNTY_STANDARDS.md` — calibrate → shadow → cutover protocol
- `CELLMEMBRANE_FIELDMOUSE_DEPLOYMENT.md` — VPS composition spec
- `MEMBRANE_CHANNEL_ARCHITECTURE.md` — 3 channels + RustDesk
- `DARK_FOREST_GLACIAL_GATE_STANDARD.md` — 5 security invariants + membrane classification
- `DISTRIBUTED_COVALENT_DEPLOYMENT.md` — multi-household compute architecture
- `DESKTOP_NUCLEUS_DEPLOYMENT.md` — single-machine full stack
- `DEPLOYMENT_PHASE_PLAN.md` — Phased deployment from parity to stadial entry
- `whitePaper/gen5/thesis/SHOW_HN_PUBLICATION.md` — External proof rubric (28 criteria, 4 categories)
- `GATEHOUSE_DARKFOREST_STANDARD.md` — Bond escalation at the gatehouse boundary
