# biomeOS Wave 157a — Stage 2 Routing Infrastructure Handoff

**Date**: August 7, 2026
**Gate**: eastGate (overwatch + biomeOS code team)
**Wave**: 157a
**Author**: biomeOS code team (eastGate IDE session)

---

## Summary

Three structural evolutions shipped to biomeOS routing infrastructure for
Stage 2 Neural API activation readiness:

1. **riboCipher-aware connection pooling** — NUCLEUS primals receive `[0xEC, 0x01]` prefix through the hot dispatch path
2. **Bootstrap→Coordinated auto-transition** — background watcher eliminates permanent Bootstrap mode when Tower arrives late
3. **TOML-driven capability translations** — method tables load from `config/capability_registry.toml` at runtime, compiled defaults become fallback only

---

## Changes Shipped

| File | Lines | Description |
|------|-------|-------------|
| `crates/biomeos-core/src/ipc/pool.rs` | +105 | Dual pool lanes (plain + riboCipher), `send_ribocipher_jsonrpc()` |
| `crates/biomeos-atomic-deploy/src/neural_router/forwarding.rs` | +52 | `forward_request_ribocipher()`, auto-detect heuristic |
| `crates/biomeos-atomic-deploy/src/neural_api_server/server_lifecycle.rs` | +49 | Bootstrap→Coordinated probe loop (15s interval, 40 max) |
| `crates/biomeos-core/src/btsp_client/config.rs` | +9/-7 | Capability-first security socket resolution |
| `crates/biomeos-atomic-deploy/src/capability_translation/defaults.rs` | +11 | TOML-first loading with compiled fallback |
| `crates/biomeos-atomic-deploy/src/capability_translation/toml_loader.rs` | +190 (new) | Runtime TOML parser, env provider overrides, 3 tests |

**Total**: +207/-21 lines across 6 files (1 new).

---

## Verification

| Check | Result |
|-------|--------|
| `cargo check` | PASS |
| `cargo test` | 578 passed, 0 failed |
| `cargo fmt --check` | CLEAN |
| `cargo clippy --all-targets` | 0 warnings |
| `cargo check --target x86_64-pc-windows-gnu` | PASS (cross-arch) |
| `cargo doc --no-deps` | 0 warnings |

---

## Deep Debt Audit (full pass)

| Dimension | Status |
|-----------|--------|
| Unsafe code | ZERO (all crates `#![forbid(unsafe_code)]`) |
| External C deps | ZERO (`blake3 features=["pure"]`) |
| Mocks in prod | ZERO (all `#[cfg(test)]` gated) |
| Dead code | ZERO |
| `todo!()`/FIXME/HACK | ZERO |
| Files >800L | ZERO (max 731L) |
| `unwrap()` in prod | ZERO (workspace lint enforced) |
| Hardcoded primal names | Centralized in `primal_names.rs` + taxonomy |

---

## Self-Knowledge Violations Identified

The following are **documented but not all patched** (some are architectural trade-offs):

1. **`capability_translation/defaults.rs`** — hardcoded method tables. NOW secondary to TOML loading. Remains as cold-start fallback.
2. **`forwarding.rs` tarpc dispatch** (L404-510) — hardcoded service method switches for tarpc hot path. Glacial: evolve when L5 learned routing replaces L4.
3. **P2P/plasmodium callers** — use songBird wire protocol names. Acceptable: cross-membrane routing contract.
4. **BTSP `BEARDOG_SOCKET` legacy env** — NOW last in resolution order (capability-first).

---

## Architecture State

```
capability.call dispatch flow (Stage 2):

  Client → riboCipher consume → routing.rs
    → CapabilityHandler::call
      → signal tier? → graph execute (TOML-driven)
      → Tower Atomic? → pooled forward (riboCipher-aware)
      → translation? → registry (TOML-loaded) → pooled forward
      → direct discovery → pooled forward → mesh fallback
```

---

## Upstream Items for Primal Teams

| Item | Primal(s) | Description |
|------|-----------|-------------|
| N2 | All (primalSpring validates) | `capability.call` routes to bearDog through Neural API |
| N3 | bearDog+songBird+skunkBat | Tower Atomic routing via Neural API |
| N4 | rhizoCrypt+loamSpine+sweetGrass | Provenance Trio routing |
| N5 | squirrel | Agent routing via Neural API |
| riboCipher enforcement | sweetGrass, remote gates | Verify `send_ribocipher_jsonrpc` pool path works |

---

## Debris Identified (for archive review)

In `primals/biomeOS/`:
- `archive/` — 212K, contains Wave ≤150 legacy scripts. → fossilRecord candidate
- `tmp-cloud-init/` — 16K, cloud-init configs. → fossilRecord or remove
- `pixel8a-deploy/` — 136K, mobile deploy configs. → fossilRecord (active? lithoSpore?)
- `livespore-usb/` — 316K, genesis keys + README. → keep (security material)
- `target/` — **50 GB** → `cargo clean` candidate
- `secrets/` — primals/chimeras README. → verify not committed to git

---

## Next Steps

1. primalSpring team: N2-N5 activation tests
2. Overwatch: review debris list above, decide archive vs keep
3. Depot: redeploy v4.57+ to `depot.primals.eco` via Sovereign CI
4. Upstream: propagate `capability_registry.toml` pattern to other primals
