# Publication Pipeline Standard

**Status**: Established pattern (first instance: hotSpring QCD → arXiv hep-lat)
**Wave**: post-155n | **Date**: Aug 1, 2026
**Owns**: Shared — sporePrint (surface), science teams (data), whitePaper (drafts)

---

## Purpose

This standard defines how ecoPrimals teams produce publications. The pattern
splits work between the **sporePrint team** (public surface, framing, reproducibility)
and the **science team** (measured data, domain validation, figures). Neither
team blocks the other — both work in parallel and converge at handoff.

---

## The Two-Track Pattern

```
SCIENCE TEAM (spring)                    SPOREPRINT TEAM
─────────────────────                    ───────────────
1. Run computation on gate hardware      1. Create pseudoSpore page on site
2. Collect measured data                 2. Write arXiv scaffold in whitePaper/subGen/
3. Validate precision (DF64 vs f64)      3. Fill sporePrint-owned sections:
4. Compute observables + errors             - Introduction + motivation
5. Generate figures                         - Method (algorithm description)
6. Fill [TODO] sections in draft            - Reproducibility section
7. Write domain-specific discussion         - Cost analysis
                                            - Limitations (known)
                                         4. Create pseudoSpore bundle template
                                         5. Create verify.md page
                                         
                    ↓ HANDOFF ↓
                    
SCIENCE TEAM fills [TODO] markers in arXiv draft
sporePrint team reviews, ensures consistency with hype cleanup
Both sign off → submit to arXiv + link from sporePrint
```

---

## What sporePrint Owns (ready before handoff)

These sections are domain-independent — sporePrint writes them for every paper:

| Section | Content | Source |
|---------|---------|--------|
| Abstract | Structure + ecosystem framing | sporePrint writes shell, science team fills results |
| 1. Introduction | Motivation, prior art gap, contribution list | sporePrint + whitePaper |
| 2.3 Shader Pipeline | WGSL → naga → backend compilation | Same for all GPU papers |
| 2.4 Provenance | 5-stage chain description | Same for all papers |
| 4.1 Cost Analysis | Hardware amortization vs cloud pricing | sporePrint computes from gate data |
| 4.2 Limitations | Known constraints (precision, scale, vendor gaps) | sporePrint + science team review |
| 4.3 Vendor Neutrality | Cross-vendor argument | Same for all GPU papers |
| 5. Reproducibility | pseudoSpore URL, license, verification | sporePrint |
| 6. Conclusion | Summary (filled last, after data) | Joint |
| Appendix A | Hardware profile | sporePrint from gate heads |
| Appendix B | Data dependencies table | sporePrint |
| References | LaTeX bibliography | Joint |

### What sporePrint also delivers:

- **pseudoSpore site page** at `/pseudospore/<name>/` — live on primals.eco
- **Verification page** at `/pseudospore/verify/` — reusable across all pseudoSpores
- **pseudoSpore bundle template** — directory structure for the downloadable archive
- **llms.txt update** — AI-discoverable metadata for the new content

---

## What the Science Team Owns (handoff deliverables)

These sections require live computation on gate hardware:

| Section | Content | Format |
|---------|---------|--------|
| 2.1 Domain Method | Algorithm description (gauge action, integrator, etc.) | Markdown in draft |
| 2.2 Precision | DF64 methodology specific to this domain | Markdown + data table |
| 3.x Results (all) | Measured data tables, observable values, error bars | Markdown tables + CSV |
| 3.x Precision Validation | DF64 vs f64 comparison (ULP analysis) | Markdown table |
| 3.x Multi-Vendor | Benchmarks on non-NVIDIA GPUs | Markdown table |
| 3.x Autocorrelation | τ_int for key observables | Markdown + figure |
| 4.x Domain Discussion | Physics interpretation of results | Markdown |
| Figures | Plots (thermalization, scaling, precision) | SVG or PNG |

### Deliverable format:

Each `[TODO]` in the arXiv draft has a marker like:

```markdown
[TODO — requires hotSpring team data]

| Column A | Column B | Column C |
|----------|----------|----------|
| [pending] | [pending] | [pending] |
```

The science team replaces `[pending]` with measured values and removes the
`[TODO]` marker. No structural changes needed — just fill the cells.

---

## File Locations

| Artifact | Repo | Path |
|----------|------|------|
| arXiv draft | whitePaper | `subGen/<DOMAIN>_<TOPIC>_ARXIV.md` |
| pseudoSpore site page | sporePrint | `content/pseudospore/<name>.md` |
| Verify guide | sporePrint | `content/pseudospore/verify.md` (shared) |
| pseudoSpore bundle | (gate filesystem) | `/data/pseudospore/<name>/` |
| AAR | wateringHole | `aars/<GATE>_<TOPIC>_AAR.md` |
| Handoff | wateringHole | `handoffs/<TEAM>_<TOPIC>_HANDOFF.md` |
| Publication pattern | wateringHole | `protocols/PUBLICATION_PIPELINE_STANDARD.md` (this file) |

---

## Handoff Protocol

1. sporePrint team creates the arXiv scaffold and pseudoSpore page
2. sporePrint team files a handoff in `wateringHole/handoffs/` with:
   - Exact list of `[TODO]` sections
   - Data format expected (tables, figures, CSVs)
   - File paths in the draft
   - Deadline (if any)
3. Science team fills `[TODO]` sections in the draft
4. Science team commits to whitePaper and files completion AAR in wateringHole
5. sporePrint team reviews for consistency with hype cleanup rules:
   - No comparative superlatives without fair baselines
   - Measured numbers only (no theoretical projections)
   - Speedup claims must specify identical hardware + identical algorithm
6. Both teams sign off → submit to arXiv
7. sporePrint team updates the site page with the arXiv ID and DOI

---

## Hype Cleanup Rules (all publications)

Every publication from ecoPrimals must pass these checks:

1. **No unfair baselines**: GPU vs CPU comparisons must be same hardware, same algorithm
2. **No theoretical TFLOPS**: Use measured throughput (ops/sec, trajectories/hour)
3. **No "Nx faster than <different tool>"**: Compiled vs interpreted is parallelism, not algorithmic improvement
4. **DF64 precision stated honestly**: "~14 significant digits" not "FP64 precision"
5. **Hardware design, not vendor throttling**: FP64 ALU count is silicon, not a software restriction
6. **Every claim verifiable**: Reader can reproduce with the pseudoSpore archive

---

## First Instance: hotSpring QCD

| Item | Status | Owner |
|------|--------|-------|
| arXiv scaffold | DONE | sporePrint (`whitePaper/subGen/LATTICE_QCD_CONSUMER_GPU_ARXIV.md`) |
| pseudoSpore page | DONE | sporePrint (`content/pseudospore/hotspring-qcd-su2.md`) |
| Verify page | DONE | sporePrint (`content/pseudospore/verify.md`) |
| Handoff | DONE | sporePrint (`wateringHole/handoffs/HOTSPRING_QCD_PUBLICATION_HANDOFF.md`) |
| Plaquette data | PENDING | hotSpring team |
| Precision validation | PENDING | hotSpring team |
| Multi-vendor benchmarks | PENDING | Node Atomic team |
| Autocorrelation analysis | PENDING | hotSpring team |
| Final review + submission | PENDING | Joint |

---

*This pattern scales to every spring. wetSpring 16S pipeline → arXiv q-bio.
airSpring FAO-56 → arXiv physics.ao-ph. The scaffold is domain-independent.
The data is domain-specific. sporePrint is the publishing surface.*
