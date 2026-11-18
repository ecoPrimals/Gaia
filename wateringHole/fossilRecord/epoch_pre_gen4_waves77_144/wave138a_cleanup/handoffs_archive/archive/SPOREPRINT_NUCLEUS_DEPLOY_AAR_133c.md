# sporePrint NUCLEUS Deploy AAR — Wave 133c

**Date**: 2026-07-07 10:00 EDT | **Gate**: sporeGate | **Target**: golgiBody VPS
**Posture**: SOVEREIGNTY TRACK — sporePrint serving via petalTongue on golgi

---

## Objective

Deploy sporePrint NUCLEUS (petalTongue, nestGate, songBird, bearDog) to golgi VPS
using cellMembrane 4dcc4dd `gateway.sporeprint.*` tooling. Establish sovereign
content serving at `primals.eco` through the golgi relay layer.

---

## What Worked

1. **cellMembrane tooling pipeline**: `gateway.sporeprint.check` validated
   readiness (8/9 pass — only missing Zola build). Clean pre-deploy signal.

2. **Binary deployment**: All 4 NUCLEUS binaries deployed from pepti depot to
   `/opt/membrane/` on golgi. Busy-binary replacement via rename pattern worked
   cleanly for running songBird/bearDog processes.

3. **Zola auto-build**: Installed zola 0.19.2 on golgi, cloned sporePrint from
   Forgejo bare repo, built 212 pages + 14 sections in 13.7s. Set
   `MEMBRANE_ZOLA_AUTO_BUILD=1` in cascade-sense for automatic rebuild on pull.

4. **petalTongue `web --docroot`**: Correctly serves Zola static output as
   catch-all behind API routes. 3MB memory footprint — ideal for VPS.

5. **Caddy symlink bridge**: `/opt/ecoPrimals/sporePrint` → `infra/sporePrint`
   resolved the path discrepancy between Caddy's existing config and the new
   clone location without touching the Caddyfile.

6. **E2E verified**: `curl https://primals.eco/` → 200, title:
   "sporePrint — ecoPrimals: Sovereign Scientific Computing"

7. **Disk impact**: Negligible — 71% used (2.7G free), same as pre-deploy.

8. **Cascade freshness**: sporeGate published+committed+pushed heads (beaa6ca0),
   15/17 repos synced.

---

## Divergences for Upstream

### UNIT-DIV-01 (P2) — `gateway.sporeprint.units` CLI mismatch

Generated unit files use CLI arguments that don't match actual binary interfaces:

| Generated | Actual |
|-----------|--------|
| `petaltongue server --bind 127.0.0.1:8080 --content-dir <path>` | `petaltongue web --bind 127.0.0.1:8090 --docroot <path>/public` |
| `nestgate server --socket /run/membrane/nestgate.sock` | `nestgate server --socket-only --socket /run/membrane/nestgate.sock` |

Additionally, nestGate requires `NESTGATE_JWT_SECRET` env var — startup blocked
with `SECURITY VALIDATION FAILED` without it. The unit generator should either:
- Introspect the binary `--help` output, or
- Reference a versioned CLI contract per primal, or
- Generate with `NESTGATE_JWT_SECRET=$(openssl rand -base64 48)` placeholder

**Fixed manually**: Rewrote both units with correct CLI invocations.

### UNIT-DIV-02 (P2) — Port 8080 conflict

Generated units assume `:8080` is available. On golgi, `songbird-membrane.service`
already binds `:8080` (drawbridge). petalTongue moved to `:8090`.

**Convergence**: Unit generator should query the manifest gate profile for
allocated ports, or accept a `--base-port` offset. Tower Atomic should
eventually eliminate this — songBird routes everything, no static port
assignments needed.

### UNIT-DIV-03 (P3) — songbird-gateway vs songbird-membrane conflict

The generated `songbird-gateway.service` binds the same `:7700` port as the
existing `songbird-membrane.service`. These are the same primal with different
unit names and slightly different ExecStart args. Cannot run both.

**Convergence**: Need a migration path — either:
- `songbird-gateway.service` replaces `songbird-membrane.service` (stop old, start new)
- Or a `membrane gateway.migrate` command that handles the cutover atomically

### UNIT-DIV-04 (P1 blocked) — bearDog ACME CryptoProvider

`beardog-sporeprint.service` installed but not started. Blocked on flockGate P1:
`rustls CryptoProvider not installed` panic when using `rustls-rustcrypto` for
ACME. Until this is resolved, TLS terminates at Caddy (which works fine).

**Current path**: Caddy handles TLS for `primals.eco` → serves Zola `public/`
directly. bearDog will replace Caddy's TLS role once CryptoProvider is fixed.

### PORT-SURFACE-01 (P2) — golgi exposes too many ports

Current golgi UFW allows 14+ distinct port ranges. Tower Atomic goal is to
reduce external surface to:

