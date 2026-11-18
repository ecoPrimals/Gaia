# cellMembrane Wave 140a — Deep Debt Delivery

**Date**: Jul 15, 2026 | **Wave**: 140a | **From**: sporeGate builder
**Scope**: Deep debt sweep, dependency evolution, smart refactoring, OS Atheism continuation

---

## Delivered (this session)

### Constants & Deduplication
- Extracted `ISO8601_UTC` and `ISO8601_TZ` timestamp format constants — replaced 18 duplicate format strings across 13 files
- Extracted `DEFAULT_HTTPS_PORT` (443) and `DEFAULT_SHADOW_PORT` (8443) — replaced hardcoded ports

### Dead Code & Safety
- Removed dead `git_rev_parse_head()` in `freshness.rs` (unused, was `#[allow(dead_code)]`)
- Evolved 3 `unreachable!()` → `.expect()` in `ribocipher.rs` HMAC helpers

### Stringly-Typed → Type-Safe
- Added `FromStr` for `MembraneComposition` and `WebhookProvider`
- Evolved `post_sync.rs` harvest/refresh status from JSON substring matching to typed `HarvestResult`/`RefreshResult` deserialization
- Evolved `pipeline()` to use typed `HarvestStatus` with `matches!()` instead of raw JSON access
- Replaced 7 JSON substring probes (`response.contains("\"result\"")`) across health, sovereignty, mesh, canary, sandbox with proper `serde_json` structural checks

### Dependency Reduction
- **Eliminated `nix` crate** (was 0.31, only used for `kill()`/`Pid` in one function). Replaced with `std::process::Command("kill")` — safe, no-`unsafe`, cross-platform

### Smart File Refactoring
- `plasmid/mod.rs`: **875 → 514 lines** — extracted `depot_sync.rs` submodule
- `plasmid/harvest.rs`: **841 → 763 lines** — extracted `harvest_manifest.rs` submodule
- Zero files over 800 lines remain

### Build Verification
- 1,074 tests pass, clippy clean, zero warnings

---

## Previously Delivered (Wave 137b–140a)

- SIGN-VERIFY-ON-FETCH: Ed25519 signature verification on depot fetch
- BIOMEOS-TEMPLATE: `service.template` subcommand
- CASCADE-HANG fix: `BranchCheckedOut` detection, reconcile timeout
- harvest `--local` mode (~10x faster builds)
- `depot_sync --push` mode (builder → VPS)
- `sources.toml` auto-provisioning from manifest
- OS Atheism Phase 1: `Platform`, `TargetArch`, `TargetOs` types
- OS Atheism Phase 2: `TransportEndpoint::NamedPipe`, `InitSystem::detect()`, platform-aware `graceful_kill`/CSPRNG/chmod
- Error taxonomy cleanup (`ShadowError::Parse` → correct variants)
- Cascade restart unit name fix (`{primal}-membrane.service`)
- `PermissionsExt` cross-platform guards

---

## Open for Upstream Teams

### From CAC Handoff (P1–P2)
1. **TreeParity for wateringHole heads auto-publish** — `temporal/mod.rs` diverge path should check tree parity before agentic dispatch
2. **Content-hash impulse deduplication** — `impulse/sync.rs` creates duplicate diverge impulses across gates

### For footPrint / tideglass Teams (from Blurb)
3. Caddy block + drawbridge routes per `COMPOSITION_ROUTING_STANDARD` for footPrint
4. Fix TLS handshake on `footprint.primals.eco` redirect
5. Caddy block at `tideglass.primals.eco`

### Remaining Deep Debt (lower priority)
6. `resolve_gate_primals` OnceLock cache never updates after first gate
7. `resolve.rs` returns first candidate UDS path even when socket doesn't exist
8. Hardcoded mesh IPs in `cytoplasm.rs` — should fall through to manifest topology
9. `caddy/` module deprecated Wave 132 — archive after Tower shadow validation
10. `cloudflare/` module S1 graduated — consider making feature non-default

---

## Codebase Health Snapshot

| Metric | Value |
|--------|-------|
| Tests | 1,074 |
| Clippy | Clean (pedantic) |
| `unsafe` | Forbidden (`#![forbid(unsafe_code)]` both crates) |
| Production `unwrap()` | 0 |
| `todo!()`/`unimplemented!()` | 0 |
| Files >800L | 0 |
| External deps | 15 (nix eliminated, reqwest on rustls) |
