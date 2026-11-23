# sweetGrass v0.7.48 — Zero Hot-Path Env Reads (Wave 78b)

**Date**: June 4, 2026
**From**: strandGate / sweetGrass
**Version**: v0.7.47 → v0.7.48

## Summary

Completed the env snapshot evolution started in v0.7.47 by threading
pre-resolved URIs through the remaining hot-path code:

- **BraidFactory** — `with_context()` injects `BraidContext` at construction;
  all 6 `Braid::builder()` calls (including `contribution.rs`) use the factory
  context instead of `BraidContext::default()` (which reads env)
- **QueryEngine** — `with_ecop_vocab()` passes the snapshotted vocabulary URI
  to `ProvoExport`; PROV-O JSON-LD exports no longer read env vars
- **ProvoExport / JsonLdDocument** — `with_ecop_vocab()` constructors on both
  types avoid runtime `env::var` for the ecoPrimals namespace
- **trust.event handler** — builds `BraidContext::with_uris()` from
  `state.ecop_vocab_uri` / `state.ecop_base_uri` instead of default
- **AppState constructors** — all three (`new_memory`, `with_store`,
  `with_self_knowledge`) now snapshot `BraidContext` for the factory and
  thread `ecop_vocab_uri` into the `QueryEngine`

## Result

Zero `env::var` reads on any hot path. Every env-sensitive value is resolved
exactly once at startup and shared via `AppState` → factory/query/handler.

## Metric Deltas

| Metric | v0.7.47 | v0.7.48 | Delta |
|--------|---------|---------|-------|
| Tests | 1,623 | 1,623 | 0 |
| LOC | 60,624 | ~60,650 | +26 |
| Source files | 209 | 209 | 0 |
| Methods | 40 | 40 | 0 |

## Forward Targets

- **`auth.check` completion** — blocks on bearDog FRAGO delivery
- **btsp/server.rs (766L), btsp/transport.rs (763L)** — approaching 800L
  threshold; candidate for test extraction if they grow
- **Holding steady** per strandGate directive: no new code work until bearDog
  delivers `auth.events.subscribe`
