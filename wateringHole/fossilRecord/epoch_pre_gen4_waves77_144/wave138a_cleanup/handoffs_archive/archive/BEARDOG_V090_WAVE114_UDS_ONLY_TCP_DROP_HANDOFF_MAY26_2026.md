<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# BearDog v0.9.0 — Wave 114: UDS-Only Mode (TCP Drop Prep)

**Date**: May 26, 2026
**Audit**: Wave 53 — Primal Mountain Teams Handoff
**Scope**: TCP drop prep for exp114 (Tower CNS convergence prototype)

---

## Deliverables

### TCP Transport Now Opt-In

`MultiTransportServer::bind_all_available` no longer unconditionally binds
TCP on `127.0.0.1:9100`. TCP is started only when:
- `--port N` or `--listen addr:port` CLI flags are passed, OR
- `BEARDOG_TCP_IPC_PORT` env var is set

Without either, bearDog runs UDS-only. Logging shows
`"Tier 2 (TCP): skipped (UDS-only mode)"` when TCP is not configured.

### Method Parity Confirmed

All 127 JSON-RPC methods are available on both UDS and TCP via the same
`HandlerRegistry` and `MethodGate`. Zero capability loss in UDS-only mode.

Health probes (`health.liveness`, `health.readiness`, `health.check`) work
on UDS via cleartext NDJSON (first-byte `{` detection). `beardog doctor`
already checks UDS, not TCP.

### Socket Health Verified

Three-layer `unlink-before-bind` defense (`SocketConfig::prepare`,
`UnixSocketIpcServer::new`, `UnixSocket::bind`) prevents stale sockets.
SIGTERM/SIGINT handler explicitly calls `stop()` on all Unix servers for
deterministic socket file removal.

### Migration Path

| Scenario | Command |
|----------|---------|
| UDS-only (exp114/Tower CNS) | `beardog server` |
| Previous behavior (UDS + TCP) | `beardog server --port 9100` |
| Env-var controlled | `BEARDOG_TCP_IPC_PORT=9100 beardog server` |

### Other Items (status unchanged)

- **S4 auth shadow**: Running on cellMembrane, consuming passively
- **Vault Phase 2**: Planned enhancement, not blocking shift
- **SouthGate stability**: bearDog socket health is solid; crash investigation is songbird-side

## Quality Gates

- `cargo fmt --check`: PASS
- `cargo clippy --workspace -- -D warnings`: PASS (0 warnings)
- `cargo test --workspace`: PASS (14,940+ tests)
