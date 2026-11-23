# Provenance Trio Integration Guide

**Version:** 2.0.0
**Date:** May 13, 2026 (wire names reconciled per GAP-36)
**Audience:** Springs, gardens, and any composition wiring rhizoCrypt + loamSpine + sweetGrass
**Status:** Active
**License:** AGPL-3.0-or-later

---

## Purpose

The provenance trio — **rhizoCrypt** (ephemeral DAG), **loamSpine**
(immutable ledger), and **sweetGrass** (semantic attribution) — is the most
referenced subsystem across all springs. As of April 27, 2026, PG-52 (UDS empty
responses) is **resolved upstream** — all three primals now respond to JSON-RPC
over UDS after rebuilds from current source.

This document provides the operational integration guide: how to wire the trio
into a composition, what to expect from each primal, known failure modes, and
workarounds. It consolidates and promotes the patterns from
`fossilRecord/consolidated-apr2026/SCYBORG_PROVENANCE_TRIO_GUIDANCE.md` and
the cross-spring convergence analysis.

For the licensing framework built on the trio, see
`fossilRecord/consolidated-apr2026/SCYBORG_PROVENANCE_TRIO_GUIDANCE.md`.

---

## The Three Roles

```
Working Memory          Permanent Record          Attribution
┌──────────┐           ┌──────────┐           ┌──────────┐
│rhizoCrypt│──dehydrate──▶│loamSpine │◀──certify───│sweetGrass│
│          │           │          │           │          │
│ DAG      │           │ Ledger   │           │ Braids   │
│ Sessions │           │ Certs    │           │ W3C PROV │
│ Merkle   │           │ DID      │           │ Roles    │
└──────────┘           └──────────┘           └──────────┘
```

| Primal | Domain | IPC Capability | What It Owns |
|--------|--------|---------------|-------------|
| **rhizoCrypt** | Ephemeral memory | `dag` | Content-addressed DAG, session lifecycle, Merkle trees, dehydration to loamSpine |
| **loamSpine** | Permanence | `ledger` | Immutable append-only ledger, DID ownership, certificate lifecycle (mint/transfer/loan), temporal anchoring |
| **sweetGrass** | Attribution | `attribution` | W3C PROV-O braids, 12 contributor roles, derivation chains, privacy controls, attribution calculation |

---

## Deploy Graph Pattern

Include the trio in your deploy graph with `fallback = "skip"` on all three
nodes. This is the canonical pattern — every spring and garden uses it.

```toml
# Provenance trio — optional enrichment
[[graph.node]]
name = "rhizocrypt"
binary = "rhizocrypt"
order = 10
required = false
depends_on = ["beardog"]
health_method = "health.liveness"
by_capability = "dag"
capabilities = ["dag.create_session", "dag.add_vertex", "dag.dehydrate"]
fallback = "skip"

[[graph.node]]
name = "loamspine"
binary = "loamspine"
order = 11
required = false
depends_on = ["beardog"]
health_method = "health.liveness"
by_capability = "ledger"
capabilities = ["ledger.commit", "ledger.mint_certificate", "ledger.verify"]
fallback = "skip"

[[graph.node]]
name = "sweetgrass"
binary = "sweetgrass"
order = 12
required = false
depends_on = ["beardog"]
health_method = "health.liveness"
by_capability = "attribution"
capabilities = ["braid.create", "contribution.record", "attribution.chain"]
fallback = "skip"
```

**Why `depends_on = ["beardog"]`**: The trio uses BearDog for cryptographic
signing of DAG vertices, ledger entries, and attribution records.

**Why `fallback = "skip"`**: Science and product logic must work without
provenance. Recording provenance is enrichment — it does not gate computation.

---

## The Commit Flow

The standard provenance commit flow composes all three primals in sequence.
biomeOS orchestrates this as the `rootpulse_commit` graph.

