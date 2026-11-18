> **FOSSILIZED** — Wave 157k Enmeshment (Aug 16, 2026). Findings absorbed into ortho review + blurb.

# swarmVine AAR — Wave 157k Deep Interstadial Response

**Date**: Aug 14, 2026 09:20 | **Wave**: 157k | **From**: ironGate (swarmVine code team)
**Commit**: `31e3e0a` | **Repo**: `ecoPrimals/swarmVine` @ golgiBody

---

## Summary

Resolved **Remaining Infrastructure #3** (P2): swarmVine `gossip.relay` call to songBird was missing the required `topic` field. songBird returned `"Missing required field: topic"`, causing relay fallback to silently fail.

---

## Root Cause

`relay_via_songbird()` in `spread.rs` constructed the `gossip.relay` JSON-RPC params with `target_peer`, `target_method`, and `payload` — but omitted `topic`. songBird's `gossip.relay` handler requires `topic` to determine which gossip channel to route the relayed entries to.

---

## Fix Applied

Extract topic from the payload being relayed (`params.entries[0].topic`) and include it in the relay request params. Defaults to `"tower"` if no entries or topic is present (defensive — all real gossip batches contain entries with topics).

```rust
let topic = parsed_payload
    .pointer("/params/entries/0/topic")
    .and_then(serde_json::Value::as_str)
    .unwrap_or("tower");
```

The relay request now sends:
```json
{
  "method": "gossip.relay",
  "params": {
    "target_peer": "<addr>",
    "target_method": "gossip.spread",
    "topic": "<extracted from entries>",
    "payload": { ... }
  }
}
```

---

## Verification

| Check | Result |
|-------|--------|
| `cargo clippy --workspace --all-targets -- -D warnings` | Clean |
| `cargo test --workspace` | 187 tests pass (84 core + 97 server + 6 integration) |
| New test: `relay_request_includes_topic_field` | Validates topic extraction end-to-end |
| `cargo check --target x86_64-pc-windows-gnu` | Clean (prior fix intact) |

---

## swarmVine ironGate — All Items Status

| # | Item | Status |
|---|------|--------|
| RI #3 | gossip.relay missing topic param | **CLOSED** (`31e3e0a`) |
| RI #7 (prev) | Windows UDS build | **CLOSED** (`0e4cb75`) |
| P2 #2 (prev) | riboCipher inbound fallback | **CLOSED** (`63c8ccc`) |
| P2 #3 (prev) | mesh.relay → gossip.relay rename | **CLOSED** (`63c8ccc`) |
| RI #5 | rust-toolchain.toml GNU target | **songBird** (separate repo) |
| RI #8 | swarmVine not in biomeOS graph | **eastGate** (biomeOS team) |

---

## Note to southGate (Canary)

Both relay fixes are now in HEAD:
1. Method renamed from `mesh.relay` to `gossip.relay` (`63c8ccc`)
2. `topic` field now included in relay params (`31e3e0a`)

Once depot refreshes southGate's binary, the `"Missing required field: topic"` error should resolve.

---

*swarmVine ironGate: 0/0/0. All code-team items CLOSED. Ready for depot rebuild.*
