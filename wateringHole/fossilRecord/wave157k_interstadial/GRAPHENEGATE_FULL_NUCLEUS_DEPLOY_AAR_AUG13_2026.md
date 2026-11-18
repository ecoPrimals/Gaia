# grapheneGate Full NUCLEUS Deployment AAR — Aug 13, 2026

**Wave**: 157k CASCADE COMPLETE | **Gate**: grapheneGate (Pixel 8a) | **From**: eastGate overwatch

## Summary

Deployed 13/15 NUCLEUS primals to grapheneGate via ADB from eastGate.
All 15 primal binaries cross-compiled for `aarch64-unknown-linux-musl` on eastGate
and pushed to `/data/local/tmp/ecoPrimals/bin/`. Tower + Nest + Node + squirrel +
biomeOS all alive and responding to health checks over TCP-only transport.

**Previous state**: Tower Atomic (4/4 primals, stale binaries from Jun-Aug 10)
**New state**: 13/15 NUCLEUS alive (fresh binaries from current HEADs)

## Primal Status

| Primal | Status | Transport | Port | Notes |
|--------|--------|-----------|------|-------|
| beardog | ALIVE | abstract+TCP | 9100 | v0.9.0, `--abstract --port` |
| songbird | ALIVE | TCP IPC | 9200 | `server --listen 127.0.0.1:9200` |
| skunkbat | ALIVE | tcp_only | 9140 | `server --bind-mode tcp-only` |
| swarmvine | ALIVE | TCP | 7801 | `--disable-tarpc --transport-endpoint {tcp}` |
| nestgate | ALIVE | HTTP | 9300 | v0.5.0, `PRIMAL_BIND_MODE=tcp_only`, tarpc 8091 conflicted |
| rhizocrypt | ALIVE | TCP | 9400/9401 | v0.14.17, tarpc:9400, JSON-RPC:9401 |
| loamspine | ALIVE | TCP | 9500 | `--port 9500 --bind-address 127.0.0.1` |
| sweetgrass | ALIVE | TCP | 9850 | `--port 127.0.0.1:9850` |
| toadstool | ALIVE | riboCipher TCP | 9600 | Expects `0xEC 0x01` prefix |
| barracuda | ALIVE | tcp_only | 9700 | `--bind-mode tcp_only` |
| coralreef | ALIVE | TCP | 9750 | `server --port 9750` |
| squirrel | ALIVE | TCP | 9800 | v0.1.0, `--port 9800` |
| biomeos | RUNNING | HTTP | 9000 | Dark Forest 403 (no BTSP family seed) |
| petaltongue | FAILED | — | — | G65 negotiate UDS crash (upstream) |
| membrane | NOT STARTED | — | — | Deployment tool, not long-running |

## SELinux Observations (Android)

All primals must use TCP-only transport. UDS sockets are denied by SELinux
policy for the `shell` context on GrapheneOS. Specific workarounds per primal:

- **beardog**: `--abstract` for abstract namespace socket (SELinux-safe)
- **songbird**: `server --listen host:port` for TCP IPC
- **skunkbat**: `server --bind-mode tcp-only`
- **swarmvine**: `--disable-tarpc --transport-endpoint {"transport":"tcp","host":"...","port":N}`
- **nestgate**: `PRIMAL_BIND_MODE=tcp_only`
- **barracuda**: `server --bind-mode tcp_only`
- **biomeos**: Auto-detects SELinux, warns "running on TCP only"
- **petaltongue**: **NO tcp_only MODE** — crashes on G65 negotiate UDS bind

## Upstream Blockers (AAR for other teams)

| # | Issue | Owner | Severity |
|---|-------|-------|----------|
| 1 | petalTongue G65 negotiate UDS crash on Android | ironGate | P2 — blocks viz on mobile |
| 2 | biomeOS Dark Forest 403 without BTSP family seed | eastGate (biomeOS) | P3 — needs Android BTSP bootstrap |
| 3 | nestGate tarpc port 8091 conflict | westGate (nestGate) | P4 — non-fatal, JSON-RPC works |

## Binary Sizes (aarch64-unknown-linux-musl, statically linked)

| Binary | Size |
|--------|------|
| biomeos | 19M |
| songbird | 22M |
| petaltongue | 16M |
| membrane | 14M |
| sweetgrass | 11M |
| toadstool | 10M |
| nestgate | 7.3M |
| beardog | 6.7M |
| coralreef | 6.9M |
| rhizocrypt | 6.3M |
| barracuda | 4.5M |
| loamspine | 4.2M |
| squirrel | 3.4M |
| skunkbat | 2.8M |
| swarmvine | 2.3M |
| **TOTAL** | **~156M** |

## Cross-Compilation

All binaries built on eastGate (x86_64) targeting `aarch64-unknown-linux-musl`
using the Rust cross-compilation toolchain with `aarch64-linux-gnu-gcc` linker.
Build times ranged from 30s (swarmvine) to ~2.5min (nestgate, songbird).
All 15 binaries successfully compiled from current HEAD of each primal repo.

---
*FOSSILIZED Wave 157k interstadial (Aug 13, 2026). Content fully absorbed into ORTHOGONAL_DIMENSIONS_REVIEW.md and ECOSYSTEM_BLURB.md.*
