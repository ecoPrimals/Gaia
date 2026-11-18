# petalTongue Wave 76 — Consolidation: S3 Cutover Readiness

**Date**: June 3, 2026
**Version**: v1.6.8 consolidation
**Commit**: `6ef5042` (deep debt pass 3, supersedes `3807229`)
**Tests**: 6,217+ passed, 0 failed
**Clippy**: 0 warnings (first-party)

## Mission: Consolidation Pass

### S3 Content Cutover Readiness

Comprehensive audit of the content backend's mesh-aware 4-tier endpoint
resolution chain completed. Findings and fixes:

#### Fixed: FAMILY_ID Default Mismatch (HIGH)

| Component | Before | After |
|-----------|--------|-------|
| `content_backend.rs` Tier 3 | `"default"` | `"nat0"` |
| `announce_to_neural_api()` | `"default"` | `"nat0"` |
| `DiscoveryServiceClient::discover()` | `"nat0"` | `"nat0"` (unchanged) |
| `socket_path::get_family_id()` | `"nat0"` | `"nat0"` (unchanged) |

All components now use `"nat0"` as the ecosystem-standard fallback family.
Convention sockets match across tiers.

#### Fixed: Tier 4 DISCOVERY_SOCKET Support

`DiscoveryServiceClient::discover()` now honors `DISCOVERY_SOCKET` env var
as highest-priority override. This aligns with the NUCLEUS pattern where
compositions set `DISCOVERY_SOCKET` to the Songbird socket path. Previously,
Tier 4 auto-discovery couldn't find the discovery service in the same
deployment where `ipc.register` succeeded.

#### Verified: Tier 1–3 Correct and Production-Ready

| Tier | Resolution | Status |
|------|-----------|--------|
| 1 | `CONTENT_BACKEND_SOCKET` | Correct — explicit UDS override |
| 2 | `CONTENT_BACKEND_ENDPOINT` | Correct — TCP cross-gate mesh |
| 3 | Convention socket `{provider}-{family}.sock` | Correct (now with aligned family default) |
| 4 | `discovery.query("content")` | Improved (DISCOVERY_SOCKET wired) |

#### Remaining Gaps (Upstream / Future)

| Gap | Priority | Notes |
|-----|----------|-------|
| `parse_primal` drops `endpoints` struct | P3 | Songbird transport advertisements not parsed into `PrimalInfo.endpoints`; generic `endpoint` field used instead |
| No Tier 4 integration test | P3 | Tiers 1–3 all tested; Tier 4 requires mock discovery server |
| Readiness doesn't probe content backend | P3 | `/health/readiness` returns `ready: true` unconditionally |
| Endpoint frozen at startup | P3 | No re-resolution on connect failure; mesh failover needs restart |
| No connection pool/timeout on RPC | P3 | Single-shot connect per request |

**Recommended cutover pattern**: Explicit `CONTENT_BACKEND_ENDPOINT` (Tier 2)
for cross-gate, explicit `CONTENT_BACKEND_SOCKET` (Tier 1) for co-located.

### Typed Error Evolution

- **`AppError::TracingInit`**: New variant for tracing/logging init errors,
  eliminating 4 `AppError::Other(format!())` sites in `init_tracing()`.
- **Remaining `AppError::Other`**: 2 sites (docroot validation in `web_mode`).
  These are genuinely contextual validation messages — acceptable.

### Stale Ref Cleanup

- Removed stale `content.get` from module doc comment (only `content.resolve`
  is called)
- Fixed duplicate doc comment on `resolve()` method
- `NESTGATE_SOCKET` already `#[deprecated]` from prior pass

### Idiom Sweep

300+ `"literal".to_string()` → `.to_owned()` across 27 files:
- `scenarios/air_spring.rs` (50), `ground_spring.rs` (47)
- `biomeos_client.rs` (34), `awakening.rs` (23)
- `display_verification/verifier.rs` (20), `neural_graph_client.rs` (16)
- `neural_api_provider/provider.rs` (13), `capabilities.rs` (12)
- `system_monitor_integration/tool.rs` (12)
- Plus 18 more files (scene, IPC, graph, telemetry, config)

Fixed 13 Clippy `assigning_clones` warnings using `clone_into` pattern.

## Quality Gates

- `cargo fmt --check`: clean
- `cargo clippy --workspace --all-targets`: 0 warnings
- `cargo test --workspace`: all passing, 0 failures
- `unsafe_code = "forbid"` enforced

## Impulse Check

Active impulses (none petalTongue-specific):
- `wave76-parity-sprint-eastgate-tools.toml`
- `wave76-parity-sprint-provenance.toml`
- `wave76-parity-sprint-springs.toml`

## For primalSpring Audit

- **S3 cutover**: Explicit env var config is recommended path. Set
  `PETALTONGUE_WEB_BACKEND=content-provider` + `CONTENT_BACKEND_ENDPOINT`
  or `CONTENT_BACKEND_SOCKET`. All 4 tiers architecturally complete.
- **FAMILY_ID alignment**: Ecosystem `"nat0"` default now consistent across
  all resolution paths. Previous `"default"` could silently miss sockets.
- **DISCOVERY_SOCKET**: Now honored by both `RegistrationClient` and
  `DiscoveryServiceClient` — NUCLEUS compositions work end-to-end.
- **Error typing**: Only 2 `AppError::Other` remain (acceptable docroot
  validation). Zero `Result<_, String>` in production.

## Deep Debt Pass 3 (same session, commit `6ef5042`)

- **TRUE PRIMAL TLS**: `nucleus.rs` TLS handshake labels evolved from
  `Songbird`/`BearDog` to `TLS provider`/`X.509`/`X25519`/`HMAC verify`.
- **NESTGATE_SOCKET removed**: Deprecated constant fully deleted (zero refs).
- **Complete idiom sweep**: ALL remaining `"literal".to_string()` in production
  replaced with `.to_owned()` — 600+ replacements across 195 files. Zero
  instances remain in non-test code.
- **Codebase audit results** (all verified clean):
  - Zero files >800L in production (max 755L)
  - Zero unsafe code (workspace `forbid`)
  - Zero hardcoded primal names in production
  - All mocks properly feature/test-gated
  - Dependencies well-narrowed, no `full` features
  - Zero `Result<_, String>` in production
