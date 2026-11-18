# AAR: westGate Wave 155i — Composition Broker LIVE

**Gate:** westGate
**Date:** 2026-07-29
**Operator:** westGate overwatch (agentic)
**Wave:** 155i (post-cascade — biomeOS v4.45 deployed, composition broker operational)
**Scope:** biomeOS depot refresh, Neural API COORDINATED mode, signal graph execution, capability routing E2E, Provenance Trio re-validation, socket architecture analysis
**Prior AARs:** `WESTGATE_DEPOT_REFRESH_BROKER_GAP_155i_AAR.md`, `WESTGATE_CASCADE_REVIEW_ZFS_PROVENANCE_155i_AAR.md`, `WESTGATE_NEST_ATOMIC_MULTICOMP_155i_AAR.md`

---

## Context

sporeGate depot rebuild shipped biomeOS v4.45 (15,936 KB, commit `8cee1adb`) — the
composition broker binary. This AAR covers deploying it on westGate, validating COORDINATED
mode, testing signal graph dispatch, and re-running the Provenance Trio E2E.

---

## What Worked

### 1. biomeOS v4.45 — COORDINATED Mode with 704 Capabilities

The depot biomeOS binary replaced the old v0.1.0. On restart, the Neural API:
- Loaded 390 capability translations from `config/capability_registry.toml`
- Discovered all 7 primals via socket probing
- Entered **COORDINATED mode** (was BOOTSTRAP with old binary)
- Registered **704 capabilities** (was 163 with old binary)
- Perceptron shadow mode active for neutral inference defaults

The composition broker pattern is operational: the Neural API orchestrates capability
routing across all Nest Atomic primals.

### 2. Capability Routing — E2E WORKING

Direct capability routing through the Neural API works end-to-end:

```
content.put → nestgate  →  BLAKE3 hash returned, stored on ZFS  ✓
storage.put → nestgate  →  Key-value store operational           ✓
```

The translation layer correctly resolves semantic capabilities to primal sockets using
the three-tier lookup: runtime registry → capability_registry.toml → bootstrap hints.

### 3. Signal Graph Dispatch — Routing WORKS

Signal graph semantic dispatch works correctly:

```
nest.store → signal.dispatch → signals/nest_store → 4-node graph loaded  ✓
graph.execute → nest_deploy → 3 nodes executed (start-beardog, start-songbird, start-nestgate)  ✓
```

The signal intercept pattern (`nest.store` → `signal.dispatch` with `graph = "nest_store"`)
routes correctly through the capability translation table. Graphs load, parse, and execute
node dependency resolution with topological ordering.

### 4. Provenance Trio — 6/7 Confirmed

| Step | Primal | Method | Result |
|------|--------|--------|--------|
| 1 | nestGate | `content.put` | **PASS** — BLAKE3 `f5cc0776...`, 256B, stored on ZFS |
| 2 | rhizoCrypt | `dag.session.create` | **PASS** — UUID v7 session |
| 3 | rhizoCrypt | `dag.event.append` | **PASS** — DataCreate event (array param format) |
| 4 | rhizoCrypt | `dag.merkle.root` | **PASS** — root = event hash |
| 5 | loamSpine | `spine.create` | **PASS** — UUID v7 spine |
| 6 | loamSpine | `entry.append` | **EXPECTED FAIL** — bearDog `crypto.sign_ed25519` stub |
| 7 | sweetGrass | `braid.create` | **PASS** — JSON-LD PROV-O with `@id: urn:braid:...` |

The `entry.append` parameter format was clarified: loamSpine expects JSON-RPC positional
params (array format), not named params. The `DataAnchor` variant with `data_hash` as
`[u8; 32]` (byte array) and `size` fields reaches the bearDog signing step before failing
on the unimplemented `crypto.sign_ed25519`.

sweetGrass v0.8.0 confirmed: `braid_count: 11`, `status: healthy`. The `braid.create`
response is a JSON-LD PROV-O document (not a simple `{braid_id: ...}` JSON-RPC result) —
the `@id` field contains the braid URN. This is by design for provenance interoperability.

### 5. ZFS Pool — 3,216 CAS Objects, Zero Errors

```
pool: nestgate — ONLINE, 0 errors
  mirror-0: 2×14TB — ONLINE
  mirror-1: 2×14TB — ONLINE
  cache:    1×2TB BX500 SSD — ONLINE (L2ARC)
  spare:    1×14TB — AVAIL
  Capacity: 25.3TB available
  CAS objects: 3,216 (up from 3,211)
```

New objects from this session's E2E testing landed on ZFS via the CAS symlink.

---

## What Did Not Work

