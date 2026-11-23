# NestGate v0.5.0 — Session 90 Content Trust & Wave 75 Response

**Date**: 2026-06-03
**Gate**: ironGate (eastGate)
**Primal**: nestgate v0.5.0
**Session**: 90

## Context

Wave 75 mission: "Content trust is your domain." When Gate A stores content and
Gate B pulls it, the BLAKE3 hash is the authority. Content is self-certifying.
But we need to prove this with real enforcement and tests.

## Delivered

### BLAKE3 Integrity Verification in `content.replicate.pull` (P0)

**Before**: `pull_blob_from_remote()` decoded base64 from remote `content.get`
and wrote directly to local CAS path — trusting the remote without verification.

**After**: Post-decode BLAKE3 hash is computed and compared against the requested
CID. Corrupted or tampered content is rejected with an explicit error:

```
BLAKE3 integrity failure: expected {cid}, got {actual_hash}
(remote {source} served corrupted content)
```

This enforces the sovereign content pipeline: no gate can serve corrupted content
to another gate without detection.

**File**: `content_federation_handlers.rs` — `pull_blob_from_remote()`

### Content Integrity Tests (2 NEW)

| Test | What it proves |
|------|----------------|
| `content_get_blake3_roundtrip_integrity` | Multiple payloads (empty, short, binary, 8KiB) through put→get cycle all match BLAKE3 |
| `corrupted_blob_detected_by_blake3_mismatch` | On-disk tampering produces a hash mismatch detectable by any consumer |

### `/tmp` Hardcoding Evolution (3 sites)

| File | Was | Now |
|------|-----|-----|
| `isomorphic_ipc/atomic/discovery.rs` L46 | `PathBuf::from("/tmp")` | `std::env::temp_dir()` |
| `isomorphic_ipc/atomic/discovery.rs` L127 | `String::from("/tmp")` | `std::env::temp_dir().to_string_lossy()` |
| `transport/security.rs` L135 | `String::from("/tmp")` | `std::env::temp_dir().to_string_lossy()` |

Fourth site (`probes.rs` L160) retained — legitimate filesystem mount point probe list.

## Metrics

- **11,546 test functions** across codebase (resolves inflated count mystery)
- **3,732 tests** passing (workspace full, serial)
- **2,269 tests** lib-only (2 new integrity tests)
- **747 RPC tests**
- **0 clippy warnings**, 0 unsafe, 0 files >800L
- **372,042 lines** of Rust across 22 workspace crates

## Wave 75 Mission Status

| Item | State |
|------|-------|
| BLAKE3 CAS (`content.put/get`) | **Operational** |
| `content.replicate.pull` BLAKE3 verification | **Implemented (this session)** |
| `route.register` mesh capability registration | **Operational** (Wave 73) |
| `content.store_stream/retrieve_stream` | **Operational on UDS** (Wave 74) |
| Content integrity tests | **2 new + 9 existing federation tests** |
| westGate ZFS integration | **Ready** (`NESTGATE_STORAGE_BASE_PATH`, ZFS detection) |
| Cross-gate mesh integration testing | **Blocked on Songbird cap propagation** (Wave 75 P0 is Songbird, not NestGate) |

## Known Issues

- 12 pre-existing test failures in parallel execution (env-var race in `nestgate-api`)
- Cross-gate integration tests use simulated file copy, not live RPC — real multi-gate
  testing requires `benchScale` lab topology
- `content.replicate.pull` and `content.store_stream*` are UDS-only — not yet surfaced
  on HTTP/transport layer

## Next

- westGate ZFS onboarding (when gate arrives)
- Cross-gate live test via benchScale topology
- Surface content streaming on HTTP transport for parity