```
1. rhizoCrypt: dag.session.create({"name": "..."})
   → session_id

2. [Your work happens — add events to the DAG]
   rhizoCrypt: dag.event.append({"session_id": "...", "event_type": {...}, "data": {...}})
   → vertex hash (content-addressed)

3. sweetGrass: braid.create({"data_hash": "...", "mime_type": "...", "size": N,
      "name": "...", "description": "...", "source_session": "<session_id>"})
   sweetGrass: contribution.record({"hash": "...", "agent": "...", "role": "Creator"})
   → braid with contributor records and urn:braid: identifier

4. rhizoCrypt: dag.merkle.root({"session_id": "..."})
   → Merkle root hash

5. loamSpine: entry.append({"spine_id": "...", "entry_type": {...}, "committer": "..."})
   → immutable ledger entry with temporal anchor

6. sweetGrass: braid.commit({"braid_id": "urn:braid:...", "spine_id": "..."})
   → braid packaged for loamSpine anchoring
```

**The result**: An immutable record that says WHO did WHAT, WHEN, with
cryptographic proof from BearDog and a permanent ledger entry from loamSpine.

---

## Transaction Semantics and Partial Completion

The trio commit flow is **not atomic** — each primal operates independently
over JSON-RPC. Consumers must handle partial completion gracefully.

### Partial Completion States

| State | rhizoCrypt | loamSpine | sweetGrass | Validity | Consumer Action |
|-------|-----------|-----------|------------|----------|----------------|
| **Full** | DAG complete | Entry sealed | Braid committed | Complete provenance | Record all IDs |
| **DAG + spine** | DAG complete | Entry sealed | Unreachable | Valid provenance without attribution | Record DAG + spine; note missing braid |
| **DAG only** | DAG complete | Unreachable | Unreachable | Ephemeral provenance (no permanence) | Record DAG; flag as unanchored |
| **None** | Unreachable | — | — | No provenance | Science still runs; record `recorded: false` |

### Rules for Consumers

1. **A DAG session without a braid is valid partial provenance.** The merkle
   root still covers the computation — it just lacks a W3C PROV-O attribution
   envelope. Consumers SHOULD record the session ID and flag it for braid
   backfill when sweetGrass becomes reachable.

2. **A braid without a spine entry is valid attribution without permanence.**
   The attribution is recorded in sweetGrass but not anchored in the immutable
   ledger. Consumers SHOULD record the braid ID and attempt spine anchoring
   later.

3. **There is no rollback.** DAG sessions that complete cannot be undone —
   they are append-only. If spine or braid fails after DAG completion, the
   DAG session remains valid and can be referenced by future spine/braid calls.

4. **Partial state MUST be reported in output.** Consumers must expose which
   primals were reached (lithoSpore uses `primals_reached: Vec<String>` in
   `Tier3Session`). This enables auditors to distinguish "provenance was
   partial" from "provenance was not attempted."

5. **Never error on partial provenance.** Domain logic (science, validation,
   product features) MUST NOT fail because provenance recording was partial.
   The pattern: `try_record_tier3()` returns `Ok(session)` even with reduced
   `primals_reached` — only returns `Err` when zero primals respond.

### lithoSpore Reference Implementation

```rust
// From litho-core/src/provenance.rs — try_record_tier3()
let dag_ep = discover("dag").ok_or("rhizoCrypt not reachable")?;  // Hard requirement
let spine_ep = discover("spine").ok_or("loamSpine not reachable")?;
let braid_ep = discover("braid").ok_or("sweetGrass not reachable")?;

// Phase 1: DAG (required)
let dag_session_id = rpc_call_extract(&dag_ep, "dag.session.create", ...)?;
// ... append events, complete session ...

// Phase 2: Spine (best-effort after DAG)
let spine_id = rpc_call_extract(&spine_ep, "spine.create", ...)
    .unwrap_or_else(|_| "pending".into());

// Phase 3: Braid (best-effort after spine)
let braid_id = rpc_call_extract(&braid_ep, "braid.create", ...)
    .unwrap_or_else(|_| "pending".into());
```

---

## JSON-RPC Methods Reference

### rhizoCrypt (capability: `dag`)

| Method | Params | Response | Notes |
|--------|--------|----------|-------|
| `health.liveness` | `{}` | `{"status": "alive", "name": "rhizocrypt"}` | Standard health probe |
| `dag.create_session` | `{"name": "my_experiment"}` | `{"session_id": "..."}` | Creates working memory scope |
| `dag.add_vertex` | `{"session_id": "...", "content": "...", "parents": [...]}` | `{"vertex_id": "..."}` | Content-addressed; parents form DAG edges |
| `dag.get_vertex` | `{"vertex_id": "..."}` | `{"content": "...", "parents": [...], "metadata": {...}}` | Retrieve by content hash |
| `dag.dehydrate` | `{"session_id": "..."}` | `{"state": "..."}` | Serialize session for loamSpine commit |
| `dag.merkle_root` | `{"session_id": "..."}` | `{"root": "..."}` | Merkle tree root of session state |

