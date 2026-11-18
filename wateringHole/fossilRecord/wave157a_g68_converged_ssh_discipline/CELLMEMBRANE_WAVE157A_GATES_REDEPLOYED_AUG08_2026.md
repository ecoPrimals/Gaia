# cellMembrane Handoff — Wave 157a (6/6 Gates Redeployed)

**Date**: 2026-08-08
**Wave**: 157a
**Commits**: `55fdff3` (Forgejo fetch fix), pending (deep debt + mesh.register)
**Tests**: 1327 passing, 0 clippy warnings, cargo fmt clean

---

## Changes

### 1. Forgejo plasmid.fetch API Parse Fix (strandGate blocker)

**Root cause**: `fetch_release_tag()` never checked HTTP status before JSON
deserialization. Non-200 error bodies (404 APINotFound) were parsed as
`ReleaseResponse { tag_name }`, producing a cryptic serde error.

**Fixes**:
- HTTP status check before deserializing release tag response
- Forgejo API token included for authenticated access (private repos)
- Empty `forgejo_api` config guarded with actionable error message
- `/releases?limit=1` fallback when `/releases/latest` returns 404
- Authenticated download path for Forgejo binary assets
- `release_api_get()` helper extracted to deduplicate HTTP plumbing

**Impact**: All remote gates now have a sovereign deploy path via Forgejo.

### 2. Deep Debt Sweep

| Item | Before | After |
|------|--------|-------|
| `bridge.rs:66` | Hardcoded `"biomeos"` | `ServiceCapability::ComputeOrchestration` lookup |
| DNS listen strings | Hardcoded `"0.0.0.0@53"` in 2 places | `DEFAULT_KNOT_LISTEN` constant |
| `arch.rs:87` | Hardcoded `"/opt/ecoPrimals"` | `crate::service::DEFAULT_ECOPRIMALS_ROOT` |
| `transport.rs:195` | Hardcoded `"127.0.0.1"` | `BIND_LOOPBACK` constant |
| SSH host key paths | Hardcoded `/etc/ssh/...` (4 sites) | `DEFAULT_SSH_HOST_KEY_PUB`, `DEFAULT_SSH_HOST_KEY`, `DEFAULT_SSH_HOST_CERT` |
| `is_beardog_socket` | Self-knowledge function name | Renamed to `is_crypto_signer_socket` |

### 3. mesh.register Command (songBird Capability Self-Registration)

New `membrane mesh.register` command:
- Iterates service registry, checks socket existence for each primal
- Publishes `capability.register` via songBird `mesh.publish` for each running primal
- Reports registered count, skipped count, and gate identity
- Upstream from westGate pattern (26 capabilities across 5 provenance primals)

### 4. New Constants Added

- `DEFAULT_KNOT_LISTEN: [&str; 2]` — Knot-DNS listen directives
- `DEFAULT_SSH_HOST_KEY_PUB` — SSH host ECDSA public key path
- `DEFAULT_SSH_HOST_KEY` — SSH host ECDSA private key path
- `DEFAULT_SSH_HOST_CERT` — SSH host certificate path

---

## Metrics

| Metric | Value |
|--------|-------|
| Tests | 1327 |
| Clippy warnings | 0 |
| `unsafe` blocks | 0 |
| TODO/FIXME markers | 0 |
| Production `unwrap()`/`expect()` | 2 (HMAC — infallible) |
| Hardcoded primal names (production) | 0 |
| `reqwest` dependency | Purged |
| Files > 800L | 1 (service registry — data, not logic) |

---

## Known Gaps / Upstream Notes

- **coralReef**: BLAKE3 checksum stale on golgi depot (regenerate after next rebuild)
- **skunkBat**: `PRIMAL_BIND_MODE` env var support on Windows (P3)
- **petalTongue**: `--port` in server mode on Windows (P4)
- **songBird**: Stale PID file cleanup on Windows (P3)
- **cellMembrane**: `native_braid.py` → Rust (no .py files exist in cellMembrane — may live elsewhere)
- **TargetArch**: Deprecated, pending removal of `#[allow(deprecated)]` callers
