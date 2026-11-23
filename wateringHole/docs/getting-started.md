# Getting Started with Sovereign Scientific Computing in Pure Rust

## No CUDA. No Cloud. No Vendor Lock-in.

This guide introduces the ecoPrimals approach to scientific computing: everything runs on commodity hardware you already own, using Pure Rust and WebGPU/WGSL for GPU compute. No NVIDIA monopoly. No cloud bills. No data leaving your network.

## The Problem

Scientific computing has become captured:

- **GPU compute** requires CUDA → NVIDIA lock-in → $10,000+ hardware
- **Cloud computing** requires AWS/GCP/Azure → per-hour billing → data sovereignty loss
- **Software stacks** require Python + C + Fortran + CUDA → 4 languages, 3 compilers, untraceable bugs
- **Reproducibility** is theoretical because builds depend on specific OS, library, and driver versions

## The ecoPrimals Solution

One language. One build system. Any GPU vendor. Your hardware.

### WebGPU/WGSL Instead of CUDA

[WebGPU](https://www.w3.org/TR/webgpu/) is a W3C standard for GPU computing that works on:

- **AMD** GPUs (including integrated Radeon)
- **NVIDIA** GPUs (without CUDA)
- **Intel** GPUs (including integrated)
- **Apple** Silicon (M1/M2/M3/M4)
- **Qualcomm** Adreno (mobile/embedded)

WGSL (WebGPU Shading Language) replaces CUDA kernels. Your compute shaders run on any vendor's hardware through the same API.

### What We Compute

| Domain | Status | Papers |
|--------|--------|--------|
| **Lattice QCD** | Production | Papers 10, 34 |
| **Molecular Dynamics** | Production | Papers 25, 83 |
| **Protein Structure Prediction** | Active | Papers 53, helixVision |
| **Pharmacometrics** | Active | Papers 13, 22 |
| **Shannon Entropy Phenotyping** | Production | Papers 48, 90 |
| **Linear Algebra (f64)** | Production | barraCuda core |
| **Fully Homomorphic Encryption** | Experimental | barraCuda FHE module |

### The 16 Primals

The ecosystem is 16 Rust crates that compose like biological organisms:

| Primal | Role | Analogy |
|--------|------|---------|
| **biomeOS** | Orchestration kernel | Operating system |
| **songBird** | Mesh networking | Nervous system |
| **skunkBat** | Network defense | Immune system |
| **toadStool** | GPU/NPU/CPU dispatch | Metabolism |
| **coralReef** | Shader compilation | Protein synthesis |
| **barraCuda** | GPU compute | Mitochondria |
| **bingoCube** | Entropy/randomness | DNA replication |
| **bearDog** | Cryptography | Cell membrane |
| **nestGate** | Content-addressed storage | Long-term memory |
| **rhizoCrypt** | DAG provenance | Ancestry tracking |
| **loamSpine** | Computation lineage | Fossil record |
| **squirrel** | AI coordination | Prefrontal cortex |
| **sweetGrass** | Attribution engine | Immune memory |
| **petalTongue** | Visualization | Sensory organs |
| **cellMembrane** | Deployment layer | Skin |
| **sourDough** | Shared primitives | Amino acids |

## Quick Start

```bash
# Clone the ecosystem
git clone https://github.com/ecoPrimals/biomeOS.git
cd biomeOS

# Build everything (Pure Rust, no other dependencies)
cargo build --release

# Run the test suite
cargo test --workspace
```

## Hardware Requirements

- **Minimum**: Any x86_64 or ARM64 Linux system with 8GB RAM
- **Recommended**: AMD/NVIDIA/Intel GPU with Vulkan support
- **Tested on**: SteamOS (Steam Deck), Ubuntu, Fedora, NixOS, Debian
- **Not required**: CUDA, Docker, Kubernetes, cloud accounts

## Research

117 research papers documenting every design decision, algorithm, and validation result:

📖 **[sporeprint.primals.eco](https://sporeprint.primals.eco)** — the full paper archive

Key papers for newcomers:
- [Paper 1: Anderson QS](https://sporeprint.primals.eco/science/01-anderson-qs/) — The founding hypothesis
- [Paper 78: Deploy Your Own Membrane](https://sporeprint.primals.eco/science/78-deploy-your-own-membrane/) — How to set up your own node
- [Paper 90: The Evolutionary Sort](https://sporeprint.primals.eco/science/90-the-evolutionary-sort/) — Shannon entropy classification of 45,470 files
- [Paper 117: The Primal Reclassification](https://sporeprint.primals.eco/science/117-the-primal-reclassification/) — Defense as recognition

## License

Everything is **AGPL-3.0-or-later**. If you use it, your users get the source. If an AI trains on it, the copyleft travels with the knowledge.

## Links

- 🔭 [HUD](https://hud.primals.eco) — Live membrane observation surface
- 📖 [sporePrint](https://sporeprint.primals.eco) — 117 research papers
- 🧬 [ORCID](https://orcid.org/0009-0004-2141-0321) — Author profile
- 💬 Discord: `.tamison`
- 🎮 Steam: `76561198002558137`
