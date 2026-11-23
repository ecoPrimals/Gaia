# projectFOUNDATION — Wave 56 UDS-First Absorption

**Date**: 2026-05-27
**Commit**: `92a0a1d`
**primalSpring**: v0.9.30 (Wave 56 context)
**Pipeline**: 460 methods · 56 scenarios · 185 targets · 29 workloads

## What Changed

### Transport Layer — UDS-First with TCP Fallback

The bash deploy layer now mirrors the graph TOML's `transport = "uds_only"` intent:

**Before**: 6/7 primals health-checked via TCP/HTTP; only rhizoCrypt used UDS.
All `rpc_*` functions were TCP/HTTP primary.

**After**: All 7 primals try UDS first via `discover_socket()`. TCP/HTTP is
a fallback for desktop/dev environments.

| Primal | Before | After |
|--------|--------|-------|
| BearDog | HTTP POST | UDS → HTTP POST → TCP nc |
| Songbird | HTTP GET /health | UDS → HTTP GET /health |
| ToadStool | HTTP POST | UDS → HTTP POST → TCP nc |
| NestGate | TCP nc | UDS → TCP nc |
| rhizoCrypt | UDS only | UDS (shared helper) |
| loamSpine | HTTP POST | UDS → HTTP POST |
| sweetGrass | HTTP POST | UDS → HTTP POST |

### Discovery Config — `[sockets]` Section

`deploy/discovery_defaults.toml` restructured:

```toml
[metadata]
vps_standard = "uds_only"
transport_preference = "uds"

[sockets]
beardog    = "${XDG_RUNTIME_DIR}/ecoPrimals/beardog.sock"
nestgate   = "${XDG_RUNTIME_DIR}/ecoPrimals/nestgate.sock"
# ... all 8 primals

[bootstrap_tcp]
# Dev/desktop only — not used in VPS --uds-only mode
beardog    = 9100
# ... TCP ports as before
```

### Graph TOML — Cell Graph Alignment

`graphs/foundation_validation.toml`:
- `vps_standard = true` in `[graph.metadata]`
- `spawn = false` on all 13 primal nodes (overlay pattern, not spawner)
- Already had `transport = "uds_only"` — now enforced by bash layer

### New Functions in primal_ipc.sh

| Function | Purpose |
|----------|---------|
| `discover_socket()` | UDS-first resolution: env → discovery socket → config |
| `_rpc_uds()` | Generic UDS JSON-RPC call (replaces per-primal Python socket code) |
| `_resolve_config_value()` | Read any section/key from discovery_defaults.toml |
| `DISCOVERY_UDS_COUNT` | Tracks how many primals resolved via UDS transport |

### Elevation Review Updated

- Phase B description: Wave 56 VPS standard, `from_live_discovery()`, `--uds-only`
- API table: `{PRIMAL}_SOCKET` env convention, `from_live_discovery()` (not `_with_fallback`)
- Wave 56 VPS deployment standard section added

## Pipeline State

| Metric | Value |
|--------|-------|
| Transport | UDS-first, TCP fallback |
| Graph | All nodes `spawn=false`, `vps_standard=true` |
| Health checks | UDS-first for all 7 primals |
| RPC functions | UDS-first for all 4 rpc_* (nestgate, rhizocrypt, loamspine, sweetgrass) |
| TCP bootstrap | `[bootstrap_tcp]` section — dev/desktop only |

## Open Items

| ID | Item | Status |
|----|------|--------|
| FN-1 | BLAKE3 backfill threads 4, 5, 1 | Blocked on .data/ fetch |
| FN-5 | Rust elevation Phase B | Unblocked by Wave 56 |
| NC-1 | Thread 10 spore ingest | Code COMPLETE (v3.81) — gated on VPS deploy |

## Upstream Notes

- **primalSpring**: `discover_socket()` in bash mirrors `from_live_discovery()`.
  When Phase B Rust lands, the bash function becomes dead code.
- **All primals**: Verify UDS socket paths match
  `${XDG_RUNTIME_DIR}/ecoPrimals/{primal}.sock` convention in
  `discovery_defaults.toml [sockets]` section.
- **Songbird**: Still has HTTP-only `/health` endpoint (no JSON-RPC health).
  UDS discovery works for JSON-RPC health.liveness but Songbird's custom
  HTTP health doesn't route through UDS. Consider adding JSON-RPC health.
