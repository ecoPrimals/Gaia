# Wave 109 — guideStone Deployment Convergence (mid-wave update)

**Date**: 2026-06-11 (cascade 08:00 EDT)
**From**: eastGate overwatch
**FRAGO**: `impulses/active/2026-06-11T07-20_eastGate__wave109-guidestone-deployment-convergence.toml`

---

## Wave Status

This is a long wave. Evolution is trickling in across both sides of the membrane. 13 items resolved since wave open; remaining work is well-scoped.

**39 total resolved** (26 from Waves 106-108, 13 from Wave 109).

---

## What Just Landed (Wave 109 cascade)

### Stream 1: Standard Primal Startup Contract — 5/6 RESOLVED

| Primal | Status | Commit |
|--------|--------|--------|
| ~~barraCuda~~ | **RESOLVED** — `--bind-mode / PRIMAL_BIND_MODE` replaces `--no-unix` | `5f0e55e5` |
| ~~coralReef~~ | **RESOLVED** — `--port`, `--bind-mode` standard envelope | `7bc90e5` |
| ~~nestGate~~ | **RESOLVED** — HTTP default in server mode | `66126899` |
| ~~biomeOS~~ | **RESOLVED** — guideStone startup contract v4.22 | `5311dd3f` |
| ~~skunkBat~~ | **RESOLVED** — `--bind-mode` replaces `--no-uds/--no-tcp` v0.2.10 | `00b3436` |
| **bearDog** | **REMAINING** — auto-detect abstract socket from bind mode | — |

**PlatformCapabilities::detect()** — RESOLVED (primalSpring `b487dad`). ipc crate now probes SELinux, UDS, abstract sockets. Primals consume this.

### Stream 2: Build Pipeline — Infrastructure LANDED, Wiring Remaining

| Item | Status |
|------|--------|
| ~~`plasmid.build` Rust port~~ | **RESOLVED** — 325-line pipeline, ephemeral staging, BLAKE3, provenance (`9b764a5`) |
| ~~`deployment.toml` emission~~ | **RESOLVED** — gate.bootstrap emits provenance record, guideStone P2 |
| ~~Gate profile infrastructure~~ | **RESOLVED** — manifest + gate/local.rs support |
| ~~Health sweep JSON-RPC~~ | **RESOLVED** — gate.bootstrap validates JSON-RPC health |
| BUILD-CACHE-01 | **REMAINING** — clean staging before `--all` |
| BUILD-ELF-01 | **REMAINING** — ELF arch validation in `--all` integration |
| HARVEST-NAME-01 | **REMAINING** — cargo-vs-primal naming audit |
| GATE-PROFILE-01 wiring | **REMAINING** — per-gate TOML declarations |
| Gate engine | **REMAINING** — `deploy_pixel.sh` becomes transport backend |

### Stream 3: Health + Orchestration — Schema LANDED, 3 Primals Remaining

| Item | Status |
|------|--------|
| ~~HEALTH-01 schema~~ | **RESOLVED** — primalSpring validation scenario (`b487dad`) |
| ~~sweetGrass HEALTH-01~~ | **RESOLVED** — bare `health` alias + enriched response (`a675425`) |
| ~~biomeOS HEALTH-01~~ | **RESOLVED** — converged in v4.22 (`5311dd3f`) |
| ~~healthSpring HEALTH-01~~ | **RESOLVED** — convergence + 12 unit tests (`c65f89a`) |
| **rhizoCrypt** HEALTH-RC-01 | **REMAINING** — converge on JSON-RPC health |
| **petalTongue** HEALTH-PT-01 | **REMAINING** — converge on JSON-RPC health |
| **songBird** HEALTH-SB-01 | **REMAINING** — standard health endpoint + federation protocol gap |
| LAUNCHER-01 | **REMAINING** — `nucleus_launcher` cross-compiled for aarch64 |
| Tolerances codification | **REMAINING** — named tolerances in deployment.toml |

### Stream 4: BTSP E2E — Server-Side Ready, Validation Remaining

| Item | Status |
|------|--------|
| ~~sweetGrass BTSP readiness~~ | **RESOLVED** — BEARDOG_SOCKET resolution, 88 BTSP tests (`a675425`) |
| BTSP-E2E-01 handshake | **REMAINING** — full bearDog → client → sweetGrass validation |
| grapheneGate BTSP | **REMAINING** — TCP-only transport validation |

### Stream 5: cellMembrane Cascade + qS/rP — OPEN

All Stream 5 items remain open. This is the long-tail divergence hardening work:
- Dual checksum authority (git + VPS)
- Post-cascade selective NUCLEUS restart
- Process version match (JSON-RPC, not pgrep)
- Agentic divergence resolution
- quorumSignal: 15 atomic signal graphs
- rootPulse: impulse → full provenance trio
- Freshness mesh: songbird mesh.publish HEADs

---

## NEW: flockGate Federation Protocol Gap

flockGate re-tested after VPS songbird restart. **Same symptom persists.** Deeper investigation reveals:

