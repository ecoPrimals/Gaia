# blueGate Sub-Builder Coevolution Handoff

**Date**: Aug 3, 2026 | **Wave**: 156a | **From**: eastGate overwatch (sporeGate)
**Status**: ACTIVE — membrane updated, sub-builder dispatch proven E2E

---

## Current State

| Component | Status |
|-----------|--------|
| membrane.exe | `v0.1.0 (f8df585)` — all CI-EVO-01 + CI-DIV fixes |
| Rust target | `x86_64-pc-windows-gnu` installed |
| SSH from sporeGate | LIVE (PowerShell, `Host blueGate` in ssh config) |
| J12 sub-builder dispatch | PROVEN — squirrel built 24MB PE binary (80s) |
| WG mesh | `10.13.37.12` (LIVE) |
| Harvest scheduler | LIVE — `harvest.queue`, `harvest.request`, `harvest.schedule` |
| Ecosystem manifest | FIXED — `steamGate.mobility = "mobile"` fix propagated |

## What blueGate Has Now

1. **Full harvest scheduler** — same CLI as sporeGate:
   - `membrane.exe harvest.queue` — show queue
   - `membrane.exe harvest.request <primal>` — signal a build
   - `membrane.exe harvest.schedule` — batch-build ready primals
   - `membrane.exe harvest.schedule --dry-run` — preview

2. **Drift detection** — `plasmid.staleness` compares provenance vs local source HEAD

3. **Sub-builder role** — sporeGate dispatches via:
   ```
   sovereign.ci.trigger --primal <name>
   ```
   This SSHes to blueGate and runs `membrane.exe plasmid.harvest --primal <name> --force`

## blueGate Coevolution Tasks

### Tier 1: Windows Deployment Validation

blueGate is the **only Windows gate** in the mesh. It should evolve its local CI to:

1. **Build + validate primals natively** — run `membrane.exe plasmid.harvest --all --force`
   to build all primals for `x86_64-pc-windows-gnu` and validate they produce valid PE binaries.

2. **Run primal smoke tests** — each primal should at minimum start and respond to
   `--version` or health endpoints on Windows. Any primal that fails is a platform
   divergence that needs fixing upstream in cellMembrane.

3. **Report validation results** — push AARs to wateringHole documenting which primals
   work on Windows, which need platform-specific fixes, and what the divergences are.

### Tier 2: Windows-Specific Deployment

blueGate runs NUCLEUS on Windows. It should:

1. **Test `--with-restart` on Windows** — the new flag uses `systemctl` which doesn't
   exist on Windows. blueGate should evolve the restart logic to use Windows service
   management (`sc.exe stop/start` or PowerShell `Stop-Service/Start-Service`).

2. **Document Windows depot paths** — equivalent of the Linux 4-path divergence
   (CI-DIV-03) for Windows (`%LOCALAPPDATA%\ecoPrimals\plasmidBin\` etc.).

3. **Test depot sync** — `membrane.exe plasmid.depot_sync --push` should work from
   blueGate to push Windows binaries to the golgi depot.

### Tier 3: Distributed Builder Autonomy

blueGate should be able to:

1. **Accept harvest.request** — when sporeGate dispatches a build, blueGate's scheduler
   should ingest it and batch with any other pending builds.

2. **Push built binaries to depot** — after local harvest, push Windows binaries
   directly to golgi depot (`membrane.exe plasmid.depot_sync --push`).

3. **Notify mesh on completion** — use songBird mesh to announce build completion
   so downstream gates know new Windows binaries are available.

## Proven E2E Path

```
sporeGate                          blueGate
┌──────────────────┐   SSH/PS     ┌─────────────────┐
│ sovereign.ci.    │──────────────│ membrane.exe     │
│ trigger          │              │ plasmid.harvest  │
│ --primal squirrel│              │ --primal squirrel│
│                  │              │ --force          │
│ Detects:         │              │                  │
│   windows-gnu    │              │ Builds PE binary │
│   not local      │              │ 24MB, 80s        │
│   dispatch to    │              │ BLAKE3 checksum  │
│   blueGate       │              │ Provenance       │
└──────────────────┘              └─────────────────┘
```

## What Changed This Session

- 30 stale membrane processes killed (hung SSH dispatches from old `882ad09` binary)
- membrane.exe updated: `882ad09` → `f8df585` (44 commits ahead)
- wateringHole pulled: manifest parse fix + all new AARs/specs
- squirrel built successfully as Windows PE binary (24683KB)
- CI-DIV-05 warning confirmed working: manifest parse errors now visible

## Next Handoff Items for Overwatch

1. blueGate should run `membrane.exe plasmid.harvest --all --force` to build all 13
   primals for Windows and report which succeed/fail.
2. Any platform-specific build failures (missing Windows APIs, path issues, etc.)
   should be filed as divergences in wateringHole.
3. blueGate's Windows depot should be pushed to golgi so other gates can fetch
   Windows binaries for testing.
