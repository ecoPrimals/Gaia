# Wave 116 — Mesh Enrollment & Gate Parity

**Status**: CLOSED → Wave 119 | **From**: eastGate overwatch | **Date**: 2026-06-17
**Final review**: Jun 19 14:07 EDT (CONVERGED: 680 tests, pepti P0 FIXED, deep debt across all 13 primals, sporePrint P0+P1 shipped, all VCS parity)
**Transition**: Wave 116 objectives 80%+ complete. Remaining physical/operator-gated items carried to Wave 119.

---

## Objective

Gates are on sovereign relay. Now: full enrollment — SSH, NUCLEUS, mesh parity.
Raise every online gate to the same operational standard as sporeGate (13/13 primals,
systemd persisted, SSH accessible, WireGuard overlay, cascade connected).

---

## Sovereign Relay Status (5/9 migrated, 3 remaining, 1 offline)

| Gate | Relay | Zone | OS | SSH | NUCLEUS | WireGuard | Next Action |
|------|-------|------|----|-----|---------|-----------|-------------|
| **sporeGate** | ✅ Sovereign | backbone | Pop!_OS | ✅ | 13/13 | ✅ (10.13.37.2) | Reference gate — fully enrolled |
| **eastGate** | ✅ Sovereign | backbone | Pop!_OS 22.04 | ✅ | **13/13** | ✅ (10.13.37.5) | **FULL NUCLEUS** — 13/13 primals, 28 sockets, user systemd. No sudo needed. |
| **northGate** | ✅ Sovereign | backbone | Windows | — | — | — | P3: hobby, SSH + NUCLEUS after Linux proven |
| **ironGate** | ✅ Sovereign | TBD | TBD | — | — | — | SSH enable, identify hardware, assign team |
| **flockGate** | ✅ Sovereign | WAN | Ubuntu 24.04 | ✅ | — | ✅ (10.13.37.6) | **LIVE on mesh** — 32ms to golgi, 72ms to sporeGate. NUCLEUS deploy next. |
| **strandGate** | ❌ Public | house2 (Omada) | TBD | — | — | — | Operator: push sovereign config |
| **southGate** | ❌ Public | house2 (Omada) | TBD | — | — | — | Operator: push sovereign config |
| **swiftGate** | ❌ Public | house2 (WiFi) | TBD | — | — | — | After Flint 2 live: push sovereign config |
| **fieldGate** | ⬛ Offline | house2 (Omada) | Pop!_OS | — | — | — | Dead CMOS, hardware repair |

---

## Teams & Ownership (3 gates, 4 subteams)

### eastGate — primalSpring Evolution + NUCLEUS (this IDE)

*The science and validation engine. Evolve primalSpring, prove NUCLEUS locally.*

| Focus | Detail |
|-------|--------|
| **primalSpring** | Validation scenarios, evolution modules, genetics compliance, Spring→NUCLEUS integration |
| **NUCLEUS on eastGate** | Deploy 13/13 primals locally, systemd persist, prove the compute gate pattern |
| **Overwatch** | Cascade review, cross-team blurbs, gate parity tracking, impulse management |
| **Ecosystem validation** | Run tests (660 cellMembrane, 75 primalSpring scenarios), catch drift, confirm convergence |

**Immediate work:**
1. NUCLEUS deploy on eastGate (13/13 primals + systemd — script staged, needs sudo)
2. primalSpring scenario expansion (mesh topology validation, gate enrollment posture)
3. Cascade review + blurb coordination across teams

### sporeGate — Two Subteams (both on NUC)

#### sporeGate Overwatch — Hardware, Topology, Integration

*Dedicated subteam (like biomeGate). Owns the physical mesh and gate enrollment.*