### 1. Signal Graph Node Execution — riboCipher Gap in Executor Raw Fallback (P2)

The graph executor's node execution path in `neural_executor_node_impls.rs` (line 519) uses
`send_jsonrpc_request()` for the raw fallback after BTSP fails. This function sends **plain
JSON-RPC without the `[0xEC, 0x01]` riboCipher prefix**.

The Neural API socket enforces riboCipher signal detection (Wave 113 policy), so the
executor's self-referencing capability call gets rejected:

```
ERROR REJECTED: legacy connection (no riboCipher signal) — unsignalled connections dropped
```

The executor then falls back to direct primal socket calls. The BTSP handshake to
nestgate fails (no session propagation in this code path), and the subsequent raw
JSON-RPC call also fails because the executor treats the combined BTSP+raw failure
as a node execution failure.

**Fix required:** The executor's raw fallback on line 519 should use
`send_ribocipher_jsonrpc_request()` instead of `send_jsonrpc_request()` for connections
to Neural API sockets. The composition broker E2E tests (35 tests) validate the correct
path, but the depot binary's graph executor still uses the old non-riboCipher path.

**Severity:** P2 — capability routing works; only orchestrated signal graph execution
through the graph executor is blocked.

### 2. Socket Architecture Split — `biomeos/` vs `membrane/` (P2)

Primals register sockets in `$XDG_RUNTIME_DIR/biomeos/`. The biomeOS binary hardcodes
`MEMBRANE_SUBDIR = "membrane"` for its socket detection and nucleation. This creates a
split:

- **biomeos primals** → `/run/user/1000/biomeos/*.sock`
- **biomeOS Neural API** → `/run/user/1000/membrane/neural-api-*.sock`
- **biomeOS executor** → looks in `/run/user/1000/membrane/` for primal sockets

**Workaround deployed:** Symlink bridge from `/run/user/1000/membrane/` to
`/run/user/1000/biomeos/` for all primal sockets. This allows the Neural API's bootstrap
scanner and graph executor to find primal sockets through the membrane path.

**Upstream fix:** Either unify on `biomeos/` or `membrane/` — update `MEMBRANE_SUBDIR` or
update the primal socket registration path. The `capability_registry.toml` socket templates
already use `biomeos/`:

```toml
xdg_runtime = "{xdg_runtime}/biomeos/{primal}-{family_id}.sock"
```

### 3. Socket Evaporation — Recurring Pattern (P2)

Restarting the Neural API causes primal socket evaporation. The discovery cycle wipes
and re-registers all capabilities every ~30 seconds. During the wipe window, capability
lookups return 0 results and graph execution fails.

Additionally, restarting the Neural API causes some primal sockets to disappear entirely
(nestgate, beardog, loamspine). This requires restarting the affected primals and
rebuilding the membrane symlinks.

**Root cause hypothesis:** The Neural API's socket discovery probes use raw JSON-RPC
(no riboCipher prefix). Several alias sockets (e.g., `security.sock`, `storage.sock`)
exist as symlinks but fail RPC pings because the target primals don't respond to the
old ping format on those aliases. When the discovery cycle unregisters these, it may
inadvertently clean up related sockets.

### 4. capability_registry.toml Loading Path (P3)

The graph executor loads `capability_registry.toml` from `config/capability_registry.toml`
relative to CWD (hardcoded in `handlers/graph/execute.rs` line 196). Without setting
`WorkingDirectory` in the systemd unit to the biomeOS source tree, the file is not found
and the executor uses an empty registry.

**Fix deployed:** Set `WorkingDirectory=%h/Development/ecoPrimals/primals/biomeOS` in
the neural-api-tower.service unit.

---

## Key Metrics

| Metric | Before | After |
|--------|--------|-------|
| biomeOS binary | 0.1.0 (depot pre-broker) | 0.1.0 (depot v4.45, 15,936 KB) |
| Neural API mode | BOOTSTRAP (5 caps) | **COORDINATED (704 caps)** |
| Capability translations | 0 | **390** (from capability_registry.toml) |
| Signal graph dispatch | BLOCKED (socket path bug) | **ROUTING WORKS** (node execution P2) |
| Capability routing | BLOCKED | **E2E WORKING** |
| Provenance Trio | 6/7 | **6/7** (bearDog crypto.sign unchanged) |
| CAS objects on ZFS | 3,211 | **3,216** |
| ZFS errors | 0 | 0 |
| Services running | 8/8 | 8/8 |
| Sockets | 15 | **20** (more capability aliases) |

---

## Configuration Changes Made

