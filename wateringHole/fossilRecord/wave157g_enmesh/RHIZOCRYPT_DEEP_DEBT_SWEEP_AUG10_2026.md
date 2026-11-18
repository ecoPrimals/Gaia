# rhizoCrypt — Deep Debt Sweep Handoff

**Date**: August 10, 2026  
**Scope**: Systematic deep debt audit + evolution across rhizoCrypt codebase  
**Commit**: `308bacd`  

## Survey Results

| Category | Finding |
|----------|---------|
| Large files (>800L) | **Zero** in production. Only `method_gate_tests.rs` (856L, test file) — now split into 3 modules |
| Unsafe code | **Zero** production unsafe. `unsafe_code = "deny"` workspace-wide |
| Hardcoding | **Zero** hardcoded IPs/endpoints in production. All test IPs, constants use `const` |
| Mocks in production | **Zero**. All mocks gated behind `#[cfg(any(test, feature = "test-utils"))]` |
| Debt markers | **3 doc references only** (no actionable TODO/FIXME/HACK/stub/placeholder) |
| Suppressed lints | **3 total**, all justified (serde API, Arc not const, `as_ref()` not const-stable) |

## Changes Executed

### P0 — High Impact

1. **Extract `build_signed_vertex()`** (`service_vertex_ops.rs`)
   - Vertex builder pattern was duplicated 4× across `impl_append_event`, `impl_append_batch` (2×), and `impl_pipeline_ingest`
   - Extracted into single `async fn build_signed_vertex()` — ~60 lines removed, single source of truth
   - Reduces bug surface for vertex construction changes

2. **Standardize branch handlers on `impl_*`** (`handler/branch.rs`)
   - `dispatch_branch`, `dispatch_diff`, `dispatch_merge`, `dispatch_federate` now call `server.impl_*()` directly
   - Eliminates tarpc `server.clone()` + `tarpc::context::current()` overhead per dispatch
   - Removed unused `RhizoCryptRpc` trait import

### P1 — Allocation & Correctness

3. **Zero-copy federate deserialization** (`handler/branch.rs`)
   - `dispatch_federate` now takes `mut params: Value` and consumes the `"vertices"` array via `obj.remove()` + `into_iter()`
   - Each vertex is deserialized by `serde_json::from_value(v)` — no `.clone()` needed
   - Real allocation win on federation payloads with many vertices

4. **PresenceVerifier doc update** (`method_gate_verifier.rs`)
   - Stale doc said "pre-JH-11 placeholder" — misleading because `CapabilityVerifier` with real `auth.verify_ionic` IPC already exists
   - Updated to describe it as "permissive-mode degradation fallback" used when no `crypto:signing` provider is discoverable

### P2 — Optimization & Structure

5. **`#[inline]` on merkle hot paths** (`merkle.rs`)
   - Added `#[inline]` to `MerkleRoot::compute` and `MerkleProof::verify`
   - These are called on every dehydration and proof verification — strong candidates for inlining

6. **Test file split** (`method_gate_tests.rs` → 3 modules)
   - Split 856-line monolithic test file into focused modules via `#[path]`:
     - `method_gate_tests_classification.rs` — classification, scope matching, enforcement, constructors (~160L)
     - `method_gate_tests_verifier.rs` — token verifiers, parse_verify_ionic, scope extraction, expires_in (~220L)
     - `method_gate_tests_gate.rs` — bearer extraction, caller context, gate checks, auth responses, BTSP (~290L)
   - Shared helpers remain in `method_gate_tests.rs` (~110L orchestrator)
   - No production file exceeds 800L

## Quality Gates

| Gate | Status |
|------|--------|
| `cargo clippy --workspace --all-targets` | ✅ 0 errors, 0 new warnings |
| `cargo test --workspace` | ✅ 1,832 passing |
| `cargo fmt --check` | ✅ Clean |
| `cargo check --target x86_64-pc-windows-gnu` | ✅ Clean |
| `cargo deny check` | ✅ advisories ok, bans ok, licenses ok, sources ok |

## Doc Cleanup Pass

- Updated stale metrics across 8 files: README, CONTEXT, DEPLOYMENT_CHECKLIST, validation-summary, RHIZOCRYPT_SPECIFICATION, specs index, rhizocrypt-service README
- Aligned: test count (1,832), source files (229), method count (40), max file size (639L)
- Removed stale WireMock comment from `tests_tarpc.rs`
- Zero debris (no backup, temp, log, or stray files)
- `cargo clean`: reclaimed 20GB (30,298 build artifacts)

## Metrics

- 229 `.rs` files, ~61,850 lines
- Max production file: 639L (`service.rs`)
- Zero unsafe, zero production mocks, zero hardcoded endpoints
- 10 wateringHole handoffs total (this session: gossip, G72, deep debt, doc cleanup)
