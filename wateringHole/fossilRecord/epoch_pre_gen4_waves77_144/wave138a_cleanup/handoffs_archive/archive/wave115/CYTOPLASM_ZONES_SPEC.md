# Cytoplasm Zones — Specification Handoff for cellMembrane Team

**From**: sporeGate overwatch (deployment team)
**To**: cellMembrane team (code evolution)
**Date**: 2026-06-17 | **Wave**: 115
**Priority**: P2 — enables zone-aware routing, preflight, discovery

---

## Context

The physical LAN has a clear hub hierarchy that is currently invisible to cellMembrane:

```
[ISP] BGW320 (WAN boundary)
    |
sporeGate (plasma membrane: NAT/DHCP/DNS/nftables)
    |
CRS310 (hub 1: L2 backbone, 10G/2.5G) — zone "backbone"
    ├── sfp+2: eastGate (10G)
    ├── ether8: sporeGate eno1 (2.5G)
    ├── ether2: Eero 6 (WiFi bridge, collapsing)
    └── sfp+1: 80m AOC (10G) to...
         Omada SX3008F (hub 2: L2 extension) — zone "house2"
              ├── northGate, fieldGate, towers
              └── TL-SG605S-M2 (2.5G expansion)
```

The existing `EnvelopeTopology` models the VPS relay chain (gate -> golgi -> pepti -> golgi-ext) but treats the cytoplasm as a monolith. Gates need to know which hub they're on and what bandwidth/latency to expect.

### What We Already Did (sporeGate overwatch, surgical)

1. **`TOPOLOGY_MAP.toml`** — Added `[cytoplasm.zones.*]` sections defining `backbone`, `house2`, and `eero_wifi` zones with hub devices, uplinks, speeds, and gate lists
2. **`ecosystem_manifest.toml`** — Annotated gate profiles with `zone`, `hub_port`, `link_speed_mbps`
3. **`GateProfile` in `manifest.rs`** — Added 3 `Option` fields (`zone`, `hub_port`, `link_speed_mbps`), all `#[serde(default)]`, backward compatible. Test added and passing.

The data is machine-readable today. What's needed: typed model in `envelope.rs` and dispatch commands to use it.

---

## Requested Types (for `cellmembrane-types/src/envelope.rs`)

### `HubRole`

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum HubRole {
    Backbone,
    Extension,
    WifiBridge,
}
```

### `SwitchHub`

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SwitchHub {
    pub device: String,
    pub role: HubRole,
    pub max_speed_mbps: u32,
    pub site: String,
    #[serde(default)]
    pub ports: Vec<String>,
}
```

### `ZoneUplink`

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ZoneUplink {
    pub target_zone: String,
    pub link_type: String,
    pub speed_mbps: u32,
    pub latency_ms: f64,
}
```

### `CytoplasmZone`

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CytoplasmZone {
    pub name: String,
    pub hub: SwitchHub,
    #[serde(default)]
    pub uplink: Option<ZoneUplink>,
    #[serde(default)]
    pub gates: Vec<String>,
    #[serde(default)]
    pub status: Option<String>,
}
```

### Integration with `EnvelopeTopology`

Add to the existing `EnvelopeTopology` struct:

```rust
#[serde(default)]
pub cytoplasm_zones: HashMap<String, CytoplasmZone>,
```

This keeps backward compatibility — existing manifests without zones will deserialize with an empty map.

---

## Requested Dispatch Command: `topology.resolve`

### Purpose

Resolve zone membership, inter-gate latency estimates, and routing paths within the cytoplasm.

### Subcommands

```
membrane topology.resolve zone <gate_name>
  → Returns: zone name, hub device, link speed, uplink chain

membrane topology.resolve latency <gate_a> <gate_b>
  → Returns: estimated one-way latency between two gates
  → Logic:
    - Same zone, same hub: < 0.5ms
    - Cross-zone via uplink: sum of uplink latencies
    - Cross-site via WAN: use WireGuard overlay latency

membrane topology.resolve path <gate_a> <gate_b>
  → Returns: ordered list of hubs/links between two gates
```

### Implementation Notes

- Load zones from `TOPOLOGY_MAP.toml` or from the `cytoplasm_zones` field on `EnvelopeTopology`
- Cross-reference `GateProfile.zone` from `ecosystem_manifest.toml`
- For latency: same-zone = hub switch latency (< 0.5ms), cross-zone = sum uplink latencies along path

---

## Requested Enhancement: Zone-Aware `gate.preflight`

### Current State

`gate.preflight` validates network interfaces, WireGuard, DNS, DHCP, nftables. It does not validate zone placement.

### Requested Check

Add a preflight phase that:
1. Reads `GateProfile.zone` from the manifest
2. Looks up the zone in `TOPOLOGY_MAP.toml` (or `EnvelopeTopology.cytoplasm_zones`)
3. Validates that the gate's primary network interface matches expected speed/type for its zone
4. Warns if the gate is not in the zone's `gates` list

### Example Output

```
[preflight] zone: backbone (CRS310)
[preflight] expected link: sfp+2 @ 10000 Mbps
[preflight] actual interface: enp3s0f0 (10G SFP+) — OK
```

---

## Requested Enhancement: Zone-Scoped `gate.discover`

### Current State

`gate.discover` (when implemented) would scan the entire `/22` subnet.

### Requested Behavior

Scope discovery to the gate's zone. If a gate is in `backbone`, scan only devices known to be on the CRS310. If in `house2`, scan only Omada-attached devices.

This reduces scan time, avoids unnecessary ARP storms, and produces zone-contextualized results.

---

## Test Requirements

1. Deserialize `CytoplasmZone` from TOML with and without uplinks
2. `topology.resolve zone` returns correct zone for backbone and extension gates
3. `topology.resolve latency` returns < 0.5ms for same-zone, ~0.5ms for cross-zone via 10G trunk
4. `topology.resolve path` returns correct hub chain (e.g., `[Omada, CRS310]` for house2 → backbone)
5. Missing zone on `GateProfile` yields `None` resolution, not an error
6. Zone hierarchy validates: extension zone must have `uplink` defined

---

## Data Sources (Already Deployed)

| File | Content |
|------|---------|
| `TOPOLOGY_MAP.toml` `[cytoplasm.zones.*]` | Zone definitions with hub devices, ports, uplinks |
| `ecosystem_manifest.toml` `[gates.*]` | Gate profiles with `zone`, `hub_port`, `link_speed_mbps` |
| `TOPOLOGY_MAP.toml` `[latency.*]` | Estimated/measured latency between segments |
| `TOPOLOGY_MAP.toml` `[affinity.*]` | Neural API routing bias weights |

---

## Non-Goals (sporeGate overwatch handles these)

- Physical Eero NAT collapse (operator task, documented in FRAGO)
- Omada controller audit (physical ops, pending access)
- [ISP] IP passthrough configuration (browser session, operator task)
- Updating nftables rules (already composition-deterministic via `firewall.rs`)

---

## Acceptance Criteria

- [ ] `CytoplasmZone`, `SwitchHub`, `ZoneUplink`, `HubRole` types in `envelope.rs`
- [ ] `EnvelopeTopology.cytoplasm_zones` field (serde default, backward compatible)
- [ ] `membrane topology.resolve zone|latency|path` dispatch commands
- [ ] `gate.preflight` zone validation phase
- [ ] Tests for all above
- [ ] `gate.discover` zone-scoping (can be separate PR)
