# HAIRPIN NAT — ROOT CAUSE DISCOVERY | Wave 244
**Timestamp**: 2026-11-15T03:39:11-05:00
**From**: swiftGate (.100) House 2
**Severity**: CRITICAL — explains RustDesk, AMOEBA, nestgate.io failures

---

## THE DISCOVERY

The AT&T BGW320 modem/router does **NOT support hairpin NAT**.

**Hairpin NAT** = when a LAN device tries to reach another LAN device
through the public IP (162.226.225.148). The BGW320 **drops it**.

## WHAT THIS EXPLAINS

| Symptom | Root Cause |
|---------|------------|
| RustDesk/AMOEBA fails | Tries to relay via public IP → hairpin dropped |
| nestgate.io:8443 TCP OPEN, HTTP TIMEOUT | Port forwards work inbound, but LAN→WAN→LAN = hairpin death |
| Flint 2 (.8.x) unreachable from .4.x | BGW320 won't route between its own subnets |
| IPv6 dual-stack confusion | BGW320 enables IPv6 by default, causes resolution ambiguity |
| Services binding to public IP invisible from LAN | Classic hairpin NAT failure |

## WHY NOBODY SAW THIS BEFORE

northGate and eastGate are **both on .4.x behind Flint 1** — same subnet.
They talk directly. No hairpin needed. No cross-subnet routing needed.

**swiftGate at House 2 is the FIRST gate to hit the .4↔.8 wall.**
The mobile gate found what the stationary gates couldn't.

## THE TOPOLOGY (CURRENT — BROKEN)

\\\
WAN (AT&T fiber)
     │
BGW320 (AT&T) ← PROBLEM: no hairpin, double NAT, IPv6 chaos
     │
Flint 1 (.1) ← our router, /22 subnet (.4.0-.7.255)
     │
CRS310 (.2) → 10G spine → Omada (.111) → Flint 2 (.8.x = ISOLATED!)
\\\

Flint 2 runs its own 192.168.8.x subnet. Devices on .4.x can't reach .8.x.
The ARP table shows Flint 2 MAC at 192.168.8.1 but Layer 3 routing is broken.

## THE FIX (PLANNED)

**Phase 1 — Immediate (software):**
- Add static route on swiftGate: \oute add 192.168.8.0/24 via WiFi\ (needs admin)
- Configure Flint 2 to bridge .8.x into .4.x (one flat subnet)
- Add GAIA SSID to Flint 2 (mirror Flint 1's WiFi config)

**Phase 2 — Cut the BGW320 (hardware):**
- New MikroTik router at WAN edge (ONT bypass, no BGW320)
- Hairpin NAT enabled, one flat subnet, no double NAT
- IPv6 under our control (disable or configure properly)
- BGP-capable for future multi-WAN

**Phase 3 — Circle of Willis for WAN:**
- Primary: AT&T fiber (raw ONT, no modem)
- Failover 1: Pixel hotspot (Mint Mobile, USB tether to MikroTik)
- Failover 2: Second phone hotspot
- MikroTik handles WAN failover — if fiber cuts, cellular carries blood

## EVIDENCE

\\\
swiftGate IP:      192.168.4.100
Subnet mask:       255.255.252.0 (/22, range .4.0-.7.255)
Gateway:           192.168.4.1 (Flint 1)
Public IP:         162.226.225.148 (= nestgate.io)
Flint 2 ARP:       94-83-c4-e0-62-b0 at 192.168.8.1 (OUTSIDE our /22!)
WiFi connected to: GL-MT6000-2ae-5G (Flint 2 default SSID)
Route to .8.x:     NONE (requires admin elevation to add)
\\\

---

**The mobile gate found the hairpin. That's what scouts do.**
lub-DUB.
