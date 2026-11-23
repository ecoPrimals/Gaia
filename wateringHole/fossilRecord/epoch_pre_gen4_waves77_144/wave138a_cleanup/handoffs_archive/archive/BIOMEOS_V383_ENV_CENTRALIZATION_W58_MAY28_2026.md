# biomeOS v3.83 — Env Var Centralization (Wave 58)

**Date:** May 28, 2026
**From:** biomeOS team (southGate)
**To:** primalSpring coordination
**Version:** v3.82 → v3.83

---

## Summary

Aligned biomeOS with the Wave 57b env var centralization push that primalSpring
ran across 8 primals. biomeOS's `env_config::vars` module existed as the
canonical SSOT but had ~5% adoption. This wave wired ~90% of production
`env::var` call sites to constants.

---

## Changes

### 1. New Constants (15 added to `env_config::vars`)

| Constant | Env var |
|----------|---------|
| `BIND_ADDRESS` | `BIOMEOS_BIND_ADDRESS` |
| `MODE` | `BIOMEOS_MODE` |
| `AUTH_MODE` | `BIOMEOS_AUTH_MODE` |
| `NODE_ID` | `BIOMEOS_NODE_ID` |
| `NODE_ID_LEGACY` | `NODE_ID` |
| `DISCOVERY_PROVIDER` | `DISCOVERY_PROVIDER` |
| `REGISTRY_PROVIDER` | `BIOMEOS_REGISTRY_PROVIDER` |
| `STORAGE_PROVIDER` | `BIOMEOS_STORAGE_PROVIDER` |
| `ALLOW_LOOPBACK` | `BIOMEOS_ALLOW_LOOPBACK_DISCOVERY` |
| `SKIP_MDNS_PROBE` | `BIOMEOS_SKIP_MDNS_PROBE` |
| `INSECURE` | `BIOMEOS_INSECURE` |
| `BTSP_ENFORCE` | `BIOMEOS_BTSP_ENFORCE` |
| `MESH_PORT` | `SONGBIRD_MESH_PORT` |
| `HTTP_PORT` | `SONGBIRD_HTTP_PORT` |

### 2. Raw String → Constant Migration (~90 sites, 37 files)

Top variables centralized:

| Env var | Sites wired | Constant |
|---------|-------------|----------|
| `FAMILY_ID` | 25+ | `vars::FAMILY_ID_LEGACY` |
| `BIOMEOS_FAMILY_ID` | 20+ | `vars::FAMILY_ID` |
| `XDG_RUNTIME_DIR` | 18+ | `vars::XDG_RUNTIME_DIR` |
| `BIOMEOS_SOCKET_DIR` | 12+ | `vars::SOCKET_DIR` |
| `BIOMEOS_SECURITY_PROVIDER` | 7 | `vars::SECURITY_PROVIDER` |
| `NEURAL_API_SOCKET` | 7 | `vars::NEURAL_API_SOCKET` |
| `BIOMEOS_STRICT_DISCOVERY` | 6 | `vars::STRICT_DISCOVERY` |
| `BIOMEOS_PLASMID_BIN_DIR` | 5 | `vars::PLASMID_BIN_DIR` |

Crates touched: `biomeos-core`, `biomeos-api`, `biomeos-atomic-deploy`,
`biomeos-graph`, `biomeos-ui`, `biomeos-spore`, `biomeos-primal-sdk`,
`biomeos-federation`, `biomeos-cli`, `biomeos-nucleus`, `biomeos-types`,
`biomeos` (unibin), `neural-api-client-sync`, `tools`.

### 3. Clippy Migration (14 sovereign test files)

All `#![allow(clippy::unwrap_used, clippy::expect_used)]` → 
`#![expect(clippy::unwrap_used, clippy::expect_used, reason = "test assertions")]`

Files: `sovereign_pen_{tokens,payloads,headers_response,http_methods,
discovery,health_paths,access}.rs`, `sovereign_mesh_{phase1-6,crypto}.rs`

### 4. Unused Import Fix

`pub(crate) use nucleus_procs::discover_binaries_with` → gated behind
`#[cfg(test)]` since only test modules reference it.

---

## Verification

- `cargo check --workspace` — 0 warnings
- `cargo test --workspace` — 8,053 passed, 0 failed
- Zero `#[allow(clippy::` in production code
- Zero raw env var string literals for the top 8 most-duplicated variables

---

## Remaining Env Var Debt (lower priority)

~50 medium/low-frequency raw string sites remain in production for variables
like `JWT_SECRET`, `BIOMEOS_DEPLOYMENT_MODE`, `BIOMEOS_VERSION`,
`BIOMEOS_STUN_*`, `AI_DEFAULT_MODEL`, `GITHUB_TOKEN`, and OS vars
(`HOME`, `USER`, `UID`). These are one-off or domain-specific reads, not
duplicated, and can be migrated incrementally.

---

## NC-1 Status

**COMPLETE** (confirmed). No code changes to NC-1 in this wave. Deploy v3.83
(or v3.81+) to VPS to unblock spring emissions.

---

*Wave 58. Env var centralization aligned with ecosystem. Deploy the ecosystem.*
