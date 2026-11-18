# FRAGO: skunkBat Live Threat Ingestion — Wave 136b

**From**: sporeGate (outer membrane ops)
**To**: skunkBat team (flockGate)
**Date**: 2026-07-11
**Priority**: P1 — live adversarial traffic available now
**Ref**: `LIVE_THREAT_DATA_ACTIVATION_AAR_136b.md`, `SKUNKBAT_OUTER_MEMBRANE_136a.md`

> **STATUS: CLOSED** — Phase 1 code delivered at `385f66f` (Wave 136b).
> Crate: `skunky-ingest`. golgi systemd deploy pending.

---

## Situation

golgi outer membrane is under sustained adversarial pressure:

- **122 unique attacker IPs** in 7 days (SSH brute-force)
- **317 failed auth attempts** caught by fail2ban, 22 IPs banned
- **HTTP scanner probes**: WordPress/Joomla enumeration, SQL injection
  attempts, SEO crawlers mapping the attack surface
- Caddy JSON access logs now capture **per-request structured telemetry**
  (host, URI, method, status, remote IP, user-agent, response time)
- fail2ban + iptables rate limiting are reactive — no predictive layer exists

The `HttpObservation` model and `advisory_check_http()` path shipped in
Wave 136a (`SKUNKBAT_OUTER_MEMBRANE_136a.md`) are ready to consume this
data. The `StatisticalProfiler` has never seen live traffic — only seed
data from `normal_baseline()`.

## Mission

Build the **SKUNY-INGEST** bridge: a log tailer that reads golgi's
structured logs and feeds `baseline.observe` with real observations,
activating skunkBat's behavioral detection on live adversarial traffic.

## Execution

### Phase 1 — Log Tailer Agent

Build a lightweight process (Rust binary or shell+jq script) that:

1. **Tails** `/var/log/caddy/access.log` (JSON, one object per line)
2. **Aggregates** per-source-IP metrics over a configurable window (suggest 60s):
   - `connection_rate` — requests per second from this IP
   - `traffic_volume` — total response bytes
   - `ports_accessed` — destination ports seen (443 for all HTTP currently)
   - `request_rate` — HTTP requests per second (HttpObservation field)
   - `error_rate_4xx` — fraction of 4xx responses
   - `path_diversity` — unique URI paths requested
   - `avg_payload_bytes` — mean response size
   - `method_diversity` — unique HTTP methods used
3. **Pushes** each aggregated window as a `baseline.observe` JSON-RPC call
   to skunkBat (TCP :9750 or UDS)

### Caddy access log schema

Each line is a JSON object. Relevant fields:

```json
{
  "request": {
    "remote_ip": "203.0.113.50",
    "host": "primals.eco",
    "uri": "/wp-includes/js/jquery/jquery.js",
    "method": "GET",
    "headers": {
      "User-Agent": ["Mozilla/5.0 ..."]
    }
  },
  "status": 404,
  "size": 1234,
  "duration": 0.002,
  "ts": 1783788660.123
}
```

### Phase 2 — SSH Auth Failure Feed

Parse `journalctl -u ssh -f` (streaming) for failed auth events:

- Extract: source IP, attempted username, timestamp, port
- Derive: `attempt_rate` per IP, `dictionary_signature` (username set hash)
- Feed as observations with `ports_accessed: [22, 2222]`

### Phase 3 — Advisory Feedback Loop

Once baseline is established (≥10 observations):

- `security.advisory` verdicts become meaningful (Allow/Warn/Block)
- Wire advisory output to a response mechanism:
  - `Warn` → log + increment watch counter
  - `Block` → trigger fail2ban-style ban or iptables rule
- This closes the loop: detect → decide → act → observe result

## Coordination

### Data location

| Source | Path on golgi | Format |
|--------|---------------|--------|
| HTTP requests | `/var/log/caddy/access.log` | JSON per line, 50MiB rotation |
| SSH failures | `journalctl -u ssh` | systemd journal |
| fail2ban bans | `fail2ban-client status forgejo-ssh` | CLI output |
| Rate limit hits | `iptables -L INPUT -v` | counters |

### Network

- skunkBat on sporeGate: `10.13.37.2:9750` (TCP) or UDS
- golgi → sporeGate: WireGuard mesh (`10.13.37.1` → `10.13.37.2`)
- The tailer runs on golgi, pushes to skunkBat over the mesh

### Existing skunkBat interfaces (ready to consume)

| Method | Transport | What it expects |
|--------|-----------|----------------|
| `baseline.observe` | JSON-RPC 2.0 | `Observation` with optional `HttpObservation` |
| `baseline.query` | JSON-RPC 2.0 | Returns current `BaselineStats` |
| `baseline.anomaly` | JSON-RPC 2.0 | Read-only anomaly check |
| `security.detect` | JSON-RPC 2.0 | Full 6-category threat analysis |
| `security.advisory` | JSON-RPC 2.0 | Per-source allow/warn/block verdict |

### Known attack patterns (training data already available)

The AAR documents specific patterns for validation:

- **Burst detection**: 45 attempts/hour peaks vs 6 attempts/hour troughs
- **Dictionary clustering**: `admin`/`ubuntu`/`postgres` vs `AdminGPON`/`telecomadmin`/`ubnt`
- **Scanner fingerprinting**: `link_checker/0.1.0`, `SemrushBot/7`, CMS probes
- **Injection signatures**: backtick-encoded SQL in URI paths (`%60+ c.id+ %60`)

## Constraints

- Phase 1 can be a simple script — sovereignty purity is secondary to
  activation. Evolve to a primal-grade component later.
- The tailer should be idempotent and crash-safe (track file position).
- Do not modify skunkBat's core `Observation` struct — `HttpObservation`
  fields already cover the HTTP dimensions.
- Rate limit the observe calls — one per aggregation window, not per log line.

## Success Criteria

1. skunkBat `baseline.query` returns established baseline with real stats
2. `security.detect` produces non-empty threat vectors from live traffic
3. `security.advisory` returns `Warn` for known scanner IPs
4. Anomaly detection fires on burst windows (validates sigma threshold)

---

*sporeGate — FRAGO issued. Live data waiting. Wire it up.*
