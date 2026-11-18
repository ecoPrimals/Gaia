# sporeGate primalSpring Ops AAR — Wave 150x (C)

**Date**: Jul 24, 2026 20:44 EDT | **Wave**: 150x | **From**: sporeGate (primalSpring team)
**Scope**: LAN discovery verification, benchmarks, sporePrint transplant, SSH setup, ops hardening

---

## What Happened

Cascaded from overwatch 20:01 EDT blurb. Executed sporeGate P1 topology tasks,
verified sporePrint transplant, ran fresh benchmarks, documented the songBird
LAN discovery routing gap, and hardened the mesh-init startup sequence.

### sporePrint Transplant (P2 #1) — DONE

eastGate shipped the full transplant (`b985c22`, 18 files) before we pushed.
Glacial correction in action — two teams executing the same guidance concurrently.
We contributed a delta fix: `toweratomic` entity registry entry still had old
description and page link. Fixed in `67cc325`.

### Fresh Benchmarks — Tower 353x LAN

50-probe benchmark, sporeGate → eastGate:

| Path | Latency (avg) | Jitter | Ratio |
|------|--------------|--------|-------|
| Tower LAN (192.168.4.244) | 0.448ms | 0.006ms | — |
| WG overlay (10.13.37.5) | 157.99ms | 0.634ms | — |
| **Advantage** | **353x** | **106x** | — |

WAN parity confirmed (sporeGate → flockGate):

| Stack | Latency (avg) | Jitter |
|-------|--------------|--------|
| Tower | 137.9ms | 1.275ms |
| WG | 136.3ms | 0.875ms |

### songBird LAN Discovery — Gap Documented

**What works**: `peer.connect` with `target_address: "192.168.4.244:7700"` creates
a LAN TCP connection. Returns `connection_id: "lan-tcp-192.168.4.244-1037"`,
`mesh_registered: true`. Direct benchmarks via LAN IP achieve 0.45ms.

**What doesn't work**: `mesh.find_path` and `mesh.peers` still resolve to
`wireguard://10.13.37.5:7700` (overlay). The mesh routing logic doesn't prefer
`EndpointType::Local` connections over overlay. This means `capability.call`
traffic routes through WG overlay (158ms) instead of LAN (0.45ms).

**Root cause**: songBird's path selection in the mesh module doesn't check for
active LAN connections. The overlay registration overwrites/takes precedence in
the peer endpoint table.

**Impact**: 353x latency difference for same-switch peers. Critical for
distributed compute dispatch scenarios.

**Workaround deployed**: `songbird-mesh-init.sh` now issues `peer.connect` for
LAN peers after `mesh.init`. Direct TCP benchmarks use the LAN path correctly.

**Fix needed**: songBird code change — `mesh.find_path` and `mesh.peers` should
prefer `EndpointType::Local` when available. Owned by flockGate/songBird team.

### SSH Access sporeGate → eastGate — Config Ready

SSH config entry added for `eastgate` (192.168.4.244, user sporegate, ed25519 key).
Key is offered but **rejected** — eastGate's `authorized_keys` doesn't have our
pubkey. Bilateral action required:

```
eastGate: echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILU4i9hEtHJA02/JZ8XR/OHaR/bSiuAaDRMhdJX7zuRp sporegate-gate-v1' >> ~/.ssh/authorized_keys
```

This unblocks: iperf3 sustained throughput, biomeos-beacon fix, remote ops.

### Manifest LAN IP — CONFIRMED

`ecosystem_manifest.toml` has `lan_ip = "192.168.4.244"` for eastGate and
`lan_ip = "192.168.4.3"` for sporeGate. Fix from previous wave persisted.

### Ops Hardening

- **Root `peers.toml` restored**: `/root/.local/share/songbird/peers.toml` was
  missing (deleted during service reconfiguration). Restored with `lan_addr` for
  eastGate.
- **`songbird-mesh-init.sh` updated**: Now issues `peer.connect` for eastGate LAN
  address after mesh initialization, ensuring LAN TCP path is established on
  every service restart.
- **Forgejo SSH outage**: golgiBody hit load avg 71.02 during cascade. TCP
  connections (including SSH/git) stalled for ~10 minutes. WG-UDP and ICMP
  unaffected. Recovered without intervention.

---

## By The Numbers

| Metric | Value |
|--------|-------|
| Shadow benchmark files | 525 (up from 213) |
| Tower LAN latency | 0.448ms avg, 0.006ms jitter |
| WG overlay latency | 157.99ms avg, 0.634ms jitter |
| LAN advantage | 353x latency, 106x jitter |
| Mesh peers | 3 (eastGate, golgiBody, flockGate) |
| Gateway uptime | 11h28m |
| Shadow timer | ACTIVE (60min interval) |

---

## Task Status

| # | Task | Status |
|---|------|--------|
| P1 #4 | songBird LAN peer discovery | **GAP DOCUMENTED** — peer.connect works, mesh routing doesn't prefer LAN |
| P1 #6 | SSH sporeGate→eastGate | **BLOCKED** — config ready, eastGate needs to add pubkey |
| P1 #7 | Manifest eastGate LAN IP | **DONE** — confirmed persisted |
| P2 #1 | sporePrint transplant | **DONE** — eastGate shipped full, we contributed entity fix |
| P1 #1 | iperf3 sustained | **BLOCKED** — needs SSH to eastGate |
| P1 #5 | biomeos-beacon fix | **BLOCKED** — needs SSH to eastGate |

---

## Blockers (eastGate bilateral)

1. **SSH key auth**: eastGate must add sporeGate pubkey to `~/.ssh/authorized_keys`
2. **iperf3 server**: eastGate must run `iperf3 -s` for sustained throughput testing
3. **biomeos-beacon**: eastGate must disable phantom unit (11,161 restarts)

## Code Gap (flockGate/songBird team)

**songBird mesh routing doesn't prefer LAN endpoints.** `peer.connect` registers
LAN TCP connections but `mesh.find_path` returns overlay. Fix: path selection
should check for active `EndpointType::Local` connections and prefer them over
overlay when both are available.

---

*Wave 150x sporeGate AAR (C): Tower 353x LAN advantage verified (0.45ms vs
158ms). LAN discovery routing gap documented for songBird team. sporePrint
transplant done (entity fix). SSH config ready, blocked on eastGate pubkey.
525 shadow files. Mesh-init hardened with LAN peer.connect. 3 tasks blocked
on eastGate bilateral access.*
