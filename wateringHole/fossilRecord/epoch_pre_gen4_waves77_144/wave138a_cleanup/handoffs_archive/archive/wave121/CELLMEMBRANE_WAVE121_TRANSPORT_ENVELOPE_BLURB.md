# cellMembrane Team — Sovereign Transport Envelope Blurb

**Date**: Jun 22, 2026 07:50 EDT | **From**: sporeGate overwatch
**To**: cellMembrane team, Tower team (songBird + bearDog)
**Wave**: 121 | **Priority**: P2 (design now, implement incrementally)

---

## Context

Network hardening is complete on the physical layer:
- 167k domain blocklist (ads/malware/trackers) via sovereign DNS
- DNS-over-TLS (stubby → Cloudflare/Quad9 DoT) — ISP blind to queries
- nftables: bogon drops, rate limiting, WG source-pinning
- DHCP: full static map, authoritative mode

**The physical topology is robust. The digital topology is next.**

## What We Need from cellMembrane

### TransportEndpoint.mesh_relay — Graduate to Operational

`cellmembrane-types/src/transport.rs` defines `TransportEndpoint::mesh_relay`
with `peer_id` + `capability` fields. It's typed, wire-compatible with
songBird/sourdough, has `is_relayed()` and `display_uri()` helpers.

**It's not wired.**

When a primal resolves a remote capability today, it gets a TCP socket on LAN.
The ask: when the transport layer resolves a `mesh_relay` endpoint, route
through songBird's relay infrastructure instead of direct TCP. This is the
abstraction boundary that decouples physical and digital topology.

### What This Enables

```
Today:   primal → TCP → LAN → peer primal
                 (plaintext on LAN, direct path visible)

Target:  primal → TransportEndpoint.mesh_relay → songBird relay
                 → BTSP-encrypted multi-hop → peer primal
                 (opaque on LAN, path through relay chain)
```

Primal code doesn't change. Only the resolution of `TransportEndpoint` changes.
This is exactly the membrane abstraction — the channel protein determines the
transport, not the primal.

### The Primitives Are Built

The Tower team has already implemented:

| Primitive | Location | Status |
|-----------|----------|--------|
| Sovereign .onion transport | `songbird-sovereign-onion/` | Feature-gated (`onion`) |
| Lineage-gated UDP relay | `songbird-lineage-relay/` | Operational on golgi |
| Beacon mesh pathfinding | `songbird-onion-relay/src/mesh/beacon.rs` | Implemented |
| Multi-tier NAT coordinator | `songbird-lineage-relay/src/multi_tier_coordinator/` | Implemented |
| BTSP encrypted framing | `beardog-tunnel/src/btsp_handshake/` | Operational (Wave 119) |
| Relay authorization | `beardog-tunnel/.../handlers/relay.rs` | `relay.authorize` |
| ntor + cell crypto | `beardog-tunnel/.../crypto_handlers_tor/` | Phase 2 ready |
| Dark Forest beacons | whitePaper spec + songBird beacon mesh | Spec complete |

**This is BirdSong + Dark Forest — not Tor.** Modeled from established systems
(onion routing, STUN/TURN), re-modeled on biology (beacon seeds = mitochondrial
DNA, lineage = nuclear DNA, relay chain = K-Derm envelope). All primitives are
pure Rust, sovereign, zero cloud dependency.

### Phased Implementation

1. **Audit** (sporeGate overwatch): Map which primal IPC uses UDS vs TCP vs HTTP.
   Verify all inter-gate WireGuard traffic is fully opaque.

2. **Relay activation** (Tower team): Enable songBird relay on golgiBody-ext
   with bearDog `relay.authorize` for lineage-gated access.

3. **Transport graduation** (cellMembrane): Wire `TransportEndpoint.mesh_relay`
   resolution through songBird mesh. Ad-hoc first, then abstract into membrane
   channel routing.

4. **Dark Forest deployment** (Tower + sporeGate): Encrypted beacon discovery
   on LAN. Gates discover each other via BirdSong beacons, not static DNS.

### Design Constraint

The primal-facing API must not change. A primal that calls `capability.call`
should not know or care whether the transport is UDS, TCP, or multi-hop
BTSP-encrypted relay. The resolution happens in the transport layer —
cellMembrane's job.

---

## Impulse Reference

Full technical proposal:
`impulses/active/2026-06-22T07-40_sporeGate__wave121-sovereign-transport-envelope.toml`

Architecture context:
- `gen5/TRANSPORT_EVOLUTION_NANOWIRE_TO_QUORUM.md` (Phase 4 added)
- `whitePaper/technical/DARK_FOREST_PROTOCOL.md`
- `whitePaper/technical/SOVEREIGN_NAT_TRAVERSAL.md`
- `whitePaper/technical/TOWER_ATOMIC_PURE_RUST_HTTPS.md`

---

*"The cell membrane doesn't care about the wire gauge of the axon.
It cares about which channel protein to open. The transport envelope
is the channel protein for sovereign routing."*
