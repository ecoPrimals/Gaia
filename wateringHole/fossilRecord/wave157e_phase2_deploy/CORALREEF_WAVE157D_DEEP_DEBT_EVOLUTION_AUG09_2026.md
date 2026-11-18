# coralReef — Wave 157d Deep Debt Evolution

**Date**: Aug 9, 2026  
**From**: coralReef on strandGate (eastGate overwatch)  
**Commit**: `fd02aa54`  
**Previous**: `2ecb25fd` (OpRedux scheduler fix)

---

## What Shipped

### File Structure Evolution
- **`transport.rs` (1285 LOC) → `transport/` directory** (4 files, max 460 LOC).
  Only file violating the 1000-line standard — now eliminated. Split into
  `mod.rs` (endpoint types + env parsing), `stream.rs` (async I/O + bind),
  `sync_stream.rs` (blocking I/O), `resolve.rs` (bind resolution + symlink).
- **`compile.rs` (834 LOC) → 569 LOC**. Batch/multi-device handlers extracted
  to `compile_batch.rs` (285 LOC) as cohesive batch compilation module.

### Hardcoded Primal Name Elimination
- **Last runtime reference**: `transport.rs:383` — `"songBird routing"` →
  `"mesh routing capability provider"`. Zero production code now references
  another primal by name.
- **12 doc-comment references** evolved to capability-domain references across
  7 files (btsp.rs, method_gate.rs, protocol_negotiation.rs, ecosystem/mod.rs,
  types.rs, sm70_instr_latencies.rs).

### Semantic Naming
- `placeholder` SSA variables (7 instances in `naga_translate`) renamed to
  `ptr_undef` — clarifies these are intentional `OpUndef` markers for
  pointer/reference slots, not unfinished implementations.

### Dependency Audit
- `blake3` build-time `cc`: confirmed inert with `features = ["pure"]`.
  Upstream declares `cc` in `[build-dependencies]` unconditionally but does
  not compile any C code. No action needed.
- `bincode` 1.3.3 unmaintained advisory: transitive via tarpc. Acknowledged
  in `deny.toml`. Not actionable without replacing tarpc.

---

## Metrics

| Metric | Value |
|--------|-------|
| Tests | **3,715** (3,711 passed, 4 ignored) |
| Clippy warnings | **0** (pedantic + nursery) |
| Unsafe in production | **0** |
| TODO/FIXME/HACK in `.rs` | **0** |
| `.unwrap()` in library | **0** |
| Files over 1000 LOC | **0** |
| Hardcoded primal names (runtime) | **0** |
| EVOLUTION markers | **9** (intentional future-work) |

---

## Audit Summary (this wave)

| Category | Status |
|----------|--------|
| Root docs updated | README, STATUS, CHANGELOG, WHATS_NEXT |
| Production code markers | Zero TODO/FIXME/HACK/DEBT in `.rs` |
| Archive material | 3 docs in `docs/archive/` (proper fossil record) |
| Debris/stale files | None found — zero `.bak`, `.tmp`, `.old` |
| Non-Rust production code | None — WGSL preambles + TOML configs only |
| Commented-out code | None found |
| `fuzz/Cargo.lock` | 3 months stale vs root — low priority |

---

## Remaining Work (coralReef-side)

Per `WHATS_NEXT.md`:

1. **Coverage push** — 84% → 90% (compiler backends are main gap)
2. **GEMM Phase 2** — shared memory tiling + `ldmatrix` + `bar.sync`
3. **Vertex/Fragment shaders** — 8-12 weeks, Phase C
4. **Compute gossip** — when swarmVine integration is ready
5. **Deploy across NUCLEUS gates** — depot unified, 4 arches

---

## For Upstream Teams

- **barraCuda**: `CoralReefDevice` → `shader.compile.wgsl` IPC wiring is
  unblocked on coralReef side (18/18 methods LIVE, wire contract tested).
- **toadStool**: `shader.compile.capabilities` queryable for silicon registry.
  Dispatch descriptor `shader_info` fields populated.
- **All primals**: Zero coralReef blockers. All P0s resolved fleet-wide.

---

*Wave 157d — deep debt evolution. transport.rs split, compile.rs refactored,
zero hardcoded primal names, zero markers, zero debris. 3,715 tests. Clean.*
