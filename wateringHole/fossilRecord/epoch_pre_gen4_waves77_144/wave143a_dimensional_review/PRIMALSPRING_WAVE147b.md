# primalSpring Wave 147b Handoff

**Date**: 2026-07-17 | **Version**: 0.9.41 | **Commit**: `fbe65a6e`

## Summary

Wave 147b: cellMembrane shipped `gate.enroll` — primalSpring validates the
automated 5-phase mesh enrollment pipeline structurally.

## What Changed

### New Scenario: `gate-enroll-pipeline`
- **Track**: Infrastructure | **Tier**: Rust | **Checks**: 20
- Validates the 6 enrollment phases have infrastructure support:
  1. `manifest.resolve` — gate profiles (IP, transport, roles) in manifest
  2. `wg.keygen` — WireGuard interface and subnet defined
  3. `wg.config` — address assignments for ≥5 gates
  4. `mesh.verify` — hub node, subnet, northGate enrolled
  5. `forgejo.verify` — Forgejo referenced, SSH derivable
  6. `git.remotes` — Forgejo-first remote standard enforceable

### Mesh Topology Updated
- northGate assigned `address = "10.13.37.8"` (6th enrolled node)
- `zone-topology` scenario updated: northGate removed from unpeered list

### KNOWN_DEBT Aligned
- Removed `sporeprint-pure-primal-parity` (now passes on eastGate)
- `graphenegate-readiness` corrected from 2 → 1

## Metrics

| Metric | Value |
|--------|-------|
| Version | 0.9.41 |
| Scenarios | 170 (12 tracks, 3 tiers) |
| Tests | 1203 lib (0 failures, 2 ignored) |
| Known Debt | 1 (graphenegate-readiness: aarch64 depot absent locally) |
| Clippy Errors | 0 |

## Upstream Gaps (for other teams)

| Gap | Owner | Priority |
|-----|-------|----------|
| Hub-side peer addition automation | cellMembrane | NEAR-TERM |
| songBird beacon protocol (BTSP self-enrollment) | songBird | NEAR-TERM |
| northGate NUCLEUS deploy + benchScale validation | northGate ops | NEXT |
| `gate.enroll` capability in registry | ecosystem | P2 |

## Notes

- The `gate-enroll-pipeline` scenario validates structural readiness, not live
  enrollment. Live enrollment is cellMembrane's responsibility.
- primalSpring's existing `gate-enrollment` scenario (Wave 139b) validates the
  staged progression model (SSH → preflight → install → NUCLEUS → systemd → WG → cascade).
  The new scenario validates the specific `membrane gate.enroll` command's phases.
- The "Forgejo-first remote standard" is now enforceable: manifest references
  Forgejo, and the enrollment pipeline's final phase configures remotes.
