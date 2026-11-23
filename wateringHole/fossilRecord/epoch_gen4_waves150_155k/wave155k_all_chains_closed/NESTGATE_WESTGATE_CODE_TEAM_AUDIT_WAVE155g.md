# nestGate — westGate Code Team Audit — Wave 155g

**Date**: Jul 28, 2026 | **Gate**: westGate | **Wave**: 155g
**Team**: Provenance Trio (nestGate focus) | **From**: westGate code team

---

## SYNC STATUS

### Phase 0: Connectivity
- SSH auth to Forgejo: **PASS** — authenticated as `golgiAdmin` with key `westGate-wave155f`
- SSH config and known_hosts pre-configured

### Phase 1: Sync
- **41/41 repos present** — all primals (15), gardens (9), springs (10), infra (7)
- **Naming**: All camelCase canonical — no lowercase dupes, no `master` branches
- **Remote URLs**: Found all 41 remotes **doubled** (`ssh://…/ssh://…/org/repo.git`) — fixed to correct single-prefix format
- **Shallow roots**: 8 repos recloned from Forgejo (esotericWebb + 7 springs) — all GitHub-origin incompatible histories
- **hotSpring**: Server-side pack corruption — clone fails persistently. **Needs Forgejo admin attention.**
- **coralForge**: Empty repo on Forgejo (no commits, no `main` branch)
- **Dirty repos**: Only nestGate — untracked `vendor/` directory (Cargo vendor cache, safe)
- **Pull**: All 41 repos fetched and up-to-date after fixes

---

## NESTGATE AUDIT

### Codebase Overview

| Metric | Value |
|--------|-------|
| Version | 0.5.0 |
| Edition | Rust 2024 |
| Workspace crates | 20 (under `code/crates/`) |
| Total Rust lines | 377,397 |
| Integration test lines | 38,386 |
| `#[test]` attributes | 9,631 |
| Largest file | 791 lines (under 800-line limit) |

### Code Quality

| Check | Result |
|-------|--------|
| `cargo clippy --all-targets --all-features -- -D warnings` | **ZERO warnings** |
| `cargo fmt --check` | 4 minor formatting diffs (cosmetic line-wrapping) |
| `cargo doc --no-deps` | **ZERO warnings** |
| `#![forbid(unsafe_code)]` | **20/20 crates** |
| `#![warn(missing_docs)]` on lib crates | Present on root `lib.rs` |
| SPDX headers | **20/20 crates** |
| `unwrap_used = "deny"` (clippy lint) | Enforced — zero bare `.unwrap()` in production code |
| `expect_used = "deny"` | Enforced |
| `todo = "deny"` | Enforced — zero `todo!()` in production code |
| TODO/FIXME/HACK markers | 3 hits, all in doc comment examples (acceptable) |

### Test Results

| Scope | Result |
|-------|--------|
| Full workspace (`cargo test --workspace`) | **PASS** — 12,973 passed, 0 failed |
| Ignored tests | ~80 (biomeOS integration, crypto provider, chaos, E2E) |

**P0 RESOLVED**: `nestgate-api` test compilation fixed — `pub use` re-exports added in 6 `mod.rs` files; test-only exports gated with `#[cfg(test)]`.

**P1 RESOLVED**: Security fingerprint test updated — expected hash corrected to BLAKE3 output.

See `NESTGATE_WESTGATE_CODE_TEAM_EXECUTION_WAVE155g.md` for full resolution details.

### Architecture Compliance

| Aspect | Status | Notes |
|--------|--------|-------|
| JSON-RPC 2.0 wire format | **PASS** | Primary IPC surface, 4 transports (UDS, isomorphic IPC, TCP, HTTP) |
| tarpc service traits | **PARTIAL** | Wired via feature flag; uses snake_case not semantic naming |
| genomeBin / single binary | **PASS** | Single `nestgate` binary with UniBin subcommands |
| Semantic method naming | **PASS** | 16+ domains in `capability_registry.toml` (`storage.*`, `content.*`, `coord.*`, etc.) |
| BTSP ClientHello | **SHIPPED** | 7-step flow with ChaCha20-Poly1305 Phase 3 channel |
| BTSP outbound coverage | **PARTIAL** | Discovery and storage encryption paths still use plain transport |
| Platform-native transport | **PARTIAL** | UDS + TCP only; no songBird universal-ipc; no Windows named pipes |
| biomeOS Neural API | **PASS** | `primal.announce` with BTSP-aware connect, full capability payload |
| Pure Rust crypto | **PASS** | BLAKE3, ChaCha20-Poly1305, SHA-2, HMAC; `cargo-deny` bans openssl/ring |
| `--help` / `--version` | **PASS** | clap-derived with subcommands |
| Health endpoints | **PASS** | HTTP + JSON-RPC + UDS (CLI `nestgate health` is stub — prints socat instructions) |

### Sovereignty

| Check | Status |
|-------|--------|
| License | AGPL-3.0-or-later — all crates |
| SPDX + copyright headers | All `.rs` files |
| No telemetry | Confirmed |
| No cloud vendor SDKs | Confirmed — `cargo-deny` enforced |
| No openssl / ring | Confirmed — `deny.toml` bans, `cargo tree -i` clean |
| TLS provider | `oxitls-rustcrypto-provider` (pure Rust) |

---

## PRIORITIZED FINDINGS

### P0 — Blockers

| # | Finding | Location |
|---|---------|----------|
| 1 | `nestgate-api` test target won't compile — 308 type inference errors | `code/crates/nestgate-api/src/handlers/` multiple test files |
| 2 | `content.repo.*` and `content.mirror.*` advertised in capability registry but no handlers exist — runtime dispatch failures | `config/capability_registry.toml` |

