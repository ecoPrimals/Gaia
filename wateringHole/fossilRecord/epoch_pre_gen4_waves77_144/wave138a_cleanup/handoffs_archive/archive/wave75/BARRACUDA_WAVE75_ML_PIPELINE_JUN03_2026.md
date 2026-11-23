# barraCuda Wave 75 — ML Inference + Persistence Pipeline

**Date**: 2026-06-03
**Gate**: strandGate (192.168.1.132)
**Status**: COMPLETE — full train → save → load → infer pipeline operational

---

## What's New (since Wave 74)

### `ml.mlp_infer` — Batch Inference Endpoint

Runs forward pass through trained perceptron on new dispatch telemetry vectors.
biomeOS `PerceptronAdvisor` can call this for real-time routing decisions.

**Wire contract:**
```json
{
  "method": "ml.mlp_infer",
  "params": {
    "model_path": "/data/gate/neural_routing_perceptron.bin",
    "records": [
      {"method": "stats.mean", "latency_ms": 1.2, "success": true},
      {"method": "crypto.hash", "latency_ms": 0.5, "success": true}
    ],
    "providers": ["beardog", "songbird", "toadstool"],
    "domain_index": {"stats": 0, "crypto": 1, "ml": 2}
  }
}
```

**Response:**
```json
{
  "results": [
    {"scores": [0.72, 0.31, 0.45], "best_index": 0, "best_provider": "beardog"},
    {"scores": [0.55, 0.68, 0.42], "best_index": 1, "best_provider": "songbird"}
  ],
  "records_processed": 2
}
```

Supports both `model_path` (load from disk) and inline `model` (embedded weights).

### `ml.mlp_save` — Model Persistence

Serializes trained model to disk (JSON format). Path-traversal guarded.

```json
{"method": "ml.mlp_save", "params": {"model": {...}, "path": "/data/gate/perceptron.bin"}}
```

### `ml.mlp_load` — Model Loading

Loads persisted model. Returns full layer structure for inference or retraining.

```json
{"method": "ml.mlp_load", "params": {"path": "/data/gate/perceptron.bin"}}
```

---

## Complete ML Pipeline

| Step | Method | Status |
|------|--------|--------|
| 1. Train from telemetry | `ml.perceptron_train` | Wave 74 ✓ |
| 2. Save weights | `ml.mlp_save` | Wave 75 ✓ |
| 3. Load on restart | `ml.mlp_load` | Wave 75 ✓ |
| 4. Infer routing | `ml.mlp_infer` | Wave 75 ✓ |
| 5. Generic training | `ml.mlp_train` | Wave 73 ✓ |
| 6. Generic forward | `ml.mlp_forward` | Existing ✓ |

---

## Cross-Gate Trust (Dark Forest Invariant 3)

All `ml.*` methods are classified as `Protected` in the `MethodGate`.
When enforcement is active, requests require a valid bearer token from
BTSP session. No unsigned compute.

Public methods (no auth required):
- `health.*`, `auth.*`, `mesh.*`, `btsp.*`

Protected methods (require bearer when enforced):
- All compute: `ml.*`, `stats.*`, `tensor.*`, `compute.*`, etc.

---

## Mesh Trust (from earlier this session)

New `mesh.*` namespace (2 methods):
- `mesh.trust_verify`: cross-gate BTSP trust confirmation with nonce echo
- `mesh.health`: security provider + discovery liveness probe

---

## Method Inventory

Total registered methods: **96** (was 93)

| New Method | Purpose |
|-----------|---------|
| `ml.mlp_infer` | Batch inference from telemetry vectors |
| `ml.mlp_save` | Persist trained model to disk |
| `ml.mlp_load` | Load model from disk |

---

## For biomeOS Integration

1. Train: `ml.perceptron_train` with batch of `dispatch_telemetry.jsonl` records
2. Save: `ml.mlp_save` with returned model + target path
3. On restart: `ml.mlp_load` from saved path
4. Hot path: `ml.mlp_infer` with incoming telemetry → provider scores → route

All methods are <1ms latency for typical model sizes (36×16 perceptron).
