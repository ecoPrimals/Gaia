# rhizoCrypt — Wave 157a Vertebrate Self-Audit

**Date**: Aug 9, 2026
**Wave**: 157a — Vertebrate Evolution (primal self-audit)
**Primal**: rhizoCrypt v0.14.17

## Self-Audit Results

Three-way comparison: `capability_registry.toml` vs `METHOD_CATALOG` (niche.rs) vs handler dispatch (handler/mod.rs).

### Divergence 1: `dag.session.tree_hash` — undeclared capability
- **Finding**: Fully implemented (handler dispatch, tarpc trait, METHOD_CATALOG) but missing from `capability_registry.toml`
- **Impact**: biomeOS/songBird discovery would not advertise this capability; consumers couldn't discover it via `capability.resolve`
- **Fix**: Added to registry with `domain = "dag.merkle"`, `stability = "stable"`

### Divergence 2: `lifecycle.status` — phantom method
- **Finding**: Listed in `method_gate.rs` PUBLIC_METHODS and `newline.rs` BTSP-exempt allowlist, but no handler dispatch arm exists. Any call returns `-32601 Method not found`.
- **Impact**: Same class of bug as bearDog P0-A (health-only stub) and nestGate P0-B (phantom API). Consumers could classify it as public and attempt calls, receiving errors.
- **Fix**: Removed from PUBLIC_METHODS, BTSP-exempt list, and test assertion

### Divergence 3: `dag.dehydrate` — legacy alias (no action)
- **Finding**: Dispatched as alias for `dag.dehydration.trigger`, not in METHOD_CATALOG separately
- **Impact**: None — correct behavior. Legacy wire name mapped at dispatch, canonical name in registry.

## Post-Audit State

| Metric | Before | After |
|--------|--------|-------|
| Registry methods | 39 | **40** |
| METHOD_CATALOG entries | 40 | 40 |
| Handler dispatch methods | 40 | 40 |
| Phantom methods | 1 (`lifecycle.status`) | **0** |
| Undeclared methods | 1 (`dag.session.tree_hash`) | **0** |
| Parity | 3 divergences | **Full parity** |

## Verification

```
cargo clippy --workspace --all-features -- -D warnings  # clean
cargo test --workspace --all-features                    # 1,825 pass, 0 fail
cargo fmt --check                                        # clean
cargo check --target x86_64-pc-windows-gnu               # clean
```

## Files Changed

| File | Change |
|------|--------|
| `config/capability_registry.toml` | Add `dag.session.tree_hash` entry |
| `crates/rhizo-crypt-rpc/src/jsonrpc/method_gate.rs` | Remove `lifecycle.status` from PUBLIC_METHODS |
| `crates/rhizo-crypt-rpc/src/jsonrpc/newline.rs` | Remove `lifecycle.status` from BTSP-exempt list |
| `crates/rhizo-crypt-rpc/src/jsonrpc/method_gate_tests.rs` | Remove phantom assertion |
| `CHANGELOG.md` | Add Wave 157a Vertebrate Self-Audit entry |
| `CONTEXT.md` | Update method count (39 → 40) |
| `sporeprint/validation-summary.md` | Update method count, add tree_hash domain row |

## Lessons for Ecosystem

1. **Registry-handler parity must be enforced** — `dag.session.tree_hash` was implemented months ago but never registered. A CI check comparing registry vs METHOD_CATALOG would catch this.
2. **Phantom allowlist entries** — `lifecycle.status` was in two allowlists with no implementation. Allowlists should be derived from actual dispatch, not maintained separately.
3. **westGate was right** — silent API divergence happens even in well-maintained primals. Self-audit found 2 divergences in rhizoCrypt (one phantom, one undeclared). The vertebrate mandate is correct.
