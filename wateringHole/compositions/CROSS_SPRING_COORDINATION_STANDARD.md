# Cross-Spring Coordination Standard

**Version:** 1.0.0
**Date:** April 27, 2026
**Audience:** All springs, primalSpring, biomeOS
**Status:** Active Standard
**License:** AGPL-3.0-or-later

---

## Purpose

Springs evolved independently, but convergent evolution produced recurring
cross-spring patterns. neuralSpring formalized these as `science.cross_spring_*`
RPC methods. healthSpring independently evolved a five-way cross-spring bridge.
groundSpring produces shared baselines that other springs consume.

This standard extracts the common patterns and defines how springs coordinate
across domain boundaries without coupling.

---

## Principles

1. **No shared crates** — springs never import each other's code
2. **IPC only** — all cross-spring communication is JSON-RPC over UDS
3. **Capability routing** — route by domain capability, never spring name
4. **Graceful absence** — cross-spring calls degrade when siblings are unavailable
5. **Attribution flows** — cross-spring work carries provenance via sweetGrass

---

## Standard Cross-Spring Methods

These methods SHOULD be implemented by any spring that participates in
cross-spring coordination. The `science.cross_spring_*` namespace is
reserved for this purpose.

### `science.cross_spring_provenance`

Request provenance chain for a shared artifact across spring boundaries.

```json
{
  "jsonrpc": "2.0",
  "method": "science.cross_spring_provenance",
  "params": {
    "artifact_id": "wetspring_exp403_parity_v1",
    "depth": 3
  },
  "id": 1
}
```

Response:

```json
{
  "jsonrpc": "2.0",
  "result": {
    "chain": [
      {
        "spring": "wetspring",
        "experiment": "exp403",
        "version": "V151",
        "artifact_hash": "blake3:abc123...",
        "timestamp": "2026-04-27T12:00:00Z"
      },
      {
        "spring": "neuralspring",
        "experiment": "surrogate_training",
        "version": "V138",
        "artifact_hash": "blake3:def456...",
        "derived_from": "blake3:abc123...",
        "timestamp": "2026-04-27T13:00:00Z"
      }
    ]
  },
  "id": 1
}
```

### `science.cross_spring_benchmark`

Run a cross-spring benchmark using a shared baseline from another spring.

```json
{
  "jsonrpc": "2.0",
  "method": "science.cross_spring_benchmark",
  "params": {
    "baseline_spring": "groundspring",
    "baseline_id": "anderson_spectral_v1",
    "method": "anderson.localization_length",
    "params": { "disorder": 4.0, "system_size": 1000 },
    "tolerance": 1e-10
  },
  "id": 2
}
```

Response:

```json
{
  "jsonrpc": "2.0",
  "result": {
    "baseline_value": 23.456,
    "computed_value": 23.456000001,
    "within_tolerance": true,
    "tolerance_used": 1e-10,
    "provenance": {
      "baseline_source": "groundspring V124",
      "compute_method": "barracuda via IPC",
      "timestamp": "2026-04-27T14:00:00Z"
    }
  },
  "id": 2
}
```

### `science.cross_spring_validate`

Request another spring to validate a result using its domain expertise.

```json
{
  "jsonrpc": "2.0",
  "method": "science.cross_spring_validate",
  "params": {
    "requesting_spring": "healthspring",
    "domain": "uncertainty",
    "method": "measurement.bias_variance",
    "data": { "predictions": [1.0, 1.1, 0.9], "observations": [1.0, 1.0, 1.0] }
  },
  "id": 3
}
```

This enables the healthSpring five-way bridge pattern: healthSpring routes
clinical models through wet (gut diversity), neural (surrogates), hot
(spectral), air (exposure), and ground (uncertainty) — each spring
validates using its own domain expertise.

### `science.cross_spring_capabilities`

Discover what cross-spring coordination a sibling supports.

```json
{
  "jsonrpc": "2.0",
  "method": "science.cross_spring_capabilities",
  "params": {},
  "id": 4
}
```

Response:

```json
{
  "jsonrpc": "2.0",
  "result": {
    "spring": "groundspring",
    "version": "V124",
    "cross_spring_methods": [
      "science.cross_spring_benchmark",
      "science.cross_spring_validate"
    ],
    "shared_baselines": [
      "anderson_spectral_v1",
      "noise_decomposition_v1",
      "bootstrap_reference_v1"
    ],
    "validation_domains": [
      "measurement.bias_variance",
      "measurement.decompose",
      "measurement.bootstrap"
    ]
  },
  "id": 4
}
```

---

## Cross-Spring Routing Patterns

### Pattern 1: Shared Baselines (groundSpring → all)

groundSpring produces "labeled dirty data" baselines — reference datasets
with known noise profiles, uncertainty bounds, and expected values. Other
springs consume these for validation.

```
groundSpring publishes:
  anderson_spectral_v1    → consumed by hotSpring, neuralSpring
  noise_decomposition_v1  → consumed by wetSpring, airSpring
  bootstrap_reference_v1  → consumed by healthSpring
```

**How to consume**: Call `science.cross_spring_benchmark` with the
baseline ID. groundSpring returns the reference value; your spring
computes and compares.

**Future**: Shared baselines will be published as validated datasets
via NestGate content-addressed storage, discoverable via
`storage.fetch_external` with provenance certificates from loamSpine.

### Pattern 2: Five-Way Bridge (healthSpring hub)

