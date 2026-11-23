<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Network Segmentation Policy — Wave 114

**Date**: June 15, 2026
**Status**: Active Standard
**Owner**: cellMembrane/ironGate (enforcement)
**Authority**: eastGate overwatch
**Complements**: MEMBRANE_CHANNEL_ARCHITECTURE.md (channel definitions)

---

## Purpose

Codifies the routing and reachability rules for the ecoPrimals gate mesh.
Gates are classified into zones (internal, external, bridge, mobile) with
explicit routing policies. cellMembrane enforces these during mesh peering,
RustDesk relay configuration, and cascade operations.

---

## Zone Definitions

### Internal (LAN) Zone

Physical basement LAN connected by Cat6e ethernet. Covalent bond topology.
Gates in this zone communicate directly via UDS and LAN TCP. They are
NEVER exposed to the public internet.

**Gates**:
- eastGate (primary dev)
- ironGate (secondary dev)
- fieldGate (NUC canary)
- southGate (science/ABG)
- strandGate (genomics)
- northGate (compute)
- westGate (cold storage)

**Properties**:
- Transport: `lan`
- Mesh peering: Direct (LAN IP + port 7700)
- RustDesk: P2P direct when both peers are LAN-local
- Cascade: Pull from VPS depot over WAN HTTPS (outbound only)
- Inbound from WAN: BLOCKED (no port forwarding, no public IP)

### External (WAN) Zone

Gates outside the physical LAN perimeter. Reach internal gates exclusively
through the bridge (golgiBody relay). Never have direct LAN access.

**Gates**:
- flockGate (WAN shadow, sporePrint team)

**Properties**:
- Transport: `wan`
- Mesh peering: Via golgiBody relay ONLY ([RELAY_PUBLIC]:7700)
- RustDesk: Relay-only via golgiBody-ext (21116/21117)
- Cascade: Pull from VPS depot (same as LAN gates)
- Direct LAN access: NEVER (no VPN, no port forward)
- Federation: Through golgiBody songBird mesh relay

### Bridge Zone (VPS)

golgiBody VPS acts as the relay bridge between external and internal zones.
Runs relay services that forward traffic without interpreting it.

**Gates**:
- golgiBody (inner membrane — depot authority, Forgejo, NUCLEUS)
- golgiBody-ext (outer membrane — Caddy TLS, RustDesk relay, TURN)
- peptidoglycan (structural — builds, sync)

