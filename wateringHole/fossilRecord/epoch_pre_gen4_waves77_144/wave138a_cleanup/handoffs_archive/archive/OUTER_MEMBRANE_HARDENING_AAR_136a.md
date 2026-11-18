# Outer Membrane Hardening AAR — Wave 136a

**Date**: 2026-07-10
**Scope**: Full outer membrane hardening sprint — security headers, CSP, 404,
fail2ban, rate limiting, access logs, WireGuard key audit, cert lifecycle

---

## Delivered

| ID | What | Detail |
|----|------|--------|
| EXP-01 | Security headers | HSTS (2yr preload), X-Frame-Options DENY, nosniff, Permissions-Policy, Referrer-Policy, Server stripped. `(security_headers)` snippet imported by all 6 server blocks. |
| EXP-02 | 404 fix | `try_files` SPA fallback removed. `handle_errors` serves Zola's styled `404.html`. Garbage paths return 404, not 200. |
| EXP-03 | Cert lifecycle | Caddy ACME auto-renewal confirmed for all 5 domains. `membrane.primals.eco` renews ~Jul 14 (33d remaining). All certs in `/caddy/certificates/`. |
| EXP-04 | Forgejo SSH | fail2ban jail on port 2222: maxretry=3, ban=1h, findtime=600s. Already banned `165.154.200.185` (17 failed attempts observed). |
| EXP-05 | Rate limiting | iptables: 50 new HTTPS connections per 10 seconds per source IP. Covers all domains on :443. Saved to `/etc/iptables.rules`. |
| CSP-01 | Content-Security-Policy | Two policies: `(csp_static)` for Zola sites (default-src 'none', self-hosted only, form-action 'none') and `(csp_proxy)` for proxied services (Forgejo, lab — allows unsafe-eval for Forgejo JS, wss: for WebSocket). |
| AUDIT-01 | Access logs | Caddy JSON logs to `/var/log/caddy/access.log`. 50MiB roll, 5 files retained, 30-day window. Structured format for future skunkBat ingestion. |
| EXP-07a | WireGuard key audit | `wg-key-audit` tool at `/usr/local/bin/`. Reports config age, peer handshake status, rotation protocol. 90-day rotation policy. All 4 peers healthy (config 19d old). |
| RF-01 | Cert renewal drill | ACME storage validated. Cert metadata files present for all domains. Caddy's default renewal (30d before expiry) confirmed active. |

## Architecture — Hardened State

```
Internet → golgi :443
  │
  ├── iptables: 50 new conn/10s per IP (DDoS baseline)
  │
  ├── Caddy (ACME, HTTP/2, H3 alt-svc, gzip)
  │   ├── All blocks: (security_headers) — HSTS, X-Frame, nosniff, -Server
  │   │
  │   ├── primals.eco      (csp_static) → file_server, handle_errors 404
  │   ├── www.primals.eco   → 301 redirect
  │   ├── membrane.*        (csp_static) → depot + health + nestgate
  │   ├── lab.*             (csp_proxy)  → WireGuard → songBird :7780
  │   ├── git.*             (csp_proxy)  → Forgejo :3000
  │   └── live.*            (csp_proxy)  → WireGuard → petalTongue :9900
  │
  ├── fail2ban
  │   ├── sshd (port 22)
  │   └── forgejo-ssh (port 2222): maxretry=3, ban=1h
  │
  ├── JSON access logs → /var/log/caddy/ (50MiB × 5, 30d)
  │
  └── WireGuard :51820 → 4 peers (90d rotation policy)
      ├── sporeGate  10.13.37.2 (handshake: live)
      ├── eastGate   10.13.37.5 (handshake: live)
      ├── southGate  10.13.37.6 (handshake: live)
      └── ironGate   10.13.37.7 (handshake: live)
```

## Exposure Triage — Final State

```
CLOSED:      EXP-01, EXP-02, EXP-03, EXP-04, EXP-05, CSP-01, AUDIT-01, EXP-07a, RF-01
ACCEPTABLE:  EXP-08 (GitHub shadow), EXP-09 (VPS provider), EXP-10 (registrar),
             EXP-11 (AI crawlers — intentional)
THEORETICAL: EXP-12 (LAN), EXP-13 (BTSP), EXP-14 (darkForest beacon)
REMAINING:   EXP-06 (lab auth-gate — songBird drawbridge, scoped to 136c)
             SIGN-01 (cascade signing — scoped to 136b)
```

## Sovereignty Evolution Path

Each hardening measure deployed here is infrastructure that the primals
eventually absorb:

| Infra (current) | Primal (target) | What it becomes |
|-----------------|-----------------|-----------------|
| Caddy TLS + CSP | bearDog gateway | SNI dispatch + header injection |
| iptables rate limit | songBird drawbridge | Capability-gated rate control |
| Caddy access logs | skunkBat | HTTP anomaly detection pipeline |
| fail2ban | skunkBat | Behavioral ban with mesh propagation |
| wg-key-audit | darkForest | Automated key rotation via birdSong |
| Caddy ACME | bearDog ACME | Already implemented, awaiting SNI dispatch |

## Files Changed

- `provision-golgi.sh` — full Caddyfile rewrite (CSP snippets, JSON logs),
  fail2ban jail, iptables rate limiting, wg-key-audit tool
- `/etc/membrane/Caddyfile` (golgi live) — deployed, validated
- `/etc/fail2ban/jail.d/forgejo-ssh.conf` (golgi live)
- `/usr/local/bin/wg-key-audit` (golgi live)
- `/var/log/caddy/` (golgi live, created)

## Validation Results

| Check | Result |
|-------|--------|
| `curl -sI primals.eco` | HSTS ✓ X-Frame ✓ nosniff ✓ CSP ✓ no Server ✓ |
| `curl primals.eco/xyzzy/` | 404 (not 200) ✓ |
| `fail2ban-client status forgejo-ssh` | 1 banned, 17 failed ✓ |
| `iptables -L INPUT` | https_flood rules present ✓ |
| `/var/log/caddy/access.log` | JSON, 44+ entries ✓ |
| `wg-key-audit 90` | 4 peers, 19d old, within window ✓ |
| HTTP/2 | confirmed ✓ |
| gzip | content-encoding: gzip ✓ |
| H3 | alt-svc: h3=":443" ✓ |
