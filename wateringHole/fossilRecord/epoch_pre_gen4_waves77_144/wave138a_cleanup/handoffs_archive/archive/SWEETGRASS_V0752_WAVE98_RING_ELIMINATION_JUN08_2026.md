# sweetGrass v0.7.52 — Wave 98 Handoff

**Date**: 2026-06-08
**From**: strandGate (sweetGrass)
**Wave**: 98

---

## What Landed

### Ring Elimination — ecoBin Cross-Arch Clean

strandGate audit flagged `ring` in the dev-dependency tree via
`testcontainers → bollard → rustls → ring`. This blocked ecoBin
cross-arch compilation for `aarch64-linux-android` and violated Tower
Atomic security posture (all crypto routes through bearDog).

**Removed:**
- `testcontainers` (workspace + `sweet-grass-store-postgres` dev-dep)
- `testcontainers-modules` (workspace + crate dev-dep)
- `postgres_test_url_for_port()` helper (dead code after removal)
- 3 `deny.toml` advisory ignores (`RUSTSEC-2025-{0111,0134,0141}`)
- `deny.toml` ring/rustls wrapper exceptions (bollard, hyper-rustls, etc.)
- `deny.toml` skip-tree entries for testcontainers

**Replaced with:**
- External `DATABASE_URL` env var connection pattern for Postgres
  integration tests (standard CI approach)
- Tests remain behind `#[cfg(feature = "integration-tests")]`

**Verification:**
```
$ cargo tree -i ring
error: package ID specification `ring` did not match any packages
```

Zero C/ASM crypto in entire dep tree (dev + production).
720 lines removed from `Cargo.lock`.

### `deny.toml` Hardened

ring and rustls are now fully denied with **zero wrappers** — any future
dep that tries to pull them will be caught immediately:

```toml
{ name = "ring", wrappers = [], reason = "C/ASM crypto backend" }
{ name = "rustls", wrappers = [], reason = "depends on ring (C/ASM)" }
```

## Metrics

| Metric | Value |
|--------|-------|
| Version | v0.7.52 |
| Tests | 1,613+ |
| Coverage | 91.7% |
| Clippy | Zero warnings (pedantic + nursery) |
| ring | **ABSENT** from dep tree |
| ecoBin cross-arch | Unblocked |

## Status

sweetGrass action item from Wave 98 blurbs: **RESOLVED**.
Ready for `sourdough validate ecobin` and VPS binary refresh.
