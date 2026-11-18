# Wave 157k Pipeline Convergence — Full AAR for Team Handoff

**Date**: Aug 14, 2026 09:00 EDT | **Wave**: 157k | **From**: sporeGate (foreman)
**Scope**: Pipeline divergence root-cause + fix, rootPulse provenance trio, depot rebuild, full push
**Handoff to**: overwatch (eastGate) → primal teams

---

## Executive Summary

The build pipeline was silently diverged — the harvest reported all 13 primals as "current" while x86_64 binaries in the depot were 2+ days stale. westGate flagged it: auto-announce persistence and convergence.check riboCipher fixes were in Forgejo but not in the depot binary.

Root cause was a **serde(flatten) field name collision** in provenance.toml parsing, compounded by a stale binary in `$PATH` and lack of per-target awareness in drift detection. All three issues fixed. 13/13 x86_64 primals rebuilt, 28 binaries pushed to golgiBody depot. rootPulse provenance trio graphs created and wired into the pipeline.

**0/0/0. Pipeline autonomous. Depot current.**

---

## What Broke

### The Symptom

```
[harvest] OK — 0 built, 13 current, 0 failed
```

The cascade ran every 30 minutes, pulled all repos, and confidently reported everything was current. But the x86_64 binaries were built from Aug 12 commits — 2 days behind HEAD.

### Root Cause: Three Stacked Bugs

**Bug 1 — Serde Flatten Collision (Critical)**

`ProvenanceFile` struct:
```rust
pub struct ProvenanceFile {
    pub target: Option<String>,      // top-level
    pub builder: Option<String>,     // top-level
    #[serde(flatten)]
    pub entries: BTreeMap<String, ProvenanceEntry>,  // per-primal sections
}

pub struct ProvenanceEntry {
    pub target: Option<String>,      // COLLIDES with ProvenanceFile.target
    pub builder: Option<String>,     // COLLIDES with ProvenanceFile.builder
    pub commit: Option<String>,
    // ...
}
```

Serde's `#[serde(flatten)]` silently consumed per-entry `target`/`builder` fields for the outer struct. Every `entry.target` deserialized as `None`.

**Bug 2 — No Target-Awareness in Drift Detection**

`has_upstream_changes()` compared `provenance.commit` vs `ls-remote HEAD`. The aarch64 cross-build had written provenance entries with correct commits (matching HEAD), so the x86_64 harvest said "commit unchanged" — unable to detect the architecture mismatch.

**Bug 3 — Stale Binary in PATH**

`~/.local/bin/membrane` (Aug 3, 11 days old) shadowed `/usr/local/bin/membrane` in `$PATH`. Multiple fix-deploy cycles went unnoticed.

**Bug 4 — Write-Back Data Loss**

`update_provenance()` re-read existing entries via the broken serde path, then wrote them back with lost fields. Each harvest cycle stripped more data from provenance.toml.

---

## What We Fixed

### 1. Two-Pass TOML Parse (`depot.rs`)

`load_provenance()` now parses raw `toml::Value` first, then deserializes each `[primal]` section individually via `try_into::<ProvenanceEntry>()`. Bypasses the serde flatten collision entirely.

`update_provenance()` also uses `load_provenance()` to read existing entries, preventing field stripping on write-back.

**Files**: `crates/membrane-shadow/src/plasmid/depot.rs`

### 2. Target-Aware Drift Detection (`drift.rs`)

`has_upstream_changes()` now checks `entry.target` against `detect_target_triple()`. If they differ, the primal is marked stale regardless of commit match. Both strict and lenient variants updated.

**Files**: `crates/membrane-shadow/src/plasmid/drift.rs`

### 3. rootPulse Trio Wiring (`drift.rs` + `harvest.rs`)

Drift detection now queries `rootpulse_harvest` via neuralAPI **first** (per-target authority), falling back to flat provenance.toml. After each harvest, per-entry build records are written to `rootpulse_harvest`.

**Files**: `crates/membrane-shadow/src/plasmid/drift.rs`, `crates/membrane-shadow/src/plasmid/harvest.rs`, `crates/membrane-shadow/src/sovereignty_ledger.rs`

### 4. rootPulse Graph Definitions

Three neuralAPI graphs created:

| Graph | Purpose | Trigger |
|-------|---------|---------|
| `rootpulse_commit` | Cascade HEAD + harvest batch recording | `rootpulse.commit` |
| `rootpulse_harvest` | Per-target build provenance (canonical drift authority) | `rootpulse.harvest` |
| `rootpulse_diff` | Sovereignty verification (compare HEADs vs ledger) | `rootpulse.diff` |

All three discoverable by neuralAPI (`graph.list` returns 6 total).

**Files**: `infra/wateringHole/graphs/rootpulse_commit.toml`, `rootpulse_harvest.toml`, `rootpulse_diff.toml`

### 5. Full x86_64 Rebuild + Depot Push

