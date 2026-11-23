# hotSpring Handoff: Sovereignty Audit + PostPrimordial Checkpoint (Exp 224)

**Date:** 2026-05-26
**From:** hotSpring GPU Solve team
**Scope:** Sovereignty audit, documentation corrections, postPrimordial transition

## Summary

Rigorous audit of the "sovereign GPU compute" claim on the hotSpring fleet
(2x Titan V GV100 under VFIO, 1x RTX 5060 under nvidia DRM). Result: **Tier 1
sovereign infrastructure confirmed, Tier 2 sovereign compute NOT achieved.**

## Key Findings

### Ground Truth: `sovereign.classify_tier` on Both Titan Vs

Both GPUs return identical evidence:

```
tier: warm_infrastructure (level 1)
tpc_alive: false
tpc_status: 0xBADF5040 (PRI fault)
gpc_enables: 0x00000000
fecs_pc: 0xBADF5040
pmc_enable: 0x5fecdff1
pramin_accessible: true
```

### Three Misconceptions Corrected

1. **VBIOS POST creates the warm state, not toadStool.** The `warm_detected: true`
   and `PMC_ENABLE=0x5fecdff1` reported by `sovereign.init` is from UEFI/VBIOS
   during power-on POST. `sovereign.init` detects and skips all hard stages.

2. **`compute_ready: true` is an init health check.** It verifies PTIMER, PRAMIN
   sentinel, and PMC_ENABLE readback — NOT TPC PRI stations or shader dispatch
   capability. Doc comments updated in `sovereign_types.rs` and `sovereign_init.rs`.

3. **RTX 5060 dispatch is vendor-mediated, not sovereign.** The 8/8 shader roundtrip
   runs through nvidia DRM on the proprietary driver.

### TPC Wall (Tier 2 Blocker)

TPC PRI stations at `0x504000` return `0xBADF5040` (PRI fault) on VFIO Titan V.
These stations are created by GPCCS firmware during GR initialization. GPCCS is
HS fuse-locked on GV100. No software-only path exists without vendor firmware
running GPCCS.

## Documentation Corrected

- `README.md` — sovereignty tier model updated with audit results
- `EXPERIMENT_INDEX.md` — tier status corrected, experiment count → 224
- `experiments/223_ACR_SOVEREIGN_BOOT_CATALYST.md` — status corrected
- `experiments/224_SOVEREIGNTY_AUDIT_CHECKPOINT.md` — new checkpoint document
- `experiments/README.md` — Exp 224 row added
- `specs/SOVEREIGN_VALIDATION_MATRIX.md` — Tier 2 status corrected
- `CHANGELOG.md` — sovereignty audit entry added
- toadStool `sovereign_types.rs` — `compute_ready` field doc clarified
- toadStool `sovereign_init.rs` — module docs clarified
- toadStool `sovereign_tiers.rs` — Tier 2 status updated

## PostPrimordial Transition

- Local `wateringHole/handoffs/` archived to `infra/wateringHole/handoffs/hotSpring/`
  (6 active + 38 archived handoffs)
- Local `wateringHole/README.md` updated as redirect pointer
- All plasmidBin primals verified (`fetch.sh --all`, `validate_composition.sh`)
- **toadStool remains local build** — hotSpring team owns it, pushes upstream
- No deprecated `/run/coralreef` paths in active code
- `socket_dirs()` discovery order works with live primals

## What's Real (Tier 1 Achievements)

VFIO + BAR0 MMIO, DMA mapping, PRAMIN, PFIFO channels, CE runlist, FECS
liveness, 183ms warm handoff, catalyst pattern (83K regs), PRI ring recovery,
falcon register map (16 tests), Bar0 hardening (ENGCTL deny-list), sovereign
tier taxonomy, RTX 5060 DRM dispatch (8/8), AMD sovereign compiler (24/24),
NVIDIA sovereign compiler (SM35/SM70/SM120).

## Remaining Path to Tier 2

1. Catalyst boot (Exp 219) — TPC station persistence across unbind not yet tested
2. Runtime Services model — nvidia loaded as persistent service (pragmatic, not sovereign)
3. GPCCS firmware research (Tier 3) — long-term
4. Generation pivot — GPUs without HS fuse locks

## Upstream Action Items

- primalSpring audit of corrected sovereignty claims
- Validate postPrimordial deployment patterns across other springs
- Consider renaming `compute_ready` → `init_pipeline_passed` in future toadStool release
