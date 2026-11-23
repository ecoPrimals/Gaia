# Wave 92 Blurbs — Targeted by Team

**Date**: 2026-06-07
**From**: eastGate overwatch
**Cascade**: 38/38 parity | Depot: 13/13 rebuilt + pushed to VPS | Pipeline: validated

---

## Status

All Wave 91 blurbed items were responded to **same-day** by all three teams:

| Item | Owner | Status |
|------|-------|--------|
| BIO-ORPHAN-01 (NUCLEUS lifecycle) | biomeOS | **RESOLVED** — v4.13 supervisor + SIGTERM |
| CM-WEBHOOK-01 (webhook cascade) | cellMembrane | **RESOLVED** — webhook handler + HMAC + selective harvest |
| TransportEndpoint canonicalization | songBird | **SHIPPED** — types in songbird-types |

VPS deployment validated: 13/13 binaries rebuilt and pushed to golgiBody via
`membrane plasmid.harvest` + `plasmid.refresh`. Depot symlink fixed. Checksums synced.

---

## cellMembrane Team — P1 (peptidoglycan depot + pipeline)

### Architecture Handoff: Peptidoglycan Shared Depot

See full spec: `WAVE92_PEPTIDOGLYCAN_DEPOT_ARCHITECTURE.md`

peptidoglycan (10.116.0.4) sits between inner and outer golgiBody on the VPC.
It has Rust 1.96, 4GB RAM, 79GB disk. It should host the **canonical binary depot**
so either membrane side can serve. The topology:

```
gates (build) → peptidoglycan (store) → golgiBody inner (LAN serve)
                                       → golgiBody outer (GitHub sync)
```

### Two build paths — both flow through pepti:

**Path A — Gate-pushed builds (preferred for large primals):**
Gates build locally on cascade, push ecobins to peptidoglycan depot.
Evolve `temporal.cascade` to support `--with-harvest`: sync repos, detect drift,
build locally, push binary + checksums to pepti in one flow. This makes binary
freshness part of the cascade contract.

**Path B — Peptidoglycan builds (fallback for small primals):**
pepti builds locally when gates haven't pushed. Needs `rustup target add
x86_64-unknown-linux-musl` (one-time). Monitor OOM on 4GB for large primals.

### Immediate items:

1. **CM-PEPTI-SSH-01**: golgiBody → peptidoglycan SSH host key trust (currently fails)
2. **VPS-BUILD-01**: `plasmid-pipeline.service` must NOT `cargo build` on golgiBody.
   Replace with: pull from pepti depot OR accept gate-pushed refresh.
3. **musl target on pepti**: `rustup target add x86_64-unknown-linux-musl`
4. **`--with-harvest` flag**: `temporal.cascade --with-harvest` builds drifted
   primals locally and pushes binaries + checksums as part of cascade.
5. **Depot report in cascade**: cascade output should include binary freshness
   (current/drifted count) alongside repo parity.

### Cosmetic: `plasmid.status` reports beardog + skunkbat as "drifted" despite
matching provenance commits. Likely stale freshness.toml on VPS. P3.

---

## songBird Team — P2 (next evolution gate)

**TransportEndpoint shipped** — thank you. Next step for Phase 2 M1:

Wire `ipc.resolve` to return `TransportEndpoint` instead of raw path strings.
This is the gate for all primals to begin transport injection. Once `ipc.resolve`
returns structured endpoints, `CompositionContext` in primalSpring can query
Songbird instead of probing sockets directly.

---

## strandGate — P1 Coordination

**2-gate mesh proof**: Both gates have Songbird :7700 LIVE. We need to coordinate:

1. `mesh.init` from one gate targeting the other
2. `discovery.peers` returns `peer_count >= 1`
3. `mesh.health_check` all_healthy
4. Cross-gate `capability.call` smoke test

This is the sole remaining P1 item and is coordination, not code.

---

## All Other Teams — NO ACTION

Mountain clear. All P1 and P2 code items resolved. 13/13 primals deployed
from plasmidBin depot on VPS. S4 auth gate review ends ~Jun 9 (automated).

---

## Remaining Work

| # | Item | Owner | Priority | Status |
|---|------|-------|----------|--------|
| 1 | 2-gate mesh proof | operators | P1 | UNBLOCKED — coordination |
| 2 | Peptidoglycan shared depot architecture | cellMembrane | P1 | Spec delivered — execute |
| 3 | VPS-BUILD-01: pipeline builds on toolchain-less VPS | cellMembrane | P1 | Open — blocked on #2 |
| 4 | CM-PEPTI-SSH-01: golgiBody→pepti SSH trust | cellMembrane | P1 | One-time setup |
| 5 | `--with-harvest` cascade flag | cellMembrane | P1 | Design delivered |
| 6 | songBird ipc.resolve structured endpoints | songBird | P2 | Types shipped, wiring next |
| 7 | Transport injection (1/14 primals) | all primals | P2 | Blocked on ipc.resolve |
| 8 | S4 auth gate review | automated | P1 | Ends ~Jun 9 |
| 9 | VPS plasmid.status drift (cosmetic) | cellMembrane | P3 | beardog/skunkbat false drift |

---

*"All code items resolved. Pipeline proven gate-to-VPS. Mesh proof is next. Transport evolution has started."*
