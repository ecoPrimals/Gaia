# petalTongue — S3 Shadow Parity: GitHub Pages Equivalence

**Date**: May 19, 2026
**Primal**: petalTongue
**Trigger**: Wave 24 shadow run execution — S3 content hosting shadow
**Priority**: HIGH — stadial requires shadow parity proof before cutover

## Context

Wave 24 defines 4 shadow runs to prove sovereign components replace their
commercial counterparts. S3 tests content hosting: petalTongue + NestGate
replacing GitHub Pages.

The composition:
```
Browser → petalTongue :8080 (HTTP)
       → nestGate content.resolve (content-addressed storage)
       → BLAKE3 hash verification
```

## Gap Analysis (pre-fix)

| Feature | GitHub Pages | petalTongue (before) | Status |
|---------|-------------|---------------------|--------|
| MIME types | CDN + extension | ServeDir + NestGate mime_type | PRESENT |
| Gzip compression | CDN automatic | None | **MISSING** |
| Security headers | nosniff, X-Frame | None | **MISSING** |
| Request metrics | CloudFlare analytics | None | **MISSING** |
| Custom 404 | `404.html` from site | Plain text "Not Found" | **MISSING** |
| Cache-Control | max-age=600 (HTML) | Configurable (default 3600s) | PRESENT |
| ETag/Last-Modified | CDN | ServeDir (filesystem only) | PARTIAL |

## Changes

### 1. Gzip + Brotli Compression

Added `tower_http::compression::CompressionLayer` to the HTTP router. All
responses now support automatic content negotiation via `Accept-Encoding`.
tower-http features enabled: `compression-gzip`, `compression-br`.

### 2. Security Headers

Axum middleware injects on all responses:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: camera=(), microphone=(), geolocation=()`

### 3. HTTP Request Tracing (Metrics)

`tower_http::trace::TraceLayer` wired with structured tracing spans:
- Span: `method`, `uri`
- On response: `status` (u16), `latency_ms` (u64)

Shadow run metric collection uses the tracing subscriber output to compute:
- **TTFB**: `latency_ms` per request
- **404 rate**: count of `status=404` events
- **Cache hit rate**: requires upstream proxy or NestGate ETag support

### 4. Custom 404 Pages

`{docroot}/404.html` served with HTTP 404 status when present (GitHub Pages /
Jekyll convention). `Cache-Control: no-cache` on error pages. Falls back to
plain text if no custom page exists.

## tower-http Features (after)

| Feature | Enabled | Used |
|---------|---------|------|
| `fs` | Yes | ServeDir |
| `cors` | Yes | CorsLayer |
| `trace` | Yes | TraceLayer |
| `compression-gzip` | Yes | CompressionLayer |
| `compression-br` | Yes | CompressionLayer |
| `set-header` | Yes | Available for future use |

## Remaining S3 Items (not petalTongue-owned)

- **Mirror GitHub Pages content to NestGate**: nestGate team via `content.put`
- **DNS shadow**: `staging.` subdomain → petalTongue :8080 (ops)
- **NestGate ETag**: content-hash-based ETag for conditional requests (nestGate)
- **7-day metric collection**: projectNUCLEUS membrane telemetry pipeline

## Quality Gate

- `cargo fmt --check`: PASS
- `cargo clippy --workspace --all-targets --all-features -- -D warnings`: PASS
- `cargo test --workspace --all-features`: all tests pass, 0 failures
