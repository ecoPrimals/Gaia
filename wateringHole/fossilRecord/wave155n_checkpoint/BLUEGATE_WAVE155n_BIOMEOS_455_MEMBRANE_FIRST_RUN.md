# blueGate Wave 155n — biomeOS v4.55 + membrane.exe First Run

**Date**: Jul 31, 2026 12:50 EDT | **Wave**: 155n | **Gate**: blueGate (Windows)
**From**: blueGate overwatch | **Validates**: biomeOS v4.55 deploy, membrane.exe Windows debut

---

## Summary

Cascaded 9 repos from Forgejo. Deployed biomeOS v4.55.0 (coevolution build) from
fresh depot (rebuilt today). Downloaded membrane.exe (first-ever Windows depot build).
13/13 NUCLEUS running. membrane.exe runs on Windows but has a P2 platform detection
gap: all local probes use Linux assumptions (UDS, musl paths).

---

## Cascade (Wave 155n)

9 repos updated, 31 already current:

| Repo | Commit | What |
|------|--------|------|
| biomeOS | `34d4ef76` | Mode gap fix (652cf8a7) |
| cellMembrane | `111c7d2` | Registry API — collapse expect() calls |
| squirrel | `4bcf79ed` | Deep debt: handoffs, stale specs, cargo clean |
| petalTongue | `b135400` | Modern idiom pass, debris audit |
| bearDog | `5e80b5364` | Root docs sync — tests, methods, seed precedence |
| toadStool | `92aeb1441` | Docs refresh — dep elimination, sporeprint |
| wateringHole | `1f76f8cf` | Wave 155n checkpoint: orthogonal + glacial + fossilization |
| whitePaper | `a95fd30` | sporePrint live science strategy |
| sporePrint | broken branch | Persistent — needs re-clone |

---

## Depot Updates

| Binary | Depot Date | Size | Local Status |
|--------|-----------|------|-------------|
| **biomeOS** | **Jul 31 15:11 UTC** | **19.2 MB** | **UPDATED → v4.55.0** |
| **membrane** | **Jul 31 14:59 UTC** | **19.1 MB** | **NEW (first Windows build)** |
| squirrel | Jul 31 12:02 UTC | 3.6 MB | Refreshed (same version) |
| petalTongue | Jul 31 12:02 UTC | 25 MB | Refreshed (same version) |
| All others | Jul 29-30 | — | Unchanged from Wave 155k |

---

## biomeOS v4.55.0 — First Deploy on Windows

```
$ biomeos.exe --version
biomeos 4.55.0
```

Previous depot version was `0.1.0` — now reports actual workspace version.
This is the coevolution build with:
- `composition.test_swap` — hot-swap binary validation
- Dual-protocol health ping (plain JSON-RPC first, BTSP fallback) — P1 FIX
- Socket ownership guard (PID ownership + confirmed kill before unlink) — P1 FIX
- 5 P3 fixes: zombie reaping, graphs_dir default, riboCipher demoted to debug, version reporting