| Focus | Detail |
|-------|--------|
| **Gate enrollment** | SSH enable → preflight → NUCLEUS deploy → WG peer on remaining gates |
| **LAN topology** | Omada (standalone L2), CRS310, Flint 2 swap, three-hub triangle backbone |
| **Mesh expansion** | WireGuard overlay admin, peer adds, routing, subnet carving |
| **Hardware integration** | Physical ports, cable runs, AP config, NUC onboarding |
| **Relay migration** | Push sovereign config to strandGate, southGate, swiftGate |

**Immediate work:**
1. NUCLEUS deploy on eastGate (via SSH, once sudo unblocked)
2. NUCLEUS deploy on flockGate (WG live, SSH live — ready now)
3. ironGate OS identification + SSH enable
4. Flint 2 physical swap + config (this weekend)
5. Add flockGate golgi peer (if not done)

#### cellMembrane Team — Code + VPS

*Subteam owns the codebase and VPS infrastructure. Evolves the tooling that overwatch deploys.*

| Focus | Detail |
|-------|--------|
| **cellMembrane code** | Cytoplasm zones, topology.resolve, firewall evolution, gate.* commands, S1-S4 sovereignty |
| **VPS management** | golgi (Forgejo, relay, WG hub), pepti (builds, depot). Fix pepti SSH→forgejo. |
| **Multi-gate support** | Ensure NUCLEUS deploy works identically on all Linux gates |
| **Cascade pipeline** | webhook.rs → GitHub, bidirectional event-driven VCS parity |
| **Fresh binary** | Build from HEAD on pepti, deploy to all gates via overwatch |

**Immediate work:**
1. Fix pepti SSH→forgejo (unblocks fresh binary from HEAD)
2. Cytoplasm zone types in envelope.rs
3. topology.resolve command implementation
4. webhook.rs → GitHub cascade wiring

### flockGate — sporePrint + K-Derm Periplasm Validator (WAN, offsite)

*The WAN proving ground and public face. Owns the website, validates the outer layers.*

| Focus | Detail |
|-------|--------|
| **sporePrint** | Modernize primals.eco (222 pages, many stale). P0: metrics refresh. P1: K-Derm glossary + deployment docs. |
| **K-Derm periplasm** | Only gate testing WG through real WAN, RustDesk relay from offsite, cascade without LAN. |
| **WAN NUCLEUS** | First non-LAN NUCLEUS gate (after sporeGate deploys it). Proves deployment over internet. |
| **Cascade validation** | Every push to Forgejo/GitHub from flockGate proves the outer membrane works. |

**Immediate work:**
1. Await NUCLEUS deploy from sporeGate team (WG + SSH are ready)
2. Begin sporePrint P0: `spore-validate refresh`, fix sitemap count, check links
3. sporePrint P1: glossary refresh (K-Derm terms), SOVEREIGN_DEPLOYMENT.md rewrite
4. Validate cascade: pull all repos via WG overlay, push updates to both remotes

---

## Enrollment Pipeline (sporeGate overwatch executes)

For each gate that's on sovereign relay:

```
1. SSH enable (apt install openssh-server + add sporeGate key)
2. gate.preflight (interface detect, DNS, NM, IP conflict check)
3. membrane binary install (fetch from pepti depot)
4. NUCLEUS deploy (13/13 primals + systemd persist)
5. WireGuard peer (add to golgi hub, assign 10.13.37.X)
6. Cascade connect (git remotes, push/pull verification)
7. Mark ENROLLED in blurb
```

### Immediate Targets (sovereign, need enrollment)

| Gate | Step 1 (SSH) | Step 2 (preflight) | Step 3-7 | Blocker |
|------|-------------|-------------------|----------|---------|
| **eastGate** | ✅ Key authorized | ✅ Probed (i9-12900K, 32GB, 10G) | `enroll.sh` staged at `~/enrollment/` | sudo password (operator) |
| **ironGate** | Pending | — | After SSH | OS identification via RustDesk |
| **flockGate** | ✅ Done + sporeGate key authorized | ✅ WG live (32ms golgi, 62ms sporeGate) | NUCLEUS deploy next | ✅ UNBLOCKED |

