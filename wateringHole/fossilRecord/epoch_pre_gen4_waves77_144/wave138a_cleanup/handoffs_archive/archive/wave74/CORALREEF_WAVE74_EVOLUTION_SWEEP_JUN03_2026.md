# coralReef — Wave 74 Evolution Sweep

**Date**: June 3, 2026  
**Sprint**: 14  
**Wave**: 74  
**From**: strandGate (coralReef team)  
**To**: primalSpring (upstream audit), hotSpring (validation)

---

## Summary

Deep debt cleanup and primal composition evolution across two commits:
1. Smart refactoring & stub evolution (file size reduction, fail-safe RT stub)
2. Composition self-knowledge (socket unification, timeout configurability, methods deduplication, matrix coverage)

## Changes Delivered

### Architecture / Composition (HIGH IMPACT)

- **Socket path resolution unified**: `config::socket_base_dir()` is now the single canonical 3-tier resolver (`$BIOMEOS_SOCKET_DIR` > `$XDG_RUNTIME_DIR` > `/run/biomeos`). Previously `ecosystem.rs`, `ipc/unix_jsonrpc.rs`, and `ipc/btsp.rs` each had their own resolution — `primal.announce` could advertise a different path than the actual bind. **Now fixed**.
- **`config::default_socket_path()`**: Both server bind and `primal.announce` use this single function.
- **`service::SERVED_METHODS`**: Single `pub const` of all 16 JSON-RPC methods. Eliminates duplication between `handle_capability_list()` and `primal.announce`.

### Env-Configurable Timeouts

| Key | Default | Purpose |
|-----|---------|---------|
| `CORALREEF_SHUTDOWN_TIMEOUT_SECS` | 30 | Graceful shutdown duration |
| `CORALREEF_REGISTRY_TIMEOUT_SECS` | 2 | Ecosystem registry RPC timeout |

### Coverage Expansion

- **3x3 matrix inverse**: Cofactor-based `emit_inverse3x3()` in `math_matrix.rs`. Uses existing `emit_det2x2` for minors + `rcp.approx.f32` for 1/det.
- **AMD `tanh` guard improved**: Error message now documents it's a defensive ICE path (IR always lowers tanh before reaching AMD encoder).

### Smart Refactoring

- `math_pack.rs` 904→662 LOC (matrix ops → `math_matrix.rs` 314 LOC)
- `service/tests.rs` 974→589 LOC (serde tests → `tests_serde.rs` 409 LOC)
- Ray query stub: fail-dangerous (`setp 1,1` → infinite loop) → fail-safe (`setp 0,1` → traversal terminates)

### Root Documentation

- `README.md` → Wave 74
- `.cursor/rules/rust-patterns.mdc` → Removed stale `coral-driver` unsafe guidance (excised Sprint 9)
- `cargo clean` → 13.1 GiB freed

## Metrics

- **3284 tests**, 0 failures
- **Zero** clippy warnings (pedantic + nursery)
- **Zero** unsafe code (`#![forbid(unsafe_code)]` all crates)
- **Zero** C dependencies
- **Zero** production `.unwrap()`

## Known Remaining Gaps (for upstream teams)

### AMD Backend (P3 — low priority, no users yet)
- Bindless CBuf access
- VOP3 third literal (needs scratch VGPR)
- `TranscendentalOp::Tanh` defensive guard (IR already lowers; guard is ICE-path)

### PTX Coverage (P3 — edge cases)
- `ImageAtomic` / `ImageStore` / `ImageLoad` on non-global images
- `SubgroupGather` non-standard modes
- N×N matrix inverse (N > 3)

### Composition (RESOLVED this wave)
- Socket path divergence ✓ FIXED
- Timeout hardcoding ✓ FIXED (env-configurable)
- Methods duplication ✓ FIXED (SERVED_METHODS)

## Deployment

```bash
ECOPRIMALS_ROOT=/path/to/ecoPrimals plasmidbin install coralreef
```

## Upstream Asks

1. **primalSpring**: Audit `config::socket_base_dir()` resolution vs other primals' socket base resolution — ensure ecosystem-wide alignment.
2. **hotSpring**: Validate `primal.announce` `socket` field now matches actual bind path under various env configurations.
3. **biomeOS**: New env keys `CORALREEF_SHUTDOWN_TIMEOUT_SECS` and `CORALREEF_REGISTRY_TIMEOUT_SECS` available for NUCLEUS tuning.

---

*Filed by strandGate coralReef — Wave 74 cascade*
