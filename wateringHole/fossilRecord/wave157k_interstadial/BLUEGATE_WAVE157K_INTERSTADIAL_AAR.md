# blueGate Wave 157k — Interstadial Enmeshment Status

**Date**: Aug 13, 2026 | **Wave**: 157k (interstadial) | **Gate**: blueGate (10.13.37.12 / 192.168.4.212)
**Role**: Windows builder (ENMESHED) | **Status**: **NUCLEUS 13/13. 3 BUILDS SUCCEEDED. ENMESHMENT LIVE.**

---

## Summary

blueGate cascaded 10 repo updates, rebuilt 3 primals from HEAD, and validated enmeshment. songBird deep-debt build SUCCEEDED (P2 #6 fix worked). swarmVine FIRST SUCCESSFUL WINDOWS BUILD. membrane rebuilt with enmeshment + content.braid. builder.serve alive on `:9800` with riboCipher framing, LAN reachable. Ready for sporeGate autonomous dispatch.

---

## Builds — All 3 Succeeded

| Binary | Commit | Size | Notes |
|--------|--------|------|-------|
| songbird.exe | `b8c22577` (deep-debt, --node-id, content.locate, P2 #6) | 17.3MB | Bypassed rust-toolchain.toml (see below) |
| swarmvine.exe | `0e4cb75` (riboCipher framing, G65 default, Windows UDS fix) | 2.1MB | **FIRST WINDOWS BUILD** |
| membrane.exe | `c1b9de1` (enmeshment TCP fallback + content.braid) | 8.1MB | builder.serve with riboCipher signal handling |

### songBird Build Workaround

The `rust-toolchain.toml` now includes `x86_64-pc-windows-msvc` target (the one-line fix from our previous AAR was applied). However, building with 1.94.0 on this machine fails because **MSVC Build Tools (`link.exe`) are not installed**. blueGate uses the GNU toolchain.

**Workaround**: Rename `rust-toolchain.toml` → build with system 1.97.1 → restore. The P2 #6 API compatibility fix ensures the code compiles on both 1.94.0 and 1.97.1.

**Recommendation**: Either:
- Add `x86_64-pc-windows-gnu` as PRIMARY Windows target (matches depot naming convention)
- Or document that Windows builders need MSVC Build Tools installed
- Or add a `.cargo/config.toml` override for Windows: `[build] target = "x86_64-pc-windows-gnu"`

### swarmVine — First Windows Build

The `0e4cb75` commit gates `test_support` + integration UDS imports behind `#[cfg(unix)]`, enabling the first clean Windows build. swarmVine is now the 16th primal in the Windows depot.

---

## Enmeshment Validation

### TCP Dispatch (Stadial #1)

| Endpoint | Port | Localhost | LAN (.212) | WireGuard (.12) |
|----------|------|-----------|------------|-----------------|
| songBird | 7700 | OPEN | OPEN | OPEN |
| builder.serve | 9800 | OPEN | OPEN | OPEN |

builder.serve accepts riboCipher-framed TCP (`[0xEC, 0x01]` prefix). sporeGate can dispatch `call_tcp(192.168.4.212:9800, plasmid.harvest)` directly — no SSH needed.

### plasmid.staleness

```
0/13 current, 13 stale
```

All 13 depot binaries are stale vs source HEAD (depot from Aug 1-3, sources from Aug 12-13). Depot rebuild is sporeGate's responsibility — blueGate will execute when dispatched.

### gate.status — DEGRADED (known Windows issues)

| Check | Status | Root Cause |
|-------|--------|------------|
| depot.integrity | DEGRADED | checksums.toml parse error |
| mesh.reachability | DEGRADED | Mesh relay socket not found (UDS) |
| primals.alive | DEGRADED 0/3 | Health probes use UDS — primals alive but unreachable via UDS on Windows |
| sovereignty.s4_auth | DEGRADED | bearDog not responding on UDS |
| sovereignty.s1_tls | OK | depot.primals.eco 200 (277ms) |
| sovereignty.s2_relay | OK | Federation reachable, RustDesk OK |
| sovereignty.s3_content | OK | Depot serving 7703KB (276ms) |

**Root cause**: `membrane gate.status` health probes use Unix Domain Sockets for primal liveness checks. Windows primals are alive (13/13 via process check) but not reachable via UDS. This is the same platform gap as the swarmVine UDS issue — membrane's health probe needs TCP fallback.

**Action for cellMembrane team (sporeGate)**: Add TCP fallback to `primals.alive` and `sovereignty.s4_auth` health probes. Same pattern as `builder.serve` TCP dispatch.

---

## Current State

- NUCLEUS: **13/13** alive (process-verified)
- songBird: **b8c22577** (deep-debt sweep) with `--node-id blueGate`, bound `0.0.0.0:7700`
- swarmVine: **0e4cb75** first Windows binary, installed
- membrane: **c1b9de1** with enmeshment + content.braid
- builder.serve: **ALIVE :9800** — riboCipher TCP dispatch ready
- dnsproxy: **ALIVE** (G29 Phase 2 DNS secondary)
- WireGuard: 5/7 peers reachable (biomeGate DOWN expected)
- Depot: STALE (0/13 current) — awaiting sporeGate dispatch

---

## Remaining Windows Divergences

| # | Issue | Severity | Owner |
|---|-------|----------|-------|
| 1 | `rust-toolchain.toml` forces MSVC linker — GNU workaround needed | P2 | songBird team (ironGate) |
| 2 | `membrane gate.status` health probes use UDS — false DEGRADED | P2 | cellMembrane team (sporeGate) |
| 3 | No systemd — builder.serve needs scheduled task for reboot persistence | P3 | blueGate ops |
| 4 | `content.braid` needs Neural API — biomeOS RPC not reachable via UDS | P3 | cellMembrane team |
| 5 | Stale PID file cleanup on restart (canonical path: `C:\ProgramData\songbird\`) | P3 | songBird team |

---

*blueGate 157k interstadial: ENMESHED. 3 builds succeeded (songBird deep-debt, swarmVine FIRST, membrane enmesh). builder.serve ALIVE :9800 with riboCipher. NUCLEUS 13/13. Depot 0/13 current — awaiting sporeGate autonomous dispatch. 5 Windows divergences documented.*

---
*FOSSILIZED Wave 157k interstadial (Aug 13, 2026). Content fully absorbed into ORTHOGONAL_DIMENSIONS_REVIEW.md and ECOSYSTEM_BLURB.md.*
