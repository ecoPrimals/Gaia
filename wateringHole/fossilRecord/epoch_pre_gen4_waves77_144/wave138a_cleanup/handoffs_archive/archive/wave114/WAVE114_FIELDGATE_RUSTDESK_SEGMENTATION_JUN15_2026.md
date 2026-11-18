# Wave 114 — ABG Sovereign Compute

**Status**: CODE COMPLETE | Deadline: Friday June 20 | **From**: eastGate overwatch
**Last review**: Jun 16 15:31Z

---

## Result: 6/7 Exit Criteria CLEARED — All Code Work DONE

| # | Criterion | Status |
|---|-----------|--------|
| 1 | fieldGate (NUC): 13/13 alive + mesh | **✅ DONE** |
| 2 | grapheneGate (Pixel): aarch64 depot + 13/13 | DEPOT READY (ops: device needed) |
| 3 | flockGate (WAN): relay depot + 13/13 | PATH PROVEN (ops: gate needed) |
| 4 | RustDesk relay operational + health-probed | **✅ DONE** |
| 5 | ABG member end-to-end | TODO (ops: first member test) |
| 6 | pepti fresh harvest (both arches) | **✅ DONE** |
| 7 | Genetics-layer wiring (11/11 accept mito-beacon) | **✅ DONE** |

**Remaining items are ops-only** (physical device access, first ABG member walkthrough).

---

## Ecosystem Snapshot (Jun 16 15:31Z)

| Metric | Value |
|--------|-------|
| VCS parity | **17/17 ✓** (zero drift, primalSpring pushed 14 local→origin) |
| Genetics | **11/11 ✅** ALL primals accept mito-beacon |
| Depot x86_64 | **13/13 BUILT** from HEAD (pepti Jun 16 02:27Z) |
| Depot aarch64 | **13/13 BUILT** on pepti (Jun 15) |
| fieldGate | **13/13 ALIVE**, mesh enrolled |
| ironGate | **DRY-RUN 11/11 PASS**, depot 14/14 verified, ready for live bootstrap |
| golgiBody | **FULL GREEN HEALTHY** (16 services, 28 sockets, 13/13 alive) |
| RustDesk relay | **EXTERNALLY REACHABLE** (:21115-21117) |
| WAN depot | **HTTPS 200 OK** (membrane.primals.eco) |
| Cascade | **ff-merge fix SHIPPED** (`8f4e4eb`) — SHA preservation in common case |

---

## Wave 114 Shipped (complete record)

### Genetics-Layer (11/11)

| Primal | Commit |
|--------|--------|
| bearDog | `f997a33` — mode-detection race resolved |
| songBird | `fc766dc` — federation handler: stub → dispatcher |
| sweetGrass | `96d35e5` — 0xED mito-beacon accepted |
| rhizoCrypt | `c5913cd` — genetics-layer + SSOT |
| barraCuda | `cbb2704` — centralized pattern adopted |
| toadStool | `5903cf6` — S320: 0xED all loops |
| loamSpine | `e68873d` — full eukaryotic model |
| cellMembrane | `fbd58ac` — signal module reference |
| squirrel | (verified) — already wired |
| petalTongue | (original) — reference impl |
| coralReef/nestGate | passes (no health method) |

### cellMembrane Deployment Hardening

| Commit | What |
|--------|------|
| `fed3335` | Robust bootstrap: systemd, install, secrets, permissions (7 hurdles) |
| `c032abf` | Mesh retry loop, docs |
| `8f4e4eb` | Cascade fix: ff-merge over rebase (SHA preservation) |
| `63a2130` | **Unified depot resolution**, env-configurable paths, capability-based freshness, multi-peer mesh |
| `9dc6a1d` | **Version reporting** (`membrane --version`), socket alias registry (28 sockets documented) |

### Infrastructure

| What | Detail |
|------|--------|
| pepti x86_64 harvest | 13/13 from HEAD (104min, exit 0) |
| pepti aarch64 harvest | 13/13 (toadstool manual for OOM) |
| RustDesk UFW | :21115-21117 opened |
| WAN depot | HTTPS 200 serving |
| ironGate dry-run | 11/11 PASS, depot verified |

---

## VPS Diderm Layer Audit (11 divergences found)

**Full AAR**: FRAGO `aar_jun16_1430_vps_divergence`

Key findings from ironGate audit of golgiBody + pepti:

