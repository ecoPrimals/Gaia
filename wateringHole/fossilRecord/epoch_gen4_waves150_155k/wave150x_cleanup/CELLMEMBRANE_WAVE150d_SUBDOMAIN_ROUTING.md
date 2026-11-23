# cellMembrane Wave 150d — Subdomain Standard Routing Overhaul

**Date**: 2026-07-18 | **Wave**: 150d | **From**: eastGate overwatch (cellMembrane)
**Commit**: `06b7a3d`

---

## Summary

All composition routing evolved to the subdomain standard (`prefix.primals.eco`).
Path-based routing eliminated. Deployment chain now matches the operator-verified
architecture from the Wave 150d trace.

## URL Standard Adopted

All compositions MUST use `prefix.primals.eco` subdomains. Path-based routing
(`primals.eco/path/`) is prohibited. Root domain redirects to sporePrint.

| Domain | Service | Gate |
|--------|---------|------|
| `footprint.primals.eco` | footPrint | sporeGate:8090 |
| `webb.primals.eco` | esotericWebb | flockGate:8090 |
| `tideglass.primals.eco` | tideGlass | (future) |
| `sporeprint.primals.eco` | sporePrint | golgiBody |
| `primals.eco` | redirect → `sporeprint.primals.eco` | golgiBody |

## Changes

### Constants (`cellmembrane-types`)
- **Removed**: `ESOTERICWEBB_PATH` (`"/webb/"` — path-based, prohibited)
- **Added**: `WEBB_DOMAIN = "webb.primals.eco"`
- **Added**: `SPOREPRINT_DOMAIN = "sporeprint.primals.eco"`

### Caddy Generation (`caddy/mod.rs`)
- **footPrint**: Simplified from 3 sub-routes to 2. Catch-all now routes to
  footPrint:8090 (Express handles static + `/ext` proxy + `/api/*`). Only
  `/ws` sub-route remains for petalTongue:8080 (agent bridge).
- **footPrint CSP**: Added `Content-Security-Policy` header with `img-src`
  for `*.arcgisonline.com` and `*.tile.openstreetmap.org` (map tile domains).
- **esotericWebb**: Changed from `SURFACE_DOMAIN` + `/webb/*` sub-route to
  simple `WEBB_DOMAIN` vhost with `reverse_proxy flockGate:8090`.
- **Root redirect**: `primals.eco` now emits `redir https://sporeprint.primals.eco permanent`.

### Gateway Routes (`gateway/config.rs`)
- esotericWebb route: `SURFACE_DOMAIN` + `ESOTERICWEBB_PATH` → `WEBB_DOMAIN` + `/`

## Test Health

1,100 tests, 0 clippy, 0 fmt drift.

---

## Ops Actions Required

### golgiBody (Caddy — run `membrane caddy.generate` or manual)

After regenerating, the Caddyfile should contain:

```
footprint.primals.eco {
    ...
    reverse_proxy 10.13.37.2:8090
}

webb.primals.eco {
    reverse_proxy 10.13.37.6:8090
}

primals.eco {
    redir https://sporeprint.primals.eco permanent
}
```

### flockGate

```
sudo systemctl enable --now esotericwebb-server
```

### Cloudflare

No changes needed — `*.primals.eco` wildcard already resolves all subdomains
to golgiBody. New subdomains (webb, sporeprint) will work immediately once
Caddy vhosts are in place.

---

## Three-Domain Model (Reference)

| Domain | Layer | Purpose |
|--------|-------|---------|
| `primals.eco` | Intra-membrane | Shared ecosystem: compositions, depot, forge, docs |
| `primal.eco` | Inner membrane | Personal sovereign: mesh, ceremonies, private |
| `nestgate.io` | Data service point | CAS, federated APIs, weak bond data |
