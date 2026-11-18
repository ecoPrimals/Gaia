# Ecosystem Communication Standard — Three-Artifact Coordination

**Authority**: Overwatch (see `OVERWATCH_POSITION_STANDARD.md`)
**Status**: Active (Wave 63+, revised Wave 68, Wave 75)
**Prerequisites**: `IMPULSE_POTENTIAL_STANDARD.md`, `CONTEXT_BRAID_STANDARD.md`, `WATERFALL_PATTERN.md`
**Lineage**: Synthesizes inter-gate coordination patterns into a unified standard

---

## The Provenance Trio of Communication

The ecosystem communicates through **three artifacts**, each with a distinct
lifetime, audience, and purpose. They mirror the provenance trio — the same
architecture that makes data trustworthy makes coordination trustworthy.

```
              Permanent ←─────────────────────────────────→ Ephemeral
              Compressed ←────────────────────────────────→ Semantic

   ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
   │  HANDOFFS         │   │  FRAGOs           │   │  BLURBS           │
   │  (loamSpine)      │   │  (rhizoCrypt)     │   │  (sweetGrass)     │
   │                   │   │                   │   │                   │
   │  "What happened   │   │  "What to do      │   │  "Here's the      │
   │   and why"        │   │   next"           │   │   context you need │
   │                   │   │                   │   │   right now"       │
   │  Fossil record    │   │  Work DAG         │   │  Semantic seed     │
   │  Forever          │   │  Time-bounded     │   │  Session-scoped    │
   │  Notebook         │   │  Async/concurrent │   │  Copy-paste ready  │
   └──────────────────┘   └──────────────────┘   └──────────────────┘
         │                       │                       │
         │   All three sync via waterFall temporal cascade   │
         └───────────────────────┴───────────────────────┘
```

---

## Artifact 1: Handoffs (Fossil Record)

**What they are**: Long-form markdown documents that capture a complete sprint,
evolution pass, or decision arc. They live in repos and in `wateringHole/handoffs/`.
They are the **notebook** — the compressed linear history of how a project evolved.

**Provenance analog**: loamSpine. Anchored, immutable, compressed. The permanent
ledger you can always trace back to.

**Audience**: Future teams, future selves, archaeological review. Any team picking
up a primal months later reads its handoffs to understand the full story.

**Lifetime**: Forever. Handoffs are never deleted. Completed waves move to
`handoffs/archive/wave{N}/`.

**Schema**: Markdown, structured by convention:

```markdown
# {PRIMAL}_V{VERSION}_WAVE{N}_{SUMMARY}_{DATE}.md

## Summary
What was accomplished in this sprint/wave.

## Changes
Detailed list of what changed, with file references.

## Test Results
What passed, what's known-debt, what's blocked.

## Next Steps
What the next team should pick up.

## Dependencies
What upstream/downstream primals are affected.
```

**Location**:
- Per-repo: `{repo}/handoffs/` or repo root (varies by primal)
- Centralized: `wateringHole/handoffs/`
- Archive: `wateringHole/handoffs/archive/wave{N}/`

**When to write**: After completing a sprint, wave, or significant evolution pass.
Before handing a primal to another gate or team.

**Current count**: 17 active handoffs + archived waves in `handoffs/archive/`.

---

## Artifact 2: FRAGOs (Work DAG)

**What they are**: Machine-readable TOML impulses that fire action directives
between gates. FRAGOs (Fragmentary Orders) are the primary subtype — short,
actionable, time-bounded amendments to the work plan. They enable **async and
concurrent** coordination: multiple gates work in parallel, FRAGOs keep them
synchronized without blocking.

**Provenance analog**: rhizoCrypt. DAG-structured, event-driven, propagating.
Fire, acknowledge, archive — like a provenance session that branches and merges.

**Audience**: Gate teams currently working. FRAGOs answer "what should I do
next?" and "what changed that affects me?"

**Lifetime**: Active until acknowledged, archived per wave. Active FRAGOs live
in `impulses/active/`, spent ones move to `impulses/archived/`.

**Schema**: TOML per `IMPULSE_POTENTIAL_STANDARD.md`:

```toml
[impulse]
id = "2026-06-02T10-56-eastGate-wave68-subject"
type = "frago"
priority = "medium"
wave = 68

[from]
gate = "eastGate"

[to]
gates = ["southGate"]

[content]
subject = "What needs to happen"
body = """Detailed action items and context."""

[meta]
created = "2026-06-02T10:56:00-04:00"
ack_required = true
```

**Location**: `wateringHole/impulses/active/` and `wateringHole/impulses/archived/`

**Transport**: Git push through waterFall cascade. Auto-discovered via
`membrane potential.sense` after cascade sync.

