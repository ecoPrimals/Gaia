# AAR — sporeGate Overwatch, Wave 115

**Date**: 2026-06-17 14:30 EDT
**From**: sporeGate overwatch (Cursor on NUC)
**Scope**: LAN topology, mesh overlay, K-Derm convergence, gate hardening
**Wave**: 115

---

## Executive Summary

sporeGate is fully operational as the sovereign plasma membrane. 13/13 primals alive, WireGuard 3-node mesh active, composition-deterministic nftables deployed, and the LAN cytoplasm is now machine-readable with zone topology. The primary blockers are SSH access to LAN gates and physical operator tasks (Eero bridge, [ISP] passthrough).

---

## WORKING — Verified Live

| System | Status | Evidence |
|--------|--------|----------|
| **13/13 primals** | ACTIVE, systemd persisted | `membrane-nucleus.target` active, all 13 `.service` units running |
| **nftables (plasma membrane)** | ACTIVE, composition-deterministic | `nft list ruleset` shows `table inet membrane` from `FirewallRuleset::for_composition()` |
| **WireGuard overlay** | 3-NODE MESH LIVE | `wg show wg0`: handshake 1m ago, 35ms to golgi, 31ms to pepti |
| **golgiBody (10.13.37.1)** | REACHABLE, hub relay | ping 35ms, IP forwarding enabled, hub for pepti relay |
| **peptidoglycan (10.13.37.4)** | REACHABLE via hub | ping 31ms (relayed through golgi) |
| **sporeGate overlay (10.13.37.2)** | LIVE | keepalive 25s, NAT punch-through via persistent keepalive |
| **systemd-networkd** | ACTIVE | WAN (enp1s0 DHCP), LAN (eno1 192.168.4.1/22), wg0 (10.13.37.2/24) |
| **DHCP server** | ACTIVE on eno1 | Pool 192.168.4.100-249, DNS=192.168.4.1 |
| **LAN backbone** | 15+ devices on ARP table | eastGate (.244), Omada (.115), Eeros, towers, NUCs all reachable |
| **eastGate (.244)** | REACHABLE (0.18ms) | L2 ping sub-ms, CRS310 sfp+2 at 10G |
| **Omada (.115)** | REACHABLE (0.43ms) | L2 ping sub-ms via 10G AOC trunk |
| **[ISP] gateway** | REACHABLE | curl confirms web UI at 192.168.1.254, firewall page accessible |
| **Git cascade** | CLEAN | wateringHole: both remotes synced, cellMembrane: origin synced (GitHub via push mirror) |
| **Cytoplasm zone model** | DEPLOYED | `TOPOLOGY_MAP.toml` v4.0.0: backbone, house2, eero_wifi zones defined |
| **Gate zone annotations** | DEPLOYED | 4 gates annotated with zone/hub_port/link_speed_mbps in manifest |
| **GateProfile zone fields** | IN cellMembrane HEAD | `zone`, `hub_port`, `link_speed_mbps` — serde-default, test passing |
| **Upstream spec** | WRITTEN | `CYTOPLASM_ZONES_SPEC.md` → cellMembrane team for typed model |

## NOT WORKING — Blockers & Failures

| System | Status | Blocker | Impact |
|--------|--------|---------|--------|
| **SSH to LAN gates (other than eastGate)** | REFUSED/TIMEOUT | `openssh-server` not running on northGate, etc. | Cannot deploy NUCLEUS or push relay config to remaining gates |
| **eastGate SSH** | **LIVE** (updated Jun 17 16:00) | `ssh eastgate@192.168.4.244` — Pop!_OS, kernel 6.17.9, up 1d+ |
| **Omada management UI** | UNREACHABLE (standalone mode) | SX3008F expects SDN controller — installing Omada Controller on sporeGate | Cannot audit L2 config until controller adopts switch |
| **Eero NAT** | ACTIVE (10.0.7.x) | Requires Eero app (operator phone access) | WiFi clients on separate NAT, invisible sub-membrane in cytoplasm |
| **[ISP] IP passthrough** | NOT CONFIGURED | Requires browser session at 192.168.1.254 with Device Access Code | Double-NAT still active ([ISP] 192.168.1.x → sporeGate 192.168.4.x) |
| **Sovereign relay push** | BLOCKED | Depends on SSH to gates | Cannot push RustDesk sovereign config to any LAN gate remotely |
| **northGate NUCLEUS** | PENDING | Depends on SSH or physical access | RustDesk reachable but NUCLEUS not yet deployed |
| **fieldGate** | OFFLINE | Dead CMOS, DDR3 NUC, hardware surgery | No software fix possible |
| **flockGate sovereign relay** | PENDING | WAN gate, needs SSH via golgi hop or physical visit | Still on public relay, not sovereign |

## PARTIALLY WORKING — Needs Attention