- 13/13 primals rebuilt for `x86_64-unknown-linux-musl` from current HEAD
- 28 binaries pushed to golgiBody depot (31 already current across 4 architectures)
- All 14 provenance entries show `target = "x86_64-unknown-linux-musl"`
- Deployed to `/usr/local/bin`, `~/.local/bin`, and depot

---

## Commits

| Repo | SHA | Description |
|------|-----|-------------|
| cellMembrane | `3f9fa14` | fix: resolve pipeline divergence — provenance target-awareness + trio wiring |
| wateringHole | `c0c7f89` | feat: rootpulse graph definitions — provenance trio authority for drift detection |
| wateringHole | `96e051e` | aar: pipeline divergence fix — provenance target-awareness + rootPulse trio |

---

## Verification

```
harvest:          0 built, 13 current, 0 skipped, 0 failed
cascade:          15 synced, 0 failed
provenance:       14/14 entries target = "x86_64-unknown-linux-musl"
neuralAPI graphs: 6 (3 rootpulse + 3 existing)
depot push:       28 synced, 31 current, 0 failed (4 arch)
```

---

## What Primal Teams Need to Know

### For ALL Teams

The depot is now current. Your latest Forgejo commits are built and in the depot binary. The pipeline divergence that westGate flagged is resolved.

### For nestGate Team (westGate)

The `rootpulse_harvest` graph defines the query contract for per-target drift detection:

```
Query:  { primal, target } → { commit, blake3, built_at }
```

To activate the trio as a live authority, nestGate needs to implement the `index.upsert` and `index.query` step handlers. Until then, the flat file with two-pass parsing handles drift correctly.

### For rhizoCrypt Team (westGate)

`rootpulse_harvest` uses `dag.append` for build event recording. Implement the step handler to receive `PRIMAL_NAME`, `TARGET_TRIPLE`, `COMMIT_SHA`, `BLAKE3_HASH`, `BUILDER_GATE`, `BUILT_AT` params.

### For bearDog Team (ironGate)

`rootpulse_commit` and `rootpulse_harvest` use `auth.sign` for identity attestation of provenance records. Standard sign step — no new API surface needed, just wire the graph step handler.

### For sweetGrass Team (westGate)

`rootpulse_commit` uses `braid.attribute` for provenance attribution braiding. The step receives `ledger_ref` and `cas_ref` from loamSpine and nestGate.

### For biomeOS Team (eastGate)

The `graph.execute` calls from harvest now succeed for `rootpulse_commit` and `rootpulse_harvest` (graphs exist). The actual step execution depends on primal handlers being registered. biomeOS should route these graph steps to the appropriate primals.

### For cellMembrane Team (sporeGate)

The `deploy.result` gossip emission (swarmVine) is the last orchestration gap. Once biomeOS Phase 1 lands and primalSpring wires `FleetDeployHealth`, the trio pipeline will close the loop: build → record → gossip → verify.

---

## Architecture: provenance.toml → rootPulse Trio

```
BEFORE:
  provenance.toml (flat file, single-target, serde collision)
    → drift detection reads commit, ignores target
    → aarch64 build overwrites x86_64 data
    → harvest blind to architecture mismatch

NOW:
  rootpulse_harvest (neuralAPI graph, per-target)
    → drift queries trio first
    → trio returns (commit, blake3, built_at) for (primal, target)
    → FALLBACK: provenance.toml with two-pass parse (target-aware)
    → each harvest writes per-entry records to trio

FUTURE (when primal step handlers activate):
  rootpulse_harvest becomes canonical authority
  provenance.toml becomes a pure cache
  rootpulse_diff provides sovereignty verification
  rootpulse_commit closes the cascade provenance loop
```

---

## Remaining Work (Infrastructure)

| # | Item | Owner | Status |
|---|------|-------|--------|
| 1 | Primal step handlers for rootPulse trio activation | nestGate, rhizoCrypt, bearDog, sweetGrass | NEW — graph definitions ready |
| 2 | graftGate SSH key enrollment + builder.serve | physical | BLOCKED — M4 Mac Mini |
| 3 | southGate SSH key enrollment | overwatch | Port open, key not authorized |
| 4 | biomeGate SSH recovery | physical | GPU lab DOWN, eventual |
| 5 | westGate CAS enrollment | sporeGate | 50.7TB cold CAS target |
| 6 | Graduate CAS archival from SSH to TCP relay | sporeGate | Use builder.serve pattern |
| 7 | Graduate depot push from SSH to TCP relay | sporeGate | Use builder.serve pattern |
| 8 | blueGate depot rebuild | sporeGate | Builder RUNNING, needs cascade auto-dispatch |

---

*Wave 157k pipeline convergence. 0/0/0. Serde flatten collision FIXED. Target-aware drift LIVE. rootPulse trio DEFINED (3 graphs, neuralAPI discoverable). 13/13 x86_64 rebuilt. 28 pushed to depot. Pipeline autonomous. Flat provenance.toml is now a cache — trio is the designed authority. Primal teams: implement step handlers to activate.*
