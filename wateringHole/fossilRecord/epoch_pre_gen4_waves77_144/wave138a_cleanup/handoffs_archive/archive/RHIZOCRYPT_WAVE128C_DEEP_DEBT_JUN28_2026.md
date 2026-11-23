# rhizoCrypt — Wave 128c Deep Debt Evolution

**Date**: Jun 28, 2026
**Version**: v0.14.17
**Commit**: `6495930`
**From**: eastGate overwatch

---

## Deliverables

### Security: CapabilityVerifier fail-closed (P0)

`CapabilityVerifier` now has a `fail_open` parameter wired from `EnforcementMode`:
- **Enforced mode** (`fail_open: false`): when no `crypto:signing` provider is discovered, tokens are treated as unverified. `MethodGate::check()` will reject the call. Previously this fell back to `PresenceVerifier` which granted `scopes: ["*"]` to any non-empty token.
- **Permissive mode** (`fail_open: true`): retains `PresenceVerifier` fallback for backward compatibility.
- Sync path (no Tokio runtime) also respects `fail_open`.
- 4 new tests exercise both modes.

### Production hardening (P1)

- **mesh/listener.rs**: Transport errors in `poll_events` no longer silently return `Ok(0)`. Consecutive errors tracked via `AtomicU32`; first 3 failures log at `debug`, then escalate to `warn` ("signing provider may be unavailable"). Counter resets on success.
- **dehydration_ops.rs**: "No signing provider" skip upgraded from `debug` to `warn`. Local-only commit reference message clarifies data will not reach the ledger.

### Adapter-agnostic documentation (P2)

- `mesh/listener.rs`, `mesh/types.rs`: all "bearDog" doc references replaced with "signing provider" / "crypto:signing provider"
- `songbird/config.rs`: discovery warning leads with `DISCOVERY_ENDPOINT` / `RHIZOCRYPT_DISCOVERY_ADAPTER`

### Architecture: constants.rs split (P3)

Split 662-line monolith into `constants/` module with 5 submodules:
- `network.rs` — ports, hosts, resource limits
- `ipc.rs` — timeouts, UDS paths, Neural API
- `methods.rs` — JSON-RPC method names
- `mesh.rs` — heartbeat, polling, trust domain
- `crypto.rs` — BTSP, genetics signals

Flat `pub use` re-exports preserve `crate::constants::NAME` API.

---

## Metrics

| Metric | Value |
|--------|-------|
| Tests | 1,870 |
| `.rs` files | 204 |
| Lines | ~61,057 |
| Max production file | 786 LOC (`method_gate.rs`) |
| Gate checks | fmt, clippy, doc, deny, test — all pass |

## Remaining Deferred

| Item | Priority | Notes |
|------|----------|-------|
| Coverage: mesh/listener 72%, dehydration_ops 75%, session 78% | P2 | Needs mock JSON-RPC server for poll path |
| JH-11 Ed25519 CapabilityVerifier | P1 | PresenceVerifier fallback now fail-closed in Enforced mode |
| axum 0.7 → 0.8, redb 2.x → 4.x, RustCrypto 0.13 | P3 | Dedicated migration waves |
| ComputeClient method surface | P1 | Shell only: discover/with_endpoint, no RPC methods |
