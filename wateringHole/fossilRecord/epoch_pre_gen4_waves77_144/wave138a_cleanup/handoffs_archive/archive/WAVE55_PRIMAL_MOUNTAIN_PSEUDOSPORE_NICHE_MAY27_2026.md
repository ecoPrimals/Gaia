# Wave 55: Primal Mountain — pseudoSpore 2.0 Niche Climate Evolution

**Date:** 2026-05-27
**From:** primalSpring (coordination)
**To:** All primal teams
**Priority:** Pre-stadial — must be absorbed before stadial gate evaluation

---

## Context

13/13 primals are CLEAN. Zero upstream code debt. The mountain is clear.

What remains is **niche climate**: the deployment topology, spore gateway, and
cross-gate mesh must warm before stadial entry. This handoff defines what each
primal team delivers so that primalSpring can evolve the patterns postPrimordial.

**Full spec:** `springs/primalSpring/specs/NICHE_CLIMATE_EVOLUTION.md` (NC-1→NC-5)
**Signal graph:** `springs/primalSpring/graphs/signals/nest_ingest_spore.toml`
**Validation matrix:** `springs/primalSpring/specs/NUCLEUS_VALIDATION_MATRIX.md` (columns U/V/W)
**Capability registry:** `nucleus.ingest_spore` + `nucleus.emit_spore` registered (460 methods)

---

## biomeOS — CRITICAL BLOCKER (NC-1.1, NC-1.2)

**You own the gateway.** hotSpring's `nest-validate guidestone deploy` step 7
already calls `biomeos nucleus ingest` and falls through to the transitional
`litho ingest-pseudospore` path because the subcommand doesn't exist yet.

### What to deliver

1. **`biomeos nucleus ingest <pseudospore-dir>` subcommand**
   Wire to clap parser in `biomeos-cli`. Handler should:
   - Validate pseudoSpore envelope (liveSpore.json schema, BLAKE3 data manifest)
   - Store via NestGate `storage.store` / `content.put`
   - Create DAG session via rhizoCrypt `dag.session.create`
   - Append ledger entry via loamSpine `entry.append`
   - Create attribution braid via sweetGrass `braid.create`
   - Sign receipt via BearDog `crypto.sign`
   - Write `receipts/nucleus_ingest.toml` with all trio IDs
   - **Use `pseudospore-core` crate** from lithoSpore for envelope parsing

2. **`biomeos nucleus emit <spore-id>` subcommand**
   Reverse of ingest: retrieve from NestGate, package envelope, sign braid.

3. **Neural API methods** (already registered in primalSpring capability_registry):
   - `nucleus.ingest_spore` — JSON-RPC entry point for programmatic ingest
   - `nucleus.emit_spore` — JSON-RPC entry point for programmatic emit

### Why this is critical

Without these subcommands:
- hotSpring pseudoSpore v1.6.1 cannot be ingested via NUCLEUS (Era 3)
- No spring can achieve postPrimordial spore emission
- NUCLEUS_VALIDATION_MATRIX column U is blocked for all springs
- primalSpring exp115 live phases cannot activate
- Stadial entry gate for spore universality cannot be evaluated

### Signal graph reference

The 6-step ingest flow is encoded in `graphs/signals/nest_ingest_spore.toml`:
```
validate_envelope (NestGate) → store (NestGate) → dag_session (rhizoCrypt)
  → ledger_entry (loamSpine) → braid (sweetGrass) → sign_receipt (BearDog)
```

This composes existing primal capabilities. No new capabilities needed from
any primal — only the biomeOS CLI orchestrator that sequences them.

### plasmidBin deployment

biomeOS deploys via plasmidBin. The new subcommands should land in a normal
biomeOS release cycle. When primalSpring's `s_nest_atomic` Phase 4 detects
`nucleus_ingest.rs`, the structural gate clears automatically. When the
subcommands work against live Nest Atomic, exp115 Phases 4-5 light up.

---

## lithoSpore — Wire pseudospore-core (NC-1.3)

**Status: COMPLETE (May 27, 2026)**

**`pseudospore-core` is wired.** Consumers: `ltee-cli`, `litho-core`.

1. ~~Add `pseudospore-core` as dependency of `ltee-cli` (`Cargo.toml`)~~ ✓
2. ~~Replace `litho-core::pseudospore` calls with `pseudospore-core` equivalents~~ ✓
3. ~~Deprecate `litho-core/src/pseudospore.rs` (parallel implementation)~~ ✓
4. ~~Verify `litho emit-pseudospore` still produces identical output~~ ✓
5. ~~Verify `litho audit` still validates correctly~~ ✓

This unblocks biomeOS from depending on the same crate for its gateway handler,
giving us one canonical envelope implementation across the ecosystem.

**Doc drift note (RESOLVED):** `SPORE_OWNERSHIP_MATRIX.md` lists `receipts.rs` and
`braid_envelope.rs` as pseudospore-core modules — both modules now exist in
`pseudospore-core`.

**Post-NC-1.3 additions (May 27, 2026):**
- `envelope.rs` added — `PseudoSporeEnvelope::load()` + `validate()` consumer API
  for biomeOS `nucleus_ingest.rs` to call instead of inline validation.
  `pseudospore-core` now has 10 `pub mod` entries (9 API + `error`).
- **Second-spring emission validated** — `litho emit-pseudospore --spring groundSpring`
  produces identical envelope structure to hotSpring (column W). Hardcoded
  `urn:hotspring` URNs in `manifest.rs` replaced with spring-agnostic
  `urn:{spring_lower}` derivation.
