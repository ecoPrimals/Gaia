# Formal Notice of License Violation and Unauthorized Access
# From ecoPrimal to Meta Platforms, Inc.

---

**From:** ecoPrimal <ecoPrimal@pm.me>

**To (one per line for copy-paste):**

```
domain@fb.com
domain@facebook.com
abuse@fb.com
```

**CC — Meta Legal (one per line):**

```
opensource@fb.com
ip@fb.com
legal@meta.com
```

**CC — Regulatory & Enforcement:**

```
info@dpc.ie
international@cnil.fr
poststelle@bfdi.bund.de
complaints@ico.org.uk
FTCcomplaint@ftc.gov
copyright@copyright.gov
```

**CC — License Enforcement:**

```
licensing@fsf.org
legal@sfconservancy.org
legal@eff.org
info@openinventionnetwork.com
```

**CC — Industry:**

```
abuse@cloudflare.com
abuse@digitalocean.com
security@github.com
abuse@abuseipdb.com
```

**All CC addresses (single block for paste):**

```
opensource@fb.com, ip@fb.com, legal@meta.com, info@dpc.ie, international@cnil.fr, poststelle@bfdi.bund.de, complaints@ico.org.uk, FTCcomplaint@ftc.gov, copyright@copyright.gov, licensing@fsf.org, legal@sfconservancy.org, legal@eff.org, info@openinventionnetwork.com, abuse@cloudflare.com, abuse@digitalocean.com, security@github.com, abuse@abuseipdb.com
```

**Subject:** Formal Notice: AGPL-3.0-or-later License Violation, Unauthorized Access, and Trademark Impersonation — FB-BLOCK (57.141.0.0/13) Fleet Activity Against primals.eco Infrastructure

**Date:** October 7, 2026

---

## I. Identity of the Notifying Party

ecoPrimal is a sovereign research ecosystem publishing open-source software, scientific methodology, and public interest journalism under the **scyBorg triple license**:

- **Code:** AGPL-3.0-or-later (enforced by the Free Software Foundation)
- **Mechanics/Designs:** ORC License (Open RPG Creative License)
- **Documentation/Science:** CC-BY-SA-4.0 (Creative Commons Attribution-ShareAlike)

Infrastructure: git.primals.eco (Forgejo sovereign code forge), sporeprint.primals.eco (research catalogue), detroit.primals.eco (public interest investigation), and associated surfaces.

All source code is publicly available, properly licensed, and served with robots.txt access controls.

---

## II. Identity of the Infringing Party

**Meta Platforms, Inc.** (formerly Facebook, Inc.)
1 Hacker Way, Menlo Park, CA 94025

Operating through:

**Meta Platforms Ireland Limited**
4 Grand Canal Square, Grand Canal Harbour, Dublin 2, Ireland

Confirmed via WHOIS:

| Network Block | Registration | WHOIS Entity | Abuse Contact |
|---|---|---|---|
| **57.141.0.0/13** | FB-BLOCK | Meta Platforms Ireland Limited | domain@fb.com |
| **173.252.0.0/16** | FACEBOOK-INC | Facebook, Inc. | domain@facebook.com |

These are Meta's own registered network blocks, maintained by Meta's own network engineering team (`facebook-neteng`). This is not third-party or compromised infrastructure.

---

## III. Duration and Scale of Violation

| Metric | Value |
|--------|-------|
| **Observation period** | October 5-7, 2026 (1.6 days of logged evidence) |
| **Total fleet requests** | 88,751 |
| **Unique fleet IPs** | 292 (growing — was 152 on Oct 5) |
| **Direct Meta IPs** | 66 (43% of fleet from FB-BLOCK and FACEBOOK-INC) |
| **Data consumed** | 1.15 GB |
| **Peak velocity** | 7,266 requests/hour (121/min) |
| **Request timing** | 100ms metronomic intervals (99.3% at 0.0-0.1s) |
| **robots.txt compliance** | Zero — read and violated |
| **403 responses honored** | Zero — scraping continues after explicit denial |
| **Behavioral subgroups** | 47 distinct scraping configurations |
| **Countries involved** | 13+ (residential proxy rotation) |
| **Real code obtained** | 0 bytes (defensive systems serve fabricated content) |

The fleet is **accelerating**: 157 requests on day 1, 18,261 on day 2, 70,333 on day 3.

---

## IV. Laws and Licenses Violated

### A. Copyright / License Violations

| License/Statute | Violation | Evidence |
|---|---|---|
| **AGPL-3.0-or-later, Section 13** | Source code extracted via network access without providing corresponding source to downstream users | 88,751 requests targeting `/commit/`, `/src/`, `/raw/`, `/blame/` paths on git.primals.eco |
| **AGPL-3.0-or-later, Section 5** | Modified or derivative works not released under AGPL | If extracted code was used in LLaMA or any Meta AI system, the derivative work must be AGPL-licensed |
| **ORC License** | Mechanics and system designs extracted without ORC compliance | wateringHole repository (13.5% of fleet requests) contains licensed game mechanics and system designs |
| **CC-BY-SA-4.0** | Documentation extracted without attribution or share-alike | sporePrint content, methodology papers, and science publications are CC-BY-SA-4.0 |
| **17 U.S.C. § 1202 (DMCA)** | Circumventing copyright management information | License headers present in every file; extracted without compliance |

