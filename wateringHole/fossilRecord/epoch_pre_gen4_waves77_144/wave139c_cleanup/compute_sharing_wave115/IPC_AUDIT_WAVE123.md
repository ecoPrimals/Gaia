# Inter-Gate IPC Audit — Wave 123

**Date**: Jun 22, 2026 | **From**: sporeGate overwatch
**Purpose**: Transport Envelope Phase 1 — map all primal IPC for plaintext exposure

---

## sporeGate ([LAN_IP])

### UDS (secure — no network exposure)

All 13 primals have UDS sockets at `/run/membrane/<primal>.sock`:

| Primal | Socket | Status |
|--------|--------|--------|
| beardog | `/run/membrane/beardog.sock` + `beardog-default.sock` | SECURE |
| songbird | `/run/membrane/songbird.sock` + `/tmp/songbird*.sock` | SECURE |
| toadstool | `/run/membrane/toadstool.sock` | SECURE |
| barracuda | `/run/membrane/barracuda.sock` | SECURE |
| coralreef | `/run/membrane/coralreef.sock` + `coralreef-tarpc.sock` | SECURE |
| nestgate | `/tmp/nestgate-*.sock` | SECURE |
| rhizocrypt | `/run/membrane/rhizocrypt.sock` | SECURE |
| loamspine | `/run/membrane/loamspine.sock` | SECURE |
| sweetgrass | `/run/membrane/sweetgrass.sock` | SECURE |
| biomeos | `/run/membrane/biomeos.sock` | SECURE |
| squirrel | `/run/membrane/squirrel.sock` + `@squirrel` | SECURE |
| petaltongue | `/run/membrane/petaltongue.sock` | SECURE |
| skunkbat | `/run/membrane/skunkbat.sock` | SECURE |

### TCP localhost (secure — loopback only)

| Primal | Port | Bind | Status |
|--------|------|------|--------|
| toadstool | 35065 | 127.0.0.1 | SECURE |
| coralreef | 40531 | 127.0.0.1 | SECURE |
| sweetgrass | 37451, 41943 | 127.0.0.1 | SECURE |
| nestgate | 9500 | 127.0.0.1 | SECURE |

### TCP/UDP all-interfaces (EXPOSED on LAN)

| Service | Port | Protocol | Bind | Risk | Notes |
|---------|------|----------|------|------|-------|
| songbird | 8091 | TCP | 0.0.0.0 | LOW | Federation HTTP API — on trusted LAN |
| songbird | 7700 | TCP | * | LOW | Mesh/relay — on trusted LAN |
| songbird | 41582 | UDP | 0.0.0.0 | LOW | STUN/beacon — expected for mesh |
| toadstool | 5353 | UDP | 0.0.0.0 | MEDIUM | mDNS/discovery — 8 listeners, noisy |
| rustdesk | 34987 | TCP | [LAN_IP] | HIGH | On WAN-side IP, not LAN |
| rustdesk | 44801, 21119 | UDP | 0.0.0.0 | MEDIUM | Relay/NAT on all interfaces |
| wireguard | 51820 | UDP | 0.0.0.0 | OK | Expected — encrypted overlay |

### Findings

1. **UDS dominance**: all 13 primals use UDS for primary IPC. This is the correct
   architecture — no network exposure for primal-to-primal communication.

2. **songBird TCP on LAN**: ports 8091 (federation) and 7700 (mesh) are open on all
   interfaces. These are expected for mesh routing but could be tightened to bind
   only on eno1 (LAN) + wg0, not enp1s0 (WAN). Currently protected by nftables.

3. **toadstool mDNS**: 8 UDP listeners on 5353 (all interfaces). This is excessive
   and conflicts with stubby's DoT on the same port. Investigate and reduce.

4. **rustdesk on WAN IP**: bound to [LAN_IP] (enp1s0). This is the only service
   directly on the WAN-side NIC. Protected by [ISP] NAT but still undesirable.

5. **No plaintext HTTP on LAN**: no primals expose unencrypted HTTP APIs on the LAN.
   All inter-primal communication uses UDS (zero network). Cross-gate traffic goes
   through WireGuard (encrypted). **The LAN is already opaque for primal IPC.**

## ironGate ([LAN_IP])

### TCP listeners

| Service | Port | Bind | Status |
|---------|------|------|--------|
| nestgate | 8083 | 127.0.0.1 | SECURE |
| songbird | 8082 | 127.0.0.1 | SECURE |
| petaltongue | 3001 | 0.0.0.0 | LOW — web UI on LAN |
| unknown | 8080 | 0.0.0.0 | INVESTIGATE — barracuda? |
| unknown | 8091 | 0.0.0.0 | songbird federation |
| cloudflared | 20241, 20242 | 127.0.0.1 | SECURE — tunnel proxy |

### Findings

- ironGate also uses UDS as primary IPC (same NUCLEUS architecture)
- cloudflared tunnels present (likely legacy from pre-mesh era) — candidate for removal
- petaltongue web UI exposed on LAN (expected for dashboard use)

## Audit Summary

| Category | Count | Risk |
|----------|-------|------|
| UDS (local only) | 17+ sockets | NONE |
| TCP localhost | 6 ports | NONE |
| TCP LAN-exposed | 4 ports | LOW (nftables protected) |
| TCP WAN-exposed | 1 port (rustdesk) | MEDIUM |
| UDP all-interfaces | 10+ | LOW-MEDIUM |

**Verdict**: The primal IPC architecture is already sound — UDS for local,
WireGuard for cross-gate. No plaintext primal APIs exposed on the network.
The transport envelope work is about adding multi-hop opacity for cross-gate
capability.call, not fixing leaks.

## Recommended Actions

1. **toadstool port 5353 conflict**: resolve with stubby DoT (both want 5353)
2. **rustdesk WAN bind**: move to LAN-only or WG-only
3. **ironGate cloudflared**: review if still needed post-WG-mesh
4. **songBird 8091/7700**: consider binding to eno1 + wg0 only (not enp1s0)
