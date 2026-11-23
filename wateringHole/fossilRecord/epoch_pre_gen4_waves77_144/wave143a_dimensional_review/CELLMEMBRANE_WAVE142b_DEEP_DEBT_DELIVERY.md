# cellMembrane Wave 142b Deep Debt Delivery

**Date**: Jul 16, 2026 | **Wave**: 142b | **From**: eastGate cellMembrane team
**Commits**: `fb6c75c` (CAC + Caddy) + `287780d` (deep debt sweep)
**Tests**: 1,072 pass | **Clippy**: 0 warnings | **Files changed**: 40+

---

## Delivered

### CAC P1 — Tree-Parity Before Cascade Policy

Both CAC P1 items resolved:

- **`sync_diverge` pre-check**: Before firing diverge impulses or applying
  divergence policy, the engine now checks if local `HEAD^{tree}` matches
  any remote's tree. Identical trees (Newton-Leibniz) auto-resolve via
  reset, bypassing agentic/flag paths entirely.
- **`try_pull_converge` fallback**: After rebase conflict, checks
  `trees_match()`. If local and remote trees are identical despite
  divergent history, resets to remote instead of failing.

This directly fixes the wateringHole heads auto-publish false divergences.

### Caddy Blocks for footPrint + tideGlass (P2)

- `FOOTPRINT_DOMAIN`, `TIDEGLASS_DOMAIN`, `DEFAULT_FOOTPRINT_PORT`
  constants added to `cellmembrane-types`.
- `caddy.generate` resolves `footprint` and `tideglass` gate roles from
  manifest. Refactored role→vhost into data-driven loop (-55 lines).
- Gateway route generator produces footPrint (drawbridge `/`, agent
  bridge `/ws`, CAS `/api`) and tideGlass (`/`) routes from gate roles.

### Visibility Tightening

- 20 modules in `lib.rs` changed `pub` → `pub(crate)`. Only the
  documented API surface remains public (`config`, `error`, `dispatch`,
  `forgejo`, `gate`, `service`).
- Dead code exposed by tightening removed: `publish_freshness_toml`,
  `auto_commit_freshness`, `exec_on_gate`, `resolve_gate_ssh`,
  `sync` wrapper, `check_all`, `TemporalReport` struct.
- Future infrastructure suppressed: ribocipher, manifest/wave, webhook
  payload types.

### Allocation Elimination

- `detect_target_triple()` → `const fn` returning `&'static str`.
  Eliminates ~25 `String` allocations and clone chains across
  gate/plasmid/temporal modules.
- `compute_blake3_file_async(impl AsRef<Path>)` — callers pass `&path`
  instead of cloning `PathBuf`.
- `verify_blake3_async(impl AsRef<Path>, &str)` — eliminates `String`
  clones at hash verification sites.

### Error Taxonomy

`ShadowError::Parse` reclassified at 8 sites:

| Site | Old | New |
|------|-----|-----|
| webhook HMAC key/signature | `Parse` | `Config` |
| push-event JSON | `Parse` | `Json` |
| forgejo SSH token ops | `Parse` | `Ssh` |
| forgejo version parse | `Parse` | `Config` |
| task panic (impulse, context) | `Parse` | `Io` |
| HTTP request/JSON failures | `Parse` | `Http` |
| gateway file read | `Config` | `Io` |

### Domain Constants Centralization

New constants in `cellmembrane-types/src/service/constants.rs`:
- `GIT_DOMAIN` (`git.primals.eco`)
- `DEPOT_DOMAIN` (`depot.primals.eco`)
- `MESH_DOMAIN` (`mesh.primals.eco`) — also fixed `mesh.primal.eco` typo
- `LAB_DOMAIN` (`lab.primals.eco`)
- `GITHUB_HOST` (`github.com`)
- `GITHUB_API` (`https://api.github.com`)

Replaced hardcoded domains in: caddy, gateway, drift, manifest,
fetch, download (6 files).

---

## Open Items for Upstream Teams

### sporePrint (P0 — Root 404)
sporePrint health check is wired in cascade post-sync (Wave 141b) but
the actual rebuild on golgi needs sporePrint/golgi team attention.

### sporeGate (P0 — Re-harvest)
Full re-harvest (14 × 4 arch = 56 binaries) is READY — all platform
blockers resolved across all 14 primals. Needs sporeGate build run.

### primalSpring
- `full-cross-compile` scenario (P1, FRAGO issued)
- `depot-architecture-coverage` scenario (P2)

### Phase 2 Transport Abstraction (P2, all downstream)
`TransportEndpoint` trait evolution needed in: squirrel, rhizoCrypt,
biomeOS, sweetGrass, loamSpine, coralReef, skunkBat, barraCuda.
petalTongue `petal-tongue-platform` is the Phase 2 reference.

---

## Remaining cellMembrane Deep Debt (Lower Priority)

| Item | Priority | Notes |
|------|----------|-------|
| `build_err` → `impl Into<String>` | P3 | Removes forced `format!()` at ~23 call sites |
| Cytoplasm static IP table → manifest-only | P3 | Requires topology file migration |
| `SPOREPRINT_NUCLEUS_BINARIES` → manifest composition | P3 | Requires manifest schema for `[compositions.*]` |
| Named Pipe transport implementation | P3 | Windows parity — stub exists |
| Hetzner provisioning provider | P3 | Enum variant exists, returns error |
| ribocipher nuclear tier | P3 | Deferred until per-peer lineage keys |
| `DEFAULT_SERVICE_FILTER` → registry-derived | P3 | Eliminate hand-maintained primal regex |
| Non-Unix CSPRNG → `getrandom` | P3 | Currently BLAKE3-derived fallback |