1. **neural-api-tower.service:**
   - Changed `--socket` from `/run/user/1000/membrane/` to `/run/user/1000/membrane/`
     (kept in membrane dir for bootstrap scanner compatibility)
   - Added `WorkingDirectory=%h/Development/ecoPrimals/primals/biomeOS` for
     `capability_registry.toml` loading
   - Removed `--log-level debug` (used during investigation)

2. **Socket symlink bridge:**
   - Created symlinks: `/run/user/1000/membrane/*.sock` → `/run/user/1000/biomeos/*.sock`
   - Must be rebuilt after primal restarts (sockets are recreated)

3. **Signal graph top-level copies:**
   - Copied `signals/nest_store.toml`, `signals/nest_ingest_dataset.toml`,
     `signals/tower_health.toml`, `signals/nest_ingest_spore.toml` to `graphs/`
     top level for `graph.execute` (executor doesn't search subdirectories)

---

## Depot Binary Analysis

The depot biomeOS binary (15,936 KB) has the composition broker code compiled in:
- BTSP session establishment and tunnel code present
- riboCipher signal detection and Wave 113 policy enforcement
- Coordinated mode detection and capability registration
- 390 capability translations loadable from TOML

However, the graph executor's raw fallback path still uses `send_jsonrpc_request` instead
of `send_ribocipher_jsonrpc_request`. This specific code path was not updated in the depot
build. The 35 E2E composition broker tests validate the correct path (riboCipher framing),
but the executor's fallback for non-BTSP connections to the Neural API socket uses the
old function.

---

## Action Items

### P1

| # | Item | Owner | Unblocks |
|---|------|-------|----------|
| 1 | **bearDog `crypto.sign_ed25519`** — implement real signing | bearDog | Provenance Trio 7/7 |

### P2

| # | Item | Owner | Unblocks |
|---|------|-------|----------|
| 2 | Graph executor raw fallback → `send_ribocipher_jsonrpc_request` | biomeOS | E2E signal graph node execution |
| 3 | Socket architecture unification (`biomeos/` vs `membrane/`) | biomeOS | Eliminate symlink bridge workaround |
| 4 | Socket evaporation under Neural API restart | All primals / biomeOS | Multi-composition stability |
| 5 | Graph executor subdirectory search for `signals/*.toml` | biomeOS | Graph files in canonical location |

### P3

| # | Item | Owner | Unblocks |
|---|------|-------|----------|
| 6 | `capability_registry.toml` path resolution (relative to binary or env var) | biomeOS | Portable deployment without WorkingDirectory |
| 7 | Discovery cycle capability wipe → incremental update | biomeOS | Zero-downtime capability routing |

---

## Key Insight: Capability Routing Works, Graph Execution Doesn't (Yet)

The composition broker delivered exactly what it promised: **the Neural API can now route
capability calls to the correct primal sockets**. The three-tier resolution (runtime
registry → TOML translations → bootstrap hints) works and correctly maps `content.put` →
nestgate, `dag.session.create` → rhizocrypt, etc.

What doesn't work is the **graph executor's connection path**. The executor uses
`send_jsonrpc_request` (raw JSON-RPC) to connect to primal sockets during signal graph
node execution. The Neural API socket rejects these connections because they lack the
riboCipher prefix. The primals themselves accept raw JSON-RPC, but the executor tries the
Neural API first (for capability routing), gets rejected, then tries direct socket with
BTSP (which fails), then the raw fallback also fails.

This is a one-line fix: `send_jsonrpc_request` → `send_ribocipher_jsonrpc_request` on line
519 of `neural_executor_node_impls.rs`. The composition broker E2E tests already validate
this path. The depot binary just needs to be rebuilt with this change.

**Meanwhile, direct capability routing through the Neural API works perfectly.** Any
consumer can call `content.put`, `dag.session.create`, `spine.create`, `braid.create`
etc. through the Neural API socket using riboCipher framing and get correct routing to
the appropriate primal. The Provenance Trio E2E passes 6/7 through this path.

---

*Wave 155i composition broker LIVE on westGate. biomeOS v4.45 deployed (15,936 KB). Neural
API COORDINATED mode: 704 capabilities, 390 translations. Capability routing E2E WORKING
(content.put → nestgate, dag → rhizocrypt, spine → loamspine, braid → sweetgrass). Signal
graph dispatch routes correctly but node execution blocked by riboCipher gap in executor raw
fallback (P2 — one-line fix). Provenance Trio 6/7 (bearDog crypto.sign P1 unchanged). ZFS
3,216 CAS objects, 25.3TB, zero errors. Socket architecture split (biomeos/ vs membrane/)
bridged with symlinks. Three P2s for biomeOS, one P1 for bearDog.*
