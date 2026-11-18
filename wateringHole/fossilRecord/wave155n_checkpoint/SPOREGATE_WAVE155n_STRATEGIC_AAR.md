# sporeGate Wave 155n Strategic AAR — What Worked, What Didn't, What Evolves

**Date**: Jul 31, 2026 08:15 EDT | **Gate**: sporeGate | **Wave**: 155n
**Gate Health**: 11/11 → 8/11 DEGRADED (socket evaporation live during AAR)

---

## WHAT WORKED

### 1. Sovereign CI Pipeline — End-to-End Automated

The pipeline went from "3 bugs preventing any automated builds" to "fully automated
push-to-deploy for non-broker primals" in a single session:

```
Forgejo push → golgi post-receive → dispatcher → 30-sovereign-ci hook
  → SSH root@sporeGate → membrane sovereign.ci.trigger
  → cargo build --release --target musl → sandbox::validate → depot push → golgi rsync
```

**Verified**: squirrel 4bcf79ed — build (2m09s) → sandbox PASS → depot push → golgi sync.
Zero human intervention. This is the first time the full J9→J10→J11 chain executed
autonomously from a real push event.

### 2. P2 Golgi Hook — Root Cause Found and Fixed

Three independent bugs, none obvious alone:

| Bug | Root Cause | Fix |
|-----|-----------|-----|
| No dispatcher | Git only runs `hooks/post-receive`, not `post-receive.d/` | Created dispatcher script in all 20 repos |
| Case mismatch | Bare repo `biomeos.git` → `biomeos`, manifest `[repos.biomeOS]` | Case-insensitive grep (`-i`) |
| Category mismatch | Manifest: `"primal"` singular, hook: `"primals"` plural | Pattern matches both forms |

**Key insight**: These bugs existed since the hook was first installed but were never
caught because no test push ever exercised the full path from golgi→sporeGate.

### 3. Multi-Primal Rebuild — 4 Primals, 3 Targets, All Clean

| Primal | Commit | musl | gnu | windows |
|--------|--------|------|-----|---------|
| biomeOS | 999044e7 | 3m15s | 3m17s | 4m18s |
| cellMembrane | 301e236 | 1m11s | — | 1m05s |
| petalTongue | b135400 | 2m41s | — | 1m40s |
| squirrel | 4bcf79ed | 2m09s | — | 1m39s |

Depot: 35 binaries, all BLAKE3 verified, golgi synced.

### 4. Gate Identity Consolidation — 3→1

cellMembrane 301e236 shipped `resolve_gate_name_async()`:
```
CLI arg → GATE_NAME env → .gate file → multi-root identity
```
Replaces 3 divergent implementations with one shared function. sporeGate now correctly
identified as "sporeGate" (was "unknown" in some code paths with old membrane).

### 5. Cascade Discipline — 4 Repos, Clean Pulls

biomeOS (4 commits), cellMembrane (4 commits), petalTongue (2 commits), squirrel
(3 commits), wateringHole (5 commits). All pulled, reviewed, built, deployed.
bearDog, songBird, toadStool correctly at STANDBY — no changes.

---

## WHAT DIDN'T WORK

### 1. biomeOS Self-Sovereignty — The Orchestrator Can't Self-Validate

**The core problem**: biomeOS is a composition broker. It discovers primals, routes
capabilities, manages lifecycle. When sovereign CI tries to sandbox-validate a freshly
built biomeOS binary, it fails because:

```
sandbox launches biomeOS standalone
  → biomeOS finds no primals (they aren't running in the sandbox)
  → empty capability registry
  → health probe asks "are you healthy?"
  → biomeOS has nothing to orchestrate
  → no response after 5 attempts (8s timeout)
  → sandbox: FAILED → deploy blocked
```

This means biomeOS can NEVER pass sovereign CI's sandbox test. Every biomeOS update
requires manual deploy. The pipeline automation (J9-J11 KILLED) is incomplete for the
single most important binary.

**Impact**: 1/16 musl primals requires manual intervention. For all others the pipeline
is fully automated.

### 2. Socket Evaporation — Live During This Session

We watched /run/membrane go from 13 sockets to EMPTY in real time:

```
08:02 — 13 sockets in /run/membrane, gate.status 11/11 HEALTHY
08:14 — biomeOS resets dir permissions to 0770 root:membrane
08:15 — ls /run/membrane: Permission denied (sporegate not root)
08:15 — ss -lxn shows 13 sockets STILL ALIVE in kernel (FDs open)
         but directory entries are invisible to non-root users
```

