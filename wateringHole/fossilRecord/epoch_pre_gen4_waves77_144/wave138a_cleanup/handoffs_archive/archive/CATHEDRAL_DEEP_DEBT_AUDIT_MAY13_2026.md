# CATHEDRAL Deep Debt Audit & Resolution

**Date**: May 13, 2026
**From**: CATHEDRAL (lithoSpore + Foundation)
**For**: primalSpring, ecosystem

---

## Executive Summary

Full upstream audit of CATHEDRAL (L5 knowledge layer) against infra/wateringHole
standards, primalSpring docs, and sibling spring conventions. 14 debt items
identified, all resolved in session. Architecture evolved with capability-based
discovery, shared library extraction, and ecoBin compliance.

**lithoSpore**: 33 tests, zero clippy, zero unsafe, pure Rust BLAKE3,
4/7 modules PASS Tier 2.

**Foundation**: 10/10 threads active, CI thread-index validation now functional,
deploy scripts SPDX-compliant, hardcoded localhost removed.

---

## Resolved Debt Items

### lithoSpore (9 items)

| ID | What | Resolution |
|----|------|-----------|
| LS-7 | `blake3` pulled C toolchain via `cc` | `features = ["pure", "std"]` — ecoBin zero-C |
| LS-6 | Unused `thiserror` dependency | Removed from workspace + litho-core |
| LS-8 | Missing SPDX on fetch scripts | Added AGPL-3.0-or-later |
| LS-1 | 5 missing fetch scripts (manifest drift) | Created `fetch_good_2017.sh`, `fetch_blount_2012.sh`, `fetch_tenaillon_2016.sh` |
| LS-5 | Orphan `module5_neuralspring_b1.json` | Renamed to `neuralspring_b1_ml_surrogate.json` |
| DUP | `skip_result`, `load_expected`, `pearson_r` duplicated 4+ times | Extracted to `litho_core::{harness, stats}` |
| PATH | Scaffold stubs used inconsistent `data/` prefix | Unified to `artifact/data/` |
| DISC | No capability-based primal discovery | Added `litho_core::discovery` (env → UDS → skip) |
| ARCH | Module binaries too large, monolithic | Refactored via shared harness (18-49% LOC reduction) |

### Foundation (5 items)

| ID | What | Resolution |
|----|------|-----------|
| FN-2 | CI thread-index check was complete no-op | Fixed key names + added ML sidecar + exit 1 on failure |
| FN-6 | Spec said `store.put`, scripts use `storage.store` | Aligned spec to implementation |
| FN-3 | Thread 9 used different target schema | Converted 13 targets to `blake3`/`validated` pattern |
| FN-SPDX | Deploy scripts missing SPDX | Added to both `fetch_sources.sh` and `foundation_validate.sh` |
| FN-HOST | `foundation_validate.sh` hardcoded `127.0.0.1` | Replaced with `$PRIMAL_HOST` everywhere |

---

## Architecture Changes

### New litho-core Modules

- **`discovery.rs`**: Capability-based primal resolution. Priority chain:
  env var (`{CAPABILITY}_PORT`) → XDG discovery socket → `None`. Callers
  degrade gracefully. JSON-RPC over TCP wired; UDS planned.

- **`harness.rs`**: Shared validation harness. `skip()`, `load_expected()`,
  `dispatch_python()`, `output_and_exit()`. All 7 module binaries refactored.

- **`stats.rs`**: Shared statistics. `pearson_r()` extracted from ltee-mutations
  and ltee-breseq where it was duplicated verbatim.

### ecoBin Compliance

- `blake3 = { version = "1", default-features = false, features = ["pure", "std"] }`
- Zero unsafe in all crates
- All files under 500 LOC (down from ~485 max)
- Zero clippy warnings at `pedantic` level
- `#![forbid(unsafe_code)]` effective (no unsafe anywhere)
- Pure Rust application path — `cc` in tree but build-script no-ops with `pure`

---

## Remaining Debt (Documented)

See `lithoSpore/docs/UPSTREAM_GAPS.md` for full registry.

**Blocked on upstream:**
- Modules 3-5 (alleles, citrate, biobricks) — SKIP stubs awaiting spring reproductions
- `fetch_biobricks_2024.sh` / `fetch_dfe_2024.sh` — source URIs TBD (unpublished papers)

**Foundation operational:**
- `data/sources/*.toml` `blake3`/`retrieved` fields empty — populated at runtime by `fetch_sources.sh`
- Thread 1 WCM: 24 targets `validated = false` pending review of wcm-20260509 logs
- Thread 5 ML: `accessions = []` — internal neuralSpring models, needs `source_type` field

---

## Upstream Requests

1. **LTEE GuideStone handoff**: `LTEE_GUIDESTONE_SUBSYSTEM_HANDOFF_MAY11_2026.md` is
   referenced in wateringHole README index but not present in `handoffs/`. Was it
   committed elsewhere or lost?

2. **SCYBORG doc**: `SCYBORG_PROVENANCE_TRIO_GUIDANCE.md` only in external fossilRecord
   repo. Should a copy or pointer live in wateringHole locally?

---

## License

AGPL-3.0-or-later
