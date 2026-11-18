# cellMembrane Wave 157a — Registry Evolution + Smart Refactor

**Date:** 2026-08-08
**Commit:** `c9971d4`
**Pushed to:** `git.primals.eco:sporeGarden/cellMembrane.git`

---

## 1. Self-Knowledge Elimination — Registry-Derived Trust

### Problem
Six production sites hardcoded primal binary name lists, bypassing the service registry:
- `SPOREPRINT_NUCLEUS_BINARIES` — 4 hardcoded names
- `POST_PRIMORDIAL_PRIMALS` — 6 hardcoded names
- `GPU_PRIMALS` — 2 hardcoded names

### Solution
Added two semantic fields to `MembraneService` registry:
- `requires_signed_lineage: bool` — post-primordial trust policy
- `gpu_required: bool` — glibc/dlopen build requirement

All three hardcoded constants eliminated:
- `is_post_primordial()` → checks registry `requires_signed_lineage` flag
- `is_gpu_primal()` → checks registry `gpu_required` flag
- `gateway/mod.rs` sporePrint deploy check → derives from `ServiceCapability` lookups

### Registry Flags

| Primal | requires_signed_lineage | gpu_required |
|--------|------------------------|--------------|
| beardog | true | false |
| songbird | true | false |
| skunkbat | true | false |
| nestgate | true | false |
| biomeos | true | false |
| barracuda | false | true |
| coralreef | false | true |
| (all others) | false | false |

Note: "cellmembrane" is not in the service registry (it IS the membrane), but `is_post_primordial("cellmembrane")` returns `true` via explicit guard.

---

## 2. Smart Refactor — service/mod.rs (855→556L)

Extracted two focused modules from the monolithic `service/mod.rs`:

| Module | Lines | Contents |
|--------|-------|----------|
| `ipc.rs` | 131 | `IpcProtocol` enum, G65 negotiation constants, wire format |
| `capability.rs` | 234 | `Protocol`, `TransportMode`, `ServerContract`, `ServiceCapability`, `HealthCheckMethod` |
| `mod.rs` (remaining) | 556 | `MembraneService` struct + impls, `ServicePaths`, registry re-exports |

All public API unchanged — re-exports maintain backward compatibility.

---

## 3. Modern Idiomatic Rust

### Let-chains (Rust 2024)
- `git_ops.rs:15-21` — triple-nested `if let Ok` → single let-chain
- `freshness.rs:227-239` — quad-nested file reading → let-chain

### Idiom fixes
- `dns/mod.rs:296` — `&String` → `&str` via `.map(|(k,v)| (k.as_str(), v))`

### Silent error debug logging
Replaced `.ok()?` with `match` + `tracing::debug` at:
- `bridge.rs` — NeuralBridge RPC call + response parse + error result
- `gate/health.rs` — crash-loop scan spawn + TLS cert manifest load
- `tower/timer.rs` — mesh probe songbird RPC + response parse
- `sync_ipc.rs` — UDS connect failure

---

## Metrics

| Metric | Value |
|--------|-------|
| Tests | 1329 (all pass) |
| Clippy warnings | 0 |
| Compiler warnings | 0 |
| Files changed | 17 |
| Lines added | 603 |
| Lines removed | 404 |

---

## Remaining Gaps

- `ribocipher.rs` — 15× `#[allow(dead_code)]` for Tier 2/3 (spec-complete, not wired)
- `transport.rs` — 3× `#[allow(dead_code)]` for G66 future API
- `manifest/mod.rs` — 9× `#[allow(dead_code)]` for manifest API surface
- `NEURAL_API_NAMESPACE = "biomeos"` — filesystem directory convention, not self-knowledge
- `TlsProvider::BearDog` — enum wire format, not binary name lookup
