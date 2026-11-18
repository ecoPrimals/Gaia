# DNS NS Cutover — Operator Checklist

**Authority**: Overwatch  
**Status**: Ready to execute  
**Date**: 2026-06-04  
**Prerequisite**: knot-dns operational on both VPS nodes (confirmed Wave 63+)

---

## Background

Sovereign DNS infrastructure has been live since Wave 63:
- **ns1**: golgiBody ([RELAY_PUBLIC]) — knot-dns primary, DNSSEC active
- **ns2**: golgiBody-ext (137.184.197.151) — knot-dns secondary, zone transfer confirmed

The registrar still points to old nameservers. This checklist switches
the registrar NS records to make sovereign DNS authoritative.

---

## Pre-Cutover Verification

Run these from any machine to confirm sovereign DNS is serving correctly:

```bash
# Verify ns1 responds
dig @[RELAY_PUBLIC] primals.eco SOA
dig @[RELAY_PUBLIC] primals.eco A
dig @[RELAY_PUBLIC] primals.eco NS

# Verify ns2 responds (zone transfer working)
dig @137.184.197.151 primals.eco SOA
dig @137.184.197.151 primals.eco A
dig @137.184.197.151 primals.eco NS

# Verify DNSSEC
dig @[RELAY_PUBLIC] primals.eco DNSKEY
```

All queries should return valid responses. SOA serial should match on both.

---

## Zone Verification (Confirmed 2026-06-04)

The knot-dns zone for `primals.eco` has been verified correct:

| Record | Points To | Correct? |
|--------|-----------|----------|
| `primals.eco` A | 137.184.197.151 (golgiBody-ext / Caddy) | Yes |
| `www.primals.eco` A | 137.184.197.151 | Yes |
| `git.primals.eco` A | [RELAY_PUBLIC] (golgiBody / Forgejo) | Yes |
| `membrane.primals.eco` A | [RELAY_PUBLIC] | Yes |
| `lab.primals.eco` A | [RELAY_PUBLIC] | Yes |
| NS records | ns1 + ns2.primals.eco | Yes |
| Glue | ns1→[RELAY_PUBLIC], ns2→137.184.197.151 | Yes |
| DNSSEC | ECDSA P-256, zone-signed | Yes |
| CAA | letsencrypt.org (issue + issuewild) | Yes |
| SPF | `v=spf1 -all` | Yes |

No GitHub Pages IPs (185.199.x.x) in the zone. Ready for cutover.
Zone transfer to ns2 (golgiBody-ext) confirmed operational.

---

## Cutover Steps (Porkbun)

### Step 1: Log In to Porkbun

