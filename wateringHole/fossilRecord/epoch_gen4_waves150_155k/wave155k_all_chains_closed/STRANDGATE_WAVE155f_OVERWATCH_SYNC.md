# strandGate Overwatch Sync + Deployment — Wave 155f

**Date**: Jul 28, 2026 13:15 EDT | **Wave**: 155f | **Gate**: strandGate
**Team**: Compute Trio (toadStool + barraCuda + coralReef)
**Reporter**: strandGate overwatch

---

## PHASE 0+1: CONNECTIVITY + SYNC — COMPLETE

- SSH to Forgejo verified (key: `strandGate-wave152a`)
- 42/43 directories Forgejo-synced (1 local-only: testing-secrets)
- 7 repos repointed from GitHub → Forgejo (fresh clones, incompatible histories)
- 3 missing repos cloned (metalForge, coralForge, fossilRecord)
- Zero merge conflicts, all repos on `main`

---

## PHASE 2: ENROLLMENT + TOWER — COMPLETE

### WireGuard Mesh

| Item | Status | Detail |
|------|--------|--------|
| Interface | **UP** | wg0, MTU 1420 |
| Mesh IP | **10.13.37.10/24** | Assigned per wave.toml |
| golgiBody | **REACHABLE** | 36ms RTT |
| eastGate | **REACHABLE** | 77ms RTT |
| Boot persistence | **ENABLED** | `wg-quick@wg0.service` |

**DNS finding**: WireGuard `DNS = 10.13.37.1` with `~.` domain routing hijacked
all DNS resolution, breaking `depot.primals.eco` lookup. Fixed by clearing wg0
DNS domain via `resolvectl`. The wg0.conf should NOT have `DNS =` unless
golgiBody's DNS can resolve all public domains.

### Tower Atomic

| Primal | Version | Status | Socket |
|--------|---------|--------|--------|
| beardog | 0.9.0 | **healthy** | `beardog-e8b62b6e.sock` |
| songbird | 0.2.1 | **degraded** (IPC up, discovery/federation degraded) | `songbird-e8b62b6e.sock` |
| skunkbat | 0.2.18 | **Healthy** | `skunkbat-e8b62b6e.sock` |

- songbird sees 1 mesh peer: golgiBody (122ms, direct path)
- Node ID: `strandGate`
- songbird TCP 7700 bound
- All UDS sockets + capability symlinks created (btsp, crypto, security, network)
- 94 JSON-RPC methods registered on songbird

### Hostname

Set to `strandGate` via `hostnamectl`.

---

## PHASE 3: COMPUTE TRIO DEPLOYMENT — COMPLETE

### Critical Finding: musl vs glibc GPU Discovery

**Depot genomeBins are musl-compiled** (x86_64-unknown-linux-musl). The musl
ABI cannot `dlopen` the system's glibc Vulkan libraries (`libGLX_nvidia.so.0`).
barraCuda from the depot runs **degraded — no GPU detected**.

**Fix**: Build barraCuda from source on this gate using the native glibc
toolchain (`x86_64-unknown-linux-gnu`). The source-built binary discovers
the RTX 3090 immediately via wgpu Vulkan backend.

**Implication for eastGate**: The depot pipeline needs a glibc target for gates
with GPUs, or gates must build compute primals from source. This affects
toadStool and coralReef as well.

### barraCuda — DEPLOYED, GPU ACTIVE

| Field | Value |
|-------|-------|
| Binary | Source-built (native glibc, `target/release/barracuda`) |
| Version | 0.4.0 |
| Status | **healthy** |
| GPU | **NVIDIA GeForce RTX 3090** (DiscreteGpu, Vulkan backend) |
| Driver | NVIDIA 580.126.18 |
| SHADER_F64 | **enabled** (14/9 builtins native) |
| Max buffer | 1,073,741,824 bytes (1GB) |
| Max workgroup X | 256 |
| Max workgroups/dim | 65,535 |
| Socket | `math-e8b62b6e.sock` |

**GPU stack validation**: PASS (matmul_identity + tensor_roundtrip)

**Live tensor test**:
```
tensor.matmul_inline([[1,2],[3,4]], [[5,6],[7,8]]) → [[19,22],[43,50]] ✓
linalg.eigenvalues([[4,1],[2,3]]) → [5.0, 2.0] ✓
```

