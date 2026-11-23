# loamSpine — Wave 157e: Gossip Injection + Deep Debt

**Date**: August 10, 2026  
**Primal**: loamSpine  
**Wave**: 157e  
**Commit**: (pending)

---

## Summary

loamSpine now has full gossip injection infrastructure for the swarmVine mesh. Four data-domain events are emitted at key service operations, enabling "ant colony" activation. The gossip emitter is fire-and-forget — gossip failures never block spine operations.

Additional deep debt: SyncEngine IPC consolidated to shared helper (62 LOC saved), `AnchorTarget::chain_name()` added.

---

## Changes

### Gossip Module (`crates/loam-spine-core/src/gossip.rs` — 305 LOC)

| Type | Description |
|------|-------------|
| `GossipEvent` enum | 4 events: `CasHave`, `BraidHead`, `SpineSealed`, `AnchorPublished` |
| `GossipEmitter` | Connects to swarmVine UDS, sends `gossip.inject` JSON-RPC |
| `GossipHandle` | `Option<Arc<GossipEmitter>>` — `None` in standalone/test mode |
| Topic | All events use `"data"` topic |
| Key format | `<event_type>:<gate_id>:<spine_id>` |
| Fire-and-forget | `tokio::spawn` — emitter never blocks caller |

### Gossip Injection Points

| Event | Trigger | Source |
|-------|---------|--------|
| `cas.have` | Entry appended to any spine | `persist_tip()` — covers all 18 call sites |
| `braid.head` | Braid committed | `BraidAcceptor::commit_braid()` |
| `spine.sealed` | Spine sealed | `seal_spine()` |
| `anchor.published` | Public chain anchor recorded | `anchor_to_public_chain()` |

### Deep Debt

- **SyncEngine IPC consolidation**: `rpc_call()` replaced with `length_prefixed_rpc_call()` wrapper (95 LOC → 33 LOC, 62 net lines saved)
- **`AnchorTarget::chain_name()`**: New method for human-readable chain names in gossip and logging

### Capability Registry

- 4 `[gossip.*]` sections document injection points with topic, key format, trigger, and description
- `[consumed.gossip]` declares swarmVine as optional dependency

---

## Wire Contract

loamSpine emits to swarmVine's `gossip.inject` JSON-RPC method:

```json
{
  "jsonrpc": "2.0",
  "method": "gossip.inject",
  "params": {
    "topic": "data",
    "key": "cas.have:sporeGate:01234567-89ab-cdef-0123-456789abcdef",
    "value": {
      "event": "cas_have",
      "spine_id": "01234567-89ab-cdef-0123-456789abcdef",
      "entry_hash": "...",
      "height": 42
    },
    "ttl": 10
  },
  "id": 1
}
```

---

## Test Results

| Metric | Value |
|--------|-------|
| Tests | **1,820** (+24 from Wave 157a) |
| Source files | **216** (+1 `gossip.rs`) |
| Clippy | PASS (zero warnings, pedantic+nursery) |
| Fmt | PASS |
| Doc | PASS |
| TODOs/FIXMEs | 0 |
| Unsafe | 0 |
| Production unwrap/expect | 0 |

---

## Activation

To enable gossip on a deployed loamSpine instance:

1. Ensure swarmVine is running on the gate with a discoverable JSON-RPC socket
2. Set gossip emitter on the `LoamSpineService`:
   ```rust
   let emitter = Arc::new(GossipEmitter::new(
       PathBuf::from("/run/user/1000/biomeos/swarmvine.sock"),
       "sporeGate".into(),
   ));
   service.set_gossip(Some(emitter));
   ```
3. All subsequent spine operations will emit gossip events

---

## Remaining

- **biomeOS socket discovery** must resolve JSON-RPC socket (not tarpc) — gate ops fix
- **Cross-gate gossip peers** must be reachable on TCP 7800 for events to propagate
- **`gossip.subscribe`** streaming method (swarmVine P3) would enable reactive patterns
