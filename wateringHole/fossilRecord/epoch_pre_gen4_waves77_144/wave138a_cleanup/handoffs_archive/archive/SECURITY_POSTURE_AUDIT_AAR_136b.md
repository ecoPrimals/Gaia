# Security Posture Audit AAR — Wave 136b

**Date**: 2026-07-11
**Scope**: Full outer membrane security posture review and remediation
on golgi, following live threat data discovery.

---

## Audit Summary

| Severity | Found | Fixed | Remaining |
|----------|-------|-------|-----------|
| P0 | 1 | 1 | 0 |
| P1 | 2 | 2 | 0 |
| P2 | 1 | 1 | 0 |
| Info | 1 | 0 | 1 (RustDesk — tracked) |

## P0 CLOSED — Orphaned songBird on :8080

**Finding**: A songBird `server` process (PID 801431) was manually launched
in an SSH session on **Jun 14** — running orphaned for 27 days. Bound to
`0.0.0.0:8080` with an iptables `ACCEPT tcp dpt:8080` rule **bypassing UFW**,
allowing direct internet access. 249,000 packets had been accepted through
this rule.

**Risk**: Unauthenticated songBird IPC server exposed to the public internet,
outside of any service management or monitoring.

**Fix**:
1. Killed PID 801431
2. Removed iptables ACCEPT rule for port 8080
3. Removed from `/etc/iptables.rules` (persist across reboot)
4. Verified port closed and rule absent

**Root cause**: Manual launch during development/testing without corresponding
systemd service or cleanup. The iptables rule was added to enable testing and
never removed.

**Prevention**: All long-running processes must be systemd-managed. No manual
iptables rules — all firewall changes through UFW only. The posture audit
pattern catches drift like this.

## P1 CLOSED — live.primals.eco TLS Failure

**Finding**: `live.primals.eco` was in the Caddyfile but had **no DNS record**
(NXDOMAIN). Caddy was repeatedly attempting ACME certificate issuance and
failing, burning through Let's Encrypt rate limits (HTTP-01, then TLS-ALPN-01,
then falling back to ZeroSSL). Any client connecting got `tlsv1 alert internal
error`.

**Risk**: ACME rate limit exhaustion could affect certificate renewal for other
domains. TLS errors in logs mask real issues.

**Fix**: Removed `live.primals.eco` from Caddyfile. Will be re-added when:
1. DNS A record is created in Cloudflare
2. petalTongue NUCLEUS is serving on sporeGate:9900
3. Both conditions validated (LIVE-ACTIVATE task)

**Files**: `/etc/membrane/Caddyfile`, `provision-golgi.sh` updated.

## P1 CLOSED — DNS Response Rate Limiting

**Finding**: Knot DNS serving 3 zones on the public IP (port 53) with **no
Response Rate Limiting**. Susceptible to DNS amplification attacks where
attackers send spoofed queries to generate large responses directed at victims.

**Risk**: DNS amplification — golgi could be an unwitting participant in
DDoS attacks against third parties.

**Fix**: Added `mod-rrl` to Knot configuration:
- `rate-limit: 200` — max 200 identical responses per second per source
- `slip: 2` — every 2nd rate-limited response is a truncated response
  (tells legitimate clients to retry over TCP)
- Applied globally via `template.default.global-module`

**Files**: `/etc/knot/knot.conf` updated on golgi. Knot reloaded, all 3
zones (primals.eco, primal.eco, nestgate.io) serving normally with RRL active.

## P2 CLOSED — Duplicate CSP on lab.primals.eco

**Finding**: `lab.primals.eco` returned **two** `Content-Security-Policy`
headers — one from Caddy's `(csp_proxy)` snippet and one from JupyterHub's
upstream response (`frame-ancestors 'none'; report-uri /hub/security/csp-report`).
Browsers may apply only one, or merge them unpredictably.

**Fix**: Added `header_down -Content-Security-Policy` to the `reverse_proxy`
block for `lab.primals.eco`, stripping the upstream CSP. Caddy's CSP is now
the single authoritative policy.

**Files**: `/etc/membrane/Caddyfile`, `provision-golgi.sh` updated.

## INFO — RustDesk Relay Security Standardization

**Finding**: RustDesk relay (hbbs + hbbr) occupies 5 public ports:
- 21115/tcp (hbbs ID server)
- 21116/tcp (hbbs NAT type test)
- 21116/udp (hbbs NAT probe)
- 21117/tcp (hbbr relay)
- 21118/tcp, 21119/tcp (hbbs additional)