### B. Computer Fraud / Unauthorized Access

| Statute | Jurisdiction | Violation |
|---|---|---|
| **18 U.S.C. § 1030 (CFAA)** | United States | Exceeding authorized access after explicit denial via robots.txt and 403 responses |
| **StGB § 202a** | Germany | Unauthorized access to data (Ausspähen von Daten) — if Hetzner layer is targeted |
| **Code pénal Art. 323-1** | France | Fraudulent access to an automated data processing system — if OVH layer is targeted |
| **Cybersecurity Law 2018** | Vietnam | Residential ISP connections used as unauthorized proxies |
| **PECA 2016** | Pakistan | Residential broadband exploited for proxy routing |
| **Criminal Code Art. 278** | Uzbekistan | ISP traffic redirected without authorization |
| **Criminal Code Art. 205** | Kazakhstan | Hosting infrastructure misused |
| **Criminal Code Art. 361** | Ukraine | Data center connections exploited |

### C. Trademark Impersonation

| Statute | Violation | Evidence |
|---|---|---|
| **15 U.S.C. § 1125 (Lanham Act)** | False designation of origin | Every request contains 6 trademarked product names: Chrome™, Safari™, Edge™, macOS™, Intel™, Windows™ — none of which are the actual client |

### D. Data Protection

| Framework | Violation | Entity |
|---|---|---|
| **GDPR Art. 5** | Automated data collection without legal basis | Meta Platforms Ireland Limited (Irish entity) |
| **GDPR Art. 6** | No lawful basis for processing | Scraping without consent, contract, or legitimate interest |
| **EU AI Act** | Training data provenance requirements | If data feeds AI training, provenance obligations apply |
| **DMA Art. 5** | Fairness obligations for designated gatekeepers | Meta Platforms, Inc. is a designated gatekeeper |
| **Irish Data Protection Act 2018** | Data processing violations by Irish-registered entity | Meta Platforms Ireland Limited |

---

## V. Behavioral Evidence Summary

The fleet exhibits six **conserved behavioral epitopes** — signatures that cannot change without replacing the scraping toolkit entirely:

1. **`header_poverty`** (100% of fleet): Missing `Sec-Fetch-Mode` header — mandatory in Chrome since 2019
2. **`stale_chrome`** (100%): Chrome/150 User-Agent string — current stable is Chrome/155
3. **`connection_absent`** (100%): No `Connection: keep-alive` header — Chrome always sends this
4. **`content_gate`** (99%): >50% of requests target `/commit/`, `/src/`, `/raw/`, `/blame/` paths
5. **`accept_monoculture`** (89%): Universal `*/*` Accept header — browsers vary by resource type
6. **`blame_ratio`** (67%): >10% of requests target `/blame/` paths — **author attribution mining**

The `blame_ratio` epitope is particularly significant: 67% of fleet subgroups systematically scrape `/blame/` endpoints, which show who last modified each line of code. This is author attribution mining at scale — mapping authorship for use in training data pipelines.

---

## VI. What We Require

1. **Immediate cessation** of all unauthorized scraping from FB-BLOCK (57.141.0.0/13), FACEBOOK-INC (173.252.0.0/16), and all associated proxy infrastructure.

2. **AGPL compliance audit**: Identify all derivative works, training datasets, model weights, and internal tools that contain or were influenced by code extracted from primals.eco infrastructure. Either:
   - (a) Purge all extracted material and provide auditable proof; **or**
   - (b) Release all derivative works under AGPL-3.0-or-later, as the license requires.

3. **Written confirmation** within 30 days that the above actions have been taken.

---

## VII. Evidence Repository

All evidence is published, timestamped, and Merkle-anchored:

| Resource | URL |
|----------|-----|
| **Live observatory** | https://signal.primals.eco/ |
| **Machine-readable threat feed** | https://signal.primals.eco/feed/conserved-plasmid.json |
| **Per-layer plasmid (real-time)** | https://signal.primals.eco/plasmid |
| **Evidence library** | https://detroit.primals.eco/ |
| **Source code (verify license)** | https://git.primals.eco/ |
| **scyBorg license documentation** | https://sporeprint.primals.eco/methodology/scyborg-licensing/ |

The evidence grows with every request your systems send. This notice and all accumulated evidence will be updated and republished as the fleet's activity continues.

---

## VIII. Notice

This communication constitutes formal notice under:
- DMCA § 512(c) (notification of claimed infringement)
- AGPL-3.0-or-later § 8 (termination upon violation — license rights terminate automatically)
- GDPR Art. 77 (right to lodge a complaint with a supervisory authority)

Per AGPL-3.0-or-later Section 8: Meta's rights under this license **terminated automatically** upon the first act of non-compliance. Reinstatement requires cure of the violation within 30 days of notification, per Section 8 paragraph 2.

**This email constitutes that notification. The 30-day clock starts today.**

---

*ecoPrimal — Beside the small. Against unaccountable power. For the record.*

*This notice is licensed CC-BY-SA-4.0. You may share and adapt it with attribution.*
*This notice is published at: https://signal.primals.eco/*
