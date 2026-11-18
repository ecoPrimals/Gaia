# NestGate Session 115: ErrorContextExt Trait — Jul 16, 2026

**Wave**: 144a
**Commit**: 5eee10c0
**Tests**: All passing (7 new ErrorContextExt tests)

## ErrorContextExt Trait (P0 map_err Evolution — Phase 1 COMPLETE)

New `ErrorContextExt` trait in `nestgate-types::error::enhanced_ergonomics`
provides domain-specific `Result` extension methods:

| Method | Error Variant | Sites Converted |
|--------|--------------|-----------------|
| `.io_ctx("ctx")` | `NestGateError::io_error` | 62 |
| `.net_ctx("ctx")` | `NestGateError::network_error` | 15 |
| `.internal_ctx("ctx")` | `NestGateError::internal` | 17 |
| `.api_ctx("ctx")` | `NestGateError::api_internal_error` | 27 |
| `.validation_ctx("ctx")` | `NestGateError::validation` | 12 |
| `.security_ctx("ctx")` | `NestGateError::security_error` | 1 |
| **Total** | | **152** |

42 remaining `map_err(format!())` sites use runtime-interpolated context
(e.g., `{family_id}`, `{hash}`) that legitimately need the full `format!` macro.

## Before / After

```rust
// Before (verbose, 87 io_error sites alone):
fs::read(path).map_err(|e| NestGateError::io_error(format!("read: {e}")))?;

// After (domain-preserving, ergonomic):
fs::read(path).io_ctx("read")?;
```

## Remaining Deep Debt Items

- **P0**: `map_err(format!())` — 42 remaining (runtime-interpolated, legitimate)
- **P1**: Typed JSON-RPC error enum (17 stringly-typed errors)
- **P2**: `pub` → `pub(crate)` visibility tightening (183 candidates)
- **P3**: Manual `impl Display` on label enums (17 strum::Display candidates)
