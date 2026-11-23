# barraCuda — Deep Debt Remediation & Evolution Sprint

**Date**: 2026-05-24
**Primal**: barraCuda v0.4.0
**Type**: Deep debt remediation, dependency evolution, architectural cleanup
**Commit**: `c81531e3`

---

## Summary

Full-spectrum audit and remediation of barraCuda targeting: large file
decomposition, unsafe code evolution, hardcoded primal references, external
dependency elimination, and documentation synchronization.

**Net result**: `-1,823 +747` lines. One external dependency eliminated.
Zero lint warnings. All tests pass.

---

## Changes

### 1. Smart File Decomposition (math.rs 1,046L → 3 modules)

| File | Lines | Domain |
|------|-------|--------|
| `math.rs` | 305 | element-wise math, activations, noise/RNG, ODE |
| `stats.rs` | 576 | descriptive stats, hypothesis tests, regression, ecology, special functions |
| `signal.rs` | 151 | peak detection, bandpass filtering, derivative |

Not a naive split — each module has cohesive domain responsibility, shared
imports, and semantic grouping per the IPC namespace (`stats.*`, `signal.*`,
`math.*`/`activation.*`/`noise.*`/`rng.*`/`ode.*`).

### 2. Dependency Elimination: `pollster` removed

- 4 production sites + 3 benches + 1 integration test migrated to existing
  `runtime::tokio_block_on` (handles sync, multi-thread tokio, current-thread
  tokio contexts correctly)
- `pollster` removed from workspace deps, crate deps, and dev-deps
- 7 fewer packages in lockfile

### 3. Hardcoding → Capability-Based Discovery

| Before | After |
|--------|-------|
| `BEARDOG_SOCKET` checked first | `BTSP_PROVIDER_SOCKET` checked first |
| `BEARDOG_FAMILY_SEED` in fallback chain | `BTSP_FAMILY_SEED` → `FAMILY_SEED` → `BIOMEOS_FAMILY_SEED` → `BEARDOG_FAMILY_SEED` |
| Error messages name specific primals | Error messages use generic protocol terms |

Backward compatibility preserved — legacy env vars remain in fallback chain.

### 4. Unsafe Code Evolution

- 47 `unsafe { std::env::{set,remove}_var() }` call sites in
  `btsp_socket_compliance.rs` replaced with safe `env_set()`/`env_remove()`
  wrappers documenting the SAFETY invariant (nextest process isolation)
- Only 2 `unsafe` calls remain (inside the wrappers), both with explicit
  SAFETY comments

### 5. Transport Trimming

- `transport.rs`: 825L → 799L via condensed doc comments that duplicated
  information already present in referenced standards documents

### 6. Documentation Synchronization

- `STATUS.md`: Updated method count from 72 → 87, date to May 24
- `README.md`: Updated method count from 50 → 87
- `CONTEXT.md`: Complete rewrite of method table (removed retired `doctor.*`,
  `security.*` namespaces; added `signal.*`, `nautilus.*`, `ode.*`, `auth.*`,
  `precision.*`, `validate.*`, `tolerances.*`)
- `WHATS_NEXT.md`: Added deep debt sprint to Recently Completed, fixed stale
  pollster reference
- `specs/REMAINING_WORK.md`: Updated dep audit note re: pollster elimination
- `CHANGELOG.md`: Full entry for deep debt sprint

---

## Audit Results (Clean)

| Category | Finding |
|----------|---------|
| Files >800L | 0 (was 2, both resolved) |
| Unsafe in production | 1 block in barracuda-spirv (justified, `#[expect]`) |
| Hardcoded other-primal names | 0 in production code |
| Mocks in production | 0 (only `FakeQuantize` — ML domain term) |
| TODO/FIXME markers | 0 |
| Archive debris | 0 (repo is clean) |
| External C deps | Only wgpu GPU stack (unavoidable) |

---

## For primalSpring Audit

- All 87 registered methods verified in `REGISTERED_METHODS` constant
- `primal.announce` schema and outbound push operational (Wave 43/44)
- `--socket` alias deployed (Wave 47)
- BTSP discovery uses generic env var names
- Zero production unsafe (forbid in barracuda + barracuda-core)
- `deny.toml` blocks openssl/ring/native-tls/aws-lc-sys
- Edition 2024, MSRV 1.87
