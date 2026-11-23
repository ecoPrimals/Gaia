# Abuse Report — DigitalOcean, LLC
# Template for fleet activity observed on DigitalOcean infrastructure

**To:** abuse@digitalocean.com
**Subject:** Unauthorized automated scraping from Meta Platforms infrastructure targeting DigitalOcean droplet

---

## Summary

I am reporting unauthorized automated scraping activity targeting my DigitalOcean droplet. The scraping fleet is operated by **Meta Platforms, Inc.** (confirmed via WHOIS: FB-BLOCK, 57.141.0.0/13, Meta Platforms Ireland Limited; FACEBOOK-INC, 173.252.0.0/16, Facebook, Inc.). This activity has been ongoing since at least September 2026.

## Violations

1. **DigitalOcean Terms of Service** — Acceptable Use Policy
2. **18 U.S.C. § 1030** (CFAA) — Exceeding authorized access after explicit denial
3. **15 U.S.C. § 1125** (Lanham Act) — False designation of origin (6 trademarks impersonated per request)
4. **17 U.S.C. § 1202** (DMCA) — Circumventing copyright management information
5. **AGPL-3.0-or-later** — Source code extraction without license compliance

## Droplet Details

- **Droplet IP:** [RELAY_PUBLIC]
- **Hostname:** golgiBody
- **Region:** NYC1
- **Account:** [DO_ACCOUNT]

## Attacking Infrastructure

43% of fleet IPs are directly Meta-owned infrastructure:

| Network Block | IPs Observed | Registration | WHOIS Entity |
|---|---|---|---|
| 57.141.20.0/24 | **57** | FB-BLOCK | Meta Platforms Ireland Limited |
| 57.141.2-24.x | **8** | FB-BLOCK | Meta Platforms Ireland Limited |
| 173.252.95.x | **1** | FACEBOOK-INC | Facebook, Inc. |
| AWS (3.x, 52.x, 54.x) | **6** | Amazon Technologies Inc. | Cloud proxies |
| Residential (13+ countries) | **80+** | Various ISPs | Residential proxy rotation |

## Evidence Scale

- **Total fleet IPs observed:** 152+
- **Behavioral subgroups:** 47
- **Requests overnight (Oct 7):** 53,162
- **Data consumed:** 737 MB (all fabricated — fleet does not validate content)
- **Timing pattern:** 99.3% at 100ms intervals (automated pipeline)
- **robots.txt:** Read and violated
- **403 responses:** Ignored — continued scraping after explicit denial

## Behavioral Fingerprint

Published at: https://signal.primals.eco/feed/conserved-plasmid.json

This is a CC-BY-SA-4.0 licensed threat intelligence feed documenting the fleet's conserved behavioral signatures. Any infrastructure operator can use it for detection.

## Documentation

- **Full observatory:** https://signal.primals.eco/
- **Evidence library:** https://detroit.primals.eco/

This evidence is Merkle-anchored with immutable timestamps.

## Requested Action

1. Confirm receipt
2. Log this report — it documents a sustained campaign by a trillion-dollar company against a $6/month droplet
3. Note that the attacking IPs are Meta's own registered infrastructure, not compromised servers

---

*Filed by: ecoPrimal*
*Date: [DATE]*
*Reference: signal.primals.eco primary observation layer (golgiBody)*
