# Handoff: toadStool G68 L3 Trait Implementation + Scanner False Positive (S361)

**Date**: Aug 7, 2026 | **Sprint**: S361 | **Wave**: 157a
**Author**: strandGate | **Primal**: toadStool
**Commit**: `0683401e6` on `main`

---

## Summary

First concrete L3 backend trait implementations shipped in `hw-safe`. Scanner L2 false positive documented for sourDough team.

## Changes

### L3 Trait Implementations (hw-safe)

| Type | Trait | Implementation |
|------|-------|---------------|
| `LinuxMemoryMapper` | `platform::MemoryMapper` | `map_file()` → `SafeMmapRegion`, `map_anonymous()` → `mmap_anonymous` |
| `LinuxPinnedMemory` | `platform::PinnedMemory` | `pin()` → `mlock`, `unpin()` → `munlock`. Safe `&[u8]` API. |
| `SafeMmapRegion` | `platform::MappedMemory` | `as_ptr()`, `as_mut_ptr()`, `len()` |

### Pattern Established

```
toadstool-common::platform::device_io   ← trait definitions (all platforms)
         ↓
toadstool-hw-safe::platform_backends    ← Linux implementations (cfg(linux))
         ↓
cylinder, akida-driver, display         ← callers (adopt incrementally)
```

## Scanner False Positive — sourDough

**Reported**: 1 L2 violation in `akida-driver/hybrid/selector.rs`
**Reality**: `self.esn.mode()` returns `&SubstrateMode` (ESN execution mode enum), **not** filesystem `Permissions::mode()`.

The sourDough scanner v2 pattern-matches `.mode()` calls without distinguishing:
- `std::fs::Permissions::mode()` — actual L2 violation
- `HybridEsn::mode()` → `SubstrateMode` — unrelated method

**Suggested fix for sourDough**: Check the receiver type or preceding import. If `PermissionsExt` is not in scope, `.mode()` is not an L2 violation.

**toadStool actual L2 count**: **0 production violations** (not 1).

## Actual toadStool G68 Status

| Layer | Status | Count |
|-------|--------|-------|
| **L1** | COMPLIANT | 0 violations |
| **L2** | COMPLIANT | 0 prod violations (scanner reports 1 false positive) |
| **L3** | TRAIT PATTERN LIVE | 15 rustix sites in 6 crates — now with concrete trait impls to migrate toward |

## Quality Gates

- `cargo check --workspace`: 0 errors
- `cargo fmt --check`: PASS
- `cargo test -p toadstool-hw-safe`: 40 tests PASS
- Windows cross-compile: PASS