Two active relay connections from sporeGate observed. This is the primary
remote access system for the ecosystem.

**Status**: Intentional and required — not a vulnerability. However:
- No fail2ban coverage for RustDesk ports
- No rate limiting on RustDesk connections
- hbbs/hbbr binaries are not version-managed through pepti depot
- No monitoring of RustDesk auth attempts
- Identity keys should be backed up and rotated on schedule

**Recommendation**: RustDesk relay should be treated as a first-class
infrastructure component:
1. Add fail2ban jail for RustDesk auth failures (when log format supports it)
2. Track hbbs/hbbr versions in depot checksums
3. Include RustDesk identity keys in key rotation audit (`wg-key-audit` pattern)
4. Future: evaluate replacing with a sovereign relay primal (birdSong transport
   layer could subsume this function)

## Validated Controls (No Issues)

| Control | Detail |
|---------|--------|
| SSH hardening | PasswordAuth=no, PubkeyOnly, prohibit-password root |
| fail2ban | 2 jails (sshd + forgejo-ssh), 24 bans total, 6 active |
| HTTPS rate limiting | iptables 50 new conn/10s, 6 drops recorded |
| Security headers | HSTS (2yr preload), X-Frame DENY, nosniff, CSP, Permissions-Policy — all domains |
| TLS certs | primals.eco (Oct 7), membrane (Aug 13), git (Aug 26), lab (Aug 26) — ACME auto-renew |
| Caddy binding | :443/:80 public, :2019 admin on localhost only |
| Forgejo | HTTP 127.0.0.1:3000, SSH :2222 (fail2ban protected) |
| petalTongue | 127.0.0.1:8090 only |
| WireGuard | :51820/udp, 4 peers, handshakes live |
| UFW default | deny incoming, allow outgoing, deny routed |
| DNSSEC | ECDSAP256SHA256, NSEC3, auto-signed for all 3 zones |
| DNS RRL | 200 qps limit, slip=2 (new) |

## Post-Audit Port Map — golgi

```
PORT      PROTO  SERVICE             ACCESS          PROTECTION
22/tcp    TCP    SSH (management)    Public          fail2ban (sshd jail), key-only
53/tcp    TCP    Knot DNS            Public          RRL 200qps, DNSSEC
53/udp    UDP    Knot DNS            Public          RRL 200qps, DNSSEC
80/tcp    TCP    Caddy HTTP          Public          ACME + redirect only
443/tcp   TCP    Caddy HTTPS         Public          rate limit 50/10s, CSP, HSTS
2222/tcp  TCP    Forgejo SSH         Public          fail2ban (forgejo-ssh jail)
3478/tcp  TCP    songBird TURN       Public          BTSP encrypted
3478/udp  UDP    songBird TURN       Public          BTSP encrypted
7700/tcp  TCP    songBird Federation Public          Tower mesh hub
21115/tcp TCP    RustDesk hbbs       Public          (needs hardening)
21116/tcp TCP    RustDesk hbbs       Public          (needs hardening)
21116/udp UDP    RustDesk hbbs       Public          (needs hardening)
21117/tcp TCP    RustDesk hbbr       Public          (needs hardening)
21118/tcp TCP    RustDesk hbbs       Public          (needs hardening)
21119/tcp TCP    RustDesk hbbr       Public          (needs hardening)
51820/udp UDP    WireGuard           Public          Encrypted mesh
49152-65535/udp  songBird TURN data  Public          BTSP relay
---
2019/tcp  TCP    Caddy admin         127.0.0.1 only  N/A
3000/tcp  TCP    Forgejo HTTP        127.0.0.1 only  N/A
8090/tcp  TCP    petalTongue         127.0.0.1 only  N/A
```

**Closed this session**: Port 8080 (orphaned songBird)

## Files Changed

- `provision-golgi.sh` — removed live.primals.eco block, added
  `header_down -Content-Security-Policy` to lab reverse proxy
- `/etc/membrane/Caddyfile` (golgi live) — live.primals.eco removed,
  lab CSP dedup, reloaded
- `/etc/knot/knot.conf` (golgi live) — mod-rrl added, reloaded
- `/etc/iptables.rules` (golgi live) — port 8080 ACCEPT removed

---

*sporeGate — posture audit complete. 4 exposures found, 4 fixed. RustDesk
relay tracked for standardization. Outer membrane validated.*
