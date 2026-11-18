<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->

# lithoSpore — Deep Debt Evolution Pass

**Date**: Jul 17, 2026 14:40 EDT | **Wave**: 147e | **From**: pseudoSpore/lithoSpore on ironGate

---

## Summary

Comprehensive evolution pass addressing hardcoding, tracing, ecoBin purity,
and proactive file size management. **222 tests**, 0 clippy, 0 debt markers,
0 unsafe, 0 unwrap in production code.

---

## What Changed

### 1. Named Constants (`litho_core::consts`)

Extracted 40+ scattered magic numbers into named, documented constants:

| Category | Constants | Files touched |
|----------|-----------|---------------|
| IPC timeouts | `IPC_READ_TIMEOUT`, `IPC_WRITE_TIMEOUT`, `IPC_CONNECT_TIMEOUT` | platform.rs, discovery.rs |
| Network probes | `UPSTREAM_PROBE_TIMEOUT`, `CONNECTIVITY_PROBE_TIMEOUT` | verify.rs |
| I/O buffers | `HASH_BUFFER_SIZE` (65536) | verify.rs |
| VM specs | `VM_DISK_SIZE`, `VM_RAM_MB`, `VM_VCPU_COUNT`, `VM_OS_VARIANT`, `VM_CLOUD_IMAGE_URL` | grow/deploy.rs |
| VM polling | `VM_BOOT_POLL_ATTEMPTS`, `VM_BOOT_POLL_INTERVAL` | grow/deploy.rs |
| Discovery | `DEFAULT_PRIMAL_HOST`, `RUNTIME_SUBDIR`, `DISCOVERY_SOCKET_NAME` | discovery.rs |
| Science | `DEFAULT_RMSD_KJ` | promote/report.rs |

3 new tests: positive timeouts, power-of-two buffer, read > write ordering.

### 2. Tracing Migration (litho-core)

Migrated all 5 `println!`/`eprintln!` calls in litho-core to structured `tracing`:
- `braid.rs`: `tracing::warn!` for parse/read errors
- `harness.rs`: `tracing::info!` for tier 0 structural results, `tracing::debug!` for Python baseline output

Added `tracing = "0.1"` as workspace dependency.

### 3. Feature-Gated `ureq`/`ring`

Network fetch is now behind `fetch` feature (default = on):
- `cargo build -p ltee-cli --no-default-features` produces a **ring-free ecoBin** with zero C/asm deps
- `fetch`, `fetch-pseudospore`, and `refresh` gracefully degrade with error messages when feature is disabled
- No impact on default builds — feature is on by default

### 4. File Refactoring

| File | Before | After | Method |
|------|--------|-------|--------|
| `main.rs` | 689 | 344 | Commands enum → `commands.rs` (377) |
| `baselines.rs` | 688 | 0 | Split into 7 per-tool modules under `viz/baselines/` (95–140 each) |

No files over 500 lines in the CLI crate after refactoring.

---

## Quality Gate

```
cargo test:                   222 pass, 0 fail
cargo clippy --pedantic:      0 warnings (allowed only)
cargo fmt --check:            clean
cargo doc --no-deps:          0 warnings
cargo build --no-default-features: builds (no ring)
unsafe:                       #![forbid(unsafe_code)] workspace-wide
unwrap/expect in prod:        0
debt markers:                 0
mocks in production:          0
```

---

## Audit Summary (post-evolution)

| Dimension | Status |
|-----------|--------|
| Files >800L | **0** (max: 585 audit/domain.rs) |
| Debt markers | **0** |
| Mocks in production | **0** |
| unsafe | **0** (forbidden) |
| unwrap/expect in prod | **0** |
| Hardcoded magic numbers | **Extracted** to litho_core::consts |
| C/asm runtime deps | **ring only** (feature-gated, documented) |
| tracing in core lib | **Done** (5/5 migrated) |

---

## Next Steps

1. USB round-trip validation — primalSpring scenario
2. CLI println! → tracing migration (729 calls in ltee-cli — sets pattern, not blocking)
3. Upstream: no blocking needs from lithoSpore on any primal team
