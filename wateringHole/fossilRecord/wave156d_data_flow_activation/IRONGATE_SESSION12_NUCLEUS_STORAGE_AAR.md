# ironGate Session 12 — NUCLEUS Storage + westGate Federation AAR

**Date**: 2026-08-05
**Wave**: 156d
**Gate**: ironGate (GPU compute, esotericWebb host)
**Operator**: ironGate hardware team

## Summary

Implemented the ironGate NUCLEUS Storage + westGate Federation plan. Mounted the 12.7 TB `nestgate-ext4` disk, started nestGate as part of the NUCLEUS composition, validated CAS write/read roundtrips through both footPrint and esotericWebb signal paths, and configured songBird federation for westGate data access.

## Results

### Phase 1: Mount + Wire nestGate (Infrastructure) — COMPLETE

- **Disk**: `/dev/sdc1` (12.7 TB ext4, label `nestgate-ext4`) mounted at `/mnt/nestgate`
- **fstab**: Added `/dev/sdc1  /mnt/nestgate  ext4  defaults,noatime  0  2`
- **CAS dirs**: `/mnt/nestgate/cas/datasets/` created, owned by `irongate:irongate`
- **Storage symlink**: `~/.local/share/nestgate/storage -> /mnt/nestgate/cas` (all CAS data lands on the big disk)
- **nestGate env**: `~/.config/nestgate/env` — family `9b32f3a8`, filesystem backend, 10 TB quota
- **nestGate**: v0.5.0 running, sockets at:
  - `/run/user/1000/biomeos/nestgate-9b32f3a8.sock` (UDS, BTSP-gated)
  - `/run/user/1000/biomeos/storage-9b32f3a8.sock` (capability symlink)
  - `TCP 127.0.0.1:8080` (SO_PEERCRED local-trust, no BTSP required)
- **Squirrel registration**: nestGate registered as both UDS and TCP provider (11 capabilities each)
- **Membrane symlinks**: nestGate sockets symlinked to `/run/user/1000/membrane/` for `biomeos doctor` visibility

### Phase 2: Wire Consumers — COMPLETE

- **footPrint**: 16/16 neural-api tests pass. E2E `content.put` → `content.get` roundtrip confirmed via TCP local-trust. footPrint's `createNeuralApiClient()` defaults to `TCP localhost:8080` — zero config needed.
- **esotericWebb**: `nest.store` signal decomposition validated:
  - `content.put` → nestGate stores blob (hash confirmed)
  - `dag.session.create` → rhizoCrypt creates session
  - `dag.event.append` (DataCreate) → rhizoCrypt records provenance vertex with content hash
  - exp006_live_composition: 19 passed, 0 failed, 3 skipped
- **Auth model**: TCP local-trust (SO_PEERCRED) bypasses BTSP for same-gate services. UDS requires BTSP via bearDog. This is the correct production security boundary.

### Phase 3: westGate Federation — CONFIGURED (BLOCKED on westGate)

- **songBird**: v0.2.1, restarted with `SONGBIRD_PEERS=westgate@192.168.4.149:7700`
- **Mesh**: 1 reachable peer (westGate) via direct LAN path
- **Federation**: Enabled, 1 active connection
- **Persistent config**: `~/.config/songbird/peers.toml` written
- **`content.replicate.pull`**: Code path validated (CID format checking works). Connection to westGate's nestGate TCP blocked — westGate hardware team needs to expose `nestgate` on TCP.
- **`capability.call` routing**: songBird attempts cross-mesh routing but no provider found on westGate for `content` capability. Expected — westGate needs to register its nestGate.
- **WireGuard**: `wg0` interface UP on ironGate, `10.13.37.4` (westGate mesh) unreachable. westGate hardware team blocker.

### Phase 4: Validate + Cell Graph Update — COMPLETE

- **`biomeos doctor`**: 4/4 healthy primals (biomeos-api, neural-api, nestgate-9b32f3a8, storage-9b32f3a8)
- **CAS roundtrip**: JSON object stored and retrieved with BLAKE3 hash verification
- **Cell graphs**: Both `esotericwebb_cell.toml` and `footprint_cell.toml` already contain `verify_nestgate` preflight checks. Copied to `~/graphs/` for runtime access.
- **Squirrel providers**: 9 total (rhizocrypt, toadstool, loamspine, nestgate, nestgate-tcp, petaltongue, beardog, songbird, sweetgrass)

## CAS Disk Usage

```
/mnt/nestgate/cas: 24M (freshly initialized + test objects)
Disk total: 12.7 TB (12 TB available)
Families: 9b32f3a8 (irongate-sovereign)
Content objects: 4+ BLAKE3-addressed blobs
Migrated data: 4011 files from previous XDG storage
```

## Blockers for Full Federation

| Blocker | Impact | Owner |
|---------|--------|-------|
| westGate nestGate TCP not exposed | Cannot `content.replicate.pull` | westGate hardware team |
| westGate songBird content capability not registered | `capability.call` routing fails | westGate hardware team |
| WireGuard mesh unreachable to westGate | No overlay path for federation | westGate hardware team |

## What's Proven

1. **ironGate has a live, 12.7 TB CAS** backing both esotericWebb and footPrint
2. **TCP local-trust (SO_PEERCRED)** is the correct auth model for same-gate services
3. **Full signal decomposition** fires: content.put → dag.event.append → provenance tracking
4. **songBird federation** is configured and connects to westGate via LAN
5. **Cell graphs** already include nestGate preflight verification
6. **9 primal providers** registered with squirrel for full G18 dispatch

## Files Changed

- `/etc/fstab` — Added sdc1 mount
- `~/.config/nestgate/env` — Created
- `~/.config/songbird/peers.toml` — Created
- `~/.local/share/nestgate/storage` — Symlinked to `/mnt/nestgate/cas`
- `/run/user/1000/membrane/nestgate-9b32f3a8.sock` — Symlinked
- `/run/user/1000/membrane/storage-9b32f3a8.sock` — Symlinked
- `~/graphs/esotericwebb_cell.toml` — Updated
- `~/graphs/footprint_cell.toml` — Updated
