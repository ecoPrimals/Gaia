# projectFOUNDATION — Wave 59b Deep Debt Resolution

**From:** projectFOUNDATION (sporeGarden/gardens)
**To:** primalSpring coordination (eastGate)
**Context:** Wave 59b, primalSpring v0.9.30, biomeOS v3.84 pending
**Date:** 2026-05-28
**Gate:** irongate

---

## Summary

Deep debt resolution pass addressing critical path bugs, type safety,
dependency cleanup, and IPC wiring. All changes committed and pushed.
Upstream audit requested.

## What Shipped

| Deliverable | Impact |
|-------------|--------|
| **ThreadIndex path resolution** | Pipeline uses `data_sources`/`data_targets` fields, not guessed paths. Fixes silent no-op on real manifests. |
| **Vacuous PASS eliminated** | Missing targets with threads selected → FAIL (was incorrectly PASS). |
| **IPC Phases 1/2/7 wired** | `HealthTriad` + `dag.session.create/commit` with graceful degradation. |
| **Type-safe enums** | `ExecType`, `IsolationLevel`, `SkipCondition` replace stringly-typed fields. |
| **`Cow<str>` zero-copy** | `expand_env_placeholder()` borrows when no `${...}` present. |
| **Executor timeout** | `try_wait()` poll loop with `kill()` — was ignored `_timeout` param. |
| **Fetcher `request_timeout`** | Wired into `ureq::Agent` config builder. |
| **`chrono` eliminated** | Replaced with stdlib epoch math (Hinnant's civil date algorithm). |
| **Unused deps removed** | `chrono`, `tracing` (core), `bytes` (fetch) — leaner compile graph. |
| **`primal_names` wired** | CLI health uses `VALIDATION_PRIMALS` instead of hardcoded list. |
| **`env_keys` wired** | Config uses centralized constants, not bare env var strings. |
| **CI split** | Library clippy (strict) + test clippy (allow `unwrap_used`). |

## Metrics

| Metric | Before (Wave 59) | After (Wave 59b) |
|--------|------------------|-------------------|
| Tests | 107 | 118 |
| Lines of Rust | ~5,076 | 6,416 |
| Library warnings | 0 | 0 |
| Binary size | 3.0 MB | 3.0 MB |
| Largest file | 439 L | 566 L (pipeline.rs) |
| External deps | blake3, chrono, serde, tokio, ureq, walkdir... | blake3, serde, tokio, ureq, walkdir (chrono removed) |
| Critical bugs | 4 (path resolution, vacuous PASS) | 0 |

## Phase C Remaining (Production Parity)

| Item | Status | Blocker |
|------|--------|---------|
| FN-5: Database-specific fetch in pipeline Phase 3 | Open | None |
| FN-5: NestGate RPC registration in Phase 4 | Open | biomeOS v3.84 on VPS |
| FN-5: toadStool dispatch in Phase 5 | Open | toadStool composition |
| FN-5: Full `ProvenanceSession` trio (Phases 2/7) | Open | rhizoCrypt/loamSpine/sweetGrass live |
| FN-1: `backfill --write` TOML mutation | Open | None |
| CI-R: Forgejo Actions shadow CI | Open | S4 sovereignty gap |
| Data dir unification (`.data/` vs `data/fetched/`) | Open | Convention decision |

## For primalSpring Audit

1. Confirm `primal_names::VALIDATION_PRIMALS` alignment with orchestrator constants
2. Verify `PhasedIpcError` phase classification matches upstream semantics
3. Review `dag.session.create/commit` RPC contract (pipeline uses minimal params)
4. Advise on `ProvenanceSession` adoption path for full trio commit
5. Confirm `family.id` RPC availability on biomeOS v3.84

## Crate Architecture (Final Phase B)

```
foundation-core    (45 tests)  Types, TOML, config, env_keys, primal_names
foundation-ipc     (30 tests)  JSON-RPC 2.0, HealthTriad, ProvenanceSession, PhasedIpcError
foundation-fetch   (15 tests)  SourceFetcher, ArtifactRegistry, BLAKE3 hasher
foundation-validate (19 tests) 8-phase pipeline, executor (timeout), comparison, report
foundation-cli     (6 tests)   UniBin: validate, fetch, health, targets, backfill
integration tests  (3 tests)   Full pipeline with fixtures
```

---

*Wave 59b. Phase B sealed. Debt resolved. Phase C unblocked.*
