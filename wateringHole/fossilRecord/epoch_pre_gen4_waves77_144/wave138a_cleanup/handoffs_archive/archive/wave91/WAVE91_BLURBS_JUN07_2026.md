# Wave 91 Blurbs — Targeted by Team

**Date**: 2026-06-07
**From**: eastGate overwatch
**Cascade**: 38/38 parity | Depot: 14/14 current | Pipeline: end-to-end proven

---

## Status

All P1 deployment blockers are **RESOLVED** (Waves 87-90). Pipeline is proven
end-to-end: team push → cascade → harvest → depot → NUCLEUS → 12/12 ACTIVE →
federation :7700 LIVE. primalSpring role formalized as composition experimentation
laboratory. Three-tier model operational: primalSpring → cellMembrane → projectNUCLEUS.

**Deep debt sprint COMPLETE** (Wave 82c): primalSpring codebase fully modernized —
zero bash in production path, all validation gates in idiomatic Rust, default auth
Enforced (fail-closed), hardcoded routing eliminated. 931 tests, 0 failures.

---

## biomeOS Team — P2

**BIO-ORPHAN-01**: NUCLEUS exits after Neural API setup, leaving 12 primals running
as orphans. Second `biomeos nucleus start` fails because old primals hold sockets.

**Preferred fix**: NUCLEUS stays alive as supervisor process (enables lifecycle
monitoring, health probes, hot-reload). At minimum: detect existing primals on
startup and reattach, or clean stale sockets + check running PIDs before spawning.

This is the sole remaining code issue in the deployment pipeline. Not blocking
mesh proof, but blocks clean restart/upgrade cycles.

**Thank you** for v4.10 (BIO-SEARCH-01), v4.11 (SB-FEDERATION-01 bind), v4.12
(health retry). All validated and deployed.

---

## songBird Team — P2 (next evolution gate)

**SB-FEDERATION-01: RESOLVED.** Federation :7700 LIVE on eastGate + strandGate.

**Next**: Begin `ipc.resolve` structured endpoint work — Phase 2 Milestone 1 of
transport evolution (wave79 FRAGO). This is the evolution gate for the entire
ecosystem to move toward transport injection.

Current `ipc.resolve` returns raw path strings. Evolve to return structured
`TransportEndpoint`:

```json
{ "transport": "uds", "path": "/run/membrane/beardog.sock" }
{ "transport": "tcp", "host": "192.168.1.144", "port": 7700 }
{ "transport": "mesh_relay", "peer_id": "strand-gate", "capability": "security" }
```

This enables Tower Atomic to select transport without string parsing and is the
foundation for isomorphic deployment across VPS/desktop/container/WASM.

**Also**: 2-gate mesh proof coordination. strandGate has :7700 LIVE. eastGate has
:7700 LIVE. We need to coordinate `mesh.init` and verify `discovery.peers` returns
peer_count >= 1 + `mesh.health_check` all_healthy. This is a coordination task,
not a code issue.

---

## cellMembrane Team — Maintenance + Evolution

**CM-WEBHOOK-01 (P3)**: Cascade is still timer-polled (30-min). Webhook-driven
cascade from Forgejo push events would reduce push-to-VPS latency from 30 min
to ~2 min. Not blocking, but improves developer experience significantly.

**projectNUCLEUS consumption surface**: `primalSpring/specs/DOWNSTREAM_CONSUMPTION.md`
is published. cellMembrane's role in the three-tier chain: deploy validated patterns,
manage plasmidBin depot, VPS ops. projectNUCLEUS consumes the composition library
and certification engine from primalSpring; cellMembrane deploys the results.

**toadStool divergence**: Cascade detected non-ff divergence from ironGate (forgejo
+13 vs origin +126). Resolved at parity now (cascade auto-resolved via merge-ff policy).
Monitor for recurrence.

---

## strandGate — Coordination

**2-gate mesh proof**: Your Songbird :7700 has been LIVE since Wave 86. eastGate's
:7700 is now LIVE (Wave 89). We need to coordinate:

1. Run `mesh.init` from one gate targeting the other
2. Verify `discovery.peers` returns `peer_count >= 1`
3. Verify `mesh.health_check` shows `all_healthy: true`
4. Smoke test cross-gate `capability.call`

This proves the mesh at 2 gates. Additional gates (westGate, northGate, etc.)
enroll using the same template (see resolved FRAGO `wave73-westgate-skunkbat-enrollment`).

---

## All Other Teams — NO ACTION

Mountain is clear. No upstream primal work blocking deployment or mesh.
barraCuda socket fix validated. bearDog, NestGate, squirrel, rhizoCrypt, loamSpine,
sweetGrass, petalTongue, coralReef, skunkBat — all at zero debt, all deployed
from plasmidBin depot.

---

## Remaining Work Summary

| # | Item | Owner | Priority | Status |
|---|------|-------|----------|--------|
| 1 | 2-gate mesh proof (eastGate↔strandGate) | operators | P1 | UNBLOCKED — coordination |
| 2 | BIO-ORPHAN-01: NUCLEUS lifecycle | biomeOS | P2 | Open |
| 3 | songBird ipc.resolve structured endpoints | songBird | P2 | Not started |
| 4 | CM-WEBHOOK-01: webhook-driven cascade | cellMembrane | P3 | Not started |
| 5 | Transport injection (1/14 primals) | all primals | P2 | sporePrint only |
| 6 | S4 auth gate review | automated | P1 | Ends ~Jun 9 |

New gate enrollment (westGate, northGate, etc.) follows the resolved enrollment
template — not tracked as active work.

**Next evolution gate**: songBird `ipc.resolve` structured endpoints (M1). Once
shipped, all primals can begin transport injection evolution. The three-tier model
ensures patterns validated in primalSpring flow through cellMembrane deployment
to projectNUCLEUS packaging.

---

*"All P1 code blockers RESOLVED. Pipeline proven. Role formalized. Mesh proof is coordination, not code. Transport injection is the next evolution horizon."*