**Deployment**: API mode on :9206, HTTP /health returns 200, all /api/v1/* endpoints
return 403 (BTSP auth enforced — correct behavior).

---

## membrane.exe — First Windows Run

### What Works

| Probe | Status | Evidence |
|-------|--------|----------|
| Identity resolution | **OK** | `blueGate (via Environment)` |
| sovereignty.s1_tls | **OK** | `depot.primals.eco 200 (220ms)` |
| sovereignty.s2_relay | **OK** | `federation:REACHABLE, RustDesk:hbbs=OK,hbbr=OK` |
| sovereignty.s3_content | **OK** | `depot serving 8459KB (212ms TTFB)` |
| CLI help/subcommands | **OK** | All 50+ domain.operation commands parse correctly |
| `--version` | **OK** | `membrane 0.1.0 (0d39075)` |

### What Doesn't Work (P2: Platform Detection)

| Probe | Expected | Actual | Root Cause |
|-------|----------|--------|------------|
| Architecture | `x86_64-pc-windows-gnu` | `x86_64-unknown-linux-musl` | Compile-time target triple from cross-build environment |
| primals.alive | 13/13 via TCP | 0/13 (probes UDS sockets) | IPC transport hardcoded to UDS |
| depot.freshness | Windows depot path | Linux path `/tmp/.local/share/...` | Path construction uses Unix conventions |
| sovereignty.s4_auth | bearDog on TCP :9100 | UDS probe fails | Socket discovery uses Unix paths |
| tower.status | 3/3 via TCP | 0/3 DOWN | Same UDS probe issue |
| mesh.reachability | TCP probe or skip | UDS socket check | Unix socket path expected |

### Root Cause Analysis

membrane.exe was cross-compiled for `x86_64-pc-windows-gnu` by sporeGate, but the
binary embeds `x86_64-unknown-linux-musl` as the target triple (likely from the build
host's `cfg!(target_arch)` or a hardcoded constant). This causes all runtime platform
decisions to follow Linux code paths.

**Fix needed in cellMembrane**:
1. Use `#[cfg(target_os = "windows")]` for IPC transport selection (TCP, not UDS)
2. Use `#[cfg(target_os = "windows")]` for depot/socket path construction
3. Ensure compile-time target triple matches the actual cross-compile target
4. Or: detect OS at runtime via `std::env::consts::OS` and `std::env::consts::ARCH`

---

## NUCLEUS Stack Health

```
13/13 RUNNING | biomeOS v4.55.0 | 171.7 MB total

Tower:  bearDog v0.9.0 ✓   songBird v0.2.1 ✓   skunkBat v0.2.18 ✓
Nest:   nestGate v0.5.0 ✓   loamSpine v0.9.16 ✓   rhizoCrypt v0.14.17 ✓
        sweetGrass v0.8.0 ✓   petalTongue v1.7.0 ✓   squirrel v0.1.0 ✓
Node:   toadStool v0.2.0 ✓   barraCuda v0.4.0 ✓   coralReef v0.2.0 ✓
Orch:   biomeOS v4.55.0 ✓ (BTSP-gated API)

toadStool riboCipher: ENFORCED (responds with [0xEC, 0x01] framing)
biomeOS API: 403 on /composition, /version (BTSP auth — correct)
```

---

## J12 Sub-Builder Readiness Assessment

| Requirement | Status | Blocker |
|-------------|--------|---------|
| membrane.exe on Windows | **RUNS** | Platform detection P2 |
| membrane.exe plasmid.harvest | **BLOCKED** | Needs Windows target triple detection |
| membrane.exe plasmid.build | **BLOCKED** | Same — builds for musl, not windows-gnu |
| songBird IPC registry | **READY** | Proven in Wave 155k (10 primals, 38 caps) |
| songBird mesh federation | **NOT INIT** | Needs SONGBIRD_PEERS or WireGuard |
| sporeGate→blueGate IPC | **BLOCKED** | Needs mesh federation for cross-gate dispatch |
| Rust toolchain on blueGate | **READY** | MinGW-w64 + stable-x86_64-pc-windows-gnu |

**Conclusion**: J12 requires two fixes:
1. membrane.exe platform detection (cellMembrane team, P2)
2. songBird mesh federation (WireGuard tunnel or SSH relay)

Once membrane detects Windows correctly, `plasmid.harvest` can build locally and
`plasmid.push` can stage to the Windows depot. sporeGate can then dispatch builds
via songBird IPC once mesh is connected.

---

## Issues for Upstream

### P2: membrane.exe platform detection (NEW)

membrane.exe embeds `x86_64-unknown-linux-musl` as target triple on Windows.
All local probes (primals.alive, depot, socket, tower) fail because they use
Linux code paths. Sovereignty probes (TLS, relay, content) work because they
use HTTP, which is platform-independent.

**Owner**: cellMembrane
**Fix**: Runtime platform detection or correct compile-time target triple embedding.
**Impact**: J12 sub-builder blocked until this is resolved.

### P3: songBird stale PID file (persistent)

songBird still creates PID files at `C:\var\run\songbird\songbird-blueGate.pid`
and fails to clean them on shutdown. Manual cleanup required between restarts.

**Workaround**: Delete PID file before restart.
**Fix needed**: songBird should check PID liveness, not just file existence.

### P3: sporePrint broken branch (persistent)

`infra/sporePrint` has a broken HEAD since Wave 155i. Non-blocking but accumulates
cascade noise.

**Fix**: Re-clone on blueGate.

---

## blueGate Status

```
Gate:        blueGate
Platform:    Windows 10 (x86_64-pc-windows-gnu)
Wave:        155n
Primals:     13/13 RUNNING
biomeOS:     v4.55.0 (coevolution build, both P1s fixed)
membrane:    0.1.0 (0d39075) — FIRST WINDOWS RUN
Memory:      171.7 MB
Repos:       40 synced (9 updated this cascade)
Transport:   TCP-only
Provenance:  7/7 VALIDATED (Wave 155k — still valid)
J12:         BLOCKED on membrane platform detection + mesh federation
```

---

*Wave 155n — biomeOS v4.55.0 deployed on blueGate. membrane.exe first Windows run:
networking probes pass (TLS, relay, content), local probes fail (platform detection P2).
13/13 NUCLEUS stable. J12 sub-builder blocked on two items: membrane Windows target
triple + songBird mesh federation. Both P1 fixes confirmed present in depot build.*