**When to fire**: When another gate needs to act on your work. Rebuild a binary,
validate a pattern, evolve a dependency, acknowledge a blocker resolution.

**Current count**: 5 active, 7 archived.

---

## Artifact 3: Blurbs (Semantic Seed)

**What they are**: Short, high-semantic-density context prompts designed for
**copy-paste into an AI dev team's IDE**. A blurb is the minimum viable context
that lets a fresh team on any gate understand what they own, what's happened,
and what to do next — without reading the full handoff history.

**Provenance analog**: sweetGrass. Semantic, woven, context-rich. Like a
sweetGrass braid that captures the *meaning* of the current state, not just
the facts.

**Audience**: AI development teams (Cursor agents) at gates. The human operator
copies the blurb and pastes it as the opening prompt in a new session.

**Lifetime**: Session-scoped. A blurb is valid for one sprint context window.
When the work it describes is complete, the blurb is spent. Unlike handoffs,
blurbs are not archived — their content is compressed into the next handoff.

**Schema**: Freeform markdown, optimized for AI comprehension:

```markdown
# {Gate} — {Primal/Project} Context

## You Are
Brief identity: what primal, what gate, what role in the ecosystem.

## Current State
What wave, what's been done, what's the latest version.

## Your Mission
Concrete next steps — what to build, fix, evolve.

## Key Files
Critical paths the agent needs to read first.

## Coordination
Active FRAGOs to check, gates to acknowledge, blockers.
```

**Location**: Not persisted in git. Blurbs are composed by the overwatch position
(see `OVERWATCH_POSITION_STANDARD.md`) or by the operator, then delivered via
copy-paste to the target gate's IDE session.

**When to compose**: When bootstrapping a fresh team on a gate. When a primal
changes ownership between gates. When a new wave begins and teams need
direction.

---

## The Graduation Path: Blurbs → Context Braids

Blurbs are the **pragmatic present**. Context braids are the **automated future**.

Today, blurbs work because:
- They require zero tooling (copy-paste)
- They fit the operator's workflow (compose in one session, paste to another)
- They're high-semantic — an AI agent gets full context in one prompt

Context braids (`CONTEXT_BRAID_STANDARD.md`) are the structured automation of
blurbs. When fully wired, `membrane context.weave` replaces manual blurb
composition, and `membrane context.sense` replaces copy-paste delivery:

| Aspect | Blurb (today) | Context Braid (graduated) |
|--------|---------------|---------------------------|
| Creation | Agent or human composes markdown | `membrane context.weave` writes TOML |
| Delivery | Copy-paste to IDE | `membrane context.sense` on session start |
| Schema | Freeform, convention-based | Structured TOML, machine-validated |
| Discovery | Human relay | Auto-discovered after cascade sync |
| Lifecycle | Manual (expires with session) | TTL auto-decay, superseding |
| Provenance | None (ephemeral) | sweetGrass-anchored on completion |

**The blurb is not deprecated.** It is the pragmatic interface until context
braids are fully reliable. Even after graduation, blurbs remain the fallback —
any team can always be bootstrapped with a paste.

---

## How the Three Artifacts Interact

```
                    ┌─────────────────────────┐
                    │   Operator / Overwatch   │
                    └─────┬───────┬───────┬───┘
                          │       │       │
                   writes │  fires│  composes
                          │       │       │
                    ┌─────▼──┐ ┌──▼────┐ ┌▼───────┐
                    │Handoff │ │ FRAGO │ │ Blurb  │
                    │  .md   │ │ .toml │ │  .md   │
                    └───┬────┘ └───┬───┘ └───┬────┘
                        │         │         │
                    committed  committed  copy-pasted
                    to repo    to wH      to IDE
                        │         │         │
                    ┌───▼─────────▼───┐  ┌──▼──────────┐
                    │  waterFall      │  │ Target gate  │
                    │  temporal       │  │ AI team gets │
                    │  cascade        │  │ instant      │
                    │  (all gates)    │  │ context      │
                    └─────────────────┘  └──────────────┘
```

### The Sprint Cycle

1. **Sprint begins**: Operator composes **blurbs** per gate, paste-delivers to teams
2. **Teams work**: Code evolves, commits accumulate, progress happens
3. **Coordination needed**: Gate fires **FRAGO** when another gate must act
4. **Sprint ends**: Team writes **handoff** — compresses the sprint into fossil record
5. **Wave archived**: FRAGOs move to `archived/`, handoffs move to `archive/wave{N}/`
6. **Next wave**: Operator reads handoffs, composes new blurbs, fires new FRAGOs

### Escalation Ladder

When something needs attention, the artifact type determines urgency:

