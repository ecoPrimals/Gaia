# strandGate End-to-End Science Pipeline — Upstream Needs

**Date**: Aug 10, 2026 | **From**: strandGate | **To**: overwatch, ironGate, sporePrint, pepti
**Context**: First end-to-end project in the ecosystem — hotSpring QCD → preprint → pseudoSpore → reviewer

---

## ARCHITECTURE: Paper as Downstream Artifact

The arXiv preprint is NOT the science — it's a **view** over live data braids.

```
GPU (AMD/NVIDIA)  →  production_v2/*.json   →  arxiv_analysis.rs (Rust)
                           │                         │
                           │                    ┌────┴────┐
                           │                    │ markdown │ → paper sections
                           │                    │ json     │ → pseudoSpore manifest
                           │                    │ validate │ → CI gate
                           │                    └─────────┘
                           │
                           ├─→ pseudospore_manifest (bearDog Ed25519)
                           │         │
                           │         ├─→ westGate CAS (data braid, immutable)
                           │         └─→ ironGate NFT (provenance braid, verifiable)
                           │
                           └─→ sporePrint page (live interactive view)
                                     │
                                     └─→ external reviewer (browser API access)
```

**Key principle**: No Python. No shell scripts. All Rust binaries. All primal systems.
Deterministic, auditable, reproducible from source.

---

## WHAT STRANDGATE HAS BUILT (this session)

| Component | Binary | Status |
|-----------|--------|--------|
| Production data generation | `arxiv_production_campaign.rs` | 24/45 running |
| Analysis pipeline | `arxiv_analysis.rs` | COMPLETE (--markdown, --json, --validate) |
| GPU HMC engine | `gpu_hmc/streaming.rs` | Validated (DF64, Omelyan 2MN) |
| Observable battery | `wilson.rs` (plaquette, Polyakov, Wilson loops, Creutz) | Validated |

---

## WHAT STRANDGATE NEEDS FROM UPSTREAM

### From ironGate (NFT/results store)

| Need | Description | Blocks |
|------|-------------|--------|
| **NFT registration endpoint** | Register signed pseudoSpore bundle as NFT on ironGate | Reviewer access to provenance |
| **`/pseudospore/<hash>` route** | Serve pseudoSpore bundles at public URL cited in paper | arXiv submission |
| **Verification page** | HTML page showing BLAKE3 tree, Ed25519 sig, DAG lineage | Reviewer trust |

### From golgiBody / pepti layers

| Need | Description | Blocks |
|------|-------------|--------|
| **`validate.sh` → Rust binary** | Bundle verification tool (BLAKE3 + DAG + Ed25519) — should be a Rust binary in the pseudoSpore bundle, not a shell script | Self-verification |
| **Depot binary for `pseudospore_manifest`** | Needs rebuild + depot push from sporeGate | Bundle generation |

### From sporePrint (public face)

| Need | Description | Blocks |
|------|-------------|--------|
| **QCD Rung 1 page** | Interactive data view: plaquette vs β, volume convergence, Wilson loops | Reviewer engagement |
| **Download route** | `.tar.gz` pseudoSpore bundle download from sporePrint domain | Paper citation URL |
| **LaTeX→web** | Preprint viewable in browser (not just PDF download) | Reviewer convenience |

### From petalTongue (visualization)

| Need | Description | Blocks |
|------|-------------|--------|
| **Data visualization capability** | Read production_v2 JSON, render plaquette evolution, β-scan curves | sporePrint integration |
| **WebGL scene for lattice** | 3D lattice visualization with plaquette coloring | Science outreach |

### From squirrel (agentic layer)

| Need | Description | Blocks |
|------|-------------|--------|
| **LAN AI access** | Allow local AI (IDE agent) to query/validate data programmatically | Development workflow |
| **External reviewer mode** | Browser API allowing a separate AI instance to independently audit the data, code, and provenance chain as a hostile analyst | Pre-submission QA |
| **Agent panel** | WebSocket → petalTongue → squirrel live wiring for science monitoring | Campaign oversight |

### From bearDog (cryptography)

| Need | Description | Blocks |
|------|-------------|--------|
| **Ed25519 signing ceremony** | Sign the final pseudoSpore manifest with project key | Bundle integrity |
| **`crypto.sign_ed25519` live** | Already in depot — needs validation on strandGate | Automation |

---

## REVIEWER INTERACTION MODEL

```
Reviewer (Murillo/Bazavov/Chuna)
    │
    ├─→ sporePrint page (browse data interactively)
    │
    ├─→ pseudoSpore download (full reproducibility bundle)
    │         ├─ production_v2/*.json (raw time series)
    │         ├─ arxiv_analysis (Rust binary, deterministic)
    │         ├─ validate (BLAKE3 + Ed25519 verification)
    │         └─ MANIFEST.toml (provenance metadata)
    │
    ├─→ nestgate.io (provenance dashboard, DAG visualization)
    │
    └─→ arXiv PDF (static snapshot, cites all URLs above)
```

**External AI reviewer mode**: A separate AI instance (via squirrel browser API) can:
1. Pull the pseudoSpore bundle
2. Read all JSON time series
3. Independently compute statistics (verify our analysis)
4. Check autocorrelation times
5. Validate thermalization (are 500 warmup trajectories sufficient?)
6. Compare against literature it knows
7. Report findings as a hostile/independent review

This is not the IDE agent reviewing its own work — it's a fresh instance with no context, acting as an adversarial analyst.

---

## CURRENT SCIENCE STATUS

| Metric | Value |
|--------|-------|
| Configs complete | 24/45 (campaign running) |
| DF64 systematic | ~1-3% below native FP64 literature |
| Volume convergence | PASS (monotonic increase 16⁴→24⁴) |
| Acceptance rates | 88-95% (16⁴), 63-72% (24⁴) |
| Creutz ratios | Physical (decrease with β, consistent with asymptotic freedom) |
| ETA for 32⁴ | ~4-5 hours remaining |

---

## EXECUTION ORDER

1. **NOW**: Campaign completes (background, ~5h)
2. **NOW**: Analysis binary validates data as it arrives
3. **NEXT**: `arxiv_analysis --json` → pseudoSpore manifest input
4. **NEEDS UPSTREAM**: bearDog signs manifest → ironGate registers NFT
5. **NEEDS UPSTREAM**: sporePrint wires QCD page to data
6. **NEEDS UPSTREAM**: petalTongue renders interactive views
7. **NEEDS UPSTREAM**: squirrel wires reviewer API
8. **FINAL**: Paper sections regenerated from `arxiv_analysis --markdown`

---

*strandGate is the first end-to-end project. The pattern we establish here becomes the template for all science in the ecosystem. Every number in the paper traces to a JSON file, every file traces to a GPU run, every run traces to a signed binary commit. The paper is just a face — the braids are the science.*