| System | Status | Detail |
|--------|--------|--------|
| **Omada L2 path** | WORKING (data plane) | Devices behind Omada are reachable on 192.168.4.x — L2 forwarding confirmed. Management plane inaccessible. |
| **WiFi (Eero)** | WORKING (with NAT) | Humans have WiFi. But it's behind 10.0.7.x NAT. Compute gates unaffected. |
| **cellMembrane binary** | STALE (v0.1.0, commit 9dc6a1d) | Local `membrane` binary is from older commit. `depot.integrity`, `firewall.generate` commands exist in code but not in deployed binary. |
| **RustDesk relay** | LIVE on golgi | hbbs/hbbr active on [RELAY_PUBLIC]. Config string works. But sovereign push to LAN gates blocked by SSH. |

---

## Sub-Work Shared with cellMembrane Team

### Already Merged (parallel IDE committed to HEAD)

| What | File | Detail |
|------|------|--------|
| `GateProfile` zone fields | `manifest.rs` | `zone: Option<String>`, `hub_port: Option<String>`, `link_speed_mbps: Option<u32>` — all `#[serde(default)]` |
| Zone deserialization test | `manifest.rs` tests | `gate_profile_zone_fields_parsed` — backbone, house2, and no-zone gates |
| K-Derm nftables generation | `firewall.rs` | `NftablesConfig`, `to_nftables_script()`, full `nft -f` idempotent output |
| nftables test suite | `tests/firewall.rs` | 10 tests for composition-deterministic firewall generation |
| Gate preflight scanner | `gate/preflight.rs` | Interface detection, WireGuard, DNS, DHCP, nftables validation |
| Async API layer | `manifest.rs`, `identity.rs`, etc. | `async` APIs for manifest load, identity check, freshness, depot integrity |

### Spec Handed Off (cellMembrane team to implement)

| Spec | File | Scope |
|------|------|-------|
| **CYTOPLASM_ZONES_SPEC.md** | `wateringHole/handoffs/` | `CytoplasmZone`, `SwitchHub`, `ZoneUplink`, `HubRole` types for `envelope.rs` |
| | | `topology.resolve zone|latency|path` dispatch commands |
| | | Zone-aware `gate.preflight` validation |
| | | Zone-scoped `gate.discover` |
| | | Integration with `EnvelopeTopology.cytoplasm_zones` HashMap |

### Deployment Team Needs from cellMembrane Team

| Need | Priority | Why |
|------|----------|-----|
| Fresh `membrane` binary harvest | P1 | Current binary is stale — `depot.integrity`, `firewall.generate`, `gate.preflight` all exist in code but not in deployed binary |
| `topology.resolve` command | P2 | Enables zone-aware routing decisions from the command line |
| `gate.discover` zone scoping | P3 | Scan only devices in gate's zone, not entire /22 |
| `plasmid.refresh` (replace deploy_membrane.sh) | P3 | Rust-native binary deployment to gates |

---

## Physical Operator Tasks (Unblocked, Needs Hands)

| Task | Steps | Risk | Time |
|------|-------|------|------|
| **Enable SSH on eastGate** | RustDesk session → `sudo apt install openssh-server` → add sporeGate pubkey | Low | 10 min |
| **Eero bridge mode** | Eero app → Settings → Advanced → DHCP & NAT → Bridge mode | Low, reversible | 5 min |
| **[ISP] IP passthrough** | Browser → 192.168.1.254 → Firewall → IP Passthrough → sporeGate MAC | Medium (brief outage) | 15 min |
| **Enable SSH on northGate** | RustDesk session → install openssh-server → add pubkey | Low | 10 min |

---

## Experiment Priorities (Moving Forward)

### Immediate (unblocked now)
1. **Harvest fresh membrane binary** — build on pepti (via SSH from sporeGate), deploy locally
2. **Test `gate.preflight`** — once binary is fresh, run against live sporeGate config
3. **Test `firewall.generate`** — compare live nftables to generated output

### After SSH Access (operator enables openssh-server)
4. **Sovereign relay push** — `sovereign-relay-push.sh discover` to all LAN gates
5. **NUCLEUS deploy to northGate** — full 13/13 primal stack
6. **Gate preflight validation** — run on eastGate, northGate to verify zone placement

### After Eero Bridge (operator switches app)
7. **Flat cytoplasm verification** — confirm WiFi clients get 192.168.4.x DHCP
8. **Update zone model** — change eero_wifi status from "collapsing" to "bridged"

### After [ISP] Passthrough (operator configures gateway)
9. **Eliminate double-NAT** — sporeGate gets public IP on enp1s0
10. **WireGuard direct connection** — peers can reach sporeGate without keepalive NAT punch

---

## Metrics

| Metric | Value |
|--------|-------|
| Primals alive | 13/13 |
| WireGuard mesh nodes | 3/3 (golgi, sporeGate, pepti) |
| VCS parity (wateringHole) | 2 remotes synced |
| VCS parity (cellMembrane) | Origin synced (GitHub via push mirror) |
| LAN devices on ARP | 15+ |
| Cytoplasm zones defined | 3 (backbone, house2, eero_wifi) |
| Gate profiles with zone data | 4/16 (physical LAN gates) |
| Tests passing (cellMembrane) | 495+ |
| nftables rules | Composition-deterministic, live |
| Upstream specs pending | 1 (CYTOPLASM_ZONES_SPEC.md) |
