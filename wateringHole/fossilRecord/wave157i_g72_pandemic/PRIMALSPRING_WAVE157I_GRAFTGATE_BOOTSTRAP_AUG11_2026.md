# primalSpring Wave 157i — graftGate Bootstrap + G72 Post-Pandemic

**Date**: Aug 11, 2026
**Team**: primalSpring (eastGate)
**Wave**: 157i (PANDEMIC RESPONDS)
**Commit**: `febdef7f`

## Delivered

### graftGate Target Support

New `Aarch64Darwin` variant in `evolution/target.rs`:

| Property | Value |
|----------|-------|
| Triple | `aarch64-apple-darwin` |
| Deployment tier | Permissive (same as x86_64 Linux) |
| Composition tier | Full (13 primals) |
| UDS | Yes (macOS supports Unix domain sockets) |
| Filesystem | Yes |
| Init system | launchd (cellMembrane `InitSystem::Launchd` path) |
| Selection pressures | IpcTransport + Network |

### Configuration Updates

- `mesh_topology.toml`: graftGate added (build role, House2 zone, LAN transport)
- `deployment_matrix.toml`: `aarch64-apple-darwin` added to architectures array + pending cell
- `biome-eastgate.yaml`: graftGate added to federation peers (6 → 7)

### G72 Post-Pandemic Baseline Tightening

exp123 thresholds updated for post-pandemic state (9/9 teams Tier 1 complete):

| Metric | Pre-pandemic | Post-pandemic |
|--------|-------------|---------------|
| tokio[full] | ≤3 | = 0 |
| HTTP clients | ≤8 | ≤5 |
| env_logger | ≤4 | ≤2 |

Tier 2 targets queued: HTTP→songBird, axum→0.8, wgpu→28.

### Code Changes

- `evolution/target.rs`: `Aarch64Darwin` variant + all match arms (triple, has_uds, has_filesystem, tier, etc.)
- `evolution/profile.rs`: apple-darwin detection before linux-aarch64 fallback
- `evolution/pressure.rs`: `Aarch64Darwin` selection pressure arm

### Test State

- **1,274 tests, 0 failures, 0 clippy errors**

## graftGate Bootstrap Plan (from eastGate)

primalSpring owns cross-arch validation. When graftGate comes online:

1. eastGate validates `aarch64-apple-darwin` binaries via depot checksums
2. exp096 (cross-arch) runs against graftGate deployment matrix cell
3. `nucleus_launcher reconcile` verifies manifest-vs-reality on graftGate
4. Composition validation: Tower Atomic first, then expand to Full NUCLEUS
