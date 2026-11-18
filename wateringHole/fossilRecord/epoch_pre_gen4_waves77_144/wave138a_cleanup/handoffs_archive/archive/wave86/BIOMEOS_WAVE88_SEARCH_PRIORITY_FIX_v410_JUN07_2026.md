# biomeOS Wave 88 — Binary Search Priority Fix (v4.10)

**Date**: June 7, 2026
**Gate**: southGate (ironGate)
**Cascade**: primalSpring → eastGate → southGate (Wave 88)
**Severity**: BIO-SEARCH-01 (P2) + BIO-DEPLOY-02 (P3) RESOLVED

---

## BIO-SEARCH-01: Depot-First Binary Discovery (P2 → RESOLVED)

### Root Cause

`discover_binaries_with()` built its search path array with `livespore-usb` entries
at indices 0-1 and `ECOPRIMALS_PLASMID_BIN` (depot) at indices 4-5. The first-match
algorithm meant 5/12 primals resolved from stale `livespore-usb` binaries instead
of the current depot build.

Critical impact: songbird resolved the pre-v4.09 binary (without federation env
passthrough), so even though `nucleus_launch_profiles.toml` was fixed, the old
binary didn't read `SONGBIRD_FEDERATION_PORT`.

### Fix

Reordered search paths:

```
1. ECOPRIMALS_PLASMID_BIN/primals     (depot — highest priority when set)
2. ECOPRIMALS_PLASMID_BIN             (depot root)
3. plasmidBin                         (local relative)
4. plasmidBin/optimized/{arch}        (local optimized)
5. ../../plasmidBin/primals           (relative traversal)
6. ../../plasmidBin                   (relative traversal)
7. livespore-usb/{arch}/primals       (USB fallback)
8. livespore-usb/primals              (USB fallback)
9. $PATH                             (system fallback)
```

`target/release` **removed entirely** — production deployments should never
resolve from build artifacts (BIO-DEPLOY-02).

---

## BIO-DEPLOY-02: target/release Removed (P3 → RESOLVED)

`deployment.rs` doc comment referenced `target/release` in search order but
the code only uses `which::which()` (`$PATH`). Doc corrected. No code change
needed — the stale path was only in `discover_binaries_with()`.

---

## Test Updates

| Test | Change |
|------|--------|
| `test_discover_depot_takes_priority_over_livespore_usb` | **NEW** — creates binaries in both depot and livespore-usb, asserts depot wins |
| `test_discover_binaries_with_plasmidbin_relative` | Renamed from target_release variant, uses plasmidBin |
| `test_discover_binaries_with_cwd_finds_in_plasmidbin` | Renamed from target_release variant, uses plasmidBin |

## Validation

- **496 tests passed** (biomeos-unibin), 0 failures
- `cargo clippy --workspace --lib` — zero warnings
- `cargo check` — clean

---

## Impact on Critical Path

With v4.09 (federation env passthrough) + v4.10 (depot-first search), the mesh
proof path is fully unblocked:

1. ~~BIO-SEARCH-01~~ **DONE** — depot binaries take priority
2. ~~songbird federation profile~~ **DONE** (v4.09)
3. **eastGate operator**: rebuild v4.10, run `plasmid.trigger`, start NUCLEUS
4. **strandGate**: already mesh-ready, waiting on eastGate federation

---

## Files Changed

| File | Change |
|------|--------|
| `crates/biomeos/src/modes/nucleus_procs.rs` | Reordered search paths: depot first, livespore-usb last, target/release removed |
| `crates/biomeos/src/modes/nucleus_tests2.rs` | 2 tests updated + 1 new depot priority test |
| `crates/biomeos-niche/src/deployment.rs` | Doc comment corrected |
| `CHANGELOG.md` | v4.10 entry |
| `CURRENT_STATUS.md` | Updated to v4.10 |
| `START_HERE.md` | Updated to v4.10 |
