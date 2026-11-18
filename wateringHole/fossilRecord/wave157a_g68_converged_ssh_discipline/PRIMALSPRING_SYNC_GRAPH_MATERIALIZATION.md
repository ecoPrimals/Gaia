# primalSpring: Sync Graph Materialization (Phase C)

**Date**: Aug 7, 2026 | **Wave**: 157a | **From**: eastGate overwatch
**Owner**: primalSpring team

---

## What Needs To Happen

Three composition graphs are registered in `config/capability_registry.toml`
(line 1178-1181) but the TOML graph files don't exist on disk.

**biomeOS Neural API is the how.** These graphs are biomeOS compositions —
the same pattern as `rootpulse_commit.toml`. The Neural API orchestrates
each graph node as a `capability.call`: `temporal.check`, `impulse.post`,
`crypto.sign_ed25519`, `mesh.publish`. No primal knows about "cascading" —
biomeOS composes the graph. When the cascade engine's `agentic` divergence
policy fires, it delegates to these graphs via the Neural API instead of
running hardcoded cellMembrane merge logic.

### Registered but not materialized

| Graph | File (expected) | Nodes | Domain |
|-------|-----------------|-------|--------|
| `sync.diverge` | `graphs/compositions/sync_diverge.toml` | 5 | fall |
| `sync.resolve` | `graphs/compositions/sync_resolve.toml` | 8 | fall |
| `sync.resolve.crossgate` | `graphs/compositions/sync_resolve_crossgate.toml` | 10 | fall |

### Already materialized (reference pattern)

5 rootPulse graphs exist and should be used as the template:

| Graph | File | Nodes |
|-------|------|-------|
| `rootpulse.commit` | `graphs/compositions/rootpulse_commit.toml` | 5 |
| `rootpulse.branch` | `graphs/compositions/rootpulse_branch.toml` | 5 |
| `rootpulse.merge` | `graphs/compositions/rootpulse_merge.toml` | 7 |
| `rootpulse.diff` | `graphs/compositions/rootpulse_diff.toml` | 4 |
| `rootpulse.federate` | `graphs/compositions/rootpulse_federate.toml` | 6 |

---

## Graph Designs

### sync_diverge.toml (5 nodes — SENSE)

Detects divergence across remotes for a repository. Pure read-only (qS domain).

```
1. temporal.check     → cellMembrane: fetch all remotes, build position matrix
2. temporal.classify  → cellMembrane: converge/diverge/parity classification
3. impulse.post       → cellMembrane: fire SYNC impulse if diverged
4. freshness.publish  → cellMembrane: update heads/<gate>.toml
5. mesh.publish       → songBird: broadcast freshness to mesh (optional)
```

Capabilities consumed:
- `temporal.check` (cellMembrane)
- `temporal.classify` (cellMembrane)
- `impulse.post` (cellMembrane)
- `freshness.publish` (cellMembrane)
- `mesh.publish` (songBird) — optional, node `required = false`

### sync_resolve.toml (8 nodes — SYNC)

Resolves a detected divergence on a single gate. This is the `agentic` policy
path from `ecosystem_manifest.toml` — when `repo_policy = "agentic"`, the
cascade delegates to this graph instead of hardcoded merge logic.

```
1. temporal.check     → cellMembrane: re-fetch to confirm divergence still exists
2. temporal.classify  → cellMembrane: classify current state
3. merge.attempt      → cellMembrane: try merge-ff or merge-rebase
4. conflict.detect    → cellMembrane: check for merge conflicts
5. sign               → bearDog: sign resolution commit (Ed25519)
6. commit             → loamSpine: record resolution in ledger
7. push               → cellMembrane: push resolved state to followers
8. impulse.resolve    → cellMembrane: fire RESOLUTION impulse, clear active SYNC impulse
```

Capabilities consumed:
- `temporal.check`, `temporal.classify`, `temporal.sync` (cellMembrane)
- `crypto.sign_ed25519` (bearDog)
- `session.commit` (loamSpine)
- `impulse.post` (cellMembrane)

### sync_resolve_crossgate.toml (10 nodes — SYNC cross-gate)

Same as `sync_resolve` but coordinates across gates via songBird mesh. Adds
mesh discovery, cross-gate fetch, and federated push.

```
1. mesh.peers         → songBird: discover which gates have the repo
2. temporal.check     → cellMembrane: fetch from all gates (via mesh relay)
3. temporal.classify  → cellMembrane: classify cross-gate state
4. merge.attempt      → cellMembrane: try resolution
5. conflict.detect    → cellMembrane: check conflicts
6. sign               → bearDog: sign
7. commit             → loamSpine: record
8. attribute          → sweetGrass: cross-gate attribution braid
9. federate.push      → songBird: push resolved state to all gates
10. impulse.resolve   → cellMembrane: clear impulses, publish freshness
```

---

## TOML Template

Follow the `rootpulse_commit.toml` pattern exactly. Here's the structure:

```toml
[graph]
id = "sync_diverge"
name = "Sync Diverge"
description = "Detect divergence across remotes. Pure read-only quorumSignal."
version = "1.0.0"
coordination = "sequential"
composition_tier = "waterfall"
composition_name = "diverge"
coordination_domain = "fall"

[graph.metadata]
particle = "photon"
security_model = "btsp_optional"
transport = "uds_only"
secure_by_default = true
fragments = ["tower_atomic"]

[[graph.nodes]]
name = "check"
binary = "membrane"
order = 1
required = true
spawn = false
by_capability = "temporal"
capabilities = ["temporal.check"]

# ... more nodes ...
```

Key differences from rootPulse graphs:
- `coordination_domain = "fall"` (not `"pulse"`)
- `composition_tier = "waterfall"` (not `"rootpulse"`)
- `particle = "photon"` for read-only, `"neutron"` for mutating
- cellMembrane is `binary = "membrane"`, not a primal name

---

## Acceptance

1. Three TOML files exist at `graphs/compositions/sync_diverge.toml`, `sync_resolve.toml`, `sync_resolve_crossgate.toml`
2. `cargo test` passes (graph loading validation in primalSpring test suite)
3. Node counts match capability_registry.toml (5, 8, 10)
4. Graphs reference only existing capabilities (temporal.check, crypto.sign_ed25519, etc.)

---

*Phase C of overwatch cascade automation. These graphs complete the waterFall
sync domain. When materialized, biomeOS Neural API can orchestrate the full
qS → wF → rP triad cycle as composition graphs.*
