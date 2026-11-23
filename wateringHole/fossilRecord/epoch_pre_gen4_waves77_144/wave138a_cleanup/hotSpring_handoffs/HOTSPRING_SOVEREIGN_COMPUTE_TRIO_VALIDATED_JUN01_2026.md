# hotSpring Handoff — Sovereign Compute Trio Validated

**Date:** 2026-06-01
**Spring:** hotSpring
**Session:** S284 (Post-Primordial QCD Evolution + Hardware Validation)
**Status:** VALIDATED — sovereign compute pipeline live across hardware

---

## Summary

Completed 8-phase "Post-Primordial QCD Evolution" plan and validated sovereign compute
across the full biomeGate fleet: 2× Titan V (GV100, vfio-pci) + RTX 5060 (Blackwell,
nvidia DRM). The coralReef → toadStool → GPU dispatch pipeline is operational for
physics workloads.

## Hardware Validation Results (June 1, 2026)

### Lockup Defense Matrix — 11/11 PASSED
- All 5 diesel-engine defense mechanisms available (interrupt quench, post-exit
  quench, exclusion guard, fire-and-poll unbind, kernel sentinel)
- Watchdog running (120s timeout)
- 9 crash vectors from Exp 229/232 cataloged with defenses

### Compute Dispatch (Exp 152) — FULL PASS
- compile + submit + result + BLAKE3 witness pipeline validated
- Output hash: `b484c05f2a7dbe77a0a65e781d5ae6280f4e995d5523df6454131b2aaeed2063`

### Compute Trio Pipeline — 16/19 PASSED
- Yukawa MD force: compiled via coralReef, dispatched via toadStool, result received
- Wilson plaquette (cold lattice): compiled, dispatched, result received
- 7/9 barrier shaders compiled through coralReef
- 2 failures are upstream coralReef compiler bugs (deformed_wavefunction WGSL parse
  error; sum_reduce_subgroup copy-prop panic)

### Silicon Capabilities (RTX 5060) — 9/12 PASSED
- FMA, DF64 arithmetic, workgroup reduction all pass on Blackwell
- 2 ReduceScalarPipeline readback failures (pre-existing)

### MMIO Hardware Probes — ALL PASSED
- Titan V #1 (02:00.0): BOOT0 0x140000a1, 23 engines, PTIMER ticking
- Titan V #2 (49:00.0): BOOT0 0x140000a1, 23 engines, PTIMER ticking
- RTX 5060 (21:00.0): SHADER_F64=YES, all precision tiers

## Code Changes (This Session)

### Phase 1-8: Post-Primordial QCD Evolution (completed prior)
- Rewired 46 lattice shader include_str! to barraCuda canonical sources
- Absorbed 40 physics+MD WGSL shaders into barraCuda upstream
- Collapsed hotSpring GPU runtime → delegate to barraCuda device API
- Built preamble merge pipeline for 51 QCD shaders in barraCuda
- Built LatticeDispatchAdapter (QCD bind groups → toadStool wire format)
- Deprecated low_level/ module → toadStool RPCs
- Built TrioGpuBackend (gpu_hmc through primal compute trio)
- Created systemd units + validate_node_atomic binary

### Hardware Validation Fixes
- `complex_f64.rs`: restored minimal Complex64 fallback for IPC-only builds
- `md/shaders.rs`: added cfg(feature) gates with include_str! fallbacks for 15
  MD shader constants (default build was broken after Phase 2 absorption)
- `compute_dispatch/mod.rs`: fixed binary_b64 extraction to handle coralReef's
  byte-array response format (was expecting string, got `[u8]` array)

## Remaining Pipeline Issues (Next Evolution Targets)

1. **coralReef compiler bugs**: `deformed_wavefunction_f64.wgsl` parse error,
   `sum_reduce_subgroup_f64.wgsl` copy-prop panic → upstream coralReef fix
2. **Songbird capability gap**: advertises types `network`/`ipc` not `discovery` →
   blocks validate_node_atomic capability routing → upstream songbird evolution
3. **barracuda IPC socket naming**: launcher creates circular symlink for
   `barracuda-hotspring-validate.sock` → plasmidBin start_primal.sh fix
4. **ReduceScalarPipeline**: zero readback on RTX 5060 → barraCuda investigation
5. **Exp 234 Run #6**: sovereign warm handoff teardown/rebind path — pending reboot

## Wave 67 Alignment

- biomeGate confirmed as air-gap tester per glacial cutover plan
- Sovereign compute validated independently of mesh cutover
- Exp 234 Run #6 cleared for execution after reboot
- Upstream audit: toadStool 720/720 tests, 0 clippy warnings
- Next after Run #6: channel-adoption → shader-dispatch → full Tier 3

## Upstream Handbacks

| Target | Issue | Priority |
|--------|-------|----------|
| coralReef | `opt_copy_prop` panic on subgroup shaders | P1 |
| coralReef | WGSL parse error on math function type in deformed wavefunction | P2 |
| songbird | `discovery` capability type not advertised (uses `network`/`ipc`) | P2 |
| plasmidBin | `start_primal.sh` creates circular symlink for barracuda socket | P1 |
| barraCuda | ReduceScalarPipeline zero readback on Blackwell (SM120) | P2 |
| primalSpring | deployment_matrix.toml `biomegate.nucleus_status` still `not_deployed` | P3 |
