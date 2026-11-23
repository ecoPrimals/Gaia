# sporeGate Hardware Team — Wave 150x Final AAR

**Date**: Jul 24, 2026
**Gate**: sporeGate (10.13.37.2) / eastGate overwatch
**Scope**: Full Wave 150w–150x hardware, topology, and deployment ops
**Handoff to**: eastGate overwatch team

---

## Completed This Wave

### 1. tower.shadow Deployed to All 3 Gates

Deployed `membrane tower.shadow` with 60-min systemd timers:

| Gate | Binary | Status | Results/Cycle |
|------|--------|--------|---------------|
| sporeGate | `eee7e84` | ACTIVE (22h+) | 131 non-empty |
| flockGate | `eee7e84` | ACTIVE (17h+) | 137 non-empty |
| golgiBody | `eee7e84` | ACTIVE (fixed this session) | 7/14 per cycle |

**golgiBody fix**: songbird binary in XDG depot lacked `benchmark` subcommand — all 252
prior results were 0 bytes. Deployed updated songbird. Now producing data.

### 2. Crash-Loop Breaker Deployed

`membrane 0.1.0 (eee7e84)` deployed to all 3 gates. Includes `CrashLoopReport` with
scan-and-disable logic. Targets the Wave 150x crash-loop divergence (nestgate 17,920 +
biomeos-beacon 11,161 restarts on eastGate).

`biomeos-beacon.service` confirmed absent on sporeGate, flockGate, golgiBody — eastGate only.

### 3. songBird 0.2.1+sustained Rebuilt and Deployed

Rebuilt from source (`2bb2f92`) on sporeGate with `--sustained` streaming mode, UDS
connection pool, `federation.broadcast`. Deployed to sporeGate depot + golgiBody.

### 4. Sustained Benchmark — Tower vs WireGuard

| Path | Metric | Tower | WireGuard | Ratio |
|------|--------|-------|-----------|-------|
| **LAN** sporeGate→eastGate | Latency | **0.586ms** | 157ms (via VPS) | **267x** |
| **LAN** | Jitter | **0.008ms** | 1.61ms | **200x** |
| **LAN** | Burst | 4,073 Mbps | 6.8 Mbps | LAN vs WAN |
| **LAN** | Sustained | 6,140 Mbps | 3.4 Mbps | LAN vs WAN |
| **WAN** sporeGate→flockGate | Latency | 133.9ms | 134.0ms | Parity |
| **WAN** | Sustained | **7.1 Mbps** | 4.2 Mbps | **1.7x** |

The 267x LAN advantage is architectural: Tower's `lan_addr` bypasses the WG overlay.
WG has no LAN awareness — all traffic routes through golgiBody VPS (157ms round-trip).

### 5. primalSpring Overwatch

| Wave | Tests | Failed | Scenarios | Notes |
|------|-------|--------|-----------|-------|
| 150w | 1225 | 0 | 176 | 6 Tower exploration scenarios |
| 150x | 1240 | 0 | 210 | 14 stress/pen scenarios absorbed |

KNOWN_DEBT calibrated for sporeGate: `graphenegate-readiness=2`, `sporeprint-pure-primal-parity=1`,
`composition-access-control=15`, plus 10 tower-stress/pen entries.

### 6. LAN Topology Map

| Device | LAN IP | MAC | RTT | songBird | Notes |
|--------|--------|-----|-----|----------|-------|
| sporeGate | 192.168.4.3 | eno1 | — | Yes | Build authority |
| eastGate | **192.168.4.244** | [MAC_SCRUBBED] | 0.12ms | Yes | Confirmed |
| northGate | 192.168.4.208 | [MAC_SCRUBBED] | unreachable | No | Windows firewall |
| unknown | 192.168.4.237 | [MAC_SCRUBBED] | 0.10ms | No | Same Intel OUI as eastGate |
| MikroTik | 192.168.4.1 | [MAC_SCRUBBED] | — | — | Gateway |

