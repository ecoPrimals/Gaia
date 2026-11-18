# plasmidBin Push Automation Pipeline — Ecosystem Standard

**Status**: ACTIVE  
**Version**: 2.0 — Rust CLI  
**Date**: May 26, 2026  
**Authority**: primalSpring (pipeline owner)  
**Depends on**: [ECOBIN_ARCHITECTURE_STANDARD.md](ECOBIN_ARCHITECTURE_STANDARD.md)

---

## Overview

Every push to a primal's `main` branch triggers an automated pipeline that
builds ecoBin-compliant static binaries, computes BLAKE3 checksums, publishes
to `plasmidBin`, and creates GitHub Releases. This document defines the
pipeline, its components, and the contract each primal team must uphold.

## Pipeline Flow

```
Primal push to main
        │
        ▼
notify-plasmidbin.yml (per-primal workflow)
  sends repository_dispatch event-type: primal-updated
  payload: { primal, sha }
        │
        ▼
auto-harvest.yml (plasmidBin repo)
        │
   ┌────┴────┐
   │ prepare  │  Determine primal + version tag
   └────┬────┘
        │
   ┌────┴──────────────────────────┐
   │ build (3x parallel matrix)    │
   │  x86_64-unknown-linux-musl    │
   │  aarch64-unknown-linux-musl   │
   │  armv7-unknown-linux-musleabihf│
   └────┬──────────────────────────┘
        │
   ┌────┴──────────┐
   │  consolidate          │
   │  plasmidbin harvest    │  per-arch: validate, strip, BLAKE3, copy
   │  ↓                     │
   │  commit                │  checksums.toml + binaries
   │  ↓                     │
   │  plasmidbin validate   │  post-harvest integrity check
   │  ↓                     │
   │  release               │  GitHub Release (vYYYY.MM.DD)
   └────────────────────────┘
        │
        ▼
Downstream consumers (plasmidbin fetch)
  verify BLAKE3 against checksums.toml
```

## Triggers

| Trigger | When | Scope |
|---------|------|-------|
| `repository_dispatch` | Primal pushes to `main` | Single primal |
| `workflow_dispatch` | Manual (operator) | Single primal or `all` |
| `check-updates.yml` (daily) | Lightweight tag checker dispatches stale primals | Per-primal (selective) |
| Weekly cron (Monday 06:00 UTC) | Full sweep | `all` |

The daily `check-updates.yml` replaces the old full-sweep cron. It queries
GitHub Releases for upstream tag changes and dispatches `auto-harvest` only
for primals with new tags. `plasmidbin harvest` skips binaries whose BLAKE3
hash already matches `checksums.toml`.

## Primal Team Contract

Every primal repository with its own git repo MUST have:

1. **`.github/workflows/notify-plasmidbin.yml`** — the dispatch workflow.
   Template lives at `infra/plasmidBin/templates/notify-plasmidbin.yml`.
   Copy it verbatim; do not customize.

2. **`PLASMIDBIN_DISPATCH_TOKEN` secret** — a GitHub PAT with `repo` scope on
   the `ecoPrimals/plasmidBin` repository. Set as a repository secret.

3. **`sources.toml` entry** — `infra/plasmidBin/sources.toml` must have a
   `[sources.<primal>]` section with the correct `repo` URL.

### Current Wiring Status (May 2026)

All 13 primals with their own repositories are wired:
bearDog, songbird, toadStool, barraCuda, coralReef, rhizoCrypt, loamSpine,
sweetGrass, biomeOS, squirrel, petalTongue, skunkBat, nestGate.

## Key Commands (Rust CLI — Wave 51)

All pipeline operations now use the `plasmidbin` Rust CLI (15 subcommands).
Legacy `.sh` scripts have been fossilized (Wave 66). The `plasmidbin` binary is the sole pipeline.

### `plasmidbin build`

Clones a primal (from `sources.toml`), builds for a target triple, and stages
the binary to `/tmp/primalspring-deploy/primals/{triple}/`.

