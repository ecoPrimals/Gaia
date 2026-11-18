# Handoff: toadStool G68 L2 Convergence (S359)

**Date**: Aug 7, 2026 | **Sprint**: S359 | **Wave**: 157a
**Author**: strandGate | **Primal**: toadStool
**Commit**: `7caa63c89` on `main`

---

## Summary

Final G68 L2 compliance — migrated last 2 production `PermissionsExt` violations in `akida-setup`. Zero raw `PermissionsExt` usage remains in production code. toadStool is now **G68 L2 COMPLIANT**.

## Changes

| File | Change |
|------|--------|
| `akida-setup/src/permissions.rs` | `set_file_permissions()` → `PlatformAccess::Custom(mode)` via `set_access()` |
| `akida-setup/src/verification.rs` | Device node perm check → `check_access(path, PlatformAccess::Custom(0o666))` |
| `platform/access.rs` | `Custom` mode in `check_access` now uses bitmask semantics (`& mask == mask`) |
| `platform/access.rs` | `#[allow(clippy::verbose_bit_mask)]` for octal permission patterns |
| `btsp/mod.rs` | Doc comment added to non-Unix stub (resolves `missing_docs` warning) |

## G68 Compliance Status

| Layer | Status | Detail |
|-------|--------|--------|
| **L1 (Links)** | COMPLIANT | `platform_link()` — 3/3 sites migrated (S358) |
| **L2 (Access)** | COMPLIANT | `PlatformAccess` + `set_access()`/`check_access()` — 9/9 sites migrated (S358+S359) |
| **L3 (Device Backends)** | GLACIAL | 11 violations in cylinder, hw-safe, nvpmu, akida-driver, sandbox, display — all already `#[cfg(unix)]` gated. Backend trait abstraction is long-term work. |

## Quality Gates

- `cargo check --workspace`: PASS (0 warnings)
- `cargo fmt --check`: PASS
- `cargo clippy -p toadstool-common -p akida-setup -- -D warnings`: PASS
- `cargo test -p toadstool-common`: 125 tests PASS
- `cargo check -p akida-setup --target x86_64-pc-windows-msvc`: PASS

## Notes for Upstream

- **sourDough**: toadStool should now report 0 L2 violations when `sourdough validate platform-substrate` is updated. The 11 L3 hits are acknowledged glacial scope (device I/O in designated unsafe crates).
- **blueGate**: Windows cross-compile remains clean — no new `#[cfg(unix)]` leakage.
- **overwatch**: The `check_access(Custom(mask))` now uses bitmask semantics (all required bits present) rather than exact-mode equality. This is the correct interpretation for "does this path have at least these permissions."
