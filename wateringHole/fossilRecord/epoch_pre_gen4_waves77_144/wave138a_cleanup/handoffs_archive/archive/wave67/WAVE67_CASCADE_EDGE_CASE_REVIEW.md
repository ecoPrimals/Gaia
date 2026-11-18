# Wave 67 Cascade Edge Case Review

**Date**: 2026-06-01  
**Gate**: eastGate  
**Session**: [Wave 67 Glacial Push](1af0078e-1bfe-4b74-8d27-81f66b6c599b)  
**Reviewer**: eastGate coordination agent

---

## Session Arc

Wave 67 began as a documentation cleanup and evolved into a full glacial
push that exposed a critical gap in the ecosystem's deployment pipeline.
The progression:

1. **Doc cleanup + wateringHole handoffs** — root docs, CONTEXT.md, specs
   aligned to Wave 67 vocabulary evolution (signal→composition)
2. **Glacial cutover plan created** — `GLACIAL_CUTOVER_PLAN.md` and
   `GATE_TEAM_COORDINATION_MATRIX.md` published to wateringHole
3. **Impulse dispatch** — per-gate impulses with specific P0 assignments
4. **Cascade #1** — 33 synced, 4 ff-only failures resolved manually
   (plasmidBin, petalTongue, neuralSpring, ludoSpring)
5. **Team response** — southGate shipped all 3 P0 blockers within hours
6. **Live mesh test** — bearDog + Songbird on eastGate, strandGate auto-discovered
7. **ecoBins gap found** — source synced but binary not deployable
8. **`plasmidbin install` shipped** — closes the source→binary gap
9. **Songbird redeployed** — eb913612 installed via new pipeline
10. **TLS handshake progression** — socket fix confirmed, DIRECT mode works,
    blocked on strandGate-side TLS (their binary needs same treatment)

---

## Edge Cases Identified

### 1. Rebase-Induced Multi-Remote Divergence

**What happened**: `plasmidbin install` was committed and pushed to origin.
Forgejo had advanced independently (harvest CI). `git pull --rebase` on
each remote rewrote commit history, creating two branches with identical
content but different SHA chains.

**Cascade behavior**: `FAIL DIVERGE — forgejo(+0,-0) origin(+6,-6)`.
The temporal position matrix correctly detected the divergence, but the
`divergence_policy = "flag"` setting meant cascade could only report it.

**Impact**: The divergence is cosmetic (same tree content, different history)
but cascade treats it as a blocking condition. This repo stays in `FAIL`
status until a human force-pushes one remote to match the other.

**Root cause**: Rebase across independently-advancing remotes creates
non-fast-forwardable history. The cascade is designed to avoid this
(`ff-only` pulls), but manual intervention during cascade failures uses
`git pull --rebase` which triggers the exact pattern cascade can't resolve.

**Spec gap**: `WATERFALL_TEMPORAL_SYNC.md` Phase 5 defines `merge-rebase`
as a graduated policy but doesn't address the meta-problem: *the fix for
a cascade failure creates a different cascade failure*.

**Recommendation**: Add a `divergence_policy = "tree-parity"` option that
compares `git diff origin/main forgejo/main` and, if the tree is identical
(SHA-for-SHA file content match), auto-resolves by force-pushing the
follower to match the leader. This is safe because the content is proven
identical — only the commit metadata (rebase timestamps, parent chains)
differs.

### 2. Source Sync ≠ Binary Deployment

**What happened**: `membrane temporal.cascade` synced songBird source with
the P0 socket fix (eb913612). But the installed binary at `~/.local/bin/songbird`
was built from a pre-fix commit (May 31). The fix existed on disk in source
form but the running system couldn't use it.

**Cascade behavior**: `OK parity` — cascade correctly reports the source
repo is synced. It has no visibility into whether the binary matches the
source.

**Impact**: Phase 1 mesh validation was blocked not by a code issue but by
a deployment pipeline gap. The fix was "deployed" (source synced) but not
"installed" (binary not rebuilt).

**Root cause**: The ecoPrimals ecosystem evolved source-first. Git is the
distribution mechanism. Binary compilation and installation was handled
ad-hoc (manual `cargo build` or plasmidBin GitHub Releases). No local
"build from synced source and install" pathway existed.

**Resolution**: `plasmidbin install` subcommand — resolves local source
via `ecosystem_manifest.toml` local_path, builds with `cargo build --release`,
strips, BLAKE3 checksums, installs to `~/.local/bin`, writes provenance
sidecar. First use: deployed Songbird socket fix in 3 minutes.

**Spec gap**: `freshness.toml` tracks git HEAD SHAs but not installed
binary versions. A gate could report parity on source but be running
stale binaries. Consider adding a `[installed]` section to freshness
that records `{primal: {sha, blake3, timestamp}}` from provenance sidecars.

### 3. Impulse Ack Loss During Rebase

**What happened**: ironGate and flockGate appended `[[acks]]` to impulse
TOML files in wateringHole. When wateringHole was rebased to resolve a
push rejection, the ack sections were silently dropped from the diff.

**Cascade behavior**: Not detected — cascade reports sync status, not
content integrity.

**Impact**: Team responses would have been lost if not caught manually.
Acks are the formal record that a gate received and acted on an impulse.
Losing them breaks the coordination chain.

