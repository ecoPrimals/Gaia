> **FOSSILIZED** — Both P2s CLOSED: songBird Windows (`b8c225775`), swarmVine Windows (`0e4cb75`). Content absorbed into ortho review. 0/0/0 posture.

# blueGate Wave 157k — Ortho Sweep Status

**Date**: Aug 12, 2026 | **Wave**: 157k (ortho sweep) | **Gate**: blueGate (10.13.37.12 / 192.168.4.212)
**Role**: Windows builder (builds all 13, no code teams)
**Status**: **NUCLEUS 13/13. DEPOT STALE. 2 BUILD FAILURES LOGGED.**

---

## Summary

blueGate cascaded 6 repo updates (songBird deep-debt, swarmVine riboCipher, biomeOS restart-detect). Depot remains STALE (Aug 1-3 binaries) — sporeGate owns the rebuild. Attempted to rebuild songBird and swarmVine from new HEAD: **both failed on Windows** with distinct root causes. NUCLEUS 13/13 alive running MeshRelay songBird from `9351230d`. Blocker #1 from previous blurb (`.210:7700` timeout) remains RESOLVED.

---

## Build Failures — Upstream Action Needed

### songBird HEAD (090e8c2d) — FAILED

**Attempt 1** (with `rust-toolchain.toml` 1.94.0):
```
error: could not compile `windows_x86_64_msvc` (build script)
error: could not compile `portable-atomic` (build script)
error: could not compile `zerocopy` (build script)
```
Root cause: `rust-toolchain.toml` specifies targets for Linux/macOS/iOS but NOT `x86_64-pc-windows-msvc`. Build scripts can't compile for Windows under this toolchain.

**Attempt 2** (system toolchain 1.97.1, bypassing `rust-toolchain.toml`):
```
error[E0599]: songbird-orchestrator - `handle` method not in scope
help: use songbird_universal_ipc::tower_atomic::JsonRpcHandler
```
Root cause: API incompatibility between 1.94.0 (code targets) and 1.97.1 (system). The deep-debt sweep code compiles on 1.94.0 but uses patterns that break on newer Rust.

**Action for songBird team (ironGate)**: Add `x86_64-pc-windows-msvc` to `rust-toolchain.toml` targets. This is a one-line fix that unblocks native Windows builds.

### swarmVine HEAD (63c8ccc) — FAILED

```
error[E0433]: tokio::net::UnixStream - the item is gated behind #[cfg(unix)]
```
Root cause: Same as previous waves — `swarmvine-server` directly uses `tokio::net::UnixStream` without platform guards. The riboCipher framing and G65 default updates did not address the 5 UDS call sites.

**Action for swarmVine team (ironGate)**: Apply `#[cfg(unix)]` guards + TCP fallback to 5 UDS call sites. Pattern documented in swarmVine `CONVENTIONS.md` ("Windows: All UDS call sites use `transport.rs` abstraction or `#[cfg(unix)]` gating").

---

## Current State

### NUCLEUS Health

13/13 alive. songBird running MeshRelay build from `9351230d` (pre-deep-debt but with MeshRelay). All other primals from depot (pre-G72).

| Binary | Source | Status |
|--------|--------|--------|
| songBird | **Local build 9351230d** (MeshRelay, 17.2MB LTO) | ALIVE :7700 (0.0.0.0) |
| 12 others | Depot (Aug 1-3, pre-G72) | ALIVE |
| builder.serve | Depot membrane | ALIVE :9800 |
| dnsproxy | System | ALIVE |

### Blocker #1 Resolution (from 157k blurb)

Both root causes fixed in prior session:
- Topology IP: `192.168.4.210` → `192.168.4.212` (committed `e6a8fc0b`)
- songBird bind: `127.0.0.1` → `0.0.0.0` (LAN + WG reachable)

### Depot Push Readiness

Reviewed `BLUEGATE_DEPOT_PUSH_GUIDE.md`. All infrastructure ready:
- golgi SSH: CONNECTED (verified)
- membrane.exe: installed with `plasmid.harvest` support
- `plasmid.harvest --local --push` workflow: documented and dry-run tested
- BLAKE3 integrity: `depot.integrity --generate` available

**Blocked by**: Need depot binaries to push. Can't build songBird HEAD or swarmVine from source due to above failures. Can push our working MeshRelay songBird (9351230d) once sporeGate confirms it's acceptable.

---

## Depot Status — STALE

Per blurb, 4 primals have fixes not in depot:

| Primal | Fix | Can blueGate Build? |
|--------|-----|---------------------|
| songBird | deep-debt, --node-id, content.locate | **NO** — rust-toolchain.toml missing Windows target |
| swarmVine | riboCipher, gossip.relay, G65 | **NO** — UDS call sites not ported |
| toadStool | vulkan-portability (already correct) | Not attempted (depot binary likely fine) |
| biomeOS | rapid-restart detection | Not attempted |

---

## Recommendations

1. **songBird team**: Add `"x86_64-pc-windows-msvc"` to `rust-toolchain.toml` targets. One-line fix enables native Windows builds.
2. **swarmVine team**: Apply TCP fallback to 5 UDS call sites per CONVENTIONS.md pattern.
3. **sporeGate**: Depot rebuild from HEAD — blueGate will pull immediately once available.
4. **blueGate can push** MeshRelay songBird (9351230d, 17.2MB) to golgi depot as interim Windows binary if sporeGate approves.

---

*blueGate 157k ortho: NUCLEUS 13/13. Depot STALE. 2 build failures (songBird toolchain, swarmVine UDS). MeshRelay operational. Blocker #1 RESOLVED. Push infrastructure ready. Waiting on depot rebuild + upstream fixes.*
