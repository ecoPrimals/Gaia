<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# LoamSpine — Wave 157a: G68 Platform Substrate + Deep Debt

**Date**: August 7, 2026  
**Wave**: 157a  
**From**: sporeGate (loamSpine team)  
**Status**: SHIPPED — G68 L1 + L2 implemented, deep debt resolved

---

## What Shipped

### G68 L1: Filesystem Links

New `platform::fs` module in `loam-spine-core`:

| Function | Unix | Windows | Other |
|----------|------|---------|-------|
| `create_link(target, link)` | `std::os::unix::fs::symlink` | `std::os::windows::fs::symlink_file` | `Unsupported` error |
| `remove_link(path)` | `std::fs::remove_file` | `std::fs::remove_file` | `std::fs::remove_file` |

**Impact**: `main.rs` no longer imports `std::os::unix::fs::symlink`. All filesystem link operations route through the `platform` module.

### G68 L2: File Access Control

New `platform::access` module in `loam-spine-core`:

| Function / Type | Unix | Windows / Other |
|-----------------|------|-----------------|
| `PlatformAccess::Executable.apply(path)` | `chmod 0o755` | no-op (extension-based) |
| `PlatformAccess::ReadOnly.apply(path)` | `chmod 0o444` | `set_readonly(true)` |
| `PlatformAccess::ReadWrite.apply(path)` | `chmod 0o644` | `set_readonly(false)` |
| `set_executable(path)` | `chmod 0o755` | no-op |
| `is_executable(path)` | `mode & 0o111 != 0` | `!readonly` heuristic |

**Impact**: `cli_signer_integration.rs` and `cli_signer_tests_integration.rs` no longer import `std::os::unix::fs::PermissionsExt`. Zero `PermissionsExt` usage outside the platform layer.

### G68 Compliance Summary

| Layer | Status | Notes |
|-------|--------|-------|
| **L1: Links** | **ABSTRACTED** | `platform::create_link` replaces raw symlink calls |
| **L2: Permissions** | **ABSTRACTED** | `PlatformAccess::apply()` replaces `PermissionsExt` |
| **L3: Device backends** | **CLEAN** | No `rustix`/`libc` usage. UDS gated at module level. |
| Transport (G66) | **GOLD STANDARD** | `TransportStream`/`TransportListener` already fully abstracted |
| Signals | **ABSTRACTED** | `wait_for_shutdown()` dispatches Unix/Windows via `#[cfg]` |

### Error Hygiene

`LoamSpineService::get_certificate()` evolved:

```
Before: pub async fn get_certificate(&self, cert_id: CertificateId) -> Option<Certificate>
         // .ok().flatten() silently swallowed storage errors

After:  pub async fn get_certificate(&self, cert_id: CertificateId) -> LoamSpineResult<Option<Certificate>>
         // Storage errors propagate; None means "not found"
```

All callers updated (2 production paths in `certificate_loan.rs`, ~25 test call sites).

### Constant Hygiene

- `socket.rs:158`: Hardcoded `"loamspine"` → `primal_names::SELF_ID`

---

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| Tests | 1,787 | **1,796** (+9: 4 fs, 5 access) |
| Source files | 212 | **215** (+3 platform module files) |
| `std::os::unix` outside platform | 7 sites | **0** |
| `PermissionsExt` outside platform | 5 sites | **0** |
| Silent error swallowing | 1 site | **0** |
| Hardcoded primal names | 1 drift | **0** |
| Clippy | 0 | 0 |
| Fmt | clean | clean |
| Doc | 0 warnings | 0 warnings |

---

## Files Changed

| File | Change |
|------|--------|
| `crates/loam-spine-core/src/platform/mod.rs` | **NEW** — G68 platform substrate module (re-exports L1 + L2) |
| `crates/loam-spine-core/src/platform/fs.rs` | **NEW** — `create_link`/`remove_link` with Unix/Windows/Other backends + 4 tests |
| `crates/loam-spine-core/src/platform/access.rs` | **NEW** — `PlatformAccess`/`set_executable`/`is_executable` + 5 tests |
| `crates/loam-spine-core/src/lib.rs` | Added `pub mod platform` |
| `crates/loam-spine-core/src/service/certificate.rs` | `get_certificate` → `LoamSpineResult<Option<Certificate>>` |
| `crates/loam-spine-core/src/service/certificate_loan.rs` | Added `?` for new Result return type |
| `crates/loam-spine-core/src/neural_api/socket.rs` | `"loamspine"` → `primal_names::SELF_ID` |
| `crates/loam-spine-api/src/service/certificate_ops.rs` | Added `?` for new Result return type |
| `bin/loamspine-service/main.rs` | `std::os::unix::fs::symlink` → `platform::create_link` |
| `crates/loam-spine-core/tests/cli_signer_integration.rs` | `PermissionsExt` → `platform::is_executable` |
| `crates/loam-spine-core/src/traits/cli_signer_tests_integration.rs` | `PermissionsExt` → `platform::set_executable` (4 sites) |
| 6 test files | Updated `.await` → `.await.unwrap()` for new Result type |
| Root docs | Test counts, source file counts, G68 status |

---

## Commit

```
cc1647b..HEAD on main
```

---

## What's Next for loamSpine

- **G68 fully compliant** — L1 links + L2 permissions + L3 clean. Zero violations.
- **G65 + G66 + G68** all shipped — loamSpine is cephalized and platform-abstracted
- Ready for **depot rebuild** when toadStool cross-arch fix lands
- **v0.10.0 targets**: Signing capability middleware, collision layer validation

---

*Wave 157a — G68 Platform Substrate shipped. `platform` module abstracts L1 links + L2 permissions. Zero `PermissionsExt` or raw OS symlink calls outside platform layer. Error hygiene: `get_certificate()` no longer swallows storage errors. 1,796 tests, 215 source files, zero silicon deism. loamSpine is G68 COMPLIANT.*
