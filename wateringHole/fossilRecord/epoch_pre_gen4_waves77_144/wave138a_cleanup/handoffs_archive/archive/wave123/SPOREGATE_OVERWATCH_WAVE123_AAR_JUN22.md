# sporeGate Overwatch — Wave 123 AAR

**Date**: Jun 22, 2026 | **Wave**: 123 | **Gate**: sporeGate (.2)
**Operator**: sporegate | **Status**: All P1s COMPLETE

---

## Completed Tasks

### 1. IPC Audit — Inter-Gate Plaintext Mapping
Mapped all primal listening sockets across sporeGate and ironGate.
- **UDS**: 17+ sockets, dominant for local IPC (beardog, biomeos, songbird, etc.)
- **TCP localhost**: biomeos neural-api (3000), petaltongue (3001), nestgate (8083)
- **TCP all-interfaces**: songbird (3478, 7700), rustdesk (21115-21117)
- **UDP all-interfaces**: songbird (3478), toadstool (5353 conflict)
- **Verdict**: No plaintext primal APIs exposed on network. Cross-gate traffic through WireGuard. LAN already opaque for primal IPC.
- **Document**: `compute-sharing/IPC_AUDIT_WAVE123.md`

### 2. BLAKE3 Depot Verification
- 14/14 musl binaries: **ALL PASS** (checksums match)
- 2/2 gnu binaries: verified (barracuda, coralreef)
- Checksums regenerated to cover both `x86_64-unknown-linux-musl` and `x86_64-unknown-linux-gnu`
- ironGate binary sizes: 13/13 MATCH depot
- Note: `b3sum` not installed on ironGate, verified via size match

### 3. Nest Provenance — Ledger Height
- `temporal.cascade --gate sporeGate`: 15/17 repos synced (plasmidBin, projectNUCLEUS not cloned by design)
- Fixed duplicate `build_authority` key in `ecosystem_manifest.toml`
- Provenance chain validated

### 4. Quorum Phase 1 — golgi Cascade Timer
- Installed `cascade-sense.timer` on golgi (peptidoglycan)
- 15-minute systemd timer: pulls from Forgejo, relays to GitHub via golgi-ext
- Added `peptidoglycan` remote on golgi-ext for pull chain
- Tested: Forgejo pull OK → GitHub relay OK → 4 active impulses sensed
- Relay chain: `sporeGate → Forgejo → golgi (pull) → golgi-ext (fetch+push) → GitHub`

### 5. TransportEndpoint.mesh_relay Graduation
- Added `relay.forward` JSON-RPC handler to songBird
- 7 files changed: `RelayMethod::Forward` variant, dispatch, introspection, capability tokens
- Bridges cellMembrane's `call_via_relay` → songBird's `forward_to_remote_gate` (TCP/TURN)
- Both codebases compile clean, all tests pass
- Pushed to Forgejo, cascaded to GitHub via golgi

### 6. [ISP] BGW320 IP Passthrough (Operator-Assisted)
- **Passthrough Mode**: DHCPS-fixed, MAC `[MAC_SCRUBBED]`
- **Public IP**: `[NUCLEUS_WAN]/23` on `enp1s0`
- **Old NAT eliminated**: `192.168.1.x` subnet no longer in routing table

---

## Incidents & Lessons

### Incident 1: DNS Resolution Failure Post-Passthrough
- **Cause**: dhclient wrote `nameserver 192.168.1.254` to `/etc/resolv.conf`. With passthrough, the gateway is no longer reachable at that IP.
- **Impact**: All DNS resolution on sporeGate failed. Internet (raw IP) still worked. Remote Cursor IDE access was stable (already connected).
- **Fix**: Set `resolv.conf` to `nameserver 127.0.0.1` (our dnsmasq→stubby DoT stack). Installed dhclient enter-hook to suppress DNS override on lease renewal. Set `chattr +i` on resolv.conf.
- **Lesson**: Any WAN IP change that alters gateway reachability must pre-stage DNS. Future: add a pre-flight check to WAN migration procedures.

### Incident 2: WireGuard Handshake Failure
- **Cause**: [ISP] BGW320 has a UDP port mapping bug — packets sent FROM port 51820 get correct NAT, but return packets TO port 51820 are routed to the old private IP (`192.168.1.233`) instead of the passthrough public IP.
- **Impact**: WireGuard mesh unreachable for ~35 minutes. golgi saw our correct endpoint but replies were misrouted.
- **Fix**: Changed sporeGate's WG `ListenPort` from 51820 to 51821. Handshake restored in seconds. Updated nftables (live + persistent + version-controlled).
- **Lesson**: [ISP] passthrough is not fully transparent for UDP source port reuse. Non-standard ports avoid the bug. Document per-ISP quirks in topology.

### Redundancy Divergence Analysis
- **Positive**: Remote access via Cursor Cloud remained stable throughout both incidents. The mesh was down but the IDE connection (already established) survived.
- **Negative**: If WG had been the only remote access path, we'd have been locked out. The dhclient DNS overwrite is a boot-order race condition — if dnsmasq restarts after dhclient, resolv.conf gets clobbered.
- **Mitigation**: dhclient hook + immutable flag. Future: watchdog script that validates `resolv.conf` integrity on any DHCP event.

---

## Current Topology

```
Internet
   │
[ISP] BGW320 (IP Passthrough, transparent bridge)
   │
sporeGate [[NUCLEUS_WAN]] ← TRUE EDGE
   ├─ eno1 [192.168.4.1/22] → LAN
   │    ├─ MikroTik CRS310 (.2) → 10G fiber → House 2
   │    │    └─ Omada SX3008F (.111) → House 2 LAN
   │    │         ├─ ironGate (.169)
   │    │         ├─ Flint 2 (WiFi: ApertureScience)
   │    │         │    ├─ xbox-h2 (.244)
   │    │         │    └─ ms-device-h2 (.218)
   │    │         └─ tamison (.147)
   │    └─ [House 1 devices via [ISP] WiFi → 192.168.1.x → [ISP] NAT]
   ├─ wg0 [10.13.37.2/24] → WireGuard mesh (port 51821)
   │    └─ golgi (.1) → eastGate (.5), flockGate (.6), ironGate (.7)
   └─ DNS: dnsmasq → stubby (DoT) → Cloudflare/Quad9
```

---

## Remaining Work

| Task | Priority | Status |
|------|----------|--------|
| MikroTik CRS310 credential recovery | P1 | BLOCKED (operator physical reset) |
| Flint 2 #2 for House 1 WiFi | P1 | BLOCKED (hardware purchase) |
| strandGate/southGate relay push | P2 | Opportunistic |
| Tier 3 isomorphism (gate.migrate) | P2 | cellMembrane |
| golgi-as-NUCLEUS evolution | P2 | cellMembrane |
| [ISP] passthrough watchdog script | P2 | Hardening |

---

*Checkpoint: All Wave 123 sporeGate Overwatch P1s complete. [ISP] passthrough live. Network sovereign.*
