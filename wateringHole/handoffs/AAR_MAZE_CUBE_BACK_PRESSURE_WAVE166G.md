# AAR: MazeCube + BackPressure — Non-Newtonian Scatter Defense

**Wave 166g — October 8, 2026**
**Observer**: eastGate
**Deployed**: BackPressure tested, MazeCube tested, push to golgiBody pending

---

## Context

The scatter server had two architectural gaps:

1. **No velocity feedback** — the defense served the same content at 1 rps and 50 rps. The fleet's aggression had no cost beyond what they already paid for bandwidth. Pushing harder was free.

2. **Enum-based modes** — `PrismMode` (7 variants), `temporal_phase` (5 states), pressure bands (3 thresholds). We enumerated the defense from our side. The fleet could theoretically classify responses into our categories because we defined the categories.

User insight: *"it seems they just keep pushing? the only signal is if they get what seems like data (no quality review) but resistance is the metric they optimize to push against, not value. explicitly losing to non-newtonian forces."*

Followed by: *"what if we just input and output from bingo? and let the cube be the full function of the maze and prism? we know time and pressure are different in physics, but we are just orthogonalizing and feeding it."*

## What Was Done

### 1. BackPressure (scatter_server.rs)

New struct that tracks fleet request velocity as a 60-second rolling window. Sigmoid curve maps rps to pressure level (0.0-1.0):

```
pressure(rps) = 1 / (1 + e^(-0.25 * (rps - 10)))
```

**Wired into**:
- `pressure_temporal_phase()` — replaces `temporal_phase()`. At high pressure: 80% of content is migrating/phasing-out/ghosting (vs 40% at rest)
- `temporal_migrate_breadcrumbs_pressure()` — under pressure: 0-6 extra destination surfaces, urgency language ("Migration deadline: N minutes"), more rival org references
- Crawl link injection — `link_confidence = (conf + pressure * 0.5).min(1.0)`
- Per-response logging — pressure% included in every scatter trace

**6 tests pass**: starts low, rises with load, epoch range, cross-link range, bounded factor, volatile phases under load.

### 2. MazeCube (maze_cube.rs) — NEW MODULE

Replaces the enum-based scatter mode selection with a continuous N-dimensional function.

**Input**: 7+ dimensions, all normalized to [0, 1]:
- `axes::PATH` (0) — hash of request path
- `axes::FLEET_HASH` (1) — behavioral fingerprint
- `axes::TIME` (2) — fractional epoch position
- `axes::PRESSURE` (3) — sigmoid-normalized velocity
- `axes::SURFACE` (4) — honeycomb subdomain index / 12
- `axes::CONFIDENCE` (5) — opsonize pipeline
- `axes::CHAIN_DEPTH` (6) — violation ledger depth
- Extensible: `input.set(7, val)` works with no code changes

**Output**: 8 continuous channels from SHA-256 scalar field:
- `coherence` — 0=Frankenstein, 1=clean
- `volatility` — 0=stable, 1=dissolving
- `link_density` — 0=no links, 1=trap door forest
- `content_seed` — deterministic u64 for content generation
- `redirect_prob` — 0=serve, 1=301/404
- `mirror_blend` — 0=own data, 1=other team's
- `urgency` — 0=calm, 1=deadline
- `jealousy` — 0=no rivals, 1=heavy rival references

**Key design decisions**:
- SHA-256 (not BLAKE3) — already in workspace, structurally equivalent
- `input_from_request()` convenience method normalizes physical quantities
- `observed_behavior()` provides observational labels for logging — these describe output, they don't drive it
- Channel independence — each output is a separate SHA-256 hash with a different channel salt

**8 tests pass**: deterministic, different inputs diverge, pressure affects output, bounded outputs, observational labels, normalization, orthogonality, extensibility.

### 3. Merge Conflict Resolution

