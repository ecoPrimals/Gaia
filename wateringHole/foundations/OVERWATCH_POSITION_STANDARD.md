# Overwatch Position Standard

**Authority**: Ecosystem convention  
**Status**: Active (Wave 75)  
**Prerequisites**: `ECOSYSTEM_COMMUNICATION_STANDARD.md`, `GATE_TEAM_COORDINATION_MATRIX.md`

---

## What Overwatch Is

Overwatch is the **active coordination role** for the ecosystem. It maintains
strategic awareness across all gates and teams, composes the three communication
artifacts (handoffs, FRAGOs, blurbs), tracks glacial progress, and guides the
ecosystem toward long-term goals.

Overwatch is **a position, not an identity**. It is not a gate. It is not a
primal. It is not a specific IDE session. It is a role that floats to wherever
the user is actively coordinating.

---

## What Overwatch Is Not

- **Not a fixed team**: Overwatch does not own code. It does not write Rust. It
  does not implement scenarios or fix bugs. Those are evolution teams.
- **Not a gate**: Overwatch currently operates from eastGate, but it could
  operate from any gate that has wateringHole access and cascade connectivity.
- **Not a primal**: primalSpring has an overwatch chat and an evolution chat.
  The overwatch chat coordinates. The evolution chat builds.
- **Not permanent**: If the user switches to ironGate and starts coordinating
  from there, ironGate becomes overwatch. The role follows the user.

---

## What Overwatch Does

### Core Functions

| Function | Artifact | Frequency |
|----------|----------|-----------|
| **Cascade and review** | Reads handoffs + impulses | Every sync cycle |
| **Compose blurbs** | Writes blurbs | Per wave or on demand |
| **Fire FRAGOs** | Writes impulses | When coordination needed |
| **Update readiness** | Edits GLACIAL_SHIFT_READINESS.md | After absorbing deliveries |
| **Update remaining work** | Edits WAVE*_REMAINING_WORK.md | After absorbing deliveries |
| **Update matrix** | Edits GATE_TEAM_COORDINATION_MATRIX.md | After state changes |
| **Archive completed work** | Moves handoffs/impulses to archive/ | Per wave |
| **Write gen5 papers** | Writes whitePaper/gen5/ | When achievements warrant |
| **Strategic guidance** | Identifies critical path, priorities | Continuous |

### The Overwatch Cycle

```
1. CASCADE          membrane temporal.cascade
                    ├── Pull evolution from all gates
                    └── Identify what changed (commits, handoffs, impulses)

2. ABSORB           Read new handoffs and impulse ACKs
                    ├── Understand what each team delivered
                    ├── Identify blockers, gaps, achievements
                    └── Update mental model of ecosystem state

3. UPDATE           Refresh coordination documents
                    ├── GLACIAL_SHIFT_READINESS.md
                    ├── WAVE*_REMAINING_WORK.md
                    ├── GATE_TEAM_COORDINATION_MATRIX.md
                    └── Archive completed handoffs/impulses

4. DIRECT           Compose artifacts for next cycle
                    ├── FRAGOs for gates that need to act
                    ├── Blurbs for teams that need context
                    └── Gen5 papers for achievements worth documenting

5. PUSH             Commit and cascade out
                    ├── git push wateringHole (origin + forgejo)
                    └── Teams pull on next cascade
```

---

## How Overwatch Floats

The overwatch position moves based on **where the user is actively coordinating**.
This is enabled by the ecosystem's sovereign infrastructure:

### Prerequisites for Overwatch Capability

Any gate/chat/session can run overwatch if it has:

1. **wateringHole access** — read/write to the coordination repository
2. **Cascade connectivity** — can run `membrane temporal.cascade` to sync
3. **Ecosystem manifest** — knows the full gate topology
4. **User presence** — the user is actively working in this session

### Movement Patterns

| Pattern | Example | What Happens |
|---------|---------|--------------|
| **Primary overwatch** | primalSpring on eastGate | Default coordination position. User's main strategic session. |
| **Gate-local overwatch** | cellMembrane on ironGate | User is debugging VPS. ironGate session takes overwatch for infrastructure decisions. |
| **Sprint overwatch** | biomeOS on southGate | User is driving a biomeOS sprint. southGate session coordinates dependencies. |
| **Distributed overwatch** | Multiple chats | User has parallel sessions. Each owns its domain's coordination. primalSpring remains strategic. |

### The User Is the Binding

Overwatch doesn't float autonomously. It follows the **user's attention**. When
the user opens a session and says "cascade and review," that session becomes
overwatch for the duration of the interaction. The artifacts (wateringHole docs,
FRAGOs, blurbs) are what persist across sessions — they are the continuity,
not the chat.

---

## How Sovereignty Enables Overwatch

The overwatch position is fundamentally enabled by the ecosystem's sovereign
infrastructure layers. Without sovereignty, overwatch depends on commercial
services and cannot truly float.

### Layer 1: wateringHole (Git-based SSOT)

All coordination state lives in `wateringHole/` — a git repository that
every gate can read and write. No Slack, no Jira, no external service.
The overwatch position's artifacts are git commits, not SaaS database rows.

