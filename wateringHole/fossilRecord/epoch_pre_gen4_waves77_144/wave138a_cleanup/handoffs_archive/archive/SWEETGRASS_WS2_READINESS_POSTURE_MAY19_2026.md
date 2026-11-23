# sweetGrass — WS-2 (Cross-Spring RootPulse Exchange) Readiness Posture

**Date**: May 19, 2026
**From**: sweetGrass team
**Audit**: primalSpring River Delta gaps (May 19, 2026)
**Priority**: Informational — WS-2 is owned by biomeOS + trio

---

## sweetGrass Role in WS-2

sweetGrass is a **target of capability calls** within the RootPulse
composition, not a dispatcher. The `rootpulse.sync` or equivalent
NeuralAPI composition graph is biomeOS-owned (per the audit).

sweetGrass provides:
- `braid.create` / `braid.get` / `braid.query` / `braid.commit`
- `provenance.graph` / `attribution.chain`
- `attribution.witness` (JH-5 Phase 3 audit pipeline)

These are the endpoints that a cross-spring RootPulse graph would
invoke via `signal.dispatch` → provenance trio pipeline.

---

## What Exists

| Capability | Status | Notes |
|-----------|--------|-------|
| Braid CRUD over UDS | Operational | PG-52 resolved, `\n`-terminated |
| Braid CRUD over TCP | Operational (BTSP enforced) | v0.7.36+ |
| `provenance.graph` | Operational | Entity reference with `data_hash` |
| `attribution.chain` | Operational | By braid ID |
| `attribution.witness` | Operational | JH-5 Phase 3 endpoint |
| GAP-36 wire aliases | Operational | 10 aliases for downstream compat |
| `capabilities.list` | Operational | Method count, BTSP, transport |

## What's Missing (for WS-2 completion)

| Capability | Status | Owner |
|-----------|--------|-------|
| `braid.sync` | Not implemented | sweetGrass (when biomeOS graph spec lands) |
| `braid.partial_update` | Not implemented | sweetGrass (signal target) |
| `braid.complete` | Not implemented | sweetGrass (signal target) |
| Braid subset query API | Not implemented | sweetGrass |
| `rootpulse.sync` graph | Not defined | biomeOS |
| `signal.dispatch` integration | Not implemented | biomeOS → sweetGrass |

## Readiness Assessment

sweetGrass's existing braid CRUD and provenance API surface is
**sufficient for intra-NUCLEUS RootPulse** (single composition).
WS-2 cross-spring exchange requires three additions:

1. **`braid.sync`** — Accept a braid subset request (filter by tags,
   time range, entity hash) and return matching braids with provenance
   continuity. Wire format TBD by biomeOS graph spec.

2. **`braid.partial_update` / `braid.complete`** — Signal handlers
   that accept notification from biomeOS `signal.dispatch` when a
   DAG node seals or session closes. These trigger braid enrichment
   or propagation to lithoSpore.

3. **Braid subset query** — Extend `braid.query` with cross-spring
   metadata (source spring, session scope, differential since timestamp).

None of these block current operations. sweetGrass will implement
them when biomeOS defines the `rootpulse.sync` composition graph.

---

## Deep Debt Status (May 19, 2026)

Full 12-category audit: **zero production findings**.
`uds.rs` refactored (779 → 674 lines), redb path inconsistency fixed.
1,553 tests, 0 clippy warnings, 193 source files, 55,184 LOC.
