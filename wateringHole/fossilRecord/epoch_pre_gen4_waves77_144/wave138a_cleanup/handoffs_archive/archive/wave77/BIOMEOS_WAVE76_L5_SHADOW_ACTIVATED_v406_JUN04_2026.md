# biomeOS — Wave 76 Handoff: L5 Perceptron Shadow Mode Activated (v4.06)

**Date**: June 4, 2026
**From**: biomeOS (southGate)
**To**: primalSpring (eastGate) — upstream audit
**Version**: v4.05 → v4.06

---

## Summary

L5 perceptron shadow mode is now **fully activated** with remote inference
wired to barraCuda via capability discovery. Every multi-provider dispatch now
runs `ml.mlp_infer` alongside L4 weighted routing, logging both decisions
without affecting actual dispatch. Falls back to local perceptron scoring if
barraCuda is unreachable.

## Changes

### Remote inference wired at startup

- `NeuralApiServer::new()` now chains `.with_remote_infer(socket_path)` on the
  `PerceptronDispatcher`, enabling remote shadow inference from first dispatch.
- The remote socket is the Neural API's own UDS — `shadow_compare_remote()`
  sends `capability.call("ml.mlp_infer")` which routes through standard
  discovery to barraCuda.

### select_primary() upgraded to async remote shadow

- `discovery_registry.rs::select_primary()` now calls `shadow_compare_remote()`
  (async, remote) when `has_remote_infer()` is true, falling back to
  `shadow_compare()` (sync, local) otherwise.
- Three-way comparison logged: L4 rule-based vs L5 local perceptron vs L5
  remote barraCuda inference.
- Graceful degradation: if `ml.mlp_infer` call fails (barraCuda offline,
  network error), falls back to local perceptron scoring with debug log.

### weight_health introspection extended

- `neural_api.weight_health` → `perceptron.remote_infer` field added (boolean).
- `NeuralRouter::perceptron_has_remote_infer()` method added.

### A/B shadow milestone

- Counter infrastructure verified working. Milestones fire at 100, 500, 1000
  multi-provider dispatches with `L4 shadow milestone` INFO logs.
- Counter resets on restart (runtime state, not persisted).
- When 1000 milestone is reached, disagreement rate between L4 (weighted) and
  legacy (first-match) is logged.

### Cross-gate composition

- All 1,339 `biomeos-atomic-deploy` tests pass.
- Gate registry, route table, and composition patterns verified compatible
  with current Songbird w76 and bearDog w137 interfaces.

## Test Status

- **4,876 tests** passing across workspace (0 failures, 18 pre-existing ignores)
- `cargo check` clean

## What's Next

1. **A/B milestone data**: When 1000-dispatch counter fires in production,
   analyze L3 vs L4 vs L5 disagreement rates and publish findings.
2. **Trained weights**: When primalSpring drops `neural_routing_perceptron.bin`,
   biomeOS auto-loads and L5 shadow compares trained vs neutral decisions.
3. **Epsilon-greedy gate**: At 1000+ L5 shadow dispatches with low
   disagreement, assess transition from `Shadow` → `EpsilonGreedy` phase.

## Blocked / Waiting

- **Training data**: primalSpring → biomeOS (training data generation for
  `neural_routing_perceptron.bin`)
- **Cross-gate mesh**: Songbird capability propagation for end-to-end test
- **Epsilon-greedy**: Gated on L5 shadow analysis results
