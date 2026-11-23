# skunkBat Outer Membrane Extension — Wave 136a (SKUNY-OM)

**Date**: 2026-07-10
**Gate**: flockGate
**Commit**: `f9154a8` (skunkBat)
**Scope**: Extend skunkBat from inner-membrane IPC monitoring to outer
membrane HTTP anomaly detection for the Tower HTTP Gateway integration.

---

## Delivered

| What | Detail |
|------|--------|
| `HttpObservation` data model | 6 HTTP dimensions: `request_rate`, `error_rate_4xx`, `error_rate_5xx`, `path_diversity`, `avg_payload_bytes`, `method_diversity`. Backwards-compatible `Option` on `Observation`. |
| `ThreatType::HttpAnomaly` | New threat variant for HTTP-layer behavioral anomalies (dimension, deviation, source IP). |
| Statistical profiler extension | `StatisticalProfiler` expanded from 3 inner-membrane dimensions to 6 (+ HTTP request rate, path diversity, 4xx error rate). Extracted `detect_http_anomalies` helper for clean separation. |
| `advisory_check_http()` | New sync advisory path that accepts HTTP telemetry, runs behavioral anomaly detection, returns `Verdict::Warn` for suspicious HTTP patterns. Filters to HTTP-only anomalies (inner-membrane dimensions excluded). |
| `security.advisory` IPC enrichment | Now accepts optional `{"source": "ip", "http": {...}}` payload. Gateway feeds per-request snapshots for real-time screening. |
| `HttpMetrics` observability | New metrics subdomain: `requests_screened`, `allows`, `warns`, `blocks`. Auto-populated by `record_http_advisory()`. Serialization omits subdomain when unused. |
| `BaselineStats` HTTP dimensions | `http_request_rate`, `http_path_diversity`, `http_error_rate_4xx` stats available via `baseline.query`. |
| Sync profiler access | `ProfilerHandle` + compute-only `block_on` for sync advisory path (no async runtime dependency in the advisory hot path). |

## Prior Hardening (same wave)

| What | Commit | Detail |
|------|--------|--------|
| `capability.list` registration | `ef49c65` | Alias was dispatched but not advertised in `METHODS` — broke capability contract completeness. Fixed. |
| `#[must_use]` sweep | `ef49c65` | 11 security-critical sync APIs annotated: `respond_to_threat`, `detect`, `scan`, `baseline_stats`, `check_anomalies`, `derive_session_keys`, `encrypt_frame`, `decrypt_frame`, `discover_all`, `discover_by_capability`, `BtspConfig::from_env`. |
| Defense test split | `ef49c65` | `defense/mod.rs` 663→382 lines, tests extracted to `defense_tests.rs`. |
| CI-DIV-02 resolved | `7d6ef6f` | `default-members` added — `cargo build --bin skunkbat` resolves without `--package`. |
| Convergence standards | `35326c3` | `.cargo/config.toml` with musl-static cross-compilation targets (x86_64 + aarch64). All 4 convergence standards met. |

## Integration Path — Tower HTTP Gateway

```
HTTP request → Tower middleware → aggregate per-source-IP metrics
                                      │
                                      ▼
                              security.advisory
                              {"source": "1.2.3.4", "http": {
                                "request_rate": 150.0,
                                "error_rate_4xx": 0.45,
                                "path_diversity": 200,
                                ...
                              }}
                                      │
                                      ▼
                              skunkBat advisory_check_http()
                              1. Quarantine check    → Block
                              2. HTTP anomaly check  → Warn (with anomaly details)
                              3. Clean               → Allow
                                      │
                                      ▼
                              Gateway decision: route / warn-log / reject
```

## Validation

- **553 tests** (12 new HTTP-specific tests), 0 failures
- clippy clean (`-D warnings`), fmt clean
- Release build verified
- All 4 convergence standards met (BUILDABLE, RUNNABLE, TOOLCHAIN, CONFIG)

## Remaining (136d backlog)

- HTTP intrusion heuristics (path enumeration signatures, method confusion patterns)
- Caddy access log → skunkBat structured ingestion (AUDIT-01 output → `baseline.observe`)
- Tower gateway integration exercise (production traffic)

---

*flockGate — skunkBat outer membrane extension delivered. Inner + outer membrane monitoring active. 553 tests.*
