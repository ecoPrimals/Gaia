# Mesh Deployment Standard — Team & Gate Handoff

**Authority**: wateringHole consensus (Wave 66, reviewed 155h)
**Version**: 1.0.0
**Applies to**: All gates, all teams, VPS nodes, new gate onboarding

---

## Purpose

This standard defines how work is delegated to teams and gates across the
mesh. It covers the full lifecycle: task assignment via impulse, team
bootstrap on a gate, work execution, delivery via cascade, and validation.

The goal is zero-friction handoff: a team on any gate should receive work,
execute it, and deliver results without manual coordination from eastGate.

---

## 1. The Handoff Lifecycle

```
eastGate                    targetGate (team)
   │                              │
   ├─ impulse.post ──────────────▶│  FRAGO with scope + acceptance criteria
   │                              │
   │                    potential.sense  │  Team reads pending impulse
   │                              │
   │◀── impulse.ack ─────────────┤  Team acknowledges + begins work
   │                              │
   │                    context.weave   │  Team weaves context braid (progress)
   │                              │
   │                    git push forgejo│  Team pushes code to periplasm
   │                              │
   │  temporal.cascade            │
   ├─ (auto-pull) ◀──────────────┤  eastGate cascades the delivery
   │                              │
   │  potential.sense             │  eastGate sees acked impulse
   │                              │
   │  impulse.archive             │  eastGate discharges spent impulse
   └──────────────────────────────┘
```

---

## 2. Firing an Impulse (Task Assignment)

Use `membrane impulse.post` to delegate work. The impulse is committed to
`wateringHole/impulses/active/` and propagated via the cascade.

```bash
membrane impulse.post \
  --to <targetGate> \
  --type frago \
  --subject "<one-line task summary>"
```

### Impulse Types

| Type | Use | Expectation |
|---|---|---|
| `frago` | Fragmentary order — new task or scope change | Ack required, work expected |
| `sitrep` | Situation report — status update | Informational, no ack needed |
| `aar` | After-action review — completed work summary | Informational, archive after read |

### Impulse Body

The `--subject` is the headline. For detailed scope, edit the generated TOML
file in `impulses/active/` before committing. Include:

- **Scope**: What files/modules/repos are involved
- **Acceptance criteria**: What "done" looks like
- **Priority**: `critical` / `routine` / `low`
- **Deadline**: Wave number or date (optional)

---

## 3. Receiving Work (Team Bootstrap)

When a team spins up on a gate, they:

### 3a. Cascade Pull

```bash
membrane temporal.cascade
```

This pulls all repos for the gate's manifest profile, including any new
impulses in `wateringHole/impulses/active/`.

### 3b. Sense Pending Impulses

```bash
membrane potential.sense --all
```

Shows all pending impulses addressed to this gate. The team reads the FRAGO
and understands the scope.

### 3c. Acknowledge

```bash
membrane impulse.ack <impulse-id> --note "Starting work on relay evolution"
```

The ack is committed to wateringHole and propagated on the next cascade.
eastGate (or any gate) can see acked impulses via `potential.sense`.

### 3d. Sense Context

```bash
membrane context.sense --all
```

Shows active context braids from all gates — what other teams are working on,
where they are, and what's blocking them. This prevents collision.

---

## 4. Working (Execution)

### 4a. Weave Context Braids

As work progresses, the team weaves braids so other gates can sense state:

```bash
membrane context.weave \
  --project gardens/cellMembrane \
  --summary "relay.rs complete, 3 subcommands, 400 lines"
```

Braids are ephemeral (48h TTL by default) and auto-decay. They're stored in
`wateringHole/context/<gateName>/`.

### 4b. Push to Forgejo

All code pushes go to Forgejo only. The K-Derm relay chain handles GitHub
propagation automatically:

```bash
git push forgejo main
```

The relay chain: gate → golgiBody (covalent) → peptidoglycan (metallic) →
golgiBody-ext (ionic) → GitHub (weak).

### 4c. Handoff Documents

For significant deliveries, write a handoff document:

```
wateringHole/handoffs/WAVE<NN>_<PROJECT>_<SUMMARY>_<DATE>.md
```

Include: what changed, what tests pass, what remains, and acceptance evidence.
After the next wave, archive it to `handoffs/archive/wave<NN>/`.

---

## 5. Receiving Deliveries (Cascade Pull)

When a team pushes to Forgejo, any gate can pull the delivery:

```bash
membrane temporal.cascade
```

The cascade is manifest-driven — each gate pulls only the repos in its profile.
Repos not in the gate's profile are ignored.

### Conflict Resolution

If `temporal.cascade` reports `FAIL pull forgejo failed (ff-only)`:

```bash
cd <repo>
git stash
git pull --rebase forgejo main
git stash pop
```

Or accept upstream wholesale:

```bash
git checkout --theirs <conflicting-file>
```

