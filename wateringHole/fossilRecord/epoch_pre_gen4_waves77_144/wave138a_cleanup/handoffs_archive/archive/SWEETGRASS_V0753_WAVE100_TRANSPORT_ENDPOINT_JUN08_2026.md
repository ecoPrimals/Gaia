# sweetGrass v0.7.53 — Wave 100 Handoff

**Date**: 2026-06-08
**From**: strandGate (sweetGrass)
**Wave**: 100

---

## What Landed

### Transport Endpoint Injection

sweetGrass now accepts `TRANSPORT_ENDPOINT` — the canonical transport
injection pattern from sourDough. The type is wire-compatible with
`sourdough_core::TransportEndpoint` and `songbird_types::TransportEndpoint`.

#### New: `sweet_grass_core::transport::TransportEndpoint`

Wire format (same serde tagged JSON as sourdough/songbird):
```json
{ "transport": "uds", "path": "/run/membrane/sweetgrass.sock" }
{ "transport": "tcp", "host": "127.0.0.1", "port": 9100 }
{ "transport": "mesh_relay", "peer_id": "strand-gate", "capability": "provenance" }
```

Helpers: `uds()`, `tcp()`, `mesh_relay()`, `is_local()`, `transport_name()`,
`Display`, `parse_transport_endpoint()`.

#### New: `sweet_grass_service::transport_connect`

- `TransportStream` enum — implements `AsyncRead + AsyncWrite` over
  UDS or TCP transparently
- `connect_transport(&endpoint)` — the outbound IPC entry point

#### Binary Changes

```
--transport-endpoint <JSON>    (also TRANSPORT_ENDPOINT env var)
```

When set by the launcher or Tower Atomic:
- UDS endpoints override `--socket`
- Logged at startup: `transport = unix:///run/membrane/sweetgrass.sock`
- Existing `--socket` and `--port` continue working as Tier 5 fallback

#### Design: Wire Compatibility Without Dependency

Rather than adding `sourdough-core` as a cross-primal dependency
(sovereignty violation + pulls blake3), we defined the type locally with
identical `#[serde(tag = "transport")]` format. The wire format is the
contract — tested with sourdough JSON fixtures.

## Compliance Status

| Check | Status |
|-------|--------|
| `TRANSPORT_ENDPOINT` env var | Accepted |
| `connect_transport()` | Available |
| Self-binding removed | TCP opt-in, localhost-only defaults |
| `--port` as Tier 5 fallback | Preserved |
| `sourdough validate transport` | Ready for audit |

## Metrics

| Metric | Value |
|--------|-------|
| Version | v0.7.53 |
| Tests | 1,630+ (15 new) |
| Coverage | 91.7% |
| Clippy | Zero warnings (pedantic + nursery) |
| ring | ABSENT |
| New external deps | 0 |

## Status

sweetGrass transport evolution action item: **RESOLVED**.
Ready for `sourdough validate transport .` audit.