**Root cause**: TOML append-only sections (`[[acks]]`) are structurally
fragile under rebase. If the base commit doesn't have the acks and the
rebased commit doesn't either, the rebase "succeeds" by dropping them.
This is standard git rebase behavior but dangerous for append-only data.

**Recommendation**:
- Impulse acks should be separate files (e.g., `impulses/acks/{impulse-id}_{gate}.toml`)
  rather than appended to the original impulse. This makes them merge-safe.
- Or: `membrane impulse.ack` should commit the ack as its own commit with
  a distinctive message pattern that `temporal.cascade` can detect and
  preserve during rebase.

### 4. SECURITY_PROVIDER_MODE Discovery Gap

**What happened**: Songbird with the socket fix correctly found bearDog at
the configured `$BEARDOG_SOCKET`. But its TLS handshake routed crypto
operations through `capability.call` (Neural API mode) by default. Without
biomeOS/Neural API running, every TLS operation failed with `-32601`.

**Resolution**: `SECURITY_PROVIDER_MODE=direct` switches to direct bearDog
JSON-RPC, bypassing the Neural API proxy layer.

**Impact**: A standalone gate deployment (bearDog + Songbird, no biomeOS)
requires an environment variable that isn't documented in any deployment
guide. The default mode assumes full NUCLEUS deployment.

**Recommendation**: Songbird should auto-detect the mode: try `capability.call`
once, and if it gets `-32601`, fall back to direct mode and cache the
decision. Or: detect whether biomeOS/Neural API socket exists and choose
mode accordingly.

---

## Cascade System Evolution Priorities

Based on this session, prioritized by impact:

| Priority | Item | Spec Section | Wave Target |
|----------|------|-------------|-------------|
| P0 | `tree-parity` divergence resolution | Phase 5 | Wave 68 |
| P1 | `freshness.toml` installed binary tracking | Phase 2 | Wave 68 |
| P1 | Impulse ack as separate file (merge-safe) | IMPULSE_POTENTIAL_STANDARD | Wave 68 |
| P2 | `plasmidbin install` integration into cascade | Phase 5 (agentic) | Wave 69 |
| P2 | Auto-detect SECURITY_PROVIDER_MODE | Songbird primal | Wave 68 |
| P3 | Post-cascade binary freshness check | Phase 3 (freshness mesh) | Wave 70 |

### Tree-Parity Resolution (P0)

The most impactful single change. When cascade detects `DIVERGE` and the
diff between the two remote HEADs is empty (`git diff remote1/main remote2/main`
produces no output), the content is identical and the divergence is
history-only. In this case:

```
if tree_identical(origin_head, forgejo_head):
    force_push(follower, leader_head)   # safe: content is identical
    classify = "CONVERGE (tree-parity)"
else:
    classify = "DIVERGE"                # real content divergence, flag
```

This would have auto-resolved the plasmidBin divergence without human review.

### Installed Binary Tracking (P1)

Extend `freshness.toml`:

```toml
[installed.songbird]
commit = "eb913612eff303168e758cb463c126e46342a988"
blake3 = "1c3dc3f1d25b4b198d911acdfa248c8e7529bbe6533c787660d400c57d92514d"
timestamp = "2026-06-01T21:56:30Z"

[installed.beardog]
commit = "5e6b5a5e611349eef36657f11111f79069826ec5"
blake3 = "..."
timestamp = "..."
```

`plasmidbin install` already writes provenance sidecars to
`~/.local/share/ecoPrimals/provenance/`. `membrane temporal.cascade --check`
could read these and compare against `freshness.toml` heads to detect
source/binary drift.

---

## Team Ack Summary

Three impulses received acks during this session:

| Gate | Impulse | Key Response |
|------|---------|-------------|
| **ironGate** | Songbird socket review | Confirmed cellMembrane relay uses native UDS, no hardcoded paths. Songbird fix is southGate-owned. 208 tests pass. |
| **ironGate** | Wave 67 glacial push | S1 TLS graduated OPERATIONAL (13d). VPS relay bash→Rust DONE (Wave 65/66). S4 auth awaiting southGate bearDog config. |
| **flockGate** | Content cutover status | Metrics refreshed (85→0 drifts). sporePrint emits schema_version + merkle_root (70/70 PASS). Awaiting Phase 2 DNS. |

**Notable**: flockGate's ack resolves 2 of the 3 known-debt items in the
`sporeprint-pure-primal-parity` scenario (merkle_root and schema_version
fields now emitted). Next cascade should update the known-debt count.

---

## Net State After Session

- **836 tests**, **58 scenarios**, 33 compositions, 490+ methods
- **Phase 0**: COMPLETE — all P0 blockers cleared
- **Phase 1**: IN PROGRESS — ecoBins pipeline built, Songbird deployed,
  strandGate auto-discovered, TLS handshake reaches ServerHello stage
- **Cascade**: 36/38 parity (plasmidBin + sporePrint flagged, known)
- **New tooling**: `plasmidbin install` closes the source→binary gap
- **Active peers on LAN**: strandGate (192.168.1.132), pop-os (192.168.1.183)

*The mesh is trying to form. The infrastructure to let it succeed now exists.
What remains is propagation — every gate needs the same `plasmidbin install`
treatment, and strandGate needs the Songbird fix to complete the TLS
handshake. The cascade edge cases documented here should inform the next
wave of temporal system evolution.*
