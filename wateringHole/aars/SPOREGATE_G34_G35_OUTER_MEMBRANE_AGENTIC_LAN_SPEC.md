# G34 + G35 — Outer Membrane Egress Masking + Fully Agentic LAN

**Date**: 2026-08-02
**Gate**: sporeGate (build authority)
**Status**: SPEC + PARTIAL IMPLEMENTATION
**Triggered by**: [ISP] gateway flagging outgoing VPN/encrypted traffic

---

## Problem Statement

### G34: Metadata Leak Through Untrusted Egress

The [ISP] gateway (`192.168.4.1`) is ISP-owned hardware that all fleet traffic passes through. Even with encrypted content, the [ISP] box observes:

- **Protocol fingerprinting**: WireGuard (UDP/51820), DNS-over-TLS (TCP/853), SSH (TCP/2222)
- **Destination mapping**: persistent connections to `[RELAY_PUBLIC]` (golgi VPS)
- **Timing analysis**: WG keepalive every 25s, CI build bursts, DNS query patterns
- **Volume correlation**: when builds run, data syncs, git operations happen

The [ISP] box started issuing warnings about outgoing traffic. The content is encrypted but the **pattern is the leak**. This is an outer membrane ownership gap — ISP hardware between the fleet and the internet is untrusted infrastructure.

### G35: Manual Credential Dependency

Accessing gates currently requires manual steps: reading credentials off hardware labels, copy-pasting passwords, enrolling SSH keys one at a time. The LAN should be fully agentic — sporeGate should reach any gate without human intervention.

---

## G34: Flint Egress Boundary

### Current Topology (leaky)

```
Internet ← [ISP] Box (192.168.4.1, ISP-owned)
               ↑ sees all traffic metadata
           flat LAN (192.168.4.0/22)
           ├── sporeGate (.3) → WG to golgi, DNS-over-TLS, SSH
           ├── ironGate (.237) → WG to golgi, RustDesk relay
           ├── strandGate (.169) → DNS queries
           ├── Flint (.111) → (idle, not in path)
           └── ... all gates independently route through [ISP]
```

### Target Topology (opaque)

```
Internet ← [ISP] Box (192.168.4.1, ISP-owned)
               ↑ sees ONE opaque UDP stream
           Flint (192.168.4.111, user-owned)
               ↑ WG tunnel aggregates all traffic
           flat LAN (192.168.4.0/22)
           ├── sporeGate (.3) → default route: Flint
           ├── ironGate (.237) → default route: Flint
           ├── strandGate (.169) → default route: Flint
           └── ... all gates route through Flint
```

### Implementation Steps

1. **[ISP] IP Passthrough**: Configure [ISP] box to pass public IP to Flint
2. **Flint WireGuard client**: Flint establishes tunnel to golgi (`[RELAY_PUBLIC]`)
3. **Flint as default gateway**: All fleet gates route through Flint (DHCP option or static)
4. **Full tunnel**: All internet traffic goes through WG tunnel to golgi
5. **golgi NAT**: golgi NATs fleet traffic to the internet

### [ISP] sees

Before: WireGuard, DNS-over-TLS, SSH, RustDesk relay, git operations — full protocol fingerprint
After: One opaque UDP stream at a steady rate — indistinguishable from a consumer VPN

### Trade-offs

- **Latency**: +40-80ms on all internet traffic (round-trip through golgi VPS)
- **Bandwidth**: limited by golgi's VPS link (1 Gbps typically)
- **Single point of failure**: golgi VPS down = no internet (mitigate: Flint falls back to direct if tunnel drops)
- **Split tunnel option**: only route fleet/ops traffic through tunnel, let consumer devices (phones, etc.) go direct

---

## G35: Fully Agentic LAN

### SSH Access Matrix (as of 2026-08-02)

| Gate | SSH User | SSH Host | Method | Status |
|------|----------|----------|--------|--------|
| sporeGate | — | localhost | — | SELF |
| ironGate | `irongate` | `10.13.37.7` / `192.168.4.237` | WG + LAN | **AGENTIC** |
| strandGate | `strandgate` | `192.168.4.169` | LAN | **AGENTIC** (enrolled via eastGate chain) |
| eastGate | `eastgate` | `192.168.4.244` | LAN | **AGENTIC** |
| blueGate | `user` | `192.168.4.210` | LAN | **AGENTIC** |
| golgiBody | `root` | `[RELAY_PUBLIC]` | VPS | **AGENTIC** |
| golgiBody-ext | `root` | `137.184.197.151` | VPS | **AGENTIC** (enrolled via golgi chain) |
| northGate | — | `192.168.4.147` | — | **BLOCKED** (Windows, all ports firewalled) |
| flockGate | `flockgate` | `10.13.37.6` | WG ProxyJump | **BLOCKED** (WG down, needs physical reboot) |
| southGate | — | — | — | **UNKNOWN** (not in SSH config) |

### Key: `sporegate-gate-v1`

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILU4i9hEtHJA02/JZ8XR/OHaR/bSiuAaDRMhdJX7zuRp sporegate-gate-v1
```

Enrolled on: ironGate, strandGate, eastGate, blueGate, golgiBody, golgiBody-ext (6/8 reachable gates)

### Remaining Enrollment

| Gate | Blocker | Resolution |
|------|---------|------------|
| northGate | Windows, SSH/OpenSSH not enabled, all ports firewalled | Physical access: enable OpenSSH, add key to `administrators_authorized_keys` |
| flockGate | WG tunnel dead 3+ days, no inbound ports | Physical access: `sudo systemctl enable --now wg-quick@wg0` + reboot |
| southGate | Not yet audited | Audit SSH access, enroll key |

### Future: `membrane remote.enroll`

Codify the enrollment process in `cellMembrane`:
```
membrane remote.enroll --gate strandGate --key sporegate-gate-v1
```

This command should:
1. Resolve gate's SSH host/user from `ecosystem_manifest.toml`
2. Copy the public key to `~/.ssh/authorized_keys` (Linux) or `administrators_authorized_keys` (Windows)
3. Verify access by running `hostname` over SSH
4. Update manifest with `ssh_agentic = true`

---

## Convergence Path

| ID | Goal | Description | Status |
|----|------|-------------|--------|
| G34 | Outer membrane egress masking | Flint as boundary, single opaque tunnel | SPEC |
| G34.1 | [ISP] IP Passthrough | Configure [ISP] box to hand off public IP to Flint | TODO |
| G34.2 | Flint WG tunnel | WireGuard client on Flint to golgi | TODO |
| G34.3 | Fleet routing | Change default gateway from [ISP] to Flint | TODO |
| G35 | Fully agentic LAN | SSH from sporeGate to all gates without manual credentials | 6/8 DONE |
| G35.1 | northGate enrollment | Enable OpenSSH on Windows, enroll key | BLOCKED (physical) |
| G35.2 | flockGate enrollment | Restart WG, enroll key | BLOCKED (physical) |
| G35.3 | `membrane remote.enroll` | CLI tool for automated enrollment | PROPOSED |
| G35.4 | `membrane remote.health` | Fleet-wide SSH + RustDesk health probe | PROPOSED |

---

*The inner membrane manages the outer membrane. The tower atomic trust chain bootstraps everything. The [ISP] box becomes invisible.*
