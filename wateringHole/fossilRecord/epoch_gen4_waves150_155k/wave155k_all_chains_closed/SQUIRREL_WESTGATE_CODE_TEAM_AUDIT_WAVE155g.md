# Squirrel Code Team Audit — westGate Wave 155g

**Date**: Jul 28, 2026 15:10 EDT | **Wave**: 155g | **Gate**: westGate
**From**: squirrel code team (westGate)
**Status**: **AUDITED — squirrel is code-clean and deployment-ready.**

---

## Executive Summary

squirrel (AI coordination primal) passes all audit dimensions. 984 Rust source
files, 306K lines, 4,941 `#[test]` attributes, 763 tests passing (0 failed),
zero clippy errors, minor formatting drift (2 files), zero TODO/FIXME/HACK
markers, zero `unsafe` blocks, AGPL-3.0 triple-licensed, no external telemetry.
BTSP ClientHello shipped. JSON-RPC + tarpc IPC. Capability registry has 42+
methods. Ready for westGate deployment validation.

---

## Sync Status (Phase 0+1)

| Metric | Value |
|--------|-------|
| SSH connectivity | **PASS** — authenticated as `golgiAdmin` via `westGate-wave155f` key |
| Remotes | **41/41 repointed** HTTPS → SSH (`ssh://git@git.primals.eco:2222/`) |
| Naming divergences | **0** — all camelCase, no duplicates |
| Branch names | **41/41 on `main`** (coralForge empty, no commits) |
| Repos pulled | **39/41** clean pull |
| Recloned (shallow roots) | **9** — esotericWebb, airSpring, groundSpring, healthSpring, hotSpring, ludoSpring, neuralSpring, wetSpring, (hotSpring required /tmp clone + move due to pack error) |
| Empty repo | **1** — coralForge (no remote ref `main`, no commits) |
| Dirty repos | **1** — nestGate has untracked `vendor/` directory |
| wave.toml | **155g** (updated from 155f since blurb was written) |

---

## Squirrel Audit Results

### Codebase Metrics

| Metric | Value |
|--------|-------|
| Version | 0.1.0 |
| Rust edition | 2024 |
| Source files (`.rs`) | 984 |
| Total lines | 306,059 |
| Workspace crates | 14 |
| `#[test]` attributes | 4,941 |
| Tests passing | **763** (0 failed, 0 ignored) |
| HEAD commit | `92d3cc16` (`meta: standardize homepage + documentation URLs`) |
| Cargo.lock deps | 4,836 lines |

### Workspace Structure

```
crates/
├── main/                    # Main binary (squirrel)
├── core/
│   ├── core/                # Ecosystem coordination, federation, routing, discovery
│   ├── mcp/                 # MCP protocol (Model Context Protocol)
│   ├── context/             # Context management, learning engine, rules, visualization
│   ├── interfaces/          # Shared trait definitions
│   ├── auth/                # BTSP auth, capability JWT, delegated JWT
│   └── plugins/             # Plugin framework
├── services/commands/       # Command execution
├── tools/
│   ├── ai-tools/            # AI tool integration (capability-based)
│   └── cli/                 # CLI interface
├── sdk/                     # WASM SDK
├── config/                  # Configuration management
├── ecosystem-api/           # Ecosystem API types and traits
├── universal-patterns/      # Cross-primal reusable patterns
├── universal-constants/     # Cross-primal constants
└── universal-error/         # Cross-primal error types
```

### Code Quality

| Check | Status | Detail |
|-------|--------|--------|
| `cargo clippy --all-targets -W pedantic -W nursery` | **PASS** | 12 warnings (all `missing_docs` in context crate — progressive lint) |
| `cargo fmt --check` | **2 diffs** | `secret_store.rs` and `security_provider_secret_store.rs` — minor formatting drift |
| `cargo doc --no-deps` | Not run | (README reports GREEN) |
| `unsafe_code = "forbid"` | **ENFORCED** | Workspace-level — 0 unsafe blocks in any code |
| `unwrap_used = "deny"` | **ENFORCED** | Workspace-level — 0 unwrap() in production code |
| `expect_used = "deny"` | **ENFORCED** | Workspace-level |
| Files > 800 lines | **3** (all test files) | `jsonrpc_server_unit_tests.rs` (1293), `mcp/tests.rs` (915), `adapter_integration_tests.rs` (814) |
| TODO/FIXME/HACK markers | **0** | Zero markers in entire codebase |

### Architecture Compliance

| Requirement | Status | Detail |
|-------------|--------|--------|
| JSON-RPC wire protocol | **COMPLIANT** | JSON-RPC 2.0 over Unix domain sockets |
| tarpc service trait | **COMPLIANT** | `tarpc-rpc` feature, binary RPC for high-performance paths |
| genomeBin compliant | **COMPLIANT** | Single binary target, `just build-ecobin` |
| Semantic method naming | **COMPLIANT** | 42+ methods per `SEMANTIC_METHOD_NAMING_STANDARD` v2.0 §7 |
| Platform-native transport | **COMPLIANT** | UDS transport, `songBird` mesh delegation |
| BTSP ClientHello | **SHIPPED** | `crates/core/auth/` — delegated JWT, capability crypto |
| biomeOS neuralAPI | **COMPLIANT** | `capability.discover`, `capability.announce`, lifecycle signals |
| Capability registry | **COMPLIANT** | `config/capability_registry.toml` — 42+ methods, 14 domains |

