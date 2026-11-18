# NestGate v0.5.0 — Session 87 Deep Debt Sweep

**Date**: 2026-06-03
**Gate**: ironGate (eastGate)
**Primal**: nestgate v0.5.0
**Session**: 87

## Delivered

### Code Quality (HIGH)

1. **`storage_stream.rs` split (1,101 → 676 + 455L)**
   - Extracted content-addressed CAS streaming into `content_stream.rs`
   - Shared session infrastructure (`StoreUpload`, `RetrieveSession`, maps, TTL) stays in `storage_stream.rs` as `pub`
   - CAS-specific handlers (BLAKE3 finalize, content path layout) in `content_stream.rs`
   - Both modules under 800-line policy

2. **CapabilityRouter honesty**
   - Replaced fake `"zfs-dataset-123"` success responses with explicit `NotImplemented` errors
   - `handle_storage_capability` → directs callers to JSON-RPC transport (UDS/TCP)
   - `send_universal_request` → directs to mesh relay transport
   - Removed stale `#[expect(clippy::unnecessary_wraps)]` that was protecting the fakes
   - 7 tests updated from asserting success to asserting correct error behavior

3. **`String::from()` idiom migration**
   - Converted `"literal".to_string()` → `String::from("literal")` in 454 production files
   - Ecosystem idiom consistency

4. **dispatch.rs deduplication**
   - 8 repeated `request.params.clone().unwrap_or_else(|| json!({}))` → `take_params()` helper
   - Merged identical `storage.retrieve_stream_chunk` / `content.retrieve_stream_chunk` match arms

5. **fsmonitor security XDG defaults**
   - `/etc/nestgate/keys` → `NESTGATE_CONFIG_DIR` → `XDG_CONFIG_HOME` → `$HOME/.config` → FHS
   - `/var/log/nestgate/audit.log` → `NESTGATE_LOG_DIR` → `XDG_STATE_HOME` → `$HOME/.local/state` → FHS
   - 2 new tests validating env-override behavior

## Metrics

- **1,607 tests** passing (serial), 0 failures
- **Zero clippy warnings** (`clippy::pedantic` + `clippy::nursery`)
- **No files > 800 lines** in production code
- **Zero fake production responses** in CapabilityRouter
- **Zero `#[allow]` in production** code

## Remaining Debt (post-audit)

- Pre-existing env-var race conditions in parallel test runs (12 tests; all pass serial)
- `nestgate-api` 501 HTTP endpoints (8 in `extras.rs`, REST snapshots) — intentional placeholders, documented
- `FederationConfig` empty placeholder struct in `nestgate-core` — low priority
- `download_components` no-op in `nestgate-installer` — low priority

## Verification

```bash
cargo clippy --all-features -- -D warnings  # zero warnings
cargo test -- --test-threads=1              # 1,607 passed, 0 failed
```
