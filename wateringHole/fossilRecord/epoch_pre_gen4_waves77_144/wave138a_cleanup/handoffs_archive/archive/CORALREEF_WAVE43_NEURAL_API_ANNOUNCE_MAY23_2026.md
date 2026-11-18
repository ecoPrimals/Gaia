<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# coralReef — Wave 43: Neural API `primal.announce` Adoption

**Date**: 2026-05-23  
**Author**: coralReef team  
**Audit reference**: Wave 43 — Neural API `primal.announce` Adoption Blurbs (primalSpring v0.9.26)  
**biomeOS target**: v3.69 (persistent weights, utilization tracking)

---

## Summary

coralReef now sends `primal.announce` to biomeOS on startup, enabling Neural API
routing intelligence for shader compilation workloads.

## Implementation

- **Location**: `crates/coralreef-core/src/ecosystem.rs` — `send_primal_announce()`
- **Trigger**: On startup, after UDS listener is bound, alongside existing `capability.register`
- **Transport**: JSON-RPC 2.0 over Unix socket (line-delimited, same as `capability.register`)
- **Discovery**: Uses existing ecosystem socket discovery (tiered: `$BIOMEOS_ECOSYSTEM_REGISTRY` → `$DISCOVERY_SOCKET` → directory scan)

## Payload Schema

```json
{
  "jsonrpc": "2.0",
  "method": "primal.announce",
  "params": {
    "name": "coralreef-core",
    "version": "0.2.0",
    "socket": "$XDG_RUNTIME_DIR/biomeos/coralreef-core-ecoPrimal.sock",
    "capabilities": ["compile", "shader_compile", "gpu"],
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

## Fields Rationale

| Field | Value | Reasoning |
|-------|-------|-----------|
| `capabilities` | `["compile", "shader_compile", "gpu"]` | Core compiler capabilities — WGSL/SPIR-V/GLSL compilation |
| `signal_tiers` | `["node"]` | Node-level compute tier (not tower/nest/meta) |
| `cost_hints.compile` | 60.0 | General compilation — moderate CPU cost |
| `cost_hints.shader_compile` | 80.0 | Full shader pipeline (parse → IR → lower → encode) — higher |
| `cost_hints.gpu` | 100.0 | GPU binary emission (PTX/SASS/ISA) — most expensive |
| `latency_estimates.compile` | 500ms | Typical WGSL→IR compile time |
| `latency_estimates.shader_compile` | 800ms | Full pipeline with optimization passes |
| `latency_estimates.gpu` | 50ms | GPU dispatch acknowledgment (binary already compiled) |

## Test Coverage

- `ecosystem::tests::primal_announce_payload_has_required_fields` — validates all schema fields

## Downstream Impact

- biomeOS `neural_api.routing_weights` will include coralReef after announce
- `capability.call` for `compile.*` / `shader_compile.*` / `gpu.*` will route through coralReef with tracked latency
- Weight persistence means routing intelligence accumulates across restarts

## Validation

```bash
echo '{"jsonrpc":"2.0","method":"neural_api.routing_weights","params":{},"id":1}' | \
  socat - UNIX-CONNECT:$XDG_RUNTIME_DIR/biomeos/neural-api-ecoPrimal.sock
```

Should show entries for `compile.*`, `shader_compile.*`, `gpu.*` with non-default affinity after coralReef announces.

## Status

- **Complete**: Implementation, test, documentation
- **No remaining gaps**: All Wave 43 requirements satisfied for coralReef