| Urgency | Artifact | Action |
|---------|----------|--------|
| **Low** — "for the record" | Handoff | Commit to repo. Teams read on next pickup. |
| **Medium** — "do this when you can" | FRAGO (priority: low/medium) | Fire impulse. Team sees on next cascade pull. |
| **High** — "do this now" | FRAGO (priority: high/critical) | Fire impulse + direct blurb delivery. |
| **Immediate** — "context crash" | Blurb | Copy-paste directly to gate IDE. |

---

## The Internal/External Mirror

Each artifact mirrors a provenance trio primal that handles the *internal*
(data) equivalent:

| Internal (data primal) | External (developer artifact) | Shared Pattern |
|------------------------|-------------------------------|----------------|
| loamSpine: anchored linear ledger | Handoffs: compressed sprint history | Permanent, immutable, traceable |
| rhizoCrypt: DAG session events | FRAGOs: async work coordination | Event-driven, branching, acknowledged |
| sweetGrass: semantic content braids | Blurbs: high-context AI prompts | Meaning-rich, woven, session-scoped |

This symmetry is intentional. The ecosystem's internal organs and its external
communication use the same architecture. When a pattern works for data, it
works for people.

---

## Neural API Triad Mapping

The three artifacts map to the Neural API triad:

| Artifact | Triad Domain | Direction | CLI |
|----------|-------------|-----------|-----|
| Handoffs | rootPulse (ACTION) | Create permanent record | `git commit`, `git push` |
| FRAGOs | rootPulse + quorumSignal | Fire + sense | `membrane impulse.post`, `membrane potential.sense` |
| Blurbs | quorumSignal (SENSE) | Observe and bootstrap | `membrane context.weave`, `membrane context.sense` |
| All three | waterFall (SYNC) | Propagate across mesh | `membrane temporal.cascade` |

The triad cycle with all three artifacts:

```
1. Gate A completes work
   ├── git commit + push             (rP: permanent record)
   ├── writes handoff .md            (rP: fossil record of sprint)
   ├── membrane impulse.post         (rP: fire FRAGO to downstream gates)
   └── operator composes blurb       (qS: semantic seed for next team)

2. waterFall propagates              (wF: temporal cascade sync)
   ├── git changes flow to all gates
   ├── handoff .md appears in wateringHole/handoffs/
   └── FRAGO TOML appears in impulses/active/

3. Gate B receives context
   ├── potential.sense → "2 pending FRAGOs"
   ├── operator pastes blurb → AI team has instant context
   └── team reads handoff for deep history if needed
```

---

## When to Use Each Artifact

| Situation | Artifact | Why |
|-----------|----------|-----|
| Completed a sprint/wave | Handoff | Permanent record for future teams |
| Another gate needs to rebuild | FRAGO | Actionable, auto-discovered on cascade |
| Requesting validation | FRAGO (AUDIT) | Directed, needs acknowledgment |
| Bootstrapping a fresh AI team | Blurb | High-context, copy-paste ready |
| Primal changing gate ownership | Handoff + Blurb | History (handoff) + immediate context (blurb) |
| Architecture decision made | Handoff + commit | Permanent, lives in handoffs/ |
| "Pull wateringHole and rebuild" | FRAGO | Replaces a Slack message |
| "Don't touch X, mid-sprint" | FRAGO (SYNC) | Coordination boundary |

### Anti-Patterns

- **Don't use FRAGOs for permanent decisions** — write a handoff, commit to git
- **Don't use blurbs for action directives** — fire a FRAGO (blurbs are context, not orders)
- **Don't use handoffs for urgent coordination** — fire a FRAGO (handoffs are read later)
- **Don't rely on blurbs for provenance** — they vanish with the session; the handoff is the record
- **Don't skip the blurb** — a FRAGO tells a team *what to do* but not *who they are*; the blurb provides identity and context

---

## VPS Mediator Pattern (Phase 4 Inversion — Wave 63+)

All three artifacts propagate through the VPS as sovereign mediator:

```
Gate ──covalent──→ golgiBody-inner (cis: Forgejo)
                       │ metallic
                   peptidoglycan (structural: sync + impulse cascade)
                       │ ionic
                   golgiBody-ext (trans: ships to extracellular)
                       │ weak
                   GitHub (external linear ledger)
```

**Push Target**: Gates push only to Forgejo (`push_target = "forgejo"` in manifest).
The K-Derm diderm relay chain propagates through all three VPS nodes with proper
bond-type degradation. Gates no longer need GitHub SSH keys.

**GitHub as External Linear Ledger**: GitHub serves the same conceptual role as
loamSpine → BTC/ETH stamping: an external, immutable, publicly-discoverable
record of ecosystem evolution. It is a trailing mirror, not the source of truth.

