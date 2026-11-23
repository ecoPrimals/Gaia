# NestGate v0.5.0 — Session 85: Wave 73 ZFS Backend + Cross-Gate Federation + Mesh Registration

**Date**: Jun 3, 2026
**Session**: 85
**Wave**: 73
**Status**: Implementation complete, all tests passing

## What Was Delivered

### M1: Unified CAS Storage Base for ZFS (P2)

**Problem**: `storage_base_path()` was hardcoded to `{data_dir}/storage`. westGate's
76TB ZFS array couldn't be used as the CAS content root without symlinks.

**Solution**: `NESTGATE_STORAGE_BASE_PATH` env var now overrides the default. On westGate,
set this to the ZFS dataset mountpoint (e.g. `/tank/nestgate-cas`). All content handlers
(`content.put`, `content.get`, `content.exists`, `content.list`, manifests) automatically
route through the new base.

**Config**:
```bash
# westGate ZFS bootstrap
export NESTGATE_STORAGE_BASE_PATH=/tank/nestgate-cas
export NESTGATE_ZFS_CAS_DATASET=tank/nestgate-cas
```

### M2: `content.replicate.pull` — Cold-From-Hot Federation (P2)

**Problem**: `content.replicate` only pushed blobs from local to remote. Cold-storage
gates (westGate) need to pull from hot gates (eastGate).

**Solution**: New `content.replicate.pull` handler:
- Params: `{cids: ["<blake3>"], source: "<socket_or_tcp>", family_id?}`
- Diff-based: skips CIDs already present locally
- Uses `content.get` on remote → writes to local CAS tree
- Returns: `{pulled: [{cid, pulled, size?}], transferred_count, skipped_count, total_bytes}`

**Signal graph**: `rootpulse.federate` (pull direction)

### M3: Extended Announce + Mesh Route Registration (P3)

**`primal.announce` payload extended**:
- `gate_id`: from `NESTGATE_GATE_ID` → `NESTGATE_FAMILY_ID` → `"standalone"`
- `endpoints`: `{uds: "<path>", tcp?: "tcp://host:port"}`
- `federation_methods`: `["content.replicate", "content.replicate.pull", ...]`
- `storage_backend`: `{type: "zfs"|"filesystem", dataset?: "..."}` (ZFS when `NESTGATE_ZFS_CAS_DATASET` set)

**New `route.register` method**:
- Registers storage + content capabilities to local route manifest
- Configurable TTL (default 300s)
- Returns full gate identity and federation capability info
- BTSP-exempt (public method, like `discovery.capability.register`)

## Metrics

- 12,537+ tests passing, 0 failures, 0 clippy warnings
- 15 new tests (5 replicate.pull, 8 announce payload, 2 route.register)
- Files modified: 12 production, 7 test
- New method: `content.replicate.pull`, `route.register`
- New env vars: `NESTGATE_STORAGE_BASE_PATH`, `NESTGATE_GATE_ID`, `NESTGATE_ZFS_CAS_DATASET`

## Environment Variables Summary (Wave 73)

| Variable | Purpose | Default |
|----------|---------|---------|
| `NESTGATE_STORAGE_BASE_PATH` | Override CAS root (ZFS mount) | `{data_dir}/storage` |
| `NESTGATE_GATE_ID` | Gate identity for mesh routing | falls back to `NESTGATE_FAMILY_ID` / `"standalone"` |
| `NESTGATE_ZFS_CAS_DATASET` | ZFS dataset name (for announce payload) | unset (filesystem mode) |
| `NESTGATE_API_PORT` | TCP port (included in announce endpoints) | unset |

## Next Steps

- [ ] westGate onboarding: provision ZFS dataset, set env vars, validate CAS write/read
- [ ] Cross-gate integration test: eastGate push → westGate pull via TCP
- [ ] biomeOS route table consumption: biomeOS reads announce payloads for cross-gate routing
- [ ] Streaming transfer: replace base64-in-JSON with chunked stream for large blobs
- [ ] ZFS snapshot integration: periodic `zfs snapshot` of CAS dataset for point-in-time federation

## Coordination

- **cellMembrane**: westGate onboarding partner
- **sporePrint**: content cutover will use NestGate cross-gate federation
- **biomeOS**: route table authority — consumes `primal.announce` + `route.register`
