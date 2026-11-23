# Songbird Wave 205 — UB-1 TURN Client Library + primal.announce

**Date**: May 15, 2026  
**Wave**: 205  
**Audit Reference**: Upstream Pattern Escalation (May 15, 2026)  
**Gaps Resolved**: UB-1 (HIGH), primal.announce adoption, signal-tier declaration

---

## UB-1: `songbird-turn-client` Crate (HIGH)

**Problem**: lithoSpore implemented a full discovery chain (env → UDS → TURN → standalone) but the TURN leg was stubbed. Songbird had STUN/TURN wire-compliant code (Waves 196-197) but no reusable client library for downstream consumers.

**Solution**: New `songbird-turn-client` crate (31st workspace member) providing:

### `TurnSession` API

```rust
let config = TurnSessionConfig::new(server_addr, credentials, peer_addr);
let session = TurnSession::connect(config).await?;

// Send data through TURN relay
session.send(b"json-rpc payload").await?;

// Receive data from peer via TURN relay
let n = session.recv(&mut buf).await?;

// Refresh allocation before expiry
session.refresh(600).await?;

// Release allocation
session.close().await?;
```

### Data Plane

- **`ChannelData` framing** (default): Efficient 4-byte header after `ChannelBind`
- **`SendIndication`/`DataIndication`** fallback: Full STUN framing when no channel bound
- Automatic demultiplexing: distinguishes STUN responses from ChannelData on same socket

### Configuration

- `TurnSessionConfig::new(server, creds, peer)` — sensible defaults
- `.without_channel()` — disable ChannelData, use Send/Data Indication
- `.with_recv_timeout(duration)` — override 30s default
- `.with_local_bind(addr)` — override ephemeral bind

### Also Exposed from `songbird-stun`

- `TurnClient::server_addr()` — public accessor
- `encode_xor_peer_address()` — re-exported for data-plane framing
- `StunAttribute::decode_address()` — now `pub` (was `pub(crate)`)

### Tests

7 unit tests + 1 doctest covering config, ChannelData roundtrip, DataIndication parsing, detection logic.

---

## `primal.announce` Adoption (biomeOS v3.57)

### What Shipped

- `PrimalMethod::Announce` variant in `songbird-types` method enum
- `"primal.announce"` wire name in both `as_wire_str` and `from_wire_str`
- `primal_announce()` handler returning atomic registration payload:

```json
{
  "primal": "songbird",
  "version": "0.2.1",
  "domain": "network",
  "provided_capabilities": ["network.discovery", "network.federation", ...],
  "consumed_capabilities": ["security", "crypto"],
  "signal_tiers": ["tower"],
  "endpoints": { "transports": ["unix_socket", "tcp"], "protocols": ["json-rpc", "ndjson", "btsp"] },
  "methods": [...all callable methods...],
  "status": "ready"
}
```

- Routed on both orchestrator UDS and TCP IPC transport
- `primal.info` and `primal.capabilities` also now routed on orchestrator UDS

### Signal-Tier Membership

Songbird declares `signal_tiers: ["tower"]` — it is a Tower atomic primal (network orchestration alongside bearDog and skunkBat).

---

## Verification

- 0 clippy warnings (31 crates, full workspace `--exclude songbird-types -D warnings`)
- 27 socket routing tests, 5 IPC handler tests, 7 turn-client tests — all pass
- `cargo fmt -- --check` clean

---

## What This Unblocks

- **lithoSpore Tier 2 geo-delocalized validation**: `discover_from_turn()` can now use `songbird-turn-client` to relay RPC through the cellMembrane relay
- **biomeOS composition**: `primal.announce` atomic registration with signal-tier
- **Downstream capability discovery**: `primal.announce` response carries full method list + capabilities
