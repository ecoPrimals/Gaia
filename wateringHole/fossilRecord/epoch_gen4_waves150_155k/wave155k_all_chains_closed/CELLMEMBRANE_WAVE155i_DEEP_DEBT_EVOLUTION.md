# cellMembrane — Wave 155i Deep Debt Evolution Sweep

**Date:** 2026-07-29
**Author:** eastGate overwatch
**Scope:** 9 files, -135 net lines, 1,221 tests green, 0 clippy

---

## P0 Fixes

### Sandbox fail-closed (nucleus_restart.rs)

**Problem:** `sandbox_validate()` returned `true` on infra `Err`, bypassing the
sandbox safety gate and allowing untested binaries to be promoted.

**Fix:** Changed `Err(e)` arm to return `false`, failing the deploy. If the
sandbox infrastructure is broken, the cascade now halts instead of proceeding
with an unvalidated binary.

### Tower status self-knowledge elimination (tower/timer.rs)

**Problem:** `dispatch_tower_status()` hardcoded `songbird_ok`, `beardog_ok`,
`skunkbat_ok` variable names and JSON keys — a self-knowledge violation where
the membrane encoded primal-specific names instead of discovering them.

**Fix:** Refactored to `MembraneComposition::Tower.spec()` — discovers all
primals in the Tower composition from the service registry, probes each by
capability (`CryptoSigner` → BTSP probe, others → plain JSON-RPC).

---

## P1 Deduplication

| Extraction | From | To | Lines saved |
|-----------|------|-----|-------------|
| `resolve_primal_socket(binary)` | 3 per-primal socket resolvers in `tower/timer.rs` | 1 unified resolver with dynamic env var `MEMBRANE_SOCKET_{UPPER}` | ~25 |
| `resolve_relay_socket()` | Duplicate `resolve_songbird_socket()` in `enroll.rs` | Uses `resolve_primal_socket_paths()` from health module | ~8 |
| `run_step(args, context)` | 5 copy-pasted `Command::new("step")` blocks in `key_portal.rs` | 1 async helper with unified error handling | ~40 |
| `detect_crash_loops(threshold)` | 3 scan variants (sync/async/scan-only) in `crash_loop.rs` | Shared detection + thin wrappers per action | ~30 |
| `push_depot_to_remote()` | ~80 duplicated lines between `depot_sync_push` and `depot_sync_push_standalone` | Shared push loop, both callers delegate | ~50 |

## P2 Modernization

- **Let-chains:** `gate_configure.rs` nested `if let Some → if let Some → if let Some` → single let-chain
- **`let ... else`:** `firewall.rs` nested `if let Some(svc)` → `let Some(svc) else { continue }`
- **`format!("{}", x)` → `.to_string()`:** `tower/mod.rs`
- **Clippy fixes:** `redundant_closure`, `map_unwrap_or` in `timer.rs` and `enroll.rs`

---

## Health After Sweep

| Metric | Value |
|--------|-------|
| Tests | 1,221 (3 consolidated → 1) |
| Clippy warnings | 0 |
| Production unwraps | 0 |
| Unsafe code | 0 |
| Files >800L | 0 (largest: enroll.rs 797L) |
| TODOs/FIXMEs | 0 |
| Hardcoded IPs (production) | 0 |

---

## Files Changed

```
crates/cellmembrane-types/src/firewall.rs           (let-else)
crates/membrane-shadow/src/dispatch/gate_configure.rs (let-chains)
crates/membrane-shadow/src/gate/crash_loop.rs        (detect_crash_loops extraction)
crates/membrane-shadow/src/gate/enroll.rs            (resolve_relay_socket)
crates/membrane-shadow/src/gate/key_portal.rs        (run_step helper)
crates/membrane-shadow/src/plasmid/depot_sync.rs     (push_depot_to_remote)
crates/membrane-shadow/src/temporal/nucleus_restart.rs (sandbox fail-closed)
crates/membrane-shadow/src/tower/mod.rs              (format cleanup)
crates/membrane-shadow/src/tower/timer.rs            (registry-driven tower status)
```

## Upstream Notes

- **sporeGate ops:** Depot binary rebuild still pending — the `membrane` binary on
  golgiBody needs to be rebuilt from HEAD to include `gate.configure`/`gate.apply`/
  `gate.keys` and this sweep's fixes.
- **Nest Atomic gates:** The sandbox fail-closed fix means cascade-restart will now
  halt if sandbox infra is down. Gates should ensure `/run/membrane/sandbox/` exists.
