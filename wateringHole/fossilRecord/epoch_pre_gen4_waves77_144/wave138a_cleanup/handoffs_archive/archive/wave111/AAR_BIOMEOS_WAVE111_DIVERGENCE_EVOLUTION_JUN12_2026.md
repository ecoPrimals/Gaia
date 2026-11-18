# AAR: biomeOS — Wave 111 Divergence Evolution

**Date**: 2026-06-12  
**Team**: biomeOS  
**Wave**: 111  
**Stream 6 Score**: 2/2 SHIPPED (ALL COMPLETE)  
**Key Commits**: 249bce28 (v4.24), 8c310e1b (v4.25)

---

## Shipped (Stream 6 Divergence Scenarios — ALL COMPLETE)

### DISCOVERY-STALE-PRUNE (249bce28, v4.24)
- **Scenario**: Register a primal, let it die (no health response), verify biomeOS prunes it
- **Solution**: `unregister_primal()` + `prune_stale_registrations()` + `capability.prune` RPC + 60s background sweep
- **Pattern**: Registry is self-cleaning — dead primals are automatically purged
- **Deprecates**: Ghost registrations that accumulate until manual cleanup or restart

### ROUTING-PARTITION-AWARE (249bce28, v4.24)
- **Scenario**: Two primals on different segments, one segment unreachable
- **Solution**: `all_circuits_open()` detection → `try_registry_lookup` returns None on all-dead → `capability.call` tries mesh before hard error
- **Pattern**: Routing degrades gracefully — unreachable segments don't block the entire system
- **Deprecates**: Routing that blocks indefinitely waiting for dead peer response

---

## Additional Evolution (v4.25, 8c310e1b)

- Security fail-closed (default deny on unknown capabilities)
- Real metrics replacing placeholder counters
- Agnostic naming (no primal-specific strings in routing logic)
- Router refactor: neural router registry extracted to `neural_router/registry.rs`

---

## Old Patterns Deprecated by biomeOS Evolution

| Old Pattern | New Pattern | Since |
|-------------|-------------|-------|
| Ghost registrations persist after primal death | 60s sweep + capability.prune RPC | 249bce28 |
| Route blocks on unreachable peer | all_circuits_open → mesh fallback → graceful error | 249bce28 |
| Security fail-open (allow unknown capabilities) | Security fail-closed (deny unknown) | 8c310e1b |
| Hardcoded primal names in routing | Capability-based routing via registry | 8c310e1b |

---

## Convergence Criteria for biomeOS

1. ✅ All 2/2 divergence scenarios implemented and tested
2. ✅ Registry self-cleaning proven
3. ✅ Partition-aware routing proven
4. ⚠️ Needs validation under real partition (when flockGate WAN federation is live)

**biomeOS is convergence-ready.** No Stream 6 items remain. Real-world partition
validation will happen naturally when flockGate federation goes live with fresh binary.

---

## Test State

- All tests passing (v4.25)
- Zero clippy warnings
- Neural router registry cleanly extracted