---

## Hub 2 WiFi Swap: Eero → GL.iNet Flint 2 (this weekend)

**Problem**: Eero bridge mode collapsed overnight — lost internet for hub 2 WiFi clients.
**Interim**: CAT6 from CRS310 restores wired connectivity now.
**Fix**: Replace Eero with GL.iNet Flint 2 (GL-MT6000). OpenWrt-based, fully controllable.

| Task | Owner | Status |
|------|-------|--------|
| Physical Eero removal + Flint 2 install | operator | This weekend |
| Flint 2 initial config: AP mode, same SSID, bridge to 192.168.4.x | sporeGate overwatch | After install |
| swiftGate connectivity (was on Eero WiFi) → connect to Flint 2 | operator | After AP live |
| Push sovereign relay config to swiftGate | operator + sporeGate | After WiFi restored |
| Omada SDN: update port map for Flint 2 | sporeGate overwatch | After install |

**Flint 2 advantages over Eero**:
- OpenWrt: SSH, full CLI, `nftables`, `dnsmasq`, package manager
- Can run as dumb AP (bridge) without stability issues
- Future: WireGuard client directly on AP, VLAN-tagged WiFi, guest isolation
- Meshable with other GL.iNet devices (Goodcloud or manual WG)

---

## Remaining Relay Migration (operator from northGate)

strandGate, southGate, and swiftGate still on public relay. Operator connects
via public RustDesk, pushes sovereign config:

```
pkexec rustdesk --config "[RUSTDESK_CONFIG_PURGED]"
```

If pkexec fails, use `sudo` or write config file directly (see RUSTDESK_CONFIG.md).

---

## Infrastructure

| System | Owner | Status |
|--------|-------|--------|
| **golgi** (10.13.37.1) | cellMembrane team | HEALTHY — Forgejo, relay, WG hub, 13/13 |
| **pepti** (10.13.37.4) | cellMembrane team | HEALTHY — build, depot, WG peer |
| **Omada SX3008F** | sporeGate overwatch | **STANDALONE L2** — controller STOPPED (broke port 8). Switch runs unmanaged. |
| **Eero 6** | retiring | **WORKAROUND** — CAT6 direct from CRS310, NAT mode. Replaced by Flint 2 this weekend. |
| **GL.iNet Flint 2** | sporeGate overwatch | **ORDERED** — OpenWrt WiFi 6, AP bridge on hub 2. SSH/root, sovereign. |
| **CRS310** | sporeGate overwatch | L2 backbone (hub 1), pure switching |
| **[ISP] BGW320** | pending passthrough | Double-NAT still active (P2) |
| **Garage (hub 3)** | planned | Future compute + outdoor WiFi. Wiring/insulation upgrade needed. |

### Topology Evolution: Three-Hub Triangle

```
         House 1 (hub 1)             Target: triangle backbone
        CRS310 + sporeGate           with redundant paths.
       [ISP] + WiFi (evaluate)         Any single leg failure
          /           \              routes through other two.
    leg A/             \leg B (LIVE, 80m AOC 10G)
        /               \
   Garage (hub 3)----House 2 (hub 2)
   planned          leg C    Omada SX3008F (standalone L2)
                    planned  + GL.iNet Flint 2 (OpenWrt WiFi)
```

**Hardware philosophy**: heterogeneous open. MikroTik (RouterOS), TP-Link (standalone L2), GL.iNet (OpenWrt), [ISP] (proprietary WAN). No single vendor, no cloud management planes. Diversity forces the primal abstraction to be robust.

---

## Primal Work Assignments (focused gate roles)

Each gate owns one atomic composition as its primary workload. All gates run full
NUCLEUS (13/13) but primals are **assigned work** based on gate role. Idle primals
still provide their services if called — this is about where work is *dispatched to*.

