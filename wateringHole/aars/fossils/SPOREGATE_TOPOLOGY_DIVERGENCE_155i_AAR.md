# sporeGate AAR — Topology Divergence Review (Wave 155i NUCLEUS)

**Date**: Jul 29, 2026 | **Gate**: sporeGate | **Wave**: 155i-nucleus
**Scope**: DNS/DHCP/mesh topology audit, cellMembrane gap analysis, agnostic/fractal/isomorphic evolution path

---

## Trigger

northGate internet lag — traced to DHCP handing out the router (`192.168.4.1`)
as DNS instead of sporeGate's cached dnsmasq (`192.168.4.3` with stubby DoT,
Cloudflare + Quad9, 1000-entry cache, 101K-entry sovereign blocklist).

**Root cause was not the network — it was DNS.** This is the second time.
The fix was a one-line config change, but the *real* issue is deeper: the entire
DNS/DHCP/mesh topology stack is **manually maintained and drifting from the manifest.**

---

## Divergences Found

### 1. DHCP DNS Option (FIXED)

```
# Was:
dhcp-option=option:dns-server,192.168.4.1   ← router (slow, no cache, no blocklist)
# Now:
dhcp-option=option:dns-server,192.168.4.3   ← sporeGate dnsmasq (fast DoT, cached, sovereign)
```

**Impact**: Every LAN client (northGate, ironGate, tamison, phones) was resolving
DNS through the Omada router → AT&T upstream instead of sporeGate's sovereign stack.
Router DNS: 173ms cold / 75ms warm. sporeGate: 66ms cold / 38ms warm. **2-4x slower.**

### 2. sporegate.primals.local Mispointed (FIXED)

```
# Was:
address=/sporegate.primals.local/192.168.4.1   ← router IP
# Now:
address=/sporegate.primals.local/192.168.4.3   ← actual sporeGate IP
```

### 3. Manifest Role Mismatch

sporeGate's manifest roles: `["build_hub", "depot", "cascade_hub", "gateway", "http", "mesh_hub"]`

**Missing roles that sporeGate actually performs:**
| Role | Evidence | cellMembrane Type |
|------|----------|-------------------|
| NAT/firewall | nftables masquerade, FORWARD rules | `GateRole::NatFirewall` |
| DHCP server | dnsmasq dhcp-range 192.168.4.100-249 | `GateRole::Dhcp` |
| DNS primary | dnsmasq + stubby DoT, `.primals.local` authority | `GateRole::DnsPrimary` |
| DNS blocklist | 101,844-entry sovereign blocklist | (not typed) |
| WireGuard spoke | wg0 to golgiBody | (not `WgHub`, but spoke) |

### 4. northGate Not in DNS

northGate's DHCP hostname is `DESKTOP-9QG6LQL` — no `address=/northgate.primals.local/`
entry in dnsmasq. The manifest lists `ipv4 = "192.168.4.147"` but that IP was
assigned to `tamison` in the DHCP reservation. **northGate has no DHCP reservation
and no DNS name.**

### 5. Gate DNS Entries Manually Maintained

Current dnsmasq `address=` entries are hand-edited. They drift from the manifest's
`lan_ip` and `GateProfile` fields. No generator derives dnsmasq config from the
ecosystem manifest or topology map.

### 6. No Mesh DNS

WireGuard mesh peers (10.13.37.x) have no DNS names. `golgi.mesh.primals.local`
or `sporegate.wg.primals.local` don't exist. Gates must use raw IPs on the mesh.

### 7. golgiBody Uses DigitalOcean Default DNS

golgiBody's resolv.conf is DigitalOcean's default (`67.207.67.2/3`), not sovereign.
No dnsmasq, no stubby, no blocklist. The outer membrane has no DNS sovereignty.

### 8. Blocklist Not Version-Controlled

`/opt/sovereign-dns/blocklist.conf` (101,844 entries) lives only on sporeGate's
local disk. Not in the manifest, not in wateringHole, no update mechanism.

