# rhizoCrypt Wave 151b — BTSP Client + Deep Debt Final

**Date**: Jul 26, 2026 | **Head**: `7e61455` | **Wave**: 151b

## Summary

rhizoCrypt implements the consumer-side BTSP `ClientHello` 4-step
handshake for outbound UDS connections to bearDog. Additionally, a
comprehensive deep-debt audit was executed with all remaining magic
numbers extracted to named constants and capability env prefix strings
centralized.

## What Shipped (2 commits)

| Commit | Change |
|--------|--------|
| `e832b94` | BTSP `ClientHello` handshake, `BtspUnixAdapter` (NDJSON), fail-closed transport, docs sweep |
| `7e61455` | `SIGNING_PROVIDER_CACHE_TTL` + `HEALTH_STALE_MULTIPLIER` to constants, 14 `CapabilityEnv` prefix constants |

## BTSP Status: DONE

- Client-side `ClientHello` handshake implemented
- HMAC-SHA256 challenge-response matches bearDog expectations
- `AdapterFactory::from_transport()` auto-selects `BtspUnixAdapter` when strict mode detected
- `send_jsonrpc_request` performs fail-closed BTSP handshake on Unix streams
- Family seed resolution: `RHIZOCRYPT_FAMILY_SEED` → `FAMILY_SEED` → `BEARDOG_FAMILY_SEED`
- Strict mode detection: `BEARDOG_UDS_REQUIRE_BTSP=1` or `BTSP_STRICT_MODE=1`

## Deep Debt Audit Results

| Dimension | Status |
|-----------|--------|
| Files > 800L | CLEAN (max 752, test file; max production 624) |
| Unsafe code | CLEAN (`unsafe_code = "deny"`, zero blocks) |
| C FFI / bindgen | CLEAN (all deps pure Rust) |
| Production unwraps | CLEAN (zero in service binary) |
| TODO/FIXME/HACK | CLEAN (zero markers) |
| `#[deprecated]` | CLEAN (zero) |
| Hardcoded primal names | CLEAN (zero in executable code) |
| Production mocks | CLEAN (all cfg-gated) |
| Magic numbers | FIXED (cache TTL + staleness multiplier) |
| Env string literals | FIXED (14 capability env prefix constants) |
| Archive/debris | CLEAN (zero stale scripts or debris) |

## Metrics

| Metric | Value |
|--------|-------|
| Tests | 1,883 |
| Source files | 225 `.rs` |
| Lines | ~62,023 |
| Coverage | 93.83% |
| Clippy | 0 warnings |
| cargo deny | CLEAN |
| Max production file | 624 lines |

## Env Vars Added

| Variable | Purpose |
|----------|---------|
| `BEARDOG_UDS_REQUIRE_BTSP` | Activate client-side BTSP handshake (`1`) |
| `BTSP_STRICT_MODE` | Alias for above |
| `BEARDOG_FAMILY_SEED` | Fallback family seed for client handshake |

## Upstream Gaps (for primal teams)

None identified. rhizoCrypt is converged — zero debt, BTSP done, ready
for Nest Atomic Phase 2 wiring.
