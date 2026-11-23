# Neighborhood Mesh — Hardware Options for Street-Crossing Links

**Date**: 2026-06-17 | **Wave**: 115
**Context**: Old Everett, Lansing MI. 1920s houses, first on the block.
**Properties**: 4422 Southgate Ave (corner lot, House 1) + 641 Samantha Ave (adjacent west, House 2)

---

## Site Profile — 4422 Southgate / 641 Samantha

```
                    N
                    ↑
    ┌───────────────────────────────────┐
    │         Emily Ave                 │  ~200m block
    ├───────────────────────────────────┤
    │                                   │
    │   ┌─────────┐  ┌─────────┐       │
    │   │ 641     │  │ neighbors│       │
    │   │Samantha │  │         │       │
    │   │(House 2)│  │         │       │
    │   │ OMADA   │  │         │       │
    │   └────┬────┘  └─────────┘       │
    │        │ ←── 80m AOC (10G) ──┐   │
    │   ┌────┴────┐                │   │  Samantha Ave
    │   │ 4422    ├────────────────┘   │  (runs N-S)
    │   │Southgate│                    │
    │   │(House 1)│                    │
    │   │ CRS310  │                    │
    │   │ [ISP] GW  │                    │
    │   └─────────┘  ← CORNER LOT     │
    │                                   │
    ├───────────────────────────────────┤
    │         Southgate Ave (runs E-W)  │
    └───────────────────────────────────┘
```

**Measured distances (from maps + AOC length):**

| Link | Distance | Current Transport |
|------|----------|-------------------|
| House 1 ↔ House 2 (adjacent lots) | ~15-25m (structure to structure) | 80m AOC (routed path) |
| House 1 ↔ across Southgate | ~25-30m (street width + setback) | None yet |
| House 1 ↔ next house east on Southgate | ~15m (shared fence) | None yet |
| Full block perimeter (loop) | ~600-700m | — |
| Farthest point on block | ~300m diagonal | — |

**The 80m AOC**: Running between adjacent properties (~15-25m as the crow flies)
with routing through walls/conduit adds length. 10G active optical cable — reliable,
but the user plans to learn custom fiber termination for future runs.

**Lot dimensions** (1920s plat, Lansing zoning): ~40-50ft wide x 100-108ft deep
**Block length**: ~200-250m (typical Midwest residential grid)
**Terrain**: Dead flat. No elevation changes. Mature trees (canopy).
**Obstructions for radio**: Trees (seasonal leaf coverage), power lines, neighboring houses

---

## Distance Reality Check

For this specific neighborhood, the distances are TINY by radio standards:

| Radio | Rated Range | Your Longest Link (~300m) | Overkill Factor |
|-------|-------------|--------------------------|-----------------|
| MikroTik SXTsq 5 ax | 1+ km | 300m | 3x+ |
| Ubiquiti NanoBeam 5AC | 10+ km | 300m | 33x |
| Ubiquiti LiteBeam 5AC | 15+ km | 300m | 50x |

Any radio in this class will have **perfect signal** at these distances.
The concern isn't range — it's trees and house obstructions. At 300m through
mature canopy, even an $65 radio will punch through fine at 16 dBi gain.

For adjacent-house links (15-25m), you don't even need directional antennas —
a standard WiFi AP mounted externally would work.

---

## Current Inter-House Link (Proven)

| Attribute | Value |
|-----------|-------|
| **Cable** | 80m Active Optical Cable (AOC) |
| **Speed** | 10 Gbps |
| **Latency** | <0.1ms |
| **Path** | House 1 CRS310 SFP+ → routed through walls/conduit → House 2 Omada SFP+ |
| **Status** | LIVE, production traffic |
| **Future** | Learn custom fiber termination (MTP/MPO, LC) for shorter/cleaner runs |

The AOC is overkill for a 15-25m physical distance (80m of cable for routing),
but it's proven and running 10G without issues. Custom fiber will be cleaner
but the AOC holds until then.

---

## Expansion Topology — Block Loop

The block around 4422 Southgate / 641 Samantha forms a natural mesh ring:

```
           ~250m
    ┌─────────────────────────────────────┐
    │            Emily Ave                 │
    │                                      │
    │  [node]    [node]    [node]   [node] │  ~15-25m between
  S │    │         │         │        │    │  adjacent houses
  a │    ├─Cat6a───┤         ├─Cat6a──┤    │  (shared fence)
  m │    │         │         │        │    │
  a │  [641]─────[you]     [?]      [?]   │  ~100m
  n │ (House2)  (House1)                   │  block depth
  t │            4422                      │
  h │         Southgate                    │
  a │              │                       │
    │              │ <── cross street ~25m  │
    ├──────────────┼───────────────────────┤
    │         Southgate Ave                │
    │              │                       │
    │            [node across street]      │
    └─────────────────────────────────────┘
```

**Link budget for full block ring:**
- Adjacent houses (shared fence): Cat6a direct burial, 15-25m, $20-30 each
- Across street: P2P radio pair ($130) OR Cat6a in conduit under road ($50 + permits)
- Full block perimeter loop: 4-6 links totaling ~$200-400 in cable/radios
- Each node: NUC ($200-350) + 2.5G NIC (built in)

A full block ring with 6 NUCs would give you:
- ~72 CPU threads (6x Ryzen 5)
- ~168 GB RAM
- Redundant paths (ring topology — cut one link, traffic routes the other way)
- All sub-1ms latency (wired) or sub-3ms (radio)
- Total hardware cost: ~$1500-2500 for compute + networking

---

## Option Comparison

| Option | Cost (per link) | Bandwidth | Latency | Range | Power | Weather | Maintenance |
|--------|-----------------|-----------|---------|-------|-------|---------|-------------|
| Cat6a Direct Burial | $35-95 | 10 Gbps | <0.5ms | 100m max | 0W (passive) | Excellent | None (buried) |
| MikroTik SXTsq 5 ax | $130 (pair) | 1.2 Gbps | 2-3ms | 1+ km | 12W (pair) | IP55 | Firmware updates |
| Ubiquiti NanoBeam 5AC | $198 (pair) | 450 Mbps | 2-3ms | 10+ km | 17W (pair) | IP67-grade | Firmware updates |
| Ubiquiti LiteBeam 5AC | $178 (pair) | 450 Mbps | 2-3ms | 15+ km | 14W (pair) | IP67-grade | Firmware updates |
| Cat6a Aerial (on fence) | $45-85 | 10 Gbps | <0.5ms | 100m max | 0W (passive) | Good (UV-rated) | Visual check |

---

## Tier A: Wired Drops (Strongest, Cheapest, Least Maintenance)

### Cat6a Direct Burial — Between Adjacent Houses

**Best for**: Houses sharing a fence line or with <50m ground distance.

| Attribute | Value |
|-----------|-------|
| **Product** | Cat6a Shielded Direct Burial (F/UTP, LLDPE jacket) |
| **Example** | Syston 1796-SB-BK-100 (Home Depot) |
| **Price** | $34-45 per 100ft |
| **Speed** | 10 Gbps (at 55m), 5 Gbps (at 100m) |
| **Latency** | <0.1ms additional |
| **Installation** | Trench 6-12" deep along fence line, or staple to fence |
| **Termination** | RJ45 keystone jacks at each end |
| **NIC required** | 2.5G NIC ($15-25) — already standard on NUCs |
| **Total cost per link** | ~$50-80 (cable + connectors + NIC) |

**Why this is ideal for Old Everett:**
- Small lots = short runs (30-50ft between houses)
- No permits needed for low-voltage direct burial in residential
- Zero ongoing power cost
- Immune to RF interference, weather, and neighbor WiFi congestion
- Full 2.5G+ bandwidth — matches CRS310 port speed

**Installation path:**
```
House 1 NUC → Cat6a patch → weatherproof junction box (exterior wall)
→ direct burial cable (trench or fence-stapled) →
→ weatherproof junction box (House 2 exterior) → Cat6a patch → NUC/switch
```

### Cat6a Aerial — Over Fences