**Implication**: Any gate that can `git pull wateringHole` can read the full
coordination history. Any gate that can `git push` can update it. Overwatch
is not locked to a single machine or service.

### Layer 2: waterFall Cascade (Sovereign Sync)

`membrane temporal.cascade` propagates state across all gates through the
Forgejo-primary push chain. No GitHub Actions, no webhooks on commercial
infrastructure. The cascade is the overwatch's primary sensing mechanism.

**Implication**: Overwatch sees all evolution through cascade pulls. It
doesn't need access to individual gate sessions — it reads what teams
committed.

### Layer 3: K-Derm Diderm Envelope (Sovereign Relay)

The three-node VPS envelope (golgiBody / peptidoglycan / golgiBody-ext)
provides the relay infrastructure for cross-gate coordination. Gates push
to Forgejo (inner membrane), peptidoglycan mediates, golgiBody-ext ships
to external.

**Implication**: Overwatch can coordinate gates that aren't on the same LAN.
flockGate (WAN) receives FRAGOs and handoffs through the same relay chain
as LAN gates.

### Layer 4: Songbird Mesh (Sovereign Discovery)

The covalent mesh enables real-time discovery of gate state. `discovery.peers`
shows which gates are online. `mesh.health_check` confirms connectivity.
Overwatch uses this to understand operational topology, not just code state.

**Implication**: Overwatch can assess which gates are available for work
assignment, which are offline (biomeGate), and which are joining (westGate).

### Layer 5: bearDog BTSP (Sovereign Trust)

bearDog's BTSP protocol provides the trust layer that makes cross-gate
coordination secure. When overwatch fires a FRAGO, the receiving gate can
verify the impulse came from a trusted source.

**Implication**: As BTSP cross-gate validation matures, FRAGOs can be
cryptographically signed and verified, making overwatch coordination
tamper-evident.

---

## Overwatch vs Evolution Teams

| Aspect | Overwatch | Evolution Team |
|--------|-----------|---------------|
| **Writes** | Handoffs, FRAGOs, blurbs, readiness docs, gen5 papers | Code, tests, experiments, crate logic |
| **Reads** | Everything — all repos, all handoffs, all commits | Primarily their own primal + wateringHole |
| **Decides** | Strategic priorities, critical path, gate assignments | Implementation approach, architecture, test strategy |
| **Produces** | Coordination artifacts | Commits, handoffs (per sprint) |
| **Persists across** | Waves, sessions, gates | One sprint/session |
| **Identity** | Floating — wherever the user coordinates | Fixed — the primal they build |

### The Parallel Chat Pattern

The user typically runs two chats per active workstation:

1. **Overwatch chat**: Cascades, reviews, composes blurbs, files FRAGOs,
   maintains readiness docs. Sees the whole ecosystem. Talks to the user
   about strategy.

2. **Evolution chat**: Receives a blurb, reads the codebase, builds and
   tests code, writes handoffs. Sees one primal deeply. Talks to the user
   about implementation.

The user is the bridge. They paste blurbs from overwatch to evolution.
They relay handoffs from evolution back to overwatch (via cascade). The
two chats never talk directly — they communicate through the three artifacts.

---

## Blurb Composition Rules (Overwatch Perspective)

When overwatch composes blurbs:

1. **One blurb per primal team** — not per gate. If strandGate runs
   toadStool, barraCuda, and coralReef, that's three blurbs.

2. **Blurbs are orders to other teams** — they describe what the team
   should do, not what overwatch will do. "Your Mission" is their work.

3. **Overwatch doesn't blurb itself** — the coordination work (cascades,
   doc updates, blurb composition) is implicit in the overwatch role.
   It doesn't need a blurb because it's the one writing them.

4. **Every team gets forward work** — zero debt is the floor, not the
   ceiling. If a team has nothing assigned, overwatch finds them work.
   Evolution never stops.

5. **Blurbs reference FRAGOs** — if there's an active FRAGO for the
   team, the blurb mentions it. The blurb provides context; the FRAGO
   provides the directive.

---

## Future: Automated Overwatch

As the ecosystem matures, pieces of overwatch can be automated:

| Function | Manual (today) | Automated (future) |
|----------|----------------|---------------------|
| Cascade + review | Agent reads commits | `membrane potential.sense` → structured report |
| Blurb composition | Agent writes markdown | `membrane context.weave` → TOML braids |
| FRAGO filing | Agent writes TOML | Impulse auto-fires on criteria (e.g., test count regression) |
| Readiness update | Agent edits markdown | Machine-readable readiness.toml + auto-update on delivery |
| Archive management | Agent moves files | TTL-based auto-archive after ACK |

The human operator remains the strategic authority. Automation handles the
mechanical parts. The overwatch position evolves from "do everything" to
"approve and steer."

---

## Changelog

| Wave | Change |
|------|--------|
| 75 | Initial: formalized from implicit practice. Codifies floating nature, sovereignty enablement, parallel chat pattern, blurb composition rules. |

---

*"Overwatch is not where you sit. It's where you look from. The position
floats because the infrastructure is sovereign — any gate, any session,
any chat can see the whole and guide it forward."*
