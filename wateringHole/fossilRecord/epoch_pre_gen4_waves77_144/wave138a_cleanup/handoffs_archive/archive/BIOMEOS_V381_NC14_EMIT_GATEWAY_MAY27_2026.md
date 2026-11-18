# biomeOS v3.81 — NC-1.4 + NC-1.emit Gateway Completion

**Date:** May 27, 2026
**From:** biomeOS
**To:** primalSpring (re-audit), lithoSpore (NC-5 unblocked), all primals

---

## Summary

Closed the two remaining NUCLEUS spore gateway gaps identified in
primalSpring Wave 56 Mountain Blurb:

- **NC-1.4 (HIGH → RESOLVED):** Replaced inline validation stub with
  canonical pseudoSpore 2.0 validation via new `biomeos-pseudospore` crate
- **NC-1.emit (MEDIUM → RESOLVED):** Full emit materialization pipeline —
  produces a complete pseudoSpore 2.0 directory, not just `emit_manifest.json`

## NC-1.4: Canonical Validation

### What changed

- Created `crates/biomeos-pseudospore/` (26th workspace crate) with types
  and validation functions compatible with `pseudospore-core` (lithoSpore's canonical API)
- Types: `PseudoSporeManifest`, `PseudoSporeScope`, `ArtifactIdentity`,
  `ValidationDoc`, `ChecksumEntry`, `SporeStatus`, etc.
- Functions: `load_pseudospore()`, `verify_checksums()`, `check_completeness()`,
  `compute_checksums()`, `format_checksums()`
- Replaced `nucleus_ingest.rs:validate_envelope()` stub (was checking
  `liveSpore.json` + `[scope].id` + inline BLAKE3) with canonical API
  (`scope.toml [artifact]`, `validation.json`, `receipts/checksums.blake3`,
  `provenance/ferment_transcript.json`, `README.md`)

### Architecture decision

`pseudospore-core` standalone crate does not exist. Rather than cross-repo
path dep to `litho-core` (primal→garden), we created `biomeos-pseudospore`
within the biomeOS workspace. When lithoSpore ships `pseudospore-core`, this
becomes a thin re-export. All deps (`serde`, `toml`, `blake3`) already
workspace deps.

### NC-1.4 → NC-5 unblocking

lithoSpore `postPrimordial` pseudoSpore ingest via `biomeos nucleus ingest`
now uses the same validation standard as `litho ingest-pseudospore`. NC-5.live
is unblocked on the validation side (still gated on live Nest Atomic deploy).

## NC-1.emit: Full Materialization

### What changed

- `run_emit()` now: dispatches signal → polls execution → extracts node
  results → materializes pseudoSpore directory → writes emit receipt
- Added `poll_execution()` with exponential backoff (100ms→5s, 120s timeout)
- Added `materialize_pseudospore()` producing:
  - `scope.toml`, `validation.json`, `receipts/environment.toml`
  - `receipts/checksums.blake3` (computed via `biomeos_pseudospore`)
  - `provenance/ferment_transcript.json` (includes braid resolve data)
  - `data/content.json` (NestGate retrieve output)
  - `README.md`, `receipts/nucleus_emit.toml`
- `emit_manifest.json` retained as dispatch audit trail
- Materialized directories pass `load_pseudospore()` validation (tested)

### Signal context params wired

`signal_context.params` (e.g. `spore_id`, `family_id`) now injected into
graph executor env so node capability calls can reference `${spore_id}`.
Previously only `metrics_namespace` was extracted.

## Metrics

- **8,053 tests** (0 failures), up from 8,038
- **26 workspace crates** (new: `biomeos-pseudospore`)
- **19 signal graphs**
- 0 clippy warnings, 0 unsafe, 0 TODO/FIXME

## Files Changed

| File | Change |
|------|--------|
| `crates/biomeos-pseudospore/` (NEW) | pseudoSpore 2.0 validation crate |
| `Cargo.toml` | Added workspace member |
| `crates/biomeos/Cargo.toml` | `biomeos-pseudospore` dep, removed `blake3` |
| `crates/biomeos/src/modes/nucleus_ingest.rs` | NC-1.4 swap + NC-1.emit materialization |
| `crates/biomeos-atomic-deploy/src/handlers/graph/execute.rs` | Signal params wiring |
| Root docs | v3.81 sync |

## Remaining Gaps

| ID | Status | Notes |
|----|--------|-------|
| NC-1.4 | **RESOLVED** | biomeos-pseudospore canonical validation |
| NC-1.emit | **RESOLVED** | Full materialization pipeline |
| NC-2 | Ops | southGate mesh stability (not code) |
| NC-5.live | Gated | On live Nest Atomic deploy + gate depth |

## For primalSpring

- Verify NC-1.4 closure: `biomeos-pseudospore` API matches `litho-core` standard
- Verify NC-1.emit: materialized dir passes canonical validation
- Update `PRIMAL_GAPS.md` biomeOS section
- Update Column U for NC-1.4 resolution
