# Overwatch Handoff — Wave 136a Security Sprint Complete

**Date**: 2026-07-10 22:15 EDT
**From**: primalSpring gate (parallel IDE)
**To**: eastGate overwatch (~/Development/)
**Wave**: 136a → ready for 136b bump

---

## Summary

The Wave 136a security sprint is **complete**. All critical and high-priority
exposure items from the triage matrix are closed. The outer membrane is hardened.
Multiple gates contributed in parallel — this handoff consolidates what landed
so overwatch can bump wave state and plan 136b.

---

## What Landed (since Wave 136a blurb was published)

### sporeGate/golgi — Infrastructure Hardening

| Commit | What |
|--------|------|
| `d84b67f` | CSP on all domains, Caddy JSON access logs, iptables rate limiting (50 conn/10s), wg-key-audit tool (90d rotation policy) |
| `9878b48` | Security headers, 404 fix, fail2ban (already in blurb) |

**Verified live**: CSP, HSTS preload, X-Frame DENY, nosniff, Permissions-Policy, Server stripped, proper 404, H3 alt-svc, gzip — all 5 public domains.

### flockGate — skunkBat + Outer Membrane Validation

| Commit | What |
|--------|------|
| `f9154a8` (skunkBat) | Outer membrane HTTP anomaly detection: `HttpObservation` model, `ThreatType::HttpAnomaly`, `advisory_check_http()`, HTTP metrics subdomain. 553 tests, 0 fail. |
| `e0593a5` (primalSpring) | `s_outer_membrane_posture` scenario — 129 scenarios, 1102 tests, 0 fail |
| WAN validation | All 4 public domains probed and confirmed from remote (flockGate.toml outer_membrane_validation) |

### ironGate — darkforest v3.0

| Commit | What |
|--------|------|
| `d35df65` (projectNUCLEUS) | darkforest v3.0 — TLS + outer membrane pen-testing live |

---

## Exposure Matrix — Final State

```
CLOSED (9/14):
  EXP-01  Security headers           — all domains
  EXP-02  404 catch-all              — proper 404.html
  EXP-03  Cert lifecycle             — Caddy ACME auto-renewal
  EXP-04  Forgejo SSH brute-force    — fail2ban (already banning IPs)
  EXP-05  Depot rate-limiting        — iptables 50 conn/10s
  CSP-01  Content-Security-Policy    — strict static + permissive proxy
  AUDIT-01 Access logs               — JSON, 50MiB roll, 30d
  EXP-07a WireGuard key audit        — tool + 90d policy
  RF-01   Cert renewal drill         — validated

ACCEPTABLE (4/14):
  EXP-08  GitHub trailing shadow
  EXP-09  VPS provider risk
  EXP-10  Registrar (DNSSEC mitigates)
  EXP-11  AI crawlers (intentional)

THEORETICAL (3/14):
  EXP-12  LAN scan (physical access required)
  EXP-13  BTSP RE (ChaCha20 AEAD)
  EXP-14  Dark Forest beacon (zero-metadata)

REMAINING (2 items for 136b+):
  EXP-06  Lab auth-gate (songBird drawbridge auth at Caddy layer)
  SIGN-01 Cascade output signing (ed25519 + BLAKE3)
```

---

## Actions for Overwatch

1. **Bump wave.toml** → `136b` with posture update:
   - "HARDENED. Outer membrane sprint complete (9/14 closed). skunkBat HTTP detection live. darkforest v3.0 active. Remaining: lab auth-gate + cascade signing."

2. **Update eastGate heads** — these are stale:
   - `primalSpring` → `e0593a5` (was `e5d569f`)
   - `skunkBat` → `f9154a8` (was `e7eaa5d`)
   - `wateringHole` → `caa3250` (was `c197f2d`)

3. **Update GLACIAL_SHIFT_READINESS.md** criterion 8:
   - Sub-criteria met: 5/5 for outer membrane (was 3/5)
   - Headers ✓, 404 ✓, fail2ban ✓, CSP ✓, rate-limiting ✓
   - Remaining items (SIGN-01, EXP-06) are defense-in-depth, not stadial blockers

4. **Plan 136b scope** (suggested):
   - SIGN-01: Cascade output signing (cellMembrane ed25519 key, signature alongside binaries)
   - EXP-06: Lab auth-gate (Caddy basic_auth or mTLS on lab.primals.eco)
   - skunkBat ingestion: Wire Caddy JSON logs → `baseline.observe`
   - darkforest: Outer membrane pen-test execution report

5. **Optional**: Publish updated ECOSYSTEM_BLURB.md once wave bump is done

---

## Test Suite Health

| Spring | Tests | Scenarios | Status |
|--------|-------|-----------|--------|
| primalSpring | 1,102 | 129 | GREEN |
| groundSpring | 1,047+ | — | GREEN |
| skunkBat | 553 | — | GREEN |

---

## Key Files to Review

| File | What |
|------|------|
| `handoffs/OUTER_MEMBRANE_HARDENING_AAR_136a.md` | Full AAR with architecture diagram |
| `handoffs/SKUNKBAT_OUTER_MEMBRANE_136a.md` | skunkBat HTTP detection spec |
| `heads/flockGate.toml` | Outer membrane validation results + mesh state |
| `heads/ironGate.toml` | darkforest v3.0 SHA |
| `provision/provision-golgi.sh` | Hardened Caddy config (source of truth) |

---

*primalSpring gate — Wave 136a sprint complete. Handing to overwatch for coordination.*
