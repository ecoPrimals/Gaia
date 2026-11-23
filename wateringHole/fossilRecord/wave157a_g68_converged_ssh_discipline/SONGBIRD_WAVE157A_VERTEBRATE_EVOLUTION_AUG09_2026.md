# songBird Wave 157a — Vertebrate Evolution

**Date**: August 9, 2026  
**Wave**: 157a  
**Primal**: songBird  
**Gate**: eastGate  
**Focus**: Shared `CanonicalTransport` trait + swarmVine delegation + RPC self-audit

---

## Summary

Vertebrate evolution phase: songBird develops internal skeletal structure by abstracting 9 transport crates behind a shared `CanonicalTransport` trait, formally delegating gossip-concern methods to swarmVine, and self-auditing its RPC surface against `capability_registry.toml`.

---

## Changes

### 1. `CanonicalTransport` Trait (songbird-types)

New trait in `crates/songbird-types/src/traits.rs`:

```rust
pub trait CanonicalTransport: Send + Sync {
    fn transport_name(&self) -> &'static str;
    async fn is_ready(&self) -> bool;
    async fn start(&self) -> SongbirdResult<()>;
    async fn shutdown(&self) -> SongbirdResult<()>;
    async fn health(&self) -> TransportHealth;
    fn endpoints(&self) -> Vec<TransportEndpoint>;
}
```

Plus `TransportHealth` struct (ready, active_connections, message).

### 2. Transport Adapters (9 crates)

Each transport crate now has a `transport_impl.rs` module with an adapter struct implementing `CanonicalTransport`:

| Crate | Adapter Struct | Transport Name |
|-------|---------------|---------------|
| songbird-stun | `StunTransport` | "STUN" |
| songbird-quic | `QuicTransport` | "QUIC" |
| songbird-tls | `TlsTransport` | "TLS" |
| songbird-igd | `IgdTransport` | "IGD" |
| songbird-onion-relay | `OnionRelayTransport` | "OnionRelay" |
| songbird-turn-client | `TurnClientTransport` | "TURN" |
| songbird-tor-protocol | `TorTransport` | "Tor" |
| songbird-lineage-relay | `LineageRelayTransport` | "LineageRelay" |
| songbird-network-federation | `FederationTransport` | "Federation" |

### 3. swarmVine Delegation

- `mesh.capabilities_announce` and `mesh.capabilities_revoke` marked as **delegated to swarmVine**
- Dispatch layer logs delegation intent via `tracing::debug`
- Handler retained as fallback (backward compat)
- Module-level documentation updated to mark delegation target
- `capability_registry.toml` declares these methods under `[capabilities.mesh_gossip]` with `owner = "swarmVine"` and `stability = "delegated"`

### 4. RPC Surface Self-Audit

Discovered 6 mesh methods implemented in code but not declared in registry:
- `mesh.probe_latency`, `mesh.enroll`, `mesh.gate_enroll`, `mesh.prune_stale`, `mesh.connectivity_check`, `mesh.throughput`

All now properly listed in `capability_registry.toml`.

---

## Verification

```
cargo clippy --workspace --all-targets -- -D warnings   # ZERO warnings
cargo check --target x86_64-pc-windows-gnu              # clean cross-compile
```

---

## What This Unblocks

- **Orchestrator refactor**: Transport lifecycle can now be managed uniformly (start all, health check all, graceful shutdown all)
- **swarmVine integration**: Gossip delegation formally declared; swarmVine team can implement forwarding shim
- **Fleet monitoring**: `TransportHealth` provides standardized health reporting across all transport layers
- **Production mesh**: Registry accuracy prevents the "phantom API" problem (westGate retrospective)

---

## Architecture After Wave 157a

```
songbird-types (trait definition)
    └── CanonicalTransport trait + TransportHealth
         ├── songbird-stun        → StunTransport
         ├── songbird-quic        → QuicTransport
         ├── songbird-tls         → TlsTransport
         ├── songbird-igd         → IgdTransport
         ├── songbird-onion-relay → OnionRelayTransport
         ├── songbird-turn-client → TurnClientTransport
         ├── songbird-tor-protocol→ TorTransport
         ├── songbird-lineage-relay→ LineageRelayTransport
         └── songbird-network-federation → FederationTransport

mesh dispatch
    └── capabilities_announce/revoke → swarmVine (delegated, local fallback)
```