| # | Divergence | Impact |
|---|-----------|--------|
| 1 | Three competing depot paths | Confusion during bootstrap |
| 2 | No cellMembrane clone on golgiBody | Cannot self-update |
| 3 | Binary version lag (pre-63a2130) | Missing all path fixes |
| 4 | Socket explosion (28 vs 13 expected) | Undocumented capability aliases |
| 5 | Systemd unit style mismatch | Hand-crafted vs bootstrap-generated |
| 6 | Environment/secrets model split | tower.env vs secrets.env |
| 7 | Unknown SONGBIRD_PEERS IPs | Undocumented mesh nodes |
| 8 | Legacy socat bridges (no TLS) | Fragile relay function |
| 9 | Deployment debris in /opt/membrane/ | Archive needed |
| 10 | pepti: no deployed binaries | Cannot self-validate harvest |
| 11 | pepti: source tree with no operational role | Needs tier decision |

---

## Overwatch Audit (Jun 16 15:31Z — Full Temporal/Ecosystem/Sovereignty/Glacial/Deployment)

### Temporal

| Tier | Repos | Age |
|------|-------|-----|
| Active (today) | cellMembrane, primalSpring, wateringHole, 8 primals | 0-3h |
| Recent | skunkBat, coralReef, plasmidBin | 26-27h |
| Settling | biomeOS, nestGate, petalTongue | 41-42h |
| Dormant springs | wetSpring, neuralSpring, etc. | 5-7d |
| Glacial | rustChip, fossilRecord, blueFish, helixVision | 17-46d |

38 repos total on disk. 17 in active cascade. 21 dormant/stable (not drift).

### Sovereignty Findings

| Check | Status |
|-------|--------|
| golgi uptime | 31 days, load 0.00 ✓ |
| golgi Forgejo | **ACTIVE** ✓ |
| golgi membrane binary | **AT HEAD** (9dc6a1d) ✓ |
| golgi RustDesk (hbbs/hbbr) | **✅ LIVE** — systemd units active, WorkingDir fixed, key generated (Jun 16 21:02Z) |
| golgi sockets | 28 running ✓ |
| pepti uptime | 17 days, load 0.00 ✓ |
| pepti cellMembrane | **AT HEAD** (9dc6a1d) ✓ |
| pepti depot | Binaries at `primals/{arch}/` subdirectory ✓ |
| fieldGate | **UP** (1d18h, 3 sockets, load 2.07) |
| eastGate NUCLEUS | No systemd units (dev mode, manual execution) |

**Resolved**: RustDesk relay fixed Jun 16 — WorkingDirectory was missing, key not generated. Created dir, restarted, key deployed to sporeGate.

### Depot State

| Arch | Count | Age | Location |
|------|-------|-----|----------|
| x86_64-musl | 13/13 | Jun 15 (1 day) | `primals/x86_64-unknown-linux-musl/` |
| aarch64-musl | 14/14 | Jun 10 (**6 days**) | `primals/aarch64-unknown-linux-musl/` |
| aarch64-android | 1 (sourdough) | — | experimental |

**Issues**: 
- x86_64 depot missing `sourdough` binary
- aarch64 depot is pre-genetics-wave (stale)
- Double-nested directory bug: `primals/x86_64/.../primals/x86_64/...`
- No checksums for aarch64

### Glacial Debt (Long-term)

- **Version tags**: Only 5/13 primals tagged. bearDog +862, toadStool +2073 since last tag
- **Manifest**: Was wave 109, updated to wave 114 this session
- **No guideStone/ or standards/ directories** in wateringHole — socket naming + service contracts undocumented
- **21 dormant repos** not in cascade (stable, not drifting — but unchecked)

---

## Team Restructuring (Jun 16)

| Gate | Previous Role | New Role |
|------|---------------|----------|
| **sporeGate** | planned/offline | **cellMembrane owner** — LAN periplasm, routing, cascade, depot, bootstrap, RustDesk |
| **ironGate** | cellMembrane primary | **projectNUCLEUS / ABG** — compute sharing, access tiers, JupyterHub/toadStool |
| **eastGate** | overwatch | overwatch (unchanged) |
| **fieldGate** | canary NUC | autonomous LAN node (unchanged) |

**Rationale**: sporeGate IS the membrane — it sits at the network perimeter, controls
what enters/exits the LAN, and mediates all gate communication. Natural owner.
ironGate's strength is ABG-facing work (science compute, user access, content delivery).

---

## Wave 115 Shape (sporeGate Hardening + ABG Access + VPS Convergence)

