# biomeGate Sovereign Dispatch — Restaged Experiment Plan

**Date:** Aug 13, 2026 | **Wave:** 157k | **Team:** biomeGate hotSpring sub-team
**Status:** RESTAGED — fresh deployment, all prior lockup vectors mitigated
**Hardware:** Threadripper 3970X, 128GB DDR4, RTX 5060 + Titan V + 2× K80
**Kernel:** 7.0.0-28-generic (PREEMPT_DYNAMIC)

---

## Current State (Post-Bootstrap)

| Component | Status | Notes |
|-----------|--------|-------|
| Tower Atomic (4/4) | ALIVE | bearDog, songBird, skunkBat, swarmVine |
| toadStool | RUNNING (source-built GNU) | Ember fleet 4/4 GPUs, PCIe keepalive active |
| coralReef | RUNNING (depot musl) | Shader compiler: sm_35/70/120 |
| barraCuda | HEALTHY (source-built GNU) | RTX 5060 via Vulkan, SHADER_F64 |
| RTX 5060 | nvidia-open Vulkan | Display GPU, stable |
| Titan V | vfio-pci (runtime) | IOMMU group 49, `/dev/vfio/49` |
| K80 fn0/fn1 | vfio-pci (runtime) | IOMMU groups 35/36 |
| Firmware (.zst) | FIXED | `NvGspBridge` now decompresses `.bin.zst` transparently |
| Boot persistence | CLEAN | Zero `/etc/modprobe.d/`, zero `/etc/modules-load.d/` |

## What We Know (Fossil Record Synthesis)

### The Tier Model

