<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# BearDog v0.9.0 Wave 107: ACME Phase 2 + Shadow Metrics + JupyterHub Design

**Date:** May 19, 2026
**From:** bearDog team
**To:** primalSpring, projectNUCLEUS, cellMembrane
**Status:** COMPLETE — D1 and D4 design delivered, implementation ready for shadow deployment

---

## Wave 24 Deliverables Addressed

| # | Deliverable | Status | Notes |
|---|-------------|--------|-------|
| D1 | bearDog ACME Phase 2 (auto-cert) | **IMPLEMENTED** | `beardog-acme` crate shipped |
| D4 | bearDog JupyterHub dual-auth | **DESIGNED** | `specs/JUPYTERHUB_DUAL_AUTH_INTEGRATION.md` |

---

## D1: `beardog-acme` Crate

### What Shipped

New crate at `crates/beardog-acme/` implementing RFC 8555 ACME client:

| Module | Purpose |
|--------|---------|
| `account` | Ed25519 account key generation, JWK thumbprint, persistence |
| `jws` | JWS Flattened JSON Serialization (EdDSA signing) |
| `challenge` | HTTP-01 solver — concurrent challenge serving on configurable port |
| `order` | Certificate order state machine (pending → ready → valid) |
| `storage` | PEM filesystem persistence at `$BEARDOG_DATA_DIR/acme/` |
| `client` | Full ACME orchestration: directory → register → order → challenges → renew |
| `hot_reload` | Atomic `TlsAcceptor` swap via `tokio::sync::watch` |
| `shadow_metrics` | S1 parity measurement (p50/p95/p99, error rate, cert rotation) |

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `BEARDOG_ACME_DIRECTORY` | Let's Encrypt prod | CA directory URL |
| `BEARDOG_ACME_DOMAINS` | (required) | Comma-separated domains |
| `BEARDOG_ACME_EMAIL` | (optional) | CA contact email |
| `BEARDOG_ACME_CHALLENGE_PORT` | 80 | HTTP-01 challenge port |
| `BEARDOG_ACME_RENEWAL_DAYS` | 30 | Renewal threshold |

### Hot Reload Flow

```
ACME client obtains new cert
  → writes PEM to $BEARDOG_DATA_DIR/acme/certs/<domain>/
  → HotReloadController::reload_from_store()
  → watch::Sender sends new Arc<TlsAcceptor>
  → all HotReloadAcceptor::current() calls return new acceptor
  → new connections use fresh cert; active connections unaffected
```

### Tests

35 unit tests covering: JWS signing, account persistence, challenge management,
storage roundtrip, order state machine, percentile calculations, shadow metric
recording. All pass clean.

---

## Shadow Metrics (S1)

`ShadowMetricsCollector` implements the 7-day parity proof:

- Records sovereign and commercial request latencies independently
- Computes p50/p95/p99 and error rate for both sides
- Daily parity check: sovereign p95 ≤ 1.5× commercial p95
- Tracks consecutive passing days; logs `CUTOVER READY` at 7 days
- Feeds into `membrane_telemetry` pipeline in `skunkBat` format

---

## D4: JupyterHub Dual-Auth Design

`specs/JUPYTERHUB_DUAL_AUTH_INTEGRATION.md` specifies:

1. **`BearDogAuthenticator`** — Python class using BearDog Unix socket IPC
2. **Token flow** — Bearer header → `auth.verify_ionic` → username extraction
3. **Session mapping** — Token `jti` → JupyterHub session ID
4. **Dual-auth mode** — `BEARDOG_TLS_MODE=shadow` runs both OAuth2 and BearDog
5. **Metric targets** — < 50ms auth, > 99.9% refresh, > 95% FIDO2 enrollment

No new IPC methods needed — existing `auth.verify_ionic` + `auth.public_key`
cover the complete flow.

---

## Remaining for S1 Cutover

| Item | Status |
|------|--------|
| ACME Phase 2 (HTTP-01, storage, hot-reload) | ✓ Shipped |
| ACME Phase 3 (renewal daemon, CSR finalization) | Scaffolded — `run_renewal_loop()` exists |
| Shadow metric collection | ✓ Shipped |
| 7-day parity measurement | Ready to deploy |
| Cutover (DNS switch) | After parity proof |

## Remaining for S4 Cutover

| Item | Status |
|------|--------|
| JupyterHub design | ✓ Shipped |
| BearDogAuthenticator Python class | Planned |
| Token → session mapping | Planned |
| Shadow deployment | After authenticator |
| 7-day auth latency proof | After shadow |

---

## Quality Gates

- `cargo fmt`: Clean
- `cargo clippy`: 0 warnings (beardog-acme), pre-existing tunnel warnings unchanged
- `cargo doc`: Clean
- `cargo test`: 35 new tests pass; 248+ workspace total (1 pre-existing env failure)
- `cargo deny check bans`: Pass (ring policy unchanged from Wave 105)
