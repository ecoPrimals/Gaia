# NestGate v0.5.0 — Session 77 / Wave 53 (Primal Mountain Teams)

**Date**: 2026-05-26
**Primal**: NestGate (storage)
**Version**: 0.5.0 (unified)

## Summary

Wave 53 audit requested version alignment and coverage push. Both addressed.

## Version Unification (CRITICAL — resolved)

NestGate had a three-way version mismatch:
- `4.7.0-dev` in all documentation (internal iteration counter)
- `0.1.0` in workspace `Cargo.toml`
- `2.1.0` in `nestgate-bin` (CLI binary)

**Fix**: Unified to **0.5.0** via `[workspace.package]` version inheritance.
All 21 workspace crates now inherit version. `nestgate --version` prints
`nestgate 0.5.0`. All `4.7.0-dev` references purged from active docs.
Historical CHANGELOG entries preserved.

**plasmidBin manifest** updated: `latest = "0.5.0"`.

## Coverage Push (83.02% → 83.24%)

35 new unit tests across 9 files targeting the highest-impact untested code:

| Crate | File | Tests | What |
|-------|------|-------|------|
| nestgate-security | auth_token_manager.rs | 6 | Token creation, validation, workspace secrets |
| nestgate-security | authentication/config.rs | 8 | Env priority chain (3-level fallback), serde roundtrip |
| nestgate-config | sovereignty_config.rs | 11 | API/WS/discovery endpoints, database URL, sovereignty validation |
| nestgate-discovery | capability_resolver/environment.rs | 8 | URL parsing (https/http/grpc/host:port), error paths |
| nestgate-rpc | semantic_router/capabilities.rs | 4 | Method list integrity, duplicates, domain prefixes |
| nestgate-rpc | semantic_router/crypto.rs | 2 | Delegation error contract (6 operations) |
| nestgate-rpc | semantic_router/health.rs | 1 | lifecycle.status pure JSON |
| nestgate-api | workspace_management/storage.rs | 4 | Workspace ID validation (edge cases) |
| nestgate-api | fail_safe/retry_executor.rs | 4 | Retry with backoff, max attempts, immediate success |

12,434 total tests, 0 failures. 90% target is multi-session — remaining gaps
are primarily in ZFS handler dispatch (needs mock ZFS), daemon lifecycle
(needs process-level testing), and UDS connection management.

## Open Items

- **Coverage 83.24% → 90%**: Multi-session target. Next focus areas:
  ZFS production handler mocking, UDS connection tests, config environment detection
- **VPS Nest expansion (Wave 54)**: eastGate atomic deployed, prepare for VPS
- **eastGate Nest deployed**: 13/13 primals, 19/19 sockets, plasmidBin 35/35

## Test Summary

```
12,434 total tests (lib + integration + doc)
8,966 lib-only tests
83.24% line coverage (83.49% region)
0 failures, 0 clippy warnings
```
