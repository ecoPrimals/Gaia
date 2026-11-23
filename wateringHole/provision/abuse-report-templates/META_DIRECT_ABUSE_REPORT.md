# Direct Abuse Report — Meta Platforms, Inc.
# To be filed with Meta's own abuse contact

**To:** domain@fb.com, domain@facebook.com
**CC:** abuse@fb.com
**Subject:** AGPL-3.0-or-later license violation — systematic unauthorized scraping from FB-BLOCK (57.141.0.0/13)

---

## Summary

Your network block **FB-BLOCK** (57.141.0.0/13, registered to Meta Platforms Ireland Limited) is conducting systematic unauthorized scraping of AGPL-3.0-or-later licensed source code hosted at git.primals.eco (Forgejo instance) and associated surfaces.

This is not a security vulnerability report. This is a **license compliance notice**.

## The Violation

### AGPL-3.0-or-later, Section 13

Your systems have extracted source code from the following repositories:
- wateringHole (13.5% of overnight requests)
- toadStool (9.1%)
- bearDog (3.1%)
- songBird (2.8%)
- biomeOS (2.0%)
- And others

All of these repositories are licensed under AGPL-3.0-or-later. Section 13 requires that any entity making the covered work available through a network service must provide the corresponding source of the modified version to users of that service.

**If your systems have used this code in any derivative work, training dataset, or model, the AGPL-3.0-or-later license has been triggered and you must provide corresponding source.**

### Your Infrastructure

65+ IPs from **your own network blocks** — not proxies, not compromised servers — are performing this extraction:

| Block | Registered To | Abuse Contact | IPs Observed |
|---|---|---|---|
| 57.141.0.0/13 | Meta Platforms Ireland Limited | domain@fb.com | 65 |
| 173.252.0.0/16 | Facebook, Inc. | domain@facebook.com | 1 |

### Access Denial

- `robots.txt` at every surface explicitly denies automated access
- 403 responses are returned for detected fleet requests
- Your systems continue scraping after receiving explicit denials
- This constitutes willful unauthorized access under 18 U.S.C. § 1030

### Additional Violations

- **15 U.S.C. § 1125 (Lanham Act)**: Every request impersonates Chrome, Safari, Edge, macOS, Intel, and Windows via fabricated User-Agent strings
- **GDPR**: Automated data collection by Meta Platforms Ireland Limited without legal basis (relevant to EU DPAs)
- **EU AI Act**: Training data provenance requirements for AI systems

## What We Require

1. **Immediate cessation** of unauthorized scraping from FB-BLOCK and FACEBOOK-INC ranges
2. **Audit** of all derivative works, training datasets, and model weights for code extracted from primals.eco infrastructure
3. **AGPL compliance**: Either purge all extracted code from derivative works, or release those works under AGPL-3.0-or-later

## Documentation

All evidence is published, timestamped, and Merkle-anchored:

- **Observatory:** https://signal.primals.eco/
- **Behavioral fingerprint feed:** https://signal.primals.eco/feed/conserved-plasmid.json
- **Evidence library:** https://detroit.primals.eco/

The evidence grows with every request your systems send.

## Timeline

If no response is received within 30 days, this notice — along with all accumulated evidence — will be forwarded to:
- Irish Data Protection Commission (Meta Ireland's supervisory authority)
- French CNIL (if OVH layer is targeted)
- German BfDI (if Hetzner layer is targeted)
- US Copyright Office (DMCA registration)
- Relevant cloud provider abuse desks (DigitalOcean, Hetzner, Vultr, OVH)

---

*Filed by: ecoPrimal*
*Date: [DATE]*
*Reference: signal.primals.eco — sovereign defense observatory*
*License: This notice itself is CC-BY-SA-4.0*
