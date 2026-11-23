# biomeOS v3.87 — TMPDIR Regression + Orphan Cleanup (Wave 62)

**Date**: May 29, 2026
**From**: biomeOS team
**To**: primalSpring coordination
**Wave**: 62 (PostPrimordial → Glacial Shift)

---

## Summary

Fixed a DH-1 regression (TMPDIR fallback reintroduced in graph.execute),
hardened JWT secret resolution, surfaced silent capability registry failures,
centralized 7 more env var constants, deleted 1,090 lines of orphan code,
and removed 4 dead feature flags.

---

## Changes

### DH-1 regression fix
- `execute.rs:270-272,310-312`: Removed `TMPDIR` env var from socket
  resolution chain — was reintroducing `/tmp` dependency after DH-1 complete
- New chain: `SystemPaths` → `BIOMEOS_RUNTIME_DIR` → `BIOMEOS_SOCKET_DIR` → `DEFAULT_SOCKET_DIR`

### Security: JWT secret hardening
- `execute.rs:156-160`: Now checks `BIOMEOS_JWT_SECRET` before `JWT_SECRET`
- Warning message names the production env var to set

### Observability: capability registry
- `execute.rs:186-189`: Load failure logged at `warn!` instead of silent empty default

### Env var centralization (7 new constants)
- `RUNTIME_DIR`, `JWT_SECRET`, `DEPLOYMENT_MODE`, `NODE_FAMILY_ID`,
  `DISCOVERY_SOCKET`, `AI_PROVIDER`, `PORT` added to `env_config::vars`
- 6 raw string references replaced in `plasmodium/`, `model_cache/`, `atomic_discovery/`

### Dead code deletion
- `biomeos-graph/src/validator.rs` (255L) — referenced `petgraph` not in deps
- `biomeos-graph/src/templates.rs` (645L) — NestGate template storage, never wired
- `biomeos-graph/src/context.rs` (190L) — duplicated `executor/context.rs`

### Dead feature flags
- `biomeos-graph`: `async = []`
- `biomeos-boot`: `efi = []`, `bios = ["default"]`
- `biomeos-nucleus`: `test-utils = []`

---

## Verification

- 8,058 tests, 0 failures, 0 warnings
- `cargo check` clean

---

## Remaining biomeOS target

Cross-gate `graph.execute` Phase B (Wave 65) — the keystone for Plasmodium.
All other primal-level debt is resolved.
