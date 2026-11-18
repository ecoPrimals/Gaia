# tideGlass CAS Wiring AAR — First Primal Live Data Integration

**Date**: Aug 3–4, 2026
**Gate**: westGate
**Wave**: 156b → 156d
**Primal**: tideGlass
**Context**: First primal to wire live nestGate CAS data. Divergences documented for upstream teams.

---

## Summary

Wired tideGlass UniBin to discover and connect to nestGate CAS on startup.
Dispatch handlers fall through from CAS-loaded data to caller-supplied params
gracefully. Health triad reports CAS connection status and loaded dataset counts.

**Aug 4 update**: Validated against **live NUCLEUS on westGate**. Socket discovery
fixed for actual deployment layout. Neural API fallback to direct nestGate wired.
First live RGES computation executed on westGate hardware.

**Aug 4 PM update (Wave 156d)**: `content.query` wired — nestGate v4.57+ shipped
metadata search (DIV-2 RESOLVED). GPS data CONVERTED by westGate team (11 JSON files,
103 MB, CAS-ingested with BLAKE3). `resolve_dataset_hash()` evolved from dead
`const fn -> None` to live `query_dataset_hash()` using `content.query` by pipeline tag.
5 P0 visualization scenes wired via petalTongue IPC client.

**220 tests passing. Clippy pedantic+nursery clean. All quality gates green.**

**Aug 5 update (Wave 156d)**: `PetalTongueClient` activated — instantiated at startup
when socket discovered, viz scenes forwarded to petalTongue via `render_scene()`.
`ServerContext` replaces separate `Arc<ModuleData>`. Server extracts method name and
fire-and-forget forwards viz results. Cell graph updated for westGate 3.21 TB / 452 GB CAS.

---

## Divergences Found

### DIV-1: DATA_ACCESS.md uses wrong hash format

**tideGlass spec** (`specs/DATA_ACCESS.md`):
```json
{"hash": "blake3:abc123...", "format": "gctx"}
```

**Actual nestGate NG-1 contract**:
```json
{"hash": "a1b2c3d4e5f6..."}  // 64-char lowercase hex, no prefix, no format param
```

**Impact**: Any primal implementing from DATA_ACCESS.md would construct invalid requests.
**Fix**: Updated tideGlass CAS client to use plain 64-char hex. DATA_ACCESS.md update needed.
**Upstream**: All DATA_ACCESS.md templates across primals likely have this issue.

### DIV-2: No query-by-tag API in nestGate

**Problem**: GPS platform data (8 files, 1.4 GB) is CAS-indexed with provenance
metadata (source, pipeline), but there's no `content.query_by_tag` or
`content.search` method. The only retrieval mechanism is by exact BLAKE3 hash.

**Impact**: tideGlass can't discover its data at runtime without pre-configured hashes.
`content.list` returns 67,680+ objects — iterating and filtering by metadata would
require fetching each object's `.meta.json` sidecar, which is O(n) network calls.

**Options** (for upstream nestGate team):
1. Add `content.query` method accepting `{source: "...", pipeline: "..."}` filters
2. Add `content.list` metadata filtering: `{family_id: "...", source: "tideglass"}`
3. Publish a `data_manifest.toml` per dataset with known CAS hashes after ingest

**Recommended**: Option 3 is cheapest (no nestGate changes). Option 1 is best long-term.
tideGlass currently uses `resolve_dataset_hash()` which returns `None` — dispatch
falls through to caller-supplied params until hashes are configured.

### DIV-3: DATA_ACCESS.md references nonexistent streaming method

**tideGlass spec**:
```
nestGate.storage.retrieve(key) → stream chunks → process
```

**Actual nestGate**:
- Inline: `content.get` (up to 64 MiB)
- Streaming: `content.retrieve_stream` / `content.retrieve_stream_chunk`
- Method `nestGate.storage.retrieve` does not exist

**Impact**: Any primal implementing streaming from DATA_ACCESS.md would get method-not-found.
**Fix**: tideGlass CAS client handles streaming redirect (`use_streaming: true` response).
Error returned until streaming client is implemented.

### DIV-4: GPS platform data format is NumPy/pickle — **RESOLVED**

**RESOLVED** (Wave 156d): westGate data team ran pickle→JSON converter. 11 JSON outputs
(103.4 MB) CAS-ingested with BLAKE3 provenance. 2198 genes, MLP weights, RCL ensembles,
compound matrices. tideGlass now discovers these via `content.query` by pipeline tag.

### DIV-5: Other primals have stale CAS client code

Found during contract research:
- `groundSpring/.../nestgate.rs` uses legacy `key`/`value` params (not the CAS contract)
- `airSpring/.../nestgate_data.rs` calls `content.store` (method is `content.put`)
- `content_pipeline_smoke.toml` comment says `content.list` returns `{items: [...]}` —
  actual field is `hashes`

**Impact**: These primals will fail when they attempt CAS integration.
**Upstream**: nestGate team should publish a canonical Rust client crate (`nestgate-client`)
that all primals can depend on, rather than each primal reimplementing the contract.

### DIV-6: `content.get` inline limit is 64 MiB but GPS files are larger

Several GPS platform files exceed 64 MiB (MolSearch.zip is ~518 MB). `content.get`
returns a streaming redirect for these. tideGlass's CAS client detects this and
returns an error — streaming not yet implemented.

**Impact**: Large CAS objects cannot be loaded at startup until streaming is wired.
**Fix**: Implement `content.retrieve_stream` + `content.retrieve_stream_chunk` protocol.
This is non-trivial (requires maintaining a streaming session across multiple RPC calls).

### DIV-7: Socket discovery path and naming convention mismatch

