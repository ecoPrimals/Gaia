# Composition Tick Model Standard

**Version:** 1.0.0
**Date:** April 27, 2026
**Audience:** Springs, gardens, biomeOS, and any composition with temporal requirements
**Status:** Active Standard
**License:** AGPL-3.0-or-later

---

## Purpose

Different domains have fundamentally different temporal requirements:

- **Games** need 60Hz fixed-timestep ticks
- **Physics** needs convergence-driven iteration (variable step, halt on convergence)
- **ML inference** needs event-driven polling (respond when ready)
- **Agriculture** uses seasonal time steps (daily/weekly/monthly)
- **Health** uses convergence checks on clinical thresholds
- **Uncertainty** needs Monte Carlo iteration counts

When biomeOS manages a heterogeneous cell graph — a game UI running over
a physics simulation with provenance recording — these temporal models must
coexist. This standard defines how domains declare their temporal requirements
and how the composition engine adapts.

---

## Tick Classes

Every node in a deploy graph operates under one of five temporal classes.

| Class | Description | Trigger | Budget | Examples |
|-------|-------------|---------|--------|----------|
| **Continuous** | Fixed-timestep loop | Timer (Hz) | Per-frame ms budget | Game ticks (60Hz), animation, sensor polling |
| **Convergence** | Iterate until criterion met | State change | Per-iteration limit | Physics equilibrium, optimization, PK/PD steady-state |
| **Event** | Respond to discrete signals | IPC message | Response timeout | AI inference, user interaction, provenance commit |
| **Batch** | Process a dataset to completion | Data availability | Total wall-clock | ETL, validation suites, cross-spring benchmarks |
| **Seasonal** | Calendar or domain-period driven | Time interval | Period budget | Water balance (daily), crop cycle (weekly), audit (monthly) |

---

## Declaration in Deploy Graphs

### Continuous Tick

For nodes requiring fixed-timestep execution, declare in the graph header:

```toml
[graph]
name = "game_engine_tick"
coordination = "continuous"

[graph.tick]
target_hz = 60
max_frame_ms = 16
underrun_policy = "skip"    # "skip" | "catchup" | "warn"
```

Per-node tick budgets:

```toml
[[graph.node]]
name = "game_logic"
binary = "ludospring"
order = 3
health_method = "health.liveness"
by_capability = "game"
tick_method = "game.tick"
budget_ms = 8

[[graph.node]]
name = "render"
binary = "petaltongue"
order = 4
health_method = "health.liveness"
by_capability = "visualization"
tick_method = "render.frame"
budget_ms = 6
```

**`tick_method`**: The JSON-RPC method biomeOS calls each frame. The primal
receives `{"tick": N, "dt_ms": 16.67, "timestamp_ms": ...}` and must respond
within `budget_ms`.

**`underrun_policy`**:
- `skip`: Drop the frame, continue at target Hz (default for games)
- `catchup`: Run multiple ticks to catch up (physics simulations)
- `warn`: Log warning, continue at reduced rate (monitoring)

### Convergence Tick

For nodes that iterate until a criterion is met:

```toml
[[graph.node]]
name = "physics_solver"
binary = "hotspring"
order = 3
health_method = "health.liveness"
by_capability = "physics"

[graph.node.convergence]
method = "science.iterate"
criterion = "residual"
threshold = 1e-12
max_iterations = 10000
timeout_ms = 30000
```

The composition engine calls `science.iterate` repeatedly. The primal
responds with `{"converged": false, "residual": 1.2e-8, "iteration": 42}`
until converged or limits are hit.

### Event-Driven

For nodes that respond to discrete events (default for most primals):

```toml
[[graph.node]]
name = "ai_agent"
binary = "squirrel"
order = 5
health_method = "health.liveness"
by_capability = "ai"

[graph.node.event]
poll_method = "inference.poll"
poll_interval_ms = 100
timeout_ms = 5000
```

### Batch

For nodes that process a finite dataset:

```toml
[[graph.node]]
name = "validation_suite"
binary = "wetspring"
order = 6
health_method = "health.liveness"
by_capability = "science"

[graph.node.batch]
method = "science.validate_batch"
timeout_ms = 300000
progress_method = "science.progress"
progress_interval_ms = 5000
```

### Seasonal

For nodes driven by calendar or domain periods:

```toml
[[graph.node]]
name = "water_balance"
binary = "airspring"
order = 3
health_method = "health.liveness"
by_capability = "agriculture"

[graph.node.seasonal]
method = "science.seasonal_step"
period = "daily"               # "hourly" | "daily" | "weekly" | "monthly"
align_to = "midnight_utc"
```

---

## Heterogeneous Composition

A single cell graph can mix temporal classes. biomeOS schedules them
according to their declared requirements.

**Example: Game with physics substrate and provenance**

