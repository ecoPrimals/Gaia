# AAR: Depot Full Harvest — Wave 139b

**Date**: 2026-07-15 02:20 UTC | **Gate**: sporeGate (eastGate overwatch)
**Wave**: 139b | **Severity**: P2 divergence resolution
**Author**: sporeGate topology team

---

## Summary

Resolved `DEPOT-COVERAGE` P2 divergence. Full multi-architecture harvest executed
on sporeGate as build authority. All 14 primals + membrane rebuilt for x86_64-musl
and aarch64-musl, plus first Windows binary (songBird) for northGate mesh enrollment.
Depot signed, verified, and pushed to golgi VPS. Live serving confirmed at
`membrane.primals.eco/depot/`.

## What Happened

### Context
The Wave 139b blurb reported `DEPOT-COVERAGE` as the sole remaining divergence:
"genomeBin on sporeGate has 6/14 primals — needs full harvest." Investigation
revealed the blurb referenced a stale `genomeBin` path. The actual depot at
`/opt/ecoPrimals/depot/` already had 16 binaries per architecture, but they were
built on Jul 13 — before bearDog's FIDO2 refactor, songBird's Windows cross-compile,
nestGate's debt sweep, and cellMembrane's cascade fixes.

### Actions Taken

1. **x86_64-unknown-linux-musl harvest** — Built all 14 primals (beardog, songbird,
   biomeos, barracuda, coralreef, nestgate, petaltongue, rhizocrypt, skunkbat,
   sourdough, squirrel, sweetgrass, toadstool, loamspine) plus membrane. All
   statically linked (musl), stripped. 16 binaries total.

2. **aarch64-unknown-linux-musl harvest** — Cross-compiled all 14 primals plus
   membrane for ARM64. 16 binaries total. Covers grapheneGate (Pixel), any future
   ARM gates, and Raspberry Pi deployments.

3. **x86_64-pc-windows-gnu target added** — Installed `x86_64-pc-windows-gnu`
   Rust target on both stable and 1.94.0 toolchains. Installed `gcc-mingw-w64-x86-64`
   cross-compiler. Built songBird as first Windows binary (`songbird.exe`, 14.9MB
   PE32+ executable). This directly enables northGate mesh enrollment.

4. **Checksums regenerated** — Fresh `checksums.toml` with BLAKE3 hashes for all
   49 binaries across 4 architectures (aarch64-android, aarch64-musl, x86_64-musl,
   x86_64-windows-gnu).

5. **Depot signed** — `membrane sign.activate` via bearDog UDS socket. Ed25519
   signature in `signatures.toml`. Verified with `membrane sign.verify`.

6. **VPS sync** — `rsync` pushed entire depot to golgi (`[RELAY_PUBLIC]:/opt/ecoPrimals/depot/`).
   33 changed files transferred (~51MB). Live HTTPS serving confirmed at
   `membrane.primals.eco/depot/`.

## Depot State Post-Harvest

| Architecture | Binaries | Status |
|---|---|---|
| x86_64-unknown-linux-musl | 16 | All fresh (Jul 15) |
| aarch64-unknown-linux-musl | 16 | All fresh (Jul 15) |
| aarch64-linux-android | 3 | Stale (Jul 13) — beardog, nucleus_launcher, songbird |
| x86_64-pc-windows-gnu | 1 | NEW — songbird.exe |

**Total**: 36 fresh binaries + 3 stale Android = 39 depot binaries

## Remaining Android Staleness

The 3 Android binaries (beardog, nucleus_launcher, songbird) are from Jul 13.
These should be re-harvested when grapheneGate work resumes. The Android build
requires NDK toolchain setup (`ANDROID_NDK_HOME` + linker configuration).

## What Worked

- **Local checkout builds**: Building from local Git repos was dramatically faster
  than the `membrane plasmid.harvest` clone-from-remote approach. Most primals
  had cached dependencies and compiled in <30 seconds.
- **membrane sign.activate**: Signing via bearDog UDS socket worked perfectly.
  No FIDO2 touch required (Ed25519 depot signing uses software keys, not hardware).
- **rsync delta compression**: Only changed data transferred — full depot sync
  in 3.6 seconds over WireGuard.

## What Didn't Work

- **membrane plasmid.harvest** — The `membrane` binary (Jul 13) crashed with
  "No such file or directory" for all `plasmid.*` commands. Root cause: the binary
  expects `sources.toml` in the depot directory (which didn't exist there) and
  requires `PLASMIDBIN_DEPOT` environment variable. After rebuilding membrane
  from source, the commands worked but harvest clones from GitHub remotes rather
  than using local checkouts.
- **membrane plasmid.depot_sync** — SSH command failed because the SSH config
  doesn't have a `golgi` host entry (only has `pepti` at a different VPS). Direct
  rsync was used as workaround.

## Lessons for cellMembrane Team

1. **Add `golgi` SSH config**: `membrane plasmid.depot_sync` assumes SSH access
   to the VPS via the `ShadowConfig`. Consider supporting `--host user@ip` override.
2. **Local checkout harvest**: `membrane plasmid.harvest --local` flag would skip
   the clone step and build from `ECOPRIMALS_ROOT/primals/`. This is ~10x faster.
3. **Depot self-healing**: `sources.toml` should be auto-generated or symlinked
   into the depot directory during harvest, not required as a pre-condition.

## Impact

- **DEPOT-COVERAGE P2**: RESOLVED — 16/16 binaries across musl targets.
- **northGate mesh enrollment**: UNBLOCKED — songbird.exe available at depot.
- **Universal deployment**: 4 architectures now served from single depot endpoint.
- **Signature chain intact**: Ed25519 signed, BLAKE3 verified, sporeGate attested.

## Cross-Team Handoffs

| Team | Item |
|---|---|
| cellMembrane | Fix `plasmid.depot_sync` SSH config, add `--local` harvest mode |
| bearDog | Android depot binaries stale (re-harvest when NDK available) |
| songBird | Windows binary ready — northGate can `curl` it from depot |
| overwatch | All gates can now `plasmid.fetch` fresh binaries |

---

*Classified: INTERNAL — sporeGate topology team operational record*
