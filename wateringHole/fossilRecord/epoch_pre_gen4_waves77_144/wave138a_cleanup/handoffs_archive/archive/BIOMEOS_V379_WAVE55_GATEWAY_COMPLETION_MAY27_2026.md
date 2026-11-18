# biomeOS v3.79 — Wave 55 Gateway Completion

**Date**: 2026-05-27
**From**: biomeOS
**To**: primalSpring (re-audit), lithoSpore (NC-1.4 upstream), all primals
**Version**: v3.79
**Tests**: 8,038 passing (0 failures)

## Summary

Addresses the 5 gaps identified by primalSpring's Wave 55 audit of the
NUCLEUS spore gateway. All items resolved except NC-1.4 (pseudospore-core
swap) which is blocked upstream.

## Changes

### 1. Signal graph synced with primalSpring conventions

**File**: `graphs/signals/nest_ingest_spore.toml`

- `dag_session` and `ledger_entry` set to `required = false` — graceful
  degradation when provenance trio unavailable (matches primalSpring
  `nest_atomic` fragment pattern).
- Added `[graph.bonding_policy]` block: `bond_type = "Ionic"`,
  `trust_model = "MethodGate"` (required for `btsp_enforced` security model).
- Added `pseudospore_version = "2.0"` and `era = "stadial"` to metadata.
- `store_content` capabilities extended with `storage.store`.
- `attribution_braid` `by_capability` changed `"commit"` → `"attribution"`.

### 2. Content path passed to NestGate

**File**: `crates/biomeos/src/modes/nucleus_ingest.rs`

- `Envelope` struct gains `pseudospore_dir: PathBuf`.
- `to_params()` includes `"source_dir"` — NestGate can now access artifact
  files during signal execution.
- `config/signal_tools.toml` updated with `source_dir` parameter.

### 3. Emit pipeline completed (NC-1.2)

**Files**: `graphs/signals/nest_emit_spore.toml` (new),
`crates/biomeos-atomic-deploy/src/neural_api_server/routing.rs`,
`config/signal_tools.toml`

- New signal graph: `nest.emit_spore` (3-node: retrieve_content →
  resolve_braid → sign_emission).
- `NucleusEmitSpore` route changed from direct `capability.call` to
  `signal.dispatch` with the new graph (mirrors ingest pattern).
- CLI `run_emit()` now dispatches via `signal.dispatch`.
- Signal graph count: 19 (up from 18).

### 4. Receipt shape aligned

**File**: `crates/biomeos/src/modes/nucleus_ingest.rs`

- `write_receipt()` now uses `extract_receipt_field()` with multi-path
  fallback: `/receipt/{field}` → `/execution/nodes/{node}/result/{field}`
  → `"pending"`.
- Receipt records `execution_id` from signal dispatch response.
- Aligned with actual response envelope from `signal.dispatch`:
  `{ signal, graph_id, execution: { execution_id, graph_id, started_at } }`.

### 5. NC-1.4 blocker — RESOLVED

**Status**: ~~BLOCKED UPSTREAM~~ **RESOLVED**

`pseudospore-core` now exists as a standalone crate at
`gardens/lithoSpore/crates/pseudospore-core/` (10 modules, `SporeError` typed
errors, `PseudoSporeEnvelope::load()` + `validate()` API). The legacy
`litho-core/src/pseudospore.rs` re-export wrapper has been retired (deleted).

biomeOS v3.81 created `biomeos-pseudospore` with compatible types. Future
evolution: swap to `pseudospore-core` directly as a workspace dep.

## Files Changed

| File | Change |
|------|--------|
| `graphs/signals/nest_ingest_spore.toml` | Sync with primalSpring conventions |
| `graphs/signals/nest_emit_spore.toml` | **New** — emit signal graph |
| `crates/biomeos/src/modes/nucleus_ingest.rs` | Envelope.pseudospore_dir, receipt shape, NC-1.4 docs |
| `crates/biomeos-atomic-deploy/src/neural_api_server/routing.rs` | Emit route → signal.dispatch |
| `crates/biomeos-atomic-deploy/tests/signal_dispatch_tests.rs` | 18→19 count |
| `config/signal_tools.toml` | source_dir param, nest.emit_spore tool |
| `CHANGELOG.md` | v3.79 entry |
| `CURRENT_STATUS.md` | Version bump, test count |

## For primalSpring Re-audit

1. Signal graph conventions — verify alignment with your `nest_atomic` fragment.
2. NC-1.4 — lithoSpore needs to extract `pseudospore-core` or biomeOS needs
   authorization to depend on `litho-core` directly.
3. Emit pipeline — verify `nest.emit_spore` graph meets your specification
   for `sweetGrass braid.resolve` and `BearDog crypto.sign` composition.
4. Receipt polling — `execution_id` is now recorded; async graph execution
   means node-level results require a status poll.
