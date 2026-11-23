# BearDog v0.9.0 — Wave 134d: Upstream Regression Fix + UNIT-DIV-04 Status

**Date**: Jul 9, 2026
**From**: eastGate (BearDog agent)
**Commits**: `d594d87` (Wave 134a), `80c322d` (Wave 134d)
**HEAD**: `80c322d`

---

## UNIT-DIV-04: RESOLVED (since Wave 132f)

The ecosystem blurb still lists `bearDog CryptoProvider panic (UNIT-DIV-04)` as a P1 blocker. **This was resolved in Wave 132f** and hardened across three subsequent commits:

1. **`main.rs` startup install** — `let _ = rustls_rustcrypto::provider().install_default();` runs before any TLS/ACME operations. The `let _ =` swallows the "already installed" case (idempotent).

2. **`beardog-acme/src/rustls_provider.rs` self-healing fallback** — `assert_installed()` checks `CryptoProvider::get_default()` and installs if absent. Works unconditionally (not just in test builds).

3. **No double-install panic** — Both call sites use the `install_default()` pattern which returns `Err(provider)` if already installed, never panics.

**Recommendation**: Remove UNIT-DIV-04 from the 134b blocker list. bearDog is ready for DNS cutover pending pepti rebuild.

---

## Wave 134d Changes

### P0 — Gateway Bind Error Silencing (upstream regression)

Upstream `579bc77` (BUILD-DIV-02) consolidated `bind_https_listener` + `serve_https_gateway` into a single function spawned via `tokio::spawn`. This silenced bind failures (`:443` port in use, insufficient privileges).

**Fix**: Restored eager bind via `bind_gateway_listener()` + `start_https_gateway()` that returns `JoinHandle` after successful bind. Bind errors now propagate at startup.

### Test Restoration

Upstream `579bc77` also removed 5 integration tests. All restored/adapted:
- 3 ACME HTTP solver tests (redirect, challenge response, 400 bad request)
- 2 gateway bind tests (port 0 success, occupied port failure)

### Wave 134a: DRY + BUILD-DIV-01 Gate

- **`connection_handlers.rs` (705L -> 655L)** — extracted `dispatch_by_protocol` helper from duplicate riboCipher dispatch
- **`.githooks/pre-push`** — enforces `cargo check --all-targets` before push (BUILD-DIV-01 prevention)

---

## Health

```
Tests:     13,884+ passing (0 failures)
Clippy:    0 warnings (workspace)
Cargo deny: all 4 pass (advisories, bans, licenses, sources)
cargo check --all-targets: PASS
```
