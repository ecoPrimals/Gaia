<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# CATHEDRAL — lithoSpore Bash-to-Rust Elevation & Deployment Validation

**Date**: May 15, 2026
**Scope**: lithoSpore (gardens/lithoSpore)
**Supersedes**: CATHEDRAL_USB_ASSEMBLY_MAY14_2026.md (entry point model changed)

---

## Summary

lithoSpore's bash-to-Rust elevation is complete. All 8 shell scripts that
previously drove data fetching, USB assembly, chaos testing, and deployment
validation have been replaced with pure Rust subcommands in the `litho` CLI.
The 7 separate module binaries have been unified into a single 5.1 MB
musl-static binary that dispatches via argv[0] symlink detection.

Cross-platform deployment validated across 5 Linux environments and Windows.

---

## Bash Scripts Removed

| Script | Replacement | Method |
|--------|-------------|--------|
| `scripts/assemble-usb.sh` | `litho assemble` | std::fs + walkdir + blake3 |
| `scripts/build-artifact.sh` | direct `cargo build --release --target musl` | n/a |
| `scripts/fetch_wiser_2013.sh` | `litho fetch --module ltee-fitness` | ureq + serde_json + blake3 |
| `scripts/fetch_barrick_2009.sh` | `litho fetch --module ltee-mutations` | ureq + serde_json + blake3 |
| `scripts/fetch_good_2017.sh` | `litho fetch --module ltee-alleles` | ureq + serde_json + blake3 |
| `scripts/fetch_blount_2012.sh` | `litho fetch --module ltee-citrate` | ureq + serde_json + blake3 |
| `scripts/fetch_tenaillon_2016.sh` | `litho fetch --module ltee-breseq` | ureq + serde_json + blake3 |
| `scripts/chaos-test.sh` | `litho chaos-test` | 10 fault injection tests, in-process |
| `scripts/deploy-test-local.sh` | `litho deploy-test` | assemble + verify + validate cycle |
| `validation/validate.sh` | `litho validate` | in-process module calls via lib::run_validation |

**Only remaining shell**: `scripts/build-container.sh` (OCI engine interaction).

## External Command Elimination

| Old Command | Replacement |
|-------------|-------------|
| `date -u +%Y-%m-%dT%H:%M:%SZ` | `chrono::Utc::now()` |
| `hostname` | `/etc/hostname` or `/proc/sys/kernel/hostname` (Linux), `%COMPUTERNAME%` (Windows) |
| `id -u` | `/proc/self/status` UID parsing (Linux), `%TEMP%` (Windows) |

## Binary Unification

7 module binaries (`ltee-fitness`, `ltee-mutations`, ..., `ltee-anderson`) unified
into single `litho` binary. Each module crate exposes `lib.rs::run_validation()`
for in-process dispatch — no subprocess spawning.

USB entry points (`validate`, `verify`, `refresh`, `spore`) are symlinks to
`bin/litho`. The binary inspects `argv[0]` to determine which subcommand to run.

## Platform Guards

`#[cfg(target_os = "windows")]` / `#[cfg(unix)]` / `#[cfg(not(unix))]` added to:
- `spore.rs` — hostname resolution
- `visualize.rs` — XDG runtime dir / temp path, UDS transport
- `assemble.rs` — symlink creation (copy fallback on Windows)
- `discovery.rs` — UDS socket discovery

## Deployment Test Matrix — All PASS

| Environment | Binary | Method | Result |
|------------|--------|--------|--------|
| Ubuntu 24.04 airgapped VM | musl-static | libvirt + cloud-init | **PASS** — 75/75 checks, 7/7 modules |
| Ubuntu 24.04 VPS VM | musl-static | libvirt + cloud-init | **PASS** — liveSpore.json provenance |
| Alpine 3.20 chroot | musl-static | chroot on host | **PASS** — musl libc portability proven |
| Read-only filesystem | musl-static | remount ro | **PASS** — graceful degradation |
| Isolated tmpdir | musl-static | cp to /tmp | **PASS** — no path assumptions |
| Windows x86_64 | litho.exe (7.9 MB) | Wine 11.0 | **PASS** — self-test + validate + verify |

## Build Artifacts

| Target | Size | Notes |
|--------|------|-------|
| `x86_64-unknown-linux-musl` | 5.1 MB | Statically linked, no libc dependency |
| `x86_64-pc-windows-gnu` | 7.9 MB | Cross-compiled via mingw-w64 |

## Documents Updated

- `README.md` — directory tree, 7/7 modules, Rust CLI references
- `GETTING_STARTED.md` — extending instructions, entry point names
- `docs/ARCHITECTURE.md` — crate tree, data flow, cross-platform table
- `docs/UPSTREAM_GAPS.md` — 7/7 status, bash migration DONE section
- `artifact/data.toml` — refresh_command fields → `litho fetch`
- `artifact/usb-root/.biomeos-spore` — entry: `spore.sh` → `spore`
- `Containerfile` — COPY shims → symlink creation
- `LITHOSPORE_USB_DEPLOYMENT.md` (wateringHole) — entry points, binary layout

## For Upstream Teams

- **primalSpring**: lithoSpore now fully composed via primal patterns. `ipc.resolve`
  method and `compute.dispatch` capability aligned with registry. Discovery chain
  tested: env → UDS → TURN → standalone.
- **benchScale / agentReagents**: New templates created (Alpine, Fedora, Debian,
  read-only). Deployment matrix script available at
  `agentReagents/scripts/lithoSpore-deployment-matrix.sh`.
- **petalTongue**: `litho-core::viz` DataBinding adapters ready for all 7 modules.
  Interactive SceneGraph handback in lithoSpore's `validation/handbacks/`.
