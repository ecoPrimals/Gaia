<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# coralReef — Wave 157g: G72 Dependency Pandemic Audit + Tier 1 Trims

**Date**: Aug 10, 2026
**Wave**: 157g (Sprint 14)
**Goal**: G72 Dependency Pandemic — audit coralReef's dependency surface, apply Tier 1 trims

---

## G72 Compliance Summary

coralReef is **already lean** relative to the ecosystem:
- Compiler crate (`coral-reef`) has **zero tokio dependency** — async is correctly isolated
- No `tokio ["full"]` anywhere — minimal feature sets
- No `reqwest`, `hyper`, `openssl`, `ring`, `async-trait`, `jsonrpsee`
- Already on `thiserror 2`, `tokio-serde 0.9`, `naga 28`, `tracing` (not env_logger)
- `sync`-wrapped-in-`async` limited to intentional `spawn_blocking` for compiler dispatch

## Tier 1 Trims Applied

| Change | Crate | Impact |
|--------|-------|--------|
| Gate `futures` + `tokio-util` behind `tarpc-transport` | coralreef-core | No longer pulled when feature disabled |
| Remove dead `tracing` dependency | primal-rpc-client | Zero source usage confirmed — pure dead dep |
| Remove duplicate `tokio` dev-dep | primal-rpc-client | Hygiene — workspace dep already provides |
| Move `tokio/process` to dev-deps | coralreef-core | Only used in e2e tests, not production |
| Remove redundant tokio feature re-declarations | coralreef-core | Workspace already provides `net`, `io-util`, `time` |

## Dep Surface After Trims

| Crate | Direct deps | tokio? | Status |
|-------|-------------|--------|--------|
| `coral-reef` | 6 (naga, thiserror, tracing, stubs, isa, bitview) | **ZERO** | Clean |
| `coral-reef-isa` | 1 (bitview) | No | Clean |
| `coral-reef-stubs` | 0 | No | Clean |
| `coral-reef-bitview` | 0 | No | Clean |
| `nak-ir-proc` | 3 (proc-macro2, quote, syn) | No | Clean |
| `primal-rpc-client` | 5 (bytes, tokio, serde, serde_json, thiserror) | Yes (async I/O) | Trimmed |
| `coralreef-core` | 15 + 4 optional | Yes (IPC server) | Trimmed |
| `amd-isa-gen` | 2 (quick-xml, thiserror) | No | Clean |

## Remaining Items (P2/P3 — deferred)

| Item | Priority | Notes |
|------|----------|-------|
| Version alignment: `nak-ir-proc` + `amd-isa-gen` at 0.1.0 | P2 | Cosmetic — path deps, no semver impact |
| `syn` feature `full` → minimal in `nak-ir-proc` | P3 | Build-time micro-optimization |
| Fuzz crate pulls full `coralreef-core` for sync `dispatch()` | P1 | Would need dispatch extraction — future sprint |
| Document serde `rc` is for `Arc`, not `Rc` | P3 | Prevents mis-audit |

## Tokio Architecture (verified correct)

```
coralreef-core (IPC server)
├── tokio — async IPC, shutdown signaling, heartbeats, timeouts
├── tarpc (optional) — binary RPC
└── spawn_blocking — dispatches sync coral-reef compiler

coral-reef (compiler)
└── zero tokio, zero async — pure sync compilation pipeline

primal-rpc-client (IPC client)
└── tokio — async TCP/Unix client (genuinely async, not wrapped)
```

No fake-async patterns. Architecture correctly isolates async (IPC layer) from sync
(compiler core). Consistent with G72 principle: tokio only where genuinely needed.

## Transitive Analysis

- `libc` only via tokio/mio (permanent, documented) + crypto RNG
- No `hyper`, `reqwest`, `openssl`, `ring`
- `bincode` 1.x via `tokio-serde` (tarpc requirement — isolated)
- Duplicate `hashbrown` versions (naga-internal) — upstream, not actionable
- Duplicate `getrandom` (0.2 crypto + 0.3 test) — acceptable