---

## 6. Validation

### 6a. Test Suite

After absorbing a delivery, run the relevant test suite:

```bash
cargo test --workspace          # In the delivered repo
```

For ecosystem-wide validation:

```bash
cd springs/primalSpring
cargo test --workspace          # 838+ tests, 57 scenarios
```

### 6b. Temporal Check

Verify all repos are temporally aligned:

```bash
membrane temporal.check
```

This shows the HEAD position of each repo across all remotes (forgejo, origin).
Divergence is flagged.

### 6c. Potential Gradient

Check ecosystem health:

```bash
membrane potential.check
```

Shows active impulse count, ack status, and wave distribution. A healthy
gradient has zero unacked impulses older than 48 hours.

---

## 7. Gate Profiles

Each gate has a repo profile in `ecosystem_manifest.toml` under
`[gates.<name>]`. The profile determines which repos cascade to that gate.

### Adding a New Gate

1. Add the gate profile to `ecosystem_manifest.toml`:

```toml
[gates.newGate]
repos = [
    "nestGate", "wateringHole", "plasmidBin",
    "bearDog", "songBird", "biomeOS",
    # ... repos this gate needs
]
```

2. On the new gate:

```bash
echo "newGate" > .gate
membrane temporal.cascade --clone-missing
```

3. Fire a sitrep to announce:

```bash
membrane impulse.post --to eastGate --type sitrep \
  --subject "newGate online, 22 repos synced"
```

### Gate Types

| Type | Bond | Example | Role |
|---|---|---|---|
| Physical (LAN) | Covalent | eastGate, ironGate | Full development |
| Physical (WAN) | Covalent (SSH) | flockGate | Remote development |
| VPS Inner | Metallic | golgiBody | Forgejo, primals |
| VPS Mediator | Metallic | peptidoglycan | Relay, builds |
| VPS Outer | Ionic/Weak | golgiBody-ext | DNS, sporePrint, GitHub push |

---

## 8. Team Patterns

### Single-Team Sprint

One team works on one repo. Standard impulse → ack → work → push → cascade.

### Multi-Team Parallel

Multiple teams on different gates work on different repos simultaneously.
Context braids prevent collision:

```
ironGate → cellMembrane (relay evolution)
ironGate → projectNUCLEUS (deploy script evolution)
flockGate → sporePrint (content evolution)
```

Each team weaves braids. eastGate senses all braids via `context.sense --all`.

### Cross-Team Dependency

When Team A's work depends on Team B:

1. Team A fires an impulse to Team B with the dependency
2. Team B acks and delivers
3. Team A cascades the delivery and continues

The impulse system handles the coordination. No manual message passing needed.

---

## 9. Deployment Artifacts

### Binary Distribution

Compiled primal binaries are distributed via `wateringHole/genomeBin/`:

```
genomeBin/primals/<name>/<version>/<name>-<arch>-<os>
```

Gates fetch binaries via:

```bash
membrane plasmid.fetch --primal <name> --source github
```

### Service Units

Systemd service templates are stored with their owning projects:

| Owner | Location | What |
|---|---|---|
| cellMembrane | `deploy/hooks/forgejo/` | Forgejo post-receive hook |
| cellMembrane | `deploy/hooks/cursor/` | Cursor context-sense hook |
| wateringHole | `systemd/cascade-pull.*` | Cascade timer template |
| Each primal | `/etc/systemd/system/<primal>-membrane.service` | VPS service units |

### VPS Deployment

VPS service units live on the VPS nodes directly (not in git). The pattern:

1. Build locally: `cargo build --release --bin <primal>`
2. Copy to VPS: `scp target/release/<primal> golgi:/opt/membrane/`
3. Restart: `ssh golgi "systemctl restart <primal>-membrane"`

Future: `membrane deploy.<primal>` automates this (Wave 67+ target).

---

## 10. Quick Reference

| Task | Command |
|---|---|
| Pull all repos | `membrane temporal.cascade` |
| Check temporal alignment | `membrane temporal.check` |
| See pending impulses | `membrane potential.sense --all` |
| Fire a task | `membrane impulse.post --to <gate> --type frago --subject "..."` |
| Ack a task | `membrane impulse.ack <id>` |
| Archive spent impulses | `membrane impulse.archive` |
| Weave context | `membrane context.weave --project <path> --summary "..."` |
| Sense all context | `membrane context.sense --all` |
| Check ecosystem health | `membrane potential.check` |
| Resolve gate identity | `membrane identity.resolve` |
| List gate repos | `membrane manifest.repos <gate>` |
| Fetch primal binary | `membrane plasmid.fetch --primal <name>` |
| Full relay (K-Derm) | `membrane relay.run` |

---

*This standard enables autonomous team operation across the gate mesh.
Teams receive work via impulses, sense context from other teams, execute
independently, and deliver via the cascade. No manual coordination required.*
