# Wave 56: Primordial Pattern Disconnection — VPS Deployment Standard

**Date:** May 27, 2026
**Author:** primalSpring (automated)
**Scope:** primalSpring, cellMembrane (downstream)

---

## Summary

Systematically disconnected primordial deployment patterns from the VPS
standard path. Springs can now deploy exclusively via `biomeos deploy` against
cellMembrane VPS with zero shell launcher involvement.

## Changes

### 1. Env Var Centralization (RESOLVED)

All scattered env var literals now route through `env_keys.rs`:
- Added: `SONGBIRD_PEERS`, `SONGBIRD_SECURITY_SOCKET`, `BIOMEOS_GRAPHS_DIR`,
  `BIOMEOS_PLASMID_BIN_DIR`, `HOST`
- Fixed: 12 literal `std::env::var("...")` calls in `nucleus_launcher`,
  `tolerances`, `s_sporeprint_surface`, `s_deployment_pipeline` now use
  `env_keys::` constants
- Deprecated: `launcher::discovery::ENV_PLASMID_BIN` and `ENV_BIOMEOS_BIN_DIR`
  (use `env_keys::ECOPRIMALS_PLASMID_BIN` / `BIOMEOS_PLASMID_BIN_DIR`)

### 2. VPS Deployment Contract

Documented in `docs/PRIMAL_GAPS.md` and `graphs/cells/cells_manifest.toml`:

```
1. deploy_membrane.sh / plasmidbin deploy → NUCLEUS base (13 primals)
2. biomeos deploy graphs/cells/{spring}_cell.toml → overlay (spawn=false)
3. CompositionContext::from_live_discovery() → Rust runtime via UDS tiers 2-4
```

### 3. Cell Graph VPS Readiness

Added `vps_standard` field to `cells_manifest.toml`:
- **VPS-ready** (spawn=false overlays): hotspring, wetspring, neuralspring,
  airspring, groundspring, healthspring
- **Desktop-only** (spawn=true): nucleus_desktop, ludospring, esotericwebb

### 4. `nucleus_launcher --uds-only`

New `--uds-only` flag for VPS-standard zero-TCP-port deployment:
- Suppresses `--port` CLI arg to primals
- Health checks via UDS socket presence instead of TCP probe
- Displayed as "UDS-only (VPS standard)" in launch banner

Usage: `nucleus_launcher start --family-id cell-1 --uds-only`

### 5. Desktop-Only Script Marking

`desktop_nucleus.sh` and `cell_launcher.sh` now carry prominent VPS-exclusion
headers documenting that they must not be used for cellMembrane deployments.

### 6. Launcher Module Documentation

Updated `launcher/mod.rs` module docs to clearly distinguish:
- VPS-needed: `discover_binary`, `SocketNucleation`, `LaunchProfile`, `LaunchError`
- Desktop-only (deprecated): `spawn_primal`, `spawn_biomeos`, `PrimalProcess`

---

## cellMembrane Team Action Items

1. **Use `--uds-only` for VPS launches**: when invoking `nucleus_launcher` from
   `deploy_membrane.sh`, add `--uds-only` to suppress TCP port allocation
2. **Consume spring cell graphs**: `graphs/cells/{spring}_cell.toml` files with
   `vps_standard = true` are ready for direct `biomeos deploy`
3. **No shell launchers**: `desktop_nucleus.sh` and `cell_launcher.sh` are
   explicitly marked as desktop-only and must not appear in VPS provisioning

## What Remains (Future Waves)

| Item | Blocker |
|------|---------|
| Retire `harness/mod.rs` | 5 integration tests need migration to live-NUCLEUS stubs |
| Remove deprecated `spawn_primal`/`spawn_biomeos` | Harness retirement |
| Normalize `esotericwebb_cell.toml` spawn flags | Needs CRPG domain audit |
| `plasmidbin fetch` replaces `fetch_primals.sh` | plasmidBin CLI v0.6.0 |

---

*797 lib tests pass. 0 clippy warnings. Checksums regenerated.*