biomeOS actively manages `/run/membrane` permissions. When it detects a connection
(every 30s REJECTED log), it resets directory ownership. The sockets are alive in the
kernel but the directory listing is restricted.

**Root cause chain**:
1. biomeOS binds sockets with `0660 root:membrane` (per v4.50 fix)
2. It also resets the parent directory to `0770 root:membrane`
3. `sporegate` user is in the `membrane` group → CAN access `0770`
4. But `gate.status` probes check via `neural-api-default.sock` symlink
5. If the symlink or socket gets recreated after the permission fix → 0660 again
6. gate.status as sporegate user → "Permission denied" on neural-api socket

**Key observation**: The 13 sockets are ALIVE. The primals are RUNNING. The issue is
purely directory/socket permission semantics between biomeOS (root) and membrane
(sporegate user).

### 3. GATE_NAME vs MEMBRANE_GATE_NAME

cellMembrane 301e236 expects `GATE_NAME`. We have both `GATE_NAME=sporeGate` and
`MEMBRANE_GATE_NAME=sporeGate` in `/etc/environment`. But older code paths still look
for `MEMBRANE_GATE_NAME`. The consolidation is 90% done but the env var name is not
yet unified.

### 4. `/run/membrane` Permission Reset Is Recurring

Every time biomeOS restarts or processes a connection, it resets `/run/membrane`
permissions. Our `tmpfiles.d` rule sets correct permissions at boot, but biomeOS
overwrites them at runtime. The fix needs to be in biomeOS itself.

---

## WHAT NEEDS TO EVOLVE — THE biomeOS ORCHESTRATION OPPORTUNITY

### The Strategic Insight

biomeOS can't self-validate because it's an orchestrator without anything to orchestrate
in isolation. But this limitation points to a bigger architectural opportunity:

**biomeOS should own the primal lifecycle, not just the capability registry.**

Right now the architecture looks like:

```
Current:
  cellMembrane → manages deployments, builds, depot
  systemd → starts/stops primals
  biomeOS → passive observer, discovers running primals, routes capabilities
  membrane gate.status → probes everything independently
```

The convergence point:

```
Evolved:
  cellMembrane → deployment authority (build, push, depot)
  biomeOS → composition authority (start, stop, health, lifecycle)
  membrane → plumbing layer between the two
```

### Evolution 1: biomeOS Composition Authority

biomeOS already has `composition.start` and boot_order discipline. The next step:

1. **biomeOS manages `/run/membrane`** — biomeOS creates the directory, sets
   permissions, owns the socket namespace. No more fighting with tmpfiles.d.
2. **biomeOS starts primals** — instead of systemd units, biomeOS uses its
   composition graph to start primals in boot_order. It already knows the dependency
   graph (Tower → Nest → Node → Viz → Orch).
3. **biomeOS health-checks itself** — the sandbox test becomes: "can biomeOS
   boot a minimal composition?" Not "can biomeOS respond to health probes in isolation?"

### Evolution 2: Sovereign CI Talks to biomeOS

Instead of `sovereign.ci.trigger` doing a standalone sandbox test:

```
Current:
  trigger → build → start binary in sandbox → health probe → fail for biomeOS

Evolved:
  trigger → build → ask running biomeOS to hot-swap the binary
  biomeOS → stops old process → starts new binary → verifies composition intact
  biomeOS → reports health to trigger → trigger pushes to depot
```

This is the "biomeOS self-takeover" pattern: the running biomeOS orchestrates its own
replacement. cellMembrane's `sovereign.ci.trigger` becomes the build authority, and
biomeOS becomes the deploy authority for its own composition.

### Evolution 3: cellMembrane ↔ biomeOS Contract

The boundary:

| Concern | Owner | Interface |
|---------|-------|-----------|
| Build binary | cellMembrane (sovereign CI) | `membrane sovereign.ci.trigger` |
| Deploy to depot | cellMembrane | `membrane plasmid.refresh` |
| Start/stop primal | biomeOS | `biomeos composition.{start,stop,swap}` |
| Health validation | biomeOS | `biomeos composition.health` |
| Socket namespace | biomeOS | `/run/membrane/` ownership |
| Gate identity | cellMembrane | `GATE_NAME` env → `.gate` file |
| Binary discovery | biomeOS | 5-tier search (already shipped in 999044e7) |
| Platform abstraction | cellMembrane | `resolve_socket_base()`, `InitSystem` |

