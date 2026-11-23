# biomeOS v3.67 — Wave 43 Persistent Routing Weights + Utilization Tracking

**Date:** May 23, 2026
**From:** biomeOS team
**To:** primalSpring, all primal teams
**Version:** v3.67
**License:** AGPL-3.0-or-later

---

## Summary

Wave 43 calls for all primals to adopt `primal.announce` with `cost_hints` and
`latency_estimates`. This release implements the biomeOS receiving
infrastructure so those fields are actionable:

1. **Payload expansion** — `cost_hints` and `latency_estimates` now accepted
2. **Persistent routing weights** — redb-backed affinity scores per primal per capability
3. **Utilization tracking** — per-capability call count, latency, success rate
4. **Introspection routes** — `neural_api.routing_weights` and `neural_api.utilization`

---

## What Changed

### PrimalAnnouncement struct

```rust
pub struct PrimalAnnouncement {
    // ... existing fields ...
    pub cost_hints: HashMap<String, f64>,       // NEW
    pub latency_estimates: HashMap<String, u64>, // NEW
}
```

Both default to empty — backward compatible with existing announcers.

### RoutingWeightStore (`neural_router/routing_weights.rs`)

| Component | Detail |
|-----------|--------|
| Storage | redb at `$BIOMEOS_DATA_DIR/routing_weights.redb` |
| Tables | `routing_weights` (per-primal per-capability affinity), `utilization` (call counters) |
| Affinity | `success_rate / (cost × √latency)` — cheap, fast, reliable = highest |
| Update | EWMA (α=0.3) on observed latency and success rate per call |
| Persistence | Writes on every announce ingestion and call recording |
| Startup | Loads all weights + utilization from disk on router init |

### Utilization tracking

Every `capability.call` dispatch records:
- Provider primal name (from routing trace)
- Capability domain
- Call latency (ms)
- Success/failure

This feeds the EWMA weight update and the `neural_api.utilization` route.

### New routes

| Route | Aliases | Returns |
|-------|---------|---------|
| `routing_weights` | `neural_api.routing_weights` | `{ weights: [...], count }` |
| `utilization` | `neural_api.utilization` | `{ utilization: [...], count }` |

### Provider selection

`RoutingWeightStore::best_provider(capability)` returns the primal with highest
affinity for a capability domain. Currently exposed for consumer querying;
integration into `try_registry_lookup` for automatic weight-based selection is
the next evolution step.

---

## Validation

```bash
# After a primal announces with cost_hints:
echo '{"jsonrpc":"2.0","method":"neural_api.routing_weights","params":{},"id":1}' | \
  socat - UNIX-CONNECT:$XDG_RUNTIME_DIR/biomeos/neural-api-ecoPrimal.sock

# After capability.call dispatches:
echo '{"jsonrpc":"2.0","method":"neural_api.utilization","params":{},"id":2}' | \
  socat - UNIX-CONNECT:$XDG_RUNTIME_DIR/biomeos/neural-api-ecoPrimal.sock
```

---

## Test Results

- `routing_weights` unit tests: 4/4 pass (ingest, utilization, provider selection, affinity degradation)
- `biomeos-atomic-deploy` lib: 1280/1280 pass
- Signal dispatch: 11/11 pass
- Neural API routing: 27/27 pass
- Clippy: 0 warnings

---

## For Primal Teams

biomeOS is ready to receive your `primal.announce` with `cost_hints` and
`latency_estimates`. Follow the Wave 43 blurb for your primal's specific
fields. Weight persistence means routing intelligence accumulates across
restarts.

Example announce payload with new fields:

```json
{
  "method": "primal.announce",
  "params": {
    "primal": "beardog",
    "socket": "/run/user/1000/biomeos/beardog-ecoPrimal.sock",
    "capabilities": ["crypto", "security"],
    "methods": ["crypto.encrypt", "crypto.hash", "security.verify"],
    "signal_tiers": ["tower"],
    "cost_hints": { "crypto": 5.0, "security": 10.0 },
    "latency_estimates": { "crypto": 2, "security": 15 }
  }
}
```
