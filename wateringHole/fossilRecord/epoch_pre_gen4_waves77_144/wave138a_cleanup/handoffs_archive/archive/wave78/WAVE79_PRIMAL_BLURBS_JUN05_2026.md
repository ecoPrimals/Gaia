# Wave 79 Primal Blurbs — Copy-Paste to Teams

**Date**: 2026-06-05 | **From**: eastGate overwatch
**Context**: All 4 upstream gaps RESOLVED. UDS-only stadial gate established.
Transport evolution formalized (Phase 2: Songbird-routed IPC).

---

## songBird

Wave 81, 14,004+ tests, 73.4% coverage. BD-TRUST-01 + deep debt shipped.

**What landed**:
- `auth.exchange_trust` wired into `mesh.init` — the P0 blocker is DONE
- Deep debt: 8 hardcoded port literals → `songbird_types::defaults` constants
- Production stubs hardened (NFC x25519_dh, lineage verify, TLS extract)
- `capability_registry.toml` shipped
- Race conditions + flaky test patterns eliminated

**P0 — Transport Phase 2**: Evolve `ipc.resolve` to return
transport-qualified endpoints:
```json
{ "transport": "uds", "path": "/run/membrane/beardog.sock" }
{ "transport": "mesh_relay", "peer_id": "strand-gate", "capability": "security" }
{ "transport": "tcp", "host": "192.168.1.144", "port": 7700 }
```
This is the keystone for O(n) gate deployment. See FRAGO
`wave79-transport-evolution-capability-routing` and
`primalSpring/docs/TRANSPORT_EVOLUTION.md`.

**P1 — Coverage**: 73.4% → 90%. Largest gap in the ecosystem. Focus on
`songbird-config`, `songbird-nfc`, `songbird-tls`.

**P3 — Doc drift**: README says v0.2.8-wave76. You're at v0.2.9-wave81.

---

## nestGate

Session 94b, 12,551+ tests, ~84% coverage.

**P1 — Binary UDS compliance**: The deployed binary must respect
`--socket /run/membrane/nestgate.sock` natively (not via `/tmp` symlink).
This is blocking the VPS binary refresh. When the binary supports native
`--socket` path specification, plasmidBin can deploy port-free.

**P2 — Coverage**: 84% → 90%. Focus on content pipeline and HTTP API handlers.

---

## skunkBat

Wave 76b, v0.2.3, 500+ tests.

**P1 — Binary UDS compliance**: Deployed binary runs TCP-only on VPS
(localhost :9140, `--no-uds`). Target: native UDS support so skunkBat
runs port-free like other primals. Blocks full Tower Atomic on VPS.

**P2 — westGate readiness**: Enrollment FRAGO updated for UDS-only +
BD-TRUST-01 auto trust. See
`impulses/active/wave73-westgate-skunkbat-enrollment.toml`.

---

## toadStool

Session 293, 23,000+ tests, ~83.6% coverage.

**P2 — Coverage**: 83.6% → 90%. Hardware paths inherently gapped. Focus
on non-VFIO: coordination, dispatch, JSON-RPC surface, CallerContext.

**P2 — Binary UDS compliance**: VPS binary uses `/tmp/biomeos/` instead
of respecting launcher-injected `--socket` path. Needs update for
port-free VPS deployment.

---

## petalTongue

Wave 78, 6,259+ tests, ~85%+ coverage. Deep debt passes 4-5 done.

**P2 — Coverage**: 85% → 90%. You're close — continue sprint on
content-backend and discovery integration paths.

**P2 — Transport compliance**: Ensure binary doesn't default to TCP bind
when `--socket` is passed. Stale :8080 process needed manual kill on VPS.

---

## barraCuda

Wave 78, 4,393+ tests, ~81% coverage.

**P2 — Coverage**: 81% → 90%. GPU hardware cap on llvmpipe. Focus on
non-GPU paths: stats, linalg, precision routing, dispatch.

**P2 — Transport prep**: Ensure `--socket` / `--unix` flags work for
launcher-injected UDS paths. No `0.0.0.0` bind in default mode.

---

## sweetGrass

Wave 78b, v0.7.49, 1,623+ tests, 91.7% coverage.

**Unblocked**: rhizoCrypt DAG append + lifecycle wiring is DELIVERED.
Attribution braid testing against live mesh events is your next evolution
path. Low priority until VPS binary refresh lands.
