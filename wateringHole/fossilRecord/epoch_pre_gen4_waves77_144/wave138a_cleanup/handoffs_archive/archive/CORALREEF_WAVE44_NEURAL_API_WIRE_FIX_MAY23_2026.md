<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# coralReef — Wave 44: Neural API Wire Identity Fix

**Date**: 2026-05-23  
**Author**: coralReef team  
**Audit reference**: Wave 44 — Neural API Announce Fix Blurbs (primalSpring v0.9.26)  
**Priority**: P0 — wire broken (biomeOS silently rejects payload)

---

## Bug

`send_primal_announce()` in `ecosystem.rs` sent `"name"` as the identity field.
biomeOS `PrimalAnnouncement` struct requires the field be called `"primal"`.
The payload was silently rejected, so coralReef never appeared in
`neural_api.routing_weights`.

Additionally, no `methods` array was included, leaving `methods_registered = 0`
in biomeOS utilization tracking.

## Fix

1. Renamed `"name": config::PRIMAL_NAME` → `"primal": config::PRIMAL_NAME`
2. Added `"methods": ANNOUNCED_METHODS` — 16 served method names from the IPC surface
3. Added `"pid": std::process::id()` for utilization tracking
4. Updated test to assert `"primal"` field, non-empty `methods`, and `pid` presence

## Wire Payload (after fix)

```json
{
  "jsonrpc": "2.0",
  "method": "primal.announce",
  "params": {
    "primal": "coralreef-core",
    "version": "0.2.0",
    "pid": 12345,
    "socket": "$XDG_RUNTIME_DIR/biomeos/coralreef-core-ecoPrimal.sock",
    "capabilities": ["compile", "shader_compile", "gpu"],
    "methods": [
      "shader.compile.spirv",
      "shader.compile.wgsl",
      "shader.compile.status",
      "shader.compile.capabilities",
      "shader.compile.wgsl.multi",
      "shader.compile.gemm",
      "health.check",
      "health.liveness",
      "health.readiness",
      "health.version",
      "identity.get",
      "capability.list",
      "btsp.negotiate",
      "auth.check",
      "auth.mode",
      "auth.peer_info"
    ],
    "signal_tiers": ["node"],
    "cost_hints": {
      "compile": 60.0,
      "shader_compile": 80.0,
      "gpu": 100.0
    },
    "latency_estimates": {
      "compile": 500,
      "shader_compile": 800,
      "gpu": 50
    }
  },
  "id": 3
}
```

## Validation

After fix, coralReef should appear in `neural_api.routing_weights` with
non-default affinity for `compile.*`, `shader_compile.*`, `gpu.*` domains.
`neural_api.utilization` should show 16 registered methods.

## Reference

Used rhizoCrypt `niche.rs` `announce_payload()` and sweetGrass `neural_announce.rs`
as reference patterns per the Wave 44 blurb.

## Status

- P0 wire fix: **complete**
- Test coverage: **complete** (assert `"primal"` not `"name"`, methods non-empty)
- No remaining Wave 44 gaps for coralReef
