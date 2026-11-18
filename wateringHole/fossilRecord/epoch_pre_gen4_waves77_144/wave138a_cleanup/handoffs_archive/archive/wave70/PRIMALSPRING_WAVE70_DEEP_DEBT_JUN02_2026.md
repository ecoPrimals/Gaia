# primalSpring — Wave 70 Deep Debt Evolution Handoff

**Date**: 2026-06-02 (evening)
**Author**: eastGate
**Gate**: eastGate
**Spring**: primalSpring v0.9.31
**Metrics**: 836 tests, 0 clippy warnings, 0 unsafe blocks

---

## Delivered

### Security Evolution

| Change | Impact |
|--------|--------|
| `SecurityVerifier` denies on missing scopes | Was granting wildcard `["*"]` when BearDog omitted scopes — now returns `None` (deny) |
| `MethodGate::new(Enforced)` mode-aware | Was always permissive regardless of mode; now discovers SecurityProvider or installs DenyVerifier |
| `ProvenanceResult::unavailable` evolved | Uses `"degraded:"` prefix with structured context — no longer fabricates synthetic IDs |

### Production Mock Elimination

| Change | Impact |
|--------|--------|
| `handle_probe_primal` / `handle_probe_capability` | Real `Instant::now()` latency measurement (was hardcoded `latency_us: 0`) |
| `validate_composition_ctx` per-primal capabilities | Reports only capabilities owned by each primal (was broadcasting all caps to every entry) |

### Self-Knowledge & Capability Purity

| Change | Impact |
|--------|--------|
| `STARTUP_ORDER` from `Primal::ALL` | Single source of truth; cannot drift from enum definition |
| `leak_or_match` enum-driven | `Primal`/`Spring` `FromStr` parsing; compiler-enforced completeness |
| `static_fallback_caps` via `LazyLock` | Derives from `ALL_CAPS` routing table; cannot diverge from TOML-driven map |

### Modern Idiomatic Rust 2024

| Change | Impact |
|--------|--------|
| `#[allow(deprecated)]` → `#[expect(deprecated, reason)]` | Zero `#[allow]` in non-test production paths |
| 12 pre-existing clippy violations fixed | `let...else`, `map_or_else`, `f64::from()`, function split, `is_ok_and` |
| Large function refactored | `phase_manifest_schema` split via `validate_repo_entries` extraction |

### Housekeeping

- fossilRecord in-tree scripts cleaned (Wave 55b + 65 copies removed)
- README stale `web/play.html` reference removed
- wateringHole doc links corrected to `infra/wateringHole/` canonical paths
- CONTEXT.md + CHANGELOG.md updated to Wave 70

---

## Upstream Gaps Found (for overwatch teams)

### BearDog (southGate)
- `auth.verify_ionic` SHOULD return `scopes` array — primalSpring now denies when missing
- `bonding.propose` not implemented (certification skip in `certification/bonding.rs`)
- `crypto.sign` does not return `public_key` field (certification skip in `certification/btsp.rs`)

### biomeOS (southGate)
- `composition.reload` not implemented (certification skip in `certification/lifecycle.rs`)
- Missing scopes on `auth.verify_ionic` response triggers new deny behavior

### Compute Trio (biomeGate — PAUSED)
- `ml.mlp_train` on barraCuda needed for perceptron feature extraction (P2)
- Gate offline; resume trigger: kernel recovery

---

## Not Applicable (survey results)

| Category | Finding |
|----------|---------|
| Files >800 lines | None (largest: 775L) |
| Unsafe code | Zero (`#![forbid(unsafe_code)]` enforced) |
| External deps | All pure Rust, policy-compliant per deny.toml |
| TODO/FIXME/HACK | Zero |

---

## Next (P0 critical path)

1. Live mesh validation: `SONGBIRD_PEERS=<southGate>:7700` + `s_covalent_mesh` live run
2. DNS NS registrar cutover (operator action)
3. S4 auth gate completes ~Jun 9 (autonomous)

---

*Wave 70 deep debt complete. primalSpring is clippy-clean, security-hardened, and ready for mesh validation.*
