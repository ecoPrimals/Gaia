# Security & Exposure Sprint — Wave 136

**Date**: Jul 10, 2026 | **From**: eastGate overwatch | **To**: All gate teams
**Priority**: P0 — public exposure achieved, warming cycle active, instability risk HIGH
**Glacial context**: Sudden warming (DNS sovereign + site live + AI crawlers enabled) after extended stadial development. This is a phase transition — the system is exposed before all hardening is complete.

---

## Threat Model Change

**Before Wave 135**: System developed behind closed doors. Inner membrane only. Attack surface = VPS endpoints + GitHub mirrors. Threat actors = opportunistic scanners.

**After Wave 135b**: Full public exposure. `primals.eco` resolves to sovereign Caddy. 301 pages indexed. robots.txt explicitly invites AI crawlers (GPTBot, ClaudeBot, PerplexityBot). Search engines discovering. The `ecoPrimal` handle exists on HN — registered, silent, findable.

**The risk**: We achieved stadial criteria (7/7 CLEAR) in a controlled environment. We are now exposed in a live environment with known gaps in outer membrane hardening. This is the warming-cooling instability: the warming (public exposure) happened; we must now rapidly cool (harden) before the thermal stress breaks something.

---

## Current Exposure Surface (Triage Matrix)

### CRITICAL (exploitable now, no mitigation in place)

| # | Exposure | Attack Vector | Impact | Mitigation |
|---|----------|---------------|--------|------------|
| EXP-01 | **No security headers on primals.eco** | Clickjacking (no X-Frame-Options), MIME sniffing, no HSTS | Site embeddable in attacker frames, browser MITM on first visit | **Deploy Caddy security headers immediately** (see §Caddy Hardening below) |
| EXP-02 | **404 catch-all returns homepage** | Content confusion, SEO poisoning, enumeration masking | Attackers can probe paths without getting 404 signals; search engines index garbage; deployment gaps invisible | **Remove try_files fallback** — let missing paths 404 |
| EXP-03 | **bearDog cert expires Aug 13** | TLS failure in 33 days | Site goes offline or falls back to insecure | **P1: cert consolidation + ACME auto-renewal validation** |

### HIGH (attack surface exists, partial mitigation)

| # | Exposure | Attack Vector | Impact | Current Mitigation | Gap |
|---|----------|---------------|--------|--------------------|-----|
| EXP-04 | **Forgejo SSH on port 2222 (public)** | Brute-force, CVE exploitation | Source compromise, cascade poisoning | SSH key-only auth, non-standard port | No fail2ban, no rate limiting, no geo-blocking |
| EXP-05 | **depot at membrane.primals.eco** | Unauthorized binary fetch, checksums.toml tampering | Supply chain attack if depot compromised | BLAKE3 verification on fetch, read-only Caddy serving | No auth on fetch (by design), but no abuse rate-limiting |
| EXP-06 | **JupyterHub at lab.primals.eco** | Auth bypass, kernel escape, lateral movement | Compute hijack, data exfiltration | 4-tier auth, mechanism-enforced isolation, iptables | Cloudflare tunnel (dependency), songBird drawbridge not yet auth-gated |
| EXP-07 | **WireGuard overlay hub (golgi)** | Peer key compromise, DDoS on UDP port | Mesh disruption, gate impersonation | WireGuard cryptographic auth, hub-spoke limits blast radius | No peer rotation policy, no intrusion detection on overlay |

### MEDIUM (limited exposure, defense-in-depth gaps)

| # | Exposure | Attack Vector | Impact | Status |
|---|----------|---------------|--------|--------|
| EXP-08 | GitHub Actions as trailing CI | Workflow injection, PAT compromise | Mirror contamination (not primary — Forgejo is source of truth) | Acceptable — trailing shadow, not authority |
| EXP-09 | DigitalOcean VPS (golgi) | Provider compromise, infrastructure seizure | Site goes down, depot unavailable | Acceptable — LAN mesh continues, data is local |
| EXP-10 | Domain registrar | Domain hijack | Site unreachable | DNSSEC + registrar lock. No mitigation for registrar-level seizure. |
| EXP-11 | AI crawler content extraction | Training data harvesting, competitive intelligence | Content freely available (AGPL — acceptable by design) | Not a risk — intentional exposure |

### LOW (theoretical, defense exists)

| # | Exposure | Notes |
|---|----------|-------|
| EXP-12 | Inner membrane LAN scan | Requires physical LAN access. Gates behind Flint router. |
| EXP-13 | BTSP protocol reverse-engineering | ChaCha20-Poly1305 AEAD. Would require primal binary RE. |
| EXP-14 | Songbird Dark Forest beacon analysis | Zero-metadata leakage by design. Family seed required. |

---

## Immediate Actions (Wave 136a — this week)

### 1. Caddy Security Headers (golgi team — P0)

Add to Caddyfile for `primals.eco`:

