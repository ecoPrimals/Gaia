# AAR: BingoCube × Neuromorphic Membrane Gate Analysis

**Wave 166g — October 8, 2026**
**Observer**: eastGate
**Type**: Analysis + reactivation flag

---

## Context

User observation: "bingocube was a math concept of a neuromorphic process. how I visualized it in my head." Followed by: "what if we use akida brainchip npus for the maze in the future? a passive immunity gate on computers?"

This prompted a systematic comparison of BingoCube's architecture against the current neuromorphic hardware landscape, identification of six unexplored directions, and a concrete proposal for using AKD1500 NPUs as a hardware-level adaptive immune gate for the membrane defense.

## What Was Done

### 1. Architectural Analysis

Mapped the structural identity between BingoCube and the AKD1500:
- Board values (int, column-locked) = NP SRAM weights (int4) — zero quantization loss
- Board response patterns (sparse cell matches) = event-based activation — zero compute for non-matches
- Multiple boards in parallel = multiple NPUs running concurrently
- FC readout = FullyConnected layer via SkipDMA single HW pass
- Board evolution (Nautilus shell) = `set_variable()` weight mutation

Key finding: BingoCube is not "like" neuromorphic computing. Its mathematical format IS the hardware's native format. No other reservoir computing architecture has this property.

### 2. Landscape Comparison

Compared against Intel Loihi 2, IBM NorthPole, SynSense Speck, and BrainChip AKD1500. Only AKD1500 matches all constraints:
- Feed-forward only (BingoCube uses evolutionary generations, not recurrence)
- int4/int8 only (board values are natively integer)
- Event-based (cell match = spike)
- On-chip learning (weight mutation via `set_variable()`)
- Commercial availability ($40/chip)
- Sovereign Rust driver (Phase D, 367 tests)

### 3. Prior Art Survey

Found three published neuromorphic IDS systems (SNN-IDS on STM32N6, SNN DDoS on FPGA, simulated NIDS on Lava). All use static classifiers. None evolves on-chip. None uses evolutionary reservoir computing. The BingoCube gate would be the first adaptive neuromorphic defense.

### 4. Passive Immunity Gate Proposal

Proposed AKD1500 between NIC and application layer:
- Input: HTTP behavioral invariants (Accept-Encoding, UA pool, Sec-Fetch, timing) → ~36 bits
- Output: entity class, confidence, pressure contribution
- Latency: ~54 µs (18,500/sec capacity vs 13 rps current fleet)
- Power: 250 mW
- Cost: $40 chip / $150 M.2 card

### 5. Documentation

- **subGen**: `BINGOCUBE_NEUROMORPHIC_MEMBRANE_WAVE166G.md` — full analysis covering structural identity, landscape comparison, six unexplored directions, deployment path
- **rustChip exploration**: `whitePaper/explorations/MEMBRANE_IMMUNITY_GATE.md` — hardware-focused architecture proposal with feature encoding, performance budget, evolution strategy, implementation phases
- **rustChip CHANGELOG**: Updated [Unreleased] section with membrane gate reactivation
- **rustChip README**: Added membrane gate to repo tree listing, status line, and science context section
- **Canvas**: Interactive comparison visualization with hardware landscape, BingoCube vs RC table, unexplored directions, architecture diagram

## Deliverables

| Document | Location |
|---|---|
| subGen analysis | `infra/whitePaper/subGen/BINGOCUBE_NEUROMORPHIC_MEMBRANE_WAVE166G.md` |
| rustChip exploration | `springs/rustChip/whitePaper/explorations/MEMBRANE_IMMUNITY_GATE.md` |
| rustChip CHANGELOG | `springs/rustChip/CHANGELOG.md` |
| rustChip README | `springs/rustChip/README.md` |
| wateringHole AAR | This file |
| Canvas | `canvases/bingocube-neuromorphic-analysis.canvas.tsx` |

## Connections

### hotQCD / biomeGate
The biomeGate brain architecture (`hotSpring/specs/BIOMEGATE_BRAIN_ARCHITECTURE.md`) already models the AKD1000 as a cerebellum — continuous monitoring, learned predictions, fast reflex. The membrane immunity gate extends this: the same NPU hardware that steers lattice QCD sampling also classifies HTTP traffic. The NPU is at < 1% utilization on physics workloads — a membrane model can coexist in the same SRAM.

### toadStool deiisle engine
rustChip is the NPU extraction from toadStool's heterogeneous compute pipeline. The membrane immunity gate is a new workload type for the deiisle engine: instead of routing physics inference to the NPU, route HTTP classification. Same driver, same `predict()` API, different model.

### MazeCube + BackPressure
The NPU gate feeds directly into existing scatter dimensions:
- Entity class → `axes::FLEET_HASH` (MazeCube)
- Confidence → `axes::CONFIDENCE` (MazeCube)
- Pressure → `BackPressure::record_request()` weight

The software path doesn't change. The NPU replaces software-side behavioral classification (bloom_live + epitope_bridge + entity_classifier) with hardware-speed inference.

## Next Steps

1. **Push rustChip to GitHub** — flag reactivation with membrane gate exploration
2. **Push whitePaper subGen** — commit analysis document
3. **Push wateringHole AAR** — this file
4. **Hardware**: Consider AKD1500 M.2 for golgiBody ($150) as next hardware investment
5. **Shadow classification**: Wire NPU classification alongside software classification on biomeGate for validation

---

## Lineage

- Builds on: BingoCube core (Wave 165i) — scalar field, progressive reveal
- Builds on: Nautilus shell — evolutionary reservoir computing
- Builds on: rustChip Phase D — sovereign Rust AKD1000 driver
- Builds on: MazeCube (Wave 166g) — N-dimensional scatter function
- Builds on: BackPressure (Wave 166g) — non-Newtonian velocity response
- Builds on: biomeGate brain architecture — substrate-as-brain-region model
- Builds on: BEYOND_SDK discoveries — 10 hardware capabilities the SDK doesn't document

*Wave 166g — The math concept was neuromorphic from the start. Now we know which silicon it maps to.*
