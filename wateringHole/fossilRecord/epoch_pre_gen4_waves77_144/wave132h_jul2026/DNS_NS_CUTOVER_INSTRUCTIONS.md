# DNS NS Cutover — primals.eco to Sovereign Nameservers

**Status**: READY TO EXECUTE
**Date prepared**: May 31, 2026
**Prepared by**: eastGate (overwatch)

## Current State

| Item | Current | Target |
|------|---------|--------|
| NS delegation | samara.ns.cloudflare.com, albert.ns.cloudflare.com | ns1.primals.eco, ns2.primals.eco |
| Primary NS | Cloudflare | golgiBody-inner ([RELAY_PUBLIC]) |
| Secondary NS | Cloudflare | golgiBody-ext (137.184.197.151) |
| DNSSEC | Unknown (Cloudflare-managed) | ECDSA P-256 (Algorithm 13), self-signed |

## Infrastructure Validated

- `ns1.primals.eco` ([RELAY_PUBLIC]) — knot-dns 3.2.6, primary, DNSSEC active
- `ns2.primals.eco` (137.184.197.151) — knot-dns 3.2.6, secondary, zone transfer confirmed (serial 2026052213)
- Zone includes: membrane.primals.eco, lab.primals.eco, git.primals.eco, ns1, ns2
- Apex A records point to GitHub Pages (185.199.108-111.153) — intentional extracellular weak bond
- CAA restricts certificate issuance to letsencrypt.org only
- Firewall port 53 TCP/UDP open on both NS servers

## Registrar Action Required

### Step 1: Change Nameservers

In your domain registrar control panel for `primals.eco`:

1. Remove existing nameservers:
   - `samara.ns.cloudflare.com`
   - `albert.ns.cloudflare.com`

2. Add sovereign nameservers:
   - `ns1.primals.eco` — glue IP: `[RELAY_PUBLIC]`
   - `ns2.primals.eco` — glue IP: `137.184.197.151`

Note: Since the nameservers are under the same domain, you MUST set glue records
(child nameserver IP addresses) at the registrar. Most registrar UIs have a
"Child Nameservers" or "Glue Records" section for this.

### Step 2: Add DS Record (DNSSEC)

Add this DS record at the registrar to chain DNSSEC to the parent `.eco` zone:

```
Key Tag:    8916
Algorithm:  13 (ECDSAP256SHA256)
Digest Type: 2 (SHA-256)
Digest:     2DDC6F7D3F7BA931BB080DD5D5B97550043CF71AB0455128C5A66E3E8699F7DA
```

### Step 3: Verify (after TTL propagation, ~24-48h)

```bash
# From any machine with dig installed:
dig NS primals.eco +short
# Expected: ns1.primals.eco. ns2.primals.eco.

dig A membrane.primals.eco +short
# Expected: [RELAY_PUBLIC]

dig A primals.eco +short
# Expected: 185.199.108.153 (GitHub Pages, intentional)
```

## Risk Assessment

- **Propagation delay**: 24-48h for NS changes to fully propagate
- **Rollback**: If issues, change NS back to Cloudflare at registrar
- **DNSSEC risk**: If DS record is wrong, domain becomes SERVFAIL. Only add DS after NS is working.
- **Recommended order**: Set NS + glue first, verify resolution works, THEN add DS record

## Post-Cutover

Once NS cutover is verified:
- Let's Encrypt can issue certs via DNS-01 challenge (CAA already set)
- golgiBody-ext can serve HTTPS for lab.primals.eco, sporePrint
- Cloudflare is fully removed from the DNS path
- GitHub Pages continues to serve apex (intentional extracellular weak bond)
