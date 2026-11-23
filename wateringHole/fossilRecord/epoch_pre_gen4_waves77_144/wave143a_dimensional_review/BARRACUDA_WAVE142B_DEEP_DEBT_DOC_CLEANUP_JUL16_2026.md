# barraCuda Wave 142b — Deep Debt Sweep, Transport Abstraction & Doc Cleanup

**Date**: 2026-07-16
**Primal**: barraCuda (Layer 1 — GPU compute engine)
**Gate**: strandGate
**Commits**: `82f0b8e2` (transport), `75c1c880` (safety/visibility), pending (docs/cleanup)

## Completed Work

### Phase 2 Transport Abstraction
- 5 `#[cfg(unix)]` gates removed — `neural_announce.rs`, `discovery.rs`, `commands.rs` now transport-agnostic via `connect_transport`
- `coral_compiler/jsonrpc.rs` intentionally retains `#[cfg(unix)]` — `barracuda` crate does not depend on `barracuda-core` transport layer (documented)

### Dead Code Removal (-867 lines)
- `pipeline/stage.rs` (384L) and `pipeline/cascade.rs` (483L) — orphan files never included in build
- Dead `parallel` feature flag removed from `Cargo.toml`

### ODE Generic Dispatch
- `integrate_adaptive`, `integrate_fixed`, `integrate_cpu`, `integrate_hybrid` — `Box<dyn Fn>` → `&impl Fn` (unboxed closures)

### Safe u32 Casts
- `checked_u32()` and `shape_to_u32()` helpers in `utils.rs`
- 3 high-risk sites migrated: `index_select`, `sparse_matmul_quantized`, `moving_window_stats`

### Visibility Tightening
- 6 shader optimizer types/functions narrowed from `pub` to `pub(super)`
- Redundant `BindingNode::latency()` method removed

### LatencyModel Enum Dispatch
- Trait with 5 implementing structs → single enum with 5 variants
- Eliminates heap allocation on every shader compilation

### GPU Test Pool Migration (76 tests)
- ESN model (22), three_springs (35), tensor_tests (17), concat (5), scalar ops, FHE ops
- Shared `WgpuDevice` via `test_pool::get_test_device()` — eliminates `SIGSEGV` from concurrent device creation

### Documentation Refresh (this wave)
- MSRV 1.87 → 1.92 across 3 docs (CONTRIBUTING, CONVENTIONS, BREAKING_CHANGES)
- Test count 4,624 → 5,153 across 6 docs (README, STATUS, PURE_RUST_EVOLUTION, sporeprint, WHATS_NEXT context)
- Shader count 826 → 860, Rust file count 1,169 → 1,211 across 5 docs
- IPC method count reconciled to 98 across capability_registry.toml, .cursor/rules, SOVEREIGN_PIPELINE_TRACKER
- Dead `parallel` feature removed from README feature flag table
- tarpc endpoints 16 → 15, mesh 4-gate → 5-gate in README
- 2 superseded specs archived to fossilRecord (MODEL_SERIALIZATION_DESIGN, AAR_CROSS_VENDOR_GPU_VALIDATION)

## Current Posture

| Metric | Value |
|--------|-------|
| MSRV | 1.92 |
| Edition | 2024 |
| IPC methods | 98 |
| tarpc endpoints | 15 |
| Tests | 5,153 (4,377 barracuda + 760 core + 16 naga-exec) |
| WGSL shaders | 860 |
| Rust source files | 1,211 |
| Clippy warnings | 0 |
| Production unwrap/panic/expect | 0 |
| `#[allow()]` suppressions | 0 |
| Files > 800L | 0 |
| Cross-arch (`x86_64-pc-windows-gnu`) | Compiles clean |

## Remaining Phase 2 Work (P2)
- Server-side listen abstraction: `server.rs` `serve_unix()` still gated — needs `TransportListener` trait
- BTSP relay un-gating: requires `serve_unix()` transport-agnostic first
- `coral_compiler/jsonrpc.rs`: architectural boundary prevents `connect_transport` adoption without cross-crate dependency

## For Upstream Audit
- WGSL duplicate shader review: 7 byte-identical pairs across `shaders/nuclear/` ↔ `shaders/physics/` and `ops/md/` ↔ `shaders/md/`
- `specs/BARRACUDA_SPECIFICATION.md`: severely stale (lists 31 methods, dead features) — needs rewrite or "SUPERSEDED" banner
- `specs/REMAINING_WORK.md`: 2K-line historical tracker — consider trimming completed sections
- Coverage 80.54% → 90% target requires real GPU hardware testing
