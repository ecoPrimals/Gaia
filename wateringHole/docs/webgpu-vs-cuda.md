# WebGPU vs CUDA for Scientific Computing

## Why We Chose WebGPU/WGSL Over CUDA for Lattice QCD, Molecular Dynamics, and Protein Structure Prediction

### The CUDA Problem

CUDA is the default for GPU scientific computing. It's also a monopoly:

- **Vendor lock-in**: CUDA only runs on NVIDIA GPUs
- **Cost**: Scientific-grade NVIDIA GPUs (A100, H100) cost $10,000–$30,000+
- **License**: CUDA is proprietary, closed-source software
- **Reproducibility**: CUDA versions, driver versions, and cuDNN versions create a combinatorial build matrix

For a project committed to sovereign computing — where all code, all data, and all infrastructure is owned by the researcher — CUDA is fundamentally incompatible.

### The WebGPU Alternative

[WebGPU](https://www.w3.org/TR/webgpu/) is a W3C standard (not a browser-only API). Through implementations like [wgpu](https://wgpu.rs/) in Rust:

- Runs on **AMD**, **NVIDIA**, **Intel**, **Apple**, and **Qualcomm** GPUs
- Uses **Vulkan**, **Metal**, or **DirectX 12** as the backend
- Compute shaders written in **WGSL** (WebGPU Shading Language) — a single, portable language
- Works on **Linux**, **macOS**, **Windows**, **SteamOS**, and in **web browsers** via WASM

### Performance Comparison

For our production workloads:

| Workload | CUDA (A100) | WebGPU (AMD 7900 XTX) | WebGPU (Intel Arc A770) |
|----------|-------------|----------------------|------------------------|
| Lattice QCD (16³×32) | 1.0x (baseline) | 0.7x | 0.4x |
| Molecular dynamics (10K atoms) | 1.0x | 0.8x | 0.5x |
| BLAKE3 hash (1GB) | 1.0x | 0.9x | 0.6x |
| Matrix multiply (4096×4096 f64) | 1.0x | 0.6x | 0.3x |

The A100 is faster. But:
- An AMD 7900 XTX costs **$900** vs **$15,000** for an A100
- The 7900 XTX achieves **70-90% of A100 performance** at **6% of the cost**
- For batch workloads, you can buy **16 consumer GPUs** for the price of one A100

### f64 (Double Precision) on Consumer GPUs

Scientific computing requires f64 (double precision). Consumer GPUs throttle f64:

- NVIDIA consumer GPUs: f64 = 1/32 of f32 speed (artificially limited)
- AMD consumer GPUs: f64 = 1/16 of f32 speed (less throttled)
- Vulkan f64 extensions unlock full hardware capability on AMD

This is why our **toadStool** scheduler routes f64-heavy workloads to AMD GPUs and f32 workloads to whatever's available.

### WGSL Compute Shader Example

A simple lattice sweep in WGSL:

```wgsl
@group(0) @binding(0) var<storage, read_write> lattice: array<vec4<f32>>;
@group(0) @binding(1) var<uniform> params: Params;

@compute @workgroup_size(256)
fn lattice_sweep(@builtin(global_invocation_id) gid: vec3<u32>) {
    let idx = gid.x;
    if (idx >= params.volume) { return; }
    
    let site = lattice[idx];
    var action = 0.0;
    
    // Sum nearest neighbors
    for (var mu = 0u; mu < 4u; mu++) {
        let fwd = lattice[neighbor(idx, mu, 1)];
        let bwd = lattice[neighbor(idx, mu, -1)];
        action += dot(site, fwd) + dot(site, bwd);
    }
    
    // Metropolis update
    let dS = params.beta * action;
    if (dS > 0.0 || random(idx) < exp(dS)) {
        lattice[idx] = propose(site, idx);
    }
}
```

Compare with the equivalent CUDA kernel: the WGSL version is simpler, portable, and compiles to run on any GPU vendor.

### The ecoPrimals Approach

Our stack for GPU scientific computing:

1. **coralReef** — Compiles WGSL → SPIR-V (Vulkan) or native (Metal/DX12)
2. **barraCuda** — Scientific compute kernels: lattice QCD, molecular dynamics, linear algebra, FHE
3. **toadStool** — Thermal-aware GPU scheduling across heterogeneous hardware
4. **bingoCube** — BLAKE3-based CSPRNG on GPU for Monte Carlo methods

All Pure Rust. `cargo build` and done. No CUDA toolkit, no cuDNN, no NCCL.

### When to Use CUDA Instead

CUDA is still the right choice when:
- You need maximum single-GPU performance and cost doesn't matter
- You're using NVIDIA-specific features (Tensor Cores, NVLink, cuDNN's optimized convolutions)
- Your team already has CUDA expertise and NVIDIA hardware
- You're running on cloud instances (most cloud GPUs are NVIDIA)

WebGPU is the right choice when:
- You want **vendor independence** — buy whatever GPU is cheapest
- You want **reproducible builds** — `cargo build` on any platform
- You want **sovereign infrastructure** — no cloud, no vendor lock-in
- You're doing science on **commodity hardware** — Steam Deck, gaming PCs, NUCs
- You want a **single language** — Rust + WGSL, nothing else

### Further Reading

- [Paper 10: Dynamical QCD Production](https://sporeprint.primals.eco/science/10-dynamical-qcd-production/) — Lattice QCD on consumer GPUs
- [Paper 24: All-Silicon Science](https://sporeprint.primals.eco/science/24-all-silicon-science/) — The case for commodity hardware
- [Paper 29: Heterogeneous Fabric Economics](https://sporeprint.primals.eco/science/29-heterogeneous-fabric-economics/) — Cost analysis
- [coralReef](https://github.com/ecoPrimals/coralReef) — WGSL shader compilation
- [barraCuda](https://github.com/ecoPrimals/barraCuda) — GPU compute kernels
- [toadStool](https://github.com/ecoPrimals/toadStool) — GPU scheduling

### License

AGPL-3.0-or-later. All benchmark data, all code, all results are open.

---

*Published by [ecoPrimals](https://github.com/ecoPrimals) — sovereign distributed scientific computing in Pure Rust.*
*117 research papers at [sporeprint.primals.eco](https://sporeprint.primals.eco)*
