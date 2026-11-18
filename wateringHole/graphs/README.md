# Cascade Graphs — biomeOS Composition Patterns

Declarative graph definitions for primal-composed operations. Each graph
describes a multi-step flow that membrane-shadow's NeuralBridge routes
through biomeOS with try-primal-first semantics.

## Graphs

| Graph | Trigger | Flow |
|-------|---------|------|
| `waterfall_publish` | `waterfall.publish` | Full cascade: code → impulse → provenance → transport |
| `impulse_post_signed` | `impulse.post` | Signed impulse with DAG recording and mesh relay |
| `context_weave_anchored` | `context.weave` | Context braid with validation and optional anchoring |

## Architecture

```
waterfall_publish (composition)
├── push_to_forgejo         membrane    temporal.sync
├── compose_impulse         membrane    impulse.compose
├── sign_impulse            bearDog     auth.sign
├── store_impulse           membrane    impulse.store
├── record_dag              rhizoCrypt  dag.append
├── weave_context           membrane    context.weave      (wave_boundary)
├── validate_braid          sweetGrass  braid.validate     (wave_boundary)
├── anchor_state            loamSpine   ledger.stamp       (wave_boundary)
├── push_mirror             membrane    mirror.push_sync
└── relay_impulse           songbird    mesh.publish
```

## Fallback Semantics

- `skip`: step is omitted if primal unavailable (non-critical)
- `defer`: step is queued for later execution (network-dependent)
- No fallback: step is required; cascade fails if primal unavailable

## Status

These graphs are declarative specifications. The NeuralBridge in
membrane-shadow routes through biomeOS when available, falling back
to local shadow implementations. Full biomeOS graph execution requires
primals to be deployed and registered.
