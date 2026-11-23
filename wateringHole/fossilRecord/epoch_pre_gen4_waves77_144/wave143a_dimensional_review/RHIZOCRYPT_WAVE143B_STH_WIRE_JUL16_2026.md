# rhizoCrypt — Wave 143b Handoff

**Date**: Jul 16, 2026  
**Commit**: `ce3d534`  
**Tests**: 1,905 | **Coverage**: 93.86% | **Files**: 216 `.rs` | **Lines**: ~62,042

## SessionTreeHash CAC L5 — Full Wire

`SessionTreeHash` (shipped as newtype in 142b) is now wired through the
complete RPC stack:

- **tarpc trait**: `session_tree_hash(SessionId) -> SessionTreeHash`
- **JSON-RPC**: `dag.session.tree_hash` method in handler dispatch
- **MCP tools**: registered in `tools.call` dispatcher
- **METHOD_CATALOG**: entry in niche (28 methods, 8 domains)
- **DashMap cache**: `tree_hash_cache: DashMap<SessionId, SessionTreeHash>`
  with invalidation on `append_vertex`, `discard_session`, and GC sweep
- **Client**: `RhizoCryptRpcClient::session_tree_hash()`
- **Metrics**: `RpcMethod::SessionTreeHash` variant + Prometheus counter
- **Tests**: handler test, client transport test, method classification test

CAC L5 FRAGO is now SHIPPED. `dag.session.tree_hash` returns the same
32-byte BLAKE3 root as `dag.merkle.root` but branded as a
content-addressable session state key with caching.

## Transport API Cleanup

- **Deleted**: `TransportHint` enum + `preferred_transport()` + `PlatformKind`
  (deprecated in 142b, zero production callers)
- **Deleted**: `platform_hints.rs` test file (16 tests for dead API)
- **Deprecated**: `AdapterFactory::create(&str)` → use `from_transport()`
- **Deprecated**: `with_endpoint(&str)` on all 5 capability clients
  (signing, storage, permanent, compute, provenance)

All production paths now use `AdapterFactory::from_transport(&TransportEndpoint)`.
String-based paths remain for backward compatibility but are marked for removal.

## Known Forward Work

- `TransportHint` → DONE (deleted)
- `with_endpoint` + `AdapterFactory::create` → deprecated, delete in 0.14.19
- Integration traits (`SigningProvider` et al.) use RPITIT — not object-safe
  for `dyn` dispatch. Evolve to `Pin<Box<dyn Future>>` when ecosystem needs it.
- 28/28 methods in METHOD_CATALOG (was 27)

## Metrics

| Metric | Value |
|--------|-------|
| Tests | 1,905 |
| Coverage | 93.86% |
| `.rs` files | 216 |
| Lines | ~62,042 |
| Max file | ~624 lines (store.rs) |
| Clippy | 0 warnings (pedantic+nursery) |
| `cargo deny` | clean |