```caddy
primals.eco {
    root * /srv/primals.eco
    file_server

    header {
        Strict-Transport-Security "max-age=63072000; includeSubDomains; preload"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "DENY"
        X-XSS-Protection "0"
        Referrer-Policy "strict-origin-when-cross-origin"
        Permissions-Policy "camera=(), microphone=(), geolocation=(), interest-cohort=()"
        -Server
    }

    encode gzip

    # Proper 404 — remove any try_files fallback
    handle_errors {
        @404 expression {err.status_code} == 404
        handle @404 {
            respond "404 — not found" 404
        }
    }
}
```

Apply same pattern to `membrane.primals.eco` and `git.primals.eco`.

**Closes**: EXP-01, EXP-02

### 2. bearDog Cert Lifecycle (bearDog team — P1)

- Validate ACME auto-renewal fires before Aug 13
- Test: `openssl s_client -connect primals.eco:443 -servername primals.eco 2>/dev/null | openssl x509 -noout -dates`
- If renewal fails: manual `caddy reload` + investigate ACME challenge path
- Long-term: bearDog gatehouse replaces Caddy TLS entirely

**Closes**: EXP-03

### 3. Forgejo SSH Hardening (golgi team — P1)

```bash
# fail2ban for SSH on port 2222
apt-get install fail2ban
cat > /etc/fail2ban/jail.d/forgejo-ssh.conf << 'EOF'
[forgejo-ssh]
enabled = true
port = 2222
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
findtime = 600
EOF
systemctl restart fail2ban
```

Additionally:
- `MaxAuthTries 3` in sshd_config for port 2222
- Consider geo-blocking (optional — may interfere with WAN gates)

**Closes**: EXP-04

### 4. Depot Rate Limiting (golgi team — P2)

```caddy
membrane.primals.eco {
    rate_limit {
        zone depot {
            key {remote_host}
            events 30
            window 1m
        }
    }
    # ... existing depot config
}
```

Prevents enumeration/abuse of binary depot without breaking legitimate gate fetches.

**Closes**: EXP-05 (partial)

---

## Pen Testing Evolution (Wave 136b — darkforest v3.0)

### Scope Expansion

darkforest v2.0 tests 13 internal primals (181 checks). v3.0 adds outer membrane:

| Module | Target | Checks (estimated) |
|--------|--------|---------------------|
| `outer.tls` | primals.eco :443 | Cipher suite audit, cert chain, HSTS preload eligibility, protocol downgrade |
| `outer.http` | primals.eco :443 | Verb fuzzing (TRACE, DELETE, PUT), path traversal, directory listing, header injection |
| `outer.depot` | membrane.primals.eco | Unauthorized write attempts, checksum integrity verification, rate abuse |
| `outer.forge` | git.primals.eco :2222 | SSH handshake fuzzing, auth bypass probes, repo enumeration |
| `outer.dns` | primal.eco nameservers | Zone transfer attempt, DNSSEC validation, cache poisoning probes |
| `outer.mesh` | WireGuard :51820 | Handshake flood, invalid peer probe, traffic analysis baseline |

### New Threat Actors (extend from 3 to 5)

| Actor | Profile | Capability |
|-------|---------|------------|
| External scanner | Automated (Shodan, Censys) | Port scan, banner grab, CVE probing |
| Targeted researcher | Motivated individual (HN reader) | Source code review, endpoint discovery, creative path probing |
| Supply chain attacker | Sophisticated | depot poisoning, dependency confusion, GitHub workflow injection |
| State-level observer | Passive | Traffic analysis, metadata correlation, DNS monitoring |
| Insider (compromised gate) | One gate key leaked | Lateral movement, mesh poisoning, capability escalation |

### Implementation

The darkforest v3.0 binary adds `--scope outer` flag:
```bash
darkforest validate --scope inner   # existing 181 checks
darkforest validate --scope outer   # new outer membrane checks
darkforest validate --scope full    # both (production audit)
```

---

## Resilience & Failover Testing (Wave 136c)

### Scenarios to Validate

| # | Scenario | Method | Expected | Recovery |
|---|----------|--------|----------|----------|
| RF-01 | **Single gate death** | `systemctl stop nucleus@*` on ironGate | Songbird routes around. No user-visible impact. | Auto-recover on gate restart via mesh.init |
| RF-02 | **golgi VPS death** | Drop WireGuard peer, stop Caddy | LAN gates continue operating. primals.eco goes offline. WAN gates lose relay. | Caddy auto-restarts (systemd). VPS provider recovery. |
| RF-03 | **Caddy crash** | `kill -9 caddy` | systemd restarts within 5s. Zero-downtime for H3 connections (QUIC survives). | Automatic (RestartSec=5) |
| RF-04 | **Depot corruption** | Tamper one binary in /srv/depot/ | Gates that fetch detect BLAKE3 mismatch, refuse binary, alert. | Re-harvest from source, regenerate checksums.toml |
| RF-05 | **DNS poisoning** | Attempt zone transfer, query with spoofed resolver | DNSSEC validation rejects. knot-dns refuses AXFR. | Self-healing (DNSSEC is cryptographic) |
| RF-06 | **Certificate expiry** | Let Aug 13 pass without renewal | Site shows TLS warning. Caddy auto-renewal should fire at 30d before expiry. | Manual `caddy reload` if ACME fails. |
| RF-07 | **Forgejo compromise** | Simulate unauthorized push to sporePrint | Cascade rebuilds site with malicious content. | Cross-membrane validation (inner membrane checks outer). Content signing needed (future). |
| RF-08 | **Mesh partition** | Disconnect LAN between house 1 and house 2 (cut trunk) | Each house operates independently. No cross-house capability.call. | Physical reconnection. Songbird auto-heals on link restore. |
| RF-09 | **Full power loss (house 1)** | UPS expiry simulation | All house 1 gates offline. flockGate + golgi continue (remote). | Power restore → gates auto-start → mesh.init → full recovery |
| RF-10 | **pepti build authority compromise** | Attacker gains SSH to peptidoglycan | Can inject malicious binaries into depot. | BLAKE3 verification + code review on source. **Gap: no binary signing yet.** |

