# AAR — footPrint Phase 2 Deployment on ironGate

**Date**: 2026-08-04 | **Gate**: ironGate | **Wave**: 156d
**Commits**: `65fcc66..a498566` (8 commits, +1,976 / -254 lines, 28 files)

---

## Mission

Deploy footPrint as a persistent Phase 2 service on ironGate with full CAS integration, eliminate all technical debt identified in audit, and validate the primal-to-product stack end-to-end.

---

## Outcome: SUCCESS

footPrint is **deployed and operational** on ironGate as a systemd service with CAS persistence via nestGate TCP local-trust.

---

## What Went Right

1. **TCP local-trust discovery** — BTSP on UDS was blocking CAS writes. Discovered nestGate exposes TCP JSON-RPC on port 8080 with no BTSP requirement for same-gate services. This unblocked the entire CAS integration path without needing a TypeScript BTSP client or upstream nestGate changes.

2. **Manifest-driven architecture** — The SourceManifest registry cleanly replaces hardcoded endpoints. Sources self-gate on endpoint availability. Category boosts derive from coverage areas. CSP hosts derive from registered endpoints. The system is genuinely capability-based now.

3. **Coverage expansion velocity** — Went from ~560 to 708 tests across the session by targeting testable logic in untested modules (properties, dimensions, sources, intelligence). Focused on pure functions and data transformations rather than fighting DOM coupling.

4. **riboCipher transport** — The 2-byte prefix (`0xEC 0x01`) for NUCLEUS UDS is now understood and implemented, even though TCP is the primary path. This knowledge is preserved for future biomeOS capability routing.

5. **Production validation on live hardware** — CAS put/get/list E2E verified against live nestGate. Agent bridge WebSocket verified. systemd service installed and running. WireGuard path accessible from mesh.

---

## What Went Wrong

1. **BTSP investigation consumed hours** — Deep-dived into X25519 DH handshake, `--dev` flags, FAMILY_ID removal before discovering the TCP path. Could have been avoided if nestGate's TCP local-trust mechanism was documented in wateringHole earlier.

2. **Overwatch blurb stale on footPrint** — The ecosystem blurb says "628 tests" and "BTSP local-trust needed" — both resolved. Downstream consumers of the blurb may make incorrect planning assumptions.

3. **golgi Caddy misconfiguration** — `footprint.primals.eco` routes to an old static deployment on sporeGate, not ironGate `:3002`. The frontend loads but API calls fail. This is a sporeGate routing ticket, not a footPrint issue.

---

## Key Decisions Made

| Decision | Rationale |
|----------|-----------|
| TCP over UDS for CAS | BTSP is mandatory on UDS when FAMILY_ID is set. TCP on localhost provides equivalent security (same-gate, loopback only) without the auth overhead. |
| Content-addressed API (BLAKE3 hashes, not keys) | Aligned to nestGate's actual protocol. `content.put` returns hash, `content.get` takes hash. No key-value semantics. |
| Self-knowledge cleanup | Removed primal names from user-facing strings. "RPC bridge" instead of "petalTongue bridge". Promotes discovery over static coupling. |
| No Rust migration for deps | footPrint is a protist (browser+Node). Its deps (leaflet, turf, geoman) are browser-appropriate. The Express server disappears into primals — no point evolving it to Rust. |
| systemd as irongate user | No `membrane` user on this gate. Primals run as root/service accounts, protists run as the gate user. |

---

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| Tests | ~560 | 708 |
| Test files | ~43 | 53 |
| Statement coverage | ~48% | 59% |
| Line coverage | ~50% | 61% |
| TypeScript errors | 0 | 0 |
| ESLint errors | 0 | 0 |
| TODOs in source | 0 | 0 |
| Largest file | 592L | 592L (server.ts) |
| CAS integration | Blocked (BTSP) | Live (TCP) |
| Service status | Manual start | systemd enabled |

---

## Upstream Actions Required

| Item | Owner | Priority |
|------|-------|----------|
| Update golgi Caddy: `footprint.primals.eco` → `10.13.37.7:3002` with WS upgrade | sporeGate | P1 |
| Update overwatch blurb: 708 tests, BTSP resolved, Phase 2 DEPLOYED | eastGate | P2 |
| Document nestGate TCP local-trust in wateringHole standards | nestGate team | P2 |
| `content.delete` method (not implemented) | nestGate team | P3 |

---

## Lessons for Ecosystem

1. **Always probe TCP before fighting BTSP** — nestGate's TCP JSON-RPC (port 8080) is the intended local-trust path for same-gate services. UDS+BTSP is for cross-gate and sensitive operations.

2. **Protists don't need Rust** — browser clients and thin Node servers are correctly TypeScript. The Rust boundary is at primals. Don't waste cycles "evolving" web deps to Rust.

3. **Coverage targets should exclude DOM-heavy modules from unit tests** — the remaining 38% client coverage gap is modules that need E2E (Playwright), not more vi.mock() gymnastics.

4. **Overwatch blurbs should pull test counts from CI, not manual entry** — the 628→708 discrepancy persists because the blurb is hand-edited.

---

## State at Close

```
footPrint Phase 2: DEPLOYED on ironGate
  systemd: active (running), enabled
  Port: 3002 (Express production)
  CAS: TCP 127.0.0.1:8080 → nestGate (3 objects stored)
  Agent bridge: ws://localhost:3002/ws/bridge (responding)
  WireGuard: 10.13.37.7:3002 reachable from mesh
  NUCLEUS: 26 sockets in /run/membrane/
  Tests: 708 passing, 0 errors
  Blocker: golgi Caddy routing (sporeGate ticket)
```

---

*Phase 2 is live. footPrint produces and consumes content-addressed data on ironGate's NUCLEUS. The protist-to-primal composition pattern is validated end-to-end.*
