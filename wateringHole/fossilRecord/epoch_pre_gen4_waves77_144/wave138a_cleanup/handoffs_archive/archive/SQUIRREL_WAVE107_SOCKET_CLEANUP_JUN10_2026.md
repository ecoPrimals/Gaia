# Squirrel Wave 107 — PRIMAL-SOCKET-CLEANUP + Codebase Audit

**Date**: June 10, 2026
**From**: squirrel (eastGate)
**Wave**: 107
**FRAGO ref**: `impulses/active/2026-06-09T23-15_eastGate__wave106-cross-topology-validation.toml`

## Socket Cleanup — RESOLVED

**Violation**: `/tmp/ecoPrimals-manifests/squirrel.json` written at startup.

**Fix** (`d6857a8b`): `manifest_directory()` fallback chain no longer touches `/tmp`:

| Tier | Source | Path |
|------|--------|------|
| 1 | `BIOMEOS_SOCKET_DIR` | `$DIR/../ecoPrimals-manifests/` |
| 2 | `XDG_RUNTIME_DIR` | `$XDG/ecoPrimals/` |
| 3 | `XDG_DATA_HOME` | `$DATA/ecoPrimals/manifests/` |
| 4 | Default | `~/.local/share/ecoPrimals/manifests/` |

**Impact**: Unblocks `ProtectSystem=strict` systemd hardening. Eliminates stale
manifest debris in `/tmp` on gate restarts.

**Verified**: Manifest now lands at `/run/user/1000/ecoPrimals/squirrel.json` on eastGate.

## Codebase Audit Results (Wave 107)

| Metric | Value |
|--------|-------|
| Tests | 7,111 / 0 failures |
| Clippy | 0 warnings |
| TODO/FIXME/HACK in code | 0 |
| Unsafe code | 0 |
| Production mocks | 0 |
| Files >800L (production) | 0 (router.rs at 820L is cohesive, no split needed) |
| `/tmp` writes (production) | 0 (only Tier 5 dev-mode socket fallback reads /tmp for discovery) |
| Transport compliance | Full Phase 2 (TRANSPORT_ENDPOINT + connect_transport) |
| External C deps | 0 (pure Rust, rustix for syscalls) |
| Deprecated dead code | 0 (all removed) |
| cargo clean | 35.9 GiB reclaimed |

## Upstream Gaps for primalSpring

From Wave 107 blurb, remaining squirrel-adjacent action items (all external):

1. **cellMembrane depot rebuild** — squirrel binary in depot is stale (pre-Wave 100)
2. **biomeOS auto-register** — after primal starts, should fire `ipc.register` with songBird
3. **songBird ipc.resolve TransportEndpoint** — consumers (squirrel included) ready, waiting on provider

No further squirrel code changes needed. Standing by for Wave 108+.
