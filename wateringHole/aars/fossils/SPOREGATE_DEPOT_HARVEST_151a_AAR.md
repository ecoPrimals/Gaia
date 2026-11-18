# sporeGate Depot Harvest AAR — Wave 151a

**Date**: Jul 25, 2026 | **Wave**: 151a | **From**: sporeGate topology/hardware team
**To**: All teams

---

## Context

Wave 151a declared Tower Atomic COMPLETE (7/7 debt items resolved) and
identified a **P0: DEPOT DIVERGENCE** — golgiBody's `plasmidBin` was 40 days
stale (provenance dated Jun 15), 12/13 x86_64 binaries predated Tower
hardening, and no aarch64 target directory existed.

## Actions Taken

### 1. Full x86_64-unknown-linux-musl Harvest

- **14/14 primals** rebuilt from HEAD (~20 minutes total build time)
- Binaries stripped and deployed to local depot via rename trick
  (running services hold file descriptors; `mv old; cp new; rm old`)
- songBird rebuilt twice — once in initial batch, once after pulling
  4 new commits (tower debt 6/7, blake3 method fix, mesh dedup)
- Stale `-next` binaries (`beardog-next`, `songbird-next` from Jul 4) cleaned

### 2. Full aarch64-unknown-linux-musl Harvest

- Cross-compile toolchain was **already installed** (rustup target +
  `aarch64-linux-gnu-gcc` linker configured in `.cargo/config.toml`)
- **14/14 primals** cross-compiled successfully (~25 minutes)
- Zero build failures across all primals
- **New target directory created** on golgiBody — grapheneGate now has binaries

### 3. Provenance Tracking

- `provenance.toml` generated for both architectures with:
  - `builder = "sporeGate"` (gate attribution — was "unknown")
  - Per-primal HEAD commit hash
  - Per-primal binary size
  - Toolchain version (`rustc 1.94.0`)
  - Host identification

### 4. golgiBody Depot Refresh

- Both architectures pushed via rsync
- x86_64: 16 files (14 primals + membrane + provenance)
- aarch64: 15 files (14 primals + provenance)
- All timestamps now Jul 25 (was Jun 15–Jul 11)

## Depot Before vs After

| Metric | Before | After |
|--------|--------|-------|
| Provenance age | 40 days (Jun 15) | 0 days (Jul 25) |
| Builder identity | `"unknown"` | `"sporeGate"` |
| x86_64 primals | 13 (12 stale) | 14 (all fresh) |
| aarch64 primals | 0 (no directory) | 14 (all fresh) |
| songBird version | Pre-tower-debt | 59c221b (tower debt 7/7) |
| bearDog version | Pre-enrollment-decomp | 6a351b8 (BTSP strict, enrollment decomp) |
| skunkBat version | Pre-public-release | a8cf5aa (public, cipher floor) |
| Stale -next files | 2 | 0 |

## Binary Sizes (x86_64 / aarch64)

| Primal | x86_64 | aarch64 |
|--------|--------|---------|
| barracuda | 5.3 MB | 4.2 MB |
| beardog | 11.1 MB | 8.8 MB |
| biomeos | 14.9 MB | 12.3 MB |
| coralreef | 7.5 MB | 6.5 MB |
| loamspine | 4.5 MB | 3.8 MB |
| nestgate | 8.5 MB | 7.3 MB |
| petaltongue | 28.1 MB | 25.3 MB |
| rhizocrypt | 7.2 MB | 5.8 MB |
| skunkbat | 2.8 MB | 2.4 MB |
| songbird | 18.7 MB | 15.2 MB |
| squirrel | 4.3 MB | 3.4 MB |
| sweetgrass | 7.6 MB | 7.0 MB |
| toadstool | 12.9 MB | 9.7 MB |
| sourdough | 3.0 MB | 2.5 MB |
| **Total** | **~137 MB** | **~114 MB** |

## Observations

1. **Cross-compile "just works"**: aarch64 target + GNU linker + `crt-static`
   flag produced zero build failures across all 14 primals. No source changes
   needed for Silicon Atheism — the architecture is truly abstracted.

2. **Rename trick is load-bearing**: Multiple depot binaries are held open by
   running services (songbird-gateway, beardog, etc.). Direct `cp` fails with
   ETXTBSY. The `mv old; cp new; rm old` pattern is essential for live depot
   updates without service interruption.

3. **songBird had 4 post-deploy commits**: Our "fresh" Jul 25 binary from
   earlier in the day was already stale by cascade time. Tower debt resolution
   (retry, health check, socket watch, IPC pool, announce validation,
   capability revocation) and blake3 method name fix were all in those commits.

4. **membrane not harvested**: The `membrane` binary (cellMembrane) was
   already recent (Jul 23) and not part of the 13-primal manifest. It was
   carried forward as-is. cellMembrane team owns its build cycle.

## Sovereign CI Gap

The blurb correctly identifies that `plasmid.harvest --all` doesn't exist yet
as a membrane subcommand. The current harvest was manual (shell loop over
`cargo build`). For the pipeline to catch drift automatically:

- **cellMembrane code team**: Ship `plasmid.harvest --all` + `plasmid.status`
  drift alarm (>7 days stale warning)
- **cellMembrane code team**: `provenance.toml` builder attribution on harvest
- **cellMembrane code team**: Multi-target harvest via `targets` field in manifest

Until then, sporeGate topology team will run manual harvests as needed.

## Remaining (P1/P2)

| # | Task | Priority | Owner |
|---|------|----------|-------|
| 1 | Gate enrollment (southGate, strandGate) | P1 | sporeGate — USB staged, physical cabling |
| 2 | songBird crypto delegation (6 seams) | P1 | flockGate songBird team |
| 3 | bearDog pen test | P2 | flockGate bearDog team |
| 4 | grapheneGate → floating autonomous gate | P2 | sporeGate — post aarch64 depot |
| 5 | Chimera Phase 0 (libtower.so) | P2 | blocked on crypto delegation |

---

*Depot divergence resolved. 28 binaries across 2 architectures, provenance
tracked, golgiBody synced. Tower Atomic COMPLETE. Next horizon: Nest Atomic.*
