> **FOSSILIZED** — Wave 157k cascade COMPLETE. Content absorbed into ORTHOGONAL_DIMENSIONS_REVIEW.md and ECOSYSTEM_BLURB.md. Superseded by ortho cascade response. All findings resolved.

# AAR: westGate Wave 157j — Nest Atomic Neural API + riboCipher Fix

**Date**: Aug 12, 2026 08:06 EDT | **Wave**: 157j | **Gate**: westGate
**Posture**: BUILDER — Nest Atomic composition + riboCipher transport fix

---

## Executive Summary

Fixed a multi-layered riboCipher transport bug that prevented all sweetGrass attribution
methods from routing through the Neural API. Built the Nest Atomic composition layer —
6 independent domain health probes modeled on hotSpring's thin-layer pattern. Deprecated
9 Python/Bash glue scripts with specific Rust/Neural API replacement paths. All 6 Nest
domains now report healthy with 14 primals alive and 139 translation routes operational.
`braid.verify`, `braid.list`, and `capability.call braid/verify` all route correctly
through riboCipher transport to sweetGrass.

---

## riboCipher Transport Fix (Critical — P0)

### Root Cause

Three independent code paths called `register_translation()` (hardcodes `ribocipher=false`),
overwriting TOML-loaded translations that correctly had `ribocipher=true`:

| Overwrite Path | Code | When |
|---------------|------|------|
| `load_from_config_for_family()` | `capability_translation/mod.rs` | Startup phase 2 — redundantly re-loaded the same TOML |
| `primal.announce` handler | `handlers/announce.rs` | Runtime — any primal self-registering |
| Graph translation loader | `neural_api_server/translation_loader.rs` | Startup phase 3 — loading `*.toml` graphs |

The TOML loader (`toml_loader.rs`) correctly inherited `ribocipher=true` from
`[domains.attribution]`, but all three subsequent paths destroyed it.

### Fix

