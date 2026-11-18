# Abuse Report — Vultr (The Constant Company, LLC)
# Template for fleet activity observed on Vultr infrastructure

**To:** abuse@vultr.com
**Subject:** Unauthorized automated scraping from Meta Platforms infrastructure targeting Vultr-hosted service

---

## Summary

I am reporting unauthorized automated scraping activity targeting my Vultr instance. The scraping fleet is operated by **Meta Platforms, Inc.** (confirmed via WHOIS: FB-BLOCK, 57.141.0.0/13, registered to Meta Platforms Ireland Limited). The fleet uses residential proxies and cloud infrastructure to rotate IPs while maintaining a consistent behavioral fingerprint.

## Violations

1. **Vultr Terms of Service** — Section 6 (Acceptable Use Policy): Unauthorized access
2. **18 U.S.C. § 1030** (Computer Fraud and Abuse Act) — Exceeding authorized access
3. **15 U.S.C. § 1125** (Lanham Act) — False designation of origin via trademark impersonation
4. **AGPL-3.0-or-later license** — Copyright violation (source code extraction without compliance)
5. **robots.txt** — Explicit access denial, read and violated

## Server Details

- **Vultr Instance IP:** [LAYER_IP]
- **Hostname:** [LAYER_DOMAIN]
- **Region:** [VULTR_REGION]
- **Account:** [VULTR_ACCOUNT]

## Attacking Infrastructure

The fleet operates from Meta's own registered network blocks:

| Network Block | Registration | WHOIS Entity | Abuse Contact |
|---|---|---|---|
| 57.141.0.0/13 | FB-BLOCK | Meta Platforms Ireland Limited | domain@fb.com |
| 173.252.0.0/16 | FACEBOOK-INC | Facebook, Inc. | domain@facebook.com |

Additionally, some fleet traffic routes through cloud providers (AWS, HPE) and residential proxy services across 13+ countries.

## Evidence

### Behavioral Fingerprint

The fleet exhibits six conserved behavioral signatures that identify it as automated scraping infrastructure:

1. Claims to be Chrome but missing mandatory browser headers
2. Hardcoded outdated Chrome version (150 vs current stable 155)
3. 100ms metronomic request timing (coefficient of variation < 0.1)
4. Zero static asset loading (reads HTML only — never loads CSS, JS, images)
5. Over 50% of requests target source code extraction paths
6. 67% of subgroups mine `/blame/` paths for author attribution

Full behavioral fingerprint published at:
https://signal.primals.eco/feed/conserved-plasmid.json

### Request Volume

- **Requests observed:** [INSERT_COUNT]
- **Time period:** [INSERT_PERIOD]
- **Data consumed:** [INSERT_MB] MB (all fabricated content — fleet does not validate)

### robots.txt Violation

```
User-agent: *
Disallow: /
```

Published at `https://[LAYER_DOMAIN]/robots.txt`. Fleet reads and ignores.

## Requested Action

1. Acknowledge receipt
2. Log this report for the record
3. Note: the attacking IPs are Meta Platforms' own registered infrastructure, not compromised third-party servers

## Full Documentation

- **Observatory:** https://signal.primals.eco/
- **Threat intelligence feed:** https://signal.primals.eco/feed/conserved-plasmid.json
- **Evidence library:** https://detroit.primals.eco/

---

*Filed by: ecoPrimal*
*Date: [DATE]*
*Reference: signal.primals.eco observation layer [LAYER_NAME]*
