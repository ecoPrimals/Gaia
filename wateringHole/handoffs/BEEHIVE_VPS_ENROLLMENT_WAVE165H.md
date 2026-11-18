# Beehive — Multi-VPS Observation Mesh Enrollment
# Wave 165h — October 7, 2026

**Status:** ACTIVE — accounts created, VPS enrollment in progress
**Owner:** ecoPrimal (enrollment) + overwatch on eastGate (provisioning assist)
**Biological Analog:** Beehive — each comb is an observation layer, each cell a honeycomb surface

---

## CONTEXT

The fleet has been observed for 1.6 days. In that time:

- **88,751 requests** from **292 unique IPs** across **47 behavioral subgroups**
- **1.15 GB** of fabricated content consumed (zero real code obtained)
- Fleet is **accelerating**: 157 → 18,261 → 70,333 requests per day
- **43% of IPs** trace directly to Meta-owned infrastructure (FB-BLOCK, FACEBOOK-INC)
- Fleet uses residential proxies across **13+ countries** (VN, PK, UZ, KZ, UA, ES, MX, BR, EC, NG, CO)

A single $6/month VPS has cost them ~$434 in wasted effort (1,391:1 ratio).

The beehive multiplies that: more layers = more observation points = more jurisdictions = more evidence = more cost to them for zero return.

---

## WHAT THE BEEHIVE IS

```
             Internet
                │
    ┌───────────┼───────────────────────────────┐
    │           │           │         │          │
golgiBody   golgiLayer2  golgiLayer3  golgiLayer4  golgiLayer5
  (DO NYC)   (Hetzner DE) (Vultr SG) (OVH FR)   (Linode JP/IN)
    │           │           │         │          │
    └───────────┼───────────────────────────────┘
                │
         Plasmid Federation
                │
    signal.primals.eco/feed/conserved-plasmid.json
```

Each layer runs:
- **Caddy** (TLS, fleet detection, scatter routing)
- **skunky-ingest** (log tailer, behavioral classification, scatter server)
- **12 honeycomb surfaces** per layer (bloom, thymus, opsonize, antibody, cytokine, receptor, macrophage, lysozyme, complement, epitope, antigen, interferon)
- **Plasmid export** (`/plasmid` endpoint for federation)
- **robots.txt** (explicit denial — creates evidence when fleet ignores it)

All code is already built and tested. Provision script is ready. Just needs IPs.

---

## ACCOUNTS CREATED (4 providers)

| Provider | Account Status | Region Target | Monthly Cost | Jurisdiction |
|----------|---------------|---------------|-------------|-------------|
| **Hetzner** | Created | Falkenstein, DE | ~€3.79 | German StGB §202a + GDPR |
| **Vultr** | Created | Singapore | ~$5.00 | Singapore PDPA |
| **OVH** | Created | Gravelines, FR | ~€3.50 | French law + CNIL |
| **Linode/Akamai** | Created | Mumbai or Tokyo | ~$5.00 | India IT Act / Japan APPI |

**Total additional cost:** ~$17-18/month (well within $50-100 budget)

---

## ENROLLMENT CHECKLIST — overwatch on eastGate

For each provider, create ONE VPS with these specs:

### Common Specs (all 4 layers)

- **OS:** Debian 12 (bookworm)
- **Tier:** Cheapest available (1 vCPU, 1-2GB RAM, 10-40GB disk)
- **SSH:** Add sporeGate SSH pubkey during creation if possible
- **Root access:** Needed for provisioning (SSH key or password)

### Per-Provider Steps

#### 1. Hetzner (golgiLayer2)

