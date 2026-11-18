# skunkBat v0.2.0 — Release Handoff

**Date**: May 24, 2026  
**From**: skunkBat (primal development)  
**To**: primalSpring (audit), plasmidBin (deployment)  
**Priority**: NORMAL — zero blockers, requesting downstream audit

---

## Summary

skunkBat v0.2.0 is release-ready with zero internal debt. All Wave 47
behavioral convergence items are resolved. Pure Rust, 389 tests passing,
`clippy::pedantic + nursery -D warnings` clean, `cargo deny` clean.

---

## Wave 47 Resolutions (all DONE)

| Item | Resolution |
|------|-----------|
| `--socket PATH` CLI flag | `#[arg(long)] socket: Option<String>` on `server` subcommand |
| `lifecycle.status` method | Returns `{"primal":"skunkbat","version":"0.2.0","status":"running"}` |
| SIGTERM handling | `tokio::signal::unix::signal(SignalKind::terminate())` in shutdown select |
| Default port → 9750 | `const DEFAULT_PORT: u16 = 9750` (aligned with `ports.env`) |

---

## Deep Debt Resolutions (this session)

| Category | Before | After |
|----------|--------|-------|
| `rand` crate | `rand::thread_rng()` for nonces | Eliminated — `OsRng` via `chacha20poly1305::aead::rand_core` |
| Hardcoded strings | `"skunkbat"` literals in forwarding | `skunk_bat_core::PRIMAL_ID` everywhere |
| `FromStr`/`Display` | Inherent `from_str` methods | Proper trait impls for `CipherSuite`, `BondType` |
| `dispatch.rs` | 180 lines (over limit) | 145 lines (extracted `capabilities_response()` helper) |
| `nestgate.rs` | Redundant `or_else` always produced socket path | Correct existence-gated resolution |
| Lint standard | Mix of `#[allow]` / `#[expect]` | `#[expect(reason)]` default, `#[allow(reason)]` for target-conditional only |
| Clippy debt | 8 distinct warnings | All resolved (pedantic + nursery clean) |

---

## Quality Gate Status

```
cargo build --release         ✓ (zero warnings)
cargo clippy --all-targets    ✓ (pedantic + nursery, -D warnings)
cargo test --workspace        ✓ (389 tests, 0 failures)
cargo deny check              ✓ (advisory/ban/license/source)
cargo fmt --check             ✓
cargo doc --no-deps           ✓
```

---

## Architecture Highlights

- **Edition 2024**, `forbid(unsafe_code)` workspace-wide
- **BTSP Phase 3**: ChaCha20-Poly1305 AEAD encrypted framing
- **JH-0 MethodGate**: Pre-dispatch capability authorization
- **JH-5 Audit Log**: Ring buffer + cross-primal forwarding (rhizoCrypt DAG + sweetGrass braids)
- **NestGate ContentProtector**: CAS integrity verification via `content.*` IPC
- **Neural API `primal.announce`**: 18 methods, cost/latency hints, signal tier
- **Pure Rust crypto**: RustCrypto only, `ring` banned in `deny.toml`
- **48 source files**, largest 815 lines (`negotiate.rs`)
- **Self-registration** with discovery (`ipc.register`) — standalone-safe
- **Deployment converged**: `--socket`, `--bind`, `--port`, SIGTERM, `lifecycle.status`

---

## For primalSpring

Requesting standard audit pass. Key areas:

1. BTSP Phase 3 cipher negotiation flow (`negotiate.rs`)
2. JH-5 forwarding to rhizoCrypt/sweetGrass (`forwarding.rs`)
3. MethodGate authorization modes (`method_gate.rs`)
4. Neural API announce payload (`registration.rs`)

---

## For plasmidBin

- `start_primal.sh` workarounds for skunkBat can be **removed**:
  - `serve` → `server` rename: done upstream
  - Port override: default is now 9750
  - Socket path: `--socket` flag works
  - SIGTERM: handled natively
- CI release workflow ready: `ci.yml` builds musl-static x86_64 + aarch64 on tag push
- Tag `v0.2.0` pending final primalSpring audit sign-off
