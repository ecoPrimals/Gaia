# S1 TLS Graduation Checklist — Cloudflare Removal Sequence

**Authority**: Overwatch  
**Status**: Ready to execute (after DNS NS cutover)  
**Date**: 2026-06-04  
**Prerequisite**: DNS NS registrar cutover COMPLETE, propagation confirmed  
**Protocol**: Calibrate → Shadow → Cutover (per `SOVEREIGNTY_STANDARDS.md`)

---

## Current State

| Metric | Value |
|--------|-------|
| Shadow probes | 198 |
| Failures | 0 |
| p95 latency | < 120ms |
| Caddy version | 2.11.3 on golgiBody-ext (137.184.197.151) |
| LE cert status | Active, auto-renewing |
| Cloudflare status | INACTIVE (proxy still in DNS chain) |
| Graduation gate | p95 < 500ms, 0 TLS failures |

The shadow has run for the full calibration window and passed all thresholds.
S1 is ready for cutover the moment DNS propagation is confirmed.

---

## Pre-Cutover Verification (Operator)

Run from any external machine:

```bash
# 1. Confirm DNS is sovereign (prerequisite)
dig @8.8.8.8 primals.eco NS
# Must return: ns1.primals.eco, ns2.primals.eco

# 2. Confirm Caddy is serving HTTPS
curl -I https://primals.eco --resolve primals.eco:443:137.184.197.151
# Must return HTTP 200 with valid TLS

# 3. Confirm LE certificate is valid
echo | openssl s_client -connect 137.184.197.151:443 -servername primals.eco 2>/dev/null | openssl x509 -noout -dates
# Not After should be > 30 days from now

# 4. Confirm Caddy handles subdomains
curl -I https://git.primals.eco --resolve git.primals.eco:443:137.184.197.151
curl -I https://www.primals.eco --resolve www.primals.eco:443:137.184.197.151
```

---

## Cutover Steps

### Step 1: Set Cloudflare to DNS-Only Mode

**Actor**: Operator

1. Log in to Cloudflare dashboard
2. Navigate to the `primals.eco` zone
3. For EACH proxied DNS record (orange cloud):
   - Click the record
   - Toggle proxy status from "Proxied" (orange cloud) to "DNS only" (gray cloud)
   - This removes Cloudflare from the TLS/HTTP path
4. Key records to change:
   - `primals.eco` A record → DNS only
   - `www.primals.eco` → DNS only
   - `git.primals.eco` → DNS only
   - Any other proxied subdomains

**Why DNS-only first (not delete)**: This is reversible. If something breaks,
re-enable the proxy (orange cloud) to instantly restore Cloudflare TLS.

### Step 2: Verify TLS Is Sovereign

**Actor**: Operator

Wait 5 minutes, then:

```bash
# Verify Caddy is now the TLS terminator (no Cloudflare headers)
curl -vI https://primals.eco 2>&1 | grep -E 'Server:|cf-ray:|CF-'
# Should show "Server: Caddy" and NO cf-ray or CF- headers

# Full TLS chain check
echo | openssl s_client -connect primals.eco:443 -servername primals.eco 2>/dev/null | openssl x509 -noout -issuer
# Should show Let's Encrypt issuer, NOT Cloudflare
```

### Step 3: Start 7-Day Post-Cutover Monitoring

**Actor**: Overwatch (fires FRAGO to cellMembrane)

cellMembrane will run automated monitoring:
- 15-minute probe interval
- HTTPS requests to primals.eco, git.primals.eco, www.primals.eco
- Record: response time, TLS version, certificate issuer, HTTP status
- Alert threshold: any failure, or p95 > 500ms

### Step 4: Monitor for 24h (Critical Window)

**Actor**: Operator

During the first 24h, periodically verify:

```bash
# Quick health check
curl -sI https://primals.eco | head -5
curl -sI https://git.primals.eco | head -5

# Check LE cert renewal isn't blocked
# (Caddy auto-renews, but verify the ACME challenge path works)
curl -s http://primals.eco/.well-known/acme-challenge/test
# 404 is fine — just confirm it reaches Caddy (not Cloudflare)
```

### Step 5: Remove Cloudflare Zone (After 7 Days)

**Actor**: Operator (only after 7-day monitoring completes successfully)

1. In Cloudflare dashboard: remove the `primals.eco` zone entirely
2. This is the point of no return — but by now, sovereign TLS has 7 days of evidence

---

## Rollback Plan

If issues arise during the 24h window:

1. **Immediate** (< 5 min): Re-enable Cloudflare proxy (orange cloud) on affected records
2. **Investigate**: Check Caddy logs on golgiBody-ext: `journalctl -u caddy -f`
3. **Common issues**:
   - LE cert renewal failure: check port 80 is open for ACME HTTP-01 challenge
   - Caddy crash: `systemctl restart caddy`
   - DNS not pointing correctly: verify A records point to 137.184.197.151

---

## After Cutover — What This Achieves

| Glacial Criterion | Status |
|-------------------|--------|
| Criterion 6: Cloudflare removed from production data path | **MET** |

| Sovereignty Track | Before | After |
|-------------------|--------|-------|
| S1 TLS | VERIFIED (shadowing) | **GRADUATED** (sovereign only) |

---

## What This Unblocks

- S3 content cutover (sporePrint can now point to golgiBody-ext without
  Cloudflare in the path)
- Glacial shift criterion 6 is the last Cloudflare dependency

---

## Notify Overwatch

After Step 2 verification succeeds:
1. Overwatch updates `GLACIAL_SHIFT_READINESS.md` — S1 to GRADUATED
2. Overwatch updates `SOVEREIGNTY_STANDARDS.md` — S1 cutover date
3. Overwatch proceeds to S3 content cutover

---

*"198 shadows cast. Zero failures. The proxy goes quiet. The glacier speaks for itself."*