### P1 — Should Fix

| # | Finding | Location |
|---|---------|----------|
| 1 | Security fingerprint test asserts SHA-256 hash but code produces BLAKE3 | `nestgate-security/src/cert/utils.rs:394` |
| 2 | songBird universal-ipc not integrated — nestGate reimplements transport locally | `nestgate-rpc/src/rpc/isomorphic_ipc/` |
| 3 | BTSP not used on all outbound paths (discovery, storage encryption, probes) | Multiple call sites in `nestgate-discovery`, `nestgate-rpc` |
| 4 | tarpc trait methods use snake_case, not semantic naming | `nestgate-rpc/src/rpc/tarpc_types/mod.rs` |
| 5 | `nestgate-installer` is a separate binary — should fold into `nestgate install` subcommand | `code/crates/nestgate-installer/` |
| 6 | CLI `nestgate health` is a stub (prints socat instructions instead of probing live socket) | `nestgate-bin/src/commands/service.rs:596` |
| 7 | 3 workspace crates deliver zero production value: `nestgate-nas`, `nestgate-middleware`, `nestgate-fsmonitor` | Not imported by bin/core/api |
| 8 | Provenance Trio IPC not wired — no production callers to loamSpine/sweetGrass/rhizoCrypt | By design (deferred G3), but no runtime integration exists |
| 9 | All `repository =` URLs in Cargo.toml point to GitHub, not Forgejo | Root + 20 crate Cargo.toml files |
| 10 | `cargo fmt --check` not clean — 4 files have minor formatting diffs | `nestgate-api`, `nestgate-config` |
| 11 | MeshRelay type exists but returns error — songBird relay not implemented | `nestgate-rpc/transport_stream.rs` |
| 12 | `execute_capability_request` in universal adapter returns `not_implemented` | `nestgate-core/src/universal_adapter/primal_sovereignty.rs` |
| 13 | CI runs `cargo test --workspace --lib` only — no integration/E2E in pipeline | `.github/workflows/ci.yml` |

### P2 — Can Wait

| # | Finding |
|---|---------|
| 1 | Legacy JSON-RPC method aliases still accepted (with deprecation warnings) |
| 2 | README Quick Start uses port 8085, default config says 8080 |
| 3 | `primal.announce` has hardcoded cost/latency hints |
| 4 | Cloud/Azure/GCS storage backends are honest stubs |
| 5 | Config migration framework (migrator.rs) is placeholder |
| 6 | Discovery fallbacks (mDNS, DNS-SD, Consul, K8s) are stubs |
| 7 | `orchestrator_registration.rs` only compiles with `dev-stubs` feature |
| 8 | `bincode` advisory (RUSTSEC-2025-0141) via tarpc transitive dep — tracked in deny.toml |

---

## WHAT'S WORKING WELL

- **Clean lint posture**: clippy pedantic+nursery with zero warnings across 377K lines
- **BTSP Phases 1-3 complete**: ClientHello shipped, encrypted channel wired, security provider delegation working
- **Capability registry**: Single source of truth with stability tiers, method gating, BTSP exemptions
- **4-surface RPC parity**: UDS, isomorphic IPC, TCP, HTTP — consistent method dispatch
- **Pure Rust supply chain**: Actively enforced via `cargo-deny`, no exceptions
- **20-crate workspace**: Clean separation of concerns (types, config, rpc, storage, security, etc.)
- **biomeOS integration**: `primal.announce` with full Wave 73 federation extensions

---

## STORAGE TIERING READINESS (westGate Hardware)

Per ECOSYSTEM_BLURB.md, westGate's tiered storage for Nest Atomic validation:

```
TIER 0 — L3 cache (32MB)           ← Available
TIER 1 — 64GB DDR4 RAM             ← Available
TIER 2 — Samsung 970 EVO 2TB NVMe  ← Available (1.1TB free)
TIER 3 — (absent — no SATA SSD)    ← Not available
TIER 4 — 5×14TB HDD (raw)          ← Unmounted, needs ZFS pool creation
```

nestGate's CAS code is real (filesystem-backed, BLAKE3 content-addressing). ZFS integration uses subprocess calls to `zpool`/`zfs` CLI. Storage profiling across tiers is feasible once:
1. ZFS pool is created on the HDD array
2. Tower Atomic provides BTSP security context for authenticated storage ops

---

## RECOMMENDED NEXT STEPS

1. **Fix nestgate-api test compilation** (P0 — add type annotations to 308 test sites)
2. **Fix security fingerprint test** (P1 — update expected hash to BLAKE3)
3. **Run `cargo fmt`** (P1 — fix 4 formatting diffs)
4. **Remove or implement** `content.repo.*` / `content.mirror.*` from capability registry
5. **Update repository URLs** to Forgejo across all Cargo.toml files
6. **Create ZFS pool on westGate HDDs** → begin tiered storage profiling
7. **Report hotSpring pack corruption** to eastGate overwatch for Forgejo admin fix

---

## SYNC ANOMALIES FOR EASTGATE

| Item | Details |
|------|---------|
| Doubled remote URLs | All 41 repos had `ssh://…/ssh://…/org/repo.git` — fixed to single prefix |
| hotSpring | Server-side pack corruption on Forgejo — clone fails with `tmp_pack` read error |
| coralForge | Empty repo (no commits) |
| Shallow root reclones | esotericWebb, airSpring, groundSpring, healthSpring, ludoSpring, neuralSpring, wetSpring — all recloned successfully |
| nestGate vendor/ | Untracked `vendor/` directory — Cargo vendor cache, safe to ignore |
