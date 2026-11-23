# ToadStool Wave 155i — Deployment Docs + Doctor Fix (S345)

**Date**: Jul 29, 2026 | **Gate**: strandGate | **Wave**: 155i
**Team**: toadStool code team (Compute Trio)

---

## Summary

P1 #5 resolved: deployment model documentation written. Production deployment
guide rewritten from scratch. Doctor CLI panic fixed (clap arg conflict).
Hardware validated on strandGate (RTX 3090, 128 cores, Tower LIVE).

---

## P1 #5 RESOLVED: Deployment Documentation

`docs/reference/PRODUCTION_DEPLOYMENT_GUIDE.md` rewritten with:

- **Three deployment patterns**: Standalone, Node Atomic (Tower + ToadStool),
  NUCLEUS Composition (biomeOS signal graph)
- **Complete CLI reference**: `toadstool server` flags, no `start` subcommand
  (corrects stale guide)
- **systemd unit template**: Type=notify, FDSTORE for VFIO, ProtectSystem=strict,
  RuntimeDirectory
- **Full env var reference**: identity, server, execution, security, GPU vars
- **Socket resolution order**: 7-tier fallback chain
- **Health probe guide**: early responder, liveness/readiness/check methods,
  timeout guidance (>=3s, +5s for BTSP)
- **Tower dependency**: graceful degradation table (crypto, coordination,
  distributed, biomeOS — all optional)
- **Deployment checklist**: standalone, Node Atomic, NUCLEUS
- **BYOB server**: documented as separate deployment from `toadstool server`

## Bug Fix: Doctor CLI Panic

**Symptom**: `toadstool doctor` panicked with:
```
Mismatch between definition and access of `config`.
Could not downcast to std::path::PathBuf, need to downcast to bool
```

**Root cause**: Root `Cli` struct defines `--config` as `Option<PathBuf>` with
`global = true`. `Doctor` subcommand also defined `config: bool` for
`--config-check` functionality. Clap's global arg shadowing caused a type
mismatch at runtime.

**Fix**: Renamed `Doctor.config` → `Doctor.check_config`, CLI flag
`--config` → `--config-check`. All tests updated (14 doctor tests + 6
integration test constructors).

## Hardware Validation (strandGate)

```
toadstool doctor output:
  CPU Cores: 128 (Dual EPYC 7713)
  GPU: GPU adapter available via wgpu (RTX 3090, 24GB)
  NPU: Akida NPU detected
  Memory: 257755 MB (258 GB)
  biomeOS Directory: /run/user/1000/biomeos (exists)
  Sockets Found: 17 (Tower LIVE)
  Primal Status: 14 OK, 3 unreachable (stale test sockets)
```

## Quality Gates

| Gate | Result |
|------|--------|
| `cargo build --workspace` | Clean |
| `cargo clippy -p toadstool-cli -- -D warnings` | 0 warnings |
| `cargo test -p toadstool-cli` | All passed, 0 failures |
| `cargo fmt --check` | 0 diffs |
| `toadstool doctor` | Runs clean (was panic before) |

---

## Node Atomic Validation Status

- Tower sockets LIVE on strandGate (crypto, security, beardog, songbird, btsp)
- RTX 3090 detected via wgpu
- `toadstool doctor` confirms ecosystem connectivity
- **Blocked**: Full `node.compute` + `node.dispatch` validation blocked on
  glibc depot rebuild (sporeGate)
- **Pre-existing**: GPU concurrent test SIGSEGV (Mesa llvmpipe driver issue,
  same as barraCuda — not a regression)
