# projectFOUNDATION — Index-Driven Dispatch + Benchmark Consolidation

**Date**: 2026-05-23
**Commit**: `512395c`
**Status**: Structural debt resolved — all phases now index-driven

---

## Resolved Items

### 1. Phase 4/6 Glob→Index Migration
Phase 4 (artifact registration) and Phase 6 (target comparison) previously used
filename globs and `sed` to resolve threads. This missed ML companion manifests
when filtering by `--thread ltee`.

**Fix**: `resolve_thread_manifests()` and `resolve_thread_targets()` added to
`deploy/lib/thread_registry.sh`. Both emit absolute paths from `THREAD_INDEX.toml`,
including primary and ML companion manifests. Phase 4 and Phase 6's `all` branch
now use `list_thread_shorts` / `resolve_thread_manifests` instead of globs.

### 2. Phase 4 `find` → Predictable Paths
`register_from_manifest` used `find(1)` with accession substring matching to
locate data files. Replaced with `resolve_data_path()` which maps
`(database, accession, format)` → known filesystem paths matching
`fetch_sources.sh`'s download layout.

### 3. Fetch Double-Python Hop Eliminated
`fetch_from_manifest` emitted JSON lines, then `run_manifest_driven` piped them
through a second `python3 -c` to convert to TSV for bash `read`. Now emits TSV
directly from the TOML parse — one Python invocation per manifest.

### 4. Fetch Thread Resolution Unified
`resolve_thread_toml()` in `fetch_sources.sh` contained a 30-line inline Python
TOML parser duplicating `thread_registry.sh` logic. Replaced with a 5-line
delegation to `resolve_thread_manifests()`.

### 5. Benchmark Provenance Consolidation
`provenance_header()` was duplicated across 6 benchmark scripts (~20 lines each,
±`scipy` field). Extracted to `benchmarks/barracuda_cpu_parity/common.py` with:
- `provenance_header(caller_file=, extra_versions=)` — repo-relative command path
- `write_results()` — unified JSON serialization with numpy type handling
- `_numpy_json_default()` — handles `np.bool_`, `np.integer`, `np.floating`

Result JSONs now use `benchmarks/barracuda_cpu_parity/<script>.py` instead of
`/home/irongate/.../script.py`.

### 6. CI Gates Added
- **Benchmark result portability check**: Asserts no absolute paths in `provenance.command`
- **Thread index count reconciliation**: Validates `meta.total_threads` matches actual `[[threads]]` count, unique shorts

---

## Pipeline Metrics (Post-Commit)
| Metric | Value |
|--------|-------|
| deploy/lib/ functions | 17 (json_rpc: 7, thread_registry: 7, primal_ipc: 3) |
| Inline `python3 -c` in foundation_validate.sh | 4 (down from 6) |
| Inline `python3 -c` in fetch_sources.sh | 1 (down from 4) |
| Benchmark scripts sharing common.py | 6/6 |
| CI gates | 17 (was 14) |
| Net LOC change | -6 (303 added, 309 removed) |

## Status
- All phases of `foundation_validate.sh` are now index-driven
- All benchmark results use portable paths
- No remaining glob-based thread resolution in deploy scripts
- Phase B (Rust elevation) remains the next major milestone
