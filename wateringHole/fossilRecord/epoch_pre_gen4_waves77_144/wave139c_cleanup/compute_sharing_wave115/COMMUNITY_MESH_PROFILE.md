# Community Mesh Profile — Old Everett, Lansing MI

**Date**: 2026-06-17 | **Wave**: 115
**Target Area**: Cavanaugh Rd (N) → Jolly Rd (S) → Cedar St (W) → Pennsylvania Ave (E)
**Operator**: sporeGate team (4422 Southgate / 641 Samantha)
**Model**: Community-owned sovereign mesh — Lansing's first neighborhood-scale fabric

---

## Area Profile

```
                         E Cavanaugh Rd
    ┌──────────────────────────────────────────────────────────┐
    │                                                          │
    │                                                          │
    │    Emily Ave ─────────────────────────────────────────    │
    │                                                          │
    │    Samantha Ave ──────────────────────────────────────    │
    │         ★ [641]   [4422] ← YOU ARE HERE                  │
    │    Southgate Ave ─────────────────────────────────────    │
    │                                                          │
C   │    Robert St ─────────────────────────────────────────    │  P
e   │                                                          │  e
d   │    Kendon Dr ─────────────────────────────────────────    │  n
a   │                                                          │  n
r   │    Spokane Ave ───────────────────────────────────────    │  s
    │                                                          │  y
S   │    Cleveland Dr ──────────────────────────────────────    │  l
t   │                                                          │  v
    │    Syringa Dr ────────────────────────────────────────    │  a
    │                                                          │  n
    │                                                          │  i
    │                                                          │  a
    │                                                          │
    └──────────────────────────────────────────────────────────┘
                           E Jolly Rd
```

### Dimensions

