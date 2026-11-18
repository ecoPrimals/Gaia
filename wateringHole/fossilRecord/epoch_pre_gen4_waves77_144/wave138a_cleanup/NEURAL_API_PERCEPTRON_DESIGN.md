# Neural API Perceptron Routing — Design Document

**Status**: DESIGN (Wave 68)
**Owner**: eastGate (primalSpring) + biomeGate (barraCuda)
**Priority**: P3 — after L4 weighted routing is complete

---

## Goal

Evolve the Neural API routing function from a deterministic heuristic
(`ProviderWeight::score()`) to a single-layer perceptron that learns optimal
provider selection from dispatch telemetry. The API surface (`capability.call`)
is unchanged — only the internal routing decision evolves.

---

## Architecture

### Current (L4 Heuristic)

```
capability.call("crypto", "hash", params)
    → discover_capability("crypto")
    → ProviderWeight::score() per candidate
    → select max score (deterministic formula)
    → dispatch to selected provider
    → record to dispatch_telemetry.jsonl
```

### Proposed (L5 Perceptron)

```
capability.call("crypto", "hash", params)
    → discover_capability("crypto")
    → build feature vector from context
    → perceptron.forward(features) → provider probabilities
    → select provider (argmax or epsilon-greedy exploration)
    → dispatch to selected provider
    → record outcome to dispatch_telemetry.jsonl
    → periodic: retrain perceptron from telemetry
```

---

## Input Feature Vector

Six features, all available at dispatch time:

| Feature | Type | Source | Range |
|---------|------|--------|-------|
| `method_domain` | categorical (one-hot) | capability registry | 0/1 per domain |
| `param_size_bytes` | numeric | `serde_json::to_vec(&params).len()` | 0..10MB |
| `gate_load` | numeric | `neural_api.utilization` hot count | 0..1000 |
| `provider_latency_ewma` | numeric | `RoutingWeightTable` | 0..10000ms |
| `provider_error_rate` | numeric | `RoutingWeightTable` | 0..1.0 |
| `topology_affinity` | numeric | `TOPOLOGY_MAP.toml` segment lookup | 0..1.0 |

With ~30 capability domains (one-hot), the input vector is ~36 dimensions.

### Feature Engineering

```rust
struct DispatchFeatures {
    domain_onehot: [f32; 32],
    param_size_norm: f32,
    gate_load_norm: f32,
    latency_ewma_norm: f32,
    error_rate: f32,
    topology_affinity: f32,
}
```

Normalization: min-max scaling from telemetry statistics (updated every 1000 dispatches).

---

## Output

One probability per candidate provider. For N candidates:

```
softmax([w · features_provider_1 + b_1, ..., w · features_provider_N + b_N])
```

Selection: argmax (deterministic) or epsilon-greedy (exploration phase).

---

## Training Pipeline

### Data Source

`dispatch_telemetry.jsonl` — already written by primalSpring `NeuralDispatcher`:

```json
{"method":"crypto.hash","owner":"beardog","latency_ms":0.8,"success":true,"gate":"eastGate","timestamp":"..."}
```

### Label

Reward signal: `1.0 / (1.0 + latency_ms)` for success, `0.0` for failure.
Higher reward = faster successful dispatch.

### Training Loop

1. Collect N dispatch records (batch size: 256)
2. For each record: build feature vector + reward
3. Compute loss: cross-entropy between predicted provider and actual provider,
   weighted by reward (good outcomes reinforce, bad outcomes penalize)
4. Gradient update: standard SGD with learning rate 0.01
5. barraCuda `ml.mlp_train` performs the computation:
   ```json
   { "layers": [36, 16], "inputs": [...], "targets": [...],
     "learning_rate": 0.01, "epochs": 10 }
   ```

### Schedule

- Offline: retrain every 1000 dispatches (batch from telemetry file)
- Online (future): incremental update after each dispatch
- Weight persistence: serialize to `neural_routing_weights.bin` in gate data dir

---

## Shadow Mode (Graduation Protocol)

The perceptron must prove itself before taking over routing decisions.

### Phase 1 — Shadow (no impact)

```
For each dispatch:
  rule_choice = ProviderWeight::score() argmax   (DECIDES)
  nn_choice   = perceptron.forward(features) argmax (OBSERVES)
  log { rule_choice, nn_choice, agree: bool }
```

Metrics:
- Agreement rate (should trend toward >90%)
- Disagreement analysis: when they disagree, which performed better?
- Latency overhead of perceptron forward pass (<0.1ms target)

### Phase 2 — Epsilon-greedy (gradual adoption)

```
epsilon = 0.1  (10% of dispatches use perceptron choice)
For each dispatch:
  if random() < epsilon:
    use perceptron choice
  else:
    use rule-based choice
  record both choices + actual outcome
```

Increase epsilon as perceptron proves superiority.

### Phase 3 — Full graduation

```
perceptron choice DECIDES
rule-based choice OBSERVES (safety net)
If perceptron error rate exceeds threshold → automatic fallback to rules
```

---

## Integration Points

| Component | Role |
|-----------|------|
| **primalSpring** `NeuralDispatcher` | Feature extraction, shadow logging, telemetry |
| **biomeOS** `discover_capability` | Consumes perceptron output for selection |
| **barraCuda** `ml.mlp_train` | Training computation (capability already registered) |
| **primalSpring** `NeuralBridge` | Observes perceptron metrics via `neural_api.weight_health` |
| **dispatch_telemetry.jsonl** | Training data source |
| **TOPOLOGY_MAP.toml** | Topology affinity feature source |

---

## Constraints

1. **Forward pass must be <0.1ms** — perceptron is in the hot dispatch path
2. **Fallback to rules on any error** — perceptron failure must not break routing
3. **No external dependencies** — barraCuda's `ml.mlp_train` is pure Rust
4. **Weights survive restart** — serialize to disk after each training batch
5. **Observable** — `neural_api.weight_health` exposes perceptron metrics
6. **Cold start** — first 1000 dispatches use rule-based only to collect training data

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Agreement rate (shadow) | >90% within 5000 dispatches |
| Latency improvement | >10% reduction in p95 dispatch latency |
| Error rate | No increase vs. rule-based baseline |
| Forward pass time | <0.1ms per dispatch |
| Training time | <1s per batch (256 records) |

---

## Timeline

| Phase | Wave | Owner | Prerequisite |
|-------|------|-------|-------------|
| L4 weighted selection complete | 69 | southGate (biomeOS) | First-match replaced with score() |
| Feature extraction in primalSpring | 70 | eastGate | L4 complete, telemetry flowing |
| Shadow mode + offline training | 71 | eastGate + biomeGate | barraCuda ml.mlp_train wired |
| Epsilon-greedy adoption | 72 | southGate (biomeOS) | Shadow agreement >90% |
| Full graduation | 73+ | southGate (biomeOS) | Epsilon performance validated |

---

*Wave 68. The Neural API begins to earn its name.*