| Tier | State | Achieved? | How |
|------|-------|-----------|-----|
| 0 — Cold | Power cycle needed | N/A | Hardware line |
| 1 — WarmInfra | VFIO + BAR0 + DMA + PFIFO + channels | YES (Exp 210) | 183ms pipeline, production-grade |
| 2 — WarmCompute | GPC + CE + TPC alive → shader dispatch | YES (Exp 229 Run #9) | Catalyst warm handoff only |
| 3 — FullSovereign | Cold boot without VBIOS | Research goal | ~100 VBIOS opcodes |

### The FECS Gate (Tier 1 → Tier 2 Transition)

The dispatch pipeline (QMD, pushbuffers, GPFIFO, doorbell) is **100% implemented** in Rust.
It gates on `fecs_ready` which requires:

1. FECS falcon running (firmware executing, PC advancing) — ✅ achieved
2. FECS method protocol (INIT_CTXSW → BIND_CHANNEL → COMMIT) — ❌ blocked
3. TPC PRI stations alive (not `0xBADF5040`) — ❌ requires GPCCS firmware
4. Channel PCCSR ≥ 5 (ON_PBDMA) — ❌ stuck at PENDING_CTX_RELOAD
5. RUNLIST_BASE configured, PBDMA bound — ❌ reads as 0

### Closed Paths (Don't Re-Attempt)

| Path | Exp | Why Closed |
|------|-----|------------|
| BAR0 register writes for TPC | 217 | TPC PRI stations are firmware-mediated; 0xBADF5040 persists |
| PMU mailbox protocol | 211 | HS-locked; DMEM returns 0xDEAD5EC2 |
| PRI ringmaster enumerate | 215 | Re-registers existing stations, cannot create missing ones |
| nouveau fini patch | N/A | `gv100_gr_fini` doesn't exist; nouveau never creates TPC on Volta |

### Viable Paths (Restage These)

| Path | Exp | Status at Lockup | What Changed |
|------|-----|-----------------|-------------|
| **nouveau warm handoff** | 190 | FECS/GPCCS survived swap | Fresh system, runtime VFIO, no boot persistence |
| **nvidia-470 catalyst** | 218-219 | HW validated, 83K alive regs | Kernel 7.0 (was 6.17), nvidia-open 595 |
| **sovereign.init (ACR chain)** | 223-224 | `compute_ready: true` via NVDEC→SEC2→ACR→PMU→FECS | **Firmware .zst decompression now fixed** |
| **catalyst_boot (nouveau + replay)** | 229,234 | Tier 2 achieved Run #9; teardown unstable | Fresh captures needed; HandoffExclusionGuard improved |
| **K80 unsigned falcons** | N/A | Expected easiest path | K80 FECS/GPCCS are LS (not HS-locked) |

### Lockup Vectors (All Mitigated)

| Vector | Root Cause | Mitigation | Status |
|--------|-----------|------------|--------|
| Boot hang | Persistent VFIO in `/etc/modprobe.d/` + initramfs | Runtime-only VFIO binding | ✅ Applied |
| pci_lock deadlock | Keepalive config reads during SBR | HandoffExclusionGuard | ✅ In code |
| Interrupt storm | Quench wrote read-only INTR_EN | CLEAR register@0x180 | ✅ In code |
| Kernel corruption | nv_dev_free_stacks frees running stacks | nv_close_device RetAtEntry | ✅ In code |
| Unbind hang | nv_pci_remove polling loop | fire-and-poll unbind | ✅ In code |
| nvsov procfs collision | MODULE_NAME baked in .rodata | Expanded NOP set | ✅ In code |

---

## Restaged Experiment Plan

### Phase A: Infrastructure Validation (Non-Destructive)

These experiments run without any driver rotation or warm handoff. Safe to repeat.

#### Exp R1: Tier Classification on Fresh VFIO GPUs

Classify the sovereignty tier of each VFIO-bound GPU as-is (post-FLR cold state).

```bash
# Via toadStool RPC (once server restarted with zstd fix)
echo '{"jsonrpc":"2.0","id":1,"method":"sovereign.warm_status","params":{}}' | \
  socat - UNIX-CONNECT:/run/user/1000/biomeos/compute.sock
```

**Expected:** Tier 0 (Cold) for Titan V and K80s — FLR during VFIO binding wiped FECS.
**Purpose:** Baseline. Confirms hardware is accessible but engines are gated.

#### Exp R2: Firmware Availability Probe

Verify the zstd fix enables firmware loading for GV100.

```bash
# Via sovereign.init dry-run or direct NvGspBridge probe
echo '{"jsonrpc":"2.0","id":1,"method":"sovereign.init","params":{"bdf":"0000:21:00.0"}}' | \
  socat - UNIX-CONNECT:/run/user/1000/biomeos/compute.sock
```

**Expected:** sovereign.init should progress past "No FECS firmware found on disk" (previous blocker).
**Watch for:** ACR blob loading (acr/bl.bin.zst, ucode_load.bin.zst), GR blob loading.
**New since last run:** `.zst` decompression enabled. Previous runs silently failed on firmware read.

#### Exp R3: K80 Firmware Extraction (Unsigned Falcons)

K80's GK210 uses Kepler falcons which are **not** HS-locked. PIO upload should work
directly — CPUCTL at `0x409100`/`0x41a100` accepts `0x00000002` (start) without ACR.

**Blocker:** K80 firmware NOT present at `/lib/firmware/nvidia/gk210/` or `/gk110/`.
Desktop Kepler firmware was never published to linux-firmware. Nouveau generates it
internally from compiled-in context tables (see `nvkm/engine/gr/ctxgk110b.c`).

**Extraction options (in order of preference):**

1. **Nouveau dump (safest):** Temporarily load nouveau on K80, dump FECS/GPCCS
   firmware from falcon IMEM/DMEM via debugfs or BAR0 reads. Save as `.bin` files.
   - nouveau's `gf100_gr_init_ctxctl()` handles firmware generation + upload
   - After upload, read back from falcon IO space at `0x409000` (FECS) and `0x41a000` (GPCCS)
   - Requires: nouveau loadable alongside nvidia-open (potential kernel module conflict)

2. **GK20A firmware (might work):** `/lib/firmware/nvidia/gk20a/` contains FECS/GPCCS
   firmware for the Tegra K1 (Kepler-class). GK20A is a subset of GK110 — firmware
   MAY be compatible but likely has different GPC/TPC counts and register init values.
   - Low confidence, but zero cost to try

3. **Context table port:** Port nouveau's `ctxgk110b.c` context tables to Rust and
   generate firmware at runtime in toadStool. Most sovereign approach but highest effort.

**PIO upload sequence (from envytools + nouveau source):**
```text
1. Write firmware code words to falcon IMEM via upload port (+0x1c0..+0x1c4)
2. Write firmware data words to falcon DMEM via upload port (+0x1c8..+0x1cc)
3. Set boot vector: write entry point to +0x104
4. Start execution: write 0x00000002 to CPUCTL (+0x100)
5. Poll mailbox0 (+0x110) for ready signal
```

**Key advantage:** No ACR, no signed firmware, no PMU chain. Direct PIO boot.
**If firmware available:** Direct PIO boot should achieve Tier 2 on K80 (simplest path).

### Phase B: Sovereign Init (Cold Boot, No Driver Rotation)

These experiments use the GspBridge cold boot path — no nvidia/nouveau loading needed.

#### Exp R4: GV100 ACR Chain (sovereign.init)

Run the full NVDEC → SEC2 → ACR → PMU → FECS boot chain on the Titan V.
This is the path that achieved `compute_ready: true` in Exp 223-224.

**What's different now:**
- Kernel 7.0 (was 6.17) — VFIO/iommufd improvements
- nvidia-open 595 (was 580) — different firmware blobs
- `.zst` decompression fixed
- Runtime VFIO (no boot-persistent state)
- No FLR suppression needed (fresh cold GPU)

**Critical observation from Exp 224:** `compute_ready: true` but `tpc_status: 0xBADF5040`.
sovereign.init declared success but tier classification showed Tier 1 (WarmInfra), not Tier 2.
The init pipeline verified PTIMER/PRAMIN/PMC but didn't check TPC.

**Hypothesis to test:** With the ACR chain successfully booting FECS and GPCCS on
a cold GPU, does the FECS method protocol (INIT_CTXSW → BIND → COMMIT) succeed?
Previous attempts may have been blocked by firmware read failures (`.zst` issue).

#### Exp R5: Tier Classification After sovereign.init

After Exp R4, re-classify tier. Check `tpc_alive` specifically.

```
If tpc_alive=true → Tier 2 achieved cold! Proceed to dispatch.
If tpc_alive=false → TPC wall still present. Need catalyst (Phase C).
```

### Phase C: Nouveau Warm Handoff (Driver Rotation)

Only attempt if Phase B doesn't achieve Tier 2. This involves loading nouveau
temporarily on the Titan V, then swapping to vfio-pci.

#### Exp R6: Nouveau Seeder (Stock)

Use stock nouveau to initialize the Titan V, then warm-swap to vfio-pci.
nouveau on Volta initializes HBM2, PMC engines, falcon firmware.

**Requirements:**
- nouveau must be loadable without conflicting with nvidia-open on RTX 5060
- RTX 5060 is on nvidia-open; nouveau targets Titan V only
- `modprobe nouveau` may conflict if nvidia-open is loaded (symbol namespace)

**Potential fix:** Use `nouveau.modeset=0` or bind nouveau only to the Titan V BDF.

**Handoff sequence:**
1. Unbind Titan V from vfio-pci
2. Load nouveau (targeting Titan V only)
3. Wait for FECS/GPCCS init (settle 10s)
4. Warm swap: nouveau → vfio-pci (preserve FECS state)
5. Classify tier

**Key breakthrough from May 15:** FECS survives this swap (CPUCTL_ALIAS confirms).
**Key risk:** nouveau may not coexist with nvidia-open on the same system.

#### Exp R7: nvidia-470 Catalyst (Patched)

If nouveau doesn't work, use nvidia-470 DKMS as catalyst:

**Sequence:**
1. Build nvidia-470 DKMS patched module (nvsov)
2. Load alongside nvidia-open-595
3. Bind Titan V to nvsov
4. Wait for RM init (settle 60s)
5. Capture BAR0 snapshot (domain-scoped, 22 Volta domains)
6. Warm swap: nvsov → vfio-pci
7. Classify tier

**This achieved Tier 2 in Exp 229 Run #9** but had 7 lockups in 9 runs.
All lockup vectors have mitigations. This is the proven-but-fragile path.

### Phase D: Dispatch Validation

Once Tier 2 is achieved by any path:

#### Exp R8: Sentinel Dispatch

Upload a trivial shader (write constant `42`), dispatch on Titan V, readback.

```rust
// The exact path in code:
// device.alloc(size) → device.upload(handle, data) → device.dispatch(shader, bufs, dims, info) → device.sync() → device.readback(handle)
```

**Expected:** `42` in readback buffer.

#### Exp R9: QCD Physics Dispatch

Compile and dispatch `wilson_plaquette_f64.wgsl` via coralReef → toadStool → Titan V.

**This was validated on Jun 1** (16/19 trio tests passed) but through the wgpu/Vulkan
path on RTX 5060. Running it on the VFIO Titan V via sovereign dispatch is the goal.

---

## Experiment Priority Order

```
R1 (classify) → R2 (firmware probe) → R4 (ACR chain cold boot)
                                            ↓
                                    R5 (tier check)
                                      ↓           ↓
                              [Tier 2?]        [Tier 1?]
                                  ↓                ↓
                           R8 (dispatch)     R6 (nouveau warm)
                                  ↓                ↓
                           R9 (QCD math)     R7 (nvidia-470 catalyst)
                                               ↓
                                        R8 → R9
```

**K80 parallel track:** R3 (firmware extraction) can proceed independently.

## Online Research Findings (Aug 2026 Scan)

### New Resources Since Last Deployment

| Resource | Relevance |
|----------|-----------|
| **nova-core** (Linux 6.15+) | NVIDIA's official Rust GPU driver. Documents Falcon boot in detail (PIO vs DMA, BROM, HS modes). Turing+ only, but Falcon docs apply to all generations. [kernel.org/gpu/nova/core/falcon.html](https://docs.kernel.org/gpu/nova/core/falcon.html) |
| **LibreCuda** (mikex86) | MIT C library replacing libcuda.so. Implements GPFIFO/QMD/pushbuffer dispatch. Still requires nvidia.ko (uses RM ioctls). Validates our command format understanding. [github.com/mikex86/LibreCuda](https://github.com/mikex86/LibreCuda) |
| **Command stream paper** (Apr 2026) | Academic reverse-engineering of NVIDIA doorbell → GPFIFO → pushbuffer hierarchy via hardware watchpoints. Confirms doorbell at BAR0 `VIRTUAL_FUNCTION_DOORBELL` offset. [arxiv.org/html/2604.26889v1](https://arxiv.org/html/2604.26889v1) |
| **NVK Vulkan 1.4** (Mesa 26.2) | NVK is Vulkan 1.4 conformant for Turing+, 1.2 for Kepler. NAK compiler (Rust) handles shaders. `VK_NVX_binary_import` can load CuBIN ELFs. Requires nouveau DRM (not usable on VFIO). |
| **envytools PDF** | 543+ pages of hardware docs. PGRAPH, Falcon ISA, CTXCTL registers. Essential reference for FECS boot. [readthedocs.org/pdf/envytools/latest/envytools.pdf](https://media.readthedocs.org/pdf/envytools/latest/envytools.pdf) |
| **NVIDIA Falcon-Security docs** | Official docs on falcon security modes (LS/HS/no-sec). [nvidia.github.io/open-gpu-doc/Falcon-Security](https://nvidia.github.io/open-gpu-doc/Falcon-Security/Falcon-Security.html) |

### Key Technical Insights

1. **Kepler FECS is the easiest sovereign target.** Unsigned falcons, PIO upload,
   no ACR chain needed. Desktop Kepler firmware not in linux-firmware though.

2. **Volta FECS requires signed firmware via ACR.** The PMU → SEC2 → ACR chain
   our `sovereign.init` implements is the correct path. The `.zst` fix may unblock it.

3. **nvidia-open reveals nothing about FECS init.** It's all inside GSP-RM firmware.
   For pre-Turing chips (our Kepler/Volta), nvidia-open doesn't even compile.

4. **nouveau is the authoritative FECS reference for Kepler.** Key files:
   - `nvkm/engine/gr/gf100.c` — `gf100_gr_init_fw()`, `gf100_gr_init_ctxctl()`
   - `nvkm/engine/gr/ctxgk110b.c` — GK210 context tables
   - `nvkm/subdev/secboot/` — Volta secure boot (ACR for FECS/GPCCS)

5. **No other project does sovereign VFIO compute dispatch.** We are unique in this space.
   LibreCuda is the closest but still requires nvidia.ko for channel/memory management.

## What Changed Between Deployments

| Factor | Before (Jun 2026) | Now (Aug 2026) |
|--------|-------------------|----------------|
| Kernel | 6.17 | 7.0.0-28-generic |
| nvidia driver | nvidia-580 (proprietary) | nvidia-open-595 |
| VFIO binding | Boot-persistent `/etc/modprobe.d/` | Runtime-only `driver_override` |
| Firmware | `.bin` (probably extracted manually) | `.bin.zst` (package-managed, now decompressible) |
| IOMMU backend | iommufd/cdev | iommufd/cdev (kernel 7.0) |
| PCIe topology | Titan V at 02:00.0 | Titan V at 21:00.0 (PLX bridge) |
| Lockup mitigations | Evolving | All 7 vectors mitigated in code |
| Diesel engine lesson | Learned mid-experiment | Applied from day 0 |

## Experiment Results (Aug 13 PM Session)

### Code Fixes Applied

| Fix | File | Impact |
|-----|------|--------|
| `.zst` firmware decompression | `nv_gsp_bridge/mod.rs` | `NvGspBridge` now loads GV100 firmware from `.bin.zst` — Linux kernel 7.0 ships firmware compressed |
| D3hot→D0 wake in probe | `compute_device/warm_probe.rs` | `probe_warm_fecs` now calls `enable_bus_master()` to wake GPU from D3hot before BAR0 reads |
| PRI fault filter (warm probe) | `compute_device/warm_probe.rs` | `0xBADFxxxx` values in FECS CPUCTL/mailbox now correctly identified as PRI faults, not warm state |
| PRI fault filter (strategy) | `sovereign_strategy.rs` | `detect_falcon_warm_state` returns Cold when FECS registers show PRI fault signature |
| Permission fix | `/dev/vfio/*`, sysfs `resource0` | VFIO device nodes chowned to `biomegate`; sysfs BAR0 set to 666 (needed until re-login applies gpu-mmio group) |

### Exp R1+R2+R4+R5: Combined Results

**sovereign.init on Titan V (0000:21:00.0)** — 202ms pipeline:

| Stage | Status | Detail |
|-------|--------|--------|
| identity_probe | OK | BOOT0=0x140000a1, chip=GV100, SM70 |
| pmc_enable | OK | PMC=0x5FECDFF1 (23 engines enabled) |
| pgraph_reset | OK | PMC stable, FECS IMEM=0KB (cold) |
| cg_sweep | OK | 0 changed, 16 faulted |
| pri_recovery | OK | 7 alive, 6 faulted, recovered |
| pgob_ungating | OK | **0 GPCs alive** |
| boot_state_probe | OK | **Cold** (PRI faulted FECS) |
| memory_training | SKIPPED | HBM2 training requires power-on reset |

**Tier Classification: Tier 0 (Cold)**

- FECS PRI faulted (`0xBADFxxxx`) — GPC fabric not powered
- 0 GPCs alive — no TPC stations reachable
- HBM2 not initialized — memory training blocked
- PMC has 23 engines but PGRAPH subsystem unreachable via PRI ring
- `NvGspBridge` correctly resolved to GV100 firmware (`.zst` fix confirmed)

### Key Discovery: PRI Fault False Positives

Previous `sovereign.init` runs (Exp 223-224) reported `compute_ready: true` on cold Volta GPUs.
This was a **false positive** — the `0xBADF1020` PRI fault value in FECS CPUCTL/MAILBOX0 was
misinterpreted as "warm preserved" state (non-zero mailbox0 = firmware resident).

This means **Exp 223-224's `compute_ready: true` result was incorrect**. The GPU was cold
and PRI-faulted in those experiments too, but the warm detection didn't filter PRI faults.
The "firmware loads but compute context never becomes ready" issue was actually
"firmware never loaded because the pipeline skipped boot (thought GPU was warm)".

### Revised Tier Assessment

**Cold boot (sovereign.init) on Volta is blocked at the HBM2 wall:**
- PMC engines are partially enabled after FLR (23 engines)
- But PGRAPH/GPC/TPC are PRI-gated — the PRI ring master can't reach them
- HBM2 training (FBPA init, DRAM sequencing) requires vendor VBIOS opcodes
- Without HBM2, the GPU has no usable memory → no context, no dispatch

**This confirms the Tier model:**
- Tier 1 requires memory — sovereign.init can't get past Tier 0 without HBM2
- Tier 2 requires FECS+GPC+TPC — which requires PGRAPH power, which requires memory
- Warm handoff (nouveau/catalyst) bypasses all of this by inheriting a fully initialized GPU

### Updated Priority Order

```
Cold boot path → BLOCKED (HBM2 wall)
    ↓
Warm handoff path → REQUIRED for Volta
    ↓
R6 (nouveau warm handoff) → Next experiment
R7 (nvidia-470 catalyst) → Fallback
    ↓
R8/R9 (dispatch + QCD)
```

**K80 parallel track:** Still the most tractable sovereign target (unsigned falcons, no HBM2 training needed — GDDR5 auto-trains from VBIOS).

## Success Criteria

**Immediate:** Nouveau warm handoff achieves Tier 2 on Titan V (preserving FECS+GPC state).
**Near-term:** End-to-end QCD shader dispatch on Titan V via VFIO, zero vendor code at runtime.
**Long-term:** K80 dispatch (unsigned falcons), multi-GPU fleet dispatch, Tier 3 research.

---

*Science requires repetitions. Fresh system. Fresh captures. Every closed path documented.
Every lockup vector mitigated. The diesel engine starts cold, but the fuel is sovereign.
Today we found three bugs (zstd, D3hot, PRI faults) that were silently corrupting previous
experiment results. Now the diagnostics are honest. The HBM2 wall is real, but the warm
handoff path is proven. Next: nouveau seeder on the Titan V.*
