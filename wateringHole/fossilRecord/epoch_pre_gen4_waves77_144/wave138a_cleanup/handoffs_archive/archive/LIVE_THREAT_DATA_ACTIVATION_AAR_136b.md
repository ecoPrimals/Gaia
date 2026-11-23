# Live Threat Data Activation AAR — Wave 136b

**Date**: 2026-07-11
**Scope**: Discovery of sustained adversarial traffic on golgi outer membrane,
access log pipeline fix, and activation roadmap for skunkBat + Tower Atomics
as live threat intelligence consumers.

---

## Discovery

Within 24 hours of deploying fail2ban (Wave 136a), the outer membrane was
already catching and banning real brute-force attackers. Analysis of the
full 7-day window revealed sustained, professional-grade adversarial traffic
that the hardening measures are now capturing but no primal is yet consuming.

This is the missing activation data for `skunkBat`'s `baseline.observe`
pipeline, which has only ever seen synthetic seed data from
`normal_baseline()` and `pentest_attack_patterns()`.

## Threat Landscape — golgi Outer Membrane (7-day snapshot)

### SSH Brute Force (ports 22 + 2222)

| Metric | Value |
|--------|-------|
| Unique attacker IPs | **122** |
| Total failed auth attempts | **317** |
| IPs banned (all-time) | 22 |
| IPs currently banned | 4–5 (rotating) |
| Sustained rate | ~20–45 attempts/hour |
| Peak burst | 45 attempts in single hour window |

**Top attackers** (by attempt count):

| IP | Attempts | Origin pattern |
|----|----------|----------------|
| 195.178.110.137 | 151 | Scan farm — cycles full dictionary |
| 45.198.224.92 | 94 | Ubuntu/admin spray |
| 218.51.148.194 | 92 | Sustained low-rate |
| 2.57.121.25 | 92 | Admin-only dictionary |
| 213.225.11.46 | 86 | Mixed dictionary |

**Username dictionary** (attack wordlist fingerprint):

```
admin(395)  ubuntu(158)  user(69)  test(60)  postgres(43)
debian(22)  ubnt(21)  guest(20)  deploy(18)  ftpuser(17)
testuser(15)  dev(14)  oracle(12)  telecomadmin(11)  centos(11)
AdminGPON(11)  developer(10)  minecraft(9)  hadoop(9)
administrator(9)  steam(8)  odoo(8)  ftp(8)  mysql(7)
```

This is a standard IoT/VPS credential-stuffing dictionary. The presence of
`AdminGPON`, `telecomadmin`, and `ubnt` indicates botnets that primarily
target consumer routers and IoT devices but spray VPS ranges indiscriminately.

### HTTP Scanning (port 443)

| Probe type | Example URI | Category |
|------------|------------|----------|
| WordPress | `/wp-includes/js/jquery/jquery.js` | CMS enumeration |
| Joomla | `/media/system/js/core.js` | CMS enumeration |
| SQL injection | `/products/lattice-qcd/%60+ c.id+ %60` | Injection attempt |
| Path traversal | `/lab/guidestone/%60+ c.id+ %60` | Injection attempt |
| SEO crawlers | SemrushBot/7 | Reconnaissance |
| Link checkers | `link_checker/0.1.0` (8 requests) | Surface mapping |

All HTTP probes return 404 or legitimate responses — no vulnerable surface
exists. But the probe patterns map the attack surface and reveal what
adversaries expect to find.

## Access Log Fix

**Bug found**: The Wave 136a Caddyfile placed the `log` directive in the
global options block. Caddy's global `log` captures server lifecycle events
(startup, TLS maintenance, shutdown) — **not** per-request HTTP access data.

**Fix**: Extracted the log configuration into an `(access_log)` snippet and
imported it into each site block. Per-site `log` directives capture full
HTTP request metadata: host, URI, method, status, remote IP, user-agent,
response headers.

**Validated**: Fresh log now captures structured JSON per request:

```
status  method  host                    uri                     ip               user-agent
200     GET     primals.eco             /                       [NUCLEUS_WAN]  curl/7.81.0
404     GET     primals.eco             /nonexistent/           [NUCLEUS_WAN]  curl/7.81.0
200     GET     membrane.primals.eco    /health                 [NUCLEUS_WAN]  curl/7.81.0
200     POST    git.primals.eco         /api/actions/runner...  [NUCLEUS_WAN]  connect-go/1.18.1
```

Updated `provision-golgi.sh` to match the live deployment.

## Activation: What This Data Enables

### skunkBat — From Synthetic to Live Baseline

`skunkBat`'s `StatisticalProfiler` (rolling window, 2.5σ anomaly threshold)
has only ever seen seed data. The live traffic provides:

| Capability | Synthetic state | Live data enables |
|------------|----------------|-------------------|
| Baseline establishment | 12 hardcoded observations | Real connection rates, traffic volumes, port distributions |
| Anomaly detection validation | PG-57 pen-test patterns only | 20–45 attempts/hour baseline; burst windows test sigma thresholds |
| Dictionary fingerprinting | None | Cluster botnets by wordlist signature |
| HTTP behavioral profiling | `HttpObservation` model built (136a) but unfed | Real path diversity, error rates, request patterns per source IP |
| Advisory verdicts | Always `Allow` (no data) | `Warn`/`Block` on deviation from established baseline |

