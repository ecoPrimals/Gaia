# blueGate G1 Post-Tower AAR — Wave 155i

**Date**: Jul 29, 2026 17:15 EDT | **Wave**: 155i | **From**: blueGate
**Scope**: Full G1 (Tower Atomic) retrospective — what the blurb envisioned vs. what
actually happened, remaining divergence, upstream actions needed.

---

## BLURB VISION vs. REALITY

### What the blurb envisioned for G1

> blueGate pull new songBird.exe from depot → Tower 3/3 → G1 COMPLETE

One step: download, run, done. Estimated time: minutes.

### What actually happened

| Step | Expected | Actual | Delta |
|------|----------|--------|-------|
| Pull songbird.exe from depot | Download fixed binary | Depot binary is from **07/16** — pre-P0-fix. Still exits with platform gate error. | **Depot not rebuilt for Windows** |
| Run songBird | Just works | 3 additional compile errors on Windows beyond the P0 fix | **Source build required** |
| Build from source | Not expected | Needed MinGW-w64 toolchain (WinLibs GCC 16.1.0). 3m 56s cold build. | **Toolchain gap** |
| Start Tower 3/3 | Start 3 processes | Stale PID file at `C:\var\run\songbird\` blocked restart. Manual cleanup. | **PID file bug** |
| Validate health | `tower.health → healthy` | bearDog: `alive`. songBird: `healthy`. skunkBat: `running`. | **SUCCESS** |

**Time to G1**: ~45 minutes instead of ~5 minutes. Root cause: the depot pipeline
only rebuilt Linux binaries, not Windows. blueGate became an ad-hoc sub-builder.

---

## REMAINING DIVERGENCE FROM BLURB

### 1. Windows Depot Stale (P1)

The entire `x86_64-pc-windows-gnu/` depot directory is from **07/16/2026**. All 14
binaries are pre-Wave-155i. The blurb says "sporeGate depot fully refreshed (19 binaries)"
but this only covers `x86_64-unknown-linux-musl` (16) and `x86_64-unknown-linux-gnu` (3).

**Impact**: Every Windows gate (blueGate, swiftGate, northGate) that tries to use depot
binaries gets pre-fix versions. swiftGate (next Windows proof) will hit the same wall.

**Fix**: sporeGate needs a Windows cross-compilation target in the depot pipeline.
blueGate can serve as the cross-build host (Rust 1.97.1 + GCC 16.1.0 now installed).

### 2. songBird 3 Additional Compile Errors (P1 — pushed upstream: d9bda555)

The P0 fix (`8c0adc8d`) fixed the primary `start_ipc_server` gate but missed 3 callsites
that use Unix-only types unconditionally:

| # | Location | Issue | Fix (pushed) |
|---|----------|-------|--------------|
| 1 | `enrollment_crypto.rs:105` | `tokio::net::UnixStream` used without `#[cfg(unix)]` | `#[cfg(unix)]`/`#[cfg(not(unix))]` split — TCP fallback to `127.0.0.1:9100` |
| 2 | `core/mod.rs:498` | `songbird_universal_ipc::IpcServiceHandler` — type not re-exported from crate root | Changed to `songbird_universal_ipc::service::IpcServiceHandler` |
| 3 | `server.rs:445` | `fn extract_unix_caller(stream: &tokio::net::UnixStream)` — Unix type in fn signature | Added `#[cfg(unix)]` gate on entire function |

**Status**: All 3 fixes pushed to songBird main (`d9bda555`). But:
- The depot binary still doesn't include them (see #1 above)
- The P0 fix was not tested on Windows before shipping — **no Windows CI gate exists**

### 3. songBird PID File Uses Unix Paths (P2)

