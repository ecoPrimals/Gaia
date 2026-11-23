# primalSpring Wave 74 — Upstream Primal Audit

**Date**: 2026-06-03
**Author**: eastGate (primalSpring evolution team + overwatch)
**Audience**: All upstream primal teams

---

## Critical Path Status

```
Songbird cap propagation ──→ cross-gate capability.call ──→ plasmodium collective
                                        │
                                        ├──→ perceptron pipeline (barraCuda ready)
                                        └──→ multi-gate composition validation
```

## Per-Team Status & Gaps

### Songbird (CRITICAL PATH — P1 BLOCKER)

| Item | Status | Detail |
|------|--------|--------|
| HTTP dispatch (d6a6f714) | **FIXED** | HTTP POST to /jsonrpc works end-to-end |
| Virtual relay Phase 2 | **DELIVERED** | Default virtual endpoints, BTSP session validation |
| Capability advertisement propagation | **OPEN P1** | discovery.peers returns `capabilities: []` for remote peers |
| HTTP/UDS state unification | **OPEN P1** | ipc.register + mesh.init separate per transport |
| mesh_seed auto-bootstrap | **NOT FIXED** | manual mesh.init still required |
| latency_ms population | **NOT FIXED** | null in all responses |

**Action**: FRAGO `wave74-songbird-capability-propagation` filed. Items 3-4 are
the only blockers to cross-gate capability routing. After those ship, plasmodium
collective validation can proceed.

### barraCuda

| Item | Status | Detail |
|------|--------|--------|
| ml.perceptron_train | **COMPLETE** | <150ms, accepts raw telemetry records |
| ml.mlp_train (legacy) | **COMPLETE** | 36→16 perceptron |
| Deep debt | Maintenance | Wave 68 complete |

**Status**: Ready for primalSpring integration. Wire contract documented.
Blocked on cross-gate capability.call for live dispatch from eastGate.

**primalSpring has**: 36-dim feature extraction module (`perceptron.rs`),
training data generator, JSONL serialization. Needs: cross-gate routing to
strandGate where barraCuda runs.

### bearDog

| Item | Status | Detail |
|------|--------|--------|
| auth.verify_ionic scopes (w131) | **FIXED** | Top-level scopes field |
| AI migration (w132) | **DELIVERED** | Mobile gate support |
| Deep debt + env (w133) | **DELIVERED** | |
| ACME refactor (w134) | **DELIVERED** | |
| health.liveness method | **GAP** | bearDog uses `health` not `health.liveness` |

**Action**: Standardize health method name to `health.liveness` per ecosystem
convention, OR update consumers to use `health`. Minor — not blocking.

### biomeOS

| Item | Status | Detail |
|------|--------|--------|
| composition.reload (v4.00) | **DELIVERED** | Hot-reload compositions |
| Perceptron consumer (shadow) | **DELIVERED** | Ingests neural_routing_perceptron.bin |
| SONGBIRD_MESH_ENABLED alignment | **OPEN P2** | Uses different env var than Songbird |
| gate.register validation | **BLOCKED** | Needs Songbird dispatch fix |

### NestGate

| Item | Status | Detail |
|------|--------|--------|
| ZFS backend (s85) | **DELIVERED** | |
| content.replicate.pull (s85) | **DELIVERED** | |
| route.register (s85) | **DELIVERED** | |
| Streaming snapshots (s86) | **DELIVERED** | |
| Deep debt sweep (s87) | **DELIVERED** | |

**Status**: Clean. No blocking gaps.

### petalTongue

| Item | Status | Detail |
|------|--------|--------|
| Sovereign mesh integration (v168) | **DELIVERED** | |
| Sovereign verify (Wave 74) | **DELIVERED** | |

**Status**: Clean.

## primalSpring Deliveries (Wave 72-74)

| Item | Tests | Status |
|------|-------|--------|
| Live 2-gate mesh validation | — | COMPLETE |
| s_covalent_mesh wire format fix | 2 | COMPLETE |
| Perceptron feature extraction (36-dim) | 12 | COMPLETE |
| MeshTopology model | 7 | COMPLETE |
| Plasmodium collective scenario | 2 | COMPLETE |
| Dual membrane path scenario | 3 | COMPLETE |
| SecurityVerifier bearDog w131 integration | 7 | COMPLETE |
| CompositionContext gate_id | — | COMPLETE |
| westGate enrollment FRAGO | — | FILED |
| Songbird capability propagation FRAGO | — | FILED |
| **Total** | **836 tests, 60 scenarios, zero clippy** | |

## Open FRAGOs (Active)

| ID | To | Priority | Subject |
|----|-----|----------|---------|
| wave74-songbird-capability-propagation | songBird | P1 | Capability advertisement propagation via mesh |
| wave73-westgate-skunkbat-enrollment | westGate | P2 | Family seed + enrollment protocol |
| wave72-strandgate-compute-trio-pickup | strandGate | P2 | barraCuda + coralReef SPIR-V |

## Mesh Validation Progression

```
Wave 49: Scenario written, no live test
Wave 51: mesh_seed module shipped, format parser fixed
Wave 55: southGate federation attempted, cross-subnet failed
Wave 67: strandGate auto-discovered via UDP, TLS failed
Wave 72: ██████████░░░░ 70% — discovery LIVE, dispatch BLOCKED (raw TCP)
Wave 74: ████████████░░ 85% — HTTP dispatch FIXED, cap propagation BLOCKED  ← HERE
Wave 75: Target — capability.call cross-gate (needs Songbird propagation)
Wave 76: Target — 3-gate plasmodium + perceptron pipeline live
```

## DNS / Dual Membrane Status

| Layer | Path | Status |
|-------|------|--------|
| Outer (Cloudflare) | www/primals.eco → CF tunnel → VPS | LIVE (shadow) |
| Inner (BTSP) | membrane.primals.eco → sovereign NS → VPS | LIVE (validated) |
| Verification | dual-membrane-path scenario | 14/14 PASS |

No NS cutover needed — Cloudflare stays as outer membrane. Sovereign DNS
resolves BTSP endpoints directly for Dark Forest inter-gate traffic.

---

*This audit is for upstream ingestion. All teams should check their entries
above. Songbird capability propagation is the single critical path item.*