### loamSpine (capability: `ledger`)

| Method | Params | Response | Notes |
|--------|--------|----------|-------|
| `health.liveness` | `{}` | `{"status": "alive", "name": "loamspine"}` | Standard health probe |
| `ledger.commit` | `{"state": "...", "signature": "..."}` | `{"entry_id": "...", "timestamp": "..."}` | Immutable append; requires BearDog signature |
| `ledger.verify` | `{"entry_id": "..."}` | `{"valid": true, "timestamp": "..."}` | Verify ledger entry integrity |
| `ledger.mint_certificate` | `{"type": "...", "subject": "...", "attributes": {...}}` | `{"cert_id": "..."}` | Issue a loam certificate |
| `ledger.get_entry` | `{"entry_id": "..."}` | `{"state": "...", "signature": "...", "timestamp": "..."}` | Retrieve ledger entry |

### sweetGrass (capability: `attribution`)

sweetGrass v0.7.35 exposes 37 canonical methods + 10 wire-name aliases.
The table below shows the primary methods used in composition. For the
full surface, see `sweetGrass/CONTEXT.md` or call `capabilities.list`.

| Method | Params | Response | Notes |
|--------|--------|----------|-------|
| `health.liveness` | `{}` | `{"status": "alive", "name": "sweetgrass"}` | Standard health probe |
| `braid.create` | `{"data_hash": "...", "mime_type": "...", "size": N}` | Full W3C PROV-O JSON-LD with `@id: "urn:braid:..."` | Also accepts flattened `name`, `description`, `tags`, `source_session`, `source_merkle_root` |
| `contribution.record` | `{"hash": "...", "agent": "did:...", "role": "Creator"}` | `{"contribution_id": "..."}` | Record a contributor to a braid |
| `attribution.chain` | `{"hash": "..."}` | `{"contributors": [...]}` | Get attribution chain for a content hash |
| `attribution.calculate_rewards` | `{"hash": "...", "value": N}` | `[{"agent": "...", "share": 0.5, "amount": N}]` | Calculate value distribution |
| `braid.commit` | `{"braid_id": "urn:braid:...", "spine_id": "..."}` | `{"braid_id": "...", "data_hash_bytes": "..."}` | Package braid for loamSpine anchoring |
| `provenance.graph` | `{"entity": {"data_hash": "..."}}` | `{...}` | Provenance graph for an entity |
| `provenance.export_provo` | `{"hash": "..."}` | W3C PROV-O JSON-LD | Export as PROV-O |
| `attribution.witness` | `{"hash": "...", "witness_agent": "did:...", "event_type": "..."}` | `{"witnessed_at": "..."}` | JH-5 audit attestation |
| `lifecycle.status` | `{}` | `{"status": "running", "version": "..."}` | Primal lifecycle state |

**Wire-name aliases** (for backward compatibility — use canonical names above):
`attribution.create_braid` → `braid.create`, `attribution.add_contribution` → `contribution.record`,
`attribution.calculate` → `attribution.calculate_rewards`, `attribution.seal` → `braid.commit`,
`attribution.export_prov` → `provenance.export_provo`, `provenance.lineage` → `attribution.chain`,
`provenance.create_braid` → `braid.create`, `attribution.braid` → `braid.create`,
`attribution.anchor` → `anchoring.anchor`, `braid.attribution.create` → `braid.create`.

---

## Graceful Degradation Pattern

Every spring MUST degrade gracefully when the trio is absent. This is the
pattern from airSpring, absorbed by all delta springs:

