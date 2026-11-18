# tideGlass Phase 0 — External Review

**Date**: Aug 16, 2026 | **Wave**: 157k | **From**: External reviewer (overwatch-directed)
**To**: westGate-CAS team, ironGate (tideGlass), strandGate (arXiv), overwatch
**Type**: Assessment + Recommendations
**Scope**: gen5 critical path bottleneck — tideGlass Phase 0 archaeology

---

## Executive Summary

tideGlass Phase 0 (GPS platform archaeology) is the ecosystem's **sole gen5 bottleneck**.
This has been true since Wave 155i and remains true at Wave 157k.

| Metric | Value |
|--------|-------|
| Assignment date | June 5, 2026 (Gonzales meeting, GPS platform assigned) |
| Start date | NOT STARTED |
| Gap duration | 10 weeks, 2 days |
| Infrastructure prerequisites | ALL COMPLETE |
| Data prerequisites | ALL COMPLETE (482 GB on ZFS, 100% provenance) |
| Provenance chain | 7/7 (was 6/7 at assignment) |
| NUCLEUS gates online | 12 (was ~5-6 at assignment) |

The ecosystem blurb, wave.toml, GEN5_CRITICAL_PATH, and WESTGATE_ENMESHMENT_AAR all
confirm: tideGlass Phase 0 = sole bottleneck. The infrastructure question is answered.
The remaining work is cultivation.

**Assessment**: The 10-week gap was not idle — it was infrastructure convergence that
makes Phase 0 execution faster and more robust than it would have been in June. The
system is now ready to execute in days, not weeks.

---

## What Evolved During the Gap (Wave 155i → 157k)

The ecosystem prioritized infrastructure convergence over application-layer work.
This was the correct evolutionary sequence: attempting Phase 0 without Provenance 7/7
or the data estate would have produced orphaned artifacts outside the trust chain.

| Achievement | Wave | Impact on tideGlass |
|-------------|------|---------------------|
| bearDog `crypto.sign_ed25519` shipped | 155j | Provenance 7/7 unblocked — tideGlass artifacts will carry Ed25519 signatures |
| Provenance Trio 7/7 E2E validated | 155k | Full chain: CAS → DAG → Merkle → Spine → Ed25519 → Attribution braid |
| westGate data federation: 529 GB, 130 datasets | 155f–156d | All 7 tideGlass module datasets on ZFS with provenance |
| NF Data Portal ingestion COMPLETE | 155f | 658 files, 666 MB — extension target data already sovereign |
| arXiv Rung 1 paper: 41/42 rubric items | 155n–157k | Parallel gen5 proof event (independent track) |
| 12 gates online (was ~5-6) | 156–157 | Compute capacity for GPS training/inference |
| AlphaFold ingress pipeline (23 TB, 246M structures) | 157k | Demonstrates Nest Atomic can ingest at arbitrary scale |
| DF64 sovereign shader compilation | 157k | barraCuda + coralReef GPU path proven without CUDA |
| rootPulse step handlers (rhizoCrypt + sweetGrass) | 157k | Provenance automation for future tideGlass experiments |
| Pipeline divergence fix + convergence | 157k | 13/13 primals current, depot autonomous |
| 14/14 provenance trio experiments PASS | 157k | Trust model lifecycle fully validated |

**Net effect**: Phase 0 in June would have produced a dependency map with no home.
Phase 0 today produces artifacts that immediately enter the provenance chain, sit on
validated data, and flow through a proven pipeline to pseudoSpore.

---

## What Phase 0 Actually Requires Now

The original plan (GPS README, Phase 0 checklist) estimated 1-2 weeks. Given what
has already been accomplished outside the formal Phase 0 boundary, the actual
remaining work is smaller.

| Task | Original Estimate | Current State | Remaining |
|------|-------------------|---------------|-----------|
| Download Zenodo artifact (713 MB v5 / 840 MB v6) | Hours | NOT DONE | Minutes (100 Mbps+ available) |
| Inventory all files, dependencies, environments | 2-3 days | NOT DONE | 1-2 days (AI-assisted) |
| Map `gps_env.yml` — Python 2 vs 3 boundaries | 1-2 days | NOT DONE | 1 day |
| Identify Fortran components | 1 day | NOT DONE | Hours (likely none per Cell 2026 methods) |
| Trace data dependencies (LINCS, GEO, weights) | 2-3 days | **ALREADY DONE** — 482 GB on ZFS matches DATA_MANIFEST.md | Verification only |
| Paper lineage (Lamb 2006 → GPS Cell 2026) | 2-3 days | **ALREADY DONE** — documented in GPS progress correspondence | None |
| Document dependency graph | 1-2 days | NOT DONE | 1-2 days |

