# primalSpring v0.9.36 — Wave 137b Evolution Handoff

**Date**: 2026-07-12 | **Wave**: 137b | **From**: primalSpring overwatch (eastGate)

## Delivered

### New Scenarios (+3, total 141)

| Scenario | Track | Validates |
|----------|-------|-----------|
| `neural-api-lifecycle` | Infrastructure | lifecycle.* routing to biomeOS, discovery domain, systemd promotion readiness, primal count expectations, live probe |
| `cross-gate-mesh-deploy` | Transport | Bidirectional federation: multi-gate participation, songBird composition coverage, port parity, version coordination, Neural API multi-gate targeting |
| `socket-directory-unification` | Infrastructure | /run/membrane/ canonical, /run/biomeos-root/ legacy awareness, naming convention (primal-{name}-{family_id}.sock), config consistency |

### Cleanup

- Removed orphan scenario files from parallel session (`s_lifecycle_registration`, `s_socket_dir_unification`) — superseded by better-named and more thorough scenarios above

### Metrics

| Metric | Value |
|--------|-------|
| Version | 0.9.36 |
| Tests | 1,131 pass / 0 fail |
| Scenarios | 141 (12 tracks, 3 tiers) |
| Clippy | zero warnings |
| Wave config | 137b |

## Upstream Gaps Surfaced (from 137b blurb)

These are validated structurally — upstream teams should execute:

| Gap | Owner | Validation Scenario |
|-----|-------|---------------------|
| NAPI-SYSTEMD: promote Neural API to systemd service | sporeGate | `neural-api-lifecycle` validates watchdog methods |
| NAPI-LIFECYCLE: LifecycleManager registration (count=0) | biomeOS | `neural-api-lifecycle` validates lifecycle.register routing |
| GOLGI-WG-BIND: songBird on golgi bind 10.13.37.1:7700 | golgi/sporeGate | `cross-gate-mesh-deploy` validates port parity |
| NAPI-CROSS-GATE: deploy songBird f05918a to sporeGate+eastGate | all gates | `cross-gate-mesh-deploy` validates version coordination |
| SOCKET-DIR-UNIFY: unify /run/membrane/ and /run/biomeos-root/ | biomeOS | `socket-directory-unification` validates convergence |

## Architecture Notes

- `neural-api-lifecycle` uses the `NeuralRoutingTable` to verify lifecycle methods route to biomeOS and discovery routes to songBird
- `cross-gate-mesh-deploy` validates the freshness tracking infrastructure (now wave.toml + heads/*.toml pattern) for cross-gate version parity
- `socket-directory-unification` validates that `NUCLEUS_SOCKET_SUBDIR` env key and `nucleus_socket_dir()` resolve consistently

---

*primalSpring overwatch: Neural API live state validated. Cross-gate mesh gaps quantified. Socket unification path validated. Cascade pushed.*
