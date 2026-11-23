# sporeGate → eastGate: KNOWN_DEBT Flapping on sporeGate

**Date**: Jul 25, 2026 | **Wave**: 150x | **From**: sporeGate topology team
**To**: eastGate primalSpring team

---

## Summary

KNOWN_DEBT calibrated from flockGate (`1e809eb`) does not align with
sporeGate's environment. The upstream values work for flockGate/eastGate but
produce consistent failures on sporeGate. Two categories:

### 1. Persistent sporeGate-specific debt (deterministic)

| Scenario | flockGate value | sporeGate value | Reason |
|----------|-----------------|-----------------|--------|
| `graphenegate-readiness` | 14 | 2 | sporeGate has partial aarch64 depot; flockGate has none |
| `sporeprint-pure-primal-parity` | 0 (passes) | 1 | sporeGate has Zola build env, eastGate doesn't |
| `arch-fitness` | 1 | 0 | Passes on sporeGate |
| `mesh-reachability` | 1 | 0 | Passes on sporeGate |

### 2. Tower stress/pen scenarios (non-deterministic)

These scenarios flap between 0 and their "expected" values depending on test
ordering and timing in the full suite:

- `tower-stress-btsp-storm`: flaps 0↔1
- `tower-stress-failover-resilience`: flaps 0↔3
- `tower-stress-uds-hop-cost`: flaps 0↔1
- `tower-pen-capability-escalation`: flaps 0↔1
- `tower-pen-cipher-downgrade`: flaps 0↔1
- `tower-pen-uds-spoof`: flaps 0↔1
- `tower-pen-mesh-poison`: flaps 0↔1
- `mesh-lan-path-preference`: flaps 0↔2

**No static KNOWN_DEBT value works** — `assert_eq!` fails whether the value
is 0 (fails when non-determinism produces failures) or N (fails when the
scenario passes clean).

### 3. Root cause

The `registry_all_rust_tier_pass` test uses `assert_eq!(v.failed, expected)`
which requires exact match. For timing-sensitive scenarios, the failure count
is non-deterministic. The same scenario produces different results:
- In isolation: usually 0 (passes clean)
- In full suite: sometimes 0, sometimes N (resource contention, socket reuse,
  timing windows)

### 4. Recommendation

Consider one of:
1. **Range-based debt**: `assert!(v.failed <= max_expected)` for flappy scenarios
2. **Per-gate calibration**: `#[cfg]` or env-based KNOWN_DEBT selection
3. **Exclude flappy scenarios** from `registry_all_rust_tier_pass` and validate
   them in a separate `#[ignore]` or `--include-flaky` test

### 5. Evidence

Ran 8+ full suite iterations on sporeGate. No single KNOWN_DEBT configuration
produces consistent passes. The isolated test (`-- registry_all_rust_tier_pass`)
has different behavior than the full suite due to test-ordering effects.

iperf3 confirmed 2.36 Gbps sporeGate→eastGate. SSH works via `eastgate@192.168.4.244`.
biomeos-beacon removed. All bilateral blockers confirmed clear.

---

*sporeGate topology team stepping back from KNOWN_DEBT calibration.
eastGate primalSpring team owns this. We'll continue to run overwatch
and report divergences.*