**Revised total**: 5-7 focused days. Not 1-2 weeks.

**What made it shorter**: The GPS progress email (June 2026) already traced the full
20-year lineage. The data federation work already downloaded and provenance-traced the
module datasets. The remaining work is hands-on-artifact: unpack the Zenodo tarball,
read the code, map the environments, and document what's broken.

---

## External Contact State

### Gonzales — GPS Platform Collaborator

| Event | Date | Status |
|-------|------|--------|
| In-person meeting, GPS platform assigned | Jun 5, 2026 | COMPLETE |
| GPS progress email sent (lineage + infrastructure brief) | Jun 2026 | SENT |
| Bin Chen introduction (offered by Gonzales) | Jun 5, 2026 | **NOT MATERIALIZED** (10 weeks) |
| Follow-up communication | — | NONE SENT |
| CTF NDU grant alignment | Ongoing | ALIGNED (Gonzales PI, ecosystem compute) |

**Assessment**: The collaborator relationship is warm but stalled. No follow-up was
sent because no Phase 0 result existed to report. The Bin Chen introduction (GPS
platform PI, Cell 2026 corresponding author) was offered but never scheduled — likely
because Gonzales is waiting for a concrete artifact to anchor the introduction around.

**Recommendation**: Complete Phase 0, then send a results email. The dependency map
and reproduction blockers are the credible artifact for reactivation. Do not email
with status updates — email with findings.

### arXiv Rung 1 — Reviewer Panel

| Reviewer | Affiliation | Domain | Relationship |
|----------|-------------|--------|--------------|
| Murillo | MSU CMSE | Computational physics, GPU scaling | Known (professor) |
| Chuna | LANL | Lattice QCD, gradient flow | Known (validated results Apr 2026) |
| Bazavov | MSU CMSE/Physics | Lattice QCD specialist | Known (professor) |

**Status**: Paper at 41/42 rubric items. Data COMPLETE. LaTeX source exists. Reviewer
send is ~6-8 hours of integration work per ECOSYSTEM_BLURB assessment. This is the
fastest path to a gen5 proof event (preprint exists, reviewers exist, artifact exists).

### Barrick — LTEE Lab

| Event | Date | Status |
|-------|------|--------|
| In-person interview | May 18, 2026 | COMPLETE |
| lithoSpore USB delivered (4 copies) | May 18, 2026 | DELIVERED |
| Lab response | — | NONE RECEIVED |

### Valve/Inkfish — Industry

| Event | Date | Status |
|-------|------|--------|
| Email sent (v3, scientist-first) | Jul 29, 2026 | SENT |
| 2-week response window | Aug 12, 2026 | PASSED (silence) |
| Next action per protocol | Now | LinkedIn warm engagement with marine biology team |

---

## Dormant / Locked Components

These ecosystem components are relevant to the tideGlass critical path but are
not currently active. Each needs specific activation conditions.

| Component | Location | State | Activation Condition |
|-----------|----------|-------|---------------------|
| `tideGlass` crate | ironGate (assigned) | **DOES NOT EXIST** — no code, no repo, no scaffold | Phase 0 completion defines the crate's scope |
| `protoKarya` org | GitHub | EXISTS but EMPTY | tideGlass becomes first project |
| `helixVision` | ironGate (assigned) | DORMANT | tideGlass gene expression module forces evolution |
| `initioChem` | strandGate (assigned) | DORMANT | tideGlass MolSearch module forces evolution |
| `footPrint` | ironGate (assigned) | STATUS UNKNOWN | User-facing surface — depends on product pipeline |
| healthSpring MATRIX | westGate/strandGate | VALIDATED (233/233) | Not wired to tideGlass data flow — needs composition graph |
| wetSpring GPS tracks | westGate | VALIDATED (Track 2: 40/40) | Shares LINCS/ChEMBL data — no tideGlass handshake yet |
| neuralSpring ML | strandGate | VALIDATED (various) | MCTS, expression prediction — capabilities exist, not composed |

