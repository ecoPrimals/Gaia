# cellMembrane Wave 157d — Dependency Evolution + Deep Debt

**Date:** 2026-08-09
**Author:** eastGate primalSpring overwatch
**Wave:** 157d
**Commit:** `2b7652f` — `evolve: chrono→time + magic numbers + byte literal hardening`

---

## Summary

Fourth commit of Wave 157d deep debt sweep. External dependency evolution,
magic number elimination, and byte literal hardening.

---

## Changes

### 1. External Dependency Evolution: `chrono` → `time`

Replaced `chrono 0.4` with `time 0.3` across 9 files (~30 call sites):
- `lib.rs` — centralized timestamp helpers
- `context.rs` — braid TTL expiry
- `impulse/lifecycle.rs`, `impulse/policy.rs`, `impulse/primal.rs`, `impulse/sync.rs` — impulse timestamps
- `plasmid/canary.rs` — canary staleness
- `gate/key_portal.rs` — SSH cert lifetime parsing
- `caddy/mod.rs` — OpenSSL cert date parsing

**Impact:** Eliminates `chrono` + `iana-time-zone` transitive deps. `time` is
pure Rust, lighter, and `#![no_std]`-compatible (future types crate path).

### 2. Centralized Timestamp Helpers

New public API in `lib.rs`:
- `local_now_iso8601_tz()` — local time with tz offset
- `utc_now_iso8601_z()` — UTC with Z suffix
- `format_offset_datetime()` — format any `OffsetDateTime`
- `parse_iso8601_tz()` — parse ISO 8601 with tz
- `parse_rfc3339()` — parse RFC 3339
- `parse_openssl_date()` — parse OpenSSL cert dates

### 3. Byte Literal Hardening

`b"127.0.0.1"` in `service/mod.rs` `is_externally_reachable()` replaced with
`const_str_eq()` helper + `BIND_LOOPBACK` constant reference. Eliminates the
only raw IP byte literal in the codebase.

### 4. Magic Numbers → Named Constants

| Constant | Value | File |
|----------|-------|------|
| `IPC_READ_BUF_CAPACITY` | 4096 | `sync_ipc.rs` |
| `NUCLEUS_STOP_GRACE_SECS` | 1 | `harvest.rs` |
| `PKILL_SETTLE_MS` | 500 | `harvest.rs` |
| `SOCKET_POLL_INTERVAL_MS` | 200 | `sandbox.rs` |
| `SOCKET_POLL_MAX_ATTEMPTS` | 40 | `sandbox.rs` |
| `DEFAULT_CERT_LIFETIME_HOURS` | 8 | `key_portal.rs` |
| `DEFAULT_CERT_LIFETIME_MINUTES` | 480 | `key_portal.rs` |
| `DEFAULT_CERT_LIFETIME_SECS` | 28800 | `key_portal.rs` |
| `SECS_PER_HOUR` | 3600 | `key_portal.rs` |
| `SECS_PER_MINUTE` | 60 | `key_portal.rs` |

---

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| Tests | 1344 | 1344 |
| Clippy warnings | 0 | 0 |
| Files changed | — | 20 |
| Net lines | — | −30 |
| External deps removed | `chrono`, `iana-time-zone` | — |
| External deps added | `time` | — |
| Bare magic numbers | ~15 | 0 |
| IP byte literals | 1 | 0 |

---

## Debris Audit

Full repo scan completed. Findings:
- **Zero TODO/FIXME/HACK/XXX** in production `.rs` code
- **Zero orphan source files** (181/181 reachable)
- **Zero empty directories**
- **`receipts/` directory** contains 1 git-tracked HSM key generation receipt — operational artifact, retained
- **`GLACIAL_SHIFT_TRACKER.md`** at 49KB — full history already externalized to fossil record; trimming deferred (low priority)
- **`caddy/` module** deprecated Wave 132 but still active during Tower shadow validation — no action
- **`deploy_membrane.sh` refs** in RUNBOOKS.md — already annotated as "fossil record" in header
- **`specs/FIELDMOUSE_CONTRACT.md`** references GitHub Releases (superseded by sovereign depot) — noted for upstream spec team

---

## Upstream Notes

- **ISO8601 format constants** (`ISO8601_UTC`, `ISO8601_TZ`) retained in `cellmembrane-types` for cross-primal interop. Primals still using `chrono` can consume them. `membrane-shadow` no longer references them.
- **`time` crate version** locked to 0.3.45 (latest compatible with Rust 1.85 MSRV). Version 0.3.55 available but requires Rust 1.88.
- **Production mock audit**: All `#[cfg(not(unix))]` stubs are intentional platform gates (UDS unavailable on Windows), not production mocks to evolve. Named Pipe transport stubs are forward declarations.