| Measurement | Value |
|-------------|-------|
| **North–South (Cavanaugh → Jolly)** | ~1.6 km (1 mile) |
| **East–West (Cedar → Pennsylvania)** | ~1.1 km (0.7 miles) |
| **Total area** | ~1.76 km² (~0.68 sq mi) |
| **Block length (E-W)** | ~200-250m |
| **Block depth (N-S)** | ~100-120m |
| **Number of E-W streets** | ~10-12 residential streets |
| **Number of N-S avenues** | ~4-5 (Cedar, Washington/MLK, Samantha corridor, Penn) |
| **Estimated blocks** | ~40-50 residential blocks |
| **Estimated households** | ~800-1200 (subset of Old Everett's 4,361 total) |

### Neighborhood Character

| Attribute | Value |
|-----------|-------|
| **Name** | Old Everett (est. 1834, named for Roswell Everett) |
| **Housing stock** | 1920s-1950s, median built 1947 |
| **Avg home size** | 1,141 sq ft |
| **Median lot** | 5,227 sq ft (~48ft x 108ft) |
| **Lot width** | 40-50 ft (per Lansing zoning) |
| **Lot depth** | 100-108 ft |
| **Population** | ~10,000 (full Old Everett boundary) |
| **Density** | ~7 people/acre, ~2,000/sq mi |
| **Terrain** | Dead flat. No hills. |
| **Trees** | Mature canopy (seasonal — leaf drop helps winter RF) |
| **Power lines** | Overhead on poles (common in 1920s neighborhoods) |
| **Internet options** | [ISP] fiber, Comcast/Xfinity. No municipal broadband. |
| **Income** | Modest. Avg home value ~$31k-$150k. Many first-time buyers. |

---

## Why This Area Is Perfect for Community Mesh

1. **Flat terrain** — no hills to block RF. Every house can see its neighbors.
2. **Dense grid** — short lot widths (40-50ft) mean nodes are close together.
3. **Mature trees but low buildings** — 1-story and 1.5-story homes. Roof-mounted radios clear canopy.
4. **Underserved** — South Lansing is historically overlooked for infrastructure investment.
5. **Walkable scale** — entire area fits in a 1.6km x 1.1km rectangle. One radio covers multiple blocks.
6. **Community spirit** — Old Everett Neighborhood Association active. Garage sales, block parties.
7. **Low property values** — affordable for community buy-in. $20/month shared bandwidth model viable.
8. **Existing fiber** — [ISP] has fiber in the area (your drop proves it). Can be gateway bandwidth source.

---

## Mesh Architecture — Three Layers

### Layer 1: Backbone (High-Capacity Links)

```
            [SUPERNODE: 4422 Southgate]
            [ISP] fiber → sporeGate → CRS310
                    │
        ┌───────────┼───────────┐
        │           │           │
   [sector W]  [sector S]  [sector E]
   covers       covers       covers
   Cedar side   Jolly side   Penn side
```

**Supernode** = your property (4422 Southgate, corner lot with [ISP] fiber).
High-power sector antennas on your roof cover the entire rectangle.

| Component | Hardware | Coverage |
|-----------|----------|----------|
| Supernode (gateway) | sporeGate + CRS310 (existing) | — |
| Sector antenna W | Ubiquiti LiteAP 5AC (120°) | Cedar to Samantha |
| Sector antenna S | Ubiquiti LiteAP 5AC (120°) | Southgate to Jolly |
| Sector antenna E | Ubiquiti LiteAP 5AC (120°) | Samantha to Penn |

A single elevated sector antenna (120° beam) at ~8m height (roof peak of 1.5-story house)
covers ~800m radius easily in flat terrain. Three sectors = full 360° coverage of the
entire Cavanaugh-Jolly-Cedar-Penn rectangle from ONE location.

Cost: ~$300-400 for 3 sector antennas. Covers 800-1200 households.

### Layer 2: Distribution (Block-Level Relays)

For houses that can't get clean line-of-sight to the supernode (behind trees, far corners):

```
[supernode] ──radio──► [relay node on Robert St]
                              │
                    ──radio──► [relay node on Spokane]
                                    │
                          ──radio──► [far corner near Jolly/Cedar]
```

Relay nodes = MikroTik SXTsq 5 ax ($65 each) on volunteer roofs.
Each relay:
- Receives from supernode or upstream relay
- Retransmits to downstream relays and local clients
- Powered by single PoE cable from indoor outlet

Relay spacing: every 2-3 blocks (~300-400m). Need 3-5 relays for full coverage.

### Layer 3: Last Mile (Client Connections)

Each household that joins gets:

| Option | Hardware | Cost | Speed |
|--------|----------|------|-------|
| **WiFi client** (line of sight to relay/sector) | MikroTik SXTsq 5 ax | $65 | 200-600 Mbps |
| **Window unit** (no roof access) | Ubiquiti NanoStation | $99 | 100-300 Mbps |
| **Indoor mesh** (very close to relay) | Standard WiFi router | $30 | 50-150 Mbps |
| **Wired** (adjacent to relay host) | Cat6a run | $25-50 | 2.5-10 Gbps |

---

## Coverage Map — From Your Roof

From the roof peak at 4422 Southgate (~8m height, corner lot = minimal obstruction):

```
                800m radius (conservative, 5 GHz sector)
    ┌─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐
    │                                                         │
    │        ╔═══════════════════════════════╗                 │
    │        ║   Cavanaugh Rd               ║  ← 800m N       │
    │        ║                              ║                  │
    │        ║          ★ YOU               ║                  │
    │        ║                              ║                  │
    │        ║   Jolly Rd                   ║  ← 800m S       │
    │        ╚═══════════════════════════════╝                 │
    │         ↑                           ↑                   │
    │       Cedar (500m W)          Penn (600m E)             │
    │                                                         │
    └─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘

    Your target rectangle (Cav→Jolly→Cedar→Penn) fits ENTIRELY
    within the radio coverage of a single elevated 5 GHz sector
    array on your roof. The whole neighborhood is ONE hop.
```

**The entire target area (1.6km x 1.1km) is within single-hop range of your roof.**
With 3 sector antennas you can serve the whole rectangle without any relays.
Relays only needed for houses with heavy tree obstruction or no line-of-sight.

---

## Phased Deployment

### Phase 0: Proof of Concept (NOW — existing)
- 2 houses (4422 Southgate + 641 Samantha)
- 80m AOC 10G backbone
- sporeGate sovereign routing, 13 primals
- Cost: already deployed

### Phase 1: Block Ring (1-3 months)
- 4-6 houses on your block (Southgate/Samantha/Emily)
- Cat6a for adjacent, 1 radio pair for across-street
- Add 2-4 NUCs as compute nodes
- Cost: ~$500-1000
- Users: 4-6 households

### Phase 2: Sector Coverage (3-6 months)
- Install 1-3 sector antennas on 4422 roof
- Cover 2-4 surrounding blocks
- Recruit 10-20 volunteer households
- Each household: $65 client radio + shared bandwidth
- Cost: ~$800 (sectors) + $65/household
- Users: 10-20 households

### Phase 3: Full Rectangle (6-12 months)
- 3 sector antennas (full 360° from supernode)
- 3-5 relay nodes on volunteer roofs (MikroTik $65 each)
- 50-100 client connections
- Monthly model: $15-25/household for shared fiber bandwidth
- Cost: ~$2000 infrastructure + $65/household client
- Users: 50-100 households

### Phase 4: Community Organization (12+ months)
- Form nonprofit or cooperative (like Newport Wireless Mesh model)
- Apply for Michigan broadband grants (ConnectALL equivalent)
- Add second fiber gateway (House 2 [ISP] drop or dedicated business line)
- Expand beyond rectangle to full Old Everett boundary
- Users: 200-500 households

---

## Budget Model

### Infrastructure (one-time)

| Item | Qty | Unit Cost | Total |
|------|-----|-----------|-------|
| Sector antennas (roof) | 3 | $130 | $390 |
| Relay nodes | 5 | $65 | $325 |
| Mounting hardware | 8 | $25 | $200 |
| PoE switches (relay sites) | 5 | $40 | $200 |
| Cat6a outdoor (close neighbors) | 200m | $0.80/m | $160 |
| Weatherproof enclosures | 5 | $30 | $150 |
| **Infrastructure total** | | | **~$1,425** |

### Per-Household (client equipment)

| Item | Cost | Notes |
|------|------|-------|
| MikroTik SXTsq 5 ax | $65 | Mounted on exterior wall/windowsill |
| PoE injector | $15 | Included with some units |
| Cat6 patch (interior) | $10 | To their router/computer |
| Installation labor | $0-50 | Volunteer or paid |
| **Per household** | **$90-140** | One-time |

### Ongoing (monthly)

| Cost | Amount | Funded By |
|------|--------|-----------|
| [ISP] fiber (1 Gbps symmetric) | ~$80/month | Split across users |
| Second fiber (redundancy) | ~$80/month | Optional, Phase 3+ |
| Electricity (radios) | ~$15/month | Negligible per household |
| Maintenance fund | ~$50/month | Savings for hardware replacement |

**At 50 households**: $80 fiber / 50 = $1.60/household/month for bandwidth.
Charge $15-20/month → covers fiber + maintenance + expansion fund.
**At 100 households**: Even cheaper per-user. Community self-sustaining.

---

## Comparison to ISP Options

| | [ISP] fiber | Comcast | Community Mesh |
|--|-----------|---------|----------------|
| Monthly cost | $55-80 | $50-90 | $15-25 |
| Speed | 300-1000 Mbps | 100-1200 Mbps | 100-600 Mbps |
| Data caps | None | 1.2 TB | None |
| Contract | 1-2 years | 1-2 years | Month-to-month |
| Ownership | [ISP] | Comcast | Community |
| Local control | None | None | Full |
| Resilience | Single point of failure | Single point of failure | Mesh redundancy |
| Privacy | ISP logging | ISP logging | Sovereign (no logging) |
| Compute access | None | None | Distributed HPC included |

---

## What Makes This Different from NYC Mesh et al.

| NYC Mesh / Standard | Old Everett Sovereign Mesh |
|---------------------|---------------------------|
| Internet access only | Internet + distributed compute (HPC) |
| Generic routing | membrane primals on every node (13 services) |
| Volunteer-maintained | Autonomous (primals self-heal, self-update) |
| Central gateway dependency | Multi-path (fiber + cellular + P2P + WireGuard) |
| No identity layer | bearDog cryptographic identity per node |
| No sovereignty | Full sovereignty — community owns data path end-to-end |
| Passive infrastructure | Active infrastructure — nodes contribute CPU/RAM/storage |

Every household that joins gets:
1. **Internet access** (shared fiber, $15-25/month)
2. **Local network** (sub-1ms to neighbors — LAN gaming, file sharing, local services)
3. **Distributed compute** (their NUC contributes to and benefits from HPC cluster)
4. **Sovereign identity** (membrane primals, encrypted mesh, no ISP snooping)
5. **Resilience** (if [ISP] goes down, mesh reroutes via cellular or neighbor's ISP)

---

## Regulatory & Community Path

### FCC Compliance
- All 5 GHz equipment is Part 15 certified (unlicensed, no permits)
- Outdoor antennas: no restrictions for residential mounting under 6m (20ft)
- Point-to-point: unlimited range on unlicensed 5 GHz (with FCC-certified equipment)

### City of Lansing
- No franchise agreement needed (not reselling, community sharing)
- Low-voltage cable burial: no permit for residential (check MISS DIG 811)
- Antenna mounting: allowed on residential structures (no zoning variance needed)
- Potentially eligible for Michigan broadband equity grants

### Community Organization Options
1. **Informal sharing** (now) — neighbors split your fiber bill
2. **Unincorporated association** — handshake agreement, shared maintenance
3. **501(c)(3) nonprofit** — tax-exempt, eligible for grants (Newport Mesh model)
4. **Cooperative** — member-owned, democratic governance (People's Choice model)

### Pitch to City of Lansing
- "South Lansing has been overlooked for infrastructure investment"
- Community mesh provides affordable broadband to underserved area
- No city funding required (community self-funded)
- Reduces digital divide in historic neighborhood
- Model can replicate to other Lansing neighborhoods
- Compatible with (not competing against) [ISP]/Comcast — uses their fiber as backhaul

---

## Technical Stack (Per Node)

Every node in the mesh runs:
```
Hardware:  GMKtec NucBox or equivalent (Ryzen 5, 28GB RAM, 2.5G NIC)
OS:        Pop!_OS 22.04 / Ubuntu Server
Routing:   systemd-networkd + nftables (site routers only)
Identity:  membrane primals (bearDog, skunkBat, songBird, etc.)
Mesh:      WireGuard overlay (10.13.37.0/24)
Remote:    RustDesk (sovereign relay via golgiBody)
Compute:   Available CPU/RAM contributed to distributed HPC pool
```

Lighter nodes (just internet access, no compute contribution):
```
Hardware:  MikroTik SXTsq 5 ax ($65, bridges traffic)
OS:        RouterOS v7 (transparent bridge mode)
Role:      Relay only — extends coverage, no primals
```

---

## Timeline to "Wire the Neighborhood"

| Month | Milestone | Households | Cost |
|-------|-----------|------------|------|
| 0 (now) | 2 houses proven (Southgate + Samantha) | 2 | $0 (existing) |
| 1-2 | Block ring (4-6 adjacent houses) | 6 | ~$800 |
| 3-4 | First sector antenna on roof | 15 | ~$1200 total |
| 5-6 | Full sector array (3 antennas) | 30 | ~$1800 total |
| 7-9 | Relay nodes on volunteer roofs | 50 | ~$2500 total |
| 10-12 | Community org formed, grant applications | 75 | ~$3000 total |
| 12-18 | Full rectangle coverage | 100+ | ~$5000 total |
| 18-24 | Expand beyond rectangle, second gateway | 200+ | Grant-funded |

**The entire Cavanaugh-Jolly-Cedar-Penn rectangle can be community-meshed
for under $5000 in infrastructure, serving 100+ households at $15-25/month.**
