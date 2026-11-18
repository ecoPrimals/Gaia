# sweetGrass v0.7.61 — Pure Rust Dogma: PostgreSQL/sqlx Removal

**Wave:** 133b Pattern Hardening  
**Date:** 2026-07-07  
**Primal:** sweetGrass  
**Version:** 0.7.60 → 0.7.61  

## Summary

Hard deprecation and removal of `sweet-grass-store-postgres` crate and all `sqlx`
dependencies. sweetGrass is now fully pure Rust — no external database requirements,
no compile-time proc macros connecting to live services, no Docker needed for any
workflow.

## What Was Removed

| Item | Rationale |
|------|-----------|
| `crates/sweet-grass-store-postgres/` | 130+ transitive deps, compile-time DB requirement |
| `sqlx` workspace dependency | Pure Rust dogma — banned in `deny.toml` |
| `docker-compose.yml` | Only existed for PostgreSQL |
| `BraidBackend::Postgres` enum variant | Dead code path |
| `StorageBackend::Postgres` config variant | Dead config |
| `DATABASE_URL` env var / CLI arg | No longer applicable |
| `StorageConfig` postgres fields | `database_url`, `pg_max_connections`, `pg_min_connections` |
| All postgres-related tests | Factory, integration, migration tests |
| Docker CI references in docs | README, DEVELOPMENT, QUICK_COMMANDS, CONTRIBUTING |

## What Was Hardened

- `deny.toml`: `sqlx`, `sqlx-core`, `sqlx-postgres`, `sqlx-sqlite`, `sqlx-mysql`,
  `libsqlite3-sys` all explicitly banned with "pure Rust dogma" rationale
- Lockfile: ~130 fewer transitive dependencies (313 packages total)
- `crossbeam-epoch` updated 0.9.18 → 0.9.20 (RUSTSEC-2026-0204)
- `env.example`, `scripts/check.sh`, `CONTEXT.md`, cursor rules all purged

## Storage Architecture (post-removal)

| Backend | Use Case | Pure Rust |
|---------|----------|-----------|
| Memory | Testing, development | ✅ |
| redb | Production (recommended) | ✅ |
| NestGate | Ecosystem delegated storage | ✅ (IPC) |

## Verification

- `cargo fmt --all -- --check` ✅
- `cargo clippy --all-features --all-targets` zero warnings ✅
- `cargo deny check` advisories ok, bans ok, licenses ok, sources ok ✅
- `cargo test --all-features` 583+ pass ✅
- `cargo build --release --bin sweetgrass` 11MB binary ✅

## Ecosystem Impact

- sweetGrass was the **only** primal using `sqlx`/PostgreSQL
- All other primals use `redb`, filesystem, or in-memory storage
- This brings sweetGrass into full alignment with ecosystem pure Rust standards
- Binary size anomaly (aarch64 101% of x86) expected to normalize

## For Upstream

- No other primals affected — `sqlx` was unique to sweetGrass
- `deny.toml` template can now include sqlx ban for all primals
- No migration path needed — redb is the ecosystem standard