- `federation.status` shows `enabled: false` even with correct env/CLI
- Port 7700 IS bound (TCP accepts connections, serves HTTP)
- Federation **listener** works; federation **client** (outbound mesh) NEVER activates
- LAN gates have working federation — possible config, feature-gate, or auth dependency
- **This is a songBird protocol issue, not a deployment issue**

See: `impulses/active/2026-06-11T12-00_flockGate__wave109-wan-federation-disabled.toml`

**songBird team**: diagnose what activates `federation.enabled = true`. Is `SECURITY_PROVIDER_SOCKET` required? Do LAN gates have additional configuration?

---

## Routing — Updated Primal Status

| Primal | Remaining Work | Status |
|--------|---------------|--------|
| **bearDog** | STARTUP-BD-01 + BTSP-E2E-01 | **ACTIVE** |
| **rhizoCrypt** | HEALTH-RC-01 | **ACTIVE** |
| **petalTongue** | HEALTH-PT-01 | **ACTIVE** |
| **songBird** | HEALTH-SB-01 + federation protocol gap | **ACTIVE** |
| ~~nestGate~~ | Stream 1 complete | **STANDBY** (was active) |
| ~~biomeOS~~ | Stream 1 + HEALTH-01 complete | **STANDBY** (was active) |
| ~~coralReef~~ | Stream 1 complete | **STANDBY** (was active) |
| ~~barraCuda~~ | Stream 1 complete | **STANDBY** (was active) |
| ~~skunkBat~~ | Stream 1 complete | **STANDBY** (was active) |
| ~~sweetGrass~~ | Stream 3 + 4 server-side complete | **STANDBY** (was active) |
| toadStool | — | **STANDBY** |
| squirrel | — | **STANDBY** |
| loamSpine | — | **STANDBY** |

> **4 primals ACTIVE, 9 STANDBY.** Wave 109 evolution moved 6 primals from active to standby. bearDog is the last Stream 1 holdout.

---

## Per-Level Guidance

### Primals

- **bearDog**: last Stream 1 item (abstract socket auto-detect) + BTSP E2E client-side
- **rhizoCrypt, petalTongue**: converge on JSON-RPC `{"method":"health"}` response schema
- **songBird**: federation protocol investigation (priority) + HEALTH-SB-01
- All others: **standby** — your Stream 1 items are resolved. Stay current.

### primalSpring — Infrastructure (not a primal)

primalSpring provides the evolution spring for primal interactions. Not a NUCLEUS primal, no binary in depot.

- ~~`PlatformCapabilities::detect()`~~ RESOLVED
- ~~HEALTH-01 schema + validation scenario~~ RESOLVED
- **REMAINING**: `nucleus_launcher` cross-compile for aarch64 (LAUNCHER-01)
- **REMAINING**: BTSP-E2E-01 handshake validation scenario execution

### Springs — healthSpring

HEALTH-01 convergence + 12 unit tests landed (`c65f89a`). 15 upstream gaps in healthSpring FRAGO — stable workarounds.

### Gates

- **flockGate**: federation protocol gap. **DO NOT re-test** until songBird team resolves `federation.enabled=false`. See impulse.
- All other gates: operational. grapheneGate 13/13 alive.

### Gardens (cellMembrane)

Stream 2 infrastructure landed (`plasmid.build`, `deployment.toml`, gate profiles, health sweep). Remaining:
- BUILD-CACHE-01, BUILD-ELF-01, HARVEST-NAME-01 (build pipeline hardening)
- GATE-PROFILE-01 per-gate TOML wiring
- All Stream 5 divergence hardening items

---

## Remaining Summary

| Stream | Remaining | Resolved |
|--------|-----------|----------|
| 1: Startup Contract | 1 (bearDog) | 6 |
| 2: Build Pipeline | 5 (wiring + hardening) | 4 |
| 3: Health + Orchestration | 5 (3 primals + launcher + tolerances) | 4 |
| 4: BTSP E2E | 2 (handshake + grapheneGate) | 1 |
| 5: Cascade + qS/rP | 7 (all open) | 0 |
| Pending | flockGate federation (P2), sourdough segfault (LOW) | — |
| **Total** | **20 remaining** | **15 resolved this wave** |

---

## Active Documents

| Document | Purpose |
|----------|---------|
| This blurb | Wave 109 per-level guidance (mid-wave update) |
| `impulses/active/...wave109-guidestone-deployment-convergence.toml` | Main FRAGO — 5 streams |
| `impulses/active/...wave109-wan-federation-disabled.toml` | flockGate federation gap |
| `impulses/active/...wave107-healthspring-upstream-gaps.toml` | healthSpring gaps |
| `cellMembrane/AAR_CELLMEMBRANE_WAVE106_DETERMINISTIC_DEPLOYMENT_JUN10_2026.md` | Living deployment standard |

Archived: `archive/wave108/`, `archive/wave109/`.

---

**This is a long wave. Evolution trickles in. 15 of 35 items resolved. 4 primals still active. The work is convergence.**
