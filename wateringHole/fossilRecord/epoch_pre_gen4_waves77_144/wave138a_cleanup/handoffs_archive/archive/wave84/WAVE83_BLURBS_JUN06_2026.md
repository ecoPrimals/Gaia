# Wave 83 — Blurbs by Level

**Date**: 2026-06-06  
**Author**: eastGate overwatch  
**Type**: Blurb — copy/paste by level  
**Wave 82c status**: ALL primal P1 items resolved. 6/6 capability_registry.toml
delivered. 3/3 domain_profile.toml delivered. UDS health probe fixed
(squirrel, petalTongue). plasmidBin fully harvested — 13/13 checksums verified.

---

## PRIMALS — Mountain Clear

All 13 primals at full parity. Zero P0/P1 gaps. Upstream is clean.

### Remaining (team-owned, non-blocking)

| Item | Owner | Priority |
|------|-------|----------|
| Coverage: songBird 73% → 90% | southGate | P3 (validation) |
| Coverage: nestGate 84% → 90% | ironGate | P3 (validation) |
| Coverage: petalTongue ~85% → 90% | ironGate | P3 (validation) |
| Coverage: toadStool ~84% → 90% | biomeGate | P3 (validation) |
| Coverage: barraCuda 81% → 90% | strandGate | P3 (validation) |
| Transport evolution: accept injected transport | all | P2 (songBird leads) |

No new code work required from primal teams for stadial gate.
Focus is deployment validation and mesh proof.

---

## SPRINGS — All Clear

All springs at full parity. `domain_profile.toml` delivered by all 3
requested springs. No remaining work.

---

## cellMembrane (ironGate) — plasmidBin Takeover

**This is the primary Wave 83 action item.**

cellMembrane assumes full ownership of plasmidBin as the ecosystem's
plasma depot for primal binaries.

### Context

plasmidBin depot is VPS-deployment-ready:
- 13/13 primal binaries rebuilt from latest upstream (today)
- BLAKE3 checksums verified (`checksums.toml`)
- Build provenance tracked (`provenance.toml`)
- Deploy script functional (`deploy_membrane.sh`)
- Build script fixed (`build_ecosystem_genomeBin.sh` — path casing,
  workspace binary overrides for biomeOS + skunkBat)

### AAR: Cascade-to-VPS Sync Gap (P1)

**Problem**: When primal teams push evolution, the outer membrane
(GitHub/Forgejo) receives it immediately. But the VPS peptidoglycan
layer has no awareness. Today's cascade pulled evolution from 4 primals
with real code changes. We manually detected changes, rebuilt
selectively, verified checksums, and pushed — 10 minutes of human
attention that should be zero-touch.

**Current flow** (manual):
```
Team pushes → GitHub ✓ → local pull ✓ → manual detect .rs changes →
manual rebuild → checksum verify → push → VPS still stale
```

**Target flow** (cellMembrane-owned):
```
Team pushes → GitHub → cellMembrane cascade detects .rs changes →
selective rebuild → checksum verify → push to depot →
VPS notified → peptidoglycan fetches + verifies + hot-swaps →
health.liveness confirms ALIVE
```

### First Long-Term Goal

Make the cascade-to-VPS pipeline zero-touch. This is the validation
check for cellMembrane owning plasmidBin. When a primal team pushes
a code change, the VPS should have the new binary within one refresh
cycle (currently 6 hours, target: 1 hour) with zero human intervention.

### Immediate Actions

1. Review `infra/plasmidBin/` repo — `sources.toml`, `checksums.toml`,
   `provenance.toml`, `deploy_membrane.sh`
2. Review `build_ecosystem_genomeBin.sh` in primalSpring
3. Run a test harvest cycle: pull upstream, detect changes, rebuild,
   verify checksums — validate the pipeline end-to-end
4. Design the VPS notification mechanism (webhook / push / poll)

### Reference Documents

- `WAVE82C_OVERWATCH_SHIFT_PLASMIDIN_HANDOFF_JUN06_2026.md` — full
  transfer table + AAR
- `CELLMEMBRANE_WAVE82C_PLASMIDOWNERSHIP_JUN06_2026.md` — ownership doc
- FRAGO: `wave80c-peptidoglycan-self-awareness` — updated with AAR

---

## GATES — Deployment Validation

### eastGate

- plasmidBin depot ready for VPS refresh
- 10G backbone installed across LAN gates
- mesh.init ready once cellMembrane confirms VPS binaries current

### strandGate

- All primal work acknowledged (Wave 82c ACK received)
- Coverage sprints ongoing (P3)
- Ready for mesh.init when triggered

### westGate

- Hardware-gated. No software action until hardware arrives.
- plasmidBin depot ready — deploy from depot on enrollment.

---

*"The mountain is clear. The membrane takes the depot. The mesh awaits."*
