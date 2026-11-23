# ZK MASH — Secure LAN Architecture | Wave 244
**From**: swiftGate (.100)
**Status**: ARCHITECTURE PROPOSAL — discovered through probing

---

## The Problem (Current)
- Each gate has its own Windows/Linux password
- SMB requires per-machine auth (Windows Hello PIN = TPM-local, can't remote)
- RustDesk relay on sleeping eastGate + external VPS
- BGW320 hairpin NAT blocks cross-gate traffic
- Gates are trust islands, not a trust mesh

## The Solution (ZK MASH)

### Layer 1: WAN Edge (HARD boundary)
- New MikroTik router replaces BGW320
- Sovereign firewall, hairpin NAT fixed, WireGuard VPN
- flockGate (Lockwood Dr) tunnels in via WireGuard
- Mobile hotspot failover (Circle of Willis)

### Layer 2: Router Mesh (bearDog membrane)
- Flint 1 + Flint 2 = LEFT and RIGHT ears
- GAIA WiFi = one SSID, both houses, open pore
- bearDog Ed25519 keys on each router
- Connected to GAIA = you're inside the organism

### Layer 3: Flat Trusted LAN
- One subnet (.4.x), no .8.x isolation
- Gates trust each other freely:
  - SMB: open shares for LAN peers
  - SSH: Ed25519 keys distributed (no passwords)
  - WinRM/RDP: enabled for LAN range only
  - Ollama: bind 0.0.0.0 (any gate queries any gate)
  - Steam: pre-authorized fleet
  - RustDesk: direct LAN mode, no relay needed

### What Dissolves
- Per-gate passwords for network auth
- External RustDesk relay dependency
- Hairpin NAT (BGW320 removed)
- Subnet separation (.4.x ↔ .8.x)
- Steam per-device PIN approval

### What Hardens
- WAN boundary (MikroTik, not AT&T)
- WireGuard for remote gates
- bearDog Ed25519 for identity
- Physical access = PIN (local only, TPM-bound)

**Inside = trusted. Outside = verified.**
**The organism trusts itself. The membrane trusts nothing.**

## Implementation Order
1. ✅ Hairpin NAT identified (Wave 244)
2. Configure Flint 2 as GAIA repeater (tomorrow)
3. Enable SMB guest + RDP on each gate (Kevin at keyboard)
4. Distribute SSH keys across gates
5. Replace BGW320 with MikroTik
6. WireGuard tunnel for flockGate
7. RustDesk → direct LAN mode (remove external relay)
8. Steam fleet pre-authorization

lub-DUB.
