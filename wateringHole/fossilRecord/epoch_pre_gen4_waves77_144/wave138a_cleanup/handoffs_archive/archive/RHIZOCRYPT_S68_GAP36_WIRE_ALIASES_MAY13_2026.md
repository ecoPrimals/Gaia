# rhizoCrypt S68 — GAP-36 Resolution: `provenance.*` Wire-Name Aliases

**Date**: May 13, 2026
**Owner**: rhizoCrypt
**Scope**: GAP-36 (Provenance trio payloads) + GAP-34/35 (wire name reconciliation)

---

## Summary

Downstream springs (primalSpring `domain_contract_sweep`, healthSpring Nest
atomic) call `provenance.session.create` / `provenance.event.append` when
exercising rhizoCrypt's DAG surface. rhizoCrypt's canonical domain is `dag`,
and prior to this change, `provenance.*` method names hit the `MethodNotFound`
catch-all — returning a JSON-RPC error (`-32601`), not "empty sockets."

GAP-36 was reported as "UDS handlers accept connections but return no JSON-RPC
payloads." The actual issue was that the JSON-RPC responses were error responses
(`MethodNotFound`), which downstream interpreted as non-functional.

## Changes

### Wire-name alias layer (`niche.rs`)

`normalize_method()` now maps all 21 `provenance.*` methods to their `dag.*`
canonical equivalents. This operates at the normalization layer, transparent
to dispatch, readiness gate, and method gate.

Full alias table:
- `provenance.session.{create,get,list,discard}` → `dag.session.*`
- `provenance.event.{append,append_batch}` → `dag.event.*`
- `provenance.vertex.{get,query,children}` → `dag.vertex.*`
- `provenance.{frontier,genesis}.get` → `dag.{frontier,genesis}.get`
- `provenance.merkle.{root,proof,verify}` → `dag.merkle.*`
- `provenance.slice.{checkout,get,list,resolve}` → `dag.slice.*`
- `provenance.dehydration.{trigger,status}` → `dag.dehydration.*`
- `provenance.dehydrate` → `dag.dehydrate` (legacy)

### Semantic aliases for biomeOS routing

`SEMANTIC_ALIASES` updated with the most common `provenance.*` → `dag.*`
mappings so biomeOS `capability.call` routing also resolves correctly.

### GAP-34/35 reconciliation

- `dag.*` is canonical for rhizoCrypt
- `provenance.*` is the downstream wire name used by springs exercising
  the DAG surface through the provenance trio lens
- Both are now valid — normalization is transparent

## Verification

```bash
# Test provenance.session.create over UDS
echo '{"jsonrpc":"2.0","method":"provenance.session.create","params":{"session_type":"General"},"id":1}' | socat - UNIX-CONNECT:/run/rhizocrypt.sock
# Should return: {"jsonrpc":"2.0","result":"<session-id>","id":1}

# Test provenance.event.append
echo '{"jsonrpc":"2.0","method":"provenance.event.append","params":{"session_id":"<id>","event_type":{"Custom":{"domain":"security","event_name":"audit"}}},"id":2}' | socat - UNIX-CONNECT:/run/rhizocrypt.sock
# Should return: {"jsonrpc":"2.0","result":"<vertex-id>","id":2}
```

## Tests

6 new tests:
- `normalize_method_maps_provenance_to_dag` (17 alias assertions)
- `normalize_method_preserves_non_aliased` (3 assertions)
- `test_provenance_session_create_alias`
- `test_provenance_event_append_alias`
- `test_provenance_dehydrate_alias`
- `test_provenance_full_pipeline_via_aliases` (full session lifecycle via `provenance.*`)

### Enriched `dag.session.get` — `dag_summary` proposal (projectNUCLEUS)

projectNUCLEUS proposed `rhizocrypt.dag_summary` for lithoSpore provenance
chains. `dag.session.get` now serves this role — `SessionInfo` enriched with:

- `agents: Vec<Did>` — all participant DIDs
- `genesis: Vec<VertexId>` — root vertex IDs (no parents)
- `frontier: Vec<VertexId>` — tip vertex IDs (no children)

New fields use `#[serde(default)]` — existing JSON consumers are unaffected.
No new method needed; `dag.session.get` is the canonical session summary.

## Tests

7 new tests:
- `normalize_method_maps_provenance_to_dag` (17 alias assertions)
- `normalize_method_preserves_non_aliased` (3 assertions)
- `test_provenance_session_create_alias`
- `test_provenance_event_append_alias`
- `test_provenance_dehydrate_alias`
- `test_provenance_full_pipeline_via_aliases` (full session lifecycle via `provenance.*`)
- `test_session_get_returns_summary_fields` (agents, genesis, frontier verified)

## Stats

- 1,638 tests passing (all features)
- 173 `.rs` files, ~53,396 lines
- 0 clippy warnings, 0 fmt diffs
- Deep debt: 12-category audit clean

## Wire compatibility

- **No breaking changes** — `dag.*` methods continue to work exactly as before
- `provenance.*` methods now resolve instead of returning `MethodNotFound`
- `SessionInfo` new fields omitted by old callers default to empty (backward-compatible)
- Callers using either naming convention are fully supported
