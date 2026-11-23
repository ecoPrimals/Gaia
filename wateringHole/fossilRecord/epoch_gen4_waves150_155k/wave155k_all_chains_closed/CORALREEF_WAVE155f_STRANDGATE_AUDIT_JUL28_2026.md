<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# coralReef — strandGate Code Team Audit (Wave 155f)

**Gate**: strandGate  
**Primal**: coralReef v0.2.0  
**Date**: 2026-07-28  
**Wave**: 155f  
**Hardware**: Dual EPYC 7452 (64 cores) + RTX 3090 (24GB VRAM)

---

## Sync State

| Check | Result |
|-------|--------|
| Origin remote | `ssh://git@git.primals.eco:2222/ecoPrimals/coralReef.git` ✅ |
| Branch | `main` ✅ |
| Divergence from origin | Zero (exactly at `origin/main`) ✅ |
| Working tree | Clean ✅ |
| Tracking branch | Fixed: was `github/main`, repointed to `origin/main` |
| GitHub remote | `github` remote still present (legacy mirror, read-only) |

---

## Build Status

| Check | Result | Details |
|-------|--------|---------|
| `cargo test --all-features` | **FAIL** | 10 compile errors in `coralreef-core` |
| `cargo clippy --all-features -- -D warnings` | **FAIL** | `assertions_on_constants` in `coral-reef-isa` |
| `cargo fmt --check` | **FAIL** | Formatting drift in `btsp.rs`, `newline_jsonrpc.rs` |
| `cargo doc --all-features --no-deps` | **FAIL** | Same compile errors as tests |
| `cargo test -p coral-reef` | **PASS** | 2183 tests (2181 pass, 2 ignored) |
| `cargo test` (supporting crates) | **PASS** | 269 tests (all pass) |

**Passing tests (non-core crates)**: 2452 / 2454 total (2 `#[ignore]`).  
**coralreef-core**: Does not compile — estimated ~1200 tests blocked.

---

## P0 — Build-Breaking Compile Errors (10 errors in `coralreef-core`)

All errors are in `coralreef-core` and appear to result from an incomplete IPC
merge resolution (commit `8ebd97d9`). The coral-reef compiler crate and all
other crates compile and test cleanly.

### 1. Missing `config::beardog_socket()` (btsp.rs:450)

`ipc/btsp.rs` calls `config::beardog_socket()` but this function does not exist
in `config.rs`. Only `config::btsp_provider_socket()` exists.

**File**: `crates/coralreef-core/src/ipc/btsp.rs:450`  
**Fix**: Either add `beardog_socket()` to `config.rs` (reading `$BEARDOG_SOCKET`
env var), or replace with `btsp_provider_socket()` if semantically equivalent.

### 2. Missing `newline_jsonrpc::compile_timeout()` (tarpc_transport.rs)

`ipc/tarpc_transport.rs` references `super::newline_jsonrpc::compile_timeout()`
in 5 locations (lines 88, 114, 142, 183, 203). This function does not exist in
`newline_jsonrpc.rs`.

**Fix**: Add a `compile_timeout()` function to `newline_jsonrpc.rs` that returns
a `Duration` (likely env-configurable via `$CORALREEF_COMPILE_TIMEOUT_SECS`),
or define it in `config.rs` and re-export.

### 3. Private visibility: `btsp::discover_by_capability` (provenance.rs:46)

`service/provenance.rs` calls `btsp::discover_by_capability()` and
`btsp::discover_security_socket()`, but both are private (`fn`, not `pub fn`).

**File**: `crates/coralreef-core/src/ipc/btsp.rs:471` and `:444`  
**Fix**: Change to `pub(crate) fn` for both functions.

### 4. Missing `unix_jsonrpc::handle_connection` (tests_unix_edge.rs:557)

Test file references `unix_jsonrpc::handle_connection()` which doesn't exist.
The function was likely renamed or restructured during the IPC merge.

**File**: `crates/coralreef-core/src/ipc/tests_unix_edge.rs:557`

### 5. Type inference cascade (btsp.rs:450–451)

The `config::beardog_socket()` error cascades into type inference failures in
the `.filter(|p| p.exists())` closure and `tracing::debug!` macro on lines
450–451.

### 6. Unused import (unix_jsonrpc.rs:206)

```rust
pub use super::newline_jsonrpc::make_response;
```

Gated under `#[cfg(all(unix, test))]` but `make_response` is not used by any
test module importing from `unix_jsonrpc`.

