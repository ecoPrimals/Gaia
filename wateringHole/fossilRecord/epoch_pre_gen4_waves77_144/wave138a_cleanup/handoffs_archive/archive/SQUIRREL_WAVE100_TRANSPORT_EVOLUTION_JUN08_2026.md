# Squirrel Wave 100 — Transport Evolution + UDS Health Fix Confirmed

**Date**: June 8, 2026
**From**: squirrel (eastGate)
**Wave**: 100
**Priority**: MEDIUM (transport evolution target Wave 103)

## Transport Evolution — TRANSPORT_ENDPOINT Accepted

Squirrel now accepts launcher-injected transport via `TRANSPORT_ENDPOINT` env var
(sourDough `TransportEndpoint` format):

```bash
TRANSPORT_ENDPOINT='{"transport":"uds","path":"/run/membrane/squirrel.sock"}' \
  squirrel server
```

### Socket Resolution Priority (updated)

| Tier | Source | Precedence |
|------|--------|------------|
| 0 | `TRANSPORT_ENDPOINT` env (launcher/Tower injected) | Highest |
| 1 | `--socket` CLI argument | |
| 2 | Config file `server.socket` | |
| 3 | `SQUIRREL_SOCKET` / `BIOMEOS_SOCKET_PATH` env | |
| 4 | XDG runtime / /tmp fallback | Lowest |

### What remains for full Wave 103 compliance

- Outbound connections (`connect_transport()` for IPC to other primals) — currently
  uses raw `UnixStream::connect` / `TcpStream::connect` directly
- TCP listener self-binding already behind `--port` flag (Tier 5 debug only)
- No production `TcpListener::bind("0.0.0.0:PORT")` in squirrel (clean)

### Audit results

| Category | Count | Status |
|----------|-------|--------|
| Production TCP self-bind | 1 | Behind `--port` flag (correct) |
| Outbound TCP connect | 4 | AI provider adapters — target for `connect_transport` |
| Outbound UDS connect | ~15 | Correct for local IPC (lifecycle, discovery, adapters) |
| Test-only TCP | 4 | Acceptable — test infrastructure |

## UDS Health Probe Fix — Confirmed Working

The Wave 82c fix (commit `5172ef50`) is confirmed working. With `FAMILY_ID` set
(production BTSP mode), plain JSON-RPC probes over UDS now receive proper responses.

## Status

- `TRANSPORT_ENDPOINT` accepted: commit `f1c06822`
- Tests: 7,098 / 0 failed
- Clippy: 0 warnings
- Transport evolution: Phase 1 complete (accept). Phase 2 (outbound) pending.
