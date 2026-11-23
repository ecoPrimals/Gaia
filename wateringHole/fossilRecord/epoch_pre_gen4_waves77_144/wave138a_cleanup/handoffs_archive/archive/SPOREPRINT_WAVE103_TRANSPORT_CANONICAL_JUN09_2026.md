# sporePrint Wave 103 — Canonical Transport + Env Injection

**Date:** 2026-06-09
**Gate:** flockGate (WAN)
**Primal:** sporePrint v0.3.0
**Wave:** 103

## Delivered

### Transport Injection — Ecosystem Canonical Parity

sporePrint now matches the ecosystem wire format for `TransportEndpoint`:

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "transport")]
pub enum TransportEndpoint {
    #[serde(rename = "uds")]   Uds { path: String },
    #[serde(rename = "tcp")]   Tcp { host: String, port: u16 },
    #[serde(rename = "mesh_relay")] MeshRelay { peer_id: String, capability: String },
}
```

### `TRANSPORT_ENDPOINT` Env Var Acceptance

sporePrint now accepts the launcher-injected transport endpoint:

```bash
# Launcher injection (Songbird ipc.resolve output → env var):
TRANSPORT_ENDPOINT='{"transport":"tcp","host":"192.168.1.173","port":9100}' \
  spore-validate cas-push --generate
```

Resolution priority:
1. `--socket` CLI flag (explicit override)
2. `TRANSPORT_ENDPOINT` env var (launcher/Songbird injection)
3. Socket discovery (legacy `NESTGATE_SOCKET` / XDG probing)

### TCP Transport Implemented

`connect_transport(TransportEndpoint::Tcp { .. })` now establishes TCP connections.
This enables cross-gate CAS push when NestGate is on a remote node.

### MeshRelay Defined (Stub)

Wire format accepted and deserialized. Returns clear error until Songbird
Phase 2 M1 (`ipc.resolve` structured endpoints) ships.

## Metrics

| Metric | Wave 85 | Wave 103 |
|--------|---------|----------|
| Tests | 128 | 133 |
| Transport variants | 1 (Uds) | 3 (Uds, Tcp, MeshRelay) |
| Serde format | None | Canonical `#[serde(tag)]` |
| Env injection | No | `TRANSPORT_ENDPOINT` |

## Status

- **Transport injection**: COMPLETE (sporePrint is NOT a server — connect-only)
- **Self-knowledge**: Zero violations (no imported transport types)
- **WAN mesh**: sporePrint doesn't need mesh enrollment (CLI tool). songBird on
  flockGate is the mesh participant for WAN validation.
- **133 tests, zero clippy, zero C deps**