| Port | Service | Role |
|------|---------|------|
| 443 | Caddy → bearDog (future) | TLS ingress — drawbridge |
| 80 | Caddy | ACME challenges + redirect |
| 7700 | songBird | Mesh federation — gatehouse |
| 22 | SSH | Management (restrict to WireGuard in time) |

Ports to retire as Tower Atomic matures:

| Port | Current Use | Retirement Path |
|------|-------------|-----------------|
| 2222 | Forgejo SSH | Route through songBird capability.call |
| 3478 | TURN relay | songBird absorbs relay function |
| 8080 | songBird drawbridge (legacy) | Merge into :7700 or :443 |
| 8091 | songBird (unknown) | Investigate and consolidate |
| 21115-21119 | RustDesk hbbs/hbbr | Route through songBird or WireGuard |
| 9443, 9444, 3001 | membrane bridges (VPC-only) | Drop when bridges retire |
| 49152-65535/udp | TURN data | songBird absorbs |
| 51820/udp | WireGuard | Keep — backhaul mesh |

Target: **4 external ports** (443, 80, 7700, 22) + WireGuard (51820).

---

## Architecture: Sovereign Relay as Living Dashboard

### Current State (Wave 133c)

```
                    ┌─────────────────────────────────────┐
                    │         CLOUDFLARE (boundary)        │
                    │   primals.eco → [RELAY_PUBLIC]        │
                    └──────────────┬──────────────────────┘
                                   │ :443
                    ┌──────────────▼──────────────────────┐
                    │         golgi (VPS relay)            │
                    │                                     │
                    │  Caddy (:443)                       │
                    │    ├─ primals.eco → Zola public/    │
                    │    ├─ membrane.primals.eco → depot  │
                    │    ├─ lab.primals.eco → sporeGate   │
                    │    └─ git.primals.eco → Forgejo     │
                    │                                     │
                    │  petalTongue (:8090) ← Zola docroot │
                    │  nestGate (UDS) ← CAS storage       │
                    │  songBird (:7700) ← mesh federation │
                    │  bearDog [installed, not active]     │
                    │                                     │
                    │  Forgejo (:3000) ← sovereign git    │
                    │  cascade-sense ← auto-sync+Zola     │
                    └──────────────┬──────────────────────┘
                                   │ songBird mesh
                    ┌──────────────▼──────────────────────┐
                    │       sporeGate (sovereign CI)       │
                    │                                     │
                    │  Full git repos (17 cloned)          │
                    │  Pepti depot (30 ecobins)            │
                    │  Forgejo mirror (39 repos)           │
                    │  songBird mesh peer                  │
                    │  Cross-compile workhorse             │
                    └──────────────┬──────────────────────┘
                                   │ LAN mesh
                    ┌──────────────▼──────────────────────┐
                    │       LAN gates (ironGate, etc)      │
                    │  songBird peers, compute workloads   │
                    └─────────────────────────────────────┘
```

### Evolution Target: Tower Atomic

The goal is for songBird to absorb all routing — Caddy retires, bearDog handles
ACME, petalTongue serves content, and the only external ports are the
drawbridge (443) and gatehouse (7700). New gates start external, enmesh through
golgiBody's gatehouse, and become internal songBird peers.

```
  External request → Cloudflare → golgi:443 (bearDog ACME)
    → songBird routes by capability
      → petalTongue (content)
      → nestGate (storage)
      → sporeGate (compute, via mesh)
      → ironGate (JupyterHub, via mesh)
```

Zola remains the static site generator but is treated as an external sovereign
tool — the primals don't depend on it, they produce content that Zola consumes.
Over time, primals.eco becomes a living dashboard: sporePrint renders the
science, petalTongue serves it, songBird routes workload interactions, and the
LAN mesh provides the compute substrate.

golgi as the golgi body: packages content for external delivery, filters
internal vs external traffic, and serves as the enmeshment point for new gates.
sporeGate as the nucleus: synthesizes the binaries, hosts the authoritative
repos, and drives the CI pipeline.

---

## Remaining Items (this gate)

| ID | Priority | Item | Status |
|----|----------|------|--------|
| UNIT-DIV-01 | P2 | Unit generator CLI mismatch | Flag for cellMembrane |
| UNIT-DIV-02 | P2 | Port conflict handling | Flag for cellMembrane |
| UNIT-DIV-03 | P3 | songbird service migration path | Flag for cellMembrane |
| UNIT-DIV-04 | P1 | bearDog CryptoProvider (blocked on flockGate) | Blocked |
| PORT-SURFACE-01 | P2 | Reduce golgi to 4+1 external ports | Tower Atomic track |
| SP-DIV-01 | P1 | DNS cutover primals.eco → golgi direct | Blocked on bearDog |
| STRAND-SSH-01 | P1 | strandGate SSH key deploy (.103) | Needs physical access |

---

*Wave 133c — sporePrint NUCLEUS deployed. petalTongue + nestGate active on golgi.
primals.eco serving 212 pages. 4 divergences flagged. Tower Atomic port
consolidation is the convergence path.*