```
Tower (trust)     → flockGate (WAN periplasm — proves trust over internet)
Node (compute)    → ironGate (compute trio — dedicated GPU/tensor when live)
Nest (data)       → sporeGate (provenance authority — ledger, depot, cascade)
Meta (orchestrate)→ eastGate (AI + viz + orchestration + primalSpring)
```

### flockGate — Tower Atomic (BearDog, Songbird, SkunkBat)

*WAN periplasm prover. The trust layer exercises over real internet latency.*

| Primal | Work Assignment |
|--------|-----------------|
| **BearDog** | WAN BTSP validation — latency-tolerant crypto handshakes over 65ms links |
| **Songbird** | WAN mesh discovery — proves NAT traversal + relay federation across internet |
| **SkunkBat** | Perimeter defense — K-Derm outer membrane threat assessment, WAN anomaly detection |

**Why flockGate**: Only gate on actual WAN (not LAN). Tower trust must work at 65ms+
latency, through NAT, over public internet. If BTSP works here, it works everywhere.
Also validates: sporePrint content integrity (SkunkBat audits), cascade authentication
(BearDog signs), relay federation (Songbird mesh from offsite).

**Status**: WG live (.6), SSH live. Awaiting NUCLEUS deploy (SSH key blocker).

### ironGate — Node Atomic (ToadStool, BarraCuda, CoralReef)

*Dedicated compute gate. When live: tensor math, GPU dispatch, shader compilation.*

| Primal | Work Assignment |
|--------|-----------------|
| **ToadStool** | Compute dispatch authority — route GPU jobs, experiment orchestration |
| **BarraCuda** | Tensor/GPU workloads — ML training, physics sims, heavy math |
| **CoralReef** | Shader compilation — visualization rendering, compute pipelines |

**Why ironGate**: Keeps heavy compute isolated from the plasma membrane (sporeGate)
and the orchestration layer (eastGate). Compute gates are fungible — future northGate
(5090) or garage gates join via covalent bond and receive dispatched work.

**Status**: On sovereign relay. BLOCKED — SSH not enabled, OS unidentified. Operator
must RustDesk in, identify OS, enable SSH. Then enrollment pipeline runs.

### sporeGate — Nest Atomic (NestGate, RhizoCrypt, LoamSpine, SweetGrass)

*Data/provenance authority. Ledger of truth, depot, cascade state, attribution.*

| Primal | Work Assignment |
|--------|-----------------|
| **NestGate** | Depot authority — serves 13/13 binaries, content-addressed blob store |
| **RhizoCrypt** | Cascade provenance — dehydrate state, rootpulse commits, DAG sessions |
| **LoamSpine** | Sovereign ledger — wave state commits, merkle proofs, permanence |
| **SweetGrass** | Attribution — commit braids, multi-gate contribution tracking |

**Why sporeGate**: Site router with 13/13 NUCLEUS, always-on, direct access to all LAN
gates + VPS. The provenance authority must be on the most connected, most stable node.
Depot serving requires high uptime. Ledger commits need to survive gate restarts.

**Also runs** (secondary): full Tower (plasma membrane firewall), BiomeOS (gate
enrollment orchestration), compute dispatch (membrane builds on pepti).

### eastGate — Meta-tier (BiomeOS, Squirrel, PetalTongue)

*Orchestration, AI inference, visualization. The brain of the mesh.*

| Primal | Work Assignment |
|--------|-----------------|
| **BiomeOS** | NUCLEUS lifecycle orchestration — graph coordination, plasmodium collective |
| **Squirrel** | AI inference — scenario intelligence, evolution guidance, pattern matching |
| **PetalTongue** | Visualization — dashboards, topology rendering, gate.health views |

**Why eastGate**: i9-12900K (24 threads, 32GB RAM) is ideal for AI inference and
orchestration workloads. PetalTongue visualization benefits from the 10G link for
streaming data. BiomeOS neural-api coordinates across all gates via WG overlay.

**Also runs** (secondary): full NUCLEUS 13/13 locally for validation. primalSpring
evolution team uses all primals for scenario testing. Provenance trio active for
local experiment tracking (rhizoCrypt, LoamSpine, SweetGrass).