```rust
pub struct ProvenanceContext {
    rhizocrypt: Option<PathBuf>,
    loamspine: Option<PathBuf>,
    sweetgrass: Option<PathBuf>,
}

impl ProvenanceContext {
    pub fn discover(socket_dir: &Path) -> Self {
        Self {
            rhizocrypt: probe_socket(socket_dir, "rhizocrypt"),
            loamspine: probe_socket(socket_dir, "loamspine"),
            sweetgrass: probe_socket(socket_dir, "sweetgrass"),
        }
    }

    pub fn is_available(&self) -> bool {
        self.rhizocrypt.is_some()
            && self.loamspine.is_some()
            && self.sweetgrass.is_some()
    }

    pub fn record_if_available(&self, artifact: &str) -> ProvenanceResult {
        if !self.is_available() {
            return ProvenanceResult { recorded: false, reason: "trio unavailable" };
        }
        // ... wire the commit flow above ...
        ProvenanceResult { recorded: true, reason: "committed" }
    }
}
```

**Rule**: Domain logic returns `Ok` with `recorded: false` when the trio is
missing — never an error. Experiments run without provenance. Provenance is
recorded when available.

---

## Shell Composition Library Support

The `nucleus_composition_lib.sh` (41 functions) provides trio wiring for
interactive compositions:

```bash
source tools/nucleus_composition_lib.sh

# Check trio availability
trio_check || warn "Provenance trio not available — continuing without"

# Record provenance (no-op if trio unavailable)
trio_record_experiment "my_experiment" "session_001"
```

The library uses the `_uds_send()` fallback chain (socat → python3 → nc)
so trio wiring works on any system with at least one transport tool.

---

## Known Issues and Workarounds

### PG-52: UDS Empty Responses — RESOLVED (April 27, 2026)

**Problem** (historical): rhizoCrypt, loamSpine, and sweetGrass returned empty
responses to JSON-RPC calls over UDS. Four springs reported independently.

**Root causes** (identified and fixed by primal teams):
- **rhizoCrypt (S49)**: Liveness gate routed all `{`-prefixed JSON to a
  liveness-only handler. Fix: plain JSON-RPC on UDS routes to the full
  `handle_newline_connection` handler.
- **loamSpine**: Double-`BufReader` on post-BTSP paths caused empty reads.
  Fix: removed duplicate buffering.
- **sweetGrass**: EOF without trailing `\n` treated as I/O error in protocol
  auto-detection. Fix: EOF is valid line-end; unknown protocol returns JSON-RPC
  error instead of silent close.

**Caller requirements**:
- Send `\n`-terminated JSON-RPC requests
- Use >=10s read timeout (sweetGrass is slower to respond)
- Pass `FAMILY_SEED` env var to rhizoCrypt when using family-scoped sockets
  (without it, BTSP gate rejects all connections)

**Validated**: Live NUCLEUS composition with all three returning valid JSON-RPC:
`dag.session.create` → session ID, `spine.create` → spine_id + genesis_hash,
`braid.create` → full JSON-LD provenance record.

**Tracking**: `primalSpring/docs/PRIMAL_GAPS.md` PG-52 RESOLVED.

### PG-48: petalTongue musl Binary Threading Panic — ADDRESSED (April 27, 2026)

**Problem** (historical): petalTongue's musl binary panicked on `winit` thread
creation in desktop mode.

**Fix**: petalTongue now uses `EventLoopBuilderExtX11::with_any_thread(true)` on
Linux, with a shared `native_options_with_any_thread()` helper. Musl builds with
`--features ui` should work on X11.

**Status**: Rebuilt musl binary harvested to plasmidBin. Verify on your target
display.

**Tracking**: `primalSpring/docs/PRIMAL_GAPS.md` PG-48 ADDRESSED.

### PG-53: Incomplete `proprioception.get` in Server Mode — RESOLVED (April 27, 2026)

**Problem** (historical): petalTongue's `proprioception.get` returned incomplete
data in `server` mode.

**Fix**: New `system/proprioception.rs` handler always returns complete JSON
including `frame_rate`, `active_scenes`, `total_frames`, `user_interactivity`,
`mode`, `uptime_secs`, and `window` fields. Dispatched via `dispatch.rs`.

**Tracking**: `primalSpring/docs/PRIMAL_GAPS.md` PG-53 RESOLVED.

---

## Cross-Spring Provenance Patterns

### Experiment Provenance (all science springs)

Every science experiment can record its lineage:

```
1. dag.session.create: "wetspring_exp403_primal_parity"
2. dag.event.append: Python baseline (content hash of expected values)
3. dag.event.append: Rust computation result (content hash of output)
4. dag.event.append: Parity comparison (depends on both above)
5. braid.create: attribute the experiment to spring + operator
6. dag.merkle.root → entry.append → braid.commit
```

