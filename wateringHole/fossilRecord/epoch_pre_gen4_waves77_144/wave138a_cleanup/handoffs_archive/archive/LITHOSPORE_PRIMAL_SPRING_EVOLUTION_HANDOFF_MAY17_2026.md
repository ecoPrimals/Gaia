<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->

# lithoSpore → Primal + Spring Evolution Handoff

**Date**: 2026-05-17
**From**: lithoSpore workstream (gardens/lithoSpore)
**For**: All primal teams (biomeOS, rhizoCrypt, loamSpine, sweetGrass, songBird,
         petalTongue, nestGate, toadStool), spring teams (wetSpring, hotSpring,
         groundSpring, neuralSpring), NUCLEUS/projectNUCLEUS integration
**Status**: Active

---

## Purpose

lithoSpore is the ecosystem's first **deployed consumer** of the primal stack.
It went from Python notebooks to a USB-deployable artifact that runs 75/75
science checks airgapped, composes into NUCLEUS for Tier 3 provenance, and
validates cross-tier mathematical parity. This handoff captures what we
learned, what works, what doesn't yet, and what primal/spring teams need to
evolve so the ecosystem's real use case — reproducible science — keeps working.

**Key framing**: lithoSpore is not a test harness. It's a product with real
users (Barrick Lab, UT Austin) and real deployment targets (USB sticks handed
to LTEE founders). Every pattern here was earned by running into a wall and
solving it.

---

## 1. What lithoSpore Actually Uses Today (Code, Not Docs)

### JSON-RPC Capabilities Exercised in Production Code

| Capability | Primal | Method | Where | Status |
|------------|--------|--------|-------|--------|
| `orchestration` | biomeOS | `primal.announce` | `discovery.rs` → `validate.rs` Tier 3 | **Wired** (non-fatal) |
| `dag` | rhizoCrypt | `dag.session.create`, `dag.event.append`, `dag.session.complete` | `provenance.rs` | **Wired** |
| `spine` | loamSpine | `spine.create`, `entry.append` | `provenance.rs` | **Wired** |
| `braid` | sweetGrass | `braid.create` | `provenance.rs` | **Wired** |
| `visualization` | petalTongue | `visualization.render` | `visualize.rs` | **Wired** |
| `discovery` | songBird | `ipc.resolve` | `discovery.rs` | **Wired** |

### Capabilities Referenced But Not Yet Exercised

| Capability | Primal | Planned Usage | Blocked By |
|------------|--------|---------------|------------|
| `compute` | toadStool | Accelerated module execution | No workload dispatch wiring |
| `storage` | nestGate | Persistent provenance | `nest.store` signal not routed |
| `crypto` | rhizoCrypt | Merkle verification augmentation | Optional enrichment |
| `health.*` | various | Health monitoring | Not a health producer |
| `capability.list` | any | Wave 20 canonical queries | Implemented, not called from CLI |

### Discovery Chain (Proven in Production)

```
1. $CAPABILITY_PORT env var     → direct TCP
2. UDS $XDG_RUNTIME_DIR/ecoPrimals/discovery.sock → ipc.resolve JSON-RPC
3. TURN $RELAY_SERVER           → geo-delocalized via cellMembrane
4. Standalone (None)            → graceful degradation, Tier 2 only
```

Every discovery result recorded in `liveSpore.json` with `discovery_path`
and `turn_relay`. This provenance is real and auditable.

---

## 2. What We Learned (Lessons for Primal Teams)

### 2a. Graceful Degradation Is Non-Negotiable

lithoSpore operates on USB sticks with no network. Every primal interaction
MUST fall back gracefully. The pattern:

```rust
match litho_core::discovery::discover("dag") {
    Some(ep) => { /* Tier 3 path */ }
    None => { /* Tier 2 path — still fully functional */ }
}
```

**Request to all primal teams**: Document your degradation behavior. When
your primal is unreachable, what does the consumer see? lithoSpore assumes
`None` from discovery means "skip enrichment, continue science." If your
primal returns partial responses, errors, or hangs — lithoSpore doesn't
know how to recover.

### 2b. Capability Strings Must Be Canonical

lithoSpore's `config/capability_registry.toml` tracks every capability
string used in code, graphs, and workloads. When primal teams rename
methods (`store.put` → `storage.store`, for example), downstream consumers
break silently — discovery succeeds but RPC fails.

