# sweetGrass v0.7.56 — Wave 109 Handoff: BTSP E2E Readiness + HEALTH-01

**Date**: June 11, 2026  
**Primal**: sweetGrass  
**Gate**: strandGate  
**Wave**: 109  
**Tests**: 1,636 passing, 0 failed  
**Clippy**: Zero warnings (pedantic + nursery)

---

## Summary

Wave 109 assigned sweetGrass to **Stream 4: BTSP E2E** (`BTSP-E2E-01`).
This release closes three gaps that would have caused E2E failures:

1. **BEARDOG_SOCKET in BTSP resolution** — deployments setting only
   `BEARDOG_SOCKET` (not `SECURITY_PROVIDER_SOCKET`) now find BearDog
   for BTSP handshake. Previously only `CryptoDelegate` (braid signing)
   checked `BEARDOG_SOCKET`; the BTSP handshake path did not.

2. **HEALTH-01 convergence** — bare `{"method":"health"}` now resolves
   to `health.check` via alias table. Response enriched with `primal` and
   `uptime_secs` to match the emerging `{status, primal, version, uptime_s}`
   probe schema.

3. **Zero clippy warnings** — doc backtick fix in new BTSP resolution docs.

---

## Key Changes

| File | Change |
|------|--------|
| `btsp/server.rs` | `resolve_security_socket_from_env()` now checks `BEARDOG_SOCKET` as tier 2 |
| `handlers/jsonrpc/registry.rs` | Added `("health", "health.check")` to ALIASES |
| `handlers/jsonrpc/health.rs` | `health.check` response includes `primal` + `uptime_secs` |
| `handlers/jsonrpc/tests.rs` | `test_bare_health_alias`, enriched `test_health_method` |
| `btsp/server.rs` (tests) | `resolve_security_socket_beardog_env` |

## BTSP E2E Readiness Status

| Component | Status |
|-----------|--------|
| Phase 1–2 server handshake | Implemented (BearDog delegation, length-prefixed + JSON-line) |
| Phase 3 ChaCha20-Poly1305 | Implemented (HKDF, AEAD framing, negotiate handler) |
| TCP BTSP enforcement | Implemented (raw JSON-RPC rejected with -32001 when FAMILY_ID set) |
| BearDog socket resolution | **Fixed** — BEARDOG_SOCKET now checked by BTSP path |
| Health probe schema | **Fixed** — `{status, primal, version, uptime_secs}` + bare `"health"` alias |
| Post-handshake framing | Length-prefixed JSON-RPC (canonical) or JSON-line (primalSpring compat) |
| BTSP test coverage | 88 tests (59 btsp/ unit + 6 integration + 23 supporting) |

## Remaining E2E Notes for primalSpring

sweetGrass is the **server under test** for BTSP-E2E-01. primalSpring
drives the E2E validation. Key integration notes:

- **TCP port**: `--port 9850` or `SWEETGRASS_PORT=9850` for TCP JSON-RPC
- **BTSP activation**: requires `FAMILY_ID` + `FAMILY_SEED` + BearDog socket
- **Post-handshake**: expects length-prefixed JSON-RPC frames (not newline)
- **Phase 3**: client sends `btsp.negotiate` with `"chacha20-poly1305"` for
  encrypted framing; omit for plaintext
- **Health probe**: `health.check` or bare `health` — both work

## Metrics

| Metric | Value |
|--------|-------|
| Version | v0.7.56 |
| Tests | 1,636 passing |
| Aliases | 11 (was 10) |
| Methods | 40 semantic |
| Clippy | 0 warnings |

---

*sweetGrass v0.7.56 — BTSP E2E ready, HEALTH-01 converged.*
