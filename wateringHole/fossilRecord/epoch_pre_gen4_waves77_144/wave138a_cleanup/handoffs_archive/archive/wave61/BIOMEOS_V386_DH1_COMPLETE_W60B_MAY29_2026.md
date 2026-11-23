# biomeOS v3.86 — DH-1 Complete + Test Extraction (Wave 60b)

**Date**: May 29, 2026
**From**: biomeOS team
**To**: primalSpring coordination
**Wave**: 60b (PostPrimordial → Glacial Shift)

---

## Summary

Completed DH-1 elimination of all `env::temp_dir()` production sites (12 call sites),
extracted 3 large inline test modules, and fixed the last hardcoded primal name.
biomeOS now has **zero `/tmp` writes** in production code (documented exception:
`biomeos-boot` FHS-standard tmpfs mount at PID 1).

---

## Changes

### DH-1b: `env::temp_dir()` → proper runtime paths (12 sites)

| File | Old | New |
|------|-----|-----|
| `biomeos-types/paths.rs` (3 sites) | `env::temp_dir().join("biomeos-$USER")` | `/run/biomeos-$USER` |
| `biomeos-api/beacon_verification.rs` | `env::temp_dir().join(basename)` | `FALLBACK_RUNTIME_BASE/basename` |
| `biomeos-core/socket_discovery/neural_api.rs` | `env::temp_dir()` | `FALLBACK_RUNTIME_BASE` |
| `biomeos-core/socket_discovery/engine.rs` | `std::env::temp_dir` | `FALLBACK_RUNTIME_BASE` |
| `biomeos-atomic-deploy/orchestrator.rs` (2 sites) | `temp_dir().join("biomeos")` | `/run/biomeos`, `/var/lib/biomeos` |
| `biomeos-genome-deploy/deployer.rs` | `temp_dir()` | `/var/lib/biomeos` |
| `neural-api-client/client.rs` | `temp_dir().join(...)` | `FALLBACK_RUNTIME_BASE/...` |
| `biomeos-deploy/biomeos-verify.rs` | `temp_dir().join(log)` | `/var/log/biomeos/...` |
| `tools/health.rs` | `temp_dir()` | `FALLBACK_RUNTIME_BASE` |

### Hardcoded primal name

- `tools/harvest/src/main.rs`: `"petaltongue"` → `primal_names::PETALTONGUE`

### Inline test extraction

| File | Before | After | Tests file |
|------|--------|-------|------------|
| `verify_lineage.rs` | 715L | 298L | `verify_lineage_tests.rs` |
| `neural-api-client-sync/lib.rs` | 781L | 341L | `lib_tests.rs` |
| `biomeos-cli main.rs` | 707L | 707L | `src/main_tests.rs` (relocated from `src/bin/`) |

### Test fix

- `test_discover_neural_api_socket_temp_dir_fallback_existing_file` →
  `test_discover_neural_api_socket_fallback_runtime_base` (uses `FALLBACK_RUNTIME_BASE` dir)

---

## DH-1 Final Status

| Category | Production sites | Status |
|----------|-----------------|--------|
| Hardcoded `/tmp` string | 0 (except boot tmpfs mount) | CLEAN |
| `env::temp_dir()` | 0 | CLEAN |
| TOML/shell `/tmp` paths | 0 | CLEAN (Wave 60) |
| Constants (`FALLBACK_RUNTIME_BASE`) | 1 definition in `constants/mod.rs` | ACCEPTABLE |

---

## Verification

- **8,058 tests**, 0 failures, 0 warnings
- `cargo check` clean
- No new dependencies

---

## Audit Checklist for primalSpring

- [ ] Verify zero `env::temp_dir()` in production `.rs` (excluding `#[cfg(test)]`)
- [ ] Verify zero hardcoded primal names outside `primal_names.rs` / tests / docs
- [ ] Verify no production `.rs` file exceeds 800 lines
- [ ] Verify extracted test modules compile and pass independently
