# SKUNY-INGEST — Live Caddy Log Tailer (Wave 136b)

**Date**: 2026-07-11
**Gate**: flockGate
**Commit**: `385f66f` (skunkBat)
**Binary**: `skunky-ingest`
**Scope**: Phase 1 of live threat ingestion — Caddy JSON access log → skunkBat behavioral profiler.

---

## Delivered

New workspace crate: `crates/skunky-ingest` (826 lines, 10 tests)

| Component | What |
|-----------|------|
| `caddy.rs` | Caddy JSON access log parser — extracts `remote_ip`, URI, method, status, size, timestamp, user-agent (future fingerprinting) |
| `aggregator.rs` | Per-source-IP metric aggregation over configurable time windows. Outputs wire-compatible `ObservationPayload` |
| `rpc.rs` | JSON-RPC 2.0 TCP client with riboCipher signal-first accept (`0xEC 0x01`). Persistent connection with auto-reconnect |
| `cursor.rs` | File position tracking for crash-safe tailing (byte offset in state file) |
| `main.rs` | Tokio async tail loop with `select!` for graceful shutdown, periodic cursor checkpoints, dry-run mode |

## CLI Interface

```
skunky-ingest [OPTIONS]

Options:
  --log-path <PATH>           Caddy JSON access log [default: /var/log/caddy/access.log]
  --skunkbat-addr <HOST:PORT> skunkBat TCP address [default: 127.0.0.1:9750]
  --window-secs <N>           Aggregation window [default: 60]
  --cursor-path <PATH>        Position cursor file [default: /var/lib/skunky-ingest/cursor.pos]
  --poll-ms <N>               Tail poll interval [default: 500]
  --dry-run                   Parse and aggregate without sending
```

## Aggregation Model

Per source IP, per window:

| Metric | Source | Maps to |
|--------|--------|---------|
| `connection_rate` | requests/window_secs | `Observation.connection_rate` |
| `traffic_volume` | sum(response_size) | `Observation.traffic_volume` |
| `ports_accessed` | always `[443]` (HTTP) | `Observation.ports_accessed` |
| `request_rate` | requests/window_secs | `HttpObservation.request_rate` |
| `error_rate_4xx` | count(4xx)/total | `HttpObservation.error_rate_4xx` |
| `error_rate_5xx` | count(5xx)/total | `HttpObservation.error_rate_5xx` |
| `path_diversity` | unique URIs | `HttpObservation.path_diversity` |
| `avg_payload_bytes` | mean(response_size) | `HttpObservation.avg_payload_bytes` |
| `method_diversity` | unique HTTP methods | `HttpObservation.method_diversity` |

## Wire Format

Uses existing skunkBat JSON-RPC 2.0 transport (NDJSON over TCP):

```json
{"jsonrpc":"2.0","method":"baseline.observe","params":{
  "connection_rate":1.08,"traffic_volume":13000,"ports_accessed":[443],
  "timestamp":{"secs_since_epoch":1720700060,"nanos_since_epoch":0},
  "http":{"request_rate":1.08,"error_rate_4xx":0.95,"error_rate_5xx":0.0,
          "path_diversity":3,"avg_payload_bytes":200,"method_diversity":2}
},"id":42}
```

## Deployment Plan (golgi)

```
golgi (10.13.37.1) ──WireGuard──▶ sporeGate (10.13.37.2:9750)
     │                                      │
     │  skunky-ingest                        │  skunkBat
     │  --log-path /var/log/caddy/access.log│  baseline.observe
     │  --skunkbat-addr 10.13.37.2:9750     │  → StatisticalProfiler
     │  --window-secs 60                    │  → BaselineStats
     │  --cursor-path /var/lib/skunky-ingest/│  → detect_anomalies()
     │    cursor.pos                        │  → security.advisory
```

### systemd unit (to be deployed)

```ini
[Unit]
Description=skunky-ingest — Caddy log tailer for skunkBat
After=network-online.target caddy.service
Wants=network-online.target

[Service]
ExecStart=/usr/local/bin/skunky-ingest \
  --log-path /var/log/caddy/access.log \
  --skunkbat-addr 10.13.37.2:9750 \
  --window-secs 60
Restart=always
RestartSec=5
StateDirectory=skunky-ingest

[Install]
WantedBy=multi-user.target
```

## Dry-Run Validation

Mock Caddy log (76 lines: 65 scanner probes from `203.0.113.50`, 10 legitimate from `10.13.37.1`, 1 trigger):

```
INFO skunky_ingest: [dry-run] would send observation rate=1.0 err_4xx=1.0 paths=1
```

Scanner IP correctly identified: 100% 4xx error rate, 1 req/sec, single path (`/wp-login.php`).

## Remaining Phases

| Phase | What | Status |
|-------|------|--------|
| Phase 1 — Log tailer | Caddy JSON → `baseline.observe` | **DONE** |
| Phase 2 — SSH feed | `journalctl -u ssh` → observations | Backlog |
| Phase 3 — Advisory loop | `security.advisory` → fail2ban/iptables | Backlog |

## Test Summary

- 10 new tests in `skunky-ingest` (parser, aggregation, flush, cursor, serialization)
- 563 total workspace tests, 0 failures

---

*flockGate — SKUNY-INGEST Phase 1 delivered. Log tailer built, dry-run validated. Ready for golgi deployment. Deploy to activate live behavioral detection on 122+ known attacker IPs.*
