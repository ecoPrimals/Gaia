# wetSpring V202 — Wave 111 Mesh Health Audit + Discovery Dedup

**Date**: 2026-06-11
**From**: southGate (wetSpring team)
**Wave**: 111 — Gate Expansion + Federation Completion + Sandbox Graduation
**FRAGO**: `impulses/active/2026-06-11T21-30_eastGate__wave111-gate-expansion-federation-sandbox.toml`

---

## Summary

wetSpring V202 ships `composition.mesh_health` — a NUCLEUS mesh health audit
endpoint with version skew detection. This directly addresses Wave 111 Stream 6
(Divergence Pressure), providing a concrete diagnostic tool for detecting stale
binaries and version skew across local NUCLEUS deployments.

Additionally: Songbird capability.resolve RPC code deduplicated (30+ lines),
upstream Wave 108-111 reviewed with no breaking changes found.

---

## What Shipped

| Item | Detail |
|------|--------|
| `composition.mesh_health` | Probes all 13 NUCLEUS primals: liveness, version, uptime |
| `MeshHealthAudit` | `version_skew: bool`, `distinct_versions[]`, per-primal info |
| Songbird RPC dedup | `songbird_capability_resolve()` extracted as shared helper |
| Capability registration | niche (52), dispatch (47), domains (22), registry updated |
| 7 new tests | mesh probe, JSON shape, absent-when-no-nucleus, dispatch, skew |
| Module docs | 4-tier cascade, composition.mesh_health in method table |

---

## Build Gate

- **Tests**: 2,124 workspace (0 failures)
- **Clippy**: zero warnings (pedantic + nursery)
- **Unsafe**: zero (`forbid(unsafe_code)`)

---

## Upstream Review (Wave 108-111)

Manual sync completed (cascade TOML parse error on northGate — cellMembrane fix needed).

| Primal | Changes | Impact on wetSpring |
|--------|---------|---------------------|
| barraCuda | Wave 109 startup convergence (`--bind-mode`), local TransportEndpoint | None — deploy flag, not wire format |
| nestGate | Session 102 HTTP-on default, BLAKE3 centralization | None — wetSpring uses `storage.*` over UDS |
| coralReef | Transport evolution, 3304 tests | None |
| sweetGrass | Socket cleanup, v0.7.55 | None |
| rhizoCrypt | Debt sweep | None |
| petalTongue | Wave 107 | None |
| skunkBat | Refactor | None |
| toadStool | Socket cleanup ACK | None |

**Verdict**: V200-V201 already absorbed the Wave 107 changes. No new code changes
needed from Wave 108-111 upstream. wetSpring is at full parity.

---

## Stream 6 Contribution: Divergence Detection

The `composition.mesh_health` endpoint enables:

1. **Version skew detection**: `distinct_versions` array shows all unique versions
   across live primals. `version_skew: true` when >1 distinct version detected.
2. **Staleness audit**: Per-primal status (live/discovered/absent) + optional
   `uptime_secs` for health-aware diagnostics.
3. **Automated mesh validation**: Callable via JSON-RPC (`composition.mesh_health`)
   from primalSpring scenarios, cellMembrane health audits, or manual debugging.

This directly supports Wave 111 Stream 6 scenarios:
- `CROSS-GATE-SKEW-REPORT`: wetSpring can report local version skew
- `S_VERSION_SKEW`: primalSpring can call `composition.mesh_health` on any gate

---

## Cascade TOML Parse Error (cellMembrane)

`membrane temporal.cascade` fails with:
```
TOML parse error at line 608, column 1
[gates.northGate]
missing field `repos`
```

northGate was added to the cascade config (Wave 111) without a `repos` field.
Manual sync completed for all repos. cellMembrane team should add `repos = []`
or the repo list to the northGate entry.

---

## Remaining wetSpring Gaps

| Priority | Item | Status |
|----------|------|--------|
| HIGH | WS-11: GPU shader binomial model | CPU shipped (V201), GPU deferred |
| MEDIUM | WS-9: Cross-tier parity L3 | Scaffolding ready, needs live NUCLEUS trio |
| MEDIUM | Tenaillon 2016 ferment transcripts | Data exists (~200 GB), pipeline not wired |
| MEDIUM | `nest.sync` orchestration | Blocked on biomeOS nest.sync E2E |
| LOW | `math-{family}.sock` discovery fallback | Fine with symlink, brittle without |

---

## Git

```
V202 commit: pending push
Tests: 2,124 (0 failures)
Clippy: zero warnings
```
