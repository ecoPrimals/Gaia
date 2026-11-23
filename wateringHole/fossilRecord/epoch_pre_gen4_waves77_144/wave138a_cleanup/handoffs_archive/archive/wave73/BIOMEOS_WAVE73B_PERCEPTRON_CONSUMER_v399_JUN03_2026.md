# biomeOS Wave 73b Handoff — Perceptron Consumer Interface

**Date**: 2026-06-03
**Version**: v3.99
**Author**: southGate (biomeOS)
**For**: primalSpring observatory, strandGate (barraCuda), eastGate

---

## Delivered

### L5 Perceptron Consumer Interface (P2)
- **Module**: `crates/biomeos-atomic-deploy/src/neural_router/perceptron.rs`
- **Feature vector**: 36-dim f32 array (32 one-hot domain + 4 numeric per-provider)
- **Weight format**: 37 f32 values (36 weights + 1 bias), little-endian binary file
- **Weight file**: `$XDG_DATA_HOME/biomeos/neural_routing_perceptron.bin`
- **Shadow mode**: perceptron runs alongside L4 weighted routing in `select_primary()`
- **Logging**: `L5 perceptron shadow [n]` at INFO, milestones at 100/500/1000/5000n
- **RPC**: `neural_api.weight_health` extended with `perceptron` section
- **Tests**: 13 new (feature building, scoring, shadow comparison, weight I/O)

### Integration Points
- `NeuralRouter` gains `perceptron: Option<PerceptronDispatcher>` field
- `NeuralApiServer::new()` auto-initializes with mock weights (shadow phase)
- When `neural_routing_perceptron.bin` exists, trained weights are loaded instead
- `select_primary()` in `discovery_registry.rs` calls `perceptron.shadow_compare()`
  after L4 weighted selection — zero impact on dispatch decisions (Phase 1)

### Weight Vector Format (for barraCuda ml.mlp_train)
```
Index  Feature                  Source
0-31   domain_onehot[32]        djb2 hash of capability domain prefix % 32
32     latency_ewma_norm        ProviderWeight.ewma_latency_ms / 500.0
33     error_rate               ProviderWeight.ewma_error_rate
34     topology_affinity        ProviderWeight.topology_affinity
35     gate_load_norm           tracked_methods / 100.0
36     bias                     (bias term)
```

Training output should be a flat 148-byte file (37 × 4 bytes, little-endian f32).

### Deep Debt Assessment (P3)
- **2 legitimate `map_err(anyhow!)` sites**: lz4_flex `DecompressError` doesn't
  implement `std::error::Error`; env var chain constructs error from scratch.
  Both are correct patterns. No action needed.
- **SONGBIRD_MESH_ENABLED alignment**: biomeOS Rust code does not reference this
  env var — it's a Songbird binary configuration set in graph TOML files.
  The mismatch is between `SONGBIRD_MESH_ENABLED` (our graphs) and
  `SONGBIRD_FEDERATION_ENABLED` (Songbird binary). Upstream coordination needed.

### Test Extraction Wave 3
- `http_client.rs`: 553 → 245 lines (308L extracted)
- `lifecycle_manager/mod.rs`: 586 → 123 lines (463L extracted)

---

## Blockers

| Item | Blocker | Owner |
|------|---------|-------|
| Perceptron Phase 2 (epsilon-greedy) | `neural_routing_perceptron.bin` from ml.mlp_train | strandGate (barraCuda) |
| Cross-gate mesh end-to-end test | Songbird dispatch fix | Songbird team |
| SONGBIRD_MESH_ENABLED alignment | Songbird binary env var name | Songbird team |

## Next Steps (for primalSpring review)

1. **When barraCuda ml.mlp_train ships**: Drop `neural_routing_perceptron.bin` in
   `$XDG_DATA_HOME/biomeos/` — biomeOS will auto-load trained weights on next
   NeuralApiServer startup. No code changes needed.
2. **Phase 2 graduation**: After 1000+ shadow dispatches with trained weights,
   assess disagreement rate. If perceptron improves dispatch quality, enable
   epsilon-greedy (ε=0.1) by changing `PerceptronPhase::Shadow` to
   `PerceptronPhase::EpsilonGreedy` in server init.
3. **Cross-gate testing**: Once Songbird dispatch fix lands, call `gate.register`
   then `capability.call` through mesh — both endpoints are operational.
