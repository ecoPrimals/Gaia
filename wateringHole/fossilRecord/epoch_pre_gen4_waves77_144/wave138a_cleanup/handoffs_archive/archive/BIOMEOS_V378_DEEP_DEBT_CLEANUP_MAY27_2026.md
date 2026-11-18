# biomeOS v3.78 — Deep Debt Cleanup Handoff

**Date**: May 27, 2026
**Commit**: `2599042f`
**Previous**: v3.77 (NUCLEUS spore gateway)

---

## Summary

Comprehensive deep debt audit and cleanup of the biomeOS workspace. All changes
are backward-compatible — no API contract changes, no new crate dependencies.

## Changes

### 1. Hardcoded Primal Names → `primal_names::` Constants

**Files**: `capability_translation/socket.rs`, `neural_router/composition.rs`

| Before | After |
|--------|-------|
| `("compute", "toadstool")` | `("compute", TOADSTOOL)` |
| `Arc::from("beardog")` | `Arc::from(BEARDOG)` |
| `"nestgate" \| "rhizocrypt"` match | `NESTGATE \| RHIZOCRYPT` match |

- `DOMAIN_PRIMAL_BOOTSTRAP` table (5 entries) in `socket.rs` — all literals
  replaced with `primal_names::` constants.
- `dual_socket_primals()` — `"toadstool"` → `TOADSTOOL`.
- `CompositionTier::from_provider()` — all 10 primal names replaced.
- `CompositionPatternRegistry::with_canonical_patterns()` — all 7 patterns'
  primal lists (26 instances total) replaced with constants.
- Removed primal-name domain aliases (`"toadstool"`, `"squirrel"`) from
  `classify()` — the `from_provider()` fallthrough handles them correctly.

### 2. Large File Refactoring

| File | Before | After | Technique |
|------|--------|-------|-----------|
| `method_gate/mod.rs` | 961 lines | 328 lines | 59 tests → `tests.rs` |
| `constants/mod.rs` | 852 lines | 540 lines | 35 tests → `tests.rs` |

Both files used `#[cfg(test)] #[path = "tests.rs"] mod tests;` pattern — zero
change to test behavior, names, or module paths.

### 3. Live Discovery REST Routes

**File**: `biomeos-api/src/handlers/live_discovery.rs`, `lib.rs`

Wired the fully-implemented but previously unused `live_discovery` module into
the REST API with three new endpoints:

| Endpoint | Handler | Description |
|----------|---------|-------------|
| `GET /api/v1/discovery/primals` | `get_live_primals` | Scan all sockets, return reachable primals |
| `GET /api/v1/discovery/capability/:domain` | `get_primals_by_capability` | Filter by capability domain (e.g. `crypto`) |
| `GET /api/v1/discovery/type/:primal_type` | `get_primals_by_type` | Filter by primary type (e.g. `security`) |

Removed:
- Module-level `#![expect(dead_code)]`
- `// TODO(REST-routes)` comment

### 4. Deferred Items (Documented, Not Debt)

- `SporeInstantiate` in `routing.rs`: scaffold correctly forwards to graph
  executor with `_deferred` flag. Blocked on lithoSpore Tier 3 upstream.
- Multicast I/O in `discovery_bootstrap.rs`: deferred until cross-gate
  deployments require it.
- HTTP bridge "temporary" comments: PetalTongue transition still in progress.

## Audit Results (Full Workspace)

| Category | Status |
|----------|--------|
| Unsafe code | **CLEAN** — zero blocks, `#[forbid(unsafe_code)]` on all crate roots |
| Hardcoded primal names | **RESOLVED** — 2 hotspots cleaned |
| Mocks in production | **CLEAN** — all behind `#[cfg(test)]` |
| TODO/FIXME/HACK | **0 actionable** — remaining are upstream-blocked |
| `.unwrap()` in production | **CLEAN** — workspace `deny(unwrap_used)` enforced |
| Dead code | **RESOLVED** — `live_discovery.rs` wired |
| C dependencies | **CLEAN** — 0 banned crates in lockfile |
| Files >800L (production) | **2 remaining** — `routing.rs` (910), `nucleus.rs` (883) |

## Documentation Cleanup (second pass)

Root docs synced to v3.78:
- All version stamps, TODO counts (1→0), signal graph counts (17→18),
  test counts (7,859→8,036), and stale footers refreshed across 20 files.
- `wateringHole` path normalized to `ecoPrimals/infra/wateringHole/` (5 files).
- Stale systemd configs deleted (personal paths, missing scripts).
- Broken `pull-primals.sh` references → `tools/harvest` (4 files).

## Test Results

- All **8,036 tests** pass (0 failures)
- All extracted tests verified with `cargo test`
- Full workspace `cargo clippy` — **0 warnings**