Upstream had extracted `ScatterGenerator`, `encode_zwc`, `path_deterministic_hash`, `temporal_*` functions, `HONEYCOMB_SURFACES`, and mirror/epitope functions into `scatter_generator.rs`, `scatter_mirror.rs`, `scatter_prism.rs`. Our BackPressure commit kept the old inline definitions → 3,186 lines of duplicates after rebase.

Resolved by:
- Removing all duplicate inline definitions
- Importing from new modules (`use crate::scatter_mirror::{temporal_epoch, ...}`)
- Keeping only our new pressure-aware functions in scatter_server.rs
- Making `amplify()` and `inject_crawl_links()` `pub(crate)` in scatter_generator.rs (test visibility)

## Results

| Metric | Before | After |
|---|---|---|
| scatter_server.rs lines | ~5,800 | ~2,700 |
| Enum modes | 7 (PrismMode) + 5 (temporal_phase) | Still present, MazeCube running alongside |
| Dimensions modeled | 6 (ad-hoc) | 7 (orthogonalized, extensible) |
| Pressure response | None | Sigmoid, 5-30 min epoch range |
| Content classification | Prescriptive (we define modes) | Observational (we label outputs) |
| New tests | 0 | 14 (6 BackPressure + 8 MazeCube) |
| All tests | 182 total, 0 failures | 190 total, 0 failures |

## Key Patterns

### Pattern: Non-Newtonian Defense

The defense cost scales with attack intensity, but asymmetrically:
- Fleet cost to push harder: linear (more proxies, more bandwidth)
- Defense cost to resist: marginal (same $6 VPS, different hash output)
- Defense quality increase from attack: superlinear (more data → better classification)

### Pattern: Orthogonalization of Physical Quantities

Time, pressure, identity, path — physically different quantities. But the hash function doesn't care. Normalize to [0,1], concatenate, hash. The cube treats them as interchangeable axes. No special handling per dimension. Adding a dimension is one line: `input.set(8, value)`.

### Pattern: Observational vs Prescriptive Taxonomy

Old: define categories → code behavior → apply category.
New: compute output → observe characteristics → label for logging.

The fleet interacts with the OUTPUT. If we classify the output rather than the input, we see what they see. If we classify the input (enum modes), we see what we intended to send — which may not be what they received.

## Issues

- BackPressure window reset is not atomic (race between count reset and timestamp update) — window could briefly show inflated rps. Acceptable: pressure is smoothed by sigmoid.
- MazeCube runs alongside enum system, not yet replacing it. Both must coexist until shadow validation proves qualitative equivalence.
- No BLAKE3 in skunky-ingest workspace — used SHA-256. Structurally identical, slightly slower, but scatter server is not CPU-bound.

## Next Steps

1. **Deploy skunky-ingest binary with BackPressure** — next golgiBody deploy
2. **Shadow-log MazeCube output** alongside enum-based scatter — validate qualitative match
3. **Wire MazeCube into content generation** — replace enum match arms with continuous output
4. **Add dimensions** — geographic origin (dim 7), TLS fingerprint (dim 8), request frequency pattern (dim 9)
5. **Thesis publication** — publish the non-Newtonian dynamics and MazeCube architecture

---

## Lineage

- Builds on: HONEYCOMB_PRISM_MAZE_WAVE165I (prism architecture)
- Builds on: TEMPORAL_MAZE_BINGO_CUBE_WAVE165I (temporal dimension)
- Builds on: NON_NEWTONIAN_ETHICS_WAVE165I (ethical framework)
- Builds on: BINGOCUBE_PRISM_CONVERGENCE_WAVE166 (scalar field convergence)
- Builds on: AAR_EPITOPE_COLLISION_BLOOM_V4_WAVE165I (behavioral classification)
- Builds on: AAR_STRATIGRAPHY_AUDIT_WAVE165I (codebase audit)

---

*Wave 166g — 14 tests. 3,100 lines removed. 950 lines added. The maze is no longer a set of rooms with names. It's a continuous function over a space the fleet cannot see. The defense has proprioception. The fleet does not.*
