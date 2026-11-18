# hotSpring Handoff: NUCLEUS Braid Evolution — Pipeline-Derived to Provenance Trio

**Date:** 2026-05-27
**From:** hotSpring (biomeGate)
**To:** primalSpring, biomeOS, lithoSpore
**Context:** [NUCLEUS Braid Evolution](56713e5b-805e-4759-aa4a-feee796f4b22)

---

## Summary

Evolved the pseudoSpore v1.6.1 braid from pipeline-derived local validation to
NUCLEUS-ready deployment. Three major structural changes:

1. **Braid schema evolution** — provenance trio (rhizoCrypt/loamSpine/sweetGrass)
   slots wired into braid JSON, ferment transcript, and liveSpore.json envelope
2. **Deploy pipeline step 7 rewired** — two-tier ingest: `biomeos nucleus ingest`
   (postPrimordial) → `litho ingest-pseudospore` (transitional) → manual instructions
3. **nest-validate ownership boundaries** — `guidestone_emit` split into
   `emit_domain_validation()` (nest-validate owned) and `emit_envelope()` (litho-owned,
   delegated when litho CLI available)

This is pseudoSpore 2.0 prep. primalSpring handles the actual NUCLEUS elevation.

---

## What Was Done

### Phase 1: Braid Schema — Provenance Trio Slots

**Files:**
- `pseudoSpore_*/provenance/braids/compchem_guidestone_v1_6_1.json`
  - Added `provenance_trio` block: rhizocrypt, loamspine, sweetgrass — each with
    role, status (pending), contract, signed_by/at, and domain-specific IDs
  - Added `deployment_eras` array documenting the three eras
- `pseudoSpore_*/provenance/ferment_transcript.json`
  - Added `nest_atomic_readiness` section with prerequisites checklist
    and pending downstream items
- `nest-validate/src/main.rs`
  - liveSpore.json envelope now includes `provenance_trio_status` and
    `deployment_era` fields, derived from `receipts/nucleus_ingest.toml` presence

### Phase 2: Deploy Step 7 — biomeos nucleus ingest

**File:** `control/plumed_nest/nest-validate/src/main.rs`

- Added `find_biomeos_binary()` — mirrors `find_litho_binary()` pattern
  (plasmidBin → PATH → not found)
- Added `--nucleus` flag to `guidestone deploy`
- Step 7 three-tier fallback:
  1. `biomeos nucleus ingest <dir> --verify` (postPrimordial)
  2. `litho ingest-pseudospore` (transitional)
  3. Manual instructions with both commands printed
- `write_nucleus_ingest_receipt()` writes `receipts/nucleus_ingest.toml`
  on successful biomeos ingest (timestamp, binary, gate, status)

### Phase 3: Ownership Boundary Cleanup

**File:** `control/plumed_nest/nest-validate/src/main.rs`

Per `SPORE_OWNERSHIP_MATRIX.md`, split `guidestone_emit` into:

| Function | Owner | Responsibility |
|----------|-------|---------------|
| `emit_domain_validation()` | nest-validate (hotSpring) | PDB resolution, scope cross-check, validation.json |
| `emit_envelope()` | litho CLI (lithoSpore) | liveSpore.json, receipts/environment.toml, checksums.blake3 |
| `guidestone_emit()` | orchestrator | calls domain validation then envelope |

`emit_envelope()` attempts delegation to `litho emit-pseudospore` when litho
CLI is available; falls back to local generation (identical schema).

### Phase 4: DEPLOY.md PostPrimordial Path

- Added section "5. NUCLEUS Nest Deployment (postPrimordial)" with full
  biomeos nucleus ingest flow, provenance trio signing contract table,
  prerequisites, and current status
- Updated Wire Format Compatibility (biomeos nucleus ingest row added)
- Rewrote Data Provenance as three-era timeline

### Phase 5: Scope + README + Full Deploy

- `scope.toml` `[provenance]`: added `provenance_trio_status = "pending"`,
  `nucleus_ingest_ready = true`, `deployment_era`, `target_era`
- `README.md`: three-era provenance chain, NUCLEUS readiness note
- Full deploy pipeline: **71/71 checks PASS, 19/19 cross-check verified,
  65/65 BLAKE3 integrity**

---

## Deploy Pipeline Verification

```
Step 1/7: BLAKE3 manifest          [OK]
Step 2/7: Full science validation   71/71 PASS (BLAKE3 + FES parity + OPES + alanine minima)
Step 3/7: Emit provenance           19/19 cross-check fields verified
Step 4/7: Re-hash                   [OK]
Step 5/7: Integrity verification    65/65 BLAKE3 verified
Step 6/7: Tarball                   (optional)
Step 7/7: Ingest                    biomeos → litho → manual (graceful fallback)
```

---

## Provenance Trio Signing Contract

| Primal | Role | Contract | Status |
|--------|------|----------|--------|
| rhizoCrypt | DAG merkle integrity | `dag_merkle_root` matches BLAKE3 chain | pending |
| loamSpine | Ledger registration | `spine_id` registered with `braid_id` + parent linkage | pending |
| sweetGrass | Attribution braid | Lineage chain + bibliography DOIs + PLUMED-NEST plum_ids | pending |

---

## Downstream Expectations

### For primalSpring (pseudoSpore 2.0)
1. **exp115 live validation**: run `biomeos nucleus ingest` against live Nest Atomic
2. **Provenance trio signing**: rhizoCrypt/loamSpine/sweetGrass fill pending slots
3. **Abstract nest-validate → Nest Atomic**: clean transitional shell-outs for
   postPrimordial compliance via Neural API

### For biomeOS
1. Wire `nucleus ingest` subcommand into top-level clap parser
2. Implement NestGate content-addressed store
3. Wire provenance trio services (rhizoCrypt DAG, loamSpine ledger, sweetGrass braid)

### For lithoSpore
1. ~~Wire `litho emit-pseudospore` positional arg interface~~ **DONE** — `--from-dir` + `--name`/`--version`
2. ~~Adopt `pseudospore-core` as dependency for envelope generation~~ **DONE** — canonical since Wave 55
3. ~~Validate domain-agnostic emission against second spring~~ **DONE** — groundSpring domain profile authored

---

## Three-Era Evolution Summary

```
Era 1: Ad-Hoc (v1.0.0 — v1.6.0)
  scope.toml hand-authored → blindly copied to validation.json

Era 2: Pipeline-Derived (v1.6.1)
  GRO/MDP/COLVAR/PDB → cross_check_scope() + env::detect()

Era 3: NUCLEUS Nest Deploy (v2.0+ target)
  litho CLI (envelope) + nest-validate (domain) + biomeos (gateway)
  → provenance trio signs → NUCLEUS-registered artifact
```
