# barraCuda Wave 150t — Root Doc Refresh & Debris Review

**Date**: Jul 21, 2026
**Gate**: eastGate
**Wave**: 150t
**Primal**: barraCuda
**Commit**: (pending)

---

## Summary

Root documentation refreshed with ground-truth metrics. Debris scan clean.
12 files updated. Zero code changes — docs only.

## Metrics Reconciliation

| Metric | Old (docs) | New (verified) | Method |
|--------|-----------|----------------|--------|
| Total test attrs | 5,153 | **5,035** | `rg '#[test]' + '#[tokio::test]'` |
| barracuda-core tests | 760 | **759** | per-crate count |
| barracuda tests | 4,377 | **4,260** | per-crate count |
| naga-exec tests | 16 | **16** | unchanged |
| WGSL shaders | 860 (most), 826 (2 files) | **860** all files | `find *.wgsl` |
| Rust source files | 1,211 | **1,211** | unchanged |
| Integration test files | 42 | **48** | `find tests/*.rs` |
| IPC methods | 98 | **98** | unchanged |
| tarpc endpoints | 15 | **15** | unchanged |

## Files Updated (12)

1. `README.md` — test count, integration files
2. `CONTEXT.md` — test count, per-crate split
3. `STATUS.md` — test count, per-crate split, header date
4. `CONTRIBUTING.md` — shader count, integration files
5. `CONVENTIONS.md` — max file size 1000→800 (align with standard)
6. `PURE_RUST_EVOLUTION.md` — test count, per-crate split
7. `SOVEREIGN_PIPELINE_TRACKER.md` — shader count, header date
8. `specs/BARRACUDA_SPECIFICATION.md` — stale test count in superseded banner
9. `specs/REMAINING_WORK.md` — HISTORICAL banner, broken link fix, shader/file counts
10. `specs/ARCHITECTURE_DEMARCATION.md` — shader count
11. `sporeprint/validation-summary.md` — test count, frontmatter date
12. `.cursor/rules/barraCuda.md` — 4 invented IPC methods corrected

## Debris Scan Results

| Category | Result |
|----------|--------|
| Empty directories | **0** — clean |
| Stale scripts | **0** — `scripts/test-tiered.sh` is active |
| .bak/.old/.tmp files | **0** |
| TODO/FIXME in Rust code | **0** |
| Orphan modules | **0** — `pipeline/mod.rs` healthy |
| `showcase/` | Already removed (Wave 49) |

## Archive Candidates (Not Moved — Cross-Referenced)

- `specs/REMAINING_WORK.md` (1,986 lines) — marked HISTORICAL, still referenced by 5 docs
- `specs/BARRACUDA_SPECIFICATION.md` — already marked SUPERSEDED (Wave 142b)

## For Upstream Review

- `.cursor/rules/barraCuda.md` had 4 invented IPC methods — fixed to match `REGISTERED_METHODS`
- `STATUS.md` internal contradiction: claims ironGate mesh operational while listing
  "toadStool not enrolled on ironGate" as P1 — left for operator review
- `CONVENTIONS.md` max file size was 1000, corrected to 800 (matches README/STATUS standard)
