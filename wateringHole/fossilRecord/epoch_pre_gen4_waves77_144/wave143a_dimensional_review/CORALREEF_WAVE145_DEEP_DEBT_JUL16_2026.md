<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# coralReef Wave 145 — Deep Debt: Error Handling, De-Hardcoding, Deduplication

**Date**: 2026-07-16  
**Commits**: `99444c5` (Wave 144) + `d51bab4` (Wave 145)  
**Status**: Deep debt round complete. Zero primal-name hardcoding in production.

---

## Summary

Six deep-debt items resolved in a single wave:

1. **BEARDOG_SOCKET excised** — deprecated env var and `security_provider_socket_legacy()` removed. BTSP discovery is now pure capability-based via `$BTSP_PROVIDER_SOCKET` only. Zero hardcoded primal names in production code.

2. **Provenance error visibility** — all `.ok()` calls in `try_sign()` now emit `tracing::warn` with structured context before discarding errors. Crypto signing failures no longer silent.

3. **Provenance timeout constants** — magic numbers `Duration::from_secs(5)` / `Duration::from_secs(2)` extracted to `CRYPTO_SIGN_READ_TIMEOUT` / `CRYPTO_SIGN_WRITE_TIMEOUT` in `config.rs`.

4. **Mutex poison logging** — `btsp_negotiate.rs` session registry and negotiated-keys registry now log `tracing::warn` on mutex poison instead of silently treating as missing session/keys.

5. **main.rs deduplication** — collapsed two nearly identical `cmd_server` implementations (tarpc / no-tarpc) into a single unified function. `main.rs`: 788 → 627 LOC (net -169 lines removed).

6. **identity.get Arc optimization** — `IDENTITY_ADVERTISED` now stores `Arc<IdentityGetResponse>`. JSON-RPC `identity.get` avoids cloning capability/transport vectors on every call.

## Quality Gates

- `cargo clippy --all-features -- -D warnings` — zero warnings
- `cargo check --target x86_64-pc-windows-gnu` — zero warnings
- `cargo test --all-features` — 3648 tests, 0 failures
- `cargo build --release --bin coralreef` — clean

## Remaining Deep Debt (Low Priority)

| Item | Priority | Notes |
|------|----------|-------|
| Server-side `bind_local()` / `LocalListener` | P2 | Extends Wave 144 client transport abstraction |
| `sm20/encoder.rs` (795 LOC) | P2 | Near-threshold; split by instruction category |
| `amd/encoding.rs` (795 LOC) | P2 | Near-threshold; split by encoding family |
| `getrandom` custom backend via rustix | P2 | Removes transitive libc from crypto path |
| 97 `CompileError::NotImplemented` sites | P1 | PTX SM120/Blackwell WIP — evolving per-wave |
