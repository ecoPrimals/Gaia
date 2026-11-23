# AAR: nestgate.io Mesh-Hosted Peptidoglycan Surface

**Date**: Aug 4, 2026 | **Wave**: 156d | **From**: eastGate overwatch (sporeGate)
**Status**: LIVE — petalTongue v1.7.0 serving nestgate.io from sporeGate NUCLEUS via WG mesh

---

## What We Did

### Architecture Change: VPS → Mesh Hosting

Moved nestgate.io from a golgi redirect to a **mesh-hosted reverse proxy**:

```
BEFORE:  nestgate.io → 301 redirect → sporeprint.primals.eco/data/
AFTER:   nestgate.io → golgi Caddy (TLS) → WG mesh (10.13.37.1→10.13.37.2) → petalTongue :8190 on sporeGate
```

golgi remains the TLS termination point and external firebreak. All compute
moves to sporeGate's NUCLEUS over the WireGuard mesh. This makes nestgate.io
a true peptidoglycan layer interaction — the VPS is just a proxy, the LAN
gates do the work.

### Components Wired

| Component | What | Where |
|-----------|------|-------|
| **petalTongue v1.7.0** | Web server (`web --bind 10.13.37.2:8190 --ipc --backend content-provider`) | sporeGate NUCLEUS |
| **systemd user service** | `petaltongue-web.service` — enabled, persistent across reboots | sporeGate `~/.config/systemd/user/` |
| **Caddy reverse proxy** | `nestgate.io { reverse_proxy 10.13.37.2:8190 }` | golgi `/etc/membrane/Caddyfile` |
| **WireGuard mesh** | golgi `10.13.37.1` → sporeGate `10.13.37.2` (39ms RTT) | Both gates |

### Three-Domain Topology Now Operational

| Domain | Envelope | Hosting | Status |
|--------|----------|---------|--------|
| **primals.eco** | Outer membrane | golgi (Zola static via Caddy) | LIVE |
| **nestgate.io** | Peptidoglycan | sporeGate (petalTongue via mesh) | **LIVE** |
| **primal.eco** | Inner membrane | WG mesh only | FUTURE |

---

## What Worked

1. **petalTongue starts instantly** — 4ms to bound, web server + IPC dual-port mode
2. **Caddy mesh proxy** — golgi validates and reloads config in <1s, auto-TLS for nestgate.io
3. **WG mesh latency** — 39ms RTT golgi→sporeGate is fine for web serving
4. **systemd user service** — lingering enabled, service persists across sessions
5. **Dashboard content** — Physical topology, K-Derm layers, hardening controls, depot status,
   ecosystem coordination all render from manifest data

## What Diverges

### DIV-1: Content backend not wired

petalTongue's `content-provider` backend looks for `content-provider-e8b62b6e.sock` under
`/run/user/1000/biomeos/` — this socket doesn't exist on sporeGate because biomeOS isn't
running the Neural API content provider.

**Impact**: WireGuard Overlay card shows "Content backend unavailable" error. Gate mesh
visualization doesn't load. Static topology data renders fine.

**Fix**: Either start biomeOS Neural API on sporeGate, or use `--backend filesystem` with
a `--docroot` pointing to a data directory.

### DIV-2: Discovery service not found

petalTongue looks for `discovery-service-e8b62b6e.sock` in standard locations. Not running
on sporeGate.

**Impact**: "No primals discovered yet. Discovery runs automatically." in Discovered Primals
section. The dashboard works but can't show live primal discovery data.

**Fix**: Start biomeOS discovery service, or have petalTongue discover primals via the
existing NUCLEUS sockets in `/run/membrane/`.

### DIV-3: Port 8090 already in use

First attempt to bind port 8090 failed (AddrInUse). Switched to 8190.

**Fix**: Audit what's on 8090 (likely another service). Use 8190 as the canonical
nestgate.io petalTongue port.

### DIV-4: Title says "petalTongue Dashboard" not "nestgate.io"

The page title and header show "petalTongue Dashboard". For the peptidoglycan trust surface,
this should be branded as "nestgate.io" or "ecoPrimals Data Surface".

**Fix**: petalTongue web mode should accept a `--title` or `--brand` flag, or read from
environment/manifest. This is a petalTongue evolution item.

---

## Other Work This Session

### blueGate Sub-Builder UNBLOCKED

Root cause of hung SSH dispatch: blueGate had **no SSH key** for Forgejo git operations.

- Generated ed25519 key on blueGate
- Created `bluegate` user on Forgejo
- Registered key via API
- Added to ecoPrimals + sporeGarden orgs
- Verified clone works (exit code 0, Cargo.toml present)
- Deployed `membrane.exe` 77c1d32 (Phase 2a manifest-driven sub-builders)

### Membrane 77c1d32 Deployed

Phase 2a (manifest-driven sub-builder registry) deployed to:
- golgi: `/opt/membrane/membrane` — verified
- blueGate: `C:\Users\user\.local\bin\membrane.exe` — verified
- sporeGate: depot copy done, install pending (text file busy during harvest)

### Full Harvest Running

`plasmid.harvest --all --force --local` — 52 builds (13 primals × 4 targets).
In progress during this session.

---

## Next Steps

| ID | Action | Priority |
|----|--------|----------|
| MESH-01 | Wire biomeOS Neural API content provider on sporeGate | P1 |
| MESH-02 | Brand nestgate.io dashboard (title, header, favicon) | P2 |
| MESH-03 | Add `--docroot` for sporePrint data pages (CAS braids) | P1 |
| MESH-04 | Audit port 8090 usage on sporeGate | P3 |
| MESH-05 | Deploy petalTongue to ironGate for redundant serving | P3 |
| MESH-06 | Wire golgi Caddy health checks (upstream keepalive) | P2 |