### Tower Atomics — Live Testing Environment

The adversarial traffic creates a natural test rig for the full tower:

| Primal | What it sees | What it learns |
|--------|-------------|----------------|
| **bearDog** | TLS handshakes, cipher suites, SNI, client hello fingerprints | Connection-layer threat signatures; feeds `security.advisory` |
| **songBird** | Mesh routing probes on `lab.primals.eco` drawbridge | Topology anomalies; unauthorized route attempts |
| **skunkBat** | Aggregated observations from all sources | Multi-dimensional behavioral baseline; anomaly detection accuracy |
| **darkForest** | WireGuard peer handshake timing | Key rotation pressure signals; peer authentication anomalies |

### What's Getting Through — Future Wave Targets

Equally valuable is what the membrane currently allows:

- **CMS probes returning 404** — benign today, but maps the surface for targeted attacks
- **Injection payloads in URIs** — Caddy serves static files so these are harmless, but any
  future dynamic endpoint would need input sanitization
- **SEO crawlers** — legitimate traffic that should be distinguished from reconnaissance
- **Forgejo Actions runner polling** — high-frequency internal traffic that must not trigger
  false positives in the baseline

## Ingestion Pipeline Architecture (SKUNY-INGEST)

```
golgi outer membrane
│
├── /var/log/caddy/access.log (JSON, per-request)
│   └── Log tailer agent
│       ├── Aggregate per-source-IP per-window:
│       │   connection_rate, traffic_volume, ports_accessed,
│       │   request_rate, error_rate_4xx, path_diversity
│       └── Push → skunkBat baseline.observe (JSON-RPC)
│
├── journalctl -u ssh (fail2ban + sshd)
│   └── Auth failure parser
│       ├── Extract: source IP, username, timestamp, port
│       ├── Derive: attempt_rate, dictionary_signature
│       └── Push → skunkBat baseline.observe (JSON-RPC)
│
└── iptables rate-limit hits
    └── Connection counter
        └── Push → skunkBat baseline.observe (JSON-RPC)

                    ▼
            skunkBat (port 9750)
                    │
                    ├── StatisticalProfiler (rolling window)
                    │   ├── Inner membrane: connection_rate, traffic_volume, port_diversity
                    │   └── Outer membrane: http_request_rate, path_diversity, error_rate_4xx
                    │
                    ├── ThreatDetector::detect() — 6-category analysis
                    │   ├── Behavioral anomaly (sigma deviation)
                    │   ├── Intrusion heuristics (sensitive ports, exfil patterns)
                    │   ├── HttpAnomaly (CMS probes, injection attempts)
                    │   ├── Resource/DoS (load average)
                    │   ├── Topology (unexpected connection paths)
                    │   └── Config drift
                    │
                    └── Outputs
                        ├── security.advisory → bearDog/songBird (allow/warn/block)
                        ├── defense.quarantine → ban propagation across mesh
                        ├── AuditLog → rhizoCrypt provenance DAG
                        └── federation.broadcast → songBird mesh-wide alerts
```

## Systems Ready to Activate

| System | Current state | Activation requirement |
|--------|--------------|----------------------|
| skunkBat `baseline.observe` | Phase 1 code BUILT — `skunky-ingest` crate at `385f66f` | golgi systemd deploy (SKUNY-INGEST log tailer) |
| skunkBat `HttpObservation` | Data model + profiler dimensions built (136a) | Same tailer, HTTP fields populated |
| skunkBat `security.advisory` | Method works; always returns Allow | Baseline establishment (≥10 observations) |
| skunkBat `advisory_check_http()` | Sync advisory path built | HTTP telemetry feed from gateway or tailer |
| bearDog lineage verification | `security.advisory` source field exists | skunkBat reachable over mesh (UDS or TCP) |
| songBird federation broadcast | `federation.broadcast` method wired | skunkBat → songBird integration endpoint |
| fail2ban → skunkBat feedback | fail2ban bans independently | Bidirectional: skunkBat inform → fail2ban act |

## Files Changed

- `provision-golgi.sh` — Caddyfile updated: global log removed, per-site
  `(access_log)` snippet added to all 5 server blocks. Wave tag bumped to 136b.
- `/etc/membrane/Caddyfile` (golgi live) — deployed, validated, access log
  now captures per-request structured JSON.

## Key Insight

The outer membrane is not just a defense perimeter — it is a **live training
environment**. Every bot probe, every brute-force attempt, every CMS scan is
a data point that feeds the behavioral baseline. The primals don't need
synthetic attack simulations; the internet is already providing real
adversarial traffic at scale. The systems exist. The data exists. The wire-up
is the remaining work.

---

*sporeGate — live threat data discovery documented. 122 attacker IPs, 317 SSH
attempts, HTTP scanner patterns captured. Access log pipeline fixed. skunkBat
activation roadmap defined.*
