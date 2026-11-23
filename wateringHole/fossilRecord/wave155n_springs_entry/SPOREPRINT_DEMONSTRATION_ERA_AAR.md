# AAR: sporePrint Demonstration Era Transition

**Date**: Aug 1, 2026 12:45 EDT
**Team**: sporePrint
**Wave**: post-155n
**Author**: sporePrint team (agent-assisted from eastGate overwatch)

---

## TL;DR

sporePrint transitioned from conceptual credibility surface to live demonstration
surface. 79 pages moved to foundation, pseudoSpore section created as lead nav item,
hype cleaned from 20 files, metrics refreshed (tests 101K → 116,930), 4 live dashboard
pages created, platform resume published. Site is live at primals.eco. First arXiv
paper draft (vendor-agnostic lattice QCD) written in whitePaper/subGen.

---

## What Changed

### Phase 1: Nav Triage (COMPLETE)

| Action | Count | Details |
|--------|-------|---------|
| Foundation-flagged pages | 79 | architecture (29), methodology (14), outreach (16), audience (7), products (4), technical (4), collaborators (3), vision (2) |
| Backstory sections | 36 | thesis (18), philosophy (15), story (3) — nav footer |
| Active in main nav | ~190 | lab (132), science (33), architecture (14), products (7), technical (4), getting-started (1) |
| New nav | — | **pseudoSpore** \| Lab \| Science \| Architecture \| Get Started |

### Phase 2: pseudoSpore Section (COMPLETE)

| Page | URL | Content |
|------|-----|---------|
| Data Catalog | /pseudospore/ | 38.2 GB, 11 datasets, 6 domains, 4,752 objects, 100% provenance |
| hotSpring QCD | /pseudospore/hotspring-qcd-su2/ | SU(2) HMC trajectories, 6-config lattice table, shader pipeline, bundle anatomy |
| Verification Guide | /pseudospore/verify/ | 7-step walkthrough: b3sum → CAS → DAG → spine → Ed25519 → attribution → reproduce |

### Phase 2: Live Dashboard Pages (COMPLETE — static, petalTongue-ready)

| Page | URL | Content |
|------|-----|---------|
| Gate Status | /lab/gate-status/ | 10 gates, 4 NUCLEUS, health model |
| GPU Compute | /lab/gpu-compute-live/ | DF64 benchmarks, 6-config QCD table, vendor independence |
| Provenance Dashboard | /lab/provenance-dashboard/ | 7/7 chain status, cross-platform validation |
| Depot Status | /lab/depot-status/ | 35 binaries, 3 platforms, build pipeline |

### Phase 2: Hype Cleanup (COMPLETE)

| Claim | Before | After | Files |
|-------|--------|-------|-------|
| 353× WireGuard | "353× faster than WireGuard" | "LAN topology awareness" | 5 files |
| 3.24 TFLOPS DF64 | "3.24 TFLOPS at f64 precision" | "measured: 2,130 matmul/sec, ~14 digits" | 8 files |
| 9.9× native f64 | "9.9× the throughput of native FP64" | removed (unfair comparison) | 3 files |
| Rust vs Python | "1,077× speedup" | "GPU vs single-threaded CPU (parallelism, not algorithmic)" | 2 files |
| CUDA throttle | "NVIDIA artificially restricts" | "hardware design choice (fewer FP64 ALUs)" | 2 files |

### Phase 3: Metric Refresh (COMPLETE)

`spore-validate refresh --write` synced 53 drifted metrics from live repos:

| Metric | Before | After | Notable |
|--------|--------|-------|---------|
| Total tests | 101,308 | 116,930 | toadStool: 9,193 → 24,463 (+166%) |
| skunkBat tests | 290 | 621 | +114% |
| bearDog tests | 14,019 | 15,210 | +8.5% |
| Total LOC | 3,595,463 | 3,598,358 | +0.08% |

### Other Deliverables

- **Platform Resume** at /resume/ — adapted from whitePaper/subGen/ECOPRIMAL_RESUME.md with hype-cleaned GPU section
- **CONTEXT.md** rewritten for demonstration era state
- **llms.txt** cleaned (stale 353×, page counts, test counts)
- **README.md** updated (79 foundation, correct test count)
- **All manifests regenerated**: content-manifest (345 pages), certification, entity graph
- **AAR** at specs/DEMONSTRATION_ERA_AAR.md documenting 5 external dependencies

