# CI-EVO-01: Harvest Scheduler — Spec + AAR

**Date**: Aug 3, 2026 | **Wave**: 156a | **From**: eastGate overwatch (sporeGate)
**Status**: IMPLEMENTED (code merged, tests passing)
**Resolves**: CI-DIV-06 (no auto-triggers), CI-DIV-07 (no build notifications)

---

## Problem Statement

The build-to-depot pipeline has 6 manual steps. Every push requires an operator to:
1. Notice the push (or remember to check)
2. Run `plasmid.harvest` manually
3. Copy binaries to the NUCLEUS install path
4. Restart NUCLEUS services
5. Push depot to golgi
6. Notify downstream gates

As we scale from 1-2 active gates to 8+, this doesn't work. Teams pushing code
(biomeGate, strandGate, westGate) shouldn't need to coordinate with sporeGate for builds.

---

## Architecture: Two-Layer Harvest Scheduler

### Layer 1: Team-Driven Intentional Builds

A gate team signals build-readiness explicitly:

| Signal Method | How | Effect |
|---------------|-----|--------|
| Commit tag | Include `[harvest]` or `[build]` in commit message | Immediate build via webhook pipeline |
| CLI request | `membrane harvest.request <primal>` | Promotes to `BUILD_REQUESTED`, built on next scheduler tick |

**Use case**: "We just finished a feature sprint on biomeOS, build it now."

### Layer 2: Pipeline-Driven Scheduled Builds

The scheduler autonomously detects and batches work:

| Trigger | Threshold | Action |
|---------|-----------|--------|
| Push without `[harvest]` signal | Queued as `dirty` | Wait for debounce window |
| Debounce elapsed (default 5min) | No new pushes for 5 minutes | Auto-build on next tick |
| Staleness threshold (default 24h) | Primal dirty for 24+ hours | Auto-promote to `BUILD_REQUESTED` |
| Scheduler tick | `harvest.schedule` (cron or timer) | Batch-build all ready primals |

**Use case**: "biomeGate pushed 8 commits over 10 minutes — we debounced and built once."

---

## Data Flow

```
 Forgejo push               sporeGate                     Queue File
 ┌──────────┐   webhook    ┌───────────────────┐         ┌────────────────┐
 │ git push │──────────────→│ webhook.listen    │         │ harvest_queue  │
 │          │   HMAC-SHA256 │ classify_push()   │         │ .toml          │
 └──────────┘               │                   │         │                │
                            │ [harvest] in msg? │         │ [config]       │
                            │   YES → immediate │         │ debounce = 300 │
                            │   NO  → ingest()  │────────→│ staleness=86400│
                            └───────────────────┘         │                │
                                                          │ [primals.X]    │
 Team request                                             │ status = dirty │
 ┌────────────────────┐                                   │ last_push = .. │
 │ harvest.request X  │─────────────────────────────────→│ push_count = 3 │
 └────────────────────┘   promotes to BUILD_REQUESTED     └────────┬───────┘
                                                                   │
 Scheduler tick (cron/timer)                                       │
 ┌────────────────────┐                                            │
 │ harvest.schedule   │←───────────────── evaluate() ──────────────┘
 │                    │
 │ build_now = [X,Y]  │──→ plasmid.harvest --all --local
 │ waiting  = [Z]     │        │
 └────────────────────┘        ↓
                          mark_complete() → remove from queue
                          mark_failed()   → re-queue as dirty
```

---

## Queue File Format

Path: `$XDG_STATE_HOME/membrane/harvest_queue.toml`
(default: `~/.local/state/membrane/harvest_queue.toml`)

```toml
[config]
debounce_secs = 300
staleness_threshold_secs = 86400

[primals.biomeos]
status = "dirty"
first_dirty = "2026-08-03T14:30:00Z"
last_push = "2026-08-03T14:42:00Z"
commit = "abc12345def6"
pusher = "biomegate"
push_count = 4

[primals.beardog]
status = "build_requested"
first_dirty = "2026-08-03T10:00:00Z"
last_push = "2026-08-03T10:00:00Z"
commit = "789abcdef012"
pusher = "strandgate"
push_count = 1
```

### Status Transitions

```
              push arrives        [harvest] signal     team request
                  │                     │                    │
                  ▼                     ▼                    ▼
              ┌───────┐          ┌─────────────┐     ┌─────────────┐
 new push ──→ │ Dirty │          │ IMMEDIATE   │     │ BUILD_      │
              │       │──stale──→│ BUILD       │     │ REQUESTED   │
              │       │ (24h)    │             │     │             │
              └───┬───┘          └──────┬──────┘     └──────┬──────┘
                  │                     │                    │
           debounce elapsed             │                    │
              (5 min)                   │                    │
                  │                     │                    │
                  ▼                     ▼                    ▼
              ┌───────────┐      ┌─────────────┐     ┌─────────────┐
              │ ready to  │──────│  Building   │─────│  Building   │
              │ build     │      │             │     │             │
              └───────────┘      └──────┬──────┘     └──────┬──────┘
                                        │                    │
                                  ok?───┤───fail?            │
                                  │     │     │              │
                                  ▼     │     ▼              │
                              [removed] │  [dirty]           │
                              from queue│  (retry)           │
                                        │                    │
                                        ▼                    ▼
                                   (same lifecycle)
```

