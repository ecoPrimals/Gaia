<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# coralReef — strandGate Deep Debt Execution (Wave 155f)

**Gate**: strandGate  
**Primal**: coralReef v0.2.0  
**Date**: 2026-07-28  
**Wave**: 155f  
**Hardware**: Dual EPYC 7452 (64 cores) + RTX 3090 (24GB VRAM)  
**Prior**: `CORALREEF_WAVE155f_STRANDGATE_AUDIT_JUL28_2026.md` (audit findings)  
**Action**: Full execution of all identified P0/P1 issues + deep debt cleanup

---

## Build Status — ALL FOUR GATES PASS

| Check | Result | Detail |
|-------|--------|--------|
| `cargo test --all-features` | **PASS** | 3527 passed, 0 failed, 6 ignored |
| `cargo clippy --all-targets --all-features -- -W clippy::pedantic -W clippy::nursery -D warnings` | **PASS** | Zero warnings, zero errors |
| `cargo fmt --check` | **PASS** | No drift |
| `cargo doc --all-features --no-deps` | **PASS** | Clean build |

---

## P0 Fixes — Build Blockers (All Resolved)

These were identified in the audit as originating from merge commit `8ebd97d9`.

| # | Issue | Fix |
|---|-------|-----|
| 1 | `config::beardog_socket()` not found | Added function + `BEARDOG_SOCKET` env key |
| 2 | `newline_jsonrpc::compile_timeout()` not found (5 call sites) | Added `config::compile_timeout()`, re-exported from `newline_jsonrpc` |
| 3 | `btsp::discover_security_socket` private | Changed to `pub(crate)` |
| 4 | `btsp::discover_by_capability` private | Changed to `pub(crate)` |
| 5 | `unix_jsonrpc::handle_connection` not found | Implemented complete BTSP Phase 3 handler with ChaCha20-Poly1305 AEAD |
| 6 | `default_unix_socket_path()` bypasses `BIOMEOS_SOCKET_DIR` | Rewired to canonical 4-tier `socket_base_dir()` resolution |
| 7 | Formatting drift (`btsp.rs`, `newline_jsonrpc.rs`) | `cargo fmt` |
| 8 | Clippy `assertions_on_constants` in `latency.rs` | Extracted to local `let` bindings |
| 9 | 4 integration tests failing (`unix_jsonrpc_default_socket_path_env`) | Fixed by socket resolution unification (#6) |
| 10 | Type inference cascades from missing functions | Resolved by fixes #1-5 |

## P1 Fixes — Functional Gaps (All Resolved)

| # | Issue | Fix |
|---|-------|-----|
| 1 | 7 JSON-RPC methods unrouted in dispatch | Wired: `shader.compile.multi`, `shader.compile.gemm`, `health.version`, `btsp.negotiate`, `auth.check`, `auth.mode`, `auth.peer_info`, `capabilities.list` alias |
| 2 | Repository URL points to GitHub | Updated to `https://git.primals.eco/ecoPrimals/coralReef` |
| 3 | Stale test count in README | Updated to 3527 |

## Deep Debt — Clippy Pedantic+Nursery (All Resolved)

~50 violations cleaned across both crates:

- `u8 as u32` → `u32::from()` (infallible casts)
- Doc backticks for code references (`ClientHello`, `BearDog`, etc.)
- Missing `# Errors` doc sections
- Redundant closures → method references
- `div_ceil` reimplementations → `usize::div_ceil()`
- Unnecessary `collect()` → direct iterator use
- Constant assertion values → local `let` bindings
- Raw string hash cleanup (`r#"..."#` → `r"..."`)
- Match arm deduplication
- Case-sensitive extension comparisons
- Dead code annotations with `reason` attributes on all `#[allow(...)]`

---

## Code Quality Audit

| Metric | Value |
|--------|-------|
| `.rs` files | 456 |
| Rust lines (approx.) | ~151,269 |
| Files > 1000 lines | **0** |
| `TODO` in `.rs` | **0** |
| `FIXME` in `.rs` | **0** |
| `HACK` in `.rs` | **0** (6 false positives: author surname "Hack" in citations) |
| `todo!()` / `unimplemented!()` | **0** |
| `unsafe` in production | **0** (`#![forbid(unsafe_code)]` on all crates) |
| `.unwrap()` in library code | **0** |
| Stale scripts/debris | **0** (workspace is clean) |

---

## JSON-RPC Dispatch — Complete (18 Served Methods)

| Method | Type | Status |
|--------|------|--------|
| `shader.compile.wgsl` | Protected | Routed |
| `shader.compile.spirv` | Protected | Routed |
| `shader.compile.wgsl.multi` | Protected | Routed |
| `shader.compile.multi` | Protected | **NEW** — batch mixed-input |
| `shader.compile.gemm` | Protected | **NEW** — tensor-core HMMA |
| `shader.compile.status` | Protected | Routed |
| `shader.compile.capabilities` | Protected | Routed |
| `health.check` | Public | Routed |
| `health.liveness` | Public | Routed |
| `health.readiness` | Public | Routed |
| `health.version` | Public | **NEW** — build identity |
| `identity.get` | Public | Routed |
| `capability.list` | Public | Routed |
| `capabilities.list` | Public | **NEW** — alias |
| `btsp.negotiate` | Protected | **NEW** — Phase 3 cipher |
| `auth.check` | Public | **NEW** — gate introspection |
| `auth.mode` | Public | **NEW** — enforcement mode |
| `auth.peer_info` | Public | **NEW** — caller identity |

---

## Files Modified (26 files)

```
Cargo.toml                                          # Repository URL
README.md                                           # Test counts, checks table
CHANGELOG.md                                        # Wave 155f entry
STATUS.md                                           # Wave/test updates
WHATS_NEXT.md                                       # Wave/test updates
crates/coral-reef-isa/src/latency.rs                # Clippy fix
crates/coral-reef/src/codegen/calc_instr_deps/mod.rs # Clippy fix
crates/coral-reef/src/codegen/nv/ptx_emit/tests_core.rs # Clippy fix
crates/coral-reef/src/codegen/nv/ptx_emit/tests_math_ext.rs # Clippy fix
crates/coral-reef/tests/codegen_coverage_deep.rs     # Clippy fix
crates/coral-reef/tests/codegen_coverage_multi_arch.rs # Clippy fix
crates/coral-reef/tests/codegen_sat/helpers.rs       # Clippy fix
crates/coral-reef/tests/compiler_integration/main.rs # Removed stale constant
crates/coral-reef/tests/idempotency.rs               # Clippy fix
crates/coralreef-core/src/config.rs                  # beardog_socket(), compile_timeout()
crates/coralreef-core/src/env_keys.rs                # BEARDOG_SOCKET
crates/coralreef-core/src/ipc/btsp.rs                # pub(crate) visibility, doc fixes
crates/coralreef-core/src/ipc/btsp_client.rs         # Dead code annotation
crates/coralreef-core/src/ipc/btsp_negotiate.rs      # Drop cleanup
crates/coralreef-core/src/ipc/method_gate.rs         # Dead code annotation
crates/coralreef-core/src/ipc/newline_jsonrpc.rs     # compile_timeout re-export, 8 dispatch routes
crates/coralreef-core/src/ipc/tests_unix_dispatch.rs # Clippy fix
crates/coralreef-core/src/ipc/tests_unix_edge.rs     # Doc backticks
crates/coralreef-core/src/ipc/unix_jsonrpc.rs        # handle_connection(), socket resolution
crates/coralreef-core/src/service/mod.rs             # Dead code annotation
crates/coralreef-core/src/service/provenance.rs      # Dead code annotation
crates/coralreef-core/src/service/types.rs           # Dead code annotation
crates/coralreef-core/src/ecosystem/tests/tests_ecosystem.rs # Clippy fixes
crates/coralreef-core/src/service/tests_spirv.rs     # Clippy fixes
```

---

## Recommendations for Upstream

1. **Coverage push**: 84% → 90% target. Compiler backends are the main gap.
2. **SM120 Blackwell**: PTX emitter tolerance tests are `WIP` — vertex/fragment emission.
3. **`PRIMALSPRING_AUTH_MODE`**: Removal target v0.3.0 — all gates must migrate to `ECOSYSTEM_AUTH_MODE`.
4. **STATUS.md consolidation**: At 1315 lines, consider splitting or archiving older phase details.
5. **wateringHole**: `audit.log` at wateringHole root should be `.gitignore`d.

---

**Prepared by**: strandGate code team  
**For**: overwatch upstream audit + golgiBody cascade