1. **Removed redundant TOML re-load** in `translation_startup.rs` (step 2 no longer
   overwrites step 1's correct translations; domain→router registration preserved)
2. **Fixed `load_from_config_for_family()`** to read per-entry and domain-level ribocipher
   flags, using `register_translation_full()` instead of `register_translation()`
3. **Fixed `primal.announce`** to call `domain_requires_ribocipher()` before registration
4. **Fixed graph loader** to inherit domain ribocipher flags

### Regression Tests

```
domain_ribocipher_inherits_to_translations     — PASS
load_from_config_respects_domain_ribocipher    — PASS
```

### Validation

```
braid.verify  → sweetGrass (ribocipher=true)  → "Braid not found" ✅  (was: -32002)
braid.list    → sweetGrass (ribocipher=true)  → 100 braids returned ✅
capability.call braid/verify → sweetGrass     → correct routing ✅
```

---

## Nest Atomic Composition Layer (New)

Built per-domain health probes modeled on hotSpring's `composition.rs` thin-layer pattern.

### New Neural API Endpoints

| Method | Route | Returns |
|--------|-------|---------|
| `nest.health` | `Route::NestHealth` | Per-domain health for all 6 Nest domains |
| `composition.nest_health` | `Route::NestHealth` | Same (alias) |
| `nest.capabilities` | `Route::NestCapabilities` | 139 translations grouped by domain with ribocipher flags |

### Nest Domains (6)

| Domain | Providers Found | Status |
|--------|----------------|--------|
| security | beardog, crypto, security, ed25519, x25519 | ok |
| discovery | songbird, network | ok |
| storage | nestgate, permanence | ok |
| dag | rhizocrypt, dag | ok |
| ledger | loamspine, ledger | ok |
| attribution | sweetgrass | ok |

```
nest.health: healthy=true, pipeline_ready=true, domains=6/6, primals_alive=14
```

### Translation Surface

| Domain | Translations | ribocipher |
|--------|-------------|-----------|
| attribution | 32 | 26 with ribocipher |
| dag | 18 | 18 with ribocipher |
| discovery | 13 | 0 |
| ledger | 5 | 0 |
| security | 42 | 0 |
| storage | 29 | 0 |
| **Total** | **139** | **44** |

### Architecture Pattern (from hotSpring)

The Nest Atomic follows hotSpring's Node Atomic thin-layer model:
- No duplicated local logic — primals are queried for health, not reimplemented
- Domain-based resolution via primal name/alias matching
- Independent per-domain health (not monolithic aggregate)
- Pipeline readiness derived from all 6 domains being `ok`

---

## Glue Deprecation

### Fossil Scripts (archived, marked DEPRECATED)

| Script | Lines | Replacement |
|--------|------:|-------------|
| `fossilRecord/bulk_ingest.py` | 552 | Superseded by `native_braid.py` |
| `fossilRecord/alphafold_prov_trailer.py` | 176 | Inline braiding at ingress |
| `fossilRecord/metered_download.sh` | 138 | `nestGate content.mirror` + `membrane data.sync` |
| `fossilRecord/alphafold_bulk_structures.sh` | 109 | Async Python (already superseded) |

### Active Scripts (marked with deprecation + replacement path)

| Script | Lines | Target Replacement |
|--------|------:|-------------------|
| `native_braid.py` | 1,308 | `membrane content.braid` + biomeOS graph composition |
| `braid_pentest.py` | 1,332 | `sourdough validate neural-api --suite braid-pentest` |
| `overwatch-temporal.sh` | 241 | `membrane gate.check --json` / `temporal.cascade` |
| `westgate_boot_check.sh` | 309 | `membrane gate.preflight --extended` + `nest.health` |
| `alphafold_full_sync.sh` | 71 | Keep rsync, replace braid hook with `membrane content.braid` |

`native_braid.py` is the **last active Python** in the westGate production pipeline.

---

## Files Modified

### biomeOS Core (8 files)

| File | Change |
|------|--------|
| `capability_translation/mod.rs` | Added `translations_with_prefix()`, fixed `load_from_config_for_family()` ribocipher |
| `capability_translation/toml_loader.rs` | 2 regression tests for domain ribocipher inheritance |
| `handlers/nest_atomic.rs` | **NEW** — Nest Atomic per-domain health + capabilities handler |
| `handlers/mod.rs` | Wired `nest_atomic` module |
| `handlers/announce.rs` | ribocipher-safe `primal.announce` registration |
| `neural_api_server/route_table.rs` | `NestHealth` + `NestCapabilities` route variants |
| `neural_api_server/routing.rs` | Dispatch wiring for nest routes |
| `neural_api_server/translation_startup.rs` | Removed redundant TOML re-load (overwrite source) |
| `neural_api_server/translation_loader.rs` | ribocipher-safe graph translation loading |

### Deprecation Headers (9 scripts)

4 fossilRecord scripts + 5 active wateringHole scripts.

---

## Near-Term Plan: Data Handling + Mesh

### Colocated Teams at westGate-CAS

- **wetSpring** — parallel IDE, local data handling
- **projectFOUNDATION** — validation + experiment orchestration

### Focus Areas

1. **Local data handling for wetSpring**
   - Nest Atomic surface (`nest.store`, `nest.retrieve`, `nest.commit`) as the data API
   - wetSpring operates as a parallel IDE consuming the same CAS + provenance trio
   - Local socket routing via biomeOS Neural API (no mesh required)

2. **Data serving for nestgate.io peti layer**
   - nestGate content API exposed through songBird HTTP + mesh relay
   - CAS content-addressable retrieval for external consumers
   - Provenance verification via `braid.verify` over mesh

3. **Mesh integration**
   - Cross-gate capability routing for federated data serving
   - songBird relay + discovery for multi-gate CAS access
   - MeshRelay authentication via bearDog riboCipher transport

4. **Replace native_braid.py**
   - Rust-native `membrane content.braid` wrapping biomeOS graph:
     `content.ingest → dag.session.create → dag.event.append_batch
     → dag.dehydration.trigger → crypto.sign → session.commit → braid.create`
   - Eliminates last Python in production pipeline

---

## Upstream Brief

For strandGate and spring teams reassembling:

1. **Nest Atomic is independently addressable** — `nest.health` returns per-domain
   health for all 6 domains (security, discovery, storage, dag, ledger, attribution)
2. **riboCipher transport is fixed** — all sweetGrass attribution methods route correctly
   through the Neural API with `[0xEC, 0x01]` framing
3. **hotSpring thin-layer pattern absorbed** — biomeOS composition follows the same
   domain-based, capability-resolved architecture as `NodeAtomicQcd`
4. **Glue is marked for deprecation** — each script has a specific Rust/Neural API
   replacement path documented in its header
5. **139 Nest translations operational** — 32 attribution, 18 dag, 29 storage, etc.
6. **wetSpring + projectFOUNDATION colocating** — local data handling + validation
   will use the Nest Atomic Neural API surface directly