---

## Code Evolution Targets (sporeGate team)

| Item | Priority | Status |
|------|----------|--------|
| ~~Fix pepti SSH→forgejo~~ | ~~P0~~ | ✅ FIXED — wrong remote URLs on pepti (port 22 → 2222, sporeGarden → ecoPrimals) |
| ~~eastGate 13/13~~ | ~~P1~~ | ✅ DONE — biomeos (neural-api) + nestgate (socket+JWT) fixed. 13/13 LIVE. |
| flockGate NUCLEUS deploy | **P1** | ✅ UNBLOCKED: SSH key authorized (irongate@pop-os). Deploy via `ssh flockgate@10.13.37.6` |
| ~~Cytoplasm zone types~~ | ~~P2~~ | ✅ SHIPPED — CytoplasmZone enum + struct, topology.resolve |
| ~~Sovereignty ledger~~ | ~~P2~~ | ✅ SHIPPED — rootpulse_commit/verify round-trip |
| webhook.rs → GitHub cascade | P2 | Provider abstraction shipped, wiring pending |
| Omada API client | P3 | Controller STOPPED but switch readable |
| Windows NUCLEUS port | P3 | northGate idle compute — after Linux proven |

---

## Ecosystem Metrics

| Metric | Value |
|--------|-------|
| Gates on sovereign relay | **5/9** (+ 3 pending, 1 offline) |
| Gates fully enrolled | **2/9** — sporeGate (13/13 system), eastGate (13/13 user systemd) |
| Gates NUCLEUS-active | **2** — sporeGate (13/13), eastGate (**13/13** user systemd) |
| Gates WG-enrolled (NUCLEUS pending) | **1** — flockGate (.6, ready for deploy) |
| WireGuard mesh nodes | **5 live** — golgi(.1), sporeGate(.2), pepti(.4), eastGate(.5), flockGate(.6) |
| cellMembrane tests | **680**, zero warnings, zero clippy |
| VCS parity | **ALL REPOS AT PARITY** — zero drift across origin + forgejo (fixed cellMembrane diverge) |
| membrane tooling | gate.preflight, gate.bootstrap, firewall.generate, gate.status, gate.health, **topology.resolve/zones/mesh** — ALL WORKING |
| Depot x86_64 | 13/13 (pepti behind HEAD — SSH→forgejo fix needed) |
| Fresh binary | Deployed sporeGate + eastGate (f7ecefe → 9c14725). topology.* commands LIVE. |
| Omada controller | **STOPPED** — switch runs standalone L2 (controller broke port 8) |
| Eero status | **RETIRING** — CAT6 workaround from CRS310, NAT mode |
| Flint 2 | **ORDERED** — OpenWrt WiFi 6, replaces Eero this weekend |
| Topology model | **v5.0.0** — three-hub triangle, heterogeneous open hardware |
| Cytoplasm zones | 3 defined (backbone, house2, garage planned) |

---

## Carry (Wave 117+)

| Debt | Owner | Priority |
|------|-------|----------|
| Flint 2 deploy + Eero retire | sporeGate overwatch | **P1** |
| [ISP] IP passthrough | operator + sporeGate | P2 |
| Hub 1 WiFi evaluation (replace [ISP] WiFi with OpenWrt AP) | sporeGate overwatch | P2 |
| Garage (hub 3) wiring + insulation | operator | P3 |
| Triangle leg A (house1↔garage) + leg C (garage↔house2) | operator + sporeGate | P3 |
| VLAN segmentation (compute/wifi/guest) | sporeGate overwatch | P3 |
| Version tag hygiene | cellMembrane team | P3 |
| IPv6 with NAT66/PD | sporeGate overwatch | P3 |
| LAN-local hbbs relay | sporeGate overwatch | P3 |
| LLDP auto-zone detection | cellMembrane team | P3 |
