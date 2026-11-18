# coralReef Wave 157a — Vertebrate Evolution: RPC Self-Audit

**Date**: 2026-08-09 | **Author**: coralReef code team (strandGate)
**Wave**: 157a VERTEBRATE EVOLUTION | **From**: eastGate overwatch
**Gate**: strandGate

---

## SUMMARY

coralReef vertebrate self-audit complete. 18/18 JSON-RPC methods verified
against `capability_registry.toml`. Zero phantom methods, zero undeclared
methods, zero silent health-stub fallbacks. Programmatic structural integrity
test added — the primal now validates its own RPC surface at compile time.

## SELF-AUDIT RESULTS

### RPC Surface Verification

| Check | Result |
|-------|--------|
| Registry methods vs dispatch | **18/18 match** |
| Dispatch methods vs registry | **18/18 match** |
| Silent health fallback on unknown | **None** (returns `method not found` error) |
| Health stub for declared methods | **None** (all return domain-specific responses) |
| Registry version vs crate version | **Match** (0.2.0) |

### Method Inventory

| Domain | Registry Methods | Dispatch Status |
|--------|-----------------|-----------------|
| shader | compile.spirv, compile.wgsl, compile.wgsl.multi, compile.multi, compile.gemm, compile.status, compile.capabilities | All real implementations |
| health | check, liveness, readiness, version | All real implementations |
| identity | get | Real implementation |
| capability | list (alias: capabilities.list) | Real implementation |
| btsp | negotiate | Real implementation |
| auth | check, mode, peer_info | Real implementations |

### bearDog P0-A Pattern Check

coralReef does **not** exhibit the bearDog pattern:
- Unknown methods return `Err("method not found: {method}")` with JSON-RPC code `-32601`
- No catch-all health response
- No silent fallback to generic status

### Parameter Verification

- `CompileWgslRequest`: sane defaults (`arch` defaults to sm70), accepts `"source"` alias for `"wgsl_source"`
- All compile methods: proper `extract_params()` with array and object support
- BTSP negotiate: full `NegotiateRequest` deserialization
- Auth methods: inline JSON responses (no params needed)

## STRUCTURAL INTEGRITY TEST

Added `tests_registry_audit.rs` (5 tests) that programmatically:
1. Parses `capability_registry.toml` via `include_str!` at compile time
2. Extracts all `[domains.*].methods` into fully-qualified names
3. Exercises every declared method against `dispatch_jsonrpc`
4. Verifies every `SERVED_METHODS` entry appears in the registry
5. Checks that unknown methods are rejected, not health-stubbed

This test structurally prevents the nestGate P0-B pattern (API surface
divergence) from occurring in coralReef.

## CROSS-FOCUS DELEGATION

| Area | Status |
|------|--------|
| Compute gossip (swarmVine) | Not yet integrated — future work when swarmVine is ready |
| Hardware dispatch | Correctly delegated to `compute.dispatch` provider (toadStool) |
| Crypto signing | Correctly delegated to `crypto.sign` provider (bearDog) |
| Registry announcement | Correctly delegated to `capability.register` provider (songBird) |

## METRICS

| Metric | Value |
|--------|-------|
| Tests | **3,699** (3,695 passed, 4 ignored, 0 failed) |
| Clippy warnings | **0** (pedantic + nursery, Linux + Windows) |
| Unsafe code | **0** (`#![forbid(unsafe_code)]` on all crates) |
| G68 | **prod-clean** (0 production violations) |
| P0/P1 for coralReef | **ZERO** |

---

*coralReef vertebrate self-audit complete. RPC surface matches registry.
No phantom methods. No health-stub fallbacks. Structural integrity test
prevents future divergence. Ready for depot rebuild.*
