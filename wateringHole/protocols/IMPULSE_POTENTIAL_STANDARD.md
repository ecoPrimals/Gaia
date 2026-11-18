# Impulse/Potential Standard — Inter-Gate Coordination

**Authority**: primalSpring coordination
**Status**: Active (Wave 63+)
**Capability domains**: `impulse.*` (rootPulse ACTION), `potential.*` (quorumSignal SENSE)
**Supersedes**: `SIGNAL_FRAGO_STANDARD.md` / `signal.*` commands (deprecated, aliases remain for one wave)

---

## The Biological Model

Communication across cell membranes happens via **action potentials**:

- **Impulse** — the discrete electrochemical event that fires and propagates. A gate creates an impulse (action), it travels through the membrane to other gates. Directional, time-bounded, carries a payload.
- **Potential** — the measurable voltage gradient across the membrane. You can measure resting potential before firing, sense what's pending after propagation. Pure observation.
- **Propagation** — the impulse travels along the membrane via ion channels (git push through SSH/Forgejo). The membrane itself is the transport medium.

### Triad Mapping

| Command | Domain | Metaphor |
|---------|--------|----------|
| `impulse.post` | rootPulse (ACTION) | Fire an action potential |
| `impulse.ack` | rootPulse + waterFall (ACTION+SYNC) | Receptor binding + propagate |
| `impulse.archive` | waterFall (SYNC) | Discharge spent impulses |
| `potential.sense` | quorumSignal (SENSE) | Measure membrane potential |
| `potential.check` | quorumSignal (SENSE) | Gradient health across mesh |

---

## Purpose

Impulses are machine-readable, git-mediated messages that ride alongside code pushes. They enable teams working across multiple gates to communicate state changes, action requests, and coordination directives without relying on ad-hoc handoff blurbs or out-of-band communication.

A **FRAGO** (Fragmentary Order) is an impulse subtype that amends an existing directive — short, actionable, and time-bounded.

---

## Architecture

Impulses live in `infra/wateringHole/impulses/`. They sync via the same waterFall cascade-pull mechanism as all other wateringHole content. Gates discover pending impulses via `potential.sense` on their next pull; `membrane temporal.cascade` automatically runs `potential.sense` after sync.

```
Team pushes code → fires impulse → commits to wateringHole → pushes
Other gates pull wateringHole → potential.sense → see pending impulses
```

---

## File Location

| Path | Purpose |
|------|---------|
| `impulses/active/*.toml` | Active impulses awaiting acknowledgment or expiry |
| `impulses/archive/wave{N}/*.toml` | Discharged impulses (completed, expired, or superseded) |

---

## Naming Convention

```
{ISO-timestamp}_{from-gate}__{slug}.toml
```

- **timestamp**: `YYYY-MM-DDTHH-MM` (colons replaced with dashes for filesystem safety)
- **from-gate**: the originating gate identity
- **slug**: lowercase-kebab summary (max 50 chars)

Example: `2026-06-01T14-30_eastGate__compchem-solver-ready.toml`

---

## Schema

```toml
[impulse]
id = "2026-06-01T14-30-eastGate-compchem-solver-ready"
type = "frago"           # frago | status | request | announce
priority = "routine"     # routine | priority | flash
wave = 63

[from]
gate = "eastGate"
team = "hotSpring"
project = "springs/hotSpring"
ref = "f048484"          # commit SHA — rootPulse DAG provenance (auto-populated)

[to]
gates = ["strandGate"]   # target gates, or ["*"] for all gates
teams = ["hotSpring"]    # target teams (informational filtering)

[content]
subject = "CompChem solver v0.3 ready for bench validation"
body = """
New adaptive grid solver merged to main.
Run bench suite with --solver=adaptive flag.
Blocking: strandGate validation before Wave 64 close.
"""

[meta]
created = "2026-06-01T14:30:00-04:00"
expires = "2026-06-03T00:00:00-04:00"
ack_required = true
```

The `[from].ref` field is auto-populated by `impulse.post` from the project repo's HEAD SHA, providing rootPulse DAG traceability.

---

## Impulse Types

| Type | Purpose | Typical TTL |
|------|---------|-------------|
| `frago` | Amends a standing order — action required | 24-48h |
| `status` | Informational state update — no action required | 12-24h |
| `request` | Asks for something from target gate(s) | Until fulfilled |
| `announce` | Broadcast to all gates — ecosystem-wide notice | Until next wave |
| `sync` | Divergence detected — merge coordination needed | 48h |

### SYNC Impulses (Wave 66+)

