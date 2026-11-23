# sweetGrass v0.7.42 — Deep Evolution: Stub Elimination + Error Chains + Store Parity

**Wave 67c | June 2, 2026 | strandGate**

## Summary

Comprehensive evolution pass eliminating stubs, preserving error chains, and achieving
store backend parity. Eight evolution targets resolved across handlers, core types,
store backends, and error infrastructure.

## Changes

### Stub Elimination

1. **tarpc `verify_anchor` evolved** — was returning `"pending_integration"` stub; now
   retrieves full braid, inspects `witness.is_signed()`, returns `"signed"` or
   `"unanchored"` with `data_hash` and `generated_at_time`. Parity with JSON-RPC handler.

2. **`lifecycle.status` enriched** — returns `uptime_secs`, `started_at`, `store_backend`,
   `method_count` (39), `capabilities_count` (39) alongside existing fields. Was hardcoded
   `"running"` only.

3. **`attribution.witness` persists attestation braids** — creates braid via
   `Braid::builder()` with attestation type, attested braid ID, and attester DID in
   metadata. Returns `witness_braid_id` in response. Was log-and-discard.

4. **`attribution.chain` accepts config** — optional `{ config: { max_depth, decay_factor } }`
   parameter. `QueryEngine::attribution_chain_with_config()` merges overrides into defaults.
   Was ignoring API-specified config on JSON-RPC path (tarpc already accepted it).

### Error Infrastructure

5. **`DispatchError` error chain preservation** — `source_detail: Option<String>` captures
   `{e:#}` alternate-formatted error chains from `internal()` helper. Propagated to
   JSON-RPC error `data` field for observability without leaking internals to clients.

### Core Type Evolution

6. **`BraidBuilder::generated_at_time`** — `const fn` fluent setter for deterministic
   timestamps in replay/backfill scenarios. Builder no longer hardcodes `now()`.

### Store Backend Parity

7. **NestGate filter parity** — `source_primal` and `niche` filters added to
   `matches_filter()`. `count()` fast-path `is_default` check extended. Mirrors memory
   backend behavior exactly.

### Test Coverage

8. **5 new handler tests** — `record_provenance` (with vertices, empty vertices, vertex
   without agent, minimal params) + pipeline merkle root verification.

## Metrics

| Metric | v0.7.41 | v0.7.42 |
|--------|---------|---------|
| Tests | 1,565 | 1,571 |
| LOC | 56,018 | 56,356 |
| Methods | 39 | 39 |
| Clippy warnings | 0 | 0 |
| Production `unwrap` | 0 | 0 |
| Unsafe blocks | 0 | 0 |

## Files Modified

- `crates/sweet-grass-service/src/server/mod.rs` — tarpc verify_anchor evolution
- `crates/sweet-grass-service/src/server/tests/attribution.rs` — updated assertions
- `crates/sweet-grass-service/src/handlers/jsonrpc/mod.rs` — DispatchError + lifecycle.status
- `crates/sweet-grass-service/src/handlers/jsonrpc/attribution.rs` — witness persistence + chain config
- `crates/sweet-grass-service/src/handlers/jsonrpc/tests_contribution.rs` — 5 new tests
- `crates/sweet-grass-core/src/braid/builder.rs` — generated_at_time setter
- `crates/sweet-grass-store-nestgate/src/store.rs` — source_primal/niche filters
- `crates/sweet-grass-query/src/engine/mod.rs` — attribution_chain_with_config

## Remaining Evolution Targets (v0.8.0 scope)

- Wire `AnchorManager` into `anchoring.anchor` handler (requires loamSpine live on LAN)
- `pipeline.attribute` outbound signing + anchoring (depends on above)
- `auth.check` token verification via BearDog
- REST `health_detailed` real integration probes
- Composition health readiness probes
- Privacy module integration into braid CRUD
- NestGate O(n) scan optimization
- redb multi-value hash index for content convergence

## Verification

```
cargo clippy --all-features  # 0 warnings
cargo test --all-features    # 1,571 passed, 0 failed
```
