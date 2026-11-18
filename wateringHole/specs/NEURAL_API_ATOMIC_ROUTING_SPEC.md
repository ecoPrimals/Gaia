# Neural API Atomic Routing Spec

**Date**: Aug 8, 2026 | **From**: eastGate overwatch
**Status**: SPEC — defines canonical routing for all atomics via biomeOS Neural API

---

## Purpose

Every caller (script, spring, gate operator) should talk to **one socket**: the biomeOS Neural API. The Neural API routes `capability.call` to the correct primal based on capability domain registration and composite atomic discovery. This eliminates:

- Direct socket management (knowing which `.sock` file to connect to)
- Wire format mismatches (callers don't need to know primal-specific param shapes)
- Gate-specific socket naming (family IDs, tower names)

```
caller → capability.call(domain.operation, args) → biomeOS Neural API
       → domain resolution → primal socket → JSON-RPC forward → response
```

---

## Neural API Socket

The biomeOS Neural API socket is always at:

```
/run/user/1000/membrane/biomeos-neural-api.sock
```

On gates where biomeOS is deployed via NUCLEUS systemd units, this socket is available once biomeOS reaches `Coordinated` state. All scripts should connect here, never to individual primal sockets.

---

## Atomic Routing Matrix

### Tower Atomic (bearDog, songBird, skunkBat)

| Domain | Operation | Routes to | Returns |
|--------|-----------|-----------|---------|
| `crypto` | `crypto.sign` | bearDog | `{ signature, public_key }` |
| `crypto` | `crypto.verify` | bearDog | `{ valid: bool }` |
| `security` | `security.authenticate` | bearDog | `{ authenticated, identity }` |
| `discovery` | `discovery.peers` | songBird | `{ peers: [...] }` |
| `discovery` | `discovery.announce` | songBird | `{ acknowledged: bool }` |
| `network` | `network.relay` | songBird | forwarded response |
| `defense` | `defense.audit` | skunkBat | `{ findings: [...] }` |
| `defense` | `defense.policy` | skunkBat | `{ policies: [...] }` |
| `health` | `health.check` | any (round-robin) | `{ status, uptime }` |

### Provenance Trio (rhizoCrypt, loamSpine, sweetGrass)

| Domain | Operation | Routes to | Returns |
|--------|-----------|-----------|---------|
| `dag` | `dag.session.create` | rhizoCrypt | `{ session_id }` |
| `dag` | `dag.event.append` | rhizoCrypt | `{ event_id }` |
| `dag` | `dag.event.append_batch` | rhizoCrypt | `{ count, events }` |
| `dag` | `dag.dehydration.trigger` | rhizoCrypt | `{ merkle_root }` |
| `dag` | `dag.partial_dehydrate` | rhizoCrypt | `{ merkle_root, vertices }` |
| `spine` | `spine.create` | loamSpine | `{ spine_id }` |
| `spine` | `spine.status` | loamSpine | `{ height, head_hash }` |
| `session` | `session.commit` | loamSpine | `{ entry_id }` |
| `certificate` | `certificate.verify` | loamSpine | `{ valid, chain }` |
| `braid` | `braid.create` | sweetGrass | `{ braid_id }` |
| `braid` | `braid.get` | sweetGrass | `{ braid }` |
| `braid` | `braid.get_by_hash` | sweetGrass | `{ braid }` |
| `braid` | `braid.list` | sweetGrass | `{ total, items }` |
| `braid` | `braid.query` | sweetGrass | `{ total, items }` |
| `braid` | `braid.commit` | sweetGrass | `{ committed, spine_entry }` |
| `braid` | `braid.anchor` | sweetGrass | `{ anchor_id }` |
| `braid` | `braid.delete` | sweetGrass | `{ deleted: bool }` |
| `braid` | `braid.batch_create` | sweetGrass | `{ created: [...] }` |
| `braid` | `braid.batch_commit` | sweetGrass | `{ committed: [...] }` |
| `convergence` | `convergence.check` | sweetGrass | `{ converged, state }` |
| `convergence` | `convergence.batch_check` | sweetGrass | `{ results: [...] }` |
| `provenance` | `provenance.lineage` | sweetGrass | `{ lineage }` |
| `anchoring` | `anchoring.verify` | sweetGrass | `{ valid, anchor }` |

### Nest Atomic (Tower + nestGate + provenance trio)

| Domain | Operation | Routes to | Returns |
|--------|-----------|-----------|---------|
| `content` | `content.put` | nestGate | `{ hash, size }` |
| `content` | `content.get` | nestGate | `{ data, hash }` |
| `content` | `content.exists` | nestGate | `{ exists: bool }` |
| `content` | `content.list` | nestGate | `{ items: [...] }` |
| `content` | `content.query` | nestGate | `{ results: [...] }` |
| `content` | `content.ingest` | nestGate | `{ ingested, hashes }` |
| `storage` | `storage.tier_status` | nestGate | `{ tiers: [...] }` |

### Node Atomic (Tower + toadStool, barraCuda, coralReef)

| Domain | Operation | Routes to | Returns |
|--------|-----------|-----------|---------|
| `compute` | `compute.dispatch` | barraCuda | `{ result, elapsed }` |
| `tensor` | `tensor.matmul` | barraCuda | `{ tensor }` |
| `shader` | `shader.compile.wgsl` | barraCuda | `{ module_id }` |
| `inference` | `inference.run` | toadStool | `{ output }` |
| `ml` | `ml.predict` | coralReef | `{ prediction }` |

---

## Wire Format: capability.call

Every call to the Neural API uses this JSON-RPC envelope:

```json
{
    "jsonrpc": "2.0",
    "method": "capability.call",
    "params": {
        "capability": "braid",
        "operation": "list",
        "args": { "filter": { "tag": "kegg" }, "limit": 50 }
    },
    "id": 1
}
```

**Semantic fallback**: You can also call `braid.list` directly as the method name. The Neural API will intercept unknown methods matching `domain.operation` and route them as `capability.call`:

```json
{
    "jsonrpc": "2.0",
    "method": "braid.list",
    "params": { "filter": { "tag": "kegg" }, "limit": 50 },
    "id": 1
}
```

Both forms are equivalent. The explicit `capability.call` form supports additional fields like `gate` (for cross-gate routing) and `timeout`.

---

## Wire Format Reference: Braid Operations

These are the canonical parameter shapes accepted by sweetGrass. **Do not use legacy field names** (`content_hash`, `dataset`, `count`).

### braid.create

```json
{
    "data_hash": "blake3:abc123...",
    "name": "kegg",
    "tags": ["data-federation", "westgate"],
    "source_session": "session-uuid",
    "source_merkle_root": "blake3:def456...",
    "mime_type": "application/octet-stream"
}
```

Returns: `{ "braid_id": "uuid" }`

### braid.get

```json
{ "id": "braid-uuid" }
```

Returns: `{ "braid": { "id", "data_hash", "name", "tags", "created_at", ... } }`

### braid.get_by_hash

```json
{ "data_hash": "blake3:abc123..." }
```

Returns: `{ "braid": { ... } }` or null

### braid.list

```json
{
    "filter": {
        "tag": "kegg",
        "source_gate": "westGate",
        "mime_type": "application/json"
    },
    "order": "NewestFirst",
    "limit": 100,
    "offset": 0
}
```

Returns: `{ "total": 42, "items": [ ... ] }`

**Common mistake**: passing `{"dataset": "kegg"}` — there is no `dataset` field. Use `filter.tag`.

### braid.query

```json
{
    "filter": { "tag": "alphafold", "data_hash": "blake3:..." },
    "limit": 50
}
```

Returns: `{ "total": N, "items": [ ... ] }`

### braid.commit

```json
{ "braid_id": "uuid" }
```

Packages braid and forwards to loamSpine. Returns: `{ "committed": true, "spine_entry": "entry-id" }`

### convergence.batch_check

```json
{ "data_hashes": ["blake3:abc...", "blake3:def...", ...] }
```

Max 1000 hashes per call. Returns: `{ "results": [{ "hash": "...", "converged": true }, ...] }`

**Common mistake**: passing `{"dataset": "kegg", "limit": 5}` — there is no `dataset` param.

---

## Cross-Gate Routing

To call a capability on a primal running on a different gate, add a `gate` field:

```json
{
    "jsonrpc": "2.0",
    "method": "capability.call",
    "params": {
        "capability": "braid",
        "operation": "list",
        "args": { "filter": { "tag": "kegg" } },
        "gate": "strandGate"
    },
    "id": 1
}
```

biomeOS resolves the remote gate's Neural API endpoint via songBird mesh and forwards the `capability.call` there.

---

## Composition Signals (Signal Tier)

For multi-primal operations, use composition signals instead of individual capability calls:

```json
{
    "jsonrpc": "2.0",
    "method": "capability.call",
    "params": {
        "capability": "nest",
        "operation": "commit",
        "args": { "session_id": "...", "sign": true }
    },
    "id": 1
}
```

Signal tiers (`tower`, `node`, `nest`, `meta`) execute TOML composition graphs that coordinate multiple primals in sequence or parallel.

| Signal | Graph | Primals involved |
|--------|-------|-----------------|
| `nest.store` | `nest_store.toml` | nestGate → rhizoCrypt → loamSpine → sweetGrass |
| `nest.commit` | `nest_commit.toml` | rhizoCrypt → bearDog → nestGate → loamSpine → sweetGrass |
| `nest.retrieve` | `nest_retrieve.toml` | nestGate, loamSpine, sweetGrass (parallel) |
| `tower.publish` | `tower_publish.toml` | bearDog → songBird → skunkBat |
| `node.compute` | `node_compute.toml` | barraCuda → toadStool → coralReef |

---

## Handoff: primalSpring Registry Gaps

The following capabilities are **shipped in sweetGrass** but **missing from the central `capability_registry.toml`**. The primalSpring deployment team should register them:

### Missing from `[braid]` section:

- `braid.list` — enumeration/observability (shipped sweetGrass v0.8.0)
- `braid.query` — filter/search braids
- `braid.get_by_hash` — lookup by content hash
- `braid.batch_create` — bulk create (G31 pipeline)
- `braid.batch_commit` — bulk commit to loamSpine
- `braid.delete` — remove braid

### Missing entirely (no `[convergence]` section):

- `convergence.check` — single-hash convergence state
- `convergence.batch_check` — multi-hash convergence state (max 1000)

Both are owned by sweetGrass and stable. Without these in the registry, CI drift checks will miss them and Neural API translation startup won't pre-register the routing paths.

---

## Known Gaps (westGate AAR, Aug 8 2026)

westGate tested Neural API routing and documented the following gaps:

1. **`capability.call` times out** for provenance queries routed through neural-api. The process is alive (responds to method-not-found) but the proxy to backend primals hangs. Likely a graph executor config issue or missing route in the dispatch table. **Owner: biomeOS team.**

2. **sweetGrass not in capability registry**: biomeOS discovers 2,088 capabilities from 14+ primals but sweetGrass has not announced. It responds on its direct socket but `capability.call("braid.query", ...)` cannot route because the `braid` domain has no live endpoint. **Fix**: sweetGrass needs to call `primal.announce` at startup, or biomeOS needs its socket in the TOML domain bridge. **Owner: sweetGrass + biomeOS teams.**

3. **No `rpc.discover`**: No primal supports method introspection. Consumers must know signatures a priori. This spec provides the canonical reference until introspection is implemented.

4. **DAG sessions ephemeral**: `dag.session.list` returns 0 after dehydration. Sessions are discarded post-Merkle root. Spine commits persist the provenance chain, but session-level forensics require a `dag.session.history` RPC (future). **Owner: rhizoCrypt team.**

---

## Evolution Path: No Python

All interaction with the Neural API must be through Rust primals and `membrane` CLI commands. Python scripts are jelly string — they reimplement primal capabilities in a non-primal language, creating wire-format drift, socket-path coupling, and untested surface area.

westGate archived 2,085 lines of Python jelly on Aug 8 2026 (prov_inline.py, bulk_braid.py, revalidate_data.py, alphafold_prov_convoy.py, alphafold_bulk_download.py, convergence_check.py). The remaining `native_braid.py` is the last Python in the active pipeline and should be evolved into either:

1. A `membrane braid.*` CLI surface (cellMembrane) — for gate operators
2. A `sourdough validate neural-api` subcommand (sourDough) — for N2-N5 verification
3. Direct `capability.call` from Rust consumers (springs, gardens, protists)

The wire formats documented in this spec are the contract. Any new tooling implements against these formats in Rust, not Python.