---

## P0 — Clippy Error

### 7. `assertions_on_constants` (coral-reef-isa/src/latency.rs:75)

```rust
assert!(InstrLatency::IALU.throughput > InstrLatency::DEFAULT.throughput);
```

Clippy requires constant assertions to use `const { assert!(..) }` blocks.

**Fix**: Wrap in `const { assert!(...) }` or move to a `const` block.

---

## P0 — Formatting Drift

### 8. `cargo fmt` differences in `btsp.rs` and `newline_jsonrpc.rs`

Multiple formatting divergences in `crates/coralreef-core/src/ipc/btsp.rs`
(missing semicolons, line wrapping, closure formatting) and one in
`newline_jsonrpc.rs:268`. These appear to be pre-existing from the IPC merge.

**Fix**: `cargo fmt` (will auto-fix all).

---

## P1 — Functional Gaps

### 9. JSON-RPC dispatch gap: 7 of 18 methods not wired

`config::SERVED_METHODS` advertises 18 methods, but `dispatch_jsonrpc` in
`newline_jsonrpc.rs` only routes 11. Missing from JSON-RPC dispatch:

| Method | Handler exists | Available via |
|--------|---------------|---------------|
| `shader.compile.multi` | ✅ `handle_compile_multi` | tarpc only |
| `shader.compile.gemm` | ✅ `handle_compile_gemm` | tarpc only |
| `health.version` | ✅ `handle_health_version` | tarpc only |
| `capabilities.list` | ✅ (alias of `capability.list`) | Not routed |
| `btsp.negotiate` | ✅ `handle_negotiate` | Not in dispatch |
| `auth.check` | ✅ method-gate introspection | Not in dispatch |
| `auth.mode` | ✅ method-gate introspection | Not in dispatch |
| `auth.peer_info` | ✅ method-gate introspection | Not in dispatch |

Tests in `tests_unix_dispatch.rs` and `tests_newline_jsonrpc.rs` expect these
methods to be callable. Likely contributes to test failures once compile errors
are fixed.

### 10. Repository URL still points at GitHub

`Cargo.toml` workspace `[workspace.package].repository` is set to
`https://github.com/ecoPrimals/coralReef` — should be updated to Forgejo
canonical URL.

### 11. README test count stale

README claims "3669 tests" but the workspace can only run ~2452 due to
`coralreef-core` compile failures. Actual count will differ once build is fixed.

---

## P2 — Minor / Cosmetic

### 12. Unused constant in test binary

`crates/coral-reef/tests/compiler_integration/main.rs:32` defines
`SPH_HEADER_BYTES` but never uses it. Produces a `dead_code` warning.

### 13. Generated ISA files approaching size limit

Two generated AMD ISA files exceed 800 lines (audit threshold) but remain under
the 1000-line hard limit:

| File | Lines |
|------|-------|
| `codegen/amd/isa_generated/vop3/mod.rs` | 929 |
| `codegen/amd/isa_generated/mimg/table.rs` | 801 |

These are machine-generated by `tools/amd-isa-gen` and not hand-edited.

---

## Code Quality (PASS)

| Dimension | Status |
|-----------|--------|
| SPDX headers (`AGPL-3.0-or-later`) | ✅ All `.rs` files |
| `#![forbid(unsafe_code)]` | ✅ All crate roots |
| `#![warn(missing_docs)]` | ✅ All library crates |
| No `TODO`/`FIXME`/`HACK`/`todo!()`/`unimplemented!()` | ✅ Clean |
| No `.unwrap()` in library code | ✅ Zero |
| All `.expect()` have reason strings | ✅ |
| No commented-out code | ✅ |
| No files >1000 lines | ✅ |
| No hardcoded primal names in production | ✅ Capability discovery only |
| No hardcoded ports (all env/CLI overridable) | ✅ |
| No `unsafe` in production code | ✅ (3 blocks in test env helper only) |
| `#[allow(...)]` with reason strings | ✅ All have reasons |

---

## Architecture Compliance

