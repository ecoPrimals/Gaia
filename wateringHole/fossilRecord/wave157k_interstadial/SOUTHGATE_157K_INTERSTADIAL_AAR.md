# southGate AAR — Wave 157k Interstadial (Aug 13 2026)

**Gate**: southGate | **Family**: 89df7a2d | **Role**: neuralSpring validation canary
**Wave**: 157k-interstadial | **From**: sporeGate foreman blurb

---

## Cascade Summary

All repos cascaded from `git.primals.eco:2222`:

| Repo | Changes |
|------|---------|
| wateringHole | +handoffs (cellMembrane debt sweep, graftGate darwin, grapheneGate, nestGate S150) |
| barraCuda | +rt_core_qcd.rs (real-time QCD kernel) |
| biomeOS | +deploy_result.toml signal graph |
| nestGate | +round_robin load balancing algorithm |
| petalTongue | +352 insertions (nestgate.io Phase 3 routes) |
| songBird | 67 files changed, 454 insertions (mesh.relay + enmeshment) |
| neuralSpring | Already up to date (our code team) |

## Depot Refresh

| Binary | Updated | Size |
|--------|---------|------|
| songBird | Aug 13 00:04 UTC → pulled | 19.5 MB |
| membrane | Aug 13 12:59 UTC → pulled | 15.7 MB |

## Key Discovery: `mesh.relay` FIXED

The new songBird binary (Aug 13 build) adds the `mesh.relay` JSON-RPC method that swarmVine needs for relay fallback. Previous error was `"unknown JSON-RPC method: mesh.relay"`. This is now **resolved**.

**Remaining issue**: swarmVine calls `mesh.relay` but doesn't include `topic` field in params. Error is now:
```
relay_error=songBird relay error: {"code":-32603,"message":"Missing required field: topic"}
```
This is a parameter format alignment issue between swarmVine (caller) and songBird (handler). Smaller fix than before — ironGate code team.

## NUCLEUS State

| Metric | Value |
|--------|-------|
| Processes | 15 (clean) |
| skunkBat | 1 (leak eliminated — was 437 overnight) |
| Sockets | 36 |
| RSS | 81 MB |
| node_id | southGate ✓ |
| songBird version | 0.2.1 |
| Mesh peers | 4 (sporeGate, eastGate, ironGate, strandGate) |
| Gossip peers | 3 (direct TCP outbound) |
| Gossip entries | 1 ingested, spreading to 3 peers |

## neuralSpring Development

**Fix pushed**: `4fa0c4c` — align GPU stage function name with capability convention.
- Renamed `stage_digester_anderson_gpu` → `stage_digester_anderson_coupling_gpu`
- Fixes `gpu_parity:struct:gpu_fn_exists:science.digester_anderson_coupling` validation check

**Validation**: 71/80 checks pass (15 skipped, 9 failures remaining):
- 3 failures: no AI provider (inference.complete) — expected, no LLM configured
- 2 failures: toadstool/compute offline (wgpu28 binary crash, strandGate fix)
- 1 failure: primal.list not in local registry (Wave 20 evolution)
- 1 failure: science_result_store needs orchestration signal
- 2 failures: songBird timeout on mesh.init/discovery.peers (connection timing)

## Observations for Topology Team

1. **Stadial #3 (SSH enrollment)**: SSH is running on southGate. Port 22 open. Key generated at `~/.ssh/id_ed25519.pub`. Ready for sporeGate to authorize.
2. **LAN IP**: We are at `192.168.4.148`. Blurb notes ".149 vs .148" discrepancy — confirm `.148` is correct.
3. **builder.serve pattern**: southGate could run `builder.serve` once SSH key is enrolled. Would enable Tower Atomic dispatch to us for validation tasks.

## Process Leak Root Cause

437 skunkbat processes accumulated overnight. Parent was biomeOS (pid confirmed). Full kill + clean restart resolved. The coralReef RAII fix prevents new leaks during normal operation, but biomeOS's previous spawn behavior (before the `ce812818` composition lifecycle fix) can still create orphans if a pre-fix biomeOS was running. Fresh restart with current binaries eliminates the issue.

---

*southGate 157k interstadial: cascade complete, songBird mesh.relay fixed (param format remaining), neuralSpring GPU parity fix pushed, 71/80 validate, SSH ready for enrollment.*