| Operation | Target | Bond | Mechanism |
|-----------|--------|------|-----------|
| `git push` | Forgejo (inner) | Covalent | Gate SSH to golgiBody |
| Sync relay | peptidoglycan | Metallic | Post-receive webhook → `pepti-sync-relay.sh` |
| GitHub mirror | GitHub | Weak | `ext-github-push.sh` on golgiBody-ext |
| Impulse relay | Mesh | — | peptidoglycan `potential.sense` → songbird |
| Context sync | All gates | — | waterFall temporal cascade |

See `WATERFALL_PATTERN.md` Phase 4, `hooks/forgejo/README.md` for relay chain,
and `graphs/waterfall_publish.toml` for cascade specification.

---

## Primal Graduation Path

Today, all three artifacts are implemented as direct filesystem operations in
`membrane-shadow`. As primals graduate, the operations compose through biomeOS graphs:

| Artifact | Shadow (today) | Graduated (future) |
|----------|----------------|---------------------|
| FRAGOs | `membrane impulse.post` writes TOML, git pushes | bearDog signs, rhizoCrypt records DAG event, songbird relays, nestGate stores |
| Blurbs | operator copy-paste | `membrane context.weave` writes TOML, `context.sense` auto-delivers |
| Handoffs | manual markdown in repo | sweetGrass validates, loamSpine anchors, sporePrint certifies |
| Git | `git commit/push` | rootPulse graph: dehydrate → sign → store → commit → attribute |

The graduation graphs are defined in:
- `infra/wateringHole/graphs/impulse_post_signed.toml`
- `infra/wateringHole/graphs/context_weave_anchored.toml`
- `infra/wateringHole/graphs/waterfall_publish.toml` (full cascade composition)

The NeuralBridge in `membrane-shadow` (feature-gated) already attempts to route
through biomeOS before falling back to shadow implementations.

---

## K-NOME Interaction

The three-artifact model formalizes the K-NOME programming pattern for multi-gate
development:

**Before** (manual K-NOME):
1. Human composes a long context blurb
2. Pastes it into a fresh IDE chat
3. AI reads specs, docs, wateringHole standards
4. AI works, produces results
5. Human copies results, pastes to next gate

**Current** (hybrid K-NOME):
1. Overwatch fires FRAGOs with action directives (async, all gates)
2. Overwatch composes blurbs with semantic context (per gate)
3. Human pastes blurb to target gate IDE → AI has instant identity + mission
4. AI reads FRAGOs via cascade → knows what to do
5. AI reads handoffs for deep history → knows why
6. AI works, produces handoff, overwatch fires completion FRAGO
7. waterFall propagates everything to all gates

**Future** (automated K-NOME):
1. `membrane impulse.post` fires FRAGOs with action directives
2. `membrane context.weave` writes structured braids (replaces blurbs)
3. AI on receiving gate runs `context.sense` → instant context (no paste)
4. AI reads impulses via `potential.sense` → knows what to do
5. AI works, weaves its own context, fires completion impulse
6. waterFall propagates everything to all gates

---

## Standards Reference

| Standard | File | Domain |
|----------|------|--------|
| This document | `ECOSYSTEM_COMMUNICATION_STANDARD.md` | Unified coordination model |
| Overwatch Position | `OVERWATCH_POSITION_STANDARD.md` | Floating coordination role definition |
| Impulse/Potential | `IMPULSE_POTENTIAL_STANDARD.md` | FRAGOs: event-driven work DAG |
| Context Braids | `CONTEXT_BRAID_STANDARD.md` | Blurbs → braids graduation target |
| WaterFall Pattern | `WATERFALL_PATTERN.md` | Transport: temporal sync across mesh |
| Semantic Methods | `SEMANTIC_METHOD_NAMING_STANDARD.md` | Method naming conventions |
| Capability Registry | `primalSpring/config/capability_registry.toml` | Registered capabilities |
| Gate Coordination | `GATE_TEAM_COORDINATION_MATRIX.md` | Gate/team/hardware/project SSOT |
| Gate Ownership | `GATE_SPRING_OWNERSHIP.md` | Canonical spring routing |

---

## Changelog

| Wave | Change |
|------|--------|
| 75 | Overwatch position formalized as separate standard (`OVERWATCH_POSITION_STANDARD.md`). Authority updated from "primalSpring coordination" to "Overwatch" — reflecting the floating, sovereign-enabled nature of the role. |
| 68 | Revised: three artifacts (Handoffs, FRAGOs, Blurbs) formally codified with provenance trio mapping. Blurbs recognized as pragmatic sweetGrass layer with graduation path to context braids. Escalation ladder, sprint cycle, anti-patterns updated. |
| 63 | Initial: three-layer model (commits, impulses, context braids) synthesized from ecosystem practice. |

---

*"Three artifacts, three lifetimes, three audiences — one water.
The handoff remembers. The FRAGO directs. The blurb ignites."*
