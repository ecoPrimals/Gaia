# Handoff: hotSpring → Rung 1 arXiv Submission

**Date**: Aug 2, 2026 PM | **Wave**: post-155n
**From**: sporePrint team | **To**: hotSpring team (strandGate + biomeGate)
**Status**: Paper reframed. 5/5 sections filled. Experiment queue is the ONLY blocker.

---

## TL;DR

The arXiv paper has been **reframed from "lattice QCD paper" to "Rung 1 of a lattice QCD
program: SU(2) execution and arithmetic validation."** An AI review correctly identified
every overclaim. The existing data (plaquette at β=2.3, DF64 precision, multi-vendor
agreement, autocorrelation, three-path PRNG validation) is solid. But reviewers will
want more: β-scan, increased statistics, HMC diagnostics.

**The experiment queue in `HOTSPRING_RUNG1_EXPERIMENT_QUEUE.md` is the critical path.**
Complete those 7 experiments, push results to whitePaper, and sporePrint submits.

LaTeX source: `whitePaper/subGen/lattice_qcd_consumer_gpu.tex`
Experiment queue: `wateringHole/handoffs/HOTSPRING_RUNG1_EXPERIMENT_QUEUE.md`
6-rung ladder: `wateringHole/handoffs/OVERWATCH_LATTICE_QCD_LADDER.md`

---

## What Changed (Rung 1 Reframing)

| Change | Old | New |
|--------|-----|-----|
| Title | "Vendor-Agnostic Lattice QCD..." | "**Toward** Vendor-Agnostic Lattice QCD: SU(2) HMC..." |
| Abstract | Claims 4⁴–16⁴ production | Restricted to 4⁴ and 8⁴ |
| Scope | Implicit full QCD | Explicit 6-rung ladder (Table 1) |
| Plaquette | No normalization equation | Equation 2 defines P explicitly |
| Precision | No component breakdown | Precision path matrix (Table 3) |
| Limitations | List of weaknesses | "Limitations of the Present Result" + experiment queue |
| Cost analysis | 16⁴ 10K-trajectory specific claim | Removed |
| Conclusion | "demonstrated lattice gauge theory" | "demonstrated SU(2)... Rung 1 of a lattice QCD program" |

---

## What hotSpring Needs to Deliver

### MUST COMPLETE (preprint blockers)

See `HOTSPRING_RUNG1_EXPERIMENT_QUEUE.md` for full details. Summary:

| # | Experiment | Deliverable |
|---|-----------|-------------|
| 1 | β-scan (1.8–2.5) at 8⁴ | Table: ⟨P⟩_GPU vs ⟨P⟩_CPU per β |
| 2 | 4-8 seeds × 1000 traj at 8⁴ β=2.3 | Per-chain means + bootstrap error |
| 3 | HMC diagnostics | ΔH histogram, Creutz equality, reversibility, unitarity/det drift |
| 4 | PRNG QQ plots | Gaussian QQ of GPU Box-Muller, tail stats, variance comparison |
| 5 | Plaquette normalization check | Cold start = 1, hot ≈ 0, compare vs published SU(2) data |

### SHOULD COMPLETE

| # | Experiment | Deliverable |
|---|-----------|-------------|
| 6 | 12⁴ and 16⁴ production | Plaquette + autocorrelation at larger volumes |
| 7 | pseudoSpore signed release | v1.0.0-rung1, bearDog signature, validate.sh |

---

## Handoff Protocol

1. Run experiments on strandGate (cpu_mom path, all standard volumes)
2. Push results to whitePaper repo in table format (markdown or CSV)
3. File completion AAR in `wateringHole/aars/`
4. sporePrint integrates into LaTeX + site pages
5. sporePrint runs final hype compliance review
6. arXiv submission to hep-lat (cross-list cs.DC)

---

## Key Insight

The AI review pattern: **the code is real, the comparisons are hype.** Every falsifiable
claim checked out. The framing was the problem. Fix: name what you proved (SU(2) HMC,
DF64 arithmetic, multi-vendor portability), not what you plan to prove (lattice QCD).
The experiment queue closes the gap between "promising first result" and "rigorous preprint."

---

*Rung 1. The β-scan and HMC validation are the highest priority. sporePrint
has the LaTeX ready to accept the data. Push results, file AAR, we submit.*
