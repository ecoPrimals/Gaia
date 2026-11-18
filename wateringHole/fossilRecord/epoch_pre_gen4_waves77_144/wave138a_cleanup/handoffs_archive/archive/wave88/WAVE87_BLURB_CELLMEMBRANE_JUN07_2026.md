# Wave 87 Blurb — cellMembrane

**Date**: 2026-06-07  
**From**: eastGate overwatch  
**To**: cellMembrane team  
**Subject**: Deployment pipeline validated — trigger mechanism needed

---

## Status

The plasmidBin deployment pipeline has been validated **end-to-end** on eastGate:

```
membrane plasmid.status   → 3 drifted (biomeOS, loamSpine, petalTongue)
membrane plasmid.harvest  → 3 built, 10 current, 0 failed (253s)
membrane plasmid.status   → 13/13 current, 0 drifted
biomeos nucleus start     → beardog HEALTHY, songbird HEALTHY (from depot)
```

The biomeOS v4.09 federation env fix was the validation target — it was harvested,
checksummed, staged, and launched from the depot successfully. The pipeline works.

Cascade: 38/38 parity, 0 failures, freshness published.

---

## P1: On-Demand Trigger Mechanism (CM-TRIGGER-01)

The 30-minute `plasmid-pipeline.timer` handles background convergence on the VPS.
But when a primal team pushes a critical fix, the operator should not have to:
1. SSH to the gate
2. Manually run `membrane plasmid.harvest`
3. Manually restart NUCLEUS

**Request**: Implement an on-demand trigger for the plasmid pipeline.

### Proposed Evolution

| Priority | Trigger | Description |
|----------|---------|-------------|
| **P1** | `membrane plasmid.pipeline --now` | CLI command: immediate harvest → refresh cycle. Runs the same logic as the timer but on-demand. |
| **P2** | Forgejo webhook → selective harvest | Push to any primal repo triggers a cascade + selective harvest for just the changed primal. Evolves CM-WEBHOOK-01. |
| **P3** | `membrane plasmid.watch` | Daemon mode: polls upstream commit positions, auto-harvests on drift detection. Complement to the timer for development-heavy periods. |

The model is: **timed + triggered**. The timer keeps everything converging in the background.
The trigger gives operators immediate response when it matters.

---

## P2: Binary Search Priority (BIO-SEARCH-01) — biomeOS team

This is a biomeOS issue but affects deployment validation. In `nucleus_procs.rs`,
`discover_binaries_with()` searches `livespore-usb/` *before* `ECOPRIMALS_PLASMID_BIN`.

Result: 5/12 primals resolve from stale `livespore-usb` instead of the depot:
- beardog, songbird, toadstool, squirrel, nestgate → livespore-usb
- coralreef, rhizocrypt, loamspine, sweetgrass, skunkbat, barracuda, petaltongue → depot

**Fix**: When `ECOPRIMALS_PLASMID_BIN` is set, it should be the **first** search path.
The depot is the single source of truth for harvested, checksummed, provenance-tracked binaries.

This is blocking the 2-gate mesh proof: songbird resolves from livespore-usb (old binary)
instead of the depot (v4.09 with federation env fix).

---

## Current Gaps Summary

| ID | Description | Owner | Priority | Status |
|----|-------------|-------|----------|--------|
| CM-TRIGGER-01 | On-demand plasmid pipeline trigger | cellMembrane | P1 | NEW |
| BIO-SEARCH-01 | Binary search priority (livespore-usb > depot) | biomeOS | P2 | NEW |
| CM-WEBHOOK-01 | Webhook-driven cascade + selective rebuild | cellMembrane | P3 | Open |
| PRIMAL-TRANSPORT-01 | Transport injection (1/14 primals) | all-primals | P2 | Open |

---

## What's Working

- `membrane plasmid.harvest` — drift detection, rebuild, checksum, staging
- `membrane plasmid.status` — freshness tracking, depot parity
- `membrane plasmid.refresh` — VPS atomic replace + restart
- `plasmid-pipeline.timer` — 30-min zero-touch VPS convergence
- `membrane temporal.cascade` — 38/38 repos, parallel (6.9s), freshness publish
- Pipeline proven: team pushes fix → harvest → depot → NUCLEUS → primal healthy

---

*"The pipeline works. Now we need the trigger so deployment doesn't wait for the clock."*
