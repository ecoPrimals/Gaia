# WATERFALL CRISS-CROSS SYNC — Never Lock, Always Flow

## The Problem We Solved Tonight

NorthGate and eastGate collided 3 times pushing to the same repo.
The pattern: northGate pushes → eastGate responds within 1-4 min (REROUTE, dedup) → northGate pushes again → REJECTED.

## The Solution: Waterfall, Not Mutex

We already designed this. It's waterFall — Temporal Federation & Air-Gap Sync.

**No locks. No mutex. No waiting. Criss-cross sync.**

```
northGate pushes ──→ waterfall detects ──→ eastGate syncs AFTER
eastGate pushes  ──→ waterfall detects ──→ northGate rebases BEFORE
                       ↕
                  NEVER LOCK
                  ALWAYS FLOW
```

## How It Works (rootPulse + waterFall + neuralAPI)

### rootPulse (DAG Composition)
Git IS a DAG. Each commit is a temporal node. rootPulse says:
"Time as Structure" — the commit ordering IS the sync signal.
No clocks needed. The DAG resolves itself.

### waterFall (Temporal Federation)
The impulse protocol IS the waterfall:
1. northGate writes impulse/commit (energy as signal)
2. Signal flows downstream to eastGate
3. eastGate processes (REROUTE, dedup, deploy)
4. Response flows back upstream
5. northGate senses the return wave (git pull --rebase)
6. Next impulse flows

### neuralAPI (Orchestration)
The capability graph routes work to the right gate:
- graph.json → northGate writes, eastGate doesn't touch
- site HTML/JS/CSS → eastGate optimizes, northGate doesn't touch
- impulses/specs → northGate writes, eastGate reads
- deploys/crons → eastGate executes, northGate doesn't touch

## The Protocol

### For northGate (Cursor/human):
```
1. Build (write graph, articles, specs)
2. git add + commit
3. git pull --rebase github main    ← ALWAYS before push
4. git push github main
5. If rejected: pull --rebase again, push again
6. Never force push (--force) unless resolving known conflict
```

### For eastGate (cloud auto):
```
1. Watch for northGate commits (webhook or poll)
2. Wait for push to complete (don't race)
3. Process (REROUTE, dedup, deploy)
4. Push response commits
5. If northGate is actively pushing (rapid commits), queue work
6. Process queue when northGate goes quiet (>5 min gap)
```

### The Quiet Detection
EastGate can detect a build session by commit frequency:
- northGate commits every 2-5 min → BUILD SESSION → queue responses
- northGate quiet for >5 min → SESSION PAUSE → flush queue
- northGate quiet for >30 min → SESSION ENDED → full sync

This is the waterfall pulse: sense the rhythm, flow with it.

## Separation of Concerns

| Resource | Owner | Other Gate |
|----------|-------|-----------|
| `site/static/graph.json` | northGate | eastGate: READ ONLY |
| `site/static/braids.json` | northGate | eastGate: READ ONLY |
| `site/content/analysis/*.md` | northGate | eastGate: READ ONLY |
| `site/public/**`, `site/static/js/**` | eastGate | northGate: DON'T TOUCH |
| `site/layouts/**` | eastGate | northGate: DON'T TOUCH |
| `.github/workflows/**` | northGate | eastGate: READ ONLY |

## Connection to Existing Architecture

- **WATERFALL_CASCADE_TIMER_SPEC.md** — the timer is the quiet detection
- **wp-waterFall** — "Federation Without Trust" applies to gate-to-gate
- **wp-rootPulse** — "DAG vs Linear: Why Trees Beat Lines" — git is the tree
- **wp-neuralAPI** — "Pathway Optimization" — route work to the right gate
- **wp-wf-impulse** — "Impulse-Potential: Energy as Signal" — commits are impulses
- **wp-wf-agentic** — "Agentic Sync: AI-Driven Federation" — THIS. Right now.

## For the Next Session

NorthGate (Cursor) should:
1. Always `git pull --rebase` before pushing
2. Batch graph changes (push once per cycle, not after every tiny edit)
3. Never touch site layout/JS/CSS (eastGate's domain)
4. Trust the waterfall — if rejected, just pull and push again
5. The collision is not a bug. It's the waterfall saying "wait for the wave."