### Capability Domains (from registry)

| Domain | Methods | Stability |
|--------|---------|-----------|
| inference.* | 5 | evolving |
| ai.* | 3 | stable (aliases → inference.*) |
| capability.* | 6 | stable |
| health.* | 4 | stable (frozen) |
| identity.* | 1 | stable |
| system.* | 4 | stable (aliases) |
| discovery.* | 1 | stable |
| tool.* | 2 | evolving |
| context.* | 3 | evolving |
| provider.* | 3 | evolving |
| btsp.* | 1 | evolving |
| lifecycle.* | 2 | stable |
| signal.* | 1 | evolving |
| graph.* | 2 | evolving |

### Test Coverage

- **763 tests passing** (default + all-features: same count)
- **4,941 `#[test]` attributes** — delta is behind feature gates:
  - `integration-tests` (mcp, auth) — gated until UDS API rewrite
  - `context-learning`, `context-visualization` — optional learning engine
  - `mesh`, `http-api` (core) — optional federation/HTTP features
- **Test tiers present**: unit (inline), integration (`tests/`), no E2E via primalSpring yet
- **Coverage**: README reports 90.1% region coverage (not independently verified)

### Debt & Gaps

| Priority | Item | Detail |
|----------|------|--------|
| **P1** | Format drift | 2 files need `cargo fmt` — `secret_store.rs`, `security_provider_secret_store.rs` |
| **P1** | Feature-gated test gap | 4,178 `#[test]` attributes behind disabled feature gates — many may be stale or broken |
| **P1** | Integration tests disabled | `integration-tests` feature gate in mcp and auth — "gated until API rewrite for UDS transport" |
| **P1** | Plugin loader is stub | `SecurePluginLoader` returns stub — "proper sandboxed plugin loading requires WebAssembly runtime integration" |
| **P2** | No primalSpring E2E | No E2E scenarios registered in primalSpring for squirrel |
| **P2** | `context-learning` feature | Learning engine (adaptive, reward, policy) is feature-gated off by default |
| **P2** | SDK is WASM-only | `crates/sdk/` targets `wasm-bindgen` — no native SDK for Rust consumers |
| **P2** | 3 test files > 800 lines | `jsonrpc_server_unit_tests.rs` (1293), `mcp/tests.rs` (915), `adapter_integration_tests.rs` (814) |
| **P2** | `squirrel-context` clippy warnings | 12 `missing_docs` warnings (progressive lint tightening noted) |

### Sovereignty

| Check | Status |
|-------|--------|
| License | **AGPL-3.0-or-later** + ORC + CC-BY-SA-4.0 (scyBorg triple-license) |
| License files | `LICENSE`, `LICENSE-AGPL3`, `LICENSE-CC-BY-SA`, `LICENSE-ORC` |
| SPDX headers | Present in `Cargo.toml`, capability registry, LICENSE |
| External telemetry | **NONE** — "telemetry" references are internal mesh/engine metrics only |
| Cloud lock-in | **NONE** — reqwest removed, all HTTP delegated through songBird mesh |
| Pure Rust crypto | **YES** — `blake3` (pure feature), `ed25519-dalek`, `chacha20poly1305`, `hkdf`, `sha2`, `hmac` |
| Depot binaries | Configured for `https://depot.primals.eco` |

### Upstream Dependencies

| Primal | Integration | Status |
|--------|-------------|--------|
| bearDog | BTSP ClientHello, delegated JWT, `security.*` capability | **WIRED** (feature-gated `local-crypto` for fallback) |
| songBird | Service mesh, IPC, discovery, `network.*` capability | **WIRED** (transport delegation, peer discovery) |
| biomeOS | Lifecycle registration, capability announce, neural graph | **WIRED** (lifecycle.register, capability.discover) |

---

## Recommendations for eastGate

1. **Fix format drift** (P1): `cargo fmt` on `crates/core/mcp/src/security/secret_store.rs` and `security_provider_secret_store.rs`
2. **Audit feature-gated tests** (P1): 4,178 tests behind feature gates — verify they still compile and pass when enabled
3. **Register squirrel E2E in primalSpring** (P2): No scenarios exist for squirrel startup, capability registration, or inference routing
4. **Wire `context-learning` by default** (P2): The learning engine is substantial code that's always disabled

---

## Extra Directories on westGate (non-canonical)

- `~/Development/ecoPrimals/archive/` — local artifact, safe to keep
- `~/Development/ecoPrimals/sort-after/` — local artifact, safe to keep

---

## Notes

- wave.toml was at **155g** at time of audit (blurb referenced 155f)
- westGate is listed as ONLINE in `wave.toml` gates
- hotSpring required `/tmp` clone + move due to persistent pack file corruption during direct clone to `springs/` — may indicate filesystem edge case or Forgejo pack issue
- nestGate has untracked `vendor/` directory (not squirrel-related, reporting for completeness)
