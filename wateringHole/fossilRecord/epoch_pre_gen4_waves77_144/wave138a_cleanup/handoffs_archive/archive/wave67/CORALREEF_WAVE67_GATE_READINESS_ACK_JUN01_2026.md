# coralReef — Wave 67 Gate Deployment Readiness ACK

**Date**: 2026-06-01  
**Impulse**: `2026-06-01T13-32-eastGate-wave67-strandgate-provenance-compute-gate-deploy`  
**Status**: ACKNOWLEDGED — Ready for deployment

---

## strandGate Assignment

coralReef is part of the **compute trio** on strandGate (Dual EPYC 7452, 256GB ECC).
Deployment planned after Phase 1 mesh validation (3+ gates proven on LAN).

## Gate-Readiness Verification

| Requirement | Status | Evidence |
|-------------|--------|----------|
| TCP bind for LAN access | ✅ | `CORALREEF_TCP_BIND` env override, defaults `127.0.0.1:0` |
| `primal.announce` | ✅ | capabilities, methods, cost_hints, latency_estimates, signal_tiers |
| `capability.register` | ✅ | Sends provides + requires + transports (populated after bind) |
| Cross-gate routing | ✅ | Transparent via biomeOS + Songbird `capability.call` |
| No hardcoded addresses | ✅ | Zero hardcoded IPs/primal-names in production code |
| BTSP authenticated IPC | ✅ | Phase 3 (ChaCha20-Poly1305 + HKDF) |
| Socket resolution | ✅ | 3-tier: `BIOMEOS_SOCKET_DIR` → `XDG_RUNTIME_DIR/biomeos` → `/run/biomeos` |
| Zero unsafe | ✅ | `#![forbid(unsafe_code)]` all crates |
| Test coverage | ✅ | 3234 tests, zero warnings |

## No Code Changes Required

coralReef's existing architecture fully supports cross-gate compute dispatch:
- NUCLEUS launcher sets `CORALREEF_TCP_BIND=0.0.0.0:<port>` at deploy time
- biomeOS discovers coralReef via local `primal.announce` on the UDS
- Cross-gate requests from biomeGate route through Songbird → biomeOS → coralReef
- coralReef compiles and responds — no mesh awareness needed in the compiler

## Blocking On

Nothing from coralReef side. Awaiting:
1. Phase 1 mesh validation (eastGate ↔ southGate proving `discovery.peers` + `capability.call`)
2. strandGate NUCLEUS bootstrap (deploy graph applied)

---

*Wave 67. Compute trio ready. Awaiting mesh gate.*
