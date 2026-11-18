# biomeOS — Wave 77 Handoff: Perceptron Training Data Pipeline (v4.07)

**Date**: June 4, 2026
**From**: biomeOS (southGate)
**To**: primalSpring (eastGate) — upstream audit
**Version**: v4.06 → v4.07

---

## Summary

The gap between L4/L5 shadow routing and barraCuda `ml.mlp_train` is now
closed. Every multi-provider dispatch emits a labeled training row containing
the full 36-dim feature vector, candidate set, chosen index, L4 score, and
post-dispatch outcome (success, latency). Rows accumulate in a 10k ring
buffer and are drained via `neural_api.training_data` RPC.

Combined with v4.06's remote `ml.mlp_infer` wiring, biomeOS now has the
complete L5 perceptron pipeline:

```
select_primary() → build features → shadow_compare_remote(ml.mlp_infer)
                 → stash PendingDispatch
forward_request() → record_dispatch_outcome()
                  → complete DispatchTrainingRow → ring buffer
neural_api.training_data → drain → barraCuda ml.mlp_train
                        → neural_routing_perceptron.bin → auto-load
```

## Changes

### DispatchTrainingRow (perceptron.rs)

New struct capturing per-dispatch labeled data:

| Field | Type | Description |
|-------|------|-------------|
| `capability` | `String` | Capability domain key |
| `candidates` | `Vec<String>` | Primal names in candidate set |
| `features` | `Vec<Vec<f32>>` | 36-dim feature vectors per candidate |
| `chosen_idx` | `usize` | Index L4 selected |
| `success` | `bool` | Post-dispatch outcome |
| `latency_ms` | `u64` | Wall-clock dispatch latency |
| `l4_score` | `f64` | L4 score at selection time |
| `timestamp` | `i64` | Unix seconds |

### PendingDispatch linkage

- `select_primary()` stashes features + chosen_idx at decision time
- `record_dispatch_outcome()` matches pending by `(capability, provider)`,
  completes the training row, and appends to ring buffer
- Stale entries (>30s) auto-evicted to prevent leaks from dropped dispatches

### neural_api.training_data RPC

- Internal method (stability tier: `internal`)
- Drains all buffered rows and returns `{ rows, count, feature_dim }`
- `weight_health` now reports `training_data_buffered` count

### Ring buffer

- Max 10,000 rows — oldest evicted on overflow
- In-memory only (not persisted to redb) — training data is ephemeral
  telemetry, not operational state

## Test Status

- **1,339 tests** in `biomeos-atomic-deploy` pass (0 failures)
- `cargo check` clean (0 warnings)

## What's Next for L5

1. **primalSpring training loop**: Poll `neural_api.training_data`, feed to
   barraCuda `ml.mlp_train`, write `neural_routing_perceptron.bin`
2. **Auto-load trained weights**: biomeOS already loads from
   `$XDG_DATA_HOME/biomeos/neural_routing_perceptron.bin` at startup
3. **Epsilon-greedy gate**: After 1000+ shadow dispatches with trained
   weights, assess `Shadow` → `EpsilonGreedy` transition

## Other Cascade Items (not biomeOS)

- **bearDog auth.events.subscribe**: strandGate FRAGO acknowledged.
  Implementation in bearDog repo, not biomeOS.
- **Songbird Phase 3.5**: Ed25519 verification wiring in Songbird repo.
- **S4 auth gate**: Running autonomously on ironGate, ends ~Jun 9.
