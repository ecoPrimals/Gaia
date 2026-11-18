# Geospatial Cross-Matrix — Pattern Document for Teams

**Wave**: 165i | **Date**: Oct 7, 2026
**From**: eastGate overwatch
**To**: sporeGate ops, northGate investigation, all gates
**Status**: ACTIVE — sensors deployed, pattern ready for implementation
**Upstream**: DISTRIBUTED_SURVEILLANCE_DETECTION_MESH.md, ENTITY_TOPOLOGY_MONITOR_SUBGEN_WAVE165H.md

---

## TL;DR

We found that the sensor mesh is a **passive planetary radar**. The fleet's traffic, observed from GPS-fixed sensor nodes, produces a spatial map of global surveillance infrastructure. This document describes the cross-matrix data structure and what each team needs to do.

---

## The Cross-Matrix

### What It Is

A sensor × entity grid where each cell contains behavioral observations from one geographic vantage point:

```
                    NYC (golgiBody)     DE (Hetzner)       IN (Linode)        VA (OVH)         UK (OVH)
                    40.71°N, 74.01°W   50.47°N, 12.37°E   19.08°N, 72.88°E  38.88°N, 77.52°W  51.51°N, 0.13°W
                    ────────────────   ────────────────   ────────────────   ────────────────   ────────────────
Meta/Dublin          56 IPs, 2.0rps    (filling...)       (CT pending)       (deploying)        (deploying)
  behavioral_hash   b6c7dc18           ?                  ?                  ?                  ?
  blame_pct          32.9%             ?                  ?                  ?                  ?
  chrome_lag         10                ?                  ?                  ?                  ?
  timing_cv          0.057             ?                  ?                  ?                  ?
  targets_real       YES               ?                  ?                  ?                  ?

Anthropic/US         1 IP, 10.8rps     (filling...)       (CT pending)       (deploying)        (deploying)
  behavioral_hash   (honest)           ?                  ?                  ?                  ?
  targets_scatter    YES               ?                  ?                  ?                  ?

Stealth/?            8 IPs             (filling...)       (CT pending)       (deploying)        (deploying)
Huawei/?             3 IPs             (filling...)       (CT pending)       (deploying)        (deploying)
```

### What Each Cell Tells You

- **Same hash across columns** → Global coordination proven. Same toolkit everywhere.
- **Different proxy pools per column** → Geographic proxy allocation exposed.
- **Entity missing from a column** → Geographic scope limitation revealed.
- **Different blame_pct per column** → Targeting strategy varies by region.
- **Different timing per column** → Fleet capacity allocation varies.

---

## Current Sensor Array Status

| Layer | IP | Provider | Location | Jurisdiction | Status | Next Step |
|-------|-----|----------|----------|-------------|--------|-----------|
| golgiBody | (WG mesh) | DigitalOcean | NYC, US 🇺🇸 | US federal | **LIVE** — 12.6 RPS, 63 fleet IPs | Baseline sensor |
| golgiLayerHetzner | 2.28.141.35 | Hetzner | Falkenstein, DE 🇩🇪 | EU + StGB | **LIVE** — 27 req | Accumulating |
| golgiLayerLinode | 172.232.85.202 | Akamai/Linode | Mumbai, IN 🇮🇳 | India IT Act | **HARDENED** | Needs provision script |
| OVH US | — | OVH | Vint Hill, VA 🇺🇸 | US + VA state | In progress | User creating |
| OVH UK | — | OVH | UK 🇬🇧 | UK CMA/GDPR | In progress | User creating |

### Credentials (for sporeGate provisioning)

**golgiLayerLinode (Mumbai)**:
- IP: `172.232.85.202`
- SSH: root, key `eastgate-beardog-v1` authorized
- Root password: `7AIvjtQHI02pwLiYCxUUjKzl`
- Latency from eastGate: ~225ms
- Prepared: updated, UFW (22/80/443), fail2ban, `/opt/membrane/` created
- **Ready for**: `provision-golgi-layer.sh` + DNS pointing

---

## What Each Team Does

### sporeGate ops

