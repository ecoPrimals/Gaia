<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# Squirrel v0.1.0 — Deep Debt: Hardcoding Elimination & Env Centralization

**Date**: May 28, 2026
**From**: squirrel team (Cursor agent)
**To**: primalSpring coordination
**Commits**: `57c0ec5a`..`71f4b950` (5 commits)
**Tests**: 7,095 passing (lib + integration) | 0 clippy warnings | cargo deny clean

---

## What Changed

### 1. Cross-Primal Hardcoding Eliminated

Squirrel no longer contains hardcoded references to other primals' names
in production routing logic:

- **`"toadstool"` removed** from `provider_trait.rs` match arm and
  `TOADSTOOL_ENDPOINT` env var fallback. Compute primal is now discovered
  via generic `COMPUTE_ENDPOINT` / `COMPUTE_SERVICE_ENDPOINT`.
- **`"biomeos"` string** replaced with `primal_names::BIOMEOS_SOCKET_DIR`
  constant in socket registry and IPC discovery.
- **Serde aliases retained** (`#[serde(alias = "beardog")]` etc.) — these
  are backward-compat for deserializing existing config files, not runtime
  routing. Field names are already capability-based (`security_provider`,
  `content_storage`, `compute_provider`).

### 2. Self-Identity Constants (25+ sites across 17 files)

All production `"squirrel"` string literals replaced with
`niche::PRIMAL_ID` or `universal_constants::identity::PRIMAL_ID`:

- `compute_client/client.rs`, `storage_client/client.rs`, `security_client/client.rs`
- `rpc/tarpc_dispatch.rs`, `capabilities/registry.rs`
- `universal_adapters/` (compute, storage, orchestration)
- `biomeos_integration/optimized_implementations.rs`
- `config.rs`, `doctor.rs`, `ecosystem/registry/config.rs`
- `universal_primal_ecosystem/mod.rs`
- `transport/client.rs`, `transport/listener.rs`
- `config/builder_presets.rs`, `ecosystem-api/config/defaults.rs`
- `config/unified/loader.rs`, `core/ecosystem_service.rs`
- `ecosystem/registry/types/interning.rs`

### 3. PrimalType Capability Fix

`PrimalType::Squirrel::capability()` now returns `"inference"` (the
capability domain) instead of `"squirrel"` (the primal name). This aligns
with the capability-based discovery standard — routing by capability, not
by name.

### 4. Environment Variable Centralization (89 additional sites)

| File | Sites Migrated | Constants Used |
|------|:--------------:|----------------|
| `config/environment.rs` | 60 | `env_vars::mcp::*`, `env_vars::database::*`, `env_vars::ai::*`, `env_vars::network::*`, `env_vars::compute::*`, `env_vars::ecosystem::*` |
| `ecosystem-api/defaults.rs` | 24 | `env_vars::discovery::*`, `env_vars::compute::*`, `env_vars::network::*`, `env_vars::primals::*`, `env_vars::security::*` |
| `api/ai/router.rs` | 5 | `env_vars::ai::INFERENCE_ENDPOINT`, `env_vars::ai::PROVIDER_SOCKETS`, `env_vars::ai::local::ENDPOINT`, `env_vars::ai::ollama::*` |

**14 new constants added** to `env_vars.rs`:
- `network::STORAGE_ENDPOINT`, `STORAGE_PORT`, `STORAGE_SERVICE_PORT`
- `network::SECURITY_ENDPOINT`, `SECURITY_PORT`, `SECURITY_SERVICE_PORT`
- `network::SERVICE_MESH_ENDPOINT`, `SERVICE_MESH_PORT`
- `http::WEB_UI_URL`, `WEB_UI_PORT`
- `ai::INFERENCE_ENDPOINT`, `AI_INFERENCE_ENDPOINT`
- `discovery::REGISTRATION_ENDPOINT`

### 5. SecurePluginStub Documented

Clarified that `SecurePluginStub` is an intentional security boundary
(deny native `.so` execution), not a mock or incomplete implementation.
All plugin capability flows through the CLI command registry.

---

## Remaining Work

~350 raw `env::var("...")` sites across ~65 files remain for incremental
migration. Highest-value next targets:
- `tools/ai-tools/src/config/defaults.rs` (31 sites)
- `tools/ai-tools/src/config/core.rs` (23 sites)
- `tools/cli/src/mcp/config.rs` (17 sites)
- `biomeos_integration/types.rs` (17 sites)

5 pre-existing doctest failures (doc examples drifted from API —
`arc_str`, `string_utils`, `protocol`, `session`) — not regression.

---

## Ecosystem Impact

- **primalSpring**: Squirrel no longer routes to `"toadstool"` by name.
  Any compute primal advertising `compute.*` capabilities and setting
  `COMPUTE_ENDPOINT` will be used.
- **biomeOS**: Socket discovery continues to use standard
  `$XDG_RUNTIME_DIR/biomeos/` path via constant, not hardcoded string.
- **downstream consumers**: No API changes. JSON-RPC surface unchanged.
  Config files with legacy primal-name keys (`beardog`, `nestgate`,
  `toadstool`) still deserialize correctly via serde aliases.

---

## Validation

```bash
cargo fmt --all -- --check       # PASS
cargo clippy --workspace         # 0 warnings
cargo test --workspace --lib --tests  # 7,095 pass / 0 fail
cargo deny check                 # advisories ok, bans ok, licenses ok, sources ok
```
