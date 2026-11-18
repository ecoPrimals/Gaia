# FRAGO: grapheneGate SELinux Compatibility Fixes

**Date**: 2026-06-16 13:00Z  
**From**: primalSpring overwatch on eastGate  
**To**: songBird team, skunkBat team, cellMembrane/ops  
**Priority**: P1 (blocks grapheneGate full NUCLEUS)  
**Wave**: 114 — ABG Sovereign Compute

---

## Context

Live grapheneGate deployment validated the full pipeline (ADB push → launcher → spawn).
BearDog survives and responds on TCP. Songbird and SkunkBat crash due to GrapheneOS
SELinux constraints. These are the **last code blockers** for exit criterion #2.

---

## Required Fixes

### FIX-1: songBird — Configurable PID Directory

**Symptom**: `Failed to create PID file directory — Read-only file system (os error 30)`

**Root Cause**: Songbird hardcodes PID file path to a system directory that is
read-only for shell-context on GrapheneOS.

**Required Change**:
```
PID file path resolution order:
  1. $SONGBIRD_PID_DIR (if set)
  2. $SONGBIRD_STATE_DIR/pids (if state dir set)
  3. $XDG_RUNTIME_DIR/songbird (if XDG available)
  4. /tmp/biomeos/pids (fallback)
  5. /var/run/songbird (legacy — fails on restricted OS)
```

**Acceptance**: Songbird starts and stays alive on grapheneGate with
`SONGBIRD_STATE_DIR=/data/local/tmp/songbird` set.

**Owner**: songBird team  
**Effort**: Small (path resolution refactor)

---

### FIX-2: skunkBat — Graceful UDS Degradation

**Symptom**: `Transport(Io(Os { code: 13, kind: PermissionDenied }))` — fatal exit

**Root Cause**: SkunkBat's transport initialization attempts UDS bind unconditionally.
When GrapheneOS SELinux denies `sock_file` permission, the error is fatal rather than
triggering TCP-only fallback.

**Required Change**:
```rust
// Current (fatal):
let uds_listener = UnixListener::bind(socket_path)?;

// Required (graceful degradation):
match UnixListener::bind(socket_path) {
    Ok(listener) => { /* use UDS + TCP */ },
    Err(e) if e.kind() == io::ErrorKind::PermissionDenied => {
        warn!("UDS bind denied (SELinux?) — degrading to TCP-only");
        // continue with TCP transport only
    },
    Err(e) => return Err(e.into()),
}
```

This is the same pattern beardog already implements — beardog survives on grapheneGate
precisely because it degrades gracefully.

**Acceptance**: SkunkBat starts and stays alive on grapheneGate with TCP-only transport
when UDS is denied.

**Owner**: skunkBat team  
**Effort**: Small (error handling branch)

---

### FIX-3: cellMembrane — Fresh aarch64 Depot Sync

**Context**: Current eastGate depot has Jun 10 binaries (pre-genetics). Pepti has
Jun 15 genetics-enabled aarch64 builds.

**Required**: Sync fresh harvest to eastGate local depot (or provide direct
`plasmidbin pull --arch aarch64` path from WAN depot).

**Acceptance**: `stat` on depot binaries shows dates ≥ Jun 15.

**Owner**: cellMembrane / ops  
**Effort**: Trivial (rsync/scp from pepti)

---

## Deployment Re-Test Protocol

Once FIX-1 and FIX-2 ship:

```bash
# From eastGate:
adb shell "cd /data/local/tmp/ecoPrimals && \
  ECOPRIMALS_PLASMID_BIN=/data/local/tmp/ecoPrimals/plasmidBin/primals \
  SONGBIRD_STATE_DIR=/data/local/tmp/songbird \
  ./nucleus_launcher --profile graphenegate start --tcp --allow-degraded"

# Expected: 3/3 STARTED, 3/3 HEALTHY (with genetics binaries)
# Then validate:
adb shell "cd /data/local/tmp/ecoPrimals && \
  ./nucleus_launcher --profile graphenegate validate"
```

---

## Timeline

| Fix | Effort | Blocks |
|-----|--------|--------|
| FIX-1 (songbird PID) | 1-2h | grapheneGate 2/3 alive |
| FIX-2 (skunkbat UDS) | 1-2h | grapheneGate 3/3 alive |
| FIX-3 (depot sync) | 15min | riboCipher health sweep pass |

All three are independent — can be done in parallel.
Friday deadline is achievable if teams pick up today/tomorrow.

---

## Reference

- AAR: `AAR_WAVE114_GRAPHENEGATE_ADB_DEPLOYMENT_JUN16_2026.md`
- Profile: `primalSpring/config/profiles/graphenegate.toml`
- Genetics arch doc: `GENETICS_ARCHITECTURE_EUKARYOTIC_MODEL_JUN16_2026.md`