**Request**: Freeze method names or version them. `dag.session.create` v1
should always work; v2 can add fields but not rename.

### 2c. The Provenance Trio Sequence Must Be Documented as a Transaction

lithoSpore's `try_record_tier3()` runs:

```
dag.session.create → dag.event.append × N → dag.session.complete
→ spine.create → entry.append
→ braid.create
```

If `loamSpine` is reachable but `sweetGrass` isn't, lithoSpore has a DAG
and spine but no braid. Is this a valid partial provenance? lithoSpore
currently treats it as success with reduced `primals_reached` count, but
this decision was arbitrary.

**Request to trio teams**: Define transaction semantics. Can a consumer
commit a DAG without a braid? Should it? What's the rollback path?

### 2d. UDS Socket Ownership Is Ambiguous

`$XDG_RUNTIME_DIR/ecoPrimals/discovery.sock` — who creates this socket?
biomeOS? songBird? NUCLEUS orchestrator? lithoSpore probes for it but
never creates it. Currently there's no standard for who owns the socket
lifecycle.

**Request to biomeOS/songBird**: Publish socket ownership documentation.
Which process binds, which process connects, what happens on crash/restart.

### 2e. Signal Dispatch Is Future, Not Present

lithoSpore's graph and workload TOMLs annotate `signals = ["nest.store",
"nest.commit"]`, but there is **no signal dispatch in lithoSpore code**.
The `nest.store` mapping in `provenance.rs` comments describes the intent:
eventually, the entire provenance phase collapses to a single signal.

**Request to biomeOS**: When `ctx.dispatch("nest.store", ...)` ships, the
ferment transcript handoff (upstream braid → lithoSpore) should collapse
to a single signal instead of the current JSON file handoff.

---

## 3. What Spring Teams Need to Do

### 3a. Ferment Transcript Pattern (wetSpring Priority)

lithoSpore ships summary statistics from papers but can't carry raw data
(some datasets are 200 GB). Upstream springs must:

1. Process raw data (e.g., breseq on 264 genomes)
2. Record provenance via the trio (DAG + spine + braid)
3. Hand the **braid** to lithoSpore via `provenance/braids/{dataset_id}.json`

The full contract is in:
`handoffs/LITHOSPORE_FERMENT_TRANSCRIPT_BRAID_HANDOFF_MAY17_2026.md`

**Priority datasets for wetSpring:**

| Dataset | Computation | Data Size | Impact |
|---------|-------------|-----------|--------|
| Tenaillon 2016 | breseq on 264 genomes | ~200 GB | Highest — impressive for Barrick/Lenski demo |
| Barrick 2009 | breseq on 19 genomes | ~15 GB | High — mutation accumulation verification |

### 3b. Summary Stats Must Match Published Claims

Springs producing summary stats for lithoSpore must output numbers that
match the published paper. lithoSpore validates **against the paper**, not
against the spring's intermediate computation. If the spring's pipeline
produces slightly different numbers (e.g., due to updated reference
genomes), the spring must document the divergence and lithoSpore must
update its tolerances.

### 3c. groundSpring / hotSpring — Data Already Integrated

Modules 1-5 and 7 use data from groundSpring and hotSpring. No additional
spring work is needed for Tier 2 — the data is shipped. Braid handoff
is optional enrichment.

### 3d. neuralSpring — ML Surrogates Are Additive

Modules 3 and 4 have neuralSpring ML surrogate enrichment queued. This
is additive — the modules pass all checks without it. When neuralSpring
B3/B4 models are ready, lithoSpore will integrate them as additional
validation dimensions, not replacements.

---

## 4. NUCLEUS Composition and Deployment

### 4a. Deploy Graph

`graphs/ltee_guidestone.toml` uses `by_capability` on every node — no
hardcoded primal names. Dark Forest metadata included. Structurally
validated by `litho-core::graph_checks` unit tests against the capability
registry.

### 4b. Workloads

Two workload TOMLs in `workloads/`:

| Workload | Type | Isolation | What It Runs |
|----------|------|-----------|-------------|
| `litho-validate-tier2.toml` | native | standard | `litho validate --json` |
| `litho-validate-tier3.toml` | composition | btsp | `litho validate --json --max-tier 3` with graph |

### 4c. Atomic Instantiation via biomeOS/neuralAPI

The deployment matrix cell `lithospore-x86-vm-uds` validates the USB
artifact in a VM with UDS primal connectivity. For biomeOS atomic
instantiation:

1. lithoSpore is a **ColdSpore** → **LiveSpore** → **lithoSpore** lifecycle
2. `biomeOS/tower.toml` declares the spore composition
3. `.biomeos-spore` marker identifies the artifact as biomeOS-aware
4. `primal.announce` registers lithoSpore with biomeOS at Tier 3 startup

**What biomeOS needs**: A `spore.instantiate` signal/command that
atomically provisions the lithoSpore artifact into a VM cell with UDS
connectivity to the trio. Currently this is manual (cloud-init YAML +
`litho grow --vm`).

### 4d. Container Deployment

`Containerfile` at repo root. `scripts/build-container.sh` wraps
Podman/Docker. The container is a deployment path, not the primary
target — the USB hypogeal cotyledon is the canonical artifact.

---

## 5. Cross-Tier Parity (New Pattern for the Ecosystem)

`litho parity` runs Python (Tier 1) and Rust (Tier 2) side-by-side for
all 7 modules and reports MATCH/DIVERGENCE. This pattern should be
adopted by other gardens/products that have multi-tier implementations:

- If your science runs in Python AND Rust, parity proves the math is stable
- The tolerance framework (`artifact/tolerances.toml`) handles expected
  numerical differences (optimizer path sensitivity, FP precision)
- `ParityReport` is a structured output suitable for CI gates

**Implication for NUCLEUS**: A composition that runs a guideStone through
parity, then records Tier 3 provenance, produces a three-layer proof:
Tier 1 confirms the science, Tier 2 confirms the implementation, Tier 3
confirms the provenance chain.

---

## 6. Current State (May 17, 2026)

| Metric | Value |
|--------|-------|
| Science modules | 7/7 PASS (Tier 2 Rust) |
| Science checks | 75/75 |
| Tier 1 (Python) | 7/7 modules with notebooks |
| Tier 3 (Primal) | JSON-RPC client wired, no primals in test yet |
| Cross-tier parity | `litho parity` wired for all 7 modules |
| Unit/integration tests | 125 |
| Chaos tests | 10 fault injection scenarios |
| CLI subcommands | 15 |
| Clippy | Zero warnings (pedantic) |
| Unsafe code | `#![forbid(unsafe_code)]` workspace-wide |
| Papers indexed | 16 DOIs in `papers/registry.toml` |
| Data model | Two-tier (summary shipped, full fetchable) |
| Upstream braids | Wired in `data.toml` (empty — awaiting first spring handoff) |