**Documentation/spec assumed**:
- Sockets in `$XDG_RUNTIME_DIR/biomeos/`
- Fixed filenames: `neural-api-default.sock`, `nestgate.sock` (stale — live uses `neural-api-<family-id>.sock`)

**Actual live NUCLEUS on westGate**:
- Sockets in `$XDG_RUNTIME_DIR/membrane/`
- Family-ID naming: `neural-api-westgate-tower-155f.sock`, `nestgate-westgate-tower-155f.sock`
- Capability aliases via symlinks: `dag.sock` → rhizocrypt, `provenance.sock` → sweetgrass

**Impact**: Any primal using `biomeos/neural-api-default.sock` will never find the socket.
**Fix**: tideGlass discovery rewritten to scan `membrane/` then `biomeos/` with prefix-glob
matching (`neural-api-*`, `nestgate-*`). `find_socket_by_prefix()` exposed as public API.
**Upstream**: Document canonical socket layout. Other primals likely have this same issue.

### DIV-8: Neural API socket does not proxy CAS methods

**Problem**: The Neural API socket (`neural-api-westgate-tower-155f.sock`) responds to
`health.check` (returns nestGate v4.56.0) but returns **empty responses** for
`content.exists`, `content.list`, and other CAS data methods. The direct nestGate socket
(`nestgate-westgate-tower-155f.sock`) responds correctly to all CAS methods.

**Impact**: Primals relying on Neural API routing for CAS data will get empty responses
and silently fail. tideGlass health.check reported "healthy" via Neural API while
data calls returned nothing.

**Fix**: tideGlass wired fallback: if Neural API health succeeds but data loading
gets errors, automatically falls through to direct nestGate socket discovery.
**Upstream**: biomeOS Neural API needs `content.*` method routing to nestGate.
This is the headline divergence — the G56 Neural API routing pattern is not
fully wired for CAS data methods yet.

---

## Live Validation (Aug 4, westGate)

Tested tideGlass binary against live 13-primal NUCLEUS on westGate:

| Test | Result |
|------|--------|
| Socket discovery | Found `neural-api-westgate-tower-155f.sock` in `$XDG_RUNTIME_DIR/membrane/` |
| Neural API health.check | `nestGate v4.56.0` (healthy) |
| Neural API content.exists | Empty response (DIV-8) |
| Direct nestGate health.check | `nestGate v0.5.0` (healthy) |
| Direct nestGate content.exists | Working — returns validation error for bad hash |
| Direct nestGate content.list | Working — **333,695 CAS objects**, 30 MB response |
| Fallback: Neural API → direct | Automatic — server retries on direct socket |
| Server startup | `tideglass run --socket /tmp/tideglass-test.sock` — listening |
| health.liveness | `{"alive": true}` |
| health.check | CAS connected, routing `neural-api`, 0 datasets loaded, 6 load errors |
| science.rges_screen | **First live RGES computation**: sorafenib + doxorubicin scored with 10K permutations each |

**CAS store**: 333,695 objects on ZFS (54.9 GB CAS, 2.97 TB data, 47.7 TB free).
GPS platform data converted to JSON and CAS-ingested (DIV-4 RESOLVED) — benchmark
is the remaining data task before real drug repurposing computation.

---

## Architecture Decisions

### CAS types in tideglass-core, async client in tideglass-bin

CAS request/response types (`CasGetResponse`, `CasPutResponse`, etc.) live in
`tideglass-core/src/cas.rs` as sync, serializable structs. The async UDS client
lives in `tideglass-bin/src/cas_client.rs`. This keeps tideglass-core free of
tokio dependency while allowing other crates to use the types.

### Graceful degradation with Neural API fallback

The server starts with or without CAS:
1. Discovers socket via env var / `$XDG_RUNTIME_DIR/membrane/` / `biomeos/` (prefix glob)
2. If Neural API found: connects, calls `health.check` to verify connectivity
3. If Neural API health succeeds but data loading fails: falls back to direct nestGate
4. If no socket found: starts with empty `ModuleData`, all modules accept caller params
5. Dispatch handlers check CAS-loaded data first, fall through to caller params

### Health triad reports CAS routing

`health.check` includes CAS routing mode and convergence status:
```json
{
  "cas": {
    "connected": true,
    "routing": "neural-api",
    "datasets_loaded": 0,
    "load_errors": 6,
    "converged_datasets": 0
  }
}
```

biomeOS orchestration can use this to verify CAS readiness before routing science work.

---

## Files Changed

- `crates/tideglass-core/src/cas.rs` — CAS types, socket discovery (new)
- `crates/tideglass-core/src/lib.rs` — export cas module
- `crates/tideglass-bin/src/cas_client.rs` — async CAS client (new)
- `crates/tideglass-bin/src/data.rs` — CAS data loading, ModuleData (new)
- `crates/tideglass-bin/src/dispatch.rs` — handlers accept ModuleData, CAS fallthrough
- `crates/tideglass-bin/src/server.rs` — thread Arc<ModuleData> to connections
- `crates/tideglass-bin/src/health.rs` — CAS-aware health triad
- `crates/tideglass-bin/src/main.rs` — CAS init on startup
- `crates/tideglass-bin/Cargo.toml` — add base64 dep
- `Cargo.toml` — add base64 workspace dep

## Upstream Review Requests

1. **nestGate team**: Publish canonical CAS client crate or review tideGlass's implementation
2. **nestGate team**: Consider `content.query` method for metadata-based lookups (DIV-2)
3. **westGate data team**: Publish GPS platform CAS hash manifest for tideGlass
4. **westGate data team**: Convert GPS NumPy/pickle to JSON and re-ingest with lineage (DIV-4)
5. **overwatch**: Audit DATA_ACCESS.md templates across all primals for DIV-1/DIV-3
6. **overwatch**: Flag stale CAS clients in groundSpring, airSpring (DIV-5)
