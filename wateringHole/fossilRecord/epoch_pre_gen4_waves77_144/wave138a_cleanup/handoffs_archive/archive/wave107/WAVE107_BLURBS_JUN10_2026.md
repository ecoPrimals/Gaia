# Wave 107 Blurb — Per-Level Guidance

**Date**: 2026-06-10
**From**: eastGate overwatch
**FRAGO**: `impulses/active/2026-06-09T23-15_eastGate__wave106-cross-topology-validation.toml`

**State**: ZERO P1. S1-S4 ALL GRADUATED. 4-gate mesh collective LIVE. grapheneGate 12/13 (CR-TARPC-01 just resolved). **1 primal code blocker remains** (BM-UDS-01). Fix biomeOS → rebuild aarch64 → grapheneGate 13/13 → full ecosystem validation complete.

---

## Remaining Work — 6 P2, 18 LOW

| Level | P2 | LOW | Your Next Action |
|-------|-----|-----|------------------|
| **Primals** | 1 | 0 | biomeOS: fix BM-UDS-01 (skip Neural API UDS bind on tcp_only) |
| **primalSpring** | 1 | 1 | After BM-UDS-01 ships: absorb, rebuild aarch64, validate 13/13 on Pixel 8 |
| **Springs** | 1 | 15 | healthSpring: live signal dispatch test (nest.store/nest.commit on ironGate) |
| **Gates** | 2 | 0 | flockGate: power on + WAN e2e 5/5. grapheneGate: aarch64 rebuild after BM-UDS-01 |
| **Gardens** | 1 | 2 | cellMembrane: NDK cross-compile pipeline (aarch64-linux-android) |
| **TOTAL** | **6** | **18** | |

---

## Level 1: Primals (Mountain)

**One fix remains.** All other primal-level work is done.

### `BM-UDS-01` — biomeOS, P2

Neural API server unconditionally binds UDS before checking `PRIMAL_BIND_MODE`. When `tcp_only`, the bind crashes the process. v4.18 "native fallback" infrastructure exists but isn't wired into the Neural API bind path.

**Action**: Check `PRIMAL_BIND_MODE` before Neural API UDS `bind()`. Skip UDS when `tcp_only`. Same pattern coralReef just shipped for tarpc (b1ec1f4b).

**Unblocks**: grapheneGate 13/13 (currently 12/13 — biomeOS is the last blocked primal).

### Recently Resolved (this cascade)

- **CR-TARPC-01** (coralReef, b1ec1f4b): tarpc skips bind on tcp_only. grapheneGate → 12/13.
- **NG-DOWNCAST-01** (nestGate, 7c3fe9a6): `is_platform_constraint()` walks full error chain. Workaround removed.
- **TOADSTOOL-SOCKET-CLEANUP**: 3-tier resolution VERIFIED. `/tmp` fallback only via `temp_dir()`.
- **SKUNKBAT-TCP-9750**: Federation port DROPPED. Zero-port standard fully compliant.

---

## Level 2: primalSpring

**Blocked on Level 1.** Once BM-UDS-01 ships:

1. Absorb fix into primalSpring grapheneGate handler
2. Rebuild all 13 primals for `aarch64-unknown-linux-musl` on peptidoglycan
3. Push to VPS depot, update checksums.toml
4. Deploy to Pixel 8 via `deploy_pixel.sh`
5. Validate `--composition full` → 13/13 alive in primalSpring scenarios

**Current**: 901 tests, 55 scenarios, 0 clippy. grapheneGate readiness scenario tracks BM-UDS-01 as structural blocker — will auto-pass when fix lands.

### LOW

- `PB-FORWARD-01`: deploy_pixel.sh ADB port conflict — silent failure. P3 convenience fix.

---

## Level 3: Springs

### healthSpring — ironGate (1 P2, 15 LOW)

**P2**: `GAP-47-SIGNAL-DISPATCH-LIVE` — live test `nest.store`/`nest.commit` against biomeOS on ironGate with signal graphs loaded. Signal-collapse provenance pipeline (2 biomeOS calls replace 5-step manual chain).

**15 LOW** — all with stable workarounds. See healthSpring FRAGO (`impulses/active/2026-06-10T14-20_ironGate__wave107-healthspring-upstream-gaps.toml`). Key items:
- `GAP-02-NESTGATE-EGRESS` (MEDIUM): egress fence for clinical data sovereignty
- `GAP-22-SOCKET-DISCOVERY` (LOW): may be resolved by biomeOS auto-register + ipc.resolve — needs verification

### Other Springs — At Parity

