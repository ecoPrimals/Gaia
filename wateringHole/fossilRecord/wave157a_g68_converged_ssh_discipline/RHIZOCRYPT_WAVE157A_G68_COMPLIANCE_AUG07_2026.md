# rhizoCrypt — G68 Platform Substrate Compliance + Transport Refactor

**Date**: Aug 7, 2026  
**Wave**: 157a  
**Primal**: rhizoCrypt v0.14.17  
**Spec**: G68 Platform Substrate Abstraction  
**Status**: COMPLIANT — all three layers clean

---

## G68 Audit Results

rhizoCrypt passes the G68 litmus test: "Does this primal do *less* on Windows,
or the *same thing differently*?" — It does the same thing differently.

| Layer | Finding | Status |
|-------|---------|--------|
| **L1: Links** | `uds/symlinks.rs` — capability domain discovery symlinks. Already `#[cfg(unix)]` gated. Intrinsically UDS-tied: on non-Unix, G66 transport abstraction uses TCP, discovery uses registry. | **CLEAN** |
| **L2: Permissions** | `PermissionsExt` + `set_permissions` in `store_redb_tests_error_paths.rs` only. `#[cfg(unix)]` gated test function. Zero production usage. | **CLEAN** |
| **L3: Device backends** | `nix::` used only in test lifecycle (`SIGTERM`/`SIGINT` signal kill). Zero `rustix`, `libc::`, `mmap`, `ioctl`, `VFIO`, `DRM`. | **CLEAN** |

### Zero Violations

- Zero unconditional Unix imports outside transport layer
- Zero `TODO`/`FIXME`/`HACK`/`DEBT` markers
- Zero `unwrap()` in production (policy enforced)
- Zero ungated mocks

---

## Transport Module Refactor

Split 697-line `transport.rs` monolith into `transport/` module directory:

| File | Lines | Domain |
|------|-------|--------|
| `transport/mod.rs` | 195 | Socket paths, BTSP config, re-exports |
| `transport/endpoint.rs` | 197 | `TransportEndpoint` enum + impls |
| `transport/connect.rs` | 148 | `connect_transport` + JSON-RPC helpers |
| `transport/listener.rs` | 95 | `TransportListener` server abstraction |
| `transport/stream.rs` | 90 | `TransportStream` + AsyncRead/AsyncWrite |

All files well under 200 lines. Max production file: 639 lines (`service.rs`).

---

## Verification

```
cargo clippy --workspace --all-features -- -D warnings   → 0 warnings
cargo test --workspace --all-features                     → 1,825 passed, 0 failed
cargo check --target x86_64-pc-windows-gnu                → pass
cargo fmt --check                                         → clean
```

---

## Metrics

| Metric | Value |
|--------|-------|
| Tests | 1,825 |
| Source files | 222 `.rs` |
| Lines | ~61,300 |
| Max production file | 639 lines |
| Windows cross-compile | Pass |
| G68 violations | 0 |
| Debt markers | 0 |
