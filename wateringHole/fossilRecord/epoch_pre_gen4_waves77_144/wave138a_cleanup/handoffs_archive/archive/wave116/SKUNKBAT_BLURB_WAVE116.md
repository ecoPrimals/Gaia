# skunkBat — Wave 116 Handoff Blurb

**Date**: Jun 19 2026 | **From**: flockGate (eastGate overwatch)
**Version**: 0.2.10 | **Tests**: 466 passing | **Source**: 50 files
**Atomic Role**: Tower (BearDog + Songbird + SkunkBat) — perimeter defense, WAN anomaly detection

---

## What skunkBat Is

Defensive network security primal. Metadata-only reconnaissance, 5-type threat
detection, graduated defense, audit trail forwarding. Content inspection is
structurally impossible (`forbid(unsafe_code)`, no packet payload access).

## Current State (Post Deep-Debt Session)

### Completed

- **riboCipher Tier 1**: `0xEC` + protocol type byte routing implemented and tested
- **ThreatThresholds**: All detection constants configurable via `SkunkBatConfig.thresholds`
- **Intrusion detection**: Port-scan and data-exfiltration heuristics wired
- **Sovereignty cleanup**: Zero hardcoded primal names in production routing —
  all discovery via `DISCOVERY_SOCKET`, `NEURAL_API_SOCKET`, capability conventions
- **Silent error elimination**: BTSP handshake, HKDF, NestGate integrity sweep
  all log failures (were silently swallowed)
- **Panic elimination**: `Timestamp::now()` non-panicking fallback
- **Clone reduction**: `dispatch()` hot path passes `id` by ref to gate, by value
  to sub-dispatchers
- **Code size**: All files under 1000L. `dispatch.rs` refactored (862→430L,
  tests extracted to `dispatch_tests.rs`)
- **Chaos tests wired**: 9 fault-injection tests now in `Cargo.toml` (were orphaned)
- **Example accuracy**: `beardog_integration.rs` and `songbird_integration.rs`
  updated to reflect real API surface (`RemoteLineageVerifier`, real config fields)

### What Upstream Teams Need to Know

| Topic | Details |
|-------|---------|
| **BTSP** | Phase 1/2/3 complete. `btsp.negotiate` + `btsp.capabilities` stable. ChaCha20-Poly1305 AEAD framing. Aligned with BearDog v0.9.0 reference. |
| **Wire Standard** | L2 (`capabilities.list`) + L3 (`identity.get`) compliant. 18 methods, all Stable tier. |
| **riboCipher** | Tier 1 only (`0xEC` clear signal). Tiers 2/3 (`0xED`/`0xEE`) reject with log — waiting on upstream spec finalization. |
| **Discovery** | Capability-based only. `DISCOVERY_SOCKET` or `discovery-{FAMILY_ID}.sock`. No primal name assumptions. |
| **Audit Forwarding** | Warn+ events → `dag.event.append` (provenance) + `braid.create` (attribution). UDS or `RHIZOCRYPT_ENDPOINT`/`SWEETGRASS_ENDPOINT`. |
| **Degradation** | skunkBat down = audit gap + no threat detection. Other primals unaffected. BearDog down = lineage degrades to conservative local deny. |

### Known Gaps (for upstream review)

1. **CI scope**: `ci.yml` runs `cargo test --workspace --lib --bins` — does NOT
   run integration tests or chaos tests. Consider `--tests` for full coverage.
2. **Design-phase specs**: `THYMIC_SELECTION_SPEC.md` and `COMPOSABLE_PRIMITIVES_SPEC.md`
   are forward-looking (not implemented). Not debt — intentional roadmap.
3. **`#[allow(dead_code)]` in transport**: `BondType`, `minimum_cipher()`,
   `SessionState.created_at`, `SessionRegistry.remove()` — reserved for
   BTSP Phase 2 bond-type enforcement and session TTL. Not stale.
4. **Legacy NDJSON bypass**: `{` first-byte peek path emits deprecation warning.
   Intentional migration aid, not permanent.
5. **Test coverage metric**: `cargo llvm-cov` not yet integrated into CI.
   Manual runs show good coverage but no enforced gate.

### What We Need From Upstream

- **BearDog team**: Confirm `lineage.verify` / `lineage.list` method stability.
  skunkBat's `RemoteLineageVerifier` targets these. Any breaking changes need
  coordination.
- **Songbird team**: Confirm `federation.broadcast` wire format. skunkBat's
  `FederationThreatBroadcaster` sends threat signatures on this method.
- **primalSpring**: Review riboCipher Tier 2/3 spec readiness. skunkBat rejects
  these today — ready to implement when spec stabilizes.
- **cellMembrane**: Validate `security.sock` domain symlink convention for
  composition-level service discovery.

---

## Quick Verify

```bash
cd primals/skunkBat
cargo fmt --all -- --check   # clean
cargo clippy --workspace -- -D warnings  # 0 warnings
cargo test --workspace       # 406 passed, 0 failed
cargo doc --no-deps          # clean
cargo deny check             # pass (ring banned)
```