PID file written to `/var/run/songbird/songbird.pid` which maps to `C:\var\run\songbird\`
on Windows. Two issues:
- Wrong path convention (should use `%LOCALAPPDATA%\songbird\` or similar)
- PID file not cleaned up on process kill → stale PID blocks restart

### 4. No Windows CI/Test Gate (P1 — systemic)

songBird (and likely other primals) have **zero Windows test coverage** in CI. The P0 fix
shipped without any Windows compilation check. All 3 additional errors would have been
caught by a `cargo check --target x86_64-pc-windows-gnu` CI step.

**Recommendation**: Add `x86_64-pc-windows-gnu` cross-check to CI for all primals.
Doesn't need Windows hardware — cross-compilation from Linux catches these compile errors.

### 5. songBird services: 0 (Expected: >0)

songBird reports `"services": 0` — no primals have registered with the IPC broker.
bearDog and skunkBat are running but haven't registered their capabilities with songBird.

This is likely because:
- bearDog's `auto` bind mode failed on UDS before falling back to TCP — the service
  registration path may only work via UDS
- skunkBat runs standalone without IPC registration
- The registration protocol may expect UDS, not TCP

**Impact**: `tower.mesh_status` and capability discovery won't reflect the full Tower
composition. Primals work independently but aren't orchestrated.

### 6. Blurb Claims "ZERO P0s" — Partially True

The blurb states "ZERO P0s" and the songBird P0 as "DONE". But:
- The P0 fix had 3 additional compile errors on Windows
- The Windows depot binary was never rebuilt
- blueGate had to build from source and patch code

The P0 is resolved in **source** but not in **deployment artifacts**. The fix is "done"
from eastGate's perspective (code merged) but not from blueGate's (binary not available).

---

## WHAT WORKED WELL

1. **Building from source**: Rust 1.97.1 + WinLibs GCC 16.1.0 produced a working binary
   in 3m 56s. blueGate can be a Windows sub-builder for the depot.

2. **TCP fallback is solid**: bearDog on TCP :9100, songBird IPC on TCP :9901 — both
   healthy. The TCP transport is a viable Windows path.

3. **songBird HTTP + IPC dual transport**: Both `:7700` (HTTP) and `:9901` (TCP IPC) are
   listening and responding. The P0 fix architecture (TCP IPC server) works.

4. **Tower memory footprint**: ~34.5 MB total (bearDog 13 MB, songBird 16 MB, skunkBat 7 MB).
   Lightweight for a Windows deployment.

5. **Upstream code fix loop**: blueGate → found 3 issues → fixed → pushed `d9bda555` → main
   updated. The closed-loop development workflow through SSH + Forgejo is working.

---

## OPEN ISSUES ROLLUP (blueGate)

| # | Priority | Issue | Owner | Status |
|---|----------|-------|-------|--------|
| 1 | P1 | Windows depot stale — all 14 binaries pre-155i | sporeGate | OPEN |
| 2 | P1 | songBird 3 compile fixes need Windows depot rebuild | sporeGate | Fixes pushed (`d9bda555`), depot rebuild needed |
| 3 | P1 | No Windows CI gate — compile errors slip through | eastGate / CI | OPEN |
| 4 | P2 | songBird PID file uses Unix paths on Windows | songBird | OPEN |
| 5 | P2 | songBird PID file not cleaned on kill | songBird | OPEN |
| 6 | P2 | songBird services: 0 — no primal registration via TCP | songBird/bearDog | OPEN — investigate registration over TCP |
| 7 | P2 | bearDog `auto` bind should prefer named pipes on Windows | bearDog | OPEN |
| 8 | P2 | bearDog health socket UDS-only — no TCP/pipe fallback | bearDog | OPEN |
| 9 | P2 | Virtual relay UDS-only bail on Windows | songBird | OPEN |
| 10 | P2 | primalSpring colon-in-filename (6 files) | primalSpring | **FIXED upstream** (`1cfee8c`) |
| 11 | P2 | Log management — primals log to void when backgrounded | ops | OPEN |
| 12 | P2 | Windows Service integration for primals | cellMembrane | OPEN |

### Resolved This Session

| Issue | Resolution |
|-------|------------|
| songBird P0 platform gate | Built from source with P0 fix + 3 local fixes |
| primalSpring colon filenames | **Fixed upstream** (`1cfee8c`) — absorbed in cascade |
| WireGuard tunnel activation | Elevated via `Start-Process -Verb RunAs` |
| SSH host key verification | `StrictHostKeyChecking=accept-new` |
| git-credential-manager blocking | `GCM_INTERACTIVE=never` |
| fossilRecord MAX_PATH | `core.longpaths=true` |

---

## TOOLCHAIN STATE (blueGate)

| Tool | Version | Notes |
|------|---------|-------|
| OS | Windows 10.0.26200 | Win32NT |
| Git | 2.55.0.3 | `core.longpaths=true` |
| Rust | 1.97.1 stable | MSVC default + GNU target added |
| GCC | WinLibs MinGW-W64 16.1.0 | Installed for songBird build |
| WireGuard | 1.1 | Tunnel active (10.13.37.12) |
| SSH | OpenSSH for Windows | Key: `id_ed25519_ecoPrimal` |

---

*blueGate G1 Tower Atomic COMPLETE but with significant divergence from the
blurb's single-step vision. Windows depot pipeline is the systemic gap —
blocks swiftGate (next Windows proof) and any future Windows gate. 3 compile
fixes pushed upstream. primalSpring filename fix absorbed. 12 open issues,
6 resolved this session. blueGate proceeding to Nest Atomic.*
