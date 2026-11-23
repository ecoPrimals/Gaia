# Songbird Wave 199 — Pass 12 VPS Relay + Pass 14 capability.resolve

**Date**: May 12, 2026  
**Primal**: Songbird v0.2.1  
**Wave**: 199  
**Addresses**: Pass 12 (Sentinel Escalation), Pass 14 (Convergence)

---

## Pass 12: TurnRelayServer (VPS Sovereign Relay)

RFC 5766 TURN relay server implemented in `songbird-stun::turn_server`.

**What shipped**:
- `TurnRelayServer` struct — listens on a single UDP socket, handles
  Allocate/Refresh/CreatePermission/ChannelBind requests
- `CredentialStore` trait — abstracts authentication (BearDog beacon-tier keys)
- `StaticCredentialStore` — in-memory impl for testing and simple deployments
- Per-allocation ephemeral relay sockets with permission-gated forwarding
- Periodic cleanup of expired allocations (30s interval, configurable lifetime)
- STUN Binding Request compatibility (responds with XOR-MAPPED-ADDRESS)
- `TurnRelayStats` — allocations_created, active, packets/bytes relayed, auth failures
- Full client↔server integration: `TurnClient::allocate()` works against `TurnRelayServer`

**Architecture**:
```
Client (TurnClient) → [UDP] → TurnRelayServer (:3478)
                                 ├─ Allocate → binds ephemeral relay socket
                                 ├─ CreatePermission → adds peer IP to allow list
                                 ├─ ChannelBind → maps channel# to peer addr
                                 └─ Relay socket ↔ Permitted peers
```

**What this unblocks**: NestGate extracellular content distribution chain:
Songbird VPS relay → NAT shadow run → NestGate extracellular → content sovereignty.

**Remaining (ops, not code)**: VPS deployment (systemd unit, TLS wrapper, monitoring).

---

## Pass 14: capability.resolve enrichment

`CapabilityResolveResponse` on the orchestrator path now includes `primal_name`
(the owning primal's registered name). This achieves parity with the universal-ipc
path which already returns `primal_id`.

**Wire response shape** (orchestrator path):
```json
{
  "service_id": "svc-beardog-001",
  "primal_name": "bearDog",
  "endpoint": "/run/user/1000/biomeos/security.sock",
  "protocol": "json-rpc",
  "capabilities": ["crypto", "identity", "bonding"]
}
```

**What this unblocks**: Discovery debt across all springs — downstream consumers
can now resolve capability→primal without maintaining separate routing tables.

---

## Verification

- `cargo clippy --workspace -- -D warnings` → 0 warnings
- `cargo fmt -- --check` → clean
- 112 songbird-stun tests pass (4 new server integration tests)
- 1625 songbird-orchestrator lib tests pass
- Pre-existing flaky `service_monitor_*` timing tests (3) unchanged
