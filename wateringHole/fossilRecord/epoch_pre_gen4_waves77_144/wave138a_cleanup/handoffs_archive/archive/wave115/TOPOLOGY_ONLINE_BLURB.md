# Topology Online — eastGate + sporeGate Operational Blurb

**Status**: ACTIVE | **Date**: Jun 17 2026 07:50 EDT
**Teams**: eastGate (ops/overwatch) + sporeGate (LAN hardware)
**Goal**: Get all eco hardware fully online so we can leverage across gates

---

## Current Reality (validated Jun 17 07:50)

| Node | IP | Link | Status |
|------|-----|------|--------|
| **eastGate** | 192.168.4.244 | 10G SFP+ (sfp-sfpplus2) | ONLINE — 0.14ms to sporeGate |
| **sporeGate** | 192.168.4.1/3 | 2.5G (ether8) | ONLINE — router, 13/13 primals |
| **northGate** | ? | via MikroTik or Omada? | RustDesk reachable, LAN IP unclear |
| **fieldGate** | 192.168.4.36 (was) | DISCONNECTED | OFFLINE — DDR3 NUC, dead CMOS, open-air surgery. Indefinite. |
| **Omada router** | 192.168.4.115 / 10.0.4.1 | 10G trunk (sfp-sfpplus1) | ALIVE — NATs WiFi to 10.0.x.x |
| **Eero base** | 192.168.1.115 | 2.5G (ether2) | Bridge to [ISP] subnet |
| **Debian server** | 192.168.4.218 (expected) | via Omada trunk | NOT in ARP — offline or behind Omada NAT |
| **flockGate** | WAN (offsite) | Internet | RustDesk on public relay |

---

## Corrections to HPC Doc

- **"Galaxy server" at .244 is eastGate** — MAC `[MAC_SCRUBBED]` matches eastGate's `enp5s0`
- eastGate hostname is still `pop-os` (not renamed)
- eastGate has Galaxy bioinformatics running on :8080 (it's a service, not a separate machine)
- eastGate IS connected to CRS310 sfp-sfpplus2 at 10G

---

## Difficulties / Blockers

### 1. Omada Double-NAT (needs password — operator grabs AM)

Omada router at `.115` serves DHCP on `10.0.x.x` for all WiFi clients.
These devices can't reach the sovereign RustDesk relay without extra work.

**Options** (sporeGate decides after controller access):
- A) Switch Omada to bridge/AP mode → all clients get 192.168.4.x from sporeGate
- B) Keep Omada NAT + add routing on sporeGate for 10.0.x.x subnet

### 2. fieldGate Offline (needs physical ops)

Last known: 192.168.4.36 on CRS310 2.5G port. Not in ARP table.
Needs: check power, check cable, plug back in.

### 3. northGate LAN Identity (needs verification)

northGate is reachable via RustDesk sovereign relay but its LAN IP is unknown.
Could be one of: .149 (68:54:5a), .223 (48:5f:2d), .248 (b8:78:26).
Or it could be behind the Omada NAT on 10.0.x.x.

**Action**: SSH via RustDesk → `ip addr show` to confirm LAN IP and subnet.

### 4. flockGate (WAN) Relay Migration

Currently on public relay. Needs sovereign config applied.
Can't physically access (offsite). Must SSH from golgi or use current public RustDesk session.

### 5. eastGate Identity Cleanup

- Hostname: `pop-os` (should be `eastGate`)
- IP: .244 via DHCP (could set static .30 or accept .244)
- SSH config on sporeGate still targets `.30`

### 6. Debian Server (.218) Status Unknown

HPC doc says it should be on Omada trunk. Not in sporeGate ARP.
Either powered off or behind Omada NAT (10.0.x.x internally).

---

## Action Plan

### Operator (physical ops)

- [ ] Hand Omada controller password to sporeGate team (soon — not yet available)
- [x] fieldGate: DDR3 NUC with dead CMOS, cut open, open-air. Offline indefinitely.
- [ ] Optional: set eastGate hostname (`hostnamectl set-hostname eastGate`)

### sporeGate Team (LAN hardware) — OWNS ALL BELOW

- [ ] Log into Omada controller, assess mode (router vs bridge)
- [ ] Switch to bridge mode OR add routing for 10.0.x.x
- [ ] Identify northGate's LAN IP (RustDesk in → `ip addr`)
- [ ] SSH-push RustDesk config to all newly reachable devices
- [ ] Deploy fieldGate systemd units once back online
- [ ] flockGate WAN relay migration (SSH from golgi)
- [ ] WireGuard overlay activation (golgi hub, then site routers)

### eastGate Overwatch — VALIDATE ONLY

- [ ] Monitor cascade as topology evolves
- [ ] Validate ecosystem convergence (no divergence in remotes)
- [ ] primalSpring validation scenarios when new gates come online

---

## Success Criteria

All gates on same 192.168.4.x subnet, all reachable from sporeGate,
all running sovereign RustDesk relay, all primals alive. At that point
we can fully leverage compute across gates.

```
Target topology:

sporeGate (.1) ──2.5G──► CRS310 ──10G──► eastGate (.244) ← overwatch + compute
                                   ├──2.5G──► northGate (.??) ← gaming/remote
                                   ├──2.5G──► fieldGate (.36) ← canary NUC
                                   ├──10G───► Omada (bridge) → WiFi clients (.x)
                                   └──10G───► eastGate Galaxy (:8080)
```

All on 192.168.4.0/22. Single NAT boundary at sporeGate. Done.
