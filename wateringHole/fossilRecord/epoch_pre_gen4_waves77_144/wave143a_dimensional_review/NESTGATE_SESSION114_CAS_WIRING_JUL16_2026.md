# NestGate Session 114: PROJECTS_PATH CAS Wiring + String::from R8 — Jul 16, 2026

**Wave**: 143b
**Commit**: e90806dc
**Tests**: All passing (12 footprint tests including 3 new PROJECTS_PATH)

## footPrint PROJECTS_PATH Wiring (Wave 143b P2 — COMPLETE)

`footprint_base_path()` in `nestgate-rpc` now checks `PROJECTS_PATH` env var
first, falling back to standard CAS layout `{storage_base}/datasets/{family}/_footprint`.

This enables footPrint composition wiring — external deployments (petalTongue,
sporePrint) can override the project storage root via environment variable.

- Capability registry updated with PROJECTS_PATH documentation
- Environment variables guide updated
- 3 new tests: override, empty-string fallback, unset fallback

## String::from → .into() Round 8

2,500+ conversions across 382 production files workspace-wide.

Files with ambiguous `impl Into<Cow<'static, str>>` targets were reverted to
preserve compilation. Those call sites need the P0 typed error helper
infrastructure in `nestgate-types` before they can be safely converted.

6 Cow-parameter call sites cleaned — bare `&str` literals passed directly
instead of `.into()` since `&str: Into<Cow<'static, str>>` trivially holds.

## Remaining Deep Debt Items

- **P0**: `map_err(format!())` (~264 sites) — needs error helper infrastructure
- **P1**: Typed JSON-RPC error enum (17 stringly-typed errors)
- **P2**: `pub` → `pub(crate)` visibility tightening (183 candidates)
- **P3**: Manual `impl Display` on label enums (17 strum::Display candidates)
