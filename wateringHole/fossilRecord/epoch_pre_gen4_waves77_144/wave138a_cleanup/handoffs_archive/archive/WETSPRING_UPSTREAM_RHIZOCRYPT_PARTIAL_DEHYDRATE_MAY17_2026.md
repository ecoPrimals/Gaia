# Upstream Ask: rhizoCrypt `partial_dehydrate` for Aglet Pattern

**Date:** May 17, 2026 (PM)
**Author:** wetSpring workstream
**Audience:** rhizoCrypt team, primalSpring
**Status:** Request — needed for live partial braid production
**License:** AGPL-3.0-or-later

---

## Context

wetSpring's sovereign resequencing pipeline processes LTEE clones sequentially
(7 for Barrick 2009, 264 for Tenaillon 2016). Each clone completes independently
and produces a sealed provenance node with a `loamSpine` aglet. The full DAG
session may run for hours or days.

Currently, the pipeline must wait until **all** clones complete before calling
`dag / dehydrate` to produce a Merkle root. This means downstream consumers
(lithoSpore, Barrick/Lenski labs) see nothing until the entire computation
finishes.

## The Ask

Add a `dag / partial_dehydrate` method to rhizoCrypt that produces a Merkle root
covering only the **sealed** nodes in a session, without closing the session.

### Wire Format (proposed)

```json
{
  "jsonrpc": "2.0",
  "method": "dag/partial_dehydrate",
  "params": {
    "session_id": "dag-...",
    "sealed_node_ids": ["node-REL1164M", "node-REL2179M"]
  },
  "id": 1
}
```

### Expected Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "partial_merkle_root": "abc123...",
    "sealed_count": 2,
    "total_count": 7,
    "session_open": true
  },
  "id": 1
}
```

## What It Unlocks

- **Live partial braids**: after each clone seals, wetSpring calls
  `partial_dehydrate`, gets a valid Merkle root, and can emit a partial braid
  that lithoSpore can verify.
- **Aglet pattern formalization**: each sealed node has a `loamSpine` commit.
  `partial_dehydrate` covers the sealed subgraph. Consumers see a valid partial
  proof without waiting for the full session.
- **Distributed workloads**: when `toadStool` dispatches clone-level work units
  across nodes, each node seals its results and `partial_dehydrate` aggregates
  them incrementally.

## Current Workaround

wetSpring emits hand-wired partial braids with `dag_merkle_root: ""` and
`"status": "partial"`. These are structurally valid but not cryptographically
verified. The DAG session tracks events via `dag / event.append` per clone, but
there is no way to get a partial Merkle root without closing the session.

## Degradation Behavior

If `partial_dehydrate` is unavailable, wetSpring continues to emit partial braids
with empty Merkle roots. Domain science is never gated behind this — provenance
is enrichment. The partial braid still carries per-clone BLAKE3 hashes and
`loamSpine` aglet IDs, which are independently verifiable.

## References

- wetSpring sovereign pipeline: `barracuda/src/bin/validate_sovereign_resequencing.rs`
- Existing aglet pattern: `provenance/braids/barrick_2009_sovereign.json`
- Trio integration guide: `infra/wateringHole/PROVENANCE_TRIO_INTEGRATION_GUIDE.md`
