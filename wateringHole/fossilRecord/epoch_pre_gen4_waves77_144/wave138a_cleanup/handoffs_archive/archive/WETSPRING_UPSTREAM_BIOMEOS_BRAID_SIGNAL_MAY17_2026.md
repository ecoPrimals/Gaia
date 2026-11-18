# Upstream Ask: biomeOS `braid.partial_update` Signal + RootPulse Sync

**Date:** May 17, 2026 (PM)
**Author:** wetSpring workstream
**Audience:** biomeOS team, RootPulse, lithoSpore, primalSpring
**Status:** Request — removes human from the braid push loop
**License:** AGPL-3.0-or-later

---

## Context

wetSpring produces ferment transcript braids for lithoSpore from long-running
genomic computations. These braids are updated incrementally as clones complete
(each clone is a sealed DAG node with a `loamSpine` aglet).

Currently, braid updates reach lithoSpore via **manual `git push`** — a human
must commit the updated braid JSON and push it upstream. This breaks the live
composition model: the computation is primal-composed, but distribution is
hand-wired.

## The Ask

### 1. `braid.partial_update` Signal

When a node seals and the partial Merkle root updates, wetSpring should be able
to fire a signal through biomeOS that notifies downstream consumers.

```json
{
  "jsonrpc": "2.0",
  "method": "signal.dispatch",
  "params": {
    "signal": "braid.partial_update",
    "payload": {
      "spring": "wetSpring",
      "dataset_id": "barrick_2009_sovereign_resequencing",
      "braid_id": "braid-...",
      "sealed_count": 3,
      "total_count": 7,
      "partial_merkle_root": "abc123..."
    }
  },
  "id": 1
}
```

### 2. `braid.complete` Signal

When the full session completes and a final braid is woven:

```json
{
  "jsonrpc": "2.0",
  "method": "signal.dispatch",
  "params": {
    "signal": "braid.complete",
    "payload": {
      "spring": "wetSpring",
      "dataset_id": "barrick_2009_sovereign_resequencing",
      "braid_id": "braid-...",
      "merkle_root": "def456...",
      "braid_path": "provenance/braids/barrick_2009_sovereign.json"
    }
  },
  "id": 1
}
```

### 3. RootPulse Propagation

RootPulse should listen for `braid.partial_update` and `braid.complete` signals
and propagate the braid artifact to lithoSpore's expected location. This replaces
the manual git push entirely.

## What It Unlocks

- **No human in the push loop**: braids propagate automatically as computation
  progresses
- **Incremental visibility**: lithoSpore sees partial results as clones complete,
  not only when the full computation finishes
- **Distributed pipeline support**: when `toadStool` fans out clone processing
  across nodes, each node's completion triggers a signal, and RootPulse
  aggregates and propagates

## Current Workaround

wetSpring writes braid JSON to `provenance/braids/` and a human runs
`git add && git commit && git push`. For the Tenaillon 2016 dataset (264 clones,
multi-day computation), this means lithoSpore sees nothing until someone manually
pushes.

## Degradation Behavior

If biomeOS/RootPulse signals are unavailable, wetSpring continues to write braids
to disk. The git-push fallback remains functional. No science is blocked.

## References

- wetSpring sovereign pipeline: `barracuda/src/bin/validate_sovereign_resequencing.rs`
- biomeOS signal dispatch: `barracuda/src/ipc/handlers/data_fetch.rs` (existing pattern)
- Existing handoff: `WETSPRING_SOVEREIGN_PIPELINE_HANDOFF_MAY17_2026.md`
