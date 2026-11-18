> **FOSSILIZED** — Wave 157k Enmeshment (Aug 16, 2026). Findings absorbed into ortho review + blurb.

<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# rhizoCrypt — Wave 157k Deep Interstadial AAR

**Date**: Aug 14, 2026 | **Wave**: 157k | **Gate**: westGate
**Primal**: rhizoCrypt (Ephemeral DAG Engine)
**Branch**: main (push to golgiBody for upstream audit)

---

## Summary

Deep debt sweep + rootPulse trio step handler activation. rhizoCrypt now
implements the two graph steps needed for biomeOS rootPulse trio activation
(`rootpulse_harvest` and `rootpulse_commit`). Parallel debt remediation
resolved all `#[allow]` suppressions, BTSP dead code, hardcoded ports,
primal name coupling, and coverage gaps.

## What Changed

### rootPulse Step Handlers (P2 Item #10 — PARTIAL)

| Handler | Graph | Wire Method | Behavior |
|---------|-------|-------------|----------|
| `rootpulse.record_build` | `rootpulse_harvest` | JSON-RPC | Creates deterministic DAG session (BLAKE3-derived UUID v7) or uses `pipeline_ingest`, appends `rootpulse.build_record` event, returns `{dag_ref}` |
| `rootpulse.dehydrate_state` | `rootpulse_commit` | JSON-RPC | Parses `SESSION_ID` + optional `AGENT_DID`/`FAMILY_ID`, calls tarpc `dehydrate`, returns `{dehydrated_blob, content_hash}` |

Files: `crates/rhizo-crypt-rpc/src/jsonrpc/handler/rootpulse.rs` (new),
`handler/mod.rs` (dispatch registration), `handler_tests_rootpulse.rs` (new, 6 tests).

### Semantic Aliases (P2 Item #11 — rhizoCrypt portion)

Added to handler dispatch + `PROVENANCE_ALIASES` + `primal.announce`:
- `dag.append` → `dag.event.append`
- `dehydrate` → `dag.dehydration.trigger`
- `dehydration.execute` → `dag.dehydration.trigger`

These resolve the "rhizoCrypt dehydration method not routed" gap identified
in westGate provenance trio experiments.

### Deep Debt Remediation

| Category | Before | After |
|----------|--------|-------|
| `#[allow]` in production | 5 suppressions | 0 (all evolved to `#[expect]`) |
| BTSP dead code (`dead_code`) | 3 `#[expect(dead_code)]` | 0 (version validated, pub stored, error logged) |
| Hardcoded test ports | Fixed ports (19400–19510 range) | Port-0 OS-assigned (zero CI collision) |
| Primal names in comments | ~30 hardcoded references | Capability-based language |
| Songbird localhost fallback | Contradictory docs | Corrected to `DiscoveryConfig::from_env()` |
| `LATENCY_BUCKETS` re-export | Unused downstream | Removed |

### Zero-Copy Vertex Hot Path

- `Vertex` gained `canonical_bytes: Option<Bytes>` cache
- CBOR encoding uses `BytesMut` with `freeze()` — zero realloc on serialized form
- `resolved_id()` + `with_known_id()` skip re-hashing on store reads
- Merkle leaf hashing uses cached IDs when available

### Coverage Improvements

| File | Before | After | What |
|------|--------|-------|------|
| `shutdown.rs` | 50% | ~85% | SIGTERM/SIGINT signal tests via `nix::sys::signal::kill` |
| `client.rs` | 81% | ~95% | `ServiceError::AddrParse` + `ServiceError::Config` error paths |
| `neural_api.rs` | 85% | ~95% | `primal.announce` lifecycle, missing socket, announce payload |

### Registry & Deploy

- `config/capability_registry.toml`: 40 → 42 methods, 7 → 8 domains (added `rootpulse`)
- `graphs/rhizocrypt_deploy.toml`: added `rootpulse.record_build`, `rootpulse.dehydrate_state` to capabilities
- `niche.rs` `METHOD_CATALOG`: 2 new `MethodSpec` entries
- `niche_derived.rs` `DOMAIN_DESCRIPTIONS`: added `rootpulse`
- `CONTRIBUTING.md`: added per wateringHole standards

## Metrics

| Metric | Value |
|--------|-------|
| Tests | 1,858 passing (`--all-features`) |
| Coverage | 92.69% lines, 91.16% functions (llvm-cov) |
| Clippy | 0 warnings (pedantic + nursery + cargo + cast) |
| Files | 231 `.rs`, ~62,620 lines |
| Max file | 752 lines (`handler_tests.rs`, limit: 800) |
| Binary | 5.7 MB musl-static |
| Unsafe | `deny` workspace-wide, zero blocks |
| `#[allow]` in production | 0 |
| Dead code | 0 |
| Deps | 270 unique (ecoBin compliant, `cargo-deny` clean) |

## Remaining Gaps (Upstream Teams)

### For biomeOS (eastGate)
- rootPulse trio graphs reference step handlers that other primals
  (nestGate, sweetGrass) have not yet implemented
- rhizoCrypt's handlers degrade gracefully (return structured errors if
  underlying tarpc methods are unavailable)

### For Neural API Translation Registry (P2 Item #11 — upstream)
- rhizoCrypt portion done (dehydration routing + aliases)
- Still needed: AEAD not surfaced in Neural API (bearDog team),
  `content.put` not in nestGate translation

### For sweetGrass (westGate)
- sweetGrass needs its own rootPulse step handlers for `rootpulse_diff`
  sovereignty verification
- Handoff filed: `SWEETGRASS_WAVE157K_DEEP_DEBT_ROOTPULSE_AUG14_2026.md`

## Files Changed (47 modified, 3 new)

### New
- `CONTRIBUTING.md`
- `crates/rhizo-crypt-rpc/src/jsonrpc/handler/rootpulse.rs`
- `crates/rhizo-crypt-rpc/src/jsonrpc/handler_tests_rootpulse.rs`

### Key Modified
- `crates/rhizo-crypt-core/src/vertex.rs` — zero-copy cache
- `crates/rhizo-crypt-core/src/niche.rs` — rootPulse METHOD_CATALOG entries
- `crates/rhizo-crypt-core/src/niche_derived.rs` — rootPulse domain + aliases
- `crates/rhizo-crypt-core/src/btsp_client.rs` — dead code resolution
- `crates/rhizo-crypt-rpc/src/jsonrpc/handler/mod.rs` — dispatch registration
- `crates/rhizo-crypt-rpc/tests/rpc_integration.rs` — ephemeral ports
- `crates/rhizocrypt-service/tests/binary_integration.rs` — ephemeral ports
- `crates/rhizocrypt-service/src/shutdown.rs` — signal tests
- `crates/rhizocrypt-service/src/client.rs` — error path tests
- `config/capability_registry.toml` — rootPulse entries
- `graphs/rhizocrypt_deploy.toml` — rootPulse capabilities

## Validation

```
cargo fmt --all --check         # PASS
cargo clippy --workspace ...    # 0 warnings
cargo test --workspace          # 1,858 passed, 0 failed
cargo llvm-cov --workspace      # 92.69% lines
cargo deny check                # advisories ok, bans ok, licenses ok, sources ok
cargo doc --workspace --no-deps # 0 warnings
```

---

*Wave 157k deep interstadial. rhizoCrypt rootPulse step handlers ACTIVE.
42 methods / 8 domains. 1,858 tests, 92.69% coverage. Zero `#[allow]`,
zero dead code, zero hardcoded ports, zero primal name coupling.
Ready for upstream audit.*
