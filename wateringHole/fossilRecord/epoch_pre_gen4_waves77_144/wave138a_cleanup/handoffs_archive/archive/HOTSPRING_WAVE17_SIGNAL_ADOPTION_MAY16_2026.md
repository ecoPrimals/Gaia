# hotSpring Wave 17 Signal Adoption — May 16, 2026

**Sprint:** Wave 17 Signal Adoption (strandGate physics team)
**Spring:** hotSpring v0.6.32
**Archetype:** Compute-heavy (Node atomic dominant)

---

## Summary

hotSpring has adopted three Wave 17 neural API signals with automatic legacy fallback:

| Signal | Function | Fallback |
|--------|----------|----------|
| `primal.announce` | Single-call registration with all methods, capabilities, semantic mappings, signal tiers | `lifecycle.register` + N × `capability.register` |
| `node.compute` | GPU workload dispatch (compile → submit → execute) | `compile_and_submit()` multi-call |
| `tower.publish` | Signed result publication (sign → announce → audit) | `crypto.sign_ed25519` + `discovery.announce` |

Domain-specific physics operations (`stats.*`, `linalg.*`, `tensor.*`, `physics.*`)
remain as `ctx.call()` per the adoption standard.

## Next candidates

- `nest.store` for physics result provenance (content.put + dag + spine + braid)
- `nest.commit` for session finalization

## Metrics

- 595/595 lib tests pass
- Zero clippy warnings
- All signal paths have automatic fallback for older biomeOS

## Upstream asks

1. Confirm `primal.announce` wire field naming (`primal` + `socket` vs `primal_id` + `transport`)
2. Validate `node.compute` signal graph matches toadStool → coralReef → barraCuda pipeline
3. 13 hotSpring methods pending addition to primalSpring canonical registry (advisory)

## Files changed

- `barracuda/src/niche.rs` — `primal.announce` registration
- `barracuda/src/compute_dispatch.rs` — `node.compute` + `tower.publish`
- `barracuda/config/capability_registry.toml` — signal tier annotations
- `docs/PRIMAL_GAPS.md` — GAP-HS-103
- `CHANGELOG.md` — sprint entry