The `ServerContract` type already exists in cellMembrane. It needs to be the formal
interface: cellMembrane builds, biomeOS deploys+validates.

### Evolution 4: Sandbox Becomes Composition Test

Instead of the current sandbox (standalone binary → health probe):

```rust
// cellMembrane sovereign.ci.trigger
fn validate_broker_primal(primal: &str, binary: &Path) -> Result<()> {
    // Ask the RUNNING biomeOS to test the new binary
    let response = neural_api_request("composition.test_swap", json!({
        "primal": primal,
        "binary_path": binary,
        "rollback_on_failure": true,
    }))?;
    // biomeOS stops the old, starts the new, verifies health, reports back
    Ok(response.health_ok)
}
```

This eliminates the false positive AND makes the test MORE rigorous — it validates
the binary in the actual composition context, not in isolation.

### Evolution 5: Socket Ownership Resolution

The permission fight between biomeOS and the sporegate user is a symptom of unclear
ownership. With biomeOS as composition authority:

1. biomeOS owns `/run/membrane/` — creates it with `0755`, manages all sockets
2. biomeOS creates sockets with `0666` (any user can connect)
3. The `membrane` group becomes irrelevant — socket access is open
4. OR: biomeOS creates sockets with `0660 root:membrane`, and `gate.status`
   talks to biomeOS via neural-api (which biomeOS makes accessible)

Either path resolves the recurring permission issue.

---

## REMAINING P3 ITEMS

| # | Issue | Owner | Sequencing |
|---|-------|-------|------------|
| P3-1 | cellMembrane not in sources.toml | cellMembrane | Blocks self-CI rebuild |
| P3-2 | GATE_NAME env var unification | cellMembrane | Cosmetic but should be unified |
| P3-3 | /run/membrane permission reset | biomeOS | Part of Evolution 5 |
| P3-4 | Sandbox false positive for brokers | cellMembrane + biomeOS | Part of Evolution 4 |
| P3-5 | vcs.parity "0 repos checked" | cellMembrane | Configure repo list |
| P3-6 | GNU depot incomplete (4/16) | sporeGate | Batch build when needed |

---

## BY THE NUMBERS

| Metric | Before (start of session) | After |
|--------|--------------------------|-------|
| Golgi hook | BROKEN (3 bugs, never fired) | FIXED (E2E verified) |
| Sovereign CI E2E | Untested from real push | Verified (squirrel full pipeline) |
| biomeOS | 0e45262 (v4.51) | 999044e7 (5-tier discovery) |
| cellMembrane | 0cfcce5 | 301e236 (gate identity 3→1) |
| petalTongue | 71c95c7 | b135400 (modern idiom pass) |
| squirrel | acbe09e | 4bcf79ed (7,138 tests, 0 clippy) |
| Depot | 35 binaries (stale) | 35 binaries (ALL current, BLAKE3) |
| Gate health | 11/11 (with manual perm fix) | 8/11 → 11/11 → 8/11 (perm drift) |
| Hook bugs fixed | 0 | 3 |
| P2s open | 1 (golgi hook) | 0 |
| P3s identified | 4 | 6 (better visibility) |

---

## RECOMMENDATION

The biomeOS self-takeover pattern is the strategic evolution that resolves 3 of the 6
P3s simultaneously (sandbox false positive, /run/membrane permissions, socket
evaporation). It also unlocks:

- **Fully automated CI for ALL primals** including biomeOS itself
- **Clean socket lifecycle** — no more permission fights
- **Hot-swap deployments** — zero-downtime primal updates
- **Composition-aware health** — test in context, not in isolation

This is a cellMembrane + biomeOS joint evolution. The `ServerContract` type and
`composition.start` already exist. The gap is `composition.test_swap` (biomeOS) and
`sovereign.ci.trigger` delegation to neural-api (cellMembrane).

**Blurb for cellMembrane team**: biomeOS sandbox validation still fails for broker
primals (false positive). Proposed fix: instead of standalone sandbox test, have
`sovereign.ci.trigger` delegate validation to the running biomeOS via neural-api
(`composition.test_swap`). biomeOS hot-swaps the binary, validates composition health,
reports back. This also resolves the /run/membrane permission issues by making biomeOS
the socket namespace authority. See `SPOREGATE_WAVE155n_P2_HOOK_FIX_AAR.md` for the
full socket evaporation trace.
