# barraCuda Wave 74 — Perceptron Training Pipeline

**Date**: 2026-06-03
**Gate**: strandGate (192.168.1.132)
**Status**: COMPLETE — end-to-end pipeline ready for primalSpring integration

---

## What's New (since Wave 73)

### `ml.perceptron_train` — End-to-End Pipeline Method

Accepts raw `dispatch_telemetry.jsonl` records directly. No feature engineering
needed on the caller side — barraCuda handles it all internally per
`NEURAL_API_PERCEPTRON_DESIGN.md`.

**Wire contract:**
```json
{
  "method": "ml.perceptron_train",
  "params": {
    "records": [
      {"method": "crypto.hash", "owner": "beardog", "latency_ms": 0.8, "success": true, "gate": "eastGate"},
      {"method": "compute.dispatch", "owner": "songbird", "latency_ms": 2.1, "success": true, "gate": "strandGate"}
    ],
    "learning_rate": 0.01,
    "epochs": 10,
    "output_path": "/data/gate/neural_routing_perceptron.bin"
  }
}
```

**Response:**
```json
{
  "layers": [{"weights": [[...36×N...]], "biases": [...], "activation": "identity"}],
  "mse": 0.042,
  "epochs": 10,
  "records_processed": 256,
  "providers": ["beardog", "songbird", "toadstool", "coralreef"],
  "domains": ["crypto", "compute", "storage", "network"],
  "output_path": "/data/gate/neural_routing_perceptron.bin"
}
```

### Feature Extraction (internal)

Per NEURAL_API_PERCEPTRON_DESIGN.md §Input Feature Vector:
- `[0..31]`: domain one-hot (from `method` field, first segment before `.`)
- `[32]`: param_size_norm (default 0.0 — not in telemetry)
- `[33]`: gate_load_norm (placeholder 0.5)
- `[34]`: latency_ewma_norm (normalized from `latency_ms`)
- `[35]`: topology_affinity proxy (success → 1.0, failure → 0.0)

### Reward Signal

Per design doc: `1.0 / (1.0 + latency_ms)` for success, `0.0` for failure.
Fast providers with high success rates get stronger reinforcement.

### Serialization

When `output_path` is provided, trained weights are serialized as JSON
(compatible with `SimpleMlp::from_json()` for direct reload). biomeOS can
load this file at startup for the `PerceptronAdvisor` hot path.

---

## Method Inventory

| Method | Purpose | Status |
|--------|---------|--------|
| `ml.mlp_train` | Generic MLP training (dims shorthand or explicit weights) | Wave 73 ✓ |
| `ml.perceptron_train` | End-to-end pipeline from raw telemetry | Wave 74 ✓ |
| `ml.mlp_forward` | Inference (hot path, <0.1ms) | Existing ✓ |

Total registered methods: **91**

---

## Mesh Status

- **Songbird**: PID 608519, federation port 7700, operational
- **bearDog**: v0.9.0, PID 706866, socket + TCP operational
- **Peer**: eastGate — ready for `capability.call` cross-gate testing

---

## GAP-HS-124 Note

coralReef already resolved GAP-HS-124 in Wave 68 (`wgsl_to_spirv()` public API).
No work needed from strandGate on this item.

---

## primalSpring Integration Guide

1. Collect dispatch telemetry (already flowing per Wave 72)
2. Call `ml.perceptron_train` with batch of records (recommended: 256+)
3. Response includes trained weights + provider/domain index mappings
4. Serialize `output_path` file is ready for biomeOS `PerceptronAdvisor`
5. For inference in hot path: call `ml.mlp_forward` with feature vector