---

## What We Need From Other Teams

| Team | Dependency | Blocks | Priority |
|------|-----------|--------|----------|
| **hotSpring** | Plaquette ⟨P⟩ values, DF64 vs f64 ULP comparison, autocorrelation τ_int | arXiv paper Sections 3.2-3.5 | HIGH — blocks first publication |
| **Node Atomic** | AMD RX 6950 XT + RTX 4060/5090 lattice benchmarks | arXiv Section 3.4 (multi-vendor proof) | HIGH |
| **biomeOS** | G22 single-process merge (steps 3-5) | Getting Started accuracy, architecture docs | MEDIUM |
| **petalTongue** | G19 Node Atomics rendering | Live dashboards (currently static) | MEDIUM |
| **cellMembrane** | J12 sub-builder IPC wire | Sovereign CI Windows pipeline docs | LOW |
| **tideGlass + Nest Atomic** | First real pseudoSpore download artifact | pseudoSpore download links on catalog page | MEDIUM |
| **eastGate ops** | southGate NUCLEUS bonding validation | Getting Started on-ramp narrative | LOW |

### Highest priority cross-team request

**hotSpring team**: We need plaquette measurements and DF64 precision data to
complete the arXiv draft. The paper structure, benchmarks, and framing are ready
in `whitePaper/subGen/LATTICE_QCD_CONSUMER_GPU_ARXIV.md`. The missing sections
are clearly marked with `[TODO]` tags. This is the path to a first ORCID/arXiv
publication for ecoPrimals.

---

## What We Delivered Without Dependencies

Everything above was completed by the sporePrint team without requiring changes
to any other repo or primal. We used:

- `spore-validate refresh --write` for metric sync (reads from local repo clones)
- `spore-validate provenance --write` for content manifest
- `spore-validate certify --emit` for certification
- `spore-validate graph --emit` for entity graph
- `zola build` for site generation
- Direct SSH to golgi for production deployment

### Deployment Note

DNS for `sporeprint.primals.eco` and `primals.eco` resolves to `[RELAY_PUBLIC]`
(original golgiBody), NOT golgi-ext (`137.184.197.151`). The golgi-ext rebuild
timer works but builds to the wrong server. Production deployment requires
direct pull + build on golgi at `/opt/ecoPrimals/sporePrint/`. The golgi-ext
timer should either be retired or DNS should be updated — this is an ops
decision for eastGate.

---

## Long-Term Goals Reached This Wave

| Goal | Status | Evidence |
|------|--------|---------|
| Site restructure (334 → <150 in main nav) | DONE | 190 active (lab bulk), 79 foundation, 36 backstory |
| pseudoSpore as front door | DONE | Lead nav item, homepage hero, data catalog live |
| Hype cleanup | DONE | 20 files, all comparative claims qualified |
| Metric freshness | DONE | 53 metrics synced, manifests regenerated |
| First arXiv draft | DONE (draft) | whitePaper/subGen/LATTICE_QCD_CONSUMER_GPU_ARXIV.md |
| Live dashboard pages | DONE (static) | 4 pages, petalTongue-ready stubs |

## Long-Term Goals Still Open

| Goal | Dependency | Path |
|------|-----------|------|
| arXiv submission | hotSpring plaquette + precision data | Fill [TODO] sections in draft |
| JOSS submission | arXiv first, then JOSS for software paper | Already in CONTEXT.md roadmap |
| Live dashboards (dynamic) | petalTongue G19 | Static pages ready, wire to pt-render |
| pseudoSpore downloads | tideGlass + lithoSpore team | Archive packaging + nestGate HTTP serving |
| Getting Started validation | southGate bonding | External deployment proof |
| WCAG 2.2 AAA | sporePrint (own work) | Pa11y integration, keyboard testing |
| CAS route registration | nestGate team | Content-addressed HTTP serving |

---

## Site Metrics (post-transition)

- **345 pages** (345 in provenance manifest)
- **617 internal links**, 0 broken
- **79 entities**, 126 edges, 0 validation errors
- **283 spore-validate tests** passing
- **Build time**: 4.4s local, 47s on golgi (slower VPS)
- **Content manifest root**: `33477282f968582c`

---

*sporePrint team scope: content, templates, spore-validate, static site.
We document what's running. We don't touch primal code.
The demonstration era is live. The first arXiv draft is ready for data.*
