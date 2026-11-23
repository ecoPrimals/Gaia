# footPrint Server Deployment Handoff — Wave 139a

**Date**: Jul 14, 2026 | **Wave**: 139a | **From**: flockGate
**Track**: 3 — Live Compositions | **Resolves**: "footPrint server on sporeGate" TODO

---

## Summary

The footPrint client SPA is **LIVE** at `primals.eco/footprint/` with 10 GIS weak bond
proxies via golgi Caddy. The remaining TODO is deploying the Express server on sporeGate
to provide:

1. **Project persistence** — save/load/delete JSON project files (`/api/projects/*`)
2. **Agent bridge** — WebSocket + REST API for browser automation (`/ws`, `/api/agent/*`)
3. **Proxy fallback** — external data proxy when songBird drawbridge is unavailable (`/ext`)
4. **Health check** — `/api/health` endpoint for monitoring

All deployment artifacts are committed to `footPrint/deploy/`.

---

## What Ships

| Artifact | Location | Purpose |
|----------|----------|---------|
| `deploy/footprint.service` | systemd unit template | Run Express as `membrane` user |
| `deploy/caddy-footprint-api.snippet` | Caddy route config | golgi reverse proxy to sporeGate |
| `deploy/README.md` | Quick-start guide | Build, run, verify steps |

---

## sporeGate Deploy Steps

### 1. Clone or pull

```bash
cd /opt/ecoPrimals/protists/footPrint
git pull origin main
```

### 2. Build

```bash
npm ci
npm run build
# Produces dist/server.js + dist/client/
```

### 3. Install systemd unit

```bash
sudo cp deploy/footprint.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now footprint
```

Verify:

```bash
sudo journalctl -u footprint -f
# "FootPrint server running at http://localhost:3000"
```

### 4. Verify endpoints

```bash
curl -s http://localhost:3000/api/health
# {"status":"ok","version":"2.0.0","uptime":…}

curl -s http://localhost:3000/api/projects
# []

curl -s http://localhost:3000/api/agent/status
# {"connected":false,"entityCount":0,…}
```

---

## golgi Caddy Wiring

Import `deploy/caddy-footprint-api.snippet` into the `primals.eco {}` block.
Place it **before** the existing static `/footprint/*` handler.

The snippet routes these paths from golgi to sporeGate `:3000`:

| Path | Method | Purpose |
|------|--------|---------|
| `/api/projects*` | GET/POST/DELETE | Project persistence |
| `/api/agent*` | GET/POST | Agent REST API |
| `/api/health` | GET | Health check |
| `/ext` | GET/POST | External data proxy |
| `/ws` | WS | Agent WebSocket bridge |

Default target IP: `10.13.37.2:3000` (adjust if Express runs on a different gate).

After adding the snippet:

```bash
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
```

Verify end-to-end:

```bash
curl -s https://primals.eco/api/health
# {"status":"ok",…}
```

---

## API Surface Reference

### Project Persistence

| Method | Path | Body | Response |
|--------|------|------|----------|
| GET | `/api/projects` | — | `string[]` (project names) |
| GET | `/api/projects/:name` | — | `ProjectFile` JSON |
| POST | `/api/projects/:name` | `ProjectFile` JSON | `{saved: true}` |
| DELETE | `/api/projects/:name` | — | `{deleted: true}` |

Projects are stored as JSON files in `projects/` (auto-created, persisted).

### Agent Bridge

| Method | Path | Purpose |
|--------|------|---------|
| WS | `/ws` | Browser↔agent WebSocket (single client) |
| GET | `/api/agent/status` | Connection status + entity count |
| GET | `/api/agent/state` | Full shadow state (serialized entities) |
| POST | `/api/agent/command` | Forward command to browser (503 if no client) |
| GET | `/api/agent/messages?flush=true` | Poll user→agent messages |
| POST | `/api/agent/messages` | Send agent→user message |

### Proxy

| Method | Path | Query | Purpose |
|--------|------|-------|---------|
| GET | `/ext` | `url=<encoded>` | Proxy GET to allowlisted hosts |
| POST | `/ext` | `url=<encoded>` | Proxy POST to allowlisted hosts |
| DELETE | `/api/cache` | — | Clear proxy cache |

Allowlisted hosts defined in `src/constants.ts` (`ALLOWED_HOSTS`).

---

## Client Constants → Server Wiring

The footPrint SPA uses configurable paths from `src/constants.ts`:

```
PROXY_PATH    = '/ext'           → Express /ext (or songBird drawbridge)
PROJECTS_PATH = '/api/projects'  → Express /api/projects (or nestGate CAS)
WS_PATH       = '/ws'            → Express /ws (or agent bridge primal)
```

All client calls go through `src/client/api.ts` — a single abstraction layer.
No client code does raw `fetch()` to backend paths.

---

## Environment

| Variable | Default | Notes |
|----------|---------|-------|
| `PORT` | `3000` | Only env var the server reads |

No secrets, no database, no API keys. Server is stateless except for disk files in
`projects/` and `cache/`.

---

## Security Notes

- **No auth** on any endpoint. Caddy should restrict access if needed (basic auth, IP allowlist).
- **No CSP changes needed** — existing golgi CSP already allows `connect-src 'self'` and `wss:`.
- Body size limit: 10 MB JSON/text.
- Outbound: HTTPS only to allowlisted GIS hosts.

---

## Primal Absorption Path (Future)

This Express server is a temporary deployment. The endpoints will be absorbed:

| Endpoint | Absorbing Primal | Mechanism |
|----------|-----------------|-----------|
| `/ext` | songBird | Drawbridge weak bonds (already partially live) |
| `/api/projects/*` | nestGate | Content-addressed storage |
| `/ws` + `/api/agent/*` | Agent bridge primal | WebSocket + REST |
| Static SPA | petalTongue | Already served by Caddy on golgi |

The client API abstraction layer (`src/client/api.ts`) is designed for this —
change the constants and the client rewires automatically.

---

## Verification Checklist

- [ ] `node dist/server.js` starts without error on sporeGate
- [ ] `curl localhost:3000/api/health` returns `{"status":"ok"}`
- [ ] `curl localhost:3000/api/projects` returns `[]`
- [ ] Caddy snippet imported and validated
- [ ] `curl https://primals.eco/api/health` returns `{"status":"ok"}`
- [ ] Save a project from browser at `primals.eco/footprint/` — persists on reload
- [ ] GIS proxy still works (`/footprint/ext/` via Caddy + `/ext` via Express)

---

*Wave 139a. footPrint server deploy-ready. systemd + Caddy artifacts in `deploy/`.
Zero code changes needed on sporeGate — build, install, wire.*