### Critical Gap Identified: RF-07 and RF-10

Both reveal the same structural weakness: **no code/content signing on the cascade output**. If Forgejo or pepti is compromised, malicious content/binaries flow downstream automatically.

**Mitigation path**:
1. Short-term: SSH key rotation + 2FA on Forgejo admin
2. Medium-term: bearDog signs all cascade artifacts (commit signatures + binary signatures)
3. Long-term: Reproducible builds — any gate can verify a binary by rebuilding from source and comparing BLAKE3

---

## Glacial Criteria Update (Wave 136 addition)

Add criterion 8 to the glacial shift readiness:

| # | Criterion | Meaning |
|---|-----------|---------|
| 8 | **Outer membrane hardened for public exposure** | Security headers deployed. Pen testing passed (darkforest v3.0 outer scope). Failover scenarios RF-01 through RF-05 validated. No CRITICAL exposures open. Certificate lifecycle automated. |

This criterion reflects the phase transition: stadial criteria (1-7) were about building sovereign infrastructure. Criterion 8 is about **surviving contact with the public internet**.

---

## Monitoring Activation (Wave 136d)

### skunkBat Outer-Membrane Mode

skunkBat currently monitors internal IPC patterns. Extend to:

| Signal | Source | Alert Condition |
|--------|--------|-----------------|
| SSH brute-force | `/var/log/auth.log` on golgi | >5 failed attempts from same IP in 10m |
| Unusual HTTP patterns | Caddy access logs | >100 req/s from single IP, scanner fingerprints (Nikto, sqlmap, nuclei) |
| Depot abuse | membrane access logs | >50 binary fetches from unknown IP in 1h |
| Cert expiry approaching | bearDog ACME | <14 days to expiry without successful renewal |
| Mesh topology change | Songbird peer table | New peer appears, existing peer disappears unexpectedly |
| DNS query anomaly | knot-dns query log | AXFR attempts, high NXDOMAIN rate (enumeration) |

### Alerting

For now: write to `wateringHole/alerts/` as timestamped TOML. Future: Songbird mesh-routes alerts to all gates with `alert.security` capability.

---

## Timeline

| Wave | Focus | Deliverable |
|------|-------|-------------|
| 136a (this week) | **Immediate hardening** | Caddy headers, 404 fix, fail2ban, cert validation |
| 136b (next week) | **darkforest v3.0 scope** | Outer membrane pen test module, 5-actor threat model |
| 136c (week 3) | **Failover playbook** | RF-01 through RF-10 executed and documented |
| 136d (week 4) | **Monitoring activation** | skunkBat outer mode, access log ingestion, alert pipeline |
| 137+ | **Hardening iteration** | Binary signing, reproducible builds, 2FA on Forgejo, peer rotation |

---

## The Warming-Cooling Metaphor

The ecosystem operated in glacial conditions (closed, controlled, internal) for 135 waves. Wave 135b triggered a **sudden warming event**: DNS propagation, site live, AI crawlers active, 301 pages indexed, sovereign TLS serving requests from the public internet.

This is thermally analogous to:
- Ice sheet exposed to warm current (rapid surface melt)
- Structural integrity depends on re-freezing the exposed surface before melt reaches the substrate

The substrate (inner membrane, primals, mesh) is solid. The exposed surface (outer membrane serving layer) has known gaps. The sprint is to **freeze the surface** (harden the outer membrane) before external probing finds the gaps.

**Success condition**: All CRITICAL and HIGH exposures closed within Wave 136. darkforest v3.0 passes outer scope. Failover scenarios validated. Then the system can sustain the warming — public exposure becomes a steady state, not a vulnerability window.

---

## Team Assignments

| Team | Wave 136 Responsibility |
|------|------------------------|
| **golgi/sporeGate** | Caddy hardening (EXP-01, EXP-02), fail2ban (EXP-04), rate limiting (EXP-05) |
| **bearDog** | Cert lifecycle validation (EXP-03), ACME monitoring, future binary signing |
| **skunkBat** | Outer-membrane monitoring mode, access log ingestion |
| **darkforest/primalSpring** | v3.0 scope definition, outer module implementation |
| **songBird** | Mesh topology monitoring, peer rotation policy design |
| **cellMembrane** | Depot integrity monitoring, reproducible build path design |
| **overwatch (eastGate)** | Failover scenario execution, RF-01 through RF-10 |
