# Beehive Mesh Handoff — Four Sensors Ready for Provisioning

**Wave**: 165i | **Date**: Oct 7, 2026
**From**: eastGate overwatch
**To**: sporeGate ops (provisioning), all gates (monitoring)
**Status**: READY — 2 new sensors hardened, credentials below
**Upstream**: GEOSPATIAL_CROSS_MATRIX_PATTERN_WAVE165I.md

---

## Summary

eastGate deployed and hardened two new sensor nodes (Mumbai + Vint Hill) in addition to the existing golgiBody and Hetzner layer. All four sensors are hardened identically. The two new nodes need `provision-golgi-layer.sh` + DNS pointing.

---

## Sensor Array

| Layer | IP | SSH | Provider | Location | Status |
|-------|-----|-----|----------|----------|--------|
| golgiBody | (WG: 10.13.37.1) | root | DigitalOcean | NYC 🇺🇸 | **LIVE** — 12.9 RPS |
| golgiLayerHetzner | 2.28.141.35 | root | Hetzner | Falkenstein 🇩🇪 | **LIVE** — 80 req |
| golgiLayerLinode | 172.232.85.202 | **root** | Akamai/Linode | Mumbai 🇮🇳 | **HARDENED** ← provision me |
| golgiLayerOVH | 40.160.96.29 | **debian** (sudo) | OVH | Vint Hill, VA 🇺🇸 | **HARDENED** ← provision me |

---

## Provisioning Instructions

### golgiLayerLinode (Mumbai)

```bash
ssh root@172.232.85.202
# Root password: 7AIvjtQHI02pwLiYCxUUjKzl
# SSH key: eastgate-beardog-v1 authorized
# Already done: hostname set, updated, UFW 22/80/443, fail2ban, /opt/membrane/
# 
# Needs: Caddy, skunky-ingest, scatter server
# DNS: layer3.primals.eco → 172.232.85.202
# Federation: add to plasmid-federation config
```

### golgiLayerOVH (Vint Hill)

```bash
ssh debian@40.160.96.29
# ⚠ USER IS 'debian' NOT 'root' — use sudo for privileged ops
# SSH key: golgiEntry / beardog-v1 authorized  
# Already done: hostname set, updated, UFW 22/80/443, fail2ban, /opt/membrane/
#
# Needs: Caddy, skunky-ingest, scatter server
# DNS: layer4.primals.eco → 40.160.96.29
# Federation: add to plasmid-federation config
#
# Note: This node has 2 vCPU + 4GB RAM — beefier than other layers.
# Could run heavier analysis (local topology computation) if useful.
```

### provision-golgi-layer.sh notes

The OVH node uses `debian` user with sudo. If the provision script assumes root, it needs either:
- `ssh debian@... sudo bash provision-golgi-layer.sh`
- Or add a user detection step at the top of the script

---

## DNS Records Needed

| Subdomain | Type | Value | Purpose |
|-----------|------|-------|---------|
| layer3.primals.eco | A | 172.232.85.202 | Mumbai sensor |
| layer4.primals.eco | A | 40.160.96.29 | Virginia sensor |

Once DNS is pointed and Caddy obtains TLS certs, the Certificate Transparency logs will trigger fleet discovery within 24-48 hours.

---

## Federation Config Update

Add to skunky-ingest federation config on golgiBody:

```rust
LayerEntry {
    name: "golgiLayerLinode".into(),
    url: "http://172.232.85.202:9753/plasmid".into(),  // or via DNS once pointed
    provider: "Akamai/Linode".into(),
    location: "Mumbai, IN".into(),
    jurisdiction: "India (IT Act 2000)".into(),
},
LayerEntry {
    name: "golgiLayerOVH".into(),
    url: "http://40.160.96.29:9753/plasmid".into(),
    provider: "OVH".into(),
    location: "Vint Hill, VA, US".into(),
    jurisdiction: "US federal + Virginia state".into(),
},
```

---

## Overwatch Tool

eastGate now has `overwatch.sh` — the central monitoring system:

```bash
# From eastGate:
cd infra/wateringHole/tools/

./overwatch.sh              # full dashboard
./overwatch.sh primals      # 15 local primals with UDS health
./overwatch.sh mesh         # beehive sensor mesh + plasmid
./overwatch.sh fleet        # entity topology (same as membrane-monitor)
./overwatch.sh gates        # gate liveness (WG, Forgejo, dormant)
./overwatch.sh matrix       # sensor × entity cross-matrix
./overwatch.sh study        # deep analysis (everything combined)
./overwatch.sh watch        # continuous 15s auto-refresh
```

This is distinct from `membrane-monitor.sh` (runs from any gate, public endpoints only). `overwatch.sh` is eastGate-exclusive — it requires local UDS sockets + WireGuard tunnel.

---

## API Tokens Available

For future mesh-provision automation:

| Provider | Token | Capability |
|----------|-------|-----------|
| Linode/Akamai | `mesh-provisioner` (PAT) | Create/destroy Linodes, manage SSH keys |
| OVH | `mesh-provisioner` (AK+AS+CK) | Full VPS API access |

eastGate can spin up new sensor nodes via API in <5 minutes per node.

---

## Active Fleet Observations (from golgiBody, this session)

| Entity | Requests | IPs | Key Finding |
|--------|----------|-----|-------------|
| Anthropic (ClaudeBot) | 18,450 | 1 | Honest, SCATTER only, semi-regular timing |
| Meta Platforms (Fleet) | 3,406 | 56 | **REAL repos only**, blame=32.9%, Chrome/146 (10 behind), METRONOMIC |
| Stealth Scraper | 28 | 8 | Chrome/135 (20 behind), mixed targets |
| Human (Browser) | 20 | 20 | Sec-Fetch PRESENT, varied timing, mixed targets |
| Huawei (PetalBot) | 4 | 3 | Honest bot, sporeprint only |

Meta's fleet is actively mining **author attribution** across all real repos. 32.9% blame rate is not browsing — it's mapping who wrote every line of code.

---

## Timeline

| When | What |
|------|------|
| **Now** | Run provision script on both new nodes |
| **+1h** | DNS pointing + Caddy TLS |
| **+24-48h** | CT log discovery → fleet begins scraping new sensors |
| **+72h** | First cross-matrix data (same behavioral hash across 3+ sensors) |
| **+1 week** | Population analysis with multi-layer corroboration |

---

*Hand back to sporeGate ops. The structure is built. The sensors are listening. The fleet will find them.*

*eastGate overwatch, Wave 165i, Oct 7, 2026*
