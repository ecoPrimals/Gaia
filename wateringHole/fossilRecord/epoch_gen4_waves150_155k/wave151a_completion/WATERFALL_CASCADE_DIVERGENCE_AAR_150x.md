# AAR: waterFall Cascade Divergence Patterns — Wave 150x

**Date**: Jul 25, 2026 | **Wave**: 150x | **From**: eastGate overwatch
**Scope**: Systematic review of all divergence classes encountered during
the Tower Atomic convergence sprint (Waves 150v–150x)

---

## Divergence Taxonomy

Five distinct divergence classes emerged during the Tower Atomic sprint.
Each maps to a specific rootPulse capability that git/Forgejo cannot provide.

### Class 1: golgiBody Auto-Publish Race

**Pattern**: golgiBody auto-publishes `heads/golgiBody.toml` on every cascade.
When eastGate commits to wateringHole and pushes, golgiBody has often already
published a new head between our last fetch and our push. Result: `rejected —
remote contains work not present locally`.

**Frequency**: 140 merge commits in wateringHole history. 4 merge commits in
the last 48 hours alone.

**Git limitation**: Git has no concept of "non-conflicting append-only files."
`heads/golgiBody.toml` never conflicts semantically — it's a monotonic
timestamp update — but git treats it as a full-file conflict requiring
fetch→merge→push.

**rootPulse solution**: DAG-based append-only ledger. Each gate publishes its
head as a signed DAG node. No merge needed — heads are naturally
non-conflicting because each gate owns its own chain. `loamSpine` anchors
the DAG state. Concurrent publishes from multiple gates are just parallel
branches in the DAG, not merge conflicts.

### Class 2: KNOWN_DEBT Calibration Thrash

**Pattern**: primalSpring `KNOWN_DEBT` is a single array shared across all
gates. Each gate runs different hardware, different binaries, different
topology. sporeGate sees 14 `graphenegate-readiness` failures (no aarch64
depot), eastGate sees 1 (only aggregate check), flockGate sees its own
counts. Every time any gate pushes a recalibration, other gates break.

**Frequency**: 34 calibration commits in primalSpring history. At least 6
in the last 48 hours of this conversation alone.

**Git limitation**: Git cannot represent "this value is gate-local." The
`KNOWN_DEBT` array is a compile-time constant — there is no mechanism for
per-gate overrides within a single source file.

**rootPulse solution**: Provenance-aware validation. Each gate publishes its
scenario results as a signed DAG attestation:
`{ gate: "eastGate", scenario: "graphenegate-readiness", failures: 1, commit: "abc123" }`.
The validator accepts attestations from any gate and computes convergence:
"all gates report ≤ expected for their topology." No shared mutable state.
`sweetGrass` semantic braids weave per-gate attestations into ecosystem-wide
health assertions.

### Class 3: Blurb Overwrite / Data Loss

**Pattern**: `ECOSYSTEM_BLURB.md` is edited by eastGate overwatch but also
receives incoming AARs and gate heads that change wateringHole. If a gate
pushes between our blurb edit and our push, the merge may silently take the
remote version of the blurb, discarding local changes.

**Frequency**: At least 3 blurb recoveries required during Wave 150v–150x
(verified via `git show <commit>` restoration).

**Git limitation**: Git merge strategies (`ort`, `recursive`) cannot
distinguish between "this file is authored by one party" and "this file is
concurrently edited." The blurb is conceptually single-writer (overwatch),
but git treats it as any other file in the tree.

**rootPulse solution**: Impulse-based coordination. The blurb becomes a
materialized view of the DAG state — generated from impulses, potentials,
and attestations rather than manually edited. `waterFall` publish cascade
already defines this flow: `git push → impulse → DAG record → context braid
→ state anchor → relay`. rootPulse makes the intermediate steps first-class,
eliminating the need for a manually-maintained blurb file.

### Class 4: AAR/Handoff Temporal Collision

**Pattern**: Multiple gates push AARs and handoffs to wateringHole
simultaneously. Gate teams don't see each other's work until the next
cascade. Result: duplicate effort (e.g., sporePrint transplant was shipped
by both eastGate and sporeGate concurrently — "glacial correction").

**Frequency**: 2 documented instances of duplicate work in Wave 150x.

**Git limitation**: Git push is atomic per-ref. There is no "pending work"
visibility — a gate cannot see another gate's uncommitted or unpushed work.

**rootPulse solution**: Context braids with TTL. Each gate publishes its
current work-in-progress as an ephemeral context braid (structured TOML,
auto-decaying). Other gates see the braid before committing, avoiding
duplicate effort. The braid is not a commit — it's a DAG-published intent
signal.

### Class 5: Cross-Repo Semantic Drift

**Pattern**: bearDog ships bond-type cipher awareness. The primalSpring
scenario `s_tower_pen_cipher_downgrade.rs` checks for `bond_type_awareness`
in the BTSP source code. But the scenario was written before the feature
existed, and the source paths it `include_str!()` may not cover the new
file where the feature was implemented.

**Frequency**: Continuous — every code evolution requires scenario
recalibration. 14 new scenarios created during 150x required calibration.

**Git limitation**: Git has no concept of "this file depends on that file
in another repo." Cross-repo dependencies are invisible to the merge
strategy.

**rootPulse solution**: `rhizoCrypt` DAG lineage tracks cross-repo
dependencies as explicit edges. When bearDog publishes a commit that
touches `btsp/negotiation.rs`, rootPulse can automatically signal
primalSpring that `s_tower_pen_cipher_downgrade.rs` needs re-evaluation.
The dependency graph is a first-class DAG structure, not a convention.

---

## By The Numbers

| Metric | Count |
|--------|-------|
| Total merge commits (wateringHole) | 140 |
| Merge commits last 48h | 4 |
| KNOWN_DEBT recalibration commits | 34 |
| Blurb data loss recoveries | 3 |
| Duplicate work incidents | 2 |
| golgiBody auto-publish heads | 30+ this wave |

---

## rootPulse Capability Map

| Divergence Class | Git Limitation | rootPulse Component | Status |
|-----------------|----------------|---------------------|--------|
| Auto-publish race | No append-only refs | `loamSpine` DAG ledger | Design phase |
| Calibration thrash | No per-gate state | `sweetGrass` semantic braids | Design phase |
| Blurb overwrite | No single-writer semantics | `waterFall` materialized views | Standard defined |
| Temporal collision | No WIP visibility | Context braids (TTL) | Standard defined |
| Cross-repo drift | No dep tracking across repos | `rhizoCrypt` DAG lineage | Design phase |

---

## Recommendations

1. **Immediate** (no rootPulse needed): Move `KNOWN_DEBT` to a TOML config
   file per gate (`config/debt/eastGate.toml`, `config/debt/sporeGate.toml`)
   so recalibrations don't conflict across gates.

2. **Near-term**: Implement impulse-based blurb generation — the blurb
   becomes a read-only artifact computed from impulses + attestations rather
   than a manually-maintained file.

3. **Medium-term**: Prototype `loamSpine` append-only ledger for gate heads
   to eliminate the golgiBody auto-publish race condition.

4. **Long-term**: Full rootPulse composition — `rhizoCrypt` + `loamSpine` +
   `sweetGrass` replace Forgejo as the coordination layer, with git as the
   storage backend only.

---

*Wave 150x: 5 divergence classes identified across Tower Atomic sprint.
All map cleanly to rootPulse capabilities. The ecosystem's own coordination
infrastructure (waterFall, impulses, context braids) already defines the
solutions — rootPulse makes them executable. This is the strongest evidence
yet that the Provenance Trio roadmap is the correct architectural direction.*
