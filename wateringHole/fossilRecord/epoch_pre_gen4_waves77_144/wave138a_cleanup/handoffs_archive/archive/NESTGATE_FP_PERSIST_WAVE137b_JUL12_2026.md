# NestGate FP-PERSIST — CAS-backed project persistence (Wave 137b)

**Date**: Jul 12, 2026  
**Wave**: 137b  
**Commit**: `88dc4fa2`  
**Tests**: 3,790 passed, 73 ignored, 0 failures (1 pre-existing env-specific)  
**Clippy**: Zero warnings from nestGate code

---

## FP-PERSIST — Replace footPrint Express CRUD with CAS persistence

### Problem

footPrint's `/api/projects` CRUD was backed by Express (Node.js). The Wave 137b
directive requires replacing this with content-addressed, provenance-traced
persistence in nestGate.

### Solution

New `footprint_handlers/` domain module following the established `coord_handlers`
pattern:

| Component | File | Purpose |
|-----------|------|---------|
| Types | `types.rs` | `FootPrintProject`, `FootPrintManifest`, `ProjectRevision` |
| Ingest | `ingest.rs` | `footprint.save`, `footprint.delete` |
| Query | `query.rs` | `footprint.list`, `footprint.get`, `footprint.history` |
| Bridge | `footprint_ops.rs` | Stateless `OnceLock<StorageState>` facade |

### CAS layout

```text
{base}/datasets/{family}/_footprint/manifest.json      # project index
{base}/datasets/{family}/_content/{hex[0:2]}/{hex}      # revision blobs (shared CAS)
{base}/datasets/{family}/_content/{hex[0:2]}/{hex}.meta.json
```

Revision content is stored in the shared `_content/` CAS directory — not in a
separate `_footprint/` blob store — giving projects automatic deduplication,
federation via `content.replicate`, HTTP serving via `GET /content/:hash`, and
provenance sidecars.

### RPC surface coverage

| Surface | Methods |
|---------|---------|
| UDS dispatch | `footprint.save`, `.get`, `.list`, `.delete`, `.history` |
| HTTP JSON-RPC (`/jsonrpc`) | Same via `handle_footprint_method` |
| Transport handler | Same via `footprint_ops` delegation |
| `UNIX_SOCKET_SUPPORTED_METHODS` | 5 methods added |
| `provided_capabilities` | New "footprint" group |
| `primal_announce` | "footprint" added to announced capabilities |
| `capability_registry.toml` | `[capabilities.footprint]` with full protocol docs |
| `NESTGATE_CAPABILITY_LABELS` | "footprint" added |

### Protocol

```
footprint.save:    {project_id, name?, content_base64, message?, metadata?}
                   → {project_id, hash, message, size, revision_count, manifest_version}

footprint.get:     {project_id, include_content?, revision?}
                   → {project_id, name, metadata, current_revision, revision?, content_base64?}

footprint.list:    {limit?, offset?}
                   → {count, projects: [{project_id, name, updated_at, ...}]}

footprint.delete:  {project_id}
                   → {deleted: true, note: "CAS content remains immutable"}

footprint.history: {project_id, limit?}
                   → {revisions: [{hash, message, saved_at, parent, size}]}
```

### Tests

9 new tests: type construction, serialization roundtrips, manifest layout, path
structure, multi-project ordering.

---

## footPrint integration next steps

1. footPrint client replaces Express `/api/projects` calls with `footprint.save`
   / `footprint.list` / `footprint.get` JSON-RPC (via HTTP or UDS)
2. Cross-gate backup: `content.replicate` on revision CIDs
3. Provenance: `spine_index` / `braid_id` populated when rootPulse trio is live