- `ingest-pseudospore` CLI help updated: "Prefer `biomeos nucleus ingest` when
  NUCLEUS is available. This command is the offline/airgapped fallback path."

**Deep debt evolution (May 27, 2026):**
- `SporeError` typed error hierarchy (thiserror) replaces `Result<_, String>` in pseudospore-core
- `harness::format_output()` + `exit_code()` — library no longer calls `process::exit`
- Tier-0 structural checks in 5/7 LTEE modules
- `ureq` explicitly rustls (pure-Rust TLS, ecoBin compliant)
- All hardcoded paths evolved: `LITHO_SPRINGS_ROOT`, `LITHO_LIBVIRT_IMAGES`, `LITHO_RUST_TARGET`
- `registry::load_modules()` reads scope.toml first, compiled LTEE_MODULES as fallback
- `LITHOSPORE_VERSION` uses `env!("CARGO_PKG_VERSION")` — zero version drift
- 191 tests (dead code retired), 0 clippy warnings, 0 unsafe, all files ≤800 LOC
- 7/7 Tier 0 structural checks, `litho parity` in CI
- `emit-pseudospore --from-dir` for nest-validate delegation

---

## BearDog — No action (supporting role)

BearDog provides `crypto.sign` for the receipt signing step (step 6 of the
ingest signal). This capability already exists and is exercised in 14,784+ tests.
No new work required. BearDog's ACME renewal daemon (Wave 112) and 127 methods
are sufficient for the spore gateway.

---

## Songbird — Mesh stability for multi-gate (NC-2)

Songbird's federation (`discovery.peers`, `mesh.init`) is the backbone of
cross-gate NUCLEUS. Current state:

- eastGate ↔ ironGate: **stable**
- southGate: **intermittent Songbird crashes** (7/13 health-responding)

### What to investigate

1. Songbird crash on southGate — is this a cold-start race? Memory pressure?
2. Bidirectional mesh seeding reliability — `mesh.init` must survive restarts
3. When stable: coordinate live `s_covalent_mesh` run across 3+ gates

No code changes expected — Songbird is deep-debt-zero (8,070+ tests, `forbid(unsafe_code)`).
This is operational stabilization.

---

## NestGate — Spore storage backend (supporting role)

NestGate provides `storage.store`, `storage.retrieve`, `storage.exists`,
`content.put` for the spore gateway. These capabilities exist (12,393+ tests).
No new work required for NC-1. NestGate is the storage tier that biomeOS's
`nucleus ingest` handler calls.

For NC-3 (cellMembrane): NestGate + provenance trio deployment on VPS
enables remote NUCLEUS spore ingest. This is an ops action, not code.

---

## Provenance Trio (rhizoCrypt, loamSpine, sweetGrass) — Supporting role

The trio provides:
- rhizoCrypt: `dag.session.create`, `dag.event.append` (DAG lineage)
- loamSpine: `entry.append`, `spine.get` (permanent ledger)
- sweetGrass: `braid.create`, `braid.commit` (semantic attribution)

All capabilities exist and are tested. No code changes required.
The trio signs ingestion events when biomeOS's handler calls them in sequence.

---

## ToadStool — No action for NC-1

ToadStool's compute capabilities are not part of the spore ingest flow.
Sovereign dispatch factory (stadial compute) is a separate stadial item.
9,156+ lib tests, zero production panic paths, 88 methods.

---

## BarraCuda / CoralReef / SkunkBat / Squirrel / PetalTongue — No action for NC-1

These primals are not involved in the spore ingest signal. All are CLEAN.

---

## Per-Gate Team Handoffs (NC-2, NC-4)

| Gate | Team | Action |
|------|------|--------|
| **southGate** | wetSpring / neuralSpring | Stabilize 13/13 health; investigate Songbird crashes + biomeOS socket; then coordinate live `s_covalent_mesh` with primalSpring |
| **ironGate** | cellMembrane | Deploy NestGate + trio on VPS; coordinate `s_cross_gate_capability_call` with primalSpring; K-Derm boundary publication |
| **biomeGate** | hotSpring | Elevate from 9→13 primals if hardware permits; first pseudoSpore 2.0 ingest via NUCLEUS once biomeOS gateway lands |
| **eastGate** | primalSpring | Already operational; orchestration hub; will run live validation when gates are ready |

---

## Timeline

| Phase | When | What |
|-------|------|------|
| **Now** | Wave 55 | biomeOS lands `nucleus ingest/emit`; lithoSpore wires `pseudospore-core` (**COMPLETE**) |
| **Next** | Wave 56 | hotSpring v1.6.1 first NUCLEUS ingest (column U); southGate stabilization |
| **Then** | Wave 57 | groundSpring second ingest (column U × 2); live `s_covalent_mesh` across 3+ gates |
| **Gate** | Wave 58+ | Stadial entry evaluation: spore universality + mesh topology + spring depth |

---

## How primalSpring validates

When you deliver, primalSpring's existing infrastructure validates automatically:

- `s_nest_atomic` Phase 4 detects `nucleus_ingest.rs` → structural gate clears
- `exp115` Phases 4-5 probe live NUCLEUS → live gate clears
- `s_atomic_signals` validates `nest_ingest_spore` signal → already passing
- `primalspring registry --check all` detects new `nucleus.ingest_spore` + `nucleus.emit_spore` methods
- NUCLEUS_VALIDATION_MATRIX columns U/V/W track per-spring readiness
