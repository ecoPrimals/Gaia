# rhizoCrypt — Wave 157e Gossip Injection Points

**Date**: Aug 10, 2026
**Wave**: 157e — NUCLEUS Composition Graph
**Primal**: rhizoCrypt v0.14.17

## Mandate

Wave 157e "All primals" mandate: *"Identify gossip injection points (what events should your primal announce to the mesh via swarmVine?)"*

## Audit Results

Comprehensive outbound event audit found rhizoCrypt talks to 5 ecosystem partners (sweetGrass, loamSpine, bearDog, songBird, biomeOS) but had **zero swarmVine/gossip interaction**.

## Gossip Injection Points Identified

Three DAG lifecycle events that cross-gate consumers care about:

| Event | Trigger | Wire payload | Why gossip? |
|-------|---------|-------------|-------------|
| `SessionDehydrated` | `dehydrate()` completes | `session_id`, `merkle_root`, `vertex_count` | Cross-gate consumers need to know permanent data is available for federation/checkout |
| `BatchDehydrated` | `dehydrate_batch()` completes | `session_count`, `session_ids` (capped at 64) | Bulk ingest completion signal for pipeline coordination |
| `Federated` | `impl_federate()` imports vertices | `session_id`, `imported_count`, `source_gate` | Data movement across gates — mesh awareness |

## Implementation

### Architecture

```text
dehydrate()       ──→ GossipEmitter.emit(SessionDehydrated) ──→ gossip.spread → swarmVine
dehydrate_batch() ──→ GossipEmitter.emit(BatchDehydrated)   ──→ gossip.spread → swarmVine
impl_federate()   ──→ GossipEmitter.emit(Federated)         ──→ gossip.spread → swarmVine
```

### Pattern

Follows `ProvenanceNotifier` pattern exactly:
- Discovers `gossip:relay` provider via `DiscoveryRegistry` at startup
- Falls back to `GOSSIP_RELAY_ENDPOINT` env var
- Non-fatal if unavailable — all `emit()` calls silently succeed
- Fire-and-forget: errors logged, never propagated to caller
- Transport-agnostic: uses `send_jsonrpc_request()` over `TransportEndpoint`

### Wire Format

```json
{
  "jsonrpc": "2.0",
  "method": "gossip.spread",
  "params": {
    "source_primal": "rhizoCrypt",
    "domain": "dag",
    "event": {
      "kind": "SessionDehydrated",
      "session_id": "...",
      "merkle_root": "...",
      "vertex_count": 42
    }
  },
  "id": 1
}
```

### New Files

| File | Lines | Content |
|------|-------|---------|
| `types_ecosystem/gossip/mod.rs` | 35 | Module docs + injection point documentation |
| `types_ecosystem/gossip/types.rs` | 155 | `GossipEvent` enum + 7 tests |
| `types_ecosystem/gossip/emitter.rs` | 220 | `GossipEmitter` struct + 4 tests |

### Modified Files

| File | Change |
|------|--------|
| `discovery/capability.rs` | Add `GossipRelay` variant + display + tests |
| `constants/methods.rs` | Add `GOSSIP_SPREAD_METHOD` |
| `constants/network.rs` | Add `GOSSIP_CONNECTION_TIMEOUT`, `GOSSIP_RESPONSE_TIMEOUT` |
| `types_ecosystem/mod.rs` | Register `gossip` module |
| `lib.rs` | Re-export `GossipEmitter`, `GossipEvent` |
| `rhizocrypt/mod.rs` | Add `gossip_emitter` field + accessor |
| `rhizocrypt/lifecycle.rs` | Connect gossip emitter at startup |
| `rhizocrypt/dehydration_ops.rs` | Inject at `dehydrate()` + `dehydrate_batch()` |
| `service_branch_ops.rs` (rpc crate) | Inject at `impl_federate()` |
| `graphs/rhizocrypt_deploy.toml` | Advertise `gossip_events` |

## Verification

```
cargo clippy --workspace --all-features -- -D warnings  # clean
cargo test --workspace --all-features                    # 1,835 pass, 0 fail
cargo fmt --check                                        # clean
cargo check --target x86_64-pc-windows-gnu               # clean
```

## Ant Colony Status

rhizoCrypt is now a gossip-ready scout. When swarmVine mesh is available (pending socket discovery fix + gossip enmeshment), rhizoCrypt will automatically announce:
- Permanent data availability (dehydration)
- Data movement across gates (federation)

No code changes needed when swarmVine comes online — just deploy with `GOSSIP_RELAY_ENDPOINT` or ensure `gossip:relay` is discoverable via songBird.