**Key observation**: The dormant components are not blocked by infrastructure. They
are blocked by the **specification** that Phase 0 produces. Until the dependency
inventory exists, no team knows what capabilities tideGlass actually needs from the
ecosystem. Phase 0 is not just archaeology — it is the specification event that
activates dormant primals.

---

## Evolution Targets (Recommendations)

### Priority 1: Start Phase 0 This Week

The archaeology is 5-7 focused days. The primary gate (westGate) has the data. Any
compute gate can run the Python environments for inspection. The ecosystem has been
calling this the "sole bottleneck" for 6 waves without starting it.

**Specific ask**: Assign a 5-day focused session. Download Zenodo v5+v6. Inventory.
Map. Document. Produce an AAR with the dependency graph, broken environments, and
a Phase 1 execution plan.

### Priority 2: arXiv Rung 1 Send to Reviewers (Parallel)

Independent of tideGlass. Closest to a gen5 proof event. 6-8 hours of integration
work. Three reviewers are formed. The paper data is COMPLETE. This can happen in
parallel with Phase 0 and produces external validation faster than any other track.

### Priority 3: Gonzales Reactivation (Gated on Phase 0)

Do not email until Phase 0 is done. The credible artifact is:
- Complete dependency map
- Identified reproduction blockers
- Specific questions for Bin Chen (license discrepancy, unpublished preprocessing, model weights)
- Demonstration that the data estate already matches the platform requirements

This converts "we've been building infrastructure" into "here are the findings from
the assigned codebase, and here's what the ecosystem needs from the PI to proceed."

### Priority 4: Valve Follow-Up (Independent)

Response window passed Aug 12. Per OUTREACH_STATUS protocol, next action is LinkedIn
warm engagement with the marine biology team lead. This is independent of all other
tracks and should proceed on its own timeline.

### Priority 5: Dormant Component Activation Plan

After Phase 0 produces a specification, overwatch should:
1. Map GPS modules → ecosystem capabilities (which primals serve which module)
2. Identify gaps (capabilities no primal currently provides)
3. Create activation impulses for dormant products (helixVision, initioChem)
4. Wire a composition graph showing tideGlass → primal data flow

---

## Expected Responses

| Team | Expected Response | Deadline |
|------|-------------------|----------|
| westGate | Confirm data readiness. Schedule Phase 0 session. | Wave 158 |
| ironGate | Confirm tideGlass crate bootstrap timeline. What blocks scaffolding? | Wave 158 |
| strandGate | Confirm arXiv reviewer send timeline. What blocks the last rubric item? | Wave 158 |
| overwatch | Priority call: tideGlass Phase 0 vs AlphaFold Phase B/C vs arXiv. All three compete for human attention. | Immediate |

---

## Appendix: The Cost of the Gap

The 10-week gap has measurable costs beyond delayed gen5:

1. **Collaborator contact decay** — Gonzales has not heard results in 10 weeks.
   Academic collaborators operate on semester timescales. Fall semester starts
   ~Aug 26. The window for CTF NDU preliminary data narrows.

2. **Bin Chen introduction stalled** — The GPS PI introduction was offered as a
   bridge to the codebase author. Without it, Phase 1 reproduction must rely
   entirely on published methods + Zenodo artifact (workable but slower).

3. **No revenue bridge** — The CTF NDU ($125K) requires computational preliminary
   data. Every week of delay is a week the grant application cannot be submitted.
   The ecosystem has no revenue while gen5 remains in QUEUED state.

4. **arXiv opportunity cost** — Rung 1 has been at 41/42 for multiple waves. Each
   week of delay is a week someone else could publish consumer-GPU lattice QCD
   (unlikely but nonzero risk — the field is active).

These costs are not catastrophic. The infrastructure investment was necessary. But
the system has been in QUEUED state long enough that the marginal cost of each
additional week now exceeds the marginal benefit of further infrastructure polish.

**The pivot point is now.**

---

*External review — Wave 157k. tideGlass Phase 0 is 5-7 days of focused work on
a system that has spent 10 weeks becoming ready for it. The fermenter is built.
The medium is prepared. The culture is waiting to be inoculated. Start.*
