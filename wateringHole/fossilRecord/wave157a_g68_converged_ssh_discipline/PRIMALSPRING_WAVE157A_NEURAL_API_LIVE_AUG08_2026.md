# primalSpring — Wave 157a Neural API Live + Cascade Ownership

**Date**: Aug 8, 2026
**Team**: primalSpring code team (eastGate)
**Wave**: 157a
**Commits**: `d1637327`, `0c1a3a2b`, `74d6eb30`, `67df1ebf`, `49fd0925`

## Summary

primalSpring now has **live Neural API integration** on eastGate hardware.
The biomeOS Neural API server is running with `--btsp-optional`, accepting
riboCipher dual-lane connections, executing graphs, and routing capabilities.

Additionally, primalSpring **owns the eastGate temporal cascade** per the
Wave 157a ownership model. The `scripts/temporal_cascade.sh` script
orchestrates pull → build check → sync graph → gate probe.

## What Was Delivered

### Neural API Experiments (live substrate)

| Experiment | Result | Key Metric |
|-----------|--------|-----------|
| exp118: Graph execution lifecycle | **12/14 PASS** | riboCipher protocol, graph.execute, graph.status timing |
| exp119: PathwayLearner structural | **12/12 ALL PASS** | 1,251 exec/s, CV=0.85 timing, 50 observations in 5.1s |
| exp120: SongBird self-registration | **29/29 ALL PASS** | 34 caps, 58 methods, 11/11 domain resolution |

### Validation Scenario

| Scenario | Track | Tier | Checks |
|----------|-------|------|--------|
| `s_neural_learning` | Lifecycle | Rust | ALL PASS |

Validates PathwayLearner structural prerequisites: graph observability,
parallelization opportunities, signal collapse measurability, method richness.

### Temporal Cascade Script

`scripts/temporal_cascade.sh` — primalSpring's cascade ownership mechanism:
1. Pulls from golgiBody (Forgejo)
2. Verifies workspace build health (`cargo check --workspace`)
3. Triggers `sync_diverge` graph via Neural API
4. Probes gate reachability via SSH

### Protocol Discovery

The biomeOS Neural API wire protocol was reverse-engineered and documented:

```
Connection: Unix domain socket
Protocol:   riboCipher dual-lane
Wire:       0xEC (signal) + 0x00 (tier) + JSON-RPC + \n
Response:   JSON-RPC + \n
```

Without `0xEC` prefix → "REJECTED: legacy connection (no riboCipher signal)"
per Wave 113 policy. This is now the canonical connection pattern for all
primalSpring Neural API interactions.

## Live Neural API State (eastGate)

```
Process:  biomeos neural-api --socket /run/user/1000/biomeos/biomeos-neural.sock --btsp-optional
Graphs:   55 loaded (from primalSpring/graphs/ recursive)
Caps:     34 capabilities, 58 methods (11 primals registered)
Mode:     Bootstrap (genesis)
Routing:  54 domains in routing table (incl. auto-discovery)
```

### Registered Primals (via primal.announce)

| Primal | Tier | Capabilities | Methods |
|--------|------|-------------|---------|
| beardog | tower | security, crypto, trust | 7 |
| songbird | tower | discovery, mesh, federation | 7 |
| skunkbat | tower | defense, firewall, intrusion | 4 |
| sweetgrass | nest | attribution, braid, convergence, provenance | 8 |
| rhizocrypt | nest | dag, session, provenance_dag | 5 |
| loamspine | nest | ledger, spine, commit | 5 |
| toadstool | node | compute, workload, shader | 5 |
| coralreef | node | rendering, gpu, display | 4 |
| barracuda | node | network, protocol, relay | 4 |
| squirrel | meta | ai, narration, mcp | 5 |
| petaltongue | meta | rendering_ui, input, proprioception | 4 |

## Upstream Gaps (biomeOS team)

### P1: capability.call forwarding timeout

`capability.call(crypto, sign_ed25519)` routes correctly (resolves beardog endpoint)
but **fails to forward** the JSON-RPC to the actual primal socket. Error:
```
Failed to forward crypto.sign_ed25519 to unix:///run/user/1000/biomeos/beardog-default.sock
```

The Neural API connects to beardog's socket but the request isn't understood
by beardog (it returns its health response for any unknown method). This is
a **biomeOS neural-api server** issue — the forwarding payload format doesn't
match what primals expect.

### P2: Socket naming convention mismatch

Neural API expects `{primal}-{family_id}.sock` but primals register as
`{primal}.sock` or `{primal}-default.sock`. Discovery works (auto-probe)
but forwarding breaks on the name mismatch.

### P3: PathwayLearner not wired to executor

Phase 3 structural prerequisites are met (exp119: 12/12 PASS) but biomeOS
has not yet wired `PathwayLearner` into the graph execution pipeline. The
`MetricsCollector` accumulates traces but no suggestions are generated.

### P4: Mesh not initialized error

`capability.call(mesh, peers)` returns "Mesh not initialized (call mesh.init first)".
songBird's mesh layer needs initialization before mesh capabilities are usable
via the Neural API routing path.

## Test Results

- 1,282 workspace tests (1,219 lib pass + 3 pre-existing env failures)
- 198 validation scenarios (15 tracks, 3 tiers)
- 98 experiments (21 tracks)
- 102+ graph TOMLs
- Zero new regressions

## What's Next

- **N6 validation**: Full graph execution through Neural API (blocked on P1 above)
- **Cascade automation**: `temporal_cascade.sh` → systemd timer for periodic sync
- **PathwayLearner wiring**: When biomeOS enables Phase 3, exp119 becomes the acceptance test
- **songbird-register.service**: Validate persistent registration across reboots (westGate pattern)
- **Cross-gate capability.resolve**: Validate resolution across mesh boundaries