---

## CLI Commands

| Command | Description |
|---------|-------------|
| `membrane harvest.ingest <primal> --commit SHA --pusher NAME` | Record a push without building |
| `membrane harvest.request <primal>` | Team signal: build this now |
| `membrane harvest.queue` | Show current queue contents |
| `membrane harvest.schedule` | Evaluate queue and build ready primals |
| `membrane harvest.schedule --dry-run` | Show what would be built |
| `membrane harvest.clear` | Clear the entire queue |

---

## Webhook Integration

The existing `webhook.listen` → `classify_push` → `handle_push` pipeline is modified:

**Before (immediate)**:
```
push → classify → harvest → sandbox → refresh
```

**After (scheduled)**:
```
push → classify → commit has [harvest]?
                    YES → harvest → sandbox → refresh  (immediate)
                    NO  → ingest() → queue             (deferred)
```

The webhook path now checks for `[harvest]` or `[build]` in commit messages.
Teams that want immediate builds include the signal. All other pushes are batched.

---

## Implementation

### Files Modified

| File | Change |
|------|--------|
| `membrane-shadow/src/plasmid/scheduler.rs` | **NEW** — Queue data structures, ingest/request/evaluate/mark lifecycle, TOML I/O, commit signal detection |
| `membrane-shadow/src/plasmid/mod.rs` | Added `pub(crate) mod scheduler;` |
| `membrane-shadow/src/dispatch/mod.rs` | Added `harvest.*` dispatch routing + `dispatch_harvest()` function |
| `membrane-shadow/src/webhook/mod.rs` | Modified `handle_push()` to use scheduler ingest for non-signaled pushes |

### Tests (7/7 passing)

| Test | Validates |
|------|-----------|
| `ingest_creates_dirty_entry` | New primal → dirty status with push_count=1 |
| `request_promotes_to_build_requested` | Dirty → BuildRequested promotion |
| `evaluate_builds_requested` | BuildRequested primals appear in build_now |
| `evaluate_waits_during_debounce` | Recent pushes stay in waiting list |
| `mark_complete_removes_from_queue` | Successful builds clear the queue |
| `iso_epoch_parse` | Timestamp parsing for debounce calculation |
| `harvest_signal_detection` | `[harvest]` and `[build]` signals detected in commits |

---

## Deployment Plan

### Phase 1: CLI-Driven (NOW)

Operators use `harvest.request` and `harvest.schedule` manually:

```bash
# Team pushes code, then signals:
membrane harvest.request biomeos

# Operator runs scheduler tick:
membrane harvest.schedule

# Or: check what would build first:
membrane harvest.schedule --dry-run
```

### Phase 2: Timer-Driven (Next)

Add a systemd timer to run `harvest.schedule` periodically:

```ini
[Unit]
Description=Harvest scheduler tick

[Timer]
OnCalendar=*:0/15
Persistent=true

[Install]
WantedBy=timers.target
```

This gives 15-minute build windows with 5-minute debounce.

### Phase 3: Webhook-Driven (Full automation)

Wire Forgejo's webhook to `webhook.listen` via Caddy reverse proxy:

```
Forgejo push → Caddy /webhook → UDS → membrane webhook.listen
  → [harvest] signal?
    YES → immediate build
    NO  → harvest.ingest → queue
  → timer tick → harvest.schedule → batch build
```

---

## Convergence Status

| Divergence | Status | Resolution |
|------------|--------|------------|
| CI-DIV-06: No auto-trigger | **RESOLVED** | Webhook ingest + scheduler evaluate |
| CI-DIV-07: No build notification | **PARTIAL** | Queue tracks pusher; notification dispatch pending |
| CI-DIV-01: staleness vs status | **INFORMED** | Scheduler uses queue state, not staleness heuristics |
| CI-DIV-03: Depot path confusion | **SEPARATE** | Scheduler builds to harvest depot; install step remains manual for now |

---

## What Worked

- **Commit signal pattern** (`[harvest]` / `[build]`): Zero overhead for teams that
  want immediate builds — just add a tag to the commit message. Natural git workflow.
- **Queue-as-TOML**: Human-readable, debuggable, survives process restarts.
  Operators can inspect and hand-edit `harvest_queue.toml` if needed.
- **Debounce + staleness dual threshold**: Prevents build storms during active
  development while ensuring nothing stays stale for more than 24h.
- **Existing webhook infrastructure**: `classify_push`, HMAC verification, provider
  abstraction (Forgejo/GitHub) already solid — scheduler just inserts between
  classification and execution.

## What Needs Evolution

- **Post-build notification**: After `harvest.schedule` completes, notify the pushing
  gate via Forgejo issue comment or webhook callback.
- **Selective primal build**: `harvest.schedule` currently calls `harvest --all`;
  should build only the dirty primals in the queue.
- **Cross-target awareness**: Queue should track which targets need building
  (musl, gnu, windows-gnu) and dispatch to appropriate sub-builders (J12).
- **Install automation**: After harvest, auto-copy to NUCLEUS install path and
  restart services (CI-DIV-03 convergence).
- **Depot push integration**: After successful harvest + install, auto-push to
  golgi depot and regenerate checksums.
