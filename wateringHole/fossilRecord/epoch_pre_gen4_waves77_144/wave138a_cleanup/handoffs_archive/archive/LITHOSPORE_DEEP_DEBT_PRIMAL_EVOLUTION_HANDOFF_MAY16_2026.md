<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->

# lithoSpore — Deep Debt Resolution + Primal Evolution Handoff

**Date**: 2026-05-16
**From**: lithoSpore workstream (gardens/lithoSpore)
**For**: primalPing audit, primal teams, spring teams, NUCLEUS integration

## Summary

lithoSpore deep debt pass complete. The viz subsystem was refactored
(baselines.rs 637→376 LOC, modules.rs 367→178 LOC) via 9 extracted
DataBinding builder helpers. Discovery evolved from primal-name-specific
env vars to capability-generic names. Rust 2024 compliance fixed.
Root docs, whitePaper/baseCamp/, and experiments/ created to match
ecosystem conventions.

**Result**: 116/116 tests PASS, 75/75 checks PASS, zero clippy warnings,
`#![forbid(unsafe_code)]` workspace-wide, zero `#[allow]` in production,
zero production mocks, zero TODO/FIXME/HACK in crates/.

---

## Deep Debt Actions (May 16, 2026)

### viz/ Builder Refactor (-393 net lines)

Extracted 9 generic `DataBinding` builder helpers from repetitive
`serde_json::json!({})` patterns into `viz/mod.rs`:

| Helper | Channel Type | Parameters |
|--------|-------------|------------|
| `bar` | bar chart | categories, values, unit |
| `bar_from_object` | bar chart | JSON object, unit |
| `gauge` | single value | value, unit, range |
| `timeseries` | time series | x, y, axis labels |
| `scatter` | scatter plot | x, y, axis labels |
| `heatmap` | 2D grid | matrix, x/y labels, unit |
| `distribution` | histogram | values, bin labels, unit |
| `genome_track` | genome browser | segments array |
| `track_segment` | track entry | start, end, label, value |

`baselines.rs` reduced from 637→376 LOC (41%), `modules.rs` from
367→178 LOC (51%). All test coverage preserved.

### Discovery Capability-Generic Evolution

| Before | After |
|--------|-------|
| `$SONGBIRD_TURN_SERVER` | `$RELAY_SERVER` (fallback `$SONGBIRD_TURN_SERVER`) |
| `$SONGBIRD_TURN_DISCOVERY_PORT` | `$RELAY_DISCOVERY_PORT` (fallback `$SONGBIRD_TURN_DISCOVERY_PORT`) |
| `$PETALTONGUE_SOCKET` | `$VISUALIZATION_SOCKET` (fallback `$PETALTONGUE_SOCKET`) |
| `discover_petaltongue_socket()` | `discover_visualization_socket()` |

Primal self-knowledge principle enforced: discovery code no longer
knows which primal provides relay or visualization services.

### Code Quality Audit (clean bill)

| Metric | Count | Notes |
|--------|-------|-------|
| `unsafe` blocks | 0 | `forbid` at workspace lint level |
| `#[allow(...)]` in production | 0 | All evolved to `#[expect]` or eliminated |
| Production mocks | 0 | All mocks in `#[cfg(test)]` |
| `.unwrap()` in production | 0 | All in test code |
| TODO/FIXME/HACK | 0 | Across all crates/ |
| Files > 800 LOC | 0 | Max is 442 (validate.rs) |
| Clippy warnings | 0 | Pedantic profile |

---

## Primal Usage and Evolution

lithoSpore is a **consumer** (verification chassis), not a primal
(service provider). It discovers primals at runtime and degrades
gracefully when they're unavailable.

### Primals Consumed

| Primal | Capability | Integration Point | Status |
|--------|-----------|-------------------|--------|
| petalTongue | `visualization` | `litho visualize` → IPC dashboard push | Functional via env/UDS |
| songBird | `discovery`, `ipc` | `litho_core::discovery` → TURN relay | Env-var stub (needs TURN client lib) |
| toadStool | `compute` | Tier 3 graph node (GPU dispatch) | Graph-declared, not runtime-tested |
| nestGate | `storage` | Tier 3 provenance persistence | Graph-declared only |
| rhizoCrypt | `dag` | Tier 3 DAG chain | Graph-declared only |
| loamSpine | `spine` | Tier 3 lineage spine | Graph-declared only |
| sweetGrass | `braid` | Tier 3 attribution braid | Graph-declared only |
| bearDog | `crypto` | FIDO2 attestation in liveSpore.json | Graph-declared, not implemented |
| biomeOS | `lifecycle` | Spore composition orchestration | Detected via `$BIOMEOS_ORCHESTRATOR` |

### Primals NOT Referenced