| Spring | Gate | Status |
|--------|------|--------|
| wetSpring V199 | southGate | 2,100/2,100 tests, 51 capabilities. TransportEndpoint confirmed on live mesh. |
| neuralSpring V182 | southGate | Inference provider registration shipped (squirrel register/unregister). |
| hotSpring | biomeGate | At parity. biomeGate OFFLINE (kernel recovery). |
| airSpring | eastGate | At parity. |
| groundSpring | eastGate | At parity. |
| ludoSpring | ironGate | At parity. |

---

## Level 4: Gates

### Operational (no code changes needed)

| ID | Owner | Action |
|----|-------|--------|
| `FLOCKGATE-WAN-E2E` | flockGate ops | Power on → re-fetch from VPS → `mesh.init [RELAY_PUBLIC]:7700` → verify 5/5 e2e |
| `GRAPHENEGATE-REBUILD` | primalSpring + cellMembrane | **After BM-UDS-01**: aarch64 rebuild on peptidoglycan → push checksums.toml → `deploy_pixel.sh` → 13/13 alive |

### Gate Enrollment

All gates: `membrane gate.bootstrap <gate-name>` (6-phase deterministic). Mobile NUCs: add `--mobile` or use `provision-golgi.sh <gate-name>`.

### Hardware Pipeline

| Gate | Status |
|------|--------|
| biomeGate | OFFLINE (kernel recovery) |
| westGate | INCOMING (Nest Atomic cold storage) |
| northGate, swiftGate, kinGate | Hardware ready, not deployed |

---

## Level 5: Gardens (cellMembrane, NUCLEUS, FOUNDATION)

### cellMembrane — 1 P2, 2 LOW

| Item | Priority | Status |
|------|----------|--------|
| NDK cross-compile (`aarch64-linux-android`) | P2 | Target on peptidoglycan for native Android. bearDog StrongBox is forcing function. |
| BearDog ACME cutover | LOW | TlsProvider wired, awaiting BearDog ACME client. Caddy LE works. |
| Forgejo Actions CI | LOW | .forgejo/workflows/ci.yml shipped, evaluation ongoing. |

### Recently Shipped (cellMembrane)

- **CM-VPS-DEPOT-SYNC** (ef3f0b8): BLAKE3 diff, atomic copy, checksums verification. Depot sync is operational.
- **MOBILE-GOLGI-FLEET** (9e07b01): GateMobility type, `--mobile` bootstrap, systemd templates, NM auto-reconnect.

### projectNUCLEUS / projectFOUNDATION

At parity. NUCLEUS consumption surface published. FOUNDATION drift detection shipped.

---

## Ecosystem Snapshot

| Metric | Value |
|--------|-------|
| P1 | **ZERO** |
| P2 | **6** (1 primal code, 2 gate ops, 3 spring/garden) |
| LOW | **18** (3 ecosystem + 15 healthSpring upstream) |
| Sovereignty | **S1-S4 ALL GRADUATED** |
| Mesh | **4-gate collective** (eastGate↔golgiBody↔ironGate+southGate) |
| grapheneGate | **12/13** (BM-UDS-01 last blocker) |
| Depot | 13/13 x86_64 BLAKE3 verified, 14/14 aarch64 built |
| Transport | 11/11 non-exempt |
| Cascade | 38/38 clean |
| Socket cleanup | **5/5 VERIFIED** |
| Zero-port standard | **CLEAN** (all federation ports dropped) |
| Deployment | Deterministic — gate.bootstrap + gate.status + supervision + depot_sync + mobile fleet |

---

## Active Documents

| Document | Purpose |
|----------|---------|
| **This blurb** | Per-level guidance for handoff |
| `WAVE107_REMAINING_SCOPE_BY_LEVEL_JUN10_2026.md` | Full breakdown with validation gates |
| `cellMembrane/AAR_CELLMEMBRANE_WAVE106_DETERMINISTIC_DEPLOYMENT_JUN10_2026.md` | Living deployment standard — 6 invariants |
| `impulses/active/...wave106-cross-topology-validation.toml` | Main FRAGO — refocused on 6 remaining items |
| `impulses/active/...wave107-healthspring-upstream-gaps.toml` | healthSpring 15 upstream gaps |

**Archived** (`archive/wave107/`): 11 handoffs + 4 FRAGOs. Full wave history preserved.

---

## Critical Path

```
biomeOS ships BM-UDS-01
  → primalSpring absorbs
    → peptidoglycan rebuilds aarch64
      → grapheneGate 13/13
        → full ecosystem validation complete
```

One primal fix. Then the mountain is clear.
