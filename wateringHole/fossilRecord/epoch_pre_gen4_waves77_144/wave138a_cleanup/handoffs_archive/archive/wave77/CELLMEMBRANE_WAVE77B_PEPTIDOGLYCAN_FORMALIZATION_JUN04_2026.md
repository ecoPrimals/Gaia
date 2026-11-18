# cellMembrane Wave 77b — Peptidoglycan Formalization

**Date**: 2026-06-04  
**Wave**: 77b  
**Gate**: ironGate  
**Team**: cellMembrane evolution  
**Status**: DELIVERED

---

## Summary

Formalized the peptidoglycan layer as a first-class composition type in
the cellMembrane type system. The peptidoglycan is the diderm trust barrier
between outer membrane (primals.eco) and inner membrane (primal.eco).

---

## Delivered

### 1. `MembraneComposition::Peptidoglycan` Variant

- Added to `crates/cellmembrane-types/src/composition.rs`
- Role variant — NOT part of the monotonic ladder
- `PartialOrd` returns `None` when comparing with ladder tiers
- `Ord` removed from derive (manual `PartialOrd` preserves ladder ordering)
- Channels: relay only
- `requires_tower_env` = true
- `stores_data` = false
- `is_trust_barrier` = true
- `is_ladder` = false
- `all_variants()` includes it; `all()` excludes it (ladder-only)

### 2. `TrustBarrierConfig` Struct

- Added to `crates/cellmembrane-types/src/config.rs`
- Fields: `inner_domain`, `outer_domain`, `opaque_relay`, `content_domain`
- Optional on `MembraneConfig` (only relevant for peptidoglycan)
- Serde-driven with `default_true` for `opaque_relay`

### 3. Trust Barrier Contract Documentation

- Appended to `specs/FIELDMOUSE_CONTRACT.md`
- Sections: Configuration, What It Relays, What It Cannot See, What It Stores,
  Invariants, Discovery, Validation
- Updated Deployment Classes table to include peptidoglycan

### 4. Tests

- `peptidoglycan_composition_parses` — full TOML round-trip
- `peptidoglycan_channels_are_relay_only` — channel validation
- `peptidoglycan_not_in_ladder_ordering` — PartialOrd returns None
- `ladder_ordering_preserved` — existing ladder still works

---

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| Tests | 210 | 214 |
| Clippy warnings | 0 | 0 |
| `#[allow]` in production | 0 | 0 |
| Compositions | 5 (ladder) | 6 (5 ladder + 1 role) |

---

## Design Decisions

1. **Role variant vs. ladder tier**: Peptidoglycan doesn't fit the monotonic
   superset model. It's not "more" than relay — it's a *different purpose*.
   Making it a role variant preserves `PartialOrd` semantics for ladder
   compositions while expressing its unique trust barrier contract.

2. **Removed `Ord` derive**: Since `PartialOrd` is no longer total (peptidoglycan
   is incomparable), `Ord` cannot be derived. Code that needs total ordering
   should use `ladder_rank()` directly.

3. **`requires_tower_env` = true**: Even though peptidoglycan doesn't run BTSP,
   it needs `tower.env` for relay identity/credentials (Songbird TURN auth).

---

## Blocker

| ID | Status | Owner | Impact |
|----|--------|-------|--------|
| `dns-ns-cutover` | Pending | Operator | Caddy reverse proxy wiring blocked until Porkbun NS records point to sovereign nameservers |

---

## Next Steps (Post-Cutover)

- Caddy vhost wiring: `primal.eco` → inner membrane, `nestgate.io` → NestGate CAS
- Validate `deploy_membrane.sh --composition peptidoglycan` end-to-end
- Test teardown + reprovision cycle (inner membrane rediscovery)