### P1: sporeGate LAN Periplasm — PHASE 1 COMPLETE (cellMembrane/sporeGate)

**DONE**: Basic routing, NAT, DHCP, DNS, 13/13 primals alive, RustDesk configured.

Remaining phases:
- Phase 2: [ISP] bridge mode (eliminate double NAT)
- Phase 3: Firewall hardening + primal systemd persistence
- Phase 4: WireGuard tunnel to golgi (persistent mesh, eliminates NAT timeouts)
- Phase 5: VLAN segmentation (compute/mobile/guest/mgmt)

Docs: `compute-sharing/NETWORK_SOVEREIGNTY.md`, `compute-sharing/SPOREGATE_ACTIVATION_BLURB.md`
Handoff: `handoffs/SPOREGATE_ONBOARDING_BLURB.md`

### P1: Any-to-Any Remote Access (cellMembrane/sporeGate)

All gates addressable via RustDesk relay. Key deployed to sporeGate.
Remaining: deploy key to eastGate + fieldGate, verify inter-tower remote.
Relay key: `[RUSTDESK_KEY_PURGED]`
Server: `[RELAY_PUBLIC]` (golgi hbbs/hbbr — systemd units running, WorkingDir fixed)

### P1: ABG Member E2E Access (ironGate/projectNUCLEUS)

- External user → RustDesk relay → NUC/tower → workload
- Access tiers: Observer (view), Reviewer (comment), User (compute), Operator (admin)
- JupyterHub + toadStool as sovereign compute interface
- Cursor IDE as pair-programming layer

### P1: VPS Layer Convergence (cellMembrane/sporeGate)

- golgi membrane is at HEAD ✓ — verify services using new socket registry
- Consolidate triple depot paths to single canonical
- Replace legacy bash `deploy_membrane.sh` with `plasmid.refresh`
- Decide pepti operational tier (Tower Atomic min for self-validation)
- RustDesk relay formalized as systemd (hbbs-membrane.service ✓, hbbr-membrane.service ✓)

### P1: Event-Driven Cascade (cellMembrane/sporeGate)

- ff-merge fix is interim — webhooks eliminate the multi-gate race
- Forgejo webhook → triggers sync to GitHub (and reverse)
- Eliminates manual force-convergence during active waves

### P2: Fresh aarch64 Harvest (cellMembrane/pepti)

- Current aarch64 depot is 6+ days old (pre-genetics wave)
- Needs rebuild including all genetics-layer commits
- Also need sourdough in x86_64 depot

### P2: Socket Naming + Service Standard (cellMembrane/sporeGate + primalSpring)

- `9dc6a1d` documents all 28 sockets in registry — but no enforcement yet
- Bootstrap should generate from registry
- Eliminate ad-hoc FAMILY_ID suffixing

### P2: Deployment Atomicity (cellMembrane/sporeGate)

- Canary promote: new binary → sandbox socket → health verify → atomic swap
- Self-refresh pipeline in Rust (replace bash)

### P3: Environment Consolidation

- Unify tower.env + secrets.env → structured `env.d/`

### P3: Bridge Evolution (cellMembrane/sporeGate + songBird)

- socat TCP bridges → Rust-native transport with mTLS

### Carry (Wave 115+)

| Debt | Owner | Priority |
|------|-------|----------|
| `BEARDOG_FAMILY_SEED` deprecation | bearDog | P2 |
| Nuclear lineage per-ABG-user | bearDog + primalSpring | P2 |
| Network segmentation (VLAN) | cellMembrane/sporeGate | P2 |
| Version tag hygiene | all teams | P3 |
| neuralAPI hollow (0 registrations) | biomeOS | P3 |
| Peer registry (mesh.peers RPC) | songBird | P3 |
| CRS310 strip L3 → pure L2 | ops + cellMembrane/sporeGate | P2 |

---

## Genetics Architecture (reference)

| Stream | Purpose | Property | Wire |
|--------|---------|----------|------|
| **MitoBeacon** | Relay access, mesh, ABG transport | Shared/copyable | `0xEC`/`0xED` |
| **Nuclear Lineage** | Per-user permissions, tiered access | Non-fungible, BearDog-spawned | `0xEE` |

BearDog owns both. `FAMILY_SEED` = mito-beacon material.
Architecture doc: `handoffs/primalSpring/GENETICS_ARCHITECTURE_EUKARYOTIC_MODEL_JUN16_2026.md`
