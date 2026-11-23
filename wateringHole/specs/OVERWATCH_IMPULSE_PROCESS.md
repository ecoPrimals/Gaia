# Overwatch Impulse-Reading Process (Phase B)

**Date**: Aug 7, 2026 | **Wave**: 157a | **Author**: eastGate overwatch
**Status**: PROCESS DEFINITION — replaces manual git-pull cascade

---

## The Change

**Before** (manual, gate-coupled):
```
overwatch IDE → git fetch 15 repos → read diffs → write blurb → push wateringHole
```

**After** (impulse-driven, gate-decoupled):
```
sporeGate timer → membrane temporal.cascade → impulses + freshness
overwatch reads impulses/active/ + heads/*.toml → strategic review → blurb
primalSpring handles deployment validation on eastGate
```

Overwatch stops doing qS (sensing) and wF (syncing). biomeOS Neural API
orchestrates those — `temporal.check`, `temporal.classify`, `impulse.post`,
`freshness.publish` are all capability calls routed through the Neural API.
The triad (qS/wF/rP) is the what. Neural API is the how.

Overwatch does the thinking: reviewing deltas, writing strategic blurbs,
updating orthogonal review, making decisions about convergence order.

---

## What Overwatch Reads

### 1. Active Impulses

**Path**: `infra/wateringHole/impulses/active/*.toml`

These are the qS output — machine-generated SYNC impulses fired by
`membrane temporal.cascade` when divergence is detected.

```
infra/wateringHole/impulses/active/
├── 2026-08-07T08-54_strandGate__diverge-wateringHole.toml
├── 2026-08-07T08-10_strandGate__diverge-wateringHole.toml
└── ...
```

Each impulse contains:
- `[from]` — which gate, which repo, which commit
- `[payload]` — diverge type, repo policy, suggested action
- `[payload.remotes]` — HEAD SHAs per remote
- `[payload.ahead]` — commit distance per remote
- `[meta]` — timestamp, ack required

**Overwatch action**: Read all active impulses. Acknowledged impulses move
to `impulses/resolved/`. Unacknowledged impulses represent unresolved
ecosystem drift.

### 2. Gate Freshness Heads

**Path**: `infra/wateringHole/heads/*.toml`

These are the wF output — per-gate snapshots of repo HEAD SHAs, deploy
status, tower health, depot state, and service status.

```
infra/wateringHole/heads/
├── sporeGate.toml     ← sync_mediator, primary freshness source
├── eastGate.toml
├── ironGate.toml
├── southGate.toml
├── golgiBody.toml
└── flockGate.toml
```

Each gate file contains:
- `[heads]` — per-repo HEAD SHAs
- `[deploy]` — version strings for key primals
- `[tower]` — Tower Atomic status
- `[gate_status]` — probe results (alive, depot, sovereignty, mesh)
- `[harvest]` — last depot rebuild details

**Overwatch action**: Compare `[heads]` across gates to see which gates
are behind. Compare `[deploy]` versions to see which gates need updates.
The `[gate_status]` section is the machine-generated health check.

### 3. Wave Identity

**Path**: `infra/wateringHole/wave.toml`

The ecosystem's current wave identity. Updated by overwatch when the
posture changes.

### 4. Ecosystem Manifest

**Path**: `infra/wateringHole/ecosystem_manifest.toml`

The `[sync]` section defines divergence policies. The `[topology.roles]`
section defines which gate does what. Overwatch uses this as the
source of truth for team/gate assignments.

---

## Overwatch Cascade Workflow (New)

### Step 1: Pull wateringHole only

```bash
cd infra/wateringHole && git pull --rebase
```

This is the ONLY repo overwatch pulls directly. Everything else is
sensed via impulses and freshness files that the cascade timer pushes
into wateringHole.

### Step 2: Read impulses

```bash
ls impulses/active/
```

Each file is a divergence signal. Read the payload to understand:
- Which repo diverged
- On which gate
- What the suggested action is
- Whether it's been acknowledged

### Step 3: Read freshness across gates

```bash
head -20 heads/sporeGate.toml heads/eastGate.toml heads/ironGate.toml
```

Compare `[heads]` sections across gates. Gates with older SHAs need
deployment. Gates with different versions need sync.

### Step 4: Strategic review

With impulses and freshness data, overwatch knows:
- Which repos have new work (impulses fired)
- Which gates are behind (freshness comparison)
- What the divergence policy recommends (impulse payload)
- Whether previous impulses are resolved (active vs resolved)

This is the input for the orthogonal review and blurb.

### Step 5: Write blurb from impulse data

The blurb's temporal section comes from impulse data, not from
reading git logs in 15 repos. Example:

```markdown
## TEMPORAL: impulse-sensed since last review

| Impulse | Gate | Repo | Action | Status |
|---------|------|------|--------|--------|
| 08:54 SYNC | strandGate | wateringHole | agentic_resolve | UNACKED |
| 08:10 SYNC | strandGate | wateringHole | agentic_resolve | UNACKED |
```

### Step 6: Acknowledge resolved impulses

Move resolved impulses from `active/` to `resolved/`:

```bash
mv impulses/active/<impulse>.toml impulses/resolved/
git add impulses/ && git commit -m "ack: resolve <N> sync impulses"
```

---

## What Overwatch Does NOT Do Anymore

| Old Pattern | New Owner |
|-------------|-----------|
| `git fetch` across 15+ repos | sporeGate cascade timer (qS/wF) |
| Cross-arch `cargo check` on all primals | primalSpring team / builder gates |
| Deploy validation on eastGate | primalSpring team |
| Depot rebuild | sporeGate golgi + blueGate builder |
| Gate deployment | Gate teams (pull from golgi depot) |

## What Overwatch STILL Does

| Responsibility | Why |
|----------------|-----|
| Strategic review (orthogonal, glacial, fossilization) | Human judgment |
| Blurb writing (posture, framing, priority) | Human judgment |
| Convergence ordering (which primals evolve first) | Ecosystem architecture |
| Glacial goal management (add, graduate, deprecate) | Long-term vision |
| Wave identity (wave.toml posture) | Ecosystem identity |
| Impulse acknowledgment | Decision authority |
| Spec writing (G68, triad activation, etc.) | Architecture |

---

## Transition

Phase B is a process change, not a code change. We start reading
impulses and freshness instead of pulling repos. The cascade timer
(Phase A) must be active on sporeGate first.

**Interim** (until Phase A is active): overwatch continues manual
cascade but treats it as temporary. We still write impulses and
freshness as if the timer were running.

**After Phase A**: overwatch pulls only wateringHole and reads the
machine-generated impulse/freshness data.

---

*Phase B of overwatch cascade automation. Overwatch reads impulses
(qS output) and freshness (wF output) instead of pulling repos.
The primals sense and sync. Overwatch thinks.*