```toml
[graph]
name = "physics_game"
coordination = "continuous"

[graph.tick]
target_hz = 60

# Game logic: runs every frame
[[graph.node]]
name = "game_logic"
tick_method = "game.tick"
budget_ms = 4
# ... other fields ...

# Physics: converges asynchronously, game reads latest state
[[graph.node]]
name = "physics"

[graph.node.convergence]
method = "science.iterate"
threshold = 1e-8
max_iterations = 100
# Runs in parallel with game tick; game reads last-converged state

# Provenance: event-driven, records on state change
[[graph.node]]
name = "provenance"

[graph.node.event]
poll_method = "dag.poll_commits"
poll_interval_ms = 1000
# Records provenance asynchronously; never blocks game tick

# Render: runs every frame after game logic
[[graph.node]]
name = "render"
tick_method = "render.frame"
budget_ms = 10
depends_on = ["game_logic"]
```

**Scheduling rules:**

1. **Continuous nodes** execute every frame in dependency order
2. **Convergence nodes** run asynchronously; consumers read last-converged state
3. **Event nodes** are polled at their declared interval, independent of frame rate
4. **Batch nodes** run to completion, blocking only their dependents
5. **Seasonal nodes** fire at their declared period, independent of everything else

---

## Tick Budget Accounting

biomeOS tracks per-frame budget consumption:

```
Frame budget: 16.67ms (60Hz)
  game_logic:    4ms budget,  3.2ms actual  ✓
  render:       10ms budget,  9.1ms actual  ✓
  overhead:      2.67ms                     ✓
  total:                     12.3ms         under budget
```

When a frame exceeds budget, the `underrun_policy` applies:
- `skip`: Next frame advances game time by 2×dt (or more)
- `catchup`: Extra iterations until caught up (may spike CPU)
- `warn`: Log + continue, accepting temporal drift

---

## Primal Tick Contract

Primals that participate in continuous compositions MUST implement:

```json
// Request (from biomeOS each tick)
{
  "jsonrpc": "2.0",
  "method": "game.tick",
  "params": {
    "tick": 1042,
    "dt_ms": 16.67,
    "timestamp_ms": 1714254000000,
    "budget_ms": 4
  },
  "id": 1042
}

// Response (within budget_ms)
{
  "jsonrpc": "2.0",
  "result": {
    "tick": 1042,
    "elapsed_ms": 3.2,
    "state_changed": true
  },
  "id": 1042
}
```

**`state_changed`**: Signals to event-driven nodes (provenance, attribution)
that they should poll for new data. Reduces unnecessary provenance overhead
on idle frames.

---

## Shell Composition Library

The `nucleus_composition_lib.sh` currently uses a fixed `POLL_INTERVAL` for
all health checks and event polling. For compositions with mixed temporal
requirements, override per-node:

```bash
POLL_INTERVAL=100    # Default: 100ms for event polling
TICK_HZ=60           # For continuous compositions
TICK_BUDGET_MS=16    # Per-frame budget
CONVERGENCE_THRESHOLD=1e-12
CONVERGENCE_MAX_ITER=10000
```

---

## Spring Temporal Profiles

Each spring's temporal nature, discovered through convergent evolution:

| Spring | Primary Class | Secondary | Notes |
|--------|--------------|-----------|-------|
| **hotSpring** | Convergence | Batch | Physics converges; validation runs as batch |
| **wetSpring** | Batch | Convergence | Validation suites are batch; PK/PD models converge |
| **neuralSpring** | Event | Batch | Inference is event-driven; training is batch |
| **healthSpring** | Convergence | Event | Clinical thresholds converge; monitoring is event |
| **ludoSpring** | Continuous | Event | Game ticks at 60Hz; user input is event |
| **groundSpring** | Batch | Convergence | Monte Carlo is batch; inverse problems converge |
| **airSpring** | Seasonal | Batch | Water balance is seasonal; validation is batch |

---

## Future: Adaptive Tick Scheduling

The composition engine will evolve from fixed scheduling to adaptive:

1. **Current**: Fixed `target_hz`, fixed budgets
2. **Near term**: biomeOS PathwayLearner observes actual tick durations and suggests budget adjustments
3. **Medium term**: Dynamic Hz scaling — reduce frame rate when physics convergence is slow, restore when fast
4. **Long term**: Cross-gate tick coordination — Plasmodium-level temporal synchronization across bonded NUCLEUS instances

---

## Related Documents

- `DEPLOYMENT_AND_COMPOSITION.md` — Deploy graph schema and coordination patterns
- `GARDEN_COMPOSITION_ONRAMP.md` — Garden product integration
- `EVOLUTION_STATUS_WAVE66.md` — Seasonal evolution model
- `SPRING_COMPOSITION_PATTERNS.md` — Per-spring patterns
- `TOADSTOOL_SENSOR_CONTRACT.md` — Hardware sensor event timing

---

**Time is not one thing. Games tick. Physics converges. Science batches. Agriculture seasons. The composition engine adapts.**
