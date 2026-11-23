# biomeOS v3.77 — NUCLEUS Spore Gateway (NC-1.1, NC-1.2)

**Date:** 2026-05-27
**From:** biomeOS team
**Scope:** Wave 55 critical blocker — pseudoSpore ingest/emit gateway

---

## What landed

### 1. CLI subcommands

`Mode::Nucleus` refactored from flat args to `NucleusCommand { Start, Ingest, Emit }`:

- **`biomeos nucleus start`** — preserves existing NUCLEUS orchestrator (no behavior change)
- **`biomeos nucleus ingest <pseudospore-dir>`** — orchestrates 6-step ingest pipeline:
  1. Validate pseudoSpore envelope (`liveSpore.json` schema, `scope.toml` extraction, BLAKE3 data manifest)
  2. Dispatch `nest.ingest_spore` signal through Neural API
  3. Write `receipts/nucleus_ingest.toml` with all trio IDs (store, DAG session, ledger entry, braid, signature)
- **`biomeos nucleus emit <spore-id>`** — retrieve from NestGate, package envelope, write `emit_manifest.json`

Both support `--dry-run`, `--socket`, `--family-id` flags.

### 2. Signal graph

New `graphs/signals/nest_ingest_spore.toml` — 6-node sequential pipeline:
```
validate_envelope (NestGate) → store_content (NestGate) → dag_session (rhizoCrypt)
  → ledger_entry (loamSpine) → attribution_braid (sweetGrass) → sign_receipt (BearDog)
```

Signal tier: `nest`, signal name: `ingest_spore`.
Registered in `config/signal_tools.toml` with full parameter/return schema.
Signal graph count: 17 → 18.

### 3. Neural API routes

- `nucleus.ingest_spore` / `nucleus.ingest` → dispatches through `signal.dispatch` → `nest_ingest_spore` graph
- `nucleus.emit_spore` / `nucleus.emit` → forwards through `capability.call` to NestGate `storage.retrieve`
- Method count: 460 → 462

### 4. Envelope validation

Local BLAKE3 + `liveSpore.json` + `scope.toml` validation. Designed as a
drop-in for `pseudospore-core` (now shipped). No external dependency.

## Files changed

| File | Change |
|------|--------|
| `crates/biomeos/src/main.rs` | `Mode::Nucleus` → subcommand tree |
| `crates/biomeos/src/modes/nucleus_ingest.rs` | **NEW** — ingest/emit handlers + envelope validation + receipt writing |
| `crates/biomeos/src/modes/mod.rs` | Added `nucleus_ingest` module |
| `crates/biomeos/Cargo.toml` | Added `blake3` dependency |
| `crates/biomeos/src/main_tests.rs` | Updated nucleus CLI parser tests |
| `crates/biomeos-atomic-deploy/src/neural_api_server/routing.rs` | Added `NucleusIngestSpore` + `NucleusEmitSpore` routes |
| `crates/biomeos-atomic-deploy/tests/signal_dispatch_tests.rs` | Updated graph count 17 → 18 |
| `graphs/signals/nest_ingest_spore.toml` | **NEW** — 6-node ingest pipeline |
| `config/signal_tools.toml` | Added `nest.ingest_spore` tool definition |
| Root docs (8 files) | Version v3.76 → v3.77, tests 8,026 → 8,036 |

## Validation

- **Tests:** 8,036 (up from 8,026), 0 failures
- **Clippy:** 0 warnings
- **New tests:** 7 envelope validation + 3 CLI parser + 0 signal dispatch = 10

## What this unblocks

- hotSpring `nest-validate guidestone deploy` step 7 can now call `biomeos nucleus ingest`
  instead of falling through to transitional `litho ingest-pseudospore`
- primalSpring `s_nest_atomic` Phase 4 can detect `nucleus_ingest.rs` → structural gate clears
- `exp115` Phases 4-5 can probe live NUCLEUS
- NUCLEUS_VALIDATION_MATRIX column U unblocked for all springs

## pseudospore-core integration — RESOLVED

lithoSpore shipped `pseudospore-core` (Wave 55). biomeOS v3.81 created
`biomeos-pseudospore` with compatible types. Remaining evolution: swap to
`pseudospore-core` directly as a workspace dep for full API parity
(`PseudoSporeEnvelope::validate()`, `SporeError` typed errors).
