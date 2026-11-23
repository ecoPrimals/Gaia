# Context Braid Standard — Ephemeral Developer State Weaving

**Authority**: primalSpring coordination
**Status**: Active (Wave 63+)
**Capability domain**: `context.*` (sweetGrass-external WEAVE)
**Lineage**: External analog of sweetGrass braids — weaves developer state across the gate mesh

---

## The Biological Model

sweetGrass braids weave meaning into data — W3C PROV-O signed provenance records that answer "what is the story of this artifact?" They compress rhizoCrypt DAG sessions into permanent, anchored records.

Context braids weave meaning into developer state — ephemeral TOML documents that answer "what is the story of this gate right now?" They compress working context into readable, superseding records that flow across the gate mesh.

```
Internal (data)                        External (developers)
─────────────────                      ─────────────────────
rhizoCrypt DAG sessions   ←→   Impulses (fire, propagate, ack)
sweetGrass braids         ←→   Context braids (weave, sense, clear)
loamSpine ledger          ←→   Git commits (permanent record)
```

### Three-Layer Coordination Model

| Layer | Pattern | Lifetime | Question answered |
|-------|---------|----------|-------------------|
| Git (loamSpine) | Linear, permanent | Forever | "What happened?" |
| Impulses (rhizoCrypt) | DAG, event-driven | Time-bounded, archived | "What should I do?" |
| Context (sweetGrass) | Woven strands, superseding | Ephemeral, auto-decay | "What's the story right now?" |

### Naming Conventions

- **context.weave** (not `set`) — you weave strands together, honoring the braid lineage
- **context.sense** (not `get`) — reading is observation, mirrors `potential.sense`
- **context.clear** (not `delete`) — braids decay/clear, they aren't destroyed

---

## Purpose

Context braids provide short-term memory for developers rotating across LAN and WAN gates. When a developer sits down at a new gate (via RustDesk or physically), `membrane context.sense` tells them what's happening without requiring manual copy-paste of guidance blurbs into each IDE.

Unlike impulses (which are action-oriented and time-bounded), context braids are state-oriented and superseding: each weave overwrites the previous braid for that gate+project, maintaining a living picture rather than an event stream.

---

## Architecture

Context braids live in `infra/wateringHole/context/`. They sync via the same waterFall cascade-pull mechanism as all other wateringHole content. Gates discover current context via `context.sense` after pull; `membrane temporal.cascade` automatically runs `context.clear --expired` after sync to decay stale braids.

```
Developer sits down → pulls wateringHole → context.sense → sees living state
Developer works     → context.weave → updates braid → pushes
Braid expires       → cascade-pull → context.clear --expired → decayed
```

---

## File Location

| Path | Purpose |
|------|---------|
| `context/{gate}/{project-slug}.toml` | One braid per gate+project intersection |

### Directory Structure

```
infra/wateringHole/context/
  flockGate/
    hotspring-compchem.toml
    membrane-shadow.toml
  eastGate/
    hotspring-solver.toml
    wateringhole-cascade.toml
  strandGate/
    wetspring-barracuda.toml
```

---

## Naming Convention

Context braid files use a **project slug** derived from the project path:

```
{project-slug}.toml
```

- **project-slug**: lowercase-kebab from the project's relative path
  - `springs/hotSpring` → `hotspring`
  - `springs/hotSpring/compChem` → `hotspring-compchem`
  - `gardens/cellMembrane` → `cellmembrane`
  - `infra/wateringHole` → `wateringhole`

The parent directory is the gate name. This gives one braid per gate per project — last writer wins.

---

## Schema

```toml
[braid]
gate = "flockGate"
project = "springs/hotSpring"
updated = "2026-05-31T09:30:00-04:00"
updated_by = "flockGate"
ttl_hours = 48
wave = 63

[strands.focus]
summary = "Validating adaptive grid solver against bench suite"
status = "active"          # active | paused | blocked | complete

[strands.breadcrumbs]
trail = [
  "compchem/solver/adaptive.rs — grid refinement loop",
  "bench/validation/run_all.sh — invocation entry point",
]

[strands.next]
actions = [
  "Run bench with --solver=adaptive",
  "Compare against baseline results in fossilRecord",
]

[strands.blockers]
items = []

[strands.notes]
body = """
eastGate pushed solver v0.3. Need to validate before Wave 64.
Using RustDesk from flockGate — bench takes ~20min per run.
"""
```

---

## Braid Header (`[braid]`)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `gate` | string | yes | Gate that wove this braid (auto-populated from identity) |
| `project` | string | yes | Project path relative to workspace root |
| `updated` | ISO-8601 | yes | When this braid was last woven |
| `updated_by` | string | yes | Gate that last updated (same as `gate` on creation) |
| `ttl_hours` | integer | yes | Hours before this braid auto-decays (default: 48) |
| `wave` | integer | yes | Ecosystem wave at time of weaving |

---

## Strand Types

Each braid weaves multiple strands together. All strands are optional except `focus`.

### `[strands.focus]` (required)

