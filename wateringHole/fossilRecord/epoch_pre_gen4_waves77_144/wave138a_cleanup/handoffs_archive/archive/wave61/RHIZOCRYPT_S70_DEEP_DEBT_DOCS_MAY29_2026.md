# rhizoCrypt — S70 Deep Debt + Root Docs Cleanup (May 29, 2026)

**Primal**: rhizoCrypt v0.14.0
**Wave**: Post-Wave 60 deep debt + documentation reconciliation
**Status**: Stadial-current, zero debt

---

## Structural Refactoring (Deep Debt S70)

### Files >700L → All production files under 700 lines

| File | Before | After | Method |
|------|--------|-------|--------|
| `rhizocrypt/mod.rs` | 858 | 676 | Extracted `branch_ops.rs` (Wave 60 branch/diff/merge/federate ops) |
| `niche.rs` | 800 | 435 | Extracted `niche_derived.rs` (PROVENANCE_ALIASES, derived accessors, response builders, MCP tools) |
| `handler_tests.rs` | 1,731 | 1,419 | Extracted `handler_tests_branching.rs` (Wave 60 tests) |

### Naming Decoupling

- `BearDogVerifier` → `PresenceVerifier` — method gate security path no longer contains a primal name; named for its behavior (presence-only check) rather than a specific provider

### Hardcoding Fixes

- biomeOS path construction: `/tmp/biomeos` hardcoded string → `constants::BIOMEOS_SOCKET_SUBDIR` centralized
- `register_with_discovery()`: Added missing `connect()` before `register()` + `RegistrationResult.success` check — registration was silently failing

### Pre-existing Fixes

- Stale songbird scaffolded registration tests: asserted `success: true` when implementation returns `success: false` without `live-clients` feature
- Restored `serde` `rc` feature: required by `Did(Arc<str>)` serialization

---

## Documentation Reconciliation

### Metrics Corrected

| Metric | Was (wrong) | Now (verified) |
|--------|-------------|----------------|
| METHOD_CATALOG entries | 37 | **36** (actual count in code + registry) |
| tarpc ops (README) | 24 | **28** (actual count in service.rs trait) |
| Stable methods | 32 | **31** stable + **5** evolving |
| `.rs` files | 172 | **175** (3 new extraction files) |
| Lines | ~54,251 | **~54,294** |
| Max prod file size | 800 / 1000 (inconsistent) | **700** (unified) |

### Dates Synchronized

- `DEPLOYMENT_CHECKLIST.md` header: May 25 → May 29
- `DEPLOYMENT_CHECKLIST.md` footer: May 17 → May 29
- `ENV_VARS.md`: April 27 → May 29

### Debris Cleaned

- Stale `showcase/` `.gitignore` rules removed (showcase fossilized in Wave 49)
- `cargo clean`: 28.6 GiB reclaimed

---

## Current Stadial Gate

| Metric | Value |
|--------|-------|
| Tests | 1,654 passing (`--all-features`) |
| `.rs` files | 175 |
| Lines | ~54,294 |
| Methods | 36 (31 stable, 5 evolving) |
| tarpc ops | 28 |
| Clippy | 0 warnings |
| unsafe | 0 blocks |
| TODO/FIXME/HACK | 0 markers |
| Max prod file | 676 lines (limit: 700) |
| Version | 0.14.0 |

---

## Audit Status

- **Zero debt markers** (TODO/FIXME/HACK/XXX)
- **Zero temp/backup/debris files**
- **Zero orphan scripts**
- **Zero stale version strings** (0.14.0-dev fully purged)
- **All docs metrics aligned** with code reality
- **showcase/** fossilized with tombstone README
- **No action required** for downstream primals