---

## cellMembrane Gap Analysis

### What Exists (types + generators)

| Layer | Type | Generator | Status |
|-------|------|-----------|--------|
| WireGuard config | `WgConfig`, `WgPeer` | `wireguard.generate` → `wg0.conf` | **Working** |
| Firewall rules | `FirewallRuleset`, `NftablesConfig` | `firewall.generate` → nftables/ufw | **Working** |
| Service units | `ServiceSpec`, `InitSystem` | `gate.configure` / `gate.apply` | **Working** |
| Interface detection | `DetectedInterface`, `InterfaceRole` | `gate.preflight` | **Working** |
| LAN DNS naming | `lan_dns_name()` | (helper only) | **Partial** |
| Topology model | `TopologyMap`, zones, segments, affinity | `topology.resolve` / `topology.summary` | **Working** |
| Gate roles | `GateRole::{DnsPrimary, Dhcp, NatFirewall, WgHub}` | (typed, not consumed) | **Typed only** |

### What's Missing (the gap)

| Layer | Need | Proposed Command |
|-------|------|------------------|
| dnsmasq config | Generate from manifest gate profiles + topology | `dns.configure` / `dns.apply` |
| stubby config | Generate DoT upstream from manifest | (part of `dns.configure`) |
| DHCP reservations | Derive from manifest `lan_ip` + MAC | (part of `dns.configure`) |
| DNS `address=` entries | Derive from manifest `lan_dns_name()` + `lan_ip` | (part of `dns.configure`) |
| Mesh DNS | Generate `address=` for WG mesh peers | (part of `dns.configure`) |
| Blocklist management | Source, version, update schedule | `sovereign.blocklist` |
| DNS health probe | Cache hit rate, upstream latency, blocklist freshness | `gate.status` addition |

---

## Evolution Path: Agnostic → Fractal → Isomorphic

### Level 1: Agnostic (decouple DNS from specific IPs)

**Goal**: DNS config is derived from the manifest, not hardcoded IPs.

```
membrane dns.configure
  → reads ecosystem_manifest.toml [gates.*] for lan_ip, wg_ip, roles
  → reads TOPOLOGY_MAP.toml for zones, segments, affinity
  → generates dnsmasq.conf:
      - address= entries from all gates with lan_ip
      - dhcp-host= entries from manifest MAC + lan_ip
      - dhcp-option=dns-server from gate with GateRole::DnsPrimary
      - server= from manifest dns.upstream config
  → generates stubby.yml:
      - upstream_recursive_servers from manifest
  → previews diff against current config

membrane dns.apply
  → writes configs
  → restarts dnsmasq + stubby via InitSystem dispatch
```

Any gate with `GateRole::DnsPrimary` can run this. Not hardcoded to sporeGate.

### Level 2: Fractal (same pattern at every scale)

**Goal**: DNS/DHCP stack replicates at each network boundary.

```
Scale 1 — LAN (sporeGate, today):
  dnsmasq → stubby → Cloudflare/Quad9
  serves: 192.168.4.0/22, .primals.local
  blocklist: sovereign-dns/blocklist.conf

Scale 2 — Mesh overlay (golgiBody, planned):
  dnsmasq → stubby → sovereign upstream
  serves: 10.13.37.0/24, .mesh.primals.local
  WG clients get DNS=10.13.37.1 (already in WgConfig)

Scale 3 — Subnet carve (marshGate, planned):
  dnsmasq → sporeGate → stubby
  serves: 192.168.5.0/24, .house2.primals.local
  hierarchical forwarding: marshGate → sporeGate → DoT

Scale 4 — Remote contract (future):
  dnsmasq → golgiBody WG → stubby
  serves: 192.168.7.0/24, .remote.primals.local
  NUC at friend's house gets full sovereign DNS stack

Scale 5 — Neighborhood mesh (planned):
  dnsmasq → sporeGate → DoT
  serves: 192.168.6.0/24, .neighborhood.primals.local
```