For runs where trenching isn't practical:
- UV-rated outdoor Cat6a ($45-85/100ft)
- Stapled to fence top or run on messenger wire
- Drip loops at entry points
- Slightly less durable than buried (UV degradation over 5-10 years)

---

## Tier B: Point-to-Point Radio (No Cable Run Needed)

### MikroTik SXTsq 5 ax (RECOMMENDED for price/performance)

**Best for**: Crossing streets, reaching non-adjacent houses, 50-500m.

| Attribute | Value |
|-----------|-------|
| **Model** | SXTsq-5axD (Wi-Fi 6 version) |
| **Price** | $65 each ($130 per link) |
| **Throughput** | Up to 1.2 Gbps (Wi-Fi 6, 80 MHz channel) |
| **Antenna** | 16 dBi integrated directional |
| **Range** | 1+ km (practical: 100-500m in residential) |
| **Power** | 6W each (PoE powered, 12-28V passive) |
| **Ports** | 1x GbE RJ45 |
| **OS** | RouterOS v7 (same as your CRS310 — familiar) |
| **Size** | 129 x 129 x 34mm (tiny, mountable on wall/pole) |
| **Temperature** | -40 to 70C |
| **IP rating** | IP55 |
| **License** | Level 4 (can be AP or station) |

**Why MikroTik for this ecosystem:**
- You already run RouterOS on the CRS310 — same management paradigm
- IPsec hardware acceleration built in (WireGuard overlay is cheap)
- $65/unit is the best price/performance for outdoor P2P
- Wi-Fi 6 gives real-world 400-600 Mbps (more than enough for gate traffic)
- RouterOS scripting can auto-detect link loss and alert via mesh

**Setup (one pair):**
```
Unit A (House 1, AP mode):
  - Mount on exterior wall facing House 3
  - PoE from indoor injector
  - Cat6 patch to CRS310 port (extends sovereign LAN)
  - RouterOS bridge mode (transparent L2)

Unit B (House 3, Station mode):
  - Mount on exterior wall facing House 1
  - PoE from indoor injector
  - Cat6 to NUC at friend's house
  - NUC gets DHCP from sporeGate (or local gate if subnetted)
```

### Ubiquiti NanoBeam 5AC Gen2

**Best for**: Longer distances (200m+), higher gain needed, RF-noisy environments.

| Attribute | Value |
|-----------|-------|
| **Model** | NBE-5AC-Gen2 |
| **Price** | $99 each ($198 per link) |
| **Throughput** | 450+ Mbps (airMAX TDMA, 80 MHz channel) |
| **Antenna** | 19 dBi integrated directional |
| **Range** | 10+ km |
| **Power** | 8.5W each (24V passive PoE, adapter included) |
| **Ports** | 2x GbE RJ45 |
| **OS** | airOS 8 (UISP managed) |
| **Size** | 189 x 189 x 125mm |
| **Temperature** | -40 to 80C |
| **Wind** | Survives 200 km/h |

**Advantages over MikroTik:**
- Higher antenna gain (19 vs 16 dBi) — better for longer/obstructed paths
- Two ethernet ports (daisy-chain potential)
- UISP cloud management (monitoring dashboard)
- ESD/EMP protection (24kV)

**Disadvantages:**
- $34 more per unit than MikroTik
- Slower throughput (450 vs 1200 Mbps theoretical)
- Different management platform (airOS vs RouterOS)
- Proprietary TDMA protocol (not standard 802.11)

### Ubiquiti LiteBeam 5AC Gen2

**Best for**: Budget long-range with higher gain.

| Attribute | Value |
|-----------|-------|
| **Model** | LBE-5AC-Gen2 |
| **Price** | ~$89 each ($178 per link) |
| **Throughput** | 450+ Mbps |
| **Antenna** | 23 dBi (highest gain in this class) |
| **Range** | 15+ km |
| **Power** | 7W each |
| **Ports** | 1x GbE RJ45 |

**Use case:** Only if you need to reach a site 500m+ away with obstructions.
For Old Everett (short distances), the NanoBeam or SXTsq are better choices.