Go to [porkbun.com](https://porkbun.com) → Domain Management → `primals.eco`

### Step 2: Change Nameservers

Navigate to: Domain Details → Nameservers → "Authoritative Nameservers"

Switch from Porkbun default nameservers to custom:

| Nameserver | Glue IP |
|-----------|---------|
| `ns1.primals.eco` | [RELAY_PUBLIC] |
| `ns2.primals.eco` | 137.184.197.151 |

Porkbun supports glue records for nameservers under the same domain.
Enter the IPs when prompted.

### Step 3: DNSSEC DS Record

knot-dns has CDS/CDNSKEY records published in the zone. If Porkbun
supports automated DNSSEC via CDS scanning, it may pick them up
automatically. Otherwise:

1. On golgiBody, get the DS record: `keymgr primals.eco ds`
2. In Porkbun → DNSSEC panel → add the DS record
   - Key Tag: 8916
   - Algorithm: 13 (ECDSAP256SHA256)
   - Digest Type: 2 (SHA-256)
   - Digest: (from keymgr output)

If DNSSEC DS is already configured from prior setup, verify it matches.

### Step 4: Save and Confirm

Save the changes. Porkbun typically processes NS changes quickly.
Global propagation takes 24-48h.

---

## Cutover Steps — primal.eco (Inner Membrane)

**Zone status**: LIVE on knot-dns (ns1 + ns2), DNSSEC active, zone transfer confirmed (2026-06-04).

### Step 1: Log In to Porkbun

Go to [porkbun.com](https://porkbun.com) → Domain Management → `primal.eco`

### Step 2: Change Nameservers

Navigate to: Domain Details → Nameservers → Custom

| Nameserver | Glue IP |
|-----------|---------|
| `ns1.primals.eco` | [RELAY_PUBLIC] |
| `ns2.primals.eco` | 137.184.197.151 |

**Note**: These are the same sovereign nameservers as `primals.eco` —
knot-dns serves multiple zones from the same instances.

### Step 3: DNSSEC DS Record

Get the DS record from golgiBody:
```bash
ssh golgi "keymgr primal.eco ds"
```

In Porkbun → DNSSEC panel → add the DS record (Algorithm 13, Digest Type 2).

### Zone Records for Verification

| Record | Type | Points To | Purpose |
|--------|------|-----------|---------|
| `primal.eco` | A | 137.184.197.151 (golgiBody-ext) | Apex — inner membrane TLS |
| `mesh.primal.eco` | A | [RELAY_PUBLIC] (golgiBody) | Songbird mesh |
| `relay.primal.eco` | A | [RELAY_PUBLIC] (peptidoglycan) | TURN relay |
| `auth.primal.eco` | A | [RELAY_PUBLIC] | bearDog BTSP |
| `api.primal.eco` | A | [RELAY_PUBLIC] | biomeOS API |
| `dns.primal.eco` | A | [RELAY_PUBLIC] | DNS management |

---

## Cutover Steps — nestgate.io (Content Layer)

**Zone status**: LIVE on knot-dns (ns1 + ns2), DNSSEC active, zone transfer confirmed (2026-06-04).

### Step 1: Log In to Porkbun

Go to [porkbun.com](https://porkbun.com) → Domain Management → `nestgate.io`

### Step 2: Change Nameservers

Navigate to: Domain Details → Nameservers → Custom

| Nameserver | Glue IP |
|-----------|---------|
| `ns1.primals.eco` | [RELAY_PUBLIC] |
| `ns2.primals.eco` | 137.184.197.151 |

### Step 3: DNSSEC DS Record

Get the DS record from golgiBody:
```bash
ssh golgi "keymgr nestgate.io ds"
```

In Porkbun → DNSSEC panel → add the DS record (Algorithm 13, Digest Type 2).

### Zone Records for Verification

| Record | Type | Points To | Purpose |
|--------|------|-----------|---------|
| `nestgate.io` | A | 137.184.197.151 (golgiBody-ext) | Apex — content layer TLS |
| `www.nestgate.io` | A | 137.184.197.151 | www redirect |

---

## Post-Cutover Verification

Run these checks periodically over 24-48h for each domain that was cut over:

```bash
# primals.eco (outer membrane)
dig @8.8.8.8 primals.eco NS
dig @1.1.1.1 primals.eco A
dig @8.8.8.8 git.primals.eco A

# primal.eco (inner membrane)
dig @8.8.8.8 primal.eco NS
dig @1.1.1.1 primal.eco A
dig @8.8.8.8 mesh.primal.eco A
dig @8.8.8.8 relay.primal.eco A

# nestgate.io (content layer)
dig @8.8.8.8 nestgate.io NS
dig @1.1.1.1 nestgate.io A

# Full chain verification
dig +trace primals.eco A
dig +trace primal.eco A
dig +trace nestgate.io A
```

**Success criteria**: All public resolvers return `ns1.primals.eco` and
`ns2.primals.eco` as authoritative nameservers for all three domains.

**TLS provisioning**: Once DNS resolves to golgiBody-ext for `primal.eco`
and `nestgate.io`, Caddy will auto-provision LE certificates (CAA records
already in place).

---

## Rollback

If something goes wrong:
1. Re-enter the old nameserver records in the registrar
2. Wait for propagation (24-48h)
3. Investigate the issue on golgiBody/golgiBody-ext

The old NS records are the fallback. knot-dns does not need to be stopped —
it continues serving regardless of registrar state.

---

## What This Unblocks

| Item | Depends On | Domain |
|------|-----------|--------|
| S1 TLS graduation (inner membrane sovereign TLS) | `primal.eco` DNS confirmed | `primal.eco` |
| S3 content cutover (sporePrint sovereign) | `primals.eco` DNS confirmed | `primals.eco` |
| S5 DNS graduation (inner membrane sovereign DNS) | `primal.eco` + `nestgate.io` DNS confirmed | Both |
| Glacial shift criterion 5 (sovereign DNS) | All 3 domains on sovereign NS | All |
| Glacial shift criterion 6 (cross-membrane validation) | Both membranes resolvable | `primal.eco` + `primals.eco` |
| Content layer operational (`nestgate.io`) | `nestgate.io` DNS confirmed | `nestgate.io` |

---

## After Cutover — Notify Overwatch

Once DNS propagation is confirmed (24-48h), notify overwatch to:
1. Update `GLACIAL_SHIFT_READINESS.md` — criterion 5 met
2. Proceed with S1 TLS graduation (`S1_TLS_GRADUATION_CHECKLIST.md`)
3. Proceed with S3 content cutover

---

*"Two nameservers. One registrar change. The domain comes home."*