**MANIFEST CORRECTION**: eastGate LAN IP is `192.168.4.244`, NOT `192.168.4.5`.

---

## Remaining Issues — Handoff to eastGate Overwatch

### BLOCKED: iperf3 Sustained Throughput

**Why blocked**: No SSH access from sporeGate to eastGate. iperf3 requires a server on
eastGate and a client on sporeGate (or reverse).

**To unblock** (eastGate team):
```bash
# On eastGate — start iperf3 server:
iperf3 -s -p 5201

# Then signal sporeGate team. We will run:
# LAN path:
iperf3 -c 192.168.4.244 -p 5201 -t 60 --json > iperf3_lan_upload.json
iperf3 -c 192.168.4.244 -p 5201 -t 60 -R --json > iperf3_lan_download.json
# WG overlay path:
iperf3 -c 10.13.37.5 -p 5201 -t 60 --json > iperf3_wg_upload.json
iperf3 -c 10.13.37.5 -p 5201 -t 60 -R --json > iperf3_wg_download.json
```

**OR** (eastGate team runs it all locally):
```bash
# eastGate as client → sporeGate server (we'll start iperf3 -s on request):
iperf3 -c 192.168.4.3 -p 5201 -t 60 --json > iperf3_lan_to_sporeGate.json
iperf3 -c 10.13.37.2 -p 5201 -t 60 --json > iperf3_wg_to_sporeGate.json
```

Target: >900 Mbps on 1G LAN. Measure WG overhead delta.

### BLOCKED: SSH Access sporeGate → eastGate

No SSH config entry, no key auth. Limits our ability to operate on eastGate remotely.

**To fix** (eastGate team):
1. Add sporeGate's public key to eastGate's `~/.ssh/authorized_keys`
2. Provide the correct username and hostname/IP for SSH config

### PHYSICAL: Gate Enrollment (southGate, strandGate)

USB seeds staged. Requires physical cabling to MikroTik and boot. R45 topology.

For each gate:
1. Cable to MikroTik (document hub_port)
2. Boot, verify link (`ip link`)
3. `membrane gate.enroll --gate <name>` from sporeGate
4. Verify WG handshake + mesh ping
5. southGate = 10.13.37.9 (allocated). strandGate needs WG IP allocation.

### PHYSICAL: 10G Backbone Cabling

4 towers NIC'd. Cabling is the sole blocker for sustained ≥1Gbps throughput testing.

### Manifest Corrections Needed

1. **eastGate `lan_ip`**: Change from `192.168.4.5` to `192.168.4.244` in `ecosystem_manifest.toml`
2. **192.168.4.237**: Identify this device (same Intel OUI as eastGate — second NIC or another tower?)
3. **northGate**: Confirm LAN IP `192.168.4.208` and whether Windows firewall should allow ICMP/songBird

### biomeos-beacon Disable

eastGate-only phantom unit (11,161 crash-loop restarts). Crash-loop breaker now handles it
but the unit should be fully removed:
```bash
sudo systemctl disable --now biomeos-beacon.service
sudo rm /etc/systemd/system/biomeos-beacon.service
sudo systemctl daemon-reload
```

---

## Deployment Summary

| Binary | Version | Gates Deployed | Method |
|--------|---------|----------------|--------|
| membrane | 0.1.0 (eee7e84) | sporeGate, flockGate, golgiBody | SCP + rename trick |
| songbird | 0.2.1+sustained | sporeGate, golgiBody | cargo build + SCP |
| petalTongue | 1.7.0 | sporeGate, flockGate | (Wave 150u) |

---

*Wave 150x complete from sporeGate hardware team. Tower EXCEEDS WG (267x LAN, 1.7x WAN).
Shadow active on 3 gates collecting continuous data. 1240/0 primalSpring. Remaining work
is physical (cabling, enrollment) or requires eastGate access (iperf3, SSH setup, biomeos-beacon).
Handing off to eastGate overwatch for continuation.*