---

## 7. Requests Summary

| # | Request | For | Priority |
|---|---------|-----|----------|
| 1 | Document degradation behavior for all primals | All primal teams | HIGH |
| 2 | Freeze/version JSON-RPC method names | All primal teams | HIGH |
| 3 | Define provenance trio transaction semantics | rhizoCrypt, loamSpine, sweetGrass | HIGH |
| 4 | Publish UDS socket ownership standard | biomeOS, songBird | MEDIUM |
| 5 | Implement `nest.store` signal dispatch | biomeOS | MEDIUM |
| 6 | Produce ferment transcript braids for LTEE datasets | wetSpring | HIGH |
| 7 | Add `spore.instantiate` for atomic VM provisioning | biomeOS | LOW |
| 8 | Wave 20 `capability.list` must return complete inventory | All primals | LOW |

---

## Related Documents

- `LITHOSPORE_FERMENT_TRANSCRIPT_BRAID_HANDOFF_MAY17_2026.md` — upstream braid contract
- `LITHOSPORE_DEEP_DEBT_PRIMAL_EVOLUTION_HANDOFF_MAY16_2026.md` — deep debt + evolution (May 16)
- `LITHOSPORE_UPSTREAM_SPRING_PRIMAL_FEEDBACK_MAY16_2026.md` — spring feedback (May 16)
- `PROVENANCE_TRIO_INTEGRATION_GUIDE.md` — trio wiring reference
- `TARGETED_GUIDESTONE_STANDARD.md` — guideStone grade definition
- `LITHOSPORE_USB_DEPLOYMENT.md` — USB deployment standard
- `lithoSpore/docs/ARCHITECTURE.md` — architecture + data model
- `lithoSpore/docs/UPSTREAM_GAPS.md` — gap registry + changelog
