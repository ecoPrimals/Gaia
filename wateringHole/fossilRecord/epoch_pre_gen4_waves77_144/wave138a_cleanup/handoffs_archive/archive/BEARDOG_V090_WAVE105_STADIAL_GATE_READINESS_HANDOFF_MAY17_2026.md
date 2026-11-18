<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# BearDog v0.9.0 — Wave 105: Stadial Gate Readiness

**Date**: May 17, 2026
**From**: bearDog (crypto spine)
**To**: primalSpring, cellMembrane, projectNUCLEUS, all primals
**Audit**: Wave 22 — Stadial Gate (All Upstream Primals)

---

## Summary

BearDog is **stadial-ready**. All three Wave 22 audit items resolved:

1. **`deny.toml` ring policy reconciled** — `ring` was banned but required as
   `rustls`'s crypto backend. Policy updated to allow `ring` only as wrapped by
   `rustls` and `rustls-webpki`. `cargo deny check bans` passes with zero
   errors and zero warnings.

2. **ACME TLS integration path documented** — New
   `specs/ACME_TLS_INTEGRATION_PATH.md` covers the stadial shadow cutover
   design: crate architecture, challenge types, certificate storage, hot-reload,
   renewal strategy, and shadow mode. Phase 1 (design) complete.

3. **Universal standards checklist verified** — Self-audit confirms compliance
   across runtime, discovery, security, build, and documentation dimensions.

---

## What Changed

### `deny.toml` — Ring Policy Fix

```toml
# Before
{ crate = "ring", wrappers = [] }

# After
{ crate = "ring", wrappers = ["rustls", "rustls-webpki"] }
```

Additionally removed stale `mio` skip (single-version resolved).

Rationale: `rustls` is the only production-quality pure-Rust TLS
implementation with WebPKI support. Its default crypto backend is `ring`.
No pure-Rust WebPKI provider exists that avoids `ring`. Direct `ring` usage
by BearDog code remains banned — only transitive use through TLS is permitted.

### ACME Integration Path (Design Only)

File: `specs/ACME_TLS_INTEGRATION_PATH.md`

Key design decisions:
- New crate `beardog-acme` for ACME lifecycle
- HTTP-01 default, TLS-ALPN-01 for port-443-only, DNS-01 for wildcards
- Hot reload via `Arc<ServerConfig>` swap (no restart)
- 12h renewal check, 30-day-before-expiry threshold
- Shadow mode: `BEARDOG_TLS_MODE=acme|static|shadow`
- Future IPC: `acme.status`, `acme.trigger_renew`, `acme.list_certs`
- Zero downstream dependencies (cellMembrane/projectNUCLEUS are enrichments)

### Universal Checklist Results

| Category | Items | Result |
|----------|-------|--------|
| Runtime | Health triad, UDS, TCP, server, standalone | PASS |
| Discovery | capabilities.list, identity.get | PASS |
| Security | BTSP, ChaCha20+HKDF, family guard, deny.toml | PASS |
| Build | edition 2024, musl targets | PASS |
| Documentation | README, CHANGELOG, STATUS current | PASS |

---

## Stadial Pairing

| Partner | Integration Point | Status |
|---------|------------------|--------|
| cellMembrane | TLS termination cutover | Ready (ACME design complete) |
| projectNUCLEUS | Sovereignty orchestration | Ready (BTSP + TLS) |
| All primals | BTSP negotiation | Ready (Phase 3 encrypted frames) |

---

## Quality Gates

| Gate | Status |
|------|--------|
| `cargo fmt --all -- --check` | Clean |
| `cargo clippy --workspace --all-targets` | 0 errors, warnings in test files only |
| `cargo doc --workspace --no-deps` | Clean |
| `cargo test --workspace` | 14,940+ pass, 1 pre-existing env-dependent skip |
| `cargo deny check bans` | Clean (0 errors, 0 warnings) |

---

## Composition Gap

**None.** BearDog has no open composition gaps per Wave 22 audit.

---

## Files Modified

- `deny.toml` — ring wrapper policy + mio skip cleanup
- `specs/ACME_TLS_INTEGRATION_PATH.md` — new
- `STATUS.md` — Wave 105 entry
- `CHANGELOG.md` — Wave 105 entry