```
cargo run -p plasmidbin -- build beardog --target x86_64-unknown-linux-musl
cargo run -p plasmidbin -- build all --target aarch64-unknown-linux-musl
```

### `plasmidbin harvest`

Takes staged binaries, validates they are static ELFs, strips them, computes
BLAKE3 checksums, copies to `plasmidBin/primals/{triple}/`, and updates
`checksums.toml`.

**Idempotent**: If the computed BLAKE3 hash matches the existing
`checksums.toml` entry, the binary is skipped. This prevents no-op commits
from polluting git history during reconciliation runs.

```
cargo run -p plasmidbin -- harvest --source /path/to/bins --arch x86_64-unknown-linux-musl
cargo run -p plasmidbin -- harvest --primal beardog --arch aarch64
cargo run -p plasmidbin -- harvest --dry-run
```

Exit code 1 if any binary fails validation.

### `plasmidbin fetch`

Downloads binaries from GitHub Releases, verifies BLAKE3 checksums against
`checksums.toml`, and installs to `primals/{triple}/`. Auto-detects host
architecture.

```
cargo run -p plasmidbin -- fetch --all
cargo run -p plasmidbin -- fetch --primal beardog
cargo run -p plasmidbin -- fetch --all --release v2026.05.26
```

### `plasmidbin validate`

Post-harvest integrity check. Reads `manifest.toml`, `checksums.toml`, and
`sources.toml`; verifies cross-references and checksum presence.

```
cargo run -p plasmidbin -- validate .
```

## `checksums.toml` Format

```toml
[primals.beardog]
"x86_64-unknown-linux-musl" = "<blake3-hex>"
"aarch64-unknown-linux-musl" = "<blake3-hex>"
"armv7-unknown-linux-musleabihf" = "<blake3-hex>"
```

Keys are full Rust target triples (quoted). Values are 64-character lowercase
hex BLAKE3 hashes of the stripped binary. Sections follow the pattern
`primals.<name>` or `springs.<name>`.

## Error Handling

The pipeline is designed to **fail loudly** rather than commit stale checksums:

- **Build failures**: `fail-fast: false` in the matrix means all three arches
  attempt to build, but the consolidate job tracks failures per-arch and
  aborts if any harvest exits non-zero.

- **Harvest failures**: `plasmidbin harvest` exits 1 if any binary fails
  static ELF validation. The consolidate step counts failures across all
  arches and aborts before committing if any occurred.

- **Post-harvest validation**: After committing, a validation step re-reads
  every binary on disk and re-computes BLAKE3 against `checksums.toml`.
  If any mismatch is found, the job fails. This catches races where a
  concurrent push updated `checksums.toml` between harvest and commit.

## Sovereign CI Bridge (Tier 3 — Pre-Stadial)

The current pipeline runs on GitHub Actions. The interstadial exit plan
(H3-02/03/04) includes migrating to sovereign Forgejo CI on ironGate
(`git.primals.eco`).

**Preparation**:
- `sources.toml` will gain a `forge` field per primal pointing to the
  Forgejo mirror. `plasmidbin build` will fall back to Forgejo when
  GitHub clone fails.
- Forgejo Actions runner on biomeGate (GPU access for coralReef/toadStool
  sovereign builds).
- Shadow CI: run both GitHub and Forgejo in parallel, compare checksums,
  cut over when parity is proven.
- NestGate as release artifact store (`content.put` with BLAKE3 provenance)
  replaces GitHub Releases for sovereign distribution.

Cross-arch on Forgejo (single x86_64 machine) will use QEMU or
cross-compilation initially; dedicated aarch64/armv7 runners are a stadial
item.

## References

- [ECOBIN_ARCHITECTURE_STANDARD.md](ECOBIN_ARCHITECTURE_STANDARD.md) — binary compliance
- [GLACIAL_SHIFT_READINESS.md](GLACIAL_SHIFT_READINESS.md) — H3 sovereign CI gates
- `infra/plasmidBin/` — pipeline source code
- `infra/plasmidBin/templates/` — workflow templates for primal repos
