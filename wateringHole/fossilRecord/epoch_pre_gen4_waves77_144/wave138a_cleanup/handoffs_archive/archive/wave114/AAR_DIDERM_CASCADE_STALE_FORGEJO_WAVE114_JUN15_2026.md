# AAR: Diderm One-Way Cascade Failure — Forgejo Stale

**Date**: 2026-06-15
**Gate**: eastGate (overwatch)
**Severity**: P1 — cascade debt, sovereignty risk
**Owner**: cellMembrane/ironGate

---

## Problem

GitHub (origin) is systematically **49 commits ahead** of Forgejo (VPS) across
**14 repositories**. Forgejo has zero unique commits — it is purely stale. This
means evolution landing on GitHub never reaches the sovereign VPS Forgejo instance.

This is NOT a merge conflict (the Wave 113 diderm AAR covered that). This is a
**one-way cascade failure** — the second remote (forgejo) is never being pushed to.

### Impact

| Category | Impact |
|----------|--------|
| Sovereignty | VPS Forgejo is our sovereign git layer. Stale = sovereignty gap. |
| Depot | plasmidBin builds from VPS repos. Stale forgejo = stale depot = stale binaries. |
| Deployment | Gates pulling from VPS (WAN gates, NUCs) get old code. |
| ABG Access | Compute infra on stale binaries means compliance gaps visible to users. |
| Audit Trail | Forgejo missing 49 commits means VPS audit trail has gaps. |

### Scope

| Repo | Commits Behind | Waves of Drift |
|------|---------------|----------------|
| toadStool | 11 | ~3-4 waves |
| rhizoCrypt | 7 | ~2-3 waves |
| bearDog | 5 | ~2 waves |
| biomeOS | 5 | ~2 waves |
| songBird | 5 | ~2 waves |
| barraCuda | 3 | ~1-2 waves |
| loamSpine | 3 | ~1 wave |
| cellMembrane | 3 | <1 wave |
| coralReef | 2 | ~1 wave |
| squirrel | 2 | <1 wave |
| nestGate | 1 | <1 wave |
| petalTongue | 1 | <1 wave |
| sweetGrass | 1 | <1 wave |
| **Total** | **49** | |

wateringHole + primalSpring are at parity (likely because overwatch pushes both manually).

---

## Root Cause Analysis

### Hypothesis 1: Gate teams push origin only

When a gate team (ironGate, eastGate, etc.) evolves a primal, the commit workflow is:
```
git commit → git push origin main
```
The `git push forgejo main` step is either:
- Not in the workflow at all (teams push origin only)
- Attempted but silently fails (SSH timeout, no error handling)
- Only triggered by cellMembrane cascade, which hasn't run since these commits landed

### Hypothesis 2: cellMembrane cascade doesn't push to forgejo

`temporal.cascade` pulls from origin and syncs local, but may not push to forgejo
as part of the cascade cycle. The `push_all_remotes()` function exists (951c96a)
but only fires on repos cellMembrane itself commits to (freshness, wateringHole).

### Hypothesis 3: VPS cascade runs infrequently

The VPS-side cascade (golgiBody) may not be running frequently enough, or may
only fetch+pull without pushing the other direction. If it only pulls from origin
and doesn't push to forgejo, the VPS forgejo stays stale.

### Most Likely

Combination of H1 + H2: gate teams push origin only, and cellMembrane cascade
doesn't include a "sync all remotes to parity" step. The diderm reconciliation
(951c96a) handles *conflicts* when both sides push, but doesn't handle the more
common case: one side is simply stale because nobody pushed to it.

### The real gap

The cascade assumes a push-to-both workflow. It should assume NOTHING about where
teams push. The peptid layer's job is to *detect drift on either side* and *heal it*
— regardless of which remote got the push. Bidirectional self-healing, not prescriptive workflow.

---

## Required Evolution (cellMembrane — peptid self-healing layer)

The peptid layer (cellMembrane cascade) must be **bidirectional and self-healing**.
Teams may push to different locations for whatever reason — that's fine. The cascade
must converge regardless of which side receives the push. If GitHub gets a push, it
syncs to Forgejo. If Forgejo gets touched, it syncs to GitHub. The K-Derm diderm
model is a living membrane that heals itself.

### First ant through (unblock Wave 114 — this week)

1. **Immediate forgejo sync**: `git push forgejo main` across all 14 repos from
   eastGate (one-time manual fix to reach parity)
2. **Bidirectional cascade**: `temporal.cascade` fetches ALL configured remotes,
   determines which is ahead, and pushes the ahead state to the behind remote.
   Direction is detected, not assumed.

### Evolve and abstract (Wave 115 — robust self-healing)

3. **Parity detection**: After fetch, compare `origin/main` vs `forgejo/main`.
   If diverged: reconcile (rebase, already shipped 951c96a). If one-way stale:
   push the fresh side to the stale side. Either direction.
4. **Event-driven convergence**: Forgejo webhook on push-receive triggers cascade
   for that repo. GitHub webhook (or periodic poll) does the same. Push to either
   side → both sides converge within one cascade cycle.
5. **Health sweep includes VCS parity**: drift > 0 commits on either side = WARN.
   Persistent drift = ERROR. Cascade auto-heals on next cycle.
6. **No "membrane push" command needed**: teams push wherever they want. The peptid
   layer notices the drift and heals it. Zero workflow change for gate teams.

### Long-term (the abstraction)

7. **Mesh-native state**: songBird mesh.publish distributes state directly —
   eliminates VCS dual-remote coordination entirely. Forgejo becomes a read-only
   mirror generated from mesh state, not a push target.
8. **Multi-gate cascade convergence**: any gate that runs cascade contributes to
   parity. No single point of failure. Whichever gate notices drift, fixes it.

---

## Immediate Action Required

```bash
# One-time sync from eastGate (push local main to forgejo for all 14 repos)
for repo in barraCuda bearDog biomeOS coralReef loamSpine nestGate \
            petalTongue rhizoCrypt songBird squirrel sweetGrass toadStool; do
  cd /home/eastgate/Development/ecoPrimals/primals/$repo
  git push forgejo main
done
cd /home/eastgate/Development/ecoPrimals/gardens/cellMembrane
git push forgejo main
```

Then cellMembrane must evolve cascade to prevent recurrence.

---

## Connection to Depot Validation (Wave 114 Exit Gate)

The depot builds from VPS source. If forgejo is stale, depot is stale, which means:
- fieldGate bootstrap pulls old binaries (bearDog without health, toadStool silent)
- grapheneGate update gets pre-compliance code
- flockGate update gets old songBird without federation fixes

**This AAR's resolution is prerequisite to the Wave 114 exit gate.**

---

## Success Criteria

| # | Criterion |
|---|-----------|
| 1 | All 14 repos: `origin/main == forgejo/main` (zero drift) |
| 2 | cellMembrane cascade includes forgejo push for all managed repos |
| 3 | Parity check in health sweep (drift > 0 = WARN) |
| 4 | plasmid.harvest rebuilds from HEAD (post-sync) produce current binaries |
