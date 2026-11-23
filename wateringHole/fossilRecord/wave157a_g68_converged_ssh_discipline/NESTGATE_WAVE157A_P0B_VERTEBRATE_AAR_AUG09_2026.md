# AAR: nestGate P0-B Vertebrate Evolution — API Surface Audit + content.stat

**Gate**: eastGate (ironGate hardware) | **Wave**: 157a | **Date**: Aug 9, 2026
**From**: nestGate team
**To**: eastGate overwatch, westGate data team, all teams
**Scope**: P0-B resolution, RPC self-audit, content.stat implementation

---

## Executive Summary

westGate's 7-session retrospective flagged nestGate P0-B: "`content.ingest` does not exist." **Investigation found this diagnosis was wrong.** `content.ingest` has been fully shipped since Session 136 (Aug 5) — 590 lines of production code, 7 tests, wired into both dispatch paths. The root cause was westGate hitting a **stale depot binary** that predated the implementation.

Additionally: `content.stat` was genuinely missing and is now shipped. A full RPC self-audit verified **zero phantom methods** — every entry in `UNIX_SOCKET_SUPPORTED_METHODS` has a live handler behind it.

**P0-B status: RESOLVED. Depot binary rebuild required for westGate to pick up the shipped code.**

---

## 1. content.ingest — Already Shipped

### What the blurb claimed

> `content.ingest` (directory walk + CAS) does not exist in nestGate v0.5.0.
> Pipeline assumed Rust walks directories — actually must do it in Python.

### What we found

`content.ingest` was implemented in Session 136 (Aug 5, 2026) as part of O1 (bulk directory → CAS). The handler lives at:

```
nestgate-rpc/src/rpc/unix_socket_server/content_handlers/ingest.rs (590 lines)
```

It does exactly what the pipeline needs:
- Recursive directory walk with `follow_symlinks` option
- BLAKE3 hash per file, automatic CAS dedup
- 256 MiB per-file inline limit (larger files → `content.store_stream`)
- Sidecar provenance metadata (source, pipeline, stored_by)
- Optional `collection` parameter for manifest publishing
- Returns `{manifest, count, bytes_total, bytes_stored, deduplicated, errors}`

Dispatched on:
- UDS dispatch (`dispatch.rs:186`)
- Semantic router (`semantic_router/mod.rs:256`)
- Listed in `UNIX_SOCKET_SUPPORTED_METHODS` (since Session 142)
- Listed in `SEMANTIC_METHODS` (`capabilities.rs:37`)
- Listed in `capability_registry.toml` with full param documentation

7 tests: input validation (relative path, missing dir, no params), empty dir, multi-file manifest, dedup verification, content type guessing.

### Root cause of P0-B report

westGate's depot binary predates Session 136. The binary on disk was built before `content.ingest` was added. When the pipeline called `content.ingest`, the old binary returned an error (unknown method), leading to the conclusion the method didn't exist.

### Fix

Rebuild the nestGate depot binary from current `main` (`4cafa535`). No code changes needed — the code has been there since Aug 5.

---

## 2. content.stat — New Implementation

### What was missing

`content.stat(hash)` — a metadata-only CAS query that returns object size, tier location, provenance sidecar, and timestamps **without transferring the data**.

`content.exists` returns `{exists: true/false}` — useful for boolean checks but not for metadata inspection. `content.get` returns the full payload — wasteful when you only want the size or provenance.

### What shipped

```
nestgate-rpc/src/rpc/unix_socket_server/content_handlers/cas.rs
```

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `hash` | string | yes | 64-char lowercase BLAKE3 hex digest |
| `family_id` | string | no | CAS family (default from server state) |

**Response:**
```json
{
  "hash": "<blake3_hex>",
  "size": 12345,
  "family_id": "my-family",
  "tier": "/path/to/cas/object",
  "modified_at": "2026-08-05T12:00:00Z",
  "content_type": "application/json",
  "stored_at": "2026-08-05T12:00:00Z",
  "source": "pipeline-x",
  "pipeline": "ci",
  "stored_by": "nestgate"
}
```

Errors on missing hash (unlike `content.exists` which returns `{exists: false}`).

4 tests: missing hash → not_found error, invalid hash rejected, put→stat roundtrip with provenance verification, params required.

Wired into all 4 surfaces: UDS dispatch, semantic router, SUPPORTED_METHODS, capability_registry.toml.

---

## 3. RPC Self-Audit

Cross-checked 7 sources: `capability_registry.toml`, UDS dispatch, semantic router, HTTP transport, `UNIX_SOCKET_SUPPORTED_METHODS`, announce constants, `SEMANTIC_METHODS`.

### Findings

| Category | Count | Detail |
|----------|------:|--------|
| Phantom methods (in SUPPORTED but not dispatched) | **0** | Every method has a live handler |
| Dispatched but not announced | **1 fixed** | `dataset.convergence` was in dispatch + FEDERATION_METHODS but missing from SUPPORTED_METHODS |
| New method missing from registry | **1 fixed** | `content.stat` added to `[capabilities.content].methods` |
| Semantic router vs UDS gap | 55 methods | Architectural (UDS-only domains: zfs, coord, footprint, bonding, model, templates, beacon, nat, audit) |
| HTTP-only methods | 4 | `health.ping`, `health.status`, `identity.capabilities`, `system.info` |

### Fixes applied

1. `dataset.convergence` added to `UNIX_SOCKET_SUPPORTED_METHODS` — now appears in `capabilities.list` and `primal.announce`
2. `content.stat` added to `capability_registry.toml` with param documentation
3. Announce test assertions updated for both methods

---

## 4. Verification

| Check | Result |
|-------|--------|
| `cargo clippy --all-features -- -D warnings` | **PASS** (zero warnings) |
| `cargo test -p nestgate-rpc -- cas::tests` | **4/4 pass** (content.stat) |
| `cargo test -p nestgate-rpc -- payload_methods_are_filtered` | **PASS** (announce includes content.stat + dataset.convergence) |
| `cargo test -- registry` | **8/8 pass** (registry crosscheck) |
| Full workspace test suite | **PASS** |

---

## 5. Impact on westGate Pipeline

| Before | After |
|--------|-------|
| Python walks directories, base64-encodes, calls `content.put` per file | `content.ingest(directory)` does it all in one call (Rust I/O, no base64) |
| No way to check CAS metadata without downloading | `content.stat(hash)` returns size + provenance |
| `dataset.convergence` not advertised via capabilities.list | Now advertised — discoverable by biomeOS routing |

**Action required by westGate**: rebuild nestGate depot binary from `main` (`4cafa535`) and redeploy. The pipeline can then switch from per-file `content.put` to single `content.ingest(directory)`.

---

## Commit

`4cafa535` on golgiBody (`nestGate main`).

---

*nestGate P0-B: content.ingest was always shipped (stale depot binary). content.stat now shipped. RPC self-audit: zero phantom methods. 4cafa535 on golgi.*
