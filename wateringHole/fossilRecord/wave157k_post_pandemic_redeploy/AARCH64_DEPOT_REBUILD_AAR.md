# AAR: aarch64-unknown-linux-musl Depot Full Rebuild

**Date**: Aug 12, 2026 20:30 | **Wave**: 157k | **Gate**: sporeGate (foreman)
**Blockers Closed**: #10 (grapheneGate depot stale), #11 (missing biomeOS + cellMembrane)

---

## Problem

grapheneGate (Pixel 8a, GrapheneOS) reported 12 primals from Jun 10 (Wave 108) — 2+ months stale.
`biomeOS` and `membrane` (cellMembrane) were **completely missing** from the `aarch64-unknown-linux-musl` depot.
`swarmvine` was also missing. grapheneGate had Tower 4-primal deployed but couldn't get full NUCLEUS.

## Root Cause

1. No sub-builder was assigned to `aarch64-unknown-linux-musl` in the foreman pipeline spec.
2. sporeGate had cross-compile capability but no automation to rebuild this target.
3. The cascade timer only rebuilt for the native x86_64-musl target.

## Resolution

### Phase 1: Local cross-compile (sporeGate)
- Built `membrane` and `swarmvine` for aarch64-musl (the two missing binaries)
- Built `nestgate` and `songbird` (stale vs x86_64 depot dates)
- Rebuilt `loamspine`, `coralreef`, `sweetgrass`, `biomeos`, `skunkbat` sequentially

### Phase 2: Sub-builder dispatch (ironGate) — FOREMAN PATTERN
- Verified ironGate has `aarch64-unknown-linux-musl` target + `aarch64-linux-gnu-gcc` linker
- Dispatched remaining 6 primals to ironGate via SSH: `beardog`, `barracuda`, `rhizocrypt`, `squirrel`, `petaltongue`, `toadstool`
- ironGate built all 6 in ~7 minutes
- Foreman pulled results back via SCP and deployed to canonical depot

### Phase 3: Distribution
- All 15 aarch64-musl binaries pushed to golgiBody WAN depot with BLAKE3SUMS
- grapheneGate can now pull full NUCLEUS from `depot.primals.eco`

## Depot Result

| Binary | Size | Source |
|--------|------|--------|
| barracuda | 4.2MB | ironGate |
| beardog | 6.6MB | ironGate |
| biomeos | 19.1MB | sporeGate |
| coralreef | 6.6MB | sporeGate |
| loamspine | 4.1MB | sporeGate |
| membrane | 13.4MB | sporeGate |
| nestgate | 7.3MB | sporeGate |
| petaltongue | 15.2MB | ironGate |
| rhizocrypt | 6.3MB | ironGate |
| skunkbat | 2.7MB | sporeGate |
| songbird | 21.5MB | sporeGate |
| squirrel | 3.4MB | ironGate |
| swarmvine | 2.2MB | sporeGate |
| sweetgrass | 10.6MB | sporeGate |
| toadstool | 9.5MB | ironGate |

## Spec Updates

- `FOREMAN_PIPELINE_SPEC.md`: Added ironGate as `aarch64-unknown-linux-musl` sub-builder (ACTIVE)
- `ECOSYSTEM_BLURB.md`: Updated depot status table with aarch64-musl row

## Lessons

1. **Sub-builder dispatch works.** ironGate has the toolchain and repos. First confirmed
   foreman → sub-builder → collect pattern for aarch64.
2. **Sequential local builds are slow.** 11 primals × ~2min each = ~22min on sporeGate.
   Dispatching 6 to ironGate in parallel cut total wall time significantly.
3. **aarch64-musl needs automation.** The cascade timer should fan out to ironGate
   for this target, same as it does for native musl. Next step in pipeline evolution.
4. **No sub-builder for aarch64-musl was a gap in the spec.** Now filled.
