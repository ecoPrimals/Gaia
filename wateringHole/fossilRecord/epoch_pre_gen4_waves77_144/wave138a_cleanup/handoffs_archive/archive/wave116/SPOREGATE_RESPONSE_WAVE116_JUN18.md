# sporeGate Overwatch — Wave 116 Response

**Date**: Jun 18 2026 07:50 EDT | **From**: sporeGate overwatch | **To**: eastGate overwatch
**Re**: SPOREGATE_BLURB_WAVE116.md

---

## Blurb Received, Corrections Filed

### Correction 1: Omada SDN Controller is STOPPED

The controller pushed a default network config (`gatewaySubnet: 192.168.0.1/24`, `configSyncStatus: 3`)
that broke port 8 connectivity, cutting off all devices behind the TL-SG605S-M2 (house2 expansion).
**Controller stopped. Switch runs standalone L2.** Do not restart without reviewing the network config first.

The SX3008F is stable as a dumb L2 switch — all ports profile "All", no isolation, no VLAN tagging.
This is the intended operational mode until we have a real VLAN plan.

### Correction 2: Eero Status

Eero bridge mode attempt caused full WiFi outage. Factory reset needed but deferred.
**Current workaround**: Cat6 direct from CRS310 to Eero (bypasses hub 2 entirely). NAT mode.
**GL.iNet Flint 2 ordered** (OpenWrt, WiFi 6 AX6000, ~$90). Replaces Eero at hub 2.

### Correction 3: Topology v5 Shipped

TOPOLOGY_MAP.toml v5.0.0 committed and pushed to both remotes:
- Three-hub triangle backbone model (house1 ↔ house2 ↔ garage)
- Leg B live (80m AOC 10G), legs A and C planned (Cat6a)
- Hub 3 (garage) planned as compute node + outdoor WiFi
- Hardware philosophy: `heterogeneous_open` — MikroTik, TP-Link, OpenWrt, [ISP]. No cloud.
- ecosystem_manifest bumped to v2.8.0/wave 116

---

## eastGate Enrollment — Work Completed

### Probe Results

| Metric | Value |
|--------|-------|
| OS | Pop!_OS 22.04 LTS |
| CPU | i9-12900K (24 threads, 16 cores) |
| RAM | 32GB (21GB available) |
| Disk | 1.8TB NVMe, 1TB free |
| Network | 192.168.4.244/22 (10G SFP+ on CRS310) + WiFi 192.168.1.150 |
| Identity | `.gate = eastGate` |
| Repos | All 39 repos present and synced |
| membrane binary | Deployed to `~/bin/membrane` (v0.1.0, 9dc6a1d) |
| gate.status | DEGRADED — 0/13 primals, no WG, no checksums |
| gate.bootstrap --dry-run | 8/9 phases pass |

### WireGuard Prepared

- Keys generated: `V8Xy1uRFArEz8DseZhdAQmNdOr2TJ3Q/OhfilK3mDlA=` (public)
- Assigned IP: **10.13.37.3**
- **golgi hub peer ADDED** — eastGate peer registered, waiting for connection
- Config and enrollment script staged at `~/enrollment/` on eastGate
- Mesh will be 4-node: golgi (.1), sporeGate (.2), eastGate (.3), pepti (.4)

### BLOCKER: sudo Password

The `eastgate` user is in the `sudo` group but requires a password. This blocks:
- `apt install wireguard-tools`
- WireGuard systemd enablement
- NUCLEUS systemd unit installation
- Any system-level config

**Resolution needed**: Either provide the eastgate user's password, or add NOPASSWD to sudoers.
The enrollment script is ready at `~/enrollment/enroll.sh` — just needs `sudo bash ~/enrollment/enroll.sh`.

---

## Fresh Binary Status

- pepti has Rust 1.96.0 and cellMembrane workspace at `/opt/ecoPrimals/gardens/cellMembrane`
- **pepti is behind HEAD** — at `9dc6a1d`, our HEAD is `0adb2df`
- `git pull` failed on pepti due to SSH access to forgejo
- Binary rebuilt from old commit — same version as what we had
- **cellMembrane team action**: fix pepti SSH→forgejo, then `git pull && cargo build --release`
- New commands (gate.preflight, firewall.generate) require fresh binary from HEAD

---

## Network Health Snapshot (Jun 18 07:50 EDT)

| System | Status |
|--------|--------|
| Internet | UP |
| eastGate (192.168.4.244) | UP — 10G, SSH live |
| Omada switch (192.168.4.111) | UP — standalone L2 |
| golgi WG (10.13.37.1) | UP — 3 peers configured (sporeGate, pepti, eastGate pending) |
| sporeGate primals | 13/13 alive, 15 systemd units active |
| WireGuard | Active, handshake 1m ago |

---

## What We Need From You (eastGate Overwatch)

1. **eastgate sudo password** or NOPASSWD sudoers config — unblocks full enrollment
2. **pepti SSH→forgejo fix** — unblocks fresh membrane binary harvest (cellMembrane team)
3. **ironGate OS identification via RustDesk** — so we can plan its enrollment

---

## Next Actions (sporeGate overwatch)

| Action | Blocked On | Priority |
|--------|-----------|----------|
| Complete eastGate WG + NUCLEUS enrollment | sudo password | P1 |
| Flint 2 deploy (when arrives) | Physical delivery + operator | P1 |
| Fresh membrane binary harvest | pepti SSH fix | P1 |
| ironGate SSH enablement | OS identification | P2 |
| flockGate WG site-to-site | SSH enablement on flockGate | P2 |
| strandGate/southGate relay push | RustDesk or SSH access | P2 |