healthSpring routes clinical compute models through five sibling springs,
each providing domain-specific validation:

```
healthSpring
  ├─ wetSpring:    gut diversity, colonization, hormesis
  ├─ neuralSpring: Hill equation surrogates, PopPK
  ├─ hotSpring:    lattice tissue models, Anderson spectral
  ├─ airSpring:    environmental exposure, hygiene hypothesis
  └─ groundSpring: uncertainty quantification, dose-response UQ
```

Each call uses `science.cross_spring_validate` with the target spring's
domain methods. healthSpring aggregates results into a clinical model.

This pattern is reusable — any spring can become a hub that routes
through siblings.

### Pattern 3: Precision Routing (neuralSpring)

neuralSpring's `science.precision_routing` determines which compute path
(CPU f64, GPU WGSL f64, GPU DF64, GPU f32) meets a requested tolerance:

```json
{
  "jsonrpc": "2.0",
  "method": "science.precision_routing",
  "params": {
    "operation": "matrix_multiply",
    "required_tolerance": 1e-14,
    "matrix_size": [1000, 1000]
  },
  "id": 5
}
```

Response:

```json
{
  "result": {
    "recommended_path": "cpu_f64",
    "alternatives": [
      { "path": "gpu_df64", "tolerance": 1e-13, "speedup": 12.0 },
      { "path": "gpu_f64", "tolerance": 1e-10, "speedup": 45.0 }
    ]
  }
}
```

Other springs call this before dispatching compute to make informed
precision-performance tradeoffs.

---

## Shared Baseline Publication Standard

Springs that produce reusable baselines SHOULD publish them with:

```json
{
  "baseline_id": "anderson_spectral_v1",
  "source_spring": "groundspring",
  "source_version": "V124",
  "domain": "measurement",
  "description": "Anderson localization length at W=4, L=1000",
  "expected_value": 23.456,
  "tolerance": 1e-10,
  "provenance": {
    "experiment": "exp_anderson_001",
    "python_baseline": "blake3:abc123...",
    "rust_validation": "blake3:def456...",
    "publication": "Anderson (1958), Phys. Rev. 109, 1492"
  }
}
```

Baselines are immutable once published. New versions get new IDs.

---

## Discovery

Cross-spring coordination requires discovering sibling springs at runtime.
Use the same tiered socket discovery as primal discovery
(`SPRING_COMPOSITION_PATTERNS.md` §3), but with spring socket naming:

```
$XDG_RUNTIME_DIR/biomeos/groundspring-${FAMILY_ID}.sock
$XDG_RUNTIME_DIR/biomeos/wetspring-${FAMILY_ID}.sock
```

Or via biomeOS Neural API:

```json
{
  "jsonrpc": "2.0",
  "method": "capability.discover",
  "params": { "capability": "measurement" },
  "id": 1
}
```

biomeOS returns the socket path for the spring providing that capability.

---

## Graceful Degradation

Cross-spring calls MUST degrade gracefully:

```rust
pub fn cross_spring_validate(
    bridge: &PrimalBridge,
    domain: &str,
    method: &str,
    data: serde_json::Value,
) -> CrossSpringResult {
    match bridge.call_optional(domain, method, data) {
        Some(result) => CrossSpringResult::Validated(result),
        None => CrossSpringResult::Unavailable {
            domain: domain.to_string(),
            reason: "sibling spring not running",
        },
    }
}
```

A spring with no running siblings operates in isolation — all cross-spring
calls return `Unavailable` and the spring's own domain logic proceeds.

---

## Attribution for Cross-Spring Work

When Spring A uses Spring B's validation, attribution flows through
sweetGrass:

```
sweetGrass braid for "healthspring_clinical_model_v3":
  - healthSpring: Publisher (0.3)
  - wetSpring: Contributor — gut diversity validation (0.2)
  - neuralSpring: Contributor — surrogate training (0.2)
  - hotSpring: Validator — spectral verification (0.15)
  - groundSpring: Validator — uncertainty quantification (0.15)
```

The provenance trio records the cross-spring lineage. The attribution
distribution enables the sunCloud economic model to flow value across
spring boundaries.

---

## Evolution Path

| Phase | What | Status |
|-------|------|--------|
| 1 | `science.cross_spring_*` methods in neuralSpring | **Implemented** (V138) |
| 2 | healthSpring five-way bridge operational | **Implemented** (V59) |
| 3 | groundSpring shared baselines consumable via IPC | **Partially implemented** (V124) |
| 4 | Standardized baseline publication format | **This document** |
| 5 | NestGate-hosted shared baselines with loamSpine certificates | Planned |
| 6 | biomeOS cross-spring graph execution (multi-spring cell graphs) | Planned |
| 7 | sunCloud attribution flow across spring boundaries | Future |

---

## Related Documents

- `SPRING_COMPOSITION_PATTERNS.md` — Per-spring absorbed patterns
- `SPRING_INTERACTION_PATTERNS.md` — Cross-evolution and interop patterns
- `PROVENANCE_TRIO_INTEGRATION_GUIDE.md` — Wiring the provenance trio
- `EVOLUTION_STATUS_WAVE66.md` — How capabilities flow between layers
- `GATE_SPRING_OWNERSHIP.md` — Spring composition readiness matrix
- `SPRING_COORDINATION_AND_VALIDATION.md` — Handoffs and validation assignments

---

**Springs are independent laboratories. Cross-spring coordination makes their discoveries compound. Every sibling's validation strengthens the whole.**
