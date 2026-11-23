# AAR — FP-DEPLOY + SKUNKY-DEPLOY (Wave 137a)

**Date**: Jul 11, 2026
**Gate**: sporeGate (primalSpring overwatch on eastGate)
**Operator**: agentic session

---

## 1. FP-DEPLOY — LIVE (HIGH)

### What

First live composition deployed: footPrint GIS home planner SPA is now
publicly accessible at `https://primals.eco/footprint/`.

### How

1. Cloned `protoKarya/footPrint` to `protists/footPrint` on sporeGate
2. Installed Node 22 via nvm (npm 10.9.8)
3. Built with `npx vite build --base /footprint/` (base path required for
   sub-path serving under `handle_path`)
4. Output: 5 files in `dist/client/` — ~233 kB gzipped (app 29 kB, turf 72 kB,
   leaflet 118 kB, CSS 13 kB, HTML 1.3 kB)
5. `rsync` to golgi at `/opt/ecoPrimals/compositions/footprint/dist/client/`
6. Added `handle_path /footprint/*` block to Caddy (before sporePrint catch-all)
7. Custom CSP allowing Leaflet tile sources (OSM, ArcGIS) and external data
   APIs (FEMA, USGS)

### Caddy Block

```caddy
handle_path /footprint/* {
    root * /opt/ecoPrimals/compositions/footprint/dist/client
    header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https://*.tile.openstreetmap.org https://*.arcgis.com; font-src 'self'; connect-src 'self' https://*.openstreetmap.org https://hazards.fema.gov https://epqs.nationalmap.gov https://*.arcgis.com; frame-ancestors 'none'"
    encode gzip
    try_files {path} /index.html
    file_server
}
```

### Validation

- `curl -sI https://primals.eco/footprint/` → HTTP/2 200
- All JS/CSS assets loading (200)
- SPA client-side routing via `try_files` fallback
- CSP header includes tile/data API origins

### Not Yet Wired

- **API proxy** (`/api/proxy/*` → songBird drawbridge): footPrint's Express
  backend used `?url=` query parameter; songBird uses path-based
  `/<service>/<path>`. Client constants need alignment before drawbridge
  can replace Express.
- **Project persistence** (`/api/projects/*`): requires nestGate CAS (Phase 2)
- **WebSocket** (`/ws`): requires petalTongue Axum WebSocket (Phase 2)

---

## 2. SKUNKY-DEPLOY — LIVE (DRY-RUN) (HIGH)

### What

skunky-ingest deployed to golgi, tailing Caddy JSON access logs and
aggregating per-IP behavioral observations. Running in `--dry-run` mode
(parses + aggregates, does not push to skunkBat TCP).

### How

1. Built `skunky-ingest` from skunkBat repo: `cargo build --release
   --target x86_64-unknown-linux-musl -p skunky-ingest`
2. Deployed to golgi: `scp` to `/opt/membrane/skunky-ingest`
3. Created state dir: `/var/lib/skunky-ingest/` (cursor position tracking)
4. Created systemd unit: `skunky-ingest.service` (enabled at boot)
5. Started in `--dry-run` mode for validation

### Configuration

| Param | Value |
|-------|-------|
| `--log-path` | `/var/log/caddy/access.log` (default) |
| `--skunkbat-addr` | `127.0.0.1:9750` (default) |
| `--window-secs` | `60` (default) |
| `--cursor-path` | `/var/lib/skunky-ingest/cursor.pos` (default) |
| `--dry-run` | `true` (validation phase) |

### Validation

Confirmed processing existing log backlog:
```
[dry-run] would send observation rate=0.5166 err_4xx=0.0 paths=1
[dry-run] would send observation rate=0.6166 err_4xx=0.0 paths=6
progress checkpoint lines=15000 failed=0 sent=0 offset=23373871
```

### To Go Live

Remove `--dry-run` from ExecStart once skunkBat's `baseline.observe`
TCP listener is running on golgi (or routed via WireGuard to sporeGate).

---

## 3. Provision Script Updated

`provision-golgi.sh` updated with:
- footPrint `handle_path /footprint/*` Caddy block + composition CSP
- `skunky-ingest.service` systemd unit
- `skunky-ingest` added to `systemctl enable` list

---

## Remaining Phase 1 Work

| ID | Status | Owner |
|----|--------|-------|
| FP-DEPLOY | **DONE** — static SPA live | sporeGate |
| SKUNKY-DEPLOY | **DONE** — dry-run active | sporeGate |
| SIGN-01-ACTIVATE | HANDOFF — 3 blockers documented | cellMembrane |
| FLOCKGATE-MESH | OPEN — port 7700 unreachable | mesh team |

*Wave 137a: First live composition deployed. Outer membrane now serves
both sovereign documentation (sporePrint) and interactive product
(footPrint). skunky-ingest operational in dry-run, ready for skunkBat
activation.*
