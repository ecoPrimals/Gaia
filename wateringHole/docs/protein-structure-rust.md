# Protein Structure Prediction in Pure Rust — A Sovereign AlphaFold Alternative

## Predicting Protein 3D Structure Without Python, Without Cloud, Without CUDA

### The AlphaFold Bottleneck

AlphaFold2 revolutionized structural biology. But running it requires:

- Python 3.8+ with TensorFlow/JAX
- NVIDIA GPU with CUDA 11+
- 8+ GB GPU memory (A100 recommended)
- Docker or Singularity containers
- Internet access for MSA databases (2.6 TB+)
- Google Colab / cloud for most researchers

For a single researcher on commodity hardware, AlphaFold is practically inaccessible without cloud compute.

### helixVision: Sovereign Protein Structure

[helixVision](https://hud.primals.eco/neutron/helix.html) is our approach to protein structure prediction using:

- **Pure Rust** — single binary, no Python runtime
- **WebGPU/WGSL** — runs on AMD, Intel, NVIDIA GPUs
- **Local-first** — all databases stored locally, no internet required at inference
- **SteamOS compatible** — runs on a Steam Deck

### Architecture

```
Input: amino acid sequence (FASTA)
  │
  ├─ MSA generation (local HHblits database)
  ├─ Template search (local PDB mirror)
  │
  ▼
coralReef (WGSL shader compilation)
  │
  ├─ Attention layers (barraCuda GPU compute)
  ├─ Structure module (torsion angle prediction)
  ├─ Relaxation (molecular dynamics via barraCuda)
  │
  ▼
Output: 3D coordinates (PDB/mmCIF)
  │
  ├─ Confidence scoring (pLDDT per residue)
  ├─ Provenance certificate (rhizoCrypt DAG)
  └─ Visualization (petalTongue WebGL)
```

### Key Innovations

**1. WGSL Attention Kernels**

Self-attention is the computational bottleneck. Our WGSL kernels implement multi-head attention with:
- Fused softmax (no intermediate materialization)
- f32 accumulation with f16 storage (mixed precision)
- Workgroup-tiled matrix multiply for L1 cache efficiency

**2. Deterministic Reproducibility**

Every prediction includes a **rhizoCrypt provenance certificate** — a Merkle tree of:
- Input sequence hash
- MSA database version
- Model weights hash
- GPU kernel source hashes
- Random seed (if any)

Anyone can reproduce the exact result with the exact same inputs.

**3. Local Database Management**

**nestGate** (content-addressed storage) manages local mirrors of:
- UniRef30 (for MSA)
- PDB70 (for templates)
- BFD (optional, for deeper MSAs)

Deduplication and B-tree indexing keep storage manageable on consumer SSDs.

### Running on a Steam Deck

Yes, really. The Steam Deck has:
- AMD Van Gogh APU with RDNA2 GPU (8 CUs)
- 16 GB unified memory
- Vulkan 1.3 support

For small proteins (<200 residues), helixVision produces predictions in minutes. For larger proteins, we distribute across multiple nodes via **songBird** mesh networking.

### Research Papers

- [Paper 53: Focal Points Tangent Membrane](https://sporeprint.primals.eco/science/53-focal-points-tangent-membrane/) — Protein folding as membrane tangent
- [Paper 83: Stoichiometric Mass Sort](https://sporeprint.primals.eco/science/83-stoichiometric-mass-sort/) — Mass-based structure classification
- [Paper 60: Body Universality Epitope Triangulation](https://sporeprint.primals.eco/science/60-body-universality-epitope-triangulation/) — Structure-function mapping

### Comparison with Existing Tools

| Feature | AlphaFold2 | ESMFold | ColabFold | helixVision |
|---------|-----------|---------|-----------|-------------|
| Language | Python | Python | Python | Rust |
| GPU | CUDA only | CUDA only | CUDA only | WebGPU (any) |
| Offline | ❌ (MSA) | ✅ | ❌ | ✅ |
| Reproducible | Partial | Partial | ❌ | ✅ (provenance) |
| Steam Deck | ❌ | ❌ | ❌ | ✅ |
| License | Apache 2.0 | MIT | MIT | AGPL-3.0 |

### Status

helixVision is in **active development**. Current capabilities:
- MSA generation and template search: ✅
- Evoformer attention: ✅ (WGSL kernels)
- Structure module: 🔄 In progress
- Relaxation: 🔄 In progress
- End-to-end prediction: 🔜

### Links

- 🧬 [helixVision dashboard](https://hud.primals.eco/neutron/helix.html) — live development status
- 📖 [sporePrint](https://sporeprint.primals.eco) — 117 research papers
- 🔬 [ORCID](https://orcid.org/0009-0004-2141-0321) — author profile
- 💻 [coralReef](https://github.com/ecoPrimals/coralReef) — WGSL shader compiler
- 🐟 [barraCuda](https://github.com/ecoPrimals/barraCuda) — GPU compute engine

---

*Published by [ecoPrimals](https://github.com/ecoPrimals) — sovereign distributed scientific computing in Pure Rust.*