### Cross-Spring Attribution

When healthSpring routes a model through wetSpring (gut diversity) →
neuralSpring (surrogate) → hotSpring (Anderson spectral), the provenance
trio tracks the full cross-spring lineage:

```
sweetGrass braid:
  - wetSpring: Creator (gut diversity model), weight 0.4
  - neuralSpring: Contributor (surrogate training), weight 0.3
  - hotSpring: Validator (spectral verification), weight 0.2
  - healthSpring: Publisher (clinical routing), weight 0.1
```

This pattern enables the "radiating attribution" model from the
`SUNCLOUD_ECONOMIC_MODEL.md` — value distribution proportional to
contribution across spring boundaries.

### Novel Ferment Transcripts

Digital objects that gain value from accumulated, verifiable history:

```
Artifact: "Gonzales Drug Candidate #7"
  └─ rhizoCrypt DAG: 47 vertices (exploration → validation → screening)
  └─ loamSpine Ledger: 12 entries (each experiment pass sealed)
  └─ sweetGrass Braid: 8 contributors across 3 springs
  └─ Loam Certificate: provenance chain from published paper → reproduction → pipeline
```

See `whitePaper/gen4/economics/NOVEL_FERMENT_TRANSCRIPTS.md` for the
economic model.

---

## Evolution Path

### Current (May 13, 2026)

- Trio primals operational, UDS IPC **fully functional** (PG-52 resolved)
- **GAP-36 wire-name reconciliation** — sweetGrass v0.7.35 resolves 10
  downstream method name variants transparently (use canonical names above)
- sweetGrass `braid.create` accepts flattened convenience fields for
  composition callers (`name`, `description`, `tags`, `source_session`,
  `source_merkle_root`)
- NFT seal round-trip verified: `braid.create` → Ed25519 witness → `braid.commit`
- `attribution.witness` accepts JH-5 Phase 3 audit events from skunkBat pipeline
- All science springs have graceful degradation wired
- Shell composition library supports trio with `_uds_send` fallback chain
- `rootpulse_commit` graph validated end-to-end
- Live NUCLEUS: `dag.session.create`, `spine.create`, `braid.create` all return
  valid JSON-RPC responses over UDS
- `FAMILY_SEED` env var required for rhizoCrypt with family-scoped sockets

### Near Term

- First-class `provenance.*` JSON-RPC surface in rhizoCrypt
- License metadata in trio (scyBorg Phase 1 — schema in existing metadata maps)
- Cross-spring provenance braids in production compositions
- plasmidBin binary rebuild cadence for trio fixes
- **Ferment transcript pattern** — upstream springs hand portable braids to
  guideStone artifacts (lithoSpore is the first consumer;
  see `handoffs/LITHOSPORE_FERMENT_TRANSCRIPT_BRAID_HANDOFF_MAY17_2026.md`)

### Medium Term

- Attribution notice generation API in sweetGrass
- Loam certificate mesh for cross-gate provenance
- `ProvenanceQueryable` trait implementation in rhizoCrypt
- sunCloud economic integration — radiating attribution becomes value distribution
- Braid-chain verification — guideStone Tier 3 provenance referencing upstream braids

---

## Related Documents

- `fossilRecord/consolidated-apr2026/SCYBORG_PROVENANCE_TRIO_GUIDANCE.md` — scyBorg licensing via trio
- `DEPLOYMENT_AND_COMPOSITION.md` — Deploy graph patterns
- `SPRING_COMPOSITION_PATTERNS.md` §7 — Graceful degradation pattern
- `GARDEN_COMPOSITION_ONRAMP.md` — Garden product integration
- `primalSpring/docs/PRIMAL_GAPS.md` — gap registry (PG-52 resolved, PG-53 resolved)
- `whitePaper/gen4/economics/NOVEL_FERMENT_TRANSCRIPTS.md` — NFT economics
- `whitePaper/economics/SUNCLOUD_ECONOMIC_MODEL.md` — Radiating attribution
- `handoffs/LITHOSPORE_FERMENT_TRANSCRIPT_BRAID_HANDOFF_MAY17_2026.md` — ferment transcript / braid handoff contract for guideStone artifacts

---

**The trio records what happened. The ledger proves it. The braid attributes it. Together they make provenance structural, not aspirational.**