Each scale uses the same `dns.configure` → `dns.apply` pipeline, parameterized
by the gate's role and zone. The parent DNS server is derived from topology.

### Level 3: Isomorphic (structurally identical configs)

**Goal**: Every gate's DNS config is a parameterized instance of the same template.

```toml
# Proposed manifest addition: [dns] section
[dns]
domain = "primals.local"
mesh_domain = "mesh.primals.local"
blocklist_source = "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts"
blocklist_refresh = "weekly"

[dns.upstream]
mode = "dot"  # dns-over-tls via stubby
servers = [
    { ip = "1.1.1.1", tls_name = "cloudflare-dns.com" },
    { ip = "1.0.0.1", tls_name = "cloudflare-dns.com" },
    { ip = "9.9.9.9", tls_name = "dns.quad9.net" },
    { ip = "149.112.112.112", tls_name = "dns.quad9.net" },
]

[dns.hierarchy]
# Each gate's DNS parent. Root has no parent (uses upstream directly).
# Fractal: child zones forward to parent zones.
sporeGate = { parent = "upstream", zone = "primals.local" }
golgiBody = { parent = "upstream", zone = "mesh.primals.local" }
marshGate = { parent = "sporeGate", zone = "house2.primals.local" }
```

The same `dns.configure` code generates:
- **sporeGate**: full dnsmasq + stubby + blocklist + DHCP
- **golgiBody**: mesh-zone dnsmasq + stubby (no DHCP — static mesh IPs)
- **marshGate**: subnet-zone dnsmasq + forward-to-parent (no stubby)
- **contract NUC**: minimal dnsmasq + forward-to-golgiBody-WG

**Isomorphism**: the config shape is identical, only the parameters differ.
`dns.configure` doesn't need to know *which* gate — it reads the gate's role
and zone from the manifest and generates the correct config.

---

## Implementation Priorities

| # | Item | Priority | Owner | Complexity |
|---|------|----------|-------|------------|
| 1 | Add `dns_primary`, `dhcp`, `nat_firewall` to sporeGate manifest roles | P1 | sporeGate | Trivial |
| 2 | Add `[dns]` section to ecosystem manifest | P1 | sporeGate + eastGate | Small |
| 3 | Add northGate DHCP reservation + DNS entry | P1 | sporeGate | Trivial |
| 4 | Add mesh DNS entries (10.13.37.x → *.mesh.primals.local) | P2 | sporeGate | Small |
| 5 | `dns.configure` generator in cellMembrane | P2 | cellMembrane | Medium |
| 6 | `dns.apply` with InitSystem dispatch | P2 | cellMembrane | Medium |
| 7 | golgiBody sovereign DNS (dnsmasq + stubby) | P2 | sporeGate | Small |
| 8 | Blocklist version control + update mechanism | P3 | sporeGate | Small |
| 9 | DNS health probe in gate.status | P3 | cellMembrane | Small |
| 10 | Fractal hierarchy forwarding | P3 | cellMembrane | Medium |

---

## Immediate Fixes Applied

1. `dhcp-option=option:dns-server` → `192.168.4.3` (was `192.168.4.1`)
2. `address=/sporegate.primals.local/` → `192.168.4.3` (was `192.168.4.1`)
3. dnsmasq restarted, verified serving LAN + localhost

**northGate**: needs `ipconfig /renew` to pick up new DNS. Will auto-renew within 12h.

---

*sporeGate — topology divergence exposes the gap between cellMembrane's rich type
system (GateRole::DnsPrimary, ::Dhcp, ::NatFirewall all exist) and the manual
configs that actually run. The manifest knows the topology. The types know the roles.
The generators don't exist yet. Fix the generators, and DNS becomes agnostic
(any gate can serve), fractal (same pattern at every scale), and isomorphic
(same template, different parameters). This is a natural cellMembrane evolution,
not a new system.*
