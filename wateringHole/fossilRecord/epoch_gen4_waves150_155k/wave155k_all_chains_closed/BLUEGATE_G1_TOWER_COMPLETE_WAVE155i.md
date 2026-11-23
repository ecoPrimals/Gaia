# blueGate G1 COMPLETE — Tower Atomic 3/3 on Windows

**Date**: Jul 29, 2026 17:12 EDT | **Wave**: 155i | **From**: blueGate
**Gate**: G1 Tower Atomic | **Status**: **COMPLETE** | **Platform**: Windows 10.0.26200

---

## TOWER ATOMIC — 3/3 PRIMALS HEALTHY

| Primal | Version | Transport | Port(s) | Health |
|--------|---------|-----------|---------|--------|
| **bearDog** | 0.9.0 | TCP | :9100 | `{"status":"alive"}` |
| **songBird** | 0.2.1 | HTTP + TCP IPC | :7700 (HTTP), :9901 (IPC) | `{"status":"healthy"}` |
| **skunkBat** | — | Process | — | RUNNING (6.7 MB) |

### JSON-RPC Health Responses

**bearDog** (TCP :9100):
```json
{"id":1,"jsonrpc":"2.0","result":{"primal":"beardog","status":"alive","version":"0.9.0"}}
```

**songBird** (TCP IPC :9901):
```json
{"jsonrpc":"2.0","result":{"primal":"songbird","services":0,"status":"healthy","uptime_s":26,"version":"0.2.1"},"id":1}
```

**songBird** (HTTP :7700/health):
```
Status: 200 OK
```

---

## HOW WE GOT HERE

### P0 Fix (8c0adc8d) — Not Sufficient Alone

The upstream P0 fix (`8c0adc8d`) fixed the primary `#[cfg(not(unix))]` platform gate in
`songbird-orchestrator/src/app/core/mod.rs` but the Windows depot binary (`x86_64-pc-windows-gnu`)
was **not rebuilt** — depot listing still shows `07/16/2026`. The P0 fix was only shipped in
Linux musl/glibc depot binaries.

### blueGate Built from Source

Since no Windows depot binary existed with the fix, blueGate built songBird from source
using the GNU toolchain (`stable-x86_64-pc-windows-gnu` via WinLibs GCC 16.1.0).

**3 additional compile errors** were discovered and fixed locally:

| # | File | Error | Fix |
|---|------|-------|-----|
| 1 | `songbird-universal-ipc/.../enrollment_crypto.rs:105` | `tokio::net::UnixStream` used unconditionally | Added `#[cfg(unix)]` / `#[cfg(not(unix))]` split with TCP fallback to `127.0.0.1:9100` |
| 2 | `songbird-orchestrator/.../core/mod.rs:498` | `songbird_universal_ipc::IpcServiceHandler` — missing re-export | Changed to `songbird_universal_ipc::service::IpcServiceHandler` |
| 3 | `songbird-orchestrator/.../server.rs:445` | `fn extract_unix_caller(stream: &tokio::net::UnixStream)` — Unix type in fn signature | Added `#[cfg(unix)]` gate on entire function |

### Additional Operational Issue

songBird's PID file path uses Unix convention (`/var/run/songbird/songbird.pid`), which
maps to `C:\var\run\songbird\songbird.pid` on Windows. After process kill, the PID file is
not cleaned up, causing "already running" errors on restart. Required manual cleanup.

---

## UPSTREAM ACTIONS NEEDED

### P1: Windows Depot Rebuild
sporeGate needs to cross-compile songBird for `x86_64-pc-windows-gnu` with commit `8c0adc8d`+
the 3 fixes below. The current Windows depot binary is from 07/16 (pre-P0-fix).

### P1: 3 Compile Fixes for Windows
These 3 fixes need to land in songBird main — they are compile errors on Windows that the
P0 fix missed:

1. **enrollment_crypto.rs** — `UnixStream` unconditional usage
2. **core/mod.rs** — `IpcServiceHandler` accessed via crate root (not re-exported)
3. **server.rs** — `extract_unix_caller` not gated behind `#[cfg(unix)]`

### P2: PID File Path
songBird writes PID files to `/var/run/songbird/` which becomes `C:\var\run\songbird\` on
Windows. Should use platform-appropriate paths (e.g., `%LOCALAPPDATA%\songbird\`).

### P2: PID File Cleanup
PID file not cleaned up on process kill/crash. Stale PID file blocks restart.

---

## RESOURCE PROFILE

| Resource | Value |
|----------|-------|
| bearDog memory | 12.8 MB |
| songBird memory | 15.0 MB |
| skunkBat memory | 6.7 MB |
| Total Tower footprint | ~34.5 MB |
| Build time (songBird) | 3m 56s (release, cold) |
| Build toolchain | stable-x86_64-pc-windows-gnu (Rust 1.97.1) |
| GCC | WinLibs MinGW-W64 GCC 16.1.0 |

---

## NEXT STEPS

1. **Nest Atomic** — deploy on blueGate (after Tower stable)
2. **Node Atomic** — deploy after Nest
3. **Sub-builder enrollment** — blueGate as Windows genomeBin builder under sporeGate
4. **Inner membrane topo owner H2** — blueGate assigned

---

*G1 Tower Atomic COMPLETE on Windows. First Windows Tower in the mesh.
3/3 primals healthy. songBird built from source with 3 local compile fixes.
blueGate ready for Nest Atomic.*
