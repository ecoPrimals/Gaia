# tideGlass Remaining Issues AAR — westGate Live Validation

**Date**: Aug 4, 2026 (updated PM — Wave 156d cascade)
**Gate**: westGate
**Wave**: 156d
**Primal**: tideGlass
**Repo**: `protoKarya/tideGlass`
**Status**: 214 tests, 0 clippy warnings, live NUCLEUS validated, all quality gates GREEN

---

## Resolved This Session (156d Cascade)

| Issue | Resolution |
|-------|------------|
| DIV-2: No query-by-tag API | **RESOLVED.** nestGate v4.57+ shipped `content.query`. tideGlass wired `CasQueryParams`/`CasQueryResponse` types and `CasClient::query()` method. `resolve_dataset_hash()` evolved from dead `const fn -> None` to live `query_dataset_hash()` using `content.query` by pipeline tag. |
| DIV-4: GPS data in NumPy/pickle format | **RESOLVED.** westGate team ran pickle→JSON converter: 2198 genes, MLP weights, RCL ensembles, compound matrices. 11 JSON outputs (103.4 MB) CAS-ingested with BLAKE3 provenance. |
| DIV-7: Socket paths use `membrane/` with family-ID naming | Discovery rewritten to prefix-glob scan of `membrane/` then `biomeos/`. `find_socket_by_prefix()` public API. |
| DIV-8: Neural API doesn't proxy `content.*` methods | Automatic fallback from Neural API to direct nestGate. Server detects empty response and retries on direct socket. |
| CAS client hangs on `content.list` (30 MB / 333K objects) | Switched from `read_line` to `read_to_end`. Startup probe changed from `content.list` to `health.check`. |
| Stale docs (test counts, socket paths, coverage refs) | All root docs, specs, validation/README reconciled. |
| Cell graph uses old deploy command | Updated to `biomeos nucleus attach --cell` (v4.57 API). |
| No visualization wiring | 5 P0 scenes implemented (`scenes.rs`), petalTongue IPC client wired, 6 new dispatch methods. |

---

## Remaining Issues — Upstream Blockers (Not tideGlass Code)

### 1. biomeOS v4.57 Not Deployed on westGate — Ops

**Problem**: westGate still needs depot pull + NUCLEUS restart.
Depot v4.57+ is synced (52 builds on sporeGate), and ironGate/strandGate are deployed/staged.

**Required**: `depot pull` on westGate, then `biomeos nucleus restart`.

**Impact**: tideGlass cell boot and `content.query` both require v4.57+ binaries on westGate.
Server works standalone via `tideglass run --socket <path>`.

**Owner**: westGate ops. Blurb says "NEXT: westGate depot pull + restart".

### 2. Neural API `content.*` Routing (DIV-8) — biomeOS Team

**Problem**: Neural API socket responds to `health.check` but returns empty responses for
CAS data methods. tideGlass has automatic direct-nestGate fallback.

**Required**: biomeOS Neural API needs to route `content.*` and `content.query` methods.

**Impact**: Capability-based routing not functional for data access. Mitigated by fallback.

**Owner**: biomeOS team.

### 3. Stale CAS Clients in Other Primals (DIV-5)

**Problem**: groundSpring, airSpring, and others have stale CAS client code.

**Required**: Canonical Rust CAS client crate or audit.

**Owner**: nestGate team / overwatch.

### 4. Large Object Streaming (DIV-6)

**Problem**: Some GPS files may exceed the 64 MiB `content.get` inline limit.
With the JSON conversion (103 MB across 11 files), individual files should be within
the limit, but this remains a concern for raw data formats.

**Required**: Streaming client for CAS objects > 64 MiB, or pre-chunked data.

**Owner**: tideGlass (code) + nestGate (protocol).

### 5. petalTongue Not Co-Deployed on westGate

**Problem**: Visualization scenes are wired and dispatch handlers return scene JSON,
but petalTongue is not in the westGate NUCLEUS. Scene forwarding requires
co-deployment.

**Required**: petalTongue in westGate NUCLEUS, or expose scenes via `tideglass.primals.eco`
on golgi Caddy routing.

**Impact**: Scenes returned as JSON only — no live WebGL render until petalTongue is present.

**Owner**: Ops (cell graph already declares petalTongue dependency).

---

## tideGlass Code — Complete and Deployment-Ready

| Aspect | Status |
|--------|--------|
| Rust workspace | 9 crates, 7 science modules, 2.0 MB release binary |
| Tests | **214**, all green |
| Clippy | pedantic + nursery, zero warnings |
| Unsafe code | `#![forbid(unsafe_code)]` on all crates |
| Dependencies | 6 direct, 21 transitive, all pure Rust |
| CAS connectivity | Live on westGate, graceful degradation |
| CAS data loading | **`content.query` wired** — discovers datasets by pipeline tag at startup |
| GPS data | **CONVERTED** — 11 JSON files (103 MB) CAS-ingested with BLAKE3 |
| Socket discovery | Handles `membrane/` layout with family-ID naming |
| Neural API fallback | Automatic when `content.*` not proxied |
| Cell graph | Ready for `biomeos nucleus attach` v4.57 |
| Health triad | Reports CAS routing, convergence, per-module readiness |
| IPC methods | **17 implemented** (7 science + 5 viz + 1 catalog + 4 infra) |
| Visualization | 5 P0 petalTongue scenes + data catalog |
| Divergences | 8 documented (DIV-2 + DIV-4 **RESOLVED**, 3 mitigated, 3 upstream) |

---

## Recommended Overwatch Actions

1. **Priority**: westGate depot pull + NUCLEUS restart (unblocks cell boot + `content.query`)
2. **Priority**: golgi Caddy routing for `tideglass.primals.eco` (unblocks web presence)
3. **Review**: biomeOS Neural API `content.*` + `content.query` routing gap (DIV-8)
4. **Audit**: Other primals' CAS clients for stale method names (DIV-5)
5. **Track**: petalTongue deployment on westGate for live science visualization
