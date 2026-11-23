# songBird Wave 157d — Transport Convergence + Gossip Excision

**Date**: August 9, 2026  
**Wave**: 157d  
**Primal**: songBird  
**Gate**: eastGate  
**Focus**: Unified transport lifecycle, formal swarmVine delegation, PID P2 fix

---

## Summary

Completes the vertebrate evolution convergence: the 9 transport crate adapters (shipped in 157a) are now managed by a unified `TransportRegistry` in the orchestrator. Gossip methods are formally excised to swarmVine with active forwarding. PID management P2 resolved.

---

## Changes

### 1. TransportRegistry (songbird-orchestrator)

New module `crates/songbird-orchestrator/src/app/transport_registry.rs`:

- **Type-erased adapter**: `TransportEntry` uses boxed closures to wrap `CanonicalTransport` impls without requiring dyn-compatibility on the trait itself
- **`entry_from<T>(Arc<T>)`**: Generic constructor that erases the transport type
- **Lifecycle methods**: `start_all()`, `shutdown_all()`, `health_all()`, `count()`, `ready_count()`
- **Wired into**: `SongbirdOrchestrator` struct (field) + `stop()` lifecycle (graceful shutdown)
- **Tests**: 2 unit tests (lifecycle + empty safety)

### 2. CanonicalTransport Trait Evolution

Changed from `async fn` methods to `fn -> impl Future<Output = T> + Send`:
- Enables the boxed-closure adapter pattern in TransportRegistry
- No `async_trait` dependency needed
- All 9 transport impl crates unaffected (Rust desugars `async fn` to `impl Future + Send` when the trait requires it)

### 3. Formal Gossip Excision

`crates/songbird-universal-ipc/src/service/dispatch/mesh.rs`:
- `mesh.capabilities_announce` and `mesh.capabilities_revoke` now call `dispatch_gossip_delegated()` **before** falling back to local handler
- `dispatch_gossip_delegated()` discovers swarmVine socket, sends `gossip.forward` JSON-RPC (fire-and-forget)
- Platform-safe: `#[cfg(unix)]` for UDS, no-op on non-Unix
- `discover_swarmvine_socket()` promoted to `pub(super)` for cross-module access

### 4. PID Legacy Cleanup (P2 Fix)

`crates/songbird-orchestrator/src/process_manager.rs`:
- New `cleanup_legacy_pid_files()` called at `ProcessManager::new()`
- Probes `/tmp/songbird.pid`, `/var/run/songbird.pid`, `/var/run/songbird/songbird.pid`, `~/.local/share/songbird/songbird.pid`
- Only removes if referenced PID is not running (via `/proc/{pid}/stat` check)
- Addresses "3 path changes in 3 waves" debt

### 5. Clippy Fix

Fixed case-sensitive extension comparison in swarmVine socket discovery (`ipc_registry.rs`).

---

## Verification

```
cargo clippy --workspace --all-targets -- -D warnings   # ZERO warnings
cargo check --target x86_64-pc-windows-gnu              # clean cross-compile
cargo test -p songbird-orchestrator --lib transport_registry  # 2/2 pass
```

---

## Architecture After Wave 157d

```
Orchestrator
├── TransportRegistry (unified lifecycle)
│   ├── entry_from(StunTransport)
│   ├── entry_from(QuicTransport)
│   ├── entry_from(TlsTransport)
│   ├── entry_from(IgdTransport)
│   ├── entry_from(OnionRelayTransport)
│   ├── entry_from(TurnClientTransport)
│   ├── entry_from(TorTransport)
│   ├── entry_from(LineageRelayTransport)
│   └── entry_from(FederationTransport)
├── ProcessManager (PID with legacy cleanup)
└── Shutdown → transport_registry.shutdown_all()

Dispatch (mesh.capabilities_announce)
├── 1. Forward to swarmVine (gossip.forward)
└── 2. Local handler (fallback)
```

---

## What This Unblocks

- **Transport health dashboard**: `health_all()` can feed into observability/mesh status
- **swarmVine Phase 3**: Active forwarding means gossip propagation works as soon as swarmVine is deployed — no code change needed in songBird
- **Fleet PID hygiene**: Stale PID files from previous wave layouts no longer block startup on gates that upgraded in-place
