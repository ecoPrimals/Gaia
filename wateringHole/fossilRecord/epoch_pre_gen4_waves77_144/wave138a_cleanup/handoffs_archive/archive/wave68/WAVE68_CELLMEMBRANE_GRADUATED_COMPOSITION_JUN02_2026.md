# Wave 68 cellMembrane — Graduated Composition Evolution

**Date:** 2026-06-02
**Gate:** ironGate
**Repo:** gardens/cellMembrane
**Wave:** 68

---

## Summary

Two-commit evolution sprint focused on graduated composition (primal-first
dispatch), bash→Rust evolution on VPS, and idiomatic Rust hardening.

## Completed Items

### Neural Bridge Integration (primal-first dispatch)

`try_bridge()` wired into `dispatch/mod.rs` for 12 commands:
- `gate.info`, `gate.pull`, `gate.check`
- `service.list`, `service.status`, `service.restart`, `service.logs`
- `repo.list`, `repo.create`
- `mirror.sync-all`
- `token.list`, `token.create`, `token.revoke`

Pattern: attempt biomeOS Neural API first → if primal handles it, return
immediately → if bridge unavailable/unrouted, fall through to shadow.

Zero-change graduation path: as primals come online, membrane-shadow
automatically delegates without code changes.

### Gate Evolution (bash→Rust on VPS)

- `gate.pull()`: uses `membrane temporal.cascade` if binary deployed, falls
  back to `cascade-pull.sh`
- `gate.check()`: uses `membrane temporal.check`, same fallback pattern

### Remaining Hardcoding Elimination

- `forgejo.rs`: `/opt/forgejo` hardcode → `forgejo_work_path()` config chain
  (`FORGEJO_WORK_DIR` env → derive from data_dir → default)
- `impulse/primal.rs`: `discover_socket()` aligned with bridge.rs XDG pattern
  (`MEMBRANE_SOCKET_{NAME}` env → XDG_RUNTIME_DIR → /tmp fallback)
- `temporal.rs` 895L→843L: `resolve_workspace_root()` promoted to crate root

### Idiomatic Rust Hardening

- `PushResult` struct: replaces silent push (fire-and-forget) with structured
  success/failure reporting per remote
- `#[must_use]` sweep: 12 pure functions across 7 modules
- `Display` impls: `GateIdentity`, `IdentitySource`
- `git_ops.rs`: `git_output()`, `git_success()`, `rev_list_count()` async
  utilities (shared across temporal, dispatch, freshness)

### Shared Utility Extraction

- `resolve_workspace_root()` promoted from temporal.rs to lib.rs (used by
  6 modules: config, temporal, freshness, git_ops, dispatch/temporal, dispatch/data)
- `git_output()` / `git_success()` / `rev_list_count()` moved to git_ops.rs
  from temporal.rs private helpers

## Metrics

| Metric | Value |
|--------|-------|
| Tests | 209 passing (+2 bridge tests) |
| Clippy | 0 warnings |
| Net lines | +358, -109 |
| Files changed | 20 |
| Bridge commands | 12 (auto-delegates when primal available) |

## Upstream Notes

- ring transitive dependency is not cellMembrane's concern — Songbird/BearDog
  (southGate Tower Atomic) own the crypto surface
- VPS `membrane` binary deployment enables Rust cascade on golgi (currently
  falls back to bash gracefully)
- S4 formal gate awaiting southGate bearDog config (blocked, not actionable)
- Forgejo Actions CI shadow is P2, Wave 70+