| Primal | Reason |
|--------|--------|
| barraCuda | Stats done locally (20 LOC `pearson_r`); GPU dispatch via toadStool |
| mycoNet | No networking mesh needed; relay via songBird |
| neuralAPI | Not yet integrated; future ML surrogate path |
| squirrel | No inference needed at lithoSpore level |
| sourDough | No key management at lithoSpore level |

### Evolution Recommendations for Primal Teams

**petalTongue team**:
- Register `visualization` capability via ecosystem discovery socket
- Accept `visualization.render` JSON-RPC method over UDS
- Respond to `$VISUALIZATION_SOCKET` env var convention
- lithoSpore's `DataBinding` output format matches `petal-tongue-types::DataBinding`

**songBird team**:
- lithoSpore needs actual TURN client library for geo-delocalized mode
- Currently uses env var `$RELAY_SERVER` for endpoint, but no relay protocol
- Legacy env vars `$SONGBIRD_TURN_*` still supported as fallback

**biomeOS team**:
- lithoSpore detects orchestration via `$BIOMEOS_ORCHESTRATOR`
- USB spore root includes `biomeOS/tower.toml` + graph
- Signal adoption annotated: `nest.store`, `nest.commit` on graph + workloads
- Atomic instantiation path: deploy USB as self-sufficient unit

**toadStool team**:
- Tier 3 graph declares `compute.dispatch` + `compute.status` capabilities
- lithoSpore has zero GPU code — toadStool dispatch is optional acceleration
- `node.compute` signal annotated on compute domain in capability registry

---

## NUCLEUS Composition Patterns

### Current Tier 3 Graph (`graphs/ltee_guidestone.toml`)

```
litho validate → bearDog (attestation) → rhizoCrypt (DAG chain)
                                        → loamSpine (lineage)
                                        → sweetGrass (attribution)
                                        → toadStool (GPU, optional)
```

All nodes resolved by `by_capability` strings, not primal names.
Discovery socket or environment variables provide endpoint resolution.

### Signal Adoption Status

| Signal | Annotation | Runtime Code? |
|--------|-----------|---------------|
| `nest.store` | Graph + workload TOML | No — needs CompositionContext |
| `nest.commit` | Graph + workload TOML | No — needs CompositionContext |
| `node.compute` | Capability registry | No — Tier 3 graph dispatch |
| `primal.announce` | Capability registry | No — CLI tool, not daemon |
| `health.readiness` | Capability registry | No — no health endpoint |

**Path to runtime signal adoption**: lithoSpore embeds no
`CompositionContext` runtime. When biomeOS provides signal dispatch
routing, the provenance phase (3 sequential nodes) collapses to a
single `nest.store` dispatch. Graph and workload TOMLs are annotated
for this transition.

### neuralAPI and Atomic Instantiation

lithoSpore's deployment matrix cell `lithospore-x86-vm-uds` defines a
validated USB-in-VM configuration. For neuralAPI atomic instantiation:

1. biomeOS instantiates the lithoSpore spore as an atomic unit
2. The spore discovers primals via the host's discovery socket
3. Validation runs at whatever tier is achievable (1/2/3)
4. Results flow back through `nest.store` if available, else local JSON
5. liveSpore.json records the deployment provenance

The spore is self-sufficient — it never requires external orchestration
to produce a valid result. NUCLEUS composition is additive (provenance,
attestation, braids) rather than constitutive.

---

## Upstream Gaps for primalPing Audit

### Still Open (lithoSpore-owned)

| ID | Priority | Gap | Notes |
|----|----------|-----|-------|
| LS-BLAKE3 | P3 | 5/8 datasets have `blake3 = ""` in data.toml | Needs `litho fetch --all` run |
| LS-DOCS | P2 | 99 public items in litho-core lack `///` doc comments | Blocks crates.io publish |
| LS-VIZ-SPLIT | P2 | LTEE-specific viz adapters in litho-core | Should move to ltee-cli |
| LS-CI-M5 | P3 | Module 5 missing from CI Python baselines job | Likely intentional (data) |
| LS-TESTS | P3 | alleles, citrate, breseq have only 2 tests each | Need unit tests on internals |

### Upstream-Blocked

| ID | Priority | Gap | Owner |
|----|----------|-----|-------|
| SB-TURN | P2 | Songbird TURN client library | songBird team |
| BD-FIDO2 | P3 | FIDO2/CTAP2 attestation for liveSpore.json | bearDog team |
| BM-SIGNAL | P2 | biomeOS signal dispatch routing | biomeOS team |
| PT-DISC | P2 | petalTongue discovery socket registration | petalTongue team |
| GB-PKG | P3 | genomeBin primal packaging for USB Tier 3 | infra team |

---

## Verification

```
cargo test --workspace:  116 passed, 0 failed
cargo clippy --workspace: 0 errors, 0 warnings
litho validate --json:   75/75 checks, 7/7 PASS
git diff --stat:         -393 net lines (viz refactor)
```
