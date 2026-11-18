# Gatehouse / Darkforest — Sovereign Network Demarcation Standard

**Wave**: 132g (reviewed 155h) | **Authority**: eastGate overwatch

---

## Overview

The ecoPrimals network has two regimes separated by a single, controlled boundary.
All external traffic enters through the **Gatehouse** (known ports, TLS termination).
All internal routing happens in the **Darkforest** (no exposed ports, mesh-only).
The **Drawbridge** is the single crossing point between them.

---

## Darkforest (Internal)

The darkforest is invisible from outside. No port scanning, no direct access, no known entry points.

**Rules**:
- No primal binds to `0.0.0.0` (except bearDog in gatehouse mode)
- All inter-primal communication uses Unix domain sockets, abstract sockets, or songBird mesh
- Services bind to `127.0.0.1` at most — never externally reachable
- Discovery is via `mesh.peers` and `capability.call` — no IPs, no ports
- Adding a new service means registering a capability with songBird, not opening a port

**Transport hierarchy**:
1. Abstract sockets (Android/grapheneGate)
2. Unix domain sockets (Linux/macOS)
3. `127.0.0.1:port` TCP (localhost only, when UDS unavailable)
4. songBird mesh relay (cross-gate, LAN direct-connect or WAN via golgi)

**Key invariant**: a new gate joining the mesh exposes ZERO ports externally. It peers via songBird and becomes reachable to the mesh. Nothing else can see it.

---

## Gatehouse (External)

The gatehouse is the castle wall — the only surface exposed to the internet.

**Exactly two ports**:
- `:443` — TLS termination (bearDog ACME gateway, `HotReloadAcceptor`)
- `:80` — ACME HTTP-01 challenges + HTTP→HTTPS redirect (bearDog `Http01Solver`)

**Owner**: bearDog (single binary, single process, single responsibility for external surface)

**Activation**: `BEARDOG_GATEHOUSE_MODE=true` (or legacy `BEARDOG_TLS_MODE=acme`)

**Behavior**:
- `:443`: Accept TLS connection → terminate → forward cleartext HTTP to upstream (songBird)
- `:80`: If `/.well-known/acme-challenge/*` → serve ACME response. Otherwise → `301 Moved Permanently` to `https://`
- skunkBat `security.advisory` is consulted for threat intelligence on inbound traffic

**Only one gate runs gatehouse mode**: sporeGate (the public entry point). Other gates are purely darkforest.

---

## Drawbridge (songBird http.proxy)

The single crossing point between the external world and the internal mesh.

**Location**: `127.0.0.1:7700` on sporeGate (or UDS: `unix:/run/membrane/songbird.sock`)

**Flow**:
```
bearDog :443 (TLS terminated)
    → cleartext HTTP → songBird http.proxy (drawbridge)
        → CapabilityProxyRouter: Host/path → capability name
            → capability.call via mesh → backend in darkforest
```

**Routing model**:
- `SONGBIRD_PROXY_ROUTES` env var: `capability=http://backend:port`
- Example: `jupyter=http://192.168.4.237:8000` (ironGate LAN direct-connect)
- The backend address is internal (LAN or mesh) — never exposed externally

**Key invariant**: the drawbridge is the ONLY place that translates external HTTP semantics into internal mesh semantics. Everything before it is "internet". Everything after it is "darkforest".

**Capability advertisement** (Wave 133d):

Drawbridge routes must be discoverable by remote gates via `capability.call`. songBird
auto-registers each unique capability from `SONGBIRD_DRAWBRIDGE_ROUTES` into the local
IPC registry at startup and announces them to mesh peers via `mesh.capabilities_announce`.

```
SONGBIRD_DRAWBRIDGE_ROUTES=/hub=jupyter,/api=jupyter,/infer=inference
```
On startup, songBird:
1. Parses unique capabilities: `["jupyter", "inference"]`
2. Registers `drawbridge:jupyter`, `drawbridge:inference` in the local IPC registry
3. Announces `["jupyter", "inference"]` to all mesh peers
4. Remote gates can now `capability.call("jupyter")` → routed to this gate's drawbridge

Every gate with drawbridge routes automatically advertises its capabilities.
No manual `ipc.register` calls or sidecar scripts needed.

---

## Topology

```
INTERNET
    │
    ▼
┌─────────────────────────────────────────┐
│         GATEHOUSE (sporeGate)           │
│                                         │
│  bearDog :443  ←→  ACME/TLS/certs     │
│  bearDog :80   ←→  challenges/redirect │
│  skunkBat      ←→  security advisory   │
│                                         │
│  ─────── DRAWBRIDGE ───────            │
│  songBird :7700 (http.proxy)           │
│  CapabilityProxyRouter                  │
└──────────────┬──────────────────────────┘
               │ mesh / LAN / UDS
               ▼
┌─────────────────────────────────────────┐
│         DARKFOREST (all gates)          │
│                                         │
│  songBird mesh (UDS, abstract, LAN)    │
│  ironGate: JupyterHub localhost:8000   │
│  strandGate: STAR alignment (local)    │
│  flockGate: Tower dev (WAN via golgi)  │
│  eastGate: primalSpring, petalTongue   │
│  grapheneGate: mobile trust anchor     │
│                                         │
│  Nothing exposed. Nothing visible.      │
│  Capabilities, not ports.               │
└─────────────────────────────────────────┘
```

---

## Biological Mapping (K-Derm Alignment)

| Network Concept | K-Derm Layer | Biology |
|----------------|--------------|---------|
| Gatehouse | Outer membrane (extracellular face) | Exposed surface proteins, receptors |
| Darkforest | Cytoplasm | Protected internal machinery |
| Drawbridge | Transport channel / porin | Selective permeability |
| bearDog :443 | LPS layer | First contact, shields interior |
| songBird http.proxy | Channel protein | Specific molecules (capabilities) pass |
| skunkBat advisory | Immune receptor | Detects threats at the surface |

---

## Configuration Reference

### sporeGate (gatehouse gate)

```bash
# /etc/beardog/gatehouse.env
BEARDOG_GATEHOUSE_MODE=true
BEARDOG_ACME_DOMAINS=lab.primals.eco
BEARDOG_ACME_EMAIL=admin@primals.eco
BEARDOG_GATEWAY_UPSTREAM=127.0.0.1:7700
BEARDOG_HTTPS_PORT=443
BEARDOG_ACME_CHALLENGE_PORT=80

# songBird proxy routes (drawbridge configuration)
SONGBIRD_PROXY_ROUTES=jupyter=http://192.168.4.237:8000
```

### Any other gate (darkforest)

No gatehouse configuration needed. Just songBird mesh peering:
```bash
# songBird mesh.init with bootstrap peers
# No ports exposed. No external configuration.
```

---

## Anti-Patterns

- Opening a port on a non-gatehouse gate for external access
- Running Caddy, nginx, or any other reverse proxy alongside bearDog
- Binding a service to `0.0.0.0` instead of `127.0.0.1`
- Routing external traffic without going through the drawbridge
- Adding DNS records that point directly to darkforest gates

---

*The gatehouse is a known point. The darkforest is invisible. The drawbridge is selective. This is sovereignty.*
