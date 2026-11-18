# swarmVine — Wave 157i WINDOWS PORT POLISH

**Date**: August 11, 2026
**Wave**: 157i (Post-Pandemic Cascade)
**From**: eastGate overwatch
**Primal**: swarmVine (#16)
**Commit**: `e5cfacd`

---

## Summary

Windows port polish: eliminate all cross-compile warnings on
`x86_64-pc-windows-gnu` and `aarch64-apple-darwin`. The ecosystem blurb
listed "5 UDS call sites need `#[cfg(unix)]` + TCP fallback" — audit
confirmed all UDS call sites were already gated from Waves 157d-157f,
but 7 helper functions/imports/structs used only by the Unix codepaths
were not gated, producing dead-code warnings on non-Unix targets.

## Changes

### tarpc_server.rs (5 warnings fixed)
- `SwarmVineService` import → `#[cfg(unix)]`
- `warn` import → `#[cfg(unix)]`
- `tarpc_endpoint()` function → `#[cfg(unix)]`
- `SwarmVineServiceHandler` struct → `#[cfg(unix)]`
- `SwarmVineServiceHandler` impl → `#[cfg(unix)]`

### announce.rs (2 warnings fixed — 3 functions)
- `gossip_port()` → `#[cfg(unix)]`
- `cost_hints()` → `#[cfg(unix)]`
- `latency_estimates()` → `#[cfg(unix)]`

## Verification

| Target | Warnings | Tests |
|--------|----------|-------|
| `x86_64-unknown-linux-gnu` (native) | 0 | 137 PASS |
| `x86_64-pc-windows-gnu` | 0 (was 7) | N/A (cross-check) |
| `aarch64-apple-darwin` | 0 | N/A (cross-check) |

## Windows port status

All UDS call sites are gated:
- `tarpc_service.rs`: `connect()` — `#[cfg(unix)]` + `#[cfg(not(unix))]` stub
- `tarpc_server.rs`: `start_tarpc_listener()` — `#[cfg(unix)]` + stub
- `announce.rs`: `announce_to_biomeos()` — `#[cfg(unix)]` + no-op stub
- `announce.rs`: `register_with_songbird()` — `#[cfg(unix)]` + no-op stub
- `transport.rs`: `TransportStream::Unix` — `#[cfg(unix)]` throughout
- `platform_signal.rs`: Unix signals — `#[cfg(unix)]` + no-op stub
- `platform_substrate.rs`: `symlink`/permissions — `#[cfg(unix)]` + stubs

**swarmVine compiles warning-free on all 3 targets** (linux-gnu,
windows-gnu, apple-darwin). The Windows binary operates in TCP-only mode
with graceful `Unsupported` stubs for UDS/tarpc features.

---

*Windows port polish complete. 7 dead-code warnings eliminated. Zero
warnings on 3 targets. swarmVine compiles clean across the full
deployment matrix. Primal #16.*
