# airSpring — Wave 17 Signal Adoption Handoff

**Date**: May 16, 2026
**Spring**: airSpring v0.10.0
**guideStone**: L4 (structural L5)
**Audit**: primalSpring Wave 17 — Neural API Signal Elevation

---

## What Changed

### 1. Registration: `primal.announce` (replaces 3-call pattern)

**Before**: `niche::register_with_target()` made 3+ separate RPC calls:
- `lifecycle.register` (1 call)
- `capability.register` per domain + per capability (50+ calls)
- `method.register` (1 call from separate `register_methods_with_biomeos()`)

**After**: Single `primal.announce` RPC call:
```json
{
  "method": "primal.announce",
  "params": {
    "primal": "airspring",
    "socket": "/run/ecoprimals/airspring-{family_id}.sock",
    "capabilities": ["agriculture", "ecology", "provenance"],
    "methods": ["science.et0_fao56", "...51 total..."],
    "signal_tiers": ["nest"],
    "version": "0.10.0"
  }
}
```

Automatic fallback to legacy pattern if `primal.announce` fails (pre-v3.57 biomeOS). The legacy path now includes `method.register` in the same flow (was separate).

### 2. Provenance Pipeline: `nest.store` + `nest.commit` Signal Dispatch

**`record_experiment_step()`** — tries `nest.store` first:
- biomeOS decomposes into: NestGate.content.put → rhizoCrypt.dag.event.append → loamSpine.spine.seal → sweetGrass.braid.create
- Falls back to legacy `capability.call("dag", "append_event")` if signal unavailable

**`complete_experiment()`** — tries `nest.commit` first:
- biomeOS decomposes into: rhizoCrypt.dehydrate → bearDog.sign → NestGate.store → loamSpine.seal
- Falls back to legacy 3-phase pipeline (dehydrate → commit → attribute)

Domain-specific methods (`science.et0_fao56`, `ag.measure`, etc.) remain as `ctx.call()` — signals only replace orchestration sequences.

### 3. New Dispatch Endpoints

| Method | Purpose |
|--------|---------|
| `primal.announce` | Accept inbound announces from other ecosystem participants |
| `primal.info` | Return niche metadata (version, 51 capabilities, signal tiers, guidestone level) |

### 4. Registry Sync

- Canonical registry: 451 methods (Wave 17, was 413)
- Cross-sync test threshold updated: `>= 450` (was `>= 410`)
- Local capability count: 51 (was 49, added `primal.announce` + `primal.info`)
- `capability_registry.toml` updated with 2 new entries

### 5. L5 Certification Evolution

`validate_method_register` → `validate_primal_announce`:
- Tries `primal.announce` against biomeOS first
- Falls back to `method.register` if announce unavailable
- Both paths validate acceptance

---

## Verification

- **1,057 lib tests**: PASS
- **62 forge tests**: PASS
- **Integration tests**: PASS (includes `capabilities_match_registry`, `capability_cross_sync`)
- **Clippy pedantic+nursery**: 0 warnings (from our changes)

---

## Signal Adoption Status

| Signal | Status | Notes |
|--------|--------|-------|
| `primal.announce` | **Adopted** | Registration path with fallback |
| `nest.store` | **Adopted** | Provenance step recording with fallback |
| `nest.commit` | **Adopted** | Experiment completion with fallback |
| `node.compute` | Not adopted | airSpring compute dispatch through toadStool is minimal; evaluate when GPU pipeline deepens |
| `tower.*` | Not applicable | Tower signals are consumed by Tower atomic specialists (ludoSpring) |
| `meta.*` | Not applicable | Meta signals are agentic layer (squirrel + petalTongue) |

---

## Remaining Glacial Items

- [ ] Thread 6 (Agricultural Science) — 36 targets exist in foundation, need expression refresh
- [ ] LTEE E3 reproduction (primary paper queue item)
- [ ] guideStone L5 live validation (blocked on live biomeOS + toadStool)

---

**Submitted by**: airSpring v0.10.0
**For**: primalSpring upstream audit
