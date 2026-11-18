# biomeOS → primalSpring: Upstream Gaps R5 + R7 Resolved

**Date:** May 19, 2026
**Author:** biomeOS team (southGate)
**Audience:** primalSpring, all springs, lithoSpore
**Status:** R5 RESOLVED, R7 DEFERRED-TO-STADIAL
**Version:** v3.63
**License:** AGPL-3.0-or-later

---

## R5: `nest.store` Signal Dispatch — RESOLVED

### Finding

The primalSpring audit reported that `nest.store` was "not yet wired as a
signal-dispatch target." Investigation revealed the infrastructure was already
complete (graph, tier, schema, interception) — the gap was **discoverability**:
`nest.store` wasn't registered as a first-class route table entry, so callers
had to know about `signal.dispatch` or `capability.call` indirection.

### What was already in place (no changes needed)

- `"nest"` in `SIGNAL_TIERS` constant (`signal.rs`)
- `graphs/signals/nest_store.toml` — 4-node sequential provenance pipeline:
  `nestgate → rhizoCrypt → loamSpine → sweetGrass`
- `config/signal_tools.toml` — `nest.store` schema with `content`, `author`,
  `metadata` parameters
- `capability.call` interception: `{ capability: "nest", operation: "store" }`
  auto-dispatches to the signal graph
- `signal.dispatch`: `{ signal: "nest.store", params: {...} }` works via
  explicit dispatch route

### What was added (v3.63)

**All 16 signal methods registered as first-class route table entries.**
Callers can now invoke `nest.store` (or `tower.publish`, `braid.complete`,
etc.) directly as a JSON-RPC method name without indirection:

```json
{"jsonrpc": "2.0", "method": "nest.store", "params": {"content": "...", "author": "did:key:z6Mk..."}, "id": 1}
```

This routes through `SemanticCapabilityCall → capability.call → signal graph
interception` — the same execution path, but discoverable via method listing
and directly callable without wrapper methods.

**New route table entries (all 16 signals):**
- nest: `nest.store`, `nest.commit`, `nest.retrieve`
- tower: `tower.publish`, `tower.authenticate`, `tower.discover`, `tower.health`, `tower.bootstrap`
- node: `node.compute`
- braid: `braid.partial_update`, `braid.complete`
- meta: `meta.observe`, `meta.intent`, `meta.render`, `meta.health`, `meta.deploy`

**3 new tests:**
- `nest_store_graph_has_provenance_pipeline` — validates 4-node sequential order,
  binary assignments, and metadata
- `signal_graph_path_resolves_all_nest_signals` — verifies `nest.{store,commit,retrieve}`
  graph files exist
- `all_signal_tools_have_matching_graphs` — cross-validates `signal_tools.toml`
  tool definitions against on-disk graph files

### Consumer adoption

Springs can now call:
```python
result = neural_api.call("nest.store", {
    "content": content_bytes,
    "author": author_did,
    "metadata": {"type": "barrick_clone", "source": "wetSpring"}
})
```

This replaces the 4-call provenance trio pattern (nestGate → rhizoCrypt →
loamSpine → sweetGrass) with a single signal dispatch.

---

## R7: `spore.instantiate` — DEFERRED-TO-STADIAL

### Current state

- `spore.instantiate` Neural API route: **wired** (v3.61)
- `livespore_create.toml` graph: **structural** (6-node workflow defined)
- Operation handlers (`validate_spore_target`, etc.): **not implemented**
- Graph executor behavior: nodes are **skipped** (`{"skipped": true}`)

### Decision

Explicitly deferred to stadial phase. lithoSpore Tier 3 VM provisioning
backend is not yet available. The route accepts calls and executes the graph
structure, but node operations produce skip responses until lithoSpore
implements the backing handlers.

The handler now includes a `_deferred` field in the execution context:
```
"_deferred": "lithoSpore Tier 3 not yet available — graph nodes will be skipped"
```

### Unblocking condition

When lithoSpore Tier 3 lands, implement operation handlers in
`biomeos-graph` executor for: `validate_spore_target`, `package_primals`,
`copy_graphs`, `generate_family_seed`, `create_autostart`, `validate_spore`.

---

## Non-biomeOS items (acknowledged, not actionable by biomeOS)

| # | Gap | Owner | biomeOS status |
|---|-----|-------|----------------|
| CG-3 | GPU API alignment (`submit_and_map`) | barraCuda + coralReef | Not biomeOS scope |
| CG-8 | Cross-gate dispatch via songbird | songbird + biomeOS | Blocked on songbird relay layer |
| S1 | `beardog-acme` auto-cert crate | bearDog | Not biomeOS scope |

CG-8 note: biomeOS has `forward_to_remote_gate()` via AtomicClient and
`capability.call` cross-gate routing. Phase 2 (songbird relay mediation)
requires songbird to expose relay-based forwarding for biomeOS to consume.
