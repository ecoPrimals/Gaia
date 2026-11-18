# wetSpring Sovereign Pipeline — lithoSpore Braid Handoff

**Date:** May 17, 2026 (PM)
**Author:** wetSpring workstream
**Audience:** lithoSpore, primalSpring, Barrick Lab, Lenski Lab
**Status:** Active — ongoing artifact production
**License:** AGPL-3.0-or-later

---

## Summary

wetSpring has deployed a **sovereign Rust resequencing pipeline** that replaces
breseq (C++) with pure Rust modules composing barraCuda GPU primitives. The
pipeline produces ferment transcript braids for lithoSpore from real LTEE data.

This is an **ongoing artifact** — braids are regenerated as the pipeline evolves,
creating a living provenance chain for the Lenski and Barrick labs' datasets.

---

## What Ships

### Barrick 2009 — Ferment Transcript Braid (READY)

| Field | Value |
|-------|-------|
| Dataset | Barrick et al. *Nature* 461, 1243–1247 (2009) |
| Accession | SRP001569 (7 clones: REL1164M → REL10926) |
| Braid ID | `braid-sovereign-barrick2009` |
| Substrate | GPU+CPU hybrid (RTX 4060 f64 native) |
| Pipeline | FM-index → SmithWatermanGpu → Tensor::scan → SnpCallingF64 |
| Location | `provenance/braids/barrick_2009_sovereign.json` |

Wire format matches the lithoSpore contract:

```json
{
  "dataset_id": "barrick_2009_sovereign_resequencing",
  "spring": "wetSpring",
  "spring_version": "0.1.0",
  "braid_id": "braid-sovereign-barrick2009",
  "dag_session_id": "dag-wetspring-sovereign-...",
  "computation": {
    "tool": "wetspring-sovereign-pipeline",
    "substrate": "GPU+CPU hybrid",
    "pipeline": "FM-index → SmithWatermanGpu → Tensor::scan → SnpCallingF64",
    "input_accession": "SRP001569",
    "node_count": 7,
    "sovereign_variants": ...,
    "breseq_variants": ...,
    "position_matches": ...
  }
}
```

### Barrick 2009 — breseq Baseline Braid (READY)

| Field | Value |
|-------|-------|
| Tool | breseq 0.40.1 |
| Braid | `provenance/braids/barrick_2009_breseq.json` |
| Mutations | REL1164M: 579, REL8593M: 1108, REL10926: 2296 |

### Tenaillon 2016 — IN PROGRESS

| Field | Value |
|-------|-------|
| Dataset | Tenaillon et al. *Nature* 536, 165–170 (2016) |
| Accession | SRP064605 (312 SRR runs, 264 genomes) |
| Status | Downloading (42/312 accessions cached) |
| Pipeline | Same sovereign pipeline, will produce braid on completion |

---

## Sovereign Pipeline Architecture

The pipeline is entirely sovereign Rust — no external C/C++ tools in the
critical path. breseq serves as a **validation baseline** (Tier 1), not a
dependency.

### Modules

| Module | Function | GPU Composition |
|--------|----------|-----------------|
| `io::fasta` | Reference genome I/O | — |
| `io::fastq` | Read I/O (plain + gzip) | — |
| `io::sam` | Alignment interchange | — |
| `bio::ref_index` | FM-index (SA-IS) | CPU only (inherently sequential) |
| `bio::read_mapper` | Seed-and-extend mapping | `SmithWatermanGpu` (long reads) |
| `bio::pileup` | Depth accumulation | `Tensor::scan` (prefix sum) |
| `bio::variant_caller` | SNP/indel detection | `SnpCallingF64` (column-parallel) |

### Dispatch Model

Smart substrate routing — each pipeline stage runs on the optimal substrate:

- **CPU**: FM-index build, short-read mapping (GPU per-pair overhead exceeds compute for 36bp reads)
- **GPU**: Coverage scan (Tensor::scan), SNP calling (SnpCallingF64)
- **Future**: Long-read mapping via batched SmithWatermanGpu, HmmBatchForwardF64 for genotype refinement

This is **toadStool-compatible** — when toadStool dispatch is live, the routing
becomes dynamic rather than compile-time `#[cfg(feature = "gpu")]`.

---

## Ongoing Artifact Model

This pipeline is designed as a **living artifact** for the Barrick and Lenski labs:

1. **Reproducibility**: Every run exports a ferment transcript braid with
   computation provenance (tool version, substrate, wall time, hash)
2. **Evolution**: As the pipeline improves (better variant calling, GPU
   acceleration for new stages), new braids supersede old ones with full
   lineage
3. **Cross-tier parity**: Sovereign variants are compared position-by-position
   against breseq baselines. Parity improves as depth increases.
4. **Portability**: lithoSpore carries the braid on USB; the full computation
   stays on NUCLEUS. Anyone can verify the transcript matches the published data.

### Regeneration

```bash
# Full-depth sovereign pipeline with GPU acceleration
cargo run --features gpu --bin validate_sovereign_resequencing --release

# Subsample for quick iteration
WETSPRING_MAX_READS=50000 cargo run --features gpu --bin validate_sovereign_resequencing --release
```

---

## What lithoSpore Should Do

1. **Ingest** `barrick_2009_sovereign.json` as a new upstream braid
   alongside the existing breseq braid
2. **Display** both braids in the guideStone — sovereign (GPU+CPU hybrid)
   and baseline (breseq C++) — showing the evolution from external tools
   to sovereign Rust composition
3. **Validate** that the sovereign braid's `computation.input_accession`
   matches the expected SRP001569
4. **Prepare** for `tenaillon_2016_sovereign.json` (same wire format,
   larger node_count)

---

## What primalSpring Should Know

- `SmithWatermanGpu` per-pair dispatch is too slow for short reads (36bp).
  Batched dispatch API would unlock GPU for mapping. Filed as evolution note.
- `Tensor::scan` and `SnpCallingF64` work well for downstream stages where
  the parallelism granularity (positions, not reads) maps to GPU threads.
- `domain-genomics` feature gate was added to wetSpring's `gpu` feature to
  access `SmithWatermanGpu`, `SnpCallingF64`, and related bio ops.
- SA-IS suffix array construction was refactored to use integer alphabets
  (`&[usize]`) instead of `&[u8]` to handle recursive name spaces exceeding
  256 symbols on real genomes.

---

## Related Documents

- `experiments/382_sovereign_resequencing_barrick_2009.md` — Exp382 spec
- `experiments/381_breseq_barrick_2009_nest_atomic.md` — Exp381 breseq baseline
- `whitePaper/gen4/compute_aware_scheduling.md` — substrate dispatch rationale
- `infra/wateringHole/handoffs/LITHOSPORE_FERMENT_TRANSCRIPT_BRAID_HANDOFF_MAY17_2026.md` — braid contract