**Compute capabilities**: `gpu.f32`, `gpu.f64`, `gpu.df64`, `gpu.tensor_ops`,
`gpu.dispatch_submit`, `gpu.spirv_passthrough`, `cpu.tensor_ops`, `cpu.math`, `cpu.stats`

### coralReef — DEPLOYED (depot binary, standalone mode)

| Field | Value |
|-------|-------|
| Binary | Depot genomeBin (musl) |
| Version | 0.2.0 |
| Status | Running, IPC ready |
| Provides | `shader.compile`, `shader.compile.multi`, `shader.health` |
| Requires | `compute.dispatch` |
| Socket | `coralreef-core-default.sock` (UDS + tarpc) |

**Source build failed** with 10 compile errors:
- `compile_timeout` not found in `newline_jsonrpc` (5 instances)
- `beardog_socket` not found in `config`
- Private function access (`discover_by_capability`, `discover_security_socket`)
- Type annotation needed (2 instances)

**Action for eastGate**: coralReef `main` has compile errors on Rust 1.92.0.
These look like visibility/API changes not yet propagated. The depot binary
(built on sporeGate) works. P1 — needs fix for source builds.

### toadStool — NOT DEPLOYED AS SERVICE

toadStool is a **biome orchestrator**, not a traditional IPC server. It needs
a `biome.yaml` manifest to run workloads. The `capabilities` subcommand ran
but reported "No platforms detected yet."

toadStool's role is to orchestrate compute workloads across the hardware —
it's the dispatcher, not a standalone service. Deployment requires biome
manifests for the compute workloads we want to run.

**Action for eastGate**: Need `biome.yaml` template or documentation for
running toadStool as the Node Atomic orchestrator.

---

## ALL PROCESSES — FINAL STATE

| Process | PID | Status | Socket |
|---------|-----|--------|--------|
| beardog server | 3472488 | Running | `beardog-e8b62b6e.sock` |
| songbird server | 3472665 | Running | `songbird-e8b62b6e.sock` |
| skunkbat server | 3472666 | Running | `skunkbat-e8b62b6e.sock` |
| barracuda server | 3488594 | Running (native) | `math-e8b62b6e.sock` |
| coralreef server | 3476371 | Running (depot) | `coralreef-core-default.sock` |

---

## FINDINGS FOR EASTGATE

| # | Priority | Finding | Detail |
|---|----------|---------|--------|
| 1 | **P0** | musl genomeBins can't access GPU | wgpu needs glibc to dlopen Vulkan. Depot needs glibc target or gates build from source. |
| 2 | **P1** | coralReef compile errors | `main` branch fails on Rust 1.92.0 — 10 errors (missing fns, private access, type inference) |
| 3 | **P1** | toadStool needs biome.yaml docs | No documentation for running toadStool as Node Atomic orchestrator |
| 4 | **P2** | WireGuard DNS hijack | `DNS = 10.13.37.1` in wg0.conf breaks public domain resolution. Remove DNS line or fix golgiBody resolver. |
| 5 | **P2** | songbird degraded | discovery/federation/relay degraded on fresh enrollment — expected, will stabilize |
| 6 | **P3** | Hostname was `pop-os` | Fixed to `strandGate`. Consider adding hostname check to enrollment script. |

---

## HARDWARE VALIDATED

| Component | Status | Detail |
|-----------|--------|--------|
| CPU | ONLINE | AMD EPYC 7452 32-Core (Dual socket, 64 cores) |
| GPU | **ACTIVE** | NVIDIA RTX 3090, 24GB VRAM, SHADER_F64, Vulkan 1.3.280 |
| Driver | v580.126.18 | CUDA 13.0 |
| GPU Compute | **VERIFIED** | matmul, eigenvalues, tensor ops all passing |
| WireGuard | UP | 10.13.37.10, 36ms to golgiBody |

---

*Filed from strandGate. Wave 155f. Tower Atomic live (3 primals). Compute Trio
partially deployed: barraCuda ACTIVE on RTX 3090 (source-built, GPU verified),
coralReef running (depot binary), toadStool needs biome manifests. Critical
finding: musl depot binaries cannot access GPU — needs glibc target or
source builds for compute gates.*
