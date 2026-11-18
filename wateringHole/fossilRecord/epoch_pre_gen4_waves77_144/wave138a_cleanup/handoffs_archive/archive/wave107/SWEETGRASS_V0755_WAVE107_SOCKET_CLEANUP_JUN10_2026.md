# sweetGrass v0.7.55 — Wave 107 Handoff: Socket Cleanup + Doc Sync

**Date**: June 10, 2026  
**Primal**: sweetGrass  
**Gate**: strandGate  
**Wave**: 107  
**Tests**: 1,634 passing, 0 failed  
**Clippy**: Zero warnings (pedantic + nursery)

---

## Summary

Wave 107 delivered `PRIMAL-SOCKET-CLEANUP` for sweetGrass and synchronized
all documentation to v0.7.55:

1. **Socket cleanup** (Wave 107): Tier 5 socket resolution fallback fixed —
   bare `$TMPDIR/sweetgrass.sock` → `$TMPDIR/biomeos/sweetgrass.sock`. All 5
   resolution tiers now consistently land in a `biomeos/` subdirectory.
   Eliminates stale `/tmp/sweetgrass.sock` and `/tmp/provenance.sock`
   symlink artifacts. Unblocks `ProtectSystem=strict` systemd hardening.

2. **Doc sync** (Wave 107): 9 documentation files synchronized from stale
   v0.7.49 references to v0.7.55 — CONTEXT.md, DEVELOPMENT.md,
   QUICK_COMMANDS.md, CONTRIBUTING.md, sporeprint/validation-summary.md,
   specs/SWEETGRASS_SPECIFICATION.md, config/capability_registry.toml,
   graphs/sweetgrass_deploy.toml. Stale `ring`/`testcontainers` claims
   removed from CONTEXT.md and CONTRIBUTING.md.

---

## Key Changes

### Wave 107: PRIMAL-SOCKET-CLEANUP

| File | Change |
|------|--------|
| `uds.rs` | Tier 5 fallback: `temp_dir().join(sock_name)` → `temp_dir().join("biomeos").join(sock_name)` |
| `uds.rs` | Doc updated: tier 5 reads `$TMPDIR/biomeos/sweetgrass-{family_id}.sock` |
| `uds/tests/resolution.rs` | `di_temp_fallback` + `di_family_id_in_temp_fallback` hardened with exact path assertions |
| `tests_contribution.rs` | `unreadable_literal` clippy fix (timestamp separators) |
| `tests_cross_gate.rs` | `items_after_statements` clippy fix (import before first statement) |
| `transport.rs` | `#[expect(clippy::unwrap_used)]` on test module |
| `common.rs` (postgres tests) | `doc_markdown` backtick on `PostgreSQL` |

### Wave 107: Doc Sync (v0.7.49 → v0.7.55)

| File | Changes |
|------|---------|
| `CONTEXT.md` | Version, test count, dep audit (ring/testcontainers removed), transport ports, socket compliance |
| `DEVELOPMENT.md` | Version, test count |
| `QUICK_COMMANDS.md` | Test count |
| `CONTRIBUTING.md` | Removed stale `ring` via testcontainers claim; updated to zero-exception pure Rust |
| `sporeprint/validation-summary.md` | Version, test count, description, date |
| `specs/SWEETGRASS_SPECIFICATION.md` | Version |
| `config/capability_registry.toml` | Version |
| `graphs/sweetgrass_deploy.toml` | Version |

---

## Metrics

| Metric | Value |
|--------|-------|
| Version | v0.7.55 |
| Tests | 1,634 passing, 0 failed |
| Clippy | 0 warnings (pedantic + nursery) |
| Unsafe | 0 (`#![forbid(unsafe_code)]` all crates) |
| TODO/FIXME/HACK | 0 |
| C/ASM deps | 0 (pure Rust) |
| Advisory ignores | 0 |
| `ring` in dep tree | 0 |
| Max file size | 783 lines |
| Crates | 10 workspace members |
| Methods | 40 semantic + 10 wire-name aliases |

## Resolved FRAGOs

| FRAGO | Wave | Resolution |
|-------|------|------------|
| `PRIMAL-SOCKET-CLEANUP` | 107 | Tier 5 fallback fixed; zero `/tmp` bare artifacts |
| `TRANSPORT_ENDPOINT` | 100 | Local wire-compatible type + `connect_transport()` |
| `ring` elimination | 98 | testcontainers → DATABASE_URL; deny.toml hardened |
| Localhost-only defaults | 79b | `127.0.0.1:0` for HTTP + tarpc |

## Upstream Gaps for primalSpring

### NO REMAINING GAPS

sweetGrass has no open action items from Wave 107. All P2 directives
resolved. Codebase audit confirms zero TODO/FIXME/HACK, zero commented-out
code, zero orphan files, zero stale advisory ignores.

## Debris Audit (Wave 107)

| Category | Finding |
|----------|---------|
| TODO/FIXME/HACK | 0 |
| Commented-out code | 0 |
| Orphan `.rs` files | 0 |
| Backup/tmp artifacts | 0 |
| Stale deny.toml entries | 0 |
| Production `unwrap()` | 0 |
| Production `println!` | 0 |
| `#[allow]` attributes | 0 |
| Fossils (intentional) | `archive/sweet-grass-store-sled/`, `showcase/` — kept per fossilization standard |

## Depot Status

Binary at v0.7.54 on southGate mesh. Rebuild required for v0.7.55 socket
cleanup to take effect. Low urgency — only affects bare-fallback tier 5
(no env vars set at all).

---

*sweetGrass v0.7.55 — zero debris, zero `/tmp` artifacts, zero debt.*