1. **Run provision script** on golgiLayerLinode (172.232.85.202):
   - Install Caddy + skunky-ingest + scatter server
   - Point `layer3.primals.eco` DNS → 172.232.85.202
   - Register in plasmid federation config
   - Wait for CT log discovery (~24-48h)

2. **Add GeoIP enrichment** to skunky-ingest:
   - Tag each `RequestFingerprint` with source GPS coordinates (from GeoIP)
   - Add `source_lat`, `source_lon` fields to `EntityProfile`
   - The sensor's own GPS is known at deploy time — store in layer config

3. **Build cross-matrix endpoint**:
   - New endpoint: `signal.primals.eco/matrix.json`
   - Each layer reports its local entity topology
   - Federation merges into the sensor × entity grid
   - Include GPS coordinates for both sensors and sources

4. **Update `membrane-monitor.sh`**:
   - New view: `membrane-monitor.sh matrix` — shows the cross-matrix
   - Color-code by confidence (single-sensor vs. multi-sensor corroboration)

### northGate investigation

1. **Prepare per-jurisdiction evidence templates** using cross-matrix data
2. **Track which entities appear in which jurisdictions** — this is the complaint timeline
3. **When 3+ sensors observe the same behavioral hash** → trigger coordinated complaint preparation

### All gates (membrane-monitor)

The `membrane-monitor.sh` tool works from any gate. Current views:

```bash
./membrane-monitor.sh              # full dashboard
./membrane-monitor.sh bloom        # bloom status
./membrane-monitor.sh topology     # entity topology
./membrane-monitor.sh fleet        # fleet activity
./membrane-monitor.sh layers       # layer health
./membrane-monitor.sh plasmid      # conserved plasmid feed
./membrane-monitor.sh live         # streaming feed
./membrane-monitor.sh watch        # continuous 10s refresh
```

After cross-matrix is built:
```bash
./membrane-monitor.sh matrix       # sensor × entity grid (future)
```

---

## API-Provisioned Sensor Pattern

### Linode API (Proven)

eastGate successfully API-provisioned golgiLayerLinode in <2 minutes:

```bash
export LINODE_TOKEN="<token>"
curl -s -X POST https://api.linode.com/v4/linode/instances \
  -H "Authorization: Bearer $LINODE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "region": "ap-west",
    "type": "g6-nanode-1",
    "image": "linode/debian12",
    "label": "golgiLayerLinode",
    "root_pass": "<generated>",
    "authorized_users": ["ecoPrimal"],
    "tags": ["beehive-mesh", "ecoPrimals"]
  }'
```

Initial hardening (SSH in, run):
```bash
hostnamectl set-hostname golgiLayerLinode
apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y -qq
apt-get install -y -qq ufw fail2ban curl unattended-upgrades
ufw allow 22/tcp && ufw allow 80/tcp && ufw allow 443/tcp && echo "y" | ufw enable
systemctl enable --now fail2ban
mkdir -p /opt/membrane /run/membrane
```

Then hand to sporeGate's `provision-golgi-layer.sh` for Caddy + skunky-ingest + scatter + DNS.

### Future: mesh-provision primal

A tool that takes `--provider linode --region tokyo` and does everything:
1. API-creates the VPS
2. Waits for boot
3. Hardens (UFW, fail2ban, updates)
4. Runs provision script (Caddy, skunky-ingest, scatter)
5. Points DNS
6. Registers in federation
7. Outputs the new column for the cross-matrix

---

## The Insight

The fleet's noise is a planetary map. Each sensor node at a known GPS coordinate receives traffic from corporate infrastructure at known GPS coordinates. The behavioral hashes are deterministic. The cross-matrix resolves a global picture of who is scraping whom, from where, with what tools, at what intensity.

**We are using their noise to map the entire planet as a digital layer.**

Every $5/month sensor adds a column to the matrix. Every column adds a jurisdiction. Every jurisdiction adds legal weight. The fleet paints the picture by scraping. The picture is the evidence. The evidence is GPS-registered.

The noise is the signal. The signal is the map. The map is the case.

---

*Wave 165i — eastGate overwatch, Oct 7, 2026*
