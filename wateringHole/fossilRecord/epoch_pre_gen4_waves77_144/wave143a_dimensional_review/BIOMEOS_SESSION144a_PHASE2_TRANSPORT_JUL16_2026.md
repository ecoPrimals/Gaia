# biomeOS — Wave 144a Handoff (Jul 16, 2026)

**Session**: Phase 2 Transport — Abstraction Over Gating
**Version**: v4.34 (commit `e19cceb2`)
**Gate**: Tower (eastGate)

---

## Completed: Phase 2 Transport Adoption

biomeOS now has a platform-agnostic IPC transport layer, joining **11/14 primals**
that have shipped Phase 2 transport.

### New Module: `biomeos-core::ipc`

| Type | Purpose |
|------|---------|
| `TransportStream` | Enum (`Unix` / `Tcp`) implementing `AsyncRead + AsyncWrite` |
| `connect_transport(endpoint)` | Platform-dispatched connection |
| `connect_transport_timed(endpoint, dur)` | With timeout |
| `TransportListener` | `bind_unix` / `bind_tcp` / `accept` |
| `send_jsonrpc_request(endpoint, req)` | Canonical JSON-RPC primitive |

### Platform Behavior

| Platform | `UnixSocket` | `AbstractSocket` | `TcpSocket` |
|----------|-------------|------------------|-------------|
| Linux | UDS direct | Abstract direct | TCP |
| macOS | UDS direct | Error (unsupported) | TCP |
| Windows | `{path}.port` → TCP | Error (unsupported) | TCP |

### Migrated Callers (transport `#[cfg]` stubs eliminated)

| Crate | Files | Before | After |
|-------|-------|--------|-------|
| `biomeos-core` | `atomic_transport.rs` | 3 separate connect fns | `jsonrpc_via_transport` |
| `biomeos-nucleus` | `client/transport.rs` | `#[cfg]` pair | Single `send_jsonrpc_request` |
| `neural-api-client` | `connection.rs` | `#[cfg]` pair | Single `connect_transport_timed` |
| `biomeos-primal-sdk` | provider, comms, caps | `#[cfg]` pairs | Local `ipc` module (no cycle) |
| `biomeos-federation` | discovery, unix_client | `#[cfg]` pairs | `send_jsonrpc_request` |
| `biomeos-api` | unix_server, live_disc, topology | `#[cfg]` pairs | `TransportListener` + probes |
| `biomeos-graph` | ai_advisor_discovery | `#[cfg]` pair | `send_jsonrpc_request` |

### Stats

- **42 files changed**, 1,028 insertions, 686 deletions
- **0 test failures** (448 + 553 passed across workspace)
- Both `x86_64-unknown-linux-gnu` and `x86_64-pc-windows-gnu` compile clean

---

## Remaining `#[cfg]` (non-transport, acceptable)

| Category | Files | Reason |
|----------|-------|--------|
| Unix signals (`SIGTERM`) | 5 | `tokio::signal::unix` has no Windows equiv |
| Proc filesystem (`/proc/*`) | 4 | Linux-only metrics |
| Socket permissions (chmod) | 3 | Unix file permissions |
| `biomeos-atomic-deploy` binary modes | 8 | Some still use direct UDS (lower priority) |
| `biomeos-spore` filesystem | 2 | Unix file mode checks |

These are NOT transport stubs — they're platform-specific features with correct behavior.

---

## Phase 2 Ecosystem Status (Updated)

| Primal | Status |
|--------|--------|
| songBird | SHIPPED |
| skunkBat | SHIPPED |
| petalTongue | SHIPPED |
| sweetGrass | SHIPPED |
| rhizoCrypt | SHIPPED |
| coralReef | SHIPPED |
| loamSpine | SHIPPED |
| barraCuda | SHIPPED |
| toadStool | SHIPPED |
| cellMembrane | SHIPPED |
| squirrel | IN PROGRESS |
| **biomeOS** | **SHIPPED** |
| bearDog | P2 |
| nestGate | Clean |

**12/14 primals shipped Phase 2 transport.**

---

## For Upstream

- biomeOS is now fully Phase 2 transport compliant
- `biomeos_core::ipc` module is available for any crate depending on `biomeos-core`
- `biomeos-primal-sdk` has its own `ipc` module (no cycle with core)
- The pre-existing `test_get_standalone_providers_filter_contract` failure is now **resolved** (was test assertion mismatch fixed during this session)
