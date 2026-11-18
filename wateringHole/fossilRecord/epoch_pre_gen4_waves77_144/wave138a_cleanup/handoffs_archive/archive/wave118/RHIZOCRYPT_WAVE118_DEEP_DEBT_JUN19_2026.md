# rhizoCrypt — Wave 118 Deep Debt Evolution

**Date**: Jun 19, 2026
**Version**: 0.14.17
**Commit**: `fd61ffc5` (eastGate `main`)
**Author**: sporeGate automation (primalSpring overwatch)

---

## Wave 117-118 Summary

Two consecutive deep debt waves executing against the full rhizoCrypt audit:

### Wave 117 — CapabilityVerifier + scyBorg Trio + Zero-Copy

- Evolved `PresenceVerifier` to `CapabilityVerifier` — discovers `crypto:signing`
  providers via `DiscoveryRegistry`, delegates to `auth.verify_ionic` IPC
- Completed scyBorg Triple-Copyleft (LICENSE-ORC + LICENSE-CC-BY-SA)
- Refactored `uds_tests.rs` (837L) into 5 domain-focused modules
- Mesh handler coverage to 100% (15 tests)
- Neural API testability refactor (23% -> 70%+)
- Added `#[allow(reason)]` strings on all suppression attributes
- Fixed 2 broken intra-doc links
- Initial production `.clone()` audit

### Wave 118 — Zero-Copy + Coverage + Dep Evolution

- Eliminated 8 unnecessary `.clone()` calls across vertex handlers,
  mesh listener, songbird client, service signing
- Added `MeshTrustEvent::to_event_type(&self)` for borrow-friendly conversion
- 26 new tests: 14 UDS error-path, 9 service startup, 3 neural_api integration
- Dependency upgrades (all ecoBin compliant):
  - tokio 1.46->1.52, bytes 1.5->1.12, blake3 1.5->1.8
  - rand 0.8.5->0.8.6 (**RUSTSEC-2026-0097 security fix**)
  - hyper 1.0->1.10, clap 4.5->4.6, tempfile 3.15->3.27
- `cargo deny check advisories` clean

---

## Current Metrics

| Metric | Value |
|--------|-------|
| Tests | 1,748 passing (`--all-features`) |
| Coverage | 93.37% lines (llvm-cov) |
| Clippy | 0 warnings (pedantic + nursery + cargo) |
| Doc warnings | 0 |
| Unsafe blocks | 0 (`unsafe_code = "deny"`) |
| TODOs/FIXMEs | 0 |
| Production mocks | 0 (all `cfg`-gated) |
| Hardcoded addresses | 0 (capability-based discovery) |
| Files > 800L | 0 (max: 756L `method_gate.rs`) |
| Source files | 190 `.rs`, ~58,642 lines |

---

## Gate Checks (all passing)

- `cargo fmt --all -- --check`
- `cargo clippy --workspace --all-features -- -D warnings`
- `cargo doc --workspace --all-features --no-deps` (0 warnings)
- `cargo deny check advisories`
- `cargo test --workspace --all-features` (1,748 pass, 0 fail)

---

## Remaining Deferred Items

| Item | Status | Blocked On |
|------|--------|------------|
| UDS server coverage 85% -> 90% | Diminishing returns (connection-limit branch, shutdown select) | Integration test complexity |
| Service lib.rs coverage 80% -> 90% | `serve_with_tcp` requires real TCP binding | Test harness evolution |
| `PresenceVerifier` -> Ed25519 | Awaiting JH-11 ecosystem key distribution | bearDog upstream |
| axum 0.7 -> 0.8 | Breaking API migration | Coordinated HTTP stack bump |
| redb 2.x -> 4.x | Major storage format migration | Staged rollout |
| hmac/sha2/hkdf 0.13 | Crypto crate family coordination | Synchronized bump |
| CI coverage gate | `ci.yml` has no llvm-cov step | CI pipeline evolution |

---

## For Upstream Overwatch

This handoff is ready for primalSpring review. Key items for upstream teams:

1. **sweetGrass/loamSpine**: rhizoCrypt mesh event types are stable —
   `TrustIssuerRegistered`, `KeyExchangeCompleted`, `FamilyEnrollment`,
   `MeshJoin`, `MeshLeave` are all covered at 100%
2. **bearDog**: `CapabilityVerifier` discovers `crypto:signing` providers;
   when JH-11 ships, replace `PresenceVerifier` fallback with Ed25519
3. **plasmidBin**: Dockerfile OCI label now `0.14.17`, musl-static build current
4. **sporePrint**: `sporeprint/validation-summary.md` updated for dispatch
5. **cellMembrane**: VPS_STATE.md still shows `v0.14.0` deployed — cascade
   will update deployed version

---

## Ecosystem Freshness

`wateringHole/freshness.toml` updated: `rhizoCrypt = "fd61ffc5..."` (Wave 118 HEAD)
