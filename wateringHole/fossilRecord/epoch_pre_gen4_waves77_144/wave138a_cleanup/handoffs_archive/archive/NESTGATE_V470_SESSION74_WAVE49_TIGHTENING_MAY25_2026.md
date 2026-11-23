# NestGate v4.7.0-dev — Sessions 73–76 Doc Refresh + Wave 49 Handoff

**Date**: May 25, 2026  
**Sessions**: 73–76  
**Version**: 4.7.0-dev (internal iteration; workspace `0.1.0`, binary `2.1.0`)  
**Primal**: nestgate  
**Status**: Zero debt — all waves current through Wave 49, aarch64-musl segfault fixed

---

## Summary

Four sessions following the Session 72 deep debt sweep: doc synchronization,
fossil banners on superseded docs, Wave 49 post-primordial tightening, and
the aarch64-musl segfault root-cause fix.

---

## Session 73: Root Doc Refresh + Fossil Banners (May 24, 2026)

- All 10 root markdown files synchronized to Session 72 / Wave 47 metrics
- Removed stale `tools/unwrap-migrator` references (tool removed, crate count 23 → 22)
- Fossil banners added to 5 docs superseded by `specs/` counterparts
- sporeprint capability tables corrected (model/zfs method names)
- `.gitignore` cleaned (stale `/unwrap-migrator/target/` entry)

## Session 74: Wave 49 Ecosystem Tightening (May 25, 2026)

- `plasmidBin` documented as sole production binary channel in root docs
- 6 additional fossil banners on pre-Wave-49 CLI/deployment guides
- `genomeBin` → `plasmidBin` terminology updated in `.cargo/config.toml` and `graphs/*.toml`
- 3 dead fuzz targets removed (796 lines of broken imports)
- `DEPLOYMENT_GUIDE.md` received post-primordial notice

### Wave 49 Verification Checklist

- [x] No `showcase/` directory
- [x] No local `wateringHole/` tree
- [x] No `which nestgate` or `target/release/nestgate` in scripts/CI
- [x] `notify-plasmidbin.yml` active and correctly configured
- [x] No `cargo install nestgate` in CI workflows

---

## Metrics (unchanged from Session 72)

```
Workspace packages:  22 (20 code/crates + fuzz + root)
RPC lib tests:       682 passing, 0 failures
Full workspace:      12,399+ tests, 0 failures
Clippy:              zero warnings (pedantic + nursery)
Coverage:            84.12%+ line (llvm-cov)
UDS methods:         68 (UNIX_SOCKET_SUPPORTED_METHODS)
Capability domains:  16 (capability_registry.toml)
File size:           all .rs under 800 lines
Unsafe:              #![forbid(unsafe_code)] on ALL crate roots
```

---

## Fossil Record

11 docs in `docs/` now carry fossil banners pointing to canonical `specs/` counterparts
or current root docs. 6 pre-Wave-49 CLI guides carry banners noting `plasmidBin` as the
production deployment channel.

---

## Session 76: aarch64-musl Segfault Fix — Validated (May 25, 2026)

- **Root cause**: `.cargo/config.toml` specified `linker = "aarch64-linux-gnu-gcc"` for
  `aarch64-unknown-linux-musl`. Without `link-self-contained=yes`, the GNU linker provided
  glibc CRT startup objects instead of musl's, causing a segfault on aarch64 systems
  (the `nucleus-aarch64-mixed-tcp` cell blocker from Wave 49 re-audit).
- **Fix**: `linker = "ld.lld"` (LLVM LLD, cross-arch capable) + `linker-flavor=ld` +
  `link-self-contained=yes` (musl CRT from Rust sysroot). x86_64-musl also updated to
  `link-self-contained=yes` (drops `musl-gcc` dep).
- **Validated on dev host**: aarch64 binary built, inspected (ELF 64-bit, ARM aarch64,
  statically linked, stripped, 6.8M, no dynamic section), and executed under
  `qemu-aarch64-static` — `--help` and `version` subcommands run without segfault.
  x86_64-musl also built and validated (7.8M, static, EXEC). 1,648 workspace tests pass.
- **Build deps**: aarch64-musl now needs `lld` (apt) + Rust target only. x86_64-musl
  is fully self-contained. Eliminates `musl-tools` and `gcc-aarch64-linux-gnu`.

---

## Open Items

- Push coverage 84.12% → 90% target
- Track vendored `rustls-rustcrypto` + `rustls-webpki` upstream for drop opportunity
- Verify aarch64-musl fix on actual aarch64 hardware (QEMU validation passed; next harvest cycle deploys)
