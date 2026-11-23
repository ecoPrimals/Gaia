# Abuse Report — Hetzner Online GmbH
# Template for fleet activity observed on Hetzner infrastructure

**To:** abuse@hetzner.com
**Subject:** Unauthorized automated scraping from Meta Platforms infrastructure targeting Hetzner-hosted service

---

## Summary

I am reporting unauthorized automated scraping activity targeting my server hosted on Hetzner infrastructure. The scraping fleet is operated by **Meta Platforms, Inc.** (confirmed via WHOIS: FB-BLOCK, 57.141.0.0/13, registered to Meta Platforms Ireland Limited). The activity violates:

1. **Hetzner Terms of Service** — Section 3 (Obligations of the Customer / Prohibited Activities)
2. **German Criminal Code (StGB) §202a** — Unauthorized access to data
3. **EU General Data Protection Regulation (GDPR)** — Automated data collection without legal basis
4. **robots.txt** — Explicit access denial, read and violated

## Server Details

- **Hetzner Server IP:** [LAYER_IP]
- **Hostname:** [LAYER_DOMAIN]
- **Account:** [HETZNER_ACCOUNT]

## Attacking Infrastructure

| Network Block | Registration | WHOIS Entity |
|---|---|---|
| 57.141.0.0/13 | FB-BLOCK | Meta Platforms Ireland Limited |
| 173.252.0.0/16 | FACEBOOK-INC | Facebook, Inc. (Menlo Park, CA) |

## Evidence

### Access Denial

- `robots.txt` is published at `https://[LAYER_DOMAIN]/robots.txt` and contains:
  ```
  User-agent: *
  Disallow: /
  ```
- The fleet reads robots.txt and continues scraping — willful violation of access controls.

### Request Characteristics

- **Requests per hour:** [INSERT_COUNT]
- **Timing pattern:** 100ms metronomic intervals (99.3% of requests at 0.0-0.1s)
- **User-Agent:** Claims Chrome/150 but missing mandatory Chrome headers (Sec-Fetch-Mode, Sec-Ch-Ua)
- **Header count:** 3 headers per request (Chrome sends 11+)
- **Content targeted:** Source code from AGPL-3.0-or-later licensed repositories

### Behavioral Fingerprint

Published at: https://signal.primals.eco/feed/conserved-plasmid.json

Six conserved behavioral signatures confirm this is automated scraping infrastructure, not browsing:
1. `header_poverty` — Missing mandatory browser headers (100% of fleet)
2. `stale_chrome` — Hardcoded outdated Chrome version (100%)
3. `connection_absent` — No Connection header (100%)
4. `content_gate` — >50% requests target source code paths (99%)
5. `accept_monoculture` — Universal `*/*` Accept header (89%)
6. `blame_ratio` — >10% requests target /blame/ paths for author attribution (67%)

### AGPL License Violation

All content on the server is licensed under AGPL-3.0-or-later. The scraping fleet extracts source code without providing corresponding source to downstream users as required by AGPL Section 13. This constitutes a copyright violation.

## Requested Action

1. Confirm receipt of this report
2. Investigate the traffic from the reported IP ranges
3. Note that this traffic originates from Meta Platforms' own registered network blocks — this is not a compromised server, this is corporate infrastructure engaged in systematic unauthorized access

## Full Documentation

The complete evidence observatory is published at:
- **Observatory:** https://signal.primals.eco/
- **Threat feed:** https://signal.primals.eco/feed/conserved-plasmid.json
- **Evidence library:** https://detroit.primals.eco/

This evidence is Merkle-anchored and timestamped.

---

*Filed by: ecoPrimal*
*Date: [DATE]*
*Reference: signal.primals.eco observation layer [LAYER_NAME]*
