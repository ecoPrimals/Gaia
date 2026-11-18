# Convergence Target: Proactive Topology Detection via Tower Atomic

**Wave**: 133c
**From**: sporeGate (hardware/topology sovereignty)
**To**: overwatch (primalSpring), skunkBat team, songBird team
**Priority**: P2 — architectural evolution, no immediate deadline
**Status**: PROPOSED — design validated, implementation phases defined

---

## Context

During the Sovereign Relay Architecture deployment (Wave 133b), a service prune on golgi accidentally deleted RustDesk binaries, breaking remote access to all gates. Root cause: no cross-layer detection noticed that a critical service vanished. skunkBat's behavioral baseline was not wired to receive live mesh telemetry, so structural changes to the relay went undetected.

Separately, a community post demonstrated Bayesian Persistent Landscapes (TDA) for proactive network failure prediction on a home router. The technique — multi-layer point cloud analysis with cross-model agreement monitoring — maps directly to our Tower Atomic architecture, though at our mesh scale (5-10 gates), simpler statistical methods outperform full TDA.

## Proposal: Cross-Layer Structural Drift Detection

Wire skunkBat's existing behavioral baseline profiler to automatically ingest telemetry from songBird mesh health and cascade sync results. Enable cross-layer correlation so that drift detected simultaneously in multiple observability layers is escalated, while single-layer drift is logged for context.

### Data Layers Already Available

| Layer | Source | Data | Frequency |
|-------|--------|------|-----------|
| Mesh health | songBird `mesh.health_probe` | Per-peer RTT, connection state, reachability | Every health probe cycle |
| Cascade sync | `temporal.cascade` post-sync | Repos synced/failed, sync duration, freshness age | Every 15min (cascade timer) |
| Service composition | `rootpulse` / biomeOS Neural API | Per-gate service status, primal count, memory/disk | On-demand via IPC |
| WireGuard tunnel | `wg show` metrics | Handshake age, transfer bytes, endpoint drift | Pollable |
| Gate identity | bearDog `lineage.verify` | Crypto identity validity, BTSP session health | On BTSP handshake |

### What skunkBat Already Has

- `baseline.observe` — accepts `Observation` structs (connection rate, traffic volume, ports)
- Statistical profiler with sigma-deviation and rolling window
- Six threat categories including **Topology** and **Behavioral**
- `security.detect` — on-demand threat assessment across all categories
- JH-5 audit log with federation broadcast to songBird
- `examples/monitoring_loop.rs` — pattern for periodic scan (not wired to production)

### What's Missing (The Gap)

1. **No automatic feed**: `baseline.observe` requires manual IPC calls. Nothing automatically pushes songBird mesh health or cascade results into skunkBat's profiler.
2. **No cross-layer correlation**: Each threat category runs independently. A gate drifting in both mesh latency AND behavioral profile simultaneously should escalate, but the categories don't cross-reference.
3. **No proactive response**: Detection is passive — it logs and alerts but doesn't trigger songBird route deprioritization or cascade verification.

## Implementation Phases

### Phase 1: Automatic Baseline Feed (cellMembrane + skunkBat)

Wire live telemetry into skunkBat's `baseline.observe`:

- **songBird → skunkBat**: After each `mesh.health_probe`, songBird pushes per-peer RTT observations to skunkBat's UDS socket via `baseline.observe`
- **cascade → skunkBat**: `temporal.cascade` post-sync phase pushes sync success/failure/duration as observations
- **Implementation**: Add a `telemetry_forward` background task in songBird that calls `baseline.observe` on the skunkBat socket after each probe cycle. Similar for cascade in `post_sync.rs`.

### Phase 2: Cross-Layer Correlation (skunkBat core)

Add a `MeshDrift` detection subcategory to the Topology threat detector:

- Compare songBird peer health anomaly score × skunkBat behavioral anomaly score
- **Both drift**: escalate (gate is actually degrading)
- **Mesh only**: log (network transient — WG rekey, route change)  
- **Behavioral only**: log (application-level change — deploy, config update)
- **Neither**: silence (the Reddit poster's "confidence through silence")

This is the cross-layer product scoring approach — simpler than TDA, validated at small mesh scales.

### Phase 3: Shadow Agreement Monitor (skunkBat core)

Implement the "shadow monitor" pattern from the TDA research:

- Run two independent anomaly scorers on the observation stream (e.g., EWMA vs rolling z-score)
- Track the gap between their outputs over time
- Alert when the gap oscillates — this catches subtle structural changes that neither scorer alone would flag
- Runs every 30 minutes, reads from existing baseline data, zero additional network traffic

### Phase 4: Proactive Response (Tower Atomic integration)

Connect detection to action via the existing `defense.respond` pipeline:

- skunkBat detects gate degrading → calls songBird `federation.deprioritize` to reduce traffic to that peer
- skunkBat detects sync staleness → triggers `temporal.cascade --force` on the affected repos
- skunkBat detects service disappearance (like the RustDesk incident) → alerts via federation broadcast with severity >= Warn

## Why NOT Full TDA

At our mesh scale (5-10 gates), persistent homology adds complexity without adding signal:

- 26 nodes in 4D feature space is too sparse for stable topological features
- Normalization sensitivity: 2.5% scaling drift can cascade into false landscape flips
- Per-gate z-scores with EWMA and cross-layer product scoring catch the same signals
- If mesh grows to 50+ gates, TDA starts earning its keep — revisit then

The simpler statistical methods already in skunkBat's profiler are the right foundation. We're adding wiring and correlation, not new math.

## Dependencies

| Dependency | Owner | Status |
|------------|-------|--------|
| songBird `mesh.health_probe` RTT data | songBird team | EXISTS — just needs IPC forwarding |
| skunkBat `baseline.observe` IPC | skunkBat team | EXISTS — needs automatic feed |
| `temporal.cascade` post-sync hooks | cellMembrane team (sporeGate) | EXISTS — `post_sync.rs` extensible |
| songBird `federation.deprioritize` | songBird team | DOES NOT EXIST — Phase 4 |
| skunkBat cross-category correlation | skunkBat team | DOES NOT EXIST — Phase 2 |

## primalSpring Resilience Tests

- **auto_baseline_feed**: Verify songBird mesh probes arrive in skunkBat baseline within 60s
- **cross_layer_escalation**: Inject simultaneous mesh + behavioral drift, verify escalation
- **single_layer_silence**: Inject mesh-only drift, verify no escalation (log only)
- **shadow_agreement**: Verify two scorers track each other under stable conditions, diverge under drift
- **service_disappearance**: Stop a service on a gate, verify skunkBat detects composition change

## Reference

- Reddit: "Adding topological analysis to my Linux router made it predict network failures" (r/homelab, Jul 2026)
- Bayesian Persistent Landscapes: `bpl_v1_posterior_band` with Matérn 2.5 GP prior
- skunkBat behavioral profiler: `crates/skunk-bat-core/src/threats/behavioral.rs`
- songBird health probing: `crates/songbird-universal-ipc/src/handlers/mesh_handler/health_probing.rs`
- cascade post-sync: `crates/membrane-shadow/src/temporal/post_sync.rs`