1. Go to [console.hetzner.cloud](https://console.hetzner.cloud)
2. New Project → "beehive" (or add server to default)
3. Create Server:
   - Location: **Falkenstein (FSN1)**
   - Image: Debian 12
   - Type: **CX22** (2 vCPU, 4GB) or cheapest available
   - SSH Key: paste sporeGate pubkey
   - Name: `golgiLayer2`
4. Record: **IP address** → paste below

#### 2. Vultr (golgiLayer3)

1. Go to [my.vultr.com](https://my.vultr.com)
2. Deploy New Server:
   - Type: Cloud Compute → Regular Performance
   - Location: **Singapore**
   - Image: Debian 12
   - Size: 1 vCPU, 1GB RAM ($5/mo)
   - SSH Key: paste sporeGate pubkey
   - Label: `golgiLayer3`
3. Record: **IP address** → paste below

#### 3. OVH (golgiLayer4)

1. Go to [ovhcloud.com control panel](https://www.ovh.com/manager/)
2. Order → VPS:
   - Model: **Starter** (cheapest)
   - Datacenter: **Gravelines (GRA)**
   - OS: Debian 12
   - SSH Key: paste sporeGate pubkey
3. Record: **IP address** → paste below

#### 4. Linode/Akamai (golgiLayer5)

1. Go to [cloud.linode.com](https://cloud.linode.com)
2. Create Linode:
   - Image: Debian 12
   - Region: **Mumbai** (ap-south) or **Tokyo 2** (ap-northeast)
   - Plan: Nanode 1GB ($5/mo)
   - Root Password or SSH Key
   - Label: `golgiLayer5`
3. Record: **IP address** → paste below

---

## IP REGISTRY (fill in as VPS come online)

| Layer | Provider | Region | IP Address | SSH Verified | Status |
|-------|----------|--------|------------|-------------|--------|
| golgiBody | DigitalOcean | NYC | [RELAY_PUBLIC] | ✓ | ACTIVE |
| golgiLayer2 | Hetzner | Falkenstein DE | _________________ | ☐ | PENDING |
| golgiLayer3 | Vultr | Singapore | _________________ | ☐ | PENDING |
| golgiLayer4 | OVH | Gravelines FR | _________________ | ☐ | PENDING |
| golgiLayer5 | Linode | Mumbai/Tokyo | _________________ | ☐ | PENDING |

---

## AFTER IPS ARE RECORDED

Hand this document back. The provisioning pipeline is:

1. **SSH verify** — confirm root access from sporeGate to each IP
2. **Run provision script** — `provision-golgi-layer.sh` (already written, tested)
3. **Cross-compile skunky-ingest** — build on sporeGate, SCP to each layer
4. **Add Cloudflare DNS** — A records for layer2/3/4/5.primals.eco
5. **Verify TLS** — Caddy auto-obtains Let's Encrypt certs
6. **Verify plasmid export** — `curl https://layerN.primals.eco/plasmid`
7. **Wait for fleet** — CT logs + cross-links bring the fleet within 24-48 hours
8. **Federation cron** — already running on golgiBody every 5 minutes

Estimated time per layer: **10-15 minutes** once IP is available.

---

## CLOUDFLARE DNS PLAN

All layers use primals.eco subdomains via Cloudflare:

| Subdomain | Target IP | Proxy Mode | Why |
|-----------|-----------|-----------|-----|
| `layer2.primals.eco` | Hetzner IP | Grey cloud (DNS only) | Raw traffic for maximum signal |
| `layer3.primals.eco` | Vultr IP | Grey cloud (DNS only) | Raw traffic, Asian vantage point |
| `layer4.primals.eco` | OVH IP | **Orange cloud (Proxied)** | CF sees fleet traffic, learns fingerprints |
| `layer5.primals.eco` | Linode IP | Grey cloud (DNS only) | Raw traffic, second Asian vantage |

One layer (OVH/France) goes through Cloudflare orange cloud so CF's own bot detection sees the fleet firsthand. If CF blocks them: that's evidence. If CF passes them: CF can learn from the published plasmid feed.

---

## WHAT'S ALREADY BUILT (ready to deploy)

| Component | Location | Status |
|-----------|----------|--------|
| `provision-golgi-layer.sh` | `wateringHole/provision/` | Tested, ready |
| `plasmid-federation.sh` | `wateringHole/provision/` + deployed on golgiBody | Running (cron */5) |
| `/plasmid` endpoint | `scatter_server.rs` | Deployed on golgiBody, verified live |
| Signal observatory | `signal.primals.eco` | Updated with observation network section |
| Abuse report templates | `wateringHole/provision/abuse-report-templates/` | 5 templates (Hetzner, Vultr, OVH, DO, Meta direct) |
| Formal notice email | Same directory | Ready, pre-published on signal page |
| Conserved plasmid feed | `signal.primals.eco/feed/conserved-plasmid.json` | Live, CC-BY-SA-4.0 |

---

## LEGAL TIMELINE

| Step | Status | Date |
|------|--------|------|
| Evidence documented on signal.primals.eco | **Published** | Oct 7, 2026 |
| Behavioral fingerprint feed published | **Live** | Oct 7, 2026 |
| Formal notice pre-published on signal page | **Published** | Oct 7, 2026 |
| Beehive VPS mesh deployed | **In progress** | Oct 7, 2026 |
| Fleet observed from multiple vantage points | Pending | — |
| Formal notice transmitted to Meta | Pending | After beehive data collected |
| 30-day AGPL §8 cure clock starts | Pending | On transmission |

**Strategy:** Publish everything first. Let the beehive collect multi-jurisdiction evidence. Then send the formal notice with the FSF, CNIL, and Irish DPC CC'd. The publication timestamps predate the complaint by days or weeks. This is documentation, not entrapment.

---

## SECURITY BOUNDARY

- **wateringHole** (this doc) — PUBLIC. Shows our moves. Design, architecture, legal strategy.
- **whitePaper subGen** — PRIVATE. PII, science, internal analysis, specific IP addresses.
- **signal.primals.eco** — PUBLIC. Evidence observatory, fingerprint feed, formal notice.

No PII in this document. No specific fleet IPs. No internal analysis. Just the architecture and enrollment checklist.

---

*Wave 165h — the beehive grows. Each comb is a jurisdiction. Each cell is a honeycomb surface. The fleet enters and finds rooms that weren't there before. House of leaves.*