SYNC impulses are auto-fired by `membrane temporal.cascade` when a repo enters
`diverge` state (controlled by `diverge_impulse = true` in `ecosystem_manifest.toml`).
They carry structured payload enabling agentic or human resolution:

```toml
[impulse]
type = "sync"
priority = "priority"
subject = "DIVERGE: plasmidBin — origin(+2) vs forgejo(+0)"
ttl_hours = 48

[from]
gate = "eastGate"
ref = "71208e9"

[to]
gates = ["*"]

[content]
subject = "DIVERGE: plasmidBin — origin(+2) vs forgejo(+0)"
body = "Cascade detected non-ff divergence. See payload for resolution context."

[payload]
repo = "infra/plasmidBin"
diverge_type = "origin_ahead"
merge_base = "a3efdef"

[payload.remotes]
origin = "36f5b39"
forgejo = "a3efdef"

[payload.ahead]
origin = 2
forgejo = 0

[payload.policy]
repo_policy = "merge-ff"
suggested_action = "pull_origin_push_forgejo"
```

Per-repo `divergence_policy` in the manifest controls resolution behavior:

| Policy | Behavior |
|--------|----------|
| `flag` | Fire impulse + print diverge warning (default) |
| `merge-ff` | Auto-resolve if one side is a strict ancestor; impulse on non-ff |
| `merge-rebase` | Auto-rebase if no content conflicts; impulse on conflict |
| `impulse-only` | Fire impulse, never auto-resolve |
| `agentic` | Full pipeline: impulse → provenance-recorded resolution (Phase 2+) |

---

## Priority Levels

| Priority | Meaning | Expected response |
|----------|---------|-------------------|
| `routine` | Normal workflow coordination | Next work session |
| `priority` | Time-sensitive, blocking other work | Same day |
| `flash` | Critical — requires immediate attention | ASAP |

---

## Lifecycle

1. **Fired**: `membrane impulse.post` generates file in `impulses/active/`, auto-populates `[from].ref`, commits, pushes.
2. **Sensed**: Target gates pull wateringHole; `membrane potential.sense` shows pending impulses. `membrane temporal.cascade` auto-triggers this after sync.
3. **Acknowledged**: `membrane impulse.ack <id>` appends `[[acks]]` entry, commits, pushes (receptor binding).
4. **Discharged**: `membrane impulse.archive` moves expired or fully-acked impulses to `impulses/archive/wave{N}/`.
5. **Health**: `membrane potential.check` reports gradient health — expired unacked, TTL violations, volume per wave.

### Acknowledgment Format

Appended to the impulse file by the receiving gate:

```toml
[[acks]]
gate = "strandGate"
timestamp = "2026-06-01T15:02:00-04:00"
note = "Bench suite queued, results by 21:00"
```

Multiple gates can ack independently; each appends its own `[[acks]]` entry.

---

## Membrane CLI Commands

### Impulse — rootPulse ACTION

| Command | Action |
|---------|--------|
| `membrane impulse.post --to <gate> --type <type> --subject "..." [--body "..."] [--project <path>]` | Fire an impulse (auto-populates ref) |
| `membrane impulse.ack <id> [--note "..."]` | Acknowledge (receptor bind) |
| `membrane impulse.archive` | Discharge expired/fully-acked impulses |

### Potential — quorumSignal SENSE

| Command | Action |
|---------|--------|
| `membrane potential.sense [--all]` | Measure pending potential for this gate |
| `membrane potential.sense --count` | Lightweight integer count (temporal cascade integration) |
| `membrane potential.check` | Gradient health across the mesh |

---

## Backward Compatibility

Old `signal.*` commands remain as deprecated aliases for one wave:

```
$ membrane signal.post ...
DEPRECATED: signal.post is now impulse.post (see IMPULSE_POTENTIAL_STANDARD.md)
```

The parser reads both `[signal]` and `[impulse]` TOML table names, so existing signal files work without migration.

---

## Conventions

- One impulse per file. Do not batch unrelated messages.
- Keep subjects under 80 characters.
- Body is optional for simple status updates.
- `ref` is auto-populated — do not set manually unless overriding.
- Impulses are never deleted — they are discharged to preserve the coordination fossil record.
- Ack notes should be brief (what you're doing, ETA if applicable).

---

## Phase 2: Near-Realtime Delivery (Future)

When Forgejo webhooks are deployed on wateringHole:

1. Forgejo post-receive detects new files in `impulses/active/`
2. Webhook POSTs to peptidoglycan `impulse-relay` service
3. `impulse-relay` broadcasts via Songbird `mesh.publish` to subscribed gates
4. Subscribing gates' temporal cascade fires immediately, triggers `potential.sense`

No schema changes required — impulse files remain the durable store regardless of delivery mechanism.
