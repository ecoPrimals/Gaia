# cellMembrane — Wave 157a Platform Abstraction Handoff

**Date**: 2026-08-08 | **From**: eastGate overwatch | **Wave**: 157a
**Commits**: `c546a27` (deep debt + docs), `9b0bc36` (platform abstraction)

---

## Summary

cellMembrane completed a deep platform abstraction pass, eliminating 15
`#[cfg(unix)]` blocks across 6 production files. All remaining cfg gates are
now confined to hub files (transport.rs, sync_ipc.rs, platform_substrate.rs,
jsonrpc.rs) or genuinely platform-specific bind points (webhook listener).

---

## Changes Delivered

### 1. Sync IPC Centralization (`sync_ipc.rs` — NEW)
- `ipc_send()`: fire-and-forget with BTSP negotiation + plain fallback
- `ipc_request()`: request/response with BTSP negotiation + plain fallback
- Replaces 7 duplicate UDS helper functions across impulse + signing
- Platform gate at connect point only (single `#[cfg(unix)]`)

### 2. BTSP Handshake Genericization
- `handshake_sync`: evolved from `&mut UnixStream` to `impl Read + Write`
- Uses `BufReader::get_mut()` for interleaved reads/writes (no `try_clone()`)
- cfg gate moved from handshake logic to connect point

### 3. Process Lifecycle in Platform Substrate
- `kill_process()` — SIGTERM (Unix) / taskkill (Windows)
- `force_kill_process()` — SIGKILL (Unix) / taskkill /F (Windows)
- `is_process_alive()` — /proc check (Unix) / tasklist (Windows)
- `detach_process_group()` — process_group(0) (Unix) / no-op (other)
- Replaces inline cfg blocks in nucleus.rs and graceful_kill

### 4. Webhook Handler Genericization
- `handle_connection` evolved to `AsyncRead + AsyncWrite + Unpin`
- cfg gate confined to `listen()` bind point only

### 5. Deep Debt Sweep
- `freshness.rs`: hardcoded `"/wateringHole"` → `INFRA_WATERING_HOLE` constant
- `harvest.rs`: extracted `atomic_copy_binaries()` helper (101→76 lines)
- `platform_substrate.rs`: added `# Errors` doc sections
- `cascade.rs`: `#[allow(struct_excessive_bools)]` on CascadeOpts

### 6. Spec Documentation Cleanup
- 5 spec documents updated: replaced all `deploy_membrane.sh` /
  `darkforest_membrane.sh` references with `membrane` CLI equivalents
- Files: FIELDMOUSE_CONTRACT.md, MULTI_MEMBRANE_DEPLOYMENT.md,
  MEMBRANE_COMPOSITION_MODEL.md, K_DERM_TOPOLOGY.md

---

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| Tests | 1319 | 1327 |
| cfg blocks (affected files) | 18 | 3 (bind points only) |
| Net lines | — | -150 |
| Clippy warnings | 0 | 0 |
| Files >800L | 0 | 0 |
| Production unwrap() | 0 | 0 |
| Unsafe code | 0 | 0 |

---

## Known Gaps / Upstream Notes

### For deployment team
- **NM hook naming drift**: `deploy/nm-dispatcher/99-mesh-reconnect` (full
  mesh.init with hardcoded VPS IP) vs bootstrap-generated `99-membrane-reconnect`
  (gate.status only). Recommend unifying name and behavior, removing hardcoded IP.

### For biomeOS team
- No action needed. `NeuralBridge::discover()` widened in prior commit.

### For toadStool team
- 4 `hw-safe` VFIO/DRM violations remaining (from blurb). Not cellMembrane work.

### For primalSpring team
- `capability_registry.toml` missing entries: `braid.list`, `braid.query`,
  `convergence.check`. Not blocking but needed for full registry coverage.

### Long-tail
- **Item 12**: `native_braid.py` → Rust — last Python in active pipeline.
  Owner: cellMembrane or sourDough.
- **Sandbox/canary systemd units** in `deploy/systemd/` are not referenced
  by Rust code (sandbox uses direct process management). Confirm if still
  needed on VPS or archive to fossilRecord.
