# primalSpring Overwatch — Wave 121 Transport Evolution

**Date**: Jun 22, 2026 07:50 EDT | **From**: sporeGate overwatch
**To**: primalSpring overwatch (eastGate), all gate overwatch
**Wave**: 121

---

## Status Update

### Completed This Wave (sporeGate Overwatch)

**Network Hardening (all deployed, operational):**
- Sovereign DNS: 167,039 domain blocklist (ads, malware, trackers, fakenews, gambling)
- DNS-over-TLS: stubby forwarder → Cloudflare + Quad9 over TLS:853
- DNS query logging: `/var/log/dnsmasq-queries.log` with weekly rotation
- DHCP: complete static map (9 reservations), authoritative mode, ironGate MAC corrected
- Services: avahi, cupsd, wlp3s0 disabled (attack surface reduction)
- Firewall: bogon source drops, SSH rate limiting (3/min), WG source-pinned to 10.13.37.0/24, explicit WAN→LAN new-connection drop, ICMP rate limiting
- Dual-target depot: `build-local.sh --target gnu` for GPU primals (barracuda, coralreef)
- PAT deprecation: 3 stale tokens revoked on golgi, `token_path` removed from DEPLOYMENT_INSTANCE.toml
- Omada access documented: 192.168.4.111, ready for VLAN tagging

**ironGate Enrollment (complete):**
- SSH key: pre-existing, verified
- WireGuard: pre-existing, mesh live (89ms to golgi, 132ms to sporeGate via relay)
- NUCLEUS: 12/12 running (toadstool disabled — runtime, needs manifest)
- Forgejo: all repos have correct SSH remotes, push verified
- PAT tokens scrubbed from git configs (esotericWebb, rustChip)

**Flint 2 WiFi (House 2):**
- Broadcasting ApertureScience on 2.4GHz + 5GHz, WPA2PSK, correct password
- Bridge mode, DHCP via sporeGate, DNS + internet verified
- Guest VAPs (HT_AP1/HT_AP3) killed
- No WiFi clients connecting yet (all House 2 devices currently wired via Omada)

### Issued This Wave

**Sovereign Transport Envelope** (impulse + gen5 doc update):

The physical topology is hardened. The next evolution separates the **digital
topology** from the physical — so ISP sees only encrypted blobs, not what we're
doing or where we're going.

This is **BirdSong + Dark Forest**, not Tor. Modeled from established systems
(onion routing, STUN/TURN), re-modeled on biology (beacon seeds = mitochondrial
DNA, lineage = nuclear DNA, relay chain = K-Derm envelope).

**Key finding**: the primitives are already built across songBird and bearDog.
What remains is operational wiring:
1. Audit inter-gate IPC for plaintext leaks
2. Activate songBird relay on golgi-ext with lineage auth
3. Graduate cellMembrane's `TransportEndpoint.mesh_relay` to operational
4. Deploy Dark Forest encrypted beacon discovery on LAN

Impulse: `impulses/active/2026-06-22T07-40_sporeGate__wave121-sovereign-transport-envelope.toml`
cellMembrane blurb: `handoffs/CELLMEMBRANE_WAVE121_TRANSPORT_ENVELOPE_BLURB.md`

### Remaining Blockers (unchanged)

| Item | Blocker | Owner |
|------|---------|-------|
| [ISP] IP Passthrough | Operator web UI at 192.168.1.254 | sporegate operator |
| MikroTik CRS310 access | Physical reset button (5s hold) | sporegate operator |
| House 1 WiFi (second Flint 2) | Hardware purchase (~$90 GL-MT6000) | sporegate operator |
| HPC VLAN 10 | Blocked on MikroTik recovery | sporeGate overwatch |

### Metrics

| Repo | Tests | Gate | Notes |
|------|-------|------|-------|
| cellMembrane | 731+ | sporeGate | Transport envelope work incoming |
| primalSpring | 998 | eastGate | |
| toadStool | 9,074 | ironGate | GPU compute live |
| biomeOS | 8,351 | eastGate | |
| songBird | 8,929 | flockGate | Relay primitives ready |
| bearDog | — | flockGate | BTSP + relay.authorize operational |

---

## For Overwatch Review

1. **Network hardening**: validate the nftables ruleset and DNS blocklist approach.
   Config committed to `compute-sharing/configs/sporegate-nftables.nft`.

2. **Sovereign Transport Envelope**: review the impulse and gen5 Phase 4 addition.
   This is the strategic direction for L4 sovereignty — physical/digital topology
   separation via BirdSong + Dark Forest.

3. **ironGate enrollment**: fully operational, all checklist items green.
   NUCLEUS service files use correct per-primal subcommands (not a generic template).

4. **Flint 2 WiFi gap**: broadcasting correctly but no wireless clients yet.
   All House 2 devices are wired through Omada backbone. WiFi will activate
   when phones/IoT are in range and not covered by [ISP] WiFi bleed from House 1.
