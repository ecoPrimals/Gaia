# primalSpring Handoff — Wave 150t

**Date**: 2026-07-21 | **Version**: 0.9.42 | **Gate**: eastGate

## Summary

Wave 150t aligns primalSpring with the sovereignty evolution roadmap and
standards reorganization. New scenario validates structural readiness for
the three-tier sovereignty evolution (REPLACE → LATE-STAGE → FIREBREAK).
Mesh topology updated for southGate enrollment.

## Changes

### New Scenarios (+3, total 173)

| Scenario | Track | Checks | Purpose |
|----------|-------|--------|---------|
| `sovereignty-roadmap` | Evolution | 17 | Tower Atomic (BTSP, mesh, bearDog, songBird, skunkBat), primal pipeline (render, CAS, serve), rootPulse (Provenance Trio, lineage), firebreaks |
| `diderm-domain-posture` | Evolution | — | Domain architecture + membrane layer conformance (upstream) |
| `composition-access-control` | Infrastructure | — | Access boundary enforcement per DIDERM standard (upstream, 15 known debt) |

### Mesh Topology

- southGate assigned `10.13.37.9` (USB enrollment pending)
- zone-topology: southGate moved from unpeered → peered
- 7 gates in topology (5 active WG peers + 2 enrolled)

### KNOWN_DEBT (eastGate)

| Scenario | Failures | Reason |
|----------|----------|--------|
| `graphenegate-readiness` | 1 | aarch64 depot directory absent on dev gate |
| `composition-access-control` | 15 | Access layer not yet wired |

### Code Quality

- 0 clippy warnings (pedantic + nursery)
- Fixed `doc_markdown` in `s_composition_access_control`, `s_diderm_domain_posture`
- Fixed `sort` → `sort_unstable` in `s_diderm_domain_posture`

## Metrics

| Metric | Value |
|--------|-------|
| Scenarios | 173 |
| Lib tests | 1213 (0 fail, 2 ignored) |
| Clippy (pedantic+nursery) | 0 warnings |
| KNOWN_DEBT | 2 scenarios (16 total failures) |
| Mesh nodes | 7 (5 active + 2 enrolled) |

## Ecosystem Context (Wave 150t blurb)

- wateringHole standards reorganized: 37 → 4 directories
- Sovereignty evolution roadmap active (3-tier classification)
- DNSSEC validated on all 3 domains
- 105k+ ecosystem tests across 43 repos
- 6/6 live surfaces healthy

## For Upstream Teams

- **No action required** — all primalSpring items self-contained
- Sovereignty roadmap scenario provides early structural validation
  for Tower Atomic parity work (bearDog + songBird + skunkBat teams)
