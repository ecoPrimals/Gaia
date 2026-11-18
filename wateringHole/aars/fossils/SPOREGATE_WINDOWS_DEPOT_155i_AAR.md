# sporeGate AAR — Windows Depot Rebuild (Wave 155i NUCLEUS)

**Date**: Jul 29, 2026 | **Gate**: sporeGate | **Wave**: 155i-nucleus
**Scope**: P1 Windows depot rebuild, songBird d9bda555 pull, code team platform-gating flags

---

## Summary

Rebuilt Windows depot (14 `.exe`) for NUCLEUS convergence wave. 11/14 primals
cross-compiled successfully from Wave 155i deep-debt commits using `x86_64-pc-windows-gnu`
target. 3 primals blocked by code team platform-gating bugs. Depot pushed to golgiBody
with BLAKE3 checksums (33 total across musl + gnu + windows).

## Completed

| # | Item | Status |
|---|------|--------|
| 1 | Pull songBird to `d9bda555` (3 Windows compile fixes) | DONE |
| 2 | Cross-compile 11 primals for `x86_64-pc-windows-gnu` | DONE |
| 3 | Push 14 `.exe` to golgiBody depot | DONE |
| 4 | Regenerate BLAKE3 checksums (33 binaries: 16 musl + 3 gnu + 14 windows) | DONE |
| 5 | Verify Caddy serves Windows depot (HTTP 200) | DONE |
| 6 | Update sporeGate head document | DONE |

## Windows Build Results

### Successfully rebuilt (11/14)
| Binary | Size | Source |
|--------|------|--------|
| songbird.exe | 21.3 MB | d9bda555 — 3 Windows compile fixes |
| biomeos.exe | 19.9 MB | 8cee1ad — v4.45 composition broker |
| skunkbat.exe | 2.7 MB | b0df971 |
| nestgate.exe | 8.5 MB | 6b6d484 — 13K+ tests, CAS |
| sweetgrass.exe | 15.9 MB | ab887e8 — v0.8.0 G3 E2E |
| rhizocrypt.exe | 6.0 MB | d4972b0 |
| loamspine.exe | 4.3 MB | d79231a |
| barracuda.exe | 5.2 MB | 3460368 — FHE bit-perfect |
| petaltongue.exe | 26.2 MB | f61c808 |
| sourdough.exe | 2.9 MB | 3a0b52d |
| squirrel.exe | 3.8 MB | a9493a8 |

### Blocked by code team (3/14) — stale `.exe` from prior build
| Binary | Error | Root Cause |
|--------|-------|------------|
| beardog.exe | `UnixStream` not found | Missing `#[cfg(unix)]` gate |
| toadstool.exe | `toadstool_runtime_gpu` not found | GPU module not available for Windows target |
| coralreef.exe | `unix_jsonrpc` imports unresolved | Unix socket imports not platform-gated |

### Also blocked (not in depot)
| Binary | Error | Root Cause |
|--------|-------|------------|
| membrane.exe | `UnixStream` + `handshake_async` | Missing `#[cfg(unix)]` gate in membrane-shadow |

## Ownership Boundaries

**sporeGate owns**: depot infrastructure, cross-compilation, binary distribution, checksums
**Code teams own**: platform-gating (`#[cfg(unix)]`) for bearDog, toadStool, coralReef, cellMembrane

The blurb's Chain 3 item 2 ("Windows CI gate — `cargo check --target x86_64-pc-windows-gnu`")
would catch these at PR time. Recommend eastGate/CI implement this gate.

## Depot State After This AAR

| Target | Binaries | Status |
|--------|----------|--------|
| `x86_64-unknown-linux-musl` | 16 | FRESH (Wave 155i) |
| `x86_64-unknown-linux-gnu` | 3 | FRESH (Wave 155i) |
| `x86_64-pc-windows-gnu` | 14 | 11 FRESH / 3 STALE (code team blocks) |

Total: 33 binaries, BLAKE3 verified, served via `depot.primals.eco`.

---

*sporeGate — Windows depot P1 resolved. 11/14 rebuilt. 3 blocked by platform gating (code team).
Recommend Windows CI gate to prevent regressions.*
