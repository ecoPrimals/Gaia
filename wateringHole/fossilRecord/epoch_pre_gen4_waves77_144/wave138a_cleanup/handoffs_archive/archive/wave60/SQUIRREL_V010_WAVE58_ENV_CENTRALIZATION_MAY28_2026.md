# Squirrel v0.1.0 — Wave 58 Env Var Centralization

**Date:** May 28, 2026
**From:** Squirrel team
**To:** primalSpring, all downstream consumers
**Priority:** Tier 2 — pattern established, incremental migration ongoing

---

## What Was Done

Expanded `crates/universal-constants/src/env_vars.rs` from 20 constants to **316**,
covering every unique env var name in the Squirrel workspace. Constants are organized
into domain modules:

| Module | Constants | Coverage |
|--------|-----------|----------|
| `squirrel` | 37 | SQUIRREL_* vars |
| `ecosystem` | 18 | BIOMEOS_*, ECOSYSTEM_*, NEURAL_API_* |
| `ai` | 7 + 25 sub-mods | AI_*, OPENAI_*, ANTHROPIC_*, OLLAMA_*, GEMINI_*, HUGGINGFACE_*, LOCAL_AI_* |
| `mcp` | 18 + 8 sub-mods | MCP_*, CLI_MCP_* |
| `network` | 24 | NETWORK_*, SERVICE_*, PORT, BIND_* |
| `discovery` | 18 | DISCOVERY_*, SERVICE_MESH_*, CONSUL_* |
| `security` | 17 | SECURITY_*, JWT_*, TLS_*, CA_* |
| `primals` | 15 | BEARDOG_*, SONGBIRD_*, NESTGATE_*, TOADSTOOL_*, CRYPTO_* |
| `primal` | 12 | PRIMAL_* (generic) |
| `btsp` | 3 | BTSP_* |
| `compute` | 7 | COMPUTE_* |
| `storage` | 6 | STORAGE_* |
| `database` | 9 | DATABASE_*, DB_*, POSTGRES_* |
| `monitoring` | 10 | MONITORING_*, METRICS_*, HEALTH_* |
| `logging` | 6 | LOG_*, RUST_LOG |
| `performance` | 5 | PERF_* |
| `sandbox` | 6 | SANDBOX_* |
| `http` | 6 | HTTP_* |
| Others | ~20 | IPC_*, deploy, task, session, sys |

## Files Migrated

| File | Sites | Domains Used |
|------|-------|--------------|
| `crates/sdk/src/infrastructure/config.rs` | 29 | mcp, logging, network, http, performance |
| `crates/sdk/src/infrastructure/plugin_config.rs` | 6 | sandbox |
| `crates/main/src/rpc/unix_socket.rs` | 6 | squirrel, ecosystem, primal |
| `crates/main/src/capabilities/lifecycle.rs` | 5 | ecosystem, squirrel |

## Remaining Work (~400 sites)

Incremental — no deadline. Highest-value next targets:
- `crates/config/src/environment.rs` (60 sites)
- `crates/tools/ai-tools/src/config/defaults.rs` (31 sites)
- `crates/ecosystem-api/src/defaults.rs` (24 sites)
- `crates/tools/cli/src/mcp/config.rs` (17 sites)
- `crates/main/src/biomeos_integration/types.rs` (17 sites)

## Usage Pattern

```rust
use universal_constants::env_vars;

// Before:
let val = std::env::var("SQUIRREL_SOCKET").ok();

// After:
let val = std::env::var(env_vars::squirrel::SOCKET).ok();
```

Backward-compatible flat re-exports (`env_vars::BIND_ADDRESS` etc.) are preserved.

## Quality Gates

- `cargo clippy --workspace` — zero warnings
- `cargo test -p universal-constants --lib` — 117 pass (8 new env_vars tests)
- `cargo test -p squirrel --lib` — 2,244 pass
- `cargo test -p squirrel-sdk --lib` — 362 pass
- `cargo deny check` — clean