What is actively being worked on.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `summary` | string | yes | One-line description of current work |
| `status` | enum | yes | `active` / `paused` / `blocked` / `complete` |

### `[strands.breadcrumbs]`

File paths, functions, entry points another developer would need.

| Field | Type | Description |
|-------|------|-------------|
| `trail` | string[] | Ordered list of relevant code locations |

### `[strands.next]`

Upcoming actions or handoff tasks.

| Field | Type | Description |
|-------|------|-------------|
| `actions` | string[] | What should happen next |

### `[strands.blockers]`

What's preventing progress.

| Field | Type | Description |
|-------|------|-------------|
| `items` | string[] | Current blockers (empty array if none) |

### `[strands.notes]`

Freeform context that doesn't fit other strands.

| Field | Type | Description |
|-------|------|-------------|
| `body` | string | Multi-line freeform text |

---

## Key Differences from Internal sweetGrass Braids

| Aspect | Internal (sweetGrass) | External (context) |
|--------|----------------------|-------------------|
| Signing | Ed25519 via BearDog | None (ephemeral, not auditable) |
| Anchoring | loamSpine permanent | Git history only (disposable) |
| Semantics | Append-only, versioned | Last-writer-wins, superseding |
| Lifetime | Permanent (explicit deletion) | TTL-based auto-decay |
| Format | JSON-LD W3C PROV-O | Human-readable TOML |
| Purpose | Data provenance | Developer coordination |

---

## Lifecycle

1. **Woven**: `membrane context.weave` creates/overwrites the braid file for this gate+project. Auto-populates gate, timestamp, wave. Commits and pushes.
2. **Sensed**: Other gates pull wateringHole; `membrane context.sense` shows current mesh state. Cascade-pull can auto-trigger this.
3. **Superseded**: A new weave for the same gate+project overwrites the previous braid. No history is preserved in the file — git is the fossil record.
4. **Decayed**: `membrane context.clear --expired` removes braids past their TTL. Run automatically during temporal cascade sync.
5. **Cleared**: `membrane context.clear --project <path>` explicitly removes a braid (work complete, no longer relevant).

---

## Membrane CLI Commands

### `context.weave` — Weave a context braid

```
membrane context.weave --project <path> --summary "..." [options]
```

| Flag | Required | Description |
|------|----------|-------------|
| `--project <path>` | yes | Project path (e.g. `springs/hotSpring`) |
| `--summary "..."` | yes | Focus strand summary |
| `--status <status>` | no | Focus status (default: `active`) |
| `--breadcrumbs "f1,f2"` | no | Comma-separated file paths/locations |
| `--next "a1,a2"` | no | Comma-separated next actions |
| `--blockers "b1,b2"` | no | Comma-separated blockers |
| `--notes "..."` | no | Freeform notes body |
| `--ttl <hours>` | no | TTL in hours (default: 48) |

Auto-populates: `gate` (from identity), `updated` (now), `wave` (from freshness.toml).

### `context.sense` — Sense context braids

```
membrane context.sense [--gate <gate>] [--project <path>] [--all]
```

| Flag | Description |
|------|-------------|
| (none) | Show all context braids for the current gate |
| `--gate <gate>` | Show braids from a specific gate |
| `--project <path>` | Filter to a specific project across all gates |
| `--all` | Show all braids across all gates (full mesh state) |

### `context.clear` — Clear/decay context braids

```
membrane context.clear [--project <path>] [--expired]
```

| Flag | Description |
|------|-------------|
| `--project <path>` | Clear this gate's braid for a specific project |
| `--expired` | Clear all braids past their TTL (temporal cascade integration) |

---

## Git Noise Mitigation

Context braids change frequently. To manage git history:

- Commits use a standard prefix: `[context] weave flockGate/hotspring-compchem`
- `context.clear --expired` batches removals: `[context] clear 3 expired braids`
- Future: squash context commits during wave transitions (manual or automated)
- Context files are never force-pushed — standard git flow applies

---

## Cascade-Pull Integration

After wateringHole sync, `membrane temporal.cascade` should:

1. Run `membrane context.clear --expired` to decay stale braids
2. Run `membrane context.sense` to show current mesh state

This mirrors the existing `potential.sense` integration for impulses.

---

## Conventions

- One braid per gate+project. Do not create multiple files for the same intersection.
- Keep summaries under 120 characters.
- Breadcrumbs should be relative to the project root, not absolute paths.
- Next actions should be concrete and actionable (not aspirational).
- Empty arrays are valid — they signal "nothing here" rather than omitting the strand.
- Braids are ephemeral coordination — git history is the permanent record.

---

## Future: IDE/Agent Integration

Context braids are structured enough for agents to consume automatically:

- A Cursor rule or hook could run `membrane context.sense --gate $(hostname)` on session start
- The braid summary surfaces as initial context without manual paste
- This replaces the "toggle between windows and paste a guidance blurb in each IDE" pattern
- Agents can also `context.weave` when completing significant milestones, providing automatic handoff context