---

## Tier C: Hybrid (Best of Both)

**Recommended deployment for Old Everett neighborhood mesh:**

```
Adjacent house (shares fence):
  → Cat6a direct burial ($50 total)
  → Full 2.5-10G bandwidth, zero power, zero maintenance

Across-street house:
  → MikroTik SXTsq 5 ax pair ($130 total)
  → 400-600 Mbps real-world, 2-3ms latency
  → PoE powered, weatherproof, RouterOS managed

Down-the-block / around-corner:
  → Ubiquiti NanoBeam 5AC pair ($198 total)
  → 300-450 Mbps real-world, 2-3ms latency
  → Higher gain punches through more obstacles
```

---

## Power Budget

All radio options use PoE (Power over Ethernet). Each link adds:

| Option | Power per link | Annual cost (at $0.12/kWh) |
|--------|---------------|---------------------------|
| Cat6a (wired) | 0W | $0 |
| MikroTik SXTsq pair | 12W | $12.60/year |
| NanoBeam pair | 17W | $17.87/year |

Negligible. A pair of radios costs less per year than a nightlight.

---

## Recommended Shopping List

**Next adjacent house (east along Southgate, shared fence):**

| Item | Qty | Price | Source |
|------|-----|-------|--------|
| Cat6a Direct Burial 50ft | 1 | $25 | Home Depot / Amazon |
| RJ45 Outdoor Junction Box | 2 | $8 each | Amazon |
| Cat6a Keystone Jacks | 4 | $3 each | Amazon |
| GMKtec NucBox (2.5G NIC) | 1 | $200-350 | Amazon |
| **Total (wired, adjacent)** | | **~$255** | |

**Across Southgate Ave (radio bridge, ~25m):**

| Item | Qty | Price | Source |
|------|-----|-------|--------|
| MikroTik SXTsq 5 ax | 2 | $65 each | Streakwave / Baltic Networks |
| PoE injector (if not included) | 2 | $15 each | Amazon |
| Outdoor Cat6 patch (short) | 2 | $10 each | Amazon |
| Wall mount bracket | 2 | $5 each | Amazon |
| GMKtec NucBox (2.5G NIC) | 1 | $200-350 | Amazon |
| **Total (radio, cross-street)** | | **~$390** | |

**Custom fiber run (when you're ready to terminate your own):**

| Item | Qty | Price | Source |
|------|-----|-------|--------|
| OM4 multimode fiber, 30m | 1 | $20-40 | FS.com / Amazon |
| LC duplex connectors | 4 | $5 each | FS.com |
| Fiber termination kit | 1 | $80-150 | Amazon (one-time) |
| SFP+ 10G SR modules (pair) | 2 | $15 each | FS.com |
| **Total (custom fiber)** | | **~$150-250** (+ $80-150 tools first time) | |

Note: You already run an 80m AOC at 10G. Custom fiber will let you do
cleaner, shorter runs and potentially multiplex (WDM) for future capacity.

---

## Integration with Sovereign Mesh

Once physical link is established (wired or radio), the remote NUC:

1. Gets DHCP from sporeGate (if same L2 via bridge) or from local gate (if subnetted)
2. Runs `membrane gate.bootstrap <name>` — gets 13 primals
3. Joins WireGuard overlay (10.13.37.x)
4. Appears in mesh with appropriate affinity score
5. Contributes compute to the distributed HPC

The transport is invisible to the primals. A NUC reached via Cat6a burial, a MikroTik radio, or a WireGuard tunnel all look the same to membrane.

---

## Regulatory Notes (Lansing, MI)

- **Direct burial cable**: No permit needed for low-voltage (Cat6) in residential. Dig safe (MISS DIG 811) recommended if deeper than 12".
- **5 GHz outdoor radios**: FCC Part 15, no license required. All listed devices are FCC certified.
- **Aerial cable**: Check local ordinance on visible cable between structures. Typically allowed if on your own property or with neighbor agreement.
- **Power lines**: Never cross or approach utility lines. Route cables at ground level or along fence lines.
