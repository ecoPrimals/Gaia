# sporePrint — arXiv Rung 1 Reframing AAR

**Date**: 2026-08-02
**Wave**: post-155n (Publication phase)
**Gate**: eastGate (sporePrint team)
**Operator**: sporePrint/overwatch
**Task**: Refine arXiv preprint per AI review, create experiment queue, define 6-rung lattice QCD ladder

---

## Summary

An external AI agent reviewed the complete arXiv preprint and correctly
identified it as **Rung 1 of a lattice QCD program** — not a finished
QCD paper. The review was constructive: every falsifiable claim checked
out, but the framing oversold what was proven (SU(2) gauge theory, not
lattice QCD) and identified specific validation gaps.

sporePrint acted on the review: refined the paper, created an experiment
queue for hotSpring, and defined a 6-rung research program for overwatch.

---

## What the AI Review Found

### Correct (no changes needed)
- Plaquette values at β=2.3 are consistent
- Three-path PRNG isolation methodology is sound
- DF64 precision measurements are accurate
- Multi-vendor agreement (3.1×10⁻⁹ cross-GPU) is a strong result
- Cryptographic provenance architecture is legitimate

### Overscoped (fixed)
- Title implied finished QCD → retitled to "Toward Vendor-Agnostic Lattice QCD"
- Abstract claimed 4⁴ to 16⁴ production → corrected to 4⁴ and 8⁴
- Cost analysis used 16⁴ 10K-trajectory run → removed specific claim
- No explicit plaquette normalization equation → added
- No precision path matrix (which component uses what precision) → added
- Limitations framed as weaknesses → reframed as "present result" + "remaining work"

### Missing validation (experiment queue created)
- Single β value (2.3) — need scan across 1.8–2.5
- Single chains of 200 trajectories — need 4-8 seeds, 1000+ trajectories
- No HMC diagnostics (ΔH histogram, Creutz equality, reversibility)
- No comparison to published SU(2) datasets
- PRNG isolation incomplete (no QQ plots, tail statistics)
- pseudoSpore not version-frozen with signed release

---

## What sporePrint Did

### Paper Refinements
| Change | Section | Effect |
|--------|---------|--------|
| Title | Header | "Toward Vendor-Agnostic Lattice QCD on Consumer GPUs: SU(2) HMC..." |
| Scope ladder | 1.2 (new) | 6-rung table: SU(2) → SU(3) → quenched → dynamical → 2+1 → hot QCD |
| Plaquette equation | 2.1 | Explicit P = (1/6V) Σ (1/N) Re Tr U definition |
| Precision matrix | 2.2 | CPU/DF64/native-f64 per HMC component |
| 16⁴ overclaims | Abstract, 3.5 | Removed; restricted quantitative claims to 4⁴ and 8⁴ |
| Limitations | 4.3 | "Limitations of the Present Result" — honest framing |
| Validation work | 4.4 (new) | 11-item experiment table with status |
| Conclusion | 6 | Reframed around what Rung 1 proves |

### Handoffs Created
- `wateringHole/handoffs/HOTSPRING_RUNG1_EXPERIMENT_QUEUE.md` — 7 must/should experiments
- `wateringHole/handoffs/OVERWATCH_LATTICE_QCD_LADDER.md` — 6-rung program + team dependencies

### Site Pages Updated
- `pseudospore/hotspring-qcd-su2-paper.md` — updated title, abstract, review instructions
- `pseudospore/hotspring-qcd-su2-audit.md` — added Phase 7 (AI review) to audit trail

---

## What Others Need to Do

| Team | Action | Priority | Blocks |
|------|--------|----------|--------|
| **hotSpring** | Run β-scan (1.8–2.5) on strandGate | HIGH | arXiv submission |
| **hotSpring** | Run 4-8 seeds × 1000 trajectories at 8⁴ β=2.3 | HIGH | arXiv submission |
| **hotSpring** | HMC diagnostic battery (ΔH, reversibility, unitarity) | HIGH | arXiv submission |
| **hotSpring** | PRNG QQ plots and tail statistics | MEDIUM | arXiv submission |
| **hotSpring** | 12⁴ and 16⁴ full production data | MEDIUM | Paper completeness |
| **Node Atomic** | pseudoSpore version freeze + signed release | MEDIUM | Paper Section 5 |
| **barraCuda** | Confirm SU(3) matrix kernel timeline (Rung 2) | LOW | Next paper |

---

## What sporePrint Can Do Next (while waiting)

- Regenerate LaTeX when experiment data arrives
- Final hype compliance review before submission
- Update site pages with new data tables
- Begin Rung 2 paper scaffold when SU(3) work starts
- WCAG 2.2 AAA accessibility pass

---

## Key Insight

The AI review pattern holds: **the code is real, the comparisons are hype.**
The engineering (plaquette values, precision, multi-vendor, provenance) all
checked out. The framing (calling it "lattice QCD," claiming 16⁴ production)
was the problem. This is the third time this pattern has appeared. The fix
is always the same: name what you proved, not what you plan to prove.

---

## Artifacts

| Artifact | Location |
|----------|----------|
| Refined paper (markdown) | `whitePaper/subGen/LATTICE_QCD_CONSUMER_GPU_ARXIV.md` |
| Experiment queue | `wateringHole/handoffs/HOTSPRING_RUNG1_EXPERIMENT_QUEUE.md` |
| 6-rung ladder | `wateringHole/handoffs/OVERWATCH_LATTICE_QCD_LADDER.md` |
| Live paper page | `primals.eco/pseudospore/hotspring-qcd-su2-paper/` |
| Live audit trail | `primals.eco/pseudospore/hotspring-qcd-su2-audit/` |
| LaTeX source | `whitePaper/subGen/lattice_qcd_consumer_gpu.tex` |

---

*sporePrint Wave post-155n — Rung 1 reframing complete. The SU(2) result is
strong on its own merits. Name it correctly, validate it thoroughly, publish
the later rungs as the data arrives. Experiment queue is the critical path.*
