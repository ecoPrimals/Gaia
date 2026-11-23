# footPrint Wave 156d — petalTongue Bridge + Auto-Load

**Date**: Aug 5, 2026 | **Gate**: ironGate | **From**: eastGate overwatch

---

## Summary

Three remaining refinements from Phase 2 deployment are now complete:

1. **petalTongue WebSocket bridge** — `/ws` path on footPrint relays to petalTongue UDS (NDJSON framing, no riboCipher). Browser clients now have live access to petalTongue's visualization API.
2. **Auto-load default project** — First available project loads on client init. Map is no longer empty on first visit.
3. **CSP deduplication** — `SKIP_CSP=1` env var disables Express CSP headers when Caddy handles them upstream.

## Technical Details

### petalTongue Bridge (`src/petal-bridge.ts`)

- WebSocket server on `/ws` (noServer mode)
- Relays to `/run/membrane/petaltongue.sock` using NDJSON framing (newline-terminated JSON-RPC)
- petalTongue does NOT use riboCipher prefix — it uses plain newline-delimited JSON-RPC
- Socket access requires `biomeos` group ACL on the socket file

### WebSocket Architecture

Both WebSocket endpoints now use `noServer` mode with manual upgrade handling:

| Path | Target | Protocol |
|------|--------|----------|
| `/ws` | petalTongue UDS | NDJSON (newline-delimited JSON-RPC) |
| `/ws/bridge` | Agent bridge (internal) | JSON-RPC 2.0 over WebSocket |

### Validated Capabilities

petalTongue exposes through the bridge:
- `visualization.render` — single DataBinding → SVG/HTML/audio/description
- `visualization.render.dashboard` — multi-panel dashboard compilation
- `visualization.render.scene` — direct SceneGraph submission
- `visualization.export` — session export as SVG/HTML

11 data binding variants available (TimeSeries, Distribution, Scatter3D, Heatmap, etc.)

## Upstream Actions

| Team | Action |
|------|--------|
| **petalTongue** | Set `SocketGroup=biomeos` in service file so footPrint/squirrel can access UDS without manual ACL |
| **squirrel** | Register as a signal dispatch provider → footPrint agent panel `agentConnected` |
| **golgi/Caddy** | Verify WebSocket upgrade passthrough for `footprint.primals.eco/ws` |

## Metrics

- 708 tests, 53 files, all GREEN
- petalTongue `health.check` round-trip: <50ms through bridge
- Build time: 1.3s (Vite client + tsc server)

## Commit

`04e3162` — `feat: wire petalTongue WS bridge, auto-load project, CSP dedup`
