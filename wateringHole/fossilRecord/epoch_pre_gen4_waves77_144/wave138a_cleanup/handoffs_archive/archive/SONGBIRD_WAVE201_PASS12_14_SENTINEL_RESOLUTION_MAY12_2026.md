# Songbird Wave 201 — Pass 12/14 Sentinel Resolution

**Date**: May 12, 2026  
**Primal**: Songbird v0.2.1  
**Wave**: 201  
**From**: Songbird team  
**For**: All primal teams, primalSpring (validation), projectNUCLEUS (NAT shadow runs)

---

## Summary

Wave 201 resolves Songbird's two remaining pass items from the primalSpring
Ecosystem Wave Sync (May 12, 2026):

- **Pass 12 — VPS Relay**: Bidirectional data plane + CLI startup path
- **Pass 14 — `capability.resolve`**: Wire-format parity across transport paths

---

## Pass 12: VPS Relay Server — RESOLVED

### Problem

`TurnRelayServer` existed as library code but had:
1. No CLI startup path (deployers couldn't run it)
2. No client→peer data relay (Send Indication / ChannelData not handled)
3. Peer→client forwarded raw bytes instead of RFC-compliant framing

### Solution

**Bidirectional data plane (RFC 5766)**:
- `SendIndication` (0x0016): Client sends data with XOR-PEER-ADDRESS + DATA attributes → server extracts, checks permissions, forwards from relay socket
- `ChannelData` (0x4000-0x7FFF): Framed channel packets forwarded to bound peer
- `DataIndication` (0x0017): Peer→client traffic wrapped in proper STUN Data Indication
- Channel-aware forwarding: Uses ChannelData frames when binding exists

**CLI startup** (`songbird relay`):
```bash
songbird relay                           # default: 0.0.0.0:3478
songbird relay --bind 10.0.0.1 --port 4000
SONGBIRD_RELAY_BIND=0.0.0.0 SONGBIRD_RELAY_PORT=3478 songbird relay
```

### What this unblocks

- NAT shadow run (H2-3c): VPS relay is now deployable as `songbird relay`
- NestGate extracellular content distribution chain is complete:
  Songbird VPS relay → NAT shadow → NestGate extracellular → content sovereignty

---

## Pass 14: `capability.resolve` — RESOLVED

### Problem

The orchestrator path returned `{service_id, primal_name, endpoint, protocol,
capabilities}` while universal-ipc returned `{primal_id, socket,
virtual_endpoint, native_endpoint, capabilities, signature, signed_payload}`.
Downstream consumers got different shapes depending on transport.

### Solution

Harmonized `CapabilityResolveResponse` to include:
- `socket: Option<String>` — bare unix path when applicable
- `native_endpoint: String` — transport-qualified URI (`unix:///path` or `tcp://host:port`)
- `virtual_endpoint: String` — capability-addressed (`capability://domain@primal`)

Both paths now emit structurally equivalent responses.

---

## Verification

- `cargo clippy --workspace -- -D warnings` — zero warnings
- `cargo fmt -- --check` — clean
- 111 songbird-stun lib tests pass
- 27 root songbird lib tests pass
- 4 capability_resolve tests pass (new wire-format assertions)

---

## Pass Schedule Impact

| Pass | Before Wave 201 | After Wave 201 |
|------|----------------|----------------|
| **12** | 2/3 resolved (Songbird VPS relay "in progress") | **3/3 RESOLVED** — Songbird VPS relay complete |
| **14** | 2/5 resolved (Songbird `capability.resolve` remaining) | **3/5 RESOLVED** — Songbird `capability.resolve` complete |

Remaining sentinel blockers: ~~coralReef FECS/GPCCS~~ **RESOLVED** (Sprint 7 stability proof shipped).
Songbird is **CLEAR** through stadial gate. **All upstream primals are clear.**
