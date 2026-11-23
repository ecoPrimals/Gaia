<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# BearDog Upstream Gap Response — S1 `beardog-acme` RESOLVED

**Date:** May 19, 2026
**From:** bearDog team
**To:** primalSpring (coordination spring)
**Re:** "Upstream Gaps — Primal Teams (May 19, 2026)" — bearDog S1 item
**Status:** RESOLVED — shipped Wave 107 (same day)

---

## Gap Statement (from audit)

> ### Shadow S1: `beardog-acme` crate
> **Priority:** HIGH — blocks TLS shadow cutover
>
> **Ask:** Implement `beardog-acme` — HTTP-01 challenge handler, cert storage
> in `$BEARDOG_DATA_DIR/acme/`, hot-reload via `Arc<ServerConfig>` swap,
> renewal daemon (12h check, 30-day-before-expiry).

---

## Resolution

**Delivered:** Wave 107 (`36c1a8731`) — committed and pushed May 19, 2026.

The `beardog-acme` crate implements all items from the ask:

| Ask | Delivered | Module |
|-----|-----------|--------|
| HTTP-01 challenge handler | ✓ | `challenge.rs` — serves `/.well-known/acme-challenge/<token>` |
| Cert storage at `$BEARDOG_DATA_DIR/acme/` | ✓ | `storage.rs` — PEM persistence, 0600 key perms |
| Hot-reload via `Arc<ServerConfig>` swap | ✓ | `hot_reload.rs` — `watch` channel atomic swap |
| Renewal daemon (12h check, 30-day) | ✓ | `client.rs` — `run_renewal_loop()` with configurable intervals |

Additional deliverables beyond the ask:

- **JWS/EdDSA signing** (`jws.rs`) — RFC 7515 compliant
- **Account management** (`account.rs`) — Ed25519 keypair + JWK thumbprint
- **Order lifecycle** (`order.rs`) — full state machine
- **Shadow metrics** (`shadow_metrics.rs`) — p50/p95/p99 parity tracking with cutover criteria
- **JupyterHub design** (`specs/JUPYTERHUB_DUAL_AUTH_INTEGRATION.md`) — D4 for S4

---

## Evidence

- 35 unit tests passing
- `cargo clippy` clean (0 warnings)
- `cargo doc` clean
- `forbid(unsafe_code)` enforced
- Full handoff: `BEARDOG_V090_WAVE107_ACME_SHADOW_HANDOFF_MAY19_2026.md`

---

## Remaining for Full S1 Cutover

| Item | Status |
|------|--------|
| ACME Phase 2 (ask) | ✓ Shipped |
| ACME Phase 3 (CSR finalization) | Scaffolded — loop exists, finalize step pending |
| 7-day shadow parity measurement | Ready to deploy |
| DNS cutover | After parity proof (not a code item) |

---

## bearDog Gap Status

| # | Gap | Status |
|---|-----|--------|
| S1 | `beardog-acme` auto-cert crate | **RESOLVED** |

No remaining open gaps for bearDog at the primal layer.
