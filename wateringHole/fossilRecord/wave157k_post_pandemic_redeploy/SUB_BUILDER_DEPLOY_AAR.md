# AAR — Sub-Builder Deployment + CAS Replication (Wave 157k)

**Date**: 2026-08-13
**Gate**: sporeGate (foreman)
**Wave**: 157k Ortho Cascade — Sub-Builder Activation

## Objective

Deploy `membrane builder.serve` on all registered sub-builders so the
foreman cascade can dispatch cross-architecture builds via Tower Atomic
mesh (songBird JSON-RPC) instead of SSH. Wire CAS replication from
foreman local CAS to ironGate's 12TB deep storage.

## Sub-Builder Status

| Gate | Target Triple | Transport | builder.serve | Port | Status |
|------|--------------|-----------|---------------|------|--------|
| ironGate | `aarch64-unknown-linux-musl` | LAN (192.168.4.237) | systemd `membrane-builder.service` | 9800 | LIVE |
| blueGate | `x86_64-pc-windows-gnu` | WG mesh (10.13.37.12) | Windows scheduled task `MembraneBuildServe` | 9800 | LIVE |
| graftGate | `aarch64-apple-darwin` | WG mesh (10.13.37.13) | — | — | BLOCKED (SSH key not enrolled) |

## Actions Taken

### ironGate (aarch64-musl)

1. Confirmed `membrane` binary present at `/usr/local/bin/membrane` (v0.1.0)
2. Confirmed Rust toolchain with `aarch64-unknown-linux-musl` target + `aarch64-linux-gnu-gcc`
3. Created `/etc/systemd/system/membrane-builder.service`:
   - `ExecStart=/usr/local/bin/membrane builder.serve`
   - `MEMBRANE_BUILD_AUTHORITY=1`
   - `Restart=on-failure`
4. Enabled and started — active (running), PID bound to `:9800`
5. Opened UFW: `allow from 192.168.4.0/22 to any port 9800 proto tcp`
6. End-to-end verified: `health` → `"builder OK (ironGate)"` from sporeGate
7. Updated `membrane` binary to `3628fd2` (G69 Phase 3 + gate hygiene)
8. Restarted builder service with new binary

### blueGate (x86_64-pc-windows-gnu)

1. Confirmed Windows NT 10.0.26200.0, `membrane.exe` at `C:\Users\user\.local\bin\`
2. Port 9800 was already listening from prior deployment
3. Confirmed `x86_64-w64-mingw32-gcc` cross toolchain + Rust 1.97.1
4. Old binary (`e0780c4`) lacked builder.serve changes — pulled latest and rebuilt on-gate
5. Deployed fresh `3628fd2` Windows binary
6. Registered `MembraneBuildServe` scheduled task (AtLogon, unlimited execution time)
7. End-to-end verified: `health` → `"builder OK (blueGate)"` from sporeGate

### graftGate (aarch64-apple-darwin)

- M4 Mac Mini at `10.13.37.13` (WG overlay)
- SSH key not authorized — `Permission denied` on all user attempts
- Requires physical access for key enrollment
- Builder deployment deferred until key enrolled

## CAS Replication

### Architecture

```
golgiBody (old binary)
    ↓ scp_from
sporeGate CAS ($DEPOT/cas/{arch}/{blake3})     ← foreman local archive
    ↓ replicate_to_cas_nodes
ironGate CAS (/mnt/nestgate/cas/primals/{arch}/{blake3})  ← 12TB deep storage
```

### Implementation

- `archive_old_binary_to_cas()` already committed (G69 Phase 3, commit `a38c70d`)
- `replicate_to_cas_nodes()` wired: after local archive, scp to ironGate's
  `/mnt/nestgate/cas/primals/{arch}/{blake3}`
- Dedup check on both ends (skip if BLAKE3 already exists)
- `CasReplicationTarget` hardcoded to ironGate for now; will move to
  `ecosystem_manifest.toml [cas_replication]` when westGate (50.7TB ZFS) enrolls
- ironGate CAS directory created at `/mnt/nestgate/cas/` (12TB free)

### Binary Deployment Summary

| Gate | Version | Commit |
|------|---------|--------|
| sporeGate | 0.1.0 | f8df585 (includes CAS replication) |
| ironGate | 0.1.0 | 3628fd2 |
| blueGate | 0.1.0 | 3628fd2 |
| golgiBody | 0.1.0 | 3628fd2 |

## Topology Update

- `ecosystem_manifest.toml` already has all three sub-builders registered
- `FOREMAN_PIPELINE_SPEC.md` already documents the foreman → sub-builder flow
- Cascade timer restarted on sporeGate with fresh binary

## Blockers

1. **graftGate SSH key enrollment** — requires physical access to M4 Mac Mini
2. **westGate CAS enrollment** — NAS has no `lan_ip` in topology yet; needs
   SSH config and LAN IP discovery before replication target can be added

## Next Steps

- Enroll graftGate SSH key and deploy `builder.serve` (launchd plist)
- Discover westGate LAN IP, add to topology, and add as CAS replication target
- Move CAS targets to `ecosystem_manifest.toml [cas_replication]` section
- Wire mesh-native (songBird capability) CAS replication to replace SSH/scp