**Properties**:
- Transport: `local` (processes co-located on VPS)
- Runs: songBird mesh relay, RustDesk hbbs/hbbr, TURN relay, WAN depot
- Forwards: External → Internal traffic through songBird mesh peering
- Does NOT: Have LAN access (it's on DigitalOcean, not the basement)
- Reachability from LAN gates: Outbound SSH + HTTPS (port 7700, 443, 21115-21117)
- Reachability from WAN gates: Inbound TCP (same ports)

### Mobile Zone

Gates that transition between zones based on physical location.

**Gates**:
- grapheneGate (Pixel 8a — aarch64)

**Properties**:
- Transport: `adb` (when connected to LAN via USB/WiFi) or `wan` (when away)
- At home (LAN): Covalent bond, direct mesh peering
- Away (WAN): Routes through golgiBody relay (same as flockGate)
- RustDesk: P2P when LAN-local, relay when away

---

## Routing Rules

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ROUTING MATRIX                                │
├──────────────────┬──────────────────┬───────────────────────────────┤
│ Source           │ Destination      │ Path                          │
├──────────────────┼──────────────────┼───────────────────────────────┤
│ LAN gate         │ LAN gate         │ DIRECT (LAN TCP/UDS)          │
│ LAN gate         │ golgiBody VPS    │ DIRECT (WAN HTTPS/SSH out)    │
│ LAN gate         │ flockGate        │ VIA golgiBody relay           │
│ flockGate        │ LAN gate         │ VIA golgiBody relay           │
│ flockGate        │ golgiBody VPS    │ DIRECT (WAN TCP)              │
│ grapheneGate@LAN │ LAN gate         │ DIRECT (LAN TCP)              │
│ grapheneGate@WAN │ LAN gate         │ VIA golgiBody relay           │
│ Any gate         │ GitHub/Forgejo   │ DIRECT (HTTPS/SSH out)        │
│ Internet         │ LAN gate         │ BLOCKED                       │
│ Internet         │ golgiBody        │ Allowed (ports 22,80,443,     │
│                  │                  │   7700, 21115-21117, 3478)    │
└──────────────────┴──────────────────┴───────────────────────────────┘
```

---

## RustDesk Segmentation

| Scenario | Connection Type | Relay Used |
|----------|----------------|------------|
| LAN gate → LAN gate | P2P direct | No relay needed |
| WAN gate → LAN gate | Relay | golgiBody-ext hbbr (:21117) |
| LAN gate → WAN gate | Relay | golgiBody-ext hbbr (:21117) |
| grapheneGate@home → LAN gate | P2P direct | No relay needed |
| grapheneGate@away → LAN gate | Relay | golgiBody-ext hbbr (:21117) |
| External user (ABG) → workload gate | Relay | golgiBody-ext hbbr (:21117) |

**Key distribution**: RustDesk relay public key is distributed during
`gate.bootstrap` (phase 4 — credential distribution). Gates use the relay
server's public key to encrypt connections.

---

## songBird Mesh Segmentation

| Gate Type | mesh_peer | Federation Path |
|-----------|-----------|-----------------|
| LAN gate | [RELAY_PUBLIC]:7700 (golgiBody) | LAN gate → golgiBody → other peers |
| WAN gate (flockGate) | [RELAY_PUBLIC]:7700 (golgiBody) | flockGate → golgiBody → LAN peers |
| VPS (golgiBody) | 127.0.0.1:7700 (self) | Hub for all external peering |

golgiBody songBird instance is the mesh hub. All cross-zone communication
flows through it. LAN gates peer to it over WAN HTTPS (outbound from LAN).
External gates peer to it over inbound TCP.

LAN gates do NOT expose port 7700 to the public internet. Their mesh peering
with golgiBody is an outbound connection initiated from the LAN side.

---

## Enforcement Points (cellMembrane)

1. **gate.bootstrap**: Sets `transport` field in gate identity — determines routing class
2. **temporal.cascade**: Pulls from depot (outbound WAN HTTPS) — never accepts inbound pushes
3. **mesh.init**: Connects to `mesh_peer` (golgiBody) — outbound TCP from LAN gates
4. **health.sweep**: Probes local sockets only (UDS) — never crosses network boundary
5. **RustDesk config**: Sets relay server during bootstrap — P2P or relay based on transport class

---

## What This Policy Prevents

- **No direct WAN exposure for LAN gates**: No SSH/port-forward from internet to LAN hardware
- **No LAN routing for WAN gates**: flockGate cannot discover or reach LAN IPs
- **No relay bypass**: External gates must use golgiBody relay, cannot connect directly to LAN
- **No unauthorized inbound**: Only golgiBody accepts inbound connections from the internet
- **Single bridge point**: All external↔internal traffic flows through golgiBody (auditable)

---

## projectNUCLEUS Compute Access Path

External ABG members reach workload gates via:

```
ABG member → RustDesk relay (golgiBody-ext) → NUC intake (fieldGate) → Cat6e → workload gate
```

Or via SSH tunnel:

```
ABG member → SSH to golgiBody → ProxyJump to fieldGate → tunnel to workload gate port
```

fieldGate serves as the intake node: expendable NUC that absorbs external traffic
and proxies to internal high-value workload gates (northGate, strandGate).

---

## References

- [MEMBRANE_CHANNEL_ARCHITECTURE.md](../MEMBRANE_CHANNEL_ARCHITECTURE.md) — Channel 2b (RustDesk) details
- [DEPLOYMENT_INSTANCE.toml](../DEPLOYMENT_INSTANCE.toml) — Gate fleet topology
- [ecosystem_manifest.toml](../ecosystem_manifest.toml) — Gate profiles and transport fields
- [TUNNEL_ACCESS_GUIDE.md](../compute-sharing/TUNNEL_ACCESS_GUIDE.md) — SSH tunnel patterns
- [SOVEREIGNTY_STANDARDS.md](../SOVEREIGNTY_STANDARDS.md) — Dark Forest principle