| Dimension | Status | Notes |
|-----------|--------|-------|
| JSON-RPC 2.0 + tarpc | ✅ | NDJSON wire, tarpc optional |
| BTSP ClientHello | ✅ SHIPPED | Phase 2 + Phase 3 + client handshake |
| UniBin (clap subcommands) | ✅ | `server`, `compile`, `doctor` |
| genomeBin scaffolding | ✅ | `genomebin/manifest.toml` present |
| Semantic method naming | ✅ | `shader.compile.*`, `health.*`, etc. |
| Capability-based discovery | ✅ | No hardcoded peer names |
| Zero unsafe | ✅ | Hardware dispatch via IPC to toadStool |
| Pure Rust deps | ✅ | Transitive `libc` via tokio/mio only |
| Platform-agnostic IPC | ✅ | Unix socket + TCP fallback |
| `bytes::Bytes` for payloads | ✅ | |

---

## Crate Architecture

| Crate | Role | Lines | Tests |
|-------|------|-------|-------|
| `coralreef-core` | Primal lifecycle, IPC, CLI binary | ~20,685 | ❌ blocked |
| `coral-reef` | Compiler core (WGSL/SPIR-V/GLSL → GPU binary) | ~120,530 | 2183 ✅ |
| `coral-reef-isa` | NVIDIA ISA tables, latency model | ~412 | 20 ✅ |
| `coral-reef-stubs` | Pure-Rust Mesa replacements | ~4,786 | 199 ✅ |
| `bitview` | Bit-level instruction encoding | ~618 | 25 ✅ |
| `nak-ir-proc` | Proc-macro derives for IR types | ~1,165 | 2 ✅ |
| `primal-rpc-client` | JSON-RPC 2.0 client library | ~970 | 21 ✅ |
| `amd-isa-gen` | ISA table generator tool | ~1,645 | (tool) |

**Total workspace**: ~456 `.rs` files, ~150K LOC.

---

## IPC Surface

### Served (18 advertised)

```
shader.compile.spirv       shader.compile.wgsl
shader.compile.status      shader.compile.capabilities
shader.compile.wgsl.multi  shader.compile.multi
shader.compile.gemm        health.check
health.liveness            health.readiness
health.version             identity.get
capability.list            capabilities.list
btsp.negotiate             auth.check
auth.mode                  auth.peer_info
```

### Consumed (client calls to other primals)

| Method | Target |
|--------|--------|
| `capability.register` | Ecosystem registry |
| `primal.announce` | Neural API routing |
| `ipc.heartbeat` | Registry keepalive |
| `crypto.sign` | bearDog (provenance signing) |
| `btsp.session.create` / `btsp.session.verify` | bearDog (BTSP handshake) |

---

## Recommendations for eastGate

### Immediate (P0 — build-breaking)

1. **Add `config::beardog_socket()`** — reads `$BEARDOG_SOCKET` env var as
   `Option<PathBuf>`, following the `non_empty_env_path` pattern already in
   `config.rs`.

2. **Add `newline_jsonrpc::compile_timeout()`** — returns `Duration`, reads
   `$CORALREEF_COMPILE_TIMEOUT_SECS` (default 120s or similar).

3. **Make `btsp::discover_by_capability` and `btsp::discover_security_socket`
   `pub(crate)`** — provenance.rs needs them for `crypto.sign` discovery.

4. **Fix or update `tests_unix_edge.rs:557`** — reference to removed
   `handle_connection` function.

5. **Run `cargo fmt`** — fixes all formatting drift.

6. **Fix clippy `assertions_on_constants`** in `latency.rs:75` — wrap in
   `const { assert!(..) }`.

### Short-term (P1)

7. **Wire remaining 7 JSON-RPC methods** in `dispatch_jsonrpc` —
   `shader.compile.multi`, `shader.compile.gemm`, `health.version`,
   `capabilities.list`, `btsp.negotiate`, `auth.check/mode/peer_info`.

8. **Update `Cargo.toml` repository URL** from GitHub to Forgejo.

9. **Update README test count** after build is fixed.

### Compute Trio deployment readiness

The compiler core (`coral-reef`) is fully functional — 2183 tests pass, zero
failures. The primal lifecycle/IPC layer (`coralreef-core`) has merge-residue
compile errors that block the `coralreef server` binary from building. The
`coralreef compile` subcommand (offline shader compilation) may work if the
compile path doesn't touch the broken IPC modules, but this needs verification
after fixes.

**Deployment of coralReef to strandGate is blocked on P0 fixes.**

---

## Root Cause

All P0 issues trace to commit `8ebd97d9` ("fix: resolve IPC merge conflicts —
accept upstream BTSP + transport evolution"). The merge introduced references to
functions that were renamed, removed, or kept private during the BTSP/transport
refactor. The merge compiled against an intermediate state that no longer exists
on `main`.
